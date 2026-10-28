import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
# Đã đổi từ agents thành huytking
from huytking import (
    load_biz_data, get_readme, planner_plan, coder_write, deepseek_review_no_gold,
    execute_ai_code, format_ans, pack_submission, BASE_DIR
)

PUBLIC_DIR = BASE_DIR / "public_test"
PUBLIC_DATA_DIR = PUBLIC_DIR / "data"
QUESTIONS_FILE = PUBLIC_DIR / "questions.jsonl"
KNOWLEDGE_FILE = BASE_DIR / "knowledge_base.json"
OUTPUT_FILE = BASE_DIR / f"submit_{datetime.now().strftime('%H_%M')}.jsonl"

def get_similar(question, knowledge, top_k=2):
    def score(k):
        return sum(1 for w in question.lower().split() if w in k["question"].lower() and len(w) > 2)
    scored = sorted(knowledge, key=score, reverse=True)
    return [k for k in scored[:top_k] if score(k) > 0]

def main():
    knowledge = json.load(open(KNOWLEDGE_FILE, "r", encoding="utf-8")) if KNOWLEDGE_FILE.exists() else []
    print(f"📚 Đã nạp {len(knowledge)} bài học.")
    
    questions = [json.loads(l) for l in open(QUESTIONS_FILE, "r", encoding="utf-8") if l.strip()]
    questions = questions[:100]
    
    processed = set()
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip(): processed.add(json.loads(l)["id"])
    
    print(f"📝 File output: {OUTPUT_FILE.name}")
    
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f_out:
        for i, q in enumerate(questions):
            q_id = q["id"]
            if q_id in processed: continue
            
            print(f"\n[{i+1}/{len(questions)}] 🎯 {q_id} | {q['business_id']}")
            dfs = load_biz_data(q["business_id"], PUBLIC_DATA_DIR)
            
            if not dfs:
                f_out.write(json.dumps({"id": q_id, "type": "abstain"}) + "\n")
                f_out.flush()
                continue
            
            readme = get_readme(q["business_id"], PUBLIC_DATA_DIR)
            schema = "\n".join([f"- '{k}': {list(v.columns)}" for k, v in dfs.items()])
            
            examples = get_similar(q["question"], knowledge)
            ex_str = ""
            for ex in examples:
                ex_str += f"\n--- VÍ DỤ THAM KHẢO ---\nCâu hỏi: {ex['question']}\n```python\n{ex['code']}\n```\nĐáp án: {ex['answer']}\n"
            
            plan = planner_plan(q["question"], q.get("as_of_date"), schema, readme)
            code = coder_write(q["question"], plan, schema, readme, examples=ex_str)
            
            final_rec = None
            if code:
                for attempt in range(3):
                    res, rsn, typ, err = execute_ai_code(code, dfs, q["question"], q.get("as_of_date"))
                    if err:
                        print(f"  ⚠️ Lỗi Runtime {attempt+1}: {err[:60]}...")
                        is_passed, feedback, fixed_code = deepseek_review_no_gold(
                            q["question"], schema, readme, code, err
                        )
                        if fixed_code:
                            code = fixed_code
                            continue
                        else:
                            break
                    
                    ans = format_ans(res, typ, q["question"])
                    temp_rec = pack_submission(q_id, ans, rsn, typ, q["question"])
                    
                    if temp_rec:
                        print(f"  -> Kết quả: {ans}. Gửi DeepSeek kiểm tra...")
                        is_passed, feedback, fixed_code = deepseek_review_no_gold(
                            q["question"], schema, readme, code, ans
                        )
                        if is_passed:
                            print("  ✅ DeepSeek duyệt!")
                            final_rec = temp_rec
                            break
                        else:
                            print("  ❌ DeepSeek chê. Sửa lại...")
                            if fixed_code:
                                code = fixed_code
                                continue
                            else:
                                final_rec = None
                                break
                    else:
                        break
            
            if final_rec:
                f_out.write(json.dumps(final_rec, ensure_ascii=False) + "\n")
                print(f"  ✅ Ghi nhận: {final_rec.get('answer')}")
            else:
                f_out.write(json.dumps({"id": q_id, "type": "abstain"}) + "\n")
                print("  ❌ Abstain")
            f_out.flush()

if __name__ == "__main__":
    main()