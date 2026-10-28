Bạn là một Chuyên gia Data Engineer và Kỹ sư AI. Nhiệm vụ của bạn là viết code Python hoàn chỉnh để xây dựng một Pipeline tự động tạo Dataset (dùng để RAG hoặc Fine-tune) cho cuộc thi DataMate.

Dữ liệu đang nằm ở: C:\Users\dinht\Downloads\train\train\
File API Key Mistral của tôi: mstrl_SKXT4AxWWSMJ61wsIaYmbN8nLnpwIzqk_2z7aXE

Hãy tạo cho tôi 2 file sau trong thư mục hiện tại:

### 1. File `utils.py`
Viết các hàm helper cực kỳ mạnh mẽ để xử lý dữ liệu bẩn:
- `load_biz_data(biz_id, data_dir)`: Đọc tất cả file .csv, .xlsx, .sqlite trong thư mục của biz_id. Tự động dò dấu phân cách (comma, tab, semicolon) và encoding (utf-8, cp1258). Trả về dict `dfs`.
- `get_readme(biz_id, data_dir)`: Đọc nội dung file README.md.
- `get_full_schema(dfs)`: Trả về string chứa tên các bảng và danh sách các cột (bỏ qua cột Unnamed).
- `get_df_by_keyword(dfs, keywords)`: Tìm DataFrame trong `dfs` dựa trên từ khóa (không phân biệt hoa thường, xóa khoảng trắng, tự động khớp gần đúng).
- `parse_date_safe(series)`: Chuyển đổi mọi định dạng ngày tháng (bao gồm cả dạng "1 thg 1 2025") sang datetime. Bắt lỗi an toàn.
- `clean_money(series)`: Xóa mọi ký tự không phải số (dấu phẩy, chữ 'đ', 'VNĐ', 'k', 'tr') và chuyển thành float.
- `clean_number(series)`: Tương tự clean_money nhưng dùng cho số lượng.
- `normalize_id(series)`: Chuyển string sang in hoa và xóa khoảng trắng để join bảng.
- `execute_ai_code(code_str, dfs, question, as_of_date)`: Hàm thực thi code do AI sinh ra. Bọc code trong một hàm `__solve__` để cô lập biến. Bắt mọi Exception (Lỗi Runtime) và trả về thông báo lỗi thay vì làm sập chương trình. Tự động thay thế lệnh `pd.read_csv` hoặc `pd.read_excel` (nếu AI lỡ viết) thành `get_df_by_keyword`.

### 2. File `generate_dataset.py`
Viết script chính thực hiện quy trình sau:
- Đọc `questions.jsonl` và `answers.jsonl`.
- Cấu hình gọi API Mistral (dùng model `mistral-large-latest` hoặc `codestral-latest`).
- **Cơ chế Resume**: Kiểm tra file `HUYTKING_learning.jsonl`, nếu câu hỏi đã có trong đó thì bỏ qua, không gọi API lại (tiết kiệm tiền).
- **Batch Processing**: Nhóm 5 câu hỏi của cùng một `business_id` lại với nhau để gửi 1 request duy nhất (giúp giảm 80% chi phí token nhờ Prompt Caching).
- **Prompt gửi cho Mistral**:
  + Cung cấp: Schema, README, Rulebook (cắt bớt 2000 ký tự), và danh sách 5 câu hỏi.
  + Yêu cầu Mistral trả về định dạng JSON chứa code Python cho từng câu.
  + Quy tắc code: Dùng `get_df_by_keyword`, `parse_date_safe`, `clean_money`. Lọc đơn hủy (`hủy|trả`). Không dùng `print()`, gán vào `ans`.
- **Kiểm duyệt tự động**: Với mỗi code nhận về từ Mistral, gọi hàm `execute_ai_code` để chạy thử với dữ liệu local.
- **So sánh đáp án**: Nếu kết quả chạy ra khớp với đáp án trong `answers.jsonl` (sai số cho phép 1e-6), ghi vào file `HUYTKING_learning.jsonl` với format: `{"id": ..., "question": ..., "code": ..., "answer": ...}`.
- Nếu code chạy lỗi hoặc ra sai đáp án, ghi vào file `HUYTKING_failed.jsonl` để tôi kiểm tra sau.
- In ra màn hình tiến độ (đang xử lý câu thứ mấy, đúng hay sai) và tự động nghỉ 2 giây giữa các batch để tránh Rate Limit.

Hãy viết code sạch, có comment rõ ràng, và đảm bảo nó chạy được ngay lập tức. Đừng giải thích dài dòng, hãy tập trung vào code.