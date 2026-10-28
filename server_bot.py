import json
import sys
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Import bộ não từ huytking.py
sys.path.insert(0, str(Path(__file__).parent))
from huytking import (
    load_biz_data, get_readme, get_detailed_schema, get_rulebook,
    planner_plan, coder_write, tester_fix, execute_ai_code, 
    format_ans, pack_submission, BASE_DIR
)

app = FastAPI(title="DataMate Agent Bot")

# Load knowledge base (nếu có)
KNOWLEDGE_FILE = BASE_DIR / "knowledge_base.json"
knowledge = []
if KNOWLEDGE_FILE.exists():
    try:
        knowledge = json.load(open(KNOWLEDGE_FILE, "r", encoding="utf-8"))
        print(f"📚 Đã nạp {len(knowledge)} bài học từ knowledge_base.json")
    except Exception as e:
        print(f"⚠️ Không thể nạp knowledge_base.json: {e}")

# ================= API NHẬN CÂU HỎI =================
class AskRequest(BaseModel):
    question: str
    business_id: str
    as_of_date: str = "2026-12-31"

@app.post("/api/ask")
async def ask_agent(req: AskRequest):
    print(f"\n🎯 Nhận câu hỏi: {req.question} | Biz: {req.business_id}")
    
    # 1. Load dữ liệu
    data_dir = BASE_DIR / "public_test" / "data" # Trỏ tới public_test
    dfs = load_biz_data(req.business_id, data_dir)
    if not dfs:
        return {"error": f"Không tìm thấy dữ liệu cho {req.business_id}"}
        
    readme = get_readme(req.business_id, data_dir)
    schema = get_detailed_schema(dfs)
    rulebook = get_rulebook()
    
    # 2. Tìm bài học tương tự (RAG)
    def get_similar(q_text, kb, top_k=2):
        def score(k):
            return sum(1 for w in q_text.lower().split() if w in k["question"].lower() and len(w) > 2)
        scored = sorted(kb, key=score, reverse=True)
        return [k for k in scored[:top_k] if score(k) > 0]
        
    examples = get_similar(req.question, knowledge)
    ex_str = ""
    for ex in examples:
        ex_str += f"\n--- VÍ DỤ THAM KHẢO ---\nCâu hỏi: {ex['question']}\n```python\n{ex['code']}\n```\nĐáp án: {ex['answer']}\n"
    
    # 3. Chạy Pipeline
    logs = []
    logs.append(f"📖 README: {readme[:200]}...")
    
    # Planner
    logs.append("🧠 Đang gọi Planner (3B)...")
    plan = planner_plan(req.question, req.as_of_date, schema, readme, rulebook)
    logs.append(f"📝 Kế hoạch: {plan}")
    
    # Coder
    logs.append("💻 Đang gọi Coder (1.5B)...")
    code = coder_write(req.question, plan, schema, readme, rulebook, examples=ex_str)
    if not code:
        return {"error": "Coder không sinh được code", "logs": logs}
    logs.append(f"Code ban đầu:\n```python\n{code}\n```")
    
    final_result = None
    final_rec = None
    
    # Execute & Review
    for attempt in range(5):
        logs.append(f"🔄 Chạy thử (Lần {attempt+1}/5)...")
        res, rsn, typ, err = execute_ai_code(code, dfs, req.question, req.as_of_date)
        
        if err:
            logs.append(f"⚠️ Lỗi Runtime: {err}")
            logs.append("🔧 Gọi Tester (7B) sửa lỗi...")
            code = tester_fix(req.question, code, err, rulebook)
            logs.append(f"Code đã sửa:\n```python\n{code}\n```")
            continue
            
        ans = format_ans(res, typ, req.question)
        logs.append(f"✅ Kết quả tính được: {ans}")
        
        final_rec = pack_submission("q_test", ans, rsn, typ, req.question)
        if final_rec:
            final_result = ans
            break
            
    return {
        "question": req.question,
        "plan": plan,
        "final_code": code,
        "answer": final_result,
        "submission_format": final_rec,
        "logs": logs
    }

# ================= GIAO DIỆN WEB =================
@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DataMate Agent Bot</title>
        <style>
            body { font-family: Arial, sans-serif; background: #1e1e1e; color: #fff; padding: 20px; }
            .container { max-width: 800px; margin: auto; }
            input, textarea, select { width: 100%; padding: 10px; margin: 5px 0; background: #333; color: #fff; border: 1px solid #555; border-radius: 5px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .log-box { background: #000; color: #0f0; padding: 15px; border-radius: 5px; margin-top: 20px; white-space: pre-wrap; font-family: monospace; max-height: 400px; overflow-y: auto; }
            .result { background: #222; padding: 15px; border-radius: 5px; margin-top: 20px; border-left: 4px solid #007bff; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 DataMate Agent Bot</h1>
            <p>Nhập câu hỏi để test hệ thống AI Agent Local.</p>
            
            <label>Mã doanh nghiệp (VD: dev_001):</label>
            <input type="text" id="biz_id" value="dev_001">
            
            <label>Ngày chốt (as_of_date):</label>
            <input type="text" id="as_of_date" value="2026-12-31">
            
            <label>Câu hỏi:</label>
            <textarea id="question" rows="3">Tháng 11 năm 2025, nhóm trà có mặt hàng nào bán được nhiều ly nhất?</textarea>
            
            <button onclick="askBot()">🚀 Gửi câu hỏi</button>
            
            <div id="result-box" class="result" style="display:none;"></div>
            <div id="log-box" class="log-box" style="display:none;"></div>
        </div>
        
        <script>
            async function askBot() {
                const biz_id = document.getElementById('biz_id').value;
                const as_of_date = document.getElementById('as_of_date').value;
                const question = document.getElementById('question').value;
                
                const resBox = document.getElementById('result-box');
                const logBox = document.getElementById('log-box');
                
                resBox.style.display = 'none';
                logBox.style.display = 'block';
                logBox.innerText = "⏳ Đang xử lý... (Quá trình này có thể mất 1-2 phút do chạy model local)";
                
                try {
                    const response = await fetch('/api/ask', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question, business_id: biz_id, as_of_date })
                    });
                    const data = await response.json();
                    
                    if (data.error) {
                        resBox.style.display = 'block';
                        resBox.innerHTML = `<span style="color:red">Lỗi: ${data.error}</span>`;
                        logBox.innerText = data.logs ? data.logs.join('\\n') : "Không có log";
                        return;
                    }
                    
                    resBox.style.display = 'block';
                    resBox.innerHTML = `
                        <h3>✅ Kết quả: <span style="color:#00ff00">${data.answer}</span></h3>
                        <p><b>Định dạng nộp bài:</b> <code>${JSON.stringify(data.submission_format)}</code></p>
                        <p><b>Code cuối cùng:</b></p>
                        <pre style="background:#000; padding:10px; color:#0f0;">${data.final_code}</pre>
                    `;
                    
                    logBox.innerText = data.logs.join('\\n');
                } catch (e) {
                    resBox.style.display = 'block';
                    resBox.innerHTML = `<span style="color:red">Lỗi kết nối: ${e}</span>`;
                }
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    print("🚀 Đang khởi động server tại http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)