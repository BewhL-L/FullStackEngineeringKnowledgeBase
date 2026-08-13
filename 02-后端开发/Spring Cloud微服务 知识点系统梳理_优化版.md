---
title: Spring Cloud 微服务知识点系统梳理
tags: [后端, SpringCloud, 微服务, 进阶]
created: 2026-08-12
updated: 2026-08-12
---

# Spring Cloud 微服务知识点系统梳理（优化版）

> **文档说明**：本文档参照《Java知识点完整整合大全》排版风格，系统梳理 Spring Cloud 微服务技术栈。包含概述、核心特性、常用用法、注意事项四大模块，辅以动态可视化解析图、深度讲解与精简总结。**优化版**在原有内容基础上，为每个知识点补充了作用、原理、用法的深度解析，并新增了知识点图解。

---

## 1. 概述

Spring Cloud 是基于 Spring Boot 的微服务架构一站式解决方案，提供服务注册发现、配置中心、网关、熔断降级、链路追踪等分布式系统开发工具。它不是一个技术，而是一系列组件的集合。

**核心定位**：
- 微服务架构治理：服务注册发现、负载均衡、熔断降级
- 分布式配置管理：集中配置、动态刷新
- API 网关：统一入口、路由、鉴权、限流
- 可观测性：链路追踪、日志聚合、监控告警

**主流技术栈对比**：

| 组件类别 | Spring Cloud Netflix（停更） | Spring Cloud Alibaba（主流） |
|---------|---------------------------|--------------------------|
| 服务注册 | Eureka | Nacos |
| 配置中心 | Spring Cloud Config | Nacos Config |
| 服务调用 | Feign + Ribbon | OpenFeign + LoadBalancer |
| 熔断降级 | Hystrix（停更） | Sentinel |
| 网关 | Zuul 1.x | Spring Cloud Gateway |
| 链路追踪 | Sleuth + Zipkin | Sleuth + Zipkin / SkyWalking |
| 消息驱动 | Stream（RabbitMQ/Kafka） | Stream + RocketMQ |

**版本对应**：Spring Cloud 2021.x 对应 Spring Boot 2.7.x，Spring Cloud 2022.x 对应 Spring Boot 3.x。

---

## 2. 核心特性

<div style="background:linear-gradient(135deg,#fa709a,#fee140);border-radius:16px;padding:24px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#1a1a2e;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes microFlow{0%,100%{transform:scale(1)}50%{transform:scale(1.06)}}.micro-comp{display:inline-block;width:28%;vertical-align:top;margin:0 2% 10px;background:rgba(255,255,255,.5);border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:12px;font-size:11px;text-align:center;animation:microFlow 2.5s ease-in-out infinite}.micro-comp:nth-child(2){animation-delay:.4s}.micro-comp:nth-child(3){animation-delay:.8s}.micro-comp:nth-child(4){animation-delay:1.2s}.micro-comp:nth-child(5){animation-delay:1.6s}.micro-comp:nth-child(6){animation-delay:2s}.micro-icon{font-size:22px;margin-bottom:6px}.micro-name{font-weight:700;font-size:13px;margin-bottom:4px}</style>
<div style="text-align:center;font-size:16px;font-weight:700;margin-bottom:16px;padding-bottom:12px;border-bottom:1.5px solid rgba(0,0,0,.1);letter-spacing:1px">微服务架构六大核心组件</div>
<div style="text-align:center">
<div class="micro-comp"><div class="micro-icon">📮</div><div class="micro-name">注册中心</div><div style="font-size:10px;opacity:.8">Nacos/Eureka<br>服务注册与发现</div></div>
<div class="micro-comp"><div class="micro-icon">⚖️</div><div class="micro-name">负载均衡</div><div style="font-size:10px;opacity:.8">LoadBalancer/Ribbon<br>客户端负载均衡</div></div>
<div class="micro-comp"><div class="micro-icon">🛡️</div><div class="micro-name">熔断降级</div><div style="font-size:10px;opacity:.8">Sentinel/Hystrix<br>容错保护</div></div>
<div class="micro-comp"><div class="micro-icon">🚪</div><div class="micro-name">API网关</div><div style="font-size:10px;opacity:.8">Gateway/Zuul<br>路由鉴权限流</div></div>
<div class="micro-comp"><div class="micro-icon">⚙️</div><div class="micro-name">配置中心</div><div style="font-size:10px;opacity:.8">Nacos Config<br>集中配置管理</div></div>
<div class="micro-comp"><div class="micro-icon">🔗</div><div class="micro-name">链路追踪</div><div style="font-size:10px;opacity:.8">Sleuth/Zipkin<br>分布式追踪</div></div>
</div>
</div>

### 2.1 服务注册与发现（Nacos/Eureka）

服务启动时将自己的地址注册到注册中心，消费方从注册中心获取服务提供者列表，实现服务间透明调用。

