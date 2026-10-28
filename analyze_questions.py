# analyze_questions.py
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

# Đường dẫn
BASE_DIR = Path(r"C:\Users\dinht\Downloads\train")
TRAIN_DIR = BASE_DIR / "train"
QUESTIONS_FILE = TRAIN_DIR / "questions.jsonl"

def normalize_text(text):
    """Chuẩn hóa: chữ thường, bỏ dấu câu thừa"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def analyze():
    print("⏳ Đang đọc 3000 câu hỏi...")
    questions = []
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))

    total = len(questions)
    print(f"✅ Đã load {total} câu hỏi.\n")

    # Định nghĩa các Intent (Ý định) dựa trên từ khóa
    # Lưu ý: Dữ liệu rất bẩn, có câu có dấu, có câu không dấu (dthu, huy, tong...)
    INTENT_PATTERNS = {
        "Doanh thu / Bán hàng": r"(doanh thu|dthu|dt|doanh so|ban duoc|ban dc|thu duoc|thu dc|revenue|tổng tiền|tong tien|tiền hàng|tien hang)",
        "Tỉ lệ huỷ đơn": r"(huỷ|huy|hủy|tỉ lệ huỷ|ti le huy|bị huỷ|bi huy|đơn huỷ|don huy)",
        "Khách hàng (Top/Chi tiêu/Nợ)": r"(khách|khach|top|mua nhiều|mua nhieu|chi tiêu|chi tieu|nợ|no|công nợ|cong no|ghi nợ|ghi no)",
        "Sản phẩm / Bán chạy": r"(sản phẩm|san pham|mặt hàng|mat hang|bán chạy|ban chay|hot|chạy nhất|chay nhat|bán được nhiều|ban duoc nhieu)",
        "Tồn kho / Nhập hàng": r"(tồn|ton|kho|nhập|nhap|xuất|xuat|nhập hàng|nhap hang|tồn kho|ton kho)",
        "Giá vốn / Lợi nhuận": r"(giá vốn|gia von|lãi|lai|lợi nhuận|loi nhuan|chi phí|chi phi|giá nhập|gia nhap)",
        "Số lượng đơn hàng": r"(số đơn|so don|bao nhiêu đơn|bao nhieu don|mấy đơn|may don|đếm đơn|dem don)",
        "Ngày / Thời gian": r"(ngày nào|ngay nao|ngày mấy|ngay may|tháng mấy|thang may|hôm nay|hom nay|hôm qua|hom qua|tuần|tuan|tháng|thang|năm|nam)",
        "Giá bán": r"(giá bán|gia ban|đơn giá|don gia|giá|gia|bao nhiêu tiền|bao nhieu tien)",
        "Khác": r".*" # Bắt tất cả những gì còn lại
    }

    # Đếm và lưu ví dụ
    intent_counts = Counter()
    intent_examples = defaultdict(list)
    
    # Đếm số câu hỏi theo từng Biz
    biz_counts = Counter()

    for q in questions:
        biz_counts[q["business_id"]] += 1
        raw_text = q["question"]
        text = normalize_text(raw_text)
        
        matched = False
        for intent, pattern in INTENT_PATTERNS.items():
            if intent == "Khác": continue
            if re.search(pattern, text):
                intent_counts[intent] += 1
                if len(intent_examples[intent]) < 5: # Lấy 5 ví dụ
                    intent_examples[intent].append(raw_text)
                matched = True
                break # Chỉ xếp vào 1 intent ưu tiên cao nhất
        
        if not matched:
            intent_counts["Khác"] += 1
            if len(intent_examples["Khác"]) < 5:
                intent_examples["Khác"].append(raw_text)

    # ===== IN KẾT QUẢ =====
    print("=" * 80)
    print("📊 PHÂN TÍCH 3000 CÂU HỎI TRAIN")
    print("=" * 80)

    print("\n🏢 TOP 10 DOANH NGHIỆP CÓ NHIỀU CÂU HỎI NHẤT:")
    for biz, count in biz_counts.most_common(10):
        print(f"   - {biz}: {count} câu")

    print("\n🎯 PHÂN BỐ CÁC LOẠI CÂU HỎI (INTENT):")
    # Sắp xếp theo số lượng giảm dần
    for intent, count in intent_counts.most_common():
        percentage = (count / total) * 100
        bar = "█" * int(percentage / 2)
        print(f"\n   🔹 {intent}: {count} câu ({percentage:.1f}%) {bar}")
        
        # In 3 ví dụ mẫu (tránh in quá dài)
        print("      Ví dụ:")
        for ex in intent_examples[intent][:3]:
            # Cắt bớt nếu câu quá dài
            short_ex = ex[:80] + "..." if len(ex) > 80 else ex
            print(f"      - \"{short_ex}\"")

    print("\n" + "=" * 80)
    print("💡 GỢI Ý HƯỚNG ĐI:")
    print("1. Nhìn vào các Intent chiếm > 10%, đó là các Template ưu tiên viết trước.")
    print("2. Nhìn vào từ ngữ trong ví dụ (có dấu hay không dấu) để viết Regex cho chuẩn.")
    print("3. Nếu Intent 'Khác' > 20%, cần xem lại danh sách ví dụ của nó để thêm Intent mới.")
    print("=" * 80)

if __name__ == "__main__":
    analyze()