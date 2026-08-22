---
title: Python 全栈前端集成知识点系统梳理
tags: [Python全栈, Python, 前端集成, Jinja2, 前后端分离, 静态资源, SSR, 面试]
created: 2026-08-13
updated: 2026-08-13
---

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。


# Python 全栈前端集成知识点系统梳理（优化版）

> **文档说明**：系统梳理 Python 全栈开发中的前端集成方案，涵盖模板引擎、前后端分离架构、静态资源工程化、SSR、Django/Flask/FastAPI 与前端框架协作。

---

## 1. 概述

Python 全栈开发有两种前端集成模式：

| 模式 | 特点 | 适用场景 |
|------|------|----------|
| **服务端渲染（SSR）** | 后端模板渲染 HTML，前后端一体 | 传统网站、CMS、SEO 要求高 |
| **前后端分离** | 后端提供 API，前端独立 SPA | 现代 Web 应用、移动端后端 |

Python 生态的模板引擎：Jinja2（Flask/FastAPI）、Django Templates（Django）。
前端框架：Vue3、React、Svelte，通过 API 与 Python 后端协作。

---


---
## 2. 模板引擎

### 2.1 Jinja2

> 🔍 **知识点深度解析**
>
> **作用**：Jinja2 是 Flask 默认的模板引擎，负责把后端数据渲染进 HTML，实现服务端页面。
>
> **原理**：模板中通过 {{ }} 输出变量、{% %} 写控制结构；引擎在渲染时把上下文变量填充进模板，生成最终 HTML 返回浏览器。
>
> **用法要点**：① {{ }} 输出变量 ② {% %} 写逻辑控制 ③ 支持模板继承 base.html ④ 自动转义防 XSS ⑤ 是 Flask/Django 之外通用引擎


```html
<!-- base.html 基础模板 -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Site{% endblock %}</title>
</head>
<body>
    <nav>{% include "nav.html" %}</nav>
    <main>{% block content %}{% endblock %}</main>
</body>
</html>

<!-- article_list.html 继承模板 -->
{% extends "base.html" %}
{% block title %}文章列表{% endblock %}

{% block content %}
<h1>文章列表</h1>
<ul>
{% for article in articles %}
    <li>
        <a href="{{ url_for('article_detail', id=article.id) }}">
            {{ article.title }}
        </a>
        <span class="date">{{ article.created_at|date:"Y-m-d" }}</span>
    </li>
{% else %}
    <li>暂无文章</li>
{% endfor %}
</ul>
{% endblock %}
```

### 2.2 Jinja2 核心语法

> 🔍 **知识点深度解析**
>
> **作用**：掌握 Jinja2 的变量、控制流与继承语法是写可维护模板的关键。
>
> **原理**：支持 for/if 等控制结构、宏（macro）复用片段、include/extends 做模板组合；过滤器（|）对变量做格式化处理。
>
> **用法要点**：① for/if 控制结构 ② extends/include 模板继承 ③ macro 定义可复用片段 ④ 过滤器 | 格式化变量 ⑤ block 实现可覆盖区域


```jinja2
{# 注释 #}
{{ variable }}           {# 输出变量，自动转义 #}
{{ variable|filter }}    {# 过滤器 #}
{% if condition %}       {# 条件 #}
{% for item in list %}   {# 循环 #}
{% block name %}         {# 模板块 #}
{% extends "base.html" %} {# 继承 #}
{% include "partial.html" %} {# 包含 #}
{% macro input(name) %}  {# 宏（函数） #}
```

### 2.3 自定义过滤器

> 🔍 **知识点深度解析**
>
> **作用**：自定义过滤器封装可复用的展示逻辑，避免模板中写复杂表达式。
>
> **原理**：用 @app.template_filter 或 env.filters 注册函数，模板中通过 {{ var|filter }} 调用；适合格式化日期、截断文本、转换状态等。
>
> **用法要点**：① 用装饰器或 filters 字典注册 ② 模板中以 | 调用 ③ 适合格式化/转换类逻辑 ④ 保持模板简洁 ⑤ 可全局复用


