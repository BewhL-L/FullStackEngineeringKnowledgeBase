---
title: curl高级用法
tags: [curl, HTTP, API, 调试, 命令行, 计算机网络, REST, 效率工具, 枢纽笔记]
category: 通用工具
created: 2026-08-13
updated: 2026-08-28
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[Linux系统管理与常用命令]]", "[[HTTPS与TLS握手]]"]
aliases: [curl高级用法]
---

# 🌐 curl 高级用法

> **文档说明**：系统讲解命令行网络工具 curl 的完整知识体系，涵盖 HTTP 方法（GET/POST/PUT/DELETE/PATCH）、请求头与响应头、Cookie 与会话管理、认证方式（Basic/Bearer/Digest）、文件上传下载、HTTPS/SSL/TLS、代理设置、超时与重试、并发请求、调试与详细输出、JSON/XML/form 数据处理、REST API 调试、性能测试、常见问题与最佳实践。curl 是开发者和运维人员最常用的网络调试工具。
>
> **适用人群**：开发者、运维工程师、DevOps、API 测试人员、安全研究人员
>
> **前置知识**：[[Linux系统管理与常用命令]] · [[HTTPS与TLS握手]]

---

## 一、概述

### 1.1 什么是 curl

curl（**Client URL**）是一个命令行工具和库（libcurl），用于在网络上传输数据。它支持几乎所有网络协议（HTTP/HTTPS/FTP/SFTP/SCP/Telnet/SMTP 等），是最流行的网络传输工具之一。

**核心特点**：
- ✅ **协议广泛**：支持 HTTP/HTTPS/FTP/SFTP/SCP/SMTP/POP3/IMAP/Telnet/DICT/LDAP 等 20+ 协议
- ✅ **跨平台**：Linux/macOS/Windows 都有，几乎所有系统预装
- ✅ **功能强大**：支持认证、Cookie、代理、SSL、断点续传、并发等
- ✅ **脚本友好**：非交互式，适合 Shell 脚本和自动化
- ✅ **库支持**：libcurl 被几乎所有编程语言绑定（PHP/Python/Go/Java 等）

### 1.2 解决的问题

| 问题 | 说明 |
|------|------|
| **API 调试** | 快速测试 REST API，无需打开 Postman 等 GUI 工具 |
| **网络排查** | 测试网络连通性、DNS 解析、SSL 证书、代理设置 |
| **文件传输** | 下载/上传文件，支持 FTP/SFTP/HTTP |
| **自动化脚本** | 在 Shell 脚本中调用 API、下载资源、健康检查 |
| **性能测试** | 简单的接口响应时间测试、并发请求测试 |
| **安全测试** | 测试认证、授权、CORS、SSL 配置等 |

### 1.3 curl vs 其他工具

| 工具 | 特点 | 优势 | 劣势 |
|------|------|------|------|
| **curl** | 命令行，全能网络工具 | 跨平台、功能全、脚本友好 | 纯命令行，复杂请求参数多 |
| **wget** | 命令行下载工具 | 下载功能强（递归、镜像） | 只支持 HTTP/FTP，上传弱 |
| **HTTPie** | 命令行，人性化 HTTP | 语法简洁、输出美观、JSON 友好 | 需安装，功能不如 curl 全 |
| **Postman** | GUI API 测试 | 界面友好、集合管理、协作 | 重量级，不适合脚本 |
| **Insomnia** | GUI API 测试 | 界面简洁、支持 GraphQL | 重量级，不适合脚本 |

---

## 二、底层原理

### 2.1 curl 工作流程

```mermaid
flowchart TB
    A[解析命令行参数] --> B[URL 解析]
    B --> C[DNS 解析]
    C --> D[建立 TCP 连接]
    D --> E{HTTPS?}
    E -->|是| F[TLS 握手]
    F --> G[发送请求]
    E -->|否| G
    G --> H[接收响应头]
    H --> I[接收响应体]
    I --> J{重定向?}
    J -->|是且-L| B
    J -->|否| K[输出结果]
    K --> L[关闭连接]

    style G fill:#667eea,color:#fff
    style K fill:#43e97b,color:#333
```

### 2.2 退出码

curl 的退出码（`$?`）对脚本自动化非常重要：

