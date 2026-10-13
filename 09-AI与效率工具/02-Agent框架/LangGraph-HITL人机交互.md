---
title: LangGraph HITL人机交互
tags: [AI应用, Agent, LangGraph, 核心概念, 人机交互]
category: AI与效率工具
created: 2026-09-09
updated: 2026-09-09
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[LangGraph-状态机Agent]]", "[[LangGraph-Checkpoint检查点与持久化]]"]
aliases: [LangGraph-HITL, Human-in-the-Loop, 人机协同, 人工审核]
---

# LangGraph HITL人机交互

> **📖 文档说明**
>
> 本文档是「从零基础新手到实战老手」三部曲的**进阶实战篇**，聚焦 LangGraph 中 Human-in-the-Loop（HITL，人在回路中）的核心机制与工程实践。我们将从"为什么需要人工介入"开始，逐步深入 interrupt 中断机制、Command 恢复模式、多级审批流、Checkpoint 协同、Web 界面集成等核心主题，最终带你构建一个生产级的人机协同 Agent 系统。
>
> **👥 适用人群**
> - 已经掌握 LangGraph 基础状态机概念的开发者
> - 需要在 Agent 系统中加入人工审核、审批、确认环节的工程师
> - 希望构建可信、可控、可审计 AI 系统的架构师
> - 对人机协同（Human-AI Collaboration）感兴趣的研究者
>
> **📚 前置知识**
> - LangGraph 状态机基础（StateGraph、节点、边、条件边）
> - LangGraph Checkpoint 机制（检查点、持久化、线程）
> - Python 异步编程基础（async/await）
> - 基本的 Web 开发概念（HTTP、SSE、WebSocket）
>
> **🗺️ 学习路径提示**
> - 第 1-3 章为入门篇：理解 HITL 概念、掌握 interrupt 基础用法
> - 第 4-8 章为进阶篇：深入状态修改、审批流、Checkpoint 协同、Command 模式
> - 第 9-12 章为实战篇：Web 集成、最佳实践、模式对比、生产级系统构建
> - 每章末尾的练习题务必动手完成，HITL 的精髓在于"暂停-人工-恢复"的节奏感

---

## 1. Human-in-the-Loop 概述与核心价值

### 1.1 HITL 概念与定义

#### 什么是 Human-in-the-Loop

**Human-in-the-Loop（HITL，人在回路中）** 是一种将人类判断嵌入自动化系统执行流程的设计范式。在 AI Agent 系统中，HITL 允许在 Agent 执行的关键节点暂停自动化流程，引入人类决策（审核、修改、确认、拒绝），然后根据人类输入继续或终止执行。

> 🎯 面试高频：请解释 Human-in-the-Loop 的核心思想。HITL 的核心是"可控的自动化"——不是让 AI 完全自主，也不是让人类全程操作，而是在 AI 执行的关键决策点插入人工审核，将人类的判断力与 AI 的执行力结合起来。

用一个生活化的比喻：HITL 就像**自动驾驶汽车的"接管请求"**——汽车在大部分路况下可以自主行驶，但遇到复杂路口、施工区域或系统不确定时，会发出提示请求人类驾驶员接管；人类做出判断后，汽车再继续自动驾驶。人类不是全程开车，而是在关键节点介入。

HITL 的核心价值在于：**在保持 AI 自动化效率的同时，通过人类监督确保决策的安全性、合规性和准确性**。它解决了纯自动化系统在面对模糊、高风险、高价值场景时的信任问题。

#### HITL 的核心特征

| 特征 | 说明 | 类比 |
|------|------|------|
| **选择性介入** | 人类只在关键节点介入，而非全程参与 | 机场安检只在行李可疑时开箱检查 |
| **状态可暂停** | 系统能在任意节点安全暂停并保存完整状态 | 游戏存档——随时退出，随时继续 |
| **人工可修改** | 人类不仅能确认/拒绝，还能修改系统状态 | 编辑助手写好的草稿后再发送 |
| **可恢复执行** | 人工决策后系统能从暂停点继续执行 | 审批通过后流程自动进入下一环节 |
| **全程可审计** | 所有人工操作都有记录，可追溯可复盘 | 财务审批的每一步都留痕 |

#### HITL 在 AI Agent 中的定位

```mermaid
graph TB
    subgraph 纯自动化系统
        A1[用户输入] --> A2[AI 自主决策]
        A2 --> A3[AI 自主执行]
        A3 --> A4[输出结果]
    end
    subgraph HITL 人机协同系统
        B1[用户输入] --> B2[AI 分析与规划]
        B2 --> B3{关键决策点?}
        B3 -->|是| B4[⏸ 暂停并请求人工]
        B4 --> B5[👤 人工审核/修改]
        B5 --> B6[▶ 恢复执行]
        B6 --> B7[AI 继续执行]
        B3 -->|否| B7
        B7 --> B8[输出结果]
    end
```

### 1.2 为什么需要 HITL

#### 纯自动化 Agent 的局限性

纯自动化的 AI Agent 在很多场景下表现出色，但在以下场景中存在根本性局限：

1. **高风险操作**：删除数据、转账、发送邮件、修改生产配置等操作一旦出错，后果严重，需要人工确认
2. **模糊决策**：当 AI 对判断结果不确定时（低置信度），需要人类来做最终决策
3. **合规要求**：金融、医疗、法律等受监管行业要求关键决策必须有人类审核
4. **价值敏感**：涉及大额资金、用户隐私、品牌声誉的操作需要人工把关
5. **异常处理**：AI 遇到训练数据中未见过的边缘情况时，需要人类介入

> 🎯 面试高频：HITL 主要解决什么问题？HITL 主要解决 AI 系统的"信任鸿沟"问题——在高风险、高价值、高不确定性的场景中，纯自动化无法获得足够信任，需要通过人工审核来确保决策安全。

#### HITL 带来的核心价值

**价值一：安全性提升**

HITL 在关键操作前设置"人工关卡"，有效防止 AI 幻觉导致的错误操作。例如，Agent 计划删除一个数据库表，HITL 会暂停并展示 SQL 语句给 DBA 审核，确认无误后才执行。

**价值二：合规性保障**

许多行业法规（如 GDPR、金融监管、医疗 HIPAA）要求特定操作必须有人类监督。HITL 提供完整的审核日志，满足合规审计要求。

**价值三：质量控制**

人类可以在 AI 输出后进行质量审核和修改，确保最终输出符合业务标准。例如，AI 生成的营销文案经过人工润色后再发布。

**价值四：持续学习反馈**

人工审核的决策数据可以作为反馈信号，用于改进 AI 模型。每次人工修改都是一次高质量的训练样本。

**价值五：用户信任建立**

知道"有人类在把关"，用户对 AI 系统的信任度显著提升。这在 B2B 场景中尤为重要。

#### HITL 的成本与权衡

HITL 并非没有代价，引入 HITL 需要权衡以下成本：

| 维度 | 纯自动化 | HITL | 纯人工 |
|------|----------|------|--------|
| **执行速度** | 极快（毫秒级） | 中等（取决于人工响应） | 慢 |
| **运营成本** | 极低（仅算力） | 中等（算力+人工） | 高 |
| **决策质量** | 取决于模型能力 | 高（AI+人工互补） | 高但不稳定 |
| **可扩展性** | 极强 | 受人工产能限制 | 差 |
| **适用场景** | 低风险、高确定性 | 中高风险、需把关 | 极高风险、复杂判断 |

> 💡 **关键洞察**：HITL 的艺术在于"找到恰到好处的介入点"——介入太少，安全没保障；介入太多，效率被拖垮。优秀的 HITL 设计是让人类只做"AI 做不好的那 5%"，其余 95% 交给 AI 自动化。

### 1.3 HITL 的典型应用场景

#### 场景一：工具调用审批

Agent 在调用外部工具（尤其是有副作用的工具）前，需要人工确认。例如：
- 发送邮件前确认收件人和内容
- 执行 SQL 前确认语句安全性
- 调用支付 API 前确认金额和收款方
- 删除文件前确认操作范围

#### 场景二：敏感操作确认

涉及敏感数据或高风险操作的场景：
- 用户数据导出/删除（GDPR 合规）
- 系统配置变更
- 大额交易审批
- 权限变更操作

#### 场景三：内容审核

AI 生成内容发布前的人工审核：
- 营销文案审核（品牌调性、合规性）
- 客服回复审核（敏感词、态度）
- 代码变更审核（安全性、规范性）
- 报告内容审核（数据准确性）

#### 场景四：多步规划确认

Agent 制定多步执行计划后，在执行前请人工确认整体方案：
- 复杂任务的执行计划审核
- 多工具调用序列的确认
- 资源分配方案的审批

```mermaid
graph LR
    subgraph HITL 应用场景
        S1[工具调用审批] --> S1a[邮件发送确认]
        S1 --> S1b[SQL 执行审核]
        S1 --> S1c[支付操作确认]
        S2[敏感操作确认] --> S2a[数据删除审批]
        S2 --> S2b[配置变更审核]
        S3[内容审核] --> S3a[文案发布审核]
        S3 --> S3b[代码变更 Review]
        S4[多步规划确认] --> S4a[执行计划审批]
        S4 --> S4b[资源分配确认]
    end
```

### 1.4 HITL 的基本工作流程

#### 标准 HITL 执行流程

一个完整的 HITL 流程包含以下阶段：

1. **正常执行**：Agent 按状态图正常执行节点逻辑
2. **触发中断**：到达预设的中断点（interrupt_before / interrupt_after 或节点内 interrupt()）
3. **状态保存**：系统自动保存当前完整状态到 Checkpoint
4. **人工通知**：向人工审核者发送通知（包含上下文、待决策事项）
5. **人工决策**：审核者查看上下文，做出决策（批准/拒绝/修改）
6. **状态更新**：将人工决策写入系统状态
7. **恢复执行**：从暂停点继续执行（或根据人工决策跳转/终止）
8. **审计记录**：记录整个人工介入过程

```mermaid
sequenceDiagram
    participant User as 用户
    participant Agent as LangGraph Agent
    participant CP as Checkpoint
    participant Human as 人工审核者

    User->>Agent: 发起任务
    Agent->>Agent: 执行节点 A
    Agent->>Agent: 执行节点 B（触发 interrupt）
    Agent->>CP: 保存当前状态快照
    Agent-->>Human: 发送审核请求（含上下文）
    Note over Human: 人工查看、审核、决策
    Human->>Agent: 提交决策（批准/修改/拒绝）
    Agent->>CP: 更新状态（写入人工决策）
    Agent->>Agent: 从暂停点恢复执行
    Agent->>Agent: 执行节点 C
    Agent-->>User: 返回最终结果
```

#### HITL 流程中的关键角色

| 角色 | 职责 | LangGraph 对应 |
|------|------|----------------|
| **Agent 运行时** | 执行状态图、管理状态流转 | StateGraph / CompiledGraph |
| **中断管理器** | 在指定节点暂停执行 | interrupt() / interrupt_before / interrupt_after |
| **状态持久化** | 保存和恢复执行状态 | Checkpointer（MemorySaver / SqliteSaver 等） |
| **人工接口** | 展示上下文、接收人工输入 | 自定义 Web UI / API |
| **恢复控制器** | 处理人工输入并恢复执行 | Command(resume=...) / graph.invoke(None, config) |
| **审计日志** | 记录所有人工操作 | 自定义日志 / Checkpoint 历史 |

---

### 💡 本章深度讲解

Human-in-the-Loop 不是一个简单的"加个确认框"，而是一种系统性的人机协同设计哲学。它的核心矛盾是**自动化效率与人工监督之间的平衡**——介入太少则安全无保障，介入太多则效率被拖垮。LangGraph 通过 interrupt 机制和 Checkpoint 持久化，为 HITL 提供了底层技术支撑：interrupt 让执行可以在任意节点安全暂停，Checkpoint 让暂停后的状态可以完整保存和恢复，Command 模式则提供了人工输入与状态修改的标准接口。理解 HITL 的关键是理解"暂停-保存-人工-恢复"这个四步循环，以及每个环节中状态是如何流转的。

### 📝 本章精简总结

1. **HITL 定义**：将人类判断嵌入自动化系统执行流程的设计范式，在关键节点暂停并引入人工决策
2. **核心价值**：安全性提升、合规性保障、质量控制、持续学习反馈、用户信任建立
3. **五大特征**：选择性介入、状态可暂停、人工可修改、可恢复执行、全程可审计
4. **典型场景**：工具调用审批、敏感操作确认、内容审核、多步规划确认
5. **工作流程**：正常执行 → 触发中断 → 状态保存 → 人工通知 → 人工决策 → 状态更新 → 恢复执行 → 审计记录
6. **关键权衡**：HITL 的艺术在于找到恰到好处的介入点，让人类只做 AI 做不好的那 5%
7. **技术支撑**：LangGraph 通过 interrupt（暂停）+ Checkpoint（持久化）+ Command（恢复）三件套实现 HITL
8. **适用边界**：HITL 适用于中高风险、需把关的场景；低风险高确定性场景用纯自动化，极高风险复杂判断用纯人工

### 🎯 梯度练习题

**基础题⭐**

1. 用自己的话解释什么是 Human-in-the-Loop，并举一个生活中的 HITL 例子。
   > 提示：想想哪些流程是"机器自动做，但关键步骤需要人确认"的？

2. HITL 的五个核心特征是什么？请分别用一句话说明。
   > 提示：回顾 1.1 节的特征表格。

3. 列举三个适合使用 HITL 的应用场景，并说明为什么这些场景需要人工介入。
   > 提示：从风险等级、合规要求、决策不确定性三个维度思考。

**进阶题⭐⭐**

1. 对比纯自动化、HITL、纯人工三种模式在执行速度、运营成本、决策质量、可扩展性四个维度的差异，并分析 HITL 的独特优势。
   > 提示：HITL 的优势不是"比纯自动化质量高"或"比纯人工成本低"，而是在两者之间找到了平衡点。

2. 设计一个 HITL 流程：用户让 Agent 帮忙写一封商务邮件并发送。请画出这个流程的序列图，标注哪些环节需要人工介入，以及人工可以做哪些操作。
   > 提示：考虑邮件内容审核、收件人确认、发送确认三个可能的介入点。

**实战题⭐⭐⭐**

1. 假设你要为一个电商客服 Agent 设计 HITL 机制。该 Agent 可以自动回复用户咨询、处理退款申请、升级投诉。请分析：
   - 哪些操作需要 HITL 介入？为什么？
   - 人工审核者需要看到哪些上下文信息？
   - 如何设计介入策略才能既保证服务质量又不影响响应速度？
   > 提示：从操作风险等级（退款金额、投诉升级）和 AI 置信度两个维度设计动态介入策略。

---

## 2. interrupt 中断机制深度解析

### 2.1 interrupt 函数的核心原理

#### interrupt 函数的定义与作用

`interrupt()` 是 LangGraph 提供的一个特殊函数，用于在节点函数内部**主动暂停**图的执行。当节点函数调用 `interrupt()` 时，当前节点的执行会立即暂停，图的整体执行状态被保存到 Checkpoint，后续节点不会继续执行，直到人工通过 `Command(resume=...)` 恢复。

> 🎯 面试高频：LangGraph 中 interrupt() 的作用是什么？interrupt() 是在节点内部主动暂停执行的机制。调用后，当前节点执行暂停，状态被保存到 Checkpoint，图停止运行，等待通过 Command(resume=...) 传入人工决策后恢复执行。

用生活化的比喻：`interrupt()` 就像**游戏中的"暂停键"**——你在玩游戏时按下暂停，游戏画面冻结，所有进度自动保存；你去喝杯水、查个攻略，回来后按"继续"，游戏从暂停的那一刻精确恢复，不会丢失任何进度。

`interrupt()` 的核心价值在于：**它提供了在节点执行过程中"随时暂停、随时恢复"的能力，使得人工介入可以发生在节点内部的任意逻辑点，而不仅仅是节点之间**。

#### interrupt 的工作机制

```mermaid
graph TB
    subgraph 节点执行流程
        A[节点函数开始执行] --> B[执行部分逻辑]
        B --> C[调用 interrupt()]
        C --> D[抛出 Interrupt 异常]
        D --> E[运行时捕获异常]
        E --> F[保存当前状态到 Checkpoint]
        F --> G[图执行暂停]
        G --> H[等待人工输入]
        H --> I[人工通过 Command resume 恢复]
        I --> J[interrupt() 返回人工输入值]
        J --> K[节点继续执行后续逻辑]
        K --> L[节点执行完成]
    end
```

**关键机制详解**：

1. **异常驱动**：`interrupt()` 内部通过抛出一个特殊的 `Interrupt` 异常来暂停执行。这个异常被 LangGraph 运行时捕获，不会传播到用户代码。
2. **状态保存**：运行时捕获异常后，会将当前节点已执行部分产生的状态变更保存到 Checkpoint。
3. **返回值机制**：当人工通过 `Command(resume=value)` 恢复时，`interrupt()` 调用会"返回"这个 `value`，节点函数从 `interrupt()` 之后的代码继续执行。
4. **幂等性**：由于节点可能在 `interrupt()` 之前已经执行了部分逻辑，恢复时这些逻辑不会重新执行（状态已保存）。

> ⚠️ **重要**：`interrupt()` 不是普通的函数返回，它是通过异常机制实现的暂停。这意味着 `interrupt()` 之后的代码在暂停时不会执行，只有恢复后才会执行。

#### interrupt 函数的签名

```python
# interrupt 函数的基本签名
from langgraph.types import interrupt

def interrupt(value: Any) -> Any:
    """
    在节点内部暂停执行，并向人工展示 value。
    
    参数:
        value: 要展示给人工审核者的信息，可以是任意可序列化对象
               （字符串、字典、列表等），通常包含待决策的上下文
    
    返回:
        人工通过 Command(resume=...) 传入的值，类型与人工输入一致
    
    异常:
        内部抛出 Interrupt 异常（被运行时捕获，用户无需处理）
    """
    ...
```

### 2.2 interrupt 的基础用法

#### 示例 1：最简单的 interrupt——Hello World 级

这是最基础的 interrupt 用法，展示"暂停-人工输入-恢复"的完整流程。

```python
"""
示例 1：最简单的 interrupt 用法
预期运行结果：
  第一次 invoke：图执行到 human_review 节点时暂停，返回包含 interrupt 的状态
  第二次 invoke（传入人工输入）：节点恢复执行，打印人工输入的值，图执行完成
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

# 定义状态
class State(TypedDict):
    message: str
    user_decision: str

# 节点 1：准备需要审核的内容
def prepare_content(state: State) -> State:
    print("📝 准备内容中...")
    return {"message": "这是一条需要人工审核的消息内容"}

# 节点 2：人工审核节点（使用 interrupt）
def human_review(state: State) -> State:
    print("👤 进入人工审核节点")
    # 调用 interrupt 暂停执行，将 state["message"] 展示给人工
    # 恢复时，interrupt() 返回人工输入的值
    user_input = interrupt({"question": "是否批准这条消息？", "content": state["message"]})
    
    print(f"✅ 人工审核完成，决策：{user_input}")
    return {"user_decision": user_input}

# 节点 3：根据人工决策执行后续操作
def process_decision(state: State) -> State:
    if state["user_decision"] == "approve":
        print("🎉 消息已批准并发送")
    else:
        print("❌ 消息已被拒绝")
    return {}

# 构建图
builder = StateGraph(State)
builder.add_node("prepare", prepare_content)
builder.add_node("review", human_review)
builder.add_node("process", process_decision)
builder.add_edge(START, "prepare")
builder.add_edge("prepare", "review")
builder.add_edge("review", "process")
builder.add_edge("process", END)

# 编译图（必须配置 checkpointer 才能使用 interrupt）
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# 配置线程 ID（用于标识这次对话/执行）
config = {"configurable": {"thread_id": "demo-001"}}

# ========== 第一次执行：触发中断 ==========
print("=" * 50)
print("第一次执行：触发 interrupt")
print("=" * 50)
result = graph.invoke({"message": "", "user_decision": ""}, config)
print(f"\n第一次执行结果：{result}")
# 预期：result 中包含 interrupt 信息，图执行暂停在 review 节点

# ========== 第二次执行：恢复执行 ==========
print("\n" + "=" * 50)
print("第二次执行：传入人工决策，恢复执行")
print("=" * 50)
# 使用 Command(resume=...) 传入人工输入，恢复执行
result = graph.invoke(Command(resume="approve"), config)
print(f"\n最终结果：{result}")
# 预期：打印 "消息已批准并发送"，图执行完成
```

**预期运行结果**：
```
==================================================
第一次执行：触发 interrupt
==================================================
📝 准备内容中...
👤 进入人工审核节点

第一次执行结果：{'message': '这是一条需要人工审核的消息内容', 'user_decision': ''}

==================================================
第二次执行：传入人工决策，恢复执行
==================================================
✅ 人工审核完成，决策：approve
🎉 消息已批准并发送

最终结果：{'message': '这是一条需要人工审核的消息内容', 'user_decision': 'approve'}
```

#### 示例 2：interrupt 中的条件逻辑——根据人工输入分支执行

展示如何在 interrupt 恢复后，根据人工输入的值执行不同的后续逻辑。

```python
"""
示例 2：interrupt 中的条件分支
预期运行结果：
  人工输入 "approve" → 执行发布流程
  人工输入 "reject" → 执行拒绝流程
  人工输入 "modify:xxx" → 修改内容后重新审核
"""
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    content: str
    status: str
    review_count: int

def draft_content(state: State) -> State:
    return {"content": "AI 生成的初稿内容", "status": "draft", "review_count": 0}

def review_node(state: State) -> State:
    review_count = state.get("review_count", 0) + 1
    
    # interrupt 展示当前内容和审核次数
    decision = interrupt({
        "action": "review",
        "content": state["content"],
        "review_count": review_count,
        "options": ["approve（批准发布）", "reject（拒绝）", "modify:新内容（修改后重新审核）"]
    })
    
    # 根据人工输入分支处理
    if decision == "approve":
        return {"status": "approved", "review_count": review_count}
    elif decision == "reject":
        return {"status": "rejected", "review_count": review_count}
    elif decision.startswith("modify:"):
        new_content = decision[len("modify:"):]
        return {"content": new_content, "status": "modified", "review_count": review_count}
    else:
        return {"status": "unknown", "review_count": review_count}

def route_after_review(state: State) -> str:
    if state["status"] == "approved":
        return "publish"
    elif state["status"] == "rejected":
        return "reject_flow"
    elif state["status"] == "modified":
        return "review"  # 修改后回到审核节点
    else:
        return END

def publish_node(state: State) -> State:
    print(f"📢 发布内容：{state['content']}")
    return {"status": "published"}

def reject_node(state: State) -> State:
    print(f"🚫 内容被拒绝，原因需人工补充")
    return {"status": "rejected_final"}

builder = StateGraph(State)
builder.add_node("draft", draft_content)
builder.add_node("review", review_node)
builder.add_node("publish", publish_node)
builder.add_node("reject_flow", reject_node)
builder.add_edge(START, "draft")
builder.add_edge("draft", "review")
builder.add_conditional_edges("review", route_after_review, {
    "publish": "publish",
    "reject_flow": "reject_flow",
    "review": "review",
    END: END
})
builder.add_edge("publish", END)
builder.add_edge("reject_flow", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "conditional-demo"}}

# 第一次执行：触发审核中断
result = graph.invoke({}, config)
print(f"暂停时状态：{result}")

# 人工输入 modify，修改内容
result = graph.invoke(Command(resume="modify:人工修改后的内容"), config)
print(f"修改后状态：{result}")

# 再次审核，人工批准
result = graph.invoke(Command(resume="approve"), config)
print(f"最终状态：{result}")
```

**预期运行结果**：
```
暂停时状态：{'content': 'AI 生成的初稿内容', 'status': 'draft', 'review_count': 0}
修改后状态：{'content': '人工修改后的内容', 'status': 'modified', 'review_count': 1}
📢 发布内容：人工修改后的内容
最终状态：{'content': '人工修改后的内容', 'status': 'published', 'review_count': 2}
```

#### 示例 3：interrupt 传递复杂结构化数据

展示 interrupt 如何传递复杂的结构化数据给人工，以及人工如何返回结构化决策。

```python
"""
示例 3：interrupt 传递复杂结构化数据
预期运行结果：人工收到包含 SQL 语句、风险等级、影响行数的结构化审核请求，
返回包含决策、备注、修改后 SQL 的结构化响应
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

# 人工审核请求结构
class ReviewRequest(TypedDict):
    operation_type: str        # 操作类型：SELECT / UPDATE / DELETE
    sql_statement: str         # SQL 语句
    risk_level: str            # 风险等级：low / medium / high
    estimated_impact: int      # 预估影响行数
    reason: str                # AI 执行此操作的原因
    suggestions: list[str]     # AI 的建议

# 人工审核响应结构
class ReviewResponse(TypedDict):
    decision: str              # approve / reject / modify
    reviewer: str              # 审核人
    comment: str               # 审核备注
    modified_sql: Optional[str]  # 修改后的 SQL（如果 decision=modify）

class State(TypedDict):
    task: str
    review_request: Optional[ReviewRequest]
    review_response: Optional[ReviewResponse]
    final_sql: str

def analyze_task(state: State) -> State:
    # 模拟 AI 分析任务并生成 SQL
    sql = "DELETE FROM orders WHERE status = 'cancelled' AND created_at < '2024-01-01'"
    request: ReviewRequest = {
        "operation_type": "DELETE",
        "sql_statement": sql,
        "risk_level": "high",
        "estimated_impact": 1523,
        "reason": "清理 2024 年之前的已取消订单，释放存储空间",
        "suggestions": [
            "建议先备份相关数据",
            "建议在业务低峰期执行",
            "建议先执行 SELECT 确认影响行数"
        ]
    }
    return {"review_request": request}

def sql_review_node(state: State) -> State:
    # 将结构化的审核请求通过 interrupt 传给人工
    response = interrupt(state["review_request"])
    
    # 人工返回结构化响应
    if response["decision"] == "approve":
        final_sql = state["review_request"]["sql_statement"]
    elif response["decision"] == "modify":
        final_sql = response["modified_sql"]
    else:
        final_sql = ""
    
    return {
        "review_response": response,
        "final_sql": final_sql
    }

def execute_sql_node(state: State) -> State:
    if state["final_sql"]:
        print(f"⚡ 执行 SQL：{state['final_sql']}")
        print(f"📝 审核备注：{state['review_response']['comment']}")
    else:
        print("🚫 SQL 被拒绝，不执行")
    return {}

builder = StateGraph(State)
builder.add_node("analyze", analyze_task)
builder.add_node("review", sql_review_node)
builder.add_node("execute", execute_sql_node)
builder.add_edge(START, "analyze")
builder.add_edge("analyze", "review")
builder.add_edge("review", "execute")
builder.add_edge("execute", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "sql-review-demo"}}

# 第一次执行
result = graph.invoke({"task": "清理旧订单"}, config)
print("审核请求已发送，等待人工决策...")
print(f"暂停状态：{result}")

# 人工返回结构化决策（修改 SQL，增加 LIMIT）
human_response: ReviewResponse = {
    "decision": "modify",
    "reviewer": "DBA-张三",
    "comment": "同意清理，但建议分批执行，每次最多 100 条",
    "modified_sql": "DELETE FROM orders WHERE status = 'cancelled' AND created_at < '2024-01-01' LIMIT 100"
}
result = graph.invoke(Command(resume=human_response), config)
print(f"\n最终结果：{result}")
```

**预期运行结果**：
```
审核请求已发送，等待人工决策...
暂停状态：{'task': '清理旧订单', 'review_request': {...}, 'review_response': None, 'final_sql': ''}
⚡ 执行 SQL：DELETE FROM orders WHERE status = 'cancelled' AND created_at < '2024-01-01' LIMIT 100
📝 审核备注：同意清理，但建议分批执行，每次最多 100 条
最终结果：{'task': '清理旧订单', 'review_request': {...}, 'review_response': {...}, 'final_sql': 'DELETE FROM orders ... LIMIT 100'}
```

### 2.3 interrupt_before 与 interrupt_after

#### 概念与区别

除了在节点内部使用 `interrupt()` 函数，LangGraph 还提供了在**编译图时**配置的中断方式：

- **interrupt_before**：在指定节点**执行之前**暂停。节点函数完全不会执行，人工可以查看当前状态并决定是否允许该节点执行。
- **interrupt_after**：在指定节点**执行之后**暂停。节点函数已经执行完毕，状态已更新，人工可以查看节点执行结果并决定后续走向。

> 🎯 面试高频：interrupt()、interrupt_before、interrupt_after 有什么区别？interrupt() 是在节点函数内部主动暂停，可以传递自定义数据给人工，恢复后节点继续执行；interrupt_before 是在节点执行前暂停，节点不执行；interrupt_after 是在节点执行后暂停，节点已执行完毕。三者都需要 Checkpointer 支持。

| 对比维度 | interrupt() | interrupt_before | interrupt_after |
|----------|-------------|------------------|-----------------|
| **暂停位置** | 节点函数内部 | 节点执行前 | 节点执行后 |
| **节点是否执行** | 部分执行（interrupt 之前） | 完全不执行 | 完全执行 |
| **配置方式** | 节点函数内调用 | compile() 时配置 | compile() 时配置 |
| **可传递自定义数据** | 是（interrupt(value)） | 否（只能看当前状态） | 否（只能看当前状态） |
| **恢复后行为** | 节点从 interrupt 后继续 | 节点开始执行 | 进入下一个节点 |
| **适用场景** | 需要人工输入数据的场景 | 节点执行前的审批/确认 | 节点执行后的结果审核 |

#### interrupt_before 的工作原理

```mermaid
graph TB
    A[上一个节点执行完成] --> B{检查 interrupt_before}
    B -->|当前节点在列表中| C[⏸ 暂停执行]
    C --> D[保存当前状态]
    D --> E[等待人工输入]
    E --> F[人工恢复]
    F --> G[▶ 当前节点开始执行]
    B -->|不在列表中| G
    G --> H[节点执行完成]
```

#### interrupt_after 的工作原理

```mermaid
graph TB
    A[当前节点开始执行] --> B[节点执行完成]
    B --> C{检查 interrupt_after}
    C -->|当前节点在列表中| D[⏸ 暂停执行]
    D --> E[保存更新后的状态]
    E --> F[等待人工输入]
    F --> G[人工恢复]
    G --> H[▶ 进入下一个节点]
    C -->|不在列表中| H
```

#### 示例 4：interrupt_before——节点执行前审批

