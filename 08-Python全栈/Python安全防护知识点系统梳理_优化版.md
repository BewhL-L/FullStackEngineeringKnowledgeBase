---
title: Python 安全防护知识点系统梳理
tags: [Python全栈, Python, 安全, 认证, 授权, 注入防护, CSRF, XSS, 面试]
created: 2026-08-13
updated: 2026-08-13
---

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。


# Python 安全防护知识点系统梳理（优化版）

> **文档说明**：系统梳理 Python Web 应用的安全防护，涵盖认证授权、密码安全、注入防护、XSS/CSRF、文件上传、HTTPS、安全头、常见漏洞防御。

---

## 1. 概述

Web 安全是后端开发的必备知识。OWASP Top 10 是最权威的 Web 安全风险清单：
1. 注入（SQL/命令/代码注入）
2. 认证失效
3. 敏感数据泄露
4. XML 外部实体（XXE）
5. 访问控制失效
6. 安全配置错误
7. 跨站脚本（XSS）
8. 不安全的反序列化
9. 使用含已知漏洞的组件
10. 日志与监控不足

---


---
## 2. 认证与授权

### 2.1 密码安全

> 🔍 **知识点深度解析**
>
> **作用**：密码安全是账户体系的底线，错误的存储方式会导致大规模泄露。
>
> **原理**：绝不明文存储；应使用慢哈希算法（bcrypt/argon2/scrypt）加盐哈希，使暴力破解成本极高；校验时比较哈希而非原文。
>
> **用法要点**：① 禁止明文/可逆加密存储 ② 使用 bcrypt/argon2/scrypt 加盐哈希 ③ 校验比对哈希而非原文 ④ 加盐防止彩虹表攻击 ⑤ 考虑加入登录限流防爆破


```python
# 永远不要明文存储密码！
import hashlib
# 错误：MD5/SHA 不加盐
password_hash = hashlib.md5(password.encode()).hexdigest()

# 正确：用 bcrypt/argon2（自动加盐 + 慢哈希）
import bcrypt
# 注册时
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode(), salt)
# 存储 hashed

# 登录时
if bcrypt.checkpw(password.encode(), stored_hash):
    print("登录成功")

# argon2（推荐，OWASP 首选）
from argon2 import PasswordHasher
ph = PasswordHasher()
hash = ph.hash(password)
ph.verify(hash, password)
```

### 2.2 JWT 认证

> 🔍 **知识点深度解析**
>
> **作用**：JWT 让无状态服务也能安全识别用户身份，广泛用于前后端分离。
>
> **原理**：服务端签名生成 Token（header.payload.signature），客户端携带于 Authorization 头；服务端验签即可信任，无需查库会话。
>
> **用法要点**：① 服务端签名、客户端携带 ② 签名保证不可篡改 ③ 无状态、易水平扩展 ④ 注意过期与刷新机制 ⑤ 密钥泄露即全面失效


```python
import jwt
from datetime import datetime, timedelta

# 生成 token
payload = {
    "user_id": user.id,
    "exp": datetime.utcnow() + timedelta(hours=2),  # 过期时间
    "iat": datetime.utcnow(),
}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# 验证 token
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    raise Exception("Token 已过期")
except jwt.InvalidTokenError:
    raise Exception("Token 无效")
```

### 2.3 OAuth2

- 授权码模式（Authorization Code）：Web 应用首选
- 隐式模式（Implicit）：已不推荐
- 密码模式（Password）：仅可信应用
- 客户端凭证（Client Credentials）：服务间调用

> 🔍 **知识点深度解析**
>
> **作用**：认证授权是安全的第一道防线，密码存储和 Token 管理是核心。
>
> **原理**：密码不能明文存储，也不能用 MD5/SHA 等快速哈希（彩虹表/暴力破解）。bcrypt/argon2 是慢哈希算法，计算成本可调，加盐后每个密码哈希不同，即使密码相同。JWT 是无状态认证方案，Token 包含用户信息（payload）+ 签名（防篡改），服务器不需要存储 Session。JWT 缺点：无法主动失效（除非加黑名单），payload 不能存敏感信息（Base64 不是加密）。OAuth2 是授权框架，不是认证协议，用于第三方应用授权访问用户资源。
>
> **用法要点**：① 密码用 bcrypt/argon2，不要自己实现哈希；② JWT 设置合理过期时间，用 Refresh Token 机制；③ JWT secret 要足够长且保密；④ 面试常考：密码存储、JWT 原理与优缺点、Session vs JWT、OAuth2 流程、CSRF 与 JWT。

