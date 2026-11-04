import pandas as pd, warnings; warnings.filterwarnings('ignore')
Z='/tmp/claude-0/-home-user/be8fbbe7-e993-51ff-a967-fb24b7a59b15/scratchpad/zip1/'
def tf(n):
    df=pd.read_excel(Z+n,header=4)
    df.columns=['kod','ad','tarih','fiyat','pay','kisi','deger']+list(df.columns[7:])
    return df.set_index('kod')
YF0=tf('Fon_Verileri_EXCEL_Tum_Veri_2026-11-03.xlsx'); YF1=tf('Fon_Verileri_EXCEL_Tum_Veri_2026-11-03 (3).xlsx')
BES0=tf('Fon_Verileri_EXCEL_Tum_Veri_2026-11-03 (1).xlsx'); BES1=tf('Fon_Verileri_EXCEL_Tum_Veri_2026-11-03 (4).xlsx')
BYF0=tf('Fon_Verileri_EXCEL_Tum_Veri_2026-11-03 (2).xlsx'); BYF1=tf('Fon_Verileri_EXCEL_Tum_Veri_2026-11-03 (5).xlsx')
