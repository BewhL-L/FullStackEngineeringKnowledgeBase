const { chromium } = require('playwright');
const path = require('path');
const { pathToFileURL } = require('url');

const TARGET = process.argv[2] || 'v16';
const FILE = TARGET === 'v16' ? 'issue-v16-explode.html' : 'issue.html';
const PRE = TARGET === 'v16' ? 'v16' : 'old';

(async () => {
  const b = await chromium.launch({
    channel: 'chrome', headless: true,
    args: ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader', '--ignore-gpu-blocklist']
  });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  const errs = [];
  p.on('pageerror', e => errs.push('pageerror: ' + e.message));
  p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  await p.goto(pathToFileURL(path.join(__dirname, '..', FILE)).href);
  await p.waitForTimeout(3200);
  await p.screenshot({ path: path.join(__dirname, PRE + '-hero.png') });

  for (const id of ['fullstack', 'agent', 'retrieval', 'case', 'evidence', 'contact']) {
    await p.evaluate(v => {
      const el = document.getElementById(v);
      if (el) scrollTo(0, el.getBoundingClientRect().top + scrollY - 90);
    }, id);
    await p.waitForTimeout(1500);
    await p.screenshot({ path: path.join(__dirname, PRE + '-' + id + '.png') });
  }

  // 全栈区：选中 03 业务层
  await p.evaluate(() => { const el = document.getElementById('fullstack'); scrollTo(0, el.getBoundingClientRect().top + scrollY - 90); });
  await p.waitForTimeout(900);
  await p.click('[data-stack="2"]');
  await p.waitForTimeout(1600);
  await p.screenshot({ path: path.join(__dirname, PRE + '-stack03.png') });

  // 渐隐取证：滚到两屏之间
  await p.evaluate(() => scrollTo(0, window.innerHeight * 1.6));
  await p.waitForTimeout(1200);
  const fadeInfo = await p.evaluate(() => {
    return [].slice.call(document.querySelectorAll('figure.plate')).map(f => ({
      cls: f.className, op: f.style.opacity || '(unset)'
    }));
  });
  await p.screenshot({ path: path.join(__dirname, PRE + '-fade.png') });
  console.log('fade states:', JSON.stringify(fadeInfo));

  const m = await b.newPage({ viewport: { width: 414, height: 900 } });
  await m.goto(pathToFileURL(path.join(__dirname, '..', FILE)).href);
  await m.waitForTimeout(2800);
  await m.screenshot({ path: path.join(__dirname, PRE + '-mobile.png') });

  console.log(FILE, '| errors:', errs.length, errs.slice(0, 5).join(' | '));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
