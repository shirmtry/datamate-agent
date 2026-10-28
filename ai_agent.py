import pandas as pd
import requests
import json
import re
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import calendar
import numpy as np

# ================= CẤU HÌNH =================
OLLAMA_URL = "http://localhost:11434/api/generate"
PLANNER_MODEL = "qwen2.5:3b"       
CODER_MODEL = "qwen2.5-coder:1.5b" 

BASE_DIR = Path(r"C:\Users\dinht\Downloads\train")
SPLIT_DIR = BASE_DIR / "public_test"  
DATA_DIR = SPLIT_DIR / "data"

timestamp = datetime.now().strftime("%H_%M")
OUTPUT_FILE = BASE_DIR / f"HUYTKING_{timestamp}.jsonl"

# ================= HÀM BỎ DẤU TIẾNG VIỆT =================
def remove_accents(text):
    text = str(text).lower()
    patterns = {
        '[àáảãạăằắẳẵặâầấẩẫậ]': 'a', '[èéẻẽẹêềếểễệ]': 'e',
        '[ìíỉĩị]': 'i', '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
        '[ùúủũụưừứửữự]': 'u', '[ỳýỷỹỵ]': 'y', '[đ]': 'd'
    }
    for p, r in patterns.items():
        text = re.sub(p, r, text)
    return text

# ================= BỘ LỌC THÔNG MINH =================
def filter_relevant_tables(question, dfs):
    q = remove_accents(question)
    
    # 1. Lọc theo thời gian
    month_match = re.search(r'thang\s*(\d{1,2})', q)
    year_match = re.search(r'(20\d{2})', q)
    
    if month_match:
        month = month_match.group(1).zfill(2) 
        month_no_zero = str(int(month))
        
        time_filtered = {}
        for name, df in dfs.items():
            name_norm = remove_accents(name)
            # Tìm tên bảng chứa tháng và năm
            if month in name_norm or f"T{month_no_zero}" in name_norm or f"T{month}" in name_norm:
                if year_match and year_match.group(1) in name_norm:
                    time_filtered[name] = df
                    
        if time_filtered:
            dfs = time_filtered
            print(f"      ⏱️  Đã lọc theo thời gian: Chỉ giữ {len(dfs)} bảng")

    # 2. Lọc theo chủ đề
    keywords = []
    if any(k in q for k in ["doanh thu", "ban hang", "ban", "tien", "hoa don", "don hang", "ly", "coc"]):
        keywords.extend(["banhang", "hoadon", "donhang"])
    if any(k in q for k in ["nhap", "mua"]):
        keywords.extend(["nhaphang", "nhap"])
    if any(k in q for k in ["ton", "kho", "con"]):
        keywords.extend(["tonkho", "kho", "sanpham", "hanghoa"])
    
    if keywords:
        filtered = {}
        for name, df in dfs.items():
            name_norm = remove_accents(name).replace("_", "").replace(" ", "")
            if any(k in name_norm for k in keywords):
                filtered[name] = df
        if filtered:
            dfs = filtered
    
    return dfs

# ================= HÀM GỘP SCHEMA =================
def get_compact_schema(dfs):
    grouped = {}
    for name, df in dfs.items():
        col_str = str(df.columns.tolist())
        if col_str not in grouped:
            grouped[col_str] = []
        grouped[col_str].append(name)
    
    schema_str = ""
    for col_str, names in grouped.items():
        if len(names) == 1:
            schema_str += f"Bảng '{names[0]}': {col_str}\n"
        else:
            schema_str += f"Các bảng {names} (dùng chung 1 cấu trúc): {col_str}\n"
    return schema_str

