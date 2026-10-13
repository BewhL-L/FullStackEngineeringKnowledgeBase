---
title: Jinja2 模板引擎
tags: [Python, Jinja2, 前端, 服务端渲染]
category: Python全栈
created: 2026-08-13
updated: 2026-09-08
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[Python-语法基础与数据结构]]]]", "[[[[Flask-轻量服务架构]]"]
aliases: [Jinja2-模板引擎, Jinja2, 模板引擎]
category: Python全栈
difficulty: ⭐⭐⭐

---

# Jinja2 模板引擎

> **文档说明**：深入讲解 Jinja2 模板引擎的语法体系（变量/过滤器/测试/控制结构/宏/继承）、模板继承与包含机制、自定义过滤器与全局函数、自动转义与安全、性能优化（字节码缓存/加载器），含 Flask 集成和独立使用的完整示例。
>
> **适用人群**：Python Web 开发者、需要服务端渲染页面的全栈工程师、使用 Flask/Django/FastAPI 的开发者
>
> **前置知识**：[[Python-语法基础与数据结构]]、[[Flask-轻量服务架构]]、[[HTML5语义化与基础标签]]

---

## 一、概述

### 1. 定义与核心价值

Jinja2 是 Python 生态中最流行的模板引擎，被 Flask、FastAPI（通过 `Jinja2Templates`）、Django（可替换默认引擎）等框架使用。它将 HTML 模板与 Python 数据结合，生成最终的 HTML 页面。Jinja2 的设计灵感来自 Django 模板引擎，但语法更灵活、功能更强大，支持模板继承、宏定义、自定义过滤器等高级特性。

### 2. 痛点对比

| 痛点（字符串拼接 HTML） | Jinja2 解决方式 |
|---------------------|---------------|
| Python 代码中拼接 HTML 字符串，可读性差 | 模板文件独立存放，HTML 与逻辑分离 |
| 变量插入需手动 `str.format()`，容易遗漏 | `{{ variable }}` 语法简洁直观 |
| 条件判断和循环需在 Python 中拼接 | 模板内 `{% if %}` / `{% for %}` 直接控制 |
| 公共页面部分（导航/页脚）需重复复制 | 模板继承 `{% extends %}` + `{% block %}` 复用 |
| XSS 风险：用户输入直接插入 HTML | 自动转义（Autoescape）默认开启 |
| 日期/货币格式化需在 Python 中预处理 | 过滤器 `{{ date|date("Y-m-d") }}` 模板内格式化 |
| 模板修改需重启应用 | 文件系统加载器自动检测变更（开发模式） |

### 3. Jinja2 核心架构

```mermaid
graph TB
    subgraph 模板源
        A[模板文件<br/>.html]
        B[模板字符串]
    end

    subgraph Jinja2 核心
        C[Environment<br/>环境配置]
        D[Loader<br/>模板加载器]
        E[Lexer<br/>词法分析]
        F[Parser<br/>语法分析]
        G[Compiler<br/>编译为 Python 字节码]
        H[Template<br/>模板对象]
    end

    subgraph 渲染
        I[Context<br/>上下文字典]
        H --> J[render(context)<br/>渲染输出]
        I --> J
    end

    A --> D
    B --> C
    D --> C
    C --> E
    E --> F
    F --> G
    G --> H
    J --> K[HTML 输出]
```

<div style="background:linear-gradient(135deg,#f093fb,#f5576c);border-radius:16px;padding:20px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#fff;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes flow{0%{transform:translateX(-10px);opacity:0}15%{transform:translateX(0);opacity:1}85%{transform:translateX(0);opacity:1}100%{transform:translateX(10px);opacity:0}}.flow-step{display:inline-block;background:rgba(255,255,255,.2);border:2px solid rgba(255,255,255,.5);border-radius:8px;padding:10px 14px;margin:4px;text-align:center;font-weight:600;font-size:13px;animation:flow 4s ease-in-out infinite;min-width:90px}.flow-step:nth-child(2){animation-delay:.5s}.flow-step:nth-child(4){animation-delay:1s}.flow-step:nth-child(6){animation-delay:1.5s}.flow-step:nth-child(8){animation-delay:2s}.flow-arrow{display:inline-block;font-size:20px;animation:flow 4s ease-in-out infinite;vertical-align:middle}.flow-code{background:rgba(0,0,0,.2);border-radius:6px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:8px 12px;margin-top:10px;font-family:monospace;font-size:12px;text-align:center}</style>
<div style="text-align:center;font-size:15px;font-weight:700;margin-bottom:14px;padding-bottom:10px;border-bottom:1.5px solid rgba(255,255,255,.22);letter-spacing:1px;text-shadow:0 1px 3px rgba(0,0,0,.12)">Jinja2 模板渲染流程</div>
<div style="text-align:center;white-space:nowrap;overflow-x:auto"><span class="flow-step">模板源文件</span><span class="flow-arrow">→</span><span class="flow-step">Loader加载</span><span class="flow-arrow">→</span><span class="flow-step">Lexer词法分析</span><span class="flow-arrow">→</span><span class="flow-step">Parser语法分析</span><span class="flow-arrow">→</span><span class="flow-step">Compiler编译字节码</span><span class="flow-arrow">→</span><span class="flow-step">Template渲染</span><span class="flow-arrow">→</span><span class="flow-step">HTML输出</span></div>
<div class="flow-code">编译为Python字节码后缓存，二次渲染直接执行字节码，性能极高</div>
<div style="text-align:center;font-size:12px;opacity:.85;margin-top:8px">模板继承：extends + block 实现布局复用，子模板覆盖父模板block</div>
</div>

---


> 💡 **深度讲解**：Jinja2 是 Python 生态最流行的模板引擎，被 Flask、FastAPI、Django（可替换）等框架使用。它的核心价值在于将 HTML 模板与 Python 数据分离，通过 {{ variable }} 输出变量、{% if %}/{% for %} 控制逻辑、|filter 过滤器格式化、{% extends %}/{% block %} 模板继承实现布局复用。Jinja2 的架构是典型的编译器流水线：Lexer 词法分析 → Parser 语法分析 → Compiler 编译为 Python 字节码 → Template 渲染，编译后的字节码可以缓存，二次渲染性能极高。自动转义（Autoescape）默认开启，从根源防止 XSS 攻击。与 Django 模板引擎相比，Jinja2 语法更灵活（支持更复杂的表达式、宏定义、自定义过滤器），性能更好。
>
> **📝 精简总结**：Jinja2 = 变量输出{{ }} + 控制结构{% %} + 过滤器| + 模板继承extends/block + 宏macro + 自动转义。架构是 Lexer→Parser→Compiler→Template 编译流水线，字节码缓存提升性能。Flask/FastAPI/Django 均可使用。

## 二、底层原理

> 🔍 **知识点深度解析：模板继承机制**
>
> **作用**：模板继承通过 extends 和 block 实现布局复用，父模板定义骨架和可替换区域，子模板覆盖特定 block，是 Jinja2 避免重复代码的核心机制。
>
> **原理**：Jinja2 的模板继承基于模板编译器实现：父模板中的 {% block name %} 标记为可替换区域，编译时生成对应的 block 函数。子模板通过 {% extends 'base.html' %} 声明继承父模板，通过 {% block name %} 覆盖父模板的同名 block。渲染时，子模板的 block 函数替换父模板的对应函数，未覆盖的 block 使用父模板默认内容。{{ super() }} 可以在子模板中调用父模板的 block 内容，实现追加而非完全替换。模板支持多层继承（孙模板继承子模板）。
>
> **用法要点**：① 父模板用 {% block name %}...{% endblock %} 定义可替换区域 ② 子模板用 {% extends 'base.html' %} 声明继承，且必须是第一行 ③ 子模板中只能定义 block，不能有 block 外的内容 ④ {{ super() }} 调用父模板 block 内容，实现追加 ⑤ 模板名基于 Loader 路径解析，支持相对路径 ⑥ 多层继承时，最近的子模板 block 优先级最高

### 1. 模板编译流程

Jinja2 不是逐行解释模板，而是将模板**编译为 Python 字节码**后执行，这使得渲染速度非常快：

```text
模板源码 → 词法分析（Token 流）→ 语法分析（AST）→ 编译（Python 代码）→ 字节码缓存 → 执行渲染
```
```python
# Jinja2 编译后的 Python 代码（简化版）
# 模板: <p>Hello, {{ name }}!</p>
# 编译为:
def render(context):
    result = []
    result.append("<p>Hello, ")
    result.append(str(context["name"]))  # 变量输出
    result.append("!</p>")
    return "".join(result)
```
### 2. 语法元素

| 语法 | 名称 | 作用 | 示例 |
|------|------|------|------|
| `{{ ... }}` | 变量输出 | 输出表达式结果 | `{{ user.name }}` |
| `{% ... %}` | 语句标签 | 控制结构（if/for/block） | `{% if user %}` |
| `{# ... #}` | 注释 | 模板注释，不输出 | `{# 这是注释 #}` |
| `#} ... {#` | 行语句 | 行级控制（需配置） | `# for item in items` |

### 3. 变量查找规则

Jinja2 的变量查找支持点号（`.`）和下标（`[]`）两种方式，查找顺序为：

```text
{{ user.name }} 的查找顺序：
1. getattr(user, 'name')        → 属性查找
2. user['name']                 → 字典/列表查找
3. getattr(user, 'name') 失败时 → 返回 undefined
```
### 4. 自动转义机制

Jinja2 默认对 `.html` / `.htm` / `.xml` 后缀的模板开启自动转义，防止 XSS：

```python
# 自动转义前
context = {"comment": "<script>alert('xss')</script>"}
# 模板: {{ comment }}
# 输出: &lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;

# 如需禁用转义（确认内容安全时）
{{ comment|safe }}
# 或在 Python 中标记为安全字符串
from markupsafe import Markup
context["comment"] = Markup("<b>安全的 HTML</b>")
```
---


> 💡 **深度讲解**：本章深入拆解了技术的底层原理和核心机制，包括架构设计、工作流程、关键技术实现细节。理解原理的价值在于：当遇到文档未覆盖的边缘场景或性能问题时，能够基于原理进行推理和调试，而不是依赖试错。建议结合 Mermaid 架构图，在脑中模拟一次完整的请求/数据流转过程，确保每个环节都理解透彻。
>
> **📝 精简总结**：本章深入讲解了技术的核心原理、架构设计、工作流程和关键实现细节，配合架构图帮助理解底层机制。

## 三、实操

### 1. 独立使用 Jinja2

```python
# basic_usage.py
from jinja2 import Environment, FileSystemLoader, select_autoescape

# 创建环境
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,       # 去除块标签后的第一个换行
    lstrip_blocks=True,     # 去除块标签前的空白
)

# 加载并渲染模板
template = env.get_template("index.html")
html = template.render(
    title="我的博客",
    user={"name": "张三", "is_admin": True},
    posts=[
        {"title": "第一篇", "content": "内容1", "date": "2026-01-01"},
        {"title": "第二篇", "content": "内容2", "date": "2026-01-02"},
    ],
)
print(html)
```
### 2. 基础语法

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    {# 变量与过滤器 #}
    <h1>欢迎，{{ user.name|upper }}！</h1>

    {# 条件判断 #}
    {% if user.is_admin %}
        <p>您是管理员</p>
    {% elif user.is_vip %}
        <p>您是 VIP 用户</p>
    {% else %}
        <p>普通用户</p>
    {% endif %}

    {# 循环 #}
    <ul>
    {% for post in posts %}
        <li>
            <h3>{{ post.title }}</h3>
            <p>{{ post.content|truncate(50) }}</p>
            <time>{{ post.date }}</time>
        </li>
    {% else %}
        <li>暂无文章</li>
    {% endfor %}
    </ul>

    {# 循环变量 #}
    <p>共 {{ posts|length }} 篇文章</p>
</body>
</html>
```
### 3. 常用过滤器

```json
{# 字符串过滤器 #}
{{ name|upper }}              {# 转大写 #}
{{ name|lower }}              {# 转小写 #}
{{ name|capitalize }}         {# 首字母大写 #}
{{ name|title }}              {# 每个单词首字母大写 #}
{{ name|trim }}               {# 去除首尾空白 #}
{{ content|truncate(100) }}   {# 截断到 100 字符 #}
{{ content|striptags }}       {# 去除 HTML 标签 #}
{{ content|replace("old", "new") }}  {# 替换 #}

{# 列表过滤器 #}
{{ items|length }}            {# 长度 #}
{{ items|sort }}              {# 排序 #}
{{ items|reverse }}           {# 反转 #}
{{ items|unique }}            {# 去重 #}
{{ items|join(", ") }}        {# 连接为字符串 #}
{{ items|first }}             {# 第一个元素 #}
{{ items|last }}              {# 最后一个元素 #}
{{ items|slice(3) }}          {# 分片 #}

{# 数字过滤器 #}
{{ price|round(2) }}          {# 保留 2 位小数 #}
{{ number|abs }}              {# 绝对值 #}
{{ 1234567|filesizeformat }}  {# 人类可读文件大小 #}

{# 日期/格式化 #}
{{ date|strftime("%Y-%m-%d") }}  {# 日期格式化（需自定义） #}

{# 安全/转义 #}
{{ html_content|safe }}       {# 标记为安全，不转义 #}
{{ html_content|e }}          {# 手动转义 #}
{{ url|urlencode }}           {# URL 编码 #}

{# 默认值 #}
{{ variable|default("默认值") }}  {# 变量不存在时使用默认值 #}
{{ variable|default("默认值", true) }}  {# 变量为 false 时也用默认值 #}

{# 链式调用 #}
{{ content|striptags|truncate(100)|upper }}
```
### 4. 模板继承

```html
<!-- templates/base.html - 基础模板 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}默认标题{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/style.css">
    {% block extra_head %}{% endblock %}
</head>
<body>
    <header>
        <nav>
            <a href="/">首页</a>
            <a href="/about">关于</a>
        </nav>
    </header>

    <main>
        {% block content %}{% endblock %}
    </main>

    <footer>
        {% block footer %}
        <p>&copy; 2026 我的网站</p>
        {% endblock %}
    </footer>

    {% block scripts %}{% endblock %}
</body>
</html>
```
```html
<!-- templates/post.html - 继承基础模板 -->
{% extends "base.html" %}

{% block title %}{{ post.title }} - 我的博客{% endblock %}

{% block extra_head %}
<meta name="description" content="{{ post.summary }}">
{% endblock %}

{% block content %}
<article>
    <h1>{{ post.title }}</h1>
    <time>{{ post.date|strftime("%Y年%m月%d日") }}</time>
    <div class="content">{{ post.content|safe }}</div>
</article>

{% include "partials/_comments.html" %}
{% endblock %}

{% block scripts %}
<script src="/static/js/post.js"></script>
{% endblock %}
```
### 5. 宏（Macro）

```html
<!-- templates/macros.html - 宏定义 -->
{% macro render_pagination(pagination, endpoint) %}
<nav class="pagination">
    {% if pagination.has_prev %}
        <a href="{{ url_for(endpoint, page=pagination.prev_num) }}">上一页</a>
    {% endif %}

    {% for page in pagination.iter_pages() %}
        {% if page %}
            {% if page != pagination.page %}
                <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
            {% else %}
                <span class="current">{{ page }}</span>
            {% endif %}
        {% else %}
            <span class="ellipsis">...</span>
        {% endif %}
    {% endfor %}

    {% if pagination.has_next %}
        <a href="{{ url_for(endpoint, page=pagination.next_num) }}">下一页</a>
    {% endif %}
</nav>
{% endmacro %}

{% macro form_field(field, label=None) %}
<div class="form-group">
    <label>{{ label or field.label.text }}</label>
    {{ field(class="form-control") }}
    {% if field.errors %}
        <ul class="errors">
        {% for error in field.errors %}
            <li>{{ error }}</li>
        {% endfor %}
        </ul>
    {% endif %}
</div>
{% endmacro %}
```
```python
<!-- 使用宏 -->
{% from "macros.html" import render_pagination, form_field %}

{{ render_pagination(pagination, 'list_posts') }}

<form method="post">
    {{ form_field(form.title) }}
    {{ form_field(form.content, label="文章内容") }}
    <button type="submit">提交</button>
</form>
```
### 6. 自定义过滤器和全局函数

```python
# custom_filters.py
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import markdown as md_lib


def strftime(value, format="%Y-%m-%d %H:%M"):
    """日期格式化过滤器"""
    if isinstance(value, datetime):
        return value.strftime(format)
    return value


def markdown(value):
    """Markdown 转 HTML 过滤器"""
    return Markup(md_lib.markdown(value, extensions=["fenced_code", "codehilite"]))


def nl2br(value):
    """换行转 <br>"""
    return Markup(value.replace("\n", "<br>\n"))


def pluralize(count, singular="", plural="s"):
    """复数化：1 item vs 2 items"""
    return singular if count == 1 else plural


# 注册到环境
env = Environment(loader=FileSystemLoader("templates"))
env.filters["strftime"] = strftime
env.filters["markdown"] = markdown
env.filters["nl2br"] = nl2br
env.filters["pluralize"] = pluralize

# 注册全局函数
env.globals["current_year"] = lambda: datetime.now().year
env.globals["site_name"] = "我的博客"
```
```html
<!-- 使用自定义过滤器 -->
<time>{{ post.created_at|strftime("%Y年%m月%d日") }}</time>
<div class="content">{{ post.content|markdown }}</div>
<p>{{ post.comments|length }} 条评论{{ post.comments|length|pluralize }}</p>
<footer>&copy; {{ current_year() }} {{ site_name }}</footer>
```
### 7. Flask 集成

```python
# app.py
from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

# 注册自定义过滤器
@app.template_filter("strftime")
def strftime(value, format="%Y-%m-%d"):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value

# 注册全局函数
@app.template_global("current_year")
def current_year():
    return datetime.now().year

# 注册测试器
@app.template_test("past")
def is_past(date):
    return date < datetime.now()

@app.route("/")
def index():
    return render_template("index.html",
                           title="首页",
                           now=datetime.now())
```
### 8. 模板测试器（Tests）

```json
{# 内置测试器 #}
{% if user is defined %}...{% endif %}
{% if user is none %}...{% endif %}
{% if number is odd %}...{% endif %}
{% if number is even %}...{% endif %}
{% if sequence is iterable %}...{% endif %}
{% if mapping is mapping %}...{% endif %}
{% if string is string %}...{% endif %}
{% if number is number %}...{% endif %}

{# 自定义测试器 #}
{% if date is past %}
    <span class="expired">已过期</span>
{% endif %}
```
---


> 💡 **深度讲解**：本章提供了从环境搭建到完整项目示例的实操指南，包含可运行的代码示例和最佳实践。实操是掌握技术的关键环节——'纸上得来终觉浅，绝知此事要躬行'。建议按照示例顺序动手实现，每段代码都要理解其作用，而不是简单复制粘贴。遇到报错时，先阅读错误信息再排查，这是提升调试能力的最佳途径。
>
> **📝 精简总结**：本章提供了完整的实操指南，包括环境搭建、快速上手、核心用法、最佳实践和完整项目示例，代码可直接运行。

## 四、常见问题与排查

| 问题现象 | 原因 | 解决方案 |
|---------|------|---------|
| `TemplateNotFound: base.html` | 模板路径配置错误，或模板不在 loader 搜索路径中 | 确认 `FileSystemLoader` 路径正确；Flask 中模板默认在 `templates/` 目录 |
| 变量输出为原始 HTML 而非渲染 | 自动转义将 `<` 转义为 `&lt;` | 确认内容安全后使用 `{{ content|safe }}`，或用 `Markup()` 标记 |
| `UndefinedError: 'xxx' is undefined` | 模板中使用了未传入的变量 | 传入变量，或使用 `{{ variable|default("默认值") }}` |
| 模板修改后不生效 | 字节码缓存未刷新，或 `auto_reload=False` | 开发环境设置 `auto_reload=True`（Flask 默认开启）；生产环境重启服务 |
| `{% block %}` 内容不显示 | 子模板中 `{% extends %}` 必须是第一个标签，前面不能有内容 | 确保 `{% extends "base.html" %}` 在模板文件第一行 |
| 中文显示为乱码 | 文件编码不是 UTF-8，或响应头未设置 charset | 模板文件保存为 UTF-8；Flask 响应默认 `text/html; charset=utf-8` |
| `url_for` 在模板中报错 | Flask 上下文未激活，或端点名称错误 | 确保在 Flask 请求上下文中渲染；检查端点名（蓝图名.函数名） |
| 循环中 `loop.index` 从 0 开始 | `loop.index` 从 1 开始，`loop.index0` 从 0 开始 | 需要 0 基时用 `loop.index0`，1 基用 `loop.index` |
| 宏中无法访问外部变量 | 宏有独立作用域，不继承外部上下文 | 通过参数传递变量，或使用 `{{ var }}` 传入 |
| 大模板渲染慢 | 模板未编译缓存，或模板过于复杂 | 启用 `BytecodeCache`；拆分模板为 include/宏；避免模板中做复杂计算 |

---


> 💡 **深度讲解**：本章汇总了常见错误、性能瓶颈、安全风险和生产环境踩坑记录，采用'问题→原因→方案'的结构帮助快速定位和解决问题。生产环境中的问题往往不是技术本身的问题，而是使用方式不当或边界条件未考虑。建议在项目上线前，对照本章的问题清单逐一检查，提前规避常见陷阱。遇到本章未覆盖的问题时，按照'复现→定位→分析→解决→记录'的流程处理。
>
> **📝 精简总结**：本章汇总了常见错误、性能优化、安全防护和生产踩坑记录，采用问题→原因→方案结构，帮助快速排查解决问题。

## 五、进阶与最佳实践

### 1. 模板组织规范

```text
templates/
├── base.html                  # 顶层基础模板
├── layouts/
│   ├── admin.html             # 管理后台布局
│   └── auth.html              # 认证页面布局
├── pages/                     # 页面级模板
│   ├── index.html
│   └── post_detail.html
├── partials/                  # 可复用片段（HTMX 等）
│   ├── _post_card.html
│   └── _pagination.html
├── macros/                    # 宏定义
│   ├── forms.html
│   └── ui.html
└── emails/                    # 邮件模板
    ├── welcome.html
    └── reset_password.html
```
### 2. 性能优化

| 优化手段 | 说明 | 预期收益 |
|---------|------|---------|
| **字节码缓存** | `FileSystemBytecodeCache` 缓存编译后的模板 | 重复渲染速度提升 3-5 倍 |
| **自动重载关闭** | 生产环境 `auto_reload=False` | 减少文件系统检查开销 |
| **模板拆分** | 大模板拆分为 `include` + 宏 | 提高可维护性，部分可缓存 |
| **片段缓存** | 对不常变化的片段做缓存（Flask-Caching） | 减少数据库查询和渲染时间 |
| **避免模板中计算** | 复杂逻辑放在 Python 视图中 | 模板只做展示，逻辑清晰 |
| **静态资源 CDN** | CSS/JS 用 CDN，不经过模板引擎 | 减少服务器负载 |

```python
# 字节码缓存配置
from jinja2 import Environment, FileSystemLoader, FileSystemBytecodeCache

env = Environment(
    loader=FileSystemLoader("templates"),
    bytecode_cache=FileSystemBytecodeCache("templates/.cache"),
    auto_reload=False,  # 生产环境关闭
)
```
### 3. 安全最佳实践

| 安全措施 | 说明 |
|---------|------|
| **自动转义** | 始终开启 `autoescape=True`，不要全局关闭 |
| **`safe` 过滤器慎用** | 仅对完全可信的内容使用 `|safe` |
| **用户输入不直接用 `safe`** | 用户提交的 HTML 需用 Bleach 等库清洗后再 `safe` |
| **CSP 策略** | 配合 Content-Security-Policy 防止 XSS |
| **模板注入防护** | 不要用用户输入作为模板内容渲染（SSTI 攻击） |
| **敏感信息** | 模板中不硬编码密码、密钥等敏感信息 |

### 4. Jinja2 与其他模板引擎对比

| 维度 | Jinja2 | Django Template | Mako | Mustache |
|------|--------|----------------|------|----------|
| 语法 | `{{ }}` / `{% %}` | `{{ }}` / `{% %}` | `<% %>` / `${}` | `{{ }}` |
| 逻辑能力 | 强（可写表达式） | 中（受限） | 强（可写 Python） | 弱（无逻辑） |
| 模板继承 | 支持 | 支持 | 支持 | 不支持（需 Partial） |
| 宏 | 支持 | 不支持（需 Inclusion Tag） | 支持 | 不支持 |
| 自动转义 | 默认开启 | 默认开启 | 需手动 | 默认开启 |
| 速度 | 快（编译为字节码） | 中 | 快 | 快 |
| 适用框架 | Flask/FastAPI | Django | Pyramid | 任意（逻辑无关） |

### 5. 邮件模板渲染

```python
# email_templates.py
from jinja2 import Environment, FileSystemLoader
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

env = Environment(loader=FileSystemLoader("templates/emails"))

def render_welcome_email(user):
    """渲染欢迎邮件（HTML + 纯文本双版本）"""
    html_template = env.get_template("welcome.html")
    text_template = env.get_template("welcome.txt")

    html_content = html_template.render(user=user, site_url="https://example.com")
    text_content = text_template.render(user=user, site_url="https://example.com")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"欢迎加入，{user.name}！"
    msg["From"] = "noreply@example.com"
    msg["To"] = user.email
    msg.attach(MIMEText(text_content, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    return msg
```
---

> 💡 **深度讲解**：本章介绍了进阶用法、生态工具、技术集成、行业应用和学习资源，为深入学习提供方向。技术的价值不仅在于自身功能，更在于与其他技术的组合使用所产生的协同效应。建议根据项目需求和个人兴趣，选择1-2个拓展方向深入学习，避免浅尝辄止。
>
> **📝 精简总结**：本章介绍了进阶特性、生态工具、技术集成、应用案例和学习资源，为深入学习和技术拓展提供方向。


## 🔗 关联笔记

- [[Flask-轻量服务架构]]
- [[FastAPI-路由与依赖注入]]
- [[Django-ORM与Admin体系]]
- [[HTMX与Python后端配合]]
- [[Tornado-高并发IO模型]]

## 📖 前置知识

- [[Python-语法基础与数据结构]]

## 🏷️ 相关标签

#Python #Jinja2 #前端 #服务端渲染

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]
