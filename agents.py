'''
Tôi đã hiểu toàn bộ yêu cầu của bạn. Chúng ta sẽ nâng cấp hệ thống lên kiến trúc **"Thầy giáo DeepSeek"** (thay vì dùng model 7B local):

1. **Planner (3B)**: Đọc đề, lên kế hoạch.
2. **Coder (1.5B)**: Viết code dựa trên kế hoạch.
3. **Giáo viên (DeepSeek API)**: Kiểm tra code + kết quả. Nếu sai, thầy giáo giải thích và **viết lại code đúng** cho học trò (1.5B). Nếu đúng, duyệt `[PASSED]`.
4. **Log**: Lưu toàn bộ quá trình vào file `%H_%M_HUYKING.md`.
5. **Sửa lỗi Scope**: Truyền `dfs` làm tham số cho hàm `__solve__` để không bao giờ bị lỗi `local variable 'dfs' referenced before assignment`.
6. **Đọc dữ liệu**: Tự động đọc `README.md` và xử lý đa encoding (`utf-8`, `cp1258`, `latin1`).

Dưới đây là **FULL CODE** cho 3 file. Bạn hãy copy đè vào các file tương ứng trong `C:\Users\dinht\Downloads\train`.
'''
'''
### 📁 File 1: `agents.py` (Hệ thống 3 Agent & Gọi DeepSeek)
import json
import re
import os
import requests
import warnings
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

# ================= CẤU HÌNH =================
OLLAMA_URL = "http://localhost:11434/api/generate"
PLANNER_MODEL = "qwen2.5:3b"
CODER_MODEL = "qwen2.5-coder:1.5b"

# 🔴 ĐIỀN API KEY DEEPSEEK CỦA BẠN VÀO ĐÂY
DEEPSEEK_API_KEY = "sk-0b8f42c32f864fbd8cbb9412593bf54e" 
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

BASE_DIR = Path(r"C:\Users\dinht\Downloads\train")
TRAIN_DIR = BASE_DIR / "train"
DATA_DIR = TRAIN_DIR / "data"

RULEBOOK = """
LUẬT CƠ BẢN:
1. DOANH THU: Chỉ tính đơn KHÔNG HỦY, KHÔNG TRẢ HÀNG.
2. SỐ ĐƠN: Chỉ đếm đơn không hủy, không trả.
3. THỜI GIAN: "Tháng M/Y" từ ngày 1 đến hết tháng. "Tuần" bắt đầu thứ 2. "N ngày gần nhất" tính cả hôm nay.
4. Nếu không tìm thấy dữ liệu, gán `ans = None` và `reason = "Lý do cụ thể"`.
5. CHỈ TRẢ VỀ GIÁ TRỊ: Tuyệt đối không viết câu giải thích vào biến `ans`.
"""

def _detect_sep(fp):
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        line = f.readline()
        if ';' in line: return ';'
        if '\t' in line: return '\t'
        return ','

def load_biz_data(biz_id, data_dir):
    biz_dir = Path(data_dir) / biz_id
    dfs = {}
    if not biz_dir.exists(): return dfs
    for f in biz_dir.iterdir():
        if f.name.startswith("~$") or not f.is_file(): continue
        if f.suffix.lower() not in [".csv", ".xlsx"]: continue
        try:
            if f.suffix.lower() == ".csv":
                sep = _detect_sep(f)
                for enc in ['utf-8', 'cp1258', 'latin1']:
                    try:
                        dfs[f.stem] = pd.read_csv(f, encoding=enc, sep=sep, on_bad_lines='skip', low_memory=False)
                        break
                    except: continue
            elif f.suffix.lower() == ".xlsx":
                import openpyxl
                wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
                for sn in wb.sheetnames:
                    data = list(wb[sn].values)
                    if not data: continue
                    best_row = max(range(min(10, len(data))), key=lambda i: sum(1 for v in data[i] if v is not None))
                    headers = [str(h).strip() if h is not None else f"Unnamed_{idx}" for idx, h in enumerate(data[best_row])]
                    rows = data[best_row+1:]
                    clean = [list(r)[:len(headers)] + [None]*(len(headers)-len(r)) for r in rows]
                    df_s = pd.DataFrame(clean, columns=headers)
                    key = f.stem if len(wb.sheetnames)==1 else f"{f.stem}_{sn}"
                    dfs[key] = df_s.dropna(how='all')
                wb.close()
        except: pass
    return dfs

def get_readme(biz_id, data_dir):
    p = Path(data_dir) / biz_id / "README.md"
    if p.exists():
        try: text = p.read_text(encoding='utf-8')
        except: 
            try: text = p.read_text(encoding='cp1258')
            except: text = ""
        return text[:2000]
    return ""

def parse_date_safe(series):
    s = series.astype(str).str.strip()
    res = pd.to_datetime(s, errors='coerce', format='%Y-%m-%d')
    if res.notna().sum() > 0.5*len(res): return res
    res = pd.to_datetime(s, errors='coerce', dayfirst=True)
    if res.notna().sum() > 0.5 * len(res): return res
    return pd.to_datetime(s, errors='coerce')

def clean_money(s):
    return pd.to_numeric(s.astype(str).str.replace(r'[^0-9.-]', '', regex=True), errors='coerce').fillna(0)

def clean_number(s):
    return pd.to_numeric(s.astype(str).str.replace(r'[^0-9.-]', '', regex=True), errors='coerce').fillna(0)

def execute_ai_code(code_str, dfs, question, as_of_date):
    if not code_str: return None, None, None, "Không có code"
    # FIX LỖI SCOPE: Truyền dfs làm tham số
    wrapper = f"""
def __solve__(dfs, question, as_of_date):
{chr(10).join('    ' + line for line in code_str.split(chr(10)))}
    return locals().get('ans', None), locals().get('reason', None), locals().get('ans_type', None)
"""
    env = {"__builtins__": __builtins__, "pd": pd, "np": np, "datetime": datetime, "timedelta": timedelta,
           "parse_date_safe": parse_date_safe, "clean_money": clean_money, "clean_number": clean_number}
    lv = {}
    try:
        exec(wrapper, env, lv)
        res = lv["__solve__"](dfs, question, as_of_date)
        return res[0], res[1], res[2], None
    except Exception as e:
        return None, None, None, f"Lỗi Runtime: {str(e)}"

def format_ans(ans, ans_type, question):
    if ans is None: return None
    if isinstance(ans, (pd.Series, tuple)): ans = ans.tolist()
    if hasattr(ans, 'item'): ans = ans.item()
    if isinstance(ans, pd.Timestamp): return ans.strftime("%Y-%m")
    if isinstance(ans, bool): return ans
    if isinstance(ans, (int, float, np.integer, np.floating)):
        v = float(ans)
        if v.is_integer(): v = int(v)
        if (ans_type == "percent") or ("%" in question) or ("tỷ lệ" in question.lower()):
            if abs(v) <= 1.0 and v != 0: v = round(v*100, 2)
            return round(v, 2)
        return v
    if isinstance(ans, list): return [str(x) for x in ans if pd.notna(x)]
    return str(ans).strip()

def check_correct(pred, gold):
    if pred is None or gold is None: return False
    g_ans = gold["answer"]
    g_type = gold.get("type", "")
    aliases = gold.get("alias", [])
    
    if g_type in ("number", "percent"):
        try: return abs(float(pred) - float(g_ans)) <= (1e-6 if g_type=="number" else 0.01)
        except: return False
    if g_type == "list":
        p = [str(x).strip().lower() for x in (pred or [])]
        g = [str(x).strip().lower() for x in g_ans]
        if p == g: return True
        for a in aliases:
            if isinstance(a, list) and p == [str(x).lower() for x in a]: return True
        return False
    p_s = str(pred).strip().lower()
    g_s = str(g_ans).strip().lower()
    if p_s == g_s: return True
    for a in aliases:
        if isinstance(a, str) and p_s == a.lower(): return True
    return False

def pack_submission(q_id, ans, reason, ans_type, question):
    if ans is None:
        if reason: return {"id": q_id, "type": "unanswerable", "reason": str(reason)}
        return None
    if isinstance(ans, (int, float, np.integer, np.floating)) or hasattr(ans, 'item'):
        typ = "percent" if (ans_type=="percent" or "%" in question or "tỷ lệ" in question.lower()) else "number"
        v = float(ans)
        return {"id": q_id, "type": typ, "answer": int(v) if v.is_integer() else v}
    if isinstance(ans, list): return {"id": q_id, "type": "list", "answer": [str(x) for x in ans]}
    if isinstance(ans, bool): return {"id": q_id, "type": "boolean", "answer": ans}
    return {"id": q_id, "type": "string", "answer": str(ans).strip()}

def _ollama(model, prompt, timeout=180):
    print(f"     [Hệ thống]: Đang gọi {model}...")
    try:
        r = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}, timeout=timeout)
        return r.json().get("response", "")
    except Exception as e:
        return f"LỖI_OLLAMA: {e}"

def planner_plan(question, as_of, schema, readme=""):
    prompt = f"""{RULEBOOK}
Câu hỏi: "{question}"
Ngày chốt: {as_of}
Thông tin doanh nghiệp: {readme}
Bảng dữ liệu: {schema}

Hãy LẬP KẾ HOẠCH ngắn gọn (bằng tiếng Việt, dưới 100 chữ):
- Cần bảng nào?
- Lọc điều kiện gì? (ngày, trạng thái, tên)
- Tính gì? (sum, count, groupby...)
"""
    return _ollama(PLANNER_MODEL, prompt, 120).strip()

def coder_write(question, plan, schema, readme="", examples=""):
    prompt = f"""{RULEBOOK}
Câu hỏi: "{question}"
Kế hoạch: {plan}
Thông tin doanh nghiệp: {readme}
Cấu trúc dữ liệu (dfs):
{schema}
{examples}

Viết code Python Pandas, gán vào `ans`. Code trong ```python...```.

QUY TẮC BẮT BUỘC:
1. KHÔNG CẦN import thư viện.
2. TUYỆT ĐỐI KHÔNG DÙNG `pd.read_csv` HAY `pd.read_excel`. Dữ liệu đã có sẵn trong `dfs`. Lấy dữ liệu bằng `df = dfs['tên_bảng']`.
3. Cột ngày dùng `parse_date_safe(df['cột'])`.
4. Cột tiền dùng `clean_money(df['cột'])`.
5. Nếu không tìm thấy dữ liệu gán `ans=None`.
"""
    text = _ollama(CODER_MODEL, prompt, 120)
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else None

def deepseek_review(question, schema, readme, code, output, gold_answer, gold_type):
    prompt = f"""Bạn là một Giáo viên chấm bài nghiêm khắc. Bạn đang hướng dẫn một học sinh yếu (model 1.5B) viết code.
Câu hỏi: {question}
Thông tin doanh nghiệp (README):
{readme}

Cấu trúc dữ liệu (dfs):
{schema}

Code của học sinh:
```python
{code}
```
Kết quả code chạy ra: {output}
Đáp án đúng của hệ thống: {gold_answer} (Type: {gold_type})

Hãy phân tích xem code trên đã đúng chưa.
- Nếu đúng, in ra chính xác: [PASSED]
- Nếu sai, hãy giải thích ngắn gọn lỗi sai (ví dụ: quên lọc đơn hủy, sai cột ngày, sai quy đổi đơn vị...) và cung cấp một đoạn code Python đã sửa hoàn chỉnh trong block ```python ... ```. Code sửa phải dùng trực tiếp `dfs['tên_bảng']` (không dùng read_csv).
"""
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": DEEPSEEK_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.0}
    try:
        res = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=120)
        if res.status_code == 200:
            text = res.json()["choices"][0]["message"]["content"]
            if "[PASSED]" in text:
                return True, text, None
            else:
                m = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
                fixed_code = m.group(1).strip() if m else None
                return False, text, fixed_code
        else:
            return False, f"Lỗi API {res.status_code}", None
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}", None

def deepseek_review_no_gold(question, schema, readme, code, output):
    prompt = f"""Bạn là một Giáo viên chấm bài nghiêm khắc.
Câu hỏi: {question}
Thông tin doanh nghiệp: {readme}
Cấu trúc dữ liệu:
{schema}

Code của học sinh:
```python
{code}
```
Kết quả code chạy ra: {output}

Hãy kiểm tra xem code trên có lỗi logic nào không (ví dụ: quên lọc đơn hủy/trả hàng, sai cột ngày, sai quy đổi đơn vị, tính sai công thức...).
- Nếu code có vẻ ĐÚNG và hợp lý, in ra chính xác: [PASSED]
- Nếu SAI, hãy giải thích ngắn gọn lỗi sai và cung cấp một đoạn code Python đã sửa hoàn chỉnh trong block ```python ... ```.
"""
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": DEEPSEEK_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.0}
    try:
        res = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=120)
        if res.status_code == 200:
            text = res.json()["choices"][0]["message"]["content"]
            if "[PASSED]" in text:
                return True, text, None
            else:
                m = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
                fixed_code = m.group(1).strip() if m else None
                return False, text, fixed_code
        else:
            return False, f"Lỗi API {res.status_code}", None
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}", None
'''
'''
Lỗi `SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes...` là do đường dẫn Windows `C:\Users\...` trong code bị thiếu chữ `r` ở đầu. Khi Python đọc chuỗi `"C:\Users..."`, nó tưởng `\U` là một ký tự đặc biệt (Unicode) nên báo lỗi.

Để khắc phục triệt để và không bao giờ gặp lại lỗi này, tôi đã sửa lại đường dẫn thành dấu gạch chéo xuôi `/` (Python trên Windows vẫn hiểu bình thường, mà lại không lo lỗi font).

Bạn hãy **xóa sạch** 3 file cũ và dán lại code dưới đây (đã fix sạch lỗi):


### 📁 File 1: `agents.py` (Bản Fix Lỗi Đường Dẫn)

import json
import re
import os
import requests
import warnings
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

# ================= CẤU HÌNH =================
OLLAMA_URL = "http://localhost:11434/api/generate"
PLANNER_MODEL = "qwen2.5:3b"
CODER_MODEL = "qwen2.5-coder:1.5b"

# 🔴 ĐIỀN API KEY DEEPSEEK CỦA BẠN VÀO ĐÂY
DEEPSEEK_API_KEY = "sk-0b8f42c32f864fbd8cbb9412593bf54e" 
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# Đã thay đổi dấu \ thành / để tránh lỗi unicodeescape
BASE_DIR = Path("C:/Users/dinht/Downloads/train")
TRAIN_DIR = BASE_DIR / "train"
DATA_DIR = TRAIN_DIR / "data"

RULEBOOK = """
LUẬT CƠ BẢN:
1. DOANH THU: Chỉ tính đơn KHÔNG HỦY, KHÔNG TRẢ HÀNG.
2. SỐ ĐƠN: Chỉ đếm đơn không hủy, không trả.
3. THỜI GIAN: "Tháng M/Y" từ ngày 1 đến hết tháng. "Tuần" bắt đầu thứ 2. "N ngày gần nhất" tính cả hôm nay.
4. Nếu không tìm thấy dữ liệu, gán `ans = None` và `reason = "Lý do cụ thể"`.
5. CHỈ TRẢ VỀ GIÁ TRỊ: Tuyệt đối không viết câu giải thích vào biến `ans`.
"""

def _detect_sep(fp):
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        line = f.readline()
        if ';' in line: return ';'
        if '\t' in line: return '\t'
        return ','

def load_biz_data(biz_id, data_dir):
    biz_dir = Path(data_dir) / biz_id
    dfs = {}
    if not biz_dir.exists(): return dfs
    for f in biz_dir.iterdir():
        if f.name.startswith("~$") or not f.is_file(): continue
        if f.suffix.lower() not in [".csv", ".xlsx"]: continue
        try:
            if f.suffix.lower() == ".csv":
                sep = _detect_sep(f)
                for enc in ['utf-8', 'cp1258', 'latin1']:
                    try:
                        dfs[f.stem] = pd.read_csv(f, encoding=enc, sep=sep, on_bad_lines='skip', low_memory=False)
                        break
                    except: continue
            elif f.suffix.lower() == ".xlsx":
                import openpyxl
                wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
                for sn in wb.sheetnames:
                    data = list(wb[sn].values)
                    if not data: continue
                    best_row = max(range(min(10, len(data))), key=lambda i: sum(1 for v in data[i] if v is not None))
                    headers = [str(h).strip() if h is not None else f"Unnamed_{idx}" for idx, h in enumerate(data[best_row])]
                    rows = data[best_row+1:]
                    clean = [list(r)[:len(headers)] + [None]*(len(headers)-len(r)) for r in rows]
                    df_s = pd.DataFrame(clean, columns=headers)
                    key = f.stem if len(wb.sheetnames)==1 else f"{f.stem}_{sn}"
                    dfs[key] = df_s.dropna(how='all')
                wb.close()
        except: pass
    return dfs

def get_readme(biz_id, data_dir):
    p = Path(data_dir) / biz_id / "README.md"
    if p.exists():
        try: text = p.read_text(encoding='utf-8')
        except: 
            try: text = p.read_text(encoding='cp1258')
            except: text = ""
        return text[:2000]
    return ""

def parse_date_safe(series):
    s = series.astype(str).str.strip()
    res = pd.to_datetime(s, errors='coerce', format='%Y-%m-%d')
    if res.notna().sum() > 0.5*len(res): return res
    res = pd.to_datetime(s, errors='coerce', dayfirst=True)
    if res.notna().sum() > 0.5 * len(res): return res
    return pd.to_datetime(s, errors='coerce')

def clean_money(s):
    return pd.to_numeric(s.astype(str).str.replace(r'[^0-9.-]', '', regex=True), errors='coerce').fillna(0)

def clean_number(s):
    return pd.to_numeric(s.astype(str).str.replace(r'[^0-9.-]', '', regex=True), errors='coerce').fillna(0)

def execute_ai_code(code_str, dfs, question, as_of_date):
    if not code_str: return None, None, None, "Không có code"
    # FIX LỖI SCOPE: Truyền dfs làm tham số
    wrapper = f"""
def __solve__(dfs, question, as_of_date):
{chr(10).join('    ' + line for line in code_str.split(chr(10)))}
    return locals().get('ans', None), locals().get('reason', None), locals().get('ans_type', None)
"""
    env = {"__builtins__": __builtins__, "pd": pd, "np": np, "datetime": datetime, "timedelta": timedelta,
           "parse_date_safe": parse_date_safe, "clean_money": clean_money, "clean_number": clean_number}
    lv = {}
    try:
        exec(wrapper, env, lv)
        res = lv["__solve__"](dfs, question, as_of_date)
        return res[0], res[1], res[2], None
    except Exception as e:
        return None, None, None, f"Lỗi Runtime: {str(e)}"

def format_ans(ans, ans_type, question):
    if ans is None: return None
    if isinstance(ans, (pd.Series, tuple)): ans = ans.tolist()
    if hasattr(ans, 'item'): ans = ans.item()
    if isinstance(ans, pd.Timestamp): return ans.strftime("%Y-%m")
    if isinstance(ans, bool): return ans
    if isinstance(ans, (int, float, np.integer, np.floating)):
        v = float(ans)
        if v.is_integer(): v = int(v)
        if (ans_type == "percent") or ("%" in question) or ("tỷ lệ" in question.lower()):
            if abs(v) <= 1.0 and v != 0: v = round(v*100, 2)
            return round(v, 2)
        return v
    if isinstance(ans, list): return [str(x) for x in ans if pd.notna(x)]
    return str(ans).strip()

def check_correct(pred, gold):
    if pred is None or gold is None: return False
    g_ans = gold["answer"]
    g_type = gold.get("type", "")
    aliases = gold.get("alias", [])
    
    if g_type in ("number", "percent"):
        try: return abs(float(pred) - float(g_ans)) <= (1e-6 if g_type=="number" else 0.01)
        except: return False
    if g_type == "list":
        p = [str(x).strip().lower() for x in (pred or [])]
        g = [str(x).strip().lower() for x in g_ans]
        if p == g: return True
        for a in aliases:
            if isinstance(a, list) and p == [str(x).lower() for x in a]: return True
        return False
    p_s = str(pred).strip().lower()
    g_s = str(g_ans).strip().lower()
    if p_s == g_s: return True
    for a in aliases:
        if isinstance(a, str) and p_s == a.lower(): return True
    return False

def pack_submission(q_id, ans, reason, ans_type, question):
    if ans is None:
        if reason: return {"id": q_id, "type": "unanswerable", "reason": str(reason)}
        return None
    if isinstance(ans, (int, float, np.integer, np.floating)) or hasattr(ans, 'item'):
        typ = "percent" if (ans_type=="percent" or "%" in question or "tỷ lệ" in question.lower()) else "number"
        v = float(ans)
        return {"id": q_id, "type": typ, "answer": int(v) if v.is_integer() else v}
    if isinstance(ans, list): return {"id": q_id, "type": "list", "answer": [str(x) for x in ans]}
    if isinstance(ans, bool): return {"id": q_id, "type": "boolean", "answer": ans}
    return {"id": q_id, "type": "string", "answer": str(ans).strip()}

def _ollama(model, prompt, timeout=180):
    print(f"     [Hệ thống]: Đang gọi {model}...")
    try:
        r = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}, timeout=timeout)
        return r.json().get("response", "")
    except Exception as e:
        return f"LỖI_OLLAMA: {e}"

def planner_plan(question, as_of, schema, readme=""):
    prompt = f"""{RULEBOOK}
Câu hỏi: "{question}"
Ngày chốt: {as_of}
Thông tin doanh nghiệp: {readme}
Bảng dữ liệu: {schema}

Hãy LẬP KẾ HOẠCH ngắn gọn (bằng tiếng Việt, dưới 100 chữ):
- Cần bảng nào?
- Lọc điều kiện gì? (ngày, trạng thái, tên)
- Tính gì? (sum, count, groupby...)
"""
    return _ollama(PLANNER_MODEL, prompt, 120).strip()

def coder_write(question, plan, schema, readme="", examples=""):
    prompt = f"""{RULEBOOK}
Câu hỏi: "{question}"
Kế hoạch: {plan}
Thông tin doanh nghiệp: {readme}
Cấu trúc dữ liệu (dfs):
{schema}
{examples}

Viết code Python Pandas, gán vào `ans`. Code trong ```python...```.

QUY TẮC BẮT BUỘC:
1. KHÔNG CẦN import thư viện.
2. TUYỆT ĐỐI KHÔNG DÙNG `pd.read_csv` HAY `pd.read_excel`. Dữ liệu đã có sẵn trong `dfs`. Lấy dữ liệu bằng `df = dfs['tên_bảng']`.
3. Cột ngày dùng `parse_date_safe(df['cột'])`.
4. Cột tiền dùng `clean_money(df['cột'])`.
5. Nếu không tìm thấy dữ liệu gán `ans=None`.
"""
    text = _ollama(CODER_MODEL, prompt, 120)
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else None

def deepseek_review(question, schema, readme, code, output, gold_answer, gold_type):
    prompt = f"""Bạn là một Giáo viên chấm bài nghiêm khắc. Bạn đang hướng dẫn một học sinh yếu (model 1.5B) viết code.
Câu hỏi: {question}
Thông tin doanh nghiệp (README):
{readme}

Cấu trúc dữ liệu (dfs):
{schema}

Code của học sinh:
```python
{code}
```
Kết quả code chạy ra: {output}
Đáp án đúng của hệ thống: {gold_answer} (Type: {gold_type})

Hãy phân tích xem code trên đã đúng chưa.
- Nếu đúng, in ra chính xác: [PASSED]
- Nếu sai, hãy giải thích ngắn gọn lỗi sai (ví dụ: quên lọc đơn hủy, sai cột ngày, sai quy đổi đơn vị...) và cung cấp một đoạn code Python đã sửa hoàn chỉnh trong block ```python ... ```. Code sửa phải dùng trực tiếp `dfs['tên_bảng']` (không dùng read_csv).
"""
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": DEEPSEEK_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.0}
    try:
        res = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=120)
        if res.status_code == 200:
            text = res.json()["choices"][0]["message"]["content"]
            if "[PASSED]" in text:
                return True, text, None
            else:
                m = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
                fixed_code = m.group(1).strip() if m else None
                return False, text, fixed_code
        else:
            return False, f"Lỗi API {res.status_code}", None
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}", None

def deepseek_review_no_gold(question, schema, readme, code, output):
    prompt = f"""Bạn là một Giáo viên chấm bài nghiêm khắc.
Câu hỏi: {question}
Thông tin doanh nghiệp: {readme}
Cấu trúc dữ liệu:
{schema}

Code của học sinh:
```python
{code}
```
Kết quả code chạy ra: {output}

Hãy kiểm tra xem code trên có lỗi logic nào không (ví dụ: quên lọc đơn hủy/trả hàng, sai cột ngày, sai quy đổi đơn vị, tính sai công thức...).
- Nếu code có vẻ ĐÚNG và hợp lý, in ra chính xác: [PASSED]
- Nếu SAI, hãy giải thích ngắn gọn lỗi sai và cung cấp một đoạn code Python đã sửa hoàn chỉnh trong block ```python ... ```.
"""
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": DEEPSEEK_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.0}
    try:
        res = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=120)
        if res.status_code == 200:
            text = res.json()["choices"][0]["message"]["content"]
            if "[PASSED]" in text:
                return True, text, None
            else:
                m = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
                fixed_code = m.group(1).strip() if m else None
                return False, text, fixed_code
        else:
            return False, f"Lỗi API {res.status_code}", None
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}", None
'''