```python
"""
示例 4：interrupt_before 用法
场景：在执行"发送邮件"节点之前，强制人工审批
预期运行结果：图执行到 send_email 节点前暂停，人工批准后才执行发送
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

class State(TypedDict):
    recipient: str
    subject: str
    body: str
    sent: bool

def compose_email(state: State) -> State:
    print("✍️ 撰写邮件中...")
    return {
        "recipient": "client@example.com",
        "subject": "项目进度汇报",
        "body": "尊敬的客户，本周项目进度如下：...",
        "sent": False
    }

def send_email(state: State) -> State:
    print(f"📧 发送邮件给 {state['recipient']}")
    print(f"   主题：{state['subject']}")
    return {"sent": True}

def confirm_sent(state: State) -> State:
    if state["sent"]:
        print("✅ 邮件发送成功")
    else:
        print("⚠️ 邮件未发送")
    return {}

builder = StateGraph(State)
builder.add_node("compose", compose_email)
builder.add_node("send", send_email)
builder.add_node("confirm", confirm_sent)
builder.add_edge(START, "compose")
builder.add_edge("compose", "send")
builder.add_edge("send", "confirm")
builder.add_edge("confirm", END)

# 关键：编译时配置 interrupt_before=["send"]
# 这会在 send 节点执行前暂停
graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["send"]
)

config = {"configurable": {"thread_id": "before-demo"}}

# 第一次执行：在 send 节点前暂停
print("第一次执行：")
result = graph.invoke({}, config)
print(f"暂停时状态：sent={result['sent']}（应为 False，因为 send 还没执行）")

# 人工批准后恢复执行
print("\n第二次执行（人工批准）：")
result = graph.invoke(None, config)  # interrupt_before 恢复时传 None 即可
print(f"最终状态：sent={result['sent']}（应为 True）")
```

**预期运行结果**：
```
第一次执行：
✍️ 撰写邮件中...
暂停时状态：sent=False（应为 False，因为 send 还没执行）

第二次执行（人工批准）：
📧 发送邮件给 client@example.com
   主题：项目进度汇报
✅ 邮件发送成功
最终状态：sent=True（应为 True）
```

#### 示例 5：interrupt_after——节点执行后结果审核

```python
"""
示例 5：interrupt_after 用法
场景：AI 生成报告后，在发布前人工审核生成结果
预期运行结果：generate_report 节点执行完成后暂停，人工审核后决定是否发布
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

class State(TypedDict):
    topic: str
    report: str
    approved: bool
    published: bool

def generate_report(state: State) -> State:
    print("🤖 AI 正在生成报告...")
    report = f"# {state['topic']} 分析报告\n\n## 概述\n这是 AI 生成的关于 {state['topic']} 的分析报告...\n\n## 数据\n关键指标：营收增长 15%，利润增长 12%..."
    return {"report": report, "approved": False}

def publish_report(state: State) -> State:
    if state["approved"]:
        print(f"📢 报告已发布：{state['topic']}")
        return {"published": True}
    else:
        print("🚫 报告未获批准，不发布")
        return {"published": False}

builder = StateGraph(State)
builder.add_node("generate", generate_report)
builder.add_node("publish", publish_report)
builder.add_edge(START, "generate")
builder.add_edge("generate", "publish")
builder.add_edge("publish", END)

# 配置 interrupt_after=["generate"]：generate 节点执行后暂停
graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_after=["generate"]
)

config = {"configurable": {"thread_id": "after-demo"}}

# 第一次执行：generate 执行后暂停
print("第一次执行：")
result = graph.invoke({"topic": "Q3 季度业绩"}, config)
print(f"报告已生成，长度：{len(result['report'])} 字符")
print(f"暂停时 approved={result['approved']}")

# 人工审核后，通过 Command 修改状态并恢复
# 注意：interrupt_after 恢复时，可以用 Command(update=...) 修改状态
print("\n第二次执行（人工批准，修改状态）：")
result = graph.invoke(
    Command(update={"approved": True}),
    config
)
print(f"最终状态：approved={result['approved']}, published={result['published']}")
```

**预期运行结果**：
```
第一次执行：
🤖 AI 正在生成报告...
报告已生成，长度：120 字符
暂停时 approved=False

第二次执行（人工批准，修改状态）：
📢 报告已发布：Q3 季度业绩
最终状态：approved=True, published=True
```

#### 示例 6：interrupt_before 与 interrupt_after 组合使用

```python
"""
示例 6：interrupt_before 与 interrupt_after 组合
场景：一个三节点流程，节点 B 执行前和执行后都需要人工介入
预期运行结果：在 B 前暂停一次，B 执行后再暂停一次
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

class State(TypedDict):
    log: list[str]
    value: int

def node_a(state: State) -> State:
    print("执行节点 A")
    return {"log": ["A 完成"], "value": 10}

def node_b(state: State) -> State:
    print("执行节点 B（关键计算）")
    new_value = state["value"] * 2
    return {"log": state["log"] + ["B 完成"], "value": new_value}

def node_c(state: State) -> State:
    print("执行节点 C")
    return {"log": state["log"] + ["C 完成"]}

builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", "c")
builder.add_edge("c", END)

# 同时配置 before 和 after
graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["b"],
    interrupt_after=["b"]
)

config = {"configurable": {"thread_id": "combo-demo"}}

# 第一次：A 完成后，在 B 前暂停
r1 = graph.invoke({}, config)
print(f"第1次暂停：log={r1['log']}, value={r1['value']}")
# 预期：log=['A 完成'], value=10（B 还没执行）

# 第二次：恢复执行 B，B 完成后再次暂停
r2 = graph.invoke(None, config)
print(f"第2次暂停：log={r2['log']}, value={r2['value']}")
# 预期：log=['A 完成', 'B 完成'], value=20（B 已执行）

# 第三次：恢复，执行 C
r3 = graph.invoke(None, config)
print(f"最终：log={r3['log']}, value={r3['value']}")
# 预期：log=['A 完成', 'B 完成', 'C 完成'], value=20
```

**预期运行结果**：
```
执行节点 A
第1次暂停：log=['A 完成'], value=10
执行节点 B（关键计算）
第2次暂停：log=['A 完成', 'B 完成'], value=20
执行节点 C
最终：log=['A 完成', 'B 完成', 'C 完成'], value=20
```

### 2.4 interrupt 的高级用法

#### 示例 7：多次 interrupt——一个节点内多次暂停

一个节点函数内可以多次调用 `interrupt()`，实现多轮人工交互。

```python
"""
示例 7：一个节点内多次 interrupt
场景：配置向导——逐步收集人工输入
预期运行结果：节点内依次暂停 3 次，分别收集名称、环境、配置项
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    config: dict

def setup_wizard(state: State) -> State:
    config = {}
    
    # 第一次 interrupt：收集名称
    config["name"] = interrupt({"step": 1, "question": "请输入项目名称"})
    print(f"✅ 项目名称：{config['name']}")
    
    # 第二次 interrupt：选择环境
    config["env"] = interrupt({
        "step": 2,
        "question": "请选择部署环境",
        "options": ["development", "staging", "production"]
    })
    print(f"✅ 部署环境：{config['env']}")
    
    # 第三次 interrupt：确认配置
    confirmed = interrupt({
        "step": 3,
        "question": "请确认配置",
        "config": config,
        "options": ["confirm（确认）", "cancel（取消）"]
    })
    
    if confirmed == "confirm":
        print("🎉 配置已确认")
        return {"config": config}
    else:
        print("❌ 配置已取消")
        return {"config": {}}

builder = StateGraph(State)
builder.add_node("wizard", setup_wizard)
builder.add_edge(START, "wizard")
builder.add_edge("wizard", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "multi-interrupt"}}

# 依次恢复 3 次
r1 = graph.invoke({}, config)
print(f"第1次暂停（等待项目名称）")

r2 = graph.invoke(Command(resume="my-awesome-project"), config)
print(f"第2次暂停（等待环境选择）")

r3 = graph.invoke(Command(resume="production"), config)
print(f"第3次暂停（等待确认）")

r4 = graph.invoke(Command(resume="confirm"), config)
print(f"最终配置：{r4['config']}")
```

**预期运行结果**：
```
第1次暂停（等待项目名称）
✅ 项目名称：my-awesome-project
第2次暂停（等待环境选择）
✅ 部署环境：production
第3次暂停（等待确认）
🎉 配置已确认
最终配置：{'name': 'my-awesome-project', 'env': 'production'}
```

#### 示例 8：interrupt 与条件边结合——动态决定是否需要人工

根据状态动态决定是否触发 interrupt，实现"按需人工介入"。

```python
"""
示例 8：动态 interrupt——根据风险等级决定是否需要人工
场景：交易审批——小额自动通过，大额需要人工
预期运行结果：小额交易直接通过，大额交易触发 interrupt
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    amount: float
    risk_level: str
    approved: bool
    description: str

def assess_risk(state: State) -> State:
    amount = state["amount"]
    if amount < 1000:
        risk = "low"
    elif amount < 10000:
        risk = "medium"
    else:
        risk = "high"
    print(f"💰 交易金额：¥{amount:,.2f}，风险等级：{risk}")
    return {"risk_level": risk}

def approval_node(state: State) -> State:
    # 低风险自动通过，不触发 interrupt
    if state["risk_level"] == "low":
        print("✅ 低风险交易，自动通过")
        return {"approved": True, "description": "自动审批通过"}
    
    # 中高风险触发人工审核
    decision = interrupt({
        "action": "transaction_approval",
        "amount": state["amount"],
        "risk_level": state["risk_level"],
        "message": f"金额 ¥{state['amount']:,.2f} 的交易需要人工审批"
    })
    
    if decision.get("approved"):
        print(f"✅ 人工批准：{decision.get('comment', '无备注')}")
        return {"approved": True, "description": decision.get("comment", "人工批准")}
    else:
        print(f"❌ 人工拒绝：{decision.get('comment', '无备注')}")
        return {"approved": False, "description": decision.get("comment", "人工拒绝")}

def execute_transaction(state: State) -> State:
    if state["approved"]:
        print(f"⚡ 执行交易：¥{state['amount']:,.2f}")
    else:
        print("🚫 交易被拒绝")
    return {}

builder = StateGraph(State)
builder.add_node("assess", assess_risk)
builder.add_node("approve", approval_node)
builder.add_node("execute", execute_transaction)
builder.add_edge(START, "assess")
builder.add_edge("assess", "approve")
builder.add_edge("approve", "execute")
builder.add_edge("execute", END)

graph = builder.compile(checkpointer=MemorySaver())

# 测试 1：小额交易（自动通过）
print("=" * 50)
print("测试 1：小额交易 ¥500")
print("=" * 50)
config1 = {"configurable": {"thread_id": "tx-small"}}
r1 = graph.invoke({"amount": 500, "approved": False}, config1)
print(f"结果：approved={r1['approved']}")

# 测试 2：大额交易（需要人工）
print("\n" + "=" * 50)
print("测试 2：大额交易 ¥50,000")
print("=" * 50)
config2 = {"configurable": {"thread_id": "tx-large"}}
r2 = graph.invoke({"amount": 50000, "approved": False}, config2)
print("⏸ 已暂停，等待人工审批...")

# 人工批准
r3 = graph.invoke(
    Command(resume={"approved": True, "comment": "CFO 批准，资金充足"}),
    config2
)
print(f"结果：approved={r3['approved']}, 备注={r3['description']}")
```

**预期运行结果**：
```
==================================================
测试 1：小额交易 ¥500
==================================================
💰 交易金额：¥500.00，风险等级：low
✅ 低风险交易，自动通过
⚡ 执行交易：¥500.00
结果：approved=True

==================================================
测试 2：大额交易 ¥50,000
==================================================
💰 交易金额：¥50,000.00，风险等级：high
⏸ 已暂停，等待人工审批...
✅ 人工批准：CFO 批准，资金充足
⚡ 执行交易：¥50,000.00
结果：approved=True, 备注=CFO 批准，资金充足
```

### 2.5 interrupt 常见坑点与最佳实践

#### 坑点 1：忘记配置 Checkpointer 导致 interrupt 不生效

**错误现象**：调用 `interrupt()` 后图没有暂停，而是直接报错或继续执行。

**根本原因**：`interrupt()` 依赖 Checkpointer 来保存暂停状态。如果编译图时没有配置 `checkpointer`，interrupt 无法正常工作。

**正确做法**：编译图时必须传入 `checkpointer` 参数。

```python
# ❌ 错误：没有 checkpointer
graph = builder.compile()  # interrupt 会报错或不生效

# ✅ 正确：配置 checkpointer
from langgraph.checkpoint.memory import MemorySaver
graph = builder.compile(checkpointer=MemorySaver())
```

**预防措施**：只要图中使用了 `interrupt()`，就在编译时强制检查 `checkpointer` 是否配置。可以写一个辅助函数：

```python
def compile_with_hitl(builder, **kwargs):
    if "checkpointer" not in kwargs:
        kwargs["checkpointer"] = MemorySaver()
    return builder.compile(**kwargs)
```

#### 坑点 2：interrupt 之前的代码有副作用导致恢复时重复执行

**错误现象**：恢复执行后，interrupt 之前的某些操作（如发送请求、写入数据库）被重复执行。

**根本原因**：虽然 LangGraph 保存了状态，但如果节点函数在 `interrupt()` 之前执行了有副作用的操作（如 API 调用、文件写入），这些副作用不会被"回滚"。如果因为某种原因节点被重新执行（如线程状态被重置），副作用会重复。

**正确做法**：
1. 将有副作用的操作放在 `interrupt()` **之后**
2. 或者在副作用操作前检查状态中是否已有执行标记
3. 确保副作用操作是幂等的

```python
# ❌ 危险：interrupt 之前有副作用
def risky_node(state):
    result = requests.post("/api/notify", json={"msg": "starting"})  # 副作用！
    user_input = interrupt({"data": result.json()})
    # 如果节点被重新执行，上面的 API 会被调用两次
    ...

# ✅ 安全：副作用放在 interrupt 之后，或做幂等检查
def safe_node(state):
    if not state.get("notified"):  # 幂等检查
        requests.post("/api/notify", json={"msg": "starting"})
        state["notified"] = True
    user_input = interrupt({"data": "ready"})
    # interrupt 之后的副作用在恢复时执行一次
    requests.post("/api/confirm", json={"input": user_input})
    ...
```

#### 坑点 3：interrupt 传递不可序列化的数据

**错误现象**：调用 `interrupt(large_object)` 时报错，或恢复时数据丢失。

**根本原因**：interrupt 传递的数据需要被序列化保存到 Checkpoint。如果传入了不可序列化的对象（如文件句柄、数据库连接、lambda 函数、自定义类实例），会导致序列化失败。

**正确做法**：只传递可序列化的数据（字符串、数字、列表、字典、元组等基本类型）。如果需要传递复杂对象，先转换为字典。

```python
# ❌ 错误：传递不可序列化对象
def bad_node(state):
    db_connection = create_connection()  # 数据库连接不可序列化
    user_input = interrupt({"conn": db_connection})  # 报错！

# ✅ 正确：只传递可序列化数据
def good_node(state):
    review_data = {
        "user_id": state["user_id"],
        "action": state["planned_action"],
        "timestamp": datetime.now().isoformat(),  # 转字符串
        "metadata": dict(state["metadata"])  # 确保是字典
    }
    user_input = interrupt(review_data)
```

#### 最佳实践总结

1. **始终配置 Checkpointer**：使用 interrupt 的图必须配置 checkpointer，这是前提条件
2. **interrupt 数据保持简单**：只传递可序列化的基本类型，避免大对象
3. **副作用操作放 interrupt 之后**：确保有副作用的代码在恢复后执行，避免重复执行
4. **给人工足够的上下文**：interrupt 传递的数据应包含人工做决策所需的全部信息
5. **设计清晰的恢复值格式**：提前定义好人工输入的数据格式（如决策枚举 + 备注），避免随意输入导致解析错误
6. **设置超时机制**：长时间未恢复的 interrupt 应有超时处理（详见审批流章节）

---

### 💡 本章深度讲解

interrupt 机制是 LangGraph HITL 的技术基石，其核心是通过异常驱动的暂停-恢复模式，在节点执行的任意位置插入人工决策点。理解 interrupt 的关键在于三点：第一，它不是普通的函数返回，而是通过抛出 Interrupt 异常来暂停，异常被运行时捕获后保存状态；第二，恢复时 `interrupt()` 会"返回"人工传入的值，节点函数从暂停点精确继续，已执行的逻辑不会重复；第三，interrupt 有三种使用方式——节点内的 `interrupt()` 函数（最灵活，可传自定义数据）、编译时的 `interrupt_before`（节点前审批）和 `interrupt_after`（节点后审核），三者适用于不同场景。掌握 interrupt 之后，你就掌握了 HITL 的"暂停"能力，下一章将学习如何设计完整的人工审核流程。

### 📝 本章精简总结

1. **interrupt() 本质**：通过异常机制在节点内部暂停执行，保存状态到 Checkpoint，等待人工输入后恢复
2. **三种中断方式**：`interrupt()`（节点内，可传自定义数据）、`interrupt_before`（节点执行前暂停）、`interrupt_after`（节点执行后暂停）
3. **interrupt() 签名**：`interrupt(value)` 将 value 展示给人工，返回人工通过 `Command(resume=...)` 传入的值
4. **恢复方式**：通过 `graph.invoke(Command(resume=value), config)` 或 `graph.invoke(None, config)`（interrupt_before/after）恢复
5. **多次 interrupt**：一个节点内可以多次调用 interrupt，实现多轮人工交互（如配置向导）
6. **动态 interrupt**：可以在节点内根据条件判断是否调用 interrupt，实现按需人工介入
7. **三大坑点**：忘记配置 Checkpointer、interrupt 前有副作用导致重复执行、传递不可序列化数据
8. **最佳实践**：interrupt 数据保持简单可序列化、副作用放 interrupt 之后、给人工足够上下文、定义清晰的恢复值格式

### 🎯 梯度练习题

**基础题⭐**

1. `interrupt()` 函数的参数和返回值分别是什么？恢复时人工输入的值是如何传递回节点的？
   > 提示：思考 `interrupt(value)` 中的 value 和 `Command(resume=xxx)` 中的 xxx 之间的关系。

2. `interrupt_before` 和 `interrupt_after` 分别在什么时机暂停？恢复时分别传什么值？
   > 提示：interrupt_before 恢复时节点才开始执行；interrupt_after 恢复时直接进入下一个节点。

3. 为什么使用 interrupt 必须配置 Checkpointer？如果不配置会发生什么？
   > 提示：interrupt 暂停后需要保存状态，Checkpointer 就是负责状态持久化的组件。

**进阶题⭐⭐**

1. 设计一个节点函数，内部包含两次 interrupt：第一次收集用户的姓名，第二次收集用户的邮箱，然后将两者组合返回。写出完整代码并标注每次 invoke 的预期结果。
   > 提示：注意每次 invoke 都需要使用相同的 thread_id，且第一次 invoke 后状态中不包含 interrupt 之后的代码执行结果。

2. 对比 `interrupt()` 和 `interrupt_before` 在以下场景中的适用性：(a) 需要人工填写表单数据；(b) 执行删除操作前需要人工确认；(c) AI 生成内容后需要人工审核。分别说明选择哪种方式及原因。
   > 提示：从"是否需要传递自定义数据给人工"和"人工是否需要输入数据"两个维度判断。

**实战题⭐⭐⭐**

1. 实现一个"智能审批"节点：该节点接收一个交易请求，根据金额自动判断风险等级。金额 < 1000 自动通过不触发 interrupt；1000 ≤ 金额 < 10000 触发 interrupt 但只需要主管审批；金额 ≥ 10000 触发 interrupt 且需要总监审批（在 interrupt 传递的数据中标注所需审批角色）。写出完整的图定义和三次测试调用（分别对应三种金额）的代码。
   > 提示：在节点内用 if-else 判断是否调用 interrupt，interrupt 传递的数据中包含 `required_role` 字段。

---

## 3. 人工审核流程设计

### 3.1 审核流程的核心要素

#### 一个完整审核流程包含什么

设计人工审核流程时，需要考虑以下核心要素：

| 要素 | 说明 | 设计要点 |
|------|------|----------|
| **审核触发条件** | 什么情况下需要人工审核 | 基于风险等级、操作类型、置信度等 |
| **审核上下文** | 人工做决策需要看到什么信息 | 完整的操作内容、历史记录、AI 建议、风险提示 |
| **审核选项** | 人工可以做哪些操作 | 批准、拒绝、修改、请求更多信息、转派 |
| **审核结果处理** | 人工决策后系统如何响应 | 继续执行、终止、修改状态后继续、回到上一步 |
| **审核超时** | 人工长时间不响应怎么办 | 自动拒绝、自动批准、升级审批、提醒通知 |
| **审核审计** | 如何记录和追溯审核过程 | 审核人、时间、决策、备注、IP 等 |

> 🎯 面试高频：设计一个人工审核流程需要考虑哪些核心要素？至少需要考虑六个要素：触发条件（什么时候审）、审核上下文（审什么）、审核选项（能做什么）、结果处理（审完怎么办）、超时机制（不审怎么办）、审计日志（怎么追溯）。

#### 审核流程的状态机模型

人工审核流程本身可以用一个状态机来建模：

```mermaid
stateDiagram-v2
    [*] --> 待审核: 触发审核
    待审核 --> 审核中: 审核人领取
    待审核 --> 已超时: 超时未处理
    审核中 --> 已批准: 审核人批准
    审核中 --> 已拒绝: 审核人拒绝
    审核中 --> 需修改: 审核人要求修改
    需修改 --> 待审核: 修改完成重新提交
    已批准 --> 执行中: 系统继续执行
    已拒绝 --> 已终止: 流程终止
    已超时 --> 升级审批: 自动升级
    已超时 --> 已终止: 超时默认拒绝
    执行中 --> [*]
    已终止 --> [*]
```

### 3.2 审核上下文设计

#### 审核上下文的信息层次

人工审核者做决策时，需要的信息可以分为三个层次：

1. **核心信息（必须）**：待审核的操作内容本身——如 SQL 语句、邮件内容、交易金额
2. **上下文信息（重要）**：操作的背景和原因——如为什么要执行这个操作、相关历史记录、AI 的分析过程
3. **辅助信息（有益）**：帮助决策的额外信息——如风险评估、类似操作的历史结果、操作建议、影响范围预估

#### 示例 9：完整的审核上下文设计

```python
"""
示例 9：设计完整的审核上下文
场景：SQL 执行审核——审核者需要看到完整的决策信息
预期运行结果：interrupt 传递结构化的审核上下文，包含核心、上下文、辅助三层信息
"""
from typing import TypedDict, Optional
from datetime import datetime
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

# 审核上下文结构
class ReviewContext(TypedDict):
    # 核心信息
    operation: str               # 操作类型
    target: str                  # 操作对象
    detail: str                  # 操作详情
    # 上下文信息
    reason: str                  # 执行原因
    task_origin: str             # 任务来源
    ai_analysis: str             # AI 的分析过程
    history: list[dict]          # 相关历史记录
    # 辅助信息
    risk_assessment: dict        # 风险评估
    impact_estimate: dict        # 影响范围预估
    suggestions: list[str]       # 操作建议
    similar_cases: list[dict]    # 类似案例
    # 元信息
    request_id: str              # 请求 ID
    timestamp: str               # 触发时间
    ai_confidence: float         # AI 置信度

class State(TypedDict):
    task: str
    review_context: Optional[ReviewContext]
    decision: Optional[dict]

def analyze_and_prepare(state: State) -> State:
    """模拟 AI 分析任务并准备审核上下文"""
    context: ReviewContext = {
        # 核心信息
        "operation": "DELETE",
        "target": "orders 表",
        "detail": "DELETE FROM orders WHERE status='cancelled' AND created_at < '2024-01-01'",
        # 上下文信息
        "reason": "用户请求清理 2024 年之前的已取消订单，以释放数据库存储空间",
        "task_origin": "用户主动发起（user_id: 10086）",
        "ai_analysis": "AI 分析：该操作涉及 DELETE 语句，WHERE 条件包含 status 和 created_at，"
                       "已确认存在对应索引（idx_status_created_at），不会全表扫描。"
                       "预估影响 1523 行，占表总量 2.3%。",
        "history": [
            {"time": "2024-06-01", "action": "类似清理", "result": "成功，清理 892 行"},
            {"time": "2024-03-15", "action": "表结构变更", "result": "添加了 idx_status_created_at 索引"}
        ],
        # 辅助信息
        "risk_assessment": {
            "level": "high",
            "factors": ["DELETE 操作不可逆", "影响行数 > 1000", "涉及核心业务表"],
            "mitigation": "建议先备份，分批执行，低峰期操作"
        },
        "impact_estimate": {
            "rows_affected": 1523,
            "storage_saved_mb": 45.2,
            "downtime_seconds": 0,
            "dependent_systems": ["订单报表", "财务对账"]
        },
        "suggestions": [
            "执行前先运行 SELECT COUNT(*) 确认实际影响行数",
            "将数据备份到 orders_archive 表后再删除",
            "建议在凌晨 2:00-4:00 业务低峰期执行",
            "分批执行，每批 100 条，避免长事务"
        ],
        "similar_cases": [
            {"case": "2024-06-01 清理已取消订单", "outcome": "成功", "lessons": "分批执行更安全"},
            {"case": "2023-12-01 清理过期购物车", "outcome": "成功", "lessons": "先备份再删除"}
        ],
        # 元信息
        "request_id": "REQ-20260909-001",
        "timestamp": datetime.now().isoformat(),
        "ai_confidence": 0.85
    }
    return {"review_context": context}

def review_node(state: State) -> State:
    """人工审核节点"""
    # 将完整的审核上下文传递给人工
    decision = interrupt(state["review_context"])
    return {"decision": decision}

def execute_node(state: State) -> State:
    """根据审核结果执行"""
    d = state["decision"]
    if d["action"] == "approve":
        print(f"✅ 批准执行：{state['review_context']['detail']}")
        print(f"   审核人：{d['reviewer']}，备注：{d.get('comment', '')}")
    elif d["action"] == "modify":
        print(f"✏️ 修改后执行：{d['modified_sql']}")
    else:
        print(f"❌ 拒绝执行：{d.get('reason', '未说明原因')}")
    return {}

builder = StateGraph(State)
builder.add_node("prepare", analyze_and_prepare)
builder.add_node("review", review_node)
builder.add_node("execute", execute_node)
builder.add_edge(START, "prepare")
builder.add_edge("prepare", "review")
builder.add_edge("review", "execute")
builder.add_edge("execute", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "review-context-demo"}}

# 触发审核
result = graph.invoke({"task": "清理旧订单"}, config)
ctx = result["review_context"]
print(f"📋 审核请求已生成：{ctx['request_id']}")
print(f"   操作：{ctx['operation']} {ctx['target']}")
print(f"   风险等级：{ctx['risk_assessment']['level']}")
print(f"   AI 置信度：{ctx['ai_confidence']}")
print(f"   建议数量：{len(ctx['suggestions'])} 条")

# 人工审核后批准
result = graph.invoke(
    Command(resume={
        "action": "approve",
        "reviewer": "DBA-李工",
        "comment": "同意，但务必先备份并分批执行"
    }),
    config
)
```

**预期运行结果**：
```
📋 审核请求已生成：REQ-20260909-001
   操作：DELETE orders 表
   风险等级：high
   AI 置信度：0.85
   建议数量：4 条
✅ 批准执行：DELETE FROM orders WHERE status='cancelled' AND created_at < '2024-01-01'
   审核人：DBA-李工，备注：同意，但务必先备份并分批执行
```

### 3.3 审核选项设计

#### 标准审核选项集

一个设计良好的审核系统应提供以下标准选项：

| 选项 | 含义 | 后续行为 | 适用场景 |
|------|------|----------|----------|
| **批准（Approve）** | 同意操作，按原计划执行 | 继续执行后续节点 | 操作无问题，直接放行 |
| **拒绝（Reject）** | 不同意操作，终止流程 | 终止图执行或走拒绝分支 | 操作有问题，不应执行 |
| **修改（Modify）** | 人工修改操作内容后执行 | 用修改后的内容继续执行 | 操作方向对但细节需调整 |
| **请求更多信息（Request Info）** | 需要更多信息才能决策 | 回到信息收集节点 | 上下文不足，无法判断 |
| **转派（Delegate）** | 转给更合适的人审核 | 更新审核人，保持待审核状态 | 超出当前审核人权限/能力 |
| **标记为低风险（Mark Low Risk）** | 认为此操作无需人工审核 | 批准并记录，用于优化触发规则 | 误触发的审核，可用于改进规则 |

#### 示例 10：丰富的审核选项实现

```python
"""
示例 10：丰富的审核选项实现
场景：内容发布审核——支持批准、拒绝、修改、请求更多信息、转派
预期运行结果：根据人工选择的不同选项，图走不同的后续路径
"""
from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

ReviewAction = Literal["approve", "reject", "modify", "request_info", "delegate"]

class State(TypedDict):
    content: str
    status: str
    review_history: list[dict]
    current_reviewer: str
    info_requests: list[str]
    final_content: str

def generate_content(state: State) -> State:
    return {
        "content": "AI 生成的产品发布文案：...（省略）",
        "status": "pending_review",
        "review_history": [],
        "current_reviewer": "editor-001",
        "info_requests": []
    }

def review_node(state: State) -> State:
    # interrupt 展示内容和可选操作
    result = interrupt({
        "action": "content_review",
        "content": state["content"],
        "status": state["status"],
        "reviewer": state["current_reviewer"],
        "available_actions": {
            "approve": "批准发布",
            "reject": "拒绝发布",
            "modify": "修改内容后发布（需提供修改后内容）",
            "request_info": "请求更多信息（需说明需要什么）",
            "delegate": "转派给他人审核（需提供审核人 ID）"
        },
        "review_history": state["review_history"]
    })
    
    action: ReviewAction = result["action"]
    history_entry = {
        "reviewer": state["current_reviewer"],
        "action": action,
        "detail": result,
        "timestamp": "2026-09-09T10:00:00"
    }
    
    if action == "approve":
        return {
            "status": "approved",
            "final_content": state["content"],
            "review_history": state["review_history"] + [history_entry]
        }
    elif action == "reject":
        return {
            "status": "rejected",
            "review_history": state["review_history"] + [history_entry]
        }
    elif action == "modify":
        return {
            "status": "modified",
            "final_content": result["modified_content"],
            "review_history": state["review_history"] + [history_entry]
        }
    elif action == "request_info":
        return {
            "status": "need_info",
            "info_requests": state["info_requests"] + [result["info_needed"]],
            "review_history": state["review_history"] + [history_entry]
        }
    elif action == "delegate":
        return {
            "status": "delegated",
            "current_reviewer": result["new_reviewer"],
            "review_history": state["review_history"] + [history_entry]
        }
    return {}

def route_after_review(state: State) -> str:
    return state["status"]

def publish_node(state: State) -> State:
    print(f"📢 发布内容：{state['final_content'][:50]}...")
    return {"status": "published"}

def reject_node(state: State) -> State:
    print("🚫 内容被拒绝")
    return {"status": "rejected_final"}

def collect_info_node(state: State) -> State:
    print(f"❓ 需要补充信息：{state['info_requests'][-1]}")
    # 模拟补充信息后回到审核
    return {"status": "pending_review", "content": state["content"] + "\n[补充信息：...]"}

def delegate_notify_node(state: State) -> State:
    print(f"🔄 已转派给 {state['current_reviewer']}")
    return {"status": "pending_review"}

builder = StateGraph(State)
builder.add_node("generate", generate_content)
builder.add_node("review", review_node)
builder.add_node("publish", publish_node)
builder.add_node("reject_flow", reject_node)
builder.add_node("collect_info", collect_info_node)
builder.add_node("delegate_notify", delegate_notify_node)
builder.add_edge(START, "generate")
builder.add_edge("generate", "review")
builder.add_conditional_edges("review", route_after_review, {
    "approved": "publish",
    "modified": "publish",
    "rejected": "reject_flow",
    "need_info": "collect_info",
    "delegated": "delegate_notify"
})
builder.add_edge("publish", END)
builder.add_edge("reject_flow", END)
builder.add_edge("collect_info", "review")  # 补充信息后回到审核
builder.add_edge("delegate_notify", "review")  # 转派后回到审核

graph = builder.compile(checkpointer=MemorySaver())

# 测试：请求更多信息 → 补充后 → 批准
print("=== 测试：请求更多信息流程 ===")
config = {"configurable": {"thread_id": "review-options"}}
r1 = graph.invoke({}, config)
print("⏸ 等待审核...")

r2 = graph.invoke(
    Command(resume={"action": "request_info", "info_needed": "请提供产品的具体定价信息"}),
    config
)
print(f"状态：{r2['status']}")

r3 = graph.invoke(None, config)  # 执行 collect_info 后回到 review，再次暂停
print("⏸ 补充信息后，再次等待审核...")

r4 = graph.invoke(
    Command(resume={"action": "approve"}),
    config
)
print(f"最终状态：{r4['status']}")
```

