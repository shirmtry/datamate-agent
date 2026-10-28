# BẮT ĐẦU QUÁ TRÌNH DẠY AI

- Tổng: 20 câu

## Câu 1: q_001883280e83 | Ngày: 2026-09-07
- **Hỏi**: tháng này tổng giá trị các phiếu nhập hàng là bao nhiu
- **Gold**: 89526400
- **Code**:
```python
# Lấy bảng nhập hàng và chi tiết nhập hàng
df_nhap = get_df_by_keyword(dfs, ['DanhSachNhapHang'])
df_ct = get_df_by_keyword(dfs, ['DanhSachChiTietNhapHang'])

if df_nhap is None or len(df_nhap) == 0 or df_ct is None or len(df_ct) == 0:
    ans = None
else:
    # Xử lý ngày
    df_nhap['Thời gian'] = parse_date_safe(df_nhap['Thời gian'])
    
    # Xác định tháng hiện tại theo as_of_date
    as_of = parse_date_safe(pd.Series([as_of_date]))[0]
    thang = as_of.month
    nam = as_of.year
    
    # Lọc phiếu nhập trong tháng này
    mask = (df_nhap['Thời gian'].dt.month == thang) & (df_nhap['Thời gian'].dt.year == nam)
    df_nhap_thang = df_nhap[mask]
    
    if len(df_nhap_thang) == 0:
        ans = 0
    else:
        # Chuẩn hóa mã để join
        df_nhap_thang = df_nhap_thang.copy()
        df_nhap_thang['_key'] = normalize_id(df_nhap_thang['Mã nhập hàng'])
        
        df_ct = df_ct.copy()
        df_ct['_key'] = normalize_id(df_ct['Mã nhập hàng'])
        
        # Lọc chi tiết thuộc các phiếu nhập trong tháng
        df_ct_thang = df_ct[df_ct['_key'].isin(df_nhap_thang['_key'])]
        
        if len(df_ct_thang) == 0:
            ans = 0
        else:
            # Xử lý tiền
            df_ct_thang['Đơn giá'] = clean_money(df_ct_thang['Đơn giá'])
            df_ct_thang['Số lượng'] = pd.to_numeric(df_ct_thang['Số lượng'], errors='coerce').fillna(0)
            
            # Tính tổng giá trị
            tong = (df_ct_thang['Số lượng'] * df_ct_thang['Đơn giá']).sum()
            ans = float(tong)
```
- **Trạng thái**: ✅ ĐÚNG

## Câu 2: q_00195e1e4049 | Ngày: 2026-05-25
- **Hỏi**: Thuốc có hoạt chất Natri clorid tháng này bán được tổng cộng bao nhiêu tiền?
- **Gold**: 2954200
- **Code**:
```python
# Lấy các bảng cần thiết
df_hh = get_df_by_keyword(dfs, ['BanHang_HangHoa'])
df_thuoc = get_df_by_keyword(dfs, ['BanHang_Thuoc'])
df_ct = get_df_by_keyword(dfs, ['BanHang_ChiTietHoaDon'])
df_hd = get_df_by_keyword(dfs, ['BanHang_HoaDon'])

if df_hh is None or df_thuoc is None or df_ct is None or df_hd is None:
    ans = None
else:
    # Lọc thuốc có hoạt chất Natri clorid
    df_thuoc['Hoạt chất'] = df_thuoc['Hoạt chất'].astype(str)
    mask_nc = df_thuoc['Hoạt chất'].str.lower().str.contains('natri clorid', na=False)
    ma_hh_nc = df_thuoc.loc[mask_nc, 'Mã HH'].dropna().unique().tolist()

    if len(ma_hh_nc) == 0:
        ans = 0
    else:
        # Chuẩn hóa mã
        df_hh['ma_sp_norm'] = normalize_id(df_hh['ma_sp'])
        df_ct['Ma hang norm'] = normalize_id(df_ct['Ma hang'])
        ma_hh_nc_norm = [normalize_id(pd.Series([m])).iloc[0] for m in ma_hh_nc]

        # Lấy ma_sp tương ứng
        ma_sp_nc = df_hh.loc[df_hh['ma_sp_norm'].isin(ma_hh_nc_norm), 'ma_sp'].dropna().unique().tolist()
        ma_sp_nc_norm = [normalize_id(pd.Series([m])).iloc[0] for m in ma_sp_nc]

        # Xử lý ngày hóa đơn
        df_hd['Ngày bán'] = parse_date_safe(df_hd['Ngày bán'])
        as_of = pd.Timestamp('2026-05-25')
        start = as_of.replace(day=1)
        mask_date = (df_hd['Ngày bán'] >= start) & (df_hd['Ngày bán'] <= as_of)
        hd_thang = df_hd.loc[mask_date, ['Mã giao dịch']].copy()
        hd_thang['Mã giao dịch norm'] = normalize_id(hd_thang['Mã giao dịch'])

        # Lọc chi tiết hóa đơn
        df_ct['Mã giao dịch norm'] = normalize_id(df_ct['Mã giao dịch'])
        df_ct_filter = df_ct[df_ct['Ma hang norm'].isin(ma_sp_nc_norm)].copy()
        df_ct_filter = df_ct_filter[df_ct_filter['Mã giao dịch norm'].isin(hd_thang['Mã giao dịch norm'])]

        if len(df_ct_filter) == 0:
            ans = 0
        else:
            df_ct_filter['Thanh tien'] = clean_money(df_ct_filter['Thanh tien'])
            ans = float(df_ct_filter['Thanh tien'].sum())
```
- **Lỗi**: Lỗi Runtime: "None of [Index(['Mã giao dịch'], dtype='object')] are in the [columns]"

