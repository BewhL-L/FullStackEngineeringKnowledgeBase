---
title: Spring Boot 知识点系统梳理
tags: [后端, SpringBoot, 框架, 入门]
created: 2026-08-12
updated: 2026-08-12
---

# Spring Boot 知识点系统梳理（优化版）

> **文档说明**：本文档参照《Java知识点完整整合大全》排版风格，系统梳理 Spring Boot 技术栈。包含概述、核心特性、常用用法、注意事项四大模块，辅以动态可视化解析图、深度讲解与精简总结。**优化版**在原有内容基础上，为每个知识点补充了作用、原理、用法的深度解析，并新增了知识点图解。

---

## 1. 概述

Spring Boot 是由 Pivotal 团队开发的基于 Spring 框架的快速开发脚手架，其核心设计理念是**"约定优于配置"（Convention over Configuration）**。它通过自动配置、起步依赖和内嵌服务器，极大简化了 Spring 应用的初始搭建和开发过程。

**核心定位**：
- 不是对 Spring 功能的增强，而是提供一种快速使用 Spring 的方式
- 整合了大量常用框架的默认配置，开箱即用
- 广泛应用于微服务架构，是 Spring Cloud 的基础

**版本演进**：

| 版本 | 发布年份 | 关键特性 |
|------|---------|---------|
| Spring Boot 1.x | 2014 | 初始版本，自动配置起步 |
| Spring Boot 2.x | 2018 | 基于 Spring 5，响应式 WebFlux，Micrometer 监控 |
| Spring Boot 3.x | 2022 | 基于 Spring 6，Jakarta EE 9+，Java 17+ 最低要求，AOT 编译 |

---


---
## 2. 核心特性

<div style="background:linear-gradient(135deg,#f6d365,#fda085);border-radius:16px;padding:24px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#1a1a2e;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes sbFeature{0%,100%{transform:scale(1);opacity:.85}50%{transform:scale(1.03);opacity:1}}.sb-feat{display:inline-block;width:30%;vertical-align:top;margin:0 1%;background:rgba(255,255,255,.4);border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:10px;font-size:11px;text-align:center;animation:sbFeature 3s ease-in-out infinite}.sb-feat:nth-child(2){animation-delay:.5s}.sb-feat:nth-child(3){animation-delay:1s}.sb-feat:nth-child(4){animation-delay:1.5s}.sb-feat:nth-child(5){animation-delay:2s}.sb-feat:nth-child(6){animation-delay:2.5s}.sb-icon{font-size:22px;margin-bottom:4px}.sb-name{font-weight:700;font-size:12px;margin-bottom:2px}</style>
<div style="text-align:center;font-size:16px;font-weight:700;margin-bottom:16px;padding-bottom:12px;border-bottom:1.5px solid rgba(0,0,0,.1);letter-spacing:1px">Spring Boot 六大核心特性</div>
<div style="text-align:center">
<div class="sb-feat"><div class="sb-icon">⚙️</div><div class="sb-name">自动配置</div><div style="font-size:9px;opacity:.8">AutoConfiguration<br>根据依赖自动装配Bean</div></div>
<div class="sb-feat"><div class="sb-icon">📦</div><div class="sb-name">起步依赖</div><div style="font-size:9px;opacity:.8">Starter POMs<br>一站式依赖管理</div></div>
<div class="sb-feat"><div class="sb-icon">🚀</div><div class="sb-name">内嵌服务器</div><div style="font-size:9px;opacity:.8">Tomcat/Jetty/Undertow<br>无需部署WAR</div></div>
<div class="sb-feat"><div class="sb-icon">📊</div><div class="sb-name">Actuator监控</div><div style="font-size:9px;opacity:.8">健康检查/指标<br>生产级运维</div></div>
<div class="sb-feat"><div class="sb-icon">🔧</div><div class="sb-name">YAML配置</div><div style="font-size:9px;opacity:.8">application.yml<br>多环境Profile</div></div>
<div class="sb-feat"><div class="sb-icon">🌐</div><div class="sb-name">微服务就绪</div><div style="font-size:9px;opacity:.8">Spring Cloud基础<br>云原生适配</div></div>
</div>
</div>

### 2.1 自动配置（AutoConfiguration）

