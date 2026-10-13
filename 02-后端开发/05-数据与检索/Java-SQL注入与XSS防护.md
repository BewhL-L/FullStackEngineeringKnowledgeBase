---
title: Java-SQL注入与XSS防护
tags: [Java, SQL注入, XSS, 原子笔记]
category: 后端开发
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["Web安全-XSS-CSRF-SQL注入", "API安全最佳实践", "密码学基础与应用"]
aliases: [Java-SQL注入与XSS防护]
---

# Java-SQL注入与XSS防护

> **文档说明**：系统讲解 SQL 注入和 XSS 的攻击原理、类型、Java 中的防护方案，包括参数化查询（PreparedStatement/MyBatis #{}）、输出转义、CSP、HttpOnly Cookie 等，以及其他注入防护（命令注入/LDAP注入）和安全编码规范。
>
> **适用人群**：后端开发工程师、全栈开发者、安全工程师、Java Web 开发者
>
> **前置知识**：[[Web安全-XSS-CSRF-SQL注入]]、[[API安全最佳实践]]、[[密码学基础与应用]]、[[CSP内容安全策略]]

---

## 一、SQL 注入

### 1. SQL 注入原理

**SQL 注入（SQL Injection）** 是攻击者通过在输入中插入恶意 SQL 代码，操纵应用程序执行非预期 SQL 语句的攻击方式。

```
正常请求：
  username = admin
  SQL: SELECT * FROM users WHERE username = 'admin'

注入攻击：
  username = admin' OR '1'='1
  SQL: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
  结果：返回所有用户，绕过登录
```

### 2. SQL 注入类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **基于错误** | 利用数据库错误信息获取数据 | `' AND 1=CONVERT(int, (SELECT @@version))--` |
| **基于联合查询** | UNION SELECT 合并结果 | `' UNION SELECT username,password FROM users--` |
| **基于布尔盲注** | 通过页面真假判断 | `' AND 1=1--` / `' AND 1=2--` |
| **基于时间盲注** | 通过响应延迟判断 | `' AND SLEEP(5)--` |
| **堆叠查询** | 多语句执行 | `'; DROP TABLE users;--` |
| **二阶注入** | 输入存储后在其他场景触发 | 注册时注入，修改密码时触发 |

### 3. SQL 注入危害

- [ ] **数据泄露**：拖库、窃取用户信息
- [ ] **数据篡改**：修改/删除数据
- [ ] **权限提升**：获取管理员权限
- [ ] **远程代码执行**：通过数据库功能执行系统命令
- [ ] **数据库接管**：获取数据库服务器控制权

---

## 二、SQL 注入防护

### 1. 参数化查询（核心防护）

**参数化查询是防御 SQL 注入的最有效手段**，将 SQL 结构和数据分离，用户输入永远作为参数而非 SQL 代码。

```java
// ❌ 危险：字符串拼接（SQL 注入漏洞）
String sql = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'";
Statement stmt = connection.createStatement();
ResultSet rs = stmt.executeQuery(sql);

// ✅ 安全：PreparedStatement 参数化查询
String sql = "SELECT * FROM users WHERE username = ? AND password = ?";
PreparedStatement pstmt = connection.prepareStatement(sql);
pstmt.setString(1, username);  // 参数绑定，自动转义
pstmt.setString(2, password);
ResultSet rs = pstmt.executeQuery();
```

### 2. MyBatis 防护

```xml
<!-- ❌ 危险：${} 直接拼接（SQL 注入） -->
<select id="findByUsername" resultType="User">
    SELECT * FROM users WHERE username = '${username}'
</select>

<!-- ✅ 安全：#{} 参数化查询 -->
<select id="findByUsername" resultType="User">
    SELECT * FROM users WHERE username = #{username}
</select>

<!-- 动态排序：${} 只能用于列名/排序，需白名单校验 -->
<select id="findUsers" resultType="User">
    SELECT * FROM users
    ORDER BY
    <choose>
        <when test="sortBy == 'name'">name</when>
        <when test="sortBy == 'createdAt'">created_at</when>
        <otherwise>id</otherwise>
    </choose>
    ${sortOrder}  <!-- sortOrder 必须白名单校验：ASC/DESC -->
</select>
```

