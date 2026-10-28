"""
generate_dataset.py — Sinh dataset (câu hỏi → code Pandas đúng) bằng Mistral.

Quy trình:
  1. Đọc questions.jsonl + answers.jsonl.
  2. Resume: bỏ qua câu đã có trong HUYTKING_learning.jsonl.
  3. Gom 5 câu cùng business_id vào 1 request (schema/README/RULEBOOK chỉ gửi 1 lần).
  4. Mistral trả JSON {id: code} -> chạy thử bằng execute_ai_code, so với gold.
  5. Đúng -> HUYTKING_learning.jsonl ; sai/lỗi -> HUYTKING_failed.jsonl.

  python generate_dataset.py                 # chạy toàn bộ (resume)
  python generate_dataset.py --limit 10      # thử 10 câu
  python generate_dataset.py --model mistral-medium-latest
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

from utils import (load_biz_data, get_readme, get_full_schema,
                   execute_ai_code, clean_code_text, strip_comments)
from pipeline import format_ans, check_correct

# ================= CẤU HÌNH =================
MISTRAL_API_KEY = "mstrl_SKXT4AxWWSMJ61wsIaYmbN8nLnpwIzqk_2z7aXE"
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
# codestral-latest: model code, chạy được với key này; mistral-large-latest bị chặn theo gói.
MISTRAL_MODEL = "codestral-latest"

TRAIN_DIR = BASE / "train"
DATA_DIR = TRAIN_DIR / "data"
QUESTIONS_FILE = TRAIN_DIR / "questions.jsonl"
ANSWERS_FILE = TRAIN_DIR / "answers.jsonl"
RULEBOOK_FILE = TRAIN_DIR / "rulebook.md"

LEARNING_FILE = BASE / "HUYTKING_learning.jsonl"
FAILED_FILE = BASE / "HUYTKING_failed.jsonl"
PAIRS_FILE = BASE / "distill" / "pairs.jsonl"      # để build_sft.py dùng lại
LOG_FILE = BASE / "logs_generate" / "mistral.log"

BATCH_SIZE = 5
RULEBOOK_CHARS = 2000
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) datamate-gen/1.0"

PROMPT = """Bạn là chuyên gia Python/Pandas. Viết code trả lời TỪNG câu hỏi dưới đây.

### DỮ LIỆU
- README (quy ước quy đổi đơn vị): {readme}
- RULEBOOK (luật thời gian, xếp hạng): {rulebook}
- SCHEMA (bảng | cột):
{schema}

### QUY TẮC CODE (bắt buộc)
1. `get_df_by_keyword(dfs, ['Tên_Bảng'])` để lấy bảng; dữ liệu tách theo tháng thì dùng
   `get_all_dfs_by_keyword(dfs, ['Tên'])`. Không đọc file.
2. `parse_date_safe(...)` cho ngày, `clean_money(...)` cho tiền, `clean_number(...)` cho số lượng.
3. Luôn loại đơn huỷ/trả: trạng thái chứa 'hủy', 'huỷ' hoặc 'trả'.
4. "Tháng này" = từ ngày 1 đến `as_of_date`. Quý 4 = tháng 10,11,12. Tuần bắt đầu thứ 2.
5. Gán `ans` và `ans_type` (number/percent/string/date/boolean/list).
6. Không `print()`, không comment, không hardcode đáp án.

### CÂU HỎI
{questions}

