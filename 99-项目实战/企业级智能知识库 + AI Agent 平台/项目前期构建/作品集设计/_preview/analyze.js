const { chromium } = require('playwright');

(async () => {
  const b = await chromium.launch({ channel: 'chrome', headless: true });
  const p = await b.newPage();
  await p.goto('http://127.0.0.1:8771/_preview/analyze.html');
  await p.waitForFunction(() => window.__A, { timeout: 15000 });
  const a = await p.evaluate(() => window.__A);
  console.log(JSON.stringify(a, null, 1));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
