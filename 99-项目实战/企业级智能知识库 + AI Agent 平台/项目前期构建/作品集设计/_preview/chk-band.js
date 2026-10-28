const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
function relL(r,g,b){const f=c=>{c/=255;return c<=0.03928?c/12.92:Math.pow((c+0.055)/1.055,2.4)};return .2126*f(r)+.7152*f(g)+.0722*f(b)}
const ratio=(a,b)=>(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
const T={paper:relL(255,253,246),p2:relL(239,233,218),p3:relL(222,216,201)};
(async () => {
  const b = await chromium.launch({ headless:true, channel:'chrome', args:['--autoplay-policy=no-user-gesture-required'] });
  for (const W of [1440, 1920]) {
    const p = await b.newPage({ viewport:{width:W,height:900} });
    await p.goto('http://127.0.0.1:8791/issue-v24-camera.html',{waitUntil:'load'});
    await sleep(2500);
    const band = await p.evaluate(()=>{const e=document.querySelector('.cam-band');const r=e.getBoundingClientRect();
      return {l:Math.round(r.left),r:Math.round(r.right),w:Math.round(r.width),bg:getComputedStyle(e).backgroundColor};});
    console.log('\n['+W+'] 保护带', JSON.stringify(band));
    for (const id of ['hero','retrieval','evidence']) {
      await p.evaluate(v=>{const e=document.getElementById(v);scrollTo(0,e.getBoundingClientRect().top+scrollY-(v==='hero'?0:60))},id);
      await sleep(1500);
      await p.evaluate(()=>{document.querySelectorAll('main,.nav,.skip').forEach(e=>e.style.visibility='hidden')});
      await sleep(240);
      const buf = await p.screenshot();
      await p.evaluate(()=>{document.querySelectorAll('main,.nav,.skip').forEach(e=>e.style.visibility='')});
      const s = await p.evaluate(async b64=>{
        const img=new Image(); await new Promise(r=>{img.onload=r;img.src='data:image/png;base64,'+b64});
        const c=document.createElement('canvas');c.width=img.width;c.height=img.height;
        const x=c.getContext('2d');x.drawImage(img,0,0);
        const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};
        const reg=(x0,x1)=>{const d=x.getImageData(x0,90,x1-x0,c.height-180).data;let s=0,n=0,mx=0;
          for(let i=0;i<d.length;i+=4){const L=.2126*f(d[i])+.7152*f(d[i+1])+.0722*f(d[i+2]);s+=L;n++;if(L>mx)mx=L}return{avg:s/n,max:mx}};
        var a=Math.max(20,Math.round((c.width-1400)/2)+20), b=Math.min(c.width-20,Math.round((c.width+1400)/2)-20), w=b-a;
        return {L:reg(a,Math.round(a+w*.33)),M:reg(Math.round(a+w*.34),Math.round(a+w*.66)),R:reg(Math.round(a+w*.67),b)};
      }, buf.toString('base64'));
      const worst=Math.max(s.L.avg,s.M.avg,s.R.avg), worstMax=Math.max(s.L.max,s.M.max,s.R.max);
      console.log('  '+id.padEnd(10)+' 平均 左'+s.L.avg.toFixed(3)+' 中'+s.M.avg.toFixed(3)+' 右'+s.R.avg.toFixed(3)
        +' | 最亮点'+worstMax.toFixed(3)
        +' | 对比度(按最亮) '+Object.keys(T).map(k=>k+' '+ratio(T[k],worstMax).toFixed(1)).join(' '));
    }
    await p.close();
  }
  await b.close();
})();
