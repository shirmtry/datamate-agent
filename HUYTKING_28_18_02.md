# BẮT ĐẦU QUÁ TRÌNH DẠY AI (SIÊU TIẾT KIỆM)

## Câu 1: q_001883280e83 | Ngày: 2026-09-07
- **Hỏi**: tháng này tổng giá trị các phiếu nhập hàng là bao nhiu
- **Gold**: 89526400
- **Code**:
```python
df = get_df_by_keyword(dfs, ['tên'])

# Lấy bảng phiếu nhập hàng (không có trong dữ liệu cung cấp)
# Dữ liệu chỉ có DanhSachSanPham và DanhSachHoaDon_04.2025
# Không có bảng phiếu nhập hàng -> không thể tính tổng giá trị phiếu nhập

ans = None
```
- **Trạng thái**: ❌ SAI

## Câu 2: q_00195e1e4049 | Ngày: 2026-05-25
- **Hỏi**: Thuốc có hoạt chất Natri clorid tháng này bán được tổng cộng bao nhiêu tiền?
- **Gold**: 2954200
- **Code**:
```python
df_hd = get_df_by_keyword(dfs, ['BanHang_HoaDon'])
df_ct = get_df_by_keyword(dfs, ['BanHang_ChiTietHoaDon'])

df_hd['Ngày bán'] = parse_date_safe(df_hd['Ngày bán'])
df_hd['Tong tien'] = clean_money(df_hd['Tong tien'])
df_ct['Thanh tien'] = clean_money(df_ct['Thanh tien'])

df_hd['Order ID'] = normalize_id(df_hd['Order ID'])
df_ct['Mã giao dịch'] = normalize_id(df_ct['Mã giao dịch'])
df_ct['Ma hang'] = normalize_id(df_ct['Ma hang'])

df_hd_thang = df_hd[
    (df_hd['Ngày bán'].dt.year == 2026) &
    (df_hd['Ngày bán'].dt.month == 5)
]

df_join = df_ct.merge(
    df_hd_thang[['Order ID', 'Tong tien']],
    left_on='Mã giao dịch',
    right_on='Order ID',
    how='inner'
)

mask = df_join['Ma hang'].astype(str).str.contains('Natri clorid', case=False, na=False)
ans = df_join.loc[mask, 'Thanh tien'].sum()
```
- **Trạng thái**: ❌ SAI

## Câu 3: q_002d03ebbded | Ngày: 2025-04-30
- **Hỏi**: Tổng doanh thu trong ngày hôm nay là bao nhiêu?
- **Gold**: 10309400
- **Code**:
```python
df = get_df_by_keyword(dfs, ['hóa đơn'])
df['Thời gian'] = df['Thời gian'].apply(parse_date_safe)
df['Tổng tiền hàng'] = df['Tổng tiền hàng'].apply(clean_money)
df['Giảm giá'] = df['Giảm giá'].apply(clean_money)
target_date = parse_date_safe('2025-04-30')
mask = df['Thời gian'].dt.date == target_date.date()
ans = (df.loc[mask, 'Tổng tiền hàng'] - df.loc[mask, 'Giảm giá']).sum()
```
- **Lỗi**: Lỗi Runtime: 'NoneType' object is not subscriptable
- **Trạng thái**: ❌ THẤT BẠI

## Câu 4: q_00558c1410ef | Ngày: 2026-06-24
- **Hỏi**: tỉ lệ huỷ đơn tháng 6/2025 là nhiêu %
- **Gold**: 2.08
- **Code**:
```python
df = get_df_by_keyword(dfs, ['SoBanHang_1_Thang 02 2025', 'SoBanHang_1_Thang 03 2025'])
df['Ngày giao dịch'] = df['Ngày giao dịch'].apply(parse_date_safe)
df['Mã hóa đơn'] = df['Mã hóa đơn'].apply(normalize_id)
df['Status'] = df['Status'].astype(str).str.strip().str.lower()

thang6 = df[(df['Ngày giao dịch'].dt.year == 2025) & (df['Ngày giao dịch'].dt.month == 6)]

tong_don = thang6['Mã hóa đơn'].nunique()
huy_don = thang6[thang6['Status'].str.contains('hủy|huỷ|cancel', na=False)]['Mã hóa đơn'].nunique()

ans = round(huy_don / tong_don * 100, 2) if tong_don > 0 else 0
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 5: q_006c26c65d50 | Ngày: 2026-07-31
- **Hỏi**: thang 7/2026 co bao nhiu don co dthu tu 55.000 dong tro len
- **Gold**: 2345
- **Code**:
```python
df = get_df_by_keyword(dfs, ['tên'])
df['Ngày'] = df['Ngày'].apply(parse_date_safe)
df['Doanh thu'] = df['Doanh thu'].apply(clean_money)
df['Mã đơn'] = df['Mã đơn'].apply(normalize_id)
mask = (df['Ngày'].dt.year == 2026) & (df['Ngày'].dt.month == 7) & (df['Doanh thu'] >= 55000)
ans = df[mask]['Mã đơn'].nunique()
```
- **Lỗi**: Lỗi Runtime: 'NoneType' object is not subscriptable
- **Trạng thái**: ❌ THẤT BẠI

## Câu 6: q_0088f7a0afc5 | Ngày: 2026-07-13
- **Hỏi**: Tháng 7/2025 mặt hàng Otrivin 0,1% xịt mũi chai 10ml bán được tổng cộng bao nhiêu chai?
- **Gold**: 77
- **Code**:
```python
df_sp = get_df_by_keyword(dfs, ['danhsachsanpham'])
df_hd = get_df_by_keyword(dfs, ['danhsachhoadon_t01-2025'])

