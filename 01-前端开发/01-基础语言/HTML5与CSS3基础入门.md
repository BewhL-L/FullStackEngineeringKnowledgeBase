---
title: HTML5与CSS3基础入门
tags: [HTML5, CSS3, 前端, 网页开发, 响应式, Flexbox, Grid, 原子笔记]
category: 前端开发
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[前端开发学习路线图]]"]
aliases: [HTML5与CSS3基础入门]
---

# HTML5与CSS3基础入门

> **文档说明**：系统讲解 HTML5 与 CSS3 前端基础，包括 HTML5 新特性（语义化标签、表单、多媒体、Canvas、SVG、Web API）、常用标签、CSS 选择器、盒模型、CSS3 新特性（Flexbox、Grid、动画、过渡、变换、渐变）、响应式设计，以及最佳实践和常见问题。
>
> **适用人群**：前端零基础入门者、全栈开发者、需要了解前端基础的后端/AI 工程师
>
> **前置知识**：[[前端开发学习路线图]]

---

## 一、HTML 概述

### 1. HTML 是什么

```text
HTML（HyperText Markup Language，超文本标记语言）：
- 网页的标准标记语言
- 由 Tim Berners-Lee 于 1991 年创建
- 定义网页的结构和内容
- 不是编程语言，是标记语言（用标签描述内容）

HTML 历史版本：
- HTML 1.0（1991）：最初版本，18 个标签
- HTML 2.0（1995）：标准化
- HTML 3.2（1997）：W3C 推荐标准
- HTML 4.0（1997）：支持 CSS、脚本
- HTML 4.01（1999）：小幅修订
- XHTML 1.0（2000）：更严格的 XML 格式
- HTML5（2014）：W3C 正式推荐标准，重大革新
- HTML 5.2/5.3（2017+）：持续更新

HTML5 的核心革新：
1. 语义化标签：<header>、<nav>、<article>、<section>、<footer>
2. 多媒体原生支持：<audio>、<video>，不再依赖 Flash
3. 表单增强：新输入类型（email、date、range）、验证属性
4. 图形绘制：<canvas>（2D 绘图）、<svg>（矢量图）
5. Web API：Web Storage、IndexedDB、Geolocation、Web Workers、WebSocket
6. 离线应用：Application Cache（已废弃，改用 Service Worker）
7. 拖放 API：原生拖放支持
8. 历史管理：History API（SPA 路由基础）
```

### 2. HTML5 文档基本结构

```html
<!DOCTYPE html>
<!-- 文档类型声明，告诉浏览器这是 HTML5 文档 -->

<html lang="zh-CN">
<!-- 根元素，lang 属性指定语言（有助于搜索引擎和屏幕阅读器） -->

<head>
    <!-- 头部：元数据，不显示在页面上 -->
    <meta charset="UTF-8">
    <!-- 字符编码，必须放在最前面，避免乱码 -->

    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- 视口设置，响应式设计必备 -->

    <meta name="description" content="这是一个示例网页">
    <!-- 页面描述，用于搜索引擎 -->

    <meta name="keywords" content="HTML, CSS, 前端">
    <!-- 关键词（SEO 作用已减弱） -->

    <meta name="author" content="Your Name">
    <!-- 作者 -->

    <title>网页标题</title>
    <!-- 浏览器标签页标题 -->

    <link rel="stylesheet" href="style.css">
    <!-- 引入外部 CSS -->

    <link rel="icon" href="favicon.ico" type="image/x-icon">
    <!-- 网站图标 -->

    <style>
        /* 内联 CSS（不推荐，仅示例） */
        body { font-family: sans-serif; }
    </style>
</head>

<body>
    <!-- 主体：页面可见内容 -->

    <header>
        <!-- 页眉 -->
        <h1>网站标题</h1>
        <nav>
            <!-- 导航 -->
            <ul>
                <li><a href="/">首页</a></li>
                <li><a href="/about">关于</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <!-- 主要内容 -->
        <article>
            <!-- 文章 -->
            <h2>文章标题</h2>
            <p>这是一段文字。</p>
        </article>

        <aside>
            <!-- 侧边栏 -->
            <h3>相关链接</h3>
        </aside>
    </main>

    <footer>
        <!-- 页脚 -->
        <p>&copy; 2024 版权所有</p>
    </footer>

    <script src="script.js"></script>
    <!-- 引入外部 JS，放在 body 末尾确保 DOM 已加载 -->
</body>

</html>
```

---

## 二、HTML5 常用标签

### 1. 语义化标签

```text
HTML5 语义化标签的价值：
- 结构清晰，可读性好
- 有利于 SEO（搜索引擎理解页面结构）
- 无障碍访问（屏幕阅读器）
- 代码维护性好

常用语义化标签：

1. <header>：页眉/头部
   - 页面或区块的头部
   - 可包含标题、导航、Logo、搜索框
   - 一个页面可以有多个 <header>

2. <nav>：导航
   - 主要导航链接
   - 一个页面可以有多个（主导航、页脚导航）
   - 不是所有链接都放 <nav>，只放主要导航

3. <main>：主要内容
   - 页面的核心内容
   - 一个页面只能有一个 <main>
   - 排除页眉、页脚、侧边栏、导航

4. <article>：文章/独立内容
   - 独立的、可单独分发的内容
   - 博客文章、新闻、论坛帖子、评论
   - 可以嵌套（文章中的评论）

5. <section>：区块/章节
   - 主题性的内容分组
   - 通常有标题
   - 不要用作样式容器（用 <div>）

6. <aside>：侧边栏/补充内容
   - 与主要内容间接相关
   - 侧边栏、广告、相关链接、引用

7. <footer>：页脚/底部
   - 页面或区块的底部
   - 版权、联系方式、相关链接
   - 一个页面可以有多个

8. <figure> + <figcaption>：图像/图表
   - <figure>：独立的流内容（图像、图表、代码块）
   - <figcaption>：标题/说明
   - 示例：
     <figure>
       <img src="chart.png" alt="数据图表">
       <figcaption>2024年销售数据</figcaption>
     </figure>

9. <time>：时间/日期
   - 表示时间或日期
   - datetime 属性：机器可读的时间
   - 示例：<time datetime="2024-01-15">2024年1月15日</time>

10. <mark>：高亮标记
    - 高亮显示文本（默认黄色背景）
    - 用于引用中的重点、搜索结果高亮

11. <details> + <summary>：可折叠内容
    - <details>：可展开/折叠的内容
    - <summary>：可见的标题
    - 原生支持，无需 JS
    - 示例：
      <details>
        <summary>点击展开</summary>
        <p>这里是隐藏的内容</p>
      </details>

12. <progress>：进度条
    - 表示任务进度
    - value / max 属性
    - 示例：<progress value="70" max="100">70%</progress>

13. <meter>：计量器
    - 表示已知范围内的标量测量
    - 如磁盘使用量、投票比例
    - 示例：<meter value="0.6">60%</meter>
```

### 2. 文本标签

```html
<!-- 标题：h1-h6，h1 最重要，一个页面通常一个 h1 -->
<h1>一级标题</h1>
<h2>二级标题</h2>
<h3>三级标题</h3>
<h4>四级标题</h4>
<h5>五级标题</h5>
<h6>六级标题</h6>

<!-- 段落 -->
<p>这是一个段落。</p>

<!-- 换行（不推荐滥用，用 CSS 控制间距） -->
<p>第一行<br>第二行</p>

<!-- 水平线 -->
<hr>

<!-- 文本格式 -->
<strong>重要文本（加粗，语义强调）</strong>
<em>强调文本（斜体，语义强调）</em>
<b>加粗文本（仅样式，无语义）</b>
<i>斜体文本（仅样式）</i>
<u>下划线</u>
<s>删除线</s>
<small>小号文本（免责声明、版权）</small>
<sub>下标</sub>  <!-- H<sub>2</sub>O -->
<sup>上标</sup>  <!-- E=mc<sup>2</sup> -->
<code>代码文本</code>
<kbd>键盘输入</kbd>  <!-- <kbd>Ctrl+C</kbd> -->
<samp>程序输出</samp>
<var>变量</var>
<blockquote cite="来源URL">
    长引用（块级，自动缩进）
</blockquote>
<q>短引用（行内，自动加引号）</q>
<abbr title="HyperText Markup Language">HTML</abbr>  <!-- 缩写，鼠标悬停显示全称 -->
<address>联系地址信息</address>
<cite>作品标题（书籍、电影）</cite>
<dfn>定义术语</dfn>

<!-- 列表 -->
<!-- 无序列表 -->
<ul>
    <li>列表项 1</li>
    <li>列表项 2</li>
</ul>

<!-- 有序列表 -->
<ol>
    <li>第一步</li>
    <li>第二步</li>
</ol>

<!-- 定义列表 -->
<dl>
    <dt>术语</dt>
    <dd>术语的定义</dd>
</dl>

<!-- 链接 -->
<a href="https://example.com" target="_blank" rel="noopener noreferrer">外部链接</a>
<a href="#section1">锚点链接</a>
<a href="mailto:test@example.com">邮件链接</a>
<a href="tel:1234567890">电话链接</a>
<a href="document.pdf" download>下载文件</a>

<!-- 图片 -->
<img src="image.jpg" alt="图片描述（必填，无障碍）" width="300" height="200" loading="lazy">

<!-- 图片映射（可点击区域） -->
<img src="map.jpg" usemap="#workmap" alt="工作区地图">
<map name="workmap">
    <area shape="rect" coords="34,44,270,350" alt="电脑" href="computer.htm">
    <area shape="circle" coords="337,300,44" alt="咖啡" href="coffee.htm">
</map>
```

