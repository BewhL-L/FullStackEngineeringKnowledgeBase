---
title: AI Agent 开发框架知识点系统梳理
tags: [AI与效率工具, AIAgent, 开发框架, LangChain, LlamaIndex, AutoGen, CrewAI, Dify, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# AI Agent 开发框架知识点系统梳理（优化版）

> **文档说明**：系统梳理主流 AI Agent 开发框架，涵盖 LangChain、LlamaIndex、AutoGen、CrewAI、LangGraph、Dify 等框架的核心概念、架构、适用场景与选型对比。

---

## 1. 概述

AI Agent 开发框架封装了 LLM 调用、工具集成、记忆管理、Agent 循环等底层逻辑，让开发者专注于业务逻辑。框架分为代码框架（LangChain 等）和低代码平台（Dify 等）。

**框架分类**：
- **通用编排框架**：LangChain、LlamaIndex
- **Agent 专用框架**：LangGraph、AutoGen、CrewAI
- **低代码平台**：Dify、Coze（扣子）
- **企业级平台**：LangSmith、Weights & Biases

---

## 2. LangChain

### 2.1 定位

最流行的 LLM 应用开发框架，提供链式调用、Agent、工具、记忆、RAG 等完整组件。

### 2.2 核心概念

| 组件 | 说明 |
|------|------|
| **LLM / Chat Model** | 大模型调用封装（OpenAI、Anthropic、本地模型） |
| **Prompt Template** | 提示词模板，支持变量注入 |
| **Chain** | 链式组合多个步骤 |
| **Agent** | 自主决策+工具调用 |
| **Tool** | 工具封装（搜索、代码、API） |
| **Memory** | 对话记忆管理 |
| **Retriever** | 文档检索（RAG） |
| **Document Loader** | 文档加载（PDF、网页、数据库） |
| **Text Splitter** | 文档切分 |
| **Embedding** | 向量化 |
| **Vector Store** | 向量数据库 |

### 2.3 基本用法

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# LCEL（LangChain Expression Language）链式调用
prompt = ChatPromptTemplate.from_template("用中文解释{topic}，适合初学者")
model = ChatOpenAI(model="gpt-4o")
chain = prompt | model | StrOutputParser()

result = chain.invoke({"topic": "Transformer注意力机制"})
```

### 2.4 Agent 示例

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气"""
    return f"{city}今天晴，25度"

tools = [get_weather]
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是有用的助手，可以使用工具"),
    ("human", "{input}"),
    ("agent_scratchpad", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(model, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
result = executor.invoke({"input": "北京今天天气怎么样？"})
```

> 🔍 **知识点深度解析**
>
> **作用**：LangChain 是 LLM 应用开发的事实标准，理解其核心抽象是开发 AI 应用的基础。
>
> **原理**：LangChain 将 LLM 应用抽象为可组合的组件。LCEL（LangChain Expression Language）用管道符 `|` 组合组件（prompt | model | parser），底层是 `Runnable` 接口，支持流式、批处理、异步、重试、回退等。Agent 通过 `AgentExecutor` 实现 ReAct 循环：LLM 决定调用工具 → 执行工具 → 结果返回 LLM → 循环直到完成。Tool 用 `@tool` 装饰器将 Python 函数转为 LLM 可调用的工具，函数名、文档字符串、参数类型注解会被解析为工具描述。Memory 管理对话历史，支持多种记忆类型（Buffer、Summary、Vector）。
>
> **用法要点**：① 简单链式调用用 LCEL，复杂 Agent 用 AgentExecutor；② 工具的 docstring 很重要，是 LLM 理解工具的依据；③ 生产环境用 LangSmith 做追踪和评估；④ 面试常考：LangChain 核心组件、LCEL、Agent 原理、Tool 定义、RAG 实现、Memory 类型。

---

## 3. LlamaIndex

### 3.1 定位

专注于 RAG（检索增强生成）的框架，提供强大的文档加载、索引、检索能力。

### 3.2 核心能力

- **数据连接器**：100+ 数据源（PDF、Notion、Slack、数据库）
- **索引类型**：Vector Store Index、Summary Index、Tree Index、Keyword Table
- **检索引擎**：语义检索、关键词检索、混合检索
- **查询引擎**：问答、摘要、子问题分解
- **Agent**：基于 RAG 的 Agent

### 3.3 基本用法

```python
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

# 加载文档
documents = SimpleDirectoryReader("./docs").load_data()

# 构建索引（自动切分、向量化、存储）
index = VectorStoreIndex.from_documents(documents)

# 查询引擎
query_engine = index.as_query_engine()
response = query_engine.query("文档中提到了哪些技术栈？")
```

### 3.4 LangChain vs LlamaIndex

| 维度 | LangChain | LlamaIndex |
|------|-----------|------------|
| 定位 | 通用 LLM 应用框架 | RAG 专精框架 |
| 优势 | 组件丰富、Agent 生态好 | 检索能力强、索引类型多 |
| RAG | 基础支持 | 深度优化 |
| Agent | 成熟 | 较弱 |
| 学习曲线 | 较陡 | 较平缓 |

**最佳实践**：两者可结合使用——LlamaIndex 做 RAG，LangChain 做 Agent 编排。

---

## 4. LangGraph

### 4.1 定位

LangChain 团队推出的 Agent 编排框架，用有向图（StateGraph）定义 Agent 工作流，支持复杂的多 Agent 协作和循环控制。

### 4.2 核心概念

- **StateGraph**：有向状态图，节点是函数，边是流转条件
- **Node**：处理节点（LLM 调用、工具执行、人工审核）
- **Edge**：条件边，根据状态决定下一步
- **State**：共享状态，在节点间传递

### 4.3 适用场景

- 需要精细控制 Agent 流程
- 多 Agent 协作
- 人工介入（Human-in-the-loop）
- 复杂的条件分支和循环

---

## 5. AutoGen

### 5.1 定位

微软推出的多 Agent 对话框架，支持多个 Agent 自主对话协作。

### 5.2 核心概念

- **ConversableAgent**：可对话的 Agent 基类
- **AssistantAgent**：AI 助手，调用 LLM
- **UserProxyAgent**：用户代理，可执行代码、获取人工输入
- **GroupChat**：多 Agent 群聊，自动选择发言者

### 5.3 特点

- 多 Agent 自然对话协作
- 内置代码执行能力
- 支持人工介入
- 灵活的对话模式

---

## 6. CrewAI

### 6.1 定位

角色扮演式多 Agent 框架，每个 Agent 有明确的角色、目标、工具，像团队一样协作。

### 6.2 核心概念

```python
from crewai import Agent, Task, Crew

# 定义 Agent（角色+目标+工具）
researcher = Agent(
    role="研究员",
    goal="收集和分析最新的AI技术信息",
    tools=[search_tool],
    verbose=True
)

writer = Agent(
    role="撰稿人",
    goal="撰写高质量的技术文章",
    tools=[],
    verbose=True
)

# 定义任务
research_task = Task(
    description="研究AI Agent的最新进展",
    agent=researcher,
    expected_output="500字研究摘要"
)

write_task = Task(
    description="基于研究结果撰写文章",
    agent=writer,
    expected_output="1000字文章"
)

# 组建团队
crew = Crew(agents=[researcher, writer], tasks=[research_task, write_task])
result = crew.kickoff()
```

### 6.3 特点

- 角色驱动，直观易懂
- 任务顺序/并行执行
- 内置工具集成
- 适合内容创作、研究分析等场景

---

## 7. Dify（低代码平台）

### 7.1 定位

开源 LLMOps 平台，可视化搭建 AI 应用和 Agent，无需大量编码。

### 7.2 核心功能

- **可视化编排**：拖拽式工作流设计
- **Prompt 工程**：在线调试提示词
- **RAG 知识库**：上传文档，自动构建检索
- **Agent**：工具调用、自主决策
- **模型管理**：支持多家 LLM（OpenAI、Anthropic、国内模型）
- **API 发布**：一键发布为 API
- **监控与日志**：调用追踪、成本统计

### 7.3 适用场景

- 快速搭建 AI 应用原型
- 企业内部 AI 工具
- 非技术人员使用
- 需要可视化管理的场景

---

## 8. 框架选型对比

| 框架 | 类型 | 优势 | 适用场景 |
|------|------|------|----------|
| **LangChain** | 代码框架 | 生态最丰富，组件全 | 通用 LLM 应用、Agent |
| **LlamaIndex** | 代码框架 | RAG 专精，检索强 | 知识库问答、文档分析 |
| **LangGraph** | 代码框架 | 图编排，精细控制 | 复杂 Agent 流程、多 Agent |
| **AutoGen** | 代码框架 | 多 Agent 对话，代码执行 | 研究型多 Agent 协作 |
| **CrewAI** | 代码框架 | 角色驱动，简单直观 | 内容创作、研究团队 |
| **Dify** | 低代码平台 | 可视化，开箱即用 | 快速原型、企业应用 |

**选型建议**：
- 学习/通用开发 → LangChain
- RAG 知识库 → LlamaIndex
- 复杂 Agent 流程 → LangGraph
- 多 Agent 协作 → CrewAI（简单）/ AutoGen（灵活）
- 快速搭建/非技术 → Dify / Coze

---

## 8.1 其他重要框架

| 框架 | 出品方 | 特点 |
|------|--------|------|
| **Semantic Kernel** | 微软 | C#/Python/Java，Planner/Functions/Memory，企业集成强 |
| **BabyAGI** | 开源 | 早期自主Agent，任务分解+优先级队列 |
| **AutoGPT** | 开源 | 自主目标驱动Agent，影响力大但可靠性有限 |
| **SuperAGI** | 开源 | Agent平台，GUI，工具市场 |
| **Coze（扣子）** | 字节跳动 | 国内低代码平台，插件市场丰富 |

### 8.2 LangChain vs LangGraph 深度对比

| 维度 | LangChain（Chain） | LangGraph（Graph） |
|------|---------------------|---------------------|
| 执行模型 | 线性链式 | 有向图，支持循环 |
| 状态管理 | 隐式 | 显式 State 对象 |
| 条件分支 | 有限 | 原生支持 |
| 人工介入 | 困难 | 原生支持 |
| 适用场景 | 简单流水线 | 复杂Agent、多Agent |

**迁移建议**：简单RAG/问答用Chain，需要工具循环/多Agent/人工审核用LangGraph。

### 8.3 生产部署与可观测性

- **LangServe**：LangChain 应用一键部署为 REST API，支持流式输出
- **FastAPI 封装**：自定义部署，灵活控制路由和中间件
- **Docker 容器化**：标准化部署环境
- **可观测性平台**：
  - **LangSmith**：LangChain官方，trace追踪+评估+监控
  - **Langfuse**：开源，trace+成本+评估
  - **Helicone**：LLM调用监控，成本分析

### 8.4 模型路由与降级

- **多模型切换**：根据任务复杂度选择不同模型
- **Fallback 机制**：主模型失败自动切换备用模型
- **成本路由**：简单任务用便宜模型，复杂任务用强模型
- **速率限制处理**：429错误自动退避重试

---

## 9. 面试高频考点

1. **LangChain 核心组件**：LLM、Prompt、Chain、Agent、Tool、Memory
2. **LCEL**：管道符组合、Runnable 接口
3. **Agent 原理**：ReAct 循环、工具调用、AgentExecutor
4. **RAG 实现**：文档加载→切分→向量化→存储→检索→生成
5. **LangChain vs LlamaIndex**：定位和优势区别
6. **LangGraph**：有向图编排、State、Node、Edge
7. **CrewAI**：角色驱动、Agent/Task/Crew
8. **AutoGen**：多 Agent 对话、GroupChat
9. **Dify**：低代码平台、可视化编排
10. **框架选型**：根据场景选择合适框架
11. **Semantic Kernel**：微软企业级框架，Planner/Functions/Memory
12. **LangChain vs LangGraph**：线性Chain vs 有状态Graph，循环/人工介入
13. **生产部署**：LangServe/FastAPI/Docker，流式输出
14. **可观测性**：LangSmith/Langfuse/Helicone，trace追踪+成本监控
15. **模型路由与降级**：多模型切换、Fallback、成本路由、速率限制处理

---

## 📝 精简总结

- LangChain：通用 LLM 应用框架，LCEL 链式调用，Agent/Tool/Memory/RAG 全组件
- LlamaIndex：RAG 专精框架，文档加载/索引/检索能力强
- LangGraph：有向图编排 Agent，支持循环/条件分支/人工介入，适合复杂流程
- LangChain vs LangGraph：Chain线性简单，Graph有状态支持循环和多Agent
- AutoGen：微软多 Agent 对话框架，内置代码执行，GroupChat群聊
- CrewAI：角色驱动多 Agent，Agent/Task/Crew 三层抽象，简单直观
- Semantic Kernel：微软企业级，C#/Python/Java，Planner/Functions/Memory
- Dify：开源低代码 LLMOps 平台，可视化搭建 AI 应用；Coze国内低代码平台
- BabyAGI/AutoGPT：早期自主Agent，任务分解+优先级，影响力大但可靠性有限
- 生产部署：LangServe一键API、FastAPI自定义、Docker容器化、流式输出SSE
- 可观测性：LangSmith（官方）、Langfuse（开源）、Helicone，trace+成本+评估
- 模型路由：多模型切换、Fallback降级、成本路由、速率限制退避重试
- 选型：通用→LangChain，RAG→LlamaIndex，复杂Agent→LangGraph，多Agent→CrewAI，低代码→Dify
- 最佳实践：框架可组合使用（LlamaIndex做RAG + LangChain做Agent）

---

[[09-AI与效率工具/MOC-AI与效率工具|← 返回 AI 与效率工具 MOC]] | [[Home|🏠 返回首页]]
