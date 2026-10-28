# BẮT ĐẦU QUÁ TRÌNH DẠY AI

- Thời gian: 2026-10-28 17:29:53
- Tổng số câu: 5

## Câu 1: q_001883280e83 | Ngày: 2026-09-07
- **Hỏi**: tháng này tổng giá trị các phiếu nhập hàng là bao nhiu
- **Gold**: 89526400 (Type: number)
- **Code ban đầu**:
```python
# Lấy bảng nhập hàng
df_nhap = get_df_by_keyword(dfs, ['DanhSachNhapHang'])

# Parse ngày
df_nhap['Thời gian'] = parse_date_safe(df_nhap['Thời gian'])

# Ngày chốt
as_of = pd.Timestamp('2026-09-07')

# Lọc tháng này (tháng 9/2026)
mask = (df_nhap['Thời gian'].dt.year == as_of.year) & (df_nhap['Thời gian'].dt.month == as_of.month)
df_thang = df_nhap[mask]

if len(df_thang) == 0:
    ans = None
else:
    # Tổng giá trị các phiếu nhập hàng = tổng "Cần trả NCC"
    df_thang = df_thang.copy()
    df_thang['Cần trả NCC'] = clean_money(df_thang['Cần trả NCC'])
    ans = df_thang['Cần trả NCC'].sum()
```
- **Trạng thái**: ĐÚNG (Kết quả: 89526400)