> **MyBatis 规则**：
> - `#{}` → PreparedStatement 参数绑定，安全
> - `${}` → 字符串直接拼接，有注入风险，仅用于列名/表名/排序，且必须白名单校验

### 3. JPA / Hibernate 防护

```java
// ✅ 安全：JPQL 参数绑定
@Query("SELECT u FROM User u WHERE u.username = :username")
User findByUsername(@Param("username") String username);

// ✅ 安全：Criteria API
CriteriaBuilder cb = em.getCriteriaBuilder();
CriteriaQuery<User> query = cb.createQuery(User.class);
Root<User> root = query.from(User.class);
query.select(root).where(cb.equal(root.get("username"), username));

// ❌ 危险：字符串拼接 JPQL
String jpql = "SELECT u FROM User u WHERE u.username = '" + username + "'";
em.createQuery(jpql).getResultList();
```

### 4. 输入验证（辅助防护）

```java
// 白名单验证（推荐）
public List<User> searchUsers(String sortBy, String sortOrder) {
    // 排序字段白名单
    Set<String> allowedSortBy = Set.of("id", "name", "created_at");
    if (!allowedSortBy.contains(sortBy)) {
        throw new IllegalArgumentException("非法排序字段");
    }
    // 排序方向白名单
    if (!"ASC".equalsIgnoreCase(sortOrder) && !"DESC".equalsIgnoreCase(sortOrder)) {
        throw new IllegalArgumentException("非法排序方向");
    }
    return userRepository.search(sortBy, sortOrder);
}

// 类型验证
public User getUserById(String idStr) {
    Long id;
    try {
        id = Long.parseLong(idStr);  // 非数字直接拒绝
    } catch (NumberFormatException e) {
        throw new IllegalArgumentException("无效的用户ID");
    }
    return userRepository.findById(id);
}
```

### 5. 最小权限原则

```sql
-- 应用数据库用户只授予必要权限
CREATE USER 'app_user'@'%' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE ON mydb.* TO 'app_user'@'%';
-- 不授予 DROP、ALTER、GRANT 等危险权限
-- 不授予 FILE、SUPER 等管理员权限
FLUSH PRIVILEGES;
```

### 6. 其他防护措施

- [ ] **禁止拼接 SQL**：代码评审禁止 Statement 和 ${}
- [ ] **存储过程**：使用参数化存储过程（但不要在存储过程内拼接）
- [ ] **错误信息脱敏**：不向用户返回数据库错误详情
- [ ] **WAF**：Web 应用防火墙检测和拦截 SQL 注入
- [ ] **ORM 框架**：使用 JPA/MyBatis 等 ORM，避免原生 SQL
- [ ] **SQL 注入扫描**：代码扫描工具（SonarQube、FindSecBugs）

---

## 三、XSS 跨站脚本攻击

### 1. XSS 原理

**XSS（Cross-Site Scripting，跨站脚本攻击）** 是攻击者向网页中注入恶意脚本，当其他用户浏览时脚本执行，窃取 Cookie、会话或执行恶意操作。

### 2. XSS 类型

| 类型 | 说明 | 攻击流程 |
|------|------|---------|
| **反射型 XSS** | 恶意脚本在 URL 参数中，服务器反射回页面 | 诱骗用户点击恶意链接 |
| **存储型 XSS** | 恶意脚本存储在数据库，所有访问者受影响 | 提交评论/帖子包含脚本 |
| **DOM 型 XSS** | 客户端 JS 操作 DOM 时注入 | 前端 JS 读取 URL 写入页面 |

```
反射型 XSS：
  URL: /search?q=<script>stealCookie()</script>
  服务器返回: <p>搜索结果: <script>stealCookie()</script></p>
  浏览器执行恶意脚本

存储型 XSS：
  攻击者提交评论: <script>stealCookie()</script>
  存储到数据库
  所有用户查看评论时执行脚本

DOM 型 XSS：
  URL: /#<img src=x onerror=stealCookie()>
  JS: document.getElementById("output").innerHTML = location.hash
  浏览器执行恶意脚本
```

