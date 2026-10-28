const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch({ headless:true, channel:'chrome', args:['--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport:{width:1440,height:900} });
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('http://127.0.0.1:8811/issue-v26-flight.html',{waitUntil:'load'});
  await sleep(3500);

  // 1) 连续性：以 8px 步进推进 2600px，记录每层 scale / 位移 / 不透明度
  const rows = await p.evaluate(async ()=>{
    document.documentElement.style.scrollBehavior='auto';
    const out=[]; const layers=[...document.querySelectorAll('.cam-layer')];
    const read=()=>layers.map(v=>{
      const m=new DOMMatrixReadOnly(getComputedStyle(v).transform);
      return {s:+m.a.toFixed(4), y:+m.f.toFixed(2), o:+(+getComputedStyle(v).opacity).toFixed(3)};
    });
    for(let y=0;y<=2600;y+=8){
      scrollTo(0,y);
      await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
      out.push({y:Math.round(scrollY),v:read()});
    }
    return out;
  });

  let worstS=0, worstO=0, worstY=0, at=null;
  for(let i=1;i<rows.length;i++){
    const a=rows[i-1].v, c=rows[i].v;
    for(let k=0;k<a.length;k++){
      if(a[k].o<=0.01&&c[k].o<=0.01) continue;   // 不可见图层的复位不算跳变
      const ds=Math.abs(c[k].s-a[k].s), dy=Math.abs(c[k].y-a[k].y), doo=Math.abs(c[k].o-a[k].o);
      if(ds>worstS){worstS=ds; at={k,prop:'scale',y:rows[i].y,from:a[k].s,to:c[k].s};}
      if(dy>worstY) worstY=dy;
      if(doo>worstO) worstO=doo;
    }
  }
  console.log('errs:', errs.length?errs.join('|'):'none');
  console.log('8px 步进内最大变化 → scale:',worstS.toFixed(4),' translate%:',worstY.toFixed(3),' opacity:',worstO.toFixed(3));
  console.log('scale 跳变位置:',JSON.stringify(at));
  console.log('末帧 opacity:', rows[rows.length-1].v.map(v=>v.o).join('|'));

  // 2) 首屏自动播放下，测一屏粗滚的帧间隔
  await p.evaluate(()=>scrollTo(0,0)); await sleep(600);
  const fps = await p.evaluate(async ()=>{
    const t=[]; let y=0;
    await new Promise(res=>{
      const t0=performance.now();
      function step(now){
        t.push(now);
        y+=9; scrollTo(0,y);
        if(now-t0<1400) requestAnimationFrame(step); else res();
      }
      requestAnimationFrame(step);
    });
    const d=[]; for(let i=1;i<t.length;i++) d.push(t[i]-t[i-1]);
    d.sort((a,b)=>a-b);
    return {frames:t.length, median:+d[Math.floor(d.length/2)].toFixed(1), p95:+d[Math.floor(d.length*0.95)].toFixed(1), max:+d[d.length-1].toFixed(1)};
  });
  console.log('滚动帧间隔(ms):', JSON.stringify(fps));
  await b.close();
})();
