# BẮT ĐẦU QUÁ TRÌNH DẠY AI

- Thời gian: 2026-10-28 17:57:06
- Tổng số câu: 50

## Câu 1: q_001883280e83 | Ngày: 2026-09-07
- **Hỏi**: tháng này tổng giá trị các phiếu nhập hàng là bao nhiu
- **Gold**: 89526400
- **Code**:
```python
# Lấy dữ liệu phiếu nhập hàng - tìm bảng có chứa thông tin nhập hàng
# Dựa vào dữ liệu, cần tìm bảng phiếu nhập hàng
import pandas as pd

# Tìm bảng phiếu nhập hàng trong dfs
nhap_hang_keys = [k for k in dfs.keys() if 'nhập' in k.lower() or 'nhap' in k.lower() or 'import' in k.lower() or 'purchase' in k.lower()]

if not nhap_hang_keys:
    ans = None
else:
    # Lấy bảng phiếu nhập hàng đầu tiên
    df_nhap = get_df_by_keyword(dfs, [nhap_hang_keys[0]])
    
    if df_nhap is None or len(df_nhap) == 0:
        ans = None
    else:
        # Xác định cột ngày
        date_col = None
        for c in df_nhap.columns:
            if 'thời gian' in c.lower() or 'ngày' in c.lower() or 'date' in c.lower():
                date_col = c
                break
        
        # Xác định cột tiền
        money_col = None
        for c in df_nhap.columns:
            if 'tổng' in c.lower() or 'tiền' in c.lower() or 'giá trị' in c.lower() or 'amount' in c.lower() or 'total' in c.lower():
                money_col = c
                break
        
        if date_col is None or money_col is None:
            ans = None
        else:
            df_nhap = df_nhap.copy()
            df_nhap['_date'] = parse_date_safe(df_nhap[date_col])
            df_nhap['_money'] = clean_money(df_nhap[money_col])
            
            # Ngày chốt 2026-09-07, tháng này = tháng 9/2026
            target_month = 9
            target_year = 2026
            
            mask = (df_nhap['_date'].dt.month == target_month) & (df_nhap['_date'].dt.year == target_year)
            filtered = df_nhap[mask]
            
            if len(filtered) == 0:
                ans = 0
            else:
                ans = filtered['_money'].sum()
```
- **Trạng thái**: ❌ SAI (None != 89526400)

## Câu 2: q_00195e1e4049 | Ngày: 2026-05-25
- **Hỏi**: Thuốc có hoạt chất Natri clorid tháng này bán được tổng cộng bao nhiêu tiền?
- **Gold**: 2954200
- **Code**:
```python
# Lấy dữ liệu
df_hoadon = get_df_by_keyword(dfs, ['BanHang_HoaDon'])
df_thuoc = get_df_by_keyword(dfs, ['BanHang_Thuoc'])

# Ngày chốt
ngay_chot = parse_date_safe(pd.Series(['2026-05-25']))[0]

# Lọc thuốc có hoạt chất Natri clorid
df_thuoc['Hoạt chất'] = df_thuoc['Hoạt chất'].astype(str)
df_natri = df_thuoc[df_thuoc['Hoạt chất'].str.contains('Natri clorid', case=False, na=False)]
ds_ma_hh = set(normalize_id(df_natri['Mã HH']).dropna().unique())

# Chuẩn hóa ngày bán
df_hoadon['NgayBan_parsed'] = parse_date_safe(df_hoadon['Ngày bán'])

# Lọc tháng hiện tại (tháng của ngày chốt)
thang_chot = ngay_chot.month
nam_chot = ngay_chot.year
mask_thang = (df_hoadon['NgayBan_parsed'].dt.month == thang_chot) & (df_hoadon['NgayBan_parsed'].dt.year == nam_chot)
df_thang = df_hoadon[mask_thang].copy()

# Lấy chi tiết hóa đơn - cần join với bảng chi tiết
# Kiểm tra có bảng chi tiết không
try:
    df_ct = get_df_by_keyword(dfs, ['BanHang_ChiTiet'])
    has_ct = True
except Exception:
    has_ct = False

if has_ct:
    df_ct['Mã HH_norm'] = normalize_id(df_ct['Mã HH'])
    df_ct_loc = df_ct[df_ct['Mã HH_norm'].isin(ds_ma_hh)]
    # Join với hóa đơn tháng
    df_join = df_ct_loc.merge(df_thang[['Order ID']], on='Order ID', how='inner')
    # Tính tiền: ưu tiên cột thành tiền trong chi tiết
    if 'Thành tiền' in df_join.columns:
        df_join['Tien'] = clean_money(df_join['Thành tiền'])
    elif 'Tong tien' in df_join.columns:
        df_join['Tien'] = clean_money(df_join['Tong tien'])
    else:
        df_join['Tien'] = 0
    ans = df_join['Tien'].sum()
else:
    # Không có bảng chi tiết -> không xác định được
    ans = None
```
- **Lỗi**: Lỗi Runtime: 'Mã HH'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 3: q_002d03ebbded | Ngày: 2025-04-30
- **Hỏi**: Tổng doanh thu trong ngày hôm nay là bao nhiêu?
- **Gold**: 10309400
- **Code**:
```python
df_hoadon = get_df_by_keyword(dfs, ['DanhSachHoaDon_12.2025'])

if df_hoadon is not None and len(df_hoadon) > 0:
    df_hoadon['Thời gian'] = parse_date_safe(df_hoadon['Thời gian'])
    df_hoadon['Tổng tiền hàng'] = clean_money(df_hoadon['Tổng tiền hàng'])
    
    target_date = parse_date_safe(pd.Series(['2025-04-30'])).iloc[0]
    df_today = df_hoadon[df_hoadon['Thời gian'] == target_date]
    
    if len(df_today) > 0:
        ans = df_today['Tổng tiền hàng'].sum()
    else:
        ans = 0
else:
    ans = None
```
- **Trạng thái**: ❌ SAI (0 != 10309400)

