"""
solve_all_train.py — Giải toàn bộ câu hỏi bằng DeepSeek, tự sửa lỗi 3 lần, chỉ lưu khi đúng gold.

  python solve_all_train.py --start 1 --end 300
  python solve_all_train.py --start 1 --end 300 --model deepseek-v4-pro
  python solve_all_train.py --public            # sinh public_test.jsonl (khi đã đúng hết train)
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
if (BASE / "vendor").exists():
    sys.path.insert(0, str(BASE / "vendor"))

import requests

from utils import (load_biz_data, get_readme, get_full_schema, execute_ai_code,
                   clean_code_text, strip_comments)
from pipeline import format_ans, check_correct

# ================= CẤU HÌNH =================
API_KEY = "sk-0b8f42c32f864fbd8cbb9412593bf54e"
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-flash"          # hoặc deepseek-v4-pro

TRAIN_DIR = BASE / "train"
DATA_DIR = TRAIN_DIR / "data"
QUESTIONS_FILE = TRAIN_DIR / "questions.jsonl"
ANSWERS_FILE = TRAIN_DIR / "answers.jsonl"
RULEBOOK_FILE = TRAIN_DIR / "rulebook.md"

LEARNING_FILE = BASE / "HUYTKING_learning.jsonl"
FAILED_FILE = BASE / "HUYTKING_failed.jsonl"
PAIRS_FILE = BASE / "distill" / "pairs.jsonl"
LOG_FILE = BASE / "logs_generate" / "solve_all.log"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) datamate-solve/1.0"

PROMPT = """Bạn là chuyên gia Python/Pandas. Viết code trả lời câu hỏi sau.

### CÂU HỎI
{question}
Ngày chốt (as_of_date): {as_of_date}   (đã là pd.Timestamp)

### DỮ LIỆU
README (quy ước quy đổi đơn vị — đọc kỹ):
{readme}

RULEBOOK (luật thời gian, xếp hạng):
{rulebook}

SCHEMA (bảng | cột):
{schema}

### QUY TẮC BẮT BUỘC (sai là hỏng)
1. Lấy bảng bằng `get_df_by_keyword(dfs, ['Tên_Bảng'])`; dữ liệu tách theo tháng thì
   `get_all_dfs_by_keyword(dfs, ['Tên'])`. KHÔNG đọc file, KHÔNG import pandas.
2. Cột ngày trong dữ liệu là CHUỖI: BẮT BUỘC `col = parse_date_safe(df['Cột'])` TRƯỚC khi
   so sánh/lọc theo ngày (nếu không sẽ lỗi str vs Timestamp).
3. Cột tiền/số lượng là CHUỖI: BẮT BUỘC `clean_money(...)` / `clean_number(...)` TRƯỚC khi
   cộng/so sánh (nếu không sẽ lỗi str >= int).
4. BẮT BUỘC lọc đơn huỷ/trả trước khi tính:
   `df = df[~df['Trạng thái'].astype(str).str.lower().str.contains('hủy|huỷ|trả', na=False)]`
5. Quy đổi đơn vị theo README (bó→cây, thùng→lon, lốc→chai...) trước khi cộng số lượng.
6. "Tháng này" = ngày 1 → as_of_date; Quý 4 = tháng 10,11,12; tuần bắt đầu thứ 2.
7. Gán `ans` và `ans_type` (number/percent/string/date/boolean/list/table/unanswerable).
8. KHÔNG print, KHÔNG comment, KHÔNG hardcode đáp án.

