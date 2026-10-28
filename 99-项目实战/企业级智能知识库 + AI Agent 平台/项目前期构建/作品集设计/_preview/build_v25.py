# -*- coding: utf-8 -*-
"""issue-v23-tide.html -> issue-v25-glass.html
   ① 移除右半部分图版（标记 / 样式 / 响应式逻辑），hero 重排为「文案 + 能力线」双列
   ② 帧率：去掉 nav 的 backdrop-filter、scroll spy 改为缓存偏移、GPU 图层按需提升、
      跳动 Sentinel 自适应降级
   ③ 滚动动效统一：动效令牌化 + 全站 transition 时长/曲线归一 + 视角过渡改为定长窗口
   ④ 模块改磨砂玻璃（15% 白），统一圆角/内距/阴影与放置节奏
"""
import os, re, shutil, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG = os.path.join(ROOT, "bg")

# ---------------- 1. 移除图版 CSS ----------------
PLATE_START = "/* 图版：原生 842×1824"
PLATE_END = "/* ============================================================\n   SECTION · 索引栏"

RESP_PLATE = """  .plate{width:100%;height:48svh;aspect-ratio:auto;max-width:none;min-width:0;border-left:0;border-bottom:1px solid var(--line-2)}
  /* 移动端是整幅出血照片带，不做软边，否则留下暗角 */
  .plate-frame{-webkit-mask-image:none;mask-image:none}
  .plate-glow{display:none}
  .plate img{object-position:50% 34%}
"""
RESP_PLATE_END = "  .plate img{object-position:50% 34%}\n}"

DEPTH_JS_START = "  /* ---------- 景深：图版随指针微移，固定底场不动 → 产生纵深 ---------- */"

# ---------------- 2. hero 重排 ----------------
HERO_START = '    <div class="hero-copy">'
HERO_END = "    </figure>\n"

HERO_NEW = """    <div class="hero-copy">
      <div class="hero-inner">
        <div class="hero-main">
          <p class="hero-eyebrow rv">全栈 / Agent / 检索 · 2024 届</p>
          <h1 class="rv" id="heroTitle" style="--d:60ms">让 AI 进入<br>真实系统。</h1>
          <p class="hero-lede rv" style="--d:120ms">我把模型接入工具、数据与业务流程，交付能运行、能观测、能验证的 AI 应用。</p>
          <div class="hero-actions rv" style="--d:180ms">
            <a class="btn primary" href="#fullstack">查看能力结构</a>
            <a class="btn" href="#retrieval">运行真实检索</a>
          </div>
          <p class="hero-meta rv" style="--d:240ms"><span>杭州 / 上海，可即时到岗</span><span>不接入线上模型</span><span>无追踪脚本</span></p>
        </div>

        <nav class="hero-ledger rv" style="--d:300ms" aria-label="三条能力线">
          <a class="lead" href="#fullstack"><span class="n">01</span><h3>全栈 AI</h3><p>从请求到部署，五层共享同一套边界。</p></a>
          <a class="lead" href="#agent"><span class="n">02</span><h3>Agent 工程</h3><p>规划、工具、观察与校验分开设计。</p></a>
          <a class="lead" href="#retrieval"><span class="n">03</span><h3>数据库检索</h3><p>三路召回到引用回链，答案先被找到。</p></a>
        </nav>
      </div>
    </div>
"""

