# schema_inference.py - Bản Fix lỗi JSON Timestamp và tên file
import json
import sqlite3
from pathlib import Path
import pandas as pd
import ollama
import re

BASE_DIR = Path(r"C:\Users\dinht\Downloads\train")
TRAIN_DIR = BASE_DIR / "train"
DATA_DIR = TRAIN_DIR / "data"
SCHEMA_MAP_FILE = BASE_DIR / "schema_map.json"

MODEL_ID = "qwen2.5-coder:1.5b"

def find_header_row(df_raw, max_scan=10):
    best_row, max_valid = 0, 0
    for i in range(min(max_scan, len(df_raw))):
        row = df_raw.iloc[i].astype(str)
        valid = sum(1 for v in row if v != 'nan' and 'Unnamed' not in v)
        if valid > max_valid:
            max_valid, best_row = valid, i
    return best_row

def clean_json_data(records):
    """Chuyển đổi dữ liệu Pandas (Timestamp, NaN) thành kiểu JSON an toàn"""
    clean_records = []
    for record in records:
        clean_rec = {}
        for k, v in record.items():
            if pd.isna(v):
                clean_rec[k] = None
            elif isinstance(v, pd.Timestamp):
                clean_rec[k] = v.strftime('%Y-%m-%d %H:%M:%S')
            else:
                clean_rec[k] = str(v)
        clean_records.append(clean_rec)
    return clean_records

def read_biz_schema(biz_dir):
    schema_dict = {}
    samples = {}
    for file in biz_dir.iterdir():
        if file.name.startswith("~$") or not file.is_file(): continue
        try:
            if file.suffix.lower() == ".csv":
                try: df = pd.read_csv(file, encoding='utf-8', nrows=3)
                except: df = pd.read_csv(file, encoding='cp1258', nrows=3)
                df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
                schema_dict[file.stem] = list(df.columns)
                samples[file.stem] = clean_json_data(df.head(2).to_dict('records'))
            elif file.suffix.lower() == ".xlsx":
                xls = pd.ExcelFile(file)
                for sheet in xls.sheet_names:
                    df_raw = pd.read_excel(file, sheet_name=sheet, header=None, nrows=10)
                    if df_raw.empty: continue
                    h = find_header_row(df_raw)
                    df = pd.read_excel(file, sheet_name=sheet, header=h, nrows=3)
                    df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
                    key = file.stem if len(xls.sheet_names) == 1 else f"{file.stem}_{sheet}"
                    schema_dict[key] = list(df.columns)
                    samples[key] = clean_json_data(df.head(2).to_dict('records'))
            elif file.suffix.lower() in [".sqlite", ".db"]:
                conn = sqlite3.connect(file)
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                for t in [r[0] for r in cur.fetchall()]:
                    df = pd.read_sql_query(f"SELECT * FROM {t} LIMIT 3", conn)
                    schema_dict[t] = list(df.columns)
                    samples[t] = clean_json_data(df.to_dict('records'))
                conn.close()
        except Exception as e:
            pass
    return schema_dict, samples

def infer_semantic_map(biz_id, schema_dict, samples):
    prompt = f"""Bạn là chuyên gia phân tích dữ liệu. Dưới đây là các FILE và CỘT của doanh nghiệp '{biz_id}'.
Hãy xác định vai trò ngữ nghĩa của từng cột quan trọng. CHỈ TRẢ VỀ JSON (không giải thích).

## Lưu ý cực kỳ quan trọng:
- Tên file trong kết quả trả về phải KHỚP CHÍNH XÁC với key trong danh sách Schema bên dưới (không tự thêm đuôi .json, .csv, hay đường dẫn).
- Nếu không tìm thấy cột phù hợp, hãy để giá trị null.

## Schema files:
{json.dumps(schema_dict, ensure_ascii=False, indent=1)}

## Mẫu dữ liệu:
{json.dumps(samples, ensure_ascii=False, indent=1)}

## Output JSON (KHÔNG giải thích, chỉ JSON):
{{
  "revenue": {{"file": "...", "date_col": "...", "money_col": "...", "status_col": "...", "cancelled_values": ["huỷ", "hủy"]}},
  "import": {{"file": "...", "date_col": "...", "money_col": "..."}},
  "inventory": {{"file": "...", "product_col": "...", "qty_col": "..."}},
  "product": {{"file": "...", "name_col": "...", "sku_col": "...", "price_col": "..."}},
  "customer": {{"file": "...", "name_col": "...", "id_col": "..."}},
  "order_detail": {{"file": "...", "order_id_col": "...", "product_col": "...", "qty_col": "...", "money_col": "..."}}
}}
"""
    try:
        resp = ollama.chat(
            model=MODEL_ID,
            messages=[{"role": "user", "content": prompt}],
            options={'temperature': 0.0, 'num_predict': 800, 'num_ctx': 8192}
        )
        raw = resp['message']['content']
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            semantic = json.loads(m.group(0))
            # Hậu kiểm: Sửa lại tên file nếu AI trả về sai key
            for role, info in semantic.items():
                if isinstance(info, dict) and "file" in info:
                    fname = info["file"]
                    if fname not in schema_dict:
                        # Thử tìm key gần đúng (bỏ đuôi, bỏ path)
                        base = Path(fname).stem
                        if base in schema_dict:
                            info["file"] = base
                        else:
                            # Tìm key có chứa base
                            for k in schema_dict.keys():
                                if base in k or k in base:
                                    info["file"] = k
                                    break
            return semantic
    except Exception as e:
        print(f"   ❌ Lỗi infer {biz_id}: {e}")
    return {}

def main():
    schema_map = {}
    businesses = sorted([d for d in DATA_DIR.iterdir() if d.is_dir()])
    print(f"🔍 Có {len(businesses)} biz. Bắt đầu infer schema...\n")
    
    for biz_dir in businesses:
        biz_id = biz_dir.name
        print(f"⏳ [{biz_id}] Đang đọc schema...")
        schema_dict, samples = read_biz_schema(biz_dir)
        print(f"   📂 {len(schema_dict)} file. Đang gọi AI hiểu ngữ nghĩa...")
        semantic = infer_semantic_map(biz_id, schema_dict, samples)
        schema_map[biz_id] = {
            "schema": schema_dict,
            "semantic": semantic,
        }
        print(f"   ✅ {json.dumps(semantic, ensure_ascii=False)[:150]}...\n")
    
    with open(SCHEMA_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(schema_map, f, ensure_ascii=False, indent=2)
    print(f"💾 Đã lưu schema_map.json tại: {SCHEMA_MAP_FILE}")

if __name__ == "__main__":
    main()