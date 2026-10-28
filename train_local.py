import json
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from huytking import (
    load_biz_data, planner_plan, deepseek_coder, deepseek_review,
    execute_ai_code, format_ans, check_correct, get_detailed_schema,
    BASE_DIR, TRAIN_DIR, DATA_DIR
)

QUESTIONS_FILE = TRAIN_DIR / "questions.jsonl"
ANSWERS_FILE = TRAIN_DIR / "answers.jsonl"
KNOWLEDGE_FILE = BASE_DIR / "knowledge_base.json"
LOG_FILE = BASE_DIR / datetime.now().strftime("%H_%M_HUYKING.md")

def main():
    questions = [json.loads(l) for l in open(QUESTIONS_FILE, "r", encoding="utf-8") if l.strip()]
    answers = {json.loads(l)["id"]: json.loads(l) for l in open(ANSWERS_FILE, "r", encoding="utf-8") if l.strip()}
    
    questions = questions[:50]
    knowledge = []
    correct_count = 0
    
    print(f"📚 Bắt đầu dạy {len(questions)} câu...")
    
    with open(LOG_FILE, "w", encoding="utf-8") as log:
        def write_log(text):
            log.write(text)
            log.flush()
        
        write_log(f"# BẮT ĐẦU QUÁ TRÌNH DẠY AI\n\n")
        
        for i, q in enumerate(questions):
            q_id = q["id"]
            gold = answers.get(q_id)
            if not gold: continue
            
            biz_id = q["business_id"]
            as_of = q.get("as_of_date")
            dfs = load_biz_data(biz_id, DATA_DIR)
            if not dfs: continue
            
            schema = get_detailed_schema(dfs)
            
            print(f"\n[{i+1}/{len(questions)}] {q_id} | Ngày: {as_of}")
            write_log(f"## Câu {i+1}: {q_id} | Ngày: {as_of}\n- **Hỏi**: {q['question']}\n- **Gold**: {gold['answer']} (Type: {gold['type']})\n")
            
            plan = planner_plan(q["question"], as_of, schema, "")
            write_log(f"- **Plan**: {plan}\n")
            
            print("  -> DeepSeek đang viết code...")
            code, err = deepseek_coder(q["question"], as_of, plan, schema, "")
            if err or not code: continue
            
            write_log(f"- **Code**:\n```python\n{code}\n```\n")
                
            final_ans = None
            for attempt in range(3):
                print(f"  -> Chạy thử (Lần {attempt+1}/3)...")
                res, rsn, typ, run_err = execute_ai_code(code, dfs, q["question"], as_of)
                
                if run_err:
                    print(f"  ⚠️ Lỗi: {run_err[:80]}...")
                    write_log(f"- **Lỗi lần {attempt+1}**: {run_err}\n")
                    code = deepseek_review(q["question"], as_of, schema, code, run_err, gold['answer'], gold['type'])
                    if code:
                        write_log(f"- **Code sửa**:\n```python\n{code}\n```\n")
                        continue
                    else: break
                        
                ans = format_ans(res, typ, q["question"])
                print(f"     -> Kết quả: {str(ans)[:100]} | Đúng: {gold['answer']}")
                
                if check_correct(ans, gold):
                    print(f"  ✅ Đúng!")
                    final_ans = ans
                    break
                else:
                    print(f"  ❌ Sai. Sửa lại...")
                    write_log(f"- **Lỗi lần {attempt+1}**: Kết quả sai ({str(ans)[:100]} != {gold['answer']})\n")
                    code = deepseek_review(q["question"], as_of, schema, code, ans, gold['answer'], gold['type'])
                    if code:
                        write_log(f"- **Code sửa**:\n```python\n{code}\n```\n")
                        continue
                    else: break
            
            if final_ans is not None:
                correct_count += 1
                knowledge.append({"question": q["question"], "code": code, "answer": final_ans, "biz_id": biz_id})
                write_log("- **Lưu**: ✅\n\n")
            else:
                write_log("- **Lưu**: ❌\n\n")
    
    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 Đã học {correct_count}/{len(questions)} câu.")

if __name__ == "__main__":
    main()