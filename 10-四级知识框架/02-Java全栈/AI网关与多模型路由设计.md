---
title: AI 网关与多模型路由设计
category: Java全栈
subcategory: AI应用开发
tags: [#Java全栈/AI应用, #AI结合/网关, #难度/高级, #类型/架构]
difficulty: 高级
pre: [[Java-SpringBoot自动配置原理]], [[Java-LLM接口统一封装]]
related: [[AI应用可观测性与Langfuse集成]], [[AI成本控制与Token计费优化]]
update: 2026-08-13
status: 完善
---

# AI 网关与多模型路由设计

## 1. 核心概述

AI 网关是 AI 应用的统一入口，屏蔽不同 LLM 厂商的 API 差异，提供统一的调用接口、模型路由、限流熔断、成本统计、日志追踪等能力。多模型路由让应用可以根据任务复杂度、成本、可用性自动选择最优模型，避免单一模型依赖。

**解决的场景问题**：
- 对接多个 LLM 厂商（OpenAI、Anthropic、通义、智谱），API 不统一
- 某个模型服务不可用时自动切换到备用模型
- 简单任务用便宜模型，复杂任务用强模型
- 统一限流、鉴权、成本统计
- 需要灰度测试新模型

## 2. 底层原理/核心逻辑

### AI 网关架构

```
客户端
    ↓
AI 网关 (Spring Boot)
    ├── 统一 API 层 (OpenAI 兼容接口)
    ├── 路由层 (模型选择策略)
    ├── 适配层 (各厂商 API 转换)
    ├── 中间件 (限流/鉴权/缓存/日志)
    └── 可观测性 (指标/追踪/成本)
    ↓
OpenAI / Anthropic / 通义 / 智谱 / 本地模型
```

### 路由策略

| 策略 | 原理 | 适用场景 |
|------|------|----------|
| 固定路由 | 配置指定模型 | 简单场景 |
| 复杂度路由 | 根据输入复杂度选模型 | 成本优化 |
| 故障转移 | 主模型失败切备用 | 高可用 |
| 灰度路由 | 按比例分流到新模型 | A/B 测试 |
| 租户路由 | 不同租户用不同模型 | 多租户 SaaS |
| 延迟优先 | 选响应最快的模型 | 低延迟需求 |

### 网关核心功能

```
1. 统一 API：所有模型用同一套接口（OpenAI 兼容）
2. 模型路由：智能选择模型
3. 限流熔断：保护后端服务
4. 请求缓存：相同请求复用结果
5. 成本统计：按用户/模型/功能统计
6. 日志追踪：完整调用链记录
7. 安全防护：注入检测、内容审核
```

## 3. 实操示例

### 统一 API 抽象

```java
// 统一请求模型
public record ChatRequest(
        String model,
        List<Message> messages,
        Double temperature,
        Integer maxTokens,
        Boolean stream
) {}

public record Message(String role, String content) {}

// 统一响应模型
public record ChatResponse(
        String id,
        String model,
        Choice choice,
        Usage usage
) {
    public record Choice(String content, String finishReason) {}
    public record Usage(int promptTokens, int completionTokens, int totalTokens) {}
}

// 统一 LLM 客户端接口
public interface LlmClient {
    ChatResponse chat(ChatRequest request);
    Flux<String> chatStream(ChatRequest request);
    String getProviderName();
}
```

### 多厂商适配器

```java
// OpenAI 适配器
@Component
public class OpenAiAdapter implements LlmClient {

    private final OpenAiApiClient apiClient;

    @Override
    public ChatResponse chat(ChatRequest request) {
        // 转换为 OpenAI 请求格式
        OpenAiRequest openAiRequest = OpenAiRequest.builder()
                .model(mapModel(request.model()))
                .messages(request.messages().stream()
                    .map(m -> new OpenAiMessage(m.role(), m.content()))
                    .toList())
                .temperature(request.temperature())
                .maxTokens(request.maxTokens())
                .build();

        OpenAiResponse response = apiClient.createChatCompletion(openAiRequest);

        // 转换为统一响应格式
        return new ChatResponse(
                response.getId(),
                request.model(),
                new ChatResponse.Choice(
                    response.getChoices().get(0).getMessage().getContent(),
                    response.getChoices().get(0).getFinishReason()
                ),
                new ChatResponse.Usage(
                    response.getUsage().getPromptTokens(),
                    response.getUsage().getCompletionTokens(),
                    response.getUsage().getTotalTokens()
                )
        );
    }

    @Override
    public Flux<String> chatStream(ChatRequest request) {
        return apiClient.streamChatCompletion(toOpenAiRequest(request))
                .map(this::toSseFormat);
    }

    @Override
    public String getProviderName() { return "openai"; }

    private String mapModel(String model) {
        return switch (model) {
            case "gpt-4o" -> "gpt-4o";
            case "gpt-4o-mini" -> "gpt-4o-mini";
            default -> model;
        };
    }
}

// 通义千问适配器（类似结构）
@Component
public class QwenAdapter implements LlmClient {
    // ... 实现转换逻辑
    @Override
    public String getProviderName() { return "qwen"; }
}
```

### 模型路由器

```java
@Service
public class ModelRouter {

    private final Map<String, LlmClient> clients;
    private final ModelRoutingConfig config;

    public ModelRouter(List<LlmClient> clientList, ModelRoutingConfig config) {
        this.clients = clientList.stream()
                .collect(Collectors.toMap(LlmClient::getProviderName, Function.identity()));
        this.config = config;
    }

    public LlmClient route(ChatRequest request) {
        String strategy = config.getStrategy();

        return switch (strategy) {
            case "fixed" -> fixedRoute(request);
            case "complexity" -> complexityRoute(request);
            case "failover" -> failoverRoute(request);
            default -> fixedRoute(request);
        };
    }

    private LlmClient fixedRoute(ChatRequest request) {
        String provider = config.getModelMapping().getOrDefault(
                request.model(), "openai");
        return clients.get(provider);
    }

    private LlmClient complexityRoute(ChatRequest request) {
        String content = request.messages().stream()
                .filter(m -> "user".equals(m.role()))
                .map(Message::content)
                .collect(Collectors.joining());

        Complexity complexity = classifyComplexity(content);

        return switch (complexity) {
            case SIMPLE -> clients.get(config.getSimpleModelProvider());
            case MEDIUM -> clients.get(config.getMediumModelProvider());
            case COMPLEX -> clients.get(config.getComplexModelProvider());
        };
    }

    private LlmClient failoverRoute(ChatRequest request) {
        List<String> providers = config.getFailoverChain();
        for (String provider : providers) {
            LlmClient client = clients.get(provider);
            if (isHealthy(client)) {
                return client;
            }
        }
        throw new RuntimeException("所有模型服务不可用");
    }

    private Complexity classifyComplexity(String text) {
        if (text.length() > 500 || containsComplexKeywords(text)) {
            return Complexity.COMPLEX;
        }
        if (text.length() < 50 || containsSimpleKeywords(text)) {
            return Complexity.SIMPLE;
        }
        return Complexity.MEDIUM;
    }

    private boolean isHealthy(LlmClient client) {
        // 健康检查逻辑
        return true;
    }

    enum Complexity { SIMPLE, MEDIUM, COMPLEX }
}
```

### 网关统一入口

```java
@RestController
@RequestMapping("/api/v1")
public class AiGatewayController {

    private final ModelRouter router;
    private final RateLimiter rateLimiter;
    private final CostTracker costTracker;
    private final RequestCache cache;

    @PostMapping("/chat/completions")
    public ChatResponse chat(@RequestBody ChatRequest request,
                             @RequestHeader("X-User-Id") String userId) {
        // 1. 限流
        rateLimiter.check(userId);

        // 2. 缓存检查
        String cached = cache.get(request);
        if (cached != null) {
            return new ChatResponse("cached", request.model(),
                new ChatResponse.Choice(cached, "cache"), null);
        }

        // 3. 路由选择模型
        LlmClient client = router.route(request);

        // 4. 调用模型
        long start = System.currentTimeMillis();
        ChatResponse response = client.chat(request);
        long latency = System.currentTimeMillis() - start;

        // 5. 成本统计
        costTracker.record(userId, request.model(),
                response.usage().promptTokens(),
                response.usage().completionTokens(), latency);

        // 6. 缓存结果
        if (request.temperature() != null && request.temperature() == 0) {
            cache.put(request, response.choice().content());
        }

        return response;
    }

    @PostMapping("/chat/completions/stream")
    public Flux<String> chatStream(@RequestBody ChatRequest request,
                                   @RequestHeader("X-User-Id") String userId) {
        rateLimiter.check(userId);
        LlmClient client = router.route(request);
        return client.chatStream(request);
    }
}
```

### 限流与熔断

```java
@Component
public class RateLimiter {

    private final Map<String, List<Long>> requestTimes = new ConcurrentHashMap<>();
    private final int maxRequestsPerMinute = 60;

    public void check(String userId) {
        long now = System.currentTimeMillis();
        List<Long> times = requestTimes.computeIfAbsent(userId, k ->
            Collections.synchronizedList(new ArrayList<>()));

        synchronized (times) {
            times.removeIf(t -> now - t > 60000);
            if (times.size() >= maxRequestsPerMinute) {
                throw new RateLimitException("请求过于频繁，请稍后再试");
            }
            times.add(now);
        }
    }
}

// 熔断：用 Resilience4j
@Configuration
public class CircuitBreakerConfig {

    @Bean
    public CircuitBreaker openAiCircuitBreaker() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
                .failureRateThreshold(50)
                .waitDurationInOpenState(Duration.ofSeconds(30))
                .slidingWindowSize(10)
                .build();
        return CircuitBreaker.of("openai", config);
    }
}
```

### Token 使用统计服务

```java
@Service
public class TokenUsageService {

    private final UsageRepository repository;

    public void record(String userId, String model,
                       int promptTokens, int completionTokens, long latencyMs) {
        UsageRecord record = new UsageRecord();
        record.setUserId(userId);
        record.setModel(model);
        record.setPromptTokens(promptTokens);
        record.setCompletionTokens(completionTokens);
        record.setTotalTokens(promptTokens + completionTokens);
        record.setLatencyMs(latencyMs);
        record.setCostUsd(calculateCost(model, promptTokens, completionTokens));
        record.setCreatedAt(LocalDateTime.now());
        repository.save(record);
    }

    private double calculateCost(String model, int prompt, int completion) {
        return switch (model) {
            case "gpt-4o" -> prompt / 1000.0 * 0.005 + completion / 1000.0 * 0.015;
            case "gpt-4o-mini" -> prompt / 1000.0 * 0.00015 + completion / 1000.0 * 0.0006;
            default -> 0.0;
        };
    }

    public UsageStats getStats(String userId, int days) {
        return repository.getStats(userId, LocalDateTime.now().minusDays(days));
    }
}
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 模型切换后效果差异大 | 不同模型能力不同 | 保持系统提示一致，做效果评估 |
| 流式响应格式不统一 | 各厂商 SSE 格式有差异 | 统一转换为 OpenAI SSE 格式 |
| 路由策略效果不好 | 复杂度分类规则简单 | 用小模型做分类器 |
| 缓存命中率低 | 用户输入变化大 | 用语义缓存 |
| 多模型成本统计不准 | 各厂商计费规则不同 | 维护统一的价格表 |

### 踩坑点

1. **不要只做接口转换**：网关的价值在路由、限流、缓存、统计
2. **流式响应的错误处理**：流中途出错要正确关闭连接
3. **模型映射要维护**：新模型上线要及时更新映射表
4. **超时设置要合理**：不同模型延迟差异大，超时要分别配置

### 优化方案

- **异步日志**：调用日志异步写入，不影响主流程
- **连接池**：每个厂商维护独立连接池
- **预热**：启动时预建连接，避免首次请求慢
- **动态配置**：路由规则、限流阈值可动态调整

## 5. 延伸拓展方向

- [[AI应用可观测性与Langfuse集成]]：网关的可观测性
- [[AI成本控制与Token计费优化]]：网关层的成本控制
- [[AI应用安全与Prompt注入防护]]：网关层的安全防护
- [[模型量化与本地部署实践]]：本地模型接入网关
- [[AI工作流编排引擎设计]]：网关 + 工作流

## 6. 参考资料

- [LiteLLM: Multi-LLM Gateway](https://github.com/BerriAI/litellm)
- [Portkey: AI Gateway](https://github.com/Portkey-AI/gateway)
- [Spring AI: Chat Models](https://docs.spring.io/spring-ai/reference/api/chat.html)
- [Resilience4j](https://resilience4j.readme.io/)

#待完善
