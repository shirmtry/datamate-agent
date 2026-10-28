# BẮT ĐẦU QUÁ TRÌNH DẠY AI

- Tổng: 30 câu

## Câu 1: q_001883280e83 | Ngày: 2026-09-07
- **Hỏi**: tháng này tổng giá trị các phiếu nhập hàng là bao nhiu
- **Gold**: 89526400
- **Code**:
```python
# -*- coding: utf-8 -*-
import pandas as pd

def total_value_of_purchase_orders_this_month(dfs, as_of_date):
    """
    Tính tổng giá trị các phiếu nhập hàng trong tháng của as_of_date.
    - df_nhap:  Bảng DanhSachNhapHang (có cột 'Mã nhập hàng', 'Thời gian')
    - df_ct   : Bảng DanhSachChiTietNhapHang (có cột 'Mã nhập hàng', 'Số lượng', 'Đơn giá')
    """
    # ------------------------------------------------------------------
    # 1. Lấy bảng nhập hàng (header) và chi tiết
    # ------------------------------------------------------------------
    df_nhap = get_df_by_keyword(dfs, ['DanhSachNhapHang'])
    df_ct   = get_df_by_keyword(dfs, ['DanhSachChiTietNhapHang'])

    # ------------------------------------------------------------------
    # 2. Kiểm tra rỗng
    # ------------------------------------------------------------------
    if df_nhap is None or len(df_nhap) == 0:
        ans = None
        return ans
    if df_ct is None or len(df_ct) == 0:
        ans = None
        return ans

    # ------------------------------------------------------------------
    # 3. Chuẩn hoá dữ liệu ngày và tiền
    # ------------------------------------------------------------------
    # ngày nhập
    df_nhap['Thời gian'] = parse_date_safe(df_nhap['Thời gian'])
    # số lượng và đơn giá (có thể là chuỗi có ký tự tiền tệ)
    df_ct['Số lượng'] = clean_money(df_ct['Số lượng'])
    df_ct['Đơn giá']   = clean_money(df_ct['Đơn giá'])

    # ------------------------------------------------------------------
    # 4. Lọc các phiếu nhập trong tháng của as_of_date
    # ------------------------------------------------------------------
    # chuyển as_of_date thành Timestamp
    as_of = pd.to_datetime(as_of_date)
    month_start = as_of.replace(day=1)
    month_end   = (month_start + pd.offsets.MonthEnd(1))

    mask_month = (df_nhap['Thời gian'] >= month_start) & (df_nhap['Thời gian'] <= month_end)
    df_nhap_month = df_nhap.loc[mask_month].copy()

    if len(df_nhap_month) == 0:
        ans = 0.0
        return ans

    # ------------------------------------------------------------------
    # 5. Join chi tiết với header (theo Mã nhập hàng)
    # ------------------------------------------------------------------
    # chuẩn hoá ID để join
    df_nhap_month['Mã nhập hàng_norm'] = normalize_id(df_nhap_month['Mã nhập hàng'])
    df_ct['Mã nhập hàng_norm']       = normalize_id(df_ct['Mã nhập hàng'])

    df_join = pd.merge(
        df_ct,
        df_nhap_month[['Mã nhập hàng_norm']],
        on='Mã nhập hàng_norm',
        how='inner'
    )

    if len(df_join) == 0:
        ans = 0.0
        return ans

    # ------------------------------------------------------------------
    # 6. Tính giá trị từng dòng và tổng
    # ------------------------------------------------------------------
    df_join['Giá trị'] = df_join['Số lượng'] * df_join['Đơn giá']
    total_value = df_join['Giá trị'].sum()

    # ------------------------------------------------------------------
    # 7. Kết quả
    # ------------------------------------------------------------------
    ans = round(total_value, 2)   # làm tròn 2 chữ số thập phân
    return ans
```
- **Trạng thái**: ❌ SAI

## Câu 2: q_00195e1e4049 | Ngày: 2026-05-25
- **Hỏi**: Thuốc có hoạt chất Natri clorid tháng này bán được tổng cộng bao nhiêu tiền?
- **Gold**: 2954200
## Câu 3: q_002d03ebbded | Ngày: 2025-04-30
- **Hỏi**: Tổng doanh thu trong ngày hôm nay là bao nhiêu?
- **Gold**: 10309400
- **Code**:
```python
# -------------------------------------------------
# Tính tổng doanh thu trong ngày hôm nay (as_of_date = 2025-04-30)
# -------------------------------------------------
import pandas as pd

# ngày cần tính
as_of_date = pd.Timestamp('2025-04-30')

# 1. Lấy bảng hoá đơn của tháng 04/2025
df = get_df_by_keyword(dfs, ['DanhSachHoaDon_04.2025'])

# 2. Kiểm tra rỗng
if df is None or len(df) == 0:
    ans = None
else:
    # 3. Chuẩn hoá cột ngày và tiền
    df['Thời gian'] = parse_date_safe(df['Thời gian'])
    df['Tổng tiền hàng'] = clean_money(df['Tổng tiền hàng'])
    df['Giảm giá'] = clean_money(df['Giảm giá'])

    # 4. Lọc các hoá đơn có ngày = as_of_date
    df_today = df[df['Thời gian'].dt.normalize() == as_of_date]

    # 5. Tính doanh thu = Tổng tiền hàng – Giảm giá
    df_today['Doanh thu'] = df_today['Tổng tiền hàng'] - df_today['Giảm giá']

    # 6. Tổng hợp
    ans = df_today['Doanh thu'].sum()
```
- **Trạng thái**: ❌ SAI

