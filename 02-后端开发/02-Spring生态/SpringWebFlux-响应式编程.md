---
title: SpringWebFlux-响应式编程
tags: [Java, WebFlux, 响应式编程, Reactor, 原子笔记]
category: 后端开发
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["SpringBoot-Web层设计", "Java-并发编程JUC", "Spring-IOCAOP核心机制"]
aliases: [SpringWebFlux-响应式编程]
---

# SpringWebFlux-响应式编程

> **文档说明**：系统讲解 Spring WebFlux 响应式编程框架，包括响应式编程原理、Reactor 核心（Mono/Flux）、WebFlux 架构、Controller 实现、响应式数据访问、WebClient、响应式安全、背压与性能优化，以及与 Spring MVC 的对比和最佳实践。
>
> **适用人群**：后端开发工程师、Java 开发者、需要构建高并发响应式系统的架构师
>
> **前置知识**：[[SpringBoot-Web层设计]]、[[Java-并发编程JUC]]、[[Spring-IOCAOP核心机制]]、[[Java函数式编程与Stream]]

---

## 一、概述

### 1. 什么是响应式编程

**响应式编程（Reactive Programming）** 是一种基于异步数据流和变化传播的编程范式，通过声明式方式处理异步数据流，支持非阻塞、背压、弹性的系统构建。

### 2. 响应式宣言（Reactive Manifesto）

| 特性 | 说明 |
|------|------|
| **即时响应（Responsive）** | 系统能及时响应请求 |
| **回弹性（Resilient）** | 系统在故障时仍能响应 |
| **弹性（Elastic）** | 系统能根据负载自动伸缩 |
| **消息驱动（Message Driven）** | 组件间通过异步消息通信 |

### 3. Reactive Streams 规范

```
Reactive Streams 四大接口：
- Publisher：数据发布者，发出数据流
- Subscriber：数据订阅者，接收数据流
- Subscription：订阅关系，控制请求量（背压）
- Processor：同时是 Publisher 和 Subscriber
```

### 4. Spring WebFlux vs Spring MVC

| 维度 | Spring MVC | Spring WebFlux |
|------|-----------|----------------|
| **编程模型** | 命令式、同步阻塞 | 声明式、异步非阻塞 |
| **运行容器** | Servlet 容器（Tomcat/Jetty） | Netty（默认）/ Servlet 3.1+ |
| **线程模型** | 每请求一线程 | 少量线程 + 事件循环 |
| **并发能力** | 受线程池大小限制 | 少量线程处理高并发 |
| **背压支持** | 不支持 | 原生支持 |
| **适用场景** | 传统 CRUD、阻塞 IO | 高并发、流式、长连接 |
| **学习曲线** | 平缓 | 较陡 |
| **生态成熟度** | 非常成熟 | 成熟但部分库不支持 |

### 5. 什么时候用 WebFlux

- [ ] **高并发 IO 密集型**：大量外部 API 调用、数据库查询
- [ ] **流式数据**：SSE、WebSocket、AI 流式输出
- [ ] **非阻塞管道**：网关、代理、实时推送
- [ ] **资源受限**：少量硬件处理大量并发
- [ ] **不适合**：CPU 密集型计算、大量阻塞操作（JDBC）

---

## 二、Reactor 核心

### 1. Mono 和 Flux

```
Reactor 两种核心类型：
- Mono<T>：发出 0 或 1 个元素的异步序列
- Flux<T>：发出 0 到 N 个元素的异步序列

Mono<String>  → 单个结果（查询单条记录、HTTP 响应）
Flux<String>  → 多个结果（列表查询、数据流）
```

```java
// Mono 示例
Mono<String> mono = Mono.just("Hello");
Mono<User> userMono = userRepository.findById(1L);
Mono.empty();  // 空结果
Mono.error(new RuntimeException("出错了"));  // 错误

// Flux 示例
Flux<String> flux = Flux.just("A", "B", "C");
Flux<Integer> range = Flux.range(1, 100);
Flux<User> users = userRepository.findAll();
Flux.interval(Duration.ofSeconds(1));  // 定时发射
```

### 2. 核心操作符