## Câu 4: q_00558c1410ef | Ngày: 2026-06-24
- **Hỏi**: tỉ lệ huỷ đơn tháng 6/2025 là nhiêu %
- **Gold**: 2.08
- **Code**:
```python
# Lấy dữ liệu tháng 6/2025 - kiểm tra các bảng có sẵn
# Vì dữ liệu mẫu chỉ có tháng 10, 11, 12/2025, ta cần tìm bảng tháng 6/2025
# Thử lấy từ các bảng có sẵn và lọc theo tháng 6/2025

dfs_keys = list(dfs.keys()) if hasattr(dfs, 'keys') else []
target_keys = [k for k in dfs_keys if '6' in k and '2025' in k]

if len(target_keys) == 0:
    # Không có bảng tháng 6/2025 -> thử gộp tất cả bảng và lọc
    all_dfs = []
    for k in dfs_keys:
        try:
            d = get_df_by_keyword(dfs, [k])
            if d is not None and len(d) > 0:
                all_dfs.append(d)
        except:
            pass
    if len(all_dfs) == 0:
        ans = None
    else:
        import pandas as pd
        df_all = pd.concat(all_dfs, ignore_index=True)
        df_all['Ngày giao dịch parsed'] = parse_date_safe(df_all['Ngày giao dịch'])
        mask = (df_all['Ngày giao dịch parsed'].dt.month == 6) & (df_all['Ngày giao dịch parsed'].dt.year == 2025)
        df_june = df_all[mask]
        if len(df_june) == 0:
            ans = None
        else:
            total = len(df_june)
            cancelled = df_june['Status'].astype(str).str.lower().str.contains('huỷ|hủy|cancel|trả hàng', na=False).sum()
            ans = round(cancelled / total * 100, 2) if total > 0 else None
else:
    df = get_df_by_keyword(dfs, [target_keys[0]])
    if df is None or len(df) == 0:
        ans = None
    else:
        df['Ngày giao dịch parsed'] = parse_date_safe(df['Ngày giao dịch'])
        mask = (df['Ngày giao dịch parsed'].dt.month == 6) & (df['Ngày giao dịch parsed'].dt.year == 2025)
        df_june = df[mask]
        if len(df_june) == 0:
            ans = None
        else:
            total = len(df_june)
            cancelled = df_june['Status'].astype(str).str.lower().str.contains('huỷ|hủy|cancel|trả hàng', na=False).sum()
            ans = round(cancelled / total * 100, 2) if total > 0 else None
```
- **Trạng thái**: ❌ SAI (2.63 != 2.08)

## Câu 5: q_006c26c65d50 | Ngày: 2026-07-31
- **Hỏi**: thang 7/2026 co bao nhiu don co dthu tu 55.000 dong tro len
- **Gold**: 2345
- **Code**:
```python
# Lấy dữ liệu bảng chi tiết bán hàng tháng 7/2026
# Tìm bảng có chứa dữ liệu tháng 7/2026 - dựa trên tên bảng có thể là T07_2026
# Thử lấy các bảng có thể có
df_jul = None
for key in dfs.keys():
    if 'T07_2026' in key or 'T7_2026' in key or '07_2026' in key:
        df_jul = get_df_by_keyword(dfs, [key])
        break

if df_jul is None or len(df_jul) == 0:
    ans = None
else:
    df = df_jul.copy()
    df['Ngày_parsed'] = parse_date_safe(df['Ngày'])
    df['Thành tiền_clean'] = clean_money(df['Thành tiền'])
    
    # Lọc tháng 7/2026
    mask = (df['Ngày_parsed'].dt.year == 2026) & (df['Ngày_parsed'].dt.month == 7)
    df_jul_filtered = df[mask]
    
    if len(df_jul_filtered) == 0:
        ans = None
    else:
        # Tính doanh thu theo đơn hàng
        order_revenue = df_jul_filtered.groupby('Mã đơn hàng')['Thành tiền_clean'].sum()
        # Đếm số đơn có doanh thu >= 55,000
        ans = int((order_revenue >= 55000).sum())
```
- **Trạng thái**: ❌ SAI (2409 != 2345)

