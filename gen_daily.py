"""
gen_daily.py — Sinh dataset tự động mỗi ngày bằng 2 key Groq free (200k token/ngày/key).

- Chia câu theo business, gộp 4 câu/lần gọi (schema/README chỉ tính 1 lần).
- Tự cân bằng 2 key, tự dừng khi hết quota ngày (TPD) của cả 2.
- Chỉ lưu khi code chạy ra đúng gold; code đã bỏ comment/print/hardcode.
- Resume: chạy lại bỏ qua câu đã có trong pairs.jsonl.

  python gen_daily.py --max-questions 320
"""
import argparse
import json
import re
import sys
import time
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
if (BASE / "vendor").exists():
    sys.path.insert(0, str(BASE / "vendor"))

import requests

from utils import (load_biz_data, get_readme, get_full_schema,
                   execute_ai_code, clean_code_text, strip_comments)
from pipeline import format_ans, check_correct

KEYS = [
    "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",
    "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",
]
URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-120b"
DAILY_BUDGET = 185_000          # mỗi key, dưới hạn 200k
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) gen-daily/1.0"

TRAIN_DIR = BASE / "train"
DATA_DIR = TRAIN_DIR / "data"
QUESTIONS = TRAIN_DIR / "questions.jsonl"
ANSWERS = TRAIN_DIR / "answers.jsonl"
RULEBOOK = TRAIN_DIR / "rulebook.md"

DISTILL = BASE / "distill"
PAIRS = DISTILL / "pairs.jsonl"
LEARNING = BASE / "HUYTKING_learning.jsonl"
FAILED = DISTILL / "failed_daily.jsonl"
STATE = DISTILL / "daily_state.json"
LOG = DISTILL / "gen_daily.log"

PROMPT = """Bạn là Chuyên gia Data Engineer. Viết code Python (Pandas) trả lời TỪNG câu hỏi dưới đây.

### DỮ LIỆU
- README (quy đổi đơn vị): {readme}
- RULEBOOK (luật thời gian, xếp hạng): {rulebook}
- SCHEMA (tên bảng | cột):
{schema}

### QUY TẮC (vi phạm = sai)
1. Lấy bảng: `get_df_by_keyword(dfs, ['Tên_Bảng'])`; nhiều bảng cùng loại: `get_all_dfs_by_keyword(dfs, ['Tên'])`. Rỗng thì `ans, ans_type = None, "unanswerable"`.
2. Ngày: `parse_date_safe(...)`; tiền/số: `clean_money/clean_number`.
3. Luôn loại đơn huỷ/trả (trạng thái chứa 'hủy','huỷ','trả') khi tính doanh thu/số đơn.
4. "Tháng này" = ngày 1 → as_of_date. Quý 4 = tháng 10,11,12. Tuần bắt đầu thứ 2.
5. Xếp hạng: giảm dần theo tiêu chí, bằng nhau thì theo tên tăng dần.
6. Gán `ans` + `ans_type` (number/percent/string/date/boolean/list/table).
7. KHÔNG print, KHÔNG comment, KHÔNG hardcode đáp án, KHÔNG đọc file.

### CÂU HỎI
{questions}

### ĐẦU RA (JSON duy nhất, khoá = id)
{{
  "q_xxx": {{"code": "code python thuần", "ans_type": "number", "ans": 123}}
}}"""


def read_jsonl(p):
    if not Path(p).exists():
        return []
    with open(p, "r", encoding="utf-8-sig") as f:
        return [json.loads(l) for l in f if l.strip()]


def trim_readme(text, max_chars):
    """Giữ các dòng quy đổi đơn vị (1 thùng = 24 lon...) để giảm token."""
    keep = [l for l in text.splitlines()
            if re.search(r"[=:]\s*\d|quy đổi|thùng|lốc|bó|cây|lon|chai|hộp|gói", l, re.I)]
    out = "\n".join(keep).strip()
    return (out or text)[:max_chars]


def load_state():
    today = str(date.today())
    st = {"date": today, "used": {str(i): 0 for i in range(len(KEYS))}}
    if STATE.exists():
        try:
            old = json.loads(STATE.read_text(encoding="utf-8"))
            if old.get("date") == today:
                st = old
        except Exception:
            pass
    return st


def save_state(st):
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


def pick_key(st):
    best, best_left = None, 0
    for i in range(len(KEYS)):
        left = DAILY_BUDGET - st["used"].get(str(i), 0)
        if left > best_left:
            best, best_left = i, left
    return best, best_left


def call(key_idx, prompt, st, cost_est):
    key = KEYS[key_idx]
    body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0, "max_tokens": 1800,
            "response_format": {"type": "json_object"}}
    r = requests.post(URL, json=body, timeout=240,
                      headers={"Authorization": f"Bearer {key}",
                               "Content-Type": "application/json",
                               "User-Agent": UA})
    if r.status_code == 200:
        d = r.json()
        used = d.get("usage", {}).get("total_tokens") or cost_est
        st["used"][str(key_idx)] = st["used"].get(str(key_idx), 0) + used
        save_state(st)
        return d["choices"][0]["message"]["content"], None

    txt = r.text[:400]
    if r.status_code == 429 and "tokens per day" in txt:
        st["used"][str(key_idx)] = DAILY_BUDGET
        save_state(st)
        return None, "TPD"
    if r.status_code == 429:
        m = re.search(r"try again in ([\d.]+)\s*s", txt)
        time.sleep(min(float(m.group(1)) + 1 if m else 20, 65))
        return None, "TPM"
    return None, f"HTTP {r.status_code}: {txt[:120]}"