# ---------------- 3. 新 CSS ----------------
CSS = """
/* ============================================================
   v25 · 动效令牌 —— 全站只有一套曲线与节奏，任何一处动画都从这里取值
   ============================================================ */
:root{
  --ease:cubic-bezier(.22,.61,.16,1);
  --ease-out:cubic-bezier(.16,1,.3,1);
  --t-fast:.22s; --t-base:.36s; --t-slow:.62s; --stagger:60ms;

  --r-glass:14px;
  --glass:rgba(255,255,255,.15);      /* 磨砂玻璃本体：15% 白 */
  --glass-2:rgba(255,255,255,.09);    /* 嵌套次级层 */
  --glass-line:rgba(255,255,255,.26);
  --glass-shadow:0 18px 44px rgba(0,10,9,.30);

  --paper:#FFFDF6;--paper-2:#EFE9DA;--paper-3:#DED8C9;
  --surf:rgba(255,255,255,.15);--surf-2:rgba(255,255,255,.11);
  --line:rgba(255,253,246,.17);--line-2:rgba(255,253,246,.30);--line-3:rgba(255,253,246,.46);
}

/* ---- 揭示：唯一一条出场曲线，位移统一 12/16px，延迟统一 60ms 网格 ---- */
.rv{transition:opacity var(--t-slow) var(--ease-out) var(--d,0ms),transform var(--t-slow) var(--ease-out) var(--d,0ms)}
html.js .rv:not(.in){opacity:0;transform:translate3d(0,var(--rv,12px),0)}
h1.rv,h2.rv{--rv:16px}

/* ============================================================
   HERO · 移除图版后重排：左文案 / 右三条能力线，两列等高，无空白塌陷
   ============================================================ */
.hero-copy{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:center;
  padding:clamp(44px,6.5vh,84px) max(var(--gut),calc((100% - var(--max))/2 + var(--gut)))}
.hero-inner{position:relative;z-index:1;width:100%;max-width:var(--max);
  display:grid;grid-template-columns:minmax(0,1.06fr) minmax(0,.94fr);
  column-gap:clamp(32px,4.6vw,76px);row-gap:clamp(32px,4vh,48px);align-items:center}
.hero-main{min-width:0}
.hero-main h1{margin-top:24px}
.hero-lede{margin-top:26px;max-width:26em}
.hero-actions{margin-top:30px}
.hero-meta{margin-top:24px}
/* 能力线：竖向三行，撑住右列高度，让两列视觉等重 */
.hero-ledger{margin-top:0;border-top:1px solid var(--line-2)}
.lead{border-right:0;border-bottom:1px solid var(--line);padding:16px 0 18px}
.lead:last-child{border-bottom:0;padding-bottom:0}
.lead h3{margin-top:4px}
@media(max-width:900px){
  .hero-inner{grid-template-columns:minmax(0,1fr);row-gap:32px;align-items:start}
  .hero-copy{padding:44px var(--gut)}
  .hero-ledger{margin-top:4px}
}

/* ============================================================
   磨砂玻璃模块：15% 白 + 背景模糊 + 亮描边。
   data-q 由运行时帧率哨兵写入，掉帧时逐级降档（blur 14 → 7 → 关）。
   ============================================================ */
/* 基底严格是 15% 白；上面再叠一层极弱的镜面高光渐变 —— 那是玻璃该有的反光，
   不是把不透明度调高。没有这层，15% 白在暗底子上只会读成一块灰板。 */
.surf,.ev-chain>div{
  background:
    linear-gradient(135deg,rgba(255,255,255,.11) 0%,rgba(255,255,255,.025) 44%,rgba(255,255,255,.07) 100%),
    var(--glass);
  border:1px solid rgba(255,255,255,.32);
  border-radius:var(--r-glass);
  box-shadow:var(--glass-shadow),inset 0 1px 0 rgba(255,255,255,.34);
}
.surf{padding:clamp(22px,2.2vw,30px)}
.surf>*:first-child{margin-top:0}
.ev-chain>div{background:var(--glass-2);border:0;border-radius:0;box-shadow:none}
.ev-chain>div:first-child{border-top-left-radius:var(--r-glass);border-bottom-left-radius:var(--r-glass)}
.ev-chain>div:last-child{border-top-right-radius:var(--r-glass);border-bottom-right-radius:var(--r-glass)}
html[data-q="0"] .surf,html[data-q="0"] .ev-chain>div{
  -webkit-backdrop-filter:blur(18px) saturate(1.35);backdrop-filter:blur(18px) saturate(1.35)}
html[data-q="1"] .surf,html[data-q="1"] .ev-chain>div{
  -webkit-backdrop-filter:blur(10px) saturate(1.2);backdrop-filter:blur(10px) saturate(1.2)}
html[data-q="2"] .surf,html[data-q="2"] .ev-chain>div{
  -webkit-backdrop-filter:none;backdrop-filter:none;
  background:rgba(255,255,255,.19)}

/* 弹窗：同材质，只是更厚一点 */
.evidence{background:rgba(255,255,255,.13);border:1px solid var(--glass-line);border-radius:var(--r-glass);
  box-shadow:0 44px 120px rgba(0,10,9,.46),inset 0 1px 0 rgba(255,255,255,.3)}
html[data-q="0"] .evidence,html[data-q="1"] .evidence{
  -webkit-backdrop-filter:blur(18px) saturate(1.25);backdrop-filter:blur(18px) saturate(1.25)}
.ev-head{background:rgba(255,255,255,.10);border-bottom:1px solid var(--glass-line)}
html[data-q="2"] .evidence{background:rgba(255,255,255,.2)}

/* 导航：去掉叠在动态视频上的 backdrop-filter（每帧重算，帧率杀手），改用实底渐变 */
.nav{background:linear-gradient(180deg,rgba(8,20,18,.90),rgba(8,20,18,.72));
  -webkit-backdrop-filter:none!important;backdrop-filter:none!important}
.nav-links.open{background:rgba(9,22,20,.96)}

/* ============================================================
   全屏五视角运镜场
   ============================================================ */
.camfield{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden;background:var(--void);--band:.66}
.cam-layers{position:absolute;inset:0}
.cam-layer{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 50%;
  filter:none;opacity:0;transform:scale(1);transform-origin:52% 50%;
  backface-visibility:hidden;-webkit-backface-visibility:hidden}
/* 只有正在显示的两层提升为合成层，其余不占 GPU 显存 */
.cam-layer.gpu{will-change:opacity,transform}
/* 内容列保护带：色相改为深松石而非纯黑，同等亮度下不再显得发死 */
.cam-band{position:absolute;top:0;bottom:0;left:50%;transform:translateX(-50%);
  width:min(100%,calc(var(--max) + 56px));
  background:rgba(9,26,24,var(--band));
  -webkit-mask-image:linear-gradient(90deg,transparent 0,#000 3.5%,#000 96.5%,transparent 100%);
  mask-image:linear-gradient(90deg,transparent 0,#000 3.5%,#000 96.5%,transparent 100%)}
.cam-scrim{position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(9,26,24,.40) 0%,rgba(9,26,24,.05) 20%,rgba(9,26,24,0) 42%,
    rgba(9,26,24,.05) 80%,rgba(9,26,24,.46) 100%)}
.cam-scrim::before{content:"";position:absolute;left:0;right:0;top:0;height:calc(var(--nav) + 30px);
  background:linear-gradient(180deg,rgba(9,26,24,.7),rgba(9,26,24,0))}
@media(max-width:900px){ .camfield{--band:.70} }
"""