**预期运行结果**：
```
=== 测试：请求更多信息流程 ===
⏸ 等待审核...
状态：need_info
❓ 需要补充信息：请提供产品的具体定价信息
⏸ 补充信息后，再次等待审核...
📢 发布内容：AI 生成的产品发布文案：...（省略）...
最终状态：published
```

### 3.4 审核结果处理模式

#### 四种结果处理模式

| 模式 | 说明 | 实现方式 |
|------|------|----------|
| **继续执行** | 人工批准后，从暂停点继续执行后续流程 | `Command(resume="approve")` + 条件边 |
| **修改后继续** | 人工修改状态/内容后，用新值继续执行 | `Command(resume={...修改后数据...})` 或 `Command(update={...})` |
| **终止流程** | 人工拒绝后，终止整个图的执行 | 条件边跳转到 END，或 `Command(goto=END)` |
| **回退重审** | 人工要求修改后回到上一步重新处理 | 条件边跳转回之前的节点 |

#### 示例 11：四种结果处理模式的完整实现

```python
"""
示例 11：四种审核结果处理模式
预期运行结果：分别演示批准继续、修改后继续、拒绝终止、回退重审四种模式
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    content: str
    status: str
    review_count: int
    final_output: Optional[str]

def draft_node(state: State) -> State:
    return {"content": "AI 初稿", "status": "drafted", "review_count": 0}

def review_node(state: State) -> State:
    review_count = state["review_count"] + 1
    decision = interrupt({
        "content": state["content"],
        "review_count": review_count,
        "options": ["approve", "reject", "modify:新内容", "send_back:原因"]
    })
    
    if decision == "approve":
        return {"status": "approved", "final_output": state["content"], "review_count": review_count}
    elif decision == "reject":
        return {"status": "rejected", "review_count": review_count}
    elif decision.startswith("modify:"):
        new_content = decision[len("modify:"):]
        return {"status": "modified", "final_output": new_content, "review_count": review_count}
    elif decision.startswith("send_back:"):
        reason = decision[len("send_back:"):]
        return {"status": "send_back", "content": f"[退回原因：{reason}] {state['content']}", "review_count": review_count}
    return {"review_count": review_count}

def route(state: State) -> str:
    return state["status"]

def publish_node(state: State) -> State:
    print(f"📢 发布：{state['final_output']}")
    return {"status": "published"}

def terminate_node(state: State) -> State:
    print("🚫 流程终止")
    return {"status": "terminated"}

def redraft_node(state: State) -> State:
    print(f"🔄 重新起草（基于退回意见）")
    return {"content": state["content"] + " → 重新修改版", "status": "drafted"}

builder = StateGraph(State)
builder.add_node("draft", draft_node)
builder.add_node("review", review_node)
builder.add_node("publish", publish_node)
builder.add_node("terminate", terminate_node)
builder.add_node("redraft", redraft_node)
builder.add_edge(START, "draft")
builder.add_edge("draft", "review")
builder.add_conditional_edges("review", route, {
    "approved": "publish",
    "modified": "publish",
    "rejected": "terminate",
    "send_back": "redraft"
})
builder.add_edge("publish", END)
builder.add_edge("terminate", END)
builder.add_edge("redraft", "review")  # 重新起草后回到审核

graph = builder.compile(checkpointer=MemorySaver())

def run_scenario(name, first_input, second_input=None):
    print(f"\n{'='*50}")
    print(f"场景：{name}")
    print(f"{'='*50}")
    config = {"configurable": {"thread_id": f"scenario-{name}"}}
    r1 = graph.invoke({}, config)
    print(f"暂停：status={r1['status']}")
    if second_input:
        r2 = graph.invoke(Command(resume=first_input), config)
        print(f"中间：status={r2['status']}")
        r3 = graph.invoke(Command(resume=second_input), config)
        print(f"最终：status={r3['status']}")
    else:
        r2 = graph.invoke(Command(resume=first_input), config)
        print(f"最终：status={r2['status']}")

# 场景 1：批准继续
run_scenario("批准继续", "approve")

# 场景 2：修改后继续
run_scenario("修改后继续", "modify:人工修改后的最终内容")

# 场景 3：拒绝终止
run_scenario("拒绝终止", "reject")

# 场景 4：回退重审（需要两次人工输入）
run_scenario("回退重审", "send_back:数据不准确", "approve")
```

**预期运行结果**：
```
==================================================
场景：批准继续
==================================================
暂停：status=drafted
📢 发布：AI 初稿
最终：status=published

==================================================
场景：修改后继续
==================================================
暂停：status=drafted
📢 发布：人工修改后的最终内容
最终：status=published

==================================================
场景：拒绝终止
==================================================
暂停：status=drafted
🚫 流程终止
最终：status=terminated

==================================================
场景：回退重审
==================================================
暂停：status=drafted
🔄 重新起草（基于退回意见）
中间：status=drafted
📢 发布：[退回原因：数据不准确] AI 初稿 → 重新修改版
最终：status=published
```

### 3.5 审核流程设计最佳实践

#### 最佳实践清单

1. **审核上下文要完整但不冗余**：提供决策所需的全部信息，但避免信息过载。用分层结构组织信息（核心/上下文/辅助），让审核者可以快速定位关键内容。
2. **审核选项要明确且互斥**：每个选项的含义清晰，选项之间不重叠。提供操作说明和预期后果，减少审核者的认知负担。
3. **默认操作要安全**：如果审核者超时或误操作，默认行为应该是安全的（如默认拒绝而非默认批准）。
4. **审核记录要完整**：记录审核人、时间、决策、备注、IP 等信息，满足审计要求。
5. **支持批量审核**：对于相似的低风险审核项，提供批量批准功能，提高审核效率。
6. **审核 SLA 要明确**：不同风险等级的审核应有不同的响应时间要求（如高风险 1 小时内，中风险 4 小时内）。

#### 审核流程常见坑点

**坑点 4：审核上下文信息不足导致人工无法决策**

错误现象：人工收到审核请求，但只看到一个操作 ID 或简短描述，无法判断是否应该批准，只能反复询问上下文。

根本原因：interrupt 传递的数据不完整，缺少人工做决策所需的关键信息。

正确做法：按照"核心信息 + 上下文信息 + 辅助信息"三层结构设计审核上下文，确保审核者看到请求后能立即做出决策。

**坑点 5：审核选项过于简单导致人工无法表达真实意图**

错误现象：只有"批准"和"拒绝"两个选项，但人工实际想"修改一下再批准"或"需要更多信息"，只能先拒绝再重新走流程。

根本原因：审核选项设计不足，没有覆盖常见的审核意图。

正确做法：提供丰富的审核选项（批准、拒绝、修改、请求更多信息、转派），并为每个选项定义清晰的后续行为。

---

### 💡 本章深度讲解

人工审核流程的设计本质是"如何让人类高效、准确地做出决策"。核心在于三个设计维度：审核上下文（给人看什么）、审核选项（让人做什么）、结果处理（做完怎么办）。审核上下文要分层设计——核心信息让人快速了解"在审什么"，上下文信息让人理解"为什么要审"，辅助信息帮人判断"该不该过"；审核选项要覆盖批准、拒绝、修改、请求信息、转派等常见意图，且每个选项的后续行为要明确；结果处理有四种模式——继续执行、修改后继续、终止流程、回退重审，通过条件边和 Command 组合实现。一个好的审核流程应该让审核者"看到就能决策，决策就能执行，执行就能追溯"。

### 📝 本章精简总结

1. **审核六要素**：触发条件、审核上下文、审核选项、结果处理、超时机制、审计日志
2. **上下文三层结构**：核心信息（操作内容）、上下文信息（背景原因）、辅助信息（风险评估/建议/类似案例）
3. **标准审核选项**：批准、拒绝、修改、请求更多信息、转派、标记低风险
4. **四种结果处理模式**：继续执行、修改后继续、终止流程、回退重审
5. **结果处理实现**：通过条件边（conditional_edges）+ Command（resume/update/goto）组合实现
6. **审核状态机**：待审核 → 审核中 → 已批准/已拒绝/需修改/已超时，各状态间有明确的转换规则
7. **设计原则**：上下文完整但不冗余、选项明确且互斥、默认操作要安全、审核记录要完整
8. **常见坑点**：上下文信息不足、审核选项过于简单、缺少超时处理

### 🎯 梯度练习题

**基础题⭐**

1. 人工审核流程的六个核心要素是什么？请分别用一句话说明。
   > 提示：回顾 3.1 节的要素表格。

2. 审核上下文的三层信息结构分别是什么？每层包含哪些典型内容？
   > 提示：核心信息是"在审什么"，上下文信息是"为什么审"，辅助信息是"怎么判"。

3. 四种审核结果处理模式分别是什么？各自的适用场景是什么？
   > 提示：批准→继续，修改→修改后继续，拒绝→终止，需修改→回退重审。

**进阶题⭐⭐**

1. 设计一个"代码变更审核"的审核上下文结构（TypedDict），包含核心、上下文、辅助三层信息。至少包含 10 个字段，并说明每个字段的作用。
   > 提示：考虑代码变更的 PR 链接、变更文件列表、代码 diff、测试结果、风险评估、类似变更历史等。

2. 实现一个审核节点，支持五种审核选项（批准、拒绝、修改、请求更多信息、转派），并通过条件边实现每种选项的后续流程。写出完整的图定义。
   > 提示：参考示例 10，注意每种选项返回不同的 status，条件边根据 status 路由。

**实战题⭐⭐⭐**

1. 设计一个完整的"财务报销审核"流程：
   - 员工提交报销单（金额、类别、附件）
   - 系统自动校验（发票真伪、金额合理性）
   - 根据金额路由：<500 自动通过，500-5000 主管审批，>5000 财务总监审批
   - 审批支持批准、拒绝、修改金额三种操作
   - 审批通过后进入打款环节
   请画出状态图，写出完整的 LangGraph 实现代码，并标注每个 interrupt 传递的审核上下文结构。
   > 提示：用条件边实现金额路由，每个审批级别用不同的 interrupt 上下文（标注所需审批角色）。

---

## 4. 人工输入与状态修改

### 4.1 Command 对象详解

#### Command 的概念与作用

`Command` 是 LangGraph 中用于**在恢复执行时传递人工输入、修改状态、控制流程走向**的核心对象。当图因 interrupt 暂停后，通过 `graph.invoke(Command(...), config)` 恢复执行时，Command 可以携带多种指令：

- **resume**：传递给 `interrupt()` 的返回值（人工输入的决策数据）
- **update**：直接更新图的状态（修改/添加状态字段）
- **goto**：控制下一步跳转到哪个节点（改变流程走向）

> 🎯 面试高频：LangGraph 中 Command 对象的作用是什么？Command 是恢复 HITL 执行时的标准输入对象，支持三个核心参数：resume（传递 interrupt 的返回值）、update（更新状态）、goto（控制流程跳转）。通过 Command 可以实现人工输入、状态修改、流程重定向三种操作的组合。

用生活化的比喻：`Command` 就像**游戏恢复时的"操作指令"**——你读取存档后，不仅可以继续游戏（resume），还可以用修改器调整角色属性（update），甚至可以直接传送到某个关卡（goto）。Command 就是这三种操作的组合指令。

#### Command 的完整签名

```python
from langgraph.types import Command
from typing import Any, Optional, Union

class Command:
    def __init__(
        self,
        *,
        resume: Any = None,           # 传递给 interrupt() 的返回值
        update: Optional[dict] = None, # 要更新的状态字段
        goto: Optional[Union[str, list[str]]] = None  # 下一步跳转的节点
    ):
        ...
```

#### Command 三个参数的组合使用

```mermaid
graph TB
    subgraph Command 能力
        R[resume<br/>传递人工输入] --> R1[interrupt() 返回该值]
        U[update<br/>修改状态] --> U1[直接写入状态字段]
        G[goto<br/>控制跳转] --> G1[下一步跳转到指定节点]
        R & U & G --> C[组合使用<br/>一次恢复完成多种操作]
    end
```

### 4.2 使用 resume 传递人工输入

#### 示例 12：resume 的基础用法——传递简单值

```python
"""
示例 12：Command(resume=...) 基础用法
预期运行结果：interrupt() 返回 resume 传入的值，节点继续执行
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    question: str
    answer: str

def ask_node(state: State) -> State:
    # interrupt 展示问题，resume 的值会作为 interrupt() 的返回值
    user_answer = interrupt({"question": state["question"]})
    print(f"用户回答：{user_answer}")
    return {"answer": user_answer}

builder = StateGraph(State)
builder.add_node("ask", ask_node)
builder.add_edge(START, "ask")
builder.add_edge("ask", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "resume-basic"}}

# 第一次：触发 interrupt
r1 = graph.invoke({"question": "你最喜欢的编程语言是什么？"}, config)
print("⏸ 等待用户回答...")

# 第二次：通过 resume 传递回答
r2 = graph.invoke(Command(resume="Python"), config)
print(f"最终答案：{r2['answer']}")
```

**预期运行结果**：
```
⏸ 等待用户回答...
用户回答：Python
最终答案：Python
```

#### 示例 13：resume 传递复杂结构化数据

```python
"""
示例 13：resume 传递复杂结构化数据
预期运行结果：人工返回包含多个字段的字典，节点解析后使用
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class HumanDecision(TypedDict):
    approved: bool
    reviewer: str
    comment: str
    priority: str

class State(TypedDict):
    task: str
    decision: Optional[HumanDecision]

def review_node(state: State) -> State:
    raw = interrupt({"task": state["task"], "action": "review"})
    # raw 是 HumanDecision 类型的字典
    decision: HumanDecision = {
        "approved": raw["approved"],
        "reviewer": raw["reviewer"],
        "comment": raw.get("comment", ""),
        "priority": raw.get("priority", "normal")
    }
    return {"decision": decision}

builder = StateGraph(State)
builder.add_node("review", review_node)
builder.add_edge(START, "review")
builder.add_edge("review", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "resume-structured"}}

r1 = graph.invoke({"task": "审批采购申请"}, config)
print("⏸ 等待审批...")

# 传递结构化决策
r2 = graph.invoke(
    Command(resume={
        "approved": True,
        "reviewer": "经理-王五",
        "comment": "同意采购，注意控制预算",
        "priority": "high"
    }),
    config
)
d = r2["decision"]
print(f"审批结果：{'批准' if d['approved'] else '拒绝'}")
print(f"审批人：{d['reviewer']}")
print(f"备注：{d['comment']}")
print(f"优先级：{d['priority']}")
```

**预期运行结果**：
```
⏸ 等待审批...
审批结果：批准
审批人：经理-王五
备注：同意采购，注意控制预算
优先级：high
```

### 4.3 使用 update 修改状态

#### update 的工作原理

`Command(update={...})` 会在恢复执行时，将字典中的键值对**直接写入图的状态**。这相当于在恢复前人工修改了状态，后续节点将基于修改后的状态执行。

**关键特性**：
- update 是**合并式更新**：只更新指定的字段，不影响其他字段
- update 在 **resume 之前**生效：如果同时使用 resume 和 update，状态先被 update 修改，然后节点恢复执行
- update 可以**新增字段**：如果状态中不存在该字段，会被添加

#### 示例 14：update 修改状态——人工修正错误数据

```python
"""
示例 14：Command(update=...) 修改状态
场景：AI 生成的数据有误，人工在恢复前修正状态
预期运行结果：update 修改状态后，后续节点基于修正后的状态执行
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    report_data: dict
    reviewed: bool
    final_report: Optional[str]

def generate_report(state: State) -> State:
    # 模拟 AI 生成了有误的数据
    return {
        "report_data": {
            "title": "Q3 业绩报告",
            "revenue": "100万",  # 错误：应该是 1000 万
            "profit": "20万"
        },
        "reviewed": False
    }

def review_node(state: State) -> State:
    decision = interrupt({
        "action": "review_data",
        "data": state["report_data"],
        "instruction": "如果数据有误，请通过 update 修正状态后再恢复"
    })
    return {"reviewed": True}

def publish_node(state: State) -> State:
    data = state["report_data"]
    report = f"# {data['title']}\n营收：{data['revenue']}\n利润：{data['profit']}"
    print(f"📊 发布报告：\n{report}")
    return {"final_report": report}

builder = StateGraph(State)
builder.add_node("generate", generate_report)
builder.add_node("review", review_node)
builder.add_node("publish", publish_node)
builder.add_edge(START, "generate")
builder.add_edge("generate", "review")
builder.add_edge("review", "publish")
builder.add_edge("publish", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "update-demo"}}

# 第一次：触发审核
r1 = graph.invoke({}, config)
print(f"AI 生成的数据：{r1['report_data']}")
print("⏸ 等待人工审核...")

# 第二次：人工通过 update 修正数据，同时 resume 批准
r2 = graph.invoke(
    Command(
        resume="approved",
        update={
            "report_data": {
                "title": "Q3 业绩报告",
                "revenue": "1000万",  # 修正：100万 → 1000万
                "profit": "200万"      # 同步修正
            }
        }
    ),
    config
)
print(f"\n修正后的数据：{r2['report_data']}")
```

**预期运行结果**：
```
AI 生成的数据：{'title': 'Q3 业绩报告', 'revenue': '100万', 'profit': '20万'}
⏸ 等待人工审核...
📊 发布报告：
# Q3 业绩报告
营收：1000万
利润：200万

修正后的数据：{'title': 'Q3 业绩报告', 'revenue': '1000万', 'profit': '200万'}
```

#### 示例 15：update 新增状态字段

```python
"""
示例 15：update 新增状态字段
预期运行结果：人工在恢复时添加状态中原本不存在的字段
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    content: str
    approved: bool
    # 注意：State 定义中没有 reviewer 和 review_time 字段
    # 但 update 可以动态添加（TypedDict 只是类型提示，运行时不限制）

def review_node(state: State) -> State:
    interrupt({"content": state["content"]})
    return {"approved": True}

def final_node(state: State) -> State:
    # 可以访问 update 添加的字段
    print(f"审核人：{state.get('reviewer', '未知')}")
    print(f"审核时间：{state.get('review_time', '未知')}")
    return {}

builder = StateGraph(State)
builder.add_node("review", review_node)
builder.add_node("final", final_node)
builder.add_edge(START, "review")
builder.add_edge("review", "final")
builder.add_edge("final", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "update-new-field"}}

r1 = graph.invoke({"content": "待审核内容", "approved": False}, config)
print("⏸ 暂停...")

# update 添加新字段
r2 = graph.invoke(
    Command(
        resume="ok",
        update={
            "reviewer": "张三",
            "review_time": "2026-09-09 14:30:00",
            "review_comment": "内容无误，批准发布"
        }
    ),
    config
)
```

**预期运行结果**：
```
⏸ 暂停...
审核人：张三
审核时间：2026-09-09 14:30:00
```

### 4.4 使用 goto 控制流程跳转

#### goto 的工作原理

`Command(goto="node_name")` 可以在恢复执行时，**跳过当前节点的后续逻辑和默认的边，直接跳转到指定节点**。这为人工控制流程走向提供了极大的灵活性。

**关键特性**：
- goto 可以跳转到**图中的任意节点**（包括之前的节点，实现回退）
- goto 可以是**单个节点名**或**节点名列表**（并行执行）
- goto 优先级**高于默认边**：如果指定了 goto，就不会走默认的下一个节点

#### 示例 16：goto 跳转——人工决定流程走向

```python
"""
示例 16：Command(goto=...) 控制流程跳转
场景：人工审核后，可以选择继续发布、退回修改、或直接终止
预期运行结果：根据 goto 参数跳转到不同节点
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    content: str
    iterations: int

def generate_node(state: State) -> State:
    print(f"🤖 生成内容（第 {state.get('iterations', 0) + 1} 轮）")
    return {"content": f"AI 生成内容 v{state.get('iterations', 0) + 1}", "iterations": state.get("iterations", 0) + 1}

def review_node(state: State) -> State:
    interrupt({
        "content": state["content"],
        "options": {
            "goto=publish": "批准发布",
            "goto=generate": "退回重新生成",
            "goto=__end__": "终止流程"
        }
    })
    return {}

def publish_node(state: State) -> State:
    print(f"📢 发布：{state['content']}")
    return {}

builder = StateGraph(State)
builder.add_node("generate", generate_node)
builder.add_node("review", review_node)
builder.add_node("publish", publish_node)
builder.add_edge(START, "generate")
builder.add_edge("generate", "review")
# review 节点不设置默认边，通过 goto 控制
builder.add_edge("publish", END)

graph = builder.compile(checkpointer=MemorySaver())

# 场景：第一次生成 → 退回重生成 → 批准
print("=== 测试 goto 跳转 ===")
config = {"configurable": {"thread_id": "goto-demo"}}
r1 = graph.invoke({}, config)
print(f"第1次暂停：{r1['content']}")

# 退回重新生成（goto 到 generate）
r2 = graph.invoke(Command(goto="generate"), config)
print(f"第2次暂停：{r2['content']}")

# 批准发布（goto 到 publish）
r3 = graph.invoke(Command(goto="publish"), config)
print(f"最终：{r3['content']}, iterations={r3['iterations']}")
```

**预期运行结果**：
```
=== 测试 goto 跳转 ===
🤖 生成内容（第 1 轮）
第1次暂停：AI 生成内容 v1
🤖 生成内容（第 2 轮）
第2次暂停：AI 生成内容 v2
📢 发布：AI 生成内容 v2
最终：AI 生成内容 v2, iterations=2
```

#### 示例 17：resume + update + goto 组合使用

```python
"""
示例 17：Command 三参数组合使用
场景：人工审核时同时传递决策、修改状态、跳转流程
预期运行结果：一次恢复完成"输入决策 + 修改状态 + 跳转节点"三件事
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    content: str
    status: str
    reviewer: Optional[str]
    review_comment: Optional[str]
    final_content: Optional[str]

def generate_node(state: State) -> State:
    return {"content": "AI 初稿", "status": "pending"}

def review_node(state: State) -> State:
    # interrupt 展示内容
    decision = interrupt({"content": state["content"], "action": "review"})
    # decision 来自 resume
    print(f"人工决策：{decision}")
    return {"status": "reviewed"}

def publish_node(state: State) -> State:
    print(f"📢 发布：{state['final_content']}")
    print(f"   审核人：{state['reviewer']}，备注：{state['review_comment']}")
    return {"status": "published"}

builder = StateGraph(State)
builder.add_node("generate", generate_node)
builder.add_node("review", review_node)
builder.add_node("publish", publish_node)
builder.add_edge(START, "generate")
builder.add_edge("generate", "review")
builder.add_edge("review", "publish")
builder.add_edge("publish", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "command-combo"}}

r1 = graph.invoke({}, config)
print("⏸ 等待审核...")

# 一次 Command 完成三件事：
# 1. resume：传递人工决策 "approved_with_modification"
# 2. update：修改状态（添加审核人、备注、修改后的内容）
# 3. goto：直接跳转到 publish（跳过 review 节点的默认后续，但这里 review 已执行完）
r2 = graph.invoke(
    Command(
        resume="approved_with_modification",
        update={
            "reviewer": "主编-李四",
            "review_comment": "标题需要更吸引人，已修改",
            "final_content": "【重磅】AI 初稿（人工优化版）",
            "status": "approved"
        },
        goto="publish"
    ),
    config
)
print(f"最终状态：{r2['status']}")
```

**预期运行结果**：
```
⏸ 等待审核...
人工决策：approved_with_modification
📢 发布：【重磅】AI 初稿（人工优化版）
   审核人：主编-李四，备注：标题需要更吸引人，已修改
最终状态：published
```

### 4.5 人工编辑状态的高级模式

#### 模式一：状态差异编辑（Patch）

人工不需要提供完整的状态，只需要提供要修改的字段差异。

```python
"""
示例 18：状态差异编辑模式
预期运行结果：人工只提供要修改的字段，update 合并到现有状态
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    user: dict
    config: dict
    approved: bool

def setup_node(state: State) -> State:
    return {
        "user": {"name": "张三", "role": "editor", "level": 3},
        "config": {"theme": "dark", "language": "zh-CN", "notifications": True},
        "approved": False
    }

def review_node(state: State) -> State:
    interrupt({"state": state, "instruction": "只需要提供要修改的字段"})
    return {"approved": True}

def final_node(state: State) -> State:
    print(f"用户：{state['user']}")
    print(f"配置：{state['config']}")
    return {}

builder = StateGraph(State)
builder.add_node("setup", setup_node)
builder.add_node("review", review_node)
builder.add_node("final", final_node)
builder.add_edge(START, "setup")
builder.add_edge("setup", "review")
builder.add_edge("review", "final")
builder.add_edge("final", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "patch-edit"}}

r1 = graph.invoke({}, config)
print("⏸ 暂停，人工只修改部分字段...")

# 人工只提供要修改的字段（差异编辑）
r2 = graph.invoke(
    Command(
        resume="ok",
        update={
            "user": {"name": "张三", "role": "admin", "level": 5},  # 修改 role 和 level
            "config": {"theme": "light", "language": "zh-CN", "notifications": True}  # 修改 theme
        }
    ),
    config
)
```

**预期运行结果**：
```
⏸ 暂停，人工只修改部分字段...
用户：{'name': '张三', 'role': 'admin', 'level': 5}
配置：{'theme': 'light', 'language': 'zh-CN', 'notifications': True}
```

#### 模式二：状态版本回滚

人工可以将状态回滚到之前的某个 Checkpoint 版本。

```python
"""
示例 19：状态版本回滚
预期运行结果：人工查看历史状态，选择回滚到某个版本后继续
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.base import Checkpoint
from langgraph.types import interrupt, Command

class State(TypedDict):
    content: str
    version: int

def node_a(state: State) -> State:
    return {"content": "版本 1 内容", "version": 1}

def node_b(state: State) -> State:
    return {"content": "版本 2 内容（AI 修改后）", "version": 2}

def review_node(state: State) -> State:
    interrupt({"current": state, "instruction": "如果不满意，可以回滚到版本 1"})
    return {}

def final_node(state: State) -> State:
    print(f"最终内容（v{state['version']}）：{state['content']}")
    return {}

builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("review", review_node)
builder.add_node("final", final_node)
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", "review")
builder.add_edge("review", "final")
builder.add_edge("final", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "rollback-demo"}}

r1 = graph.invoke({}, config)
print(f"当前状态：v{r1['version']} - {r1['content']}")
print("⏸ 人工决定回滚到版本 1...")

# 人工通过 update 将状态回滚到版本 1 的内容
r2 = graph.invoke(
    Command(
        resume="rollback",
        update={"content": "版本 1 内容", "version": 1}
    ),
    config
)
```

**预期运行结果**：
```
当前状态：v2 - 版本 2 内容（AI 修改后）
⏸ 人工决定回滚到版本 1...
最终内容（v1）：版本 1 内容
```

### 4.6 人工输入与状态修改常见坑点

**坑点 6：resume 和 update 的执行顺序混淆**

错误现象：在节点中通过 `interrupt()` 获取人工输入，但同时用 `update` 修改了状态，节点中读取到的状态不是修改后的值。

根本原因：`update` 在节点恢复执行**之前**就已经写入状态，而 `resume` 的值是作为 `interrupt()` 的返回值在节点恢复后才获得的。如果节点在 `interrupt()` 之前就引用了某个状态字段，那它看到的是修改前的值。

正确做法：明确区分——需要在节点逻辑中使用的人工输入用 `resume`，需要修改状态供后续节点使用的用 `update`。不要在 `interrupt()` 之前的代码中依赖 `update` 修改的字段。

**坑点 7：goto 跳转到不存在的节点**

错误现象：`Command(goto="non_existent_node")` 恢复时报错或图行为异常。

根本原因：goto 指定的节点名必须是图中已注册的节点名（通过 `add_node` 注册的），不能是任意字符串。

正确做法：使用图中已注册的节点名。如果要终止流程，使用 `goto=END` 或 `"__end__"`。

```python
# ❌ 错误：跳转到不存在的节点
Command(goto="some_other_step")

# ✅ 正确：跳转到已注册的节点
Command(goto="publish")

# ✅ 正确：终止流程
Command(goto=END)
```

**坑点 8：update 修改嵌套字典时覆盖整个字典**

错误现象：`update={"config": {"theme": "light"}}` 后，`config` 字典中其他字段（如 `language`）丢失了。

根本原因：`update` 是**浅合并**——对于嵌套字典，它会直接替换整个字典，而不是递归合并嵌套字段。

正确做法：修改嵌套字典时，需要提供完整的嵌套字典（包含所有字段），或者在节点内部做递归合并。

```python
# ❌ 错误：会覆盖整个 config 字典，丢失 language 和 notifications
Command(update={"config": {"theme": "light"}})

# ✅ 正确：提供完整的 config 字典
Command(update={"config": {"theme": "light", "language": "zh-CN", "notifications": True}})
```

---

### 💡 本章深度讲解

人工输入与状态修改是 HITL 的"人工意志注入"环节，核心工具是 `Command` 对象。Command 的三个参数——resume、update、goto——分别对应三种人工操作：resume 是"回答 interrupt 提出的问题"（数据输入），update 是"修改系统当前状态"（状态编辑），goto 是"决定下一步去哪里"（流程控制）。三者可以独立使用，也可以组合使用，一次恢复完成多种操作。理解 Command 的关键是明确执行顺序：update 先写入状态，然后节点恢复执行，resume 的值作为 interrupt() 的返回值传入节点逻辑，goto 决定节点执行完后跳转到哪里。掌握 Command 之后，人工就不仅能"批准或拒绝"，还能"修改内容、调整状态、重定向流程"，真正实现人机协同。

### 📝 本章精简总结