### 3. 表单标签

```html
<!-- 表单基本结构 -->
<form action="/submit" method="post" enctype="multipart/form-data">
    <!-- action：提交地址；method：GET/POST；enctype：编码类型（文件上传需 multipart） -->

    <!-- 文本输入 -->
    <label for="username">用户名：</label>
    <input type="text" id="username" name="username" required minlength="3" maxlength="20" placeholder="请输入用户名">

    <!-- 密码 -->
    <input type="password" id="password" name="password" required>

    <!-- 邮箱（HTML5 新类型，自带验证） -->
    <input type="email" id="email" name="email" required>

    <!-- 手机号 -->
    <input type="tel" id="phone" name="phone" pattern="[0-9]{11}">

    <!-- URL -->
    <input type="url" id="website" name="website">

    <!-- 数字 -->
    <input type="number" id="age" name="age" min="1" max="120" step="1">

    <!-- 范围滑块 -->
    <input type="range" id="volume" name="volume" min="0" max="100" value="50">

    <!-- 日期 -->
    <input type="date" id="birthday" name="birthday">
    <input type="time" id="time" name="time">
    <input type="datetime-local" id="datetime" name="datetime">
    <input type="month" id="month" name="month">
    <input type="week" id="week" name="week">

    <!-- 颜色选择器 -->
    <input type="color" id="color" name="color" value="#ff0000">

    <!-- 搜索 -->
    <input type="search" id="search" name="search" placeholder="搜索...">

    <!-- 多行文本 -->
    <textarea id="message" name="message" rows="4" cols="50" placeholder="请输入留言"></textarea>

    <!-- 下拉选择 -->
    <select id="country" name="country">
        <option value="">请选择国家</option>
        <option value="cn">中国</option>
        <option value="us">美国</option>
        <optgroup label="欧洲">
            <option value="uk">英国</option>
            <option value="fr">法国</option>
        </optgroup>
    </select>

    <!-- 单选框 -->
    <input type="radio" id="male" name="gender" value="male" checked>
    <label for="male">男</label>
    <input type="radio" id="female" name="gender" value="female">
    <label for="female">女</label>

    <!-- 复选框 -->
    <input type="checkbox" id="agree" name="agree" required>
    <label for="agree">我同意用户协议</label>

    <!-- 文件上传 -->
    <input type="file" id="avatar" name="avatar" accept="image/*" multiple>

    <!-- 隐藏字段 -->
    <input type="hidden" name="token" value="abc123">

    <!-- 按钮 -->
    <button type="submit">提交</button>
    <button type="reset">重置</button>
    <button type="button" onclick="alert('点击了')">普通按钮</button>
    <input type="submit" value="提交（旧方式）">

    <!-- 数据列表（输入建议） -->
    <input list="browsers" name="browser">
    <datalist id="browsers">
        <option value="Chrome">
        <option value="Firefox">
        <option value="Safari">
    </datalist>

    <!-- 输出（计算结果显示） -->
    <form oninput="result.value=parseInt(a.value)+parseInt(b.value)">
        <input type="number" id="a" value="10"> +
        <input type="number" id="b" value="20"> =
        <output name="result" for="a b">30</output>
    </form>
</form>

<!-- HTML5 表单验证属性 -->
<!-- required：必填 -->
<!-- minlength / maxlength：最小/最大长度 -->
<!-- min / max：最小/最大值（数字/日期） -->
<!-- pattern：正则表达式验证 -->
<!-- type="email/url/tel"：自带格式验证 -->
<!-- novalidate：禁用验证（form 属性） -->
<!-- formnovalidate：禁用验证（按钮属性） -->
```

### 4. 多媒体标签

```html
<!-- 音频 -->
<audio controls autoplay loop muted preload="auto">
    <source src="audio.mp3" type="audio/mpeg">
    <source src="audio.ogg" type="audio/ogg">
    您的浏览器不支持音频播放。
</audio>
<!-- controls：显示控制条；autoplay：自动播放（多数浏览器需 muted）；loop：循环；muted：静音；preload：预加载策略 -->

<!-- 视频 -->
<video width="640" height="360" controls poster="cover.jpg" preload="metadata">
    <source src="video.mp4" type="video/mp4">
    <source src="video.webm" type="video/webm">
    <track kind="subtitles" src="subtitles.vtt" srclang="zh" label="中文">
    您的浏览器不支持视频播放。
</video>
<!-- poster：封面图；track：字幕轨道 -->

<!-- 内嵌网页（iframe） -->
<iframe src="https://example.com" width="800" height="600" frameborder="0" allowfullscreen sandbox></iframe>
<!-- sandbox：安全限制；allowfullscreen：允许全屏 -->

<!-- Canvas（2D 绘图，需 JS） -->
<canvas id="myCanvas" width="400" height="200">
    您的浏览器不支持 Canvas。
</canvas>
<script>
    const canvas = document.getElementById('myCanvas');
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#FF0000';
    ctx.fillRect(10, 10, 100, 50);
</script>

<!-- SVG（矢量图） -->
<svg width="100" height="100" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="40" fill="green" stroke="black" stroke-width="2"/>
    <text x="50" y="55" text-anchor="middle" fill="white">SVG</text>
</svg>
```

### 5. 表格标签

```html
<table>
    <caption>学生成绩表</caption>  <!-- 表格标题 -->
    <thead>  <!-- 表头 -->
        <tr>
            <th>姓名</th>
            <th>数学</th>
            <th>英语</th>
        </tr>
    </thead>
    <tbody>  <!-- 表体 -->
        <tr>
            <td>张三</td>
            <td>90</td>
            <td>85</td>
        </tr>
        <tr>
            <td>李四</td>
            <td colspan="2">95</td>  <!-- 跨列 -->
        </tr>
    </tbody>
    <tfoot>  <!-- 表尾 -->
        <tr>
            <td>平均</td>
            <td>92.5</td>
            <td>85</td>
        </tr>
    </tfoot>
</table>
<!-- 注意：表格应用于展示数据，不用于布局（布局用 CSS Flexbox/Grid） -->
```

---

## 三、CSS 概述

### 1. CSS 是什么

```text
CSS（Cascading Style Sheets，层叠样式表）：
- 控制网页的外观和样式
- 由 Håkon Wium Lie 于 1994 年提出
- 与 HTML 分离：HTML 负责结构，CSS 负责表现
- "层叠"：多个样式规则可以叠加，有优先级机制

CSS 历史：
- CSS 1（1996）：基础样式
- CSS 2（1998）：定位、媒体类型
- CSS 2.1（2011）：修订完善
- CSS 3（2001+）：模块化，持续更新
  - Selectors Level 3/4
  - Flexbox（2017 标准）
  - Grid（2017 标准）
  - Transitions / Animations
  - Transforms
  - Gradients
  - Media Queries
  - Custom Properties（CSS 变量）
  - Container Queries（2023）
  - :has() 选择器（2023）
```

### 2. CSS 引入方式

```html
<!-- 方式1：外部样式表（推荐，结构与样式分离） -->
<head>
    <link rel="stylesheet" href="style.css">
</head>

<!-- 方式2：内部样式表（单页面特殊样式） -->
<head>
    <style>
        body { font-family: sans-serif; }
    </style>
</head>

<!-- 方式3：内联样式（不推荐，仅特殊情况） -->
<p style="color: red; font-size: 16px;">红色文字</p>

<!-- 方式4：@import（不推荐，性能差） -->
<style>
    @import url("other.css");
</style>
```

### 3. CSS 基本语法

```css
/* 注释 */

/* 选择器 { 属性: 值; } */
h1 {
    color: #333;
    font-size: 24px;
    margin: 0;
}

/* 多个选择器共享样式 */
h1, h2, h3 {
    font-weight: bold;
}

/* 后代选择器 */
nav ul li {
    list-style: none;
}

/* 伪类 */
a:hover {
    color: blue;
}

/* 伪元素 */
p::first-line {
    font-weight: bold;
}
```

---

## 四、CSS 选择器

### 1. 基础选择器