# ---------------- 4. 控制器 JS ----------------
JS = r"""
/* ============================================================
   v25 滚动/运镜控制器
   · 只写 opacity + transform，绝不在滚动回调里读布局（避免强制回流）
   · 视角过渡改为「定长窗口」：每条过渡都占同样像素行程，节奏统一，
     不再随章节长短忽快忽慢
   · 链式交叉溶解保证各层不透明度恒等于 1，切换过程不会出现亮度塌陷
   ============================================================ */
(function camera(){
  var host=document.getElementById("camLayers");
  if(!host) return;
  var layers=Array.prototype.slice.call(host.querySelectorAll(".cam-layer"));
  var reduce=window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var saveData=(navigator.connection&&navigator.connection.saveData)||false;

  /* 锚点取 hero / fullstack / retrieval / case / evidence。
     不用 contact —— 它的顶边落在最大可滚动量之外，会挤掉最后一个视角的过渡区，
     实测导致第 5 个视角只有 187px 行程、几乎不出现。 */
  var IDS=["hero","fullstack","retrieval","case","evidence"];
  function light(){ return window.matchMedia("(max-width:768px)").matches||saveData; }
  /* 轻量档只用 V1 V3 V5，少下约 23MB */
  function list(){ return light()?[0,2,4]:[0,1,2,3,4]; }
  /* smootherstep：一阶二阶导在两端都为 0，起步与收尾都没有速度突变 */
  function sm(x){ x=x<0?0:(x>1?1:x); return x*x*x*(x*(6*x-15)+10); }

  var loaded=[],ready=[],anchors=[],queued=false,gpuSet="";

  function measure(){
    anchors=IDS.map(function(id){
      var el=document.getElementById(id);
      return el?Math.round(el.getBoundingClientRect().top+window.pageYOffset):0;
    });
    for(var k=1;k<anchors.length;k++) if(anchors[k]<=anchors[k-1]) anchors[k]=anchors[k-1]+1;
  }

  function ensure(i){
    if(i<0||i>=layers.length||loaded[i]) return;
    loaded[i]=true;
    var v=layers[i];
    v.addEventListener("loadeddata",function(){ ready[i]=true; queue(); });
    v.addEventListener("error",function(){ ready[i]=false; loaded[i]=false; queue(); });
    v.setAttribute("preload","auto");
    v.src=v.getAttribute("data-src");
    v.load();
  }

  function apply(){
    queued=false;
    var y=window.pageYOffset;
    var L=list(), pos=L.map(function(i){ return anchors[i]; });
    var vh=window.innerHeight||800;

    /* 每条过渡结束于下一个视角的锚点，行程长度固定 → 节奏一致。
       两处必要的钳制：
         · end 不得超过最大可滚动距离（否则最后一个视角永远走不完）
         · start 不得早于上一条过渡的结束（否则两条过渡重叠，出现同时换两次视角） */
    var maxY=Math.max(1,(document.documentElement.scrollHeight||0)-vh);
    var F=new Array(L.length).fill(0), prevEnd=pos[0];
    for(var m=1;m<L.length;m++){
      var end=Math.min(pos[m],maxY);
      if(end<=prevEnd) end=prevEnd+1;
      var w=Math.min(vh*0.92, Math.max(240,(end-pos[m-1])*0.72));
      var start=Math.max(prevEnd, end-w);
      F[m]=sm((y-start)/Math.max(1,end-start));
      prevEnd=end;
    }

    /* 链式交叉溶解：sum ≡ 1 */
    var op=new Array(L.length).fill(0), prod=1;
    for(var j=0;j<L.length-1;j++){
      var f=F[j+1];
      op[j]=prod*(1-f);
      prod*=f;
    }
    op[L.length-1]=prod;

    /* 未就绪（仍在下载 / 加载失败）的图层绝不上屏，权重让给最近的就绪图层。
       否则会出现半透明的空视频层压在静态兜底场上面。 */
    var eff=new Array(L.length).fill(0);
    for(var a=0;a<L.length;a++){
      if(op[a]<=0) continue;
      if(ready[L[a]]){ eff[a]+=op[a]; continue; }
      var t=-1;
      for(var c=a-1;c>=0;c--){ if(ready[L[c]]){ t=c; break; } }
      if(t<0){ for(var c2=a+1;c2<L.length;c2++){ if(ready[L[c2]]){ t=c2; break; } } }
      if(t>=0) eff[t]+=op[a];
    }

    var plain=new Array(layers.length).fill(0);
    var sc=new Array(layers.length).fill(1);
    for(var k=0;k<L.length;k++){
      var li=L[k];
      plain[li]=eff[k];
      /* 匹配剪辑：离场层微推近、入场层微拉远，两层反向运动 → 读起来是一条连续运镜 */
      sc[li]=1+0.03*(1-eff[k]);
    }

    var visible=[];
    for(var i2=0;i2<layers.length;i2++){
      var v=layers[i2], o=Math.round(plain[i2]*1000)/1000;
      if(v._o!==o){ v._o=o; v.style.opacity=o; }
      var s=Math.round(sc[i2]*10000)/10000, tf=s===1?"scale(1)":"scale("+s+")";
      if(v._s!==tf){ v._s=tf; v.style.transform=tf; }
      if(o>0.004){
        ensure(i2);
        visible.push(i2);
        if(!reduce&&v.paused&&document.visibilityState==="visible"){
          var pr=v.play(); if(pr&&pr.catch) pr.catch(function(){});
        }
      }else if(!v.paused){ v.pause(); }
    }
    /* GPU 图层只在可见集合变化时切换，不做逐帧抖动 */
    var key=visible.join(",");
    if(key!==gpuSet){
      gpuSet=key;
      for(var q=0;q<layers.length;q++) layers[q].classList.toggle("gpu",visible.indexOf(q)>=0);
    }
    if(!reduce){
      /* 预取下一视角，避免进入过渡区才开始下载 */
      var next=Math.min(pos.length-1, F.findIndex(function(f,i){return i>0&&f<1;}) );
      if(next>0) ensure(L[next]);
    }
  }

  function queue(){ if(!queued){ queued=true; requestAnimationFrame(apply); } }

  measure();
  addEventListener("scroll",queue,{passive:true});
  addEventListener("resize",function(){ measure(); queue(); },{passive:true});
  addEventListener("load",function(){ measure(); queue(); });
  addEventListener("orientationchange",function(){ setTimeout(function(){ measure(); queue(); },260); });
  document.addEventListener("visibilitychange",function(){ queue(); });

  if(reduce){
    var f=layers[0];
    loaded[0]=true;
    f.setAttribute("preload","metadata");
    f.src=f.getAttribute("data-src");
    f.load();
    f.addEventListener("loadeddata",function(){ ready[0]=true; f.classList.add("gpu"); queue(); },{once:true});
    return;
  }
  ensure(0);
  apply();
  var idle=window.requestIdleCallback||function(fn){ return setTimeout(fn,1200); };
  idle(function(){ for(var j=1;j<layers.length;j++) ensure(j); });

  /* ------------------------------------------------------------
     帧率哨兵：估算屏幕刷新率，滚动/播放掉帧时把磨砂玻璃逐级降档。
     不改动任何布局，只在 documentElement 上写 data-q。
     ------------------------------------------------------------ */
  (function fpsGuard(){
    var root=document.documentElement, tier=0, frames=0, budget=1000;
    var t0=0, acc=0, dtBuf=[], hz=0;
    var KNOWN=[60,75,90,100,120,144,165,240];
    root.setAttribute("data-q",0);
    function tick(now){
      if(document.visibilityState!=="visible"){ t0=now; requestAnimationFrame(tick); return; }
      if(t0){ var dt=now-t0; if(dt>0&&dt<200){ acc+=dt; frames++; dtBuf.push(dt); } }
      t0=now;
      if(acc>=budget){
        var fps=frames/(acc/1000);
        /* 帧距中位数≈屏幕刷新间隔，再吸附到常见刷新率，避免误判 */
        if(!hz&&dtBuf.length>20){
          dtBuf.sort(function(a,b){return a-b;});
          var est=1000/dtBuf[Math.floor(dtBuf.length/2)];
          hz=KNOWN.reduce(function(a,c){ return Math.abs(c-est)<Math.abs(a-est)?c:a; },60);
          root.setAttribute("data-hz",hz);
        }
        var target=hz||60;
        if(fps < target*0.72 && tier<2){ tier++; root.setAttribute("data-q",tier); }
        else if(fps > target*0.92 && tier>0){ tier--; root.setAttribute("data-q",tier); }
        frames=0; acc=0; if(dtBuf.length>240) dtBuf.length=0;
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  })();
})();
"""

