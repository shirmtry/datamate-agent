"""
run_train.py — DataMate: sinh code Pandas bằng LLM (Groq) từ câu hỏi + schema + rulebook.

Cách dùng:
    python run_train.py                          # train, 30 câu đầu, có chấm điểm
    python run_train.py --limit 5 --start 100    # train, 5 câu từ vị trí 100
    python run_train.py --split public --limit 10 --out submission_public.jsonl
    python run_train.py --split public --use-cache          # dùng lại code đã sinh

Không phụ thuộc `requests` (dùng urllib) để chạy được với mọi bản Python có pandas + openpyxl.
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from utils import load_biz_data, get_full_schema, execute_ai_code

# ================= CẤU HÌNH =================
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-120b"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) run_train/1.0"

SPLITS = {
    "train": {
        "data_dir": BASE_DIR / "train" / "data",
        "questions": BASE_DIR / "train" / "questions.jsonl",
        "answers": BASE_DIR / "train" / "answers.jsonl",
        "rulebook": BASE_DIR / "train" / "rulebook.md",
        "calendar": BASE_DIR / "train" / "calendar.csv",
    },
    "public": {
        "data_dir": BASE_DIR / "public_test" / "data",
        "questions": BASE_DIR / "public_test" / "questions.jsonl",
        "answers": None,
        "rulebook": BASE_DIR / "public_test" / "rulebook.md",
        "calendar": BASE_DIR / "public_test" / "calendar.csv",
    },
}

SYSTEM_PROMPT = """Bạn là một Chuyên gia Phân tích Dữ liệu (Data Engineer) cấp cao, đang tham gia cuộc thi DataMate. Nhiệm vụ của bạn là viết code Python (Pandas) để trả lời câu hỏi tiếng Việt dựa trên dữ liệu được cung cấp.

### 1. THÔNG TIN ĐẦU VÀO
- Câu hỏi: "{question}"
- Ngày chốt (as_of_date): {as_of_date}
- Dữ liệu (Bảng và Cột):
{schema}
- Luật lệ (Rulebook):
{rulebook}

### 2. QUY TẮC SỬ DỤNG HÀM (BẮT BUỘC)
Hệ thống đã cung cấp sẵn các hàm sau, bạn PHẢI sử dụng chúng:
- `get_df_by_keyword(dfs, ['tên_bảng'])`: Lấy bảng dữ liệu (tự động sửa lỗi font, sai tên).
- `get_all_dfs_by_keyword(dfs, ['tên_bảng'])`: Gộp TẤT CẢ bảng khớp thành 1 DataFrame (dùng khi dữ liệu chia theo tháng/quý mà câu hỏi cần nhiều kỳ).
- `parse_date_safe(df['cột'])`: Chuyển đổi cột ngày tháng (xử lý mọi định dạng: dd/mm/yyyy, 1 thg 1 2025...).
- `clean_money(df['cột'])`: Làm sạch cột tiền (xóa dấu phẩy, chữ 'đ', 'VNĐ').
- `clean_number(df['cột'])`: Làm sạch cột số lượng (xóa chữ 'cây', 'lon', 'thùng').
- `normalize_id(df['cột'])`: Chuẩn hóa mã (viết hoa, xóa khoảng trắng) để JOIN bảng.

### 3. LUẬT NGHIỆP VỤ (BẮT BUỘC TUÂN THỦ)
- **Doanh thu**: Chỉ tính đơn KHÔNG HỦY, KHÔNG TRẢ HÀNG. Đơn trả hàng (dù chỉ 1 phần) thì bỏ cả đơn.
- **Số đơn**: Đếm bằng `df['Mã_Đơn'].nunique()`. TUYỆT ĐỐI KHÔNG dùng `len(df)`.
- **Bảng chia theo tháng**: nếu dữ liệu tách bảng theo tháng (vd `DanhSachHoaDon_04.2025`) mà câu hỏi cần nhiều tháng, dùng `get_all_dfs_by_keyword(dfs, ['DanhSachHoaDon'])` để gộp, rồi lọc theo cột ngày.
- **Thời gian**: "Tháng này" = từ ngày 1 đến hết `as_of_date`. "Tuần" bắt đầu từ Thứ 2.
- **Bán chạy**: Xếp hạng theo TỔNG SỐ LƯỢNG (đã quy đổi về đơn vị cơ bản).
- **Lỗi rỗng**: Nếu `df is None` hoặc `len(df) == 0`, gán `ans = None` và `ans_type = "unanswerable"`.

