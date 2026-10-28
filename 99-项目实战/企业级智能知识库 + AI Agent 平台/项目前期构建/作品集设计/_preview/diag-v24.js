const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const URL = n => 'http://127.0.0.1:8791/' + n;

(async () => {
  const b = await chromium.launch({ headless: true, channel: 'chrome', args: ['--autoplay-policy=no-user-gesture-required'] });

  for (const file of ['issue-v23-tide.html', 'issue-v24-camera.html']) {
    const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
    const bad = [];
    p.on('requestfailed', r => bad.push('FAILED ' + r.url()));
    p.on('response', r => { if (r.status() >= 400) bad.push(r.status() + ' ' + r.url()); });
    await p.goto(URL(file), { waitUntil: 'load' });
    await sleep(1800);
    const r = await p.evaluate(() => {
      const de = document.documentElement;
      const over = [];
      document.querySelectorAll('*').forEach(el => {
        const b = el.getBoundingClientRect();
        if (b.width === 0) return;
        if (b.right > de.clientWidth + 1 || b.left < -1) {
          over.push({
            t: el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ').filter(Boolean).slice(0, 2).join('.') : ''),
            l: Math.round(b.left), r: Math.round(b.right)
          });
        }
      });
      return { sw: de.scrollWidth, cw: de.clientWidth, over: over.slice(0, 12) };
    });
    console.log('\n===== ' + file + ' =====');
    console.log('scrollWidth', r.sw, 'clientWidth', r.cw);
    console.log('越界元素:', JSON.stringify(r.over));
    console.log('网络问题:', bad.length ? bad.join('\n  ') : '无');
    await p.close();
  }
  await b.close();
})();
