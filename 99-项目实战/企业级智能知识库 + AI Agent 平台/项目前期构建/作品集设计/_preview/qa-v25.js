const { chromium } = require('playwright');
const path = require('path');
const OUT = __dirname;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const U = f => 'http://127.0.0.1:8791/' + f;

(async () => {
  const b = await chromium.launch({ headless: true, channel: 'chrome', args: ['--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  const errs = [];
  p.on('pageerror', e => errs.push('pageerror: ' + e.message));
  p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });

  await p.goto(U('issue-v25-glass.html'), { waitUntil: 'load' });
  await sleep(2600);

  // ---- ① 图版是否彻底移除 + hero 布局 ----
  const dom = await p.evaluate(() => ({
    plate: document.querySelectorAll('.plate,.plate-frame,.plate-glow,.stage,.sea-glow,.wipe,.veil').length,
    heroCols: getComputedStyle(document.querySelector('.hero-inner')).gridTemplateColumns,
    heroH: Math.round(document.querySelector('.hero').getBoundingClientRect().height),
    copyW: Math.round(document.querySelector('.hero-copy').getBoundingClientRect().width),
    ledgerW: Math.round(document.querySelector('.hero-ledger').getBoundingClientRect().width),
    q: document.documentElement.getAttribute('data-q'),
    hz: document.documentElement.getAttribute('data-hz'),
    surfBg: getComputedStyle(document.querySelector('.surf')).backgroundColor,
    surfFilter: getComputedStyle(document.querySelector('.surf')).backdropFilter,
    navFilter: getComputedStyle(document.querySelector('.nav')).backdropFilter,
    radius: getComputedStyle(document.querySelector('.surf')).borderRadius,
    pad: getComputedStyle(document.querySelector('.surf')).padding
  }));
  console.log('--- ① 结构与材质 ---');
  console.log(JSON.stringify(dom, null, 1));

  // ---- ② 滚动帧时间分布 + longtask ----
  await p.evaluate(() => scrollTo(0, 0));
  await sleep(600);
  const perf = await p.evaluate(async () => {
    const long = [];
    try {
      new PerformanceObserver(l => l.getEntries().forEach(e => long.push(Math.round(e.duration))))
        .observe({ entryTypes: ['longtask'] });
    } catch (e) { }
    const total = document.documentElement.scrollHeight - innerHeight;
    const frames = [];
    let last = performance.now(), stop = false;
    (function tick(t) { frames.push(t - last); last = t; if (!stop) requestAnimationFrame(tick); })(performance.now());
    const steps = 180;
    for (let i = 0; i <= steps; i++) {
      scrollTo(0, Math.round(total * i / steps));
      await new Promise(r => requestAnimationFrame(r));
    }
    await new Promise(r => setTimeout(r, 500));
    stop = true;
    const f = frames.slice(3).filter(x => x > 0).sort((a, b) => a - b);
    const q = k => f.length ? +f[Math.min(f.length - 1, Math.floor(f.length * k))].toFixed(2) : -1;
    return {
      帧数: f.length, 中位帧时: q(.5), p95帧时: q(.95), 最大帧时: q(1),
      超8_3ms: f.filter(x => x > 8.34).length, 超16_7ms: f.filter(x => x > 16.7).length,
      longtask: long.length, longtask最长: long.length ? Math.max(...long) : 0
    };
  });
  console.log('\n--- ② 滚动帧时间（毫秒，越小越稳）---');
  console.log(JSON.stringify(perf));

  // ---- ③ 视角过渡：等长窗口 + 不透明度和恒为 1 ----
  console.log('\n--- ③ 过渡窗口与亮度连续性 ---');
  const sweep = await p.evaluate(async () => {
    const vs = [...document.querySelectorAll('.cam-layer')];
    const total = document.documentElement.scrollHeight - innerHeight;
    const rows = [];
    for (let i = 0; i <= 140; i++) {
      const y = Math.round(total * i / 140);
      scrollTo(0, y);
      await new Promise(r => setTimeout(r, 70));
      const op = vs.map(v => +getComputedStyle(v).opacity);
      rows.push({ y, op, sum: op.reduce((a, c) => a + c, 0), top: op.indexOf(Math.max(...op)) });
    }
    return rows;
  });
  const sums = sweep.map(r => r.sum);
  console.log('  不透明度和  min=' + Math.min(...sums).toFixed(3) + '  max=' + Math.max(...sums).toFixed(3) + '  (应恒为 1)');
  // 统计每个边界的过渡行程
  const bounds = [];
  let cur = sweep[0].top;
  for (const r of sweep) { if (r.top !== cur) { bounds.push(r.y); cur = r.top; } }
  console.log('  视角接管位置(px):', bounds.join(', '));

  // 每条过渡的行程宽度：不透明度从 0.02 走到 0.98 所占的滚动像素
  const widths = [];
  for (let n = 0; n < 5; n++) {
    const on = sweep.filter(r => r.op[n] > 0.02 && r.op[n] < 0.98);
    if (on.length) widths.push(n + ': ' + (on[on.length - 1].y - on[0].y) + 'px');
  }
  console.log('  各视角过渡行程:', widths.join('  '));

  // 单次过渡采样：确认是平滑插值而非跳变
  const one = await p.evaluate(async () => {
    const vs = [...document.querySelectorAll('.cam-layer')];
    const el = document.getElementById('retrieval');
    const target = Math.round(el.getBoundingClientRect().top + scrollY);
    const out = [];
    for (let i = 0; i <= 24; i++) {
      scrollTo(0, target - 700 + Math.round(1000 * i / 24));
      await new Promise(r => setTimeout(r, 70));
      out.push(+(+getComputedStyle(vs[2]).opacity).toFixed(3));
    }
    return out;
  });
  console.log('  V3 入场曲线采样:', one.join(' '));

  // ---- ④ 屏幕截图 ----
  for (const id of ['hero', 'fullstack', 'retrieval', 'evidence', 'contact']) {
    await p.evaluate(v => {
      const el = document.getElementById(v);
      scrollTo(0, el.getBoundingClientRect().top + scrollY - (v === 'hero' ? 0 : 40));
    }, id);
    await sleep(1500);
    await p.screenshot({ path: path.join(OUT, 'v25-' + id + '.png') });
  }

  // ---- ⑤ 溢出 ----
  console.log('\n--- ⑤ 溢出 ---');
  const of = [];
  for (const w of [1920, 1440, 1280, 1024, 900, 768, 390, 360]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 } });
    await pg.goto(U('issue-v25-glass.html'), { waitUntil: 'load' });
    await sleep(1300);
    await pg.evaluate(() => scrollTo(0, document.documentElement.scrollHeight));
    await sleep(700);
    const r = await pg.evaluate(() => ({ s: document.documentElement.scrollWidth, c: document.documentElement.clientWidth }));
    of.push(w + (r.s - r.c > 1 ? ':溢出' + (r.s - r.c) : ':ok'));
    await pg.close();
  }
  console.log('  ' + of.join('  '));

  console.log('\n--- 错误 ---');
  console.log(errs.length ? errs.join('\n') : '无');
  await b.close();
})();
