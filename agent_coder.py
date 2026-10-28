import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:1.5b"

def write_code(question, plan, schema_info):
    prompt = f"""Bạn là Coder. Viết code Python (Pandas) giải quyết câu hỏi dựa trên kế hoạch sau.
Câu hỏi: "{question}"
Kế hoạch:
{plan}
Cấu trúc dữ liệu (dict `dfs` đã có sẵn):
{schema_info}

QUY TẮC BẮT BUỘC:
1. KHÔNG import thư viện. `pd`, `np`, `datetime`, `parse_date_safe`, `clean_money`, `clean_number` đã có sẵn.
2. KHÔNG DÙNG pd.read_csv/read_excel. Dữ liệu đã có sẵn trong `dfs`.
3. Gán kết quả cuối cùng vào biến `ans`.
4. Code trong block ```python ... ```.
5. TUYỆT ĐỐI KHÔNG dùng biến lạ (như `qd_map`, `he_so_map`...). Mọi biến phải được định nghĩa.
6. LÀM SẠCH SỐ: Dùng `clean_money(df['Cột'])` hoặc `clean_number(df['Cột'])` cho các cột chứa chữ.
7. NGÀY THÁNG: Dùng `parse_date_safe(df['tên_cột'])`.
8. Nếu không tìm thấy dữ liệu, gán `ans = None` và `reason = "Lý do cụ thể"`.
"""
    try:
        res = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}, timeout=120)
        text = res.json().get("response", "")
        match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
        return match.group(1).strip() if match else None
    except Exception as e:
        return None