## Câu 3: q_002d03ebbded | Ngày: 2025-04-30
- **Hỏi**: Tổng doanh thu trong ngày hôm nay là bao nhiêu?
- **Gold**: 10309400
- **Code**:
```python
# Lấy bảng hóa đơn tháng 04.2025 (tháng chứa ngày chốt 2025-04-30)
df = get_df_by_keyword(dfs, ['DanhSachHoaDon_04.2025'])

if df is None or len(df) == 0:
    ans = None
else:
    # Xử lý ngày
    df['Thời gian'] = parse_date_safe(df['Thời gian'])
    # Xử lý tiền
    df['Tổng tiền hàng'] = clean_money(df['Tổng tiền hàng'])
    df['Giảm giá'] = clean_money(df['Giảm giá'])
    
    # Lọc hóa đơn trong ngày hôm nay (2025-04-30)
    as_of_date = pd.Timestamp('2025-04-30')
    df_today = df[df['Thời gian'].dt.normalize() == as_of_date]
    
    # Loại bỏ hóa đơn hủy
    df_today = df_today[~df_today['Trạng thái'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)]
    
    if len(df_today) == 0:
        ans = 0
    else:
        # Tổng doanh thu = Tổng tiền hàng - Giảm giá
        doanh_thu = (df_today['Tổng tiền hàng'] - df_today['Giảm giá']).sum()
        ans = doanh_thu
```
- **Trạng thái**: ❌ SAI

## Câu 4: q_00558c1410ef | Ngày: 2026-06-24
- **Hỏi**: tỉ lệ huỷ đơn tháng 6/2025 là nhiêu %
- **Gold**: 2.08
- **Code**:
```python
# Lấy bảng doanh số tháng 6/2025
df = get_df_by_keyword(dfs, ['SoBanHang_1_Thang 06 2025'])

if df is None or len(df) == 0:
    ans = None
else:
    # Chuẩn hóa cột ngày giao dịch
    df['Ngày giao dịch'] = parse_date_safe(df['Ngày giao dịch'])
    
    # Lọc dữ liệu tháng 6/2025
    df_june = df[
        (df['Ngày giao dịch'].dt.month == 6) & 
        (df['Ngày giao dịch'].dt.year == 2025)
    ]
    
    if len(df_june) == 0:
        ans = None
    else:
        # Tổng số đơn hàng (unique theo Mã hóa đơn)
        tong_don = df_june['Mã hóa đơn'].nunique()
        
        # Số đơn hủy
        don_huy = df_june[
            df_june['Status'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)
        ]['Mã hóa đơn'].nunique()
        
        # Tính tỉ lệ hủy
        if tong_don == 0:
            ans = None
        else:
            ans = round(don_huy / tong_don * 100, 2)
```
- **Trạng thái**: ❌ SAI

