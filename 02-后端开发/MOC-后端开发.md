---
title: 后端开发 MOC
tags: [Java, SpringBoot, SpringCloud, Redis, Kafka, JVM, 微服务, AI后端]
category: 后端开发
created: 2026-08-12
updated: 2026-09-07
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: []
aliases: [MOC-后端开发]
---

# ☕ 后端开发 MOC

> 基于 Java + Spring 生态的现代后端技术栈，覆盖 Java核心、Spring生态、微服务与中间件、AI后端集成、数据与检索、工程化与测试、问题排查、API设计、安全认证九大领域，共 70 篇文档。
>
> **学习建议**：先掌握 Java 核心和 JVM，再深入 Spring Boot，然后学习微服务和中间件，最后探索 AI 后端集成和性能调优。

---

## 📚 学习路线

```
入门阶段：Java基础 → 集合框架 → 异常处理 → Maven → SpringBoot入门
进阶阶段：Java并发(JUC) → JVM内存模型 → Spring IOC/AOP → MyBatis → Redis
高级阶段：SpringCloud微服务 → 消息队列(Kafka/RabbitMQ) → 分布式事务 → 高并发设计
专家阶段：JVM调优 → 源码原理 → 架构设计 → AI后端集成 → 线上故障排查
```

---

## 📂 文档索引

### 一、Java核心

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Java知识点完整整合大全_优化版\|Java知识点完整整合大全]] | Java完整知识体系、语法、集合、并发、JVM、IO、网络、反射、注解、面试考点 | 🔴高级 |
| [[Java-语法进阶与StreamAPI]] | Java语法进阶、Stream API、Lambda、Optional、函数式接口、方法引用 | 🟡进阶 |
| [[Java-集合框架源码分析]] | ArrayList/LinkedList/HashMap/ConcurrentHashMap源码级分析、选型、最佳实践 | 🔴高级 |
| [[Java-并发编程JUC]] | Java并发编程、JUC包、线程池、锁、原子类、并发容器、AQS、CompletableFuture | 🔴高级 |
| [[并发编程 知识点系统梳理_优化版\|并发编程知识点系统梳理]] | 线程、锁、线程池、并发容器、AQS、CAS、内存模型、面试考点 | 🔴高级 |
| [[JVM-内存模型与GC调优]] | JVM内存模型、垃圾回收算法、GC调优、类加载、OOM排查、性能调优 | 🔴高级 |
| [[JVM-调优工具实战-Arthas]] | Arthas调优工具、在线诊断、反编译、方法监控、线程分析、内存分析 | 🔴高级 |
| [[Java-反射与字节码操作]] | 反射机制、Class对象、动态代理、字节码操作(ASM/CGLib/ByteBuddy)、应用场景 | 🔴高级 |
| [[Java-异常体系与最佳实践]] | 异常体系、受检异常非受检异常、异常处理最佳实践、自定义异常、异常链 | 🟡进阶 |
| [[Java-LTS版本新特性]] | Java 8/11/17/21 LTS版本新特性、语法改进、API增强、性能优化、迁移指南 | 🟡进阶 |
| [[设计模式知识点系统梳理_优化版\|设计模式知识点系统梳理]] | 23种设计模式、创建型/结构型/行为型、适用场景、Java实现、面试考点 | 🟡进阶 |

