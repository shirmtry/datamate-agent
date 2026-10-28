"""
gen_dataset.py — Sinh dataset (câu hỏi → code đúng) cho TOÀN BỘ 3000 câu, chi phí token thấp.

Khác run_self_learning.py:
  - Không gọi học sinh (tốn thời gian vô ích): gửi thẳng câu hỏi + gold cho giáo viên.
  - GỬI NHIỀU CÂU / 1 LẦN GỌI (mặc định 8) cùng 1 business -> schema/readme/rulebook chỉ tính 1 lần.
  - Schema nén (gộp bảng cùng cột), README/rulebook cắt gọn, code KHÔNG comment.
  - Chỉ lưu khi code chạy ra đúng gold + không hardcode đáp án.

  python gen_dataset.py --limit 80 --batch 8
  python gen_dataset.py --all                 # chạy hết 3000 câu (resume được)
"""
import argparse
import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
if (BASE / "vendor").exists():
    sys.path.insert(0, str(BASE / "vendor"))
from utils import (load_biz_data, get_readme, compact_schema, get_full_schema,
                   execute_ai_code, clean_code_text, strip_comments)
from pipeline import format_ans, check_correct

import requests

TEACHER = {
    "url": "https://api.groq.com/openai/v1/chat/completions",
    "key": "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",
    "model": "openai/gpt-oss-120b",
}

TRAIN_DIR = BASE / "train"
DATA_DIR = TRAIN_DIR / "data"
QUESTIONS = TRAIN_DIR / "questions.jsonl"
ANSWERS = TRAIN_DIR / "answers.jsonl"
RULEBOOK = TRAIN_DIR / "rulebook.md"

OUT_DIR = BASE / "distill"
PAIRS = OUT_DIR / "pairs.jsonl"
LOG = OUT_DIR / "gen_log.md"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) gen/1.0"

PROMPT = """Bạn là kỹ sư dữ liệu. Viết code Pandas trả lời TỪNG câu hỏi dưới đây.

MÔI TRƯỜNG: `dfs` (dict tên_bảng→DataFrame), `get_df_by_keyword(dfs,['Tên'])`,
`get_all_dfs_by_keyword(dfs,['Tên'])` (gộp mọi bảng khớp), `parse_date_safe`,
`clean_money`, `clean_number`, `normalize_id`, `as_of_date` (Timestamp), `pd`, `np`.

QUY TẮC:
1. Chỉ dùng cột có trong SCHEMA. Không đọc file, không print, KHÔNG viết comment.
2. Luôn: `if df is None or len(df)==0: ans, ans_type = None, "unanswerable"`.
3. Đơn huỷ/trả hàng không tính doanh thu, số đơn. Tháng này = từ ngày 1 đến hết as_of_date.
4. Gán `ans` + `ans_type` ∈ number/percent/string/date/boolean/list/table.
5. Code ngắn nhất có thể (5-25 dòng). KHÔNG hardcode đáp án, KHÔNG gán ans = hằng số.

SCHEMA (tên bảng | cột):
{schema}

README (quy đổi đơn vị):
{readme}

RULEBOOK (trích):
{rulebook}

CÂU HỎI:
{questions}

TRẢ VỀ DUY NHẤT JSON: [{{"id":"...","code":"..."}}] — code là 1 chuỗi, không markdown."""


def read_jsonl(p):
    if not Path(p).exists():
        return []
    with open(p, "r", encoding="utf-8-sig") as f:
        return [json.loads(l) for l in f if l.strip()]


