const { chromium } = require('playwright');
const path = require('path');
const { pathToFileURL } = require('url');
const pageUrl = pathToFileURL(path.join(__dirname, '..', 'issue-single.html')).href;

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page.goto(pageUrl);
  await page.waitForTimeout(1200);
  const info = await page.evaluate(() => {
    const screen = document.querySelector('.screen.on');
    const cs = getComputedStyle(screen);
    const stage = document.querySelector('.stage');
    const r = screen.getBoundingClientRect();
    return {
      screenClass: screen.className,
      position: cs.position,
      top: cs.top,
      bottom: cs.bottom,
      height: cs.height,
      transform: cs.transform,
      rect: { top: r.top, bottom: r.bottom, height: r.height },
      stageRect: stage.getBoundingClientRect().toJSON(),
      navH: getComputedStyle(document.documentElement).getPropertyValue('--nav-h'),
      dockH: getComputedStyle(document.documentElement).getPropertyValue('--dock-h'),
      scrollHeight: document.documentElement.scrollHeight,
      innerHeight: window.innerHeight
    };
  });
  console.log(info);
  await browser.close();
})().catch(e => { console.error(e); process.exitCode = 1; });