# ================= AGENT 1: PLANNER (3B) =================
def run_planner_agent(question, dfs, rulebook):
    schema_str = get_compact_schema(dfs)
    rulebook_short = rulebook[:1000] if len(rulebook) > 1000 else rulebook
    
    prompt = f"""Bạn là Chuyên gia Dữ liệu. Câu hỏi: "{question}"

DỮ LIỆU THỰC TẾ ĐANG CÓ:
{schema_str}

LUẬT DOANH NGHIỆP (Trích lục):
{rulebook_short}

Hãy vạch ra KẾ HOẠCH TÍNH TOÁN (tiếng Việt, tối đa 3 bước):
1. Chọn bảng nào? (Dùng `pd.concat(dfs.values(), ignore_index=True)` nếu cần gộp).
2. Chuyển cột ngày tháng sang datetime.
3. Lọc dữ liệu gì? (tháng mấy, nhóm trà, v.v.).
4. Tính toán gì? (sum, groupby, max...).
"""
    payload = {"model": PLANNER_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.0, "num_predict": 150}}
    try:
        res = requests.post(OLLAMA_URL, json=payload, timeout=300)
        plan = res.json().get("response", "").strip()
        print(f"      🧠 Kế hoạch:\n      {plan.replace(chr(10), chr(10) + '      ')}\n")
        return plan
    except Exception as e:
        print(f"   ❌ Planner Lỗi: {e}")
        return ""

# ================= AGENT 2: CODER (1.5B) =================
def run_coder_agent(question, plan, dfs, max_retries=2):
    schema_str = get_compact_schema(dfs)
    table_names = list(dfs.keys())
    
    # Nếu chỉ có 1 bảng, ép AI dùng đúng tên đó
    force_rule = ""
    if len(table_names) == 1:
        force_rule = f"BẮT BUỘC LẤY DỮ LIỆU BẰNG LỆNH: `df = dfs['{table_names[0]}']`"
    
    error_msg, prev_code = None, None
    
    for attempt in range(max_retries + 1):
        prompt = f"""Bạn là Coder. Viết code Python theo kế hoạch:
KẾ HOẠCH:
{plan}

CÁC BẢNG ĐANG CÓ SẴN: {table_names}
{schema_str}

{force_rule}

QUY TẮC TỐI THƯỢNG:
1. KHÔNG VIẾT `import`.
2. KHÔNG DÙNG `read_csv`. (Nếu dùng, code sẽ lỗi ngay).
3. Gán kết quả vào biến `ans`.

Viết code trong khối ```python ... ```.
"""
        if error_msg and prev_code:
            prompt += f"""
            LẦN TRƯỚC BẠN VIẾT:
            ```python
            {prev_code}
            ```
            LỖI: {error_msg}. TUYỆT ĐỐI KHÔNG DÙNG read_csv. Sửa lại đi.
            """

        payload = {
            "model": CODER_MODEL, "prompt": prompt, "stream": False, 
            "options": {"temperature": 0.0, "num_ctx": 8192, "num_predict": 300}
        }
        
        try:
            res = requests.post(OLLAMA_URL, json=payload, timeout=120)
            llm_response = res.json().get("response", "")
        except Exception as e:
            print(f"      ❌ Coder Lỗi: {e}")
            return None
            
        match = re.search(r"```python\n(.*?)```", llm_response, re.DOTALL)
        code = match.group(1) if match else llm_response
        prev_code = code
        
        # CHẶN ĐỨNG NẾU CÓ read_csv
        if "read_csv" in code:
            error_msg = "LỖI NGHIÊM TRỌNG: Bạn đã dùng read_csv. Hãy dùng dfs['tên_bảng']."
            print(f"      ⚠️ Lỗi: AI vẫn cố tình dùng read_csv.")
            continue
            
        # Xóa import nếu AI lén viết
        code = re.sub(r'^\s*(import|from)\s+.*$', '', code, flags=re.MULTILINE)
        
        print(f"      📝 Code AI viết:\n{code}\n")
        
        safe_builtins = {
            'len': len, 'range': range, 'str': str, 'int': int, 'float': float, 
            'list': list, 'dict': dict, 'set': set, 'sum': sum, 'min': min, 'max': max, 
            'abs': abs, 'round': round, 'zip': zip
        }
        local_vars = {"dfs": dfs, "pd": pd, "np": np, "datetime": datetime, "timedelta": timedelta, "calendar": calendar}
        
        try:
            exec(code, {"__builtins__": safe_builtins}, local_vars)
            ans = local_vars.get("ans")
            if ans is not None or "ans" in local_vars:
                return ans
            else:
                error_msg = "Code không gán giá trị cho biến `ans`."
        except Exception as e:
            error_msg = str(e)
            print(f"      ⚠️ Code bị lỗi: {error_msg}")
            
    return None

