### 📁 File 2: `predict.sh` và `predict.py` (Chạy trong Docker)

import json
import sys
from pathlib import Path
from datetime import datetime
import time

sys.path.insert(0, str(Path(__file__).parent))
from huytking import (
    load_biz_data, get_readme, planner_plan, coder_write, tester_fix, tester_review,
    execute_ai_code, format_ans, pack_submission, get_detailed_schema, get_rulebook,
    DATA_ROOT, RESULT_DIR
)

QUESTIONS_FILE = DATA_ROOT / "questions.jsonl"
KNOWLEDGE_FILE = Path(__file__).parent / "knowledge_base.json" # File này mang từ ngoài vào
OUTPUT_FILE = RESULT_DIR / "HUYTKING_%Y-%m-%d_%H-%M-%S.jsonl"
LOG_DIR = RESULT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def get_similar(question, knowledge, top_k=2):
    def score(k):
        return sum(1 for w in question.lower().split() if w in k["question"].lower() and len(w) > 2)
    scored = sorted(knowledge, key=score, reverse=True)
    return [k for k in scored[:top_k] if score(k) > 0]

def main():
    knowledge = json.load(open(KNOWLEDGE_FILE, "r", encoding="utf-8")) if KNOWLEDGE_FILE.exists() else []
    rulebook = get_rulebook()
    
    questions = [json.loads(l) for l in open(QUESTIONS_FILE, "r", encoding="utf-8") if l.strip()]
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        for i, q in enumerate(questions):
            q_id = q["id"]
            start_time = time.time()
            
            dfs = load_biz_data(q["business_id"], DATA_ROOT / "data")
            
            if not dfs:
                f_out.write(json.dumps({"id": q_id, "type": "abstain"}) + "\n")
                f_out.flush()
                continue
            
            readme = get_readme(q["business_id"], DATA_ROOT / "data")
            schema = get_detailed_schema(dfs)
            
            # RAG
            examples = get_similar(q["question"], knowledge)
            ex_str = ""
            for ex in examples:
                ex_str += f"\n--- VÍ DỤ THAM KHẢO ---\nCâu hỏi: {ex['question']}\n```python\n{ex['code']}\n```\nĐáp án: {ex['answer']}\n"
            
            plan = planner_plan(q["question"], q.get("as_of_date"), schema, readme, rulebook)
            code = coder_write(q["question"], plan, schema, readme, rulebook, examples=ex_str)
            
            final_rec = None
            final_log = ""
            
            if code:
                for attempt in range(5):
                    res, rsn, typ, err = execute_ai_code(code, dfs, q["question"], q.get("as_of_date"))
                    
                    if err:
                        final_log += f"Lần {attempt+1} lỗi: {err}\n"
                        code = tester_fix(q["question"], code, err, rulebook)
                        continue
                    
                    ans = format_ans(res, typ, q["question"])
                    temp_rec = pack_submission(q_id, ans, rsn, typ, q["question"])
                    
                    if temp_rec:
                        # Dùng Qwen 7B Review Logic (Thay vì DeepSeek)
                        is_passed, fixed_code = tester_review(q["question"], code, ans, schema, readme, rulebook)
                        if is_passed:
                            final_rec = temp_rec
                            final_log += f"Thành công ở lần {attempt+1}. Kết quả: {ans}\n"
                            break
                        else:
                            final_log += f"Lần {attempt+1} sai logic. Sửa lại...\n"
                            if fixed_code: code = fixed_code
                            else: break
                    else:
                        code = tester_fix(q["question"], code, "Không có `ans`", rulebook)
            
            if final_rec:
                f_out.write(json.dumps(final_rec, ensure_ascii=False) + "\n")
            else:
                f_out.write(json.dumps({"id": q_id, "type": "abstain"}) + "\n")
                final_log += "Thất bại -> Abstain.\n"
            f_out.flush()
            
            # Ghi Log theo yêu cầu của BTC
            elapsed = time.time() - start_time
            with open(LOG_DIR / f"{q_id}.txt", "w", encoding="utf-8") as f_log:
                f_log.write(f"ID: {q_id}\nTime: {elapsed:.2f}s\nAnswer: {final_rec}\n\nDetails:\n{final_log}")

if __name__ == "__main__":
    main()