| 退出码 | 含义 |
|--------|------|
| 0 | 成功 |
| 1 | 不支持的协议 |
| 2 | 初始化失败 |
| 3 | URL 格式错误 |
| 5 | 无法解析代理 |
| 6 | 无法解析主机（DNS 失败） |
| 7 | 无法连接到主机 |
| 8 | 服务器返回异常响应 |
| 22 | HTTP 错误（`-f` 选项时，4xx/5xx 返回 22） |
| 23 | 写入数据失败 |
| 26 | 读取文件错误 |
| 27 | 内存分配失败 |
| 28 | 连接超时 |
| 35 | SSL/TLS 握手错误 |
| 51 | SSL 证书错误（证书 CN 不匹配） |
| 52 | 服务器无响应 |
| 55 | 发送数据失败 |
| 56 | 接收数据失败 |
| 60 | SSL 证书验证失败（CA 不被信任） |

```bash
# 在脚本中检查退出码
curl -s https://api.example.com/health
if [ $? -eq 0 ]; then
  echo "健康检查通过"
else
  echo "健康检查失败"
  exit 1
fi
```

---

## 三、实操示例

### 3.1 基础用法

```bash
# ===== 最基础：GET 请求 =====
curl https://api.example.com/users
curl http://example.com            # 不写协议默认 HTTP
curl example.com                    # 甚至可以省略 http://

# ===== 保存响应到文件 =====
curl -o output.html https://example.com        # 保存为指定文件名
curl -O https://example.com/file.zip           # 保存为远程文件名
curl -J -O https://example.com/download        # 用 Content-Disposition 中的文件名

# ===== 静默模式（不显示进度条）=====
curl -s https://api.example.com/users          # 静默，只输出响应体
curl -sS https://api.example.com/users         # 静默但显示错误
curl -s -o /dev/null https://example.com       # 丢弃响应体（只看状态码）

# ===== 显示详细信息 =====
curl -v https://example.com                     # 详细输出（请求头+响应头+SSL信息）
curl -vv https://example.com                    # 更详细
curl --trace output.txt https://example.com     # 完整跟踪（所有数据）
curl --trace-ascii output.txt https://example.com  # ASCII 跟踪

# ===== 只看响应头 =====
curl -I https://example.com                     # HEAD 请求，只看响应头
curl -i https://example.com                     # 显示响应头+响应体
curl -D headers.txt https://example.com         # 响应头保存到文件

# ===== 跟随重定向 =====
curl -L https://example.com/redirect            # 自动跟随 3xx 重定向
curl -L --max-redirs 5 https://example.com      # 最多跟随 5 次重定向
```

### 3.2 HTTP 方法

```bash
# ===== GET（默认）=====
curl https://api.example.com/users
curl -X GET https://api.example.com/users       # 显式指定

# ===== POST =====
curl -X POST https://api.example.com/users

# ===== PUT =====
curl -X PUT https://api.example.com/users/1

# ===== DELETE =====
curl -X DELETE https://api.example.com/users/1

# ===== PATCH =====
curl -X PATCH https://api.example.com/users/1

# ===== HEAD =====
curl -I https://api.example.com/users            # 或 -X HEAD

# ===== OPTIONS（预检请求）=====
curl -X OPTIONS https://api.example.com/users -i
```

### 3.3 请求头

```bash
# ===== 设置请求头 =====
curl -H "Content-Type: application/json" https://api.example.com/users
curl -H "Authorization: Bearer token123" https://api.example.com/users
curl -H "Accept: application/json" -H "X-API-Key: abc123" https://api.example.com

# ===== 多个请求头 =====
curl \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token123" \
  -H "X-Request-ID: $(uuidgen)" \
  https://api.example.com/users

# ===== 空请求头（删除默认头）=====
curl -H "User-Agent:" https://example.com       # 移除 User-Agent
curl -H "Accept:" https://example.com            # 移除 Accept

# ===== 自定义 User-Agent =====
curl -A "MyApp/1.0" https://example.com          # 或 -H "User-Agent: MyApp/1.0"
curl -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..." https://example.com

# ===== Referer =====
curl -e "https://google.com" https://example.com  # 或 -H "Referer: https://google.com"
```

### 3.4 发送数据

