import numpy as np, json
from load import *
def hh_frame():
    Y=YF0.copy(); Y['avg']=Y.deger/Y.kisi.clip(lower=1); Y['bn']=Y.deger/1e9
    a=Y.avg.values;b=Y.bn.values
    s=np.where(a<=2e5,.9,np.where(a<=1e6,.85,np.where(a<=5e6,.75,np.where(a<=2.8e7,.5,np.nan))))
    m=np.isnan(s); c=(5911.26-np.nansum(s*b))/b[m].sum(); Y['sh']=np.where(m,c,s); Y['hh']=Y.sh*Y.bn
    return Y,c
