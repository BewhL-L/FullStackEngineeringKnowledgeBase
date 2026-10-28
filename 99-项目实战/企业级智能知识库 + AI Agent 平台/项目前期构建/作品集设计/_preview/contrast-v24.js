const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const URL_ = 'http://127.0.0.1:8791/issue-v24-camera.html';

const CAND = [
  ['vbri1.0 band.58', 1.00, 0.58],
  ['vbri.95 band.55', 0.95, 0.55],
  ['vbri.90 band.52', 0.90, 0.52],
  ['vbri.80 band.50', 0.80, 0.50],
  
];

function relL(r, g, b) {
  const f = c => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
}
const ratio = (a, b) => (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
const TEXT = { paper: relL(255, 253, 246), p2: relL(239, 233, 218), p3: relL(217, 211, 196) };

(async () => {
  const b = await chromium.launch({ headless: true, channel: 'chrome', args: ['--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1000 }, deviceScaleFactor: 1 });
  await p.goto(URL_, { waitUntil: 'load' });
  await sleep(2600);
  const stops = ['hero', 'retrieval', 'evidence'];

  for (const [name, vbri, band] of CAND) {
    const tag = await p.addStyleTag({ content: `.camfield{--vbri:${vbri}!important;--band:${band}!important}` });
    const rows = [];
    for (const id of stops) {
      await p.evaluate(v => { const el = document.getElementById(v); scrollTo(0, el.getBoundingClientRect().top + scrollY - (v === 'hero' ? 0 : 60)); }, id);
      await sleep(1500);
      await p.evaluate(() => { document.querySelectorAll('main,.nav,.skip').forEach(e => e.style.visibility = 'hidden'); });
      await sleep(240);
      const buf = await p.screenshot();
      await p.evaluate(() => { document.querySelectorAll('main,.nav,.skip').forEach(e => e.style.visibility = ''); });
      const s = await p.evaluate(async (b64) => {
        const img = new Image();
        await new Promise(r => { img.onload = r; img.src = 'data:image/png;base64,' + b64; });
        const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
        const x = c.getContext('2d'); x.drawImage(img, 0, 0);
        const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
        const region = (x0, x1) => {
          const d = x.getImageData(x0, 90, x1 - x0, c.height - 180).data;
          let s = 0, n = 0;
          for (let i = 0; i < d.length; i += 4) { s += 0.2126 * f(d[i]) + 0.7152 * f(d[i + 1]) + 0.0722 * f(d[i + 2]); n++; }
          return s / n;
        };
        return { L: region(320, 900), R: region(920, 1600), G: region(1720, 1915) };
      }, buf.toString('base64'));
      rows.push({ id, ...s });
    }
    console.log('\n===== ' + name + ' =====');
    for (const r of rows) {
      const worst = Math.max(r.L, r.R);
      const cs = Object.keys(TEXT).map(k => k + ' ' + ratio(TEXT[k], worst).toFixed(1)).join(' ');
      console.log('  ' + r.id.padEnd(10),
        '左 L=' + r.L.toFixed(3), '右 L=' + r.R.toFixed(3),
        '| 最差对比度', cs,
        '| 带外视频 L=' + r.G.toFixed(3));
    }
    await tag.evaluate(e => e.remove());
  }
  await b.close();
})();
