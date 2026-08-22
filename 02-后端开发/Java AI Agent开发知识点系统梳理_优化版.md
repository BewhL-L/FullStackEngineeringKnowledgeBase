---
title: Java AI Agent 开发知识点系统梳理
tags: [后端, Java, AIAgent, SpringAI, LangChain4j, AIGC, 面试]
created: 2026-08-13
updated: 2026-08-13
---

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。

# Java AI Agent 开发知识点系统梳理（优化版）

> **文档说明**：系统梳理 Java 生态下 AI Agent 开发的核心技术，涵盖 Spring AI、LangChain4j 两大主流框架，以及工具调用、RAG、记忆管理、多 Agent 协作、向量数据库集成等实战内容。

---

## 1. 概述

Java 生态在 AI Agent 开发领域已有成熟方案，核心框架包括 **Spring AI**（Spring 官方推出，与 Spring Boot 深度集成）和 **LangChain4j**（Java 版 LangChain，功能全面）。Java 开发者可基于现有技术栈快速构建企业级 AI Agent 应用。

**核心能力矩阵**：

| 能力 | Spring AI | LangChain4j |
|------|-----------|-------------|
| LLM 接入 | OpenAI、Azure、Ollama、国内模型 | 同上 + 更多 |
| Function Calling | 支持 | 支持（@Tool） |
| RAG | 基础支持 | 深度支持 |
| 记忆管理 | ChatMemory | ChatMemory |
| 多 Agent | 有限 | AiServices 多 Agent |
| Spring 集成 | 原生 | 需适配 |
| 向量数据库 | 多家支持 | 多家支持 |

---


---
## 2. Spring AI

### 2.1 定位与核心概念

Spring AI 是 Spring 官方推出的 AI 应用开发框架，设计哲学与 Spring 生态一致，提供自动配置、Starter 依赖、统一抽象。

**核心抽象**：

| 接口 | 说明 |
|------|------|
| `ChatModel` | 聊天模型统一接口 |
| `EmbeddingModel` | 向量化模型 |
| `Prompt` | 提示词封装（含消息列表） |
| `ChatResponse` | 模型响应 |
| `Advisor` | 拦截器（记忆、日志、防护） |
| `VectorStore` | 向量存储接口 |
| `Document` | 文档封装（内容+元数据） |

> 🔍 **知识点深度解析**
>
> **作用**：用最小配置跑通一个可对话的 Spring AI 应用，验证框架自动配置与模型接入能力。
>
> **原理**：引入 starter 后，AutoConfiguration 根据 api-key 自动创建 ChatModel bean；@RestController 注入 ChatModel，chatModel.call(String) 内部构造 Prompt 并调用模型 HTTP API，返回生成文本。
>
> **用法要点**：① 只需配置 spring.ai.openai.api-key 与 model；② call 接受 String/Prompt，返回 String/ChatResponse；③ temperature 控制随机性（0 稳定、1 发散）；④ 生产环境 api-key 用环境变量 ${OPENAI_API_KEY}；⑤ 多模型用不同前缀配置（如 spring.ai.dashscope）。

### 2.2 快速开始

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
</dependency>
```

```yaml

> 🔍 **知识点深度解析**
>
> **作用**：Spring AI 快速集成：引入 starter、配置 API Key、注入 ChatClient 即可调用大模型。
>
> **原理**：添加 spring-ai-openai-spring-boot-starter 依赖，在 application.yml 配置 spring.ai.openai.api-key 和 base-url。注入 ChatClient.Builder 构建 ChatClient，调用 .prompt().user("问题").call().content() 获得响应。Spring Boot 自动配置根据 classpath 和配置属性创建 ChatModel/ChatClient Bean。
>
> **用法要点**：① 引入 spring-ai-bom 管理版本，starter 自动装配  ② application.yml 配置 api-key/base-url/chat.options.model  ③ ChatClient 是核心入口，支持 prompt/user/system/call/stream  ④ call() 同步返回，stream() 返回 Flux 流式响应  ⑤ 面试常考：Spring AI 自动配置原理、ChatClient 用法

# application.yml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      chat:
        options:
          model: gpt-4o
          temperature: 0.7
