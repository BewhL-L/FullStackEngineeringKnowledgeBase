---
title: LangChain-Memory记忆机制
tags: [LangChain, Memory, 对话记忆, 长期记忆, 向量记忆]
category: AI与效率工具
created: 2026-09-09
updated: 2026-09-09
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[LangChain-核心抽象与链]]", "[[LangChain-Message消息类型与对话历史]]", "[[Agent记忆机制设计]]", "[[LLM大模型入门概念]]"]
aliases: [LangChain记忆, ConversationMemory, 对话记忆]
---

# LangChain Memory 记忆机制

> **一句话定义**：Memory 是 LangChain 中负责**存储、检索和管理对话历史**的核心抽象，它让 LLM 应用具备"记得之前说过什么"的能力，从而支撑多轮对话、上下文理解和个性化交互。
>
> **核心价值**：将"对话历史"这一可变状态从 Prompt 模板和模型调用中解耦——开发者无需手动拼接历史消息、无需关心 Token 窗口管理、无需自己实现摘要压缩，只需选择合适的 Memory 策略，框架自动完成历史的注入、保存、修剪与持久化。
>
> **适用场景**：多轮对话机器人、客服系统、个人助理、RAG 问答上下文记忆、Agent 长期状态管理、有状态的工作流。

---

## 一、概述：记忆到底在解决什么问题

### 1.1 通俗比喻：Memory 就是 AI 的"记事本"

把 LLM 想象成一个**记忆力只有 24 小时的天才顾问**——他智商极高、反应极快，但每次对话结束就会"失忆"，不记得你昨天聊过什么。Memory 就是你给他准备的**记事本**：

- **每次对话前**，你把记事本上相关的几页翻给他看（`load_memory_variables` 加载历史）；
- **每次对话后**，你把新发生的一问一问答抄到记事本上（`save_context` 保存本轮）；
- **记事本有厚度上限**（上下文 Token 窗口有限），所以你得想办法决定"哪些留着、哪些丢掉、哪些浓缩成摘要"。

不同的 Memory 实现，本质上就是**不同的"记事本管理策略"**：有的整本照抄、有的只抄最近几页、有的把旧的浓缩成摘要、有的按人物/实体做笔记、有的把整本做成"索引卡片"按需翻找。

### 1.2 为什么 LLM 需要外部记忆

LLM 本身是**无状态（stateless）**的——每次 API 调用都是独立的，模型不会自动记住上一次调用的内容。所有"记忆"必须由应用层在每次请求时**重新塞进 Prompt**。

```mermaid
graph LR
    subgraph 无状态的LLM调用
        Q1[第1次请求<br/>问题A+历史] --> L1[LLM]
        L1 --> A1[回答A]
        Q2[第2次请求<br/>问题B+历史+回答A] --> L2[LLM]
        L2 --> A2[回答B]
    end
    style Q1 fill:#e3f2fd
    style Q2 fill:#fff3e0
```

**关键结论**：所谓"对话记忆"，99% 是**应用层把历史消息拼进下一次 Prompt** 的工程问题，而不是模型真的"记住了"。Memory 抽象就是为了自动化这件事。

### 1.3 记忆的核心概念一览

| 概念 | 说明 | 类比 |
|------|------|------|
| **input_key / output_key** | 标识用户输入和 AI 输出的字段名 | 记事本上"问""答"两栏的标签 |
| **memory_key** | 历史变量在 Prompt 中的占位符名 | 记事本插入到提示词的位置 |
| **return_messages** | 是否返回消息对象列表（而非字符串） | 用结构化消息还是纯文本记录 |
| **chat_memory** | 底层消息存储（BaseChatMessageHistory） | 记事本的"物理纸张" |
| **moving_summary_buffer** | 滚动摘要缓冲区 | 笔记本末尾的"浓缩摘要页" |
| **max_token_limit** | 触发摘要/修剪的 Token 阈值 | 记事本厚度上限 |
| **k / window** | 窗口记忆保留的轮数 | 只保留最近 K 轮 |
| **session_id** | 多会话隔离的标识 | 多个不同客户各自的记事本 |

### 1.4 记忆分类总览图

```mermaid
graph TB
    MEM[Memory 记忆体系]
    MEM --> SHORT[短期记忆<br/>对话窗口内]
    MEM --> LONG[长期记忆<br/>跨会话持久化]

    SHORT --> B[ConversationBufferMemory<br/>完整缓冲]
    SHORT --> BW[ConversationBufferWindowMemory<br/>窗口缓冲]
    SHORT --> S[ConversationSummaryMemory<br/>LLM摘要]
    SHORT --> SB[ConversationSummaryBufferMemory<br/>摘要+缓冲]

    LONG --> E[ConversationEntityMemory<br/>实体记忆]
    LONG --> KG[ConversationKGMemory<br/>知识图谱记忆]
    LONG --> V[VectorStoreRetrieverMemory<br/>向量检索记忆]
    LONG --> EXT[外部服务记忆<br/>Motorhead / Zep]

    style MEM fill:#ede7f6
    style SHORT fill:#e3f2fd
    style LONG fill:#e8f5e9
```

### 1.5 Memory 在 LangChain 中的演进

| 阶段 | 形态 | 说明 |
|------|------|------|
| **v0.1 旧版** | `ConversationChain` + Memory 对象 | 记忆作为 Chain 的属性，自动注入 |
| **v0.2 过渡** | `RunnableWithMessageHistory` | 用 LCEL + 消息历史做有状态链 |
| **现代推荐** | 直接管理消息列表 + LangGraph 状态 | 记忆 = 显式状态，开发者完全掌控 |

> ⚠️ **重要提醒**：新版 LangChain（0.2+）中，`langchain.memory` 下的许多类属于**兼容/遗留 API**。生产新项目强烈推荐使用 `RunnableWithMessageHistory` 或将消息历史显式管理在链状态中（尤其配合 LangGraph）。本文为了知识体系完整，会同时讲解经典 Memory 类与现代做法，并在每处标注推荐程度。

> 🔍 **知识点深度解析**
>
> **作用**：Memory 把"对话历史的存取与整理"封装成标准化组件，让多轮对话的构建从"手写字符串拼接"变成"配置一个策略对象"。
>
> **原理**：所有 Memory 都围绕两个核心方法工作——`load_memory_variables(inputs)` 在调用链**之前**被调用，把历史以 `{memory_key: 历史}` 的形式注入 Prompt；`save_context(inputs, outputs)` 在调用链**之后**被调用，把本轮的用户输入和模型输出追加到底层消息历史。中间是否做窗口截断、是否做摘要压缩、是否做实体抽取，就是不同子类的差异所在。
>
> **用法要点**：① 先明确"要保留多少、保留多细"再选 Memory 类型；② `return_messages=True` 配合 `MessagesPlaceholder` 是聊天模型的标准姿势；③ `memory_key` 必须与 Prompt 占位符一致；④ 多用户场景必须用 `session_id` 隔离；⑤ 生产环境把历史落到 Redis/DB，不要用内存字典。

---

> 💡 **深度讲解**：理解 Memory 的关键是抓住"**记忆 = 历史消息的可插拔整理器**"这条主线。LLM 的上下文窗口是稀缺资源（既有限额又贵），而对话会无限增长，于是产生了"信息压缩"这个永恒矛盾。完整缓冲（Buffer）最忠实但最贵；窗口缓冲（Window）只看最近、最便宜但会遗忘；摘要（Summary）用 LLM 把旧历史压缩成一段文字，是"摘要 vs 原文"的经典权衡；实体/知识图谱/向量检索则更进一步——它们不再"按时间顺序记流水账"，而是"按信息的语义和结构重新组织记忆"，这正是从"对话记忆"走向"Agent 长期记忆"的方向。外部记忆服务（Zep、Motorhead）则把记忆本身变成一个独立的微服务，解决多实例部署下的状态共享问题。
>
> **📝 精简总结**：Memory 解决 LLM 无状态问题，把对话历史在每次请求时注入 Prompt；核心方法是 `load_memory_variables`（调用前加载）与 `save_context`（调用后保存）；分类上短期记忆含 Buffer/Window/Summary/SummaryBuffer，长期记忆含 Entity/KG/VectorStore/外部服务；新版推荐 `RunnableWithMessageHistory` 或显式状态管理；选型核心是"记忆精度 × Token 成本 × 遗忘程度"的三角权衡。

---

## 二、原理：BaseMemory 与 BaseChatMemory 基类

### 2.1 BaseMemory：记忆的抽象根类

