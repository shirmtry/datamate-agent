# BẮT ĐẦU QUÁ TRÌNH DẠY AI

- Thời gian: 2026-10-28 18:52:23
- Tổng số câu: 50

## Câu 1: q_001883280e83 | Ngày: 2026-09-07
- **Hỏi**: tháng này tổng giá trị các phiếu nhập hàng là bao nhiu
- **Gold**: 89526400
## Câu 2: q_00195e1e4049 | Ngày: 2026-05-25
- **Hỏi**: Thuốc có hoạt chất Natri clorid tháng này bán được tổng cộng bao nhiêu tiền?
- **Gold**: 2954200
## Câu 3: q_002d03ebbded | Ngày: 2025-04-30
- **Hỏi**: Tổng doanh thu trong ngày hôm nay là bao nhiêu?
- **Gold**: 10309400
- **Code**:
```python
import pandas as pd

# Lấy bảng hóa đơn tháng 04.2025 (ngày chốt 2025-04-30)
df = get_df_by_keyword(dfs, ['DanhSachHoaDon_04.2025'])

if df is None:
    ans = None
else:
    # Tìm cột ngày và cột tổng tiền
    date_col = None
    for c in df.columns:
        cl = c.lower()
        if 'ngay' in cl and ('lap' in cl or 'hd' in cl or 'hoa' in cl or 'ban' in cl):
            date_col = c
            break
    if date_col is None:
        for c in df.columns:
            if 'ngay' in c.lower():
                date_col = c
                break

    money_col = None
    for c in df.columns:
        cl = c.lower()
        if ('tong' in cl and ('tien' in cl or 'cong' in cl)) or 'thanhtien' in cl or 'tongtien' in cl:
            money_col = c
            break

    if date_col is None or money_col is None:
        ans = None
    else:
        df = df.copy()
        df[date_col] = parse_date_safe(df[date_col])
        df[money_col] = clean_money(df[money_col])
        target = pd.Timestamp('2025-04-30')
        mask = df[date_col].dt.normalize() == target
        ans = df.loc[mask, money_col].sum()
```
- **Trạng thái**: ❌ SAI (None != 10309400)

## Câu 4: q_00558c1410ef | Ngày: 2026-06-24
- **Hỏi**: tỉ lệ huỷ đơn tháng 6/2025 là nhiêu %
- **Gold**: 2.08
- **Code**:
```python
import pandas as pd
import numpy as np

# Lấy bảng bán hàng tháng 6/2025
df = get_df_by_keyword(dfs, ['SoBanHang_1_Thang 06 2025'])

if df is None:
    ans = None
else:
    # Tìm cột trạng thái đơn (hủy/hoàn)
    status_col = None
    for c in df.columns:
        cl = str(c).lower()
        if 'trang' in cl and 'thai' in cl:
            status_col = c
            break
        if 'status' in cl or 'tinh trang' in cl or 'tinhtrang' in cl:
            status_col = c
            break
    
    if status_col is None:
        ans = None
    else:
        total = len(df)
        if total == 0:
            ans = 0.0
        else:
            s = df[status_col].astype(str).str.lower().str.strip()
            cancel_mask = s.str.contains('huy|hủy|cancel|hoan|hoàn|return|tra hang|trả hàng', na=False)
            cancel_count = cancel_mask.sum()
            ans = round(cancel_count / total * 100, 2)
```
- **Trạng thái**: ❌ SAI (2.41 != 2.08)

## Câu 5: q_006c26c65d50 | Ngày: 2026-07-31
- **Hỏi**: thang 7/2026 co bao nhiu don co dthu tu 55.000 dong tro len
- **Gold**: 2345
- **Code**:
```python
import pandas as pd

# Chọn bảng tháng 7/2026
df = get_df_by_keyword(dfs, ['So_chi_tiet_ban_hang_2026_T07_2026'])

if df is None:
    ans = None
else:
    # Tìm cột ngày và cột doanh thu
    date_col = None
    for c in df.columns:
        cl = c.lower()
        if 'ngay' in cl or 'date' in cl:
            date_col = c
            break
    
    money_col = None
    for c in df.columns:
        cl = c.lower()
        if 'tien' in cl or 'dthu' in cl or 'doanh' in cl or 'thanh' in cl or 'amount' in cl or 'total' in cl:
            money_col = c
            break
    
    if date_col is None or money_col is None:
        ans = None
    else:
        df['_date'] = parse_date_safe(df[date_col])
        df['_money'] = clean_money(df[money_col])
        
        # Lọc tháng 7/2026
        mask = (df['_date'].dt.year == 2026) & (df['_date'].dt.month == 7)
        df_jul = df[mask]
        
        # Tìm cột mã đơn
        order_col = None
        for c in df.columns:
            cl = c.lower()
            if 'don' in cl or 'order' in cl or 'so_ct' in cl or 'chung_tu' in cl:
                order_col = c
                break
        
        if order_col is None:
            ans = None
        else:
            # Tính doanh thu theo đơn
            grouped = df_jul.groupby(order_col)['_money'].sum()
            ans = int((grouped >= 55000).sum())
```
- **Trạng thái**: ❌ SAI (None != 2345)

## Câu 6: q_0088f7a0afc5 | Ngày: 2026-07-13
- **Hỏi**: Tháng 7/2025 mặt hàng Otrivin 0,1% xịt mũi chai 10ml bán được tổng cộng bao nhiêu chai?
- **Gold**: 77
## Câu 7: q_008f69128180 | Ngày: 2026-05-20
- **Hỏi**: trong thang 10/2025, ti le don huy la bnhiu %
- **Gold**: 1.21
- **Code**:
```python
import pandas as pd

# Lấy bảng bán hàng tháng 10/2025
df = get_df_by_keyword(dfs, ['SoBanHang_Tháng 10-2025'])

if df is None:
    ans = None
else:
    # Tìm cột trạng thái đơn (chứa thông tin hủy)
    status_col = None
    for c in df.columns:
        cl = c.lower()
        if 'trang' in cl or 'status' in cl or 'tinh_trang' in cl or 'tình trạng' in cl:
            status_col = c
            break
    
    if status_col is None:
        ans = None
    else:
        total = len(df)
        if total == 0:
            ans = 0.0
        else:
            s = df[status_col].astype(str).str.lower().str.strip()
            cancelled = s.str.contains('huy|hủy|cancel', regex=True, na=False).sum()
            ans = round(cancelled / total * 100, 2)
```
- **Trạng thái**: ❌ SAI (None != 1.21)