```bash
# ===== 1. 表单数据（application/x-www-form-urlencoded）=====
curl -X POST https://api.example.com/login \
  -d "username=admin&password=123456"

# 多个 -d 会自动用 & 连接
curl -X POST https://api.example.com/login \
  -d "username=admin" \
  -d "password=123456"

# ===== 2. JSON 数据 =====
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name":"张三","email":"zhang@example.com","age":25}'

# 从文件读取 JSON
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d @user.json

# ===== 3. 多行 JSON（用引号包裹）=====
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "email": "zhang@example.com",
    "age": 25,
    "address": {
      "city": "北京",
      "street": "长安街"
    }
  }'

# ===== 4. multipart/form-data（文件上传）=====
curl -X POST https://api.example.com/upload \
  -F "file=@/path/to/file.jpg" \
  -F "description=这是一张图片"

# 多个文件
curl -X POST https://api.example.com/upload \
  -F "files=@/path/to/file1.jpg" \
  -F "files=@/path/to/file2.jpg"

# 指定文件类型和文件名
curl -X POST https://api.example.com/upload \
  -F "file=@/path/to/file.jpg;type=image/jpeg;filename=photo.jpg"

# ===== 5. URL 查询参数 =====
curl "https://api.example.com/users?page=1&size=10&sort=name"
# 注意：URL 中有 & 时必须用引号包裹，否则 Shell 会把 & 当作后台运行

# URL 编码（特殊字符）
curl -G https://api.example.com/search \
  --data-urlencode "q=hello world" \
  --data-urlencode "lang=zh-CN"
# -G 会把 -d 的数据作为查询参数附加到 URL

# ===== 6. XML 数据 =====
curl -X POST https://api.example.com/soap \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?><request><name>张三</name></request>'

# ===== 7. 原始数据（从 stdin）=====
echo '{"name":"test"}' | curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d @-
```

### 3.5 Cookie 与会话

```bash
# ===== 发送 Cookie =====
curl -b "sessionid=abc123; token=xyz789" https://example.com/dashboard

# 从文件读取 Cookie
curl -b cookies.txt https://example.com/dashboard

# ===== 保存 Cookie =====
curl -c cookies.txt https://example.com/login
# -c 会把服务器返回的 Set-Cookie 保存到文件

# ===== 完整会话（登录 + 访问）=====
# 1. 登录，保存 Cookie
curl -c cookies.txt -X POST https://example.com/login \
  -d "username=admin&password=123456"

# 2. 用保存的 Cookie 访问需要登录的页面
curl -b cookies.txt https://example.com/dashboard

# 3. 同时读取和保存 Cookie（会话保持）
curl -b cookies.txt -c cookies.txt https://example.com/profile

# ===== Cookie Jar 文件格式 =====
# Netscape Cookie 格式（以 #HttpOnly_ 开头的是 HttpOnly Cookie）
# .example.com    TRUE    /    FALSE    1735689600    sessionid    abc123
# 域名            是否所有子域  路径  是否安全  过期时间        名称         值
```

### 3.6 认证

```bash
# ===== 1. Basic Auth =====
curl -u username:password https://api.example.com/users
curl -u username https://api.example.com/users   # 只输入用户名，会提示输入密码

# 手动构造 Basic Auth 头
# Base64(username:password) = Base64("admin:123456") = YWRtaW46MTIzNDU2
curl -H "Authorization: Basic YWRtaW46MTIzNDU2" https://api.example.com/users

# ===== 2. Bearer Token（JWT/OAuth2）=====
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." https://api.example.com/users

# ===== 3. Digest Auth =====
curl --digest -u username:password https://api.example.com/users

# ===== 4. API Key =====
# 方式1：请求头
curl -H "X-API-Key: abc123def456" https://api.example.com/users
# 方式2：查询参数
curl "https://api.example.com/users?api_key=abc123def456"

# ===== 5. OAuth2 客户端凭证模式 =====
# 获取 Token
TOKEN=$(curl -s -X POST https://auth.example.com/oauth/token \
  -u "client_id:client_secret" \
  -d "grant_type=client_credentials" | jq -r .access_token)

# 使用 Token
curl -H "Authorization: Bearer $TOKEN" https://api.example.com/users

# ===== 6. SSL 客户端证书认证 =====
curl --cert client.crt --key client.key https://api.example.com/users
curl --cert client.p12:password https://api.example.com/users  # PKCS#12 格式
```

### 3.7 HTTPS / SSL / TLS

