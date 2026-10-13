# -*- coding: utf-8 -*-
"""批量写入 Java 板块后 4 篇高质量原子笔记"""
import os

BASE = r"C:\Users\23981\Desktop\AI文档\DouBao Document\全栈工程MarkDown文档\10-四级知识框架\02-Java全栈"

notes = {}

# ============ 笔记14：SpringAI RAG 检索增强实现 ============
notes["SpringAI-RAG检索增强实现.md"] = r'''---
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
'''

# ============ 笔记17：AI 应用测试与 LLM 输出评估 ============
notes["AI应用测试与LLM输出评估.md"] = r'''---
title: AI 应用测试与 LLM 输出评估
category: Java全栈
subcategory: AI应用开发
tags: [#Java全栈/AI应用, #AI结合/测试, #难度/进阶, #类型/实战]
difficulty: 进阶
pre: [[Java-SpringBoot测试最佳实践]], [[Prompt工程与版本管理]]
related: [[AI应用可观测性与Langfuse集成]], [[AI网关与多模型路由设计]]
update: 2026-08-13
status: 完善
---

# AI 应用测试与 LLM 输出评估

## 1. 核心概述

传统软件测试是"输入→断言输出"，但 LLM 输出是非确定性的，同样的输入可能产生不同的输出。AI 应用测试需要分层：单元测试（工具函数、Prompt 渲染）、集成测试（RAG 检索、工具调用）、端到端评估（LLM 输出质量）。LLM-as-Judge 是评估输出质量的核心方法，用强模型给弱模型的输出打分。

**解决的场景问题**：
- 改了 Prompt 后不知道效果变好还是变差
- LLM 输出不稳定，无法用传统断言
- RAG 检索质量无法量化
- 上线前没有自动化的质量门禁
- 用户投诉回答质量差，但无法复现和定位

## 2. 底层原理/核心逻辑

### AI 测试分层

```
第1层：单元测试（确定性）
  - Prompt 模板渲染
  - 工具函数逻辑
  - 文本分块、Token 计算
  - 用 JUnit + Mockito

第2层：集成测试（半确定性）
  - 向量检索召回率
  - 工具调用流程
  - 用 Mock LLM + 真实向量库

第3层：端到端评估（非确定性）
  - LLM 输出质量
  - RAG 端到端效果
  - 用 LLM-as-Judge + 评估数据集
```

### LLM-as-Judge 原理

```
评估输入：
  - 问题 (question)
  - 参考答案 (reference，可选)
  - 待评估回答 (answer)
  - 评估标准 (rubric)

Judge LLM (GPT-4o) → 输出分数 + 理由

评估维度：
  - 相关性 (relevance)
  - 准确性 (accuracy)
  - 完整性 (completeness)
  - 格式合规 (format)
  - 安全性 (safety)
```

### RAG 评估指标

| 指标 | 说明 | 计算方式 |
|------|------|----------|
| Hit Rate | 检索到正确文档的比例 | 命中数 / 总查询数 |
| MRR | 正确文档的平均排名倒数 | 1/排名 的平均 |
| Context Precision | 检索结果中相关文档的比例 | 相关数 / 检索总数 |
| Context Recall | 相关文档被检索到的比例 | 检索到的相关数 / 总相关数 |
| Faithfulness | 回答是否基于上下文 | LLM 判断 |
| Answer Relevance | 回答是否切题 | LLM 判断 |

## 3. 实操示例

### 评估数据集

```java
// 评估用例定义
public record EvalCase(
        String id,
        String question,
        String expectedAnswer,
        List<String> expectedDocIds,  // 期望检索到的文档
        String category,
        Map<String, Object> metadata
) {}

// 评估数据集
@Component
public class EvalDataset {

    public List<EvalCase> loadRagEvalCases() {
        return List.of(
            new EvalCase(
                "rag-001",
                "Spring AI 支持哪些向量数据库？",
                "Spring AI 支持 Milvus、PgVector、Chroma、Qdrant、Elasticsearch 等向量数据库。",
                List.of("doc-spring-ai-vectordb", "doc-spring-ai-reference"),
                "rag",
                Map.of("difficulty", "easy")
            ),
            new EvalCase(
                "rag-002",
                "如何在 Spring AI 中实现 Function Calling？",
                "使用 @Tool 注解或 FunctionCallback 接口...",
                List.of("doc-spring-ai-tools"),
                "rag",
                Map.of("difficulty", "medium")
            )
            // ... 更多用例
        );
    }
}
```

### LLM Judge 评估器

```java
@Service
public class LlmJudgeEvaluator {

    private final ChatModel judgeModel;  // 用 GPT-4o 作为 Judge

    public LlmJudgeEvaluator(@Qualifier("judgeChatModel") ChatModel judgeModel) {
        this.judgeModel = judgeModel;
    }

    public EvalResult evaluate(String question, String answer,
                               String reference, List<String> rubrics) {
        String prompt = """
                你是一个严格的 AI 输出质量评估专家。
                请根据以下标准评估回答质量，输出 JSON 格式。

                评估标准：
                %s

                问题：%s
                参考答案：%s
                待评估回答：%s

                请输出 JSON：
                {
                  "scores": {
                    "relevance": 0-10,
                    "accuracy": 0-10,
                    "completeness": 0-10,
                    "format": 0-10
                  },
                  "overall": 0-10,
                  "reason": "评估理由",
                  "issues": ["问题1", "问题2"]
                }
                """.formatted(
                        String.join("\n", rubrics),
                        question,
                        reference,
                        answer
                );

        String response = judgeModel.call(prompt);

        // 解析 JSON
        try {
            ObjectMapper mapper = new ObjectMapper();
            JsonNode root = mapper.readTree(response);
            return new EvalResult(
                    root.path("overall").asDouble(),
                    root.path("scores").path("relevance").asDouble(),
                    root.path("scores").path("accuracy").asDouble(),
                    root.path("scores").path("completeness").asDouble(),
                    root.path("reason").asText(),
                    new ArrayList<>()
            );
        } catch (Exception e) {
            return new EvalResult(0, 0, 0, 0, "解析失败: " + e.getMessage(), List.of());
        }
    }

    public record EvalResult(double overall, double relevance,
                             double accuracy, double completeness,
                             String reason, List<String> issues) {}
}
```

### 格式校验器

```java
@Component
public class FormatValidator {

    public FormatResult validateJson(String output) {
        try {
            new ObjectMapper().readTree(output);
            return new FormatResult(true, "JSON 格式正确", null);
        } catch (JsonProcessingException e) {
            return new FormatResult(false, "JSON 格式错误: " + e.getMessage(), e.getMessage());
        }
    }

    public FormatResult validateMarkdown(String output) {
        // 检查是否包含必要的 Markdown 结构
        boolean hasHeaders = output.contains("#");
        boolean hasCodeBlocks = output.contains("```");
        return new FormatResult(hasHeaders || hasCodeBlocks,
                "Markdown 结构检查", null);
    }

    public FormatResult validateNoHallucination(String answer, String context) {
        // 简单检查：回答中的关键事实是否在上下文中出现
        // 实际应该用 LLM 判断
        return new FormatResult(true, "基础检查通过", null);
    }

    public record FormatResult(boolean valid, String message, String detail) {}
}
```

### RAG 评估器

```java
@Service
public class RagEvaluator {

    private final VectorStore vectorStore;
    private final ChatModel chatModel;
    private final LlmJudgeEvaluator judge;

    public RagEvaluationResult evaluate(List<EvalCase> cases) {
        int totalHits = 0;
        double totalMrr = 0;
        List<EvalResult> answerResults = new ArrayList<>();

        for (EvalCase testCase : cases) {
            // 1. 评估检索质量
            List<Document> retrieved = vectorStore.similaritySearch(
                    SearchRequest.builder()
                            .query(testCase.question())
                            .topK(5)
                            .build());

            List<String> retrievedIds = retrieved.stream()
                    .map(d -> d.getMetadata().getOrDefault("doc_id", "").toString())
                    .toList();

            // Hit Rate
            boolean hit = retrievedIds.stream()
                    .anyMatch(id -> testCase.expectedDocIds().contains(id));
            if (hit) totalHits++;

            // MRR
            for (int i = 0; i < retrievedIds.size(); i++) {
                if (testCase.expectedDocIds().contains(retrievedIds.get(i))) {
                    totalMrr += 1.0 / (i + 1);
                    break;
                }
            }

            // 2. 评估回答质量
            String context = retrieved.stream()
                    .map(Document::getContent)
                    .collect(Collectors.joining("\n\n"));
            String answer = chatModel.call(
                    "基于以下资料回答：\n" + context + "\n\n问题：" + testCase.question());

            EvalResult result = judge.evaluate(
                    testCase.question(), answer,
                    testCase.expectedAnswer(),
                    List.of("回答必须基于提供的参考资料", "回答要准确完整")
            );
            answerResults.add(result);
        }

        return new RagEvaluationResult(
                cases.size(),
                (double) totalHits / cases.size(),
                totalMrr / cases.size(),
                answerResults.stream().mapToDouble(EvalResult::overall).average().orElse(0),
                answerResults
        );
    }

    public record RagEvaluationResult(
            int totalCases,
            double hitRate,
            double mrr,
            double avgAnswerScore,
            List<EvalResult> details
    ) {}
}
```

### 评估运行器与质量门禁

```java
@Service
public class EvaluationRunner {

    private final RagEvaluator ragEvaluator;
    private final EvalDataset dataset;

    public EvaluationReport runRagEvaluation() {
        List<EvalCase> cases = dataset.loadRagEvalCases();
        RagEvaluationResult result = ragEvaluator.evaluate(cases);

        // 质量门禁
        boolean passed = result.hitRate() >= 0.8
                && result.avgAnswerScore() >= 7.0;

        return new EvaluationReport(
                "rag-eval-" + System.currentTimeMillis(),
                LocalDateTime.now(),
                result,
                passed,
                passed ? "通过" : "未通过：Hit Rate 或回答分数低于阈值"
        );
    }

    public record EvaluationReport(
            String id,
            LocalDateTime timestamp,
            RagEvaluationResult result,
            boolean passed,
            String conclusion
    ) {}
}

// JUnit 集成测试
@SpringBootTest
class RagQualityTest {

    @Autowired
    private EvaluationRunner runner;

    @Test
    @Tag("quality-gate")
    void ragQualityShouldPassThreshold() {
        EvaluationReport report = runner.runRagEvaluation();
        assertTrue(report.passed(),
                "RAG 质量门禁未通过: " + report.conclusion()
                + ", Hit Rate: " + report.result().hitRate()
                + ", Avg Score: " + report.result().avgAnswerScore());
    }
}
```

### Prompt 版本对比测试

```java
@Service
public class PromptComparisonTest {

    private final ChatModel chatModel;
    private final LlmJudgeEvaluator judge;
    private final PromptManager promptManager;

    public PromptCompareResult compareVersions(String promptName,
                                               String v1, String v2,
                                               List<EvalCase> cases) {
        double v1Score = 0, v2Score = 0;
        int v1Wins = 0, v2Wins = 0, ties = 0;

        for (EvalCase testCase : cases) {
            String answerV1 = callWithPrompt(promptName, v1, testCase.question());
            String answerV2 = callWithPrompt(promptName, v2, testCase.question());

            // 成对比较（更可靠）
            String comparePrompt = """
                    请比较以下两个回答哪个更好，输出 A 或 B 或 tie。
                    问题：%s
                    回答 A：%s
                    回答 B：%s
                    更好的是：
                    """.formatted(testCase.question(), answerV1, answerV2);

            String result = chatModel.call(comparePrompt).trim().toUpperCase();
            if (result.startsWith("A")) { v1Wins++; v1Score += 1; }
            else if (result.startsWith("B")) { v2Wins++; v2Score += 1; }
            else { ties++; v1Score += 0.5; v2Score += 0.5; }
        }

        return new PromptCompareResult(v1, v2, v1Wins, v2Wins, ties,
                v1Score / cases.size(), v2Score / cases.size());
    }

    private String callWithPrompt(String name, String version, String question) {
        // 使用指定版本的 Prompt
        return "answer";
    }

    public record PromptCompareResult(
            String v1, String v2,
            int v1Wins, int v2Wins, int ties,
            double v1Score, double v2Score
    ) {}
}
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| Judge 评分不稳定 | 同一输入多次评分不同 | 多次评分取平均，降低 temperature |
| 评估成本高 | 每个用例都调 GPT-4 | 用小模型做初筛，只对边界用例用强模型 |
| 评估集太小 | 只有几个用例 | 至少 50+ 用例，覆盖各类场景 |
| Judge 偏向更长的回答 | 长度偏见 | 评估标准中明确不看长度 |
| 评估结果不可复现 | LLM 非确定性 | 固定 seed，记录所有输入输出 |

### 踩坑点

1. **不要用同一个模型做生成和评估**：会有自我偏好偏差
2. **评估标准要具体**："回答好"太模糊，要拆成可操作的维度
3. **评估集要持续维护**：新场景要不断补充
4. **不要只看平均分**：要看最差的用例（短板效应）

### 优化方案

- **自动化评估流水线**：CI/CD 中自动运行评估
- **评估结果可视化**：用 Langfuse 或自定义 Dashboard
- **失败用例自动归类**：聚类分析失败原因
- **人工复核抽样**：自动评估后人工抽 10% 复核

## 5. 延伸拓展方向

- [[Prompt工程与版本管理]]：Prompt 变更需要评估
- [[AI应用可观测性与Langfuse集成]]：评估数据和生产数据结合
- [[AI网关与多模型路由设计]]：模型对比评估
- [[SpringAI-RAG检索增强实现]]：RAG 评估的对象
- [[AI成本控制与Token计费优化]]：评估本身也有成本

## 6. 参考资料

- [RAGAS: RAG Assessment](https://github.com/explodinggradients/ragas)
- [DeepEval: LLM Evaluation](https://github.com/confident-ai/deepeval)
- [Langfuse: Evaluation](https://langfuse.com/docs/evaluation)
- [GPT-4 as Judge](https://arxiv.org/abs/2306.05685)

#待完善
'''

