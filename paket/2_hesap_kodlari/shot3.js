const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const [name, vp, scheme] of [['rd', {width: 1200, height: 900}, 'light'], ['rm', {width: 390, height: 844}, 'light'], ['rk', {width: 1200, height: 900}, 'dark']]) {
    const p = await b.newPage({ viewport: vp, colorScheme: scheme }); const errs = [];
    p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    await p.goto('file:///home/user/hanehalki-mtm/buyuk_resim.html'); await p.waitForTimeout(700);
    const t = await p.evaluate(() => ({h: document.getElementById('ozet-h').innerText, k: [...document.querySelectorAll('.kpi')].map(x => x.innerText.replace(/\n/g,' | ')), f: [...document.querySelectorAll('#find li')].map(x=>x.innerText), sc: document.getElementById('sc-out').innerText.replace(/\n/g,' | '), sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth}));
    if (name === 'rd') console.log(JSON.stringify(t, null, 1));
    console.log(name, 'overflow', t.sw > t.cw, 'ERR', errs);
    await p.screenshot({ path: name + '.png', fullPage: true });
    if (name === 'rd') { await p.emulateMedia({media: 'print'}); await p.evaluate(() => window.dispatchEvent(new Event('beforeprint'))); await p.pdf({path: 'rapor.pdf', format: 'A4', printBackground: true}); }
  }
  await b.close();
})();
