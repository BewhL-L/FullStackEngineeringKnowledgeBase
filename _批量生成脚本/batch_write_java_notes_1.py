# -*- coding: utf-8 -*-
"""批量写入 Java 板块前 4 篇高质量原子笔记"""
import os

BASE = r"C:\Users\23981\Desktop\AI文档\DouBao Document\全栈工程MarkDown文档\10-四级知识框架\02-Java全栈"

notes = {}

# ============ 笔记2：SpringAI Function Calling 工具调用 ============
notes["SpringAI-FunctionCalling工具调用.md"] = r'''---
title: SpringAI Function Calling 工具调用
category: Java全栈
subcategory: AI应用开发
tags: [#Java全栈/AI应用, #AI结合/工具调用, #难度/高级, #类型/实战]
difficulty: 高级
pre: [[Java-SpringBoot自动配置原理]], [[Java-LLM接口统一封装]]
related: [[AI网关与多模型路由设计]], [[多Agent协作模式实现]]
update: 2026-08-13
status: 完善
---

# SpringAI Function Calling 工具调用

## 1. 核心概述

Function Calling（工具调用）让 LLM 不再只是"聊天"，而是可以调用外部工具完成实际操作——查天气、查数据库、发邮件、执行代码。Spring AI 通过 `@Tool` 注解和 `FunctionCallback` 抽象，将 Java 方法自动注册为 LLM 可调用的工具，处理参数解析、调用执行、结果回传的完整流程。

**解决的场景问题**：
- LLM 知识截止，无法获取实时信息（天气、股价）
- 需要操作业务系统（查订单、发通知）
- 需要执行计算或代码
- 多步骤任务需要工具协作
- 结构化数据查询

## 2. 底层原理/核心逻辑

### Function Calling 工作流程

```
用户提问 → LLM 判断需要调用工具
    ↓
LLM 返回 tool_call（工具名 + JSON 参数）
    ↓
应用解析参数，执行对应 Java 方法
    ↓
将工具执行结果返回给 LLM
    ↓
LLM 基于工具结果生成最终回答
```

### Spring AI 工具调用抽象

```
@Tool 注解的方法
    ↓ 自动扫描
FunctionCallback 接口实现
    ↓ 注册到 ChatClient
ChatClient.prompt().functions("toolName")
    ↓
LLM 调用时自动匹配并执行
```

### 工具调用的两种模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| 自动模式 | LLM 决定是否调用，框架自动执行 | 通用对话 Agent |
| 手动模式 | 应用代码控制调用流程 | 精细控制、安全校验 |

## 3. 实操示例

### @Tool 注解定义工具

```java
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

@Component
public class WeatherTools {

    @Tool(description = "查询指定城市的当前天气")
    public String getWeather(
            @ToolParam(description = "城市名称，如北京、上海") String city) {
        // 调用天气 API
        return String.format("%s今天晴，气温25-32°C，湿度60%%", city);
    }

    @Tool(description = "查询未来几天的天气预报")
    public String getForecast(
            @ToolParam(description = "城市名称") String city,
            @ToolParam(description = "天数，1-7") int days) {
        return String.format("%s未来%d天天气预报：第1天晴，第2天多云...", city, days);
    }
}
```

### ChatClient 自动工具调用

```java
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.stereotype.Service;

@Service
public class WeatherAgentService {

    private final ChatClient chatClient;
    private final WeatherTools weatherTools;

    public WeatherAgentService(ChatClient.Builder builder, WeatherTools weatherTools) {
        this.chatClient = builder
                .defaultSystem("你是一个天气助手，可以查询天气信息。")
                .defaultTools(weatherTools)  // 注册工具
                .build();
        this.weatherTools = weatherTools;
    }

    public String chat(String userInput) {
        return chatClient.prompt()
                .user(userInput)
                .call()
                .content();
    }
}

// 使用
// 输入："北京今天天气怎么样？"
// LLM 自动调用 getWeather("北京")，然后生成回答
```

### FunctionCallback 手动定义

```java
import org.springframework.ai.tool.function.FunctionToolCallback;
import java.util.function.Function;

// 1. 定义参数类
public record OrderQueryRequest(
        @JsonPropertyDescription("订单号") String orderId,
        @JsonPropertyDescription("用户ID") String userId
) {}

// 2. 定义返回类
public record OrderInfo(
        String orderId,
        String status,
        BigDecimal amount,
        String createTime
) {}

// 3. 创建 FunctionCallback
FunctionToolCallback<OrderQueryRequest, OrderInfo> orderQueryCallback =
    FunctionToolCallback.builder("queryOrder", "查询订单信息",
        (Function<OrderQueryRequest, OrderInfo>) request -> {
            // 实际业务逻辑
            return orderService.queryOrder(request.orderId(), request.userId());
        })
        .inputType(OrderQueryRequest.class)
        .build();

// 4. 注册到 ChatClient
ChatClient client = ChatClient.builder(chatModel)
        .defaultTools(orderQueryCallback)
        .build();
```

### 手动控制工具调用流程

```java
@Service
public class ManualToolCallingService {

    private final ChatModel chatModel;
    private final ToolCallback[] tools;

    public String chatWithManualControl(String userInput) {
        // 第一轮：发送用户消息，获取 LLM 响应
        ChatResponse response = chatModel.call(
            Prompt.builder()
                .instructions(List.of(
                    new SystemMessage("你是一个助手，可以使用工具。"),
                    new UserMessage(userInput)
                ))
                .toolCallbacks(List.of(tools))
                .build()
        );

        AssistantMessage assistant = response.getResult().getOutput();

        // 检查是否有工具调用
        if (assistant.getToolCalls() != null && !assistant.getToolCalls().isEmpty()) {
            List<ToolResponseMessage> toolResponses = new ArrayList<>();

            for (ToolCall toolCall : assistant.getToolCalls()) {
                // 安全校验：检查工具是否允许调用
                if (!isToolAllowed(toolCall.name())) {
                    toolResponses.add(new ToolResponseMessage(
                        toolCall.id(), toolCall.name(),
                        "工具调用被拒绝：权限不足"
                    ));
                    continue;
                }

                // 执行工具
                String result = executeTool(toolCall.name(), toolCall.arguments());
                toolResponses.add(new ToolResponseMessage(
                    toolCall.id(), toolCall.name(), result
                ));
            }

            // 第二轮：将工具结果返回给 LLM
            ChatResponse finalResponse = chatModel.call(
                Prompt.builder()
                    .instructions(List.of(
                        new SystemMessage("你是一个助手。"),
                        new UserMessage(userInput),
                        assistant,
                        (Message) toolResponses.get(0)
                    ))
                    .build()
            );

            return finalResponse.getResult().getOutput().getText();
        }

        return assistant.getText();
    }

    private boolean isToolAllowed(String toolName) {
        // 权限校验逻辑
        return true;
    }

    private String executeTool(String name, String arguments) {
        // 工具执行逻辑
        return "result";
    }
}
```

### 结构化输出（Structured Output）

```java
// 定义输出结构
public record CustomerInfo(
        String name,
        String email,
        String phone,
        List<String> preferences
) {}

// 使用 entity() 方法直接获取结构化对象
CustomerInfo info = chatClient.prompt()
        .user("从以下文本中提取客户信息：张三，邮箱 zhangsan@example.com，电话 13800138000，喜欢科技产品")
        .call()
        .entity(CustomerInfo.class);

System.out.println("姓名：" + info.name());
System.out.println("邮箱：" + info.email());
```

### 多工具组合 Agent

```java
@Service
public class TravelAgentService {

    private final ChatClient chatClient;

    public TravelAgentService(ChatClient.Builder builder,
                              WeatherTools weatherTools,
                              FlightTools flightTools,
                              HotelTools hotelTools) {
        this.chatClient = builder
                .defaultSystem("""
                    你是一个旅行规划助手。
                    可以查询天气、航班和酒店信息，帮用户规划行程。
                    步骤：1.查目的地天气 2.查航班 3.查酒店 4.综合推荐
                    """)
                .defaultTools(weatherTools, flightTools, hotelTools)
                .build();
    }

    public String planTrip(String destination, String date) {
        return chatClient.prompt()
                .user(String.format("我想%s去%s旅行，帮我规划一下", date, destination))
                .call()
                .content();
    }
}
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| LLM 不调用工具 | 工具描述不清晰 | 优化 description，说明何时使用 |
| 参数解析错误 | 参数类型不匹配 | 用 record 定义参数，加 @ToolParam 描述 |
| 工具循环调用 | LLM 反复调用同一工具 | 加最大调用次数限制 |
| 工具执行超时 | 外部 API 慢 | 加超时控制，异步执行 |
| 多工具调用顺序错 | LLM 不知道依赖关系 | 在系统提示中说明执行顺序 |

### 踩坑点

1. **工具描述是关键**：description 写得好，LLM 才知道什么时候调用
2. **参数要加描述**：@ToolParam 的 description 帮助 LLM 正确传参
3. **返回值要简洁**：工具返回太长会占用 Token，只返回必要信息
4. **不要注册太多工具**：工具太多会让 LLM 困惑，按需注册

### 优化方案

- **工具分组**：不同场景注册不同工具集
- **工具调用日志**：记录每次工具调用的参数和结果
- **工具结果缓存**：相同参数的工具调用结果缓存
- **错误处理**：工具执行失败时返回友好错误信息

## 5. 延伸拓展方向

- [[多Agent协作模式实现]]：工具调用是 Agent 的基础
- [[AI网关与多模型路由设计]]：网关层的工具管理
- [[AI工作流编排引擎设计]]：工具作为工作流节点
- [[AI应用可观测性与Langfuse集成]]：工具调用追踪
- [[AI应用安全与Prompt注入防护]]：工具调用安全

## 6. 参考资料

- [Spring AI: Function Calling](https://docs.spring.io/spring-ai/reference/api/tools.html)
- [OpenAI: Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Spring AI ChatClient](https://docs.spring.io/spring-ai/reference/api/chatclient.html)

#待完善
'''

