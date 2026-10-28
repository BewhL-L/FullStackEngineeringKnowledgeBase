const { chromium } = require('playwright');
(async()=>{
 const b=await chromium.launch({headless:true,channel:'chrome',args:['--autoplay-policy=no-user-gesture-required']});
 const p=await b.newPage({viewport:{width:960,height:540}});
 await p.goto('http://127.0.0.1:8811/assets/beach-field.jpg');
 for (const n of ['v1-nadir','v2-oblique','v3-eyelevel','v4-side','v5-macro']){
   await p.evaluate(async(nm)=>{
     document.body.innerHTML='';
     const v=document.createElement('video');
     v.id='V'; v.src='/bg/'+nm+'.mp4'; v.muted=true; v.playsInline=true; v.loop=false;
     v.style.cssText='position:fixed;inset:0;width:100vw;height:100vh;object-fit:cover';
     document.body.appendChild(v);
     await new Promise(r=>{v.onloadeddata=r; setTimeout(r,9000)});
     await v.play();
   },n);
   let last=0;
   for (const t of [0.15, 2.0, 4.0, 6.3]){
     await p.waitForFunction(t=>{const v=document.getElementById('V'); return v.currentTime>=t}, t, {timeout:12000});
     await p.evaluate(()=>{document.getElementById('V').pause()});
     await new Promise(r=>setTimeout(r,260));
     await p.screenshot({path:`_preview/_g_${n}_${String(Math.round(t*10)).padStart(3,'0')}.png`});
     await p.evaluate(()=>{document.getElementById('V').play()});
   }
   console.log('ok',n);
 }
 await b.close();
})();
