"""
finetune_lora.py — LoRA fine-tune Qwen2.5-Coder trên dataset distill/train.jsonl.

Máy này KHÔNG có GPU (torch +cpu) nên chạy thật sẽ cực chậm; script chặn CPU trừ khi --allow-cpu.
Khuyến nghị: chạy trên Colab/Kaggle GPU (T4/P100) rồi mang adapter/GGUF về máy.

Ví dụ:
  python finetune_lora.py --dry-run                      # kiểm tra dữ liệu + token, không train
  python finetune_lora.py --epochs 3 --bs 2 --grad-accum 8
  python finetune_lora.py --merge --out lora_out         # gộp adapter vào base để convert GGUF

Sau khi train (trên GPU):
  python finetune_lora.py --merge  ->  lora_out/merged/
  convert:  python llama.cpp/convert_hf_to_gguf.py lora_out/merged --outfile qwen-coder-ft.gguf
  ollama:   ollama create qwen-coder-ft -f Modelfile
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
DISTILL = BASE / "distill"
if (BASE / "vendor").exists():
    sys.path.insert(0, str(BASE / "vendor"))
os.environ.setdefault("HF_HOME", str(BASE / ".hf"))   # cache trong workspace (tránh bị chặn quyền)
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")  # Windows không có quyền tạo symlink
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")


def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="Qwen/Qwen2.5-Coder-1.5B-Instruct")
    ap.add_argument("--train", default=str(DISTILL / "train.jsonl"))
    ap.add_argument("--val", default=str(DISTILL / "val.jsonl"))
    ap.add_argument("--out", default=str(BASE / "lora_out"))
    ap.add_argument("--epochs", type=float, default=3.0)
    ap.add_argument("--bs", type=int, default=1)
    ap.add_argument("--grad-accum", type=int, default=8)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--max-len", type=int, default=4608)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--lora-alpha", type=int, default=32)
    ap.add_argument("--max-steps", type=int, default=-1)
    ap.add_argument("--limit", type=int, default=0, help="Chỉ dùng N mẫu đầu (để test)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-cpu", action="store_true")
    ap.add_argument("--merge", action="store_true")
    args = ap.parse_args()

    import torch
    from transformers import AutoTokenizer

    train_rows = load_jsonl(args.train)
    val_rows = load_jsonl(args.val) if Path(args.val).exists() else []
    if args.limit:
        train_rows = train_rows[: args.limit]
    print(f"📚 train {len(train_rows)} | val {len(val_rows)} mẫu")

    tokenizer = AutoTokenizer.from_pretrained(args.base, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def render(msgs, gen_prompt):
        if getattr(tokenizer, "chat_template", None):
            return tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=gen_prompt)
        # fallback cho tokenizer không có chat template (model test nhỏ)
        body = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in msgs)
        return body + ("\nASSISTANT:" if gen_prompt else "")

    def encode(sample):
        msgs = sample["messages"]
        prompt_text = render(msgs[:-1], True)
        answer_text = msgs[-1]["content"] + tokenizer.eos_token
        p_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
        a_ids = tokenizer(answer_text, add_special_tokens=False)["input_ids"]
        ids = (p_ids + a_ids)[: args.max_len]
        labels = ([-100] * len(p_ids) + a_ids)[: args.max_len]
        return {"input_ids": ids, "labels": labels}

    encoded, dropped = [], 0
    for s in train_rows:
        e = encode(s)
        if all(l == -100 for l in e["labels"]):
            dropped += 1
            continue
        encoded.append(e)
    if not encoded:
        sys.exit(f"❌ Không có mẫu hợp lệ trong {args.train}. Chạy run_self_learning.py trước.")
    lens = [len(e["input_ids"]) for e in encoded]
    print(f"🔤 token: min {min(lens)} / max {max(lens)} / trung bình {sum(lens)/len(lens):.0f}"
          f" | bỏ do quá dài: {dropped}")

    if args.dry_run:
        e = encoded[0]
        print("\n--- MẪU 0 (phần prompt bị mask -100) ---")
        print(tokenizer.decode([t for t in e["input_ids"][:400]]))
        print("\n--- PHẦN HỌC (assistant) ---")
        print(tokenizer.decode([t for t, l in zip(e["input_ids"], e["labels"]) if l != -100]))
        print("\n✅ Dataset OK. Bỏ --dry-run để train.")
        return

    use_cuda = torch.cuda.is_available()
    if not use_cuda and not args.allow_cpu:
        sys.exit(
            "❌ Không thấy GPU CUDA.\n"
            "   - Train Qwen1.5B trên CPU chậm gấp ~50-100 lần (nhiều ngày cho 3000 mẫu).\n"
            "   - Dùng Colab/Kaggle GPU, hoặc chạy lại với --allow-cpu --limit 20 --max-steps 5 để thử.\n")

    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import (AutoModelForCausalLM, Trainer, TrainingArguments,
                              default_data_collator)

    dtype = torch.bfloat16 if (use_cuda and torch.cuda.is_bf16_supported()) else torch.float16
    if not use_cuda:
        dtype = torch.float32
    print(f"🖥️  device={'cuda' if use_cuda else 'cpu'} dtype={dtype}")

    model = AutoModelForCausalLM.from_pretrained(
        args.base, torch_dtype=dtype, device_map=None, trust_remote_code=True)
    model.config.use_cache = False
    if use_cuda:
        model = prepare_model_for_kbit_training(model) if False else model
        model.gradient_checkpointing_enable()

    lora_cfg = LoraConfig(
        r=args.lora_r, lora_alpha=args.lora_alpha, lora_dropout=0.05, bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        task_type="CAUSAL_LM")
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()

    import inspect

    def build(cls, **kw):
        """Chỉ truyền tham số mà phiên bản transformers đang cài hỗ trợ (4.x và 5.x khác nhau)."""
        params = set(inspect.signature(cls.__init__).parameters)
        out = {}
        for k, v in kw.items():
            if k in params:
                out[k] = v
            elif k == "warmup_ratio" and "warmup_steps" in params:
                out["warmup_steps"] = int(v * 500)
            elif k == "eval_strategy" and "evaluation_strategy" in params:
                out["evaluation_strategy"] = v
            elif k == "tokenizer" and "processing_class" in params:
                out["processing_class"] = v
        return out

    ta = build(
        TrainingArguments,
        output_dir=args.out,
        per_device_train_batch_size=args.bs,
        gradient_accumulation_steps=args.grad_accum,
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=5,
        save_steps=200,
        save_total_limit=2,
        eval_strategy="steps" if val_rows else "no",
        eval_steps=200,
        bf16=(dtype == torch.bfloat16),
        fp16=(dtype == torch.float16),
        report_to="none",
        gradient_checkpointing=use_cuda,
        dataloader_num_workers=0,
    )
    args_t = TrainingArguments(**ta)

    def collate(batch):
        pad = tokenizer.pad_token_id
        m = max(len(b["input_ids"]) for b in batch)
        input_ids, labels, attn = [], [], []
        for b in batch:
            n = m - len(b["input_ids"])
            input_ids.append(b["input_ids"] + [pad] * n)
            labels.append(b["labels"] + [-100] * n)
            attn.append([1] * len(b["input_ids"]) + [0] * n)
        return {"input_ids": torch.tensor(input_ids),
                "labels": torch.tensor(labels),
                "attention_mask": torch.tensor(attn)}

    val_enc = [encode(s) for s in val_rows[:50]]
    tr = build(Trainer, model=model, args=args_t, train_dataset=encoded,
               eval_dataset=val_enc or None, data_collator=collate, tokenizer=tokenizer)
    trainer = Trainer(**tr)

    trainer.train()
    trainer.save_model(args.out)
    tokenizer.save_pretrained(args.out)
    print(f"💾 Adapter: {args.out}")

    if args.merge:
        merged_dir = Path(args.out) / "merged"
        merged = model.merge_and_unload()
        merged.save_pretrained(merged_dir, safe_serialization=True)
        tokenizer.save_pretrained(merged_dir)
        print(f"🧩 Đã gộp: {merged_dir}")
        print("   convert_hf_to_gguf.py → GGUF → ollama create")


if __name__ == "__main__":
    main()
