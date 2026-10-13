---
title: 认证与授权原理-OAuth2-JWT
tags: [安全, OAuth2, JWT, OIDC, 原子笔记]
category: 计算机基础
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[SpringSecurity-认证授权]]", "[[JWT与OAuth2认证授权]]", "[[密码学基础与应用]]"]
aliases: [认证与授权原理-OAuth2-JWT]
---

# 认证与授权原理-OAuth2-JWT

> **文档说明**：系统讲解认证与授权的核心原理，包括 OAuth2 四种授权模式、OpenID Connect、JWT 结构与签名算法、Token 生命周期、微服务认证架构，以及安全最佳实践和常见问题。
>
> **适用人群**：后端开发工程师、全栈开发者、安全工程师、需要构建认证授权系统的架构师
>
> **前置知识**：[[SpringSecurity-认证授权]]、[[JWT与OAuth2认证授权]]、[[密码学基础与应用]]、[[Java-微服务安全架构]]

---

## 一、概述

### 1. 认证 vs 授权

| 概念 | 英文 | 说明 | 问题 |
|------|------|------|------|
| **认证** | Authentication | 验证用户身份 | "你是谁？" |
| **授权** | Authorization | 验证用户权限 | "你能做什么？" |

```text
认证（Authentication）：
用户提供凭证（用户名密码/Token）→ 系统验证身份 → 返回身份标识

授权（Authorization）：
已认证用户请求资源 → 系统检查权限 → 允许/拒绝访问
```

### 2. 认证方式演进

```mermaid
graph LR
    A[Session-Cookie] --> B[Token-JWT]
    B --> C[OAuth2]
    C --> D[OIDC]
    D --> E[SSO单点登录]
```

| 方式 | 特点 | 适用场景 |
|------|------|---------|
| **Session-Cookie** | 服务端存储 Session，Cookie 传 ID | 传统 Web、单体应用 |
| **JWT Token** | 无状态、自包含、跨服务 | 前后端分离、微服务 |
| **OAuth2** | 委托授权、第三方登录 | 开放平台、第三方应用 |
| **OIDC** | OAuth2 + 身份层 | 单点登录、身份联邦 |
| **SAML** | XML 格式、企业级 | 企业 SSO、老系统 |

### 3. 核心术语

| 术语 | 说明 |
|------|------|
| **Principal** | 主体（用户/服务）的身份标识 |
| **Credential** | 凭证（密码、Token、证书） |
| **Claim** | JWT 中的声明（用户信息） |
| **Scope** | OAuth2 授权范围（权限粒度） |
| **Issuer** | Token 签发者 |
| **Audience** | Token 接收者 |
| **Resource Owner** | 资源所有者（用户） |
| **Client** | 客户端应用 |
| **Authorization Server** | 授权服务器 |
| **Resource Server** | 资源服务器 |

---

## 二、OAuth2 授权框架

### 1. OAuth2 角色

```mermaid
graph LR
    A[资源所有者<br/>Resource Owner] -->|授权| B[客户端<br/>Client]
    B -->|请求授权| C[授权服务器<br/>Authorization Server]
    C -->|签发Token| B
    B -->|携带Token| D[资源服务器<br/>Resource Server]
    D -->|返回资源| B
```

| 角色 | 说明 | 示例 |
|------|------|------|
| **资源所有者** | 拥有数据的用户 | 终端用户 |
| **客户端** | 请求访问资源的应用 | Web 应用、移动 App |
| **授权服务器** | 认证用户并签发 Token | 微信登录、Auth0 |
| **资源服务器** | 持有受保护资源的 API | 用户信息 API |

### 2. 四种授权模式

| 模式 | 英文 | 适用场景 | 安全性 |
|------|------|---------|--------|
| **授权码模式** | Authorization Code | 有后端的 Web 应用 | ⭐⭐⭐⭐⭐ |
| **授权码+PKCE** | Authorization Code + PKCE | 移动端/SPA 单页应用 | ⭐⭐⭐⭐⭐ |
| **密码模式** | Resource Owner Password | 受信任的第一方应用 | ⭐⭐ |
| **客户端凭证** | Client Credentials | 服务间调用（无用户） | ⭐⭐⭐⭐ |
| **简化模式** | Implicit | 已废弃，不推荐 | ⭐ |

