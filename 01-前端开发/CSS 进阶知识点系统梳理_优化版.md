---
title: CSS 进阶知识点系统梳理
tags: [前端, CSS, 布局, 动画, 响应式, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# CSS 进阶知识点系统梳理（优化版）

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。


> **文档说明**：系统梳理 CSS 进阶知识，涵盖 Flexbox、Grid、定位、BFC、动画、响应式、性能优化等核心内容。

---

## 1. 概述

CSS（Cascading Style Sheets）层叠样式表，用于描述 HTML 文档的呈现方式。从基础的样式美化，发展到如今支持复杂布局、动画、响应式设计的完整样式体系。

**发展阶段**：
- CSS 2.1：浮动、定位、基础选择器
- CSS3：Flexbox、Grid、动画、渐变、媒体查询
- 现代 CSS：容器查询、CSS 变量、subgrid、:has() 选择器

---


---
## 2. 盒模型

### 2.1 标准盒模型 vs IE 盒模型

```
标准盒模型（content-box）：width = 内容宽度
IE盒模型（border-box）：width = 内容 + padding + border
```

```css
* {
  box-sizing: border-box; /* 推荐全局设置，布局更直观 */
}
```


> 🔍 **知识点深度解析**
>
> **作用**：明确元素 width/height 到底包含哪些部分，是精确还原设计稿与排查布局错位的前提。
>
> **原理**：标准盒模型 content-box 的 width 仅指内容区，实际占位需再加 padding 与 border；IE 盒模型 border-box 的 width 已包含内容+padding+border，内容区被压缩。box-sizing 属性决定采用哪种模型。
>
> **用法要点**：① 全局推荐 *{box-sizing:border-box}，使设定宽度即实际宽度  ② content-box 下设宽后内容+padding+border 会超出预期宽度  ③ border-box 下增大 padding/border 不改变总宽，只挤占内容区  ④ 表单元素（input/select）默认盒模型不一致，需显式统一  ⑤ 面试常考两种模型区别与 box-sizing 取值

### 2.2 盒模型组成

`content` → `padding` → `border` → `margin`（外边距不计算在 width 内）

> 🔍 **知识点深度解析**
>
> **作用**：盒模型是 CSS 布局的基础，理解盒模型才能精准控制元素尺寸。
>
> **原理**：`box-sizing: content-box` 时，设置的 width 只是内容区宽度，元素实际占据宽度 = width + padding-left/right + border-left/right。`box-sizing: border-box` 时，width 包含内容+padding+border，内容区会自动缩小。全局设置 border-box 后，设置宽度就是元素实际宽度，布局更符合直觉。
>
> **用法要点**：① 推荐全局 `* { box-sizing: border-box; }`；② margin 会发生外边距折叠（相邻垂直 margin 取最大值）；③ 行内元素设置 width/height 无效，padding/margin 上下无效；④ 面试常考：两种盒模型区别、box-sizing 取值。

---


---
## 3. 定位（Position）

| 值 | 定位基准 | 是否脱离文档流 |
|----|----------|----------------|
| `static` | 默认，正常文档流 | 否 |
| `relative` | 相对于自身原位置 | 否（原位置保留） |
| `absolute` | 相对于最近的非 static 祖先 | 是 |
| `fixed` | 相对于视口 | 是 |
| `sticky` | 滚动到阈值时相对视口 | 否（阈值前在文档流） |

```css
.parent { position: relative; }
.child {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%); /* 绝对定位居中 */
}
```

> 🔍 **知识点深度解析**
>
> **作用**：定位是实现层叠、悬浮、固定元素的核心手段。
>
> **原理**：`position: absolute` 元素脱离文档流，相对于最近的 `position` 不为 `static` 的祖先元素定位，如果没有则相对于初始包含块（视口）。`fixed` 总是相对于视口（除非祖先有 transform 属性，则相对于该祖先）。`sticky` 是 relative 和 fixed 的结合——滚动到阈值前表现为 relative，达到阈值后表现为 fixed。
>
> **用法要点**：① absolute 父级必须设 relative（定位上下文）；② 绝对定位元素 margin: auto 可实现居中（需设宽高和 top/bottom/left/right: 0）；③ fixed 在有 transform 的祖先中会失效（变成 absolute）；④ sticky 需要设置 top/left 等阈值才生效；⑤ 面试常考：定位类型区别、sticky 原理、绝对定位居中。

---


---
## 4. BFC（块级格式化上下文）

### 4.1 什么是 BFC

BFC 是一个独立的渲染区域，内部元素的布局不会影响外部元素。


> 🔍 **知识点深度解析**
>
> **作用**：理解 BFC（块级格式化上下文）是掌握 margin 折叠、清除浮动、自适应两栏等布局问题的钥匙。
>
> **原理**：BFC 是一个独立的块级渲染区域，内部盒子按块格式化规则垂直排列且对外隔离——内部浮动不会影响外部，外部浮动也不会侵入其内部。
>
> **用法要点**：① BFC 是封闭的布局上下文，内部布局不影响外部  ② 同一 BFC 内相邻块级盒子的垂直 margin 会发生折叠  ③ 计算 BFC 高度时会包含其中的浮动元素  ④ 常与 IFC（行内格式化上下文）对比理解  ⑤ 面试常以“解决 margin 塌陷/清除浮动”引出

### 4.2 触发条件

- `overflow: hidden/auto/scroll`（非 visible）
- `float: left/right`（非 none）
- `position: absolute/fixed`
- `display: inline-block/table-cell/flex/grid`
- `contain: layout/content/paint`


> 🔍 **知识点深度解析**
>
> **作用**：知道如何主动创建 BFC，才能用它解决具体布局问题。
>
> **原理**：满足特定 CSS 条件时元素会生成新 BFC，如 overflow 非 visible、浮动、绝对/固定定位、display 为 flex/grid/inline-block 等。
>
> **用法要点**：① overflow:hidden/auto/scroll 最常用，但可能裁剪溢出内容  ② display:flex/grid 容器及其直接子项会形成 BFC  ③ float 非 none、position:absolute/fixed 也会触发  ④ display:flow-root 是专为创建 BFC 设计、无副作用的属性  ⑤ 现代布局优先用 flex/grid 而非 overflow hack

### 4.3 BFC 应用

1. **解决 margin 折叠**：父元素触发 BFC，子元素 margin 不会溢出
2. **清除浮动**：父元素触发 BFC，包含浮动子元素
3. **阻止元素被浮动覆盖**：两栏布局，右侧触发 BFC 不被左侧浮动覆盖

```css
/* 清除浮动 */
.clearfix::after {
  content: '';
  display: block;
  clear: both;
}
```

> 🔍 **知识点深度解析**
>
> **作用**：BFC 是 CSS 布局的重要概念，理解 BFC 能解决很多布局问题。
>
> **原理**：BFC（Block Formatting Context）是 Web 页面中盒模型布局的一种渲染规则，它是一个独立的区域，内部块级盒子垂直排列，内部浮动不会影响外部，外部浮动也不会侵入。BFC 区域在计算高度时会包含浮动元素（所以能清除浮动），且 BFC 区域不会与浮动元素重叠（所以能实现两栏自适应）。
>
> **用法要点**：① 最常用触发方式 `overflow: hidden`，但可能裁剪内容；② 现代布局用 Flex/Grid 天然形成 BFC，不需要 hack；③ 面试常考：BFC 定义、触发条件、应用场景；④ IFC（行内格式化上下文）是行内元素的布局规则，了解即可。

---


---
## 5. Flexbox 布局

### 5.1 容器属性

```css
.container {
  display: flex;
  flex-direction: row | row-reverse | column | column-reverse;
  flex-wrap: nowrap | wrap | wrap-reverse;
  justify-content: flex-start | center | flex-end | space-between | space-around | space-evenly;
  align-items: stretch | flex-start | center | flex-end | baseline;
  align-content: stretch | flex-start | center | flex-end | space-between | space-around; /* 多行时 */
}
```


> 🔍 **知识点深度解析**
>
> **作用**：Flex 容器属性决定子项整体的排列方向、换行与对齐，是一维布局的“主轴控制”。
>
> **原理**：Flex 容器存在主轴（main axis，由 flex-direction 决定方向）与交叉轴（cross axis）。justify-content 控制主轴分布，align-items 控制交叉轴对齐，flex-wrap 控制是否换行。
>
> **用法要点**：① flex-direction 决定主轴方向（row/column）  ② justify-content 管主轴（center 居中、space-between 两端）  ③ align-items 管交叉轴（center 居中、stretch 拉伸）  ④ 多行时 align-content 控制行与行之间的分布  ⑤ 容器设 display:flex 后，子项 float/clear/vertical-align 失效

### 5.2 子项属性

```css
.item {
  flex-grow: 0; /* 放大比例 */
  flex-shrink: 1; /* 缩小比例 */
  flex-basis: auto; /* 初始大小 */
  flex: 0 1 auto; /* 简写 */
  align-self: auto | flex-start | center | flex-end | stretch; /* 单独对齐 */
  order: 0; /* 排列顺序，越小越靠前 */
}
```


> 🔍 **知识点深度解析**
>
> **作用**：子项属性在容器规则基础上对单个元素做精细控制（放大、缩小、排序、单独对齐）。
>
> **原理**：flex-grow 分配主轴剩余空间，flex-shrink 在空间不足时收缩，flex-basis 设定初始主轴尺寸；最终尺寸 = basis + grow/shrink 调整。order 改变视觉顺序，align-self 覆盖容器 align-items。
>
> **用法要点**：① flex:1 = flex:1 1 0%，按剩余空间比例平分  ② flex-basis 优先级高于 width（主轴为 row 时）  ③ flex-shrink:0 防止被压缩，用于固定宽栏  ④ order 仅改视觉顺序，不影响 DOM 与可访问性顺序  ⑤ align-self 可对单个子项单独设置交叉轴对齐

### 5.3 经典布局

```css
/* 水平垂直居中 */
.center { display: flex; justify-content: center; align-items: center; }

/* 两栏布局：左固定右自适应 */
.two-col { display: flex; }
.left { width: 200px; flex-shrink: 0; }
.right { flex: 1; }

/* 等高布局 */
.equal-height { display: flex; align-items: stretch; }
```

> 🔍 **知识点深度解析**
>
> **作用**：Flexbox 是一维布局的首选方案，取代了传统的浮动+定位布局。
>
> **原理**：Flex 容器有主轴（main axis）和交叉轴（cross axis），`flex-direction` 决定主轴方向。子项在主轴上的排列由 `justify-content` 控制，交叉轴由 `align-items` 控制。`flex-grow` 定义剩余空间分配比例，`flex-shrink` 定义空间不足时的收缩比例，`flex-basis` 定义初始大小。`flex: 1` 等于 `flex: 1 1 0%`，表示可放大可缩小，初始大小 0（平分剩余空间）。
>
> **用法要点**：① 设了 flex: 1 的元素，width 不生效（被 flex-basis: 0 覆盖）；② flex-shrink: 0 防止元素被压缩（固定宽度栏常用）；③ 多行布局用 flex-wrap: wrap，行间距用 gap；④ 面试常考：flex 属性含义、居中方案、两栏布局实现。

---


---
## 6. Grid 布局

### 6.1 容器属性

```css
.grid {
  display: grid;
  grid-template-columns: 200px 1fr 200px; /* 三列 */
  grid-template-rows: auto 1fr auto; /* 三行 */
  gap: 20px; /* 间距 */
  justify-items: stretch | start | center | end; /* 单元格内水平 */
  align-items: stretch | start | center | end; /* 单元格内垂直 */
  justify-content: start | center | end | space-between; /* 整个网格水平 */
  align-content: start | center | end | space-between; /* 整个网格垂直 */
}
```


> 🔍 **知识点深度解析**
>
> **作用**：Grid 容器属性定义网格的行列轨道、间距与整体对齐，是二维布局的骨架。
>
> **原理**：display:grid 将容器划分为行轨道（grid-template-rows）和列轨道（grid-template-columns）组成的二维网格；fr 表示剩余空间比例；gap 统一设置间距。
>
> **用法要点**：① grid-template-columns/rows 用长度、fr 或 repeat() 定义轨道  ② repeat(3,1fr) 等价于 1fr 1fr 1fr  ③ fr 是剩余空间比例，可配合固定值做混合布局  ④ justify/align-items 控制单元格内对齐，content 系列控制整个网格分布  ⑤ 响应式可用 repeat(auto-fill/auto-fit, minmax())

### 6.2 子项属性

```css
.item {
  grid-column: 1 / 3; /* 从第1列线到第3列线（跨2列） */
  grid-row: 1 / 2;
  grid-area: header; /* 命名区域 */
  justify-self: center; /* 单独水平对齐 */
  align-self: center; /* 单独垂直对齐 */
}
```


> 🔍 **知识点深度解析**
>
> **作用**：Grid 子项属性让单个元素跨越指定行列或占据命名区域，实现复杂版式。
>
> **原理**：grid-column/grid-row 用“起始线/结束线”指定子项占据的网格区间（线编号从 1 开始）；grid-area 可引用 grid-template-areas 定义的命名区域；justify-self/align-self 单独控制对齐。
>
> **用法要点**：① grid-column:1/3 表示跨第1到第3列线（占2列）  ② 线编号可用负数表示从末尾倒数  ③ grid-area 四值简写：row-start/col-start/row-end/col-end  ④ 命名区域法（grid-template-areas）可读性最好  ⑤ justify-self/align-self 覆盖容器对单个子项的对齐

### 6.3 网格区域命名

```css
.layout {
  display: grid;
  grid-template-areas:
    "header header header"
    "sidebar main main"
    "footer footer footer";
  grid-template-columns: 200px 1fr 1fr;
  grid-template-rows: auto 1fr auto;
}
.header { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main { grid-area: main; }
.footer { grid-area: footer; }
```

> 🔍 **知识点深度解析**
>
> **作用**：Grid 是二维布局系统，适合复杂的页面整体布局，与 Flex（一维）互补。
>
> **原理**：Grid 将容器划分为行和列形成网格，子项通过 `grid-column/row` 或 `grid-area` 指定占据的单元格。`fr` 单位表示剩余空间的比例（fraction），`1fr 2fr` 表示按 1:2 分配。`grid-template-areas` 用字符串可视化定义布局区域，是 Grid 最强大的功能之一。`auto-fill` 和 `auto-fit` 配合 `minmax()` 可实现响应式网格，无需媒体查询。
>
> **用法要点**：① 一维布局用 Flex，二维布局用 Grid；② `repeat(3, 1fr)` = `1fr 1fr 1fr`；③ `minmax(200px, 1fr)` 最小 200px，最大 1fr；④ `auto-fill` 尽可能多创建列（有空列），`auto-fit` 空列会被折叠（元素拉伸）；⑤ 面试常考：Grid 与 Flex 区别、grid-template-areas 用法、响应式网格实现。

---


---
## 7. 响应式设计

### 7.1 媒体查询

```css
/* 移动端优先 */
.container { width: 100%; }
@media (min-width: 768px) { .container { width: 750px; } }
@media (min-width: 1024px) { .container { width: 970px; } }

/* 常用断点 */
/* < 576px: 手机 */
/* 576-768px: 大屏手机 */
/* 768-1024px: 平板 */
/* 1024-1440px: 笔记本 */
/* > 1440px: 桌面 */
```


> 🔍 **知识点深度解析**
>
> **作用**：媒体查询是响应式设计的开关，按设备视口/特性加载不同样式。
>
> **原理**：@media 在满足条件（min/max-width、orientation、resolution 等）时应用内部样式块；移动端优先用 min-width 由小到大增强，PC 优先用 max-width 由大到小降级。
>
> **用法要点**：① 移动端优先推荐 min-width，避免大屏冗余覆盖  ② 断点应按内容而非具体设备设定（如 768/1024）  ③ 常用条件 width、height、orientation、prefers-reduced-motion  ④ 可组合多个条件用 and / ,（或）  ⑤ 媒体查询只切换样式、无法改变 DOM 结构

### 7.2 视口设置

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```


> 🔍 **知识点深度解析**
>
> **作用**：viewport meta 标签控制移动端页面按设备宽度渲染，是响应式的前提。
>
> **原理**：默认移动浏览器以约 980px 的“布局视口”渲染再缩放；width=device-width 让布局视口等于设备宽度，initial-scale=1 设初始缩放为 1，从而避免页面被缩扁。
>
> **用法要点**：① 移动端必须加 <meta name=viewport content=width=device-width,initial-scale=1>  ② width=device-width 使 CSS 像素映射设备宽度  ③ maximum-scale/user-scalable 可禁缩放（影响可访问性，慎用）  ④ 需配合 rem/vw 方案才能实现等比适配  ⑤ 缺失它会让媒体查询基于桌面视口，布局错乱

### 7.3 相对单位

| 单位 | 基准 |
|------|------|
| `%` | 父元素 |
| `em` | 自身 font-size（继承） |
| `rem` | 根元素 html 的 font-size |
| `vw/vh` | 视口宽/高的 1% |
| `vmin/vmax` | 视口较小/较大边的 1% |


> 🔍 **知识点深度解析**
>
> **作用**：相对单位让尺寸随上下文（父/根/视口）伸缩，是流式布局与等比适配的基础。
>
> **原理**：% 相对父元素；em 相对自身 font-size（易层层放大）；rem 相对根元素 html 的 font-size（可控）；vw/vh 相对视口宽高；vmin/vmax 取视口较小/较大边。
>
> **用法要点**：① rem 适配：动态设 html font-size，全站用 rem 实现等比缩放  ② em 受父级 font-size 影响，嵌套需谨慎  ③ vw/vh 适合全屏与流体字号，但极端宽屏需 clamp 限制  ④ vmin/vmax 用于需兼顾横竖屏的场景  ⑤ 与媒体查询/容器查询配合覆盖不同断点

### 7.4 图片响应式

```css
img { max-width: 100%; height: auto; }

/* <picture> 元素：根据设备选择不同图片 */
<picture>
  <source media="(min-width: 1024px)" srcset="large.jpg">
  <source media="(min-width: 768px)" srcset="medium.jpg">
  <img src="small.jpg" alt="响应式图片">
</picture>
```

> 🔍 **知识点深度解析**
>
> **作用**：响应式设计让页面在不同设备上都有良好体验，是现代前端必备技能。
>
> **原理**：媒体查询根据设备特性（宽度、高度、方向、分辨率等）应用不同样式。移动端优先（mobile first）是从最小屏幕开始设计，逐步增强。rem 方案通过动态设置 html 的 font-size（用 JS 或媒体查询），实现等比缩放。vw/vh 直接基于视口，更简单但兼容性需注意。容器查询（container queries）是未来趋势，基于父容器宽度而非视口。
>
> **用法要点**：① 移动端优先用 min-width，PC 优先用 max-width；② rem 适配方案：设计稿 750px，html font-size = 屏幕宽度 / 7.5；③ 1px 边框问题用 transform: scale(0.5) 或 border-image；④ 图片用 max-width: 100% 防止溢出；⑤ 面试常考：响应式方案、rem 原理、媒体查询断点。

---


---
## 8. CSS 动画

### 8.1 transition 过渡

```css
.box {
  transition: property duration timing-function delay;
  transition: all 0.3s ease;
  transition: transform 0.3s ease, opacity 0.5s ease;
}
```


> 🔍 **知识点深度解析**
>
> **作用**：transition 让属性在状态变化时平滑过渡，用于 hover、展开等轻量动效。
>
> **原理**：transition 监听指定属性从旧值到新值的变化，在 duration 内按 timing-function 插值；仅在属性“值改变”时触发，首次渲染不生效。
>
> **用法要点**：① 语法：transition: 属性 时长 缓动 延迟  ② 可写 all 或指定属性（推荐指定，性能更可控）  ③ 仅对可插值属性生效（颜色、transform、尺寸），display 不可过渡  ④ 回退状态用 opacity+visibility 代替 display:none  ⑤ 配合 will-change 可提前提升合成层（勿滥用）

### 8.2 animation 关键帧动画

```css
@keyframes slideIn {
  from { transform: translateX(-100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

.element {
  animation: slideIn 0.5s ease forwards;
  /* animation: name duration timing-function delay iteration-count direction fill-mode play-state */
}
```


> 🔍 **知识点深度解析**
>
> **作用**：animation + @keyframes 实现多关键帧、可循环的复杂动画，比 transition 更自由。
>
> **原理**：@keyframes 定义动画在 0%→100% 各阶段的样式，animation 将其绑定到元素并控制时长、缓动、次数、方向、填充模式；浏览器在每帧计算插值并渲染。
>
> **用法要点**：① @keyframes 用 from/to 或百分比定义关键帧  ② animation 简写：name duration timing delay iteration direction fill-mode  ③ forwards 让动画结束后保持终态  ④ infinite 无限循环，alternate 来回播放  ⑤ 优先动画 transform/opacity 以走合成层、避免重排重绘

### 8.3 性能优化

**优先使用 transform 和 opacity**，它们只触发合成（composite），不触发重排重绘。

```css
/* 好：GPU 加速 */
transform: translateX(100px);
opacity: 0.5;

/* 差：触发重排 */
left: 100px;
margin-left: 100px;
```

> 🔍 **知识点深度解析**
>
> **作用**：CSS 动画提升交互体验，性能优化是关键。
>
> **原理**：浏览器渲染流程：Layout（布局/重排）→ Paint（绘制/重绘）→ Composite（合成）。修改 width/height/left 等属性会触发 Layout（性能最差），修改 background/color 触发 Paint，修改 transform/opacity 只触发 Composite（性能最好，GPU 加速）。`will-change: transform` 提前告知浏览器该元素会变化，提前优化，但不要滥用（消耗内存）。
>
> **用法要点**：① 动画优先用 transform 和 opacity；② 避免在动画中用 display: none（无过渡效果，用 opacity + visibility）；③ `animation-fill-mode: forwards` 保持动画结束状态；④ 无限循环用 `animation-iteration-count: infinite`；⑤ 过渡只在属性变化时生效，首次渲染不生效；⑥ 面试常考：重排重绘区别、动画性能优化、transform 原理。

---


---
## 9. 选择器优先级

### 9.1 优先级计算

`!important` > 行内样式（1000）> ID（100）> 类/属性/伪类（10）> 标签/伪元素（1）> 通配符（0）


> 🔍 **知识点深度解析**
>
> **作用**：掌握优先级才能预判哪条样式生效，快速定位“样式不生效”类问题。
>
> **原理**：CSS 按（行内, ID, 类/属性/伪类, 标签/伪元素）四元组权重比较，高位相同才比低位；!important 可压过一切（除更高优先级 !important）；同权重后写覆盖先写。
>
> **用法要点**：① 权重顺序：!important > 行内(1000) > ID(100) > 类(10) > 标签(1) > 通配符(0)  ② 权重是逐位比较而非简单相加，10 个类胜不了 1 个 ID  ③ 内联 style 优先级极高、难覆盖  ④ 避免过度嵌套导致优先级失控  ⑤ 调试用 DevTools 的“计算样式”查看命中规则

### 9.2 常用选择器

```css
/* 后代选择器 */
.parent .child { }
/* 子选择器 */
.parent > .child { }
/* 相邻兄弟 */
.item + .item { }
/* 通用兄弟 */
.item ~ .item { }
/* 属性选择器 */
input[type="text"] { }
a[href^="https"] { } /* 开头 */
a[href$=".pdf"] { } /* 结尾 */
a[href*="google"] { } /* 包含 */
/* 伪类 */
:hover, :focus, :active, :nth-child(n), :not(selector), :has(selector)
/* 伪元素 */
::before, ::after, ::first-line, ::selection
```

> 🔍 **知识点深度解析**
>
> **作用**：理解选择器优先级才能写出可维护的 CSS，避免样式冲突。
>
> **原理**：CSS 优先级用四个维度的权重计算（a, b, c, d），分别对应 !important、行内、ID、类/属性/伪类、标签/伪元素。比较时从高位开始，高位相同再比低位。注意优先级不是简单的数字相加（10个类不会超过1个ID），而是逐位比较。同优先级时，后面的样式覆盖前面的。
>
> **用法要点**：① 不要滥用 !important，会破坏优先级体系；② 推荐用类选择器，避免 ID（复用性差）；③ CSS Modules / BEM 命名规范解决优先级冲突；④ `:has()` 是父选择器（2023年主流浏览器支持），革命性特性；⑤ 面试常考：优先级计算、伪类与伪元素区别、:nth-child 用法。

---


---
## 10. CSS 变量与现代特性

### 10.1 CSS 自定义属性（变量）

```css
:root {
  --primary-color: #3498db;
  --spacing: 16px;
}

.button {
  background: var(--primary-color);
  padding: var(--spacing);
}

/* JS 操作 CSS 变量 */
document.documentElement.style.setProperty('--primary-color', '#e74c3c');
```


> 🔍 **知识点深度解析**
>
> **作用**：CSS 变量实现一处定义、多处复用，是主题切换与设计 token 化的基础。
>
> **原理**：自定义属性以 --name 声明（常放 :root 作为全局），用 var(--name[, fallback]) 引用；变量可继承，可被 JS 通过 style.setProperty 动态修改，从而实时换肤。
>
> **用法要点**：① 声明：--primary:#3498db，使用：color:var(--primary)  ② :root 声明的变量全局可用  ③ var() 第二个参数为回退值（变量未定义时生效）  ④ JS 改主题：document.documentElement.style.setProperty('--primary', x)  ⑤ 结合 calc() 可做数学运算；变量区分大小写

### 10.2 现代 CSS 特性

- `aspect-ratio`：宽高比
- `gap`：Flex/Grid 间距
- `clamp(min, preferred, max)`：流体排版
- `min()/max()`：动态计算
- `:is()` / `:where()`：选择器分组
- `backdrop-filter`：毛玻璃效果
- `subgrid`：嵌套网格继承

```css
/* 流体字号：最小14px，理想2vw，最大20px */
font-size: clamp(14px, 2vw, 20px);

/* 毛玻璃 */
.glass {
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
}
```

---


> 🔍 **知识点深度解析**
>
> **作用**：现代 CSS 特性减少 JS 依赖，用声明式方式解决比例、流体排版、毛玻璃等常见需求。
>
> **原理**：aspect-ratio 固定宽高比；clamp(min,pref,max) 在上下限间选取首选值（流体排版）；min()/max() 取极值；:is()/:where() 分组选择器（:where 权重为 0）；backdrop-filter 对元素后方做模糊；subgrid 让嵌套网格继承父轨道。
>
> **用法要点**：① clamp(14px,2vw,20px) 实现随视口缩放但有界的字号  ② aspect-ratio 替代 padding-top hack 做响应式盒子  ③ backdrop-filter:blur() 实现毛玻璃（注意性能与背景要求）  ④ :where() 权重为 0，适合写重置样式  ⑤ subgrid 需父网格支持，用于对齐嵌套内容；这些特性需关注兼容并加回退


---
## 11. 面试高频考点

1. **盒模型**：标准 vs IE，box-sizing
2. **居中方案**：水平垂直居中的 N 种实现
3. **BFC**：定义、触发、应用
4. **Flex**：flex 属性、布局实现
5. **Grid**：与 Flex 区别、grid-template-areas
6. **定位**：absolute/fixed/sticky 区别
7. **重排重绘**：区别、性能优化
8. **响应式**：rem/vw、媒体查询
9. **选择器优先级**：计算规则
10. **动画**：transition vs animation、性能

---


---
## 📝 精简总结

- 盒模型是布局基础，推荐 border-box
- BFC 解决 margin 折叠和浮动问题
- Flex 一维布局，Grid 二维布局，互补使用
- 定位实现层叠和特殊定位，sticky 是吸顶方案
- 响应式用媒体查询 + 相对单位，移动端优先
- 动画优先 transform/opacity，避免重排重绘
- CSS 变量实现主题切换，现代 CSS 持续进化

---

[[01-前端开发/MOC-前端开发|← 返回前端开发 MOC]] | [[Home|🏠 返回首页]]