# ============ 笔记5：Java 向量数据库客户端集成 ============
notes["Java向量数据库客户端集成.md"] = r'''---
title: Java 向量数据库客户端集成
category: Java全栈
subcategory: AI应用开发
tags: [#Java全栈/AI应用, #AI结合/向量数据库, #难度/进阶, #类型/实战]
difficulty: 进阶
pre: [[Java-SpringBoot数据访问]], [[Java-LLM接口统一封装]]
related: [[SpringAI-RAG检索增强实现]], [[RAG文本分块策略与实践]]
update: 2026-08-13
status: 完善
---

# Java 向量数据库客户端集成

## 1. 核心概述

向量数据库是 RAG 系统的核心存储，用于存储文档的 Embedding 向量并做相似度检索。Java 生态中，Milvus、PgVector、Chroma、Qdrant 各有优势。Spring AI 提供了统一的 `VectorStore` 抽象，屏蔽底层差异，让开发者可以无缝切换向量数据库。

**解决的场景问题**：
- 需要存储和检索大量文档的向量表示
- 传统数据库不支持相似度搜索
- 不同向量数据库 API 不统一，切换成本高
- 需要过滤、分页、混合检索等高级功能
- 高并发场景下的检索性能

## 2. 底层原理/核心逻辑

### 向量检索原理

```
文档 → 文本分块 → Embedding 模型 → 向量 (768/1024/1536维)
    ↓
存入向量数据库（带索引）
    ↓
用户查询 → Embedding → 向量
    ↓
相似度计算（余弦/欧氏/内积）→ Top-K 结果
```

### 相似度度量

| 度量方式 | 公式 | 适用场景 |
|----------|------|----------|
| 余弦相似度 | cos(A,B) = A·B / (|A||B|) | 文本语义相似度（最常用） |
| 欧氏距离 | d = √Σ(aᵢ-bᵢ)² | 图像、数值向量 |
| 内积 | A·B = Σaᵢbᵢ | 归一化向量（等价余弦） |

### 索引类型

| 索引 | 原理 | 速度 | 精度 | 内存 |
|------|------|------|------|------|
| Flat | 暴力搜索 | 慢 | 100% | 低 |
| IVF | 倒排文件，先聚类再搜索 | 快 | 高 | 中 |
| HNSW | 层次化导航小世界图 | 极快 | 高 | 高 |

### 向量数据库对比

| 数据库 | 类型 | Java SDK | 性能 | 生态 | 适用场景 |
|--------|------|----------|------|------|----------|
| Milvus | 独立服务 | ✅ 完善 | 极高 | 好 | 大规模生产 |
| PgVector | PostgreSQL 扩展 | ✅ JDBC | 中 | 极好 | 已有 PG 栈 |
| Chroma | 嵌入式/服务 | ✅ 基本 | 中 | 中 | 原型/中小规模 |
| Qdrant | 独立服务 | ✅ 完善 | 高 | 好 | 生产级 |
| Elasticsearch | 搜索引擎 | ✅ 完善 | 中 | 极好 | 已有 ES 栈 |

## 3. 实操示例

### Spring AI VectorStore 统一抽象

```java
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.document.Document;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class RagService {

    private final VectorStore vectorStore;

    public RagService(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
    }

    // 添加文档
    public void addDocuments(List<Document> documents) {
        vectorStore.add(documents);
    }

    // 相似度检索
    public List<Document> search(String query, int topK) {
        return vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(query)
                .topK(topK)
                .build()
        );
    }

    // 带过滤条件的检索
    public List<Document> searchWithFilter(String query, String category) {
        return vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(query)
                .topK(5)
                .filterExpression("category == '" + category + "'")
                .build()
        );
    }

    // 删除文档
    public void deleteDocuments(List<String> ids) {
        vectorStore.delete(ids);
    }
}
```

### Milvus Java SDK 集成

```java
import io.milvus.client.MilvusServiceClient;
import io.milvus.param.ConnectParam;
import io.milvus.param.collection.CreateCollectionParam;
import io.milvus.param.collection.FieldType;
import io.milvus.param.dml.InsertParam;
import io.milvus.param.dml.SearchParam;
import io.milvus.response.SearchResultsWrapper;
import java.util.Arrays;
import java.util.List;

@Configuration
public class MilvusConfig {

    @Bean
    public MilvusServiceClient milvusClient() {
        ConnectParam connectParam = ConnectParam.newBuilder()
                .withHost("localhost")
                .withPort(19530)
                .build();
        return new MilvusServiceClient(connectParam);
    }
}

@Service
public class MilvusVectorService {

    private final MilvusServiceClient client;
    private static final String COLLECTION = "documents";
    private static final int VECTOR_DIM = 1536;

    // 创建集合
    public void createCollection() {
        FieldType idField = FieldType.newBuilder()
                .withName("id")
                .withDataType(io.milvus.grpc.DataType.VarChar)
                .withPrimaryKey(true)
                .withMaxLength(64)
                .build();

        FieldType vectorField = FieldType.newBuilder()
                .withName("vector")
                .withDataType(io.milvus.grpc.DataType.FloatVector)
                .withDimension(VECTOR_DIM)
                .build();

        FieldType contentField = FieldType.newBuilder()
                .withName("content")
                .withDataType(io.milvus.grpc.DataType.VarChar)
                .withMaxLength(65535)
                .build();

        CreateCollectionParam param = CreateCollectionParam.newBuilder()
                .withCollectionName(COLLECTION)
                .withDescription("文档向量库")
                .addFieldType(idField)
                .addFieldType(vectorField)
                .addFieldType(contentField)
                .build();

        client.createCollection(param);
    }

    // 插入向量
    public void insert(String id, List<Float> vector, String content) {
        InsertParam param = InsertParam.newBuilder()
                .withCollectionName(COLLECTION)
                .withFields(Arrays.asList(
                    InsertParam.Field.builder().withName("id").withValues(List.of(id)).build(),
                    InsertParam.Field.builder().withName("vector").withValues(List.of(vector)).build(),
                    InsertParam.Field.builder().withName("content").withValues(List.of(content)).build()
                ))
                .build();
        client.insert(param);
    }

    // 相似度搜索
    public List<SearchResultsWrapper.IDScore> search(List<Float> queryVector, int topK) {
        SearchParam param = SearchParam.newBuilder()
                .withCollectionName(COLLECTION)
                .withVectorFieldName("vector")
                .withVectors(List.of(queryVector))
                .withTopK(topK)
                .withMetricType(io.milvus.common.clientenum.ConsistencyLevelEnum.STRONG)
                .withOutFields(List.of("content"))
                .build();

        SearchResultsWrapper wrapper = new SearchResultsWrapper(
            client.search(param).getData().getResults());
        return wrapper.getIDScore(0);
    }
}
```

### PgVector 集成

```sql
-- 启用 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建表
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(1536) NOT NULL
);

-- 创建 HNSW 索引（余弦相似度）
CREATE INDEX documents_embedding_idx ON documents
USING hnsw (embedding vector_cosine_ops);

-- 相似度查询
SELECT id, content, 1 - (embedding <=> :query_vector) AS similarity
FROM documents
ORDER BY embedding <=> :query_vector
LIMIT 5;
```

```java
@Repository
public class PgVectorRepository {

    private final JdbcTemplate jdbcTemplate;

    public List<Document> searchSimilar(float[] queryVector, int topK) {
        String sql = """
            SELECT id, content, metadata,
                   1 - (embedding <=> ?::vector) AS similarity
            FROM documents
            ORDER BY embedding <=> ?::vector
            LIMIT ?
            """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> new Document(
            rs.getString("id"),
            rs.getString("content"),
            rs.getObject("metadata", Map.class),
            rs.getFloat("similarity")
        ), vectorToString(queryVector), vectorToString(queryVector), topK);
    }

    private String vectorToString(float[] vector) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < vector.length; i++) {
            if (i > 0) sb.append(",");
            sb.append(vector[i]);
        }
        sb.append("]");
        return sb.toString();
    }
}
```

### Spring AI Milvus VectorStore 配置

```java
@Configuration
public class VectorStoreConfig {

    @Bean
    public VectorStore vectorStore(EmbeddingModel embeddingModel) {
        MilvusVectorStoreConfig config = MilvusVectorStoreConfig.builder()
                .withUri("http://localhost:19530")
                .withCollectionName("spring_ai_docs")
                .withEmbeddingDimension(1536)
                .withMetricType(MilvusVectorStore.MetricType.COSINE)
                .withIndexType(MilvusVectorStore.IndexType.IVF_FLAT)
                .build();

        return new MilvusVectorStore(config, embeddingModel);
    }
}
```

### 混合检索（向量 + 关键词）

```java
@Service
public class HybridSearchService {

    private final VectorStore vectorStore;
    private final ElasticsearchRestTemplate esTemplate;

    public List<Document> hybridSearch(String query, int topK) {
        // 1. 向量检索
        List<Document> vectorResults = vectorStore.similaritySearch(
            SearchRequest.builder().query(query).topK(topK * 2).build()
        );

        // 2. 关键词检索
        Query esQuery = new NativeSearchQueryBuilder()
                .withQuery(QueryBuilders.matchQuery("content", query))
                .withPageable(PageRequest.of(0, topK * 2))
                .build();
        List<Document> keywordResults = esTemplate.search(esQuery, Document.class)
                .stream().map(SearchHit::getContent).toList();

        // 3. RRF 融合排序
        return rrfFusion(vectorResults, keywordResults, topK);
    }

    private List<Document> rrfFusion(List<Document> a, List<Document> b, int topK) {
        Map<String, Double> scores = new HashMap<>();
        Map<String, Document> docs = new HashMap<>();
        int k = 60;

        for (int i = 0; i < a.size(); i++) {
            String id = a.get(i).getId();
            scores.merge(id, 1.0 / (k + i), Double::sum);
            docs.put(id, a.get(i));
        }
        for (int i = 0; i < b.size(); i++) {
            String id = b.get(i).getId();
            scores.merge(id, 1.0 / (k + i), Double::sum);
            docs.put(id, b.get(i));
        }

        return scores.entrySet().stream()
                .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
                .limit(topK)
                .map(e -> docs.get(e.getKey()))
                .toList();
    }
}
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 检索结果不相关 | Embedding 模型不匹配 | 用和查询相同的 Embedding 模型 |
| 检索速度慢 | 数据量大，索引没建好 | 建 HNSW/IVF 索引，调整参数 |
| 内存占用高 | HNSW 索引内存大 | 用 IVF 索引，或降低维度 |
| 过滤条件不生效 | 元数据字段没建索引 | 为过滤字段建标量索引 |
| 向量维度不匹配 | 文档和查询用了不同模型 | 统一 Embedding 模型 |

### 踩坑点

1. **Embedding 模型必须统一**：入库和查询必须用同一个模型，否则维度和语义空间都不同
2. **向量归一化**：用内积时必须归一化，余弦不需要
3. **Milvus 需要先建索引再加载**：创建集合后要 create index + load collection
4. **PgVector 维度要匹配**：建表时 vector(N) 的 N 必须和 Embedding 维度一致

### 优化方案

- **批量插入**：一次插入多条，减少网络开销
- **异步索引构建**：大数据量时后台构建索引
- **分区策略**：按时间/类别分区，提升检索效率
- **缓存热门查询**：高频查询结果缓存

## 5. 延伸拓展方向

- [[SpringAI-RAG检索增强实现]]：向量库的上层应用
- [[RAG文本分块策略与实践]]：入库前的文本处理
- [[高级RAG-Hybrid检索与重排序]]：混合检索进阶
- [[GraphRAG知识图谱增强检索]]：图谱 + 向量
- [[AI成本控制与Token计费优化]]：Embedding 成本控制

## 6. 参考资料

- [Spring AI: Vector Stores](https://docs.spring.io/spring-ai/reference/api/vectordbs.html)
- [Milvus Java SDK](https://milvus.io/api-reference/java/v2.4.x/About.md)
- [pgvector](https://github.com/pgvector/pgvector)
- [Qdrant Java Client](https://github.com/qdrant/java-client)

#待完善
'''

# ============ 笔记8：AI 网关与多模型路由设计 ============
notes["AI网关与多模型路由设计.md"] = r'''---
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
'''

# ============ 笔记11：AI 应用可观测性与 Langfuse 集成 ============
notes["AI应用可观测性与Langfuse集成.md"] = r'''---
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
'''

# 写入文件
for filename, content in notes.items():
    filepath = os.path.join(BASE, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
    print(f"已写入: {filename} ({len(content)} 字节)")

print(f"\n共写入 {len(notes)} 篇笔记")