# ================= AGENT 3: FORMATTER =================
def run_formatter_agent(ans, q_id):
    if ans is None:
        return {"id": q_id, "type": "unanswerable", "reason": "Không tính được"}
    if isinstance(ans, pd.DataFrame):
        ans = ans.replace({np.nan: None})
        return {"id": q_id, "type": "table", "answer": {"columns": [str(c) for c in ans.columns], "rows": ans.values.tolist()}}
    if isinstance(ans, pd.Series): ans = ans.tolist()
    if isinstance(ans, (np.integer, np.floating)): ans = ans.item()
    if isinstance(ans, (pd.Timestamp, datetime)): return {"id": q_id, "type": "date", "answer": ans.strftime("%Y-%m-%d")}
    if isinstance(ans, (int, float)):
        if isinstance(ans, float) and ans.is_integer(): ans = int(ans)
        return {"id": q_id, "type": "number", "answer": ans}
    if isinstance(ans, bool): return {"id": q_id, "type": "boolean", "answer": ans}
    if isinstance(ans, list):
        ans = [str(x) for x in ans if pd.notna(x)]
        return {"id": q_id, "type": "list", "answer": ans}
    return {"id": q_id, "type": "string", "answer": str(ans).strip()}

# ================= ORCHESTRATOR =================
def load_biz_data(biz_dir):
    dfs = {}
    if not biz_dir.exists(): return dfs
    for f in biz_dir.iterdir():
        if f.name.startswith("~$") or not f.is_file(): continue
        try:
            if f.suffix.lower() == ".csv":
                try: dfs[f.stem] = pd.read_csv(f, encoding='utf-8')
                except: dfs[f.stem] = pd.read_csv(f, encoding='cp1258')
            elif f.suffix.lower() == ".xlsx":
                xls = pd.ExcelFile(f)
                for sheet in xls.sheet_names:
                    key = f.stem if len(xls.sheet_names) == 1 else f"{f.stem}_{sheet}"
                    dfs[key] = pd.read_excel(f, sheet_name=sheet)
            elif f.suffix.lower() == ".sqlite":
                conn = sqlite3.connect(f)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                for t in cursor.fetchall():
                    dfs[t[0]] = pd.read_sql(f"SELECT * FROM {t[0]}", conn)
                conn.close()
        except Exception as e:
            pass
    return dfs

def main():
    rulebook = ""
    if (SPLIT_DIR / "rulebook.md").exists():
        rulebook = (SPLIT_DIR / "rulebook.md").read_text(encoding="utf-8")
        
    questions = [json.loads(l) for l in open(SPLIT_DIR / "questions.jsonl", "r", encoding="utf-8") if l.strip()]
    
    # CHẠY THỬ 5 CÂU ĐẦU
    questions = questions[:5] 
    
    print(f"🚀 Bắt đầu chạy Planner + Coder trên {len(questions)} câu hỏi...")
    
    biz_cache = {}
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        for i, q in enumerate(questions):
            biz_id = q["business_id"]
            
            if biz_id not in biz_cache:
                print(f"\n📁 Đang load data cho: {biz_id}")
                biz_cache[biz_id] = load_biz_data(DATA_DIR / biz_id)
            dfs_all = biz_cache[biz_id]
            
            if not dfs_all:
                rec = {"id": q["id"], "type": "unanswerable", "reason": "Không có data"}
            else:
                print(f"\n❓ Câu hỏi: {q['question']}")
                dfs_filtered = filter_relevant_tables(q["question"], dfs_all)
                print(f"   🔍 Đã lọc: {len(dfs_filtered)}/{len(dfs_all)} bảng")
                
                plan = run_planner_agent(q["question"], dfs_filtered, rulebook)
                
                if plan:
                    ans = run_coder_agent(q["question"], plan, dfs_filtered)
                    rec = run_formatter_agent(ans, q["id"])
                else:
                    rec = {"id": q["id"], "type": "unanswerable", "reason": "AI không lên được kế hoạch"}
                
            f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f_out.flush()
            print(f"✅ KẾT QUẢ CÂU {i+1}: {rec['type']} -> {rec.get('answer')}\n" + "="*60 + "\n")
                
    print(f"🎉 Hoàn tất! File: {OUTPUT_FILE.name}")

if __name__ == "__main__":
    main()