## Câu 2: q_00195e1e4049 | Ngày: 2026-05-25
- **Hỏi**: Thuốc có hoạt chất Natri clorid tháng này bán được tổng cộng bao nhiêu tiền?
- **Gold**: 2954200 (Type: number)
- **Code ban đầu**:
```python
# Lấy các bảng cần thiết
hh = get_df_by_keyword(dfs, ['BanHang_HangHoa'])
thuoc = get_df_by_keyword(dfs, ['BanHang_Thuoc'])
cthd = get_df_by_keyword(dfs, ['BanHang_ChiTietHoaDon'])
hoadon = get_df_by_keyword(dfs, ['BanHang_HoaDon'])

# Tìm các mã hàng có hoạt chất Natri clorid
thuoc_natri = thuoc[thuoc['Hoạt chất'].astype(str).str.contains('Natri clorid', case=False, na=False)]
ma_hh_natri = thuoc_natri['Mã HH'].tolist()

# Lọc chi tiết hóa đơn có mã hàng thuộc nhóm Natri clorid
cthd_natri = cthd[cthd['Ma hang'].isin(ma_hh_natri)].copy()

# Chuẩn hóa ngày bán trên hóa đơn
hoadon = hoadon.copy()
hoadon['NgayBan_parsed'] = parse_date_safe(hoadon['Ngày bán'])

# Xác định tháng hiện tại theo as_of_date
as_of = pd.Timestamp('2026-05-25')
start_month = as_of.replace(day=1)
end_month = as_of + pd.Timedelta(days=1)

# Lọc hóa đơn trong tháng này, không huỷ, không trả hàng
hd_thang = hoadon[
    (hoadon['NgayBan_parsed'] >= start_month) &
    (hoadon['NgayBan_parsed'] < end_month) &
    (~hoadon['Trạng thái'].astype(str).str.contains('huỷ|hủy|Đổi trả', case=False, na=False))
]

# Lấy các mã giao dịch hợp lệ
ma_gd_hop_le = hd_thang['Order ID'].tolist()

# Lọc chi tiết hóa đơn thuộc các giao dịch hợp lệ và có hoạt chất Natri clorid
cthd_loc = cthd_natri[cthd_natri['Mã giao dịch'].isin(ma_gd_hop_le)].copy()

if len(cthd_loc) == 0:
    ans = 0
else:
    cthd_loc['ThanhTien_clean'] = clean_money(cthd_loc['Thanh tien'])
    ans = int(cthd_loc['ThanhTien_clean'].sum())
```
- **Lỗi lần 1**: Kết quả sai (718000 != 2954200)
- **Code đã sửa**:
```python
# Lấy các bảng cần thiết
hh = get_df_by_keyword(dfs, ['BanHang_HangHoa'])
thuoc = get_df_by_keyword(dfs, ['BanHang_Thuoc'])
cthd = get_df_by_keyword(dfs, ['BanHang_ChiTietHoaDon'])
hoadon = get_df_by_keyword(dfs, ['BanHang_HoaDon'])

# Tìm các mã hàng có hoạt chất Natri clorid
thuoc_natri = thuoc[thuoc['Hoạt chất'].astype(str).str.contains('Natri clorid', case=False, na=False)]
ma_hh_natri = thuoc_natri['Mã HH'].tolist()

# Lọc chi tiết hóa đơn có mã hàng thuộc nhóm Natri clorid
cthd_natri = cthd[cthd['Ma hang'].isin(ma_hh_natri)].copy()

# Chuẩn hóa ngày bán trên hóa đơn
hoadon = hoadon.copy()
hoadon['NgayBan_parsed'] = parse_date_safe(hoadon['Ngày bán'])

# Xác định tháng hiện tại theo as_of_date
as_of = pd.Timestamp('2026-05-25')
start_month = as_of.replace(day=1)
end_month = start_month + pd.offsets.MonthBegin(1)

# Lọc hóa đơn trong tháng này, không huỷ, không trả hàng
hd_thang = hoadon[
    (hoadon['NgayBan_parsed'] >= start_month) &
    (hoadon['NgayBan_parsed'] < end_month) &
    (~hoadon['Trạng thái'].astype(str).str.contains('huỷ|hủy|Đổi trả', case=False, na=False))
]

# Lấy các mã giao dịch hợp lệ
ma_gd_hop_le = hd_thang['Order ID'].tolist()

# Lọc chi tiết hóa đơn thuộc các giao dịch hợp lệ và có hoạt chất Natri clorid
cthd_loc = cthd_natri[cthd_natri['Mã giao dịch'].isin(ma_gd_hop_le)].copy()

if len(cthd_loc) == 0:
    ans = 0
else:
    cthd_loc['ThanhTien_clean'] = clean_money(cthd_loc['Thanh tien'])
    ans = int(cthd_loc['ThanhTien_clean'].sum())
```
- **Lỗi lần 2**: Kết quả sai (718000 != 2954200)
- **Code đã sửa**:
```python
# Lấy các bảng cần thiết
hh = get_df_by_keyword(dfs, ['BanHang_HangHoa'])
thuoc = get_df_by_keyword(dfs, ['BanHang_Thuoc'])
cthd = get_df_by_keyword(dfs, ['BanHang_ChiTietHoaDon'])
hoadon = get_df_by_keyword(dfs, ['BanHang_HoaDon'])

# Tìm các mã hàng có hoạt chất Natri clorid
thuoc_natri = thuoc[thuoc['Hoạt chất'].astype(str).str.contains('Natri clorid', case=False, na=False)]
ma_hh_natri = thuoc_natri['Mã HH'].tolist()

# Lọc chi tiết hóa đơn có mã hàng thuộc nhóm Natri clorid
cthd_natri = cthd[cthd['Ma hang'].isin(ma_hh_natri)].copy()

# Chuẩn hóa ngày bán trên hóa đơn
hoadon = hoadon.copy()
hoadon['NgayBan_parsed'] = parse_date_safe(hoadon['Ngày bán'])

# Xác định tháng hiện tại theo as_of_date
as_of = pd.Timestamp('2026-05-25')
start_month = as_of.replace(day=1)
end_month = start_month + pd.offsets.MonthBegin(1)

# Lọc hóa đơn trong tháng này, không huỷ, không trả hàng
hd_thang = hoadon[
    (hoadon['NgayBan_parsed'] >= start_month) &
    (hoadon['NgayBan_parsed'] < end_month) &
    (~hoadon['Trạng thái'].astype(str).str.contains('huỷ|hủy|Đổi trả', case=False, na=False))
]

# Lấy các mã giao dịch hợp lệ
ma_gd_hop_le = hd_thang['Order ID'].tolist()

# Lọc chi tiết hóa đơn thuộc các giao dịch hợp lệ và có hoạt chất Natri clorid
cthd_loc = cthd_natri[cthd_natri['Mã giao dịch'].isin(ma_gd_hop_le)].copy()

if len(cthd_loc) == 0:
    ans = 0
else:
    cthd_loc['ThanhTien_clean'] = clean_money(cthd_loc['Thanh tien'])
    ans = int(cthd_loc['ThanhTien_clean'].sum())
```
- **Lỗi lần 3**: Kết quả sai (718000 != 2954200)
- **Code đã sửa**:
```python
# Lấy các bảng cần thiết
hh = get_df_by_keyword(dfs, ['BanHang_HangHoa'])
thuoc = get_df_by_keyword(dfs, ['BanHang_Thuoc'])
cthd = get_df_by_keyword(dfs, ['BanHang_ChiTietHoaDon'])
hoadon = get_df_by_keyword(dfs, ['BanHang_HoaDon'])

# Tìm các mã hàng có hoạt chất Natri clorid
thuoc_natri = thuoc[thuoc['Hoạt chất'].astype(str).str.contains('Natri clorid', case=False, na=False)]
ma_hh_natri = thuoc_natri['Mã HH'].tolist()

# Lọc chi tiết hóa đơn có mã hàng thuộc nhóm Natri clorid
cthd_natri = cthd[cthd['Ma hang'].isin(ma_hh_natri)].copy()

# Chuẩn hóa ngày bán trên hóa đơn
hoadon = hoadon.copy()
hoadon['NgayBan_parsed'] = parse_date_safe(hoadon['Ngày bán'])

# Xác định tháng hiện tại theo as_of_date
as_of = pd.Timestamp('2026-05-25')
start_month = as_of.replace(day=1)
end_month = start_month + pd.offsets.MonthBegin(1)

# Lọc hóa đơn trong tháng này, không huỷ, không trả hàng
hd_thang = hoadon[
    (hoadon['NgayBan_parsed'] >= start_month) &
    (hoadon['NgayBan_parsed'] < end_month) &
    (~hoadon['Trạng thái'].astype(str).str.contains('huỷ|hủy|Đổi trả', case=False, na=False))
]

# Lấy các mã giao dịch hợp lệ
ma_gd_hop_le = hd_thang['Order ID'].tolist()

# Lọc chi tiết hóa đơn thuộc các giao dịch hợp lệ và có hoạt chất Natri clorid
cthd_loc = cthd_natri[cthd_natri['Mã giao dịch'].isin(ma_gd_hop_le)].copy()

if len(cthd_loc) == 0:
    ans = 0
else:
    cthd_loc['ThanhTien_clean'] = clean_money(cthd_loc['Thanh tien'])
    ans = int(cthd_loc['ThanhTien_clean'].sum())
```
- **Trạng thái**: ❌ THẤT BẠI

