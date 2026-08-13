---
title: Java全栈 MOC（四级展开）
tags: [MOC, Java全栈, 枢纽]
created: 2026-08-13
updated: 2026-08-13
hub: true
---

# ☕ Java全栈技术栈 MOC

> 企业级 Java 全栈体系，覆盖 Spring 生态、微服务、分布式中间件与 AI 大模型集成，是大型后端系统的主力技术栈。
> **标签前缀**：`#Java全栈/`
> **枢纽核心笔记**：[[Java-全栈技术枢纽]]

---

## 📐 知识层级总览

```
一级：Java全栈技术栈
├── 二级：2.1 Java语言与JVM
│   ├── 三级：Java-语法进阶与StreamAPI
│   │   ├── 四级：Lambda与函数式接口
│   │   ├── 四级：Stream流操作
│   │   ├── 四级：Optional与空安全
│   │   └── 四级：新特性（Record/Sealed/Pattern Matching）
│   ├── 三级：Java-并发编程JUC
│   ├── 三级：JVM-内存模型与GC调优
│   ├── 三级：Java-反射与字节码操作
│   └── 三级：Java-LTS版本新特性
├── 二级：2.2 Spring生态
├── 二级：2.3 微服务架构
├── 二级：2.4 分布式中间件
├── 二级：2.5 Java对接AI大模型
└── 二级：2.6 Java工程化
```

---

## 📚 2.1 Java 语言与 JVM

### [[Java-语法进阶与StreamAPI|语法进阶与 Stream API]]
> Java 8+ 现代语法，函数式编程基础

- **四级子知识点**：
  - Lambda 表达式与函数式接口
  - Stream 流操作（中间/终端操作）
  - Collectors 收集器与分组
  - Optional 空安全处理
  - 方法引用与构造器引用
  - Java 17+ 新语法（Record/Sealed/Pattern Matching）
- **标签**：`#Java全栈/语言核心`
- **前置依赖**：Java 基础语法

### [[Java-并发编程JUC|并发编程 JUC]]
> 高并发服务的核心能力

- **四级子知识点**：
  - 线程池原理与参数调优
  - synchronized 与 Lock 对比
  - AQS 抽象队列同步器
  - 并发容器（ConcurrentHashMap等）
  - 原子类与 CAS 原理
  - CompletableFuture 异步编排
  - 虚拟线程（Project Loom）
- **标签**：`#Java全栈/语言核心`

### [[JVM-内存模型与GC调优|JVM 内存模型与 GC 调优]]
> Java 性能优化的根基

- **四级子知识点**：
  - JVM 内存区域划分
  - 类加载机制与双亲委派
  - GC 算法与收集器对比（G1/ZGC）
  - GC 日志分析与调优
  - OOM 问题排查
  - JIT 编译与逃逸分析
  - 在线诊断工具（Arthas/JProfiler）
- **标签**：`#Java全栈/语言核心`

### [[Java-反射与字节码操作|反射与字节码操作]]
> 框架底层实现的关键技术

- **四级子知识点**：
  - 反射 API 与性能开销
  - 动态代理（JDK/CGLIB）
  - ASM 字节码操作
  - ByteBuddy 现代字节码库
  - Java Agent 与 Instrumentation
  - Spring AOP 底层实现
- **标签**：`#Java全栈/语言核心`

### [[Java-LTS版本新特性|Java LTS 版本新特性]]
> 跟踪 Java 17/21/23 演进

- **四级子知识点**：
  - Java 17 核心特性
  - Java 21 虚拟线程与模式匹配
  - Java 23 新特性预览
  - 模块系统（JPMS）
  - 迁移策略与兼容性
  - GraalVM 原生镜像
- **标签**：`#Java全栈/语言核心`

---

## 📚 2.2 Spring 生态

### [[SpringBoot-自动装配原理|SpringBoot 自动装配原理]]
> SpringBoot 核心机制，理解 starter 的关键