df_sp['Mã hàng'] = df_sp['Mã hàng'].apply(normalize_id)
df_hd['Mã hóa đơn'] = df_hd['Mã hóa đơn'].apply(normalize_id)

sp = df_sp[df_sp['Tên hàng'].str.contains('Otrivin 0,1%', case=False, na=False) & 
           df_sp['Tên hàng'].str.contains('10ml', case=False, na=False)]

df_hd['Thời gian'] = df_hd['Thời gian'].apply(parse_date_safe)
hd_t7 = df_hd[(df_hd['Thời gian'].dt.month == 7) & (df_hd['Thời gian'].dt.year == 2025)]

ans = 0
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'astype'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 7: q_008f69128180 | Ngày: 2026-05-20
- **Hỏi**: trong thang 10/2025, ti le don huy la bnhiu %
- **Gold**: 1.21
- **Code**:
```python
df = get_df_by_keyword(dfs, ['SoBanHang_Tháng 10-2025'])
df['Ngày lập'] = df['Ngày lập'].apply(parse_date_safe)
df['Tiền'] = df['Tiền'].apply(clean_money)
df['Mã phiếu'] = df['Mã phiếu'].apply(normalize_id)

mask = (df['Ngày lập'].dt.month == 10) & (df['Ngày lập'].dt.year == 2025)
df_t10 = df[mask]

total = len(df_t10)
huy = df_t10['Ghi chú TT'].astype(str).str.lower().str.contains('hủy|huy', na=False).sum()

ans = round(huy / total * 100, 2) if total > 0 else 0
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 8: q_00a6e23cbacf | Ngày: 2026-08-05
- **Hỏi**: Trong tháng 1/2025, Mì Omachi sườn hầm nhập vào giá bình quân một thùng là bao nhiêu ạ?
- **Gold**: 200556
## Câu 9: q_00bb4edee433 | Ngày: 2026-09-20
- **Hỏi**: trong tổng doanh thu tháng 7/2025, phần của thuốc kê đơn là bao nhiêu phần trăm
- **Gold**: 2.27
- **Code**:
```python
df = get_df_by_keyword(dfs, ['tên'])
df['Ngày đặt hàng'] = df['Ngày đặt hàng'].apply(parse_date_safe)
df['Tổng tiền'] = df['Tổng tiền'].apply(clean_money)
df['Tên sản phẩm'] = df['Tên sản phẩm'].apply(normalize_id)

df_thang7 = df[(df['Ngày đặt hàng'].dt.year == 2025) & (df['Ngày đặt hàng'].dt.month == 7)]

df_thuoc = get_df_by_keyword(dfs, ['quy đổi'])
df_thuoc['Tên sản phẩm'] = df_thuoc['Tên sản phẩm'].apply(normalize_id)

thuoc_ke_don = df_thuoc[df_thuoc['Đơn vị quy đổi'].str.contains('kê đơn', case=False, na=False)]['Tên sản phẩm'].unique()

df_thang7['La_thuoc_ke_don'] = df_thang7['Tên sản phẩm'].isin(thuoc_ke_don)

tong_doanh_thu = df_thang7['Tổng tiền'].sum()
doanh_thu_thuoc_ke_don = df_thang7[df_thang7['La_thuoc_ke_don']]['Tổng tiền'].sum()

ans = (doanh_thu_thuoc_ke_don / tong_doanh_thu * 100) if tong_doanh_thu != 0 else 0
```
- **Lỗi**: Lỗi Runtime: 'NoneType' object is not subscriptable
- **Trạng thái**: ❌ THẤT BẠI

## Câu 10: q_00c4e64fe706 | Ngày: 2026-09-14
- **Hỏi**: Tháng 5/2025 cửa hàng bán đc tổng cộng bao nhiêu tiền?
- **Gold**: 271866000
- **Code**:
```python
df_hd = get_df_by_keyword(dfs, ['hóa đơn'])
df_hd['Thời gian'] = parse_date_safe(df_hd['Thời gian'])
mask = (df_hd['Thời gian'].dt.year == 2025) & (df_hd['Thời gian'].dt.month == 5)
df_may = df_hd[mask]
ans = clean_money(df_may['Tổng sau giảm giá']).sum()
```
- **Lỗi**: Lỗi Runtime: 'NoneType' object is not subscriptable
- **Trạng thái**: ❌ THẤT BẠI

## Câu 11: q_00d4d6380d03 | Ngày: 2026-06-21
- **Hỏi**: thang 6/2025 hang nao chay nhat
- **Gold**: Gạch ống 8x8x18 Tuynel
- **Code**:
```python
df = get_df_by_keyword(dfs, ['ban_hang'])
df['Ngày'] = df['Ngày'].apply(parse_date_safe)
df['Tổng'] = df['Tổng'].apply(clean_money)
df['Sản phẩm'] = df['Sản phẩm'].apply(normalize_id)
mask = (df['Ngày'].dt.year == 2025) & (df['Ngày'].dt.month == 6)
df6 = df[mask]
ans = df6.groupby('Sản phẩm')['Tổng'].sum().sort_values(ascending=False).head(1)
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 12: q_00e9f0bed567 | Ngày: 2026-08-05
- **Hỏi**: dthu các đơn bán qua ddieenj thoại tháng 1/2025 bằng bnhiu % tổng doanh thu tháng 1/2025
- **Gold**: 5.27
- **Code**:
```python
df = get_df_by_keyword(dfs, ['DanhSachHoaDon'])
df['Thời gian'] = parse_date_safe(df['Thời gian'])
df['Tổng sau giảm giá'] = clean_money(df['Tổng sau giảm giá'])

df_t1 = df[(df['Thời gian'].dt.year == 2025) & (df['Thời gian'].dt.month == 1)]

tong_dt = df_t1['Tổng sau giảm giá'].sum()

df_dt = df_t1[df_t1['Kênh bán'].astype(str).str.lower().str.contains('điện thoại|dien thoai', na=False)]
dt_dt = df_dt['Tổng sau giảm giá'].sum()

ans = (dt_dt / tong_dt * 100) if tong_dt != 0 else 0
```
- **Lỗi**: Lỗi Runtime: 'Thời gian'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 13: q_00eadfc5c599 | Ngày: 2026-06-02
- **Hỏi**: đếm số đơn đã huỷ trong tháng 12/2025
- **Gold**: 64
- **Code**:
```python
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])
df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])
mask = (df['Ngày đặt hàng'].dt.month == 12) & (df['Ngày đặt hàng'].dt.year == 2025) & (df['Trạng thái đơn hàng'].astype(str).str.strip().str.lower().isin(['đã huỷ', 'đã hủy', 'hủy', 'huỷ', 'cancelled', 'canceled']))
ans = df.loc[mask, 'Mã đơn hàng'].nunique()
```
- **Trạng thái**: ĐÚNG

