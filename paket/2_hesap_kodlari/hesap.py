"""Hanehalki MTM guncellemesi: baz 28 Agustos 2026, son 2 Kasim 2026.
Girdiler: kullanicinin yukledigi zip (BIST TUM, EVDS altin/kur, TEFAS YF/BES/BYF, MKK, TCMB haftalik).
Cikti: ds_new.json (sayfadaki DS nesnesinin yeni hali) + kontrol.txt
"""
import sys, json, re, warnings
import numpy as np, pandas as pd
warnings.filterwarnings('ignore')
sys.path.insert(0, '.')
from load import YF0, YF1, BES0, BES1, BYF0, Z
from yfclass import yfk, GOLD
from besclass import besk0

OLD = json.loads(re.search(r'const DS=(\{.*?\});\n', open('/home/user/hanehalki-mtm/index.html', encoding='utf-8').read(), re.S).group(1))
OM = {r['anahtar']: r['deger'] for r in OLD['model']}
OZ = {r['kalem']: r for r in OLD['ozet']}
D0, D1 = pd.Timestamp('2026-08-28'), pd.Timestamp('2026-11-02')
log = []
def L(*a):
    s = ' '.join(str(x) for x in a); log.append(s); print(s)

# ---------------- fiyat serileri ----------------
b = pd.read_excel(Z + 'BIST TUM.xlsx', header=None, skiprows=7).iloc[:, :2].dropna()
bist = pd.Series(b[1].astype(float).values, index=pd.to_datetime(b[0])).sort_index()
bist = bist[(bist.index >= D0) & (bist.index <= D1)]

g = pd.read_excel(Z + 'EVDS_03-11-2026.xlsx')
g = g[g.Tarih.astype(str).str.match(r'\d\d-\d\d-\d{4}$')]
g.index = pd.to_datetime(g.Tarih, format='%d-%m-%Y')
gram = (pd.to_numeric(g.TP_ALTINPIYASA_KAP02, errors='coerce') / 1000).dropna()
ons = pd.to_numeric(g.TP_ALTINPIYASA_KAP03, errors='coerce').dropna()
u = pd.read_excel(Z + 'EVDS_03-11-2026 (2).xlsx')
u = u[u.Tarih.astype(str).str.match(r'\d\d-\d\d-\d{4}$')]
u.index = pd.to_datetime(u.Tarih, format='%d-%m-%Y')
usd = pd.to_numeric(u.TP_DK_USD_A_YTL, errors='coerce').dropna()
gram, ons, usd = [s[(s.index >= D0) & (s.index <= D1)] for s in (gram, ons, usd)]
g0, g1 = gram[D0], gram[D1]
o0, o1 = ons[D0], ons[D1]
usd0, usd1 = usd[D0], usd[D1]
L('gram', g0, g1, 'ons', o0, o1, 'usd', usd0, usd1, 'bist', bist[D0], bist[D1])

# ---------------- HISSE ----------------
r = bist.pct_change().dropna()
A31, S30, O30 = pd.Timestamp('2026-08-31'), pd.Timestamp('2026-09-30'), pd.Timestamp('2026-10-30')
# MKK Veri Analiz Platformu: pay senedi, gercek kisi, yerli (milyon TL) ay sonu
_v = pd.read_excel('/tmp/claude-0/-home-user/be8fbbe7-e993-51ff-a967-fb24b7a59b15/scratchpad/vap/vap.xlsx', sheet_name='grafik_12ay')
_v = _v[(_v.kiymet_sinifi == 'PAY SENEDİ') & (_v.kimlik_filtresi == 'Gerçek') & (_v.uyruk_filtresi == 'Yerli')].set_index('ay').portfoy_mtl_ham
MKK8, MKK9, MKK10 = _v['2026-08'] / 1e3, _v['2026-09'] / 1e3, _v['2026-10'] / 1e3
MKK_HEDEF = MKK10 / MKK8 - 1   # 31 Agustos -> 31 Ekim (son islem gunu 30 Ekim)
L('MKK yerli gercek pay', MKK8, MKK9, MKK10, 'eylul', MKK9 / MKK8 - 1, 'ekim', MKK10 / MKK9 - 1, '2 ay', MKK_HEDEF)
def comp(beta, a, z):
    rr = r[(r.index > a) & (r.index <= z)]
    return float(np.prod(1 + beta * rr.values) - 1)
