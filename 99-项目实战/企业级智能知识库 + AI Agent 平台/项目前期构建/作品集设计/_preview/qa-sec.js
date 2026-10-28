const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async()=>{
 const b=await chromium.launch({headless:true,channel:'chrome',args:['--autoplay-policy=no-user-gesture-required']});
 for(const V of [{w:1440,h:900,t:'d'},{w:844,h:1086,t:'p'}]){
  const p=await b.newPage({viewport:{width:V.w,height:V.h}});
  await p.goto('http://127.0.0.1:8811/issue-v26-flight.html',{waitUntil:'load'});
  await sleep(3000);
  await p.evaluate(()=>document.documentElement.style.scrollBehavior='auto');
  for(const id of ['evidence','contact','case','retrieval']){
    await p.evaluate(i=>{const e=document.getElementById(i);scrollTo(0,e.getBoundingClientRect().top+scrollY-40)},id);
    await sleep(1400);
    await p.screenshot({path:`_preview/_sec_${V.t}_${id}.png`});
  }
  await p.close();
 }
 await b.close();
})();
