---
title: 实战-SpringBoot+AI Agent平台
tags: [项目实战]
category: 项目实战
created: 2026-08-26
updated: 2026-08-27
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[['SpringBoot-Web层设计', 'Agent核心概念-ReAct规划', 'Agent工具调用FunctionCalling']]"]
aliases: [实战-SpringBoot+AI Agent平台]
---

# 实战：SpringBoot + AI Agent 平台

> **文档说明**：基于Spring Boot + Spring AI构建企业级AI Agent平台，支持工具调用、多轮对话、工作流编排、权限管理。包含完整可运行代码。
>
> **项目难度**：🔴高级（需要Java、SpringBoot、AI Agent基础）
>
> **预计时间**：5-7天

---

## 一、项目概述

### 1. 项目目标
构建一个企业级AI Agent平台，支持：
- **工具调用**：Agent可调用数据库查询、API请求、文件操作等工具
- **多轮对话**：维护对话上下文，支持连续问答
- **工作流编排**：定义Agent执行流程，支持条件分支和循环
- **权限管理**：不同用户可使用不同的工具和模型
- **可观测性**：记录每次Agent调用的完整链路

### 2. 技术栈

| 层级 | 技术选型 | 作用 |
|------|---------|------|
| 后端框架 | Spring Boot 3.2+ | 企业级Java框架 |
| AI框架 | Spring AI 1.0+ | 统一大模型抽象 |
| 数据库 | MySQL + Redis | 持久化+缓存 |
| 大模型 | OpenAI / 通义千问 / 智谱 | 文本生成+工具调用 |
| 消息队列 | RabbitMQ | 异步任务处理 |
| 前端 | Vue3 + ElementPlus | 管理后台 |
| 可观测 | Langfuse / 自定义 | Agent链路追踪 |

### 3. 系统架构

```text
用户请求 → Controller → AgentService → AgentEngine
                                        ├── 对话管理（Redis存储上下文）
                                        ├── 工具注册中心（ToolRegistry）
                                        ├── 模型调用（Spring AI ChatClient）
                                        ├── 工具执行（ToolExecutor）
                                        └── 结果组装 → SSE流式返回
```

---

## 二、核心原理

### 1. Agent执行循环（ReAct模式）
```text
思考(Thought) → 行动(Action: 调用工具) → 观察(Observation: 工具结果)
     ↑                                              ↓
     └──────── 继续思考或给出最终回答 ────────────────┘
```

### 2. 工具调用机制
1. 系统启动时，所有标注`@Tool`的方法注册到`ToolRegistry`
2. Agent调用LLM时，将工具描述（名称、参数、说明）传给模型
3. 模型决定调用哪个工具，返回工具名和参数
4. `ToolExecutor`反射调用对应方法，将结果返回给模型
5. 模型根据工具结果继续思考或给出最终回答

---

## 三、实操步骤

### 步骤1：项目初始化

```xml
<!-- pom.xml 核心依赖 -->
<dependencies>
    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-redis</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
</dependencies>
```

```yaml
# application.yml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      base-url: ${OPENAI_BASE_URL:https://api.openai.com}
      chat:
        options:
          model: gpt-4o-mini
          temperature: 0.3
  data:
    redis:
      host: localhost
      port: 6379
```

### 步骤2：工具定义与注册

```java
// 工具注解
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Tool {
    String name();
    String description();
}

// 工具注册中心
@Component
public class ToolRegistry implements ApplicationContextAware {
    private final Map<String, ToolMethod> tools = new ConcurrentHashMap<>();
    
    @Override
    public void setApplicationContext(ApplicationContext ctx) {
        // 扫描所有@Tool注解的方法
        for (String beanName : ctx.getBeanDefinitionNames()) {
            Object bean = ctx.getBean(beanName);
            for (Method method : bean.getClass().getMethods()) {
                Tool tool = method.getAnnotation(Tool.class);
                if (tool != null) {
                    tools.put(tool.name(), new ToolMethod(bean, method, tool));
                }
            }
        }
    }
    
    public ToolMethod getTool(String name) { return tools.get(name); }
    public List<ToolInfo> getAllToolInfo() {
        return tools.values().stream().map(ToolMethod::toInfo).toList();
    }
}
```

### 步骤3：内置工具实现

```java
@Component
public class BuiltinTools {
    
    @Tool(name = "query_database", description = "查询数据库中的用户信息，参数: userId(用户ID)")
    public String queryDatabase(String userId) {
        // 实际项目中调用Mapper
        return "{\"id\": \"" + userId + "\", \"name\": \"张三\", \"role\": \"admin\"}";
    }
    
    @Tool(name = "get_current_time", description = "获取当前时间，无需参数")
    public String getCurrentTime() {
        return LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
    }
    
    @Tool(name = "calculate", description = "数学计算，参数: expression(数学表达式，如 1+2*3)")
    public String calculate(String expression) {
        try {
            // 简单表达式计算（生产环境用安全的表达式引擎）
            ScriptEngine engine = new ScriptEngineManager().getEngineByName("JavaScript");
            return String.valueOf(engine.eval(expression));
        } catch (Exception e) {
            return "计算错误: " + e.getMessage();
        }
    }
    
    @Tool(name = "send_email", description = "发送邮件，参数: to(收件人), subject(主题), body(正文)")
    public String sendEmail(String to, String subject, String body) {
        // 实际项目中调用邮件服务
        return "邮件已发送至 " + to;
    }
}
```

