import json
import sys

sys.path.insert(0, r"C:\Users\dinht\Downloads\train")
sys.path.insert(0, r"C:\Users\dinht\Downloads\train\vendor")

import requests
import solve_all_train as S
from utils import load_biz_data, get_readme, get_full_schema

q = [json.loads(l) for l in open(S.QUESTIONS_FILE, encoding="utf-8")][1]
golds = {g["id"]: g for g in S.read_jsonl(S.ANSWERS_FILE)}
dfs = load_biz_data(q["business_id"], S.DATA_DIR)
prompt = S.build_prompt(q, get_full_schema(dfs), get_readme(q["business_id"], S.DATA_DIR, 3000), "")

print("id:", q["id"], "| prompt chars:", len(prompt))
for model in ["deepseek-flash", "deepseek-chat"]:
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "temperature": 0, "max_tokens": 1500,
            "response_format": {"type": "json_object"}}
    try:
        r = requests.post(S.API_URL, json=body, timeout=180,
                          headers={"Authorization": "Bearer " + S.API_KEY,
                                   "Content-Type": "application/json"})
        print(model, r.status_code)
        d = r.json()
        ch = d["choices"][0]
        print(" finish:", ch.get("finish_reason"), "| usage:", d.get("usage"))
        print(" content:", (ch["message"].get("content") or "")[:300])
        print(" keys:", list(ch["message"].keys()))
    except Exception as e:
        print(model, "ERR", e, getattr(r, "text", "")[:200])
