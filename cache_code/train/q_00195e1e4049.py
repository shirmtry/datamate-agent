# -*- coding: utf-8 -*-
import pandas as pd

# ------------------------------------------------------------------
# 1. Load required tables
# ------------------------------------------------------------------
df_hoa_don = get_df_by_keyword(dfs, ['BanHang_HoaDon'])
df_chi_tiet = get_df_by_keyword(dfs, ['BanHang_ChiTietHoaDon'])
df_thuoc = get_df_by_keyword(dfs, ['BanHang_Thuoc'])

# ------------------------------------------------------------------
# 2. Kiểm tra dữ liệu tồn tại
# ------------------------------------------------------------------
if any(df is None or len(df) == 0 for df in [df_hoa_don, df_chi_tiet, df_thuoc]):
    ans, ans_type = None, "unanswerable"
else:
    # ------------------------------------------------------------------
    # 3. Chuẩn bị ngày tháng
    # ------------------------------------------------------------------
    df_hoa_don['Ngày bán'] = parse_date_safe(df_hoa_don['Ngày bán'])
    start_month = pd.Timestamp(as_of_date).replace(day=1)
    end_month = pd.Timestamp(as_of_date)

    # ------------------------------------------------------------------
    # 4. Lọc đơn trong tháng hiện tại (từ 1/ tháng tới as_of_date)
    # ------------------------------------------------------------------
    df_hoa_don_month = df_hoa_don[
        (df_hoa_don['Ngày bán'] >= start_month) &
        (df_hoa_don['Ngày bán'] <= end_month)
    ].copy()

    # ------------------------------------------------------------------
    # 5. Loại bỏ đơn hủy
    # ------------------------------------------------------------------
    df_hoa_don_month = df_hoa_don_month[
        ~df_hoa_don_month['Trạng thái']
        .astype(str)
        .str.lower()
        .str.contains('hủy|huỷ|cancel', na=False)
    ]

    # ------------------------------------------------------------------
    # 6. Loại bỏ đơn trả hàng (nếu trạng thái có từ “trả”)
    # ------------------------------------------------------------------
    df_hoa_don_month = df_hoa_don_month[
        ~df_hoa_don_month['Trạng thái']
        .astype(str)
        .str.lower()
        .str.contains('trả|return', na=False)
    ]

    # ------------------------------------------------------------------
    # 7. Chuẩn hoá khóa nối
    #    - Trong chi tiết: cột “Mã giao dịch”
    #    - Trong hoá đơn: cột “Order ID” (đại diện cho mã giao dịch)
    # ------------------------------------------------------------------
    df_chi_tiet['Mã giao dịch'] = normalize_id(df_chi_tiet['Mã giao dịch'])
    df_hoa_don_month['Order ID'] = normalize_id(df_hoa_don_month['Order ID'])

    # ------------------------------------------------------------------
    # 8. Nối chi tiết với hoá đơn đã lọc
    # ------------------------------------------------------------------
    df_detail = df_chi_tiet.merge(
        df_hoa_don_month[['Order ID']],
        left_on='Mã giao dịch',
        right_on='Order ID',
        how='inner'
    )

    # ------------------------------------------------------------------
    # 9. Lọc sản phẩm có hoạt chất “Natri clorid”
    # ------------------------------------------------------------------
    df_thuoc['Hoạt chất'] = df_thuoc['Hoạt chất'].astype(str).str.lower()
    natri_ids_raw = df_thuoc[
        df_thuoc['Hoạt chất'].str.contains('natri clorid', na=False)
    ]['Mã HH'].unique()
    natri_ids = [normalize_id(x) for x in natri_ids_raw]

    df_detail['Ma hang'] = normalize_id(df_detail['Ma hang'])
    df_natri = df_detail[df_detail['Ma hang'].isin(natri_ids)].copy()

    # ------------------------------------------------------------------
    # 10. Tính tổng doanh thu (cột “Thanh tien”)
    # ------------------------------------------------------------------
    df_natri['Thanh tien'] = clean_money(df_natri['Thanh tien'])
    total_money = df_natri['Thanh tien'].sum()

    ans = int(total_money)
    ans_type = "number"