## Câu 4: q_00558c1410ef | Ngày: 2026-06-24
- **Hỏi**: tỉ lệ huỷ đơn tháng 6/2025 là nhiêu %
- **Gold**: 2.08
- **Code**:
```python
# Giả sử dfs là dict chứa tất cả các DataFrame đã được load trước đó
# 1. Lấy bảng bán hàng tháng 06/2025
df = get_df_by_keyword(dfs, ['SoBanHang_1_Thang 06 2025'])

# 2. Kiểm tra rỗng
if df is None or len(df) == 0:
    ans = None
else:
    # 3. Xử lý ngày giao dịch
    df['Ngày giao dịch'] = parse_date_safe(df['Ngày giao dịch'])

    # 4. Đếm tổng số đơn (dùng cột "Mã hóa đơn")
    total_orders = df['Mã hóa đơn'].nunique()

    # 5. Đếm số đơn hủy (cột "Status")
    cancelled_mask = df['Status'].astype(str).str.lower().str.contains(r'hủy|huỷ|cancel', na=False)
    cancelled_orders = df.loc[cancelled_mask, 'Mã hóa đơn'].nunique()

    # 6. Tính tỉ lệ hủy (%)
    if total_orders == 0:
        ans = 0.0
    else:
        ans = round(cancelled_orders / total_orders * 100, 2)
```
- **Trạng thái**: ✅ ĐÚNG

## Câu 5: q_006c26c65d50 | Ngày: 2026-07-31
- **Hỏi**: thang 7/2026 co bao nhiu don co dthu tu 55.000 dong tro len
- **Gold**: 2345
- **Code**:
```python
# 1. Lấy bảng chi tiết bán hàng của tháng 07/2026
df = get_df_by_keyword(dfs, ['So_chi_tiet_ban_hang_2026_T07_2026'])

# 2. Kiểm tra bảng rỗng
if df is None or len(df) == 0:
    ans = None
else:
    # 3. Chuyển đổi cột ngày sang kiểu datetime
    df['Ngày'] = parse_date_safe(df['Ngày'])

    # 4. Lọc dữ liệu chỉ trong tháng 7/2026
    df = df[(df['Ngày'] >= '2026-07-01') & (df['Ngày'] <= '2026-07-31')]

    # 5. Làm sạch cột tiền (Thành tiền)
    df['Thành tiền'] = clean_money(df['Thành tiền'])

    # 6. Tính tổng doanh thu mỗi đơn hàng
    order_sum = (
        df.groupby('Mã đơn hàng')['Thành tiền']
          .sum()
          .reset_index()
    )

    # 7. Đếm số đơn hàng có doanh thu >= 55.000 đồng
    ans = (
        order_sum[order_sum['Thành tiền'] >= 55_000]
                ['Mã đơn hàng']
                .nunique()
    )
```
- **Trạng thái**: ❌ SAI

## Câu 6: q_0088f7a0afc5 | Ngày: 2026-07-13
- **Hỏi**: Tháng 7/2025 mặt hàng Otrivin 0,1% xịt mũi chai 10ml bán được tổng cộng bao nhiêu chai?
- **Gold**: 77
- **Code**:
```python
# -*- coding: utf-8 -*-
# Tính tổng số chai Otrivin 0,1% xịt mũi chai 10ml bán được trong tháng 7/2025

# 1. Lấy bảng hoá đơn tháng 7/2025 và bảng chi tiết hoá đơn
df_hd = get_df_by_keyword(dfs, ['DanhSachHoaDon_T07-2025'])
df_ct = get_df_by_keyword(dfs, ['DanhSachHoaDonChiTiet'])

# 2. Kiểm tra rỗng
if df_hd is None or len(df_hd) == 0:
    ans = None
else:
    if df_ct is None or len(df_ct) == 0:
        ans = None
    else:
        # 3. Chuẩn hoá cột ngày và lọc theo tháng 7/2025
        df_hd['Thời gian'] = parse_date_safe(df_hd['Thời gian'])
        df_hd_month = df_hd[
            (df_hd['Thời gian'].dt.year == 2025) &
            (df_hd['Thời gian'].dt.month == 7)
        ]

        # 4. Lọc chi tiết hoá đơn theo tên hàng (không phân biệt hoa thường)
        target_name = 'Otrivin 0,1% xịt mũi chai 10ml'
        df_ct_product = df_ct[
            df_ct['Tên hàng'].astype(str).str.strip().str.lower()
                .eq(target_name.lower())
        ]

        # 5. Kết nối chi tiết với hoá đơn đã lọc (sử dụng mã hoá đơn)
        # Chuẩn hoá mã hoá đơn để tránh sai lệch ký tự
        df_hd_month['Mã hóa đơn_norm'] = normalize_id(df_hd_month['Mã hóa đơn'])
        df_ct_product['Mã hóa đơn_norm'] = normalize_id(df_ct_product['Mã hóa đơn'])

        df_merge = pd.merge(
            df_ct_product,
            df_hd_month[['Mã hóa đơn_norm']],
            on='Mã hóa đơn_norm',
            how='inner'
        )

        # 6. Tổng hợp số lượng (đơn vị: chai)
        total_qty = df_merge['Số lượng'].sum()

        # 7. Kết quả
        ans = int(total_qty) if not pd.isna(total_qty) else 0
```
- **Trạng thái**: ❌ SAI