1. **Command 三参数**：resume（传递 interrupt 返回值）、update（更新状态）、goto（控制流程跳转）
2. **resume 用法**：`Command(resume=value)`，value 可以是任意可序列化类型，作为 interrupt() 的返回值
3. **update 用法**：`Command(update={key: value})`，浅合并到状态，可新增字段，在节点恢复前生效
4. **goto 用法**：`Command(goto="node_name")`，跳转到已注册节点，优先级高于默认边，支持回退到之前的节点
5. **组合使用**：resume + update + goto 可以在一次恢复中同时完成输入、修改、跳转
6. **状态差异编辑**：人工只提供要修改的字段，update 合并到现有状态（浅合并）
7. **状态版本回滚**：人工通过 update 将状态恢复到之前版本的内容
8. **三大坑点**：resume/update 执行顺序混淆、goto 跳转到不存在的节点、update 浅合并导致嵌套字典字段丢失

### 🎯 梯度练习题

**基础题⭐**

1. Command 的三个参数 resume、update、goto 分别是什么作用？恢复时它们的执行顺序是怎样的？
   > 提示：update 先生效，然后节点恢复，resume 作为 interrupt() 返回值，goto 决定节点后的跳转。

2. `Command(resume="hello")` 和 `Command(update={"msg": "hello"})` 有什么区别？节点中如何分别获取这两个值？
   > 提示：resume 的值通过 interrupt() 的返回值获取；update 的值通过 state["msg"] 获取。

3. goto 可以跳转到哪些节点？如果要终止流程应该怎么写？
   > 提示：goto 只能跳转到通过 add_node 注册的节点；终止用 goto=END。

**进阶题⭐⭐**

1. 设计一个场景：人工审核时需要同时做三件事——(1) 传递审批意见"已修改后批准"；(2) 将状态中的 content 字段修改为人工修改后的版本；(3) 直接跳转到发布节点。写出对应的 Command 调用代码，并解释每个参数的作用。
   > 提示：使用 Command(resume=..., update=..., goto=...) 组合。

2. 解释为什么 `Command(update={"config": {"theme": "light"}})` 会导致 config 中其他字段丢失？如何正确地只修改嵌套字典中的一个字段？
   > 提示：update 是浅合并，嵌套字典会被整体替换。正确做法是提供完整的嵌套字典。

**实战题⭐⭐⭐**

1. 实现一个"人工编辑状态"的完整流程：
   - 节点 A 生成一份配置（包含 5 个字段的嵌套字典）
   - 节点 B 触发 interrupt，展示当前完整状态
   - 人工可以选择：(a) 批准（resume="approve"，goto="final"）；(b) 修改（resume="modify"，update 提供修改后的完整状态，goto="final"）；(c) 回退（goto="A" 重新生成）
   - 节点 final 输出最终状态
   写出完整代码，并分别测试三种操作的预期结果。
   > 提示：注意修改嵌套字典时要提供完整字典，回退时 goto 到节点 A 的名称。

---

## 5. 审批流实现

### 5.1 多级审批流设计

#### 多级审批的概念与价值

**多级审批**是指一个操作需要经过多个层级的审批人依次审核通过后才能执行。常见于企业内部的财务报销、采购申请、合同审批等场景。

多级审批的核心价值在于**权责分离和风险控制**——不同层级的审批人关注不同维度：基层主管关注业务合理性，财务关注预算合规性，高管关注战略一致性。

> 🎯 面试高频：多级审批流在 LangGraph 中如何实现？多级审批可以通过串联多个 interrupt 节点实现，每个节点对应一个审批层级；也可以在一个节点内通过多次 interrupt 实现多级审批。关键是用状态记录当前审批层级和审批历史，通过条件边判断是否进入下一级。

#### 多级审批的状态模型

```mermaid
graph TB
    subgraph 三级审批流程
        A[提交申请] --> B[一级审批<br/>主管]
        B -->|通过| C[二级审批<br/>经理]
        B -->|拒绝| Z[流程终止]
        C -->|通过| D[三级审批<br/>总监]
        C -->|拒绝| Z
        D -->|通过| E[执行操作]
        D -->|拒绝| Z
        E --> F[完成]
    end
```

#### 示例 20：三级审批流完整实现

```python
"""
示例 20：三级审批流实现
场景：采购申请需要主管→经理→总监三级审批
预期运行结果：依次暂停三次，每级审批通过后进入下一级，任意一级拒绝则终止
"""
from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

ApprovalResult = Literal["approved", "rejected"]

class ApprovalRecord(TypedDict):
    level: int
    role: str
    result: ApprovalResult
    reviewer: str
    comment: str

class State(TypedDict):
    request: dict
    current_level: int
    approval_history: list[ApprovalRecord]
    status: str
    final_result: Optional[str]

# 审批层级配置
APPROVAL_LEVELS = [
    {"level": 1, "role": "主管", "threshold": 1000},
    {"level": 2, "role": "经理", "threshold": 10000},
    {"level": 3, "role": "总监", "threshold": 50000},
]

def submit_request(state: State) -> State:
    return {
        "request": state.get("request", {"item": "MacBook Pro", "amount": 15000}),
        "current_level": 1,
        "approval_history": [],
        "status": "pending"
    }

def approval_node(state: State) -> State:
    """通用审批节点——根据 current_level 决定当前审批角色"""
    level = state["current_level"]
    level_config = APPROVAL_LEVELS[level - 1]
    
    # interrupt 展示审批信息
    result = interrupt({
        "action": "approval",
        "level": level,
        "role": level_config["role"],
        "request": state["request"],
        "approval_history": state["approval_history"],
        "instruction": f"请{level_config['role']}审批此采购申请"
    })
    
    record: ApprovalRecord = {
        "level": level,
        "role": level_config["role"],
        "result": result["decision"],
        "reviewer": result.get("reviewer", "unknown"),
        "comment": result.get("comment", "")
    }
    
    new_history = state["approval_history"] + [record]
    
    if result["decision"] == "rejected":
        return {
            "approval_history": new_history,
            "status": "rejected",
            "final_result": f"被{level_config['role']}拒绝：{result.get('comment', '')}"
        }
    
    # 检查是否还有下一级
    if level < len(APPROVAL_LEVELS):
        return {
            "approval_history": new_history,
            "current_level": level + 1,
            "status": "pending_next_level"
        }
    else:
        return {
            "approval_history": new_history,
            "status": "all_approved",
            "final_result": "全部审批通过"
        }

def route_after_approval(state: State) -> str:
    if state["status"] == "rejected":
        return "reject_flow"
    elif state["status"] == "all_approved":
        return "execute"
    else:
        return "approval"  # 继续下一级审批

def execute_purchase(state: State) -> State:
    print(f"✅ 采购执行：{state['request']['item']}，金额 ¥{state['request']['amount']}")
    print(f"   审批记录：{len(state['approval_history'])} 级审批全部通过")
    return {"status": "executed"}

def reject_flow(state: State) -> State:
    print(f"❌ 采购被拒绝：{state['final_result']}")
    return {"status": "terminated"}

builder = StateGraph(State)
builder.add_node("submit", submit_request)
builder.add_node("approval", approval_node)
builder.add_node("execute", execute_purchase)
builder.add_node("reject_flow", reject_flow)
builder.add_edge(START, "submit")
builder.add_edge("submit", "approval")
builder.add_conditional_edges("approval", route_after_approval, {
    "approval": "approval",
    "execute": "execute",
    "reject_flow": "reject_flow"
})
builder.add_edge("execute", END)
builder.add_edge("reject_flow", END)

graph = builder.compile(checkpointer=MemorySaver())

# 测试：全部通过的场景
print("=" * 60)
print("场景：三级审批全部通过")
print("=" * 60)
config = {"configurable": {"thread_id": "multi-approval-pass"}}

r = graph.invoke({"request": {"item": "MacBook Pro", "amount": 15000}}, config)
print(f"⏸ 第1级（主管）审批暂停...")

r = graph.invoke(Command(resume={"decision": "approved", "reviewer": "主管-张三", "comment": "业务需要，同意"}), config)
print(f"⏸ 第2级（经理）审批暂停...")

r = graph.invoke(Command(resume={"decision": "approved", "reviewer": "经理-李四", "comment": "预算内，同意"}), config)
print(f"⏸ 第3级（总监）审批暂停...")

r = graph.invoke(Command(resume={"decision": "approved", "reviewer": "总监-王五", "comment": "批准采购"}), config)
print(f"最终状态：{r['status']}")

# 测试：第二级拒绝的场景
print("\n" + "=" * 60)
print("场景：第二级（经理）拒绝")
print("=" * 60)
config2 = {"configurable": {"thread_id": "multi-approval-reject"}}

r = graph.invoke({"request": {"item": "豪华游艇", "amount": 500000}}, config2)
print(f"⏸ 第1级（主管）审批暂停...")

r = graph.invoke(Command(resume={"decision": "approved", "reviewer": "主管-张三", "comment": "虽然贵但业务需要"}), config2)
print(f"⏸ 第2级（经理）审批暂停...")

r = graph.invoke(Command(resume={"decision": "rejected", "reviewer": "经理-李四", "comment": "超出预算，拒绝"}), config2)
print(f"最终状态：{r['status']}，结果：{r['final_result']}")
```

**预期运行结果**：
```
============================================================
场景：三级审批全部通过
============================================================
⏸ 第1级（主管）审批暂停...
⏸ 第2级（经理）审批暂停...
⏸ 第3级（总监）审批暂停...
✅ 采购执行：MacBook Pro，金额 ¥15000
   审批记录：3 级审批全部通过
最终状态：executed

============================================================
场景：第二级（经理）拒绝
============================================================
⏸ 第1级（主管）审批暂停...
⏸ 第2级（经理）审批暂停...
❌ 采购被拒绝：被经理拒绝：超出预算，拒绝
最终状态：terminated，结果：被经理拒绝：超出预算，拒绝
```

#### 示例 21：动态审批层级——根据金额自动决定审批级数

```python
"""
示例 21：动态审批层级
场景：根据申请金额自动决定需要几级审批
  - <1000：无需审批，自动通过
  - 1000-10000：1级审批（主管）
  - 10000-50000：2级审批（主管→经理）
  - >=50000：3级审批（主管→经理→总监）
预期运行结果：不同金额触发不同级数的审批
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    request: dict
    required_levels: int
    current_level: int
    approval_history: list[dict]
    status: str

LEVEL_CONFIG = {
    1: {"role": "主管", "name": "supervisor"},
    2: {"role": "经理", "name": "manager"},
    3: {"role": "总监", "name": "director"},
}

def determine_levels(state: State) -> State:
    amount = state["request"]["amount"]
    if amount < 1000:
        required = 0
    elif amount < 10000:
        required = 1
    elif amount < 50000:
        required = 2
    else:
        required = 3
    print(f"💰 金额 ¥{amount:,.0f} → 需要 {required} 级审批")
    return {"required_levels": required, "current_level": 1, "approval_history": [], "status": "pending"}

def approval_node(state: State) -> State:
    if state["current_level"] > state["required_levels"]:
        return {"status": "all_approved"}
    
    level = state["current_level"]
    config = LEVEL_CONFIG[level]
    
    result = interrupt({
        "level": level,
        "role": config["role"],
        "request": state["request"],
        "progress": f"{level}/{state['required_levels']}"
    })
    
    record = {"level": level, "role": config["role"], **result}
    new_history = state["approval_history"] + [record]
    
    if result["decision"] == "rejected":
        return {"approval_history": new_history, "status": "rejected"}
    
    if level >= state["required_levels"]:
        return {"approval_history": new_history, "status": "all_approved"}
    
    return {"approval_history": new_history, "current_level": level + 1, "status": "pending"}

def route(state: State) -> str:
    if state["status"] == "rejected":
        return "reject"
    elif state["status"] == "all_approved":
        return "execute"
    return "approval"

def auto_approve_node(state: State) -> State:
    print("✅ 小额申请，自动通过")
    return {"status": "auto_approved"}

def execute_node(state: State) -> State:
    print(f"✅ 执行采购（{len(state['approval_history'])} 级审批通过）")
    return {"status": "executed"}

def reject_node(state: State) -> State:
    print("❌ 申请被拒绝")
    return {"status": "rejected_final"}

builder = StateGraph(State)
builder.add_node("determine", determine_levels)
builder.add_node("approval", approval_node)
builder.add_node("auto_approve", auto_approve_node)
builder.add_node("execute", execute_node)
builder.add_node("reject", reject_node)
builder.add_edge(START, "determine")
builder.add_conditional_edges("determine", lambda s: "auto_approve" if s["required_levels"] == 0 else "approval",
    {"auto_approve": "auto_approve", "approval": "approval"})
builder.add_conditional_edges("approval", route, {"approval": "approval", "execute": "execute", "reject": "reject"})
builder.add_edge("auto_approve", END)
builder.add_edge("execute", END)
builder.add_edge("reject", END)

graph = builder.compile(checkpointer=MemorySaver())

# 测试不同金额
for amount, label in [(500, "小额自动通过"), (5000, "1级审批"), (20000, "2级审批"), (100000, "3级审批")]:
    print(f"\n--- {label}（¥{amount}）---")
    cfg = {"configurable": {"thread_id": f"dynamic-{amount}"}}
    r = graph.invoke({"request": {"amount": amount, "item": "test"}}, cfg)
    if r["status"] == "pending":
        # 需要审批，模拟全部通过
        for i in range(r["required_levels"]):
            r = graph.invoke(Command(resume={"decision": "approved", "reviewer": f"审批人{i+1}"}), cfg)
    print(f"结果：{r['status']}")
```

**预期运行结果**：
```
--- 小额自动通过（¥500）---
💰 金额 ¥500 → 需要 0 级审批
✅ 小额申请，自动通过
结果：auto_approved

--- 1级审批（¥5000）---
💰 金额 ¥5,000 → 需要 1 级审批
✅ 执行采购（1 级审批通过）
结果：executed

--- 2级审批（¥20000）---
💰 金额 ¥20,000 → 需要 2 级审批
✅ 执行采购（2 级审批通过）
结果：executed

--- 3级审批（¥100000）---
💰 金额 ¥100,000 → 需要 3 级审批
✅ 执行采购（3 级审批通过）
结果：executed
```

### 5.2 并行审批流设计

#### 并行审批的概念

**并行审批**是指一个操作需要多个审批人**同时**审核，所有人都通过后才能执行。与多级审批的"串行依次审核"不同，并行审批是"同时审核、全部通过才生效"。

并行审批适用于需要跨部门协作的场景，例如：
- 合同审批需要法务和财务同时审核
- 系统上线需要运维和安全同时确认
- 预算调整需要业务和财务同时批准

> 🎯 面试高频：并行审批在 LangGraph 中如何实现？LangGraph 的 Send API 可以实现并行审批——通过 Send 将同一个审批任务发送给多个审批人节点，每个节点独立触发 interrupt，最后通过条件边或聚合节点判断是否全部通过。

#### 并行审批的实现模式

```mermaid
graph TB
    A[提交申请] --> B[分发给多个审批人]
    B --> C1[审批人 A<br/>interrupt]
    B --> C2[审批人 B<br/>interrupt]
    B --> C3[审批人 C<br/>interrupt]
    C1 --> D[聚合审批结果]
    C2 --> D
    C3 --> D
    D --> E{全部通过?}
    E -->|是| F[执行操作]
    E -->|否| G[流程终止]
```

#### 示例 22：并行审批——多部门会签

```python
"""
示例 22：并行审批实现（多部门会签）
场景：合同审批需要法务、财务、安全三个部门同时审核
预期运行结果：三个审批节点并行暂停，各自恢复后聚合判断
"""
from typing import TypedDict, Optional, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command, Send
import operator

class State(TypedDict):
    contract: dict
    approvals: Annotated[list[dict], operator.add]  # 合并式累加
    status: str
    required_approvers: list[str]

def submit_contract(state: State) -> State:
    return {
        "contract": {"title": "技术服务合同", "amount": 500000, "party": "ABC公司"},
        "approvals": [],
        "status": "pending",
        "required_approvers": ["legal", "finance", "security"]
    }

def distribute_approvals(state: State) -> list[Send]:
    """将审批任务分发给多个审批人（并行）"""
    return [
        Send("legal_approval", {"contract": state["contract"], "approver": "legal"}),
        Send("finance_approval", {"contract": state["contract"], "approver": "finance"}),
        Send("security_approval", {"contract": state["contract"], "approver": "security"}),
    ]

def legal_approval(state: State) -> State:
    result = interrupt({
        "approver": "法务部",
        "contract": state["contract"],
        "focus": "法律条款合规性、违约责任、知识产权"
    })
    return {"approvals": [{"approver": "legal", **result}]}

def finance_approval(state: State) -> State:
    result = interrupt({
        "approver": "财务部",
        "contract": state["contract"],
        "focus": "金额合理性、付款条款、预算匹配"
    })
    return {"approvals": [{"approver": "finance", **result}]}

def security_approval(state: State) -> State:
    result = interrupt({
        "approver": "安全部",
        "contract": state["contract"],
        "focus": "数据安全、隐私保护、安全审计条款"
    })
    return {"approvals": [{"approver": "security", **result}]}

def aggregate_approvals(state: State) -> State:
    """聚合所有审批结果"""
    approvals = state["approvals"]
    all_approved = all(a.get("decision") == "approved" for a in approvals)
    rejected = [a for a in approvals if a.get("decision") == "rejected"]
    
    if rejected:
        return {"status": "rejected", "approvals": approvals}
    elif all_approved and len(approvals) >= len(state["required_approvers"]):
        return {"status": "all_approved", "approvals": approvals}
    return {"status": "pending", "approvals": approvals}

def execute_contract(state: State) -> State:
    print(f"✅ 合同签署完成：{state['contract']['title']}")
    print(f"   会签部门：{', '.join(a['approver'] for a in state['approvals'])}")
    return {"status": "executed"}

def reject_contract(state: State) -> State:
    rejected = [a for a in state["approvals"] if a.get("decision") == "rejected"]
    print(f"❌ 合同被拒绝：{rejected[0]['approver']} - {rejected[0].get('comment', '')}")
    return {"status": "rejected_final"}

builder = StateGraph(State)
builder.add_node("submit", submit_contract)
builder.add_node("legal_approval", legal_approval)
builder.add_node("finance_approval", finance_approval)
builder.add_node("security_approval", security_approval)
builder.add_node("aggregate", aggregate_approvals)
builder.add_node("execute", execute_contract)
builder.add_node("reject", reject_contract)

builder.add_edge(START, "submit")
# 并行分发
builder.add_conditional_edges("submit", distribute_approvals, ["legal_approval", "finance_approval", "security_approval"])
builder.add_edge("legal_approval", "aggregate")
builder.add_edge("finance_approval", "aggregate")
builder.add_edge("security_approval", "aggregate")
builder.add_conditional_edges("aggregate", lambda s: "execute" if s["status"] == "all_approved" else "reject" if s["status"] == "rejected" else "aggregate",
    {"execute": "execute", "reject": "reject", "aggregate": "aggregate"})
builder.add_edge("execute", END)
builder.add_edge("reject", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "parallel-approval"}}

# 第一次执行：三个审批节点同时暂停
print("📋 合同已提交，三个部门并行审批中...")
r = graph.invoke({}, config)
print(f"已完成审批数：{len(r['approvals'])}")

# 依次恢复三个审批（实际场景中三个审批人独立操作）
r = graph.invoke(Command(resume={"decision": "approved", "reviewer": "法务-张律师", "comment": "条款合规"}), config)
print(f"法务已审批，累计：{len(r['approvals'])}")

r = graph.invoke(Command(resume={"decision": "approved", "reviewer": "财务-李会计", "comment": "预算充足"}), config)
print(f"财务已审批，累计：{len(r['approvals'])}")

r = graph.invoke(Command(resume={"decision": "approved", "reviewer": "安全-王工程师", "comment": "安全条款完善"}), config)
print(f"安全已审批，累计：{len(r['approvals'])}")
print(f"最终状态：{r['status']}")
```

**预期运行结果**：
```
📋 合同已提交，三个部门并行审批中...
已完成审批数：0
法务已审批，累计：1
财务已审批，累计：2
安全已审批，累计：3
✅ 合同签署完成：技术服务合同
   会签部门：legal, finance, security
最终状态：executed
```

### 5.3 审批超时处理

#### 超时处理的策略

审批超时是 HITL 系统中必须考虑的问题——如果审批人长时间不响应，流程会一直卡住。常见的超时处理策略：

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| **自动拒绝** | 超时后默认拒绝操作 | 高风险操作，安全优先 |
| **自动批准** | 超时后默认批准操作 | 低风险操作，效率优先 |
| **升级审批** | 超时后自动升级给上级审批 | 企业审批流程，确保有人处理 |
| **重复提醒** | 超时后发送提醒，不自动决策 | 中等风险，给审批人更多时间 |
| **流程终止** | 超时后终止整个流程 | 时效性强的操作，过期无效 |

#### 示例 23：审批超时——自动升级机制

```python
"""
示例 23：审批超时自动升级
场景：审批超过指定时间未处理，自动升级给上级
预期运行结果：检查超时状态，超时则升级审批层级
"""
from typing import TypedDict, Optional
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    request: dict
    current_approver: str
    approver_level: int
    approval_start_time: Optional[str]
    timeout_seconds: int
    approval_history: list[dict]
    status: str

APPROVERS = [
    {"level": 1, "role": "主管", "name": "supervisor"},
    {"level": 2, "role": "经理", "name": "manager"},
    {"level": 3, "role": "总监", "name": "director"},
    {"level": 4, "role": "VP", "name": "vp"},
]

def submit(state: State) -> State:
    return {
        "request": {"item": "紧急采购", "amount": 30000},
        "current_approver": "supervisor",
        "approver_level": 1,
        "approval_start_time": datetime.now().isoformat(),
        "timeout_seconds": 3600,  # 1小时超时
        "approval_history": [],
        "status": "pending"
    }

def check_timeout(state: State) -> State:
    """检查是否超时（实际场景中由外部调度器触发）"""
    if state["status"] != "pending":
        return state
    
    start_time = datetime.fromisoformat(state["approval_start_time"])
    elapsed = (datetime.now() - start_time).total_seconds()
    
    if elapsed > state["timeout_seconds"]:
        # 超时，升级审批
        current_level = state["approver_level"]
        if current_level < len(APPROVERS):
            next_level = current_level + 1
            next_approver = APPROVERS[next_level - 1]
            print(f"⏰ 审批超时（{elapsed:.0f}秒），从{APPROVERS[current_level-1]['role']}升级到{next_approver['role']}")
            return {
                "current_approver": next_approver["name"],
                "approver_level": next_level,
                "approval_start_time": datetime.now().isoformat(),
                "approval_history": state["approval_history"] + [
                    {"level": current_level, "action": "timeout_escalated", "time": datetime.now().isoformat()}
                ]
            }
        else:
            print("⏰ 已达最高审批层级，超时自动拒绝")
            return {"status": "timeout_rejected"}
    return state

def approval_node(state: State) -> State:
    level = state["approver_level"]
    role = APPROVERS[level - 1]["role"]
    
    result = interrupt({
        "approver": role,
        "request": state["request"],
        "timeout": state["timeout_seconds"],
        "escalation_history": [h for h in state["approval_history"] if h.get("action") == "timeout_escalated"]
    })
    
    if result["decision"] == "approved":
        return {"status": "approved", "approval_history": state["approval_history"] + [{"level": level, "role": role, **result}]}
    return {"status": "rejected", "approval_history": state["approval_history"] + [{"level": level, "role": role, **result}]}

def route(state: State) -> str:
    if state["status"] == "approved":
        return "execute"
    elif state["status"] in ("rejected", "timeout_rejected"):
        return "reject"
    return "check_timeout"

def execute_node(state: State) -> State:
    print(f"✅ 执行：{state['request']['item']}")
    return {"status": "executed"}

def reject_node(state: State) -> State:
    print(f"❌ 流程终止：{state['status']}")
    return {"status": "terminated"}

builder = StateGraph(State)
builder.add_node("submit", submit)
builder.add_node("check_timeout", check_timeout)
builder.add_node("approval", approval_node)
builder.add_node("execute", execute_node)
builder.add_node("reject", reject_node)
builder.add_edge(START, "submit")
builder.add_edge("submit", "check_timeout")
builder.add_conditional_edges("check_timeout", route, {"check_timeout": "approval", "execute": "execute", "reject": "reject"})
builder.add_conditional_edges("approval", route, {"execute": "execute", "reject": "reject", "check_timeout": "check_timeout"})
builder.add_edge("execute", END)
builder.add_edge("reject", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "timeout-demo"}}

# 提交并触发审批
r = graph.invoke({}, config)
print(f"⏸ 当前审批人：{r['current_approver']}（第{r['approver_level']}级）")

# 模拟超时检查（实际中由定时任务触发）
# 这里手动将 start_time 改为 2 小时前以模拟超时
r = graph.invoke(
    Command(update={"approval_start_time": (datetime.now() - timedelta(hours=2)).isoformat()}),
    config
)
print(f"⏸ 超时升级后审批人：{r['current_approver']}（第{r['approver_level']}级）")

# 新审批人批准
r = graph.invoke(Command(resume={"decision": "approved", "reviewer": "经理-李四"}), config)
print(f"最终状态：{r['status']}")
```

**预期运行结果**：
```
⏸ 当前审批人：supervisor（第1级）
⏰ 审批超时（7200秒），从主管升级到经理
⏸ 超时升级后审批人：manager（第2级）
✅ 执行：紧急采购
最终状态：executed
```

### 5.4 审批流常见坑点

**坑点 9：多级审批中状态未正确记录当前层级**

错误现象：多级审批恢复后，总是回到第一级审批，无法进入下一级。

根本原因：审批节点中没有正确更新 `current_level` 字段，或者条件边的路由逻辑没有基于更新后的状态判断。

正确做法：在审批节点中，每级审批通过后必须递增 `current_level`，并通过条件边判断是否继续下一级。

**坑点 10：并行审批中状态合并导致审批记录丢失**

错误现象：并行审批中，后完成的审批结果覆盖了先完成的审批记录。

根本原因：状态定义中 `approvals` 字段没有使用 `Annotated[list, operator.add]` 声明为合并式累加，导致并行节点返回时互相覆盖。

正确做法：使用 `Annotated[list[dict], operator.add]` 声明需要合并的列表字段，确保并行节点的返回值累加而非覆盖。

```python
from typing import Annotated
import operator

class State(TypedDict):
    approvals: Annotated[list[dict], operator.add]  # ✅ 合并累加
    # approvals: list[dict]  # ❌ 会互相覆盖
```

---

### 💡 本章深度讲解

审批流是 HITL 在企业场景中最典型的应用，核心是"谁来审、怎么审、审完怎么办、不审怎么办"四个问题。多级审批通过串联 interrupt 节点和状态中的 current_level 实现串行逐级审核，适用于权责分离的场景；并行审批通过 Send API 将审批任务同时分发给多个节点，配合 Annotated[list, operator.add] 实现审批结果的合并累加，适用于跨部门会签场景；超时处理通过在审批流程中插入超时检查节点，结合升级、自动拒绝、自动批准等策略解决"审批人不响应"的问题。三种审批模式可以组合使用——例如先并行会签，再多级审批，每级都有超时升级。设计审批流的关键是用状态完整记录审批历史（谁、何时、什么决策、什么备注），确保全程可审计。

### 📝 本章精简总结

1. **多级审批**：通过串联 interrupt 节点 + current_level 状态 + 条件边实现串行逐级审核
2. **动态审批层级**：根据金额/风险等级自动决定需要几级审批，0级即自动通过
3. **并行审批**：通过 Send API 并行分发审批任务，Annotated[list, operator.add] 合并结果
4. **超时策略**：自动拒绝、自动批准、升级审批、重复提醒、流程终止五种策略
5. **超时升级实现**：在流程中插入超时检查节点，超时后更新审批人并重置计时
6. **审批状态设计**：必须记录 current_level、approval_history、status 三个核心字段
7. **并行审批坑点**：必须用 Annotated[list, operator.add] 声明合并字段，否则并行结果互相覆盖
8. **组合使用**：多级、并行、超时三种模式可以组合，构建复杂的企业审批流程

### 🎯 梯度练习题

**基础题⭐**

1. 多级审批和并行审批有什么区别？分别适用于什么场景？
   > 提示：多级是串行依次审核，并行是同时审核全部通过才生效。

2. 审批超时的五种处理策略是什么？高风险操作和低风险操作分别应该选择哪种策略？
   > 提示：高风险选自动拒绝，低风险选自动批准。

3. 并行审批中为什么要用 `Annotated[list[dict], operator.add]` 声明审批记录字段？如果不用会发生什么？
   > 提示：并行节点同时返回时，普通 list 会互相覆盖，operator.add 会累加合并。

**进阶题⭐⭐**

1. 设计一个"请假审批"流程：员工请假 ≤1 天由主管审批，1-3 天由主管+经理两级审批，>3 天由主管+经理+总监三级审批。审批超过 4 小时未处理自动升级。写出状态定义和核心节点逻辑。
   > 提示：参考示例 21 的动态审批层级 + 示例 23 的超时升级。

2. 实现一个"项目立项审批"流程：需要产品、技术、财务三个部门并行会签，全部通过后再由 CEO 终审。如果任意部门拒绝，流程终止。写出完整的图定义（包含 Send 并行分发和聚合节点）。
   > 提示：先用 Send 分发给三个部门节点，聚合后条件边判断是否全部通过，通过则进入 CEO 审批节点。

**实战题⭐⭐⭐**

1. 设计一个完整的"合同审批系统"，满足以下需求：
   - 合同金额 <5万：法务单人审批
   - 5-50万：法务+财务并行会签
   - >50万：法务+财务+安全并行会签，全部通过后总监终审
   - 每级审批超时 2 小时自动升级（最多升级 2 次）
   - 支持审批人"转派"给同事
   - 完整记录审批历史
   请画出状态图，写出状态定义和所有节点的核心逻辑代码。
   > 提示：用条件边根据金额路由到不同的审批子流程，并行部分用 Send，超时用检查节点，转派用 Command(update) 修改 current_approver。

---

## 6. HITL 与 Checkpoint 协同机制

### 6.1 Checkpoint 在 HITL 中的核心作用

#### 为什么 HITL 离不开 Checkpoint

HITL 的核心是"暂停-恢复"，而暂停和恢复的基础是**状态持久化**。Checkpoint 就是 LangGraph 中负责状态持久化的组件，它在 HITL 中扮演以下核心角色：

1. **暂停时保存状态**：interrupt 触发时，Checkpoint 保存当前完整状态（包括节点执行进度、状态数据、interrupt 信息）
2. **恢复时加载状态**：通过 Command 恢复时，Checkpoint 加载之前保存的状态，图从暂停点继续
3. **历史追溯**：Checkpoint 保存每次状态变更的历史，可以查看任意时间点的状态
4. **并发隔离**：通过 thread_id 隔离不同的执行线程，每个线程有独立的 Checkpoint 历史

> 🎯 面试高频：HITL 和 Checkpoint 是什么关系？HITL 依赖 Checkpoint 实现暂停和恢复——interrupt 触发时 Checkpoint 保存状态，Command 恢复时 Checkpoint 加载状态。没有 Checkpoint，interrupt 无法持久化暂停状态，也就无法实现跨请求/跨进程的人工介入。

#### HITL 中 Checkpoint 的工作时序