## Câu 6: q_0088f7a0afc5 | Ngày: 2026-07-13
- **Hỏi**: Tháng 7/2025 mặt hàng Otrivin 0,1% xịt mũi chai 10ml bán được tổng cộng bao nhiêu chai?
- **Gold**: 77
- **Code**:
```python
# Lấy dữ liệu sản phẩm
df_sp = get_df_by_keyword(dfs, ['DanhSachSanPham'])

# Tìm sản phẩm Otrivin 0,1% xịt mũi chai 10ml
mask_sp = df_sp['Tên hàng'].astype(str).str.contains('Otrivin', case=False, na=False) & \
          df_sp['Tên hàng'].astype(str).str.contains('0,1%', case=False, na=False) & \
          df_sp['Tên hàng'].astype(str).str.contains('10ml', case=False, na=False)
sp_match = df_sp[mask_sp]

if sp_match.empty:
    ans = None
else:
    ma_hang_list = normalize_id(sp_match['Mã hàng']).tolist()
    
    # Lấy hóa đơn tháng 7/2025 - cần tìm bảng phù hợp
    # Dữ liệu mẫu chỉ có T11, T12-2025, nhưng câu hỏi về T7/2025
    # Thử lấy bảng hóa đơn tháng 7 nếu có
    try:
        df_hd = get_df_by_keyword(dfs, ['DanhSachHoaDon_T7-2025'])
    except:
        df_hd = None
    
    if df_hd is None or df_hd.empty:
        ans = None
    else:
        # Lọc hóa đơn tháng 7/2025
        df_hd = df_hd.copy()
        df_hd['ThoiGian'] = parse_date_safe(df_hd['Thời gian'])
        mask_t7 = (df_hd['ThoiGian'].dt.month == 7) & (df_hd['ThoiGian'].dt.year == 2025)
        df_hd_t7 = df_hd[mask_t7]
        
        # Cần bảng chi tiết hóa đơn để đếm số lượng
        try:
            df_ct = get_df_by_keyword(dfs, ['ChiTietHoaDon_T7-2025'])
        except:
            df_ct = None
        
        if df_ct is None or df_ct.empty:
            ans = None
        else:
            df_ct = df_ct.copy()
            df_ct['MaHang'] = normalize_id(df_ct['Mã hàng'])
            df_ct['MaHD'] = normalize_id(df_ct['Mã hóa đơn'])
            df_hd_t7['MaHD'] = normalize_id(df_hd_t7['Mã hóa đơn'])
            
            # Join chi tiết với hóa đơn tháng 7
            merged = df_ct.merge(df_hd_t7[['MaHD']], on='MaHD', how='inner')
            
            # Lọc theo mã hàng Otrivin
            merged_otrivin = merged[merged['MaHang'].isin(ma_hang_list)]
            
            if merged_otrivin.empty:
                ans = 0
            else:
                # Đếm tổng số lượng (chai)
                if 'Số lượng' in merged_otrivin.columns:
                    ans = int(merged_otrivin['Số lượng'].astype(float).sum())
                else:
                    ans = len(merged_otrivin)
```
- **Trạng thái**: ❌ SAI (None != 77)

## Câu 7: q_008f69128180 | Ngày: 2026-05-20
- **Hỏi**: trong thang 10/2025, ti le don huy la bnhiu %
- **Gold**: 1.21
- **Code**:
```python
df = get_df_by_keyword(dfs, ['SoBanHang_Tháng 10-2025'])

if df is None or len(df) == 0:
    ans = None
else:
    df = df.copy()
    df['Ngày lập'] = parse_date_safe(df['Ngày lập'])
    df = df[df['Ngày lập'].notna()]
    df = df[(df['Ngày lập'].dt.month == 10) & (df['Ngày lập'].dt.year == 2025)]
    
    if len(df) == 0:
        ans = None
    else:
        total = len(df)
        ghi_chu = df['Ghi chú TT'].astype(str).str.strip().str.lower()
        huy_mask = ghi_chu.str.contains('hủy|huỷ|huy|cancel', na=False)
        so_huy = huy_mask.sum()
        ans = round(so_huy / total * 100, 2)
```
- **Trạng thái**: ❌ SAI (4.17 != 1.21)