---


---
## 3. 注入防护

### 3.1 SQL 注入

> 🔍 **知识点深度解析**
>
> **作用**：SQL 注入可在拼接 SQL 时执行攻击者构造的恶意语句，是最常见高危漏洞之一。
>
> **原理**：成因是把用户输入直接拼进 SQL 字符串；参数化查询/ORM 会把输入当作数据而非代码，从根本上杜绝注入。
>
> **用法要点**：① 成因：拼接用户输入到 SQL ② 用参数化查询/ORM 防注入 ③ 避免字符串格式化拼 SQL ④ 最小权限数据库账户 ⑤ 输入校验作为纵深防御


```python
# 危险：字符串拼接
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)

# 安全：参数化查询
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))

# ORM 自动防注入
User.objects.filter(username=username)  # Django ORM
session.query(User).filter(User.username == username)  # SQLAlchemy
```

### 3.2 命令注入

> 🔍 **知识点深度解析**
>
> **作用**：命令注入在调用系统命令时执行了攻击者插入的额外指令，危害极大。
>
> **原理**：成因是用 shell 拼接用户输入执行 subprocess；应使用列表形式传参、避免 shell=True，并对输入严格白名单。
>
> **用法要点**：① 避免 shell=True 拼接 ② 用列表参数调用 subprocess ③ 输入白名单校验 ④ 最小权限运行进程 ⑤ 不回显原始命令错误


```python
# 危险：os.system 字符串拼接
os.system(f"ping {host}")

# 安全：subprocess 列表参数（不经过 shell）
subprocess.run(["ping", "-c", "1", host], check=True)

# 如需 shell，严格校验输入
import shlex
if not shlex.quote(host) == host:
    raise ValueError("非法输入")
```

### 3.3 代码注入

```python

> 🔍 **知识点深度解析**
>
> **作用**：代码注入通过 eval/exec/pickle 等危险函数执行恶意代码，Python 中需严格避免执行用户可控输入。
>
> **原理**：eval/exec 执行用户输入可直接执行任意代码（eval("__import__('os').system('rm -rf /')")）。pickle/yaml.load 反序列化恶意数据可执行任意代码（__reduce__ 魔术方法）。模板注入（SSTI）：Jinja2 render_template_string(user_input) 可执行 {{ config }} 或 {{ ''.__class__.__mro__ }}。防护：禁用 eval/exec、用 ast.literal_eval 替代 eval、yaml.safe_load、模板用 render_template 而非字符串拼接、沙箱隔离。
>
> **用法要点**：① 禁用 eval/exec 处理用户输入，用 ast.literal_eval 替代  ② pickle/yaml.load 可执行任意代码，用 yaml.safe_load  ③ Jinja2 SSTI：render_template_string 拼接用户输入可 RCE  ④ subprocess 用列表参数不用 shell=True，避免命令注入  ⑤ 面试常考：eval 危险、pickle 反序列化、SSTI、防护措施

# 危险：eval/exec 执行用户输入
eval(user_input)
exec(user_input)

# 安全：避免使用，或用 ast.literal_eval（只解析字面量）
import ast
data = ast.literal_eval(user_input)  # 只允许 dict/list/str/num
```

> 🔍 **知识点深度解析**
>
> **作用**：注入是 OWASP Top 1 漏洞，必须严防。
>
> **原理**：SQL 注入的本质是用户输入被当作 SQL 代码执行。参数化查询将 SQL 语句和参数分开传递给数据库，参数永远被当作数据，不会被解析为代码。ORM 底层也是参数化查询。命令注入是用户输入被拼接到 shell 命令中，`subprocess.run` 用列表参数时不经过 shell 解析，所以安全。`eval`/`exec` 执行任意代码极其危险，几乎所有场景都应避免。`ast.literal_eval` 只解析 Python 字面量（dict/list/str/num/bool/None），不执行代码，相对安全。
>
> **用法要点**：① 永远用参数化查询，不要拼接 SQL；② 用 subprocess 列表参数，不要 `shell=True`；③ 避免 eval/exec，用 ast.literal_eval 替代；④ 面试常考：SQL 注入原理与防护、参数化查询原理、命令注入、eval 风险。

---


---
## 4. XSS 防护

### 4.1 类型

