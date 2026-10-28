# BẮT ĐẦU QUÁ TRÌNH DẠY AI

- Thời gian: 2026-10-28 14:29:22
- Tổng số câu: 50

## Câu 1/50: q_001883280e83 | Biz: biz_128
- **Câu hỏi**: tháng này tổng giá trị các phiếu nhập hàng là bao nhiu
- **Đáp án đúng**: 89526400 (Type: number)
- **Kế hoạch (3B)**: Lấy thông tin khách hàng, nhập hàng, sản phẩm và lịch sự kiện, lọc theo tháng 4.
- **Code ban đầu (DeepSeek)**:
```python
import pandas as pd

# Lấy dữ liệu
nhap_hang = dfs['DanhSachNhapHang'].copy()

# Xử lý ngày tháng
nhap_hang['Thời gian'] = parse_date_safe(nhap_hang['Thời gian'])

# Xử lý tiền
nhap_hang['Cần trả NCC'] = clean_money(nhap_hang['Cần trả NCC'])

# Xác định "tháng này" = tháng của ngày cuối dữ liệu (07/09/2026) -> tháng 9/2026
# Lọc theo tháng 9 năm 2026
mask = (nhap_hang['Thời gian'].dt.month == 9) & (nhap_hang['Thời gian'].dt.year == 2026)
nhap_thang_nay = nhap_hang[mask]

# Tổng giá trị các phiếu nhập hàng
ans = nhap_thang_nay['Cần trả NCC'].sum()

print(f"Tổng giá trị các phiếu nhập hàng tháng 9/2026: {ans:,.0f} VNĐ")
ans
```
- **Lần thử 1**: Kết quả = 89526400
- **Trạng thái**: ĐÚNG
- **Kết quả cuối**: ✅ ĐÃ LƯU VÀO BỘ NHỚ

## Câu 2/50: q_00195e1e4049 | Biz: biz_124
- **Câu hỏi**: Thuốc có hoạt chất Natri clorid tháng này bán được tổng cộng bao nhiêu tiền?
- **Đáp án đúng**: 2954200 (Type: number)
- **Kế hoạch (3B)**: Lấy bảng ton_kho, lọc hàng hóa 'Panadol Extra', tính tổng ton kho.
- **Code ban đầu (DeepSeek)**:
```python
import pandas as pd
import numpy as np

# Lấy dữ liệu
thuoc = dfs['BanHang_Thuoc'].copy()
hanghoa = dfs['BanHang_HangHoa'].copy()
cthd = dfs['BanHang_ChiTietHoaDon'].copy()
hoadon = dfs['BanHang_HoaDon'].copy()

# Lọc thuốc có hoạt chất Natri clorid
thuoc_nacl = thuoc[thuoc['Hoạt chất'].fillna('').str.contains('Natri clorid', case=False, na=False)]
ma_hh_nacl = set(thuoc_nacl['Mã HH'].astype(str))

# Lấy tháng cuối cùng có dữ liệu
hoadon['Ngay'] = parse_date_safe(hoadon['Ngày bán'])
max_date = hoadon['Ngay'].max()
thang_cuoi = max_date.month
nam_cuoi = max_date.year

# Lọc hóa đơn tháng cuối
hd_thang = hoadon[(hoadon['Ngay'].dt.month == thang_cuoi) & (hoadon['Ngay'].dt.year == nam_cuoi)]
ma_hd_thang = set(hd_thang['Order ID'].astype(str))

# Lọc chi tiết hóa đơn thuộc tháng cuối và có mã hàng Natri clorid
cthd['Thanh tien_num'] = clean_money(cthd['Thanh tien'])
cthd_nacl = cthd[
    (cthd['Mã giao dịch'].astype(str).isin(ma_hd_thang)) &
    (cthd['Ma hang'].astype(str).isin(ma_hh_nacl))
]

ans = cthd_nacl['Thanh tien_num'].sum()
print(f"Tháng {thang_cuoi}/{nam_cuoi}: Tổng tiền bán thuốc có hoạt chất Natri clorid = {ans:,.0f} VNĐ")
```
- **Lần thử 1**: Kết quả = 253800
  - Feedback từ DeepSeek: ## Kiểm tra code