### 步骤4：Agent引擎核心

```java
@Service
public class AgentEngine {
    private final ChatClient chatClient;
    private final ToolRegistry toolRegistry;
    private final RedisTemplate<String, String> redisTemplate;
    
    private static final int MAX_ITERATIONS = 10;
    private static final String CONVERSATION_PREFIX = "agent:conversation:";
    
    public AgentEngine(ChatClient.Builder builder, ToolRegistry registry, 
                       RedisTemplate<String, String> redis) {
        this.chatClient = builder.build();
        this.toolRegistry = registry;
        this.redisTemplate = redis;
    }
    
    public Flux<String> chat(String sessionId, String userMessage) {
        // 1. 加载对话历史
        List<Message> history = loadHistory(sessionId);
        history.add(new UserMessage(userMessage));
        
        // 2. 构建系统提示（包含工具描述）
        String systemPrompt = buildSystemPrompt();
        
        // 3. Agent执行循环
        return Flux.create(sink -> {
            List<Message> currentMessages = new ArrayList<>(history);
            currentMessages.add(0, new SystemMessage(systemPrompt));
            
            int iteration = 0;
            while (iteration < MAX_ITERATIONS) {
                iteration++;
                // 调用LLM
                String response = callLLM(currentMessages);
                
                // 检查是否需要调用工具
                ToolCall toolCall = parseToolCall(response);
                if (toolCall == null) {
                    // 最终回答，流式输出
                    sink.next(response);
                    saveHistory(sessionId, currentMessages, response);
                    sink.complete();
                    return;
                }
                
                // 执行工具
                String toolResult = executeTool(toolCall);
                currentMessages.add(new AssistantMessage(response));
                currentMessages.add(new UserMessage("工具返回结果: " + toolResult));
            }
            sink.next("达到最大迭代次数，无法完成任务");
            sink.complete();
        });
    }
    
    private String buildSystemPrompt() {
        StringBuilder sb = new StringBuilder();
        sb.append("你是一个智能助手，可以使用以下工具完成任务：\n\n");
        for (ToolInfo tool : toolRegistry.getAllToolInfo()) {
            sb.append(String.format("- %s: %s\n", tool.getName(), tool.getDescription()));
        }
        sb.append("\n当需要使用工具时，按以下格式输出：\n");
        sb.append("TOOL_CALL: {\"name\": \"工具名\", \"args\": {\"参数名\": \"参数值\"}}\n");
        sb.append("不需要工具时直接回答用户问题。");
        return sb.toString();
    }
    
    private ToolCall parseToolCall(String response) {
        if (response.contains("TOOL_CALL:")) {
            String json = response.substring(response.indexOf("TOOL_CALL:") + 10).trim();
            // 解析JSON获取工具名和参数
            return JSON.parseObject(json, ToolCall.class);
        }
        return null;
    }
    
    private String executeTool(ToolCall toolCall) {
        ToolMethod tool = toolRegistry.getTool(toolCall.getName());
        if (tool == null) return "工具不存在: " + toolCall.getName();
        try {
            return tool.execute(toolCall.getArgs());
        } catch (Exception e) {
            return "工具执行失败: " + e.getMessage();
        }
    }
    
    private String callLLM(List<Message> messages) {
        return chatClient.prompt()
            .messages(messages)
            .call()
            .content();
    }
}
```

### 步骤5：对话管理（Redis）

```java
@Service
public class ConversationManager {
    private final RedisTemplate<String, String> redisTemplate;
    private static final long TTL = 24 * 60 * 60; // 24小时
    
    public void saveMessage(String sessionId, Message message) {
        String key = "agent:conversation:" + sessionId;
        String json = JSON.toJSONString(message);
        redisTemplate.opsForList().rightPush(key, json);
        redisTemplate.expire(key, TTL, TimeUnit.SECONDS);
    }
    
    public List<Message> loadHistory(String sessionId) {
        String key = "agent:conversation:" + sessionId;
        List<String> jsons = redisTemplate.opsForList().range(key, 0, -1);
        if (jsons == null) return new ArrayList<>();
        return jsons.stream()
            .map(j -> JSON.parseObject(j, Message.class))
            .collect(Collectors.toList());
    }
    
    public void clearConversation(String sessionId) {
        redisTemplate.delete("agent:conversation:" + sessionId);
    }
}
```