```python
from flask import Flask
app = Flask(__name__)

@app.template_filter("reverse")
def reverse_filter(s):
    return s[::-1]

# 模板中使用
{{ "hello"|reverse }}  {# 输出 olleh #}
```

### 2.4 Django Templates

```html
<!-- Django 模板语法与 Jinja2 类似但有差异 -->
{% extends "base.html" %}
{% block content %}
{% for article in articles %}
    <h2>{{ article.title }}</h2>
    <p>{{ article.content|truncatewords:30 }}</p>
    {% if article.is_published %}
        <span class="badge">已发布</span>
    {% endif %}
{% empty %}
    <p>暂无文章</p>
{% endfor %}
{% endblock %}
```

> 🔍 **知识点深度解析**
>
> **作用**：模板引擎是服务端渲染的核心，理解模板继承和自动转义很重要。
>
> **原理**：Jinja2 是基于文本的模板引擎，将模板编译为 Python 字节码执行，性能好。模板继承（extends）通过 block 实现子模板覆盖父模板内容，include 引入公共片段，macro 实现可复用组件。自动转义（Autoescape）默认开启，输出变量时自动转义 HTML 特殊字符（防 XSS），`|safe` 过滤器关闭转义（仅对可信内容使用）。Jinja2 与 Django Templates 语法相似但不完全兼容：Jinja2 用 `{% if x > 5 %}`，Django 用 `{% if x > 5 %}`（新版支持），过滤器参数语法不同。
>
> **用法要点**：① 模板中不要写复杂逻辑，逻辑放后端；② 用继承 + include 组织模板，减少重复；③ 不要随意用 `|safe`，防 XSS；④ 面试常考：Jinja2 语法、模板继承、自动转义、与 Django 模板区别、SSR 优缺点。

---


---
## 3. 前后端分离架构

### 3.1 架构图

> 🔍 **知识点深度解析**
>
> **作用**：前后端分离架构图帮助理解请求链路与职责划分，是方案沟通的基石。
>
> **原理**：典型链路：浏览器/App → 前端（SPA）→ 后端 API（Django/Flask/FastAPI）→ 数据库/缓存；前后端通过 JSON 接口契约协作。
>
> **用法要点**：① 前端负责视图与交互 ② 后端提供 JSON API ③ 通过 HTTP 接口契约协作 ④ 常见 SPA + REST/GraphQL ⑤ 可配合网关与 CDN


```
┌─────────────┐     HTTP/JSON      ┌──────────────┐
│  前端 SPA   │ ◄──────────────► │  Python API  │
│ (Vue/React) │                    │ (REST/GraphQL)│
└─────────────┘                    └──────┬───────┘
                                          │
                                    ┌─────▼──────┐
                                    │  DB/Redis  │
                                    └────────────┘
```

### 3.2 跨域（CORS）

> 🔍 **知识点深度解析**
>
> **作用**：CORS 解决浏览器同源策略限制，使前端能安全访问不同源的 API。
>
> **原理**：浏览器预检（OPTIONS）请求携带 Origin，服务端通过 Access-Control-Allow-Origin 等响应头授权；简单请求与带凭证请求规则不同。
>
> **用法要点**：① 同源策略限制跨域请求 ② 服务端返回 Allow-Origin 头授权 ③ 预检 OPTIONS 携带 Origin ④ 带 Cookie 需 Allow-Credentials ⑤ Flask-CORS/Django-cors-headers 封装


```python
# FastAPI
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Flask
from flask_cors import CORS
CORS(app, origins=["http://localhost:5173"])

# Django
# settings.py
INSTALLED_APPS += ["corsheaders"]
MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
```

### 3.3 认证

