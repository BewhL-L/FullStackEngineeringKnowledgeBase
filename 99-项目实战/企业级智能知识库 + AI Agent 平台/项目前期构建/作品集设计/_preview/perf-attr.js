const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));

const VARIANTS = {
  A_baseline: '',
  B_nobackdrop: '.surf,.ev-chain>div,.evidence,.hero-ledger,.nav{-webkit-backdrop-filter:none!important;backdrop-filter:none!important}',
  C_noblur: '',
  D_both: '.surf,.ev-chain>div,.evidence,.hero-ledger,.nav{-webkit-backdrop-filter:none!important;backdrop-filter:none!important}',
};

(async () => {
  const b = await chromium.launch({ headless:true, channel:'chrome', args:['--autoplay-policy=no-user-gesture-required'] });
  for (const [name, css] of Object.entries(VARIANTS)) {
    const p = await b.newPage({ viewport:{width:1440,height:900} });
    const cdp = await p.context().newCDPSession(p);
    await cdp.send('Performance.enable');
    await p.goto('http://127.0.0.1:8811/issue-v26-flight.html',{waitUntil:'load'});
    if (css) await p.addStyleTag({content:css});
    if (name === 'C_noblur' || name === 'D_both') await p.evaluate(()=>document.documentElement.setAttribute('data-q','2'));
    await sleep(3000);
    await p.evaluate(()=>{ document.documentElement.style.scrollBehavior='auto'; window.__lt=0;
      new PerformanceObserver(l=>{window.__lt+=l.getEntries().length}).observe({entryTypes:['longtask']}); });
    await sleep(500);
    const m0 = (await cdp.send('Performance.getMetrics')).metrics;
    // 2.4s 匀速滚动，跨过两次过场
    await p.evaluate(()=>new Promise(res=>{
      const t0=performance.now(); let y=0;
      (function step(){
        y+=7; scrollTo(0,y);
        if(performance.now()-t0<2400) requestAnimationFrame(step); else res();
      })();
    }));
    const m1 = (await cdp.send('Performance.getMetrics')).metrics;
    const lt = await p.evaluate(()=>window.__lt);
    const g = k => ((m1.find(x=>x.name===k)||{value:0}).value - (m0.find(x=>x.name===k)||{value:0}).value);
    console.log(name.padEnd(14),
      'Task', (g('TaskDuration')*1000).toFixed(0)+'ms',
      'Script', (g('ScriptDuration')*1000).toFixed(0)+'ms',
      'Style', (g('RecalcStyleDuration')*1000).toFixed(0)+'ms',
      'Layout', (g('LayoutDuration')*1000).toFixed(0)+'ms',
      'longtask', lt);
    await p.close();
  }
  await b.close();
})();