```css
/* 元素选择器（标签选择器） */
p { color: black; }

/* ID 选择器（唯一，不推荐用于样式，优先用于 JS） */
#header { background: white; }

/* 类选择器（最常用） */
.button { padding: 8px 16px; }

/* 通配符选择器（选择所有元素，谨慎使用） */
* { box-sizing: border-box; }

/* 属性选择器 */
input[type="text"] { border: 1px solid #ccc; }
a[href^="https"] { color: green; }  /* 以 https 开头 */
a[href$=".pdf"] { color: red; }     /* 以 .pdf 结尾 */
a[href*="example"] { color: blue; } /* 包含 example */
```

### 2. 组合选择器

```css
/* 后代选择器（所有后代） */
nav a { color: blue; }

/* 子选择器（直接子元素） */
nav > ul { margin: 0; }

/* 相邻兄弟选择器（紧跟在后面的第一个兄弟） */
h1 + p { margin-top: 0; }

/* 通用兄弟选择器（后面的所有兄弟） */
h1 ~ p { color: gray; }

/* 分组选择器（多个选择器共享样式） */
h1, h2, h3 { font-family: serif; }
```

### 3. 伪类选择器

```css
/* 链接伪类（注意顺序：LVHA） */
a:link { color: blue; }       /* 未访问 */
a:visited { color: purple; }   /* 已访问 */
a:hover { color: red; }        /* 鼠标悬停 */
a:active { color: orange; }     /* 点击时 */

/* 表单伪类 */
input:focus { outline: 2px solid blue; }  /* 获得焦点 */
input:disabled { opacity: 0.5; }           /* 禁用 */
input:checked { accent-color: green; }     /* 选中 */
input:required { border-color: red; }      /* 必填 */
input:valid { border-color: green; }       /* 验证通过 */
input:invalid { border-color: red; }       /* 验证失败 */

/* 结构伪类 */
li:first-child { font-weight: bold; }    /* 第一个子元素 */
li:last-child { border-bottom: none; }    /* 最后一个子元素 */
li:nth-child(odd) { background: #f0f0f0; }  /* 奇数 */
li:nth-child(even) { background: #fff; }     /* 偶数 */
li:nth-child(3n) { color: red; }              /* 第 3、6、9... 个 */
li:nth-child(2) { font-size: 18px; }          /* 第 2 个 */
p:first-of-type { color: blue; }            /* 第一个该类型 */
p:last-of-type { color: blue; }             /* 最后一个该类型 */
p:only-child { color: red; }                /* 唯一子元素 */
p:empty { display: none; }                  /* 空元素 */

/* 其他伪类 */
:not(.special) { color: gray; }     /* 排除选择器 */
:root { --primary: blue; }           /* 根元素（html） */
:target { background: yellow; }      /* 锚点目标 */
:enabled { background: white; }      /* 启用状态 */
```

### 4. 伪元素选择器

```css
/* 首字母 */
p::first-letter {
    font-size: 2em;
    float: left;
    margin-right: 4px;
}

/* 首行 */
p::first-line {
    font-weight: bold;
}

/* 元素前插入内容 */
li::before {
    content: "✓ ";
    color: green;
}

/* 元素后插入内容 */
a::after {
    content: " ↗";
    font-size: 0.8em;
}

/* 选中的文本 */
::selection {
    background: #b3d4fc;
    color: #000;
}

/* 占位符文本 */
input::placeholder {
    color: #999;
    font-style: italic;
}

/* 滚动条（Webkit） */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-thumb { background: #888; border-radius: 4px; }
```

### 5. :has() 父选择器（CSS4 新特性）

```css
/* :has() 父选择器（2023 年主流浏览器支持） */

/* 包含 img 的 a 标签 */
a:has(img) {
    border: 2px solid blue;
}

/* 包含 checked 子元素的 label */
label:has(input:checked) {
    font-weight: bold;
    color: green;
}

/* 不包含 p 的 div */
div:not(:has(p)) {
    padding: 0;
}

/* 表单验证：包含无效输入的表单显示警告 */
form:has(input:invalid) {
    border: 2px solid red;
}
```

### 6. 选择器优先级

```css
CSS 优先级（从高到低）：

1. !important（最高，尽量避免使用）
   color: red !important;

2. 内联样式（style 属性）
   <p style="color: red;">

3. ID 选择器
   #header { }

4. 类选择器 / 属性选择器 / 伪类
   .button { }  [type="text"] { }  :hover { }

5. 元素选择器 / 伪元素
   p { }  ::before { }

6. 通配符 / 继承
   * { }

优先级计算（特异性 Specificity）：
- (0, 0, 0, 0) = (内联, ID, 类/属性/伪类, 元素/伪元素)
- #nav .item a:hover = (0, 1, 2, 1)

相同优先级时：
- 后面的规则覆盖前面的（层叠）
- 外部样式表和内部样式表按出现顺序

最佳实践：
- 优先用类选择器，少用 ID
- 避免 !important
- 选择器不要嵌套太深（不超过 3-4 层）
- 用 BEM 等命名规范减少冲突
```

---

## 五、CSS 常用属性

### 1. 文本与字体

```css
.text-demo {
    /* 字体族 */
    font-family: "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif;
    /* 多个字体，浏览器依次尝试，最后是通用族（serif/sans-serif/monospace/cursive/fantasy） */

    /* 字体大小 */
    font-size: 16px;          /* 像素 */
    font-size: 1em;           /* 相对父元素 */
    font-size: 1rem;          /* 相对根元素（推荐） */
    font-size: 100%;          /* 百分比 */
    font-size: larger;        /* 相对更大 */

    /* 字重 */
    font-weight: normal;      /* 400 */
    font-weight: bold;        /* 700 */
    font-weight: 100-900;    /* 100-900 */

    /* 字体样式 */
    font-style: normal;       /* 正常 */
    font-style: italic;       /* 斜体 */
    font-style: oblique;      /* 倾斜 */

    /* 行高 */
    line-height: 1.5;         /* 无单位，推荐 */
    line-height: 24px;        /* 像素 */
    line-height: 150%;        /* 百分比 */

    /* 文本颜色 */
    color: #333;              /* 十六进制 */
    color: rgb(51, 51, 51);   /* RGB */
    color: rgba(51, 51, 51, 0.8);  /* RGBA（带透明度） */
    color: hsl(0, 0%, 20%);   /* HSL */
    color: blue;              /* 颜色名 */

    /* 文本对齐 */
    text-align: left;         /* 左对齐 */
    text-align: center;       /* 居中 */
    text-align: right;        /* 右对齐 */
    text-align: justify;      /* 两端对齐 */

    /* 文本装饰 */
    text-decoration: none;           /* 无装饰 */
    text-decoration: underline;      /* 下划线 */
    text-decoration: line-through;   /* 删除线 */
    text-decoration: overline;       /* 上划线 */
    text-decoration-color: red;      /* 装饰线颜色 */
    text-decoration-style: wavy;     /* 装饰线样式 */

    /* 文本转换 */
    text-transform: uppercase;   /* 大写 */
    text-transform: lowercase;   /* 小写 */
    text-transform: capitalize;  /* 首字母大写 */
    text-transform: none;        /* 不变 */

    /* 字符间距 */
    letter-spacing: 2px;     /* 字符间距 */
    word-spacing: 4px;       /* 单词间距 */

    /* 文本缩进 */
    text-indent: 2em;        /* 首行缩进 */

    /* 垂直对齐 */
    vertical-align: middle;   /* 垂直居中（用于行内元素/表格） */

    /* 文本阴影 */
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    /* 水平偏移 垂直偏移 模糊半径 颜色 */

    /* 空白处理 */
    white-space: normal;      /* 正常换行 */
    white-space: nowrap;      /* 不换行 */
    white-space: pre;         /* 保留空白和换行 */
    white-space: pre-wrap;    /* 保留空白，允许换行 */
    white-space: pre-line;    /* 合并空白，保留换行 */

    /* 文本溢出 */
    overflow: hidden;
    text-overflow: ellipsis;  /* 省略号（需配合 overflow:hidden 和 white-space:nowrap） */

    /* 多行省略（Webkit） */
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;

    /* 字体平滑 */
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
```

### 2. 盒模型