## Câu 14: q_0139627bccae | Ngày: 2025-10-18
- **Hỏi**: check gium hnay cua hang co bao nhiu don
- **Gold**: 107
- **Code**:
```python
df = get_df_by_keyword(dfs, ['tên'])
df['Ngày'] = df['Ngày'].apply(parse_date_safe)
df_hom_nay = df[df['Ngày'] == parse_date_safe('2025-10-18')]
ans = len(df_hom_nay)
```
- **Lỗi**: Lỗi Runtime: 'NoneType' object is not subscriptable
- **Trạng thái**: ❌ THẤT BẠI

## Câu 15: q_0166f82c0223 | Ngày: 2026-06-02
- **Hỏi**: thang 9/2025 cua hang co bnhiu % don bi huy
- **Gold**: 1.66
- **Code**:
```python
df = get_df_by_keyword(dfs, ['tên'])
df['Ngày'] = df['Ngày'].apply(parse_date_safe)
df_thang9 = df[(df['Ngày'].dt.year == 2025) & (df['Ngày'].dt.month == 9)]
tong_don = len(df_thang9)
don_huy = len(df_thang9[df_thang9['Trạng thái'].str.contains('hủy|huỷ|Hủy|Huỷ', na=False)])
ans = (don_huy / tong_don * 100) if tong_don > 0 else 0
```
- **Lỗi**: Lỗi Runtime: 'NoneType' object is not subscriptable
- **Trạng thái**: ❌ THẤT BẠI

## Câu 16: q_0174cb13db2a | Ngày: 2026-09-10
- **Hỏi**: tháng này cửa hàng đã chở giao bao nhiêu đợt hàng cho khách nhỉ
- **Gold**: 290
- **Code**:
```python
df = get_df_by_keyword(dfs, ['phiếu giao hàng'])
df['Ngày giao hàng'] = df['Ngày giao hàng'].apply(parse_date_safe)
df['Mã đơn hàng'] = df['Mã đơn hàng'].apply(normalize_id)
df['Lần giao'] = df['Lần giao'].apply(normalize_id)
current_month = parse_date_safe('2026-09-10').replace(day=1)
df_month = df[(df['Ngày giao hàng'] >= current_month) & (df['Ngày giao hàng'] <= parse_date_safe('2026-09-10'))]
ans = df_month[['Mã đơn hàng', 'Lần giao']].drop_duplicates().shape[0]
```
- **Lỗi**: Lỗi Runtime: 'NoneType' object is not subscriptable
- **Trạng thái**: ❌ THẤT BẠI

## Câu 17: q_0183529f9d61 | Ngày: 2026-05-25
- **Hỏi**: dthu 3 tháng liền nhau kết thúc ở tháng 6/2025 là bao nhiêu mỗi tháng, từ tháng cũ đến tháng mới
- **Gold**: [287435200, 346554700, 309693800]
- **Code**:
```python
df = get_df_by_keyword(dfs, ['BanHang_LichSuGia'])
df['Ngày áp dụng'] = df['Ngày áp dụng'].apply(parse_date_safe)
df['Giá mới'] = df['Giá mới'].apply(clean_money)
df['Mã sản phẩm'] = df['Mã sản phẩm'].apply(normalize_id)

end_date = parse_date_safe('2025-06-30')
start_date = parse_date_safe('2025-04-01')

df_period = df[(df['Ngày áp dụng'] >= start_date) & (df['Ngày áp dụng'] <= end_date)].copy()
df_period['Tháng'] = df_period['Ngày áp dụng'].dt.to_period('M')

df_sorted = df_period.sort_values(['Mã sản phẩm', 'Ngày áp dụng'])
df_last = df_sorted.groupby(['Mã sản phẩm', 'Tháng'], as_index=False).last()

ans = df_last.groupby('Tháng')['Giá mới'].sum().reset_index()
ans['Tháng'] = ans['Tháng'].astype(str)
ans = ans.sort_values('Tháng').reset_index(drop=True)
```
- **Lỗi**: Lỗi Runtime: 'Timestamp' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 18: q_0194d8d10f17 | Ngày: 2026-08-19
- **Hỏi**: Tính đến hết ngày 19/08/2026, có bao nhiêu khách còn nợ cửa hàng?
- **Gold**: 35
- **Code**:
```python
df_kh = get_df_by_keyword(dfs, ['khach_hang'])
df_dh = get_df_by_keyword(dfs, ['don_hang'])

df_dh['NgayBan'] = parse_date_safe(df_dh['NgayBan'])
df_dh['Còn lại'] = clean_money(df_dh['Còn lại'])
df_dh['Tổng bill'] = clean_money(df_dh['Tổng bill'])
df_dh['Khách trả'] = clean_money(df_dh['Khách trả'])

df_dh_f = df_dh[df_dh['NgayBan'] <= parse_date_safe('2026-08-19')].copy()

df_dh_f['ma_kh'] = df_dh_f['Số KH'].apply(normalize_id)
df_kh['ma_kh'] = df_kh['ma_kh'].apply(normalize_id)

no_theo_kh = df_dh_f.groupby('ma_kh')['Còn lại'].sum().reset_index()
no_theo_kh = no_theo_kh[no_theo_kh['Còn lại'] > 0]

ans = no_theo_kh['ma_kh'].nunique()
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 19: q_019ec94d9799 | Ngày: 2026-08-19
- **Hỏi**: 3 mặt hàng bán chạy nhất tuần này là những mặt hàng nào?
- **Gold**: ['Cà phê sữa (M)', 'Trà đào cam sả (M)', 'Cà phê đen (M)']
- **Code**:
```python
df_sp = get_df_by_keyword(dfs, ['tên'])
df_ton = get_df_by_keyword(dfs, ['tồn'])

