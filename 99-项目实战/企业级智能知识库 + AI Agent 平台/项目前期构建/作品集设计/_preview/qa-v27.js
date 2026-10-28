const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch({ headless:true, channel:'chrome', args:['--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport:{width:1440,height:900} });
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{if(m.type()==='error')errs.push('C:'+m.text())});
  await p.goto('http://127.0.0.1:8811/issue-v27-cine.html',{waitUntil:'load'});
  await sleep(3200);
  console.log('errs:', errs.length?errs.join(' | '):'none');
  console.log('fx =', await p.evaluate(()=>document.documentElement.getAttribute('data-fx')));
  console.log('hud =', await p.evaluate(()=>{const h=document.getElementById('camHud');return h?h.innerText.replace(/\s+/g,' '):'MISSING'}));
  await p.screenshot({path:'_preview/_v27_hero.png'});

  // 滚到中段
  await p.evaluate(()=>window.scrollTo(0,2450)); await sleep(1400);
  console.log('hud mid =', await p.evaluate(()=>document.getElementById('camHud').innerText.replace(/\s+/g,' ')));
  await p.screenshot({path:'_preview/_v27_mid.png'});

  // 点导航看飞行动画
  await p.evaluate(()=>window.scrollTo(0,0)); await sleep(800);
  await p.click('a[data-nav="retrieval"]');
  const ys=[];
  for(let i=0;i<8;i++){ await sleep(110); ys.push(await p.evaluate(()=>Math.round(scrollY))); }
  console.log('fly 采样:', ys.join(' → '));
  await sleep(1200);
  console.log('落点 scrollY =', await p.evaluate(()=>Math.round(scrollY)));
  await p.screenshot({path:'_preview/_v27_fly.png'});

  // 底部 HUD 是否退场
  await p.evaluate(()=>window.scrollTo(0,document.documentElement.scrollHeight)); await sleep(900);
  console.log('hud out?', await p.evaluate(()=>document.getElementById('camHud').classList.contains('out')));

  await p.close();

  // 玻璃档对照
  const p2 = await b.newPage({ viewport:{width:1440,height:900} });
  await p2.goto('http://127.0.0.1:8811/issue-v27-cine.html?fx=glass',{waitUntil:'load'});
  await sleep(2600);
  console.log('glass fx =', await p2.evaluate(()=>document.documentElement.getAttribute('data-fx')));
  await p2.screenshot({path:'_preview/_v27_glass.png'});
  await p2.close();

  // 移动端
  const p3 = await b.newPage({ viewport:{width:390,height:844}, deviceScaleFactor:2 });
  await p3.goto('http://127.0.0.1:8811/issue-v27-cine.html',{waitUntil:'load'});
  await sleep(2800);
  await p3.evaluate(()=>window.scrollTo(0,1000)); await sleep(900);
  await p3.screenshot({path:'_preview/_v27_mob.png'});
  await p3.close();
  await b.close();
})();
