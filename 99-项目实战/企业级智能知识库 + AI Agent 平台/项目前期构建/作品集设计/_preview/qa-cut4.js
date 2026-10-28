const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async()=>{
 const b=await chromium.launch({headless:true,channel:'chrome',args:['--autoplay-policy=no-user-gesture-required']});
 const p=await b.newPage({viewport:{width:1440,height:900}});
 await p.goto('http://127.0.0.1:8811/issue-v26-flight.html',{waitUntil:'load'});
 await sleep(3000);
 await p.evaluate(()=>document.documentElement.style.scrollBehavior='auto');
 const a = await p.evaluate(()=>["hero","fullstack","agent","retrieval","case","evidence"].map(id=>{const e=document.getElementById(id);return Math.round(e.getBoundingClientRect().top+scrollY)}));
 const vh=900, w=Math.min(460,Math.max(280,Math.round(vh*0.38)));
 for(const m of [1,3,4]){
   const end=a[m], start=Math.max(a[m-1], end-w);
   for(const q of [0.3,0.5,0.7]){
     await p.evaluate(v=>scrollTo(0,v), Math.round(start+(end-start)*q));
     await sleep(1100);
     await p.screenshot({path:`_preview/_c4_${m}_${Math.round(q*100)}.png`});
   }
 }
 const pr = await p.evaluate(()=>[...document.querySelectorAll('.cam-layer')].map(v=>v.playbackRate+'/'+(v.paused?'P':'R')));
 console.log('rate/paused:',pr.join(' '));
 await b.close();
})();