**Vấn đề phát hiện:**

1. **Sai logic xác định "tháng này"**: Code lấy tháng cuối cùng có dữ liệu trong bảng `BanHang_HoaDon`. Nhưng câu hỏi "tháng này" cần xác định theo ngày hiện tại (hoặc tháng có dữ liệu thực tế phù hợp). Cần kiểm tra lại — nếu dữ liệu trải dài nhiều tháng, "th...
  - Code đã sửa:
```python
import pandas as pd
import numpy as np

thuoc = dfs['BanHang_Thuoc'].copy()
cthd = dfs['BanHang_ChiTietHoaDon'].copy()
hoadon = dfs['BanHang_HoaDon'].copy()

# Lọc thuốc có hoạt chất Natri clorid (linh hoạt hơn)
thuoc_nacl = thuoc[
    thuoc['Hoạt chất'].fillna('').str.contains('natri clorid', case=False, na=False)
]
ma_hh_nacl = set(thuoc_nacl['Mã HH'].astype(str))

# Xác định "tháng này" = tháng của ngày bán lớn nhất
hoadon['Ngay'] = parse_date_safe(hoadon['Ngày bán'])
max_date = hoadon['Ngay'].max()
thang_cuoi = max_date.month
nam_cuoi = max_date.year

# Lọc hóa đơn tháng này, LOẠI các đơn Đổi trả / Hủy
hd_thang = hoadon[
    (hoadon['Ngay'].dt.month == thang_cuoi) &
    (hoadon['Ngay'].dt.year == nam_cuoi) &
    (~hoadon['Trạng thái'].fillna('').str.contains('Đổi trả|Hủy', case=False, na=False))
]
ma_hd_thang = set(hd_thang['Order ID'].astype(str))

# Tính tiền
cthd['Thanh tien_num'] = clean_money(cthd['Thanh tien'])
cthd_nacl = cthd[
    (cthd['Mã giao dịch'].astype(str).isin(ma_hd_thang)) &
    (cthd['Ma hang'].astype(str).isin(ma_hh_nacl))
]

ans = cthd_nacl['Thanh tien_num'].sum()
print(f"Tháng {thang_cuoi}/{nam_cuoi}: Tổng tiền = {ans:,.0f} VNĐ")
```
- **Lần thử 2**: Kết quả = 251000
  - Feedback từ DeepSeek: ## Kiểm tra code

**Vấn đề phát hiện:**

1. **Sai logic "tháng này"**: Code lấy tháng của ngày bán **lớn nhất** trong toàn bộ dữ liệu hóa đơn. Nhưng câu hỏi "tháng này" nên hiểu là tháng hiện tại của dữ liệu (tháng có nhiều giao dịch / tháng gần nhất có phát sinh bán hàng thực tế). Cách này có thể c...
  - Code đã sửa:
```python
import pandas as pd
import numpy as np

thuoc = dfs['BanHang_Thuoc'].copy()
cthd = dfs['BanHang_ChiTietHoaDon'].copy()
hoadon = dfs['BanHang_HoaDon'].copy()

# Lọc thuốc có hoạt chất Natri clorid
thuoc_nacl = thuoc[
    thuoc['Hoạt chất'].fillna('').str.contains('natri clorid', case=False, na=False)
]
ma_hh_nacl = set(thuoc_nacl['Mã HH'].astype(str))

# Xác định "tháng này" = tháng của ngày bán lớn nhất
hoadon['Ngay'] = parse_date_safe(hoadon['Ngày bán'])
max_date = hoadon['Ngay'].max()
thang_cuoi = max_date.month
nam_cuoi = max_date.year

# Lọc hóa đơn tháng này — CHỈ loại đơn Hủy (giữ lại Đổi trả vì vẫn có doanh thu)
hd_thang = hoadon[
    (hoadon['Ngay'].dt.month == thang_cuoi) &
    (hoadon['Ngay'].dt.year == nam_cuoi) &
    (~hoadon['Trạng thái'].fillna('').str.contains('Hủy', case=False, na=False))
]
ma_hd_thang = set(hd_thang['Order ID'].astype(str))

# Tính tiền
cthd['Thanh tien_num'] = clean_money(cthd['Thanh tien'])
cthd_nacl = cthd[
    (cthd['Mã giao dịch'].astype(str).isin(ma_hd_thang)) &
    (cthd['Ma hang'].astype(str).isin(ma_hh_nacl))
]

ans = cthd_nacl['Thanh tien_num'].sum()
print(f"Tháng {thang_cuoi}/{nam_cuoi}: Tổng tiền = {ans:,.0f} VNĐ")
```
- **Lần thử 3**: Kết quả = 253800
  - Feedback từ DeepSeek: ## Kiểm tra code

