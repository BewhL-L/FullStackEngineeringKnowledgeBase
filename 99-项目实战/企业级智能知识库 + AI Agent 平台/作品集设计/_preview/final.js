const { chromium } = require('playwright');
const path = require('path'); const { pathToFileURL } = require('url');
const u = pathToFileURL(path.join(__dirname, '..', 'issue.html')).href;
(async () => {
  const b = await chromium.launch({ channel: 'chrome', headless: true });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  await p.goto(u); await p.waitForTimeout(2600);
  const ids = ['hero','fullstack','agent','retrieval','case','evidence','contact'];
  for (const id of ids) {
    await p.evaluate(v => { const el = document.getElementById(v); scrollTo(0, el.getBoundingClientRect().top + scrollY - (v==='hero'?0:80)); }, id);
    await p.waitForTimeout(950);
    await p.screenshot({ path: path.join(__dirname, 'f-' + id + '.png') });
  }
  const info = await p.evaluate(() => {
    const sizes = {}, colors = {};
    [...document.querySelectorAll('body *')].filter(el => [...el.childNodes].some(n => n.nodeType===3 && n.textContent.trim().length>1)).forEach(el => {
      const cs = getComputedStyle(el);
      sizes[cs.fontSize] = (sizes[cs.fontSize]||0)+1;
      colors[cs.color] = (colors[cs.color]||0)+1;
    });
    return { height: document.documentElement.scrollHeight, sizes, colors };
  });
  console.log(JSON.stringify(info));
  const m = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true });
  await m.goto(u); await m.waitForTimeout(2200);
  await m.screenshot({ path: path.join(__dirname, 'f-m-hero.png') });
  await m.evaluate(() => { const el = document.getElementById('fullstack'); scrollTo(0, el.getBoundingClientRect().top + scrollY - 20); });
  await m.waitForTimeout(800);
  await m.screenshot({ path: path.join(__dirname, 'f-m-fs.png') });
  await m.evaluate(() => { const el = document.getElementById('contact'); scrollTo(0, el.getBoundingClientRect().top + scrollY - 20); });
  await m.waitForTimeout(800);
  await m.screenshot({ path: path.join(__dirname, 'f-m-ct.png') });
  console.log('mh', await m.evaluate(() => document.documentElement.scrollHeight));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
