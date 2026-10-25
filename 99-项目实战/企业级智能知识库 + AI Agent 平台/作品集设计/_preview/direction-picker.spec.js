const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const path = require('path');
const { pathToFileURL } = require('url');

const pageUrl = pathToFileURL(path.join(__dirname, '..', 'direction-picker.html')).href;
const selectors = ['.lacquer', '.editorial', '.field'];

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => {
    if (message.type() === 'error') errors.push(message.text());
  });

  for (let i = 1; i <= 3; i++) {
    await page.goto(`${pageUrl}?v=${i}`);
    const root = page.locator(selectors[i - 1]);
    await root.waitFor({ state: 'visible' });
    assert.equal(await root.locator('.hit').count(), 3, `variant ${i}: expected three retrieval hits`);
    await root.locator('.js-q').fill('系统 部署');
    await root.locator('.js-q').press('Enter');
    assert.match(await root.locator('.js-answer').textContent(), /10 层/, `variant ${i}: retrieval answer did not update`);
    await root.locator('.js-sources .source').first().click();
    await page.locator('#evidence').waitFor({ state: 'visible' });
    assert.match(await page.locator('#evidence').textContent(), /79/);
    await page.locator('[data-close-evidence]').click();
    await page.locator('#evidence').waitFor({ state: 'hidden' });
    const preset = root.locator('[data-query]').first();
    if (await preset.count()) {
      await preset.click();
      assert.doesNotMatch(await root.locator('.js-answer').textContent(), /没有可回答/);
    }
    console.log(`desktop variant ${i}: search, answer, sources and evidence OK`);
  }

  await page.goto(`${pageUrl}?v=3`);
  await page.locator('[data-node="1"]').click();
  assert.equal(await page.locator('.js-node-title').textContent(), '向量召回');
  await page.locator('body').click({ position: { x: 8, y: 8 } });
  await page.keyboard.press('2');
  await page.locator('.editorial').waitFor({ state: 'visible' });
  assert.match(page.url(), /v=2/);
  await page.keyboard.press('ArrowRight');
  await page.locator('.field').waitFor({ state: 'visible' });
  await page.keyboard.press('r');
  await page.locator('.field').waitFor({ state: 'visible' });
  console.log('picker number keys, arrow keys, replay and 3D nodes OK');

  await page.setViewportSize({ width: 390, height: 844 });
  for (let i = 1; i <= 3; i++) {
    await page.goto(`${pageUrl}?v=${i}`);
    await page.locator(selectors[i - 1]).waitFor({ state: 'visible' });
    await page.waitForTimeout(900);
    const dimensions = await page.evaluate(() => ({
      viewport: window.innerWidth,
      content: document.documentElement.scrollWidth
    }));
    assert.ok(dimensions.content <= dimensions.viewport + 1, `mobile variant ${i}: horizontal overflow ${dimensions.content} > ${dimensions.viewport}`);
    await page.screenshot({ path: path.join(__dirname, `direction-mobile-v${i}.png`), fullPage: true });
    console.log(`mobile variant ${i}: no horizontal overflow`);
  }

  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto(`${pageUrl}?v=1`);
  await page.locator('.la-seal').waitFor({ state: 'visible' });
  assert.deepEqual(errors, [], `browser errors: ${errors.join('\n')}`);
  console.log('reduced-motion rendering and browser console OK');
  await browser.close();
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
