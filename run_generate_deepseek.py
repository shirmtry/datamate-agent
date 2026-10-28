"""
run_generate_deepseek.py — Sinh dataset (câu hỏi → code đúng) bằng DeepSeek, verify bằng gold.

Tối ưu chi phí: gộp NHIỀU câu / 1 lần gọi (mặc định 4) cùng 1 business,
nên schema/README/RULEBOOK chỉ tính token 1 lần. Code trả về không comment.

  python run_generate_deepseek.py --limit 8 --batch 4 --workers 4   # thử
  python run_generate_deepseek.py                                    # full 3000
"""
import argparse
import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
if (BASE / "vendor").exists():
    sys.path.insert(0, str(BASE / "vendor"))

import requests

from utils import (load_biz_data, get_readme, get_full_schema, compact_schema,
                   execute_ai_code, clean_code_text, strip_comments)
from pipeline import format_ans, check_correct

# ================= CẤU HÌNH =================
API_KEY = "sk-0b8f42c32f864fbd8cbb9412593bf54e"
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"

TRAIN_DIR = BASE / "train"
DATA_DIR = TRAIN_DIR / "data"
QUESTIONS_FILE = TRAIN_DIR / "questions.jsonl"
ANSWERS_FILE = TRAIN_DIR / "answers.jsonl"
RULEBOOK_FILE = TRAIN_DIR / "rulebook.md"

PAIRS_FILE = BASE / "distill" / "pairs.jsonl"
LEARNING_FILE = BASE / "HUYTKING_learning.jsonl"
FAILED_FILE = BASE / "distill" / "failed_ds.jsonl"
LOG_FILE = BASE / "distill" / "gen_deepseek.log"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) gen-ds/2.0"

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


_lock = threading.Lock()
_ctr = {"ok": 0, "bad": 0, "api": 0, "q": 0}
_t0 = time.time()
_local = threading.local()


def log(line):
    with _lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def session():
    if not hasattr(_local, "s"):
        s = requests.Session()
        s.headers.update({"Authorization": f"Bearer {API_KEY}",
                          "Content-Type": "application/json",
                          "User-Agent": UA})
        _local.s = s
    return _local.s


def ask(prompt, max_tokens=4000, retries=3):
    body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0, "max_tokens": max_tokens,
            "response_format": {"type": "json_object"}}
    last = None
    for attempt in range(retries):
        try:
            r = session().post(API_URL, json=body, timeout=240)
            if r.status_code == 402:
                return None, "HẾT SỐ DƯ (402)"
            if r.status_code in (429, 500, 502, 503):
                time.sleep(3 * (attempt + 1))
                last = f"HTTP {r.status_code}"
                continue
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}: {r.text[:150]}"
            txt = r.json()["choices"][0]["message"]["content"]
            try:
                return json.loads(txt), None
            except json.JSONDecodeError:
                m = re.search(r"\{.*\}", txt, re.DOTALL)
                if m:
                    try:
                        return json.loads(m.group(0)), None
                    except Exception:
                        pass
                return None, "JSON hỏng"
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            time.sleep(2 * (attempt + 1))
    return None, last


