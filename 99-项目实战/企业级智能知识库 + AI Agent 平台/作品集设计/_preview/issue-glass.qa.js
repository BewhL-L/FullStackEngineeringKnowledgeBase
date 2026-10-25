const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const path = require('path');
const { pathToFileURL } = require('url');

const pageUrl = pathToFileURL(path.join(__dirname, '..', 'issue.html')).href;

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => {
    const text = message.text();
    if (message.type() === 'error' && !/Failed to load resource|net::ERR|fontshare|jsdelivr/i.test(text)) errors.push(text);
  });
  await page.addInitScript(() => {
    window.__ls = 0;
    try {
      new PerformanceObserver(list => {
        for (const entry of list.getEntries()) if (!entry.hadRecentInput) window.__ls += entry.value;
      }).observe({ type: 'layout-shift', buffered: true });
    } catch (e) {}
  });

  await page.goto(pageUrl);
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(__dirname, 'issue-glass-core.png') });

  const glass = await page.evaluate(() => {
    const demo = getComputedStyle(document.querySelector('.demo'));
    const metric = getComputedStyle(document.querySelector('.metric'));
    return {
      demoBg: demo.backgroundColor,
      demoBlur: demo.backdropFilter || demo.webkitBackdropFilter,
      metricBg: metric.backgroundColor,
      metricBlur: metric.backdropFilter || metric.webkitBackdropFilter
    };
  });
  assert.equal(glass.demoBg, 'rgba(18, 18, 26, 0.3)');
  assert.match(glass.demoBlur, /blur\(18px\)/);
  assert.equal(glass.metricBg, 'rgba(18, 18, 26, 0.3)');
  assert.match(glass.metricBlur, /blur\(16px\)/);
  console.log('module panels use 30% frosted glass');

  await page.locator('.dock button[data-screen="3"]').click();
  await page.waitForTimeout(1100);
  const stair = await page.evaluate(() => {
    const layers = [...document.querySelectorAll('.system .layer')];
    const first = layers[0].getBoundingClientRect();
    const last = layers[layers.length - 1].getBoundingClientRect();
    const screen = document.querySelector('.screen.on').getBoundingClientRect();
    return { count: layers.length, first, last, screenBottom: screen.bottom };
  });
  assert.equal(stair.count, 10);
  assert.ok(stair.first.right > stair.last.right + 60, `stair is not right-to-left: first ${stair.first.right}, last ${stair.last.right}`);
  assert.ok(stair.last.top > stair.first.top + 180, `stair is not top-to-bottom: first ${stair.first.top}, last ${stair.last.top}`);
  assert.ok(stair.last.left < stair.first.left - 80, `last card is not left-bottom: first ${stair.first.left}, last ${stair.last.left}`);
  assert.ok(stair.last.bottom <= stair.screenBottom + 1, `last layer clipped: ${stair.last.bottom} > ${stair.screenBottom}`);
  await page.screenshot({ path: path.join(__dirname, 'issue-glass-system.png') });
  console.log('system staircase runs from top-right to bottom-left');

  await page.locator('.dock button[data-screen="0"]').click();
  await page.waitForTimeout(700);
  await page.locator('.js-q').fill('系统 部署');
  await page.locator('.js-q').press('Enter');
  await page.waitForFunction(() => /10 层/.test(document.querySelector('.js-answer').textContent || ''));
  await page.locator('[data-evidence]').first().click();
  await page.locator('#evidence').waitFor({ state: 'visible' });
  await page.locator('[data-close-evidence]').click();
  await page.locator('#evidence').waitFor({ state: 'hidden' });
  console.log('retrieval and evidence still work');

  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(900);
  const mobile = await page.evaluate(() => {
    const screen = document.querySelector('.screen.on').getBoundingClientRect();
    const dock = document.querySelector('.dock').getBoundingClientRect();
    return {
      overflowX: document.documentElement.scrollWidth - window.innerWidth,
      pageScroll: document.documentElement.scrollHeight - window.innerHeight,
      screenBottom: screen.bottom,
      dockTop: dock.top
    };
  });
  assert.ok(mobile.overflowX <= 1, `mobile overflow: ${mobile.overflowX}`);
  assert.ok(mobile.pageScroll <= 1, `mobile page scroll: ${mobile.pageScroll}`);
  assert.ok(mobile.screenBottom <= mobile.dockTop + 1, `content under dock: ${mobile.screenBottom} > ${mobile.dockTop}`);
  await page.screenshot({ path: path.join(__dirname, 'issue-glass-mobile.png'), fullPage: true });
  console.log('mobile layout remains clean');

  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.reload();
  await page.waitForTimeout(900);
  assert.equal(await page.locator('.screen.on').count(), 1);
  console.log('reduced-motion rendering OK');

  const cls = await page.evaluate(() => window.__ls || 0);
  assert.ok(cls < 0.1, `CLS too high: ${cls}`);
  console.log(`CLS OK: ${cls.toFixed(4)}`);

  assert.deepEqual(errors, [], `browser errors: ${errors.join('\n')}`);
  console.log('browser console clean');
  await browser.close();
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
