const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const path = require('path');
const { pathToFileURL } = require('url');

const pageUrl = pathToFileURL(path.join(__dirname, '..', 'issue-single.html')).href;

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
  await page.waitForTimeout(1400);
  await page.screenshot({ path: path.join(__dirname, 'issue-single-hero.png') });

  const noPageScroll = await page.evaluate(() => ({
    bodyOverflow: getComputedStyle(document.body).overflow,
    pageScrollHeight: document.documentElement.scrollHeight,
    viewport: window.innerHeight,
    activeScreens: document.querySelectorAll('.screen.on').length
  }));
  assert.equal(noPageScroll.bodyOverflow, 'hidden');
  assert.ok(noPageScroll.pageScrollHeight <= noPageScroll.viewport + 1, `page scrolls: ${noPageScroll.pageScrollHeight} > ${noPageScroll.viewport}`);
  assert.equal(noPageScroll.activeScreens, 1);
  console.log('single-screen layout has no page scroll');

  await page.locator('.dock button[data-screen="3"]').click();
  await page.waitForTimeout(900);
  await page.locator('.system').waitFor({ state: 'visible' });
  const layerInfo = await page.evaluate(() => {
    const layers = [...document.querySelectorAll('.system .layer')];
    return { count: layers.length, firstOpacity: getComputedStyle(layers[0]).opacity };
  });
  assert.equal(layerInfo.count, 10);
  assert.ok(Number(layerInfo.firstOpacity) > 0.9, `system layers did not expand: ${layerInfo.firstOpacity}`);
  await page.screenshot({ path: path.join(__dirname, 'issue-single-system.png') });
  console.log('system module expands ten layers');

  await page.locator('.dock button[data-screen="0"]').click();
  await page.waitForTimeout(700);
  await page.locator('.js-q').fill('系统 部署');
  await page.locator('.js-q').press('Enter');
  await page.waitForFunction(() => /10 层/.test(document.querySelector('.js-answer').textContent || ''));
  console.log('live retrieval still works');

  await page.locator('[data-evidence]').first().click();
  await page.locator('#evidence').waitFor({ state: 'visible' });
  await page.locator('[data-close-evidence]').click();
  await page.locator('#evidence').waitFor({ state: 'hidden' });
  console.log('evidence dialog works');

  const engineering = await page.evaluate(() => {
    const mail = [...document.querySelectorAll('a[data-mail]')].map(a => a.getAttribute('href'));
    const external = [...document.querySelectorAll('.foot a[target="_blank"]')].map(a => a.getAttribute('href'));
    return { mail, external };
  });
  assert.ok(engineering.mail.every(href => href && href.startsWith('mailto:2398198416@qq.com')), 'placeholder mailto found');
  assert.ok(engineering.external.length === 2, 'external links missing');
  console.log('email and external links finalized');

  await page.keyboard.press('2');
  await page.waitForTimeout(500);
  assert.ok(await page.locator('.proof').isVisible());
  await page.keyboard.press('ArrowRight');
  await page.waitForTimeout(500);
  assert.ok(await page.locator('.case').isVisible());
  console.log('keyboard module navigation works');

  await page.locator('.dock button[data-screen="0"]').click();
  await page.waitForTimeout(600);
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
  assert.ok(mobile.overflowX <= 1, `mobile horizontal overflow: ${mobile.overflowX}`);
  assert.ok(mobile.pageScroll <= 1, `mobile page scroll: ${mobile.pageScroll}`);
  assert.ok(mobile.screenBottom <= mobile.dockTop + 1, `content under dock: ${mobile.screenBottom} > ${mobile.dockTop}`);
  await page.screenshot({ path: path.join(__dirname, 'issue-single-mobile.png'), fullPage: true });
  console.log('mobile single-screen layout has no overflow or dock overlap');

  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.reload();
  await page.waitForTimeout(900);
  assert.equal(await page.locator('.screen.on').count(), 1);
  console.log('reduced-motion rendering OK');

  const cls = await page.evaluate(() => window.__ls || 0);
  assert.ok(cls < 0.1, `cumulative layout shift too high: ${cls}`);
  console.log(`CLS OK: ${cls.toFixed(4)}`);

  assert.deepEqual(errors, [], `browser errors: ${errors.join('\n')}`);
  console.log('browser console clean');
  await browser.close();
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