> 🔍 **知识点深度解析**
>
> **作用**：了解 XSS 的类型有助于针对性防护：存储型、反射型、DOM 型。
>
> **原理**：存储型入库后展示给用户；反射型通过 URL 参数即时回显；DOM 型在浏览器端脚本中触发；三者都源于不可信内容被当作代码执行。
>
> **用法要点**：① 存储型：入库后展示 ② 反射型：URL 参数回显 ③ DOM 型：前端脚本触发 ④ 均因未转义不可信内容 ⑤ 危害为窃取 Cookie/劫持会话


- **反射型 XSS**：URL 参数直接输出到页面
- **存储型 XSS**：恶意脚本存入数据库，其他用户查看时执行
- **DOM 型 XSS**：前端 JS 操作 DOM 时引入

### 4.2 防护

> 🔍 **知识点深度解析**
>
> **作用**：XSS 防护核心是让不可信内容永远不被当作可执行代码。
>
> **原理**：输出到 HTML 时自动转义（框架默认开启）、对富文本做白名单净化（bleach）、设置 CSP 限制脚本来源、敏感操作避免依赖 Cookie 自动携带。
>
> **用法要点**：① 输出自动转义 ② 富文本用白名单净化 ③ 设置 Content-Security-Policy ④ HttpOnly Cookie 防 JS 读取 ⑤ 避免 innerHTML 拼接不可信内容


```python
# 模板自动转义（Django/Jinja2 默认开启）
{{ user_content }}  {# 自动转义 < > & " ' #}

# 不要关闭自动转义
{{ user_content|safe }}  {# 危险，除非内容可信 #}

# 后端手动转义
from html import escape
safe_content = escape(user_content)
```

**关键**：永远不要信任用户输入，输出到 HTML 时必须转义。

---


---
## 5. CSRF 防护

### 5.1 原理

> 🔍 **知识点深度解析**
>
> **作用**：理解 CSRF 原理才能正确配置防护；它利用用户已登录状态伪造请求。
>
> **原理**：攻击者诱导已登录用户在第三方页面提交请求，浏览器自动附带 Cookie；若服务端仅依赖 Cookie 鉴权即会误执行。
>
> **用法要点**：① 利用自动携带的 Cookie ② 伪造跨站请求 ③ 针对状态变更操作 ④ 需用户已登录 ⑤ GET 不应做变更操作


攻击者诱导用户在已登录的网站上执行非预期操作（利用用户的 Cookie/Session）。

### 5.2 防护

> 🔍 **知识点深度解析**
>
> **作用**：CSRF 防护通过验证请求来源或携带的随机凭证来阻断伪造。
>
> **原理**：常用 CSRF Token（表单/Header 中随请求提交并由服务端校验）、SameSite Cookie 限制跨站携带、校验 Origin/Referer。
>
> **用法要点**：① CSRF Token 校验 ② SameSite=Strict/Lax Cookie ③ 校验 Origin/Referer ④ 敏感操作要求二次确认 ⑤ 配合框架中间件统一防护


```python
# Django 内置 CSRF 防护
# 表单中添加 {% csrf_token %}
# POST 请求自动验证 CSRF token

# Flask-WTF
from flask_wtf.csrf import CSRFProtect
CSRFProtect(app)

# FastAPI/JWT：JWT 放在 Authorization Header 而非 Cookie，天然防 CSRF
```

**其他措施**：
- SameSite Cookie 属性（`SameSite=Lax/Strict`）
- 验证 Referer/Origin Header
- 关键操作二次确认

---


---
## 6. 文件上传安全

```python
# 1. 校验文件类型（不要只看扩展名）
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# 2. 用 magic number 验证真实类型
import filetype
kind = filetype.guess(uploaded_file.read())
if kind.mime not in ["image/png", "image/jpeg"]:
    raise ValueError("文件类型不允许")

# 3. 重命名文件（防路径遍历和覆盖）
import uuid
filename = f"{uuid.uuid4()}.{ext}"

# 4. 存储到非 Web 根目录，通过接口读取
# 5. 设置文件大小限制
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB
```

---


---
## 7. HTTPS 与安全头

### 7.1 安全响应头

> 🔍 **知识点深度解析**
>
> **作用**：安全响应头是低成本高收益的纵深防御手段，能缓解多种前端攻击。
>
> **原理**：如 Content-Security-Policy 限制资源加载、X-Content-Type-Options 防 MIME 嗅探、X-Frame-Options 防点击劫持、Strict-Transport-Security 强制 HTTPS。
>
> **用法要点**：① CSP 限制脚本/资源来源 ② X-Frame-Options 防点击劫持 ③ HSTS 强制 HTTPS ④ X-Content-Type-Options 防嗅探 ⑤ 可经 Nginx/框架统一设置


