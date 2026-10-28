# BẮT ĐẦU QUÁ TRÌNH DẠY AI

- Thời gian: 2026-10-28 13:22:25
- Tổng số câu: 50

## Câu 1/50: q_001883280e83 | Biz: biz_128
- **Câu hỏi**: tháng này tổng giá trị các phiếu nhập hàng là bao nhiu
- **Đáp án đúng**: 89526400 (Type: number)
- **Kế hoạch (3B)**: - Cần bảng `DanhSachHoaDon_09.2025` và `DanhSachHoaDonChiTiet`.
- Lọc `Thời gian` từ `09.2025` và trạng thái `Đã thanh toán`.
- Tính tổng `Tổng tiền hàng`.
- **Code ban đầu (1.5B)**:
```python
import pandas as pd

# Đọc dữ liệu từ các bảng
dfs = {
    'BaoCaoTonKho': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='BaoCaoTonKho'),
    'DanhSachChiTietNhapHang': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachChiTietNhapHang'),
    'DanhSachHoaDon_04.2025': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_04.2025'),
    'DanhSachHoaDon_05.2025': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_05.2025'),
    'DanhSachHoaDon_06.2025': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_06.2025'),
    'DanhSachHoaDon_07.2025': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_07.2025'),
    'DanhSachHoaDon_08.2025': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_08.2025'),
    'DanhSachHoaDon_09.2025': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_09.2025'),
    'DanhSachHoaDon_10.2025': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_10.2025'),
    'DanhSachHoaDon_11.2025': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_11.2025'),
    'DanhSachHoaDon_12.2025': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_12.2025'),
    'DanhSachHoaDon_01.2026': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_01.2026'),
    'DanhSachHoaDon_02.2026': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_02.2026'),
    'DanhSachHoaDon_03.2026': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_03.2026'),
    'DanhSachHoaDon_04.2026': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_04.2026'),
    'DanhSachHoaDon_05.2026': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_05.2026'),
    'DanhSachHoaDon_06.2026': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_06.2026'),
    'DanhSachHoaDon_07.2026': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_07.2026'),
    'DanhSachHoaDon_08.2026': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_08.2026'),
    'DanhSachHoaDon_09.2026': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDon_09.2026'),
    'DanhSachHoaDonChiTiet': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDonChiTiet'),
    'DanhSachHoaDonPhongBan': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachHoaDonPhongBan'),
    'DanhSachKhachHang': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachKhachHang'),
    'DanhSachNhapHang': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachNhapHang'),
    'DanhSachSanPham': pd.read_excel('DanhSachHoaDon.xlsx', sheet_name='DanhSachSanPham')
}

# Lấy dữ liệu từ bảng BaoCaoTonKho
df = dfs['BaoCaoTonKho']

# Cột ngày dùng parse_date_safe(df['cột'])
df['Ngày'] = pd.to_datetime(df['Ngày'], errors='coerce')

# Cột tiền dùng clean_money(df['cột'])
df['Tiền'] = df['Tiền'].str.replace(',', '').astype(float)

# Kiểm tra nếu không tìm thấy dữ liệu
if df.empty:
    ans = None
else:
    # Tính tổng tiền bán hàng
    total_revenue = df['Tiền'].sum()
    ans = total_revenue
```
- **Lần thử 1**: Lỗi Runtime: Lỗi Runtime: [Errno 2] No such file or directory: 'DanhSachHoaDon.xlsx'
  - Feedback từ DeepSeek: [FAILED]

**Phân tích lỗi sai:**

1. **Sai nguồn dữ liệu hoàn toàn**: Câu hỏi hỏi về "phiếu nhập hàng" → phải dùng bảng `DanhSachNhapHang` (và có thể cả `DanhSachChiTietNhapHang`), nhưng học sinh lại ...
  - Code đã sửa:
