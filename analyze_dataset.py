import json
import pandas as pd
import sqlite3
from pathlib import Path
from collections import defaultdict

# Cấu hình đường dẫn
BASE_DIR = Path(r"C:\Users\dinht\Downloads\train")
TRAIN_DIR = BASE_DIR / "train"
DATA_DIR = TRAIN_DIR / "data"
QUESTIONS_FILE = TRAIN_DIR / "questions.jsonl"

def analyze():
    print("=" * 80)
    print("📊 BÁO CÁO PHÂN TÍCH DATASET ZALO AI CHALLENGE")
    print("=" * 80)

    # 1. Phân tích câu hỏi trước
    print("\n[1] ĐANG PHÂN TÍCH CÂU HỎI (questions.jsonl)...")
    questions_by_biz = defaultdict(list)
    total_questions = 0
    
    if QUESTIONS_FILE.exists():
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    q = json.loads(line)
                    questions_by_biz[q["business_id"]].append(q)
                    total_questions += 1
        print(f"✅ Tổng số câu hỏi: {total_questions}")
        print(f"✅ Số lượng doanh nghiệp có câu hỏi: {len(questions_by_biz)}")
    else:
        print(f"❌ Không tìm thấy file {QUESTIONS_FILE}")

    # 2. Quét toàn bộ thư mục Data
    print("\n[2] ĐANG QUÉT CẤU TRÚC DỮ LIỆU (thư mục data/)...")
    if not DATA_DIR.exists():
        print(f"❌ Không tìm thấy thư mục {DATA_DIR}")
        return

    businesses = sorted([d.name for d in DATA_DIR.iterdir() if d.is_dir()])
    print(f"✅ Tìm thấy {len(businesses)} thư mục doanh nghiệp: {businesses}\n")

    # 3. In chi tiết từng doanh nghiệp
    for biz_id in businesses:
        biz_dir = DATA_DIR / biz_id
        print("=" * 80)
        print(f"🏢 DOANH NGHIỆP: {biz_id}")
        
        # Đọc README để đoán ngành hàng
        readme_path = biz_dir / "README.md"
        if readme_path.exists():
            readme_text = readme_path.read_text(encoding="utf-8")
            # Lấy 100 ký tự đầu tiên của README làm mô tả
            desc = readme_text.strip().replace('\n', ' ')[:150]
            print(f"📝 Mô tả (từ README): {desc}...")
        else:
            print("📝 Mô tả: (Không có file README)")

        # Liệt kê file dữ liệu
        files = list(biz_dir.glob("*.*"))
        print(f"📂 Các file dữ liệu ({len(files)}):")
        
        for file in files:
            if file.suffix.lower() == ".csv":
                try:
                    # Đọc thử 3 dòng đầu để lấy tên cột
                    df = pd.read_csv(file, nrows=3)
                    cols = ", ".join(df.columns)
                    print(f"   - {file.name} (CSV) | {len(df.columns)} cột: [{cols}]")
                except Exception as e:
                    print(f"   - {file.name} (CSV) | Lỗi đọc: {e}")
            elif file.suffix.lower() == ".sqlite":
                try:
                    conn = sqlite3.connect(file)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = [r[0] for r in cursor.fetchall()]
                    print(f"   - {file.name} (SQLite) | Các bảng: {tables}")
                    conn.close()
                except Exception as e:
                    print(f"   - {file.name} (SQLite) | Lỗi đọc: {e}")

        # In số lượng câu hỏi và mẫu 2 câu hỏi
        q_count = len(questions_by_biz[biz_id])
        print(f"❓ Số câu hỏi trong file jsonl: {q_count}")
        
        if q_count > 0:
            print(f"   Ví dụ câu hỏi:")
            for q in questions_by_biz[biz_id][:2]: # Lấy 2 câu đầu
                print(f"     + \"{q['question']}\" (as_of_date: {q['as_of_date']})")
        print()

    # 4. Các doanh nghiệp có câu hỏi nhưng thiếu folder data
    print("=" * 80)
    print("⚠️ KIỂM TRA CHÉO (CÂU HỎI NHƯNG KHÔNG CÓ DATA):")
    missing_data = []
    for biz_id in questions_by_biz.keys():
        if biz_id not in businesses:
            missing_data.append(biz_id)
            
    if missing_data:
        print(f"❌ Phát hiện {len(missing_data)} doanh nghiệp có câu hỏi nhưng THIẾU thư mục data:")
        print(f"   {missing_data}")
        print("   -> Bạn cần tải bổ sung dữ liệu của các biz này để test!")
    else:
        print("✅ Tất cả các biz có câu hỏi đều đã có dữ liệu trên máy.")

if __name__ == "__main__":
    analyze()