```bash
# ===== 跳过证书验证（不安全，仅用于测试）=====
curl -k https://self-signed.example.com          # 或 --insecure
curl --insecure https://self-signed.example.com

# ===== 指定 CA 证书 =====
curl --cacert /path/to/ca.crt https://internal.example.com

# ===== 指定客户端证书 =====
curl --cert /path/to/client.crt --key /path/to/client.key https://example.com

# ===== 查看 SSL 证书信息 =====
curl -v https://example.com 2>&1 | grep -E "subject:|issuer:|SSL connection|expire date"

# 用 openssl 查看证书（更详细）
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null | openssl x509 -noout -text

# ===== 指定 TLS 版本 =====
curl --tlsv1.2 https://example.com               # 强制 TLS 1.2
curl --tlsv1.3 https://example.com               # 强制 TLS 1.3
curl --tls-max 1.2 https://example.com           # 最大 TLS 1.2

# ===== 密码套件 =====
curl --ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384' https://example.com

# ===== 测试 SSL 配置（用 nmap 更全面）=====
curl -v --tlsv1.0 https://example.com 2>&1 | grep "SSL connection"
```

### 3.8 代理

```bash
# ===== HTTP 代理 =====
curl -x http://proxy.example.com:8080 https://example.com
curl --proxy http://proxy.example.com:8080 https://example.com

# ===== SOCKS 代理 =====
curl --socks5 socks5://proxy.example.com:1080 https://example.com
curl --socks5-hostname socks5://proxy.example.com:1080 https://example.com  # DNS 也走代理

# ===== 带认证的代理 =====
curl -x http://user:password@proxy.example.com:8080 https://example.com
curl -x http://proxy.example.com:8080 -U user:password https://example.com

# ===== 环境变量代理 =====
export http_proxy=http://proxy.example.com:8080
export https_proxy=http://proxy.example.com:8080
export no_proxy=localhost,127.0.0.1,.internal.com
curl https://example.com   # 自动使用代理

# ===== 不使用代理 =====
curl --noproxy '*' https://internal.example.com
```

### 3.9 超时与重试

```bash
# ===== 超时设置 =====
curl --connect-timeout 5 https://example.com     # 连接超时 5 秒
curl --max-time 30 https://example.com            # 总超时 30 秒（连接+传输）
curl -m 30 https://example.com                     # 同 --max-time

# ===== 重试 =====
curl --retry 3 https://api.example.com/users      # 失败重试 3 次
curl --retry 3 --retry-delay 2 https://api.example.com  # 每次重试间隔 2 秒
curl --retry 3 --retry-max-time 30 https://api.example.com  # 重试总时间不超过 30 秒

# 重试的条件（默认只重试连接错误和 5xx）
curl --retry 3 --retry-connrefused https://api.example.com  # 连接被拒绝也重试

# ===== 限速 =====
curl --limit-rate 100K https://example.com/file.zip   # 限速 100 KB/s
curl --limit-rate 1M https://example.com/file.zip      # 限速 1 MB/s
```

### 3.10 文件下载

```bash
# ===== 基础下载 =====
curl -O https://example.com/file.zip                 # 保存为原文件名
curl -o myfile.zip https://example.com/file.zip      # 保存为指定文件名

# ===== 断点续传 =====
curl -C - -O https://example.com/large-file.zip      # -C - 自动检测续传位置
curl -C 1024 -O https://example.com/large-file.zip   # 从 1024 字节处续传

# ===== 并行下载（多个文件）=====
curl -O https://example.com/file1.zip -O https://example.com/file2.zip

# ===== 下载进度条 =====
curl -# -O https://example.com/large-file.zip        # 用 # 显示进度（默认是统计信息）
curl -s -O https://example.com/file.zip               # 静默下载（无进度）

# ===== 检查文件是否更新（条件请求）=====
curl -z file.zip -O https://example.com/file.zip      # 只在远程文件更新时下载
curl -R -O https://example.com/file.zip                # 保留远程文件的修改时间

# ===== FTP 下载 =====
curl -u user:password ftp://example.com/file.zip -O
curl ftp://user:password@example.com/file.zip -O
```

### 3.11 调试与详细输出

