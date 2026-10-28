const { chromium } = require('playwright');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const OUT = __dirname;
const URL = 'http://127.0.0.1:8791/issue-v24-camera.html';

const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const b = await chromium.launch({
    headless: true,
    channel: 'chrome',
    args: ['--autoplay-policy=no-user-gesture-required', '--enable-gpu-rasterization']
  });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  const errs = [];
  p.on('pageerror', e => errs.push('pageerror: ' + e.message));
  p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });

  await p.goto(URL, { waitUntil: 'load' });
  await sleep(2500);

  const meta = await p.evaluate(() => {
    const vs = [...document.querySelectorAll('.cam-layer')];
    return {
      docH: document.documentElement.scrollHeight,
      anchors: ['hero', 'fullstack', 'retrieval', 'evidence', 'contact'].map(id => {
        const el = document.getElementById(id);
        return el ? Math.round(el.getBoundingClientRect().top + scrollY) : -1;
      }),
      layers: vs.map(v => ({ w: v.videoWidth, h: v.videoHeight, dur: +(v.duration || 0).toFixed(2), src: (v.currentSrc || '').split('/').pop() }))
    };
  });
  console.log('--- 锚点 / 素材 ---');
  console.log(JSON.stringify(meta, null, 1));

  // 逐章节滚动，读图层透明度与播放状态
  const stops = ['hero', 'fullstack', 'agent', 'retrieval', 'case', 'evidence', 'contact'];
  console.log('\n--- 滚动视角状态 ---');
  for (const id of stops) {
    await p.evaluate(v => {
      const el = document.getElementById(v);
      scrollTo(0, el.getBoundingClientRect().top + scrollY - (v === 'hero' ? 0 : 60));
    }, id);
    await sleep(1400);
    const st = await p.evaluate(() => {
      const vs = [...document.querySelectorAll('.cam-layer')];
      return {
        y: Math.round(scrollY),
        op: vs.map(v => +(+getComputedStyle(v).opacity).toFixed(2)),
        playing: vs.map(v => !v.paused && v.currentTime > 0.05),
        tf: vs.map(v => getComputedStyle(v).transform === 'none' ? '-' : 'scaled')
      };
    });
    console.log(id.padEnd(10), 'y=' + String(st.y).padStart(5), 'op=' + JSON.stringify(st.op), 'play=' + JSON.stringify(st.playing), 'tf=' + JSON.stringify(st.tf));
    await p.screenshot({ path: path.join(OUT, 'v24-' + id + '.png') });
  }

  // 帧率：连续滚动 2.4s，数 rAF 帧数
  await p.evaluate(() => scrollTo(0, 0));
  await sleep(600);
  const fps = await p.evaluate(async () => {
    const total = document.documentElement.scrollHeight - innerHeight;
    let frames = 0, stop = false;
    const t0 = performance.now();
    (function tick() { if (stop) return; frames++; requestAnimationFrame(tick); })();
    const steps = 140;
    for (let i = 0; i <= steps; i++) {
      scrollTo(0, Math.round(total * (i / steps)));
      await new Promise(r => requestAnimationFrame(r));
    }
    await new Promise(r => setTimeout(r, 400));
    stop = true;
    return { frames, ms: Math.round(performance.now() - t0), fps: +(frames / ((performance.now() - t0) / 1000)).toFixed(1) };
  });
  console.log('\n--- 滚动帧率 ---');
  console.log(JSON.stringify(fps));

  // 横向溢出
  console.log('\n--- 溢出检查 ---');
  for (const w of [1920, 1440, 1280, 1024, 900, 768, 390, 360]) {
    await p.setViewportSize({ width: w, height: 900 });
    await sleep(420);
    const r = await p.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
    console.log(String(w).padStart(5), r.sw > r.cw + 1 ? ('溢出 ' + (r.sw - r.cw) + 'px') : 'ok');
  }

  // 轻量档（窄屏）是否只启用 3 个视角
  await p.setViewportSize({ width: 390, height: 844 });
  await p.goto(URL, { waitUntil: 'load' });
  await sleep(2600);
  const mob = await p.evaluate(() => {
    const el = document.getElementById('evidence');
    scrollTo(0, el.getBoundingClientRect().top + scrollY);
    return null;
  });
  await sleep(1600);
  const mobState = await p.evaluate(() => {
    const vs = [...document.querySelectorAll('.cam-layer')];
    return { op: vs.map(v => +(+getComputedStyle(v).opacity).toFixed(2)), loaded: vs.map(v => !!v.currentSrc) };
  });
  console.log('\n--- 轻量档 (390px, evidence) ---', JSON.stringify(mobState));
  await p.screenshot({ path: path.join(OUT, 'v24-mobile.png') });

  console.log('\n--- 错误 ---');
  console.log(errs.length ? errs.join('\n') : '无');
  await b.close();
})();
