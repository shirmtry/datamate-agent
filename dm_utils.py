"""Parsing helpers + per-business loaders for DataMate data."""
import os, re, glob, sqlite3, unicodedata, functools
import warnings
import numpy as np
import pandas as pd
warnings.filterwarnings('ignore')
pd.set_option('future.no_silent_downcasting', True)

ROOT = os.path.dirname(os.path.abspath(__file__))


def unaccent(s):
    s = str(s).replace('đ', 'd').replace('Đ', 'D')
    s = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


def norm(s):
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return ''
    s = unaccent(str(s)).lower()
    s = re.sub(r'[^a-z0-9%+]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def parse_money(v):
    if v is None:
        return np.nan
    if isinstance(v, (int, float, np.integer, np.floating)):
        return float(v)
    s = str(v).strip().lower().replace('đ', '').replace('vnd', '').replace(' ', '').replace('\u00a0', '')
    if s in ('', 'nan', 'none', '-'):
        return np.nan
    neg = s.startswith('-')
    s = s.lstrip('-+')
    try:
        if 'tr' in s:
            a, b = s.split('tr', 1)
            val = float(a.replace(',', '.')) * 1e6 if a else 0.0
            b = re.sub(r'\D', '', b)
            if b:
                val += int(b) * 10 ** (6 - len(b))
        elif s.endswith('k'):
            val = float(s[:-1].replace(',', '.')) * 1000
        elif ',' in s and '.' in s:
            if s.rfind(',') > s.rfind('.'):
                val = float(s.replace('.', '').replace(',', '.'))
            else:
                val = float(s.replace(',', ''))
        elif '.' in s:
            val = float(s.replace('.', '')) if re.fullmatch(r'\d{1,3}(\.\d{3})+', s) else float(s)
        elif ',' in s:
            val = float(s.replace(',', '')) if re.fullmatch(r'\d{1,3}(,\d{3})+', s) else float(s.replace(',', '.'))
        else:
            val = float(s)
    except ValueError:
        return np.nan
    return -val if neg else val


def parse_qty(v):
    if v is None:
        return np.nan
    if isinstance(v, (int, float, np.integer, np.floating)):
        return float(v)
    m = re.match(r'\s*(-?\d+(?:[.,]\d+)?)', str(v))
    return float(m.group(1).replace(',', '.')) if m else np.nan


def parse_date(v, year=None):
    """Return pd.Timestamp (date or datetime) or NaT."""
    if v is None:
        return pd.NaT
    if isinstance(v, pd.Timestamp):
        return v
    if hasattr(v, 'year') and hasattr(v, 'month'):
        return pd.Timestamp(v)
    if isinstance(v, (int, float, np.integer, np.floating)):
        if np.isnan(v):
            return pd.NaT
        if 20000 < v < 80000:
            return pd.Timestamp('1899-12-30') + pd.Timedelta(days=float(v))
        return pd.NaT
    s = str(v).strip()
    if not s or s.lower() in ('nan', 'nat', 'none'):
        return pd.NaT
    if re.fullmatch(r'\d{5}(\.0+)?', s):
        return parse_date(float(s))
    m = re.fullmatch(r'(\d{1,2})\s*thg\s*(\d{1,2})\s*(\d{4})', s)
    if m:
        return pd.Timestamp(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    m = re.fullmatch(r'(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T](\d{1,2}):(\d{2})(?::(\d{2}))?)?.*', s)
    if m:
        g = [int(x) if x else 0 for x in m.groups()]
        return pd.Timestamp(g[0], g[1], g[2], g[3], g[4], g[5])
    m = re.fullmatch(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})(?:\s+(\d{1,2}):(\d{2})(?::(\d{2}))?)?', s)
    if m:
        y = int(m.group(3)); y = y + 2000 if y < 100 else y
        g = [int(x) if x else 0 for x in m.groups()[3:]]
        return pd.Timestamp(y, int(m.group(2)), int(m.group(1)), *g)
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})', s)
    if m and year:
        return pd.Timestamp(int(year), int(m.group(2)), int(m.group(1)))
    try:
        return pd.Timestamp(s)
    except Exception:
        return pd.NaT


WALKIN = {'', 'le', 'kl', 'khach le', 'khach vang lai', 'vang lai', 'nan', 'none'}