```python
# Nginx 配置
add_header X-Frame-Options "SAMEORIGIN" always;           # 防点击劫持
add_header X-Content-Type-Options "nosniff" always;       # 防 MIME 嗅探
add_header X-XSS-Protection "1; mode=block" always;       # XSS 过滤
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;  # 强制HTTPS
add_header Content-Security-Policy "default-src 'self'" always;  # CSP 防XSS
```

### 7.2 CORS 配置

> 🔍 **知识点深度解析**
>
> **作用**：合理的 CORS 配置在开放跨域能力的同时避免过度授权。
>
> **原理**：精确设置 Access-Control-Allow-Origin（避免盲目 * 配合凭证）、限制方法与头、对带凭证请求显式声明来源；错误配置会放大 XSS 影响。
>
> **用法要点**：① 避免 Allow-Origin:* + 凭证 ② 显式声明允许的来源 ③ 限制方法与请求头 ④ 凭证请求需精确匹配 ⑤ 与安全头协同配置


```python
# FastAPI
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],  # 不要用 "*"
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---


---
## 8. 其他安全措施

- **输入校验**：所有用户输入都要校验（类型、长度、格式、范围）
- **敏感数据**：密码/Token 不打日志，传输用 HTTPS，数据库加密存储
- **限流**：防暴力破解、防爬虫（登录接口、API 接口）
- **依赖安全**：定期更新依赖，`pip-audit` 扫描漏洞
- **日志审计**：记录关键操作（登录、修改、删除），但不记录敏感数据
- **配置安全**：生产环境关闭 DEBUG，密钥不硬编码，用环境变量

---

## 8.1 SSRF（服务端请求伪造）

攻击者诱导服务器发起请求，访问内网资源。

```python

> 🔍 **知识点深度解析**
>
> **作用**：SSRF 让服务端请求攻击者指定的 URL，可访问内网服务、云元数据或本地文件，造成内网穿透。
>
> **原理**：应用根据用户输入发起 HTTP 请求（如 URL 预览、Webhook、图片下载），攻击者传入 http://169.254.169.254/latest/meta-data/（云元数据）、http://localhost:6379（内网 Redis）、file:///etc/passwd。防护：URL 白名单（只允许指定域名）、禁止内网 IP（10./172.16-31./192.168./127./169.254.）、禁止 file/gopher 协议、DNS 重绑定防护（解析后校验 IP）、最小权限网络策略。
>
> **用法要点**：① 风险：访问云元数据（窃取密钥）、内网服务、本地文件  ② 白名单限制目标域名，禁止内网 IP 段  ③ 禁用 file://、gopher:// 等非 HTTP 协议  ④ DNS 重绑定：先解析 DNS 再校验 IP，连接前再校验  ⑤ 面试常考：SSRF 原理、云元数据攻击、防护措施

# 危险：用户控制 URL，服务器发起请求
import requests
def fetch_url(user_url):
    return requests.get(user_url).text  # 可能访问 http://169.254.169.254/

# 防护：
# 1. 协议白名单（只允许 http/https）
# 2. 域名解析后校验 IP（禁止内网 IP：10.x、172.16-31.x、192.168.x、127.x、169.254.x）
# 3. 禁止重定向（或重定向后重新校验）
# 4. 使用专用 SSRF 防护库（如 ssrf-protect）
```

---

## 8.2 不安全的反序列化

```python

> 🔍 **知识点深度解析**
>
> **作用**：不安全的反序列化（pickle/marshal/shelve）可导致远程代码执行，是 Python 特有的高危漏洞。
>
> **原理**：pickle.loads 反序列化时调用对象的 __reduce__ 方法，攻击者构造恶意 pickle 数据即可执行任意系统命令。PyYAML 的 yaml.load 同样危险（!!python/object/apply:os.system）。shelve 基于 pickle。JSON 反序列化安全（只解析数据）。防护：永远不要反序列化不可信数据、用 JSON 替代 pickle、必须用 pickle 时用 hmac 签名验证、yaml.safe_load。
>
> **用法要点**：① pickle.loads 不可信数据 = RCE（__reduce__ 执行任意命令）  ② yaml.load 同样危险，必须用 yaml.safe_load  ③ JSON 反序列化安全，跨语言数据交换用 JSON  ④ 必须用 pickle 时用 hmac 签名确保数据未被篡改  ⑤ 面试常考：pickle RCE、__reduce__、安全替代方案