```css
.box-demo {
    /* 内容区 */
    width: 300px;
    height: 200px;
    min-width: 200px;
    max-width: 500px;
    min-height: 100px;
    max-height: 400px;

    /* 内边距 */
    padding: 20px;                    /* 四边相同 */
    padding: 10px 20px;               /* 上下 左右 */
    padding: 10px 20px 30px;          /* 上 左右 下 */
    padding: 10px 20px 30px 40px;     /* 上 右 下 左（顺时针） */
    padding-top: 10px;
    padding-right: 20px;
    padding-bottom: 30px;
    padding-left: 40px;

    /* 边框 */
    border: 2px solid #333;           /* 宽度 样式 颜色 */
    border-width: 2px;
    border-style: solid;               /* solid/dashed/dotted/double/none */
    border-color: #333;
    border-top: 1px solid red;
    border-radius: 8px;                /* 圆角 */
    border-radius: 8px 16px;           /* 左上右下 右上左下 */
    border-radius: 50%;                 /* 圆形 */

    /* 外边距 */
    margin: 20px;
    margin: 0 auto;                     /* 水平居中（需有宽度） */
    margin-top: 10px;
    margin-bottom: 20px;

    /* 盒模型类型（重要！） */
    box-sizing: content-box;   /* 默认：width = 内容宽度，总宽 = width + padding + border */
    box-sizing: border-box;    /* 推荐：width = 内容 + padding + border，总宽 = width */
}

/* 全局设置 border-box（推荐） */
*, *::before, *::after {
    box-sizing: border-box;
}

/* 外边距折叠（Margin Collapse）：
   - 相邻块级元素的上下外边距会折叠，取较大值
   - 父元素与第一个/最后一个子元素的外边距会折叠
   - 解决：用 padding 替代 margin、overflow:hidden、border、flex/grid 容器
*/
```

### 3. 背景

```css
.bg-demo {
    /* 背景颜色 */
    background-color: #f5f5f5;

    /* 背景图片 */
    background-image: url("image.jpg");
    background-image: linear-gradient(to right, red, blue);  /* 渐变 */

    /* 背景重复 */
    background-repeat: no-repeat;    /* 不重复 */
    background-repeat: repeat-x;      /* 水平重复 */
    background-repeat: repeat-y;      /* 垂直重复 */
    background-repeat: repeat;        /* 重复（默认） */

    /* 背景位置 */
    background-position: center;      /* 居中 */
    background-position: top right;   /* 右上 */
    background-position: 50% 50%;     /* 百分比 */
    background-position: 100px 50px;  /* 像素 */

    /* 背景大小 */
    background-size: cover;            /* 覆盖（可能裁剪） */
    background-size: contain;          /* 包含（可能留白） */
    background-size: 100% 100%;       /* 拉伸 */
    background-size: 300px 200px;     /* 固定大小 */

    /* 背景固定 */
    background-attachment: scroll;     /* 随页面滚动（默认） */
    background-attachment: fixed;      /* 固定（视差效果） */
    background-attachment: local;      /* 随内容滚动 */

    /* 简写 */
    background: #f5f5f5 url("image.jpg") no-repeat center / cover;
    /* 颜色 图片 重复 位置 / 大小 */

    /* 多背景 */
    background:
        linear-gradient(to bottom, rgba(0,0,0,0.5), rgba(0,0,0,0.8)),
        url("image.jpg") center / cover;
}

/* 渐变 */
.gradient-demo {
    /* 线性渐变 */
    background: linear-gradient(to right, red, yellow, green);
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    background: linear-gradient(to bottom, transparent, rgba(0,0,0,0.5));

    /* 径向渐变 */
    background: radial-gradient(circle at center, red, blue);
    background: radial-gradient(ellipse at top, #ff9a9e, #fecfef);

    /* 圆锥渐变 */
    background: conic-gradient(from 0deg, red, yellow, green, blue, red);

    /* 重复渐变 */
    background: repeating-linear-gradient(45deg, #f0f0f0, #f0f0f0 10px, #fff 10px, #fff 20px);
    background: repeating-radial-gradient(circle, #f0f0f0, #f0f0f0 10px, #fff 10px, #fff 20px);
}
```

### 4. 边框与阴影

```css
.border-demo {
    /* 边框 */
    border: 2px solid #333;
    border-top: 1px dashed #999;
    border-bottom: 3px double #666;

    /* 圆角 */
    border-radius: 8px;
    border-radius: 8px 16px 24px 32px;  /* 四个角 */
    border-radius: 50%;                     /* 圆形 */

    /* 椭圆圆角（水平半径 / 垂直半径） */
    border-radius: 50px / 25px;

    /* 外阴影 */
    box-shadow: 5px 5px 10px rgba(0,0,0,0.3);
    /* 水平偏移 垂直偏移 模糊半径 扩展半径 颜色 */
    box-shadow: 5px 5px 10px 2px rgba(0,0,0,0.3);
    box-shadow: inset 2px 2px 5px rgba(0,0,0,0.3);  /* 内阴影 */

    /* 多层阴影 */
    box-shadow:
        0 2px 4px rgba(0,0,0,0.1),
        0 4px 8px rgba(0,0,0,0.1),
        0 8px 16px rgba(0,0,0,0.1);

    /* 轮廓（不占空间，聚焦时常用） */
    outline: 2px solid blue;
    outline-offset: 2px;

    /* 描边（仅 SVG） */
    /* stroke: red; stroke-width: 2; */
}
```

### 5. 列表与表格

```css
/* 列表 */
ul {
    list-style-type: disc;       /* 实心圆（默认） */
    list-style-type: circle;      /* 空心圆 */
    list-style-type: square;      /* 方块 */
    list-style-type: none;        /* 无标记 */
    list-style-image: url("icon.png");  /* 自定义图片 */
    list-style-position: inside;   /* 标记在内容内 */
    list-style-position: outside;  /* 标记在内容外（默认） */
}

ol {
    list-style-type: decimal;          /* 1, 2, 3 */
    list-style-type: lower-alpha;      /* a, b, c */
    list-style-type: upper-alpha;      /* A, B, C */
    list-style-type: lower-roman;      /* i, ii, iii */
    list-style-type: upper-roman;      /* I, II, III */
    list-style-type: cjk-ideographic;  /* 一, 二, 三 */
}

/* 表格 */
table {
    border-collapse: collapse;   /* 合并边框 */
    border-spacing: 0;           /* 边框间距 */
    width: 100%;
    caption-side: top;           /* 标题位置 */
    empty-cells: show;           /* 空单元格显示边框 */
    table-layout: fixed;         /* 固定布局（列宽由设置决定，不随内容变化） */
    table-layout: auto;          /* 自动布局（默认，列宽由内容决定） */
}

th, td {
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: left;
    vertical-align: middle;
}

th {
    background: #f5f5f5;
    font-weight: bold;
}

tr:nth-child(even) {
    background: #fafafa;   /* 斑马纹 */
}

tr:hover {
    background: #e3f2fd;   /* 悬停高亮 */
}
```

---

## 六、CSS3 布局

### 1. Flexbox（弹性盒子）

```css
/* Flexbox 容器 */
.flex-container {
    display: flex;           /* 启用 Flexbox */
    display: inline-flex;    /* 行内 Flex */

    /* 主轴方向 */
    flex-direction: row;            /* 水平（默认） */
    flex-direction: row-reverse;    /* 水平反向 */
    flex-direction: column;         /* 垂直 */
    flex-direction: column-reverse; /* 垂直反向 */

    /* 换行 */
    flex-wrap: nowrap;       /* 不换行（默认） */
    flex-wrap: wrap;         /* 换行 */
    flex-wrap: wrap-reverse; /* 反向换行 */

    /* 简写：方向 + 换行 */
    flex-flow: row wrap;

    /* 主轴对齐 */
    justify-content: flex-start;    /* 起点对齐（默认） */
    justify-content: flex-end;      /* 终点对齐 */
    justify-content: center;        /* 居中 */
    justify-content: space-between; /* 两端对齐，首尾贴边 */
    justify-content: space-around;  /* 均匀分布，首尾半间距 */
    justify-content: space-evenly;  /* 均匀分布，首尾等间距 */

    /* 交叉轴对齐（单行） */
    align-items: stretch;       /* 拉伸（默认） */
    align-items: flex-start;    /* 起点对齐 */
    align-items: flex-end;      /* 终点对齐 */
    align-items: center;        /* 居中 */
    align-items: baseline;      /* 基线对齐 */

    /* 交叉轴对齐（多行） */
    align-content: stretch;        /* 拉伸（默认） */
    align-content: flex-start;     /* 起点对齐 */
    align-content: flex-end;       /* 终点对齐 */
    align-content: center;         /* 居中 */
    align-content: space-between;  /* 两端对齐 */
    align-content: space-around;   /* 均匀分布 */

    /* 间距（新属性，推荐） */
    gap: 16px;              /* 行列间距相同 */
    row-gap: 16px;          /* 行间距 */
    column-gap: 16px;       /* 列间距 */
}

/* Flex 子项 */
.flex-item {
    /* 增长比例（剩余空间分配） */
    flex-grow: 0;    /* 不增长（默认） */
    flex-grow: 1;    /* 等比例增长 */
    flex-grow: 2;    /* 2倍增长 */

    /* 收缩比例（空间不足时收缩） */
    flex-shrink: 1;   /* 可收缩（默认） */
    flex-shrink: 0;   /* 不收缩 */

    /* 基础大小 */
    flex-basis: auto;    /* 自动（默认） */
    flex-basis: 200px;   /* 固定大小 */
    flex-basis: 50%;      /* 百分比 */

    /* 简写：grow shrink basis */
    flex: 0 1 auto;    /* 默认 */
    flex: 1;            /* 1 1 0%（等比例填充） */
    flex: none;         /* 0 0 auto（不增长不收缩） */
    flex: auto;         /* 1 1 auto */

    /* 单独对齐（覆盖容器的 align-items） */
    align-self: auto;          /* 继承容器 */
    align-self: flex-start;
    align-self: center;
    align-self: stretch;

    /* 顺序（默认 0，数值越小越靠前） */
    order: 0;     /* 默认 */
    order: -1;    /* 提前 */
    order: 1;     /* 靠后 */
}

/* 经典布局示例 */

/* 水平垂直居中 */
.center-box {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}

/* 导航栏 */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
}

/* 圣杯布局（三栏） */
.holy-grail {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}
.holy-grail .body {
    display: flex;
    flex: 1;
}
.holy-grail .main { flex: 1; order: 2; }
.holy-grail .nav { width: 200px; order: 1; }
.holy-grail .aside { width: 200px; order: 3; }

/* 卡片网格 */
.card-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
}
.card {
    flex: 1 1 300px;  /* 最小 300px，自动填充 */
}
```