### 3. 授权码模式流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant C as 客户端
    participant AS as 授权服务器
    participant RS as 资源服务器

    U->>C: 点击登录
    C->>AS: 重定向到授权页<br/>?response_type=code&client_id=xxx&redirect_uri=xxx&scope=read
    U->>AS: 输入凭证，同意授权
    AS->>C: 重定向 redirect_uri?code=授权码
    C->>AS: POST /token<br/>grant_type=authorization_code&code=xxx&client_secret=xxx
    AS->>C: 返回 Access Token + Refresh Token
    C->>RS: GET /api/user<br/>Authorization: Bearer <token>
    RS->>C: 返回用户数据
```

### 4. 授权码 + PKCE（推荐用于 SPA/移动端）

```text
PKCE（Proof Key for Code Exchange）解决客户端无法安全存储 client_secret 的问题：

1. 客户端生成 code_verifier（随机字符串）
2. 计算 code_challenge = BASE64URL(SHA256(code_verifier))
3. 授权请求携带 code_challenge
4. 换取 Token 时携带 code_verifier
5. 授权服务器验证 code_verifier 与 code_challenge 匹配
```

```http
# 授权请求
GET /authorize?
  response_type=code
  &client_id=xxx
  &redirect_uri=xxx
  &code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM
  &code_challenge_method=S256

# 换取 Token
POST /token
grant_type=authorization_code
&code=xxx
&client_id=xxx
&code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
```

### 5. 客户端凭证模式（服务间调用）

```http
POST /token
grant_type=client_credentials
&client_id=service-a
&client_secret=xxx
&scope=read:users

# 返回
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 6. 刷新 Token

```http
POST /token
grant_type=refresh_token
&refresh_token=xxx
&client_id=xxx
&client_secret=xxx

# 返回新的 Access Token（Refresh Token 可轮换）
{
  "access_token": "new_token",
  "refresh_token": "new_refresh_token",  # 轮换
  "expires_in": 3600
}
```

---

## 三、OpenID Connect（OIDC）

### 1. OIDC 概述

**OIDC** 是在 OAuth2 之上构建的身份层，在 OAuth2 授权的基础上增加了身份认证能力，返回 ID Token 证明用户身份。

| OAuth2 | OIDC |
|--------|------|
| 解决授权（能做什么） | 解决认证（你是谁） |
| 返回 Access Token | 返回 Access Token + ID Token |
| 无标准用户信息 | 标准 UserInfo 端点 |

### 2. ID Token

ID Token 是一个 JWT，包含用户身份信息：

```json
{
  "iss": "https://auth.example.com",
  "sub": "user_123",
  "aud": "client_id",
  "exp": 1693001800,
  "iat": 1693000000,
  "nonce": "random_nonce",
  "name": "张三",
  "email": "zhangsan@example.com",
  "email_verified": true,
  "picture": "https://...",
  "amr": ["pwd", "mfa"]
}
```

### 3. OIDC 端点

| 端点 | 说明 |
|------|------|
| `/authorize` | 授权端点（获取授权码） |
| `/token` | Token 端点（换取 Token） |
| `/userinfo` | 用户信息端点（获取用户详情） |
| `/.well-known/openid-configuration` | 发现端点（自动发现配置） |
| `/jwks.json` | 公钥端点（验证 JWT 签名） |
| `/end_session` | 登出端点 |

---

## 四、JWT 详解

### 1. JWT 结构

**JWT（JSON Web Token）** 由三部分组成，用 `.` 分隔：