### 4. ĐỊNH DẠNG ĐẦU RA (BẮT BUỘC - NẾU SAI FORMAT SẼ BỊ 0 ĐIỂM)
Bạn phải gán kết quả vào 2 biến: `ans` (giá trị) và `ans_type` (kiểu dữ liệu). Tuyệt đối KHÔNG dùng `print()`.
- Nếu hỏi số lượng/tiền: `ans = int(...)` hoặc `float(...)`, `ans_type = "number"`.
- Nếu hỏi phần trăm: `ans = round(..., 2)`, `ans_type = "percent"`.
- Nếu hỏi tên (sản phẩm, khách): `ans = "Tên"`, `ans_type = "string"`.
- Nếu hỏi ngày: `ans = "YYYY-MM-DD"`, `ans_type = "date"`.
- Nếu hỏi đúng/sai: `ans = True/False`, `ans_type = "boolean"`.
- Nếu hỏi danh sách/top: `ans = ["A", "B"]`, `ans_type = "list"`.
   *Lưu ý List*: Sắp xếp giảm dần theo tiêu chí. Nếu bằng điểm, xếp theo Mã/Tên tăng dần.
- Nếu hỏi bảng: `ans = {{"columns": [...], "rows": [[...]]}}`, `ans_type = "table"`.
- Nếu không có dữ liệu: `ans = None`, `ans_type = "unanswerable"`.

### 5. VÍ DỤ CODE MẪU
```python
# Ví dụ 1: Hỏi doanh thu
df = get_df_by_keyword(dfs, ['DanhSachHoaDon'])
if df is None or len(df) == 0:
    ans, ans_type = None, "unanswerable"
else:
    df['Ngày'] = parse_date_safe(df['Ngày'])
    # Lọc đơn hủy
    df = df[~df['Trạng thái'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)]
    # Lọc tháng
    df_thang = df[(df['Ngày'].dt.year == 2026) & (df['Ngày'].dt.month == 5)]
    ans = int(clean_money(df_thang['Thành tiền']).sum())
    ans_type = "number"

# Ví dụ 2: Hỏi Top 3
df = get_df_by_keyword(dfs, ['ChiTietHoaDon'])
if df is not None:
    df['Số lượng'] = clean_number(df['Số lượng'])
    top3 = df.groupby('Tên sản phẩm')['Số lượng'].sum().reset_index()
    top3 = top3.sort_values(by=['Số lượng', 'Tên sản phẩm'], ascending=[False, True])
    ans = top3['Tên sản phẩm'].head(3).tolist()
    ans_type = "list"
```

NHIỆM VỤ CỦA BẠN
Viết code Python giải quyết câu hỏi trên. CHỈ TRẢ VỀ CODE TRONG BLOCK python .... KHÔNG GIẢI THÍCH."""


# ================= TIỆN ÍCH =================
def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_rulebook(path):
    path = Path(path)
    if not path.exists():
        return "(Không có rulebook)"
    return path.read_text(encoding="utf-8-sig").strip()


def load_calendar(path):
    """calendar.csv -> DataFrame (bảng tra âm lịch) để nhét vào dfs."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        cal = pd.read_csv(path, encoding="utf-8-sig")
        if "date" in cal.columns:
            cal["date"] = pd.to_datetime(cal["date"], errors="coerce")
        return cal
    except Exception:
        return None


def build_prompt(question, as_of_date, schema, rulebook):
    # Prompt đã chứa cặp ngoặc nhọn của dict kết quả -> chỉ .format các trường cần thiết
    return SYSTEM_PROMPT.format(question=question, as_of_date=as_of_date,
                                schema=schema, rulebook=rulebook)