```

```java
@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private final ChatModel chatModel;

    public ChatController(ChatModel chatModel) {
        this.chatModel = chatModel;
    }

    @GetMapping
    public String chat(@RequestParam String message) {
        return chatModel.call(message);
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：让 LLM 在回答时调用本地 Java 方法获取实时数据（天气、库存等），突破模型静态知识限制，实现"工具增强"。
>
> **原理**：用 @Description 把方法用途传给模型；模型判断需要工具时返回函数名+JSON 参数，Spring AI 反射调用对应 @Bean Function，把结果回填 Prompt 后让模型生成最终回答。
>
> **用法要点**：① 工具方法用 @Bean + @Description 标注（描述越清楚模型越会用）；② 参数建议用 record，字段加 @Description 帮助理解；③ 用 OpenAiChatOptions.builder().withFunction("beanName") 启用；④ 工具应幂等、快速、可降级；⑤ 写操作不要直接暴露给模型，需人工确认。

### 2.3 Function Calling（工具调用）

```java
// 定义工具函数
@Configuration
public class ToolConfig {

    @Bean
    @Description("查询指定城市的当前天气")
    public Function<WeatherRequest, WeatherResponse> weatherService() {
        return request -> {
            // 调用天气API
            return new WeatherResponse(request.city(), "晴", 25);
        };
    }

    public record WeatherRequest(String city) {}
    public record WeatherResponse(String city, String weather, int temp) {}
}

// 使用工具
@GetMapping("/agent")
public String agent(@RequestParam String message) {
    var prompt = new Prompt(message,
        OpenAiChatOptions.builder()
            .withFunction("weatherService")
            .build());
    return chatModel.call(prompt).getResult().getOutput().getText();
}
```


> 🔍 **知识点深度解析**
>
> **作用**：Function Calling 让 LLM 能调用 Java 方法获取外部数据或执行操作，是 Agent 工具能力的基础。
>
> **原理**：定义 @Bean Function<Request, Response> 并在 ChatClient 中通过 .functions("beanName") 注册。LLM 返回工具调用请求（函数名+JSON 参数），Spring AI 自动调用对应 Java 方法，将结果序列化为 JSON 回传 LLM，LLM 再生成最终回答。支持多轮工具调用和函数回调。
>
> **用法要点**：① @Bean 实现 Function<I,O> 接口，方法名即函数名  ② @JsonPropertyDescription 描述参数，帮助 LLM 理解  ③ .functions("beanName") 注册到 ChatClient  ④ Spring AI 自动处理 JSON 序列化和方法调用  ⑤ 面试常考：Function Calling 流程、参数描述、多工具调用

### 2.4 RAG 实现

```java
@Service
public class RagService {

    private final VectorStore vectorStore;
    private final ChatModel chatModel;

    // 文档入库
    public void ingest(String content) {
        var documents = List.of(new Document(content));
        vectorStore.add(documents);
    }

    // 检索增强问答
    public String query(String question) {
        var docs = vectorStore.similaritySearch(question);
        var context = docs.stream()
            .map(Document::getContent)
            .collect(Collectors.joining("\n"));

        var prompt = """
            请根据以下上下文回答问题。如果上下文中没有相关信息，请说"我不知道"。

            上下文：%s

            问题：%s
            """.formatted(context, question);

        return chatModel.call(prompt);
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：检索增强生成（RAG）让模型基于私有/最新文档回答，缓解知识滞后与幻觉，是企业落地的核心模式。
>
> **原理**：文档切分→Embedding 向量化→存入 VectorStore；查询时把问题向量化做相似度检索，命中文档作为上下文拼进 Prompt，模型据此生成答案。
>
> **用法要点**：① 入库用 vectorStore.add(List<Document>)；② 检索用 similaritySearch 返回 Top-K 文档；③ 提示加"若无相关信息请说不知道"约束；④ 切分粒度影响召回（太小碎片化、太大噪声多）；⑤ 可加 rerank 重排提升精度。

### 2.5 记忆管理

```java
@Bean
public ChatClient chatClient(ChatModel chatModel) {
    return ChatClient.builder(chatModel)
        .defaultAdvisors(
            new MessageChatMemoryAdvisor(
                new InMemoryChatMemory(), "default", 10))
        .build();
}

// 带记忆的对话
chatClient.prompt()
    .user(message)
    .advisors(a -> a.param("chat_memory_id", sessionId))
    .call()
    .content();
```

> 🔍 **知识点深度解析**
>
> **作用**：Spring AI 让 Java/Spring 开发者用熟悉的方式构建 AI 应用，无需学习新的技术栈。
>
> **原理**：Spring AI 通过 `ChatModel` 接口统一不同 LLM 提供商，底层用 `RestClient` 调用各厂商 API。Function Calling 利用 OpenAI 的工具调用协议：LLM 判断需要调用工具时返回函数名和参数，Spring AI 反射调用对应 `@Bean` Function，将结果返回 LLM 继续生成。RAG 流程为：文档切分 → Embedding 向量化 → 存入 VectorStore → 查询时相似度检索 → 上下文拼接 Prompt → LLM 生成。记忆通过 `ChatMemoryAdvisor` 拦截器自动维护对话历史，按 conversationId 隔离。
>
> **用法要点**：① 用 Starter 自动配置，只需配置 api-key；② Function Calling 的 `@Description` 是 LLM 理解工具的关键；③ 向量数据库选 Redis/PGVector/Milvus 等；④ 生产环境用 `ChatClient` 而非直接 `ChatModel`；⑤ 面试常考：Spring AI 核心抽象、Function Calling 原理、RAG 流程、记忆管理。

---


---
## 3. LangChain4j

### 3.1 定位与核心概念

LangChain4j 是 Java 版 LangChain，功能更全面，支持更复杂的 Agent 场景，不依赖 Spring 也可独立使用。

**核心组件**：

| 组件 | 说明 |
|------|------|
| `ChatLanguageModel` | LLM 模型封装 |
| `AiServices` | 核心抽象，接口即 Agent |
| `@Tool` | 工具方法注解 |
| `ChatMemory` | 对话记忆 |
| `EmbeddingStore` | 向量存储 |
| `DocumentSplitter` | 文档切分 |
| `ContentRetriever` | 内容检索 |

> 🔍 **知识点深度解析**
>
> **作用**：LangChain4j 是 Java 版 LangChain，功能全面、框架无关，适合复杂 Agent 与链式编排场景。
>
> **原理**：核心是 AiServices（接口即 Agent），框架用动态代理把接口方法映射到 LLM 调用；ChatMemory/ContentRetriever/EmbeddingStore 等组件可插拔组合成流水线。
>
> **用法要点**：① 不依赖 Spring 也能用（也可适配 Spring）；② 核心组件：ChatLanguageModel、AiServices、@Tool、ChatMemory、EmbeddingStore；③ RAG/多 Agent 上比 Spring AI 更开箱即用；④ 模型用工厂（如 OpenAiChatModel.builder()）创建；⑤ 选型：Spring 生态优先 Spring AI，复杂 Agent 优先 LangChain4j。

### 3.2 AiServices（核心抽象）

```java
// 定义 Agent 接口
interface CustomerSupportAgent {
    String chat(String userMessage);
}

// 创建 Agent 实例
CustomerSupportAgent agent = AiServices.builder(CustomerSupportAgent.class)
    .chatLanguageModel(model)
    .chatMemory(MessageWindowChatMemory.withMaxMessages(20))
    .tools(new OrderTools(), new PaymentTools())
    .contentRetriever(embeddingStoreContentRetriever)
    .build();

// 使用
String response = agent.chat("我的订单什么时候发货？");
```

> 🔍 **知识点深度解析**
>
> **作用**：AiServices 是 LangChain4j 的核心抽象，用一个接口定义 Agent 行为，免去手写模型调用样板。
>
> **原理**：AiServices.builder(接口).chatLanguageModel(...).build() 通过动态代理生成实现类；调用接口方法时框架组装消息、调用模型，必要时触发工具，并把结果映射回返回类型。
>
> **用法要点**：① 接口方法可声明参数（转 user message）与返回值（String 或 POJO）；② 链式挂 chatMemory、tools、contentRetriever；③ MessageWindowChatMemory 控制历史窗口大小；④ 返回类型支持 POJO（框架解析 JSON）；⑤ 一个接口即一个 Agent，多 Agent 可互相调用。

### 3.3 工具调用（@Tool）

```java
class OrderTools {

    @Tool("根据订单号查询订单状态")
    String getOrderStatus(@P("订单号") String orderId) {
        return orderService.getStatus(orderId);
    }

    @Tool("取消指定订单")
    String cancelOrder(@P("订单号") String orderId) {
        return orderService.cancel(orderId);
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：@Tool 把普通 Java 方法暴露给模型作为工具，比 Spring AI 的 @Bean 方式更贴近业务类，调用更自然。
>
> **原理**：标注 @Tool 的方法被框架扫描为工具，@P 描述参数；模型需要时用工具名+JSON 参数调用，结果回填后继续生成。
>
> **用法要点**：① @Tool("描述") 的描述要清晰准确；② 参数用 @P("说明") 标注；③ 多个工具类通过 .tools(obj1, obj2) 注册；④ 工具方法应 public、无副作用或显式确认；⑤ 与 AiServices 配合，无需定义 @Bean。

### 3.4 RAG 高级用法

```java
// 文档入库
DocumentSplitter splitter = DocumentSplitters.recursive(500, 50);
List<TextSegment> segments = splitter.split(document);
embeddingStore.addAll(segments);

// 检索增强
ContentRetriever retriever = EmbeddingStoreContentRetriever.builder()
    .embeddingStore(embeddingStore)
    .embeddingModel(embeddingModel)
    .maxResults(5)
    .minScore(0.7)
    .build();

// 集成到 Agent
AiServices.builder(Agent.class)
    .contentRetriever(retriever)
    .build();
```

> 🔍 **知识点深度解析**
>
> **作用**：LangChain4j 提供成熟的 RAG 流水线组件，支持切分、嵌入、检索、重排全链路，召回质量更可控。
>
> **原理**：DocumentSplitter 把文档切成 TextSegment，EmbeddingStore 存入向量；ContentRetriever 按 maxResults/minScore 检索；集成进 AiServices 后自动在每次对话前注入相关上下文。
>
> **用法要点**：① 切分用 DocumentSplitters.recursive(size, overlap)；② 重叠窗口 overlap 减少切分边界信息丢失；③ ContentRetriever 设 minScore 过滤低质量命中；④ 可接 reranking（如 Cohere）提升精度；⑤ 检索结果自动作为 user 上下文参与生成。

### 3.5 多 Agent 协作

```java
// 专家 Agent 定义
interface Researcher { String research(String topic); }
interface Writer { String write(String research); }

// 协调器
Researcher researcher = AiServices.builder(Researcher.class)
    .chatLanguageModel(model).tools(searchTool).build();

Writer writer = AiServices.builder(Writer.class)
    .chatLanguageModel(model).build();

// 顺序协作
String research = researcher.research("AI Agent 最新进展");
String article = writer.write(research);
```

---

> 🔍 **知识点深度解析**
>
> **作用**：把复杂任务拆解给多个专家 Agent 协作完成，模拟"团队工作"，提升复杂任务的处理质量。
>
> **原理**：分别构建不同职责的 AiServices Agent（研究员/写手），主流程按顺序或并行调用它们，前一个输出作为后一个输入，形成流水线。
>
> **用法要点**：① 每个 Agent 职责单一（researcher/writer）；② 顺序协作：A 结果喂给 B；③ 并行可用 CompletableFuture；④ 辩论模式让 Agent 互相评审提升质量；⑤ 注意上下文传递与 token 成本控制。


---
## 4. 向量数据库集成

| 数据库 | Spring AI | LangChain4j | 适用场景 |
|--------|-----------|-------------|----------|
| **Redis** | ✅ | ✅ | 已有 Redis 基础设施 |
| **PGVector** | ✅ | ✅ | PostgreSQL 扩展，事务支持 |
| **Milvus** | ✅ | ✅ | 大规模向量检索 |
| **Elasticsearch** | ✅ | ✅ | 混合检索（向量+关键词） |
| **Chroma** | ✅ | ✅ | 轻量本地开发 |
| **Qdrant** | ✅ | ✅ | 高性能 Rust 实现 |

---


---
## 5. 国内大模型接入

| 模型 | Spring AI 支持 | LangChain4j 支持 | 接入方式 |
|------|---------------|-----------------|----------|
| **通义千问** | ✅ Starter | ✅ | dashscope SDK / OpenAI 兼容 |
| **文心一言** | ✅ | ✅ | 千帆 SDK |
| **豆包** | ✅ | ✅ | OpenAI 兼容接口 |
| **DeepSeek** | ✅ | ✅ | OpenAI 兼容接口 |
| **智谱 GLM** | ✅ | ✅ | OpenAI 兼容接口 |
| **Ollama（本地）** | ✅ | ✅ | 本地部署，免费 |

```yaml
# 通义千问配置示例
spring:
  ai:
    dashscope:
      api-key: ${DASHSCOPE_API_KEY}
      chat:
        options:
          model: qwen-max
```

---


---
## 6. 企业级最佳实践

### 6.1 异常处理与降级

```java
try {
    return chatModel.call(prompt);
} catch (ApiException e) {
    // 限流：退避重试
    if (e.getCode() == 429) {
        Thread.sleep(1000);
        return chatModel.call(prompt);
    }
    // 降级：切换备用模型
    return fallbackModel.call(prompt);
}
```

> 🔍 **知识点深度解析**
>
> **作用**：LLM API 存在限流/超时/不稳定，需要容错保证 AI 服务可用性。
>
> **原理**：捕获 ApiException，429 限流做指数退避重试，其他异常切换 fallbackModel；配合熔断（Sentinel/Resilience4j）防止级联故障。
>
> **用法要点**：① 429 用指数退避重试；② 配置 fallback 备用模型兜底；③ 用 Resilience4j/Sentinel 做熔断限流；④ 返回友好降级文案而非抛错；⑤ 设置超时避免无限等待。

### 6.2 成本控制

- 模型分级：简单任务用 qwen-turbo，复杂任务用 gpt-4o
- Token 统计：记录每次调用的输入/输出 Token
- 缓存：相同查询缓存结果
- Prompt 精简：去除冗余上下文

> 🔍 **知识点深度解析**
>
> **作用**：大模型按 token 计费，需从架构层面控制成本，避免预算失控。
>
> **原理**：按任务复杂度选模型（简单用便宜、复杂用强），缓存相同查询结果，统计 token 用量。
>
> **用法要点**：① 模型分级路由（qwen-turbo / gpt-4o）；② 相同查询加缓存（Redis）；③ 统计输入/输出 token；④ 精简 Prompt 减少冗余 token；⑤ 批量接口进一步降本。

### 6.3 安全防护

- 输入过滤：检测 Prompt 注入
- 输出审核：敏感内容过滤
- 工具权限：最小权限原则，写操作需确认
- 数据脱敏：敏感信息不上传云端

---

> 🔍 **知识点深度解析**
>
> **作用**：AI 应用面临 Prompt 注入、数据泄露、越权操作风险，需多层防护保障合规与安全。
>
> **原理**：输入过滤检测注入，输出审核过滤违规内容，工具按最小权限开放，敏感数据脱敏/不出域。
>
> **用法要点**：① 输入做注入检测与指令隔离；② 输出用审核 API 或分类模型；③ 写操作工具需确认/审批；④ 敏感信息脱敏、隐私数据用本地模型；⑤ 限流防滥用。

## 6.4 可观测性与监控

```java
// Micrometer 指标统计
@Service
public class ObservableChatService {

    private final ChatModel chatModel;
    private final MeterRegistry meterRegistry;

    public String chatWithMetrics(String message) {
        long start = System.currentTimeMillis();
        try {
            String result = chatModel.call(message);
            meterRegistry.counter("ai.chat.success").increment();
            meterRegistry.timer("ai.chat.latency").record(System.currentTimeMillis() - start, TimeUnit.MILLISECONDS);
            return result;
        } catch (Exception e) {
            meterRegistry.counter("ai.chat.error", "type", e.getClass().getSimpleName()).increment();
            throw e;
        }
    }
}

// 日志记录 Advisor
public class LoggingAdvisor implements CallAdvisor {
    private static final Logger log = LoggerFactory.getLogger(LoggingAdvisor.class);

    @Override
    public Prompt adviseCall(Prompt prompt, CallAdvisorContext context) {
        log.info("AI 请求: prompt={}, model={}", prompt.getContents(), context.getChatModel());
        return prompt;
    }

    @Override
    public ChatResponse adviseCall(ChatResponse response, CallAdvisorContext context) {
        log.info("AI 响应: tokens={}", response.getMetadata().getUsage().getTotalTokens());
        return response;
    }
}
```

---

> 🔍 **知识点深度解析**
>
> **作用**：监控 token、延迟、成功率，保障 AI 服务可运维、可优化。
>
> **原理**：用 Micrometer 记录指标，LoggingAdvisor 实现 CallAdvisor 在请求前后记录 prompt/响应 token，数据送 Prometheus+Grafana。
>
> **用法要点**：① 记录成功率、延迟、token 消耗（counter/timer）；② Advisor 实现 CallAdvisor 拦截请求响应；③ 配合 Prometheus+Grafana 看板；④ 日志保留 prompt/模型/耗时便于排查；⑤ 对错误率/成本突增配置告警。

## 6.5 测试策略（Mock LLM）

```java
// 使用 MockChatModel 进行单元测试
@SpringBootTest
class AgentServiceTest {

    @MockBean
    private ChatModel chatModel;

    @Autowired
    private AgentService agentService;

    @Test
    void testChat() {
        when(chatModel.call(any(Prompt.class)))
            .thenReturn(new ChatResponse(List.of(
                new Generation(new AssistantMessage("Mock 回复"))
            )));

        String result = agentService.chat("你好");
        assertEquals("Mock 回复", result);
        verify(chatModel).call(any(Prompt.class));
    }
}

// 集成测试：使用 Ollama 本地模型
@SpringBootTest
class AgentIntegrationTest {

    @Autowired
    private ChatModel chatModel;  // 配置为 Ollama 本地模型

    @Test
    void testRealModel() {
        String result = chatModel.call("用一句话介绍Java");
        assertNotNull(result);
        assertTrue(result.length() > 0);
    }
}
```

---

> 🔍 **知识点深度解析**
>
> **作用**：用 Mock 隔离外部 LLM，保证 Agent 逻辑可测、稳定、快速，不依赖云端额度。
>
> **原理**：@MockBean 替换 ChatModel 返回固定 ChatResponse，验证业务编排；集成测试用 Ollama 本地模型做真实调用。
>
> **用法要点**：① 单测用 MockChatModel/@MockBean 返回预设响应；② 用 verify 验证调用次数与参数；③ 集成测试用 Ollama 本地模型避免云端消耗；④ 覆盖工具调用、RAG 检索等逻辑；⑤ 不依赖外部 API，CI 可稳定跑。

## 6.6 Spring AI ChatClient 高级用法

```java
// ChatClient 是 Spring AI 1.0+ 推荐的高级 API
@Bean
public ChatClient chatClient(ChatModel chatModel, VectorStore vectorStore) {
    return ChatClient.builder(chatModel)
        .defaultSystem("你是一个专业的技术顾问")
        .defaultAdvisors(
            new MessageChatMemoryAdvisor(new InMemoryChatMemory(), "default", 10),
            new QuestionAnswerAdvisor(vectorStore, SearchRequest.defaults())
        )
        .defaultTools("weatherService", "calculatorService")
        .build();
}

// 调用示例
String answer = chatClient.prompt()
    .user("北京今天天气怎么样？适合穿什么？")
    .advisors(a -> a.param("chat_memory_id", "session-123"))
    .call()
    .content();

// 流式调用
Flux<String> stream = chatClient.prompt()
    .user("写一篇关于Spring AI的文章")
    .stream()
    .content();
```

---

> 🔍 **知识点深度解析**
>
> **作用**：ChatClient 是 Spring AI 1.0+ 推荐的高级 API，链式构建对话（系统提示/记忆/工具/流式），比 ChatModel 更易用。
>
> **原理**：ChatClient.builder(model).defaultAdvisors/tools/system 预置配置，prompt().user().call()/stream() 执行；QuestionAnswerAdvisor 内部做 RAG 检索增强。
>
> **用法要点**：① defaultSystem 设定角色；② defaultAdvisors 挂记忆(MessageChatMemoryAdvisor)与 RAG(QuestionAnswerAdvisor)；③ defaultTools 注册工具；④ 用 advisors(a->param("chat_memory_id",id)) 隔离会话；⑤ stream() 返回 Flux 实现逐字流式输出。


---
## 7. 面试高频考点

1. **Spring AI 核心抽象**：ChatModel、Prompt、Advisor、VectorStore、ChatClient
2. **Function Calling 原理**：LLM 返回函数名+参数 → 框架反射调用 → 结果返回 LLM
3. **RAG 完整流程**：切分→向量化→存储→检索→重排→生成
4. **LangChain4j AiServices**：接口即 Agent，@Tool 工具注解
5. **Spring AI vs LangChain4j**：Spring 集成 vs 功能全面，ChatClient vs AiServices
6. **记忆管理**：ChatMemory、MessageWindowChatMemory、按会话隔离
7. **向量数据库选型**：Redis/PGVector/Milvus/ES 对比
8. **国内模型接入**：通义/文心/豆包/DeepSeek 配置
9. **多 Agent 协作**：顺序/并行/辩论模式
10. **企业级实践**：异常降级、成本控制、安全防护
11. **流式输出**：Flux/SSE、chatModel.stream()、逐字返回
12. **可观测性**：Micrometer 指标、Token 消耗、延迟监控、LoggingAdvisor
13. **测试策略**：MockChatModel 单元测试、Ollama 集成测试
14. **ChatClient 高级 API**：defaultSystem/defaultAdvisors/defaultTools、流式调用
15. **文档切分策略**：递归切分、语义切分、重叠窗口
16. **混合检索**：向量检索 + BM25 关键词检索互补
17. **Prompt 模板**：参数化提示词、系统提示设计
18. **AI Agent 架构**：感知→规划→工具调用→记忆→循环

---


---
## 📝 精简总结

- Java AI Agent 两大框架：Spring AI（Spring 官方，自动配置，ChatClient 高级API）、LangChain4j（功能全面，AiServices 核心抽象）
- Spring AI 核心：ChatModel 统一接口、Function Calling（@Bean Function + @Description）、ChatClient 高级 API、Advisor 拦截器
- ChatClient（1.0+推荐）：defaultSystem 系统提示、defaultAdvisors（记忆+RAG）、defaultTools 工具、prompt().user().call()/stream()
- LangChain4j 核心：AiServices（接口即 Agent）、@Tool 工具注解、ChatMemory 记忆、ContentRetriever 检索
- RAG 流程：文档切分（recursive 500字+50重叠）→ Embedding 向量化 → VectorStore 存储 → 相似度检索 Top-K → 上下文拼接 → LLM 生成
- 工具调用：LLM 判断需要工具 → 返回函数名和JSON参数 → 框架反射调用 → 结果返回LLM继续生成
- 记忆管理：MessageWindowChatMemory（保留最近N条）、按 conversationId 隔离、ChatMemoryAdvisor 自动注入
- 向量数据库：Redis（已有基础设施）、PGVector（事务+向量）、Milvus（大规模）、ES（混合检索）
- 国内模型：通义千问/文心一言/豆包/DeepSeek，大多支持 OpenAI 兼容接口
- 多 Agent：AiServices 定义多个专家 Agent，顺序/并行/辩论协作
- 流式输出：chatModel.stream() 返回 Flux、SSE TEXT_EVENT_STREAM_VALUE、前端逐字渲染
- 可观测性：Micrometer 统计成功率/延迟/Token、LoggingAdvisor 记录请求响应、Prometheus+Grafana 监控
- 测试：MockChatModel 单元测试（@MockBean）、Ollama 本地集成测试、测试隔离不依赖外部API
- 企业级：异常降级（429退避/模型切换）、成本控制（模型分级/缓存/Token统计）、安全（输入过滤/输出审核/工具权限）
- 最佳实践：用 ChatClient 而非 ChatModel、Function 的 @Description 要清晰、生产用向量数据库而非内存、流式输出提升体验、可观测性必做

---

[[02-后端开发/MOC-后端开发|← 返回后端开发 MOC]] | [[Home|🏠 返回首页]]
