const { chromium } = require('playwright');
const fs=require('fs');
(async()=>{
 const b=await chromium.launch({headless:true,channel:'chrome'});
 const p=await b.newPage({viewport:{width:1280,height:720}});
 await p.goto('http://127.0.0.1:8811/assets/beach-field.jpg');
 const names=['v1-nadir','v2-oblique','v3-eyelevel','v4-side','v5-macro'];
 const ts=[0.05,3.3,6.45];
 for(const n of names){
   await p.evaluate(async(nm)=>{
     document.body.innerHTML='';
     const v=document.createElement('video');
     v.id='V'; v.src='/bg/'+nm+'.mp4'; v.muted=true; v.playsInline=true;
     v.style.cssText='position:fixed;inset:0;width:100vw;height:100vh;object-fit:cover';
     document.body.appendChild(v);
     await new Promise(r=>{v.onloadeddata=r; setTimeout(r,8000)});
   },n);
   for(let i=0;i<ts.length;i++){
     await p.evaluate(async(t)=>{
       const v=document.getElementById('V');
       await new Promise(r=>{ v.onseeked=r; v.currentTime=t; setTimeout(r,1500); });
     },ts[i]);
     await new Promise(r=>setTimeout(r,300));
     await p.screenshot({path:`_preview/_f_${n}_${i}.png`});
   }
   console.log('ok',n);
 }
 await b.close();
})();
