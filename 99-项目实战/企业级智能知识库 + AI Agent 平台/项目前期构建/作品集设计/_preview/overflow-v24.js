const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const b = await chromium.launch({ headless: true, channel: 'chrome', args: ['--autoplay-policy=no-user-gesture-required'] });
  for (const file of ['issue-v23-tide.html', 'issue-v24-camera.html']) {
    console.log('\n===== ' + file + ' =====');
    for (const w of [1920, 1440, 1280, 1024, 900, 768, 390, 360]) {
      const p = await b.newPage({ viewport: { width: w, height: 900 } });
      const bad = [];
      p.on('response', r => { if (r.status() >= 400) bad.push(r.status() + ' ' + r.url().split('/').pop()); });
      await p.goto('http://127.0.0.1:8791/' + file, { waitUntil: 'load' });
      await sleep(1500);
      // 滚到底再回顶，模拟真实浏览后的状态
      await p.evaluate(() => scrollTo(0, document.documentElement.scrollHeight));
      await sleep(900);
      await p.evaluate(() => scrollTo(0, 0));
      await sleep(900);
      const r = await p.evaluate(() => {
        const de = document.documentElement;
        return { sw: de.scrollWidth, cw: de.clientWidth, bw: document.body.scrollWidth };
      });
      const d = r.sw - r.cw;
      console.log(String(w).padStart(5), d > 1 ? ('溢出 ' + d + 'px  (body ' + r.bw + ')') : 'ok', bad.length ? '[' + bad.join(',') + ']' : '');
      await p.close();
    }
  }
  await b.close();
})();