def verify(q, gold, dfs, entry):
    code = entry.get("code") if isinstance(entry, dict) else None
    if not code:
        return None, None, "không có code"
    code = strip_comments(str(code).strip().strip("`"))
    code = re.sub(r"^\s*python\s*\n", "", code)
    code = clean_code_text(code)

    res, _r, typ, e = execute_ai_code(code, dfs, q["question"], q.get("as_of_date"))
    if e:
        return None, None, f"runtime: {e}"
    ans = format_ans(res, typ, q["question"])
    if not check_correct(ans, gold):
        return None, None, f"ra {ans} vs gold {gold['answer']}"
    if not re.search(r"\bdfs\b|get_df_by_keyword|get_all_dfs_by_keyword", code):
        return None, None, "không dùng dfs"
    if len(str(gold["answer"])) >= 3 and str(gold["answer"]) in code:
        return None, None, "nghi hardcode"
    return code, ans, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-questions", type=int, default=320)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--readme-chars", type=int, default=2500)
    ap.add_argument("--rulebook-chars", type=int, default=2000)
    ap.add_argument("--retry-failed", action="store_true", help="Thử lại các câu đã fail")
    args = ap.parse_args()

    DISTILL.mkdir(exist_ok=True)
    st = load_state()
    qs = read_jsonl(QUESTIONS)
    golds = {g["id"]: g for g in read_jsonl(ANSWERS)}
    done = {r["id"] for r in read_jsonl(PAIRS)}
    tried = set() if args.retry_failed else {r["id"] for r in read_jsonl(FAILED)}
    rulebook = RULEBOOK.read_text(encoding="utf-8")[: args.rulebook_chars] if RULEBOOK.exists() else ""

    todo = [q for q in qs if q["id"] in golds and q["id"] not in done and q["id"] not in tried]
    if not todo:
        print("✅ Không còn câu nào cần làm.")
        return

    # chia theo business, mỗi chunk tối đa `batch` câu, xoay vòng business
    groups = defaultdict(list)
    for q in todo:
        groups[q["business_id"]].append(q)
    chunks = []
    while any(groups.values()) and sum(len(c) for _, c in chunks) < args.max_questions:
        for b in list(groups):
            if groups[b] and sum(len(c) for _, c in chunks) < args.max_questions:
                chunks.append((b, groups[b][: args.batch]))
                groups[b] = groups[b][args.batch:]

    print(f"🎯 {len(todo)} câu chưa làm | hôm nay làm {sum(len(c) for _, c in chunks)} câu "
          f"({len(chunks)} call) | quota: {[DAILY_BUDGET - st['used'].get(str(i), 0) for i in range(len(KEYS))]}")
    log = open(LOG, "a", encoding="utf-8")
    log.write(f"\n# {datetime.now():%Y-%m-%d %H:%M} — {len(chunks)} chunk\n")

    ok = bad = 0
    ctx_cache = {}
    for n, (biz, items) in enumerate(chunks, 1):
        if biz not in ctx_cache:
            dfs = load_biz_data(biz, DATA_DIR)
            if not dfs:
                continue
            ctx_cache[biz] = {"dfs": dfs, "schema": get_full_schema(dfs),
                              "readme": trim_readme(get_readme(biz, DATA_DIR, max_chars=6000),
                                                    args.readme_chars)}
        ctx = ctx_cache[biz]
        lines = "\n".join(f'- id={q["id"]} | as_of={q.get("as_of_date")} | {q["question"]}' for q in items)
        prompt = PROMPT.format(readme=ctx["readme"], rulebook=rulebook,
                               schema=ctx["schema"], questions=lines)
        cost = int(len(prompt) / 2.8) + 900

        text, err = None, None
        for _ in range(3):
            ki, left = pick_key(st)
            if left < cost:
                print("🛑 Hết quota hôm nay của cả 2 key.")
                log.write("- hết quota\n")
                log.close()
                save_state(st)
                print(f"ok={ok} bad={bad}")
                return
            text, err = call(ki, prompt, st, cost)
            if text:
                break
            if err == "TPD":
                continue
            if err == "TPM":
                continue
            break

        if not text:
            bad += len(items)
            log.write(f"- {biz} call lỗi: {err}\n")
            continue

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", text, re.DOTALL)
            data = json.loads(m.group(0)) if m else {}
            if not data:
                bad += len(items)
                log.write(f"- {biz} JSON hỏng\n")
                continue

        for q in items:
            entry = data.get(q["id"])
            code, ans, why = verify(q, golds[q["id"]], ctx["dfs"], entry)
            if why is None:
                rec = {"id": q["id"], "business_id": biz, "as_of_date": q.get("as_of_date"),
                       "question": q["question"], "code": code, "answer": ans,
                       "gold": golds[q["id"]]["answer"], "gold_type": golds[q["id"]].get("type"),
                       "schema": ctx["schema"], "readme": ctx["readme"], "verified": True}
                with open(PAIRS, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                with open(LEARNING, "a", encoding="utf-8") as f:
                    f.write(json.dumps({k: rec[k] for k in ("id", "business_id", "question", "code", "answer")},
                                       ensure_ascii=False) + "\n")
                ok += 1
            else:
                bad += 1
                with open(FAILED, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"id": q["id"], "business_id": biz, "why": why},
                                       ensure_ascii=False) + "\n")

        if n % 5 == 0:
            print(f"  {n}/{len(chunks)} call | ok={ok} bad={bad} "
                  f"| còn {[DAILY_BUDGET - st['used'].get(str(i), 0) for i in range(len(KEYS))]}")

    log.write(f"- ok={ok} bad={bad}\n")
    log.close()
    print(f"\n✅ Hôm nay: ok={ok} bad={bad}")
    print(f"→ {PAIRS}")


if __name__ == "__main__":
    main()