def clean_cust_name(s):
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return None
    s = str(s).strip()
    s = re.sub(r'\s*[-(]?\s*\+?\(?0\d[\d .]{7,13}\)?\s*$', '', s).strip(' -()')
    if norm(s) in WALKIN:
        return None
    return s


def status_of(s):
    n = norm(s)
    if not n:
        return 'done'
    if re.search(r'huy|cancel', n):
        return 'cancel'
    if re.search(r'tra hang|tra lai|return|hoan hang|hoan tra|khach tra|mang tra', n):
        return 'return'
    if re.search(r'khong giao duoc', n):
        return 'cancel'
    if re.search(r'dang giao|chua giao|shipping|delivering|dang van chuyen|cho giao|giao hang', n):
        return 'shipping'
    return 'done'


def read_table(path, sheet=0, header_hint=None):
    """Read an xlsx sheet/csv as raw strings-ish frame and auto-detect header row."""
    if path.endswith('.csv'):
        for enc in ('utf-8', 'utf-8-sig', 'cp1258', 'latin1'):
            try:
                return pd.read_csv(path, encoding=enc, dtype=object)
            except UnicodeDecodeError:
                continue
    raw = pd.read_excel(path, sheet_name=sheet, header=None, dtype=object)
    best, bi = -1, 0
    for i in range(min(8, len(raw))):
        row = raw.iloc[i]
        score = sum(isinstance(x, str) for x in row) - (0 if header_hint is None else 0)
        nonnull = row.notna().sum()
        if header_hint and any(isinstance(x, str) and x.strip() == header_hint for x in row):
            bi = i; break
        if nonnull == len(row) and score >= nonnull * 0.8 and score > best:
            best, bi = score, i
            break
        if score > best:
            best, bi = score, i
    df = raw.iloc[bi + 1:].reset_index(drop=True)
    df.columns = [str(c).strip() if c is not None and not (isinstance(c, float) and np.isnan(c)) else f'col{j}'
                  for j, c in enumerate(raw.iloc[bi])]
    return df.dropna(how='all')


# ---------------------------------------------------------------- README-driven loader
FIELD_RULES = [  # (description prefix (normalized), field)
    ('ma don', 'oid'), ('so hoa don', 'oid'),
    ('ngay ban', 'date'), ('thoi diem dat don', 'ts'), ('gio dat don', 'time'),
    ('trang thai don', 'status'),
    ('ten khach', 'cust_name'), ('ma khach', 'cust_code'), ('nhom khach', 'cgroup'),
    ('ten hang', 'item'), ('ma hang', 'code'), ('nhom hang', 'group'),
    ('so luong da doi ra don vi co ban', 'bqty'), ('so luong', 'qty'),
    ('don gia', 'price'), ('thanh tien sau giam', 'amount'), ('thanh tien cua dong', 'amount'),
    ('don vi tinh', 'unit'), ('kenh ban', 'channel'), ('ma nhan vien ban', 'staff'),
    ('hinh thuc thanh toan', 'pay'), ('ghi chu cua don', 'note'), ('ghi chu', 'note'),
    ('gia von', 'cost'),
]
HEADER_WORDS = {'ten san pham', 'ngay dat hang', 'trang thai don hang', 'so luong san pham', 'ten hang', 'ngay', 'sl', 'hang ban', 'thoi gian', 'trang thai xu ly', 'sl ban', 'ten hang hoa', 'trang thai', 'so luong'}
ORDER_FIELDS = ['date', 'ts', 'time', 'status', 'cust_name', 'cust_code', 'cgroup', 'channel', 'staff', 'pay', 'note']
NON_ITEM_RE = re.compile(r'^(voucher|dung \d+ diem|phi ship|phi giao hang)$')


def parse_readme(path):
    txt = open(path, encoding='utf-8').read()
    secs = []
    for m in re.finditer(r'^## Cột trong `([^`]+)`(?:, sheet `([^`]+)`)?\n(.*?)(?=^## |\Z)', txt, re.S | re.M):
        cols = re.findall(r'^- \*\*(.+?)\*\*: (.*)$', m.group(3), re.M)
        secs.append({'file': m.group(1), 'sheet': m.group(2), 'cols': cols})
    end = re.search(r'Dữ liệu có đến hết (\d{1,2}/\d{1,2}/\d{4})', txt)
    return txt, secs, (parse_date(end.group(1)) if end else None)