def verify_one(q, gold, dfs, entry):
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
    ap.add_argument("--limit", type=int, default=0, help="0 = tất cả")
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--schema", choices=["full", "compact"], default="full")
    ap.add_argument("--readme-chars", type=int, default=2500)
    ap.add_argument("--rulebook-chars", type=int, default=2000)
    args = ap.parse_args()

    PAIRS_FILE.parent.mkdir(parents=True, exist_ok=True)
    questions = read_jsonl(QUESTIONS_FILE)
    golds = {g["id"]: g for g in read_jsonl(ANSWERS_FILE)}
    done = {r["id"] for r in read_jsonl(PAIRS_FILE)}
    rulebook = (RULEBOOK_FILE.read_text(encoding="utf-8")[: args.rulebook_chars]
                if RULEBOOK_FILE.exists() else "")

    todo = [q for q in questions if q["id"] in golds and q["id"] not in done]
    if args.limit:
        todo = todo[: args.limit]

    # gom theo business để dùng lại schema/readme
    by_biz = {}
    for q in todo:
        by_biz.setdefault(q["business_id"], []).append(q)

    ctx = {}
    for b in by_biz:
        dfs = load_biz_data(b, DATA_DIR)
        if not dfs:
            continue
        ctx[b] = {"dfs": dfs,
                  "schema": get_full_schema(dfs) if args.schema == "full" else compact_schema(dfs),
                  "readme": get_readme(b, DATA_DIR, max_chars=args.readme_chars)}

    chunks = []
    for b, items in by_biz.items():
        if b not in ctx:
            continue
        for i in range(0, len(items), args.batch):
            chunks.append((b, items[i:i + args.batch]))

    print(f"🎯 {len(todo)} câu → {len(chunks)} lần gọi | batch {args.batch} | "
          f"{args.workers} luồng | đã có {len(done)}")
    log(f"\n# {datetime.now():%Y-%m-%d %H:%M} — {len(todo)} câu, {len(chunks)} call")

    lock_file = threading.Lock()

    def save(rec):
        with lock_file:
            with open(PAIRS_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            with open(LEARNING_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps({k: rec[k] for k in ("id", "business_id", "question", "code", "answer")},
                                   ensure_ascii=False) + "\n")

    def save_failed(q, why):
        with lock_file:
            with open(FAILED_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps({"id": q["id"], "business_id": q["business_id"],
                                    "question": q["question"], "as_of_date": q.get("as_of_date"),
                                    "gold": golds[q["id"]]["answer"], "why": why},
                                   ensure_ascii=False) + "\n")

    def run_chunk(chunk):
        b, items = chunk
        c = ctx[b]
        lines = "\n".join(
            f'- id={q["id"]} | as_of={q.get("as_of_date")} | {q["question"]}' for q in items)
        prompt = PROMPT.format(readme=c["readme"], rulebook=rulebook,
                               schema=c["schema"], questions=lines)
        data, err = ask(prompt, max_tokens=min(4000, 700 * len(items) + 800))
        if not data:
            return b, items, {}, err

        out = {}
        for q in items:
            entry = data.get(q["id"])
            if entry is None:  # đôi khi model trả list
                for v in data.values():
                    if isinstance(v, dict) and v.get("code") and len(items) == 1:
                        entry = v
            out[q["id"]] = entry
        return b, items, out, None

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run_chunk, ch): ch for ch in chunks}
        for fut in as_completed(futs):
            b, items = futs[fut][0], futs[fut][1]
            try:
                b, items, out, err = fut.result()
            except Exception as e:
                out, err = {}, f"exception {e}"
            _ctr["q"] += len(items)
            for q in items:
                if err:
                    _ctr["api"] += 1
                    continue
                res = verify_one(q, golds[q["id"]], ctx[b]["dfs"], out.get(q["id"]))
                code, ans, why = res
                if why is None:
                    save({"id": q["id"], "business_id": b, "as_of_date": q.get("as_of_date"),
                          "question": q["question"], "code": code, "answer": ans,
                          "gold": golds[q["id"]]["answer"], "gold_type": golds[q["id"]].get("type"),
                          "schema": ctx[b]["schema"], "readme": ctx[b]["readme"],
                          "verified": True})
                    _ctr["ok"] += 1
                else:
                    _ctr["bad"] += 1
                    save_failed(q, why)
            log(f"{b}: {len(out)}/{len(items)} | ok={_ctr['ok']} bad={_ctr['bad']} api={_ctr['api']}")
            if _ctr["q"] % 20 < args.batch:
                el = time.time() - _t0
                print(f"  {_ctr['q']}/{len(todo)} câu | ok {_ctr['ok']} | bad {_ctr['bad']} "
                      f"| api {_ctr['api']} | {_ctr['q']/max(el,1)*60:.0f} câu/phút")

    print(f"\n✅ Xong: {_ctr} | {(time.time()-_t0)/60:.1f} phút")
    print(f"→ {PAIRS_FILE}")


if __name__ == "__main__":
    main()