```bash
# ===== 查看完整请求和响应 =====
curl -v https://example.com
# 输出包含：
# *   Trying 93.184.216.34:443...
# * Connected to example.com (93.184.216.34) port 443
# * SSL connection using TLSv1.3 / ...
# > GET / HTTP/1.1
# > Host: example.com
# > User-Agent: curl/8.0.0
# > Accept: */*
# >
# < HTTP/1.1 200 OK
# < Content-Type: text/html; charset=UTF-8
# < Content-Length: 1256
# <
# <!doctype html>...

# ===== 只看请求头 =====
curl -v -s -o /dev/null https://example.com 2>&1 | grep "^>"

# ===== 只看响应头 =====
curl -v -s -o /dev/null https://example.com 2>&1 | grep "^<"

# ===== 格式化输出（用 write-out）=====
# 显示 HTTP 状态码
curl -s -o /dev/null -w "%{http_code}\n" https://example.com

# 显示详细统计
curl -s -o /dev/null -w "
URL: %{url_effective}
HTTP 状态码: %{http_code}
DNS 解析时间: %{time_namelookup}s
TCP 连接时间: %{time_connect}s
TLS 握手时间: %{time_appconnect}s
首字节时间(TTFB): %{time_starttransfer}s
总时间: %{time_total}s
下载大小: %{size_download} bytes
下载速度: %{speed_download} bytes/s
重定向次数: %{num_redirects}
" https://example.com

# 常用变量：
# %{http_code}         HTTP 状态码
# %{time_total}        总时间（秒）
# %{time_namelookup}   DNS 解析时间
# %{time_connect}      TCP 连接时间
# %{time_appconnect}   TLS/SSL 握手时间
# %{time_starttransfer} 首字节时间（TTFB）
# %{size_download}     下载大小
# %{speed_download}    下载速度
# %{url_effective}     最终请求的 URL
# %{num_redirects}     重定向次数
# %{content_type}      Content-Type
```

### 3.12 REST API 调试实战

```bash
# ===== 用户 CRUD 示例 =====

# 1. 获取所有用户
curl -s https://api.example.com/users | jq .

# 2. 获取单个用户
curl -s https://api.example.com/users/1 | jq .

# 3. 创建用户
curl -s -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"张三","email":"zhang@example.com"}' | jq .

# 4. 更新用户
curl -s -X PUT https://api.example.com/users/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"张三三","email":"zhangsan@example.com"}' | jq .

# 5. 部分更新
curl -s -X PATCH https://api.example.com/users/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"email":"new@example.com"}' | jq .

# 6. 删除用户
curl -s -X DELETE https://api.example.com/users/1 \
  -H "Authorization: Bearer $TOKEN" -w "\n状态码: %{http_code}\n"

# ===== 分页查询 =====
curl -s "https://api.example.com/users?page=1&size=20&sort=created_at,desc" | jq .

# ===== 过滤搜索 =====
curl -s -G https://api.example.com/users \
  --data-urlencode "name=张" \
  --data-urlencode "status=active" | jq .

# ===== 上传头像 =====
curl -s -X POST https://api.example.com/users/1/avatar \
  -H "Authorization: Bearer $TOKEN" \
  -F "avatar=@/path/to/avatar.jpg;type=image/jpeg" | jq .

# ===== 健康检查 =====
curl -s -f https://api.example.com/health && echo "服务正常" || echo "服务异常"
```

### 3.13 并发与性能测试

```bash
# ===== 简单并发（xargs）=====
# 10 个并发请求
seq 1 10 | xargs -P 10 -I {} curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" https://api.example.com/users

# ===== 循环测试 =====
for i in {1..100}; do
  curl -s -o /dev/null -w "%{http_code} %{time_total}\n" https://api.example.com/users
done | awk '{sum+=$2; count++} END {print "平均响应时间:", sum/count, "s"}'

# ===== 用 ab（Apache Bench）做压力测试 =====
ab -n 1000 -c 100 https://api.example.com/users
# -n 总请求数，-c 并发数

# ===== 用 hey 做压力测试（Go 编写，更现代）=====
hey -n 1000 -c 100 -m GET https://api.example.com/users
```

### 3.14 .curlrc 配置文件

```bash
# ~/.curlrc — curl 默认配置文件
# 每行一个选项，curl 启动时自动加载

# 默认 User-Agent
user-agent = "Mozilla/5.0 (compatible; MyApp/1.0)"

# 默认请求头
header = "Accept: application/json"

# 静默模式（不显示进度条）
silent = true
show-error = true

# 跟随重定向
location = true

# 连接超时
connect-timeout = 10
max-time = 60

# 重试
retry = 2
retry-delay = 1

# 代理（如果需要）
# proxy = http://proxy.example.com:8080

# 证书（如果需要）
# cacert = /path/to/ca.crt
```

---

## 四、常见问题与排查