lo, hi = 0.1, 3.0
for _ in range(100):
    mid = (lo + hi) / 2
    if comp(mid, A31, O30) > MKK_HEDEF: lo = mid
    else: hi = mid
beta_kal = (lo + hi) / 2
beta = round(beta_kal, 2)   # kaydirici 0,01 adimli; senaryo bazi ile birebir ayni olsun
L('beta kalibre', beta_kal)
L('beta', beta, 'eylul', comp(beta, A31, S30), 'ekim', comp(beta, S30, O30), '2ay', comp(beta, A31, O30), 'bist eylul', bist[S30] / bist[A31] - 1, 'bist ekim', bist[O30] / bist[S30] - 1)
# MKK Agustos sonu (31 Ag) bireysel portfoy: eski sayfadaki baz ile eski seri/beta uzerinden geri bulunur
old_x = {r_['tarih']: r_['xutum'] for r_ in OLD['seyir']}
V31_eski = OM['hisse_baz'] * (1 + OM['beta'] * (old_x['2026-08-31'] / old_x['2026-08-28'] - 1))
V31 = MKK8
L('V31 eski turetilmis', V31_eski, 'MKK VAP', V31)
hisse_baz = V31 / (1 + beta * r[A31])
L('V31', V31, 'hisse_baz', hisse_baz)
hisse_cum = {d: hisse_baz * comp(beta, D0, d) for d in bist.index}
hisse_net = hisse_cum[D1]
beta_tab = []
for bb in np.round(np.arange(max(0.3, round(beta - 0.35, 2)), round(beta + 0.36, 2), 0.01), 2):
    beta_tab.append({'beta': float(bb), 'getiri': round(comp(bb, D0, D1), 5)})

# ---------------- ALTIN ----------------
erkin_ton = 4305.0                               # Agustos 2026 yurt ici toplam altin stoku (yastik alti dahil), aylik -8 ton
tuzel_usd = 8.931034e9                             # TCMB: 23 Ekim stok eksi haftalik akis+parite (EVDS TP.HPBITABLO5) -> 28 Ag tuzel KMDH $
tuzel_ton = tuzel_usd / (o0 / 31.1035) / 1e6
bes_altin_bn = BES0[BES0.ad.map(besk0) == 'Altın'].deger.sum() / 1e9
bes_ton = bes_altin_bn * 1e9 / g0 / 1e6
YFg = YF0[YF0.ad.str.upper().map(lambda n: bool(GOLD.search(n)))]
fon_altin_bn = YFg.deger.sum() / 1e9
fon_ton = fon_altin_bn * 1e9 / g0 / 1e6
BYFg = BYF0[BYF0.ad.str.upper().map(lambda n: bool(GOLD.search(n)))]
byf_bn = BYFg.deger.sum() / 1e9
byf_ton = byf_bn * 1e9 / g0 / 1e6
banka_usd = 89.591038                              # TCMB: 23 Ekim stok eksi haftalik akis+parite -> 28 Ag gercek kisi KMDH, milyar $
banka_ton = banka_usd * 1e9 / (o0 / 31.1035) / 1e6
hh_ton = erkin_ton - tuzel_ton - bes_ton - fon_ton - byf_ton
yastik_ton = hh_ton - banka_ton
L('ton: tuzel', tuzel_ton, 'bes', bes_ton, f'({bes_altin_bn:.2f} bn)', 'fon', fon_ton, f'({fon_altin_bn:.2f} bn, {len(YFg)} fon)', 'byf', byf_ton, f'({byf_bn:.2f} bn)', 'banka', banka_ton, 'hh', hh_ton, 'yastik', yastik_ton)
yastik_baz = yastik_ton * g0 / 1000
banka_baz = banka_ton * g0 / 1000
yastik_net = yastik_ton * (g1 - g0) / 1000
banka_net = banka_ton * (g1 - g0) / 1000