## Câu 8: q_00a6e23cbacf | Ngày: 2026-08-05
- **Hỏi**: Trong tháng 1/2025, Mì Omachi sườn hầm nhập vào giá bình quân một thùng là bao nhiêu ạ?
- **Gold**: 200556
## Câu 9: q_00bb4edee433 | Ngày: 2026-09-20
- **Hỏi**: trong tổng doanh thu tháng 7/2025, phần của thuốc kê đơn là bao nhiêu phần trăm
- **Gold**: 2.27
- **Code**:
```python
import pandas as pd

# Lấy bảng chi tiết đơn hàng
df_ct = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])
# Lấy bảng danh sách thuốc để biết thuốc kê đơn
df_thuoc = get_df_by_keyword(dfs, ['DuLieuXuat_DanhSachThuoc'])

if df_ct is None or df_thuoc is None:
    ans = None
else:
    df_ct = df_ct.copy()
    df_thuoc = df_thuoc.copy()

    # Chuẩn hóa ngày
    df_ct['NgayBan'] = parse_date_safe(df_ct['NgayBan'])

    # Lọc tháng 7/2025
    mask = (df_ct['NgayBan'].dt.year == 2025) & (df_ct['NgayBan'].dt.month == 7)
    df_jul = df_ct[mask].copy()

    # Chuẩn hóa tiền
    df_jul['ThanhTien'] = clean_money(df_jul['ThanhTien'])

    # Chuẩn hóa id để join
    df_jul['MaThuoc'] = normalize_id(df_jul['MaThuoc'])
    df_thuoc['MaThuoc'] = normalize_id(df_thuoc['MaThuoc'])

    # Xác định cột thuốc kê đơn
    col_ke_don = None
    for c in df_thuoc.columns:
        if 'kedon' in c.lower().replace('_', '').replace(' ', '') or 'kê đơn' in c.lower():
            col_ke_don = c
            break

    if col_ke_don is None:
        ans = None
    else:
        df_merge = df_jul.merge(
            df_thuoc[['MaThuoc', col_ke_don]],
            on='MaThuoc',
            how='left'
        )

        tong = df_merge['ThanhTien'].sum()
        if tong == 0 or pd.isna(tong):
            ans = None
        else:
            ke_don = df_merge[df_merge[col_ke_don].astype(str).str.lower().isin(['1', 'true', 'yes', 'có', 'co', 'x'])]
            ans = ke_don['ThanhTien'].sum() / tong * 100
```
- **Lỗi**: Lỗi Runtime: 'NgayBan'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 10: q_00c4e64fe706 | Ngày: 2026-09-14
- **Hỏi**: Tháng 5/2025 cửa hàng bán đc tổng cộng bao nhiêu tiền?
- **Gold**: 271866000
- **Code**:
```python
# Tìm bảng hóa đơn
df_hoadon = get_df_by_keyword(dfs, ['DanhSachHoaDon'])

if df_hoadon is None:
    ans = None
else:
    # Tìm cột ngày và cột tổng tiền
    date_col = None
    for c in df_hoadon.columns:
        if 'ngay' in c.lower():
            date_col = c
            break
    
    money_col = None
    for c in df_hoadon.columns:
        cl = c.lower()
        if ('tong' in cl and 'tien' in cl) or 'thanhtien' in cl or 'sotien' in cl:
            money_col = c
            break
    
    if date_col is None or money_col is None:
        ans = None
    else:
        df = df_hoadon.copy()
        df[date_col] = parse_date_safe(df[date_col])
        df[money_col] = clean_money(df[money_col])
        
        mask = (df[date_col].dt.year == 2025) & (df[date_col].dt.month == 5)
        ans = df.loc[mask, money_col].sum()
```
- **Trạng thái**: ❌ SAI (None != 271866000)

## Câu 11: q_00d4d6380d03 | Ngày: 2026-06-21
- **Hỏi**: thang 6/2025 hang nao chay nhat
- **Gold**: Gạch ống 8x8x18 Tuynel
## Câu 12: q_00e9f0bed567 | Ngày: 2026-08-05
- **Hỏi**: dthu các đơn bán qua ddieenj thoại tháng 1/2025 bằng bnhiu % tổng doanh thu tháng 1/2025
- **Gold**: 5.27
## Câu 13: q_00eadfc5c599 | Ngày: 2026-06-02
- **Hỏi**: đếm số đơn đã huỷ trong tháng 12/2025
- **Gold**: 64
- **Code**:
```python
import pandas as pd

# Chọn bảng phù hợp nhất
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])

if df is None:
    ans = None
else:
    # Tìm cột ngày và cột trạng thái
    date_col = None
    status_col = None
    for c in df.columns:
        cl = c.lower()
        if date_col is None and ('ngay' in cl or 'date' in cl or 'thoi_gian' in cl or 'time' in cl):
            date_col = c
        if status_col is None and ('trang_thai' in cl or 'status' in cl or 'tinh_trang' in cl):
            status_col = c
    
    if date_col is None or status_col is None:
        ans = None
    else:
        df = df.copy()
        df['_date'] = parse_date_safe(df[date_col])
        mask_month = (df['_date'].dt.year == 2025) & (df['_date'].dt.month == 12)
        mask_cancel = df[status_col].astype(str).str.lower().str.contains('huy|cancel|huỷ', na=False)
        ans = int((mask_month & mask_cancel).sum())
```
- **Trạng thái**: ❌ SAI (None != 64)

## Câu 14: q_0139627bccae | Ngày: 2025-10-18
- **Hỏi**: check gium hnay cua hang co bao nhiu don
- **Gold**: 107
- **Code**:
```python
import pandas as pd

# Lấy bảng phù hợp nhất
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])

if df is None:
    ans = None
else:
    # Tìm cột ngày
    date_col = None
    for c in df.columns:
        if 'ngay' in c.lower() or 'date' in c.lower():
            date_col = c
            break
    
    if date_col is None:
        ans = None
    else:
        df['_date'] = parse_date_safe(df[date_col])
        target = pd.Timestamp('2025-10-18')
        filtered = df[df['_date'].dt.normalize() == target]
        
        # Đếm số đơn (unique mã đơn nếu có, ngược lại đếm dòng)
        order_col = None
        for c in df.columns:
            if 'don' in c.lower() and ('ma' in c.lower() or 'id' in c.lower() or 'so' in c.lower()):
                order_col = c
                break
        
        if order_col is not None:
            ans = normalize_id(filtered[order_col]).nunique()
        else:
            ans = len(filtered)
```
- **Trạng thái**: ❌ SAI (None != 107)

## Câu 15: q_0166f82c0223 | Ngày: 2026-06-02
- **Hỏi**: thang 9/2025 cua hang co bnhiu % don bi huy
- **Gold**: 1.66
- **Code**:
```python
import pandas as pd

# Lấy bảng phù hợp nhất
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])

if df is None:
    ans = None
else:
    # Tìm cột ngày và cột trạng thái
    date_col = None
    status_col = None
    for c in df.columns:
        cl = c.lower()
        if date_col is None and ('ngay' in cl or 'date' in cl or 'thoi_gian' in cl):
            date_col = c
        if status_col is None and ('trang_thai' in cl or 'status' in cl or 'huy' in cl):
            status_col = c
    
    if date_col is None or status_col is None:
        ans = None
    else:
        df = df.copy()
        df[date_col] = parse_date_safe(df[date_col])
        mask = (df[date_col].dt.year == 2025) & (df[date_col].dt.month == 9)
        sub = df[mask]
        if len(sub) == 0:
            ans = 0.0
        else:
            status_str = sub[status_col].astype(str).str.lower()
            cancelled = status_str.str.contains('huy|hủy|cancel', na=False)
            ans = cancelled.sum() / len(sub) * 100
```
- **Trạng thái**: ❌ SAI (None != 1.66)

