# -*- coding: utf-8 -*-
"""issue.html -> issue-v16-explode.html 的增量补丁（第一轮优化顺序 + 方向 02 的 3D 重构）"""
import io, sys, re

SRC = "issue-v16-explode.html"
s = io.open(SRC, encoding="utf-8", newline="").read()
report = []
fail = []

def rep(name, old, new, expect=None, count=None):
    n = s.count(old)
    if expect is not None and n != expect:
        fail.append("%s: expected %d got %d" % (name, expect, n))
        return
    if count is not None and n < 1:
        fail.append("%s: not found" % name)
        return
    globals()['s'] = s.replace(old, new)
    report.append("%-28s x%d" % (name, n))

# ---------------------------------------------------------------- 记号层
rep("tokens: 线宽四档 + 8pt 尺度",
    "  --rule:rgba(240,234,224,.17);\n  --rule-2:rgba(240,234,224,.075);",
    "  --hair:rgba(240,234,224,.06);\n"
    "  --rule:rgba(240,234,224,.10);\n"
    "  --edge:rgba(240,234,224,.22);\n"
    "  --focus:rgba(240,234,224,.55);\n"
    "  --rule-2:rgba(240,234,224,.06);\n"
    "  --s1:8px;--s2:16px;--s3:24px;--s4:32px;--s5:48px;--s6:64px;--s7:96px;--s8:128px;", 1)

rep("tokens: 字号补齐中间层",
    "  --t-xs:12px;--t-sm:14px;--t-md:16px;--t-xl:56px;--t-xxl:96px;--t-num:220px;",
    "  --t-xs:12px;--t-sm:14px;--t-md:16px;--t-lg:18px;--t-h3:20px;--t-h4:24px;--t-xl:56px;--t-xxl:96px;--t-num:220px;", 1)

rep("color: 三级文字对比度 4.6->6.3",
    "  --ink-3:#837A6B;", "  --ink-3:#9A9083;", 1)

# 旧的 --rule-2 全部落到 hair（与原 visual 等价）
rep("global: rule-2 -> hair", "var(--rule-2)", "var(--hair)")

# ---------------------------------------------------------------- 线的层级
edge_map = [
  (".nav-cta", ".nav-cta{flex:none;font-size:14px;border-bottom:1px solid var(--rule);",
              ".nav-cta{flex:none;font-size:14px;border-bottom:1px solid var(--edge);"),
  (".btn",     ".btn{display:inline-flex;align-items:center;gap:10px;height:44px;padding:0 20px;border:1px solid var(--rule);",
              ".btn{display:inline-flex;align-items:center;gap:10px;height:44px;padding:0 20px;border:1px solid var(--edge);"),
  (".link",    '.link{display:inline-flex;align-items:center;gap:8px;font-size:14px;color:var(--ink-2);border-bottom:1px solid var(--rule);',
              '.link{display:inline-flex;align-items:center;gap:8px;font-size:14px;color:var(--ink-2);border-bottom:1px solid var(--edge);'),
  (".hero-ledger", ".hero-ledger{grid-column:1/13;grid-row:2;display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--rule);",
                   ".hero-ledger{grid-column:1/13;grid-row:2;display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--edge);"),
  (".steps",   ".steps{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--hair);border-bottom:1px solid var(--hair)}",
               ".steps{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--edge);border-bottom:1px solid var(--edge)}"),
  (".lab",     ".lab{margin-top:52px;border-top:1px solid var(--rule);padding-top:18px}",
               ".lab{margin-top:48px;border-top:1px solid var(--edge);padding-top:16px}"),
  (".channels",".channels{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--hair);border-bottom:1px solid var(--hair)}",
               ".channels{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--edge);border-bottom:1px solid var(--edge)}"),
  ("dialog",   'border:1px solid var(--rule);background:#100E0C;color:var(--ink);overflow:auto}',
               'border:1px solid var(--edge);background:#1A1714;color:var(--ink);overflow:auto;box-shadow:0 40px 120px rgba(0,0,0,.6)}'),
  ("dialog backdrop", ".evidence::backdrop{background:rgba(8,7,5,.87)}", ".evidence::backdrop{background:rgba(6,5,4,.74)}"),
  ("dialog head", 'padding:18px 24px;border-bottom:1px solid var(--rule);background:#100E0C}',
                  'padding:18px 24px;border-bottom:1px solid var(--rule);background:#1A1714}'),
]
for nm, o, n in edge_map:
    rep(nm, o, n, 1)

