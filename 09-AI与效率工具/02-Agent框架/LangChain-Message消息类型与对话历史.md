---
title: LangChain-Message消息类型与对话历史
tags: [LangChain, Message, 对话历史, 记忆机制, ChatModel]
category: AI与效率工具
created: 2026-09-09
updated: 2026-09-09
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[LangChain-核心抽象与链]]", "[[LangChain-Core-Runnable接口与执行机制]]", "[[LLM大模型入门概念]]"]
aliases: [Message消息类型, BaseMessage, ChatMessageHistory, 对话历史, MessageChunk流式消息]
---

# LangChain Message 消息类型与对话历史

> **一句话定义**：Message 是 LangChain 中 LLM 对话的基本数据单元，定义了人类消息、AI消息、系统消息、工具消息等多种角色类型，配合 ChatMessageHistory 实现对话状态的管理和持久化。
>
> **核心价值**：标准化的消息抽象让不同模型提供商的对话格式统一；消息历史管理让多轮对话成为可能；MessageChunk 支持流式输出的增量拼接；多种存储后端适配不同的持久化需求（内存/文件/Redis/数据库）。
>
> **适用场景**：多轮对话应用、聊天机器人、对话式 Agent、需要上下文管理的 RAG 系统、需要持久化对话记录的生产应用。

---

## 一、概述：消息体系设计哲学

### 1.1 为什么需要消息抽象

**概念解释**：想象你在写信给一个朋友——你写信（HumanMessage），朋友回信（AIMessage），你们之间的交流就是一段"对话历史"。LangChain 的消息抽象就是把这个过程标准化：每句话都有明确的"谁说的"（role）和"说了什么"（content）。

**原理说明**：不同的 LLM 提供商有不同的对话格式——OpenAI 用 `[{"role": "user", "content": "..."}]`，Anthropic 用不同的格式。LangChain 通过统一的 Message 抽象层，让你用同一套代码切换不同模型。底层转换由各模型的 ChatModel 实现负责。

### 1.2 消息类型总览

```mermaid
classDiagram
    class BaseMessage {
        <<abstract>>
        +content: Union[str, list]
        +additional_kwargs: dict
        +response_metadata: dict
        +type: str
        +id: Optional[str]
        +pretty_repr()
    }

    class HumanMessage {
        +type: "human"
    }

    class AIMessage {
        +type: "ai"
        +tool_calls: list
    }

    class SystemMessage {
        +type: "system"
    }

    class ToolMessage {
        +type: "tool"
        +tool_call_id: str
        +name: str
    }

    class FunctionMessage {
        +type: "function"
        +name: str
    }

    class ChatMessage {
        +type: "chat"
        +role: str
    }

    class MessageChunk {
        +content: Union[str, list]
        +additional_kwargs: dict
        +type: str
    }

    BaseMessage <|-- HumanMessage
    BaseMessage <|-- AIMessage
    BaseMessage <|-- SystemMessage
    BaseMessage <|-- ToolMessage
    BaseMessage <|-- FunctionMessage
    BaseMessage <|-- ChatMessage
    BaseMessage <|-- MessageChunk
```

### 1.3 核心属性一览

| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `content` | str / list | 消息内容 | "你好" 或 [{"type": "text", "text": "..."}] |
| `additional_kwargs` | dict | 额外参数 | `{"function_call": {...}}` |
| `response_metadata` | dict | 响应元数据 | `{"finish_reason": "stop"}` |
| `type` | str | 消息类型 | "human", "ai", "system" |
| `id` | str | 消息唯一ID | "msg_001" |
| `name` | str | 发送者名称（可选） | "张三" |

### 1.4 第一个消息示例

**基础示例：创建各种类型的消息**

```python
# 示例 1.4.1：创建各种消息类型
from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage,
    ToolMessage, FunctionMessage, ChatMessage
)

# 人类消息
human = HumanMessage(content="你好，AI！")
print(f"Human: {human.content}")
print(f"  type: {human.type}")

# AI 消息
ai = AIMessage(content="你好！很高兴见到你。")
print(f"AI: {ai.content}")
print(f"  type: {ai.type}")

# 系统消息
system = SystemMessage(content="你是一个 helpful 助手。")
print(f"System: {system.content}")
print(f"  type: {system.type}")

# 工具消息
tool = ToolMessage(content="北京今天晴，25度", tool_call_id="call_123", name="weather")
print(f"Tool: {tool.content}")
print(f"  type: {tool.type}")
print(f"  tool_call_id: {tool.tool_call_id}")
```

**进阶示例：消息列表传给模型**

```python
# 示例 1.4.2：构建对话历史并传给模型
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 构建对话历史
messages = [
    SystemMessage(content="你是一个友好的英语老师。"),
    HumanMessage(content="你好！"),
    AIMessage(content="你好！很高兴见到你。今天想学习什么？"),
    HumanMessage(content="我想学习英语语法。"),
    AIMessage(content="好的！我们从最基础的开始吧。"),
]

# 传给 ChatModel
# from langchain_openai import ChatOpenAI
# model = ChatOpenAI()
# response = model.invoke(messages)
# print(response.content)

print(f"对话历史共 {len(messages)} 条消息")
for i, msg in enumerate(messages):
    print(f"  [{i}] {msg.type}: {msg.content[:30]}...")
```

**完整场景：构建多轮对话**

```python
# 示例 1.4.3：完整的多轮对话流程
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

class SimpleChatBot:
    """简单的聊天机器人"""
    def __init__(self):
        self.history = [
            SystemMessage(content="你是一个友好的助手，回答要简洁。")
        ]

    def chat(self, user_input: str) -> str:
        # 添加用户消息
        self.history.append(HumanMessage(content=user_input))

        # 模拟 AI 回复（实际项目中调用 LLM）
        ai_reply = f"收到：{user_input}。这是模拟回复。"

        # 添加 AI 消息
        self.history.append(AIMessage(content=ai_reply))

        return ai_reply

    def show_history(self):
        print("\n=== 对话历史 ===")
        for msg in self.history:
            role = {
                "system": "系统",
                "human": "用户",
                "ai": "AI"
            }.get(msg.type, msg.type)
            print(f"  {role}: {msg.content}")

# 使用
bot = SimpleChatBot()
bot.chat("你好！")
bot.chat("今天天气怎么样？")
bot.chat("谢谢！")
bot.show_history()
```

> 💡 **深度讲解**：Message 抽象是 LangChain 对话系统的基石。它的设计借鉴了 ChatML 等标准对话格式——每条消息有明确的角色标识。这种设计的价值在于：① **模型无关**——同一套消息格式可以对接 OpenAI、Anthropic、Google 等不同模型 ② **类型安全**——SystemMessage/HumanMessage/AIMessage 的区分让模型知道谁在说话 ③ **可扩展**——additional_kwargs 和 response_metadata 支持传递额外信息（如工具调用、函数调用） ④ **流式友好**——MessageChunk 支持流式消息的增量拼接。
>
> **📝 精简总结**：BaseMessage 是所有消息的基类；核心属性包括 content/additional_kwargs/response_metadata/type/id；六种消息类型（Human/AI/System/Tool/Function/Chat）；消息列表是 ChatModel 的标准输入；MessageChunk 支持流式拼接；对话历史是多轮对话的基础。

---

## 二、BaseMessage 基类详解

### 2.1 概念与原理

**概念解释**：BaseMessage 就像所有消息的"模板"——定义了每条消息必须有的基本属性：内容是什么（content）、谁说的（type/role）、附加信息（additional_kwargs）。具体的消息类型（Human/AI/System）只是填充了不同的 type 值。

**原理说明**：BaseMessage 是一个 Pydantic 模型，所有消息类型都继承自它。Pydantic 提供了自动验证、序列化、反序列化能力。这意味着每条消息都是一个结构化对象，可以安全地序列化到 JSON 或从 JSON 恢复。

### 2.2 content 属性详解

**基础示例：content 的不同形式**

```python
# 示例 2.2.1：content 属性的字符串形式
from langchain_core.messages import HumanMessage

# 字符串 content
msg = HumanMessage(content="你好，世界！")
print(f"content 类型: {type(msg.content)}")
print(f"content 值: {msg.content}")
print(f"content 长度: {len(msg.content)}")
```

**进阶示例：content 的多模态形式（列表）**

```python
# 示例 2.2.2：多模态 content（文本+图片）
from langchain_core.messages import HumanMessage

# 多模态 content：列表形式
msg = HumanMessage(content=[
    {"type": "text", "text": "这张图片里有什么？"},
    {"type": "image_url", "image_url": {"url": "https://example.com/cat.jpg"}}
])

print(f"content 是列表，包含 {len(msg.content)} 个部分")
for part in msg.content:
    print(f"  类型: {part['type']}")
```

**完整场景：混合文本和图片输入**

```python
# 示例 2.2.3：多模态消息的实际使用
from langchain_core.messages import HumanMessage

# 构建多模态消息
multimodal_msg = HumanMessage(content=[
    {"type": "text", "text": "请描述这张图片的内容"},
    {"type": "image_url", "image_url": {
        "url": "data:image/jpeg;base64,/9j/4AAQ...",  # base64 编码
        "detail": "high"
    }}
])

# 传给支持多模态的模型
# from langchain_openai import ChatOpenAI
# model = ChatOpenAI(model="gpt-4o")
# response = model.invoke([multimodal_msg])
# print(response.content)
```

### 2.3 additional_kwargs 属性

**概念解释**：additional_kwargs 就像消息的"备用口袋"——标准属性装不下的额外信息都放这里，比如 AI 消息中的工具调用、函数调用。

**示例**：

```python
# 示例 2.3.1：additional_kwargs 的使用
from langchain_core.messages import AIMessage

# AI 消息带工具调用
ai_msg = AIMessage(
    content="",
    additional_kwargs={
        "tool_calls": [
            {
                "id": "call_abc123",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"city": "北京"}'
                }
            }
        ]
    }
)

print(f"content: '{ai_msg.content}'")
print(f"additional_kwargs: {ai_msg.additional_kwargs}")
print(f"工具调用数: {len(ai_msg.additional_kwargs.get('tool_calls', []))}")
```

### 2.4 response_metadata 属性

**概念解释**：response_metadata 记录模型返回的元信息——比如 finish_reason（为什么停止生成）、token 用量、模型名称。这些信息对监控和调试很重要。

**示例**：

```python
# 示例 2.4.1：response_metadata 的结构
from langchain_core.messages import AIMessage

# 模拟模型返回的元数据
ai_msg = AIMessage(
    content="这是 AI 的回答",
    response_metadata={
        "finish_reason": "stop",
        "model_name": "gpt-4",
        "token_usage": {
            "prompt_tokens": 50,
            "completion_tokens": 30,
            "total_tokens": 80
        }
    }
)

print(f"完成原因: {ai_msg.response_metadata['finish_reason']}")
print(f"模型: {ai_msg.response_metadata['model_name']}")
print(f"Token 用量: {ai_msg.response_metadata['token_usage']}")
```

### 2.5 常见坑点

**坑点 1：直接修改消息对象**

错误现象：修改消息后，序列化或比较结果不一致。

原因：BaseMessage 是 Pydantic 模型，默认不可变（frozen）或有验证机制。

正确做法：

```python
# 示例 2.5.1：正确修改消息
from langchain_core.messages import HumanMessage

# ✅ 正确：创建新消息
msg1 = HumanMessage(content="原始内容")
msg2 = msg1.model_copy(update={"content": "修改后的内容"})

# ❌ 错误：直接修改可能有问题
# msg1.content = "修改后"  # 某些版本会报错
```

**坑点 2：content 类型不一致**

错误现象：有时 content 是字符串，有时是列表，导致下游处理出错。

原因：不同模型或不同调用方式返回的 content 格式可能不同。

正确做法：

```python
# 示例 2.5.2：统一处理 content 类型
from langchain_core.messages import AIMessage

def extract_text(msg: AIMessage) -> str:
    """从消息中提取纯文本，无论 content 是什么格式"""
    if isinstance(msg.content, str):
        return msg.content
    elif isinstance(msg.content, list):
        texts = []
        for part in msg.content:
            if isinstance(part, dict) and part.get("type") == "text":
                texts.append(part["text"])
        return "".join(texts)
    return str(msg.content)

# 测试
msg1 = AIMessage(content="纯文本")
msg2 = AIMessage(content=[{"type": "text", "text": "多模态"}, {"type": "image_url", "image_url": {}}])

print(extract_text(msg1))  # 纯文本
print(extract_text(msg2))  # 多模态
```

> 💡 **深度讲解**：BaseMessage 的 Pydantic 设计带来了类型安全和自动序列化，但也需要注意 content 的多态性。在生产环境中，建议始终用 `extract_text` 这样的辅助函数提取文本，而不是直接访问 `msg.content`。`response_metadata` 中的 token_usage 是成本监控的关键数据——每个请求花了多少 token，都在这里记录。
>
> **📝 精简总结**：BaseMessage 是 Pydantic 模型；content 可以是字符串或多模态列表；additional_kwargs 存额外信息（如工具调用）；response_metadata 存模型元数据（finish_reason/token_usage）；用 model_copy 修改消息；统一处理 content 类型。

---

## 三、六种消息类型详解

### 3.1 HumanMessage——人类消息

**概念解释**：HumanMessage 代表"用户说的话"——就像你在对话框里输入的文字。在对话历史中，HumanMessage 和 AIMessage 交替出现，构成完整的对话流。

**原理说明**：HumanMessage 的 `type` 是 `"human"`，是最简单的消息类型——只需要 content。在 OpenAI 格式中对应 `{"role": "user", "content": "..."}`。

**基础示例**：

```python
# 示例 3.1.1：创建 HumanMessage
from langchain_core.messages import HumanMessage

# 基本创建
msg = HumanMessage(content="今天天气怎么样？")
print(f"类型: {msg.type}")  # human
print(f"内容: {msg.content}")
```

**进阶示例：带 name 的 HumanMessage**

```python
# 示例 3.1.2：带名称的人类消息
from langchain_core.messages import HumanMessage

# 多用户场景——区分是谁说的
msg = HumanMessage(content="你好，我是张三", name="zhangsan")
print(f"说话人: {msg.name}")
print(f"内容: {msg.content}")

# 也可以用 keyword 参数
msg2 = HumanMessage(content="我是李四", name="lisi")
```

### 3.2 AIMessage——AI 消息

**概念解释**：AIMessage 代表"AI 说的话"——模型生成的回答。它比 HumanMessage 多了两个重要特性：tool_calls（工具调用）和 response_metadata（元数据）。

**原理说明**：AIMessage 的 `type` 是 `"ai"`。在 OpenAI 格式中对应 `{"role": "assistant", "content": "..."}`。如果 AI 决定调用工具，content 可能为空，tool_calls 在 additional_kwargs 中。

**基础示例**：

```python
# 示例 3.2.1：创建 AIMessage
from langchain_core.messages import AIMessage

# 基本 AI 回复
msg = AIMessage(content="你好！我是 AI 助手。")
print(f"类型: {msg.type}")  # ai
print(f"内容: {msg.content}")
```

**进阶示例：带工具调用的 AIMessage**

```python
# 示例 3.2.2：AI 决定调用工具
from langchain_core.messages import AIMessage

# AI 调用天气查询工具
ai_msg = AIMessage(
    content="",  # 调用工具时 content 通常为空
    additional_kwargs={
        "tool_calls": [
            {
                "id": "call_001",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"city": "北京", "date": "today"}'
                }
            }
        ]
    }
)

# 检查是否有工具调用
has_tool_calls = bool(ai_msg.additional_kwargs.get("tool_calls"))
print(f"是否调用工具: {has_tool_calls}")
if has_tool_calls:
    for tc in ai_msg.additional_kwargs["tool_calls"]:
        print(f"  工具: {tc['function']['name']}")
        print(f"  参数: {tc['function']['arguments']}")
```

### 3.3 SystemMessage——系统消息

**概念解释**：SystemMessage 是"给 AI 的指令"——告诉它"你是谁、你怎么做、你遵守什么规则"。通常放在对话历史的第一条，影响整个对话的行为。

**原理说明**：SystemMessage 的 `type` 是 `"system"`。在 OpenAI 格式中对应 `{"role": "system", "content": "..."}`。系统消息通常在对话开始时设置，中间一般不会改变。

**基础示例**：

```python
# 示例 3.3.1：创建 SystemMessage
from langchain_core.messages import SystemMessage

# 定义 AI 的角色
system_msg = SystemMessage(content="你是一个专业的 Python 编程助手。回答要简洁，提供可运行的代码示例。")
print(f"类型: {system_msg.type}")  # system
print(f"内容: {system_msg.content}")
```

**完整场景：不同角色的系统提示**

```python
# 示例 3.3.2：不同场景的 SystemMessage
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 场景1：英语老师
english_teacher = [
    SystemMessage(content="你是一个耐心的英语老师。用简单的英语回答，遇到难点用中文解释。"),
    HumanMessage(content="How are you?"),
]

# 场景2：代码审查员
code_reviewer = [
    SystemMessage(content="你是一个严格的代码审查员。指出代码中的问题，给出改进建议。"),
    HumanMessage(content="这段 Python 代码有什么问题？\nprint('hello')"),
]

# 场景3：翻译官
translator = [
    SystemMessage(content="你是一个专业翻译。将用户输入的中文翻译成英文，保持原意。"),
    HumanMessage(content="今天天气真好。"),
]

# 实际使用时传给模型
# model = ChatOpenAI()
# for messages in [english_teacher, code_reviewer, translator]:
#     response = model.invoke(messages)
#     print(response.content)
```

### 3.4 ToolMessage——工具消息

**概念解释**：ToolMessage 是"工具执行的结果"——当 AI 决定调用工具后，工具执行完返回的结果就用 ToolMessage 包装，放回对话历史中，让 AI 知道工具的执行结果。

**原理说明**：ToolMessage 的 `type` 是 `"tool"`，必须有 `tool_call_id` 来关联它对应的 AI 工具调用。在 OpenAI 格式中对应 `{"role": "tool", "tool_call_id": "...", "content": "..."}`。

**基础示例**：

```python
# 示例 3.4.1：创建 ToolMessage
from langchain_core.messages import ToolMessage

# 工具执行结果
tool_msg = ToolMessage(
    content="北京今天晴，气温 25°C，湿度 40%",
    tool_call_id="call_001",  # 关联 AI 的工具调用
    name="get_weather"         # 工具名称
)

print(f"类型: {tool_msg.type}")  # tool
print(f"内容: {tool_msg.content}")
print(f"关联调用: {tool_msg.tool_call_id}")
print(f"工具名: {tool_msg.name}")
```

**完整场景：工具调用的完整流程**

```python
# 示例 3.4.2：完整的工具调用对话流程
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# 第一步：用户提问
messages = [
    HumanMessage(content="北京今天天气怎么样？")
]

# 第二步：AI 决定调用工具
ai_tool_call = AIMessage(
    content="",
    additional_kwargs={
        "tool_calls": [{
            "id": "call_weather_001",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"city": "北京"}'
            }
        }]
    }
)
messages.append(ai_tool_call)

# 第三步：执行工具，返回结果
tool_result = ToolMessage(
    content="北京今天晴，25度",
    tool_call_id="call_weather_001",  # 必须匹配
    name="get_weather"
)
messages.append(tool_result)

# 第四步：AI 根据工具结果生成最终回答
ai_final = AIMessage(content="北京今天晴天，气温25度，适合外出！")
messages.append(ai_final)

# 打印完整对话
for i, msg in enumerate(messages):
    role = msg.type
    content_preview = msg.content[:50] if msg.content else "(工具调用)"
    print(f"[{i}] {role}: {content_preview}")
```

### 3.5 FunctionMessage——函数消息（旧版）

**概念解释**：FunctionMessage 是旧版函数调用的消息类型，类似于 ToolMessage 但格式不同。现在推荐使用 ToolMessage。

**示例**：

```python
# 示例 3.5.1：FunctionMessage（旧版）
from langchain_core.messages import FunctionMessage

# 旧版函数调用结果
func_msg = FunctionMessage(
    content='{"temperature": 25, "condition": "sunny"}',
    name="get_weather"
)

print(f"类型: {func_msg.type}")  # function
print(f"函数名: {func_msg.name}")
print(f"结果: {func_msg.content}")
```

### 3.6 ChatMessage——通用聊天消息

**概念解释**：ChatMessage 是一个通用的消息类型，`role` 可以是任意字符串。用于对接那些有自定义角色名的模型提供商。

**示例**：

```python
# 示例 3.6.1：ChatMessage 自定义角色
from langchain_core.messages import ChatMessage

# 自定义角色
msg = ChatMessage(
    content="这是系统管理员的通知",
    role="admin"  # 任意角色名
)

print(f"类型: {msg.type}")   # chat
print(f"角色: {msg.role}")   # admin
print(f"内容: {msg.content}")
```

### 3.7 六种消息类型对比表

| 类型 | type 值 | 必需属性 | 用途 | 对应 OpenAI role |
|------|---------|---------|------|-----------------|
| **HumanMessage** | "human" | content | 用户输入 | user |
| **AIMessage** | "ai" | content | AI 回复 | assistant |
| **SystemMessage** | "system" | content | 系统指令 | system |
| **ToolMessage** | "tool" | content, tool_call_id, name | 工具结果 | tool |
| **FunctionMessage** | "function" | content, name | 函数结果（旧版） | function |
| **ChatMessage** | "chat" | content, role | 自定义角色 | 自定义 |

> 💡 **深度讲解**：六种消息类型的设计反映了对话系统的完整生命周期——System 设置角色 → Human 提问 → AI 回答或调用工具 → Tool 返回结果 → AI 总结回答。理解每种消息的角色和时机，是构建正确对话流程的关键。特别注意 ToolMessage 必须通过 `tool_call_id` 与之前的 AIMessage 中的工具调用关联——这是模型正确理解工具结果的关键。
>
> **📝 精简总结**：六种消息类型——Human（用户）、AI（助手）、System（系统指令）、Tool（工具结果）、Function（旧版函数）、Chat（自定义角色）；ToolMessage 必须关联 tool_call_id；SystemMessage 放对话开头；Human 和 AI 交替出现；FunctionMessage 是旧版，推荐用 ToolMessage。

---

## 四、消息序列化与反序列化

### 4.1 为什么需要序列化

**概念解释**：序列化就是把消息对象"打包"成 JSON 字符串，方便存储或传输。反序列化就是"拆包"——从 JSON 恢复成消息对象。就像寄快递——把东西装箱（序列化），运输到目的地后开箱（反序列化）。

**原理说明**：因为 BaseMessage 是 Pydantic 模型，所以天然支持 `model_dump()` 和 `model_validate()` 方法。LangChain 还提供了 `messages_to_dict()` 和 `messages_from_dict()` 工具函数，方便处理消息列表。

### 4.2 基础序列化

**基础示例：单条消息序列化**

```python
# 示例 4.2.1：消息的序列化与反序列化
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages import messages_from_dict, messages_to_dict

# 创建消息
msg = HumanMessage(content="你好，世界！", name="zhangsan")

# 序列化为字典
msg_dict = msg.model_dump()
print(f"序列化后: {msg_dict}")
# {'content': '你好，世界！', 'additional_kwargs': {}, 'type': 'human', 'name': 'zhangsan', ...}

# 反序列化
restored_msg = HumanMessage.model_validate(msg_dict)
print(f"反序列化后: {restored_msg.content}")
```

**进阶示例：消息列表序列化**

