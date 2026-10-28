const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const b = await chromium.launch({ headless:true, channel:'chrome', args:['--autoplay-policy=no-user-gesture-required'] });
  for (const V of [{w:1440,h:900,tag:'desk'},{w:844,h:1086,tag:'port'}]) {
    const p = await b.newPage({ viewport:{width:V.w,height:V.h} });
    const errs=[]; p.on('pageerror',e=>errs.push(e.message));
    await p.goto('http://127.0.0.1:8811/issue-v26-flight.html',{waitUntil:'load'});
    await sleep(3200);
    console.log(`\n===== ${V.tag} ${V.w}x${V.h} ===== errs:${errs.length?errs.join('|'):'none'}`);

    const H = await p.evaluate(()=>document.documentElement.scrollHeight-innerHeight);
    for (const f of [0,0.10,0.16,0.24,0.34,0.42,0.5,0.58,0.66,0.74,0.84,0.94]) {
      const y = Math.round(H*f);
      await p.evaluate(v=>scrollTo(0,v), y);
      await sleep(950);
      const st = await p.evaluate(()=>{
        const ls=[...document.querySelectorAll('.cam-layer')].map(v=>({
          o:+(+getComputedStyle(v).opacity).toFixed(2),
          f:getComputedStyle(v).filter,
          tf:getComputedStyle(v).transform.replace(/matrix\(([^)]+)\)/,'$1').split(',').slice(0,2).join(',')
        }));
        const live=ls.filter(x=>x.o>0.02);
        return {ls,liveN:live.length,sum:+(ls.reduce((a,c)=>a+c.o,0)).toFixed(2)};
      });
      await p.screenshot({path:`_preview/_v26_${V.tag}_${String(Math.round(f*100)).padStart(3,'0')}.png`});
      console.log(` ${f.toFixed(2)} y=${y} live=${st.liveN} sum=${st.sum} ` +
        st.ls.map((x,i)=>x.o>0.02?`[${i}]o=${x.o} ${x.f}`:'').filter(Boolean).join(' '));
    }
    await p.close();
  }
  await b.close();
})();
