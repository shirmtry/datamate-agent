import json
import urllib.error
import urllib.request

KEY = "sk-0b8f42c32f864fbd8cbb9412593bf54e"
for model in ["deepseek-flash", "deepseek-v4-pro"]:
    body = {"model": model,
            "messages": [{"role": "user", "content": 'tra json {"ok": true}'}],
            "response_format": {"type": "json_object"}, "max_tokens": 30, "temperature": 0}
    req = urllib.request.Request("https://api.deepseek.com/v1/chat/completions",
                                 data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + KEY,
                                          "Content-Type": "application/json",
                                          "User-Agent": "curl/8"})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=60))
        print(model, "OK", d["choices"][0]["message"]["content"][:60], d.get("usage"))
    except urllib.error.HTTPError as e:
        print(model, "ERR", e.code, e.read().decode()[:200])