### 2. Grid（网格布局）

```css
/* Grid 容器 */
.grid-container {
    display: grid;            /* 启用 Grid */
    display: inline-grid;     /* 行内 Grid */

    /* 列定义 */
    grid-template-columns: 200px 200px 200px;  /* 三列固定宽度 */
    grid-template-columns: 1fr 2fr 1fr;          /* 三列比例 */
    grid-template-columns: repeat(3, 1fr);        /* 三列等宽 */
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));  /* 响应式 */
    grid-template-columns: 200px repeat(3, 1fr);  /* 第一列固定，其余三等分 */

    /* 行定义 */
    grid-template-rows: auto 1fr auto;  /* 三行 */
    grid-template-rows: repeat(3, 100px);  /* 三行等高 */

    /* 简写：行 / 列 */
    grid-template: repeat(3, 100px) / repeat(3, 1fr);

    /* 间距 */
    gap: 20px;              /* 行列间距 */
    row-gap: 20px;          /* 行间距 */
    column-gap: 20px;       /* 列间距 */

    /* 网格区域命名 */
    grid-template-areas:
        "header header header"
        "nav main aside"
        "footer footer footer";

    /* 对齐 */
    justify-items: stretch;    /* 单元格内容水平对齐（默认 stretch） */
    justify-items: start;
    justify-items: center;
    justify-items: end;

    align-items: stretch;      /* 单元格内容垂直对齐 */
    align-items: center;

    place-items: center stretch;  /* 简写：align justify */

    /* 整个网格对齐（容器有剩余空间时） */
    justify-content: start;    /* 网格水平对齐 */
    justify-content: center;
    justify-content: space-between;
    align-content: start;      /* 网格垂直对齐 */
    place-content: center;     /* 简写 */

    /* 自动行/列大小（隐式网格） */
    grid-auto-rows: 100px;     /* 自动行高 */
    grid-auto-columns: 100px;  /* 自动列宽 */
    grid-auto-flow: row;        /* 自动排列方向 */
    grid-auto-flow: column;
    grid-auto-flow: dense;      /* 紧密排列（填补空隙） */
}

/* Grid 子项 */
.grid-item {
    /* 列位置 */
    grid-column-start: 1;
    grid-column-end: 3;
    grid-column: 1 / 3;          /* 简写：起始 / 结束 */
    grid-column: 1 / span 2;     /* 从第1列开始，跨2列 */
    grid-column: span 2;          /* 跨2列（自动位置） */

    /* 行位置 */
    grid-row-start: 1;
    grid-row-end: 3;
    grid-row: 1 / 3;
    grid-row: 1 / span 2;

    /* 简写：行 / 列 */
    grid-area: 1 / 1 / 3 / 3;  /* 行起始 / 列起始 / 行结束 / 列结束 */

    /* 命名区域 */
    grid-area: header;  /* 对应 grid-template-areas 中的命名 */

    /* 单独对齐 */
    justify-self: center;   /* 水平对齐 */
    align-self: center;     /* 垂直对齐 */
    place-self: center;     /* 简写 */

    /* 层级（重叠时） */
    z-index: 10;
}

/* 经典布局示例 */

/* 圣杯布局（Grid 版，更简洁） */
.holy-grail-grid {
    display: grid;
    grid-template-areas:
        "header header header"
        "nav main aside"
        "footer footer footer";
    grid-template-columns: 200px 1fr 200px;
    grid-template-rows: auto 1fr auto;
    min-height: 100vh;
    gap: 10px;
}
.header { grid-area: header; }
.nav { grid-area: nav; }
.main { grid-area: main; }
.aside { grid-area: aside; }
.footer { grid-area: footer; }

/* 响应式卡片网格 */
.responsive-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}
/* auto-fit：自动填充，空列收缩 */
/* auto-fill：自动填充，保留空列 */
/* minmax(250px, 1fr)：最小 250px，最大等分 */
```

### 3. 定位（Position）

```css
.position-demo {
    /* 定位类型 */
    position: static;       /* 静态（默认，正常文档流） */
    position: relative;     /* 相对定位（相对于自身原位置） */
    position: absolute;     /* 绝对定位（相对于最近的非 static 祖先） */
    position: fixed;        /* 固定定位（相对于视口，不随滚动） */
    position: sticky;       /* 粘性定位（滚动到阈值时固定） */

    /* 偏移量（定位元素才生效） */
    top: 20px;
    right: 20px;
    bottom: 20px;
    left: 20px;

    /* 层级 */
    z-index: 10;     /* 数值越大越靠前（仅定位元素生效） */
    z-index: auto;   /* 自动（0） */
}

/* 经典用法 */

/* 子元素绝对定位，父元素相对定位 */
.parent {
    position: relative;
}
.child {
    position: absolute;
    top: 0;
    right: 0;
}

/* 固定导航栏 */
.fixed-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
}

/* 粘性侧边栏 */
.sticky-sidebar {
    position: sticky;
    top: 20px;  /* 滚动到距顶部 20px 时固定 */
}

/* 全屏遮罩 */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    z-index: 9999;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* 元素居中（绝对定位 + transform） */
.center-absolute {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}
```

### 4. 显示与可见性

```css
.display-demo {
    /* 显示类型 */
    display: block;          /* 块级元素（独占一行，可设宽高） */
    display: inline;         /* 行内元素（不独占一行，不可设宽高） */
    display: inline-block;   /* 行内块（不独占一行，可设宽高） */
    display: none;           /* 隐藏（不占空间） */
    display: flex;           /* 弹性盒子 */
    display: grid;           /* 网格 */
    display: table;          /* 表格 */
    display: list-item;      /* 列表项 */

    /* 可见性 */
    visibility: visible;     /* 可见（默认） */
    visibility: hidden;      /* 隐藏（仍占空间） */
    visibility: collapse;    /* 折叠（表格行列） */

    /* 透明度 */
    opacity: 1;              /* 完全不透明（默认） */
    opacity: 0.5;            /* 半透明 */
    opacity: 0;              /* 完全透明（仍占空间，可点击） */

    /* display:none vs visibility:hidden vs opacity:0
       - display:none：不占空间，不可点击，子元素不可恢复
       - visibility:hidden：占空间，不可点击，子元素可设 visible 恢复
       - opacity:0：占空间，可点击，子元素受影响
    */
}
```

---

## 七、CSS3 动画与变换

### 1. 过渡（Transition）

```css
.transition-demo {
    /* 过渡属性 */
    transition-property: all;            /* 过渡的属性（all/具体属性名） */
    transition-property: width, height;   /* 多个属性 */

    /* 过渡时长 */
    transition-duration: 0.3s;            /* 秒 */
    transition-duration: 300ms;            /* 毫秒 */

    /* 过渡速度曲线 */
    transition-timing-function: ease;           /* 慢-快-慢（默认） */
    transition-timing-function: linear;         /* 匀速 */
    transition-timing-function: ease-in;        /* 慢入 */
    transition-timing-function: ease-out;       /* 慢出 */
    transition-timing-function: ease-in-out;    /* 慢入慢出 */
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);  /* 自定义贝塞尔曲线 */
    transition-timing-function: steps(4, end);  /* 阶梯函数 */

    /* 过渡延迟 */
    transition-delay: 0s;               /* 延迟开始 */
    transition-delay: 100ms;

    /* 简写：property duration timing-function delay */
    transition: all 0.3s ease;
    transition: width 0.3s ease, height 0.5s ease-in-out 100ms;
}

/* 示例：悬停过渡 */
.button {
    background: #3498db;
    color: white;
    padding: 10px 20px;
    transition: all 0.3s ease;
}
.button:hover {
    background: #2980b9;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
.button:active {
    transform: translateY(0);
}

/* 可过渡的属性：颜色、长度、百分比、数值、transform、opacity 等
   不可过渡：display、visibility（可配合 opacity）、background-image
*/
```

