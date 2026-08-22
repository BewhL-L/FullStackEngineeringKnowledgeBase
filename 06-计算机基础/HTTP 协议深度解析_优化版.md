---
title: HTTP 协议深度解析
tags: [计算机基础, HTTP, 网络, 面试]
created: 2026-08-13
updated: 2026-08-13
---

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。

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

> 🔍 **知识点深度解析**
>
> **作用**：请求结构定义了客户端发往服务器的完整报文格式，是 HTTP 通信的起点，决定了服务器如何解析与路由请求。
>
> **原理**：请求由「请求行（方法 + 路径 + 协议版本）+ 请求头（键值对元信息）+ 空行 + 请求体（可选）」四部分构成；HTTP/1.1 强制要求 Host 头以支撑虚拟主机，请求头以空行结束，请求体由 Content-Length 或 Transfer-Encoding 界定边界。
>
> **用法要点**：① 请求行三部分以空格分隔、结尾为 CRLF；② GET 无 body，参数在 URL 中，POST/PUT 的数据放 body；③ Host 头缺失服务器返回 400；④ 用 curl -v 或浏览器 F12 查看真实请求结构便于排障；⑤ 路径中的查询串（?id=1）属于 URL 一部分；⑥ 大 body 用 chunked 分块传输，避免预知长度。

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


> 🔍 **知识点深度解析**
>
> **作用**：HTTP 响应由状态行、响应头、空行和响应体四部分组成，状态行包含版本、状态码和原因短语。
>
> **原理**：状态行：HTTP/1.1 200 OK（版本+状态码+原因短语）。响应头：Content-Type/Content-Length/Set-Cookie/Cache-Control 等。空行（\r\n）分隔头部和主体。响应体：HTML/JSON/图片等资源。状态码分类：1xx 信息、2xx 成功、3xx 重定向、4xx 客户端错误、5xx 服务端错误。
>
> **用法要点**：① 状态行：HTTP版本 + 状态码 + 原因短语  ② 2xx 成功（200/201/204），3xx 重定向（301/302/304）  ③ 4xx 客户端错误（400/401/403/404），5xx 服务端错误（500/502/503）  ④ 响应头和响应体之间用空行分隔  ⑤ 面试常考：状态码含义、301 vs 302、401 vs 403


---
## 5. 常用 Header

> 🔍 **知识点深度解析**
>
> **作用**：响应结构定义了服务器返回给客户端的报文格式，客户端据此解析状态码、头部与响应体并决定后续行为。
>
> **原理**：响应由「状态行（协议版本 + 状态码 + 原因短语）+ 响应头 + 空行 + 响应体」组成；状态码表明结果类别，Content-Type 告诉客户端如何解释 body，Content-Length 界定 body 长度，重定向靠 Location 头配合 3xx。
>
> **用法要点**：① 机器只认状态码数字，原因短语仅供人读；② Content-Type 必须正确（如 application/json; charset=utf-8）否则乱码；③ 204/304 可无响应体；④ 流式响应用 Transfer-Encoding: chunked 代替 Content-Length；⑤ 用 curl -i 查看完整响应头；⑥ 重定向响应务必携带 Location。

### 5.1 通用 Header

- `Content-Type`：请求/响应体类型（application/json、text/html、multipart/form-data）
- `Content-Length`：body 长度
- `Connection`：keep-alive（长连接）/ close
- `Cache-Control`：缓存控制

> 🔍 **知识点深度解析**
>
> **作用**：通用 Header 同时适用于请求与响应，控制连接、消息长度与缓存等跨双方的元信息。
>
> **原理**：Connection: keep-alive 在 HTTP/1.1 默认复用 TCP 连接；Content-Length 是 body 字节数用于界定消息边界；Cache-Control 统一描述缓存行为；Content-Type 声明 body 媒体类型与编码。
>
> **用法要点**：① 启用长连接减少握手开销；② 必须正确设置 Content-Length 或用 chunked，否则 body 被截断或粘包；③ JSON 接口显式指定 charset=utf-8 防乱码；④ 文件上传用 multipart/form-data 并以 boundary 分隔字段；⑤ Cache-Control 同时影响请求与响应的缓存决策；⑥ 调试可临时 Connection: close 强制每次新建连接。

### 5.2 请求 Header

