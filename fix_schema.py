import json
import pandas as pd
from pathlib import Path
import re

BASE_DIR = Path(r"C:\Users\dinht\Downloads\train")
DATA_DIR = BASE_DIR / "train" / "data"
SCHEMA_FILE = BASE_DIR / "schema_map.json"
OUTPUT_SCHEMA = BASE_DIR / "schema_map_fixed.json"

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

def find_best_col(cols, keywords):
    """Tìm cột phù hợp nhất dựa vào danh sách từ khóa"""
    # 1. Ưu tiên khớp chính xác (normalize)
    for c in cols:
        c_norm = normalize(c)
        for kw in keywords:
            if c_norm == kw:
                return c
    # 2. Khớp chứa từ khóa
    for c in cols:
        c_norm = normalize(c)
        for kw in keywords:
            if kw in c_norm:
                return c
    return None

def get_table_headers(biz_dir):
    """Lấy tên file và danh sách cột của tất cả các bảng trong biz"""
    tables = {}
    if not biz_dir.exists(): return tables
    for f in biz_dir.iterdir():
        if f.name.startswith("~$") or not f.is_file(): continue
        try:
            if f.suffix.lower() == ".csv":
                try: df = pd.read_csv(f, nrows=0, encoding='utf-8')
                except: df = pd.read_csv(f, nrows=0, encoding='cp1258')
                tables[f.stem] = df.columns.tolist()
            elif f.suffix.lower() == ".xlsx":
                xls = pd.ExcelFile(f)
                for sheet in xls.sheet_names:
                    df = pd.read_excel(f, sheet_name=sheet, nrows=0)
                    key = f.stem if len(xls.sheet_names)==1 else f"{f.stem}_{sheet}"
                    tables[key] = df.columns.tolist()
        except:
            pass
    return tables

def main():
    schema_map = json.load(open(SCHEMA_FILE, "r", encoding="utf-8"))
    fixed_count = 0

    for biz_id, biz_cfg in schema_map.items():
        biz_dir = DATA_DIR / biz_id
        tables = get_table_headers(biz_dir)
        if not tables: continue

        # Các cấu hình cho từng field (file, các cột cần tìm)
        configs = {
            "revenue": {
                "cols": ["date_col", "money_col", "status_col"],
                "kw": {"date_col": ["ngay", "thoi gian", "date"], "money_col": ["tien", "tong", "thanh", "amount", "gia"], "status_col": ["trang thai", "tinh trang", "status", "xu ly"]}
            },
            "import": {
                "cols": ["date_col", "money_col"],
                "kw": {"date_col": ["ngay", "thoi gian", "date"], "money_col": ["tien", "tong", "thanh", "amount", "gia"]}
            },
            "inventory": {
                "cols": ["product_col", "qty_col"],
                "kw": {"product_col": ["ten", "san pham", "hang", "mat hang"], "qty_col": ["so luong", "sl", "ton", "qty"]}
            },
            "product": {
                "cols": ["name_col", "price_col"],
                "kw": {"name_col": ["ten", "san pham", "hang", "mat hang"], "price_col": ["gia", "price"]}
            },
            "customer": {
                "cols": ["name_col", "id_col"],
                "kw": {"name_col": ["ten", "khach"], "id_col": ["ma", "id", "sdt", "dien thoai"]}
            },
            "order_detail": {
                "cols": ["order_id_col", "product_col", "qty_col", "money_col"],
                "kw": {"order_id_col": ["ma don", "ma hoa don", "so phieu", "ma gd", "ma bill", "id"], "product_col": ["ten", "san pham", "hang", "mat hang"], "qty_col": ["so luong", "sl", "slg"], "money_col": ["tien", "tong", "thanh", "amount"]}
            }
        }

        for field, cfg in biz_cfg.get("semantic", {}).items():
            if field not in configs: continue
            
            field_cfg = cfg.copy()
            # Đánh dấu là chưa tìm thấy bảng phù hợp
            best_table = None
            best_match_count = 0
            
            # Quét qua TẤT CẢ các bảng trong biz để xem bảng nào khớp nhất
            for t_name, cols in tables.items():
                match_count = 0
                temp_cfg = {}
                
                for c_type in configs[field]["cols"]:
                    found_col = find_best_col(cols, configs[field]["kw"].get(c_type, []))
                    if found_col:
                        match_count += 1
                        temp_cfg[c_type] = found_col
                
                # Nếu bảng này có nhiều cột khớp nhất (VD: có cả Ngày, Tiền, Trạng thái)
                if match_count > best_match_count:
                    best_match_count = match_count
                    best_table = t_name
                    # Lưu lại các cột tìm được
                    for k, v in temp_cfg.items():
                        field_cfg[k] = v

            # Nếu tìm được bảng có số cột khớp >= 2 (hoặc 1 nếu là inventory/customer)
            min_req = 1 if field in ["inventory", "customer", "import"] else 2
            if best_table and best_match_count >= min_req:
                if field_cfg.get("file") != best_table:
                    print(f"[{biz_id}] {field}: Sửa file từ '{cfg.get('file')}' -> '{best_table}'")
                    field_cfg["file"] = best_table
                    fixed_count += 1
                
                # Cập nhật lại các cột đã sửa
                for k, v in field_cfg.items():
                    if k.endswith("_col") and cfg.get(k) != v:
                        print(f"    + Sửa cột {k}: '{cfg.get(k)}' -> '{v}'")
                        cfg[k] = v
                
                cfg["file"] = best_table

    with open(OUTPUT_SCHEMA, "w", encoding="utf-8") as f:
        json.dump(schema_map, f, ensure_ascii=False, indent=2)
        
    print(f"\n✅ Đã sửa tổng cộng {fixed_count} lỗi mapping.")
    print(f"📄 File mới: {OUTPUT_SCHEMA}")

if __name__ == "__main__":
    main()