#### 创建操作符

```java
// 从值创建
Flux.just("a", "b", "c");
Mono.just("hello");

// 从集合创建
Flux.fromIterable(List.of("a", "b", "c"));
Flux.fromArray(new String[]{"a", "b"});
Flux.fromStream(() -> Stream.of("a", "b"));

// 从其他类型创建
Mono.fromCallable(() -> heavyOperation());
Mono.fromRunnable(() -> cleanup());
Flux.from(Mono.just("a"));

// 延迟创建
Mono.defer(() -> Mono.just(LocalDateTime.now().toString()));
Flux.defer(() -> Flux.fromIterable(queryFromDB()));

// 空/错误
Mono.empty();
Mono.error(new RuntimeException("error"));
Flux.never();  // 永不结束
```

#### 转换操作符

```java
Flux<Integer> numbers = Flux.just(1, 2, 3, 4, 5);

// map：同步转换
numbers.map(n -> n * 2);  // 2, 4, 6, 8, 10

// flatMap：异步转换（合并内部流，无序）
numbers.flatMap(n -> Mono.just(n * 2).delayElement(Duration.ofMillis(100)));

// concatMap：异步转换（保持顺序）
numbers.concatMap(n -> Mono.just(n * 2).delayElement(Duration.ofMillis(100)));

// flatMapSequential：异步转换（按顺序输出）
numbers.flatMapSequential(n -> Mono.just(n * 2));

// filter：过滤
numbers.filter(n -> n % 2 == 0);  // 2, 4

// take：取前 N 个
numbers.take(3);  // 1, 2, 3

// skip：跳过前 N 个
numbers.skip(2);  // 3, 4, 5

// distinct：去重
Flux.just(1, 1, 2, 2, 3).distinct();  // 1, 2, 3

// buffer：缓冲为集合
numbers.buffer(2);  // [1,2], [3,4], [5]

// groupBy：分组
Flux.just(1, 2, 3, 4, 5).groupBy(n -> n % 2 == 0 ? "even" : "odd");
```

#### 组合操作符

```java
Flux<String> flux1 = Flux.just("a", "b", "c");
Flux<String> flux2 = Flux.just("d", "e", "f");

// merge：合并（按时间交错）
Flux.merge(flux1, flux2);  // a, d, b, e, c, f（取决于发射时间）

// concat：连接（按顺序）
Flux.concat(flux1, flux2);  // a, b, c, d, e, f

// zip：配对组合
Flux.zip(flux1, flux2, (a, b) -> a + b);  // ad, be, cf

// combineLatest：组合最新值
Flux.combineLatest(flux1, flux2, (a, b) -> a + b);

// startWith：前置元素
flux1.startWith("start");  // start, a, b, c
```

#### 错误处理操作符

```java
Mono<String> risky = riskyOperation();

// onErrorReturn：出错返回默认值
risky.onErrorReturn("default value");

// onErrorResume：出错切换到备用流
risky.onErrorResume(e -> fallbackOperation());

// onErrorMap：转换错误类型
risky.onErrorMap(original -> new BusinessException("包装错误", original));

// doOnError：副作用（不改变流）
risky.doOnError(e -> log.error("出错了", e));

// retry：重试
risky.retry(3);  // 重试 3 次
risky.retryWhen(Retry.backoff(3, Duration.ofSeconds(1)));  // 退避重试

// timeout：超时
risky.timeout(Duration.ofSeconds(5));
```

#### 副作用操作符

```java
flux
    .doOnSubscribe(sub -> log.info("开始订阅"))
    .doOnNext(item -> log.info("收到元素: {}", item))
    .doOnComplete(() -> log.info("流完成"))
    .doOnError(e -> log.error("流出错", e))
    .doOnCancel(() -> log.info("订阅被取消"))
    .doFinally(signal -> log.info("最终信号: {}", signal));
```

### 3. 背压（Backpressure）

