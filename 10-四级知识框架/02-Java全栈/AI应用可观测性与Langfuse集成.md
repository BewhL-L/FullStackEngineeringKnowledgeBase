---
title: AI 应用可观测性与 Langfuse 集成
category: Java全栈
subcategory: AI应用开发
tags: [#Java全栈/AI应用, #AI结合/可观测性, #难度/进阶, #类型/实战]
difficulty: 进阶
pre: [[Java-SpringBoot自动配置原理]], [[AI网关与多模型路由设计]]
related: [[AI应用测试与LLM输出评估]], [[AI成本控制与Token计费优化]]
update: 2026-08-13
status: 完善
---

# AI 应用可观测性与 Langfuse 集成

## 1. 核心概述

AI 应用的可观测性比传统应用更复杂：不仅要记录请求/响应，还要追踪 Token 消耗、Prompt 版本、工具调用、多轮 Agent 执行链路。Langfuse 是开源的 LLM 可观测性平台，提供 Tracing、Metrics、Evaluation、Prompt 管理等能力，帮助开发者理解 AI 应用的运行状态、发现性能瓶颈、评估输出质量。

**解决的场景问题**：
- 用户反馈回答不好，但不知道具体是哪次调用出了问题
- Token 消耗异常，无法定位是哪个功能导致的
- Agent 多步执行，无法看到完整的调用链路
- 想评估不同 Prompt 版本的效果差异
- 需要用户反馈（点赞/点踩）和 AI 输出关联

## 2. 底层原理/核心逻辑

### 可观测性三大支柱

```
Tracing（追踪）：
  记录每次 LLM 调用的完整链路
  - Span：一次 LLM 调用 / 工具调用 / 检索
  - Trace：一次用户请求的完整链路
  - 包含输入、输出、Token、延迟、元数据

Metrics（指标）：
  聚合统计数据
  - 调用量、延迟 P50/P95/P99
  - Token 消耗、成本
  - 错误率、缓存命中率

Evaluation（评估）：
  输出质量评估
  - LLM-as-Judge 自动评分
  - 用户反馈收集
  - 数据集批量评估
```

### Langfuse 核心概念

| 概念 | 说明 |
|------|------|
| Trace | 一次完整的用户请求链路 |
| Span | 链路中的一个步骤（LLM调用/工具/检索） |
| Generation | LLM 调用类型的 Span |
| Score | 对 Trace/Span 的评分（人工或自动） |
| Prompt | 受版本管理的 Prompt 模板 |
| Dataset | 评估用的测试数据集 |

### 追踪数据结构

```
Trace (用户一次对话)
├── Span: RAG 检索 (100ms)
│   └── Span: 向量数据库查询 (50ms)
├── Generation: LLM 调用 (2000ms, 1500 tokens)
├── Span: 工具调用 (300ms)
│   └── Generation: 工具参数解析 (100ms)
└── Generation: 最终回答 (1500ms, 800 tokens)
```

## 3. 实操示例

### Langfuse Java SDK 集成

```xml
<!-- pom.xml -->
<dependency>
    <groupId>com.langfuse</groupId>
    <artifactId>langfuse-java</artifactId>
    <version>2.0.0</version>
</dependency>
```

```java
@Configuration
public class LangfuseConfig {

    @Bean
    public Langfuse langfuse(
            @Value("${langfuse.public-key}") String publicKey,
            @Value("${langfuse.secret-key}") String secretKey,
            @Value("${langfuse.host:https://cloud.langfuse.com}") String host) {
        return Langfuse.builder()
                .publicKey(publicKey)
                .secretKey(secretKey)
                .host(host)
                .build();
    }
}
```

### AOP 切面自动追踪

```java
@Aspect
@Component
public class LlmTracingAspect {

    private final Langfuse langfuse;

    public LlmTracingAspect(Langfuse langfuse) {
        this.langfuse = langfuse;
    }

    @Around("@annotation(aiTrace)")
    public Object trace(ProceedingJoinPoint joinPoint, AITrace aiTrace) throws Throwable {
        // 创建 Trace
        Trace trace = langfuse.trace(TraceCreate.builder()
                .name(aiTrace.value())
                .metadata(Map.of("method", joinPoint.getSignature().getName()))
                .build());

        // 创建 Generation Span
        Generation generation = trace.generation(GenerationCreate.builder()
                .name(aiTrace.value())
                .model(aiTrace.model())
                .build());

        long start = System.currentTimeMillis();
        try {
            Object result = joinPoint.proceed();

            // 记录成功
            generation.update(GenerationUpdate.builder()
                    .endTime(new Date())
                    .completionStartTime(new Date(start))
                    .status(Status.SUCCESS)
                    .build());

            return result;
        } catch (Exception e) {
            // 记录失败
            generation.update(GenerationUpdate.builder()
                    .endTime(new Date())
                    .status(Status.ERROR)
                    .metadata(Map.of("error", e.getMessage()))
                    .build());
            throw e;
        }
    }
}

// 自定义注解
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface AITrace {
    String value();
    String model() default "gpt-4o";
}
```

### 手动追踪 Agent 执行

```java
@Service
public class AgentService {

    private final Langfuse langfuse;
    private final ChatModel chatModel;

    public String runAgent(String userInput, String sessionId) {
        // 1. 创建 Trace
        Trace trace = langfuse.trace(TraceCreate.builder()
                .name("agent-execution")
                .sessionId(sessionId)
                .userId("user-123")
                .metadata(Map.of("input", userInput))
                .build());

        try {
            // 2. 检索 Span
            Span retrievalSpan = trace.span(SpanCreate.builder()
                    .name("rag-retrieval")
                    .build());

            List<Document> docs = vectorStore.similaritySearch(userInput, 5);
            retrievalSpan.update(SpanUpdate.builder()
                    .endTime(new Date())
                    .metadata(Map.of("doc_count", docs.size()))
                    .build());

            // 3. LLM 调用 Generation
            Generation generation = trace.generation(GenerationCreate.builder()
                    .name("llm-call")
                    .model("gpt-4o")
                    .input(List.of(
                        Map.of("role", "system", "content", "你是一个助手"),
                        Map.of("role", "user", "content", userInput)
                    ))
                    .build());

            ChatResponse response = chatModel.call(
                new Prompt(List.of(
                    new SystemMessage("你是一个助手"),
                    new UserMessage(userInput + "\n参考资料：" + docs)
                ))
            );

            String answer = response.getResult().getOutput().getText();

            generation.update(GenerationUpdate.builder()
                    .output(answer)
                    .usage(Map.of(
                        "promptTokens", response.getMetadata().getUsage().getPromptTokens(),
                        "completionTokens", response.getMetadata().getUsage().getCompletionTokens(),
                        "totalTokens", response.getMetadata().getUsage().getTotalTokens()
                    ))
                    .endTime(new Date())
                    .build());

            // 4. 给 Trace 打分
            trace.score(ScoreCreate.builder()
                    .name("quality")
                    .value(0.8)
                    .comment("回答质量良好")
                    .build());

            return answer;

        } finally {
            langfuse.flush();
        }
    }
}
```

### 用户反馈收集

```java
@RestController
@RequestMapping("/api/feedback")
public class FeedbackController {

    private final Langfuse langfuse;

    @PostMapping("/{traceId}")
    public void submitFeedback(@PathVariable String traceId,
                               @RequestBody FeedbackRequest request) {
        langfuse.score(ScoreCreate.builder()
                .traceId(traceId)
                .name(request.type())  // "thumbs_up" / "thumbs_down"
                .value(request.value()) // 1.0 / 0.0
                .comment(request.comment())
                .build());
        langfuse.flush();
    }

    public record FeedbackRequest(String type, double value, String comment) {}
}
```

### 指标统计服务

```java
@Service
public class UsageAnalyticsService {

    private final Langfuse langfuse;

    public DailyStats getDailyStats(LocalDate date) {
        // 从 Langfuse API 获取统计数据
        var metrics = langfuse.fetchMetrics(MetricsQuery.builder()
                .fromDate(date.atStartOfDay())
                .toDate(date.plusDays(1).atStartOfDay())
                .build());

        return new DailyStats(
                metrics.getTotalCalls(),
                metrics.getTotalTokens(),
                metrics.getTotalCost(),
                metrics.getLatencyP50(),
                metrics.getLatencyP95(),
                metrics.getErrorRate()
        );
    }

    public List<ModelUsage> getModelUsageBreakdown(LocalDate date) {
        // 按模型分组统计
        return langfuse.fetchDailyMetrics(DailyMetricsQuery.builder()
                .fromDate(date.atStartOfDay())
                .toDate(date.plusDays(1).atStartOfDay())
                .groupBy("model")
                .build())
            .stream()
            .map(m -> new ModelUsage(
                m.getModel(),
                m.getCalls(),
                m.getTokens(),
                m.getCost()
            ))
            .toList();
    }

    public record DailyStats(int calls, int tokens, double cost,
                             double latencyP50, double latencyP95, double errorRate) {}
    public record ModelUsage(String model, int calls, int tokens, double cost) {}
}
```

### Spring Boot Actuator 集成

```java
@Component
public class AiMetricsEndpoint implements MeterBinder {

    private final MeterRegistry registry;
    private final AtomicInteger activeRequests = new AtomicInteger(0);

    @Override
    public void bindTo(MeterRegistry registry) {
        Gauge.builder("ai.active.requests", activeRequests, AtomicInteger::get)
                .description("活跃 AI 请求数")
                .register(registry);

        Counter.builder("ai.requests.total")
                .description("AI 请求总数")
                .tag("model", "gpt-4o")
                .register(registry);

        Timer.builder("ai.request.latency")
                .description("AI 请求延迟")
                .publishPercentiles(0.5, 0.95, 0.99)
                .register(registry);
    }

    public void recordRequest(String model, long latencyMs, boolean success) {
        activeRequests.incrementAndGet();
        try {
            registry.counter("ai.requests.total",
                    "model", model,
                    "status", success ? "success" : "error")
                    .increment();
            registry.timer("ai.request.latency", "model", model)
                    .record(latencyMs, TimeUnit.MILLISECONDS);
        } finally {
            activeRequests.decrementAndGet();
        }
    }
}
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 追踪数据丢失 | 应用崩溃时未 flush | 用 try/finally 确保 flush |
| 性能影响大 | 同步发送追踪数据 | 用异步批量发送 |
| Trace 关联不上 | sessionId/userId 没传 | 统一在拦截器中注入 |
| Token 统计不准 | 流式响应没有 usage | 结束后手动计算 |
| 数据量太大成本高 | 全量采集 | 采样率配置，只记录异常 |

### 踩坑点

1. **不要在 finally 外 flush**：异常时也要确保数据发送
2. **流式调用要特殊处理**：流式结束后再更新 Generation
3. **Prompt 要记录完整**：包括系统提示和变量，方便复现
4. **用户 ID 要脱敏**：不要记录真实手机号、邮箱

### 优化方案

- **采样策略**：正常请求 10% 采样，错误请求 100% 记录
- **批量发送**：攒一批再发送，减少网络开销
- **本地缓冲**：先写本地文件，后台异步上报
- **数据脱敏**：自动检测并脱敏敏感信息

## 5. 延伸拓展方向

- [[AI应用测试与LLM输出评估]]：评估数据和追踪结合
- [[AI成本控制与Token计费优化]]：Token 统计用于成本分析
- [[AI网关与多模型路由设计]]：网关层统一埋点
- [[Prompt工程与版本管理]]：Langfuse Prompt 管理
- [[多Agent协作模式实现]]：Agent 链路追踪

## 6. 参考资料

- [Langfuse 官方文档](https://langfuse.com/docs)
- [Langfuse Java SDK](https://github.com/langfuse/langfuse-java)
- [OpenTelemetry: LLM Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Spring Boot Actuator](https://spring.io/projects/spring-boot)

#待完善
