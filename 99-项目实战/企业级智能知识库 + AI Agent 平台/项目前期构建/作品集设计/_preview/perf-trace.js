const { chromium } = require('playwright');
const fs = require('fs');
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function run(b, label, css, q) {
  const p = await b.newPage({ viewport:{width:1440,height:900} });
  await p.goto('http://127.0.0.1:8811/issue-v26-flight.html',{waitUntil:'load'});
  if (css) await p.addStyleTag({content:css});
  if (q!==null) await p.evaluate(v=>document.documentElement.setAttribute('data-q',v), String(q));
  await sleep(3000);
  await p.evaluate(()=>{ document.documentElement.style.scrollBehavior='auto'; });

  const cdp = await p.context().newCDPSession(p);
  const events = [];
  cdp.on('Tracing.dataCollected', d => events.push(...d.value));
  const done = new Promise(r => cdp.once('Tracing.tracingComplete', r));
  await cdp.send('Tracing.start', {
    traceConfig: { includedCategories:['devtools.timeline','disabled-by-default-devtools.timeline'] },
    transferMode: 'ReportEvents'
  });
  await p.evaluate(()=>new Promise(res=>{
    const t0=performance.now(); let y=0;
    (function step(){ y+=7; scrollTo(0,y);
      if(performance.now()-t0<2400) requestAnimationFrame(step); else res(); })();
  }));
  await cdp.send('Tracing.end');
  await done;
  await p.close();

  const sum = {}, cnt = {};
  for (const e of events) {
    if (!e.dur) continue;
    const n = e.name;
    if (!/RasterTask|DrawFrame|CompositeLayers|Paint|Layerize|UpdateLayer|Commit|PrePaint|FunctionCall|UpdateLayoutTree|HitTest/.test(n)) continue;
    sum[n] = (sum[n]||0) + e.dur/1000;
    cnt[n] = (cnt[n]||0) + 1;
  }
  const pick = k => (sum[k]||0).toFixed(0)+'ms/'+(cnt[k]||0);
  console.log(label.padEnd(13),
    'Raster', pick('RasterTask'),
    '| Draw', pick('DrawFrame'),
    '| Composite', pick('CompositeLayers'),
    '| Paint', pick('Paint'),
    '| Layerize', pick('Layerize'));
}

(async () => {
  const b = await chromium.launch({ headless:true, channel:'chrome', args:['--autoplay-policy=no-user-gesture-required'] });
  const NOBD = '.surf,.ev-chain>div,.evidence,.hero-ledger,.nav{-webkit-backdrop-filter:none!important;backdrop-filter:none!important}';
  await run(b, 'A 基线', '', null);
  await run(b, 'B 去毛玻璃', NOBD, null);
  await run(b, 'C 去过场模糊', '', 2);
  await run(b, 'D 两者都去', NOBD, 2);
  await b.close();
})();