### 3. XSS 危害

- [ ] **Cookie 窃取**：窃取用户会话，冒充用户
- [ ] **会话劫持**：获取登录态，执行操作
- [ ] **钓鱼攻击**：伪造登录表单，窃取密码
- [ ] **键盘记录**：记录用户输入
- [ ] **网站篡改**：修改页面内容
- [ ] **蠕虫传播**：自动转发，感染其他用户

---

## 四、XSS 防护

### 1. 输出转义（核心防护）

根据输出上下文选择合适的转义方式：

| 上下文 | 转义规则 | 示例 |
|--------|---------|------|
| **HTML 内容** | 转义 `< > & " '` | `<` → `&lt;` |
| **HTML 属性** | 转义 `< > & " '` | 用引号包裹属性 |
| **JavaScript** | 转义非字母数字 | `\xHH` 或 `\uHHHH` |
| **URL** | URL 编码 | `encodeURIComponent` |
| **CSS** | 转义非字母数字 | `\HH` |

### 2. Java 后端转义

```java
// Apache Commons Text 转义
import org.apache.commons.text.StringEscapeUtils;

// HTML 转义
String safeHtml = StringEscapeUtils.escapeHtml4(userInput);
// <script> → &lt;script&gt;

// JavaScript 转义
String safeJs = StringEscapeUtils.escapeEcmaScript(userInput);

// XML 转义
String safeXml = StringEscapeUtils.escapeXml11(userInput);

// 自定义 HTML 转义
public static String escapeHtml(String input) {
    if (input == null) return null;
    return input
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\"", "&quot;")
        .replace("'", "&#x27;");
}
```

### 3. 模板引擎自动转义

**Thymeleaf（默认自动转义）**：

```html
<!-- ✅ 安全：th:text 自动 HTML 转义 -->
<p th:text="${userInput}"></p>

<!-- ❌ 危险：th:utext 不转义 -->
<p th:utext="${userInput}"></p>

<!-- ✅ 安全：内联表达式自动转义 -->
<p>[[${userInput}]]</p>

<!-- ❌ 危险：内联不转义 -->
<p>[(${userInput})]</p>
```

**JSP（需手动转义）**：

```jsp
<!-- ❌ 危险：不转义 -->
<%= userInput %>
${userInput}

<!-- ✅ 安全：JSTL 自动转义 -->
<c:out value="${userInput}" />

<!-- ✅ 安全：fn:escapeXml -->
${fn:escapeXml(userInput)}
```

**Vue/React（默认自动转义）**：

```vue
<!-- ✅ 安全：{{ }} 自动转义 -->
<p>{{ userInput }}</p>

<!-- ❌ 危险：v-html 不转义 -->
<p v-html="userInput"></p>
```

```jsx
// ✅ 安全：JSX 自动转义
<p>{userInput}</p>

// ❌ 危险：dangerouslySetInnerHTML 不转义
<p dangerouslySetInnerHTML={{__html: userInput}}></p>
```

### 4. CSP 内容安全策略

CSP 是 XSS 的纵深防御层，限制脚本来源和执行方式。详细参考 [[CSP内容安全策略]]。

```http
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'nonce-{random}';  # 禁止内联脚本和 eval
  style-src 'self';
  object-src 'none';
  base-uri 'self';
  frame-ancestors 'self';
```

### 5. HttpOnly Cookie

```java
// 设置 HttpOnly + Secure + SameSite Cookie
Cookie cookie = new Cookie("session", sessionId);
cookie.setHttpOnly(true);   // 禁止 JS 访问，防止 XSS 窃取
cookie.setSecure(true);     // 仅 HTTPS 传输
cookie.setPath("/");
cookie.setMaxAge(3600);
response.addCookie(cookie);

// Spring Boot 配置
server:
  servlet:
    session:
      cookie:
        http-only: true
        secure: true
        same-site: strict
```

### 6. 输入验证与过滤

