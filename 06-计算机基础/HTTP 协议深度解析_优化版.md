---
title: HTTP 协议深度解析
tags: [计算机基础, HTTP, 网络, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# HTTP 协议深度解析（优化版）

> **文档说明**：系统梳理 HTTP 协议核心知识，涵盖 HTTP/1.1、HTTP/2、HTTP/3、请求方法、状态码、Header、HTTPS、缓存、跨域等面试高频考点。

---

## 1. 概述

HTTP（HyperText Transfer Protocol，超文本传输协议）是 Web 的基础协议，定义了客户端和服务器之间的通信格式。基于 TCP/IP，默认端口 80（HTTPS 443）。

**版本演进**：

| 版本 | 年份 | 核心特性 |
|------|------|----------|
| HTTP/1.0 | 1996 | 基本请求响应，短连接 |
| HTTP/1.1 | 1999 | 长连接、管道化、缓存、Host 头 |
| HTTP/2 | 2015 | 二进制分帧、多路复用、头部压缩、服务器推送 |
| HTTP/3 | 2022 | 基于 QUIC（UDP）、0-RTT、连接迁移 |

---

## 2. 请求方法

| 方法 | 作用 | 幂等 | 安全 |
|------|------|------|------|
| GET | 获取资源 | 是 | 是 |
| POST | 创建/提交资源 | 否 | 否 |
| PUT | 全量更新资源 | 是 | 否 |
| PATCH | 部分更新资源 | 否 | 否 |
| DELETE | 删除资源 | 是 | 否 |
| HEAD | 获取响应头（无 body） | 是 | 是 |
| OPTIONS | 查询支持的方法/CORS 预检 | 是 | 是 |
| CONNECT | 建立隧道（HTTPS 代理） | - | - |
| TRACE | 回显请求（调试） | 是 | 是 |

> 🔍 **知识点深度解析**
>
> **作用**：理解 HTTP 方法是 RESTful API 设计的基础。
>
> **原理**：幂等性：多次执行结果相同（GET/PUT/DELETE），非幂等（POST/PATCH）每次执行可能产生不同结果。安全性：不改变服务器状态（GET/HEAD/OPTIONS）。GET 参数在 URL 中，有长度限制（浏览器限制，不是协议限制），POST 参数在 body 中，更安全且无长度限制。PUT 是全量替换（不传的字段变为 null），PATCH 是部分更新（只改传的字段）。
>
> **用法要点**：① 查询用 GET，创建用 POST，更新用 PUT/PATCH，删除用 DELETE；② GET 不要有副作用（不要用 GET 修改数据）；③ 面试常考：GET vs POST、幂等性、PUT vs PATCH、RESTful 设计。

---

## 3. 状态码

| 类别 | 含义 |
|------|------|
| 1xx | 信息性，请求已接收，继续处理 |
| 2xx | 成功 |
| 3xx | 重定向 |
| 4xx | 客户端错误 |
| 5xx | 服务器错误 |

**常见状态码**：

| 码 | 说明 |
|----|------|
| 200 OK | 成功 |
| 201 Created | 创建成功 |
| 204 No Content | 成功但无返回体 |
| 301 Moved Permanently | 永久重定向 |
| 302 Found | 临时重定向 |
| 304 Not Modified | 协商缓存命中 |
| 307 Temporary Redirect | 临时重定向（保持方法） |
| 308 Permanent Redirect | 永久重定向（保持方法） |
| 400 Bad Request | 请求参数错误 |
| 401 Unauthorized | 未认证 |
| 403 Forbidden | 无权限 |
| 404 Not Found | 资源不存在 |
| 405 Method Not Allowed | 方法不允许 |
| 408 Request Timeout | 请求超时 |
| 409 Conflict | 冲突 |
| 429 Too Many Requests | 请求过多（限流） |
| 500 Internal Server Error | 服务器内部错误 |
| 502 Bad Gateway | 网关错误（后端挂了） |
| 503 Service Unavailable | 服务不可用 |
| 504 Gateway Timeout | 网关超时 |

> 🔍 **知识点深度解析**
>
> **作用**：状态码是 HTTP 通信的状态反馈，排查问题和 API 设计必备。
>
> **原理**：301/302 重定向时浏览器会将 POST 改为 GET（历史遗留），307/308 保持原方法不变。304 是协商缓存：客户端带 If-Modified-Since/If-None-Match 请求，服务器判断资源未变则返回 304（无 body），客户端用本地缓存。401 是未登录/Token 无效，403 是已登录但无权限。502 是网关（Nginx）连不上后端，504 是后端响应超时。
>
> **用法要点**：① API 设计用正确的状态码，不要都返回 200；② 301 对 SEO 友好（权重转移），302 不转移；③ 面试常考：301 vs 302、304 缓存、401 vs 403、502 vs 504、常见状态码含义。

---

## 4. 请求/响应结构

### 4.1 请求结构

```
GET /api/users?id=1 HTTP/1.1        # 请求行：方法 路径 版本
Host: api.example.com               # 请求头
Accept: application/json
User-Agent: Mozilla/5.0
Authorization: Bearer tokenxxx
Content-Type: application/json
Content-Length: 27
                                    # 空行
{"name": "Tom"}                     # 请求体
```

### 4.2 响应结构

```
HTTP/1.1 200 OK                     # 状态行：版本 状态码 原因短语
Content-Type: application/json      # 响应头
Content-Length: 45
Cache-Control: max-age=3600
                                    # 空行
{"id": 1, "name": "Tom"}            # 响应体
```

---

## 5. 常用 Header

### 5.1 通用 Header

- `Content-Type`：请求/响应体类型（application/json、text/html、multipart/form-data）
- `Content-Length`：body 长度
- `Connection`：keep-alive（长连接）/ close
- `Cache-Control`：缓存控制

### 5.2 请求 Header

- `Accept`：客户端能接受的内容类型
- `Accept-Encoding`：支持的压缩（gzip, br）
- `Authorization`：认证凭证（Bearer Token、Basic）
- `Cookie`：客户端发送的 Cookie
- `Host`：目标主机（HTTP/1.1 必需）
- `Referer`：来源页面
- `User-Agent`：客户端标识
- `If-Modified-Since` / `If-None-Match`：协商缓存

### 5.3 响应 Header

- `Set-Cookie`：设置 Cookie
- `Location`：重定向目标
- `ETag`：资源版本标识
- `Last-Modified`：最后修改时间
- `Access-Control-Allow-Origin`：CORS 允许的源

---

## 6. Cookie / Session / Token

### 6.1 Cookie

- 服务器通过 Set-Cookie 设置，浏览器自动保存
- 后续请求自动携带（同域）
- 属性：`HttpOnly`（防 XSS）、`Secure`（仅 HTTPS）、`SameSite`（防 CSRF）、`Max-Age`/`Expires`、`Domain`、`Path`

### 6.2 Session

- 服务器端存储用户信息，SessionID 通过 Cookie 传递
- 分布式环境需共享 Session（Redis）

### 6.3 Token（JWT）

- 服务器签发，客户端存储（localStorage/Cookie）
- 请求时放在 Authorization 头
- 无状态，适合分布式和微服务
- 结构：Header.Payload.Signature

> 🔍 **知识点深度解析**
>
> **作用**：认证机制是 Web 安全的基础，面试高频。
>
> **原理**：Cookie 是浏览器存储机制，自动携带，有大小限制（4KB）和数量限制。Session 是服务端存储，SessionID 存在 Cookie 中，分布式需要 Session 共享（Redis/粘性会话）。JWT（JSON Web Token）是无状态认证，服务器不存储，Token 包含用户信息和签名，服务器验证签名即可，适合微服务和跨域。JWT 缺点：无法主动失效（除非黑名单）、Payload 不能存敏感信息（Base64 不是加密）。
>
> **用法要点**：① Cookie 加 HttpOnly 防 XSS 窃取，SameSite 防 CSRF；② JWT 放 Authorization: Bearer 头，不要放 URL；③ JWT 设置合理过期时间，用 Refresh Token 续期；④ 面试常考：Cookie vs Session vs Token、JWT 原理、CSRF/XSS 防护、Cookie 属性。

---

## 7. HTTPS 与 TLS

### 7.1 HTTP vs HTTPS

| 特性 | HTTP | HTTPS |
|------|------|-------|
| 端口 | 80 | 443 |
| 加密 | 无 | TLS 加密 |
| 安全性 | 明文，可窃听篡改 | 加密，防窃听篡改 |
| 性能 | 快 | 稍慢（握手开销） |
| 证书 | 不需要 | 需要 CA 证书 |

### 7.2 TLS 握手过程

1. 客户端发送 ClientHello（支持的加密套件、随机数）
2. 服务器返回 ServerHello（选定加密套件、随机数）+ 证书
3. 客户端验证证书，生成预主密钥，用服务器公钥加密发送
4. 双方用随机数+预主密钥计算会话密钥
5. 客户端发送 Finished（加密）
6. 服务器发送 Finished（加密）
7. 后续通信使用会话密钥对称加密

> 🔍 **知识点深度解析**
>
> **作用**：HTTPS 是 Web 安全的基础，TLS 握手是面试重点。
>
> **原理**：HTTPS = HTTP + TLS，TLS 握手用非对称加密（RSA/ECC）交换会话密钥，后续通信用对称加密（AES）——非对称加密安全但慢，对称加密快但需要安全交换密钥，两者结合。证书由 CA 签发，包含服务器公钥和身份信息，客户端用 CA 根证书验证签名确认真伪。TLS 1.3 简化了握手（1-RTT 甚至 0-RTT），移除了不安全的加密套件。
>
> **用法要点**：① 生产环境必须 HTTPS（Chrome 标记 HTTP 为不安全）；② TLS 1.2+，禁用 SSLv3/TLS 1.0/1.1；③ 证书用 Let's Encrypt 免费证书；④ 面试常考：HTTPS 原理、TLS 握手过程、对称 vs 非对称加密、证书验证、HTTP/2 必须 HTTPS（实际规范不强制，但浏览器只支持 HTTPS 的 HTTP/2）。

---

## 8. 缓存机制

### 8.1 强缓存

不发请求，直接用本地缓存。

- `Cache-Control: max-age=3600`：缓存 3600 秒
- `Expires: <绝对时间>`：旧标准，优先级低于 Cache-Control

### 8.2 协商缓存

发请求验证，未变返回 304（无 body）。

- `Last-Modified` / `If-Modified-Since`：基于时间
- `ETag` / `If-None-Match`：基于内容哈希（更精确）

### 8.3 缓存优先级

`Cache-Control` > `Expires` > `ETag` > `Last-Modified`

> 🔍 **知识点深度解析**
>
> **作用**：HTTP 缓存是性能优化的核心手段，面试必问。
>
> **原理**：强缓存期间浏览器不发请求，直接用本地副本（from disk cache/memory cache）。max-age 过期后进入协商缓存：浏览器带 If-Modified-Since（对应 Last-Modified）或 If-None-Match（对应 ETag）发请求，服务器比较后如果资源没变返回 304（无 body，省流量），变了返回 200+新资源。ETag 比 Last-Modified 精确：Last-Modified 精度到秒，1秒内多次修改检测不到；ETag 是内容哈希，内容变了就变。
>
> **用法要点**：① 不常变的资源（JS/CSS/图片）设长缓存 + 文件名 hash（内容变了文件名变，自然更新）；② HTML 设 no-cache（每次协商）；③ 面试常考：强缓存 vs 协商缓存、Cache-Control 指令、ETag vs Last-Modified、304 过程、缓存优先级。

---

## 9. 跨域与 CORS

### 9.1 同源策略

协议、域名、端口都相同才是同源。非同源请求会被浏览器拦截（响应被拦截，请求可能已发出）。

### 9.2 CORS（跨域资源共享）

服务器设置响应头允许跨域：

```
Access-Control-Allow-Origin: https://example.com  # 允许的源
Access-Control-Allow-Methods: GET, POST, PUT       # 允许的方法
Access-Control-Allow-Headers: Content-Type         # 允许的头
Access-Control-Allow-Credentials: true             # 允许携带 Cookie
Access-Control-Max-Age: 86400                      # 预检缓存时间
```

### 9.3 简单请求 vs 预检请求

- **简单请求**：GET/POST/HEAD + 简单 Content-Type，直接发
- **预检请求**：非简单请求先发 OPTIONS 预检，通过后再发真实请求

---

## 10. HTTP/2 与 HTTP/3

### 10.1 HTTP/2 特性

- **二进制分帧**：消息分为帧，更高效解析
- **多路复用**：一个连接并行多个请求，解决队头阻塞
- **头部压缩**：HPACK 算法，减少重复 Header
- **服务器推送**：主动推送资源
- **流量控制**：流级别

### 10.2 HTTP/3 特性

- 基于 **QUIC**（UDP 之上）
- 0-RTT 握手（更快）
- 连接迁移（网络切换不断连）
- 解决 TCP 队头阻塞
- 内置 TLS 1.3

> 🔍 **知识点深度解析**
>
> **作用**：HTTP 版本演进是性能优化的重要方向，了解 HTTP/2/3 是加分项。
>
> **原理**：HTTP/1.1 队头阻塞：一个连接同时只能处理一个请求，前面的请求阻塞后面的（虽然有管道化但问题多），浏览器开 6 个连接缓解但不够。HTTP/2 多路复用：一个连接上多个流并行，互不阻塞，解决应用层队头阻塞。但 HTTP/2 基于 TCP，TCP 层仍有队头阻塞（一个包丢了整个连接等待重传）。HTTP/3 用 QUIC（基于 UDP），每个流独立，丢包只影响对应流，解决传输层队头阻塞，且 QUIC 内置加密和连接迁移。
>
> **用法要点**：① 生产环境开启 HTTP/2（Nginx 配置 http2）；② HTTP/2 不需要域名分片（反而有害，多路复用一个连接更好）；③ HTTP/3 逐步普及，Cloudflare/nginx-quic 支持；④ 面试常考：HTTP/1.1 vs HTTP/2、多路复用、队头阻塞、HTTP/3 QUIC。

---

## 11. 面试高频考点

1. **GET vs POST**：参数位置、幂等、安全、长度
2. **状态码**：301/302、304、401/403、502/504
3. **HTTPS/TLS**：握手过程、对称非对称、证书
4. **缓存**：强缓存/协商缓存、Cache-Control、ETag
5. **Cookie/Session/Token**：区别、JWT 原理
6. **跨域/CORS**：同源策略、预检请求、配置
7. **HTTP/2**：多路复用、头部压缩、队头阻塞
8. **HTTP/3**：QUIC、UDP、连接迁移
9. **Header**：常用请求/响应头
10. **RESTful**：API 设计规范

---

## 📝 精简总结

- HTTP 是无状态应用层协议，基于 TCP/IP
- 方法：GET 查、POST 增、PUT 全量改、PATCH 部分改、DELETE 删
- 状态码：2xx 成功、3xx 重定向、4xx 客户端错、5xx 服务端错
- HTTPS = HTTP + TLS，非对称交换密钥 + 对称加密通信
- 缓存：强缓存（Cache-Control）不发请求，协商缓存（ETag）发请求验证
- 认证：Cookie+Session 有状态，JWT Token 无状态
- 跨域：CORS 服务器配置，预检请求 OPTIONS
- HTTP/2 多路复用解决应用层队头阻塞，HTTP/3 QUIC 解决传输层队头阻塞

---

[[06-计算机基础/MOC-计算机基础|← 返回计算机基础 MOC]] | [[Home|🏠 返回首页]]
