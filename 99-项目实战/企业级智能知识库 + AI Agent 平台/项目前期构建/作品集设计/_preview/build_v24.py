# -*- coding: utf-8 -*-
"""issue-v23-tide.html -> issue-v24-camera.html
   ① 复制五条视角素材到 bg/ 并统一命名
   ② 注入全屏运镜场 CSS（内容列保护带经实测标定）
   ③ 替换 .field 为视频叠层结构
   ④ 注入滚动驱动交叉溶解控制器
"""
import os, shutil, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_ASSETS = os.path.join(ROOT, "camera-angles_assets")
BG = os.path.join(ROOT, "bg")

MAP = [
    ("e1a4137a", "v1-nadir.mp4"),     # 俯视 nadir
    ("d01b48a3", "v2-oblique.mp4"),   # 斜视 45
    ("711647c9", "v3-eyelevel.mp4"),  # 主视平视
    ("dda57f7f", "v4-side.mp4"),      # 侧视沿岸
    ("fe034600", "v5-macro.mp4"),     # 微距水面
]

os.makedirs(BG, exist_ok=True)
for pref, dst in MAP:
    hits = [f for f in os.listdir(SRC_ASSETS) if f.startswith(pref) and f.endswith(".mp4")]
    if not hits:
        raise SystemExit("missing source: " + pref)
    shutil.copy2(os.path.join(SRC_ASSETS, hits[0]), os.path.join(BG, dst))

CSS = """
/* ============================================================
   v24 五视角运镜全屏场
   视频本身不加任何滤镜（2K 图层每帧跑 filter 会实打实吃掉合成帧率）。
   可读性由「内容列保护带」承担：强度均匀、左右软边，只压内容列，
   带外视频保持原始亮度。--band 经实测标定：
     .58 -> 正文对比度 7.9 / 最小灰字 6.4，过 AA 并接近 AAA
   想整体压暗视频时给 .camfield 设 --cam-filter:brightness(.8)。
   ============================================================ */
:root{
  --paper:#FFFDF6;--paper-2:#EFE9DA;--paper-3:#DED8C9;
  --surf:rgba(6,18,17,.86);--surf-2:rgba(5,15,14,.93);
  --line:rgba(255,253,246,.17);--line-2:rgba(255,253,246,.28);--line-3:rgba(255,253,246,.42);
}
body{text-shadow:0 1px 2px rgba(3,10,10,.55),0 2px 20px rgba(3,10,10,.34)}
.nav{background:linear-gradient(180deg,rgba(5,14,13,.9),rgba(5,14,13,.78))}
.surf{-webkit-backdrop-filter:blur(12px) saturate(1.08);backdrop-filter:blur(12px) saturate(1.08)}
.plate-cap span{color:rgba(255,253,246,.62)}

.camfield{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden;background:var(--void);--band:.66}
.cam-layers{position:absolute;inset:0}
.cam-layer{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 50%;
  filter:var(--cam-filter,none);
  opacity:0;transform:scale(1);transform-origin:52% 50%;
  backface-visibility:hidden;-webkit-backface-visibility:hidden}
.cam-band{position:absolute;top:0;bottom:0;left:50%;transform:translateX(-50%);
  width:min(100%,calc(var(--max) + 56px));
  background:rgba(4,13,12,var(--band));
  -webkit-mask-image:linear-gradient(90deg,transparent 0,#000 3.5%,#000 96.5%,transparent 100%);
  mask-image:linear-gradient(90deg,transparent 0,#000 3.5%,#000 96.5%,transparent 100%)}
.cam-scrim{position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(4,13,12,.40) 0%,rgba(4,13,12,.05) 20%,rgba(4,13,12,0) 42%,
    rgba(4,13,12,.05) 80%,rgba(4,13,12,.46) 100%)}
.cam-scrim::before{content:"";position:absolute;left:0;right:0;top:0;height:calc(var(--nav) + 30px);
  background:linear-gradient(180deg,rgba(4,13,12,.7),rgba(4,13,12,0))}
@media(max-width:900px){
  .camfield{--band:.62}
  body{text-shadow:0 1px 2px rgba(3,10,10,.6),0 2px 22px rgba(3,10,10,.42)}
}
"""

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