> 🔍 **知识点深度解析**
>
> **作用**：前后端分离下的认证机制保障接口安全，常见为 JWT/Session/OAuth2。
>
> **原理**：JWT 将用户信息编码进无状态 Token，前端存于内存/localStorage 并在 Header 携带；Session 依赖服务端状态；OAuth2 用于第三方授权。
>
> **用法要点**：① JWT 无状态、前端携带 ② Session 依赖服务端存储 ③ Token 放 Authorization 头 ④ 注意 XSS 窃取 Token 风险 ⑤ 刷新 Token 提升安全性


```javascript
// 前端：Axios 拦截器，自动携带 Token
import axios from 'axios'
const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response.status === 401) {
      // Token 过期，跳转登录
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)
```

### 3.4 开发环境代理

```javascript
// Vite 配置：开发时代理 API 请求到后端
// vite.config.js
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：前后端分离是现代 Web 开发的主流架构，理解协作机制很关键。
>
> **原理**：前后端分离后，前端是独立的 SPA（单页应用），通过 HTTP API 与后端通信，数据格式为 JSON。跨域问题：浏览器同源策略阻止不同源的 AJAX 请求，CORS（跨域资源共享）通过后端响应头 `Access-Control-Allow-Origin` 允许指定源访问。开发时用 Vite/Webpack 代理避免跨域，生产环境用 Nginx 反向代理（前端和 API 同源）。认证通常用 JWT，前端存在 localStorage，请求时放在 `Authorization: Bearer <token>` Header。部署时前端构建为静态文件，由 Nginx 提供，API 请求反向代理到后端。
>
> **用法要点**：① 开发用 Vite 代理，生产用 Nginx 同域部署；② JWT 放 Authorization Header（防 CSRF），不要放 Cookie；③ API 路径统一前缀 `/api`；④ 面试常考：前后端分离优缺点、CORS 原理、JWT 认证流程、部署方案、SSR vs CSR。

---


---
## 4. 静态资源工程化

### 4.1 Django 静态资源

> 🔍 **知识点深度解析**
>
> **作用**：Django 的静态资源管理区分开发期与收集期，是模板正确加载 CSS/JS 的前提。
>
> **原理**：开发用 STATIC_URL 直接服务；生产用 collectstatic 将各 app 静态文件汇总到 STATIC_ROOT，由 Nginx 直接托管提升性能。
>
> **用法要点**：① STATIC_URL 配置访问前缀 ② collectstatic 收集到 STATIC_ROOT ③ 生产由 Nginx 直接托管 ④ DEBUG=False 需配置静态服务 ⑤ 避免动态服务静态文件


```python
# settings.py
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # 收集后目录
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]  # 源目录

# 生产环境收集静态文件
python manage.py collectstatic
```

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/app.js' %}"></script>
```

### 4.2 前端构建集成

> 🔍 **知识点深度解析**
>
> **作用**：前端构建集成把打包产物接入后端模板或静态目录，实现一体化部署。
>
> **原理**：前端用 Vite/Webpack 构建产物（JS/CSS），后端模板引用或复制到静态目录；可通过 manifest 做缓存破坏（cache busting）。
>
> **用法要点**：① 构建产物交由后端托管 ② 模板引用带 hash 的资源 ③ 支持缓存破坏 ④ CI 中先构建再收集 ⑤ 前后端版本需对齐


```bash
# 前端构建输出到 Django 静态目录
# vite.config.js
export default {
  build: {
    outDir: '../backend/static/dist',
    emptyOutDir: true,
  }
}

# 构建
cd frontend && npm run build
# 输出到 backend/static/dist/
```

### 4.3 Nginx 静态资源配置

> 🔍 **知识点深度解析**
>
> **作用**：用 Nginx 直接托管静态资源可大幅降低后端压力并提升加载速度。
>
> **原理**：location 规则将 /static 映射到文件目录，expires 设置浏览器缓存，gzip 压缩传输；动态请求再反代到应用服务器。
>
> **用法要点**：① location 映射静态目录 ② expires 设置缓存 ③ gzip 开启压缩 ④ 静态由 Nginx 直接返回 ⑤ 动态请求反代到后端