### ĐẦU RA (JSON duy nhất, khoá là id câu hỏi)
{{
  "q_xxx": {{"code": "code python thuần", "ans_type": "number", "ans": 123}}
}}"""


def read_jsonl(path):
    if not Path(path).exists():
        return []
    with open(path, "r", encoding="utf-8-sig") as f:
        return [json.loads(l) for l in f if l.strip()]


def append_jsonl(path, rec):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def call_mistral(prompt, model=MISTRAL_MODEL, retries=4):
    """Gọi Mistral, trả về dict JSON đã parse."""
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 3000,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}",
               "Content-Type": "application/json", "User-Agent": UA}
    last = None
    for attempt in range(retries):
        try:
            r = requests.post(MISTRAL_URL, headers=headers, json=body, timeout=180)
            if r.status_code == 429:
                wait = 10 * (attempt + 1)
                print(f"    ⏳ rate limit, chờ {wait}s")
                time.sleep(wait)
                last = "429"
                continue
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}: {r.text[:200]}"
            text = r.json()["choices"][0]["message"]["content"]
            try:
                return json.loads(text), None
            except json.JSONDecodeError:
                m = re.search(r"\{.*\}", text, re.DOTALL)
                if m:
                    return json.loads(m.group(0)), None
                return None, "JSON hỏng"
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            time.sleep(2 * (attempt + 1))
    return None, last


def verify(q, gold, dfs, entry):
    """Chạy code và so với gold. Trả (ans, code, error)."""
    code = entry.get("code") if isinstance(entry, dict) else None
    if not code:
        return None, None, "không có code"
    code = clean_code_text(strip_comments(str(code)).strip().strip("`"))
    code = re.sub(r"^\s*python\s*\n", "", code)

    ans, _reason, typ, err = execute_ai_code(code, dfs, q["question"], q.get("as_of_date"))
    if err:
        return None, code, err
    ans = format_ans(ans, typ, q["question"])
    if not check_correct(ans, gold):
        return ans, code, f"ra {ans} vs gold {gold['answer']}"
    return ans, code, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="0 = tất cả")
    ap.add_argument("--model", default=MISTRAL_MODEL)
    ap.add_argument("--batch", type=int, default=BATCH_SIZE)
    ap.add_argument("--sleep", type=float, default=2.0)
    args = ap.parse_args()

    questions = read_jsonl(QUESTIONS_FILE)
    golds = {g["id"]: g for g in read_jsonl(ANSWERS_FILE)}
    rulebook = (RULEBOOK_FILE.read_text(encoding="utf-8")[:RULEBOOK_CHARS]
                if RULEBOOK_FILE.exists() else "")

    done = {r["id"] for r in read_jsonl(LEARNING_FILE)}
    todo = [q for q in questions if q["id"] in golds and q["id"] not in done]
    if args.limit:
        todo = todo[: args.limit]

    # gom theo business để dùng lại schema/README
    by_biz = {}
    for q in todo:
        by_biz.setdefault(q["business_id"], []).append(q)

    batches = [(b, items[i:i + args.batch])
               for b, items in by_biz.items()
               for i in range(0, len(items), args.batch)]

    print(f"🚀 {len(todo)} câu cần làm | {len(batches)} batch | model={args.model} "
          f"| resume: {len(done)} câu đã có")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    log = open(LOG_FILE, "a", encoding="utf-8")
    log.write(f"\n# {datetime.now():%Y-%m-%d %H:%M} — {len(todo)} câu\n")

    ok = bad = 0
    t0 = time.time()
    for n, (biz, items) in enumerate(batches, 1):
        dfs = load_biz_data(biz, DATA_DIR)
        if not dfs:
            print(f"  [{n}] {biz}: không đọc được dữ liệu")
            continue

        schema = get_full_schema(dfs)
        readme = get_readme(biz, DATA_DIR, max_chars=3000)
        lines = "\n".join(
            f'- id={q["id"]} | as_of={q.get("as_of_date")} | {q["question"]}' for q in items)
        prompt = PROMPT.format(readme=readme, rulebook=rulebook, schema=schema, questions=lines)

        print(f"\n[{n}/{len(batches)}] {biz} — {len(items)} câu")
        data, err = call_mistral(prompt, model=args.model)
        if not data:
            print(f"  ❌ API: {err}")
            log.write(f"- {biz}: API lỗi {err}\n")
            bad += len(items)
            time.sleep(args.sleep)
            continue

        failed_here = []
        for q in items:
            gold = golds[q["id"]]
            ans, code, why = verify(q, gold, dfs, data.get(q["id"]))
            if why is None:
                rec = {"id": q["id"], "business_id": biz, "as_of_date": q.get("as_of_date"),
                       "question": q["question"], "code": code, "answer": ans,
                       "gold": gold["answer"], "gold_type": gold.get("type"),
                       "schema": schema, "readme": readme, "verified": True}
                append_jsonl(LEARNING_FILE, {k: rec[k] for k in ("id", "question", "code", "answer")})
                append_jsonl(PAIRS_FILE, rec)
                ok += 1
                print(f"  ✅ {q['id']} → {ans}")
            else:
                failed_here.append((q, why, code))
                print(f"  ❌ {q['id']} — {why}")
            log.write(f"{q['id']}: {'ok' if why is None else why}\n")

        # Vòng 2: gửi lại kèm lỗi cụ thể (sửa được phần lớn lỗi kiểu dữ liệu)
        for q, why, code in failed_here:
            gold = golds[q["id"]]
            retry_prompt = PROMPT.format(readme=readme, rulebook=rulebook, schema=schema,
                                         questions=f'- id={q["id"]} | as_of={q.get("as_of_date")} | {q["question"]}')
            retry_prompt += (f"\n\nCODE LẦN TRƯỚC BỊ LỖI/SAI:\n{code}\n\nLỖI: {why}\n"
                             "Sửa lại: ép kiểu dữ liệu trước khi so sánh (dùng clean_money/clean_number), "
                             "không dùng pd.concat(df) mà dùng get_all_dfs_by_keyword, kiểm tra tên cột.")
            data2, err2 = call_mistral(retry_prompt, model=args.model)
            if not data2:
                append_jsonl(FAILED_FILE, {"id": q["id"], "business_id": biz, "question": q["question"],
                                           "as_of_date": q.get("as_of_date"), "gold": gold["answer"],
                                           "pred": None, "why": f"{why} | retry API: {err2}", "code": code})
                bad += 1
                continue
            entry = data2.get(q["id"])
            if entry is None:
                for v in data2.values():
                    if isinstance(v, dict) and v.get("code"):
                        entry = v
                        break
            ans2, code2, why2 = verify(q, gold, dfs, entry)
            if why2 is None:
                rec = {"id": q["id"], "business_id": biz, "as_of_date": q.get("as_of_date"),
                       "question": q["question"], "code": code2, "answer": ans2,
                       "gold": gold["answer"], "gold_type": gold.get("type"),
                       "schema": schema, "readme": readme, "verified": True}
                append_jsonl(LEARNING_FILE, {k: rec[k] for k in ("id", "question", "code", "answer")})
                append_jsonl(PAIRS_FILE, rec)
                ok += 1
                print(f"  ✅ (retry) {q['id']} → {ans2}")
            else:
                append_jsonl(FAILED_FILE, {"id": q["id"], "business_id": biz, "question": q["question"],
                                           "as_of_date": q.get("as_of_date"), "gold": gold["answer"],
                                           "pred": ans2, "why": f"{why} | retry: {why2}", "code": code2})
                bad += 1
                print(f"  ❌ (retry) {q['id']} — {why2}")
            time.sleep(args.sleep)

        time.sleep(args.sleep)  # tránh rate limit giữa các batch

    log.close()
    print(f"\n📊 Xong: đúng {ok} | sai {bad} | {(time.time()-t0)/60:.1f} phút")
    print(f"→ {LEARNING_FILE}")


if __name__ == "__main__":
    main()
