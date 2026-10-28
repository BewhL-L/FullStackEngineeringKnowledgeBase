const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
function relL(r,g,b){const f=c=>{c/=255;return c<=0.03928?c/12.92:Math.pow((c+0.055)/1.055,2.4)};return .2126*f(r)+.7152*f(g)+.0722*f(b)}
const ratio=(a,b)=>(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
(async () => {
  const b = await chromium.launch({ headless:true, channel:'chrome', args:['--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport:{width:1440,height:900} });
  await p.goto('http://127.0.0.1:8791/issue-v25-glass.html',{waitUntil:'load'});
  await sleep(2600);
  await p.addStyleTag({content:'html{scroll-behavior:auto!important}'});
  for (const id of ['fullstack','retrieval']) {
    await p.evaluate(v=>{const e=document.getElementById(v);scrollTo(0,e.getBoundingClientRect().top+scrollY-40)},id);
    await sleep(1500);
    const r = await p.evaluate(()=>{
      const el=document.querySelectorAll('.surf')[0];
      const rc=el.getBoundingClientRect();
      return {x:Math.round(rc.left),y:Math.round(rc.top),w:Math.round(rc.width),h:Math.round(rc.height)};
    });
    // 隐藏文字，量模块内部底色亮度
    await p.evaluate(()=>{document.querySelectorAll('.surf *').forEach(e=>e.style.visibility='hidden')});
    await sleep(300);
    const buf = await p.screenshot({clip:{x:r.x+6,y:Math.max(0,r.y+6),width:Math.min(r.w-12,600),height:Math.min(r.h-12,400)}});
    await p.evaluate(()=>{document.querySelectorAll('.surf *').forEach(e=>e.style.visibility='')});
    const L = await p.evaluate(async b64=>{
      const img=new Image(); await new Promise(r=>{img.onload=r;img.src='data:image/png;base64,'+b64});
      const c=document.createElement('canvas');c.width=img.width;c.height=img.height;
      const x=c.getContext('2d');x.drawImage(img,0,0);
      const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};
      const d=x.getImageData(0,0,c.width,c.height).data;let s=0,n=0,mx=0;
      for(let i=0;i<d.length;i+=4){const L=.2126*f(d[i])+.7152*f(d[i+1])+.0722*f(d[i+2]);s+=L;n++;if(L>mx)mx=L}
      return {avg:s/n,max:mx,size:c.width+'x'+c.height};
    }, buf.toString('base64'));
    const paper=relL(255,253,246), p2=relL(239,233,218), p3=relL(222,216,201);
    console.log(id.padEnd(10)+' 模块'+L.size+' 内底 L='+L.avg.toFixed(3)+' 最亮'+L.max.toFixed(3)
      +' | 对比度 paper '+ratio(paper,L.avg).toFixed(1)+' p2 '+ratio(p2,L.avg).toFixed(1)+' p3 '+ratio(p3,L.avg).toFixed(1)
      +' | 最坏点 p3 '+ratio(p3,L.max).toFixed(1));
    await p.screenshot({path:__dirname+'/v25g-'+id+'.png'});
  }
  await b.close();
})();