```java
// 背压策略
Flux.range(1, 1000)
    .onBackpressureBuffer(100)  // 缓冲 100 个元素
    .onBackpressureDrop()       // 丢弃溢出元素
    .onBackpressureLatest()     // 只保留最新元素
    .onBackpressureError();     // 溢出时报错

// 订阅时指定请求量
flux.subscribe(
    item -> process(item),
    error -> handleError(error),
    () -> complete(),
    subscription -> subscription.request(10)  // 每次请求 10 个
);
```

---

## 三、Spring WebFlux Controller

### 1. 注解式 Controller

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserRepository userRepository;

    // 查询单个用户 → Mono
    @GetMapping("/{id}")
    public Mono<User> getUser(@PathVariable Long id) {
        return userRepository.findById(id)
            .switchIfEmpty(Mono.error(new NotFoundException("用户不存在")));
    }

    // 查询用户列表 → Flux
    @GetMapping
    public Flux<User> listUsers() {
        return userRepository.findAll();
    }

    // 创建用户 → Mono
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Mono<User> createUser(@Valid @RequestBody Mono<User> userMono) {
        return userMono.flatMap(userRepository::save);
    }

    // 更新用户
    @PutMapping("/{id}")
    public Mono<User> updateUser(@PathVariable Long id,
                                  @RequestBody Mono<User> userMono) {
        return userRepository.findById(id)
            .switchIfEmpty(Mono.error(new NotFoundException()))
            .flatMap(existing -> userMono.flatMap(user -> {
                existing.setName(user.getName());
                return userRepository.save(existing);
            }));
    }

    // 删除用户
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public Mono<Void> deleteUser(@PathVariable Long id) {
        return userRepository.deleteById(id);
    }

    // SSE 流式响应
    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<User> streamUsers() {
        return userRepository.findAll()
            .delayElements(Duration.ofSeconds(1));
    }
}
```

### 2. 函数式端点（Functional Endpoints）

```java
@Configuration
public class UserRouter {

    @Bean
    public RouterFunction<ServerResponse> userRoutes(UserHandler handler) {
        return RouterFunctions.route()
            .GET("/api/users", handler::list)
            .GET("/api/users/{id}", handler::get)
            .POST("/api/users", handler::create)
            .PUT("/api/users/{id}", handler::update)
            .DELETE("/api/users/{id}", handler::delete)
            .build();
    }
}

@Component
public class UserHandler {

    @Autowired
    private UserRepository userRepository;

    public Mono<ServerResponse> list(ServerRequest request) {
        Flux<User> users = userRepository.findAll();
        return ServerResponse.ok().body(users, User.class);
    }

    public Mono<ServerResponse> get(ServerRequest request) {
        Long id = Long.valueOf(request.pathVariable("id"));
        return userRepository.findById(id)
            .flatMap(user -> ServerResponse.ok().bodyValue(user))
            .switchIfEmpty(ServerResponse.notFound().build());
    }

    public Mono<ServerResponse> create(ServerRequest request) {
        Mono<User> userMono = request.bodyToMono(User.class);
        return userMono
            .flatMap(userRepository::save)
            .flatMap(user -> ServerResponse.created(
                URI.create("/api/users/" + user.getId())).bodyValue(user));
    }
}
```

### 3. 全局异常处理

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(NotFoundException.class)
    public Mono<ResponseEntity<ErrorResponse>> handleNotFound(NotFoundException ex) {
        return Mono.just(ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("NOT_FOUND", ex.getMessage())));
    }

    @ExceptionHandler(WebExchangeBindException.class)
    public Mono<ResponseEntity<ErrorResponse>> handleValidation(WebExchangeBindException ex) {
        String message = ex.getBindingResult().getFieldErrors().stream()
            .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
            .collect(Collectors.joining(", "));
        return Mono.just(ResponseEntity.badRequest()
            .body(new ErrorResponse("VALIDATION_ERROR", message)));
    }
}
```

---

## 四、响应式数据访问

### 1. R2DBC（响应式数据库）

