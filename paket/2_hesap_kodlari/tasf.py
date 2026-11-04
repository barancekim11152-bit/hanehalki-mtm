import itertools
from load import *
def tasfiye_set():
    T={'TERA':(6,565.06),'PUSULA':(12,375.66),'ATLAS':(16,81.61),'PARDUS':(42,84.1),'HEDEF':(29,111.61),'BULLS':(15,21.18),'A1 CAP':(9,3.32)}
    hayir={'PHE','PBR','TMV','AC2'}
    out={}
    for co,(n,b) in T.items():
        s=YF0[YF0.ad.str.upper().str.startswith(co)].copy()
        s=s[~s.index.isin(hayir)]
        s['r']=(YF1.reindex(s.index).fiyat/s.fiyat).fillna(0); s['bn']=s.deger/1e9
        s=s.sort_values('r')
        best=None
        # candidates: lowest-r funds; search removing up to k from first m
        for m in range(n,min(len(s),n+8)+1):
            c=s.iloc[:m]
            for rem in itertools.combinations(c.index,m-n):
                keep=[i for i in c.index if i not in rem]
                if abs(c.loc[keep,'bn'].sum()-b)<0.006:
                    sc=c.loc[keep,'r'].sum()
                    if best is None or sc<best[0]: best=(sc,keep)
            if best: break
        out[co]=best[1] if best else None
    return out
