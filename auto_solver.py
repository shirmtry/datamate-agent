"""Local rule-based DataMate solver (no LLM/API).

Usage: python auto_solver.py --start 0 --end 20 [--questions public_test/questions.jsonl]
                             [--data public_test/data] [--out submission_public.jsonl]
"""
import argparse, json, math, os, re, sys, traceback
from datetime import timedelta
import numpy as np
import pandas as pd
from dm_utils import ROOT, load_biz_data, norm, unaccent

Unans = type('Unans', (Exception,), {})
Skip = type('Skip', (Exception,), {})

TEEN = [
    (r'\bbao nhi[a-z]*\b|\bbnhi[a-z]*\b|\bbn\b|\bbao nhieu?\b', 'bao nhieu'),
    (r'\bdthu\b|\bdoanh so\b', 'doanh thu'), (r'\bhnay\b|\bhom ni\b|\bbua nay\b|\bbua ni\b', 'hom nay'),
    (r'\bhqua\b|\bbua qua\b', 'hom qua'), (r'\bdh\b|\bdon hang\b|\bhoa don\b', 'don'),
    (r'\b(thang|tuan|nam|quy) ni\b', r'\1 nay'), (r'\bdc\b|\bdk\b|\bduoc[a-z]?\b|\bduocj\b', 'duoc'),
    (r'\bsp\b', 'san pham'), (r'\bthangs\b|\bth\b', 'thang'), (r'\bbans\b', 'ban'),
    (r'\bnh(ta|at[a-z]|ats)\b', 'nhat'), (r'\bnhiu\b|\bnhieuf\b', 'nhieu'), (r'\bko\b|\bkhong\b|\bhok\b', 'khong'),
    (r'\bmon\b|\bmat hang\b|\bhang hoa\b|\bsan pham\b', 'hang'), (r'\bty le\b', 'ti le'), (r'\bphan tram\b', '%'),
    (r'\bthang roi\b', 'thang truoc'), (r'\btuan roi\b', 'tuan truoc'), (r'\bquy roi\b', 'quy truoc'),
    (r'\bnam ngoai\b|\bnam roi\b', 'nam truoc'), (r'\bt(\d{1,2})\s*/', r'thang \1/'),
]


EXTRA = [
    (r'\b(\d+)tr(\d{1,3})\b', lambda m: str(int(m.group(1)) * 1000000 + int(m.group(2).ljust(3, '0')) * 1000)),
    (r'\b(\d+(?:[.,]\d+)?)\s?(?:tr|trieu)\b', lambda m: str(int(float(m.group(1).replace(',', '.')) * 1000000))),
    (r'\b(\d+)\s?k\b', lambda m: str(int(m.group(1)) * 1000)),
    (r'\bth\s?(?=\d)', 'thang '), (r'\bt(?=\d{1,2}[/-]\d)', 'thang '),
    (r'\bth (?=nay|truoc|roi|ni|sau|nao)', 'thang '),
    (r'\b(\d{1,2})/(2[4-7])\b(?!/)', r'\1/20\2'),
    (r'\b(thang|tuan|quy|nam) (ni|nay)\b', r'\1 nay'), (r'\b(thang|tuan|quy) (roi|vua roi|vua qua|truoc do)\b', r'\1 truoc'),
    (r'\bnam (roi|ngoai)\b', 'nam truoc'), (r'\b(bua|hom) (ni|nay)\b|\bhnay\b|\bhom nay\b|\bbua nay\b', 'hom nay'),
    (r'\bhqua\b|\bbua qua\b', 'hom qua'), (r'\b(dh|don hang|dhang|o do)\b', 'don'),
    (r'\bdthu\b|\bdt\b', 'doanh thu'), (r'\bhom nao\b|\bbua nao\b', 'ngay nao'),
    (r'\btu (ngay )?0?1/0?1\b(?!/)( nam nay)?', 'tu dau nam'), (r'\bbill\b|\bhd\b', 'don'),
    (r'\bnhut\b', 'nhat'), (r'\bngaynao\b', 'ngay nao'), (r'\b(ngay|hang|thang|khach|tho|ai) mo\b', r'\1 nao'),
    (r'\blen hay xuong\b|\bcao hay thap hon\b|\bcao hay thap\b|\bnhieu hay it hon\b|\bhon hay thua\b', 'tang hay giam'),
    (r'\bcung so ngay (dau )?(cua )?thang (truoc|roi)\b', 'cung ky thang truoc'), (r'\bnhieudon\b', 'nhieu don'),
    (r'\bquy[sfrxj]\b', 'quy'), (r'\border\b', 'don'), (r'\bmoo?i[xsfrj]\b', 'moi'), (r'\bhown\b', 'hon'), (r'\bcung[fsrxj]\b', 'cung'), (r'\bnhieu[fsrxj]\b', 'nhieu'), (r'\bquaan\b', 'quan'), (r'\bban (duoc )?nhieu tien\b(?! nhat)', 'doanh thu'),
    (r'\btien ban hang\b|\bban duoc bao nhieu tien\b', 'doanh thu'),
]