## Câu 5: q_006c26c65d50 | Ngày: 2026-07-31
- **Hỏi**: thang 7/2026 co bao nhiu don co dthu tu 55.000 dong tro len
- **Gold**: 2345
- **Code**:
```python
# Lấy bảng chi tiết bán hàng tháng 7/2026
df = get_df_by_keyword(dfs, ['So_chi_tiet_ban_hang_2026_T07_2026'])

if df is None or len(df) == 0:
    ans = None
else:
    # Xử lý ngày
    df['Ngày'] = parse_date_safe(df['Ngày'])
    
    # Xử lý tiền
    df['Thành tiền'] = clean_money(df['Thành tiền'])
    
    # Lọc tháng 7/2026
    df_jul = df[(df['Ngày'] >= '2026-07-01') & (df['Ngày'] <= '2026-07-31')]
    
    # Loại bỏ đơn hủy
    mask_cancel = df_jul['Trạng thái'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)
    df_valid = df_jul[~mask_cancel]
    
    # Tính doanh thu theo đơn hàng
    order_revenue = df_valid.groupby('Mã đơn hàng')['Thành tiền'].sum()
    
    # Đếm số đơn có doanh thu >= 55.000
    ans = int((order_revenue >= 55000).sum())
```
- **Trạng thái**: ❌ SAI

## Câu 6: q_0088f7a0afc5 | Ngày: 2026-07-13
- **Hỏi**: Tháng 7/2025 mặt hàng Otrivin 0,1% xịt mũi chai 10ml bán được tổng cộng bao nhiêu chai?
- **Gold**: 77
- **Code**:
```python
# Lấy bảng hóa đơn tháng 7/2025 và chi tiết hóa đơn
df_hd = get_df_by_keyword(dfs, ['DanhSachHoaDon_T07-2025'])
df_ct = get_df_by_keyword(dfs, ['DanhSachHoaDonChiTiet'])

if df_hd is None or len(df_hd) == 0 or df_ct is None or len(df_ct) == 0:
    ans = None
else:
    # Chuẩn hóa mã hóa đơn để join
    df_hd['Mã hóa đơn'] = normalize_id(df_hd['Mã hóa đơn'])
    df_ct['Mã hóa đơn'] = normalize_id(df_ct['Mã hóa đơn'])
    
    # Lọc các hóa đơn không bị hủy
    df_hd_valid = df_hd[~df_hd['Trạng thái'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)]
    
    # Join chi tiết với hóa đơn hợp lệ
    df_merged = df_ct.merge(df_hd_valid[['Mã hóa đơn']], on='Mã hóa đơn', how='inner')
    
    # Lọc theo tên hàng Otrivin 0,1% xịt mũi chai 10ml
    mask = df_merged['Tên hàng'].astype(str).str.lower().str.contains('otrivin', na=False) & \
           df_merged['Tên hàng'].astype(str).str.contains('0,1%|0.1%', na=False, regex=True) & \
           df_merged['Tên hàng'].astype(str).str.lower().str.contains('xịt mũi|xit mui', na=False) & \
           df_merged['Tên hàng'].astype(str).str.contains('10ml', na=False, case=False)
    
    df_filtered = df_merged[mask]
    
    if len(df_filtered) == 0:
        ans = 0
    else:
        df_filtered['Số lượng'] = clean_money(df_filtered['Số lượng'])
        ans = int(df_filtered['Số lượng'].sum())
```
- **Trạng thái**: ✅ ĐÚNG

## Câu 7: q_008f69128180 | Ngày: 2026-05-20
- **Hỏi**: trong thang 10/2025, ti le don huy la bnhiu %
- **Gold**: 1.21
- **Code**:
```python
# Lấy bảng bán hàng tháng 10/2025
df = get_df_by_keyword(dfs, ['SoBanHang_Tháng 10-2025'])

if df is None or len(df) == 0:
    ans = None
else:
    # Xử lý ngày
    df['Ngày lập'] = parse_date_safe(df['Ngày lập'])
    
    # Lọc theo tháng 10/2025
    df = df[(df['Ngày lập'].dt.year == 2025) & (df['Ngày lập'].dt.month == 10)]
    
    if len(df) == 0:
        ans = None
    else:
        # Tổng số đơn hàng (unique mã phiếu)
        tong_don = df['Mã phiếu'].nunique()
        
        # Số đơn hủy (dựa vào Ghi chú TT)
        don_huy = df[df['Ghi chú TT'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)]['Mã phiếu'].nunique()
        
        if tong_don == 0:
            ans = None
        else:
            ans = round(don_huy / tong_don * 100, 2)
```
- **Trạng thái**: ❌ SAI