## Câu 16: q_0174cb13db2a | Ngày: 2026-09-10
- **Hỏi**: tháng này cửa hàng đã chở giao bao nhiêu đợt hàng cho khách nhỉ
- **Gold**: 290
- **Code**:
```python
import pandas as pd
from datetime import datetime

# Lấy bảng phiếu giao hàng
df = get_df_by_keyword(dfs, ['Bảng kê phiếu giao hàng'])

if df is None:
    ans = None
else:
    # Tìm cột ngày
    date_col = None
    for c in df.columns:
        cl = c.lower()
        if 'ngày' in cl and ('giao' in cl or 'lập' in cl or 'chứng từ' in cl):
            date_col = c
            break
    if date_col is None:
        for c in df.columns:
            if 'ngày' in c.lower():
                date_col = c
                break
    
    if date_col is None:
        ans = None
    else:
        df['_date'] = parse_date_safe(df[date_col])
        target_month = 9
        target_year = 2026
        mask = (df['_date'].dt.month == target_month) & (df['_date'].dt.year == target_year)
        ans = int(mask.sum())
```
- **Trạng thái**: ❌ SAI (None != 290)

## Câu 17: q_0183529f9d61 | Ngày: 2026-05-25
- **Hỏi**: dthu 3 tháng liền nhau kết thúc ở tháng 6/2025 là bao nhiêu mỗi tháng, từ tháng cũ đến tháng mới
- **Gold**: [287435200, 346554700, 309693800]
- **Code**:
```python
import pandas as pd

# Lấy bảng hóa đơn
df_hd = get_df_by_keyword(dfs, ['BanHang_HoaDon'])

if df_hd is None:
    ans = None
else:
    df = df_hd.copy()
    # Tìm cột ngày và cột tiền
    date_col = None
    for c in df.columns:
        if 'ngay' in c.lower():
            date_col = c
            break
    money_col = None
    for c in df.columns:
        cl = c.lower()
        if ('tien' in cl or 'tong' in cl or 'thanh' in cl) and 'toan' in cl:
            money_col = c
            break
    if money_col is None:
        for c in df.columns:
            cl = c.lower()
            if 'tien' in cl or 'tong' in cl or 'thanh' in cl:
                money_col = c
                break

    if date_col is None or money_col is None:
        ans = None
    else:
        df['_date'] = parse_date_safe(df[date_col])
        df['_money'] = clean_money(df[money_col])
        df = df.dropna(subset=['_date'])
        df['_ym'] = df['_date'].dt.to_period('M')
        # 3 tháng liền nhau kết thúc ở 6/2025: 4,5,6/2025
        target = [pd.Period('2025-04', 'M'), pd.Period('2025-05', 'M'), pd.Period('2025-06', 'M')]
        df_f = df[df['_ym'].isin(target)]
        grouped = df_f.groupby('_ym')['_money'].sum()
        ans = {str(k): float(grouped.get(k, 0)) for k in target}
```
- **Trạng thái**: ❌ SAI (None != [287435200, 346554700, 309693800])

## Câu 18: q_0194d8d10f17 | Ngày: 2026-08-19
- **Hỏi**: Tính đến hết ngày 19/08/2026, có bao nhiêu khách còn nợ cửa hàng?
- **Gold**: 35
## Câu 19: q_019ec94d9799 | Ngày: 2026-08-19
- **Hỏi**: 3 mặt hàng bán chạy nhất tuần này là những mặt hàng nào?
- **Gold**: ['Cà phê sữa (M)', 'Trà đào cam sả (M)', 'Cà phê đen (M)']
## Câu 20: q_01a252a82858 | Ngày: 2026-06-02
- **Hỏi**: Ngày 14/07/2025 cửa hàng bán Cà phê muối (L) với đơn giá bao nhiêu một ly?
- **Gold**: 41000
- **Code**:
```python
import pandas as pd

# Lấy bảng phù hợp
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])

if df is None:
    ans = None
else:
    # Tìm cột ngày, tên sản phẩm, đơn giá
    date_col = None
    for c in df.columns:
        if 'ngày' in c.lower() or 'date' in c.lower():
            date_col = c
            break
    
    name_col = None
    for c in df.columns:
        if 'tên' in c.lower() or 'sản phẩm' in c.lower() or 'mặt hàng' in c.lower():
            name_col = c
            break
    
    price_col = None
    for c in df.columns:
        if 'đơn giá' in c.lower() or 'giá' in c.lower() or 'price' in c.lower():
            price_col = c
            break
    
    if date_col is None or name_col is None or price_col is None:
        ans = None
    else:
        df['_date'] = parse_date_safe(df[date_col])
        df['_price'] = clean_money(df[price_col])
        
        mask = (df['_date'] == pd.Timestamp('2025-07-14')) & \
               (df[name_col].astype(str).str.contains('Cà phê muối', case=False, na=False)) & \
               (df[name_col].astype(str).str.contains(r'\(L\)', case=False, na=False, regex=True))
        
        filtered = df[mask]
        if len(filtered) == 0:
            ans = None
        else:
            ans = filtered['_price'].iloc[0]
```
- **Trạng thái**: ❌ SAI (None != 41000)

## Câu 21: q_01a28f2233bd | Ngày: 2026-07-31
- **Hỏi**: gia ban mot ly soda chanh day (m) vao ngay 01/12/2025 la bn
- **Gold**: 37000
## Câu 22: q_01a47607f90c | Ngày: 2026-08-11
- **Hỏi**: tổng dthu trong ngày hôm nay là bao nhiêu vaayj
- **Gold**: 39793500
- **Code**:
```python
import pandas as pd

# Xác định bảng hóa đơn tháng 08.2026 (ngày chốt 2026-08-11)
df = get_df_by_keyword(dfs, ['DanhSachHoaDon_08.2026'])

if df is None:
    ans = None
else:
    # Tìm cột ngày và cột doanh thu
    date_col = None
    for c in df.columns:
        cl = c.lower()
        if 'ngay' in cl or 'date' in cl:
            date_col = c
            break

    money_col = None
    for c in df.columns:
        cl = c.lower()
        if ('tong' in cl and 'tien' in cl) or 'thanhtien' in cl or 'doanhthu' in cl or 'tongcong' in cl:
            money_col = c
            break

    if date_col is None or money_col is None:
        ans = None
    else:
        df['_date'] = parse_date_safe(df[date_col])
        df['_money'] = clean_money(df[money_col])
        target = pd.Timestamp('2026-08-11')
        mask = df['_date'].dt.normalize() == target
        ans = df.loc[mask, '_money'].sum()
```
- **Trạng thái**: ❌ SAI (None != 39793500)

## Câu 23: q_01b914589609 | Ngày: 2025-02-19
- **Hỏi**: Cho tôi biết dthu 30 ngày gần nhất
- **Gold**: 730984600
- **Code**:
```python
import pandas as pd
from datetime import timedelta

# Lấy bảng bán hàng tháng 01-2025 và 02-2025 (30 ngày gần nhất tính từ 2025-02-19)
df1 = get_df_by_keyword(dfs, ['SoBanHang_Tháng 01-2025'])
df2 = get_df_by_keyword(dfs, ['SoBanHang_Tháng 02-2025'])

if df1 is None and df2 is None:
    ans = None
else:
    frames = [d for d in [df1, df2] if d is not None]
    df = pd.concat(frames, ignore_index=True)

    # Xác định cột ngày
    date_col = None
    for c in df.columns:
        if 'ngày' in c.lower() or 'ngay' in c.lower() or 'date' in c.lower():
            date_col = c
            break

    # Xác định cột doanh thu
    rev_col = None
    for c in df.columns:
        cl = c.lower()
        if ('doanh thu' in cl) or ('dthu' in cl) or ('thành tiền' in cl) or ('thanh tien' in cl) or ('số tiền' in cl) or ('so tien' in cl):
            rev_col = c
            break

    if date_col is None or rev_col is None:
        ans = None
    else:
        df['_date'] = parse_date_safe(df[date_col])
        df['_rev'] = clean_money(df[rev_col])

        end_date = pd.Timestamp('2025-02-19')
        start_date = end_date - timedelta(days=29)

        mask = (df['_date'] >= start_date) & (df['_date'] <= end_date)
        ans = df.loc[mask, '_rev'].sum()
```
- **Trạng thái**: ❌ SAI (None != 730984600)

