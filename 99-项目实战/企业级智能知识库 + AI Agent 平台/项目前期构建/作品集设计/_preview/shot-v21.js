const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const b = await chromium.launch({ channel: 'chrome', headless: true });
  const url = 'http://127.0.0.1:8771/issue-v21-plate.html';
  const out = (n) => path.join(__dirname, 'v21-' + n + '.png');

  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  await p.goto(url, { waitUntil: 'networkidle' });
  await p.waitForTimeout(1500);

  await p.screenshot({ path: out('hero') });

  for (const id of ['fullstack', 'agent', 'retrieval', 'case', 'evidence', 'contact']) {
    await p.evaluate(v => {
      const el = document.getElementById(v);
      scrollTo(0, el.getBoundingClientRect().top + scrollY - 70);
    }, id);
    await p.waitForTimeout(750);
    await p.screenshot({ path: out(id) });
  }

  // 证据面板
  await p.evaluate(() => scrollTo(0, document.body.scrollHeight));
  await p.waitForTimeout(600);
  await p.click('[data-evidence="tables"]');
  await p.waitForTimeout(600);
  await p.screenshot({ path: out('dialog') });
  await p.keyboard.press('Escape');
  await p.waitForTimeout(300);

  // 宽屏 & 窄桌面
  for (const [w, h, tag] of [[1920, 1080, 'w1920'], [1280, 800, 'w1280']]) {
    const q = await b.newPage({ viewport: { width: w, height: h } });
    await q.goto(url, { waitUntil: 'networkidle' });
    await q.waitForTimeout(1200);
    await q.screenshot({ path: out(tag) });
    const d = await q.evaluate(() => {
      const r = document.querySelector('.plate').getBoundingClientRect();
      const a = document.querySelector('.hero-actions').getBoundingClientRect();
      return { plate: [Math.round(r.width), Math.round(r.height)], actionsBottom: Math.round(a.bottom), vh: innerHeight };
    });
    console.log(tag, JSON.stringify(d));
    await q.close();
  }

  const m = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  await m.goto(url, { waitUntil: 'networkidle' });
  await m.waitForTimeout(1200);
  await m.screenshot({ path: out('m-hero') });
  const md = await m.evaluate(() => {
    const h1 = document.querySelector('h1').getBoundingClientRect();
    const a = document.querySelector('.hero-actions').getBoundingClientRect();
    return { h1Bottom: Math.round(h1.bottom), actionsBottom: Math.round(a.bottom), vh: innerHeight, overflowX: document.documentElement.scrollWidth > innerWidth };
  });
  console.log('mobile', JSON.stringify(md));
  await m.evaluate(() => { const el = document.getElementById('retrieval'); scrollTo(0, el.getBoundingClientRect().top + scrollY - 60); });
  await m.waitForTimeout(600);
  await m.screenshot({ path: out('m-retrieval') });

  console.log('errors:', errs.length, errs.slice(0, 3).join(' | '));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