### 二、Spring生态

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Spring Boot 知识点系统梳理_优化版\|SpringBoot知识点系统梳理]] | SpringBoot核心、自动装配、Starter、配置、Web、数据访问、安全、监控、面试考点 | 🟡进阶 |
| [[Spring原理 知识点系统梳理_优化版\|Spring原理知识点系统梳理]] | Spring IOC/AOP原理、Bean生命周期、循环依赖、事务、SpringMVC、源码解析 | 🔴高级 |
| [[Spring-IOCAOP核心机制]] | Spring IOC容器、Bean定义、依赖注入、AOP动态代理、切面、通知、织入 | 🔴高级 |
| [[SpringBoot-自动装配原理]] | SpringBoot自动装配原理、@EnableAutoConfiguration、SPI机制、Starter开发、条件装配 | 🔴高级 |
| [[SpringBoot-Web层设计]] | SpringBoot Web层、SpringMVC、控制器、拦截器、过滤器、参数绑定、返回值处理 | 🟡进阶 |
| [[SpringBoot-配置管理与多环境]] | 配置管理、application.yml、多环境配置、配置优先级、外部化配置、Nacos配置中心 | 🟡进阶 |
| [[Spring Cloud微服务 知识点系统梳理_优化版\|SpringCloud微服务知识点系统梳理]] | 微服务架构、注册中心、配置中心、网关、负载均衡、熔断降级、分布式事务、链路追踪 | 🔴高级 |
| [[SpringCloud-Alibaba组件体系]] | SpringCloud Alibaba、Nacos、Sentinel、Seata、RocketMQ、Dubbo、组件集成 | 🔴高级 |
| [[MyBatis-Plus 知识点系统梳理_优化版\|MyBatis-Plus知识点系统梳理]] | MyBatis-Plus、CRUD、条件构造器、分页、代码生成器、多租户、逻辑删除、乐观锁 | 🟡进阶 |
| [[SpringDataJPA与MyBatis对比]] | Spring Data JPA与MyBatis对比、ORM框架选型、优缺点、适用场景、最佳实践 | 🟡进阶 |
| [[SpringSecurity-认证授权]] | Spring Security、认证授权、过滤器链、JWT、OAuth2、RBAC、方法级安全、自定义登录 | 🔴高级 |
| [[SpringValidation-参数校验]] | 参数校验、JSR-303、@Valid/@Validated、自定义校验注解、分组校验、全局异常处理 | 🟡进阶 |
| [[SpringCache-缓存抽象]] | Spring Cache抽象、@Cacheable/@CachePut/@CacheEvict、Redis集成、缓存穿透/击穿/雪崩 | 🟡进阶 |
| [[SpringWebFlux-响应式编程]] | Spring WebFlux、响应式编程、Reactor、Mono/Flux、非阻塞IO、函数式端点、背压 | 🔴高级 |
| [[SpringAI-框架入门与模型抽象]] | Spring AI框架入门、模型抽象、ChatClient、Prompt、OutputParser、模型适配 | 🟡进阶 |
| [[SpringAI-FunctionCalling工具调用]] | Spring AI Function Calling、工具调用、@Tool、函数注册、参数解析、多轮工具调用 | 🟡进阶 |
| [[SpringAI-RAG检索增强实现]] | Spring AI RAG、检索增强生成、向量存储、文档加载、分块、嵌入、检索、生成 | 🟡进阶 |

