"""
run_self_learning.py — Giáo viên (LLM lớn) dạy học sinh (Qwen nhỏ) bằng gold answer.

Luồng:
  1. Học sinh (Ollama qwen2.5-coder:*) viết code cho câu hỏi.
  2. Chạy code, so với gold. Sai -> gọi Giáo viên (Groq/DeepSeek):
     phân tích nguyên nhân, sửa code, rút ra bài học (JSON).
  3. Code Giáo viên sửa PHẢI chạy ra đúng gold mới được lưu (verified).
  4. Ghi ra:
       distill/learning.jsonl  — id, question, code đã đúng, answer, rule
       distill/sft.jsonl       — dataset chat để fine-tune (system/user/assistant)
       distill/rules.md        — bài học tổng quát (nhét lại vào prompt học sinh)
       distill/failed.jsonl    — câu bó tay
       distill/logs/*.md       — log chi tiết

Chạy:
  python run_self_learning.py --limit 20
  python run_self_learning.py --limit 200 --student qwen2.5-coder:1.5b --max-retries 3
  python run_self_learning.py --teacher deepseek --limit 50
"""
import argparse
import json
import re
import sys
import time
import requests
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
if (BASE_DIR / "vendor").exists():          # thư viện cài thủ công (peft/accelerate/openpyxl...)
    sys.path.insert(0, str(BASE_DIR / "vendor"))

from utils import load_biz_data, get_readme, get_full_schema, execute_ai_code, clean_code_text
from pipeline import format_ans, check_correct

# ================= CẤU HÌNH =================
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5-coder:7b"

TEACHERS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key": "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",
        "model": "openai/gpt-oss-120b",
    },
    "deepseek": {
        "url": "https://api.deepseek.com/v1/chat/completions",
        "key": "",  # điền key DeepSeek nếu dùng
        "model": "deepseek-chat",
    },
}

BASE = Path("C:/Users/dinht/Downloads/train")
TRAIN_DIR = BASE / "train"
DATA_DIR = TRAIN_DIR / "data"
QUESTIONS_FILE = TRAIN_DIR / "questions.jsonl"
ANSWERS_FILE = TRAIN_DIR / "answers.jsonl"
RULEBOOK_FILE = TRAIN_DIR / "rulebook.md"

DISTILL_DIR = BASE / "distill"
LOG_DIR = DISTILL_DIR / "logs"
for _d in (DISTILL_DIR, LOG_DIR):
    _d.mkdir(exist_ok=True)

LEARNING_FILE = DISTILL_DIR / "learning.jsonl"
SFT_FILE = DISTILL_DIR / "sft.jsonl"
RULE_FILE = DISTILL_DIR / "rules.md"
FAILED_FILE = DISTILL_DIR / "failed.jsonl"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) self-learning/1.0"

# ================= PROMPT =================
STUDENT_SYSTEM = """Bạn là chuyên gia Python Pandas giải câu hỏi dữ liệu bán hàng.

MÔI TRƯỜNG CÓ SẴN:
- `dfs`: dict {tên_bảng: DataFrame}
- `get_df_by_keyword(dfs, ['Tên_Bảng'])`: lấy 1 bảng theo tên gần đúng
- `get_all_dfs_by_keyword(dfs, ['Tên_Bảng'])`: gộp tất cả bảng khớp (dữ liệu chia theo tháng)
- `parse_date_safe(series)`, `clean_money(series)`, `clean_number(series)`, `normalize_id(series)`
- `as_of_date`: ngày chốt (pd.Timestamp)
- `pd`, `np`

QUY TẮC BẮT BUỘC:
1. Chỉ dùng cột có trong schema được cung cấp.
2. Luôn kiểm tra rỗng: `if df is None or len(df) == 0: ans, ans_type = None, "unanswerable"`.
3. Đơn huỷ/trả hàng không được tính doanh thu, số đơn.
4. Gán `ans` và `ans_type` ("number", "percent", "string", "date", "boolean", "list").
5. Không dùng `print()`, không đọc file, không gọi API, KHÔNG hardcode ngày (dùng `as_of_date`).

TRẢ LỜI: chỉ một block ```python ...``` duy nhất, không giải thích."""

