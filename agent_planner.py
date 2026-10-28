import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"

def create_plan(question, as_of_date, schema_info):
    prompt = f"""Bạn là Chuyên gia Phân tích Dữ liệu. Nhiệm vụ của bạn là đọc câu hỏi và lập KẾ HOẠCH TÍNH TOÁN (không cần viết code).
Câu hỏi: "{question}"
Ngày chốt dữ liệu (as_of_date): {as_of_date}
Cấu trúc dữ liệu hiện có:
{schema_info}

Hãy lập kế hoạch từng bước bằng tiếng Việt:
1. Cần lấy dữ liệu từ bảng nào?
2. Cần lọc các điều kiện gì? (Ngày tháng, trạng thái đơn hàng, tên sản phẩm, khách hàng...)
3. Cần tính toán gì? (Tổng, trung bình, đếm, tìm max/min, groupby...)

CHÚ Ý CÁC LUẬT:
- Doanh thu chỉ tính đơn KHÔNG HỦY, KHÔNG TRẢ HÀNG.
- Số đơn chỉ đếm đơn KHÔNG HỦY, KHÔNG TRẢ HÀNG.
- Nếu tính doanh thu, cần lọc ngày đặt hàng (không phải ngày giao).
- Nếu có quy đổi đơn vị, cần chú ý đơn vị cơ bản.

Trả về kế hoạch ngắn gọn, rõ ràng.
"""
    try:
        res = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}, timeout=120)
        return res.json().get("response", "").strip()
    except Exception as e:
        return f"Lỗi Planner: {e}"