### 三、微服务与中间件

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Nacos-注册中心与配置中心]] | Nacos注册中心、服务发现、配置中心、动态配置、命名空间、分组、集群、AP/CP | 🟡进阶 |
| [[OpenFeign-服务间调用]] | OpenFeign声明式调用、接口定义、负载均衡、超时重试、降级、拦截器、日志配置 | 🟡进阶 |
| [[Gateway-网关路由与鉴权]] | Spring Cloud Gateway、路由、断言、过滤器、限流、鉴权、跨域、灰度发布、动态路由 | 🔴高级 |
| [[Sentinel-流量控制与熔断]] | Sentinel流量控制、熔断降级、热点参数限流、系统保护、规则持久化、Dashboard、网关限流 | 🔴高级 |
| [[Seata-分布式事务]] | Seata分布式事务、AT/TCC/SAGA/XA模式、TC/TM/RM、全局事务、补偿、隔离级别 | 🔴高级 |
| [[RocketMQ-事务消息]] | RocketMQ事务消息、半消息、回查、提交/回滚、消息可靠性、顺序消息、延迟消息 | 🔴高级 |
| [[Kafka-消息队列与消费模型]] | Kafka架构、Producer/Consumer、Topic/Partition、消费组、副本、ISR、消息可靠性、Exactly-Once | 🔴高级 |
| [[RabbitMQ-消息中间件]] | RabbitMQ、Exchange/Queue/Binding、四种交换机、消息确认、死信队列、延迟队列、优先级队列 | 🟡进阶 |
| [[Redis-分布式锁与缓存穿透]] | Redis分布式锁、Redisson、缓存穿透/击穿/雪崩、布隆过滤器、缓存一致性、延迟双删 | 🔴高级 |
| [[XXL-Job-分布式任务调度]] | XXL-Job分布式任务调度、执行器、调度中心、任务管理、分片广播、失败重试、日志 | 🟡进阶 |
| [[Maven-多模块与依赖管理]] | Maven多模块、依赖管理、dependencyManagement、插件、生命周期、私服、版本管理 | 🟢入门 |
| [[Java-高并发系统设计]] | 高并发系统设计、限流、熔断、降级、缓存、异步、分库分表、负载均衡、容量规划 | 🔴高级 |
| [[Java-微服务安全架构]] | 微服务安全架构、认证授权、JWT、OAuth2、服务间认证、API网关安全、零信任 | 🔴高级 |

### 四、AI后端集成

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Java AI Agent开发知识点系统梳理_优化版\|Java AI Agent开发]] | LangChain4j、Spring AI、Agent开发、工具调用、记忆、规划、多Agent、RAG | 🟡进阶 |
| [[Java AIGC应用开发知识点系统梳理_优化版\|Java AIGC应用开发]] | 文本/图像/语音生成、多模态、内容审核、流式输出、Prompt工程、模型适配 | 🟡进阶 |
| [[LangChain4j-Agent与RAG实现]] | LangChain4j框架、Agent实现、RAG检索增强、工具调用、记忆、嵌入、向量存储 | 🟡进阶 |
| [[Java-AI流式响应实战]] | Java AI流式响应、SSE、WebSocket、流式输出、背压、取消、错误处理、前端对接 | 🟡进阶 |
| [[Java-LLM接口封装与降级策略]] | LLM接口封装、统一抽象、多模型适配、降级策略、重试、限流、缓存、成本控制 | 🔴高级 |
| [[Java调用OpenAI兼容API]] | Java调用OpenAI兼容API、HTTP客户端、请求响应、流式调用、函数调用、错误处理 | 🟡进阶 |
| [[Java-向量数据库客户端]] | Java向量数据库客户端、Milvus/Pinecone/Chroma、向量CRUD、相似度搜索、过滤、批量 | 🟡进阶 |
| [[Java向量数据库客户端集成]] | 向量数据库集成、Spring Boot集成、配置、索引管理、嵌入模型、检索策略、性能优化 | 🟡进阶 |
| [[Java-多模态AI集成]] | 多模态AI集成、文本/图像/语音/视频、模型调用、内容理解、生成、转换、最佳实践 | 🟡进阶 |
| [[AI网关与多模型路由设计]] | AI网关设计、多模型路由、负载均衡、故障转移、成本优化、限流、缓存、可观测性 | 🔴高级 |
| [[AI工作流编排引擎设计]] | AI工作流编排、DAG、节点设计、条件分支、循环、并行、状态管理、持久化、可视化 | 🔴高级 |
| [[多Agent协作模式实现]] | 多Agent协作、角色分工、通信机制、任务分配、协调策略、冲突解决、性能优化 | 🔴高级 |
| [[AI应用可观测性与Langfuse集成]] | AI应用可观测性、Langfuse集成、Trace、Span、评估、成本追踪、Prompt管理、调试 | 🟡进阶 |
| [[AI应用测试与LLM输出评估]] | AI应用测试、LLM输出评估、自动化测试、评估指标、回归测试、A/B测试、质量保障 | 🟡进阶 |