```nginx
location /static/ {
    alias /path/to/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

location / {
    # SPA 前端路由 fallback
    try_files $uri $uri/ /index.html;
}

location /api/ {
    proxy_pass http://127.0.0.1:8000;
}
```

---


---
## 5. SSR vs CSR

| 维度 | SSR（服务端渲染） | CSR（客户端渲染） |
|------|-------------------|-------------------|
| 首屏速度 | 快（HTML 直出） | 慢（需加载JS再渲染） |
| SEO | 友好 | 不友好（需SSR/预渲染） |
| 服务器压力 | 大 | 小 |
| 交互体验 | 页面跳转 | 无刷新体验好 |
| 开发复杂度 | 低（模板） | 高（前后端分离） |
| 适用 | 内容站、电商 | 后台管理、应用 |

**混合方案**：
- Nuxt.js（Vue SSR）/ Next.js（React SSR）+ Python API
- 首屏 SSR，后续 CSR（同构应用）

---


---
## 6. Django REST Framework（DRF）

```python
# serializers.py
from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    
    class Meta:
        model = Article
        fields = ["id", "title", "content", "author_name", "created_at"]

# views.py
from rest_framework import viewsets
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# urls.py
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r"articles", ArticleViewSet)
urlpatterns = [path("api/", include(router.urls))]
```

---

## 6.1 WebSocket 实时通信

```python

> 🔍 **知识点深度解析**
>
> **作用**：Python 后端通过 WebSocket 实现服务端主动推送，适用于聊天、通知、实时数据和协同编辑。
>
> **原理**：FastAPI 原生 WebSocket：async def ws_endpoint(websocket: WebSocket)，await websocket.accept()/receive_text()/send_text()。Django Channels 用 Consumer 处理连接，channel layer（Redis）支持跨进程广播。Flask-SocketIO 用 @socketio.on。生产需 ASGI 服务器（Uvicorn/Daphne），Nginx 配置 Upgrade/Connection 头支持 WebSocket 代理。
>
> **用法要点**：① FastAPI 原生 WebSocket，Django Channels（ASGI）  ② Redis channel layer 实现跨进程广播和房间  ③ Nginx 需配置 proxy_set_header Upgrade $http_upgrade  ④ WebSocket 鉴权：连接时 token 校验（query 参数或子协议）  ⑤ 面试常考：WebSocket vs SSE、ASGI 部署、广播实现

# FastAPI WebSocket
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"服务器收到: {data}")
    except WebSocketDisconnect:
        print("客户端断开")
```

```javascript
// 前端 Vue + WebSocket（心跳重连）
const ws = new WebSocket('ws://localhost:8000/ws/chat')
ws.onmessage = (e) => console.log(e.data)
ws.onclose = () => {
  // 自动重连
  setTimeout(() => location.reload(), 3000)
}
// 心跳：每30秒发 ping
setInterval(() => ws.send('ping'), 30000)
```

---

## 6.2 文件上传与下载

