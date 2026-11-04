s=open('rapor.html',encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    assert s.count(a)==c,(s.count(a),a[:80]); s=s.replace(a,b)
s=s.replace('Yerli şirketler','Yerli şirket ve kurumlar')
rep("<h2>Şirket kayıpları hisse ve tasfiyedeki fonlarda yoğunlaştı</h2>","<h2>Şirket ve kurum kayıpları hisse ve tasfiyedeki fonlarda yoğunlaştı</h2>")
rep('<a href="#tz">Şirketler</a>','<a href="#tz">Şirket ve kurumlar</a>')
anchor='''  <div class="g2">
    <div class="card"><h3>Yerli diğer sınıfı</h3>'''
rep(anchor,'''  <div class="g2">
    <div class="card"><h3>Reel sektör firmalarının tasfiye maruziyeti</h3><p class="cs">TCMB, 15 Eylül 2026, milyar TL</p>
      <div class="scout" id="tc-stat" style="margin-bottom:12px"></div><div class="chart" id="c-tc"></div>
      <p class="note" id="tc-note"></p></div>
    <div class="card"><h3>Bu firmaların ve tedarikçilerinin ekonomideki payı</h3><p class="cs">Yüzde, TCMB firma verileri</p>
      <div class="legend"><span><i class="sw" style="background:var(--tz)"></i>Fon yatırımcısı firmalar</span><span><i class="sw" style="background:var(--dg)"></i>Tedarikçiler</span></div>
      <div class="chart" id="c-tcpay"></div>
      <p class="note">Tedarikçiler, satışlarının %5'inden fazlası fon yatırımcısı firmalara giden firmalar. Fon yatırımının dönen varlıklara oranı %50'yi aşan yüksek maruziyetli firmalar istihdam ve cironun on binde 3'ünü, ticari kredilerin on binde 2'sini oluşturuyor.</p></div>
  </div>
'''+anchor)
TCdef = """// ---------- TCMB reel sektor ----------
const TC = {tutar: 116.2, firma: 4500, pp: 57, rpp: -0.05456, rnpp: -0.84785,
  pay: [['Aktifler', 1.2, null], ['İstihdam', 0.6, 1.2], ['Ciro', 0.9, 1.5], ['İhracat', 1.1, null], ['Ticari krediler', 0.9, null]]};
TC.kayip_pp = TC.pp * TC.rpp; TC.kayip_d = (TC.tutar - TC.pp) * TC.rnpp; TC.kayip = TC.kayip_pp + TC.kayip_d;
"""
rep("// ---------- text ----------", TCdef + "// ---------- text ----------")
drawTC = """function drawTC() {
  $('tc-stat').innerHTML = [['Yatırım', f1.format(TC.tutar), `yaklaşık ${f1.format(TC.firma / 1000)} bin firma`], ['Para piyasası fonlarında', f0.format(TC.pp), `yatırımın ${ek(pa(100 * TC.pp / TC.tutar, f0), 'i')}`], ['Tahmini kayıp', sg(TC.kayip), `yatırımın ${ek(pa(100 * TC.kayip / TC.tutar, f0), 'i')}`]]
    .map(([l, x, d]) => `<div><div class="l">${l}</div><div class="x">${x}</div><div class="d">${d}</div></div>`).join('');
  hbar('c-tc', [
    {l: 'Para piyasası fonları', v: TC.kayip_pp, c: 'var(--tz)', vl: `${sg(TC.kayip_pp, f1)} · ${pc(100 * TC.rpp, f0)}`, tip: `<div class="t">${f0.format(TC.pp)} milyar TL yatırım</div>Tasfiyedeki para piyasası fonlarının ortalama getirisi ${pc(100 * TC.rpp)}<br><b>${sg(TC.kayip_pp, f1)} milyar TL</b>`},
    {l: 'Hisse ve diğer fonlar', v: TC.kayip_d, c: 'var(--tz)', vl: `${sg(TC.kayip_d, f1)} · ${pc(100 * TC.rnpp, f0)}`, tip: `<div class="t">${f1.format(TC.tutar - TC.pp)} milyar TL yatırım</div>Tasfiyedeki diğer fonların ortalama getirisi ${pc(100 * TC.rnpp)}<br><b>${sg(TC.kayip_d, f1)} milyar TL</b>`},
  ], {vw: 110, lab: 150});
  $('tc-note').textContent = `TCMB'nin 116,2 milyar TL'lik reel sektör yatırımına tasfiyedeki fonların 28 Ağustos - 2 Kasım değer ağırlıklı getirisi uygulandı. Reel sektör, hanehalkı dışındaki ${f0.format(B.fon_kurumsal.baz_tasfiye)} milyar TL'lik tasfiye payının ${ek(pa(100 * TC.tutar / B.fon_kurumsal.baz_tasfiye, f0), 'ini')} oluşturuyor, kalanı finansal kurumlar ve fon sepetleri.`;
  const box = $('c-tcpay'); box.replaceChildren();
  const W = width(box), rows = TC.pay, bh = 14, gap = 16, lab = Math.min(120, W * .3), H = rows.length * (2 * bh + gap) + 4;
  const svg = svgOf(box, W, H, 'Ekonomideki pay'); const mx = 1.6, sx = (v) => lab + v / mx * (W - lab - 60);
  el('line', {x1: lab, x2: lab, y1: 0, y2: H, stroke: 'var(--axis)'}, svg);
  const tip = tipFor(box);
  rows.forEach(([l, a, b], i) => { const y = 2 + i * (2 * bh + gap);
    tx(svg, 0, y + bh, l, {'dominant-baseline': 'middle', fill: 'var(--ink)'});
    el('path', {d: rbar(lab, y, sx(a) - lab, bh, 'r'), fill: 'var(--tz)'}, svg); tx(svg, sx(a) + 6, y + bh / 2, '%' + f1.format(a), {'dominant-baseline': 'middle', fill: 'var(--ink)'});
    if (b != null) { el('path', {d: rbar(lab, y + bh + 2, sx(b) - lab, bh, 'r'), fill: 'var(--dg)'}, svg); tx(svg, sx(b) + 6, y + bh * 1.5 + 2, '%' + f1.format(b), {'dominant-baseline': 'middle', fill: 'var(--ink)'}); }
    const hit = el('rect', {x: 0, y: y - 4, width: W, height: 2 * bh + 8, fill: 'transparent'}, svg);
    hit.addEventListener('mousemove', (e) => tip.show(e, `<div class="t">${l}</div>Fon yatırımcısı firmalar %${f1.format(a)}${b != null ? `<br>Tedarikçiler %${f1.format(b)}` : ''}`)); hit.addEventListener('mouseleave', () => tip.hide());
  });
}
"""
rep("// ---------- yabanci ----------", drawTC + "// ---------- yabanci ----------")
rep("drawTZ(); drawYPay();","drawTZ(); drawTC(); drawYPay();")
rep("Para piyasası ve döviz fonları dengeleyici kaldı.`,",
    "Para piyasası ve döviz fonları dengeleyici kaldı.`,\n  `TCMB verisine göre yaklaşık 4.500 reel sektör firmasının tasfiyedeki fonlarda <b>116 milyar lirası</b> var. Fon getirileriyle bu yaklaşık ${f0.format(-TC.kayip)} milyar liralık kayba karşılık geliyor. Bu firmalar istihdamın %0,6'sını oluşturuyor.`,")
rep("<div><h4>Mevduat ve DİBS</h4>","<div><h4>Reel sektör maruziyeti</h4><p>TCMB Blog, Seven ve Gürci, 4 Kasım 2026. SPK'nın 17 Eylül kararıyla tasfiyeye alınan fonlarda 15 Eylül itibarıyla yatırımı olan firmalar. Kayıp tahmini bu rapora ait.</p></div>\n    <div><h4>Mevduat ve DİBS</h4>")
rep("Kaynaklar MKK Veri Analiz Platformu ve Aylık Piyasa Bülteni, TEFAS,","Kaynaklar MKK Veri Analiz Platformu ve Aylık Piyasa Bülteni, TEFAS, TCMB Blog,")
open('rapor.html','w',encoding='utf-8').write(s)
print('ok')
