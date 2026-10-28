# BẮT ĐẦU QUÁ TRÌNH DẠY AI

## Câu 1: q_001883280e83 | Ngày: 2026-09-07
- **Hỏi**: tháng này tổng giá trị các phiếu nhập hàng là bao nhiu
- **Gold**: 89526400 (Type: number)
- **Plan**: Lấy bảng 'DanhSachChiTietNhapHang', lọc mã nhập hàng trong tháng 9 năm 2026, tính tổng số lượng.
- **Code**:
```python
# Lấy bảng chi tiết nhập hàng và bảng nhập hàng
df_ct = dfs['DanhSachChiTietNhapHang'].copy()
df_nh = dfs['DanhSachNhapHang'].copy()

# Làm sạch số lượng và đơn giá
df_ct['Số lượng'] = clean_number(df_ct['Số lượng'])
df_ct['Đơn giá'] = clean_money(df_ct['Đơn giá'])

# Parse ngày nhập hàng
df_nh['Thời gian'] = parse_date_safe(df_nh['Thời gian'])

# Lọc phiếu nhập trong tháng 9 năm 2026
mask = (df_nh['Thời gian'].dt.year == 2026) & (df_nh['Thời gian'].dt.month == 9)
ma_nh_thang9 = df_nh.loc[mask, 'Mã nhập hàng']

# Lọc chi tiết nhập hàng theo mã nhập hàng tháng 9/2026
df_filtered = df_ct[df_ct['Mã nhập hàng'].isin(ma_nh_thang9)]

if df_filtered.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Tính tổng giá trị = số lượng * đơn giá
    df_filtered = df_filtered.copy()
    df_filtered['Thành tiền'] = df_filtered['Số lượng'] * df_filtered['Đơn giá']
    ans = df_filtered['Thành tiền'].sum()
```
- **Lưu**: ✅

## Câu 2: q_00195e1e4049 | Ngày: 2026-05-25
- **Hỏi**: Thuốc có hoạt chất Natri clorid tháng này bán được tổng cộng bao nhiêu tiền?
- **Gold**: 2954200 (Type: number)
- **Plan**: Để trả lời câu hỏi này, tôi sẽ thực hiện các bước sau:

1. Lấy bảng 'BanHang_ChiTietHoaDon' và lọc các giao dịch có Mã giao dịch trong 'ORD000005'.
2. Lấy bảng 'BanHang_DonViQuyDoi' và tìm đơn vị quy đổi tương ứng với 'St
- **Code**:
```python
# Lấy bảng cần thiết
thuoc = dfs['BanHang_Thuoc']
hanghoa = dfs['BanHang_HangHoa']
cthd = dfs['BanHang_ChiTietHoaDon']
hoadon = dfs['BanHang_HoaDon']

# Lọc thuốc có hoạt chất Natri clorid
thuoc_nc = thuoc[thuoc['Hoạt chất'].astype(str).str.contains('Natri clorid', case=False, na=False)]
ma_hh_nc = thuoc_nc['Mã HH'].tolist()

# Lấy mã sản phẩm tương ứng từ HangHoa (ma_sp)
hh_nc = hanghoa[hanghoa['ma_sp'].isin(ma_hh_nc)]
ma_sp_nc = hh_nc['ma_sp'].tolist()

# Lọc chi tiết hóa đơn có Ma hang thuộc nhóm Natri clorid
ct = cthd[cthd['Ma hang'].isin(ma_sp_nc)].copy()

# Lọc hóa đơn trong tháng 5/2026
hd = hoadon.copy()
hd['Ngay'] = parse_date_safe(hd['Ngày bán'])
hd_thang = hd[(hd['Ngay'].dt.year == 2026) & (hd['Ngay'].dt.month == 5)]
ma_hd_thang = hd_thang['Order ID'].tolist()

# Lọc chi tiết thuộc hóa đơn tháng 5/2026
ct = ct[ct['Mã giao dịch'].isin(ma_hd_thang)]

if ct.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    ct['Thanh tien_clean'] = clean_money(ct['Thanh tien'])
    ans = ct['Thanh tien_clean'].sum()
```
- **Lỗi lần 1**: Kết quả sai (718000 != 2954200)
- **Code sửa**:
```python
# Lấy bảng cần thiết
thuoc = dfs['BanHang_Thuoc']
hanghoa = dfs['BanHang_HangHoa']
cthd = dfs['BanHang_ChiTietHoaDon']
hoadon = dfs['BanHang_HoaDon']

# Lọc thuốc có hoạt chất Natri clorid
thuoc_nc = thuoc[thuoc['Hoạt chất'].astype(str).str.contains('Natri clorid', case=False, na=False)]
ma_hh_nc = thuoc_nc['Mã HH'].tolist()

# Lấy mã sản phẩm tương ứng từ HangHoa
hh_nc = hanghoa[hanghoa['ma_sp'].isin(ma_hh_nc)]
ma_sp_nc = hh_nc['ma_sp'].tolist()

# Lọc chi tiết hóa đơn có Ma hang thuộc nhóm Natri clorid
ct = cthd[cthd['Ma hang'].isin(ma_sp_nc)].copy()

# Lọc hóa đơn trong tháng 5/2026
hd = hoadon.copy()
hd['Ngay'] = parse_date_safe(hd['Ngày bán'])
hd_thang = hd[(hd['Ngay'].dt.year == 2026) & (hd['Ngay'].dt.month == 5)]
ma_hd_thang = hd_thang['Order ID'].tolist()

# Lọc chi tiết thuộc hóa đơn tháng 5/2026
ct = ct[ct['Mã giao dịch'].isin(ma_hd_thang)]

if ct.empty:
    ans = None
else:
    ct['Thanh tien_clean'] = clean_money(ct['Thanh tien'])
    ans = ct['Thanh tien_clean'].sum()
```
- **Lỗi lần 2**: Kết quả sai (718000 != 2954200)
- **Code sửa**:
```python
# Lấy bảng cần thiết
thuoc = dfs['BanHang_Thuoc']
hanghoa = dfs['BanHang_HangHoa']
cthd = dfs['BanHang_ChiTietHoaDon']
hoadon = dfs['BanHang_HoaDon']

# Lọc thuốc có hoạt chất Natri clorid
thuoc_nc = thuoc[thuoc['Hoạt chất'].astype(str).str.contains('Natri clorid', case=False, na=False)]
ma_hh_nc = thuoc_nc['Mã HH'].tolist()

# Lấy mã sản phẩm tương ứng từ HangHoa
hh_nc = hanghoa[hanghoa['ma_sp'].isin(ma_hh_nc)]
ma_sp_nc = hh_nc['ma_sp'].tolist()

# Lọc chi tiết hóa đơn có Ma hang thuộc nhóm Natri clorid
ct = cthd[cthd['Ma hang'].isin(ma_sp_nc)].copy()

# Lọc hóa đơn trong tháng 5/2026
hd = hoadon.copy()
hd['Ngay'] = parse_date_safe(hd['Ngày bán'])
hd_thang = hd[(hd['Ngay'].dt.year == 2026) & (hd['Ngay'].dt.month == 5)]
ma_hd_thang = hd_thang['Order ID'].tolist()

# Lọc chi tiết thuộc hóa đơn tháng 5/2026
ct = ct[ct['Mã giao dịch'].isin(ma_hd_thang)]

if ct.empty:
    ans = None
else:
    ct['Thanh tien_clean'] = clean_money(ct['Thanh tien'])
    ans = ct['Thanh tien_clean'].sum()
```
- **Lỗi lần 3**: Kết quả sai (718000 != 2954200)
- **Code sửa**:
```python
# Lấy bảng cần thiết
thuoc = dfs['BanHang_Thuoc']
hanghoa = dfs['BanHang_HangHoa']
cthd = dfs['BanHang_ChiTietHoaDon']
hoadon = dfs['BanHang_HoaDon']

# Lọc thuốc có hoạt chất Natri clorid
thuoc_nc = thuoc[thuoc['Hoạt chất'].astype(str).str.contains('Natri clorid', case=False, na=False)]
ma_hh_nc = thuoc_nc['Mã HH'].tolist()

# Lấy mã sản phẩm tương ứng từ HangHoa
hh_nc = hanghoa[hanghoa['ma_sp'].isin(ma_hh_nc)]
ma_sp_nc = hh_nc['ma_sp'].tolist()

# Lọc chi tiết hóa đơn có Ma hang thuộc nhóm Natri clorid
ct = cthd[cthd['Ma hang'].isin(ma_sp_nc)].copy()

# Lọc hóa đơn trong tháng 5/2026
hd = hoadon.copy()
hd['Ngay'] = parse_date_safe(hd['Ngày bán'])
hd_thang = hd[(hd['Ngay'].dt.year == 2026) & (hd['Ngay'].dt.month == 5)]
ma_hd_thang = hd_thang['Order ID'].tolist()

# Lọc chi tiết thuộc hóa đơn tháng 5/2026
ct = ct[ct['Mã giao dịch'].isin(ma_hd_thang)]

if ct.empty:
    ans = None
else:
    ct['Thanh tien_clean'] = clean_money(ct['Thanh tien'])
    ans = ct['Thanh tien_clean'].sum()
```
- **Lưu**: ❌

## Câu 3: q_002d03ebbded | Ngày: 2025-04-30
- **Hỏi**: Tổng doanh thu trong ngày hôm nay là bao nhiêu?
- **Gold**: 10309400 (Type: number)
- **Plan**: Để trả lời câu hỏi "Tổng doanh thu trong ngày hôm nay là bao nhiêu?", chúng tôi cần thực hiện các bước sau:

1. Lấy bảng 'DanhSachHoaDon_01.2025' và lọc các hóa đơn có thời gian trong ngày 2025-04-30.
2. T
- **Code**:
```python
# Lấy bảng hóa đơn tháng 4/2025
df = dfs['DanhSachHoaDon_04.2025'].copy()

# Parse ngày tháng
df['Thời gian'] = parse_date_safe(df['Thời gian'])

# Lọc hóa đơn trong ngày 2025-04-30
target_date = pd.Timestamp('2025-04-30')
df_today = df[df['Thời gian'].dt.normalize() == target_date]

# Loại bỏ hóa đơn hủy/trả hàng
if not df_today.empty:
    status = df_today['Trạng thái'].astype(str).str.strip().str.lower()
    valid_mask = ~status.isin(['hủy đơn', 'huỷ đơn', 'trả hàng', 'đã trả hàng'])
    df_today = df_today[valid_mask]

if df_today.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    df_today['Tổng tiền hàng'] = clean_money(df_today['Tổng tiền hàng'])
    ans = int(df_today['Tổng tiền hàng'].sum())
```
- **Lưu**: ✅

## Câu 4: q_00558c1410ef | Ngày: 2026-06-24
- **Hỏi**: tỉ lệ huỷ đơn tháng 6/2025 là nhiêu %
- **Gold**: 2.08 (Type: percent)
- **Plan**: Để trả lời câu hỏi này, chúng ta cần thực hiện các bước sau:

1. Lấy bảng 'SoBanHang_1_Thang 06 2025' (hoặc tương đương với tháng 6/2025).
2. Lọc các hàng có Status là 'Đã hủy đơn'.
3. Tính tỷ lệ các hàng đã hủy
- **Code**:
```python
# Lấy bảng tháng 6/2025
df = dfs['SoBanHang_1_Thang 06 2025'].copy()

# Chuẩn hóa cột Status
status = df['Status'].astype(str).str.strip().str.lower()

# Tổng số đơn (tất cả các hàng)
total = len(df)

# Lọc các đơn bị hủy: 'đã hủy đơn' hoặc 'hủy'
cancel_mask = status.isin(['đã hủy đơn', 'hủy'])
cancel_count = cancel_mask.sum()

if total == 0:
    ans = None
    reason = "Không có dữ liệu"
else:
    ans = round(cancel_count / total * 100, 2)
```
- **Lỗi lần 1**: Kết quả sai (2.11 != 2.08)
- **Code sửa**:
```python
# Lấy bảng tháng 6/2025
df = dfs['SoBanHang_1_Thang 06 2025'].copy()

# Chuẩn hóa cột Status
status = df['Status'].astype(str).str.strip().str.lower()

# Tổng số đơn (tất cả các hàng)
total = len(df)

# Lọc các đơn bị hủy: 'đã hủy đơn' hoặc 'hủy'
cancel_mask = status.isin(['đã hủy đơn', 'hủy'])
cancel_count = cancel_mask.sum()

if total == 0:
    ans = None
else:
    ans = round(cancel_count / total * 100, 2)
```
- **Lỗi lần 2**: Kết quả sai (2.11 != 2.08)
- **Code sửa**:
```python
# Lấy bảng tháng 6/2025
df = dfs['SoBanHang_1_Thang 06 2025'].copy()

# Chuẩn hóa cột Status
status = df['Status'].astype(str).str.strip().str.lower()

# Tổng số đơn (tất cả các hàng)
total = len(df)

# Lọc các đơn bị hủy: 'đã hủy đơn' hoặc 'hủy'
cancel_mask = status.isin(['đã hủy đơn', 'hủy'])
cancel_count = cancel_mask.sum()

if total == 0:
    ans = None
else:
    ans = round(cancel_count / total * 100, 2)
```
- **Lỗi lần 3**: Kết quả sai (2.11 != 2.08)
- **Code sửa**:
```python
# Lấy bảng tháng 6/2025
df = dfs['SoBanHang_1_Thang 06 2025'].copy()

# Chuẩn hóa cột Status
status = df['Status'].astype(str).str.strip().str.lower()

# Tổng số đơn (tất cả các hàng)
total = len(df)

# Lọc các đơn bị hủy: 'đã hủy đơn' hoặc 'hủy'
cancel_mask = status.isin(['đã hủy đơn', 'hủy'])
cancel_count = cancel_mask.sum()

if total == 0:
    ans = None
else:
    ans = round(cancel_count / total * 100, 2)
```
- **Lưu**: ❌

## Câu 5: q_006c26c65d50 | Ngày: 2026-07-31
- **Hỏi**: thang 7/2026 co bao nhiu don co dthu tu 55.000 dong tro len
- **Gold**: 2345 (Type: number)
- **Plan**: Để trả lời câu hỏi này, tôi sẽ thực hiện các bước sau:

1. Lấy bảng 'Danh sách hàng hóa' để lấy thông tin về hàng hóa có mã hàng hóa là 'SP0004' (Cà phê sữa (M)).
2. Lấy bảng 'So_chi_tiet_ban_hang_1_T04_202
- **Code**:
```python
import pandas as pd

# Lấy bảng chi tiết bán hàng tháng 7/2026
df = dfs['So_chi_tiet_ban_hang_2026_T07_2026'].copy()

# Làm sạch ngày
df['Ngày'] = parse_date_safe(df['Ngày'])

# Lọc tháng 7/2026
df = df[(df['Ngày'].dt.year == 2026) & (df['Ngày'].dt.month == 7)]

# Làm sạch thành tiền
df['Thành tiền'] = clean_money(df['Thành tiền'])

# Lọc đơn có doanh thu >= 55.000 (tính theo từng dòng chi tiết)
df_filtered = df[df['Thành tiền'] >= 55000]

# Đếm số đơn hàng duy nhất
if df_filtered.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    ans = df_filtered['Mã đơn hàng'].nunique()
```
- **Lỗi lần 1**: Kết quả sai (1130 != 2345)
- **Code sửa**:
```python
import pandas as pd

# Lấy bảng chi tiết bán hàng tháng 7/2026
df = dfs['So_chi_tiet_ban_hang_2026_T07_2026'].copy()

# Làm sạch ngày
df['Ngày'] = parse_date_safe(df['Ngày'])

# Lọc tháng 7/2026
df = df[(df['Ngày'].dt.year == 2026) & (df['Ngày'].dt.month == 7)]

# Làm sạch thành tiền
df['Thành tiền'] = clean_money(df['Thành tiền'])

# Tính tổng doanh thu theo từng đơn hàng
order_revenue = df.groupby('Mã đơn hàng')['Thành tiền'].sum()

# Lọc đơn có tổng doanh thu >= 55.000
ans = int((order_revenue >= 55000).sum())
```
- **Lỗi lần 2**: Kết quả sai (2409 != 2345)
- **Code sửa**:
```python
import pandas as pd

# Lấy bảng chi tiết bán hàng tháng 7/2026
df = dfs['So_chi_tiet_ban_hang_2026_T07_2026'].copy()

# Làm sạch ngày
df['Ngày'] = parse_date_safe(df['Ngày'])

# Lọc tháng 7/2026 (đến ngày chốt 2026-07-31)
df = df[(df['Ngày'].dt.year == 2026) & (df['Ngày'].dt.month == 7) & (df['Ngày'] <= pd.Timestamp('2026-07-31'))]

# Làm sạch thành tiền
df['Thành tiền'] = clean_money(df['Thành tiền'])

# Tính tổng doanh thu theo từng đơn hàng
order_revenue = df.groupby('Mã đơn hàng')['Thành tiền'].sum()

# Lọc đơn có tổng doanh thu >= 55.000
ans = int((order_revenue >= 55000).sum())
```
- **Lỗi lần 3**: Kết quả sai (2409 != 2345)
- **Code sửa**:
```python
import pandas as pd

# Lấy bảng chi tiết bán hàng tháng 7/2026
df = dfs['So_chi_tiet_ban_hang_2026_T07_2026'].copy()

# Làm sạch ngày
df['Ngày'] = parse_date_safe(df['Ngày'])

# Lọc tháng 7/2026 (đến ngày chốt 2026-07-31)
df = df[(df['Ngày'].dt.year == 2026) & (df['Ngày'].dt.month == 7) & (df['Ngày'] <= pd.Timestamp('2026-07-31'))]

# Làm sạch thành tiền
df['Thành tiền'] = clean_money(df['Thành tiền'])

# Tính tổng doanh thu theo từng đơn hàng
order_revenue = df.groupby('Mã đơn hàng')['Thành tiền'].sum()

# Lọc đơn có tổng doanh thu >= 55.000
ans = int((order_revenue >= 55000).sum())
```
- **Lưu**: ❌

## Câu 6: q_0088f7a0afc5 | Ngày: 2026-07-13
- **Hỏi**: Tháng 7/2025 mặt hàng Otrivin 0,1% xịt mũi chai 10ml bán được tổng cộng bao nhiêu chai?
- **Gold**: 77 (Type: number)
- **Plan**: Để trả lời câu hỏi này, tôi sẽ thực hiện các bước sau:

1. Lấy thông tin về hàng hóa Otrivin 0,1% xịt mũi từ bảng DanhSachHoaDon_T01-2025.
2. Lấy thông tin về đơn hàng cuối cùng trước ngày 2026-07-13
- **Code**:
```python
# Tìm sản phẩm Otrivin 0,1% xịt mũi chai 10ml
sp = dfs['DanhSachSanPham']
mask_sp = sp['Tên hàng'].str.contains('Otrivin', case=False, na=False) & sp['Tên hàng'].str.contains('0,1%', na=False)
sp_otrivin = sp[mask_sp]
ma_hang_list = sp_otrivin['Mã hàng'].tolist()

if len(ma_hang_list) == 0:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Lấy chi tiết hóa đơn tháng 7/2025
    ct = dfs['DanhSachHoaDonChiTiet']
    hd = dfs['DanhSachHoaDon_T07-2025']
    
    # Lọc hóa đơn tháng 7/2025 (loại bỏ hủy/trả hàng)
    hd_valid = hd[~hd['Trạng thái'].isin(['Đã hủy', 'Đã trả hàng'])]
    ma_hd_valid = hd_valid['Mã hóa đơn'].tolist()
    
    # Lọc chi tiết theo mã hàng và hóa đơn hợp lệ
    ct_filter = ct[ct['Mã hàng'].isin(ma_hang_list) & ct['Mã hóa đơn'].isin(ma_hd_valid)]
    
    if ct_filter.empty:
        ans = None
        reason = "Không có dữ liệu"
    else:
        sl = clean_number(ct_filter['Số lượng'])
        ans = int(sl.sum())
```
- **Lưu**: ✅

## Câu 7: q_008f69128180 | Ngày: 2026-05-20
- **Hỏi**: trong thang 10/2025, ti le don huy la bnhiu %
- **Gold**: 1.21 (Type: percent)
- **Plan**: Để giải quyết câu hỏi này, tôi sẽ cần lấy dữ liệu từ bảng 'BangGia' và 'SoBanHang_Tháng 01-2025' để tính tỷ lệ đơn hàng bị huỷ trong tháng 10/2025. Đầu tiên, tôi sẽ lọc dữ liệu từ bảng 'SoBanHang_Tháng 01-2
- **Code**:
```python
import pandas as pd

# Lấy dữ liệu tháng 10/2025
df = dfs['SoBanHang_Tháng 10-2025'].copy()

# Chuẩn hóa cột Ghi chú TT
ghi_chu = df['Ghi chú TT'].astype(str).str.strip().str.lower()

# Xác định đơn hủy: 'hủy', 'huy', 'đã trả hàng', 'trả lại'
huy_mask = ghi_chu.isin(['hủy', 'huy', 'đã trả hàng', 'trả lại'])

tong_don = len(df)
so_huy = huy_mask.sum()

if tong_don == 0:
    ans = None
    reason = "Không có dữ liệu"
else:
    ans = round(so_huy / tong_don * 100, 2)
```
- **Lỗi lần 1**: Kết quả sai (2.39 != 1.21)
- **Code sửa**:
```python
import pandas as pd

# Lấy dữ liệu tháng 10/2025
df = dfs['SoBanHang_Tháng 10-2025'].copy()

# Chuẩn hóa cột Ghi chú TT
ghi_chu = df['Ghi chú TT'].astype(str).str.strip().str.lower()

# Xác định đơn hủy: 'hủy', 'huy', 'đã trả hàng', 'trả lại'
huy_mask = ghi_chu.isin(['hủy', 'huy', 'đã trả hàng', 'trả lại'])

tong_don = len(df)
so_huy = huy_mask.sum()

if tong_don == 0:
    ans = None
else:
    ans = round(so_huy / tong_don * 100, 2)
```
- **Lỗi lần 2**: Kết quả sai (2.39 != 1.21)
- **Code sửa**:
```python
import pandas as pd

# Lấy dữ liệu tháng 10/2025
df = dfs['SoBanHang_Tháng 10-2025'].copy()

# Chuẩn hóa cột Ghi chú TT
ghi_chu = df['Ghi chú TT'].astype(str).str.strip().str.lower()

# Xác định đơn hủy: 'hủy', 'huy', 'đã trả hàng', 'trả lại'
huy_mask = ghi_chu.isin(['hủy', 'huy', 'đã trả hàng', 'trả lại'])

tong_don = len(df)
so_huy = huy_mask.sum()

if tong_don == 0:
    ans = None
else:
    ans = round(so_huy / tong_don * 100, 2)
```
- **Lỗi lần 3**: Kết quả sai (2.39 != 1.21)
- **Code sửa**:
```python
import pandas as pd

# Lấy dữ liệu tháng 10/2025
df = dfs['SoBanHang_Tháng 10-2025'].copy()

# Chuẩn hóa cột Ghi chú TT
ghi_chu = df['Ghi chú TT'].astype(str).str.strip().str.lower()

# Xác định đơn hủy: 'hủy', 'huy', 'đã trả hàng', 'trả lại'
huy_mask = ghi_chu.isin(['hủy', 'huy', 'đã trả hàng', 'trả lại'])

tong_don = len(df)
so_huy = huy_mask.sum()

if tong_don == 0:
    ans = None
else:
    ans = round(so_huy / tong_don * 100, 2)
```
- **Lưu**: ❌