`BaseMemory` 是所有记忆的抽象基类，它定义了记忆最本质的两个契约。

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseMemory(ABC):
    """所有 Memory 的抽象基类"""

    @abstractmethod
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """调用链之前被调用：返回要注入 Prompt 的历史变量。

        Returns:
            形如 {"history": "..."} 的字典，key 即 memory_key
        """
        pass

    @abstractmethod
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """调用链之后被调用：保存本轮对话。"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """清空所有记忆。"""
        pass

    @property
    @abstractmethod
    def memory_variables(self) -> List[str]:
        """该记忆会暴露哪些变量名。"""
        pass
```

**三个必须理解的契约**：

```python
# 契约1：load_memory_variables 的输入是"用户本次的原始输入"
# 某些记忆（如 EntityMemory）会用它来决定加载哪些相关实体
memory.load_memory_variables({"input": "帮我查查张三的订单"})

# 契约2：save_context 的两个参数
# inputs 是用户本轮输入字典，outputs 是模型本轮输出字典
memory.save_context(
    inputs={"input": "我叫李四"},
    outputs={"output": "你好，李四！"}
)

# 契约3：memory_variables 声明暴露的变量，供框架校验 Prompt 是否需要它
print(memory.memory_variables)  # ['history']
```

### 2.2 BaseChatMemory：聊天记忆的中间层

`BaseChatMemory` 继承自 `BaseMemory`，它引入了**底层消息历史存储** `chat_memory`，把"存消息"和"整理消息"两件事分开。

```python
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage

class BaseChatMemory(BaseMemory):
    """聊天记忆的中间层：持有一个消息历史存储"""

    chat_memory: BaseChatMessageMemory  # 底层存储（可换成 Redis/DB）
    output_key: str | None = None        # 模型输出在 outputs 字典里的 key
    input_key: str | None = None         # 用户输入在 inputs 字典里的 key
    return_messages: bool = False         # 返回字符串还是消息列表

    def save_context(self, inputs, outputs) -> None:
        # 1. 从 inputs 里提取用户输入
        _input = inputs[self.input_key] if self.input_key else self._get_input(inputs)
        # 2. 从 outputs 里提取模型输出
        _output = outputs[self.output_key] if self.output_key else self._get_output(outputs)
        # 3. 追加到底层消息历史
        self.chat_memory.add_user_message(_input)
        self.chat_memory.add_ai_message(_output)
```

**设计精髓：职责分离**

```mermaid
graph LR
    A[Memory 子类<br/>决定如何整理] -->|读写| B[chat_memory<br/>BaseChatMessageHistory<br/>决定存在哪]
    B --> C[InMemoryHistory<br/>内存列表]
    B --> D[RedisChatMessageHistory<br/>Redis]
    B --> E[SQLChatMessageHistory<br/>数据库]
    B --> F[FileChatMessageHistory<br/>文件]
```

这意味着：**"记忆策略"和"记忆存储"是正交的两个维度**。你可以用"摘要策略"搭配"Redis 存储"，也可以用"窗口策略"搭配"数据库存储"，自由组合。

### 2.3 BaseChatMessageHistory：底层消息存储

`BaseChatMessageHistory` 负责最朴素的"存消息、取消息、清消息"，它不做任何整理。

```python
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage

class BaseChatMessageHistory(ABC):
    messages: List[BaseMessage]  # 当前会话的全部消息

    @abstractmethod
    def add_user_message(self, message: str) -> None: ...
    @abstractmethod
    def add_ai_message(self, message: str) -> None: ...
    def add_message(self, message: BaseMessage) -> None: ...  # 新版统一接口
    @abstractmethod
    def clear(self) -> None: ...
```

**常用的现成实现**：

```python
# 1. 内存存储（最快，重启即失）
from langchain_core.chat_history import InMemoryChatMessageHistory
history = InMemoryChatMessageHistory()
history.add_user_message("你好")
history.add_ai_message("你好！有什么可以帮你？")
print(history.messages)
# [HumanMessage(content='你好'), AIMessage(content='你好！...')]

# 2. 文件存储（简单持久化）
from langchain_community.chat_message_histories import FileChatMessageHistory
file_history = FileChatMessageHistory("chat_session_001.json")
file_history.add_user_message("持久化的消息")

# 3. Redis 存储（生产推荐，支持多实例共享）
from langchain_community.chat_message_histories import RedisChatMessageHistory
redis_history = RedisChatMessageHistory(
    session_id="user_123",
    url="redis://localhost:6379/0",
    ttl=3600 * 24 * 7  # 保留7天
)

# 4. SQL 数据库存储
from langchain_community.chat_message_histories import SQLChatMessageHistory
sql_history = SQLChatMessageHistory(
    session_id="user_456",
    connection_string="sqlite:///chat.db"
)
```

### 2.4 消息类型体系

```python
from langchain_core.messages import (
    SystemMessage,      # 系统指令
    HumanMessage,       # 用户消息
    AIMessage,          # 模型消息
    FunctionMessage,    # 函数调用结果（旧）
    ToolMessage,        # 工具调用结果（新）
    AIMessageChunk,     # 流式分块
)

# 一条结构化的对话长这样
messages = [
    SystemMessage(content="你是一个客服助手"),
    HumanMessage(content="我的订单还没发货"),
    AIMessage(content="请问订单号是多少？"),
    HumanMessage(content="ORD-10086"),
    AIMessage(content="已查到，预计明天送达"),
]
```

| 消息类型 | 角色 | 用途 |
|----------|------|------|
| `SystemMessage` | system | 设定人设、规则、格式约束 |
| `HumanMessage` | user | 用户输入 |
| `AIMessage` | assistant | 模型回复 |
| `ToolMessage` | tool | 工具执行结果回传给模型 |

### 2.5 记忆的输入输出数据流

```mermaid
sequenceDiagram
    participant U as 用户
    participant Mem as Memory
    participant Prompt as Prompt模板
    participant LLM as 模型

    Note over Mem: 本轮开始
    U->>Mem: 本轮输入 input="订单到哪了"
    Mem->>Mem: load_memory_variables() 读取历史
    Mem-->>Prompt: 注入 history=[...上几轮...]
    Prompt->>LLM: 渲染完整Prompt(含历史+本轮)
    LLM-->>Mem: 输出 answer
    Mem->>Mem: save_context(input, answer)
    Mem-->>U: 返回 answer
```

---

> 💡 **深度讲解**：BaseMemory 与 BaseChatMemory 的分层设计，体现了 LangChain "**组合优于继承**" 的核心哲学。如果只有一个 Memory 类，那么"完整缓冲/窗口/摘要/实体"每加一种策略都要同时重写"怎么存"；分层之后，"怎么存"被收敛到 `chat_memory`（可插拔的存储后端），"怎么整理"留给各个 Memory 子类去实现。这就是为什么你能写出 `ConversationSummaryMemory(chat_memory=RedisChatMessageHistory(...))` 这样的组合——策略和存储正交。另一个容易被忽略的细节是 `input_key` / `output_key` 的自动推断：当你的链有多个输入字段时，如果不显式指定，框架会"猜"哪一个是用户输入，猜错了记忆就会存错东西。生产环境建议**永远显式指定 `input_key` 和 `output_key`**。
>
> **📝 精简总结**：BaseMemory 定义 `load_memory_variables`/`save_context`/`clear`/`memory_variables` 四个契约；BaseChatMemory 引入 `chat_memory` 把"存储"与"整理"解耦；BaseChatMessageHistory 是底层消息存储，有 InMemory/File/Redis/SQL 等多种实现；消息类型含 System/Human/AI/Tool；数据流是"调用前加载历史→渲染Prompt→调用模型→调用后保存本轮"；多输入场景务必显式指定 input_key/output_key。

---

## 三、实操：八大记忆类型逐个吃透

### 3.1 ConversationBufferMemory —— 完整缓冲（全量照抄）

**通俗理解**：最老实的记事本，你说一句它抄一句，一字不落。

```python
from langchain.memory import ConversationBufferMemory

# 基础用法
memory = ConversationBufferMemory()

# 第一轮对话
memory.save_context({"input": "你好，我叫张三"}, {"output": "你好张三！"})
memory.save_context({"input": "我在做电商运营"}, {"output": "电商运营很有前景！"})

# 查看加载出来的历史变量
print(memory.load_memory_variables({}))
# {'history': 'Human: 你好，我叫张三\nAI: 你好张三！\nHuman: 我在做电商运营\nAI: 电商运营很有前景！'}
```

**返回字符串 vs 返回消息列表**：

```python
# 方式A：return_messages=False（默认），返回拼接字符串
mem_str = ConversationBufferMemory(return_messages=False)
mem_str.save_context({"input": "hi"}, {"output": "hello"})
print(type(mem_str.load_memory_variables({})["history"]))  # <class 'str'>

# 方式B：return_messages=True，返回消息列表（聊天模型推荐）
mem_msgs = ConversationBufferMemory(return_messages=True)
mem_msgs.save_context({"input": "hi"}, {"output": "hello"})
hist = mem_msgs.load_memory_variables({})["history"]
print(type(hist))        # <class 'list'>
print(type(hist[0]))     # <class 'langchain_core.messages.human.HumanMessage'>
```

**指定 memory_key 与 key 名**：

```python
memory = ConversationBufferMemory(
    memory_key="chat_history",   # Prompt 里用 {chat_history} 占位
    input_key="user_query",      # 明确输入字段
    output_key="ai_reply",       # 明确输出字段
    return_messages=True
)
memory.save_context({"user_query": "今天天气如何"}, {"ai_reply": "晴转多云"})
print(memory.load_memory_variables({}).keys())  # dict_keys(['chat_history'])
```

**完整对话示例（手动版）**：

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
memory = ConversationBufferMemory(return_messages=True, memory_key="history")

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的助手"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chain = prompt | llm | StrOutputParser()

def chat(user_input: str) -> str:
    # 1. 加载历史
    vars_ = memory.load_memory_variables({})
    # 2. 调用链
    answer = chain.invoke({"history": vars_["history"], "input": user_input})
    # 3. 保存本轮
    memory.save_context({"input": user_input}, {"output": answer})
    return answer

print(chat("我叫王五，是做服装电商的"))
print(chat("我刚才说我是做什么的？"))  # 能答出"服装电商"
```

**优点与代价**：

| 维度 | 评价 |
|------|------|
| 记忆完整度 | ★★★★★ 一字不漏 |
| Token 成本 | ★☆☆☆☆ 随轮数线性增长，易爆上下文 |
| 遗忘风险 | 无（但会爆窗口） |
| 适用轮数 | 短对话（<10 轮） |

### 3.2 ConversationBufferWindowMemory —— 窗口缓冲（只留最近 K 轮）

**通俗理解**：记事本只写最新的 K 页，前面写满了就把最老的撕掉。

```python
from langchain.memory import ConversationBufferWindowMemory

# k=2 表示只保留最近 2 轮对话（一问一答算一轮的话是2对）
memory = ConversationBufferWindowMemory(k=2, return_messages=True)

# 连续聊 5 轮
dialogues = [
    ("第一轮问题", "第一轮回答"),
    ("第二轮问题", "第二轮回答"),
    ("第三轮问题", "第三轮回答"),
    ("第四轮问题", "第四轮回答"),
    ("第五轮问题", "第五轮回答"),
]
for q, a in dialogues:
    memory.save_context({"input": q}, {"output": a})

# 只保留最近 k=2 轮（4条消息）
hist = memory.load_memory_variables({})["history"]
print(f"保留了 {len(hist)} 条消息")  # 4
for m in hist:
    print(m.content)
# 第三轮问题 / 第三轮回答 / 第四轮问题 / 第四轮回答 / 第五轮问题 / 第五轮回答
```

**k 值的权衡实验**：

```python
for k in [1, 2, 3, 5]:
    mem = ConversationBufferWindowMemory(k=k)
    for i in range(10):
        mem.save_context({"input": f"问题{i}"}, {"output": f"回答{i}"})
    h = mem.load_memory_variables({})["history"]
    print(f"k={k} -> 历史长度约 {len(h.split(chr(10)))} 行")
```

**带链的完整窗口对话**：

```python
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
memory = ConversationBufferWindowMemory(k=3)

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

conversation.predict(input="你好，我叫赵六")
conversation.predict(input="我喜欢打篮球")
conversation.predict(input="我今年25岁")
# 此时再问"我叫什么、喜欢什么"，由于k=3全部在窗口内都记得
```

> ⚠️ **坑点**：窗口记忆的"轮"和"条"要分清。`k=2` 在 `return_messages=True` 时通常保留 **2 个"问答对" = 4 条消息**（2 Human + 2 AI）。如果你的对话包含 system 消息或工具消息，它们不会自动计入窗口，需要自己额外处理。

### 3.3 ConversationSummaryMemory —— LLM 摘要记忆（浓缩旧历史）

**通俗理解**：笔记本太厚了，于是让 AI 帮你把前面聊过的内容**概括成一段小作文**，只带这篇小作文去见下一次对话。

```python
from langchain.memory import ConversationSummaryMemory
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

memory = ConversationSummaryMemory(
    llm=llm,
    return_messages=True,
    memory_key="summary"
)

memory.save_context({"input": "我叫张三，今年28岁"}, {"output": "你好张三！"})
memory.save_context({"input": "我在杭州做跨境电商"}, {"output": "杭州跨境电商很发达"})
memory.save_context({"input": "主营3C配件"}, {"output": "3C配件市场需求大"})

# 历史被压缩成一段摘要，而不是逐条消息
print(memory.load_memory_variables({})["summary"])
# 示例输出："用户介绍自己叫张三，28岁，在杭州从事跨境电商，主营3C配件。"
```

**摘要是怎么随对话"滚动更新"的**：

```mermaid
graph LR
    A[已有摘要] --> C{新对话到来}
    B[新一问一答] --> C
    C --> D[LLM: 把旧摘要+新对话合并成新摘要]
    D --> E[更新摘要buffer]
    E --> A
```

**关键参数与 Prompt**：

```python
memory = ConversationSummaryMemory(
    llm=llm,
    prompt=ConversationSummaryMemory.prompt,  # 可自定义摘要提示词
    return_messages=False,
)

# 查看默认摘要提示词
from langchain.chains.conversation.prompt import SUMMARY_PROMPT
print(SUMMARY_PROMPT.template)
# 包含 "Progressively summarize the lines of conversation provided..."
```

**自定义摘要 Prompt**：

```python
from langchain_core.prompts import PromptTemplate

custom_summary_prompt = PromptTemplate.from_template("""
请把以下对话进展总结成简洁的中文笔记，保留关键事实（人名、年龄、职业、偏好）：
现有摘要：{summary}
新对话：
Human: {new_lines}
AI: {new_lines_ai}
新摘要：""")

memory = ConversationSummaryMemory(llm=llm, prompt=custom_summary_prompt)
```

> ⚠️ **坑点1：每次 save_context 都调一次 LLM**。摘要记忆每存一轮就会用 LLM 重新压缩一次摘要，**成本和延迟翻倍**（每次对话 = 2 次模型调用：一次回答、一次摘要）。高频场景慎用。
>
> ⚠️ **坑点2：摘要会丢细节**。"张三在杭州西湖区文三路398号做亚马逊欧洲站"可能被压成"张三做跨境电商"，精确数字/地址信息会丢失。

### 3.4 ConversationSummaryBufferMemory —— 摘要+缓冲混合（甜点方案）

**通俗理解**：近期的对话**原文照抄**（细节不丢），一旦超过 Token 阈值，**再往前的才压成摘要**。这是工业界最常用的平衡方案。

```python
from langchain.memory import ConversationSummaryBufferMemory

memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=200,   # 超过200 token就把最早的压成摘要
    return_messages=True,
    memory_key="history"
)

# 前几轮直接保留原文
memory.save_context({"input": "你好"}, {"output": "你好！"})
# ... 持续对话直到超过 max_token_limit
# 触发后：早期对话 -> 摘要 buffer；近期对话 -> 原文保留
```

**内部结构解剖**：

```python
# SummaryBufferMemory 内部有两个部分：
# 1. moving_summary_buffer：滚动摘要（旧对话的浓缩）
# 2. chat_memory.messages：近期原文消息

# 加载历史时的拼装顺序：
# [摘要作为一条 SystemMessage] + [近期原文消息列表]

# 触发条件：len(chat_memory.messages) 的 token 估算 > max_token_limit
# 触发动作：把最早的 (n) 条消息交给 LLM 合并进 moving_summary_buffer
```

**实际观察它的混合形态**：

```python
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=50, return_messages=True)

samples = [
    ("我叫孙七", "你好孙七"),
    ("我喜欢养猫", "猫很可爱"),
    ("我家有两只英短", "英短性格温顺"),
    ("一只叫年糕一只叫团子", "名字很可爱"),
]
for q, a in samples:
    memory.save_context({"input": q}, {"output": a})

loaded = memory.load_memory_variables({})["history"]
# 前几条：早期对话被压成的 SystemMessage
# 后几条：最近的原文 Human/AI Message
for msg in loaded:
    print(f"[{type(msg).__name__}]: {msg.content[:50]}")
```

**完整对话应用**：

```python
from langchain.chains import ConversationChain

conversation = ConversationChain(
    llm=llm,
    memory=ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=300,
        return_messages=True
    ),
    verbose=True
)

# 长对话场景：既记得住最近的细节，又不会撑爆上下文
conversation.predict(input="先简单介绍一下你自己吧")
# ... 持续多轮，自动在摘要与原文间平衡
```

| 记忆类型 | 保留近期细节 | 保留长期事实 | Token 成本 | 推荐度 |
|----------|--------------|--------------|------------|--------|
| Buffer | ✅ 全部 | ✅ 全部 | 高 | 短对话 |
| Window | ✅ 最近K轮 | ❌ 会遗忘 | 低 | 闲聊 |
| Summary | ❌ 全部压缩 | 部分保留 | 中(每次摘要) | 超长对话 |
| **SummaryBuffer** | ✅ 近期原文 | ✅ 旧的有摘要 | 中 | **⭐生产推荐** |

---

> 💡 **深度讲解**：Buffer 系（3.1/3.2）和 Summary 系（3.3/3.4）代表了记忆设计的两条哲学路线。Buffer 系是"**原文主义**"——相信模型自己能从原文里找重点，问题是原文越积越多、成本失控；Summary 系是"**压缩主义**"——相信 LLM 的概括能力，问题是压缩必然有损。SummaryBuffer 是两者的工程折中：它用一个 Token 计数器做"哨兵"，未达阈值就原样保留（无损），一旦越线就把最老的一段交给 LLM 合并进滚动摘要（有损但有序）。这种"阈值触发式压缩"和操作系统的虚拟内存换页、Redis 的内存淘汰策略异曲同工。选型时记住一个经验法则：**对话平均轮数 < 10 用 Buffer；10~50 用 SummaryBuffer；> 50 且需要跨会话用向量/实体记忆**。
>
> **📝 精简总结**：ConversationBufferMemory 全量照抄、最忠实但贵；WindowMemory 只留最近 k 轮、便宜但会忘；SummaryMemory 用 LLM 把旧对话滚成摘要、长对话不爆窗但有损且每轮多一次LLM调用；SummaryBufferMemory 是混合甜点——近期原文+远期摘要，靠 max_token_limit 触发压缩，生产首选；return_messages=True 时配合 MessagesPlaceholder 注入消息列表。

---
### 3.5 ConversationEntityMemory —— 实体记忆（按"人/事/物"做笔记）

**通俗理解**：记事本不按时间流水账记，而是**给每个提到的关键人物/事物单独开一页**，专门记录关于它的所有事实。下次聊到这个人，就把这一页翻出来。

```python
from langchain.memory import ConversationEntityMemory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Faiss

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

memory = ConversationEntityMemory(
    llm=llm,
    chat_history_key="history",
    input_key="input"
)

# 聊到多个实体
memory.save_context({"input": "张三是我的大学同学，现在在字节跳动工作"},
                    {"output": "了解了"})
memory.save_context({"input": "李四是我的同事，负责供应链"},
                    {"output": "好的"})

# 加载时：会自动抽取"当前对话涉及哪些实体"，并取出这些实体的笔记
loaded = memory.load_memory_variables({"input": "张三最近怎么样"})
print(loaded["entities"])   # {'张三': '在字节跳动工作', '李四': '负责供应链'}
print(loaded["history"])
```

**实体记忆的内部流程**：

```mermaid
graph TB
    A[新对话] --> B[LLM抽取: 本段提到哪些实体?]
    B --> C{实体已存在?}
    C -->|是| D[取出该实体旧笔记]
    C -->|否| E[新建实体条目]
    D --> F[LLM: 把新信息合并进实体笔记]
    E --> F
    F --> G[更新实体字典]
    G --> H[Prompt注入: 相关实体笔记 + 对话历史]
```

**自定义实体抽取与总结 Prompt**：

```python
from langchain_core.prompts import PromptTemplate

# 自定义"抽取实体"的提示词
ENTITY_EXTRACTION_PROMPT = PromptTemplate.from_template("""
从以下对话中抽取所有关键实体（人名、公司、产品、地点）。
只输出实体名，逗号分隔。

