const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch({ headless:true, channel:'chrome', args:['--autoplay-policy=no-user-gesture-required'] });
  // 减弱动效
  const c1 = await b.newContext({ viewport:{width:1440,height:900}, reducedMotion:'reduce' });
  const p1 = await c1.newPage();
  await p1.goto('http://127.0.0.1:8791/issue-v25-glass.html',{waitUntil:'load'}); await sleep(2500);
  console.log('reduced-motion:', JSON.stringify(await p1.evaluate(()=>{
    const vs=[...document.querySelectorAll('.cam-layer')];
    return {op:vs.map(v=>+(+getComputedStyle(v).opacity).toFixed(2)),paused:vs.map(v=>v.paused),
            loaded:vs.map(v=>!!v.currentSrc)};
  })));
  await p1.screenshot({path:__dirname+'/v24-reduced.png'});
  // 视频全部 404 时的兜底
  const c2 = await b.newContext({ viewport:{width:1440,height:900} });
  const p2 = await c2.newPage();
  await p2.route('**/bg/*.mp4', r => r.abort());
  const e2=[]; p2.on('pageerror',e=>e2.push(e.message));
  await p2.goto('http://127.0.0.1:8791/issue-v25-glass.html',{waitUntil:'load'}); await sleep(2500);
  await p2.evaluate(()=>scrollTo(0,2000)); await sleep(1200);
  console.log('视频全部加载失败:', JSON.stringify(await p2.evaluate(()=>{
    const vs=[...document.querySelectorAll('.cam-layer')];
    return {op:vs.map(v=>+(+getComputedStyle(v).opacity).toFixed(2)),
            兜底图可见: !!document.querySelector('.field img') && document.querySelector('.field img').naturalWidth>0,
            bodyBg:getComputedStyle(document.body).backgroundColor};
  })), 'JS错误:', e2.length?e2.join('|'):'无');
  await p2.screenshot({path:__dirname+'/v24-novideo.png'});
  await b.close();
})();
