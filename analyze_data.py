import json
import pandas as pd
import sqlite3
from pathlib import Path

# Trỏ vào thư mục data (nằm trong thư mục train)
TRAIN_DIR = Path("./train")

def analyze():
    print("="*60)
    print("1. ĐỌC RULEBOOK (Quy tắc tính toán)")
    print("="*60)
    rulebook_path = TRAIN_DIR / "rulebook.md"
    if rulebook_path.exists():
        print(rulebook_path.read_text(encoding="utf-8")[:500] + "\n... (còn nữa)")
    
    print("\n" + "="*60)
    print("2. MẪU CÂU HỎI (Questions)")
    print("="*60)
    q_path = TRAIN_DIR / "questions.jsonl"
    with open(q_path, "r", encoding="utf-8") as f:
        for i in range(3):
            line = f.readline()
            if line:
                q = json.loads(line)
                print(f"❓ {q['question']} (Business: {q['business_id']})")

    print("\n" + "="*60)
    print("3. CẤU TRÚC DỮ LIỆU DOANH NGHIỆP")
    print("="*60)
    data_dir = TRAIN_DIR / "data"
    if not data_dir.exists():
        print("❌ Không tìm thấy thư mục data/")
        return
        
    businesses = [d for d in data_dir.iterdir() if d.is_dir()]
    
    # Chỉ phân tích 2 doanh nghiệp đầu tiên
    for biz in businesses[:2]:
        print(f"\n🏢 Doanh nghiệp: {biz.name}")
        
        for csv_file in biz.glob("*.csv"):
            print(f"  📄 File CSV: {csv_file.name}")
            df = pd.read_csv(csv_file, nrows=2)
            print(f"     - Cột: {list(df.columns)}")
            
        for sqlite_file in biz.glob("*.sqlite"):
            print(f"  🗄️ File SQLite: {sqlite_file.name}")
            conn = sqlite3.connect(sqlite_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table});")
                cols = [c[1] for c in cursor.fetchall()]
                print(f"     - Bảng '{table}': Cột {cols}")
            conn.close()

if __name__ == "__main__":
    analyze()