```python
import pandas as pd
from datetime import datetime

# Lấy tháng/năm hiện tại
now = datetime.now()
thang = now.month
nam = now.year

# Bảng phiếu nhập hàng
df_nhap = dfs['DanhSachNhapHang'].copy()
df_ct = dfs['DanhSachChiTietNhapHang'].copy()

# Parse ngày
df_nhap['Thời gian'] = pd.to_datetime(df_nhap['Thời gian'], dayfirst=True, errors='coerce')

# Lọc phiếu nhập trong tháng hiện tại
mask = (df_nhap['Thời gian'].dt.month == thang) & (df_nhap['Thời gian'].dt.year == nam)
df_nhap_thang = df_nhap[mask]

# Tính giá trị từng phiếu = tổng (Số lượng * Đơn giá) từ chi tiết
df_ct['Số lượng'] = pd.to_numeric(df_ct['Số lượng'], errors='coerce').fillna(0)
df_ct['Đơn giá'] = pd.to_numeric(df_ct['Đơn giá'], errors='coerce').fillna(0)
df_ct['ThanhTien'] = df_ct['Số lượng'] * df_ct['Đơn giá']

gia_tri_theo_phieu = df_ct.groupby('Mã nhập hàng')['ThanhTien'].sum()

# Chỉ lấy các phiếu trong tháng hiện tại
ma_phieu_thang = set(df_nhap_thang['Mã nhập hàng'])
ans = float(gia_tri_theo_phieu[gia_tri_theo_phieu.index.isin(ma_phieu_thang)].sum())

print(ans)
```
- **Lần thử 2**: Kết quả = 0
  - Feedback từ DeepSeek: [FAILED]

Lỗi sai: Học sinh dùng `datetime.now()` để lấy tháng/năm hiện tại, nhưng dữ liệu trong hệ thống là dữ liệu lịch sử (các file từ 04.2025 đến 09.2026). "Tháng này" phải được hiểu là tháng có dữ liệu mới nhất trong bộ dữ liệu (tháng lớn nhất trong `DanhSachNhapHang`), không phải tháng hiện tạ...
  - Code đã sửa:
```python
import pandas as pd

df_nhap = dfs['DanhSachNhapHang'].copy()
df_ct = dfs['DanhSachChiTietNhapHang'].copy()

# Parse ngày
df_nhap['Thời gian'] = pd.to_datetime(df_nhap['Thời gian'], dayfirst=True, errors='coerce')
df_nhap = df_nhap.dropna(subset=['Thời gian'])

# Xác định "tháng này" = tháng mới nhất có dữ liệu nhập hàng
thang_max = df_nhap['Thời gian'].max()
thang = thang_max.month
nam = thang_max.year

# Lọc phiếu nhập trong tháng đó
mask = (df_nhap['Thời gian'].dt.month == thang) & (df_nhap['Thời gian'].dt.year == nam)
df_nhap_thang = df_nhap[mask]

# Tính giá trị từng phiếu từ chi tiết
df_ct['Số lượng'] = pd.to_numeric(df_ct['Số lượng'], errors='coerce').fillna(0)
df_ct['Đơn giá'] = pd.to_numeric(df_ct['Đơn giá'], errors='coerce').fillna(0)
df_ct['ThanhTien'] = df_ct['Số lượng'] * df_ct['Đơn giá']

gia_tri_theo_phieu = df_ct.groupby('Mã nhập hàng')['ThanhTien'].sum()

ma_phieu_thang = set(df_nhap_thang['Mã nhập hàng'])
ans = float(gia_tri_theo_phieu[gia_tri_theo_phieu.index.isin(ma_phieu_thang)].sum())

print(ans)
```
- **Lần thử 3**: Kết quả = 0
  - Feedback từ DeepSeek: Phân tích lỗi:

1. **Sai logic "tháng này"**: Code lấy tháng mới nhất có dữ liệu nhập hàng (`thang_max`). Nhưng dữ liệu `DanhSachNhapHang` có thể chỉ có vài tháng, trong khi "tháng này" theo ngữ cảnh câu hỏi (dựa trên dữ liệu hóa đơn) phải là tháng hiện tại của doanh nghiệp — tức tháng mới nhất tron...
  - Code đã sửa:
```python
import pandas as pd

df_nhap = dfs['DanhSachNhapHang'].copy()

# Parse ngày
df_nhap['Thời gian'] = pd.to_datetime(df_nhap['Thời gian'], dayfirst=True, errors='coerce')
df_nhap = df_nhap.dropna(subset=['Thời gian'])

# "Tháng này" = tháng mới nhất có dữ liệu trong DanhSachNhapHang
thang_max = df_nhap['Thời gian'].max()
thang = thang_max.month
nam = thang_max.year

# Lọc phiếu nhập trong tháng đó
mask = (df_nhap['Thời gian'].dt.month == thang) & (df_nhap['Thời gian'].dt.year == nam)
df_nhap_thang = df_nhap[mask].copy()

# Loại phiếu đã hủy nếu có (trạng thái chứa "hủy"/"Hủy")
if 'Trạng thái' in df_nhap_thang.columns:
    df_nhap_thang = df_nhap_thang[
        ~df_nhap_thang['Trạng thái'].astype(str).str.lower().str.contains('hủy|huỷ', na=False)
    ]

# Dùng trực tiếp cột "Cần trả NCC" làm giá trị phiếu nhập
df_nhap_thang['Cần trả NCC'] = pd.to_numeric(df_nhap_thang['Cần trả NCC'], errors='coerce').fillna(0)

ans = float(df_nhap_thang['Cần trả NCC'].sum())
print(ans)
```
- **Kết quả cuối**: ❌ THẤT BẠI

## Câu 2/50: q_00195e1e4049 | Biz: biz_124
- **Câu hỏi**: Thuốc có hoạt chất Natri clorid tháng này bán được tổng cộng bao nhiêu tiền?
- **Đáp án đúng**: 2954200 (Type: number)
- **Kế hoạch (3B)**: - Cần bảng `BanHang_ChiTietHoaDon`, `BanHang_HangHoa`, `BanHang_PhieuThu`.
- Lọc `Ngày bán` từ `2026-05-01` đến `2026-05-31`, `Thuốc` `Kê đơn` = 1.
- Tính `sum` `Thanh tien` (Số tiền thu).
- **Code ban đầu (1.5B)**:
```python
import pandas as pd

# Đọc dữ liệu từ các bảng
df_BanHang_ChiTietHoaDon = dfs['BanHang_ChiTietHoaDon']
df_BanHang_HangHoa = dfs['BanHang_HangHoa']
df_BanHang_PhieuThu = dfs['BanHang_PhieuThu']
df_BanHang_HoaDon = dfs['BanHang_HoaDon']
df_BanHang_KhachHang = dfs['BanHang_KhachHang']
df_BanHang_LichSuGia = dfs['BanHang_LichSuGia']
df_BanHang_LoHang = dfs['BanHang_LoHang']
df_BanHang_PhieuThu = dfs['BanHang_PhieuThu']
df_BanHang_Thuoc = dfs['BanHang_Thuoc']
df_SoTay_ChiPhi = dfs['SoTay_ChiPhi']
df_SoTay_NhapHang = dfs['SoTay_NhapHang']
df_ton_kho = dfs['ton_kho']

# Lọc dữ liệu từ 2026-05-01 đến 2026-05-31
df_BanHang_ChiTietHoaDon = df_BanHang_ChiTietHoaDon[(df_BanHang_ChiTietHoaDon['Ngày bán'] >= '2026-05-01') & (df_BanHang_ChiTietHoaDon['Ngày bán'] <= '2026-05-31')]

# Tính tổng thu
total_revenue = df_BanHang_ChiTietHoaDon['Thanh tien'].sum()

# Gán kết quả vào ans
ans = total_revenue
reason = "Lý do cụ thể: Thuốc có hoạt chất Natri clorid tháng này bán được tổng cộng bao nhiêu tiền?"
```
- **Lần thử 1**: Lỗi Runtime: Lỗi Runtime: 'Ngày bán'
  - Feedback từ DeepSeek: [FAILED]