# ---------------------------------------------------------------- 指示器
rep("indicator: step 全宽", '.step.on::after{content:"";position:absolute;left:0;right:20px;bottom:-1px;height:1px;background:var(--ink)}',
                            '.step.on::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:2px;background:var(--focus)}', 1)
rep("indicator: channel 全宽", '.ch.on::after{content:"";position:absolute;left:0;right:16px;bottom:-1px;height:1px;background:var(--ink)}',
                               '.ch.on::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:2px;background:var(--focus)}', 1)

# ---------------------------------------------------------------- 指标网格
rep("metric grid: 对称 + 收口",
    ".metrics{display:grid;grid-template-columns:1fr 1fr}\n"
    ".metric{padding:20px 0;border-bottom:1px solid var(--hair)}\n"
    ".metric:nth-child(odd){border-right:1px solid var(--hair);padding-right:16px}\n"
    ".metric:nth-child(even){padding-left:20px}\n"
    ".metric:nth-last-child(-n+2){border-bottom:0}",
    ".metrics{display:grid;grid-template-columns:1fr 1fr;border-top:1px solid var(--rule)}\n"
    ".metric{padding:20px 0 24px;border-bottom:1px solid var(--rule)}\n"
    ".metric:nth-child(odd){border-right:1px solid var(--rule);padding-right:24px}\n"
    ".metric:nth-child(even){padding-left:24px}\n"
    ".metric:nth-last-child(-n+2){border-bottom:0}", 1)

# ---------------------------------------------------------------- 栅格统一
grid_map = [
  (".hero-plate", ".hero-plate{grid-column:8/13;grid-row:1;align-self:center;width:100%}",
                  ".hero-plate{grid-column:9/13;grid-row:1;align-self:center;width:100%}\n.hero-plate .plate-frame{aspect-ratio:3/4}"),
  (".ev-hero", ".ev-hero{grid-column:1/7}", ".ev-hero{grid-column:1/8}"),
  (".ev-list", ".ev-list{grid-column:8/13}", ".ev-list{grid-column:9/13}"),
  (".ct-copy", ".ct-copy{grid-column:1/7}", ".ct-copy{grid-column:1/8}"),
  (".ct-side", ".ct-side{grid-column:8/13}", ".ct-side{grid-column:9/13}"),
  ("1180 head", "  .sec-head .intro{grid-column:8/13;font-size:16px}", "  .sec-head .intro{grid-column:9/13;font-size:16px}"),
  ("1180 side", "  .arch{grid-column:1/8}.side{grid-column:8/13}\n  .trace{grid-column:1/8}.agent-side{grid-column:8/13}\n  .compare{grid-column:1/8}.proof{grid-column:8/13}",
                "  .arch{grid-column:1/8}.side{grid-column:9/13}\n  .trace{grid-column:1/8}.agent-side{grid-column:9/13}\n  .compare{grid-column:1/8}.proof{grid-column:9/13}\n  .hero-plate .plate-frame{aspect-ratio:4/5}"),
  ("1180 hero", "  .hero-plate{grid-column:8/13}", "  .hero-plate{grid-column:9/13}"),
  ("860 hero", "  .hero-plate{grid-column:1/13;grid-row:2;width:100%}",
               "  .hero-plate{grid-column:1/13;grid-row:2;width:100%}\n  .hero-plate .plate-frame{aspect-ratio:16/10}"),
]
for nm, o, n in grid_map:
    rep(nm, o, n, 1)

