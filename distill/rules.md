# Bài học rút ra (Dynamic Rulebook)

- Khi câu hỏi liên quan tới "phiếu nhập hàng", luôn dùng bảng DanhSachNhapHang, lọc theo tháng của `as_of_date` (năm và tháng), loại bỏ các dòng có trạng thái chứa 'hủy' hoặc 'huỷ', và tính tổng bằng cách áp dụng `clean_money` lên cột 'Cần trả NCC' trước khi cộng; không đọc file trực tiếp mà dùng `get_df_by_keyword`.