| 问题现象 | 可能原因 | 解决方案 |
|---------|---------|---------|
| **URL 中有 & 被截断** | Shell 把 & 当作后台运行符 | 用引号包裹 URL：`curl "https://example.com?a=1&b=2"` |
| **中文/特殊字符乱码** | URL 未编码 | 用 `--data-urlencode` 或 `jq -sRr @uri` 编码 |
| **POST 数据被截断** | 数据中有引号未转义 | 用单引号包裹 JSON，或用 `@file` 从文件读取 |
| **证书验证失败** | 自签名证书；CA 不被信任 | 测试用 `-k` 跳过；生产用 `--cacert` 指定 CA |
| **连接超时** | 网络不通；防火墙；服务未启动 | `ping`/`telnet` 测试；检查防火墙；检查服务状态 |
| **DNS 解析失败** | DNS 配置错误；域名不存在 | `nslookup`/`dig` 测试；检查 `/etc/resolv.conf`；用 `--resolve` 指定 IP |
| **403 Forbidden** | 权限不足；缺少认证；IP 被封 | 检查 Token/认证头；检查权限；检查 IP 白名单 |
| **404 Not Found** | URL 错误；资源不存在 | 检查 URL 路径；检查 API 文档；用 `-v` 看实际请求 URL |
| **500 Internal Server Error** | 服务端错误 | 查看服务端日志；用 `-v` 看请求是否正确；联系后端 |
| **响应体中文乱码** | 编码不匹配；终端编码问题 | 设置 `LANG=zh_CN.UTF-8`；用 `iconv` 转换；检查 Content-Type charset |
| **Cookie 不生效** | Cookie 域不匹配；路径不匹配；HttpOnly | 用 `-b cookies.txt -c cookies.txt` 保持会话；检查 Cookie 属性 |
| **大文件下载中断** | 网络不稳定；服务器限制 | 用 `-C -` 断点续传；用 `--retry` 重试；用 `wget` 替代 |
| **curl 太慢** | DNS 慢；TLS 握手慢；网络延迟 | 用 `-w` 分析各阶段耗时；用 `--resolve` 跳过 DNS；HTTP/2 复用连接 |
| **Windows 下引号问题** | PowerShell/CMD 引号处理不同 | PowerShell 用 `curl.exe`（避免调用 Invoke-WebRequest 别名）；用单引号 |
| **JSON 解析错误** | JSON 格式不对；引号转义问题 | 用 `jq .` 验证 JSON；用 `@file` 从文件读取避免转义 |
| **重定向不跟随** | 未加 `-L` | 加 `-L` 自动跟随 3xx 重定向 |
| **HTTP/2 不支持** | curl 版本旧；服务器不支持 | 升级 curl；用 `--http1.1` 强制 HTTP/1.1 |

---

## 五、进阶与最佳实践

### 5.1 效率提升技巧

```bash
curl 效率提升技巧：

✅ 用 jq 处理 JSON 响应：curl ... | jq .
✅ 用 -w 格式化输出统计信息，不要用 -v 手动找
✅ 用 -sS 静默但显示错误（脚本中必用）
✅ 用 -f 在 HTTP 错误时返回非零退出码（脚本中判断）
✅ 用 -b/-c 保持 Cookie 会话（登录后操作）
✅ 用 --data-urlencode 自动编码查询参数
✅ 用 @file 从文件读取数据，避免 Shell 转义问题
✅ 用 ~/.curlrc 设置默认选项（User-Agent/超时/重试）
✅ 用 -C - 断点续传大文件
✅ 用 -I 快速检查响应头（不下载 body）
✅ 用 --resolve 测试特定 IP 的服务（DNS 未配置时）
✅ 用 -K config.txt 从配置文件读取参数（复杂请求）
✅ 用 --limit-rate 限速下载（避免占满带宽）
✅ 用 -z 条件下载（只在文件更新时下载）
```

### 5.2 脚本中使用 curl 的最佳实践