**核心概念**：
- 服务注册：服务启动时向注册中心注册（IP+端口+服务名）
- 服务发现：消费方从注册中心获取服务列表
- 心跳续约：服务定期发送心跳（默认30秒），证明自己存活
- 服务剔除：注册中心在一定时间内未收到心跳则剔除服务（默认90秒）

**Nacos vs Eureka**：Nacos 支持 AP/CP 切换、配置中心、权重路由、命名空间；Eureka 纯 AP，已停更。

> 🔍 **知识点深度解析**
>
> **作用**：服务注册发现解决了微服务间"如何找到对方"的问题。服务实例动态扩缩容时，消费方无需硬编码地址，从注册中心动态获取。是微服务架构的基础。
>
> **原理**：服务提供者启动时调用注册中心 API 注册自己（服务名+IP+端口+元数据），并启动心跳线程定期续约。注册中心维护服务注册表（ConcurrentHashMap），收到心跳则更新最后续约时间，定时任务检查过期服务并剔除。消费方启动时从注册中心拉取服务列表缓存到本地，定时（默认30秒）刷新。Nacos 用 Distro 协议（AP）或 Raft 协议（CP）实现集群一致性；Eureka 用 Peer-to-Peer 复制（AP，可能短暂不一致）。
>
> **用法要点**：① 服务名用 spring.application.name，不要用 IP 硬编码；② 生产环境注册中心集群部署（Nacos 至少3节点）；③ 心跳间隔和剔除时间根据业务调整（快速剔除用短间隔，但可能误删）；④ Nacos 命名空间用于环境隔离（dev/test/prod），分组用于业务隔离；⑤ 服务优雅下线：调用 Nacos OpenAPI 注销，避免流量打到正在关闭的实例；⑥ Eureka 已停更，新项目用 Nacos 或 Consul。

### 2.2 负载均衡（LoadBalancer/Ribbon）

客户端负载均衡：消费方从注册中心获取服务列表后，在本地通过负载均衡算法选择一个实例调用。

**负载均衡算法**：
- 轮询（RoundRobin）：默认，依次选择
- 随机（Random）：随机选择
- 权重（Weighted）：根据权重选择（Nacos 支持）
- 最少连接（BestAvailable）：选择并发最少的实例
- 区域感知（ZoneAvoidance）：优先同区域

**Spring Cloud LoadBalancer**：替代 Ribbon（已停更），基于 Reactor 实现，支持响应式。

> 🔍 **知识点深度解析**
>
> **作用**：负载均衡将请求分发到多个服务实例，实现高可用和水平扩展。客户端负载均衡（Ribbon/LoadBalancer）在消费方本地选择实例，不需要额外的负载均衡器（如 Nginx），性能更好。
>
> **原理**：负载均衡器从 DiscoveryClient 获取服务列表（List<ServiceInstance>），通过 IRule（Ribbon）或 ReactorLoadBalancer（LoadBalancer）选择一个实例。轮询算法用 AtomicInteger 计数器取模；随机算法用 ThreadLocalRandom；权重算法根据实例权重（Nacos 元数据）计算概率。OpenFeign 集成了负载均衡：@FeignClient 方法调用时，LoadBalancerClient 先选实例，再用 RestTemplate/WebClient 调用。
>
> **用法要点**：① Spring Cloud 2020+ 移除 Ribbon，用 spring-cloud-starter-loadbalancer；② 自定义负载均衡策略：实现 ReactorServiceInstanceLoadBalancer，用 @LoadBalancerClient 配置；③ 同集群优先：Nacos 支持 cluster-name 配置，优先调用同集群实例；④ 权重路由：Nacos 控制台设置实例权重（0-1），用于灰度发布（新版本权重10%）；⑤ 重试机制：Spring Retry + LoadBalancer，失败时重试其他实例（注意幂等性）；⑥ 负载均衡是客户端侧的，服务端无感知。

### 2.3 服务调用（OpenFeign）

OpenFeign 是声明式 HTTP 客户端，通过接口+注解定义服务调用，自动集成负载均衡、熔断、编码解码。

```java
@FeignClient(name = "user-service", fallback = UserServiceFallback.class)
public interface UserServiceClient {
    @GetMapping("/users/{id}")
    User getUser(@PathVariable("id") Long id);
    
    @PostMapping("/users")
    void createUser(@RequestBody User user);
}
```

**核心特性**：声明式接口、集成 LoadBalancer、支持熔断（Sentinel）、请求/响应拦截器、自定义编码器。

