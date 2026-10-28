const { chromium } = require('playwright');
(async()=>{
 const b=await chromium.launch({headless:true,channel:'chrome'});
 const p=await b.newPage();
 await p.goto('http://127.0.0.1:8811/assets/beach-field.jpg');
 const r=await p.evaluate(async()=>{
   const names=['v1-nadir','v2-oblique','v3-eyelevel','v4-side','v5-macro'];
   const out=[];
   for(const n of names){
     const v=document.createElement('video');
     v.src='/bg/'+n+'.mp4'; v.preload='metadata'; v.muted=true;
     await new Promise(res=>{v.onloadedmetadata=res; v.onerror=res; setTimeout(res,8000)});
     out.push({n,dur:+v.duration.toFixed(2),w:v.videoWidth,h:v.videoHeight});
   }
   return out;
 });
 console.log(r);
 await b.close();
})();