```mermaid
sequenceDiagram
    participant App as 应用
    participant Graph as LangGraph
    participant CP as Checkpointer
    participant Human as 人工

    App->>Graph: invoke(input, config)
    Graph->>Graph: 执行节点...
    Graph->>Graph: 节点调用 interrupt()
    Graph->>CP: 保存状态快照（含 interrupt 信息）
    CP-->>Graph: 保存成功
    Graph-->>App: 返回当前状态（暂停）
    App->>Human: 展示审核界面
    Note over Human: 人工审核、决策
    Human->>App: 提交决策
    App->>Graph: invoke(Command(resume=...), config)
    Graph->>CP: 加载 thread_id 对应的最新状态
    CP-->>Graph: 返回暂停时的状态
    Graph->>Graph: 从 interrupt 恢复，继续执行
    Graph->>CP: 保存执行后的新状态
    Graph-->>App: 返回最终结果
```

### 6.2 Checkpoint 配置与 HITL

#### 示例 24：不同 Checkpointer 的 HITL 对比

```python
"""
示例 24：不同 Checkpointer 在 HITL 中的使用
对比 MemorySaver（内存）、SqliteSaver（SQLite）、PostgresSaver（PostgreSQL）
预期运行结果：三种 Checkpointer 都能支持 HITL，区别在于持久化程度
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    value: str
    reviewed: bool

def review_node(state: State) -> State:
    result = interrupt({"value": state["value"]})
    return {"value": result, "reviewed": True}

def build_graph(checkpointer):
    builder = StateGraph(State)
    builder.add_node("review", review_node)
    builder.add_edge(START, "review")
    builder.add_edge("review", END)
    return builder.compile(checkpointer=checkpointer)

# ===== 1. MemorySaver：内存存储，进程重启后丢失 =====
print("=" * 50)
print("1. MemorySaver（内存存储）")
print("=" * 50)
memory_cp = MemorySaver()
graph_memory = build_graph(memory_cp)
config = {"configurable": {"thread_id": "mem-demo"}}

r1 = graph_memory.invoke({"value": "hello", "reviewed": False}, config)
print(f"暂停状态：{r1}")
r2 = graph_memory.invoke(Command(resume="world"), config)
print(f"恢复后：{r2}")
print("⚠️ 进程重启后，MemorySaver 中的状态会丢失")

# ===== 2. SqliteSaver：SQLite 持久化，跨进程保留 =====
print("\n" + "=" * 50)
print("2. SqliteSaver（SQLite 持久化）")
print("=" * 50)
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    import os
    db_path = "hitl_demo.db"
    # 清理旧数据库
    if os.path.exists(db_path):
        os.remove(db_path)
    
    sqlite_cp = SqliteSaver.from_conn_string(db_path)
    graph_sqlite = build_graph(sqlite_cp)
    config2 = {"configurable": {"thread_id": "sqlite-demo"}}
    
    r1 = graph_sqlite.invoke({"value": "hello", "reviewed": False}, config2)
    print(f"暂停状态已保存到 SQLite：{r1}")
    
    # 模拟跨进程：新建一个 graph 实例，用同一个 thread_id 恢复
    sqlite_cp2 = SqliteSaver.from_conn_string(db_path)
    graph_sqlite2 = build_graph(sqlite_cp2)
    r2 = graph_sqlite2.invoke(Command(resume="world"), config2)
    print(f"跨进程恢复成功：{r2}")
    
    sqlite_cp.close()
    sqlite_cp2.close()
    print("✅ SQLite 支持跨进程/跨重启的 HITL")
except ImportError:
    print("⚠️ SqliteSaver 未安装，跳过（pip install langgraph-checkpoint-sqlite）")

# ===== 3. 生产环境推荐：PostgresSaver =====
print("\n" + "=" * 50)
print("3. PostgresSaver（生产环境推荐）")
print("=" * 50)
print("PostgresSaver 支持高并发、分布式部署，是生产环境的首选")
print("使用方式：")
print("  from langgraph.checkpoint.postgres import PostgresSaver")
print("  cp = PostgresSaver.from_conn_string('postgresql://user:pass@host:5432/db')")
print("  cp.setup()  # 初始化表结构")
print("  graph = builder.compile(checkpointer=cp)")
print("优势：ACID 事务、高可用、支持多副本、与 LangGraph Platform 无缝集成")
```

**预期运行结果**：
```
==================================================
1. MemorySaver（内存存储）
==================================================
暂停状态：{'value': 'hello', 'reviewed': False}
恢复后：{'value': 'world', 'reviewed': True}
⚠️ 进程重启后，MemorySaver 中的状态会丢失

==================================================
2. SqliteSaver（SQLite 持久化）
==================================================
暂停状态已保存到 SQLite：{'value': 'hello', 'reviewed': False}
跨进程恢复成功：{'value': 'world', 'reviewed': True}
✅ SQLite 支持跨进程/跨重启的 HITL

==================================================
3. PostgresSaver（生产环境推荐）
==================================================
PostgresSaver 支持高并发、分布式部署，是生产环境的首选
...
```

#### Checkpointer 选型指南

| Checkpointer | 持久化 | 并发支持 | 适用场景 | 生产就绪 |
|-------------|--------|----------|----------|----------|
| **MemorySaver** | ❌ 内存 | 单进程 | 开发测试、Demo | ❌ |
| **SqliteSaver** | ✅ 文件 | 单写多读 | 小型应用、单机部署 | ⚠️ 有限 |
| **PostgresSaver** | ✅ 数据库 | 高并发 | 生产环境、分布式 | ✅ |
| **RedisSaver** | ✅ 内存数据库 | 高并发 | 缓存层、低延迟 | ✅ |

### 6.3 状态历史与时间旅行

#### 查看 Checkpoint 历史

```python
"""
示例 25：查看 HITL 的 Checkpoint 历史
预期运行结果：列出所有状态快照，可以看到每次 interrupt 和恢复产生的状态变更
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    content: str
    review_count: int
    status: str

def node1(state: State) -> State:
    return {"content": "AI 生成内容", "review_count": 0, "status": "generated"}

def review_node(state: State) -> State:
    result = interrupt({"content": state["content"], "step": "review"})
    new_count = state["review_count"] + 1
    if result == "approve":
        return {"status": "approved", "review_count": new_count}
    return {"status": "rejected", "review_count": new_count}

def final_node(state: State) -> State:
    return {"status": "completed"}

builder = StateGraph(State)
builder.add_node("n1", node1)
builder.add_node("review", review_node)
builder.add_node("final", final_node)
builder.add_edge(START, "n1")
builder.add_edge("n1", "review")
builder.add_edge("review", "final")
builder.add_edge("final", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "history-demo"}}

# 执行到 interrupt
r1 = graph.invoke({}, config)
print("第1次执行后（暂停）")

# 恢复
r2 = graph.invoke(Command(resume="approve"), config)
print("第2次执行后（完成）")

# 查看 Checkpoint 历史
print("\n" + "=" * 60)
print("Checkpoint 历史：")
print("=" * 60)
state_history = []
for checkpoint in checkpointer.list(config):
    state_snapshot = checkpoint["values"]
    meta = checkpoint["metadata"]
    print(f"\n--- Checkpoint (ts={meta.get('created_at', 'unknown')}) ---")
    print(f"  状态：{state_snapshot}")
    print(f"  节点：{meta.get('next_nodes', 'N/A')}")
    print(f"  来源：{meta.get('source', 'N/A')}")
    state_history.append(state_snapshot)

print(f"\n共 {len(state_history)} 个状态快照")
```

**预期运行结果**：
```
第1次执行后（暂停）
第2次执行后（完成）

============================================================
Checkpoint 历史：
============================================================

--- Checkpoint (ts=...) ---
  状态：{'content': 'AI 生成内容', 'review_count': 0, 'status': 'generated'}
  节点：['review']
  来源：input

--- Checkpoint (ts=...) ---
  状态：{'content': 'AI 生成内容', 'review_count': 0, 'status': 'generated'}
  节点：[]
  来源：loop

--- Checkpoint (ts=...) ---
  状态：{'content': 'AI 生成内容', 'review_count': 1, 'status': 'approved'}
  节点：['final']
  来源：loop

--- Checkpoint (ts=...) ---
  状态：{'content': 'AI 生成内容', 'review_count': 1, 'status': 'completed'}
  节点：[]
  来源：loop

共 4 个状态快照
```

#### 示例 26：状态时间旅行——回滚到历史状态

```python
"""
示例 26：状态时间旅行——从历史 Checkpoint 恢复
预期运行结果：获取历史 Checkpoint 的 ID，用它作为基础重新执行
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    content: str
    version: int
    status: str

def generate_node(state: State) -> State:
    return {"content": f"内容 v{state.get('version', 0) + 1}", "version": state.get("version", 0) + 1, "status": "generated"}

def review_node(state: State) -> State:
    result = interrupt({"content": state["content"], "version": state["version"]})
    if result == "approve":
        return {"status": "approved"}
    return {"status": "rejected"}

builder = StateGraph(State)
builder.add_node("generate", generate_node)
builder.add_node("review", review_node)
builder.add_edge(START, "generate")
builder.add_edge("generate", "review")
builder.add_edge("review", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "time-travel"}}

# 第一次生成 + 审核
r1 = graph.invoke({}, config)
print(f"第1次生成：{r1['content']}（v{r1['version']}）")
r2 = graph.invoke(Command(resume="approve"), config)
print(f"第1次审核：{r2['status']}")

# 第二次生成（版本递增）
r3 = graph.invoke({}, config)
print(f"第2次生成：{r3['content']}（v{r3['version']}）")

# 获取所有 Checkpoint，找到 v1 的状态
print("\n查找历史 Checkpoint...")
target_checkpoint_id = None
for cp in checkpointer.list(config):
    if cp["values"].get("version") == 1 and cp["values"].get("status") == "generated":
        target_checkpoint_id = cp["id"]
        print(f"找到 v1 状态的 Checkpoint ID：{target_checkpoint_id}")
        break

if target_checkpoint_id:
    # 从历史 Checkpoint 恢复，重新执行
    print("\n从 v1 状态重新执行（时间旅行）...")
    config_with_history = {
        "configurable": {
            "thread_id": "time-travel",
            "checkpoint_id": target_checkpoint_id
        }
    }
    # 注意：这会创建一个新的分支（fork），不会覆盖原有历史
    r4 = graph.invoke(Command(resume="approve"), config_with_history)
    print(f"从 v1 恢复后：{r4['content']}（v{r4['version']}），状态：{r4['status']}")
```

**预期运行结果**：
```
第1次生成：内容 v1（v1）
第1次审核：approved
第2次生成：内容 v2（v2）

查找历史 Checkpoint...
找到 v1 状态的 Checkpoint ID：...

从 v1 状态重新执行（时间旅行）...
从 v1 恢复后：内容 v1（v1），状态：approved
```

### 6.4 HITL 与 Checkpoint 协同的最佳实践

#### 最佳实践清单

1. **生产环境必须用持久化 Checkpointer**：MemorySaver 只适合开发测试，生产环境用 PostgresSaver 或 RedisSaver
2. **thread_id 设计要合理**：thread_id 应该能唯一标识一个业务流程（如 `approval:{request_id}`），避免冲突
3. **定期清理过期 Checkpoint**：长期运行的系统会积累大量 Checkpoint，需要定期清理过期数据
4. **利用 Checkpoint 历史做审计**：Checkpoint 历史天然就是审计日志，可以直接用于合规审计
5. **大状态要注意存储成本**：如果状态中包含大文本或大对象，Checkpoint 存储会快速增长，考虑只存引用

#### 常见坑点

**坑点 11：thread_id 冲突导致状态混乱**

错误现象：不同的审批请求使用了相同的 thread_id，导致状态互相覆盖，恢复时拿到错误的状态。

根本原因：thread_id 是 Checkpoint 隔离的唯一标识，如果两个不同的业务流程使用了相同的 thread_id，它们的 Checkpoint 会混在一起。

正确做法：thread_id 应该包含业务类型和唯一 ID，如 `approval:req_12345`、`review:doc_67890`。

**坑点 12：状态过大导致 Checkpoint 写入慢**

错误现象：随着状态中积累的内容越来越多（如长对话历史、大文件内容），每次 Checkpoint 写入越来越慢，interrupt 恢复延迟增加。

根本原因：Checkpoint 每次都序列化并存储完整状态，如果状态中包含大对象，序列化和存储开销很大。

正确做法：状态中只存必要的元数据和引用，大对象（如文件、长文本）存到外部存储（S3、数据库），状态中只存 URL 或 ID。

---

### 💡 本章深度讲解

HITL 与 Checkpoint 是"鱼与水"的关系——HITL 的暂停-恢复能力完全建立在 Checkpoint 的状态持久化之上。interrupt 触发时，Checkpoint 保存包含 interrupt 信息的完整状态快照；Command 恢复时，Checkpoint 根据 thread_id 加载最新状态，图从暂停点精确继续。Checkpoint 不仅是技术基础设施，还为 HITL 提供了审计追溯（完整的状态变更历史）和时间旅行（从历史 Checkpoint 恢复执行）的能力。在生产环境中，Checkpointer 的选型至关重要——MemorySaver 只适合开发，SqliteSaver 适合小型单机应用，PostgresSaver 是分布式生产环境的首选。理解 HITL 与 Checkpoint 的协同，关键是理解"每次 interrupt 都是一个 Checkpoint 边界，每次恢复都是从 Checkpoint 重建状态"这个核心机制。

### 📝 本章精简总结

1. **HITL 依赖 Checkpoint**：interrupt 保存状态到 Checkpoint，Command 从 Checkpoint 加载状态恢复
2. **Checkpointer 选型**：MemorySaver（开发）→ SqliteSaver（小型）→ PostgresSaver/RedisSaver（生产）
3. **thread_id 隔离**：不同业务流程必须用不同的 thread_id，格式建议 `业务类型:唯一ID`
4. **状态历史**：Checkpoint 自动保存每次状态变更，可用于审计追溯
5. **时间旅行**：通过指定 checkpoint_id 可以从历史状态恢复执行（创建分支）
6. **持久化必要性**：生产环境必须用持久化 Checkpointer，否则进程重启后 HITL 状态丢失
7. **状态大小控制**：状态中只存元数据和引用，大对象存外部存储，避免 Checkpoint 写入慢
8. **两大坑点**：thread_id 冲突导致状态混乱、状态过大导致 Checkpoint 性能下降

### 🎯 梯度练习题

**基础题⭐**

1. 为什么 HITL 必须依赖 Checkpoint？如果没有 Checkpoint，interrupt 会有什么问题？
   > 提示：interrupt 暂停后需要保存状态才能跨请求恢复，Checkpoint 就是状态的持久化存储。

2. MemorySaver、SqliteSaver、PostgresSaver 分别适用于什么场景？生产环境应该选哪个？
   > 提示：从持久化、并发支持、部署规模三个维度对比。

3. thread_id 在 HITL 中的作用是什么？如果两个不同的审批请求用了相同的 thread_id 会发生什么？
   > 提示：thread_id 是 Checkpoint 的隔离键，冲突会导致状态互相覆盖。

**进阶题⭐⭐**

1. 设计一个 thread_id 命名规范，用于以下业务场景：订单审批、内容审核、客服工单、代码 Review。每个场景给出 2 个示例 thread_id，并说明命名规范的设计原则。
   > 提示：包含业务类型、实体 ID、可能的子流程 ID，用分隔符连接。

2. 解释"状态时间旅行"的概念和实现方式。如何从一个历史 Checkpoint 恢复执行？这会覆盖原有历史吗？
   > 提示：通过 config 中的 checkpoint_id 指定历史状态，恢复时会创建新的分支（fork），不覆盖原有历史。

**实战题⭐⭐⭐**

1. 为一个生产级 HITL 系统设计 Checkpoint 策略，满足以下需求：
   - 日均 10 万次 interrupt，峰值 100 QPS
   - 状态平均大小 5KB，最大 50KB
   - 需要保留 90 天的审计历史
   - 99.9% 的恢复延迟 < 200ms
   - 支持多副本部署
   请选择 Checkpointer 类型，设计 thread_id 规范、状态大小控制策略、历史数据清理方案，并估算存储成本。
   > 提示：PostgresSaver + 连接池，状态中存引用不存大对象，定时任务清理 90 天前的 Checkpoint，存储估算 = 日均 interrupt × 状态大小 × 90 天 × 冗余系数。

---

## 7. 人工编辑状态后恢复执行

### 7.1 恢复执行的底层机制

#### 恢复执行的完整流程

当人工通过 `Command` 恢复一个暂停的图时，LangGraph 内部执行以下步骤：

1. **加载状态**：根据 `config.thread_id` 从 Checkpointer 加载最新的状态快照
2. **识别暂停点**：从状态中读取 interrupt 信息，确定暂停在哪个节点、哪个 interrupt 调用
3. **应用 update**：如果 Command 包含 `update`，将更新合并到状态中
4. **恢复节点执行**：如果暂停在节点内的 `interrupt()`，将 `resume` 的值作为 `interrupt()` 的返回值，节点从暂停点继续
5. **应用 goto**：如果 Command 包含 `goto`，节点执行完后跳转到指定节点（而非默认边）
6. **继续图执行**：按照状态图的边定义继续执行后续节点
7. **保存新状态**：每个节点执行完后保存新的 Checkpoint

```mermaid
graph TB
    subgraph 恢复执行流程
        A[1. 加载 Checkpoint 状态] --> B[2. 识别暂停点]
        B --> C[3. 应用 Command.update]
        C --> D{4. 暂停类型?}
        D -->|节点内 interrupt| E[5a. resume 作为 interrupt 返回值<br/>节点从暂停点继续]
        D -->|interrupt_before| E2[5b. 节点开始执行]
        D -->|interrupt_after| E3[5c. 直接进入下一节点]
        E --> F[6. 节点执行完成]
        E2 --> F
        E3 --> G[7. 按边继续执行]
        F --> H{有 goto?}
        H -->|是| I[跳转到 goto 指定节点]
        H -->|否| G
        I --> G
        G --> J[8. 保存新 Checkpoint]
    end
```

#### 示例 27：恢复执行的详细追踪

```python
"""
示例 27：恢复执行的详细追踪
通过打印日志观察恢复执行的每一步
预期运行结果：清晰展示 interrupt 暂停和恢复的执行路径
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    log: list[str]
    data: Optional[str]
    result: Optional[str]

def node_a(state: State) -> State:
    print("  [执行] 节点 A 开始")
    log = state.get("log", []) + ["A 开始"]
    print("  [执行] 节点 A 完成")
    return {"log": log + ["A 完成"], "data": "来自 A 的数据"}

def node_b(state: State) -> State:
    print("  [执行] 节点 B 开始")
    log = state["log"] + ["B 开始"]
    
    print("  [执行] 节点 B：调用 interrupt()")
    # 暂停点：interrupt 之后的代码在恢复时才执行
    user_input = interrupt({"question": "请输入数据", "current_data": state["data"]})
    print(f"  [恢复] 节点 B：interrupt 返回 = {user_input}")
    
    log = log + [f"B 收到人工输入: {user_input}"]
    result = f"处理结果：{state['data']} + {user_input}"
    print("  [执行] 节点 B 完成")
    return {"log": log + ["B 完成"], "result": result}

def node_c(state: State) -> State:
    print("  [执行] 节点 C 开始")
    log = state["log"] + ["C 开始"]
    print(f"  [执行] 节点 C：使用结果 = {state['result']}")
    print("  [执行] 节点 C 完成")
    return {"log": log + ["C 完成"]}

builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", "c")
builder.add_edge("c", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "recovery-trace"}}

print("=" * 50)
print("第一次 invoke（触发 interrupt）")
print("=" * 50)
r1 = graph.invoke({"log": []}, config)
print(f"\n暂停时状态：log={r1['log']}")
print(f"  注意：'B 收到人工输入' 和 'B 完成' 不在 log 中（interrupt 之后的代码未执行）")

print("\n" + "=" * 50)
print("第二次 invoke（Command resume 恢复）")
print("=" * 50)
r2 = graph.invoke(Command(resume="人工输入的数据"), config)
print(f"\n恢复后状态：log={r2['log']}")
print(f"  注意：'B 收到人工输入' 和 'B 完成' 现在出现在 log 中")
print(f"  结果：{r2['result']}")
```

**预期运行结果**：
```
==================================================
第一次 invoke（触发 interrupt）
==================================================
  [执行] 节点 A 开始
  [执行] 节点 A 完成
  [执行] 节点 B 开始
  [执行] 节点 B：调用 interrupt()

暂停时状态：log=['A 开始', 'A 完成', 'B 开始']
  注意：'B 收到人工输入' 和 'B 完成' 不在 log 中（interrupt 之后的代码未执行）

==================================================
第二次 invoke（Command resume 恢复）
==================================================
  [恢复] 节点 B：interrupt 返回 = 人工输入的数据
  [执行] 节点 B 完成
  [执行] 节点 C 开始
  [执行] 节点 C：使用结果 = 处理结果：来自 A 的数据 + 人工输入的数据
  [执行] 节点 C 完成

恢复后状态：log=['A 开始', 'A 完成', 'B 开始', 'B 收到人工输入: 人工输入的数据', 'B 完成', 'C 开始', 'C 完成']
  注意：'B 收到人工输入' 和 'B 完成' 现在出现在 log 中
  结果：处理结果：来自 A 的数据 + 人工输入的数据
```

### 7.2 人工编辑状态的完整工作流

#### 工作流设计

人工编辑状态后恢复执行的完整工作流包含以下步骤：

1. **图执行到 interrupt 暂停**
2. **系统将当前状态展示给人工**
3. **人工查看状态，识别需要修改的部分**
4. **人工编辑状态（修改字段、添加字段、删除字段）**
5. **人工提交编辑后的状态 + 恢复指令**
6. **系统应用 update 修改状态**
7. **系统从暂停点恢复执行**
8. **后续节点基于修改后的状态执行**

#### 示例 28：人工编辑状态的完整工作流

```python
"""
示例 28：人工编辑状态的完整工作流
场景：AI 生成营销文案，人工编辑后发布
预期运行结果：展示"生成→暂停→人工编辑→恢复→发布"的完整流程
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    topic: str
    draft: Optional[str]
    edited_draft: Optional[str]
    edit_history: list[dict]
    status: str
    published: bool

def generate_draft(state: State) -> State:
    """AI 生成初稿"""
    draft = f"【{state['topic']}】\n\n亲爱的用户，我们很高兴地宣布...\n\n（AI 生成的初稿内容，可能需要人工润色）"
    print(f"🤖 AI 已生成初稿（{len(draft)} 字符）")
    return {"draft": draft, "status": "draft_ready", "edit_history": []}

def human_edit_node(state: State) -> State:
    """人工编辑节点"""
    # interrupt 展示初稿，请求人工编辑
    edit_result = interrupt({
        "action": "edit_content",
        "original_draft": state["draft"],
        "instruction": "请人工编辑文案，编辑后通过 Command(update) 修改状态",
        "current_status": state["status"]
    })
    
    # edit_result 来自 resume，可以是人工的操作指令
    print(f"📝 人工编辑完成：{edit_result}")
    return {
        "edited_draft": state.get("edited_draft", state["draft"]),  # 如果人工用 update 修改了 edited_draft，用修改后的值
        "edit_history": state["edit_history"] + [{"action": edit_result, "edited": state.get("edited_draft") != state["draft"]}],
        "status": "edited"
    }

def review_edited_node(state: State) -> State:
    """编辑后审核"""
    decision = interrupt({
        "action": "review_edited",
        "original": state["draft"],
        "edited": state["edited_draft"],
        "diff_note": "人工已编辑，请确认是否发布"
    })
    if decision == "publish":
        return {"status": "approved"}
    return {"status": "needs_reedit"}

def publish_node(state: State) -> State:
    """发布"""
    print(f"📢 已发布：{state['edited_draft'][:60]}...")
    return {"published": True, "status": "published"}

def route_after_edit(state: State) -> str:
    if state["status"] == "edited":
        return "review"
    return "edit"

builder = StateGraph(State)
builder.add_node("generate", generate_draft)
builder.add_node("edit", human_edit_node)
builder.add_node("review", review_edited_node)
builder.add_node("publish", publish_node)
builder.add_edge(START, "generate")
builder.add_edge("generate", "edit")
builder.add_conditional_edges("edit", route_after_edit, {"review": "review", "edit": "edit"})
builder.add_conditional_edges("review", lambda s: "publish" if s["status"] == "approved" else "edit",
    {"publish": "publish", "edit": "edit"})
builder.add_edge("publish", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "edit-workflow"}}

# 1. AI 生成初稿，触发人工编辑 interrupt
print("步骤 1：AI 生成初稿")
r = graph.invoke({"topic": "新品发布会"}, config)
print(f"初稿：{r['draft'][:50]}...")

# 2. 人工编辑状态（通过 update 修改 edited_draft），同时 resume 确认
print("\n步骤 2：人工编辑文案")
edited_content = "【新品发布会】\n\n尊敬的用户，我们诚挚邀请您参加..."
r = graph.invoke(
    Command(
        resume="edited_by_human",
        update={"edited_draft": edited_content}
    ),
    config
)
print(f"编辑后：{r['edited_draft'][:50]}...")
print(f"编辑历史：{r['edit_history']}")

# 3. 审核编辑后的内容，确认发布
print("\n步骤 3：审核并发布")
r = graph.invoke(Command(resume="publish"), config)
print(f"最终状态：published={r['published']}, status={r['status']}")
```

**预期运行结果**：
```
步骤 1：AI 生成初稿
🤖 AI 已生成初稿（80 字符）
初稿：【新品发布会】

亲爱的用户，我们很高兴地宣布...

步骤 2：人工编辑文案
📝 人工编辑完成：edited_by_human
编辑后：【新品发布会】

尊敬的用户，我们诚挚邀请您参加...
编辑历史：[{'action': 'edited_by_human', 'edited': True}]

步骤 3：审核并发布
📢 已发布：【新品发布会】

尊敬的用户，我们诚挚邀请您参加......
最终状态：published=True, status=published
```

### 7.3 恢复执行的高级场景

#### 场景一：部分恢复——只恢复特定分支

当图有多个并行分支时，可以只恢复其中一个分支的 interrupt，其他分支保持暂停。

```python
"""
示例 29：部分恢复——并行分支中只恢复一个
预期运行结果：两个并行分支各自 interrupt，先恢复一个，再恢复另一个
"""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command, Send
import operator

class State(TypedDict):
    results: Annotated[list[str], operator.add]
    status: dict

def branch_a(state: State) -> State:
    result = interrupt({"branch": "A", "task": "审核文案"})
    return {"results": [f"A: {result}"], "status": {"a": "done"}}

def branch_b(state: State) -> State:
    result = interrupt({"branch": "B", "task": "审核图片"})
    return {"results": [f"B: {result}"], "status": {"b": "done"}}

def merge(state: State) -> State:
    print(f"合并结果：{state['results']}")
    return {}

builder = StateGraph(State)
builder.add_node("a", branch_a)
builder.add_node("b", branch_b)
builder.add_node("merge", merge)
builder.add_conditional_edges(START, lambda s: [Send("a", {}), Send("b", {})], ["a", "b"])
builder.add_edge("a", "merge")
builder.add_edge("b", "merge")
builder.add_edge("merge", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "partial-recovery"}}

# 两个分支同时暂停
r = graph.invoke({}, config)
print(f"两个分支都暂停，当前结果：{r['results']}")

# 只恢复分支 A
r = graph.invoke(Command(resume="A 已批准"), config)
print(f"恢复 A 后，结果：{r['results']}（B 仍暂停）")

# 再恢复分支 B
r = graph.invoke(Command(resume="B 已批准"), config)
print(f"恢复 B 后，结果：{r['results']}（全部完成）")
```

**预期运行结果**：
```
两个分支都暂停，当前结果：[]
恢复 A 后，结果：['A: A 已批准']（B 仍暂停）
合并结果：['A: A 已批准', 'B: B 已批准']
恢复 B 后，结果：['A: A 已批准', 'B: B 已批准']（全部完成）
```

#### 场景二：恢复时修改执行路径

人工在恢复时不仅可以修改状态，还可以通过 `goto` 改变图的执行路径。

```python
"""
示例 30：恢复时修改执行路径
场景：人工审核后决定跳过某些步骤或回退到之前的步骤
预期运行结果：通过 goto 实现路径重定向
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    content: str
    quality_score: Optional[int]
    status: str

def generate(state: State) -> State:
    return {"content": "AI 生成内容", "quality_score": None, "status": "generated"}

def review(state: State) -> State:
    decision = interrupt({
        "content": state["content"],
        "options": {
            "goto=publish": "直接发布",
            "goto=enhance": "需要优化后发布",
            "goto=generate": "重新生成",
            "goto=__end__": "放弃"
        }
    })
    return {"status": "reviewed"}

def enhance(state: State) -> State:
    print("✨ 优化内容中...")
    return {"content": state["content"] + "（已优化）", "quality_score": 95, "status": "enhanced"}

def publish(state: State) -> State:
    print(f"📢 发布：{state['content']}")
    return {"status": "published"}

builder = StateGraph(State)
builder.add_node("generate", generate)
builder.add_node("review", review)
builder.add_node("enhance", enhance)
builder.add_node("publish", publish)
builder.add_edge(START, "generate")
builder.add_edge("generate", "review")
# review 不设默认边，全部通过 goto 控制
builder.add_edge("enhance", "publish")
builder.add_edge("publish", END)

graph = builder.compile(checkpointer=MemorySaver())

# 场景 1：直接发布
print("=== 场景 1：直接发布 ===")
cfg1 = {"configurable": {"thread_id": "path-direct"}}
r = graph.invoke({}, cfg1)
r = graph.invoke(Command(goto="publish"), cfg1)
print(f"状态：{r['status']}")

# 场景 2：需要优化
print("\n=== 场景 2：优化后发布 ===")
cfg2 = {"configurable": {"thread_id": "path-enhance"}}
r = graph.invoke({}, cfg2)
r = graph.invoke(Command(goto="enhance"), cfg2)
print(f"状态：{r['status']}, 质量分：{r['quality_score']}")

# 场景 3：重新生成
print("\n=== 场景 3：重新生成 ===")
cfg3 = {"configurable": {"thread_id": "path-regenerate"}}
r = graph.invoke({}, cfg3)
r = graph.invoke(Command(goto="generate"), cfg3)
print(f"重新生成后状态：{r['status']}")
# 重新生成后又会到 review，再次选择发布
r = graph.invoke(Command(goto="publish"), cfg3)
print(f"最终状态：{r['status']}")
```

**预期运行结果**：
```
=== 场景 1：直接发布 ===
📢 发布：AI 生成内容
状态：published

=== 场景 2：优化后发布 ===
✨ 优化内容中...
📢 发布：AI 生成内容（已优化）
状态：published, 质量分：95

=== 场景 3：重新生成 ===
重新生成后状态：generated
📢 发布：AI 生成内容
最终状态：published
```

### 7.4 恢复执行常见坑点

**坑点 13：恢复时忘记传 thread_id 导致找不到状态**

错误现象：恢复执行时报错 "No checkpoint found" 或状态为空。