```java
// 白名单验证（推荐）
public void setUsername(String username) {
    if (!username.matches("^[a-zA-Z0-9_]{3,20}$")) {
        throw new IllegalArgumentException("用户名只能包含字母数字下划线，长度3-20");
    }
    this.username = username;
}

// HTML 清理（允许部分标签，如富文本）
// 使用 Jsoup 清理
import org.jsoup.Jsoup;
import org.jsoup.safety.Safelist;

String safeHtml = Jsoup.clean(userHtml, Safelist.basic());
// basic 白名单：a, b, blockquote, br, cite, code, dd, dl, dt, em, i, li, ol, p, pre, q, small, span, strike, strong, sub, sup, u, ul

// 自定义白名单
Safelist safelist = Safelist.relaxed()
    .addTags("div", "span")
    .addAttributes("a", "href", "title")
    .addProtocols("a", "href", "http", "https");
String safe = Jsoup.clean(userHtml, safelist);
```

### 7. DOM 型 XSS 防护

```javascript
// ❌ 危险：innerHTML 写入未转义内容
document.getElementById("output").innerHTML = location.search;

// ✅ 安全：textContent 自动转义
document.getElementById("output").textContent = location.search;

// ✅ 安全：创建元素并设置属性
const img = document.createElement("img");
img.src = userInput;  // 仍需验证 URL 协议
document.body.appendChild(img);

// URL 验证
function isSafeUrl(url) {
    try {
        const u = new URL(url);
        return ['http:', 'https:'].includes(u.protocol);
    } catch {
        return false;
    }
}
```

---

## 五、其他注入防护

### 1. 命令注入

```java
// ❌ 危险：字符串拼接执行系统命令
Runtime.getRuntime().exec("ping " + ip);  // ip = "127.0.0.1; rm -rf /"

// ✅ 安全：参数数组形式（不经过 shell 解析）
ProcessBuilder pb = new ProcessBuilder("ping", ip);
pb.start();

// ✅ 更安全：白名单验证输入
if (!ip.matches("^\\d{1,3}(\\.\\d{1,3}){3}$")) {
    throw new IllegalArgumentException("非法 IP 地址");
}
```

### 2. LDAP 注入

```java
// ❌ 危险：拼接 LDAP 查询
String filter = "(uid=" + username + ")";

// ✅ 安全：使用参数化搜索控件
SearchControls ctls = new SearchControls();
ctls.setSearchScope(SearchControls.SUBTREE_SCOPE);
// 使用 DirContext.search 的参数化形式
NamingEnumeration answer = ctx.search("ou=users", "(uid={0})", new Object[]{username}, ctls);
```

### 3. XPath 注入

```java
// ❌ 危险：拼接 XPath
String xpath = "//user[username='" + username + "']";

// ✅ 安全：使用变量解析器
XPath xpath = XPathFactory.newInstance().newXPath();
SimpleVariableResolver resolver = new SimpleVariableResolver();
resolver.addVariable("username", username);
xpath.setXPathVariableResolver(resolver);
String expression = "//user[username=$username]";
```

### 4. XML 外部实体注入（XXE）

```java
// ❌ 危险：允许外部实体
DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
DocumentBuilder builder = factory.newDocumentBuilder();
Document doc = builder.parse(inputStream);  // 可能被 XXE 攻击

// ✅ 安全：禁用外部实体
DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
factory.setXIncludeAware(false);
factory.setExpandEntityReferences(false);
```

---

## 六、安全编码规范

### 1. SQL 安全规范

- [ ] **禁止 Statement**：使用 PreparedStatement 或 ORM
- [ ] **禁止 ${}**：MyBatis 使用 #{}，${} 仅用于白名单场景
- [ ] **禁止动态表名/列名**：必须用白名单校验
- [ ] **最小权限**：数据库用户只授必要权限
- [ ] **错误脱敏**：不向前端返回 SQL 错误详情
- [ ] **批量操作**：使用 addBatch 批量执行，避免循环拼接

### 2. XSS 安全规范

- [ ] **默认转义**：所有用户输入输出到 HTML 时必须转义
- [ ] **模板自动转义**：使用 Thymeleaf/Vue/React 等自动转义模板
- [ ] **禁止 v-html/innerHTML**：除非内容经过严格清理
- [ ] **富文本清理**：使用 Jsoup 白名单清理富文本
- [ ] **HttpOnly Cookie**：会话 Cookie 设置 HttpOnly
- [ ] **CSP 策略**：部署 CSP，禁用内联脚本
- [ ] **输入验证**：白名单验证所有用户输入