Lỗi sai:
1. `BanHang_ChiTietHoaDon` không có cột `Ngày bán` — cột ngày nằm ở `BanHang_HoaDon`. Cần merge để lấy ngày.
2. Chưa lọc theo hoạt chất `Natri clorid` (bảng `BanHang_Thuoc`).
3. Chư...
  - Code đã sửa:
```python
import pandas as pd

df_ct = dfs['BanHang_ChiTietHoaDon'].copy()
df_hd = dfs['BanHang_HoaDon'].copy()
df_thuoc = dfs['BanHang_Thuoc'].copy()

# Chuẩn hóa ngày
df_hd['Ngày bán'] = pd.to_datetime(df_hd['Ngày bán'], errors='coerce')

# Lọc hóa đơn tháng 5/2026
mask_thang5 = (df_hd['Ngày bán'] >= '2026-05-01') & (df_hd['Ngày bán'] <= '2026-05-31')
df_hd_t5 = df_hd.loc[mask_thang5, ['Mã giao dịch', 'Ngày bán']]

# Lọc thuốc có hoạt chất Natri clorid
mask_thuoc = df_thuoc['Hoạt chất'].astype(str).str.contains('Natri clorid', case=False, na=False)
ma_thuoc_nc = df_thuoc.loc[mask_thuoc, 'Mã HH'].unique()

# Nối chi tiết với hóa đơn tháng 5
df_merge = df_ct.merge(df_hd_t5, on='Mã giao dịch', how='inner')

# Lọc các dòng thuốc Natri clorid
df_filter = df_merge[df_merge['Ma hang'].isin(ma_thuoc_nc)]

ans = df_filter['Thanh tien'].sum()
reason = "Tổng tiền bán thuốc có hoạt chất Natri clorid trong tháng 5/2026."
```
- **Lần thử 2**: Lỗi Runtime: Lỗi Runtime: "['Mã giao dịch'] not in index"
  - Feedback từ DeepSeek: Lỗi sai: Cột khóa nối giữa `BanHang_ChiTietHoaDon` và `BanHang_HoaDon` không phải `'Mã giao dịch'`. Theo cấu trúc dữ liệu, `BanHang_HoaDon` có cột `'Order ID'` (mã hóa đơn), còn `BanHang_ChiTietHoaDon...
  - Code đã sửa:
```python
import pandas as pd

df_ct = dfs['BanHang_ChiTietHoaDon'].copy()
df_hd = dfs['BanHang_HoaDon'].copy()
df_thuoc = dfs['BanHang_Thuoc'].copy()

# Chuẩn hóa ngày
df_hd['Ngày bán'] = pd.to_datetime(df_hd['Ngày bán'], errors='coerce')

# Lọc hóa đơn tháng 5/2026 (loại đơn hủy nếu có)
mask_thang5 = (df_hd['Ngày bán'] >= '2026-05-01') & (df_hd['Ngày bán'] <= '2026-05-31')
if 'Trạng thái' in df_hd.columns:
    mask_thang5 &= ~df_hd['Trạng thái'].astype(str).str.contains('hủy|Hủy|HỦY', na=False)

df_hd_t5 = df_hd.loc[mask_thang5, ['Order ID', 'Ngày bán']]

# Lọc thuốc có hoạt chất Natri clorid
mask_thuoc = df_thuoc['Hoạt chất'].astype(str).str.contains('Natri clorid', case=False, na=False)
ma_thuoc_nc = df_thuoc.loc[mask_thuoc, 'Mã HH'].unique()