def map_fields(cols):
    out = {}
    for col, desc in cols:
        d = norm(desc)
        for pre, f in FIELD_RULES:
            if d.startswith(pre) and f not in out:
                out[f] = col
                break
    return out


def files_for(bdir, pattern):
    if '<' in pattern:
        rx = '^' + re.sub(r'<[^>]+>', r'[^/]+', re.escape(pattern).replace(r'\<', '<').replace(r'\>', '>')) + '$'
        names = [f for f in os.listdir(bdir) if re.match(rx, f)]
    else:
        stem, ext = os.path.splitext(pattern)
        stem = unicodedata.normalize('NFC', stem)
        def fix(f):
            try:
                f = f.encode('cp437').decode('utf-8')
            except Exception:
                pass
            return unicodedata.normalize('NFC', f)
        names = [f for f in os.listdir(bdir) if fix(f) == unicodedata.normalize('NFC', pattern)
                 or re.fullmatch(re.escape(stem) + r'(_\w+)?' + re.escape(ext), fix(f))]
    return sorted(os.path.join(bdir, f) for f in names)


def year_of(*names):
    for n in names:
        m = re.search(r'(20\d\d)', str(n))
        if m:
            return int(m.group(1))
    return None


def read_section(bdir, sec):
    frames = []
    for p in files_for(bdir, sec['file']):
        if p.endswith('.csv'):
            df = read_table(p); df['_year'] = year_of(os.path.basename(p)); frames.append(df)
            continue
        sheets = [sec['sheet']] if sec['sheet'] else pd.ExcelFile(p).sheet_names
        want = [c for c, _ in sec['cols']]
        for sh in sheets:
            df = read_table(p, sh)
            if len(set(want) & set(df.columns)) < max(1, len(want) // 2):
                continue
            df['_year'] = year_of(sh, os.path.basename(p))
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else None


class Biz:
    pass


@functools.lru_cache(maxsize=4)
def load_biz_data(bdir):
    import pickle
    bdir = os.path.abspath(bdir)
    cdir = os.path.join(ROOT, '.cache'); os.makedirs(cdir, exist_ok=True)
    mt = max(os.path.getmtime(os.path.join(bdir, f)) for f in os.listdir(bdir))
    mt = max(mt, os.path.getmtime(os.path.abspath(__file__)))
    cp = os.path.join(cdir, bdir.strip('/').replace('/', '_') + '.pkl')
    if os.path.exists(cp) and os.path.getmtime(cp) > mt:
        with open(cp, 'rb') as fh:
            return pickle.load(fh)
    b = _load_biz(bdir)
    with open(cp, 'wb') as fh:
        pickle.dump(b, fh)
    return b


def _load_biz(bdir):
    b = Biz(); b.dir = bdir
    b.readme, secs, b.data_end = parse_readme(os.path.join(bdir, 'README.md'))
    sales, orders, conv, cat, codecat = None, None, {}, {}, {}
    item_groups, item_base, aliases, custs, code_groups = {}, {}, {}, {}, {}
    seen = set()
    for sec in secs:
        fm = map_fields(sec['cols'])
        dn = {norm(d): c for c, d in sec['cols']}
        name_col = fm.get('item') or dn.get('ten')
        key = (tuple(files_for(bdir, sec['file'])), sec['sheet'])
        if key in seen:
            continue
        seen.add(key)
        if 'oid' in fm and ('item' in fm or 'code' in fm) and ('amount' in fm or 'status' in fm):
            df = read_section(bdir, sec)
            if df is not None:
                df = df[[c for c in fm.values() if c in df] + ['_year']].rename(columns={v: k for k, v in fm.items()})
                sales = df if sales is None else pd.concat([sales, df], ignore_index=True)
            continue
        if 'oid' in fm and ('date' in fm or 'ts' in fm):
            df = read_section(bdir, sec)
            if df is not None:
                keep = [c for f, c in fm.items() if f in ['oid'] + ORDER_FIELDS and c in df]
                df = df[keep + ['_year']].rename(columns={v: k for k, v in fm.items()})
                orders = df if orders is None else pd.concat([orders, df], ignore_index=True)
            continue
        big = next((c for d, c in dn.items() if d.startswith('he so')), None)
        if big and name_col:
            df = read_section(bdir, sec)
            bu = next((c for d, c in dn.items() if d.startswith('don vi co ban')), None)
            lu = next((c for d, c in dn.items() if d.startswith('don vi lon')), None)
            for _, r in df.iterrows():
                k = norm(r[name_col])
                conv.setdefault(k, {})[norm(r[lu])] = parse_qty(r[big])
                if bu: item_base[k] = str(r[bu]).strip()
            continue
        if 'cust_code' in fm and dn.get('ten') and 'oid' not in fm:
            df = read_section(bdir, sec)
            for _, r in df.iterrows():
                custs[str(r[fm['cust_code']]).strip()] = (str(r[dn['ten']]).strip(), r[fm['cgroup']] if 'cgroup' in fm else None)
            continue
        if name_col and ('group' in fm or 'code' in fm or any(d.startswith('quy doi') for d in dn)) and 'oid' not in fm:
            df = read_section(bdir, sec)
            if df is None:
                continue
            qd = next((c for d, c in dn.items() if d.startswith('quy doi')), None)
            alias = next((c for d, c in dn.items() if d.startswith('ten goi khac')), None)
            dvt = next((c for c, d in sec['cols'] if norm(d) in ('don vi co ban', 'don vi tinh')), None)
            for _, r in df.iterrows():
                if pd.isna(r[name_col]): continue
                k = norm(r[name_col]); cat[k] = str(r[name_col]).strip()
                if 'code' in fm and pd.notna(r[fm['code']]): codecat[str(r[fm['code']]).strip()] = cat[k]
                if 'group' in fm and pd.notna(r[fm['group']]):
                    item_groups[k] = str(r[fm['group']]).strip()
                    if 'code' in fm: code_groups[str(r[fm['code']]).strip()] = item_groups[k]
                if dvt and pd.notna(r[dvt]): item_base.setdefault(k, str(r[dvt]).strip())
                if qd and pd.notna(r[qd]):
                    m = re.match(r'\s*1\s+(.+?)\s*=\s*(\d+(?:[.,]\d+)?)\s*(.+)', str(r[qd]))
                    if m: conv.setdefault(k, {})[norm(m.group(1))] = float(m.group(2).replace(',', '.'))
                if alias and pd.notna(r[alias]):
                    for al in str(r[alias]).split(','):
                        if norm(al): aliases[norm(al)] = k
    for m in re.finditer(r'\*\*Hàng theo (\w+)\*\*: (.+?) bán theo \w+, 1 (\w+) = (\d+) (\w+)', b.readme):
        for it in m.group(2).split(', '):
            conv.setdefault(norm(it), {})[norm(m.group(3))] = float(m.group(4))
    for m in re.finditer(r'^\s+- (.+?): 1 (.+?) = (\d+(?:[.,]\d+)?) (.+)$', b.readme, re.M):
        conv.setdefault(norm(m.group(1)), {})[norm(m.group(2))] = float(m.group(3).replace(',', '.'))
    if sales is not None and orders is not None:
        oc = [c for c in orders.columns if c not in sales.columns or c == 'oid']
        orders = orders[oc].copy(); orders['oid'] = orders['oid'].astype(str).str.strip()
        sales['oid'] = sales['oid'].astype(str).str.strip()
        sales = sales.merge(orders.drop_duplicates('oid'), on='oid', how='left')
    if sales is not None and 'item' not in sales and 'code' in sales:
        sales['item'] = sales['code'].astype(str).str.strip().map(codecat)
    if sales is not None and 'group' not in sales and code_groups and 'code' in sales:
        sales['group'] = sales['code'].astype(str).str.strip().map(code_groups)
    if sales is not None and custs and 'cust_code' in sales:
        cc = sales['cust_code'].astype(str).str.strip()
        if 'cust_name' not in sales: sales['cust_name'] = cc.map(lambda x: custs.get(x, (None,))[0])
        if 'cgroup' not in sales: sales['cgroup'] = cc.map(lambda x: custs.get(x, (None, None))[1])
    if sales is None:
        sales = _custom_sales(bdir)
    lo = os.path.join(bdir, 'DonHang_Lo.xlsx')
    if sales is not None and os.path.exists(lo):
        d = read_table(lo)
        ret = set(d.loc[pd.to_numeric(d['Số lượng trả'], errors='coerce') > 0, 'Mã đơn hàng'].astype(str).str.strip())
        oid = sales['oid'].astype(str).str.strip().where(sales['oid'].notna()).ffill()
        sales['status'] = np.where(oid.isin(ret), 'Trả hàng', sales['status'] if 'status' in sales else 'Hoàn thành')
    b.conv, b.item_groups, b.item_base, b.aliases, b.catalog = conv, item_groups, item_base, aliases, cat
    b.lines = build_lines(b, sales, {c: c for c in sales.columns if c != '_year'}) if sales is not None else None
    return b



def _custom_sales(bdir):
    import sqlite3, glob
    db = glob.glob(os.path.join(bdir, '*.sqlite'))
    if db:
        c = sqlite3.connect(db[0])
        df = pd.read_sql_query("""select d.MaHoaDon oid, substr(d.ThoiGianLap,1,10) date, d.ThoiGianLap ts,
            case when d.MaHoaDon in (select MaHoaDon from tra_hang) then 'Trả hàng' when d.TinhTrang='completed' then 'Hoàn thành'
                 when d.TinhTrang='cancelled' then 'Đã hủy' when d.TinhTrang='returned' then 'Trả hàng' else 'Đang giao' end status,
            d.KenhBanHang channel, d.PhuongThucTT pay, d.MaNhanVien staff, d.MaKhachHang cust_code,
            coalesce(k.TenGoi,'Khách lẻ') cust_name, k.LoaiKhachHang cgroup, s.TenGoi item, s.DanhMuc "group",
            t.DonViTinh unit, t.SL qty, t.SLQuyDoi bqty, t.TriGia amount
            from chi_tiet_don t join don_hang d on d.MaHoaDon=t.MaHoaDon
            left join san_pham s on s.MaHangHoa=t.MaHangHoa left join khach_hang k on k.MaKhachHang=d.MaKhachHang""", c)
        return df
    f = os.path.join(bdir, 'danh_sach_hoa_don.csv')
    if os.path.exists(f):
        d = read_table(f)
        return pd.DataFrame({'oid': d['Mã hóa đơn'], 'date': d['Ngày tháng'], 'status': d['Trạng thái đơn'],
                             'cust_name': d['Đối tác'], 'item': 'Tiền hàng', 'qty': 1, 'amount': d['Giá trị hàng']})
    bh = sorted(glob.glob(os.path.join(bdir, 'BanHang_TongHop_*.xlsx')))
    if bh:
        out = []
        for f in bh:
            for sh in pd.ExcelFile(f).sheet_names:
                if sh.startswith('BanHang') and sh.count('_') == 0 or re.fullmatch(r'BanHang.*\d', sh):
                    d = read_table(f, sh)
                    if 'Đơn số' not in d: continue
                    m = {'Đơn số': 'oid', 'Ngày HĐ': 'date', 'Trạng thái giao': 'status', 'Khách hàng (tên)': 'cust_name',
                         'Mã khách': 'cust_code', 'Hàng hóa': 'item', 'ĐV': 'unit', 'S.L': 'qty', 'SL (ĐV cơ bản)': 'bqty',
                         'Thành tiền (đ)': 'amount', 'Mã NV bán': 'staff', 'Hình thức thanh toán': 'pay', 'Nguồn': 'channel'}
                    out.append(d[[k for k in m if k in d]].rename(columns=m))
        if not out:
            return None
        df = pd.concat(out, ignore_index=True)
        x = pd.ExcelFile(bh[0])
        if 'BanHang_HangHoa' in x.sheet_names:
            h = read_table(bh[0], 'BanHang_HangHoa')
            gm = {norm(a): g for a, g in zip(h['Tên hàng hóa'], h['Nhóm hàng'])}
            df['group'] = df['item'].map(lambda v: gm.get(norm(v)))
        if 'BanHang_KhachHang' in x.sheet_names:
            k = read_table(bh[0], 'BanHang_KhachHang')
            cm = {str(a).strip(): g for a, g in zip(k['Mã KH mua'], k['Kiểu khách'])}
            df['cgroup'] = df['cust_code'].map(lambda v: cm.get(str(v).strip()) if pd.notna(v) else None)
        return df
    f = os.path.join(bdir, 'SoBanHang.xlsx')
    if os.path.exists(f):
        x = pd.ExcelFile(f); out = []
        g = read_table(f, 'Ghi tắt') if 'Ghi tắt' in x.sheet_names else None
        gm = {norm(a): b for a, b in zip(g['Ghi tắt'], g['Tên hàng'])} if g is not None else {}
        gl = {norm(b): l for b, l in zip(g['Tên hàng'], g['Loại'])} if g is not None else {}
        for sh in x.sheet_names:
            if sh == 'Ghi tắt': continue
            d = read_table(f, sh)
            if 'STT' not in d: continue
            d['STT'] = d['STT'].ffill()
            note = d['Ghi chú'].fillna('').astype(str) if 'Ghi chú' in d else ''
            item = d['Hàng'].map(lambda v: gm.get(norm(v), v))
            out.append(pd.DataFrame({'oid': d['STT'].astype(str), 'date': d['Ngày'], 'cust_name': d.get('Khách'),
                'status': note.where(note.str.strip() != '', 'Hoàn thành') if isinstance(note, pd.Series) else 'Hoàn thành',
                'item': item, 'group': item.map(lambda v: gl.get(norm(v))), 'qty': d['SL'], 'amount': d['Thành tiền']}))
        return pd.concat(out, ignore_index=True) if out else None
    return None


def build_lines(b, df, fm):
    df = df.copy()
    oc = fm['oid']
    df = df[df[oc].astype(str).str.strip() != oc]
    for f in ('item', 'date', 'status', 'qty'):
        if f in fm:
            hdr = df[fm[f]].map(lambda v: norm(v) in HEADER_WORDS)
            df = df[~hdr]
    blank = df[oc].isna() | (df[oc].astype(str).str.strip() == '')
    if blank.any():
        for f in ['oid'] + ORDER_FIELDS:
            if f in fm and fm[f] in df:
                col = df[fm[f]].where(~(df[fm[f]].astype(str).str.strip() == ''))
                df[fm[f]] = col.where(~blank, np.nan).ffill() if f == 'oid' else col.where(~blank).ffill().where(blank, col)
    df = df.drop_duplicates()
    L = pd.DataFrame(index=df.index)
    L['oid'] = df[oc].where(df[oc].notna() & (df[oc].astype(str).str.strip() != ''))
    L['oid'] = L['oid'].ffill().astype(str).str.strip()
    for f in ORDER_FIELDS + ['item', 'code', 'group', 'unit']:
        if f in fm:
            L[f] = df[fm[f]].where(df[fm[f]].astype(str).str.strip() != '')
    if '_year' not in df: df['_year'] = None
    yrs = df['_year']
    if 'date' in L:
        L['date'] = [parse_date(v, y) for v, y in zip(L['date'], yrs)]
    if 'ts' in L:
        L['ts'] = [parse_date(v) for v in L['ts']]
    if 'time' in L:
        L['ts'] = [parse_date(v) for v in L['time']]
    present = [f for f in ORDER_FIELDS if f in L]
    if present:
        L[present] = L.groupby('oid', sort=False)[present].transform(lambda s: s.ffill().bfill())
    if 'date' not in L:
        L['date'] = L['ts']
    L['date'] = pd.to_datetime(L['date']).dt.normalize()
    if 'ts' in L:
        L['date'] = L['date'].fillna(pd.to_datetime(L['ts']).dt.normalize())
        L['ts'] = pd.to_datetime(L['ts'])
    L['qty'] = [parse_qty(v) for v in df[fm['qty']]] if 'qty' in fm else 1.0
    L['amount'] = [parse_money(v) for v in df[fm['amount']]] if 'amount' in fm else np.nan
    if 'price' in fm:
        pr = pd.Series([parse_money(v) for v in df[fm['price']]], index=df.index)
        L['amount'] = L['amount'].fillna(pr * L['qty'])
    L['cost'] = [parse_money(v) for v in df[fm['cost']]] if 'cost' in fm else np.nan
    L['bqty'] = [parse_qty(v) for v in df[fm['bqty']]] if 'bqty' in fm else np.nan
    L['item'] = L['item'].astype(str).str.strip()
    L = L[L['item'].notna() & (L['item'] != 'nan')]
    # topping split
    if 'Topping' in b.readme and L['item'].str.contains(r' \+ ').any():
        rows = []
        for r in L.itertuples(index=False):
            parts = r.item.split(' + ')
            if len(parts) == 1:
                rows.append(r._asdict()); continue
            main = r._asdict(); tot = 0
            for tp in parts[1:]:
                m = re.match(r'\s*(?:(\d+)\s+)?(.+?)\s*\(([^)]*)\)\s*$', tp)
                if not m:
                    continue
                n = float(m.group(1) or 1); money = parse_money(m.group(3)); tot += money
                t = dict(main); t.update(item='Topping ' + m.group(2).strip(), qty=n, amount=money, bqty=np.nan,
                                         unit='phần')
                rows.append(t)
            main['item'] = parts[0].strip(); main['amount'] = main['amount'] - tot
            rows.append(main)
        L = pd.DataFrame(rows)
    L['ikey'] = L['item'].map(norm)
    L = L[~L['ikey'].str.match(r'(tong|cong)( ngay| thang| cong| tien| so| ca| don|$)|(total|subtotal)\b')]
    L['is_item'] = ~L['ikey'].str.match(NON_ITEM_RE)
    L['is_fee'] = L['ikey'].eq('phi phuc vu')
    # canonical item names
    canon = {}
    for k, g in L.groupby('ikey')['item']:
        if k in b.catalog:
            canon[k] = b.catalog[k]
        else:
            vc = g.value_counts()
            withacc = [v for v in vc.index if unaccent(v) != v]
            canon[k] = (withacc or list(vc.index))[0]
    L['item'] = L['ikey'].map(canon)
    if 'group' not in L and b.item_groups:
        L['group'] = L['ikey'].map(b.item_groups)
    # base qty
    ukey = L['unit'].map(norm) if 'unit' in L else pd.Series('', index=L.index)
    def fac(k, u):
        return b.conv.get(k, {}).get(u, 1.0)
    calc = [q * fac(k, u) for q, k, u in zip(L['qty'], L['ikey'], ukey)]
    L['bqty'] = L['bqty'].fillna(pd.Series(calc, index=L.index))
    base = {}
    for k in L['ikey'].unique():
        base[k] = b.item_base.get(k)
    if 'unit' in L:
        for k, g in L[['ikey', 'unit']].assign(u=ukey).groupby('ikey'):
            if base.get(k) is None:
                small = g[~g['u'].isin(list(b.conv.get(k, {}).keys()))]['unit'].dropna()
                base[k] = small.map(lambda x: str(x).strip()).mode().iloc[0] if len(small) else None
    L['bunit'] = L['ikey'].map(base)
    # status
    st = L['status'] if 'status' in L else L.get('note', pd.Series('', index=L.index))
    L['lstatus'] = st.map(status_of)
    L.loc[(L['qty'] < 0) | (L['bqty'] < 0), 'lstatus'] = 'return'
    pri = {'cancel': 3, 'return': 2, 'shipping': 1, 'done': 0}
    ost = L.groupby('oid')['lstatus'].agg(lambda s: max(s, key=pri.get))
    L['ostatus'] = L['oid'].map(ost)
    L['valid'] = L['ostatus'].isin(['done', 'shipping'])
    # customers
    if 'cust_code' in L:
        L['cust'] = L['cust_code'].where(L['cust_code'].notna(), None)
        names = L['cust_name'] if 'cust_name' in L else L['cust_code']
        L['cust_disp'] = names
    elif 'cust_name' in L:
        cn = L['cust_name'].map(clean_cust_name)
        L['cust'] = cn.map(lambda x: norm(x) if x else None)
        disp = {}
        for k, g in cn.dropna().groupby(L['cust']):
            vc = g.value_counts(); wa = [v for v in vc.index if unaccent(v) != v]
            disp[k] = (wa or list(vc.index))[0]
        L['cust_disp'] = L['cust'].map(disp)
    return L.reset_index(drop=True)