### 2. 变换（Transform）

```css
.transform-demo {
    /* 2D 变换 */
    transform: translate(50px, 100px);   /* 平移：X Y */
    transform: translateX(50px);           /* X 平移 */
    transform: translateY(100px);          /* Y 平移 */
    transform: rotate(45deg);              /* 旋转：角度 */
    transform: scale(1.5);                  /* 缩放：X Y 相同 */
    transform: scale(1.5, 0.8);            /* 缩放：X Y 不同 */
    transform: scaleX(1.5);                 /* X 缩放 */
    transform: scaleY(0.8);                 /* Y 缩放 */
    transform: skew(10deg, 5deg);          /* 倾斜：X Y */
    transform: skewX(10deg);                /* X 倾斜 */
    transform: skewY(5deg);                 /* Y 倾斜 */

    /* 矩阵变换（底层） */
    transform: matrix(1, 0, 0, 1, 50, 100);  /* a b c d e f */

    /* 多个变换组合（从右到左执行） */
    transform: translate(50px, 50px) rotate(45deg) scale(1.5);

    /* 变换原点（默认中心） */
    transform-origin: center;           /* 中心（默认） */
    transform-origin: top left;         /* 左上 */
    transform-origin: 50% 50%;          /* 百分比 */
    transform-origin: 100px 100px;      /* 像素 */

    /* 3D 变换 */
    transform: perspective(500px) rotateY(45deg);  /* 透视 + Y 轴旋转 */
    transform: rotateX(45deg);           /* X 轴旋转 */
    transform: rotateY(45deg);           /* Y 轴旋转 */
    transform: rotateZ(45deg);           /* Z 轴旋转（同 rotate） */
    transform: rotate3d(1, 1, 1, 45deg); /* 3D 旋转：x y z 角度 */
    transform: translateZ(100px);        /* Z 轴平移 */
    transform: translate3d(50px, 50px, 100px);  /* 3D 平移 */
    transform: scaleZ(2);                 /* Z 轴缩放 */
    transform: scale3d(1.5, 1.5, 2);     /* 3D 缩放 */

    /* 3D 相关属性 */
    perspective: 500px;                   /* 透视距离（父元素设置） */
    perspective-origin: center;           /* 透视原点 */
    transform-style: flat;                /* 2D（默认） */
    transform-style: preserve-3d;         /* 保留 3D */
    backface-visibility: visible;         /* 背面可见（默认） */
    backface-visibility: hidden;          /* 背面隐藏 */
}

/* 示例：卡片翻转 */
.card-container {
    perspective: 1000px;
}
.card {
    position: relative;
    width: 200px;
    height: 300px;
    transform-style: preserve-3d;
    transition: transform 0.6s;
}
.card:hover {
    transform: rotateY(180deg);
}
.card-face {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
}
.card-front { background: #3498db; }
.card-back {
    background: #e74c3c;
    transform: rotateY(180deg);
}
```

### 3. 动画（Animation）

```css
/* 定义关键帧 */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 百分比关键帧 */
@keyframes slideIn {
    0% { transform: translateX(-100%); opacity: 0; }
    60% { transform: translateX(10px); opacity: 1; }
    80% { transform: translateX(-5px); }
    100% { transform: translateX(0); }
}

/* 多属性动画 */
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

/* 使用动画 */
.animation-demo {
    /* 动画名称 */
    animation-name: fadeIn;

    /* 动画时长 */
    animation-duration: 1s;

    /* 速度曲线 */
    animation-timing-function: ease;
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    animation-timing-function: steps(10, end);

    /* 延迟 */
    animation-delay: 0s;
    animation-delay: 200ms;

    /* 播放次数 */
    animation-iteration-count: 1;          /* 一次（默认） */
    animation-iteration-count: infinite;    /* 无限 */
    animation-iteration-count: 3;            /* 3次 */

    /* 播放方向 */
    animation-direction: normal;            /* 正常（默认） */
    animation-direction: reverse;           /* 反向 */
    animation-direction: alternate;         /* 交替（正→反→正） */
    animation-direction: alternate-reverse; /* 交替反向 */

    /* 填充模式（动画前后的状态） */
    animation-fill-mode: none;              /* 无（默认） */
    animation-fill-mode: forwards;          /* 保持结束状态 */
    animation-fill-mode: backwards;         /* 应用开始状态（延迟期间） */
    animation-fill-mode: both;              /* 两者都应用 */

    /* 播放状态 */
    animation-play-state: running;          /* 运行（默认） */
    animation-play-state: paused;           /* 暂停 */

    /* 简写：name duration timing-function delay iteration-count direction fill-mode */
    animation: fadeIn 1s ease 200ms both;
    animation: pulse 2s ease-in-out infinite;
}

/* 示例：加载动画 */
.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* 示例：悬停暂停 */
.hover-pause:hover {
    animation-play-state: paused;
}

/* 动画性能优化：
   - 优先用 transform 和 opacity（GPU 加速，不触发重排重绘）
   - 避免用 width/height/top/left 做动画（触发重排）
   - will-change: transform; 提示浏览器优化
   - 动画元素用 position:fixed/absolute 减少影响范围
*/
```

---

## 八、响应式设计

### 1. 媒体查询（Media Queries）

```css
/* 基本语法 */
@media media-type and (media-feature) {
    /* 样式 */
}

/* 媒体类型 */
@media all { }          /* 所有设备（默认） */
@media screen { }       /* 屏幕 */
@media print { }        /* 打印 */
@media speech { }       /* 屏幕阅读器 */

/* 常用媒体特性 */
@media (min-width: 768px) { }       /* 最小宽度（≥768px） */
@media (max-width: 768px) { }       /* 最大宽度（≤768px） */
@media (min-width: 768px) and (max-width: 1024px) { }  /* 范围 */
@media (orientation: portrait) { }   /* 竖屏 */
@media (orientation: landscape) { }  /* 横屏 */
@media (prefers-color-scheme: dark) { }  /* 深色模式 */
@media (prefers-color-scheme: light) { } /* 浅色模式 */
@media (prefers-reduced-motion: reduce) { }  /* 减少动画 */
@media (hover: hover) { }             /* 支持悬停（PC） */
@media (pointer: coarse) { }          /* 粗指针（触屏） */
@media (resolution: 2dppx) { }       /* 分辨率（Retina） */

/* 移动端优先（Mobile First）：默认样式是移动端，大屏用 min-width 覆盖 */
.container {
    width: 100%;
    padding: 10px;
}
@media (min-width: 768px) {
    .container {
        width: 750px;
        margin: 0 auto;
        padding: 20px;
    }
}
@media (min-width: 1024px) {
    .container { width: 970px; }
}
@media (min-width: 1200px) {
    .container { width: 1170px; }
}

/* 常用断点 */
/* 手机：< 640px */
/* 平板：640px - 1024px */
/* 桌面：> 1024px */
/* 大屏：> 1440px */

/* 示例：响应式导航 */
.nav {
    display: flex;
    flex-direction: column;  /* 移动端垂直 */
}
@media (min-width: 768px) {
    .nav {
        flex-direction: row;  /* 桌面端水平 */
        justify-content: space-between;
    }
}

/* 示例：响应式网格 */
.grid {
    display: grid;
    grid-template-columns: 1fr;  /* 移动端单列 */
    gap: 16px;
}
@media (min-width: 640px) {
    .grid { grid-template-columns: repeat(2, 1fr); }  /* 平板两列 */
}
@media (min-width: 1024px) {
    .grid { grid-template-columns: repeat(3, 1fr); }  /* 桌面三列 */
}
@media (min-width: 1440px) {
    .grid { grid-template-columns: repeat(4, 1fr); }  /* 大屏四列 */
}

/* 打印样式 */
@media print {
    body { background: white; color: black; }
    .no-print { display: none; }
    a { text-decoration: underline; color: blue; }
    a[href]::after { content: " (" attr(href) ")"; }  /* 显示链接 URL */
}
```

### 2. 视口与弹性单位

```html
<!-- 视口设置（必须） -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- width=device-width：宽度等于设备宽度 -->
<!-- initial-scale=1.0：初始缩放 100% -->
<!-- maximum-scale=1.0：禁止用户缩放（不推荐，无障碍问题） -->
<!-- user-scalable=no：禁止缩放（不推荐） -->
```