**核心原理**：
- `@SpringBootApplication` 包含 `@EnableAutoConfiguration`
- 通过 `spring.factories`（Spring Boot 2.7-）或 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`（Spring Boot 2.7+）加载自动配置类
- 条件注解 `@ConditionalOnClass`、`@ConditionalOnMissingBean`、`@ConditionalOnProperty` 决定是否生效

**自动配置报告**：`--debug` 启动查看哪些自动配置生效/未生效。

> 🔍 **知识点深度解析**
>
> **作用**：自动配置是 Spring Boot 的核心，根据 classpath 中的依赖自动装配 Bean，无需手动 XML/Java 配置。极大减少了配置代码，实现"约定优于配置"。
>
> **原理**：@EnableAutoConfiguration 通过 AutoConfigurationImportSelector 加载 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports 文件中定义的自动配置类（Spring Boot 2.7+，旧版用 spring.factories）。每个自动配置类用条件注解控制：@ConditionalOnClass（classpath 有某类才生效）、@ConditionalOnMissingBean（容器中没有该 Bean 才创建）、@ConditionalOnProperty（配置属性满足才生效）、@ConditionalOnWebApplication（Web 应用才生效）。自动配置类的 Bean 定义在用户自定义 Bean 之后加载，所以用户定义的 Bean 优先（@ConditionalOnMissingBean 保证不覆盖用户 Bean）。
>
> **用法要点**：① 启动加 --debug 查看自动配置报告（Positive matches/ Negative matches）；② 自定义 Bean 会覆盖自动配置的 Bean（@ConditionalOnMissingBean）；③ 排除自动配置：@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)；④ 自定义 Starter：写 AutoConfiguration 类 + 注册到 AutoConfiguration.imports；⑤ 条件注解顺序：先 @ConditionalOnClass 再 @ConditionalOnBean（避免类不存在报错）；⑥ 自动配置不是黑盒，读源码理解默认配置；⑦ 面试常考：自动配置原理、spring.factories 机制。

### 2.2 起步依赖（Starter）

**常用 Starter**：
- `spring-boot-starter-web`：Spring MVC + Tomcat + Jackson
- `spring-boot-starter-data-jpa`：Hibernate + Spring Data JPA
- `spring-boot-starter-data-redis`：Redis + Lettuce
- `spring-boot-starter-amqp`：RabbitMQ
- `spring-boot-starter-test`：JUnit + Mockito + AssertJ

**原理**：Starter 是一组依赖的聚合 POM，引入一个 Starter 就自动引入相关依赖，并由自动配置完成装配。

> 🔍 **知识点深度解析**
>
> **作用**：Starter 解决了依赖管理问题，不需要手动找一堆依赖和版本号。引入一个 Starter 就获得完整的技术栈（依赖+自动配置），版本由 Spring Boot BOM 统一管理。
>
> **原理**：Starter 本质是一个 Maven POM（或 Gradle 依赖描述），声明了一组相关依赖。如 spring-boot-starter-web 依赖 spring-web、spring-webmvc、tomcat-embed-core、jackson-databind 等。版本号由 spring-boot-dependencies BOM 统一管理，避免版本冲突。Starter 本身不含代码（只有 pom.xml），实际的自动配置在 spring-boot-autoconfigure 或第三方 starter 的 autoconfigure 模块中。
>
> **用法要点**：① 优先用官方 Starter（spring-boot-starter-*），第三方用 groupId-spring-boot-starter 命名；② 版本不用指定（由 Spring Boot BOM 管理），除非需要特定版本；③ 排除不需要的依赖：exclusions（如排除 Tomcat 用 Jetty）；④ 自定义 Starter：命名规范 myproject-spring-boot-starter，包含 starter（pom）+ autoconfigure（代码）两个模块；⑤ Spring Boot 3.x 用 Jakarta EE（jakarta.* 包），2.x 用 Java EE（javax.*）；⑥ 不要重复引入依赖（Starter 已包含）；⑦ 查看依赖树：mvn dependency:tree。

### 2.3 内嵌服务器

**默认 Tomcat**，可切换 Jetty、Undertow。

```xml
<!-- 切换 Undertow -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-undertow</artifactId>
</dependency>
```

**配置**：`server.port`、`server.servlet.context-path`、`server.tomcat.*`。

> 🔍 **知识点深度解析**
>
> **作用**：内嵌服务器让 Spring Boot 应用可以直接 `java -jar` 运行，不需要外部 Tomcat/WAR 部署。简化了部署，适合微服务和容器化（Docker/K8s）。
>
> **原理**：Spring Boot 的 web 应用是一个包含 main 方法的 Java 应用，启动时创建 AnnotationConfigServletWebServerApplicationContext，该上下文在刷新时调用 ServletWebServerFactory（TomcatServletWebServerFactory/JettyServletWebServerFactory）创建内嵌服务器实例。Tomcat 通过 TomcatEmbeddedServletContainerFactory 配置端口、连接器、上下文等，然后启动 Tomcat 线程监听请求。DispatcherServlet 自动注册（DispatcherServletAutoConfiguration），不需要 web.xml。
>
> **用法要点**：① 默认 Tomcat，性能足够大多数场景；② Undertow 性能更好（非阻塞 IO），资源占用更低，高并发推荐；③ Jetty 轻量，适合嵌入式场景；④ 端口配置：server.port=0 随机端口（测试用）；⑤ 容器配置：server.tomcat.threads.max（最大线程数，默认200）、server.tomcat.accept-count（等待队列）；⑥ 优雅停机：server.shutdown=graceful + spring.lifecycle.timeout-per-shutdown-phase=30s；⑦ 外部容器部署：继承 SpringBootServletInitializer，打包 war。

### 2.4 YAML 配置与 Profile

**YAML 优势**：层级结构清晰，支持列表，比 properties 更易读。

**多环境配置**：
- `application.yml`：公共配置
- `application-dev.yml`：开发环境
- `application-prod.yml`：生产环境
- 激活：`spring.profiles.active=dev` 或 `--spring.profiles.active=prod`

**配置绑定**：`@Value` 注入单个值，`@ConfigurationProperties` 批量绑定到对象。

> 🔍 **知识点深度解析**
>
> **作用**：YAML 配置比 properties 更结构化，Profile 实现多环境配置分离（开发/测试/生产不同配置）。@ConfigurationProperties 实现类型安全的配置绑定。
>
> **原理**：Spring Boot 启动时加载 application.yml（或 properties），再根据 spring.profiles.active 加载对应的 application-{profile}.yml（后者覆盖前者）。配置属性通过 Environment 抽象，支持多种来源（优先级从高到低）：命令行参数 > 环境变量 > application-{profile}.yml > application.yml > 默认值。@ConfigurationProperties 通过 setter 方法或构造器绑定，支持类型转换、校验（@Validated）、元数据自动生成（IDE 提示）。YAML 用 SnakeYAML 解析，注意缩进（2空格）和列表语法。
>
> **用法要点**：① 生产用 YAML（结构化），简单配置用 properties 也可；② Profile 命名：dev/test/staging/prod；③ 激活 Profile：环境变量 SPRING_PROFILES_ACTIVE 或启动参数 --spring.profiles.active；④ @ConfigurationProperties 用于一组相关配置（如 spring.datasource.*），@Value 用于单个值；⑤ @ConfigurationProperties 配合 @Validated 做参数校验；⑥ 敏感配置（密码）用环境变量或配置中心（Nacos/Apollo），不要写在代码里；⑦ 配置优先级：命令行 > 环境变量 > 配置文件，了解优先级避免配置不生效的困惑。

### 2.5 Actuator 监控

**常用端点**：
- `/actuator/health`：健康检查（UP/DOWN）
- `/actuator/metrics`：指标（JVM、CPU、HTTP 请求）
- `/actuator/info`：应用信息
- `/actuator/env`：环境变量
- `/actuator/loggers`：日志级别动态调整

**安全**：生产环境只暴露必要端点，配合 Spring Security 认证。

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: when-authorized
```

