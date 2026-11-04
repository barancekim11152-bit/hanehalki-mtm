import runpy, json, numpy as np, pandas as pd, sys, io, contextlib
sys.path.insert(0,'.')
with contextlib.redirect_stdout(io.StringIO()):
    G = runpy.run_path('hesap.py')
bist, r, comp = G['bist'], G['r'], G['comp']
D0, D1, A31, S30, O30 = G['D0'], G['D1'], G['A31'], G['S30'], G['O30']
usd0, usd1, g0, g1 = G['usd0'], G['usd1'], G['g0'], G['g1']
V='/tmp/claude-0/-home-user/be8fbbe7-e993-51ff-a967-fb24b7a59b15/scratchpad/vap/vap.xlsx'
gv = pd.read_excel(V, sheet_name='grafik_12ay')
def mkk(sinif, kim, uy):
    x = gv[(gv.kiymet_sinifi==sinif)&(gv.kimlik_filtresi==kim)&(gv.uyruk_filtresi==uy)].set_index('ay').portfoy_mtl_ham/1e3
    return x
kimlik = pd.read_excel(V, sheet_name='kimlik_tablosu')
def mkk_k(sinif, kim, uy):
    x = kimlik[(kimlik.kiymet_sinifi==sinif)&(kimlik.satir==kim)&(kimlik.uyruk_filtresi==uy)].set_index('ay').cari_portfoy_mtl/1e3
    return x
def solve(target):
    lo, hi = 0.02, 3.0
    for _ in range(100):
        m=(lo+hi)/2
        if comp(m, A31, O30) > target: lo=m
        else: hi=m
    return round((lo+hi)/2, 2)
# --- hisse: grup bazli al-tut (beta, MKK 31 Ag -> 31 Eki kalibrasyonu)
gruplar = [('Yerli','Gerçek'),('Yerli','Tüzel'),('Yerli','Diğer'),('Yabancı','Gerçek'),('Yabancı','Tüzel'),('Yabancı','Diğer')]
hisse = []
for uy, kim in gruplar:
    s = mkk_k('PAY SENEDİ', kim, uy)
    a8, a9, a10 = s['2026-08'], s['2026-09'], s['2026-10']
    t = a10/a8-1; b = solve(t)
    baz = a8/(1+b*r[A31]); mtm = baz*comp(b, D0, D1)
    hisse.append(dict(uyruk=uy, kimlik=kim, ag=round(a8,2), ey=round(a9,2), ek=round(a10,2), mkk_2ay=round(100*t,2), beta=b, baz=round(baz,2), mtm=round(mtm,2),
                      getiri=round(100*mtm/baz,2), usd_baz=round(baz/usd0,2), usd_son=round((baz+mtm)/usd1,2)))
H = {(h['uyruk'],h['kimlik']): h for h in hisse}
# hanehalki sayfasi ile tutarlilik: yerli gercek
assert abs(H[('Yerli','Gerçek')]['mtm'] - [x for x in G['ozet'] if x['kalem']=='hisse'][0]['net']) < 0.05
piyasa = {m: round(mkk('PAY SENEDİ','Tümü','Tümü')[m],2) for m in ['2026-08','2026-09','2026-10']}
# --- fonlar: tum yatirimci ve hanehalki MTM, fark = kurumsal/tuzel
Dg, T, S = G['Dg'], G['T'], G['S']
dg_all = np.where(Dg.r.notna(), Dg.bn*Dg.r, Dg.mtm/Dg.sh)
fon_diger_all = float(np.nansum(dg_all)); fon_diger_hh = float(Dg.mtm.sum())
fon_diger_baz_all = float(Dg.bn.sum())
tas_all = 0.0
for co, ids in S.items():
    t = T.loc[ids]
    if co == 'TERA': tas_all += -261.63   # eski sayfa: karar oncesi +48,9, model -310,53 (tum yatirimci)
    else: tas_all += float((t.bn*np.where(t.r.notna(), t.r, G['r_imp'])).sum())