# ---------------- YATIRIM FONLARI ----------------
Y = YF0.copy()
Y['avg'] = Y.deger / Y.kisi.clip(lower=1); Y['bn'] = Y.deger / 1e9
a_ = Y.avg.values; b_ = Y.bn.values
s_ = np.where(a_ <= 2e5, .9, np.where(a_ <= 1e6, .85, np.where(a_ <= 5e6, .75, np.where(a_ <= 2.8e7, .5, np.nan))))
m_ = np.isnan(s_)
HH_TOPLAM = OZ['fon_tasfiye']['baz'] + OZ['fon_diger']['baz']   # 5.911,26: MKK yerli gercek kisi fon portfoyune esitlenmis toplam (degismedi)
cc = (HH_TOPLAM - np.nansum(s_ * b_)) / b_[m_].sum()
Y['sh'] = np.where(m_, cc, s_); Y['hh'] = Y.sh * Y.bn
L('hh pay c', cc)
Y['p1'] = YF1.reindex(Y.index).fiyat
Y['r'] = Y.p1 / Y.fiyat - 1
Y.loc[Y.p1.isna() | (Y.p1 <= 0), 'r'] = np.nan     # fiyatsiz (durdurulmus / kapanmis)
S = json.load(open('tasfiye.json'))
co_of = {i: co for co, v in S.items() for i in v}
Y['tasfiye'] = Y.index.map(lambda i: i in co_of)
Y['k'] = Y.ad.map(lambda n: yfk(n, False, 'Fon sepeti'))

# Tasfiye: fiyat yayimlayanlarda gozlenen NAV; fiyatsizlarda (Tera haric) fiyat yayimlayan, PP olmayan tasfiye fonlarinin
# deger agirlikli ortalama getirisi (eski sayfanin yontemi); Tera: eski sayfanin model tahmini korunur (yeni veri yok).
T = Y[Y.tasfiye].copy()
T['pp'] = T.ad.str.upper().str.contains('PARA PİYASASI')
obs = T[T.r.notna() & ~T.pp & ~T.index.isin(S['TERA'])]
r_imp = float((obs.bn * obs.r).sum() / obs.bn.sum())
L('tasfiye imput getiri (fiyat yayimlayan, PP haric)', r_imp, 'n', len(obs))
old_tas = {r_['portfoy']: r_ for r_ in OLD['tasfiye']}
names = {'TERA': 'Tera', 'PUSULA': 'Pusula', 'ATLAS': 'Atlas', 'PARDUS': 'Pardus', 'HEDEF': 'Hedef', 'BULLS': 'Bulls', 'A1 CAP': 'A1 Capital'}
tas_rows = []; T['mtm_all'] = np.nan; T['mtm_hh'] = np.nan; T['kaynak'] = ''
for co, ids in S.items():
    t = T.loc[ids]
    if co == 'TERA':
        o = old_tas['Tera']
        tas_rows.append({'portfoy': 'Tera', 'fon_sayisi': len(ids), 'toplam_buyukluk': round(t.bn.sum(), 2), 'hanehalki_payi': round(t.hh.sum(), 2),
                         'karar_oncesi': o['karar_oncesi'], 'karar_sonrasi': o['karar_sonrasi'], 'hanehalki_mtm': o['hanehalki_mtm']})
        continue
    ob = t[t.r.notna()]; im = t[t.r.isna()]
    mo = float((ob.bn * ob.r).sum()); mi = float((im.bn * r_imp).sum())
    hh = float((ob.hh * ob.r).sum() + (im.hh * r_imp).sum())
    T.loc[ob.index, 'mtm_hh'] = ob.hh * ob.r; T.loc[im.index, 'mtm_hh'] = im.hh * r_imp
    tas_rows.append({'portfoy': names[co], 'fon_sayisi': len(ids), 'toplam_buyukluk': round(t.bn.sum(), 2), 'hanehalki_payi': round(t.hh.sum(), 2),
                     'karar_oncesi': round(mo, 2), 'karar_sonrasi': round(mi, 2), 'hanehalki_mtm': round(hh, 2)})
tas_rows.sort(key=lambda x: x['hanehalki_mtm'])
tas_baz = sum(x['hanehalki_payi'] for x in tas_rows)
tas_net = sum(x['hanehalki_mtm'] for x in tas_rows)
L('tasfiye', len(T), 'baz', tas_baz, 'net', tas_net)