- `Accept`：客户端能接受的内容类型
- `Accept-Encoding`：支持的压缩（gzip, br）
- `Authorization`：认证凭证（Bearer Token、Basic）
- `Cookie`：客户端发送的 Cookie
- `Host`：目标主机（HTTP/1.1 必需）
- `Referer`：来源页面
- `User-Agent`：客户端标识
- `If-Modified-Since` / `If-None-Match`：协商缓存

> 🔍 **知识点深度解析**
>
> **作用**：请求 Header 携带客户端能力与意图，服务器据此完成鉴权、内容协商与路由。
>
> **原理**：Host 标识目标虚拟主机（HTTP/1.1 必需）；Authorization 携带凭证（Bearer/Basic）；Cookie 自动回传会话标识；Accept/Accept-Encoding 声明可接收的类型与压缩；If-Modified-Since/If-None-Match 触发协商缓存。
>
> **用法要点**：① 缺失 Host 头返回 400；② 鉴权放 Authorization: Bearer <token>，勿放 URL（防日志泄露）；③ 跨域请求带 Cookie 需同域或 CORS 允许；④ 启用 Accept-Encoding: gzip,br 压缩省带宽；⑤ Referer 仅作防盗链/CSRF 辅助，不可全信；⑥ 协商缓存优先带 If-None-Match（ETag）。

### 5.3 响应 Header

- `Set-Cookie`：设置 Cookie
- `Location`：重定向目标
- `ETag`：资源版本标识
- `Last-Modified`：最后修改时间
- `Access-Control-Allow-Origin`：CORS 允许的源

---


> 🔍 **知识点深度解析**
>
> **作用**：HTTP 响应头控制缓存、内容类型、跨域、Cookie 和安全策略，是服务端指令的传递载体。
>
> **原理**：Content-Type：响应体 MIME 类型（application/json; charset=utf-8）。Cache-Control：缓存策略（max-age/no-cache/no-store）。Set-Cookie：下发 Cookie（含 HttpOnly/Secure/SameSite）。Access-Control-Allow-Origin：CORS 跨域允许。Content-Encoding：压缩编码（gzip/br）。Strict-Transport-Security：强制 HTTPS。X-Content-Type-Options：nosniff 防 MIME 嗅探。
>
> **用法要点**：① Content-Type 指定媒体类型和字符集  ② Cache-Control: max-age=31536000 强缓存，no-cache 协商缓存  ③ Set-Cookie 加 HttpOnly/Secure/SameSite 防 XSS/CSRF  ④ CORS 相关：Allow-Origin/Allow-Methods/Allow-Headers  ⑤ 面试常考：缓存头、安全头、CORS 头、Content-Type


---
## 6. Cookie / Session / Token

> 🔍 **知识点深度解析**
>
> **作用**：响应 Header 告知客户端如何处理响应、设置 Cookie、控制缓存与跨域。
>
> **原理**：Set-Cookie 写入客户端 Cookie（含 HttpOnly/Secure/SameSite 属性）；Location 配合 3xx 重定向；ETag/Last-Modified 用于协商缓存校验；Access-Control-Allow-Origin 等实现 CORS。
>
> **用法要点**：① 敏感 Cookie 必须 HttpOnly+Secure+SameSite 防 XSS/CSRF；② 重定向响应必须带 Location；③ 协商缓存返回 ETag（优先）或 Last-Modified；④ 带凭证的跨域需 Access-Control-Allow-Credentials: true 且 Origin 不能为 *；⑤ 用 Cache-Control 而非仅依赖 Expires；⑥ 服务器时钟/时区影响 Last-Modified 与 Expires 准确性。

### 6.1 Cookie

- 服务器通过 Set-Cookie 设置，浏览器自动保存
- 后续请求自动携带（同域）
- 属性：`HttpOnly`（防 XSS）、`Secure`（仅 HTTPS）、`SameSite`（防 CSRF）、`Max-Age`/`Expires`、`Domain`、`Path`

> 🔍 **知识点深度解析**
>
> **作用**：Cookie 是浏览器持久化小规模客户端状态的机制，用于会话识别、偏好保存与追踪。
>
> **原理**：服务器通过 Set-Cookie 写入，浏览器按域名存储并在后续同域请求自动携带；受 HttpOnly（禁 JS 读取）、Secure（仅 HTTPS 传输）、SameSite（跨站是否携带）、Max-Age/Domain/Path 等属性约束；容量约 4KB、数量有限。
>
> **用法要点**：① HttpOnly 防 XSS 窃取令牌；② Secure 仅在 HTTPS 下发送；③ SameSite=Lax/Strict 缓解 CSRF；④ Max-Age/Expires 控制生命周期，不设则为会话级；⑤ Domain/Path 限制作用范围；⑥ 不存敏感明文，大数据用 Token 或后端存储。