tas_baz_all = float(T.bn.sum())
tas_hh = sum(x['hanehalki_mtm'] for x in G['tas_rows'])
Dg2 = Dg.copy(); Dg2['all'] = dg_all; Dg2['kur'] = Dg2['all'] - Dg2['mtm']
kur_kat = Dg2.groupby('k').agg(baz=('bn','sum'), hhbaz=('hh','sum'), kur=('kur','sum'), hh=('mtm','sum')).reset_index()
kur_kat = [dict(kategori=x.k, baz=round(x.baz - x.hhbaz,2), mtm=round(x.kur,2)) for x in kur_kat.itertuples()]
fon_kur = dict(kategori=kur_kat, baz_tasfiye=round(tas_baz_all - G['tas_baz'],2), baz=round(fon_diger_baz_all+tas_baz_all - (G['fon_baz']+G['tas_baz']),2),
               mtm=round(fon_diger_all+tas_all - (fon_diger_hh+tas_hh),2),
               tasfiye=round(tas_all-tas_hh,2), diger=round(fon_diger_all-fon_diger_hh,2))
# --- tuzel altin ve doviz
tuzel_altin = dict(ton=round(G['tuzel_ton'],2), baz=round(G['tuzel_ton']*g0/1000,2), mtm=round(G['tuzel_ton']*(g1-g0)/1000,2))
e3 = pd.read_excel('/tmp/claude-0/-home-user/be8fbbe7-e993-51ff-a967-fb24b7a59b15/scratchpad/evds3/e3.xlsx', header=None)
d = e3[e3[0].astype(str).str.match(r'\d\d-\d\d-\d{4}$')].copy(); d.index=pd.to_datetime(d[0],format='%d-%m-%Y'); d=d.drop(columns=0).astype(float)
w = d[(d.index>'2026-08-28')&(d.index<='2026-10-23')]
tuzel_yp_usd = (42021+33379+2277 - w[[8,9,10,19,20,21]].sum().sum())/1e3
gercek_yp_usd = (30993+25772+3237 - w[[3,4,5,14,15,16]].sum().sum())/1e3
tuzel_kur = dict(usd=round(tuzel_yp_usd,2), kazanc=round(tuzel_yp_usd*(usd1-usd0),2))
# --- DIBS pozisyonlari (fiyat + akis, MTM degil)
dibs = []
for uy, kim in gruplar:
    s = mkk_k('DEVLET İÇ BORÇLANMA ARAÇLARI', kim, uy)
    dibs.append(dict(uyruk=uy, kimlik=kim, ag=round(s['2026-08'],2), ek=round(s['2026-10'],2), degisim=round(s['2026-10']-s['2026-08'],2), pct=round(100*(s['2026-10']/s['2026-08']-1),2)))
hh = {x['kalem']: x for x in G['ozet']}
out = dict(hisse=hisse, piyasa=piyasa, fon_kurumsal=fon_kur, tuzel_altin=tuzel_altin, tuzel_kur=tuzel_kur, gercek_kur=round(G['kur_kazanci'],2),
           dibs=dibs, hanehalki=dict(toplam=round(sum(x['net'] for x in G['ozet']),2), hisse=hh['hisse']['net'], altin=round(hh['altin_yastik']['net']+hh['altin_banka']['net'],2),
           fon=round(hh['fon_diger']['net']+hh['fon_tasfiye']['net'],2), bes=hh['bes']['net'], genis_payda=round(G['genis_payda'],2)),
           usd0=round(usd0,4), usd1=round(usd1,4), g0=g0, g1=g1)
json.dump(out, open('buyuk.json','w'), ensure_ascii=False, indent=1)
for h in hisse: print(h)
print('piyasa', piyasa); print('fon kurumsal', fon_kur, 'all', round(fon_diger_all+tas_all,2), 'baz all', round(fon_diger_baz_all+tas_baz_all,2))
print('tuzel altin', tuzel_altin, 'tuzel kur', tuzel_kur, 'gercek yp $', round(gercek_yp_usd,3))
for x in dibs: print(x)
print(out['hanehalki'])