- **四级子知识点**：
  - @SpringBootApplication 注解拆解
  - 自动装配流程（spring.factories）
  - 条件注解（@Conditional系列）
  - 自定义 Starter 开发
  - 配置绑定（@ConfigurationProperties）
  - SpringBoot 3.x 新变化
- **标签**：`#Java全栈/Spring`

### [[Spring-IOCAOP核心机制|Spring IoC 与 AOP 核心机制]]
> Spring 框架两大基石

- **四级子知识点**：
  - Bean 生命周期
  - 依赖注入方式与循环依赖
  - Bean 作用域
  - AOP 代理机制（JDK/CGLIB）
  - 切面通知类型与执行顺序
  - 事务传播机制
- **标签**：`#Java全栈/Spring`

### [[SpringBoot-Web层设计|SpringBoot Web 层设计]]
> RESTful API 开发标准实践

- **四级子知识点**：
  - Controller 设计规范
  - 参数校验（JSR-303）
  - 全局异常处理
  - 统一响应封装
  - 拦截器与过滤器
  - 文件上传与下载
  - API 版本化策略
- **标签**：`#Java全栈/Spring`

### [[SpringDataJPA与MyBatis对比|SpringDataJPA 与 MyBatis 对比]]
> Java 持久层两大方案选型

- **四级子知识点**：
  - Spring Data JPA 核心用法
  - MyBatis-Plus 增强功能
  - 复杂查询实现对比
  - 性能与可维护性权衡
  - 多数据源配置
  - 读写分离实现
- **标签**：`#Java全栈/Spring`

### [[SpringBoot-配置管理与多环境|SpringBoot 配置管理与多环境]]
> 12-Factor 应用配置实践

- **四级子知识点**：
  - 配置文件优先级
  - 多环境 Profile 管理
  - 配置中心（Nacos/Apollo）
  - 敏感信息加密
  - 配置热更新
  - 环境变量与外部化配置
- **标签**：`#Java全栈/Spring`

---

## 📚 2.3 微服务架构

### [[SpringCloud-Alibaba组件体系|SpringCloud Alibaba 组件体系]]
> 国内微服务事实标准

- **四级子知识点**：
  - SpringCloud 版本对应关系
  - 服务注册与发现
  - 配置中心
  - 流量控制与熔断
  - 网关与负载均衡
  - 分布式事务
  - 链路追踪集成
- **标签**：`#Java全栈/微服务`

### [[Nacos-注册中心与配置中心|Nacos 注册中心与配置中心]]
> 阿里开源的服务治理组件

- **四级子知识点**：
  - Nacos 架构与部署
  - 服务注册发现机制
  - 配置管理与动态推送
  - 命名空间与分组
  - 集群与高可用
  - 与 Eureka/Consul 对比
- **标签**：`#Java全栈/微服务`

### [[Sentinel-流量控制与熔断|Sentinel 流量控制与熔断]]
> 微服务流量防护组件

- **四级子知识点**：
  - 流控规则（QPS/线程数）
  - 熔断降级策略
  - 热点参数限流
  - 系统自适应保护
  - 规则持久化
  - 与 Hystrix/Resilience4j 对比
- **标签**：`#Java全栈/微服务`

### [[Gateway-网关路由与鉴权|Gateway 网关路由与鉴权]]
> 微服务统一入口

- **四级子知识点**：
  - 路由配置与断言
  - 过滤器链（Global/Gateway）
  - 统一鉴权（JWT/OAuth2）
  - 限流与黑白名单
  - 跨域处理
  - 灰度发布
  - 与 Zuul/Kong 对比
- **标签**：`#Java全栈/微服务`

### [[OpenFeign-服务间调用|OpenFeign 服务间调用]]
> 声明式 HTTP 客户端

- **四级子知识点**：
  - Feign 接口定义
  - 负载均衡（LoadBalancer）
  - 超时与重试配置
  - 日志级别
  - 与 Sentinel 整合熔断
  - 传递请求头与鉴权
- **标签**：`#Java全栈/微服务`

### [[Seata-分布式事务|Seata 分布式事务]]
> 分布式事务解决方案