## Câu 8: q_00a6e23cbacf | Ngày: 2026-08-05
- **Hỏi**: Trong tháng 1/2025, Mì Omachi sườn hầm nhập vào giá bình quân một thùng là bao nhiêu ạ?
- **Gold**: 200556 (Type: number)
- **Plan**: Để trả lời câu hỏi này, tôi sẽ thực hiện các bước sau:

1. Lấy bảng 'DuLieuBanHang_DanhSachHoaDon' và lọc các hóa đơn có thời gian là 01/01/2025.
2. Tính giá bình quân một thùng của sản phẩm Mì Omachi sườn hầm nhập
- **Code**:
```python
import pandas as pd

# Lấy dữ liệu
hd = dfs['DuLieuBanHang_DanhSachHoaDon']
ct = dfs['DuLieuBanHang_DanhSachChiTietNhapHang']
nh = dfs['DuLieuBanHang_DanhSachNhapHang']
sp = dfs['DuLieuBanHang_DanhSachSanPham']

# Làm sạch ngày
nh['Thời gian'] = parse_date_safe(nh['Thời gian'])

# Lọc tháng 1/2025
mask_nh = (nh['Thời gian'].dt.year == 2025) & (nh['Thời gian'].dt.month == 1)
nh_jan = nh[mask_nh]

# Lọc sản phẩm Mì Omachi sườn hầm
sp_omachi = sp[sp['Tên hàng'].str.contains('Omachi', case=False, na=False) & 
               sp['Tên hàng'].str.contains('sườn hầm', case=False, na=False)]
ma_hang_omachi = sp_omachi['Mã hàng'].tolist()

# Lọc chi tiết nhập hàng
ct_jan = ct[ct['Mã nhập hàng'].isin(nh_jan['Mã nhập hàng'])]
ct_omachi = ct_jan[ct_jan['Mã hàng'].isin(ma_hang_omachi)]

if ct_omachi.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Làm sạch số
    ct_omachi = ct_omachi.copy()
    ct_omachi['Số lượng'] = clean_number(ct_omachi['Số lượng'])
    ct_omachi['Đơn giá'] = clean_money(ct_omachi['Đơn giá'])
    
    # Tính giá bình quân một thùng
    # Đơn vị tính là 'thùng' -> tính trực tiếp
    # Nếu ĐVT khác, cần quy đổi - nhưng theo câu hỏi "một thùng"
    # Giả sử đơn giá đã là giá/thùng hoặc tính theo đơn vị tương ứng
    total_value = (ct_omachi['Số lượng'] * ct_omachi['Đơn giá']).sum()
    total_qty = ct_omachi['Số lượng'].sum()
    
    if total_qty == 0:
        ans = None
        reason = "Không có dữ liệu"
    else:
        ans = total_value / total_qty
```
- **Lỗi lần 1**: Kết quả sai (200555.55555555556 != 200556)
- **Code sửa**:
```python
import pandas as pd

# Lấy dữ liệu
nh = dfs['DuLieuBanHang_DanhSachNhapHang']
ct = dfs['DuLieuBanHang_DanhSachChiTietNhapHang']
sp = dfs['DuLieuBanHang_DanhSachSanPham']

# Làm sạch ngày
nh = nh.copy()
nh['Thời gian'] = parse_date_safe(nh['Thời gian'])

# Lọc tháng 1/2025
mask_nh = (nh['Thời gian'].dt.year == 2025) & (nh['Thời gian'].dt.month == 1)
nh_jan = nh[mask_nh]

# Lọc sản phẩm Mì Omachi sườn hầm
sp_omachi = sp[sp['Tên hàng'].str.contains('Omachi', case=False, na=False) & 
               sp['Tên hàng'].str.contains('sườn hầm', case=False, na=False)]
ma_hang_omachi = sp_omachi['Mã hàng'].tolist()

# Lọc chi tiết nhập hàng
ct_jan = ct[ct['Mã nhập hàng'].isin(nh_jan['Mã nhập hàng'])]
ct_omachi = ct_jan[ct_jan['Mã hàng'].isin(ma_hang_omachi)].copy()

if ct_omachi.empty:
    ans = None
else:
    ct_omachi['Số lượng'] = clean_number(ct_omachi['Số lượng'])
    ct_omachi['Đơn giá'] = clean_money(ct_omachi['Đơn giá'])
    
    total_value = (ct_omachi['Số lượng'] * ct_omachi['Đơn giá']).sum()
    total_qty = ct_omachi['Số lượng'].sum()
    
    if total_qty == 0:
        ans = None
    else:
        ans = round(total_value / total_qty)
```
- **Lưu**: ✅

## Câu 9: q_00bb4edee433 | Ngày: 2026-09-20
- **Hỏi**: trong tổng doanh thu tháng 7/2025, phần của thuốc kê đơn là bao nhiêu phần trăm
- **Gold**: 2.27 (Type: percent)
- **Plan**: Để giải quyết câu hỏi này, tôi sẽ cần thực hiện các bước sau:

1. Lấy bảng 'DonHang_ChiTiet' và lọc các đơn hàng thuộc tháng 7/2025.
2. Tính tổng doanh thu của các đơn hàng này.
3. Lấy bảng 'DuLieuXuat_DanhSachSanPham' để xác
- **Code**:
```python
# Lọc đơn hàng tháng 7/2025
dh = dfs['DonHang_ChiTiet'].copy()
dh['Ngày đặt hàng'] = parse_date_safe(dh['Ngày đặt hàng'])
dh['Tổng tiền'] = clean_money(dh['Tổng tiền'])

mask = (dh['Ngày đặt hàng'].dt.month == 7) & (dh['Ngày đặt hàng'].dt.year == 2025)
dh_july = dh[mask]

if dh_july.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Lấy danh sách thuốc kê đơn
    thuoc = dfs['DuLieuXuat_DanhSachThuoc'][['Mã SKU', 'Thuốc kê đơn']]
    sp = dfs['DuLieuXuat_DanhSachSanPham'][['Mã SKU', 'Tên sản phẩm']]
    sp_thuoc = sp.merge(thuoc, on='Mã SKU', how='left')
    
    # Map tên sản phẩm -> thuốc kê đơn
    ten_to_kd = dict(zip(sp_thuoc['Tên sản phẩm'], sp_thuoc['Thuốc kê đơn']))
    
    dh_july = dh_july.copy()
    dh_july['Thuốc kê đơn'] = dh_july['Tên sản phẩm'].map(ten_to_kd)
    
    tong = dh_july['Tổng tiền'].sum()
    tong_kd = dh_july.loc[dh_july['Thuốc kê đơn'] == True, 'Tổng tiền'].sum()
    
    if tong == 0:
        ans = None
        reason = "Không có dữ liệu"
    else:
        ans = round(tong_kd / tong * 100, 2)
```
- **Lỗi lần 1**: Kết quả sai (1.71 != 2.27)
- **Code sửa**:
```python
# Lọc đơn hàng tháng 7/2025
dh = dfs['DonHang_ChiTiet'].copy()
dh['Ngày đặt hàng'] = parse_date_safe(dh['Ngày đặt hàng'])
dh['Tổng tiền'] = clean_money(dh['Tổng tiền'])

mask = (dh['Ngày đặt hàng'].dt.month == 7) & (dh['Ngày đặt hàng'].dt.year == 2025)
dh_july = dh[mask]

if dh_july.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Lấy danh sách thuốc kê đơn
    thuoc = dfs['DuLieuXuat_DanhSachThuoc'][['Mã SKU', 'Thuốc kê đơn']]
    sp = dfs['DuLieuXuat_DanhSachSanPham'][['Mã SKU', 'Tên sản phẩm']]
    sp_thuoc = sp.merge(thuoc, on='Mã SKU', how='left')
    
    # Map tên sản phẩm -> thuốc kê đơn
    ten_to_kd = dict(zip(sp_thuoc['Tên sản phẩm'], sp_thuoc['Thuốc kê đơn']))
    
    dh_july = dh_july.copy()
    dh_july['Thuốc kê đơn'] = dh_july['Tên sản phẩm'].map(ten_to_kd)
    
    tong = dh_july['Tổng tiền'].sum()
    tong_kd = dh_july.loc[dh_july['Thuốc kê đơn'] == True, 'Tổng tiền'].sum()
    
    if tong == 0:
        ans = None
        reason = "Không có dữ liệu"
    else:
        ans = round(tong_kd / tong * 100, 2)
```
- **Lỗi lần 2**: Kết quả sai (1.71 != 2.27)
- **Code sửa**:
```python
# Lọc đơn hàng tháng 7/2025
dh = dfs['DonHang_ChiTiet'].copy()
dh['Ngày đặt hàng'] = parse_date_safe(dh['Ngày đặt hàng'])
dh['Tổng tiền'] = clean_money(dh['Tổng tiền'])

mask = (dh['Ngày đặt hàng'].dt.month == 7) & (dh['Ngày đặt hàng'].dt.year == 2025)
dh_july = dh[mask]

if dh_july.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Lấy danh sách thuốc kê đơn
    thuoc = dfs['DuLieuXuat_DanhSachThuoc'][['Mã SKU', 'Thuốc kê đơn']]
    sp = dfs['DuLieuXuat_DanhSachSanPham'][['Mã SKU', 'Tên sản phẩm']]
    sp_thuoc = sp.merge(thuoc, on='Mã SKU', how='left')
    
    # Map tên sản phẩm -> thuốc kê đơn
    ten_to_kd = dict(zip(sp_thuoc['Tên sản phẩm'], sp_thuoc['Thuốc kê đơn']))
    
    dh_july = dh_july.copy()
    dh_july['Thuốc kê đơn'] = dh_july['Tên sản phẩm'].map(ten_to_kd)
    
    tong = dh_july['Tổng tiền'].sum()
    tong_kd = dh_july.loc[dh_july['Thuốc kê đơn'] == True, 'Tổng tiền'].sum()
    
    if tong == 0:
        ans = None
        reason = "Không có dữ liệu"
    else:
        ans = round(tong_kd / tong * 100, 2)
```
- **Lỗi lần 3**: Kết quả sai (1.71 != 2.27)
- **Code sửa**:
```python
# Lọc đơn hàng tháng 7/2025
dh = dfs['DonHang_ChiTiet'].copy()
dh['Ngày đặt hàng'] = parse_date_safe(dh['Ngày đặt hàng'])
dh['Tổng tiền'] = clean_money(dh['Tổng tiền'])

mask = (dh['Ngày đặt hàng'].dt.month == 7) & (dh['Ngày đặt hàng'].dt.year == 2025)
dh_july = dh[mask]

if dh_july.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Lấy danh sách thuốc kê đơn
    thuoc = dfs['DuLieuXuat_DanhSachThuoc'][['Mã SKU', 'Thuốc kê đơn']]
    sp = dfs['DuLieuXuat_DanhSachSanPham'][['Mã SKU', 'Tên sản phẩm']]
    sp_thuoc = sp.merge(thuoc, on='Mã SKU', how='left')
    
    # Map tên sản phẩm -> thuốc kê đơn
    ten_to_kd = dict(zip(sp_thuoc['Tên sản phẩm'], sp_thuoc['Thuốc kê đơn']))
    
    dh_july = dh_july.copy()
    dh_july['Thuốc kê đơn'] = dh_july['Tên sản phẩm'].map(ten_to_kd)
    
    tong = dh_july['Tổng tiền'].sum()
    tong_kd = dh_july.loc[dh_july['Thuốc kê đơn'] == True, 'Tổng tiền'].sum()
    
    if tong == 0:
        ans = None
        reason = "Không có dữ liệu"
    else:
        ans = round(tong_kd / tong * 100, 2)
```
- **Lưu**: ❌

