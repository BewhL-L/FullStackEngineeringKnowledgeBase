---
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
