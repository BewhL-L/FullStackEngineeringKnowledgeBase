const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const path = require('path');
const { pathToFileURL } = require('url');

const pageUrl = pathToFileURL(path.join(__dirname, '..', 'issue.html')).href;

(async () => {
  const browser = await chromium.launch({
    channel: 'chrome',
    headless: true,
    args: ['--disable-frame-rate-limit', '--disable-gpu-vsync']
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto(pageUrl);
  await page.waitForTimeout(1800);

  const samples = [];
  for (let i = 0; i < 3; i++) {
    await page.waitForTimeout(1050);
    samples.push(await page.evaluate(() => ({ ...window.__engineDiagnostics })));
  }
  const final = samples[samples.length - 1];
  const minFps = Math.min(...samples.map(sample => sample.fps));
  assert.equal(final.target, 120);
  assert.ok(samples.every(sample => sample.refreshHz >= 120), `refresh probe too low: ${samples.map(s => s.refreshHz).join(', ')}`);
  assert.ok(minFps >= 120, `sustained render below 120fps: ${samples.map(s => s.fps).join(', ')}`);
  assert.ok(final.renderMs < 8.33, `CPU frame budget exceeded: ${final.renderMs}ms`);
  assert.equal(final.quality, 'high', `quality degraded during benchmark: ${final.quality}`);
  assert.ok(final.drawCalls < 90, `draw calls: ${final.drawCalls}`);
  assert.ok(final.triangles < 20000, `triangles: ${final.triangles}`);
  assert.deepEqual(errors, [], `browser errors: ${errors.join('\n')}`);

  console.log('3D HIGH-REFRESH BENCHMARK');
  samples.forEach((sample, index) => console.log(`window ${index + 1}: fps=${sample.fps} target=${sample.target} render=${sample.renderMs}ms calls=${sample.drawCalls} tris=${sample.triangles} quality=${sample.quality}`));
  await page.screenshot({ path: path.join(__dirname, 'issue-3d-perf.png') });
  await browser.close();
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
