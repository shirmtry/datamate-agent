# lấy tất cả bảng bán hàng có chứa dữ liệu tháng 2025
df_sales = get_all_dfs_by_keyword(dfs, ['SoBanHang'])

# nếu không có dữ liệu
if df_sales is None or len(df_sales) == 0:
    ans, ans_type = None, "unanswerable"
else:
    # chuẩn hoá cột ngày giao dịch
    df_sales['Ngày giao dịch'] = parse_date_safe(df_sales['Ngày giao dịch'])

    # lọc chỉ các đơn đặt trong tháng 6/2025 (theo ngày đặt)
    df_june = df_sales[
        (df_sales['Ngày giao dịch'].dt.year == 2025) &
        (df_sales['Ngày giao dịch'].dt.month == 6)
    ]

    # nếu không có đơn nào trong tháng này
    if len(df_june) == 0:
        ans, ans_type = None, "unanswerable"
    else:
        # tổng số đơn (đếm mã hoá đơn duy nhất)
        total_orders = df_june['Mã hóa đơn'].nunique()

        # xác định đơn hủy: trạng thái chứa từ "hủy" (không phân biệt hoa thường)
        cancelled_mask = df_june['Status'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)
        cancelled_orders = df_june.loc[cancelled_mask, 'Mã hóa đơn'].nunique()

        # tính tỉ lệ % (tròn 2 chữ số)
        rate = (cancelled_orders / total_orders) * 100 if total_orders > 0 else 0
        ans = round(rate, 2)
        ans_type = "percent"