## Câu 8: q_00a6e23cbacf | Ngày: 2026-08-05
- **Hỏi**: Trong tháng 1/2025, Mì Omachi sườn hầm nhập vào giá bình quân một thùng là bao nhiêu ạ?
- **Gold**: 200556
- **Code**:
```python
# Lấy bảng chi tiết nhập hàng và danh sách nhập hàng
df_ct = get_df_by_keyword(dfs, ['DuLieuBanHang_DanhSachChiTietNhapHang'])
df_nh = get_df_by_keyword(dfs, ['DuLieuBanHang_DanhSachNhapHang'])

if df_ct is None or len(df_ct) == 0 or df_nh is None or len(df_nh) == 0:
    ans = None
else:
    # Chuẩn hóa mã nhập hàng để join
    df_ct = df_ct.copy()
    df_nh = df_nh.copy()
    df_ct['Mã nhập hàng'] = normalize_id(df_ct['Mã nhập hàng'])
    df_nh['Mã nhập hàng'] = normalize_id(df_nh['Mã nhập hàng'])

    # Xử lý ngày
    df_nh['Thời gian'] = parse_date_safe(df_nh['Thời gian'])

    # Xử lý tiền
    df_ct['Đơn giá'] = clean_money(df_ct['Đơn giá'])
    df_ct['Số lượng'] = clean_money(df_ct['Số lượng'])

    # Lọc tháng 1/2025
    mask_time = (df_nh['Thời gian'].dt.year == 2025) & (df_nh['Thời gian'].dt.month == 1)
    df_nh_jan = df_nh[mask_time]

    # Join
    df_join = df_ct.merge(df_nh_jan[['Mã nhập hàng']], on='Mã nhập hàng', how='inner')

    # Lọc theo tên hàng chứa "Omachi" và "sườn hầm"
    mask_sp = df_join['Mã hàng'].astype(str).str.lower().str.contains('omachi', na=False) | \
              df_join['Mã hàng'].astype(str).str.lower().str.contains('sườn hầm', na=False)
    # Nếu không có cột Tên hàng trong chi tiết nhập, dùng Mã hàng; thử lọc theo cả 2
    df_filter = df_join[mask_sp]

    if len(df_filter) == 0:
        ans = None
    else:
        # Tính giá bình quân gia quyền
        tong_tien = (df_filter['Đơn giá'] * df_filter['Số lượng']).sum()
        tong_sl = df_filter['Số lượng'].sum()
        if tong_sl == 0:
            ans = None
        else:
            ans = round(tong_tien / tong_sl, 2)
```
- **Trạng thái**: ❌ SAI