对话：{history}
当前输入：{input}
实体列表：""")

# 自定义"总结实体笔记"的提示词
ENTITY_SUMMARY_PROMPT = PromptTemplate.from_template("""
根据新对话，更新关于 {entity} 的笔记。
现有笔记：{summary}
新对话：{input} -> {output}
更新后的笔记：""")

memory = ConversationEntityMemory(
    llm=llm,
    entity_extraction_prompt=ENTITY_EXTRACTION_PROMPT,
    entity_summarization_prompt=ENTITY_SUMMARY_PROMPT,
)
```

**带向量库的实体记忆（实体笔记也可检索）**：

```python
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Faiss.from_texts(["初始化"], embeddings)

memory = ConversationEntityMemory(
    llm=llm,
    entity_cache=vectorstore,  # 实体笔记存入向量库，支持语义检索
)
```

**完整实体对话链**：

```python
from langchain.chains import ConversationChain

conversation = ConversationChain(
    llm=llm,
    memory=ConversationEntityMemory(llm=llm),
    verbose=True
)

conversation.predict(input="我叫王五，在腾讯做产品经理")
conversation.predict(input="我女朋友叫赵雨，是个设计师")
# 下次问"我女朋友是做什么的"，实体记忆能从"赵雨"这一页翻出"设计师"
```

> ⚠️ **坑点**：实体记忆每轮也要调 LLM 做抽取和合并，成本高；且实体名归一化是难点——"张三""小张""张先生"会被当成三个实体。生产中通常配合实体链接（Entity Linking）做归一。

### 3.6 ConversationKGMemory —— 知识图谱记忆（三元组记忆）

**通俗理解**：比实体记忆更进一步——不只记"关于张三的笔记"，而是把知识存成**主谓宾三元组**（张三-职业-工程师），像一张知识图谱。

```python
from langchain.memory import ConversationKGMemory

memory = ConversationKGMemory(
    llm=llm,
    input_key="input",
    return_messages=True
)

memory.save_context(
    {"input": "张三在字节跳动担任工程师，他毕业于清华大学"},
    {"output": "好的"}
)

# 加载时抽取与当前输入相关的三元组
loaded = memory.load_memory_variables({"input": "张三的教育背景"})
print(loaded["history"])
# 形如：[("张三", "毕业于", "清华大学"), ("张三", "任职于", "字节跳动")]
```

**知识图谱三元组结构**：

```mermaid
graph LR
    ZS[张三] -->|职业| ENG[工程师]
    ZS -->|任职于| BYTED[字节跳动]
    ZS -->|毕业于| THU[清华大学]
    ZS -->|同事| LS[李四]
    LS -->|负责| SCM[供应链]
```

**自定义 KG 抽取 Prompt**：

```python
from langchain.chains.conversation.prompt import ENTITY_EXTRACTION_PROMPT

# 默认会让 LLM 输出 (head, relation, tail) 三元组
# 可自定义抽取格式
custom_kg_prompt = PromptTemplate.from_template("""
从对话中抽取知识三元组，格式为 (头实体, 关系, 尾实体)。
对话：{history}
当前：{input}
三元组列表：""")

memory = ConversationKGMemory(
    llm=llm,
    prompt=custom_kg_prompt,
)
```

**KG 记忆 vs 实体记忆对比**：

| 维度 | ConversationEntityMemory | ConversationKGMemory |
|------|--------------------------|----------------------|
| 存储结构 | 实体 -> 自由文本笔记 | (头, 关系, 尾) 三元组 |
| 结构化程度 | 半结构化 | 强结构化 |
| 关系推理 | 弱 | 强（可沿关系遍历） |
| 实现复杂度 | 中 | 高 |
| 适用 | 记"关于某人的事" | 记"实体间的关系网络" |

### 3.7 VectorStoreRetrieverMemory —— 向量检索记忆（语义索引记忆）

**通俗理解**：把所有历史对话**向量化存进向量库**，下次对话时按"语义相似度"捞出最相关的几段历史，而不是按时间顺序。这是**长期记忆的主流方案**。

```python
from langchain.memory import VectorStoreRetrieverMemory
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# 1. 准备向量库
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    embedding_function=embeddings,
    persist_directory="./memory_vectors"
)

# 2. 转成 retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# 3. 包装成 Memory
memory = VectorStoreRetrieverMemory(
    retriever=retriever,
    memory_key="relevant_history",
    input_key="input"
)

# 4. 写入历史
memory.save_context({"input": "我们公司的退货政策是7天无理由"},
                    {"output": "已记录退货政策"})
memory.save_context({"input": "客服小王的工号是10086"},
                    {"output": "已记录"})

# 5. 下次提问时，按语义检索相关历史
loaded = memory.load_memory_variables({"input": "退货怎么处理？"})
print(loaded["relevant_history"])
# 自动捞出"退货政策"那一段，即使它是很早之前说的
```

**向量记忆的检索原理**：

```mermaid
graph LR
    Q[新问题: 退货怎么处理] --> E[Embedding向量化]
    E --> V[(向量库<br/>所有历史)]
    V --> S[余弦相似度 Top-K]
    S --> R[最相关的几段历史]
    R --> P[注入Prompt]
```

**完整 RAG 式对话记忆链**：

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from operator import itemgetter

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是客服助手。参考以下相关历史：\n{relevant_history}"),
    ("human", "{input}")
])

chain = (
    RunnableLambda(lambda x: {
        **x,
        "relevant_history": memory.load_memory_variables(x)["relevant_history"]
    })
    | prompt | llm
)

ans = chain.invoke({"input": "退货流程是什么"})
memory.save_context({"input": "退货流程是什么"}, {"output": ans.content})
```

**关键参数调优**：

```python
# k 控制召回条数
retriever = vectorstore.as_retriever(
    search_type="mmr",          # 最大边际相关性，兼顾多样与相关
    search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.5}
)

# 相似度阈值过滤
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.7}
)
```

> ⚠️ **坑点**：向量记忆检索的是"语义相似"而非"时间相关"，可能捞出无关但措辞相似的历史；且它不天然保留对话的时序上下文。通常与窗口记忆**组合使用**——向量记忆管"长期事实"，窗口记忆管"近期对话流"。

### 3.8 MotorheadMemory 与 ZepMemory —— 外部服务记忆

**通俗理解**：记忆不再存在你自己的进程里，而是交给一个**专门的记忆微服务**，它帮你做摘要、向量化、时序管理，你只管调 API。

#### MotorheadMemory

```python
from langchain.memory import MotorheadMemory

# Motorhead 是开源的记忆服务器（Docker 自部署）
memory = MotorheadMemory(
    session_id="user_abc",
    url="http://localhost:8080",   # Motorhead 服务地址
    memory_key="history",
    context_window_size=5          # 服务端自动摘要的窗口
)

# 用法和普通 Memory 一致
memory.save_context({"input": "你好"}, {"output": "你好！"})
print(memory.load_memory_variables({}))
```

**Motorhead 服务端能力**：

| 能力 | 说明 |
|------|------|
| 自动摘要 | 服务端自动滚动压缩历史 |
| 跨实例共享 | 多进程/多副本部署共享同一份记忆 |
| 持久化 | 自带存储，重启不丢 |
| 元数据 | 支持按 session 管理 |

#### ZepMemory

```python
from langchain_memory import ZepMemory  # 注意包名可能为 langchain_zep

# Zep 是一个长期记忆服务，自带知识图谱抽取与时序摘要
memory = ZepMemory(
    session_id="user_xyz",
    url="http://localhost:8000",
    api_key="...",
    memory_type="perpetual",   # 永久记忆
    return_messages=True
)

memory.save_context({"input": "我在做抖音美食赛道"}, {"output": "了解"})
loaded = memory.load_memory_variables({})
print(loaded["history"])  # Zep 已自动抽取实体、时间线、主题
```

**Zep 的高级特性**：

```python
# Zep 自动做的事：
# 1. 事实抽取（Fact Extraction）
# 2. 实体与主题识别
# 3. 时序线（Timeline）
# 4. 知识图谱自动构建
# 5. 冲突事实检测（用户改主意了会更新旧事实）

# 按"用户长期画像"查询
from zep_cloud import Zep
client = Zep(api_key="...")
user = client.user.get(user_id="user_xyz")
print(user.context)   # AI 整理出的用户画像摘要
```

**自部署 vs SaaS 记忆服务对比**：

| 维度 | 自部署 Motorhead | Zep Cloud | 自研向量记忆 |
|------|------------------|-----------|--------------|
| 部署成本 | 中（Docker） | 低（SaaS） | 高 |
| 自动摘要 | ✅ | ✅ | ❌ 需自己写 |
| 知识图谱 | ❌ | ✅ | ❌ |
| 数据合规 | 自建可控 | 数据出域 | 完全可控 |
| 适合 | 中小团队快速起步 | 不想运维 | 有定制需求 |

---

> 💡 **深度讲解**：从 Buffer 到 Entity/KG 再到 VectorStore/外部服务，记忆的演进主线是"**从时间序列到语义结构**"。早期记忆把对话当成一条时间线，问题是时间线越长、越靠后的信息越被"稀释"。Entity/KG 记忆意识到"对话里真正值得记的不是流水账，而是事实和关系"，于是转向结构化抽取。VectorStore 记忆则用一个更灵活的方案——不预设知识结构，直接把每段对话向量化，需要时按语义检索。这三者其实对应了人类记忆的不同侧面：时间线 = 情景记忆（episodic）、实体/KG = 语义记忆（semantic）、向量检索 = 联想记忆（associative）。生产上一个成熟的长期记忆系统往往是"**分层记忆**"：最上层是最近 N 轮原文（情景），中间是滚动摘要（语义压缩），底层是向量索引的全量历史（可检索）。Zep/Motorhead 这类服务把这套分层自动化了，代价是引入额外的服务依赖。
>
> **📝 精简总结**：EntityMemory 按实体单独记笔记，KGMemory 记(头-关系-尾)三元组，二者从流水账走向结构化事实；VectorStoreRetrieverMemory 把历史向量化、按语义召回，是长期记忆主流；Motorhead/Zep 是独立记忆微服务，自带自动摘要、知识图谱、跨实例共享；选型上短期对话用Buffer系，长期事实用向量/实体，分布式部署用外部记忆服务。

---

## 四、记忆与链的集成

### 4.1 旧版 ConversationChain（理解演进）

```python
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

chain = ConversationChain(
    llm=llm,
    memory=ConversationBufferMemory(),
    verbose=True
)

# 旧版：predict 自动处理记忆的 load + save
chain.predict(input="我叫周九")
chain.predict(input="我叫什么名字？")  # 记得
```

**ConversationChain 内部做了什么**：

```mermaid
graph LR
    A[输入] --> B[memory.load_memory_variables]
    B --> C[拼接Prompt: 历史+本轮]
    C --> D[LLM]
    D --> E[memory.save_context]
    E --> F[输出]
```

### 4.2 现代方式：RunnableWithMessageHistory（强烈推荐）

新版 LangChain 推荐用 `RunnableWithMessageHistory` 把消息历史挂到 LCEL 链上，它**自动**管理历史的加载与保存，且天然支持多会话（session_id）。

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

# 1. 基础 LCEL 链
model = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个助手"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])
chain = prompt | model | StrOutputParser()

# 2. 会话存储（生产换 Redis/SQL）
store = {}
def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# 3. 用 RunnableWithMessageHistory 包装
wrapped_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# 4. 调用时通过 config 传 session_id
wrapped_chain.invoke(
    {"input": "我叫吴十"},
    config={"configurable": {"session_id": "sess_001"}}
)
wrapped_chain.invoke(
    {"input": "我叫什么？"},
    config={"configurable": {"session_id": "sess_001"}}   # 记得吴十
)
# 另一个会话互不干扰
wrapped_chain.invoke(
    {"input": "我叫什么？"},
    config={"configurable": {"session_id": "sess_002"}}   # 不记得
)
```

**RunnableWithMessageHistory 工作原理**：

```mermaid
sequenceDiagram
    participant C as 客户端
    participant W as RunnableWithMessageHistory
    participant H as get_session_history
    participant Chain as 底层链

    C->>W: invoke({input}, config={session_id})
    W->>H: 取该 session 的历史
    H-->>W: messages=[...]
    W->>W: 把 messages 塞进 history_messages_key
    W->>Chain: invoke({input, history: messages})
    Chain-->>W: AI 回复
    W->>H: append(本轮 user + ai)
    W-->>C: 返回回复
```

### 4.3 多输入/多输出时的 key 指定

```python
# 当链有多个输入字段，必须用 input_messages_key 指明哪个是用户消息
wrapped_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",       # 用户消息字段
    history_messages_key="history",
    output_messages_key="answer",         # 模型输出字段（若输出是dict）
)
```

### 4.4 带窗口修剪的现代链（用 trim_messages）

新版推荐用 `trim_messages` 做窗口控制，而非旧的 WindowMemory：

```python
from langchain_core.messages import trim_messages
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

trimmer = trim_messages(
    max_tokens=1000,
    strategy="last",          # 保留最后 N 个 token 内的消息
    token_counter=ChatOpenAI(model="gpt-4o-mini"),  # 用模型算 token
    include_system=True,
    allow_partial=False,
    start_on="human",
)

# 在链中先 trim 再喂给模型
chain_with_trim = (
    RunnableLambda(lambda x: {**x, "history": trimmer.invoke(x["history"])})
    | prompt | model
)
```

### 4.5 带摘要的现代链（自己组装）

```python
# 现代做法：不依赖 SummaryMemory 类，自己用 LCEL 组装
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableLambda

summary_prompt = ChatPromptTemplate.from_template(
    "把以下对话总结成简短笔记：\n{history}"
)
summarizer = summary_prompt | llm | StrOutputParser()

# 自定义：超长历史时先摘要
def maybe_summarize(history):
    if len(history) > 20:
        old, recent = history[:-10], history[-10:]
        summary = summarizer.invoke({"history": old})
        return [SystemMessage(content=f"前情摘要：{summary}")] + recent
    return history
```

---

> 💡 **深度讲解**：`RunnableWithMessageHistory` 是现代 LangChain 记忆集成的"标准答案"，它的设计比旧的 `ConversationChain` 优雅得多。旧版把记忆"藏"在 Chain 内部，黑盒、难调试；新版把记忆历史显式作为链的一个输入变量（`MessagesPlaceholder`），开发者看得见、改得着。更重要的是，它通过 `config.configurable.session_id` 优雅地解决了**多租户**问题——同一个部署服务可以同时服务成千上万用户，每个用户有自己的消息历史，互不污染。这在旧版里需要自己写一堆字典管理。至于"修剪策略"，新版把它从 Memory 类里抽出来，变成独立的 `trim_messages` 工具——你可以在任何链的任意位置插入修剪，灵活度更高。
>
> **📝 精简总结**：旧版 ConversationChain 自动 load+save 记忆；现代推荐 RunnableWithMessageHistory，包装 LCEL 链，通过 get_session_history(session_id) 取/存历史，多会话用 config.configurable.session_id 隔离；trim_messages 是新一代窗口修剪工具；多输入/多输出务必指定 input_messages_key/history_messages_key/output_messages_key；推荐把历史显式放进 MessagesPlaceholder，透明可控。

---

## 五、记忆的持久化

### 5.1 为什么必须持久化

内存中的记忆（InMemoryChatMessageHistory）**进程一重启就全没了**。生产环境必须把对话历史落到外部存储。

```mermaid
graph TB
    subgraph 无持久化[❌ 内存记忆]
        A1[进程] --> A2[内存dict<br/>重启丢失]
    end
    subgraph 有持久化[✅ 外部存储]
        B1[进程] --> B2[(Redis/DB/文件)]
        B3[另一进程] --> B2
    end
```

### 5.2 RedisChatMessageHistory 实战

```python
from langchain_community.chat_message_histories import RedisChatMessageHistory

# 基础连接
history = RedisChatMessageHistory(
    session_id="user_1001",
    url="redis://localhost:6379/0",   # 含密码用 redis://:password@host:port/db
    ttl=60 * 60 * 24 * 30,           # 30天过期
)

history.add_user_message("持久化到 Redis 的消息")
history.add_ai_message("即使重启进程也在")

# 验证：新开一个进程
history2 = RedisChatMessageHistory(session_id="user_1001", url="redis://localhost:6379/0")
print(history2.messages)   # 能读到上一个进程存的消息
```

### 5.3 SQLChatMessageHistory 实战

```python
from langchain_community.chat_message_histories import SQLChatMessageHistory

# SQLite 示例（生产换 PostgreSQL/MySQL）
history = SQLChatMessageHistory(
    session_id="user_2002",
    connection_string="sqlite:///./chat_history.db",
)

history.add_user_message("存进 SQLite")
history.add_ai_message("可以用SQL查")

# 直接用 SQL 查
import sqlite3
conn = sqlite3.connect("./chat_history.db")
for row in conn.execute("SELECT session_id, type, content FROM message_store LIMIT 5"):
    print(row)
```

### 5.4 PostgresChatMessageHistory 与异步

```python
from langchain_postgres import PostgresChatMessageHistory
import asyncio

sync_history = PostgresChatMessageHistory(
    session_id="user_3003",
    connection_string="postgresql://user:pass@localhost:5432/chatdb",
    async_mode=False
)

# 异步版本（配合 ainvoke）
async def demo_async():
    async_history = PostgresChatMessageHistory(
        session_id="user_3003",
        connection_string="postgresql://user:pass@localhost:5432/chatdb",
        async_mode=True
    )
    await async_history.aadd_user_message("异步写入")
    await async_history.aclear()

asyncio.run(demo_async())
```

### 5.5 用字典按 session 管理（轻量多用户）

```python
from langchain_core.chat_history import BaseChatMessageHistory

class SessionManager:
    """按 session_id 管理多份历史"""
    def __init__(self):
        self.sessions: dict[str, BaseChatMessageHistory] = {}

    def get(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.sessions:
            self.sessions[session_id] = InMemoryChatMessageHistory()
        return self.sessions[session_id]

    def clear(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id].clear()

mgr = SessionManager()
wrapped = RunnableWithMessageHistory(chain, mgr.get, ...)
```

### 5.6 持久化方案选型表

| 存储 | 延迟 | 持久化 | 多实例共享 | TTL | 适用 |
|------|------|--------|------------|-----|------|
| InMemory | 极低 | ❌ | ❌ | 无 | 开发测试 |
| File | 低 | ✅ | ❌ | 无 | 单机小应用 |
| **Redis** | 低 | ✅ | ✅ | ✅ | **生产首选** |
| SQL/Postgres | 中 | ✅ | ✅ | 需自己加 | 强一致/查询 |
| 外部服务(Zep) | 中 | ✅ | ✅ | 服务端管 | 高级记忆 |

---

> 💡 **深度讲解**：持久化看似只是"把数据存下来"，实则牵扯**分布式一致性**。当你的应用部署了多个副本（K8s 多 Pod），每个副本都有自己的内存，用户这次请求落到 Pod-A、下次落到 Pod-B，内存历史就对不上了。这就是为什么生产必须用**外部共享存储**——Redis 是最常见选择，因为它天然支持 TTL（会话自动过期）和低延迟读写；SQL 则适合需要审计、复杂查询的场景（比如"导出某用户全部聊天记录"）。另一个常被忽略的点是**消息裁剪也要持久化同步**——如果你在内存里做了窗口裁剪，但历史全量存在 Redis，要确保裁剪逻辑读的是全量、写回的是全量，否则会出现"内存里剪过、Redis 里还是全量"的不一致。
>
> **📝 精简总结**：内存记忆重启即失，生产必须外部持久化；Redis 适合低延迟+TTL+多实例共享，SQL/Postgres 适合审计与复杂查询；SessionManager 按 session_id 管理多份历史；多副本部署必须用共享存储，否则历史对不上；裁剪逻辑要与持久化读写保持一致。

---

## 六、记忆的修剪策略与多轮对话管理

### 6.1 为什么要修剪

LLM 上下文窗口有限（如 GPT-4o 128k），且越长越贵、越慢、越容易"迷路"。修剪（trimming）= 在塞进 Prompt 前，把历史裁剪到可控范围。

```mermaid
graph LR
    A[全量历史 500条] --> B{修剪策略}
    B --> C[保留最近N条]
    B --> D[Token预算内保留]
    B --> E[旧的摘要化]
    B --> F[相关性检索]
    C --> G[精简后历史]
    D --> G
    E --> G
    F --> G
```

### 6.2 trim_messages 五种策略

```python
from langchain_core.messages import trim_messages, HumanMessage, AIMessage

msgs = [
    SystemMessage(content="你是客服"),
    HumanMessage(content="问题1"), AIMessage(content="答1"),
    HumanMessage(content="问题2"), AIMessage(content="答2"),
    # ... 几十条
]

# 策略1：按消息条数保留
trim_messages(msgs, max_count=6, strategy="last", include_system=True)

# 策略2：按 token 数保留（推荐，更精确）
trim_messages(
    msgs,
    max_tokens=500,
    strategy="last",
    token_counter=len,   # 生产用真实模型计数
    include_system=True,
    start_on="human",   # 保证从 human 开始，不截断半轮
)
```

### 6.3 多种修剪策略对比

| 策略 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| **固定窗口** | 保留最近 K 轮 | 简单可控 | 丢失早期事实 |
| **Token 预算** | 按 token 预算保留 | 精确控成本 | 需 token 计数 |
| **滑动+摘要** | 旧的摘要化 | 兼顾长短 | 实现复杂 |
| **向量检索** | 只留相关历史 | 精准 | 可能漏时序 |
| **重要性排序** | 按 LLM 打分保留 | 智能 | 贵、慢 |

### 6.4 多轮对话状态机管理

```python
# 用字典管理对话状态，配合 session
class DialogState:
    def __init__(self):
        self.states: dict[str, dict] = {}

    def get(self, sid: str) -> dict:
        return self.states.setdefault(sid, {
            "stage": "greeting",
            "slots": {},          # 槽位：订单号、问题类型等
            "turn_count": 0,
        })

    def update_slot(self, sid: str, key: str, value):
        self.get(sid)["slots"][key] = value

state = DialogState()

def route(sid: str, user_input: str):
    s = state.get(sid)
    s["turn_count"] += 1
    if s["stage"] == "greeting" and "订单" in user_input:
        s["stage"] = "collecting_order"
        return "请提供订单号"
    if s["stage"] == "collecting_order":
        state.update_slot(sid, "order_no", user_input)
        s["stage"] = "solving"
        return f"已收到订单{user_input}，正在查询"
```

### 6.5 上下文窗口预算分配

```python
# 经验公式：一次请求的 token 预算分配
def allocate_budget(total_budget: int) -> dict:
    return {
        "system_prompt": int(total_budget * 0.1),     # 系统提示 10%
        "history": int(total_budget * 0.5),           # 对话历史 50%
        "rag_context": int(total_budget * 0.25),       # 检索上下文 25%
        "output_reserve": int(total_budget * 0.15),   # 预留输出 15%
    }

print(allocate_budget(128000))
# {'system_prompt': 12800, 'history': 64000, 'rag_context': 32000, 'output_reserve': 19200}
```

---

> 💡 **深度讲解**：修剪策略的本质是"**在有限上下文预算里最大化信息价值**"。固定窗口最便宜但最笨；Token 预算制更贴近真实约束；滑动+摘要最优雅但最贵；向量检索最智能但会破坏时序一致性。生产系统往往是**混合策略**：system 提示永远保留 + 最近 3 轮原文 + 更早的用摘要 + 与本轮语义强相关的历史通过向量召回补进来。多轮对话管理的另一维度是**对话状态（slots）**——客服场景里你不光要"记得说过什么"，还要"记得问到哪一步了、还差哪些信息"，这部分通常不放在 LLM 记忆里，而是用显式的状态机/槽位表管理，LLM 只负责理解用户说了什么，状态流转由代码控制。
>
> **📝 精简总结**：修剪是把历史压到上下文预算内；trim_messages 支持 last/first 策略，按条数或 token 计数，include_system 保留系统消息；策略含固定窗口/Token预算/滑动摘要/向量检索/重要性排序；多轮对话用状态机管理槽位与阶段，状态别全靠 LLM；上下文预算建议 system 10%/history 50%/rag 25%/output 15%。

---

## 七、长期记忆 vs 短期记忆、可观测性、自定义 Memory

### 7.1 长期记忆 vs 短期记忆

| 维度 | 短期记忆（Short-term） | 长期记忆（Long-term） |
|------|------------------------|----------------------|
| 生命周期 | 一次会话内 | 跨会话、跨天 |
| 存储 | 上下文窗口 | 向量库/DB/知识图谱 |
| 典型实现 | Buffer/Window/Summary | VectorStore/Entity/KG/Zep |
| 容量 | 有限（受上下文限制） | 近乎无限 |
| 访问 | 全量注入 | 按需检索 |
| 类比 | 桌面打开的文档 | 硬盘归档的文件柜 |

**混合记忆架构**：

```mermaid
graph TB
    U[用户输入] --> ROUTER{路由}
    ROUTER --> ST[短期记忆<br/>近期对话原文<br/>上下文窗口]
    ROUTER --> LT[长期记忆<br/>向量库/知识图谱<br/>历史事实画像]
    ST --> MERGE[合并注入Prompt]
    LT --> MERGE
    MERGE --> LLM[模型]
```

### 7.2 记忆的可观测性

记忆问题是最难排查的——"为什么它忘了我说过的话"。需要把记忆的加载/保存过程暴露出来。

```python
from langchain_core.callbacks import BaseCallbackHandler

class MemoryTraceCallback(BaseCallbackHandler):
    def on_chain_start(self, serialized, inputs, **kwargs):
        print(f"[记忆追踪] 输入: {inputs}")

    def on_chain_end(self, outputs, **kwargs):
        print(f"[记忆追踪] 输出: {outputs}")

# 用 verbose 打印记忆细节
memory = ConversationSummaryBufferMemory(
    llm=llm, max_token_limit=200, verbose=True
)

# 用 LangSmith 看记忆每步
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "memory-debug"
```

### 7.3 打印记忆内部状态（调试利器）

```python
# 查看 BufferMemory 完整历史
print(memory.chat_memory.messages)

# 查看 SummaryBufferMemory 的滚动摘要
print("摘要buffer:", memory.moving_summary_buffer)

# 查看 EntityMemory 的实体表
print("实体字典:", memory.entity_store)

# 查看当前加载了哪些变量
print(memory.load_memory_variables({}))
```

### 7.4 自定义 Memory：从零实现一个

**场景需求**：实现一个"只保留包含关键词的重要对话"的过滤记忆。

```python
from langchain.memory.chat_memory import BaseChatMemory
from langchain_core.messages import BaseMessage, get_buffer_string
from typing import Dict, Any

class KeywordFilteredMemory(BaseChatMemory):
    """只保留含指定关键词的对话的自定义记忆"""

    keywords: list[str] = []
    memory_key: str = "history"

    @property
    def memory_variables(self):
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        # 过滤出含关键词的消息
        msgs = [
            m for m in self.chat_memory.messages
            if any(kw in m.content for kw in self.keywords)
        ]
        return {self.memory_key: get_buffer_string(msgs)}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        # 只在用户输入含关键词时才存
        user_text = inputs.get("input", "")
        if any(kw in user_text for kw in self.keywords):
            super().save_context(inputs, outputs)
```

**使用自定义记忆**：

```python
memory = KeywordFilteredMemory(
    keywords=["密码", "订单", "退款"],
    return_messages=False
)
memory.save_context({"input": "今天天气不错"}, {"output": "哈哈"})  # 不存
memory.save_context({"input": "我的订单ORD123怎么退款"}, {"output": "好的"})  # 存
print(memory.load_memory_variables({}))
```

### 7.5 异步自定义记忆

```python
class AsyncCustomMemory(BaseChatMemory):
    async def aload_memory_variables(self, inputs):
        # 异步加载（如查 Redis）
        return {"history": await self._afetch(inputs)}

    async def asave_context(self, inputs, outputs):
        await self._asave(inputs, outputs)
```

---

> 💡 **深度讲解**：把长期/短期记忆结合起来看，你会发现成熟的 AI 助手其实在模仿人脑：**短期工作记忆**（上下文窗口里的最近几轮）负责当前任务连贯，**长期情景记忆**（向量库）负责"以前发生过什么"，**长期语义记忆**（知识图谱/实体表）负责"关于某人/某事的稳定事实"。可观测性在这里尤其重要——因为记忆错误不像代码报错，它是"沉默的错"：模型只是答错了，你很难立刻定位是记忆没加载、加载了不相关的、还是被截断了。LangSmith 把每次 `load_memory_variables` 和 `save_context` 都记录成一条 trace，你能精确看到"这次 Prompt 里到底塞了哪些历史"。自定义 Memory 则是应对特殊业务需求的出口——比如"涉及密码的对话只加密存储""超过1小时的会话自动归档"这类策略，官方类不覆盖时，继承 BaseChatMemory 实现两个方法即可。
>
> **📝 精简总结**：短期记忆活在上下文窗口、长期记忆存在向量库/图谱，生产做混合架构（近期原文+长期检索+摘要）；可观测性靠 verbose/自定义 Callback/LangSmith trace，重点看 load/save 了什么；自定义 Memory 继承 BaseChatMemory，实现 load_memory_variables 与 save_context 两个方法即可，异步场景额外实现 aload/asave。

---

## 八、常见坑点（错误现象 + 原因 + 修复）

### 坑1：记忆完全不生效，模型像失忆

- **现象**：`memory.save_context` 调了，但下一轮模型就是不记得之前说过的话。
- **原因**：① `memory_key` 与 Prompt 占位符不一致；② 用了 LCEL 链但忘了在 invoke 前调用 `load_memory_variables`；③ `ConversationChain` 与 LCEL 混用。
- **修复**：

```python
# ❌ 错误：占位符叫 history，但 memory_key 写成了 chat_history
prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder("history"),
    ("human", "{input}")
])
memory = ConversationBufferMemory(memory_key="chat_history")  # 不匹配！

# ✅ 正确：两边对齐
memory = ConversationBufferMemory(memory_key="history")
# 或用 RunnableWithMessageHistory，框架自动对齐
```

### 坑2：return_messages 类型报错

- **现象**：`ValueError: Got unexpected type 'str'` 或 `History variable should be a list of messages`。
- **原因**：`MessagesPlaceholder` 期望消息列表，但 `return_messages=False` 返回的是字符串。
- **修复**：

```python
# ❌ MessagesPlaceholder 需要 list[BaseMessage]
memory = ConversationBufferMemory(return_messages=False)  # 返回 str

# ✅ 配合 MessagesPlaceholder 必须 return_messages=True
memory = ConversationBufferMemory(return_messages=True)
```

### 坑3：摘要记忆成本翻倍

- **现象**：每次对话都触发两次 LLM 调用，账单飙升。
- **原因**：ConversationSummary/SummaryBufferMemory 每次 `save_context` 都会调 LLM 做摘要。
- **修复**：

```python
# 方案A：短对话改用 BufferMemory，省掉摘要调用
memory = ConversationBufferMemory(k=5)

# 方案B：提高触发阈值，减少摘要频率
memory = ConversationSummaryBufferMemory(
    llm=cheap_llm,        # 摘要用便宜模型，回答用贵模型
    max_token_limit=2000   # 设大点，少触发
)
```

### 坑4：多用户串号，A 能看到 B 的对话

- **现象**：用户 A 问"我叫什么"，模型答出了用户 B 的名字。
- **原因**：所有请求共用同一个内存 Memory 对象，没按 session 隔离。
- **修复**：

```python
# ❌ 全局单例，所有人共用
memory = ConversationBufferMemory()

# ✅ 用 session_id 隔离
def get_history(sid: str):
    return RedisChatMessageHistory(session_id=sid, url="redis://...")
wrapped = RunnableWithMessageHistory(chain, get_history, ...)
wrapped.invoke({"input": "..."}, config={"configurable": {"session_id": user_id}})
```

### 坑5：上下文爆掉，token 超限报错

- **现象**：`openai.BadRequestError: context_length_exceeded`。
- **原因**：BufferMemory 无限累积，历史超过模型上下文窗口。
- **修复**：

```python
# ❌ 不设上限
memory = ConversationBufferMemory(return_messages=True)

# ✅ 用窗口/摘要/trim
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=1000)
# 或
chain | RunnableLambda(lambda x: {**x, "history": trim_messages(x["history"], max_tokens=1000)})
```

### 坑6：save_context 找不到 output key

- **现象**：`KeyError: 'output'` 或 `output_key is not specified and multiple output keys`。
- **原因**：链返回字典且有多个 key，框架无法判断哪个是模型输出。
- **修复**：

```python
# ❌ 多输出时不指定
memory = ConversationBufferMemory()

# ✅ 显式指定
memory = ConversationBufferMemory(
    input_key="input",
    output_key="answer"   # 告诉它 outputs["answer"] 是模型回复
)
```

### 坑7：流式输出与记忆保存冲突

- **现象**：stream 边出字边调 save_context，导致保存了半截回复。
- **修复**：

```python
# ❌ 边流边存
async for chunk in chain.astream(input):
    print(chunk)
    memory.save_context(...)   # 此时 answer 不完整！

# ✅ 先收完整结果再存
full = ""
async for chunk in chain.astream(input):
    full += chunk
    print(chunk, end="")
memory.save_context({"input": input}, {"output": full})  # 完整回复再存
```

---

> 💡 **深度讲解**：Memory 的坑几乎都可以归结为"**两个不一致**"：key 不一致（memory_key/input_key/output_key 与 Prompt/链对不上）和**生命周期不一致**（流式保存时机、多实例存储、进程重启）。key 不一致是新手高频错误，解决靠"显式声明 + 打印 load_memory_variables 验证"。生命周期问题在生产更隐蔽——开发时单机内存跑得好好的，一上 K8s 多副本就偶发"失忆"，根因就是状态没外存。流式场景的保存时机也常被忽略：人类直觉是"边说边记"，但工程上必须"说完再记"，否则记忆里存了个残缺的半句。
>
> **📝 精修总结**：七大坑分别是记忆不生效（key 不匹配）、类型报错（return_messages）、成本翻倍（每轮摘要）、多用户串号（缺 session 隔离）、上下文超限（缺修剪）、output key 报错（多输出未指定）、流式保存半截（先收全再存）；排查口诀：先打印 load_memory_variables 看历史对不对，再检查 key 对齐，最后查持久化与 session 隔离。

---

## 九、记忆选型决策树与最佳实践

### 9.1 选型决策树

```mermaid
graph TD
    Q[选择记忆策略] --> A{对话平均多长?}
    A|<5轮| B[BufferMemory 全量]
    A|5-30轮| C{需要记得很早的细节吗?}
    C|不需要| D[WindowMemory k=5]
    C|需要| E[SummaryBufferMemory]
    A|>30轮或跨会话| F{需要按语义找历史?}
    F|需要| G[VectorStoreRetrieverMemory]
    F|需要实体关系| H[Entity/KG Memory]
    F|都要| I[混合: 短期Window + 长期向量]
```

### 9.2 生产最佳实践清单

| 实践 | 说明 |
|------|------|
| ① 优先 RunnableWithMessageHistory | 替代旧 ConversationChain |
| ② return_messages=True | 配合 MessagesPlaceholder |
| ③ 持久化用 Redis | 多实例共享 + TTL |
| ④ 显式指定所有 key | input/output/memory_key |
| ⑤ 必做修剪 | trim_messages 或 SummaryBuffer |
| ⑥ 摘要用便宜模型 | 主回答用强模型，摘要用 mini |
| ⑦ 流式先收全再存 | 避免半截入库 |
| ⑧ LangSmith trace | 调试记忆问题 |
| ⑨ 设 session TTL | 定期清理，省存储成本 |
| ⑩ 敏感对话脱敏 | 密码/身份证不入长期记忆 |

---

> 💡 **深度讲解**：记忆选型没有银弹，只有"**匹配你的对话特征**"。短客服咨询用 Buffer 就够；长陪伴型对话（AI 女友、个人助理）必须上 SummaryBuffer + 向量长期记忆；需要"记住用户偏好并跨天使用"的产品，长期记忆是刚需。最佳实践里最值钱的两条是"**摘要用便宜模型**"和"**显式 key 声明**"——前者直接砍一半成本，后者避免 80% 的记忆 bug。最后，永远记住：LLM 记忆不是数据库，它擅长"模糊关联"，不擅长"精确查询"。需要精确数据（订单号、余额）不要靠记忆，要靠工具调用实时查。
>
> **📝 精简总结**：选型按对话轮数和是否跨会话决策，短用Buffer、中用SummaryBuffer、长用向量/实体；最佳实践十条：RunnableWithMessageHistory、return_messages、Redis持久化、显式key、必修剪、摘要用小模型、流式先收全再存、LangSmith追踪、TTL清理、敏感脱敏；核心原则：LLM记忆管模糊偏好，精确数据走工具查询。

---

## 十、记忆内部机制深挖与完整工程案例

### 10.1 ConversationBufferMemory 源码级剖析

```python
# ConversationBufferMemory 继承链：
# BaseMemory -> BaseChatMemory -> ConversationBufferMemory
# 它的 load_memory_variables 极其简单——就是把 chat_memory 里的消息格式化

from langchain_core.messages import get_buffer_string

class ConversationBufferMemory(BaseChatMemory):
    human_prefix: str = "Human"
    ai_prefix: str = "AI"
    memory_key: str = "history"

    @property
    def memory_variables(self):
        return [self.memory_key]

    def load_memory_variables(self, inputs):
        if self.return_messages:
            buffer = self.chat_memory.messages   # 直接返回消息列表
        else:
            buffer = get_buffer_string(          # 拼成 "Human: ...\nAI: ..."
                self.chat_memory.messages,
                human_prefix=self.human_prefix,
                ai_prefix=self.ai_prefix,
            )
        return {self.memory_key: buffer}
```

**自定义前缀（多角色场景）**：

```python
# 多轮角色扮演时，自定义 Human/AI 前缀
memory = ConversationBufferMemory(
    human_prefix="用户",
    ai_prefix="客服小助手",
)
memory.save_context({"input": "退款"}, {"output": "好的"})
print(memory.load_memory_variables({})["history"])
# 用户: 退款
# 客服小助手: 好的
```

### 10.2 get_buffer_string 的格式化细节

```python
from langchain_core.messages import get_buffer_string, HumanMessage, AIMessage, SystemMessage

msgs = [
    SystemMessage("你是助手"),
    HumanMessage("你好"),
    AIMessage("你好！"),
]

# 默认拼接
print(get_buffer_string(msgs))
# System: 你是助手
# Human: 你好
# AI: 你好！

# 自定义前缀
print(get_buffer_string(msgs, human_prefix="用户", ai_prefix="助手"))
```

### 10.3 ConversationSummaryMemory 源码级剖析

```python
# SummaryMemory 的核心：每存一轮就用 LLM 把旧摘要+新对话合并
class ConversationSummaryMemory(BaseChatMemory):
    llm: BaseChatModel
    summarize_step: LLMChain   # 负责合并摘要
    moving_summary_buffer: str = ""   # 滚动摘要
    memory_key: str = "history"

    def save_context(self, inputs, outputs):
        input_str, output_str = self._get_input_output(inputs, outputs)
        # 把新对话行交给 LLM 更新摘要
        self.moving_summary_buffer = self.predict_new_summary(
            self.moving_summary_buffer,
            [input_str, output_str]
        )

    def load_memory_variables(self, inputs):
        # 直接返回摘要文本（不是逐条消息）
        return {self.memory_key: self.moving_summary_buffer}
```

**手动观察摘要如何增长**：

```python
memory = ConversationSummaryMemory(llm=llm, return_messages=False)

memory.save_context({"input": "我叫张三"}, {"output": "你好张三"})
print("第1轮后摘要:", memory.moving_summary_buffer)

memory.save_context({"input": "我做电商运营"}, {"output": "不错"})
print("第2轮后摘要:", memory.moving_summary_buffer)  # 已合并两轮
```

### 10.4 ConversationSummaryBufferMemory 触发逻辑源码

```python
class ConversationSummaryBufferMemory(ConversationSummaryMemory):
    max_token_limit: int = 2000
    moving_summary_buffer: str = ""

    def save_context(self, inputs, outputs):
        self.chat_memory.add_user_message(...)
        self.chat_memory.add_ai_message(...)
        # 关键：估算 token，超限就压缩
        while self._token_count() > self.max_token_limit:
            # 把最早的两条消息移出，交给 LLM 合并进摘要
            messages = self.chat_memory.messages
            _new_lines = [messages[0], messages[1]]
            self.moving_summary_buffer = self.predict_new_summary(
                self.moving_summary_buffer, _new_lines
            )
            # 从 chat_memory 删除这两条
            self.chat_memory.messages = messages[2:]

    def load_memory_variables(self, inputs):
        # 拼装：[摘要作为一条消息] + [剩余原文]
        buffer = self.chat_memory.messages
        if self.moving_summary_buffer != "":
            buffer = [SystemMessage(self.moving_summary_buffer)] + buffer
        return {self.memory_key: buffer}
```

**token 计数函数**：

```python
from langchain_core.messages import count_tokens_approximately

# 估算消息列表的 token 数
approx = count_tokens_approximately(msgs, encoder_name="cl100k_base")
print(f"约 {approx} tokens")
```

### 10.5 ConversationEntityMemory 实体表结构

```python
# EntityMemory 内部维护一个 dict: entity -> 笔记
# entity_store: Dict[str, str]

memory = ConversationEntityMemory(llm=llm)
memory.save_context({"input": "张三在字节工作"}, {"output": "好"})

# 直接查看实体表
print(type(memory.entity_store))   # <class 'dict'>
print(memory.entity_store)         # {'张三': '在字节跳动工作'}

# 手动预填实体（冷启动用户画像）
memory.entity_store["用户"] = "22岁女性，电商专业，求职中"
```

### 10.6 VectorStoreRetrieverMemory 写入格式

```python
# 它把每轮对话存成一条 Document：
# page_content = "输入: {input}\n输出: {output}"
# metadata = {"history": ...}

# 检索时，用当前 input 作为 query 去向量库找相似的历史
# 这意味着：存的时候是"问答对"，查的时候是"当前问题"

# 自定义文档格式化
memory = VectorStoreRetrieverMemory(
    retriever=retriever,
    # 自定义写入时的文本
)
```

### 10.7 完整场景：带记忆的 RAG 客服机器人

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 1. 知识库检索器
kb = Chroma(persist_directory="./kb", embedding_function=OpenAIEmbeddings())
retriever = kb.as_retriever(k=3)

# 2. 带记忆+检索的 Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是电商客服。参考知识库：\n{context}"),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])

# 3. 链：并行检索 + 注入历史
def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

chain = (
    RunnablePassthrough.assign(
        context=retriever | format_docs
    )
    | prompt | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()
)

# 4. 包装记忆
def get_history(sid):
    return RedisChatMessageHistory(session_id=sid, url="redis://localhost:6379")

wrapped = RunnableWithMessageHistory(
    chain, get_history,
    input_messages_key="input",
    history_messages_key="history",
)

# 5. 多轮客服对话
wrapped.invoke({"input": "我想退货"},
    config={"configurable": {"session_id": "cust_001"}})
wrapped.invoke({"input": "订单号是ORD888"},
    config={"configurable": {"session_id": "cust_001"}})
```

### 10.8 完整场景：AI 个人助理的长期画像

```python
# 长期记忆：从对话中抽取用户画像，存向量库
import json

def extract_profile(text: str) -> dict:
    """用 LLM 从对话抽取结构化画像"""
    extract_prompt = ChatPromptTemplate.from_template("""
    从对话抽取用户画像，输出JSON：
    对话：{text}
    字段：name, age, job, preferences[]
    只输出JSON：""")
    result = (extract_prompt | llm | StrOutputParser()).invoke({"text": text})
    return json.loads(result)

# 对话结束后更新画像
def update_profile(user_id: str, dialog: str):
    profile = extract_profile(dialog)
    # 存入向量库，下次召回
    profile_vec.add_texts(
        [json.dumps(profile, ensure_ascii=False)],
        metadatas=[{"user": user_id}]
    )
```

### 10.9 完整场景：带记忆的流式聊天 API

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/chat")
async def chat(request: dict):
    sid = request["session_id"]
    user_input = request["input"]

    async def gen():
        full = ""
        async for chunk in wrapped.astream(
            {"input": user_input},
            config={"configurable": {"session_id": sid}}
        ):
            full += chunk
            yield f"data: {chunk}\n\n"
        # 流结束后，RunnableWithMessageHistory 已自动保存历史
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
```

### 10.10 记忆的 Token 成本估算工具

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

def estimate_memory_cost(history: list, model: str = "gpt-4o-mini") -> dict:
    """估算一段历史的 token 与成本"""
    total_chars = sum(len(m.content) for m in history)
    approx_tokens = total_chars // 2   # 粗估：中文约2字/token
    cost_per_1k = 0.00015
    return {
        "messages": len(history),
        "approx_tokens": approx_tokens,
        "est_cost_usd": approx_tokens / 1000 * cost_per_1k,
    }

hist = [HumanMessage("我叫张三")] * 50
print(estimate_memory_cost(hist))
```

### 10.11 记忆数据结构对照表

| Memory 类 | 内部存储 | 暴露变量 | 是否调 LLM | 持久化友好 |
|-----------|----------|----------|------------|------------|
| BufferMemory | chat_memory.messages | history(str/list) | 否 | 高 |
| WindowMemory | chat_memory.messages(切片) | history | 否 | 高 |
| SummaryMemory | moving_summary_buffer | summary(str) | 是(每轮) | 中 |
| SummaryBufferMemory | buffer+summary | history(list) | 是(触发时) | 中 |
| EntityMemory | entity_store dict | entities+history | 是(每轮) | 中 |
| KGMemory | knowledge_triples | history | 是(每轮) | 低 |
| VectorStoreRetriever | 向量库 | relevant_history | 否(检索) | 高 |
| ZepMemory | 外部服务 | history | 服务端 | 高 |

### 10.12 多记忆组合：短期窗口 + 长期向量

```python
from langchain_core.runnables import RunnableLambda

# 同时注入：近期窗口历史 + 向量召回的长期事实
combined_chain = (
    RunnablePassthrough.assign(
        recent=RunnableLambda(lambda x: window_mem.load_memory_variables(x)["history"]),
        longterm=RunnableLambda(lambda x: vector_mem.load_memory_variables(x)["relevant_history"])
    )
    | ChatPromptTemplate.from_messages([
        ("system", "长期事实：{longterm}"),
        MessagesPlaceholder("recent"),
        ("human", "{input}")
    ])
    | llm
)
```

### 10.13 记忆的"遗忘"策略：主动删除

```python
# 场景：用户说"忘掉我刚才说的手机号"
def forget_recent(history: list, n: int = 2):
    """遗忘最近 n 轮"""
    return history[:-2*n]

# 或从 Redis 删除
def forget_session(sid: str):
    RedisChatMessageHistory(session_id=sid, url="redis://...").clear()

# 按关键词遗忘（GDPR 被遗忘权）
def forget_topic(history: list, keyword: str):
    return [m for m in history if keyword not in m.content]
```

### 10.14 记忆序列化与备份

```python
import json

def export_history(history, path: str):
    """导出对话历史为 JSON 备份"""
    data = [{"type": type(m).__name__, "content": m.content} for m in history]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def import_history(path: str, memory):
    """从 JSON 恢复"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        if item["type"] == "HumanMessage":
            memory.chat_memory.add_user_message(item["content"])
        elif item["type"] == "AIMessage":
            memory.chat_memory.add_ai_message(item["content"])