df_sp['Mã hàng'] = normalize_id(df_sp['Mã hàng'])
df_ton['Mã hàng'] = normalize_id(df_ton['Mã hàng'])

df_sp['Thời gian tạo'] = parse_date_safe(df_sp['Thời gian tạo'])
df_ton['Tồn cuối kỳ'] = clean_money(df_ton['Tồn cuối kỳ'])

ngay_chot = parse_date_safe('2026-08-19')
tuan_truoc = ngay_chot - pd.Timedelta(days=7)

df_ban = df_sp[df_sp['Được bán trực tiếp'].astype(str).str.lower().isin(['true', '1', 'có', 'yes'])]
df_ban = df_ban[(df_ban['Thời gian tạo'] >= tuan_truoc) & (df_ban['Thời gian tạo'] <= ngay_chot)]

df_join = df_ban.merge(df_ton[['Mã hàng', 'Tồn cuối kỳ']], on='Mã hàng', how='left')
df_join['Tồn cuối kỳ'] = df_join['Tồn cuối kỳ'].fillna(0)

df_join = df_join.sort_values('Tồn cuối kỳ', ascending=False)
ans = df_join[['Mã hàng', 'Tên hàng', 'Tồn cuối kỳ']].head(3)
```
- **Lỗi**: Lỗi Runtime: 'NoneType' object is not subscriptable
- **Trạng thái**: ❌ THẤT BẠI

## Câu 20: q_01a252a82858 | Ngày: 2026-06-02
- **Hỏi**: Ngày 14/07/2025 cửa hàng bán Cà phê muối (L) với đơn giá bao nhiêu một ly?
- **Gold**: 41000
- **Code**:
```python
df = get_df_by_keyword(dfs, ['tên'])
df['Ngày đặt hàng'] = df['Ngày đặt hàng'].apply(parse_date_safe)
df['Giá sản phẩm'] = df['Giá sản phẩm'].apply(clean_money)
df['Tên sản phẩm'] = df['Tên sản phẩm'].astype(str).str.strip()
mask = (df['Ngày đặt hàng'] == parse_date_safe('2025-07-14')) & (df['Tên sản phẩm'].str.lower() == 'cà phê muối (l)')
ans = df.loc[mask, 'Giá sản phẩm'].tolist()
```
- **Lỗi**: Lỗi Runtime: 'NoneType' object is not subscriptable
- **Trạng thái**: ❌ THẤT BẠI

## Câu 21: q_01a28f2233bd | Ngày: 2026-07-31
- **Hỏi**: gia ban mot ly soda chanh day (m) vao ngay 01/12/2025 la bn
- **Gold**: 37000
- **Code**:
```python
df = get_df_by_keyword(dfs, ['tên'])
df['Tên hàng hóa'] = df['Tên hàng hóa'].astype(str)
mask = df['Tên hàng hóa'].str.lower().str.contains('soda chanh', na=False)
df_soda = df[mask].copy()
df_soda['Giá bán'] = df_soda['Giá bán'].apply(clean_money)
ans = df_soda['Giá bán'].iloc[0] if len(df_soda) > 0 else None
```
- **Lỗi**: Lỗi Runtime: 'NoneType' object is not subscriptable
- **Trạng thái**: ❌ THẤT BẠI

## Câu 22: q_01a47607f90c | Ngày: 2026-08-11
- **Hỏi**: tổng dthu trong ngày hôm nay là bao nhiêu vaayj
- **Gold**: 39793500
- **Code**:
```python
df = get_df_by_keyword(dfs, ['DanhSachHoaDon_04.2025', 'DanhSachHoaDon_05.2025'])
df['Thời gian'] = df['Thời gian'].apply(parse_date_safe)
df['Tổng sau giảm giá'] = df['Tổng sau giảm giá'].apply(clean_money)
target = parse_date_safe('2026-08-11')
mask = df['Thời gian'].apply(lambda x: x is not None and x.date() == target.date())
ans = df.loc[mask, 'Tổng sau giảm giá'].sum()
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 23: q_01b914589609 | Ngày: 2025-02-19
- **Hỏi**: Cho tôi biết dthu 30 ngày gần nhất
- **Gold**: 730984600
- **Code**:
```python
df = get_df_by_keyword(dfs, ['SoBanHang_Tháng 01-2025'])
df['Ngày lập'] = df['Ngày lập'].apply(parse_date_safe)
df['Tiền'] = df['Tiền'].apply(clean_money)
end_date = parse_date_safe('2025-02-19')
start_date = end_date - pd.Timedelta(days=30)
mask = (df['Ngày lập'] >= start_date) & (df['Ngày lập'] <= end_date)
ans = df.loc[mask, 'Tiền'].sum()
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 24: q_01bba93199de | Ngày: 2026-08-29
- **Hỏi**: Doanh thu tháng 4/2026 bao nhiêu?
- **Gold**: 1380833500
- **Code**:
```python
df = get_df_by_keyword(dfs, ['tên'])