> 🔍 **知识点深度解析**
>
> **作用**：Actuator 提供生产级监控能力（健康检查、指标、日志管理），是微服务可观测性的基础。配合 Prometheus + Grafana 实现完整监控体系。
>
> **原理**：Actuator 通过 Endpoint 暴露监控信息，每个 Endpoint 是一个被 @Endpoint 注解的 Bean，通过 HTTP 或 JMX 访问。健康检查（HealthEndpoint）聚合多个 HealthIndicator（DataSourceHealthIndicator、RedisHealthIndicator 等），任一 DOWN 则整体 DOWN。指标通过 Micrometer 门面抽象，支持 Prometheus/Graphite/InfluxDB 等多种后端。Prometheus 端点（/actuator/prometheus）暴露 Prometheus 格式的指标，Prometheus Server 定时抓取。
>
> **用法要点**：① 生产只暴露必要端点（health,info,metrics,prometheus），不要暴露 env/heapdump（敏感信息）；② 健康检查用于 K8s liveness/readiness 探针；③ 自定义 HealthIndicator 实现业务健康检查（如下游服务状态）；④ 自定义指标：MeterRegistry.counter/gauge/timer；⑤ 日志级别动态调整：POST /actuator/loggers/包名 {"configuredLevel":"DEBUG"}；⑥ Prometheus 格式：management.endpoints.web.exposure.include=prometheus；⑦ 安全：Actuator 端口独立（management.server.port）或 Spring Security 保护。

