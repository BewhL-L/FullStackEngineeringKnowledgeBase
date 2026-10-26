const { chromium } = require('playwright');
const path = require('path');
const { pathToFileURL } = require('url');

(async () => {
  const b = await chromium.launch({ channel: 'chrome', headless: true });
  async function shot(file, prefix) {
    const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
    const errs = [];
    p.on('pageerror', e => errs.push(e.message));
    await p.goto(pathToFileURL(file).href);
    await p.waitForTimeout(3000);
    await p.screenshot({ path: path.join(__dirname, prefix + '-hero.png') });
    for (const id of ['fullstack', 'agent']) {
      await p.evaluate(v => {
        const el = document.getElementById(v);
        scrollTo(0, el.getBoundingClientRect().top + scrollY - 80);
      }, id);
      await p.waitForTimeout(1200);
      await p.screenshot({ path: path.join(__dirname, prefix + '-' + id + '.png') });
    }
    console.log(prefix, '| webgl-ready:', await p.evaluate(() => document.documentElement.classList.contains('webgl-ready')), '| errors:', errs.length, errs.slice(0, 2).join(' / '));
    await p.close();
  }
  await shot(path.join(__dirname, '..', 'issue.html'), 'chk-restored');
  await shot(path.join(__dirname, '..', 'issue-v15-redesign.html'), 'chk-v15');
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
