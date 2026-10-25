const { chromium } = require('playwright');
const path = require('path');
const { pathToFileURL } = require('url');
const pageUrl = pathToFileURL(path.join(__dirname, '..', 'issue.html')).href;

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  await page.goto(pageUrl);
  await page.waitForTimeout(1200);
  await page.locator('.dock button[data-screen="3"]').click();
  await page.waitForTimeout(1300);
  const info = await page.evaluate(() => {
    const layers = [...document.querySelectorAll('.system .layer')];
    return layers.map((l, i) => {
      const r = l.getBoundingClientRect();
      const mid = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
      return {
        i,
        text: l.textContent.trim().slice(0, 12),
        x: Math.round(r.x),
        y: Math.round(r.y),
        w: Math.round(r.width),
        h: Math.round(r.height),
        opacity: getComputedStyle(l).opacity,
        hit: mid ? (mid.closest('.layer') === l ? 'self' : (mid.className || mid.tagName)) : 'none'
      };
    });
  });
  console.log(info);
  await page.locator('.system .layer').nth(9).screenshot({ path: path.join(__dirname, 'issue-glass-layer10.png') });
  await browser.close();
})().catch(e => { console.error(e); process.exitCode = 1; });
