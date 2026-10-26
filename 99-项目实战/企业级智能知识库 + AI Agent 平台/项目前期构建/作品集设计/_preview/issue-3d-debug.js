const { chromium } = require('playwright');
const path = require('path');
const { pathToFileURL } = require('url');
const pageUrl = pathToFileURL(path.join(__dirname, '..', 'issue-3d.html')).href;

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  await page.goto(pageUrl);
  await page.waitForTimeout(1200);
  await page.locator('#s03').scrollIntoViewIfNeeded();
  await page.waitForTimeout(600);
  const info = await page.evaluate(() => {
    const layers = [...document.querySelectorAll('.js-sys-stack .layer')];
    const target = layers[1];
    const r = target.getBoundingClientRect();
    const el = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    return {
      layerIndex: target.style.getPropertyValue('--i'),
      rect: { x: r.x, y: r.y, w: r.width, h: r.height },
      hit: el ? (el.className || el.tagName) : null,
      hitIsLayer: !!(el && el.closest && el.closest('.layer')),
      hitLayerIndex: el && el.closest ? (el.closest('.layer') ? el.closest('.layer').style.getPropertyValue('--i') : null) : null
    };
  });
  console.log(info);
  await page.locator('.js-sys-stack .layer').nth(1).dispatchEvent('click');
  await page.waitForTimeout(200);
  console.log('after dispatch:', await page.locator('.js-sys-text').textContent());
  await browser.close();
})().catch(e => { console.error(e); process.exitCode = 1; });