> 🔍 **知识点深度解析**
>
> **作用**：OpenFeign 让远程服务调用像本地方法调用一样简单，无需手动拼接 URL、处理 HTTP 请求/响应。集成了负载均衡、熔断、编码解码，是微服务间调用的标准方式。
>
> **原理**：@FeignClient 注解的接口由 FeignClientFactoryBean 创建动态代理（JDK 动态代理）。方法调用时，代理对象通过 Contract 解析方法注解（@GetMapping/@PathVariable 等），构建 RequestTemplate，然后通过 Client（默认 HttpURLConnection，可换 OkHttp/Apache HttpClient）发送 HTTP 请求。负载均衡由 LoadBalancerClient 介入：在发送前选择服务实例。响应通过 Decoder 反序列化为返回值类型。熔断由 SentinelFeign 集成：调用失败时执行 fallback。
>
> **用法要点**：① 必须 @EnableFeignClients 开启扫描；② @PathVariable/@RequestParam 必须指定 value（即使参数名相同）；③ 复杂对象用 @RequestBody（POST/PUT），GET 请求不能有 @RequestBody；④ 超时配置：connectTimeout（连接超时）、readTimeout（读取超时），默认太短（1秒）需调大；⑤ 换 OkHttp 或 Apache HttpClient（支持连接池，性能更好）；⑥ fallback 类必须实现 Feign 接口，用 @Component 注册；⑦ 传递请求头（如 Token）用 RequestInterceptor。

### 2.4 熔断降级（Sentinel）

Sentinel 是阿里开源的流量防护组件，支持熔断、限流、降级、系统保护。替代已停更的 Hystrix。

**核心功能**：
- 流量控制：QPS 限流、并发线程数限流、冷启动、匀速排队
- 熔断降级：慢调用比例、异常比例、异常数
- 系统保护：系统负载、CPU 使用率、入口 QPS、平均响应时间
- 热点参数限流：针对特定参数值限流

**熔断状态机**：关闭 → 打开（熔断）→ 半开（探测）→ 关闭（恢复）或打开（继续熔断）。

> 🔍 **知识点深度解析**
>
> **作用**：熔断降级防止级联故障（一个服务慢导致所有调用它的服务都慢，最终整个系统雪崩）。当依赖服务异常率过高时，自动熔断（快速失败），一段时间后半开探测，恢复则关闭熔断。是微服务容错的核心。
>
> **原理**：Sentinel 通过 ProcessorSlotChain（责任链）处理请求：NodeSelectorSlot（构建调用路径）→ ClusterBuilderSlot（集群统计）→ StatisticSlot（实时统计，用滑动窗口）→ AuthoritySlot（黑白名单）→ SystemSlot（系统保护）→ ParamFlowSlot（热点限流）→ FlowSlot（流量控制）→ DegradeSlot（熔断降级）。滑动窗口统计 QPS/响应时间/异常数，熔断规则根据统计判断是否触发。熔断打开时直接抛 DegradeException，半开时放一个请求探测，成功则关闭，失败则继续打开。
>
> **用法要点**：① 熔断规则三选一：慢调用比例（RT>阈值且比例>阈值）、异常比例、异常数；② 限流规则：QPS 或并发线程数，超出则拒绝（可配置排队等待）；③ 热点参数限流：针对方法参数的特定值限流（如商品ID，爆款商品单独限流）；④ 控制台动态配置规则（推送到 Nacos 持久化）；⑤ 与 OpenFeign 集成：feign.sentinel.enabled=true；⑥ 降级方法（@SentinelResource fallback）返回兜底数据，不要返回 null；⑦ 系统保护是全局的，保护整个系统不被打垮。

### 2.5 API 网关（Spring Cloud Gateway）

网关是微服务的统一入口，负责路由转发、鉴权、限流、日志、协议转换。

