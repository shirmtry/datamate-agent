# run_pipeline_public.py - Chạy tính toán cho tập public_test
import json
import re
import gc
from datetime import datetime, timedelta
from pathlib import Path
from calendar import monthrange
from collections import Counter
import pandas as pd
import warnings

# Tắt cảnh báo rác
warnings.filterwarnings("ignore", category=UserWarning, module="pandas")

BASE_DIR        = Path(r"C:\Users\dinht\Downloads\train")
PUBLIC_DIR      = BASE_DIR / "public_test"
DATA_DIR        = PUBLIC_DIR / "data"
OUTPUT_FILE     = BASE_DIR / "submission_public.jsonl"
SCHEMA_MAP_FILE = BASE_DIR / "schema_map_public.json"

# ================== UTILS ==================
def normalize(text):
    text = str(text).lower()
    patterns = {
        '[àáảãạăằắẳẵặâầấẩẫậ]': 'a', '[èéẻẽẹêềếểễệ]': 'e',
        '[ìíỉĩị]': 'i', '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
        '[ùúủũụưừứửữự]': 'u', '[ỳýỷỹỵ]': 'y', '[đ]': 'd'
    }
    for p, r in patterns.items():
        text = re.sub(p, r, text)
    return re.sub(r'\s+', ' ', text).strip()

def to_money(series):
    def _parse_one(x):
        if pd.isna(x): return 0.0
        s = str(x).strip()
        if not s or s.lower() in ('nan', 'none', 'n/a', ''): return 0.0
        s = re.sub(r'[đĐ$₫\s]', '', s).replace('vnđ', '').replace('VND', '')
        n_dot = s.count('.'); n_comma = s.count(',')
        if n_dot > 0 and n_comma > 0:
            if s.rfind('.') > s.rfind(','): s = s.replace(',', '').replace('.', '#').replace('#', '.')
            else: s = s.replace('.', '').replace(',', '.')
        elif n_comma > 0:
            parts = s.split(',')
            if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]): s = s.replace(',', '')
            else: s = s.replace(',', '.')
        elif n_dot > 0:
            parts = s.split('.')
            if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]): s = s.replace('.', '')
        try: return float(s)
        except: return 0.0
    return series.apply(_parse_one)

def parse_dates(series):
    s = series.astype(str).str.strip()
    if len(s) == 0: return pd.Series(dtype='datetime64[ns]')
    try:
        res = pd.to_datetime(s, errors='coerce', dayfirst=True)
        if res.notna().sum() > 0.5 * len(res): return res
    except: pass
    for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d'):
        try:
            res = pd.to_datetime(s, format=fmt, errors='coerce')
            if res.notna().sum() > 0.5 * len(res): return res
        except: pass
    return pd.to_datetime(s, dayfirst=True, errors='coerce')

def get_period(question, as_of_date_str):
    try:
        q = normalize(question)
        today = pd.to_datetime(as_of_date_str).normalize()
        if re.search(r'\b(hnay|hom nay|ngay hom nay)\b', q): return today, today
        if re.search(r'\b(hqua|hom qua)\b', q):
            y = today - timedelta(days=1); return y, y
        m = re.search(r'(\d+)\s*ngay\s*(?:gan nhat|truoc)', q)
        if m:
            n = int(m.group(1)); return today - timedelta(days=n - 1), today
        if re.search(r'\b(thang nay)\b', q): return today.replace(day=1), today
        m = re.search(r'thang\s*(\d{1,2})(?:[/\-\s](\d{4}))?', q)
        if m:
            month = int(m.group(1)); year = int(m.group(2)) if m.group(2) else today.year
            if not m.group(2) and month > today.month: year -= 1
            start = pd.Timestamp(year=year, month=month, day=1)
            end = pd.Timestamp(year=year, month=month, day=monthrange(year, month)[1])
            return start, min(end, today)
        m = re.search(r'quy\s*(\d)(?:[/\-\s](\d{4}))?', q)
        if m:
            q_num = int(m.group(1)); year = int(m.group(2)) if m.group(2) else today.year
            start_month = 3 * q_num - 2
            start = pd.Timestamp(year=year, month=start_month, day=1)
            end_month = start_month + 2
            end = pd.Timestamp(year=year, month=end_month, day=monthrange(year, end_month)[1])
            return start, min(end, today)
        if re.search(r'\b(tuan nay)\b', q):
            start = today - timedelta(days=today.weekday()); return start, today
        if re.search(r'\b(tuan truoc|tuan roi)\b', q):
            start = today - timedelta(days=today.weekday() + 7); end = start + timedelta(days=6)
            return start, end
        if re.search(r'\b(nam nay)\b', q): return pd.Timestamp(year=today.year, month=1, day=1), today
        m = re.search(r'nam\s*(\d{4})', q)
        if m:
            year = int(m.group(1)); return pd.Timestamp(year=year, month=1, day=1), pd.Timestamp(year=year, month=12, day=31)
        m = re.search(r'ngay\s*(\d{1,2})/(\d{1,2})(?:/(\d{4}))?', q)
        if m:
            day = int(m.group(1)); month = int(m.group(2)); year = int(m.group(3)) if m.group(3) else today.year
            d = pd.Timestamp(year=year, month=month, day=day); return d, d
        return today, today
    except: return None