ans = None
```
- **Trạng thái**: ❌ SAI

## Câu 25: q_0266c6b24cbf | Ngày: 2026-09-14
- **Hỏi**: Tháng 5/2026 giá nhập bình quân một hộp Bánh croissant là bao nhiêu vậy?
- **Gold**: 92897
- **Code**:
```python
df = get_df_by_keyword(dfs, ['tên'])
df['Ngày'] = df['Mã hóa đơn'].apply(parse_date_safe)
df['Đơn giá'] = df['Đơn giá'].apply(clean_money)
df['Số lượng'] = df['Số lượng'].apply(clean_money)
df['Mã hàng'] = df['Mã hàng'].apply(normalize_id)
mask = (df['Tên hàng'].str.contains('croissant', case=False, na=False)) & \
       (df['Ngày'].dt.year == 2026) & (df['Ngày'].dt.month == 5)
df_f = df[mask]
ans = (df_f['Đơn giá'] * df_f['Số lượng']).sum() / df_f['Số lượng'].sum() if df_f['Số lượng'].sum() != 0 else 0
```
- **Lỗi**: Lỗi Runtime: 'NoneType' object is not subscriptable
- **Trạng thái**: ❌ THẤT BẠI

## Câu 26: q_026fa17395ed | Ngày: 2026-05-25
- **Hỏi**: Tính đến hết ngày 25/05/2026, khách hàng còn nợ cửa hàng tổng cộng bao nhiêu tiền?
- **Gold**: 948973
- **Code**:
```python
df_hd = get_df_by_keyword(dfs, ['BanHang_HoaDon'])
df_kh = get_df_by_keyword(dfs, ['BanHang_KhachHang'])

df_hd['Ngày bán'] = parse_date_safe(df_hd['Ngày bán'])
df_hd['Còn nợ'] = clean_money(df_hd['Còn nợ'])

df_hd['Mã KH mua'] = normalize_id(df_hd['Mã KH mua'])
df_kh['Customer ID'] = normalize_id(df_kh['Customer ID'])

mask = df_hd['Ngày bán'] <= parse_date_safe('2026-05-25')
df_filtered = df_hd[mask]

ans = df_filtered['Còn nợ'].sum()
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 27: q_026fabde15fc | Ngày: 2026-07-09
- **Hỏi**: Cho hỏi tổng doanh thu quý 2/2026 là bao nhiêu?
- **Gold**: 518445500
- **Code**:
```python
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])
df['Ngày đặt hàng'] = df['Ngày đặt hàng'].apply(parse_date_safe)
df['Tổng tiền'] = df['Tổng tiền'].apply(clean_money)
df['Mã đơn hàng'] = df['Mã đơn hàng'].apply(normalize_id)
mask = (df['Ngày đặt hàng'] >= parse_date_safe('2026-04-01')) & (df['Ngày đặt hàng'] <= parse_date_safe('2026-06-30'))
ans = df.loc[mask, 'Tổng tiền'].sum()
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 28: q_0271d9f39fde | Ngày: 2026-07-31
- **Hỏi**: tháng 5/2026 cửa hàng có nhiêu % đơn bị huỷ
- **Gold**: 2.19
- **Code**:
```python
df = get_df_by_keyword(dfs, ['So_chi_tiet_ban_hang_1_T04_2025'])
df['Ngày'] = df['Ngày'].apply(parse_date_safe)
df['Mã đơn hàng'] = df['Mã đơn hàng'].apply(normalize_id)
df['Trạng thái'] = df['Trạng thái'].astype(str).str.strip().str.lower()

mask = (df['Ngày'].dt.year == 2026) & (df['Ngày'].dt.month == 5)
df_may = df[mask]

total_orders = df_may['Mã đơn hàng'].nunique()
cancelled_orders = df_may[df_may['Trạng thái'].str.contains('hủy|huỷ|cancel', na=False)]['Mã đơn hàng'].nunique()

ans = (cancelled_orders / total_orders * 100) if total_orders > 0 else 0
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 29: q_0279f675859e | Ngày: 2026-08-19
- **Hỏi**: thang 7/2025, cac khach thuoc nhom than thiet mua tong cong bao nhiu tien hang
- **Gold**: 46871000
## Câu 30: q_0283688e44df | Ngày: 2025-06-20
- **Hỏi**: Cho hỏi tuần trước riêng ca chiều bán được tổng cộng bao nhiêu tiền?
- **Gold**: 109181000
- **Code**:
```python
df = get_df_by_keyword(dfs, ['DanhSachHoaDon_04.2025', 'DanhSachHoaDon_05.2025'])
df['Thời gian'] = df['Thời gian'].apply(parse_date_safe)
df['Tổng sau giảm giá'] = df['Tổng sau giảm giá'].apply(clean_money)
end_date = parse_date_safe('2025-06-20')
start_date = end_date - pd.Timedelta(days=7)
df_week = df[(df['Thời gian'] >= start_date) & (df['Thời gian'] < end_date)]
df_week['Giờ'] = df_week['Thời gian'].dt.hour
df_afternoon = df_week[(df_week['Giờ'] >= 12) & (df_week['Giờ'] < 18)]
ans = df_afternoon['Tổng sau giảm giá'].sum()
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 31: q_0285dfd1bb28 | Ngày: 2026-07-28
- **Hỏi**: Doanh thu trung bình trên một đơn tháng 3/2025 là bao nhiêu ạ?
- **Gold**: 522915
## Câu 32: q_028dcfb561ea | Ngày: 2026-09-10
- **Hỏi**: Tháng 6/2026 khách mua từ 4 đơn trở lên chiếm bao nhiêu % số khách đã mua nhỉ?
- **Gold**: 23.77
- **Code**:
```python
df = get_df_by_keyword(dfs, ['chi_tiet_ban_hang'])
df['Ngày'] = df['Ngày'].apply(parse_date_safe)
df['Mã đơn hàng'] = df['Mã đơn hàng'].apply(normalize_id)
df['Khách hàng'] = df['Khách hàng'].apply(normalize_id)