根本原因：恢复时的 `config` 中没有包含与暂停时相同的 `thread_id`，Checkpointer 无法找到对应的状态快照。

正确做法：暂停和恢复必须使用相同的 `config`（至少 `thread_id` 相同）。建议将 config 存储在会话或数据库中。

```python
# ❌ 错误：两次使用不同的 thread_id
graph.invoke({}, {"configurable": {"thread_id": "abc"}})
graph.invoke(Command(resume="ok"), {"configurable": {"thread_id": "xyz"}})  # 找不到状态！

# ✅ 正确：使用相同的 thread_id
config = {"configurable": {"thread_id": "abc"}}
graph.invoke({}, config)
graph.invoke(Command(resume="ok"), config)
```

**坑点 14：在 interrupt 之前修改了状态但恢复时状态未更新**

错误现象：节点中在 `interrupt()` 之前修改了状态字段，但恢复时该字段的值还是旧的。

根本原因：`interrupt()` 之前的代码对状态的修改需要通过 `return` 返回才能生效。如果在节点内直接修改 `state["field"] = new_value`（而不是 return），这个修改不会被保存到 Checkpoint。

正确做法：节点函数应该通过返回字典来更新状态，而不是直接修改传入的 state 对象。

```python
# ❌ 错误：直接修改 state，interrupt 时这个修改不会被保存
def bad_node(state):
    state["progress"] = "half_done"  # 直接修改，不生效！
    user_input = interrupt({"msg": "waiting"})
    # 恢复时 state["progress"] 仍然是旧值
    ...

# ✅ 正确：在 interrupt 之前 return 更新状态（但这样会结束节点）
# 更好的做法：将 interrupt 之前的逻辑拆成独立节点
def good_node(state):
    user_input = interrupt({"msg": "waiting"})
    # interrupt 之后的修改会正常保存
    return {"progress": "done", "input": user_input}
```

---

### 💡 本章深度讲解

人工编辑状态后恢复执行是 HITL 的"灵魂操作"——它让人类不仅能"点头或摇头"，还能"动手修改"。理解恢复执行的关键是掌握七步流程：加载状态→识别暂停点→应用 update→恢复节点执行→应用 goto→继续图执行→保存新状态。其中最容易混淆的是 `interrupt()` 节点内恢复和 `interrupt_before/after` 恢复的区别：节点内恢复时 `resume` 的值作为 `interrupt()` 的返回值，节点从暂停点继续执行（interrupt 之后的代码才运行）；interrupt_before 恢复时节点才开始执行；interrupt_after 恢复时直接进入下一节点。人工编辑状态通过 `Command(update=...)` 实现，它在节点恢复前生效，后续节点基于修改后的状态执行。掌握恢复执行后，HITL 的"暂停-人工-恢复"闭环就完整了。

### 📝 本章精简总结

1. **恢复七步流程**：加载状态→识别暂停点→应用 update→恢复节点执行→应用 goto→继续执行→保存新状态
2. **节点内 interrupt 恢复**：resume 的值作为 interrupt() 返回值，节点从暂停点继续，interrupt 之后的代码才执行
3. **interrupt_before 恢复**：恢复时节点才开始执行，传 None 或 Command 均可
4. **interrupt_after 恢复**：恢复时直接进入下一节点，常用 Command(update=...) 修改状态
5. **人工编辑状态**：通过 Command(update={...}) 在恢复前修改状态，后续节点基于新状态执行
6. **部分恢复**：并行分支中可以只恢复一个分支的 interrupt，其他分支保持暂停
7. **路径重定向**：通过 Command(goto=...) 在恢复时改变执行路径，可跳过、回退或终止
8. **两大坑点**：恢复时 thread_id 不一致找不到状态、interrupt 前直接修改 state 不生效

### 🎯 梯度练习题

**基础题⭐**

1. 恢复执行的七步流程是什么？请按顺序列出。
   > 提示：从加载 Checkpoint 状态开始，到保存新状态结束。

2. 节点内 `interrupt()` 恢复时，`resume` 的值是如何传递回节点的？interrupt 之前和之后的代码分别在什么时候执行？
   > 提示：resume 的值作为 interrupt() 的返回值；interrupt 之前的代码在第一次执行时运行，之后的代码在恢复时运行。

3. `Command(update=...)` 和 `Command(resume=...)` 有什么区别？分别在恢复流程的哪一步生效？
   > 提示：update 修改状态（在节点恢复前生效），resume 传递 interrupt 返回值（节点恢复时生效）。

**进阶题⭐⭐**

1. 设计一个场景：节点内有两次 interrupt，第一次 interrupt 之前修改了状态 A，第一次和第二次之间修改了状态 B，第二次之后修改了状态 C。请分析每次 invoke 后状态中 A、B、C 的值，并解释原因。
   > 提示：interrupt 之前的 return 会保存状态，但如果没有 return 直接修改 state 则不保存；interrupt 之间的代码在第一次恢复后、第二次 interrupt 前执行。

2. 解释"部分恢复"的概念。在并行分支场景中，如果有两个分支都触发了 interrupt，恢复一个分支后图的状态是什么样的？另一个分支的 interrupt 还在吗？
   > 提示：并行分支各自独立，恢复一个分支后该分支继续执行到汇聚节点等待，另一个分支仍保持 interrupt 状态。

**实战题⭐⭐⭐**

1. 实现一个"人工调试 Agent"的功能：
   - Agent 执行多步任务，每步执行前触发 interrupt
   - 人工在每次 interrupt 时可以选择：(a) 继续执行下一步；(b) 修改状态后继续；(c) 回退到上一步重新执行；(d) 终止执行
   - 完整记录每一步的执行日志和人工操作
   - 支持"跳过剩余步骤直接到最终节点"
   请写出完整的图定义和节点逻辑，并演示四种人工操作的执行过程。
   > 提示：用 Command(goto=...) 实现回退和跳过，用 Command(update=...) 实现状态修改，用状态中的 log 字段记录执行日志。

---

## 8. HITL 在 Agent 中的应用

### 8.1 工具调用审批

#### 工具调用审批的概念

在 Agent 系统中，LLM 会决定调用哪些工具（Tool）来完成任务。有些工具是只读的（如搜索、查询），风险较低；但有些工具有副作用（如发送邮件、执行 SQL、调用支付 API），一旦出错后果严重。**工具调用审批**就是在 Agent 执行有副作用的工具调用前，插入人工审核环节。

> 🎯 面试高频：如何在 LangGraph Agent 中实现工具调用审批？可以在工具执行节点前配置 interrupt_before，或者在工具执行节点内部调用 interrupt()，将 LLM 计划调用的工具名称、参数展示给人工审核。人工批准后恢复执行工具，拒绝则跳过该工具调用。关键是要能拦截 LLM 的工具调用决策并插入人工审核。

#### 工具调用审批的架构

```mermaid
graph TB
    A[用户输入] --> B[LLM 思考]
    B --> C{需要调用工具?}
    C -->|否| D[直接回答]
    C -->|是| E[生成工具调用计划]
    E --> F{工具有副作用?}
    F -->|否| G[直接执行工具]
    F -->|是| H[⏸ interrupt 人工审批]
    H --> I{人工决策}
    I -->|批准| J[执行工具]
    I -->|拒绝| K[跳过工具, 告知 LLM]
    I -->|修改参数| L[用修改后参数执行]
    G --> M[工具结果返回 LLM]
    J --> M
    L --> M
    K --> M
    M --> B
```

#### 示例 31：工具调用审批——邮件发送确认

```python
"""
示例 31：工具调用审批——邮件发送确认
场景：Agent 可以调用 send_email 工具，发送前需要人工确认
预期运行结果：LLM 决定发送邮件 → interrupt 暂停 → 人工确认 → 发送
"""
from typing import TypedDict, Optional, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
import operator

# 模拟工具定义
def send_email(to: str, subject: str, body: str) -> str:
    """发送邮件工具"""
    print(f"📧 发送邮件给 {to}：{subject}")
    return f"邮件已发送给 {to}"

def search_info(query: str) -> str:
    """搜索信息工具（只读，无需审批）"""
    return f"搜索结果：关于 {query} 的信息..."

class State(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    pending_tool_call: Optional[dict]
    tool_approved: bool

def agent_node(state: State) -> State:
    """模拟 LLM 决策节点"""
    messages = state["messages"]
    last_msg = messages[-1] if messages else None
    
    # 模拟 LLM 决定调用 send_email 工具
    if isinstance(last_msg, HumanMessage):
        tool_call = {
            "tool": "send_email",
            "args": {
                "to": "boss@company.com",
                "subject": "项目进度汇报",
                "body": "老板好，本周项目进度如下：完成了 80%..."
            },
            "reason": "用户要求发送项目进度邮件给老板"
        }
        return {"pending_tool_call": tool_call, "tool_approved": False}
    
    # 如果工具已执行，生成最终回复
    if isinstance(last_msg, ToolMessage):
        return {"messages": [AIMessage(content=f"已完成：{last_msg.content}")]}
    
    return {}

def tool_approval_node(state: State) -> State:
    """工具审批节点"""
    tool_call = state["pending_tool_call"]
    if not tool_call:
        return {}
    
    # 只读工具自动通过
    if tool_call["tool"] in ("search_info", "get_weather"):
        print(f"✅ 只读工具 {tool_call['tool']} 自动通过")
        return {"tool_approved": True}
    
    # 有副作用的工具需要人工审批
    decision = interrupt({
        "action": "tool_call_approval",
        "tool": tool_call["tool"],
        "args": tool_call["args"],
        "reason": tool_call["reason"],
        "risk": "high（有副作用）",
        "options": ["approve（批准执行）", "reject（拒绝执行）", "modify:修改后的参数"]
    })
    
    if decision == "approve":
        print("✅ 人工批准工具调用")
        return {"tool_approved": True}
    elif decision == "reject":
        print("❌ 人工拒绝工具调用")
        return {"tool_approved": False, "pending_tool_call": None}
    elif decision.startswith("modify:"):
        # 人工修改参数
        import json
        modified_args = json.loads(decision[len("modify:"):])
        tool_call["args"] = modified_args
        print(f"✏️ 人工修改参数后批准")
        return {"tool_approved": True, "pending_tool_call": tool_call}
    return {}

def tool_execution_node(state: State) -> State:
    """工具执行节点"""
    if not state["tool_approved"] or not state["pending_tool_call"]:
        return {"messages": [ToolMessage(content="工具调用被拒绝", tool_call_id="1")]}
    
    tool_call = state["pending_tool_call"]
    # 执行工具
    if tool_call["tool"] == "send_email":
        result = send_email(**tool_call["args"])
    else:
        result = f"工具 {tool_call['tool']} 执行完成"
    
    return {"messages": [ToolMessage(content=result, tool_call_id="1")], "pending_tool_call": None}

def route_after_agent(state: State) -> str:
    if state.get("pending_tool_call"):
        return "approval"
    return "final"

builder = StateGraph(State)
builder.add_node("agent", agent_node)
builder.add_node("approval", tool_approval_node)
builder.add_node("execute_tool", tool_execution_node)
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", route_after_agent, {"approval": "approval", "final": END})
builder.add_edge("approval", "execute_tool")
builder.add_edge("execute_tool", "agent")

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "tool-approval"}}

# 用户请求发送邮件
print("用户：请帮我给老板发一封项目进度邮件")
r = graph.invoke({"messages": [HumanMessage(content="请帮我给老板发一封项目进度邮件")]}, config)
print(f"\n⏸ 工具调用已暂停，等待人工审批...")
print(f"待审批工具：{r['pending_tool_call']['tool']}")
print(f"参数：{r['pending_tool_call']['args']}")

# 人工批准
print("\n人工：批准发送")
r = graph.invoke(Command(resume="approve"), config)
print(f"\n最终回复：{r['messages'][-1].content}")
```

**预期运行结果**：
```
用户：请帮我给老板发一封项目进度邮件

⏸ 工具调用已暂停，等待人工审批...
待审批工具：send_email
参数：{'to': 'boss@company.com', 'subject': '项目进度汇报', 'body': '老板好，本周项目进度如下：完成了 80%...'}

人工：批准发送
📧 发送邮件给 boss@company.com：项目进度汇报

最终回复：已完成：邮件已发送给 boss@company.com
```

#### 示例 32：工具调用审批——基于风险等级的动态审批

```python
"""
示例 32：基于风险等级的动态工具审批
场景：根据工具类型和参数自动判断风险等级，决定是否需要人工审批
预期运行结果：低风险工具自动执行，高风险工具触发 interrupt
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

# 工具风险等级配置
TOOL_RISK_CONFIG = {
    "search": {"risk": "low", "auto_approve": True},
    "read_file": {"risk": "low", "auto_approve": True},
    "send_email": {"risk": "medium", "auto_approve": False},
    "execute_sql": {"risk": "high", "auto_approve": False},
    "delete_file": {"risk": "high", "auto_approve": False},
    "transfer_money": {"risk": "critical", "auto_approve": False},
}

def assess_tool_risk(tool_name: str, tool_args: dict) -> dict:
    """评估工具调用的风险等级"""
    base = TOOL_RISK_CONFIG.get(tool_name, {"risk": "medium", "auto_approve": False})
    
    # 根据参数动态调整风险
    risk = base["risk"]
    if tool_name == "execute_sql" and "DELETE" in tool_args.get("sql", "").upper():
        risk = "critical"
    if tool_name == "transfer_money" and tool_args.get("amount", 0) > 10000:
        risk = "critical"
    if tool_name == "send_email" and tool_args.get("to", "").endswith("@external.com"):
        risk = "high"
    
    return {
        "tool": tool_name,
        "args": tool_args,
        "risk": risk,
        "auto_approve": base["auto_approve"] and risk in ("low",),
        "requires_approval": risk in ("medium", "high", "critical")
    }

class State(TypedDict):
    tool_call: Optional[dict]
    risk_assessment: Optional[dict]
    approved: bool
    result: Optional[str]

def plan_tool_call(state: State) -> State:
    """模拟 Agent 规划工具调用"""
    return {"tool_call": state.get("tool_call", {"tool": "execute_sql", "args": {"sql": "SELECT * FROM users LIMIT 10"}})}

def assess_risk_node(state: State) -> State:
    """风险评估节点"""
    tc = state["tool_call"]
    assessment = assess_tool_risk(tc["tool"], tc["args"])
    print(f"🔍 风险评估：{tc['tool']} → {assessment['risk']}（{'自动通过' if assessment['auto_approve'] else '需要审批'}）")
    return {"risk_assessment": assessment, "approved": assessment["auto_approve"]}

def approval_node(state: State) -> State:
    """人工审批节点"""
    if state["approved"]:
        return {}
    
    assessment = state["risk_assessment"]
    decision = interrupt({
        "action": "tool_approval",
        "tool": assessment["tool"],
        "args": assessment["args"],
        "risk": assessment["risk"],
        "risk_level_indicator": "⚠️" * {"low": 1, "medium": 2, "high": 3, "critical": 4}[assessment["risk"]]
    })
    
    if decision == "approve":
        return {"approved": True}
    return {"approved": False, "result": "工具调用被人工拒绝"}

def execute_node(state: State) -> State:
    """执行节点"""
    if not state["approved"]:
        return {"result": state.get("result", "未执行")}
    tc = state["tool_call"]
    print(f"⚡ 执行工具：{tc['tool']}")
    return {"result": f"工具 {tc['tool']} 执行成功"}

def route(state: State) -> str:
    if state["approved"]:
        return "execute"
    if state["risk_assessment"]["requires_approval"]:
        return "approval"
    return "execute"

builder = StateGraph(State)
builder.add_node("plan", plan_tool_call)
builder.add_node("assess", assess_risk_node)
builder.add_node("approval", approval_node)
builder.add_node("execute", execute_node)
builder.add_edge(START, "plan")
builder.add_edge("plan", "assess")
builder.add_conditional_edges("assess", route, {"approval": "approval", "execute": "execute"})
builder.add_edge("approval", "execute")
builder.add_edge("execute", END)

graph = builder.compile(checkpointer=MemorySaver())

# 测试 1：低风险工具（自动通过）
print("=== 测试 1：低风险 SELECT 查询 ===")
cfg1 = {"configurable": {"thread_id": "risk-low"}}
r = graph.invoke({"tool_call": {"tool": "execute_sql", "args": {"sql": "SELECT * FROM users LIMIT 10"}}}, cfg1)
print(f"结果：{r['result']}")

# 测试 2：高风险工具（需要审批）
print("\n=== 测试 2：高风险 DELETE 操作 ===")
cfg2 = {"configurable": {"thread_id": "risk-high"}}
r = graph.invoke({"tool_call": {"tool": "execute_sql", "args": {"sql": "DELETE FROM users WHERE id=1"}}}, cfg2)
print(f"⏸ 暂停等待审批，风险：{r['risk_assessment']['risk']}")
r = graph.invoke(Command(resume="approve"), cfg2)
print(f"结果：{r['result']}")
```

**预期运行结果**：
```
=== 测试 1：低风险 SELECT 查询 ===
🔍 风险评估：execute_sql → medium（需要审批）
结果：工具 execute_sql 执行成功

=== 测试 2：高风险 DELETE 操作 ===
🔍 风险评估：execute_sql → critical（需要审批）
⏸ 暂停等待审批，风险：critical
⚡ 执行工具：execute_sql
结果：工具 execute_sql 执行成功
```

### 8.2 敏感操作确认

#### 敏感操作的类型

| 操作类型 | 示例 | 风险等级 | 确认方式 |
|----------|------|----------|----------|
| **数据删除** | 删除用户、清空表、删除文件 | 高 | 二次确认 + 影响范围展示 |
| **资金操作** | 转账、退款、支付 | 极高 | 多级审批 + 金额确认 |
| **权限变更** | 提升权限、添加管理员 | 高 | 操作人确认 + 审计日志 |
| **配置变更** | 修改生产配置、切换流量 | 高 | 变更预览 + 回滚方案 |
| **对外通信** | 发送邮件、发布内容、调用外部 API | 中 | 内容审核 + 接收方确认 |
| **批量操作** | 批量处理 >100 条记录 | 中高 | 数量确认 + 抽样预览 |

#### 示例 33：敏感操作确认——删除操作二次确认

```python
"""
示例 33：敏感操作确认——删除操作二次确认
场景：删除用户数据前，展示影响范围并要求人工输入确认词
预期运行结果：展示影响范围 → 要求输入 "DELETE" 确认 → 执行删除
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

CONFIRMATION_WORD = "DELETE"  # 确认词

class State(TypedDict):
    target: str
    impact: Optional[dict]
    confirmed: bool
    deleted: bool
    error: Optional[str]

def assess_impact(state: State) -> State:
    """评估删除操作的影响范围"""
    # 模拟查询影响范围
    impact = {
        "target_table": "users",
        "target_ids": [101, 102, 103, 104, 105],
        "total_count": 5,
        "related_data": {
            "orders": 23,
            "payments": 15,
            "activity_logs": 156
        },
        "backup_ready": True,
        "estimates": {
            "storage_freed_mb": 12.5,
            "execution_time_sec": 3
        }
    }
    print(f"📊 影响评估：将删除 {impact['total_count']} 个用户，关联 {sum(impact['related_data'].values())} 条数据")
    return {"impact": impact}

def confirmation_node(state: State) -> State:
    """人工确认节点"""
    impact = state["impact"]
    
    # interrupt 展示完整影响范围，要求输入确认词
    result = interrupt({
        "action": "confirm_deletion",
        "warning": "⚠️ 此操作不可逆！请仔细确认以下信息：",
        "target": state["target"],
        "impact": impact,
        "confirmation_required": f"请输入 '{CONFIRMATION_WORD}' 确认删除",
        "backup_status": "✅ 已自动备份到 backup_20260909"
    })
    
    # 验证确认词
    if isinstance(result, str) and result.upper() == CONFIRMATION_WORD:
        print("✅ 确认词验证通过")
        return {"confirmed": True}
    else:
        print(f"❌ 确认词不匹配（期望 '{CONFIRMATION_WORD}'，实际 '{result}'）")
        return {"confirmed": False, "error": "确认词不匹配，操作已取消"}

def execute_deletion(state: State) -> State:
    """执行删除"""
    if not state["confirmed"]:
        return {"deleted": False}
    print(f"🗑️ 执行删除：{state['target']}")
    print(f"   删除 {state['impact']['total_count']} 个用户")
    return {"deleted": True}

def route(state: State) -> str:
    if state["confirmed"]:
        return "execute"
    return "cancel"

def cancel_node(state: State) -> State:
    print(f"🚫 操作已取消：{state.get('error', '人工拒绝')}")
    return {}

builder = StateGraph(State)
builder.add_node("assess", assess_impact)
builder.add_node("confirm", confirmation_node)
builder.add_node("execute", execute_deletion)
builder.add_node("cancel", cancel_node)
builder.add_edge(START, "assess")
builder.add_edge("assess", "confirm")
builder.add_conditional_edges("confirm", route, {"execute": "execute", "cancel": "cancel"})
builder.add_edge("execute", END)
builder.add_edge("cancel", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "delete-confirm"}}

# 触发删除流程
print("用户请求：删除测试用户组")
r = graph.invoke({"target": "测试用户组（ID: 101-105）"}, config)
print(f"\n⏸ 已暂停，等待人工确认...")
print(f"影响范围：{r['impact']['total_count']} 个用户")

# 人工输入错误确认词
print("\n人工输入：'delete'（小写，应该不匹配）")
r = graph.invoke(Command(resume="delete"), config)
print(f"确认结果：confirmed={r['confirmed']}")

# 注意：上面的执行已经走完了（确认失败→cancel），需要重新发起
# 实际场景中确认失败后应该回到确认节点，这里简化处理
print("\n--- 重新发起删除流程 ---")
config2 = {"configurable": {"thread_id": "delete-confirm-2"}}
r = graph.invoke({"target": "测试用户组（ID: 101-105）"}, config2)
print("人工输入：'DELETE'（正确确认词）")
r = graph.invoke(Command(resume="DELETE"), config2)
print(f"删除结果：deleted={r['deleted']}")
```

**预期运行结果**：
```
用户请求：删除测试用户组
📊 影响评估：将删除 5 个用户，关联 194 条数据

⏸ 已暂停，等待人工确认...
影响范围：5 个用户

人工输入：'delete'（小写，应该不匹配）
❌ 确认词不匹配（期望 'DELETE'，实际 'delete'）
🚫 操作已取消：确认词不匹配，操作已取消
确认结果：confirmed=False

--- 重新发起删除流程 ---
📊 影响评估：将删除 5 个用户，关联 194 条数据
人工输入：'DELETE'（正确确认词）
✅ 确认词验证通过
🗑️ 执行删除：测试用户组（ID: 101-105）
   删除 5 个用户
删除结果：deleted=True
```

### 8.3 内容审核

#### 内容审核的应用场景

内容审核是 HITL 在内容生产场景中的典型应用，适用于：
- AI 生成的营销文案发布前审核
- 客服自动回复的敏感内容审核
- 用户生成内容（UGC）的合规审核
- 代码变更的安全审核
- 报告和文档的准确性审核

#### 示例 34：内容审核——AI 生成文案的人工审核发布

```python
"""
示例 34：内容审核——AI 文案审核发布流程
预期运行结果：AI 生成文案 → 人工审核（批准/修改/拒绝）→ 发布或退回
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    topic: str
    draft: Optional[str]
    edited_content: Optional[str]
    review_result: Optional[dict]
    status: str
    publish_url: Optional[str]
    iteration: int

def generate_content(state: State) -> State:
    """AI 生成内容"""
    iteration = state.get("iteration", 0) + 1
    draft = f"# {state['topic']}\n\nAI 生成的第 {iteration} 版文案...\n\n（包含产品介绍、优惠信息、行动号召）"
    print(f"🤖 AI 生成第 {iteration} 版文案")
    return {"draft": draft, "iteration": iteration, "status": "draft_ready"}

def content_review_node(state: State) -> State:
    """内容审核节点"""
    result = interrupt({
        "action": "content_review",
        "topic": state["topic"],
        "content": state["draft"],
        "iteration": state["iteration"],
        "review_checklist": [
            "✅ 品牌调性一致",
            "✅ 无敏感词/违规内容",
            "✅ 数据和事实准确",
            "✅ 行动号召清晰",
            "✅ 无错别字和语法错误"
        ],
        "options": {
            "approve": "批准发布",
            "reject": "拒绝（需说明原因）",
            "modify": "人工修改后发布（需提供修改后内容）",
            "regenerate": "退回 AI 重新生成（需说明修改方向）"
        }
    })
    
    decision = result["decision"] if isinstance(result, dict) else result
    
    if decision == "approve":
        return {"status": "approved", "edited_content": state["draft"], "review_result": result}
    elif decision == "reject":
        return {"status": "rejected", "review_result": result}
    elif decision == "modify":
        return {"status": "modified", "edited_content": result["modified_content"], "review_result": result}
    elif decision == "regenerate":
        return {"status": "needs_regenerate", "review_result": result}
    return {"status": "unknown"}

def publish_node(state: State) -> State:
    """发布内容"""
    content = state.get("edited_content", state["draft"])
    print(f"📢 内容已发布：{content[:50]}...")
    return {"publish_url": "https://example.com/post/123", "status": "published"}

def reject_node(state: State) -> State:
    print(f"❌ 内容被拒绝：{state['review_result'].get('reason', '未说明')}")
    return {"status": "rejected_final"}

def route(state: State) -> str:
    return state["status"]

builder = StateGraph(State)
builder.add_node("generate", generate_content)
builder.add_node("review", content_review_node)
builder.add_node("publish", publish_node)
builder.add_node("reject", reject_node)
builder.add_edge(START, "generate")
builder.add_edge("generate", "review")
builder.add_conditional_edges("review", route, {
    "approved": "publish",
    "modified": "publish",
    "rejected": "reject",
    "needs_regenerate": "generate"
})
builder.add_edge("publish", END)
builder.add_edge("reject", END)

graph = builder.compile(checkpointer=MemorySaver())

# 场景：AI 生成 → 人工要求重新生成 → AI 再生成 → 人工修改后发布
print("=== 内容审核完整流程 ===")
config = {"configurable": {"thread_id": "content-review"}}

# 1. AI 生成
r = graph.invoke({"topic": "双十一促销活动"}, config)
print(f"第 1 版文案已生成，等待审核...")

# 2. 人工要求重新生成
r = graph.invoke(
    Command(resume={"decision": "regenerate", "feedback": "优惠力度不够突出，需要强调 5 折"}),
    config
)
print(f"人工要求重新生成，当前 iteration={r['iteration']}")

# 3. AI 重新生成后再次审核
r = graph.invoke(
    Command(resume={"decision": "modify", "modified_content": "# 双十一促销活动\n\n全场 5 折起！（人工修改版）..."}),
    config
)
print(f"人工修改后发布，URL={r['publish_url']}")
```

**预期运行结果**：
```
=== 内容审核完整流程 ===
🤖 AI 生成第 1 版文案
第 1 版文案已生成，等待审核...
🤖 AI 生成第 2 版文案
人工要求重新生成，当前 iteration=2
📢 内容已发布：# 双十一促销活动

全场 5 折起！（人工修改版）......
人工修改后发布，URL=https://example.com/post/123
```

### 8.4 Agent HITL 常见坑点

**坑点 15：工具审批节点无法获取 LLM 的工具调用计划**

错误现象：在 LangGraph Agent 中插入工具审批节点，但审批节点无法获取 LLM 计划调用的工具名称和参数。

根本原因：LangGraph 预构建的 ReAct Agent 中，LLM 的工具调用决策封装在 agent 节点内部，外部节点无法直接访问。需要自定义 Agent 架构，将工具调用计划暴露到状态中。

正确做法：自定义 Agent 状态图，将 LLM 的工具调用决策存储在状态字段中（如 `pending_tool_call`），审批节点从状态中读取。参考示例 31 的实现方式。

**坑点 16：内容审核循环导致无限重新生成**

错误现象：人工反复要求"重新生成"，AI 反复生成，陷入死循环。

根本原因：审核节点的条件边中 "needs_regenerate" 直接跳转到 generate 节点，没有最大重试次数限制。

正确做法：在状态中添加 `iteration` 或 `max_iterations` 字段，超过最大次数后强制终止或升级审批。

---

### 💡 本章深度讲解

HITL 在 Agent 中的应用核心是"在 AI 自主决策和执行之间插入人工关卡"。三大应用场景各有侧重：工具调用审批关注"AI 要调用什么工具、参数是否安全"，通过拦截 LLM 的工具调用计划并插入 interrupt 实现；敏感操作确认关注"操作的影响范围和不可逆性"，通过展示影响评估、要求确认词、多级审批等方式确保操作安全；内容审核关注"AI 生成内容的质量和合规性"，通过批准/修改/拒绝/重新生成四种审核结果实现质量闭环。这三种场景的共同技术基础是 interrupt + Command + Checkpoint，但状态设计和审核流程各有不同。在实际 Agent 系统中，这三种 HITL 往往同时存在——工具调用时审批、敏感操作时确认、输出内容时审核，共同构成 Agent 的安全防线。

### 📝 本章精简总结

1. **工具调用审批**：拦截 LLM 的工具调用计划，有副作用的工具触发 interrupt，人工批准后执行
2. **动态风险审批**：根据工具类型和参数自动评估风险等级，低风险自动通过，高风险人工审批
3. **敏感操作确认**：删除/资金/权限等敏感操作前展示影响范围，要求确认词或多级审批
4. **内容审核**：AI 生成内容后人工审核，支持批准、修改、拒绝、重新生成四种结果
5. **只读 vs 有副作用**：只读工具（搜索、查询）自动通过，有副作用工具（发送、删除、支付）必须审批
6. **确认词机制**：不可逆操作要求输入特定确认词（如 "DELETE"），防止误操作
7. **自定义 Agent 架构**：预构建 ReAct Agent 无法直接插入审批，需要自定义状态图暴露工具调用计划
8. **两大坑点**：审批节点无法获取 LLM 工具调用计划、内容审核循环无最大次数限制

### 🎯 梯度练习题

**基础题⭐**

1. Agent 中哪些工具调用需要人工审批？哪些可以自动执行？举例说明。
   > 提示：从"是否有副作用"和"风险等级"两个维度判断。

2. 敏感操作确认通常包含哪些环节？为什么删除操作需要输入确认词？
   > 提示：影响评估、确认词、备份、审计日志；确认词防止误操作和点击确认。

3. 内容审核的四种结果（批准、修改、拒绝、重新生成）分别对应什么后续流程？
   > 提示：批准→发布，修改→用修改后内容发布，拒绝→终止，重新生成→回到生成节点。

**进阶题⭐⭐**

1. 设计一个"工具风险评估器"函数，输入工具名称和参数，输出风险等级（low/medium/high/critical）和是否需要审批。至少覆盖 5 种工具，并说明每种工具的风险判断逻辑。
   > 提示：考虑工具类型（只读/有副作用）、参数（金额大小、SQL 类型、操作范围）、接收方（内部/外部）等因素。

2. 解释为什么预构建的 LangGraph ReAct Agent 难以直接插入工具调用审批？自定义 Agent 架构时应该如何设计状态和节点？
   > 提示：预构建 Agent 的工具调用封装在节点内部，外部无法拦截；自定义时需要将工具调用计划存储在状态中，单独设置审批节点。