#Lỗi này là do **dấu gạch chéo ngược `\`** trong đường dẫn `C:\Users` bị Python hiểu nhầm thành ký tự đặc biệt (`\U`). 

#Đồng thời, trong file `agents.py` của bạn, dòng số 12 đang bị lỗi cú pháp do dùng sai dấu ngoặc kép (bạn đang dùng `'''` thay vì `"""`).

#Để giải quyết triệt để, tôi đã sửa lại toàn bộ code, **thay thế tất cả dấu `\` thành `/`** (Python trên Windows vẫn hiểu và không bao giờ bị lỗi font nữa). 

#Bạn hãy **XÓA SẠCH** cả 3 file cũ, sau đó tạo lại 3 file mới và dán đoạn code dưới đây vào nhé:

### 📁 File 1: `agents.py`
import json
import re
import os
import requests
import warnings
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

# ================= CẤU HÌNH =================
OLLAMA_URL = "http://localhost:11434/api/generate"
PLANNER_MODEL = "qwen2.5:3b"
CODER_MODEL = "qwen2.5-coder:1.5b"

# 🔴 ĐIỀN API KEY DEEPSEEK CỦA BẠN VÀO ĐÂY
DEEPSEEK_API_KEY = "sk-0b8f42c32f864fbd8cbb9412593bf54e" 
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# Đã thay đổi dấu \ thành / để tránh lỗi unicodeescape
BASE_DIR = Path("C:/Users/dinht/Downloads/train")
TRAIN_DIR = BASE_DIR / "train"
DATA_DIR = TRAIN_DIR / "data"