## Câu 24: q_01bba93199de | Ngày: 2026-08-29
- **Hỏi**: Doanh thu tháng 4/2026 bao nhiêu?
- **Gold**: 1380833500
## Câu 25: q_0266c6b24cbf | Ngày: 2026-09-14
- **Hỏi**: Tháng 5/2026 giá nhập bình quân một hộp Bánh croissant là bao nhiêu vậy?
- **Gold**: 92897
## Câu 26: q_026fa17395ed | Ngày: 2026-05-25
- **Hỏi**: Tính đến hết ngày 25/05/2026, khách hàng còn nợ cửa hàng tổng cộng bao nhiêu tiền?
- **Gold**: 948973
## Câu 27: q_026fabde15fc | Ngày: 2026-07-09
- **Hỏi**: Cho hỏi tổng doanh thu quý 2/2026 là bao nhiêu?
- **Gold**: 518445500
- **Code**:
```python
# Tổng doanh thu quý 2/2026 = tháng 4 + 5 + 6 năm 2026
tables = ['DonHang_ChiTiet_04.2026', 'DonHang_ChiTiet_05.2026', 'DonHang_ChiTiet_06.2026']

total = 0.0
found_any = False

for tname in tables:
    df = get_df_by_keyword(dfs, [tname])
    if df is None:
        continue
    # Tìm cột ngày và cột tiền
    date_col = None
    for c in df.columns:
        cl = c.lower()
        if 'ngay' in cl or 'date' in cl or 'thoi_gian' in cl or 'time' in cl:
            date_col = c
            break
    money_col = None
    for c in df.columns:
        cl = c.lower()
        if 'thanh_tien' in cl or 'doanh_thu' in cl or 'tong_tien' in cl or 'amount' in cl or 'total' in cl or 'tien' in cl:
            money_col = c
            break
    if date_col is None or money_col is None:
        continue
    df = df.copy()
    df['_date'] = parse_date_safe(df[date_col])
    df['_money'] = clean_money(df[money_col])
    mask = (df['_date'].dt.year == 2026) & (df['_date'].dt.month.isin([4, 5, 6]))
    total += df.loc[mask, '_money'].sum()
    found_any = True

ans = total if found_any else None
```
- **Trạng thái**: ❌ SAI (None != 518445500)

## Câu 28: q_0271d9f39fde | Ngày: 2026-07-31
- **Hỏi**: tháng 5/2026 cửa hàng có nhiêu % đơn bị huỷ
- **Gold**: 2.19
- **Code**:
```python
import pandas as pd

# Lấy bảng chi tiết bán hàng tháng 5/2026
df = get_df_by_keyword(dfs, ['So_chi_tiet_ban_hang_1_T05_2026'])

if df is None:
    ans = None
else:
    # Tìm cột trạng thái đơn
    status_col = None
    for c in df.columns:
        cl = c.lower()
        if 'trang' in cl or 'status' in cl or 'huy' in cl or 'huỷ' in cl:
            status_col = c
            break
    
    if status_col is None:
        ans = None
    else:
        total = len(df)
        if total == 0:
            ans = 0.0
        else:
            s = df[status_col].astype(str).str.lower().str.strip()
            cancelled = s.str.contains('huy|huỷ|cancel', regex=True, na=False).sum()
            ans = cancelled / total * 100
```
- **Trạng thái**: ❌ SAI (None != 2.19)

## Câu 29: q_0279f675859e | Ngày: 2026-08-19
- **Hỏi**: thang 7/2025, cac khach thuoc nhom than thiet mua tong cong bao nhiu tien hang
- **Gold**: 46871000
## Câu 30: q_0283688e44df | Ngày: 2025-06-20
- **Hỏi**: Cho hỏi tuần trước riêng ca chiều bán được tổng cộng bao nhiêu tiền?
- **Gold**: 109181000
- **Code**:
```python
import pandas as pd
from datetime import timedelta

# Ngày chốt
ngay_chot = pd.Timestamp('2025-06-20')

# Tuần trước: từ thứ 2 đến chủ nhật của tuần trước
# ngay_chot là thứ 6 (2025-06-20)
# Tuần trước: 2025-06-09 (thứ 2) đến 2025-06-15 (chủ nhật)
start_of_week = ngay_chot - timedelta(days=ngay_chot.weekday() + 7)
end_of_week = start_of_week + timedelta(days=6)

# Lấy bảng hóa đơn tháng 06.2025
df_hd = get_df_by_keyword(dfs, ['DanhSachHoaDon_06.2025'])

if df_hd is None:
    ans = None
else:
    # Tìm cột ngày và cột ca
    date_col = None
    for c in df_hd.columns:
        if 'ngày' in c.lower() or 'ngay' in c.lower():
            date_col = c
            break
    
    ca_col = None
    for c in df_hd.columns:
        if 'ca' in c.lower():
            ca_col = c
            break
    
    # Tìm cột tiền (thành tiền / tổng tiền)
    money_col = None
    for c in df_hd.columns:
        cl = c.lower()
        if ('thành tiền' in cl or 'thanh tien' in cl or 'tổng tiền' in cl or 'tong tien' in cl or 'số tiền' in cl or 'so tien' in cl):
            money_col = c
            break
    
    if date_col is None or ca_col is None or money_col is None:
        ans = None
    else:
        df_hd = df_hd.copy()
        df_hd[date_col] = parse_date_safe(df_hd[date_col])
        df_hd[money_col] = clean_money(df_hd[money_col])
        
        # Lọc ca chiều
        mask_ca = df_hd[ca_col].astype(str).str.lower().str.contains('chiều|chieu', na=False)
        # Lọc tuần trước
        mask_date = (df_hd[date_col] >= start_of_week) & (df_hd[date_col] <= end_of_week)
        
        filtered = df_hd[mask_ca & mask_date]
        ans = filtered[money_col].sum()
```
- **Trạng thái**: ❌ SAI (None != 109181000)