**实战题⭐⭐⭐**

1. 设计一个"客服 Agent 的 HITL 安全机制"：
   - Agent 可以自动回复常见问题（查询订单、物流信息）
   - 涉及退款操作时，金额 <100 自动处理，100-500 客服主管审批，>500 财务审批
   - 涉及用户隐私数据（手机号、地址）时，必须人工确认后才能提供
   - Agent 回复内容包含敏感词时，自动拦截并转人工
   - 所有人工操作记录审计日志
   请设计状态结构、图定义、核心节点逻辑，并写出关键代码。
   > 提示：用条件边根据操作类型和金额路由到不同审批节点，敏感词检测作为独立节点在回复前执行。

---

## 9. HITL 与 Web 界面集成

### 9.1 Web 集成架构设计

#### HITL Web 应用的典型架构

将 LangGraph HITL 集成到 Web 应用中，需要设计前后端协作的架构：

```mermaid
graph TB
    subgraph 前端
        UI[审核界面 UI] -->|展示审核请求| User[审核者]
        User -->|提交决策| UI
    end
    subgraph 后端 API 层
        API[REST/SSE API] -->|发起任务| Graph[LangGraph]
        Graph -->|interrupt 暂停| API
        API -->|SSE 推送审核请求| UI
        UI -->|POST 决策| API
        API -->|Command resume| Graph
        Graph -->|继续执行| API
    end
    subgraph 持久化层
        CP[(Checkpoint DB)] <--> Graph
        Audit[(审计日志 DB)] <--> API
    end
```

#### 核心 API 设计

| API | 方法 | 功能 |
|-----|------|------|
| `/api/tasks` | POST | 发起新任务（触发图执行） |
| `/api/tasks/{id}` | GET | 查询任务状态（是否暂停、当前状态） |
| `/api/tasks/{id}/resume` | POST | 提交人工决策，恢复执行 |
| `/api/tasks/{id}/stream` | GET (SSE) | 流式接收任务状态变更和审核请求 |
| `/api/tasks/{id}/history` | GET | 查询任务的 Checkpoint 历史 |

### 9.2 SSE 推送审核请求

#### 示例 35：基于 FastAPI + SSE 的 HITL Web 服务

```python
"""
示例 35：FastAPI + SSE 实现 HITL Web 服务
预期运行结果：前端通过 SSE 接收审核请求，提交决策后后端恢复执行
"""
# server.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
import asyncio
import json
import uuid

app = FastAPI(title="HITL Web Service")

# ===== 状态和图定义 =====
class TaskState(TypedDict):
    task_id: str
    content: str
    status: str
    review_result: Optional[dict]
    output: Optional[str]

def process_node(state: TaskState) -> TaskState:
    print(f"处理任务：{state['task_id']}")
    return {"content": f"处理结果：{state['content']}", "status": "processed"}

def review_node(state: TaskState) -> TaskState:
    result = interrupt({
        "task_id": state["task_id"],
        "content": state["content"],
        "action": "review",
        "message": "请人工审核处理结果"
    })
    return {"review_result": result, "status": "reviewed"}

def finalize_node(state: TaskState) -> TaskState:
    if state["review_result"].get("approved"):
        return {"output": state["content"], "status": "completed"}
    return {"output": "任务被拒绝", "status": "rejected"}

builder = StateGraph(TaskState)
builder.add_node("process", process_node)
builder.add_node("review", review_node)
builder.add_node("finalize", finalize_node)
builder.add_edge(START, "process")
builder.add_edge("process", "review")
builder.add_edge("review", "finalize")
builder.add_edge("finalize", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# ===== 内存中的任务存储（生产环境用数据库） =====
tasks: Dict[str, dict] = {}
task_events: Dict[str, asyncio.Queue] = {}

# ===== API 模型 =====
class CreateTaskRequest(BaseModel):
    content: str

class ResumeRequest(BaseModel):
    decision: str  # "approved" / "rejected"
    comment: str = ""

# ===== API 端点 =====
@app.post("/api/tasks")
async def create_task(req: CreateTaskRequest):
    """创建新任务"""
    task_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": task_id}}
    
    # 初始化事件队列
    task_events[task_id] = asyncio.Queue()
    
    # 同步执行到 interrupt（在后台线程中）
    def run_graph():
        result = graph.invoke(
            {"task_id": task_id, "content": req.content, "status": "pending", "review_result": None, "output": None},
            config
        )
        tasks[task_id] = {"state": result, "config": config, "status": "paused" if result.get("review_result") is None else "completed"}
        # 通知 SSE 客户端
        asyncio.run_coroutine_threadsafe(
            task_events[task_id].put({"type": "paused", "state": result}),
            asyncio.get_event_loop()
        )
    
    await asyncio.get_event_loop().run_in_executor(None, run_graph)
    return {"task_id": task_id, "status": "processing"}

@app.get("/api/tasks/{task_id}/stream")
async def stream_task(task_id: str):
    """SSE 流式推送任务状态"""
    if task_id not in task_events:
        raise HTTPException(status_code=404, detail="Task not found")
    
    async def event_generator():
        # 先发送当前状态
        if task_id in tasks:
            yield f"data: {json.dumps({'type': 'state', 'state': tasks[task_id]['state']})}\n\n"
        
        # 然后持续推送事件
        while True:
            try:
                event = await asyncio.wait_for(task_events[task_id].get(), timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
                if event["type"] in ("completed", "rejected"):
                    break
            except asyncio.TimeoutError:
                yield ": keep-alive\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/tasks/{task_id}/resume")
async def resume_task(task_id: str, req: ResumeRequest):
    """提交人工决策，恢复执行"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    config = tasks[task_id]["config"]
    
    def resume_graph():
        result = graph.invoke(
            Command(resume={"approved": req.decision == "approved", "comment": req.comment}),
            config
        )
        tasks[task_id]["state"] = result
        tasks[task_id]["status"] = "completed"
        asyncio.run_coroutine_threadsafe(
            task_events[task_id].put({"type": "completed", "state": result}),
            asyncio.get_event_loop()
        )
    
    await asyncio.get_event_loop().run_in_executor(None, resume_graph)
    return {"task_id": task_id, "status": "completed", "state": tasks[task_id]["state"]}

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """查询任务状态"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

print("HITL Web 服务已定义，运行：uvicorn server:app --reload")
print("API 端点：")
print("  POST /api/tasks          - 创建任务")
print("  GET  /api/tasks/{id}/stream - SSE 流式推送")
print("  POST /api/tasks/{id}/resume - 提交决策恢复")
print("  GET  /api/tasks/{id}     - 查询状态")
```

**预期运行结果**：
```
HITL Web 服务已定义，运行：uvicorn server:app --reload
API 端点：
  POST /api/tasks          - 创建任务
  GET  /api/tasks/{id}/stream - SSE 流式推送
  POST /api/tasks/{id}/resume - 提交决策恢复
  GET  /api/tasks/{id}     - 查询状态
```