```css
/* 弹性单位 */

/* rem：相对于根元素（html）的字体大小 */
html { font-size: 16px; }  /* 1rem = 16px */
h1 { font-size: 2rem; }     /* 32px */

/* 响应式 rem：根据屏幕宽度调整根字体大小 */
html { font-size: 14px; }
@media (min-width: 768px) {
    html { font-size: 16px; }
}
@media (min-width: 1024px) {
    html { font-size: 18px; }
}

/* em：相对于父元素的字体大小 */
.parent { font-size: 16px; }
.child { font-size: 1.5em; }  /* 24px（相对于 parent） */
/* 注意：em 会累积，嵌套时可能不是预期 */

/* vw / vh：视口宽高百分比 */
.full-screen {
    width: 100vw;   /* 视口宽度 100% */
    height: 100vh;  /* 视口高度 100% */
}
.responsive-text {
    font-size: 5vw;  /* 字体大小随视口宽度变化 */
}

/* vmin / vmax：视口较小/较大边的百分比 */
.square {
    width: 50vmin;   /* 视口较小边的 50% */
    height: 50vmin;
}

/* clamp()：限制范围（CSS 函数，推荐用于响应式字体） */
.fluid-text {
    font-size: clamp(14px, 2vw, 24px);
    /* 最小 14px，首选 2vw，最大 24px */
}

/* calc()：计算 */
.calc-demo {
    width: calc(100% - 40px);
    height: calc(100vh - 80px);
    font-size: calc(1rem + 2px);
}

/* 图片响应式 */
img {
    max-width: 100%;
    height: auto;  /* 保持比例 */
}

/* 背景图响应式 */
.hero {
    background: url("hero.jpg") center / cover;
    height: 50vh;  /* 视口高度的 50% */
}
```

### 3. 容器查询（Container Queries，CSS 新特性）

```css
/* 容器查询：根据父容器大小而非视口大小响应 */
/* 2023 年主流浏览器支持 */

/* 定义容器 */
.card-container {
    container-type: inline-size;  /* 内联尺寸（宽度） */
    container-name: card;          /* 容器名称（可选） */
}

/* 容器查询 */
@container card (min-width: 400px) {
    .card {
        display: flex;
        gap: 16px;
    }
    .card-image {
        width: 150px;
        flex-shrink: 0;
    }
}

@container (max-width: 399px) {
    .card {
        display: block;
    }
    .card-image {
        width: 100%;
        margin-bottom: 12px;
    }
}

/* 简写 */
.card-container {
    container: card / inline-size;  /* name / type */
}

/* 容器查询单位 */
/* cqw：容器宽度 1% */
/* cqh：容器高度 1% */
/* cqi：容器内联尺寸 1% */
/* cqb：容器块尺寸 1% */
/* cqmin：较小边 1% */
/* cqmax：较大边 1% */

.card-title {
    font-size: clamp(16px, 4cqi, 24px);  /* 基于容器宽度的响应式字体 */
}
```

---

## 九、CSS 变量与高级特性

### 1. CSS 自定义属性（变量）

```css
/* 定义变量（通常在 :root 全局定义） */
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --danger-color: #e74c3c;
    --text-color: #333;
    --bg-color: #fff;
    --font-family: "Helvetica Neue", Arial, sans-serif;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --radius: 8px;
    --shadow: 0 2px 8px rgba(0,0,0,0.1);
    --transition: all 0.3s ease;
}

/* 使用变量 */
.button {
    background: var(--primary-color);
    color: white;
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius);
    transition: var(--transition);
}

.button:hover {
    background: var(--secondary-color);
    box-shadow: var(--shadow);
}

/* 局部变量（覆盖全局） */
.dark-theme {
    --bg-color: #1a1a1a;
    --text-color: #fff;
    --primary-color: #5dade2;
}

/* 变量默认值 */
.element {
    color: var(--custom-color, #333);  /* 如果 --custom-color 未定义，用 #333 */
}

/* 变量嵌套 */
:root {
    --base-color: #3498db;
    --hover-color: color-mix(in srgb, var(--base-color) 80%, black);  /* 混合颜色 */
}

/* 主题切换示例 */
body {
    background: var(--bg-color);
    color: var(--text-color);
    transition: background 0.3s, color 0.3s;
}

/* 配合 JS 切换主题 */
/* document.documentElement.setAttribute('data-theme', 'dark'); */
[data-theme="dark"] {
    --bg-color: #1a1a1a;
    --text-color: #fff;
}

/* CSS 变量的优势：
   - 减少重复代码
   - 易于维护和修改
   - 支持动态修改（JS 或媒体查询）
   - 有作用域（局部覆盖全局）
   - 可用于计算（calc(var(--x) + 10px)）
*/
```

### 2. 颜色函数

```css
/* rgb / rgba */
.color-rgb {
    color: rgb(255, 0, 0);           /* 红 */
    color: rgba(255, 0, 0, 0.5);     /* 半透明红 */
    color: rgb(255 0 0 / 0.5);       /* 新语法（空格分隔，/ 透明度） */
}

/* hsl / hsla */
.color-hsl {
    color: hsl(0, 100%, 50%);         /* 红：色相0，饱和100%，亮度50% */
    color: hsla(0, 100%, 50%, 0.5);  /* 半透明 */
    color: hsl(0 100% 50% / 0.5);    /* 新语法 */
}

/* color-mix：颜色混合（CSS4 新特性，2023 支持） */
.color-mix {
    background: color-mix(in srgb, red 50%, blue 50%);  /* 红蓝各50% */
    background: color-mix(in srgb, #3498db 80%, white);  /* 80%蓝 + 白（变浅） */
    background: color-mix(in srgb, #3498db 80%, black);  /* 80%蓝 + 黑（变深） */
    background: color-mix(in oklch, red, blue);           /* oklch 色彩空间混合 */
}

/* color-contrast：对比度颜色（实验性） */
/* .contrast {
    color: color-contrast(black vs white, #fff);
} */

/* 相对颜色（CSS4 新特性） */
.relative-color {
    --base: #3498db;
    background: rgb(from var(--base) r g b / 50%);  /* 基于基础色，透明度50% */
    background: hsl(from var(--base) h s calc(l * 1.2));  /* 亮度增加20% */
}

/* 十六进制透明度 */
.hex-alpha {
    background: #ff000080;  /* #RRGGBBAA，最后两位是透明度（80=50%） */
    background: #f008;       /* #RGBA 简写 */
}
```

### 3. 逻辑属性（Logical Properties）

```css
/* 逻辑属性：根据书写方向（LTR/RTL）自动调整 */
/* 替代物理属性（top/right/bottom/left） */

.logical-demo {
    /*  margin/padding/border 逻辑属性 */
    margin-inline-start: 20px;   /* 行首（LTR=左，RTL=右） */
    margin-inline-end: 20px;     /* 行尾（LTR=右，RTL=左） */
    margin-block-start: 20px;    /* 块首（LTR=上） */
    margin-block-end: 20px;      /* 块尾（LTR=下） */

    padding-inline: 16px;         /* 行内方向（左右） */
    padding-block: 16px;          /* 块方向（上下） */

    border-inline: 1px solid #ccc;  /* 行内边框 */
    border-block-end: 2px solid #333;  /* 底部边框 */

    /* 尺寸逻辑属性 */
    inline-size: 300px;     /* 行内尺寸（LTR=宽度） */
    block-size: 200px;      /* 块尺寸（LTR=高度） */
    min-inline-size: 200px;
    max-block-size: 400px;

    /* 定位逻辑属性 */
    inset-inline-start: 0;   /* left/right */
    inset-block-start: 0;    /* top */
    inset: 0;                 /* top right bottom left */
    inset-inline: 0;          /* left right */
    inset-block: 0;           /* top bottom */

    /* 文本逻辑属性 */
    text-align: start;        /* 行首对齐（LTR=左，RTL=右） */
    text-align: end;          /* 行尾对齐 */
}

/* 书写方向 */
.rtl {
    direction: rtl;           /* 从右到左（阿拉伯语、希伯来语） */
    writing-mode: horizontal-tb;  /* 水平从上到下（默认） */
    writing-mode: vertical-rl;    /* 垂直从右到左（中文竖排） */
    writing-mode: vertical-lr;    /* 垂直从左到右 */
}
```

---

## 十、最佳实践

### 1. HTML 最佳实践

- [ ] **语义化标签**：用 <header>/<nav>/<main>/<article>/<section>/<footer>，少用 <div>
- [ ] **DOCTYPE 声明**：第一行必须是 <!DOCTYPE html>
- [ ] **字符编码**：<meta charset="UTF-8"> 放在 head 最前面
- [ ] **视口设置**：<meta name="viewport" ...> 响应式必备
- [ ] **alt 属性**：所有图片必须有 alt（无障碍+SEO）
- [ ] **label 关联**：表单控件用 <label for> 关联，提升可访问性
- [ ] **标题层级**：h1-h6 按顺序，不要跳级，一个页面一个 h1
- [ ] **表格用于数据**：不用表格做布局，布局用 CSS
- [ ] **内联样式最小化**：样式写在 CSS 文件，不用 style 属性
- [ ] **注释清晰**：复杂结构加注释，但不过度
- [ ] **代码缩进**：统一缩进（2 或 4 空格），保持可读性
- [ ] **属性顺序**：id → class → name → src/href → type → value → 其他
- [ ] **小写标签**：标签和属性用小写（HTML5 不强制，但约定俗成）
- [ ] **闭合标签**：所有标签正确闭合（自闭合标签如 <img />、<br />）
- [ ] **SEO 元数据**：title、description、Open Graph、Twitter Card
- [ ] **无障碍（a11y）**：ARIA 角色、键盘导航、颜色对比度
- [ ] **性能优化**：懒加载图片、预加载关键资源、最小化 DOM