RULEBOOK = """
LUẬT CƠ BẢN:
1. DOANH THU: Chỉ tính đơn KHÔNG HỦY, KHÔNG TRẢ HÀNG.
2. SỐ ĐƠN: Chỉ đếm đơn không hủy, không trả.
3. THỜI GIAN: "Tháng M/Y" từ ngày 1 đến hết tháng. "Tuần" bắt đầu thứ 2. "N ngày gần nhất" tính cả hôm nay.
4. Nếu không tìm thấy dữ liệu, gán `ans = None` và `reason = "Lý do cụ thể"`.
5. CHỈ TRẢ VỀ GIÁ TRỊ: Tuyệt đối không viết câu giải thích vào biến `ans`.
"""

def _detect_sep(fp):
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        line = f.readline()
        if ';' in line: return ';'
        if '\t' in line: return '\t'
        return ','

def load_biz_data(biz_id, data_dir):
    biz_dir = Path(data_dir) / biz_id
    dfs = {}
    if not biz_dir.exists(): return dfs
    for f in biz_dir.iterdir():
        if f.name.startswith("~$") or not f.is_file(): continue
        if f.suffix.lower() not in [".csv", ".xlsx"]: continue
        try:
            if f.suffix.lower() == ".csv":
                sep = _detect_sep(f)
                for enc in ['utf-8', 'cp1258', 'latin1']:
                    try:
                        dfs[f.stem] = pd.read_csv(f, encoding=enc, sep=sep, on_bad_lines='skip', low_memory=False)
                        break
                    except: continue
            elif f.suffix.lower() == ".xlsx":
                import openpyxl
                wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
                for sn in wb.sheetnames:
                    data = list(wb[sn].values)
                    if not data: continue
                    best_row = max(range(min(10, len(data))), key=lambda i: sum(1 for v in data[i] if v is not None))
                    headers = [str(h).strip() if h is not None else f"Unnamed_{idx}" for idx, h in enumerate(data[best_row])]
                    rows = data[best_row+1:]
                    clean = [list(r)[:len(headers)] + [None]*(len(headers)-len(r)) for r in rows]
                    df_s = pd.DataFrame(clean, columns=headers)
                    key = f.stem if len(wb.sheetnames)==1 else f"{f.stem}_{sn}"
                    dfs[key] = df_s.dropna(how='all')
                wb.close()
        except: pass
    return dfs

