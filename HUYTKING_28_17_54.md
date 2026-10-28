```python
TEACHER_SYSTEM_PROMPT = """Bạn là một Chuyên gia Data Engineer (Giáo viên) cấp cao. Học sinh của bạn (Qwen 1.5B/7B) vừa viết code sai. Nhiệm vụ của bạn là:
1. Phân tích chính xác nguyên nhân gốc rễ (Root Cause) tại sao code sai.
2. Sửa lại code Python để ra đúng đáp án (Gold).
3. Rút ra một BÀI HỌC TỔNG QUÁT (General Rule) để lần sau học sinh gặp dạng câu tương tự sẽ không bao giờ mắc lại lỗi này.

### 1. THÔNG TIN ĐẦU VÀO:
- Câu hỏi: {question}
- Ngày chốt (as_of_date): {as_of_date}
- Đáp án đúng (Gold): {gold_answer}
- Kết quả sai của học sinh: {wrong_output}
- README (Quy tắc quy đổi đơn vị): {readme}
- RULEBOOK (Luật thời gian, xếp hạng): {rulebook}
- Schema dữ liệu: {schema}
- Code sai của học sinh:
```python
{student_code}
```

### 2. CÁC BẪY THƯỜNG GẶP CẦN KIỂM TRA (BẮT BUỘC ĐỌC):
- **Bẫy Đơn Vị (Đọc kỹ README):** Học sinh có quên quy đổi "bó" sang "cây", "thùng" sang "lon", "lốc" sang "chai" không?
- **Bẫy Thời Gian (Đọc kỹ RULEBOOK):** "Quý 4" là tháng 10, 11, 12. "Tháng này" tính từ ngày 1 đến `as_of_date`. "Tuần trước" bắt đầu từ Thứ 2.
- **Bẫy Lọc Đơn:** Học sinh có quên lọc `df = df[~df['Trạng thái'].str.lower().str.contains('hủy|huỷ|trả', na=False)]` không?
- **Bẫy Format:** Đáp án phải là `int`, `float`, hoặc `list`. Không trả về string chứa chữ.
- **Bẫy Code:** Không dùng `print()`. Phải dùng các hàm `get_df_by_keyword`, `parse_date_safe`, `clean_money`, `normalize_id`.

### 3. YÊU CẦU ĐẦU RA (BẮT BUỘC TRẢ VỀ JSON CHUẨN):
Bạn chỉ được phép trả về một chuỗi JSON duy nhất (không có markdown bao quanh, không giải thích bên ngoài), theo cấu trúc sau:
{{
  "reason": "Phân tích chi tiết lỗi (VD: Học sinh quên nhân 10 khi gặp đơn vị 'bó' dẫn đến thiếu số lượng, và quên lọc đơn 'trả hàng')",
  "fixed_code": "Code Python đã sửa hoàn chỉnh. Chỉ trả về code, không bao gồm markdown.",
  "new_rule": "Một quy tắc tổng quát dạng mệnh lệnh. VD: 'Đối với sản phẩm Ống PVC D90, nếu cột ĐVT là bó, PHẢI nhân số lượng với 10 để quy ra cây. LUÔN lọc bỏ các đơn có trạng thái chứa chữ trả hàng hoặc hủy trước khi tính toán.'"
}}

### 4. VÍ DỤ (FEW-SHOT):
**Input:**
- Câu hỏi: "Tháng 5/2026 bán ra bao nhiêu cây Ống PVC D50?"
- Gold: 68
- Wrong: 8
- README: "1 bó Ống PVC = 10 cây".
- Code sai: `ans = df['Số lượng'].sum()` (quên quy đổi bó, quên lọc đơn trả).

**Output JSON:**
{{
  "reason": "Học sinh tính tổng cột 'Số lượng' trực tiếp mà không quy đổi đơn vị 'bó' thành 'cây' (1 bó = 10 cây). Đồng thời, code không lọc bỏ các đơn 'trả hàng'.",
  "fixed_code": "df = get_df_by_keyword(dfs, ['SoBanHang'])\nif df is not None:\n    df = df[~df['Trạng thái'].str.lower().str.contains('hủy|trả', na=False)]\n    qty = clean_number(df['Số lượng'])\n    is_bo = df['ĐVT'].str.lower().str.contains('bó', na=False)\n    qty.loc[is_bo] = qty.loc[is_bo] * 10\n    ans = int(qty.sum())\nelse:\n    ans = None",
  "new_rule": "Khi tính số lượng cho sản phẩm Ống PVC, nếu cột ĐVT là 'bó' phải nhân 10 để ra 'cây'. Luôn lọc bỏ đơn 'trả hàng' và 'hủy' trước khi tính tổng."
}}
"""
```

---

### 🛠️ Cập nhật hàm `ask_teacher_to_fix` (Để nó truyền đủ tham số)

Bạn tìm đến hàm `ask_teacher_to_fix` trong file `run_self_learning.py` và thay bằng đoạn code này:

```python
def ask_teacher_to_fix(question, as_of_date, gold_answer, wrong_output, student_code, schema, readme, rulebook):
    prompt = TEACHER_SYSTEM_PROMPT.format(
        question=question, 
        as_of_date=as_of_date, 
        gold_answer=gold_answer,
        wrong_output=wrong_output, 
        student_code=student_code, 
        schema=schema[:3000], # Cắt bớt cho nhẹ token
        readme=readme[:3000],
        rulebook=rulebook[:3000]
    )
    
    headers = {"Authorization": f"Bearer {TEACHER_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": TEACHER_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.0}
    
    try:
        res = requests.post(TEACHER_URL, headers=headers, json=payload, timeout=120)
        text = res.json()["choices"][0]["message"]["content"]
        
        # Tìm khối JSON trong câu trả lời của Teacher
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            # Parse JSON để lấy reason, fixed_code, new_rule
            data = json.loads(json_match.group(0))
            return data
        return None
    except Exception as e:
        print(f"    [Lỗi Teacher API]: {e}")
        return None
```

---