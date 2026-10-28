# Tổng doanh thu trong ngày hôm nay (as_of_date = 2025-04-30)

# 1. Lấy bảng hoá đơn (các tháng có thể chứa ngày hôm nay)
df_hd = get_df_by_keyword(dfs, [
    'DanhSachHoaDon_04.2025', 'DanhSachHoaDon_05.2025',
    'DanhSachHoaDon_03.2025', 'DanhSachHoaDon_02.2025',
    'DanhSachHoaDon_01.2025', 'DanhSachHoaDon_04.2026',
    'DanhSachHoaDon_03.2026', 'DanhSachHoaDon_02.2026',
    'DanhSachHoaDon_01.2026'
])

if df_hd is None or len(df_hd) == 0:
    ans, ans_type = None, "unanswerable"
else:
    # 2. Chuẩn hoá ngày đặt (cột 'Thời gian')
    df_hd['Ngày_đặt'] = parse_date_safe(df_hd['Thời gian'])

    # 3. Lọc chỉ các đơn đặt trong ngày as_of_date
    target_date = pd.to_datetime('2025-04-30')
    df_today = df_hd[df_hd['Ngày_đặt'].dt.normalize() == target_date]

    # 4. Loại bỏ đơn hủy và đơn trả hàng
    # - Trạng thái hủy
    df_today = df_today[~df_today['Trạng thái'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)]

    # - Trả hàng: nếu có bất kỳ dòng chi tiết nào có số lượng trả > 0 thì toàn bộ đơn bị loại
    #   Lấy chi tiết hoá đơn
    df_ct = get_df_by_keyword(dfs, ['DanhSachHoaDonChiTiet'])
    if df_ct is not None and len(df_ct) > 0:
        df_ct['Mã hóa đơn'] = normalize_id(df_ct['Mã hóa đơn'])
        # Giả sử cột 'Số lượng trả' không có, dùng thông tin trả hàng từ chi tiết trả (không có trong mô tả)
        # Vì không có cột trả hàng rõ ràng, chỉ dựa vào trạng thái 'Trạng thái' ở bảng hoá đơn.
        # Do đó, ở đây chỉ loại bỏ các đơn có trạng thái chứa 'trả' hoặc 'hoàn trả'
        df_today = df_today[~df_today['Trạng thái'].astype(str).str.lower().str.contains('trả|hoàn trả', na=False)]

    # 5. Tính doanh thu: tổng tiền hàng (cột 'Tổng tiền hàng') sau khi làm sạch tiền
    df_today['Tổng tiền hàng'] = clean_money(df_today['Tổng tiền hàng'])
    total_revenue = df_today['Tổng tiền hàng'].sum()

    ans = int(total_revenue)
    ans_type = "number"