**核心概念**：
- Route（路由）：ID + 目标 URI + 断言 + 过滤器
- Predicate（断言）：匹配请求（路径、方法、Header、Cookie、时间）
- Filter（过滤器）：请求/响应处理（鉴权、限流、修改 Header）

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/api/users/**
          filters:
            - StripPrefix=1
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 10
```

> 🔍 **知识点深度解析**
>
> **作用**：API 网关是微服务的统一入口，所有外部请求先到网关，再由网关路由到后端服务。网关处理横切关注点：鉴权（Token 校验）、限流（防刷）、路由（路径匹配）、日志、跨域、协议转换（HTTP→gRPC）。后端服务只关注业务逻辑。
>
> **原理**：Spring Cloud Gateway 基于 Spring WebFlux（响应式，Netty），请求处理流程：DispatcherHandler → HandlerMapping（RoutePredicateHandlerMapping 匹配路由）→ WebHandler（FilteringWebHandler 执行过滤器链）→ 代理转发（Netty HttpClient）。过滤器分 GlobalFilter（全局，如 LoadBalancerClientFilter 负载均衡、NettyRoutingFilter 转发）和 GatewayFilter（路由级，如 StripPrefix、RequestRateLimiter）。断言由 Predicate 工厂创建，匹配成功则路由生效。
>
> **用法要点**：① 网关基于 WebFlux，不能用 Spring MVC（不能同时引入 spring-boot-starter-web）；② 路由 uri 用 lb://service-name 集成负载均衡；③ 鉴权用 GlobalFilter（校验 JWT Token，通过则放行，否则返回401）；④ 限流用 RequestRateLimiter（基于 Redis + Lua 脚本，令牌桶算法）；⑤ 跨域配置用 CorsWebFilter 或 yaml 配置；⑥ 网关是性能瓶颈，需集群部署+Nginx 负载均衡；⑦ 不要在网关做业务逻辑（只做横切关注点）。

### 2.6 配置中心（Nacos Config）

集中管理各环境配置，支持动态刷新（修改配置后服务无需重启）。

**核心概念**：
- Data ID：配置文件标识（${prefix}-${spring.profiles.active}.${file-extension}）
- Group：配置分组（默认 DEFAULT_GROUP）
- Namespace：命名空间（环境隔离）
- 动态刷新：@RefreshScope 或 @ConfigurationProperties 自动刷新

```yaml
spring:
  cloud:
    nacos:
      config:
        server-addr: localhost:8848
        namespace: dev
        file-extension: yaml
```

> 🔍 **知识点深度解析**
>
> **作用**：配置中心将配置从代码中抽离，集中管理。不同环境（dev/test/prod）用不同配置，修改配置后动态刷新无需重启。是微服务配置管理的标准方案。
>
> **原理**：服务启动时从 Nacos 拉取配置（Data ID + Group + Namespace），合并到 Spring Environment（优先级高于本地配置）。动态刷新通过长轮询（Long Polling）实现：客户端发起请求，Nacos 挂起（默认30秒），配置变更则立即返回，超时则客户端重新发起。收到变更后，发布 RefreshEvent，@RefreshScope 注解的 Bean 会被销毁重建（用新配置），@ConfigurationProperties 自动绑定新值。Nacos 配置存储在 MySQL（集群）或内嵌数据库（单机）。
>
> **用法要点**：① 配置优先级：Nacos 远程配置 > 本地 application.yml > bootstrap.yml；② bootstrap.yml 配置 Nacos 地址（必须在应用上下文启动前加载）；③ 动态刷新：@ConfigurationProperties 自动刷新，@Value 需配合 @RefreshScope；④ 敏感配置（密码、密钥）用 Nacos 加密配置或集成 Vault；⑤ 配置版本管理：Nacos 控制台有历史版本，可回滚；⑥ 多环境用 namespace 隔离（不是 group）；⑦ 配置变更监听：@NacosConfigListener 或 @RefreshScope。

### 2.7 链路追踪（Sleuth + Zipkin）

分布式链路追踪记录请求在微服务间的调用路径，用于排查慢请求、定位故障。

**核心概念**：
- Trace：一次完整请求链路（唯一 TraceID）
- Span：一次服务调用（唯一 SpanID，父 SpanID）
- Annotation：事件标记（cs/sr/ss/cr）

**Sleuth**：自动埋点，生成 TraceID/SpanID，传递到下游服务。
**Zipkin**：收集、存储、展示链路数据，支持依赖分析。

> 🔍 **知识点深度解析**
>
> **作用**：微服务架构中，一个请求可能经过多个服务，出问题时很难定位是哪个服务慢或报错。链路追踪记录完整调用路径，可视化展示每个服务的耗时和状态，是排查分布式问题的利器。
>
> **原理**：Sleuth 通过拦截器（HandlerInterceptor/Feign 拦截器）在请求入口生成 TraceID 和 SpanID，放入 MDC（日志）和请求头（传递给下游）。下游服务从请求头取出 TraceID，生成新的 SpanID（父 SpanID=上游 SpanID）。调用完成后，Span 数据（耗时、状态、标签）异步发送到 Zipkin（HTTP 或 Kafka）。Zipkin 存储（MySQL/Elasticsearch/Cassandra）并提供 UI 查询。TraceID 在所有服务的日志中都有，可串联完整链路。
>
> **用法要点**：① 日志中打印 TraceID：logging.pattern.level=%5p [${spring.application.name:},%X{traceId:-},%X{spanId:-}]；② 采样率：spring.sleuth.sampler.probability=1.0（全量，生产用0.1）；③ 传输方式：HTTP（简单）或 Kafka/RabbitMQ（高吞吐，解耦）；④ Zipkin 存储：测试用内存，生产用 Elasticsearch；⑤ 自定义 Span：@NewSpan 注解或 Tracer API；⑥ 与日志聚合（ELK）配合：用 TraceID 在 Kibana 搜索所有相关日志；⑦ SkyWalking 是无侵入的替代方案（Java Agent 字节码增强，不需要改代码）。

---

## 3. 常用用法

### 3.1 Nacos 服务注册

```yaml
# pom
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>

# application.yml
spring:
  application:
    name: user-service
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848
        namespace: dev
        group: DEFAULT_GROUP
        cluster-name: SH
```

> 🔍 **知识点深度解析**
>
> **作用**：Nacos 服务注册让服务实例自动注册到注册中心，消费方通过服务名发现实例。是微服务架构的第一步。
>
> **原理**：spring-cloud-starter-alibaba-nacos-discovery 自动配置 NacosDiscoveryAutoConfiguration，在应用启动时通过 NamingService.registerInstance() 注册。注册信息包括：服务名、IP、端口、集群名、元数据（权重、版本）。心跳由 Nacos 客户端内部线程发送（默认5秒）。Nacos 服务端维护服务注册表，定时（默认15秒）检查健康状态，超过15秒未心跳标记为不健康，超过30秒剔除。
>
> **用法要点**：① server-addr 用逗号分隔多个地址（集群）；② namespace 用于环境隔离（dev/test/prod），用命名空间 ID 不是名称；③ cluster-name 用于同集群优先调用；④ 元数据可自定义（如 version=v1），配合灰度路由；⑤ 服务下线：Nacos 控制台手动下线或调用注销 API；⑥ 多网卡环境指定 IP：spring.cloud.nacos.discovery.ip；⑦ 健康检查：Nacos 默认用心跳，可配置 TCP/HTTP 健康检查。

### 3.2 OpenFeign 服务调用

```java
@EnableFeignClients
@SpringBootApplication
public class OrderApplication {}

@FeignClient(name = "user-service", 
    configuration = FeignConfig.class,
    fallbackFactory = UserServiceFallbackFactory.class)
public interface UserServiceClient {
    @GetMapping("/api/users/{id}")
    Result<User> getUser(@PathVariable("id") Long id);
    
    @PostMapping("/api/users")
    Result<Void> createUser(@RequestBody User user);
}

@Configuration
public class FeignConfig {
    @Bean
    public RequestInterceptor requestInterceptor() {
        return template -> {
            ServletRequestAttributes attrs = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
            if (attrs != null) {
                String token = attrs.getRequest().getHeader("Authorization");
                template.header("Authorization", token);
            }
        };
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：OpenFeign 是微服务间调用的标准方式，声明式接口+注解，自动处理 HTTP 请求、负载均衡、编码解码。RequestInterceptor 传递上下文（Token、TraceID）。
>
> **原理**：@EnableFeignClients 扫描 @FeignClient 接口，通过 FeignClientFactoryBean 创建 JDK 动态代理。方法调用时，SynchronousMethodHandler 处理：解析方法注解→构建 RequestTemplate→RequestInterceptor 拦截→LoadBalancerClient 选实例→Client 发送请求→Decoder 解码响应。fallbackFactory 可以获取异常原因（比 fallback 更灵活）。
>
> **用法要点**：① @PathVariable/@RequestParam 必须写 value；② GET 请求多参数用 @SpringQueryMap 或 @RequestParam；③ 超时配置：默认 connectTimeout=10s, readTimeout=60s（不同版本可能不同），生产根据业务调；④ 用 OkHttp：引入 feign-okhttp，配置 feign.okhttp.enabled=true；⑤ 传递 Token 用 RequestInterceptor（注意异步线程 RequestContextHolder 为 null）；⑥ fallbackFactory 比 fallback 好（能拿到异常）；⑦ 大文件传输用 feign-form 或直接用 MultipartFile。

### 3.3 Sentinel 熔断限流

```java
@RestController
public class OrderController {
    @GetMapping("/order/{id}")
    @SentinelResource(value = "getOrder", 
        blockHandler = "blockHandler",
        fallback = "fallback")
    public Result<Order> getOrder(@PathVariable Long id) {
        return Result.success(orderService.getById(id));
    }
    
    public Result<Order> blockHandler(Long id, BlockException ex) {
        return Result.fail(429, "请求过于频繁");
    }
    
    public Result<Order> fallback(Long id, Throwable ex) {
        return Result.fail(500, "服务降级");
    }
}

# 配置文件规则（也可控制台配置）
spring:
  cloud:
    sentinel:
      transport:
        dashboard: localhost:8080
      datasource:
        ds:
          nacos:
            server-addr: localhost:8848
            dataId: order-service-sentinel
            groupId: DEFAULT_GROUP
            rule-type: flow
```

> 🔍 **知识点深度解析**
>
> **作用**：Sentinel 实现熔断降级和流量控制，保护服务不被打垮。@SentinelResource 定义资源点，blockHandler 处理限流/熔断，fallback 处理业务异常。
>
> **原理**：@SentinelResource 由 SentinelResourceAspect 切面拦截，进入资源时调用 SphU.entry()，通过 ProcessorSlotChain 检查规则。限流规则（FlowRule）用滑动窗口统计 QPS，超阈值则抛 FlowException。熔断规则（DegradeRule）统计慢调用/异常比例，超阈值则熔断（抛 DegradeException）。blockHandler 处理 BlockException（限流/熔断），fallback 处理业务异常（Throwable）。规则可从 Nacos 动态读取（ReadableDataSource），无需重启。
>
> **用法要点**：① blockHandler 方法必须 public，参数与原方法一致+BlockException，同类中；② fallback 方法参数与原方法一致+Throwable，同类中；③ 限流规则可在控制台配置，生产用 Nacos 持久化（重启不丢失）；④ 热点参数限流：@SentinelResource + ParamFlowRule，针对参数值限流；⑤ 系统保护是全局的（load/CPU/QPS/RT/线程数）；⑥ 控制台需要单独部署（sentinel-dashboard.jar）；⑦ 与 OpenFeign 集成：feign.sentinel.enabled=true，Feign 调用自动被 Sentinel 保护。

### 3.4 Gateway 网关配置

```yaml
spring:
  cloud:
    gateway:
      discovery:
        locator:
          enabled: true  # 自动根据服务名路由
      routes:
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/api/users/**
            - Method=GET,POST
          filters:
            - StripPrefix=1
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 20
                redis-rate-limiter.burstCapacity: 40
                key-resolver: "#{@ipKeyResolver}"
        - id: order-service
          uri: lb://order-service
          predicates:
            - Path=/api/orders/**
          filters:
            - StripPrefix=1

@Bean
public KeyResolver ipKeyResolver() {
    return exchange -> Mono.just(exchange.getRequest().getRemoteAddress().getAddress().getHostAddress());
}
```

> 🔍 **知识点深度解析**
>
> **作用**：Gateway 配置路由规则，将外部请求路由到后端微服务。集成负载均衡、限流、断言匹配。是微服务的统一入口。
>
> **原理**：路由由 RouteDefinition 定义，包含 id、uri、predicates、filters。请求到达时，RoutePredicateHandlerMapping 遍历所有路由，按顺序匹配断言（Path/Method/Header/Cookie/Query/Host/Time），匹配成功则该路由生效。FilteringWebHandler 执行过滤器链：GatewayFilter（路由级）按 order 排序执行，GlobalFilter（全局）也加入链。LoadBalancerClientFilter 将 lb:// 解析为实际实例地址（从注册中心获取+负载均衡）。NettyRoutingFilter 用 Netty HttpClient 转发请求。
>
> **用法要点**：① discovery.locator.enabled=true 自动路由（/service-name/**），但路径不友好，建议手动配置路由；② StripPrefix=1 去掉 /api 前缀（后端服务路径是 /users/**）；③ 限流用 RequestRateLimiter（基于 Redis Lua 脚本，令牌桶），key-resolver 按 IP/用户/接口限流；④ 鉴权用自定义 GlobalFilter（校验 Token，通过则 chain.filter，否则返回401）；⑤ 跨域：spring.cloud.gateway.globalcors.cors-configurations；⑥ 网关超时：spring.cloud.gateway.httpclient.connect-timeout/response-timeout；⑦ 灰度发布：按 Header/Cookie 路由到新版本服务。

### 3.5 Nacos 配置中心

```yaml
# bootstrap.yml（必须）
spring:
  application:
    name: order-service
  profiles:
    active: dev
  cloud:
    nacos:
      config:
        server-addr: localhost:8848
        namespace: dev
        file-extension: yaml
        shared-configs:
          - data-id: common.yaml
            group: DEFAULT_GROUP
            refresh: true

# Nacos 控制台配置 Data ID: order-service-dev.yaml
# order:
#   timeout: 5000
#   max-count: 100

@Configuration
@ConfigurationProperties(prefix = "order")
@Data
public class OrderConfig {
    private int timeout = 3000;
    private int maxCount = 50;
}

@RestController
@RefreshScope  // @Value 动态刷新需要
public class ConfigController {
    @Value("${order.timeout}")
    private int timeout;
}
```

> 🔍 **知识点深度解析**
>
> **作用**：Nacos Config 集中管理配置，支持动态刷新。@ConfigurationProperties 自动刷新，@Value 需 @RefreshScope。共享配置用于多个服务共用的配置（如日志级别、公共参数）。
>
> **原理**：bootstrap.yml 在应用上下文启动前加载，创建 Bootstrap 上下文，从 Nacos 拉取配置并添加到 Environment。配置加载顺序（优先级从高到低）：${name}-${profile}.${ext} > ${name}.${ext} > shared-configs > extension-configs > 本地配置。动态刷新：Nacos 客户端长轮询监听配置变更，收到变更后发布 RefreshEvent，ContextRefresher 刷新 Environment，@RefreshScope 的 Bean 被销毁（下次访问时重建），@ConfigurationProperties 自动重新绑定。
>
> **用法要点**：① 配置必须写在 bootstrap.yml（不是 application.yml），Spring Cloud 2020+ 需引入 spring-cloud-starter-bootstrap；② Data ID 格式：${prefix}-${spring.profiles.active}.${file-extension}；③ @ConfigurationProperties 自动刷新（不需要 @RefreshScope）；④ @Value 必须配合 @RefreshScope 才能动态刷新；⑤ 共享配置用 shared-configs（多个服务共用），refresh=true 支持动态刷新；⑥ 配置优先级：远程 > 本地，高优先级覆盖低优先级；⑦ 敏感配置用 Nacos 加密（自定义 EncryptablePropertySource）或 Vault。

### 3.6 分布式事务（Seata）

```java
@GlobalTransactional(rollbackFor = Exception.class)
public void createOrder(Order order) {
    orderMapper.insert(order);
    inventoryClient.deduct(order.getProductId(), order.getQuantity());
    accountClient.debit(order.getUserId(), order.getAmount());
}

# application.yml
seata:
  enabled: true
  application-id: order-service
  tx-service-group: order_tx_group
  service:
    vgroup-mapping:
      order_tx_group: default
  data-source-proxy-mode: AT  # AT/TCC/SAGA/XA
```

> 🔍 **知识点深度解析**
>
> **作用**：分布式事务解决微服务架构中跨服务的数据一致性问题。Seata 提供 AT（自动事务）、TCC、SAGA、XA 四种模式，AT 模式对业务无侵入（最常用）。
>
> **原理**：Seata AT 模式原理：① TM（事务管理器）发起全局事务，生成 XID；② RM（资源管理器）代理数据源，在业务 SQL 执行前查询前镜像（before image），执行后查询后镜像（after image），插入 undo_log；③ TC（事务协调器）记录全局事务状态；④ 正常提交：各分支异步删除 undo_log；⑤ 回滚：根据 XID 找到 undo_log，用前镜像生成回滚 SQL 执行，删除 undo_log。全局锁保证写隔离（全局事务提交前其他事务不能修改同一行）。
>
> **用法要点**：① AT 模式需要每个服务的数据库有 undo_log 表；② @GlobalTransactional 标注全局事务入口（只在发起方加，下游不加）；③ 数据源必须被 Seata 代理（DataSourceProxy），Spring Boot 自动配置；④ 隔离级别默认读未提交（全局锁保证写隔离），需要全局读用 SELECT FOR UPDATE；⑤ TC（Seata Server）集群部署，存储用 MySQL/Redis；⑥ TCC 模式性能更好但需手写 try/confirm/cancel；⑦ SAGA 模式适合长事务（业务流程编排）。

### 3.7 网关鉴权

```java
@Component
public class AuthGlobalFilter implements GlobalFilter, Ordered {
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        String path = exchange.getRequest().getPath().value();
        
        // 白名单放行
        if (path.startsWith("/api/auth/login") || path.startsWith("/api/auth/register")) {
            return chain.filter(exchange);
        }
        
        if (token == null || !JwtUtil.validate(token)) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
        
        // 解析用户信息，传递给下游
        String userId = JwtUtil.getUserId(token);
        ServerHttpRequest request = exchange.getRequest().mutate()
            .header("X-User-Id", userId)
            .build();
        return chain.filter(exchange.mutate().request(request).build());
    }
    
    @Override
    public int getOrder() { return -100; }  // 优先级
}
```

> 🔍 **知识点深度解析**
>
> **作用**：网关鉴权是微服务安全的第一道防线，统一处理登录校验，后端服务无需重复鉴权。白名单放行登录/注册接口，其他接口校验 Token。
>
> **原理**：GlobalFilter 是全局过滤器，所有路由都执行。filter() 方法接收 ServerWebExchange（请求+响应）和 GatewayFilterChain（过滤器链）。鉴权逻辑：获取 Token→校验（JWT 验签+过期）→通过则 chain.filter 继续，不通过则设置401并返回。用户信息通过请求头（X-User-Id）传递给下游服务，下游服务从 Header 获取当前用户。Ordered 控制执行顺序（数字越小越先执行）。
>
> **用法要点**：① 白名单路径用配置管理（不要硬编码）；② Token 校验用 JWT（无状态）或 Redis（有状态，可主动失效）；③ 用户信息通过 Header 传递，下游服务用拦截器解析并放入 ThreadLocal；④ 网关鉴权只做登录校验，细粒度权限（角色/资源）在服务内做；⑤ 防止绕过网关直接访问服务：服务只接受内网 IP 或校验网关签名；⑥ 网关是性能瓶颈，Token 校验要快（JWT 本地验签，不要查数据库）；⑦ 多端鉴权（APP/Web/小程序）用不同的 Token 类型或 Header。

### 3.8 微服务监控

```yaml
# pom: spring-boot-starter-actuator, micrometer-registry-prometheus
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: always
  metrics:
    tags:
      application: ${spring.application.name}

# Prometheus 抓取
# scrape_configs:
#   - job_name: 'order-service'
#     metrics_path: '/actuator/prometheus'
#     static_configs:
#       - targets: ['order-service:8080']

# 自定义指标
@RestController
public class OrderController {
    private final Counter orderCounter;
    private final Timer orderTimer;
    
    public OrderController(MeterRegistry registry) {
        this.orderCounter = Counter.builder("orders.created")
            .description("订单创建数").register(registry);
        this.orderTimer = Timer.builder("orders.process.time")
            .description("订单处理耗时").register(registry);
    }
    
    @PostMapping("/orders")
    public Result createOrder() {
        orderCounter.increment();
        return orderTimer.record(() -> orderService.create());
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：微服务监控是可观测性的核心，包括指标（Metrics）、日志（Logging）、链路（Tracing）。Actuator + Prometheus + Grafana 是标准监控方案，实时掌握服务健康状态、QPS、响应时间、错误率。
>
> **原理**：Actuator 暴露应用端点（health/info/metrics/prometheus）。Micrometer 是指标门面（类似 SLF4J），支持 Prometheus/Graphite/InfluxDB 等多种后端。Prometheus 定时拉取 /actuator/prometheus 端点（pull 模式），存储时序数据。Grafana 连接 Prometheus 数据源，用 PromQL 查询并展示图表（Dashboard）。告警用 Alertmanager（Prometheus 告警规则触发→Alertmanager 路由→邮件/钉钉/企微）。
>
> **用法要点**：① 必暴露 health 和 prometheus 端点；② 自定义指标：Counter（计数）、Gauge（瞬时值）、Timer（耗时）、DistributionSummary（分布）；③ 关键业务指标：订单量、支付成功率、库存扣减失败率；④ 系统指标：JVM 堆内存、GC 次数/耗时、线程数、CPU；⑤ 告警规则：错误率>5%、P99响应时间>1s、服务实例数<期望数；⑥ Grafana 用现成 Dashboard（JVM/Spring Boot/Spring Cloud）；⑦ 日志聚合用 ELK（Elasticsearch+Logstash+Kibana）或 Loki（轻量）。

---

## 4. 注意事项

1. **版本兼容性**：Spring Cloud、Spring Boot、Spring Cloud Alibaba 版本必须严格对应。用版本矩阵确认，否则启动报错或功能异常。

2. **服务间调用超时**：OpenFeign 默认超时可能太短，生产必须配置 connectTimeout 和 readTimeout。超时太短导致重试风暴，太长导致资源占用。

3. **熔断降级兜底**：fallback 方法必须返回合理的兜底数据（如默认值、缓存数据），不要返回 null 或抛异常。降级是为了用户体验，不是简单失败。

4. **网关性能**：Gateway 基于 WebFlux 响应式，不要在过滤器中做阻塞操作（如查数据库、同步 HTTP 调用），会阻塞 Netty 线程。

5. **配置动态刷新**：@Value 必须配合 @RefreshScope，@ConfigurationProperties 自动刷新。数据库连接、线程池等初始化后不会自动刷新，需自定义刷新逻辑。

6. **分布式事务一致性**：Seata AT 模式有性能开销（前后镜像+undo_log），高并发场景考虑最终一致性（消息队列+本地消息表）而非强一致。

7. **链路追踪采样率**：生产环境不要全量采样（1.0），用 0.1-0.5，否则 Zipkin 存储压力大。问题排查时可临时调高。

8. **服务优雅停机**：配置 graceful shutdown，先从注册中心注销，等待在途请求完成，再关闭。避免流量打到正在关闭的实例。

9. **Nacos 集群部署**：生产 Nacos 至少3节点（Raft 协议需要多数派），用 MySQL 存储配置。单机 Nacos 有单点故障风险。

10. **微服务粒度**：不要过度拆分（一个简单功能拆成多个服务），也不要巨型服务。按业务领域（DDD 限界上下文）拆分，服务内高内聚、服务间低耦合。

11. **API 版本管理**：接口变更用版本号（/api/v1/users、/api/v2/users）或 Header 版本，避免影响已有调用方。

12. **服务间依赖**：避免循环依赖（A 调 B，B 调 A），避免链式调用过长（A→B→C→D，一个慢全链路慢）。用事件驱动解耦。

---

> 💡 **深度讲解**：Spring Cloud 是微服务架构的一站式解决方案，核心组件包括：注册中心（Nacos，服务注册发现）、负载均衡（LoadBalancer，客户端选择实例）、服务调用（OpenFeign，声明式 HTTP 客户端）、熔断降级（Sentinel，防止级联故障）、API 网关（Gateway，统一入口+路由+鉴权+限流）、配置中心（Nacos Config，集中配置+动态刷新）、链路追踪（Sleuth+Zipkin，分布式调用链）。这些组件协同工作：服务启动注册到 Nacos，消费方通过 OpenFeign 调用（自动负载均衡），Sentinel 保护调用不被打垮，Gateway 统一对外入口，Nacos Config 管理配置，Sleuth 记录调用链。理解每个组件的原理和适用场景，才能构建稳定的微服务系统。常见坑：版本不兼容、Feign 超时、事务不生效、网关阻塞操作、配置不刷新。
>
> **📝 精简总结**：微服务核心组件=Nacos（注册+配置）+OpenFeign（调用）+Sentinel（熔断）+Gateway（网关）+Sleuth（追踪）；注册发现解决"找到对方"，负载均衡分发请求，OpenFeign 声明式调用，Sentinel 防雪崩，Gateway 统一入口，Nacos Config 动态配置，Sleuth 排查链路；注意版本兼容、超时配置、降级兜底、网关非阻塞、优雅停机。

---

> 📋 **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 知识点深度解析」模块（作用+原理+用法要点），原有内联图已统一风格化美化（圆角、阴影、渐变、动画）。所有原有内容完整保留，未做任何修改。