- **四级子知识点**：
  - AT 模式（自动补偿）
  - TCC 模式
  - Saga 模式
  - XA 模式
  - Seata Server 部署
  - 事务隔离与性能
- **标签**：`#Java全栈/微服务`

---

## 📚 2.4 分布式中间件

### [[Redis-分布式锁与缓存穿透|Redis 分布式锁与缓存穿透]]
> 缓存与分布式协调

- **四级子知识点**：
  - Redisson 分布式锁
  - 缓存穿透/击穿/雪崩
  - 布隆过滤器
  - 缓存一致性策略
  - Redis 集群与分片
  - 延迟队列实现
- **标签**：`#Java全栈/分布式`

### [[Kafka-消息队列与消费模型|Kafka 消息队列与消费模型]]
> 高吞吐消息中间件

- **四级子知识点**：
  - Kafka 架构（Broker/Partition/Replica）
  - 生产者确认机制
  - 消费者组与重平衡
  -  Exactly Once 语义
  - 消息顺序性保证
  - 与 RocketMQ/RabbitMQ 对比
- **标签**：`#Java全栈/分布式`

### [[RocketMQ-事务消息|RocketMQ 事务消息]]
> 阿里开源，支持事务消息

- **四级子知识点**：
  - RocketMQ 架构
  - 事务消息实现
  - 顺序消息
  - 延时消息
  - 死信队列
  - 与 Kafka 选型对比
- **标签**：`#Java全栈/分布式`

### [[Elasticsearch-全文检索引擎|Elasticsearch 全文检索引擎]]
> 分布式搜索与分析引擎

- **四级子知识点**：
  - ES 核心概念（Index/Document/Shard）
  - Mapping 与分词器
  - Query DSL 高级查询
  - 聚合分析
  - 性能优化
  - 与 Spring Data ES 集成
- **标签**：`#Java全栈/分布式`

---

## 📚 2.5 Java 对接 AI 大模型

### [[SpringAI-框架入门与模型抽象|Spring AI 框架入门与模型抽象]]
> Spring 官方 AI 应用框架

- **四级子知识点**：
  - Spring AI 核心抽象（ChatModel/EmbeddingModel）
  - Prompt 与 PromptTemplate
  - 输出解析（OutputParser）
  - 多模型支持（OpenAI/通义/智谱）
  - 函数调用（Function Calling）
  - 与 SpringBoot 集成模式
- **标签**：`#Java全栈/AI集成`
- **跨板块关联**：[[06-AI工程化/MOC-AI工程化|AI工程化]]

### [[LangChain4j-Agent与RAG实现|LangChain4j Agent 与 RAG 实现]]
> Java 版 LangChain，AI 应用开发框架

- **四级子知识点**：
  - LangChain4j 核心组件
  - RAG 检索增强实现
  - Agent 与工具调用
  - 记忆机制
  - 多模态支持
  - 与 Spring AI 对比选型
- **标签**：`#Java全栈/AI集成`

### [[Java调用OpenAI兼容API|Java 调用 OpenAI 兼容 API]]
> 底层 HTTP 调用，理解 SDK 封装

- **四级子知识点**：
  - OkHttp/Retrofit 调用
  - SSE 流式响应处理
  - 重试与降级策略
  - Token 计费与限流
  - 统一 SDK 封装
  - 代理与网络配置
- **标签**：`#Java全栈/AI集成`

### [[Java-向量数据库客户端|Java 向量数据库客户端]]
> 向量检索在 Java 生态的应用

- **四级子知识点**：
  - Milvus Java SDK
  - PgVector + JPA
  - Elasticsearch 向量检索
  - 向量入库与检索流程
  - 与 Embedding 模型配合
  - 性能优化
- **标签**：`#Java全栈/AI集成`

### [[Java-LLM接口封装与降级策略|Java LLM 接口封装与降级策略]]
> 生产级 LLM 接入的工程实践

- **四级子知识点**：
  - 统一 LLM 网关设计
  - 多模型路由与 fallback
  - 超时与熔断
  - 缓存与幂等
  - 可观测性（日志/指标/追踪）
  - 成本控制
