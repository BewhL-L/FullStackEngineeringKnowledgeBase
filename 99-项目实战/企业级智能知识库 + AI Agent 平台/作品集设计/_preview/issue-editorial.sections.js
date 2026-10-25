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
    if (message.type() === 'error') errors.push(message.text());
  });

  await page.goto(pageUrl);
  await page.waitForTimeout(1200);
  await page.screenshot({ path: path.join(__dirname, 'issue-editorial-hero.png') });

  for (const id of ['s01', 's02', 's03', 's04']) {
    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(1000);
    const active = await page.evaluate(() => document.querySelector('.chapter.on')?.id || null);
    await page.screenshot({ path: path.join(__dirname, `issue-editorial-${id}.png`) });
    console.log(`section ${id}: active chapter ${active}`);
  }

  await page.keyboard.press('Home');
  await page.waitForTimeout(900);
  await page.locator('#q').fill('系统 部署');
  await page.locator('#q').press('Enter');
  await page.waitForFunction(() => /10 层/.test(document.querySelector('#streamText').textContent || ''));
  assert.match(await page.locator('#streamText').textContent(), /10 层/, '检索回答未随查询更新');
  await page.locator('.hero [data-open-evidence]').click();
  await page.locator('#drawer').waitFor({ state: 'visible' });
  await page.locator('#dClose').click();
  await page.locator('#drawer').waitFor({ state: 'hidden' });
  console.log('desktop search and evidence drawer OK');

  await page.setViewportSize({ width: 390, height: 844 });
  for (const id of ['s00', 's01', 's02', 's03', 's04']) {
    await page.locator(`#${id}`).scrollIntoViewIfNeeded();
    await page.waitForTimeout(700);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    assert.ok(overflow <= 1, `mobile ${id}: horizontal overflow ${overflow}px`);
  }
  await page.screenshot({ path: path.join(__dirname, 'issue-editorial-mobile-sections.png'), fullPage: true });
  console.log('mobile sections and horizontal overflow OK');

  assert.deepEqual(errors, [], `browser errors: ${errors.join('\n')}`);
  console.log('browser console clean');
  await browser.close();
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