## Câu 31: q_0285dfd1bb28 | Ngày: 2026-07-28
- **Hỏi**: Doanh thu trung bình trên một đơn tháng 3/2025 là bao nhiêu ạ?
- **Gold**: 522915
- **Code**:
```python
import pandas as pd

# Lấy bảng đơn hàng
df = get_df_by_keyword(dfs, ['don_hang'])

if df is None:
    ans = None
else:
    # Chuẩn hóa ngày
    df['ngay_dat'] = parse_date_safe(df['ngay_dat'])
    
    # Lọc tháng 3/2025
    mask = (df['ngay_dat'].dt.year == 2025) & (df['ngay_dat'].dt.month == 3)
    df_m3 = df[mask]
    
    if df_m3.empty:
        ans = None
    else:
        # Lấy cột doanh thu (tổng tiền đơn)
        col_money = None
        for c in ['tong_tien', 'thanh_tien', 'doanh_thu', 'tong_thanh_toan', 'gia_tri_don']:
            if c in df_m3.columns:
                col_money = c
                break
        
        if col_money is None:
            ans = None
        else:
            df_m3 = df_m3.copy()
            df_m3[col_money] = clean_money(df_m3[col_money])
            ans = df_m3[col_money].mean()
```
- **Lỗi**: Lỗi Runtime: 'ngay_dat'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 32: q_028dcfb561ea | Ngày: 2026-09-10
- **Hỏi**: Tháng 6/2026 khách mua từ 4 đơn trở lên chiếm bao nhiêu % số khách đã mua nhỉ?
- **Gold**: 23.77
- **Code**:
```python
import pandas as pd

# Lấy bảng chi tiết bán hàng tháng 6/2026
df = get_df_by_keyword(dfs, ['So_chi_tiet_ban_hang_T06-2026'])

if df is None:
    ans = None
else:
    # Xác định cột ngày và cột mã khách
    date_col = None
    for c in df.columns:
        cl = c.lower()
        if 'ngay' in cl or 'date' in cl:
            date_col = c
            break
    
    cust_col = None
    for c in df.columns:
        cl = c.lower()
        if 'ma_kh' in cl or 'makh' in cl or 'khach' in cl or 'customer' in cl:
            cust_col = c
            break
    
    # Xác định cột số hóa đơn / phiếu
    bill_col = None
    for c in df.columns:
        cl = c.lower()
        if 'so_hd' in cl or 'sohd' in cl or 'so_ct' in cl or 'soct' in cl or 'hoa_don' in cl or 'phieu' in cl or 'chung_tu' in cl:
            bill_col = c
            break
    
    if date_col is None or cust_col is None or bill_col is None:
        ans = None
    else:
        df = df.copy()
        df[date_col] = parse_date_safe(df[date_col])
        df[cust_col] = normalize_id(df[cust_col])
        
        # Lọc tháng 6/2026
        mask = (df[date_col].dt.year == 2026) & (df[date_col].dt.month == 6)
        df_jun = df[mask]
        
        if len(df_jun) == 0:
            ans = 0.0
        else:
            # Đếm số đơn (unique) theo từng khách
            orders_per_cust = df_jun.groupby(cust_col)[bill_col].nunique()
            total_cust = orders_per_cust.shape[0]
            cust_ge4 = (orders_per_cust >= 4).sum()
            ans = round(cust_ge4 / total_cust * 100, 2) if total_cust > 0 else 0.0
```
- **Trạng thái**: ❌ SAI (None != 23.77)

## Câu 33: q_02a28b3629be | Ngày: 2026-07-09
- **Hỏi**: Cho hỏi số đơn bị huỷ trong tháng 8 năm 2025 là bao nhiêu?
- **Gold**: 32
- **Code**:
```python
import pandas as pd

# Chọn bảng phù hợp: tháng 8 năm 2025
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet_08.2025'])

if df is None:
    ans = None
else:
    # Tìm cột trạng thái đơn hàng
    status_col = None
    for c in df.columns:
        cl = c.lower()
        if 'trangthai' in cl or 'trạng thái' in cl or 'status' in cl or 'tinhtrang' in cl:
            status_col = c
            break
    
    if status_col is None:
        ans = None
    else:
        # Đếm số đơn bị huỷ (unique theo mã đơn nếu có)
        id_col = None
        for c in df.columns:
            cl = c.lower()
            if 'madon' in cl or 'mã đơn' in cl or 'orderid' in cl or 'order_id' in cl or 'sohoadon' in cl:
                id_col = c
                break
        
        mask = df[status_col].astype(str).str.lower().str.contains('hủy|huỷ|huy|cancel', na=False)
        
        if id_col is not None:
            ans = df.loc[mask, id_col].nunique()
        else:
            ans = int(mask.sum())
```
- **Trạng thái**: ĐÚNG (Kết quả: 32)

## Câu 34: q_02a70ea566f1 | Ngày: 2026-07-31
- **Hỏi**: Top 3 sp bán nhiều nhất tháng 3 năm 2026 là những gì?
- **Gold**: ['Cà phê sữa (M)', 'Trà đào cam sả (M)', 'Cà phê đen (M)']
- **Code**:
```python
import pandas as pd

# Lấy bảng chi tiết bán hàng tháng 3/2026
df = get_df_by_keyword(dfs, ['So_chi_tiet_ban_hang_1_T03_2026'])
df_hh = get_df_by_keyword(dfs, ['Danh_s├ích_h├áng_h├│a'])

if df is None or df_hh is None:
    ans = None
else:
    try:
        # Xác định cột số lượng và mã hàng
        qty_col = None
        for c in df.columns:
            cl = str(c).lower()
            if 'số lượng' in cl or 'so_luong' in cl or 'sl' in cl:
                qty_col = c
                break
        ma_col = None
        for c in df.columns:
            cl = str(c).lower()
            if 'mã' in cl and ('hàng' in cl or 'hh' in cl or 'sp' in cl):
                ma_col = c
                break
        if ma_col is None:
            for c in df.columns:
                if 'ma' in str(c).lower():
                    ma_col = c
                    break

        # Cột mã trong danh sách hàng hóa
        ma_hh_col = None
        ten_hh_col = None
        for c in df_hh.columns:
            cl = str(c).lower()
            if 'mã' in cl and ma_hh_col is None:
                ma_hh_col = c
            if ('tên' in cl) and ten_hh_col is None:
                ten_hh_col = c

        if qty_col is None or ma_col is None or ma_hh_col is None:
            ans = None
        else:
            df['_ma'] = normalize_id(df[ma_col])
            df['_qty'] = pd.to_numeric(df[qty_col], errors='coerce').fillna(0)
            grouped = df.groupby('_ma', as_index=False)['_qty'].sum()
            grouped = grouped.sort_values('_qty', ascending=False).head(3)

            df_hh['_ma'] = normalize_id(df_hh[ma_hh_col])
            merged = grouped.merge(df_hh[['_ma', ten_hh_col]], on='_ma', how='left')
            ans = merged[[ten_hh_col, '_qty']].rename(columns={ten_hh_col: 'Tên hàng hóa', '_qty': 'Số lượng bán'})
    except Exception:
        ans = None
```
- **Trạng thái**: ❌ SAI (['nan', 'nan', 'nan'] != ['Cà phê sữa (M)', 'Trà đào cam sả (M)', 'Cà phê đen (M)'])

## Câu 35: q_02b4a032b9f3 | Ngày: 2026-06-12
- **Hỏi**: Trong tháng 11/2025, tỉ lệ đơn huỷ là bao nhiêu phần trăm?
- **Gold**: 1.17
- **Code**:
```python
import pandas as pd

# Lấy bảng hóa đơn tháng 11/2025
df = get_df_by_keyword(dfs, ['DanhSachHoaDon_11.2025'])

if df is None:
    ans = None
else:
    # Tìm cột trạng thái đơn hàng
    status_col = None
    for c in df.columns:
        cl = c.lower()
        if 'trạng thái' in cl or 'trang thai' in cl or 'status' in cl or 'tình trạng' in cl:
            status_col = c
            break
    
    if status_col is None:
        ans = None
    else:
        total = len(df)
        if total == 0:
            ans = 0.0
        else:
            status_series = df[status_col].astype(str).str.strip().str.lower()
            # Đếm đơn huỷ
            cancel_mask = status_series.str.contains('huỷ|hủy|cancel|đã hủy|đã huỷ', na=False)
            cancelled = cancel_mask.sum()
            ans = round(cancelled / total * 100, 2)
```
- **Trạng thái**: ĐÚNG (Kết quả: 1.17)