## Câu 7: q_008f69128180 | Ngày: 2026-05-20
- **Hỏi**: trong thang 10/2025, ti le don huy la bnhiu %
- **Gold**: 1.21
- **Code**:
```python
# 1. Lấy bảng dữ liệu bán hàng tháng 10/2025
df = get_df_by_keyword(dfs, ['SoBanHang_Tháng 10-2025'])

# 2. Kiểm tra dữ liệu rỗng
if df is None or len(df) == 0:
    ans = None
else:
    # 3. Xử lý cột ngày và tiền (theo quy tắc)
    df['Ngày lập'] = parse_date_safe(df['Ngày lập'])
    df['Tiền']      = clean_money(df['Tiền'])

    # 4. Đếm tổng số đơn (độc nhất theo Mã phiếu)
    total_orders = df['Mã phiếu'].nunique()

    # 5. Đếm số đơn hủy: dựa vào nội dung trong cột Ghi chú TT
    cancelled_mask = df['Ghi chú TT']\
        .astype(str)\
        .str.lower()\
        .str.contains(r'hủy|huỷ|cancel', na=False)

    cancelled_orders = df.loc[cancelled_mask, 'Mã phiếu'].nunique()

    # 6. Tính tỷ lệ % (đảm bảo không chia cho 0)
    if total_orders == 0:
        ans = 0.0
    else:
        ans = round(cancelled_orders / total_orders * 100, 2)
```
- **Trạng thái**: ❌ SAI

## Câu 8: q_00a6e23cbacf | Ngày: 2026-08-05
- **Hỏi**: Trong tháng 1/2025, Mì Omachi sườn hầm nhập vào giá bình quân một thùng là bao nhiêu ạ?
- **Gold**: 200556
## Câu 9: q_00bb4edee433 | Ngày: 2026-09-20
- **Hỏi**: trong tổng doanh thu tháng 7/2025, phần của thuốc kê đơn là bao nhiêu phần trăm
- **Gold**: 2.27
## Câu 10: q_00c4e64fe706 | Ngày: 2026-09-14
- **Hỏi**: Tháng 5/2025 cửa hàng bán đc tổng cộng bao nhiêu tiền?
- **Gold**: 271866000
- **Code**:
```python
# 1. Lấy bảng DanhSachHoaDon
df = get_df_by_keyword(dfs, ['DanhSachHoaDon'])

# 2. Kiểm tra rỗng
if df is None or len(df) == 0:
    ans = None
else:
    # 3. Xử lý ngày và tiền
    df['Thời gian'] = parse_date_safe(df['Thời gian'])
    df['Tổng sau giảm giá'] = clean_money(df['Tổng sau giảm giá'])

    # 4. Lọc các hoá đơn thuộc tháng 5/2025
    mask = (df['Thời gian'].dt.year == 2025) & (df['Thời gian'].dt.month == 5)
    df_month = df.loc[mask]

    # 5. Tính tổng tiền bán được trong tháng
    ans = df_month['Tổng sau giảm giá'].sum()
```
- **Trạng thái**: ❌ SAI

## Câu 11: q_00d4d6380d03 | Ngày: 2026-06-21
- **Hỏi**: thang 6/2025 hang nao chay nhat
- **Gold**: Gạch ống 8x8x18 Tuynel
- **Code**:
```python
# Lấy bảng bán_hàng
df = get_df_by_keyword(dfs, ['ban_hang'])

# Kiểm tra rỗng
if df is None or len(df) == 0:
    ans = None
else:
    # Xử lý ngày
    df['Ngày'] = parse_date_safe(df['Ngày'])

    # Lọc dữ liệu tháng 6/2025
    df_june_2025 = df[
        (df['Ngày'].dt.year == 2025) &
        (df['Ngày'].dt.month == 6)
    ]

    # Nếu không có dữ liệu trong tháng 6/2025
    if df_june_2025.empty:
        ans = None
    else:
        # Đảm bảo cột Sluong là số
        df_june_2025['Sluong'] = pd.to_numeric(df_june_2025['Sluong'], errors='coerce').fillna(0)

        # Tổng số lượng bán theo sản phẩm
        prod_qty = df_june_2025.groupby('Sản phẩm', as_index=False)['Sluong'].sum()

        # Sản phẩm có lượng bán cao nhất
        top_product = prod_qty.nlargest(1, 'Sluong')['Sản phẩm'].tolist()

        # Kết quả
        ans = top_product
```
- **Trạng thái**: ❌ SAI

## Câu 12: q_00e9f0bed567 | Ngày: 2026-08-05
- **Hỏi**: dthu các đơn bán qua ddieenj thoại tháng 1/2025 bằng bnhiu % tổng doanh thu tháng 1/2025
- **Gold**: 5.27
- **Code**:
```python
# -*- coding: utf-8 -*-
import pandas as pd

# ------------------------------------------------------------------
# 1. Lấy bảng dữ liệu chính (hóa đơn)
df = get_df_by_keyword(dfs, ['DuLieuBanHang_DanhSachHoaDon'])

# 2. Kiểm tra rỗng
if df is None or len(df) == 0:
    ans = None
else:
    # 3. Xử lý ngày và tiền
    #    - cột ngày: 'Thời gian'
    #    - cột tiền: 'Tổng sau giảm giá' (doanh thu sau giảm)
    df['Thời gian'] = parse_date_safe(df['Thời gian'])
    df['Tổng sau giảm giá'] = clean_money(df['Tổng sau giảm giá'])

    # 4. Lọc dữ liệu tháng 1/2025
    mask_jan2025 = (df['Thời gian'].dt.year == 2025) & (df['Thời gian'].dt.month == 1)
    df_jan = df[mask_jan2025]

    # 5. Kiểm tra nếu không có dữ liệu trong tháng cần tính
    if len(df_jan) == 0:
        ans = None
    else:
        # 6. Tổng doanh thu tháng 1/2025
        total_rev = df_jan['Tổng sau giảm giá'].sum()

        # 7. Doanh thu các đơn bán qua kênh "điện thoại"
        #    - lọc kênh bán chứa từ khóa "điện thoại" hoặc "phone" (không phân biệt hoa thường)
        phone_mask = df_jan['Kênh bán'].astype(str).str.contains(
            r'điện\s*thoại|phone', flags=pd.regex.IGNORECASE, na=False
        )
        phone_rev = df_jan.loc[phone_mask, 'Tổng sau giảm giá'].sum()

        # 8. Tính % (làm tròn 2 chữ số thập phân)
        if total_rev == 0:
            ans = None
        else:
            ans = round(phone_rev / total_rev * 100, 2)
```
- **Lỗi**: Lỗi Runtime: module 'pandas' has no attribute 'regex'