```bash
#!/bin/bash
# curl 在脚本中的最佳实践

# ===== 1. 基础设置 =====
set -euo pipefail  # 严格模式：错误即退出、未定义变量报错、管道错误传播

API_BASE="https://api.example.com"
TOKEN="${API_TOKEN:?环境变量 API_TOKEN 未设置}"  # 必需变量检查

# ===== 2. 通用 curl 函数 =====
api_request() {
  local method="$1"
  local path="$2"
  local data="${3:-}"
  
  local args=(
    -sS                    # 静默但显示错误
    -f                     # HTTP 错误返回非零退出码
    -X "$method"
    -H "Authorization: Bearer $TOKEN"
    -H "Content-Type: application/json"
    -H "X-Request-ID: $(uuidgen)"
    --connect-timeout 10
    --max-time 30
    --retry 3
    --retry-delay 2
  )
  
  if [ -n "$data" ]; then
    args+=(-d "$data")
  fi
  
  curl "${args[@]}" "$API_BASE$path"
}

# ===== 3. 使用函数 =====
get_user() {
  local user_id="$1"
  api_request "GET" "/users/$user_id"
}

create_user() {
  local name="$1"
  local email="$2"
  local json=$(jq -n --arg name "$name" --arg email "$email" \
    '{name: $name, email: $email}')  # 用 jq 构造 JSON，避免转义
  api_request "POST" "/users" "$json"
}

# ===== 4. 错误处理 =====
if ! response=$(get_user 1); then
  echo "获取用户失败" >&2
  exit 1
fi

# 用 jq 提取字段
user_name=$(echo "$response" | jq -r '.name')
echo "用户名: $user_name"

# ===== 5. 并行请求（后台进程）=====
# 同时获取多个用户
for id in 1 2 3 4 5; do
  get_user "$id" > "user_$id.json" &
done
wait  # 等待所有后台进程完成
echo "所有用户获取完成"
```

### 5.3 安全最佳实践

| 场景 | 建议 |
|------|------|
| **密码/Token** | 不要在命令行中明文写密码（会出现在 `ps` 和历史记录中）；用环境变量或 `-u user`（提示输入） |
| **证书验证** | 生产环境不要用 `-k` 跳过证书验证；用 `--cacert` 指定可信 CA |
| **敏感数据** | 敏感请求体用 `@file` 从文件读取，文件权限设为 600 |
| **历史记录** | 包含敏感信息的 curl 命令，用 ` HISTCONTROL=ignorespace`（空格开头不记录）或执行后 `history -d` |
| **代理** | 不要在公共网络用 HTTP 代理传输敏感数据；用 HTTPS 代理或 SOCKS5 |
| **重定向** | `-L` 跟随重定向时注意凭证泄露（curl 默认不会把 Authorization 头发送到不同域） |
| **SSL 版本** | 用 `--tlsv1.2` 或更高，禁用 SSLv3/TLS1.0/1.1 |
| **脚本** | 脚本中的 Token 用环境变量注入，不要硬编码；脚本文件权限 700 |

### 5.4 与其他工具组合

| 组合 | 用途 | 示例 |
|------|------|------|
| **curl + jq** | JSON 解析和处理 | `curl ... \| jq '.data[].name'` |
| **curl + grep** | 文本搜索 | `curl -s ... \| grep "keyword"` |
| **curl + xargs** | 批量/并发请求 | `seq 1 10 \| xargs -P 5 -I {} curl ...` |
| **curl + awk** | 统计分析 | `curl -w ... \| awk '{sum+=$1} END {print sum/N}'` |
| **curl + tee** | 同时显示和保存 | `curl ... \| tee output.json` |
| **curl + watch** | 定时监控 | `watch -n 5 'curl -s https://api/health \| jq .'` |
| **curl + ab/hey** | 压力测试 | `ab -n 1000 -c 100 https://api/` |
| **curl + openssl** | SSL 证书检查 | `echo \| openssl s_client -connect host:443` |
| **curl + ssh** | 通过 SSH 隧道 | `ssh -L 8080:internal:80 server` 然后 `curl localhost:8080` |

---

## 六、关联笔记

### 网络与安全
- [[HTTPS与TLS握手]] · [[TCPIP协议栈详解]] · [[DNS与CDN架构]]
- [[网络抓包与调试]] · [[WebSocket与SSE原理]]

### 通用工具
- [[Linux系统管理与常用命令]] · [[Shell脚本编程]] · [[tmux-终端复用]]
- [[Zsh与OhMyZsh]] · [[fzf-模糊搜索神器]]

### API 与开发
- [[RESTfulAPI设计原则]] · [[API版本管理策略]] · [[Apifox-接口管理平台]]

### 导航
- [[MOC-通用工具]] · [[MOC-终端与命令行]] · [[MOC-综合导航]] · [[Home]]

