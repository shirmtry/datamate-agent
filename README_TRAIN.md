# Dạy model nhỏ (Qwen 1.5B/7B) bằng "thầy" lớn — quy trình đầy đủ

## Ý tưởng

Model 1.5B không thể "hiểu" toàn bộ nghiệp vụ 3000 câu nếu chỉ prompt. Cách hiệu quả:

```
Câu hỏi + schema + README + rulebook
        │
        ▼
  HỌC SINH (qwen2.5-coder 1.5B/7B, Ollama)
        │  code sai
        ▼
  GIÁO VIÊN (gpt-oss-120b / deepseek)  ← có GOLD
        │  reason + fixed_code + new_rule
        ▼
  KIỂM CHỨNG: chạy fixed_code, phải ra đúng gold  ✅ mới lưu
        │
        ├──► distill/learning.jsonl   (code đúng + bài học)
        ├──► distill/rules.md         (nhét lại vào prompt học sinh)
        └──► distill/sft.jsonl        (dataset chat để fine-tune)
                    │
                    ▼
        build_sft.py → train.jsonl / val.jsonl
                    │
                    ▼
        finetune_lora.py (LoRA, GPU) → adapter → merge → GGUF
                    │
                    ▼
        ollama create qwen-coder-ft → học sinh mới
```

Điểm mấu chốt: **dữ liệu train là code đã được kiểm chứng bằng gold**, không phải lời giải thích suông.

## File

| File | Việc |
|---|---|
| `run_self_learning.py` | Sinh dữ liệu: học sinh làm → giáo viên sửa (JSON) → verify → ghi `distill/` |
| `build_sft.py` | Làm sạch, dedupe, chia train/val |
| `finetune_lora.py` | LoRA fine-tune (transformers + peft), có `--dry-run` và `--merge` |
| `utils.py` | `load_biz_data`, `get_df_by_keyword`, `execute_ai_code` (chặn đọc file)… |
| `distill/` | learning.jsonl, sft.jsonl, rules.md, failed.jsonl, logs/ |

## Chạy

```powershell
# 0) Môi trường (máy này đã cài sẵn vào ./vendor)
#    transformers + torch có sẵn; peft/accelerate/openpyxl nằm trong vendor/

# 1) Sinh dữ liệu — chạy theo lô, có resume
python run_self_learning.py --limit 50 --student qwen2.5-coder:1.5b
python run_self_learning.py --limit 200 --student qwen2.5-coder:7b --max-retries 3

# 2) Làm sạch + chia tập
python build_sft.py

# 3) Kiểm tra trước khi train (không cần GPU)
python finetune_lora.py --dry-run

# 4) Train (GPU)
python finetune_lora.py --epochs 3 --bs 2 --grad-accum 8 --max-len 4608

# 5) Gộp adapter + xuất GGUF
python finetune_lora.py --merge
#   python llama.cpp/convert_hf_to_gguf.py lora_out/merged --outfile qwen-coder-ft.gguf
#   ollama create qwen-coder-ft -f Modelfile
```

`Modelfile`:

```
FROM ./qwen-coder-ft.gguf
PARAMETER temperature 0
PARAMETER num_ctx 16384
```

## Chạy tự động hằng ngày (2 key Groq free)

```powershell
# một lần: mở scheduler vòng lặp (không cần quyền admin)
start_daily.cmd

# hoặc chạy tay 1 lượt
python gen_daily.py --max-questions 320 --retry-failed
```

- Quota: 2 key × 200k token/ngày; script tự cân bằng, tự dừng khi hết cả 2.
- Mỗi lượt: gộp 4 câu/lần gọi cùng business, bỏ comment, verify bằng gold, resume.
- Log: `logs_daily/daily_YYYYMMDD_HHMM.log`, trạng thái quota: `distill/daily_state.json`.
- Muốn nhanh hơn: thêm key vào list `KEYS` trong `gen_daily.py` (mỗi key +200k token/ngày).

Năng suất thực tế (đo trên prompt đã rút gọn): **~950 token/câu thử** → 2 key ≈ **380 câu/ngày**
→ tỉ lệ đúng ~40% ⇒ **~150 dòng verified/ngày** ⇒ 3000 dòng ≈ **20 ngày**.
Muốn 5 ngày cần ~8 key free (hoặc nạp DeepSeek ~100 CNY).

## Vì sao phải train trên GPU

Máy này chỉ có `torch 2.x+cpu`. Với Qwen2.5-Coder-1.5B, mỗi bước (seq ~4.5k, LoRA) trên CPU mất hàng phút
→ 3000 mẫu × 3 epoch là **nhiều tuần**. Trên T4 (Colab/Kaggle free) cùng cấu hình: **~25–40 phút/epoch**.

Notebook Colab:

```python
!pip -q install transformers==4.46.3 peft==0.13.2 accelerate==1.1.1 datasets==3.1.0
# upload distill/train.jsonl, distill/val.jsonl, finetune_lora.py
!python finetune_lora.py --epochs 3 --bs 2 --grad-accum 8 --max-len 4608 --out /content/lora_out
# tải lora_out/ về máy
```

## Ngân sách token (quan trọng)

- Groq free: **8.000 token/phút**. Mỗi lần gọi giáo viên ~3–4k token → **~1 câu/phút**.
- 3000 câu, tỉ lệ sai ~70% → ~2000 lần gọi giáo viên → **~30–40 giờ**. Chạy đêm theo lô 200–300 câu.
- Rẻ/nhanh hơn: dùng DeepSeek (`--teacher deepseek`, điền key) hoặc Groq Dev Tier.
- Học sinh tự đúng thì **không** gọi giáo viên → càng về sau càng nhanh (nhờ `distill/rules.md`).

## Mẹo tăng chất lượng dữ liệu

1. `add_rule()` chỉ lưu rule ≥ 15 ký tự và không trùng → `rules.md` là "bộ nhớ" dùng ngay cho câu sau.
2. Code được lưu **đã clean**: bỏ `print()`, bỏ hardcode `as_of_date`, bỏ `read_excel` (bị chặn trong `execute_ai_code`).
3. `max-len 4608`: prompt (schema + README) ~3.7k token + code ~350 token.
4. Mỗi câu sinh 2 biến thể SFT (có rules / không rules) để model không phụ thuộc rules.
5. Câu thất bại nằm ở `distill/failed.jsonl` — chạy lại sau khi rules dày lên.

## Đánh giá

```powershell
# trước fine-tune
python run_train.py --split train --limit 30
# sau fine-tune: trỏ học sinh sang model mới
python run_self_learning.py --student qwen-coder-ft --limit 30 --max-retries 1
```