```text
Header.Payload.Signature

示例：
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

| 部分 | 说明 | 内容 |
|------|------|------|
| **Header** | 头部 | 算法、类型 |
| **Payload** | 载荷 | 声明（用户信息、过期时间） |
| **Signature** | 签名 | 验证完整性和来源 |

### 2. Header

```json
{
  "alg": "HS256",    // 签名算法
  "typ": "JWT"       // Token 类型
}
```

### 3. Payload（声明）

```json
{
  // 注册声明（标准）
  "iss": "https://auth.example.com",  // 签发者
  "sub": "user_123",                 // 主体（用户ID）
  "aud": "my-app",                   // 接收者
  "exp": 1693001800,                 // 过期时间
  "nbf": 1693000000,                 // 生效时间
  "iat": 1693000000,                 // 签发时间
  "jti": "unique-token-id",          // Token 唯一ID

  // 公共声明（自定义）
  "name": "张三",
  "email": "zhangsan@example.com",
  "roles": ["USER", "ADMIN"],
  "tenant_id": "tenant_001"
}
```

> **注意**：JWT 的 Payload 是 Base64 编码，不是加密！任何人都可以解码查看内容。不要在 JWT 中存放敏感信息（密码、密钥等）。

### 4. 签名算法

| 算法 | 类型 | 密钥 | 安全性 | 适用场景 |
|------|------|------|--------|---------|
| **HS256** | 对称加密 | 共享密钥 | 中 | 单服务、简单场景 |
| **RS256** | 非对称加密 | 私钥签名/公钥验证 | 高 | 微服务、多服务验证 |
| **ES256** | 非对称加密 | ECDSA 密钥 | 高 | 短 Token、高性能 |
| **PS256** | 非对称加密 | RSA-PSS | 高 | 高安全要求 |

**HS256（对称）**：

```text
签名 = HMAC-SHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret)
```

**RS256（非对称，推荐）**：

```text
签名 = RSA-SHA256(data, private_key)
验证 = RSA-SHA256_verify(data, signature, public_key)
```

### 5. JWT 验证流程

```mermaid
graph LR
    A[客户端请求<br/>携带JWT] --> B[服务端验证]
    B --> C{签名是否正确?}
    C -->|否| D[拒绝 401]
    C -->|是| E{是否过期?}
    E -->|是| D
    E -->|否| F{签发者/接收者是否匹配?}
    F -->|否| D
    F -->|是| G[解析 Payload<br/>获取用户信息]
    G --> H[授权检查]
```

### 6. JWT 验证代码

```java
// Java 使用 jjwt 验证 JWT
public class JwtValidator {
    private final JwtParser parser;

    public JwtValidator(PublicKey publicKey) {
        this.parser = Jwts.parserBuilder()
            .setSigningKey(publicKey)
            .requireIssuer("https://auth.example.com")
            .requireAudience("my-app")
            .build();
    }

    public Claims validate(String token) {
        try {
            return parser.parseClaimsJws(token).getBody();
        } catch (ExpiredJwtException e) {
            throw new TokenException("Token 已过期");
        } catch (SignatureException e) {
            throw new TokenException("Token 签名无效");
        } catch (MalformedJwtException e) {
            throw new TokenException("Token 格式错误");
        }
    }
}
```

```python
# Python 使用 PyJWT 验证
import jwt
from jwt import PyJWKClient

def validate_token(token: str):
    # 从 JWKS 端点获取公钥
    jwks_client = PyJWKClient("https://auth.example.com/.well-known/jwks.json")
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    payload = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience="my-app",
        issuer="https://auth.example.com"
    )
    return payload
```

---

## 五、Token 生命周期管理

### 1. Token 类型

| Token | 作用 | 有效期 | 存储 |
|-------|------|--------|------|
| **Access Token** | 访问资源 | 短（15分钟-1小时） | 内存/HttpOnly Cookie |
| **Refresh Token** | 刷新 Access Token | 长（7天-30天） | HttpOnly Cookie |
| **ID Token** | 身份证明 | 短（与 Access 同） | 内存 |

### 2. Token 刷新策略

```text
策略1：固定过期，重新登录
- 简单，但用户体验差

策略2：Refresh Token 刷新（推荐）
- Access Token 短期（15分钟）
- Refresh Token 长期（7天）
- Access 过期后用 Refresh 换取新 Token
- Refresh Token 轮换（每次刷新生成新的）

