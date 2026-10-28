# BẮT ĐẦU QUÁ TRÌNH DẠY AI

- Tổng: 10 câu

## Câu 1: q_001883280e83 | Ngày: 2026-09-07
- **Hỏi**: tháng này tổng giá trị các phiếu nhập hàng là bao nhiu
- **Gold**: 89526400
- **Code**:
```python
df = get_df_by_keyword(dfs, ['DanhSachHoaDon_12.2025'])
if df is None or len(df) == 0:
    ans = None
else:
    df['Thời gian'] = parse_date_safe(df['Thời gian'])
    df['Tổng tiền hàng'] = clean_money(df['Tổng tiền hàng'])
    df['Giảm giá'] = clean_money(df['Giảm giá'])
    df['Tổng sau giảm giá'] = clean_money(df['Tổng sau giảm giá'])
    target_month = 9
    target_year = 2026
    mask = (df['Thời gian'].dt.month == target_month) & (df['Thời gian'].dt.year == target_year)
    ans = int(df.loc[mask, 'Tổng sau giảm giá'].sum())
```
- **Trạng thái**: ❌ SAI

## Câu 2: q_00195e1e4049 | Ngày: 2026-05-25
- **Hỏi**: Thuốc có hoạt chất Natri clorid tháng này bán được tổng cộng bao nhiêu tiền?
- **Gold**: 2954200
- **Code**:
```python
df_sales = get_df_by_keyword(dfs, ['BanHang_HoaDon'])
df_drug = get_df_by_keyword(dfs, ['BanHang_Thuoc'])

if df_sales is None or len(df_sales) == 0 or df_drug is None or len(df_drug) == 0:
    ans = None
else:
    df_drug_filtered = df_drug[df_drug['Hoạt chất'].astype(str).str.contains('Natri clorid', case=False, na=False)]
    valid_ids = df_drug_filtered['Mã HH'].unique().tolist()
    
    df_sales['Ngày bán parsed'] = parse_date_safe(df_sales['Ngày bán'])
    df_sales['Tong tien clean'] = clean_money(df_sales['Tong tien'])
    
    df_month = df_sales[
        (df_sales['Ngày bán parsed'].dt.year == 2026) &
        (df_sales['Ngày bán parsed'].dt.month == 5)
    ]
    
    df_result = df_month[df_month['Order ID'].isin(valid_ids)]
    ans = int(df_result['Tong tien clean'].sum())
```
- **Trạng thái**: ❌ SAI

## Câu 3: q_002d03ebbded | Ngày: 2025-04-30
- **Hỏi**: Tổng doanh thu trong ngày hôm nay là bao nhiêu?
- **Gold**: 10309400
- **Code**:
```python
df = get_df_by_keyword(dfs, ['DanhSachHoaDon_12.2025'])
if df is None or len(df) == 0:
    ans = None
else:
    df['Thời gian'] = parse_date_safe(df['Thời gian'])
    df['Tổng tiền hàng'] = clean_money(df['Tổng tiền hàng'])
    df['Giảm giá'] = clean_money(df['Giảm giá'])
    target_date = parse_date_safe(pd.Series(['2025-04-30']))[0]
    df_today = df[df['Thời gian'] == target_date]
    df_today = df_today[~df_today['Trạng thái'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)]
    ans = int((df_today['Tổng tiền hàng'] - df_today['Giảm giá']).sum())
```
- **Trạng thái**: ❌ SAI

## Câu 4: q_00558c1410ef | Ngày: 2026-06-24
- **Hỏi**: tỉ lệ huỷ đơn tháng 6/2025 là nhiêu %
- **Gold**: 2.08
- **Code**:
```python
df = get_df_by_keyword(dfs, ['SoBanHang_1_Thang 12 2025'])
if df is None or len(df) == 0:
    ans = None
else:
    df['Ngày giao dịch'] = parse_date_safe(df['Ngày giao dịch'])
    df_jun = df[(df['Ngày giao dịch'].dt.month == 6) & (df['Ngày giao dịch'].dt.year == 2025)]
    total_orders = df_jun['Mã hóa đơn'].nunique()
    cancelled_orders = df_jun[df_jun['Status'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)]['Mã hóa đơn'].nunique()
    ans = round(cancelled_orders / total_orders * 100, 2) if total_orders > 0 else 0
```
- **Trạng thái**: ❌ SAI