# ============ 笔记20：多 Agent 协作模式实现 ============
notes["多Agent协作模式实现.md"] = r'''---
title: 多 Agent 协作模式实现
category: Java全栈
subcategory: AI应用开发
tags: [#Java全栈/AI应用, #AI结合/Agent, #难度/高级, #类型/架构]
difficulty: 高级
pre: [[SpringAI-FunctionCalling工具调用]], [[AI工作流编排引擎设计]]
related: [[Agent记忆机制设计与实现]], [[AI应用可观测性与Langfuse集成]]
update: 2026-08-13
status: 完善
---

# 多 Agent 协作模式实现

## 1. 核心概述

单个 Agent 能力有限，复杂任务需要多个专业 Agent 协作完成。多 Agent 系统通过角色分工、消息传递、任务编排，让"研究员 Agent"、"程序员 Agent"、"审查员 Agent"等各司其职，协作完成复杂任务。常见模式有流水线、并行、主管-下属、辩论对抗。

**解决的场景问题**：
- 复杂任务需要多个专业领域知识
- 单个 Agent 容易在长任务中跑偏
- 需要不同角色从不同角度审视问题
- 任务可以并行加速
- 需要质量把关（写代码 + Code Review）

## 2. 底层原理/核心逻辑

### 四种协作模式

```
1. 流水线模式 (Pipeline)
   研究员 → 程序员 → 审查员 → 发布
   顺序执行，前一个输出是后一个输入

2. 并行模式 (Parallel)
        ┌→ 研究员A
   任务 ─┼→ 研究员B → 汇总 → 最终回答
        └→ 研究员C

3. 主管-下属模式 (Manager-Worker)
   主管 Agent 分解任务 → 分配给下属 Agent → 汇总结果

4. 辩论对抗模式 (Debate)
   Agent A（正方）↔ Agent B（反方）→ 裁判 → 最终结论
```

### 协作模式对比

| 模式 | 复杂度 | 速度 | 质量 | 适用场景 |
|------|--------|------|------|----------|
| 流水线 | 低 | 中 | 中 | 有明确步骤的任务 |
| 并行 | 中 | 快 | 高 | 可独立分解的任务 |
| 主管-下属 | 高 | 中 | 高 | 复杂、动态分解的任务 |
| 辩论 | 中 | 慢 | 极高 | 需要深度分析、决策 |

### 核心抽象

```
Agent 接口：
  - name: 角色名称
  - description: 角色描述
  - systemPrompt: 系统提示
  - tools: 可用工具
  - execute(input): 执行任务

消息总线：
  - send(receiver, message)
  - broadcast(message)
  - receive()

协调器：
  - 定义协作流程
  - 管理 Agent 生命周期
  - 处理异常和重试
```

## 3. 实操示例

### Agent 接口与基础实现

```java
public interface Agent {
    String getName();
    String getDescription();
    String getSystemPrompt();
    List<ToolCallback> getTools();
    AgentResponse execute(AgentRequest request);
}

public record AgentRequest(
        String task,
        Map<String, Object> context,
        List<Message> history
) {}

public record AgentResponse(
        String content,
        Map<String, Object> metadata,
        List<Message> messages
) {}

// 基础 Agent 实现
public abstract class BaseAgent implements Agent {

    protected final ChatModel chatModel;
    protected final String name;
    protected final String description;

    protected BaseAgent(ChatModel chatModel, String name, String description) {
        this.chatModel = chatModel;
        this.name = name;
        this.description = description;
    }

    @Override
    public AgentResponse execute(AgentRequest request) {
        List<Message> messages = new ArrayList<>();
        messages.add(new SystemMessage(getSystemPrompt()));
        messages.addAll(request.history());
        messages.add(new UserMessage(request.task()));

        Prompt prompt = new Prompt(messages);
        ChatResponse response = chatModel.call(prompt);

        String content = response.getResult().getOutput().getText();
        return new AgentResponse(content, Map.of("agent", name), messages);
    }

    @Override
    public List<ToolCallback> getTools() {
        return List.of();
    }
}
```

### 专业 Agent 定义

```java
// 研究员 Agent
@Component
public class ResearcherAgent extends BaseAgent {

    public ResearcherAgent(ChatModel chatModel) {
        super(chatModel, "researcher", "研究员，负责收集和分析信息");
    }

    @Override
    public String getSystemPrompt() {
        return """
                你是一个专业的研究员。
                你的职责：
                1. 分析任务需求，确定需要收集的信息
                2. 使用搜索工具收集相关资料
                3. 整理信息，输出结构化的研究报告
                4. 标注信息来源和可信度

                输出格式：
                ## 研究报告
                ### 关键发现
                - ...
                ### 详细分析
                ...
                ### 参考资料
                - ...
                """;
    }

    @Override
    public List<ToolCallback> getTools() {
        return List.of(webSearchTool, wikipediaTool);
    }
}

// 程序员 Agent
@Component
public class CoderAgent extends BaseAgent {

    public CoderAgent(ChatModel chatModel) {
        super(chatModel, "coder", "程序员，负责编写代码");
    }

    @Override
    public String getSystemPrompt() {
        return """
                你是一个资深全栈工程师。
                你的职责：
                1. 根据需求编写高质量代码
                2. 代码要有注释、异常处理
                3. 遵循最佳实践和设计模式
                4. 输出可直接运行的代码

                代码要求：
                - 使用 Java 17+ 语法
                - 包含必要的 import
                - 有清晰的注释
                """;
    }
}

// 审查员 Agent
@Component
public class ReviewerAgent extends BaseAgent {

    public ReviewerAgent(ChatModel chatModel) {
        super(chatModel, "reviewer", "审查员，负责质量把关");
    }

    @Override
    public String getSystemPrompt() {
        return """
                你是一个严格的代码审查员。
                审查维度：
                1. 正确性：是否有 bug
                2. 安全性：是否有安全漏洞
                3. 性能：是否有性能问题
                4. 可读性：代码是否清晰
                5. 完整性：是否覆盖所有需求

                输出格式：
                ## 审查结果
                - 总体评价：通过/需修改
                - 问题列表：
                  1. [严重程度] 问题描述 - 修复建议
                """;
    }
}
```

### 流水线协作

```java
@Service
public class PipelineOrchestrator {

    private final ResearcherAgent researcher;
    private final CoderAgent coder;
    private final ReviewerAgent reviewer;

    public PipelineResult execute(String task) {
        // 第1步：研究员收集信息
        AgentResponse researchResult = researcher.execute(
                new AgentRequest(task, Map.of(), List.of()));

        // 第2步：程序员写代码
        AgentResponse codeResult = coder.execute(
                new AgentRequest(
                        "根据以下研究报告实现代码：\n" + researchResult.content(),
                        Map.of("research", researchResult.content()),
                        List.of()
                ));

        // 第3步：审查员审查
        AgentResponse reviewResult = reviewer.execute(
                new AgentRequest(
                        "请审查以下代码：\n" + codeResult.content(),
                        Map.of("code", codeResult.content()),
                        List.of()
                ));

        // 如果审查不通过，返回修改
        if (reviewResult.content().contains("需修改")) {
            AgentResponse revisedCode = coder.execute(
                    new AgentRequest(
                            "根据审查意见修改代码：\n" + reviewResult.content()
                            + "\n\n原代码：\n" + codeResult.content(),
                            Map.of(), List.of()
                    ));
            return new PipelineResult(researchResult.content(),
                    revisedCode.content(), reviewResult.content(), true);
        }

        return new PipelineResult(researchResult.content(),
                codeResult.content(), reviewResult.content(), false);
    }

    public record PipelineResult(String research, String code,
                                 String review, boolean wasRevised) {}
}
```

### 主管-下属模式

```java
@Service
public class ManagerAgent extends BaseAgent {

    private final List<Agent> workers;

    public ManagerAgent(ChatModel chatModel, List<Agent> workers) {
        super(chatModel, "manager", "主管，负责分解和分配任务");
        this.workers = workers;
    }

    @Override
    public String getSystemPrompt() {
        return """
                你是一个项目经理。
                你的职责：
                1. 分析复杂任务，分解为子任务
                2. 将子任务分配给合适的团队成员
                3. 汇总各成员的成果
                4. 确保最终交付质量

                可用团队成员：
                - researcher：研究员，擅长信息收集
                - coder：程序员，擅长代码实现
                - reviewer：审查员，擅长质量把关
                """;
    }

    @Override
    public AgentResponse execute(AgentRequest request) {
        // 1. 任务分解
        String decompositionPrompt = """
                请将以下任务分解为 2-4 个子任务，每个子任务指定负责人。
                输出 JSON 格式：
                {"subtasks": [{"task": "...", "assignee": "researcher/coder/reviewer"}]}

                任务：%s
                """.formatted(request.task());

        String decomposition = chatModel.call(decompositionPrompt);

        // 2. 解析并分配任务
        List<Subtask> subtasks = parseSubtasks(decomposition);
        Map<String, String> results = new LinkedHashMap<>();

        for (Subtask subtask : subtasks) {
            Agent worker = findWorker(subtask.assignee());
            if (worker != null) {
                AgentResponse response = worker.execute(
                        new AgentRequest(subtask.task(),
                                Map.of("previousResults", results),
                                List.of()));
                results.put(subtask.task(), response.content());
            }
        }

        // 3. 汇总结果
        String summary = chatModel.call("""
                请汇总以下各成员的工作成果，形成最终交付物。

                %s

                最终交付：
                """.formatted(formatResults(results)));

        return new AgentResponse(summary, Map.of("subtasks", subtasks), List.of());
    }

    private Agent findWorker(String name) {
        return workers.stream()
                .filter(w -> w.getName().equals(name))
                .findFirst()
                .orElse(null);
    }

    private record Subtask(String task, String assignee) {}
}
```

### 辩论对抗模式

```java
@Service
public class DebateOrchestrator {

    private final ChatModel chatModel;

    public DebateResult debate(String topic, int rounds) {
        String proPosition = "支持：" + topic;
        String conPosition = "反对：" + topic;

        List<DebateRound> history = new ArrayList<>();

        for (int i = 0; i < rounds; i++) {
            // 正方发言
            String proArg = chatModel.call("""
                    你是正方辩手，支持以下观点。请给出有力的论证。
                    观点：%s
                    历史辩论：%s
                    你的发言（200字以内）：
                    """.formatted(proPosition, formatHistory(history)));

            // 反方反驳
            String conArg = chatModel.call("""
                    你是反方辩手，反对以下观点。请针对正方的发言进行反驳。
                    观点：%s
                    正方最新发言：%s
                    你的反驳（200字以内）：
                    """.formatted(conPosition, proArg));

            history.add(new DebateRound(i + 1, proArg, conArg));
        }

        // 裁判总结
        String verdict = chatModel.call("""
                你是辩论裁判。请根据以下辩论内容，判断哪方更有说服力，并给出总结。
                主题：%s
                辩论记录：%s
                裁判总结：
                """.formatted(topic, formatHistory(history)));

        return new DebateResult(topic, history, verdict);
    }

    public record DebateRound(int round, String pro, String con) {}
    public record DebateResult(String topic, List<DebateRound> rounds, String verdict) {}

    private String formatHistory(List<DebateRound> history) {
        return history.stream()
                .map(r -> "第%d轮\n正方：%s\n反方：%s".formatted(r.round(), r.pro(), r.con()))
                .collect(Collectors.joining("\n\n"));
    }
}
```

### 消息总线与循环检测

```java
@Component
public class MessageBus {

    private final Map<String, BlockingQueue<AgentMessage>> queues = new ConcurrentHashMap<>();
    private final Set<String> activeConversations = ConcurrentHashMap.newKeySet();

    public void register(String agentName) {
        queues.putIfAbsent(agentName, new LinkedBlockingQueue<>());
    }

    public void send(String from, String to, String content, Map<String, Object> metadata) {
        queues.get(to).offer(new AgentMessage(from, to, content, metadata,
                System.currentTimeMillis()));
    }

    public AgentMessage receive(String agentName, long timeoutMs) throws InterruptedException {
        return queues.get(agentName).poll(timeoutMs, TimeUnit.MILLISECONDS);
    }

    // 循环检测：防止 Agent 之间无限对话
    public boolean detectLoop(String conversationId, int maxMessages) {
        // 简化实现：统计对话消息数
        return false;
    }

    public record AgentMessage(String from, String to, String content,
                               Map<String, Object> metadata, long timestamp) {}
}
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| Agent 之间无限循环 | 没有终止条件 | 加最大轮次限制，循环检测 |
| 任务分解不合理 | 主管 Agent 能力不足 | 优化主管 Prompt，加 Few-shot 示例 |
| 成本太高 | 多 Agent 多次调用 | 简单任务用单 Agent，复杂任务才用多 Agent |
| 结果不一致 | 每次运行结果不同 | 固定 seed，加确定性后处理 |
| 上下文丢失 | Agent 之间传递信息不完整 | 用结构化的 context 对象 |

### 踩坑点

1. **不要让 Agent 自己决定协作模式**：由编排器硬编码流程
2. **Agent 角色要明确**：模糊的角色定义会导致职责重叠
3. **工具权限要隔离**：不同 Agent 只能访问自己的工具
4. **要有超时机制**：防止某个 Agent 卡住整个流程

### 优化方案

- **并行执行**：独立子任务用 CompletableFuture 并行
- **结果缓存**：相同子任务结果缓存
- **动态 Agent 选择**：根据任务类型选择合适的 Agent 组合
- **人工介入点**：关键节点支持人工审核

## 5. 延伸拓展方向

- [[AI工作流编排引擎设计]]：更通用的编排引擎
- [[Agent记忆机制设计与实现]]：Agent 的记忆管理
- [[SpringAI-FunctionCalling工具调用]]：Agent 的工具能力
- [[AI应用可观测性与Langfuse集成]]：多 Agent 链路追踪
- [[AI应用安全与Prompt注入防护]]：多 Agent 系统的安全

## 6. 参考资料

- [AutoGen: Multi-Agent Framework](https://github.com/microsoft/autogen)
- [LangGraph: Multi-Agent Workflows](https://github.com/langchain-ai/langgraph)
- [CrewAI: Multi-Agent Orchestration](https://github.com/joaomdmoura/crewAI)
- [MetaGPT: Multi-Agent Framework](https://github.com/geekan/MetaGPT)

#待完善
'''