def get_readme(biz_id, data_dir):
    p = Path(data_dir) / biz_id / "README.md"
    if p.exists():
        try: text = p.read_text(encoding='utf-8')
        except: 
            try: text = p.read_text(encoding='cp1258')
            except: text = ""
        return text[:2000]
    return ""

def parse_date_safe(series):
    s = series.astype(str).str.strip()
    res = pd.to_datetime(s, errors='coerce', format='%Y-%m-%d')
    if res.notna().sum() > 0.5*len(res): return res
    res = pd.to_datetime(s, errors='coerce', dayfirst=True)
    if res.notna().sum() > 0.5 * len(res): return res
    return pd.to_datetime(s, errors='coerce')

def clean_money(s):
    return pd.to_numeric(s.astype(str).str.replace(r'[^0-9.-]', '', regex=True), errors='coerce').fillna(0)

def clean_number(s):
    return pd.to_numeric(s.astype(str).str.replace(r'[^0-9.-]', '', regex=True), errors='coerce').fillna(0)

def execute_ai_code(code_str, dfs, question, as_of_date):
    if not code_str: return None, None, None, "Không có code"
    wrapper = f"""
def __solve__(dfs, question, as_of_date):
{chr(10).join('    ' + line for line in code_str.split(chr(10)))}
    return locals().get('ans', None), locals().get('reason', None), locals().get('ans_type', None)
"""
    env = {"__builtins__": __builtins__, "pd": pd, "np": np, "datetime": datetime, "timedelta": timedelta,
           "parse_date_safe": parse_date_safe, "clean_money": clean_money, "clean_number": clean_number}
    lv = {}
    try:
        exec(wrapper, env, lv)
        res = lv["__solve__"](dfs, question, as_of_date)
        return res[0], res[1], res[2], None
    except Exception as e:
        return None, None, None, f"Lỗi Runtime: {str(e)}"

