# DataMate public — 28_20_23

- Model: `openai/gpt-oss-120b`
- Câu: 1 (từ #0)
- Rulebook: 3026 ký tự

## 1. q_008fdebb6ec9 | dev_002 | as_of 2026-05-24
- **Hỏi**: Tháng 11 năm 2025, nhóm trà có mặt hàng nào bán được nhiều ly nhất?
- **Gold**: (không có) (-)
- **Code** (lần 1):
```python
# -*- coding: utf-8 -*-
# Solution for: "Tháng 11 năm 2025, nhóm trà có mặt hàng nào bán được nhiều ly nhất?"
# Required output variables: ans, ans_type

# 1. Load all sales tables that contain November 2025 data
df_sales = get_all_dfs_by_keyword(dfs, ['BanHang_T11_2025'])

# 2. Validate data existence
if df_sales is None or len(df_sales) == 0:
    ans, ans_type = None, "unanswerable"
else:
    # 3. Standardize column names (remove leading/trailing spaces, unify case)
    df_sales.columns = [c.strip() for c in df_sales.columns]

    # 4. Parse order date
    df_sales['Ngày đặt hàng'] = parse_date_safe(df_sales['Ngày đặt hàng'])

    # 5. Keep only orders placed in November 2025
    df_sales = df_sales[
        (df_sales['Ngày đặt hàng'].dt.year == 2025) &
        (df_sales['Ngày đặt hàng'].dt.month == 11)
    ]

    # 6. Exclude cancelled or returned orders
    #   - Cancelled: status contains 'hủy' / 'cancel'
    #   - Returned: status contains 'trả hàng' / 'return'
    status_lower = df_sales['Trạng thái đơn hàng'].astype(str).str.lower()
    mask_not_cancel = ~status_lower.str.contains('hủy|huỷ|cancel', na=False)
    mask_not_return = ~status_lower.str.contains('trả hàng|return', na=False)
    df_sales = df_sales[mask_not_cancel & mask_not_return]

    # 7. Filter only products belonging to the "trà" group
    #    Assuming product names containing the word "trà" (case‑insensitive)
    prod_mask = df_sales['Tên sản phẩm'].astype(str).str.lower().str.contains('trà')
    df_sales = df_sales[prod_mask]

    # 8. Clean quantity column
    df_sales['Số lượng sản phẩm'] = clean_number(df_sales['Số lượng sản phẩm'])

    # 9. If there is a conversion table, convert quantities to the basic unit (ly)
    #    The conversion table maps product → unit → rate → basic unit.
    #    For simplicity, we assume the basic unit for tea products is "ly".
    #    If a conversion is needed, join and apply the rate.
    if 'DanhSachQuyDoi' in dfs:
        df_conv = get_df_by_keyword(dfs, ['DanhSachQuyDoi'])
        if df_conv is not None and len(df_conv) > 0:
            # Keep only conversion rows that map to the basic unit "ly"
            df_conv = df_conv[df_conv['Đơn vị cơ bản'].astype(str).str.lower() == 'ly']
            # Merge to get conversion rate
            df_sales = df_sales.merge(
                df_conv[['Tên sản phẩm', 'Tỉ lệ quy đổi']],
                on='Tên sản phẩm',
                how='left'
            )
            # If a rate exists, apply it; otherwise keep original quantity
            df_sales['Tỉ lệ quy đổi'] = pd.to_numeric(df_sales['Tỉ lệ quy đổi'], errors='coerce')
            df_sales['Số lượng (ly)'] = df_sales.apply(
                lambda r: r['Số lượng sản phẩm'] * r['Tỉ lệ quy đổi']
                if pd.notnull(r['Tỉ lệ quy đổi']) else r['Số lượng sản phẩm'],
                axis=1
            )
        else:
            df_sales['Số lượng (ly)'] = df_sales['Số lượng sản phẩm']
    else:
        df_sales['Số lượng (ly)'] = df_sales['Số lượng sản phẩm']

    # 10. Aggregate total quantity per product
    agg = (
        df_sales.groupby('Tên sản phẩm', as_index=False)['Số lượng (ly)']
        .sum()
        .rename(columns={'Số lượng (ly)': 'Tổng_lượng'})
    )

    # 11. Determine the product with the highest total quantity
    if agg.empty:
        ans, ans_type = None, "unanswerable"
    else:
        top_row = agg.sort_values(
            by=['Tổng_lượng', 'Tên sản phẩm'],
            ascending=[False, True]
        ).iloc[0]
        ans = top_row['Tên sản phẩm']
        ans_type = "string"
```
- **Dự đoán**: string = Trà đào cam sả (M)


## Tổng kết
- Đúng: 0
- Sai: 0
- Bỏ qua: 0
- Lỗi: 0