# ---------------- 构建 ----------------
src = os.path.join(ROOT, "issue-v23-tide.html")
dst = os.path.join(ROOT, "issue-v25-glass.html")
html = io.open(src, "r", encoding="utf-8").read()

def cut(text, a, b, guard):
    i = text.find(a)
    if i < 0:
        raise SystemExit("not found: " + guard)
    j = text.find(b, i)
    if j < 0:
        raise SystemExit("not found end: " + guard)
    return text[:i] + text[j:]

# ① 图版样式与 responsive 逻辑
html = cut(html, PLATE_START, PLATE_END, "plate css")
#
j = html.find(RESP_PLATE)
if j >= 0:
    html = html[:j] + html[j + len(RESP_PLATE):]
html = html.replace("  .plate img{object-position:50% 34%}\n}", "}")
html = html.replace("  .plate,.plate-glow{display:none}\n", "")

# ② hero 重排
a = html.find(HERO_START)
b = html.find(HERO_END, a)
if a < 0 or b < 0:
    raise SystemExit("hero block not found")
html = html[:a] + HERO_NEW + html[b + len(HERO_END):]

# ③ 移除失效的景深 JS（依赖已删除的 .plate）
i = html.find(DEPTH_JS_START)
if i >= 0:
    k = html.find("\n})();", i)
    html = html[:i] + html[k + 1:]

