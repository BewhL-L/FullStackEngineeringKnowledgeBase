const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const path = require('path');
const { pathToFileURL } = require('url');

const pageUrl = pathToFileURL(path.join(__dirname, '..', 'issue-3d.html')).href;

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => {
    const text = message.text();
    if (message.type() === 'error' && !/Failed to load resource|net::ERR|fontshare|jsdelivr/i.test(text)) errors.push(text);
  });

  await page.goto(pageUrl);
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(__dirname, 'issue-3d-hero.png') });

  await page.waitForFunction(() => typeof window.__heroSelectChannel === 'function', null, { timeout: 12000 });
  console.log('three.js hero scene ready');

  await page.locator('.js-q').fill('系统 部署');
  await page.locator('.js-q').press('Enter');
  await page.waitForFunction(() => /10 层/.test(document.querySelector('.js-answer').textContent || ''));
  assert.match(await page.locator('.js-answer').textContent(), /10 层/);
  console.log('live retrieval answer updates');

  await page.locator('.chips button[data-channel="2"]').click();
  assert.equal(await page.locator('#channelName').textContent(), 'GRAPH · 关系召回');
  console.log('channel control updates 3D focus');

  await page.locator('[data-evidence]').first().click();
  await page.locator('#evidence').waitFor({ state: 'visible' });
  await page.locator('[data-close-evidence]').click();
  await page.locator('#evidence').waitFor({ state: 'hidden' });
  console.log('evidence dialog works');

  await page.locator('.js-case-list button').nth(2).click();
  assert.equal(await page.locator('.js-case-title').textContent(), 'RRF 融合');
  await page.locator('#s03').scrollIntoViewIfNeeded();
  await page.waitForTimeout(600);
  const layerPoint = await page.evaluate(() => {
    const layers = [...document.querySelectorAll('.js-sys-stack .layer')];
    const target = layers[1];
    const r = target.getBoundingClientRect();
    for (let y = r.top + 4; y < r.bottom - 4; y += 4) {
      for (let x = r.left + 4; x < r.right - 4; x += 4) {
        const el = document.elementFromPoint(x, y);
        if (el && el.closest && el.closest('.layer') === target) return { x, y };
      }
    }
    return null;
  });
  assert.ok(layerPoint, 'could not find clickable point on system layer');
  await page.mouse.click(layerPoint.x, layerPoint.y);
  assert.match(await page.locator('.js-sys-text').textContent(), /网关/);
  console.log('case and system interactions work');

  await page.locator('.links a[href="#s03"]').click();
  await page.waitForTimeout(900);
  const scrolled = await page.evaluate(() => window.scrollY);
  assert.ok(scrolled > 100, `anchor navigation did not scroll: ${scrolled}`);
  await page.screenshot({ path: path.join(__dirname, 'issue-3d-system.png') });
  console.log('anchor navigation works without deck mode');

  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(900);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  assert.ok(overflow <= 1, `mobile horizontal overflow: ${overflow}px`);
  await page.screenshot({ path: path.join(__dirname, 'issue-3d-mobile.png'), fullPage: true });
  console.log('mobile layout has no horizontal overflow');

  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.reload();
  await page.waitForFunction(() => typeof window.__heroSelectChannel === 'function', null, { timeout: 12000 });
  await page.waitForTimeout(500);
  const reducedOverflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  assert.ok(reducedOverflow <= 1, `reduced-motion mobile overflow: ${reducedOverflow}px`);
  console.log('reduced-motion rendering and layout OK');

  assert.deepEqual(errors, [], `browser errors: ${errors.join('\n')}`);
  console.log('browser console clean');
  await browser.close();
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