def filter_by_date(df, date_col, start, end):
    if date_col not in df.columns: return df.iloc[0:0]
    cache_col = f"__parsed_{date_col}"
    dates = df[cache_col] if cache_col in df.columns else parse_dates(df[date_col])
    return df[(dates >= start) & (dates <= end)]

def is_cancelled(df, status_col, cancelled_values):
    if status_col not in df.columns: return pd.Series([False] * len(df), index=df.index)
    if not cancelled_values: cancelled_values = ["huỷ", "hủy", "đã hủy", "cancelled", "hàng trả về", "trả lại"]
    status_norm = df[status_col].astype(str).str.lower().apply(normalize)
    pattern = "|".join([normalize(v) for v in cancelled_values])
    return status_norm.str.contains(pattern, na=False)

# ================== INTENT PARSER ==================
def detect_intent(question):
    q = normalize(question)
    if re.search(r'(ti le|ty le).*(huy|huy don|don huy)', q) or "ti le don huy" in q: return "cancel_rate"
    if re.search(r'(bao nhieu|may|dem|so).*(don hang|don)', q) and "huy" not in q: return "order_count"
    if re.search(r'(top|ban chay|hot nhat|chay nhat|nhieu nhat)', q) and re.search(r'(san pham|mat hang|hang)', q): return "top_products"
    if re.search(r'(top|nhieu tien nhat|mua nhieu|chi tieu)', q) and re.search(r'(khach)', q): return "top_customers"
    if re.search(r'(ton kho|ton|con lai|con bao nhieu)', q) and not re.search(r'(doanh thu|thu duoc)', q): return "inventory"
    if re.search(r'(cong no|con no|no cua hang|khach no)', q): return "debt"
    if re.search(r'(phieu nhap|nhap hang|tien nhap|gia nhap)', q): return "imports"
    if re.search(r'(doanh thu|thu duoc|ban duoc|tong tien|dthu)', q): return "revenue"
    return "revenue"

# ================== PROCESSING ==================
def process_question(q, dfs, semantic):
    period = get_period(q["question"], q["as_of_date"])
    if period is None: return None, None
    start, end = period
    intent = detect_intent(q["question"])
    
    try:
        if intent == "revenue":
            rev = semantic.get("revenue") or {}
            f = rev.get("file")
            if not f or f not in dfs or rev.get("date_col") not in dfs[f].columns: return None, None
            df_period = filter_by_date(dfs[f], rev["date_col"], start, end)
            df_period = df_period[~is_cancelled(df_period, rev["status_col"], rev.get("cancelled_values"))]
            return float(to_money(df_period[rev["money_col"]]).sum()) if not df_period.empty else 0.0, "number"
            
        if intent == "cancel_rate":
            rev = semantic.get("revenue") or {}
            f = rev.get("file")
            if not f or f not in dfs: return None, None
            df_period = filter_by_date(dfs[f], rev["date_col"], start, end)
            if len(df_period) == 0: return 0.0, "percent"
            cancelled = int(is_cancelled(df_period, rev["status_col"], rev.get("cancelled_values")).sum())
            return round(cancelled / len(df_period) * 100, 2), "percent"
            
        if intent == "inventory":
            inv = semantic.get("inventory") or {}
            f = inv.get("file")
            if not f or f not in dfs: return None, None
            df = dfs[f]
            if inv.get("qty_col") not in df.columns: return None, None
            return float(pd.to_numeric(df[inv["qty_col"]].astype(str).str.replace(',', '', regex=False), errors='coerce').sum()), "number"
            
        if intent == "top_products":
            od = semantic.get("order_detail") or {}; rev = semantic.get("revenue") or {}
            f_od, f_rev = od.get("file"), rev.get("file")
            if not f_od or not f_rev or f_od not in dfs or f_rev not in dfs: return None, None
            if rev.get("date_col") not in dfs[f_rev].columns: return None, None
            df_rev_period = filter_by_date(dfs[f_rev], rev["date_col"], start, end)
            df_rev_period = df_rev_period[~is_cancelled(df_rev_period, rev["status_col"], rev.get("cancelled_values"))]
            oid = od.get("order_id_col")
            valid_ids = set(df_rev_period[oid].dropna().unique()) if oid and oid in df_rev_period.columns else None
            df_od_period = dfs[f_od][dfs[f_od][oid].isin(valid_ids)] if valid_ids is not None and oid in dfs[f_od].columns else dfs[f_od]
            if df_od_period.empty: return [], "list"
            qty = pd.to_numeric(df_od_period[od["qty_col"]].astype(str).str.replace(',', '', regex=False), errors='coerce')
            top = df_od_period.assign(_qty=qty).groupby(od["product_col"])['_qty'].sum().nlargest(3)
            return [str(x) for x in top.index.tolist()], "list"
    except Exception:
        pass
    return None, None