> 🔍 **知识点深度解析**
>
> **作用**：curl 解决的是「命令行下网络数据传输和 API 调试」问题，支持几乎所有网络协议，是开发者和运维人员最常用的网络工具，无需 GUI 即可完成 API 测试、文件下载、网络排查等任务。
>
> **底层原理**：curl 基于 libcurl 库，工作流程：解析 URL → DNS 解析 → 建立 TCP 连接 →（HTTPS 时）TLS 握手 → 发送 HTTP 请求 → 接收响应头 → 接收响应体 →（重定向时重复）→ 输出结果。curl 支持多种认证（Basic/Bearer/Digest/SSL 客户端证书）、Cookie 管理（Cookie Jar）、代理（HTTP/SOCKS4/SOCKS5）、断点续传（Range 请求）、并发（多 URL 或 xargs）。退出码非零表示错误（28=超时、60=证书验证失败、22=HTTP 错误）。
>
> **用法要点**：① 基础：`curl URL` GET，`-X POST` 指定方法，`-d` 发送数据，`-H` 设置头 ② JSON：`-H "Content-Type: application/json" -d '{"key":"value"}'` ③ 认证：`-u user:pass`（Basic），`-H "Authorization: Bearer token"`（JWT） ④ Cookie：`-c` 保存，`-b` 读取，`-b -c` 保持会话 ⑤ 文件：`-O` 保存原名，`-o` 指定名，`-C -` 断点续传，`-F` 上传 ⑥ HTTPS：`-k` 跳过验证（测试），`--cacert` 指定 CA ⑦ 调试：`-v` 详细，`-I` 只看头，`-w "%{http_code} %{time_total}"` 统计 ⑧ 脚本：`-sS -f` 静默+错误退出码，用 jq 解析 JSON，用函数封装 ⑨ 安全：密码用环境变量，不用 `-k` 生产，敏感数据用 `@file` ⑩ 效率：`~/.curlrc` 默认配置，`--data-urlencode` 自动编码，`-L` 跟随重定向。

> 💡 **深度讲解**：curl 最强大的地方在于「通用性」——它不是只做 HTTP，而是支持 20+ 种协议，从 HTTP/FTP 到 SMTP/POP3/LDAP，几乎所有网络传输任务都能搞定。但日常 99% 的使用是 HTTP。curl 的另一个优势是「脚本友好」——它是非交互式的，退出码明确，输出可管道处理，非常适合 Shell 脚本和 CI/CD 流水线。最容易踩的坑是「Shell 引号和转义」——URL 中的 `&` 会被 Shell 当作后台运行符，JSON 中的双引号需要转义，解决方案是用引号包裹 URL、用单引号包裹 JSON、或用 `@file` 从文件读取数据。另一个常见坑是「证书验证」——内网服务常用自签名证书，curl 默认会验证失败（退出码 60），测试时用 `-k` 跳过，但生产环境一定要用 `--cacert` 指定可信 CA，不能图省事用 `-k`。实际工作中，建议把常用的 curl 命令封装成 Shell 函数或脚本，配合 jq 处理 JSON 响应，能极大提升 API 调试效率。

> 📝 **精简总结**：curl = 命令行网络传输工具，支持 20+ 协议，最常用 HTTP。核心参数：`-X` 方法、`-d` 数据、`-H` 头、`-u` 认证、`-b/-c` Cookie、`-O/-o` 下载、`-F` 上传、`-k` 跳过证书、`-v` 调试、`-w` 统计、`-L` 重定向、`-sS` 静默。脚本中用 `-sS -f` + jq，安全用环境变量+CA证书，效率用 .curlrc+函数封装。

> **学习路径建议**：先学习 [[Linux系统管理与常用命令]] 掌握命令行基础 → 学习 [[HTTPS与TLS握手]] 理解 HTTP/HTTPS 原理 → 学习本文档掌握 curl 用法 → 学习 [[Shell脚本编程]] 掌握脚本自动化 → 学习 [[RESTfulAPI设计原则]] 理解 API 设计 → 在日常开发和运维中持续使用 curl 形成肌肉记忆。

---

> **curl 的本质是「命令行里的瑞士军刀」——一把工具搞定所有网络传输。它不华丽，但无处不在；它不简单，但核心用法 10 分钟就能上手。掌握 curl，你就拥有了在任何终端里调试任何网络服务的能力。**

---

## 🔗 关联笔记

- [[MOC-通用工具]] — 返回本分类知识地图，查看更多相关文档

## 📖 前置知识

- [[Linux系统管理与常用命令]]
- [[HTTPS与TLS握手]]

## 🏷️ 相关标签

`#curl` `#HTTP` `#API` `#调试` `#命令行` `#计算机网络`

[[Home|🏠 返回首页]] · [[MOC-通用工具|📚 返回分类]]