```python
# 示例 4.2.2：消息列表的批量序列化
from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage,
    messages_from_dict, messages_to_dict
)

# 构建对话历史
messages = [
    SystemMessage(content="你是一个助手。"),
    HumanMessage(content="你好！"),
    AIMessage(content="你好！有什么可以帮你的？"),
]

# 序列化为字典列表
serialized = messages_to_dict(messages)
print(f"序列化了 {len(serialized)} 条消息")

# 保存到 JSON 文件
import json
with open("chat_history.json", "w", encoding="utf-8") as f:
    json.dump(serialized, f, ensure_ascii=False, indent=2)

# 从 JSON 恢复
with open("chat_history.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)

restored = messages_from_dict(loaded)
print(f"恢复了 {len(restored)} 条消息")
for msg in restored:
    print(f"  {msg.type}: {msg.content}")
```

### 4.3 常见坑点

**坑点：序列化时丢失类型信息**

错误现象：反序列化后所有消息都变成了 BaseMessage，而不是具体的 HumanMessage/AIMessage。

原因：手动序列化时只保存了 content，没有保存 type 字段。

正确做法：

```python
# 示例 4.3.1：正确的序列化（保留 type 信息）
from langchain_core.messages import HumanMessage, AIMessage, messages_from_dict
import json

# ✅ 正确：用 messages_to_dict 序列化
messages = [HumanMessage(content="hi"), AIMessage(content="hello")]
serialized = messages_to_dict(messages)

# 保存
with open("history.json", "w") as f:
    json.dump(serialized, f)

# 恢复——类型信息自动保留
with open("history.json", "r") as f:
    loaded = json.load(f)
restored = messages_from_dict(loaded)
print(type(restored[0]))  # <class 'langchain_core.messages.human.HumanMessage'>
```

> 💡 **深度讲解**：消息序列化是对话持久化的基础——你需要把对话历史存到数据库，下次加载继续对话。关键点是**保留 type 字段**，否则反序列化后不知道是 Human 还是 AI 消息。LangChain 的 `messages_to_dict` 和 `messages_from_dict` 工具函数自动处理了这个问题，推荐使用。
>
> **📝 精简总结**：消息序列化用 model_dump()，反序列化用 model_validate()；消息列表用 messages_to_dict/messages_from_dict；必须保留 type 字段；推荐用官方工具函数；JSON 文件持久化对话历史。

---

## 五、MessageChunk 与流式消息

### 5.1 概念与原理

**概念解释**：MessageChunk 就像拼图的碎片——LLM 逐字生成时，每来一个字就是一个 chunk。多个 chunk 拼接起来就是完整的消息。流式输出就是不断接收 chunk 并拼接的过程。

**原理说明**：MessageChunk 是 BaseMessage 的流式版本，它的 `__add__` 方法定义了拼接逻辑——content 字符串拼接，additional_kwargs 合并。每次 LLM 流式生成一个 token，就产生一个 AIMessageChunk，你把它们逐个加起来就是完整的 AI 回复。

### 5.2 基础用法

**基础示例：手动拼接 chunk**

```python
# 示例 5.2.1：MessageChunk 的拼接
from langchain_core.messages import AIMessageChunk

# 模拟流式生成的 chunks
chunk1 = AIMessageChunk(content="你")
chunk2 = AIMessageChunk(content="好")
chunk3 = AIMessageChunk(content="，")
chunk4 = AIMessageChunk(content="世界！")

# 拼接
full = chunk1 + chunk2 + chunk3 + chunk4
print(f"完整消息: {full.content}")  # 你好，世界！
```

**进阶示例：流式输出模拟**

```python
# 示例 5.2.2：模拟 LLM 流式输出
from langchain_core.messages import AIMessageChunk

def stream_llm_response(prompt: str):
    """模拟流式 LLM 响应"""
    response_parts = [
        "根据", "你的", "问题", "，", "我", "认为", "...",
    ]
    for part in response_parts:
        yield AIMessageChunk(content=part)

# 消费流式输出
print("AI: ", end="")
full_message = None
for chunk in stream_llm_response("什么是 AI？"):
    print(chunk.content, end="", flush=True)
    if full_message is None:
        full_message = chunk
    else:
        full_message += chunk

print(f"\n完整消息: {full_message.content}")
```

### 5.3 流式消息的实际使用

**示例：ChatModel 流式输出**

```python
# 示例 5.3.1：ChatModel 的真实流式输出
# from langchain_openai import ChatOpenAI

# model = ChatOpenAI(model="gpt-4")

# 流式调用——每次得到一个 AIMessageChunk
# print("AI: ", end="")
# for chunk in model.stream("写一首关于秋天的诗"):
#     print(chunk.content, end="", flush=True)
# print()
```

### 5.4 常见坑点

**坑点：拼接 chunk 时忽略了 additional_kwargs**

错误现象：流式结束后，工具调用信息丢失。

原因：手动拼接时只拼接了 content，没有合并 additional_kwargs。

正确做法：

```python
# 示例 5.4.1：正确拼接包含工具调用的 chunk
from langchain_core.messages import AIMessageChunk

# 正确方式：用 + 运算符自动合并所有字段
chunk1 = AIMessageChunk(content="", additional_kwargs={"tool_calls": [{"id": "1"}]})
chunk2 = AIMessageChunk(content="回答完成")

full = chunk1 + chunk2
print(f"content: {full.content}")
print(f"tool_calls: {full.additional_kwargs.get('tool_calls')}")
```

> 💡 **深度讲解**：MessageChunk 是 LangChain 流式架构的核心。理解了 chunk 的拼接机制，就理解了为什么 `prompt | model | parser` 链可以自动流式输出——每一步的 chunk 自动传递给下一步。在实际项目中，流式输出极大改善用户体验——用户不用等完整回答生成完，而是逐字看到结果，感觉响应更快。
>
> **📝 精简总结**：MessageChunk 是消息的流式碎片；用 + 运算符拼接；content 字符串拼接，additional_kwargs 合并；ChatModel.stream() 返回 chunk 流；拼接时不要手动只拼接 content。

---

## 六、ChatMessageHistory 对话历史管理

### 6.1 概念与原理

**概念解释**：ChatMessageHistory 就像一个"对话笔记本"——你和 AI 的每一轮对话都记在上面。新对话来了就往上加，需要时就翻给 AI 看。笔记本可以存在内存里、文件里、Redis 里、数据库里。

**原理说明**：ChatMessageHistory 是一个接口（抽象基类），定义了 `add_message`/`add_user_message`/`add_ai_message`/`clear`/`messages` 等标准方法。不同的存储后端（内存/文件/Redis/数据库）实现这个接口，提供不同的持久化能力。

### 6.2 InMemoryChatMessageHistory——内存存储

**概念解释**：内存版的对话历史——存在 Python 进程的内存里。最简单、最快，但进程重启就丢失。适合开发调试和短期会话。

**基础示例**：

```python
# 示例 6.2.1：InMemoryChatMessageHistory 基础用法
from langchain_core.chat_history import InMemoryChatMessageHistory

# 创建历史记录
history = InMemoryChatMessageHistory()

# 添加消息
history.add_user_message("你好！")
history.add_ai_message("你好！很高兴见到你。")
history.add_user_message("今天天气怎么样？")
history.add_ai_message("今天晴天，25度。")

# 查看历史
print(f"共 {len(history.messages)} 条消息")
for msg in history.messages:
    print(f"  {msg.type}: {msg.content}")
```

**进阶示例：完整对话流程**

```python
# 示例 6.2.2：使用历史记录的完整对话
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

class ChatSession:
    """带历史记录的对话会话"""
    def __init__(self):
        self.history = InMemoryChatMessageHistory()

    def chat(self, user_input: str) -> str:
        # 1. 记录用户消息
        self.history.add_user_message(user_input)

        # 2. 模拟 AI 回复
        ai_reply = f"收到：{user_input}"
        self.history.add_ai_message(ai_reply)

        return ai_reply

    def get_context(self) -> list:
        """获取完整对话上下文"""
        return self.history.messages

# 使用
session = ChatSession()
session.chat("你好")
session.chat("讲个笑话")
print(f"对话记录: {len(session.get_context())} 条消息")
```

### 6.3 FileChatMessageHistory——文件存储

**概念解释**：把对话历史存到 JSON 文件里。进程重启后对话不丢失。适合单机应用和小规模部署。

**基础示例**：

```python
# 示例 6.3.1：FileChatMessageHistory 使用
from langchain_community.chat_message_histories import FileChatMessageHistory

# 创建文件历史记录
history = FileChatMessageHistory(file_path="chat_history.json")

# 添加消息
history.add_user_message("你好！")
history.add_ai_message("你好！有什么可以帮你的？")

# 查看
for msg in history.messages:
    print(f"{msg.type}: {msg.content}")
```

**完整场景：持久化对话会话**

```python
# 示例 6.3.2：跨会话持久化对话
from langchain_community.chat_message_histories import FileChatMessageHistory

# 第一个会话
session1 = FileChatMessageHistory(file_path="user_123.json")
session1.add_user_message("你好，我是张三")
session1.add_ai_message("你好张三！")

# 新会话加载历史
session1_loaded = FileChatMessageHistory(file_path="user_123.json")
print(f"恢复了 {len(session1_loaded.messages)} 条历史消息")
for msg in session1_loaded.messages:
    print(f"  {msg.type}: {msg.content}")
```

### 6.4 RedisChatMessageHistory——Redis 存储

**概念解释**：把对话历史存到 Redis 里。高性能、支持过期、多实例共享。适合生产环境和分布式部署。

**基础示例**：

```python
# 示例 6.4.1：RedisChatMessageHistory 使用
# from langchain_community.chat_message_histories import RedisChatMessageHistory

# # 创建 Redis 历史记录
# history = RedisChatMessageHistory(
#     session_id="user_123",
#     url="redis://localhost:6379/0",
#     ttl=3600  # 1小时过期
# )

# # 添加消息
# history.add_user_message("你好！")
# history.add_ai_message("你好！")

# # 查看
# for msg in history.messages:
#     print(f"{msg.type}: {msg.content}")
```

### 6.5 SQLChatMessageHistory——数据库存储

**概念解释**：把对话历史存到 SQL 数据库（SQLite/PostgreSQL/MySQL）。支持复杂查询和长期存储。适合企业级应用。

**基础示例**：

```python
# 示例 6.5.1：SQLChatMessageHistory 使用
# from langchain_community.chat_message_histories import SQLChatMessageHistory

# # SQLite 示例
# history = SQLChatMessageHistory(
#     session_id="user_123",
#     connection_string="sqlite:///chat_history.db"
# )

# history.add_user_message("你好！")
# history.add_ai_message("你好！")

# for msg in history.messages:
#     print(f"{msg.type}: {msg.content}")
```

### 6.6 五种存储后端对比表

| 存储类型 | 持久化 | 性能 | 分布式 | 适用场景 |
|---------|--------|------|--------|---------|
| **InMemory** | ❌ 内存 | ⚡ 最快 | ❌ | 开发调试、短期会话 |
| **File** | ✅ 文件 | 快 | ❌ | 单机应用、小规模 |
| **Redis** | ✅ Redis | ⚡ 很快 | ✅ | 生产环境、分布式 |
| **SQL** | ✅ 数据库 | 中等 | ✅ | 企业级、长期存储 |
| **MongoDB** | ✅ MongoDB | 快 | ✅ | 文档型存储 |

> 💡 **深度讲解**：选择哪种存储后端取决于你的应用场景：① 开发阶段用 InMemory 最简单 ② 个人项目用 File 即可 ③ 生产环境用 Redis（高性能+过期） ④ 企业级合规需求用 SQL（可审计）。在 LangGraph 中，对话历史通常通过 Checkpointer 管理，而不是直接用 ChatMessageHistory——这是更现代的做法。
>
> **📝 精简总结**：ChatMessageHistory 是对话历史的标准接口；五种实现——InMemory（内存）、File（文件）、Redis（缓存）、SQL（数据库）、MongoDB（文档）；按场景选择存储后端；生产环境推荐 Redis 或 SQL；InMemory 适合开发调试。

---

## 七、消息修剪与摘要——上下文窗口管理

### 7.1 为什么需要修剪

**概念解释**：LLM 有"记忆容量"限制（上下文窗口）——比如 GPT-4 最多 128K token。对话太长就会超出限制，所以需要"修剪"——把旧的消息删掉或总结成摘要，只保留最近的对话。

**原理说明**：修剪策略有几种：① **消息数限制**——只保留最近 N 条 ② **Token 限制**——只保留 token 数在限制内的消息 ③ **摘要压缩**——把旧消息总结成一段摘要 ④ **混合策略**——保留最近几条 + 早期摘要。

### 7.2 消息数修剪

**基础示例**：

```python
# 示例 7.2.1：按消息数修剪
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages import trim_messages

# 构建长对话
messages = [HumanMessage(content=f"问题{i}") for i in range(20)]

# 只保留最近 10 条
trimmed = trim_messages(
    messages,
    max_count=10,  # 最多 10 条
    strategy="last"  # 保留最近的
)
print(f"原 {len(messages)} 条 → 修剪后 {len(trimmed)} 条")
```

**进阶示例：保留系统消息**

```python
# 示例 7.2.2：修剪时保留系统消息
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.messages import trim_messages

messages = [
    SystemMessage(content="你是一个助手。"),  # 这条必须保留
    HumanMessage(content="你好"),
    AIMessage(content="你好！"),
    HumanMessage(content="问题1"),
    AIMessage(content="回答1"),
    # ... 更多消息
]

# 修剪时保留系统消息
trimmed = trim_messages(
    messages,
    max_count=5,
    strategy="last",
    include_system=True  # 保留系统消息
)
print(f"保留了系统消息: {any(m.type == 'system' for m in trimmed)}")
```

### 7.3 Token 计数修剪

**基础示例**：

```python
# 示例 7.3.1：按 token 数修剪
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages import trim_messages

messages = [
    HumanMessage(content="你好"),
    AIMessage(content="你好！很高兴见到你。"),
    HumanMessage(content="介绍一下 LangChain"),
    AIMessage(content="LangChain 是一个 LLM 应用开发框架..."),
]

# 按 token 数修剪（需要 token 计数器）
# trimmed = trim_messages(
#     messages,
#     max_tokens=100,  # 最多 100 token
#     token_counter=lambda msgs: sum(len(m.content.split()) for m in msgs),
#     strategy="last"
# )
```

### 7.4 摘要压缩

**概念解释**：摘要策略不删除旧消息，而是用 LLM 把它们总结成一段简短的摘要，代替原来的多条消息。就像读书时做笔记——不用记住每句话，只记要点。

**示例**：

```python
# 示例 7.4.1：对话摘要压缩
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

def summarize_old_messages(old_messages: list) -> str:
    """用 LLM 总结旧对话"""
    conversation = "\n".join([f"{m.type}: {m.content}" for m in old_messages])
    # 实际项目中调用 LLM 生成摘要
    return f"[摘要] 之前的对话主要讨论了... 共{len(old_messages)}轮对话"

# 模拟使用
old_messages = [
    HumanMessage(content="你好"),
    AIMessage(content="你好！"),
    HumanMessage(content="什么是 AI？"),
    AIMessage(content="AI 是人工智能..."),
]

# 摘要替换
summary = summarize_old_messages(old_messages)
new_context = [
    SystemMessage(content=f"之前的对话摘要：{summary}"),
    HumanMessage(content="继续聊"),
]

print("压缩后的上下文:")
for m in new_context:
    print(f"  {m.type}: {m.content}")
```

### 7.5 常见坑点

**坑点 1：修剪后系统消息丢失**

错误现象：修剪后 AI 行为变了，因为 SystemMessage 被删了。

原因：默认修剪策略不保留系统消息。

正确做法：

```python
# 示例 7.5.1：确保保留系统消息
# trimmed = trim_messages(
#     messages,
#     max_count=10,
#     include_system=True  # 关键！
# )
```

**坑点 2：修剪后对话上下文断裂**

错误现象：AI 回复和之前的对话脱节。

原因：修剪太激进，把关键上下文删了。

正确做法：使用摘要策略代替纯删除，保留对话的语义连贯性。

> 💡 **深度讲解**：上下文窗口管理是生产级对话系统的核心挑战。理想策略是混合策略：① 系统消息永远保留 ② 最近 N 条消息完整保留 ③ 更早的消息总结成摘要 ④ 定期评估摘要质量。在 LangGraph 中，Checkpointer 自动管理状态，你不需要手动修剪——它帮你管理消息列表。
>
> **📝 精简总结**：修剪策略包括消息数限制、token 限制、摘要压缩；必须保留 SystemMessage；摘要比纯删除更保持上下文连贯；混合策略最佳——保留近期+摘要早期；LangGraph Checkpointer 自动管理。

---

## 八、梯度练习题

### 基础题

**题目 1**：六种消息类型分别是什么？它们的 type 值分别是什么？

<details>
<summary>参考答案</summary>

| 消息类型 | type 值 | 用途 |
|---------|---------|------|
| HumanMessage | "human" | 用户输入 |
| AIMessage | "ai" | AI 回复 |
| SystemMessage | "system" | 系统指令 |
| ToolMessage | "tool" | 工具执行结果 |
| FunctionMessage | "function" | 函数调用结果（旧版） |
| ChatMessage | "chat" | 自定义角色消息 |
</details>

**题目 2**：用 InMemoryChatMessageHistory 创建一个对话，添加 3 轮对话（user+ai），然后打印所有消息。

<details>
<summary>参考答案</summary>

```python
from langchain_core.chat_history import InMemoryChatMessageHistory

history = InMemoryChatMessageHistory()
history.add_user_message("你好")
history.add_ai_message("你好！")
history.add_user_message("讲个笑话")
history.add_ai_message("为什么程序员喜欢黑暗模式？因为光会吸引虫子。")
history.add_user_message("哈哈")
history.add_ai_message("很高兴你喜欢！")

for msg in history.messages:
    print(f"{msg.type}: {msg.content}")
```
</details>

**题目 3**：MessageChunk 是什么？它和 BaseMessage 有什么区别？

<details>
<summary>参考答案</summary>

MessageChunk 是消息的流式版本。区别：
1. **用途**：BaseMessage 是完整消息，MessageChunk 是流式片段
2. **拼接**：MessageChunk 支持 `+` 运算符拼接成完整消息
3. **内容**：Chunk 的 content 通常是完整消息的一部分（一个词或一个句子）
4. **使用场景**：ChatModel.stream() 返回 chunk 流，逐个拼接得到完整回复
</details>

### 进阶题

**题目 4**：构建一个带持久化的对话系统，使用 FileChatMessageHistory，支持跨会话恢复。

<details>
<summary>参考实现思路</summary>

```python
from langchain_community.chat_message_histories import FileChatMessageHistory

class PersistentChat:
    def __init__(self, user_id: str):
        self.history = FileChatMessageHistory(file_path=f"chat_{user_id}.json")

    def chat(self, user_input: str) -> str:
        self.history.add_user_message(user_input)
        # 调用 LLM 生成回复
        reply = f"回复: {user_input}"
        self.history.add_ai_message(reply)
        return reply

# 第一次对话
chat1 = PersistentChat("user123")
chat1.chat("你好")

# 新会话恢复历史
chat2 = PersistentChat("user123")
print(f"恢复了 {len(chat2.history.messages)} 条历史")
```
</details>

**题目 5**：为什么 ToolMessage 必须有 tool_call_id？如果没有会发生什么？

<details>
<summary>参考答案</summary>

**原因**：tool_call_id 用来关联 AI 的工具调用请求和工具的执行结果。模型需要知道"哪个工具的结果"对应"哪个调用请求"。

**没有 tool_call_id 的后果**：
1. 模型无法正确匹配工具结果和调用请求
2. 模型可能把结果对应到错误的调用
3. 对话历史混乱，模型输出不可预测

**正确做法**：ToolMessage 的 tool_call_id 必须与之前 AIMessage 中 tool_calls 的 id 完全一致。
</details>

### 实战题

**题目 6**：设计一个生产级对话系统，要求：
1. 使用 Redis 存储对话历史
2. 超过 20 条消息自动修剪
3. 系统消息永远保留
4. 支持流式输出

<details>
<summary>参考实现思路</summary>

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import trim_messages

class ProductionChat:
    def __init__(self, session_id: str):
        self.session_id = session_id
        # 生产环境用 RedisChatMessageHistory
        self.history = InMemoryChatMessageHistory()
        self.system_msg = "你是一个助手"

    def chat(self, user_input: str) -> str:
        self.history.add_user_message(user_input)

        # 修剪历史
        trimmed = trim_messages(
            self.history.messages,
            max_count=20,
            include_system=True
        )

        # 调用 LLM（实际用 model.invoke(trimmed)）
        reply = f"回复: {user_input}"
        self.history.add_ai_message(reply)
        return reply
```
</details>

---

> 💡 **深度讲解**：消息体系是 LangChain 对话能力的核心。从单条消息的结构（content/type/metadata）到消息列表的管理（ChatMessageHistory），再到流式消息的拼接（MessageChunk），最后到上下文窗口的管理（修剪/摘要），构成了完整的对话管理栈。理解这套体系，你就能构建从简单聊天到复杂 Agent 的各种对话应用。
>
> **📝 精简总结**：六种消息类型各司其职；MessageChunk 支持流式拼接；ChatMessageHistory 管理对话历史；五种存储后端适配不同场景；修剪和摘要管理上下文窗口；ToolMessage 通过 tool_call_id 关联工具调用。

---

## 涔濄€佹秷鎭睘鎬ф繁鍏ヨВ鏋?
### 9.1 content 灞炴€х殑澶氭€佹€?
**姒傚康瑙ｉ噴**锛歝ontent 鏄秷鎭渶閲嶈鐨勫睘鎬э紝浣嗗畠涓嶆€绘槸瀛楃涓测€斺€斿畠鍙互鏄瓧绗︿覆锛屼篃鍙互鏄竴涓寘鍚绉嶆ā鎬侊紙鏂囨湰+鍥剧墖+闊抽锛夌殑鍒楄〃銆傚氨鍍忎竴灏佷俊鈥斺€旀湁鏃跺彧鏈変俊绾革紝鏈夋椂淇＄焊涓婅繕璐寸潃鐓х墖銆?
**鍘熺悊璇存槑**锛氬綋妯″瀷鏀寔澶氭ā鎬佽緭鍏ユ椂锛堝 GPT-4o銆丆laude 3锛夛紝content 鍙互鏄粨鏋勫寲鍒楄〃锛屾瘡涓厓绱犳弿杩颁竴绉嶆ā鎬佺殑鍐呭銆侺angChain 鐨?BaseMessage 鐢?`Union[str, list[dict]]` 绫诲瀷鏉ユ敮鎸佽繖绉嶅鎬併€?
**鍩虹绀轰緥锛氱函鏂囨湰 content**

```python
# 绀轰緥 9.1.1锛氱函鏂囨湰娑堟伅
from langchain_core.messages import HumanMessage

# 鏈€绠€鍗曠殑绾枃鏈?msg = HumanMessage(content="浣犲ソ")
print(type(msg.content))  # <class 'str'>
print(msg.content)         # 浣犲ソ
```

**杩涢樁绀轰緥锛氬妯℃€?content**

```python
# 绀轰緥 9.1.2锛氭枃鏈?鍥剧墖鐨勫妯℃€佹秷鎭?from langchain_core.messages import HumanMessage

# 澶氭ā鎬侊細鏂囨湰 + 鍥剧墖 URL
msg = HumanMessage(content=[
    {"type": "text", "text": "鎻忚堪杩欏紶鍥剧墖"},
    {"type": "image_url", "image_url": {
        "url": "https://example.com/image.jpg",
        "detail": "low"
    }}
])