# 危险：pickle 反序列化用户输入（可执行任意代码）
import pickle
data = pickle.loads(user_input)  # 极度危险！

# 危险：PyYAML unsafe_load
import yaml
data = yaml.unsafe_load(user_input)  # 可执行代码

# 安全：yaml.safe_load（只解析数据，不执行）
data = yaml.safe_load(user_input)

# 替代：用 JSON 序列化（安全）
import json
data = json.loads(user_input)
```

---

## 8.3 依赖漏洞扫描

```bash

> 🔍 **知识点深度解析**
>
> **作用**：依赖漏洞扫描检查第三方库的已知 CVE，是供应链安全的基础实践。
>
> **原理**：工具：pip-audit（PyPA 官方，扫描 requirements.txt 已知漏洞）、safety（免费数据库）、Dependabot/Renovate（GitHub 自动 PR 更新）、Snyk（商业，多语言）。CI 中集成 pip-audit 阻断高危漏洞。定期更新依赖（pip install --upgrade），关注 PyPA 安全公告。最小化依赖：不用的库不安装，减少攻击面。
>
> **用法要点**：① pip-audit -r requirements.txt 扫描已知漏洞  ② safety check 另一个免费扫描工具  ③ Dependabot/Renovate 自动提交依赖更新 PR  ④ CI 集成扫描，高危漏洞阻断构建  ⑤ 面试常考：供应链安全、pip-audit、依赖更新策略

# pip-audit：扫描 Python 依赖漏洞
pip install pip-audit
pip-audit                    # 扫描当前环境
pip-audit -r requirements.txt

# safety：商业+开源漏洞数据库
pip install safety
safety check

# CI 集成
# GitHub Actions 中 Dependabot 自动检测依赖漏洞
```

---

## 8.4 速率限制与防暴力破解

```python

> 🔍 **知识点深度解析**
>
> **作用**：速率限制限制单位时间内请求次数，防止暴力破解、撞库和 CC 攻击。
>
> **原理**：slowapi（FastAPI，基于 limits 库）：@limiter.limit("5/minute") 装饰器。Django：django-ratelimit。Flask：Flask-Limiter。策略：固定窗口（简单但有临界问题）、滑动窗口（更平滑）、令牌桶（允许突发）。登录接口额外限制：同 IP 5次/分钟、同账号锁定/验证码、失败计数。Redis 实现分布式限流（INCR + EXPIRE 或令牌桶 Lua 脚本）。
>
> **用法要点**：① slowapi（FastAPI）/django-ratelimit/Flask-Limiter  ② 登录接口：IP+账号双维度限流，失败锁定+验证码  ③ Redis INCR+EXPIRE 实现固定窗口，Lua 脚本保证原子性  ④ 滑动窗口/令牌桶比固定窗口更精确  ⑤ 面试常考：限流算法、登录防爆破、Redis 限流实现

# 登录接口限流（防暴力破解）
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/login")
@limiter.limit("5/minute")  # 每分钟最多5次
async def login(request: Request):
    # 验证密码
    pass

# 账号锁定：连续失败 N 次后锁定账号
# 验证码：登录失败后要求验证码
# IP 封禁：异常 IP 加入黑名单
```

---

## 8.5 目录遍历与路径安全

```python

> 🔍 **知识点深度解析**
>
> **作用**：目录遍历通过 ../ 或绝对路径访问未授权文件，文件操作必须校验和规范化路径。
>
> **原理**：用户传入文件名（如 ?file=../../etc/passwd），服务端直接 open 拼接路径导致读取任意文件。防护：os.path.realpath 规范化路径后校验是否在允许目录内（os.path.commonpath）；用白名单限定可访问文件；Flask send_from_directory 内置安全检查；Django FileResponse 不允许路径穿越；禁止用户直接控制文件路径。
>
> **用法要点**：① 风险：?file=../../../etc/passwd 读取系统文件  ② os.path.realpath 规范化后校验是否在 BASE_DIR 内  ③ send_from_directory / FileResponse 内置路径安全检查  ④ 白名单限定可访问文件，不用用户输入直接拼接路径  ⑤ 面试常考：目录遍历原理、路径规范化、防护方法

# 危险：用户输入拼接到文件路径
filename = request.query_params.get("file")
with open(f"/data/{filename}") as f:  # ../../etc/passwd 可越权
    content = f.read()