TEACHER_SYSTEM_PROMPT = """Bạn là một Chuyên gia Data Engineer (Giáo viên) cấp cao. Học sinh của bạn (Qwen 1.5B/7B) vừa viết code sai. Nhiệm vụ của bạn là:
1. Phân tích chính xác nguyên nhân gốc rễ (Root Cause) tại sao code sai.
2. Sửa lại code Python để ra đúng đáp án (Gold).
3. Rút ra một BÀI HỌC TỔNG QUÁT (General Rule) để lần sau học sinh gặp dạng câu tương tự sẽ không bao giờ mắc lại lỗi này.

### 1. THÔNG TIN ĐẦU VÀO:
- Câu hỏi: {question}
- Ngày chốt (as_of_date): {as_of_date}
- Đáp án đúng (Gold): {gold_answer}
- Kết quả sai của học sinh: {wrong_output}
- README (Quy tắc quy đổi đơn vị): {readme}
- RULEBOOK (Luật thời gian, xếp hạng): {rulebook}
- Schema dữ liệu: {schema}
- Code sai của học sinh:
```python
{student_code}
```

### 2. CÁC BẪY THƯỜNG GẶP CẦN KIỂM TRA (BẮT BUỘC ĐỌC):
- **Bẫy Đơn Vị (Đọc kỹ README):** Học sinh có quên quy đổi "bó" sang "cây", "thùng" sang "lon", "lốc" sang "chai" không?
- **Bẫy Thời Gian (Đọc kỹ RULEBOOK):** "Quý 4" là tháng 10, 11, 12. "Tháng này" tính từ ngày 1 đến `as_of_date`. "Tuần trước" bắt đầu từ Thứ 2.
- **Bẫy Lọc Đơn:** Học sinh có quên lọc các đơn có trạng thái chứa 'hủy', 'huỷ', 'trả' không?
- **Bẫy Format:** Đáp án phải là `int`, `float`, hoặc `list`. Không trả về string chứa chữ.
- **Bẫy Code:** Không dùng `print()`, không đọc file. Phải dùng các hàm `get_df_by_keyword`, `parse_date_safe`, `clean_money`, `clean_number`, `normalize_id`. TUYỆT ĐỐI KHÔNG hardcode ngày/tháng — luôn dùng biến `as_of_date`.

### 3. YÊU CẦU ĐẦU RA (BẮT BUỘC TRẢ VỀ JSON CHUẨN):
Bạn chỉ được phép trả về một chuỗi JSON duy nhất (không có markdown bao quanh, không giải thích bên ngoài), theo cấu trúc sau:
{{
  "reason": "Phân tích chi tiết lỗi",
  "fixed_code": "Code Python đã sửa hoàn chỉnh. Chỉ trả về code, không bao gồm markdown.",
  "new_rule": "Một quy tắc tổng quát dạng mệnh lệnh, ngắn gọn, áp dụng cho lần sau."
}}

### 4. VÍ DỤ (FEW-SHOT):
Input:
- Câu hỏi: "Tháng 5/2026 bán ra bao nhiêu cây Ống PVC D50?"
- Gold: 68
- Wrong: 8
- README: "1 bó Ống PVC = 10 cây".
- Code sai: ans = df['Số lượng'].sum()  (quên quy đổi bó, quên lọc đơn trả).

Output JSON:
{{
  "reason": "Học sinh tính tổng cột Số lượng trực tiếp mà không quy đổi đơn vị 'bó' thành 'cây' (1 bó = 10 cây), đồng thời không lọc bỏ đơn trả hàng.",
  "fixed_code": "df = get_df_by_keyword(dfs, ['SoBanHang'])\\nif df is not None and len(df) > 0:\\n    df = df[~df['Trạng thái'].astype(str).str.lower().str.contains('hủy|huỷ|trả', na=False)]\\n    qty = clean_number(df['Số lượng'])\\n    is_bo = df['ĐVT'].astype(str).str.lower().str.contains('bó', na=False)\\n    qty = qty.where(~is_bo, qty * 10)\\n    ans = int(qty.sum())\\n    ans_type = 'number'\\nelse:\\n    ans, ans_type = None, 'unanswerable'",
  "new_rule": "Với sản phẩm tính theo 'bó', PHẢI nhân 10 để quy ra 'cây' trước khi cộng. LUÔN lọc bỏ đơn 'trả hàng' và 'hủy' trước khi tính."
}}"""


# ================= GỌI MODEL =================
def ollama_chat(messages, model, timeout=600, temperature=0.0):
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature, "num_ctx": 16384},
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=timeout,
                      headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    return r.json().get("message", {}).get("content", "")


