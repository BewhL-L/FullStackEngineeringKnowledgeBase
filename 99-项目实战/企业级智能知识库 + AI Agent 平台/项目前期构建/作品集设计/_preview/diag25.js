const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch({ headless:true, channel:'chrome', args:['--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport:{width:1440,height:900} });
  await p.goto('http://127.0.0.1:8791/issue-v25-glass.html',{waitUntil:'load'});
  await sleep(2800);
  const meta = await p.evaluate(()=>{
    const ids=['hero','fullstack','agent','retrieval','case','evidence','contact'];
    return {total:document.documentElement.scrollHeight-innerHeight, vh:innerHeight,
      anchors:ids.map(id=>{const e=document.getElementById(id);return e?Math.round(e.getBoundingClientRect().top+scrollY):-1}),
      ready:[...document.querySelectorAll('.cam-layer')].map(v=>v.readyState)};
  });
  console.log('total',meta.total,'vh',meta.vh,'anchors',JSON.stringify(meta.anchors),'readyState',JSON.stringify(meta.ready));
  const rows = await p.evaluate(async (total)=>{
    const vs=[...document.querySelectorAll('.cam-layer')];
    const out=[];
    for(let i=0;i<=28;i++){
      const y=Math.round(total*i/28);
      scrollTo(0,y);
      await new Promise(r=>requestAnimationFrame(r));
      await new Promise(r=>requestAnimationFrame(r));
      out.push(y+': ['+vs.map(v=>(+getComputedStyle(v).opacity).toFixed(2)).join(' ')+']');
    }
    return out;
  }, meta.total);
  rows.forEach(r=>console.log('  '+r));
  await b.close();
})();