JS = r"""
/* ============================================================
   v24 五视角运镜控制器
   滚动位置 -> 段落内进度 -> 交叉溶解权重 -> 图层 opacity / scale
   只写 opacity 与 transform，全程走合成器，不触发重排。
   解码预算：同时只有「当前 + 下一个」两条在播，其余 pause。
   ============================================================ */
(function camera(){
  var host=document.getElementById("camLayers");
  if(!host) return;
  var layers=Array.prototype.slice.call(host.querySelectorAll(".cam-layer"));
  var reduce=window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var saveData=(navigator.connection&&navigator.connection.saveData)||false;

  var IDS=["hero","fullstack","retrieval","evidence","contact"];
  function light(){ return window.matchMedia("(max-width:768px)").matches||saveData; }
  function resolve(j){ return light()?(j===1?0:(j===3?2:j)):j; }
  function ease(x){ x=x<0?0:(x>1?1:x); return x*x*(3-2*x); }

  var loaded=[],ready=[],anchors=[],queued=false;

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
    /* 素材缺失或解码失败：该层永久退出，交回静态兜底场 */
    v.addEventListener("error",function(){ ready[i]=false; loaded[i]=false; queue(); });
    v.setAttribute("preload","auto");
    v.src=v.getAttribute("data-src");
    v.load();
  }

  function apply(){
    queued=false;
    var y=window.pageYOffset,n=anchors.length,i=0;
    for(var k=n-2;k>=0;k--){ if(y>=anchors[k]){ i=k; break; } }
    var span=Math.max(1,anchors[i+1]-anchors[i]);
    var t=(y-anchors[i])/span;
    var w=ease((t-0.42)/0.46);

    var a=resolve(i),b=resolve(i+1);
    var op=layers.map(function(){return 0;}),sc=layers.map(function(){return 1;});
    var ra=!!ready[a],rb=a===b?ra:!!ready[b];
    /* 只有真正就绪的图层才参与溶解；未就绪时交回静态兜底场，不留半透明空层 */
    if(a===b){ if(ra) op[a]=1; }
    else if(ra&&rb){
      op[a]=1-w; op[b]=w;
      sc[a]=1+0.035*w; sc[b]=1.035-0.035*w;
    }
    else if(ra){ op[a]=1; }
    else if(rb){ op[b]=1; }

    for(var j=0;j<layers.length;j++){
      var v=layers[j],o=Math.round(op[j]*1000)/1000;
      if(v._o!==o){ v._o=o; v.style.opacity=o; }
      var s=Math.round(sc[j]*10000)/10000,tf=s===1?"":"scale("+s+")";
      if(v._s!==tf){ v._s=tf; v.style.transform=tf; }
      if(o>0.004){
        ensure(j);
        if(!reduce&&v.paused&&document.visibilityState==="visible"){
          var pr=v.play(); if(pr&&pr.catch) pr.catch(function(){});
        }
      }else if(!v.paused){ v.pause(); }
    }
    /* 预取下一个视角，避免进入过渡区才开下载；减弱动效下不预取 */
    if(!reduce) ensure(resolve(Math.min(i+1,layers.length-1)));
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
    /* 停在首帧即可，不播放；就绪标记交给 apply 统一决定显示哪一层 */
    f.addEventListener("loadeddata",function(){ ready[0]=true; queue(); },{once:true});
    f.addEventListener("error",function(){ ready[0]=false; },{once:true});
    return;
  }
  ensure(0);
  apply();
  var idle=window.requestIdleCallback||function(fn){ return setTimeout(fn,1200); };
  idle(function(){ for(var j=1;j<layers.length;j++) ensure(j); });
})();
"""

src = os.path.join(ROOT, "issue-v23-tide.html")
dst = os.path.join(ROOT, "issue-v24-camera.html")
with io.open(src, "r", encoding="utf-8") as f:
    html = f.read()

assert html.count("</style>") == 1, "style anchor not unique"
assert html.count(OLD_FIELD) == 1, "field anchor not unique"
assert html.count("</script>") == 1, "script anchor not unique"

html = html.replace('<meta name="theme-color" content="#050D0C">',
                    '<meta name="theme-color" content="#050D0C">\n<link rel="icon" href="data:,">')
html = html.replace("</style>", CSS + "\n</style>")
html = html.replace(OLD_FIELD, NEW_FIELD)
html = html.replace("</script>", JS + "\n</script>")
html = html.replace(
    "<title>罗子强 — AI 应用工程 / 全栈 · Agent · 检索</title>",
    "<title>罗子强 — AI 应用工程 / 全栈 · Agent · 检索</title>\n"
    "<!-- v24 五视角运镜 · 素材规格 2560x1440 / 24fps / 6.58s / 158帧 / H.264 mp4，五条共约 65MB -->")

with io.open(dst, "w", encoding="utf-8", newline="\n") as f:
    f.write(html)

print("built:", dst, os.path.getsize(dst) // 1024, "KB")