### 五、数据与检索

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Elasticsearch-全文检索引擎]] | Elasticsearch全文检索、倒排索引、文档、索引、分片、查询DSL、聚合、集群、性能优化 | 🔴高级 |
| [[Java-数据库性能优化]] | 数据库性能优化、SQL优化、索引优化、连接池、慢查询、执行计划、分库分表、缓存 | 🔴高级 |
| [[Java-SQL注入与XSS防护]] | SQL注入防护、XSS防护、输入验证、参数化查询、输出编码、CSP、安全编码规范 | 🟡进阶 |

### 六、工程化与测试

| 文档 | 说明 | 难度 |
|------|------|------|
| [[JUnit5与Mockito测试]] | JUnit5单元测试、Mockito Mock、断言、参数化测试、Spring Boot测试、测试分层、覆盖率 | 🟡进阶 |
| [[SkyWalking-分布式链路追踪]] | SkyWalking分布式链路追踪、Agent、Trace/Span、服务拓扑、性能分析、告警、采样 | 🔴高级 |
| [[SonarQube-代码质量门禁]] | SonarQube代码质量、静态分析、代码规范、漏洞检测、质量门禁、CI/CD集成、报告 | 🟡进阶 |
| [[Java-应用性能调优实战]] | Java应用性能调优、JVM调优、数据库调优、缓存调优、并发调优、架构调优、性能测试 | 🔴高级 |
| [[Java-数据加密与脱敏]] | 数据加密、对称非对称加密、哈希、数字签名、数据脱敏、密钥管理、加密存储、合规 | 🟡进阶 |

### 七、问题排查

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Java问题排查手册]] | Java问题排查、内存泄漏、CPU飙高、死锁、OOM、线程阻塞、GC问题、工具使用、案例分析 | 🔴高级 |
| [[线上故障排查手册]] | 线上故障排查、应急响应、故障定位、日志分析、监控告警、回滚、复盘、预防措施 | 🔴高级 |

### 八、API设计

| 文档 | 说明 | 难度 |
|------|------|------|
| [[API设计规范与选型]] | API设计规范、RESTful、GraphQL、gRPC、版本管理、错误处理、文档、安全、性能、选型 | 🟡进阶 |

### 九、安全认证

| 文档 | 说明 | 难度 |
|------|------|------|
| [[SSO单点登录与分布式会话]] | SSO单点登录、OAuth2、SAML、CAS、分布式会话、Session共享、JWT、记住我、登出 | 🔴高级 |

---

## 🔗 知识关联

```
后端开发体系
├── Java核心 ← 后端开发的基础
│   ├── 集合框架 → 数据结构、性能
│   ├── 并发编程 → 多线程、线程池
│   ├── JVM → 内存管理、GC、调优
│   └── 反射/字节码 → 框架底层、动态代理
├── Spring生态 ← 核心框架
│   ├── IOC/AOP → 依赖注入、切面编程
│   ├── SpringBoot → 自动装配、快速开发
│   ├── SpringCloud → 微服务架构
│   ├── MyBatis → 数据访问
│   └── SpringSecurity → 安全认证
├── 微服务与中间件 ← 分布式系统
│   ├── 注册中心(Nacos) → 服务发现
│   ├── 网关(Gateway) → 路由、限流、鉴权
│   ├── 消息队列(Kafka/RabbitMQ) → 异步、解耦
│   ├── 分布式事务(Seata) → 数据一致性
│   └── 熔断限流(Sentinel) → 高可用
├── AI后端集成 ← AI应用后端
│   ├── Spring AI → AI框架
│   ├── LangChain4j → Agent/RAG
│   ├── 流式响应 → SSE/WebSocket
│   └── 向量数据库 → RAG检索
├── 数据与检索 ← 数据存储
│   ├── MySQL → 关系型数据库
│   ├── Redis → 缓存
│   └── Elasticsearch → 全文检索
├── 工程化与测试 ← 质量保障
│   ├── JUnit/Mockito → 单元测试
│   ├── SkyWalking → 链路追踪
│   └── SonarQube → 代码质量
└── 问题排查 ← 线上运维
    ├── Java问题排查 → JVM/线程/内存
    └── 线上故障排查 → 应急响应
```