### 2.6 全局异常处理

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(BusinessException.class)
    public Result handleBusiness(BusinessException e) {
        return Result.fail(e.getCode(), e.getMessage());
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result handleValidation(MethodArgumentNotValidException e) {
        String msg = e.getBindingResult().getFieldErrors().stream()
            .map(FieldError::getDefaultMessage).collect(Collectors.joining(", "));
        return Result.fail("PARAM_ERROR", msg);
    }
    
    @ExceptionHandler(Exception.class)
    public Result handleException(Exception e) {
        log.error("系统异常", e);
        return Result.fail("SYSTEM_ERROR", "系统繁忙，请稍后重试");
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：全局异常处理统一管理异常响应格式，避免每个 Controller 写 try-catch。@RestControllerAdvice 是 AOP 切面，拦截所有 Controller 的异常。
>
> **原理**：@ControllerAdvice（@RestControllerAdvice = @ControllerAdvice + @ResponseBody）通过 ExceptionHandlerExceptionResolver 匹配 @ExceptionHandler 方法。当 Controller 抛出异常时，DispatcherServlet 调用 HandlerExceptionResolver 链，ExceptionHandlerExceptionResolver 查找 @ControllerAdvice 中匹配的 @ExceptionHandler 方法（按异常类型匹配，子类优先），调用该方法处理异常并返回响应。@ExceptionHandler 可以指定多个异常类型，方法参数支持 Exception、WebRequest、HttpServletRequest 等。
>
> **用法要点**：① 业务异常继承 RuntimeException（带 code 和 message）；② 参数校验异常（MethodArgumentNotValidException）单独处理，返回友好提示；③ 系统异常（Exception）兜底，返回通用错误信息（不暴露堆栈）；④ 记录日志：系统异常要 log.error，业务异常 log.warn 或不记；⑤ 统一响应格式：Result<T>（code/message/data）；⑥ 多个 @ControllerAdvice 用 @Order 控制优先级；⑦ 不要在异常处理中再抛异常（会导致 500）。

### 2.7 参数校验

```java
@Data
public class UserCreateRequest {
    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度3-20")
    private String username;
    
    @Email(message = "邮箱格式不正确")
    private String email;
    
    @NotNull(message = "年龄不能为空")
    @Min(value = 0, message = "年龄不能为负")
    @Max(value = 150, message = "年龄不合法")
    private Integer age;
}

@RestController
@RequestMapping("/users")
@Validated
public class UserController {
    @PostMapping
    public Result create(@RequestBody @Valid UserCreateRequest req) {
        // 校验失败自动抛 MethodArgumentNotValidException
        return Result.success();
    }
    
    @GetMapping("/{id}")
    public Result getById(@PathVariable @Min(1) Long id) {
        return Result.success();
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：参数校验在 Controller 层拦截非法参数，避免业务代码到处写 if 判断。JSR-303（Bean Validation）注解声明式校验，简洁优雅。
>
> **原理**：Spring Boot 引入 spring-boot-starter-validation（Hibernate Validator 实现）后，@Valid 或 @Validated 注解触发校验。@RequestBody 参数校验失败抛 MethodArgumentNotValidException，@RequestParam/@PathVariable 校验失败抛 ConstraintViolationException（需类上 @Validated）。校验通过 AOP（MethodValidationInterceptor）实现，校验器（Validator）根据注解（@NotNull/@NotBlank/@Email 等）检查字段值，不满足则收集错误信息抛出异常。自定义校验注解：@Constraint + ConstraintValidator 实现。
>
> **用法要点**：① @Valid 用于 @RequestBody 对象，@Validated 用于类（方法参数校验）和分组校验；② 字符串用 @NotBlank（非空且非空白），对象用 @NotNull，集合用 @NotEmpty；③ 自定义校验注解：@Constraint(validatedBy = XxxValidator.class)；④ 分组校验：@Validated(Group.Create.class) 实现不同场景不同规则；⑤ 校验失败统一由全局异常处理返回友好提示；⑥ 嵌套校验：对象字段加 @Valid；⑦ 不要用校验替代业务规则校验（如用户名是否已存在需查数据库）。

---


---
## 3. 常用用法

### 3.1 项目结构与启动类

```
src/main/java/com/example/app/
├── Application.java          # 启动类（@SpringBootApplication）
├── controller/               # 控制层
├── service/                  # 业务层
├── mapper/                   # 数据访问层
├── entity/                   # 实体类
├── dto/                      # 数据传输对象
├── config/                   # 配置类
├── exception/                # 异常定义
└── common/                   # 通用工具
src/main/resources/
├── application.yml           # 主配置
├── application-dev.yml       # 开发环境
├── application-prod.yml      # 生产环境
└── mapper/                   # MyBatis XML
```

```java
@SpringBootApplication
@MapperScan("com.example.app.mapper")
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：标准项目结构提高可维护性，启动类是应用入口。@SpringBootApplication 是组合注解，开启自动配置和组件扫描。
>
> **原理**：@SpringBootApplication = @SpringBootConfiguration（标记配置类）+ @EnableAutoConfiguration（开启自动配置）+ @ComponentScan（组件扫描，默认扫描启动类所在包及子包）。所以启动类要放在根包下（如 com.example.app），这样 controller/service/mapper 等子包都能被扫描到。@MapperScan 扫描 MyBatis Mapper 接口，生成代理 Bean。SpringApplication.run 启动流程：创建 SpringApplication → 准备 Environment → 创建 ApplicationContext → 刷新上下文（加载 Bean、启动内嵌服务器）→ 运行 CommandLineRunner。
>
> **用法要点**：① 启动类放在根包（com.example.app），不要放在子包；② 分层：controller（接收请求）→ service（业务逻辑）→ mapper（数据访问）；③ DTO 与 Entity 分离（不要把数据库实体直接返回前端）；④ 配置类放 config 包（@Configuration）；⑤ 启动类不要写业务逻辑；⑥ 多模块项目：启动类在 web 模块，其他模块被依赖；⑦ 启动失败看日志：常见是 Bean 冲突、自动配置排除、端口占用。

### 3.2 RESTful API 开发

```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;
    
    @GetMapping
    public Result<PageResult<UserVO>> list(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size) {
        return Result.success(userService.page(page, size));
    }
    
    @GetMapping("/{id}")
    public Result<UserVO> getById(@PathVariable Long id) {
        return Result.success(userService.getById(id));
    }
    
    @PostMapping
    public Result<Void> create(@RequestBody @Valid UserCreateRequest req) {
        userService.create(req);
        return Result.success();
    }
    
    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, 
                               @RequestBody @Valid UserUpdateRequest req) {
        userService.update(id, req);
        return Result.success();
    }
    
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        userService.delete(id);
        return Result.success();
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：RESTful API 用 HTTP 方法（GET/POST/PUT/DELETE）表示操作，URL 表示资源，是现代 Web API 的标准。统一响应格式（Result）便于前端处理。
>
> **原理**：@RestController = @Controller + @ResponseBody，方法返回值自动序列化为 JSON（Jackson）。@RequestMapping 定义基础 URL，@GetMapping/@PostMapping 等是组合注解（method + path）。@PathVariable 绑定 URL 路径变量，@RequestParam 绑定查询参数，@RequestBody 绑定请求体 JSON（HttpMessageConverter 反序列化）。参数名默认通过反射获取（Spring Boot 3.x 需 -parameters 编译参数，默认已配置）。分页用 Pageable 或自定义 page/size 参数。
>
> **用法要点**：① URL 用名词复数（/api/users），不用动词（/api/getUser）；② GET 查询、POST 创建、PUT 全量更新、PATCH 部分更新、DELETE 删除；③ 统一响应：Result<T> {code, message, data}；④ 分页参数：page 从1开始，size 默认10；⑤ @RequestBody 必须配合 POST/PUT，GET 不能用；⑥ 路径变量校验：@PathVariable @Min(1) Long id（类上 @Validated）；⑦ API 版本：URL 版本（/api/v1/users）或 Header 版本。

### 3.3 数据访问（Spring Data JPA / MyBatis）

```java
// Spring Data JPA
public interface UserRepository extends JpaRepository<User, Long> {
    // 方法名查询
    List<User> findByAgeGreaterThan(Integer age);
    Optional<User> findByUsername(String username);
    
    // @Query 自定义 JPQL
    @Query("SELECT u FROM User u WHERE u.status = :status")
    List<User> findByStatus(@Param("status") Integer status);
}

// MyBatis-Plus
public interface UserMapper extends BaseMapper<User> {
    @Select("SELECT * FROM user WHERE age > #{age}")
    List<User> selectByAge(@Param("age") Integer age);
}
```

> 🔍 **知识点深度解析**
>
> **作用**：数据访问层操作数据库，Spring Data JPA 适合简单 CRUD（方法名自动生成 SQL），MyBatis/MyBatis-Plus 适合复杂 SQL（手写 XML 灵活）。
>
> **原理**：Spring Data JPA：JpaRepository 提供基础 CRUD，方法名解析（findByXxxAndYyy）生成 JPQL，@Query 写自定义 JPQL/SQL。运行时通过动态代理生成 Repository 实现，Hibernate 执行 SQL。MyBatis：Mapper 接口通过动态代理（MapperProxy）映射 XML 或注解中的 SQL，SqlSession 执行。MyBatis-Plus 在 MyBatis 基础上封装 BaseMapper（内置 CRUD）和 IService（业务层封装），LambdaQueryWrapper 类型安全查询。
>
> **用法要点**：① 简单 CRUD 用 Spring Data JPA 或 MyBatis-Plus（减少样板代码）；② 复杂查询/多表关联用 MyBatis XML（SQL 可控）；③ 不要在 Repository/Mapper 写业务逻辑；④ 分页：JPA 用 Pageable，MyBatis-Plus 用 Page 对象+插件；⑤ 事务：@Transactional 在 Service 层（不是 Controller/Mapper）；⑥ N+1 问题：JPA 用 @EntityGraph 或 JOIN FETCH，MyBatis 用嵌套查询或 JOIN；⑦ 连接池：HikariCP（Spring Boot 默认，性能最好）。

### 3.4 事务管理

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderMapper orderMapper;
    private final InventoryMapper inventoryMapper;
    
    @Transactional(rollbackFor = Exception.class)
    public void createOrder(Order order) {
        orderMapper.insert(order);
        inventoryMapper.deduct(order.getProductId(), order.getQuantity());
        // 异常则回滚
    }
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logOperation(OperationLog log) {
        // 独立事务，不受外部事务影响
        operationLogMapper.insert(log);
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：声明式事务通过 @Transactional 自动管理事务（开启/提交/回滚），不需要手动写 try-catch-commit-rollback。是数据一致性的基础。
>
> **原理**：@Transactional 基于 Spring AOP（动态代理），TransactionInterceptor 拦截方法：方法前开启事务（DataSourceTransactionManager 绑定 Connection 到 ThreadLocal），方法正常结束提交，异常则回滚。传播行为（Propagation）：REQUIRED（默认，有事务则加入，没有则新建）、REQUIRES_NEW（新建独立事务，挂起当前）、NESTED（嵌套事务，savepoint）。默认只回滚 RuntimeException，rollbackFor=Exception.class 让受检异常也回滚。
>
> **用法要点**：① @Transactional 在 Service 层（public 方法），不要在 Controller/私有方法；② rollbackFor = Exception.class（默认只回滚 RuntimeException，受检异常不回滚）；③ 同类内调用不生效（AOP 代理问题，用 self 注入或拆类）；④ try-catch 吞异常不回滚（需手动 setRollbackOnly 或重抛）；⑤ 只读事务：@Transactional(readOnly=true) 优化（不能写操作）；⑥ 传播行为：REQUIRES_NEW 用于日志（独立事务，主事务回滚不影响日志）；⑦ 事务不要跨远程调用（分布式事务用 Seata/MQ）。

### 3.5 日志配置

```yaml
logging:
  level:
    root: INFO
    com.example.app: DEBUG
    org.springframework.web: INFO
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"
  file:
    name: logs/app.log
  logback:
    rollingpolicy:
      max-file-size: 100MB
      max-history: 30
      total-size-cap: 10GB
```

> 🔍 **知识点深度解析**
>
> **作用**：日志是排查问题的核心手段。Spring Boot 默认 Logback，配置日志级别、格式、文件滚动。合理的日志配置便于生产排查。
>
> **原理**：Spring Boot 默认用 Logback（spring-boot-starter-logging 引入），也支持 Log4j2（排除 logback 引入 log4j2）。日志级别从高到低：ERROR > WARN > INFO > DEBUG > TRACE，设置某级别后该级别及以上输出。日志通过 MDC（Mapped Diagnostic Context）传递 TraceID（Sleuth 自动设置）。文件滚动：RollingFileAppender 按大小（max-file-size）和时间滚动，保留历史（max-history），总大小限制（total-size-cap）。
>
> **用法要点**：① 生产 root 级别 INFO，业务包 DEBUG（便于排查），第三方包 WARN/INFO（减少噪音）；② 日志格式包含时间、线程、级别、类名、消息；③ 生产输出到文件并滚动（按大小+时间），不要只输出控制台；④ 敏感信息（密码、Token、身份证）不要打日志；⑤ 异常日志用 log.error("msg", e)（带堆栈），不要 log.error(e.getMessage())；⑥ 动态调整日志级别：Actuator /actuator/loggers；⑦ 微服务用 ELK/Loki 集中收集日志，TraceID 串联。

### 3.6 单元测试与集成测试

```java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerTest {
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void shouldReturnUserList() throws Exception {
        mockMvc.perform(get("/api/users").param("page", "1").param("size", "10"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.code").value(0))
            .andExpect(jsonPath("$.data.records").isArray());
    }
}

// Service 层单元测试（Mockito）
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock
    private UserMapper userMapper;
    @InjectMocks
    private UserServiceImpl userService;
    
    @Test
    void shouldCreateUser() {
        when(userMapper.insert(any())).thenReturn(1);
        userService.create(new UserCreateRequest());
        verify(userMapper).insert(any());
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：测试保证代码质量和重构安全。单元测试（Mockito）测 Service 逻辑（不依赖数据库），集成测试（@SpringBootTest）测完整流程（Controller→Service→DB）。
>
> **原理**：@SpringBootTest 启动完整 Spring 上下文（加载所有 Bean），@AutoConfigureMockMvc 注入 MockMvc（模拟 HTTP 请求，不启动真实服务器）。@WebMvcTest 只加载 Web 层（Controller），配合 @MockBean Mock Service。Mockito：@Mock 创建代理对象，when().thenReturn() 定义行为，verify() 验证调用。@InjectMocks 自动注入 Mock 到被测对象。Testcontainers 启动真实数据库容器做集成测试（比 H2 更接近生产）。
>
> **用法要点**：① Service 层用单元测试（Mockito，快，不依赖外部）；② Controller 层用 @WebMvcTest + @MockBean；③ 完整流程用 @SpringBootTest + Testcontainers（真实数据库）；④ 测试命名：should_预期行为_When_条件；⑤ 断言用 AssertJ（fluent API）或 JUnit 5；⑥ 不要测试框架本身（如 Spring 的功能），只测业务逻辑；⑦ 测试要独立（不依赖执行顺序，每个测试前清理数据）；⑧ 覆盖率：核心业务 70%+，不要追求 100%。

### 3.7 打包与部署

```bash

> 🔍 **知识点深度解析**
>
> **作用**：Spring Boot 打包为可执行 JAR/WAR，通过 java -jar 或容器部署，支持多环境配置。
>
> **原理**：spring-boot-maven-plugin 将应用打包为 fat JAR（内嵌 Tomcat），java -jar app.jar 启动。可执行 JAR 内部用 JarLauncher 加载 BOOT-INF/classes 和 BOOT-INF/lib。多环境用 --spring.profiles.active=prod 指定。Docker 部署用 eclipse-temurin/jre 基础镜像，分层构建优化镜像缓存。JVM 参数通过 JAVA_OPTS 环境变量传递。
>
> **用法要点**：① mvn package 打 fat JAR，java -jar 启动  ② java -jar app.jar --spring.profiles.active=prod  ③ Docker 分层构建：依赖层和应用层分离，利用缓存  ④ JVM 参数：-Xms/-Xmx/-XX:+UseG1GC，通过 JAVA_OPTS 传入  ⑤ 面试常考：fat JAR 原理、JarLauncher、多环境部署、Docker 最佳实践

# Maven 打包
mvn clean package -DskipTests
# 运行
java -jar target/app-1.0.0.jar
# 指定 Profile
java -jar target/app-1.0.0.jar --spring.profiles.active=prod
# 指定 JVM 参数
java -Xms512m -Xmx1024m -jar target/app-1.0.0.jar

# Dockerfile
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY target/app-1.0.0.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

> 🔍 **知识点深度解析**
>
> **作用**：Spring Boot 打包为可执行 JAR（内嵌服务器），java -jar 直接运行。Docker 容器化部署是云原生标准。
>
> **原理**：spring-boot-maven-plugin 的 repackage 目标将普通 JAR 重新打包为可执行 JAR（fat jar），包含所有依赖和 Spring Boot Loader。JAR 内结构：BOOT-INF/classes（业务类）、BOOT-INF/lib（依赖 JAR）、META-INF（MANIFEST.MF 指定 Main-Class=JarLauncher）。java -jar 启动时，JarLauncher 加载 BOOT-INF/classes 和 BOOT-INF/lib，然后调用主类的 main 方法。Docker 多阶段构建：第一阶段 Maven 构建 JAR，第二阶段 JRE 运行（镜像更小）。
>
> **用法要点**：① 生产用 java -jar 或 Docker，不要用 IDE 启动；② JVM 参数：-Xms=-Xmx（避免动态扩容），容器环境用 -XX:MaxRAMPercentage=75（自适应容器内存）；③ Spring Boot 3.x 需 Java 17+；④ Docker 用多阶段构建（builder 阶段 + runtime 阶段）；⑤ 健康检查：Docker HEALTHCHECK 或 K8s liveness/readiness 探针（调 /actuator/health）；⑥ 优雅停机：Docker stop 发 SIGTERM，Spring Boot 3.x 默认支持；⑦ 不要在镜像中用 root 用户运行（安全）。

### 3.8 常用配置项

```yaml
server:
  port: 8080
  servlet:
    context-path: /api
  tomcat:
    threads:
      max: 200
    accept-count: 100
  shutdown: graceful

spring:
  application:
    name: order-service
  datasource:
    url: jdbc:mysql://localhost:3306/app?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
    username: root
    password: ${DB_PASSWORD}
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
  data:
    redis:
      host: localhost
      port: 6379
      password: ${REDIS_PASSWORD}
      lettuce:
        pool:
          max-active: 20
          max-idle: 10

mybatis-plus:
  mapper-locations: classpath:mapper/*.xml
  configuration:
    map-underscore-to-camel-case: true
  global-config:
    db-config:
      logic-delete-field: deleted
      logic-delete-value: 1
      logic-not-delete-value: 0
```

> 🔍 **知识点深度解析**
>
> **作用**：常用配置项覆盖服务器、数据源、Redis、MyBatis 等核心组件。掌握这些配置是 Spring Boot 开发的基础。
>
> **原理**：配置项通过 @ConfigurationProperties 绑定到对应自动配置类的属性。如 spring.datasource.* 绑定到 DataSourceProperties，HikariCP 参数绑定到 HikariDataSource。环境变量占位符 ${DB_PASSWORD} 从环境变量读取（12-factor 推荐，敏感配置不写在文件里）。下划线转驼峰（map-underscore-to-camel-case）自动映射数据库列名（user_name）到 Java 属性（userName）。逻辑删除（logic-delete-field）自动将 DELETE 转为 UPDATE deleted=1，查询自动加 WHERE deleted=0。
>
> **用法要点**：① 数据库密码用环境变量（${DB_PASSWORD}），不要明文写在配置文件；② HikariCP 连接池：maximum-pool-size 根据数据库承载能力（通常 10-30）；③ Redis 用 Lettuce（默认，非阻塞），高并发配连接池；④ 逻辑删除：全局配置后自动处理，不需要手写；⑤ 服务名 spring.application.name 是微服务注册和配置中心的标识；⑥ context-path 统一 API 前缀（/api）；⑦ 配置文件敏感信息用配置中心（Nacos/Apollo）管理，不要提交到 Git。

---


---
## 4. 注意事项

1. **启动类位置**：必须放在根包下（如 com.example.app），否则子包的 Bean 不会被扫描到。

2. **事务不生效场景**：同类内调用（AOP 代理不生效）、非 public 方法、try-catch 吞异常、默认不回滚受检异常。

3. **自动配置被覆盖**：用户定义的 Bean 会覆盖自动配置的 Bean（@ConditionalOnMissingBean），排查问题时注意。

4. **配置优先级**：命令行参数 > 环境变量 > application-{profile}.yml > application.yml。配置不生效时检查优先级。

5. **循环依赖**：Spring Boot 2.6+ 默认禁止循环依赖。用 @Lazy 或重构解决，不要依赖循环依赖。

6. **大文件上传**：默认 1MB，需配置 spring.servlet.multipart.max-file-size 和 max-request-size。

7. **日期格式化**：全局配置 spring.jackson.date-format=yyyy-MM-dd HH:mm:ss 和 time-zone=Asia/Shanghai，避免每个字段加 @JsonFormat。

8. **Actuator 安全**：生产不要暴露 env、heapdump、threaddump 等敏感端点，只暴露 health、info、metrics、prometheus。

9. **日志敏感信息**：密码、Token、身份证、手机号不要打日志。用脱敏工具或日志脱敏组件。

10. **依赖版本冲突**：用 mvn dependency:tree 排查，排除冲突依赖。Spring Boot BOM 管理的版本不要随意覆盖。

11. **异步方法**：@Async 需要 @EnableAsync，且不能在同类内调用（AOP 代理问题）。返回值用 Future/CompletableFuture。

12. **生产 JVM 参数**：-Xms=-Xmx（避免动态扩容）、-XX:+UseG1GC（JDK 9+ 默认）、-XX:+HeapDumpOnOutOfMemoryError（OOM 时 dump）。

---

> 💡 **深度讲解**：Spring Boot 的核心是"约定优于配置"，通过自动配置（@EnableAutoConfiguration + 条件注解）、起步依赖（Starter POM 聚合依赖）、内嵌服务器（Tomcat/Jetty/Undertow）三大特性，让 Spring 应用开箱即用。自动配置原理是面试高频考点：通过 AutoConfiguration.imports 加载自动配置类，用 @ConditionalOnClass/@ConditionalOnMissingBean 等条件注解控制是否生效，用户 Bean 优先。开发 RESTful API 用 @RestController + HTTP 方法语义，参数校验用 JSR-303 注解，全局异常用 @RestControllerAdvice 统一处理。数据访问选 Spring Data JPA（简单 CRUD）或 MyBatis-Plus（复杂 SQL），事务用 @Transactional（注意 rollbackFor 和同类调用问题）。生产环境配置 Actuator 监控（配合 Prometheus+Grafana）、合理日志配置（文件滚动+敏感信息脱敏）、优雅停机。部署用可执行 JAR 或 Docker，JVM 参数根据容器资源调整。理解了自动配置原理和 AOP 代理机制（事务/异步/缓存的坑），就能高效开发和快速排查 Spring Boot 问题。
>
> **📝 精简总结**：Spring Boot=自动配置+起步依赖+内嵌服务器；自动配置=@EnableAutoConfiguration+条件注解(@ConditionalOnClass/MissingBean)；Web=@RestController+RESTful+@Valid校验+@RestControllerAdvice异常；数据=JPA(简单)/MyBatis-Plus(复杂)+HikariCP；事务=@Transactional(rollbackFor=Exception,注意同类调用)；监控=Actuator+Prometheus+Grafana；部署=fat jar java -jar/Docker；坑=启动类位置/事务不生效/配置优先级/循环依赖。

---

> 📋 **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 知识点深度解析」模块（作用+原理+用法要点），原有内联图已统一风格化美化（圆角、阴影、渐变、动画）。所有原有内容完整保留，未做任何修改。