def format_ans(ans, ans_type, question):
    if ans is None: return None
    if isinstance(ans, (pd.Series, tuple)): ans = ans.tolist()
    if hasattr(ans, 'item'): ans = ans.item()
    if isinstance(ans, pd.Timestamp): return ans.strftime("%Y-%m")
    if isinstance(ans, bool): return ans
    if isinstance(ans, (int, float, np.integer, np.floating)):
        v = float(ans)
        if v.is_integer(): v = int(v)
        if (ans_type == "percent") or ("%" in question) or ("tỷ lệ" in question.lower()):
            if abs(v) <= 1.0 and v != 0: v = round(v*100, 2)
            return round(v, 2)
        return v
    if isinstance(ans, list): return [str(x) for x in ans if pd.notna(x)]
    return str(ans).strip()

def check_correct(pred, gold):
    if pred is None or gold is None: return False
    g_ans = gold["answer"]
    g_type = gold.get("type", "")
    aliases = gold.get("alias", [])
    
    if g_type in ("number", "percent"):
        try: return abs(float(pred) - float(g_ans)) <= (1e-6 if g_type=="number" else 0.01)
        except: return False
    if g_type == "list":
        p = [str(x).strip().lower() for x in (pred or [])]
        g = [str(x).strip().lower() for x in g_ans]
        if p == g: return True
        for a in aliases:
            if isinstance(a, list) and p == [str(x).lower() for x in a]: return True
        return False
    p_s = str(pred).strip().lower()
    g_s = str(g_ans).strip().lower()
    if p_s == g_s: return True
    for a in aliases:
        if isinstance(a, str) and p_s == a.lower(): return True
    return False

