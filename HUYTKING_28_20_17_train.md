# DataMate train — 28_20_17

- Model: `openai/gpt-oss-120b`
- Câu: 3 (từ #0)
- Rulebook: 3026 ký tự

## 1. q_001883280e83 | biz_128 | as_of 2026-09-07
- **Hỏi**: tháng này tổng giá trị các phiếu nhập hàng là bao nhiu
- **Gold**: 89526400 (number)
- **Code**:
```python
# -*- coding: utf-8 -*-
import pandas as pd

# as_of_date is provided by the environment (2026-09-07)
# ----------------------------------------------------
# 1. Load tables
df_nhap = get_df_by_keyword(dfs, ['DanhSachNhapHang'])
df_ct   = get_df_by_keyword(dfs, ['DanhSachChiTietNhapHang'])

# 2. Kiểm tra dữ liệu tồn tại
if df_nhap is None or df_ct is None or len(df_nhap) == 0 or len(df_ct) == 0:
    ans, ans_type = None, "unanswerable"
else:
    # 3. Chuẩn hoá và lọc thời gian (tháng hiện tại)
    df_nhap['Thời gian'] = parse_date_safe(df_nhap['Thời gian'])
    # chỉ giữ các phiếu nhập trong tháng của as_of_date
    cur_year  = as_of_date.year
    cur_month = as_of_date.month
    df_nhap_month = df_nhap[
        (df_nhap['Thời gian'].dt.year == cur_year) &
        (df_nhap['Thời gian'].dt.month == cur_month)
    ]

    # 4. Loại bỏ phiếu nhập bị hủy (nếu có)
    df_nhap_month = df_nhap_month[
        ~df_nhap_month['Trạng thái']
        .astype(str)
        .str.lower()
        .str.contains('hủy|huỷ|cancel', na=False)
    ]

    # 5. Chuẩn hoá mã nhập hàng để join
    df_nhap_month['Mã nhập hàng'] = normalize_id(df_nhap_month['Mã nhập hàng'])
    df_ct['Mã nhập hàng']      = normalize_id(df_ct['Mã nhập hàng'])

    # 6. Lọc chi tiết chỉ thuộc các phiếu nhập đã chọn
    df_ct_month = df_ct[df_ct['Mã nhập hàng'].isin(df_nhap_month['Mã nhập hàng'])].copy()

    # 7. Làm sạch số lượng và đơn giá
    df_ct_month['Số lượng'] = clean_number(df_ct_month['Số lượng'])
    df_ct_month['Đơn giá']  = clean_money(df_ct_month['Đơn giá'])

    # 8. Tính giá trị từng dòng và tổng
    df_ct_month['Giá trị'] = df_ct_month['Số lượng'] * df_ct_month['Đơn giá']
    total_value = df_ct_month['Giá trị'].sum()

    # 9. Kết quả
    ans = int(total_value) if not pd.isna(total_value) else 0
    ans_type = "number"
```
- **Kết quả**: ✅ ĐÚNG

## 2. q_00195e1e4049 | biz_124 | as_of 2026-05-25
- **Hỏi**: Thuốc có hoạt chất Natri clorid tháng này bán được tổng cộng bao nhiêu tiền?
- **Gold**: 2954200 (number)
- **Code**:
```python
# Load required tables
df_hoa_don = get_df_by_keyword(dfs, ['BanHang_HoaDon'])
df_chi_tiet = get_df_by_keyword(dfs, ['BanHang_ChiTietHoaDon'])
df_thuoc = get_df_by_keyword(dfs, ['BanHang_Thuoc'])

# Validate presence
if any(df is None or len(df) == 0 for df in [df_hoa_don, df_chi_tiet, df_thuoc]):
    ans, ans_type = None, "unanswerable"
else:
    # Clean and prepare dates
    df_hoa_don['Ngày bán'] = parse_date_safe(df_hoa_don['Ngày bán'])
    # Filter orders placed in current month up to as_of_date
    start_month = pd.Timestamp(as_of_date).replace(day=1)
    end_month = pd.Timestamp(as_of_date)
    df_hoa_don_month = df_hoa_don[
        (df_hoa_don['Ngày bán'] >= start_month) &
        (df_hoa_don['Ngày bán'] <= end_month)
    ]

    # Exclude cancelled orders
    df_hoa_don_month = df_hoa_don_month[
        ~df_hoa_don_month['Trạng thái'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)
    ]

    # Identify orders that have any return (return flag not provided, assume status indicates return)
    # Here we treat orders with status containing 'trả' as returned
    returned_ids = df_hoa_don_month[
        df_hoa_don_month['Trạng thái'].astype(str).str.lower().str.contains('trả|return', na=False)
    ]['Mã giao dịch'].unique()
    df_hoa_don_month = df_hoa_don_month[~df_hoa_don_month['Mã giao dịch'].isin(returned_ids)]

    # Join with invoice details
    df_chi_tiet['Mã giao dịch'] = normalize_id(df_chi_tiet['Mã giao dịch'])
    df_hoa_don_month['Mã giao dịch'] = normalize_id(df_hoa_don_month['Mã giao dịch'])
    df_detail = df_chi_tiet.merge(df_hoa_don_month[['Mã giao dịch']], on='Mã giao dịch', how='inner')

    # Filter products with active ingredient "Natri clorid"
    df_thuoc['Hoạt chất'] = df_thuoc['Hoạt chất'].astype(str).str.lower()
    natri_ids = df_thuoc[df_thuoc['Hoạt chất'].str.contains('natri clorid', na=False)]['Mã HH'].unique()
    df_detail['Ma hang'] = normalize_id(df_detail['Ma hang'])
    natri_ids = [normalize_id(x) for x in natri_ids]
    df_natri = df_detail[df_detail['Ma hang'].isin(natri_ids)]

    # Calculate total revenue (sum of Thanh tien)
    df_natri['Thanh tien'] = clean_money(df_natri['Thanh tien'])
    total_money = df_natri['Thanh tien'].sum()
    ans = int(total_money)
    ans_type = "number"
```
- **Runtime lỗi**: Lỗi Runtime: 'Mã giao dịch'

## 3. q_002d03ebbded | biz_120 | as_of 2025-04-30
- **Hỏi**: Tổng doanh thu trong ngày hôm nay là bao nhiêu?
- **Gold**: 10309400 (number)
- **Code**:
```python
# Tổng doanh thu trong ngày hôm nay (as_of_date = 2025-04-30)

# 1. Lấy bảng hoá đơn (các tháng có thể chứa ngày hôm nay)
df_hd = get_df_by_keyword(dfs, [
    'DanhSachHoaDon_04.2025', 'DanhSachHoaDon_05.2025',
    'DanhSachHoaDon_03.2025', 'DanhSachHoaDon_02.2025',
    'DanhSachHoaDon_01.2025', 'DanhSachHoaDon_04.2026',
    'DanhSachHoaDon_03.2026', 'DanhSachHoaDon_02.2026',
    'DanhSachHoaDon_01.2026'
])

if df_hd is None or len(df_hd) == 0:
    ans, ans_type = None, "unanswerable"
else:
    # 2. Chuẩn hoá ngày đặt (cột 'Thời gian')
    df_hd['Ngày_đặt'] = parse_date_safe(df_hd['Thời gian'])

    # 3. Lọc chỉ các đơn đặt trong ngày as_of_date
    target_date = pd.to_datetime('2025-04-30')
    df_today = df_hd[df_hd['Ngày_đặt'].dt.normalize() == target_date]

    # 4. Loại bỏ đơn hủy và đơn trả hàng
    # - Trạng thái hủy
    df_today = df_today[~df_today['Trạng thái'].astype(str).str.lower().str.contains('hủy|huỷ|cancel', na=False)]

    # - Trả hàng: nếu có bất kỳ dòng chi tiết nào có số lượng trả > 0 thì toàn bộ đơn bị loại
    #   Lấy chi tiết hoá đơn
    df_ct = get_df_by_keyword(dfs, ['DanhSachHoaDonChiTiet'])
    if df_ct is not None and len(df_ct) > 0:
        df_ct['Mã hóa đơn'] = normalize_id(df_ct['Mã hóa đơn'])
        # Giả sử cột 'Số lượng trả' không có, dùng thông tin trả hàng từ chi tiết trả (không có trong mô tả)
        # Vì không có cột trả hàng rõ ràng, chỉ dựa vào trạng thái 'Trạng thái' ở bảng hoá đơn.
        # Do đó, ở đây chỉ loại bỏ các đơn có trạng thái chứa 'trả' hoặc 'hoàn trả'
        df_today = df_today[~df_today['Trạng thái'].astype(str).str.lower().str.contains('trả|hoàn trả', na=False)]

    # 5. Tính doanh thu: tổng tiền hàng (cột 'Tổng tiền hàng') sau khi làm sạch tiền
    df_today['Tổng tiền hàng'] = clean_money(df_today['Tổng tiền hàng'])
    total_revenue = df_today['Tổng tiền hàng'].sum()

    ans = int(total_revenue)
    ans_type = "number"
```
- **Kết quả**: ❌ SAI | Gold: 10309400 (number)


## Tổng kết
- Đúng: 1
- Sai: 1
- Bỏ qua: 0
- Lỗi: 1
