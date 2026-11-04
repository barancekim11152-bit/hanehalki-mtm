def part(n):
    n=n.upper(); i=n.find('A.Ş'); return n[i+3:] if i>=0 else n
def besk0(n):
    n=part(n); h=lambda *w: any(x in n for x in w)
    if h('OKS','BAŞLANGIÇ','STANDART'): return 'OKS/Başlangıç/Standart'
    if h('PARA PİYASASI'): return 'Para piyasası'
    if h('ALTIN','KIYMETLİ'): return 'Altın'
    if h('GÜMÜŞ'): return 'Değişken/karma/sepet'
    if h('KİRA'): return 'Borçlanma araçları'
    if h('HİSSE','ENDEKS','BIST','TEMETTÜ'): return 'Hisse senedi'
    if h('DÖVİZ'): return 'Döviz/yabancı'
    if h('KATILIM'): return 'Katılım'
    if h('DIŞ','YABANCI','ABD','S&P'): return 'Döviz/yabancı'
    if h('BORÇLANMA','KAMU','ÖZEL SEKTÖR'): return 'Borçlanma araçları'
    return 'Değişken/karma/sepet'