## Câu 8: q_00a6e23cbacf | Ngày: 2026-08-05
- **Hỏi**: Trong tháng 1/2025, Mì Omachi sườn hầm nhập vào giá bình quân một thùng là bao nhiêu ạ?
- **Gold**: 200556
- **Code**:
```python
# Lấy dữ liệu
df_ct = get_df_by_keyword(dfs, ['DanhSachHoaDonChiTiet'])
df_hd = get_df_by_keyword(dfs, ['DuLieuBanHang_DanhSachHoaDon'])

# Chuẩn hóa ngày tháng
df_hd['Thời gian'] = parse_date_safe(df_hd['Thời gian'])

# Lọc hóa đơn tháng 1/2025
mask_hd = (df_hd['Thời gian'].dt.year == 2025) & (df_hd['Thời gian'].dt.month == 1)
df_hd_jan = df_hd[mask_hd][['Mã hóa đơn']]

# Join chi tiết với hóa đơn
df_ct['Mã hóa đơn'] = normalize_id(df_ct['Mã hóa đơn'])
df_hd_jan['Mã hóa đơn'] = normalize_id(df_hd_jan['Mã hóa đơn'])
df_merge = df_ct.merge(df_hd_jan, on='Mã hóa đơn', how='inner')

# Lọc sản phẩm Mì Omachi sườn hầm
mask_sp = df_merge['Tên hàng'].str.contains('Omachi', case=False, na=False) & \
           df_merge['Tên hàng'].str.contains('sườn hầm', case=False, na=False)
df_sp = df_merge[mask_sp].copy()

if len(df_sp) == 0:
    ans = None
else:
    # Chuẩn hóa số lượng và đơn giá
    df_sp['Số lượng'] = clean_money(df_sp['Số lượng'])
    df_sp['Đơn giá'] = clean_money(df_sp['Đơn giá'])
    
    # Tính giá bình quân một thùng
    # Đơn vị tính là thùng -> đơn giá đã là giá/thùng
    df_thung = df_sp[df_sp['Đơn vị tính'].str.lower().str.contains('thùng', na=False)]
    
    if len(df_thung) > 0:
        tong_tien = (df_thung['Số lượng'] * df_thung['Đơn giá']).sum()
        tong_sl = df_thung['Số lượng'].sum()
        ans = tong_tien / tong_sl if tong_sl > 0 else None
    else:
        # Nếu không có đơn vị thùng, dùng toàn bộ
        tong_tien = (df_sp['Số lượng'] * df_sp['Đơn giá']).sum()
        tong_sl = df_sp['Số lượng'].sum()
        ans = tong_tien / tong_sl if tong_sl > 0 else None
```
- **Trạng thái**: ❌ SAI (240000 != 200556)

## Câu 9: q_00bb4edee433 | Ngày: 2026-09-20
- **Hỏi**: trong tổng doanh thu tháng 7/2025, phần của thuốc kê đơn là bao nhiêu phần trăm
- **Gold**: 2.27
- **Code**:
```python
df_orders = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])
df_products = get_df_by_keyword(dfs, ['DuLieuXuat_DanhSachSanPham'])

df_orders['Ngày đặt hàng'] = parse_date_safe(df_orders['Ngày đặt hàng'])
df_orders['Tổng tiền'] = clean_money(df_orders['Tổng tiền'])

df_july = df_orders[
    (df_orders['Ngày đặt hàng'].dt.year == 2025) &
    (df_orders['Ngày đặt hàng'].dt.month == 7)
]

df_july = df_july[df_july['Trạng thái đơn hàng'] == 'Đã hoàn thành']

df_products['Tên sản phẩm'] = df_products['Tên sản phẩm'].astype(str).str.strip()
df_july['Tên sản phẩm'] = df_july['Tên sản phẩm'].astype(str).str.strip()

df_merged = df_july.merge(
    df_products[['Tên sản phẩm', 'Loại sản phẩm']],
    on='Tên sản phẩm',
    how='left'
)

total_revenue = df_merged['Tổng tiền'].sum()

prescription_mask = df_merged['Loại sản phẩm'].astype(str).str.lower().str.contains('kê đơn', na=False)
prescription_revenue = df_merged.loc[prescription_mask, 'Tổng tiền'].sum()

if total_revenue and total_revenue > 0:
    ans = round(prescription_revenue / total_revenue * 100, 2)
else:
    ans = None
```
- **Trạng thái**: ❌ SAI (0 != 2.27)

## Câu 10: q_00c4e64fe706 | Ngày: 2026-09-14
- **Hỏi**: Tháng 5/2025 cửa hàng bán đc tổng cộng bao nhiêu tiền?
- **Gold**: 271866000
