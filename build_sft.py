"""
build_sft.py — Gộp + làm sạch dữ liệu thành dataset chat để fine-tune.

Nguồn:
  - distill/pairs.jsonl  (gen_dataset.py sinh: câu hỏi → code đã verify)
  - distill/sft.jsonl    (run_self_learning.py sinh)

Xử lý:
  - Bỏ comment (#...), print(), import thừa, hardcode as_of_date  → giảm ~30-40% token
  - Chỉ giữ code compile được và có gán `ans`
  - Dedupe theo câu hỏi, chia train/val

  python build_sft.py
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
DISTILL = BASE / "distill"

SYSTEM = """Bạn viết code Pandas trả lời câu hỏi dữ liệu.

CÓ SẴN: `dfs` (dict tên_bảng→DataFrame), `get_df_by_keyword(dfs,['Tên'])`, `get_all_dfs_by_keyword(dfs,['Tên'])`,
`parse_date_safe`, `clean_money`, `clean_number`, `normalize_id`, `as_of_date` (Timestamp), `pd`, `np`.

QUY TẮC: chỉ dùng cột trong schema; nếu bảng rỗng thì `ans, ans_type = None, "unanswerable"`;
luôn gán `ans` và `ans_type` (number/percent/string/date/boolean/list); không comment, không print, không đọc file.

Trả về duy nhất một block ```python."""


def load(path):
    out = []
    if Path(path).exists():
        with open(path, "r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return out


def extract_code(text):
    m = re.search(r"```(?:python|py)?\s*\r?\n(.*?)```", text, re.DOTALL)
    return (m.group(1).strip() if m else text.strip())


def strip_comments(code):
    """Xoá comment an toàn (dùng tokenize, không phá '#' trong string) + dòng trống."""
    import io
    import tokenize
    lines = (code or "").splitlines()
    spans = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(code).readline):
            if tok.type == tokenize.COMMENT:
                r, c0 = tok.start
                _, c1 = tok.end
                spans.setdefault(r - 1, []).append((c0, c1))
    except Exception:
        return "\n".join(l for l in lines if l.strip())
    for r, sp in spans.items():
        line = lines[r]
        for c0, c1 in sorted(sp, reverse=True):
            line = line[:c0] + line[c1:]
        lines[r] = line.rstrip()
    return "\n".join(l for l in lines if l.strip())


def clean_code(code):
    out = []
    for line in strip_comments(code).splitlines():
        s = line.strip()
        if re.match(r"^(print\s*\(|import\s+pandas|import\s+numpy|from\s+pandas\b|from\s+numpy\b)", s):
            continue
        if re.match(r"^as_of_date\s*=\s*(pd\.Timestamp|pd\.to_datetime|datetime\.strptime)", s):
            continue
        out.append(line)
    return "\n".join(out).strip()


def to_sample(item):
    """pairs.jsonl -> mẫu chat."""
    user = (f"Câu hỏi: {item['question']}\n"
            f"Ngày chốt (as_of_date): {item.get('as_of_date')}\n\n"
            f"SCHEMA (tên bảng | cột):\n{item.get('schema', '')}\n\n"
            f"README (quy đổi đơn vị):\n{item.get('readme', '')}")
    return {"id": item["id"], "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
        {"role": "assistant", "content": item["code"]},
    ], "meta": {"business_id": item.get("business_id"), "as_of_date": item.get("as_of_date"),
                "answer": item.get("answer"), "gold": item.get("gold"),
                "gold_type": item.get("gold_type"), "source": "gen"}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", default=str(DISTILL / "pairs.jsonl"))
    ap.add_argument("--sft", default=str(DISTILL / "sft.jsonl"))
    ap.add_argument("--val-ratio", type=float, default=0.03)
    args = ap.parse_args()

    raw = []
    for p in load(args.pairs):
        if p.get("code"):
            s = to_sample(p)
            raw.append(s)
    for s in load(args.sft):
        if s.get("messages"):
            raw.append(s)

    seen, kept, reasons = set(), [], Counter()
    before = after = 0

    for s in raw:
        msgs = s.get("messages") or []
        if len(msgs) != 3 or [m.get("role") for m in msgs] != ["system", "user", "assistant"]:
            reasons["sai cấu trúc"] += 1
            continue
        raw_code = extract_code(msgs[2]["content"])
        code = clean_code(raw_code)
        before += len(raw_code)
        after += len(code)
        if "ans" not in code:
            reasons["không gán ans"] += 1
            continue
        try:
            compile(code, "<sft>", "exec")
        except SyntaxError as e:
            reasons[f"syntax: {e.msg[:30]}"] += 1
            continue
        key = s["id"] if s.get("id") else msgs[1]["content"].split("\n")[0]
        if key in seen:
            reasons["trùng"] += 1
            continue
        seen.add(key)
        msgs[2]["content"] = f"```python\n{code}\n```"
        kept.append(s)

    step = max(1, int(1 / args.val_ratio)) if args.val_ratio > 0 else 0
    use_val = bool(step) and len(kept) >= 4 * step
    train, val = [], []
    for i, s in enumerate(kept):
        (val if use_val and i % step == 0 else train).append(s)

    def dump(path, rows):
        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    dump(DISTILL / "train.jsonl", train)
    dump(DISTILL / "val.jsonl", val)

    biz = Counter(s.get("meta", {}).get("business_id", "?") for s in kept)
    print(f"📥 Nguồn    : {len(raw)} mẫu (pairs + sft)")
    print(f"✅ Giữ lại  : {len(kept)}  (train {len(train)} / val {len(val)})")
    print(f"♻️  Bỏ       : {dict(reasons)}")
    print(f"✂️  Comment  : {before} → {after} ký tự code (-{100 - after * 100 // max(before,1)}%)")
    print(f"🏢 Business : {len(biz)} | {dict(biz.most_common(6))}")
    print(f"→ {DISTILL/'train.jsonl'}")


if __name__ == "__main__":
    main()