**Kết quả code: 253800** — **Đáp án đúng: 2954200** → **SAI**

### Phân tích lỗi

Code có 2 vấn đề chính:

**1. Lọc hoạt chất quá hẹp (thiếu dấu/khác cách viết)**
- `str.contains('natri clorid')` chỉ khớp chính xác chuỗi "natri clorid". Nếu dữ liệu ghi "Natri Clorid", "Natri clorua...
  - Code đã sửa:
```python
import pandas as pd
import numpy as np
import re

thuoc = dfs['BanHang_Thuoc'].copy()
cthd = dfs['BanHang_ChiTietHoaDon'].copy()
hoadon = dfs['BanHang_HoaDon'].copy()

# 1) Lọc hoạt chất Natri clorid — chấp nhận nhiều biến thể viết
pattern = r'natri\s*clorid|natri\s*clorua|sodium\s*chlorid|nacl'
thuoc_nacl = thuoc[
    thuoc['Hoạt chất'].fillna('').str.lower().str.contains(pattern, regex=True, na=False)
]
ma_hh_nacl = set(thuoc_nacl['Mã HH'].astype(str))
print("Sản phẩm Natri clorid:", ma_hh_nacl)

# 2) Xác định "tháng này" = tháng hiện tại của hệ thống
hoadon['Ngay'] = parse_date_safe(hoadon['Ngày bán'])
today = pd.Timestamp.today()
thang_cuoi = today.month
nam_cuoi = today.year

# Nếu dữ liệu không có giao dịch trong tháng hiện tại, fallback về tháng có nhiều đơn nhất
hd_tmp = hoadon.dropna(subset=['Ngay'])
if not ((hd_tmp['Ngay'].dt.month == thang_cuoi) & (hd_tmp['Ngay'].dt.year == nam_cuoi)).any():
    counts = hd_tmp.groupby([hd_tmp['Ngay'].dt.year, hd_tmp['Ngay'].dt.month]).size()
    nam_cuoi, thang_cuoi = counts.idxmax()

# 3) Lọc hóa đơn tháng này — loại đơn Hủy
hd_thang = hoadon[
    (hoadon['Ngay'].dt.month == thang_cuoi) &
    (hoadon['Ngay'].dt.year == nam_cuoi) &
    (~hoadon['Trạng thái'].fillna('').str.contains('Hủy', case=False, na=False))
]
ma_hd_thang = set(hd_thang['Order ID'].astype(str))

# 4) Tính tiền
cthd['Thanh tien_num'] = clean_money(cthd['Thanh tien'])
cthd_nacl = cthd[
    (cthd['Mã giao dịch'].astype(str).isin(ma_hd_thang)) &
    (cthd['Ma hang'].astype(str).isin(ma_hh_nacl))
]

ans = cthd_nacl['Thanh tien_num'].sum()
print(f"Tháng {thang_cuoi}/{nam_cuoi}: Tổng tiền = {ans:,.0f} VNĐ")
```
- **Kết quả cuối**: ❌ THẤT BẠI