## Câu 9: q_00bb4edee433 | Ngày: 2026-09-20
- **Hỏi**: trong tổng doanh thu tháng 7/2025, phần của thuốc kê đơn là bao nhiêu phần trăm
- **Gold**: 2.27
- **Code**:
```python
# Lấy bảng chi tiết đơn hàng
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])

if df is None or len(df) == 0:
    ans = None
else:
    # Xử lý ngày và tiền
    df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])
    df['Tổng tiền'] = clean_money(df['Tổng tiền'])
    
    # Lọc đơn hàng tháng 7/2025 và loại bỏ đơn hủy
    df['Trạng thái đơn hàng'] = df['Trạng thái đơn hàng'].astype(str)
    mask_huy = df['Trạng thái đơn hàng'].str.lower().str.contains('hủy|huỷ|cancel', na=False)
    df = df[~mask_huy]
    
    mask_t7 = (df['Ngày đặt hàng'].dt.year == 2025) & (df['Ngày đặt hàng'].dt.month == 7)
    df_t7 = df[mask_t7]
    
    if len(df_t7) == 0:
        ans = None
    else:
        # Lấy bảng thuốc kê đơn
        df_thuoc = get_df_by_keyword(dfs, ['DuLieuXuat_DanhSachThuoc'])
        
        if df_thuoc is None or len(df_thuoc) == 0:
            ans = None
        else:
            # Chuẩn hóa tên sản phẩm để join
            df_t7 = df_t7.copy()
            df_thuoc = df_thuoc.copy()
            df_t7['Tên sản phẩm'] = normalize_id(df_t7['Tên sản phẩm'])
            df_thuoc['Tên sản phẩm'] = normalize_id(df_thuoc['Tên sản phẩm'])
            
            # Join để lấy thông tin thuốc kê đơn
            df_merged = df_t7.merge(
                df_thuoc[['Tên sản phẩm', 'Thuốc kê đơn']],
                on='Tên sản phẩm',
                how='left'
            )
            
            # Tính tổng doanh thu tháng 7
            tong_doanh_thu = df_merged['Tổng tiền'].sum()
            
            # Tính doanh thu thuốc kê đơn
            mask_ke_don = df_merged['Thuốc kê đơn'].astype(str).str.lower().str.contains('có|yes|true|1|x', na=False)
            doanh_thu_ke_don = df_merged.loc[mask_ke_don, 'Tổng tiền'].sum()
            
            if tong_doanh_thu == 0:
                ans = None
            else:
                ans = round(doanh_thu_ke_don / tong_doanh_thu * 100, 2)
```
- **Lỗi**: Lỗi Runtime: 'Tên sản phẩm'

## Câu 10: q_00c4e64fe706 | Ngày: 2026-09-14
- **Hỏi**: Tháng 5/2025 cửa hàng bán đc tổng cộng bao nhiêu tiền?
- **Gold**: 271866000
- **Code**:
```python
# Lấy bảng hóa đơn
df_hd = get_df_by_keyword(dfs, ['DanhSachHoaDon'])

if df_hd is None or len(df_hd) == 0:
    ans = None
else:
    # Xử lý ngày
    df_hd['Thời gian'] = parse_date_safe(df_hd['Thời gian'])
    
    # Xử lý tiền
    df_hd['Tổng sau giảm giá'] = clean_money(df_hd['Tổng sau giảm giá'])
    
    # Lọc hóa đơn tháng 5/2025
    mask = (df_hd['Thời gian'].dt.year == 2025) & (df_hd['Thời gian'].dt.month == 5)
    df_may = df_hd[mask]
    
    # Loại bỏ hóa đơn hủy
    df_may = df_may[~df_may['Trạng thái'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)]
    
    if len(df_may) == 0:
        ans = 0
    else:
        ans = df_may['Tổng sau giảm giá'].sum()
```
- **Trạng thái**: ❌ SAI

## Câu 11: q_00d4d6380d03 | Ngày: 2026-06-21
- **Hỏi**: thang 6/2025 hang nao chay nhat
- **Gold**: Gạch ống 8x8x18 Tuynel
- **Code**:
```python
df = get_df_by_keyword(dfs, ['ban_hang'])

if df is None or len(df) == 0:
    ans = None
else:
    df['Ngày'] = parse_date_safe(df['Ngày'])
    df['Tổng'] = clean_money(df['Tổng'])
    
    # Lọc tháng 6/2025
    mask = (df['Ngày'].dt.year == 2025) & (df['Ngày'].dt.month == 6)
    df_t6 = df[mask]
    
    # Loại bỏ đơn hủy
    df_t6 = df_t6[~df_t6['trang_thai'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)]
    
    if len(df_t6) == 0:
        ans = None
    else:
        # Nhóm theo sản phẩm (hàng) và tính tổng doanh thu
        result = df_t6.groupby('Sản phẩm')['Tổng'].sum().nlargest(1)
        ans = result.index.tolist()
```
- **Trạng thái**: ❌ SAI

