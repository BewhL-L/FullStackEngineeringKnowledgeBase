const { chromium } = require('playwright');
const path = require('path');
const { pathToFileURL } = require('url');

(async () => {
  const b = await chromium.launch({
    channel: 'chrome', headless: true,
    args: ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader', '--ignore-gpu-blocklist']
  });

  // ---- dir 02 ----
  let p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  const err2 = []; p.on('pageerror', e => err2.push(e.message));
  p.on('console', m => { if (m.type() === 'error') err2.push('console: ' + m.text()); });
  await p.goto(pathToFileURL(path.join(__dirname, '..', 'dir-02-explode.html')).href);
  await p.waitForTimeout(2500);
  await p.screenshot({ path: path.join(__dirname, 'dir02-idle.png') });
  await p.hover('[data-i="2"]');
  await p.waitForTimeout(1400);
  await p.screenshot({ path: path.join(__dirname, 'dir02-hover.png') });
  console.log('dir02 errors:', err2.length, err2.slice(0, 4).join(' | '));
  await p.close();

  // ---- dir 03 ----
  p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  const err3 = []; p.on('pageerror', e => err3.push(e.message));
  p.on('console', m => { if (m.type() === 'error') err3.push('console: ' + m.text()); });
  await p.goto(pathToFileURL(path.join(__dirname, '..', 'dir-03-field.html')).href);
  await p.waitForTimeout(2600);
  await p.screenshot({ path: path.join(__dirname, 'dir03-searched.png') });
  console.log('dir03 errors:', err3.length, err3.slice(0, 4).join(' | '));
  console.log('dir03 stat:', await p.textContent('#sv'));
  await p.close();

  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
