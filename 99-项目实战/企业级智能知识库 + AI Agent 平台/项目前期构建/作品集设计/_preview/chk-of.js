const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch({ headless: true, channel: 'chrome', args: ['--autoplay-policy=no-user-gesture-required'] });
  for (const f of ['issue-v23-tide.html', 'issue-v24-camera.html']) {
    const p = await b.newPage({ viewport: { width: 1920, height: 900 } });
    await p.goto('http://127.0.0.1:8791/' + f, { waitUntil: 'load' });
    await sleep(2000);
    await p.evaluate(() => scrollTo(0, document.documentElement.scrollHeight));
    await sleep(1200);
    const out = [];
    for (const w of [1920, 1440, 1280, 1024]) {
      await p.setViewportSize({ width: w, height: 900 });
      await sleep(1500);
      const a = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      await p.evaluate(() => scrollBy(0, -1)); await sleep(500);
      const b2 = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      // 去掉缩放变换再测
      await p.evaluate(() => { document.querySelectorAll('.cam-layer').forEach(v => v.style.transform = ''); });
      await sleep(400);
      const c = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      out.push(w + ': resize后=' + a + ' 滚动后=' + b2 + ' 去scale=' + c);
    }
    console.log(f + '\n  ' + out.join('\n  '));
    await p.close();
  }
  await b.close();
})();