def qnorm(q):
    s = unaccent(q).lower()
    s = re.sub(r'[^a-z0-9%+/\-.,() ]+', ' ', s)
    s = re.sub(r'(?<=\d)[.,](?=\d{3}(?!\d))', '', s)
    s = re.sub(r'[,()?!]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    for a, b in TEEN:
        s = re.sub(a, b, s)
    for a, b in EXTRA:
        s = re.sub(a, b, s)
    return ' ' + re.sub(r'\s+', ' ', s).strip() + ' '


# ------------------------------------------------------------------ periods
def month_end(y, m):
    return pd.Timestamp(y, m, 1) + pd.offsets.MonthEnd(0)


def ym_rule(m, today):
    y = today.year
    return y if pd.Timestamp(y, m, 1) <= today else y - 1


def parse_periods(n, today):
    """Return list of (start, end, kind, pos) in order of appearance."""
    out = []
    t = today
    def add(pos, s, e, kind, rel=False):
        out.append((pd.Timestamp(s), pd.Timestamp(e), kind, pos, rel))
    used = []
    def free(a, b):
        return all(b <= x or a >= y for x, y in used)
    pats = [
        (r'tu (?:ngay )?(\d{1,2})/(\d{1,2})/(\d{4}) (?:den|toi|-) (?:ngay )?(\d{1,2})/(\d{1,2})/(\d{4})', 'range'),
        (r'(\d{1,2})/(\d{1,2})/(\d{4})', 'day'),
        (r'quy (\d|iv|iii|ii|i)\s*(?:/|-|nam)?\s*(20\d\d)?\b', 'quarter'),
        (r'(?:thang )?(\d{1,2})\s*(?:/|-)\s*(20\d\d)\b', 'month'),
        (r'thang (\d{1,2}) nam (20\d\d)', 'month'),
        (r'thang (\d{1,2})\b(?! ngay)', 'month_noyear'),
        (r'nam (20\d\d)', 'year'),
    ]
    for rx, kind in pats:
        for m in re.finditer(rx, n):
            a, b = m.span()
            if not free(a, b):
                continue
            g = m.groups()
            try:
                if kind == 'range':
                    add(a, pd.Timestamp(int(g[2]), int(g[1]), int(g[0])), pd.Timestamp(int(g[5]), int(g[4]), int(g[3])), 'range')
                elif kind == 'day':
                    d = pd.Timestamp(int(g[2]), int(g[1]), int(g[0])); add(a, d, d, 'day')
                elif kind == 'month':
                    mm, yy = int(g[0]), int(g[1])
                    if not 1 <= mm <= 12: continue
                    add(a, pd.Timestamp(yy, mm, 1), month_end(yy, mm), 'month')
                elif kind == 'month_noyear':
                    mm = int(g[0])
                    if not 1 <= mm <= 12: continue
                    yy = ym_rule(mm, t); add(a, pd.Timestamp(yy, mm, 1), month_end(yy, mm), 'month')
                elif kind == 'quarter':
                    qv = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4}.get(g[0]) or int(g[0])
                    if not 1 <= qv <= 4: continue
                    yy = int(g[1]) if g[1] else ym_rule(3 * qv - 2, t)
                    add(a, pd.Timestamp(yy, 3 * qv - 2, 1), month_end(yy, 3 * qv), 'quarter')
                elif kind == 'year':
                    add(a, pd.Timestamp(int(g[0]), 1, 1), pd.Timestamp(int(g[0]), 12, 31), 'year')
            except ValueError:
                continue
            used.append((a, b))
    rel = [
        (r'\bhom nay\b', lambda: (t, t, 'day')),
        (r'\bhom qua\b', lambda: (t - timedelta(1), t - timedelta(1), 'day')),
        (r'\bhom kia\b', lambda: (t - timedelta(2), t - timedelta(2), 'day')),
        (r'\btuan nay\b', lambda: (t - timedelta(t.weekday()), t, 'week_td')),
        (r'\btuan truoc\b', lambda: (t - timedelta(t.weekday() + 7), t - timedelta(t.weekday() + 1), 'week')),
        (r'\bthang nay\b', lambda: (t.replace(day=1), t, 'month_td')),
        (r'\bthang truoc\b', lambda: ((t.replace(day=1) - timedelta(1)).replace(day=1), t.replace(day=1) - timedelta(1), 'month')),
        (r'\bquy nay\b', lambda: (pd.Timestamp(t.year, 3 * ((t.month - 1) // 3) + 1, 1), t, 'quarter_td')),
        (r'\bquy truoc\b', lambda: (pd.Timestamp(t.year, 3 * ((t.month - 1) // 3) + 1, 1) - pd.offsets.QuarterBegin(1, startingMonth=1),
                                     pd.Timestamp(t.year, 3 * ((t.month - 1) // 3) + 1, 1) - timedelta(1), 'quarter')),
        (r'\btu dau nam\b|\bnam nay\b', lambda: (pd.Timestamp(t.year, 1, 1), t, 'year_td')),
        (r'\bnam truoc\b', lambda: (pd.Timestamp(t.year - 1, 1, 1), pd.Timestamp(t.year - 1, 12, 31), 'year')),
    ]
    for rx, f in rel:
        for m in re.finditer(rx, n):
            if free(*m.span()):
                s, e, k = f(); add(m.start(), s, e, k, True); used.append(m.span())
    for m in re.finditer(r'(\d+) ngay (?:gan nhat|gan day|qua|vua qua|cuoi)', n):
        if free(*m.span()):
            k = int(m.group(1)); add(m.start(), t - timedelta(k - 1), t, 'ndays'); used.append(m.span())
    out.sort(key=lambda x: x[3])
    return out


def prev_period(p, today, n):
    s, e, kind = p[:3]
    if re.search(r'cung ky nam|so voi nam truoc|cung thang (cua )?nam (truoc|ngoai)', n):
        return (s - pd.DateOffset(years=1), e - pd.DateOffset(years=1))
    if kind == 'month_td':
        ps = (s - timedelta(1)).replace(day=1)
        last = month_end(ps.year, ps.month)
        return ps, min(ps + timedelta(e.day - 1), last)
    if kind in ('month',):
        ps = (s - timedelta(1)).replace(day=1); return ps, month_end(ps.year, ps.month)
    if kind in ('quarter',):
        ps = s - pd.DateOffset(months=3); return ps, s - timedelta(1)
    if kind == 'quarter_td':
        ps = s - pd.DateOffset(months=3); return ps, ps + (e - s)
    if kind in ('week', 'week_td', 'day', 'ndays', 'range'):
        d = (e - s).days + 1; return s - timedelta(d), s - timedelta(1)
    if kind == 'year':
        return s - pd.DateOffset(years=1), e - pd.DateOffset(years=1)
    if kind == 'year_td':
        return s - pd.DateOffset(years=1), e - pd.DateOffset(years=1)
    raise Skip('no prev period')


# ------------------------------------------------------------------ helpers
def r_money(x):
    return int(math.floor(float(x) + 0.5))


def r2(x):
    from decimal import Decimal, ROUND_HALF_UP
    return float(Decimal(repr(round(float(x), 9))).quantize(Decimal('0.01'), ROUND_HALF_UP))
    return float(round(float(x) + 1e-12, 2))


def topk(n, default=1):
    m = re.search(r'\btop (\d+)\b|\b(\d+) (?:hang|khach|nhan vien|ngay|san pham)\b', n)
    return int(m.group(1) or m.group(2)) if m else default


class Ctx:
    def __init__(self, q, data_root):
        self.q = q
        self.n = qnorm(q['question'])
        self.nn = ' ' + norm(q['question']) + ' '
        self.today = pd.Timestamp(q['as_of_date'])
        self.b = load_biz_data(os.path.join(data_root, q['business_id']))
        self.L = self.b.lines
        if self.L is None:
            raise Skip('no sales lines')
        self.dmin = self.L['date'].min()
        self.dmax = self.b.data_end or self.L['date'].max()
        self.periods = parse_periods(self.n, self.today)

    def check_range(self, s, e):
        if e < self.dmin or s > self.dmax:
            raise Unans('Kỳ hỏi nằm ngoài khoảng ngày có dữ liệu của shop')

    def sel(self, s, e, valid=True):
        self.check_range(s, e)
        L = self.L
        m = (L['date'] >= s) & (L['date'] <= min(e, self.today))
        if valid:
            m &= L['valid']
        return L[m]

    # entity filters -----------------------------------------------------
    def match_item(self):
        keys = set(self.L['ikey'].unique()) | set(self.b.aliases)
        best = None
        for k in keys:
            if len(k) >= 3 and (' ' + k + ' ') in self.nn and (best is None or len(k) > len(best)):
                best = k
        if best is None:
            return None
        return self.b.aliases.get(best, best)

    def match_group(self):
        if 'group' not in self.L:
            if re.search(r'\bnhom (?!khach)\w+', self.n):
                raise Unans('Dữ liệu không có cột nhóm hàng')
            return None
        best = None
        for g in self.L['group'].dropna().unique():
            k = norm(g)
            if k and (' ' + k + ' ') in self.nn and (best is None or len(k) > len(norm(best))):
                best = g
        if best is None and re.search(r'\bnhom (?!khach)\w+', self.n):
            raise Skip('group not matched')
        return best

    def match_channel(self):
        if 'channel' not in self.L:
            return None
        for c in self.L['channel'].dropna().unique():
            k = norm(c)
            if k and (' ' + k + ' ') in self.nn:
                return c
        return None

    def match_cgroup(self):
        if 'cgroup' not in self.L or not re.search(r'\bkhach\b', self.n):
            return None
        for v in sorted({norm(x) for x in self.L['cgroup'].dropna().unique()}, key=len, reverse=True):
            if v and re.search(r'\b' + re.escape(v) + r'\b', self.n):
                return v
        return None

    def filt(self, D, item=True):
        g = self.match_group()
        if g is not None:
            D = D[D['group'] == g]
        c = self.match_channel()
        if c is not None:
            D = D[D['channel'] == c]
        if 'ts' in D and D['ts'].notna().any():
            hr = D['ts'].dt.hour
            if re.search(r'ca sang', self.n) and not re.search(r'ca chieu', self.n):
                D = D[(hr >= 6) & (hr < 14)]
            elif re.search(r'ca chieu', self.n) and not re.search(r'ca sang', self.n):
                D = D[(hr >= 14) & (hr < 22)]
        elif re.search(r'ca sang|ca chieu', self.n):
            raise Unans('Dữ liệu không ghi giờ tạo đơn')
        cg = self.match_cgroup()
        if cg is not None:
            D = D[D['cgroup'].map(norm) == cg]
        if 'pay' in D:
            ms = pay_methods(self.n)
            if len(ms) == 1:
                D = D[D['pay'].map(lambda v: pay_of(v) == ms[0])]
        if item:
            it = self.match_item()
            if it is not None:
                D = D[D['ikey'] == it]
        return D


PAY = [('cash', r'tien mat|\btm\b|cash'), ('transfer', r'chuyen khoan|\bck\b|transfer|ngan hang'),
       ('ewallet', r'vi dien tu|\bvi\b|momo|zalopay|ewallet|e wallet'), ('cod', r'\bcod\b|thu ho'),
       ('card', r'\bthe\b|quet the|card|pos'), ('debt', r'ghi no|\bno\b|debt|cong no')]


CHAN = [('phone', r'dien thoai|goi dien|phone'), ('zalo', r'zalo'), ('store', r'tai quay|tai cua hang|tai cho|truc tiep|\bstore\b|offline'),
        ('shopee', r'shopee'), ('grab', r'grab'), ('facebook', r'facebook|\bfb\b|fanpage'), ('tiktok', r'tiktok'), ('website', r'website|\bweb\b')]


def chan_of(v):
    n = norm(v)
    for k, rx in CHAN:
        if re.search(rx, n):
            return k
    return n


def pay_of(v):
    n = norm(v)
    for k, rx in PAY:
        if re.search(rx, n):
            return k
    return n


def pay_methods(n):
    if not re.search(r'tra bang|thanh toan|hinh thuc|phuong thuc|tien mat|chuyen khoan|\bcod\b|vi dien tu|\btm\b|\bck\b', n):
        return []
    found = []
    for k, rx in PAY:
        if k == 'debt':
            continue
        m = re.search(rx, n)
        if m:
            found.append((m.start(), k))
    return [k for _, k in sorted(found)]


def revenue(D):
    return D.loc[D['is_item'] | D['is_fee'], 'amount'].sum()


def items_only(D):
    return D[D['is_item'] & ~D['is_fee']]


def need_period(c, k=1):
    if len(c.periods) < k:
        raise Skip('period not found')
    return c.periods


# ------------------------------------------------------------------ intents
def h_cancel_rate(c):
    if not (re.search(r'\bhuy\b', c.n) and re.search(r'ti le|%', c.n)):
        return None
    s, e, *_ = need_period(c)[0]
    D = c.sel(s, e, valid=False)
    tot = D['oid'].nunique()
    if tot == 0:
        raise Skip('no orders')
    can = D.loc[D['ostatus'] == 'cancel', 'oid'].nunique()
    return 'percent', r2(can / tot * 100)


def h_cancel_count(c):
    if not (re.search(r'\bhuy\b', c.n) and re.search(r'(bao nhieu|may|so) don', c.n)):
        return None
    s, e, *_ = need_period(c)[0]
    D = c.sel(s, e, valid=False)
    return 'number', int(D.loc[D['ostatus'] == 'cancel', 'oid'].nunique())


def metric_fn(c):
    if re.search(r'(so|bao nhieu|may) don', c.n):
        return lambda D: D['oid'].nunique()
    if re.search(r'doanh thu|tien', c.n):
        return revenue
    raise Skip('metric unknown')


def h_growth(c):
    pct = re.search(r'%', c.n) and re.search(r'tang|giam|thay doi|tang truong|chenh|hon hay kem|hon kem', c.n)
    diff = re.search(r'chenh lech|hon bao nhieu|kem bao nhieu|(tang|giam) bao nhieu(?! %)', c.n)
    if not (pct or diff) or re.search(r'ti trong|chiem', c.n):
        return None
    if re.search(r'ca sang|ca chieu', c.n):
        raise Skip('shift compare')
    P = need_period(c)
    f = metric_fn(c)
    E = [p for p in P if not p[4]]
    tgt = E[0] if E else next((p for p in P if p[2].endswith('_td') or p[2] == 'day'), P[0])
    a = tgt[:2]
    b = E[1][:2] if len(E) >= 2 else prev_period(tgt, c.today, c.n)
    va = f(c.filt(c.sel(*a))); vb = f(c.filt(c.sel(*b)))
    if pct:
        if vb == 0:
            raise Skip('zero base')
        return 'percent', r2((va - vb) / vb * 100)
    return 'number', r_money(va - vb)


def h_share(c):
    if not re.search(r'ti trong|chiem (bao nhieu |may )?%|bao nhieu % (doanh thu|tong)|duoc (bao nhieu|may) %', c.n):
        return None
    s, e, *_ = need_period(c)[0]
    D = c.sel(s, e)
    sub = c.filt(D)
    if len(sub) == len(D):
        raise Skip('no filter for share')
    tot = revenue(D)
    return 'percent', r2(revenue(sub) / tot * 100)


def h_aov(c):
    if not re.search(r'trung binh (moi|mot|1) don|gia tri trung binh|binh quan (moi|mot|1) don|trung binh don|(moi|mot|1) don (binh quan|trung binh)', c.n):
        return None
    s, e, *_ = need_period(c)[0]
    D = c.filt(c.sel(s, e), item=False)
    k = D['oid'].nunique()
    if k == 0:
        raise Skip('no orders')
    return 'number', r_money(revenue(D) / k)


def h_size(c):
    m = re.search(r'\bsize (m|l)\b', c.n)
    if not (m and re.search(r'\bly\b', c.n)):
        return None
    s, e, *_ = need_period(c)[0]
    D = items_only(c.sel(s, e))
    D = D[D['ikey'].str.endswith(' ' + m.group(1))]
    return 'number', float(D['qty'].sum())


def h_top_customers(c):
    if not (re.search(r'\bkhach\b', c.n) and re.search(r'chi tieu nhieu nhat|chi nhieu (tien )?nhat|mua nhieu tien nhat', c.n)):
        return None
    s, e, *_ = need_period(c)[0]
    D = c.sel(s, e)
    D = D[D['cust'].notna()]
    g = D.groupby('cust').apply(revenue).reset_index(name='v')
    g['disp'] = g['cust'].map(D.groupby('cust')['cust_disp'].first())
    g = g.sort_values(['v', 'disp'], ascending=[False, True])
    k = topk(c.n)
    names = g['disp'].head(k).tolist()
    if re.search(r'\btop \d+|(?<!/)\b\d{1,2} khach|liet ke|nhung khach', c.n):
        return 'list', names
    return 'string', names[0]


def h_top_items(c):
    if not re.search(r'ban chay|ban (duoc |ra )?nhieu (\w+ )?nhat|hot nhat|chay nhat', c.n) or re.search(r'\bkhach\b|\bngay nao\b|nhan vien|thang nao|tien', c.n):
        return None
    s, e, *_ = need_period(c)[0]
    D = items_only(c.filt(c.sel(s, e), item=False))
    g = D.groupby('item')['bqty'].sum().reset_index()
    g = g.sort_values(['bqty', 'item'], ascending=[False, True])
    if g.empty:
        raise Skip('no items')
    k = topk(c.n)
    if re.search(r'\btop \d+|(?<!/)\b\d{1,2} (hang|san pham)|nhung hang|liet ke', c.n):
        return 'list', g['item'].head(k).tolist()
    return 'string', g['item'].iloc[0]


def h_qty(c):
    if re.search(r'doanh thu|tien|\bdon\b', c.n) or not re.search(r'(bao nhieu|may|so) ', c.n):
        return None
    if re.search(r'\bton\b|trong kho|\bkho\b|con lai|\bcon (bao nhieu|may)\b', c.n):
        if not re.search(r'ton kho|ton cuoi|the kho', norm(c.b.readme)):
            raise Unans('Không có dữ liệu tồn kho')
        raise Skip('stock')
    it = c.match_item()
    s, e, *_ = need_period(c)[0]
    D = items_only(c.filt(c.sel(s, e)))
    units = {norm(u) for u in c.L['bunit'].dropna().unique()}
    m = re.search(r'(?:bao nhieu|may|so) (\w+(?: \w+)?)', c.n)
    asked = None
    if m:
        for cand in (m.group(1), m.group(1).split()[0]):
            if cand in units:
                asked = cand; break
    if it is None:
        if asked is None or not re.search(r'\bban\b', c.n):
            return None
        D = D[D['bunit'].map(norm) == asked]
        return 'number', float(D['bqty'].sum())
    base = norm(c.L.loc[c.L['ikey'] == it, 'bunit'].dropna().iloc[0]) if c.L.loc[c.L['ikey'] == it, 'bunit'].notna().any() else None
    if asked is not None and base is not None and asked != base:
        f = c.b.conv.get(it, {}).get(asked)
        if not f:
            raise Skip('unit mismatch')
        return 'number', r2(D['bqty'].sum() / f)
    if asked is None and not re.search(r'so luong|\bban (duoc|ra)? ?(bao nhieu|may)\b', c.n):
        return None
    return 'number', float(D['bqty'].sum())


def h_orders(c):
    if not re.search(r'(bao nhieu|may|so|tong so) don', c.n) or re.search(r'trung binh|%|ti le', c.n):
        return None
    if re.search(r'\btu \d+|\btren \d+|\bduoi \d+|\bhon \d+|khach', c.n):
        raise Skip('order filter not supported')
    s, e, *_ = need_period(c)[0]
    D = c.filt(c.sel(s, e))
    return 'number', int(D['oid'].nunique())


def h_revenue(c):
    if not re.search(r'doanh thu|bao nhieu tien|tien ban|thu ve|ban duoc bao nhieu$', c.n):
        return None
    if re.search(r'tung thang|tang lien tuc|luon cao|\bgia\b|%|trung binh|binh quan', c.n):
        raise Skip('multi variant')
    cg = c.match_cgroup()
    if re.search(r'trung binh|moi ngay|lai|loi nhuan|gia von|\bno\b|nhap|nhan vien|' + ('' if cg else 'khach|') + 'cao nhat|thap nhat|ngay nao|thang nao', c.n):
        raise Skip('revenue variant not supported')
    s, e, *_ = need_period(c)[0]
    if pay_methods(c.n) and 'pay' not in c.L:
        raise Unans('Dữ liệu không ghi hình thức thanh toán')
    chs = [k for _, k in sorted((m.start(), k) for k, rx in CHAN for m in [re.search(rx, c.n)] if m)]
    if chs and 'channel' not in c.L:
        raise Unans('Dữ liệu không ghi kênh bán')
    if len(chs) >= 2 and 'channel' in c.L:
        s, e, *_ = need_period(c)[0]
        D = c.sel(s, e)
        cv = D['channel'].map(chan_of)
        return 'list', [r_money(revenue(D[cv == k])) for k in chs]
    if len(chs) == 1 and 'channel' in c.L:
        s, e, *_ = need_period(c)[0]
        D = c.sel(s, e)
        return 'number', r_money(revenue(c.filt(D[D['channel'].map(chan_of) == chs[0]], item=False)))
    ms = pay_methods(c.n) if 'pay' in c.L else []
    if len(ms) >= 2:
        D = c.sel(s, e)
        return 'list', [r_money(revenue(c.filt(D[D['pay'].map(lambda v, m=m: pay_of(v) == m)]))) for m in ms]
    D = c.filt(c.sel(s, e))
    return 'number', r_money(revenue(D))


def h_best_day(c):
    if not re.search(r'\bngay nao\b', c.n) or not re.search(r'doanh thu (len )?cao nhat|ban duoc nhieu (tien )?nhat|nhieu don nhat|dat khach nhat|dong khach nhat', c.n):
        return None
    s, e, *_ = need_period(c)[0]
    D = c.filt(c.sel(s, e), item=False)
    if re.search(r'don|dat khach|dong khach', c.n):
        g = D.groupby('date')['oid'].nunique()
    else:
        g = D.groupby('date').apply(revenue)
    g = g.sort_index().sort_values(ascending=False, kind='stable')
    return 'date', g.index[0].strftime('%Y-%m-%d')


def threshold(c):
    nums = [int(x) for x in re.findall(r'\b(\d{4,})\b', c.n) if not (len(x) == 4 and x.startswith('20'))]
    if not nums:
        return None
    strict = bool(re.search(r'(tren|hon|qua|vuot) \d', c.n)) and '≥' not in c.q['question']
    return max(nums), strict


def h_best_month(c):
    if not (re.search(r'\bthang nao\b', c.n) and re.search(r'nhieu tien nhat|cao nhat|ban (duoc )?nhieu nhat|thap nhat|it tien nhat', c.n) and re.search(r'doanh thu|tien|ban', c.n)):
        return None
    P = need_period(c)
    s, e = P[0][0], P[-1][1]
    D = c.filt(c.sel(s, e))
    g = D.groupby(D['date'].dt.to_period('M')).apply(revenue)
    low = re.search(r'thap nhat|it tien nhat', c.n)
    g = g.sort_index()
    k = g.idxmin() if low else g.idxmax()
    return 'date', str(k)


def h_days_threshold(c):
    if not (re.search(r'(bao nhieu|may|so|nhieu) ngay', c.n) and re.search(r'doanh thu|ban duoc', c.n)):
        return None
    t = threshold(c)
    if not t:
        raise Skip('no threshold')
    s, e, *_ = need_period(c)[0]
    D = c.filt(c.sel(s, e))
    g = D.groupby('date').apply(revenue)
    return 'number', int((g > t[0]).sum() if t[1] else (g >= t[0]).sum())


def h_orders_threshold(c):
    if not (re.search(r'(bao nhieu|may|so) don', c.n) and re.search(r'doanh thu|tien hang|gia tri', c.n)):
        return None
    t = threshold(c)
    if not t:
        return None
    s, e, *_ = need_period(c)[0]
    D = c.filt(c.sel(s, e), item=False)
    g = D.groupby('oid').apply(revenue)
    return 'number', int((g > t[0]).sum() if t[1] else (g >= t[0]).sum())


def h_monthly_list(c):
    m = re.search(r'(\d+) thang lien (nhau|tiep) ket thuc (o |vao |tai )?thang', c.n)
    if not (m and re.search(r'doanh thu|tien', c.n)):
        return None
    P = need_period(c)
    end = P[-1][0]
    out = []
    for i in range(int(m.group(1)) - 1, -1, -1):
        ms = end - pd.DateOffset(months=i)
        out.append(r_money(revenue(c.filt(c.sel(ms, month_end(ms.year, ms.month))))))
    return 'list', out


def month_list(c):
    E = [p for p in c.periods if not p[4]]
    m = re.search(r'tu thang .* (den|toi|qua) thang', c.n)
    if len(E) == 2 and m and E[0][2] == E[1][2] == 'month':
        out, ms = [], E[0][0]
        while ms <= E[1][0]:
            out.append(ms); ms = ms + pd.DateOffset(months=1)
        return out
    if len(E) >= 2 and all(p[2] == 'month' for p in E):
        return [p[0] for p in E]
    return None


def h_trend(c):
    if not (re.search(r'doanh thu', c.n) and re.search(r'tang lien tuc|giam lien tuc|luon cao hon|luon thap hon|lan luot|tung thang|moi thang|theo thu tu', c.n)):
        return None
    ms = month_list(c)
    if not ms:
        return None
    v = [revenue(c.filt(c.sel(m, month_end(m.year, m.month)))) for m in ms]
    if re.search(r'tang lien tuc|luon cao hon', c.n):
        return 'boolean', all(b > a for a, b in zip(v, v[1:]))
    if re.search(r'giam lien tuc|luon thap hon', c.n):
        return 'boolean', all(b < a for a, b in zip(v, v[1:]))
    return 'list', [r_money(x) for x in v]


def h_top_cust_orders(c):
    if not (re.search(r'\bkhach\b|\bai\b', c.n) and re.search(r'nhieu don nhat|mua nhieu lan nhat|so don (mua )?nhieu nhat|so lan mua nhieu nhat', c.n)):
        return None
    if 'cust' not in c.L:
        raise Unans('Dữ liệu không ghi khách hàng')
    s, e, *_ = need_period(c)[0]
    D = c.sel(s, e)
    D = D[D['cust'].notna()]
    g = D.groupby('cust')['oid'].nunique().reset_index(name='v')
    g['disp'] = g['cust'].map(D.groupby('cust')['cust_disp'].first())
    g = g.sort_values(['v', 'disp'], ascending=[False, True])
    return 'string', g['disp'].iloc[0]


def h_cust_pct(c):
    m = re.search(r'(it nhat|tu|tren) (\d+) don', c.n)
    if not (m and '%' in c.n and re.search(r'\bkhach\b', c.n)):
        return None
    if 'cust' not in c.L:
        raise Unans('Dữ liệu không ghi khách hàng')
    s, e, *_ = need_period(c)[0]
    D = c.sel(s, e)
    g = D[D['cust'].notna()].groupby('cust')['oid'].nunique()
    k = int(m.group(2))
    hit = (g > k).sum() if m.group(1) == 'tren' else (g >= k).sum()
    return 'percent', r2(hit / len(g) * 100)


def h_cust_count(c):
    m = re.search(r'(bao nhieu|may|so) khach (mua|dat)? ?(it nhat|tu|tren) (\d+) don', c.n) or re.search(r'()khach ()(?:mua |dat )?(it nhat|tu|tren) (\d+) don.*(may|bao nhieu) (nguoi|khach)', c.n)
    if not m or re.search(r'%', c.n):
        return None
    if 'cust' not in c.L:
        raise Unans('Dữ liệu không ghi khách hàng')
    s, e, *_ = need_period(c)[0]
    D = c.sel(s, e)
    D = D[D['cust'].notna()]
    g = D.groupby('cust')['oid'].nunique()
    k = int(m.group(4))
    return 'number', int((g > k).sum() if m.group(3) == 'tren' else (g >= k).sum())


def opt_period(c):
    if c.periods:
        return c.periods[0][:2]
    return c.dmin, c.today


def h_peak_hour(c):
    if not re.search(r'gio cao diem|(may|khung) gio .*(dong|nhieu don|dat khach)|(dong khach|nhieu don|dat khach) nhat (vao |la |luc )?(may|khung) gio', c.n):
        return None
    if 'ts' not in c.L or c.L['ts'].isna().all():
        raise Unans('Dữ liệu không ghi giờ tạo đơn')
    s, e = opt_period(c)
    D = c.sel(s, e)
    g = D.dropna(subset=['ts']).groupby(D['ts'].dt.hour)['oid'].nunique()
    g = g.sort_index().sort_values(ascending=False, kind='stable')
    return 'number', int(g.index[0])


def h_shift_cmp(c):
    if not (re.search(r'ca chieu', c.n) and re.search(r'ca sang', c.n) and re.search(r'%|chenh|hon|kem|tang hay giam', c.n)):
        return None
    if 'ts' not in c.L or c.L['ts'].isna().all():
        raise Unans('Dữ liệu không ghi giờ tạo đơn')
    s, e, *_ = need_period(c)[0]
    D = c.sel(s, e)
    hr = D['ts'].dt.hour
    f = (lambda X: X['oid'].nunique()) if re.search(r'(so|bao nhieu|may) don', c.n) else revenue
    vm, va = f(D[(hr >= 6) & (hr < 14)]), f(D[(hr >= 14) & (hr < 22)])
    if '%' in c.n:
        return 'percent', r2((va - vm) / vm * 100)
    return 'number', r_money(va - vm)


def h_top_items_rev(c):
    if not (re.search(r'\bhang nao\b|\bthuoc nao\b|\bsan pham nao\b|\bmon nao\b', c.n) and re.search(r'nhieu tien nhat|doanh thu (cao|lon) nhat|thu ve nhieu nhat', c.n)):
        return None
    s, e, *_ = need_period(c)[0]
    D = items_only(c.filt(c.sel(s, e), item=False))
    g = D.groupby('item')['amount'].sum().reset_index().sort_values(['amount', 'item'], ascending=[False, True])
    if g.empty:
        raise Skip('no items')
    return 'string', g['item'].iloc[0]


def h_fav_item(c):
    if not re.search(r'ua chuong nhat', c.n):
        return None
    s, e, *_ = need_period(c)[0]
    D = items_only(c.filt(c.sel(s, e), item=False))
    g = D.groupby('item')['oid'].nunique().reset_index().sort_values(['oid', 'item'], ascending=[False, True])
    return 'string', g['item'].iloc[0]


def h_items_in_orders(c):
    m = re.search(r'(bao nhieu|may) hang .*(it nhat|tu) (\d+) don', c.n)
    if not m:
        return None
    s, e, *_ = need_period(c)[0]
    D = items_only(c.sel(s, e))
    g = D.groupby('ikey')['oid'].nunique()
    return 'number', int((g >= int(m.group(3))).sum())


def h_unsold(c):
    if not (re.search(r'\bhang\b', c.n) and re.search(r'khong ban duoc|\be\b|e hang|khong ai mua|khong ban ra', c.n)):
        return None
    s, e, *_ = need_period(c)[0]
    c.check_range(s, e)
    V = items_only(c.L[c.L['valid'] & (c.L['date'] <= c.today)])
    before = set(V.loc[V['date'] < s, 'ikey'])
    during = set(V.loc[(V['date'] >= s) & (V['date'] <= e), 'ikey'])
    res = before - during
    if re.search(r'(bao nhieu|may) hang', c.n):
        return 'number', len(res)
    disp = V.groupby('ikey')['item'].first()
    return 'list', sorted(disp[list(res)].tolist())


def h_cust_rank(c):
    if not re.search(r'\bkhach\b', c.n):
        return None
    kind = 'loyal' if re.search(r'trung thanh nhat', c.n) else 'sop' if re.search(r'\bsop nhat', c.n) else 'cancel' if re.search(r'doi y nhat|huy (don )?nhieu nhat|nhieu don huy nhat', c.n) else None
    if not kind:
        return None
    if 'cust' not in c.L:
        raise Unans('Dữ liệu không ghi khách hàng')
    s, e, *_ = need_period(c)[0]
    D = c.sel(s, e, valid=(kind != 'cancel'))
    D = D[D['cust'].notna()]
    if kind == 'loyal':
        g = D.groupby('cust')['date'].nunique()
    elif kind == 'cancel':
        g = D[D['ostatus'] == 'cancel'].groupby('cust')['oid'].nunique()
    else:
        k = D.groupby('cust')['oid'].nunique()
        r = D.groupby('cust').apply(revenue)
        g = (r / k)[k >= 3]
    if g.empty:
        raise Skip('empty')
    g = g.reset_index(name='v')
    g['disp'] = g['cust'].map(D.groupby('cust')['cust_disp'].first())
    g = g.sort_values(['v', 'disp'], ascending=[False, True])
    return 'string', g['disp'].iloc[0]


HANDLERS = [h_peak_hour, h_shift_cmp, h_top_items_rev, h_fav_item, h_items_in_orders, h_unsold, h_cust_rank, h_trend, h_cust_pct, h_top_cust_orders, h_cust_count, h_monthly_list, h_best_month, h_days_threshold, h_orders_threshold,h_cancel_rate, h_cancel_count, h_growth, h_share, h_aov, h_size, h_top_customers,
            h_best_day, h_top_items, h_orders, h_revenue, h_qty]


def solve(q, data_root):
    c = Ctx(q, data_root)
    for h in HANDLERS:
        r = h(c)
        if r is not None:
            t, a = r
            if isinstance(a, float) and t == 'number' and a.is_integer():
                a = int(a)
            if isinstance(a, (np.integer,)):
                a = int(a)
            return {'id': q['id'], 'type': t, 'answer': a}, h.__name__
    raise Skip('intent not recognised')


def solve_safe(q, data_root):
    try:
        return solve(q, data_root)
    except Unans as ex:
        return {'id': q['id'], 'type': 'unanswerable', 'reason': str(ex)}, 'unans'
    except Skip as ex:
        return {'id': q['id'], 'type': 'abstain'}, 'skip:' + str(ex)
    except Exception as ex:
        return {'id': q['id'], 'type': 'abstain'}, 'error:' + repr(ex)[:120]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--end', type=int, default=None)
    ap.add_argument('--questions', default=os.path.join(ROOT, 'public_test', 'questions.jsonl'))
    ap.add_argument('--data', default=os.path.join(ROOT, 'public_test', 'data'))
    ap.add_argument('--out', default=os.path.join(ROOT, 'submission_public.jsonl'))
    a = ap.parse_args()
    qs = [json.loads(l) for l in open(a.questions, encoding='utf-8') if l.strip()]
    done = set()
    if os.path.exists(a.out):
        for l in open(a.out, encoding='utf-8'):
            try:
                done.add(json.loads(l)['id'])
            except Exception:
                pass
    batch = qs[a.start:a.end]
    with open(a.out, 'a', encoding='utf-8') as fo:
        for i, q in enumerate(batch, a.start):
            if q['id'] in done:
                print(f'[{i}] {q["id"]} skip (resume)')
                continue
            res, why = solve_safe(q, a.data)
            fo.write(json.dumps(res, ensure_ascii=False) + '\n'); fo.flush()
            print(f'[{i}] {q["id"]} {q["business_id"]} | {q["question"]} -> {json.dumps(res, ensure_ascii=False)} ({why})')


if __name__ == '__main__':
    main()