### ĐẦU RA: JSON duy nhất
{{"code": "code python thuần", "ans_type": "number", "answer": 123}}"""


def read_jsonl(p):
    if not Path(p).exists():
        return []
    with open(p, "r", encoding="utf-8-sig") as f:
        return [json.loads(l) for l in f if l.strip()]


def append_jsonl(p, rec):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def ask(prompt, model=MODEL, retries=4):
    body = {"model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0, "max_tokens": 2000,
            "response_format": {"type": "json_object"}}
    last = None
    for attempt in range(retries):
        try:
            r = requests.post(API_URL, json=body, timeout=180,
                              headers={"Authorization": f"Bearer {API_KEY}",
                                       "Content-Type": "application/json",
                                       "User-Agent": UA})
            if r.status_code == 402:
                return None, "HET_SO_DU"
            if r.status_code == 429:
                time.sleep(5 * (attempt + 1))
                last = "429"
                continue
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}: {r.text[:150]}"
            txt = r.json()["choices"][0]["message"]["content"]
            try:
                return json.loads(txt), None
            except json.JSONDecodeError:
                m = re.search(r"\{.*\}", txt, re.DOTALL)
                return (json.loads(m.group(0)), None) if m else (None, "JSON hỏng")
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            time.sleep(2 * (attempt + 1))
    return None, last


def build_prompt(q, schema, readme, rulebook):
    return PROMPT.format(question=q["question"], as_of_date=q.get("as_of_date"),
                         readme=readme, rulebook=rulebook, schema=schema)


def run_one(q, gold, dfs, schema, readme, rulebook, model, max_retries):
    """Trả (code, ans, None) nếu đúng, ngược lại (None, ans_cuối, lý_do)."""
    prompt = build_prompt(q, schema, readme, rulebook)
    code = ans = None
    for attempt in range(1, max_retries + 1):
        data, err = ask(prompt, model=model)
        if err == "HET_SO_DU":
            return None, None, "HET_SO_DU"
        if not data or not data.get("code"):
            prompt += "\n\nLẦN TRƯỚC: bạn không trả JSON hợp lệ. Chỉ trả JSON."
            continue

        code = clean_code_text(strip_comments(str(data["code"]).strip().strip("`")))
        code = re.sub(r"^\s*python\s*\n", "", code)
        res, _r, typ, e = execute_ai_code(code, dfs, q["question"], q.get("as_of_date"))
        if e:
            reason = e
        else:
            ans = format_ans(res, typ, q["question"])
            if check_correct(ans, gold):
                return code, ans, None
            reason = f"chạy ra {ans}, đáp án đúng là {gold['answer']}"

        if attempt < max_retries:
            prompt = build_prompt(q, schema, readme, rulebook) + (
                f"\n\n### CODE LẦN {attempt} BỊ SAI\n```python\n{code}\n```\n"
                f"LỖI/KẾT QUẢ SAI: {reason}\n"
                f"Đáp án đúng phải là: {gold['answer']} ({gold.get('type')}).\n"
                "Hãy sửa: kiểm tra parse_date_safe/clean_money đã dùng chưa, bộ lọc hủy/trả, "
                "quy đổi đơn vị, đúng tên cột. KHÔNG được gán ans bằng hằng số.")
    return None, ans, "hết lượt thử"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=300)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--max-retries", type=int, default=3)
    ap.add_argument("--sleep", type=float, default=2.0)
    ap.add_argument("--public", action="store_true", help="sinh public_test.jsonl")
    args = ap.parse_args()

    questions = read_jsonl(QUESTIONS_FILE)
    golds = {g["id"]: g for g in read_jsonl(ANSWERS_FILE)}
    rulebook = RULEBOOK_FILE.read_text(encoding="utf-8")[:2000] if RULEBOOK_FILE.exists() else ""
    done = {r["id"] for r in read_jsonl(LEARNING_FILE)}

    if args.public:
        return solve_public(args, rulebook)

    subset = questions[max(args.start - 1, 0): args.end]
    todo = [q for q in subset if q["id"] in golds and q["id"] not in done]

    print(f"🎯 {len(todo)} câu cần giải (đoạn {args.start}-{args.end}) | đã có {len(done)} "
          f"| model={args.model} | retry={args.max_retries}")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    log = open(LOG_FILE, "a", encoding="utf-8")
    log.write(f"\n# {datetime.now():%Y-%m-%d %H:%M} — {args.start}-{args.end}\n")

    ok = bad = 0
    ctx = {}
    t0 = time.time()
    for i, q in enumerate(todo, 1):
        biz = q["business_id"]
        if biz not in ctx:
            dfs = load_biz_data(biz, DATA_DIR)
            if not dfs:
                print(f"[{i}] {q['id']} ⚠️ không đọc được dữ liệu")
                continue
            ctx[biz] = {"dfs": dfs, "schema": get_full_schema(dfs),
                        "readme": get_readme(biz, DATA_DIR, max_chars=3000)}

        code, ans, why = run_one(q, golds[q["id"]], ctx[biz]["dfs"], ctx[biz]["schema"],
                                 ctx[biz]["readme"], rulebook, args.model, args.max_retries)

        if why == "HET_SO_DU":
            print("\n🛑 Hết số dư DeepSeek — dừng. Nạp thêm rồi chạy lại (resume tự động).")
            break

        if why is None:
            rec = {"id": q["id"], "business_id": biz, "as_of_date": q.get("as_of_date"),
                   "question": q["question"], "code": code, "answer": ans,
                   "gold": golds[q["id"]]["answer"], "gold_type": golds[q["id"]].get("type"),
                   "schema": ctx[biz]["schema"], "readme": ctx[biz]["readme"], "verified": True}
            append_jsonl(LEARNING_FILE, {k: rec[k] for k in ("id", "question", "code", "answer")})
            append_jsonl(PAIRS_FILE, rec)
            ok += 1
            print(f"[{i}/{len(todo)}] ✅ {q['id']} → {ans}")
            log.write(f"{q['id']}: ok {ans}\n")
        else:
            append_jsonl(FAILED_FILE, {"id": q["id"], "business_id": biz, "question": q["question"],
                                       "as_of_date": q.get("as_of_date"),
                                       "gold": golds[q["id"]]["answer"], "pred": ans,
                                       "why": why, "code": code})
            bad += 1
            print(f"[{i}/{len(todo)}] ❌ {q['id']} — {why}")
            log.write(f"{q['id']}: {why}\n")

        time.sleep(args.sleep)

    log.close()
    print(f"\n📊 Đúng {ok} | Sai {bad} | {(time.time()-t0)/60:.1f} phút | tổng đã có {len(done)+ok}")


def solve_public(args, rulebook):
    """Chạy câu hỏi public_test (không có gold) -> public_test.jsonl."""
    qs = read_jsonl(BASE / "public_test" / "questions.jsonl")
    out_path = BASE / "public_test.jsonl"
    out = open(out_path, "w", encoding="utf-8")
    ctx = {}
    print(f"🌐 {len(qs)} câu public_test | model={args.model}")
    for i, q in enumerate(qs, 1):
        biz = q["business_id"]
        if biz not in ctx:
            dfs = load_biz_data(biz, BASE / "public_test" / "data")
            ctx[biz] = {"dfs": dfs, "schema": get_full_schema(dfs),
                        "readme": get_readme(biz, BASE / "public_test" / "data", max_chars=3000)}
        prompt = build_prompt(q, ctx[biz]["schema"], ctx[biz]["readme"], rulebook)
        data, err = ask(prompt, model=args.model)
        if not data or not data.get("code"):
            out.write(json.dumps({"id": q["id"], "type": "unanswerable", "answer": None},
                                 ensure_ascii=False) + "\n")
            continue
        code = clean_code_text(strip_comments(str(data["code"])).strip().strip("`"))
        res, _r, typ, e = execute_ai_code(code, ctx[biz]["dfs"], q["question"], q.get("as_of_date"))
        ans = None if e else format_ans(res, typ, q["question"])
        out.write(json.dumps({"id": q["id"], "type": typ or "unanswerable", "answer": ans},
                             ensure_ascii=False) + "\n")
        out.flush()
        print(f"[{i}/{len(qs)}] {q['id']} → {ans}")
        time.sleep(args.sleep)
    out.close()
    print(f"→ {out_path}")


if __name__ == "__main__":
    main()