### 6.2 Session

- 服务器端存储用户信息，SessionID 通过 Cookie 传递
- 分布式环境需共享 Session（Redis）

> 🔍 **知识点深度解析**
>
> **作用**：Session 在服务器端保存用户会话状态，弥补 HTTP 无状态，常用于登录态管理。
>
> **原理**：服务器创建 Session 并生成 SessionID，通过 Cookie（如 JSESSIONID）传给浏览器；后续请求带 SessionID，服务器据此查到对应用户数据；数据存于服务器内存或 Redis，客户端仅持 ID。
>
> **用法要点**：① 分布式部署用 Redis 集中存储 Session 实现共享；② 粘性会话（同用户落同节点）扩展性差，仅作替代；③ Session 占服务端资源，需设超时清理；④ 防 Session 固定攻击（登录后重置 ID）；⑤ 无 Cookie 场景用 URL 重写或 Token；⑥ 高并发下 Session 存储/查找是性能关注点。

### 6.3 Token（JWT）

- 服务器签发，客户端存储（localStorage/Cookie）
- 请求时放在 Authorization 头
- 无状态，适合分布式和微服务
- 结构：Header.Payload.Signature

> 🔍 **知识点深度解析**
>
> **作用**：Token（尤其 JWT）提供无状态认证，适合分布式、微服务与跨域场景。
>
> **原理**：JWT 由 Header（算法/类型）.Payload（声明，Base64 可解码但非加密）.Signature（服务端密钥签名）三段组成；服务器验签即可信，无需查库；客户端自行保存并在 Authorization 头携带。
>
> **用法要点**：① Payload 可解码，绝不能放密码等敏感信息；② 用 Authorization: Bearer 传递，别放 URL；③ 设较短过期时间 + Refresh Token 续期；④ 无法主动失效，可用黑名单或短过期缓解；⑤ 签名密钥必须保密且足够强；⑥ 需配合 HTTPS 防窃听。

> 🔍 **知识点深度解析**
>
> **作用**：认证机制是 Web 安全的基础，面试高频。
>
> **原理**：Cookie 是浏览器存储机制，自动携带，有大小限制（4KB）和数量限制。Session 是服务端存储，SessionID 存在 Cookie 中，分布式需要 Session 共享（Redis/粘性会话）。JWT（JSON Web Token）是无状态认证，服务器不存储，Token 包含用户信息和签名，服务器验证签名即可，适合微服务和跨域。JWT 缺点：无法主动失效（除非黑名单）、Payload 不能存敏感信息（Base64 不是加密）。
>
> **用法要点**：① Cookie 加 HttpOnly 防 XSS 窃取，SameSite 防 CSRF；② JWT 放 Authorization: Bearer 头，不要放 URL；③ JWT 设置合理过期时间，用 Refresh Token 续期；④ 面试常考：Cookie vs Session vs Token、JWT 原理、CSRF/XSS 防护、Cookie 属性。

---


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

> 🔍 **知识点深度解析**
>
> **作用**：区分明文与加密传输，决定通信的机密性、完整性与身份可信度。
>
> **原理**：HTTPS = HTTP + TLS；HTTP 明文易被窃听/篡改，HTTPS 在传输层加密；端口（80 vs 443）、证书、握手开销是主要差异；现代浏览器将 HTTP 标记为不安全。
>
> **用法要点**：① 生产全站 HTTPS（含内部服务间调用）；② 证书由 CA 签发，自签仅用于测试；③ 启用 TLS 1.2+，禁用 SSLv3/TLS 1.0/1.1；④ HSTS 强制 HTTPS 防降级攻击；⑤ 混合内容（HTTPS 页嵌 HTTP 资源）被浏览器拦截；⑥ 监控证书到期与域名匹配，避免访问失败。

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
> **作用**：在客户端与服务器间安全地协商出对称密钥，建立加密信道，是 HTTPS 安全性的核心。
>
> **原理**：双方交换随机数，服务器发证书（含公钥）供客户端验证身份；客户端生成预主密钥用公钥加密回传，双方据随机数与预主密钥推导出相同会话密钥；之后用对称加密通信。TLS 1.3 简化至 1-RTT/0-RTT。
>
> **用法要点**：① 证书链须完整且被客户端信任（根 CA 内置）；② 握手含非对称运算是 HTTPS 延迟主因，用会话恢复（Session Ticket）复用；③ 密钥仅本次会话有效，具前向安全；④ 校验证书有效期、域名与吊销状态；⑤ OCSP Stapling 减少客户端校验延迟；⑥ 抓包需服务端私钥才能解密，便于排障但须妥善保管。