def pack_submission(q_id, ans, reason, ans_type, question):
    if ans is None:
        if reason: return {"id": q_id, "type": "unanswerable", "reason": str(reason)}
        return None
    if isinstance(ans, (int, float, np.integer, np.floating)) or hasattr(ans, 'item'):
        typ = "percent" if (ans_type=="percent" or "%" in question or "tỷ lệ" in question.lower()) else "number"
        v = float(ans)
        return {"id": q_id, "type": typ, "answer": int(v) if v.is_integer() else v}
    if isinstance(ans, list): return {"id": q_id, "type": "list", "answer": [str(x) for x in ans]}
    if isinstance(ans, bool): return {"id": q_id, "type": "boolean", "answer": ans}
    return {"id": q_id, "type": "string", "answer": str(ans).strip()}

def _ollama(model, prompt, timeout=180):
    print(f"     [Hệ thống]: Đang gọi {model}...")
    try:
        r = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}, timeout=timeout)
        return r.json().get("response", "")
    except Exception as e:
        return f"LỖI_OLLAMA: {e}"

def planner_plan(question, as_of, schema, readme=""):
    prompt = f"""{RULEBOOK}
Câu hỏi: "{question}"
Ngày chốt: {as_of}
Thông tin doanh nghiệp: {readme}
Bảng dữ liệu: {schema}

Hãy LẬP KẾ HOẠCH ngắn gọn (bằng tiếng Việt, dưới 100 chữ):
- Cần bảng nào?
- Lọc điều kiện gì? (ngày, trạng thái, tên)
- Tính gì? (sum, count, groupby...)
"""
    return _ollama(PLANNER_MODEL, prompt, 120).strip()