## Câu 5: q_006c26c65d50 | Ngày: 2026-07-31
- **Hỏi**: thang 7/2026 co bao nhiu don co dthu tu 55.000 dong tro len
- **Gold**: 2345
- **Code**:
```python
import pandas as pd
import re

def parse_date_safe(s):
    return pd.to_datetime(s, format='%d/%m/%Y', errors='coerce')

def clean_money(s):
    return pd.to_numeric(s.astype(str).str.replace(',', '').str.replace('.', '', regex=False), errors='coerce')

# Lấy bảng chính
df = get_df_by_keyword(dfs, ['So_chi_tiet_ban_hang_1_T07_2026'])

if df is None or len(df) == 0:
    ans = None
else:
    df = df.copy()
    df['Ngày_parsed'] = parse_date_safe(df['Ngày'])
    df['Thành tiền_clean'] = clean_money(df['Thành tiền'])
    
    # Lọc tháng 7/2026
    mask = (df['Ngày_parsed'].dt.year == 2026) & (df['Ngày_parsed'].dt.month == 7)
    df_jul = df[mask]
    
    # Loại đơn hủy
    cancel_mask = df_jul['Trạng thái'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)
    df_valid = df_jul[~cancel_mask]
    
    # Tính doanh thu theo đơn
    order_rev = df_valid.groupby('Mã đơn hàng')['Thành tiền_clean'].sum()
    
    # Đếm đơn có doanh thu >= 55,000
    ans = int((order_rev >= 55000).sum())
```
- **Trạng thái**: ❌ SAI

## Câu 6: q_0088f7a0afc5 | Ngày: 2026-07-13
- **Hỏi**: Tháng 7/2025 mặt hàng Otrivin 0,1% xịt mũi chai 10ml bán được tổng cộng bao nhiêu chai?
- **Gold**: 77
## Câu 7: q_008f69128180 | Ngày: 2026-05-20
- **Hỏi**: trong thang 10/2025, ti le don huy la bnhiu %
- **Gold**: 1.21
- **Code**:
```python
df = get_df_by_keyword(dfs, ['SoBanHang_Tháng 10-2025'])
if df is None or len(df) == 0:
    ans = None
else:
    total_orders = df['Mã phiếu'].nunique()
    cancelled_orders = df[df['Ghi chú TT'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)]['Mã phiếu'].nunique()
    ans = round(cancelled_orders / total_orders * 100, 2) if total_orders > 0 else 0
```
- **Trạng thái**: ❌ SAI

## Câu 8: q_00a6e23cbacf | Ngày: 2026-08-05
- **Hỏi**: Trong tháng 1/2025, Mì Omachi sườn hầm nhập vào giá bình quân một thùng là bao nhiêu ạ?
- **Gold**: 200556
## Câu 9: q_00bb4edee433 | Ngày: 2026-09-20
- **Hỏi**: trong tổng doanh thu tháng 7/2025, phần của thuốc kê đơn là bao nhiêu phần trăm
- **Gold**: 2.27
- **Code**:
```python
import pandas as pd
import re

def parse_date_safe(s):
    return pd.to_datetime(s, format='%d/%m/%Y', errors='coerce')

def clean_money(s):
    return pd.to_numeric(s.astype(str).str.replace(',', '').str.replace('.', '').str.strip(), errors='coerce')

df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])
if df is None or len(df) == 0:
    ans = None
else:
    df_sp = get_df_by_keyword(dfs, ['DuLieuXuat_DanhSachSanPham'])
    
    df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])
    df['Tổng tiền'] = clean_money(df['Tổng tiền'])
    
    mask_t7 = (df['Ngày đặt hàng'].dt.month == 7) & (df['Ngày đặt hàng'].dt.year == 2025)
    df_t7 = df[mask_t7].copy()
    
    df_t7 = df_t7[~df_t7['Trạng thái đơn hàng'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)]
    
    if df_sp is not None and len(df_sp) > 0:
        sp_rx = df_sp[df_sp['Loại sản phẩm'].astype(str).str.lower().str.contains('kê đơn|ke don|rx', na=False)]['Tên sản phẩm'].astype(str).str.strip().unique().tolist()
        df_t7['_sp'] = df_t7['Tên sản phẩm'].astype(str).str.strip()
        df_rx = df_t7[df_t7['_sp'].isin(sp_rx)]
    else:
        df_rx = df_t7.iloc[0:0]
    
    total = df_t7['Tổng tiền'].sum()
    rx_total = df_rx['Tổng tiền'].sum()
    
    if total and total > 0:
        ans = round(rx_total / total * 100, 2)
    else:
        ans = None
```
- **Trạng thái**: ❌ SAI

## Câu 10: q_00c4e64fe706 | Ngày: 2026-09-14
- **Hỏi**: Tháng 5/2025 cửa hàng bán đc tổng cộng bao nhiêu tiền?
- **Gold**: 271866000
- **Code**:
```python
df = get_df_by_keyword(dfs, ['DanhSachHoaDonChiTiet_2'])
if df is None or len(df) == 0:
    ans = None
else:
    df_hd = get_df_by_keyword(dfs, ['DanhSachHoaDon'])
    if df_hd is None or len(df_hd) == 0:
        ans = None
    else:
        df_hd['Ngày'] = parse_date_safe(df_hd['Ngày'])
        mask = (df_hd['Ngày'].dt.year == 2025) & (df_hd['Ngày'].dt.month == 5)
        ma_hd = df_hd.loc[mask, 'Mã hóa đơn'].unique()
        df_ct = df[df['Mã hóa đơn'].isin(ma_hd)].copy()
        df_ct['Thành tiền'] = clean_money(df_ct['Thành tiền'])
        ans = int(df_ct['Thành tiền'].sum())
```
- **Lỗi**: Lỗi Runtime: 'Ngày'

