### 🧠 1. System Prompt dành cho Harness / Teacher (DeepSeek/Groq)

Prompt này sẽ được gửi cho DeepSeek khi Học sinh làm sai. Nó sẽ trả về 3 thứ: Lý do sai, Code đã sửa, và **Bài học (Rule) để lưu lại**.

```python
TEACHER_SYSTEM_PROMPT = """Bạn là một Chuyên gia Data Engineer (Giáo viên). Học sinh của bạn (Qwen 1.5B/7B) vừa viết code sai.
Nhiệm vụ của bạn là phân tích lỗi sai, sửa lại code, và QUAN TRỌNG NHẤT: Rút ra một BÀI HỌC (Rule) để lần sau gặp câu hỏi tương tự, học sinh không bao giờ mắc lại lỗi này.

### DỮ LIỆU ĐẦU VÀO:
- Câu hỏi: {question}
- Ngày chốt: {as_of_date}
- Đáp án đúng (Gold): {gold_answer}
- Kết quả học sinh tính ra (Sai): {wrong_output}
- Code của học sinh:
```python
{student_code}
```
- Dữ liệu mẫu (Schema): {schema}

### YÊU CẦU ĐẦU RA (Định dạng JSON BẮT BUỘC):
Bạn phải trả về CHÍNH XÁC một chuỗi JSON (không có markdown ```json bao quanh), theo cấu trúc sau:
{{
  "reason": "Giải thích ngắn gọn tại sao code trên sai (Ví dụ: Học sinh quên lọc đơn hủy, nhầm đơn vị 'bó' thành 'cây', hoặc dùng hàm .nunique() sai cột).",
  "fixed_code": "Đoạn code Python ĐÃ SỬA HOÀN CHỈNH. Chỉ trả về code, không giải thích. Phải dùng các hàm get_df_by_keyword, clean_money, parse_date_safe có sẵn.",
  "new_rule": "Một quy tắc TỔNG QUÁT (General Rule) rút ra từ lỗi này. Phải viết dưới dạng câu lệnh cho AI. Ví dụ: 'KHI tính số lượng Ống PVC, nếu cột ĐVT là 'bó' thì phải nhân với 10 để ra 'cây'. LUÔN LUÔN lọc bỏ đơn 'hàng trả về' trước khi tính.'"
}}
"""
```

---

### 🛠️ 2. Code Pipeline: Tự động sửa lỗi và lưu "Bài học"

Tạo một file mới tên là `run_self_learning.py`. File này sẽ kết nối Local Model (Qwen 7B) để viết code ban đầu, và API (DeepSeek/Groq) để sửa lỗi và rút ra bài học.

```python
import json
import sys
import re
import requests
from pathlib import Path
from datetime import datetime
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_biz_data, get_full_schema, execute_ai_code
from pipeline import format_ans, check_correct

# ================= CẤU HÌNH =================
# 1. Local Student (Qwen Coder)
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:7b"  # Hoặc 1.5b nếu máy yếu

# 2. API Teacher (DeepSeek hoặc Groq)
TEACHER_API_KEY = "sk-..." # 🔴 ĐIỀN DEEPSEEK API KEY HOẶC GROQ KEY
TEACHER_URL = "https://api.deepseek.com/v1/chat/completions" 
TEACHER_MODEL = "deepseek-chat"

BASE_DIR = Path("C:/Users/dinht/Downloads/train")
TRAIN_DIR = BASE_DIR / "train"
DATA_DIR = TRAIN_DIR / "data"
QUESTIONS_FILE = TRAIN_DIR / "questions.jsonl"
ANSWERS_FILE = TRAIN_DIR / "answers.jsonl"

# Bộ nhớ động: Lưu các bài học rút ra
DYNAMIC_RULEBOOK = BASE_DIR / "dynamic_rulebook.md"
KNOWLEDGE_FILE = BASE_DIR / "knowledge_base.json"

def ask_local_student(question, as_of_date, schema, learned_rules):
    prompt = f"""Câu hỏi: "{question}"
Ngày chốt: {as_of_date}
Dữ liệu: 
{schema}

CÁC BÀI HỌC TỪ QUÁ KHỨ (BẮT BUỘC TUÂN THỦ):
{learned_rules}

