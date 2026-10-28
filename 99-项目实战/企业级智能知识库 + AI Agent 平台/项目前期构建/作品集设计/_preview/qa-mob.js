const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async()=>{
 const b=await chromium.launch({headless:true,channel:'chrome',args:['--autoplay-policy=no-user-gesture-required']});
 const p=await b.newPage({viewport:{width:390,height:844},deviceScaleFactor:2});
 const errs=[]; p.on('pageerror',e=>errs.push(e.message));
 await p.goto('http://127.0.0.1:8811/issue-v26-flight.html',{waitUntil:'load'});
 await sleep(3200);
 await p.evaluate(()=>document.documentElement.style.scrollBehavior='auto');
 console.log('errs',errs.length?errs:'none');
 const a = await p.evaluate(()=>["hero","fullstack","agent","retrieval","case","evidence"].map(id=>{const e=document.getElementById(id);return Math.round(e.getBoundingClientRect().top+scrollY)}));
 console.log('anchors',a);
 for (let m=0;m<a.length;m++){
   await p.evaluate(v=>scrollTo(0,v), a[m]+20);
   await sleep(1300);
   const st=await p.evaluate(()=>[...document.querySelectorAll('.cam-layer')].map(v=>v.style.opacity||'-').join('|'));
   await p.screenshot({path:`_preview/_mob_${m}.png`});
   console.log('stage',m,'op',st);
 }
 await b.close();
})();
