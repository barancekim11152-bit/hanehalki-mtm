import json, re, sys
P = '/home/user/hanehalki-mtm/index.html'
s = open(P, encoding='utf-8').read()
ds = json.load(open('ds_new.json'))
beta = [r for r in ds['model'] if r['anahtar'] == 'beta'][0]['deger']
bmin, bmax = ds['beta'][0]['beta'], ds['beta'][-1]['beta']

m = re.search(r'const DS=(\{.*?\});\n', s, re.S)
s = s[:m.start(1)] + json.dumps(ds, ensure_ascii=False) + s[m.end(1):]

R = [
 ('Hanehalkının 28 Ağustos 2026 bazlı borsa', 'Hanehalkının 28 Ağustos 2026 bazlı, 2 Kasım 2026 itibarıyla borsa'),
 ('Baz 28 Ağustos 2026 · Son 23 Ekim 2026 · al-tut değerleme', 'Baz 28 Ağustos 2026 · Son 2 Kasım 2026 · al-tut değerleme'),
 ('<span class="s">23 Ekim kuru ile</span>', '<span class="s">2 Kasım kuru ile</span>'),
 ("Her çubuk 28 Ağustos portföyünün 23 Ekim'e fiyat etkisi.", "Her çubuk 28 Ağustos portföyünün 2 Kasım'a fiyat etkisi."),
 ('Hisse günlük, altın haftalık. Fon ve BES TEFAS gözlem günlerinde, aradaki boşluk kesikli çizgi.',
  'Hisse ve altın günlük. Fon ve BES TEFAS gözlem günlerinde, aradaki boşluk kesikli çizgi.'),
 ('<input id="sl-beta" type="range" min="0.9" max="1.5" step="0.01">', f'<input id="sl-beta" type="range" min="{bmin}" max="{bmax}" step="0.01">'),
 ('Toplam büyüklük ve kayıp tüm yatırımcılar için, son sütun hanehalkına düşen. Karar öncesi gözlenen NAV, karar sonrası değerler model tahmini. Tera fonlarında taban serisindeki grup hisseleri kullanıldı.',
  "Toplam büyüklük ve kayıp tüm yatırımcılar için, son sütun hanehalkına düşen. Gözlenen sütunu 2 Kasım'da fiyat yayımlayan fonların NAV değişimi, tahmin sütunu fiyat yayımı durmuş fonlar. Tera'da 23 Ekim'deki karar öncesi NAV ve grup hisseleri modeli korundu."),
 ('<th class="n" data-field="karar_oncesi">Karar öncesi</th>', '<th class="n" data-field="karar_oncesi">Gözlenen</th>'),
 ('<th class="n" data-field="karar_sonrasi">Karar sonrası</th>', '<th class="n" data-field="karar_sonrasi">Tahmin</th>'),
 ('Tasfiyedeki fonlarda karar sonrası kayıp model tahminidir ve gerçekleşmiş zarar değildir.',
  'Tera fonlarında ve fiyat yayımı durmuş fonlarda kayıp model tahminidir, gerçekleşmiş zarar değildir.'),
 ("Her kalem 28 Ağustos'taki elde tutulan miktarın 23 Ekim fiyatıyla yeniden değerlenmesi.",
  "Her kalem 28 Ağustos'taki elde tutulan miktarın 2 Kasım fiyatıyla yeniden değerlenmesi."),
 ("Bireysel portföyün Eylül'deki düşüşü BIST Tüm ile günlük bileşik betaya kalibre edildi ve aynı beta Ekim'e uygulandı.",
  "Bireysel portföyün 31 Ağustos-31 Ekim arasındaki %35,46'lık düşüşü (MKK Veri Analiz Platformu, yerli gerçek kişi) BIST Tüm ile günlük bileşik betaya kalibre edildi, aynı beta Kasım'ın ilk günlerine uygulandı."),
 ('Kalan stok gram altın farkıyla değerlendi. Bankadaki gerçek kişi altını TCMB haftalık verisinden tona çevrildi.',
  'Kalan stok gram altın farkıyla değerlendi, gram ve ons EVDS BİST serisinden. Bankadaki gerçek kişi altını TCMB haftalık verisinden tona çevrildi. BYF altını TEFAS altın BYF büyüklüğü.'),
 ('TEFAS fiyatı bir önceki günün kapanışını yansıtır.</p>',
  "TEFAS fiyatı bir önceki günün kapanışını yansıtır. 2 Kasım'da fiyatı olmayan fonlarda kategori ortalaması, vadesi dolan döviz fonlarında sıfır, PHE, PBR ve TMV'de 23 Ekim son gözlemi kullanıldı.</p>"),
 ("<p>Karar öncesi son NAV'a kadar gözlenen fiyat. Sonrası için para piyasası tipinde kayıp yok, Tera fonlarında taban serisindeki grup hisseleri, diğerlerinde ödeme yapmamış ve fiyat yayımlayan tasfiye fonlarının ortalaması kullanıldı.</p>",
  "<p>Fiyat yayımlayan tasfiye fonlarında 2 Kasım NAV'ı. Fiyat yayımı durmuş fonlarda fiyat yayımlayan, para piyasası dışı tasfiye fonlarının ortalama getirisi. Tera fonlarında yeni veri olmadığından 23 Ekim'deki taban serisi grup hisseleri modeli korundu.</p>"),
 ('Kaynaklar TCMB EVDS ve Finansal Hesaplar 2026-II, MKK Aylık Piyasa Bülteni, TEFAS ve gram altın fiyat serileridir.',
  'Kaynaklar TCMB EVDS (BİST altın, TCMB kur), TCMB Finansal Hesaplar 2026-II ve haftalık para ve banka istatistikleri, MKK Aylık Piyasa Bülteni (Ağustos, Eylül) ve Veri Analiz Platformu (Ekim), TEFAS (28 Ağustos ve 2 Kasım) ve Bloomberg BIST Tüm (XTUMY) serileridir. Güncelleme 4 Kasım 2026.'),
]
for a, b in R:
    n = s.count(a)
    if n != 1:
        sys.exit(f'BULUNAMADI/ÇOKLU ({n}): {a[:80]}')
    s = s.replace(a, b)
open(P, 'w', encoding='utf-8').write(s)
print('ok', bmin, bmax, beta)