# Diger fonlar
Dg = Y[~Y.tasfiye & (Y.kisi > 0)].copy()
old_last = {'PHE': -23.92, 'PBR': -5.25, 'TMV': -16.22}   # 23 Ekim'de gozlenen, sonra fiyat yayimi durdu
Dg['mtm'] = Dg.hh * Dg.r
Dg['kaynak'] = np.where(Dg.r.notna(), 'TEFAS 2 Kasım', '')
for k_, v_ in old_last.items():
    Dg.loc[k_, 'mtm'] = v_; Dg.loc[k_, 'kaynak'] = '23 Ekim son gözlem'
miss = Dg.mtm.isna()
cat_r = (Dg[~miss & Dg.r.notna()].groupby('k').apply(lambda x: (x.hh * x.r).sum() / x.hh.sum()))
mat = miss & Dg.ad.str.upper().str.contains(r'DÖVİZ|DÖVIZ') & Dg.ad.str.upper().str.contains(r'20\d\d')
Dg.loc[mat, 'mtm'] = 0.0; Dg.loc[mat, 'kaynak'] = 'vadesi doldu, 0'
rest = Dg.mtm.isna()
Dg.loc[rest, 'mtm'] = Dg.loc[rest, 'hh'] * Dg.loc[rest, 'k'].map(cat_r)
Dg.loc[rest, 'kaynak'] = 'fiyatsız, kategori ortalaması'
L('diger fon: fiyatsiz', int(miss.sum()), 'vadesi dolan', int(mat.sum()), 'kategori ort', int(rest.sum()), 'hh', round(Dg.loc[miss, 'hh'].sum(), 2))
fon_baz = Dg.hh.sum(); fon_net = Dg.mtm.sum(); fon_brut = Dg.mtm.clip(upper=0).sum()
L('fon diger baz', fon_baz, 'net', fon_net, 'brut', fon_brut)
kat = Dg.groupby('k').agg(baz=('hh', 'sum'), mtm=('mtm', 'sum'), fon_sayisi=('hh', 'size')).reset_index()
fon_kategori = [{'kategori': x.k, 'baz': round(x.baz, 2), 'mtm': round(x.mtm, 2), 'fon_sayisi': int(x.fon_sayisi), 'getiri': round(100 * x.mtm / x.baz, 2)}
                for x in kat.sort_values('mtm').itertuples()]

# En cok kaybettiren (fon bazinda hanehalki MTM)
tera_known = {'TLY': -146.0, 'THF': -43.84, 'DOH': -7.28}   # eski sayfa Tera model tahmini
rows = []
for i, x in Dg.iterrows(): rows.append((i, x.ad, x.k, 'Hayır', x.hh, x.mtm))
for i, x in T.iterrows():
    v = tera_known.get(i) if i in S['TERA'] else x.mtm_hh
    if v is None or pd.isna(v): continue
    rows.append((i, x.ad, x.k, 'Evet', x.hh, v))
rows.sort(key=lambda z: z[5])
def tc(s):
    keep = {'(TL)', 'BIST', 'BYF', '(DÖVİZ)', 'PP', 'ÖPY', 'TL', 'ABD'}
    def low(w): return w.replace('I', 'ı').replace('İ', 'i').lower()
    out = []
    for w in s.split():
        if w in keep: out.append(w); continue
        pre = '(' if w.startswith('(') else ''
        core = w[1:] if pre else w
        out.append(pre + core[:1] + low(core[1:]))
    return ' '.join(out)
en_cok = [{'kod': i, 'fon': tc(ad), 'kategori': k, 'tasfiye': t_, 'hanehalki_baz': round(h, 2), 'hanehalki_mtm': round(m, 2)}
          for i, ad, k, t_, h, m in rows[:12]]

# ---------------- BES ----------------
B = BES0.copy(); B['p1'] = BES1.reindex(B.index).fiyat; B['bn'] = B.deger / 1e9
B['mtm'] = B.bn * (B.p1 / B.fiyat - 1); B['k'] = B.ad.map(besk0)
assert B.p1.notna().all() and (B.p1 > 0).all()
bes_baz, bes_net, bes_brut = B.bn.sum(), B.mtm.sum(), B.mtm.clip(upper=0).sum()
L('BES baz', bes_baz, 'net', bes_net, 'brut', bes_brut)
bk = B.groupby('k').agg(baz=('bn', 'sum'), mtm=('mtm', 'sum'), fon_sayisi=('bn', 'size')).reset_index()
bes_kategori = [{'kategori': x.k, 'baz': round(x.baz, 2), 'mtm': round(x.mtm, 2), 'fon_sayisi': int(x.fon_sayisi), 'getiri': round(100 * x.mtm / x.baz, 2)}
                for x in bk.sort_values('mtm').itertuples()]