策略3：滑动过期
- 每次请求刷新过期时间
- 适合活跃用户
```

### 3. Token 吊销

JWT 是无状态的，无法直接吊销，需要辅助方案：

| 方案 | 说明 | 优缺点 |
|------|------|--------|
| **短过期时间** | Access Token 15分钟过期 | 简单，但有窗口期 |
| **黑名单** | Redis 存储吊销的 Token jti | 精确，但需存储 |
| **版本号** | 用户表维护 token_version，JWT 中携带 | 吊销所有 Token |
| **服务端会话** | 存储会话状态，JWT 仅作标识 | 有状态，失去 JWT 优势 |

```java
// 黑名单方案（Redis）
public void revokeToken(String token) {
    Claims claims = jwtValidator.validate(token);
    String jti = claims.getId();
    long exp = claims.getExpiration().getTime() - System.currentTimeMillis();
    // 将 jti 存入 Redis，过期时间与 Token 相同
    redisTemplate.opsForValue().set("token:blacklist:" + jti, "1", exp, TimeUnit.MILLISECONDS);
}

public boolean isTokenRevoked(String jti) {
    return Boolean.TRUE.equals(redisTemplate.hasKey("token:blacklist:" + jti));
}
```

---

## 六、微服务认证架构

### 1. 网关统一认证

```mermaid
graph LR
    A[客户端] --> B[API网关<br/>认证校验]
    B -->|验证通过<br/>传递用户信息| C[用户服务]
    B --> D[订单服务]
    B --> E[支付服务]
    C --> F[(数据库)]
    D --> F
    E --> F
```

```java
// 网关过滤器：验证 JWT 并传递用户信息
@Component
public class AuthFilter implements GlobalFilter {
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String token = extractToken(exchange.getRequest());
        if (token == null) {
            return unauthorized(exchange);
        }
        try {
            Claims claims = jwtValidator.validate(token);
            // 将用户信息放入请求头传递给下游
            ServerHttpRequest request = exchange.getRequest().mutate()
                .header("X-User-Id", claims.getSubject())
                .header("X-User-Roles", String.join(",", claims.get("roles", List.class)))
                .header("X-Tenant-Id", claims.get("tenant_id", String.class))
                .build();
            return chain.filter(exchange.mutate().request(request).build());
        } catch (Exception e) {
            return unauthorized(exchange);
        }
    }
}
```

### 2. 服务间认证

```text
服务间调用认证：
1. 客户端凭证模式（Client Credentials）
2. mTLS 双向证书认证
3. Service Mesh（Istio）自动认证