def teacher_chat(prompt, cfg, retries=3, timeout=180):
    payload = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 3000,
    }
    last = None
    for attempt in range(retries):
        try:
            res = requests.post(cfg["url"], json=payload, timeout=timeout,
                                headers={"Authorization": f"Bearer {cfg['key']}",
                                         "Content-Type": "application/json",
                                         "User-Agent": USER_AGENT})
            if res.status_code == 429:
                m = re.search(r"try again in ([\d.]+)s", res.text)
                time.sleep(float(m.group(1)) + 1 if m else 10)
                continue
            if res.status_code != 200:
                return None, f"HTTP {res.status_code}: {res.text[:200]}"
            choice = res.json()["choices"][0]
            content = (choice.get("message") or {}).get("content")
            if not content:
                last = f"content rỗng (finish_reason={choice.get('finish_reason')})"
                time.sleep(2)
                continue
            return content, None
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            time.sleep(2 * (attempt + 1))
    return None, last


def parse_json_block(text):
    """Parse JSON từ output LLM: bỏ fence, cắt từ { đầu đến } cuối, và escape newline thô trong string."""
    if not text:
        return None

    def esc_ctrl(s):
        out, in_str, esc = [], False, False
        for ch in s:
            if in_str:
                if esc:
                    out.append(ch); esc = False
                elif ch == "\\":
                    out.append(ch); esc = True
                elif ch == '"':
                    in_str = False; out.append(ch)
                elif ch == "\n":
                    out.append("\\n")
                elif ch == "\r":
                    pass
                elif ch == "\t":
                    out.append("\\t")
                else:
                    out.append(ch)
            else:
                if ch == '"':
                    in_str = True
                out.append(ch)
        return "".join(out)

    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j <= i:
        return None
    cand = t[i:j + 1]
    for attempt in (cand, esc_ctrl(cand)):
        try:
            return json.loads(attempt)
        except Exception:
            continue
    return None