## Câu 13: q_00eadfc5c599 | Ngày: 2026-06-02
- **Hỏi**: đếm số đơn đã huỷ trong tháng 12/2025
- **Gold**: 64
- **Code**:
```python
# Lấy bảng chi tiết đơn hàng
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])

# Kiểm tra bảng có dữ liệu hay không
if df is None or len(df) == 0:
    ans = None
else:
    # Chuyển đổi cột ngày sang kiểu datetime an toàn
    df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])

    # Lọc các đơn hàng trong tháng 12/2025
    df_dec_2025 = df[
        (df['Ngày đặt hàng'].dt.year == 2025) &
        (df['Ngày đặt hàng'].dt.month == 12)
    ]

    # Lọc các đơn hàng có trạng thái là hủy (các từ khóa: hủy, huỷ, cancel)
    df_cancel = df_dec_2025[
        df_dec_2025['Trạng thái đơn hàng']
        .astype(str)
        .str.lower()
        .str.contains('hủy|huỷ|cancel', na=False)
    ]

    # Đếm số đơn hàng hủy duy nhất
    ans = df_cancel['Mã đơn hàng'].nunique()
```
- **Trạng thái**: ✅ ĐÚNG

## Câu 14: q_0139627bccae | Ngày: 2025-10-18
- **Hỏi**: check gium hnay cua hang co bao nhiu don
- **Gold**: 107
- **Code**:
```python
import pandas as pd

# -------------------------------------------------
# Bước 1: Lấy bảng chi tiết đơn hàng
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])

# Bước 2: Kiểm tra rỗng
if df is None or len(df) == 0:
    ans = None
else:
    # Bước 3: Xử lý cột ngày
    df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])

    # Bước 4: Lọc các đơn đặt trong ngày cần kiểm tra
    target_date = pd.Timestamp('2025-10-18')
    df_today = df[df['Ngày đặt hàng'] == target_date]

    # Bước 5: Đếm số đơn hàng duy nhất trong ngày
    ans = df_today['Mã đơn hàng'].nunique()
```
- **Trạng thái**: ❌ SAI

## Câu 15: q_0166f82c0223 | Ngày: 2026-06-02
- **Hỏi**: thang 9/2025 cua hang co bnhiu % don bi huy
- **Gold**: 1.66
- **Code**:
```python
# Lấy bảng chi tiết đơn hàng
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])

# Kiểm tra rỗng
if df is None or len(df) == 0:
    ans = None
else:
    # Xử lý ngày đặt hàng
    df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])
    
    # Lọc dữ liệu tháng 9/2025
    df_month = df[
        (df['Ngày đặt hàng'].dt.year == 2025) &
        (df['Ngày đặt hàng'].dt.month == 9)
    ]
    
    # Tổng số đơn hàng (đếm mã đơn hàng duy nhất)
    total_orders = df_month['Mã đơn hàng'].nunique()
    
    # Đếm số đơn hàng bị hủy
    cancelled_orders = df_month[
        df_month['Trạng thái đơn hàng']
        .astype(str)
        .str.lower()
        .str.contains('hủy|huỷ|cancel', na=False)
    ]['Mã đơn hàng'].nunique()
    
    # Tính % đơn bị hủy (tránh chia cho 0)
    if total_orders == 0:
        ans = 0.0
    else:
        ans = round(cancelled_orders / total_orders * 100, 2)
```
- **Trạng thái**: ✅ ĐÚNG

## Câu 16: q_0174cb13db2a | Ngày: 2026-09-10
- **Hỏi**: tháng này cửa hàng đã chở giao bao nhiêu đợt hàng cho khách nhỉ
- **Gold**: 290
- **Code**:
```python
import pandas as pd

# ------------------------------------------------------------------
# Helper functions (assumed to be provided elsewhere in the environment)
# ------------------------------------------------------------------
# def get_df_by_keyword(dfs, keywords): ...
# def parse_date_safe(series): ...
# def clean_money(series): ...

# ------------------------------------------------------------------
# Input
# ------------------------------------------------------------------
as_of_date = pd.Timestamp('2026-09-10')          # ngày chốt
target_month = as_of_date.to_period('M')         # tháng 2026‑09

# ------------------------------------------------------------------
# 1. Lấy bảng giao hàng
# ------------------------------------------------------------------
df = get_df_by_keyword(dfs, ['Bß║úng k├¬ phiß║┐u giao h├áng'])

# ------------------------------------------------------------------
# 2. Kiểm tra rỗng
# ------------------------------------------------------------------
if df is None or len(df) == 0:
    ans = None
else:
    # ------------------------------------------------------------------
    # 3. Xử lý ngày giao hàng
    # ------------------------------------------------------------------
    df['Ngày giao hàng'] = parse_date_safe(df['Ngày giao hàng'])

    # ------------------------------------------------------------------
    # 4. Lọc dữ liệu trong tháng hiện tại (theo as_of_date)
    # ------------------------------------------------------------------
    df_month = df[df['Ngày giao hàng'].dt.to_period('M') == target_month]

    # ------------------------------------------------------------------
    # 5. Đếm số đợt giao (mỗi “Lần giao” được xem là một đợt)
    # ------------------------------------------------------------------
    # Sử dụng nunique theo quy tắc: không dùng len(df) để đếm.
    ans = df_month['Lần giao'].nunique()
```
- **Trạng thái**: ❌ SAI