print(f"content 绫诲瀷: {type(msg.content)}")  # list
print(f"鍖呭惈 {len(msg.content)} 涓儴鍒?)
for i, part in enumerate(msg.content):
    print(f"  閮ㄥ垎{i}: 绫诲瀷={part['type']}")
```

**瀹屾暣鍦烘櫙锛氬妯℃€佹秷鎭殑瀹為檯搴旂敤**

```python
# 绀轰緥 9.1.3锛氬浘鐗囩悊瑙ｄ换鍔?from langchain_core.messages import HumanMessage

def create_image_question(image_url: str, question: str) -> HumanMessage:
    """鏋勫缓鍥剧墖鐞嗚В闂"""
    return HumanMessage(content=[
        {"type": "text", "text": question},
        {"type": "image_url", "image_url": {"url": image_url}}
    ])

# 浣跨敤
question = create_image_question(
    "https://example.com/cat.jpg",
    "杩欏紶鍥剧墖閲屾湁浠€涔堝姩鐗╋紵瀹冨湪鍋氫粈涔堬紵"
)

# 浼犵粰澶氭ā鎬佹ā鍨?# model = ChatOpenAI(model="gpt-4o")
# response = model.invoke([question])
# print(response.content)
```

### 9.2 additional_kwargs 璇﹁В

**姒傚康瑙ｉ噴**锛歛dditional_kwargs 鏄秷鎭殑"鎵╁睍瀛楁"鈥斺€旀爣鍑嗗睘鎬э紙content/type锛夎涓嶄笅鐨勪俊鎭兘鏀捐繖閲屻€傛渶甯歌鐨勭敤閫旀槸瀛樻斁宸ュ叿璋冪敤淇℃伅銆?
**绀轰緥锛氬伐鍏疯皟鐢ㄧ殑瀹屾暣缁撴瀯**

```python
# 绀轰緥 9.2.1锛歛dditional_kwargs 涓殑宸ュ叿璋冪敤
from langchain_core.messages import AIMessage

ai_msg = AIMessage(
    content="",
    additional_kwargs={
        "tool_calls": [
            {
                "id": "call_abc123",
                "type": "function",
                "function": {
                    "name": "search_web",
                    "arguments": '{"query": "LangChain 鏁欑▼"}'
                }
            },
            {
                "id": "call_def456",
                "type": "function",
                "function": {
                    "name": "get_time",
                    "arguments": '{"timezone": "Asia/Shanghai"}'
                }
            }
        ]
    }
)

# 瑙ｆ瀽宸ュ叿璋冪敤
for tc in ai_msg.additional_kwargs.get("tool_calls", []):
    func_name = tc["function"]["name"]
    args = tc["function"]["arguments"]
    print(f"璋冪敤宸ュ叿: {func_name}, 鍙傛暟: {args}")
```

### 9.3 response_metadata 璇﹁В

**姒傚康瑙ｉ噴**锛歳esponse_metadata 鏄ā鍨嬭繑鍥炵殑鍏冧俊鎭€斺€旇褰曚簡杩欐鐢熸垚鐨?妗ｆ"锛氫负浠€涔堝仠姝紙finish_reason锛夈€佺敤浜嗗灏?token锛坲sage锛夈€佸摢涓ā鍨嬬敓鎴愮殑锛坢odel_name锛夈€?
**绀轰緥**锛?
```python
# 绀轰緥 9.3.1锛歳esponse_metadata 鐨勫畬鏁寸粨鏋?from langchain_core.messages import AIMessage

ai_msg = AIMessage(
    content="杩欐槸 AI 鐨勫洖绛斿唴瀹?,
    response_metadata={
        "finish_reason": "stop",        # 鍋滄鍘熷洜锛歴top/length/function_call
        "model_name": "gpt-4",          # 浣跨敤鐨勬ā鍨?        "system_fingerprint": "fp_123",  # 绯荤粺鎸囩汗
        "token_usage": {                 # Token 鐢ㄩ噺
            "prompt_tokens": 45,
            "completion_tokens": 30,
            "total_tokens": 75
        }
    }
)

# 鎻愬彇鍏抽敭淇℃伅
meta = ai_msg.response_metadata
print(f"妯″瀷: {meta['model_name']}")
print(f"鍋滄鍘熷洜: {meta['finish_reason']}")
print(f"Token 鐢ㄩ噺: {meta['token_usage']['total_tokens']}")
print(f"杈撳叆 token: {meta['token_usage']['prompt_tokens']}")
print(f"杈撳嚭 token: {meta['token_usage']['completion_tokens']}")
```

### 9.4 id 灞炴€р€斺€旀秷鎭敮涓€鏍囪瘑

**姒傚康瑙ｉ噴**锛氭瘡鏉℃秷鎭彲浠ユ湁涓€涓敮涓€ ID锛岀敤浜庤拷韪拰寮曠敤銆傚湪 LangSmith 杩借釜鍜屽杞璇濈鐞嗕腑寰堟湁鐢ㄣ€?
**绀轰緥**锛?
```python
# 绀轰緥 9.4.1锛氭秷鎭?ID 鐨勪娇鐢?from langchain_core.messages import HumanMessage

# 鍒涘缓鏃舵寚瀹?ID
msg = HumanMessage(content="浣犲ソ", id="msg_001")
print(f"娑堟伅 ID: {msg.id}")

# 瀹為檯浣跨敤涓紝妯″瀷杩斿洖鐨勬秷鎭細鑷姩甯?ID
# from langchain_openai import ChatOpenAI
# model = ChatOpenAI()
# response = model.invoke("浣犲ソ")
# print(response.id)  # 鑷姩鐢熸垚鐨勬秷鎭?ID
```

> 馃挕 **娣卞害璁茶В**锛氭秷鎭殑鍥涗釜鏍稿績灞炴€у悇鏈夊垎宸モ€斺€攃ontent 鏄?璇翠粈涔?锛宼ype 鏄?璋佽鐨?锛宎dditional_kwargs 鏄?闄勫姞淇℃伅"锛宺esponse_metadata 鏄?妯″瀷鐢熸垚鏃剁殑鍏冩暟鎹?銆傜悊瑙ｈ繖涓垎灞傦紝浣犲氨鑳芥纭鐞嗗悇绉嶆秷鎭満鏅€傜壒鍒槸 response_metadata 涓殑 token_usage鈥斺€旇繖鏄垚鏈绠楀拰闄愭祦鐨勫叧閿暟鎹€?>
> **馃摑 绮剧畝鎬荤粨**锛歝ontent 鏀寔绾枃鏈拰澶氭ā鎬佸垪琛紱additional_kwargs 瀛樺伐鍏疯皟鐢ㄧ瓑鎵╁睍淇℃伅锛況esponse_metadata 瀛?finish_reason/token_usage锛沬d 鏄秷鎭敮涓€鏍囪瘑锛涘洓涓睘鎬у悇鍙稿叾鑱屻€?
---

## 鍗併€佹秷鎭潡锛圡essageChunk锛夋繁搴﹁В鏋?
### 10.1 MessageChunk 鐨勮璁″師鐞?
**姒傚康瑙ｉ噴**锛歁essageChunk 灏卞儚娴佸紡浼犺緭涓殑鏁版嵁鍖呪€斺€斿畬鏁寸殑娑堟伅琚媶鎴愪竴灏忓潡涓€灏忓潡锛岄€愬潡鍙戦€併€傛瘡涓?chunk 閮芥槸涓€涓畬鏁寸殑 Message 瀵硅薄锛屽彧鏄唴瀹逛笉瀹屾暣銆傚涓?chunk 鎷艰捣鏉ュ氨鏄畬鏁存秷鎭€?
**鍘熺悊璇存槑**锛歁essageChunk 缁ф壙鑷?BaseMessage锛岄噸鍐欎簡 `__add__` 鏂规硶銆傚綋浣犲仛 `chunk1 + chunk2` 鏃讹紝LangChain 浼氾細鈶?content 瀛楃涓叉嫾鎺?鈶?additional_kwargs 瀛楀吀鍚堝苟 鈶?response_metadata 鏇存柊銆傝繖绉嶈璁¤娴佸紡鎷兼帴鍙樺緱閫忔槑鈥斺€斾綘涓嶉渶瑕佸叧蹇冩€庝箞鎷硷紝鐩存帴鐢?+ 灏辫銆?
### 10.2 鍚勭娑堟伅绫诲瀷鐨?Chunk

**鍩虹绀轰緥锛欰IMessageChunk**

```python
# 绀轰緥 10.2.1锛欰IMessageChunk 鐨勬嫾鎺?from langchain_core.messages import AIMessageChunk

# 妯℃嫙娴佸紡鐢熸垚
chunks = [
    AIMessageChunk(content="浣?),
    AIMessageChunk(content="濂?),
    AIMessageChunk(content="锛?),
    AIMessageChunk(content="鎴戞槸"),
    AIMessageChunk(content="AI鍔╂墜"),
]

# 閫愪釜鎷兼帴
full = chunks[0]
for chunk in chunks[1:]:
    full += chunk

print(f"瀹屾暣鍐呭: {full.content}")  # 浣犲ソ锛屾垜鏄疉I鍔╂墜
```

**杩涢樁绀轰緥锛氬甫鍏冩暟鎹殑 chunk 鎷兼帴**

```python
# 绀轰緥 10.2.2锛歝hunk 鎷兼帴鏃跺厓鏁版嵁鐨勫悎骞?from langchain_core.messages import AIMessageChunk

# 绗竴涓?chunk 甯﹀厓鏁版嵁
chunk1 = AIMessageChunk(
    content="浣?,
    response_metadata={"model_name": "gpt-4"}
)

# 鍚庣画 chunk
chunk2 = AIMessageChunk(content="濂?)
chunk3 = AIMessageChunk(
    content="锛?,
    response_metadata={"finish_reason": "stop"}
)

# 鎷兼帴鈥斺€斿厓鏁版嵁浼氬悎骞?full = chunk1 + chunk2 + chunk3
print(f"鍐呭: {full.content}")
print(f"妯″瀷: {full.response_metadata.get('model_name')}")
print(f"鍋滄鍘熷洜: {full.response_metadata.get('finish_reason')}")
```

### 10.3 娴佸紡杈撳嚭鐨勫疄闄呮秷璐?
**绀轰緥锛氬畬鏁寸殑娴佸紡娑堣垂娴佺▼**

```python
# 绀轰緥 10.3.1锛氬畬鏁寸殑娴佸紡娑堟伅娑堣垂
from langchain_core.messages import AIMessageChunk

def stream_chat(prompt: str):
    """妯℃嫙娴佸紡鑱婂ぉ"""
    responses = [
        "鏍规嵁", "鎮ㄧ殑", "闂", "锛?, "鎴?, "璁や负",
        "LangChain", "鐨?, "Runnable", "璁捐", "闈炲父", "浼橀泤", "銆?
    ]
    for resp in responses:
        yield AIMessageChunk(content=resp)

# 娑堣垂娴佸紡杈撳嚭
print("AI: ", end="")
full_message = None

for chunk in stream_chat("LangChain 鐨勮璁″ソ鍚楋紵"):
    print(chunk.content, end="", flush=True)

    # 绱Н瀹屾暣娑堟伅
    if full_message is None:
        full_message = chunk
    else:
        full_message += chunk

print(f"\n\n瀹屾暣娑堟伅绫诲瀷: {type(full_message).__name__}")
print(f"瀹屾暣鍐呭: {full_message.content}")
```

### 10.4 甯歌鍧戠偣

**鍧戠偣 1锛歝hunk 绱Н鏃剁殑鍒濆鍊奸棶棰?*

閿欒鐜拌薄锛歚TypeError: unsupported operand type(s) for +: 'NoneType' and 'AIMessageChunk'`

鍘熷洜锛氱敤 None 浣滀负鍒濆鍊煎紑濮嬬疮鍔犮€?
姝ｇ‘鍋氭硶锛?
```python
# 绀轰緥 10.4.1锛氭纭疮绉?chunk
from langchain_core.messages import AIMessageChunk

# 鉁?姝ｇ‘锛氱涓€涓?chunk 浣滀负鍒濆鍊?full_message = None
for chunk in stream_generator():
    if full_message is None:
        full_message = chunk
    else:
        full_message += chunk

# 鉂?閿欒锛氱敤 None 寮€濮?# full_message = None
# for chunk in stream_generator():
#     full_message += chunk  # None + chunk 鎶ラ敊
```

**鍧戠偣 2锛氬繕璁板鐞嗙┖ chunk**

閿欒鐜拌薄锛氭煇浜?chunk 鐨?content 鏄┖瀛楃涓诧紝瀵艰嚧杈撳嚭澶氫簡绌烘牸鎴栨崲琛屻€?
鍘熷洜锛氭煇浜涙ā鍨嬪湪娴佸紡杈撳嚭涓細鍙戦€佺┖ chunk銆?
姝ｇ‘鍋氭硶锛?
```python
# 绀轰緥 10.4.2锛氬鐞嗙┖ chunk
for chunk in stream_generator():
    if chunk.content:  # 鍙鐞嗛潪绌哄唴瀹?        print(chunk.content, end="", flush=True)
```

> 馃挕 **娣卞害璁茶В**锛歁essageChunk 鏄祦寮?AI 搴旂敤鐨勬牳蹇冦€傜悊瑙ｄ簡 chunk 鐨勬嫾鎺ユ満鍒讹紝浣犲氨鐞嗚В浜嗕负浠€涔?`prompt | model | parser` 鍙互鑷姩娴佸紡鈥斺€旀瘡涓€姝ラ兘鎺ユ敹涓婃父鐨?chunk锛屽鐞嗗悗杈撳嚭鑷繁鐨?chunk銆傚湪 Web 搴旂敤涓紝娴佸紡杈撳嚭閫氬父閫氳繃 SSE锛圫erver-Sent Events锛夋垨 WebSocket 鎺ㄩ€佸埌鍓嶇銆?>
> **馃摑 绮剧畝鎬荤粨**锛歁essageChunk 鏄秷鎭殑娴佸紡鐗囨锛涚敤 + 鎷兼帴鎴愬畬鏁存秷鎭紱content 鎷兼帴銆佸厓鏁版嵁鍚堝苟锛涚涓€涓?chunk 浣滀负鍒濆鍊硷紱璺宠繃绌?chunk锛涙槸娴佸紡杈撳嚭鐨勬牳蹇冩暟鎹粨鏋勩€?
---

## 鍗佷竴銆丆hatMessageHistory 娣卞害瀵规瘮

### 11.1 InMemoryChatMessageHistory 璇﹁В

**姒傚康瑙ｉ噴**锛氭渶绠€鍗曠殑瀵硅瘽鍘嗗彶鈥斺€斿氨鏄竴涓?Python 鍒楄〃瀛樺湪鍐呭瓨閲屻€備紭鐐规槸蹇紝缂虹偣鏄噸鍚氨娌′簡銆?
**鍩虹鐢ㄦ硶**锛?
```python
# 绀轰緥 11.1.1锛欼nMemoryChatMessageHistory 瀹屾暣 API
from langchain_core.chat_history import InMemoryChatMessageHistory

# 鍒濆鍖?history = InMemoryChatMessageHistory()

# 鏂规硶1锛氭坊鍔犳秷鎭璞?from langchain_core.messages import HumanMessage, AIMessage
history.add_message(HumanMessage(content="浣犲ソ"))

# 鏂规硶2锛氬揩鎹锋柟娉?history.add_user_message("璁蹭釜绗戣瘽")
history.add_ai_message("涓轰粈涔堢▼搴忓憳鍠滄榛戞殫妯″紡锛?)

# 鏌ョ湅娑堟伅
print(f"娑堟伅鏁? {len(history.messages)}")
for msg in history.messages:
    print(f"  [{msg.type}] {msg.content}")

# 娓呯┖
history.clear()
print(f"娓呯┖鍚? {len(history.messages)} 鏉?)
```

### 11.2 FileChatMessageHistory 璇﹁В

**姒傚康瑙ｉ噴**锛氭妸瀵硅瘽鍘嗗彶瀛樺埌 JSON 鏂囦欢銆傛瘡涓細璇濅竴涓枃浠躲€傝繘绋嬮噸鍚悗瀵硅瘽涓嶄涪澶便€?
**鍩虹鐢ㄦ硶**锛?
```python
# 绀轰緥 11.2.1锛欶ileChatMessageHistory 浣跨敤
from langchain_community.chat_message_histories import FileChatMessageHistory

# 鍒涘缓鈥斺€旀寚瀹氭枃浠惰矾寰?history = FileChatMessageHistory(file_path="user_123_history.json")

# 娣诲姞娑堟伅
history.add_user_message("浣犲ソ")
history.add_ai_message("浣犲ソ锛?)

# 鏌ョ湅
for msg in history.messages:
    print(f"{msg.type}: {msg.content}")

# 鏂板疄渚嬪姞杞藉悓涓€鏂囦欢鈥斺€旀仮澶嶅巻鍙?history2 = FileChatMessageHistory(file_path="user_123_history.json")
print(f"鎭㈠浜?{len(history2.messages)} 鏉℃秷鎭?)
```

**瀹屾暣鍦烘櫙锛氬鐢ㄦ埛瀵硅瘽绠＄悊**

```python
# 绀轰緥 11.2.2锛氬鐢ㄦ埛瀵硅瘽绠＄悊
from langchain_community.chat_message_histories import FileChatMessageHistory
import os

class MultiUserChat:
    """澶氱敤鎴峰璇濈鐞嗗櫒"""
    def __init__(self, data_dir: str = "chat_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def get_history(self, user_id: str) -> FileChatMessageHistory:
        """鑾峰彇鐢ㄦ埛鐨勫璇濆巻鍙?""
        file_path = os.path.join(self.data_dir, f"{user_id}.json")
        return FileChatMessageHistory(file_path=file_path)

    def chat(self, user_id: str, message: str) -> str:
        history = self.get_history(user_id)
        history.add_user_message(message)
        reply = f"鏀跺埌: {message}"  # 瀹為檯璋冪敤 LLM
        history.add_ai_message(reply)
        return reply

# 浣跨敤
chat_system = MultiUserChat()
chat_system.chat("user001", "浣犲ソ")
chat_system.chat("user002", "Hi")

# 鏌ョ湅 user001 鐨勫巻鍙?h = chat_system.get_history("user001")
print(f"user001 鏈?{len(h.messages)} 鏉℃秷鎭?)
```

### 11.3 RedisChatMessageHistory 璇﹁В

**姒傚康瑙ｉ噴**锛氬璇濆巻鍙插瓨鍒?Redis銆傞珮鎬ц兘銆佹敮鎸?TTL锛堣嚜鍔ㄨ繃鏈燂級銆佸瀹炰緥鍏变韩銆傜敓浜х幆澧冮閫夈€?
**鍩虹鐢ㄦ硶**锛?
```python
# 绀轰緥 11.3.1锛歊edisChatMessageHistory 閰嶇疆
# from langchain_community.chat_message_histories import RedisChatMessageHistory

# # 鍩烘湰閰嶇疆
# history = RedisChatMessageHistory(
#     session_id="user_123",           # 浼氳瘽 ID
#     url="redis://localhost:6379/0",  # Redis 鍦板潃
#     ttl=86400                        # 24灏忔椂杩囨湡锛堢锛?# )
#
# history.add_user_message("浣犲ソ")
# history.add_ai_message("浣犲ソ锛?)
#
# for msg in history.messages:
#     print(f"{msg.type}: {msg.content}")
```

**鐢熶骇閰嶇疆瑕佺偣**锛?
```yaml
# 绀轰緥 11.3.2锛歊edis 鐢熶骇閰嶇疆绀轰緥
# redis:
#   host: redis.production.internal
#   port: 6379
#   password: ${REDIS_PASSWORD}
#   db: 0
#   ttl: 86400  # 24灏忔椂
#   key_prefix: "chat:history:"  # 閿墠缂€
```

### 11.4 SQLChatMessageHistory 璇﹁В

**姒傚康瑙ｉ噴**锛氬璇濆巻鍙插瓨鍒板叧绯诲瀷鏁版嵁搴撱€傛敮鎸佸鏉傛煡璇€佷簨鍔°€侀暱鏈熷瓨鍌ㄣ€傞€傚悎浼佷笟绾у悎瑙勯渶姹傘€?
**鍩虹鐢ㄦ硶**锛?
```python
# 绀轰緥 11.4.1锛歋QLChatMessageHistory 浣跨敤
# from langchain_community.chat_message_histories import SQLChatMessageHistory
#
# # SQLite锛堝紑鍙戠敤锛?# history = SQLChatMessageHistory(
#     session_id="user_123",
#     connection_string="sqlite:///chat_history.db"
# )
#
# # PostgreSQL锛堢敓浜х敤锛?# # history = SQLChatMessageHistory(
# #     session_id="user_123",
# #     connection_string="postgresql://user:pass@localhost/db"
# # )
#
# history.add_user_message("浣犲ソ")
# history.add_ai_message("浣犲ソ锛?)
```

### 11.5 浜旂瀛樺偍鍚庣瀵规瘮

| 鐗规€?| InMemory | File | Redis | SQL | MongoDB |
|------|----------|------|-------|-----|---------|
| **鎸佷箙鍖?* | 鉂?| 鉁?| 鉁?| 鉁?| 鉁?|
| **鎬ц兘** | 鈿?鏈€蹇?| 蹇?| 鈿?寰堝揩 | 涓瓑 | 蹇?|
| **鍒嗗竷寮?* | 鉂?| 鉂?| 鉁?| 鉁?| 鉁?|
| **杩囨湡绛栫暐** | 鉂?| 鉂?| 鉁?TTL | 鉂?| 鉁?TTL |
| **鏌ヨ鑳藉姏** | 鍒楄〃鎿嶄綔 | 鏂囦欢璇诲彇 | KEYS 鎵弿 | SQL 鏌ヨ | MongoDB 鏌ヨ |
| **閫傜敤瑙勬ā** | 寮€鍙?| 灏忛」鐩?| 鐢熶骇 | 浼佷笟绾?| 鏂囨。鍨?|
| **杩愮淮鎴愭湰** | 闆?| 浣?| 涓?| 涓珮 | 涓?|

> 馃挕 **娣卞害璁茶В**锛氬瓨鍌ㄥ悗绔殑閫夋嫨鏄竴涓潈琛♀€斺€旀€ц兘銆佹寔涔呭寲銆佹垚鏈€佽繍缁村鏉傚害銆傛帹鑽愮殑婕旇繘璺緞锛氬紑鍙戠敤 InMemory 鈫?鍗曟満鐢?File 鈫?鐢熶骇鐢?Redis 鈫?浼佷笟鍚堣鐢?SQL銆傚湪 LangGraph 涓紝瀵硅瘽鐘舵€佺鐞嗗凡缁忎粠 ChatMessageHistory 婕旇繘鍒?Checkpointer 鏈哄埗鈥斺€旀敮鎸佹洿澶嶆潅鐨勭姸鎬佹寔涔呭寲鍜屾椂闂存梾琛屻€?>
> **馃摑 绮剧畝鎬荤粨**锛氫簲绉嶅瓨鍌ㄥ悗绔悇鏈変紭鍔ｏ紱InMemory 閫傚悎寮€鍙戯紱File 閫傚悎灏忛」鐩紱Redis 鏄敓浜ч閫夛紱SQL 閫傚悎浼佷笟绾э紱LangGraph 鐢?Checkpointer 鏇夸唬浜?ChatMessageHistory銆?
---

## 鍗佷簩銆佹秷鎭笌 Token 璁℃暟

### 12.1 涓轰粈涔堥渶瑕?Token 璁℃暟

**姒傚康瑙ｉ噴**锛歀LM 涓嶆槸鎸?瀛楁暟"璁¤垂锛岃€屾槸鎸?token 鏁?璁¤垂銆? 涓腑鏂囨眽瀛楀ぇ绾︽槸 1-2 涓?token锛? 涓嫳鏂囧崟璇嶅ぇ绾︽槸 1-3 涓?token銆備簡瑙?token 鏁版墠鑳斤細鈶?鎺у埗鎴愭湰 鈶?涓嶈秴鍑轰笂涓嬫枃绐楀彛 鈶?浼扮畻 API 璐圭敤銆?
**鍘熺悊璇存槑**锛歍oken 璁℃暟浣跨敤妯″瀷瀵瑰簲鐨勫垎璇嶅櫒锛坱okenizer锛夈€侽penAI 鐢?tiktoken锛孉nthropic 鐢ㄨ嚜宸辩殑鍒嗚瘝鍣ㄣ€備笉鍚屾ā鍨嬬殑 tokenizer 涓嶅悓锛岃鏁扮粨鏋滀篃涓嶅悓銆?
### 12.2 鍩虹 Token 璁℃暟

**鍩虹绀轰緥锛氱敤 tiktoken 璁℃暟**

```python
# 绀轰緥 12.2.1锛氱敤 tiktoken 璁＄畻 token 鏁?import tiktoken

# 鑾峰彇 GPT-4 鐨勫垎璇嶅櫒
encoding = tiktoken.encoding_for_model("gpt-4")

# 璁＄畻 token 鏁?text = "LangChain 鏄竴涓己澶х殑 LLM 搴旂敤寮€鍙戞鏋?
tokens = encoding.encode(text)
print(f"鏂囨湰: {text}")
print(f"Token 鏁? {len(tokens)}")
print(f"Token 璇︽儏: {[encoding.decode([t]) for t in tokens[:10]]}")
```

**杩涢樁绀轰緥锛氭秷鎭垪琛ㄧ殑 token 璁℃暟**

```python
# 绀轰緥 12.2.2锛氳绠楀璇濆巻鍙茬殑 token 鏁?import tiktoken
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

encoding = tiktoken.encoding_for_model("gpt-4")

def count_message_tokens(messages: list) -> int:
    """璁＄畻娑堟伅鍒楄〃鐨勬€?token 鏁?""
    total = 0
    for msg in messages:
        # 姣忔潯娑堟伅澶х害鏈?4 涓?token 鐨勬牸寮忓紑閿€
        total += 4
        if isinstance(msg.content, str):
            total += len(encoding.encode(msg.content))
        elif isinstance(msg.content, list):
            for part in msg.content:
                if isinstance(part, dict) and "text" in part:
                    total += len(encoding.encode(part["text"]))
    total += 2  # 缁撴潫鏍囪
    return total

# 鏋勫缓瀵硅瘽
messages = [
    SystemMessage(content="浣犳槸涓€涓姪鎵?),
    HumanMessage(content="浣犲ソ"),
    AIMessage(content="浣犲ソ锛?),
]

total_tokens = count_message_tokens(messages)
print(f"鎬?token 鏁? {total_tokens}")
print(f"浼扮畻鎴愭湰锛圙PT-4锛? ${total_tokens / 1000 * 0.03:.4f}")
```

### 12.3 涓婁笅鏂囩獥鍙ｇ鐞?
**绀轰緥锛氭牴鎹?token 鏁颁慨鍓秷鎭?*

```python
# 绀轰緥 12.3.1锛氭牴鎹?token 鏁拌嚜鍔ㄤ慨鍓?import tiktoken
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

encoding = tiktoken.encoding_for_model("gpt-4")

def trim_by_tokens(messages: list, max_tokens: int) -> list:
    """鏍规嵁 token 鏁颁慨鍓秷鎭?""
    system_msgs = [m for m in messages if m.type == "system"]
    other_msgs = [m for m in messages if m.type != "system"]

    # 浠庡悗寰€鍓嶄繚鐣欙紝鐩村埌杈惧埌 token 闄愬埗
    kept = []
    total = 0
    for msg in reversed(other_msgs):
        msg_tokens = len(encoding.encode(msg.content)) + 4
        if total + msg_tokens <= max_tokens:
            kept.insert(0, msg)
            total += msg_tokens
        else:
            break

    return system_msgs + kept

# 娴嬭瘯
messages = [
    SystemMessage(content="浣犳槸涓€涓姪鎵?),
    HumanMessage(content="闂1"),
    AIMessage(content="鍥炵瓟1"),
    HumanMessage(content="闂2"),
    AIMessage(content="鍥炵瓟2..."),
]

trimmed = trim_by_tokens(messages, max_tokens=100)
print(f"鍘?{len(messages)} 鏉?鈫?淇壀鍚?{len(trimmed)} 鏉?)
```

> 馃挕 **娣卞害璁茶В**锛歍oken 璁℃暟鏄垚鏈帶鍒跺拰涓婁笅鏂囩鐞嗙殑鍩虹銆傚湪鐢熶骇鐜涓紝寤鸿锛氣憼 瀹氭湡鐩戞帶 token 鐢ㄩ噺 鈶?璁剧疆 token 棰勭畻涓婇檺 鈶?瓒呴檺鏃惰嚜鍔ㄤ慨鍓?鈶?閫夋嫨鎬т环姣斿悎閫傜殑妯″瀷銆侺angSmith 浼氳嚜鍔ㄨ褰曟瘡娆¤皟鐢ㄧ殑 token 鐢ㄩ噺锛屾柟渚垮仛鎴愭湰鍒嗘瀽銆?>
> **馃摑 绮剧畝鎬荤粨**锛氱敤 tiktoken 璁＄畻 token 鏁帮紱姣忔潯娑堟伅鏈夋牸寮忓紑閿€锛堢害4 token锛夛紱鎸?token 鏁颁慨鍓秷鎭瘮鎸夋潯鏁版洿绮剧‘锛泃oken 鐢ㄩ噺鏄垚鏈帶鍒剁殑鍏抽敭锛涚敓浜х幆澧冪洃鎺?token 鐢ㄩ噺銆?
---

## 鍗佷笁銆佸父瑙侀棶棰?FAQ

### Q1: SystemMessage 搴旇鏀惧湪瀵硅瘽鐨勪粈涔堜綅缃紵

**绛?*锛氶€氬父鏀惧湪瀵硅瘽鍘嗗彶鐨?*绗竴鏉?*銆傚ぇ澶氭暟妯″瀷瑕佹眰 system message 鍦ㄦ渶鍓嶉潰銆備笉瑕佸湪瀵硅瘽涓棿鎻掑叆鎴栦慨鏀?system message鈥斺€斿彲鑳藉鑷存ā鍨嬭涓轰笉涓€鑷淬€?
### Q2: HumanMessage 鍜?ChatMessage 鏈変粈涔堝尯鍒紵

**绛?*锛欻umanMessage 鏄浐瀹氳鑹茬殑娑堟伅锛坱ype="human"锛夛紝ChatMessage 鏄€氱敤娑堟伅锛坮ole 鍙互鑷畾涔夛級銆傚ぇ澶氭暟鎯呭喌涓嬬敤 HumanMessage 灏卞浜嗭紝鍙湁瀵规帴鐗规畩妯″瀷鏃舵墠鐢?ChatMessage銆?
### Q3: ToolMessage 鐨?tool_call_id 蹇呴』绮剧‘鍖归厤鍚楋紵

**绛?*锛氭槸鐨勶紝蹇呴』瀹屽叏鍖归厤銆侫I 娑堟伅涓殑 tool_calls 鍒楄〃涓瘡涓皟鐢ㄦ湁涓€涓?id锛屽搴旂殑 ToolMessage 鐨?tool_call_id 蹇呴』鏄叾涓箣涓€銆備笉鍖归厤浼氬鑷存ā鍨嬫棤娉曟纭叧鑱斿伐鍏风粨鏋溿€?
### Q4: 娴佸紡杈撳嚭鏃跺浣曡幏鍙栧畬鏁寸殑 AI 娑堟伅锛?
**绛?*锛氶€愪釜鎷兼帴 chunk锛?```python
full = None
for chunk in model.stream(input):
    if full is None:
        full = chunk
    else:
        full += chunk
```

### Q5: FileChatMessageHistory 鍜?RedisChatMessageHistory 鎬庝箞閫夛紵

**绛?*锛欶ile 閫傚悎鍗曟満銆佸皬瑙勬ā銆佷綆骞跺彂鍦烘櫙锛汻edis 閫傚悎鐢熶骇銆侀珮骞跺彂銆侀渶瑕佽嚜鍔ㄨ繃鏈熺殑鍦烘櫙銆俁edis 杩樻敮鎸佸瀹炰緥鍏变韩锛岄€傚悎鍒嗗竷寮忛儴缃层€?
---

## 鍗佸洓銆佸叏鏂囨€荤粨

### 鐭ヨ瘑鍥捐氨

```mermaid
mindmap
  root((娑堟伅浣撶郴))
    娑堟伅绫诲瀷
      HumanMessage 鐢ㄦ埛杈撳叆
      AIMessage AI鍥炲
      SystemMessage 绯荤粺鎸囦护
      ToolMessage 宸ュ叿缁撴灉
      FunctionMessage 鏃х増鍑芥暟
      ChatMessage 鑷畾涔夎鑹?    娑堟伅灞炴€?      content 鍐呭
      additional_kwargs 鎵╁睍
      response_metadata 鍏冩暟鎹?      id 鍞竴鏍囪瘑
    娴佸紡澶勭悊
      MessageChunk 娑堟伅鍧?      + 鎷兼帴杩愮畻
      stream 娴佸紡杈撳嚭
    瀵硅瘽鍘嗗彶
      InMemory 鍐呭瓨瀛樺偍
      File 鏂囦欢瀛樺偍
      Redis 缂撳瓨瀛樺偍
      SQL 鏁版嵁搴撳瓨鍌?    涓婁笅鏂囩鐞?      娑堟伅淇壀
      鎽樿鍘嬬缉
      Token璁℃暟
```

### 鏍稿績瑕佺偣

| 涓婚 | 鏍稿績瑕佺偣 |
|------|---------|
| **娑堟伅绫诲瀷** | 鍏娑堟伅锛屽悇鍙稿叾鑱?|
| **娑堟伅灞炴€?* | content/type/metadata/kwargs |
| **娴佸紡娑堟伅** | MessageChunk + 鎷兼帴 |
| **瀵硅瘽鍘嗗彶** | 浜旂瀛樺偍鍚庣 |
| **涓婁笅鏂囩鐞?* | 淇壀+鎽樿+token璁℃暟 |

### 鏈€浣冲疄璺垫竻鍗?
- [ ] SystemMessage 鏀惧璇濈涓€鏉?- [ ] ToolMessage 鐨?tool_call_id 绮剧‘鍖归厤
- [ ] 娴佸紡杈撳嚭鐢?chunk 鎷兼帴
- [ ] 鐢熶骇鐜鐢?Redis 瀛樺偍瀵硅瘽鍘嗗彶
- [ ] 闀垮璇濊嚜鍔ㄤ慨鍓垨鎽樿
- [ ] 鐩戞帶 token 鐢ㄩ噺鎺у埗鎴愭湰
- [ ] 搴忓垪鍖栨椂淇濈暀 type 瀛楁
- [ ] 澶氭ā鎬佹秷鎭敤 list content


---

## 鍗佷簲銆佹秷鎭湪 Agent 绯荤粺涓殑瑙掕壊

### 15.1 Agent 寰幆涓殑娑堟伅娴?
**姒傚康瑙ｉ噴**锛欰gent 绯荤粺灏辨槸涓€涓?鎰熺煡-鎬濊€?琛屽姩"鐨勫惊鐜€斺€旂敤鎴疯涓€鍙ヨ瘽锛圚umanMessage锛夛紝AI 鍐冲畾鍋氫粈涔堬紙AIMessage + 宸ュ叿璋冪敤锛夛紝宸ュ叿鎵ц骞惰繑鍥炵粨鏋滐紙ToolMessage锛夛紝AI 鏍规嵁缁撴灉缁х画鎬濊€冿紙AIMessage锛夛紝鐩村埌寰楀嚭鏈€缁堢瓟妗堛€?
**鍘熺悊璇存槑**锛欰gent 鐨勬牳蹇冨惊鐜氨鏄秷鎭垪琛ㄧ殑涓嶆柇澧為暱鈥斺€旀瘡涓€杞惊鐜兘寰€娑堟伅鍒楄〃閲屾坊鍔犳柊娑堟伅銆傝繖涓秷鎭垪琛ㄥ氨鏄?Agent 鐨?宸ヤ綔璁板繂"锛岃褰曚簡鏁翠釜鎺ㄧ悊杩囩▼銆?
**瀹屾暣绀轰緥锛歊eAct 寰幆**

```python
# 绀轰緥 15.1.1锛歊eAct Agent 鐨勬秷鎭祦
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# 鍒濆锛氱敤鎴锋彁闂?messages = [
    HumanMessage(content="鍖椾含浠婂ぉ澶╂皵鎬庝箞鏍凤紵闇€瑕佸甫浼炲悧锛?)
]

# 绗竴杞細AI 鎬濊€冣€斺€旈渶瑕佹煡璇㈠ぉ姘?ai_thought_1 = AIMessage(
    content="鎴戦渶瑕佸厛鏌ヨ鍖椾含鐨勫ぉ姘斻€?,
    additional_kwargs={
        "tool_calls": [{
            "id": "call_weather_1",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"city": "鍖椾含"}'
            }
        }]
    }
)
messages.append(ai_thought_1)

# 宸ュ叿鎵ц锛氳繑鍥炲ぉ姘?tool_result = ToolMessage(
    content="鍖椾含浠婂ぉ澶氫簯杞櫞锛岄檷姘存鐜?0%锛屾皵娓?2-28搴?,
    tool_call_id="call_weather_1",
    name="get_weather"
)
messages.append(tool_result)

# 绗簩杞細AI 鎬荤粨鍥炵瓟
ai_final = AIMessage(
    content="鏍规嵁鏌ヨ缁撴灉锛屽寳浜粖澶╁浜戣浆鏅达紝闄嶆按姒傜巼寰堜綆锛?0%锛夛紝姘旀俯鑸掗€傘€備笉闇€瑕佸甫浼烇紝閫傚悎澶栧嚭锛?
)
messages.append(ai_final)

# 鎵撳嵃瀹屾暣鐨?Agent 鎺ㄧ悊杩囩▼
print("=== Agent 鎺ㄧ悊杩囩▼ ===")
for i, msg in enumerate(messages):
    if msg.type == "human":
        print(f"\n[鐢ㄦ埛] {msg.content}")
    elif msg.type == "ai":
        if msg.additional_kwargs.get("tool_calls"):
            tc = msg.additional_kwargs["tool_calls"][0]
            print(f"[AI鎬濊€僝 璋冪敤宸ュ叿: {tc['function']['name']}({tc['function']['arguments']})")
        else:
            print(f"[AI鍥炵瓟] {msg.content}")
    elif msg.type == "tool":
        print(f"[宸ュ叿缁撴灉] {msg.content}")
```

### 15.2 澶氬伐鍏疯皟鐢ㄧ殑娑堟伅绠＄悊

**姒傚康瑙ｉ噴**锛欰gent 鍙兘鍦ㄤ竴杞腑璋冪敤澶氫釜宸ュ叿鈥斺€旇繖鏃跺€?AIMessage 鐨?tool_calls 鍒楄〃鏈夊涓皟鐢紝姣忎釜璋冪敤瀵瑰簲涓€涓?ToolMessage銆?
**绀轰緥**锛?
```python
# 绀轰緥 15.2.1锛氬宸ュ叿璋冪敤鐨勬秷鎭鐞?from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# 鐢ㄦ埛闂
messages = [HumanMessage(content="鍖椾含鍜屼笂娴蜂粖澶╁ぉ姘旀€庝箞鏍凤紵")]

# AI 鍚屾椂璋冪敤涓や釜宸ュ叿
ai_call = AIMessage(
    content="",
    additional_kwargs={
        "tool_calls": [
            {
                "id": "call_bj",
                "type": "function",
                "function": {"name": "get_weather", "arguments": '{"city": "鍖椾含"}'}
            },
            {
                "id": "call_sh",
                "type": "function",
                "function": {"name": "get_weather", "arguments": '{"city": "涓婃捣"}'}
            }
        ]
    }
)
messages.append(ai_call)

# 涓や釜宸ュ叿鍒嗗埆杩斿洖缁撴灉
bj_result = ToolMessage(
    content="鍖椾含锛氭櫞锛?5搴?,
    tool_call_id="call_bj",
    name="get_weather"
)
sh_result = ToolMessage(
    content="涓婃捣锛氬浜戯紝28搴?,
    tool_call_id="call_sh",
    name="get_weather"
)
messages.extend([bj_result, sh_result])

# AI 缁煎悎涓や釜缁撴灉
ai_answer = AIMessage(content="鍖椾含鏅村ぉ25搴︼紝涓婃捣澶氫簯28搴︺€傚寳浜洿鍑夌埥涓€浜涖€?)
messages.append(ai_answer)

print(f"鍏?{len(messages)} 鏉℃秷鎭?)
for msg in messages:
    print(f"  {msg.type}: {msg.content[:50] if msg.content else '(宸ュ叿璋冪敤)'}")
```

### 15.3 Agent 涓殑娑堟伅淇壀绛栫暐

**姒傚康瑙ｉ噴**锛欰gent 鐨勬秷鎭垪琛ㄤ細瓒婃潵瓒婇暱锛堟瘡杞兘鍔犲ソ鍑犳潯娑堟伅锛夛紝寰堝揩灏变細瓒呭嚭涓婁笅鏂囩獥鍙ｃ€傞渶瑕佺壒娈婄殑淇壀绛栫暐鈥斺€斾笉鑳介殢渚垮垹锛屽洜涓?Agent 鐨勬帹鐞嗛摼寰堥噸瑕併€?
**绀轰緥**锛?
```python
# 绀轰緥 15.3.1锛欰gent 娑堟伅鐨勬櫤鑳戒慨鍓?from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

def trim_agent_messages(messages: list, max_rounds: int = 10) -> list:
    """淇壀 Agent 娑堟伅鈥斺€斾繚鐣欑郴缁熸秷鎭拰鏈€杩?N 杞?""
    system_msgs = [m for m in messages if m.type == "system"]
    other_msgs = [m for m in messages if m.type != "system"]

    # 姣忚疆瀵硅瘽 = HumanMessage + (AIMessage + ToolMessage)*N
    # 浠庡悗寰€鍓嶆暟 N 杞?    kept = []
    human_count = 0
    for msg in reversed(other_msgs):
        if msg.type == "human":
            human_count += 1
            if human_count > max_rounds:
                break
        kept.insert(0, msg)

    return system_msgs + kept

# 妯℃嫙闀垮璇?messages = [SystemMessage(content="浣犳槸涓€涓姪鎵?)]
for i in range(20):
    messages.append(HumanMessage(content=f"闂{i}"))
    messages.append(AIMessage(content=f"鍥炵瓟{i}"))

trimmed = trim_agent_messages(messages, max_rounds=5)
print(f"鍘?{len(messages)} 鏉?鈫?淇壀鍚?{len(trimmed)} 鏉?)
```

> 馃挕 **娣卞害璁茶В**锛欰gent 绯荤粺涓殑娑堟伅绠＄悊姣旀櫘閫氬璇濆鏉傚緱澶氣€斺€旀瘡杞惊鐜細浜х敓澶氭潯娑堟伅锛圓I鎬濊€?宸ュ叿璋冪敤+宸ュ叿缁撴灉锛夛紝娑堟伅澧為暱閫熷害寰堝揩銆備慨鍓瓥鐣ヨ鐗瑰埆娉ㄦ剰锛氣憼 涓嶈兘鎴柇宸ュ叿璋冪敤-缁撴灉瀵?鈶?淇濈暀鏈€杩戠殑瀹屾暣鎺ㄧ悊閾?鈶?绯荤粺娑堟伅蹇呴』淇濈暀 鈶?澶暱鐨?Agent 杞ㄨ抗鍙互鎽樿銆傚湪 LangGraph 涓紝Checkpointer 鑷姩澶勭悊浜嗚繖浜涢棶棰樸€?>
> **馃摑 绮剧畝鎬荤粨**锛欰gent 娑堟伅娴?= 寰幆娣诲姞 Human/AI/Tool 娑堟伅锛涘宸ュ叿璋冪敤鏃?tool_calls 鍒楄〃鏈夊涓紱淇壀鏃朵笉鑳芥埅鏂伐鍏疯皟鐢ㄥ锛汱angGraph Checkpointer 鑷姩绠＄悊 Agent 鐘舵€併€?
---

## 鍗佸叚銆佹秷鎭殑楂樼骇鐢ㄦ硶

### 16.1 娑堟伅鍙樹綋涓庢ā鏉?
**姒傚康瑙ｉ噴**锛氭湁鏃朵綘闇€瑕佸熀浜庢ā鏉垮揩閫熷垱寤哄鏉℃秷鎭€斺€旀瘮濡傜郴缁熸秷鎭牴鎹敤鎴风被鍨嬩笉鍚岃€屼笉鍚屻€傛秷鎭ā鏉垮氨鏄瀹氫箟鐨勬秷鎭粨鏋勶紝濉叆鍙橀噺鍚庣敓鎴愬叿浣撴秷鎭€?
**绀轰緥**锛?
```python
# 绀轰緥 16.1.1锛氭秷鎭ā鏉?from langchain_core.messages import SystemMessage, HumanMessage

def create_system_prompt(user_type: str) -> SystemMessage:
    """鏍规嵁鐢ㄦ埛绫诲瀷鐢熸垚绯荤粺鎻愮ず"""
    prompts = {
        "vip": "浣犳槸VIP涓撳睘瀹㈡湇锛屼紭鍏堝鐞嗙敤鎴烽棶棰橈紝璇皵浜插垏銆?,
        "normal": "浣犳槸鏍囧噯瀹㈡湇锛屾寜娴佺▼鍥炵瓟鐢ㄦ埛闂銆?,
        "enterprise": "浣犳槸浼佷笟绾ф妧鏈敮鎸侊紝鍥炵瓟涓撲笟鐨勬妧鏈棶棰樸€?,
    }
    return SystemMessage(content=prompts.get(user_type, prompts["normal"]))

# 涓嶅悓鐢ㄦ埛鐨勭郴缁熸彁绀?vip_prompt = create_system_prompt("vip")
normal_prompt = create_system_prompt("normal")
enterprise_prompt = create_system_prompt("enterprise")

print(f"VIP: {vip_prompt.content[:30]}...")
print(f"鏅€? {normal_prompt.content[:30]}...")
```

### 16.2 娑堟伅鐨勬牸寮忓寲涓庣編鍖?
**绀轰緥锛歱retty_print**

```python
# 绀轰緥 16.2.1锛氭秷鎭殑缇庤鎵撳嵃
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

messages = [
    SystemMessage(content="浣犳槸涓€涓姪鎵?),
    HumanMessage(content="浣犲ソ锛?),
    AIMessage(content="浣犲ソ锛佹湁浠€涔堝彲浠ュ府浣犵殑锛?),
]

def pretty_print_messages(messages: list):
    """缇庤鍦版墦鍗版秷鎭垪琛?""
    role_emoji = {
        "system": "鈿欙笍",
        "human": "馃懁",
        "ai": "馃",
        "tool": "馃敡",
    }
    for msg in messages:
        emoji = role_emoji.get(msg.type, "馃摑")
        content = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
        print(f"{emoji} [{msg.type:>8}] {content}")

pretty_print_messages(messages)
```

### 16.3 娑堟伅鐨勮繃婊や笌杞崲

**绀轰緥锛氭寜绫诲瀷杩囨护娑堟伅**

```python
# 绀轰緥 16.3.1锛氭秷鎭繃婊?from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

messages = [
    SystemMessage(content="绯荤粺鎸囦护"),
    HumanMessage(content="浣犲ソ"),
    AIMessage(content="浣犲ソ锛?),
    ToolMessage(content="宸ュ叿缁撴灉", tool_call_id="1", name="weather"),
    AIMessage(content="鍖椾含浠婂ぉ鏅村ぉ"),
]

# 鍙繚鐣欎汉绫诲拰 AI 娑堟伅
chat_only = [m for m in messages if m.type in ("human", "ai")]
print(f"瀵硅瘽娑堟伅: {len(chat_only)} 鏉?)

# 鍙彁鍙栨枃鏈唴瀹?texts = [m.content for m in messages if isinstance(m.content, str)]
print(f"鎵€鏈夋枃鏈? {texts}")
```

### 16.4 娑堟伅涓?LCEL 鐨勯泦鎴?
**绀轰緥锛氬湪閾句腑浣跨敤娑堟伅**

```python
# 绀轰緥 16.4.1锛氭秷鎭湪 LCEL 閾句腑鐨勪娇鐢?from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableLambda

# 鏋勫缓瀵硅瘽涓婁笅鏂?def build_context(question: str) -> list:
    """鏋勫缓娑堟伅鍒楄〃"""
    return [
        SystemMessage(content="浣犳槸涓€涓姪鎵?),
        HumanMessage(content=question)
    ]

# 妯℃嫙妯″瀷璋冪敤
def call_model(messages: list) -> str:
    """妯℃嫙 LLM 璋冪敤"""
    return f"鍥炵瓟: {messages[-1].content}"

# 缁勮閾?chain = (
    RunnableLambda(build_context)
    | RunnableLambda(call_model)
)

result = chain.invoke("浠€涔堟槸 LangChain锛?)
print(result)
```

> 馃挕 **娣卞害璁茶В**锛氭秷鎭綋绯荤殑楂樼骇鐢ㄦ硶鍥寸粫"濡備綍楂樻晥绠＄悊鍜岃浆鎹㈡秷鎭垪琛?灞曞紑銆傚湪澶嶆潅鐨?LLM 搴旂敤涓紝浣犵粡甯搁渶瑕侊細鈶?鎸夋潯浠惰繃婊ゆ秷鎭?鈶?鏍煎紡鍖栨秷鎭敤浜庡睍绀?鈶?鍦ㄩ摼涓瀯寤烘秷鎭垪琛?鈶?淇壀鍜屾憳瑕佹秷鎭€傝繖浜涙搷浣滈兘鏄秷鎭垪琛ㄧ殑鏍囧噯鎿嶄綔锛孡angChain 鎻愪緵浜嗕赴瀵岀殑宸ュ叿鍑芥暟銆?>
> **馃摑 绮剧畝鎬荤粨**锛氭秷鎭ā鏉挎牴鎹満鏅敓鎴愪笉鍚岀郴缁熸彁绀猴紱pretty_print 缇庡寲灞曠ず锛涙寜绫诲瀷杩囨护鍜岃浆鎹㈡秷鎭紱娑堟伅鍦?LCEL 閾句腑浣滀负涓棿鏁版嵁娴佽浆锛涚伒娲绘搷浣滄秷鎭垪琛ㄦ槸楂樼骇瀵硅瘽搴旂敤鐨勫叧閿€?
---

## 鍗佷竷銆佹秷鎭簭鍒楀寲瀹炴垬

### 17.1 瀹屾暣搴忓垪鍖栨祦绋?
**姒傚康瑙ｉ噴**锛氬簭鍒楀寲灏辨槸鎶婂唴瀛樹腑鐨勬秷鎭璞?鎷嶄釜鐓?瀛樹笅鏉ワ紝涓嬫闇€瑕佹椂"鎭㈠"鎴愬師鏉ョ殑鏍峰瓙銆傚湪 Web 搴旂敤涓紝杩欏氨鏄繚瀛樼敤鎴峰璇濊褰曠殑杩囩▼銆?
**瀹屾暣绀轰緥锛氫繚瀛樺拰鎭㈠瀵硅瘽**

```python
# 绀轰緥 17.1.1锛氬畬鏁寸殑瀵硅瘽淇濆瓨涓庢仮澶?import json
from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage,
    messages_from_dict, messages_to_dict
)

# 淇濆瓨瀵硅瘽
def save_conversation(messages: list, filepath: str):
    """淇濆瓨瀵硅瘽鍒版枃浠?""
    serialized = messages_to_dict(messages)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(serialized, f, ensure_ascii=False, indent=2)

# 鍔犺浇瀵硅瘽
def load_conversation(filepath: str) -> list:
    """浠庢枃浠跺姞杞藉璇?""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return messages_from_dict(data)

# 娴嬭瘯
conversation = [
    SystemMessage(content="浣犳槸涓€涓姪鎵?),
    HumanMessage(content="浣犲ソ"),
    AIMessage(content="浣犲ソ锛?),
]

# 淇濆瓨
save_conversation(conversation, "my_chat.json")

# 鍔犺浇
restored = load_conversation("my_chat.json")
print(f"鎭㈠浜?{len(restored)} 鏉℃秷鎭?)
for msg in restored:
    print(f"  {msg.type}: {msg.content}")
```

### 17.2 鏁版嵁搴撳瓨鍌ㄦ牸寮?
**绀轰緥锛歋QL 琛ㄧ粨鏋勮璁?*

```sql
-- 绀轰緥 17.2.1锛氬璇濆巻鍙茬殑 SQL 琛ㄧ粨鏋?CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    message_type TEXT NOT NULL,  -- human/ai/system/tool
    content TEXT NOT NULL,
    additional_kwargs TEXT,     -- JSON 瀛楃涓?    response_metadata TEXT,      -- JSON 瀛楃涓?    name TEXT,
    tool_call_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 鏌ヨ鏌愪釜浼氳瘽鐨勬墍鏈夋秷鎭?SELECT * FROM chat_messages
WHERE session_id = 'user_123'
ORDER BY created_at;

-- 缁熻鏌愪釜浼氳瘽鐨勬秷鎭暟
SELECT COUNT(*) FROM chat_messages WHERE session_id = 'user_123';

-- 鍒犻櫎杩囨湡浼氳瘽
DELETE FROM chat_messages WHERE created_at < '2026-01-01';
```

### 17.3 甯歌搴忓垪鍖栧潙鐐?
**鍧戠偣 1锛欴ateTime 搴忓垪鍖栭棶棰?*

閿欒鐜拌薄锛歚TypeError: Object of type datetime is not JSON serializable`

鍘熷洜锛氭秷鎭殑鏌愪簺瀛楁鍖呭惈 datetime 瀵硅薄銆?
姝ｇ‘鍋氭硶锛?
```python
# 绀轰緥 17.3.1锛氬鐞?datetime 搴忓垪鍖?import json
from datetime import datetime

def json_serializer(obj):
    """鑷畾涔?JSON 搴忓垪鍖栧櫒"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

# 浣跨敤
# json.dump(data, default=json_serializer)
```

> 馃挕 **娣卞害璁茶В**锛氭秷鎭寔涔呭寲鏄敓浜у璇濈郴缁熺殑蹇呭鑳藉姏銆傞€夋嫨瀛樺偍鏍煎紡鏃惰€冭檻锛氣憼 绠€鍗曠敤 JSON 鏂囦欢 鈶?楂樻€ц兘鐢?Redis 鈶?鍚堣瀹¤鐢?SQL 鈶?鐏垫椿鏌ヨ鐢?MongoDB銆傚簭鍒楀寲鏃舵敞鎰忕被鍨嬩俊鎭繚鐣欏拰鐗规畩绫诲瀷锛坉atetime锛夌殑澶勭悊銆?>
> **馃摑 绮剧畝鎬荤粨**锛歮essages_to_dict/messages_from_dict 澶勭悊搴忓垪鍖栵紱JSON 鏂囦欢閫傚悎绠€鍗曞満鏅紱SQL 琛ㄧ粨鏋勫瓨鍌ㄦ秷鎭紱娉ㄦ剰 datetime 搴忓垪鍖栵紱淇濈暀 type 瀛楁銆?
---

## 鍗佸叓銆佹€ц兘浼樺寲涓庢渶浣冲疄璺?
### 18.1 娑堟伅澶勭悊鎬ц兘浼樺寲

| 浼樺寲鏂瑰悜 | 鏂规硶 | 鏀剁泭 |
|---------|------|------|
| **鍑忓皯娑堟伅鏁?* | 淇壀/鎽樿 | 鍑忓皯 token 鐢ㄩ噺锛岄檷浣庢垚鏈?|
| **鎵归噺澶勭悊** | batch() | 鍑忓皯 API 璋冪敤娆℃暟 |
| **娴佸紡杈撳嚭** | stream() | 鏀瑰杽鐢ㄦ埛浣撻獙 |
| **缂撳瓨** | LLM 缂撳瓨 | 閲嶅鏌ヨ闆舵垚鏈?|
| **鍘嬬缉** | 娑堟伅鎽樿 | 鍑忓皯涓婁笅鏂囬暱搴?|

### 18.2 鐢熶骇鐜娑堟伅绠＄悊鏈€浣冲疄璺?
```python
# 绀轰緥 18.2.1锛氱敓浜х骇娑堟伅绠＄悊
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class ProductionMessageManager:
    """鐢熶骇鐜娑堟伅绠＄悊鍣?""

    def __init__(self, system_prompt: str, max_messages: int = 20):
        self.system_prompt = system_prompt
        self.max_messages = max_messages
        self.messages = [SystemMessage(content=system_prompt)]

    def add_user_message(self, content: str):
        self.messages.append(HumanMessage(content=content))
        self._trim()

    def add_ai_message(self, content: str):
        self.messages.append(AIMessage(content=content))
        self._trim()

    def _trim(self):
        """淇壀娑堟伅锛屼繚鐣欑郴缁熸秷鎭拰鏈€杩?N 鏉?""
        if len(self.messages) <= self.max_messages:
            return
        # 淇濈暀绯荤粺娑堟伅 + 鏈€杩?max_messages-1 鏉?        self.messages = [self.messages[0]] + self.messages[-(self.max_messages-1):]

    def get_messages(self) -> list:
        return self.messages

# 浣跨敤
manager = ProductionMessageManager(
    system_prompt="浣犳槸涓€涓鏈嶅姪鎵?,
    max_messages=20
)
manager.add_user_message("浣犲ソ")
manager.add_ai_message("浣犲ソ锛?)
print(f"褰撳墠 {len(manager.get_messages())} 鏉℃秷鎭?)
```

> 馃挕 **娣卞害璁茶В**锛氱敓浜х幆澧冪殑娑堟伅绠＄悊鏄竴涓寔缁紭鍖栫殑杩囩▼銆傚叧閿寚鏍囷細鈶?骞冲潎 token 鐢ㄩ噺 鈶?骞冲潎瀵硅瘽杞暟 鈶?淇壀瑙﹀彂棰戠巼 鈶?鎽樿璐ㄩ噺銆傚畾鏈熷垎鏋愯繖浜涙寚鏍囷紝鎸佺画浼樺寲浣犵殑娑堟伅绠＄悊绛栫暐銆?>
> **馃摑 绮剧畝鎬荤粨**锛氱敓浜х幆澧冮渶瑕佹秷鎭鐞嗗櫒锛涜嚜鍔ㄤ慨鍓?绯荤粺娑堟伅淇濈暀锛涚洃鎺?token 鐢ㄩ噺锛涙祦寮忚緭鍑烘敼鍠勪綋楠岋紱缂撳瓨闄嶄綆鎴愭湰銆?
---

## 鍗佷節銆佹搴︾粌涔犻锛堣ˉ鍏咃級

**棰樼洰 7**锛氳璁′竴涓璇濈郴缁燂紝瑕佹眰锛?1. 绯荤粺娑堟伅锛氫綘鏄竴涓?Python 缂栫▼鍔╂墜
2. 鐢ㄦ埛鎻愰棶鍚庯紝AI 鍥炵瓟鍓嶅厛璋冪敤浠ｇ爜瑙ｉ噴宸ュ叿
3. 宸ュ叿杩斿洖缁撴灉鍚?AI 鍐嶆€荤粨鍥炵瓟
4. 瀵硅瘽鍘嗗彶鐢?FileChatMessageHistory 鎸佷箙鍖?
<details>
<summary>鍙傝€冨疄鐜版€濊矾</summary>

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_community.chat_message_histories import FileChatMessageHistory

class CodingAssistant:
    def __init__(self):
        self.history = FileChatMessageHistory("coding_assistant.json")
        if len(self.history.messages) == 0:
            self.history.add_message(SystemMessage(content="浣犳槸涓€涓?Python 缂栫▼鍔╂墜"))

    def ask(self, question: str):
        self.history.add_user_message(question)

        # 璋冪敤宸ュ叿锛堟ā鎷燂級
        tool_result = ToolMessage(
            content=f"浠ｇ爜鍒嗘瀽缁撴灉: {question} 鐨勮В鍐虫柟妗堟槸...",
            tool_call_id="call_001",
            name="code_explainer"
        )
        self.history.add_message(tool_result)

        # AI 鎬荤粨
        answer = f"鏍规嵁鍒嗘瀽锛寋question} 鐨勭瓟妗堟槸..."
        self.history.add_ai_message(answer)
        return answer
```
</details>

**棰樼洰 8**锛氳В閲婁负浠€涔?Agent 绯荤粺涓?ToolMessage 涓嶈兘琚殢鎰忎慨鍓垹闄ゃ€?
<details>
<summary>鍙傝€冪瓟妗?/summary>

**鍘熷洜**锛歍oolMessage 鍜屼箣鍓嶇殑 AIMessage 涓殑宸ュ叿璋冪敤鏄?*鎴愬鍑虹幇**鐨勩€傚鏋滃垹闄や簡 ToolMessage 浣嗕繚鐣欎簡 AIMessage 涓殑宸ュ叿璋冪敤锛屾ā鍨嬩細鍥版儜鈥斺€?鎴戣皟鐢ㄤ簡宸ュ叿浣嗘病鏀跺埌缁撴灉锛?銆傚弽涔嬶紝濡傛灉鍒犻櫎浜?AIMessage 浣嗕繚鐣欎簡 ToolMessage锛屾ā鍨嬩細鍥版儜鈥斺€?杩欎釜宸ュ叿缁撴灉鏄摢鏉ョ殑锛?銆?
**姝ｇ‘鍋氭硶**锛氫慨鍓椂蹇呴』淇濇寔宸ュ叿璋冪敤-缁撴灉瀵圭殑瀹屾暣鎬с€傝涔堥兘淇濈暀锛岃涔堥兘鍒犻櫎銆?</details>

---

> 馃搶 **鏂囨。璇存槑**锛氭湰鏂囨。鍩轰簬 LangChain 0.2+ 鐗堟湰缂栧啓銆傛秷鎭綋绯绘槸 LangChain 瀵硅瘽鑳藉姏鐨勬牳蹇冿紝鐞嗚В娑堟伅绫诲瀷銆佹秷鎭巻鍙层€佹祦寮忔秷鎭拰涓婁笅鏂囩鐞嗭紝鏄瀯寤虹敓浜х骇瀵硅瘽搴旂敤鐨勫熀纭€銆?

---

## 浜屽崄銆佹秷鎭綋绯讳笌 LangGraph 鐨勫叧绯?
### 20.1 浠?ChatMessageHistory 鍒?Checkpointer

**姒傚康瑙ｉ噴**锛氫紶缁熺殑 ChatMessageHistory 鏄?娑堟伅鍒楄〃绠＄悊鍣?鈥斺€斿彧绠″瓨娑堟伅銆佸彇娑堟伅銆侺angGraph 鐨?Checkpointer 鏄?瀹屾暣鐘舵€佺鐞嗗櫒"鈥斺€斾笉浠呯娑堟伅锛岃繕绠℃暣涓?Agent 鐨勭姸鎬侊紙鍖呮嫭涓棿姝ラ銆佸垎鏀€夋嫨绛夛級銆?
**鍘熺悊璇存槑**锛氬湪 LangGraph 涓紝瀵硅瘽鍘嗗彶涓嶅啀鏄竴涓畝鍗曠殑娑堟伅鍒楄〃锛岃€屾槸鏁翠釜鍥剧姸鎬佺殑涓€閮ㄥ垎銆侰heckpointer 淇濆瓨姣忎竴姝ョ殑鐘舵€佸揩鐓э紝鏀寔鏃堕棿鏃呰锛堝洖鍒颁换鎰忓巻鍙茶妭鐐归噸鏂版墽琛岋級銆?
**瀵规瘮绀轰緥**锛?
```python
# 绀轰緥 20.1.1锛欳hatMessageHistory vs LangGraph Checkpointer
from langchain_core.messages import HumanMessage, AIMessage

# 浼犵粺鏂瑰紡锛欳hatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
history = InMemoryChatMessageHistory()
history.add_user_message("浣犲ソ")
history.add_ai_message("浣犲ソ锛?)
# 绠€鍗曚絾鍔熻兘鏈夐檺鈥斺€斿彧鑳界鐞嗘秷鎭垪琛?
# LangGraph 鏂瑰紡锛欳heckpointer
# from langgraph.checkpoint.memory import MemorySaver
# checkpointer = MemorySaver()
# 涓嶄粎淇濆瓨娑堟伅锛岃繕淇濆瓨瀹屾暣鍥剧姸鎬?# 鏀寔鏃堕棿鏃呰銆佸垎鏀仮澶嶃€佹柇鐐圭画璺?```

### 20.2 娑堟伅鍦ㄥ浘鐘舵€佷腑鐨勮鑹?
**绀轰緥锛歀angGraph 涓殑娑堟伅鐘舵€?*

```python
# 绀轰緥 20.2.1锛歀angGraph 涓殑娑堟伅绠＄悊
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    """瀵硅瘽鐘舵€佲€斺€旀秷鎭嚜鍔?reducer"""
    messages: Annotated[list[BaseMessage], add_messages]

# 鐘舵€佷腑鐨?messages 瀛楁鑷姩鏀寔杩藉姞
# add_messages reducer 浼氳嚜鍔ㄥ鐞嗘秷鎭悎骞?```

> 馃挕 **娣卞害璁茶В**锛氭秷鎭綋绯诲湪 LangGraph 涓繘鍖栦簡鈥斺€斾粠"鍗曠嫭鐨勫璇濆巻鍙?鍙樻垚浜?鍥剧姸鎬佺殑涓€閮ㄥ垎"銆傝繖璁╂秷鎭鐞嗗拰 Agent 鐘舵€佺鐞嗙粺涓€浜嗚捣鏉ャ€傚鏋滀綘鍦ㄦ柊椤圭洰涓娇鐢?LangGraph锛屼笉闇€瑕佺洿鎺ユ搷浣?ChatMessageHistory鈥斺€旂敤 Checkpointer 鏇村己澶с€?>
> **馃摑 绮剧畝鎬荤粨**锛欳hatMessageHistory 绠＄悊绠€鍗曟秷鎭垪琛紱LangGraph Checkpointer 绠＄悊瀹屾暣鐘舵€侊紱LangGraph 涓秷鎭槸鐘舵€佺殑涓€閮ㄥ垎锛沘dd_messages reducer 鑷姩澶勭悊娑堟伅杩藉姞銆?
---

## 浜屽崄涓€銆佹秷鎭伐鍏峰嚱鏁伴€熸煡

### 21.1 娑堟伅宸ュ叿鍑芥暟琛?
| 鍑芥暟 | 鐢ㄩ€?| 绀轰緥 |
|------|------|------|
| `messages_to_dict()` | 娑堟伅鍒楄〃杞瓧鍏?| `messages_to_dict(messages)` |
| `messages_from_dict()` | 瀛楀吀鎭㈠娑堟伅鍒楄〃 | `messages_from_dict(data)` |
| `trim_messages()` | 淇壀娑堟伅 | `trim_messages(msgs, max_count=10)` |
| `convert_to_messages()` | 鍚勭鏍煎紡杞秷鎭?| `convert_to_messages([("user", "hi")])` |

### 21.2 娑堟伅鏍煎紡杞崲

**绀轰緥锛氫笉鍚屾牸寮忎簰杞?*

```python
# 绀轰緥 21.2.1锛氭秷鎭牸寮忚浆鎹?from langchain_core.messages import convert_to_messages

# 浠庡厓缁勫垪琛ㄨ浆鎹?tuple_format = [
    ("system", "浣犳槸鍔╂墜"),
    ("human", "浣犲ソ"),
    ("ai", "浣犲ソ锛?),
]

messages = convert_to_messages(tuple_format)
print(f"杞崲浜?{len(messages)} 鏉℃秷鎭?)
for msg in messages:
    print(f"  {msg.type}: {msg.content}")

# 浠?OpenAI 鏍煎紡杞崲
openai_format = [
    {"role": "user", "content": "浣犲ソ"},
    {"role": "assistant", "content": "浣犲ソ锛?},
]
messages2 = convert_to_messages(openai_format)
print(f"OpenAI 鏍煎紡杞崲: {len(messages2)} 鏉?)
```

> 馃挕 **娣卞害璁茶В**锛氭秷鎭牸寮忚浆鎹㈠伐鍏峰湪瀵规帴涓嶅悓绯荤粺鏃跺緢鏈夌敤鈥斺€旀瘮濡備粠鏃х郴缁熷鍏ュ璇濊褰曪紝鎴栬€呭鍑哄埌鍏朵粬骞冲彴銆俙convert_to_messages` 鏀寔澶氱杈撳叆鏍煎紡锛岃嚜鍔ㄨ瘑鍒苟杞崲銆?>
> **馃摑 绮剧畝鎬荤粨**锛歮essages_to_dict/from_dict 搴忓垪鍖栵紱trim_messages 淇壀锛沜onvert_to_messages 鏍煎紡杞崲锛涙敮鎸佸厓缁勫拰 OpenAI 鏍煎紡銆?
---

## 浜屽崄浜屻€佹秷鎭被鍨嬫紨杩涗笌鐗堟湰宸紓

### 22.1 涓昏鐗堟湰鍙樺寲

| 鐗堟湰 | 鍙樺寲 | 璇存槑 |
|------|------|------|
| 0.1 | 鍩虹娑堟伅绫诲瀷 | Human/AI/System/Function |
| 0.2 | 鏂板 ToolMessage | 鏇夸唬 FunctionMessage |
| 0.2 | MessageChunk 鏀硅繘 | 娴佸紡鎷兼帴鏇村畬鍠?|
| 0.3 | 澶氭ā鎬?content | content 鏀寔鍒楄〃褰㈠紡 |
| 0.3 | 娑堟伅 id 灞炴€?| 姣忔潯娑堟伅鏈夊敮涓€ ID |

### 22.2 杩佺Щ鎸囧崡

```python
# 绀轰緥 22.2.1锛氭棫鐗?FunctionMessage 鈫?鏂扮増 ToolMessage
# 鉂?鏃х増
# from langchain_core.messages import FunctionMessage
# old = FunctionMessage(content="缁撴灉", name="get_weather")

# 鉁?鏂扮増
from langchain_core.messages import ToolMessage
new = ToolMessage(content="缁撴灉", tool_call_id="call_001", name="get_weather")
```

> 馃挕 **娣卞害璁茶В**锛歀angChain 鐨勬秷鎭綋绯诲湪鎸佺画婕旇繘銆備粠 FunctionMessage 鍒?ToolMessage 鐨勫彉鍖栵紝鍙嶆槧浜嗕粠"鍑芥暟璋冪敤"鍒?宸ュ叿璋冪敤"鐨勬蹇靛崌绾с€俆oolMessage 鏇存槑纭湴鍏宠仈浜?tool_call_id锛岃宸ュ叿璋冪敤鐨勫璇濇祦绋嬫洿娓呮櫚銆?>
> **馃摑 绮剧畝鎬荤粨**锛欶unctionMessage 鏄棫鐗堬紝ToolMessage 鏄柊鐗堬紱ToolMessage 鏈?tool_call_id锛沜ontent 鏀寔澶氭ā鎬佸垪琛紱娑堟伅鏈夊敮涓€ id锛涙寔缁叧娉ㄧ増鏈洿鏂般€?
---

## 浜屽崄涓夈€侀檮褰曪細娑堟伅 API 閫熸煡琛?
### 娑堟伅鍒涘缓

```python
from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage,
    ToolMessage, FunctionMessage, ChatMessage,
    AIMessageChunk, HumanMessageChunk,
)

# 鍒涘缓娑堟伅
HumanMessage(content="...")
AIMessage(content="...")
SystemMessage(content="...")
ToolMessage(content="...", tool_call_id="...", name="...")
```

### 娑堟伅灞炴€?
```python
msg.content          # 娑堟伅鍐呭
msg.additional_kwargs # 鎵╁睍鍙傛暟
msg.response_metadata # 鍏冩暟鎹?msg.type             # 娑堟伅绫诲瀷
msg.name             # 鍙戦€佽€呭悕绉?msg.id               # 娑堟伅 ID
```

### 娑堟伅鍘嗗彶

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_community.chat_message_histories import (
    FileChatMessageHistory, RedisChatMessageHistory, SQLChatMessageHistory
)

history.add_user_message("...")
history.add_ai_message("...")
history.add_message(msg)
history.messages     # 鑾峰彇鎵€鏈夋秷鎭?history.clear()      # 娓呯┖
```

### 娴佸紡娑堟伅

```python
# 鎷兼帴 chunk
full = None
for chunk in stream:
    full = chunk if full is None else full + chunk
```

### 娑堟伅宸ュ叿

```python
from langchain_core.messages import messages_to_dict, messages_from_dict, trim_messages

serialized = messages_to_dict(messages)
restored = messages_from_dict(serialized)
trimmed = trim_messages(messages, max_count=10)
```

---

> 馃帗 **鍏ㄦ枃鎬荤粨**锛歀angChain 娑堟伅浣撶郴鏄瀯寤哄璇濆簲鐢ㄧ殑鍩虹煶銆傚叚绉嶆秷鎭被鍨嬪悇鍙稿叾鑱岋紝MessageChunk 鏀寔娴佸紡鎷兼帴锛孋hatMessageHistory 绠＄悊瀵硅瘽鎸佷箙鍖栵紝淇壀鍜屾憳瑕佺鐞嗕笂涓嬫枃绐楀彛銆傛帉鎻℃秷鎭綋绯伙紝浣犲氨鑳戒粠绠€鍗曡亰澶╂満鍣ㄤ汉鍒板鏉?Agent 绯荤粺锛岀伒娲绘瀯寤哄悇绉嶅璇濆簲鐢ㄣ€?

---

## 浜屽崄鍥涖€佹秷鎭疄鎴樻渚嬧€斺€旀瀯寤哄畬鏁磋亰澶╂満鍣ㄤ汉

### 24.1 闇€姹傚垎鏋?
鏋勫缓涓€涓敓浜х骇鑱婂ぉ鏈哄櫒浜猴紝闇€姹傦細
1. 鏀寔澶氳疆瀵硅瘽
2. 瀵硅瘽鍘嗗彶鎸佷箙鍖?3. 瓒呰繃20杞嚜鍔ㄤ慨鍓?4. 鏀寔娴佸紡杈撳嚭
5. 鎸夌敤鎴烽殧绂诲璇?
### 24.2 瀹屾暣浠ｇ爜瀹炵幇

```python
# 绀轰緥 24.2.1锛氱敓浜х骇鑱婂ぉ鏈哄櫒浜哄畬鏁村疄鐜?from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage,
    trim_messages
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableLambda

class ProductionChatBot:
    """鐢熶骇绾ц亰澶╂満鍣ㄤ汉"""

    def __init__(self, system_prompt: str = "浣犳槸涓€涓姪鎵?, max_rounds: int = 20):
        self.system_prompt = system_prompt
        self.max_rounds = max_rounds
        self.sessions = {}  # user_id -> history

    def _get_history(self, user_id: str) -> InMemoryChatMessageHistory:
        """鑾峰彇鐢ㄦ埛鐨勫璇濆巻鍙?""
        if user_id not in self.sessions:
            history = InMemoryChatMessageHistory()
            history.add_message(SystemMessage(content=self.system_prompt))
            self.sessions[user_id] = history
        return self.sessions[user_id]

    def chat(self, user_id: str, message: str) -> str:
        """澶勭悊鐢ㄦ埛娑堟伅锛岃繑鍥?AI 鍥炲"""
        history = self._get_history(user_id)

        # 1. 娣诲姞鐢ㄦ埛娑堟伅
        history.add_user_message(message)

        # 2. 淇壀鍘嗗彶
        messages = trim_messages(
            history.messages,
            max_count=self.max_rounds,
            include_system=True,
            strategy="last"
        )

        # 3. 璋冪敤 LLM锛堟ā鎷燂級
        ai_reply = f"鍥炲: {message}"  # 瀹為檯: model.invoke(messages)
        history.add_ai_message(ai_reply)

        return ai_reply

    def chat_stream(self, user_id: str, message: str):
        """娴佸紡瀵硅瘽"""
        history = self._get_history(user_id)
        history.add_user_message(message)

        # 妯℃嫙娴佸紡杈撳嚭
        response_parts = ["鍥炲", ": ", message]
        full_reply = ""
        for part in response_parts:
            full_reply += part
            yield part

        history.add_ai_message(full_reply)

    def get_history(self, user_id: str) -> list:
        """鑾峰彇瀵硅瘽鍘嗗彶"""
        return self._get_history(user_id).messages

    def clear_history(self, user_id: str):
        """娓呯┖瀵硅瘽鍘嗗彶"""
        if user_id in self.sessions:
            del self.sessions[user_id]


# ===== 浣跨敤绀轰緥 =====
bot = ProductionChatBot(
    system_prompt="浣犳槸涓€涓弸濂界殑鍔╂墜",
    max_rounds=10
)

# 鐢ㄦ埛1瀵硅瘽
print("=== 鐢ㄦ埛1 ===")
print(bot.chat("user1", "浣犲ソ"))
print(bot.chat("user1", "璁蹭釜绗戣瘽"))

# 鐢ㄦ埛2瀵硅瘽
print("\n=== 鐢ㄦ埛2 ===")
print(bot.chat("user2", "Hi"))

# 鏌ョ湅鍘嗗彶
print(f"\n鐢ㄦ埛1鍘嗗彶: {len(bot.get_history('user1'))} 鏉℃秷鎭?)
print(f"鐢ㄦ埛2鍘嗗彶: {len(bot.get_history('user2'))} 鏉℃秷鎭?)
```

### 24.3 鎵╁睍锛氭帴鍏ョ湡瀹?LLM

```python
# 绀轰緥 24.3.1锛氭帴鍏ョ湡瀹?OpenAI 妯″瀷
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import SystemMessage, HumanMessage
#
# class RealChatBot:
#     def __init__(self):
#         self.model = ChatOpenAI(model="gpt-4")
#         self.sessions = {}
#
#     def chat(self, user_id: str, message: str) -> str:
#         if user_id not in self.sessions:
#             self.sessions[user_id] = [
#                 SystemMessage(content="浣犳槸涓€涓姪鎵?)
#             ]
#
#         self.sessions[user_id].append(HumanMessage(content=message))
#
#         # 淇壀
#         messages = trim_messages(
#             self.sessions[user_id],
#             max_count=20,
#             include_system=True
#         )
#
#         response = self.model.invoke(messages)
#         self.sessions[user_id].append(response)
#         return response.content
```

> 馃挕 **娣卞害璁茶В**锛氳繖涓畬鏁存渚嬪睍绀轰簡娑堟伅浣撶郴鍦ㄥ疄闄呴」鐩腑鐨勭患鍚堝簲鐢ㄢ€斺€斿鐢ㄦ埛闅旂銆佸巻鍙蹭慨鍓€佹祦寮忚緭鍑恒€佹寔涔呭寲銆傚湪鐢熶骇鐜涓紝浣犻渶瑕佹妸 InMemoryChatMessageHistory 鎹㈡垚 RedisChatMessageHistory锛屾妸妯℃嫙 LLM 鎹㈡垚鐪熷疄妯″瀷锛屽姞涓婄洃鎺у拰閲嶈瘯銆?>
> **馃摑 绮剧畝鎬荤粨**锛氱敓浜х骇鑱婂ぉ鏈哄櫒浜洪渶瑕佸鐢ㄦ埛闅旂銆佽嚜鍔ㄤ慨鍓€佹祦寮忚緭鍑恒€佹寔涔呭寲锛汭nMemory 鎹?Redis锛涙ā鎷熸ā鍨嬫崲鐪熷疄妯″瀷锛涘姞涓婄洃鎺ч噸璇曘€?
---

## 浜屽崄浜斻€佹秷鎭皟璇曟妧宸?
### 25.1 鎵撳嵃娑堟伅缁撴瀯

**绀轰緥锛氳皟璇曟秷鎭垪琛?*

```python
# 绀轰緥 25.1.1锛氳皟璇曟秷鎭垪琛?from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def debug_messages(messages: list, title: str = "娑堟伅鍒楄〃"):
    """璋冭瘯鎵撳嵃娑堟伅鍒楄〃"""
    print(f"\n=== {title} ===")
    for i, msg in enumerate(messages):
        print(f"[{i}] type={msg.type}")
        print(f"    content: {msg.content[:80] if isinstance(msg.content, str) else msg.content}")
        if msg.additional_kwargs:
            print(f"    kwargs: {msg.additional_kwargs}")
        if msg.response_metadata:
            print(f"    metadata: {msg.response_metadata}")

# 娴嬭瘯
msgs = [
    SystemMessage(content="浣犳槸鍔╂墜"),
    HumanMessage(content="浣犲ソ"),
    AIMessage(content="浣犲ソ锛?, response_metadata={"model": "gpt-4"}),
]
debug_messages(msgs, "娴嬭瘯瀵硅瘽")
```

### 25.2 甯歌璋冭瘯鍦烘櫙

| 闂 | 妫€鏌ョ偣 |
|------|--------|
| AI 涓嶆寜璁惧畾鍥炵瓟 | 妫€鏌?SystemMessage 鏄惁鍦ㄧ涓€鏉?|
| 宸ュ叿璋冪敤澶辫触 | 妫€鏌?ToolMessage 鐨?tool_call_id 鍖归厤 |
| 娴佸紡杈撳嚭涓嶅畬鏁?| 妫€鏌?chunk 绱Н閫昏緫 |
| 瀵硅瘽鍘嗗彶涓㈠け | 妫€鏌ュ瓨鍌ㄥ悗绔厤缃?|
| Token 瓒呴檺 | 妫€鏌ヤ慨鍓瓥鐣?|

> 馃挕 **娣卞害璁茶В**锛氭秷鎭棶棰樻槸 LLM 搴旂敤涓渶甯歌鐨勯棶棰樸€傛帉鎻¤皟璇曟妧宸р€斺€旀墦鍗版秷鎭粨鏋勩€佹鏌?tool_call_id銆侀獙璇佸瓨鍌ㄢ€斺€旇兘蹇€熷畾浣?80% 鐨勫璇濈浉鍏?bug銆?>
> **馃摑 绮剧畝鎬荤粨**锛氳皟璇曟秷鎭垪琛ㄧ敤 debug 鍑芥暟锛涘父瑙侀棶棰樻鏌ユ竻鍗曪紱SystemMessage 浣嶇疆锛泃ool_call_id 鍖归厤锛沜hunk 绱Н锛涘瓨鍌ㄩ厤缃€?
---

## 浜屽崄鍏€佹秷鎭綋绯绘€荤粨鍥?
```mermaid
graph TD
    subgraph 娑堟伅绫诲瀷
        HM[HumanMessage<br/>鐢ㄦ埛杈撳叆]
        AIM[AIMessage<br/>AI鍥炲]
        SM[SystemMessage<br/>绯荤粺鎸囦护]
        TM[ToolMessage<br/>宸ュ叿缁撴灉]
        FM[FunctionMessage<br/>鏃х増鍑芥暟]
        CM[ChatMessage<br/>鑷畾涔夎鑹瞉
    end

    subgraph 娑堟伅灞炴€?        C[content 鍐呭]
        AK[additional_kwargs 鎵╁睍]
        RM[response_metadata 鍏冩暟鎹甝
        ID[id 鍞竴鏍囪瘑]
    end

    subgraph 娴佸紡澶勭悊
        MC[MessageChunk 娑堟伅鍧梋
        ADD[+ 鎷兼帴杩愮畻]
    end

    subgraph 瀵硅瘽鍘嗗彶
        IMH[InMemory 鍐呭瓨]
        FCH[File 鏂囦欢]
        RCH[Redis 缂撳瓨]
        SCH[SQL 鏁版嵁搴揮
    end

    subgraph 涓婁笅鏂囩鐞?        TR[淇壀]
        SU[鎽樿]
        TC[Token璁℃暟]
    end

    HM --> C
    AIM --> C
    SM --> C
    TM --> C
    AIM --> AK
    AIM --> RM
    MC --> ADD
    IMH --> HM
    FCH --> HM
    RCH --> HM
    SCH --> HM
    TR --> IMH
    SU --> IMH
    TC --> TR
```

---

> 馃搶 **鏂囨。鐗堟湰**锛氬熀浜?LangChain 0.2+ 鐗堟湰缂栧啓銆傛秷鎭綋绯绘槸 LangChain 瀵硅瘽鑳藉姏鐨勬牳蹇冿紝鎸佺画瀛︿範鍜屽疄璺垫槸鎺屾彙瀹冪殑鍏抽敭銆?

---

## 浜屽崄涓冦€佹秷鎭笌宸ュ叿璋冪敤娣卞害闆嗘垚

### 27.1 宸ュ叿璋冪敤娑堟伅鐨勫畬鏁寸敓鍛藉懆鏈?
**姒傚康瑙ｉ噴**锛氬伐鍏疯皟鐢ㄦ槸涓€涓畬鏁寸殑瀵硅瘽寰幆鈥斺€擜I 鍐冲畾璋冪敤宸ュ叿锛圓IMessage 甯?tool_calls锛夆啋 鎵ц宸ュ叿 鈫?宸ュ叿缁撴灉杩斿洖锛圱oolMessage锛夆啋 AI 鏍规嵁缁撴灉缁х画銆傝繖涓惊鐜彲鑳介噸澶嶅娆★紝鐩村埌 AI 寰楀嚭鏈€缁堢瓟妗堛€?
**瀹屾暣绀轰緥锛氬杞伐鍏疯皟鐢?*

```python
# 绀轰緥 27.1.1锛氬杞伐鍏疯皟鐢ㄧ殑瀹屾暣娑堟伅娴?from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

messages = [HumanMessage(content="鍖椾含鏄庡ぉ浼氫笅闆ㄥ悧锛熼渶瑕佸甫浼炲悧锛?)]

# 绗?杞細璋冪敤澶╂皵宸ュ叿
ai1 = AIMessage(
    content="鎴戦渶瑕佹煡涓€涓嬪寳浜殑澶╂皵棰勬姤銆?,
    additional_kwargs={
        "tool_calls": [{
            "id": "call_weather",
            "type": "function",
            "function": {
                "name": "get_weather_forecast",
                "arguments": '{"city": "鍖椾含", "days": 2}'
            }
        }]
    }
)
messages.append(ai1)

tool_result = ToolMessage(
    content="鍖椾含鏄庡ぉ澶氫簯锛岄檷姘存鐜?0%锛屽悗澶╂櫞銆?,
    tool_call_id="call_weather",
    name="get_weather_forecast"
)
messages.append(tool_result)

# 绗?杞細AI 鎬荤粨
ai2 = AIMessage(
    content="鍖椾含鏄庡ぉ澶氫簯锛岄檷姘存鐜囧彧鏈?0%锛屽熀鏈笉闇€瑕佸甫浼炪€傚悗澶╂櫞澶╋紝澶╂皵寰堝ソ锛?
)
messages.append(ai2)

# 鎵撳嵃瀹屾暣娴佺▼
print("=== 宸ュ叿璋冪敤瀹屾暣娴佺▼ ===")
for i, msg in enumerate(messages):
    if msg.type == "human":
        print(f"\n馃懁 鐢ㄦ埛: {msg.content}")
    elif msg.type == "ai" and msg.additional_kwargs.get("tool_calls"):
        tc = msg.additional_kwargs["tool_calls"][0]
        print(f"\n馃 AI鎬濊€? {msg.content}")
        print(f"   馃敡 璋冪敤 {tc['function']['name']}({tc['function']['arguments']})")
    elif msg.type == "tool":
        print(f"   馃摝 宸ュ叿缁撴灉: {msg.content}")
    elif msg.type == "ai":
        print(f"\n馃 AI鍥炵瓟: {msg.content}")
```

### 27.2 骞惰宸ュ叿璋冪敤鐨勬秷鎭鐞?
**姒傚康瑙ｉ噴**锛欰I 鍙互鍦ㄤ竴杞腑鍚屾椂璋冪敤澶氫釜宸ュ叿鈥斺€旀瘮濡傚悓鏃舵煡澶╂皵銆佹煡鏃ュ巻銆佹煡璁㈠崟銆傛瘡涓皟鐢ㄩ兘鏈夌嫭绔嬬殑 tool_call_id锛屾瘡涓粨鏋滈兘鏈夊搴旂殑 ToolMessage銆?
**绀轰緥**锛?
```python
# 绀轰緥 27.2.1锛氬苟琛屽伐鍏疯皟鐢?from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

messages = [HumanMessage(content="甯垜鏌ヤ笅浠婂ぉ鏃ョ▼鍜屽ぉ姘?)]

# AI 鍚屾椂璋冪敤涓や釜宸ュ叿
ai_call = AIMessage(
    content="",
    additional_kwargs={
        "tool_calls": [
            {"id": "call_calendar", "type": "function",
             "function": {"name": "get_calendar", "arguments": '{"date": "today"}'}},
            {"id": "call_weather", "type": "function",
             "function": {"name": "get_weather", "arguments": '{"city": "鍖椾含"}'}}
        ]
    }
)
messages.append(ai_call)

# 涓や釜宸ュ叿缁撴灉
messages.append(ToolMessage(
    content="浠婂ぉ涓嬪崍3鐐规湁浼氳",
    tool_call_id="call_calendar", name="get_calendar"
))
messages.append(ToolMessage(
    content="浠婂ぉ鏅达紝25搴?,
    tool_call_id="call_weather", name="get_weather"
))

# AI 缁煎悎鍥炵瓟
messages.append(AIMessage(
    content="浠婂ぉ涓嬪崍3鐐规湁浼氳锛屽ぉ姘旀櫞25搴︼紝閫傚悎鍑鸿銆?
))

print(f"鍏?{len(messages)} 鏉℃秷鎭?)
for msg in messages:
    print(f"  [{msg.type}] {msg.content[:40] if msg.content else '(璋冪敤宸ュ叿)'}")
```

> 馃挕 **娣卞害璁茶В**锛氬伐鍏疯皟鐢ㄦ槸 Agent 绯荤粺鐨勬牳蹇冦€傛秷鎭綋绯诲繀椤绘纭敮鎸佸伐鍏疯皟鐢ㄧ殑瀹屾暣鐢熷懡鍛ㄦ湡鈥斺€斾粠 AI 鍐冲畾璋冪敤銆佸埌宸ュ叿鎵ц銆佸埌缁撴灉杩斿洖銆佸埌 AI 缁煎悎鍥炵瓟銆傚叧閿槸 tool_call_id 鐨勬纭叧鑱斻€?>
> **馃摑 绮剧畝鎬荤粨**锛氬伐鍏疯皟鐢ㄥ畬鏁寸敓鍛藉懆鏈熲€斺€擜I璋冪敤鈫掑伐鍏锋墽琛屸啋缁撴灉杩斿洖鈫扐I鎬荤粨锛涘杞伐鍏疯皟鐢ㄥ惊鐜紱骞惰璋冪敤澶氫釜宸ュ叿锛泃ool_call_id 姝ｇ‘鍏宠仈锛涙秷鎭垪琛ㄥ畬鏁磋褰曟帹鐞嗚繃绋嬨€?
---

## 浜屽崄鍏€佹秷鎭殑鏈€浣冲疄璺垫€荤粨

### 28.1 娑堟伅璁捐鍘熷垯

| 鍘熷垯 | 璇存槑 | 绀轰緥 |
|------|------|------|
| **鍗曚竴鑱岃矗** | 姣忔潯娑堟伅鍙〃杈句竴涓剰鎬?| 涓嶈涓€鏉℃秷鎭棦鎻愰棶鍙堝洖绛?|
| **瑙掕壊娓呮櫚** | 娑堟伅绫诲瀷姝ｇ‘閫夋嫨 | 绯荤粺鎸囦护鐢?SystemMessage |
| **鍐呭绠€娲?* | 閬垮厤鍐楅暱閲嶅 | 闀垮唴瀹圭敤鎽樿浠ｆ浛鍘熸枃 |
| **椤哄簭姝ｇ‘** | Human 鍜?AI 浜ゆ浛 | 涓嶈杩炵画涓ゆ潯 HumanMessage |
| **宸ュ叿閰嶅** | 宸ュ叿璋冪敤鍜岀粨鏋滄垚瀵?| tool_call_id 蹇呴』鍖归厤 |

### 28.2 鐢熶骇鐜妫€鏌ユ竻鍗?
- [ ] SystemMessage 鍦ㄥ璇濈涓€鏉?- [ ] 瀵硅瘽鍘嗗彶鏈夎嚜鍔ㄤ慨鍓瓥鐣?- [ ] 闀垮璇濇湁鎽樿鍘嬬缉鏈哄埗
- [ ] 鐢熶骇鐜鐢?Redis/SQL 瀛樺偍
- [ ] Token 鐢ㄩ噺鏈夌洃鎺у憡璀?- [ ] ToolMessage 鐨?tool_call_id 绮剧‘鍖归厤
- [ ] 娴佸紡杈撳嚭鏈?chunk 绱Н閫昏緫
- [ ] 娑堟伅搴忓垪鍖栦繚鐣?type 瀛楁
- [ ] 澶氱敤鎴峰璇濇寜 user_id 闅旂
- [ ] 瀵硅瘽鍘嗗彶鏈夎繃鏈熸竻鐞嗙瓥鐣?
### 28.3 甯歌閿欒閫熸煡

| 閿欒 | 鍘熷洜 | 淇 |
|------|------|------|
| AI 蹇界暐绯荤粺鎸囦护 | SystemMessage 浣嶇疆涓嶅 | 纭繚鍦ㄧ涓€鏉?|
| 宸ュ叿璋冪敤缁撴灉鏈娇鐢?| tool_call_id 涓嶅尮閰?| 妫€鏌?ID 涓€鑷存€?|
| 瀵硅瘽瓒婃潵瓒婃參 | 鍘嗗彶娑堟伅澶 | 鍚敤淇壀 |
| 鎴愭湰瓒呴鏈?| token 鐢ㄩ噺澶辨帶 | 鐩戞帶+淇壀 |
| 娴佸紡杈撳嚭鍗￠】 | chunk 绱Н闂 | 妫€鏌ユ嫾鎺ラ€昏緫 |
| 鍘嗗彶娑堟伅涓㈠け | 瀛樺偍鍚庣閰嶇疆閿?| 妫€鏌ユ枃浠?鏁版嵁搴撹矾寰?|

---

> 馃帗 **鏈€缁堟€荤粨**锛歀angChain 娑堟伅浣撶郴鏄璇濆簲鐢ㄧ殑鍩虹煶銆備粠鍏娑堟伅绫诲瀷鐨勬纭娇鐢紝鍒?MessageChunk 鐨勬祦寮忔嫾鎺ワ紝鍐嶅埌 ChatMessageHistory 鐨勬寔涔呭寲绠＄悊锛屾渶鍚庡埌涓婁笅鏂囩獥鍙ｇ殑淇壀鍜屾憳瑕佲€斺€旀瘡涓€灞傞兘鏈夋渶浣冲疄璺点€傛帉鎻¤繖浜涳紝浣犲氨鑳芥瀯寤轰粠绠€鍗曡亰澶╁埌澶嶆潅 Agent 鐨勫悇绉嶅璇濆簲鐢ㄣ€?

---

## 浜屽崄涔濄€佹秷鎭綋绯?FAQ 琛ュ厖

### Q6: 娑堟伅鍙互宓屽娑堟伅鍚楋紵

**绛?*锛氫笉鑳界洿鎺ュ祵濂楋紝浣嗗彲浠ュ湪 content 涓寘鍚粨鏋勫寲鏁版嵁銆傛瘮濡?ToolMessage 鐨?content 鍙互鏄?JSON 瀛楃涓诧紝鍖呭惈澶嶆潅鐨勫伐鍏锋墽琛岀粨鏋溿€?
### Q7: 濡備綍璁＄畻涓€鏉℃秷鎭殑 token 鏁帮紵

**绛?*锛氱敤 tiktoken锛?```python
import tiktoken
encoding = tiktoken.encoding_for_model("gpt-4")
token_count = len(encoding.encode(message.content))
```

### Q8: 娴佸紡杈撳嚭涓浣曡幏鍙栧伐鍏疯皟鐢紵

**绛?*锛欰IMessageChunk 鐨?additional_kwargs 涓細鏈?tool_call_chunks锛岄渶瑕佺疮绉捣鏉ャ€?
### Q9: 澶氳疆瀵硅瘽涓浣曠鐞嗙敤鎴风殑涓婁笅鏂囩獥鍙ｏ紵

**绛?*锛氱粍鍚堢瓥鐣モ€斺€斺憼 淇濈暀 SystemMessage 鈶?淇濈暀鏈€杩?N 杞畬鏁村璇?鈶?鏇存棭鐨勫璇濈敤 LLM 鎽樿 鈶?瓒呴檺鏃惰嚜鍔ㄨЕ鍙戞憳瑕併€?
### Q10: ChatMessage 鍜?HumanMessage 鍙互浜掓崲鍚楋紵

**绛?*锛氫笉瀹屽叏鍙互銆侰hatMessage 鐨?role 鏄嚜瀹氫箟鐨勶紝鑰?HumanMessage 鐨?type 鍥哄畾涓?"human"銆傚ぇ澶氭暟妯″瀷鍙璇嗘爣鍑嗙殑 human/ai/system 瑙掕壊銆?
---

## 涓夊崄銆佹秷鎭綋绯绘湳璇〃

| 鏈 | 鑻辨枃 | 瑙ｉ噴 |
|------|------|------|
| **娑堟伅** | Message | 瀵硅瘽涓殑涓€鏉¤褰?|
| **娑堟伅鍧?* | MessageChunk | 娴佸紡杈撳嚭鐨勬秷鎭墖娈?|
| **瀵硅瘽鍘嗗彶** | Chat History | 瀹屾暣瀵硅瘽璁板綍 |
| **淇壀** | Trimming | 绉婚櫎鏃ф秷鎭?|
| **鎽樿** | Summarization | 鍘嬬缉鏃у璇濅负鎽樿 |
| **Token 璁℃暟** | Token Count | 璁＄畻 token 鏁伴噺 |
| **宸ュ叿璋冪敤** | Tool Call | AI 鍐冲畾璋冪敤澶栭儴宸ュ叿 |
| **宸ュ叿缁撴灉** | Tool Result | 宸ュ叿鎵ц鐨勮繑鍥炲€?|
| **涓婁笅鏂囩獥鍙?* | Context Window | 妯″瀷鑳藉鐞嗙殑鏈€澶?token 鏁?|
| **绯荤粺鎻愮ず** | System Prompt | 瀹氫箟 AI 瑙掕壊鐨勬寚浠?|

---

> 馃搶 **缁撴潫璇?*锛氭秷鎭綋绯绘槸 LangChain 鏈€鍩虹涔熸渶閲嶈鐨勬娊璞′箣涓€銆傛帉鎻″畠锛屼綘灏辨帉鎻′簡 LLM 瀵硅瘽搴旂敤鐨勪竴鍗娿€傚彟涓€鍗婃槸 Prompt 宸ョ▼鈥斺€旀垜浠皢鍦ㄤ笅涓€绡囨枃妗ｄ腑璇︾粏璁茶В銆?

---

## 闄勫綍锛氭秷鎭綋绯诲畬鏁翠唬鐮佺ず渚嬮泦

### A1. 瀹屾暣瀵硅瘽绠＄悊绫?
```python
# 绀轰緥 A1锛氬畬鏁寸殑瀵硅瘽绠＄悊绫?from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage,
    ToolMessage, trim_messages
)
from langchain_core.chat_history import InMemoryChatMessageHistory

class ConversationManager:
    """瀹屾暣鐨勫璇濈鐞嗗櫒"""

    def __init__(self, system_prompt: str, max_messages: int = 20):
        self.max_messages = max_messages
        self.history = InMemoryChatMessageHistory()
        self.history.add_message(SystemMessage(content=system_prompt))

    def add_user(self, content: str):
        self.history.add_user_message(content)
        self._trim()

    def add_ai(self, content: str):
        self.history.add_ai_message(content)
        self._trim()

    def add_tool(self, content: str, tool_call_id: str, name: str):
        self.history.add_message(ToolMessage(
            content=content, tool_call_id=tool_call_id, name=name
        ))

    def _trim(self):
        if len(self.history.messages) > self.max_messages:
            trimmed = trim_messages(
                self.history.messages,
                max_count=self.max_messages,
                include_system=True
            )
            self.history.messages = trimmed

    def get_messages(self):
        return self.history.messages

    def clear(self):
        self.history.clear()
```

### A2. 娴佸紡鑱婂ぉ绠＄悊鍣?
```python
# 绀轰緥 A2锛氭祦寮忚亰澶╃鐞嗗櫒
class StreamingChatManager:
    """鏀寔娴佸紡杈撳嚭鐨勮亰澶╃鐞嗗櫒"""

    def __init__(self):
        self.history = InMemoryChatMessageHistory()

    async def chat_stream(self, user_input: str, model):
        self.history.add_user_message(user_input)
        full_reply = ""

        async for chunk in model.astream(
            self.history.messages + [HumanMessage(content=user_input)]
        ):
            full_reply += chunk.content
            yield chunk.content

        self.history.add_ai_message(full_reply)
```

### A3. 澶氱敤鎴蜂細璇濈鐞?
```python
# 绀轰緥 A3锛氬鐢ㄦ埛浼氳瘽绠＄悊
class MultiUserSession:
    """澶氱敤鎴蜂細璇濈鐞嗗櫒"""

    def __init__(self):
        self.sessions = {}

    def get_or_create(self, user_id: str) -> ConversationManager:
        if user_id not in self.sessions:
            self.sessions[user_id] = ConversationManager(
                system_prompt="浣犳槸鍔╂墜"
            )
        return self.sessions[user_id]

    def chat(self, user_id: str, message: str) -> str:
        session = self.get_or_create(user_id)
        session.add_user(message)
        reply = f"鍥炲: {message}"  # 瀹為檯璋冪敤 LLM
        session.add_ai(reply)
        return reply

    def clear_user(self, user_id: str):
        if user_id in self.sessions:
            del self.sessions[user_id]
```

---

> 馃搶 **鏂囨。琛ュ厖璇存槑**锛氫互涓婁唬鐮佺ず渚嬩负娑堟伅浣撶郴鐨勫畬鏁村疄鎴樹唬鐮侊紝鍙洿鎺ョ敤浜庨」鐩紑鍙戝弬鑰冦€?

---

## 闄勫綍B锛氭秷鎭綋绯诲疄鎴樹唬鐮侀泦

### B1. 甯﹀伐鍏疯皟鐢ㄧ殑 Agent 寰幆

```python
# 绀轰緥 B1锛氬畬鏁寸殑 Agent 瀵硅瘽寰幆
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

class SimpleAgent:
    """绠€鍗曠殑宸ュ叿璋冪敤 Agent"""

    def __init__(self):
        self.messages = []

    def run(self, user_input: str, tools: dict):
        """杩愯 Agent 寰幆"""
        self.messages.append(HumanMessage(content=user_input))

        for step in range(5):  # 鏈€澶?姝?            # 妯℃嫙妯″瀷鍐崇瓥
            ai_decision = self._decide()
            self.messages.append(ai_decision)

            if not ai_decision.additional_kwargs.get("tool_calls"):
                break  # 娌℃湁宸ュ叿璋冪敤锛岀粨鏉?
            # 鎵ц宸ュ叿
            for tc in ai_decision.additional_kwargs["tool_calls"]:
                tool_name = tc["function"]["name"]
                result = tools[tool_name](tc["function"]["arguments"])
                self.messages.append(ToolMessage(
                    content=result,
                    tool_call_id=tc["id"],
                    name=tool_name
                ))

        return self.messages[-1].content

    def _decide(self):
        """妯℃嫙妯″瀷鍐崇瓥"""
        return AIMessage(content="鏈€缁堝洖绛?)
```

### B2. 娑堟伅鎽樿鐢熸垚鍣?
```python
# 绀轰緥 B2锛氬璇濇憳瑕佺敓鎴?from langchain_core.messages import HumanMessage, AIMessage

class ConversationSummarizer:
    """瀵硅瘽鎽樿鐢熸垚鍣?""

    def summarize(self, messages: list) -> str:
        """鐢熸垚瀵硅瘽鎽樿"""
        user_msgs = [m for m in messages if m.type == "human"]
        ai_msgs = [m for m in messages if m.type == "ai"]

        summary = f"瀵硅瘽鍏眥len(user_msgs)}杞€?
        if user_msgs:
            summary += f"棣栭棶锛歿user_msgs[0].content[:30]}銆?
        if ai_msgs:
            summary += f"娑夊強涓婚锛歿[m.content[:20] for m in ai_msgs[:3]]}"

        return summary
```

### B3. Token 棰勭畻绠＄悊鍣?
```python
# 绀轰緥 B3锛歍oken 棰勭畻绠＄悊鍣?import tiktoken

class TokenBudget:
    """绠＄悊瀵硅瘽鐨?token 棰勭畻"""

    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model("gpt-4")

    def count(self, messages: list) -> int:
        """璁＄畻娑堟伅鎬?token"""
        total = 0
        for m in messages:
            total += 4  # 鏍煎紡寮€閿€
            total += len(self.encoding.encode(m.content))
        return total + 2

    def fits(self, messages: list) -> bool:
        """鏄惁鍦ㄩ绠楀唴"""
        return self.count(messages) <= self.max_tokens

    def trim_to_fit(self, messages: list) -> list:
        """淇壀鍒伴绠楀唴"""
        system = [m for m in messages if m.type == "system"]
        others = [m for m in messages if m.type != "system"]

        kept = []
        total = 0
        for m in reversed(others):
            tokens = len(self.encoding.encode(m.content)) + 4
            if total + tokens <= self.max_tokens:
                kept.insert(0, m)
                total += tokens
        return system + kept
```

### B4. 娑堟伅鏍煎紡杞崲鍣?
```python
# 绀轰緥 B4锛氭秷鎭牸寮忚浆鎹㈠伐鍏?from langchain_core.messages import convert_to_messages

# 浠庡厓缁勮浆鎹?tuple_format = [("system", "浣犲ソ"), ("human", "闂")]
messages = convert_to_messages(tuple_format)

# 浠?OpenAI 鏍煎紡杞崲
openai_format = [
    {"role": "user", "content": "浣犲ソ"},
    {"role": "assistant", "content": "浣犲ソ锛?},
]
messages2 = convert_to_messages(openai_format)
```

---

> 馃搶 **鏂囨。琛ュ厖**锛氫互涓婇檮褰曚唬鐮佷负娑堟伅浣撶郴鐨勫疄鎴樺伐鍏风被锛屽彲鐩存帴鐢ㄤ簬椤圭洰寮€鍙戙€?

---

## 闄勫綍C锛氭秷鎭鐞嗗伐鍏峰嚱鏁伴泦

### C1. 娑堟伅楠岃瘉鍣?
```python
# 绀轰緥 C1锛氭秷鎭獙璇佸櫒
from langchain_core.messages import BaseMessage

class MessageValidator:
    """楠岃瘉娑堟伅鍒楄〃鐨勫畬鏁存€?""

    @staticmethod
    def validate(messages: list) -> list:
        """楠岃瘉娑堟伅鍒楄〃锛岃繑鍥炶鍛?""
        warnings = []

        # 妫€鏌ョ┖娑堟伅
        for i, m in enumerate(messages):
            if not m.content and not m.additional_kwargs:
                warnings.append(f"娑堟伅{i}鍐呭涓虹┖")

        # 妫€鏌ヨ繛缁悓瑙掕壊
        for i in range(1, len(messages)):
            if messages[i].type == messages[i-1].type:
                warnings.append(f"杩炵画涓ゆ潯{messages[i].type}娑堟伅")

        # 妫€鏌ュ伐鍏疯皟鐢ㄩ厤瀵?        tool_calls = set()
        for m in messages:
            if m.type == "ai" and m.additional_kwargs.get("tool_calls"):
                for tc in m.additional_kwargs["tool_calls"]:
                    tool_calls.add(tc["id"])
            elif m.type == "tool":
                tool_calls.discard(m.tool_call_id)

        if tool_calls:
            warnings.append(f"鏈厤瀵圭殑宸ュ叿璋冪敤: {tool_calls}")

        return warnings
```

### C2. 娑堟伅鏍煎紡鍖栧櫒

```python
# 绀轰緥 C2锛氭秷鎭牸寮忓寲宸ュ叿
class MessageFormatter:
    """娑堟伅鏍煎紡鍖栧伐鍏?""

    ROLE_EMOJI = {
        "system": "鈿欙笍",
        "human": "馃懁",
        "ai": "馃",
        "tool": "馃敡",
    }

    @classmethod
    def format_console(cls, messages: list) -> str:
        """鎺у埗鍙版牸寮忓寲杈撳嚭"""
        lines = []
        for m in messages:
            emoji = cls.ROLE_EMOJI.get(m.type, "馃摑")
            content = m.content[:80] if isinstance(m.content, str) else str(m.content)[:80]
            lines.append(f"{emoji} {m.type}: {content}")
        return "\n".join(lines)

    @classmethod
    def format_markdown(cls, messages: list) -> str:
        """Markdown 鏍煎紡杈撳嚭"""
        lines = []
        for m in messages:
            lines.append(f"**{m.type}**: {m.content}")
        return "\n\n".join(lines)
```

### C3. 娑堟伅杩囨护鍣?
```python
# 绀轰緥 C3锛氭秷鎭繃婊ゅ櫒
class MessageFilter:
    """娑堟伅杩囨护鍣?""

    @staticmethod
    def by_type(messages: list, types: list) -> list:
        """鎸夌被鍨嬭繃婊?""
        return [m for m in messages if m.type in types]

    @staticmethod
    def recent(messages: list, n: int) -> list:
        """鏈€杩?N 鏉?""
        return messages[-n:] if n < len(messages) else messages

    @staticmethod
    def without_tools(messages: list) -> list:
        """鍘绘帀宸ュ叿娑堟伅"""
        return [m for m in messages if m.type not in ("tool", "function")]
```

---

> 馃搶 浠ヤ笂宸ュ叿鍑芥暟鍙洿鎺ョ敤浜庨」鐩紑鍙戙€?

---

## 闄勫綍D锛氭秷鎭綋绯荤患鍚堝疄鎴樷€斺€旀櫤鑳藉鏈嶇郴缁熷畬鏁村疄鐜?
### D1. 绯荤粺鏋舵瀯

```mermaid
graph TD
    U[鐢ㄦ埛杈撳叆] --> N[鎰忓浘璇嗗埆]
    N -->|閫€娆緗 R[閫€娆炬祦绋媇
    N -->|鐗╂祦| S[鐗╂祦鏌ヨ]
    N -->|浜у搧| P[浜у搧鍜ㄨ]
    N -->|鎶曡瘔| C[鎶曡瘔澶勭悊]
    N -->|鍏朵粬| G[閫氱敤瀹㈡湇]
    R --> F[鏍煎紡鍖栧洖澶峕
    S --> F
    P --> F
    C --> F
    G --> F
    F --> U
```

### D2. 瀹屾暣浠ｇ爜

```python
# 绀轰緥 D2锛氭櫤鑳藉鏈嶇郴缁?from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.chat_history import InMemoryChatMessageHistory

class CustomerServiceBot:
    """鏅鸿兘瀹㈡湇鏈哄櫒浜?""

    def __init__(self):
        self.history = InMemoryChatMessageHistory()
        self.history.add_message(SystemMessage(
            content="浣犳槸鐢靛晢瀹㈡湇銆傜ぜ璨屼笓涓氾紝瑙ｅ喅鐢ㄦ埛闂銆?
        ))

    def detect_intent(self, message: str) -> str:
        """鎰忓浘璇嗗埆"""
        if any(w in message for w in ["閫€娆?, "閫€璐?]):
            return "refund"
        elif any(w in message for w in ["鐗╂祦", "蹇€?]):
            return "shipping"
        elif any(w in message for w in ["鎶曡瘔", "宸瘎"]):
            return "complaint"
        return "general"

    def handle(self, message: str) -> str:
        """澶勭悊鐢ㄦ埛娑堟伅"""
        self.history.add_user_message(message)
        intent = self.detect_intent(message)

        responses = {
            "refund": "姝ｅ湪涓烘偍杞帴閫€娆句笓鍛?..",
            "shipping": "姝ｅ湪鏌ヨ鐗╂祦淇℃伅...",
            "complaint": "闈炲父鎶辨瓑锛佸凡涓烘偍璁板綍鎶曡瘔銆?,
            "general": "鏀跺埌鎮ㄧ殑闂锛屾鍦ㄨВ绛?..",
        }

        reply = responses.get(intent, "鎮ㄥソ锛佽闂湁浠€涔堝彲浠ュ府鎮紵")
        self.history.add_ai_message(reply)
        return reply

    def get_history(self):
        return self.history.messages
```

### D3. 浣跨敤绀轰緥

```python
# 绀轰緥 D3锛氫娇鐢ㄥ鏈嶇郴缁?bot = CustomerServiceBot()

print(bot.handle("鎴戣閫€娆?))
print(bot.handle("鎴戠殑蹇€掑埌鍝簡"))
print(bot.handle("浣犱滑鏈嶅姟澶樊浜嗭紒"))
print(bot.handle("浣犱滑鍑犵偣涓婄彮"))

print("\n=== 瀵硅瘽鍘嗗彶 ===")
for msg in bot.get_history():
    print(f"  {msg.type}: {msg.content}")
```

---

> 馃搶 浠ヤ笂涓烘秷鎭綋绯诲湪鏅鸿兘瀹㈡湇涓殑瀹屾暣瀹炴垬瀹炵幇銆?

---

## 闄勫綍E锛氭秷鎭皟璇曚笌璇婃柇宸ュ叿

### E1. 娑堟伅璋冭瘯鍣?
```python
# 绀轰緥 E1锛氭秷鎭皟璇曞伐鍏?class MessageDebugger:
    """娑堟伅璋冭瘯宸ュ叿"""

    @staticmethod
    def dump(messages: list, title: str = "娑堟伅鍒楄〃"):
        """瀹屾暣杞偍娑堟伅"""
        print(f"\n=== {title} ===")
        for i, m in enumerate(messages):
            print(f"\n[{i}] type={m.type}")
            print(f"    content: {repr(m.content[:100])}")
            if m.additional_kwargs:
                print(f"    kwargs: {m.additional_kwargs}")
            if m.response_metadata:
                print(f"    metadata: {m.response_metadata}")
            if hasattr(m, 'tool_call_id') and m.tool_call_id:
                print(f"    tool_call_id: {m.tool_call_id}")

    @staticmethod
    def stats(messages: list) -> dict:
        """缁熻娑堟伅淇℃伅"""
        from collections import Counter
        types = Counter(m.type for m in messages)
        total_chars = sum(len(m.content) for m in messages if isinstance(m.content, str))
        return {
            "total": len(messages),
            "by_type": dict(types),
            "total_chars": total_chars,
        }
```

### E2. 娑堟伅涓€鑷存€ф鏌ュ櫒

```python
# 绀轰緥 E2锛氭秷鎭竴鑷存€ф鏌?class MessageConsistencyChecker:
    """妫€鏌ユ秷鎭垪琛ㄧ殑涓€鑷存€?""

    @staticmethod
    def check(messages: list) -> list:
        issues = []

        # 妫€鏌ュ伐鍏疯皟鐢ㄩ厤瀵?        called = set()
        returned = set()
        for m in messages:
            if m.type == "ai" and m.additional_kwargs.get("tool_calls"):
                for tc in m.additional_kwargs["tool_calls"]:
                    called.add(tc["id"])
            if m.type == "tool":
                returned.add(m.tool_call_id)

        if called - returned:
            issues.append(f"鏈繑鍥炵粨鏋滅殑璋冪敤: {called - returned}")
        if returned - called:
            issues.append(f"鏃犺皟鐢ㄧ殑缁撴灉: {returned - called}")

        return issues
```

---

> 馃搶 浠ヤ笂璋冭瘯宸ュ叿鍙敤浜庢帓鏌ユ秷鎭浉鍏抽棶棰樸€?

---

## 闄勫綍F锛氭秷鎭綋绯讳笌 LangGraph 闆嗘垚瀹炴垬

### F1. LangGraph 涓殑娑堟伅绠＄悊

```python
# 绀轰緥 F1锛歀angGraph 娑堟伅鐘舵€?from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END

class ChatState(TypedDict):
    """瀵硅瘽鐘舵€佲€斺€旀秷鎭嚜鍔?reducer"""
    messages: Annotated[list[BaseMessage], add_messages]

# 鍒涘缓鍥?graph = StateGraph(ChatState)

# 鑺傜偣鍑芥暟
def chat_node(state: ChatState) -> dict:
    """澶勭悊瀵硅瘽"""
    return {"messages": [("ai", "浣犲ソ锛?)]}

graph.add_node("chat", chat_node)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

# compiled = graph.compile()
```

### F2. 娑堟伅鎸佷箙鍖栧湪 LangGraph 涓?
```python
# 绀轰緥 F2锛歀angGraph 娑堟伅鎸佷箙鍖?# from langgraph.checkpoint.memory import MemorySaver
#
# checkpointer = MemorySaver()
# graph = builder.compile(checkpointer=checkpointer)
#
# # 鑷姩淇濆瓨鍜屾仮澶嶅璇濈姸鎬?# config = {"configurable": {"thread_id": "user_123"}}
# result = graph.invoke(inputs, config=config)
```

### F3. 娑堟伅淇壀鍦?LangGraph 涓?
```python
# 绀轰緥 F3锛歀angGraph 涓殑娑堟伅淇壀
from langchain_core.messages import trim_messages

def should_trim(state: ChatState) -> bool:
    """鍒ゆ柇鏄惁闇€瑕佷慨鍓?""
    return len(state["messages"]) > 20

def trim_node(state: ChatState) -> dict:
    """淇壀娑堟伅鑺傜偣"""
    trimmed = trim_messages(
        state["messages"],
        max_count=15,
        include_system=True
    )
    return {"messages": trimmed}
```

---

## 闄勫綍G锛氭秷鎭綋绯绘湳璇〃

| 鏈 | 鑻辨枃 | 瑙ｉ噴 |
|------|------|------|
| 娑堟伅 | Message | 瀵硅瘽涓殑涓€鏉¤褰?|
| 娑堟伅鍧?| MessageChunk | 娴佸紡娑堟伅鐗囨 |
| 瀵硅瘽鍘嗗彶 | Chat History | 瀹屾暣瀵硅瘽 |
| 淇壀 | Trimming | 绉婚櫎鏃ф秷鎭?|
| 鎽樿 | Summarization | 鍘嬬缉瀵硅瘽 |
| Token | Token | 妯″瀷澶勭悊鍗曚綅 |
| 宸ュ叿璋冪敤 | Tool Call | AI 璋冪敤宸ュ叿 |
| 宸ュ叿缁撴灉 | Tool Result | 宸ュ叿杩斿洖鍊?|
| 涓婁笅鏂囩獥鍙?| Context Window | 鏈€澶ц緭鍏ラ暱搴?|
| 绯荤粺鎻愮ず | System Prompt | 瑙掕壊瀹氫箟 |

---

## 闄勫綍H锛氭秷鎭綋绯绘渶浣冲疄璺垫竻鍗?
- [ ] SystemMessage 鏀惧璇濈涓€鏉?- [ ] ToolMessage 鐨?tool_call_id 绮剧‘鍖归厤
- [ ] 娴佸紡杈撳嚭鐢?chunk 鎷兼帴
- [ ] 鐢熶骇鐜鐢?Redis/SQL 瀛樺偍
- [ ] 闀垮璇濊嚜鍔ㄤ慨鍓?- [ ] 鐩戞帶 token 鐢ㄩ噺
- [ ] 搴忓垪鍖栦繚鐣?type 瀛楁
- [ ] 澶氱敤鎴锋寜 user_id 闅旂
- [ ] 瀵硅瘽鏈夎繃鏈熸竻鐞嗙瓥鐣?- [ ] 娑堟伅鏍煎紡鏈夐獙璇?

---

## 闄勫綍I锛氭秷鎭綋绯诲父瑙侀敊璇€熸煡琛?
| 閿欒鐜拌薄 | 鍙兘鍘熷洜 | 瑙ｅ喅鏂规 |
|---------|---------|---------|
| KeyError: 'xxx' | 鍙橀噺鏈畾涔?| 妫€鏌?input_variables |
| TypeError: content 绫诲瀷閿?| content 鏄垪琛ㄤ笉鏄?str | 鐢?extract_text 鎻愬彇 |
| tool_call_id 涓嶅尮閰?| ToolMessage 鍏宠仈閿?| 妫€鏌?ID 涓€鑷存€?|
| 瀵硅瘽瓒婃潵瓒婃參 | 鍘嗗彶澶暱 | 鍚敤淇壀 |
| 骞昏涓ラ噸 | 娌℃湁绾︽潫 | 鍔?涓嶇煡閬撳氨璇翠笉鐭ラ亾" |
| 娴佸紡杈撳嚭涓嶅畬鏁?| chunk 绱Н閿?| 妫€鏌ユ嫾鎺ラ€昏緫 |
| 鍘嗗彶娑堟伅涓㈠け | 瀛樺偍閰嶇疆閿?| 妫€鏌ユ枃浠?鏁版嵁搴撹矾寰?|
| Token 瓒呴檺 | 鎻愮ず璇嶅お闀?| 淇壀/鎽樿/鍘嬬缉 |
| 妯″瀷涓嶇悊瑙ｈ鑹?| SystemMessage 浣嶇疆閿?| 纭繚鍦ㄧ涓€鏉?|
| 澶氱敤鎴蜂覆璇?| user_id 鏈殧绂?| 鎸?user_id 鍒嗕細璇?|

---

## 闄勫綍J锛氭秷鎭綋绯诲涔犺祫婧?
| 璧勬簮 | 璇存槑 |
|------|------|
| LangChain 瀹樻柟鏂囨。 | 娑堟伅绫诲瀷 API 鍙傝€?|
| LangChain GitHub | 婧愮爜鍜岀ず渚?|
| LangSmith | 瀵硅瘽杩借釜鍜屽垎鏋?|
| OpenAI Cookbook | 瀵硅瘽璁捐鏈€浣冲疄璺?|
| 绀惧尯鏁欑▼ | 瀹炴垬缁忛獙鍒嗕韩 |

---

## 闄勫綍K锛氭秷鎭綋绯荤増鏈巻鍙?
| 鐗堟湰 | 鍙樺寲 |
|------|------|
| 0.1 | 鍩虹娑堟伅绫诲瀷 |
| 0.2 | 鏂板 ToolMessage |
| 0.2 | MessageChunk 鏀硅繘 |
| 0.3 | 澶氭ā鎬?content |
| 0.3 | 娑堟伅 id 灞炴€?|

---

> 馃搶 鏂囨。缁撴潫銆傛秷鎭綋绯绘槸 LangChain 瀵硅瘽鑳藉姏鐨勫熀鐭筹紝鎸佺画瀹炶返鍜屽涔犳槸鎺屾彙瀹冪殑鍏抽敭銆?

---

## 闄勫綍L锛氭秷鎭鐞嗗畬鏁村伐鍏峰簱

### L1. 娑堟伅缁熻涓庡垎鏋?
```python
# 绀轰緥 L1锛氭秷鎭粺璁″垎鏋愬伐鍏?from collections import Counter

class MessageAnalytics:
    """娑堟伅缁熻鍒嗘瀽"""

    @staticmethod
    def by_type(messages: list) -> dict:
        """鎸夌被鍨嬬粺璁?""
        return dict(Counter(m.type for m in messages))

    @staticmethod
    def avg_length(messages: list) -> float:
        """骞冲潎娑堟伅闀垮害"""
        lengths = [len(m.content) for m in messages if isinstance(m.content, str)]
        return sum(lengths) / len(lengths) if lengths else 0

    @staticmethod
    def tool_call_stats(messages: list) -> dict:
        """宸ュ叿璋冪敤缁熻"""
        calls = 0
        results = 0
        for m in messages:
            if m.type == "ai" and m.additional_kwargs.get("tool_calls"):
                calls += len(m.additional_kwargs["tool_calls"])
            elif m.type == "tool":
                results += 1
        return {"calls": calls, "results": results}
```

### L2. 娑堟伅瀵煎嚭宸ュ叿

```python
# 绀轰緥 L2锛氭秷鎭鍑哄伐鍏?import json
from langchain_core.messages import messages_to_dict

class MessageExporter:
    """娑堟伅瀵煎嚭"""

    @staticmethod
    def to_json(messages: list, path: str):
        """瀵煎嚭涓?JSON"""
        data = messages_to_dict(messages)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def to_text(messages: list) -> str:
        """瀵煎嚭涓虹函鏂囨湰"""
        lines = []
        for m in messages:
            lines.append(f"[{m.type}] {m.content}")
        return "\n".join(lines)
```

### L3. 娑堟伅瀵规瘮宸ュ叿

```python
# 绀轰緥 L3锛氭秷鎭姣斿伐鍏?class MessageComparer:
    """瀵规瘮涓ょ粍娑堟伅"""

    @staticmethod
    def diff(msgs1: list, msgs2: list) -> dict:
        """瀵规瘮宸紓"""
        return {
            "len1": len(msgs1),
            "len2": len(msgs2),
            "added": len(msgs2) - len(msgs1),
        }
```

---

> 馃搶 浠ヤ笂宸ュ叿搴撳彲鐩存帴鐢ㄤ簬娑堟伅鍒嗘瀽鍜屽鐞嗐€?

---

## 闄勫綍M锛氭秷鎭綋绯诲畬鏁村疄鎴樷€斺€斾紒涓氱骇鑱婂ぉ鏈哄櫒浜?
### M1. 绯荤粺璁捐

```mermaid
graph TB
    U[鐢ㄦ埛] --> API[FastAPI鎺ュ彛]
    API --> Auth[璁よ瘉]
    Auth --> Session[浼氳瘽绠＄悊]
    Session --> History[瀵硅瘽鍘嗗彶<br/>Redis瀛樺偍]
    History --> Bot[瀵硅瘽寮曟搸]
    Bot --> Model[LLM]
    Bot --> Tools[宸ュ叿闆哴
    History --> Monitor[鐩戞帶]
```

### M2. 鏍稿績浠ｇ爜

```python
# 绀轰緥 M2锛氫紒涓氱骇鑱婂ぉ鏈哄櫒浜烘牳蹇?from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

class EnterpriseChatBot:
    """浼佷笟绾ц亰澶╂満鍣ㄤ汉"""

    def __init__(self):
        self.sessions = {}
        self.system_prompt = "浣犳槸浼佷笟鍔╂墜銆備笓涓氥€佸噯纭€?

    def get_session(self, session_id: str) -> InMemoryChatMessageHistory:
        """鑾峰彇浼氳瘽"""
        if session_id not in self.sessions:
            h = InMemoryChatMessageHistory()
            h.add_message(SystemMessage(content=self.system_prompt))
            self.sessions[session_id] = h
        return self.sessions[session_id]

    def chat(self, session_id: str, message: str) -> str:
        """瀵硅瘽"""
        history = self.get_session(session_id)
        history.add_user_message(message)
        reply = f"鍥炲: {message}"  # 瀹為檯璋冪敤 LLM
        history.add_ai_message(reply)
        return reply

    def clear(self, session_id: str):
        """娓呴櫎浼氳瘽"""
        if session_id in self.sessions:
            del self.sessions[session_id]
```

### M3. 浼氳瘽缁熻

```python
# 绀轰緥 M3锛氫細璇濈粺璁?class SessionStats:
    """浼氳瘽缁熻"""

    def __init__(self):
        self.sessions = {}

    def record(self, session_id: str, message_count: int):
        """璁板綍浼氳瘽"""
        self.sessions[session_id] = message_count

    def summary(self) -> dict:
        """姹囨€?""
        total = len(self.sessions)
        avg = sum(self.sessions.values()) / total if total else 0
        return {"total_sessions": total, "avg_messages": avg}
```

---

> 馃搶 浠ヤ笂涓轰紒涓氱骇鑱婂ぉ鏈哄櫒浜虹殑鏍稿績瀹炵幇妗嗘灦銆?

---

## 闄勫綍R锛氭秷鎭綋绯诲畬鏁村疄鎴樷€斺€斿杞璇濈郴缁?
### R1. 绯荤粺鏋舵瀯

```mermaid
graph TB
    U[鐢ㄦ埛] --> I[杈撳叆澶勭悊]
    I --> H[鍘嗗彶绠＄悊]
    H --> P[鎻愮ず璇嶆瀯寤篯
    P --> M[妯″瀷璋冪敤]
    M --> O[杈撳嚭瑙ｆ瀽]
    O --> U
    H --> S[瀛樺偍]
```

### R2. 鏍稿績浠ｇ爜

```python
# 绀轰緥 R2锛氬杞璇濈郴缁熸牳蹇?from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import trim_messages

class MultiTurnChat:
    """澶氳疆瀵硅瘽绯荤粺"""

    def __init__(self, system_prompt: str = "浣犳槸鍔╂墜", max_turns: int = 10):
        self.max_turns = max_turns
        self.history = InMemoryChatMessageHistory()
        self.history.add_message(SystemMessage(content=system_prompt))

    def chat(self, user_input: str) -> str:
        """瀵硅瘽涓€杞?""
        self.history.add_user_message(user_input)
        self._trim()

        # 妯℃嫙妯″瀷鍥炲
        reply = f"鏀跺埌: {user_input}"
        self.history.add_ai_message(reply)
        return reply

    def _trim(self):
        """淇壀鍘嗗彶"""
        msgs = self.history.messages
        if len(msgs) > self.max_turns * 2:
            self.history.messages = trim_messages(
                msgs, max_count=self.max_turns * 2,
                include_system=True
            )

    def clear(self):
        self.history.clear()
```

### R3. 浣跨敤绀轰緥

```python
# 绀轰緥 R3锛氫娇鐢ㄥ璇濈郴缁?chat = MultiTurnChat(system_prompt="浣犳槸Python涓撳")
print(chat.chat("浠€涔堟槸鍒楄〃锛?))
print(chat.chat("鎬庝箞閬嶅巻锛?))
print(chat.chat("鎺ㄥ寮忔€庝箞鍐欙紵"))
```

---

> 馃搶 浠ヤ笂涓哄杞璇濈郴缁熺殑瀹屾暣瀹炵幇銆?

---

## 闄勫綍S锛氭秷鎭綋绯讳笌鍥炶皟闆嗘垚

### S1. 娑堟伅鍥炶皟

```python
# 绀轰緥 S1锛氭秷鎭洖璋?from langchain_core.callbacks import BaseCallbackHandler

class MessageCallback(BaseCallbackHandler):
    """娑堟伅鍥炶皟澶勭悊鍣?""

    def on_chat_model_start(self, serialized, messages, **kwargs):
        """妯″瀷寮€濮嬪鐞?""
        print(f"寮€濮嬪鐞?{len(messages[0])} 鏉℃秷鎭?)

    def on_llm_end(self, response, **kwargs):
        """妯″瀷瀹屾垚"""
        print(f"鐢熸垚: {response.generations[0][0].text[:50]}...")
```

### S2. 娑堟伅鐩戞帶

```python
# 绀轰緥 S2锛氭秷鎭洃鎺?class MessageMonitor:
    """娑堟伅鐩戞帶"""

    def __init__(self):
        self.message_count = 0
        self.total_tokens = 0

    def on_message_added(self, message):
        """娑堟伅娣诲姞鏃?""
        self.message_count += 1
```

---

## 闄勫綍T锛氭秷鎭綋绯绘湳璇€熸煡

| 缂╁啓 | 鍏ㄧО | 瑙ｉ噴 |
|------|------|------|
| LLM | Large Language Model | 澶ц瑷€妯″瀷 |
| RAG | Retrieval-Augmented Generation | 妫€绱㈠寮虹敓鎴?|
| Agent | AI Agent | AI 鏅鸿兘浣?|
| Tool | Function Calling | 宸ュ叿璋冪敤 |
| Chunk | MessageChunk | 娑堟伅鍧?|
| Token | Token | 妯″瀷澶勭悊鍗曚綅 |

---

> 馃搶 浠ヤ笂涓烘秷鎭綋绯荤殑鍥炶皟闆嗘垚鍜屾湳璇€熸煡銆?

---

## 闄勫綍U锛氭秷鎭綋绯绘渶缁堟€荤粨

### 鏍稿績瑕佺偣鍥為【

| 涓婚 | 涓€鍙ヨ瘽鎬荤粨 |
|------|-----------|
| BaseMessage | 鎵€鏈夋秷鎭殑鍩虹被 |
| 6绉嶆秷鎭?| Human/AI/System/Tool/Function/Chat |
| 娑堟伅灞炴€?| content + additional_kwargs + metadata + id |
| MessageChunk | 娴佸紡娑堟伅鐗囨 |
| 搴忓垪鍖?| to_dict / from_dict |
| ChatHistory | 瀵硅瘽鍘嗗彶瀛樺偍 |
| 淇壀 | trim_messages 鎺у埗闀垮害 |
| 鎽樿 | 鍘嬬缉闀垮璇?|
| Token璁℃暟 | 鎺у埗涓婁笅鏂囩獥鍙?|

### 瀛︿範寤鸿

1. **鍔ㄦ墜瀹炶返**锛氬啓浠ｇ爜娴嬭瘯姣忕娑堟伅绫诲瀷
2. **鐞嗚В瑙掕壊**锛氫笉鍚岃鑹叉湁涓嶅悓鐢ㄩ€?3. **鐢熶骇鎬濈淮**锛氳€冭檻瀛樺偍銆佹墿灞曘€佺洃鎺?4. **鎸佺画瀛︿範**锛歀angChain 蹇€熷彂灞?
---

## 闄勫綍V锛氭秷鎭綋绯诲揩閫熶笂鎵嬩唬鐮?
```python
# 绀轰緥 V锛氬揩閫熶笂鎵?from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 鍒涘缓娑堟伅
msgs = [
    SystemMessage(content="浣犳槸鍔╂墜"),
    HumanMessage(content="浣犲ソ"),
    AIMessage(content="浣犲ソ锛?),
]

# 搴忓垪鍖?import json
data = [{"type": m.type, "content": m.content} for m in msgs]
print(json.dumps(data, ensure_ascii=False))
```

---

> 馃搶 鏂囨。鍒版缁撴潫銆傛劅璋㈤槄璇伙紒


---

## 闄勫綍W锛氭秷鎭綋绯诲弬鑰冭祫婧?
### 瀹樻柟璧勬簮
- LangChain 瀹樻柟鏂囨。锛歨ttps://python.langchain.com
- GitHub 浠撳簱锛歨ttps://github.com/langchain-ai/langchain
- LangSmith 鐩戞帶骞冲彴锛歨ttps://smith.langchain.com

### 鎺ㄨ崘闃呰
- 銆夿uilding LLM Applications銆?- 銆奓angChain in Action銆?- OpenAI Function Calling 鎸囧崡

### 绀惧尯
- LangChain Discord 绀惧尯
- GitHub Discussions
- Stack Overflow 鏍囩 langchain

---

## 闄勫綍X锛氭秷鎭綋绯绘枃妗ｇ増鏈?
| 鐗堟湰 | 鏃ユ湡 | 璇存槑 |
|------|------|------|
| 1.0 | 2026-09-09 | 鍒濆鐗堟湰 |

---

> 馃帗 **鍏ㄦ枃瀹?*锛氭劅璋㈤槄璇昏繖浠藉叧浜?LangChain 娑堟伅浣撶郴鐨勬繁搴︽枃妗ｃ€傚笇鏈涘畠鑳藉府鍔╀綘鍦?LLM 搴旂敤寮€鍙戜腑寰楀績搴旀墜銆?

---

## 闄勫綍Y锛氭秷鎭綋绯昏ˉ鍏呯煡璇嗙偣

### 娑堟伅 ID 鐨勪綔鐢?
姣忎釜娑堟伅鏈変竴涓敮涓€鐨?id 灞炴€э紝鐢ㄤ簬锛?- 杩借釜娑堟伅鏉ユ簮
- 娴佸紡杈撳嚭鏃剁殑鎺掑簭
- 宸ュ叿璋冪敤鐨勯厤瀵?
```python
# 绀轰緥锛氬甫 ID 鐨勬秷鎭?from langchain_core.messages import HumanMessage

msg = HumanMessage(content="浣犲ソ", id="msg_001")
print(msg.id)  # msg_001
```

### 娑堟伅鐨勪笉鍙彉鎬?
娑堟伅瀵硅薄鍒涘缓鍚庯紝閫氬父涓嶅簲璇ヤ慨鏀广€傚鏋滈渶瑕佷慨鏀癸紝搴旇鍒涘缓鏂扮殑娑堟伅銆?
```python
# 姝ｇ‘鍋氭硶锛氬垱寤烘柊娑堟伅
old_msg = HumanMessage(content="浣犲ソ")
new_msg = HumanMessage(content="浣犲ソ锛?)
```

### 澶氳疆瀵硅瘽涓殑娑堟伅椤哄簭

娑堟伅椤哄簭寰堥噸瑕佲€斺€旀ā鍨嬩緷璧栭『搴忕悊瑙ｅ璇濄€備笉瑕侀殢鎰忛噸鎺掓秷鎭€?
---

> 馃搶 浠ヤ笂涓烘秷鎭綋绯荤殑琛ュ厖鐭ヨ瘑鐐广€?

---

## 闄勫綍Z锛氭秷鎭綋绯诲父瑙侀棶棰樻渶缁堣В绛?
### Q: 浠€涔堟椂鍊欑敤 HumanMessage 浠€涔堟椂鍊欑敤 SystemMessage锛?绛旓細SystemMessage 鐢ㄤ簬瀹氫箟瑙掕壊鍜岃鍒欙紝HumanMessage 鐢ㄤ簬鐢ㄦ埛杈撳叆銆係ystem 鏀剧涓€鏉°€?
### Q: 娴佸紡杈撳嚭鏃跺浣曠疮绉秷鎭紵
绛旓細鐢?AIMessageChunk.accumulate() 鎴栨墜鍔ㄦ嫾鎺?content銆?
### Q: 濡備綍鍒ゆ柇瀵硅瘽鏄惁澶暱锛?绛旓細璁＄畻 token 鏁帮紝瓒呰繃妯″瀷涓婁笅鏂囩獥鍙ｇ殑 80% 灏卞簲璇ヤ慨鍓€?
### Q: 澶氱敤鎴峰浣曢殧绂伙紵
绛旓細鎸?user_id/session_id 鍒嗗埆瀛樺偍鍘嗗彶銆傛瘡涓敤鎴蜂竴涓嫭绔嬬殑 ChatHistory銆?
### Q: 娑堟伅鍙互璺ㄨ澶囧悓姝ュ悧锛?绛旓細鍙互銆傜敤 File/Redis/SQL 瀛樺偍锛屼笉鍚岃澶囪鍙栧悓涓€浠藉巻鍙层€?
---

> 馃搶 浠ヤ笂涓烘秷鎭綋绯荤殑鏈€缁堝父瑙侀棶棰樿В绛斻€?

---

## 闄勫綍AA锛氭秷鎭綋绯绘渶缁堟€荤粨鍗＄墖

```
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?  LangChain Message 鏍稿績鎬荤粨     鈹?鈹溾攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?鍩虹被: BaseMessage               鈹?鈹?绫诲瀷: Human/AIMessage/System/   鈹?鈹?      Tool/Function/Chat        鈹?鈹?瀛樺偍: InMemory/File/Redis/SQL   鈹?鈹?绠＄悊: 淇壀/鎽樿/Token璁℃暟       鈹?鈹?娴佸紡: MessageChunk 绱Н         鈹?鈹?瀹炴垬: 澶氳疆瀵硅瘽/Agent/RAG        鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?```

### 鍏抽敭鏁板瓧

| 鎸囨爣 | 鍊?|
|------|-----|
| 娑堟伅绫诲瀷 | 6绉?|
| 瀛樺偍鏂规 | 5绉?|
| 绠＄悊绛栫暐 | 3绉?|
| 浠ｇ爜绀轰緥 | 120+ |

---

> 馃帗 鏂囨。缁撴潫銆?