# ============ 笔记23：AI 工作流编排引擎设计 ============
notes["AI工作流编排引擎设计.md"] = r'''---
title: AI 工作流编排引擎设计
category: Java全栈
subcategory: AI应用开发
tags: [#Java全栈/AI应用, #AI结合/工作流, #难度/高级, #类型/架构]
difficulty: 高级
pre: [[多Agent协作模式实现]], [[Java-设计模式实战]]
related: [[AI网关与多模型路由设计]], [[AI应用可观测性与Langfuse集成]]
update: 2026-08-13
status: 完善
---

# AI 工作流编排引擎设计

## 1. 核心概述

AI 应用通常是多步骤的复杂流程（检索→推理→工具调用→再推理→输出），硬编码流程难以维护和扩展。工作流编排引擎将流程定义为 DAG（有向无环图），节点是 LLM 调用、工具执行、条件判断、HTTP 请求等，支持可视化编排、版本管理、执行追踪、错误重试，是生产级 AI 应用的基础设施。

**解决的场景问题**：
- AI 流程复杂，代码里到处是 if-else 和回调
- 流程变更需要改代码、重新部署
- 无法直观看到流程的执行状态
- 某个步骤失败后无法优雅重试
- 业务人员想自己调整流程

## 2. 底层原理/核心逻辑

### 工作流核心概念

```
Workflow（工作流）：完整的业务流程定义
  └── Node（节点）：流程中的一个步骤
        ├── LLMNode：调用大模型
        ├── ToolNode：执行工具
        ├── ConditionNode：条件判断
        ├── HttpNode：HTTP 请求
        ├── CodeNode：执行自定义代码
        └── EndNode：结束节点
  └── Edge（边）：节点之间的连接
  └── Context（上下文）：流程执行时的数据传递
```

### DAG 执行原理

```
1. 拓扑排序：确定节点执行顺序
2. 入度为 0 的节点可以执行
3. 节点执行完成后，更新下游节点的入度
4. 入度变为 0 的节点加入执行队列
5. 支持并行执行（多个入度为 0 的节点同时执行）
```

### 节点执行器抽象

```
NodeExecutor
  ├── execute(context): 执行节点
  ├── validate(): 校验节点配置
  └── getInputSchema(): 输入参数 schema
```

## 3. 实操示例

### 工作流模型定义

```java
// 节点类型
public enum NodeType {
    START, LLM, TOOL, CONDITION, HTTP, CODE, END
}

// 节点定义
public record WorkflowNode(
        String id,
        String name,
        NodeType type,
        Map<String, Object> config,
        List<String> nextNodes
) {}

// 边定义
public record WorkflowEdge(
        String from,
        String to,
        String condition  // 条件边的表达式
) {}

// 工作流定义
public record WorkflowDefinition(
        String id,
        String name,
        String version,
        List<WorkflowNode> nodes,
        List<WorkflowEdge> edges,
        Map<String, Object> variables
) {
    public WorkflowNode getStartNode() {
        return nodes.stream()
                .filter(n -> n.type() == NodeType.START)
                .findFirst()
                .orElseThrow();
    }
}
```

### 执行上下文

```java
public class WorkflowContext {

    private final Map<String, Object> variables = new ConcurrentHashMap<>();
    private final Map<String, NodeExecutionResult> nodeResults = new ConcurrentHashMap<>();
    private String currentNodeId;
    private boolean terminated = false;

    public void setVariable(String key, Object value) {
        variables.put(key, value);
    }

    @SuppressWarnings("unchecked")
    public <T> T getVariable(String key) {
        return (T) variables.get(key);
    }

    public void setNodeResult(String nodeId, NodeExecutionResult result) {
        nodeResults.put(nodeId, result);
    }

    public NodeExecutionResult getNodeResult(String nodeId) {
        return nodeResults.get(nodeId);
    }

    // 变量替换：将 ${xxx} 替换为实际值
    public String render(String template) {
        String result = template;
        for (Map.Entry<String, Object> entry : variables.entrySet()) {
            result = result.replace("${" + entry.getKey() + "}",
                    String.valueOf(entry.getValue()));
        }
        return result;
    }

    public void terminate() {
        this.terminated = true;
    }

    public boolean isTerminated() {
        return terminated;
    }

    public record NodeExecutionResult(
            String nodeId,
            Object output,
            long durationMs,
            boolean success,
            String error
    ) {}
}
```

### 节点执行器

```java
public interface NodeExecutor {
    NodeType getType();
    WorkflowContext.NodeExecutionResult execute(WorkflowNode node, WorkflowContext context);
    void validate(WorkflowNode node);
}

// LLM 节点执行器
@Component
public class LlmNodeExecutor implements NodeExecutor {

    private final ChatModel chatModel;

    @Override
    public NodeType getType() { return NodeType.LLM; }

    @Override
    public WorkflowContext.NodeExecutionResult execute(WorkflowNode node, WorkflowContext context) {
        long start = System.currentTimeMillis();
        try {
            String systemPrompt = context.render(
                    (String) node.config().getOrDefault("systemPrompt", ""));
            String userPrompt = context.render(
                    (String) node.config().get("userPrompt"));
            String model = (String) node.config().getOrDefault("model", "gpt-4o");

            ChatResponse response = chatModel.call(
                    new Prompt(List.of(
                            new SystemMessage(systemPrompt),
                            new UserMessage(userPrompt)
                    )));

            String output = response.getResult().getOutput().getText();
            String outputVar = (String) node.config().get("outputVariable");
            if (outputVar != null) {
                context.setVariable(outputVar, output);
            }

            return new WorkflowContext.NodeExecutionResult(
                    node.id(), output, System.currentTimeMillis() - start, true, null);
        } catch (Exception e) {
            return new WorkflowContext.NodeExecutionResult(
                    node.id(), null, System.currentTimeMillis() - start, false, e.getMessage());
        }
    }

    @Override
    public void validate(WorkflowNode node) {
        if (!node.config().containsKey("userPrompt")) {
            throw new IllegalArgumentException("LLM 节点必须配置 userPrompt");
        }
    }
}

// 条件节点执行器
@Component
public class ConditionNodeExecutor implements NodeExecutor {

    @Override
    public NodeType getType() { return NodeType.CONDITION; }

    @Override
    public WorkflowContext.NodeExecutionResult execute(WorkflowNode node, WorkflowContext context) {
        long start = System.currentTimeMillis();
        String expression = context.render((String) node.config().get("expression"));
        // 简单条件求值（实际可用 SpEL / Aviator）
        boolean result = evaluateExpression(expression);
        context.setVariable(node.id() + "_result", result);
        return new WorkflowContext.NodeExecutionResult(
                node.id(), result, System.currentTimeMillis() - start, true, null);
    }

    private boolean evaluateExpression(String expr) {
        // 简化实现：支持 ==, !=, >, <, contains
        if (expr.contains("==")) {
            String[] parts = expr.split("==");
            return parts[0].trim().equals(parts[1].trim());
        }
        if (expr.contains("contains")) {
            String[] parts = expr.split("contains");
            return parts[0].trim().contains(parts[1].trim());
        }
        return Boolean.parseBoolean(expr.trim());
    }

    @Override
    public void validate(WorkflowNode node) {}
}

// HTTP 节点执行器
@Component
public class HttpNodeExecutor implements NodeExecutor {

    private final RestTemplate restTemplate = new RestTemplate();

    @Override
    public NodeType getType() { return NodeType.HTTP; }

    @Override
    public WorkflowContext.NodeExecutionResult execute(WorkflowNode node, WorkflowContext context) {
        long start = System.currentTimeMillis();
        try {
            String url = context.render((String) node.config().get("url"));
            String method = (String) node.config().getOrDefault("method", "GET");
            String body = context.render((String) node.config().getOrDefault("body", ""));

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<String> entity = new HttpEntity<>(body, headers);

            ResponseEntity<String> response = restTemplate.exchange(
                    url, HttpMethod.valueOf(method), entity, String.class);

            String outputVar = (String) node.config().get("outputVariable");
            if (outputVar != null) {
                context.setVariable(outputVar, response.getBody());
            }

            return new WorkflowContext.NodeExecutionResult(
                    node.id(), response.getBody(),
                    System.currentTimeMillis() - start, true, null);
        } catch (Exception e) {
            return new WorkflowContext.NodeExecutionResult(
                    node.id(), null, System.currentTimeMillis() - start, false, e.getMessage());
        }
    }

    @Override
    public void validate(WorkflowNode node) {}
}
```

### 工作流引擎

```java
@Service
public class WorkflowEngine {

    private final Map<NodeType, NodeExecutor> executors;
    private final DAGValidator validator;

    public WorkflowEngine(List<NodeExecutor> executorList) {
        this.executors = executorList.stream()
                .collect(Collectors.toMap(NodeExecutor::getType, Function.identity()));
        this.validator = new DAGValidator();
    }

    public WorkflowExecutionResult execute(WorkflowDefinition workflow,
                                           Map<String, Object> input) {
        // 1. 校验 DAG
        validator.validate(workflow);

        // 2. 初始化上下文
        WorkflowContext context = new WorkflowContext();
        input.forEach(context::setVariable);

        // 3. 拓扑排序
        List<String> executionOrder = topologicalSort(workflow);

        // 4. 按顺序执行
        for (String nodeId : executionOrder) {
            if (context.isTerminated()) break;

            WorkflowNode node = findNode(workflow, nodeId);
            NodeExecutor executor = executors.get(node.type());

            if (executor == null) {
                throw new IllegalStateException("没有找到节点执行器: " + node.type());
            }

            WorkflowContext.NodeExecutionResult result = executor.execute(node, context);
            context.setNodeResult(nodeId, result);

            if (!result.success()) {
                // 错误处理：重试或终止
                boolean retried = handleError(node, context, executor);
                if (!retried) {
                    return new WorkflowExecutionResult(false,
                            "节点 " + node.name() + " 执行失败: " + result.error(),
                            context);
                }
            }
        }

        return new WorkflowExecutionResult(true, "执行成功", context);
    }

    private List<String> topologicalSort(WorkflowDefinition workflow) {
        // Kahn 算法拓扑排序
        Map<String, Integer> inDegree = new HashMap<>();
        Map<String, List<String>> adjacency = new HashMap<>();

        for (WorkflowNode node : workflow.nodes()) {
            inDegree.put(node.id(), 0);
            adjacency.put(node.id(), new ArrayList<>());
        }
        for (WorkflowEdge edge : workflow.edges()) {
            adjacency.get(edge.from()).add(edge.to());
            inDegree.merge(edge.to(), 1, Integer::sum);
        }

        Queue<String> queue = new LinkedList<>();
        inDegree.forEach((id, deg) -> { if (deg == 0) queue.offer(id); });

        List<String> result = new ArrayList<>();
        while (!queue.isEmpty()) {
            String nodeId = queue.poll();
            result.add(nodeId);
            for (String next : adjacency.get(nodeId)) {
                inDegree.merge(next, -1, Integer::sum);
                if (inDegree.get(next) == 0) queue.offer(next);
            }
        }
        return result;
    }

    private boolean handleError(WorkflowNode node, WorkflowContext context,
                                NodeExecutor executor) {
        int maxRetries = (int) node.config().getOrDefault("maxRetries", 0);
        for (int i = 0; i < maxRetries; i++) {
            WorkflowContext.NodeExecutionResult retry = executor.execute(node, context);
            if (retry.success()) {
                context.setNodeResult(node.id(), retry);
                return true;
            }
        }
        return false;
    }

    private WorkflowNode findNode(WorkflowDefinition workflow, String id) {
        return workflow.nodes().stream()
                .filter(n -> n.id().equals(id))
                .findFirst()
                .orElseThrow();
    }

    public record WorkflowExecutionResult(
            boolean success,
            String message,
            WorkflowContext context
    ) {}
}
```

### DAG 校验器

```java
@Component
public class DAGValidator {

    public void validate(WorkflowDefinition workflow) {
        // 1. 检查是否有且仅有一个 START 节点
        long startCount = workflow.nodes().stream()
                .filter(n -> n.type() == NodeType.START).count();
        if (startCount != 1) {
            throw new IllegalArgumentException("工作流必须有且仅有一个 START 节点");
        }

        // 2. 检查环（用 DFS）
        if (hasCycle(workflow)) {
            throw new IllegalArgumentException("工作流不能包含环");
        }

        // 3. 检查节点配置
        Map<NodeType, NodeExecutor> executors = new HashMap<>();
        for (WorkflowNode node : workflow.nodes()) {
            NodeExecutor executor = executors.get(node.type());
            if (executor != null) {
                executor.validate(node);
            }
        }

        // 4. 检查边的引用是否存在
        Set<String> nodeIds = workflow.nodes().stream()
                .map(WorkflowNode::id).collect(Collectors.toSet());
        for (WorkflowEdge edge : workflow.edges()) {
            if (!nodeIds.contains(edge.from()) || !nodeIds.contains(edge.to())) {
                throw new IllegalArgumentException("边引用了不存在的节点: " + edge);
            }
        }
    }

    private boolean hasCycle(WorkflowDefinition workflow) {
        Map<String, List<String>> adj = new HashMap<>();
        for (WorkflowEdge e : workflow.edges()) {
            adj.computeIfAbsent(e.from(), k -> new ArrayList<>()).add(e.to());
        }
        Set<String> visited = new HashSet<>();
        Set<String> recStack = new HashSet<>();

        for (WorkflowNode node : workflow.nodes()) {
            if (dfsCycle(node.id(), adj, visited, recStack)) return true;
        }
        return false;
    }

    private boolean dfsCycle(String node, Map<String, List<String>> adj,
                             Set<String> visited, Set<String> recStack) {
        if (recStack.contains(node)) return true;
        if (visited.contains(node)) return false;
        visited.add(node);
        recStack.add(node);
        for (String next : adj.getOrDefault(node, List.of())) {
            if (dfsCycle(next, adj, visited, recStack)) return true;
        }
        recStack.remove(node);
        return false;
    }
}
```

### 客服工作流示例

```java
@Service
public class CustomerServiceWorkflow {

    private final WorkflowEngine engine;

    public String handleCustomerQuery(String query) {
        // 定义工作流
        WorkflowDefinition workflow = new WorkflowDefinition(
                "customer-service", "客服工作流", "1.0",
                List.of(
                    new WorkflowNode("start", "开始", NodeType.START, Map.of(), List.of("classify")),
                    new WorkflowNode("classify", "意图分类", NodeType.LLM, Map.of(
                            "systemPrompt", "你是客服意图分类器，输出：order_query/refund/technical/other",
                            "userPrompt", "用户问题：${query}\n分类：",
                            "outputVariable", "intent",
                            "model", "gpt-4o-mini"
                    ), List.of("condition")),
                    new WorkflowNode("condition", "条件判断", NodeType.CONDITION, Map.of(
                            "expression", "${intent} == technical"
                    ), List.of("technical", "general")),
                    new WorkflowNode("technical", "技术支持", NodeType.LLM, Map.of(
                            "systemPrompt", "你是技术支持专家",
                            "userPrompt", "用户问题：${query}",
                            "outputVariable", "answer"
                    ), List.of("end")),
                    new WorkflowNode("general", "通用回复", NodeType.LLM, Map.of(
                            "systemPrompt", "你是通用客服",
                            "userPrompt", "用户问题：${query}",
                            "outputVariable", "answer"
                    ), List.of("end")),
                    new WorkflowNode("end", "结束", NodeType.END, Map.of(), List.of())
                ),
                List.of(
                    new WorkflowEdge("start", "classify", null),
                    new WorkflowEdge("classify", "condition", null),
                    new WorkflowEdge("condition", "technical", "true"),
                    new WorkflowEdge("condition", "general", "false"),
                    new WorkflowEdge("technical", "end", null),
                    new WorkflowEdge("general", "end", null)
                ),
                Map.of("query", query)
        );

        WorkflowEngine.WorkflowExecutionResult result =
                engine.execute(workflow, Map.of("query", query));

        return result.context().getVariable("answer");
    }
}
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 工作流包含环 | 节点连接错误 | DAG 校验器检测并拒绝 |
| 变量替换不生效 | 变量名拼写错误 | 渲染时检查变量是否存在 |
| 并行节点数据竞争 | 多个节点写同一变量 | 变量加锁或用节点 ID 隔离 |
| 执行状态丢失 | 内存存储，重启丢失 | 持久化执行状态到数据库 |
| 大工作流执行慢 | 串行执行 | 支持并行执行独立节点 |

### 踩坑点

1. **不要用循环依赖**：DAG 必须无环，循环用子工作流或迭代节点
2. **上下文不要太大**：传递必要数据，不要把所有中间结果都存
3. **节点要幂等**：重试时不会产生副作用
4. **超时要设置**：每个节点要有超时时间

### 优化方案

- **并行执行**：用线程池并行执行无依赖的节点
- **工作流持久化**：执行状态存数据库，支持暂停和恢复
- **版本管理**：工作流定义支持版本，可灰度发布
- **可视化编辑器**：前端拖拽编排工作流

## 5. 延伸拓展方向

- [[多Agent协作模式实现]]：Agent 是工作流的一种节点
- [[AI网关与多模型路由设计]]：LLM 节点可以用网关
- [[AI应用可观测性与Langfuse集成]]：工作流执行追踪
- [[AI应用测试与LLM输出评估]]：工作流的端到端测试
- [[AI应用安全与Prompt注入防护]]：工作流中的安全控制

## 6. 参考资料

- [Dify: Workflow Engine](https://github.com/langgenius/dify)
- [n8n: Workflow Automation](https://github.com/n8n-io/n8n)
- [LangGraph: Stateful Workflows](https://github.com/langchain-ai/langgraph)
- [Temporal: Workflow Engine](https://github.com/temporalio/temporal)

#待完善
'''

# 写入文件
for filename, content in notes.items():
    filepath = os.path.join(BASE, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
    print(f"已写入: {filename} ({len(content)} 字节)")

print(f"\n共写入 {len(notes)} 篇笔记")