## Câu 12: q_00e9f0bed567 | Ngày: 2026-08-05
- **Hỏi**: dthu các đơn bán qua ddieenj thoại tháng 1/2025 bằng bnhiu % tổng doanh thu tháng 1/2025
- **Gold**: 5.27
- **Code**:
```python
# Lấy bảng hóa đơn
df = get_df_by_keyword(dfs, ['DuLieuBanHang_DanhSachHoaDon'])

if df is None or len(df) == 0:
    ans = None
else:
    # Xử lý ngày
    df['Thời gian'] = parse_date_safe(df['Thời gian'])
    
    # Xử lý tiền
    df['Tổng sau giảm giá'] = clean_money(df['Tổng sau giảm giá'])
    
    # Lọc tháng 1/2025
    mask_t1 = (df['Thời gian'].dt.year == 2025) & (df['Thời gian'].dt.month == 1)
    df_t1 = df[mask_t1]
    
    if len(df_t1) == 0:
        ans = None
    else:
        # Tổng doanh thu tháng 1/2025
        tong_doanh_thu = df_t1['Tổng sau giảm giá'].sum()
        
        # Doanh thu đơn bán qua điện thoại
        mask_dt = df_t1['Kênh bán'].astype(str).str.lower().str.contains('điện thoại|dien thoai|phone', na=False)
        doanh_thu_dt = df_t1[mask_dt]['Tổng sau giảm giá'].sum()
        
        if tong_doanh_thu == 0:
            ans = None
        else:
            ans = round(doanh_thu_dt / tong_doanh_thu * 100, 2)
```
- **Trạng thái**: ❌ SAI

## Câu 13: q_00eadfc5c599 | Ngày: 2026-06-02
- **Hỏi**: đếm số đơn đã huỷ trong tháng 12/2025
- **Gold**: 64
- **Code**:
```python
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])

if df is None or len(df) == 0:
    ans = None
else:
    df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])
    
    # Lọc đơn hàng trong tháng 12/2025
    mask_thang12 = (df['Ngày đặt hàng'].dt.year == 2025) & (df['Ngày đặt hàng'].dt.month == 12)
    df_thang12 = df[mask_thang12]
    
    # Đếm số đơn đã hủy
    ans = df_thang12[
        df_thang12['Trạng thái đơn hàng'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)
    ]['Mã đơn hàng'].nunique()
```
- **Trạng thái**: ✅ ĐÚNG

## Câu 14: q_0139627bccae | Ngày: 2025-10-18
- **Hỏi**: check gium hnay cua hang co bao nhiu don
- **Gold**: 107
- **Code**:
```python
# Lấy bảng chính
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])

if df is None or len(df) == 0:
    ans = None
else:
    # Xử lý ngày
    df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])
    
    # Lọc đơn hàng trong ngày chốt (as_of_date = 2025-10-18)
    as_of_date = pd.to_datetime('2025-10-18').date()
    df_today = df[df['Ngày đặt hàng'].dt.date == as_of_date]
    
    # Đếm số đơn hàng (unique mã đơn)
    ans = df_today['Mã đơn hàng'].nunique()
```
- **Trạng thái**: ❌ SAI

## Câu 15: q_0166f82c0223 | Ngày: 2026-06-02
- **Hỏi**: thang 9/2025 cua hang co bnhiu % don bi huy
- **Gold**: 1.66
- **Code**:
```python
# Lấy bảng chính
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])

if df is None or len(df) == 0:
    ans = None
else:
    # Xử lý ngày
    df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])
    
    # Lọc đơn hàng tháng 9/2025
    mask_thang9 = (df['Ngày đặt hàng'].dt.year == 2025) & (df['Ngày đặt hàng'].dt.month == 9)
    df_thang9 = df[mask_thang9]
    
    if len(df_thang9) == 0:
        ans = None
    else:
        # Tổng số đơn hàng trong tháng 9/2025
        tong_don = df_thang9['Mã đơn hàng'].nunique()
        
        # Số đơn bị hủy
        don_huy = df_thang9[
            df_thang9['Trạng thái đơn hàng'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)
        ]['Mã đơn hàng'].nunique()
        
        # Tính %
        if tong_don == 0:
            ans = None
        else:
            ans = round(don_huy / tong_don * 100, 2)
```
- **Trạng thái**: ✅ ĐÚNG