df_jun = df[(df['Ngày'] >= pd.Timestamp('2026-06-01')) & (df['Ngày'] <= pd.Timestamp('2026-06-30'))]

don_per_kh = df_jun.groupby('Khách hàng')['Mã đơn hàng'].nunique()

tong_kh = don_per_kh.shape[0]
kh_4plus = (don_per_kh >= 4).sum()

ans = kh_4plus / tong_kh * 100 if tong_kh > 0 else 0
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 33: q_02a28b3629be | Ngày: 2026-07-09
- **Hỏi**: Cho hỏi số đơn bị huỷ trong tháng 8 năm 2025 là bao nhiêu?
- **Gold**: 32
- **Code**:
```python
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet_04.2025', 'DonHang_ChiTiet_05.2025'])
df['Ngày đặt hàng'] = df['Ngày đặt hàng'].apply(parse_date_safe)
df['Trạng thái đơn hàng'] = df['Trạng thái đơn hàng'].astype(str).str.strip().str.lower()
df['Mã đơn hàng'] = df['Mã đơn hàng'].apply(normalize_id)
mask = (df['Ngày đặt hàng'].dt.year == 2025) & (df['Ngày đặt hàng'].dt.month == 8) & (df['Trạng thái đơn hàng'].str.contains('huỷ|hủy|cancel', na=False))
ans = df.loc[mask, 'Mã đơn hàng'].nunique()
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 34: q_02a70ea566f1 | Ngày: 2026-07-31
- **Hỏi**: Top 3 sp bán nhiều nhất tháng 3 năm 2026 là những gì?
- **Gold**: ['Cà phê sữa (M)', 'Trà đào cam sả (M)', 'Cà phê đen (M)']
## Câu 35: q_02b4a032b9f3 | Ngày: 2026-06-12
- **Hỏi**: Trong tháng 11/2025, tỉ lệ đơn huỷ là bao nhiêu phần trăm?
- **Gold**: 1.17
- **Code**:
```python
df = get_df_by_keyword(dfs, ['hóa đơn'])
df['Thời gian'] = df['Thời gian'].apply(parse_date_safe)
df_nov = df[(df['Thời gian'].dt.year == 2025) & (df['Thời gian'].dt.month == 11)]
total = len(df_nov)
cancelled = len(df_nov[df_nov['Trạng thái'].astype(str).str.strip().str.lower().isin(['đã hủy', 'hủy', 'đã huỷ', 'huỷ', 'cancelled', 'canceled'])])
ans = (cancelled / total * 100) if total > 0 else 0
```
- **Lỗi**: Lỗi Runtime: 'NoneType' object is not subscriptable
- **Trạng thái**: ❌ THẤT BẠI

## Câu 36: q_02b5f208ee57 | Ngày: 2026-05-25
- **Hỏi**: Từ ngày 16/03/2025, Fugacar 500mg hộp 1 viên tăng giá lên 23.000đ. So 7 ngày kể từ ngày 16/03/2025 với 7 ngày ngay trước đó, số viên bán ra thay đổi bao nhiêu phần trăm nhỉ?
- **Gold**: 69.57
## Câu 37: q_02b7cc8b174d | Ngày: 2026-07-28
- **Hỏi**: Xem giúp tháng 2/2026 nhóm hải sản chiếm bao nhiêu % doanh thu?
- **Gold**: 9.37
- **Code**:
```python
df_sp = get_df_by_keyword(dfs, ['san_pham'])
df_tt = get_df_by_keyword(dfs, ['thanh_toan'])

df_sp['_id'] = df_sp['Mã sản phẩm bán'].apply(normalize_id)
df_sp['_cat'] = df_sp['Danh mục'].astype(str).str.strip().str.lower()

df_tt['_date'] = df_tt['Ngày thu'].apply(parse_date_safe)
df_tt['_val'] = df_tt['Giá trị'].apply(clean_money)
df_tt['_id'] = df_tt['Mã GD'].apply(normalize_id)

mask = (df_tt['_date'].dt.year == 2026) & (df_tt['_date'].dt.month == 2)
df_feb = df_tt[mask]

merged = df_feb.merge(df_sp[['_id', '_cat']], on='_id', how='left')

total = merged['_val'].sum()
seafood = merged[merged['_cat'].str.contains('hải sản', na=False)]['_val'].sum()