```java
// R2DBC 配置
@Configuration
public class R2dbcConfig extends AbstractR2dbcConfiguration {

    @Bean
    public ConnectionFactory connectionFactory() {
        return ConnectionFactories.get(
            "r2dbcs:mysql://user:password@localhost:3306/mydb");
    }
}

// 响应式 Repository
public interface UserRepository extends ReactiveCrudRepository<User, Long> {
    Flux<User> findByName(String name);
    Mono<User> findByEmail(String email);
    @Query("SELECT * FROM users WHERE age > $1")
    Flux<User> findByAgeGreaterThan(int age);
}

// 响应式事务
@Service
public class UserService {

    @Transactional
    public Mono<User> createUserWithLog(User user) {
        return userRepository.save(user)
            .flatMap(saved -> logRepository.save(new Log("创建用户: " + saved.getId()))
                .then(Mono.just(saved)));
    }
}
```

### 2. 响应式 Redis

```java
@Configuration
public class RedisConfig {

    @Bean
    public ReactiveRedisTemplate<String, Object> reactiveRedisTemplate(
            ReactiveRedisConnectionFactory factory) {
        Jackson2JsonRedisSerializer<Object> serializer =
            new Jackson2JsonRedisSerializer<>(Object.class);
        RedisSerializationContext<String, Object> context =
            RedisSerializationContext.<String, Object>newSerializationContext(
                new StringRedisSerializer())
                .value(serializer)
                .build();
        return new ReactiveRedisTemplate<>(factory, context);
    }
}

@Service
public class CacheService {

    @Autowired
    private ReactiveRedisTemplate<String, Object> redisTemplate;

    public Mono<User> getUserWithCache(Long id) {
        String key = "user:" + id;
        return redisTemplate.opsForValue().get(key)
            .cast(User.class)
            .switchIfEmpty(
                userRepository.findById(id)
                    .flatMap(user -> redisTemplate.opsForValue()
                        .set(key, user, Duration.ofMinutes(10))
                        .thenReturn(user))
            );
    }
}
```

### 3. 响应式 MongoDB

```java
public interface UserRepository extends ReactiveMongoRepository<User, String> {
    Flux<User> findByAgeGreaterThan(int age);
    Mono<User> findByEmail(String email);
}
```

---

## 五、WebClient 响应式 HTTP 客户端

### 1. 基础使用

```java
@Configuration
public class WebClientConfig {

    @Bean
    public WebClient webClient() {
        return WebClient.builder()
            .baseUrl("https://api.example.com")
            .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
            .defaultCookie("cookie-name", "cookie-value")
            .filter(ExchangeFilterFunctions.basicAuthentication("user", "pass"))
            .build();
    }
}

@Service
public class ApiService {

    @Autowired
    private WebClient webClient;

    // GET 请求
    public Mono<User> getUser(Long id) {
        return webClient.get()
            .uri("/users/{id}", id)
            .retrieve()
            .bodyToMono(User.class);
    }

    // POST 请求
    public Mono<User> createUser(User user) {
        return webClient.post()
            .uri("/users")
            .bodyValue(user)
            .retrieve()
            .onStatus(HttpStatusCode::is4xxClientError,
                response -> Mono.error(new ClientException()))
            .onStatus(HttpStatusCode::is5xxServerError,
                response -> Mono.error(new ServerException()))
            .bodyToMono(User.class);
    }

    // 流式响应（SSE）
    public Flux<UserEvent> streamEvents() {
        return webClient.get()
            .uri("/events/stream")
            .retrieve()
            .bodyToFlux(UserEvent.class);
    }

    // 并行调用
    public Mono<UserDetail> getUserDetail(Long id) {
        Mono<User> userMono = getUser(id);
        Mono<List<Order>> ordersMono = getOrders(id).collectList();
        return Mono.zip(userMono, ordersMono,
            (user, orders) -> new UserDetail(user, orders));
    }
}
```

### 2. 重试与超时

```java
public Mono<User> getUserWithRetry(Long id) {
    return webClient.get()
        .uri("/users/{id}", id)
        .retrieve()
        .bodyToMono(User.class)
        .timeout(Duration.ofSeconds(5))
        .retryWhen(Retry.backoff(3, Duration.ofSeconds(1))
            .maxBackoff(Duration.ofSeconds(10))
            .filter(ex -> ex instanceof WebClientRequestException
                || ex instanceof TimeoutException));
}
```

---