# ---------------- PAYDA ----------------
payda = [dict(r_) for r_ in OLD['payda']]
d_banka = banka_baz - OZ['altin_banka']['baz']
d_hisse = hisse_baz - OM['hisse_baz']
for p in payda:
    if p['kalem'].startswith('Para ve mevduat'): p['agustos'] = round(p['agustos'] + d_banka, 2)
    if p['kalem'].startswith('Hisse senedi'): p['agustos'] = round(p['agustos'] + d_hisse, 2)
    if p['kalem'] == 'Yastık altı altın': p['agustos'] = round(yastik_baz, 2)
fin_payda = sum(p['agustos'] for p in payda if p['tur'] == 'Finansal')
genis_payda = fin_payda + yastik_baz
dov_usd = 59.264599   # TCMB: 28 Ag gercek kisi doviz mevduati (USD+EUR+diger), milyar $
kur_kazanci = dov_usd * (usd1 - usd0)

# ---------------- OZET / MODEL ----------------
bdate = '2 Kasım'
ozet = [
    {'kalem': 'hisse', 'ad': 'Doğrudan hisse senedi', 'grup': 'Borsa', 'baz': round(hisse_baz, 2), 'net': round(hisse_net, 2), 'brut': round(hisse_net, 2),
     'yontem': f'MKK yerli gerçek kişi portföyü, BIST Tüm ile beta {beta:.2f}'.replace('.', ',') + f' (Eylül-Ekim kalibrasyonu), {bdate} kapanış'},
    {'kalem': 'altin_yastik', 'ad': 'Yastık altı altın', 'grup': 'Altın', 'baz': round(yastik_baz, 2), 'net': round(yastik_net, 2), 'brut': round(yastik_net, 2),
     'yontem': 'Erkin Işık stoku eksi banka, fon, BES, BYF ve tüzel altını, gram altın farkı'},
    {'kalem': 'altin_banka', 'ad': 'Bankadaki altın (gerçek kişi)', 'grup': 'Altın', 'baz': round(banka_baz, 2), 'net': round(banka_net, 2), 'brut': round(banka_net, 2),
     'yontem': 'TCMB gerçek kişi kıymetli maden hesabı, ton bazında gram fiyat farkı'},
    {'kalem': 'fon_tasfiye', 'ad': f'Tasfiyedeki {len(T)} fon', 'grup': 'Yatırım fonu', 'baz': round(tas_baz, 2), 'net': round(tas_net, 2), 'brut': round(tas_net, 2),
     'yontem': 'Fiyat yayımlayanlarda 2 Kasım NAV, fiyatsızlarda tasfiye ortalaması, Tera model tahmini, hanehalkı payı'},
    {'kalem': 'fon_diger', 'ad': 'Diğer yatırım fonları', 'grup': 'Yatırım fonu', 'baz': round(fon_baz, 2), 'net': round(fon_net, 2), 'brut': round(fon_brut, 2),
     'yontem': 'TEFAS fon bazında al-tut, 28 Ağustos pay adedi, hanehalkı payı'},
    {'kalem': 'bes', 'ad': 'BES ve OKS fonları', 'grup': 'BES', 'baz': round(bes_baz, 2), 'net': round(bes_net, 2), 'brut': round(bes_brut, 2),
     'yontem': 'TEFAS emeklilik fonları al-tut, tamamı hanehalkı'},
]
model = [
    ('usd0', usd0), ('usd1', usd1), ('gram0', g0), ('gram1', g1), ('hh_altin_ton', hh_ton), ('erkin_ton', erkin_ton),
    ('altin_kesinti_ton', erkin_ton - hh_ton), ('banka_ton', banka_ton), ('hisse_baz', hisse_baz), ('beta', beta),
    ('fin_payda', fin_payda), ('genis_payda', genis_payda), ('yastik_deger', yastik_baz), ('q2_toplam', OM['q2_toplam']),
    ('doviz_kur_kazanci', kur_kazanci), ('doviz_mevduat_usd', dov_usd), ('xutum0', bist[D0]), ('xutum1', bist[D1]),
]
model = [{'anahtar': k, 'deger': round(float(v), 4 if k == 'beta' else 2)} for k, v in model]

