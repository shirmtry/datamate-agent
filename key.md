# DataMate public_test solution key

Dữ liệu public test của repo này được định nghĩa trong `public_test/questions.jsonl` và quy tắc tính toán trong `public_test/rulebook.md`. Repo đã có solver chuẩn theo luật `auto_solver.py` và script chạy hàng loạt `run_all.sh`.

Các bước chuẩn để tạo file nộp bài:

```bash
python3 auto_solver.py --start 0 --end 1000 --questions public_test/questions.jsonl --data public_test/data --out answer.jsonl
```

Hoặc chạy toàn bộ batch:

```bash
bash run_all.sh
```

Lưu ý quan trọng: khi xem trực tiếp trên GitHub, các file dữ liệu public test và bản nộp bài có thể ở dạng Git LFS pointer. Để có dữ liệu thật cần `git lfs pull` hoặc clone repo với Git LFS support trước khi chạy solver.

File nộp bài được yêu cầu là `answer.jsonl` theo định dạng JSONL từng dòng:

```json
{"id": "<question_id>", "type": "number", "answer": 12345}
```

hoặc `abstain` / `unanswerable` nếu không đủ dữ liệu.

Nội dung `answer.jsonl` cần sinh từ `auto_solver.py` chứ không phải sửa thủ công theo ý riêng.