def extract_code(text):
    if not text:
        return None
    m = re.search(r"```(?:python|py)?\s*\r?\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"```(?:python|py)?\s*\r?\n(.*)$", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


# ================= DỮ LIỆU =================
def read_jsonl(path):
    if not Path(path).exists():
        return []
    with open(path, "r", encoding="utf-8-sig") as f:
        return [json.loads(l) for l in f if l.strip()]


def build_student_messages(question, as_of, schema, readme, rules, examples):
    ex = ""
    for e in examples:
        ex += f"\n--- VÍ DỤ ĐÃ GIẢI ĐÚNG ---\nCâu hỏi: {e['question']}\n```python\n{e['code']}\n```\n"
    user = f"""Câu hỏi: {question}
Ngày chốt (as_of_date): {as_of}

README (quy ước quy đổi đơn vị):
{readme}

SCHEMA CÁC BẢNG VÀ CỘT:
{schema}

BÀI HỌC ĐÃ RÚT RA (BẮT BUỘC TUÂN THỦ):
{rules or '(chưa có)'}
{ex}
Viết code Python (Pandas) giải quyết câu hỏi trên, dùng `dfs` và các hàm có sẵn.
CHỈ trả về một block ```python ...``` duy nhất, không giải thích."""
    return [{"role": "system", "content": STUDENT_SYSTEM},
            {"role": "user", "content": user}]


def similar_examples(question, knowledge, k=2):
    words = [w for w in re.findall(r"\w+", question.lower()) if len(w) > 2]
    scored = []
    for item in knowledge:
        q = item["question"].lower()
        score = sum(1 for w in words if w in q)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [it for _, it in scored[:k]]


def verify(code, dfs, question, as_of_ts, gold):
    res, _r, typ, err = execute_ai_code(code, dfs, question, as_of_ts)
    if err:
        return None, f"lỗi runtime: {err}"
    ans = format_ans(res, typ, question)
    return ans, (None if check_correct(ans, gold) else f"sai: ra {ans}, gold {gold['answer']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--student", default=OLLAMA_MODEL)
    ap.add_argument("--teacher", choices=list(TEACHERS), default="groq")
    ap.add_argument("--teacher-model", default=None)
    ap.add_argument("--max-retries", type=int, default=3, help="Số lần học sinh thử lại")
    ap.add_argument("--teacher-retries", type=int, default=2, help="Số lần giáo viên tự sửa lại")
    ap.add_argument("--no-resume", action="store_true")
    args = ap.parse_args()

    cfg = dict(TEACHERS[args.teacher])
    if args.teacher_model:
        cfg["model"] = args.teacher_model

    questions = read_jsonl(QUESTIONS_FILE)
    golds = {g["id"]: g for g in read_jsonl(ANSWERS_FILE)}
    rulebook = RULEBOOK_FILE.read_text(encoding="utf-8") if RULEBOOK_FILE.exists() else ""

    done = set() if args.no_resume else {x["id"] for x in read_jsonl(LEARNING_FILE)}
    failed = {x["id"] for x in read_jsonl(FAILED_FILE)}
    todo = [q for q in questions if q["id"] in golds and q["id"] not in done and q["id"] not in failed]
    todo = todo[args.start: args.start + args.limit]

    rules = RULE_FILE.read_text(encoding="utf-8") if RULE_FILE.exists() else ""
    knowledge = read_jsonl(LEARNING_FILE)

    stamp = datetime.now().strftime("%d_%H_%M")
    log_path = LOG_DIR / f"run_{stamp}.md"
    log = open(log_path, "w", encoding="utf-8")

    def wl(t):
        log.write(t)
        log.flush()

    print(f"🎓 {len(todo)} câu | student={args.student} | teacher={cfg['model']}")
    wl(f"# Self-learning {stamp}\n- student: `{args.student}`\n- teacher: `{cfg['model']}`\n\n")

    stats = {"correct_student": 0, "correct_teacher": 0, "failed": 0, "error": 0}

    for i, q in enumerate(todo):
        qid, biz = q["id"], q["business_id"]
        as_of, question = q.get("as_of_date"), q["question"]
        gold = golds[qid]

        dfs = load_biz_data(biz, DATA_DIR)
        if not dfs:
            stats["error"] += 1
            continue
        schema = get_full_schema(dfs)
        readme = get_readme(biz, DATA_DIR)
        as_of_ts = __import__("pandas").Timestamp(as_of) if as_of else None

        print(f"\n[{i+1}/{len(todo)}] {qid} ({biz}) {question[:70]}")
        wl(f"## {i+1}. {qid} | {biz} | as_of {as_of}\n- **Hỏi**: {question}\n- **Gold**: {gold['answer']} ({gold.get('type')})\n")

        solved = False
        for attempt in range(args.max_retries):
            examples = similar_examples(question, knowledge)
            messages = build_student_messages(question, as_of, schema, readme, rules, examples)
            try:
                text = ollama_chat(messages, args.student)
            except Exception as e:
                print(f"   ⚠️ Ollama lỗi: {e}")
                time.sleep(3)
                continue

            code = extract_code(text)
            if not code:
                print(f"   ⚠️ Học sinh không trả code (raw {len(text)} ký tự)")
                wl(f"- Học sinh không trả code. Raw:\n```\n{text[:800]}\n```\n")
                continue

            ans, why = verify(code, dfs, question, as_of_ts, gold)
            if why is None:
                print(f"   ✅ Học sinh đúng: {ans}")
                wl(f"- Lần {attempt+1}: ✅ học sinh đúng ({ans})\n")
                save_learning(qid, biz, as_of, question, code, ans, "student", "", dfs, gold, schema, readme, rules)
                stats["correct_student"] += 1
                solved = True
                break

            print(f"   ❌ Lần {attempt+1}: {why}")
            wl(f"- Lần {attempt+1}: ❌ {why}\n")

            prompt = TEACHER_SYSTEM_PROMPT.format(
                question=question, as_of_date=as_of, gold_answer=gold["answer"],
                wrong_output=ans if ans is not None else why,
                readme=readme[:4000], rulebook=rulebook[:3000],
                schema=schema[:7000], student_code=code)

            saved = False
            for t_try in range(args.teacher_retries):
                t_text, t_err = teacher_chat(prompt, cfg)
                if not t_text:
                    print(f"   ⚠️ Teacher lỗi: {t_err}")
                    break

                data = parse_json_block(t_text)
                if not data or not data.get("fixed_code"):
                    print("   ⚠️ Teacher trả JSON hỏng")
                    wl(f"- Teacher trả về không parse được:\n```\n{str(t_text)[:1200]}\n```\n")
                    prompt += "\n\nLƯU Ý: chỉ trả về MỘT chuỗi JSON hợp lệ, không thêm chữ nào khác."
                    continue

                fixed = data["fixed_code"].strip().strip("`")
                fixed = re.sub(r"^python\s*\n", "", fixed)
                f_ans, f_why = verify(fixed, dfs, question, as_of_ts, gold)
                if f_why is not None:
                    print(f"   ⚠️ Teacher sửa vẫn sai (lần {t_try+1}): {f_why}")
                    wl(f"- Teacher sửa lần {t_try+1} nhưng vẫn sai: {f_why}\n")
                    prompt += (f"\n\nLƯU Ý: code bạn vừa trả về ra {f_ans}, nhưng ĐÁP ÁN ĐÚNG là "
                               f"{gold['answer']} ({gold.get('type')}). Hãy kiểm tra lại tên cột, "
                               f"bộ lọc đơn huỷ/trả và cách quy đổi đơn vị, rồi sửa lại.")
                    continue

                print(f"   ✅ Teacher sửa đúng: {f_ans} | rule: {str(data.get('new_rule'))[:80]}")
                wl(f"- Teacher ✅ ({f_ans}) — {data.get('reason', '')[:200]}\n")
                save_learning(qid, biz, as_of, question, fixed, f_ans, "teacher",
                              data.get("new_rule", ""), dfs, gold, schema, readme, rules, data.get("reason", ""))
                add_rule(data.get("new_rule", ""))
                rules = RULE_FILE.read_text(encoding="utf-8") if RULE_FILE.exists() else rules
                stats["correct_teacher"] += 1
                saved = True
                break

            if saved:
                solved = True
                break

        if not solved:
            stats["failed"] += 1
            with open(FAILED_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps({"id": qid, "business_id": biz, "question": question,
                                    "as_of_date": as_of, "gold": gold["answer"]},
                                   ensure_ascii=False) + "\n")
            wl("- **Kết quả**: THẤT BẠI\n\n")

    wl(f"\n## Tổng kết\n- Học sinh tự đúng: {stats['correct_student']}\n"
       f"- Teacher sửa được: {stats['correct_teacher']}\n- Thất bại: {stats['failed']}\n")
    log.close()

    print("\n" + "=" * 50)
    print(f"Học sinh đúng: {stats['correct_student']} | Teacher cứu: {stats['correct_teacher']} "
          f"| Thất bại: {stats['failed']}")
    print(f"SFT: {SFT_FILE} ({len(read_jsonl(SFT_FILE))} mẫu)")
    print(f"Log: {log_path}")


def save_learning(qid, biz, as_of, question, code, ans, source, rule, dfs, gold, schema, readme, rules, reason=""):
    code = clean_code_text(code)
    rec = {"id": qid, "business_id": biz, "as_of_date": as_of, "question": question,
           "code": code, "answer": ans, "source": source, "rule": rule, "reason": reason,
           "gold": gold["answer"], "gold_type": gold.get("type")}
    with open(LEARNING_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Dataset chat: system cố định, user chứa schema/readme/rules, assistant là code
    user = f"""Câu hỏi: {question}
Ngày chốt (as_of_date): {as_of}

README (quy ước quy đổi đơn vị):
{readme}

SCHEMA CÁC BẢNG VÀ CỘT:
{schema}

BÀI HỌC ĐÃ RÚT RA (BẮT BUỘC TUÂN THỦ):
{rules or '(chưa có)'}

Viết code Python (Pandas) giải quyết câu hỏi trên, dùng `dfs` và các hàm có sẵn.
CHỈ trả về một block ```python ...``` duy nhất, không giải thích."""
    sft = {"id": qid, "messages": [
        {"role": "system", "content": STUDENT_SYSTEM},
        {"role": "user", "content": user},
        {"role": "assistant", "content": f"```python\n{code}\n```"},
    ], "meta": {"business_id": biz, "as_of_date": as_of, "answer": ans,
                "source": source, "gold": gold["answer"], "rule": rule}}
    with open(SFT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(sft, ensure_ascii=False) + "\n")

    # Biến thể 2: chỉ đưa câu hỏi + schema (không kèm rules) để model không phụ thuộc rules
    user2 = f"""Câu hỏi: {question}
Ngày chốt (as_of_date): {as_of}

README (quy ước quy đổi đơn vị):
{readme}

SCHEMA CÁC BẢNG VÀ CỘT:
{schema}"""
    sft2 = {"id": qid + "_norule", "messages": [
        {"role": "system", "content": STUDENT_SYSTEM},
        {"role": "user", "content": user2},
        {"role": "assistant", "content": f"```python\n{code}\n```"},
    ], "meta": {"business_id": biz, "as_of_date": as_of, "answer": ans,
                "source": source, "gold": gold["answer"], "rule": rule}}
    with open(SFT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(sft2, ensure_ascii=False) + "\n")


def add_rule(rule):
    rule = (rule or "").strip()
    if len(rule) < 15:
        return
    existing = RULE_FILE.read_text(encoding="utf-8") if RULE_FILE.exists() else ""
    if rule in existing:
        return
    line = f"- {rule}"
    with open(RULE_FILE, "a", encoding="utf-8") as f:
        if not existing:
            f.write("# Bài học rút ra (Dynamic Rulebook)\n\n")
        f.write(line + "\n")


if __name__ == "__main__":
    main()
