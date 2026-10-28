import json
import pandas as pd
from pathlib import Path
import re

BASE_DIR = Path(r"C:\Users\dinht\Downloads\train")
TEST_DIR = BASE_DIR / "public_test"
DATA_DIR = TEST_DIR / "data"
OUTPUT_SCHEMA = BASE_DIR / "schema_map_public.json"

def normalize(text):
    text = str(text).lower()
    patterns = {'[àáảãạăằắẳẵặâầấẩẫậ]': 'a', '[èéẻẽẹêềếểễệ]': 'e','[ìíỉĩị]': 'i', '[òóỏõọôồốổỗộơờớởỡợ]': 'o','[ùúủũụưừứửữự]': 'u', '[ỳýỷỹỵ]': 'y', '[đ]': 'd'}
    for p, r in patterns.items(): text = re.sub(p, r, text)
    return re.sub(r'\s+', ' ', text).strip()

def find_col(cols, keywords):
    for c in cols:
        c_norm = normalize(c)
        for kw in keywords:
            if kw in c_norm: return c
    return None

def main():
    schema_map = {}
    if not DATA_DIR.exists():
        print(f"❌ Không tìm thấy thư mục {DATA_DIR}")
        return

    for biz_dir in DATA_DIR.iterdir():
        if not biz_dir.is_dir(): continue
        biz_id = biz_dir.name
        print(f"🔍 Đang dò schema cho: {biz_id}")
        
        tables = {}
        # 1. Quét tất cả file để lấy tên cột
        for f in biz_dir.iterdir():
            if f.name.startswith("~$") or f.suffix.lower() not in [".csv", ".xlsx"]: continue
            try:
                if f.suffix.lower() == ".csv":
                    df = pd.read_csv(f, nrows=0)
                    tables[f.stem] = df.columns.tolist()
                elif f.suffix.lower() == ".xlsx":
                    xls = pd.ExcelFile(f)
                    for sheet in xls.sheet_names:
                        df = pd.read_excel(f, sheet_name=sheet, nrows=0)
                        key = f.stem if len(xls.sheet_names) == 1 else f"{f.stem}_{sheet}"
                        tables[key] = df.columns.tolist()
            except: pass
        
        # 2. Tự động gán cột dựa trên từ khóa
        biz_cfg = {"schema": {k: v for k, v in tables.items()}, "semantic": {}}
        
        # Tìm bảng doanh thu (thường là bảng có chữ "BanHang" hoặc "HoaDon")
        best_rev_table = next((t for t in tables.keys() if any(k in normalize(t) for k in ["banhang", "hoadon", "donhang"])), list(tables.keys())[0] if tables else None)
        
        if best_rev_table:
            cols = tables[best_rev_table]
            biz_cfg["semantic"]["revenue"] = {
                "file": best_rev_table,
                "date_col": find_col(cols, ["ngay", "thoi gian", "date"]),
                "money_col": find_col(cols, ["tien", "tong", "thanh", "amount", "gia"]),
                "status_col": find_col(cols, ["trang thai", "status", "tinh trang", "xu ly"]),
                "cancelled_values": ["hủy", "huỷ", "đổi trả", "hàng trả về"]
            }
            biz_cfg["semantic"]["order_detail"] = {
                "file": best_rev_table,
                "order_id_col": find_col(cols, ["ma don", "ma hoa don", "so phieu", "ma gd", "id"]),
                "product_col": find_col(cols, ["ten", "san pham", "hang", "mat hang"]),
                "qty_col": find_col(cols, ["so luong", "sl", "slg"]),
                "money_col": find_col(cols, ["tien", "tong", "thanh", "amount"])
            }
            
        # Tìm bảng tồn kho
        best_inv_table = next((t for t in tables.keys() if any(k in normalize(t) for k in ["tonkho", "kho"])), None)
        if best_inv_table:
            cols = tables[best_inv_table]
            biz_cfg["semantic"]["inventory"] = {
                "file": best_inv_table,
                "product_col": find_col(cols, ["ten", "san pham", "hang", "mat hang"]),
                "qty_col": find_col(cols, ["ton", "so luong", "sl", "qty"])
            }
            
        schema_map[biz_id] = biz_cfg
        print(f"   ✅ Xong: {biz_id} (Tìm thấy {len(biz_cfg['semantic'])} field)")

    with open(OUTPUT_SCHEMA, "w", encoding="utf-8") as f:
        json.dump(schema_map, f, ensure_ascii=False, indent=2)
    print(f"\n🎉 Đã lưu schema tự động vào: {OUTPUT_SCHEMA}")

if __name__ == "__main__":
    main()