# ---------------------------------------------------------------- 8pt 间距
sp = [
  (".hero h1 26->24", ".hero h1{margin-top:26px}", ".hero h1{margin-top:24px}"),
  (".hero-lede 30->32", ".hero-lede{margin-top:30px;max-width:28em}", ".hero-lede{margin-top:32px;max-width:28em}"),
  (".hero-actions 34->32", ".hero-actions{display:flex;gap:12px;margin-top:34px}", ".hero-actions{display:flex;gap:12px;margin-top:32px}"),
  (".hero-meta 30->24", "margin-top:30px;font-size:var(--t-xs);color:var(--ink-3)}", "margin-top:24px;font-size:var(--t-xs);color:var(--ink-3)}"),
  (".hero-ledger 58->48", "border-top:1px solid var(--edge);margin-top:58px}", "border-top:1px solid var(--edge);margin-top:48px}"),
  (".lead pad 20->24", ".lead{position:relative;display:block;padding:20px 28px 0 0;", ".lead{position:relative;display:block;padding:24px 28px 0 0;"),
  (".lead h3 9->8", ".lead h3{margin-top:9px;", ".lead h3{margin-top:8px;"),
  (".sec 132->128", ".sec{padding:132px 0 0;position:relative}", ".sec{padding:128px 0 0;position:relative}"),
  (".sec idx 18->16", ".sec-head .idx{grid-column:1/4;grid-row:1;margin-bottom:18px}", ".sec-head .idx{grid-column:1/4;grid-row:1;margin-bottom:16px}"),
  (".side-index 22->24", ".side-index{display:block;margin-top:22px;", ".side-index{display:block;margin-top:24px;"),
  (".side h3 14->16", ".side h3{margin-top:14px;", ".side h3{margin-top:16px;"),
  (".arch-plate 26->24", ".arch-plate{width:100%;margin-bottom:26px}", ".arch-plate{width:100%;margin-bottom:24px}"),
  (".agent-plate 26->24", ".agent-plate{width:100%;margin-bottom:26px}", ".agent-plate{width:100%;margin-bottom:24px}"),
  (".agent-grid 56->48", ".agent-grid{display:grid;grid-template-columns:repeat(12,1fr);column-gap:24px;margin-top:56px}",
                          ".agent-grid{display:grid;grid-template-columns:repeat(12,1fr);column-gap:24px;margin-top:48px}"),
  (".lab-grid 26->24", ".lab-grid{display:grid;grid-template-columns:repeat(12,1fr);column-gap:24px;margin-top:26px}",
                        ".lab-grid{display:grid;grid-template-columns:repeat(12,1fr);column-gap:24px;margin-top:24px}"),
  (".res-meta 26->24", ".res-meta{display:flex;justify-content:space-between;margin-top:26px;", ".res-meta{display:flex;justify-content:space-between;margin-top:24px;"),
  (".log 26->24", ".log{margin-top:26px;", ".log{margin-top:24px;"),
  (".step pad", ".step{position:relative;display:block;width:100%;padding:20px 20px 20px 0;", ".step{position:relative;display:block;width:100%;padding:16px 20px 16px 0;"),
  (".ch pad", ".ch{position:relative;display:block;width:100%;padding:18px 16px 18px 0;", ".ch{position:relative;display:block;width:100%;padding:16px 16px 16px 0;"),
  (".ev-cap pad 14->16", ".ev-cap{display:flex;align-items:baseline;gap:14px;margin-top:24px;padding-top:14px;",
                          ".ev-cap{display:flex;align-items:baseline;gap:14px;margin-top:24px;padding-top:16px;"),
  (".ev-actions 30->32", ".ev-actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:30px}", ".ev-actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:32px}"),
  (".contact 150/110", ".contact{padding:150px 0 110px}", ".contact{padding:160px 0 96px}"),
  (".answer 18->16", ".answer{margin-top:18px;", ".answer{margin-top:16px;"),
  (".presets pad 5->6", ".presets button{font-size:12px;color:var(--ink-3);border:1px solid var(--hair);padding:5px 10px;",
                        ".presets button{font-size:12px;color:var(--ink-3);border:1px solid var(--hair);padding:6px 10px;"),
]
for nm, o, n in sp:
    rep(nm, o, n, 1)

# ---------------------------------------------------------------- 字号 token
ty = [
  (".lead h3", ".lead h3{margin-top:8px;font-size:20px;", ".lead h3{margin-top:8px;font-size:var(--t-h3);"),
  (".side h3", ".side h3{margin-top:16px;font-size:20px;", ".side h3{margin-top:16px;font-size:var(--t-h3);"),
  (".arch-row .nm", ".arch-row .nm{display:block;font-size:18px;", ".arch-row .nm{display:block;font-size:var(--t-lg);"),
  (".step b", ".step b{display:block;margin-top:12px;font-size:18px;", ".step b{display:block;margin-top:12px;font-size:var(--t-lg);"),
  (".trace h3", ".trace h3{margin-top:24px;font-size:24px;", ".trace h3{margin-top:24px;font-size:var(--t-h4);"),
  (".search input", "font-size:20px;color:var(--ink);padding:4px 0}", "font-size:var(--t-h3);color:var(--ink);padding:4px 0}"),
  (".answer", ".answer{margin-top:16px;font-size:20px;", ".answer{margin-top:16px;font-size:var(--t-h3);"),
  (".ev-head h2", ".ev-head h2{font-size:18px;", ".ev-head h2{font-size:var(--t-lg);"),
  (".ev-table c", "font-family:var(--f-serif);font-size:18px;text-align:right;padding-right:24px}", "font-family:var(--f-serif);font-size:var(--t-lg);text-align:right;padding-right:24px}"),
  ("1180 type", "  :root{--t-xxl:76px;--t-xl:48px;--t-num:150px;--gut:32px}", "  :root{--t-xxl:76px;--t-xl:48px;--t-num:150px;--gut:32px;--t-h4:22px;--t-h3:19px;--t-lg:17px}"),
  ("860 type", "  :root{--t-xxl:52px;--t-xl:34px;--t-num:96px;--gut:22px;--nav:56px}", "  :root{--t-xxl:52px;--t-xl:34px;--t-num:96px;--gut:22px;--nav:56px;--t-h4:20px;--t-h3:18px;--t-lg:16px}"),
]
for nm, o, n in ty:
    rep(nm, o, n, 1)

