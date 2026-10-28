# DataMate public — 28_20_26

- Model: `openai/gpt-oss-120b`
- Câu: 1000 (từ #0)
- Rulebook: 3026 ký tự

## 1. q_008fdebb6ec9 | dev_002 | as_of 2026-05-24
- **Hỏi**: Tháng 11 năm 2025, nhóm trà có mặt hàng nào bán được nhiều ly nhất?
- **Gold**: (không có) (-)
- **Code** (lần 1):
```python
# -*- coding: utf-8 -*-
import pandas as pd

# assume dfs is provided in the environment
# 1. Load all sales tables for November 2025
df_sales = get_all_dfs_by_keyword(dfs, ['BanHang_T11_2025'])

# 2. Validate data existence
if df_sales is None or len(df_sales) == 0:
    ans, ans_type = None, "unanswerable"
else:
    # 3. Parse dates
    df_sales['Ngày đặt hàng'] = parse_date_safe(df_sales['Ngày đặt hàng'])

    # 4. Filter orders up to as_of_date (2026-05-24) – although all are in 2025, keep rule
    as_of = pd.to_datetime("2026-05-24")
    df_sales = df_sales[df_sales['Ngày đặt hàng'] <= as_of]

    # 5. Exclude cancelled or returned orders
    status_col = df_sales['Trạng thái đơn hàng'].astype(str).str.lower()
    df_sales = df_sales[~status_col.str.contains('hủy|huỷ|cancel|return|trả', na=False)]

    # 6. Keep only products belonging to the "trà" group (name contains 'trà')
    prod_mask = df_sales['Tên sản phẩm'].astype(str).str.contains('trà', case=False, na=False)
    df_trà = df_sales[prod_mask].copy()

    # 7. Clean quantity column
    df_trà['Số lượng sản phẩm'] = clean_number(df_trà['Số lượng sản phẩm'])

    # 8. If there is a conversion table, convert to basic unit
    df_quydoi = get_df_by_keyword(dfs, ['DanhSachQuyDoi'])
    if df_quydoi is not None and not df_quydoi.empty:
        # merge conversion info
        df_quydoi = df_quydoi[['Tên sản phẩm', 'Đơn vị quy đổi', 'Tỉ lệ quy đổi', 'Đơn vị cơ bản']].drop_duplicates()
        df_trà = df_trà.merge(df_quydoi, on='Tên sản phẩm', how='left')
        # where conversion exists, apply it
        has_rate = df_trà['Tỉ lệ quy đổi'].notna()
        df_trà.loc[has_rate, 'Số lượng sản phẩm'] = (
            df_trà.loc[has_rate, 'Số lượng sản phẩm'].astype(float) *
            df_trà.loc[has_rate, 'Tỉ lệ quy đổi'].astype(float)
        )
        # after conversion, treat all as basic unit
        df_trà['Tên sản phẩm'] = df_trà['Tên sản phẩm']  # keep original name for output
    else:
        # no conversion table, just ensure numeric
        df_trà['Số lượng sản phẩm'] = pd.to_numeric(df_trà['Số lượng sản phẩm'], errors='coerce').fillna(0)

    # 9. Aggregate total quantity per product
    agg = (
        df_trà.groupby('Tên sản phẩm', as_index=False)['Số lượng sản phẩm']
        .sum()
        .rename(columns={'Số lượng sản phẩm': 'Tổng_lượng'})
    )

    # 10. Find product with maximum quantity
    if agg.empty:
        ans, ans_type = None, "unanswerable"
    else:
        max_qty = agg['Tổng_lượng'].max()
        top_products = agg[agg['Tổng_lượng'] == max_qty].sort_values('Tên sản phẩm')
        ans = top_products['Tên sản phẩm'].iloc[0]
        ans_type = "string"
```
- **Dự đoán**: string = Trà đào cam sả (M)

## 2. q_009187cd2960 | dev_004 | as_of 2026-06-10
- **Hỏi**: Tháng 5/2026 bán ra bao nhiêu cây Ống PVC Bình Minh D50 cây 4m?
- **Gold**: (không có) (-)
- **Code** (lần 1):
```python
# Lấy toàn bộ bảng bán hàng của năm 2026
df_sales = get_all_dfs_by_keyword(dfs, ['SoBanHang_T'])

# Kiểm tra dữ liệu tồn tại
if df_sales is None or len(df_sales) == 0:
    ans, ans_type = None, "unanswerable"
else:
    # Chuẩn hoá ngày đặt (cột "Thời gian")
    df_sales['Thời gian'] = parse_date_safe(df_sales['Thời gian'])

    # Lọc các đơn không hủy, không trả hàng
    # Giả sử trạng thái hủy hoặc trả hàng chứa các từ khóa 'hủy', 'huỷ', 'cancel', 'trả'
    df_sales = df_sales[~df_sales['Trạng thái xử lý'].astype(str).str.lower()
                        .str.contains('hủy|huỷ|cancel|trả', na=False)]

    # Lọc tháng 5/2026
    df_sales = df_sales[(df_sales['Thời gian'].dt.year == 2026) &
                        (df_sales['Thời gian'].dt.month == 5)]

    # Lọc sản phẩm "Ống PVC Bình Minh D50 cây 4m"
    mask_product = df_sales['Hàng bán'].astype(str).str.contains(
        r'Ống\s*PVC\s*Bình\s*Minh\s*D50\s*cây\s*4m', flags=0, case=False, na=False)
    df_sales = df_sales[mask_product]

    # Chuẩn hoá số lượng bán (cột "SL bán")
    df_sales['SL bán'] = clean_number(df_sales['SL bán'])

    # Tính tổng số cây bán ra
    total_qty = df_sales['SL bán'].astype(float).sum()

    ans = int(total_qty) if not pd.isna(total_qty) else 0
    ans_type = "number"
```
- **Dự đoán**: number = 8

## 3. q_00bf8df3ea0b | dev_002 | as_of 2025-03-04
- **Hỏi**: Rieng ngay hom nay doanh thu quan la bao nhieu?
- **Gold**: (không có) (-)
- **Code** (lần 1):
```python
# -*- coding: utf-8 -*-
# Answer code for question: "Rieng ngay hom nay doanh thu quan la bao nhieu?"
# as_of_date = 2025-03-04

# 1. Load all sales tables
df_sales = get_all_dfs_by_keyword(dfs, ['BanHang'])

# 2. Validate data existence
if df_sales is None or len(df_sales) == 0:
    ans, ans_type = None, "unanswerable"
else:
    # 3. Standardize column names (remove spaces, unify case)
    df_sales = df_sales.rename(columns=lambda x: x.strip().replace(' ', '_'))

    # 4. Parse order date
    df_sales['Ngày_đặt_hàng'] = parse_date_safe(df_sales['Ngày_đặt_hàng'])

    # 5. Filter orders placed on the as_of_date (2025-03-04)
    target_date = pd.Timestamp('2025-03-04')
    df_today = df_sales[df_sales['Ngày_đặt_hàng'] == target_date]

    # 6. Exclude cancelled or returned orders
    #   - Cancelled: status contains 'hủy' or 'cancel' (case‑insensitive)
    #   - Returned: status contains 'trả hàng' or 'return' (any part)
    status_col = df_today['Trạng_thái_đơn_hàng'].astype(str).str.lower()
    mask_not_cancel = ~status_col.str.contains(r'hủy|huỷ|cancel', na=False)
    mask_not_return = ~status_col.str.contains(r'trả hàng|return', na=False)
    df_valid = df_today[mask_not_cancel & mask_not_return]

    # 7. Clean monetary column and compute total revenue
    if len(df_valid) == 0:
        ans, ans_type = 0, "number"
    else:
        df_valid['Tổng_tiền'] = clean_money(df_valid['Tổng_tiền'])
        total_revenue = df_valid['Tổng_tiền'].sum()
        ans = int(total_revenue)
        ans_type = "number"
```
- **Dự đoán**: number = 1692992

## 4. q_00c4e24fa228 | dev_013 | as_of 2026-06-30
- **Hỏi**: Nhóm đồ dùng tháng 6/2026 bán được bao nhiêu tiền?
- **Gold**: (không có) (-)
- **Code** (lần 1):
```python
# -*- coding: utf-8 -*-
import pandas as pd

# -------------------------------------------------
# 1. Load relevant tables
# -------------------------------------------------
# Bảng bán hàng tháng 06/2026
df_sales = get_df_by_keyword(dfs, ['BanHang_2026_T06'])
# Bảng danh mục sản phẩm
df_cat = get_df_by_keyword(dfs, ['QuanLy_DanhMuc'])

# Nếu không có dữ liệu cần thiết
if df_sales is None or len(df_sales) == 0 or df_cat is None or len(df_cat) == 0:
    ans, ans_type = None, "unanswerable"
else:
    # -------------------------------------------------
    # 2. Chuẩn hoá ngày và tiền
    # -------------------------------------------------
    df_sales['Ngày'] = parse_date_safe(df_sales['Ngày'])
    # Lọc chỉ các đơn đặt trong tháng 6/2026 (theo ngày đặt)
    df_sales = df_sales[
        (df_sales['Ngày'].dt.year == 2026) &
        (df_sales['Ngày'].dt.month == 6)
    ]

    # Nếu không có đơn trong tháng 6/2026
    if len(df_sales) == 0:
        ans, ans_type = 0, "number"
    else:
        # Làm sạch cột tiền (cột "TT" là thành tiền của từng dòng)
        df_sales['TT_clean'] = clean_money(df_sales['TT'])

        # -------------------------------------------------
        # 3. Gộp với danh mục để lấy nhóm sản phẩm
        # -------------------------------------------------
        # Chuẩn hoá tên hàng để join
        df_sales['Tên hàng_norm'] = normalize_id(df_sales['Tên hàng'])
        df_cat['Tên hàng_norm'] = normalize_id(df_cat['Tên hàng'])

        df_merged = pd.merge(
            df_sales,
            df_cat[['Tên hàng_norm', 'Nhóm']],
            on='Tên hàng_norm',
            how='left'
        )

        # Lọc nhóm "đồ dùng" (không phân biệt chữ hoa/thường, bỏ dấu)
        # Đơn giản: kiểm tra chứa từ "đồ dùng"
        df_merged['Nhóm_norm'] = df_merged['Nhóm'].astype(str).str.lower()
        mask_group = df_merged['Nhóm_norm'].str.contains('đồ dùng')
        df_group = df_merged[mask_group]

        # -------------------------------------------------
        # 4. Áp dụng luật doanh thu: chỉ tính đơn không hủy, không trả hàng
        # -------------------------------------------------
        # Giả sử có cột trạng thái (không có trong mô tả), nên loại bỏ nếu có từ khóa hủy/huỷ/trả
        if 'Trạng thái' in df_group.columns:
            df_group = df_group[
                ~df_group['Trạng thái'].astype(str).str.lower().str.contains(
                    r'hủy|huỷ|cancel|trả|return', na=False)
            ]

        # Tổng doanh thu cho nhóm đồ dùng trong tháng 6/2026
        total_revenue = df_group['TT_clean'].sum()

        ans = int(total_revenue)
        ans_type = "number"
```
- **Dự đoán**: number = 1784

## 5. q_013b4ff35811 | dev_004 | as_of 2025-11-16
- **Hỏi**: Cho tôi biết doanh thu tuần này.
- **Gold**: (không có) (-)
- **Code** (lần 1):
```python
# -*- coding: utf-8 -*-
# Tính doanh thu tuần hiện tại (từ Thứ Hai đến Chủ Nhật) tính đến as_of_date = 2025-11-16

# 1. Lấy toàn bộ bảng bán hàng (các tháng, các năm)
df_sales = get_all_dfs_by_keyword(dfs, ['SoBanHang_T'])

# Kiểm tra dữ liệu tồn tại
if df_sales is None or len(df_sales) == 0:
    ans, ans_type = None, "unanswerable"
else:
    # 2. Chuẩn hoá cột ngày giờ
    df_sales['Thời gian'] = parse_date_safe(df_sales['Thời gian'])

    # 3. Lọc các đơn chỉ tính trong khoảng thời gian tới as_of_date
    as_of = pd.to_datetime("2025-11-16")
    df_sales = df_sales[df_sales['Thời gian'].dt.date <= as_of.date()]

    # 4. Xác định tuần hiện tại (từ Thứ Hai)
    #   - Tìm ngày Thứ Hai của tuần chứa as_of_date
    week_start = as_of - pd.Timedelta(days=(as_of.weekday()))  # Monday
    week_end   = week_start + pd.Timedelta(days=6)               # Sunday

    # 5. Lọc dữ liệu trong tuần
    df_week = df_sales[(df_sales['Thời gian'] >= week_start) &
                       (df_sales['Thời gian'] <= week_end)]

    # 6. Loại bỏ đơn hủy và trả hàng
    #    - Trạng thái xử lý chứa các từ khóa hủy/huy hoặc trả (trả hàng, trả một phần)
    status_col = df_week['Trạng thái xử lý'].astype(str).str.lower()
    mask_not_cancel = ~status_col.str.contains('hủy|huỷ|cancel', na=False)
    mask_not_return = ~status_col.str.contains('trả|return', na=False)
    df_valid = df_week[mask_not_cancel & mask_not_return]

    # 7. Làm sạch cột Amount (tiền) và tính tổng doanh thu
    df_valid['Amount'] = clean_money(df_valid['Amount'])
    total_revenue = df_valid['Amount'].sum()

    # 8. Gán kết quả
    ans = int(total_revenue) if not pd.isna(total_revenue) else 0
    ans_type = "number"
```
- **Dự đoán**: number = 10628063

## 6. q_014cdcc1da6e | dev_007 | as_of 2026-09-19
- **Hỏi**: 8/26 tiền bán ca chiều là bnhiu?
- **Gold**: (không có) (-)
- **Code** (lần 1):
```python
# -*- coding: utf-8 -*-
# Answer code for question: "8/26 tiền bán ca chiều là bnhiu?"
# Required output variables: ans, ans_type

# 1. Load the relevant table
df = get_df_by_keyword(dfs, ['chi_tiet_hoa_don'])

# 2. Validate data existence
if df is None or len(df) == 0:
    ans, ans_type = None, "unanswerable"
else:
    # 3. Prepare date column
    df['Ngày giao dịch'] = parse_date_safe(df['Ngày giao dịch'])

    # 4. Filter to the target day (8/26) – use as_of_date year (2026)
    target_date = pd.Timestamp('2026-08-26')
    df_day = df[df['Ngày giao dịch'].dt.normalize() == target_date]

    # 5. Keep only afternoon shift (ca chiều)
    # Giờ bán may contain strings like "14:30", "15h", or "chiều"
    df_day = df_day[
        df_day['Giờ bán'].astype(str).str.lower().str.contains('chiều')
    ]

    # 6. Exclude cancelled or returned orders
    # Trạng thái HĐĐT column holds order status
    status_col = df_day['Trạng thái HĐĐT'].astype(str).str.lower()
    df_day = df_day[
        ~status_col.str.contains('hủy|huỷ|cancel|trả|return', na=False)
    ]

    # 7. Clean monetary column and compute total sales
    df_day['Thành tiền_clean'] = clean_money(df_day['Thành tiền'])
    total_sales = df_day['Thành tiền_clean'].sum()

    # 8. Set answer
    ans = int(total_sales) if not pd.isna(total_sales) else 0
    ans_type = "number"
```
- **Dự đoán**: number = 0

## 7. q_01ac0fc9f2a2 | dev_003 | as_of 2026-08-18
- **Hỏi**: Tuần rồi trung bình mổi đơn quán bán được nhiêu tiền vậy?
- **Gold**: (không có) (-)
- **Code** (lần 1):
```python
# -*- coding: utf-8 -*-
import pandas as pd

# -------------------------------------------------
# 1. Lấy dữ liệu đơn hàng (các bảng có thể chứa đơn)
# -------------------------------------------------
df_orders = get_all_dfs_by_keyword(dfs, ['BanHang_TongHop_2026'])
if df_orders is None or len(df_orders) == 0:
    ans, ans_type = None, "unanswerable"
else:
    # -------------------------------------------------
    # 2. Chuẩn hoá ngày đặt và lọc theo tuần trước
    # -------------------------------------------------
    df_orders['Ngày HĐ'] = parse_date_safe(df_orders['Ngày HĐ'])
    # ngày hiện tại (as_of_date) được truyền trong biến as_of_date
    cur_date = pd.to_datetime(as_of_date)

    # tuần hiện tại bắt đầu từ Thứ Hai
    cur_monday = cur_date - pd.Timedelta(days=cur_date.weekday())
    # tuần trước: từ Monday trước đó đến Sunday trước đó
    prev_monday = cur_monday - pd.Timedelta(days=7)
    prev_sunday = cur_monday - pd.Timedelta(days=1)

    mask_week = (df_orders['Ngày HĐ'] >= prev_monday) & (df_orders['Ngày HĐ'] <= prev_sunday)
    df_week = df_orders.loc[mask_week].copy()

    # -------------------------------------------------
    # 3. Loại bỏ đơn hủy và trả hàng
    # -------------------------------------------------
    # trạng thái hủy / trả hàng thường có từ khóa 'hủy', 'huỷ', 'cancel', 'return'
    status_col = df_week['Trạng thái giao'].astype(str).str.lower()
    df_week = df_week[~status_col.str.contains(r'hủy|huỷ|cancel|return', na=False)]

    # -------------------------------------------------
    # 4. Tính doanh thu của mỗi đơn (không tính phí ship, giảm tổng đơn, thuế)
    # -------------------------------------------------
    # cột "Thành tiền (đ)" là doanh thu của từng dòng hàng
    df_week['Thành tiền (đ)'] = clean_money(df_week['Thành tiền (đ)'])

    # tổng doanh thu mỗi đơn
    revenue_per_order = (
        df_week.groupby('Đơn số')['Thành tiền (đ)']
        .sum()
        .reset_index(name='doanh_thu')
    )

    # -------------------------------------------------
    # 5. Tính trung bình doanh thu mỗi đơn
    # -------------------------------------------------
    total_rev = revenue_per_order['doanh_thu'].sum()
    num_orders = revenue_per_order['Đơn số'].nunique()

    if num_orders == 0:
        ans, ans_type = None, "unanswerable"
    else:
        avg_rev = total_rev / num_orders
        ans = round(avg_rev, 2)          # giữ 2 chữ số thập phân
        ans_type = "number"
```
- **Dự đoán**: number = 71266.49

## 8. q_01ba91ff94c6 | dev_008 | as_of 2025-11-10
- **Hỏi**: Tuần rồi 5 món bán chạy nhất là những món nàoo?
- **Gold**: (không có) (-)
- **Code** (lần 1):
```python
# -*- coding: utf-8 -*-
# Code for: "Tuần rồi 5 món bán chạy nhất là những món nàoo?"
# Required output: ans (list of product names), ans_type = "list"

# 1. Load and merge detail tables
df1 = get_df_by_keyword(dfs, ['ChiTietHoaDon_1'])
df2 = get_df_by_keyword(dfs, ['ChiTietHoaDon_2'])
if df1 is None and df2 is None:
    ans, ans_type = None, "unanswerable"
else:
    # concatenate available parts
    dfs_list = [d for d in (df1, df2) if d is not None and len(d) > 0]
    df = dfs_list[0] if len(dfs_list) == 1 else dfs_list[0].append(dfs_list[1], ignore_index=True)

    # 2. Clean and prepare columns
    # ngày đặt
    df['Ngày xuất'] = parse_date_safe(df['Ngày xuất'])

    # lọc chỉ các đơn không hủy, không trả hàng
    status_col = df['Trạng thái HĐĐT'].astype(str).str.lower()
    not_cancel = ~status_col.str.contains('hủy|huỷ|cancel|huy|đã hủy|đã huỷ', na=False)
    not_return = ~status_col.str.contains('trả|hoàn|đổi', na=False)   # giả định các từ trả hàng
    df = df[not_cancel & not_return]

    # 3. Xác định khoảng thời gian "tuần rồi"
    # as_of_date = 2025-11-10 (được truyền trong môi trường)
    as_of = pd.to_datetime("2025-11-10")
    # tuần trước: từ thứ Hai trước đó đến Chủ Nhật trước
    start_week = (as_of - pd.Timedelta(days=7)).normalize()  # 2025-11-03 00:00
    end_week = (as_of - pd.Timedelta(days=1)).normalize() + pd.Timedelta(hours=23, minutes=59, seconds=59)  # 2025-11-09 23:59:59
    df = df[(df['Ngày xuất'] >= start_week) & (df['Ngày xuất'] <= end_week)]

    # 4. Lượng bán (số lượng)
    # cột số lượng: dùng 'SLg' nếu có, nếu không fallback 'SL lẻ'
    qty_col = None
    for col in ['SLg', 'SL lẻ', 'Số lượng', 'SL']:
        if col in df.columns:
            qty_col = col
            break
    if qty_col is None:
        ans, ans_type = None, "unanswerable"
    else:
        df['Quantity'] = clean_number(df[qty_col])

        # 5. Tính tổng lượng theo tên hàng
        if 'Tên hàng' not in df.columns:
            ans, ans_type = None, "unanswerable"
        else:
            top5 = (
                df.groupby('Tên hàng')['Quantity']
                .sum()
                .reset_index()
                .sort_values(by=['Quantity', 'Tên hàng'], ascending=[False, True])
                .head(5)
            )
            ans = top5['Tên hàng'].tolist()
            ans_type = "list"
```
- **Runtime lỗi**: Lỗi Runtime: 'DataFrame' object has no attribute 'append'
