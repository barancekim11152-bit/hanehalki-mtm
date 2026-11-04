import pandas as pd, json, re
V='/tmp/claude-0/-home-user/be8fbbe7-e993-51ff-a967-fb24b7a59b15/scratchpad/vap/'
W='/tmp/claude-0/-home-user/be8fbbe7-e993-51ff-a967-fb24b7a59b15/scratchpad/work/'
y=pd.read_csv(V+'yan.csv',dtype=str)
g=pd.read_excel(V+'vap.xlsx',sheet_name='grafik_12ay')
num=lambda s: float(str(s).replace('.','').replace(',','.'))
# 12 ay grup serisi (pay senedi), milyar TL
G=g[g.kiymet_sinifi=='PAY SENEDİ']
def ser(k,u): return G[(G.kimlik_filtresi==k)&(G.uyruk_filtresi==u)].set_index('ay')
yg,yt,yy,yb,tt=ser('Gerçek','Yerli'),ser('Tüzel','Yerli'),ser('Tümü','Yerli'),ser('Tümü','Yabancı'),ser('Tümü','Tümü')
mkk12=[]
for a in tt.index:
    r=dict(ay=a, yerli_gercek=yg.portfoy_mtl_ham[a]/1e3, yerli_tuzel=yt.portfoy_mtl_ham[a]/1e3, yabanci=yb.portfoy_mtl_ham[a]/1e3, toplam=tt.portfoy_mtl_ham[a]/1e3,
           yatirimci_yerli_gercek=int(yg.yatirimci_sayisi[a]), yatirimci_toplam=int(tt.yatirimci_sayisi[a]))
    r['yerli_diger']=yy.portfoy_mtl_ham[a]/1e3-r['yerli_gercek']-r['yerli_tuzel']
    mkk12.append({k:(round(v,2) if isinstance(v,float) else v) for k,v in r.items()})
# portfoy dilimleri (tum yatirimcilar, pay senedi), Eylul vs Ekim
P=y[(y.sayfa=='portfoy_dilimi')&y.satir.notna()&~y.satir.str.match(r'^\d{4} ',na=False)]
cols={'Cari Dönem Portföy Değeri (MTL)':'v1','Geçen Dönem Portföy Değeri (MTL)':'v0','Cari Dönem Yatırımcı Sayısı':'n1','Geçen Dönem Yatırımcı Sayısı':'n0'}
pv=P[P.sutun.isin(cols)].pivot_table(index='satir',columns='sutun',values='deger_formatli',aggfunc='first').rename(columns=cols)
def lo(s): return float(s.split(' - ')[0].replace(' ',''))
pv['lo']=[lo(i) for i in pv.index]; pv=pv.sort_values('lo')
etiket={0:'0-1',2:'2-100',101:'101-1 bin',1001:'1-5 bin',5001:'5-10 bin',10001:'10-20 bin',20001:'20-50 bin',50001:'50-100 bin',100001:'100-250 bin',250001:'250-500 bin',500001:'500 bin-1 milyon',1000001:'1-5 milyon',5000001:'5-10 milyon',10000001:'10 milyon +'}
dilim=[dict(dilim=etiket[int(r.lo)], v0=num(r.v0)/1e3, v1=num(r.v1)/1e3, n0=int(num(r.n0)), n1=int(num(r.n1))) for r in pv.itertuples()]
# iller (yerli, pay senedi, Ekim)
I=y[(y.sayfa=='illere_gore')&y.satir.notna()&(y.sutun=='Portföy Değeri (MTL)')]
iller=[]
for r in I.itertuples():
    n,la,lo_=[p.strip() for p in r.satir.split('|')]
    iller.append(dict(il=n, lat=float(la.replace(',','.')), lon=float(lo_.replace(',','.')), v=round(float(r.deger_ham)/1e3,3)))
yat=y[(y.sayfa=='illere_gore')&y.satir.isna()&y.sutun.str.endswith('| Yatırımcı Sayısı')&~y.sutun.str.match(r'^\d{4}-')]
il_yat={s.split(' |')[0]:int(float(v)) for s,v in zip(yat.sutun,yat.deger_ham)}
for i in iller: i['n']=il_yat.get(i['il'])
il12=y[(y.sayfa=='illere_gore')&y.sutun.str.match(r'^\d{4}-\d\d \| Portföy',na=False)]
il_toplam_ekim=float(il12[il12.sutun.str.startswith('2026-10')].deger_ham.iloc[0])/1e3
ds=json.loads(re.search(r'const DS=(\{.*?\});\n',open('/home/user/hanehalki-mtm/index.html',encoding='utf-8').read(),re.S).group(1))
hh_keys=['ozet','model','seyir','altin_fiyat','altin_ton','fon_kategori','bes_kategori','tasfiye','en_cok_kaybettiren','beta']
pak=dict(b=json.load(open(W+'buyuk.json')), y=json.load(open('yab.json')), h={k:ds[k] for k in hh_keys}, mkk12=mkk12, dilim=dilim, iller=iller, il_toplam_ekim=round(il_toplam_ekim,2))
json.dump(pak,open('paket.json','w'),ensure_ascii=False)
print(len(json.dumps(pak)), 'iller',len(iller), 'il toplam', il_toplam_ekim, 'sum', sum(i['v'] for i in iller))
print(dilim[-3:]); print(mkk12[-1])