## Câu 17: q_0183529f9d61 | Ngày: 2026-05-25
- **Hỏi**: dthu 3 tháng liền nhau kết thúc ở tháng 6/2025 là bao nhiêu mỗi tháng, từ tháng cũ đến tháng mới
- **Gold**: [287435200, 346554700, 309693800]
- **Code**:
```python
import pandas as pd

# 1. Lấy bảng chính (doanh thu dựa trên hoá đơn bán)
df = get_df_by_keyword(dfs, ['BanHang_HoaDon'])

# 2. Kiểm tra rỗng
if df is None or len(df) == 0:
    ans = None
else:
    # 3. Xử lý ngày và tiền
    df['Ngày bán'] = parse_date_safe(df['Ngày bán'])
    df['Tong tien'] = clean_money(df['Tong tien'])

    # 4. Lọc 3 tháng liền nhau kết thúc tháng 6/2025 (từ 01/04/2025 đến 30/06/2025)
    start_date = pd.Timestamp('2025-04-01')
    end_date   = pd.Timestamp('2025-06-30')
    mask = (df['Ngày bán'] >= start_date) & (df['Ngày bán'] <= end_date)
    df_period = df.loc[mask].copy()

    # 5. Nếu không có dữ liệu trong khoảng thời gian này
    if len(df_period) == 0:
        ans = {}
    else:
        # 6. Tạo cột tháng (định dạng YYYY-MM)
        df_period['Month'] = df_period['Ngày bán'].dt.to_period('M').astype(str)

        # 7. Tính tổng doanh thu mỗi tháng
        monthly_rev = (
            df_period
            .groupby('Month', as_index=False)['Tong tien']
            .sum()
            .sort_values('Month')
        )

        # 8. Kết quả trả về dạng dict: {'2025-04': 123456.78, '2025-05': 234567.89, '2025-06': 345678.90}
        ans = dict(zip(monthly_rev['Month'], monthly_rev['Tong tien']))
```
- **Trạng thái**: ❌ SAI

## Câu 18: q_0194d8d10f17 | Ngày: 2026-08-19
- **Hỏi**: Tính đến hết ngày 19/08/2026, có bao nhiêu khách còn nợ cửa hàng?
- **Gold**: 35
- **Code**:
```python
import pandas as pd

# -------------------------------------------------
# Bước 1: Lấy bảng đơn hàng
df = get_df_by_keyword(dfs, ['don_hang'])

# Bước 2: Kiểm tra rỗng
if df is None or len(df) == 0:
    ans = None
else:
    # -------------------------------------------------
    # Bước 3: Xử lý ngày và tiền
    df['NgayBan'] = parse_date_safe(df['NgayBan'])          # ngày bán
    df['Còn lại'] = clean_money(df['Còn lại'])              # số tiền còn nợ

    # -------------------------------------------------
    # Bước 4: Lọc dữ liệu tới thời điểm yêu cầu và còn nợ > 0
    as_of_date = pd.Timestamp('2026-08-19')
    df_valid = df[(df['NgayBan'] <= as_of_date) & (df['Còn lại'] > 0)]

    # -------------------------------------------------
    # Bước 5: Chuẩn hoá mã khách hàng và đếm số khách còn nợ
    df_valid['Số KH'] = normalize_id(df_valid['Số KH'])
    ans = df_valid['Số KH'].nunique()
```
- **Trạng thái**: ❌ SAI

## Câu 19: q_019ec94d9799 | Ngày: 2026-08-19
- **Hỏi**: 3 mặt hàng bán chạy nhất tuần này là những mặt hàng nào?
- **Gold**: ['Cà phê sữa (M)', 'Trà đào cam sả (M)', 'Cà phê đen (M)']
## Câu 20: q_01a252a82858 | Ngày: 2026-06-02
- **Hỏi**: Ngày 14/07/2025 cửa hàng bán Cà phê muối (L) với đơn giá bao nhiêu một ly?
- **Gold**: 41000
- **Code**:
```python
# Lấy bảng chi tiết đơn hàng
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])
if df is None or len(df) == 0:
    ans = None
else:
    # Xử lý ngày và tiền
    df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])
    df['Giá sản phẩm'] = clean_money(df['Giá sản phẩm'])

    # Lọc theo ngày 14/07/2025 và tên sản phẩm "Cà phê muối (L)"
    target_date = pd.Timestamp('2025-07-14')
    mask = (
        (df['Tên sản phẩm'] == 'Cà phê muối (L)') &
        (df['Ngày đặt hàng'] == target_date)
    )
    df_filtered = df[mask]

    # Kiểm tra kết quả
    if df_filtered.empty:
        ans = None
    else:
        # Lấy giá đơn vị (giá sản phẩm) – nếu có nhiều giá khác nhau, trả về danh sách duy nhất
        unique_prices = df_filtered['Giá sản phẩm'].unique()
        ans = unique_prices[0] if len(unique_prices) == 1 else unique_prices.tolist()
```
- **Trạng thái**: ✅ ĐÚNG