## Câu 36: q_02b5f208ee57 | Ngày: 2026-05-25
- **Hỏi**: Từ ngày 16/03/2025, Fugacar 500mg hộp 1 viên tăng giá lên 23.000đ. So 7 ngày kể từ ngày 16/03/2025 với 7 ngày ngay trước đó, số viên bán ra thay đổi bao nhiêu phần trăm nhỉ?
- **Gold**: 69.57
## Câu 37: q_02b7cc8b174d | Ngày: 2026-07-28
- **Hỏi**: Xem giúp tháng 2/2026 nhóm hải sản chiếm bao nhiêu % doanh thu?
- **Gold**: 9.37
- **Code**:
```python
import pandas as pd

# Lấy các bảng cần thiết
df_ct = get_df_by_keyword(dfs, ['chi_tiet_don'])
df_sp = get_df_by_keyword(dfs, ['san_pham'])

if df_ct is None or df_sp is None:
    ans = None
else:
    # Chuẩn hóa ID để join
    df_ct = df_ct.copy()
    df_sp = df_sp.copy()
    df_ct['san_pham_id'] = normalize_id(df_ct['san_pham_id'])
    df_sp['san_pham_id'] = normalize_id(df_sp['san_pham_id'])
    
    # Parse ngày
    df_ct['ngay'] = parse_date_safe(df_ct['ngay'])
    
    # Lọc tháng 2/2026
    mask = (df_ct['ngay'].dt.year == 2026) & (df_ct['ngay'].dt.month == 2)
    df_feb = df_ct[mask].copy()
    
    # Tính doanh thu từng dòng
    df_feb['doanh_thu'] = clean_money(df_feb['thanh_tien']) if 'thanh_tien' in df_feb.columns else clean_money(df_feb['gia_ban']) * df_feb['so_luong']
    
    # Join với sản phẩm để lấy nhóm
    df_merge = df_feb.merge(df_sp[['san_pham_id', 'nhom_hang']], on='san_pham_id', how='left')
    
    # Tính tổng doanh thu và doanh thu hải sản
    tong = df_merge['doanh_thu'].sum()
    hai_san = df_merge[df_merge['nhom_hang'].astype(str).str.contains('hải sản', case=False, na=False)]['doanh_thu'].sum()
    
    ans = round(hai_san / tong * 100, 2) if tong > 0 else 0
```
- **Lỗi**: Lỗi Runtime: 'san_pham_id'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 38: q_02eb42db6665 | Ngày: 2026-05-11
- **Hỏi**: tháng 5/2025 hàng nào bán chạy nhất
- **Gold**: Bia Tiger lon
- **Code**:
```python
import pandas as pd

df = get_df_by_keyword(dfs, ['ban_hang'])

if df is None:
    ans = None
else:
    try:
        df = df.copy()
        date_col = None
        for c in df.columns:
            if 'ngay' in c.lower() or 'date' in c.lower():
                date_col = c
                break
        
        if date_col is None:
            ans = None
        else:
            df[date_col] = parse_date_safe(df[date_col])
            mask = (df[date_col].dt.year == 2025) & (df[date_col].dt.month == 5)
            df_may = df[mask]
            
            if df_may.empty:
                ans = None
            else:
                # Tìm cột hàng hóa và cột số lượng
                hang_col = None
                for c in df_may.columns:
                    cl = c.lower()
                    if 'hang' in cl or 'san_pham' in cl or 'ten_hang' in cl or 'product' in cl:
                        hang_col = c
                        break
                
                qty_col = None
                for c in df_may.columns:
                    cl = c.lower()
                    if 'so_luong' in cl or 'quantity' in cl or 'sl' in cl:
                        qty_col = c
                        break
                
                if hang_col is None:
                    ans = None
                else:
                    if qty_col is not None:
                        grouped = df_may.groupby(hang_col)[qty_col].sum()
                    else:
                        grouped = df_may.groupby(hang_col).size()
                    ans = grouped.idxmax()
    except Exception:
        ans = None
```
- **Trạng thái**: ❌ SAI (None != Bia Tiger lon)

## Câu 39: q_02ed16421456 | Ngày: 2026-06-24
- **Hỏi**: tháng 8/2025 quán bán đc bn ly size m
- **Gold**: 5604
- **Code**:
```python
import pandas as pd
import re

def get_df_by_keyword(dfs, keywords):
    for k in keywords:
        for name, df in dfs.items():
            if k.lower() in name.lower():
                return df
    return None

def parse_date_safe(s):
    return pd.to_datetime(s, errors='coerce', dayfirst=False)

def clean_money(s):
    if s is None:
        return s
    return pd.to_numeric(s.astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce')

def normalize_id(s):
    if s is None:
        return s
    return s.astype(str).str.strip().str.upper()

ans = None
try:
    df = get_df_by_keyword(dfs, ['SoBanHang_1_Thang 08 2025'])
    if df is None:
        ans = None
    else:
        cols = {c.lower(): c for c in df.columns}
        size_col = None
        for c in df.columns:
            cl = c.lower()
            if 'size' in cl or 'cỡ' in cl or 'co' == cl:
                size_col = c
                break
        qty_col = None
        for c in df.columns:
            cl = c.lower()
            if 'số lượng' in cl or 'so luong' in cl or 'sl' == cl or 'quantity' in cl:
                qty_col = c
                break
        if size_col is None or qty_col is None:
            ans = None
        else:
            mask = df[size_col].astype(str).str.strip().str.upper() == 'M'
            qty = clean_money(df.loc[mask, qty_col])
            ans = int(qty.sum()) if qty is not None else None
except Exception:
    ans = None
```
- **Trạng thái**: ❌ SAI (None != 5604)

## Câu 40: q_02f8f6235ddb | Ngày: 2026-05-16
- **Hỏi**: coi gium trong thang 5 nam 2025 cua hang ban duoc may kg thep cuon phi 6 hoa phat
- **Gold**: 130
- **Code**:
```python
import pandas as pd
import re

# Lấy bảng chi tiết bán hàng tháng 5/2025
df = get_df_by_keyword(dfs, ['So_chi_tiet_ban_hang_05.2025'])

if df is None:
    ans = None
else:
    # Tìm cột mã hàng và tên hàng
    ma_col = None
    ten_col = None
    for c in df.columns:
        cl = c.lower()
        if 'ma' in cl and ('hang' in cl or 'hh' in cl or 'vt' in cl):
            ma_col = c
        if ('ten' in cl) and ('hang' in cl or 'hh' in cl or 'vt' in cl):
            ten_col = c
    
    # Tìm cột số lượng
    sl_col = None
    for c in df.columns:
        cl = c.lower()
        if 'so_luong' in cl or 'soluong' in cl or ('sl' in cl and 'luong' in cl):
            sl_col = c
            break
    
    if sl_col is None:
        ans = None
    else:
        # Lọc theo tên hàng chứa "phi 6" và "hoa phat"
        mask = pd.Series([False]*len(df), index=df.index)
        if ten_col is not None:
            ten_norm = df[ten_col].astype(str).str.lower().str.replace(r'\s+', ' ', regex=True)
            mask = ten_norm.str.contains('phi 6', na=False) & ten_norm.str.contains('hoa phat', na=False)
        elif ma_col is not None:
            ma_norm = df[ma_col].astype(str).str.lower()
            mask = ma_norm.str.contains('phi 6', na=False) & ma_norm.str.contains('hoa phat', na=False)
        
        filtered = df[mask]
        
        if len(filtered) == 0:
            ans = 0
        else:
            sl = pd.to_numeric(filtered[sl_col], errors='coerce').fillna(0)
            ans = float(sl.sum())
```
- **Trạng thái**: ❌ SAI (None != 130)