> 🔍 **知识点深度解析**
>
> **作用**：HTTPS 是 Web 安全的基础，TLS 握手是面试重点。
>
> **原理**：HTTPS = HTTP + TLS，TLS 握手用非对称加密（RSA/ECC）交换会话密钥，后续通信用对称加密（AES）——非对称加密安全但慢，对称加密快但需要安全交换密钥，两者结合。证书由 CA 签发，包含服务器公钥和身份信息，客户端用 CA 根证书验证签名确认真伪。TLS 1.3 简化了握手（1-RTT 甚至 0-RTT），移除了不安全的加密套件。
>
> **用法要点**：① 生产环境必须 HTTPS（Chrome 标记 HTTP 为不安全）；② TLS 1.2+，禁用 SSLv3/TLS 1.0/1.1；③ 证书用 Let's Encrypt 免费证书；④ 面试常考：HTTPS 原理、TLS 握手过程、对称 vs 非对称加密、证书验证、HTTP/2 必须 HTTPS（实际规范不强制，但浏览器只支持 HTTPS 的 HTTP/2）。

---


---
## 8. 缓存机制

### 8.1 强缓存

不发请求，直接用本地缓存。

- `Cache-Control: max-age=3600`：缓存 3600 秒
- `Expires: <绝对时间>`：旧标准，优先级低于 Cache-Control

> 🔍 **知识点深度解析**
>
> **作用**：让客户端在缓存有效期内直接复用本地副本，不发请求，是性能最优的缓存方式。
>
> **原理**：浏览器据 Cache-Control: max-age 或 Expires 判断资源是否新鲜；新鲜则直接使用本地缓存（from memory/disk cache），不访问网络。
>
> **用法要点**：① 静态资源（JS/CSS/图片）设长 max-age + 文件名 hash，内容变则文件名变自然更新；② Expires 为绝对时间受时钟影响，优先级低于 Cache-Control；③ no-cache 不是不缓存而是每次校验；④ no-store 完全不缓存（敏感数据）；⑤ max-age=0 立即过期转协商；⑥ 强缓存命中无网络请求，DevTools 显示 200 (from cache)。

### 8.2 协商缓存

发请求验证，未变返回 304（无 body）。

- `Last-Modified` / `If-Modified-Since`：基于时间
- `ETag` / `If-None-Match`：基于内容哈希（更精确）

> 🔍 **知识点深度解析**
>
> **作用**：缓存过期后由服务器判定资源是否变化，未变则返回 304 省流量。
>
> **原理**：客户端带 If-Modified-Since（对应 Last-Modified）或 If-None-Match（对应 ETag）请求；服务器比较：未变返回 304（无 body），已变返回 200 + 新内容。
>
> **用法要点**：① ETag（内容哈希）比 Last-Modified（秒级时间）更精确，优先用；② 1 秒内多次修改 Last-Modified 检测不到，ETag 可；③ 304 无响应体，仅省带宽不省请求；④ 动态接口慎用缓存（数据易变）；⑤ 网关/CDN 也遵循缓存头；⑥ 改了文件但 ETag 没变需确认生成策略。

### 8.3 缓存优先级

`Cache-Control` > `Expires` > `ETag` > `Last-Modified`

> 🔍 **知识点深度解析**
>
> **作用**：明确多缓存头共存时的生效顺序，避免配置冲突导致意外行为。
>
> **原理**：当多种缓存机制同时出现，浏览器按 Cache-Control > Expires > ETag/Last-Modified 的优先级决策；强缓存（前两者）优先于协商缓存（后两者）。
>
> **用法要点**：① 以 Cache-Control 为主，其他作兜底；② 同时设 max-age 与 Expires，以 max-age 为准；③ 设了强缓存仍需 ETag 支持过期后再校验；④ 不同层（浏览器/CDN/代理）缓存头需一致；⑤ 调试用禁用缓存（DevTools/禁用 Cache-Control）看真实来源；⑥ 缓存策略按资源变更频率分级。

