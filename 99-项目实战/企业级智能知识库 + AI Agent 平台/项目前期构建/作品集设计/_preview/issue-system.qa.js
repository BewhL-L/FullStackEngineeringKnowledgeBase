const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const path = require('path');
const { pathToFileURL } = require('url');

const pageUrl = pathToFileURL(path.join(__dirname, '..', 'issue.html')).href;
const shot = name => path.join(__dirname, name);

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => {
    if (message.type() === 'error') errors.push(message.text());
  });
  await page.addInitScript(() => {
    window.__cls = 0;
    window.__shiftLog = [];
    try {
      new PerformanceObserver(list => {
        for (const entry of list.getEntries()) if (!entry.hadRecentInput) {
          window.__cls += entry.value;
          window.__shiftLog.push({ value: entry.value, time: entry.startTime, sources: entry.sources.map(source => ({
            node: source.node ? source.node.tagName + '.' + String(source.node.className || '') : 'unknown',
            previous: source.previousRect, current: source.currentRect
          })) });
        }
      }).observe({ type: 'layout-shift', buffered: true });
    } catch (e) {}
  });

  await page.goto(pageUrl);
  await page.waitForTimeout(1700);
  await page.screenshot({ path: shot('issue-system-hero.png') });
  const initial = await page.evaluate(() => ({
    overflowX: document.documentElement.scrollWidth - innerWidth,
    pageHeight: document.documentElement.scrollHeight,
    viewport: innerHeight,
    webgl: document.documentElement.classList.contains('webgl-ready'),
    fallback: document.documentElement.classList.contains('no-3d'),
    blurred: [...document.querySelectorAll('body *')].filter(el => {
      const style = getComputedStyle(el);
      return (style.backdropFilter && style.backdropFilter !== 'none') || (style.webkitBackdropFilter && style.webkitBackdropFilter !== 'none');
    }).length,
    canvasWidth: document.querySelector('#engineCanvas').width
  }));
  assert.ok(initial.overflowX <= 1, `desktop horizontal overflow: ${initial.overflowX}`);
  assert.ok(initial.pageHeight > initial.viewport * 4, 'continuous scroll narrative missing');
  assert.ok(initial.webgl && !initial.fallback, 'WebGL scene did not initialize');
  assert.equal(initial.blurred, 0, 'live backdrop blur remains in content');
  assert.ok(initial.canvasWidth <= 1440 * 1.35 + 1, 'desktop DPR cap failed');
  const engine = await page.evaluate(() => window.__engineDiagnostics);
  assert.equal(engine.target, 120, `high-refresh target is ${engine.target}, expected 120`);
  assert.ok(engine.fps >= 120, `renderer throughput below 120fps: ${engine.fps}`);
  assert.ok(engine.renderMs < 8.33, `CPU frame cost exceeds 120fps budget: ${engine.renderMs}ms`);
  assert.ok(engine.drawCalls < 90, `draw call budget exceeded: ${engine.drawCalls}`);
  assert.ok(engine.triangles < 20000, `triangle budget exceeded: ${engine.triangles}`);
  console.log(`PASS: continuous scroll, WebGL ready, no blur, target ${engine.target}fps, observed ${engine.fps}fps`);

  const revealInitial = await page.evaluate(() => ({
    forcedLayers: [...document.querySelectorAll('.rv')].filter(el => getComputedStyle(el).willChange !== 'auto').length,
    heroIn: document.querySelector('.hero-copy .eyebrow').classList.contains('in')
  }));
  assert.equal(revealInitial.heroIn, true, 'hero element did not reveal on load');
  assert.equal(revealInitial.forcedLayers, 0, 'reveal elements keep forced will-change layers');
  await page.evaluate(() => {
    document.documentElement.style.scrollBehavior = 'auto';
    window.scrollTo(0, document.documentElement.scrollHeight);
  });
  await page.waitForTimeout(260);
  const revealHidden = await page.evaluate(() => {
    const el = document.querySelector('.hero-copy .eyebrow');
    return { in: el.classList.contains('in'), above: el.classList.contains('rv-above') };
  });
  assert.equal(revealHidden.in, false, 'element did not fade out after leaving viewport');
  assert.equal(revealHidden.above, true, 'exit direction was not detected as above');
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(260);
  const revealRestored = await page.evaluate(() => {
    const el = document.querySelector('.hero-copy .eyebrow');
    return { in: el.classList.contains('in'), above: el.classList.contains('rv-above') };
  });
  assert.equal(revealRestored.in, true, 'element did not re-enter when scrolled back');
  assert.equal(revealRestored.above, false, 'exit state was not cleared on re-entry');
  console.log('PASS: bidirectional scroll reveal without forced compositor layers');

  await page.locator('.links a[href="#fullstack"]').click();
  await page.waitForTimeout(950);
  await page.locator('[data-stack="4"]').click();
  assert.match(await page.locator('#inspectorTitle').textContent(), /容器化交付/);
  assert.equal(await page.locator('#sceneName').textContent(), 'FULLSTACK / SERVICE STRATA');
  assert.equal(await page.locator('.arch-row.on').count(), 1);
  assert.equal(await page.locator('.arch-row.on').getAttribute('data-stack'), '4');
  const headingAlignment = await page.evaluate(() => {
    const heading = document.querySelector('#fullstack .section-heading').getBoundingClientRect().left;
    const list = document.querySelector('#fullstack .architecture').getBoundingClientRect().left;
    return Math.abs(heading - list);
  });
  assert.ok(headingAlignment <= 1, `section heading misaligned with content: ${headingAlignment}px`);
  await page.waitForTimeout(300);
  await page.screenshot({ path: shot('issue-system-fullstack.png') });
  console.log('PASS: native anchor navigation and fullstack inspector');

  await page.locator('.links a[href="#agent"]').click();
  await page.waitForTimeout(850);
  await page.locator('[data-agent="2"]').click();
  assert.match(await page.locator('#traceTitle').textContent(), /保留反馈/);
  await page.locator('#agentPlay').click();
  await page.waitForTimeout(850);
  assert.equal(await page.locator('#traceState').textContent(), 'STEP 04 / 04');
  await page.screenshot({ path: shot('issue-system-agent.png') });
  console.log('PASS: agent step inspection and trace replay');

  await page.locator('.links a[href="#retrieval"]').click();
  await page.waitForTimeout(850);
  await page.locator('.js-q').fill('系统 部署');
  await page.locator('.js-q').press('Enter');
  await page.waitForFunction(() => /10 层/.test(document.querySelector('.js-answer').textContent || ''));
  await page.locator('[data-channel="2"]').click();
  assert.match(await page.locator('#channelDescription').textContent(), /实体关系/);
  await page.locator('.js-q').fill('混合检索为什么有效');
  await page.locator('.js-q').press('Enter');
  await page.waitForFunction(() => /BM25/.test(document.querySelector('.js-answer').textContent || ''));
  await page.locator('.result').first().focus();
  const firstResult = await page.locator('.result.on').getAttribute('data-id');
  await page.keyboard.press('ArrowDown');
  await page.waitForTimeout(80);
  const secondResult = await page.locator('.result.on').getAttribute('data-id');
  assert.notEqual(secondResult, firstResult, 'keyboard did not move to the next retrieval result');
  await page.keyboard.press('Enter');
  await page.locator('#evidenceDialog').waitFor({ state: 'visible' });
  await page.locator('[data-close-evidence]').click();
  await page.locator('#evidenceDialog').waitFor({ state: 'hidden' });
  await page.screenshot({ path: shot('issue-system-retrieval.png') });
  console.log('PASS: local retrieval, keyboard result navigation and 3D channel controls');

  await page.locator('.links a[href="#case"]').click();
  await page.waitForTimeout(850);
  assert.equal(await page.locator('#sceneName').textContent(), 'CASE / TRACEABLE PATH');
  assert.equal(await page.locator('.case-metric').count(), 4);
  await page.screenshot({ path: shot('issue-system-case.png') });
  console.log('PASS: case-study before/after section and scene state');

  await page.locator('.links a[href="#evidence"]').click();
  await page.waitForTimeout(850);
  await page.locator('#evidence [data-evidence="tables"]').click();
  await page.locator('#evidenceDialog').waitFor({ state: 'visible' });
  assert.ok(await page.locator('[data-ev-panel="tables"]').isVisible());
  assert.equal(await page.evaluate(() => document.body.classList.contains('modal-open')), true);
  await page.waitForTimeout(350);
  await page.screenshot({ path: shot('issue-system-evidence.png') });
  await page.locator('[data-close-evidence]').click();
  await page.locator('#evidenceDialog').waitFor({ state: 'hidden' });
  assert.equal(await page.evaluate(() => document.body.classList.contains('modal-open')), false);
  console.log('PASS: tabbed evidence dialog and scroll lock');

  await page.locator('.links a[href="#contact"]').click();
  await page.waitForTimeout(850);
  assert.match(await page.locator('#contactTitle').textContent(), /AI 负责快/);
  await page.screenshot({ path: shot('issue-system-contact.png') });
  console.log('PASS: contact section');

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(pageUrl);
  await page.waitForTimeout(1300);
  const mobile = await page.evaluate(() => ({
    overflowX: document.documentElement.scrollWidth - innerWidth,
    canvasWidth: document.querySelector('#engineCanvas').width,
    navVisible: getComputedStyle(document.querySelector('.links')).display
  }));
  assert.ok(mobile.overflowX <= 1, `mobile horizontal overflow: ${mobile.overflowX}`);
  assert.ok(mobile.canvasWidth <= 390 * 1.2 + 1, 'mobile DPR cap failed');
  assert.equal(mobile.navVisible, 'none');
  await page.screenshot({ path: shot('issue-system-mobile.png') });
  await page.locator('.nav-toggle').click();
  await page.waitForTimeout(80);
  assert.equal(await page.locator('.nav-toggle').getAttribute('aria-expanded'), 'true');
  assert.equal(await page.evaluate(() => !!document.activeElement.closest('#siteLinks')), true);
  await page.keyboard.press('Shift+Tab');
  assert.equal(await page.evaluate(() => document.activeElement.getAttribute('data-nav')), 'contact');
  await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(() => document.activeElement.getAttribute('data-nav')), 'fullstack');
  await page.mouse.click(200, 400);
  assert.equal(await page.locator('.nav-toggle').getAttribute('aria-expanded'), 'false');
  await page.locator('.nav-toggle').click();
  await page.locator('.links a[href="#agent"]').click();
  await page.waitForTimeout(700);
  assert.equal(await page.locator('.nav-toggle').getAttribute('aria-expanded'), 'false');
  await page.screenshot({ path: shot('issue-system-mobile-agent.png') });
  await page.evaluate(() => document.querySelector('#evidence [data-evidence="chain"]').click());
  await page.locator('#evidenceDialog').waitFor({ state: 'visible' });
  await page.waitForTimeout(320);
  const dialogBox = await page.locator('#evidenceDialog').evaluate(el => {
    const rect = el.getBoundingClientRect();
    return { left: rect.left, right: rect.right, width: innerWidth, overflow: el.scrollWidth - el.clientWidth };
  });
  assert.ok(dialogBox.left >= 0 && dialogBox.right <= dialogBox.width + 1, `mobile dialog clipped: ${JSON.stringify(dialogBox)}`);
  assert.ok(dialogBox.overflow <= 1, `mobile dialog horizontal overflow: ${dialogBox.overflow}`);
  await page.screenshot({ path: shot('issue-system-mobile-evidence.png') });
  const dialogScroll = await page.locator('#evidenceDialog').evaluate(el => { el.scrollTop = el.scrollHeight; return el.scrollTop; });
  assert.ok(dialogScroll > 0, 'mobile evidence dialog is not vertically scrollable');
  await page.locator('[data-close-evidence]').click();
  await page.locator('#evidenceDialog').waitFor({ state: 'hidden' });
  console.log('PASS: mobile recomposition, DPR cap, menu and evidence dialog');

  for (const viewport of [{ width: 1280, height: 800 }, { width: 1024, height: 768 }, { width: 768, height: 1024 }, { width: 320, height: 740 }]) {
    await page.setViewportSize(viewport);
    await page.goto(pageUrl);
    await page.waitForTimeout(520);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    assert.ok(overflow <= 1, `${viewport.width}x${viewport.height} horizontal overflow: ${overflow}`);
    const primaryActionsFit = await page.evaluate(() => [...document.querySelectorAll('.hero-actions .btn')].every(el => el.getBoundingClientRect().right <= innerWidth + 1));
    assert.equal(primaryActionsFit, true, `${viewport.width}x${viewport.height} hero action overflow`);
    if (viewport.width === 1024 || viewport.width === 768) await page.screenshot({ path: shot(`issue-system-${viewport.width}.png`) });
  }
  console.log('PASS: 1280 / 1024 / 768 / 320 breakpoints');

  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto(pageUrl);
  await page.waitForTimeout(900);
  assert.ok(await page.locator('.rv.in').count() > 20, 'reduced-motion content not visible');
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth - innerWidth <= 1), true);
  const cls = await page.evaluate(() => window.__cls || 0);
  if (cls >= 0.1) console.log('SHIFT LOG', JSON.stringify(await page.evaluate(() => window.__shiftLog || []), null, 2));
  assert.ok(cls < 0.1, `CLS too high: ${cls}`);
  assert.deepEqual(errors, [], `browser errors: ${errors.join('\n')}`);
  console.log(`PASS: reduced motion, responsive layout, clean console; CLS=${cls.toFixed(4)}`);
  await browser.close();
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