# ---------------------------------------------------------------- hover 缓动统一
rep("easing: 颜色/边框统一 -.22s var(--ease)", ".2s ease", ".22s var(--ease)")
rep("easing: .25s 补齐", ".25s ease", ".25s var(--ease)")

# ---------------------------------------------------------------- reveal 位移三档
rep("reveal: 位移量与元素尺度成正比",
    "html.js .rv:not(.in){opacity:0;transform:translate3d(0,14px,0)}",
    "html.js .rv:not(.in){opacity:0;transform:translate3d(0,var(--rv,14px),0)}\n"
    "h1.rv,h2.rv{--rv:26px}\n"
    ".plate.rv,.lead.rv,.metric.rv,.log.rv{--rv:8px}", 1)

# ---------------------------------------------------------------- Case 前后对比
rep("case: 负形 vs 面板",
    ".compare{grid-column:1/8;display:grid;grid-template-columns:1fr 1fr;column-gap:32px}",
    ".compare{grid-column:1/8;display:grid;grid-template-columns:1fr 1fr;column-gap:0}\n"
    ".before{padding-right:24px}\n"
    ".after{padding-left:24px;border-left:1px solid var(--hair)}\n"
    ".after .cmp-step h4::before{content:\"\";display:inline-block;width:5px;height:5px;background:var(--signal);margin-right:9px;vertical-align:middle}\n"
    ".before .cmp-step p,.before .cmp-step h4{opacity:.72}", 1)
rep("case: 移动端复位",
    "  .compare{grid-template-columns:1fr;gap:36px}",
    "  .compare{grid-template-columns:1fr;gap:36px}\n  .before{padding-right:0}\n  .after{padding-left:0;border-left:0}", 1)

# ---------------------------------------------------------------- nav 去掉无效 blur
rep("nav: 纯黑背景上的 blur 无收益",
    ".nav{position:fixed;inset:0 0 auto;z-index:80;height:var(--nav);background:rgba(13,12,10,.92);border-bottom:1px solid var(--hair);backdrop-filter:blur(10px)}",
    ".nav{position:fixed;inset:0 0 auto;z-index:80;height:var(--nav);background:rgba(13,12,10,.94);border-bottom:1px solid var(--hair)}", 1)

# ---------------------------------------------------------------- canvas 沉到正文之下
rep("canvas: z-index 4 -> 2（不再压住正文）", "z-index:4;pointer-events:none;opacity:0;", "z-index:2;pointer-events:none;opacity:0;", 1)

# ---------------------------------------------------------------- selectStack 挂接 3D
rep("hook: 列表 -> 物体", "  selectStack(0);", "  selectStack(0);\n  /* 列表与右侧物体是同一件事：选中哪一层的钩子由 3D 引擎注册 */", 1)
rep("hook: 调用", '  function selectStack(i){\n    var l=STACK[i];if(!l)return;',
                  '  function selectStack(i){\n    var l=STACK[i];if(!l)return;\n    if(layerHook)layerHook(i);', 1)

# ================================================================ 3D 重构
START = "  /* ---------- 3D: one machined object, one key light ---------- */"
END = '  if("requestAnimationFrame" in window)setTimeout(initEngine,120);'
a = s.index(START)
b = s.index(END)
assert a < b, "3D block markers out of order"

