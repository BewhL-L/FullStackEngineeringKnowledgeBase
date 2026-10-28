const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch({ headless:true, channel:'chrome', args:['--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport:{width:1440,height:900} });
  await p.goto('http://127.0.0.1:8811/issue-v26-flight.html',{waitUntil:'load'});
  await sleep(3200);
  const anchors = await p.evaluate(()=>["hero","fullstack","agent","retrieval","case","evidence"]
      .map(id=>{const e=document.getElementById(id);return Math.round(e.getBoundingClientRect().top+scrollY)}));
  console.log('anchors', anchors);
  const vh = 900, w = Math.min(520, Math.max(300, Math.round(vh*0.5)));
  for (let m=1;m<anchors.length;m++){
    const end = anchors[m], start = Math.max(anchors[m-1], end-w);
    for (const q of [0.0,0.35,0.5,0.65,1.0]) {
      const y = Math.round(start + (end-start)*q);
      await p.evaluate(v=>scrollTo(0,v), y);
      await sleep(1200);
      const s = await p.evaluate(()=>[...document.querySelectorAll('.cam-layer')].map(v=>v.style.opacity).join('|'));
      await p.screenshot({path:`_preview/_cut_${m}_${String(Math.round(q*100)).padStart(3,'0')}.png`});
      console.log(`cut${m} q=${q} y=${y} op=${s}`);
    }
  }
  await b.close();
})();