## Câu 10: q_00c4e64fe706 | Ngày: 2026-09-14
- **Hỏi**: Tháng 5/2025 cửa hàng bán đc tổng cộng bao nhiêu tiền?
- **Gold**: 271866000 (Type: number)
- **Plan**: Để trả lời câu hỏi này, tôi sẽ thực hiện các bước sau:

1. Lấy bảng DanhSachDonViTinh để tìm mã hàng tương ứng với các sản phẩm trong bảng DanhSachNhapHang.
2. Sử dụng kết quả từ bước 1, lấy tổng số lượng của các sản phẩm đó từ bảng DanhSachNhapHang.
3. Á
- **Code**:
```python
# Lấy bảng hóa đơn và chi tiết hóa đơn
hoadon = dfs['DanhSachHoaDon'].copy()
ct1 = dfs['DanhSachHoaDonChiTiet_1'].copy()
ct2 = dfs['DanhSachHoaDonChiTiet_2'].copy()

# Chuẩn hóa thời gian hóa đơn
hoadon['ThoiGian'] = parse_date_safe(hoadon['Thời gian'])

# Lọc hóa đơn tháng 5/2025
mask = (hoadon['ThoiGian'].dt.year == 2025) & (hoadon['ThoiGian'].dt.month == 5)
hd_t5 = hoadon[mask]

# Loại bỏ hóa đơn hủy/trả lại
trangthai_loai = ['hủy đơn', 'trả lại', 'Đã hủy', 'Hủy', 'hủy']
hd_t5 = hd_t5[~hd_t5['Trạng thái'].astype(str).str.strip().str.lower().isin([s.lower() for s in trangthai_loai])]

if hd_t5.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Gộp chi tiết từ 2 bảng
    ct = pd.concat([ct1, ct2], ignore_index=True)
    ct_t5 = ct[ct['Mã hóa đơn'].isin(hd_t5['Mã hóa đơn'])]
    
    if ct_t5.empty:
        ans = None
        reason = "Không có dữ liệu"
    else:
        ct_t5 = ct_t5.copy()
        ct_t5['ThanhTienNum'] = clean_money(ct_t5['Thành tiền'])
        ans = int(ct_t5['ThanhTienNum'].sum())
```
- **Lỗi lần 1**: Kết quả sai (47808500 != 271866000)
- **Code sửa**:
```python
# Lấy bảng hóa đơn và chi tiết hóa đơn
hoadon = dfs['DanhSachHoaDon'].copy()
ct1 = dfs['DanhSachHoaDonChiTiet_1'].copy()
ct2 = dfs['DanhSachHoaDonChiTiet_2'].copy()

# Chuẩn hóa thời gian hóa đơn
hoadon['ThoiGian'] = parse_date_safe(hoadon['Thời gian'])

# Lọc hóa đơn tháng 5/2025
mask = (hoadon['ThoiGian'].dt.year == 2025) & (hoadon['ThoiGian'].dt.month == 5)
hd_t5 = hoadon[mask]

# Loại bỏ hóa đơn hủy/trả lại
trangthai_loai = ['hủy đơn', 'trả lại', 'Đã hủy', 'Hủy', 'hủy']
hd_t5 = hd_t5[~hd_t5['Trạng thái'].astype(str).str.strip().str.lower().isin([s.lower() for s in trangthai_loai])]

if hd_t5.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Gộp chi tiết từ 2 bảng
    ct = pd.concat([ct1, ct2], ignore_index=True)
    ct_t5 = ct[ct['Mã hóa đơn'].isin(hd_t5['Mã hóa đơn'])]
    
    if ct_t5.empty:
        ans = None
        reason = "Không có dữ liệu"
    else:
        ct_t5 = ct_t5.copy()
        ct_t5['ThanhTienNum'] = clean_money(ct_t5['Thành tiền'])
        ans = int(ct_t5['ThanhTienNum'].sum())
```
- **Lỗi lần 2**: Kết quả sai (47808500 != 271866000)
- **Code sửa**:
```python
# Lấy bảng hóa đơn và chi tiết hóa đơn
hoadon = dfs['DanhSachHoaDon'].copy()
ct1 = dfs['DanhSachHoaDonChiTiet_1'].copy()
ct2 = dfs['DanhSachHoaDonChiTiet_2'].copy()

# Chuẩn hóa thời gian hóa đơn
hoadon['ThoiGian'] = parse_date_safe(hoadon['Thời gian'])

# Lọc hóa đơn tháng 5/2025
mask = (hoadon['ThoiGian'].dt.year == 2025) & (hoadon['ThoiGian'].dt.month == 5)
hd_t5 = hoadon[mask]

# Loại bỏ hóa đơn hủy/trả lại
trangthai_loai = ['hủy đơn', 'trả lại', 'Đã hủy', 'Hủy', 'hủy']
hd_t5 = hd_t5[~hd_t5['Trạng thái'].astype(str).str.strip().str.lower().isin([s.lower() for s in trangthai_loai])]

if hd_t5.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Gộp chi tiết từ 2 bảng
    ct = pd.concat([ct1, ct2], ignore_index=True)
    ct_t5 = ct[ct['Mã hóa đơn'].isin(hd_t5['Mã hóa đơn'])]
    
    if ct_t5.empty:
        ans = None
        reason = "Không có dữ liệu"
    else:
        ct_t5 = ct_t5.copy()
        ct_t5['ThanhTienNum'] = clean_money(ct_t5['Thành tiền'])
        ans = int(ct_t5['ThanhTienNum'].sum())
```
- **Lỗi lần 3**: Kết quả sai (47808500 != 271866000)
- **Code sửa**:
```python
# Lấy bảng hóa đơn và chi tiết hóa đơn
hoadon = dfs['DanhSachHoaDon'].copy()
ct1 = dfs['DanhSachHoaDonChiTiet_1'].copy()
ct2 = dfs['DanhSachHoaDonChiTiet_2'].copy()

# Chuẩn hóa thời gian hóa đơn
hoadon['ThoiGian'] = parse_date_safe(hoadon['Thời gian'])

# Lọc hóa đơn tháng 5/2025
mask = (hoadon['ThoiGian'].dt.year == 2025) & (hoadon['ThoiGian'].dt.month == 5)
hd_t5 = hoadon[mask]

# Loại bỏ hóa đơn hủy/trả lại
trangthai_loai = ['hủy đơn', 'trả lại', 'Đã hủy', 'Hủy', 'hủy']
hd_t5 = hd_t5[~hd_t5['Trạng thái'].astype(str).str.strip().str.lower().isin([s.lower() for s in trangthai_loai])]

if hd_t5.empty:
    ans = None
else:
    # Gộp chi tiết từ 2 bảng
    ct = pd.concat([ct1, ct2], ignore_index=True)
    ct_t5 = ct[ct['Mã hóa đơn'].isin(hd_t5['Mã hóa đơn'])]
    
    if ct_t5.empty:
        ans = None
    else:
        ct_t5 = ct_t5.copy()
        ct_t5['ThanhTienNum'] = clean_money(ct_t5['Thành tiền'])
        ans = int(ct_t5['ThanhTienNum'].sum())
```
- **Lưu**: ❌

## Câu 11: q_00d4d6380d03 | Ngày: 2026-06-21
- **Hỏi**: thang 6/2025 hang nao chay nhat
- **Gold**: Gạch ống 8x8x18 Tuynel (Type: string)
- **Plan**: Để trả lời câu hỏi "tháng 6/2025 hàng nào chạy nhat", tôi sẽ thực hiện các bước sau:

