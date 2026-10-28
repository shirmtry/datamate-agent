# -*- coding: utf-8 -*-
import pandas as pd

# as_of_date is provided by the environment (2026-09-07)
# ----------------------------------------------------
# 1. Load tables
df_nhap = get_df_by_keyword(dfs, ['DanhSachNhapHang'])
df_ct   = get_df_by_keyword(dfs, ['DanhSachChiTietNhapHang'])

# 2. Kiểm tra dữ liệu tồn tại
if df_nhap is None or df_ct is None or len(df_nhap) == 0 or len(df_ct) == 0:
    ans, ans_type = None, "unanswerable"
else:
    # 3. Chuẩn hoá và lọc thời gian (tháng hiện tại)
    df_nhap['Thời gian'] = parse_date_safe(df_nhap['Thời gian'])
    # chỉ giữ các phiếu nhập trong tháng của as_of_date
    cur_year  = as_of_date.year
    cur_month = as_of_date.month
    df_nhap_month = df_nhap[
        (df_nhap['Thời gian'].dt.year == cur_year) &
        (df_nhap['Thời gian'].dt.month == cur_month)
    ]

    # 4. Loại bỏ phiếu nhập bị hủy (nếu có)
    df_nhap_month = df_nhap_month[
        ~df_nhap_month['Trạng thái']
        .astype(str)
        .str.lower()
        .str.contains('hủy|huỷ|cancel', na=False)
    ]

    # 5. Chuẩn hoá mã nhập hàng để join
    df_nhap_month['Mã nhập hàng'] = normalize_id(df_nhap_month['Mã nhập hàng'])
    df_ct['Mã nhập hàng']      = normalize_id(df_ct['Mã nhập hàng'])

    # 6. Lọc chi tiết chỉ thuộc các phiếu nhập đã chọn
    df_ct_month = df_ct[df_ct['Mã nhập hàng'].isin(df_nhap_month['Mã nhập hàng'])].copy()

    # 7. Làm sạch số lượng và đơn giá
    df_ct_month['Số lượng'] = clean_number(df_ct_month['Số lượng'])
    df_ct_month['Đơn giá']  = clean_money(df_ct_month['Đơn giá'])

    # 8. Tính giá trị từng dòng và tổng
    df_ct_month['Giá trị'] = df_ct_month['Số lượng'] * df_ct_month['Đơn giá']
    total_value = df_ct_month['Giá trị'].sum()

    # 9. Kết quả
    ans = int(total_value) if not pd.isna(total_value) else 0
    ans_type = "number"