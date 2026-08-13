---
title: SpringAI RAG 检索增强实现
category: Java全栈
subcategory: AI应用开发
tags: [#Java全栈/AI应用, #AI结合/RAG, #难度/高级, #类型/实战]
difficulty: 高级
pre: [[Java向量数据库客户端集成]], [[Java-LLM接口统一封装]]
related: [[RAG文本分块策略与实践]], [[高级RAG-Hybrid检索与重排序]]
update: 2026-08-13
status: 完善
---

# SpringAI RAG 检索增强实现

## 1. 核心概述

RAG（检索增强生成）通过在 LLM 回答前检索相关文档作为上下文，解决模型知识截止和幻觉问题。Spring AI 提供了完整的 RAG 工具链：文档加载器、文本分割器、Embedding 模型、向量存储、检索增强 Advisor，几行代码即可搭建生产级 RAG 系统。

**解决的场景问题**：
- LLM 不知道企业内部知识
- 模型回答存在幻觉，需要基于真实文档
- 需要让 AI 基于特定文档回答问题
- 文档经常更新，微调模型不现实
- 需要可追溯的回答来源

## 2. 底层原理/核心逻辑

### RAG 两阶段流程

```
索引阶段（离线）：
文档 → 加载器 → 文本分割 → Embedding → 向量库

检索阶段（在线）：
用户问题 → Embedding → 向量检索 Top-K → 拼接上下文
→ LLM 生成回答 → 返回（带引用来源）
```

### Spring AI RAG 核心抽象

| 组件 | 接口 | 作用 |
|------|------|------|
| 文档加载器 | DocumentReader | 读取 PDF/Word/HTML 等 |
| 文本分割器 | DocumentTransformer | 将长文档切分为块 |
| Embedding 模型 | EmbeddingModel | 文本转向量 |
| 向量存储 | VectorStore | 存储和检索向量 |
| 检索增强 | QuestionAnswerAdvisor | 自动检索并注入上下文 |

### Advisors 机制

Spring AI 的 Advisor 是一种拦截器模式，可以在 LLM 调用前后插入逻辑。QuestionAnswerAdvisor 自动完成：
1. 提取用户问题
2. 检索相关文档
3. 将文档注入到 Prompt 中
4. LLM 基于上下文回答

## 3. 实操示例

### 基础 RAG 配置

```java
@Configuration
public class RagConfig {

    @Bean
    public VectorStore vectorStore(EmbeddingModel embeddingModel) {
        return new SimpleVectorStore(embeddingModel);
    }

    @Bean
    public QuestionAnswerAdvisor questionAnswerAdvisor(VectorStore vectorStore) {
        return QuestionAnswerAdvisor.builder(vectorStore)
                .topK(5)
                .build();
    }

    @Bean
    public ChatClient ragChatClient(ChatClient.Builder builder,
                                    QuestionAnswerAdvisor advisor) {
        return builder
                .defaultSystem("你是一个知识库助手，请基于提供的参考资料回答问题。如果资料中没有答案，请说"我不知道"。")
                .defaultAdvisors(advisor)
                .build();
    }
}
```

### 文档加载与索引

```java
@Service
public class DocumentIndexingService {

    private final VectorStore vectorStore;
    private final TokenTextSplitter splitter;

    public DocumentIndexingService(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
        this.splitter = TokenTextSplitter.builder()
                .chunkSize(800)
                .chunkOverlap(200)
                .build();
    }

    public void indexPdfFile(String filePath) {
        // 1. 加载 PDF
        PagePdfDocumentReader reader = new PagePdfDocumentReader(
                new FileSystemResource(filePath),
                PdfDocumentReaderConfig.builder()
                        .withPageExtractedTextFormatter(
                                new ExtractedTextFormatter(false, 0, 0, false, "\n\n"))
                        .build());

        List<Document> documents = reader.get();

        // 2. 添加元数据
        documents.forEach(doc -> {
            doc.getMetadata().put("source", filePath);
            doc.getMetadata().put("type", "pdf");
        });

        // 3. 文本分割
        List<Document> chunks = splitter.apply(documents);

        // 4. 存入向量库
        vectorStore.add(chunks);

        System.out.println("索引完成：" + chunks.size() + " 个文档块");
    }

    public void indexText(String content, Map<String, Object> metadata) {
        Document doc = new Document(content, metadata);
        List<Document> chunks = splitter.apply(List.of(doc));
        vectorStore.add(chunks);
    }
}
```

### 带检索的对话

```java
@Service
public class RagChatService {

    private final ChatClient ragChatClient;

    public RagChatService(ChatClient ragChatClient) {
        this.ragChatClient = ragChatClient;
    }

    public String chat(String question) {
        return ragChatClient.prompt()
                .user(question)
                .call()
                .content();
    }

    // 获取带引用的回答
    public RagAnswer chatWithCitations(String question) {
        ChatResponse response = ragChatClient.prompt()
                .user(question)
                .call()
                .chatResponse();

        String answer = response.getResult().getOutput().getText();

        // 从 Advisor 上下文中提取检索到的文档
        List<Document> retrievedDocs = (List<Document>) response.getMetadata()
                .get(QuestionAnswerAdvisor.RETRIEVED_DOCUMENTS);

        List<Citation> citations = retrievedDocs.stream()
                .map(doc -> new Citation(
                        doc.getMetadata().getOrDefault("source", "unknown").toString(),
                        doc.getContent().substring(0, Math.min(100, doc.getContent().length()))
                ))
                .toList();

        return new RagAnswer(answer, citations);
    }

    public record RagAnswer(String answer, List<Citation> citations) {}
    public record Citation(String source, String snippet) {}
}
```

### 自定义检索过滤器

```java
@Service
public class FilteredRagService {

    private final VectorStore vectorStore;
    private final ChatModel chatModel;

    public String chatWithCategoryFilter(String question, String category) {
        // 构建带过滤的检索请求
        SearchRequest searchRequest = SearchRequest.builder()
                .query(question)
                .topK(5)
                .filterExpression("category == '" + category + "'")
                .build();

        List<Document> docs = vectorStore.similaritySearch(searchRequest);

        // 手动拼接上下文
        String context = docs.stream()
                .map(Document::getContent)
                .collect(Collectors.joining("\n\n---\n\n"));

        String prompt = """
                请基于以下参考资料回答问题。
                如果资料中没有答案，请说"根据现有资料无法回答"。

                参考资料：
                %s

                问题：%s

                回答：
                """.formatted(context, question);

        return chatModel.call(prompt);
    }
}
```

### 混合检索 + 重排序

```java
@Service
public class AdvancedRagService {

    private final VectorStore vectorStore;
    private final ChatModel chatModel;
    private final RerankModel rerankModel;

    public String advancedChat(String question) {
        // 1. 向量检索（多取一些候选）
        List<Document> vectorDocs = vectorStore.similaritySearch(
                SearchRequest.builder().query(question).topK(20).build());

        // 2. 关键词检索（可选，需要 ES）
        // List<Document> keywordDocs = keywordSearch(question);

        // 3. 重排序
        List<RerankResult> reranked = rerankModel.rerank(
                RerankRequest.builder()
                        .query(question)
                        .documents(vectorDocs.stream().map(Document::getContent).toList())
                        .topN(5)
                        .build());

        // 4. 取 Top-N 作为上下文
        String context = reranked.stream()
                .map(r -> vectorDocs.get(r.getIndex()).getContent())
                .collect(Collectors.joining("\n\n"));

        // 5. 生成回答
        return chatModel.call("基于以下资料回答：\n" + context + "\n\n问题：" + question);
    }
}
```

### 多查询检索（Multi-Query）

```java
@Service
public class MultiQueryRagService {

    private final ChatModel chatModel;
    private final VectorStore vectorStore;

    public String multiQueryChat(String question) {
        // 1. 让 LLM 生成多个查询角度
        String multiQueryPrompt = """
                你是一个 AI 助手，需要为以下问题生成 3 个不同角度的搜索查询，
                用于从知识库中检索相关文档。每个查询一行，不要编号。

                原始问题：%s

                查询：
                """.formatted(question);

        String queriesText = chatModel.call(multiQueryPrompt);
        List<String> queries = Arrays.stream(queriesText.split("\n"))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .toList();

        // 2. 对每个查询做检索
        Set<Document> allDocs = new HashSet<>();
        for (String query : queries) {
            allDocs.addAll(vectorStore.similaritySearch(
                    SearchRequest.builder().query(query).topK(3).build()));
        }

        // 3. 去重并生成回答
        String context = allDocs.stream()
                .map(Document::getContent)
                .collect(Collectors.joining("\n\n---\n\n"));

        return chatModel.call("参考资料：\n" + context + "\n\n问题：" + question);
    }
}
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 检索不到相关文档 | 分块太大或太小 | 调整 chunkSize，用递归分割器 |
| 回答不基于检索内容 | Prompt 没强调约束 | 系统提示明确要求基于资料 |
| 上下文太长超 Token | Top-K 太大 | 减少 topK，或压缩上下文 |
| 引用来源不准确 | 元数据没保留 | 分块时保留 source、page 等元数据 |
| 更新文档后检索到旧内容 | 向量库没更新 | 建立增量索引机制 |

### 踩坑点

1. **Embedding 模型要和检索时一致**：入库和查询必须用同一个模型
2. **PDF 加载要处理页眉页脚**：否则检索结果包含大量噪声
3. **代码文档要特殊分块**：按函数切，不要按字符切
4. **QuestionAnswerAdvisor 会修改 user message**：自定义处理时要注意

### 优化方案

- **父子分块**：小块检索，大块返回
- **查询改写**：用户问题模糊时先改写再检索
- **缓存检索结果**：相同问题的检索结果缓存
- **增量索引**：文档更新时只重新索引变化部分

## 5. 延伸拓展方向

- [[RAG文本分块策略与实践]]：分块是 RAG 质量的基础
- [[Java向量数据库客户端集成]]：向量存储的底层实现
- [[高级RAG-Hybrid检索与重排序]]：混合检索进阶
- [[GraphRAG知识图谱增强检索]]：图谱增强 RAG
- [[AI应用测试与LLM输出评估]]：RAG 效果评估

## 6. 参考资料

- [Spring AI: Retrieval Augmented Generation](https://docs.spring.io/spring-ai/reference/api/advices/question-answer-advisor.html)
- [Spring AI: Vector Stores](https://docs.spring.io/spring-ai/reference/api/vectordbs.html)
- [RAG Survey](https://arxiv.org/abs/2312.10997)

#待完善