# Nối chi tiết với hóa đơn tháng 5: 'Mã giao dịch' (chi tiết) <-> 'Order ID' (hóa đơn)
df_merge = df_ct.merge(df_hd_t5, left_on='Mã giao dịch', right_on='Order ID', how='inner')

# Lọc các dòng thuốc Natri clorid
df_filter = df_merge[df_merge['Ma hang'].isin(ma_thuoc_nc)]

ans = df_filter['Thanh tien'].sum()
reason = "Tổng tiền bán thuốc có hoạt chất Natri clorid trong tháng 5/2026."
```
- **Lần thử 3**: Kết quả = 28,00010,0005,6001,4001,40028,00030,0001,40030,0001,40010,00030,00040,00028,00010,0005,6004,2002,8001,4002,8002,80020,0005,60010,0002,80028,00020,0002,80010,00010,00028,0002,80020,00010,00040,0002,8001,40010,00020,00028,0004,20010,0001,40040,00056,0001,40020,00010,00028,000
  - Feedback từ DeepSeek: [FAILED]

Lỗi sai:
1. **Sai cột doanh thu**: Cột `Thanh tien` trong `BanHang_ChiTietHoaDon` không phải là số tiền bán thực tế của dòng. Cần dùng `TT dòng` (thành tiền dòng sau giảm giá/khuyến mãi) — hoặc theo README, `Tong tien` ở hóa đơn là tổng phải trả, còn chi tiết dòng dùng `TT dòng`.
2. **Khôn...
  - Code đã sửa:
```python
import pandas as pd
import re

df_ct = dfs['BanHang_ChiTietHoaDon'].copy()
df_hd = dfs['BanHang_HoaDon'].copy()
df_thuoc = dfs['BanHang_Thuoc'].copy()

# Chuẩn hóa ngày
df_hd['Ngày bán'] = pd.to_datetime(df_hd['Ngày bán'], errors='coerce')

# Lọc hóa đơn tháng 5/2026, loại đơn hủy
mask_thang5 = (df_hd['Ngày bán'] >= '2026-05-01') & (df_hd['Ngày bán'] <= '2026-05-31')
if 'Trạng thái' in df_hd.columns:
    mask_thang5 &= ~df_hd['Trạng thái'].astype(str).str.contains('hủy', case=False, na=False)

df_hd_t5 = df_hd.loc[mask_thang5, ['Order ID', 'Ngày bán']]

# Lọc thuốc có hoạt chất Natri clorid (tách theo " + " để so khớp chính xác từng hoạt chất)
def co_natri_clorid(s):
    if pd.isna(s):
        return False
    parts = [p.strip().lower() for p in str(s).split('+')]
    return any(p == 'natri clorid' for p in parts)

mask_thuoc = df_thuoc['Hoạt chất'].apply(co_natri_clorid)
ma_thuoc_nc = df_thuoc.loc[mask_thuoc, 'Mã HH'].unique()

# Nối chi tiết với hóa đơn tháng 5
df_merge = df_ct.merge(df_hd_t5, left_on='Mã giao dịch', right_on='Order ID', how='inner')

# Lọc các dòng thuốc Natri clorid
df_filter = df_merge[df_merge['Ma hang'].isin(ma_thuoc_nc)].copy()

# Dùng cột tiền đúng và ép kiểu số
df_filter['TT dòng'] = pd.to_numeric(df_filter['TT dòng'], errors='coerce')

ans = df_filter['TT dòng'].sum()
reason = "Tổng tiền bán thuốc có hoạt chất Natri clorid trong tháng 5/2026 (dùng cột TT dòng)."
```
- **Kết quả cuối**: ❌ THẤT BẠI

## Câu 3/50: q_002d03ebbded | Biz: biz_120
- **Câu hỏi**: Tổng doanh thu trong ngày hôm nay là bao nhiêu?
- **Đáp án đúng**: 10309400 (Type: number)
