const { chromium } = require('playwright');
const path = require('path');

const srgb = c => (c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
const lum = ([r, g, b]) => 0.2126 * srgb(r / 255) + 0.7152 * srgb(g / 255) + 0.0722 * srgb(b / 255);
const cr = (a, b) => {
  const [l1, l2] = [lum(a), lum(b)].sort((x, y) => y - x);
  return +( (l1 + 0.05) / (l2 + 0.05) ).toFixed(2);
};
const parse = s => s.match(/\d+(\.\d+)?/g).slice(0, 3).map(Number);

(async () => {
  const b = await chromium.launch({ channel: 'chrome', headless: true });
  const url = 'http://127.0.0.1:8771/issue-v21-plate.html';
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.goto(url, { waitUntil: 'networkidle' });
  await p.waitForTimeout(1200);

  // 1. 证据面板标签切换
  await p.evaluate(() => scrollTo(0, document.body.scrollHeight));
  await p.click('[data-evidence="tables"]');
  await p.waitForTimeout(400);
  const panel = await p.evaluate(() => {
    const chain = document.querySelector('[data-ev-panel="chain"]');
    const tables = document.querySelector('[data-ev-panel="tables"]');
    return { chainVisible: !!chain.offsetParent, tablesVisible: !!tables.offsetParent };
  });
  console.log('PANEL tables-tab:', JSON.stringify(panel));
  await p.click('[data-ev-tab="chain"]');
  await p.waitForTimeout(300);
  const panel2 = await p.evaluate(() => {
    const chain = document.querySelector('[data-ev-panel="chain"]');
    const tables = document.querySelector('[data-ev-panel="tables"]');
    return { chainVisible: !!chain.offsetParent, tablesVisible: !!tables.offsetParent };
  });
  console.log('PANEL chain-tab:', JSON.stringify(panel2));
  await p.keyboard.press('Escape');
  await p.waitForTimeout(250);

  // 2. 对比度
  const contrasts = await p.evaluate(() => {
    const bg = getComputedStyle(document.body).backgroundColor;
    const pick = sel => {
      const el = document.querySelector(sel);
      if (!el) return null;
      const s = getComputedStyle(el);
      return { color: s.color, size: s.fontSize, weight: s.fontWeight, opacity: s.opacity };
    };
    return {
      bg,
      body: pick('.hero-lede'),
      note: pick('.hero-meta'),
      k: pick('.k'),
      railI: pick('.rail i'),
      railSpan: pick('.rail span'),
      archMt: pick('.arch-row .mt'),
      logTime: pick('.log-row .time'),
      evFoot: pick('.ev-foot p'),
      leadP: pick('.lead p'),
      cmpBefore: pick('.before .cmp-step p'),
      plateCap: pick('.plate-cap span')
    };
  });
  const bgc = parse(contrasts.bg);
  console.log('BG', contrasts.bg);
  for (const [k, v] of Object.entries(contrasts)) {
    if (k === 'bg' || !v) continue;
    console.log('  ' + k.padEnd(12), v.size.padStart(6), 'w' + v.weight, 'op' + v.opacity, '=>', cr(parse(v.color), bgc) + ':1');
  }

  // 3. 横向溢出
  for (const w of [1024, 900, 768, 390, 360]) {
    const q = await b.newPage({ viewport: { width: w, height: 800 } });
    await q.goto(url, { waitUntil: 'networkidle' });
    await q.waitForTimeout(700);
    const r = await q.evaluate(() => ({
      overflow: document.documentElement.scrollWidth - innerWidth,
      heroH: Math.round(document.querySelector('.hero').getBoundingClientRect().height)
    }));
    console.log('W' + w, JSON.stringify(r));
    await q.close();
  }

  // 4. 交互
  await p.evaluate(() => { const el = document.getElementById('fullstack'); scrollTo(0, el.getBoundingClientRect().top + scrollY - 70); });
  await p.waitForTimeout(400);
  await p.click('[data-stack="3"]');
  await p.waitForTimeout(200);
  const insp = await p.evaluate(() => document.getElementById('inspectorTitle').textContent);
  console.log('arch click ->', insp);

  await p.evaluate(() => { const el = document.getElementById('retrieval'); scrollTo(0, el.getBoundingClientRect().top + scrollY - 70); });
  await p.waitForTimeout(400);
  await p.fill('.js-q', '评测 指标');
  await p.waitForTimeout(500);
  const res = await p.evaluate(() => ({
    count: document.querySelector('.js-count').textContent,
    answer: document.querySelector('.js-answer').textContent.slice(0, 24),
    rows: document.querySelectorAll('.result').length
  }));
  console.log('search ->', JSON.stringify(res));

  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