## Câu 21: q_01a28f2233bd | Ngày: 2026-07-31
- **Hỏi**: gia ban mot ly soda chanh day (m) vao ngay 01/12/2025 la bn
- **Gold**: 37000
- **Code**:
```python
# Giả sử hàm get_df_by_keyword, parse_date_safe và clean_money đã được định nghĩa sẵn trong môi trường.

def answer_gia_ban_ly_soda_chanh(as_of_date='2026-07-31'):
    # 1. Lấy bảng chi tiết bán hàng tháng 12/2025
    df = get_df_by_keyword(dfs, ['So_chi_tiet_ban_hang_1_T12_2025'])
    
    # 2. Kiểm tra rỗng
    if df is None or len(df) == 0:
        ans = None
        return ans
    
    # 3. Xử lý ngày và tiền
    df['Ngày'] = parse_date_safe(df['Ngày'])
    df['Đơn giá'] = clean_money(df['Đơn giá'])
    
    # 4. Lọc ngày 01/12/2025
    target_date = pd.Timestamp('2025-12-01')
    df = df[df['Ngày'] == target_date]
    
    # 5. Lọc tên hàng hóa: “ly soda chanh” (không phân biệt hoa/thường)
    mask_product = (
        df['Tên hàng hóa'].astype(str).str.lower()
        .str.contains('soda')
        & df['Tên hàng hóa'].astype(str).str.lower()
        .str.contains('chanh')
        & df['Tên hàng hóa'].astype(str).str.lower()
        .str.contains('ly')
    )
    df = df[mask_product]
    
    # 6. Nếu không có dữ liệu trả về None
    if df.empty:
        ans = None
        return ans
    
    # 7. Lấy giá bán (đơn giá) – giả sử giá bán cho 1 ly là cố định,
    #    nên lấy giá đầu tiên (hoặc trung bình nếu có nhiều giá khác nhau)
    ans = df['Đơn giá'].iloc[0]          # hoặc: ans = df['Đơn giá'].mean()
    
    return ans

# Gọi hàm để lấy kết quả
ans = answer_gia_ban_ly_soda_chanh()
```
- **Trạng thái**: ❌ SAI

## Câu 22: q_01a47607f90c | Ngày: 2026-08-11
- **Hỏi**: tổng dthu trong ngày hôm nay là bao nhiêu vaayj
- **Gold**: 39793500
## Câu 23: q_01b914589609 | Ngày: 2025-02-19
- **Hỏi**: Cho tôi biết dthu 30 ngày gần nhất
- **Gold**: 730984600
- **Code**:
```python
import pandas as pd
from datetime import datetime, timedelta

# -------------------------------------------------
# Helper functions are assumed to be available in the environment:
#   get_df_by_keyword(dfs, keywords) -> DataFrame or None
#   parse_date_safe(series)          -> Series of datetime64[ns]
#   clean_money(series)              -> Series of numeric (float)
# -------------------------------------------------

def revenue_last_30_days(dfs, as_of_date_str='2025-02-19'):
    """
    Tính doanh thu (cột Tiền) của 30 ngày gần nhất tính tới as_of_date.
    Kết quả trả về trong biến ans.
    """
    # 1. Chuyển ngày chốt sang datetime
    as_of_date = pd.to_datetime(as_of_date_str)

    # 2. Xác định khoảng ngày cần lấy (30 ngày gần nhất)
    start_date = as_of_date - pd.Timedelta(days=29)   # bao gồm cả as_of_date

    # 3. Lấy các bảng bán hàng có thể chứa dữ liệu trong khoảng này
    #    - Tháng 01-2025
    #    - Tháng 02-2025
    df_jan = get_df_by_keyword(dfs, ['SoBanHang_Tháng 01-2025'])
    df_feb = get_df_by_keyword(dfs, ['SoBanHang_Tháng 02-2025'])

    # 4. Kiểm tra rỗng
    if (df_jan is None or len(df_jan) == 0) and (df_feb is None or len(df_feb) == 0):
        ans = None
        return ans

    # 5. Chuẩn hoá dữ liệu (ngày và tiền) cho từng bảng nếu tồn tại
    frames = []
    for df in [df_jan, df_feb]:
        if df is None or len(df) == 0:
            continue
        # ngày lập
        df['Ngày lập'] = parse_date_safe(df['Ngày lập'])
        # tiền
        df['Tiền'] = clean_money(df['Tiền'])
        frames.append(df)

    # 6. Gộp các bảng lại
    df_all = pd.concat(frames, ignore_index=True)

    # 7. Lọc dữ liệu trong khoảng 30 ngày
    mask = (df_all['Ngày lập'] >= start_date) & (df_all['Ngày lập'] <= as_of_date)
    df_30 = df_all.loc[mask]

    # 8. Nếu không có dữ liệu sau khi lọc
    if df_30 is None or len(df_30) == 0:
        ans = 0.0
        return ans

    # 9. Tính tổng doanh thu
    total_revenue = df_30['Tiền'].sum()

    # 10. Gán kết quả vào ans
    ans = round(total_revenue, 2)
    return ans

# ------------------------------------------------------------------
# Cách dùng (giả sử dfs là dict chứa tất cả DataFrame):
# result = revenue_last_30_days(dfs, as_of_date_str='2025-02-19')
# ------------------------------------------------------------------
```
- **Trạng thái**: ❌ SAI

