import pandas as pd, json, numpy as np
V='/tmp/claude-0/-home-user/be8fbbe7-e993-51ff-a967-fb24b7a59b15/scratchpad/vap/'
g=pd.read_excel(V+'vap.xlsx',sheet_name='grafik_12ay')
k=pd.read_excel(V+'vap.xlsx',sheet_name='kimlik_tablosu')
y=pd.read_csv(V+'yan.csv',dtype=str)
u=pd.read_excel('/tmp/claude-0/-home-user/be8fbbe7-e993-51ff-a967-fb24b7a59b15/scratchpad/zip1/EVDS_03-11-2026 (2).xlsx')
u=u[u.Tarih.astype(str).str.match(r'\d\d-\d\d-\d{4}$')]; u.index=pd.to_datetime(u.Tarih,format='%d-%m-%Y')
usd=pd.to_numeric(u.TP_DK_USD_A_YTL,errors='coerce').dropna()
kur={m: float(usd[usd.index<=pd.Timestamp(d)].iloc[-1]) for m,d in [('2026-06','2026-06-30'),('2026-07','2026-07-31'),('2026-08','2026-08-31'),('2026-09','2026-09-30'),('2026-10','2026-10-31')]}
SIN={'PAY SENEDİ':'pay','DEVLET İÇ BORÇLANMA ARAÇLARI':'dibs'}
out={'kur':kur}
# 12 ay: yabanci toplam, genel toplam, yerli toplam
for s,kod in SIN.items():
    G=g[g.kiymet_sinifi==s]
    def ser(kim,uy): 
        x=G[(G.kimlik_filtresi==kim)&(G.uyruk_filtresi==uy)].set_index('ay'); return x
    yb=ser('Tümü','Yabancı'); tt=ser('Tümü','Tümü'); yl=ser('Tümü','Yerli')
    out[kod+'_12ay']=[{'ay':a,'yabanci':round(yb.portfoy_mtl_ham[a]/1e3,2),'toplam':round(tt.portfoy_mtl_ham[a]/1e3,2),'yerli':round(yl.portfoy_mtl_ham[a]/1e3,2),
        'pay':round(100*yb.portfoy_mtl_ham[a]/tt.portfoy_mtl_ham[a],2),'yab_yatirimci':int(yb.yatirimci_sayisi[a])} for a in yb.index]
    # kimlik x uyruk Temmuz-Ekim
    K=k[(k.kiymet_sinifi==s)]
    rows=[]
    for uy in ['Yabancı','Yerli']:
        for kim in ['Gerçek','Tüzel','Diğer']:
            x=K[(K.uyruk_filtresi==uy)&(K.satir==kim)].set_index('ay')
            seri={'2026-07':x.gecen_portfoy_mtl['2026-08']}
            for a in ['2026-08','2026-09','2026-10']: seri[a]=x.cari_portfoy_mtl[a]
            yat={'2026-07':int(x.gecen_yatirimci['2026-08'])}
            for a in ['2026-08','2026-09','2026-10']: yat[a]=int(x.cari_yatirimci[a])
            rows.append({'uyruk':uy,'kimlik':kim,'tl':{a:round(v/1e3,2) for a,v in seri.items()},'usd':{a:round(v/1e3/kur[a],3) for a,v in seri.items()},'yatirimci':yat})
    # sanity: kimlik toplami = Toplam satiri
    for uy in ['Yabancı','Yerli']:
        for a in ['2026-08','2026-09','2026-10']:
            t=K[(K.uyruk_filtresi==uy)&(K.satir=='Toplam')&(K.ay==a)].cari_portfoy_mtl.iloc[0]/1e3
            ssum=sum(r['tl'][a] for r in rows if r['uyruk']==uy)
            assert abs(t-ssum)<0.01, (s,uy,a,t,ssum)
    out[kod+'_kimlik']=rows
# ulke
U=y[(y.sayfa=='pay_senedi_yabanci_ilk10_ulke')&y.satir.notna()]
ul={}
for _,r in U.iterrows():
    ul.setdefault(r.satir,{}).setdefault(r.sutun,[]).append(float(r.deger_ham))
ulke=[]
for n,d in ul.items():
    # KKTC iki kez geciyor (iki ayri kayit) -> topla
    ulke.append({'ulke':n.title() if n!='AMERİKA BİRLEŞİK DEVLETLERİ' else 'ABD','portfoy':round(sum(d['Cari Dönem Portföy Değeri (MTL)'])/1e3,2),'yatirimci':int(sum(d['Cari Dönem Yatırımcı Sayısı']))})
ulke.sort(key=lambda x:-x['portfoy'])
P=y[(y.sayfa=='pay_senedi_yabanci_ilk10_ulke')&y.satir.isna()&y.sutun.str.match(r'2026-10 \| Portföy')]
out['ulke']=ulke; out['ulke_panel_toplam_ekim']=round(float(P.deger_ham.iloc[0])/1e9,2)
json.dump(out,open('yab.json','w'),ensure_ascii=False,indent=0)
# kontrol cikti
for kod in ['pay','dibs']:
    print(kod,[ (r['ay'],r['yabanci'],r['pay']) for r in out[kod+'_12ay']])
    for r in out[kod+'_kimlik']:
        t=r['tl']; print(' ',r['uyruk'],r['kimlik'],t,'eyl %.1f ekim %.1f 2ay %.1f'%(100*(t['2026-09']/t['2026-08']-1),100*(t['2026-10']/t['2026-09']-1),100*(t['2026-10']/t['2026-08']-1)),'usd',r['usd'],r['yatirimci'])
print(kur); print(out['ulke'],out['ulke_panel_toplam_ekim'])