## 六、响应式安全

### 1. Spring Security WebFlux

```java
@Configuration
@EnableWebFluxSecurity
public class SecurityConfig {

    @Bean
    public SecurityWebFilterChain securityWebFilterChain(ServerHttpSecurity http) {
        return http
            .csrf(csrf -> csrf.disable())
            .authorizeExchange(exchanges -> exchanges
                .pathMatchers("/api/public/**").permitAll()
                .pathMatchers("/api/admin/**").hasRole("ADMIN")
                .anyExchange().authenticated()
            )
            .httpBasic(Customizer.withDefaults())
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
            .build();
    }

    @Bean
    public ReactiveUserDetailsService userDetailsService() {
        UserDetails user = User.withUsername("user")
            .password("{noop}password")
            .roles("USER")
            .build();
        return new MapReactiveUserDetailsService(user);
    }
}
```

### 2. 获取当前用户

```java
@GetMapping("/me")
public Mono<User> getCurrentUser() {
    return ReactiveSecurityContextHolder.getContext()
        .map(ctx -> ctx.getAuthentication().getPrincipal())
        .cast(User.class);
}
```

---

## 七、性能优化

### 1. 线程模型

```
WebFlux 默认线程模型：
- Netty EventLoop：CPU 核心数个线程（如 8 核 = 8 线程）
- 所有非阻塞操作在 EventLoop 上执行
- 阻塞操作必须切换到弹性线程池

关键：不要在 EventLoop 上执行阻塞操作！
```

### 2. 避免阻塞操作

```java
// ❌ 错误：在响应式流中调用阻塞方法
public Mono<User> getUser(Long id) {
    User user = jdbcTemplate.queryForObject(...);  // 阻塞！
    return Mono.just(user);
}

// ✅ 正确：使用响应式驱动或切换线程池
public Mono<User> getUser(Long id) {
    return Mono.fromCallable(() -> jdbcTemplate.queryForObject(...))
        .subscribeOn(Schedulers.boundedElastic());  // 切换到弹性线程池
}

// ✅ 最佳：使用 R2DBC 响应式驱动
public Mono<User> getUser(Long id) {
    return r2dbcRepository.findById(id);  // 非阻塞
}
```

### 3. 调度器（Scheduler）

```java
// publishOn：影响后续操作的线程
flux.publishOn(Schedulers.parallel())
    .map(this::cpuIntensiveTask)  // 在 parallel 线程执行
    .publishOn(Schedulers.boundedElastic())
    .map(this::ioTask);  // 在 boundedElastic 线程执行

// subscribeOn：影响整个流的订阅线程
Mono.fromCallable(this::blockingOperation)
    .subscribeOn(Schedulers.boundedElastic());

// 常用调度器
Schedulers.parallel();          // 并行计算，CPU 核心数线程
Schedulers.boundedElastic();    // 弹性线程池，适合 IO 阻塞
Schedulers.single();            // 单线程
Schedulers.immediate();         // 当前线程
Schedulers.newParallel("custom", 4);  // 自定义并行调度器
```

### 4. 缓存与热流

```java
// 缓存结果（避免重复订阅）
Mono<User> cachedUser = userRepository.findById(1L)
    .cache(Duration.ofMinutes(10));  // 缓存 10 分钟

// 热流：多个订阅者共享同一个流
Flux<Long> hotFlux = Flux.interval(Duration.ofSeconds(1))
    .publish()  // 变成 ConnectableFlux
    .autoConnect();  // 第一个订阅者时自动连接
```

---

