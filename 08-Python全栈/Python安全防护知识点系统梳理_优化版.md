---
title: Python 安全防护知识点系统梳理
tags: [Python全栈, Python, 安全, 认证, 授权, 注入防护, CSRF, XSS, 面试]
created: 2026-08-13
updated: 2026-08-13
---

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

## 2. 认证与授权

### 2.1 密码安全

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

## 3. 注入防护

### 3.1 SQL 注入

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

## 4. XSS 防护

### 4.1 类型

- **反射型 XSS**：URL 参数直接输出到页面
- **存储型 XSS**：恶意脚本存入数据库，其他用户查看时执行
- **DOM 型 XSS**：前端 JS 操作 DOM 时引入

### 4.2 防护

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

## 5. CSRF 防护

### 5.1 原理

攻击者诱导用户在已登录的网站上执行非预期操作（利用用户的 Cookie/Session）。

### 5.2 防护

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

## 7. HTTPS 与安全头

### 7.1 安全响应头

```python
# Nginx 配置
add_header X-Frame-Options "SAMEORIGIN" always;           # 防点击劫持
add_header X-Content-Type-Options "nosniff" always;       # 防 MIME 嗅探
add_header X-XSS-Protection "1; mode=block" always;       # XSS 过滤
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;  # 强制HTTPS
add_header Content-Security-Policy "default-src 'self'" always;  # CSP 防XSS
```

### 7.2 CORS 配置

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
# 安全的 JWT 配置
jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])  # 显式算法
# 用 RS256：私钥签名，公钥验证，密钥不随服务分发
```

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
