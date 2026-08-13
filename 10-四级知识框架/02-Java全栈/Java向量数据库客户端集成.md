---
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