## Câu 16: q_0174cb13db2a | Ngày: 2026-09-10
- **Hỏi**: tháng này cửa hàng đã chở giao bao nhiêu đợt hàng cho khách nhỉ
- **Gold**: 290
- **Code**:
```python
# Lấy bảng phiếu giao hàng
df = get_df_by_keyword(dfs, ['Bảng kê phiếu giao hàng'])

if df is None or len(df) == 0:
    ans = None
else:
    # Xử lý ngày giao hàng
    df['Ngày giao hàng'] = parse_date_safe(df['Ngày giao hàng'])
    
    # Xác định tháng hiện tại dựa trên as_of_date
    as_of = parse_date_safe(pd.Series([as_of_date]))[0]
    start_of_month = as_of.replace(day=1)
    
    # Lọc các đợt giao trong tháng này
    mask = (df['Ngày giao hàng'] >= start_of_month) & (df['Ngày giao hàng'] <= as_of)
    df_month = df[mask]
    
    if len(df_month) == 0:
        ans = 0
    else:
        # Đếm số đợt giao hàng (mỗi đợt = 1 dòng phiếu giao)
        ans = len(df_month)
```
- **Trạng thái**: ❌ SAI

## Câu 17: q_0183529f9d61 | Ngày: 2026-05-25
- **Hỏi**: dthu 3 tháng liền nhau kết thúc ở tháng 6/2025 là bao nhiêu mỗi tháng, từ tháng cũ đến tháng mới
- **Gold**: [287435200, 346554700, 309693800]
- **Code**:
```python
# Lấy bảng hóa đơn
df = get_df_by_keyword(dfs, ['BanHang_HoaDon'])
if df is None or len(df) == 0:
    ans = None
else:
    # Xử lý ngày và tiền
    df['Ngày bán'] = parse_date_safe(df['Ngày bán'])
    df['Tong tien'] = clean_money(df['Tong tien'])
    
    # Lọc bỏ đơn hủy
    df = df[~df['Trạng thái'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)]
    
    # Lọc theo ngày chốt
    as_of = parse_date_safe(pd.Series(['2026-05-25']))[0]
    df = df[df['Ngày bán'] <= as_of]
    
    # Lấy 3 tháng liền nhau kết thúc ở tháng 6/2025: tháng 4, 5, 6 năm 2025
    df['Tháng'] = df['Ngày bán'].dt.to_period('M')
    target_months = [pd.Period('2025-04', 'M'), pd.Period('2025-05', 'M'), pd.Period('2025-06', 'M')]
    df_f = df[df['Tháng'].isin(target_months)]
    
    # Tính doanh thu mỗi tháng
    result = df_f.groupby('Tháng')['Tong tien'].sum()
    
    # Đảm bảo đủ 3 tháng, sắp xếp từ cũ đến mới
    ans = {}
    for m in target_months:
        key = str(m)
        ans[key] = float(result.get(m, 0))
```
- **Trạng thái**: ❌ SAI

## Câu 18: q_0194d8d10f17 | Ngày: 2026-08-19
- **Hỏi**: Tính đến hết ngày 19/08/2026, có bao nhiêu khách còn nợ cửa hàng?
- **Gold**: 35
- **Code**:
```python
# Lấy bảng đơn hàng
df_dh = get_df_by_keyword(dfs, ['don_hang'])
df_kh = get_df_by_keyword(dfs, ['khach_hang'])

if df_dh is None or len(df_dh) == 0:
    ans = None
else:
    # Xử lý ngày
    df_dh['NgayBan'] = parse_date_safe(df_dh['NgayBan'])
    
    # Xử lý tiền
    df_dh['Tổng bill'] = clean_money(df_dh['Tổng bill'])
    df_dh['Khách trả'] = clean_money(df_dh['Khách trả'])
    df_dh['Còn lại'] = clean_money(df_dh['Còn lại'])
    
    # Lọc đơn hàng tính đến hết ngày 19/08/2026
    as_of_date = pd.Timestamp('2026-08-19')
    df_filtered = df_dh[df_dh['NgayBan'] <= as_of_date].copy()
    
    # Loại bỏ đơn hủy nếu có cột Xử lý
    if 'Xử lý' in df_filtered.columns:
        df_filtered = df_filtered[~df_filtered['Xử lý'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)]
    
    # Tính nợ: ưu tiên cột 'Còn lại', nếu không có thì Tổng bill - Khách trả
    df_filtered['no'] = df_filtered['Còn lại'].fillna(df_filtered['Tổng bill'] - df_filtered['Khách trả'])
    
    # Nhóm theo khách hàng, tính tổng nợ
    df_no = df_filtered.groupby('Số KH')['no'].sum().reset_index()
    
    # Đếm số khách còn nợ (nợ > 0)
    ans = int((df_no['no'] > 0).sum())
```
- **Trạng thái**: ❌ SAI