# 安全：路径规范化 + 校验是否在允许目录内
import os
base_dir = "/data/"
safe_path = os.path.realpath(os.path.join(base_dir, filename))
if not safe_path.startswith(os.path.realpath(base_dir)):
    raise HTTPException(400, "非法路径")
```

---

## 8.6 JWT 安全细节

| 风险 | 说明 | 防护 |
|------|------|------|
| **算法混淆** | 把 RS256 改成 none 或 HS256 | 显式指定 algorithms，不允许 none |
| **密钥泄露** | HS256 密钥被破解 | 用足够长的密钥，或用 RS256 非对称 |
| **过期时间过长** | Token 被盗用后长期有效 | 短期 Access + 长期 Refresh |
| **无法主动失效** | 登出后 Token 仍有效 | 维护黑名单（Redis）或短过期 |
| **payload 存敏感信息** | Base64 不是加密 | 不存密码/密钥等敏感信息 |

```python

> 🔍 **知识点深度解析**
>
> **作用**：JWT 安全涉及密钥管理、算法选择、Token 存储和撤销机制，配置不当可导致认证绕过。
>
> **原理**：风险：none 算法绕过（服务端未校验算法）、弱密钥（HS256 密钥可暴力破解）、Payload 未加密（Base64 可解码，勿存敏感信息）、Token 无法撤销（JWT 无状态，需黑名单/短有效期）。安全实践：强制 RS256/ES256 非对称算法、强密钥（≥256bit）、短 access token + refresh token、HTTPS 传输、HttpOnly Cookie 存储防 XSS、敏感操作重新认证。
>
> **用法要点**：① 禁用 none 算法，用 RS256/ES256 非对称签名  ② Payload 是 Base64 不是加密，不能存密码/身份证  ③ 短 access token（15min）+ refresh token，黑名单撤销  ④ Token 存 HttpOnly Cookie 防 XSS，不用 localStorage  ⑤ 面试常考：JWT 安全风险、算法选择、撤销机制、存储方式

# 安全的 JWT 配置
jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])  # 显式算法
# 用 RS256：私钥签名，公钥验证，密钥不随服务分发
```

---


---
## 9. 面试高频考点

1. **OWASP Top 10**：常见漏洞清单
2. **SQL 注入**：原理、参数化查询防护
3. **XSS**：三种类型、转义防护、CSP
4. **CSRF**：原理、Token/SameSite 防护
5. **密码存储**：bcrypt/argon2、加盐、慢哈希
6. **JWT**：原理、优缺点、安全细节（算法混淆/过期/失效）
7. **OAuth2**：授权流程、四种模式
8. **文件上传**：类型校验、重命名、大小限制
9. **HTTPS**：TLS 握手、证书、HSTS
10. **安全头**：CSP、X-Frame-Options、CORS
11. **SSRF**：服务端请求伪造、内网 IP 过滤
12. **反序列化漏洞**：pickle/PyYAML 风险、safe_load
13. **依赖漏洞**：pip-audit/safety、CI 集成
14. **目录遍历**：路径规范化、白名单校验
15. **速率限制**：防暴力破解、登录限流、账号锁定

---


---
## 📝 精简总结

- OWASP Top 10：注入、认证失效、XSS、CSRF、SSRF、反序列化是高频
- 认证：密码用 bcrypt/argon2，JWT 无状态认证（显式算法+短过期+Refresh），OAuth2 第三方授权
- 注入防护：参数化查询（SQL）、subprocess列表参数（命令）、避免eval/exec
- XSS：模板自动转义，不要用 `|safe`，CSP 安全头
- CSRF：CSRF Token + SameSite Cookie，JWT 放 Header 天然防
- 文件上传：校验真实类型（magic number）、重命名、大小限制、非根目录存储
- SSRF：协议白名单、内网 IP 过滤、禁止重定向
- 反序列化：禁止 pickle 反序列化用户输入，用 yaml.safe_load/json
- 目录遍历：os.path.realpath 规范化 + 白名单目录校验
- 依赖安全：pip-audit/safety 扫描漏洞，CI 集成 Dependabot
- 速率限制：登录接口限流、账号锁定、验证码、IP 封禁
- HTTPS：强制 HTTPS + HSTS + 安全响应头
- 通用：输入校验、限流、依赖更新、日志审计、关闭DEBUG

---

[[08-Python全栈/MOC-Python全栈|← 返回 Python 全栈 MOC]] | [[Home|🏠 返回首页]]