1. Lấy bảng 'ban_hang'.
2. Lọc các dòng có ngày '01/06/2025' và '30/06/2025' (tháng 6/2
- **Code**:
```python
df = dfs['ban_hang'].copy()
df['Ngày'] = parse_date_safe(df['Ngày'])
df = df[(df['Ngày'] >= '2025-06-01') & (df['Ngày'] <= '2025-06-30')]
df = df[~df['trang_thai'].str.lower().isin(['đã hủy đơn', 'trả hàng'])]
if df.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    df['Sluong_clean'] = clean_number(df['Sluong'])
    grouped = df.groupby('Sản phẩm')['Sluong_clean'].sum().sort_values(ascending=False)
    ans = [grouped.index[0]]
```
- **Lỗi lần 1**: Kết quả sai (['Đá 1x2'] != Gạch ống 8x8x18 Tuynel)
- **Code sửa**:
```python
df = dfs['ban_hang'].copy()
df['Ngày'] = parse_date_safe(df['Ngày'])
df = df[(df['Ngày'] >= '2025-06-01') & (df['Ngày'] <= '2025-06-30')]
df = df[~df['trang_thai'].str.lower().isin(['đã hủy đơn', 'trả hàng'])]
if df.empty:
    ans = None
else:
    df['Sluong_clean'] = clean_money(df['Sluong'])
    grouped = df.groupby('Sản phẩm')['Sluong_clean'].sum().sort_values(ascending=False)
    ans = [grouped.index[0]]
```
- **Lỗi lần 2**: Kết quả sai (['Đá 1x2'] != Gạch ống 8x8x18 Tuynel)
- **Code sửa**:
```python
df = dfs['ban_hang'].copy()
df['Ngày'] = parse_date_safe(df['Ngày'])
df = df[(df['Ngày'] >= '2025-06-01') & (df['Ngày'] <= '2025-06-30')]
df = df[~df['trang_thai'].str.lower().isin(['đã hủy đơn', 'trả hàng'])]
if df.empty:
    ans = None
else:
    df['Sluong_clean'] = clean_money(df['Sluong'])
    grouped = df.groupby('Sản phẩm')['Sluong_clean'].sum().sort_values(ascending=False)
    ans = [grouped.index[0]]
```
- **Lỗi lần 3**: Kết quả sai (['Đá 1x2'] != Gạch ống 8x8x18 Tuynel)
- **Code sửa**:
```python
df = dfs['ban_hang'].copy()
df['Ngày'] = parse_date_safe(df['Ngày'])
df = df[(df['Ngày'] >= '2025-06-01') & (df['Ngày'] <= '2025-06-30')]
df = df[~df['trang_thai'].str.lower().isin(['đã hủy đơn', 'trả hàng'])]
if df.empty:
    ans = None
else:
    df['Sluong_clean'] = clean_money(df['Sluong'])
    grouped = df.groupby('Sản phẩm')['Sluong_clean'].sum().sort_values(ascending=False)
    ans = [grouped.index[0]]
```
- **Lưu**: ❌

## Câu 12: q_00e9f0bed567 | Ngày: 2026-08-05
- **Hỏi**: dthu các đơn bán qua ddieenj thoại tháng 1/2025 bằng bnhiu % tổng doanh thu tháng 1/2025
- **Gold**: 5.27 (Type: percent)
- **Plan**: Để giải quyết câu hỏi, tôi sẽ thực hiện các bước sau:

1. Lấy bảng 'DanhSachHoaDonChiTiet' và 'DuLieuBanHang_DanhSachHoaDon'.
2. Lọc các hóa đơn có thời gian là 01/01/2025 từ bảng 'DuLieuBanHang_Danh
- **Code**:
```python
import pandas as pd

# Lấy dữ liệu
hoadon = dfs['DuLieuBanHang_DanhSachHoaDon'].copy()

# Làm sạch ngày
hoadon['Thời gian'] = parse_date_safe(hoadon['Thời gian'])

# Lọc hóa đơn tháng 1/2025
mask = (hoadon['Thời gian'].dt.month == 1) & (hoadon['Thời gian'].dt.year == 2025)
hd_t1 = hoadon[mask].copy()

if hd_t1.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Làm sạch tiền
    hd_t1['Tổng sau giảm giá'] = clean_money(hd_t1['Tổng sau giảm giá'])
    
    # Tổng doanh thu tháng 1
    tong_dt = hd_t1['Tổng sau giảm giá'].sum()
    
    # Doanh thu đơn bán qua điện thoại
    dt_phone = hd_t1[hd_t1['Kênh bán'] == 'phone']['Tổng sau giảm giá'].sum()
    
    if tong_dt == 0:
        ans = None
        reason = "Không có dữ liệu"
    else:
        ans = round(dt_phone / tong_dt * 100, 2)
```
- **Lỗi lần 1**: Kết quả sai (5.52 != 5.27)
- **Code sửa**:
```python
import pandas as pd

# Lấy dữ liệu
hoadon = dfs['DuLieuBanHang_DanhSachHoaDon'].copy()

# Làm sạch ngày
hoadon['Thời gian'] = parse_date_safe(hoadon['Thời gian'])

# Lọc hóa đơn tháng 1/2025
mask = (hoadon['Thời gian'].dt.month == 1) & (hoadon['Thời gian'].dt.year == 2025)
hd_t1 = hoadon[mask].copy()

if hd_t1.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Làm sạch tiền
    hd_t1['Tổng sau giảm giá'] = clean_money(hd_t1['Tổng sau giảm giá'])
    
    # Tổng doanh thu tháng 1
    tong_dt = hd_t1['Tổng sau giảm giá'].sum()
    
    # Doanh thu đơn bán qua điện thoại
    dt_phone = hd_t1[hd_t1['Kênh bán'] == 'phone']['Tổng sau giảm giá'].sum()
    
    if tong_dt == 0:
        ans = None
        reason = "Không có dữ liệu"
    else:
        ans = round(dt_phone / tong_dt * 100, 2)
```
- **Lỗi lần 2**: Kết quả sai (5.52 != 5.27)
- **Code sửa**:
```python
import pandas as pd

# Lấy dữ liệu
hoadon = dfs['DuLieuBanHang_DanhSachHoaDon'].copy()

# Làm sạch ngày
hoadon['Thời gian'] = parse_date_safe(hoadon['Thời gian'])

# Lọc hóa đơn tháng 1/2025
mask = (hoadon['Thời gian'].dt.month == 1) & (hoadon['Thời gian'].dt.year == 2025)
hd_t1 = hoadon[mask].copy()

if hd_t1.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Làm sạch tiền
    hd_t1['Tổng sau giảm giá'] = clean_money(hd_t1['Tổng sau giảm giá'])
    
    # Tổng doanh thu tháng 1
    tong_dt = hd_t1['Tổng sau giảm giá'].sum()
    
    # Doanh thu đơn bán qua điện thoại
    dt_phone = hd_t1[hd_t1['Kênh bán'] == 'phone']['Tổng sau giảm giá'].sum()
    
    if tong_dt == 0:
        ans = None
        reason = "Không có dữ liệu"
    else:
        ans = round(dt_phone / tong_dt * 100, 2)
```
- **Lỗi lần 3**: Kết quả sai (5.52 != 5.27)
- **Code sửa**:
```python
import pandas as pd

# Lấy dữ liệu
hoadon = dfs['DuLieuBanHang_DanhSachHoaDon'].copy()

# Làm sạch ngày
hoadon['Thời gian'] = parse_date_safe(hoadon['Thời gian'])

# Lọc hóa đơn tháng 1/2025
mask = (hoadon['Thời gian'].dt.month == 1) & (hoadon['Thời gian'].dt.year == 2025)
hd_t1 = hoadon[mask].copy()

if hd_t1.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Làm sạch tiền
    hd_t1['Tổng sau giảm giá'] = clean_money(hd_t1['Tổng sau giảm giá'])
    
    # Tổng doanh thu tháng 1
    tong_dt = hd_t1['Tổng sau giảm giá'].sum()
    
    # Doanh thu đơn bán qua điện thoại
    dt_phone = hd_t1[hd_t1['Kênh bán'] == 'phone']['Tổng sau giảm giá'].sum()
    
    if tong_dt == 0:
        ans = None
        reason = "Không có dữ liệu"
    else:
        ans = round(dt_phone / tong_dt * 100, 2)
```
- **Lưu**: ❌

## Câu 13: q_00eadfc5c599 | Ngày: 2026-06-02
- **Hỏi**: đếm số đơn đã huỷ trong tháng 12/2025
- **Gold**: 64 (Type: number)
- **Plan**: Để giải quyết câu hỏi "đếm số đơn đã huỷ trong tháng 12/2025", chúng ta cần thực hiện các bước sau:

1. Lấy bảng 'DonHang_ChiTiet'.
2. Lọc các dòng có ngày đặt hàng trong tháng 12/2025 và trạng thái đơn hàng là 'Đã hủy'.
- **Code**:
```python
df = dfs['DonHang_ChiTiet'].copy()
df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])
mask = (df['Ngày đặt hàng'].dt.month == 12) & (df['Ngày đặt hàng'].dt.year == 2025) & (df['Trạng thái đơn hàng'] == 'Đã hủy')
filtered = df[mask]
if filtered.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    ans = filtered['Mã đơn hàng'].nunique()
```
- **Lưu**: ✅

## Câu 14: q_0139627bccae | Ngày: 2025-10-18
- **Hỏi**: check gium hnay cua hang co bao nhiu don
- **Gold**: 107 (Type: number)
- **Plan**: Lấy bảng DonHang_ChiTiet, lọc theo ngày 2025-10-18 và tên khách hàng là "Hà Hồng Bích", sau đó tính tổng số lượng sản phẩm (cột Số lượng sản phẩm) để biết hàng hóa đã được đặt bao nhiêu hộp.
- **Code**:
```python
df = dfs['DonHang_ChiTiet'].copy()
df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])
df['Số lượng sản phẩm'] = clean_number(df['Số lượng sản phẩm'])

target_date = pd.Timestamp('2025-10-18')
filtered = df[(df['Ngày đặt hàng'] == target_date) & (df['Tên khách hàng'] == 'Hà Hồng Bích')]

if filtered.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    ans = filtered['Số lượng sản phẩm'].sum()
```
- **Lỗi lần 1**: Kết quả sai (None != 107)
- **Code sửa**:
```python
df = dfs['DonHang_ChiTiet'].copy()
df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])

target_date = pd.Timestamp('2025-10-18')
filtered = df[df['Ngày đặt hàng'] == target_date]

ans = filtered['Mã đơn hàng'].nunique() if not filtered.empty else 0
```
- **Lỗi lần 2**: Kết quả sai (111 != 107)
- **Code sửa**:
```python
df = dfs['DonHang_ChiTiet'].copy()
df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])

target_date = pd.Timestamp('2025-10-18')
filtered = df[df['Ngày đặt hàng'] == target_date]

ans = filtered['Mã đơn hàng'].nunique() if not filtered.empty else 0
```
- **Lỗi lần 3**: Kết quả sai (111 != 107)
- **Code sửa**:
```python
df = dfs['DonHang_ChiTiet'].copy()
df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])

target_date = pd.Timestamp('2025-10-18')
filtered = df[df['Ngày đặt hàng'] == target_date]

ans = filtered['Mã đơn hàng'].nunique() if not filtered.empty else 0
```
- **Lưu**: ❌

## Câu 15: q_0166f82c0223 | Ngày: 2026-06-02
- **Hỏi**: thang 9/2025 cua hang co bnhiu % don bi huy
- **Gold**: 1.66 (Type: percent)
- **Plan**: Để giải quyết câu hỏi này, chúng ta cần thực hiện các bước sau:

1. Lấy bảng 'DanhSachQuyDoi' để lấy tỉ lệ quy đổi từ hộp thành cái.
2. Lấy bảng 'DonHang_ChiTiet' và lọc các đơn hàng đặt trong tháng 9/2025.
3. Lọc các đơn hàng đã
- **Code**:
```python
df = dfs['DonHang_ChiTiet'].copy()
df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])
df_thang9 = df[(df['Ngày đặt hàng'].dt.month == 9) & (df['Ngày đặt hàng'].dt.year == 2025)]

if df_thang9.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    tong_don = len(df_thang9)
    so_don_huy = len(df_thang9[df_thang9['Trạng thái đơn hàng'] == 'Đã hủy'])
    ans = round(so_don_huy / tong_don * 100, 2)
```
- **Lỗi lần 1**: Kết quả sai (1.67 != 1.66)
- **Code sửa**:
```python
df = dfs['DonHang_ChiTiet'].copy()
df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])
df_thang9 = df[(df['Ngày đặt hàng'].dt.month == 9) & (df['Ngày đặt hàng'].dt.year == 2025)]

if df_thang9.empty:
    ans = None
else:
    # Đếm đơn hàng duy nhất (không đếm theo dòng chi tiết)
    don_hang = df_thang9.drop_duplicates(subset=['Mã đơn hàng']) if 'Mã đơn hàng' in df_thang9.columns else df_thang9
    tong_don = len(don_hang)
    so_don_huy = len(don_hang[don_hang['Trạng thái đơn hàng'] == 'Đã hủy'])
    ans = round(so_don_huy / tong_don * 100, 2)
```
- **Lưu**: ✅

## Câu 16: q_0174cb13db2a | Ngày: 2026-09-10
- **Hỏi**: tháng này cửa hàng đã chở giao bao nhiêu đợt hàng cho khách nhỉ
- **Gold**: 290 (Type: number)
- **Plan**: Để trả lời câu hỏi này, tôi sẽ thực hiện các bước sau:

1. Lấy bảng 'Bảng: 'Búng kphiu giao hản''
2. Lọc các hàng có Mã đơn hàng tương ứng với 'ORD000005' và 'ORD000007'
3. Tính tổng giá trị của cột 'L
- **Code**:
```python
# Lấy bảng phiếu giao hàng
df = dfs['Bảng: \'Búng kphiu giao hản\''].copy()

# Parse ngày giao hàng
df['Ngày giao hàng'] = parse_date_safe(df['Ngày giao hàng'])

# Ngày chốt: 2026-09-10 -> tháng này là tháng 9/2026
start = pd.Timestamp('2026-09-01')
end = pd.Timestamp('2026-09-30')

# Lọc các đợt giao trong tháng này
mask = (df['Ngày giao hàng'] >= start) & (df['Ngày giao hàng'] <= end)
df_month = df[mask]

if df_month.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Đếm số đợt hàng (số lần giao) - mỗi dòng là 1 đợt giao
    ans = int(len(df_month))
```
- **Lỗi lần 1**: Lỗi Runtime: "Bảng: 'Búng kphiu giao hản'"
- **Code sửa**:
```python
# Lấy bảng phiếu giao hàng - tên bảng có thể bị lỗi encoding
# Tìm bảng phù hợp trong dfs
delivery_key = None
for k in dfs.keys():
    if 'giao' in k.lower() and ('phi' in k.lower() or 'phieu' in k.lower()):
        delivery_key = k
        break

if delivery_key is None:
    # Thử tìm bảng có cột 'Ngày giao hàng'
    for k, v in dfs.items():
        if hasattr(v, 'columns') and any('Ngày giao' in str(c) for c in v.columns):
            delivery_key = k
            break

df = dfs[delivery_key].copy()

# Parse ngày giao hàng
df['Ngày giao hàng'] = parse_date_safe(df['Ngày giao hàng'])

# Ngày chốt: 2026-09-10 -> tháng này là tháng 9/2026
start = pd.Timestamp('2026-09-01')
end = pd.Timestamp('2026-09-30')

# Lọc các đợt giao trong tháng này
mask = (df['Ngày giao hàng'] >= start) & (df['Ngày giao hàng'] <= end)
df_month = df[mask]

if df_month.empty:
    ans = None
else:
    # Đếm số đợt hàng (số lần giao) - mỗi dòng là 1 đợt giao
    ans = int(len(df_month))
```
- **Lỗi lần 2**: Kết quả sai (664 != 290)
- **Code sửa**:
```python
# Lấy bảng phiếu giao hàng
delivery_key = None
for k in dfs.keys():
    if 'giao' in k.lower() and ('phi' in k.lower() or 'phieu' in k.lower()):
        delivery_key = k
        break

if delivery_key is None:
    for k, v in dfs.items():
        if hasattr(v, 'columns') and any('Ngày giao' in str(c) for c in v.columns):
            delivery_key = k
            break

df = dfs[delivery_key].copy()

# Parse ngày giao hàng
df['Ngày giao hàng'] = parse_date_safe(df['Ngày giao hàng'])

# Ngày chốt: 2026-09-10 -> tháng này là tháng 9/2026
start = pd.Timestamp('2026-09-01')
end = pd.Timestamp('2026-09-30')

# Lọc các đợt giao trong tháng này
mask = (df['Ngày giao hàng'] >= start) & (df['Ngày giao hàng'] <= end)
df_month = df[mask]

if df_month.empty:
    ans = None
else:
    # Tìm cột số lượng/khối lượng để tính tổng số đợt hàng
    qty_col = None
    for c in df_month.columns:
        cl = str(c).lower()
        if any(x in cl for x in ['số lượng', 'so luong', 'khối lượng', 'khoi luong', 'số đợt', 'so dot', 'quantity', 'qty']):
            qty_col = c
            break
    
    if qty_col is not None:
        ans = int(clean_money(df_month[qty_col]).sum())
    else:
        ans = int(len(df_month))
```
- **Lỗi lần 3**: Kết quả sai (1594 != 290)
- **Code sửa**:
```python
# Lấy bảng phiếu giao hàng
delivery_key = None
for k in dfs.keys():
    if 'giao' in k.lower() and ('phi' in k.lower() or 'phieu' in k.lower()):
        delivery_key = k
        break

if delivery_key is None:
    for k, v in dfs.items():
        if hasattr(v, 'columns') and any('Ngày giao' in str(c) for c in v.columns):
            delivery_key = k
            break

df = dfs[delivery_key].copy()

# Parse ngày giao hàng
df['Ngày giao hàng'] = parse_date_safe(df['Ngày giao hàng'])

# Ngày chốt: 2026-09-10 -> tháng này là tháng 9/2026
start = pd.Timestamp('2026-09-01')
end = pd.Timestamp('2026-09-30')

# Lọc các đợt giao trong tháng này
mask = (df['Ngày giao hàng'] >= start) & (df['Ngày giao hàng'] <= end)
df_month = df[mask]

# Đếm số đợt hàng (số dòng/phiếu giao), không cộng số lượng
ans = int(len(df_month))
```
- **Lưu**: ❌

## Câu 17: q_0183529f9d61 | Ngày: 2026-05-25
- **Hỏi**: dthu 3 tháng liền nhau kết thúc ở tháng 6/2025 là bao nhiêu mỗi tháng, từ tháng cũ đến tháng mới
- **Gold**: [287435200, 346554700, 309693800] (Type: list)
- **Plan**: Để giải quyết câu hỏi này, tôi sẽ thực hiện các bước sau:

1. Lấy bảng 'BanHang_BanTheoLo' để lấy thông tin về số lượng và giá bán của từng lô hàng.
2. Sử dụng bảng 'BanHang_ChiTietHoaDon' để lấy giá bán niêm yết và thanh toán cho từng lô hàng.
- **Code**:
```python
# Lấy bảng cần thiết
hoadon = dfs['BanHang_HoaDon'].copy()
chitiet = dfs['BanHang_ChiTietHoaDon'].copy()

# Làm sạch ngày
hoadon['NgayBan_parsed'] = parse_date_safe(hoadon['Ngày bán'])
hoadon['GioTao_parsed'] = parse_date_safe(hoadon['Giờ tạo đơn'])

# Ưu tiên Giờ tạo đơn, fallback Ngày bán
hoadon['NgayChuan'] = hoadon['GioTao_parsed'].fillna(hoadon['NgayBan_parsed'])

# Lọc 3 tháng liền nhau kết thúc ở tháng 6/2025: tháng 4, 5, 6 năm 2025
mask = (hoadon['NgayChuan'].dt.year == 2025) & (hoadon['NgayChuan'].dt.month.isin([4, 5, 6]))
hd_loc = hoadon[mask].copy()

if hd_loc.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Làm sạch tiền
    hd_loc['TongTien_clean'] = clean_money(hd_loc['Tong tien'])
    hd_loc['Thang'] = hd_loc['NgayChuan'].dt.month

    # Tính doanh thu theo tháng
    doanh_thu = hd_loc.groupby('Thang')['TongTien_clean'].sum().sort_index()

    # Đảm bảo đủ 3 tháng
    ket_qua = {}
    for m in [4, 5, 6]:
        ket_qua[m] = float(doanh_thu.get(m, 0))

    ans = ket_qua
```
- **Lỗi lần 1**: Kết quả sai ({4: 294664600.0, 5: 351770300.0, 6: 314579700.0} != [287435200, 346554700, 309693800])
- **Code sửa**:
```python
# Lấy bảng cần thiết
hoadon = dfs['BanHang_HoaDon'].copy()
chitiet = dfs['BanHang_ChiTietHoaDon'].copy()

# Làm sạch ngày
hoadon['NgayBan_parsed'] = parse_date_safe(hoadon['Ngày bán'])
hoadon['GioTao_parsed'] = parse_date_safe(hoadon['Giờ tạo đơn'])

# Ưu tiên Giờ tạo đơn, fallback Ngày bán
hoadon['NgayChuan'] = hoadon['GioTao_parsed'].fillna(hoadon['NgayBan_parsed'])

# Lọc 3 tháng liền nhau kết thúc ở tháng 6/2025: tháng 4, 5, 6 năm 2025
mask = (hoadon['NgayChuan'].dt.year == 2025) & (hoadon['NgayChuan'].dt.month.isin([4, 5, 6]))
hd_loc = hoadon[mask].copy()

if hd_loc.empty:
    ans = None
else:
    # Làm sạch tiền
    hd_loc['TongTien_clean'] = clean_money(hd_loc['Tong tien'])
    hd_loc['Thang'] = hd_loc['NgayChuan'].dt.month

    # Tính doanh thu theo tháng
    doanh_thu = hd_loc.groupby('Thang')['TongTien_clean'].sum().sort_index()

    # Đảm bảo đủ 3 tháng, trả về list theo thứ tự tháng cũ -> mới
    ans = [float(doanh_thu.get(m, 0)) for m in [4, 5, 6]]
```
- **Lỗi lần 2**: Kết quả sai (['294664600.0', '351770300.0', '314579700.0'] != [287435200, 346554700, 309693800])
- **Code sửa**:
```python
# Lấy bảng cần thiết
hoadon = dfs['BanHang_HoaDon'].copy()
chitiet = dfs['BanHang_ChiTietHoaDon'].copy()

# Làm sạch ngày
hoadon['NgayBan_parsed'] = parse_date_safe(hoadon['Ngày bán'])
hoadon['GioTao_parsed'] = parse_date_safe(hoadon['Giờ tạo đơn'])

# Ưu tiên Giờ tạo đơn, fallback Ngày bán
hoadon['NgayChuan'] = hoadon['GioTao_parsed'].fillna(hoadon['NgayBan_parsed'])

# Lọc 3 tháng liền nhau kết thúc ở tháng 6/2025: tháng 4, 5, 6 năm 2025
mask = (hoadon['NgayChuan'].dt.year == 2025) & (hoadon['NgayChuan'].dt.month.isin([4, 5, 6]))
hd_loc = hoadon[mask].copy()

if hd_loc.empty:
    ans = None
else:
    # Làm sạch tiền
    hd_loc['TongTien_clean'] = clean_money(hd_loc['Tong tien'])
    hd_loc['Thang'] = hd_loc['NgayChuan'].dt.month

    # Tính doanh thu theo tháng
    doanh_thu = hd_loc.groupby('Thang')['TongTien_clean'].sum().sort_index()

    # Đảm bảo đủ 3 tháng, trả về list theo thứ tự tháng cũ -> mới
    ans = [float(doanh_thu.get(m, 0)) for m in [4, 5, 6]]
```
- **Lỗi lần 3**: Kết quả sai (['294664600.0', '351770300.0', '314579700.0'] != [287435200, 346554700, 309693800])
- **Code sửa**:
```python
# Lấy bảng cần thiết
hoadon = dfs['BanHang_HoaDon'].copy()
chitiet = dfs['BanHang_ChiTietHoaDon'].copy()

# Làm sạch ngày
hoadon['NgayBan_parsed'] = parse_date_safe(hoadon['Ngày bán'])
hoadon['GioTao_parsed'] = parse_date_safe(hoadon['Giờ tạo đơn'])

# Ưu tiên Giờ tạo đơn, fallback Ngày bán
hoadon['NgayChuan'] = hoadon['GioTao_parsed'].fillna(hoadon['NgayBan_parsed'])

# Lọc 3 tháng liền nhau kết thúc ở tháng 6/2025: tháng 4, 5, 6 năm 2025
mask = (hoadon['NgayChuan'].dt.year == 2025) & (hoadon['NgayChuan'].dt.month.isin([4, 5, 6]))
hd_loc = hoadon[mask].copy()

if hd_loc.empty:
    ans = None
else:
    # Làm sạch tiền
    hd_loc['TongTien_clean'] = clean_money(hd_loc['Tong tien'])
    hd_loc['Thang'] = hd_loc['NgayChuan'].dt.month

    # Tính doanh thu theo tháng
    doanh_thu = hd_loc.groupby('Thang')['TongTien_clean'].sum().sort_index()

    # Đảm bảo đủ 3 tháng, trả về list theo thứ tự tháng cũ -> mới
    ans = [float(doanh_thu.get(m, 0)) for m in [4, 5, 6]]
```
- **Lưu**: ❌

## Câu 18: q_0194d8d10f17 | Ngày: 2026-08-19
- **Hỏi**: Tính đến hết ngày 19/08/2026, có bao nhiêu khách còn nợ cửa hàng?
- **Gold**: 35 (Type: number)
- **Plan**: Để giải quyết câu hỏi này, tôi sẽ thực hiện các bước sau:

1. Lấy bảng 'don_hang' và lọc các đơn hàng có Mã chứng từ (Ma don) kết thúc với ngày 19/08/2026.
2. Tính tổng số khách hàng (Số KH) còn nợ (không đã hoàn thành, không đã hủy
- **Code**:
```python
don_hang = dfs['don_hang'].copy()
don_hang['NgayBan'] = parse_date_safe(don_hang['NgayBan'])
don_hang['ConNo'] = clean_money(don_hang['Còn lại'])

cutoff = pd.Timestamp('2026-08-19')
mask = (don_hang['NgayBan'] <= cutoff) & (don_hang['ConNo'] > 0)
df = don_hang[mask]

if df.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    ans = df['Số KH'].nunique()
```
- **Lỗi lần 1**: Kết quả sai (25 != 35)
- **Code sửa**:
```python
don_hang = dfs['don_hang'].copy()
don_hang['NgayBan'] = parse_date_safe(don_hang['NgayBan'])
don_hang['ConNo'] = clean_money(don_hang['Còn lại'])

cutoff = pd.Timestamp('2026-08-19')
mask = (don_hang['NgayBan'] <= cutoff) & (don_hang['ConNo'] > 0)
df = don_hang[mask]

if df.empty:
    ans = None
else:
    ans = int(df['Số KH'].nunique())
```
- **Lỗi lần 2**: Kết quả sai (25 != 35)
- **Code sửa**:
```python
don_hang = dfs['don_hang'].copy()
don_hang['NgayBan'] = parse_date_safe(don_hang['NgayBan'])
don_hang['ConNo'] = clean_money(don_hang['Còn lại'])

cutoff = pd.Timestamp('2026-08-19')
mask = (don_hang['NgayBan'] <= cutoff) & (don_hang['ConNo'] > 0)
df = don_hang[mask]

if df.empty:
    ans = None
else:
    ans = int(df['Số KH'].nunique())
```
- **Lỗi lần 3**: Kết quả sai (25 != 35)
- **Code sửa**:
```python
don_hang = dfs['don_hang'].copy()
don_hang['NgayBan'] = parse_date_safe(don_hang['NgayBan'])
don_hang['ConNo'] = clean_money(don_hang['Còn lại'])

cutoff = pd.Timestamp('2026-08-19')
mask = (don_hang['NgayBan'] <= cutoff) & (don_hang['ConNo'] > 0)
df = don_hang[mask]

if df.empty:
    ans = None
else:
    ans = int(df['Số KH'].nunique())
```
- **Lưu**: ❌

## Câu 19: q_019ec94d9799 | Ngày: 2026-08-19
- **Hỏi**: 3 mặt hàng bán chạy nhất tuần này là những mặt hàng nào?
- **Gold**: ['Cà phê sữa (M)', 'Trà đào cam sả (M)', 'Cà phê đen (M)'] (Type: list)
- **Plan**: Để trả lời câu hỏi này, tôi sẽ thực hiện các bước sau:

1. Lấy bảng 'DanhSachHoaDon' và lọc các hóa đơn trong tuần 2026-08-19.
2. Tính tổng số lượng hàng hóa bán ra từ các hóa đơn này.
3. Lọc ra các mặt hàng có tổng số lượng bán ra
- **Code**:
```python
# Lấy bảng hóa đơn và chi tiết hóa đơn
hoadon = dfs['DanhSachHoaDon'].copy()
chitiet1 = dfs['DanhSachHoaDonChiTiet_1'].copy()
chitiet2 = dfs['DanhSachHoaDonChiTiet_2'].copy()

# Chuẩn hóa ngày
hoadon['Thời gian'] = parse_date_safe(hoadon['Thời gian'])
hoadon['Thời gian tạo'] = parse_date_safe(hoadon['Thời gian tạo'])

# Ngày chốt
ngay_chot = pd.Timestamp('2026-08-19')
# Tuần chứa ngày chốt (thứ 2 -> chủ nhật)
start_week = ngay_chot - pd.Timedelta(days=ngay_chot.weekday())
end_week = start_week + pd.Timedelta(days=6)

# Lọc hóa đơn trong tuần, loại bỏ hủy/trả lại
trang_thai_huy = ['hủy đơn', 'Hủy đơn', 'Đã hủy', 'đã hủy', 'trả lại', 'Trả lại']
hoadon_tuan = hoadon[
    (hoadon['Thời gian'] >= start_week) &
    (hoadon['Thời gian'] <= end_week) &
    (~hoadon['Trạng thái'].isin(trang_thai_huy))
]

if hoadon_tuan.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    ma_hd = set(hoadon_tuan['Mã hóa đơn'].astype(str))
    
    # Gộp chi tiết từ 2 bảng
    ct = pd.concat([chitiet1, chitiet2], ignore_index=True)
    ct = ct[ct['Mã hóa đơn'].astype(str).isin(ma_hd)].copy()
    
    if ct.empty:
        ans = None
        reason = "Không có dữ liệu"
    else:
        ct['Số lượng'] = clean_number(ct['Số lượng'])
        ct['Số lượng quy đổi'] = clean_number(ct['Số lượng quy đổi'])
        
        # Tổng số lượng bán ra theo mặt hàng
        tong = ct.groupby('Tên hàng', as_index=False)['Số lượng'].sum()
        tong = tong.sort_values('Số lượng', ascending=False).head(3)
        ans = tong['Tên hàng'].tolist()
```
- **Lỗi lần 1**: Kết quả sai (None != ['Cà phê sữa (M)', 'Trà đào cam sả (M)', 'Cà phê đen (M)'])
- **Code sửa**:
```python
# Lấy bảng hóa đơn và chi tiết hóa đơn
hoadon = dfs['DanhSachHoaDon'].copy()
chitiet1 = dfs['DanhSachHoaDonChiTiet_1'].copy()
chitiet2 = dfs['DanhSachHoaDonChiTiet_2'].copy()

# Chuẩn hóa ngày
hoadon['Thời gian'] = parse_date_safe(hoadon['Thời gian'])
hoadon['Thời gian tạo'] = parse_date_safe(hoadon['Thời gian tạo'])

# Ngày chốt
ngay_chot = pd.Timestamp('2026-08-19')
# Tuần chứa ngày chốt (thứ 2 -> chủ nhật)
start_week = ngay_chot - pd.Timedelta(days=ngay_chot.weekday())
end_week = start_week + pd.Timedelta(days=6)

# Lọc hóa đơn trong tuần, loại bỏ hủy/trả lại
trang_thai_huy = ['hủy đơn', 'Hủy đơn', 'Đã hủy', 'đã hủy', 'trả lại', 'Trả lại']
hoadon_tuan = hoadon[
    (hoadon['Thời gian'] >= start_week) &
    (hoadon['Thời gian'] <= end_week) &
    (~hoadon['Trạng thái'].isin(trang_thai_huy))
]

if hoadon_tuan.empty:
    ans = None
else:
    ma_hd = set(hoadon_tuan['Mã hóa đơn'].astype(str))
    
    # Gộp chi tiết từ 2 bảng
    ct = pd.concat([chitiet1, chitiet2], ignore_index=True)
    ct = ct[ct['Mã hóa đơn'].astype(str).isin(ma_hd)].copy()
    
    if ct.empty:
        ans = None
    else:
        ct['Số lượng'] = clean_number(ct['Số lượng'])
        ct['Số lượng quy đổi'] = clean_number(ct['Số lượng quy đổi'])
        
        # Tổng số lượng bán ra theo mặt hàng (dùng số lượng quy đổi)
        tong = ct.groupby('Tên hàng', as_index=False)['Số lượng quy đổi'].sum()
        tong = tong.sort_values('Số lượng quy đổi', ascending=False).head(3)
        ans = tong['Tên hàng'].tolist()
```
- **Lỗi lần 2**: Kết quả sai (None != ['Cà phê sữa (M)', 'Trà đào cam sả (M)', 'Cà phê đen (M)'])
- **Code sửa**:
```python
# Lấy bảng hóa đơn và chi tiết hóa đơn
hoadon = dfs['DanhSachHoaDon'].copy()
chitiet1 = dfs['DanhSachHoaDonChiTiet_1'].copy()
chitiet2 = dfs['DanhSachHoaDonChiTiet_2'].copy()

# Chuẩn hóa ngày
hoadon['Thời gian'] = parse_date_safe(hoadon['Thời gian'])
hoadon['Thời gian tạo'] = parse_date_safe(hoadon['Thời gian tạo'])

# Ngày chốt
ngay_chot = pd.Timestamp('2026-08-19')
# Tuần chứa ngày chốt (thứ 2 -> chủ nhật)
start_week = ngay_chot - pd.Timedelta(days=ngay_chot.weekday())
end_week = start_week + pd.Timedelta(days=6)

# Lọc hóa đơn trong tuần, loại bỏ hủy/trả lại
trang_thai_huy = ['hủy đơn', 'Hủy đơn', 'Đã hủy', 'đã hủy', 'trả lại', 'Trả lại']
hoadon_tuan = hoadon[
    (hoadon['Thời gian'] >= start_week) &
    (hoadon['Thời gian'] <= end_week) &
    (~hoadon['Trạng thái'].isin(trang_thai_huy))
]

if hoadon_tuan.empty:
    ans = None
else:
    ma_hd = set(hoadon_tuan['Mã hóa đơn'].astype(str))
    
    # Gộp chi tiết từ 2 bảng
    ct = pd.concat([chitiet1, chitiet2], ignore_index=True)
    ct = ct[ct['Mã hóa đơn'].astype(str).isin(ma_hd)].copy()
    
    if ct.empty:
        ans = None
    else:
        ct['Số lượng'] = clean_number(ct['Số lượng'])
        ct['Số lượng quy đổi'] = clean_number(ct['Số lượng quy đổi'])
        
        # Tổng số lượng bán ra theo mặt hàng (dùng số lượng quy đổi)
        tong = ct.groupby('Tên hàng', as_index=False)['Số lượng quy đổi'].sum()
        tong = tong.sort_values('Số lượng quy đổi', ascending=False).head(3)
        ans = tong['Tên hàng'].tolist()
```
- **Lỗi lần 3**: Kết quả sai (None != ['Cà phê sữa (M)', 'Trà đào cam sả (M)', 'Cà phê đen (M)'])
- **Code sửa**:
```python
# Lấy bảng hóa đơn và chi tiết hóa đơn
hoadon = dfs['DanhSachHoaDon'].copy()
chitiet1 = dfs['DanhSachHoaDonChiTiet_1'].copy()
chitiet2 = dfs['DanhSachHoaDonChiTiet_2'].copy()

# Chuẩn hóa ngày
hoadon['Thời gian'] = parse_date_safe(hoadon['Thời gian'])
hoadon['Thời gian tạo'] = parse_date_safe(hoadon['Thời gian tạo'])

# Ngày chốt
ngay_chot = pd.Timestamp('2026-08-19')
# Tuần chứa ngày chốt (thứ 2 -> chủ nhật)
start_week = ngay_chot - pd.Timedelta(days=ngay_chot.weekday())
end_week = start_week + pd.Timedelta(days=6)

# Lọc hóa đơn trong tuần, loại bỏ hủy/trả lại
trang_thai_huy = ['hủy đơn', 'Hủy đơn', 'Đã hủy', 'đã hủy', 'trả lại', 'Trả lại']
hoadon_tuan = hoadon[
    (hoadon['Thời gian'] >= start_week) &
    (hoadon['Thời gian'] <= end_week) &
    (~hoadon['Trạng thái'].isin(trang_thai_huy))
]

if hoadon_tuan.empty:
    ans = None
else:
    ma_hd = set(hoadon_tuan['Mã hóa đơn'].astype(str))
    
    # Gộp chi tiết từ 2 bảng
    ct = pd.concat([chitiet1, chitiet2], ignore_index=True)
    ct = ct[ct['Mã hóa đơn'].astype(str).isin(ma_hd)].copy()
    
    if ct.empty:
        ans = None
    else:
        ct['Số lượng'] = clean_number(ct['Số lượng'])
        ct['Số lượng quy đổi'] = clean_number(ct['Số lượng quy đổi'])
        
        # Tổng số lượng bán ra theo mặt hàng (dùng số lượng quy đổi)
        tong = ct.groupby('Tên hàng', as_index=False)['Số lượng quy đổi'].sum()
        tong = tong.sort_values('Số lượng quy đổi', ascending=False).head(3)
        ans = tong['Tên hàng'].tolist()
```
- **Lưu**: ❌

## Câu 20: q_01a252a82858 | Ngày: 2026-06-02
- **Hỏi**: Ngày 14/07/2025 cửa hàng bán Cà phê muối (L) với đơn giá bao nhiêu một ly?
- **Gold**: 41000 (Type: number)
- **Plan**: Để trả lời câu hỏi này, tôi sẽ cần thực hiện các bước sau:

1. Lấy bảng DonHang_ChiTiet.
2. Lọc các dòng có ngày đặt hàng là 14/07/2025.
3. Tìm dòng có tên sản phẩm là "Cà phê muối (L)".
4. Lấy giá của dòng đó.
- **Code**:
```python
df = dfs['DonHang_ChiTiet'].copy()
df['Ngày đặt hàng'] = parse_date_safe(df['Ngày đặt hàng'])
df['Giá sản phẩm'] = clean_money(df['Giá sản phẩm'])

target_date = parse_date_safe(pd.Series(['14/07/2025']))[0]
filtered = df[(df['Ngày đặt hàng'] == target_date) & (df['Tên sản phẩm'] == 'Cà phê muối (L)')]

if filtered.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    ans = filtered['Giá sản phẩm'].iloc[0]
```
- **Lưu**: ✅

## Câu 21: q_01a28f2233bd | Ngày: 2026-07-31
- **Hỏi**: gia ban mot ly soda chanh day (m) vao ngay 01/12/2025 la bn
- **Gold**: 37000 (Type: number)
- **Plan**: Lấy bảng 'Danh s├ích h├áng h├│a', lọc cột 'Tên hàng hóa' bằng 'Cà phê sữa (M)' và 'Mã vạch EAN' bằng '8937352408968', sau đó lấy giá bán tương ứng.
- **Code**:
```python
# Lấy bảng danh sách hàng hóa
df_hh = dfs['Danh s├ích h├áng h├│a']

# Lọc theo Tên hàng hóa và Mã vạch EAN
df_filtered = df_hh[
    (df_hh['Tên hàng hóa'] == 'Cà phê sữa (M)') &
    (df_hh['Mã vạch EAN'] == '8937352408968')
]

if df_filtered.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Làm sạch cột giá bán
    gia_ban = clean_money(df_filtered['Giá bán'])
    ans = float(gia_ban.iloc[0])
```
- **Lỗi lần 1**: Kết quả sai (None != 37000)
- **Code sửa**:
```python
# Lấy bảng danh sách hàng hóa
df_hh = dfs['Danh sách hàng hóa']

# Lọc theo Tên hàng hóa: "Soda chanh đầy (M)"
df_filtered = df_hh[
    (df_hh['Tên hàng hóa'] == 'Soda chanh đầy (M)')
]

if df_filtered.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    # Làm sạch cột giá bán
    gia_ban = clean_money(df_filtered['Giá bán'])
    ans = float(gia_ban.iloc[0])
```
- **Lỗi lần 2**: Lỗi Runtime: 'Danh sách hàng hóa'
- **Code sửa**:
```python
# Lấy bảng danh sách hàng hóa
df_hh = dfs['Danh sách hàng hóa']

# Lọc theo Tên hàng hóa: "Soda chanh đầy (M)"
df_filtered = df_hh[
    (df_hh['Tên hàng hóa'] == 'Soda chanh đầy (M)')
]

if df_filtered.empty:
    ans = None
else:
    # Làm sạch cột giá bán
    gia_ban = clean_money(df_filtered['Giá bán'])
    ans = float(gia_ban.iloc[0])
```
- **Lỗi lần 3**: Lỗi Runtime: 'Danh sách hàng hóa'
- **Code sửa**:
```python
# Lấy bảng danh sách hàng hóa
df_hh = dfs['Danh sách hàng hóa']

# Lọc theo Tên hàng hóa: "Soda chanh đầy (M)"
df_filtered = df_hh[
    (df_hh['Tên hàng hóa'] == 'Soda chanh đầy (M)')
]

if df_filtered.empty:
    ans = None
else:
    # Làm sạch cột giá bán
    gia_ban = clean_money(df_filtered['Giá bán'])
    ans = float(gia_ban.iloc[0])
```
- **Lưu**: ❌

## Câu 22: q_01a47607f90c | Ngày: 2026-08-11
- **Hỏi**: tổng dthu trong ngày hôm nay là bao nhiêu vaayj
- **Gold**: 39793500 (Type: number)
- **Plan**: Lấy bảng 'DanhSachHoaDon_04.2025', lọc ngày 2026-08-11, tính tổng cột 'Tổng tiền hàng'.
- **Code**:
```python
df = dfs['DanhSachHoaDon_08.2026'].copy()
df['Thời gian'] = parse_date_safe(df['Thời gian'])
df['Tổng tiền hàng'] = clean_money(df['Tổng tiền hàng'])
target = pd.Timestamp('2026-08-11')
filtered = df[df['Thời gian'].dt.normalize() == target]
if filtered.empty:
    ans = None
    reason = "Không có dữ liệu"
else:
    ans = filtered['Tổng tiền hàng'].sum()
```
- **Lưu**: ✅

## Câu 23: q_01b914589609 | Ngày: 2025-02-19
- **Hỏi**: Cho tôi biết dthu 30 ngày gần nhất
- **Gold**: 730984600 (Type: number)
- **Plan**: Để trả lời câu hỏi này, tôi sẽ thực hiện các bước sau:

1. Lấy bảng 'BangGia' và lọc các dòng có 'Ngày áp dụng' gần nhất với ngày 2025-02-19.
2. Hiển thị giá mới tương ứng với hàng gần nhất.

Lý thuyết:
- 'Ngày áp dụng' trong bảng
- **Code**:
```python
# Lấy tất cả các bảng SoBanHang
sales_tables = [k for k in dfs.keys() if k.startswith('SoBanHang_')]

# Ngày chốt
end_date = pd.Timestamp('2025-02-19')
start_date = end_date - pd.Timedelta(days=30)

total_revenue = 0
has_data = False

for tbl in sales_tables:
    df = dfs[tbl].copy()
    if df.empty:
        continue
    df['_date'] = parse_date_safe(df['Ngày lập'])
    df = df.dropna(subset=['_date'])
    mask = (df['_date'] >= start_date) & (df['_date'] <= end_date)
    df_f = df[mask]
    if df_f.empty:
        continue
    # Loại bỏ các đơn hủy/trả lại
    status = df_f['Ghi chú TT'].astype(str).str.lower()
    exclude = status.str.contains('hủy|trả lại|đã trả hàng|đã trả', na=False)
    df_f = df_f[~exclude]
    if df_f.empty:
        continue
    money = clean_money(df_f['Tiền'])
    total_revenue += money.sum()
    has_data = True

if not has_data:
    ans = None
    reason = "Không có dữ liệu"
else:
    ans = total_revenue
```
- **Lỗi lần 1**: Kết quả sai (201253.09999999998 != 730984600)
- **Code sửa**:
```python
# Lấy tất cả các bảng SoBanHang
sales_tables = [k for k in dfs.keys() if k.startswith('SoBanHang_')]

# Ngày chốt
end_date = pd.Timestamp('2025-02-19')
start_date = end_date - pd.Timedelta(days=30)

total_revenue = 0
has_data = False

for tbl in sales_tables:
    df = dfs[tbl].copy()
    if df.empty:
        continue
    df['_date'] = parse_date_safe(df['Ngày lập'])
    df = df.dropna(subset=['_date'])
    mask = (df['_date'] >= start_date) & (df['_date'] <= end_date)
    df_f = df[mask]
    if df_f.empty:
        continue
    # Loại bỏ các đơn hủy/trả lại
    status = df_f['Ghi chú TT'].astype(str).str.lower()
    exclude = status.str.contains('hủy|trả lại|đã trả hàng|đã trả', na=False)
    df_f = df_f[~exclude]
    if df_f.empty:
        continue
    money = clean_money(df_f['Tiền'])
    total_revenue += money.sum()
    has_data = True

if not has_data:
    ans = None
else:
    ans = total_revenue
```
- **Lỗi lần 2**: Kết quả sai (201253.09999999998 != 730984600)
- **Code sửa**:
```python
# Lấy tất cả các bảng SoBanHang
sales_tables = [k for k in dfs.keys() if k.startswith('SoBanHang_')]

# Ngày chốt
end_date = pd.Timestamp('2025-02-19')
start_date = end_date - pd.Timedelta(days=30)

total_revenue = 0
has_data = False

for tbl in sales_tables:
    df = dfs[tbl].copy()
    if df.empty:
        continue
    df['_date'] = parse_date_safe(df['Ngày lập'])
    df = df.dropna(subset=['_date'])
    mask = (df['_date'] >= start_date) & (df['_date'] <= end_date)
    df_f = df[mask]
    if df_f.empty:
        continue
    # Loại bỏ các đơn hủy/trả lại
    status = df_f['Ghi chú TT'].astype(str).str.lower()
    exclude = status.str.contains('hủy|trả lại|đã trả hàng|đã trả', na=False)
    df_f = df_f[~exclude]
    if df_f.empty:
        continue
    money = clean_money(df_f['Tiền'])
    total_revenue += money.sum()
    has_data = True

if not has_data:
    ans = None
else:
    ans = total_revenue
```
- **Lỗi lần 3**: Kết quả sai (201253.09999999998 != 730984600)
- **Code sửa**:
```python
# Lấy tất cả các bảng SoBanHang
sales_tables = [k for k in dfs.keys() if k.startswith('SoBanHang_')]

# Ngày chốt
end_date = pd.Timestamp('2025-02-19')
start_date = end_date - pd.Timedelta(days=30)

total_revenue = 0
has_data = False

for tbl in sales_tables:
    df = dfs[tbl].copy()
    if df.empty:
        continue
    df['_date'] = parse_date_safe(df['Ngày lập'])
    df = df.dropna(subset=['_date'])
    mask = (df['_date'] >= start_date) & (df['_date'] <= end_date)
    df_f = df[mask]
    if df_f.empty:
        continue
    # Loại bỏ các đơn hủy/trả lại
    status = df_f['Ghi chú TT'].astype(str).str.lower()
    exclude = status.str.contains('hủy|trả lại|đã trả hàng|đã trả', na=False)
    df_f = df_f[~exclude]
    if df_f.empty:
        continue
    money = clean_money(df_f['Tiền'])
    total_revenue += money.sum()
    has_data = True

if not has_data:
    ans = None
else:
    ans = total_revenue
```
- **Lưu**: ❌

## Câu 24: q_01bba93199de | Ngày: 2026-08-29
- **Hỏi**: Doanh thu tháng 4/2026 bao nhiêu?
- **Gold**: 1380833500 (Type: number)