### 2. CSS 最佳实践

- [ ] **外部样式表**：样式写在 .css 文件，结构与表现分离
- [ ] **CSS Reset/Normalize**：统一浏览器默认样式（Normalize.css 推荐）
- [ ] **box-sizing: border-box**：全局设置，盒模型更直观
- [ ] **类选择器优先**：少用 ID 和元素选择器，用类（可复用、优先级适中）
- [ ] **命名规范**：BEM / OOCSS / SMACSS / Atomic CSS，选一种坚持
- [ ] **避免 !important**：除非万不得已，用更高优先级替代
- [ ] **选择器简洁**：不要嵌套过深（不超过 3-4 层），减少特异性
- [ ] **CSS 变量**：颜色、间距、字体等用变量，易于维护和主题切换
- [ ] **Flexbox/Grid 布局**：不用 float 做布局，用 Flexbox/Grid
- [ ] **响应式设计**：移动端优先，媒体查询适配不同屏幕
- [ ] **硬件加速动画**：动画用 transform 和 opacity，避免 width/top 等
- [ ] **前缀处理**：用 Autoprefixer 自动加浏览器前缀，不手写
- [ ] **性能优化**：减少重排重绘、使用 contain、will-change 谨慎使用
- [ ] **字体优化**：font-display: swap、WOFF2 格式、预加载关键字体
- [ ] **图片优化**：max-width:100%、响应式图片（srcset）、WebP/AVIF
- [ ] **打印样式**：@media print 优化打印效果
- [ ] **深色模式**：prefers-color-scheme 支持深色模式
- [ ] **减少动画**：prefers-reduced-motion 为用户减少动画
- [ ] **代码组织**：按组件/功能分文件，用 @import 或构建工具合并
- [ ] **注释规范**：复杂样式、变量、hack 加注释
- [ ] **验证**：用 W3C CSS Validator 检查语法错误

### 3. BEM 命名规范（推荐）

```css
/* BEM：Block Element Modifier */
/* 块（Block）：独立的组件 */
.button { }

/* 元素（Element）：块的组成部分，用 __ 连接 */
.button__icon { }
.button__text { }

/* 修饰符（Modifier）：块或元素的变体，用 -- 连接 */
.button--primary { }       /* 主按钮 */
.button--large { }         /* 大按钮 */
.button--disabled { }      /* 禁用按钮 */
.button__icon--large { }   /* 大图标 */

/* 示例 */
<nav class="navbar">
    <div class="navbar__logo">Logo</div>
    <ul class="navbar__menu">
        <li class="navbar__item navbar__item--active">首页</li>
        <li class="navbar__item">关于</li>
    </ul>
    <button class="navbar__button navbar__button--primary">登录</button>
</nav>

/* BEM 的优势：
   - 扁平结构，优先级低，易覆盖
   - 语义清晰，一看就知道关系
   - 模块化，可复用
   - 避免命名冲突
*/
```

---

## 十一、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **HTML 中文乱码** | 未设置 charset/编码不匹配 | <meta charset="UTF-8">；文件保存为 UTF-8；服务器 Content-Type 设 UTF-8 |
| **CSS 样式不生效** | 选择器优先级低/路径错/缓存/语法错 | 检查选择器优先级；确认 CSS 路径；强制刷新(Ctrl+F5)；用开发者工具检查；验证 CSS 语法 |
| **margin 塌陷** | 相邻块级元素/父子元素外边距折叠 | 用 padding 替代；overflow:hidden；border 分隔；flex/grid 容器；display:flow-root |
| **inline-block 间隙** | HTML 换行/空格被渲染为空格 | 标签间不换行；font-size:0 父元素 + 子元素恢复；用 flex 替代 |
| **图片下方有空白** | img 是行内元素，基线对齐 | img { display: block; } 或 vertical-align: middle/top |
| **Flex 子项不收缩** | flex-shrink:0 或内容溢出 | 设置 flex-shrink:1；min-width:0；overflow:hidden |
| **Grid 内容溢出** | 单元格内容太长/未设 minmax | grid-template-columns: repeat(auto-fit, minmax(0, 1fr))；min-width:0 |
| **position:absolute 找不到定位父级** | 父元素都是 static | 给最近的祖先设 position:relative/absolute/fixed |
| **z-index 不生效** | 元素不是定位元素/层叠上下文问题 | 设 position:relative/absolute/fixed；检查父元素是否创建了层叠上下文 |
| **CSS 动画卡顿** | 用了触发重排的属性/太多元素同时动画 | 用 transform/opacity；will-change；减少同时动画的元素；GPU 加速 |
| **响应式在手机上不生效** | 未设 viewport meta | 加 <meta name="viewport" content="width=device-width, initial-scale=1.0"> |
| **媒体查询不生效** | 顺序错/优先级低/语法错 | 移动端优先用 min-width；媒体查询放后面；检查 and 和括号语法；用开发者工具模拟设备 |
| **字体不显示** | 字体路径错/CORS/格式不支持 | 检查 @font-face 路径；服务器设 CORS；用 WOFF2 格式；font-display:swap |
| **背景图不显示** | 路径错/元素无尺寸/被覆盖 | 检查 url 路径（相对 CSS 文件）；元素有宽高；检查 background-color 是否覆盖；用开发者工具 Network 检查 |
| **表格边框不合并** | 未设 border-collapse | table { border-collapse: collapse; } |
| **placeholder 样式不生效** | 选择器错/浏览器前缀 | ::placeholder { }；::-webkit-input-placeholder；:-ms-input-placeholder |
| **滚动条样式不生效** | 浏览器差异/属性错 | ::-webkit-scrollbar（Chrome/Safari）；scrollbar-width（Firefox）；scrollbar-color |
| **CSS 变量未定义** | 作用域问题/拼写错 | 在 :root 定义；检查变量名拼写；用 var(--x, default) 设默认值 |
| **calc() 计算错** | 运算符前后无空格/单位错 | calc(100% - 40px)（减号前后必须有空格）；确保单位兼容 |
| **打印样式不对** | 背景色不打印/元素隐藏 | @media print；background 加 color-adjust:exact；检查 .no-print；用 print-color-adjust:exact |
| **深色模式闪烁** | JS 切换主题晚于 CSS 渲染 | 在 <head> 内联 JS 提前设置 data-theme；CSS 默认深色；用 cookie 保存主题 |
| **移动端点击延迟** | 旧浏览器双击缩放 | viewport 设 user-scalable=no（不推荐）；CSS touch-action:manipulation；用 FastClick（旧方案） |
| **1px 边框在高清屏变粗** | 物理像素与逻辑像素差异 | 用 transform:scaleY(0.5)；box-shadow 模拟；SVG 边框；border-image |
| **input 聚焦有蓝色边框** | 浏览器默认 outline | input:focus { outline: none; } 或自定义 outline（无障碍建议保留焦点样式） |
| **button 默认样式** | 浏览器默认 button 样式 | button { background:none; border:none; padding:0; cursor:pointer; } 或 all:unset |
| **a 标签颜色/下划线** | 浏览器默认链接样式 | a { color:inherit; text-decoration:none; } 按需设置 hover 状态 |

---

## 十二、关联笔记

### 前端开发
- [[JavaScript基础入门与进阶]] · [[Vue3-组合式API设计模式]] · [[TypeScript-类型声明文件编写实战]]
- [[前端工程化与构建工具]] · [[前端构建产物分析与优化]] · [[Web性能指标与监控-LCP-FID-CLS]]
- [[Vue表单解决方案-VeeValidate]] · [[Pinia-状态管理核心]] · [[Vue-i18n国际化方案]]

### 全栈与AI
- [[Python-Web框架FastAPI实战]] · [[Python-LangChain应用开发]] · [[AI产品实战框架-从0到1]]
- [[RESTfulAPI设计原则]]

### 导航
- [[MOC-前端开发]] · [[MOC-Python全栈]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握本文 HTML5+CSS3 基础 → 学习 [[JavaScript基础入门与进阶]] 交互逻辑 → 深入 [[Vue3-组合式API设计模式]] 框架开发 → 实践 [[前端工程化与构建工具]] 工程化 → 研究 [[Web性能指标与监控-LCP-FID-CLS]] 性能优化 → 构建完整的前端开发能力。