def write_jsonl_append(p, rows):
    with open(p, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def parse_json_array(text):
    if not text:
        return None
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    i, j = t.find("["), t.rfind("]")
    if i < 0 or j <= i:
        return None
    cand = t[i:j + 1]
    for attempt in (cand, cand.replace("\n", "\\n")):
        try:
            return json.loads(attempt)
        except Exception:
            continue
    return None


def looks_cheated(code, gold):
    """Chặn code hardcode đáp án hoặc không dùng dữ liệu."""
    if not re.search(r"\bdfs\b|get_df_by_keyword|get_all_dfs_by_keyword|get_all_dfs", code):
        return True
    g = str(gold).strip().rstrip("%")
    if len(g) >= 3 and g.replace(",", "") in code.replace(",", ""):
        return True
    if re.fullmatch(r"\s*ans\s*=\s*[\d.'\"]+\s*", code.strip()):
        return True
    return False


def call_teacher(prompt, max_tokens=1500, retries=6):
    body = {
        "model": TEACHER["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": max_tokens,
    }
    last = None
    for attempt in range(retries):
        try:
            r = requests.post(TEACHER["url"], json=body, timeout=240,
                              headers={"Authorization": f"Bearer {TEACHER['key']}",
                                       "Content-Type": "application/json",
                                       "User-Agent": UA})
            if r.status_code == 429:
                body_txt = r.text[:300]
                m = re.search(r"try again in ([\d.]+)\s*s", body_txt)
                wait = float(m.group(1)) + 1 if m else 20
                wait = min(wait, 65)
                print(f"    ⏳ 429 — chờ {wait:.0f}s")
                time.sleep(wait)
                continue
            if r.status_code != 200:
                last = f"HTTP {r.status_code}: {r.text[:150]}"
                time.sleep(3)
                continue
            ch = r.json()["choices"][0]
            c = (ch.get("message") or {}).get("content")
            if not c:
                last = f"content rỗng ({ch.get('finish_reason')})"
                time.sleep(2)
                continue
            return c, None
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            time.sleep(2 * (attempt + 1))
    return None, last


def call_ollama(prompt, model, timeout=1800):
    r = requests.post("http://localhost:11434/api/chat", timeout=timeout,
                      headers={"User-Agent": UA},
                      json={"model": model, "stream": False,
                            "options": {"temperature": 0.0, "num_ctx": 16384},
                            "messages": [{"role": "user", "content": prompt}]})
    r.raise_for_status()
    return r.json().get("message", {}).get("content", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--teacher", choices=["groq", "local"], default="groq")
    ap.add_argument("--model", default="qwen2.5-coder:7b", help="model khi --teacher local")
    ap.add_argument("--schema", choices=["full", "compact"], default="full")
    ap.add_argument("--tpm", type=int, default=8000, help="token/phút của tài khoản")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--readme-chars", type=int, default=2500)
    ap.add_argument("--rulebook-chars", type=int, default=2500)
    args = ap.parse_args()

    qs = read_jsonl(QUESTIONS)
    golds = {g["id"]: g for g in read_jsonl(ANSWERS)}
    done = {p["id"] for p in read_jsonl(PAIRS)}
    rulebook = RULEBOOK.read_text(encoding="utf-8") if RULEBOOK.exists() else ""

    todo = [q for q in qs if q["id"] in golds and q["id"] not in done]
    if not args.all:
        todo = todo[args.start: args.start + args.limit]
    else:
        todo = todo[args.start:]

    by_biz = defaultdict(list)
    for q in todo:
        by_biz[q["business_id"]].append(q)

    print(f"🎯 còn {len(todo)} câu cần sinh | đã có {len(done)} | {len(by_biz)} business")
    log = open(LOG, "a", encoding="utf-8")
    log.write(f"\n# {datetime.now():%Y-%m-%d %H:%M} — {len(todo)} câu\n")

    stats = {"ok": 0, "bad_verify": 0, "cheat": 0, "api": 0, "json": 0}
    t0 = time.time()
    WINDOW = []

    for biz, items in by_biz.items():
        dfs = load_biz_data(biz, DATA_DIR)
        if not dfs:
            continue
        schema = get_full_schema(dfs) if args.schema == "full" else compact_schema(dfs)
        readme = get_readme(biz, DATA_DIR, max_chars=args.readme_chars)
        rb = rulebook[: args.rulebook_chars]

        for i in range(0, len(items), args.batch):
            chunk = items[i: i + args.batch]
            lines = "\n".join(
                f'{k+1}. id={q["id"]} | as_of={q.get("as_of_date")} | gold={golds[q["id"]]["answer"]}'
                f' ({golds[q["id"]].get("type")}) | {q["question"]}'
                for k, q in enumerate(chunk))
            prompt = PROMPT.format(schema=schema, readme=readme, rulebook=rb, questions=lines)

            text, err = None, None
            if args.teacher == "groq":
                # token-bucket: giữ tổng token/phút dưới hạn
                need = int(len(prompt) / 2.8) + 900
                while sum(n for t, n in WINDOW if time.time() - t < 60) + need > args.tpm * 0.9:
                    oldest = WINDOW[0][0]
                    wait = max(60 - (time.time() - oldest) + 0.5, 1)
                    print(f"    ⏳ giữ nhịp TPM, chờ {wait:.0f}s")
                    time.sleep(wait)
                    WINDOW[:] = [(t, n) for t, n in WINDOW if time.time() - t < 60]
                WINDOW.append((time.time(), need))
                text, err = call_teacher(prompt)
            else:
                try:
                    text, err = call_ollama(prompt, args.model), None
                except Exception as e:
                    text, err = None, f"{type(e).__name__}: {e}"
            if not text:
                stats["api"] += len(chunk)
                print(f"  ❌ API {biz}: {err}")
                continue
            arr = parse_json_array(text)
            if not arr:
                stats["json"] += len(chunk)
                print(f"  ❌ JSON hỏng {biz} ({len(chunk)} câu)")
                log.write(f"- JSON hỏng {biz}: {str(text)[:200]}\n")
                continue

            codes = {}
            for it in arr:
                if isinstance(it, dict) and it.get("id") and it.get("code"):
                    codes[str(it["id"]).strip()] = it["code"]

            rows = []
            fails = []
            for q in chunk:
                code = codes.get(q["id"]) or codes.get(q["id"].strip())
                if not code:
                    fails.append(f"{q['id']}: teacher không trả code")
                    continue
                code = strip_comments(str(code).strip().strip("`"))
                code = re.sub(r"^\s*python\s*\n", "", code)
                code = clean_code_text(code)
                gold = golds[q["id"]]
                as_of = q.get("as_of_date")

                res, _r, typ, e = execute_ai_code(code, dfs, q["question"], as_of)
                if e:
                    stats["bad_verify"] += 1
                    fails.append(f"{q['id']}: {e[:90]}")
                    continue
                ans = format_ans(res, typ, q["question"])
                if not check_correct(ans, gold):
                    stats["bad_verify"] += 1
                    fails.append(f"{q['id']}: ra {ans} vs gold {gold['answer']}")
                    continue
                if looks_cheated(code, gold["answer"]):
                    stats["cheat"] += 1
                    fails.append(f"{q['id']}: hardcode")
                    continue

                rows.append({"id": q["id"], "business_id": biz, "as_of_date": as_of,
                             "question": q["question"], "code": code,
                             "answer": ans, "gold": gold["answer"],
                             "gold_type": gold.get("type"), "schema": schema,
                             "readme": readme, "verified": True})
                stats["ok"] += 1

            if rows:
                write_jsonl_append(PAIRS, rows)
            print(f"  {biz} [{i+len(chunk)}/{len(items)}] +{len(rows)}/{len(chunk)} "
                  f"| tổng OK {stats['ok']} | {time.time()-t0:.0f}s")
            for f in fails[:3]:
                print(f"      ✗ {f}")
            if fails:
                log.write(f"- {biz}: " + " ;; ".join(fails[:5]) + "\n")

    log.write(f"- Kết quả: {stats}\n")
    log.close()
    print(f"\n✅ Xong: {stats}")
    print(f"→ {PAIRS}")


if __name__ == "__main__":
    main()
