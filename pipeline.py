import pandas as pd
import numpy as np
import re
from datetime import datetime

def format_ans(ans, ans_type, question):
    if ans is None: return None
    if isinstance(ans, pd.DataFrame):
        if ans.empty: return None
        if ans_type == "list" or "top" in question.lower() or "nào" in question.lower():
            return [str(x) for x in ans.iloc[:, 0].tolist()]
        clean_df = ans.astype(object).where(pd.notnull(ans), None)
        return {"columns": [str(c) for c in clean_df.columns], "rows": clean_df.values.tolist()}

    if isinstance(ans, pd.Series): ans = ans.tolist()
    if hasattr(ans, 'item'): ans = ans.item()

    if isinstance(ans, (pd.Timestamp, datetime)):
        if "tháng" in question.lower() and "ngày" not in question.lower():
            return ans.strftime("%Y-%m")
        return ans.strftime("%Y-%m-%d")

    if isinstance(ans, (int, float, np.integer, np.floating)):
        v = float(ans)
        if (ans_type == "percent") or ("%" in question) or ("tỷ lệ" in question.lower()):
            if abs(v) <= 1.0 and v != 0: v = round(v * 100, 2)
            return round(v, 2)
        return int(v) if v.is_integer() else round(v, 2)

    if isinstance(ans, bool): return ans

    if isinstance(ans, (list, tuple)):
        clean_list = []
        for x in ans:
            if pd.isna(x): continue
            if isinstance(x, dict): clean_list.append(str(list(x.values())[0]))
            elif isinstance(x, (int, float, np.integer, np.floating)): clean_list.append(float(x) if not float(x).is_integer() else int(x))
            else: clean_list.append(str(x).strip())
        return clean_list

    ans_str = re.sub(r'^["\']|["\']$', '', str(ans).strip())
    return ans_str

def check_correct(pred, gold):
    if pred is None or gold is None: return False
    g_ans, g_type, aliases = gold["answer"], gold.get("type", ""), gold.get("alias", [])
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
    p_s, g_s = str(pred).strip().lower(), str(g_ans).strip().lower()
    if p_s == g_s: return True
    for a in aliases:
        if isinstance(a, str) and p_s == a.lower(): return True
    return False