## Câu 41: q_03766ac30505 | Ngày: 2026-09-10
- **Hỏi**: Quý 4/2025 cửa hàng có bao nhiêu đơn hàng ạ?
- **Gold**: 3238
- **Code**:
```python
import pandas as pd

# Quý 4/2025 gồm tháng 10, 11, 12 năm 2025
tables_q4_2025 = [
    'So_chi_tiet_ban_hang_T10-2025',
    'So_chi_tiet_ban_hang_T11-2025',
    'So_chi_tiet_ban_hang_T12-2025'
]

total_orders = 0
found_any = False

for tbl in tables_q4_2025:
    try:
        df = get_df_by_keyword(dfs, [tbl])
        if df is None or df.empty:
            continue
        found_any = True
        # Tìm cột mã đơn hàng
        order_col = None
        for c in df.columns:
            cl = str(c).lower()
            if 'mã đơn' in cl or 'ma don' in cl or 'số phiếu' in cl or 'so phieu' in cl or 'mã phiếu' in cl or 'ma phieu' in cl or 'mã hđ' in cl or 'ma hd' in cl:
                order_col = c
                break
        if order_col is None:
            # fallback: cột đầu tiên
            order_col = df.columns[0]
        total_orders += df[order_col].dropna().nunique()
    except Exception:
        continue

if found_any:
    ans = total_orders
else:
    ans = None
```
- **Trạng thái**: ❌ SAI (3340 != 3238)

## Câu 42: q_03a446be8b75 | Ngày: 2026-09-20
- **Hỏi**: trong thang 2/2025, ti le don huy la bao nhieu %
- **Gold**: None
- **Code**:
```python
import pandas as pd

# Tìm bảng phù hợp nhất
df = get_df_by_keyword(dfs, ['DuLieuXuat_DonHang_Lo'])

if df is None:
    ans = None
else:
    # Tìm cột ngày và cột trạng thái hủy
    date_col = None
    for c in df.columns:
        if 'ngay' in c.lower() or 'date' in c.lower() or 'thoi_gian' in c.lower():
            date_col = c
            break
    
    status_col = None
    for c in df.columns:
        if 'trang_thai' in c.lower() or 'status' in c.lower() or 'huy' in c.lower():
            status_col = c
            break
    
    if date_col is None or status_col is None:
        ans = None
    else:
        df['_date'] = parse_date_safe(df[date_col])
        df_feb = df[(df['_date'].dt.year == 2025) & (df['_date'].dt.month == 2)]
        
        if len(df_feb) == 0:
            ans = 0.0
        else:
            status_str = df_feb[status_col].astype(str).str.lower()
            cancelled = status_str.str.contains('huy|hủy|cancel', na=False).sum()
            ans = round(cancelled / len(df_feb) * 100, 2)
```
- **Trạng thái**: ❌ SAI (None != None)

## Câu 43: q_03cf8b6c4b16 | Ngày: 2026-06-24
- **Hỏi**: thang 3/2026 hang nuoc ep dua hau (l) thu ve bao nhieu tien ha
- **Gold**: 4012000
- **Code**:
```python
import pandas as pd
import re

# Lấy bảng bán hàng tháng 03/2026
df = get_df_by_keyword(dfs, ['SoBanHang_2026_Thang 03 2026'])

if df is None:
    ans = None
else:
    # Tìm cột tên sản phẩm và cột thành tiền
    cols = list(df.columns)
    
    # Xác định cột tên hàng
    name_col = None
    for c in cols:
        cl = c.lower()
        if 'tên' in cl or 'ten' in cl or 'hàng' in cl or 'hang' in cl or 'sản phẩm' in cl or 'san pham' in cl:
            name_col = c
            break
    
    # Xác định cột thành tiền / doanh thu
    money_col = None
    for c in cols:
        cl = c.lower()
        if 'thành tiền' in cl or 'thanh tien' in cl or 'doanh thu' in cl or 'doanh_thu' in cl or 'số tiền' in cl or 'so tien' in cl or 'tổng' in cl or 'tong' in cl:
            money_col = c
            break
    
    if name_col is None or money_col is None:
        ans = None
    else:
        # Lọc dòng có "nước ép dưa hấu"
        mask = df[name_col].astype(str).str.lower().str.contains('nước ép dưa hấu', na=False) | \
               df[name_col].astype(str).str.lower().str.contains('nuoc ep dua hau', na=False)
        filtered = df[mask]
        
        if filtered.empty:
            ans = 0
        else:
            ans = clean_money(filtered[money_col]).sum()
```
- **Trạng thái**: ❌ SAI (None != 4012000)