```python

> 🔍 **知识点深度解析**
>
> **作用**：Python Web 文件上传处理 multipart/form-data，下载通过 FileResponse/Streaming 实现大文件流式传输。
>
> **原理**：FastAPI：UploadFile 接收上传文件（await file.read() 读取，file.file 是 SpooledTemporaryFile 假脱机到磁盘）。Django：request.FILES 获取文件，FileSystemStorage 保存。下载：FastAPI FileResponse（支持断点续传）或 StreamingResponse（流式生成）。大文件上传用分片上传，下载用 StreamingResponse 分块读取避免内存溢出。
>
> **用法要点**：① FastAPI UploadFile 自动假脱机到磁盘，不占内存  ② Django request.FILES['file'] 获取上传文件  ③ FileResponse 自动处理 Content-Length 和断点续传  ④ StreamingResponse 分块流式传输大文件/动态生成内容  ⑤ 面试常考：大文件上传、流式下载、断点续传、内存控制

# FastAPI 文件上传
from fastapi import UploadFile, File

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # 大文件分片上传：前端切片，后端合并
    # 断点续传：记录已上传分片，支持续传
    content = await file.read()
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(content)
    return {"filename": file.filename}

# 流式下载（大文件不占内存）
from fastapi.responses import StreamingResponse

@app.get("/download")
async def download_file():
    def iterfile():
        with open("large_file.zip", "rb") as f:
            for chunk in iter(lambda: f.read(1024*1024), b""):
                yield chunk
    return StreamingResponse(
        iterfile(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=file.zip"}
    )
```

---

## 6.3 国际化（i18n）

```python

> 🔍 **知识点深度解析**
>
> **作用**：Python Web 国际化通过 gettext 提取翻译字符串，配合中间件根据用户语言切换 locale。
>
> **原理**：Django：USE_I18N=True，{% trans "text" %} 或 gettext_lazy 标记字符串，django-admin makemessages -l zh_Hans 生成 .po 文件，compilemessages 编译为 .mo。FastAPI：使用 babel 库，gettext 标记，babel extract/init/compile 流程。语言检测：Accept-Language 头、URL 前缀（/zh/、/en/）或 Cookie。
>
> **用法要点**：① gettext_lazy 延迟翻译（模型/表单定义时用），gettext 即时翻译  ② makemessages 提取 .po，compilemessages 编译 .mo  ③ LocaleMiddleware 根据 Accept-Language/URL 切换语言  ④ FastAPI 用 Babel 库，中间件设置 locale  ⑤ 面试常考：i18n 流程、gettext、.po/.mo、语言检测

# Django i18n
# settings.py
USE_I18N = True
LANGUAGE_CODE = "zh-hans"
LANGUAGES = [("en", "English"), ("zh-hans", "简体中文")]

# 模板中
{% load i18n %}
<h1>{% trans "欢迎" %}</h1>

# Flask-Babel
from flask_babel import Babel, gettext
babel = Babel(app)
print(gettext("Hello"))  # 根据 locale 翻译

# 前端 vue-i18n
// Vue3 国际化，语言切换，消息翻译
```

---

## 6.4 SEO 优化

| 技术 | 说明 |
|------|------|
| **SSR/SSG** | 服务端渲染/静态生成，搜索引擎直接抓取 HTML |
| **meta 标签** | title、description、keywords、og: 标签 |
| **sitemap.xml** | 提交给搜索引擎的站点地图 |
| **robots.txt** | 控制搜索引擎爬取 |
| **结构化数据** | JSON-LD Schema.org 标记 |
| **语义化 HTML** | h1-h6、article、nav、header 等 |

```python

> 🔍 **知识点深度解析**
>
> **作用**：Python Web SEO 包括 SSR/模板渲染、sitemap、robots.txt、结构化数据和元标签优化。
>
> **原理**：Django/Flask/Jinja2 服务端渲染（SSR）对搜索引擎友好（SPA 需 prerender 或 SSR）。sitemap.xml：Django 自带 sitemaps 框架，FastAPI 动态生成。robots.txt 控制爬取范围。语义化 HTML、meta description/og 标签、结构化数据（JSON-LD）提升搜索展现。URL 设计语义化（/articles/python-asyncio 而非 /article?id=1）。
>
> **用法要点**：① 服务端渲染（Jinja2/Django Template）比 SPA 更利于 SEO  ② sitemap.xml 动态生成，robots.txt 控制爬取  ③ meta description/og 标签、JSON-LD 结构化数据  ④ 语义化 URL 和面包屑导航  ⑤ 面试常考：SSR vs CSR for SEO、sitemap、meta 标签

# Django 生成 sitemap
# FastAPI 可直接返回 XML
@app.get("/sitemap.xml")
async def sitemap():
    return Response(content=sitemap_xml, media_type="application/xml")
```