> 🔍 **知识点深度解析**
>
> **作用**：HTTP 缓存是性能优化的核心手段，面试必问。
>
> **原理**：强缓存期间浏览器不发请求，直接用本地副本（from disk cache/memory cache）。max-age 过期后进入协商缓存：浏览器带 If-Modified-Since（对应 Last-Modified）或 If-None-Match（对应 ETag）发请求，服务器比较后如果资源没变返回 304（无 body，省流量），变了返回 200+新资源。ETag 比 Last-Modified 精确：Last-Modified 精度到秒，1秒内多次修改检测不到；ETag 是内容哈希，内容变了就变。
>
> **用法要点**：① 不常变的资源（JS/CSS/图片）设长缓存 + 文件名 hash（内容变了文件名变，自然更新）；② HTML 设 no-cache（每次协商）；③ 面试常考：强缓存 vs 协商缓存、Cache-Control 指令、ETag vs Last-Modified、304 过程、缓存优先级。

---


---
## 9. 跨域与 CORS

### 9.1 同源策略

协议、域名、端口都相同才是同源。非同源请求会被浏览器拦截（响应被拦截，请求可能已发出）。

> 🔍 **知识点深度解析**
>
> **作用**：浏览器安全基石，限制一个源（协议+域名+端口）的文档读取另一源的资源，防数据泄露。
>
> **原理**：同源指协议、域名、端口三者全同；跨源读取（如 fetch 其他域、读取 iframe DOM）被阻止；注意请求可能已发出，只是响应被拦截。
>
> **用法要点**：① 同源判断严格包含端口（不同端口即跨源）；② 表单提交/脚本/img 标签不受同源限制（但读响应受限）；③ 跨域读数据需 CORS/代理/JSONP（已过时）；④ 父子 iframe 跨源无法互访 DOM；⑤ 同源是 CORS/CSRF 防护的前提；⑥ 本地开发跨端口调接口需配代理或 CORS。

### 9.2 CORS（跨域资源共享）

服务器设置响应头允许跨域：

```
Access-Control-Allow-Origin: https://example.com  # 允许的源
Access-Control-Allow-Methods: GET, POST, PUT       # 允许的方法
Access-Control-Allow-Headers: Content-Type         # 允许的头
Access-Control-Allow-Credentials: true             # 允许携带 Cookie
Access-Control-Max-Age: 86400                      # 预检缓存时间
```

> 🔍 **知识点深度解析**
>
> **作用**：跨域资源共享，在同源策略下安全地放行指定跨源请求。
>
> **原理**：服务器通过响应头声明允许的来源、方法、头；浏览器按此决定是否放行跨源响应；带凭证需 Allow-Credentials 且 Origin 不能写 *。
>
> **用法要点**：① Access-Control-Allow-Origin 指定可信源，* 表示任意（不能带凭证）；② 带自定义头/凭证需 Allow-Headers/Allow-Credentials；③ 配置错误导致前端报 CORS 错误，后端修响应头；④ 与 Cookie 同用时 Origin 必须具体且 Allow-Credentials: true；⑤ 暴露响应头用 Access-Control-Expose-Headers；⑥ 预检结果可用 Access-Control-Max-Age 缓存。

### 9.3 简单请求 vs 预检请求

- **简单请求**：GET/POST/HEAD + 简单 Content-Type，直接发
- **预检请求**：非简单请求先发 OPTIONS 预检，通过后再发真实请求

---


> 🔍 **知识点深度解析**
>
> **作用**：CORS 将请求分为简单请求和预检请求，预检请求用 OPTIONS 方法询问服务端是否允许实际请求。
>
> **原理**：简单请求需同时满足：方法为 GET/POST/HEAD；Content-Type 仅限 application/x-www-form-urlencoded/multipart/form-data/text/plain；无自定义头。简单请求直接发送，服务端返回 Access-Control-Allow-Origin 即可。不满足条件的请求（如 application/json、PUT/DELETE、自定义头）先发 OPTIONS 预检请求，服务端返回允许的方法/头/有效期，预检通过后才发实际请求。
>
> **用法要点**：① 简单请求：GET/POST/HEAD + 三种 Content-Type + 无自定义头  ② 预检请求：OPTIONS 方法，询问 Access-Control-Request-Method/Headers  ③ 预检通过后才发实际请求，增加一次 RTT  ④ Access-Control-Max-Age 缓存预检结果，减少 OPTIONS 请求  ⑤ 面试常考：简单请求条件、预检流程、OPTIONS 优化


