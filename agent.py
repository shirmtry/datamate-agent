# agent.py
import re
import ollama

MODEL_ID = "qwen2.5:3b" 
print(f"✅ Đã kết nối với Ollama (Model: {MODEL_ID})")

def extract_code(text):
    # Tìm code trong block ```python
    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Thử tìm block code không có chữ python
    match = re.search(r"```(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
        
    if "final_answer" in text:
        text = text.replace("```", "").strip()
        return text
    
    return "final_answer = None"

def generate_code(question, rulebook, schema_str, as_of_date, error_msg=None, old_code=None):
    # Prompt cực kỳ nghiêm khắc
    system_prompt = f"""Bạn là một máy viết code Python tự động.
Nhiệm vụ: Viết code pandas để tính toán câu hỏi của người dùng.

## RULEBOOK:
{rulebook}

## SCHEMA DỮ LIỆU:
{schema_str}

## QUY TẮC BẮT BUỘC:
- Truy cập dữ liệu qua biến `dfs`. Ví dụ: `df = dfs['ban_hang']`.
- `as_of_date` là biến có sẵn, không phải cột.
- Kết quả cuối cùng gán vào biến `final_answer`.
- KHÔNG ĐƯỢC TRẢ LỜI ĐÁP ÁN BẰNG SỐ HAY CHỮ. CHỈ TRẢ VỀ ĐOẠN CODE.
"""

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f"Viết code Python cho câu hỏi: {question}"}
    ]

    if error_msg and old_code:
        messages.append({'role': 'assistant', 'content': f"```python\n{old_code}\n```"})
        messages.append({'role': 'user', 'content': f"Code trên bị lỗi: {error_msg}. Sửa lại code."})

    try:
        response = ollama.chat(
            model=MODEL_ID,
            messages=messages,
            options={'temperature': 0.0, 'num_predict': 500}
        )
        raw_text = response['message']['content']
        print(f"   🤖 [Debug LLM]: {raw_text[:100]}...") # In thử LLM nói gì
        return extract_code(raw_text)
    except Exception as e:
        return f"final_answer = 'LỖI_GỌI_LLM: {str(e)}'"