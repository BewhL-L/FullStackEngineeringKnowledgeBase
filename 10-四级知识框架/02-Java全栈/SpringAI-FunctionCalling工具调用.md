---
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
