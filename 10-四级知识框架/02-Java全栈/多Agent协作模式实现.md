---
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