---

## 6.5 SSE（Server-Sent Events）

比 WebSocket 轻量的单向服务器推送。

```python

> 🔍 **知识点深度解析**
>
> **作用**：SSE 是服务端单向推送协议，基于 HTTP，比 WebSocket 轻量，适合通知/日志流/AI 流式输出。
>
> **原理**：SSE 使用 text/event-stream Content-Type，服务端持续发送 data: 内容\n\n 格式的事件。浏览器用 EventSource API 接收（自动重连）。FastAPI 返回 StreamingResponse 生成器，media_type='text/event-stream'。相比 WebSocket：SSE 单向（服务端→客户端）、基于 HTTP 无需特殊协议、自动重连、支持自定义事件类型。LLM 流式输出（打字机效果）是典型场景。
>
> **用法要点**：① Content-Type: text/event-stream，data: 消息\n\n 格式  ② EventSource 浏览器 API，自动重连，比 WebSocket 简单  ③ FastAPI StreamingResponse + 生成器实现  ④ 单向推送，适合通知/日志/AI 流式响应  ⑤ 面试常考：SSE vs WebSocket、event-stream、自动重连

# FastAPI SSE
from fastapi.responses import StreamingResponse
import asyncio

@app.get("/events")
async def events():
    async def event_generator():
        while True:
            yield f"data: {json.dumps({'time': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

```javascript
// 前端 EventSource
const es = new EventSource('/events')
es.onmessage = (e) => console.log(JSON.parse(e.data))
```

---


---
## 7. 面试高频考点

1. **Jinja2 模板**：语法、继承、自动转义、过滤器
2. **前后端分离**：优缺点、协作流程
3. **CORS**：原理、配置、同源策略
4. **JWT 认证**：前后端流程、Token 管理
5. **静态资源**：Django collectstatic、Nginx 配置
6. **SSR vs CSR**：区别、选型、混合方案
7. **DRF**：Serializer、ViewSet、Router
8. **部署方案**：Nginx 反向代理 + 静态资源 + API
9. **开发环境**：Vite 代理、前后端联调
10. **模板引擎对比**：Jinja2 vs Django Templates
11. **WebSocket**：实时通信、心跳重连、Django Channels
12. **文件处理**：大文件分片上传、断点续传、流式下载
13. **国际化**：Django i18n、Flask-Babel、vue-i18n
14. **SEO**：SSR/SSG、meta标签、sitemap、结构化数据
15. **SSE**：服务端推送、与WebSocket区别

---


---
## 📝 精简总结

- 两种模式：SSR（模板渲染）和前后端分离（API + SPA）
- 模板引擎：Jinja2（Flask/FastAPI）、Django Templates，继承+include+自动转义
- 前后端分离：JSON API 通信，CORS 跨域，JWT 认证
- 开发：Vite 代理 API，生产：Nginx 同域部署
- 静态资源：Django collectstatic，前端构建输出到 static，Nginx 缓存
- SSR 首屏快 SEO 好，CSR 体验好，混合用 Nuxt/Next
- DRF 是 Django API 首选，Serializer+ViewSet+Router
- WebSocket：FastAPI 原生支持，Django Channels，前端心跳重连
- 文件处理：大文件分片上传+断点续传，流式下载 StreamingResponse
- 国际化：Django i18n / Flask-Babel / vue-i18n，语言切换
- SEO：SSR/SSG、meta标签、sitemap.xml、robots.txt、结构化数据
- SSE：服务端单向推送，比 WebSocket 轻量，EventSource 接收
- 前端工程化：Vite/Webpack 构建，与 Python 后端通过 API 解耦

---

[[08-Python全栈/MOC-Python全栈|← 返回 Python 全栈 MOC]] | [[Home|🏠 返回首页]]
