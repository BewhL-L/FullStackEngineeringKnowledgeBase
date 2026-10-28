const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch({ headless:true, channel:'chrome', args:['--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport:{width:1440,height:900} });
  await p.goto('http://127.0.0.1:8791/issue-v25-glass.html',{waitUntil:'load'});
  await sleep(2800);
  const a = await p.evaluate(()=>['hero','fullstack','retrieval','case','evidence','contact']
    .map(id=>{const e=document.getElementById(id);return id+'='+(e?Math.round(e.getBoundingClientRect().top+scrollY):-1)}));
  console.log('锚点', a.join(' '), '| maxScroll', await p.evaluate(()=>document.documentElement.scrollHeight-innerHeight));
  for (const y of [0,400,700,1000,1400,1900,2300,2700,3000,3500,4000,4500,5000,5241]) {
    await p.evaluate(v=>scrollTo(0,v), y);
    await sleep(420);
    const op = await p.evaluate(()=>[...document.querySelectorAll('.cam-layer')].map(v=>(+getComputedStyle(v).opacity).toFixed(2)));
    console.log('  y='+String(y).padStart(4)+'  ['+op.join(' ')+']');
  }
  await b.close();
})();