- **Java核心** 是后端开发的基础，[[Java-并发编程JUC|并发编程]] 和 [[JVM-内存模型与GC调优|JVM]] 是面试高频考点
- **Spring生态** 是核心框架，[[SpringBoot-自动装配原理|自动装配原理]] 和 [[Spring-IOCAOP核心机制|IOC/AOP]] 是源码重点
- **微服务** 是分布式系统的基础，与 [[MOC-分布式与中间件|分布式与中间件]] 紧密关联
- **AI后端集成** 是新兴领域，与 [[MOC-AI与效率工具|AI与效率工具]] 紧密关联
- 后端通过 API 与前端 [[MOC-前端开发|Vue3]] 交互

---

## 📖 学习顺序

1. **Java核心**：[[Java知识点完整整合大全_优化版|Java大全]] → [[Java-集合框架源码分析|集合框架]] → [[Java-并发编程JUC|并发编程]] → [[JVM-内存模型与GC调优|JVM]]
2. **Spring入门**：[[Spring Boot 知识点系统梳理_优化版|SpringBoot]] → [[MyBatis-Plus 知识点系统梳理_优化版|MyBatis-Plus]]
3. **Spring深入**：[[Spring原理 知识点系统梳理_优化版|Spring原理]] → [[SpringBoot-自动装配原理|自动装配]] → [[Spring-IOCAOP核心机制|IOC/AOP]]
4. **微服务**：[[Spring Cloud微服务 知识点系统梳理_优化版|SpringCloud]] → [[Nacos-注册中心与配置中心|Nacos]] → [[Gateway-网关路由与鉴权|Gateway]] → [[Sentinel-流量控制与熔断|Sentinel]]
5. **中间件**：[[Redis-分布式锁与缓存穿透|Redis]] → [[Kafka-消息队列与消费模型|Kafka]] → [[Seata-分布式事务|Seata]]
6. **AI后端**：[[Java AI Agent开发知识点系统梳理_优化版|Java AI Agent]] → [[LangChain4j-Agent与RAG实现|LangChain4j]] → [[Java-AI流式响应实战|流式响应]]
7. **性能调优**：[[Java-应用性能调优实战|性能调优]] → [[JVM-调优工具实战-Arthas|Arthas]] → [[Java问题排查手册|问题排查]]
8. **实战**：[[MOC-项目实战|全栈项目实战]]

---

## 🚀 知识域旗舰全集

- [[Java知识点完整整合大全_优化版|Java知识点完整整合大全]] — Java完整知识体系、语法、集合、并发、JVM、IO、网络、反射、注解、面试考点

## 🧩 排查与进阶手册

- [[Java问题排查手册|Java问题排查手册]] — 内存泄漏、CPU飙高、死锁、OOM、线程阻塞、GC问题、工具使用、案例分析
- [[线上故障排查手册|线上故障排查手册]] — 应急响应、故障定位、日志分析、监控告警、回滚、复盘、预防措施

## 🏷️ 相关标签

`#后端` `#Java` `#SpringBoot` `#SpringCloud` `#微服务` `#JVM` `#并发编程` `#MyBatis` `#Redis` `#Kafka` `#分布式事务` `#AI后端` `#性能调优` `#面试`

---

[[Home|🏠 返回首页]] · [[MOC-综合导航|📚 综合导航]] · [[学习路线总览|🗺️ 学习路线]]
---

## 📝 新增文档（2026-09）

- [[Spring事务管理与传播机制|Spring事务管理与传播机制]]

