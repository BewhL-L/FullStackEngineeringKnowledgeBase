const { chromium } = require('playwright');
const path = require('path');
const { pathToFileURL } = require('url');

const targets = process.argv[2] ? process.argv[2].split(',') : ['hero', 'fullstack', 'agent', 'retrieval', 'case', 'evidence', 'contact'];

(async () => {
  const b = await chromium.launch({
    channel: 'chrome',
    headless: true,
    args: ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader', '--ignore-gpu-blocklist']
  });
  const file = path.join(__dirname, '..', 'issue.html');
  const p = await b.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto(pathToFileURL(file).href);
  await p.waitForTimeout(3500);
  console.log('webgl-ready:', await p.evaluate(() => document.documentElement.classList.contains('webgl-ready')));
  for (const id of targets) {
    if (id !== 'hero') {
      await p.evaluate(v => {
        const el = document.getElementById(v);
        if (el) scrollTo(0, el.getBoundingClientRect().top + scrollY - 90);
      }, id);
    } else {
      await p.evaluate(() => scrollTo(0, 0));
    }
    await p.waitForTimeout(1800);
    await p.screenshot({ path: path.join(__dirname, 'rev-' + id + '.png') });
  }
  const m = await b.newPage({ viewport: { width: 414, height: 900 }, deviceScaleFactor: 1 });
  await m.goto(pathToFileURL(file).href);
  await m.waitForTimeout(3000);
  await m.screenshot({ path: path.join(__dirname, 'rev-mobile-hero.png') });
  console.log('errors:', errs.length, errs.slice(0, 3).join(' / '));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