## 八、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **响应慢/阻塞** | EventLoop 上执行了阻塞操作 | 使用 R2DBC、subscribeOn 切换线程 |
| **内存溢出** | 背压未处理 / 无界缓冲 | 配置背压策略、限制 buffer 大小 |
| **数据不返回** | 流未被订阅（冷流） | 确保调用 subscribe 或返回给框架 |
| **事务不生效** | 响应式事务配置问题 | 使用 @Transactional + R2DBC |
| **上下文丢失** | 线程切换导致上下文丢失 | 使用 Reactor Context、正确的调度器 |
| **错误被吞掉** | 未处理 onError | 添加 doOnError、onErrorResume |
| **重复请求** | Mono/Flux 被多次订阅 | 使用 cache()、share() |
| **WebClient 超时** | 默认无超时 | 配置 timeout、responseTimeout |
| **SSE 连接断开** | 代理超时 / 无心跳 | Nginx 配置、发送心跳 |
| **线程数暴涨** | 滥用 boundedElastic | 合理使用调度器、控制并发 |
| **测试困难** | 异步测试复杂 | 使用 StepVerifier、reactor-test |
| **调试困难** | 异步堆栈不直观 | 使用 checkpoint()、Hooks.onOperatorDebug |
| **JDBC 不兼容** | JDBC 是阻塞的 | 使用 R2DBC 或 subscribeOn 包装 |
| **安全上下文丢失** | 响应式安全上下文传播 | 使用 ReactiveSecurityContextHolder |
| **性能不如 MVC** | 误用响应式（CPU 密集/阻塞） | 评估场景，适合 IO 密集型才用 WebFlux |

### 调试技巧

```java
// 启用调试模式（开发环境）
Hooks.onOperatorDebug();

// 使用 checkpoint 标记关键节点
userRepository.findById(id)
    .checkpoint("查询用户")
    .flatMap(this::enrichUser)
    .checkpoint("丰富用户信息")
    .switchIfEmpty(Mono.error(new NotFoundException()));

// 测试工具 StepVerifier
StepVerifier.create(flux)
    .expectNext("a", "b", "c")
    .expectComplete()
    .verify();

StepVerifier.create(errorMono)
    .expectError(RuntimeException.class)
    .verify();
```

---

## 九、最佳实践

### 1. 编码规范

- [ ] **返回 Mono/Flux**：Controller 方法返回响应式类型，不要 block()
- [ ] **避免 block()**：除测试外，不要调用 block()/subscribe()
- [ ] **错误处理**：每个外部调用都要有错误处理和重试
- [ ] **超时控制**：所有外部调用设置超时
- [ ] **背压处理**：数据流考虑背压策略
- [ ] **上下文传播**：使用 Reactor Context 传递请求上下文
- [ ] **日志规范**：使用 doOnNext/doOnError 记录关键日志

### 2. 架构规范

- [ ] **分层清晰**：Controller → Service → Repository，每层返回响应式类型
- [ ] **响应式全链路**：从 Controller 到数据库全链路非阻塞
- [ ] **混合使用谨慎**：MVC 和 WebFlux 不要混用在同一应用
- [ ] **网关场景**：API 网关优先考虑 WebFlux（高并发代理）
- [ ] **AI 流式输出**：WebFlux + SSE 是 AI 流式输出的最佳组合

### 3. 性能规范

- [ ] **不阻塞 EventLoop**：阻塞操作必须切换线程
- [ ] **合理并发**：使用 flatMap 控制并发度（flatMap(fn, concurrency)）
- [ ] **缓存热点**：热点数据使用 cache() 或 Redis
- [ ] **批量操作**：数据库操作尽量批量
- [ ] **监控指标**：监控线程池、背压、延迟指标

---

## 十、关联笔记

### Spring 生态
- [[SpringBoot-Web层设计]] · [[Spring-IOCAOP核心机制]] · [[SpringSecurity-认证授权]]
- [[SpringBoot-配置管理与多环境]] · [[实战-SpringCloud微服务电商系统]]

### Java 并发
- [[Java-并发编程JUC]] · [[Java函数式编程与Stream]] · [[JVM-内存模型与GC调优]]

### 实时通信
- [[WebSocket-SSE联调实战]] · [[Java-AI流式响应实战]] · [[Gateway-网关路由与鉴权]]

### 导航
- [[MOC-后端开发]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[Java函数式编程与Stream]] 函数式基础 → 学习 [[Java-并发编程JUC]] 并发编程 → 深入本文 Spring WebFlux 响应式编程 → 实践 [[WebSocket-SSE联调实战]] 实时通信 → 研究 [[Java-AI流式响应实战]] AI 流式输出 → 应用于高并发响应式系统构建。