def format_record(q_id, ans, ans_type):
    if (ans is None or (isinstance(ans, list) and len(ans) == 0) or (isinstance(ans, float) and pd.isna(ans))):
        return {"id": q_id, "type": "unanswerable", "reason": "Không tính được"}
    if ans_type == "number":
        v = float(ans); return {"id": q_id, "type": "number", "answer": int(v) if v.is_integer() else v}
    if ans_type == "percent": return {"id": q_id, "type": "percent", "answer": round(float(ans), 2)}
    if ans_type == "list": return {"id": q_id, "type": "list", "answer": [str(x) for x in ans]}
    return {"id": q_id, "type": "string", "answer": str(ans)}

def find_header_row(df_raw, max_scan=10):
    best_row, max_valid = 0, 0
    for i in range(min(max_scan, len(df_raw))):
        valid = sum(1 for v in df_raw.iloc[i].astype(str) if v != 'nan' and 'Unnamed' not in v)
        if valid > max_valid: max_valid, best_row = valid, i
    return best_row

# ================== MAIN ==================
def main():
    print("🚀 BẮT ĐẦU CHẠY PUBLIC TEST")
    if not SCHEMA_MAP_FILE.exists():
        print(f"❌ Không tìm thấy {SCHEMA_MAP_FILE}. Hãy chạy auto_schema.py trước!")
        return

    schema_map = json.load(open(SCHEMA_MAP_FILE, "r", encoding="utf-8"))
    q_file = PUBLIC_DIR / "questions.jsonl"
    if not q_file.exists():
        print(f"❌ Không tìm thấy {q_file}")
        return
        
    questions = [json.loads(l) for l in open(q_file, "r", encoding="utf-8") if l.strip()]
    print(f"📥 {len(questions)} câu hỏi\n")
    
    q_by_biz = {}
    for q in questions: q_by_biz.setdefault(q["business_id"], []).append(q)
    
    # Mở file ở chế độ ghi, dùng buffering=1 để ghi ngay lập tức xuống ổ cứng
    with open(OUTPUT_FILE, "w", encoding="utf-8", buffering=1) as f_out:
        for biz_idx, (biz_id, biz_qs) in enumerate(q_by_biz.items(), 1):
            print(f"📁 [{biz_idx:2d}/{len(q_by_biz)}] {biz_id} ({len(biz_qs)} câu)", flush=True)
            
            if biz_id not in schema_map:
                for q in biz_qs:
                    f_out.write(json.dumps({"id": q["id"], "type": "unanswerable"}) + "\n")
                continue

            biz_dir = DATA_DIR / biz_id; dfs = {}
            if biz_dir.exists():
                for f in biz_dir.iterdir():
                    if f.name.startswith("~$") or not f.is_file(): continue
                    try:
                        if f.suffix.lower() == ".csv":
                            try: df = pd.read_csv(f, encoding='utf-8')
                            except: df = pd.read_csv(f, encoding='cp1258')
                            dfs[f.stem] = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
                        elif f.suffix.lower() == ".xlsx":
                            all_sheets = pd.read_excel(f, sheet_name=None, header=None)
                            for sheet_name, df_raw in all_sheets.items():
                                if df_raw.empty: continue
                                h = find_header_row(df_raw)
                                if h < len(df_raw) - 1:
                                    df = df_raw.iloc[h+1:].copy()
                                    df.columns = df_raw.iloc[h]
                                    df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')].dropna(how='all')
                                    key = f.stem if len(all_sheets) == 1 else f"{f.stem}_{sheet_name}"
                                    dfs[key] = df
                    except: pass
            
            # Cache ngày tháng để tăng tốc
            for field_cfg in schema_map[biz_id].get("semantic", {}).values():
                if isinstance(field_cfg, dict) and "date_col" in field_cfg:
                    f_name = field_cfg.get("file"); d_col = field_cfg.get("date_col")
                    if f_name in dfs and d_col in dfs[f_name].columns:
                        cache_name = f"__parsed_{d_col}"
                        if cache_name not in dfs[f_name].columns:
                            dfs[f_name][cache_name] = parse_dates(dfs[f_name][d_col])

            for q in biz_qs:
                ans, ans_type = process_question(q, dfs, schema_map[biz_id].get("semantic", {}))
                rec = format_record(q["id"], ans, ans_type)
                f_out.write(json.dumps(rec, ensure_ascii=False) + "\n") # Ghi ngay vào file
                
            del dfs; gc.collect()
    
    print(f"\n✅ Đã chạy xong toàn bộ! File nộp bài: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()