## Câu 44: q_03d662023a15 | Ngày: 2026-09-03
- **Hỏi**: trong thang 9/2025, cua hang co may don o trang thai huy
- **Gold**: 23
## Câu 45: q_040c9dd7f4de | Ngày: 2026-09-03
- **Hỏi**: Tháng 9/2025 top 5 hàng bán chạy nhất là gì?
- **Gold**: ['Xi măng Hà Tiên PCB40 bao 50kg', 'Gạch ống 8x8x18 Tuynel', 'Xi măng INSEE Power-S bao 50kg', 'Băng keo điện Nano 20 yard', 'Ống PVC Bình Minh D32 cây 4m']
- **Code**:
```python
import pandas as pd

# Chọn bảng chi tiết bán hàng
df = get_df_by_keyword(dfs, ['Bao_cao_ban_hang_So_chi_tiet_ban_hang'])

if df is None:
    ans = None
else:
    try:
        # Tìm cột ngày và cột số lượng
        date_col = None
        for c in df.columns:
            cl = c.lower()
            if 'ngày' in cl or 'ngay' in cl or 'date' in cl:
                date_col = c
                break
        
        qty_col = None
        for c in df.columns:
            cl = c.lower()
            if 'số lượng' in cl or 'so luong' in cl or 'quantity' in cl:
                qty_col = c
                break
        
        item_col = None
        for c in df.columns:
            cl = c.lower()
            if 'mã hàng' in cl or 'ma hang' in cl or 'tên hàng' in cl or 'ten hang' in cl or 'hàng hóa' in cl or 'hang hoa' in cl or 'sản phẩm' in cl or 'san pham' in cl:
                item_col = c
                break
        
        if date_col is None or qty_col is None or item_col is None:
            ans = None
        else:
            df = df.copy()
            df[date_col] = parse_date_safe(df[date_col])
            df[qty_col] = pd.to_numeric(df[qty_col], errors='coerce')
            
            mask = (df[date_col].dt.year == 2025) & (df[date_col].dt.month == 9)
            df_sep = df[mask]
            
            ans = (
                df_sep.groupby(item_col)[qty_col]
                .sum()
                .sort_values(ascending=False)
                .head(5)
                .reset_index()
            )
    except Exception:
        ans = None
```
- **Trạng thái**: ❌ SAI (['Gạch ống 8x8x18 Tuynel', 'Thép cuộn phi 6 Hòa Ph != ['Xi măng Hà Tiên PCB40 bao 50kg', 'Gạch ống 8x8x18 Tuynel', 'Xi măng INSEE Power-S bao 50kg', 'Băng keo điện Nano 20 yard', 'Ống PVC Bình Minh D32 cây 4m'])

## Câu 46: q_040ffbb6869a | Ngày: 2026-05-16
- **Hỏi**: cho hoi dem so don da huy trong thang 2/2026
- **Gold**: 14
- **Code**:
```python
import pandas as pd

# Chọn bảng phù hợp nhất: So_chi_tiet_ban_hang_02.2026
df = get_df_by_keyword(dfs, ['So_chi_tiet_ban_hang_02.2026'])

if df is None:
    ans = None
else:
    # Tìm cột ngày và cột trạng thái/hủy đơn
    date_col = None
    status_col = None
    for c in df.columns:
        cl = str(c).lower()
        if date_col is None and ('ngay' in cl or 'date' in cl):
            date_col = c
        if status_col is None and ('trang_thai' in cl or 'status' in cl or 'huy' in cl):
            status_col = c
    
    if date_col is None or status_col is None:
        ans = None
    else:
        df = df.copy()
        df[date_col] = parse_date_safe(df[date_col])
        mask_month = (df[date_col].dt.month == 2) & (df[date_col].dt.year == 2026)
        mask_cancel = df[status_col].astype(str).str.lower().str.contains('huy|hủy|cancel', na=False)
        ans = int((mask_month & mask_cancel).sum())
```
- **Trạng thái**: ❌ SAI (None != 14)

## Câu 47: q_04128078842a | Ngày: 2026-09-10
- **Hỏi**: cửa hàng có mấy khách nhà ở đường Hai Bà Trưng
- **Gold**: None
- **Code**:
```python
import pandas as pd
import re

# Lấy bảng chi tiết bán hàng (gộp tất cả các tháng)
sales_tables = []
for key in dfs.keys():
    if 'So_chi_tiet_ban_hang' in key:
        sales_tables.append(dfs[key])

if len(sales_tables) == 0:
    ans = None
else:
    df = pd.concat(sales_tables, ignore_index=True)
    
    # Tìm cột chứa địa chỉ khách hàng
    addr_col = None
    for c in df.columns:
        cl = c.lower()
        if 'dia_chi' in cl or 'địa chỉ' in cl or 'address' in cl:
            addr_col = c
            break
    
    if addr_col is None:
        ans = None
    else:
        # Lọc khách có địa chỉ chứa "Hai Bà Trưng"
        mask = df[addr_col].astype(str).str.contains('Hai Bà Trưng', case=False, na=False)
        df_filtered = df[mask]
        
        # Tìm cột mã khách hàng
        cust_col = None
        for c in df.columns:
            cl = c.lower()
            if 'ma_khach' in cl or 'mã khách' in cl or 'ma_kh' in cl:
                cust_col = c
                break
        
        if cust_col is None:
            ans = len(df_filtered)
        else:
            ans = df_filtered[cust_col].nunique()
```
- **Trạng thái**: ❌ SAI (None != None)

## Câu 48: q_042171000b2c | Ngày: 2026-06-02
- **Hỏi**: Tháng 2/2026 có bao nhiêu đơn hàng bị huỷ?
- **Gold**: 41
- **Code**:
```python
import pandas as pd

# Lấy bảng phù hợp nhất
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])

if df is None:
    ans = None
else:
    # Tìm cột ngày và cột trạng thái
    date_col = None
    status_col = None
    for c in df.columns:
        cl = c.lower()
        if date_col is None and ('ngay' in cl or 'date' in cl or 'thoi_gian' in cl or 'time' in cl):
            date_col = c
        if status_col is None and ('trang_thai' in cl or 'status' in cl or 'tinh_trang' in cl):
            status_col = c
    
    if date_col is None or status_col is None:
        ans = None
    else:
        df = df.copy()
        df[date_col] = parse_date_safe(df[date_col])
        mask_month = (df[date_col].dt.year == 2026) & (df[date_col].dt.month == 2)
        mask_cancel = df[status_col].astype(str).str.lower().str.contains('huy|cancel|huỷ', na=False)
        ans = int((mask_month & mask_cancel).sum())
```
- **Trạng thái**: ❌ SAI (None != 41)

## Câu 49: q_04293d2ed907 | Ngày: 2026-06-18
- **Hỏi**: Ca chiều tuần trước doanh thu được bao nhiêu?
- **Gold**: 112133300
## Câu 50: q_044a0d4c3ff0 | Ngày: 2026-07-28
- **Hỏi**: tieenf bán má heo nướng nước mắm tháng 9/2025 là nhiêu
- **Gold**: 7623000
- **Code**:
```python
import pandas as pd
import re

def get_df_by_keyword(dfs, keywords):
    for k in keywords:
        if k in dfs:
            return dfs[k]
    return None

def parse_date_safe(series):
    return pd.to_datetime(series, errors='coerce')

def clean_money(series):
    return pd.to_numeric(
        series.astype(str).str.replace(r'[^\d.-]', '', regex=True),
        errors='coerce'
    )

def normalize_id(series):
    return series.astype(str).str.strip().str.lstrip('0')

# Lấy bảng chi tiết đơn
df = get_df_by_keyword(dfs, ['chi_tiet_don'])
if df is None:
    ans = None
else:
    # Tìm cột ngày, cột sản phẩm, cột số lượng, cột đơn giá/thành tiền
    date_col = next((c for c in df.columns if 'ngay' in c.lower() or 'date' in c.lower()), None)
    sp_col = next((c for c in df.columns if 'san_pham' in c.lower() or 'product' in c.lower() or 'ten' in c.lower()), None)
    qty_col = next((c for c in df.columns if 'so_luong' in c.lower() or 'quantity' in c.lower() or 'sl' in c.lower()), None)
    price_col = next((c for c in df.columns if 'thanh_tien' in c.lower() or 'total' in c.lower()), None)
    if price_col is None:
        price_col = next((c for c in df.columns if 'don_gia' in c.lower() or 'price' in c.lower() or 'gia' in c.lower()), None)

    if date_col is None or sp_col is None or price_col is None:
        ans = None
    else:
        df = df.copy()
        df['_date'] = parse_date_safe(df[date_col])
        df['_sp'] = df[sp_col].astype(str).str.lower()
        df['_money'] = clean_money(df[price_col])

        mask = (
            df['_sp'].str.contains('má heo', na=False) &
            df['_sp'].str.contains('nướng', na=False) &
            df['_sp'].str.contains('nước mắm', na=False) &
            (df['_date'].dt.year == 2025) &
            (df['_date'].dt.month == 9)
        )
        ans = df.loc[mask, '_money'].sum()
```
- **Trạng thái**: ❌ SAI (None != 7623000)