def extract_code(text):
    if not text:
        return None
    m = re.search(r"```(?:python|py)?[ \t]*\r?\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Fence bị cắt cụt (hết max_tokens) -> lấy từ sau dấu ``` đến hết
    m = re.search(r"```(?:python|py)?[ \t]*\r?\n(.*)$", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Không có fence: nếu trông giống code thì lấy luôn
    if re.search(r"^\s*(df|ans|import)\b", text, re.MULTILINE):
        return text.strip()
    return None


def estimate_tokens(text):
    """Ước lượng token (tiếng Việt ~2.5-3 ký tự/token)."""
    return int(len(text) / 2.8) + 1


def wait_from_429(detail, default):
    m = re.search(r"try again in ([\d.]+)\s*s", detail)
    return float(m.group(1)) + 1.0 if m else default


class RateLimiter:
    """Giữ tổng token gửi đi trong 60s dưới hạn TPM của Groq free tier."""

    def __init__(self, tpm=8000, safety=0.85):
        self.budget = int(tpm * safety)
        self.window = []  # [(time, tokens)]

    def wait(self, tokens):
        while True:
            now = time.time()
            self.window = [(t, n) for t, n in self.window if now - t < 60]
            used = sum(n for _, n in self.window)
            if not self.window or used + tokens <= self.budget:
                break
            sleep_for = 60 - (now - self.window[0][0]) + 0.5
            print(f"   ⏳ chờ {sleep_for:.1f}s (TPM {used}/{self.budget})")
            time.sleep(max(sleep_for, 1))
        self.window.append((time.time(), tokens))


def groq_chat(prompt, model=GROQ_MODEL, api_key=GROQ_API_KEY,
              temperature=0.0, max_tokens=3000, retries=4, limiter=None,
              reasoning_effort=None):
    if limiter is not None:
        limiter.wait(estimate_tokens(prompt) + min(max_tokens, 1200))
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort
    body = json.dumps(payload).encode("utf-8")
    last_err = None
    for attempt in range(retries):
        req = urllib.request.Request(
            GROQ_URL,
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as res:
                data = json.loads(res.read().decode("utf-8"))
            choice = data["choices"][0]
            content = (choice.get("message") or {}).get("content")
            if not content:
                last_err = f"content rỗng (finish_reason={choice.get('finish_reason')})"
                time.sleep(2)
                continue
            return content, None
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")[:300]
            last_err = f"HTTP {e.code}: {detail}"
            if e.code == 429:
                time.sleep(wait_from_429(detail, 5 * (attempt + 1)))
                continue
            if e.code in (500, 502, 503, 504):
                time.sleep(2 ** attempt * 2)
                continue
            return None, last_err
        except Exception as e:  # timeout, mạng...
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(2 ** attempt * 2)
    return None, last_err


def normalize_type(t, gold):
    t = (t or "").strip().lower()
    if t in {"number", "percent", "string", "date", "boolean", "list", "table", "unanswerable"}:
        return t
    if gold:
        return gold.get("type", "")
    return t


def compare_answer(pred_type, pred_ans, gold):
    """So khớp theo đúng luật chấm của BTC (evaluate.py)."""
    if gold is None:
        return None
    g_type = gold.get("type", "")
    g_ans = gold.get("answer")
    aliases = gold.get("alias") or []

    if pred_type == "unanswerable":
        return g_type == "unanswerable"
    if g_type == "unanswerable":
        return False
    if pred_type != g_type:
        return False

    if g_type in ("number", "percent"):
        try:
            tol = 1e-6 if g_type == "number" else 0.01
            return abs(float(pred_ans) - float(g_ans)) <= tol
        except Exception:
            return False

    if g_type == "list":
        p = [str(x).strip().lower() for x in (pred_ans or [])]
        g = [str(x).strip().lower() for x in (g_ans or [])]
        if p == g:
            return True
        for alias in aliases:
            if isinstance(alias, list) and p == [str(x).strip().lower() for x in alias]:
                return True
        return False

    if g_type == "table":
        try:
            return json.dumps(pred_ans, ensure_ascii=False, sort_keys=True) == \
                   json.dumps(g_ans, ensure_ascii=False, sort_keys=True)
        except Exception:
            return False

    p_s, g_s = str(pred_ans).strip().lower(), str(g_ans).strip().lower()
    if p_s == g_s:
        return True
    for alias in aliases:
        if isinstance(alias, str) and p_s == alias.strip().lower():
            return True
        if isinstance(alias, list) and p_s in [str(a).strip().lower() for a in alias]:
            return True
    return False


def preview(v, n=120):
    s = str(v)
    return s if len(s) <= n else s[:n] + "..."


# ================= MAIN =================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=list(SPLITS), default="train")
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--model", default=GROQ_MODEL)
    ap.add_argument("--api-key", default=GROQ_API_KEY)
    ap.add_argument("--out", default=None, help="File jsonl dự đoán")
    ap.add_argument("--log", default=None, help="File markdown log")
    ap.add_argument("--rulebook-chars", type=int, default=4000, help="0 = dùng toàn bộ rulebook")
    ap.add_argument("--max-tokens", type=int, default=3000)
    ap.add_argument("--reasoning", default="low", choices=["none", "low", "medium", "high"],
                    help="reasoning_effort cho gpt-oss (low = tốn ít token hơn)")
    ap.add_argument("--tpm", type=int, default=8000, help="Hạn token/phút của tài khoản Groq")
    ap.add_argument("--use-cache", action="store_true", help="Dùng lại code đã sinh (cache/...)")
    ap.add_argument("--repair", type=int, default=1, help="Số lần nhờ AI sửa code khi runtime lỗi")
    args = ap.parse_args()

    cfg = SPLITS[args.split]
    questions = read_jsonl(cfg["questions"])
    gold = read_jsonl(cfg["answers"]) if cfg["answers"] and Path(cfg["answers"]).exists() else []
    gold = {g["id"]: g for g in gold}

    rulebook = load_rulebook(cfg["rulebook"])
    if args.rulebook_chars and len(rulebook) > args.rulebook_chars:
        rulebook = rulebook[: args.rulebook_chars] + "\n... (rulebook bị cắt bớt)"

    calendar = load_calendar(cfg["calendar"])
    limiter = RateLimiter(tpm=args.tpm)
    subset = questions[args.start: args.start + args.limit]

    stamp = datetime.now().strftime("%d_%H_%M")
    out_path = Path(args.out) if args.out else BASE_DIR / f"pred_{args.split}_{stamp}.jsonl"
    log_path = Path(args.log) if args.log else BASE_DIR / f"HUYTKING_{stamp}_{args.split}.md"
    cache_dir = BASE_DIR / "cache_code" / args.split
    if args.use_cache:
        cache_dir.mkdir(parents=True, exist_ok=True)

    print(f"📚 {args.split}: {len(subset)} câu (từ #{args.start}) | model={args.model}")
    print(f"   questions : {cfg['questions']}")
    print(f"   data      : {cfg['data_dir']}")
    print(f"   rulebook  : {len(rulebook)} ký tự | gold: {len(gold)} câu")
    print(f"   out       : {out_path.name} | log: {log_path.name}\n")

    stats = {"correct": 0, "wrong": 0, "abstain": 0, "error": 0, "no_code": 0}
    out_f = open(out_path, "a", encoding="utf-8")
    log_f = open(log_path, "w", encoding="utf-8")

    def wl(t):
        log_f.write(t)
        log_f.flush()

    wl(f"# DataMate {args.split} — {stamp}\n\n- Model: `{args.model}`\n"
       f"- Câu: {len(subset)} (từ #{args.start})\n- Rulebook: {len(rulebook)} ký tự\n\n")

    for i, q in enumerate(subset):
        q_id, question = q["id"], q["question"]
        as_of = q.get("as_of_date")
        g = gold.get(q_id)

        dfs = load_biz_data(q["business_id"], cfg["data_dir"])
        if calendar is not None:
            dfs["calendar"] = calendar
        if not dfs:
            print(f"[{i+1}/{len(subset)}] {q_id} ⚠️ không đọc được dữ liệu")
            wl(f"## {i+1}. {q_id}\n- Hỏi: {question}\n- Lỗi: không đọc được dữ liệu\n\n")
            continue

        schema = get_full_schema(dfs)
        print(f"[{i+1}/{len(subset)}] {q_id} ({q['business_id']}) {preview(question, 90)}")
        wl(f"## {i+1}. {q_id} | {q['business_id']} | as_of {as_of}\n"
           f"- **Hỏi**: {question}\n- **Gold**: {g.get('answer') if g else '(không có)'} "
           f"({g.get('type') if g else '-'})\n")

        # 1) Lấy code: cache -> LLM
        prompt = build_prompt(question, as_of, schema, rulebook)
        code = None
        cache_file = cache_dir / f"{q_id}.py"
        if args.use_cache and cache_file.exists():
            code = cache_file.read_text(encoding="utf-8")
            print("   (cache)")
        if not code:
            text, err = groq_chat(prompt, model=args.model, api_key=args.api_key,
                                  max_tokens=args.max_tokens, limiter=limiter,
                                  reasoning_effort=None if args.reasoning == "none" else args.reasoning)
            if not text:
                stats["error"] += 1
                print(f"   ❌ API lỗi: {err}")
                wl(f"- **Lỗi API**: {err}\n\n")
                continue
            code = extract_code(text)
            if not code:
                stats["no_code"] += 1
                print("   ❌ Không tìm thấy block python")
                wl(f"- **Lỗi**: không tìm thấy block code\n- Raw: {preview(text, 400)}\n\n")
                continue
            if args.use_cache:
                cache_file.write_text(code, encoding="utf-8")

        # 2) Chạy code (as_of_date đưa vào môi trường dưới dạng Timestamp để code dễ tính toán)
        as_of_ts = pd.Timestamp(as_of) if as_of else None
        exec_err = None
        for attempt in range(args.repair + 1):
            wl(f"- **Code** (lần {attempt + 1}):\n```python\n{code}\n```\n")
            res, _reason, typ, exec_err = execute_ai_code(code, dfs, question, as_of_ts)
            if not exec_err or attempt >= args.repair:
                break
            print(f"   ⚠️ Runtime: {preview(exec_err, 90)} → nhờ sửa")
            wl(f"- **Runtime lỗi**: {exec_err}\n")
            fix_prompt = (
                prompt
                + f"\n\nCODE BẠN VỪA VIẾT BỊ LỖI KHI CHẠY:\n```python\n{code}\n```\n"
                + f"LỖI: {exec_err}\n"
                + "Hãy viết lại code đã sửa (chỉ dùng cột có trong danh sách). "
                  "CHỈ TRẢ VỀ CODE TRONG BLOCK python."
            )
            text, api_err = groq_chat(fix_prompt, model=args.model, api_key=args.api_key,
                                      max_tokens=args.max_tokens, limiter=limiter,
                                      reasoning_effort=None if args.reasoning == "none" else args.reasoning)
            if not text:
                wl(f"- **Lỗi sửa code**: {api_err}\n")
                break
            new_code = extract_code(text)
            if not new_code:
                break
            code = new_code
            if args.use_cache:
                cache_file.write_text(code, encoding="utf-8")

        if exec_err:
            stats["error"] += 1
            print(f"   ⚠️ Runtime: {preview(exec_err, 100)}")
            wl(f"- **Runtime lỗi**: {exec_err}\n\n")
            continue

        pred_type = normalize_type(typ, g)
        ans = res
        if ans is not None and pred_type == "date" and isinstance(ans, pd.Timestamp):
            ans = ans.strftime("%Y-%m-%d")

        record = {"id": q_id, "type": pred_type,
                  "answer": json.loads(json.dumps(ans, ensure_ascii=False, default=str))}
        out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
        out_f.flush()

        if g is None:
            print(f"   -> {pred_type}: {preview(ans, 90)}")
            wl(f"- **Dự đoán**: {pred_type} = {preview(ans, 200)}\n\n")
            continue

        ok = compare_answer(pred_type, ans, g)
        if ok:
            stats["correct"] += 1
            print(f"   ✅ {preview(ans, 70)}")
            wl("- **Kết quả**: ✅ ĐÚNG\n\n")
        elif pred_type == "unanswerable":
            stats["abstain"] += 1
            print(f"   ⚪ bỏ qua | gold={preview(g.get('answer'), 60)}")
            wl(f"- **Kết quả**: ⚪ BỎ QUA | Gold: {g.get('answer')}\n\n")
        else:
            stats["wrong"] += 1
            print(f"   ❌ {preview(ans, 60)} | gold={preview(g.get('answer'), 60)} ({g.get('type')})")
            wl(f"- **Kết quả**: ❌ SAI | Gold: {g.get('answer')} ({g.get('type')})\n\n")

    out_f.close()
    log_f.write(f"\n## Tổng kết\n- Đúng: {stats['correct']}\n- Sai: {stats['wrong']}\n"
                f"- Bỏ qua: {stats['abstain']}\n- Lỗi: {stats['error'] + stats['no_code']}\n")
    log_f.close()

    print("\n" + "=" * 55)
    print(f"Đúng: {stats['correct']} | Sai: {stats['wrong']} | "
          f"Bỏ qua: {stats['abstain']} | Lỗi: {stats['error'] + stats['no_code']}")
    if gold and len(subset) > 0:
        score = (stats["correct"] - stats["wrong"]) / len(subset)
        print(f"Điểm ước tính: {score:+.4f}")
    print(f"Pred: {out_path}")
    print(f"Log : {log_path}")


if __name__ == "__main__":
    main()