## Câu 24: q_01bba93199de | Ngày: 2026-08-29
- **Hỏi**: Doanh thu tháng 4/2026 bao nhiêu?
- **Gold**: 1380833500
- **Code**:
```python
# -*- coding: utf-8 -*-
# Answer for: "Doanh thu tháng 4/2026 bao nhiêu?"
# -------------------------------------------------
# 1. Lấy dữ liệu chi tiết bán hàng (có thể có 2 bảng)
df1 = get_df_by_keyword(dfs, ['So_chi_tiet_ban_hang_1'])
df2 = get_df_by_keyword(dfs, ['So_chi_tiet_ban_hang_2'])

# 2. Kiểm tra bảng 1
if df1 is None or len(df1) == 0:
    ans = None
else:
    # 3. Kiểm tra bảng 2
    if df2 is None or len(df2) == 0:
        # chỉ có bảng 1
        df = df1.copy()
    else:
        # gộp 2 bảng lại (cùng cấu trúc)
        df = pd.concat([df1, df2], ignore_index=True)

    # 4. Xử lý ngày
    df['Ngày'] = parse_date_safe(df['Ngày'])

    # 5. Xử lý tiền
    df['Thành tiền'] = clean_money(df['Thành tiền'])

    # 6. Lọc dữ liệu tháng 4/2026
    mask_apr_2026 = (df['Ngày'].dt.year == 2026) & (df['Ngày'].dt.month == 4)
    df_apr = df.loc[mask_apr_2026]

    # 7. Tính tổng doanh thu
    ans = df_apr['Thành tiền'].sum()
```
- **Trạng thái**: ❌ SAI

## Câu 25: q_0266c6b24cbf | Ngày: 2026-09-14
- **Hỏi**: Tháng 5/2026 giá nhập bình quân một hộp Bánh croissant là bao nhiêu vậy?
- **Gold**: 92897
## Câu 26: q_026fa17395ed | Ngày: 2026-05-25
- **Hỏi**: Tính đến hết ngày 25/05/2026, khách hàng còn nợ cửa hàng tổng cộng bao nhiêu tiền?
- **Gold**: 948973
- **Code**:
```python
# -*- coding: utf-8 -*-
import pandas as pd

# -------------------------------------------------
# Helper functions (assumed to be provided in the environment)
# -------------------------------------------------
def parse_date_safe(series):
    """Convert a series to datetime, coercing errors to NaT."""
    return pd.to_datetime(series, errors='coerce')

def clean_money(series):
    """Remove common money formatting and convert to float."""
    # Replace commas, spaces, currency symbols, then cast
    return (
        series.astype(str)
        .str.replace(r'[^\d\.\-]', '', regex=True)   # keep digits, dot, minus
        .replace('', pd.NA)
        .astype(float)
    )

def normalize_id(series):
    """Standardise ID columns for safe joins."""
    return series.astype(str).str.strip().str.upper()

# -------------------------------------------------
# Main calculation
# -------------------------------------------------
def calculate_total_debt(dfs, as_of_date='2026-05-25'):
    """
    Tính tổng số tiền còn nợ của tất cả khách hàng tính đến ngày as_of_date.
    Kết quả được gán vào biến `ans`.
    """
    # 1. Lấy bảng Hoá đơn
    df = get_df_by_keyword(dfs, ['BanHang_HoaDon'])
    
    # 2. Kiểm tra rỗng
    if df is None or len(df) == 0:
        ans = None
        return ans
    
    # 3. Xử lý ngày và tiền
    df['Ngày bán'] = parse_date_safe(df['Ngày bán'])
    df['Còn nợ']   = clean_money(df['Còn nợ'])
    
    # 4. Lọc theo ngày (đến hết ngày as_of_date)
    cutoff = pd.to_datetime(as_of_date)
    df = df[df['Ngày bán'] <= cutoff]
    
    # 5. Loại bỏ các hoá đơn đã hủy (nếu có)
    #   - Kiểm tra cột 'Trạng thái' chứa các từ khóa hủy/huỷ/cancel
    if 'Trạng thái' in df.columns:
        mask_not_cancel = ~df['Trạng thái'].astype(str)\
                               .str.lower()\
                               .str.contains(r'hủy|huỷ|cancel', na=False)
        df = df[mask_not_cancel]
    
    # 6. Tính tổng số tiền còn nợ
    total_debt = df['Còn nợ'].sum()
    
    # 7. Gán kết quả
    ans = total_debt
    return ans

# -------------------------------------------------
# Gọi hàm (ví dụ)
# -------------------------------------------------
# ans = calculate_total_debt(dfs, as_of_date='2026-05-25')
```
- **Trạng thái**: ❌ SAI