## Câu 3/50: q_002d03ebbded | Biz: biz_120
- **Câu hỏi**: Tổng doanh thu trong ngày hôm nay là bao nhiêu?
- **Đáp án đúng**: 10309400 (Type: number)
- **Kế hoạch (3B)**: Lấy bảng DanhSachLoHang, lọc các lô hết hạn trước 2026-06-30, tính tổng số lượng.
- **Code ban đầu (DeepSeek)**:
```python
import pandas as pd
import numpy as np

# Xác định ngày hôm nay = ngày cuối cùng có dữ liệu
# Dữ liệu có đến hết 12/06/2026
today = pd.Timestamp('2026-06-12')

# Lấy bảng hóa đơn tháng 06/2026
df_hd = dfs['DanhSachHoaDon_06.2026'].copy()

# Parse ngày tháng
df_hd['Thời gian'] = parse_date_safe(df_hd['Thời gian'])

# Lọc hóa đơn trong ngày hôm nay
df_today = df_hd[df_hd['Thời gian'].dt.normalize() == today].copy()

# Loại bỏ đơn hủy (trạng thái chứa "hủy"/"huỷ")
status_lower = df_today['Trạng thái'].astype(str).str.lower()
mask_cancel = status_lower.str.contains('hủy|huỷ', na=False)
df_valid = df_today[~mask_cancel].copy()

# Tính doanh thu = Tổng tiền hàng - Giảm giá
df_valid['Tổng tiền hàng'] = clean_money(df_valid['Tổng tiền hàng'])
df_valid['Giảm giá'] = clean_money(df_valid['Giảm giá'])

doanh_thu = (df_valid['Tổng tiền hàng'] - df_valid['Giảm giá']).sum()

ans = doanh_thu
print(f"Ngày: {today.date()}")
print(f"Số hóa đơn hợp lệ: {len(df_valid)}")
print(f"Tổng doanh thu trong ngày: {ans:,.0f} VNĐ")
```
- **Lần thử 1**: Kết quả = 8115700
  - Feedback từ DeepSeek: ## Phân tích lỗi

Code hiện tại có **2 vấn đề chính**:

### 1. Xác định "hôm nay" sai
Code hardcode `today = pd.Timestamp('2026-06-12')` với giả định "ngày cuối cùng có dữ liệu". Nhưng dữ liệu mẫu cho thấy các bảng hóa đơn chỉ có ngày **01** của mỗi tháng (mẫu 3 dòng đầu). Cần kiểm tra ngày thực tế ...
  - Code đã sửa:
```python
import pandas as pd
import numpy as np

# Gom tất cả bảng hóa đơn lại
hd_tables = [k for k in dfs.keys() if k.startswith('DanhSachHoaDon_') and k != 'DanhSachHoaDonChiTiet' and k != 'DanhSachHoaDonChiTietLo']
df_all = pd.concat([dfs[k] for k in hd_tables], ignore_index=True)

# Parse ngày
df_all['Thời gian'] = parse_date_safe(df_all['Thời gian'])
df_all = df_all.dropna(subset=['Thời gian'])

# Xác định "hôm nay" = ngày lớn nhất có hóa đơn
today = df_all['Thời gian'].dt.normalize().max()

# Lọc hóa đơn trong ngày hôm nay
df_today = df_all[df_all['Thời gian'].dt.normalize() == today].copy()

# Loại bỏ đơn hủy
status_lower = df_today['Trạng thái'].astype(str).str.lower()
mask_cancel = status_lower.str.contains('hủy|huỷ', na=False)
df_valid = df_today[~mask_cancel].copy()

# Tính doanh thu = Tổng tiền hàng - Giảm giá
df_valid['Tổng tiền hàng'] = clean_money(df_valid['Tổng tiền hàng'])
df_valid['Giảm giá'] = clean_money(df_valid['Giảm giá'])

doanh_thu = (df_valid['Tổng tiền hàng'] - df_valid['Giảm giá']).sum()

ans = doanh_thu
print(f"Ngày: {today.date()}")
print(f"Số hóa đơn hợp lệ: {len(df_valid)}")
print(f"Tổng doanh thu trong ngày: {ans:,.0f} VNĐ")
```
- **Lần thử 2**: Kết quả = 8115700
  - Feedback từ DeepSeek: ## Phân tích lỗi

Code chọn `today = df_all['Thời gian'].dt.normalize().max()` — tức là ngày **lớn nhất có hóa đơn** trong toàn bộ dữ liệu. Nhưng dữ liệu trải dài đến tháng 06/2026, nên "hôm nay" theo code sẽ là **01/06/2026**, không phải ngày thực tế cần tính.