推荐：网关层用户认证 + 服务间 mTLS/Client Credentials
```

---

## 七、安全最佳实践

### 1. Token 安全

- [ ] **使用 RS256**：非对称签名，公钥验证，私钥仅授权服务器持有
- [ ] **短过期时间**：Access Token 15分钟，Refresh Token 7天
- [ ] **HttpOnly Cookie**：Token 存储在 HttpOnly Cookie，防止 XSS
- [ ] **Secure + SameSite**：Cookie 设置 Secure 和 SameSite=Strict/Lax
- [ ] **不存敏感信息**：JWT 中不放密码、密钥等敏感数据
- [ ] **验证所有字段**：验证签名、过期、签发者、接收者
- [ ] **Token 轮换**：Refresh Token 每次刷新轮换
- [ ] **吊销机制**：实现黑名单或版本号方案

### 2. OAuth2 安全

- [ ] **使用授权码+PKCE**：不使用简化模式（Implicit）
- [ ] **验证 redirect_uri**：严格白名单，防止开放重定向
- [ ] **state 参数**：防止 CSRF 攻击
- [ ] **nonce 参数**：OIDC 中防止重放攻击
- [ ] **scope 最小化**：只请求必要的权限
- [ ] **client_secret 保护**：不暴露给前端，SPA 用 PKCE
- [ ] **HTTPS 强制**：所有通信使用 HTTPS
- [ ] **速率限制**：Token 端点限流，防止暴力破解

### 3. 常见攻击与防护

| 攻击 | 说明 | 防护 |
|------|------|------|
| **CSRF** | 跨站请求伪造 | SameSite Cookie、CSRF Token |
| **XSS** | 跨站脚本，窃取 Token | HttpOnly Cookie、CSP、输出编码 |
| **重放攻击** | 截获 Token 重放 | 短过期、nonce、jti 黑名单 |
| **Token 篡改** | 修改 Payload | 签名验证（RS256） |
| **开放重定向** | 篡改 redirect_uri | 严格白名单验证 |
| **中间人攻击** | 窃取传输中的 Token | HTTPS、HSTS |
| **暴力破解** | 猜测 Token/密码 | 速率限制、强密钥 |
| **权限提升** | 越权访问 | 服务端重新验证权限，不信任 JWT 中的角色 |

---

## 八、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **JWT 验证失败** | 密钥不匹配 / 算法不一致 | 检查签名算法、公钥是否正确 |
| **Token 过期频繁** | 过期时间太短 / 无刷新机制 | 合理设置过期、实现 Refresh Token |
| **跨域认证失败** | Cookie SameSite / CORS 配置 | SameSite=None; Secure、配置 CORS |
| **微服务间认证** | 服务间无认证 | Client Credentials / mTLS / Service Mesh |
| **登出后 Token 仍有效** | JWT 无状态无法吊销 | 黑名单 / 短过期 / 版本号 |
| **JWT 被 XSS 窃取** | Token 存在 localStorage | 改用 HttpOnly Cookie |
| **Token 体积过大** | Payload 字段过多 | 只存必要信息，用户详情从 API 获取 |
| **算法混淆攻击** | alg: none / 对称密钥当公钥 | 固定验证算法、禁用 none |
| **OAuth2 回调失败** | redirect_uri 不匹配 | 精确匹配白名单，URL 编码 |
| **刷新 Token 泄露** | Refresh Token 存储不当 | HttpOnly Cookie、轮换、绑定设备 |
| **多服务验证慢** | 每次请求调用授权服务器 | 缓存 JWKS 公钥、本地验证 |
| **并发刷新问题** | 多请求同时刷新 Token | 刷新锁、幂等处理 |
| **移动端安全** | 无法安全存储 client_secret | 使用 PKCE，不使用密码模式 |
| **SSO 登出不全** | 各系统 Session 未清除 | 单点登出协议、前端轮询 |
| **权限变更不生效** | JWT 中角色缓存 | 短过期、版本号、关键操作重新查询 |

---

## 九、关联笔记

### 认证授权
- [[SpringSecurity-认证授权]] · [[JWT与OAuth2认证授权]] · [[Java-微服务安全架构]]
- [[API安全最佳实践]]

### 安全基础
- [[密码学基础与应用]] · [[Web安全-XSS-CSRF-SQL注入]] · [[零信任安全架构]]
- [[CSP内容安全策略]]

### 微服务
- [[Gateway-网关路由与鉴权]] · [[实战-SpringCloud微服务电商系统]] · [[Nacos-注册中心与配置中心]]

### 导航
- [[MOC-计算机基础]] · [[MOC-后端开发]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[密码学基础与应用]] 密码学基础 → 学习 [[SpringSecurity-认证授权]] 框架实现 → 深入本文 OAuth2-JWT 原理 → 实践 [[JWT与OAuth2认证授权]] 应用开发 → 研究 [[Java-微服务安全架构]] 微服务安全 → 构建完整的认证授权体系。

---

## 💡 全文深度讲解

本文系统梳理了认证与授权原理-OAuth2-JWT的核心知识体系，从概述入手，深入OAuth2 授权框架的底层机制，再通过OpenID Connect（OIDC）掌握实战应用，最后涵盖常见问题与排查与关联笔记。学习时建议先建立整体认知，再动手实践，最后结合常见问题深化理解。

## 📝 全文精简总结

- **概述**：掌握本模块的核心概念与关键要点
- **OAuth2 授权框架**：掌握本模块的核心概念与关键要点
- **OpenID Connect（OIDC）**：掌握本模块的核心概念与关键要点
- **JWT 详解**：掌握本模块的核心概念与关键要点
- **Token 生命周期管理**：掌握本模块的核心概念与关键要点
- **微服务认证架构**：掌握本模块的核心概念与关键要点
- **安全最佳实践**：掌握本模块的核心概念与关键要点
- **常见问题与排查**：掌握本模块的核心概念与关键要点
- 其余1个模块涵盖进阶主题与拓展内容

