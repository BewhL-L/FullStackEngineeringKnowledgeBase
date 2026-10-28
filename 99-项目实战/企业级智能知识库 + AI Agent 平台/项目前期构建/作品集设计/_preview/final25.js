const { chromium } = require('playwright');
const path = require('path');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch({ headless:true, channel:'chrome', args:['--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport:{width:1440,height:900} });
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
  await p.goto('http://127.0.0.1:8791/issue-v25-glass.html',{waitUntil:'load'});
  await sleep(2600);
  await p.addStyleTag({content:'html{scroll-behavior:auto!important}'});

  // 精确扫描：每条过渡 0.02→0.98 的实际行程
  const total = await p.evaluate(()=>document.documentElement.scrollHeight-innerHeight);
  const rows = await p.evaluate(async (total)=>{
    const vs=[...document.querySelectorAll('.cam-layer')]; const out=[];
    for(let y=0;y<=total;y+=25){
      scrollTo(0,y);
      await new Promise(r=>setTimeout(r,26));
      out.push({y,op:vs.map(v=>+getComputedStyle(v).opacity)});
    }
    return out;
  }, total);
  console.log('--- 过渡行程（0.02→0.98 的滚动像素）---');
  for(let n=0;n<5;n++){
    const up = rows.filter(r=>r.op[n]>0.02&&r.op[n]<0.98);
    if(up.length){
      // 只取单调上升段（排除离场段）
      let s=up[0].y, e=up[up.length-1].y;
      console.log('  V'+(n+1)+': '+s+' → '+e+'  行程 '+(e-s)+'px');
    }
  }
  const sums = rows.map(r=>r.op.reduce((a,c)=>a+c,0));
  console.log('  不透明度和 min='+Math.min(...sums).toFixed(3)+' max='+Math.max(...sums).toFixed(3));

  // 帧时间（禁用平滑，真实连续滚动）
  await p.evaluate(()=>scrollTo(0,0)); await sleep(700);
  const perf = await p.evaluate(async ()=>{
    const long=[]; try{new PerformanceObserver(l=>l.getEntries().forEach(e=>long.push(Math.round(e.duration)))).observe({entryTypes:['longtask']});}catch(e){}
    const total=document.documentElement.scrollHeight-innerHeight, fr=[];
    let last=performance.now(), stop=false;
    (function t(x){fr.push(x-last);last=x;if(!stop)requestAnimationFrame(t);})(performance.now());
    for(let i=0;i<=200;i++){scrollTo(0,Math.round(total*i/200));await new Promise(r=>requestAnimationFrame(r));}
    await new Promise(r=>setTimeout(r,400)); stop=true;
    const f=fr.slice(4).filter(x=>x>0).sort((a,b)=>a-b), q=k=>+f[Math.min(f.length-1,Math.floor(f.length*k))].toFixed(2);
    return {帧数:f.length,中位:q(.5),p95:q(.95),p99:q(.99),最大:q(1),超8_3ms:f.filter(x=>x>8.34).length,超16_7ms:f.filter(x=>x>16.7).length,longtask:long.length};
  });
  console.log('\n--- 滚动帧时间(ms) ---\n  '+JSON.stringify(perf));

  for(const id of ['hero','fullstack','retrieval','evidence','contact']){
    await p.evaluate(v=>{const e=document.getElementById(v);scrollTo(0,e.getBoundingClientRect().top+scrollY-(v==='hero'?0:40))},id);
    await sleep(1400);
    await p.screenshot({path:path.join(__dirname,'v25-'+id+'.png')});
  }
  console.log('\n错误:', errs.length?errs.join(' | '):'无');
  await b.close();
})();
