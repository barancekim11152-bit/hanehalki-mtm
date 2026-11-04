import re
GOLD=re.compile(r'\bALTIN\b|KIYMETLİ|KÜLÇE')
SILV=re.compile(r'\bGÜMÜŞ\b')
def yfk(n, katfirst=True, silver='Fon sepeti'):
    n=n.upper(); h=lambda *w: any(x in n for x in w)
    if 'SERBEST' in n:
        if h('DÖVİZ','DÖVIZ','EUROBOND','DOLAR','AVRO','EURO'): return 'Serbest döviz'
        if GOLD.search(n) or SILV.search(n): return 'Serbest altın'
        if h('HİSSE'): return 'Serbest hisse'
        if h('KISA VADE','PARA PİYASASI','LİKİT'): return 'Serbest kısa vade/PP'
        return 'Serbest diğer'
    if h('PARA PİYASASI'): return 'Para piyasası'
    if h('HİSSE'): return 'Hisse senedi'
    if GOLD.search(n): return 'Altın/kıymetli maden'
    if SILV.search(n): return silver
    if katfirst and h('KATILIM'): return 'Katılım (diğer)'
    if h('FON SEPETİ','FON SEPETI'): return 'Fon sepeti'
    if h('DEĞİŞKEN','DEĞIŞKEN','KARMA','ÇOKLU VARLIK'): return 'Değişken/karma'
    if h('DÖVİZ','EUROBOND','DIŞ BORÇ'): return 'Döviz/Eurobond'
    if h('BORÇLANMA','TAHVİL','BONO','KİRA SERTİFİKA','KISA VADE','LİKİT'): return 'Borçlanma araçları'
    if h('KATILIM'): return 'Katılım (diğer)'
    return 'Diğer'