ans = (seafood / total * 100) if total else 0
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'astype'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 38: q_02eb42db6665 | Ngày: 2026-05-11
- **Hỏi**: tháng 5/2025 hàng nào bán chạy nhất
- **Gold**: Bia Tiger lon
- **Code**:
```python
df = get_df_by_keyword(dfs, ['ban_hang'])
df['Ngày bán'] = df['Ngày bán'].apply(parse_date_safe)
df['SL bán'] = df['SL bán'].apply(clean_money)
df['Hàng bán'] = df['Hàng bán'].apply(normalize_id)

mask = (df['Ngày bán'].dt.year == 2025) & (df['Ngày bán'].dt.month == 5)
df_may = df[mask]

ans = (
    df_may.groupby('Hàng bán')['SL bán']
    .sum()
    .sort_values(ascending=False)
    .head(1)
)
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 39: q_02ed16421456 | Ngày: 2026-06-24
- **Hỏi**: tháng 8/2025 quán bán đc bn ly size m
- **Gold**: 5604
- **Code**:
```python
df = get_df_by_keyword(dfs, ['SoBanHang_1_Thang 02 2025', 'SoBanHang_1_Thang 03 2025'])
df['Ngày giao dịch'] = df['Ngày giao dịch'].apply(parse_date_safe)
df['so_luong'] = df['so_luong'].apply(clean_money)
mask = (
    (df['Ngày giao dịch'].dt.year == 2025) &
    (df['Ngày giao dịch'].dt.month == 8) &
    (df['Hàng'].astype(str).str.lower().str.contains('size m', na=False))
)
ans = df.loc[mask, 'so_luong'].sum()
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 40: q_02f8f6235ddb | Ngày: 2026-05-16
- **Hỏi**: coi gium trong thang 5 nam 2025 cua hang ban duoc may kg thep cuon phi 6 hoa phat
- **Gold**: 130
- **Code**:
```python
df = get_df_by_keyword(dfs, ['chi_tiet_ban_hang'])
df['Ngày'] = df['Ngày'].apply(parse_date_safe)
df['Số lượng quy đổi'] = df['Số lượng quy đổi'].apply(clean_money)
df['Tên hàng hóa'] = df['Tên hàng hóa'].astype(str).str.strip()
mask = (
    (df['Ngày'].dt.year == 2025) &
    (df['Ngày'].dt.month == 5) &
    (df['Tên hàng hóa'].str.contains('thép cuộn phi 6', case=False, na=False)) &
    (df['Tên hàng hóa'].str.contains('hòa phát', case=False, na=False))
)
ans = df.loc[mask, 'Số lượng quy đổi'].sum()
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 41: q_03766ac30505 | Ngày: 2026-09-10
- **Hỏi**: Quý 4/2025 cửa hàng có bao nhiêu đơn hàng ạ?
- **Gold**: 3238
- **Code**:
```python
df = get_df_by_keyword(dfs, ['chi_tiet_ban_hang'])
df['Ngày'] = df['Ngày'].apply(parse_date_safe)
df_q4 = df[(df['Ngày'] >= parse_date_safe('2025-10-01')) & (df['Ngày'] <= parse_date_safe('2025-12-31'))]
ans = df_q4['Mã đơn hàng'].apply(normalize_id).nunique()
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 42: q_03a446be8b75 | Ngày: 2026-09-20
- **Hỏi**: trong thang 2/2025, ti le don huy la bao nhieu %
- **Gold**: None
- **Code**:
```python
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])
df['Ngày đặt hàng'] = df['Ngày đặt hàng'].apply(parse_date_safe)
df_thang2 = df[(df['Ngày đặt hàng'].dt.year == 2025) & (df['Ngày đặt hàng'].dt.month == 2)]
tong_don = len(df_thang2)
don_huy = len(df_thang2[df_thang2['Trạng thái đơn hàng'].str.strip().str.lower().isin(['hủy', 'huỷ', 'đã hủy', 'đã huỷ', 'cancelled', 'canceled'])])
ans = round(don_huy / tong_don * 100, 2) if tong_don > 0 else 0
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 43: q_03cf8b6c4b16 | Ngày: 2026-06-24
- **Hỏi**: thang 3/2026 hang nuoc ep dua hau (l) thu ve bao nhieu tien ha
- **Gold**: 4012000
- **Code**:
```python
df = get_df_by_keyword(dfs, ['tên'])
df['Ngày giao dịch'] = df['Ngày giao dịch'].apply(parse_date_safe)
df['Trị giá'] = df['Trị giá'].apply(clean_money)
df['Hàng'] = df['Hàng'].astype(str).str.strip().str.lower()
mask = (
    (df['Ngày giao dịch'].dt.year == 2026) &
    (df['Ngày giao dịch'].dt.month == 3) &
    (df['Hàng'].str.contains('nước ép dưa hấu', na=False))
)
ans = df.loc[mask, 'Trị giá'].sum()
```
- **Lỗi**: Lỗi Runtime: 'NoneType' object is not subscriptable
- **Trạng thái**: ❌ THẤT BẠI

## Câu 44: q_03d662023a15 | Ngày: 2026-09-03
- **Hỏi**: trong thang 9/2025, cua hang co may don o trang thai huy
- **Gold**: 23
- **Code**:
```python
df = get_df_by_keyword(dfs, ['Bao_cao_ban_hang_So_chi_tiet_ban_hang'])
df['Ngày'] = df['Ngày'].apply(parse_date_safe)
df['Mã đơn hàng'] = df['Mã đơn hàng'].apply(normalize_id)
mask = (df['Ngày'].dt.month == 9) & (df['Ngày'].dt.year == 2025) & (df['Trạng thái'].astype(str).str.strip().str.lower() == 'hủy')
ans = df.loc[mask, 'Mã đơn hàng'].nunique()
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 45: q_040c9dd7f4de | Ngày: 2026-09-03
- **Hỏi**: Tháng 9/2025 top 5 hàng bán chạy nhất là gì?
- **Gold**: ['Xi măng Hà Tiên PCB40 bao 50kg', 'Gạch ống 8x8x18 Tuynel', 'Xi măng INSEE Power-S bao 50kg', 'Băng keo điện Nano 20 yard', 'Ống PVC Bình Minh D32 cây 4m']
- **Code**:
```python
df = get_df_by_keyword(dfs, ['Bảng kê phiếu giao hàng'])
df['Ngày giao hàng'] = df['Ngày giao hàng'].apply(parse_date_safe)
df = df[(df['Ngày giao hàng'].dt.year == 2025) & (df['Ngày giao hàng'].dt.month == 9)]
df['Tên hàng hóa'] = df['Tên hàng hóa'].apply(normalize_id)
df['Số lượng giao'] = df['Số lượng giao'].apply(clean_money)
ans = df.groupby('Tên hàng hóa')['Số lượng giao'].sum().sort_values(ascending=False).head(5)
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 46: q_040ffbb6869a | Ngày: 2026-05-16
- **Hỏi**: cho hoi dem so don da huy trong thang 2/2026
- **Gold**: 14
- **Code**:
```python
df = get_df_by_keyword(dfs, ['so_chi_tiet_ban_hang_02.2026'])
df['Ngày'] = df['Ngày'].apply(parse_date_safe)
df['Mã đơn hàng'] = df['Mã đơn hàng'].apply(normalize_id)
df['Trạng thái'] = df['Trạng thái'].astype(str).str.strip().str.lower()
mask = (df['Ngày'].dt.month == 2) & (df['Ngày'].dt.year == 2026) & (df['Trạng thái'].str.contains('hủy|huỷ|huy', na=False))
ans = df.loc[mask, 'Mã đơn hàng'].nunique()
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 47: q_04128078842a | Ngày: 2026-09-10
- **Hỏi**: cửa hàng có mấy khách nhà ở đường Hai Bà Trưng
- **Gold**: None
- **Code**:
```python
df = get_df_by_keyword(dfs, ['Bảng kê phiếu giao hàng'])
df['Ngày giao hàng'] = df['Ngày giao hàng'].apply(parse_date_safe)
df = df[df['Ngày giao hàng'] <= parse_date_safe('2026-09-10')]

df_hh = get_df_by_keyword(dfs, ['Danh sách hàng hóa'])
df_hh['Mã hàng hóa'] = df_hh['Mã hàng hóa'].apply(normalize_id)
df['Mã đơn hàng'] = df['Mã đơn hàng'].apply(normalize_id)

df_kh = df[df['Tên hàng hóa'].astype(str).str.contains('Hai Bà Trưng', case=False, na=False)]
ans = df_kh['Mã đơn hàng'].nunique()
```
- **Lỗi**: Lỗi Runtime: 'NoneType' object is not subscriptable
- **Trạng thái**: ❌ THẤT BẠI