# ④ 全站动效归一：所有 transition 的时长与曲线改用令牌
style_start = html.index("<style>") + len("<style>")
style_end = html.index("</style>")
style = html[style_start:style_end]

FAST = [".18s", ".2s", ".22s", ".25s", ".28s", ".3s"]
BASE = [".26s", ".36s", ".4s"]

def unify(m):
    s = m.group(0)
    if s.strip() in ("transition:none",):
        return s
    for d in FAST:
        s = s.replace(d, "var(--t-fast)")
    for d in BASE:
        s = s.replace(d, "var(--t-base)")
    s = s.replace(".5s", "var(--t-slow)")
    if "var(--ease" not in s and "cubic-bezier" not in s:
        s = s + " var(--ease)"
    return s

style = re.sub(r"transition:[^;}]+", unify, style)

# ⑤ 揭示延迟统一到 60ms 网格
def snap(m):
    v = int(m.group(1))
    return "--d:%dms" % (min(6, max(0, int(round(v / 60.0)))) * 60)

style = re.sub(r"--d:(\d+)ms", snap, style)

html = (html[:style_start]
        + style
        + CSS
        + "\n</style>"
        + html[style_end + len("</style>"):])

# ⑥ video 叠层结构
OLD_FIELD = '<div class="field" aria-hidden="true"><img src="assets/beach-field.jpg" alt="" width="40" height="87" decoding="async"></div>'
NEW_FIELD = """<div class="camfield" aria-hidden="true">
  <div class="field"><img src="assets/beach-field.jpg" alt="" width="40" height="87" decoding="async"></div>
  <div class="cam-layers" id="camLayers">
    <video class="cam-layer" data-src="bg/v1-nadir.mp4"    muted loop playsinline preload="none" disablepictureinpicture></video>
    <video class="cam-layer" data-src="bg/v2-oblique.mp4"  muted loop playsinline preload="none" disablepictureinpicture></video>
    <video class="cam-layer" data-src="bg/v3-eyelevel.mp4" muted loop playsinline preload="none" disablepictureinpicture></video>
    <video class="cam-layer" data-src="bg/v4-side.mp4"     muted loop playsinline preload="none" disablepictureinpicture></video>
    <video class="cam-layer" data-src="bg/v5-macro.mp4"    muted loop playsinline preload="none" disablepictureinpicture></video>
  </div>
  <div class="cam-band"></div>
  <div class="cam-scrim"></div>
</div>"""
assert html.count(OLD_FIELD) == 1
html = html.replace(OLD_FIELD, NEW_FIELD)