Kiểm tra ngày 01/06/2026 (bảng `DanhS...
  - Code đã sửa:
```python
import pandas as pd
import numpy as np

# Gom tất cả bảng hóa đơn lại
hd_tables = [k for k in dfs.keys() 
             if k.startswith('DanhSachHoaDon_') 
             and k not in ('DanhSachHoaDonChiTiet', 'DanhSachHoaDonChiTietLo')]
df_all = pd.concat([dfs[k] for k in hd_tables], ignore_index=True)

# Parse ngày
df_all['Thời gian'] = parse_date_safe(df_all['Thời gian'])
df_all = df_all.dropna(subset=['Thời gian'])

# "Hôm nay" = ngày hiện tại của hệ thống (không phải max của dữ liệu)
today = pd.Timestamp.now().normalize()

# Nếu không có hóa đơn hôm nay trong dữ liệu, fallback về ngày gần nhất <= hôm nay
df_today = df_all[df_all['Thời gian'].dt.normalize() == today].copy()
if df_today.empty:
    # Lấy ngày có doanh thu (dùng ngày đầu tiên có dữ liệu làm mốc tham chiếu)
    today = df_all['Thời gian'].dt.normalize().min()
    df_today = df_all[df_all['Thời gian'].dt.normalize() == today].copy()

# Loại bỏ đơn hủy
status_lower = df_today['Trạng thái'].astype(str).str.lower()
mask_cancel = status_lower.str.contains('hủy|huỷ', na=False)
df_valid = df_today[~mask_cancel].copy()

# Tính doanh thu = Tổng tiền hàng - Giảm giá
df_valid['Tổng tiền hàng'] = clean_money(df_valid['Tổng tiền hàng'])
df_valid['Giảm giá'] = clean_money(df_valid['Giảm giá'])

doanh_thu = (df_valid['Tổng tiền hàng'] - df_valid['Giảm giá']).sum()

ans = doanh_thu
print(f"Ngày: {today.date()}")
print(f"Số hóa đơn hợp lệ: {len(df_valid)}")
print(f"Tổng doanh thu trong ngày: {ans:,.0f} VNĐ")
```
- **Lần thử 3**: Kết quả = 7030100
  - Feedback từ DeepSeek: ## Phân tích lỗi

**Vấn đề chính:** Code dùng `pd.Timestamp.now()` (ngày hiện tại của hệ thống) để xác định "hôm nay". Nhưng dữ liệu thực tế chỉ có từ 01/01/2025 đến 01/06/2026 — không có ngày nào trùng với "hôm nay" thực tế. Do đó code rơi vào nhánh fallback và lấy **ngày nhỏ nhất** trong dữ liệu (...
  - Code đã sửa:
```python
import pandas as pd
import numpy as np

# Gom tất cả bảng hóa đơn lại
hd_tables = [k for k in dfs.keys() 
             if k.startswith('DanhSachHoaDon_') 
             and k not in ('DanhSachHoaDonChiTiet', 'DanhSachHoaDonChiTietLo')]
df_all = pd.concat([dfs[k] for k in hd_tables], ignore_index=True)

# Parse ngày
df_all['Thời gian'] = parse_date_safe(df_all['Thời gian'])
df_all = df_all.dropna(subset=['Thời gian'])

# "Hôm nay" = ngày hiện tại của hệ thống
today = pd.Timestamp.now().normalize()

df_today = df_all[df_all['Thời gian'].dt.normalize() == today].copy()

# Nếu không có hóa đơn hôm nay trong dữ liệu -> lấy NGÀY GẦN NHẤT (max), không phải min
if df_today.empty:
    today = df_all['Thời gian'].dt.normalize().max()
    df_today = df_all[df_all['Thời gian'].dt.normalize() == today].copy()

# Loại bỏ đơn hủy
status_lower = df_today['Trạng thái'].astype(str).str.lower()
mask_cancel = status_lower.str.contains('hủy|huỷ', na=False)
df_valid = df_today[~mask_cancel].copy()

# Tính doanh thu = Tổng tiền hàng - Giảm giá
df_valid['Tổng tiền hàng'] = clean_money(df_valid['Tổng tiền hàng'])
df_valid['Giảm giá'] = clean_money(df_valid['Giảm giá'])

doanh_thu = (df_valid['Tổng tiền hàng'] - df_valid['Giảm giá']).sum()

ans = doanh_thu
print(f"Ngày: {today.date()}")
print(f"Số hóa đơn hợp lệ: {len(df_valid)}")
print(f"Tổng doanh thu trong ngày: {ans:,.0f} VNĐ")
```
- **Kết quả cuối**: ❌ THẤT BẠI

## Câu 4/50: q_00558c1410ef | Biz: biz_105
- **Câu hỏi**: tỉ lệ huỷ đơn tháng 6/2025 là nhiêu %
- **Đáp án đúng**: 2.08 (Type: percent)
- **Kế hoạch (3B)**: Lấy bảng SoBanHang_2026_Thang 04 2026, lọc hàng hóa cà phê sữa (M) và (L), tính tổng trị giá.
- **Code ban đầu (DeepSeek)**:
```python
import pandas as pd
import numpy as np

# Lấy dữ liệu tháng 6/2025
df = dfs['SoBanHang_1_Thang 06 2025'].copy()

# Chuẩn hóa ngày giao dịch
df['Ngày giao dịch'] = parse_date_safe(df['Ngày giao dịch'])

# Lọc tháng 6/2025
df = df[(df['Ngày giao dịch'] >= '2025-06-01') & (df['Ngày giao dịch'] <= '2025-06-30')]

# Xác định đơn bị huỷ/trả: đơn có dòng số lượng âm (trả hàng)
# Nhóm theo mã hoá đơn
order_has_return = df.groupby('Mã hóa đơn')['so_luong'].apply(lambda x: (x < 0).any())
cancelled_orders = set(order_has_return[order_has_return].index)

# Tổng số đơn trong tháng
total_orders = df['Mã hóa đơn'].nunique()

# Số đơn huỷ
num_cancelled = len(cancelled_orders)

# Tỉ lệ huỷ
ty_le_huy = num_cancelled / total_orders * 100 if total_orders > 0 else 0

ans = round(ty_le_huy, 2)
print(f"Tổng đơn: {total_orders}, Đơn huỷ: {num_cancelled}, Tỉ lệ huỷ: {ans}%")
```
- **Lần thử 1**: Kết quả = 32.0
  - Feedback từ DeepSeek: ## Kiểm tra

**Kết quả code: 32.0%** — Sai so với đáp án đúng **2.08%**.

### Nguyên nhân sai

Code xác định "đơn huỷ" bằng cách kiểm tra đơn có dòng `so_luong < 0` (trả hàng). Nhưng cách này **đếm sai mẫu số và tử số**:

1. **Tử số sai**: Một đơn bị trả hàng thường có **cả dòng dương (mua) và dòng ...
  - Code đã sửa:
```python
import pandas as pd
import numpy as np

df = dfs['SoBanHang_1_Thang 06 2025'].copy()

# Chuẩn hóa ngày
df['Ngày giao dịch'] = parse_date_safe(df['Ngày giao dịch'])
df = df[(df['Ngày giao dịch'] >= '2025-06-01') & (df['Ngày giao dịch'] <= '2025-06-30')]

# Xác định các dòng huỷ/trả theo Status
cancel_status = ['Đổi trả', 'Trả hàng', 'hàng trả về', 'Hủy', 'Huỷ', 'Đã hủy', 'Đã huỷ']
mask_cancel = df['Status'].astype(str).str.strip().isin(cancel_status) | (df['so_luong'] < 0)

# Tổng số dòng bán (loại các dòng huỷ/trả khỏi mẫu số)
total_lines = (~mask_cancel).sum()

# Số dòng huỷ/trả
cancel_lines = mask_cancel.sum()

ty_le_huy = cancel_lines / total_lines * 100 if total_lines > 0 else 0

ans = round(ty_le_huy, 2)
print(f"Tổng dòng bán: {total_lines}, Dòng huỷ/trả: {cancel_lines}, Tỉ lệ huỷ: {ans}%")
```
- **Lần thử 2**: Kết quả = 69.0
  - Feedback từ DeepSeek: **Kiểm tra:**

Code tính tỉ lệ huỷ = số dòng huỷ / số dòng bán (không huỷ) × 100 = 69.0%. Đáp án đúng là 2.08%.

**Vấn đề:** Tỉ lệ huỷ đơn phải được tính theo **số đơn (hóa đơn)**, không phải theo **số dòng sản phẩm**. Một hóa đơn có thể có nhiều dòng hàng; nếu tính theo dòng sẽ phóng đại tỉ lệ huỷ ...
  - Code đã sửa:
```python
import pandas as pd
import numpy as np

df = dfs['SoBanHang_1_Thang 06 2025'].copy()

# Chuẩn hóa ngày
df['Ngày giao dịch'] = parse_date_safe(df['Ngày giao dịch'])
df = df[(df['Ngày giao dịch'] >= '2025-06-01') & (df['Ngày giao dịch'] <= '2025-06-30')]

# Xác định các dòng huỷ/trả theo Status
cancel_status = ['Đổi trả', 'Trả hàng', 'hàng trả về', 'Hủy', 'Huỷ', 'Đã hủy', 'Đã huỷ']
mask_cancel = df['Status'].astype(str).str.strip().isin(cancel_status) | (df['so_luong'] < 0)

# Tính theo Mã hóa đơn (đơn hàng), không theo dòng sản phẩm
total_orders = df['Mã hóa đơn'].nunique()
cancel_orders = df.loc[mask_cancel, 'Mã hóa đơn'].nunique()

ty_le_huy = cancel_orders / total_orders * 100 if total_orders > 0 else 0

ans = round(ty_le_huy, 2)
print(f"Tổng đơn: {total_orders}, Đơn huỷ/trả: {cancel_orders}, Tỉ lệ huỷ: {ans}%")
```
- **Lần thử 3**: Kết quả = 63.0
  - Feedback từ DeepSeek: ## Phân tích lỗi

Code hiện tại tính **tỉ lệ đơn huỷ/trả trên tổng số đơn hàng** (đếm theo `Mã hóa đơn` unique), ra 63.0%.

Nhưng đáp án đúng là **2.08%** — đây là tỉ lệ **số lượng sản phẩm bị huỷ/trả trên tổng số lượng sản phẩm bán ra** (tính theo `so_luong`), không phải theo số đơn.

Kiểm tra nhan...
  - Code đã sửa:
```python
import pandas as pd
import numpy as np

df = dfs['SoBanHang_1_Thang 06 2025'].copy()

# Chuẩn hóa ngày
df['Ngày giao dịch'] = parse_date_safe(df['Ngày giao dịch'])
df = df[(df['Ngày giao dịch'] >= pd.Timestamp('2025-06-01')) & 
        (df['Ngày giao dịch'] <= pd.Timestamp('2025-06-30'))]

# Xác định các dòng huỷ/trả theo Status hoặc so_luong âm
cancel_status = ['Đổi trả', 'Trả hàng', 'hàng trả về', 'Hủy', 'Huỷ', 'Đã hủy', 'Đã huỷ']
mask_cancel = df['Status'].astype(str).str.strip().isin(cancel_status) | (df['so_luong'] < 0)

# Tính theo SỐ LƯỢNG sản phẩm (không theo đơn)
total_qty = df.loc[~mask_cancel, 'so_luong'].sum()      # tổng SL bán ra (dương)
cancel_qty = df.loc[mask_cancel, 'so_luong'].abs().sum() # tổng SL huỷ/trả (lấy trị tuyệt đối)

ty_le_huy = cancel_qty / total_qty * 100 if total_qty > 0 else 0

ans = round(ty_le_huy, 2)
print(f"Tổng SL bán: {total_qty}, SL huỷ/trả: {cancel_qty}, Tỉ lệ huỷ: {ans}%")
```
- **Kết quả cuối**: ❌ THẤT BẠI

## Câu 5/50: q_006c26c65d50 | Biz: biz_112
- **Câu hỏi**: thang 7/2026 co bao nhiu don co dthu tu 55.000 dong tro len
- **Đáp án đúng**: 2345 (Type: number)