## Câu 3: q_002d03ebbded | Ngày: 2025-04-30
- **Hỏi**: Tổng doanh thu trong ngày hôm nay là bao nhiêu?
- **Gold**: 10309400 (Type: number)
- **Code ban đầu**:
```python
# Lấy bảng hóa đơn tháng 4/2025
df = get_df_by_keyword(dfs, ['DanhSachHoaDon_04.2025'])

# Chuẩn hóa ngày
df['Thời gian'] = parse_date_safe(df['Thời gian'])

# Ngày hôm nay
today = pd.Timestamp('2025-04-30')

# Lọc đơn trong ngày hôm nay
df_today = df[df['Thời gian'].dt.normalize() == today]

# Loại đơn huỷ và trả hàng
df_valid = df_today[~df_today['Trạng thái'].str.lower().str.contains('huỷ|hủy|trả hàng', na=False)]

if len(df_valid) == 0:
    ans = 0
else:
    # Tính doanh thu = tổng tiền hàng - giảm giá (theo rulebook: doanh thu = thành tiền các dòng hàng)
    # Ở đây dùng Tổng tiền hàng (đã là thành tiền các dòng)
    df_valid = df_valid.copy()
    df_valid['Tổng tiền hàng'] = clean_money(df_valid['Tổng tiền hàng'])
    ans = int(df_valid['Tổng tiền hàng'].sum())
```
- **Trạng thái**: ĐÚNG (Kết quả: 10309400)

## Câu 4: q_00558c1410ef | Ngày: 2026-06-24
- **Hỏi**: tỉ lệ huỷ đơn tháng 6/2025 là nhiêu %
- **Gold**: 2.08 (Type: percent)
- **Code ban đầu**:
```python
# Lấy bảng dữ liệu tháng 6/2025
df = get_df_by_keyword(dfs, ['SoBanHang_1_Thang 06 2025'])

# Chuẩn hóa cột Status
status = df['Status'].astype(str).str.strip().str.lower()

# Xác định đơn huỷ: trạng thái chứa "hủy" hoặc "huỷ"
is_cancel = status.str.contains('hủy|huỷ', na=False)

# Tổng số đơn đặt trong kỳ (mọi trạng thái) - đếm theo mã hoá đơn
total_orders = df['Mã hóa đơn'].nunique()

# Số đơn huỷ
cancel_orders = df.loc[is_cancel, 'Mã hóa đơn'].nunique()

# Tỉ lệ huỷ
if total_orders > 0:
    ans = round(cancel_orders / total_orders * 100, 2)
else:
    ans = None
```
- **Trạng thái**: ĐÚNG (Kết quả: 2.08)

## Câu 5: q_006c26c65d50 | Ngày: 2026-07-31
- **Hỏi**: thang 7/2026 co bao nhiu don co dthu tu 55.000 dong tro len
- **Gold**: 2345 (Type: number)
- **Code ban đầu**:
```python
# Lấy bảng chi tiết bán hàng tháng 7/2026
df = get_df_by_keyword(dfs, ['So_chi_tiet_ban_hang_2026_T07_2026'])

# Chuẩn hóa ngày và tiền
df['Ngày'] = parse_date_safe(df['Ngày'])
df['Thành tiền'] = clean_money(df['Thành tiền'])

# Lọc theo tháng 7/2026
df_jul = df[(df['Ngày'].dt.year == 2026) & (df['Ngày'].dt.month == 7)]

# Loại đơn huỷ và trả hàng
trang_thai_huy = ['cancel', 'Đã hủy đơn', 'trả hàng', 'Hoàn trả']
df_valid = df_jul[~df_jul['Trạng thái'].isin(trang_thai_huy)]

# Tính doanh thu theo từng đơn
rev_per_order = df_valid.groupby('Mã đơn hàng')['Thành tiền'].sum()

# Đếm số đơn có doanh thu >= 55.000
ans = int((rev_per_order >= 55000).sum())
```
- **Trạng thái**: ĐÚNG (Kết quả: 2345)