```

---

> 💡 **深度讲解**：深挖到源码层你会发现，所有 Memory 类的复杂度其实都集中在"**如何把 chat_memory.messages 加工成 load_memory_variables 的返回值**"这一件事上。Buffer 系就是直接返回或切片返回；Summary 系是把 messages 喂给 LLM 产出一段文本再返回；Entity/KG 是把 messages 喂给 LLM 抽取结构化信息再返回；VectorStore 是把 messages 存进向量库、查询时按相似度返回。理解了这一点，你就能预测任何 Memory 类的行为，也能在需要时自己写一个。工程上最有价值的是 10.7 的"记忆+RAG 混合"和 10.12 的"多记忆组合"——真实产品从来不是单一记忆策略，而是把短期对话流、长期事实库、知识库检索三条线在 Prompt 里合流。
>
> **📝 精简总结**：源码层所有 Memory 都在加工 messages；Buffer 直接返回/切片，Summary 用 LLM 压缩成文本，Entity/KG 用 LLM 抽结构化事实，VectorStore 按语义检索；生产常做记忆+RAG混合、短期窗口+长期向量组合；记得实现"遗忘"与"序列化备份"以满足合规与恢复需求；Token 成本要随对话长度持续监控。

---

## 十一、完整工程案例与性能调优

### 11.1 案例一：电商客服多轮会话（完整可运行）

```python
"""
完整示例：电商客服多轮会话
依赖：pip install langchain langchain-openai langchain-community redis
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory

# 初始化模型
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# 客服 Prompt：人设 + 规则 + 历史
prompt = ChatPromptTemplate.from_messages([
    ("system", """你是【云购商城】的金牌客服小购。
    规则：
    1. 礼貌、简洁、专业
    2. 涉及订单/退款时，主动索要订单号
    3. 不知道的不要编造，说"帮您转接人工"
    """),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

# 基础链
base_chain = prompt | llm | StrOutputParser()

# 会话工厂：按 user_id 取历史
def get_session_history(user_id: str):
    return RedisChatMessageHistory(
        session_id=user_id,
        url="redis://localhost:6379/0",
        ttl=60 * 60 * 24 * 7,  # 7天
    )

# 包装成有状态链
customer_service = RunnableWithMessageHistory(
    base_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# 模拟对话
def talk(user_id: str, text: str) -> str:
    return customer_service.invoke(
        {"input": text},
        config={"configurable": {"session_id": user_id}}
    )

# 客户A
print(talk("A", "你好，我上周买的手机没收到"))
print(talk("A", "订单号是 ORD-20240901-001"))
# 客户B（互不干扰）
print(talk("B", "你好，我要退货"))
```

### 11.2 案例二：AI 陪伴聊天机器人（长期记忆）

```python
"""
AI陪伴：短期窗口 + 长期向量记忆
"""
from langchain.memory import VectorStoreRetrieverMemory
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import trim_messages, HumanMessage

emb = OpenAIEmbeddings(model="text-embedding-3-small")
vec = Chroma(embedding_function=emb, persist_directory="./companion_memory")
retriever = vec.as_retriever(search_kwargs={"k": 4})

# 长期记忆：语义召回历史
long_term_mem = VectorStoreRetrieverMemory(retriever=retriever)

# 短期：最近3轮原文
recent_mem = ConversationBufferWindowMemory(k=3, return_messages=True)

# 合并链
def build_context(x):
    longterm = long_term_mem.load_memory_variables(x)["relevant_history"]
    recent = recent_mem.load_memory_variables(x)["history"]
    recent = trim_messages(recent, max_tokens=600, strategy="last",
                           token_counter=len, include_system=False)
    return {"input": x["input"], "longterm": longterm, "recent": recent}

prompt = ChatPromptTemplate.from_messages([
    ("system", "亲密陪伴助手。记得这些长期信息：{longterm}"),
    MessagesPlaceholder("recent"),
    ("human", "{input}"),
])

chain = RunnableLambda(build_context) | prompt | llm | StrOutputParser()

def chat(text):
    ans = chain.invoke({"input": text})
    # 同时写入长期和短期
    long_term_mem.save_context({"input": text}, {"output": ans})
    recent_mem.save_context({"input": text}, {"output": ans})
    return ans
```

### 11.3 案例三：带实体记忆的个人管家

```python
"""个人管家：记住家庭成员、日程、偏好"""
memory = ConversationEntityMemory(llm=llm)

# 登记家庭信息
dialogues = [
    ("我老婆叫林晓，生日是3月8日", "好的"),
    ("我儿子叫豆豆，今年5岁", "记下了"),
    ("我妈喜欢喝普洱", "了解"),
]
for q, a in dialogues:
    memory.save_context({"input": q}, {"output": a})

# 查询
loaded = memory.load_memory_variables({"input": "我家人都有谁"})
print(loaded["entities"])
# {'林晓': '用户的老婆，生日3月8日', '豆豆': '用户儿子，5岁', '我妈': '喜欢喝普洱'}
```

### 11.4 案例四：记忆 + 工具调用的 Agent 对话

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

@tool
def get_order_status(order_no: str) -> str:
    """查询订单状态"""
    return f"订单{order_no}：已发货，预计明天送达"

tools = [get_order_status]
prompt = ChatPromptTemplate.from_messages([
    ("system", "客服Agent，可用工具查订单"),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(
    agent=agent, tools=tools,
    memory=ConversationBufferWindowMemory(k=10, return_messages=True),
    verbose=True, handle_parsing_errors=True,
)
executor.invoke({"input": "帮我查ORD123"})
executor.invoke({"input": "那它到哪了"})  # 记得上一轮提到ORD123
```

### 11.5 性能调优：降低记忆带来的延迟

| 调优点 | 做法 | 效果 |
|--------|------|------|
| 摘要用小模型 | SummaryMemory 的 llm 换成 gpt-4o-mini | 摘要成本降 80% |
| 批量摘要 | 攒 N 轮再摘要一次，而非每轮 | 摘要调用降 80% |
| 历史预取 | 异步并行取历史+检索 | 首字延迟降 30% |
| 缓存历史 | 相同 session 短时间内缓存 | 重复查询快 |
| 向量索引预热 | 启动时预热向量库连接 | 冷启动快 |
| 连接池 | Redis 用连接池 | 高并发不卡 |

```python
# 异步并行：同时取历史和检索
import asyncio

async def parallel_prepare(session_id, query):
    hist_task = asyncio.to_thread(get_history, session_id)
    search_task = asyncio.to_thread(retriever.invoke, query)
    history, docs = await asyncio.gather(hist_task, search_task)
    return history, docs
```

### 11.6 监控记忆指标

```python
class MetricsCollector:
    """采集记忆相关指标"""
    def __init__(self):
        self.turns = {}

    def record_turn(self, sid: str, tokens: int, latency: float):
        if sid not in self.turns:
            self.turns[sid] = {"count": 0, "tokens": [], "latency": []}
        self.turns[sid]["count"] += 1
        self.turns[sid]["tokens"].append(tokens)
        self.turns[sid]["latency"].append(latency)

    def report(self, sid: str):
        t = self.turns[sid]
        return {
            "total_turns": t["count"],
            "avg_tokens": sum(t["tokens"]) / len(t["tokens"]),
            "avg_latency": sum(t["latency"]) / len(t["latency"]),
        }

metrics = MetricsCollector()
metrics.record_turn("A", 1500, 1.2)
print(metrics.report("A"))
```

---

> 💡 **深度讲解**：真实项目里，记忆不是"选一个类"就完事，而是要把它放进完整的对话管线：会话路由（session_id）→ 历史加载（Redis）→ 记忆整理（trim/summary）→ 知识库检索（RAG）→ Prompt 组装 → 模型调用 → 流式输出 → 历史保存。这条管线的每一环都可能成为瓶颈。最容易被忽视的性能点是"**摘要每轮都调 LLM**"——一个 100 轮的对话，光是摘要就多花了 100 次模型调用。优化思路是"攒批摘要"：只在历史长度跨阈值时才摘要，而不是机械地每轮摘要。监控指标也很关键——你需要知道平均每轮塞了多少 token、延迟多少、哪个用户的对话最长，才能持续调优修剪阈值。
>
> **📝 精简总结**：四大工程案例覆盖客服/陪伴/管家/带工具Agent；性能调优靠摘要用小模型、攒批摘要、异步并行预取、缓存、连接池；监控会话轮数、token、延迟；记忆是一条完整管线而非单一组件，每个环节都要监控和优化。

---

## 十二、进阶专题：异步记忆、混合策略与调试实战

### 12.1 异步记忆的完整用法

```python
"""异步记忆：配合 ainvoke/astream 提升并发"""
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_messages([
    ("system", "助手"),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])
chain = prompt | llm

stores = {}
def get_history(sid):
    return stores.setdefault(sid, InMemoryChatMessageHistory())

wrapped = RunnableWithMessageHistory(chain, get_history,
    input_messages_key="input", history_messages_key="history")

async def main():
    # 并发处理多个用户
    results = await asyncio.gather(*[
        wrapped.ainvoke({"input": f"用户{i}打招呼"},
            config={"configurable": {"session_id": f"u{i}"}})
        for i in range(5)
    ])
    for r in results:
        print(r.content)

asyncio.run(main())
```

### 12.2 异步流式记忆

```python
async def stream_chat(sid: str, text: str):
    """边流式边自动保存历史"""
    async for chunk in wrapped.astream(
        {"input": text},
        config={"configurable": {"session_id": sid}}
    ):
        print(chunk.content, end="", flush=True)
    # RunnableWithMessageHistory 在 astream 结束后自动保存
```

### 12.3 记忆与 LangGraph 的现代结合

```python
"""LangGraph 中用 Checkpoint 替代传统 Memory"""
from langgraph.graph import StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver

def call_model(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}

workflow = StateGraph(MessagesState)
workflow.add_node("chat", call_model)
workflow.set_entry_point("chat")
graph = workflow.compile(checkpointer=MemorySaver())

# LangGraph 自动管理消息历史，无需传统 Memory 类
graph.invoke(
    {"messages": [HumanMessage("我叫钱七")]},
    config={"configurable": {"thread_id": "t1"}}
)
graph.invoke(
    {"messages": [HumanMessage("我叫什么")]},
    config={"configurable": {"thread_id": "t1"}}   # 记得钱七
)
```

### 12.4 记忆裁剪：按类型/长度/重要性

```python
from langchain_core.messages import RemoveMessage, SystemMessage

def smart_trim(history: list) -> list:
    """智能裁剪：保留 system、最近N轮、关键实体相关"""
    system_msgs = [m for m in history if isinstance(m, SystemMessage)]
    others = [m for m in history if not isinstance(m, SystemMessage)]
    # 保留最近10条
    recent = others[-10:]
    return system_msgs + recent

# LangGraph 中删除旧消息
def delete_old_messages(state):
    return {"messages": [RemoveMessage(id=m.id) for m in state["messages"][:-10]]}
```

### 12.5 记忆的"分块存储"：按主题分桶

```python
class TopicBucketMemory:
    """按主题分桶的记忆：不同话题的对话分开存"""
    def __init__(self):
        self.buckets = {
            "订单": InMemoryChatMessageHistory(),
            "退款": InMemoryChatMessageHistory(),
            "咨询": InMemoryChatMessageHistory(),
        }

    def route(self, text: str) -> str:
        if "订单" in text: return "订单"
        if "退" in text: return "退款"
        return "咨询"

    def save(self, text, answer):
        bucket = self.route(text)
        self.buckets[bucket].add_user_message(text)
        self.buckets[bucket].add_ai_message(answer)

    def load_all(self):
        out = {}
        for k, v in self.buckets.items():
            out[k] = v.messages
        return out
```

### 12.6 记忆冲突解决：用户改口了

```python
# 场景：用户先说"我在做电商"，后说"其实我转行了做教育"
# 实体记忆/Zep 会检测冲突并更新旧事实

# 传统向量记忆需要自己处理：
def update_with_correction(vec_store, user_id, new_fact: str):
    """覆盖式更新用户事实"""
    # 1. 先删掉旧的相关事实
    old = vec_store.similarity_search(new_fact, k=3)
    for doc in old:
        vec_store.delete([doc.metadata["id"]])
    # 2. 写入新事实
    vec_store.add_texts([new_fact], metadatas=[{"user": user_id}])
```

### 12.7 记忆压缩的多种实现

```python
# 方法1：LLM 摘要（最常见）
def llm_summarize(messages):
    text = "\n".join(f"{type(m).__name__}: {m.content}" for m in messages)
    return llm.invoke(f"总结这段对话：{text}").content

# 方法2：抽取式摘要（不调LLM，关键词保留）
def extractive_summarize(messages, keep=3):
    # 只保留含关键词的消息
    keywords = ["订单", "退货", "金额", "地址"]
    return [m for m in messages if any(k in m.content for k in keywords)][:keep]

# 方法3：结构化要点（JSON）
def structured_summarize(messages):
    fmt = """提取对话要点为JSON：{用户诉求, 已提供信息, 待办}
    对话：{text}"""
    return (ChatPromptTemplate.from_template(fmt) | llm).invoke({"text": messages})
```

### 12.8 记忆质量评估：它真的记住了吗

```python
def evaluate_memory(memory, facts: list) -> float:
    """用一组事实测试记忆召回率"""
    hits = 0
    for fact in facts:
        loaded = memory.load_memory_variables({"input": fact["query"]})
        if any(fact["keyword"] in str(v) for v in loaded.values()):
            hits += 1
    return hits / len(facts) * 100

# 测试
facts = [
    {"query": "我叫什么", "keyword": "张三"},
    {"query": "我做什么工作", "keyword": "电商"},
]
print(f"记忆召回率: {evaluate_memory(memory, facts)}%")
```

### 12.9 记忆的脱敏与合规

```python
import re

def sanitize(text: str) -> str:
    """脱敏：身份证、手机号、银行卡"""
    text = re.sub(r"\d{18}|\d{17}X", "[身份证]", text)
    text = re.sub(r"1[3-9]\d{9}", "[手机号]", text)
    text = re.sub(r"\d{16,19}", "[银行卡]", text)
    return text

# 存入记忆前先脱敏
def safe_save(memory, user_input, answer):
    memory.save_context(
        {"input": sanitize(user_input)},
        {"output": sanitize(answer)}
    )
```

### 12.10 记忆 vs RAG：边界在哪

| 对比项 | 记忆(Memory) | RAG 检索 |
|--------|--------------|----------|
| 存什么 | 用户对话历史 | 外部知识库文档 |
| 来源 | 与用户的对话产生 | 预先准备的资料 |
| 生命周期 | 随对话增长 | 静态/定期更新 |
| 检索方式 | 全量注入/窗口/摘要 | 语义相似度 Top-K |
| 典型问题 | "我刚才说过什么" | "公司的政策是什么" |

**组合使用**：

```python
# 记忆管"用户说过什么"，RAG 管"公司知道什么"
combined = RunnablePassthrough.assign(
    history=lambda x: memory.load_memory_variables(x)["history"],
    context=retriever | (lambda docs: "\n".join(d.page_content for d in docs))
) | ChatPromptTemplate.from_messages([
    ("system", "知识库：{context}\n历史：{history}"),
    ("human", "{input}")
]) | llm
```

### 12.11 调试：打印完整 Prompt 看记忆注入效果

```python
# 用 verbose 打印链的每一步
chain = chain.with_config({"verbose": True})
# 或用 callbacks
from langchain_core.callbacks import StdOutCallbackHandler
chain.invoke({"input": "测试"}, config={"callbacks": [StdOutCallbackHandler()]})

# 手动打印最终 Prompt
final_prompt = prompt.invoke({
    "history": memory.load_memory_variables({})["history"],
    "input": "测试"
})
print(final_prompt.to_messages())
```

### 12.12 记忆相关报错速查表

| 报错信息 | 含义 | 修复 |
|----------|------|------|
| `KeyError: 'history'` | Prompt 占位符与 memory_key 不一致 | 对齐变量名 |
| `ValueError: unexpected type 'str'` | MessagesPlaceholder 收到字符串 | return_messages=True |
| `NotImplementedError` | 自定义 Memory 没实现抽象方法 | 实现 load/save/clear |
| `KeyError: 'output'` | 多输出没指定 output_key | 显式指定 |
| `RedisConnectionError` | Redis 连不上 | 检查 url/密码/网络 |
| `context_length_exceeded` | 历史超长 | 加修剪/摘要 |
| `AttributeError: 'dict' object has no attribute 'content'` | 类型串了 | 检查链的输入输出 |

---

> 💡 **深度讲解**：进阶阶段你会发现记忆的真问题不在"选哪个类"，而在"**如何在动态对话中维护一份高质量的历史**"。异步记忆让高并发服务成为可能；LangGraph 用 Checkpoint 把记忆提升为图状态，是比传统 Memory 类更现代的方案；按主题分桶、冲突解决、智能裁剪、质量评估这些"非标准"操作，才是真实产品需要补的功课。尤其是"用户改口"场景——传统向量记忆会把新旧两个事实都存下来，模型可能混淆，必须主动删旧。合规脱敏也不能等上线后再补——对话里常有身份证、手机号，存入长期记忆前必须脱敏，否则是合规事故。
>
> **📝 精简总结**：异步记忆配合 ainvoke/astream 提升并发；LangGraph 用 Checkpointer 替代传统 Memory；进阶需求含主题分桶、冲突解决、智能裁剪、召回率评估、脱敏；记忆管"用户说过什么"、RAG 管"外部知识"，二者在 Prompt 合流；调试靠 verbose/Callbacks/手动打印最终 Prompt；报错速查表覆盖常见 KeyError/类型/连接/超限问题。

---

## 十三、八大记忆类型横向对比与决策矩阵

### 13.1 八大记忆类型完整对比表

| 记忆类型 | 原理 | 保留内容 | 调LLM? | Token成本 | 适用轮数 | 持久化 |
|----------|------|----------|--------|-----------|----------|--------|
| BufferMemory | 全量存 | 所有原文 | 否 | 极高 | <10轮 | 易 |
| WindowMemory | 切片存 | 最近k轮 | 否 | 低 | 任意 | 易 |
| SummaryMemory | LLM压缩 | 一段摘要 | 是/每轮 | 中 | 任意 | 中 |
| SummaryBufferMemory | 混合 | 近期原文+旧摘要 | 是/触发 | 中 | 中长 | 中 |
| EntityMemory | 实体抽取 | 各实体笔记 | 是/每轮 | 中 | 长期 | 中 |
| KGMemory | 三元组 | 关系图谱 | 是/每轮 | 高 | 长期 | 难 |
| VectorStoreRetriever | 向量检索 | 语义相关段 | 否(检索) | 低 | 长期 | 易 |
| Zep/Motorhead | 外部服务 | 自动管理 | 服务端 | 服务端 | 超长 | 易 |

### 13.2 选型评分矩阵（满分5分）

| 维度 \ 类型 | Buffer | Window | Summary | SummaryBuf | Entity | KG | Vector | Zep |
|-------------|--------|--------|---------|------------|--------|-----|--------|-----|
| 记忆完整度 | 5 | 2 | 3 | 4 | 4 | 4 | 3 | 5 |
| Token经济性 | 1 | 5 | 4 | 4 | 3 | 2 | 4 | 4 |
| 长期记忆 | 1 | 1 | 4 | 3 | 5 | 5 | 5 | 5 |
| 实现简单度 | 5 | 5 | 4 | 3 | 2 | 1 | 3 | 4 |
| 生产成熟度 | 4 | 4 | 3 | 5 | 2 | 1 | 4 | 3 |
| 成本可控 | 2 | 5 | 3 | 4 | 3 | 2 | 4 | 3 |

### 13.3 按业务场景推荐

| 业务场景 | 推荐记忆 | 理由 |
|----------|----------|------|
| 客服工单咨询 | Window+RAG | 轮次短，靠知识库 |
| 陪伴型AI | SummaryBuffer+Vector | 长对话+跨天记忆 |
| 个人助理 | Entity+Vector | 记用户画像与偏好 |
| 代码助手 | Window | 上下文短，看最近 |
| 教育辅导 | SummaryBuffer | 长对话，需连贯性 |
| 医疗问诊 | 短期+脱敏 | 隐私敏感，不能存太久 |
| 销售对话 | Entity+KG | 记客户关系与跟进 |

### 13.4 记忆演进时间线

```mermaid
timeline
    title LangChain Memory 演进
    v0.1 : ConversationChain : 记忆藏在Chain内
    v0.2 : Memory类体系 : Buffer/Window/Summary
    v0.3 : Entity/KG : 结构化记忆
    v0.4 : VectorStore记忆 : 语义检索
    v0.5 : RunnableWithMessageHistory : 现代有状态链
    v0.6 : LangGraph Checkpointer : 图状态持久化
    v0.7 : 外部服务Zep : 记忆即服务
```

### 13.5 记忆架构分层图

```mermaid
graph TB
    subgraph 应用层
        A1[对话API]
        A2[LangGraph工作流]
    end
    subgraph 编排层
        B1[RunnableWithMessageHistory]
        B2[trim_messages修剪]
    end
    subgraph 策略层
        C1[短期: Window/Buffer]
        C2[长期: Vector/Entity]
        C3[摘要: SummaryBuffer]
    end
    subgraph 存储层
        D1[Redis会话历史]
        D2[向量库长期记忆]
        D3[DB审计日志]
    end
    A1 --> B1
    A2 --> B1
    B1 --> B2
    B2 --> C1
    B2 --> C2
    B2 --> C3
    C1 --> D1
    C2 --> D2
    C3 --> D1
    C3 --> D3
```

### 13.6 与其他框架记忆方案对比

| 框架 | 记忆方案 | 特点 |
|------|----------|------|
| LangChain | Memory类+RunnableWithMessageHistory | 生态最全 |
| LangGraph | Checkpointer | 图状态，最现代 |
| LlamaIndex | Memory/聊天缓冲 | RAG为主 |
| AutoGen | 消息历史列表 | 多Agent对话 |
| CrewAI | 任务上下文 | 角色记忆 |
| Dify | 数据库会话表 | 可视化管理 |

---

> 💡 **深度讲解**：横向对比能帮你跳出"学习单个类"的视角，站在系统高度选型。没有任何一种记忆在所有维度都满分——Buffer 完整但费钱，Window 省钱但健忘，Summary 长记忆但有损，Vector 语义好但破坏时序。真实答案永远是"**组合**"。评分矩阵的价值在于让你把模糊的"我觉得这个好"变成可讨论的"这个场景下哪个维度最重要"。例如医疗问诊场景，"合规"和"成本可控"权重最高，那就选短期+脱敏；陪伴场景"记忆完整度"权重最高，那就 SummaryBuffer+Vector。
>
> **📝 精简总结**：八大记忆各有取舍，选型按业务场景定；评分矩阵六维度对比，生产首选 SummaryBuffer（平衡）或 Vector（长期）；架构分应用/编排/策略/存储四层；LangGraph Checkpointer 是现代方向；与其他框架相比 LangChain 生态最全。

---

## 十四、生产环境实战清单与深度案例

### 14.1 从0到1搭建生产级记忆系统（完整清单）

```python
"""生产级记忆系统搭建清单代码模板"""
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_community.vectorstores import Chroma
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import trim_messages

# 1. 环境配置（密钥从环境变量读，绝不硬编码）
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "prod-memory"

# 2. 模型分层：主模型强，摘要模型弱
main_llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
cheap_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 3. 短期历史：Redis
def get_short_history(user_id: str):
    return RedisChatMessageHistory(
        session_id=user_id,
        url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        ttl=86400 * 30,
    )

# 4. 长期记忆：向量库
long_vec = Chroma(
    embedding_function=OpenAIEmbeddings(),
    persist_directory="./long_term"
)

# 5. Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是专业助手"),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])

# 6. 修剪器
trimmer = trim_messages(
    max_tokens=2000, strategy="last", token_counter=main_llm,
    include_system=True, start_on="human",
)

# 7. 组装链
from langchain_core.runnables import RunnableLambda
chain = (
    RunnableLambda(lambda x: {**x, "history": trimmer.invoke(x["history"])})
    | prompt | main_llm
)

# 8. 有状态包装
wrapped = RunnableWithMessageHistory(
    chain, get_short_history,
    input_messages_key="input", history_messages_key="history",
)

# 9. 健康检查
def health_check():
    try:
        get_short_history("test").add_user_message("ping")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
```

### 14.2 记忆容量规划

```python
def plan_storage(active_users: int, avg_dialogues: int,
                 avg_chars: int, retention_days: int) -> dict:
    """估算存储需求"""
    bytes_per_msg = avg_chars * 3   # UTF-8中文
    msgs_per_user = avg_dialogues * 6   # 平均每人对话消息数
    total_msgs = active_users * msgs_per_user
    total_bytes = total_msgs * bytes_per_msg
    return {
        "total_messages": total_msgs,
        "total_gb": round(total_bytes / 1024**3, 2),
        "redis_ram_gb": round(total_bytes / 1024**3 * 1.5, 2),  # 1.5倍冗余
        "retention_days": retention_days,
    }

print(plan_storage(10000, 20, 100))
# 估算1万活跃用户、每人20轮对话的存储
```

### 14.3 记忆成本预算

```python
def monthly_cost(active_users, dialogues_per_day, avg_tokens,
                 price_per_1k=0.00015):
    """估算记忆+对话的月成本"""
    total_tokens = active_users * dialogues_per_day * avg_tokens * 30
    cost = total_tokens / 1000 * price_per_1k
    summary_cost = active_users * dialogues_per_day * 200 * 30 / 1000 * 0.000015
    return {"monthly_usd": round(cost + summary_cost, 2)}

print(monthly_cost(10000, 10, 2000))
```

### 14.4 灰度发布记忆策略

```python
# 按用户分桶，灰度测试不同记忆策略
import random

def get_memory_strategy(user_id: str):
    bucket = hash(user_id) % 100
    if bucket < 50:
        return "window"      # 50% 老策略
    elif bucket < 80:
        return "summarybuf" # 30% 新策略
    else:
        return "vector"     # 20% 实验策略
```

### 14.5 A/B 测试记忆质量

```python
def ab_test(strategy_a, strategy_b, users_a, users_b, metric_fn):
    """对比两种记忆策略的指标"""
    score_a = sum(metric_fn(u) for u in users_a) / len(users_a)
    score_b = sum(metric_fn(u) for u in users_b) / len(users_b)
    return {"strategy_a": score_a, "strategy_b": score_b,
            "winner": "A" if score_a > score_b else "B"}
```

### 14.6 记忆导出与迁移（GDPR）

```python
def export_user_data(user_id: str) -> dict:
    """导出某用户全部记忆（GDPR 被遗忘权）"""
    hist = get_short_history(user_id).messages
    long = long_vec.get(where={"user": user_id})
    return {
        "short_term": [{"role": type(m).__name__, "content": m.content} for m in hist],
        "long_term": long["documents"] if long else [],
    }

def delete_user_data(user_id: str):
    """彻底删除某用户记忆"""
    get_short_history(user_id).clear()
    # 向量库按 metadata 删除
    long_vec.delete(where={"user": user_id})
```

### 14.7 多语言记忆处理

```python
# 中文记忆的 token 估算要注意：中文 token 效率低
def estimate_chinese_tokens(text: str) -> int:
    """粗略：中文1字≈1.5 token"""
    return int(len(text) * 1.5)

# 多语言对话时，摘要 Prompt 用统一语言
summary_prompt = ChatPromptTemplate.from_template(
    "用中文总结以下{lang}对话：{text}"
)
```

### 14.8 记忆与权限控制

```python
# 不同角色用户能访问不同记忆
ROLE_MEMORY_SCOPE = {
    "user": ["self"],
    "agent": ["self", "group"],
    "admin": ["self", "group", "global"],
}

def get_history_for_role(role: str, user_id: str):
    scopes = ROLE_MEMORY_SCOPE[role]
    histories = []
    if "self" in scopes:
        histories.append(RedisChatMessageHistory(session_id=user_id, ...))
    if "group" in scopes:
        histories.append(RedisChatMessageHistory(session_id=f"group_{user_id}", ...))
    return histories
```

### 14.9 记忆故障降级

```python
# 记忆服务挂了怎么办？降级为无记忆模式
def safe_invoke(chain, memory_chain, user_input, sid):
    try:
        return memory_chain.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": sid}}
        )
    except Exception as e:
        # 降级：不带记忆，保证服务可用
        return chain.invoke({"input": user_input})
```

### 14.10 记忆冷启动：新用户无历史

```python
# 新用户首次对话，注入欢迎语和引导
def welcome_first_time(history, prompt):
    if len(history.messages) == 0:
        return ChatPromptTemplate.from_messages([
            ("system", "新用户首次对话，主动介绍能力"),
            ("human", "{input}")
        ])
    return prompt
```

---

> 💡 **深度讲解**：生产落地最后一公里，全是"**工程细节**"。容量规划让你知道要申请多少 Redis 内存；成本预算让老板知道每个月要花多少钱；灰度发布让新记忆策略不至于一把全量上线翻车；GDPR 导出/删除让你能合规运营；多语言、权限、降级、冷启动，每一个都是线上踩过坑才知道要做的。其中最关键的两个理念是"**故障降级**"和"**可观测**"——记忆服务挂了，主对话不能跟着挂，要能降级为无记忆模式继续服务；同时用 LangSmith 把每次记忆操作记录下来，出了问题能回放。
>
> **📝 精简总结**：生产级记忆系统九步搭建清单；容量/成本要提前规划；灰度A/B测试新策略；GDPR导出删除合规；多语言、权限、降级、冷启动缺一不可；核心是故障可降级、全程可观测。

---

## 十五、记忆高级模式与疑难杂症

### 15.1 记忆的"分阶段总结"：按对话阶段归档

```python
class PhasedMemory:
    """按对话阶段归档：每完成一个阶段就把该阶段压成摘要"""
    def __init__(self, llm):
        self.llm = llm
        self.phases = []          # 各阶段的摘要
        self.current = []         # 当前阶段原文
        self.phase_size = 5       # 每5轮归档一次

    def save(self, user, ai):
        self.current.extend([user, ai])
        if len(self.current) >= self.phase_size * 2:
            summary = self._summarize(self.current)
            self.phases.append(summary)
            self.current = []

    def load(self):
        # 所有阶段摘要 + 当前阶段原文
        return self.phases + self.current

    def _summarize(self, msgs):
        text = "\n".join(msgs)
        return self.llm.invoke(f"总结：{text}").content
```

### 15.2 记忆的"重要性打分"：只留重要对话

```python
class ImportanceMemory:
    """给每条对话打重要性分，只保留高分"""
    def __init__(self, llm, threshold=0.6):
        self.llm = llm
        self.threshold = threshold
        self.important = []

    def score(self, user_text, ai_text):
        prompt = f"给这段对话重要性打分(0-1)：{user_text} -> {ai_text}"
        return float(self.llm.invoke(prompt).content)

    def save(self, user, ai):
        score = self.score(user, ai)
        if score >= self.threshold:
            self.important.append({"u": user, "a": ai, "score": score})
```

### 15.3 记忆的"时间衰减"：越旧越不重要

```python
import time

class TimeDecayMemory:
    """时间衰减：老对话权重低"""
    def __init__(self):
        self.records = []   # [(timestamp, user, ai)]

    def save(self, user, ai):
        self.records.append((time.time(), user, ai))

    def load_weighted(self):
        now = time.time()
        weighted = []
        for ts, u, a in self.records:
            age_hours = (now - ts) / 3600
            weight = 1 / (1 + age_hours)   # 半衰期约1小时
            weighted.append({"u": u, "a": a, "weight": round(weight, 2)})
        return weighted
```

### 15.4 记忆的"话题切换检测"

```python
TOPIC_KEYWORDS = {
    "售后": ["退货", "退款", "坏了", "质量"],
    "咨询": ["怎么用", "功能", "区别"],
    "投诉": ["投诉", "差评", "气死"],
}

def detect_topic_change(history, new_input):
    """检测话题是否切换"""
    last_topic = None
    for kw_group, words in TOPIC_KEYWORDS.items():
        if any(w in new_input for w in words):
            if last_topic and last_topic != kw_group:
                return True   # 话题变了
            last_topic = kw_group
    return False
```

### 15.5 记忆的"上下文压缩"：边压缩边用

```python
class StreamingCompressor:
    """流式压缩：边收边压缩长历史"""
    def __init__(self, llm, buffer_size=10):
        self.llm = llm
        self.buffer = []
        self.compressed = ""
        self.buffer_size = buffer_size

    def add(self, msg):
        self.buffer.append(msg)
        if len(self.buffer) >= self.buffer_size:
            new_summary = self.llm.invoke(
                f"把旧摘要和新对话合并：旧{self.compressed} 新{self.buffer}"
            ).content
            self.compressed = new_summary
            self.buffer = []
```

### 15.6 记忆疑难杂症：症状与药方

| 症状 | 诊断 | 药方 |
|------|------|------|
| 模型答非所问 | 历史注入太多干扰 | 加修剪，减少历史量 |
| 模型忽略近期 | system太长，注意力分散 | 精简system，把近期放最后 |
| 模型重复回答 | 历史里重复信息 | 去重，压缩 |
| 模型编造 | 历史缺关键信息 | 补充历史，或用工具查 |
| 响应越来越慢 | 历史越长token越多 | 摘要化，裁剪 |
| 成本越来越高 | 全量历史不压 | 上SummaryBuffer |
| 跨天失忆 | 内存历史没持久化 | 换Redis/DB |
| 串号 | session没隔离 | 用RunnableWithMessageHistory |

### 15.7 记忆的"反模式"清单

```python
# ❌ 反模式1：把所有历史塞进system prompt
bad_prompt = ChatPromptTemplate.from_messages([
    ("system", "历史：" + str(all_history)),  # 错！应该放MessagesPlaceholder
    ("human", "{input}")
])

# ✅ 正解
good_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是助手"),
    MessagesPlaceholder("history"),   # 历史放这
    ("human", "{input}")
])

# ❌ 反模式2：在循环里反复 new Memory
for msg in msgs:
    memory = ConversationBufferMemory()  # 错！每次都是新的
    memory.save_context(...)

# ✅ 正解：同一个memory实例贯穿
memory = ConversationBufferMemory()
for msg in msgs:
    memory.save_context(...)

# ❌ 反模式3：流式输出后忘记保存
async for chunk in chain.astream(...):
    print(chunk)
# 忘了 save_context！
```

### 15.8 记忆与工具调用的配合

```python
# Agent对话中，工具调用结果也要进记忆
from langchain_core.messages import ToolMessage

# 工具调用的完整轮次：
# Human -> AI(tool_call) -> ToolMessage(结果) -> AI(最终回复)
# 这四步都要进历史，否则模型下次不知道用过什么工具

agent_executor = AgentExecutor(
    agent=agent, tools=tools,
    memory=ConversationBufferWindowMemory(k=15, return_messages=True),
)
```

### 15.9 记忆的"多模态"扩展

```python
# 图片/语音对话的记忆
from langchain_core.messages import HumanMessage

# 记住用户发过的图（存URL）
def save_image_memory(memory, user_id, image_url, text):
    msg = HumanMessage(content=[
        {"type": "text", "text": text},
        {"type": "image_url", "image_url": {"url": image_url}},
    ])
    memory.chat_memory.add_message(msg)
```

### 15.10 记忆的单元测试

```python
def test_memory_basic():
    mem = ConversationBufferMemory(return_messages=True)
    mem.save_context({"input": "hi"}, {"output": "hello"})
    hist = mem.load_memory_variables({})["history"]
    assert len(hist) == 2
    assert hist[0].content == "hi"

def test_window_memory():
    mem = ConversationBufferWindowMemory(k=1)
    for i in range(5):
        mem.save_context({"input": f"q{i}"}, {"output": f"a{i}"})
    hist = mem.load_memory_variables({})["history"]
    assert "q4" in hist and "q0" not in hist

def test_session_isolation():
    s1 = get_history("u1")
    s2 = get_history("u2")
    s1.add_user_message("A的消息")
    assert len(s2.messages) == 0  # u2不受影响
```

---

> 💡 **深度讲解**：高级模式本质是在解决"**记忆质量**"这个软问题。分阶段总结应对长对话的归档；重要性打分应对"不是所有对话都值得记"；时间衰减模拟人类记忆的遗忘曲线；话题切换检测应对用户跑题；流式压缩应对边聊边长。这些都不是 LangChain 现成的类，而是需要你自己组合。反模式清单则是血泪教训——历史放错位置、Memory 实例用错、流式忘存，这些都是上线前会犯的。单元测试保障记忆逻辑改了不回归，尤其是 session 隔离这种关键行为。
>
> **📝 精简总结**：高级模式含分阶段归档、重要性打分、时间衰减、话题检测、流式压缩；八大症状药方表覆盖答非所问到串号；反模式三条：历史别塞system、Memory实例要复用、流式后要存；工具调用完整轮次要进历史；记忆逻辑要写单元测试。

---

## 十六、Memory API 速查手册与完整对照

### 16.1 所有 Memory 类导入路径速查

```python
# 短期记忆
from langchain.memory import ConversationBufferMemory
from langchain.memory import ConversationBufferWindowMemory
from langchain.memory import ConversationSummaryMemory
from langchain.memory import ConversationSummaryBufferMemory

# 长期记忆
from langchain.memory import ConversationEntityMemory
from langchain.memory import ConversationKGMemory
from langchain.memory import VectorStoreRetrieverMemory

# 外部服务
from langchain.memory import MotorheadMemory
# from langchain_zep import ZepMemory  # 或 langchain-memory

# 底层历史存储
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_postgres import PostgresChatMessageHistory

# 现代有状态链
from langchain_core.runnables.history import RunnableWithMessageHistory

# 消息与修剪
from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage, ToolMessage,
    trim_messages, get_buffer_string,
)
```

### 16.2 关键参数速查表

| 参数 | 所属类 | 类型 | 说明 |
|------|--------|------|------|
| `memory_key` | 所有 | str | 历史在Prompt中的占位符名 |
| `input_key` | BaseChatMemory | str | 用户输入字段名 |
| `output_key` | BaseChatMemory | str | 模型输出字段名 |
| `return_messages` | BaseChatMemory | bool | 返回消息列表还是字符串 |
| `k` | WindowMemory | int | 保留最近轮数 |
| `max_token_limit` | SummaryBuffer | int | 触发摘要的token阈值 |
| `llm` | Summary/Entity/KG | BaseChatModel | 做摘要/抽取的模型 |
| `human_prefix` | Buffer | str | 用户消息前缀 |
| `ai_prefix` | Buffer | str | AI消息前缀 |
| `session_id` | 外部存储 | str | 会话标识 |
| `ttl` | Redis | int | 过期秒数 |
| `chat_memory` | BaseChatMemory | BaseChatMessageHistory | 底层存储 |

### 16.3 三种集成方式对比

```mermaid
graph TB
    subgraph 方式1旧版[旧版 ConversationChain]
        M1[Memory对象] --> C1[ConversationChain<br/>自动存取]
    end
    subgraph 方式2LCEL[LCEL手动版]
        M2[Memory对象] --> P2[手动load/save]
        P2 --> C2[prompt|model|parser]
    end
    subgraph 方式3现代[现代 RunnableWithMessageHistory]
        H3[get_history工厂] --> W3[RunnableWithMessageHistory<br/>自动存取+session]
        W3 --> C3[LCEL链]
    end
```

| 集成方式 | 自动存取 | 多会话 | 推荐度 |
|----------|----------|--------|--------|
| ConversationChain | ✅ | ❌ 需自己包 | 遗留 |
| LCEL手动 | ❌ | 自己写 | 灵活 |
| **RunnableWithMessageHistory** | ✅ | ✅ | **⭐推荐** |
| LangGraph Checkpointer | ✅ | ✅ | 现代复杂流程 |

### 16.4 Memory 与 Chain 的输入输出契约

```python
# 一个 Memory 期望链的输入字典长这样：
# {"input": "用户的问题", ...其他字段}
# Memory.save_context(inputs={"input": ...}, outputs={"output": ...})

# 所以链的输出必须是 dict，且包含 output_key 字段
# 如果你用 StrOutputParser，输出是 str，不是 dict！
# 此时需要：
from operator import itemgetter

chain = prompt | llm | {"output": StrOutputParser()} | itemgetter("output")
# 或直接在 RunnableWithMessageHistory 里处理
```

### 16.5 常见导入错误修复

```python
# ❌ 错误1：从错误的包导入
# from langchain.memory import ChatMessageHistory  # 旧路径
# ✅ 正确
from langchain_core.chat_history import InMemoryChatMessageHistory

# ❌ 错误2：langchain-community 没装
# ModuleNotFoundError: langchain_community
# ✅ 安装
# pip install langchain-community redis

# ❌ 错误3：Postgres 记忆包名变了
# ✅ 新版
# pip install langchain-postgres
```

### 16.6 完整状态：从零到对话结束的全时序

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant API
    participant W as RunnableWithMessageHistory
    participant Redis
    participant Prompt
    participant LLM
    participant Vector

    User->>API: POST /chat {input, session_id}
    API->>W: invoke({input}, config={session_id})
    W->>Redis: 取历史
    Redis-->>W: messages
    W->>W: trim_messages 修剪
    W->>Vector: 召回长期记忆
    Vector-->>W: relevant_docs
    W->>Prompt: 组装(历史+长期+本轮)
    Prompt->>LLM: 调用
    LLM-->>W: 流式输出
    W->>Redis: 保存本轮
    W-->>API: SSE 流式返回
    API-->>User: 逐字显示
```

### 16.7 一份生产级对话配置模板

```python
PROD_CONFIG = {
    "model": "gpt-4o",
    "summary_model": "gpt-4o-mini",
    "history_storage": "redis",
    "redis_url": "redis://prod-redis:6379/0",
    "session_ttl_days": 30,
    "trim_max_tokens": 2000,
    "summary_trigger_tokens": 1500,
    "vector_long_term": True,
    "vector_top_k": 3,
    "streaming": True,
    "langsmith_trace": True,
    "sanitize": True,
    "fallback_to_stateless": True,
}
```

---

> 💡 **深度讲解**：API 速查手册的价值是"**用到时能快速查到**"，而不是"全部背下来"。真正需要记住的就三件事：① Memory 的两个核心方法 load/save；② return_messages 和 memory_key 两个关键参数；③ 现代用 RunnableWithMessageHistory。其他参数在需要时查。时序图把一次完整对话拆成 9 步，你在排查问题时可以对号入座——是历史没取到？还是修剪太狠？还是向量没召回？定位到哪一步，问题就解决了一半。生产配置模板把所有决策收敛到一处，方便 review 和切换环境。
>
> **📝 精简总结**：API 速查含导入路径/关键参数/三种集成方式/输入输出契约/导入错误修复；全时序9步帮助排查；生产配置模板把所有决策收敛到一处；记住三件事就够：load/save、return_messages、RunnableWithMessageHistory。

---

## 十七、完整项目实战：从需求到上线

### 17.1 需求分析：一个"AI面试官"的记忆设计

```
需求：AI面试官与求职者多轮对话，记住求职者简历信息，跨多轮追问。
关键记忆点：
1. 求职者说过的项目经历（不能重复问）
2. 求职者的技能栈（针对性追问）
3. 面试进度（问了哪些、还差哪些）
```

```python
# 设计：短期Window管对话流 + 长期Vector管简历事实 + 显式槽位管进度
from langchain_core.runnables import RunnableLambda

# 显式槽位（不靠LLM记忆，用代码管）
interview_slots = {
    "projects": [],      # 项目经历
    "skills": [],        # 技能
    "questions_asked": [],
    "stage": "intro",
}

def extract_facts(text: str):
    """从回答中抽取结构化事实"""
    prompt = ChatPromptTemplate.from_template("""
    从求职者回答抽取项目和技能，输出JSON：
    回答：{text}
    格式：{{"projects":[...], "skills":[...]}}
    """)
    result = (prompt | llm | StrOutputParser()).invoke({"text": text})
    import json
    return json.loads(result)

# 每次回答后更新槽位
def after_answer(slots, answer):
    facts = extract_facts(answer)
    slots["projects"].extend(facts.get("projects", []))
    slots["skills"].extend(facts.get("skills", []))
    return slots
```

### 17.2 记忆驱动的追问策略

```python
def next_question(slots, llm):
    """根据已掌握的信息，生成下一个追问"""
    prompt = ChatPromptTemplate.from_template("""
    你是面试官。已了解：{projects} {skills}
    已问过：{questions_asked}
    生成下一个有深度的追问（不要重复已问过的）：
    """)
    return (prompt | llm).invoke(slots).content
```

### 17.3 面试结束自动生成评估

```python
def evaluate_interview(slots, llm):
    """面试结束，根据记忆生成评估报告"""
    prompt = ChatPromptTemplate.from_template("""
    根据以下面试记录生成评估报告：
    项目：{projects}
    技能：{skills}
    输出：评分/优势/不足/建议
    """)
    return (prompt | llm | StrOutputParser()).invoke(slots)
```

### 17.4 记忆驱动的个性化推荐

```python
# 记住用户偏好，下次个性化
def recommend(user_id, vec_store):
    prefs = vec_store.similarity_search(user_id, k=5)
    prompt = ChatPromptTemplate.from_template(
        "根据用户偏好{prefs}推荐3个商品："
    )
    return (prompt | llm).invoke({"prefs": prefs})
```

### 17.5 记忆的"复盘"功能

```python
def review_conversation(history, llm):
    """对话结束，自动复盘总结"""
    prompt = ChatPromptTemplate.from_template("""
    总结这次对话：
    1. 用户主要诉求
    2. 已解决/未解决
    3. 后续跟进建议
    对话：{history}
    """)
    return (prompt | llm | StrOutputParser()).invoke(
        {"history": history.messages}
    )
```

### 17.6 记忆容量与成本曲线

```python
# 经验：不同记忆策略的成本随对话轮数增长曲线
# Buffer: 线性增长 y = x * avg_cost
# Window: 恒定（k轮封顶）
# Summary: 每轮+1次摘要，略高于Window
# SummaryBuffer: 前期恒定，超阈值后略增

def cost_curve(turns, strategy):
    if strategy == "buffer":
        return turns * 0.001
    elif strategy == "window":
        return 0.005   # 封顶
    elif strategy == "summarybuf":
        return 0.005 + (turns // 10) * 0.0001
```

### 17.7 记忆选型的最终决策口诀

```
短对话（<10轮）：Buffer
中对话（10-30轮）：SummaryBuffer
长对话（30+轮）：SummaryBuffer + Vector
跨会话/长期：Vector + Entity
多实例部署：Redis 持久化
复杂Agent流程：LangGraph Checkpointer
```

### 17.8 学习路径建议

| 阶段 | 学习内容 | 目标 |
|------|----------|------|
| 入门 | Buffer/Window + 手动存取 | 理解记忆本质 |
| 进阶 | SummaryBuffer + RunnableWithMessageHistory | 生产可用 |
| 高级 | Vector/Entity + 混合记忆 | 长期记忆 |
| 专家 | LangGraph Checkpointer + 自研策略 | 掌控任意场景 |

---

> 💡 **深度讲解**：AI 面试官这个案例把"记忆"从技术组件变成了业务能力——记住求职者说过什么，才能不重复提问、才能针对性追问、才能最后写出有依据的评估。这恰恰是 LLM 记忆的真正价值：**让对话有连续性，让交互有累积性**。显式槽位（projects/skills）和记忆（对话流）分工明确——结构化的、需要精确判断的用代码管槽位，模糊的、需要语义连贯的用 LLM 记忆。这种"结构化状态 + 非结构化记忆"的双轨制，是所有复杂对话系统的通用范式。
>
> **📝 精简总结**：AI面试官案例展示结构化槽位+非结构化记忆双轨制；记忆驱动追问、推荐、复盘；成本曲线随轮数增长；决策口诀按轮数选型；学习路径从Buffer到LangGraph Checkpointer四阶段。

---

## 十八、记忆机制常见疑问 FAQ

### FAQ1：Memory 和 LangGraph 的 Checkpointer 是什么关系？

```
答：Checkpointer 是 LangGraph 对"记忆"的现代重写。
传统 Memory：作为链的属性，黑盒存取。
Checkpointer：作为图的状态，显式保存到 checkpoint。
两者本质都是"存历史、取历史"，但 Checkpointer 更灵活：
- 可保存任意状态（不只是消息）
- 可回放、可分支
- 持久化到 Postgres/SQLite
新项目推荐 LangGraph + Checkpointer。
```

### FAQ2：为什么我的 Memory 调了 save_context 但 Prompt 里没有？

```python
# 检查清单：
# 1. memory_key 和 Prompt 占位符一致吗？
# 2. 用 RunnableWithMessageHistory 时，history_messages_key 对吗？
# 3. load_memory_variables 的调用结果真的注入了吗？

# 调试：打印最终 Prompt
final = prompt.invoke({
    "history": memory.load_memory_variables({})["history"],
    "input": "test"
})
print(final.to_string())  # 看历史在不在
```

### FAQ3：SummaryMemory 和 SummaryBufferMemory 哪个贵？

```
SummaryMemory：每存一轮都调一次 LLM 摘要 → 始终贵
SummaryBufferMemory：未超阈值时不调 LLM → 短对话便宜，长对话才贵
结论：不确定对话多长时，SummaryBuffer 更省钱。
```

### FAQ4：多个 Memory 能同时用吗？

```python
# 可以，用 RunnablePassthrough.assign 注入多个变量
chain = (
    RunnablePassthrough.assign(
        recent=lambda x: recent_mem.load_memory_variables(x)["history"],
        profile=lambda x: vector_mem.load_memory_variables(x)["relevant"],
    )
    | ChatPromptTemplate.from_messages([
        ("system", "画像：{profile}"),
        MessagesPlaceholder("recent"),
        ("human", "{input}")
    ])
    | llm
)
```

### FAQ5：Memory 是线程安全的吗？

```
答：默认的 InMemoryChatMessageHistory 不是线程安全的。
多线程并发访问同一个 memory 实例可能出问题。
生产用 Redis/SQL（外部存储自带并发控制）。
```

### FAQ6：怎么清空某个用户的记忆？

```python
# 方式1：Redis
RedisChatMessageHistory(session_id=uid, url=...).clear()

# 方式2：RunnableWithMessageHistory
# 需要在 get_history 暴露的对象上调 clear
# 方式3：LangGraph
graph.update_state(config, None)  # 或 delete
```

### FAQ7：记忆能存文件/图片吗？

```python
# 可以，但要存 URL/路径，不要存二进制本身
# 向量库存描述文本，图片用消息内容的多模态格式
HumanMessage(content=[{"type":"image_url","image_url":{"url":"..."}}])
```

### FAQ8：Memory 的 token 是怎么算的？

```python
from langchain_core.messages import count_tokens_approximately
# 粗算：字符数 / 2（英文），中文约字符数 * 1.5
# 精确：用模型的 tokenizer（如 tiktoken）
import tiktoken
enc = tiktoken.encoding_for_model("gpt-4o")
print(len(enc.encode("你的文本")))
```

### FAQ9：能不能只保留 system 消息，自动清用户消息？

```python
def keep_system_only(history):
    return [m for m in history if isinstance(m, SystemMessage)]
# 配合 trim_messages 的 filter
```

### FAQ10：生产上要不要用 LangChain 的 Memory 类？

```
答：新项目推荐 RunnableWithMessageHistory 或 LangGraph。
旧版 Memory 类（ConversationBufferMemory 等）仍可用，
但功能迭代重心已转到 Checkpointer 和显式状态管理。
学习时仍要掌握，因为老代码和教程里到处都是。
```

---

> 💡 **深度讲解**：FAQ 是从"学习"到"实战"的桥梁。最关键的认知是：**Memory 的本质没变，只是实现形式从"黑盒组件"演进到"显式状态"**。理解了 load/save 两个方法，你就理解了所有 Memory 类的内核，也能快速判断任何教程/文档里的代码是新是旧。生产决策上，记住"RunnableWithMessageHistory 解决多会话短期记忆，LangGraph Checkpointer 解决复杂流程长期状态"这个分工就够了。
>
> **📝 精简总结**：FAQ 覆盖Checkpointer关系、调试Prompt、成本对比、多Memory组合、线程安全、清空、多模态、token计算、system保留、生产选型十个高频疑问；核心认知是Memory本质未变，只是从黑盒组件演进为显式状态。

---

## 十九、记忆机制完整知识图谱

### 19.1 知识总览图

```mermaid
mindmap
  root((LangChain Memory))
    核心概念
      BaseMemory
      load_memory_variables
      save_context
      memory_key
      input/output_key
    短期记忆
      Buffer全量
      Window窗口
      Summary摘要
      SummaryBuffer混合
    长期记忆
      Entity实体
      KG知识图谱
      Vector向量
      Zep外部服务
    集成方式
      ConversationChain旧版
      RunnableWithMessageHistory现代
      LangGraph Checkpointer
    持久化
      Redis
      SQL/Postgres
      File
    工程要点
      修剪trim
      脱敏
      多会话隔离
      可观测
      故障降级
```

### 19.2 一张图总结记忆选型

```mermaid
graph LR
    A[记忆需求] --> B{对话长度?}
    B|短| C[Buffer/Window]
    B|中| D[SummaryBuffer]
    B|长| E{需要跨会话?}
    E|是| F[Vector+Redis]
    E|否| D
    F --> G{需要关系?}
    G|是| H[Entity/KG]
    G|否| F
```

### 19.3 与其他章节的关系

| 关联章节 | 关系 |
|----------|------|
| LangChain核心抽象 | Memory是七大抽象之一 |
| LCEL表达式 | Memory通过RunnableWithMessageHistory接入LCEL |
| OutputParser | 记忆加载后喂给Prompt，输出经Parser |
| LangGraph State | Checkpointer是现代记忆实现 |
| RAG架构 | 长期记忆常配合向量检索 |

### 19.4 记忆术语表

| 术语 | 英文 | 释义 |
|------|------|------|
| 记忆 | Memory | 对话历史的存取组件 |
| 会话 | Session | 一次独立对话上下文 |
| 会话ID | session_id | 多会话隔离标识 |
| 修剪 | Trimming | 裁剪历史到预算内 |
| 摘要 | Summary | 用LLM压缩旧历史 |
| 情景记忆 | Episodic | 按时间记发生过什么 |
| 语义记忆 | Semantic | 按结构记事实关系 |
| 向量记忆 | Vector Memory | 语义检索的长期记忆 |
| 检查点 | Checkpoint | LangGraph的状态快照 |
| 有状态链 | Stateful Chain | 带记忆的可运行链 |

### 19.5 记忆的"十条军规"

```
1. 永远显式指定 memory_key / input_key / output_key
2. 聊天模型用 return_messages=True + MessagesPlaceholder
3. 生产用 Redis 持久化，别用内存
4. 多用户必用 session_id 隔离
5. 长对话必做修剪或摘要
6. 摘要用便宜模型，回答用强模型
7. 流式先收全再保存
8. 敏感数据先脱敏再存长期记忆
9. 用 LangSmith trace 排查记忆问题
10. 新项目优先 RunnableWithMessageHistory / LangGraph
```

---

> 💡 **深度讲解**：知识图谱和术语表把前面所有零散知识点收束成一张网。你会发现记忆领域的术语其实都来自认知科学——情景记忆、语义记忆、联想记忆，LLM 工程只是在工程上复现人类记忆的不同侧面。十条军规则是把所有踩坑浓缩成可执行的 checklist，新人照着做能避开 90% 的问题。学到这里，你应该能回答三个终极问题：① 为什么 LLM 需要外部记忆（无状态）；② 不同 Memory 类的本质差异（怎么整理历史）；③ 生产怎么选（长度×成本×持久化）。
>
> **📝 精简总结**：知识图谱收束全部知识点；术语表对齐中英概念；与LCEL/LangGraph/RAG关联；十条军规是可执行checklist；三个终极问题：无状态本质、整理方式差异、生产选型。

---

## 二十、记忆机制实践检验：15道自测题

### 基础自测（理解概念）

**Q1**：Memory 抽象的两个核心方法是什么？分别在什么时候调用？

<details><summary>答案</summary>`load_memory_variables` 在调用链之前加载历史；`save_context` 在调用链之后保存本轮。</details>

**Q2**：`return_messages=True` 必须配合哪个 Prompt 组件？

<details><summary>答案</summary>必须配合 `MessagesPlaceholder(variable_name=...)`，因为它接收消息列表。</details>

**Q3**：ConversationBufferWindowMemory 的 `k=3` 保留几条消息？

<details><summary>答案</summary>3个问答对 = 6条消息（3 Human + 3 AI）。</details>

**Q4**：ConversationSummaryBufferMemory 靠什么决定何时压缩？

<details><summary>答案</summary>靠 `max_token_limit`，当历史 token 估算超过阈值时把最早对话合并进滚动摘要。</details>

### 进阶自测（原理与设计）

**Q5**：为什么 SummaryMemory 每次对话会触发两次 LLM 调用？

<details><summary>答案</summary>一次用于回答用户，一次用于把新对话合并进滚动摘要。</details>

**Q6**：多用户部署时，为什么内存 Memory 一定不行？

<details><summary>答案</summary>内存不共享、重启即失、多副本不一致，必须用 Redis/SQL 等外部存储并按 session_id 隔离。</details>

**Q7**：VectorStoreRetrieverMemory 和 RAG 的检索有什么异同？

<details><summary>答案</summary>原理相同（向量相似度），但前者检索的是"自己与用户的对话历史"，后者检索的是"外部知识库文档"。</details>

**Q8**：RunnableWithMessageHistory 如何实现多会话隔离？

<details><summary>答案</summary>通过 `config.configurable.session_id` 调用 `get_session_history(session_id)` 工厂函数，每个 id 对应独立的历史存储。</details>

### 实战自测（排错与设计）

**Q9**：模型不记得之前说的话，第一步怎么排查？

<details><summary>答案</summary>打印 `load_memory_variables({})` 的返回，确认历史里有没有之前的内容；再检查 memory_key 与 Prompt 占位符是否一致。</details>

**Q10**：上线后成本飙升，怀疑是摘要记忆导致的，怎么定位？

<details><summary>答案</summary>看 LangSmith trace 每次对话是否触发两次 LLM 调用；把摘要模型换成 gpt-4o-mini 或提高 max_token_limit 减少触发。</details>

**Q11**：用户 A 问"我叫什么"，模型答出用户 B 的名字，为什么？

<details><summary>答案</summary>session_id 没传或传错，两个用户共用了同一份历史。检查调用时 config 里的 session_id。</details>

**Q12**：流式输出后半截模型回复被存进记忆了，怎么修？

<details><summary>答案</summary>先把所有 chunk 累加成完整字符串，流结束后再 save_context，不要边流边存。</details>

### 设计自测（架构决策）

**Q13**：要做一个能跨月记住用户偏好的 AI 助手，记忆怎么设计？

<details><summary>答案</summary>短期用 Redis 存近期对话（TTL 30天）；长期用向量库存用户偏好/画像，按语义召回；近期对话用 trim_messages 压到预算内。</details>

**Q14**：医疗问诊场景，记忆设计要注意什么？

<details><summary>答案</summary>隐私脱敏（身份证/病历）、最短必要留存期、可导出可删除（合规）、不把敏感信息写进长期向量库。</details>

**Q15**：为什么说"LLM 记忆不适合存精确数据"？

<details><summary>答案</summary>LLM 擅长模糊关联，不擅长精确查询；订单号、余额、库存等精确数据应通过工具调用实时查，而非靠记忆。</details>

---

> 💡 **深度讲解**：15 道自测题覆盖了从概念到设计的完整光谱。基础题检验你懂不懂"是什么"，进阶题检验你懂不懂"为什么"，实战题检验你会不会"排错"，设计题检验你能不能"做决策"。能全部答对，说明你对 LangChain Memory 的理解已经到了生产可用水平。最后再强调一次：记忆不是银弹，它的上限取决于你对业务对话特征的理解——想清楚"要记住什么、忘记什么、什么时候压缩"，比记住 API 更重要。
>
> **📝 精简总结**：15道自测题分基础/进阶/实战/设计四层；全部答对即生产可用；记忆设计核心是想清楚记什么、忘什么、何时压缩；LLM记忆不替代精确数据查询。

---

## 二十一、记忆机制扩展阅读与资源

### 21.1 关键源码位置索引

```
langchain_core/chat_history/       # BaseChatMessageHistory 基类
langchain_core/runnables/history.py # RunnableWithMessageHistory
langchain/memory/                  # 各 Memory 子类
langchain_community/chat_message_histories/ # Redis/SQL/File 实现
```

### 21.2 记忆相关的环境变量

```python
import os
os.environ["OPENAI_API_KEY"] = "..."
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "memory-prod"
```

### 21.3 最小可运行记忆示例（30行）

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_messages([
    ("system", "助手"),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])
store = {}
chain = RunnableWithMessageHistory(
    prompt | llm,
    lambda sid: store.setdefault(sid, InMemoryChatMessageHistory()),
    input_messages_key="input",
    history_messages_key="history",
)
chain.invoke({"input": "我叫周八"}, config={"configurable": {"session_id": "1"}})
print(chain.invoke({"input": "我叫什么"}, config={"configurable": {"session_id": "1"}}).content)
```

### 21.4 记忆的版本演进备忘

| 版本 | 变化 |
|------|------|
| 0.1 | ConversationChain + Memory |
| 0.2 | 引入 RunnableWithMessageHistory |
| 0.3 | langchain.memory 标记为兼容API |
| 0.4+ | 推荐 LangGraph Checkpointer |

### 21.5 一句话总结记忆机制

> **Memory = 把对话历史在每次请求时注入 Prompt 的可插拔策略；选 Buffer 还是 Summary、用 Redis 还是内存、短期窗口还是长期向量，本质都是在"记忆精度 × Token 成本 × 遗忘程度"这个三角里找你的平衡点。**

---

> 💡 **深度讲解**：扩展阅读是为了让你在需要深入实现时知道往哪看。源码位置帮你定位 bug；环境变量帮你快速配环境；最小示例帮你 30 行跑通；版本备忘帮你判断网上教程的新旧。一句话总结把整个章节压缩成可记住的核心。
>
> **📝 精简总结**：扩展阅读含源码位置/环境变量/最小示例/版本演进/一句话总结；核心是"精度×成本×遗忘"三角平衡。

---

## 二十二、记忆机制常见安装与依赖问题

### 22.1 安装依赖速查

```bash
# 核心
pip install langchain langchain-core langchain-openai

# 社区集成（Redis/SQL 历史）
pip install langchain-community redis

# Postgres
pip install langchain-postgres psycopg2-binary

# 向量库
pip install langchain-chroma faiss-cpu

# LangGraph（现代记忆）
pip install langgraph
```

### 22.2 版本兼容矩阵

| 包 | 推荐版本 | 说明 |
|----|----------|------|
| langchain | >=0.2 | 主包 |
| langchain-core | >=0.2 | 核心抽象 |
| langchain-openai | >=0.1 | OpenAI集成 |
| langchain-community | >=0.2 | 第三方集成 |
| langgraph | >=0.1 | 图编排 |

### 22.3 常见 ImportError 修复

```python
# ❌ ModuleNotFoundError: No module named 'langchain_community'
# ✅ pip install langchain-community

# ❌ ImportError: cannot import name 'ChatMessageHistory'
# ✅ from langchain_core.chat_history import InMemoryChatMessageHistory

# ❌ ImportError: cannot import name 'ConversationBufferMemory'
# ✅ from langchain.memory import ConversationBufferMemory
```

### 22.4 调试技巧：逐字段打印

```python
def debug_memory(memory, inputs):
    """完整调试一个 Memory"""
    print("=== Memory 调试 ===")
    print("memory_variables:", memory.memory_variables)
    loaded = memory.load_memory_variables(inputs)
    print("loaded:", loaded)
    for k, v in loaded.items():
        print(f"  {k}: {v}")
    if hasattr(memory, 'chat_memory'):
        print("messages:", memory.chat_memory.messages)
```

---

> 💡 **深度讲解**：安装与依赖问题是新手第一道坎。LangChain 拆成多个包后，版本不兼容是高频问题。建议用虚拟环境、锁版本。调试时逐字段打印是最朴素有效的手段——把 memory_variables、loaded、messages 都打出来，问题一眼可见。
>
> **📝 精简总结**：安装分核心/社区/向量/LangGraph四组包；版本要对齐；ImportError 多为路径变更；调试靠逐字段打印 memory_variables/loaded/messages。

---

## 二十三、结语：从会用 Memory 到用好 Memory

### 23.1 三个层次

```
第一层：会用 —— 知道选哪个类、怎么接进链
第二层：用好 —— 知道修剪/持久化/隔离/降级
第三层：用透 —— 知道记忆是业务能力，不是技术组件
```

### 23.2 记住这张图就够了

```mermaid
graph LR
    U[用户输入] --> LOAD[加载历史]
    LOAD --> TRIM[修剪/摘要]
    TRIM --> PROMPT[组装Prompt]
    PROMPT --> LLM[调用模型]
    LLM --> SAVE[保存本轮]
    SAVE --> U
    style LOAD fill:#e3f2fd
    style SAVE fill:#e8f5e9
```

### 23.3 最后的话

Memory 看似是 LangChain 里相对小的一个组件，但它直接决定了对话产品的"温度"——没有记忆的 AI 是冰冷的问答机，有了好记忆它才像一个真正认识你的伙伴。希望这篇文档让你不仅"会调 API"，更能"想清楚为什么这样设计"。

---

> 💡 **深度讲解**：从"会用"到"用透"，差的是业务理解。技术组件永远服务于产品目标——你做的是客服就要高效解决问题，做陪伴就要有温度地记住偏好，做面试就要记住履历不重复问。记忆策略没有最优，只有最匹配。
>
> **📝 精简总结**：三个层次：会用→用好→用透；核心循环是加载→修剪→组装→调用→保存；记忆决定对话产品的"温度"；策略匹配业务目标才是好设计。

---

## 二十四、记忆机制速查卡（打印贴墙版）

### 24.1 选型决策一句话

```
短对话用Buffer，长对话用SummaryBuffer，跨会话用Vector+Redis，
复杂流程用LangGraph Checkpointer。
```

### 24.2 接入三步

```python
# 1. 建历史工厂
def get_hist(sid): return RedisChatMessageHistory(sid, url="redis://...")
# 2. 建链
chain = prompt | llm
# 3. 包装
wrapped = RunnableWithMessageHistory(chain, get_hist,
    input_messages_key="input", history_messages_key="history")
# 4. 调用带session
wrapped.invoke({"input": "你好"}, config={"configurable": {"session_id": "u1"}})
```

### 24.3 必查清单

- [ ] memory_key 与 Prompt 占位符一致
- [ ] return_messages=True 配合 MessagesPlaceholder
- [ ] 持久化用 Redis/SQL
- [ ] session_id 隔离
- [ ] 有修剪/摘要
- [ ] 流式先收全再存
- [ ] 敏感数据脱敏
- [ ] LangSmith 追踪

---

> 💡 **深度讲解**：速查卡是给实战时"贴墙"用的。选型一句话、接入三步、必查清单，覆盖 90% 的日常场景。剩下的 10% 特殊需求，回到正文相应章节深挖。
>
> **📝 精简总结**：速查卡含选型一句话/接入三步/必查清单；覆盖90%日常场景；特殊需求回正文深挖。

---

## 二十五、记忆机制收尾：一页纸总结

### 25.1 全章核心一句话

> Memory 让无状态的 LLM 在每次请求时重新获得对话历史，是多轮对话的基石；选哪种记忆，本质是在"记住多少、花多少钱、忘多快"之间做业务权衡。

### 25.2 你应该带走的五句话

1. LLM 无状态，记忆是应用层把历史塞进 Prompt 的工程问题。
2. 所有 Memory 都靠 load_memory_variables（调用前）和 save_context（调用后）工作。
3. Buffer 全量贵、Window 便宜忘、Summary 长但损、SummaryBuffer 是甜点。
4. 多会话必须 session_id 隔离，生产用 Redis 持久化。
5. 新项目用 RunnableWithMessageHistory 或 LangGraph Checkpointer。

---

> 💡 **深度讲解**：一页纸总结是为了让你合上文档后还能回忆起全貌。五句话分别回答了"为什么需要""怎么工作""怎么选""怎么部署""怎么用新方法"。
>
> **📝 精简总结**：核心一句话+带走五句；覆盖为什么/怎么工作/怎么选/怎么部署/怎么用新方法。

---

## 二十六、梯度练习题（附答案）

### 基础题

**题1**：为什么说 LLM 本身是"无状态"的？Memory 解决的核心工程问题是什么？

<details>
<summary>👉 点击查看答案</summary>
LLM 每次 API 调用都是独立的，不会自动保留上一次调用的内容。Memory 解决的是"如何把历史对话在每次请求时重新注入 Prompt"的工程问题，让应用层在无状态模型之上构建出有状态的多轮对话体验。
</details>

**题2**：`return_messages=True` 和 `False` 有什么区别？分别配合什么用？

<details>
<summary>👉 点击查看答案</summary>
`False`（默认）把历史拼成字符串（如 "Human: ...\nAI: ..."），适合纯文本 Prompt Template；`True` 返回 `List[BaseMessage]`（HumanMessage/AIMessage 对象），必须配合 `MessagesPlaceholder` 使用，是聊天模型的标准姿势。
</details>

**题3**：ConversationBufferMemory 和 ConversationBufferWindowMemory 的本质区别？

<details>
<summary>👉 点击查看答案
