# inspect_biz.py
import pandas as pd
import sqlite3
from pathlib import Path
import sys
import os

# SỬA TÊN BIZ BẠN MUỐN XEM Ở ĐÂY
BIZ_ID = "biz_128" 

# Đường dẫn gốc
BASE_DIR = Path(r"C:\Users\dinht\Downloads\train\train\data")
BIZ_DIR = BASE_DIR / BIZ_ID

def inspect():
    print("=" * 100)
    print(f"🔍 ĐANG PHÂN TÍCH CHI TIẾT DOANH NGHIỆP: {BIZ_ID}")
    print("=" * 100)

    if not BIZ_DIR.exists():
        print(f"❌ LỖI: Thư mục không tồn tại!")
        print(f"👉 Đường dẫn kiểm tra: {BIZ_DIR}")
        print(f"👉 Bạn hãy chắc chắn đã copy thư mục '{BIZ_ID}' vào trong 'train/data/'")
        return

    # 1. In README (nếu có)
    readme_path = BIZ_DIR / "README.md"
    if readme_path.exists():
        print("\n📄 NỘI DUNG FILE README.MD:")
        print("-" * 50)
        print(readme_path.read_text(encoding="utf-8")[:1000]) # In 1000 ký tự đầu
        print("-" * 50)
    else:
        print("\n⚠️ Không có file README.md")

    # 2. Quét và in dữ liệu của từng file
    files = list(BIZ_DIR.glob("*.*"))
    print(f"\n📂 TÌM THẤY {len(files)} FILE DỮ LIỆU:")
    
    for file in files:
        if file.suffix.lower() not in [".csv", ".xlsx", ".sqlite"]:
            continue
            
        print("\n" + "=" * 80)
        print(f"📄 FILE: {file.name} (Định dạng: {file.suffix})")
        print("=" * 80)

        try:
            if file.suffix.lower() == ".csv":
                df = pd.read_csv(file)
                print(f"✅ Đọc thành công! Số dòng: {len(df)}, Số cột: {len(df.columns)}")
                print(f"👉 Tên các cột: {list(df.columns)}")
                print("\n📊 5 DÒNG DỮ LIỆU ĐẦU TIÊN:")
                print(df.head(5).to_string()) # In dạng bảng CLI

            elif file.suffix.lower() == ".xlsx":
                df = pd.read_excel(file)
                print(f"✅ Đọc thành công! Số dòng: {len(df)}, Số cột: {len(df.columns)}")
                print(f"👉 Tên các cột: {list(df.columns)}")
                print("\n📊 5 DÒNG DỮ LIỆU ĐẦU TIÊN:")
                print(df.head(5).to_string())

            elif file.suffix.lower() == ".sqlite":
                conn = sqlite3.connect(file)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [r[0] for r in cursor.fetchall()]
                print(f"✅ Kết nối SQLite thành công! Các bảng có trong file: {tables}")
                
                for table in tables:
                    df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5", conn)
                    # Lấy tổng số dòng
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    total_rows = cursor.fetchone()[0]
                    
                    print(f"\n📊 BẢNG '{table}' (Tổng số dòng: {total_rows}):")
                    print(f"👉 Tên các cột: {list(df.columns)}")
                    print("5 dòng đầu tiên:")
                    print(df.to_string())
                conn.close()

        except Exception as e:
            print(f"❌ Lỗi khi đọc file này: {e}")

if __name__ == "__main__":
    inspect()