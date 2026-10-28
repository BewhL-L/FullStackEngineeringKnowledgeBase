const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch({ headless:true, channel:'chrome', args:['--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport:{width:1440,height:900} });
  p.on('pageerror',e=>console.log('ERR',e.message));
  await p.goto('http://127.0.0.1:8791/issue-v25-glass.html',{waitUntil:'load'});
  await sleep(2600);
  for (const y of [0, 1872, 3000, 5000]) {
    await p.evaluate(v=>scrollTo(0,v), y);
    await sleep(900);
    const d = await p.evaluate(()=>({...window.__dbg(),
      op:[...document.querySelectorAll('.cam-layer')].map(v=>+(+getComputedStyle(v).opacity).toFixed(3))}));
    console.log(JSON.stringify(d));
  }
  await b.close();
})();