## Câu 27: q_026fabde15fc | Ngày: 2026-07-09
- **Hỏi**: Cho hỏi tổng doanh thu quý 2/2026 là bao nhiêu?
- **Gold**: 518445500
- **Code**:
```python
# Tổng doanh thu quý 2/2026 (tháng 04, 05, 06)
def total_revenue_q2_2026(dfs, as_of_date='2026-07-09'):
    # 1. Lấy dữ liệu từng tháng
    df_04 = get_df_by_keyword(dfs, ['DonHang_ChiTiet_04.2026'])
    df_05 = get_df_by_keyword(dfs, ['DonHang_ChiTiet_05.2026'])
    df_06 = get_df_by_keyword(dfs, ['DonHang_ChiTiet_06.2026'])

    # 2. Kiểm tra rỗng
    if (df_04 is None or len(df_04) == 0) and \
       (df_05 is None or len(df_05) == 0) and \
       (df_06 is None or len(df_06) == 0):
        ans = None
        return ans

    # 3. Chuẩn hoá ngày và tiền cho từng bảng (nếu bảng tồn tại)
    def prepare(df):
        if df is None or len(df) == 0:
            return None
        # ngày đặt hàng
        df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])
        # tiền
        df['Tổng tiền'] = clean_money(df['Tổng tiền'])
        # lọc theo ngày <= as_of_date (đảm bảo chỉ lấy dữ liệu tới thời điểm chốt)
        df = df[df['Ngày đặt hàng'] <= pd.to_datetime(as_of_date)]
        return df

    df_04 = prepare(df_04)
    df_05 = prepare(df_05)
    df_06 = prepare(df_06)

    # 4. Gộp ba tháng lại
    frames = [f for f in [df_04, df_05, df_06] if f is not None and len(f) > 0]
    if not frames:
        ans = None
        return ans

    df_q2 = pd.concat(frames, ignore_index=True)

    # 5. Tính tổng doanh thu (cột 'Tổng tiền')
    total_revenue = df_q2['Tổng tiền'].sum()

    # 6. Gán kết quả
    ans = total_revenue
    return ans
```
- **Trạng thái**: ❌ SAI

## Câu 28: q_0271d9f39fde | Ngày: 2026-07-31
- **Hỏi**: tháng 5/2026 cửa hàng có nhiêu % đơn bị huỷ
- **Gold**: 2.19
- **Code**:
```python
# 1. Lấy bảng chi tiết bán hàng tháng 5/2026
df = get_df_by_keyword(dfs, ['So_chi_tiet_ban_hang_1_T05_2026'])

# 2. Kiểm tra rỗng
if df is None or len(df) == 0:
    ans = None
else:
    # 3. Xử lý ngày và tiền (đảm bảo định dạng chuẩn)
    df['Ngày'] = parse_date_safe(df['Ngày'])
    df['Thành tiền'] = clean_money(df['Thành tiền'])

    # 4. Đếm tổng số đơn hàng (unique Mã đơn hàng)
    total_orders = df['Mã đơn hàng'].nunique()

    # 5. Đếm số đơn hàng bị hủy
    cancelled_mask = df['Trạng thái'].astype(str).str.lower().str.contains(
        r'hủy|huỷ|cancel', na=False
    )
    cancelled_orders = df.loc[cancelled_mask, 'Mã đơn hàng'].nunique()

    # 6. Tính % đơn bị hủy (tròn 2 chữ số)
    if total_orders == 0:
        ans = None
    else:
        ans = round(cancelled_orders / total_orders * 100, 2)
```
- **Trạng thái**: ✅ ĐÚNG

## Câu 29: q_0279f675859e | Ngày: 2026-08-19
- **Hỏi**: thang 7/2025, cac khach thuoc nhom than thiet mua tong cong bao nhiu tien hang
- **Gold**: 46871000
- **Code**:
```python
# -*- coding: utf-8 -*-
# Tính tổng tiền mua hàng của khách thuộc nhóm "than thiet" trong tháng 7/2025

# 1. Lấy các bảng cần thiết
df_kh = get_df_by_keyword(dfs, ['khach_hang'])
df_dh = get_df_by_keyword(dfs, ['don_hang'])
df_ct = get_df_by_keyword(dfs, ['chi_tiet_don'])

# 2. Kiểm tra rỗng
if df_kh is None or len(df_kh) == 0:
    ans = None
    return
if df_dh is None or len(df_dh) == 0:
    ans = None
    return
if df_ct is None or len(df_ct) == 0:
    ans = None
    return

# 3. Chuẩn hoá các cột ID
df_kh['ma_kh_norm']   = normalize_id(df_kh['ma_kh'])
df_dh['ma_kh_norm']   = normalize_id(df_dh['Số KH'])
df_dh['ma_dh_norm']   = normalize_id(df_dh['Mã chứng từ'])
df_ct['ma_dh_norm']   = normalize_id(df_ct['Ma don'])

# 4. Lọc khách thuộc nhóm "than thiet" (không phân biệt hoa thường)
df_kh_th = df_kh[df_kh['Nhóm'].astype(str).str.lower().str.contains('than thiet', na=False)]

# 5. Lọc đơn hàng của những khách này
df_dh_th = df_dh.merge(df_kh_th[['ma_kh_norm']], on='ma_kh_norm', how='inner')

# 6. Xử lý ngày bán và lọc tháng 7/2025
df_dh_th['NgayBan'] = parse_date_safe(df_dh_th['NgayBan'])
df_dh_th = df_dh_th[
    (df_dh_th['NgayBan'].dt.year == 2025) &
    (df_dh_th['NgayBan'].dt.month == 7)
]

# 7. Kết nối chi tiết đơn với đơn hàng đã lọc
df_ct_th = df_ct.merge(df_dh_th[['ma_dh_norm']], on='ma_dh_norm', how='inner')

# 8. Làm sạch cột tiền và tính tổng
df_ct_th['T.Tiền'] = clean_money(df_ct_th['T.Tiền'])
total_money = df_ct_th['T.Tiền'].sum()

# 9. Kết quả
ans = total_money
```
- **Trạng thái**: ❌ SAI

## Câu 30: q_0283688e44df | Ngày: 2025-06-20
- **Hỏi**: Cho hỏi tuần trước riêng ca chiều bán được tổng cộng bao nhiêu tiền?
- **Gold**: 109181000