NEW3D = u'''  /* ---------- 3D: 一件机器，五层各自带着自己的数据形状 ---------- */
  var plates=$$("[data-plate]");
  var T=window.THREE;
  var layerHook=null;          /* selectStack 通过它把选中层告诉物体 */

  function makeEnvironment(){
    var c=document.createElement("canvas");c.width=1024;c.height=512;
    var g=c.getContext("2d");
    var lg=g.createLinearGradient(0,0,0,512);
    lg.addColorStop(0,"#5A544A");lg.addColorStop(0.40,"#3B352D");
    lg.addColorStop(0.55,"#221E19");lg.addColorStop(1,"#0A0908");
    g.fillStyle=lg;g.fillRect(0,0,1024,512);
    /* 地面反弹带：金属要有东西可以反射，否则只有高光是亮的，其余全是死黑 */
    var band=g.createLinearGradient(0,300,0,512);
    band.addColorStop(0,"rgba(226,212,190,0)");
    band.addColorStop(0.55,"rgba(226,212,190,.30)");
    band.addColorStop(1,"rgba(226,212,190,.06)");
    g.fillStyle=band;g.fillRect(0,300,1024,212);
    var keyL=g.createRadialGradient(292,148,8,292,148,252);
    keyL.addColorStop(0,"rgba(255,250,238,1)");
    keyL.addColorStop(0.28,"rgba(255,246,229,.76)");
    keyL.addColorStop(0.62,"rgba(255,243,223,.16)");
    keyL.addColorStop(1,"rgba(255,242,220,0)");
    g.fillStyle=keyL;g.fillRect(0,0,1024,512);
    var cool=g.createRadialGradient(806,214,4,806,214,172);
    cool.addColorStop(0,"rgba(206,220,236,.62)");
    cool.addColorStop(0.5,"rgba(200,214,230,.16)");
    cool.addColorStop(1,"rgba(200,214,230,0)");
    g.fillStyle=cool;g.fillRect(0,0,1024,512);
    /* 一条长形柔光箱：让圆柱面有一条连续不断的长高光 */
    g.save();g.translate(742,196);g.scale(0.085,1);
    var strip=g.createRadialGradient(0,0,0,0,0,230);
    strip.addColorStop(0,"rgba(255,250,238,.55)");
    strip.addColorStop(0.45,"rgba(255,248,236,.34)");
    strip.addColorStop(1,"rgba(255,248,236,0)");
    g.fillStyle=strip;g.beginPath();g.arc(0,0,230,0,Math.PI*2);g.fill();g.restore();
    var tex=new T.CanvasTexture(c);
    tex.mapping=T.EquirectangularReflectionMapping;
    if(T.SRGBColorSpace)tex.colorSpace=T.SRGBColorSpace;
    return tex;
  }

  function floorTexture(){
    var c=document.createElement("canvas");c.width=c.height=512;
    var g=c.getContext("2d");
    var rg=g.createRadialGradient(256,256,10,256,256,250);
    rg.addColorStop(0,"rgba(226,212,190,.15)");
    rg.addColorStop(0.30,"rgba(218,204,182,.09)");
    rg.addColorStop(0.44,"rgba(212,198,178,.03)");
    rg.addColorStop(0.52,"rgba(212,198,178,0)");
    rg.addColorStop(1,"rgba(212,198,178,0)");
    g.fillStyle=rg;g.fillRect(0,0,512,512);
    var tex=new T.CanvasTexture(c);
    if(T.SRGBColorSpace)tex.colorSpace=T.SRGBColorSpace;
    return tex;
  }

  function initEngine(){
    var canvas=$("#engineCanvas");
    if(!T||!window.WebGLRenderingContext)return;
    var renderer;
    try{
      renderer=new T.WebGLRenderer({canvas:canvas,alpha:true,antialias:true,powerPreference:"high-performance",stencil:false});
    }catch(e){return;}
    renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.75));
    renderer.autoClear=false;
    if(T.SRGBColorSpace)renderer.outputColorSpace=T.SRGBColorSpace;
    renderer.toneMapping=T.ACESFilmicToneMapping;
    renderer.toneMappingExposure=1.22;
    renderer.shadowMap.enabled=true;
    renderer.shadowMap.type=T.PCFSoftShadowMap;

    var scene=new T.Scene();
    scene.fog=new T.FogExp2(0x0C0B09,0.024);
    scene.environment=makeEnvironment();

    var camera=new T.PerspectiveCamera(30,1,0.1,60);
    camera.position.set(0.75,0.55,6.9);

    /* 只有两盏灯：一盏主光、一盏轮廓光。剩下的层次交给环境贴图。 */
    var key=new T.DirectionalLight(0xFFF1DE,2.5);
    key.position.set(-3.4,4.8,3.6);
    key.castShadow=true;
    key.shadow.mapSize.set(1024,1024);
    key.shadow.camera.left=-3.4;key.shadow.camera.right=3.4;
    key.shadow.camera.top=3.4;key.shadow.camera.bottom=-3.4;
    key.shadow.camera.near=0.5;key.shadow.camera.far=16;
    key.shadow.bias=-0.0012;key.shadow.radius=5;
    scene.add(key);
    var rim=new T.DirectionalLight(0xCBDCEC,1.3);rim.position.set(4.6,1.2,-3.4);scene.add(rim);

    /* 三种质感靠 roughness 分层，不靠多打灯 */
    var polished=new T.MeshStandardMaterial({color:0xB9B2A6,metalness:.92,roughness:.22,envMapIntensity:1.9});
    var matte   =new T.MeshStandardMaterial({color:0x2E2A25,metalness:.60,roughness:.62,envMapIntensity:1.1});
    var deep    =new T.MeshStandardMaterial({color:0x1D1A16,metalness:.50,roughness:.76,envMapIntensity:.75});
    var signal  =new T.MeshStandardMaterial({color:0xC97B45,emissive:0xC97B45,emissiveIntensity:.55,metalness:.35,roughness:.42,envMapIntensity:1.1});

    /* 渐隐不用 opacity（半透明金属会 ghosting），改为把颜色乘向黑：在纯黑背景上等价于淡出 */
    var fadeList=[];
    function reg(m,shadow){
      fadeList.push({m:m,c:m.color.clone(),e:m.envMapIntensity,ei:m.emissiveIntensity,op:m.opacity,shadow:!!shadow,mul:1});
    }
    [polished,matte,deep,signal].forEach(function(m){reg(m);});
    function applyFade(f){
      for(var i=0;i<fadeList.length;i++){
        var o=fadeList[i];
        if(o.shadow){o.m.opacity=o.op*f;continue;}
        o.m.color.copy(o.c).multiplyScalar(f*o.mul);
        o.m.envMapIntensity=o.e*f*o.mul;
        if(o.m.emissive)o.m.emissiveIntensity=o.ei*f;
      }
    }

    var rig=new T.Group();scene.add(rig);
    var core=new T.Group();rig.add(core);

    /* 轮廓保留原方案：一根主轴串起五片盘 */
    var profile=[
      [0.30,0.085],[1.05,0.085],[1.12,0.062],[1.17,0.033],
      [1.17,-0.033],[1.12,-0.062],[1.05,-0.085],[0.30,-0.085],[0.30,0.085]
    ].map(function(p){return new T.Vector2(p[0],p[1]);});
    var discGeo=new T.LatheGeometry(profile,128);
    discGeo.rotateX(Math.PI/2);

    var SEGS=5,SEG_GAP=0.262;
    var segs=[],rings=[];
    for(var i=0;i<SEGS;i++){
      var m=new T.Mesh(discGeo,i%2?matte:polished);
      m.castShadow=true;m.receiveShadow=true;
      m.position.z=(i-2)*SEG_GAP;
      m.userData.base=(i-2)*SEG_GAP;
      core.add(m);segs.push(m);
      var rm=signal.clone();rm.transparent=true;rm.opacity=0;reg(rm);
      var ring=new T.Mesh(new T.TorusGeometry(1.182,0.012,10,180),rm);
      ring.position.z=m.userData.base;core.add(ring);rings.push(ring);
    }

    var dummy=new T.Object3D();
    function instanced(geo,mat,count,place){
      var m=new T.InstancedMesh(geo,mat,count);
      for(var i=0;i<count;i++){
        dummy.position.set(0,0,0);dummy.rotation.set(0,0,0);dummy.scale.set(1,1,1);
        place(i,dummy);
        dummy.updateMatrix();m.setMatrixAt(i,dummy.matrix);
      }
      m.instanceMatrix.needsUpdate=true;
      return m;
    }

    /* 每层把自己的那一项数据变成几何：列表里的行号，就是物体上的形状 */
    function layerSlots(z,count){
      return instanced(new T.BoxGeometry(0.052,0.038,0.098),deep,count,function(i,d){
        var a=i/count*Math.PI*2;
        d.position.set(Math.cos(a)*1.116,Math.sin(a)*1.116,z);
        d.rotation.set(0,0,a);
      });
    }
    var portGeo=new T.CylinderGeometry(0.026,0.026,0.05,14);portGeo.rotateX(Math.PI/2);
    function layerPorts(z){
      var g=new T.Group();
      /* 52 个接口，分成 13 个一组 —— 13 个路由各带 4 个端点 */
      [1,-1].forEach(function(s){
        g.add(instanced(portGeo,deep,52,function(i,d){
          var grp=Math.floor(i/13),k=i%13;
          var a=grp*(Math.PI/2)+0.14+k*((Math.PI/2-0.28)/12);
          d.position.set(Math.cos(a)*0.76,Math.sin(a)*0.76,s*0.098);
        }));
      });
      return g;
    }
    function layerEtch(z){
      var g=new T.Group();
      /* 3,454 行：一圈极细的读写纹 */
      [1,-1].forEach(function(s){
        g.add(instanced(new T.BoxGeometry(0.46,0.0075,0.006),matte,84,function(i,d){
          var a=i/84*Math.PI*2;
          d.position.set(Math.cos(a)*0.72,Math.sin(a)*0.72,s*0.088);
          d.rotation.set(0,0,a);
        }));
      });
      return g;
    }
    function layerTracks(z){
      var g=new T.Group();
      /* 12 张表：12 条同心轨道 */
      [1,-1].forEach(function(s){
        for(var k=0;k<12;k++){
          var t=new T.Mesh(new T.TorusGeometry(0.44+k*0.052,0.0062,8,180),matte);
          t.position.z=s*0.088;g.add(t);
        }
      });
      return g;
    }
    function layerSlotsFive(z){
      /* 5 个容器：5 个定位卡槽 */
      return instanced(new T.BoxGeometry(0.10,0.078,0.17),deep,5,function(i,d){
        var a=i/5*Math.PI*2;
        d.position.set(Math.cos(a)*1.104,Math.sin(a)*1.104,z);
        d.rotation.set(0,0,a);
      });
    }

    var features=[layerSlots,layerPorts,layerEtch,layerTracks,layerSlotsFive];
    var fGroups=[];
    features.forEach(function(fn,i){
      var g=fn(segs[i].userData.base);
      g.userData.base=segs[i].userData.base;
      core.add(g);fGroups.push(g);
    });

    /* 保留原有的机加工齿圈 */
    var boltGeo=new T.BoxGeometry(0.042,0.070,0.105);
    var bolts=new T.InstancedMesh(boltGeo,polished,40);
    bolts.castShadow=true;
    for(var b=0;b<40;b++){
      var ang=b/40*Math.PI*2;
      dummy.position.set(Math.cos(ang)*1.098,Math.sin(ang)*1.098,0.190);
      dummy.rotation.set(0,0,ang);
      dummy.updateMatrix();
      bolts.setMatrixAt(b,dummy.matrix);
    }
    core.add(bolts);

    var shaft=new T.Mesh(new T.CylinderGeometry(0.125,0.125,2.40,48),polished);
    shaft.rotation.x=Math.PI/2;shaft.castShadow=true;shaft.receiveShadow=true;core.add(shaft);
    [1.20,-1.20].forEach(function(z){
      var cap=new T.Mesh(new T.CylinderGeometry(0.26,0.125,0.18,48),deep);
      cap.rotation.x=Math.PI/2*(z>0?1:-1);
      cap.position.z=z;
      cap.castShadow=true;core.add(cap);
    });

    /* 唯一的橙色件：随滚动沿主轴移动的那道环 */
    var collar=new T.Mesh(new T.CylinderGeometry(0.24,0.24,0.055,64),signal);
    collar.rotation.x=Math.PI/2;collar.position.z=0.72;core.add(collar);

    var floor=new T.Mesh(new T.PlaneGeometry(9,9),new T.MeshBasicMaterial({map:floorTexture(),transparent:true,depthWrite:false,opacity:1}));
    floor.rotation.x=-Math.PI/2;floor.position.set(0,-1.35,-1.5);floor.renderOrder=0;scene.add(floor);
    reg(floor.material);

    var shadowMat=new T.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.5,depthWrite:false});
    if(T.ShadowMaterial)shadowMat=new T.ShadowMaterial({color:0x000000,opacity:0.5,depthWrite:false});
    var shadowPlane=new T.Mesh(new T.PlaneGeometry(12,12),shadowMat);
    shadowPlane.rotation.x=-Math.PI/2;shadowPlane.position.set(0,-1.345,-1.5);shadowPlane.receiveShadow=true;shadowPlane.renderOrder=1;scene.add(shadowPlane);
    reg(shadowMat,true);

    /* 选中层：抽出并点亮 */
    var activeLayer=0;
    layerHook=function(i){activeLayer=i;};

    var state={unfold:0};
    var clock=0,last=performance.now(),running=true,unfoldMarks=[0,0,0];

    function smooth(t){return t*t*(3-2*t);}
    function measureUnfold(){
      ["hero","fullstack","agent"].forEach(function(id,i){
        var el=document.getElementById(id);
        if(!el){unfoldMarks[i]=0;return;}
        var r=el.getBoundingClientRect();
        unfoldMarks[i]=r.top+window.scrollY+r.height*0.5-window.innerHeight*0.5;
      });
    }
    function unfoldAt(){
      var y=window.scrollY,a=unfoldMarks[0],b=unfoldMarks[1],c=unfoldMarks[2];
      if(y<=a)return 0;
      if(y>=c)return 1;
      if(y<b)return 0.55*smooth((y-a)/Math.max(1,b-a));
      return 0.55+0.45*smooth((y-b)/Math.max(1,c-b));
    }
    /* 滚动渐入渐出：离画面中心越远越淡，边缘彻底退出 */
    function fadeFor(r){
      var vh=window.innerHeight||1;
      var d=Math.abs(r.top+r.height*0.5-vh*0.5)/(vh*0.62);
      var f=1-d;
      return f<=0?0:(f>=1?1:smooth(f));
    }
    function damp(a,b,l,dt){return b+(a-b)*Math.exp(-l*dt);}

    function frame(now){
      if(!running)return;
      requestAnimationFrame(frame);
      var dt=Math.min(0.05,(now-last)/1000);last=now;
      clock+=reduce?0:dt;

      state.unfold+=(unfoldAt()-state.unfold)*(1-Math.pow(0.0004,dt));
      var u=state.unfold;
      var sep=smooth(Math.min(1,u/0.62));

      segs.forEach(function(m,i){
        var base=m.userData.base;
        var push=(i<activeLayer)?-0.05:(i>activeLayer?0.05:0);
        var lift=(i===activeLayer)?0.075:0;
        var target=base+(i-2)*0.24*sep+push*sep+lift*sep;
        m.position.z=damp(m.position.z,target,7,dt);
        m.userData.cur=m.position.z;
        rings[i].position.z=m.position.z;
        rings[i].material.opacity=damp(rings[i].material.opacity,i===activeLayer?(0.35+0.55*sep):0,6,dt);
        rings[i].visible=rings[i].material.opacity>0.01;
        fGroups[i].position.z=m.position.z-fGroups[i].userData.base*0;
      });

      bolts.position.z=sep*0.24;
      collar.position.z=0.72+0.30*u;

      rig.rotation.x=-0.42-0.18*sep;
      rig.rotation.y=1.02+0.12*sep;
      core.rotation.z=clock*(0.045-0.018*u);
      core.rotation.y=Math.sin(clock*0.22)*0.05;

      camera.position.set(1.05-0.55*u,1.02+0.05*u,6.9+1.6*u);
      camera.lookAt(0,-0.26*sep,0);

      var list=[];
      plates.forEach(function(el){
        var fig=el.parentNode;
        var r=el.getBoundingClientRect();
        if(r.width<20||r.height<20){if(fig&&fig.style)fig.style.opacity="0";return;}
        var f=fadeFor(r);
        if(fig&&fig.style)fig.style.opacity=f<=0.02?"0":f.toFixed(3);
        if(f<=0.02)return;
        list.push({r:r,f:f});
      });

      renderer.setScissorTest(false);
      renderer.clear();
      if(!list.length)return;

      list.forEach(function(o){
        var r=o.r;
        applyFade(o.f);
        var x=Math.round(r.left),y=Math.round(window.innerHeight-r.bottom);
        var w=Math.round(r.width),h=Math.round(r.height);
        renderer.setViewport(x,y,w,h);
        renderer.setScissorTest(true);
        renderer.setScissor(x,y,w,h);
        renderer.clearDepth();
        camera.aspect=w/h;
        camera.updateProjectionMatrix();
        renderer.render(scene,camera);
      });
      renderer.setScissorTest(false);
    }

    function resize(){renderer.setSize(window.innerWidth,window.innerHeight,false);measureUnfold();}
    resize();
    addEventListener("resize",resize,{passive:true});
    document.addEventListener("visibilitychange",function(){
      running=!document.hidden;
      if(running){last=performance.now();requestAnimationFrame(frame);}
    });
    measureUnfold();
    if(document.fonts&&document.fonts.ready)document.fonts.ready.then(measureUnfold);
    document.documentElement.classList.add("webgl-ready");
    requestAnimationFrame(frame);
  }

'''
s = s[:a] + NEW3D + s[b:]
report.append("%-28s block replaced (%d chars)" % ("3D engine", len(NEW3D)))

io.open(SRC, "w", encoding="utf-8", newline="").write(s)

print("\n".join(report))
if fail:
    print("\nFAILED:")
    print("\n".join(fail))
    sys.exit(1)
print("\nOK")