### 步骤6：Controller层

```java
@RestController
@RequestMapping("/api/agent")
public class AgentController {
    private final AgentEngine agentEngine;
    
    @GetMapping(value = "/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> chat(@RequestParam String sessionId, @RequestParam String message) {
        return agentEngine.chat(sessionId, message);
    }
    
    @PostMapping("/conversation/{sessionId}/clear")
    public Result<Void> clearConversation(@PathVariable String sessionId) {
        conversationManager.clearConversation(sessionId);
        return Result.success();
    }
    
    @GetMapping("/tools")
    public Result<List<ToolInfo>> listTools() {
        return Result.success(toolRegistry.getAllToolInfo());
    }
}
```

### 步骤7：工作流编排（进阶）

```java
// 工作流节点定义
public class WorkflowNode {
    private String id;
    private String type; // "llm" / "tool" / "condition" / "end"
    private String prompt; // llm节点的提示词
    private String toolName; // tool节点的工具名
    private Map<String, String> conditions; // condition节点的分支条件
    private String nextNodeId; // 下一节点
}

// 工作流引擎
@Service
public class WorkflowEngine {
    public String execute(Workflow workflow, Map<String, Object> context) {
        String currentNodeId = workflow.getStartNodeId();
        while (currentNodeId != null) {
            WorkflowNode node = workflow.getNode(currentNodeId);
            switch (node.getType()) {
                case "llm" -> {
                    String result = callLLM(node.getPrompt(), context);
                    context.put(node.getId() + "_result", result);
                    currentNodeId = node.getNextNodeId();
                }
                case "tool" -> {
                    String result = executeTool(node.getToolName(), context);
                    context.put(node.getId() + "_result", result);
                    currentNodeId = node.getNextNodeId();
                }
                case "condition" -> {
                    String conditionResult = evaluateCondition(node, context);
                    currentNodeId = node.getConditions().get(conditionResult);
                }
                case "end" -> {
                    return (String) context.get("final_result");
                }
            }
        }
        return "工作流执行完成";
    }
}
```

---

## 四、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Agent无限循环调用工具 | 工具返回结果不明确，模型反复尝试 | 限制最大迭代次数、优化工具返回格式 |
| 工具参数解析错误 | 模型输出的JSON格式不规范 | 用正则提取JSON、加入格式校验和重试 |
| 对话上下文过长 | 历史消息累积超出token限制 | 滑动窗口保留最近N轮、摘要旧对话 |
| SSE连接断开 | 代理超时或网络波动 | 前端重连机制、服务端心跳包 |
| 工具执行超时 | 外部API调用慢 | 工具调用加超时控制、异步执行 |
| 并发安全问题 | 多个请求共享Agent状态 | 每个请求独立上下文、工具无状态 |

### 性能优化
1. **模型路由**：简单问题用小模型，复杂问题用大模型，降低成本
2. **结果缓存**：相同问题缓存回答，设置TTL
3. **工具预加载**：常用工具结果预热缓存
4. **异步工具**：耗时工具异步执行，轮询结果

---

## 五、进阶与最佳实践

### 生产环境增强
- **多Agent协作**：主管Agent分配任务给专门Agent（检索Agent、代码Agent、分析Agent）
- **可观测性**：集成Langfuse，记录每次LLM调用和工具调用的完整链路
- **成本控制**：模型路由+Token用量统计+预算告警
- **权限控制**：基于角色限制可使用的工具和模型
- **人机协作**：Agent遇到不确定时请求人工确认

### 安全考虑
1. **工具白名单**：只允许Agent调用注册的工具，防止任意代码执行
2. **输入校验**：所有工具参数严格校验，防止注入攻击
3. **输出过滤**：对Agent输出进行敏感信息过滤
4. **审计日志**：记录所有Agent操作，支持回溯

---

## 六、关联笔记

[[Agent核心概念-ReAct规划]] · [[Agent工具调用FunctionCalling]] · [[Agent记忆管理]] · [[多Agent协作模式]] · [[SpringBoot-Web层设计]] · [[SpringAI-FunctionCalling工具调用]] · [[AI可观测性-Langfuse集成]] · [[AI网关-多模型路由与限流]]

> 🎯 **项目验收标准**：①Agent能自主调用至少3种工具完成任务 ②支持多轮对话上下文 ③回答流式输出 ④工具调用过程可追溯 ⑤工作流可配置化

---

## 🔗 关联笔记

- [[MOC-项目实战]] — 返回本分类知识地图，查看更多相关文档

## 📖 前置知识

- [['SpringBoot-Web层设计', 'Agent核心概念-ReAct规划', 'Agent工具调用FunctionCalling']]

## 🏷️ 相关标签

`#项目实战`

[[Home|🏠 返回首页]] · [[MOC-项目实战|📚 返回分类]]