## Câu 48: q_042171000b2c | Ngày: 2026-06-02
- **Hỏi**: Tháng 2/2026 có bao nhiêu đơn hàng bị huỷ?
- **Gold**: 41
- **Code**:
```python
df = get_df_by_keyword(dfs, ['DonHang_ChiTiet'])
df['Ngày đặt hàng'] = df['Ngày đặt hàng'].apply(parse_date_safe)
df['Trạng thái đơn hàng'] = df['Trạng thái đơn hàng'].astype(str).str.strip().str.lower()
mask = (df['Ngày đặt hàng'].dt.year == 2026) & (df['Ngày đặt hàng'].dt.month == 2) & (df['Trạng thái đơn hàng'].str.contains('hủy|huỷ|cancel'))
ans = df.loc[mask, 'Mã đơn hàng'].apply(normalize_id).nunique()
```
- **Lỗi**: Lỗi Runtime: 'str' object has no attribute 'empty'
- **Trạng thái**: ❌ THẤT BẠI

## Câu 49: q_04293d2ed907 | Ngày: 2026-06-18
- **Hỏi**: Ca chiều tuần trước doanh thu được bao nhiêu?
- **Gold**: 112133300
- **Code**:
```python
df = get_df_by_keyword(dfs, ['tên'])
ans = None
```
- **Trạng thái**: ❌ SAI

## Câu 50: q_044a0d4c3ff0 | Ngày: 2026-07-28
- **Hỏi**: tieenf bán má heo nướng nước mắm tháng 9/2025 là nhiêu
- **Gold**: 7623000
- **Code**:
```python
df_sp = get_df_by_keyword(dfs, ['tên'])
df_dh = get_df_by_keyword(dfs, ['đơn'])

df_sp['Mã sản phẩm bán'] = df_sp['Mã sản phẩm bán'].apply(normalize_id)
df_dh['Mã chứng từ'] = df_dh['Mã chứng từ'].apply(normalize_id)

df_dh['Ngày'] = df_dh['Ngày'].apply(parse_date_safe)
df_dh['Tổng đơn'] = df_dh['Tổng đơn'].apply(clean_money)

mask_sp = df_sp['Tên SP'].astype(str).str.lower().str.contains('má heo nướng nước mắm', na=False)
sp_match = df_sp[mask_sp]

mask_date = (df_dh['Ngày'].dt.year == 2025) & (df_dh['Ngày'].dt.month == 9)
dh_match = df_dh[mask_date]

ans = dh_match[dh_match['Diễn giải'].astype(str).str.lower().str.contains('má heo nướng nước mắm', na=False)]['Tổng đơn'].sum()
```
- **Lỗi**: Lỗi Runtime: 'NoneType' object is not subscriptable
- **Trạng thái**: ❌ THẤT BẠI