### 3. 通用安全规范

- [ ] **不信任任何输入**：所有外部输入都是不可信的
- [ ] **白名单优于黑名单**：只允许已知合法的输入
- [ ] **纵深防御**：多层防护，不依赖单一措施
- [ ] **安全依赖**：定期更新依赖，修复已知漏洞
- [ ] **安全扫描**：CI 中集成安全扫描（SonarQube、Dependency-Check）
- [ ] **代码评审**：安全相关代码必须评审
- [ ] **渗透测试**：定期进行安全测试

---

## 七、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **SQL 注入漏洞** | 使用 Statement / MyBatis ${} | 改为 PreparedStatement / #{} |
| **排序注入** | ORDER BY 使用 ${} 未校验 | 白名单校验排序字段和方向 |
| **LIKE 注入** | LIKE 通配符未转义 | 转义 % 和 _，使用 ESCAPE 子句 |
| **XSS 存储型** | 用户输入未转义直接存储/展示 | 输出时转义，或存储前清理 |
| **XSS 反射型** | URL 参数直接输出到页面 | 输出转义，模板自动转义 |
| **XSS DOM 型** | 前端 JS 用 innerHTML 写入 URL | 改用 textContent，验证输入 |
| **富文本 XSS** | 允许 HTML 输入未清理 | Jsoup 白名单清理，CSP 限制 |
| **Cookie 窃取** | Cookie 未设置 HttpOnly | 设置 HttpOnly + Secure + SameSite |
| **CSP 阻止合法脚本** | 策略过严 / 内联脚本 | 使用 nonce/hash，或移到外部文件 |
| **命令注入** | Runtime.exec 字符串拼接 | ProcessBuilder 参数数组 + 白名单 |
| **XXE 漏洞** | XML 解析允许外部实体 | 禁用 DOCTYPE 和外部实体 |
| **LDAP 注入** | LDAP 查询字符串拼接 | 参数化搜索控件 |
| **JSON 注入** | 拼接 JSON 字符串 | 使用 JSON 库序列化 |
| **日志注入** | 用户输入写入日志未处理 | 过滤换行符，使用结构化日志 |
| **SSRF** | 用户提供 URL 发起请求 | URL 白名单、内网 IP 过滤 |

### SQL 注入检测

```bash
# 代码扫描
# SonarQube / FindSecBugs / SpotBugs
mvn spotbugs:check

# 依赖漏洞扫描
# OWASP Dependency-Check
mvn org.owasp:dependency-check-maven:check

# 渗透测试工具
# sqlmap：自动化 SQL 注入检测
sqlmap -u "https://example.com/api/users?id=1" --batch
```

---

## 八、关联笔记

### 安全相关
- [[Web安全-XSS-CSRF-SQL注入]] · [[API安全最佳实践]] · [[密码学基础与应用]]
- [[CSP内容安全策略]] · [[前端安全-XSS-CSRF防护]] · [[前端敏感数据保护]]
- [[Java-数据加密与脱敏]] · [[SpringSecurity-认证授权]] · [[零信任安全架构]]

### 后端框架
- [[SpringBoot-Web层设计]] · [[SpringSecurity-认证授权]] · [[JWT与OAuth2认证授权]]
- [[Gateway-网关路由与鉴权]]

### 前端
- [[Vue3-组合式API设计模式]] · [[前端工程化知识点系统梳理_优化版]] · [[Axios网络请求封装]]

### 导航
- [[MOC-后端开发]] · [[MOC-计算机基础]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[Web安全-XSS-CSRF-SQL注入]] Web 安全基础 → 深入本文 Java SQL 注入与 XSS 防护 → 实践 [[CSP内容安全策略]] CSP 部署 → 学习 [[SpringSecurity-认证授权]] 安全框架 → 研究 [[API安全最佳实践]] API 安全 → 建立完整的 Web 应用安全防护体系。