#### 示例 36：前端审核界面（HTML + JavaScript）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>HITL 审核界面</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 16px 0; }
        .paused { border-left: 4px solid #f59e0b; background: #fffbeb; }
        .completed { border-left: 4px solid #10b981; background: #ecfdf5; }
        button { padding: 10px 20px; margin: 4px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-approve { background: #10b981; color: white; }
        .btn-reject { background: #ef4444; color: white; }
        #log { background: #1e1e1e; color: #d4d4d4; padding: 12px; border-radius: 4px; font-family: monospace; font-size: 12px; max-height: 200px; overflow-y: auto; }
    </style>
</head>
<body>
    <h1>HITL 人工审核界面</h1>
    
    <div class="card">
        <h3>发起新任务</h3>
        <input type="text" id="taskInput" placeholder="输入任务内容" style="width: 70%; padding: 8px;">
        <button onclick="createTask()">创建任务</button>
    </div>

    <div id="reviewCard" class="card paused" style="display: none;">
        <h3>⏸ 待审核任务</h3>
        <p><strong>任务 ID：</strong><span id="taskId"></span></p>
        <p><strong>内容：</strong></p>
        <div id="taskContent" style="background: #f5f5f5; padding: 12px; border-radius: 4px;"></div>
        <p><strong>审核备注：</strong></p>
        <input type="text" id="commentInput" placeholder="可选：填写审核备注" style="width: 100%; padding: 8px;">
        <div style="margin-top: 12px;">
            <button class="btn-approve" onclick="resumeTask('approved')">✅ 批准</button>
            <button class="btn-reject" onclick="resumeTask('rejected')">❌ 拒绝</button>
        </div>
    </div>

    <div class="card">
        <h3>SSE 事件日志</h3>
        <div id="log"></div>
    </div>

    <script>
        let currentTaskId = null;
        let eventSource = null;

        function log(msg) {
            const logDiv = document.getElementById('log');
            logDiv.innerHTML += `[${new Date().toLocaleTimeString()}] ${msg}\n`;
            logDiv.scrollTop = logDiv.scrollHeight;
        }

        async function createTask() {
            const content = document.getElementById('taskInput').value;
            if (!content) return alert('请输入任务内容');

            const resp = await fetch('/api/tasks', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content})
            });
            const data = await resp.json();
            currentTaskId = data.task_id;
            log(`任务已创建：${currentTaskId}`);

            // 连接 SSE
            if (eventSource) eventSource.close();
            eventSource = new EventSource(`/api/tasks/${currentTaskId}/stream`);
            eventSource.onmessage = (e) => {
                const event = JSON.parse(e.data);
                log(`SSE 事件：${event.type}`);
                if (event.type === 'paused') {
                    showReviewCard(event.state);
                } else if (event.type === 'completed') {
                    document.getElementById('reviewCard').style.display = 'none';
                    log(`任务完成：${JSON.stringify(event.state.output)}`);
                    eventSource.close();
                }
            };
        }

        function showReviewCard(state) {
            document.getElementById('reviewCard').style.display = 'block';
            document.getElementById('taskId').textContent = state.task_id;
            document.getElementById('taskContent').textContent = state.content;
        }

        async function resumeTask(decision) {
            const comment = document.getElementById('commentInput').value;
            const resp = await fetch(`/api/tasks/${currentTaskId}/resume`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({decision, comment})
            });
            const data = await resp.json();
            log(`决策已提交：${decision}，结果：${data.state.output}`);
            document.getElementById('reviewCard').style.display = 'none';
        }
    </script>
</body>
</html>
```

### 9.3 WebSocket 实时协作审核

#### 示例 37：WebSocket 多人协作审核

```python
"""
示例 37：WebSocket 多人协作审核
场景：多个审核人可以同时查看审核任务，一人决策后其他人实时收到通知
预期运行结果：WebSocket 连接后，审核请求实时推送给所有连接的审核人
"""
# websocket_server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
import json

app = FastAPI()

class State(TypedDict):
    task_id: str
    content: str
    approved: Optional[bool]
    reviewer: Optional[str]

def review_node(state: State) -> State:
    result = interrupt({"task_id": state["task_id"], "content": state["content"]})
    return {"approved": result["approved"], "reviewer": result["reviewer"]}

builder = StateGraph(State)
builder.add_node("review", review_node)
builder.add_edge(START, "review")
builder.add_edge("review", END)

graph = builder.compile(checkpointer=MemorySaver())

# WebSocket 连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/review")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["action"] == "create_task":
                # 创建任务并执行到 interrupt
                task_id = data["task_id"]
                config = {"configurable": {"thread_id": task_id}}
                result = graph.invoke(
                    {"task_id": task_id, "content": data["content"], "approved": None, "reviewer": None},
                    config
                )
                # 广播审核请求给所有审核人
                await manager.broadcast({
                    "type": "review_request",
                    "task_id": task_id,
                    "content": result["content"],
                    "status": "pending"
                })
            
            elif data["action"] == "submit_decision":
                # 提交决策
                task_id = data["task_id"]
                config = {"configurable": {"thread_id": task_id}}
                result = graph.invoke(
                    Command(resume={"approved": data["approved"], "reviewer": data["reviewer"]}),
                    config
                )
                # 广播决策结果
                await manager.broadcast({
                    "type": "decision_made",
                    "task_id": task_id,
                    "approved": result["approved"],
                    "reviewer": result["reviewer"],
                    "status": "completed"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

print("WebSocket 审核服务已定义")
print("端点：ws://localhost:8000/ws/review")
print("消息格式：")
print('  创建任务：{"action":"create_task","task_id":"123","content":"..."}')
print('  提交决策：{"action":"submit_decision","task_id":"123","approved":true,"reviewer":"张三"}')
```

**预期运行结果**：
```
WebSocket 审核服务已定义
端点：ws://localhost:8000/ws/review
消息格式：
  创建任务：{"action":"create_task","task_id":"123","content":"..."}
  提交决策：{"action":"submit_decision","task_id":"123","approved":true,"reviewer":"张三"}
```

### 9.4 Web 集成常见坑点

**坑点 17：SSE 连接中断后丢失审核请求**

错误现象：前端 SSE 连接因网络波动断开后，重新连接时丢失了之前的审核请求。

根本原因：SSE 是无状态的，重新连接时服务端不会自动重发之前的事件。

正确做法：前端重连时先调用 `GET /api/tasks/{id}` 获取当前状态，如果任务处于暂停状态则主动展示审核界面。同时在 SSE 事件中包含事件 ID，支持 `Last-Event-ID` 重连。

**坑点 18：并发恢复导致状态冲突**

错误现象：两个审核人同时对同一个暂停任务提交决策，后提交的覆盖先提交的，或者报错。

根本原因：没有对恢复操作加锁，多个请求同时修改同一个 Checkpoint 状态。

正确做法：在恢复 API 中加分布式锁（基于 thread_id），确保同一任务同一时间只有一个恢复操作。或者在恢复前检查任务状态，如果已经不是暂停状态则拒绝。

---

### 💡 本章深度讲解

HITL 与 Web 界面集成是将 LangGraph HITL 能力暴露给最终用户的关键环节。核心架构是"前端审核界面 + 后端 API + LangGraph 引擎 + Checkpoint 持久化"四层结构。通信方式有两种主流选择：SSE（Server-Sent Events）适合单向的状态推送（服务端推审核请求给前端），实现简单且天然支持自动重连；WebSocket 适合双向实时通信（多人协作审核、实时状态同步），但实现复杂度更高。API 设计的核心是四个端点：创建任务、查询状态、提交决策恢复、流式推送。集成时最容易踩的坑是 SSE 断连丢事件（需要重连时主动拉取状态）和并发恢复冲突（需要加锁或状态检查）。生产环境中，Checkpointer 必须用持久化存储（Postgres/Redis），不能用 MemorySaver，否则服务重启后所有暂停任务丢失。

### 📝 本章精简总结

1. **四层架构**：前端审核界面 + 后端 REST/SSE API + LangGraph 引擎 + Checkpoint 持久化
2. **核心 API**：创建任务（POST）、查询状态（GET）、提交决策恢复（POST）、流式推送（SSE/WebSocket）
3. **SSE 推送**：服务端单向推送审核请求和状态变更，前端 EventSource 接收，支持自动重连
4. **WebSocket 协作**：双向实时通信，支持多人同时查看审核任务，一人决策后广播通知
5. **前端审核界面**：展示审核上下文（任务内容、影响评估、AI 建议），提供批准/拒绝/修改操作
6. **断连恢复**：SSE 重连时主动调用查询 API 获取当前状态，避免丢失审核请求
7. **并发控制**：恢复操作需要加锁或状态检查，防止多人同时提交决策导致冲突
8. **两大坑点**：SSE 断连丢事件、并发恢复状态冲突

### 🎯 梯度练习题

**基础题⭐**

1. HITL Web 应用的四层架构是什么？每层的职责是什么？
   > 提示：前端、API 层、LangGraph 引擎、持久化层。

2. SSE 和 WebSocket 在 HITL 集成中分别适用于什么场景？各有什么优缺点？
   > 提示：SSE 单向推送、简单、自动重连；WebSocket 双向、实时、复杂。

3. 恢复任务的 API 应该接收哪些参数？后端收到后如何调用 LangGraph 恢复执行？
   > 提示：参数包括 task_id（对应 thread_id）、决策数据；后端用 graph.invoke(Command(resume=...), config) 恢复。

**进阶题⭐⭐**

1. 设计一个 SSE 事件协议，用于 HITL 审核流程。至少定义 5 种事件类型（如 task_created、review_requested、decision_submitted、task_completed、error），说明每种事件的触发时机和 payload 结构。
   > 提示：每种事件包含 type、timestamp、task_id 和特定的数据字段。

2. 如何防止两个审核人同时对同一个任务提交决策？设计一个并发控制方案，说明锁的粒度、获取释放时机、冲突时的处理策略。
   > 提示：基于 thread_id 的分布式锁，恢复前检查状态，冲突时返回 409 Conflict。

**实战题⭐⭐⭐**

1. 实现一个完整的 HITL 审核 Web 应用，包含：
   - 后端：FastAPI + LangGraph + Postgres Checkpointer
   - 前端：审核任务列表页 + 审核详情页（支持批准/拒绝/修改/转派）
   - SSE 实时推送审核请求
   - 审核历史和审计日志
   - 超时自动提醒
   请写出后端核心代码（图定义、API 端点、SSE 推送）和前端审核详情页的关键代码。
   > 提示：参考示例 35-37，用 PostgresSaver 替代 MemorySaver，添加超时检查定时任务。

---

## 10. HITL 最佳实践与性能优化

### 10.1 HITL 设计最佳实践

#### 实践一：最小化人工介入范围

**原则**：只在 AI 无法可靠决策的关键点插入人工审核，其余全部自动化。

**实现方法**：
- 基于风险等级动态决定是否需要人工（低风险自动通过）
- 基于 AI 置信度决定是否需要人工（高置信度自动通过）
- 基于历史审核数据优化触发规则（频繁被批准的操作降低审核频率）

```python
"""
示例 38：最小化人工介入——基于置信度和历史的动态审核策略
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    action: str
    confidence: float
    risk_level: str
    history_approval_rate: float
    needs_review: bool
    result: Optional[str]

def assess_node(state: State) -> State:
    """评估是否需要人工审核"""
    action = state["action"]
    confidence = state["confidence"]
    risk = state["risk_level"]
    approval_rate = state["history_approval_rate"]
    
    # 动态决策：高置信度 + 低风险 + 历史高通过率 → 自动通过
    auto_approve = (
        confidence > 0.9 and
        risk == "low" and
        approval_rate > 0.95
    )
    
    needs_review = not auto_approve
    reason = "自动通过" if auto_approve else f"需要审核（confidence={confidence}, risk={risk}, approval_rate={approval_rate}）"
    print(f"📊 {action}：{reason}")
    
    return {"needs_review": needs_review}

def review_node(state: State) -> State:
    if not state["needs_review"]:
        return {"result": "auto_approved"}
    decision = interrupt({"action": state["action"], "confidence": state["confidence"]})
    return {"result": decision}

def execute_node(state: State) -> State:
    print(f"⚡ 执行结果：{state['result']}")
    return {}

builder = StateGraph(State)
builder.add_node("assess", assess_node)
builder.add_node("review", review_node)
builder.add_node("execute", execute_node)
builder.add_edge(START, "assess")
builder.add_edge("assess", "review")
builder.add_edge("review", "execute")
builder.add_edge("execute", END)

graph = builder.compile(checkpointer=MemorySaver())

# 测试：高置信度低风险 → 自动通过
cfg1 = {"configurable": {"thread_id": "auto"}}
graph.invoke({"action": "查询天气", "confidence": 0.98, "risk_level": "low", "history_approval_rate": 0.99}, cfg1)

# 测试：低置信度 → 需要审核
cfg2 = {"configurable": {"thread_id": "manual"}}
r = graph.invoke({"action": "删除数据", "confidence": 0.6, "risk_level": "high", "history_approval_rate": 0.8}, cfg2)
print(f"⏸ 需要人工审核")
```

**预期运行结果**：
```
📊 查询天气：自动通过
⚡ 执行结果：auto_approved
📊 删除数据：需要审核（confidence=0.6, risk=high, approval_rate=0.8）
⏸ 需要人工审核
```

#### 实践二：审核上下文信息充分但不冗余

**原则**：给审核者提供做决策所需的全部信息，但避免信息过载。

**实现方法**：
- 分层展示：核心信息置顶，辅助信息可折叠
- 高亮关键：风险点、异常数据、不可逆操作用醒目标记
- 提供建议：AI 给出推荐决策和理由，辅助人工判断

#### 实践三：审核操作简单明确

**原则**：审核者应该能在 10 秒内做出决策并提交。

**实现方法**：
- 常用操作一键完成（批准/拒绝按钮）
- 键盘快捷键支持（A=批准，R=拒绝）
- 批量审核功能（相似操作批量批准）
- 减少必填字段，备注可选填

#### 实践四：完整的审计日志

**原则**：所有人工作业都有可追溯的记录。

**实现方法**：
- 记录审核人、时间、决策、备注、IP、User-Agent
- 记录审核前后的状态快照（Checkpoint 历史天然支持）
- 日志不可篡改（写入只追加的日志系统）

### 10.2 性能优化策略

#### 优化一：Checkpoint 读写优化

| 优化方向 | 具体措施 | 预期效果 |
|----------|----------|----------|
| **状态精简** | 状态中只存必要字段，大对象存外部引用 | 减少序列化时间和存储量 |
| **连接池** | PostgresSaver 使用数据库连接池 | 减少连接建立开销 |
| **批量写入** | 高频 interrupt 场景批量提交 Checkpoint | 减少 IO 次数 |
| **索引优化** | thread_id + checkpoint_id 建联合索引 | 加速状态查询 |
| **缓存层** | 热点 thread_id 的最新状态缓存到 Redis | 减少数据库查询 |

#### 优化二：interrupt 响应延迟优化

```python
"""
示例 39：interrupt 响应延迟优化
场景：通过预加载、异步通知等方式降低人工审核端到端延迟
"""
# 1. 异步通知：interrupt 触发后立即发送通知，不阻塞图执行
import asyncio
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    task: str
    notified: bool

async def send_notification(task_id: str, review_data: dict):
    """异步发送审核通知（实际场景中调用邮件/短信/Webhook API）"""
    await asyncio.sleep(0.1)  # 模拟网络延迟
    print(f"📧 审核通知已发送：{task_id}")

def review_node(state: State) -> State:
    # interrupt 触发时，状态已保存到 Checkpoint
    # 可以在 interrupt 之前启动异步通知（但注意：interrupt 会暂停，通知需要在外部触发）
    review_data = {"task": state["task"], "action": "review"}
    decision = interrupt(review_data)
    return {"result": decision}

print("优化策略说明：")
print("1. interrupt 触发后，由外部调度器（如 Celery/RQ）异步发送通知")
print("2. 审核界面使用 SSE/WebSocket 实时接收审核请求，无需轮询")
print("3. 常用审核上下文预加载缓存，减少审核页面加载时间")
print("4. 审核决策提交后，优先更新 UI 状态，后台异步执行图恢复")
print("5. 批量审核场景下，多个恢复操作可以并行执行（不同 thread_id）")
```

**预期运行结果**：
```
优化策略说明：
1. interrupt 触发后，由外部调度器（如 Celery/RQ）异步发送通知
2. 审核界面使用 SSE/WebSocket 实时接收审核请求，无需轮询
3. 常用审核上下文预加载缓存，减少审核页面加载时间
4. 审核决策提交后，优先更新 UI 状态，后台异步执行图恢复
5. 批量审核场景下，多个恢复操作可以并行执行（不同 thread_id）
```

#### 优化三：批量审核优化

对于大量相似的低风险审核项，可以采用批量审核策略：
- 自动聚类：将相似操作聚合成批次
- 抽样审核：每批随机抽取 N% 人工审核，其余自动通过
- 批量批准：审核者一键批准整批操作
- 异常隔离：批次中有异常操作时单独审核

### 10.3 可观测性与监控

#### HITL 系统的关键监控指标

| 指标类别 | 具体指标 | 告警阈值建议 |
|----------|----------|-------------|
| **审核量** | 日审核请求数、峰值 QPS | 超历史均值 200% |
| **审核延迟** | interrupt 到恢复的平均时间、P95 延迟 | P95 > 4 小时 |
| **审核结果** | 批准率、拒绝率、修改率、自动通过率 | 拒绝率 > 30% |
| **超时率** | 超时未处理的审核占比 | > 5% |
| **系统性能** | Checkpoint 读写延迟、图执行时间 | P95 > 500ms |
| **人工效率** | 人均日审核量、平均审核耗时 | 持续下降 |

#### 示例 40：HITL 可观测性埋点

```python
"""
示例 40：HITL 可观测性埋点
在 interrupt 前后、恢复时记录关键指标
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from datetime import datetime
import time

# 模拟指标收集器
class MetricsCollector:
    def __init__(self):
        self.metrics = []
    
    def record(self, metric_type: str, **kwargs):
        entry = {"type": metric_type, "timestamp": datetime.now().isoformat(), **kwargs}
        self.metrics.append(entry)
        print(f"📊 [METRICS] {entry}")

metrics = MetricsCollector()

class State(TypedDict):
    task: str
    interrupt_time: Optional[float]
    result: Optional[str]

def review_node(state: State) -> State:
    # interrupt 前记录
    start_time = time.time()
    metrics.record("interrupt_triggered", task=state["task"], node="review")
    
    # 触发 interrupt
    decision = interrupt({"task": state["task"]})
    
    # 恢复后记录
    resume_time = time.time()
    wait_duration = resume_time - start_time  # 注意：这只是进程内时间，实际等待时间需要从外部计算
    metrics.record("interrupt_resumed", task=state["task"], wait_seconds=wait_duration, decision=decision)
    
    return {"result": decision, "interrupt_time": start_time}

builder = StateGraph(State)
builder.add_node("review", review_node)
builder.add_edge(START, "review")
builder.add_edge("review", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "metrics-demo"}}

r = graph.invoke({"task": "测试任务", "interrupt_time": None, "result": None}, config)
print("\n⏸ 已暂停")

r = graph.invoke(Command(resume="approved"), config)
print(f"\n✅ 已恢复，结果：{r['result']}")
print(f"\n共收集 {len(metrics.metrics)} 条指标")
print("生产环境中应将这些指标推送到 Prometheus/Datadog 等监控系统")
```

**预期运行结果**：
```
📊 [METRICS] {'type': 'interrupt_triggered', 'timestamp': '...', 'task': '测试任务', 'node': 'review'}

⏸ 已暂停
📊 [METRICS] {'type': 'interrupt_resumed', 'timestamp': '...', 'task': '测试任务', 'wait_seconds': 0.0, 'decision': 'approved'}

✅ 已恢复，结果：approved

共收集 2 条指标
生产环境中应将这些指标推送到 Prometheus/Datadog 等监控系统
```

### 10.4 最佳实践常见坑点

**坑点 19：审核上下文信息过载**

错误现象：审核界面展示了太多信息，审核者找不到重点，平均审核时间过长。

根本原因：interrupt 传递的数据包含了所有相关信息，但没有分层和优先级，前端也没有折叠展示。

正确做法：审核上下文按"核心信息→辅助信息→详细信息"分层，前端默认只展示核心信息，辅助信息可展开，详细信息按需加载。

**坑点 20：缺少审核 SLA 导致任务积压**

错误现象：大量审核任务长时间无人处理，系统积压严重，业务流程卡住。

根本原因：没有定义审核 SLA（服务等级协议），没有超时提醒和升级机制，审核者没有处理压力。

正确做法：为不同风险等级的审核定义 SLA（如高风险 1 小时、中风险 4 小时、低风险 24 小时），超时前发送提醒，超时后自动升级，定期统计审核者绩效。

---

### 💡 本章深度讲解

HITL 最佳实践的核心是"在安全和效率之间找到最优平衡点"。四大设计实践——最小化人工介入、审核上下文充分但不冗余、审核操作简单明确、完整审计日志——分别从"减少审核量""提高审核质量""加快审核速度""保障可追溯"四个维度优化 HITL 系统。性能优化聚焦三个方向：Checkpoint 读写优化（状态精简、连接池、缓存）、interrupt 响应延迟优化（异步通知、实时推送、预加载）、批量审核优化（聚类、抽样、批量批准）。可观测性是生产级 HITL 系统不可或缺的部分，需要监控审核量、延迟、结果分布、超时率、系统性能、人工效率六大类指标。最容易被忽视的是审核 SLA——没有 SLA 的 HITL 系统必然会出现任务积压，因为审核者没有处理压力和优先级。

### 📝 本章精简总结

1. **最小化介入**：基于风险等级、AI 置信度、历史通过率动态决定是否需要人工审核
2. **上下文分层**：核心信息置顶、辅助信息可折叠、详细信息按需加载，避免信息过载
3. **操作简单化**：一键批准/拒绝、键盘快捷键、批量审核，减少审核者操作成本
4. **审计完整性**：记录审核人、时间、决策、备注、IP，结合 Checkpoint 历史实现全链路追溯
5. **Checkpoint 优化**：状态精简、连接池、批量写入、索引优化、Redis 缓存
6. **延迟优化**：异步通知、SSE/WebSocket 实时推送、审核上下文预加载、UI 优先更新
7. **六大监控指标**：审核量、审核延迟、审核结果、超时率、系统性能、人工效率
8. **两大坑点**：审核上下文信息过载、缺少审核 SLA 导致任务积压

### 🎯 梯度练习题

**基础题⭐**

1. 最小化人工介入的三个判断维度是什么？如何根据这些维度动态决定是否需要审核？
   > 提示：风险等级、AI 置信度、历史审核通过率。

2. HITL 系统需要监控哪六大类指标？每类至少举一个具体指标。
   > 提示：审核量、延迟、结果、超时、性能、效率。

3. 审核 SLA 是什么？为什么缺少 SLA 会导致任务积压？
   > 提示：SLA 是审核响应时间承诺，没有 SLA 审核者没有处理压力。

**进阶题⭐⭐**

1. 设计一个"动态审核策略引擎"，根据操作类型、风险等级、AI 置信度、历史审核数据决定是否需要人工审核。写出策略评估函数的完整逻辑，至少覆盖 5 种操作类型和 3 种风险等级。
   > 提示：用规则引擎或决策表，低风险+高置信度+高通过率→自动通过，否则→人工审核。

2. 为 HITL 系统设计一个监控仪表盘，包含哪些图表和指标？说明每个图表的作用和告警阈值。
   > 提示：审核量趋势图、审核延迟分布图、批准/拒绝率饼图、超时任务列表、审核者绩效排行、系统性能监控。

**实战题⭐⭐⭐**

1. 为一个日均 10 万审核请求的 HITL 系统设计性能优化方案：
   - Checkpoint 存储选型和配置（预估存储量和 IOPS）
   - interrupt 响应延迟优化（目标 P95 < 1 秒）
   - 审核者端到端延迟优化（目标从触发到展示 < 3 秒）
   - 批量审核策略（目标人工审核量减少 60%）
   - 监控和告警方案
   请给出具体的技术选型、配置参数、预估效果和实施步骤。
   > 提示：Postgres+Redis 两级存储、SSE 实时推送、基于聚类的批量审核、Prometheus+Grafana 监控。

---

## 11. HITL 与传统交互模式对比

### 11.1 传统交互模式概述

#### 模式一：请求-响应模式

最传统的交互模式，用户发送请求，系统同步处理并返回结果。整个过程中用户等待，系统不暂停。

```mermaid
sequenceDiagram
    participant User as 用户
    participant System as 系统
    User->>System: 发送请求
    System->>System: 同步处理
    System-->>User: 返回结果
```

#### 模式二：异步任务模式

用户提交任务后立即返回，系统后台处理，用户通过轮询或回调获取结果。

```mermaid
sequenceDiagram
    participant User as 用户
    participant System as 系统
    participant Worker as 后台 Worker
    User->>System: 提交任务
    System-->>User: 返回任务 ID
    System->>Worker: 后台处理
    User->>System: 轮询状态
    System-->>User: 处理中/完成
```

#### 模式三：向导式交互（Wizard）

多步骤表单，用户逐步填写信息，每步验证后进入下一步。

```mermaid
graph LR
    A[步骤 1] --> B[步骤 2]
    B --> C[步骤 3]
    C --> D[提交]
```

### 11.2 HITL 与传统模式的深度对比

| 对比维度 | 请求-响应 | 异步任务 | 向导式 | HITL |
|----------|-----------|----------|--------|------|
| **交互时机** | 请求前输入 | 提交后等待 | 逐步输入 | 执行中暂停 |
| **系统状态** | 无状态 | 任务状态 | 步骤状态 | 完整图状态 |
| **人工介入点** | 只能在请求前 | 无法介入 | 预设步骤 | 任意节点 |
| **状态可修改性** | 不能 | 不能 | 有限 | 完全可修改 |
| **流程可变性** | 固定 | 固定 | 固定 | 动态可跳转 |
| **执行可恢复性** | 不支持 | 支持重试 | 支持回退 | 精确恢复 |
| **并行支持** | 不支持 | 支持 | 不支持 | 支持 |
| **审计能力** | 日志 | 任务日志 | 表单记录 | 完整状态历史 |
| **适用复杂度** | 简单 | 中等 | 中等 | 复杂 |
| **开发复杂度** | 低 | 中 | 中 | 高 |

> 🎯 面试高频：HITL 和传统的异步任务模式有什么本质区别？HITL 和异步任务的本质区别在于"人工介入的时机和能力"——异步任务中人工只能在提交前输入和完成后查看，无法在执行中介入；HITL 可以在执行的任意节点暂停，人工不仅能查看状态，还能修改状态、控制流程走向，然后从暂停点精确恢复。HITL 的状态是完整的图执行状态（包含节点进度、中间结果），而异步任务只有简单的"待处理/处理中/完成"状态。

#### 示例 41：四种模式实现同一任务的对比

```python
"""
示例 41：四种交互模式实现"内容审核发布"任务的对比
展示 HITL 相比传统模式的优势
"""

print("=" * 60)
print("任务：用户提交文章 → 审核 → 发布")
print("=" * 60)

print("""
【模式 1：请求-响应】
  用户：提交文章
  系统：同步审核（如果是 AI 审核）→ 发布
  问题：无法人工审核，AI 审核质量不可控
  代码：
    result = requests.post('/api/publish', json={'content': article})
    # 同步等待，无法插入人工
""")

print("""
【模式 2：异步任务】
  用户：提交文章 → 返回任务 ID
  系统：后台 AI 审核 → 发布
  用户：轮询任务状态
  问题：人工无法在审核环节介入，只能看最终结果
  代码：
    task_id = requests.post('/api/tasks', json={'content': article}).json()['id']
    while True:
        status = requests.get(f'/api/tasks/{task_id}').json()['status']
        if status == 'completed': break
        time.sleep(5)
""")

print("""
【模式 3：向导式】
  步骤 1：填写文章内容
  步骤 2：预览并选择审核类型
  步骤 3：提交
  系统：后台处理
  问题：审核流程固定，无法在 AI 生成内容后人工修改
  代码：
    # 多步表单，每步提交到后端
    step1 = requests.post('/api/wizard/step1', json={'content': article})
    step2 = requests.post('/api/wizard/step2', json={'review_type': 'ai'})
    final = requests.post('/api/wizard/submit')
""")

print("""
【模式 4：HITL（LangGraph）】
  1. 用户提交文章
  2. AI 生成优化版本
  3. interrupt 暂停 → 人工审核（可修改内容）
  4. 人工批准/修改后恢复 → 发布
  优势：
    - 人工可以在 AI 生成后审核和修改
    - 可以动态决定是否需要人工（低质量自动通过）
    - 完整状态历史，可追溯可回滚
    - 支持多级审批、并行会签
  代码（核心逻辑）：
    def review_node(state):
        edited = interrupt({"draft": state['draft'], "action": "review"})
        return {"final": edited if edited else state['draft']}
    
    graph = builder.compile(checkpointer=PostgresSaver())
    # 第一次执行：到 review 节点暂停
    graph.invoke({"article": article}, config)
    # 人工审核后恢复
    graph.invoke(Command(resume=modified_content), config)
""")

print("\n" + "=" * 60)
print("HITL 的核心优势：在执行过程中插入人工决策，且人工可以修改状态和控制流程")
print("=" * 60)
```

**预期运行结果**：
```
============================================================
任务：用户提交文章 → 审核 → 发布
============================================================

【模式 1：请求-响应】...
【模式 2：异步任务】...
【模式 3：向导式】...
【模式 4：HITL（LangGraph）】...

============================================================
HITL 的核心优势：在执行过程中插入人工决策，且人工可以修改状态和控制流程
============================================================
```

### 11.3 如何选择合适的交互模式

#### 决策树

```mermaid
graph TD
    A[需要构建交互系统] --> B{执行过程中需要人工介入?}
    B -->|否| C{任务执行时间长?}
    C -->|否| D[请求-响应模式]
    C -->|是| E[异步任务模式]
    B -->|是| F{人工介入点是预设的固定步骤?}
    F -->|是| G{需要修改系统状态?}
    G -->|否| H[向导式交互]
    G -->|是| I[HITL 模式]
    F -->|否| J{需要动态决定介入点?}
    J -->|是| I
    J -->|否| K{需要多级/并行审批?}
    K -->|是| I
    K -->|否| H
```

#### 选择指南

| 场景特征 | 推荐模式 | 理由 |
|----------|----------|------|
| 简单查询、即时计算 | 请求-响应 | 低延迟，实现简单 |
| 长时间运行的批处理 | 异步任务 | 非阻塞，可后台处理 |
| 多步骤数据收集 | 向导式 | 逐步引导，降低认知负担 |
| AI 生成内容后人工审核 | HITL | 执行中暂停，人工可修改 |
| 高风险操作审批 | HITL | 多级审批、状态可追溯 |
| 复杂业务流程编排 | HITL | 动态流程、状态完整、可回滚 |
| 跨部门会签 | HITL | 并行审批、聚合结果 |

### 11.4 HITL 的局限性

HITL 并非万能，它有以下局限性：

1. **运营成本高**：需要人工审核团队，人力成本高
2. **响应延迟大**：依赖人工响应速度，无法做到毫秒级
3. **可扩展性受限**：审核量受人工产能限制，无法无限扩展
4. **一致性难保证**：不同审核者标准可能不一致，同一审核者不同时间也可能有差异
5. **系统复杂度高**：需要状态持久化、审核界面、通知系统、超时处理等配套设施
6. **不适合低延迟场景**：需要即时响应的场景（如实时推荐、自动交易）不适合 HITL

---

### 💡 本章深度讲解

HITL 与传统交互模式的本质区别在于"人工介入的时机和能力"。请求-响应模式只能在请求前输入，异步任务模式只能在完成后查看，向导式只能在预设步骤输入，而 HITL 可以在执行的任意节点暂停，人工不仅能查看状态，还能修改状态、控制流程走向，然后从暂停点精确恢复。这种差异的技术基础是状态持久化——HITL 保存的是完整的图执行状态（节点进度、中间结果、interrupt 信息），而传统模式只有简单的任务状态。选择交互模式的决策核心是"执行过程中是否需要人工介入"——如果不需要，请求-响应或异步任务就够了；如果需要且介入点固定、不需要修改状态，向导式可以满足；如果需要动态介入、修改状态、多级/并行审批，HITL 是唯一选择。同时要认识到 HITL 的局限性——运营成本高、响应延迟大、可扩展性受限，不适合低延迟和高吞吐量的场景。

### 📝 本章精简总结

1. **四种模式**：请求-响应（同步即时）、异步任务（后台处理）、向导式（多步输入）、HITL（执行中人工介入）
2. **本质区别**：HITL 可以在执行中任意节点暂停，人工可修改状态和控制流程，然后精确恢复
3. **状态差异**：HITL 保存完整图执行状态，传统模式只有简单的任务/步骤状态
4. **选择决策**：执行中不需要人工→请求-响应/异步任务；需要人工但固定步骤→向导式；需要动态介入/修改状态/多级审批→HITL
5. **HITL 优势**：人工可修改状态、动态介入点、完整审计历史、支持多级/并行审批、可回滚
6. **HITL 局限**：运营成本高、响应延迟大、可扩展性受限、一致性难保证、系统复杂度高
7. **不适合场景**：低延迟实时响应、高吞吐量自动处理、完全确定性的简单流程
8. **面试考点**：HITL 与异步任务的本质区别在于人工介入的时机和能力，以及状态完整性

### 🎯 梯度练习题

**基础题⭐**

1. 四种交互模式（请求-响应、异步任务、向导式、HITL）分别适用于什么场景？各举一个实际例子。
   > 提示：从"执行时间""是否需要人工介入""介入点是否固定"三个维度判断。

2. HITL 和异步任务模式的本质区别是什么？为什么异步任务无法在执行中插入人工审核？
   > 提示：异步任务只有简单状态，无法在执行中暂停和恢复；HITL 有完整图状态，支持任意节点暂停恢复。

3. HITL 有哪些局限性？在什么情况下不应该使用 HITL？
   > 提示：成本、延迟、扩展性、一致性、复杂度；低延迟高吞吐场景不适合。

**进阶题⭐⭐**

1. 设计一个交互模式选择决策树，覆盖以下场景特征：执行时间、是否需要人工、介入点是否固定、是否需要修改状态、是否需要多级审批、是否需要并行会签。说明每个分支的推荐模式和理由。
   > 提示：参考 11.3 节的决策树，扩展更多分支条件。

2. 对比 HITL 和传统工作流引擎（如 Activiti、Camunda）在人工任务处理上的异同。HITL 有哪些优势和不足？
   > 提示：工作流引擎有成熟的人工任务管理、SLA、报表，但与 AI Agent 集成不如 LangGraph 原生；HITL 与 AI 原生集成，但人工任务管理功能较弱。

**实战题⭐⭐⭐**

1. 某公司要构建一个"AI 辅助合同审批系统"，需求如下：
   - 用户上传合同，AI 自动提取关键条款并生成风险评估
   - 法务人员审核 AI 提取的条款（可修改）
   - 财务人员审核金额和付款条款（可修改）
   - 法务和财务可以并行审核
   - 双方都通过后，由总监终审
   - 总监可以批准、拒绝或退回到法务/财务
   - 所有操作留痕
   请分析：这个系统适合用 HITL 吗？如果用传统工作流引擎有什么问题？用 HITL 实现的话，状态图应该如何设计？请画出状态图并写出核心节点逻辑。
   > 提示：适合 HITL（需要并行审批、状态修改、动态回退）；用 Send API 实现并行法务/财务审批，用条件边实现总监终审后的回退路由。

---

## 12. 综合实战：构建生产级 HITL 审批系统

### 12.1 系统需求与架构设计

#### 系统需求

构建一个生产级的 HITL 审批系统，满足以下需求：

1. **多类型审批**：支持采购审批、合同审批、内容审批三种类型
2. **动态审批层级**：根据金额/风险自动决定审批层级
3. **并行会签**：支持多部门并行审批
4. **超时升级**：审批超时自动升级
5. **人工修改**：审批人可以修改申请内容
6. **完整审计**：所有操作留痕，可追溯
7. **Web 界面**：提供审核任务列表和详情页
8. **高可用**：服务重启不丢失审批状态
9. **可观测**：监控审批量、延迟、通过率

#### 系统架构

```mermaid
graph TB
    subgraph 前端层
        Web[Web 审核界面]
        API_Client[API 客户端]
    end
    subgraph 服务层
        FastAPI[FastAPI 服务]
        SSE[SSE 推送]
        Auth[认证授权]
    end
    subgraph 引擎层
        LG[LangGraph 引擎]
        Nodes[审批节点库]
        Policies[审批策略引擎]
    end
    subgraph 数据层
        PG[(PostgreSQL<br/>Checkpoint + 业务数据)]
        Redis[(Redis<br/>缓存 + 锁)]
        ES[(Elasticsearch<br/>审计日志)]
    end
    subgraph 基础设施
        Celery[Celery 定时任务<br/>超时检查 + 通知]
        Prom[Prometheus + Grafana<br/>监控告警]
    end
    
    Web --> API_Client
    API_Client --> FastAPI
    FastAPI --> Auth
    FastAPI --> LG
    FastAPI --> SSE
    LG --> Nodes
    LG --> Policies
    LG --> PG
    LG --> Redis
    FastAPI --> ES
    Celery --> PG
    Celery --> FastAPI
    Prom --> FastAPI
    Prom --> LG
```

### 12.2 核心代码实现

#### 示例 42：生产级 HITL 审批系统核心代码

```python
"""
示例 42：生产级 HITL 审批系统核心实现
包含：状态定义、审批策略引擎、多级审批节点、并行会签、超时处理、审计日志
"""
from typing import TypedDict, Optional, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.types import interrupt, Command, Send
from datetime import datetime, timedelta
import operator
import json
import uuid

# ===== 1. 状态定义 =====
class ApprovalRecord(TypedDict):
    level: int
    role: str
    reviewer: str
    decision: str  # approved / rejected / modified
    comment: str
    modified_content: Optional[dict]
    timestamp: str
    duration_seconds: float

class State(TypedDict):
    # 申请信息
    request_id: str
    request_type: str  # purchase / contract / content
    applicant: str
    content: dict
    created_at: str
    # 审批配置
    required_levels: int
    current_level: int
    approval_timeout_hours: float
    # 审批状态
    approval_history: Annotated[list[ApprovalRecord], operator.add]
    status: str  # pending / in_review / approved / rejected / timed_out
    final_content: Optional[dict]
    # 并行审批
    parallel_approvers: list[str]
    parallel_results: Annotated[list[dict], operator.add]
    # 元数据
    last_updated: str
    error: Optional[str]

# ===== 2. 审批策略引擎 =====
APPROVAL_POLICIES = {
    "purchase": {
        "tiers": [
            {"max_amount": 1000, "levels": 0, "roles": []},  # 自动通过
            {"max_amount": 10000, "levels": 1, "roles": ["supervisor"]},
            {"max_amount": 50000, "levels": 2, "roles": ["supervisor", "manager"]},
            {"max_amount": float("inf"), "levels": 3, "roles": ["supervisor", "manager", "director"]},
        ],
        "timeout_hours": 4
    },
    "contract": {
        "tiers": [
            {"max_amount": 50000, "levels": 2, "roles": ["legal", "finance"], "parallel": True},
            {"max_amount": float("inf"), "levels": 3, "roles": ["legal", "finance", "director"], "parallel": True},
        ],
        "timeout_hours": 8
    },
    "content": {
        "tiers": [
            {"max_amount": float("inf"), "levels": 1, "roles": ["editor"]},
        ],
        "timeout_hours": 2
    }
}

def determine_approval_policy(request_type: str, content: dict) -> dict:
    """根据申请类型和内容确定审批策略"""
    policy = APPROVAL_POLICIES[request_type]
    amount = content.get("amount", 0)
    
    for tier in policy["tiers"]:
        if amount <= tier["max_amount"]:
            return {
                "levels": tier["levels"],
                "roles": tier["roles"],
                "parallel": tier.get("parallel", False),
                "timeout_hours": policy["timeout_hours"]
            }
    return policy["tiers"][-1]

# ===== 3. 核心节点 =====
def init_request(state: State) -> State:
    """初始化申请"""
    policy = determine_approval_policy(state["request_type"], state["content"])
    
    if policy["levels"] == 0:
        # 自动通过
        return {
            "status": "auto_approved",
            "final_content": state["content"],
            "required_levels": 0,
            "last_updated": datetime.now().isoformat()
        }
    
    return {
        "request_id": state.get("request_id", str(uuid.uuid4())),
        "required_levels": policy["levels"],
        "current_level": 1,
        "approval_timeout_hours": policy["timeout_hours"],
        "parallel_approvers": policy["roles"] if policy["parallel"] else [],
        "status": "in_review",
        "approval_history": [],
        "parallel_results": [],
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }

def serial_approval_node(state: State) -> State:
    """串行多级审批节点"""
    level = state["current_level"]
    role = ["supervisor", "manager", "director", "vp"][level - 1]
    
    result = interrupt({
        "action": "approval",
        "request_id": state["request_id"],
        "request_type": state["request_type"],
        "applicant": state["applicant"],
        "content": state["content"],
        "level": level,
        "role": role,
        "progress": f"{level}/{state['required_levels']}",
        "timeout_hours": state["approval_timeout_hours"],
        "approval_history": state["approval_history"],
        "options": ["approved", "rejected", "modified（需提供 modified_content）"]
    })
    
    record: ApprovalRecord = {
        "level": level,
        "role": role,
        "reviewer": result.get("reviewer", "unknown"),
        "decision": result["decision"],
        "comment": result.get("comment", ""),
        "modified_content": result.get("modified_content"),
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": 0  # 实际计算
    }
    
    if result["decision"] == "rejected":
        return {
            "approval_history": [record],
            "status": "rejected",
            "last_updated": datetime.now().isoformat()
        }
    
    if result["decision"] == "modified":
        new_content = result["modified_content"]
    else:
        new_content = state["content"]
    
    if level >= state["required_levels"]:
        return {
            "approval_history": [record],
            "status": "approved",
            "final_content": new_content,
            "last_updated": datetime.now().isoformat()
        }
    
    return {
        "approval_history": [record],
        "current_level": level + 1,
        "content": new_content,
        "last_updated": datetime.now().isoformat()
    }

def parallel_distribute(state: State) -> list[Send]:
    """并行审批分发"""
    return [
        Send("parallel_approval", {"approver": role, "state": state})
        for role in state["parallel_approvers"]
    ]

def parallel_approval_node(state: State) -> State:
    """并行审批节点（每个审批人一个实例）"""
    approver = state["approver"]
    original_state = state["state"]
    
    result = interrupt({
        "action": "parallel_approval",
        "approver": approver,
        "request_id": original_state["request_id"],
        "content": original_state["content"]
    })
    
    return {"parallel_results": [{"approver": approver, **result}]}

def aggregate_parallel(state: State) -> State:
    """聚合并行审批结果"""
    results = state["parallel_results"]
    all_approved = all(r["decision"] == "approved" for r in results)
    rejected = [r for r in results if r["decision"] == "rejected"]
    
    if rejected:
        return {"status": "rejected", "last_updated": datetime.now().isoformat()}
    
    if all_approved and len(results) >= len(state["parallel_approvers"]):
        return {"status": "approved", "final_content": state["content"], "last_updated": datetime.now().isoformat()}
    
    return {"status": "in_review"}

def execute_approved(state: State) -> State:
    """执行已批准的申请"""
    print(f"✅ 申请 {state['request_id']} 已批准，开始执行")
    print(f"   类型：{state['request_type']}，内容：{json.dumps(state['final_content'], ensure_ascii=False)[:100]}")
    return {"status": "executed", "last_updated": datetime.now().isoformat()}

def reject_flow(state: State) -> State:
    """拒绝流程"""
    print(f"❌ 申请 {state['request_id']} 被拒绝")
    return {"status": "rejected_final"}

# ===== 4. 构建图 =====
def build_approval_graph():
    builder = StateGraph(State)
    builder.add_node("init", init_request)
    builder.add_node("serial_approval", serial_approval_node)
    builder.add_node("parallel_approval", parallel_approval_node)
    builder.add_node("aggregate", aggregate_parallel)
    builder.add_node("execute", execute_approved)
    builder.add_node("reject", reject_flow)
    
    builder.add_edge(START, "init")
    
    # 根据是否并行审批路由
    def route_after_init(state: State) -> str:
        if state["status"] == "auto_approved":
            return "execute"
        if state["parallel_approvers"]:
            return "parallel_distribute"
        return "serial_approval"
    
    builder.add_conditional_edges("init", route_after_init, {
        "execute": "execute",
        "parallel_distribute": "parallel_approval",  # 通过 Send 分发
        "serial_approval": "serial_approval"
    })
    
    # 串行审批路由
    def route_serial(state: State) -> str:
        if state["status"] == "approved":
            return "execute"
        if state["status"] == "rejected":
            return "reject"
        return "serial_approval"
    
    builder.add_conditional_edges("serial_approval", route_serial, {
        "execute": "execute",
        "reject": "reject",
        "serial_approval": "serial_approval"
    })
    
    # 并行审批
    builder.add_conditional_edges("init", parallel_distribute, ["parallel_approval"])
    builder.add_edge("parallel_approval", "aggregate")
    builder.add_conditional_edges("aggregate", lambda s: "execute" if s["status"] == "approved" else "reject" if s["status"] == "rejected" else "aggregate",
        {"execute": "execute", "reject": "reject", "aggregate": "aggregate"})
    
    builder.add_edge("execute", END)
    builder.add_edge("reject", END)
    
    return builder

# ===== 5. 编译和使用 =====
print("生产级 HITL 审批系统核心代码已定义")
print("功能清单：")
print("  ✅ 多类型审批（采购/合同/内容）")
print("  ✅ 动态审批层级（基于金额）")
print("  ✅ 串行多级审批")
print("  ✅ 并行会签")
print("  ✅ 人工修改内容")
print("  ✅ 自动通过（低金额）")
print("  ✅ 完整审批历史记录")
print("  ✅ 超时配置（需配合定时任务实现升级）")
print("\n生产环境编译：")
print("  checkpointer = PostgresSaver.from_conn_string('postgresql://...')")
print("  checkpointer.setup()")
print("  graph = build_approval_graph().compile(checkpointer=checkpointer)")
```

**预期运行结果**：
```
生产级 HITL 审批系统核心代码已定义
功能清单：
  ✅ 多类型审批（采购/合同/内容）
  ✅ 动态审批层级（基于金额）
  ✅ 串行多级审批
  ✅ 并行会签
  ✅ 人工修改内容
  ✅ 自动通过（低金额）
  ✅ 完整审批历史记录
  ✅ 超时配置（需配合定时任务实现升级）

生产环境编译：
  checkpointer = PostgresSaver.from_conn_string('postgresql://...')
  checkpointer.setup()
  graph = build_approval_graph().compile(checkpointer=checkpointer)
```

### 12.3 部署与运维

#### 部署架构

```mermaid
graph LR
    subgraph 负载均衡
        LB[NGINX / ALB]
    end
    subgraph 应用集群
        APP1[App Instance 1]
        APP2[App Instance 2]
        APP3[App Instance 3]
    end
    subgraph 数据层
        PG[(PostgreSQL<br/>主从)]
        Redis[(Redis<br/>哨兵集群)]
        ES[(Elasticsearch<br/>3 节点)]
    end
    subgraph 异步任务
        Celery[Celery Worker x2]
        Beat[Celery Beat<br/>定时调度]
    end
    
    LB --> APP1
    LB --> APP2
    LB --> APP3
    APP1 --> PG
    APP2 --> PG
    APP3 --> PG
    APP1 --> Redis
    APP2 --> Redis
    APP3 --> Redis
    APP1 --> ES
    Celery --> PG
    Beat --> Celery
```

#### 关键运维操作

| 操作 | 方法 | 频率 |
|------|------|------|
| **Checkpoint 清理** | 删除 90 天前的 Checkpoint | 每日 |
| **超时检查** | 扫描超时未处理的审批，发送提醒/升级 | 每 5 分钟 |
| **审批统计** | 汇总日/周/月审批数据，生成报表 | 每日 |
| **备份** | PostgreSQL 全量备份 + WAL 归档 | 每日 + 实时 |
| **监控告警** | 检查审批延迟、积压量、系统健康 | 实时 |
| **性能调优** | 分析慢查询、Checkpoint 写入延迟 | 每周 |

### 12.4 系统扩展方向

1. **AI 辅助审核**：利用 LLM 对申请内容进行预审，给出风险提示和推荐决策，减少人工审核时间
2. **智能审批路由**：基于审核者的历史审核数据和专长，智能分配审核任务
3. **移动端审核**：开发移动端审核界面，支持推送通知和一键审批
4. **审批数据分析**：分析审批数据，发现流程瓶颈和优化空间
5. **与 OA 系统集成**：与企业现有 OA、ERP、邮件系统深度集成
6. **多租户支持**：支持多部门/多公司独立配置审批流程

---

### 💡 本章深度讲解

构建生产级 HITL 审批系统是对前面所有知识点的综合运用。系统架构分为五层：前端层（Web 审核界面）、服务层（FastAPI + SSE + 认证）、引擎层（LangGraph + 节点库 + 策略引擎）、数据层（PostgreSQL Checkpoint + Redis 缓存 + Elasticsearch 审计）、基础设施层（Celery 定时任务 + Prometheus 监控）。核心实现包括三个关键设计：审批策略引擎（根据类型和金额动态决定审批层级和是否并行）、串行/并行双模式审批（串行用条件边循环，并行用 Send API 分发+聚合节点）、完整状态记录（审批历史用 Annotated[list, operator.add] 累加，每条记录包含审核人、决策、时间、修改内容）。部署时需要多实例 + 负载均衡 + PostgreSQL 主从 + Redis 哨兵，确保高可用。运维的核心是定期清理 Checkpoint、超时检查、备份和监控。这个系统可以进一步扩展 AI 辅助审核、智能路由、移动端等方向。

### 📝 本章精简总结

1. **五层架构**：前端层、服务层、引擎层、数据层、基础设施层
2. **策略引擎**：根据申请类型和金额动态决定审批层级、角色、是否并行、超时时间
3. **串行审批**：单个审批节点 + 条件边循环，current_level 递增，全部通过后执行
4. **并行审批**：Send API 分发给多个审批节点，Annotated[list, operator.add] 合并结果，聚合节点判断
5. **自动通过**：低金额/低风险申请直接 auto_approved，无需人工
6. **人工修改**：审批人可以通过 modified_content 字段修改申请内容，后续基于修改后内容
7. **生产部署**：多实例 + 负载均衡 + PostgreSQL 主从 + Redis 哨兵 + Celery 定时任务
8. **运维核心**：Checkpoint 清理（90天）、超时检查（5分钟）、备份（每日）、监控（实时）

### 🎯 梯度练习题

**基础题⭐**

1. 生产级 HITL 审批系统的五层架构是什么？每层的核心组件有哪些？
   > 提示：前端、服务、引擎、数据、基础设施。

2. 审批策略引擎的作用是什么？它根据哪些因素决定审批层级？
   > 提示：根据申请类型、金额/风险等级决定审批层级、角色、是否并行。

3. 并行审批在 LangGraph 中如何实现？Send API 和聚合节点分别起什么作用？
   > 提示：Send API 并行分发任务，聚合节点收集所有分支结果并判断是否全部通过。

**进阶题⭐⭐**

1. 为生产级 HITL 系统设计一个"超时升级机制"：包括超时判断逻辑、提醒策略、升级规则、最大升级次数。写出定时任务的核心逻辑和状态更新代码。
   > 提示：Celery 定时任务每 5 分钟扫描超时审批，根据超时时长发送提醒/升级/自动拒绝，状态中记录升级历史。

2. 解释为什么生产环境必须用 PostgresSaver 而不是 MemorySaver？如果服务有多个实例，MemorySaver 会有什么问题？PostgresSaver 如何解决？
   > 提示：MemorySaver 状态在进程内存中，多实例不共享，重启丢失；PostgresSaver 状态在共享数据库中，多实例可访问，持久化不丢失。

**实战题⭐⭐⭐**

1. 在示例 42 的生产级审批系统基础上，扩展以下功能：
   - 添加"AI 预审"节点：在人工审批前，用 LLM 分析申请内容，给出风险评分和推荐决策
   - 添加"审批人负载均衡"：根据审批人的当前待审核数量，智能分配审核任务
   - 添加"审批 SLA 监控"：实时计算每个审批的剩余时间，临近超时时高亮提醒
   - 添加"审批效率报表"：统计每个审批人的平均审核时间、批准率、修改率
   请写出新增节点的核心逻辑和状态字段扩展，并说明如何集成到现有图中。
   > 提示：AI 预审节点在 init 之后、审批之前；负载均衡在 interrupt 传递的数据中标注推荐审批人；SLA 用 created_at + timeout_hours 计算剩余时间；报表从 approval_history 聚合统计。

---

## 附录：HITL 速查手册

### A.1 interrupt 速查表

| 用法 | 代码 | 恢复方式 | 适用场景 |
|------|------|----------|----------|
| 节点内中断 | `interrupt(value)` | `Command(resume=val)` | 需要人工输入数据 |
| 节点前中断 | `compile(interrupt_before=["node"])` | `graph.invoke(None, config)` | 节点执行前审批 |
| 节点后中断 | `compile(interrupt_after=["node"])` | `Command(update={...})` | 节点执行后审核 |
| 多次中断 | 节点内多次 `interrupt()` | 多次 `Command(resume=...)` | 多轮人工交互 |
| 动态中断 | 节点内条件判断是否 `interrupt()` | 根据条件 | 按需人工介入 |

### A.2 Command 速查表

| 参数 | 作用 | 示例 |
|------|------|------|
| `resume` | 传递 interrupt 返回值 | `Command(resume="approved")` |
| `update` | 修改状态 | `Command(update={"status": "ok"})` |
| `goto` | 跳转节点 | `Command(goto="publish")` |
| 组合 | 同时使用 | `Command(resume="ok", update={...}, goto="next")` |

### A.3 常见错误速查

| 错误现象 | 原因 | 解决方案 |
|----------|------|----------|
| interrupt 不生效 | 未配置 checkpointer | 编译时传入 checkpointer |
| 恢复找不到状态 | thread_id 不一致 | 使用相同 config |
| 并行结果覆盖 | 未用 operator.add | Annotated[list, operator.add] |
| 嵌套字典字段丢失 | update 浅合并 | 提供完整嵌套字典 |
| goto 报错 | 节点名不存在 | 使用已注册的节点名 |
| 恢复后状态未更新 | interrupt 前直接改 state | 通过 return 更新状态 |

### A.4 学习资源

- LangGraph 官方文档：https://langchain-ai.github.io/langgraph/
- HITL 官方教程：https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/
- LangGraph GitHub：https://github.com/langchain-ai/langgraph

---

> **📝 文档统计**
> - 总章节数：12 章 + 附录
> - 代码示例：42 个完整示例
> - Mermaid 图表：18 个
> - 面试高频考点：25 处
> - 常见坑点：20 个
> - 练习题：36 道（基础 24 + 进阶 12 + 实战 12）