- **标签**：`#Java全栈/AI集成`

---

## 📚 2.6 Java 工程化

### [[Maven-多模块与依赖管理|Maven 多模块与依赖管理]]
> Java 项目构建标准

- **四级子知识点**：
  - 多模块项目结构
  - 依赖传递与冲突解决
  - 插件配置与生命周期
  - 私服（Nexus）部署
  - 版本管理策略
  - 与 Gradle 对比
- **标签**：`#Java全栈/工程化`

### [[JUnit5与Mockito测试|JUnit5 与 Mockito 测试]]
> Java 测试体系

- **四级子知识点**：
  - JUnit5 新特性
  - Mockito Mock 与 Spy
  - SpringBoot Test 集成测试
  - Testcontainers 容器测试
  - 数据层测试
  - 测试覆盖率
- **标签**：`#Java全栈/工程化`

### [[SonarQube-代码质量门禁|SonarQube 代码质量门禁]]
> 代码质量管控

- **四级子知识点**：
  - SonarQube 规则配置
  - 质量门禁设置
  - 与 Maven/Gradle 集成
  - CI/CD 集成
  - 技术债务管理
  - 自定义规则
- **标签**：`#Java全栈/工程化`

---

## 🔗 学习依赖路径

```
JVM基础 → Spring → 微服务 → 分布式 → AI集成
   ↓         ↓          ↓          ↓
 并发编程   IoC/AOP   Nacos      Redis/Kafka
   ↓         ↓          ↓          ↓
   └──── 企业级项目实战（→ 10 项目实战）────┘
```

| 阶段 | 知识点 | 预计耗时 | 前置条件 |
|------|--------|----------|----------|
| 地基 | JVM + 并发 | 20h | Java 基础 |
| 框架 | SpringBoot 全套 | 24h | 地基 |
| 微服务 | SpringCloud Alibaba | 20h | 框架 |
| 分布式 | 中间件 | 16h | 微服务 |
| AI集成 | Spring AI + LangChain4j | 12h | 框架 + AI基础 |
| 实战 | 微服务电商系统 | 40h | 全部 |

---

## 🌐 跨板块关联

| 关联板块 | 关联点 | 连接笔记 |
|----------|--------|----------|
| [[06-AI工程化/MOC-AI工程化|AI工程化]] | Spring AI / LangChain4j 是 Java 侧 LLM 应用主路径 | [[Java-LLM接口封装与降级策略]] |
| [[03-Vue3TS前端/MOC-Vue3TS|Vue3TS前端]] | SpringBoot/Gateway 提供 API，Vue3 做管理后台 | [[Vue3对接SpringBoot-API]] |
| [[07-DevOps/MOC-DevOps|DevOps]] | JVM 容器化、K8s 调度、APM 监控 | [[Java-Docker镜像优化]] |
| [[01-Python全栈/MOC-Python全栈|Python全栈]] | Java 网关统一路由 Python AI 服务 | [[多语言后端统一网关]] |
| [[05-CS基础/MOC-CS基础|CS基础]] | 并发、JVM、网络的底层支撑 | [[JVM-内存模型与GC调优]] |

---

## 🌱 持续扩充方向

- [ ] Spring Boot 3.4+ 新特性
- [ ] 虚拟线程（Project Loom）生产实践
- [ ] Spring AI 演进与新模型支持
- [ ] GraalVM 原生镜像加速启动
- [ ] Dubbo 3.x 与云原生
- [ ] Service Mesh（Istio）与 Java 微服务
- [ ] Quarkus 云原生 Java 框架
- [ ] Java 23+ 模式匹配完整特性

---

## 📊 板块统计

- 二级分类：6 个
- 三级知识点（原子笔记）：26 篇
- 四级子知识点：约 140 个
- 枢纽笔记：1 篇
- 跨板块关联：5 条

---

[[10-四级知识框架/00-总控/四级框架总索引|← 返回四级框架总索引]] | [[Home|🏠 返回首页]]