Viết code Python gán kết quả vào `ans`. Code trong ```python ... ```."""
    
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}
    try:
        res = requests.post(OLLAMA_URL, json=payload, timeout=120)
        text = res.json().get("response", "")
        m = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
        return m.group(1).strip() if m else None
    except Exception as e:
        return None

def ask_teacher_to_fix(question, as_of_date, gold_answer, wrong_output, student_code, schema):
    prompt = TEACHER_SYSTEM_PROMPT.format(
        question=question, as_of_date=as_of_date, gold_answer=gold_answer,
        wrong_output=wrong_output, student_code=student_code, schema=schema
    )
    
    headers = {"Authorization": f"Bearer {TEACHER_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": TEACHER_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.0}
    
    try:
        res = requests.post(TEACHER_URL, headers=headers, json=payload, timeout=120)
        text = res.json()["choices"][0]["message"]["content"]
        # Parse JSON từ Teacher
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return None
    except Exception as e:
        print(f"Lỗi gọi Teacher: {e}")
        return None

def main():
    questions = [json.loads(l) for l in open(QUESTIONS_FILE, "r", encoding="utf-8") if l.strip()]
    answers = {json.loads(l)["id"]: json.loads(l) for l in open(ANSWERS_FILE, "r", encoding="utf-8") if l.strip()}
    
    # Đọc rulebook động (nếu có)
    learned_rules = DYNAMIC_RULEBOOK.read_text(encoding="utf-8") if DYNAMIC_RULEBOOK.exists() else ""
    
    questions = questions[:20] # Test 20 câu
    knowledge = []
    correct_count = 0
    
    print(f"📚 Bắt đầu Self-Learning trên {len(questions)} câu...")
    
    for i, q in enumerate(questions):
        q_id = q["id"]
        gold = answers.get(q_id)
        if not gold: continue
        
        dfs = load_biz_data(q["business_id"], DATA_DIR)
        if not dfs: continue
        
        schema = get_full_schema(dfs)
        print(f"\n[{i+1}/{len(questions)}] {q_id} | {q['question']}")
        
        # 1. Học sinh (Qwen Local) viết code
        code = ask_local_student(q["question"], q.get("as_of_date"), schema, learned_rules)
        if not code: continue
        
        # 2. Chạy thử code
        res, rsn, typ, err = execute_ai_code(code, dfs, q["question"], q.get("as_of_date"))
        
        if err:
            print(f"  ⚠️ Lỗi Runtime: {err[:60]}...")
            is_correct = False
            ans = f"Lỗi: {err}"
        else:
            ans = format_ans(res, typ, q["question"])
            is_correct = check_correct(ans, gold)
            
        # 3. Xử lý kết quả
        if is_correct:
            print(f"  ✅ Đúng! ({ans})")
            correct_count += 1
            knowledge.append({"question": q["question"], "code": code, "answer": ans})
        else:
            print(f"  ❌ Sai: {ans} (Đúng: {gold['answer']}). Gọi Teacher sửa bài...")
            
            # Gọi API Teacher để sửa và rút ra bài học
            fix_data = ask_teacher_to_fix(
                q["question"], q.get("as_of_date"), gold['answer'], ans, code, schema
            )
            
            if fix_data:
                print(f"  🧠 Lý do sai: {fix_data.get('reason')}")
                print(f"  💡 Bài học mới: {fix_data.get('new_rule')}")
                
                # Lưu bài học mới vào file Dynamic Rulebook
                new_rule = fix_data.get('new_rule', '')
                if new_rule and new_rule not in learned_rules:
                    with open(DYNAMIC_RULEBOOK, "a", encoding="utf-8") as f:
                        f.write(f"- {new_rule}\n")
                    learned_rules += f"\n- {new_rule}"
                
                # Chạy lại code đã sửa để kiểm tra
                fixed_code = fix_data.get('fixed_code')
                res2, rsn2, typ2, err2 = execute_ai_code(fixed_code, dfs, q["question"], q.get("as_of_date"))
                if not err2 and check_correct(format_ans(res2, typ2, q["question"]), gold):
                    print(f"  ✅ Teacher đã sửa thành công!")
                    correct_count += 1
                    knowledge.append({"question": q["question"], "code": fixed_code, "answer": format_ans(res2, typ2, q["question"])})
                else:
                    print(f"  ❌ Teacher sửa vẫn sai hoặc lỗi.")
            else:
                print(f"  ⚠️ Teacher không phản hồi.")
                
    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)
        
    print(f"\n🎉 Đã học {correct_count}/{len(questions)} câu. Rulebook đã được cập nhật tại {DYNAMIC_RULEBOOK.name}")

if __name__ == "__main__":
    main()
```

---

### 💡 Tại sao Pipeline này lại "bá đạo"?

1. **Tự động bắt bệnh (Root Cause Analysis)**: Khi bạn đưa ví dụ về "1 bó = 10 cây", nếu Qwen 7B (local) tính ra `8` thay vì `68`. DeepSeek (Teacher) sẽ nhìn vào đáp án và code, nó sẽ nói: *"Lý do sai: Quên quy đổi đơn vị 'bó' thành 'cây'"*.
2. **Rút ra Rule (Dynamic Rulebook)**: Teacher sẽ đẻ ra một câu: *"Bài học: Khi tính số lượng Ống PVC, nếu ĐVT là 'bó' phải nhân 10. Luôn lọc đơn 'trả hàng' ra khỏi doanh thu"*. Câu này được ghi vào file `dynamic_rulebook.md`.
3. **Lần sau không bao giờ sai**: Ở câu thứ 2, thứ 3 (hoặc khi đi thi), con Qwen 7B local sẽ được đọc file `dynamic_rulebook.md` này trước khi viết code. Nó sẽ tự động nhân 10 cho "bó" mà không cần Teacher phải nhắc lại.

### 🚀 Hướng dẫn chạy:
2. Đảm bảo Ollama đang chạy ngầm (với model `qwen2.5-coder:7b`).
3. Chạy lệnh: `python run_self_learning.py`.
4. Mở file `dynamic_rulebook.md` ra xem, bạn sẽ thấy các "bài học xương máu" được AI tự động đúc kết sau mỗi lần làm sai. Khi đi thi thật, bạn chỉ cần copy file `dynamic_rulebook.md` này vào Docker là con AI local của bạn đã khôn hơn rất nhiều!