---
## 10. HTTP/2 与 HTTP/3

> 🔍 **知识点深度解析**
>
> **作用**：区分两类跨域请求，理解浏览器何时先发 OPTIONS 预检，避免接口设计踩坑。
>
> **原理**：简单请求（GET/HEAD/POST + 受限方法/头/Content-Type）直接发；非简单请求（如 PUT、带自定义头、Content-Type 为 application/json）先发 OPTIONS 预检，服务器同意后才发真实请求。
>
> **用法要点**：① application/json 的 POST 属非简单请求，会触发预检；② 预检 OPTIONS 不带 body，服务器须正确响应（含允许头）；③ 后端对 OPTIONS 直接返回 204/200 且不走业务逻辑；④ 用 Max-Age 缓存预检减少请求；⑤ 携带凭证的跨域即便简单请求也受限；⑥ 调试跨域先看 Network 里的 OPTIONS 是否被放行。

### 10.1 HTTP/2 特性

- **二进制分帧**：消息分为帧，更高效解析
- **多路复用**：一个连接并行多个请求，解决队头阻塞
- **头部压缩**：HPACK 算法，减少重复 Header
- **服务器推送**：主动推送资源
- **流量控制**：流级别

> 🔍 **知识点深度解析**
>
> **作用**：在 HTTP/1.1 之上大幅降低延迟、提升并发，解决应用层队头阻塞。
>
> **原理**：二进制分帧将消息拆成帧在单连接上多路复用，并行无阻塞；HPACK 压缩头部去重；服务器可主动推送；流级流量控制。
>
> **用法要点**：① 多路复用下不要再域名分片（反而有害）；② 头部压缩对大量重复 Cookie/头收益大；③ 服务器推送需服务端主动配置，使用场景有限；④ 仍需 HTTPS（浏览器仅支持加密 HTTP/2）；⑤ 单连接上并发流受 SETTINGS 限制；⑥ 调试用 curl --http2 或 Chrome net-internals。

### 10.2 HTTP/3 特性

- 基于 **QUIC**（UDP 之上）
- 0-RTT 握手（更快）
- 连接迁移（网络切换不断连）
- 解决 TCP 队头阻塞
- 内置 TLS 1.3

> 🔍 **知识点深度解析**
>
> **作用**：用 QUIC（基于 UDP）解决 TCP 层队头阻塞与连接迁移，进一步降延迟。
>
> **原理**：HTTP/3 在 QUIC 之上运行，QUIC 内置 TLS 1.3 与可靠传输，每个流独立，单流丢包不影响其他流；0-RTT 复用会话密钥快速建连；连接 ID 支持网络切换不断连。
>
> **用法要点**：① QUIC 解决 TCP 队头阻塞（HTTP/2 仍受其困）；② 连接迁移适合移动端切网；③ 0-RTT 有重放风险，敏感操作仍用 1-RTT；④ 部署需支持 UDP（部分网络封锁 UDP）；⑤ Nginx/Cloudflare 等已支持，可渐进开启；⑥ 监控 UDP/QUIC 连通性与丢包。

> 🔍 **知识点深度解析**
>
> **作用**：HTTP 版本演进是性能优化的重要方向，了解 HTTP/2/3 是加分项。
>
> **原理**：HTTP/1.1 队头阻塞：一个连接同时只能处理一个请求，前面的请求阻塞后面的（虽然有管道化但问题多），浏览器开 6 个连接缓解但不够。HTTP/2 多路复用：一个连接上多个流并行，互不阻塞，解决应用层队头阻塞。但 HTTP/2 基于 TCP，TCP 层仍有队头阻塞（一个包丢了整个连接等待重传）。HTTP/3 用 QUIC（基于 UDP），每个流独立，丢包只影响对应流，解决传输层队头阻塞，且 QUIC 内置加密和连接迁移。
>
> **用法要点**：① 生产环境开启 HTTP/2（Nginx 配置 http2）；② HTTP/2 不需要域名分片（反而有害，多路复用一个连接更好）；③ HTTP/3 逐步普及，Cloudflare/nginx-quic 支持；④ 面试常考：HTTP/1.1 vs HTTP/2、多路复用、队头阻塞、HTTP/3 QUIC。

---


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
