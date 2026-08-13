---
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