# ⑦ scroll spy 改为缓存偏移：滚动时不再逐帧读 getBoundingClientRect
OLD_SPY = """  var sections=$$("main section[id]"),navLinks=$$("[data-nav]");
  var activeSection="hero",spyQueued=false;
  function spy(){
    spyQueued=false;
    var probe=window.innerHeight*0.4,current=sections[0];
    sections.forEach(function(s){if(s.getBoundingClientRect().top<=probe)current=s;});"""
NEW_SPY = """  var sections=$$("main section[id]"),navLinks=$$("[data-nav]");
  var activeSection="hero",spyQueued=false,secTops=[];
  /* 偏移只在布局变化时测量一次；滚动回调里不再触碰 getBoundingClientRect，
     否则每帧都会强制回流，这是滚动掉帧最常见的根因 */
  function measureSpy(){
    secTops=sections.map(function(s){return Math.round(s.getBoundingClientRect().top+window.pageYOffset);});
  }
  function spy(){
    spyQueued=false;
    var probe=window.pageYOffset+window.innerHeight*0.4,current=sections[0];
    for(var si=0;si<sections.length;si++){ if(secTops[si]<=probe) current=sections[si]; }"""
assert html.count(OLD_SPY) == 1, "spy block not found"
html = html.replace(OLD_SPY, NEW_SPY)
html = html.replace(
    '  addEventListener("resize",queueSpy,{passive:true});\n  spy();',
    '  addEventListener("resize",function(){measureSpy();queueSpy();},{passive:true});\n  addEventListener("load",measureSpy,{passive:true});\n  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(function(){measureSpy();queueSpy();});\n  measureSpy();\n  spy();')

html = html.replace('<meta name="theme-color" content="#050D0C">',
                    '<meta name="theme-color" content="#050D0C">\n<link rel="icon" href="data:,">')
html = html.replace("</script>", JS + "\n</script>")

with io.open(dst, "w", encoding="utf-8", newline="\n") as f:
    f.write(html)

print("built:", dst, os.path.getsize(dst) // 1024, "KB")
for probe in ["class=\"plate\"", ".plate{", "plate-glow", "sea-glow", "getBoundingClientRect().top<=probe"]:
    print("  残留 %-38s %s" % (probe, "有!! " + str(html.count(probe)) if html.count(probe) else "无"))