def coder_write(question, plan, schema, readme="", examples=""):
    prompt = f"""{RULEBOOK}
Câu hỏi: "{question}"
Kế hoạch: {plan}
Thông tin doanh nghiệp: {readme}
Cấu trúc dữ liệu (dfs):
{schema}
{examples}

Viết code Python Pandas, gán vào `ans`. Code trong ```python...```.

QUY TẮC BẮT BUỘC:
1. KHÔNG CẦN import thư viện.
2. TUYỆT ĐỐI KHÔNG DÙNG `pd.read_csv` HAY `pd.read_excel`. Dữ liệu đã có sẵn trong `dfs`. Lấy dữ liệu bằng `df = dfs['tên_bảng']`.
3. Cột ngày dùng `parse_date_safe(df['cột'])`.
4. Cột tiền dùng `clean_money(df['cột'])`.
5. Nếu không tìm thấy dữ liệu gán `ans=None`.
"""
    text = _ollama(CODER_MODEL, prompt, 120)
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else None

def deepseek_review(question, schema, readme, code, output, gold_answer, gold_type):
    prompt = f"""Bạn là một Giáo viên chấm bài nghiêm khắc. Bạn đang hướng dẫn một học sinh yếu (model 1.5B) viết code.
Câu hỏi: {question}
Thông tin doanh nghiệp (README):
{readme}

Cấu trúc dữ liệu (dfs):
{schema}

Code của học sinh:
```python
{code}
```
Kết quả code chạy ra: {output}
Đáp án đúng của hệ thống: {gold_answer} (Type: {gold_type})

Hãy phân tích xem code trên đã đúng chưa.
- Nếu đúng, in ra chính xác: [PASSED]
- Nếu sai, hãy giải thích ngắn gọn lỗi sai (ví dụ: quên lọc đơn hủy, sai cột ngày, sai quy đổi đơn vị...) và cung cấp một đoạn code Python đã sửa hoàn chỉnh trong block ```python ... ```. Code sửa phải dùng trực tiếp `dfs['tên_bảng']` (không dùng read_csv).
"""
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": DEEPSEEK_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.0}
    try:
        res = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=120)
        if res.status_code == 200:
            text = res.json()["choices"][0]["message"]["content"]
            if "[PASSED]" in text:
                return True, text, None
            else:
                m = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
                fixed_code = m.group(1).strip() if m else None
                return False, text, fixed_code
        else:
            return False, f"Lỗi API {res.status_code}", None
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}", None

def deepseek_review_no_gold(question, schema, readme, code, output):
    prompt = f"""Bạn là một Giáo viên chấm bài nghiêm khắc.
Câu hỏi: {question}
Thông tin doanh nghiệp: {readme}
Cấu trúc dữ liệu:
{schema}

Code của học sinh:
```python
{code}
```
Kết quả code chạy ra: {output}

Hãy kiểm tra xem code trên có lỗi logic nào không (ví dụ: quên lọc đơn hủy/trả hàng, sai cột ngày, sai quy đổi đơn vị, tính sai công thức...).
- Nếu code có vẻ ĐÚNG và hợp lý, in ra chính xác: [PASSED]
- Nếu SAI, hãy giải thích ngắn gọn lỗi sai và cung cấp một đoạn code Python đã sửa hoàn chỉnh trong block ```python ... ```.
"""
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": DEEPSEEK_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.0}
    try:
        res = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=120)
        if res.status_code == 200:
            text = res.json()["choices"][0]["message"]["content"]
            if "[PASSED]" in text:
                return True, text, None
            else:
                m = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
                fixed_code = m.group(1).strip() if m else None
                return False, text, fixed_code
        else:
            return False, f"Lỗi API {res.status_code}", None
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}", None