altin_ton = [
    {'kalem': 'Yurt içi toplam altın stoku (Ağustos)', 'ton': round(erkin_ton, 2), 'not': "Ağustos 2026, aylık 8 ton düşüş, Kasım 2021'den beri en sert"},
    {'kalem': 'Eksi tüzel kişi banka altını', 'ton': -round(tuzel_ton, 2), 'not': 'TCMB tüzel kişi KMDH 8,93 milyar $, 28 Ağustos ons fiyatıyla'},
    {'kalem': 'Eksi BES altın fonları', 'ton': -round(bes_ton, 2), 'not': 'BES altın fonları büyüklüğü / gram altın'},
    {'kalem': 'Eksi yatırım fonu altını', 'ton': -round(fon_ton, 2), 'not': 'Altın ve kıymetli maden fonları / gram altın'},
    {'kalem': 'Eksi altın BYF', 'ton': -round(byf_ton, 2), 'not': 'TEFAS altın BYF büyüklüğü / gram altın'},
    {'kalem': 'Hanehalkının doğrudan altını', 'ton': round(hh_ton, 2), 'not': 'Fiyat etkisine tabi doğrudan stok'},
    {'kalem': '… bankada (gerçek kişi)', 'ton': round(banka_ton, 2), 'not': 'TCMB haftalık, 28 Ağustos 89,59 milyar $'},
    {'kalem': '… yastık altında', 'ton': round(yastik_ton, 2), 'not': 'Kalan'},
]

# altin fiyat tablosu: 28 Ag, her cuma, 30 Ekim, 2 Kasim
fd = [d for d in gram.index if d == D0 or d.weekday() == 4 or d == D1]
altin_fiyat = [{'tarih': d.strftime('%Y-%m-%d'), 'ons_usd': round(float(ons[d]), 2), 'gram_tl': round(float(gram[d]), 2),
                'usdtry': round(float(usd.get(d, np.nan)), 2), 'kaynak': 'EVDS: BİST altın, TCMB kur'} for d in fd]

# seyir: gunluk hisse + altin (EVDS olan gunler), fon/bes TEFAS gozlem gunleri (eski Eylul/Ekim gozlemleri korunur)
old_fb = {r_['tarih']: (r_['fon'], r_['bes']) for r_ in OLD['seyir'] if r_['fon'] is not None}
seyir = []
for d in bist.index:
    k = d.strftime('%Y-%m-%d')
    al = (yastik_ton + banka_ton) * (gram[d] - g0) / 1000 if d in gram.index else None
    fo, be = old_fb.get(k, (None, None))
    if d == D1: fo, be = round(fon_net + tas_net, 2), round(bes_net, 2)
    seyir.append({'tarih': k, 'hisse': round(hisse_cum[d], 2), 'altin': None if al is None else round(al, 2), 'fon': fo, 'bes': be,
                  'xutum': round(float(bist[d]), 2), 'gram': None if d not in gram.index else round(float(gram[d]), 2)})

DS = dict(OLD)
DS.update({'fon_kategori': fon_kategori, 'seyir': seyir, 'altin_fiyat': altin_fiyat, 'model': model, 'beta': beta_tab, 'ozet': ozet,
           'bes_kategori': bes_kategori, 'en_cok_kaybettiren': en_cok, 'tasfiye': tas_rows, 'payda': payda, 'altin_ton': altin_ton})
json.dump(DS, open('ds_new.json', 'w'), ensure_ascii=False)
tot = sum(x['net'] for x in ozet); totb = sum(x['brut'] for x in ozet)
L('TOPLAM net', tot, 'brut', totb, 'genis', genis_payda, 'oran', tot / genis_payda, 'fin oran', (tot - yastik_net) / fin_payda, 'usd', tot / usd1)
L('ESKI toplam', sum(x['net'] for x in OLD['ozet']))
open('kontrol.txt', 'w').write('\n'.join(log))
Dg[Dg.kaynak != 'TEFAS 2 Kasım'][['ad', 'k', 'hh', 'mtm', 'kaynak']].to_csv('fiyatsiz_fonlar.csv')
