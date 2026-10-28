const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch({ headless:true, channel:'chrome', args:['--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport:{width:1440,height:900} });
  await p.goto('http://127.0.0.1:8811/issue-v25-glass.html',{waitUntil:'load'});
  await sleep(3000);
  const info = await p.evaluate(()=>{
    const band=document.querySelector('.cam-band').getBoundingClientRect();
    const cs=getComputedStyle(document.querySelector('.cam-band'));
    return {band:{l:Math.round(band.left),w:Math.round(band.width)},bg:cs.backgroundColor,
      h:document.documentElement.scrollHeight, vh:innerHeight,
      layers:[...document.querySelectorAll('.cam-layer')].map(v=>({src:v.dataset.src,op:getComputedStyle(v).opacity,tf:getComputedStyle(v).transform,ready:v.readyState}))};
  });
  console.log(JSON.stringify(info,null,1));
  // 采样滚动位置
  const H = info.h - info.vh;
  for (const f of [0,0.12,0.2,0.28,0.36,0.46,0.56,0.66,0.78,0.9,1]) {
    const y = Math.round(H*f);
    await p.evaluate(v=>scrollTo(0,v), y);
    await sleep(900);
    const st = await p.evaluate(()=>[...document.querySelectorAll('.cam-layer')].map(v=>+getComputedStyle(v).opacity.slice(0,5)));
    await p.screenshot({path:`_preview/_cam_${String(Math.round(f*100)).padStart(3,'0')}.png`});
    console.log(f.toFixed(2), y, 'opacity', st.join(' | '));
  }
  await b.close();
})();