## Câu 19: q_019ec94d9799 | Ngày: 2026-08-19
- **Hỏi**: 3 mặt hàng bán chạy nhất tuần này là những mặt hàng nào?
- **Gold**: ['Cà phê sữa (M)', 'Trà đào cam sả (M)', 'Cà phê đen (M)']
- **Code**:
```python
# Lấy bảng hóa đơn và chi tiết hóa đơn
df_hd = get_df_by_keyword(dfs, ['DanhSachHoaDon'])
df_ct1 = get_df_by_keyword(dfs, ['DanhSachHoaDonChiTiet_1'])
df_ct2 = get_df_by_keyword(dfs, ['DanhSachHoaDonChiTiet_2'])

if df_hd is None or len(df_hd) == 0:
    ans = None
else:
    # Xử lý ngày
    df_hd['Thời gian'] = parse_date_safe(df_hd['Thời gian'])
    
    # Xác định tuần hiện tại (tuần chứa as_of_date)
    as_of = pd.Timestamp('2026-08-19')
    # Tuần bắt đầu từ thứ 2
    start_week = as_of - pd.Timedelta(days=as_of.weekday())
    start_week = start_week.normalize()
    end_week = start_week + pd.Timedelta(days=7)
    
    # Lọc hóa đơn trong tuần, loại hủy
    df_hd_week = df_hd[
        (df_hd['Thời gian'] >= start_week) & 
        (df_hd['Thời gian'] < end_week)
    ].copy()
    
    # Loại hóa đơn hủy
    df_hd_week = df_hd_week[
        ~df_hd_week['Trạng thái'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)
    ]
    
    # Gộp chi tiết hóa đơn từ 2 bảng
    frames = []
    for df_ct in [df_ct1, df_ct2]:
        if df_ct is not None and len(df_ct) > 0:
            frames.append(df_ct[['Mã hóa đơn', 'Mã hàng', 'Tên hàng', 'Số lượng quy đổi']])
    
    if len(frames) == 0:
        ans = None
    else:
        df_ct_all = pd.concat(frames, ignore_index=True)
        
        # Chuẩn hóa mã hóa đơn để join
        df_hd_week['Mã hóa đơn'] = normalize_id(df_hd_week['Mã hóa đơn'])
        df_ct_all['Mã hóa đơn'] = normalize_id(df_ct_all['Mã hóa đơn'])
        
        # Join
        df_merged = df_ct_all.merge(
            df_hd_week[['Mã hóa đơn']], 
            on='Mã hóa đơn', 
            how='inner'
        )
        
        if len(df_merged) == 0:
            ans = None
        else:
            # Tính số lượng bán
            df_merged['Số lượng quy đổi'] = pd.to_numeric(df_merged['Số lượng quy đổi'], errors='coerce').fillna(0)
            
            # Top 3 mặt hàng bán chạy nhất
            top3 = df_merged.groupby('Tên hàng')['Số lượng quy đổi'].sum().nlargest(3)
            ans = top3.index.tolist()
```
- **Trạng thái**: ❌ SAI

## Câu 20: q_01a252a82858 | Ngày: 2026-06-02
- **Hỏi**: Ngày 14/07/2025 cửa hàng bán Cà phê muối (L) với đơn giá bao nhiêu một ly?
- **Gold**: 41000
- **Code**:
```python
# Lấy bảng chính
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])

if df is None or len(df) == 0:
    ans = None
else:
    # Xử lý ngày
    df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])
    # Xử lý tiền
    df['Giá sản phẩm'] = clean_money(df['Giá sản phẩm'])
    
    # Lọc theo ngày 14/07/2025 và sản phẩm Cà phê muối (L)
    target_date = pd.Timestamp('2025-07-14')
    mask = (df['Ngày đặt hàng'].dt.normalize() == target_date) & \
           (df['Tên sản phẩm'].astype(str).str.strip().str.lower() == 'cà phê muối (l)')
    
    filtered = df[mask]
    
    if len(filtered) == 0:
        ans = None
    else:
        # Lấy đơn giá (Giá sản phẩm là đơn giá 1 ly)
        ans = filtered['Giá sản phẩm'].iloc[0]
```
- **Trạng thái**: ✅ ĐÚNG

