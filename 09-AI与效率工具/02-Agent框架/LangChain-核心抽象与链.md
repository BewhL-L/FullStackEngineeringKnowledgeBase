---
title: LangChain 核心抽象与链
tags: [AI应用, AI工程化, Agent, LLM, 核心]
category: AI与效率工具
created: 2026-08-13
updated: 2026-09-09
difficulty: ⭐⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[LLM大模型入门概念]]", "[[Prompt工程进阶]]"]
aliases: [LangChain, LangChain核心抽象, LCEL, LangChain表达式语言]
---

# LangChain 核心抽象与链

> **📖 文档说明**
>
> 本文档是「从零基础新手到实战老手」三部曲的**完整体系**，覆盖入门篇、进阶篇、实战篇三个层次。我们将从"LangChain 是什么"开始，一步步深入核心抽象、LCEL 表达式语言、Runnable 接口、Chain 组合、记忆系统、回调机制，最终到 RAG 实战、Agent 构建和生产部署。每个知识点都配有通俗解释、原理图解、可直接运行的代码示例、最佳实践和常见坑点。
>
> **👥 适用人群**
> - 完全没有 LLM 应用开发经验的纯新手
> - 用过 OpenAI API 但想系统化学习 LangChain 的开发者
> - 学过一点 LangChain 但对 LCEL/Runnable 理解不深的同学
> - 需要构建生产级 RAG/Agent 应用的全栈工程师
>
> **📚 前置知识**
> - Python 基础语法（函数、类、装饰器、类型注解）
> - LLM 基本概念（Token、Temperature、System Prompt）
> - HTTP API 基本调用方式
>
> **🗺️ 学习路径提示**
> - 入门篇（第1-3章）：建立整体认知，掌握核心抽象和 LCEL 基础
> - 进阶篇（第4-6章）：深入 Runnable 组合、Chain 类型、记忆与回调
> - 实战篇（第7-10章）：RAG 完整实战、Agent 构建、生产部署、最佳实践
> - 每章末尾的「梯度练习题」务必尝试完成，代码是练出来的

---

## 一、入门篇：LangChain 概述与环境搭建

### 1.1 LangChain 是什么

#### 概念解释

**正式定义**：LangChain 是一个开源的 LLM（大语言模型）应用开发框架，通过标准化的核心抽象（Model、Prompt Template、Output Parser、Retriever、Tool、Memory、Chain）和表达式语言（LCEL），简化 LLM 应用的开发、组合和部署。

**生活化比喻**：如果把 LLM 比作一台超级发动机，那么 LangChain 就是整车制造平台——它提供了方向盘（Prompt Template）、变速箱（Chain）、仪表盘（Callback）、油箱（Memory）、导航系统（Retriever）等标准化零部件，你不需要从零造车，只需要选择合适的零部件组装即可。

**核心价值**：将 LLM 应用开发中的常见模式抽象为可组合的组件，通过链式调用快速构建从简单问答到复杂 Agent 的各种应用，同时提供 100+ 模型提供商、50+ 向量数据库、100+ 工具的丰富集成生态。

#### 原理说明

LangChain 的核心设计哲学是"**组合优于继承**"（Composition over Inheritance）。在传统面向对象编程中，我们通过继承基类来扩展功能；而在 LangChain 中，每个组件都是独立的、实现了统一接口（Runnable）的对象，组件之间通过 `|` 运算符组合成链。

```mermaid
graph TB
    subgraph LangChain 三层架构
        A[应用层<br/>Chain / Agent / LCEL 管道]
        B[组件层<br/>Model / Prompt / Parser / Retriever / Tool / Memory]
        C[基础层<br/>Runnable 协议 / Callback 系统]
    end

    C --> B
    B --> A

    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e9
```

**为什么这样设计**：
1. **可替换性**：每个组件可以独立替换——换模型只需要换 Model 组件，换输出格式只需要换 Output Parser
2. **可测试性**：每个组件可以独立测试，不需要启动整个应用
3. **可组合性**：组件可以任意组合，链本身也是组件，可以继续组合
4. **统一执行接口**：所有组件都支持 invoke/stream/batch/async，构建的链天然支持这些模式

**技术对比**：

| 维度 | 直接调用 LLM API | LangChain |
|------|-------------------|-----------|
| 代码复用 | 每个应用重写胶水代码 | 标准化组件可复用 |
| 模型切换 | 需要修改调用代码 | 替换 Model 组件即可 |
| 流式输出 | 手动处理 SSE | 链自动支持 .stream() |
| 异步调用 | 手动编写 async 代码 | 链自动支持 .ainvoke() |
| 可观测性 | 手动埋点 | Callback 系统自动追踪 |
| 生态集成 | 自行编写适配器 | 100+ 开箱即用集成 |

> 🎯 **面试高频考点**：LangChain 的核心设计哲学是什么？答：组合优于继承（Composition over Inheritance），通过标准化的 Runnable 接口和 `|` 运算符实现组件的自由组合，而非通过继承基类扩展功能。

#### 代码示例

**示例1：基础——最简单的 LangChain 调用**

```python
# 安装：pip install langchain langchain-openai
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# 1. 创建模型实例
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 2. 直接调用（LangChain 的 Model 组件封装了 API 调用）
response = model.invoke([HumanMessage(content="你好，请用一句话介绍 LangChain")])

# 3. 输出结果
print(response.content)
# 预期输出：LangChain 是一个用于构建大语言模型应用的开源框架...
```

**示例2：进阶——使用 Prompt Template + Model + Output Parser**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 1. 创建 Prompt Template（提示词模板）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{role}，请用简洁专业的语言回答问题。"),
    ("human", "{question}")
])

# 2. 创建 Model
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

# 3. 创建 Output Parser
output_parser = StrOutputParser()

# 4. 组合成链（LCEL 表达式语言）
chain = prompt | model | output_parser

# 5. 调用链
result = chain.invoke({
    "role": "技术顾问",
    "question": "什么是 RAG？它解决了什么问题？"
})

print(result)
# 预期输出：RAG（Retrieval-Augmented Generation，检索增强生成）是一种...
```

**示例3：完整场景——带变量注入和格式化的翻译链**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 定义翻译链
translation_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业翻译官。请将以下文本从{source_lang}翻译成{target_lang}。"
               "要求：准确传达原意，保持语气风格，不要添加解释。"),
    ("human", "{text}")
])

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
chain = translation_prompt | model | StrOutputParser()

# 调用：中译英
result_en = chain.invoke({
    "source_lang": "中文",
    "target_lang": "英文",
    "text": "LangChain 是 LLM 应用开发的事实标准框架，通过可组合的抽象简化开发流程。"
})
print("英译结果:", result_en)
# 预期输出：LangChain is the de facto standard framework for LLM application development...

# 调用：英译日
result_ja = chain.invoke({
    "source_lang": "英文",
    "target_lang": "日文",
    "text": "LangChain simplifies LLM application development through composable abstractions."
})
print("日译结果:", result_ja)
# 预期输出：LangChainは、構成可能な抽象化を通じてLLMアプリケーション開発を簡素化します。
```

#### 使用场景与最佳实践

**适用场景**：
- RAG（检索增强生成）问答系统
- 带记忆的多轮对话机器人
- Agent 自主决策与工具调用系统
- 文本摘要、翻译、分类、提取等 NLP 任务
- 多步骤 AI 工作流自动化
- 企业级 AI 应用快速原型和生产部署

**不适用场景**：
- 仅需单次简单 API 调用（直接用 OpenAI SDK 更轻量）
- 对延迟极度敏感且不需要组合的场景（框架有少量开销）
- 非 Python 技术栈（LangChain JS 存在但生态不如 Python 丰富）
- 需要完全自定义底层逻辑且不需要任何抽象的场景

**最佳实践**：
1. **优先使用 LCEL**：新代码一律用 `|` 运算符组合链，避免使用旧版 Chain 类（LLMChain 等）
2. **模型配置外置**：通过环境变量或配置文件管理 API Key 和模型参数，不要硬编码
3. **从简单链开始**：先构建 `prompt | model | parser` 基础链，验证通过后再逐步添加复杂组件
4. **使用类型注解**：为自定义组件和链的输入输出添加类型注解，提升代码可维护性
5. **版本锁定**：在 requirements.txt 中锁定 langchain-core、langchain 等包的版本，避免自动升级导致不兼容

**性能建议**：
- 简单任务使用 `gpt-4o-mini` 等小模型，延迟降低 50%+，成本降低 80%+
- 使用 `temperature=0` 获得确定性输出，适合数据提取、分类等任务
- 批量处理使用 `.batch()` 方法，利用 API 的并发能力
- 长文本任务使用流式输出 `.stream()`，提升用户体验（首字延迟降低 50-80%）

#### 常见坑点

**坑点1：API Key 未配置导致认证失败**
- **错误现象**：调用模型时报 `AuthenticationError: Invalid API key` 或 `openai.APIConnectionError`
- **根本原因**：未设置 `OPENAI_API_KEY` 环境变量，或设置了错误的 Key
- **正确做法**：
  ```python
  import os
  os.environ["OPENAI_API_KEY"] = "your-api-key-here"
  # 或者在创建模型时显式传入
  model = ChatOpenAI(api_key="your-api-key", model="gpt-4o-mini")
  ```
- **预防措施**：使用 `.env` 文件管理密钥，配合 `python-dotenv` 加载；在 CI/CD 中使用环境变量注入

**坑点2：Prompt 变量名与输入字典的 Key 不匹配**
- **错误现象**：调用链时报 `KeyError: 'question'` 或 Prompt 中变量未被替换
- **根本原因**：Prompt Template 中定义的变量名（如 `{question}`）与 invoke 时传入的字典 Key 不一致
- **正确做法**：
  ```python
  # Prompt 中定义了 {question} 变量
  prompt = ChatPromptTemplate.from_template("回答问题：{question}")
  # invoke 时必须传入 question 这个 Key
  chain.invoke({"question": "什么是 LangChain？"})  # ✅ 正确
  chain.invoke({"input": "什么是 LangChain？"})     # ❌ 错误，Key 不匹配
  ```
- **预防措施**：使用 `prompt.input_variables` 查看模板需要哪些变量，确保输入字典包含所有必需 Key

---

### 1.2 LangChain 生态与安装

#### 概念解释

**正式定义**：LangChain 生态是由多个独立包组成的模块化生态系统，包括 langchain-core（核心抽象）、langchain-community（第三方集成）、langchain（高级链与 Agent）、langgraph（多 Agent 编排）、langserve（API 部署）、langsmith（可观测性）等，各包职责清晰、可独立安装使用。

**生活化比喻**：LangChain 生态就像一个工具超市——langchain-core 是基础工具套装（螺丝刀、扳手），langchain-community 是各种品牌的专用配件，langchain 是组合好的工具箱，langgraph 是自动化工作台，langserve 是快递发货系统，langsmith 是质量检测台。你可以按需购买，不需要一次买齐所有东西。

**核心价值**：模块化设计使得开发者可以按需安装，减少依赖体积；核心接口稳定，第三方集成快速迭代；各包之间通过标准化接口协作，既可以单独使用也可以组合使用。

#### 原理说明

```mermaid
graph TB
    subgraph LangChain 生态包关系
        CORE[langchain-core<br/>核心抽象与接口]
        COMM[langchain-community<br/>第三方集成]
        MAIN[langchain<br/>高级链与Agent]
        GRAPH[langgraph<br/>多Agent编排]
        SERVE[langserve<br/>API部署]
        SMITH[langsmith<br/>可观测性]
        TEXT[langchain-text-splitters<br/>文本分割]
    end

    CORE --> COMM
    CORE --> MAIN
    CORE --> GRAPH
    COMM --> MAIN
    MAIN --> GRAPH
    MAIN --> SERVE
    CORE --> SMITH
    CORE --> TEXT

    style CORE fill:#ffeb3b
    style COMM fill:#e3f2fd
    style MAIN fill:#f3e5f5
    style GRAPH fill:#e8f5e9
```

**各包职责说明**：

| 包名 | 职责 | 核心内容 | 安装命令 |
|------|------|---------|---------|
| **langchain-core** | 核心抽象层 | Runnable、Model I/O、Prompt、Output Parser、Callback | `pip install langchain-core` |
| **langchain-community** | 第三方集成 | 100+ 模型、50+ 向量库、100+ 工具集成 | `pip install langchain-community` |
| **langchain** | 主包（高级抽象） | Chain、Agent、Memory、Retrieval 策略 | `pip install langchain` |
| **langchain-text-splitters** | 文本分割 | RecursiveCharacterTextSplitter 等 | `pip install langchain-text-splitters` |
| **langgraph** | 多 Agent 编排 | StateGraph、状态机、Checkpoint、HITL | `pip install langgraph` |
| **langserve** | API 部署 | 将 Chain 部署为 REST API | `pip install langserve` |
| **langsmith** | 可观测性 | 链路追踪、评估、数据集、监控 | `pip install langsmith` |
| **langchain-openai** | OpenAI 集成 | ChatOpenAI、OpenAIEmbeddings | `pip install langchain-openai` |

> 🎯 **面试高频考点**：langchain-core 和 langchain 的区别是什么？答：langchain-core 是核心抽象层，定义了 Runnable、Model I/O、Prompt、Output Parser 等基础接口，不包含具体实现；langchain 是主包，依赖 langchain-core 和 langchain-community，提供 Chain、Agent、Memory 等高级抽象。模块化拆分使得核心接口稳定，高级功能可以独立迭代。

#### 代码示例

**示例1：基础——最小化安装与验证**

```bash
# 最小化安装：只装核心和 OpenAI 集成
pip install langchain-core langchain-openai

# 验证安装
python -c "import langchain_core; print('langchain-core 版本:', langchain_core.__version__)"
# 预期输出：langchain-core 版本: 0.3.x
```

**示例2：进阶——完整开发环境安装**

```bash
# 完整安装：包含核心、主包、OpenAI集成、社区集成、文本分割
pip install langchain langchain-core langchain-community langchain-openai langchain-text-splitters

# 可选：向量数据库
pip install chromadb  # 本地向量数据库

# 可选：可观测性
pip install langsmith

# 使用 requirements.txt 锁定版本
# langchain==0.3.0
# langchain-core==0.3.0
# langchain-community==0.3.0
# langchain-openai==0.2.0
# langchain-text-splitters==0.3.0
```

**示例3：完整场景——使用虚拟环境隔离项目依赖**

```bash
# 1. 创建项目目录
mkdir my-langchain-project
cd my-langchain-project

# 2. 创建虚拟环境（推荐 Python 3.10+）
python -m venv .venv

# 3. 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# 4. 升级 pip
pip install --upgrade pip

# 5. 安装 LangChain 相关包
pip install langchain langchain-openai langchain-community chromadb python-dotenv

# 6. 导出依赖清单
pip freeze > requirements.txt

# 7. 验证环境
python -c "
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
print('✅ LangChain 环境就绪')
print('✅ ChatOpenAI 可用')
print('✅ ChatPromptTemplate 可用')
"
# 预期输出：
# ✅ LangChain 环境就绪
# ✅ ChatOpenAI 可用
# ✅ ChatPromptTemplate 可用
```

#### 使用场景与最佳实践

**适用场景**：
- 新项目启动时按需选择安装包
- 生产环境需要精简依赖体积时只装必要包
- 学习和原型开发时安装完整生态
- CI/CD 流水线中使用 requirements.txt 复现环境

**不适用场景**：
- 非 Python 项目（使用 LangChain JS 或其他语言框架）
- 仅需调用一次 LLM API 的极简脚本（直接用 OpenAI SDK）

**最佳实践**：
1. **按需安装**：生产环境只安装必要的包，避免 `pip install langchain` 拉入大量不必要的依赖
2. **使用虚拟环境**：每个项目使用独立的 venv，避免全局包版本冲突
3. **锁定版本**：使用 `pip freeze > requirements.txt` 锁定所有依赖版本，确保可复现
4. **关注版本兼容**：langchain-core、langchain、langchain-community 之间有版本兼容要求，升级前查看 CHANGELOG
5. **使用国内镜像**：在国内开发时使用清华/阿里 PyPI 镜像加速安装

**性能建议**：
- 使用 `pip install --no-cache-dir` 减少磁盘占用
- 在 Docker 中使用多阶段构建减小镜像体积
- 生产环境只安装运行时依赖，开发依赖（pytest、black 等）单独管理

#### 常见坑点

**坑点1：包版本不兼容导致导入错误**
- **错误现象**：`ImportError: cannot import name 'Runnable' from 'langchain_core.runnables'` 或 `AttributeError: module 'langchain_core' has no attribute '__version__'`
- **根本原因**：langchain-core 版本过旧或与 langchain 主包版本不匹配
- **正确做法**：
  ```bash
  # 查看已安装版本
  pip show langchain-core langchain langchain-community

  # 升级到兼容版本
  pip install --upgrade langchain-core langchain langchain-community

  # 或者使用兼容的版本组合
  pip install langchain==0.3.0 langchain-core==0.3.0 langchain-community==0.3.0
  ```
- **预防措施**：在 requirements.txt 中锁定所有相关包的版本；升级前在测试环境验证

**坑点2：langchain-community 集成包需要额外安装依赖**
- **错误现象**：`ImportError: Could not import chromadb python package. Please install it with pip install chromadb`
- **根本原因**：langchain-community 中的第三方集成为可选依赖，不会自动安装对应的第三方包
- **正确做法**：
  ```bash
  # 使用 Chroma 向量数据库需要额外安装
  pip install chromadb

  # 使用 Tavily 搜索需要额外安装
  pip install tavily-python

  # 使用 Pinecone 需要额外安装
  pip install pinecone-client
  ```
- **预防措施**：阅读集成文档的"Installation"部分，确认需要安装哪些额外依赖；错误信息通常会提示需要安装的包名

---

### 1.3 LangChain 核心抽象全景

#### 概念解释

**正式定义**：LangChain 的核心抽象是一组标准化的接口定义，包括 Chat Model/LLM（模型调用）、Message（消息类型）、Prompt Template（提示词模板）、Output Parser（输出解析器）、Retriever（检索器）、Document（文档）、Tool（工具）、Memory（记忆）、Callback（回调）、Runnable（可运行对象），它们共同构成了 LLM 应用的标准化组件体系。

**生活化比喻**：LangChain 的核心抽象就像乐高积木的标准接口——每块积木都有相同的凸点和凹槽（Runnable 接口），所以可以任意拼接。Model 是发动机积木，Prompt 是方向盘积木，Output Parser 是变速箱积木，Retriever 是导航积木，Tool 是外挂工具箱，Memory 是行车记录仪，Callback 是仪表盘。标准接口让这些积木可以自由组合成各种车辆。

**核心价值**：通过标准化抽象，开发者不需要关心每个组件的内部实现细节，只需要了解输入输出格式即可组合使用；组件可以独立替换、测试和优化；整个生态基于统一接口协作，避免了重复造轮子。

#### 原理说明

```mermaid
graph LR
    subgraph 输入侧
        IN[用户输入]
    end

    subgraph LangChain 核心抽象
        PT[Prompt Template<br/>提示词模板]
        M[Chat Model / LLM<br/>语言模型]
        OP[Output Parser<br/>输出解析器]
        R[Retriever<br/>检索器]
        T[Tool<br/>工具]
        MEM[Memory<br/>记忆]
        CB[Callback<br/>回调]
    end

    subgraph 输出侧
        OUT[结构化输出]
    end

    IN --> PT
    R --> PT
    MEM --> PT
    PT --> M
    T --> M
    M --> OP
    M --> CB
    OP --> OUT

    style PT fill:#e3f2fd
    style M fill:#f3e5f5
    style OP fill:#e8f5e9
    style R fill:#fff3e0
    style T fill:#fce4ec
    style MEM fill:#f3e5f5
```

**核心抽象一览表**：

| 抽象 | 职责 | 核心接口/方法 | 输入 | 输出 |
|------|------|--------------|------|------|
| **Chat Model** | 聊天模型，接收消息列表返回消息 | `invoke(messages) -> AIMessage` | `List[BaseMessage]` | `AIMessage` |
| **LLM** | 文本补全模型，接收字符串返回字符串 | `invoke(text) -> str` | `str` | `str` |
| **Message** | 消息类型，封装角色和内容 | `content`, `role` | - | - |
| **Prompt Template** | 提示词模板，变量注入 | `format(**kwargs) -> PromptValue` | 变量字典 | `PromptValue` |
| **Output Parser** | 输出解析器，文本转结构化数据 | `parse(text) -> Any` | `str` | 结构化对象 |
| **Retriever** | 检索器，查询返回相关文档 | `invoke(query) -> List[Document]` | `str` | `List[Document]` |
| **Document** | 文档，文本+元数据 | `page_content`, `metadata` | - | - |
| **Tool** | 工具，LLM 可调用的外部功能 | `run(**kwargs) -> str` | 参数 | 结果字符串 |
| **Memory** | 记忆，存储和检索对话历史 | `save_context()`, `load_memory_variables()` | 输入输出 | 历史变量 |
| **Callback** | 回调，执行流程钩子 | `on_llm_start()`, `on_llm_end()` | 事件 | - |
| **Runnable** | 可运行对象，所有组件的基类 | `invoke()`, `stream()`, `batch()` | 任意 | 任意 |

> 🎯 **面试高频考点**：LangChain 的六大核心抽象是什么？答：Model I/O（模型输入输出，含 Prompt Template、Chat Model/LLM、Output Parser）、Retrieval（检索，含 Retriever、Document）、Chain（链组合）、Agents（Agent 与 Tool）、Memory（记忆）、Callbacks（回调）。这六大抽象构成了 LangChain 的完整能力体系。

#### 代码示例

**示例1：基础——查看各核心抽象的输入输出类型**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 1. Message 类型
human_msg = HumanMessage(content="你好")
ai_msg = AIMessage(content="你好！有什么可以帮你的？")
system_msg = SystemMessage(content="你是一个友好的助手")

print(f"HumanMessage: role={human_msg.type}, content={human_msg.content}")
print(f"AIMessage: role={ai_msg.type}, content={ai_msg.content}")
print(f"SystemMessage: role={system_msg.type}, content={system_msg.content}")
# 预期输出：
# HumanMessage: role=human, content=你好
# AIMessage: role=ai, content=你好！有什么可以帮你的？
# SystemMessage: role=system, content=你是一个友好的助手

# 2. Prompt Template 的输入输出
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是{role}"),
    ("human", "{question}")
])
prompt_value = prompt.invoke({"role": "程序员", "question": "什么是递归？"})
print(f"Prompt 输出类型: {type(prompt_value)}")
print(f"转换为消息: {prompt_value.to_messages()}")
# 预期输出：Prompt 输出类型: <class 'langchain_core.prompt_values.ChatPromptValue'>

# 3. Output Parser 的输入输出
parser = StrOutputParser()
result = parser.invoke(AIMessage(content="递归是函数调用自身的编程技巧"))
print(f"Parser 输出类型: {type(result)}, 值: {result}")
# 预期输出：Parser 输出类型: <class 'str'>, 值: 递归是函数调用自身的编程技巧
```

**示例2：进阶——用核心抽象组装一个完整的问答链**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

# 组装：Prompt Template → Chat Model → Output Parser
chain = (
    ChatPromptTemplate.from_template("用{style}的风格解释：{topic}")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    | StrOutputParser()
)

# 调用
result = chain.invoke({"style": "相声", "topic": "递归"})
print(result)
# 预期输出：（相声风格的递归解释）
```

**示例3：完整场景——带 Retriever 和 Memory 的 RAG 问答链骨架**

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI
from operator import itemgetter

# 模拟一个 Retriever（实际使用时替换为向量数据库检索器）
def fake_retriever(query: str) -> list:
    """模拟检索器：根据查询返回相关文档"""
    return [f"[文档1] 关于'{query}'的相关知识...", f"[文档2] 补充信息..."]

# 模拟 Memory（实际使用时替换为 ConversationBufferMemory 等）
def load_history(_: dict) -> list:
    """模拟加载对话历史"""
    return []

# 构建 RAG 链
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "根据以下上下文回答问题。如果上下文没有相关信息，请说'我不知道'。\n\n上下文：{context}"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

rag_chain = (
    RunnablePassthrough.assign(
        context=itemgetter("question") | RunnableLambda(fake_retriever) | (lambda docs: "\n".join(docs)),
        history=RunnableLambda(load_history)
    )
    | rag_prompt
    | model
    | StrOutputParser()
)

# 调用
answer = rag_chain.invoke({"question": "什么是 RAG？"})
print(answer)
# 预期输出：根据上下文，RAG 是检索增强生成...
```

#### 使用场景与最佳实践

**适用场景**：
- 理解 LangChain 整体架构时建立全局认知
- 设计 LLM 应用架构时选择合适的抽象组件
- 排查问题时定位是哪个抽象层出了问题
- 学习新组件时理解它在整体架构中的位置

**不适用场景**：
- 不需要了解架构的简单脚本开发
- 已经熟悉 LangChain 的开发者不需要反复阅读此节

**最佳实践**：
1. **理解数据流**：在设计链之前，先画数据流图，明确每个组件的输入输出
2. **选择合适抽象**：简单任务用 Chat Model + StrOutputParser，复杂任务才引入 Retriever/Memory/Tool
3. **保持组件单一职责**：每个组件只做一件事，复杂逻辑拆分为多个 Runnable
4. **利用类型系统**：使用 TypedDict/Pydantic 定义链的输入输出类型，提前发现类型错误
5. **文档化自定义组件**：为自定义 Runnable/Tool 编写清晰的 docstring，说明输入输出和用途

**性能建议**：
- 减少链中不必要的组件，每个组件都有函数调用开销
- 对于高频调用的链，考虑使用缓存（`RunnableWithCache`）
- 大输入的 Prompt Template 渲染有性能开销，考虑预渲染静态部分

#### 常见坑点

**坑点1：混淆 Chat Model 和 LLM 的输入输出格式**
- **错误现象**：将字符串传给 Chat Model 报错，或将消息列表传给 LLM 报错
- **根本原因**：Chat Model 接收 `List[BaseMessage]` 返回 `AIMessage`；LLM 接收 `str` 返回 `str`。两者接口不同
- **正确做法**：
  ```python
  from langchain_openai import ChatOpenAI, OpenAI
  from langchain_core.messages import HumanMessage

  # Chat Model：消息列表 → AIMessage
  chat_model = ChatOpenAI(model="gpt-4o-mini")
  chat_result = chat_model.invoke([HumanMessage(content="你好")])  # ✅ 正确
  # chat_model.invoke("你好")  # ❌ 错误，需要消息列表

  # LLM：字符串 → 字符串（注意：新版 OpenAI 已不推荐使用纯 LLM 接口）
  # llm = OpenAI(model="gpt-3.5-turbo-instruct")
  # llm_result = llm.invoke("你好")  # ✅ 正确
  ```
- **预防措施**：新项目统一使用 Chat Model（所有现代模型都支持聊天接口）；查看组件的 `input_schema` 和 `output_schema` 确认类型

**坑点2：Output Parser 的输入类型不匹配**
- **错误现象**：`StrOutputParser` 收到字符串时报错，或 `PydanticOutputParser` 收到 AIMessage 时解析失败
- **根本原因**：Output Parser 的输入通常是 `AIMessage` 或 `str`，但某些 Parser 对输入类型有特定要求
- **正确做法**：
  ```python
  from langchain_core.output_parsers import StrOutputParser
  from langchain_core.messages import AIMessage

  parser = StrOutputParser()

  # StrOutputParser 可以处理 AIMessage 和 str
  parser.invoke(AIMessage(content="你好"))  # ✅ 返回 "你好"
  parser.invoke("你好")                       # ✅ 返回 "你好"

  # PydanticOutputParser 需要 LLM 输出符合格式的文本
  # 通常放在 Chat Model 之后，由 Chat Model 输出 AIMessage，Parser 自动提取 content
  chain = prompt | model | pydantic_parser  # ✅ 正确，model 输出 AIMessage，parser 提取 content
  ```
- **预防措施**：在链中使用 Parser 时，确保前一个组件的输出类型与 Parser 的输入类型兼容；使用 `chain.input_schema` 和 `chain.output_schema` 验证类型

---

> 💡 **深度讲解**
>
> LangChain 的成功在于它抓住了 LLM 应用开发的"组合性"本质。LLM 应用通常不是单一的模型调用，而是多个步骤的组合——Prompt 模板填充 → 模型调用 → 输出解析 → 检索增强 → 工具调用 → 记忆管理。在 LangChain 出现之前，开发者需要自己编写胶水代码将这些步骤组合起来，导致代码重复、难以维护、难以测试。
>
> LangChain 通过标准化的 Runnable 协议和 `|` 运算符，将这些步骤变成了可组合的积木——`prompt | model | output_parser` 就是一个完整的链，每个组件都可以独立替换（换模型只需要换 model 组件，换输出格式只需要换 output_parser）。这种设计的另一个优势是"统一的执行接口"——所有 Runnable 都支持 `invoke`（同步）、`ainvoke`（异步）、`stream`（流式）、`batch`（批量），这意味着你构建的链天然支持这些执行模式，不需要额外编写代码。
>
> LangChain 的生态也是其核心竞争力——它集成了 100+ 模型提供商、50+ 向量数据库、100+ 工具和数据源，开发者不需要自己编写适配器，直接使用社区集成即可。LangChain 的演进也值得关注——从最初的 Chain 类（LLMChain、SequentialChain）到 LCEL（表达式语言），从单一的 langchain 包到 langchain-core/langchain-community/langgraph 的拆分，LangChain 正在变得更加模块化和灵活。
>
> 对于新手来说，最重要的是建立"组件思维"——不要把 LangChain 当成一个黑盒框架，而是把它理解为一组标准化的乐高积木。理解了每个积木的输入输出和用途，你就可以自由组合出任何复杂度的 LLM 应用。同时，要关注 LangChain 的最佳实践——使用 LCEL 而非旧版 Chain 类、使用异步方法提升并发、使用 LangSmith 进行可观测性、使用 LangGraph 处理复杂 Agent 流程。

> **📝 精简总结**
>
> LangChain 是最流行的 LLM 应用开发框架，核心设计是"组合优于继承"；核心抽象包括 Chat Model/LLM、Message、Prompt Template、Output Parser、Retriever、Document、Tool、Memory、Callback、Runnable；生态采用模块化设计，包括 langchain-core（核心接口）、langchain-community（第三方集成）、langchain（高级抽象）、langgraph（多Agent编排）、langserve（API部署）、langsmith（可观测性）；核心是 Runnable 协议和 `|` 运算符组合链，数据在 Runnable 间流动；优势是标准化抽象、可组合组件、丰富集成生态、统一执行接口（invoke/stream/batch/async）。

> **🎯 梯度练习题**
>
> **入门级**：
> 1. 安装 LangChain 环境，运行 `prompt | model | parser` 基础链，输出"你好，LangChain"
> 2. 使用 ChatPromptTemplate 定义一个带 `{name}` 和 `{role}` 两个变量的提示词，调用模型生成自我介绍
> 3. 解释 LangChain 六大核心抽象各自的职责，用一句话概括
>
> **进阶级**：
> 1. 构建一个翻译链，支持通过变量指定源语言和目标语言，调用3次验证中→英、英→日、日→中
> 2. 查看 `ChatOpenAI` 的 `input_schema` 和 `output_schema`，解释为什么 Chat Model 的输入是消息列表而不是字符串
> 3. 对比直接调用 OpenAI API 和使用 LangChain 的代码量差异，列出 LangChain 带来的 5 个具体好处
>
> **实战级**：
> 1. 设计一个"智能客服"链的架构图，标注每个环节使用哪个 LangChain 抽象，说明输入输出数据流
> 2. 使用虚拟环境搭建完整的 LangChain 开发环境，导出 requirements.txt，说明每个包的作用
> 3. 编写一个自定义 Runnable，功能是将输入文本转换为大写，然后将其组合到 `prompt | model | parser` 链中，验证完整流程

---

## 二、入门篇：核心抽象详解（Model I/O）

### 2.1 Chat Model 与 LLM

#### 概念解释

**正式定义**：Chat Model（聊天模型）是 LangChain 中对支持聊天接口的 LLM 的抽象，接收消息列表（`List[BaseMessage]`）作为输入，返回 `AIMessage` 作为输出；LLM（文本补全模型）是对传统文本补全接口的抽象，接收字符串返回字符串。现代 LLM 应用几乎都使用 Chat Model。

**生活化比喻**：Chat Model 就像一个有记忆的对话伙伴——你把之前的对话记录（消息列表）给它，它能理解上下文并给出回应；LLM 就像一个一次性的文本续写器——你给它一段文字开头，它接着往下写，不知道之前聊过什么。

**核心价值**：Chat Model 抽象屏蔽了不同模型提供商（OpenAI、Anthropic、Google 等）的 API 差异，提供统一的调用接口；支持消息列表使得多轮对话、系统提示、工具调用等高级功能成为可能；统一接口使得模型可以无缝切换。

#### 原理说明

```mermaid
sequenceDiagram
    participant U as 用户代码
    participant CM as Chat Model
    participant API as 模型提供商 API
    participant LLM as 大语言模型

    U->>CM: invoke([SystemMessage, HumanMessage])
    CM->>CM: 格式化消息（统一格式→提供商格式）
    CM->>API: 发送 HTTP 请求
    API->>LLM: 推理计算
    LLM-->>API: 返回生成结果
    API-->>CM: 返回 JSON 响应
    CM->>CM: 解析响应（提供商格式→AIMessage）
    CM-->>U: 返回 AIMessage
```

**Chat Model 的核心机制**：
1. **消息标准化**：将 LangChain 的 `BaseMessage` 转换为各提供商的 API 格式（OpenAI 的 `{"role": "user", "content": "..."}`）
2. **参数映射**：将 LangChain 的参数（temperature、max_tokens 等）映射为各提供商的参数名
3. **响应解析**：将 API 返回的 JSON 解析为 `AIMessage`，提取 content、tool_calls 等字段
4. **错误处理**：统一处理 API 错误、超时、限流等异常
5. **流式支持**：将 SSE 流式响应转换为 Python 生成器

**技术对比**：

| 维度 | Chat Model | LLM（文本补全） |
|------|-----------|----------------|
| 输入 | `List[BaseMessage]` | `str` |
| 输出 | `AIMessage` | `str` |
| 系统提示 | 原生支持（SystemMessage） | 需拼接到输入文本 |
| 多轮对话 | 原生支持（消息列表） | 需手动拼接历史 |
| 工具调用 | 原生支持（tool_calls） | 不支持 |
| 现代模型支持 | 所有新模型都支持 | 逐渐被淘汰 |
| 推荐度 | ⭐⭐⭐⭐⭐（推荐） | ⭐⭐（不推荐） |

> 🎯 **面试高频考点**：Chat Model 和 LLM 的区别是什么？为什么推荐使用 Chat Model？答：Chat Model 接收消息列表返回 AIMessage，原生支持系统提示、多轮对话和工具调用；LLM 接收字符串返回字符串，是传统文本补全接口。推荐使用 Chat Model 因为所有现代 LLM 都采用聊天接口，Chat Model 功能更强大、接口更统一，LLM 接口正在被逐步淘汰。

#### 代码示例

**示例1：基础——使用 ChatOpenAI 进行简单对话**

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# 1. 创建 Chat Model 实例
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,        # 创造性：0=确定性，1=最大创造性
    max_tokens=500,         # 最大生成 Token 数
    timeout=30,             # 超时时间（秒）
    max_retries=2,          # 失败重试次数
)

# 2. 单轮对话
response = model.invoke([
    SystemMessage(content="你是一个专业的 Python 讲师，用简洁的语言回答问题。"),
    HumanMessage(content="什么是列表推导式？")
])

print(f"回复类型: {type(response)}")
print(f"回复内容: {response.content}")
# 预期输出：
# 回复类型: <class 'langchain_core.messages.ai.AIMessage'>
# 回复内容: 列表推导式是 Python 中一种简洁的创建列表的方式...
```

**示例2：进阶——多轮对话与消息历史管理**

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

# 构建多轮对话消息列表
messages = [
    SystemMessage(content="你是一个乐于助人的 AI 助手。"),
    HumanMessage(content="我叫小明，今年25岁。"),
    AIMessage(content="你好小明！很高兴认识你。有什么我可以帮你的吗？"),
    HumanMessage(content="我叫什么名字？今年多大？"),
]

# 调用模型（模型能从消息历史中获取上下文）
response = model.invoke(messages)
print(response.content)
# 预期输出：你叫小明，今年25岁。

# 继续对话（将上一轮回复加入消息列表）
messages.append(response)
messages.append(HumanMessage(content="根据我的年龄，你推荐我做哪些理财规划？"))
response2 = model.invoke(messages)
print(response2.content)
# 预期输出：根据你25岁的年龄，我建议...
```

**示例3：完整场景——模型切换与统一接口演示**

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# 定义一个通用的问答链
def create_qa_chain(model):
    """创建问答链，接受任意 Chat Model 实例"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个知识渊博的助手，请准确回答问题。"),
        ("human", "{question}")
    ])
    return prompt | model | StrOutputParser()

# 使用 GPT-4o-mini
model_mini = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain_mini = create_qa_chain(model_mini)
result_mini = chain_mini.invoke({"question": "Python 和 JavaScript 的主要区别是什么？"})
print("=== GPT-4o-mini 回答 ===")
print(result_mini[:200])
print()

# 使用 GPT-4o（只需替换模型实例，链的其他部分不变）
model_4o = ChatOpenAI(model="gpt-4o", temperature=0)
chain_4o = create_qa_chain(model_4o)
result_4o = chain_4o.invoke({"question": "Python 和 JavaScript 的主要区别是什么？"})
print("=== GPT-4o 回答 ===")
print(result_4o[:200])

# 预期输出：两个模型都能正确回答问题，代码结构完全相同，只需替换 model 参数
```

#### 使用场景与最佳实践

**适用场景**：
- 所有现代 LLM 应用的模型调用（聊天、问答、生成、提取等）
- 需要多轮对话上下文的场景
- 需要系统提示引导模型行为的场景
- 需要工具调用（Function Calling）的场景
- 需要在不同模型提供商之间切换的场景

**不适用场景**：
- 使用传统文本补全模型（如 GPT-3 davinci）的遗留系统
- 对延迟极度敏感且不需要消息列表的极简调用（直接用 SDK 可能更快）

**最佳实践**：
1. **统一使用 Chat Model**：新项目一律使用 Chat Model，不要使用 LLM 文本补全接口
2. **合理设置 temperature**：创造性任务（写作、头脑风暴）用 0.7-1.0；确定性任务（提取、分类、翻译）用 0-0.3
3. **限制 max_tokens**：根据任务需要设置合理的 max_tokens，避免意外生成超长内容消耗配额
4. **使用 SystemMessage 引导行为**：通过系统提示设定角色、风格、约束，比在用户消息中说明更有效
5. **设置超时和重试**：生产环境必须设置 timeout 和 max_retries，应对网络波动和 API 限流

**性能建议**：
- 简单任务优先使用小模型（gpt-4o-mini），成本仅为大模型的 1/10，延迟降低 50%+
- 使用 `model_kwargs` 传递提供商特定参数，如 `{"top_p": 0.9, "frequency_penalty": 0.5}`
- 批量调用使用 `.batch()` 方法，LangChain 会自动并发处理
- 对于高频重复请求，考虑使用缓存层减少 API 调用

#### 常见坑点

**坑点1：temperature 设置不当导致输出不稳定**
- **错误现象**：同样的输入每次输出差异很大，或数据提取结果格式不一致
- **根本原因**：temperature 过高（如 0.7+）导致模型输出随机性大，对于需要确定性输出的任务（提取、分类）不合适
- **正确做法**：
  ```python
  # 确定性任务：temperature=0
  extraction_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

  # 创造性任务：temperature=0.7-1.0
  creative_model = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)

  # 平衡型任务：temperature=0.3-0.5
  balanced_model = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)
  ```
- **预防措施**：根据任务类型选择 temperature；在代码注释中说明为什么选择该 temperature 值

**坑点2：消息列表中角色顺序错误导致模型行为异常**
- **错误现象**：模型忽略系统提示，或回复风格不符合预期，或工具调用不触发
- **根本原因**：消息列表的角色顺序不符合 API 要求——SystemMessage 应在最前面，HumanMessage 和 AIMessage 应交替出现，不能连续两个相同角色
- **正确做法**：
  ```python
  # ✅ 正确：System → Human → AI → Human
  messages = [
      SystemMessage(content="你是一个友好的助手"),
      HumanMessage(content="你好"),
      AIMessage(content="你好！有什么可以帮你？"),
      HumanMessage(content="今天天气怎么样？"),
  ]

  # ❌ 错误：连续两个 HumanMessage
  # messages = [
  #     SystemMessage(content="..."),
  #     HumanMessage(content="你好"),
  #     HumanMessage(content="今天天气怎么样？"),  # 缺少 AI 回复
  # ]

  # ❌ 错误：SystemMessage 不在最前面
  # messages = [
  #     HumanMessage(content="你好"),
  #     SystemMessage(content="你是一个友好的助手"),  # System 应在最前
  # ]
  ```
- **预防措施**：构建消息列表时遵循 System→Human→AI 交替的模式；使用 LangChain 的 Memory 组件自动管理消息历史，避免手动拼接出错

---

### 2.2 Message 消息类型体系

#### 概念解释

**正式定义**：Message（消息）是 LangChain 中对 LLM 对话中单条消息的抽象，包含 `content`（内容）和 `type`/`role`（角色）两个核心属性。LangChain 定义了五种消息类型：`SystemMessage`（系统消息）、`HumanMessage`（人类消息）、`AIMessage`（AI 消息）、`ToolMessage`（工具消息）、`FunctionMessage`（函数消息，已弃用），它们共同构成了 LLM 的对话上下文。

**生活化比喻**：Message 就像剧本中的台词——每条台词都有说话者（角色）和内容。SystemMessage 是舞台指示（"这是一个悬疑剧场景"），HumanMessage 是观众提问，AIMessage 是演员回答，ToolMessage 是道具组递上来的道具（工具执行结果）。不同角色的台词组合起来就是完整的剧本（对话上下文）。

**核心价值**：标准化的消息类型使得多轮对话、系统提示、工具调用等功能可以统一表示；不同模型提供商的消息格式差异被屏蔽；消息可以序列化、存储、传输，支持记忆和持久化。

#### 原理说明

```mermaid
classDiagram
    class BaseMessage {
        +content: str | list
        +type: str
        +additional_kwargs: dict
        +response_metadata: dict
        +to_json()
        +pretty_print()
    }
    class SystemMessage {
        +type = "system"
    }
    class HumanMessage {
        +type = "human"
        +example: bool
    }
    class AIMessage {
        +type = "ai"
        +tool_calls: list
        +invalid_tool_calls: list
    }
    class ToolMessage {
        +type = "tool"
        +tool_call_id: str
        +name: str
    }
    BaseMessage <|-- SystemMessage
    BaseMessage <|-- HumanMessage
    BaseMessage <|-- AIMessage
    BaseMessage <|-- ToolMessage
```

**各消息类型详解**：

| 消息类型 | 角色 | 用途 | 关键属性 |
|---------|------|------|---------|
| **SystemMessage** | system | 设定模型角色、行为、约束 | `content` |
| **HumanMessage** | human | 用户输入/提问 | `content`, `example` |
| **AIMessage** | ai | 模型回复/工具调用请求 | `content`, `tool_calls` |
| **ToolMessage** | tool | 工具执行结果 | `content`, `tool_call_id`, `name` |
| **FunctionMessage** | function | 函数执行结果（已弃用，用 ToolMessage） | `content`, `name` |

**AIMessage 的 tool_calls 结构**：
```python
# AIMessage 中的工具调用请求结构
{
    "name": "search",           # 工具名称
    "args": {"query": "AI新闻"}, # 工具参数
    "id": "call_abc123",        # 工具调用 ID（用于匹配 ToolMessage）
    "type": "tool_call"
}
```

> 🎯 **面试高频考点**：LangChain 有哪几种消息类型？ToolMessage 的 tool_call_id 有什么作用？答：有 SystemMessage、HumanMessage、AIMessage、ToolMessage 四种主要类型（FunctionMessage 已弃用）。ToolMessage 的 tool_call_id 用于与 AIMessage 中的 tool_calls 进行匹配——模型发起工具调用时会生成一个 call_id，工具执行后返回的 ToolMessage 必须携带相同的 tool_call_id，这样模型才能将工具结果与对应的调用请求关联起来。

#### 代码示例

**示例1：基础——创建和使用各种消息类型**

```python
from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage, ToolMessage
)

# 1. SystemMessage：系统提示
system_msg = SystemMessage(content="你是一个专业的代码审查专家，关注代码质量和安全性。")
print(f"[{system_msg.type}] {system_msg.content}")
# 预期输出：[system] 你是一个专业的代码审查专家...

# 2. HumanMessage：用户输入
human_msg = HumanMessage(content="请审查这段代码：print('hello')")
print(f"[{human_msg.type}] {human_msg.content}")
# 预期输出：[human] 请审查这段代码...

# 3. AIMessage：AI 回复
ai_msg = AIMessage(content="这段代码语法正确，但缺少错误处理和文档字符串。")
print(f"[{ai_msg.type}] {ai_msg.content}")
# 预期输出：[ai] 这段代码语法正确...

# 4. ToolMessage：工具执行结果
tool_msg = ToolMessage(
    content="搜索结果：Python print 函数用于输出文本到控制台。",
    tool_call_id="call_abc123",
    name="web_search"
)
print(f"[{tool_msg.type}] (工具:{tool_msg.name}, id:{tool_msg.tool_call_id}) {tool_msg.content}")
# 预期输出：[tool] (工具:web_search, id:call_abc123) 搜索结果...
```

**示例2：进阶——带工具调用的完整消息序列**

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 完整的工具调用消息序列
messages = [
    # 1. 系统提示：告知模型可以使用工具
    SystemMessage(content="你是一个智能助手，可以使用搜索工具获取最新信息。"),

    # 2. 用户提问
    HumanMessage(content="今天的 AI 领域有什么重大新闻？"),

    # 3. AI 决定调用工具（tool_calls 字段包含工具调用请求）
    AIMessage(
        content="",  # 工具调用时 content 通常为空
        tool_calls=[{
            "name": "web_search",
            "args": {"query": "2026年 AI 重大新闻"},
            "id": "call_001",
            "type": "tool_call"
        }]
    ),

    # 4. 工具执行结果（tool_call_id 必须与上面的 id 匹配）
    ToolMessage(
        content="1. OpenAI 发布 GPT-5 模型；2. Google 推出 Gemini 3.0；3. 某 AI 公司获得 10 亿美元融资。",
        tool_call_id="call_001",
        name="web_search"
    ),

    # 5. AI 根据工具结果生成最终回答（此时不需要手动构造，模型会自动生成）
]

# 调用模型，模型会根据工具结果生成最终回答
response = model.invoke(messages)
print(response.content)
# 预期输出：根据最新搜索结果，今天 AI 领域有以下重大新闻：1. OpenAI 发布 GPT-5...
```

**示例3：完整场景——消息序列化与反序列化（用于记忆存储）**

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.load import dumps, loads

# 创建消息列表
messages = [
    SystemMessage(content="你是一个友好的助手"),
    HumanMessage(content="你好，我叫小红"),
    AIMessage(content="你好小红！很高兴认识你！"),
]

# 序列化：将消息列表转换为 JSON 字符串（用于存储到数据库或文件）
serialized = dumps(messages)
print(f"序列化后类型: {type(serialized)}")
print(f"序列化后长度: {len(serialized)} 字符")
print(f"序列化内容预览: {serialized[:200]}...")
# 预期输出：序列化后类型: <class 'str'>，包含 JSON 格式的消息数据

# 反序列化：从 JSON 字符串恢复消息列表
restored_messages = loads(serialized)
print(f"\n反序列化后消息数量: {len(restored_messages)}")
for msg in restored_messages:
    print(f"  [{msg.type}] {msg.content[:50]}")
# 预期输出：
# 反序列化后消息数量: 3
#   [system] 你是一个友好的助手
#   [human] 你好，我叫小红
#   [ai] 你好小红！很高兴认识你！

# 验证：反序列化后的消息可以直接用于模型调用
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o-mini")
restored_messages.append(HumanMessage(content="我叫什么名字？"))
response = model.invoke(restored_messages)
print(f"\n模型回答: {response.content}")
# 预期输出：你叫小红。
```

#### 使用场景与最佳实践

**适用场景**：
- 构建多轮对话的消息历史
- 实现工具调用（Function Calling）的消息序列
- 序列化对话历史用于记忆存储
- 构建 Few-shot 示例（使用 `example=True` 的 HumanMessage/AIMessage 对）
- 调试和日志记录（打印消息内容和元数据）

**不适用场景**：
- 不需要对话上下文的单次调用（可以直接用字符串 + Prompt Template）
- 非聊天模型的调用（传统 LLM 接口不使用消息类型）

**最佳实践**：
1. **SystemMessage 放在最前面**：系统提示应始终是消息列表的第一条，设定模型的整体行为
2. **Human/AIMessage 交替出现**：保持对话的自然交替，不要连续出现两条相同角色的消息
3. **ToolMessage 必须匹配 tool_call_id**：工具结果消息的 tool_call_id 必须与 AIMessage 中对应的 tool_call id 一致
4. **使用消息序列化存储历史**：使用 `dumps()`/`loads()` 序列化消息，不要手动拼接字符串
5. **控制消息列表长度**：过长的消息列表会增加 Token 消耗和延迟，定期摘要或截断历史

**性能建议**：
- 消息列表的 Token 数直接影响 API 成本和延迟，使用 `model.get_num_tokens_from_messages(messages)` 估算 Token 数
- 对于长对话，使用摘要记忆（ConversationSummaryMemory）减少历史消息数量
- 批量处理多个对话时，注意每个对话的消息列表独立，不要共享引用

#### 常见坑点

**坑点1：ToolMessage 的 tool_call_id 不匹配导致模型忽略工具结果**
- **错误现象**：模型调用了工具，但收到工具结果后仍然说"我无法获取实时信息"或重复调用同一个工具
- **根本原因**：ToolMessage 的 tool_call_id 与 AIMessage 中 tool_calls 的 id 不匹配，模型无法将工具结果与调用请求关联
- **正确做法**：
  ```python
  # 模型返回的 AIMessage 中有 tool_calls
  ai_response = model.invoke(messages)
  # ai_response.tool_calls = [{"name": "search", "args": {...}, "id": "call_abc123"}]

  # 执行工具后，必须使用相同的 id 创建 ToolMessage
  for tool_call in ai_response.tool_calls:
      result = execute_tool(tool_call["name"], tool_call["args"])
      tool_msg = ToolMessage(
          content=result,
          tool_call_id=tool_call["id"],  # ✅ 必须匹配
          name=tool_call["name"]
      )
      messages.append(tool_msg)
  ```
- **预防措施**：使用 LangChain 的 `ToolNode` 或 Agent 执行器自动管理 tool_call_id；手动构造时从 AIMessage 的 tool_calls 中提取 id

**坑点2：消息内容中包含特殊字符导致 JSON 解析错误**
- **错误现象**：序列化消息后反序列化失败，或模型返回的 AIMessage 无法解析 tool_calls
- **根本原因**：消息内容中包含未转义的特殊字符（如引号、反斜杠、换行符），导致 JSON 格式损坏
- **正确做法**：
  ```python
  import json

  # 不要手动构造 JSON 格式的消息
  # ❌ 错误：手动拼接可能导致转义问题
  # msg_json = '{"content": "他说："你好"", "type": "human"}'

  # ✅ 正确：使用 LangChain 的消息类和序列化函数
  from langchain_core.messages import HumanMessage
  from langchain_core.load import dumps, loads

  msg = HumanMessage(content='他说："你好"')  # 特殊字符自动处理
  serialized = dumps([msg])  # 自动正确转义
  restored = loads(serialized)  # 自动正确解析
  print(restored[0].content)  # 输出：他说："你好"
  ```
- **预防措施**：始终使用 LangChain 提供的消息类和序列化函数，不要手动构造 JSON；对于模型返回的内容，使用 `AIMessage.model_validate()` 进行校验

---

### 2.3 Prompt Template 提示词模板

#### 概念解释

**正式定义**：Prompt Template（提示词模板）是 LangChain 中对可复用提示词的抽象，支持变量注入、消息列表构建和部分预填充。主要包括 `PromptTemplate`（字符串模板）和 `ChatPromptTemplate`（聊天消息模板），通过 `format()` 或 `invoke()` 方法将变量替换为实际值，生成模型可接受的提示词。

**生活化比喻**：Prompt Template 就像填空题试卷——试卷上有固定的题目框架（模板文本）和空白处（变量占位符 `{name}`），你只需要在空白处填入具体内容（变量值），就能生成一份完整的试卷。ChatPromptTemplate 则像一个分角色的剧本模板——有旁白（SystemMessage）、观众台词（HumanMessage）、演员台词（AIMessage），每个角色的台词都可以有填空题。

**核心价值**：将提示词逻辑与业务代码分离，提高可维护性；支持变量注入实现动态提示词；支持部分预填充复用公共参数；标准化的模板格式便于分享和版本管理。

#### 原理说明

```mermaid
graph LR
    subgraph 输入
        V[变量字典<br/>{name: "小明", role: "程序员"}]
    end

    subgraph Prompt Template
        T[模板文本<br/>"你是{role}，请介绍{name}"]
        R[渲染引擎<br/>变量替换]
    end

    subgraph 输出
        PV[PromptValue<br/>可转换为 str 或 messages]
    end

    V --> R
    T --> R
    R --> PV
    PV -->|to_string()| S[字符串]
    PV -->|to_messages()| M[消息列表]

    style T fill:#e3f2fd
    style R fill:#fff3e0
```

**Prompt Template 的核心机制**：
1. **变量解析**：使用 Python `string.Formatter` 语法解析模板中的 `{variable}` 占位符
2. **变量替换**：调用 `format(**kwargs)` 或 `invoke()` 时将变量替换为实际值
3. **格式校验**：检查所有必需变量是否已提供，缺少变量时抛出明确的错误
4. **部分预填充**：使用 `partial()` 方法预填充部分变量，返回新的模板
5. **消息构建**：ChatPromptTemplate 将多条消息模板组合为消息列表

**技术对比**：

| 维度 | PromptTemplate（字符串） | ChatPromptTemplate（聊天） |
|------|------------------------|--------------------------|
| 输出 | `str` | `List[BaseMessage]` |
| 适用模型 | LLM（文本补全） | Chat Model（推荐） |
| 系统提示 | 需手动拼接 | 原生支持 |
| 多角色 | 不支持 | 支持 system/human/ai/tool |
| 推荐度 | ⭐⭐（遗留用） | ⭐⭐⭐⭐⭐（推荐） |

> 🎯 **面试高频考点**：PromptTemplate 和 ChatPromptTemplate 的区别是什么？答：PromptTemplate 生成字符串提示词，适用于传统 LLM 文本补全接口；ChatPromptTemplate 生成消息列表（List[BaseMessage]），适用于现代 Chat Model，原生支持系统提示和多角色消息。新项目推荐使用 ChatPromptTemplate，因为所有现代 LLM 都采用聊天接口。

#### 代码示例

**示例1：基础——使用 ChatPromptTemplate 创建聊天提示词**

```python
from langchain_core.prompts import ChatPromptTemplate

# 1. from_messages：从消息元组列表创建（最常用）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{role}，用简洁的语言回答问题。"),
    ("human", "{question}")
])

# 2. 查看模板需要的变量
print(f"需要的变量: {prompt.input_variables}")
# 预期输出：需要的变量: ['question', 'role']

# 3. 渲染模板（invoke 返回 PromptValue）
prompt_value = prompt.invoke({"role": "Python 讲师", "question": "什么是装饰器？"})
print(f"输出类型: {type(prompt_value)}")
print(f"消息列表: {prompt_value.to_messages()}")
# 预期输出：
# 输出类型: <class 'langchain_core.prompt_values.ChatPromptValue'>
# 消息列表: [SystemMessage(content='你是一个专业的Python 讲师...'), HumanMessage(content='什么是装饰器？')]
```

**示例2：进阶——部分预填充与消息占位符**

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# 1. 部分预填充：预填充 role 变量，返回新模板
base_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{role}。"),
    ("human", "{question}")
])

# 预填充 role 为 "数据分析师"
data_analyst_prompt = base_prompt.partial(role="数据分析师")
print(f"预填充后需要的变量: {data_analyst_prompt.input_variables}")
# 预期输出：预填充后需要的变量: ['question']（role 已预填充）

# 只需传入 question
result = data_analyst_prompt.invoke({"question": "什么是 A/B 测试？"})
print(result.to_messages()[0].content)  # 你是一个专业的数据分析师。

# 2. MessagesPlaceholder：动态插入消息列表（用于对话历史）
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的助手。"),
    MessagesPlaceholder(variable_name="history"),  # 动态插入历史消息
    ("human", "{input}")
])

# 传入历史消息
history = [
    HumanMessage(content="我叫小红"),
    AIMessage(content="你好小红！"),
]
prompt_value = chat_prompt.invoke({
    "history": history,
    "input": "我叫什么名字？"
})
messages = prompt_value.to_messages()
print(f"消息数量: {len(messages)}")
for msg in messages:
    print(f"  [{msg.type}] {msg.content}")
# 预期输出：
# 消息数量: 4
#   [system] 你是一个友好的助手。
#   [human] 我叫小红
#   [ai] 你好小红！
#   [human] 我叫什么名字？
```

**示例3：完整场景——Few-shot 示例模板与动态示例选择**

```python
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 1. 定义 Few-shot 示例
examples = [
    {"input": "这款手机拍照效果很好，电池也耐用", "output": "正面"},
    {"input": "物流太慢了，包装也有破损", "output": "负面"},
    {"input": "价格还行，质量一般般", "output": "中性"},
]

# 2. 创建示例消息模板
example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}")
])

# 3. 创建 Few-shot 消息模板
few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

# 4. 组合最终提示词
final_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个情感分析专家。请判断以下评论的情感倾向，只回答：正面、负面、中性。"),
    few_shot_prompt,  # 插入 Few-shot 示例
    ("human", "{input}")
])

# 5. 组合链
chain = final_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0) | StrOutputParser()

# 6. 测试
test_cases = [
    "这个产品太棒了，强烈推荐！",
    "太差了，再也不会买了。",
    "收到了，还没用，先给个中评。",
]

for text in test_cases:
    result = chain.invoke({"input": text})
    print(f"评论: {text}")
    print(f"情感: {result}")
    print()

# 预期输出：
# 评论: 这个产品太棒了，强烈推荐！
# 情感: 正面
#
# 评论: 太差了，再也不会买了。
# 情感: 负面
#
# 评论: 收到了，还没用，先给个中评。
# 情感: 中性
```

#### 使用场景与最佳实践

**适用场景**：
- 所有需要动态生成提示词的 LLM 应用
- 多轮对话中注入历史消息（MessagesPlaceholder）
- Few-shot 学习（提供示例引导模型输出格式）
- 系统提示与用户输入分离
- 提示词版本管理和 A/B 测试

**不适用场景**：
- 提示词完全固定且无变量的极简场景（直接用字符串即可）
- 需要极端性能优化且模板渲染成为瓶颈的场景（罕见）

**最佳实践**：
1. **使用 ChatPromptTemplate.from_messages**：这是最灵活的创建方式，支持多种消息类型和变量
2. **系统提示与用户输入分离**：将角色设定、约束条件放在 SystemMessage，将具体问题放在 HumanMessage
3. **使用 MessagesPlaceholder 注入历史**：不要手动拼接历史消息到字符串中，使用 MessagesPlaceholder 保持类型安全
4. **利用 partial 预填充公共变量**：对于多个链共享的变量（如角色、语言），使用 partial 预填充减少重复
5. **提示词外部化**：将复杂提示词存储在单独的文件或 LangSmith Hub 中，便于版本管理和非技术人员编辑

**性能建议**：
- 模板渲染本身很快（微秒级），不会成为性能瓶颈
- 对于超大模板（>10KB），预渲染静态部分减少每次调用的渲染开销
- 使用 `prompt.pretty_print()` 调试时查看渲染后的完整提示词

#### 常见坑点

**坑点1：模板变量与输入字典 Key 不匹配**
- **错误现象**：`KeyError: 'question'` 或模板中的 `{question}` 未被替换，原样输出
- **根本原因**：Prompt Template 中定义的变量名与 invoke 时传入的字典 Key 不一致（拼写错误、大小写差异、遗漏变量）
- **正确做法**：
  ```python
  from langchain_core.prompts import ChatPromptTemplate

  prompt = ChatPromptTemplate.from_messages([
      ("system", "你是{role}"),
      ("human", "{question}")
  ])

  # 查看需要哪些变量
  print(prompt.input_variables)  # ['question', 'role']

  # ✅ 正确：传入所有必需变量
  prompt.invoke({"role": "老师", "question": "什么是 AI？"})

  # ❌ 错误：缺少 role 变量
  # prompt.invoke({"question": "什么是 AI？"})

  # ❌ 错误：Key 名不匹配（用了 name 而不是 role）
  # prompt.invoke({"name": "老师", "question": "什么是 AI？"})
  ```
- **预防措施**：使用 `prompt.input_variables` 查看所有必需变量；在调用前验证输入字典包含所有 Key；使用类型注解（TypedDict）定义输入类型

**坑点2：在 Prompt 中使用花括号导致变量解析错误**
- **错误现象**：模板中包含 JSON 示例或代码块时，`{` 和 `}` 被误认为变量占位符，导致 `KeyError` 或格式错误
- **根本原因**：Prompt Template 使用 Python `string.Formatter` 语法，单个 `{` 和 `}` 被解析为变量占位符。如果模板中需要字面花括号（如 JSON 示例），必须使用 `{{` 和 `}}` 转义
- **正确做法**：
  ```python
  from langchain_core.prompts import ChatPromptTemplate

  # ❌ 错误：JSON 中的花括号被误认为变量
  # prompt = ChatPromptTemplate.from_template(
  #     "请输出 JSON 格式：{\"name\": \"{name}\", \"age\": {age}}"
  # )

  # ✅ 正确：使用双花括号转义字面花括号
  prompt = ChatPromptTemplate.from_template(
      "请输出 JSON 格式：{{\"name\": \"{name}\", \"age\": {age}}}"
  )

  result = prompt.invoke({"name": "小明", "age": 25})
  print(result.to_string())
  # 预期输出：请输出 JSON 格式：{"name": "小明", "age": 25}

  # 另一种方式：使用 Output Parser 的 get_format_instructions() 自动生成格式说明
  from langchain_core.output_parsers import JsonOutputParser
  parser = JsonOutputParser()
  format_instructions = parser.get_format_instructions()
  # format_instructions 中已正确转义花括号
  ```
- **预防措施**：模板中包含 JSON、代码块或任何字面花括号时，使用 `{{` 和 `}}` 转义；优先使用 Output Parser 的 `get_format_instructions()` 生成格式说明，而不是手动编写 JSON 模板

---

> 💡 **深度讲解**
>
> Model I/O 是 LangChain 最基础也最重要的模块，它包含三个核心组件：Chat Model（模型调用）、Message（消息类型）、Prompt Template（提示词模板）。理解这三个组件的关系是掌握 LangChain 的第一步。
>
> Chat Model 是对 LLM API 的统一抽象，它屏蔽了不同模型提供商的 API 差异，使得开发者可以用相同的代码调用 GPT-4o、Claude 3.5、Gemini Pro 等不同模型。这种统一接口的价值在模型切换时尤为明显——只需要替换 model 参数，链的其他部分完全不需要修改。
>
> Message 消息类型体系是 Chat Model 的输入输出格式。SystemMessage 设定模型行为，HumanMessage 是用户输入，AIMessage 是模型回复，ToolMessage 是工具执行结果。这四种消息类型构成了完整的对话上下文。特别是 ToolMessage 的 tool_call_id 机制，它确保了工具调用请求和结果的正确匹配，是 Function Calling 能够工作的关键。
>
> Prompt Template 是提示词工程的工程化实现。它将提示词从硬编码字符串提升为可复用、可参数化、可版本管理的模板。ChatPromptTemplate 支持多种消息类型的模板组合，MessagesPlaceholder 支持动态注入对话历史，FewShotChatMessagePromptTemplate 支持 Few-shot 学习。这些特性使得复杂的提示词工程可以用简洁的代码实现。
>
> 对于新手来说，最容易混淆的是 Chat Model 和 LLM、PromptTemplate 和 ChatPromptTemplate 的区别。记住一个简单原则：现代 LLM 应用统一使用 Chat Model + ChatPromptTemplate，LLM 和 PromptTemplate 只在遗留系统中使用。

> **📝 精简总结**
>
> Model I/O 模块包含 Chat Model、Message、Prompt Template 三大核心组件；Chat Model 接收消息列表返回 AIMessage，统一屏蔽不同模型 API 差异，推荐使用 Chat Model 而非传统 LLM；Message 有 SystemMessage（系统提示）、HumanMessage（用户输入）、AIMessage（AI回复/工具调用请求）、ToolMessage（工具结果，需匹配 tool_call_id）四种类型；Prompt Template 支持变量注入，推荐使用 ChatPromptTemplate.from_messages 创建，支持 MessagesPlaceholder 注入历史和 FewShot 示例；三者组合为 `ChatPromptTemplate → Chat Model → Output Parser` 基础链。

> **🎯 梯度练习题**
>
> **入门级**：
> 1. 创建一个 ChatOpenAI 实例，设置 temperature=0，调用模型回答"什么是机器学习"
> 2. 使用四种消息类型（System/Human/AI/Tool）构建一个完整的工具调用消息序列
> 3. 创建一个 ChatPromptTemplate，包含 `{language}` 和 `{text}` 两个变量，实现翻译功能
>
> **进阶级**：
> 1. 构建一个多轮对话链，使用 MessagesPlaceholder 注入历史消息，验证模型能记住之前的对话内容
> 2. 使用 FewShotChatMessagePromptTemplate 实现文本分类（正面/负面/中性），提供3个示例并测试5个新样本
> 3. 实现一个模型切换函数，接受模型名称参数，返回使用对应模型的问答链，验证 GPT-4o-mini 和 GPT-4o 的输出差异
>
> **实战级**：
> 1. 设计一个"代码审查助手"链，使用 SystemMessage 设定审查标准（安全、性能、可读性），使用 Prompt Template 接受代码输入，输出审查报告
> 2. 实现消息历史的序列化存储（保存到 JSON 文件）和加载恢复，验证重启后对话历史不丢失
> 3. 对比直接使用 OpenAI SDK 和使用 LangChain Chat Model 的代码，列出 5 个具体差异点，分析 LangChain 在什么场景下带来的价值最大

---

## 三、入门篇：LCEL 与 Runnable 接口基础

### 3.1 LCEL 表达式语言原理

#### 概念解释

**正式定义**：LCEL（LangChain Expression Language）是 LangChain 的表达式语言，通过 `|` 运算符（管道符）将实现了 Runnable 接口的组件组合成链（Chain），链本身也是 Runnable，可以继续组合。LCEL 是 LangChain 推荐的组合组件的方式，替代了旧版的 Chain 类（LLMChain、SequentialChain 等）。

**生活化比喻**：LCEL 就像 Unix 管道命令——`cat file.txt | grep "error" | sort | uniq`，每个命令的输出作为下一个命令的输入，简单的命令组合起来完成复杂的任务。LCEL 中的 `prompt | model | parser` 也是同样的道理——Prompt 的输出作为 Model 的输入，Model 的输出作为 Parser 的输入，组合起来就是一个完整的问答链。

**核心价值**：用最简单的语法（`|` 运算符）实现最灵活的组件组合，链天然支持流式、异步、批量、并行、回退、重试等高级特性，无需额外编写代码；组件可以自由替换和测试，代码简洁易读。

#### 原理说明

```mermaid
graph LR
    subgraph LCEL 管道执行流程
        A[输入数据] --> B[Runnable 1<br/>Prompt Template]
        B -->|输出1| C[Runnable 2<br/>Chat Model]
        C -->|输出2| D[Runnable 3<br/>Output Parser]
        D --> E[最终输出]
    end

    subgraph RunnableSequence 内部
        F[first: Runnable] --> G[middle: Runnable...] --> H[last: Runnable]
    end

    style B fill:#e3f2fd
    style C fill:#f3e5f5
    style D fill:#e8f5e9
```

**LCEL 的核心机制**：
1. **`|` 运算符重载**：Runnable 类实现了 `__or__` 方法，`a | b` 等价于 `RunnableSequence(first=a, last=b)`
2. **RunnableSequence**：链的内部表示，按顺序执行各个 Runnable，前一个的输出作为后一个的输入
3. **类型推断**：链的输入类型是第一个 Runnable 的输入类型，输出类型是最后一个 Runnable 的输出类型
4. **自动特性继承**：链自动继承所有 Runnable 的执行模式（invoke/stream/batch/async），因为 RunnableSequence 本身实现了完整的 Runnable 接口
5. **配置传递**：调用链时传入的 config（如 callbacks、tags、metadata）会自动传递给链中的每个 Runnable

**LCEL 与旧版 Chain 类对比**：

| 维度 | 旧版 Chain 类（LLMChain 等） | LCEL（`|` 运算符） |
|------|------------------------------|-------------------|
| 组合方式 | 继承 Chain 基类，编写类 | `|` 运算符组合 |
| 灵活性 | 每种组合需要新类，类爆炸 | 任意 Runnable 自由组合 |
| 流式支持 | 需手动实现 | 链自动支持 |
| 异步支持 | 需手动实现 | 链自动支持 |
| 批量支持 | 不支持 | 链自动支持 |
| 并行支持 | 不支持 | RunnableParallel |
| 类型安全 | 弱 | 强（input_schema/output_schema） |
| 推荐度 | ⭐（已弃用） | ⭐⭐⭐⭐⭐（推荐） |

> 🎯 **面试高频考点**：LCEL 是什么？它相比旧版 Chain 类有什么优势？答：LCEL（LangChain Expression Language）是通过 `|` 运算符组合 Runnable 的表达式语言。优势包括：① 语法简洁，用 `|` 替代类继承；② 无限组合，任意 Runnable 可自由组合；③ 链自动支持流式/异步/批量/并行；④ 类型安全，有 input_schema/output_schema；⑤ 可观测性，链执行自动被 LangSmith 追踪。旧版 Chain 类已被弃用，新代码应使用 LCEL。

#### 代码示例

**示例1：基础——最简单的 LCEL 链**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 1. 创建各个组件
prompt = ChatPromptTemplate.from_template("用一句话解释：{topic}")
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = StrOutputParser()

# 2. 使用 | 运算符组合成链
chain = prompt | model | parser

# 3. 查看链的类型
print(f"链的类型: {type(chain).__name__}")
print(f"链的输入变量: {chain.input_schema.schema().get('properties', {}).keys()}")
# 预期输出：
# 链的类型: RunnableSequence
# 链的输入变量: dict_keys(['topic'])

# 4. 调用链
result = chain.invoke({"topic": "LCEL"})
print(f"结果: {result}")
# 预期输出：LCEL（LangChain Expression Language）是 LangChain 的表达式语言...
```

**示例2：进阶——链的多种执行模式**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import asyncio

chain = (
    ChatPromptTemplate.from_template("列出{topic}的3个要点，用数字编号")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

# 1. 同步调用 invoke
print("=== invoke（同步）===")
result = chain.invoke({"topic": "时间管理"})
print(result)

# 2. 流式输出 stream
print("\n=== stream（流式）===")
for chunk in chain.stream({"topic": "健康饮食"}):
    print(chunk, end="", flush=True)
print()

# 3. 批量处理 batch
print("\n=== batch（批量）===")
results = chain.batch([
    {"topic": "机器学习"},
    {"topic": "深度学习"},
    {"topic": "强化学习"},
])
for i, r in enumerate(results):
    print(f"结果 {i+1}: {r[:80]}...")

# 4. 异步调用 ainvoke
print("\n=== ainvoke（异步）===")
async def async_call():
    result = await chain.ainvoke({"topic": "云计算"})
    print(result)

asyncio.run(async_call())

# 预期输出：四种执行模式都能正确返回结果，stream 会逐字输出
```

**示例3：完整场景——链的嵌套组合与配置传递**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI

# 1. 创建子链：摘要链
summary_chain = (
    ChatPromptTemplate.from_template("用3句话总结以下内容：\n{text}")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

# 2. 创建子链：翻译链
translation_chain = (
    ChatPromptTemplate.from_template("将以下内容翻译成英文：\n{text}")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

# 3. 组合：并行执行摘要和翻译（RunnableParallel）
parallel_chain = RunnableParallel({
    "summary": summary_chain,
    "translation": translation_chain
})

# 4. 再组合：将并行结果格式化输出
format_prompt = ChatPromptTemplate.from_template("""
处理结果：

【摘要】
{summary}

【英文翻译】
{translation}
""")

# 5. 完整链：并行处理 → 格式化 → 模型润色
final_chain = (
    parallel_chain
    | format_prompt
    | ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    | StrOutputParser()
)

# 6. 调用完整链
input_text = """
LangChain 是一个用于构建大语言模型应用的开源框架。
它提供了标准化的核心抽象和表达式语言（LCEL），
使得开发者可以快速构建从简单问答到复杂 Agent 的各种应用。
LangChain 拥有丰富的生态系统，集成了 100+ 模型提供商和 50+ 向量数据库。
"""

result = final_chain.invoke({"text": input_text})
print(result)
# 预期输出：包含摘要和英文翻译的格式化结果
```

#### 使用场景与最佳实践

**适用场景**：
- 所有新的 LangChain 项目（替代旧版 Chain 类）
- 需要组合多个组件的 LLM 应用
- 需要流式、异步、批量等高级执行模式的场景
- 需要并行执行多个子任务的场景（RunnableParallel）
- 需要回退、重试等容错机制的生产环境

**不适用场景**：
- 维护旧版 LangChain 代码（需要逐步迁移而非一次性重写）
- 仅需单次模型调用的极简脚本（直接用 model.invoke 即可）

**最佳实践**：
1. **一律使用 LCEL**：新代码使用 `|` 运算符，不要使用 LLMChain 等旧版类
2. **保持链的可读性**：复杂链使用多行缩进和注释，每个 Runnable 占一行
3. **利用链的执行模式**：需要实时反馈用 stream，需要高并发用 ainvoke/abatch，需要处理多个输入用 batch
4. **使用 RunnableParallel 并行化**：无依赖的子任务用 RunnableParallel 并行执行，减少总延迟
5. **为链添加配置**：使用 `.with_config()` 添加 tags、metadata 便于 LangSmith 追踪和筛选

**性能建议**：
- 链中的每个 Runnable 都有函数调用开销（微秒级），对于极简单任务可以减少链的层数
- 并行执行使用 RunnableParallel，LangChain 会自动使用线程池并发执行
- 批量处理使用 `.batch()`，可以设置 `config={"max_concurrency": 5}` 控制并发数
- 流式输出时，Output Parser 可能会阻塞流式传输，对于简单字符串输出可以省略 Parser

#### 常见坑点

**坑点1：链中相邻 Runnable 的输入输出类型不匹配**
- **错误现象**：`TypeError: Can't instantiate abstract class ...` 或运行时类型错误，链执行失败
- **根本原因**：前一个 Runnable 的输出类型与后一个 Runnable 的输入类型不兼容。例如 Prompt Template 输出 PromptValue，而某个自定义 Runnable 期望字符串输入
- **正确做法**：
  ```python
  from langchain_core.prompts import ChatPromptTemplate
  from langchain_core.output_parsers import StrOutputParser
  from langchain_core.runnables import RunnableLambda
  from langchain_openai import ChatOpenAI

  # ✅ 正确：类型匹配
  # Prompt → Chat Model（PromptValue → AIMessage）
  # Chat Model → StrOutputParser（AIMessage → str）
  chain = ChatPromptTemplate.from_template("{question}") | ChatOpenAI() | StrOutputParser()

  # ❌ 错误：类型不匹配
  # Chat Model 输出 AIMessage，但自定义函数期望 str
  # def process(text: str): return text.upper()
  # bad_chain = ChatPromptTemplate.from_template("{q}") | ChatOpenAI() | RunnableLambda(process)
  # # ChatOpenAI 输出 AIMessage，不是 str

  # ✅ 修复：在中间加 StrOutputParser 转换
  fixed_chain = (
      ChatPromptTemplate.from_template("{q}")
      | ChatOpenAI()
      | StrOutputParser()  # 先转换为 str
      | RunnableLambda(lambda text: text.upper())
  )
  ```
- **预防措施**：使用 `chain.input_schema` 和 `chain.output_schema` 验证类型；在链中插入 RunnableLambda 进行类型转换；为自定义 Runnable 添加类型注解

**坑点2：在链中使用 lambda 导致序列化失败**
- **错误现象**：使用 LangServe 部署链时报 `PicklingError: Can't pickle <function <>`，或链无法保存到文件
- **根本原因**：Python 的 lambda 函数无法被 pickle 序列化，而 LangServe 部署和链的持久化需要序列化所有组件
- **正确做法**：
  ```python
  from langchain_core.runnables import RunnableLambda

  # ❌ 错误：使用 lambda（无法序列化）
  # bad_chain = RunnableLambda(lambda x: x.upper())

  # ✅ 正确：使用命名函数（可以序列化）
  def to_upper(text: str) -> str:
      return text.upper()

  good_chain = RunnableLambda(to_upper)

  # ✅ 正确：使用 itemgetter（可序列化）
  from operator import itemgetter
  extract_chain = itemgetter("key")  # itemgetter 可以被 pickle

  # ✅ 正确：使用 RunnablePassthrough（内置可序列化）
  from langchain_core.runnables import RunnablePassthrough
  pass_chain = RunnablePassthrough()
  ```
- **预防措施**：在链中避免使用 lambda，改用命名函数或 operator 模块中的函数；使用 LangServe 部署前先测试链是否可序列化；使用 `cloudpickle` 替代标准 pickle（但仍建议避免 lambda）

---

### 3.2 Runnable 接口详解

#### 概念解释

**正式定义**：Runnable 是 LangChain 中所有可运行组件的基类协议，定义了统一的执行接口：`invoke`（同步调用）、`stream`（流式输出）、`batch`（批量处理）、`ainvoke`（异步调用）、`astream`（异步流式）、`abatch`（异步批量）。所有核心组件（Chat Model、Prompt Template、Output Parser、Retriever、Tool）都实现了 Runnable 接口，因此可以通过 `|` 运算符自由组合。

**生活化比喻**：Runnable 接口就像电器的标准插头——所有电器（组件）都使用相同规格的插头（Runnable 接口），所以可以插入任何标准插座（链中的位置）。你不需要关心电器内部是怎么工作的，只需要知道它有标准插头就能用。Runnable 的六种方法就像电器的六种运行模式——正常运行（invoke）、渐进式输出（stream）、批量运行（batch）、遥控运行（ainvoke）等。

**核心价值**：统一的执行接口使得所有组件可以互换使用；链自动继承所有执行模式（不需要为每种模式编写额外代码）；自定义组件只需实现 Runnable 接口即可融入 LangChain 生态；接口标准化使得可观测性、容错、配置等横切关注点可以统一处理。

#### 原理说明

```mermaid
classDiagram
    class Runnable {
        <<abstract>>
        +invoke(input, config) Any
        +stream(input, config) Iterator
        +batch(inputs, config) List
        +ainvoke(input, config) Any
        +astream(input, config) AsyncIterator
        +abatch(inputs, config) List
        +__or__(other) RunnableSequence
        +with_fallbacks(fallbacks) RunnableWithFallbacks
        +with_retry(...) RunnableRetry
        +with_config(config) RunnableBinding
        +bind(**kwargs) RunnableBinding
    }
    class RunnableSequence
    class RunnableParallel
    class RunnableLambda
    class RunnablePassthrough
    class RunnableBranch
    Runnable <|-- RunnableSequence
    Runnable <|-- RunnableParallel
    Runnable <|-- RunnableLambda
    Runnable <|-- RunnablePassthrough
    Runnable <|-- RunnableBranch
```

**Runnable 六种核心方法详解**：

| 方法 | 同步/异步 | 输入 | 输出 | 适用场景 |
|------|----------|------|------|---------|
| `invoke` | 同步 | 单个输入 | 单个输出 | 最常用，简单调用 |
| `stream` | 同步 | 单个输入 | 输出迭代器 | 实时反馈、长文本生成 |
| `batch` | 同步 | 输入列表 | 输出列表 | 批量处理、高吞吐 |
| `ainvoke` | 异步 | 单个输入 | 单个输出 | 高并发服务、异步框架 |
| `astream` | 异步 | 单个输入 | 异步迭代器 | 异步流式响应 |
| `abatch` | 异步 | 输入列表 | 输出列表 | 异步批量处理 |

**Runnable 的增强方法**：

| 方法 | 作用 | 示例 |
|------|------|------|
| `with_fallbacks` | 主链失败时切换到备用链 | `chain.with_fallbacks([backup_chain])` |
| `with_retry` | 失败时自动重试 | `chain.with_retry(stop_after_attempt=3)` |
| `with_config` | 注入配置（callbacks/tags等） | `chain.with_config({"tags": ["production"]})` |
| `bind` | 绑定额外参数 | `model.bind(temperature=0.5)` |
| `assign` | 添加上下文字段（RunnablePassthrough） | `RunnablePassthrough.assign(history=...)` |
| `pick` | 选择输出字段 | `chain.pick("summary")` |

> 🎯 **面试高频考点**：Runnable 接口定义了哪些核心方法？为什么说 Runnable 是 LangChain 的基石？答：Runnable 定义了 invoke、stream、batch、ainvoke、astream、abatch 六种核心方法。Runnable 是基石因为：① 所有核心组件都实现了 Runnable 接口，统一了执行方式；② `|` 运算符基于 Runnable 的 `__or__` 方法，实现了组件组合；③ 链（RunnableSequence）本身也是 Runnable，可以继续组合；④ 统一接口使得流式、异步、批量、回退、重试等特性可以自动继承，无需重复实现。

#### 代码示例

**示例1：基础——Runnable 的六种执行方法**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import asyncio

chain = (
    ChatPromptTemplate.from_template("用一句话回答：{question}")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

# 1. invoke：同步调用，返回完整结果
result = chain.invoke({"question": "什么是 Runnable？"})
print(f"invoke 结果: {result}")

# 2. stream：流式输出，逐块返回
print("\nstream 结果:")
for chunk in chain.stream({"question": "什么是 LCEL？"}):
    print(chunk, end="", flush=True)
print()

# 3. batch：批量处理多个输入
results = chain.batch([
    {"question": "什么是 LangChain？"},
    {"question": "什么是 LangGraph？"},
    {"question": "什么是 LangSmith？"},
])
print(f"\nbatch 结果数量: {len(results)}")
for i, r in enumerate(results):
    print(f"  {i+1}. {r}")

# 4. ainvoke：异步调用
async def async_demo():
    result = await chain.ainvoke({"question": "什么是异步？"})
    print(f"\nainvoke 结果: {result}")

asyncio.run(async_demo())

# 预期输出：六种方法都能正确执行，stream 逐字输出，batch 返回3个结果
```

**示例2：进阶——自定义 Runnable**

```python
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from typing import Any, Iterator, AsyncIterator

# 自定义 Runnable：文本清洗器
class TextCleanerRunnable(Runnable):
    """自定义 Runnable：清洗输入文本，去除多余空白和特殊字符"""

    def invoke(self, input: Any, config: RunnableConfig = None) -> str:
        """同步调用：清洗文本"""
        if isinstance(input, dict):
            text = input.get("text", "")
        else:
            text = str(input)
        # 去除多余空白
        lines = [line.strip() for line in text.splitlines()]
        cleaned = "\n".join(line for line in lines if line)
        return cleaned

    def stream(self, input: Any, config: RunnableConfig = None) -> Iterator:
        """流式输出：默认实现为 invoke 后 yield"""
        yield self.invoke(input, config)

# 使用自定义 Runnable
cleaner = TextCleanerRunnable()

# 测试自定义 Runnable
dirty_text = """
  你好，世界！

  这是   一段   有很多   空白的   文本。

  """
cleaned = cleaner.invoke({"text": dirty_text})
print(f"清洗前长度: {len(dirty_text)}")
print(f"清洗后长度: {len(cleaned)}")
print(f"清洗结果: {repr(cleaned)}")
# 预期输出：
# 清洗前长度: 50+
# 清洗后长度: 减少
# 清洗结果: '你好，世界！\n这是   一段   有很多   空白的   文本。'

# 组合到链中
chain = (
    cleaner
    | ChatPromptTemplate.from_template("请总结以下内容：\n{text}")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

# 注意：cleaner 输出字符串，但 Prompt Template 需要字典
# 需要用 RunnableLambda 转换
from langchain_core.runnables import RunnableLambda
chain_fixed = (
    cleaner
    | RunnableLambda(lambda text: {"text": text})
    | ChatPromptTemplate.from_template("请总结以下内容：\n{text}")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

result = chain_fixed.invoke({"text": dirty_text})
print(f"\n总结结果: {result}")
```

**示例3：完整场景——Runnable 的增强方法（回退、重试、配置）**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig

# 1. with_fallbacks：主模型失败时切换到备用模型
primary_chain = (
    ChatPromptTemplate.from_template("回答：{question}")
    | ChatOpenAI(model="gpt-4o", temperature=0)
    | StrOutputParser()
)

backup_chain = (
    ChatPromptTemplate.from_template("回答：{question}")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

# 主链失败时自动切换到备用链
resilient_chain = primary_chain.with_fallbacks([backup_chain])

result = resilient_chain.invoke({"question": "什么是高可用性？"})
print(f"回退链结果: {result}")

# 2. with_retry：失败时自动重试
retry_chain = primary_chain.with_retry(
    stop_after_attempt=3,           # 最多重试3次
    wait_exponential_jitter=True,    # 指数退避 + 随机抖动
    # retry_if_exception_type=(TimeoutError, RateLimitError),  # 只重试特定异常
)

result = retry_chain.invoke({"question": "什么是重试机制？"})
print(f"重试链结果: {result}")

# 3. with_config：注入配置（tags、metadata、callbacks）
from langchain_core.callbacks import StdOutCallbackHandler

configured_chain = primary_chain.with_config(
    config=RunnableConfig(
        tags=["production", "qa-bot"],
        metadata={"version": "1.0", "owner": "ai-team"},
        callbacks=[StdOutCallbackHandler()],  # 打印执行过程
        run_name="qa_chain_v1",
    )
)

result = configured_chain.invoke({"question": "什么是可观测性？"})
print(f"配置链结果: {result}")

# 4. bind：绑定额外参数（如模型参数）
model = ChatOpenAI(model="gpt-4o-mini")
# 绑定 temperature 和 max_tokens
bound_model = model.bind(temperature=0.3, max_tokens=100)

bound_chain = ChatPromptTemplate.from_template("{q}") | bound_model | StrOutputParser()
result = bound_chain.invoke({"q": "用不超过20字介绍 LangChain"})
print(f"绑定参数结果: {result}")
# 预期输出：所有增强方法都能正常工作，回退和重试提升健壮性
```

#### 使用场景与最佳实践

**适用场景**：
- 所有 LangChain 组件的调用（invoke/stream/batch/async）
- 需要自定义处理逻辑时实现自定义 Runnable
- 生产环境需要回退、重试、配置注入等容错机制
- 需要高并发处理时使用异步方法
- 需要实时反馈时使用流式输出

**不适用场景**：
- 不需要 LangChain 抽象的极简脚本（直接用 requests 调用 API）
- 非 Python 环境（使用 LangChain JS 或其他框架）

**最佳实践**：
1. **优先使用 invoke**：简单调用用 invoke，需要实时反馈才用 stream，需要高并发才用 async
2. **自定义 Runnable 继承基类**：继承 `Runnable` 基类而不是自己实现接口，自动获得默认的 stream/batch/async 实现
3. **生产环境必须加回退和重试**：使用 `.with_fallbacks()` 和 `.with_retry()` 提升应用健壮性
4. **为链添加 tags 和 metadata**：使用 `.with_config()` 添加标签，便于 LangSmith 中筛选和分析
5. **控制 batch 并发数**：使用 `config={"max_concurrency": 5}` 控制批量处理的并发数，避免触发 API 限流

**性能建议**：
- 流式输出（stream）的首字延迟比 invoke 低 50-80%，用户体验更好
- 批量处理（batch）的吞吐量比逐个 invoke 高 2-5 倍，适合离线处理
- 异步方法（ainvoke/abatch）在高并发场景下吞吐量提升显著，但在单请求场景下与同步无差异
- 自定义 Runnable 的 invoke 方法应尽量高效，避免在其中执行阻塞操作（如同步 IO），异步场景下应实现 ainvoke

#### 常见坑点

**坑点1：在同步上下文中调用异步方法导致事件循环错误**
- **错误现象**：`RuntimeError: asyncio.run() cannot be called from a running event loop` 或 `RuntimeError: This event loop is already running`
- **根本原因**：在已经运行事件循环的环境中（如 Jupyter Notebook、FastAPI 路由函数、async 函数内部）直接调用 `asyncio.run()` 或同步调用异步方法
- **正确做法**：
  ```python
  import asyncio
  from langchain_core.prompts import ChatPromptTemplate
  from langchain_core.output_parsers import StrOutputParser
  from langchain_openai import ChatOpenAI

  chain = ChatPromptTemplate.from_template("{q}") | ChatOpenAI() | StrOutputParser()

  # ✅ 正确1：在普通 Python 脚本中使用 asyncio.run()
  def main():
      result = asyncio.run(chain.ainvoke({"q": "你好"}))
      print(result)

  # ✅ 正确2：在 async 函数中直接 await
  async def async_main():
      result = await chain.ainvoke({"q": "你好"})
      print(result)

  # ✅ 正确3：在 Jupyter 中直接 await（IPython 有内置事件循环）
  # result = await chain.ainvoke({"q": "你好"})

  # ✅ 正确4：在 FastAPI 路由中直接 await
  # @app.get("/chat")
  # async def chat(q: str):
  #     result = await chain.ainvoke({"q": q})
  #     return {"result": result}

  # ❌ 错误：在 async 函数中调用 asyncio.run()
  # async def bad():
  #     result = asyncio.run(chain.ainvoke({"q": "你好"}))  # 事件循环已在运行
  ```
- **预防措施**：了解当前运行环境是否有事件循环；在异步框架（FastAPI、aiohttp）中使用 `await` 而非 `asyncio.run()`；在普通脚本中使用 `asyncio.run()`；Jupyter 中直接 `await`

**坑点2：batch 中某个输入失败导致整个 batch 失败**
- **错误现象**：批量处理 10 个输入时，第 5 个输入导致异常，整个 batch 抛出异常，前 4 个成功的结果也丢失
- **根本原因**：`batch()` 方法默认在任何一个输入失败时抛出异常，不会部分成功。这是因为 batch 内部使用并发执行，一个异常会取消所有未完成的任务
- **正确做法**：
  ```python
  from langchain_core.runnables import RunnableConfig

  # 方式1：使用 exceptions_handler 处理单个失败
  results = chain.batch(
      inputs,
      config=RunnableConfig(
          callbacks=[],  # 可以添加回调记录失败
      ),
      # 注意：LangChain 的 batch 目前没有直接的 exceptions_handler 参数
      # 需要在自定义 Runnable 中处理，或使用以下方式
  )

  # 方式2：在链中包裹错误处理（推荐）
  from langchain_core.runnables import RunnableLambda
  from langchain_core.output_parsers import StrOutputParser

  def safe_invoke(question):
      try:
          return chain.invoke({"question": question})
      except Exception as e:
          return f"[错误: {str(e)}]"

  safe_chain = RunnableLambda(safe_invoke)
  results = safe_chain.batch(["q1", "q2", "q3"])
  # 每个结果要么是正常回答，要么是错误信息，不会整个 batch 失败

  # 方式3：逐个调用并收集结果（最简单可靠）
  results = []
  for inp in inputs:
      try:
          results.append(chain.invoke(inp))
      except Exception as e:
          results.append(f"[错误: {str(e)}]")
  ```
- **预防措施**：对于可能失败的输入，在链中添加错误处理逻辑；使用 `return_exceptions=True` 参数（如果版本支持）；重要的批量处理使用逐个调用 + try/except，确保部分失败不影响整体

---

> 💡 **深度讲解**
>
> LCEL 和 Runnable 接口是 LangChain 的灵魂。理解了这两个概念，就理解了 LangChain 的本质——它不是一个黑盒框架，而是一组标准化的、可组合的积木。
>
> LCEL 的设计借鉴了 Unix 管道和函数式编程。在 Unix 中，`cat file | grep error | sort` 将简单命令组合成复杂任务；在 LangChain 中，`prompt | model | parser` 将简单组件组合成复杂应用。这种设计的核心优势是"组合性"——每个组件只做一件事，组件之间通过标准接口连接，可以自由替换和重组。
>
> Runnable 接口是 LCEL 的基础。它定义了六种核心方法（invoke/stream/batch/ainvoke/astream/abatch），所有组件都实现了这个接口。这意味着：① 你构建的链天然支持所有执行模式，不需要额外编写代码；② 自定义组件只需实现 Runnable 接口即可融入生态；③ 统一接口使得可观测性、容错、配置等横切关注点可以统一处理。
>
> Runnable 的增强方法（with_fallbacks、with_retry、with_config、bind）是生产环境的利器。with_fallbacks 实现了"主备切换"——主模型失败时自动切换到备用模型；with_retry 实现了"自动重试"——应对 API 临时故障；with_config 实现了"配置注入"——添加 tags、metadata、callbacks 便于追踪和调试。这些方法使得基于 LCEL 构建的应用天然具备高可用性。
>
> 对于新手来说，最重要的是建立"管道思维"——不要把链当成一个神秘的黑盒，而是把它理解为数据在组件之间的流动。前一个组件的输出必须匹配后一个组件的输入，这是正确组合链的关键。同时，要善用 LangChain 提供的各种 Runnable 变体（RunnableLambda、RunnableParallel、RunnablePassthrough、RunnableBranch），它们可以解决大多数组合需求。

> **📝 精简总结**
>
> LCEL（LangChain Expression Language）通过 `|` 运算符组合 Runnable，替代旧版 Chain 类，优势是语法简洁、无限组合、自动支持流式/异步/批量/并行、类型安全、可观测性好；Runnable 是所有组件的基类协议，定义了 invoke（同步）、stream（流式）、batch（批量）、ainvoke（异步）、astream（异步流式）、abatch（异步批量）六种核心方法；Runnable 增强方法包括 with_fallbacks（回退）、with_retry（重试）、with_config（配置注入）、bind（参数绑定）；自定义 Runnable 继承基类即可获得默认实现；链本身也是 Runnable，可以继续组合；核心是理解数据流和类型匹配。

> **🎯 梯度练习题**
>
> **入门级**：
> 1. 使用 LCEL 构建 `prompt | model | parser` 基础链，分别用 invoke、stream、batch 三种方式调用
> 2. 解释 Runnable 六种核心方法的区别和适用场景
> 3. 使用 `with_retry` 为链添加重试机制，设置最多重试 3 次
>
> **进阶级**：
> 1. 实现一个自定义 Runnable，功能是统计输入文本的字数，将其组合到链中验证
> 2. 使用 `with_fallbacks` 构建主备链（GPT-4o 为主，GPT-4o-mini 为备），模拟主链失败时的切换
> 3. 使用 RunnableParallel 并行执行摘要和翻译两个子任务，然后将结果合并格式化输出
>
> **实战级**：
> 1. 构建一个完整的"文档处理链"：输入文档 → 清洗文本（自定义 Runnable）→ 并行执行摘要/关键词提取/情感分析 → 合并结果 → 格式化输出报告
> 2. 为生产环境的链添加完整的容错配置：回退（主备模型）、重试（3次指数退避）、配置（tags/metadata/callbacks），并编写测试验证容错机制
> 3. 对比 LCEL 链和旧版 LLMChain 的代码实现，列出 5 个具体差异，分析 LCEL 在可维护性、可测试性、可扩展性方面的优势

---

## 四、进阶篇：Runnable 组合与管道高级用法

### 4.1 RunnableParallel 并行执行

#### 概念解释

**正式定义**：RunnableParallel 是 LangChain 中用于并行执行多个 Runnable 的特殊 Runnable，它接收一个字典（key 为名称，value 为 Runnable），调用时并行执行所有 Runnable，将结果合并为一个字典返回。RunnableParallel 是实现 Map-Reduce、多任务并行、RAG 检索与输入传递等模式的核心组件。

**生活化比喻**：RunnableParallel 就像餐厅的后厨——一个订单进来后，多个厨师同时做菜（并行执行），凉菜师傅做凉菜、热菜师傅做热菜、汤品师傅做汤，所有菜做好后一起上桌（结果合并）。如果没有并行，就只能一个厨师做完一道再做下一道，效率低很多。

**核心价值**：将无依赖的子任务并行执行，显著减少总延迟（从串行的 N 倍延迟变为最大子任务延迟）；结果自动合并为字典，便于后续组件使用；是 RAG、多视角分析、Map-Reduce 等模式的基础。

#### 原理说明

```mermaid
graph TB
    subgraph 输入
        IN[输入数据]
    end

    subgraph RunnableParallel 并行执行
        IN --> R1[Runnable A<br/>摘要]
        IN --> R2[Runnable B<br/>翻译]
        IN --> R3[Runnable C<br/>关键词]
        R1 -->|线程1| OUT1[结果A]
        R2 -->|线程2| OUT2[结果B]
        R3 -->|线程3| OUT3[结果C]
    end

    subgraph 输出合并
        OUT1 --> MERGE[合并为字典]
        OUT2 --> MERGE
        OUT3 --> MERGE
        MERGE --> FINAL[{summary: A, translation: B, keywords: C}]
    end

    style R1 fill:#e3f2fd
    style R2 fill:#f3e5f5
    style R3 fill:#e8f5e9
```

**RunnableParallel 的核心机制**：
1. **并发执行**：使用 `concurrent.futures.ThreadPoolExecutor` 并行执行所有 Runnable
2. **结果合并**：等待所有 Runnable 完成后，将结果按 key 合并为字典
3. **输入分发**：相同的输入被传递给所有 Runnable（每个 Runnable 收到完整输入）
4. **错误传播**：任何一个 Runnable 失败，整个 RunnableParallel 失败（可通过包裹错误处理避免）
5. **流式支持**：支持流式输出，每个 Runnable 的流可以独立消费

**技术对比**：

| 维度 | 串行执行（`a | b | c`） | 并行执行（RunnableParallel） |
|------|------------------------|------------------------------|
| 执行方式 | 顺序执行，前一个输出是后一个输入 | 同时执行，所有 Runnable 收到相同输入 |
| 总延迟 | 各步骤延迟之和 | 最大步骤延迟 |
| 数据依赖 | 有依赖（链式传递） | 无依赖（独立执行） |
| 输出格式 | 单个值 | 字典（key → 结果） |
| 适用场景 | 流水线处理 | 多任务并行、Map-Reduce |

> 🎯 **面试高频考点**：RunnableParallel 如何实现并行执行？它的输入输出格式是什么？答：RunnableParallel 内部使用 ThreadPoolExecutor 并发执行所有 Runnable，每个 Runnable 收到相同的输入，执行完成后将结果按 key 合并为字典。输入是任意值（被传递给所有 Runnable），输出是 `Dict[str, Any]`。总延迟等于最慢的 Runnable 的延迟，而非所有延迟之和。

#### 代码示例

**示例1：基础——并行执行多个 LLM 任务**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI
import time

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 定义三个子链
summary_chain = ChatPromptTemplate.from_template("用3句话总结：{text}") | model | StrOutputParser()
translation_chain = ChatPromptTemplate.from_template("翻译成英文：{text}") | model | StrOutputParser()
keywords_chain = ChatPromptTemplate.from_template("提取5个关键词（逗号分隔）：{text}") | model | StrOutputParser()

# 并行执行
parallel_chain = RunnableParallel({
    "summary": summary_chain,
    "translation": translation_chain,
    "keywords": keywords_chain
})

input_text = "LangChain 是一个用于构建大语言模型应用的开源框架，提供了标准化的核心抽象和表达式语言。"

# 计时对比
start = time.time()
result = parallel_chain.invoke({"text": input_text})
parallel_time = time.time() - start

print(f"并行执行耗时: {parallel_time:.2f}秒")
print(f"摘要: {result['summary']}")
print(f"翻译: {result['translation']}")
print(f"关键词: {result['keywords']}")

# 串行对比
start = time.time()
s1 = summary_chain.invoke({"text": input_text})
s2 = translation_chain.invoke({"text": input_text})
s3 = keywords_chain.invoke({"text": input_text})
serial_time = time.time() - start
print(f"\n串行执行耗时: {serial_time:.2f}秒")
print(f"并行加速比: {serial_time/parallel_time:.2f}x")

# 预期输出：并行执行耗时约为单个任务的时间，串行约为3倍，加速比约2-3x
```

**示例2：进阶——RAG 链中的并行检索与输入传递**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI
from operator import itemgetter

# 模拟检索器
def fake_retriever(query: str) -> list:
    """模拟向量数据库检索"""
    return [
        f"[文档1] 关于'{query}'的技术原理...",
        f"[文档2] 关于'{query}'的应用案例...",
        f"[文档3] 关于'{query}'的最佳实践...",
    ]

def format_docs(docs: list) -> str:
    """格式化文档列表为字符串"""
    return "\n\n".join(docs)

# RAG 链：并行执行检索和传递原始问题
rag_chain = (
    RunnableParallel({
        "context": itemgetter("question") | RunnableLambda(fake_retriever) | RunnableLambda(format_docs),
        "question": itemgetter("question"),  # 直接传递原始问题
    })
    | ChatPromptTemplate.from_template("""
根据以下上下文回答问题。如果上下文中没有相关信息，请说"根据现有知识无法回答"。

上下文：
{context}

问题：{question}

回答：
""")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

# 调用
answer = rag_chain.invoke({"question": "什么是 RAG？"})
print(answer)
# 预期输出：根据上下文，RAG（检索增强生成）是一种...

# 更简洁的写法（RunnablePassthrough）
rag_chain_v2 = (
    RunnableParallel({
        "context": RunnableLambda(fake_retriever) | RunnableLambda(format_docs),
        "question": RunnablePassthrough(),
    })
    | ChatPromptTemplate.from_template("上下文：{context}\n\n问题：{question}\n\n回答：")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

# 注意：这种写法输入是字符串（question），不是字典
answer2 = rag_chain_v2.invoke("RAG 和微调有什么区别？")
print(answer2)
```

**示例3：完整场景——Map-Reduce 模式处理长文档**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 长文档（模拟）
long_document = """
第1章：LangChain 概述。LangChain 是一个 LLM 应用开发框架...
第2章：核心抽象。包括 Model、Prompt、Output Parser...
第3章：LCEL。表达式语言，通过 | 运算符组合组件...
第4章：RAG。检索增强生成，结合外部知识库...
第5章：Agent。自主决策和工具调用...
"""

# Map 阶段：将文档分块，对每块并行生成摘要
def split_document(doc: str) -> list:
    """将文档按章节分块"""
    chapters = [c.strip() for c in doc.split("第") if c.strip()]
    return [f"第{chap}" for chap in chapters if chap]

summary_prompt = ChatPromptTemplate.from_template("用一句话总结以下章节内容：\n{chunk}")
summary_chain = summary_prompt | model | StrOutputParser()

# Map：对每个块并行生成摘要
def map_summarize(chunks: list) -> list:
    """对所有块并行生成摘要"""
    parallel = RunnableParallel({
        f"chunk_{i}": (RunnableLambda(lambda c, idx=i: {"chunk": chunks[idx]}) | summary_chain)
        for i in range(len(chunks))
    })
    result = parallel.invoke({})
    return [result[f"chunk_{i}"] for i in range(len(chunks))]

# Reduce 阶段：合并所有摘要生成最终总结
reduce_prompt = ChatPromptTemplate.from_template("""
以下是文档各章节的摘要：
{summaries}

请生成一份完整的文档总结，涵盖所有要点。
""")

reduce_chain = reduce_prompt | model | StrOutputParser()

# 完整 Map-Reduce 链
map_reduce_chain = (
    RunnableLambda(split_document)
    | RunnableLambda(map_summarize)
    | RunnableLambda(lambda summaries: {"summaries": "\n".join(summaries)})
    | reduce_chain
)

# 执行
result = map_reduce_chain.invoke(long_document)
print("=== Map-Reduce 文档总结 ===")
print(result)
# 预期输出：涵盖所有5章要点的完整文档总结
```

#### 使用场景与最佳实践

**适用场景**：
- RAG 应用中并行执行检索和传递原始输入
- 多视角分析（同时生成摘要、翻译、关键词、情感分析）
- Map-Reduce 模式处理长文档或大量数据
- 多模型对比（同时调用多个模型比较结果）
- 无依赖子任务的并行加速

**不适用场景**：
- 有数据依赖的任务（后一个任务需要前一个的输出，必须串行）
- 任务数量极多（>50）且每个任务都是 API 调用（可能触发限流）
- 需要严格顺序执行的场景（如审批工作流）

**最佳实践**：
1. **确保子任务无依赖**：RunnableParallel 中的所有 Runnable 应相互独立，不应有数据依赖
2. **控制并行数量**：大量并行 API 调用可能触发限流，使用 `config={"max_concurrency": N}` 控制并发数
3. **错误隔离**：为每个子 Runnable 添加错误处理，避免一个失败导致全部失败
4. **结果合并后使用 itemgetter**：后续组件使用 `itemgetter("key")` 从合并字典中提取需要的字段
5. **监控并行性能**：使用 LangSmith 追踪每个子任务的耗时，识别瓶颈

**性能建议**：
- 并行执行的总延迟 = max(各子任务延迟)，而非 sum，适合 IO 密集型任务（API 调用）
- 对于 CPU 密集型任务，Python GIL 可能限制并行效果，考虑使用多进程
- 大量并行调用时注意 API 限流（Rate Limit），设置合理的 max_concurrency
- 并行结果合并需要等待所有任务完成，最慢的任务决定总延迟

#### 常见坑点

**坑点1：RunnableParallel 中一个子任务失败导致整个链失败**
- **错误现象**：并行执行3个任务时，第2个任务超时，整个 RunnableParallel 抛出异常，其他2个成功的结果也丢失
- **根本原因**：RunnableParallel 默认使用 `ThreadPoolExecutor`，任何一个 future 异常都会在获取结果时抛出，不会部分返回
- **正确做法**：
  ```python
  from langchain_core.runnables import RunnableParallel, RunnableLambda
  from langchain_core.output_parsers import StrOutputParser
  from langchain_openai import ChatOpenAI

  model = ChatOpenAI(model="gpt-4o-mini")

  # 为每个子链包裹错误处理
  def safe_chain(chain, default_value=""):
      def _invoke(input):
          try:
              return chain.invoke(input)
          except Exception as e:
              return f"[错误: {str(e)}]"
      return RunnableLambda(_invoke)

  summary_chain = safe_chain(
      ChatPromptTemplate.from_template("总结：{text}") | model | StrOutputParser()
  )
  translation_chain = safe_chain(
      ChatPromptTemplate.from_template("翻译：{text}") | model | StrOutputParser()
  )

  parallel = RunnableParallel({
      "summary": summary_chain,
      "translation": translation_chain,
  })

  result = parallel.invoke({"text": "测试文本"})
  # 即使某个子任务失败，结果中会包含错误信息而非抛出异常
  print(f"摘要: {result['summary']}")
  print(f"翻译: {result['translation']}")
  ```
- **预防措施**：生产环境中为所有并行子任务添加错误处理；使用 `return_exceptions=True`（如果版本支持）；关键任务设置超时

**坑点2：RunnableParallel 的输入被错误地分发到子 Runnable**
- **错误现象**：RunnableParallel 中的子 Runnable 收到的输入格式不正确，导致 KeyError 或类型错误
- **根本原因**：RunnableParallel 将相同的输入传递给所有子 Runnable。如果输入是字典，子 Runnable 收到完整字典；如果输入是字符串，子 Runnable 收到字符串。需要确保每个子 Runnable 能处理该输入格式
- **正确做法**：
  ```python
  from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
  from operator import itemgetter

  # ❌ 错误：子 Runnable 期望 {"text": ...} 但收到完整输入
  # parallel = RunnableParallel({
  #     "summary": summary_chain,  # summary_chain 期望 {"text": "..."}
  #     "raw": RunnablePassthrough(),
  # })
  # parallel.invoke("直接传入字符串")  # summary_chain 收到字符串而非字典

  # ✅ 正确1：使用 itemgetter 提取字段
  from langchain_core.prompts import ChatPromptTemplate
  from langchain_core.output_parsers import StrOutputParser
  from langchain_openai import ChatOpenAI

  model = ChatOpenAI(model="gpt-4o-mini")
  summary_chain = ChatPromptTemplate.from_template("总结：{text}") | model | StrOutputParser()

  parallel = RunnableParallel({
      "summary": itemgetter("text") | summary_chain,  # 先提取 text 字段
      "original": itemgetter("text"),  # 提取原始文本
  })
  result = parallel.invoke({"text": "需要总结的文本", "other": "其他字段"})
  # summary_chain 收到 {"text": "需要总结的文本"} ✅

  # ✅ 正确2：使用 RunnableLambda 转换输入格式
  parallel2 = RunnableParallel({
      "summary": RunnableLambda(lambda x: {"text": x}) | summary_chain,
      "original": RunnablePassthrough(),
  })
  result2 = parallel2.invoke("直接传入字符串")
  # RunnableLambda 将字符串转换为 {"text": 字符串} ✅
  ```
- **预防措施**：明确每个子 Runnable 的输入类型；使用 itemgetter 或 RunnableLambda 进行输入转换；在链的入口处验证输入格式

---

### 4.2 RunnableLambda 与 RunnablePassthrough

#### 概念解释

**正式定义**：RunnableLambda 是将任意 Python 可调用对象（函数、lambda、方法）包装为 Runnable 的适配器，使得自定义函数可以融入 LCEL 管道；RunnablePassthrough 是一个特殊的 Runnable，它直接将输入原样返回（或通过 `.assign()` 方法添加上下文字段），常用于传递原始输入、构建 RAG 链、合并数据流。

**生活化比喻**：RunnableLambda 就像电源转换器——你的电器（自定义函数）用的是两脚插头，而 LangChain 插座（Runnable 接口）是三脚的，RunnableLambda 就是那个转换插头，让你的电器能插上电。RunnablePassthrough 就像一根直通水管——水（数据）从这头进，那头出，不做任何处理，但你可以在水管上接一个分支（`.assign()`）来添加额外的水流（上下文字段）。

**核心价值**：RunnableLambda 使得任何 Python 函数都可以成为链的一部分，极大扩展了 LangChain 的能力边界；RunnablePassthrough 解决了"在链中传递原始输入"的常见需求，特别是在 RAG 和多分支管道中；两者都是 LCEL 管道中不可或缺的"胶水"组件。

#### 原理说明

```mermaid
graph LR
    subgraph RunnableLambda
        IN1[输入] --> WRAP[包装函数]
        WRAP --> FUNC[自定义函数<br/>def my_func(x): ...]
        FUNC --> OUT1[输出]
    end

    subgraph RunnablePassthrough
        IN2[输入] --> PASS[直接传递]
        PASS --> OUT2[输出 = 输入]
    end

    subgraph RunnablePassthrough.assign
        IN3[输入字典] --> ASSIGN[添加/更新字段]
        ASSIGN -->|保留原字段| OUT3[输出字典]
        ASSIGN -->|添加新字段| OUT3
    end

    style WRAP fill:#fff3e0
    style PASS fill:#e8f5e9
    style ASSIGN fill:#f3e5f5
```

**RunnableLambda 的核心机制**：
1. **函数包装**：将 Python 可调用对象包装为实现了 Runnable 接口的对象
2. **输入传递**：调用时将输入传递给被包装的函数
3. **同步优先**：默认使用函数的同步调用，异步时在线程池中执行
4. **配置支持**：可以接受可选的 `config` 参数（如果函数签名包含）
5. **类型推断**：根据函数的类型注解推断输入输出 schema

**RunnablePassthrough 的核心机制**：
1. **原样传递**：`invoke(x)` 返回 `x`，不做任何处理
2. **assign 方法**：`.assign(**kwargs)` 返回新的 Runnable，将 kwargs 中的字段添加到输入字典中
3. **输入要求**：assign 模式要求输入是字典，新字段的值可以是静态值或 Runnable
4. **字段覆盖**：如果新字段名与输入字典中的字段同名，会覆盖原有值

**技术对比**：

| 维度 | RunnableLambda | RunnablePassthrough |
|------|---------------|---------------------|
| 作用 | 将自定义函数包装为 Runnable | 原样传递输入（或添加上下文） |
| 输入处理 | 调用自定义函数处理 | 不处理，直接返回 |
| 典型用途 | 数据转换、格式化、自定义逻辑 | 传递原始输入、RAG 链、合并数据 |
| 灵活性 | 高（任意函数） | 低（固定行为） |
| 性能开销 | 函数调用开销 | 几乎为零 |

> 🎯 **面试高频考点**：RunnablePassthrough.assign() 的作用是什么？在 RAG 链中如何使用？答：`.assign()` 方法返回一个新的 Runnable，它将输入字典与指定的新字段合并后返回。新字段的值可以是静态值或 Runnable（会被调用并将结果作为字段值）。在 RAG 链中，常用 `RunnablePassthrough.assign(context=retriever | format_docs)` 来同时保留原始问题（question）和添加检索到的上下文（context），然后传递给 Prompt Template。

#### 代码示例

**示例1：基础——RunnableLambda 包装自定义函数**

```python
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 1. 自定义函数：文本清洗
def clean_text(text: str) -> str:
    """去除多余空白和特殊字符"""
    import re
    text = re.sub(r'\s+', ' ', text)  # 多个空白替换为单个空格
    text = text.strip()
    return text

# 包装为 Runnable
clean_runnable = RunnableLambda(clean_text)

# 测试
result = clean_runnable.invoke("  这是   一段    有很多   空白的   文本  ")
print(f"清洗结果: {repr(result)}")
# 预期输出：清洗结果: '这是 一段 有很多 空白的 文本'

# 2. 组合到链中
chain = (
    RunnableLambda(clean_text)
    | ChatPromptTemplate.from_template("请总结以下内容：\n{text}")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

# 注意：clean_text 输出字符串，但 Prompt 需要字典
# 需要转换
chain_fixed = (
    RunnableLambda(clean_text)
    | RunnableLambda(lambda text: {"text": text})
    | ChatPromptTemplate.from_template("请总结以下内容：\n{text}")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

result = chain_fixed.invoke("  LangChain   是一个    LLM 应用   开发框架  ")
print(f"总结结果: {result}")
```

**示例2：进阶——RunnablePassthrough 与 assign 用法**

```python
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from operator import itemgetter

# 1. 基本用法：原样传递
pass_through = RunnablePassthrough()
result = pass_through.invoke({"question": "你好", "user": "小明"})
print(f"Passthrough 结果: {result}")
# 预期输出：Passthrough 结果: {'question': '你好', 'user': '小明'}（原样返回）

# 2. assign：添加静态字段
pass_with_static = RunnablePassthrough.assign(
    system_prompt="你是一个友好的助手",
    language="中文"
)
result = pass_with_static.invoke({"question": "你好"})
print(f"assign 静态字段: {result}")
# 预期输出：{'question': '你好', 'system_prompt': '你是一个友好的助手', 'language': '中文'}

# 3. assign：添加动态字段（Runnable 值）
def get_timestamp(_):
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

pass_with_dynamic = RunnablePassthrough.assign(
    timestamp=RunnableLambda(get_timestamp),
    upper_question=itemgetter("question") | RunnableLambda(lambda q: q.upper())
)
result = pass_with_dynamic.invoke({"question": "hello world"})
print(f"assign 动态字段: {result}")
# 预期输出：包含 timestamp 和 upper_question 字段

# 4. RAG 链中的经典用法
def fake_retrieve(query: str) -> str:
    return f"[检索结果] 关于'{query}'的相关知识..."

rag_chain = (
    RunnablePassthrough.assign(
        context=itemgetter("question") | RunnableLambda(fake_retrieve)
    )
    # 此时输入变为 {"question": "...", "context": "..."}
    | RunnableLambda(lambda x: f"上下文：{x['context']}\n问题：{x['question']}")
)

result = rag_chain.invoke({"question": "什么是 RAG？"})
print(f"\nRAG 链结果:\n{result}")
# 预期输出：包含检索上下文和问题的格式化文本
```

**示例3：完整场景——使用 RunnableLambda 和 Passthrough 构建数据处理管道**

```python
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI
from operator import itemgetter
import json

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 数据处理函数
def parse_input(raw: str) -> dict:
    """解析原始输入为结构化数据"""
    parts = raw.split("|")
    return {
        "title": parts[0].strip() if len(parts) > 0 else "",
        "content": parts[1].strip() if len(parts) > 1 else "",
        "category": parts[2].strip() if len(parts) > 2 else "未分类",
    }

def validate_data(data: dict) -> dict:
    """验证数据完整性"""
    errors = []
    if not data.get("title"):
        errors.append("标题为空")
    if not data.get("content"):
        errors.append("内容为空")
    if len(data.get("content", "")) < 10:
        errors.append("内容过短（少于10字符）")
    return {**data, "errors": errors, "is_valid": len(errors) == 0}

# LLM 处理链
analysis_prompt = ChatPromptTemplate.from_template("""
请分析以下文章，输出 JSON 格式：
{{"summary": "摘要", "sentiment": "正面/负面/中性", "keywords": ["关键词1", "关键词2"]}}

标题：{title}
内容：{content}
分类：{category}

只输出 JSON，不要其他文字。
""")

analysis_chain = analysis_prompt | model | JsonOutputParser()

# 完整数据处理管道
pipeline = (
    # 步骤1：解析原始输入
    RunnableLambda(parse_input)
    # 步骤2：验证数据（保留原始字段，添加验证结果）
    | RunnableLambda(validate_data)
    # 步骤3：如果数据有效，并行执行 LLM 分析和传递元数据
    | RunnablePassthrough.assign(
        analysis=RunnableLambda(
            lambda data: analysis_chain.invoke(data) if data["is_valid"] else {"error": "数据无效，跳过分析"}
        )
    )
    # 步骤4：格式化最终输出
    | RunnableLambda(lambda result: json.dumps({
        "title": result["title"],
        "category": result["category"],
        "is_valid": result["is_valid"],
        "errors": result["errors"],
        "analysis": result.get("analysis", {}),
    }, ensure_ascii=False, indent=2))
)

# 测试有效数据
valid_input = "人工智能发展|人工智能正在改变各行各业，从医疗到金融，从教育到娱乐。大语言模型的突破使得自然语言处理达到了新的高度。|科技"
result1 = pipeline.invoke(valid_input)
print("=== 有效数据处理结果 ===")
print(result1)

# 测试无效数据
invalid_input = "|短|未分类"
result2 = pipeline.invoke(invalid_input)
print("\n=== 无效数据处理结果 ===")
print(result2)
# 预期输出：有效数据返回完整分析，无效数据返回错误信息
```

#### 使用场景与最佳实践

**适用场景**：
- RunnableLambda：数据转换、格式化、自定义业务逻辑、调用外部 API、非 LLM 处理步骤
- RunnablePassthrough：传递原始输入到下游、RAG 链中同时传递问题和上下文、合并多个数据流、构建分支管道
- 两者配合：复杂的数据处理管道、条件执行、错误处理

**不适用场景**：
- RunnableLambda：极其简单的操作（直接用内置组件即可）、需要异步优化的场景（RunnableLambda 的异步默认在线程池执行）
- RunnablePassthrough：不需要保留原始输入的场景（直接用转换函数即可）

**最佳实践**：
1. **使用命名函数而非 lambda**：RunnableLambda 包装命名函数，便于序列化（LangServe 部署）和调试
2. **为函数添加类型注解**：帮助 LangChain 推断输入输出 schema，提升类型安全性
3. **RunnablePassthrough.assign 用于 RAG**：这是最经典的用法，`assign(context=retriever | format_docs)` 同时保留问题和上下文
4. **使用 itemgetter 提取字段**：从字典中提取特定字段用 `operator.itemgetter`，比 lambda 更高效且可序列化
5. **保持函数纯粹**：RunnableLambda 包装的函数应是无副作用的纯函数，避免在函数中修改全局状态

**性能建议**：
- RunnableLambda 的函数调用开销很小（微秒级），不会成为性能瓶颈
- 对于 IO 密集型自定义函数，实现异步版本并使用 `RunnableLambda` 的 `func` 参数支持 async
- RunnablePassthrough 几乎零开销，可以放心使用
- 大量数据转换时，考虑使用向量化操作（如 pandas）而非逐行处理的 RunnableLambda

#### 常见坑点

**坑点1：RunnableLambda 包装的函数无法被 pickle 序列化**
- **错误现象**：使用 LangServe 部署链时报 `PicklingError: Can't pickle <function < at 0x...>`，或链无法保存到文件
- **根本原因**：Python 的 lambda 函数和闭包无法被标准 pickle 序列化，而 LangServe 部署和链的持久化需要序列化所有组件
- **正确做法**：
  ```python
  from langchain_core.runnables import RunnableLambda
  from operator import itemgetter

  # ❌ 错误：使用 lambda（无法序列化）
  # bad = RunnableLambda(lambda x: x.upper())

  # ✅ 正确1：使用命名函数
  def to_upper(text: str) -> str:
      return text.upper()
  good1 = RunnableLambda(to_upper)

  # ✅ 正确2：使用 operator 模块函数（可序列化）
  good2 = itemgetter("key")

  # ✅ 正确3：使用 functools.partial（可序列化）
  from functools import partial
  def add_n(x, n):
      return x + n
  add_5 = partial(add_n, n=5)
  good3 = RunnableLambda(add_5)

  # ✅ 正确4：使用类的方法（如果类可序列化）
  class TextProcessor:
      def clean(self, text):
          return text.strip().lower()
  processor = TextProcessor()
  good4 = RunnableLambda(processor.clean)  # 如果 processor 可序列化
  ```
- **预防措施**：在链中避免使用 lambda，改用命名函数；使用 LangServe 部署前先测试链是否可序列化（`import pickle; pickle.dumps(chain)`）；使用 `cloudpickle` 替代标准 pickle（但仍建议避免 lambda）

**坑点2：RunnablePassthrough.assign 的输入不是字典导致 AttributeError**
- **错误现象**：`AttributeError: 'str' object has no attribute 'items'` 或 `TypeError: cannot assign to ...`
- **根本原因**：`RunnablePassthrough.assign()` 要求输入必须是字典（dict），因为它需要将新字段合并到输入字典中。如果输入是字符串或其他类型，会报错
- **正确做法**：
  ```python
  from langchain_core.runnables import RunnablePassthrough, RunnableLambda

  # ❌ 错误：输入是字符串
  # chain = RunnablePassthrough.assign(new_field="value")
  # chain.invoke("字符串输入")  # 报错，字符串没有 items()

  # ✅ 正确1：确保输入是字典
  chain = RunnablePassthrough.assign(new_field="value")
  result = chain.invoke({"question": "你好"})  # ✅ 输入是字典
  print(result)  # {'question': '你好', 'new_field': 'value'}

  # ✅ 正确2：在 assign 前将输入转换为字典
  chain2 = (
      RunnableLambda(lambda text: {"input": text})  # 先转换为字典
      | RunnablePassthrough.assign(upper=lambda x: x["input"].upper())
  )
  result2 = chain2.invoke("hello")
  print(result2)  # {'input': 'hello', 'upper': 'HELLO'}

  # ✅ 正确3：使用 RunnableParallel 替代（更灵活）
  from langchain_core.runnables import RunnableParallel
  chain3 = RunnableParallel({
      "original": RunnablePassthrough(),
      "upper": RunnableLambda(lambda x: x.upper()),
  })
  result3 = chain3.invoke("hello")
  print(result3)  # {'original': 'hello', 'upper': 'HELLO'}
  ```
- **预防措施**：使用 `.assign()` 前确认输入类型是字典；在链的入口处添加输入验证；对于字符串输入，使用 RunnableParallel 而非 assign

---

### 4.3 RunnableBranch 条件分支与路由

#### 概念解释

**正式定义**：RunnableBranch 是 LangChain 中用于条件分支执行的 Runnable，它接收一个条件-分支对列表（`(condition_fn, runnable)`），调用时按顺序评估条件函数，执行第一个条件为 True 的分支，类似于 if-elif-else 结构。RunnableBranch 常用于根据输入内容动态选择处理路径，如路由到不同模型、不同提示词、不同处理流程。

**生活化比喻**：RunnableBranch 就像医院的分诊台——病人（输入）进来后，护士（条件函数）根据症状（输入特征）判断应该去哪个科室（分支）：发烧去发热门诊，心脏病去心内科，骨折去骨科。每个科室有不同的医生和处理流程（不同的 Runnable）。如果都不匹配，去全科门诊（默认分支）。

**核心价值**：实现动态路由和条件执行，根据输入特征选择最优处理路径；避免对所有输入使用相同的处理流程，提升效率和质量；是 RouterChain、模型路由、分类处理等模式的基础。

#### 原理说明

```mermaid
graph TB
    subgraph 输入
        IN[输入数据]
    end

    subgraph RunnableBranch 条件分支
        IN --> C1{条件1?<br/>是否为技术问题?}
        C1 -->|是| B1[分支1<br/>技术专家链]
        C1 -->|否| C2{条件2?<br/>是否为客服问题?}
        C2 -->|是| B2[分支2<br/>客服链]
        C2 -->|否| C3{条件3?<br/>是否为闲聊?}
        C3 -->|是| B3[分支3<br/>闲聊链]
        C3 -->|否| DEFAULT[默认分支<br/>通用链]
    end

    subgraph 输出
        B1 --> OUT[分支结果]
        B2 --> OUT
        B3 --> OUT
        DEFAULT --> OUT
    end

    style C1 fill:#fff3e0
    style C2 fill:#fff3e0
    style C3 fill:#fff3e0
    style B1 fill:#e3f2fd
    style B2 fill:#f3e5f5
    style B3 fill:#e8f5e9
```

**RunnableBranch 的核心机制**：
1. **顺序评估**：按列表顺序评估条件函数，第一个返回 True 的条件对应的分支被执行
2. **条件函数**：条件函数接收输入，返回布尔值（True/False）
3. **默认分支**：最后一个分支通常是默认分支（条件始终为 True），处理所有未匹配的情况
4. **短路执行**：一旦某个条件匹配，后续条件不再评估（类似 if-elif 的短路）
5. **输入传递**：匹配的分支收到完整的输入

**技术对比**：

| 维度 | RunnableBranch | 条件边（LangGraph） | if-else（Python） |
|------|---------------|---------------------|-------------------|
| 适用场景 | LCEL 管道内的分支 | 状态机中的节点路由 | 普通 Python 代码 |
| 可组合性 | 是（Runnable） | 是（图的一部分） | 否（不能直接组合） |
| 流式支持 | 是 | 是 | 否 |
| 可观测性 | 自动追踪 | 自动追踪 | 需手动埋点 |
| 复杂度 | 简单分支 | 复杂循环和分支 | 任意逻辑 |

> 🎯 **面试高频考点**：RunnableBranch 和 LangGraph 条件边的区别是什么？答：RunnableBranch 是 LCEL 管道中的条件分支，用于在链中根据输入选择不同的处理路径，是无状态的、一次性的分支决策；LangGraph 条件边是状态机中的动态路由，用于在图执行中根据当前状态决定下一个节点，支持循环、持久化和复杂状态管理。简单的一次性分支用 RunnableBranch，复杂的有状态流程（需要循环、持久化、HITL）用 LangGraph 条件边。

#### 代码示例

**示例1：基础——根据问题类型路由到不同专家**

```python
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 定义各专家链
tech_chain = (
    ChatPromptTemplate.from_template("你是技术专家。请用专业术语回答：{question}")
    | model | StrOutputParser()
)
customer_chain = (
    ChatPromptTemplate.from_template("你是客服代表。请用友好耐心的语气回答：{question}")
    | model | StrOutputParser()
)
casual_chain = (
    ChatPromptTemplate.from_template("你是聊天伙伴。请用轻松幽默的语气回答：{question}")
    | model | StrOutputParser()
)

# 条件函数
def is_tech_question(input: dict) -> bool:
    keywords = ["编程", "代码", "技术", "软件", "系统", "数据库", "API", "bug"]
    return any(kw in input["question"] for kw in keywords)

def is_customer_question(input: dict) -> bool:
    keywords = ["退款", "退货", "订单", "物流", "发票", "投诉", "售后", "客服"]
    return any(kw in input["question"] for kw in keywords)

def is_casual_question(input: dict) -> bool:
    keywords = ["你好", "在吗", "聊", "天气", "笑话", "故事", "兴趣"]
    return any(kw in input["question"] for kw in keywords)

# 构建分支
branch = RunnableBranch(
    (is_tech_question, tech_chain),
    (is_customer_question, customer_chain),
    (is_casual_question, casual_chain),
    RunnablePassthrough() | RunnableLambda(lambda x: f"无法分类的问题：{x['question']}"),  # 默认分支
)

# 测试
questions = [
    {"question": "如何用 Python 实现快速排序？"},
    {"question": "我的订单什么时候能到货？"},
    {"question": "你好，今天天气怎么样？"},
    {"question": "请推荐一本书"},
]

for q in questions:
    result = branch.invoke(q)
    print(f"Q: {q['question']}")
    print(f"A: {result[:100]}...")
    print()

# 预期输出：技术问题由技术专家回答，客服问题由客服回答，闲聊由聊天伙伴回答，未分类走默认分支
```

**示例2：进阶——根据输入复杂度路由到不同模型**

```python
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 大模型（复杂任务）
strong_model = ChatOpenAI(model="gpt-4o", temperature=0)
# 小模型（简单任务）
fast_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_template("{question}")
strong_chain = prompt | strong_model | StrOutputParser()
fast_chain = prompt | fast_model | StrOutputParser()

# 条件：判断问题复杂度
def is_complex(input: dict) -> bool:
    """判断问题是否复杂（需要大模型）"""
    q = input["question"]
    # 简单启发式：长问题、包含复杂关键词的问题用大模型
    complex_keywords = ["分析", "设计", "架构", "优化", "对比", "解释为什么", "如何实现", "详细"]
    if len(q) > 100:
        return True
    return any(kw in q for kw in complex_keywords)

# 模型路由分支
model_router = RunnableBranch(
    (is_complex, strong_chain),    # 复杂问题 → 大模型
    fast_chain,                      # 简单问题 → 小模型（默认分支）
)

# 测试
test_cases = [
    {"question": "1+1等于几？"},  # 简单 → 小模型
    {"question": "请详细分析微服务架构和单体架构的优缺点，并给出迁移策略"},  # 复杂 → 大模型
    {"question": "今天星期几？"},  # 简单 → 小模型
    {"question": "如何设计一个高并发的秒杀系统？请给出完整的架构设计和技术选型"},  # 复杂 → 大模型
]

for tc in test_cases:
    result = model_router.invoke(tc)
    model_used = "GPT-4o（大模型）" if is_complex(tc) else "GPT-4o-mini（小模型）"
    print(f"问题: {tc['question'][:50]}...")
    print(f"路由到: {model_used}")
    print(f"回答: {result[:80]}...")
    print()

# 预期输出：简单问题用小模型（快速、低成本），复杂问题用大模型（高质量）
```

**示例3：完整场景——多级路由与分支嵌套**

```python
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough, RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI
import json

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 一级分类：判断问题大类
def classify_category(input: dict) -> str:
    """使用 LLM 分类问题类别"""
    classification_prompt = ChatPromptTemplate.from_template("""
    请将以下问题分类为：技术、客服、闲聊、其他。只输出类别名称。
    问题：{question}
    """)
    chain = classification_prompt | model | StrOutputParser()
    result = chain.invoke(input)
    return result.strip()

# 技术问题的二级路由
tech_branch = RunnableBranch(
    (lambda x: "编程" in x["question"] or "代码" in x["question"],
     ChatPromptTemplate.from_template("你是编程专家。回答：{question}") | model | StrOutputParser()),
    (lambda x: "数据库" in x["question"] or "SQL" in x["question"],
     ChatPromptTemplate.from_template("你是数据库专家。回答：{question}") | model | StrOutputParser()),
    ChatPromptTemplate.from_template("你是通用技术专家。回答：{question}") | model | StrOutputParser(),
)

# 客服问题的二级路由
customer_branch = RunnableBranch(
    (lambda x: "退款" in x["question"] or "退货" in x["question"],
     ChatPromptTemplate.from_template("你是退款专员。回答：{question}") | model | StrOutputParser()),
    (lambda x: "物流" in x["question"] or "快递" in x["question"],
     ChatPromptTemplate.from_template("你是物流专员。回答：{question}") | model | StrOutputParser()),
    ChatPromptTemplate.from_template("你是客服主管。回答：{question}") | model | StrOutputParser(),
)

# 一级路由
main_branch = RunnableBranch(
    (lambda x: classify_category(x) == "技术", tech_branch),
    (lambda x: classify_category(x) == "客服", customer_branch),
    (lambda x: classify_category(x) == "闲聊",
     ChatPromptTemplate.from_template("你是聊天伙伴。回答：{question}") | model | StrOutputParser()),
    ChatPromptTemplate.from_template("你是通用助手。回答：{question}") | model | StrOutputParser(),
)

# 测试多级路由
test_cases = [
    {"question": "Python 中如何处理异常？"},
    {"question": "我想退款，应该怎么操作？"},
    {"question": "你喜欢什么电影？"},
    {"question": "MySQL 中索引的原理是什么？"},
]

for tc in test_cases:
    category = classify_category(tc)
    result = main_branch.invoke(tc)
    print(f"问题: {tc['question']}")
    print(f"一级分类: {category}")
    print(f"回答: {result[:100]}...")
    print()

# 预期输出：技术问题进入 tech_branch 再二级路由，客服问题进入 customer_branch 再二级路由
```

#### 使用场景与最佳实践

**适用场景**：
- 根据输入内容路由到不同专家/模型/提示词
- 简单的条件分支处理（if-elif-else 逻辑）
- 模型路由（简单问题用小模型，复杂问题用大模型）
- 分类处理（不同类别的输入走不同处理流程）
- 错误恢复（主流程失败时走备用流程）

**不适用场景**：
- 需要循环执行的复杂流程（用 LangGraph）
- 需要状态持久化和中断恢复的场景（用 LangGraph）
- 条件判断本身需要复杂的状态管理（用 LangGraph）
- 超过 3-4 层的嵌套分支（代码可读性差，考虑用 LangGraph 或重构）

**最佳实践**：
1. **始终提供默认分支**：最后一个分支应为默认分支（条件始终为 True），处理所有未匹配的输入
2. **条件函数保持简单**：条件判断应快速且无副作用，避免在条件函数中调用 LLM（会增加延迟）
3. **使用 LLM 分类时缓存结果**：如果条件判断需要 LLM 分类，将分类结果存入输入字典，避免重复调用
4. **控制分支数量**：超过 5 个分支时考虑使用字典映射 + 动态查找，而非长长的分支列表
5. **为每个分支添加标签**：使用 `.with_config(tags=["branch_tech"])` 为分支添加标签，便于 LangSmith 追踪

**性能建议**：
- 条件函数应是 O(1) 或 O(n) 的简单检查（关键词匹配、长度判断），避免耗时操作
- 如果条件判断需要 LLM 调用，考虑将分类和处理合并为一个 LLM 调用（让模型同时输出分类和回答）
- 分支中的 Runnable 可以复用相同的模型实例，避免重复创建
- 对于高频路由，考虑使用缓存（相同输入路由到相同分支）

#### 常见坑点

**坑点1：RunnableBranch 的条件函数收到的输入类型不匹配**
- **错误现象**：`KeyError: 'question'` 或 `TypeError: string indices must be integers`
- **根本原因**：条件函数假设输入是字典（如 `input["question"]`），但实际传入的是字符串或其他类型；或者输入字典中缺少条件函数访问的字段
- **正确做法**：
  ```python
  from langchain_core.runnables import RunnableBranch, RunnableLambda

  # ❌ 错误：条件函数假设输入有 question 字段
  # def condition(x):
  #     return "技术" in x["question"]  # 如果 x 是字符串会报错

  # ✅ 正确1：条件函数中处理不同类型
  def condition(x):
      if isinstance(x, dict):
          return "技术" in x.get("question", "")
      elif isinstance(x, str):
          return "技术" in x
      return False

  # ✅ 正确2：在分支前统一输入格式
  normalize = RunnableLambda(lambda x: {"question": x} if isinstance(x, str) else x)
  branch = normalize | RunnableBranch(
      (lambda x: "技术" in x["question"], tech_chain),
      default_chain,
  )

  # ✅ 正确3：使用 TypedDict 定义输入类型并验证
  from typing import TypedDict
  class InputType(TypedDict):
      question: str

  def condition(x: InputType) -> bool:
      return "技术" in x["question"]
  ```
- **预防措施**：在链的入口处验证输入格式；条件函数中添加类型检查；使用 TypedDict/Pydantic 定义输入类型

**坑点2：RunnableBranch 中条件函数调用 LLM 导致重复调用和延迟增加**
- **错误现象**：每次分支执行都调用两次 LLM（一次分类，一次回答），延迟是预期的两倍，成本也翻倍
- **根本原因**：条件函数中调用了 LLM 进行分类，而分支中的 Runnable 又调用了一次 LLM 进行回答，导致重复调用
- **正确做法**：
  ```python
  from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough
  from langchain_core.prompts import ChatPromptTemplate
  from langchain_core.output_parsers import StrOutputParser
  from langchain_openai import ChatOpenAI

  model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

  # ❌ 错误：条件函数中调用 LLM
  # def is_tech(x):
  #     result = model.invoke(f"判断以下问题是否为技术问题：{x['question']}。回答是或否")
  #     return "是" in result.content
  # branch = RunnableBranch((is_tech, tech_chain), default_chain)
  # # 每次调用：1次分类 LLM + 1次回答 LLM = 2次

  # ✅ 正确1：使用简单关键词匹配（无 LLM 调用）
  def is_tech(x):
      keywords = ["编程", "代码", "技术", "软件", "系统", "数据库"]
      return any(kw in x["question"] for kw in keywords)

  # ✅ 正确2：一次 LLM 调用同时输出分类和回答
  classify_and_answer_prompt = ChatPromptTemplate.from_template("""
  请先判断问题类别（技术/客服/闲聊），然后给出回答。
  输出格式：
  类别：[类别]
  回答：[回答内容]

  问题：{question}
  """)
  chain = classify_and_answer_prompt | model | StrOutputParser()
  # 每次调用只需 1 次 LLM

  # ✅ 正确3：先分类并缓存结果，再路由（如果分类逻辑复杂）
  def classify(x):
      result = model.invoke(f"分类：{x['question']}。只输出类别。")
      return {**x, "category": result.content.strip()}

  classify_then_branch = (
      RunnableLambda(classify)
      | RunnableBranch(
          (lambda x: x["category"] == "技术", tech_chain),
          (lambda x: x["category"] == "客服", customer_chain),
          default_chain,
      )
  )
  # 分类结果缓存在 x["category"] 中，条件函数直接读取，不重复调用 LLM
  ```
- **预防措施**：条件函数中避免 LLM 调用，使用简单规则匹配；如果必须用 LLM 分类，先分类并缓存结果，条件函数读取缓存；考虑将分类和回答合并为一次 LLM 调用

---

> 💡 **深度讲解**
>
> Runnable 组合是 LCEL 的精髓所在。掌握了 RunnableParallel、RunnableLambda、RunnablePassthrough、RunnableBranch 这四个组合工具，你就可以构建出任意复杂度的 LLM 应用管道。
>
> RunnableParallel 是性能优化的利器——它将无依赖的子任务并行执行，总延迟从 sum 变为 max。在 RAG 应用中，检索文档和传递原始问题可以并行执行；在多视角分析中，摘要、翻译、关键词提取可以同时进行。但要注意，并行执行不适用于有数据依赖的任务，也不适用于任务数量极多的场景（可能触发 API 限流）。
>
> RunnableLambda 和 RunnablePassthrough 是管道中的"胶水"——RunnableLambda 让任意 Python 函数都能成为链的一部分，RunnablePassthrough 解决了"传递原始输入"的常见需求。特别是 `RunnablePassthrough.assign()` 方法，它是 RAG 链的经典写法——`assign(context=retriever | format_docs)` 同时保留原始问题和添加检索上下文，然后一起传递给 Prompt Template。
>
> RunnableBranch 实现了条件分支和动态路由。它类似于 if-elif-else 结构，根据输入特征选择不同的处理路径。常见用途包括：根据问题类型路由到不同专家、根据复杂度路由到不同模型、根据分类结果走不同处理流程。但要注意，RunnableBranch 适用于简单的一次性分支，如果需要循环、持久化、复杂状态管理，应该使用 LangGraph 的条件边。
>
> 这四个组合工具的设计哲学是"小而美"——每个工具只做一件事，但组合起来可以构建任意复杂度的管道。这正是 Unix 哲学在 LLM 应用开发中的体现——Write programs that do one thing and do it well. Write programs to work together.

> **📝 精简总结**
>
> RunnableParallel 并行执行多个 Runnable，使用 ThreadPoolExecutor 并发，总延迟=max(各子任务)，输出为字典，适用于 RAG、多视角分析、Map-Reduce；RunnableLambda 将任意 Python 函数包装为 Runnable，使用命名函数而非 lambda 以支持序列化；RunnablePassthrough 原样传递输入，`.assign()` 方法添加上下文字段，是 RAG 链的经典写法；RunnableBranch 实现条件分支（if-elif-else），按顺序评估条件，执行第一个匹配的分支，始终提供默认分支，适用于动态路由和模型路由；复杂有状态流程应使用 LangGraph 而非 RunnableBranch。

> **🎯 梯度练习题**
>
> **入门级**：
> 1. 使用 RunnableParallel 并行执行摘要和翻译两个任务，对比串行和并行的耗时
> 2. 使用 RunnableLambda 包装一个文本统计函数（字数、句子数），组合到链中
> 3. 使用 RunnablePassthrough.assign() 为输入添加时间戳字段，验证输出包含原始字段和新字段
>
> **进阶级**：
> 1. 构建一个 RAG 链，使用 RunnablePassthrough.assign() 同时传递问题和检索上下文，使用 RunnableParallel 并行执行多个检索器
> 2. 使用 RunnableBranch 实现模型路由：简单问题用 gpt-4o-mini，复杂问题用 gpt-4o，定义合理的复杂度判断规则
> 3. 实现 Map-Reduce 模式：将长文档分块，并行生成每块摘要，然后合并为最终总结
>
> **实战级**：
> 1. 构建一个完整的"智能客服路由系统"：一级路由（技术/客服/闲聊）→ 二级路由（具体领域）→ 专家回答，使用 RunnableBranch 嵌套实现，并添加错误处理和默认分支
> 2. 为一个数据处理管道添加完整的容错机制：每个并行子任务包裹错误处理，使用 RunnableBranch 在数据无效时走备用流程，验证部分失败不影响整体
> 3. 对比 RunnableBranch 和 LangGraph 条件边的适用场景，分别用两种方式实现同一个"审批工作流"（申请→审批→通过/拒绝→执行），分析各自的优劣

---

## 五、进阶篇：Chain 类型与记忆系统

### 5.1 传统 Chain 类型与 LCEL 迁移

#### 概念解释

**正式定义**：传统 Chain 类型是 LangChain 早期版本中用于组合组件的类，包括 LLMChain（Prompt + LLM）、RouterChain（路由链）、SequentialChain（顺序链）、TransformChain（转换链）等。这些 Chain 类继承自 `Chain` 基类，通过 `run()` 方法执行。LCEL（表达式语言）出现后，这些传统 Chain 类已被弃用，推荐使用 `|` 运算符组合 Runnable。

**生活化比喻**：传统 Chain 类就像预制菜——每种菜（Chain 类型）都是预先配好的，你只能选择现成的菜品，不能自由搭配。LCEL 就像自助餐——你可以自由选择各种食材（Runnable），自己组合成想要的菜品（链）。预制菜方便但不灵活，自助餐灵活但需要自己搭配。

**核心价值**：了解传统 Chain 类型有助于阅读和维护旧代码；掌握从传统 Chain 到 LCEL 的迁移方法是升级现有项目的关键；理解两者的对应关系可以帮助你在遇到旧代码时快速理解其逻辑并用 LCEL 重写。

#### 原理说明

```mermaid
graph TB
    subgraph 传统 Chain 类（已弃用）
        LLMChain[LLMChain<br/>Prompt + LLM]
        RouterChain[RouterChain<br/>路由选择]
        SequentialChain[SequentialChain<br/>顺序执行]
        TransformChain[TransformChain<br/>数据转换]
        SimpleSequentialChain[SimpleSequentialChain<br/>简单顺序]
    end

    subgraph LCEL 替代方案（推荐）
        PIPE1[prompt | model | parser]
        PIPE2[RunnableBranch]
        PIPE3[chain1 | chain2 | chain3]
        PIPE4[RunnableLambda]
        PIPE5[RunnableSequence]
    end

    LLMChain -->|迁移到| PIPE1
    RouterChain -->|迁移到| PIPE2
    SequentialChain -->|迁移到| PIPE3
    TransformChain -->|迁移到| PIPE4
    SimpleSequentialChain -->|迁移到| PIPE5

    style LLMChain fill:#ffebee
    style RouterChain fill:#ffebee
    style SequentialChain fill:#ffebee
    style PIPE1 fill:#e8f5e9
    style PIPE2 fill:#e8f5e9
    style PIPE3 fill:#e8f5e9
```

**传统 Chain 类型与 LCEL 对应关系**：

| 传统 Chain 类 | 用途 | LCEL 替代方案 | 迁移难度 |
|--------------|------|--------------|---------|
| **LLMChain** | Prompt + LLM 组合 | `prompt | model` 或 `prompt | model | parser` | 低 |
| **SimpleSequentialChain** | 简单顺序执行 | `chain1 | chain2 | chain3` | 低 |
| **SequentialChain** | 多输入输出顺序链 | `RunnableParallel` + `|` 组合 | 中 |
| **RouterChain** | 路由选择 | `RunnableBranch` | 中 |
| **TransformChain** | 数据转换 | `RunnableLambda` | 低 |
| **ConstitutionalChain** | 宪法原则审查 | 自定义链 + `RunnableLambda` | 高 |
| **MathChain** | 数学计算 | `LLMMathChain` 或自定义 Tool | 中 |
| **SQLDatabaseChain** | SQL 查询 | `SQLDatabase` + 自定义链 | 中 |

> 🎯 **面试高频考点**：LLMChain 和 LCEL 链的区别是什么？为什么推荐使用 LCEL？答：LLMChain 是传统的 Chain 类，将 Prompt Template 和 LLM 封装在一起，通过 `run()` 方法执行，输入输出格式固定，不支持流式/异步/批量等高级特性。LCEL 链使用 `|` 运算符组合任意 Runnable，输入输出类型灵活，自动支持流式/异步/批量/并行/回退/重试。推荐使用 LCEL 因为：① 更灵活（任意组合）；② 更强大（自动支持高级特性）；③ 更易维护（组件可独立替换）；④ 传统 Chain 类已被弃用。

#### 代码示例

**示例1：基础——LLMChain 到 LCEL 的迁移**

```python
# ========== 旧版：LLMChain（已弃用）==========
# from langchain.chains import LLMChain
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI
#
# prompt = ChatPromptTemplate.from_template("用一句话解释：{topic}")
# model = ChatOpenAI(model="gpt-4o-mini")
# chain = LLMChain(llm=model, prompt=prompt)
# result = chain.run(topic="LangChain")  # 旧版用 run()
# print(result)

# ========== 新版：LCEL（推荐）==========
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template("用一句话解释：{topic}")
model = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

# LCEL 链
chain = prompt | model | parser

# 调用（用 invoke 而非 run）
result = chain.invoke({"topic": "LangChain"})
print(result)
# 预期输出：LangChain 是一个用于构建大语言模型应用的开源框架...

# 优势：自动支持流式
for chunk in chain.stream({"topic": "LCEL"}):
    print(chunk, end="", flush=True)
print()

# 优势：自动支持批量
results = chain.batch([{"topic": "RAG"}, {"topic": "Agent"}, {"topic": "Prompt"}])
for r in results:
    print(r)
```

**示例2：进阶——SequentialChain 到 LCEL 的迁移**

```python
# ========== 旧版：SequentialChain（已弃用）==========
# from langchain.chains import SequentialChain, LLMChain
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI
#
# model = ChatOpenAI(model="gpt-4o-mini")
#
# # 链1：生成大纲
# outline_prompt = ChatPromptTemplate.from_template("为主题'{topic}'生成文章大纲")
# outline_chain = LLMChain(llm=model, prompt=outline_prompt, output_key="outline")
#
# # 链2：根据大纲写文章
# article_prompt = ChatPromptTemplate.from_template("根据大纲写文章：\n{outline}")
# article_chain = LLMChain(llm=model, prompt=article_prompt, output_key="article")
#
# # 顺序链
# overall_chain = SequentialChain(
#     chains=[outline_chain, article_chain],
#     input_variables=["topic"],
#     output_variables=["outline", "article"],
# )
# result = overall_chain({"topic": "人工智能"})

# ========== 新版：LCEL（推荐）==========
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI
from operator import itemgetter

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 链1：生成大纲
outline_chain = (
    ChatPromptTemplate.from_template("为主题'{topic}'生成文章大纲（3-5个要点）")
    | model | StrOutputParser()
)

# 链2：根据大纲写文章
article_chain = (
    ChatPromptTemplate.from_template("根据以下大纲写一篇300字的文章：\n{outline}")
    | model | StrOutputParser()
)

# 方式1：简单顺序链（前一个输出作为后一个输入）
simple_chain = outline_chain | article_chain
# 注意：outline_chain 输出字符串，但 article_chain 的 Prompt 需要 {"outline": ...}
# 需要转换

# 方式2：使用 RunnablePassthrough.assign 保留中间结果
full_chain = (
    RunnablePassthrough.assign(outline=outline_chain)
    | RunnablePassthrough.assign(article=itemgetter("outline") | article_chain)
)

result = full_chain.invoke({"topic": "人工智能的未来"})
print(f"主题: {result['topic']}")
print(f"\n大纲:\n{result['outline']}")
print(f"\n文章:\n{result['article']}")
# 预期输出：包含大纲和文章的完整结果，中间结果被保留
```

**示例3：完整场景——RouterChain 到 RunnableBranch 的迁移**

```python
# ========== 旧版：RouterChain（已弃用）==========
# from langchain.chains.router import MultiPromptChain
# from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
# from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
# ... 复杂的设置代码 ...

# ========== 新版：RunnableBranch（推荐）==========
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 定义各领域专家提示词
physics_template = "你是物理教授。请用物理原理解释：{input}"
math_template = "你是数学教授。请用数学公式推导：{input}"
history_template = "你是历史教授。请用历史背景解释：{input}"
computer_template = "你是计算机教授。请用技术术语解释：{input}"

# 创建各专家链
physics_chain = ChatPromptTemplate.from_template(physics_template) | model | StrOutputParser()
math_chain = ChatPromptTemplate.from_template(math_template) | model | StrOutputParser()
history_chain = ChatPromptTemplate.from_template(history_template) | model | StrOutputParser()
computer_chain = ChatPromptTemplate.from_template(computer_template) | model | StrOutputParser()

# 分类函数（简单关键词匹配）
def is_physics(x): return any(w in x["input"] for w in ["物理", "力", "能量", "运动", "电磁"])
def is_math(x): return any(w in x["input"] for w in ["数学", "方程", "积分", "导数", "概率"])
def is_history(x): return any(w in x["input"] for w in ["历史", "朝代", "战争", "革命", "古代"])
def is_computer(x): return any(w in x["input"] for w in ["计算机", "编程", "算法", "代码", "软件"])

# 构建路由分支
router_branch = RunnableBranch(
    (is_physics, physics_chain),
    (is_math, math_chain),
    (is_history, history_chain),
    (is_computer, computer_chain),
    ChatPromptTemplate.from_template("你是通用教授。请解释：{input}") | model | StrOutputParser(),
)

# 测试
questions = [
    {"input": "什么是量子力学？"},
    {"input": "如何求解一元二次方程？"},
    {"input": "法国大革命的原因是什么？"},
    {"input": "什么是快速排序算法？"},
    {"input": "今天天气怎么样？"},
]

for q in questions:
    result = router_branch.invoke(q)
    print(f"Q: {q['input']}")
    print(f"A: {result[:100]}...")
    print()
# 预期输出：每个问题被路由到对应的专家链，未匹配的走通用教授
```

#### 使用场景与最佳实践

**适用场景**：
- 维护和升级使用传统 Chain 类的旧项目
- 阅读旧版 LangChain 教程和代码示例
- 将旧版 Chain 逐步迁移到 LCEL
- 理解 LangChain 的演进历史和设计决策

**不适用场景**：
- 新项目（直接使用 LCEL，不要使用已弃用的 Chain 类）
- 需要流式、异步、批量等高级特性的场景（传统 Chain 不支持）

**最佳实践**：
1. **新项目一律使用 LCEL**：不要使用 LLMChain、SequentialChain 等已弃用的类
2. **旧项目逐步迁移**：不要一次性重写，逐个 Chain 迁移到 LCEL，每步验证功能
3. **使用自动化工具辅助迁移**：LangChain 提供了 `chain.to_runnable()` 方法可以将部分旧 Chain 转换为 Runnable
4. **保留旧代码的测试**：迁移前确保有测试覆盖，迁移后对比输出一致性
5. **关注弃用警告**：运行代码时注意 DeprecationWarning，及时处理

**性能建议**：
- LCEL 链的性能与传统 Chain 相当或更好（减少了封装开销）
- 迁移到 LCEL 后可以利用流式和并行特性进一步提升性能
- 批量处理使用 `.batch()` 方法，传统 Chain 不支持批量

#### 常见坑点

**坑点1：旧代码中使用 `chain.run()` 方法在新版中报错**
- **错误现象**：`AttributeError: 'RunnableSequence' object has no attribute 'run'` 或 `DeprecationWarning: The method `run` was deprecated`
- **根本原因**：`run()` 是传统 Chain 类的方法，LCEL 链使用 `invoke()` 方法。如果代码从旧版迁移但未修改调用方式，会报错
- **正确做法**：
  ```python
  # ❌ 旧版写法
  # result = chain.run(topic="LangChain")
  # result = chain.run("LangChain")  # 位置参数

  # ✅ 新版写法
  result = chain.invoke({"topic": "LangChain"})  # 字典参数

  # 如果需要字符串输出（旧版 run 默认返回字符串）
  from langchain_core.output_parsers import StrOutputParser
  chain = prompt | model | StrOutputParser()  # 添加 Output Parser
  result = chain.invoke({"topic": "LangChain"})  # 返回字符串

  # 流式输出（旧版 run 不支持）
  for chunk in chain.stream({"topic": "LangChain"}):
      print(chunk, end="", flush=True)
  ```
- **预防措施**：迁移时全局搜索 `.run(` 替换为 `.invoke(`；确保链末尾有 StrOutputParser 以返回字符串；使用 IDE 的重构功能批量替换

**坑点2：SequentialChain 的多输入输出在 LCEL 中处理不当导致数据丢失**
- **错误现象**：迁移 SequentialChain 到 LCEL 后，某些中间结果或输入变量丢失，后续步骤报 KeyError
- **根本原因**：SequentialChain 通过 `input_variables` 和 `output_variables` 管理多变量传递，而 LCEL 的 `|` 运算符默认只传递前一个的输出。如果简单地用 `chain1 | chain2`，chain1 的输出会覆盖原始输入，导致后续步骤无法访问原始变量
- **正确做法**：
  ```python
  from langchain_core.runnables import RunnablePassthrough
  from operator import itemgetter

  # ❌ 错误：简单链式组合，原始输入被覆盖
  # bad_chain = outline_chain | article_chain
  # # outline_chain 输出字符串，article_chain 收到字符串而非 {"outline": ...}

  # ✅ 正确1：使用 RunnablePassthrough.assign 保留所有变量
  good_chain = (
      RunnablePassthrough.assign(outline=outline_chain)
      | RunnablePassthrough.assign(article=itemgetter("outline") | article_chain)
  )
  # 每一步都保留原始输入和新增字段，所有变量都可访问

  # ✅ 正确2：使用 RunnableParallel 显式管理输入
  from langchain_core.runnables import RunnableParallel
  good_chain2 = (
      RunnableParallel({
          "topic": itemgetter("topic"),
          "outline": itemgetter("topic") | outline_chain,
      })
      | RunnableParallel({
          "topic": itemgetter("topic"),
          "outline": itemgetter("outline"),
          "article": itemgetter("outline") | article_chain,
      })
  )

  # ✅ 正确3：自定义函数管理状态（适合复杂场景）
  def generate_outline(state):
      outline = outline_chain.invoke({"topic": state["topic"]})
      return {**state, "outline": outline}

  def generate_article(state):
      article = article_chain.invoke({"outline": state["outline"]})
      return {**state, "article": article}

  from langchain_core.runnables import RunnableLambda
  good_chain3 = RunnableLambda(generate_outline) | RunnableLambda(generate_article)
  ```
- **预防措施**：迁移 SequentialChain 时，画出变量流转图，明确每个步骤需要哪些输入、产生哪些输出；使用 RunnablePassthrough.assign 保留中间结果；测试每个步骤的输入输出是否符合预期

---

### 5.2 记忆系统 Memory

#### 概念解释

**正式定义**：Memory（记忆）是 LangChain 中用于存储和检索对话历史的组件，使得 LLM 应用可以在多轮对话中记住之前的交互内容。主要包括 ConversationBufferMemory（完整缓冲）、ConversationSummaryMemory（摘要记忆）、ConversationBufferWindowMemory（窗口记忆）、ConversationSummaryBufferMemory（摘要+缓冲）、ConversationKGMemory（知识图谱记忆）、EntityMemory（实体记忆）等。在 LCEL 中，记忆通常通过 MessagesPlaceholder 和自定义 Runnable 实现。

**生活化比喻**：Memory 就像人类的短期记忆——对话时你能记住之前聊过什么，所以对方说"我刚才提到的那个问题"时你能理解。ConversationBufferMemory 就像逐字记录的笔记本（记住所有对话），ConversationSummaryMemory 就像写了摘要的笔记本（只记住要点），ConversationBufferWindowMemory 就像只能翻最近几页的笔记本（只记住最近几轮）。

**核心价值**：使 LLM 应用具备多轮对话能力，理解上下文和指代关系；不同记忆策略在记忆完整性和 Token 消耗之间取得平衡；是构建对话机器人、客服系统、个人助手等应用的基础。

#### 原理说明

```mermaid
graph TB
    subgraph 记忆系统工作流程
        U[用户输入] --> LOAD[加载记忆<br/>load_memory_variables]
        LOAD --> PROMPT[构建 Prompt<br/>注入历史消息]
        PROMPT --> LLM[调用 LLM]
        LLM --> RESP[生成回复]
        RESP --> SAVE[保存记忆<br/>save_context]
        SAVE --> OUT[返回回复]
    end

    subgraph 记忆类型
        BUFFER[ConversationBufferMemory<br/>完整对话历史]
        SUMMARY[ConversationSummaryMemory<br/>摘要历史]
        WINDOW[ConversationBufferWindowMemory<br/>最近N轮]
        SUMBUF[ConversationSummaryBufferMemory<br/>摘要+最近N轮]
    end

    style LOAD fill:#e3f2fd
    style SAVE fill:#e8f5e9
    style BUFFER fill:#fff3e0
```

**各记忆类型对比**：

| 记忆类型 | 存储内容 | Token 消耗 | 记忆完整性 | 适用场景 |
|---------|---------|-----------|-----------|---------|
| **ConversationBufferMemory** | 完整对话历史 | 高（随轮次增长） | 完整 | 短对话、重要对话 |
| **ConversationSummaryMemory** | 对话摘要 | 低（稳定） | 要点完整，细节丢失 | 长对话、客服系统 |
| **ConversationBufferWindowMemory** | 最近 N 轮 | 中（有上限） | 最近完整，早期丢失 | 日常闲聊、上下文窗口有限 |
| **ConversationSummaryBufferMemory** | 摘要 + 最近 N 轮 | 中（稳定） | 要点+最近完整 | 生产级长对话 |
| **ConversationKGMemory** | 知识图谱 | 中 | 实体关系完整 | 复杂关系推理 |
| **EntityMemory** | 实体信息 | 低 | 实体属性完整 | 个人助手、CRM |

**LCEL 中实现记忆的核心模式**：
1. **MessagesPlaceholder**：在 Prompt Template 中预留消息历史的位置
2. **RunnableLambda**：包装记忆的加载和保存逻辑
3. **RunnablePassthrough.assign**：将历史消息注入输入字典
4. **外部存储**：将消息历史存储在数据库、Redis 或文件中

> 🎯 **面试高频考点**：ConversationBufferMemory 和 ConversationSummaryMemory 的区别是什么？在长对话中应该选择哪种？答：ConversationBufferMemory 存储完整的对话历史，记忆完整但 Token 消耗随轮次线性增长，可能超出上下文窗口；ConversationSummaryMemory 存储对话的摘要（由 LLM 生成），Token 消耗稳定但会丢失细节。在长对话中推荐使用 ConversationSummaryBufferMemory（摘要 + 最近 N 轮的组合），它在记忆完整性和 Token 消耗之间取得了最佳平衡——早期对话用摘要保留要点，最近对话用完整历史保留细节。

#### 代码示例

**示例1：基础——使用 ConversationBufferMemory 的对话链**

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from operator import itemgetter

# 1. 创建模型和 Prompt
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的 AI 助手。请用中文回答用户的问题。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# 2. 创建记忆
memory = ConversationBufferMemory(
    return_messages=True,  # 返回消息对象而非字符串
    memory_key="history",   # 记忆在 Prompt 中的变量名
)

# 3. 构建带记忆的链
chain = (
    RunnablePassthrough.assign(
        history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
    )
    | prompt
    | model
    | StrOutputParser()
)

# 4. 对话循环
print("=== 带记忆的对话 ===")
print("输入 '退出' 结束对话\n")

conversation = [
    "你好，我叫小明，今年25岁",
    "我叫什么名字？今年多大？",
    "我是做什么工作的？（提示：我没说过）",
]

for user_input in conversation:
    print(f"你: {user_input}")
    response = chain.invoke({"input": user_input})
    print(f"AI: {response}")
    # 保存对话到记忆
    memory.save_context({"input": user_input}, {"output": response})
    print()

# 预期输出：
# 你: 你好，我叫小明，今年25岁
# AI: 你好小明！很高兴认识你。25岁是个美好的年纪...
# 你: 我叫什么名字？今年多大？
# AI: 你叫小明，今年25岁。
# 你: 我是做什么工作的？
# AI: 你没有告诉我你的工作，能和我分享一下吗？
```

**示例2：进阶——使用 ConversationSummaryMemory 的长对话**

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryMemory
from operator import itemgetter

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 创建摘要记忆（使用 LLM 生成摘要）
summary_memory = ConversationSummaryMemory(
    llm=model,              # 用于生成摘要的模型
    return_messages=True,
    memory_key="history",
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个知识渊博的助手。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chain = (
    RunnablePassthrough.assign(
        history=RunnableLambda(summary_memory.load_memory_variables) | itemgetter("history")
    )
    | prompt | model | StrOutputParser()
)

# 模拟长对话
long_conversation = [
    "我正在学习 Python，能推荐一些学习资源吗？",
    "我已经学完了基础语法，接下来应该学什么？",
    "我对数据分析感兴趣，需要学哪些库？",
    "pandas 和 numpy 有什么区别？",
    "我想做一个数据分析项目，有什么推荐？",
]

print("=== 摘要记忆长对话 ===")
for i, user_input in enumerate(long_conversation, 1):
    response = chain.invoke({"input": user_input})
    summary_memory.save_context({"input": user_input}, {"output": response})
    print(f"轮次 {i}:")
    print(f"  你: {user_input}")
    print(f"  AI: {response[:80]}...")
    # 查看当前摘要
    print(f"  当前记忆: {summary_memory.buffer[:100]}...")
    print()

# 验证：即使对话很长，记忆中存储的是摘要而非完整历史
print(f"记忆类型: {type(summary_memory.buffer)}")
print(f"记忆内容: {summary_memory.buffer[:200]}...")
# 预期输出：记忆中存储的是对话摘要，Token 消耗稳定
```

**示例3：完整场景——LCEL 原生记忆实现（不使用旧版 Memory 类）**

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from typing import List
from operator import itemgetter

# 1. 自定义记忆管理类（LCEL 原生方式）
class ConversationMemory:
    """基于消息列表的对话记忆管理"""

    def __init__(self, max_messages: int = 20):
        self.messages: List[BaseMessage] = []
        self.max_messages = max_messages  # 最大保留消息数（窗口记忆）

    def add_user_message(self, content: str):
        self.messages.append(HumanMessage(content=content))
        self._truncate()

    def add_ai_message(self, content: str):
        self.messages.append(AIMessage(content=content))
        self._truncate()

    def _truncate(self):
        """截断超出最大消息数的早期消息"""
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_messages(self) -> List[BaseMessage]:
        return self.messages

    def clear(self):
        self.messages = []

# 2. 创建链
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
memory = ConversationMemory(max_messages=10)  # 保留最近10条消息（5轮对话）

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个编程助手。请用简洁的语言回答编程问题。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# 链：注入历史 → Prompt → Model → Parser
chain = (
    RunnablePassthrough.assign(
        history=RunnableLambda(lambda _: memory.get_messages())
    )
    | prompt | model | StrOutputParser()
)

# 3. 对话函数
def chat(user_input: str) -> str:
    """发送消息并获取回复，自动管理记忆"""
    # 添加用户消息到记忆
    memory.add_user_message(user_input)
    # 调用链（记忆中的消息会被注入）
    response = chain.invoke({"input": user_input})
    # 添加 AI 回复到记忆
    memory.add_ai_message(response)
    return response

# 4. 测试对话
print("=== LCEL 原生记忆对话 ===")
test_inputs = [
    "什么是递归？",
    "能举一个 Python 的例子吗？",
    "递归和循环有什么区别？",
    "我之前问的第一个问题是什么？",
]

for user_input in test_inputs:
    response = chat(user_input)
    print(f"你: {user_input}")
    print(f"AI: {response}")
    print(f"[记忆中有 {len(memory.messages)} 条消息]")
    print()

# 5. 验证记忆截断
print("=== 测试记忆截断 ===")
for i in range(10):
    chat(f"这是第 {i+6} 轮对话")
print(f"当前记忆消息数: {len(memory.messages)}（最大为 {memory.max_messages}）")
# 预期输出：记忆消息数不超过 max_messages，早期消息被截断
```

#### 使用场景与最佳实践

**适用场景**：
- 多轮对话机器人（客服、个人助手、聊天伴侣）
- 需要上下文理解的问答系统（指代消解、省略恢复）
- 长对话场景（需要摘要或窗口记忆控制 Token 消耗）
- 个性化应用（记住用户偏好、历史交互）

**不适用场景**：
- 单次问答（不需要记忆）
- 无状态 API 服务（每次请求独立，不需要跨请求记忆）
- 对延迟极度敏感的场景（记忆加载有少量开销）

**最佳实践**：
1. **使用 MessagesPlaceholder 注入历史**：在 Prompt Template 中使用 MessagesPlaceholder，不要手动拼接历史消息字符串
2. **选择合适的记忆策略**：短对话用 BufferMemory，长对话用 SummaryBufferMemory，生产环境推荐 SummaryBufferMemory
3. **控制记忆大小**：设置 max_tokens 或 max_messages 限制，避免记忆无限增长导致 Token 消耗过高和上下文溢出
4. **记忆外部化**：生产环境将记忆存储在数据库/Redis 中，不要只存在内存中（服务重启会丢失）
5. **在链外管理记忆**：使用 LCEL 时，记忆的加载和保存通常在链外进行（调用链前加载，调用链后保存），保持链的无状态性

**性能建议**：
- 记忆加载的开销很小（微秒级），不会成为性能瓶颈
- 长对话使用摘要记忆可将 Token 消耗从 O(n) 降为 O(1)
- 窗口记忆（最近 N 轮）在记忆完整性和 Token 消耗之间取得平衡
- 大量并发用户时，使用 Redis 存储记忆，避免内存溢出

#### 常见坑点

**坑点1：记忆未正确保存导致多轮对话丢失上下文**
- **错误现象**：模型在第二轮对话时忘记了第一轮的内容，回答"我不知道你在说什么"
- **根本原因**：调用链后忘记调用 `memory.save_context()` 保存对话，或保存时输入输出的 Key 不匹配
- **正确做法**：
  ```python
  from langchain.memory import ConversationBufferMemory

  memory = ConversationBufferMemory(return_messages=True, memory_key="history")

  # ❌ 错误：只调用链，不保存记忆
  # response = chain.invoke({"input": user_input})
  # # 下一轮对话时记忆是空的

  # ✅ 正确：调用链后保存记忆
  response = chain.invoke({"input": user_input})
  memory.save_context(
      {"input": user_input},   # 输入（Key 必须与 memory 的 input_key 一致）
      {"output": response}      # 输出（Key 必须与 memory 的 output_key 一致）
  )

  # ✅ 正确：使用封装函数自动管理记忆
  def chat(user_input):
      response = chain.invoke({"input": user_input})
      memory.save_context({"input": user_input}, {"output": response})
      return response

  # 使用
  chat("你好，我叫小明")
  chat("我叫什么名字？")  # 模型能记住"小明"
  ```
- **预防措施**：将对话逻辑封装为函数，在函数内自动保存记忆；使用 LangGraph 的 Checkpoint 机制自动管理状态（不需要手动保存记忆）；在测试中验证多轮对话的上下文连续性

**坑点2：记忆中的消息历史过长导致 Token 超出模型上下文窗口**
- **错误现象**：`openai.BadRequestError: maximum context length exceeded` 或对话到一定轮次后报错
- **根本原因**：ConversationBufferMemory 存储完整对话历史，随着轮次增加，消息总 Token 数超过模型的上下文窗口限制（如 gpt-4o-mini 为 128K tokens）
- **正确做法**：
  ```python
  # ❌ 错误：使用无限制的 ConversationBufferMemory
  # memory = ConversationBufferMemory(return_messages=True)

  # ✅ 正确1：使用窗口记忆（只保留最近 N 轮）
  from langchain.memory import ConversationBufferWindowMemory
  memory = ConversationBufferWindowMemory(
      k=5,  # 保留最近5轮对话
      return_messages=True,
      memory_key="history"
  )

  # ✅ 正确2：使用摘要记忆（Token 消耗稳定）
  from langchain.memory import ConversationSummaryMemory
  memory = ConversationSummaryMemory(
      llm=model,
      return_messages=True,
      memory_key="history"
  )

  # ✅ 正确3：使用摘要+窗口记忆（推荐生产环境）
  from langchain.memory import ConversationSummaryBufferMemory
  memory = ConversationSummaryBufferMemory(
      llm=model,
      max_token_limit=1000,  # 超过1000 token 时开始摘要
      return_messages=True,
      memory_key="history"
  )

  # ✅ 正确4：自定义记忆截断逻辑
  class TruncatedMemory:
      def __init__(self, max_messages=20):
          self.messages = []
          self.max_messages = max_messages

      def add(self, msg):
          self.messages.append(msg)
          if len(self.messages) > self.max_messages:
              self.messages = self.messages[-self.max_messages:]
  ```
- **预防措施**：始终设置记忆的大小限制（max_token_limit 或 k）；生产环境使用 ConversationSummaryBufferMemory；监控每次请求的 Token 消耗，设置告警；在 Prompt 中设置系统提示告知模型"如果历史过长，只关注最近的对话"

---

### 5.3 回调系统 Callbacks

#### 概念解释

**正式定义**：Callbacks（回调系统）是 LangChain 中用于在执行流程的各个节点触发自定义逻辑的钩子机制，包括 `on_llm_start`、`on_llm_end`、`on_llm_error`、`on_chain_start`、`on_chain_end`、`on_tool_start`、`on_tool_end`、`on_text` 等回调方法。通过实现 `BaseCallbackHandler` 类并注册到链或模型中，可以实现日志记录、性能监控、流式输出、LangSmith 追踪等横切关注点。

**生活化比喻**：Callbacks 就像汽车中的传感器和仪表盘——发动机启动时触发"启动传感器"（on_llm_start），发动机停止时触发"停止传感器"（on_llm_end），出现故障时触发"故障警报"（on_llm_error）。这些传感器将数据发送到仪表盘（Callback Handler），让你实时了解车辆状态。没有传感器，你就是在"盲开"——不知道发动机转多快、耗多少油、有没有故障。

**核心价值**：实现可观测性（日志、追踪、监控）、流式输出（实时获取 LLM 生成的 Token）、自定义逻辑（成本统计、内容审核、异常告警）；是 LangSmith 等可观测性平台的基础；不需要修改业务代码即可添加横切关注点。

#### 原理说明

```mermaid
graph TB
    subgraph 回调触发流程
        START[链开始执行] -->|on_chain_start| CH1[Callback Handler]
        CH1 --> LLM_START[LLM 开始调用]
        LLM_START -->|on_llm_start| CH2[Callback Handler]
        CH2 -->|on_llm_new_token| CH3[流式 Token]
        CH3 --> LLM_END[LLM 调用结束]
        LLM_END -->|on_llm_end| CH4[Callback Handler]
        CH4 --> TOOL_START[工具开始执行]
        TOOL_START -->|on_tool_start| CH5[Callback Handler]
        CH5 --> TOOL_END[工具执行结束]
        TOOL_END -->|on_tool_end| CH6[Callback Handler]
        CH6 --> END[链执行结束]
        END -->|on_chain_end| CH7[Callback Handler]
    end

    subgraph 常见用途
        LOG[日志记录]
        MONITOR[性能监控]
        STREAM[流式输出]
        COST[成本统计]
        AUDIT[内容审核]
    end

    CH1 --> LOG
    CH2 --> MONITOR
    CH3 --> STREAM
    CH4 --> COST
    CH5 --> AUDIT

    style CH1 fill:#e3f2fd
    style CH3 fill:#f3e5f5
```

**核心回调方法一览**：

| 回调方法 | 触发时机 | 参数 | 常见用途 |
|---------|---------|------|---------|
| `on_chain_start` | 链开始执行 | serialized, inputs | 记录链入口、输入日志 |
| `on_chain_end` | 链执行结束 | outputs | 记录链出口、输出日志 |
| `on_chain_error` | 链执行出错 | error | 错误告警、异常记录 |
| `on_llm_start` | LLM 开始调用 | serialized, prompts | 记录模型调用、输入 |
| `on_llm_end` | LLM 调用结束 | response | 记录输出、Token 统计 |
| `on_llm_error` | LLM 调用出错 | error | 错误告警、重试触发 |
| `on_llm_new_token` | LLM 生成新 Token | token, **kwargs | 流式输出、实时显示 |
| `on_tool_start` | 工具开始执行 | serialized, input_str | 记录工具调用、参数 |
| `on_tool_end` | 工具执行结束 | output | 记录工具结果、耗时 |
| `on_tool_error` | 工具执行出错 | error | 错误告警 |
| `on_text` | 收到文本 | text, **kwargs | 原始文本记录 |

**回调的注册方式**：
1. **构造函数注册**：在创建模型/链时传入 `callbacks=[handler]`
2. **调用时注册**：在 `invoke()`/`stream()` 时传入 `config={"callbacks": [handler]}`
3. **全局注册**：使用 `langchain_core.callbacks.set_handler()` 注册全局回调
4. **上下文管理器**：使用 `with get_callback_manager().get_context() as cm:` 临时注册

> 🎯 **面试高频考点**：LangChain 的回调系统有哪些核心方法？如何实现流式输出？答：核心回调方法包括 on_chain_start/end/error、on_llm_start/end/error/new_token、on_tool_start/end/error、on_text 等。实现流式输出有两种方式：① 使用链的 `.stream()` 方法，它内部会触发 `on_llm_new_token` 回调并 yield 每个 Token；② 自定义 CallbackHandler，实现 `on_llm_new_token` 方法，在方法中处理每个 Token（如写入 WebSocket、更新 UI）。`.stream()` 是更简单的方式，自定义 Handler 适合需要复杂处理的场景。

#### 代码示例

**示例1：基础——使用 StdOutCallbackHandler 打印执行过程**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import StdOutCallbackHandler

# 创建回调处理器（打印执行过程到标准输出）
handler = StdOutCallbackHandler()

# 创建链
chain = (
    ChatPromptTemplate.from_template("用一句话解释：{topic}")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0, callbacks=[handler])
    | StrOutputParser()
)

# 调用链（回调会自动触发）
print("=== 带回调的链执行 ===")
result = chain.invoke({"topic": "LangChain"})
print(f"\n最终结果: {result}")

# 预期输出：
# > Entering new RunnableSequence chain...
# > Entering new ChatPromptTemplate chain...
# > Finished chain.
# > Entering new ChatOpenAI chain...
# > Finished chain.
# > Entering new StrOutputParser chain...
# > Finished chain.
# > Finished chain.
# 最终结果: LangChain 是...
```

**示例2：进阶——自定义 CallbackHandler 实现成本统计和性能监控**

```python
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import time
from typing import Any, Dict, List

# 自定义回调处理器
class StatsCallbackHandler(BaseCallbackHandler):
    """统计 LLM 调用次数、Token 消耗、耗时的回调处理器"""

    def __init__(self):
        self.llm_calls = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.llm_start_times = {}
        self.llm_durations = []

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """LLM 开始调用时记录开始时间"""
        self.llm_calls += 1
        self.llm_start_times[self.llm_calls] = time.time()
        print(f"[LLM 调用 #{self.llm_calls}] 开始执行...")

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """LLM 调用结束时统计 Token 和耗时"""
        duration = time.time() - self.llm_start_times.get(self.llm_calls, time.time())
        self.llm_durations.append(duration)

        # 从响应中提取 Token 使用量
        if hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            prompt_tokens = token_usage.get('prompt_tokens', 0)
            completion_tokens = token_usage.get('completion_tokens', 0)
            total = token_usage.get('total_tokens', 0)

            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            self.total_tokens += total

            # 估算成本（gpt-4o-mini 价格）
            cost = (prompt_tokens * 0.00015 + completion_tokens * 0.0006) / 1000
            self.total_cost += cost

            print(f"[LLM 调用 #{self.llm_calls}] 完成 | 耗时: {duration:.2f}s | "
                  f"Prompt: {prompt_tokens} tokens | Completion: {completion_tokens} tokens | "
                  f"成本: ${cost:.6f}")

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """LLM 调用出错时记录"""
        print(f"[LLM 调用 #{self.llm_calls}] 出错: {str(error)}")

    def print_summary(self):
        """打印统计摘要"""
        print("\n" + "="*50)
        print("📊 LLM 调用统计摘要")
        print("="*50)
        print(f"总调用次数: {self.llm_calls}")
        print(f"总 Prompt Tokens: {self.total_prompt_tokens}")
        print(f"总 Completion Tokens: {self.total_completion_tokens}")
        print(f"总 Tokens: {self.total_tokens}")
        print(f"总耗时: {sum(self.llm_durations):.2f}s")
        print(f"平均耗时: {sum(self.llm_durations)/len(self.llm_durations):.2f}s" if self.llm_durations else "")
        print(f"估算总成本: ${self.total_cost:.6f}")
        print("="*50)

# 使用自定义回调
stats_handler = StatsCallbackHandler()

chain = (
    ChatPromptTemplate.from_template("回答问题：{question}")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0, callbacks=[stats_handler])
    | StrOutputParser()
)

# 多次调用
questions = [
    {"question": "什么是 LangChain？"},
    {"question": "什么是 LCEL？"},
    {"question": "什么是 Runnable？"},
]

for q in questions:
    chain.invoke(q)

# 打印统计摘要
stats_handler.print_summary()
# 预期输出：每次调用的详细统计 + 最终汇总
```

**示例3：完整场景——自定义 CallbackHandler 实现流式输出和内容审核**

```python
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from typing import Any, Dict, List
import queue
import threading

# 回调1：流式输出处理器
class StreamingCallbackHandler(BaseCallbackHandler):
    """将 LLM 生成的 Token 放入队列，实现流式输出"""

    def __init__(self):
        self.token_queue = queue.Queue()
        self.generation_complete = False

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """每个新 Token 生成时触发"""
        self.token_queue.put(token)

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """LLM 生成结束时触发"""
        self.generation_complete = True
        self.token_queue.put(None)  # 放入结束标记

    def get_stream(self):
        """获取流式输出生成器"""
        while True:
            token = self.token_queue.get()
            if token is None:
                break
            yield token

# 回调2：内容审核处理器
class ContentModerationCallbackHandler(BaseCallbackHandler):
    """审核 LLM 输出内容，标记敏感信息"""

    def __init__(self):
        self.sensitive_keywords = ["密码", "密钥", "token", "API Key", "身份证"]
        self.flagged_content = []

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """LLM 输出结束时审核内容"""
        # 提取生成的文本
        generated_text = ""
        if hasattr(response, 'generations') and response.generations:
            for gen_list in response.generations:
                for gen in gen_list:
                    if hasattr(gen, 'text'):
                        generated_text += gen.text

        # 检查敏感关键词
        for keyword in self.sensitive_keywords:
            if keyword.lower() in generated_text.lower():
                self.flagged_content.append({
                    "keyword": keyword,
                    "content_preview": generated_text[:100],
                    "warning": f"输出包含敏感关键词: {keyword}"
                })
                print(f"⚠️  [内容审核] 检测到敏感关键词: {keyword}")

    def on_chain_end(self, outputs: Any, **kwargs: Any) -> None:
        """链结束时打印审核结果"""
        if self.flagged_content:
            print(f"\n🚨 内容审核报告: 发现 {len(self.flagged_content)} 处敏感内容")
            for item in self.flagged_content:
                print(f"  - {item['warning']}")
        else:
            print("\n✅ 内容审核通过: 未发现敏感内容")

# 使用两个回调处理器
streaming_handler = StreamingCallbackHandler()
moderation_handler = ContentModerationCallbackHandler()

chain = (
    ChatPromptTemplate.from_template("回答问题：{question}")
    | ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        callbacks=[streaming_handler, moderation_handler],
        streaming=True,  # 启用流式输出
    )
    | StrOutputParser()
)

# 在后台线程中执行链，同时消费流式输出
def run_chain():
    chain.invoke({"question": "什么是 API Key？如何安全存储？"})

thread = threading.Thread(target=run_chain)
thread.start()

# 消费流式输出
print("=== 流式输出 ===")
for token in streaming_handler.get_stream():
    print(token, end="", flush=True)
print()

thread.join()

# 审核结果已在回调中打印
# 预期输出：实时流式输出 + 内容审核警告（因为问题涉及 API Key）
```

#### 使用场景与最佳实践

**适用场景**：
- 日志记录和调试（打印执行过程、输入输出）
- 性能监控（统计调用次数、耗时、Token 消耗）
- 成本统计（估算 API 调用费用）
- 流式输出（实时显示 LLM 生成的内容）
- 内容审核（检查输入输出中的敏感信息）
- 错误告警（LLM/工具出错时发送通知）
- LangSmith 集成（自动追踪链的执行过程）

**不适用场景**：
- 极简脚本（不需要可观测性）
- 对性能极度敏感且回调逻辑复杂的场景（回调有少量开销）

**最佳实践**：
1. **使用 StdOutCallbackHandler 调试**：开发阶段使用 `StdOutCallbackHandler()` 打印执行过程，快速定位问题
2. **生产环境使用 LangSmith**：不要自己造轮子，使用 LangSmith 进行完整的链路追踪、评估和监控
3. **回调逻辑保持轻量**：回调方法中不要执行耗时操作（如数据库写入、网络请求），应异步处理或批量处理
4. **多个回调可以组合**：可以同时注册多个 CallbackHandler（如流式 + 审核 + 统计），它们会按顺序触发
5. **使用 `on_llm_new_token` 实现流式**：需要自定义流式处理时实现此方法，简单场景直接用 `.stream()` 即可

**性能建议**：
- 回调的开销很小（微秒级），不会成为性能瓶颈
- 但如果回调中执行耗时操作（如写数据库、发网络请求），会显著增加延迟
- 对于高频调用，考虑使用异步回调（`AsyncCallbackHandler`）或批量处理
- 流式输出时，每个 Token 触发一次回调，大量 Token 会有累积开销，使用 `.stream()` 更高效

#### 常见坑点

**坑点1：回调未正确注册导致不触发**
- **错误现象**：自定义的 CallbackHandler 没有任何输出，`on_llm_start` 等方法从未被调用
- **根本原因**：回调处理器没有正确注册到模型或链上。回调需要在创建模型时通过 `callbacks` 参数传入，或在调用时通过 `config` 传入。只创建 Handler 但不注册是不会触发的
- **正确做法**：
  ```python
  from langchain_core.callbacks import StdOutCallbackHandler
  from langchain_openai import ChatOpenAI

  handler = StdOutCallbackHandler()

  # ✅ 正确1：在创建模型时注册
  model = ChatOpenAI(model="gpt-4o-mini", callbacks=[handler])
  model.invoke("你好")  # 回调会触发

  # ✅ 正确2：在调用时通过 config 注册
  model2 = ChatOpenAI(model="gpt-4o-mini")
  model2.invoke("你好", config={"callbacks": [handler]})  # 回调会触发

  # ✅ 正确3：在链的每个组件上注册
  from langchain_core.prompts import ChatPromptTemplate
  from langchain_core.output_parsers import StrOutputParser
  chain = (
      ChatPromptTemplate.from_template("{q}")
      | ChatOpenAI(model="gpt-4o-mini", callbacks=[handler])  # 注册到模型
      | StrOutputParser()
  )
  chain.invoke({"q": "你好"})

  # ❌ 错误：只创建 Handler 不注册
  # handler = StdOutCallbackHandler()
  # model = ChatOpenAI(model="gpt-4o-mini")
  # model.invoke("你好")  # 回调不会触发！
  ```
- **预防措施**：创建 Handler 后立即注册到模型或链；使用 `handler` 变量名避免遗忘；在 Handler 的 `__init__` 中打印日志确认创建成功

**坑点2：流式回调 `on_llm_new_token` 不触发**
- **错误现象**：实现了 `on_llm_new_token` 方法，但调用时从未触发，只有 `on_llm_end` 触发
- **根本原因**：模型没有启用流式模式。`on_llm_new_token` 只在流式输出时触发，需要在创建模型时设置 `streaming=True`，或使用 `.stream()` 方法调用
- **正确做法**：
  ```python
  from langchain_core.callbacks import BaseCallbackHandler
  from langchain_openai import ChatOpenAI

  class TokenCounter(BaseCallbackHandler):
      def __init__(self):
          self.token_count = 0
      def on_llm_new_token(self, token: str, **kwargs):
          self.token_count += 1
          print(token, end="", flush=True)

  counter = TokenCounter()

  # ❌ 错误：未启用流式
  # model = ChatOpenAI(model="gpt-4o-mini")
  # model.invoke("写一首诗", config={"callbacks": [counter]})
  # # on_llm_new_token 不会触发

  # ✅ 正确1：创建模型时启用 streaming=True
  model = ChatOpenAI(model="gpt-4o-mini", streaming=True, callbacks=[counter])
  model.invoke("写一首关于 AI 的短诗")
  print(f"\n共生成 {counter.token_count} 个 Token")

  # ✅ 正确2：使用 .stream() 方法（自动启用流式）
  model2 = ChatOpenAI(model="gpt-4o-mini")
  for chunk in model2.stream("写一首关于 AI 的短诗"):
      print(chunk.content, end="", flush=True)
  print()

  # ✅ 正确3：链的 .stream() 方法
  from langchain_core.prompts import ChatPromptTemplate
  from langchain_core.output_parsers import StrOutputParser
  chain = ChatPromptTemplate.from_template("{q}") | model2 | StrOutputParser()
  for chunk in chain.stream({"q": "写一首短诗"}):
      print(chunk, end="", flush=True)
  print()
  ```
- **预防措施**：需要流式输出时设置 `streaming=True` 或使用 `.stream()`；在自定义 Handler 中同时实现 `on_llm_new_token` 和 `on_llm_end`，兼容流式和非流式模式；测试时先验证流式是否生效

---

> 💡 **深度讲解**
>
> Chain 类型和记忆系统是 LangChain 从"简单链"到"复杂应用"的关键升级。传统 Chain 类（LLMChain、SequentialChain、RouterChain）是 LangChain 早期的组合方式，它们将常见的组合模式封装为类，方便开发者快速使用。但随着 LLM 应用复杂度的增加，传统 Chain 类的局限性逐渐暴露——每种组合模式都需要一个新类（类爆炸）、输入输出格式不统一、不支持流式/异步/批量。LCEL 的出现解决了这些问题，用 `|` 运算符替代了类继承，用 Runnable 协议统一了接口。
>
> 记忆系统是构建多轮对话应用的基础。没有记忆，LLM 每次调用都是无状态的——它不知道之前聊过什么，无法理解"他""那个问题"等指代。LangChain 提供了多种记忆策略：ConversationBufferMemory 记住所有对话（适合短对话），ConversationSummaryMemory 记住摘要（适合长对话），ConversationBufferWindowMemory 记住最近 N 轮（平衡方案），ConversationSummaryBufferMemory 摘要+最近 N 轮（生产推荐）。在 LCEL 中，记忆通常通过 MessagesPlaceholder 注入历史，在链外管理加载和保存。
>
> 回调系统是可观测性的基础。LLM 应用的执行过程是"黑盒"——如果没有日志和追踪，问题排查非常困难。回调系统在执行流程的各个节点（LLM 调用前后、工具执行前后、链开始结束）触发钩子，开发者可以实现自定义逻辑（日志、监控、流式、审核）。StdOutCallbackHandler 是最常用的调试工具，它打印完整的执行过程。生产环境推荐使用 LangSmith，它提供了完整的链路追踪、评估和监控能力。
>
> 这三个主题的共同线索是"从简单到复杂"——Chain 类型从简单的 LLMChain 到复杂的 SequentialChain，记忆从简单的 Buffer 到复杂的 SummaryBuffer，回调从简单的打印到复杂的 LangSmith。掌握了这些，你就可以构建从简单问答到生产级对话系统的各种应用。

> **📝 精简总结**
>
> 传统 Chain 类型（LLMChain/SequentialChain/RouterChain/TransformChain）已被弃用，推荐使用 LCEL（`|` 运算符）替代；LLMChain → `prompt | model | parser`，SequentialChain → `RunnablePassthrough.assign()` 链式组合，RouterChain → `RunnableBranch`，TransformChain → `RunnableLambda`；记忆系统包括 ConversationBufferMemory（完整历史）、ConversationSummaryMemory（摘要）、ConversationBufferWindowMemory（最近N轮）、ConversationSummaryBufferMemory（摘要+最近N轮，生产推荐），LCEL 中通过 MessagesPlaceholder 注入历史，链外管理加载保存；回调系统通过 BaseCallbackHandler 实现 on_llm_start/end/new_token、on_chain_start/end、on_tool_start/end 等钩子，用于日志、监控、流式输出、成本统计、内容审核，生产环境推荐使用 LangSmith。

> **🎯 梯度练习题**
>
> **入门级**：
> 1. 将一个使用 LLMChain 的旧代码迁移到 LCEL，验证输出一致性
> 2. 使用 ConversationBufferMemory 构建一个多轮对话链，验证模型能记住之前的对话内容
> 3. 使用 StdOutCallbackHandler 打印链的执行过程，观察各个回调方法的触发顺序
>
> **进阶级**：
> 1. 将一个使用 SequentialChain 的多步骤链迁移到 LCEL，使用 RunnablePassthrough.assign 保留中间结果
> 2. 对比 ConversationBufferMemory、ConversationSummaryMemory、ConversationSummaryBufferMemory 在 20 轮对话后的 Token 消耗差异
> 3. 实现一个自定义 CallbackHandler，统计 LLM 调用的 Token 消耗和估算成本，在 10 次调用后打印汇总
>
> **实战级**：
> 1. 构建一个生产级对话系统：使用 ConversationSummaryBufferMemory 管理长对话，自定义 CallbackHandler 实现流式输出+成本统计+内容审核，将记忆存储在外部（JSON 文件）
> 2. 将一个完整的旧版 LangChain 项目（使用 LLMChain + SequentialChain + RouterChain + ConversationBufferMemory）全面迁移到 LCEL，编写测试验证迁移前后输出一致
> 3. 设计一个可观测性方案：使用自定义 CallbackHandler 实现日志记录（输入输出/耗时/Token）、错误告警（邮件通知）、性能监控（Prometheus 指标），并与 LangSmith 对比优劣

---

## 七、实战篇：RAG 应用完整实战

### 7.1 Retriever 与 Document 核心

#### 概念解释

**正式定义**：Retriever（检索器）是 LangChain 中根据查询文本返回相关文档的组件，核心接口是 `invoke(query) -> List[Document]`；Document（文档）是 LangChain 中对文本内容的封装，包含 `page_content`（文本内容）和 `metadata`（元数据字典）两个核心属性。最常见的 Retriever 实现是 `VectorStoreRetriever`，基于向量数据库的语义搜索。

**生活化比喻**：Retriever 就像图书馆的图书管理员——你告诉它你想找什么（查询文本），它在书库（向量数据库）中搜索最相关的书籍（文档），然后把最相关的几本递给你。Document 就像一本书——`page_content` 是书的正文内容，`metadata` 是书的封面信息（书名、作者、出版日期、页码等）。

**核心价值**：Retriever 是 RAG（检索增强生成）的核心组件，解决 LLM 知识截止日期和幻觉问题；Document 标准化了文本内容的表示，支持元数据过滤和溯源；丰富的 Retriever 实现（向量检索、关键词检索、混合检索、重排序）满足不同场景需求。

#### 原理说明

```mermaid
graph LR
    subgraph RAG 检索流程
        Q[用户查询] --> E[Embedding 模型<br/>查询向量化]
        E --> VS[向量数据库<br/>相似度搜索]
        VS --> RERANK[重排序<br/>Cross-Encoder]
        RERANK --> DOCS[Top-K 文档]
        DOCS --> FORMAT[格式化<br/>拼接为上下文]
        FORMAT --> PROMPT[注入 Prompt]
    end

    subgraph Document 结构
        PC[page_content<br/>文本内容]
        MD[metadata<br/>元数据字典]
    end

    DOCS -.-> PC
    DOCS -.-> MD

    style E fill:#e3f2fd
    style VS fill:#f3e5f5
    style RERANK fill:#e8f5e9
```

**Retriever 的核心机制**：
1. **查询向量化**：使用 Embedding 模型将查询文本转换为向量
2. **相似度搜索**：在向量数据库中计算查询向量与文档向量的相似度（余弦相似度、内积等）
3. **Top-K 筛选**：返回相似度最高的 K 个文档
4. **元数据过滤**：支持根据 metadata 过滤文档（如按来源、日期、标签过滤）
5. **重排序（可选）**：使用 Cross-Encoder 模型对初步检索结果重新排序，提升精度

**常见 Retriever 类型对比**：

| Retriever 类型 | 原理 | 优势 | 劣势 | 适用场景 |
|---------------|------|------|------|---------|
| **VectorStoreRetriever** | 向量语义搜索 | 语义理解强，支持同义查询 | 精确匹配差，成本高 | 通用 RAG、语义问答 |
| **BM25Retriever** | 关键词匹配（TF-IDF改进） | 精确匹配好，无需 Embedding | 语义理解弱 | 关键词搜索、法律文档 |
| **EnsembleRetriever** | 向量+关键词混合 | 兼顾语义和精确 | 配置复杂 | 生产级 RAG |
| **ContextualCompressionRetriever** | 检索+压缩+重排序 | 精度高，上下文精简 | 延迟高，成本高 | 高精度需求 |
| **MultiQueryRetriever** | 生成多个查询变体检索 | 召回率高 | 延迟高（多次检索） | 模糊查询、复杂问题 |
| **ParentDocumentRetriever** | 小块检索+大块返回 | 兼顾检索精度和上下文完整 | 配置复杂 | 长文档 RAG |

> 🎯 **面试高频考点**：RAG 的工作原理是什么？Retriever 在其中扮演什么角色？答：RAG（Retrieval-Augmented Generation，检索增强生成）的工作原理是：① 将知识库文档分块并向量化存储到向量数据库；② 用户提问时，将查询向量化并在向量数据库中检索最相关的文档；③ 将检索到的文档作为上下文注入 Prompt；④ LLM 基于上下文生成回答。Retriever 是 RAG 的核心组件，负责根据查询返回相关文档，它的检索质量直接决定 RAG 系统的回答质量——检索不到相关文档，LLM 就无法基于事实回答；检索到不相关的文档，会干扰 LLM 生成正确答案。

#### 代码示例

**示例1：基础——使用 Chroma 向量数据库构建 Retriever**

```python
# 安装：pip install chromadb langchain-chroma langchain-openai langchain-text-splitters
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from operator import itemgetter

# 1. 准备文档（模拟知识库）
documents = [
    Document(
        page_content="LangChain 是一个用于构建大语言模型应用的开源框架，由 Harrison Chase 于 2022 年创建。",
        metadata={"source": "官网", "date": "2024-01-15", "category": "框架介绍"}
    ),
    Document(
        page_content="LCEL（LangChain Expression Language）是 LangChain 的表达式语言，通过 | 运算符组合 Runnable 组件。",
        metadata={"source": "文档", "date": "2024-02-20", "category": "核心概念"}
    ),
    Document(
        page_content="RAG（检索增强生成）是一种结合外部知识库和 LLM 的技术，通过检索相关文档增强生成质量。",
        metadata={"source": "论文", "date": "2024-03-10", "category": "技术原理"}
    ),
    Document(
        page_content="LangGraph 是 LangChain 团队推出的多 Agent 编排框架，基于状态机模型，支持复杂工作流。",
        metadata={"source": "官网", "date": "2024-04-05", "category": "框架介绍"}
    ),
    Document(
        page_content="向量数据库用于存储文档的 Embedding 向量，支持相似度搜索，常见的有 Chroma、Pinecone、Weaviate。",
        metadata={"source": "文档", "date": "2024-05-12", "category": "基础设施"}
    ),
]

# 2. 文档分块（如果文档较长）
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
)
splits = text_splitter.split_documents(documents)
print(f"原始文档数: {len(documents)}, 分块后: {len(splits)}")

# 3. 创建向量数据库和 Retriever
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./chroma_db",  # 持久化到本地
    collection_name="langchain_knowledge",
)

retriever = vectorstore.as_retriever(
    search_type="similarity",  # 相似度搜索
    search_kwargs={"k": 3},     # 返回 Top-3 文档
)

# 4. 测试检索
query = "什么是 LCEL？它有什么作用？"
retrieved_docs = retriever.invoke(query)
print(f"\n查询: {query}")
print(f"检索到 {len(retrieved_docs)} 个文档:")
for i, doc in enumerate(retrieved_docs, 1):
    print(f"  [{i}] {doc.page_content[:80]}...")
    print(f"      来源: {doc.metadata.get('source', '未知')}")

# 预期输出：检索到与 LCEL 相关的文档
```

**示例2：进阶——构建完整的 RAG 问答链**

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from operator import itemgetter

# 假设已有 vectorstore 和 retriever（见示例1）
# retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 1. 格式化文档函数
def format_docs(docs):
    """将文档列表格式化为字符串，添加来源信息"""
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "未知")
        formatted.append(f"[文档{i} | 来源:{source}]\n{doc.page_content}")
    return "\n\n".join(formatted)

# 2. RAG Prompt 模板
rag_prompt = ChatPromptTemplate.from_template("""你是一个知识问答助手。请根据以下上下文回答用户的问题。

要求：
1. 只根据上下文中的信息回答，不要编造
2. 如果上下文中没有相关信息，请回答"根据现有知识库无法回答该问题"
3. 回答时引用相关文档的编号（如[文档1]）
4. 用简洁清晰的语言回答

上下文：
{context}

用户问题：{question}

回答：""")

# 3. 构建 RAG 链
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

rag_chain = (
    # 并行执行：检索文档 + 传递原始问题
    {
        "context": itemgetter("question") | retriever | RunnableLambda(format_docs),
        "question": itemgetter("question"),
    }
    | rag_prompt
    | model
    | StrOutputParser()
)

# 4. 调用 RAG 链
questions = [
    "LangChain 是什么时候创建的？",
    "LCEL 的作用是什么？",
    "RAG 技术解决了什么问题？",
    "LangGraph 和 LangChain 是什么关系？",
    "如何制作红烧肉？（知识库中没有的内容）",
]

for q in questions:
    print(f"\n{'='*60}")
    print(f"问题: {q}")
    print(f"{'='*60}")
    answer = rag_chain.invoke({"question": q})
    print(f"回答: {answer}")

# 预期输出：
# - 前4个问题基于知识库回答，引用文档编号
# - 最后一个问题回答"根据现有知识库无法回答"
```

**示例3：完整场景——带元数据过滤和重排序的高级 RAG**

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from operator import itemgetter

# 1. 元数据过滤的 Retriever（只检索特定来源的文档）
retriever_filtered = vectorstore.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"category": "技术原理"},  # 只检索技术原理类文档
    }
)

# 测试元数据过滤
docs = retriever_filtered.invoke("什么是 RAG？")
print(f"过滤后检索到 {len(docs)} 个文档（均为技术原理类）")
for doc in docs:
    print(f"  - {doc.metadata.get('category')}: {doc.page_content[:60]}...")

# 2. 使用 LLMChainExtractor 进行上下文压缩（只保留与查询相关的句子）
compressor = LLMChainExtractor.from_llm(
    ChatOpenAI(model="gpt-4o-mini", temperature=0)
)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
)

# 测试压缩检索
query = "LangChain 的核心抽象有哪些？"
compressed_docs = compression_retriever.invoke(query)
print(f"\n压缩前检索 5 个文档，压缩后保留 {len(compressed_docs)} 个相关片段")
for doc in compressed_docs:
    print(f"  - {doc.page_content[:100]}...")

# 3. 构建带压缩的 RAG 链
def format_compressed_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

advanced_rag_chain = (
    {
        "context": itemgetter("question") | compression_retriever | RunnableLambda(format_compressed_docs),
        "question": itemgetter("question"),
    }
    | ChatPromptTemplate.from_template("""
根据以下上下文回答问题。上下文已经过相关度筛选，只包含最相关的内容。

上下文：
{context}

问题：{question}

回答：""")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

# 调用
result = advanced_rag_chain.invoke({"question": "LangChain 和 LangGraph 的区别是什么？"})
print(f"\n高级 RAG 回答:\n{result}")
# 预期输出：基于压缩后的相关片段回答，更精准
```

#### 使用场景与最佳实践

**适用场景**：
- 企业知识库问答（内部文档、产品手册、FAQ）
- 客服机器人（基于产品文档和历史工单回答）
- 法律/医疗/金融专业问答（基于专业文档和法规）
- 代码文档问答（基于 API 文档和代码仓库）
- 研究助手（基于论文和技术报告）

**不适用场景**：
- 知识库内容频繁变化（需要实时更新索引）
- 问题答案需要实时数据（应使用 Tool 调用而非 RAG）
- 简单的常识性问题（直接用 LLM 即可，不需要检索）
- 对延迟极度敏感的场景（检索增加 100-500ms 延迟）

**最佳实践**：
1. **合理的分块策略**：chunk_size 500-1000，chunk_overlap 10-20%，根据文档类型调整
2. **使用混合检索**：向量检索 + 关键词检索（EnsembleRetriever），兼顾语义和精确匹配
3. **添加重排序**：使用 Cross-Encoder 或 LLM 压缩器对检索结果重排序，提升 Top-K 精度
4. **元数据过滤**：为文档添加丰富的 metadata（来源、日期、分类、作者），支持过滤检索
5. **检索结果溯源**：在回答中引用文档来源，提升可信度，支持用户验证
6. **评估检索质量**：使用命中率（Hit Rate）、平均倒数排名（MRR）等指标评估检索效果

**性能建议**：
- Embedding 模型选择：text-embedding-3-small 性价比最高，text-embedding-3-large 精度最高
- 批量 Embedding：文档索引时批量处理，提升吞吐量
- 缓存检索结果：相同查询的检索结果可以缓存，减少重复计算
- 异步检索：高并发场景使用异步 Retriever（aretrieve_documents）
- 向量数据库选择：小规模用 Chroma，中规模用 Weaviate，大规模用 Pinecone/Milvus

#### 常见坑点

**坑点1：检索结果不相关导致回答质量差**
- **错误现象**：RAG 系统回答"根据现有知识无法回答"，但知识库中明明有相关内容；或回答与问题不相关
- **根本原因**：① 文档分块不合理（chunk 太大或太小）；② Embedding 模型不匹配（索引用的模型和查询用的模型不同）；③ 检索参数不当（Top-K 太小、相似度阈值太高）；④ 查询与文档的语义差异大（用户用口语化表达，文档用专业术语）
- **正确做法**：
  ```python
  # 1. 优化分块策略
  from langchain_text_splitters import RecursiveCharacterTextSplitter
  text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=800,       # 根据文档类型调整，技术文档用 500-800
      chunk_overlap=100,    # 10-20% 的重叠
      separators=["\n\n", "\n", "。", "！", "？", " ", ""],  # 中文友好的分隔符
  )

  # 2. 确保索引和查询使用相同的 Embedding 模型
  embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
  # 索引用：Chroma.from_documents(docs, embedding=embeddings)
  # 查询用：Chroma(persist_directory="...", embedding_function=embeddings)
  # 必须使用相同的 model 参数！

  # 3. 调整检索参数
  retriever = vectorstore.as_retriever(
      search_type="similarity_score_threshold",  # 带分数阈值
      search_kwargs={
          "k": 5,                    # 增加 Top-K
          "score_threshold": 0.5,    # 降低相似度阈值
      }
  )

  # 4. 使用查询改写（Query Rewriting）提升检索效果
  from langchain_core.prompts import ChatPromptTemplate
  rewrite_prompt = ChatPromptTemplate.from_template("""
  将以下用户问题改写为更适合检索的关键词查询。
  要求：使用专业术语，提取关键实体，去掉口语化表达。
  
  原始问题：{question}
  改写后的查询：""")
  rewrite_chain = rewrite_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0) | StrOutputParser()

  # 在 RAG 链中先改写查询再检索
  optimized_rag_chain = (
      {
          "context": itemgetter("question") | rewrite_chain | retriever | format_docs,
          "question": itemgetter("question"),
      }
      | rag_prompt | model | StrOutputParser()
  )
  ```
- **预防措施**：建立检索质量评估流程（使用标注数据集测试命中率）；定期检查检索结果的相关性；使用混合检索和重排序提升鲁棒性；为用户提供"相关文档"展示，便于反馈

**坑点2：向量数据库持久化后加载失败或检索结果为空**
- **错误现象**：重启应用后从持久化目录加载向量数据库，检索返回空列表或报错
- **根本原因**：① 加载时使用了不同的 Embedding 模型（维度不匹配）；② 持久化目录路径错误或权限不足；③ Chroma 版本升级导致数据格式不兼容；④ collection_name 不匹配（存储时和加载时使用不同的 collection 名）
- **正确做法**：
  ```python
  # ❌ 错误：加载时使用不同的 Embedding 模型
  # vectorstore = Chroma(
  #     persist_directory="./chroma_db",
  #     embedding_function=OpenAIEmbeddings(model="text-embedding-3-large")  # 索引时用的是 small
  # )

  # ✅ 正确：使用相同的 Embedding 模型和 collection_name
  embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # 与索引时相同

  vectorstore = Chroma(
      persist_directory="./chroma_db",
      embedding_function=embeddings,
      collection_name="langchain_knowledge",  # 与索引时相同
  )

  # 验证加载成功
  print(f"集合中的文档数: {vectorstore._collection.count()}")
  # 如果为 0，说明加载失败，需要重新索引

  # ✅ 正确：使用环境变量管理配置，避免硬编码不一致
  import os
  EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
  CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
  COLLECTION_NAME = os.getenv("COLLECTION_NAME", "knowledge_base")

  # 索引和加载都使用相同的环境变量
  embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

  # ✅ 正确：添加索引存在性检查，避免重复索引
  def get_or_create_vectorstore(docs, embeddings, persist_dir, collection_name):
      vectorstore = Chroma(
          persist_directory=persist_dir,
          embedding_function=embeddings,
          collection_name=collection_name,
      )
      if vectorstore._collection.count() == 0:
          print("索引为空，正在创建索引...")
          vectorstore.add_documents(docs)
      else:
          print(f"索引已存在，包含 {vectorstore._collection.count()} 个文档")
      return vectorstore
  ```
- **预防措施**：使用环境变量或配置文件统一管理 Embedding 模型、持久化路径、collection_name；加载后验证文档数量；定期备份向量数据库；升级 Chroma 版本前测试数据兼容性

---

### 7.2 高级 RAG 模式与优化

#### 概念解释

**正式定义**：高级 RAG 模式是在基础 RAG（检索→生成）之上的优化技术，包括查询改写（Query Rewriting）、多查询检索（Multi-Query）、混合检索（Hybrid Search）、重排序（Reranking）、上下文压缩（Contextual Compression）、父文档检索（Parent Document Retriever）、自适应检索（Adaptive RAG）、Self-RAG 等，旨在提升检索精度、减少幻觉、优化上下文使用。

**生活化比喻**：基础 RAG 就像用一个关键词在图书馆搜索——可能找到相关的书，也可能找不到。高级 RAG 就像有一个专业的图书管理员助手：① 先帮你把问题改写成更专业的检索词（查询改写）；② 用多个不同的检索词同时搜索（多查询）；③ 既用电脑搜索又用卡片目录搜索（混合检索）；④ 把找到的书按相关度重新排序（重排序）；⑤ 只把书中最相关的章节摘出来给你（上下文压缩）。

**核心价值**：解决基础 RAG 的检索精度不足、上下文冗余、幻觉等问题；在不增加 LLM 调用成本的前提下显著提升回答质量；是生产级 RAG 系统的必备优化。

#### 原理说明

```mermaid
graph TB
    subgraph 高级 RAG 架构
        Q[用户查询] --> QR[查询改写<br/>Query Rewriting]
        QR --> MQ[多查询生成<br/>Multi-Query]
        MQ --> HYBRID[混合检索<br/>向量 + BM25]
        HYBRID --> RRF[融合排序<br/>RRF]
        RRF --> RERANK[重排序<br/>Cross-Encoder]
        RERANK --> COMPRESS[上下文压缩<br/>LLM Extractor]
        COMPRESS --> PROMPT[注入 Prompt]
        PROMPT --> LLM[生成回答]
        LLM --> SELF[Self-RAG<br/>自我评估]
        SELF -->|需要更多信息| MQ
        SELF -->|回答充分| OUT[输出回答]
    end

    style QR fill:#e3f2fd
    style HYBRID fill:#f3e5f5
    style RERANK fill:#e8f5e9
    style SELF fill:#fff3e0
```

**高级 RAG 模式对比**：

| 模式 | 原理 | 提升点 | 成本增加 | 适用场景 |
|------|------|--------|---------|---------|
| **查询改写** | LLM 将用户问题改写为检索友好的查询 | 检索召回率 | 1次 LLM 调用 | 口语化查询、模糊问题 |
| **多查询检索** | 生成多个查询变体分别检索后合并 | 召回率、鲁棒性 | N次检索 | 复杂问题、多方面问题 |
| **混合检索** | 向量检索 + 关键词检索结果融合 | 精确匹配 + 语义 | 2次检索 | 通用场景、专业术语 |
| **重排序** | Cross-Encoder 对检索结果重新打分排序 | Top-K 精度 | 1次模型推理 | 高精度需求 |
| **上下文压缩** | LLM 提取文档中与查询相关的句子 | 上下文精简、精度 | 1次 LLM 调用 | 长文档、Token 敏感 |
| **父文档检索** | 小块检索 + 返回大块父文档 | 检索精度 + 上下文完整 | 存储增加 | 长文档、章节级文档 |
| **Self-RAG** | LLM 自我评估是否需要检索、回答是否充分 | 减少不必要检索、提升质量 | 多次 LLM 调用 | 高质量问答、自适应 |
| **Adaptive RAG** | 根据问题类型选择检索策略 | 效率 + 质量 | 1次分类调用 | 多样化问题类型 |

> 🎯 **面试高频考点**：如何优化 RAG 系统的检索质量？列举至少 5 种方法。答：① 优化分块策略（合理的 chunk_size 和 overlap，按语义分块）；② 查询改写（用 LLM 将用户问题改写为检索友好的查询）；③ 多查询检索（生成多个查询变体分别检索后合并）；④ 混合检索（向量检索 + BM25 关键词检索，用 RRF 融合）；⑤ 重排序（用 Cross-Encoder 模型对检索结果重新排序）；⑥ 上下文压缩（用 LLM 提取文档中与查询相关的句子）；⑦ 父文档检索（小块检索，返回包含小块的大块父文档）；⑧ 添加元数据过滤和丰富的 metadata。

#### 代码示例

**示例1：基础——混合检索（向量 + BM25）**

```python
# 安装：pip install langchain-retrievers rank_bm25
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# 准备文档
documents = [
    Document(page_content="Python 是一种高级编程语言，以简洁优雅著称。", metadata={"source": "编程入门"}),
    Document(page_content="Python 的装饰器是一种高阶函数，用于修改函数行为。", metadata={"source": "Python进阶"}),
    Document(page_content="JavaScript 是 Web 开发的核心语言，支持事件驱动编程。", metadata={"source": "Web开发"}),
    Document(page_content="向量数据库用于存储 Embedding 向量，支持相似度搜索。", metadata={"source": "AI基础设施"}),
    Document(page_content="RAG 通过检索外部文档增强 LLM 的生成能力，减少幻觉。", metadata={"source": "AI技术"}),
]

# 1. BM25 关键词检索器
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 3

# 2. 向量检索器
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(documents, embeddings)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 3. 混合检索（Ensemble Retriever）
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5],  # BM25 和向量各占 50%
)

# 4. 测试混合检索
query = "Python 装饰器是什么？"
results = ensemble_retriever.invoke(query)
print(f"查询: {query}")
print(f"混合检索结果 ({len(results)} 个文档):")
for i, doc in enumerate(results, 1):
    print(f"  [{i}] {doc.page_content}")
    print(f"      来源: {doc.metadata['source']}")

# 对比：纯向量检索可能漏掉"装饰器"的精确匹配
# 纯 BM25 可能不理解"是什么"的语义
# 混合检索兼顾两者

# 预期输出：Python 装饰器的文档排在第一位
```

**示例2：进阶——多查询检索 + 重排序**

```python
from langchain.retrievers import MultiQueryRetriever
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from operator import itemgetter

# 假设已有 vectorstore
# vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings())

# 1. 多查询检索器（自动生成多个查询变体）
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
multiquery_retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    llm=llm,
    include_original=True,  # 包含原始查询
)

# 测试多查询检索
query = "LangChain 框架的核心设计理念和主要组件是什么？"
results = multiquery_retriever.invoke(query)
print(f"原始查询: {query}")
print(f"多查询检索结果: {len(results)} 个文档（去重后）")

# 2. 重排序（使用 LLM 作为重排序器）
class LLMReranker:
    """使用 LLM 对检索结果进行重排序"""

    def __init__(self, llm, top_k=3):
        self.llm = llm
        self.top_k = top_k
        self.rerank_prompt = ChatPromptTemplate.from_template("""
        你是一个文档相关性评估专家。请评估以下文档与查询的相关性，给出 0-10 的分数。

        查询：{query}

        文档：
        {doc_content}

        请只输出一个数字（0-10），不要其他文字。
        相关性分数：""")

    def rerank(self, query, docs):
        scored_docs = []
        for doc in docs:
            score_str = self.llm.invoke(
                self.rerank_prompt.format_messages(query=query, doc_content=doc.page_content)
            ).content.strip()
            try:
                score = float(score_str)
            except ValueError:
                score = 0.0
            scored_docs.append((doc, score))

        # 按分数降序排列，取 Top-K
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored_docs[:self.top_k]]

reranker = LLMReranker(llm, top_k=3)

# 3. 构建完整的高级 RAG 链
def advanced_retrieve(query):
    """多查询检索 + 重排序"""
    docs = multiquery_retriever.invoke(query)
    reranked = reranker.rerank(query, docs)
    return reranked

def format_docs(docs):
    return "\n\n".join(f"[文档{i+1}]\n{doc.page_content}" for i, doc in enumerate(docs))

advanced_rag_chain = (
    {
        "context": itemgetter("question") | RunnableLambda(advanced_retrieve) | RunnableLambda(format_docs),
        "question": itemgetter("question"),
    }
    | ChatPromptTemplate.from_template("""
根据以下上下文回答问题。上下文已经过多查询检索和重排序优化。

上下文：
{context}

问题：{question}

回答：""")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

# 调用
result = advanced_rag_chain.invoke({"question": "LangChain 的核心设计理念是什么？"})
print(f"\n高级 RAG 回答:\n{result}")
```

**示例3：完整场景——父文档检索 + 上下文压缩**

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers import ContextualCompressionRetriever

# 1. 准备长文档（模拟技术文档）
long_docs = [
    Document(
        page_content="""
# LangChain 核心架构

## 设计理念
LangChain 的核心设计理念是组合优于继承。通过标准化的 Runnable 接口和 | 运算符，
开发者可以像搭积木一样构建 LLM 应用。每个组件都是独立的、可替换的、可测试的。

## 核心抽象
LangChain 包含六大核心抽象：Model I/O、Retrieval、Chain、Agents、Memory、Callbacks。
Model I/O 负责模型的输入输出，包括 Prompt Template、Chat Model、Output Parser。
Retrieval 负责文档检索，包括 Retriever 和 Document。

## LCEL 表达式语言
LCEL 是 LangChain 的表达式语言，通过 | 运算符组合 Runnable。
LCEL 支持流式、异步、批量、并行、回退、重试等高级特性。
""",
        metadata={"source": "LangChain架构文档", "chapter": "核心架构"}
    ),
    Document(
        page_content="""
# RAG 技术详解

## 什么是 RAG
RAG（Retrieval-Augmented Generation）是检索增强生成技术。
它通过检索外部知识库的相关文档，将其作为上下文注入 Prompt，
让 LLM 基于事实生成回答，减少幻觉。

## RAG 的工作流程
1. 文档索引：将知识库文档分块、向量化、存储到向量数据库
2. 查询检索：将用户问题向量化，在向量数据库中检索相关文档
3. 上下文构建：将检索到的文档格式化为上下文字符串
4. 生成回答：将上下文和问题一起传给 LLM，生成基于事实的回答

## RAG 的优化技术
包括查询改写、多查询检索、混合检索、重排序、上下文压缩、父文档检索等。
""",
        metadata={"source": "RAG技术文档", "chapter": "技术详解"}
    ),
]

# 2. 父文档检索器配置
# 父文档分块器（较大的块，作为最终返回的上下文）
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
# 子文档分块器（较小的块，用于检索匹配）
child_splitter = RecursiveCharacterTextSplitter(chunk_size=200)

# 向量数据库（存储子文档的向量）
vectorstore = Chroma(
    collection_name="parent_docs",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
)

# 文档存储（存储完整的父文档）
store = InMemoryStore()

# 创建父文档检索器
parent_retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

# 添加文档
parent_retriever.add_documents(long_docs)

# 3. 测试父文档检索
query = "LangChain 的设计理念是什么？"
results = parent_retriever.invoke(query)
print(f"查询: {query}")
print(f"父文档检索结果: {len(results)} 个文档")
for i, doc in enumerate(results, 1):
    print(f"\n[文档{i}] 来源: {doc.metadata['source']}")
    print(f"内容长度: {len(doc.page_content)} 字符")
    print(f"内容预览: {doc.page_content[:150]}...")

# 4. 添加上下文压缩
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
compressor = LLMChainExtractor.from_llm(llm)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=parent_retriever,
)

# 5. 构建 RAG 链
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from operator import itemgetter

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {
        "context": itemgetter("question") | compression_retriever | RunnableLambda(format_docs),
        "question": itemgetter("question"),
    }
    | ChatPromptTemplate.from_template("根据上下文回答：{context}\n\n问题：{question}\n\n回答：")
    | llm
    | StrOutputParser()
)

result = rag_chain.invoke({"question": "RAG 的工作流程包括哪些步骤？"})
print(f"\nRAG 回答:\n{result}")
# 预期输出：父文档检索返回完整的章节，上下文压缩只保留相关句子
```

#### 使用场景与最佳实践

**适用场景**：
- 生产级 RAG 系统（需要高精度和可靠性）
- 长文档问答（技术文档、法律合同、学术论文）
- 专业领域问答（医疗、法律、金融，对精度要求高）
- 多语言知识库（需要跨语言检索）
- 用户查询多样化（口语化、模糊、复杂）

**不适用场景**：
- 简单 FAQ（基础 RAG 足够，高级优化增加复杂度和成本）
- 对延迟极度敏感（高级 RAG 增加 200-1000ms 延迟）
- 小规模知识库（<100 文档，基础检索足够）
- 成本敏感（高级 RAG 增加多次 LLM 调用）

**最佳实践**：
1. **从基础 RAG 开始，逐步优化**：先实现基础 RAG，评估效果后再针对性地添加优化
2. **混合检索是性价比最高的优化**：向量 + BM25 混合检索，成本增加少，效果提升明显
3. **重排序对精度提升显著**：如果 Top-K 精度不够，优先添加重排序
4. **父文档检索适合长文档**：技术文档、合同等长文档用父文档检索，兼顾检索精度和上下文完整
5. **监控和评估**：建立 RAG 评估指标（命中率、MRR、回答质量评分），持续优化
6. **控制优化层级**：不要一次性添加所有优化，根据瓶颈选择对应的优化技术

**性能建议**：
- 多查询检索的查询数量控制在 3-5 个，过多会增加延迟和重复
- 重排序模型选择：bge-reranker 性价比高，Cohere Rerank 精度高但需要 API
- 上下文压缩使用小模型（gpt-4o-mini），减少成本和延迟
- 缓存常用查询的检索结果和重排序结果
- 异步执行多个查询的检索（MultiQueryRetriever 内部已支持并发）

#### 常见坑点

**坑点1：高级 RAG 优化导致延迟过高**
- **错误现象**：添加了多查询检索 + 重排序 + 上下文压缩后，回答延迟从 2 秒增加到 10 秒以上
- **根本原因**：每个优化都增加了额外的 LLM 调用或检索操作，多层叠加后延迟线性增长。多查询检索生成 3 个查询（1次 LLM + 3次检索），重排序对 10 个文档打分（10次 LLM），上下文压缩（1次 LLM），总共 12+ 次 LLM 调用
- **正确做法**：
  ```python
  # ❌ 错误：一次性添加所有优化，延迟爆炸
  # bad_chain = query_rewrite | multi_query(5) | hybrid_search | rerank(10) | compress | generate

  # ✅ 正确1：根据瓶颈选择优化，控制总延迟预算
  # 延迟预算：2秒（检索）+ 3秒（生成）= 5秒

  # 选择1-2个最有效的优化
  optimized_retriever = EnsembleRetriever(  # 混合检索（+200ms）
      retrievers=[bm25_retriever, vector_retriever],
      weights=[0.5, 0.5],
  )

  # 只在检索结果质量差时才用重排序（自适应）
  def conditional_rerank(query, docs):
      if len(docs) <= 3:
          return docs  # 结果少，不需要重排序
      return reranker.rerank(query, docs, top_k=3)  # 只对 Top-3 重排序

  # ✅ 正确2：使用更高效的重排序模型（不是 LLM）
  # 使用 bge-reranker 等专用重排序模型（推理速度比 LLM 快 10x）
  # from langchain.retrievers.document_compressors import CrossEncoderReranker
  # compressor = CrossEncoderReranker(model_name="BAAI/bge-reranker-base", top_n=3)

  # ✅ 正确3：并行执行无依赖的操作
  # 多查询检索内部已使用并发
  # 检索和查询改写可以并行
  from langchain_core.runnables import RunnableParallel
  parallel_step = RunnableParallel({
      "rewritten_query": rewrite_chain,
      "raw_docs": base_retriever,  # 原始查询的检索可以和改写并行
  })
  ```
- **预防措施**：设定延迟预算（如 5 秒），根据预算选择优化技术；优先使用低成本优化（混合检索、父文档检索），高成本优化（LLM 重排序、上下文压缩）按需使用；监控每个环节的耗时，识别瓶颈；使用专用模型（Cross-Encoder）替代 LLM 进行重排序

**坑点2：父文档检索的父文档过大导致上下文溢出**
- **错误现象**：使用父文档检索后，检索到的父文档内容过长（>5000 字符），注入 Prompt 后超出 LLM 上下文窗口或消耗大量 Token
- **根本原因**：父文档分块器的 chunk_size 设置过大，或者文档本身就是一个完整的长文档（如整章技术文档），父文档检索返回完整的父文档导致上下文过大
- **正确做法**：
  ```python
  # ❌ 错误：父文档分块过大
  # parent_splitter = RecursiveCharacterTextSplitter(chunk_size=5000)  # 太大
  # child_splitter = RecursiveCharacterTextSplitter(chunk_size=200)

  # ✅ 正确1：合理设置父文档大小（500-1500 字符）
  parent_splitter = RecursiveCharacterTextSplitter(
      chunk_size=1000,   # 父文档 1000 字符左右
      chunk_overlap=100,
  )
  child_splitter = RecursiveCharacterTextSplitter(
      chunk_size=200,    # 子文档 200 字符
      chunk_overlap=50,
  )

  # ✅ 正确2：添加上下文压缩，只保留相关部分
  from langchain.retrievers.document_compressors import LLMChainExtractor
  from langchain.retrievers import ContextualCompressionRetriever

  compressor = LLMChainExtractor.from_llm(ChatOpenAI(model="gpt-4o-mini"))
  compression_retriever = ContextualCompressionRetriever(
      base_compressor=compressor,
      base_retriever=parent_retriever,
  )
  # 压缩后只保留与查询相关的句子，大幅减少上下文长度

  # ✅ 正确3：限制返回的父文档数量
  parent_retriever = ParentDocumentRetriever(
      vectorstore=vectorstore,
      docstore=store,
      child_splitter=child_splitter,
      parent_splitter=parent_splitter,
      search_kwargs={"k": 2},  # 只返回 2 个父文档
  )

  # ✅ 正确4：使用 LLM 上下文窗口限制
  # 在 Prompt 中限制上下文长度，或使用 token 计数截断
  import tiktoken
  def truncate_docs(docs, max_tokens=3000):
      """截断文档列表，确保总 Token 不超过限制"""
      encoder = tiktoken.encoding_for_model("gpt-4o-mini")
      total_tokens = 0
      truncated = []
      for doc in docs:
          doc_tokens = len(encoder.encode(doc.page_content))
          if total_tokens + doc_tokens > max_tokens:
              break
          truncated.append(doc)
          total_tokens += doc_tokens
      return truncated
  ```
- **预防措施**：合理设置父文档 chunk_size（500-1500）；限制返回的父文档数量（k=2-3）；添加上下文压缩；监控每次请求的上下文 Token 数；设置 Token 上限和截断逻辑

---

> 💡 **深度讲解**
>
> RAG 是 LangChain 最核心的应用场景之一，也是生产级 LLM 应用最常用的架构。基础 RAG 的原理很简单——检索相关文档，注入 Prompt，让 LLM 基于事实回答。但要构建一个高质量的生产级 RAG 系统，需要考虑很多细节：文档分块策略、Embedding 模型选择、检索参数调优、元数据管理、检索质量评估、高级优化技术等。
>
> 文档分块是 RAG 的基础——分块太大，检索精度低（一个块包含太多不相关内容）；分块太小，上下文不完整（一个块无法涵盖完整的语义）。一般推荐 chunk_size 500-1000，overlap 10-20%。对于代码文档，可以按函数/类分块；对于长文档，可以使用父文档检索（小块检索，大块返回）。
>
> 检索质量是 RAG 系统的关键瓶颈。如果检索不到相关文档，LLM 就无法基于事实回答；如果检索到不相关的文档，会干扰 LLM 生成正确答案。提升检索质量的技术包括：查询改写（将口语化问题改写为专业检索词）、多查询检索（生成多个查询变体提升召回率）、混合检索（向量 + 关键词兼顾语义和精确匹配）、重排序（Cross-Encoder 提升 Top-K 精度）、上下文压缩（只保留相关句子）。
>
> 高级 RAG 优化是一个"按需添加"的过程——不要一次性添加所有优化，而是根据瓶颈选择对应的技术。如果检索召回率低，添加多查询检索或混合检索；如果 Top-K 精度低，添加重排序；如果上下文冗余，添加上下文压缩；如果文档很长，使用父文档检索。每个优化都有成本（延迟、Token、复杂度），需要在效果和成本之间取得平衡。
>
> 生产级 RAG 系统还需要考虑：索引更新（文档变更后如何更新向量数据库）、多租户隔离（不同用户的知识库隔离）、权限控制（用户只能检索有权限的文档）、可观测性（检索质量监控、回答质量评估）、成本控制（Embedding 和 LLM 调用成本）。这些都是从原型到生产必须跨越的鸿沟。

> **📝 精简总结**
>
> Retriever 是 RAG 的核心组件，根据查询返回相关 Document（page_content + metadata）；常见类型包括 VectorStoreRetriever（向量语义搜索）、BM25Retriever（关键词匹配）、EnsembleRetriever（混合检索）、ContextualCompressionRetriever（压缩+重排序）、MultiQueryRetriever（多查询）、ParentDocumentRetriever（父文档）；基础 RAG 链使用 `RunnableParallel({"context": retriever | format_docs, "question": passthrough}) | prompt | model | parser`；高级 RAG 优化包括查询改写、多查询检索、混合检索（RRF 融合）、重排序（Cross-Encoder）、上下文压缩（LLM Extractor）、父文档检索（小块检索+大块返回）、Self-RAG（自我评估）；最佳实践是从基础 RAG 开始，根据瓶颈逐步添加优化，混合检索性价比最高，重排序对精度提升显著；常见坑点是检索结果不相关（优化分块/模型匹配/查询改写）和高级优化导致延迟过高（控制优化层级/使用专用模型/并行执行）。

> **🎯 梯度练习题**
>
> **入门级**：
> 1. 使用 Chroma + OpenAIEmbeddings 构建一个向量数据库，存入 5 篇文档，实现基础检索
> 2. 构建一个基础 RAG 问答链，使用 `RunnableParallel` 并行检索和传递问题
> 3. 解释 Document 的 page_content 和 metadata 的作用，为文档添加 3 个 metadata 字段
>
> **进阶级**：
> 1. 实现混合检索（BM25 + 向量），对比纯向量检索在精确匹配查询上的效果差异
> 2. 使用 MultiQueryRetriever 实现多查询检索，打印生成的查询变体和检索结果
> 3. 实现父文档检索，配置 child_splitter=200 和 parent_splitter=1000，验证检索返回的是父文档
>
> **实战级**：
> 1. 构建一个完整的生产级 RAG 系统：文档加载→分块→向量化→混合检索→重排序→上下文压缩→RAG 链，包含元数据过滤和来源溯源
> 2. 设计一个 RAG 评估方案：使用 10 个标注问题，计算检索命中率（Hit Rate）、MRR、回答质量评分，对比基础 RAG 和高级 RAG 的效果
> 3. 优化一个 RAG 系统的延迟：当前延迟 8 秒（多查询+重排序+压缩+生成），通过并行执行、专用重排序模型、自适应优化等手段将延迟降低到 3 秒以内，同时保持回答质量

---

## 八、实战篇：Agent 系统构建与工具调用

### 8.1 Tool 工具定义与使用

#### 概念解释

**正式定义**：Tool（工具）是 LangChain 中 LLM 可以调用的外部功能封装，包含 `name`（工具名称）、`description`（工具描述，引导 LLM 何时调用）、`args_schema`（参数 schema，定义输入格式）、`run()`/`invoke()`（执行逻辑）四个核心属性。LLM 通过 Function Calling 机制决定是否调用工具、调用哪个工具、传入什么参数，工具执行后将结果返回给 LLM 继续生成回答。

**生活化比喻**：Tool 就像给 AI 助手配备的工具箱——里面有计算器（计算工具）、搜索引擎（搜索工具）、温度计（天气工具）、遥控器（控制工具）等。AI 助手在回答问题时，如果发现需要用到某个工具（比如用户问"12345 * 67890 等于多少"），它会从工具箱中取出计算器，输入参数，得到结果，然后基于结果回答用户。工具的 description 就像工具上的标签，告诉 AI"这个工具是用来做什么的，什么时候该用它"。

**核心价值**：扩展 LLM 的能力边界，使其可以访问实时数据、执行计算、操作外部系统；解决 LLM 的知识截止日期问题（通过搜索工具获取最新信息）和计算能力不足问题（通过代码执行工具）；是构建 Agent 系统的基础。

#### 原理说明

```mermaid
sequenceDiagram
    participant U as 用户
    participant LLM as 大语言模型
    participant TC as Tool Calling 层
    participant T as 工具执行

    U->>LLM: 用户问题（含工具描述）
    LLM->>LLM: 分析问题，决定是否需要工具
    alt 需要工具
        LLM->>TC: 输出 tool_calls（工具名+参数）
        TC->>T: 执行工具（传入参数）
        T->>T: 执行外部逻辑（API调用/计算/搜索）
        T-->>TC: 返回工具结果
        TC->>LLM: 将工具结果作为 ToolMessage 传入
        LLM->>LLM: 基于工具结果生成最终回答
        LLM-->>U: 返回回答
    else 不需要工具
        LLM-->>U: 直接回答
    end
```

**Tool 的核心机制**：
1. **工具描述注入**：工具的 name、description、args_schema 被转换为 Function Calling 的 function 定义，注入到 LLM 的系统提示或 API 参数中
2. **LLM 决策**：LLM 根据用户问题和工具描述，决定是否调用工具、调用哪个工具、传入什么参数
3. **工具执行**：LangChain 根据 LLM 输出的 tool_calls，查找对应的工具并执行，传入解析后的参数
4. **结果返回**：工具执行结果被包装为 ToolMessage（携带 tool_call_id），与之前的消息一起传回 LLM
5. **最终生成**：LLM 基于工具结果生成最终回答，可能继续调用其他工具（多轮工具调用）

**Tool 定义方式对比**：

| 定义方式 | 说明 | 优势 | 劣势 | 适用场景 |
|---------|------|------|------|---------|
| **@tool 装饰器** | 装饰 Python 函数 | 简单快捷，自动提取 docstring 和类型注解 | 灵活性有限 | 简单工具、快速原型 |
| **StructuredTool** | 显式构造工具对象 | 灵活，可自定义所有属性 | 代码稍多 | 复杂工具、生产环境 |
| **BaseTool 子类** | 继承 BaseTool 实现 | 最灵活，可实现复杂逻辑 | 代码最多 | 复杂工具、需要状态管理 |
| **Tool 类** | 简单封装函数 | 最简单 | 不支持结构化参数 | 单参数简单工具 |

> 🎯 **面试高频考点**：LangChain 中定义 Tool 的方式有哪些？@tool 装饰器的工作原理是什么？答：定义 Tool 的方式有四种：① @tool 装饰器（装饰 Python 函数，自动提取 docstring 作为 description，类型注解作为 args_schema）；② StructuredTool（显式构造，传入 name、description、func、args_schema）；③ 继承 BaseTool 子类（最灵活，实现 _run 方法）；④ Tool 类（简单封装单参数函数）。@tool 装饰器的工作原理是：读取函数的名称作为 name，读取 docstring 作为 description，读取函数参数的类型注解作为 args_schema（使用 Pydantic 自动生成），将函数包装为 StructuredTool 对象。

#### 代码示例

**示例1：基础——使用 @tool 装饰器定义工具**

```python
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# 1. 使用 @tool 装饰器定义工具
@tool
def calculator(expression: str) -> str:
    """执行数学计算并返回结果。

    Args:
        expression: 数学表达式字符串，如 "2 + 3 * 4"、"sqrt(16)"、"2**10"

    Returns:
        计算结果的字符串表示
    """
    try:
        # 使用安全的 eval（限制内置函数）
        import math
        safe_globals = {
            "sqrt": math.sqrt, "pow": math.pow, "log": math.log,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "pi": math.pi, "e": math.e, "abs": abs, "round": round,
        }
        result = eval(expression, {"__builtins__": {}}, safe_globals)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

@tool
def get_current_time() -> str:
    """获取当前的日期和时间。不需要任何参数。"""
    from datetime import datetime
    now = datetime.now()
    return f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')} (星期{['一','二','三','四','五','六','日'][now.weekday()]})"

@tool
def word_count(text: str) -> str:
    """统计文本的字数和字符数。

    Args:
        text: 需要统计的文本

    Returns:
        包含字数和字符数的统计结果
    """
    char_count = len(text)
    word_count = len(text.split())
    return f"统计结果: 字符数={char_count}, 单词数={word_count}"

# 2. 查看工具信息
print(f"工具名称: {calculator.name}")
print(f"工具描述: {calculator.description[:80]}...")
print(f"工具参数 Schema: {calculator.args_schema.schema()}")
print()

# 3. 绑定工具到模型
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
model_with_tools = model.bind_tools([calculator, get_current_time, word_count])

# 4. 测试工具调用
messages = [
    SystemMessage(content="你是一个智能助手，可以使用工具来回答问题。如果需要计算、获取时间或统计文本，请使用相应的工具。"),
    HumanMessage(content="请计算 12345 * 67890 等于多少？"),
]

response = model_with_tools.invoke(messages)
print(f"AI 回复内容: {response.content}")
print(f"工具调用: {response.tool_calls}")

# 如果有工具调用，执行工具并返回结果
if response.tool_calls:
    for tool_call in response.tool_calls:
        print(f"\n调用工具: {tool_call['name']}")
        print(f"参数: {tool_call['args']}")

        # 执行工具
        if tool_call["name"] == "calculator":
            tool_result = calculator.invoke(tool_call["args"])
        elif tool_call["name"] == "get_current_time":
            tool_result = get_current_time.invoke({})
        elif tool_call["name"] == "word_count":
            tool_result = word_count.invoke(tool_call["args"])
        else:
            tool_result = "未知工具"

        print(f"工具结果: {tool_result}")

        # 将工具结果添加到消息列表
        from langchain_core.messages import ToolMessage
        messages.append(response)
        messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))

    # 让 LLM 基于工具结果生成最终回答
    final_response = model_with_tools.invoke(messages)
    print(f"\n最终回答: {final_response.content}")

# 预期输出：AI 调用 calculator 工具，得到结果后生成最终回答
```

**示例2：进阶——使用 StructuredTool 和 Pydantic 定义结构化参数工具**

```python
from langchain_core.tools import StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# 1. 使用 Pydantic 定义工具参数
class SearchInput(BaseModel):
    """搜索工具的输入参数"""
    query: str = Field(description="搜索关键词，应简洁明确")
    max_results: int = Field(default=5, description="返回的最大结果数量，范围 1-10")
    language: str = Field(default="zh", description="搜索结果的语言，如 zh、en、ja")

# 2. 工具执行函数
def web_search(query: str, max_results: int = 5, language: str = "zh") -> str:
    """模拟网络搜索，返回搜索结果。"""
    # 实际项目中替换为真实的搜索 API（如 Tavily、SerpAPI）
    results = [
        f"[结果1] 关于 '{query}' 的最新信息...",
        f"[结果2] '{query}' 的详细介绍...",
        f"[结果3] '{query}' 相关的新闻报道...",
        f"[结果4] '{query}' 的技术文档...",
        f"[结果5] '{query}' 的社区讨论...",
    ]
    return f"搜索 '{query}'（语言: {language}），返回 {min(max_results, len(results))} 条结果:\n" + "\n".join(results[:max_results])

# 3. 使用 StructuredTool 构造工具
search_tool = StructuredTool(
    name="web_search",
    description="搜索互联网获取最新信息。当用户询问最新新闻、实时数据、或知识库中没有的信息时使用此工具。",
    func=web_search,
    args_schema=SearchInput,
)

# 4. 另一个工具：发送邮件
class EmailInput(BaseModel):
    """发送邮件的输入参数"""
    to: str = Field(description="收件人邮箱地址")
    subject: str = Field(description="邮件主题")
    body: str = Field(description="邮件正文内容")
    priority: str = Field(default="normal", description="邮件优先级: high, normal, low")

def send_email(to: str, subject: str, body: str, priority: str = "normal") -> str:
    """发送邮件给指定收件人。"""
    # 实际项目中替换为真实的邮件发送逻辑
    return f"邮件已发送\n收件人: {to}\n主题: {subject}\n优先级: {priority}\n正文: {body[:100]}..."

email_tool = StructuredTool(
    name="send_email",
    description="发送电子邮件给指定收件人。当用户要求发送邮件、通知他人、或分享信息时使用此工具。",
    func=send_email,
    args_schema=EmailInput,
)

# 5. 绑定工具并测试
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
model_with_tools = model.bind_tools([search_tool, email_tool])

# 测试搜索
response = model_with_tools.invoke([
    HumanMessage(content="搜索一下最新的 AI 新闻，返回 3 条结果")
])
print("=== 搜索测试 ===")
print(f"工具调用: {response.tool_calls}")
if response.tool_calls:
    result = search_tool.invoke(response.tool_calls[0]["args"])
    print(f"工具结果:\n{result}")

# 测试邮件
response2 = model_with_tools.invoke([
    HumanMessage(content="给 john@example.com 发一封高优先级邮件，主题是'会议通知'，内容是'明天下午3点在会议室A开会'")
])
print("\n=== 邮件测试 ===")
print(f"工具调用: {response2.tool_calls}")
if response2.tool_calls:
    result = email_tool.invoke(response2.tool_calls[0]["args"])
    print(f"工具结果:\n{result}")

# 预期输出：AI 正确解析参数并调用对应工具
```

**示例3：完整场景——使用 AgentExecutor 构建完整的工具调用 Agent**

```python
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage

# 1. 定义工具
@tool
def calculator(expression: str) -> str:
    """执行数学计算。输入数学表达式如 '2 + 3 * 4'。"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息。

    Args:
        city: 城市名称，如 '北京'、'上海'、'New York'
    """
    # 模拟天气数据
    weather_data = {
        "北京": "晴，25°C，湿度 40%，风速 3m/s",
        "上海": "多云，28°C，湿度 65%，风速 5m/s",
        "深圳": "阵雨，30°C，湿度 80%，风速 4m/s",
    }
    return weather_data.get(city, f"暂无 {city} 的天气数据")

@tool
def translate_text(text: str, target_lang: str) -> str:
    """将文本翻译为目标语言。

    Args:
        text: 要翻译的文本
        target_lang: 目标语言，如 '英文'、'日文'、'法文'
    """
    # 模拟翻译（实际使用翻译 API）
    translations = {
        ("你好", "英文"): "Hello",
        ("你好", "日文"): "こんにちは",
        ("谢谢", "英文"): "Thank you",
    }
    return translations.get((text, target_lang), f"[翻译] {text} → {target_lang}: [模拟翻译结果]")

tools = [calculator, get_weather, translate_text]

# 2. 创建 Prompt（必须包含 agent_scratchpad）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能助手，可以使用以下工具来帮助用户：\n"
               "- calculator: 数学计算\n"
               "- get_weather: 天气查询\n"
               "- translate_text: 文本翻译\n\n"
               "请根据用户问题选择合适的工具。如果不需要工具，直接回答。"),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

# 3. 创建模型和 Agent
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_openai_tools_agent(model, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,           # 打印执行过程
    max_iterations=5,       # 最大迭代次数，防止无限循环
    handle_parsing_errors=True,  # 自动处理解析错误
    return_intermediate_steps=True,  # 返回中间步骤，便于调试
)

# 4. 测试 Agent
print("=== 测试1: 计算 ===")
result1 = agent_executor.invoke({"input": "计算 (123 + 456) * 789 等于多少？"})
print(f"回答: {result1['output']}")

print("\n=== 测试2: 天气查询 ===")
result2 = agent_executor.invoke({"input": "北京今天天气怎么样？"})
print(f"回答: {result2['output']}")

print("\n=== 测试3: 翻译 ===")
result3 = agent_executor.invoke({"input": "把'你好'翻译成英文和日文"})
print(f"回答: {result3['output']}")

print("\n=== 测试4: 多工具组合 ===")
result4 = agent_executor.invoke({"input": "上海今天天气怎么样？用英文告诉我结果"})
print(f"回答: {result4['output']}")

print("\n=== 测试5: 不需要工具 ===")
result5 = agent_executor.invoke({"input": "你好，你能做什么？"})
print(f"回答: {result5['output']}")

# 预期输出：
# - 计算问题调用 calculator
# - 天气问题调用 get_weather
# - 翻译问题调用 translate_text
# - 多工具问题可能先查天气再翻译
# - 闲聊问题不调用工具，直接回答
```

#### 使用场景与最佳实践

**适用场景**：
- 需要实时数据的问答（新闻、天气、股票、汇率）
- 需要计算能力的任务（数学计算、数据处理、代码执行）
- 需要操作外部系统的任务（发送邮件、创建日历、操作数据库）
- 需要搜索能力的任务（网络搜索、知识库检索、文档查询）
- 多步骤复杂任务（需要多个工具协作完成）

**不适用场景**：
- 简单的常识性问答（直接用 LLM 即可，不需要工具）
- 高风险操作（删除数据、转账、发送邮件给外部）——需要人工确认
- 对延迟极度敏感（工具调用增加 100-2000ms 延迟）
- 工具不可靠或结果不稳定（会影响 LLM 生成质量）

**最佳实践**：
1. **工具描述清晰准确**：description 应说明工具的用途、何时使用、何时不使用，引导 LLM 正确决策
2. **参数 schema 详细**：使用 Pydantic Field 为每个参数添加 description，提供示例值，减少参数错误
3. **工具数量控制**：一次绑定 5-10 个工具，过多工具会增加 LLM 决策难度和 Token 消耗
4. **工具结果简洁**：工具返回结果应简洁明了，避免返回过长内容消耗 Token
5. **错误处理完善**：工具执行失败时返回有意义的错误信息，让 LLM 可以调整策略
6. **设置 max_iterations**：防止 Agent 无限循环，一般设置 5-10 次
7. **高风险操作加确认**：删除、发送、支付等高风险工具应配合 Human-in-the-loop 确认

**性能建议**：
- 工具执行应尽量快（<1秒），慢工具会显著增加总延迟
- 并行执行无依赖的工具调用（LangGraph 支持并行工具节点）
- 缓存常用工具的结果（如天气、汇率），减少重复调用
- 工具结果控制在 1000 Token 以内，过长结果会增加后续 LLM 调用成本
- 使用异步工具（_arun）提升并发性能

#### 常见坑点

**坑点1：LLM 不调用工具或调用错误的工具**
- **错误现象**：用户明确需要工具的问题，LLM 直接回答（不调用工具）；或调用了错误的工具（如用计算器搜索天气）
- **根本原因**：① 工具描述不清晰，LLM 无法判断何时使用；② 工具名称和参数有歧义；③ 模型能力不足（小模型工具调用能力弱）；④ 工具数量过多，LLM 选择困难；⑤ 系统提示中没有明确引导使用工具
- **正确做法**：
  ```python
  # ❌ 错误：工具描述模糊
  # @tool
  # def search(query: str) -> str:
  #     """搜索信息"""
  #     ...

  # ✅ 正确：工具描述清晰，说明何时使用
  @tool
  def web_search(query: str) -> str:
      """搜索互联网获取最新信息。

      何时使用：
      - 用户询问最新新闻、事件、动态
      - 用户询问实时数据（天气、股价、汇率）
      - 问题涉及 2024 年之后的信息（模型知识截止）
      - 用户明确要求"搜索一下"、"查一下"

      何时不使用：
      - 常识性问题（如"1+1等于几"）
      - 模型已有知识的问题（如"Python 是什么"）
      - 需要计算的问题（用 calculator 工具）

      Args:
          query: 搜索关键词，应简洁明确，如 "2024年AI最新进展"
      """
      ...

  # ✅ 正确：在系统提示中明确引导
  prompt = ChatPromptTemplate.from_messages([
      ("system", "你是一个智能助手。回答问题时遵循以下规则：\n"
                 "1. 如果问题需要实时信息（新闻、天气、数据），使用 web_search 工具\n"
                 "2. 如果问题需要计算，使用 calculator 工具\n"
                 "3. 如果问题需要翻译，使用 translate_text 工具\n"
                 "4. 如果不需要工具，直接回答\n"
                 "5. 不确定是否需要工具时，优先使用工具"),
      ...
  ])

  # ✅ 正确：使用能力强的模型
  model = ChatOpenAI(model="gpt-4o", temperature=0)  # gpt-4o 工具调用能力强于 gpt-4o-mini

  # ✅ 正确：控制工具数量，按场景分组
  # 不要一次绑定 20 个工具，根据场景选择 3-5 个相关工具
  # 可以使用路由机制，先判断问题类型，再绑定对应工具
  ```
- **预防措施**：为每个工具编写清晰的 description（含何时使用/不使用）；使用 Pydantic Field 为参数添加详细描述；在系统提示中明确工具使用规则；使用工具调用能力强的模型（gpt-4o、claude-3.5）；控制工具数量在 5-10 个；建立工具调用的评估和测试流程

**坑点2：工具调用参数格式错误导致执行失败**
- **错误现象**：LLM 调用工具时报 `ValidationError`、`TypeError`、`KeyError`，或工具收到错误的参数值（如字符串传入数字参数）
- **根本原因**：① 工具的 args_schema 定义不清晰，LLM 生成了错误格式的参数；② LLM 输出的 JSON 格式不标准（缺少引号、trailing comma）；③ 参数类型不匹配（LLM 生成字符串但工具期望整数）；④ 缺少必填参数；⑤ 枚举值不在允许范围内
- **正确做法**：
  ```python
  from langchain_core.pydantic_v1 import BaseModel, Field
  from typing import Literal, Optional
  from enum import Enum

  # ❌ 错误：参数定义不清晰
  # class SearchInput(BaseModel):
  #     query: str
  #     max_results: int
  #     language: str

  # ✅ 正确：使用 Pydantic Field 详细定义每个参数
  class SearchInput(BaseModel):
      query: str = Field(
          description="搜索关键词，应简洁明确，不超过50个字符",
          examples=["2024年AI最新进展", "北京天气"]
      )
      max_results: int = Field(
          default=5,
          description="返回的最大结果数量",
          ge=1,  # 大于等于1
          le=10  # 小于等于10
      )
      language: Literal["zh", "en", "ja"] = Field(  # 使用 Literal 限制枚举值
          default="zh",
          description="搜索结果的语言"
      )
      date_range: Optional[str] = Field(  # 可选参数
          default=None,
          description="日期范围，格式如 '2024-01-01:2024-12-31'"
      )

  # ✅ 正确：在工具描述中提供参数示例
  @tool
  def search(query: str, max_results: int = 5) -> str:
      """搜索互联网。

      Args:
          query: 搜索关键词，如 "AI 最新新闻"
          max_results: 返回结果数量，默认 5，范围 1-10

      示例:
          search(query="Python 教程", max_results=3)
      """
      ...

  # ✅ 正确：使用 handle_parsing_errors 自动处理解析错误
  agent_executor = AgentExecutor(
      agent=agent,
      tools=tools,
      handle_parsing_errors=True,  # 解析错误时自动让 LLM 修正
      max_iterations=5,
  )

  # ✅ 正确：工具内部添加参数校验和错误处理
  @tool
  def safe_calculator(expression: str) -> str:
      """安全的数学计算器"""
      if not expression or not isinstance(expression, str):
          return "错误：请提供有效的数学表达式字符串"
      try:
          # 校验表达式只包含安全字符
          import re
          if not re.match(r'^[\d\s\+\-\*\/\(\)\.\%\^\*]+$', expression):
              return f"错误：表达式包含不支持的字符"
          result = eval(expression, {"__builtins__": {}}, {})
          return f"计算结果: {expression} = {result}"
      except Exception as e:
          return f"计算失败: {str(e)}，请检查表达式格式"
  ```
- **预防措施**：使用 Pydantic Field 为每个参数添加 description、examples、ge/le 约束；使用 Literal 或 Enum 限制枚举值；可选参数使用 Optional 并设置默认值；在工具描述中提供参数示例；启用 handle_parsing_errors；工具内部添加参数校验和错误处理；建立工具调用的单元测试，覆盖各种参数组合

---

### 8.2 ReAct Agent 与 Tool Calling Agent

#### 概念解释

**正式定义**：ReAct（Reasoning + Acting）Agent 是一种通过"思考-行动-观察"循环自主决策的 Agent 模式——LLM 先思考（Reasoning）需要做什么，然后决定行动（Acting，调用工具），接收观察结果（Observation，工具返回），再思考下一步，直到给出最终回答。Tool Calling Agent 是基于 LLM 原生 Function Calling 能力的 Agent 模式——LLM 直接输出结构化的工具调用请求（tool_calls），框架执行工具后将结果返回，比 ReAct 更高效、更可靠。

**生活化比喻**：ReAct Agent 就像一个边想边做的侦探——他先思考"我需要查什么线索"（Reasoning），然后去调查（Acting），得到线索后观察分析（Observation），再思考下一步查什么，直到破案。Tool Calling Agent 就像一个有经验的管家——你告诉他需求，他直接告诉你"我需要用吸尘器打扫客厅"（结构化工具调用），不需要大声说出思考过程，更高效更直接。

**核心价值**：ReAct Agent 适用于不支持 Function Calling 的模型，通过 Prompt 引导 LLM 输出思考和行动；Tool Calling Agent 利用模型原生能力，更高效可靠，是当前主流方案；两者都支持多轮工具调用、复杂任务分解、自主决策，是构建 Agent 系统的核心模式。

#### 原理说明

```mermaid
graph TB
    subgraph ReAct Agent 循环
        Q[用户问题] --> TH[思考 Reasoning<br/>LLM 分析问题，决定下一步]
        TH --> ACT{需要工具?}
        ACT -->|是| ACTION[行动 Acting<br/>调用工具]
        ACTION --> OBS[观察 Observation<br/>获取工具结果]
        OBS --> TH
        ACT -->|否| ANS[最终回答]
    end

    subgraph Tool Calling Agent
        Q2[用户问题] --> TC[LLM 输出 tool_calls<br/>结构化工具调用]
        TC --> HAS{有 tool_calls?}
        HAS -->|是| EXEC[执行工具<br/>ToolNode]
        EXEC --> TC2[将 ToolMessage 传回 LLM]
        TC2 --> TC
        HAS -->|否| ANS2[最终回答]
    end

    style TH fill:#e3f2fd
    style TC fill:#f3e5f5
    style EXEC fill:#e8f5e9
```

**ReAct vs Tool Calling 对比**：

| 维度 | ReAct Agent | Tool Calling Agent |
|------|------------|-------------------|
| 原理 | Prompt 引导 LLM 输出"思考-行动-观察"文本 | LLM 原生 Function Calling 输出结构化 tool_calls |
| 模型要求 | 任何 LLM（通过 Prompt 引导） | 必须支持 Function Calling 的模型 |
| 效率 | 较低（思考过程消耗 Token，需要解析文本） | 较高（结构化输出，无需解析文本） |
| 可靠性 | 较低（文本解析容易出错，格式不稳定） | 较高（结构化输出，格式稳定） |
| 可观测性 | 思考过程可见（可调试） | 思考过程不可见（黑盒） |
| 多工具调用 | 支持（逐轮调用） | 支持（可并行调用多个工具） |
| 推荐度 | ⭐⭐（遗留方案） | ⭐⭐⭐⭐⭐（推荐） |
| LangChain 实现 | `create_react_agent` | `create_openai_tools_agent` / `create_tool_calling_agent` |

**Agent 执行流程（Tool Calling）**：
1. 用户输入传入 Agent，包含系统提示、对话历史、工具定义
2. LLM 分析问题，决定是否调用工具，输出 tool_calls（可能为空或多个）
3. 如果有 tool_calls，框架执行对应工具，将结果包装为 ToolMessage
4. 将 ToolMessage 加入消息历史，再次调用 LLM
5. 重复 2-4，直到 LLM 不再调用工具，输出最终回答
6. AgentExecutor 管理循环，设置 max_iterations 防止无限循环

> 🎯 **面试高频考点**：ReAct 和 Tool Calling 的区别是什么？为什么推荐使用 Tool Calling？答：ReAct 通过 Prompt 引导 LLM 输出"思考-行动-观察"的文本格式，适用于不支持 Function Calling 的模型，但效率低（思考过程消耗 Token）、可靠性差（文本解析容易出错）。Tool Calling 利用 LLM 原生的 Function Calling 能力，输出结构化的 tool_calls，效率高（无需解析文本）、可靠性好（格式稳定）、支持并行调用多个工具。推荐使用 Tool Calling 因为：① 所有现代模型都支持 Function Calling；② 结构化输出比文本解析更可靠；③ 支持并行工具调用提升效率；④ LangChain 提供了 create_openai_tools_agent 等便捷的创建函数。

#### 代码示例

**示例1：基础——使用 create_openai_tools_agent 构建 Tool Calling Agent**

```python
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 1. 定义工具
@tool
def get_weather(city: str) -> str:
    """获取指定城市的当前天气。

    Args:
        city: 城市名称，如 '北京'、'上海'、'New York'
    """
    weather = {
        "北京": "晴，25°C，南风3级",
        "上海": "多云，28°C，东南风4级",
        "广州": "阵雨，30°C，南风2级",
    }
    return weather.get(city, f"暂无{city}的天气数据")

@tool
def get_news(category: str = "科技") -> str:
    """获取最新新闻。

    Args:
        category: 新闻分类，可选 '科技'、'财经'、'体育'、'娱乐'，默认 '科技'
    """
    news = {
        "科技": "1. AI 大模型技术取得新突破\n2. 量子计算机实现 1000 量子比特\n3. 新能源汽车销量创新高",
        "财经": "1. A股三大指数集体上涨\n2. 央行宣布降准 0.5 个百分点\n3. 国际油价突破 80 美元",
        "体育": "1. 中国队获得世锦赛金牌\n2. NBA 季后赛激战正酣\n3. 世界杯预选赛即将开始",
    }
    return news.get(category, f"暂无{category}分类的新闻")

@tool
def calculator(expression: str) -> str:
    """执行数学计算。输入数学表达式如 '2 + 3 * 4'。"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"

tools = [get_weather, get_news, calculator]

# 2. 创建 Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能助手，可以使用工具获取信息。"
               "如果需要天气、新闻或计算，请使用相应工具。"
               "回答要简洁明了。"),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

# 3. 创建 Agent
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_openai_tools_agent(model, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True,
)

# 4. 测试
print("=== 测试1: 单工具调用 ===")
result = agent_executor.invoke({"input": "北京今天天气怎么样？"})
print(f"回答: {result['output']}\n")

print("=== 测试2: 多工具调用 ===")
result = agent_executor.invoke({"input": "上海天气怎么样？另外告诉我最新的科技新闻"})
print(f"回答: {result['output']}\n")

print("=== 测试3: 工具+计算组合 ===")
result = agent_executor.invoke({"input": "如果北京气温 25°C，上海 28°C，计算平均气温是多少？"})
print(f"回答: {result['output']}\n")

print("=== 测试4: 不需要工具 ===")
result = agent_executor.invoke({"input": "你好，介绍一下你自己"})
print(f"回答: {result['output']}")
```

**示例2：进阶——使用 LangGraph 构建更可控的 Tool Calling Agent**

```python
# 安装：pip install langgraph
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition

# 1. 定义状态
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

# 2. 定义工具
@tool
def search(query: str) -> str:
    """搜索互联网获取信息"""
    return f"搜索结果：关于'{query}'的最新信息..."

@tool
def calculate(expression: str) -> str:
    """执行数学计算"""
    try:
        return f"结果: {eval(expression, {'__builtins__': {}}, {})}"
    except Exception as e:
        return f"错误: {e}"

tools = [search, calculate]

# 3. 创建模型（绑定工具）
model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)

# 4. 定义节点
def agent_node(state: AgentState) -> dict:
    """Agent 节点：调用 LLM"""
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

# 5. 构建图
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

workflow.set_entry_point("agent")

# 条件边：根据 LLM 输出决定下一步
workflow.add_conditional_edges(
    "agent",
    tools_condition,  # 内置条件：有 tool_calls 则去 tools，否则去 END
    {
        "tools": "tools",
        END: END,
    }
)

# 工具执行后回到 agent
workflow.add_edge("tools", "agent")

# 编译图
app = workflow.compile()

# 6. 运行
print("=== LangGraph Agent ===")
result = app.invoke({
    "messages": [HumanMessage(content="搜索最新的 AI 新闻，然后计算 2024 * 25 是多少")]
})

# 输出最终回答
final_message = result["messages"][-1]
print(f"\n最终回答: {final_message.content}")

# 输出执行过程
print("\n=== 执行过程 ===")
for i, msg in enumerate(result["messages"]):
    if hasattr(msg, 'tool_calls') and msg.tool_calls:
        print(f"步骤{i}: [AI 调用工具] {msg.tool_calls}")
    elif isinstance(msg, ToolMessage):
        print(f"步骤{i}: [工具结果] {msg.content[:80]}...")
    else:
        print(f"步骤{i}: [{msg.type}] {msg.content[:80]}...")

# 预期输出：Agent 先调用 search，再调用 calculate，最后生成综合回答
```

**示例3：完整场景——带记忆和 Human-in-the-loop 的生产级 Agent**

```python
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# 1. 定义状态（包含消息和用户信息）
class State(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    user_name: str

# 2. 定义工具
@tool
def get_user_profile(name: str) -> str:
    """获取用户的个人资料和偏好。

    Args:
        name: 用户名
    """
    profiles = {
        "小明": "年龄25，职业程序员，偏好技术新闻，使用 Python 和 JavaScript",
        "小红": "年龄23，职业设计师，偏好设计和艺术新闻，使用 Figma 和 Photoshop",
    }
    return profiles.get(name, f"暂无用户 {name} 的资料")

@tool
def recommend_news(interest: str) -> str:
    """根据用户兴趣推荐新闻。

    Args:
        interest: 用户兴趣标签，如 '技术'、'设计'、'财经'
    """
    news = {
        "技术": "推荐：1. AI 大模型新进展 2. Rust 2.0 发布 3. WebAssembly 新标准",
        "设计": "推荐：1. 2024 UI 设计趋势 2. Figma 新功能介绍 3. 色彩心理学在设计中的应用",
    }
    return news.get(interest, f"暂无{interest}相关新闻推荐")

@tool
def send_notification(user: str, message: str) -> str:
    """发送通知给用户。

    Args:
        user: 接收通知的用户名
        message: 通知内容
    """
    return f"通知已发送给 {user}：{message}"

tools = [get_user_profile, recommend_news, send_notification]

# 3. 创建模型
model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)

# 4. 定义节点
def agent_node(state: State) -> dict:
    """Agent 节点，注入用户信息到系统提示"""
    messages = state["messages"]
    user_name = state.get("user_name", "用户")

    # 构建带用户信息的系统提示
    system_msg = f"你是一个个性化助手。当前用户是 {user_name}。"
    from langchain_core.messages import SystemMessage
    full_messages = [SystemMessage(content=system_msg)] + messages

    response = model.invoke(full_messages)
    return {"messages": [response]}

# 5. 构建图（带持久化）
workflow = StateGraph(State)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {"tools": "tools", END: END}
)
workflow.add_edge("tools", "agent")

# 使用 MemorySaver 持久化（支持多轮对话记忆）
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# 6. 多轮对话测试
config = {"configurable": {"thread_id": "user_001"}}

print("=== 多轮对话 Agent ===")
print(f"配置: thread_id={config['configurable']['thread_id']}\n")

# 第一轮：设置用户信息并提问
result1 = app.invoke(
    {
        "messages": [HumanMessage(content="你好，我是小明")],
        "user_name": "小明",
    },
    config=config
)
print(f"轮次1 - AI: {result1['messages'][-1].content}")

# 第二轮：利用记忆和用户信息
result2 = app.invoke(
    {"messages": [HumanMessage(content="根据我的资料，推荐一些新闻")]},
    config=config
)
print(f"轮次2 - AI: {result2['messages'][-1].content}")

# 第三轮：继续对话
result3 = app.invoke(
    {"messages": [HumanMessage(content="给我发一条通知，内容是'记得明天开会'")]},
    config=config
)
print(f"轮次3 - AI: {result3['messages'][-1].content}")

# 查看执行历史
print("\n=== 完整消息历史 ===")
for i, msg in enumerate(result3["messages"]):
    role = getattr(msg, 'type', 'unknown')
    content = msg.content[:100] if msg.content else "[工具调用]"
    print(f"  [{i}] {role}: {content}")

# 预期输出：Agent 记住用户是小明，调用 get_user_profile 获取资料，
# 调用 recommend_news 推荐技术新闻，调用 send_notification 发送通知
```

#### 使用场景与最佳实践

**适用场景**：
- 多步骤复杂任务（需要多个工具协作）
- 需要自主决策的任务（LLM 决定调用哪些工具、按什么顺序）
- 需要实时数据的问答（搜索、天气、股票）
- 需要操作外部系统的任务（邮件、日历、数据库）
- 个性化助手（结合用户信息和记忆）

**不适用场景**：
- 简单的单步任务（直接用链即可，不需要 Agent 的循环开销）
- 高风险操作（需要严格的流程控制和人工确认，用 LangGraph 显式图更合适）
- 对延迟极度敏感（Agent 循环可能需要多轮 LLM 调用）
- 需要精确控制执行流程的场景（Agent 的自主决策不可控）

**最佳实践**：
1. **优先使用 Tool Calling**：所有现代模型都支持 Function Calling，Tool Calling 比 ReAct 更高效可靠
2. **使用 LangGraph 替代 AgentExecutor**：LangGraph 提供更灵活的控制、持久化、HITL、流式输出，是生产级 Agent 的首选
3. **设置 max_iterations**：防止 Agent 无限循环，一般设置 5-10 次
4. **工具描述清晰**：工具的 name、description、args_schema 要清晰准确，引导 LLM 正确调用
5. **添加记忆和持久化**：生产环境使用 Checkpointer 持久化状态，支持多轮对话和中断恢复
6. **高风险操作加 HITL**：删除、发送、支付等高风险工具使用 Human-in-the-loop 确认
7. **监控和评估**：记录 Agent 的执行过程（工具调用、思考过程），建立评估指标（成功率、工具调用准确率、平均迭代次数）

**性能建议**：
- 使用小模型（gpt-4o-mini）处理简单的工具调用决策，大模型（gpt-4o）处理复杂推理
- 并行执行无依赖的工具调用（LangGraph 的 ToolNode 支持并行）
- 缓存常用工具的结果，减少重复调用
- 控制工具数量（5-10 个），过多工具增加 LLM 决策时间和 Token 消耗
- 使用流式输出提升用户体验（首字延迟降低 50-80%）

#### 常见坑点

**坑点1：Agent 无限循环或迭代次数过多**
- **错误现象**：Agent 反复调用同一个工具，或在多个工具之间循环，超过 max_iterations 后报错，或消耗大量 Token
- **根本原因**：① 工具返回结果不充分，LLM 无法得到足够信息；② 工具描述有歧义，LLM 反复尝试不同参数；③ 缺少明确的终止条件；④ 工具结果格式不一致，LLM 无法解析；⑤ 任务过于复杂，超出模型能力
- **正确做法**：
  ```python
  # ✅ 正确1：设置合理的 max_iterations
  agent_executor = AgentExecutor(
      agent=agent,
      tools=tools,
      max_iterations=5,           # 最多 5 次迭代
      max_execution_time=30,      # 最多 30 秒超时
      early_stopping_method="force",  # 超时时强制停止
  )

  # ✅ 正确2：工具返回充分的信息，避免反复调用
  @tool
  def search(query: str) -> str:
      """搜索工具"""
      results = do_search(query)
      if not results:
          # 返回明确的"无结果"信息，让 LLM 知道不需要重试
          return f"搜索 '{query}' 未找到相关结果。建议尝试其他关键词或直接回答。"
      # 返回结构化的结果，包含足够信息
      return "\n".join([f"[{i+1}] {r.title}: {r.summary}" for i, r in enumerate(results[:5])])

  # ✅ 正确3：在系统提示中明确终止条件
  prompt = ChatPromptTemplate.from_messages([
      ("system", "你是一个智能助手。遵循以下规则：\n"
                 "1. 最多调用 3 次工具，如果仍无法解决，直接给出最佳猜测回答\n"
                 "2. 如果工具返回'无结果'，不要重复调用同一工具\n"
                 "3. 得到足够信息后，立即给出最终回答，不要不必要地调用工具\n"
                 "4. 如果任务无法完成，明确告知用户原因"),
      ...
  ])

  # ✅ 正确4：使用 LangGraph 显式控制流程，避免不可控的循环
  # 在 LangGraph 中可以添加计数器节点，超过限制直接 END
  def should_continue(state):
      iterations = len([m for m in state["messages"] if m.type == "ai"])
      if iterations >= 5:
          return END
      return "agent"
  ```
- **预防措施**：设置 max_iterations 和 max_execution_time；工具返回充分且结构化的信息；在系统提示中明确终止条件；使用 LangGraph 显式控制流程；监控 Agent 的平均迭代次数，异常时告警；建立 Agent 执行日志，分析循环原因

**坑点2：Agent 不调用工具或调用错误工具**
- **错误现象**：用户明确需要工具的问题，Agent 直接回答（不调用工具）；或调用了错误的工具（如用搜索工具做计算）；或忽略工具结果直接回答
- **根本原因**：① 工具描述不清晰，LLM 无法判断何时使用；② 系统提示中没有明确引导使用工具；③ 模型能力不足（小模型工具调用能力弱）；④ 工具数量过多，LLM 选择困难；⑤ 工具结果与问题不相关，LLM 忽略结果
- **正确做法**：
  ```python
  # ✅ 正确1：工具描述清晰，包含"何时使用"和"何时不使用"
  @tool
  def web_search(query: str) -> str:
      """搜索互联网获取最新信息。

      何时使用：
      - 用户询问最新新闻、事件、动态
      - 用户询问实时数据（天气、股价、汇率）
      - 问题涉及模型知识截止日期之后的信息
      - 用户明确要求"搜索"、"查一下"

      何时不使用：
      - 常识性问题（如"1+1等于几"）
      - 模型已有知识的问题
      - 需要计算的问题（用 calculator）

      Args:
          query: 搜索关键词，简洁明确
      """
      ...

  # ✅ 正确2：在系统提示中明确工具使用规则
  prompt = ChatPromptTemplate.from_messages([
      ("system", "你是一个智能助手，拥有以下工具：\n"
                 "- web_search: 搜索互联网（用于实时信息、新闻）\n"
                 "- calculator: 数学计算（用于任何计算任务）\n"
                 "- get_weather: 天气查询（用于天气问题）\n\n"
                 "规则：\n"
                 "1. 遇到需要实时信息的问题，必须使用 web_search\n"
                 "2. 遇到计算问题，必须使用 calculator\n"
                 "3. 遇到天气问题，必须使用 get_weather\n"
                 "4. 工具返回结果后，必须基于结果回答，不要忽略\n"
                 "5. 不确定是否需要工具时，优先使用工具"),
      ...
  ])

  # ✅ 正确3：使用工具调用能力强的模型
  model = ChatOpenAI(model="gpt-4o", temperature=0)  # gpt-4o > gpt-4o-mini

  # ✅ 正确4：控制工具数量，按场景分组
  # 不要一次绑定 20 个工具，根据场景选择 3-5 个
  # 可以先分类问题，再绑定对应工具
  def get_tools_for_category(category):
      if category == "技术":
          return [search, calculator, code_executor]
      elif category == "生活":
          return [weather, search, translator]
      return [search]

  # ✅ 正确5：在 Prompt 中提供 Few-shot 示例
  prompt = ChatPromptTemplate.from_messages([
      ("system", "..."),
      ("human", "北京今天天气怎么样？"),
      ("ai", "", tool_calls=[{"name": "get_weather", "args": {"city": "北京"}, "id": "1"}]),
      ("tool", "晴，25°C", tool_call_id="1"),
      ("ai", "北京今天晴，气温 25°C。"),
      ("human", "{input}"),
      MessagesPlaceholder("agent_scratchpad"),
  ])
  ```
- **预防措施**：工具描述包含"何时使用/不使用"；系统提示明确工具使用规则；使用工具调用能力强的模型；控制工具数量在 5-10 个；提供 Few-shot 示例；建立工具调用准确率的评估指标；定期审查 Agent 的执行日志，识别不调用或错调用的模式

---

> 💡 **深度讲解**
>
> Agent 是 LangChain 生态中最强大也最复杂的应用模式。与简单的链（Chain）不同，Agent 具有自主决策能力——它可以根据问题决定调用哪些工具、按什么顺序调用、是否需要多轮调用。这种自主性使得 Agent 可以处理复杂的多步骤任务，但也带来了不可控性——你无法精确预测 Agent 会走哪条路径。
>
> Tool 的定义是 Agent 系统的基础。一个好的 Tool 定义应该包含清晰的 name（简洁明了）、description（说明用途、何时使用、何时不使用）、args_schema（使用 Pydantic 详细定义每个参数的类型、描述、约束、示例）。工具定义的质量直接决定了 LLM 能否正确调用工具——描述模糊会导致 LLM 不调用或错调用，参数 schema 不清晰会导致参数格式错误。
>
> ReAct 和 Tool Calling 是两种主要的 Agent 模式。ReAct 通过 Prompt 引导 LLM 输出"思考-行动-观察"的文本，适用于不支持 Function Calling 的模型，但效率低、可靠性差。Tool Calling 利用 LLM 原生的 Function Calling 能力，输出结构化的 tool_calls，效率高、可靠性好，是当前主流方案。所有现代模型（GPT-4o、Claude 3.5、Gemini Pro）都支持 Function Calling，新项目应优先使用 Tool Calling。
>
> 从 AgentExecutor 到 LangGraph 是 Agent 开发的重要演进。AgentExecutor 是 LangChain 早期的 Agent 执行器，封装了 ReAct/Tool Calling 循环，简单易用但不够灵活——无法自定义执行流程、不支持持久化、不支持 Human-in-the-loop。LangGraph 基于状态机模型，提供了完全的流程控制、持久化、HITL、流式输出、多 Agent 协作等生产级特性，是构建生产级 Agent 的首选。对于简单的 Agent，可以用 AgentExecutor 快速原型；对于生产级 Agent，应迁移到 LangGraph。
>
> Agent 系统的常见挑战包括：无限循环（设置 max_iterations）、不调用/错调用工具（优化工具描述和系统提示）、参数格式错误（使用 Pydantic 和 handle_parsing_errors）、高风险操作（配合 HITL 人工确认）、可观测性不足（记录执行过程和工具调用）。解决这些挑战需要从工具定义、Prompt 设计、执行控制、监控评估等多个维度入手。

> **📝 精简总结**
>
> Tool 是 LLM 可调用的外部功能封装，包含 name、description、args_schema、run() 四要素；定义方式有 @tool 装饰器（简单快捷）、StructuredTool（灵活）、BaseTool 子类（最灵活）、Tool 类（最简单）；工具描述应包含"何时使用/不使用"，参数使用 Pydantic Field 详细定义；ReAct Agent 通过"思考-行动-观察"循环自主决策，适用于不支持 Function Calling 的模型；Tool Calling Agent 利用 LLM 原生 Function Calling 输出结构化 tool_calls，效率高、可靠性好，是推荐方案；AgentExecutor 封装了 Agent 循环，简单易用但不够灵活；LangGraph 提供完全的流程控制、持久化、HITL，是生产级首选；最佳实践包括优先使用 Tool Calling、使用 LangGraph、设置 max_iterations、工具描述清晰、高风险操作加 HITL；常见坑点是无限循环（设置 max_iterations/明确终止条件）和不调用/错调用工具（优化描述/系统提示/Few-shot/强模型）。

> **🎯 梯度练习题**
>
> **入门级**：
> 1. 使用 @tool 装饰器定义 3 个工具（计算器、天气查询、翻译），打印每个工具的 name、description、args_schema
> 2. 使用 create_openai_tools_agent + AgentExecutor 构建一个简单 Agent，测试单工具调用和多工具调用
> 3. 解释 ReAct 和 Tool Calling 的区别，说明为什么推荐使用 Tool Calling
>
> **进阶级**：
> 1. 使用 StructuredTool + Pydantic 定义一个结构化参数工具（如发送邮件，包含 to/subject/body/priority），验证参数校验
> 2. 使用 LangGraph 构建一个 Tool Calling Agent，包含 agent 节点、tools 节点、条件边，测试多轮工具调用
> 3. 为 Agent 添加记忆（MemorySaver Checkpointer），实现多轮对话，验证 Agent 能记住之前的对话内容
>
> **实战级**：
> 1. 构建一个生产级 Agent：5+ 工具（搜索、计算、天气、邮件、数据库）、LangGraph 状态机、持久化、Human-in-the-loop（高风险操作需确认）、流式输出、执行日志记录
> 2. 设计一个 Agent 评估方案：定义 20 个测试问题（覆盖单工具、多工具、不需要工具、工具失败等场景），评估工具调用准确率、任务成功率、平均迭代次数、Token 消耗
> 3. 优化一个 Agent 的工具调用准确率：当前准确率 60%，通过优化工具描述、系统提示、Few-shot 示例、模型选择等手段将准确率提升到 90%+，记录每个优化手段的效果

---

## 九、实战篇：从 LCEL 到生产部署

### 9.1 LangServe API 部署

#### 概念解释

**正式定义**：LangServe 是 LangChain 团队推出的部署工具，可将 LCEL 链（Runnable）一键部署为 REST API 服务，支持同步调用、流式输出、批量处理、异步调用、输入输出 Schema 自动生成、Playground 调试界面等功能。LangServe 基于 FastAPI 和 Pydantic，自动为链生成 `/invoke`、`/stream`、`/batch` 等 API 端点。

**生活化比喻**：LangServe 就像餐厅的外卖平台——你的链（菜品）做好后，LangServe 帮你把它放到外卖平台上，顾客（客户端）可以通过手机 APP（API 调用）下单（invoke）、看实时制作过程（stream）、批量订餐（batch）。LangServe 还提供了一个"开放式厨房"（Playground），让顾客可以看到菜品的制作过程并现场调试。

**核心价值**：将 LCEL 链快速部署为生产级 API，无需手动编写 FastAPI 路由、请求解析、响应格式化、流式传输等样板代码；自动生成 OpenAPI 文档和 Playground 调试界面；支持所有 LCEL 执行模式（invoke/stream/batch/async）；与 LangSmith 深度集成，自动追踪 API 调用。

#### 原理说明

```mermaid
graph TB
    subgraph LangServe 架构
        subgraph API 层
            INVOKE[/invoke<br/>同步调用]
            STREAM[/stream<br/>流式输出]
            BATCH[/batch<br/>批量处理]
            PLAYGROUND[/playground<br/>调试界面]
        end
        subgraph 核心层
            ROUTER[FastAPI 路由<br/>自动生成]
            SCHEMA[Pydantic Schema<br/>输入输出校验]
            HANDLER[Runnable Handler<br/>链执行管理]
        end
        CHAIN[LCEL Chain<br/>Runnable]
    end
    INVOKE --> ROUTER
    STREAM --> ROUTER
    BATCH --> ROUTER
    PLAYGROUND --> ROUTER
    ROUTER --> SCHEMA
    SCHEMA --> HANDLER
    HANDLER --> CHAIN
    style ROUTER fill:#e3f2fd
    style SCHEMA fill:#f3e5f5
    style HANDLER fill:#e8f5e9
```

**LangServe 核心机制**：
1. **自动路由生成**：根据链的输入输出 Schema 自动生成 FastAPI 路由
2. **Schema 校验**：使用 Pydantic 自动校验请求参数和响应格式
3. **流式传输**：使用 Server-Sent Events（SSE）实现流式输出
4. **Playground**：自动生成 Web 调试界面，支持输入参数、调用链、查看输出
5. **配置注入**：支持通过请求头或参数注入 RunnableConfig

**LangServe API 端点**：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/invoke` | POST | 同步调用，返回完整结果 |
| `/stream` | POST | 流式输出，SSE 格式逐块返回 |
| `/batch` | POST | 批量处理 |
| `/ainvoke` | POST | 异步调用 |
| `/stream_log` | POST | 流式输出日志（包含中间步骤） |
| `/playground` | GET | Web 调试界面 |
| `/docs` | GET | OpenAPI 文档 |
| `/input_schema` | GET | 输入 Schema |
| `/output_schema` | GET | 输出 Schema |

> 🎯 **面试高频考点**：LangServe 的作用是什么？它自动生成哪些 API 端点？答：LangServe 是将 LCEL 链部署为 REST API 的工具，基于 FastAPI 和 Pydantic。自动生成的端点包括：/invoke（同步调用）、/stream（流式输出SSE）、/batch（批量处理）、/ainvoke（异步调用）、/astream（异步流式）、/stream_log（流式日志）、/playground（调试界面）、/docs（OpenAPI文档）、/input_schema、/output_schema、/config_schema。核心价值是无需手动编写 API 层代码，一键部署链为生产级服务。

#### 代码示例

**示例1：基础——将 LCEL 链部署为 LangServe API**

```python
# 安装：pip install langserve
# 文件：server.py
from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langserve import add_routes

# 1. 创建 LCEL 链
prompt = ChatPromptTemplate.from_template("用{style}的风格写一段关于{topic}的文字")
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
chain = prompt | model | StrOutputParser()

# 2. 创建 FastAPI 应用
app = FastAPI(title="LangChain 文本生成 API", version="1.0")

# 3. 添加路由（核心步骤）
add_routes(app, chain, path="/generate", playground_type="default")

# 4. 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 5. 运行：uvicorn server:app --host 0.0.0.0 --port 8000
# 访问：http://localhost:8000/docs（API文档）
#       http://localhost:8000/generate/playground（调试界面）
```

**示例2：进阶——客户端调用 LangServe API**

```python
# 安装：pip install langserve
from langserve import RemoteRunnable

# 1. 创建远程 Runnable
remote_chain = RemoteRunnable("http://localhost:8000/generate")

# 2. 同步调用
result = remote_chain.invoke({"style": "诗歌", "topic": "春天"})
print(f"同步调用结果:\n{result}\n")

# 3. 流式调用
print("流式调用结果:")
for chunk in remote_chain.stream({"style": "散文", "topic": "大海"}):
    print(chunk, end="", flush=True)
print("\n")

# 4. 批量调用
results = remote_chain.batch([
    {"style": "幽默", "topic": "上班"},
    {"style": "严肃", "topic": "教育"},
])
for i, r in enumerate(results, 1):
    print(f"批量结果 {i}: {r[:80]}...")

# 5. 使用 requests 直接调用
import requests
response = requests.post(
    "http://localhost:8000/generate/invoke",
    json={"input": {"style": "简洁", "topic": "AI"}, "config": {}, "kwargs": {}}
)
print(f"\n直接 HTTP 调用:\n{response.json()['output']}")
```

**示例3：完整场景——带认证和配置的生产级 LangServe 部署**

```python
# 文件：production_server.py
import os
from fastapi import FastAPI, HTTPException, Header
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langserve import add_routes

# 1. 配置管理
API_SECRET = os.getenv("API_SECRET", "my-secret-key")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

# 2. 认证依赖
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

# 3. 创建链
def create_chain(model_name: str = MODEL_NAME, temperature: float = 0.7):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的{role}，请用{language}回答问题。"),
        ("human", "{question}")
    ])
    model = ChatOpenAI(model=model_name, temperature=temperature, timeout=30, max_retries=2)
    return prompt | model | StrOutputParser()

default_chain = create_chain()

# 4. 创建 FastAPI 应用
app = FastAPI(title="生产级 LangChain API", version="2.0")

# 5. 健康检查
@app.get("/health")
async def health():
    return {"status": "healthy", "model": MODEL_NAME}

# 6. 添加 LangServe 路由（带认证）
add_routes(app, default_chain, path="/qa", playground_type="default",
            dependencies=[verify_api_key])

# 7. 另一个链（不同配置）
creative_chain = create_chain(temperature=0.9)
add_routes(app, creative_chain, path="/creative", playground_type="default",
            dependencies=[verify_api_key])

# 8. 运行
# uvicorn production_server:app --host 0.0.0.0 --port 8000 --workers 4
# 生产环境：gunicorn production_server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

#### 使用场景与最佳实践

**适用场景**：
- 将 LCEL 链快速部署为 REST API 服务
- 构建 AI 应用的后端服务（供前端或其他服务调用）
- 需要流式输出的 AI 应用（如聊天机器人、文本生成）
- 内部工具和原型的快速部署
- 需要 Playground 调试界面的开发场景

**不适用场景**：
- 非 LCEL 链的部署
- 需要复杂业务逻辑的 API（应直接使用 FastAPI 编写）
- 高并发低延迟的极端场景（LangServe 有少量 overhead）

**最佳实践**：
1. **使用环境变量管理配置**：API Key、模型名称、密钥通过环境变量注入
2. **添加认证**：生产环境必须添加 API Key 或 OAuth 认证
3. **设置超时和限流**：使用 FastAPI 中间件设置请求超时和速率限制
4. **启用 LangSmith 追踪**：设置 LANGCHAIN_TRACING_V2=true
5. **使用多 worker 部署**：生产环境使用 gunicorn + 多个 uvicorn worker
6. **健康检查端点**：添加 /health 端点，便于负载均衡器检测
7. **日志和监控**：添加请求日志、错误日志、性能指标

**性能建议**：
- 使用异步链（ainvoke/astream）提升并发性能
- 设置合理的超时（如 60 秒）
- 使用连接池和 HTTP/2 提升网络性能
- 对于高频调用的链，考虑添加缓存层（如 Redis）
- 监控 API 延迟和错误率，设置告警阈值

#### 常见坑点

**坑点1：LangServe 部署后流式输出不工作**
- **错误现象**：调用 /stream 端点时，客户端收到完整响应而非逐块流式输出
- **根本原因**：① 反向代理（Nginx、CDN）缓冲了 SSE 响应；② 客户端没有正确处理 SSE 格式；③ 链中某个组件不支持流式
- **正确做法**：
  ```python
  # 1. 配置 Nginx 不缓冲 SSE
  # nginx.conf:
  # location /stream {
  #     proxy_pass http://backend;
  #     proxy_buffering off;
  #     proxy_cache off;
  #     chunked_transfer_encoding on;
  # }

  # 2. 客户端使用 langserve RemoteRunnable（自动处理 SSE）
  from langserve import RemoteRunnable
  remote = RemoteRunnable("http://localhost:8000/chain")
  for chunk in remote.stream({"input": "你好"}):
      print(chunk, end="", flush=True)

  # 3. 确保链中所有组件支持流式
  # StrOutputParser 支持流式，PydanticOutputParser 可能阻塞
  from langchain_core.output_parsers import StrOutputParser
  chain = prompt | model | StrOutputParser()  # 支持流式
  ```
- **预防措施**：部署后测试 /stream 端点；配置反向代理关闭缓冲；客户端使用 langserve RemoteRunnable；确保链中组件支持流式

**坑点2：LangServe API 的输入输出格式与预期不符**
- **错误现象**：调用 /invoke 时报 422 Validation Error，或返回的 JSON 结构与预期不同
- **根本原因**：① 请求体格式不正确（LangServe 期望 {"input": ..., "config": ..., "kwargs": ...}）；② 链的输入类型与请求参数不匹配
- **正确做法**：
  ```python
  # ✅ 使用 LangServe 标准请求格式
  import requests
  response = requests.post(
      "http://localhost:8000/chain/invoke",
      json={
          "input": {"question": "你好", "style": "简洁"},
          "config": {"tags": ["production"]},
          "kwargs": {}
      }
  )
  result = response.json()["output"]  # 输出在 output 字段中

  # ✅ 使用 langserve RemoteRunnable（自动处理格式）
  from langserve import RemoteRunnable
  remote = RemoteRunnable("http://localhost:8000/chain")
  result = remote.invoke({"question": "你好"})  # 直接传入链的输入

  # ✅ 查看 Schema 确认格式
  # GET http://localhost:8000/chain/input_schema
  # GET http://localhost:8000/chain/output_schema
  # 访问 /playground 调试
  ```
- **预防措施**：使用 langserve RemoteRunnable 客户端；部署后查看 /docs 和 /input_schema；使用 Playground 调试；在 API 文档中明确说明请求和响应格式

---

### 9.2 LangSmith 可观测性与评估

#### 概念解释

**正式定义**：LangSmith 是 LangChain 团队推出的 LLM 应用可观测性和评估平台，提供链路追踪（Tracing）、日志记录（Logging）、评估（Evaluation）、数据集（Datasets）、监控（Monitoring）、提示词管理（Prompt Hub）等功能。通过设置环境变量 `LANGCHAIN_TRACING_V2=true` 和 `LANGCHAIN_API_KEY`，LangChain 应用的所有调用会自动被追踪并发送到 LangSmith 平台。

**生活化比喻**：LangSmith 就像 AI 应用的"黑匣子+体检中心"——黑匣子记录每一次飞行（调用）的完整过程（输入、输出、每一步的耗时和 Token），体检中心定期检查健康状况（评估回答质量、检测异常、对比不同版本的效果）。没有 LangSmith，你的 AI 应用就是在"盲飞"——出了问题不知道是哪一步的错，优化效果不知道有没有提升。

**核心价值**：解决 LLM 应用的"黑盒"问题，提供完整的链路追踪和可观测性；支持自动化评估，量化回答质量，支持 A/B 测试和版本对比；提供数据集管理，支持回归测试；是生产级 LLM 应用不可或缺的工具。

#### 原理说明

```mermaid
graph TB
    subgraph LangSmith 平台
        subgraph 数据采集
            CB[LangChain Callback<br/>自动追踪]
            SDK[LangSmith SDK<br/>手动记录]
        end
        subgraph 核心功能
            TRACE[链路追踪<br/>Tracing]
            EVAL[评估<br/>Evaluation]
            DATA[数据集<br/>Datasets]
            MONITOR[监控<br/>Monitoring]
            PROMPT[提示词管理<br/>Prompt Hub]
        end
    end
    APP[LangChain 应用] -->|自动追踪| CB
    CB --> TRACE
    TRACE --> EVAL
    DATA --> EVAL
    TRACE --> MONITOR
    style TRACE fill:#e3f2fd
    style EVAL fill:#f3e5f5
    style DATA fill:#e8f5e9
```

**LangSmith 核心功能**：

| 功能 | 说明 | 核心价值 |
|------|------|---------|
| **链路追踪 Tracing** | 记录每次调用的完整链路（每个组件的输入输出、耗时、Token） | 调试问题、性能分析 |
| **日志记录 Logging** | 结构化记录所有调用的输入输出和元数据 | 审计、搜索、分析 |
| **评估 Evaluation** | 使用 LLM 或规则自动评估回答质量 | 量化效果、A/B 测试 |
| **数据集 Datasets** | 管理测试用例和标注数据 | 标准化测试、持续集成 |
| **监控 Monitoring** | 实时监控调用量、延迟、错误率、成本 | 生产运维、告警 |
| **提示词管理 Prompt Hub** | 提示词版本管理、协作、A/B 测试 | 提示词工程、团队协作 |

> 🎯 **面试高频考点**：LangSmith 的核心功能有哪些？如何在 LangChain 应用中启用 LangSmith 追踪？答：LangSmith 的核心功能包括：① 链路追踪（Tracing）- 记录每次调用的完整链路；② 日志记录（Logging）- 结构化记录输入输出；③ 评估（Evaluation）- 自动评估回答质量；④ 数据集（Datasets）- 管理测试用例；⑤ 监控（Monitoring）- 实时监控调用量/延迟/错误率/成本；⑥ 提示词管理（Prompt Hub）- 版本管理和协作。启用方法：设置环境变量 LANGCHAIN_TRACING_V2=true、LANGCHAIN_API_KEY=your_key、LANGCHAIN_PROJECT=project_name，LangChain 的 Callback 系统会自动将所有调用追踪发送到 LangSmith。

#### 代码示例

**示例1：基础——启用 LangSmith 追踪**

```python
# 安装：pip install langsmith
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-api-key"
os.environ["LANGCHAIN_PROJECT"] = "my-rag-project"

# 启用后，所有 LangChain 调用会自动被追踪
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

chain = (
    ChatPromptTemplate.from_template("用一句话解释：{topic}")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

result = chain.invoke({"topic": "LangSmith"})
print(result)

# 登录 https://smith.langchain.com 查看追踪记录
# 可以看到：完整调用链路、每个步骤的输入输出、耗时、Token 消耗
```

**示例2：进阶——使用 LangSmith 数据集和评估**

```python
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langsmith.evaluation import evaluate, LangChainStringEvaluator

# 1. 初始化客户端
client = Client()

# 2. 创建数据集
dataset_name = "RAG-问答测试集"
try:
    dataset = client.read_dataset(dataset_name=dataset_name)
except:
    dataset = client.create_dataset(dataset_name=dataset_name, description="RAG 测试用例")
    test_cases = [
        {"input": "什么是 RAG？", "reference": "RAG 是检索增强生成技术"},
        {"input": "LangChain 的核心抽象有哪些？", "reference": "Model/Prompt/Parser/Retriever/Tool/Memory"},
    ]
    for case in test_cases:
        client.create_example(
            inputs={"question": case["input"]},
            outputs={"answer": case["reference"]},
            dataset_id=dataset.id,
        )

# 3. 定义待评估的链
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = ChatPromptTemplate.from_template("回答问题：{question}") | model | StrOutputParser()

# 4. 定义评估器
qa_evaluator = LangChainStringEvaluator(
    "qa",
    config={"criteria": {"accuracy": "回答是否准确", "relevance": "回答是否相关"}}
)

# 5. 运行评估
results = evaluate(
    chain.invoke,
    data=dataset_name,
    evaluators=[qa_evaluator],
    experiment_prefix="rag-evaluation-v1",
    max_concurrency=5,
)

print(f"评估完成: {results.experiment_name}")
# 在 LangSmith 平台查看评估结果和分数
```

**示例3：完整场景——生产级 LangSmith 监控与告警**

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"
os.environ["LANGCHAIN_PROJECT"] = "production-rag"

from langsmith import Client
from langchain_core.runnables import RunnableConfig
from datetime import datetime, timedelta

client = Client()

# 1. 为不同环境添加 tags 和 metadata
def get_config(user_id: str, feature: str) -> RunnableConfig:
    return RunnableConfig(
        tags=["production", feature],
        metadata={"user_id": user_id, "environment": "production", "version": "2.1.0"},
        run_name=f"{feature}-{user_id}",
    )

# 2. 查询追踪数据（用于监控）
def get_recent_runs(project_name: str, hours: int = 24):
    since = datetime.now() - timedelta(hours=hours)
    runs = list(client.list_runs(project_name=project_name, start_time=since, execution_order=1))
    return runs

def analyze_runs(runs):
    total = len(runs)
    success = sum(1 for r in runs if r.status == "success")
    error = sum(1 for r in runs if r.status == "error")
    avg_duration = sum(r.duration for r in runs if r.duration) / total if total else 0
    return {
        "total_calls": total,
        "success_count": success,
        "error_count": error,
        "error_rate": f"{error/total*100:.1f}%" if total else "0%",
        "avg_duration_seconds": round(avg_duration, 2),
    }

# 3. 错误告警
def check_errors_and_alert(project_name: str, threshold: int = 5):
    since = datetime.now() - timedelta(hours=1)
    error_runs = list(client.list_runs(project_name=project_name, start_time=since, error=True))
    if len(error_runs) > threshold:
        print(f"🚨 告警：最近 1 小时错误数 {len(error_runs)} 超过阈值 {threshold}！")
        # 实际项目中发送邮件/钉钉/短信通知
    else:
        print(f"✅ 正常：最近 1 小时错误数 {len(error_runs)}")

# 4. 自定义追踪（手动记录非 LangChain 操作）
from langsmith import traceable

@traceable(run_type="tool", name="custom_database_query")
def query_database(sql: str) -> list:
    """自定义函数，自动被 LangSmith 追踪"""
    import time
    time.sleep(0.1)
    return [{"id": 1, "name": "测试数据"}]

result = query_database("SELECT * FROM users")
print(f"数据库查询结果: {result}")

# 5. 运行监控
recent_runs = get_recent_runs("production-rag", hours=24)
stats = analyze_runs(recent_runs)
print("\n=== 最近 24 小时监控数据 ===")
for key, value in stats.items():
    print(f"  {key}: {value}")

check_errors_and_alert("production-rag", threshold=5)
```

#### 使用场景与最佳实践

**适用场景**：
- 生产级 LLM 应用的可观测性（追踪、日志、监控）
- LLM 应用的调试和问题排查
- 回答质量评估和 A/B 测试
- 回归测试和持续集成（数据集 + 自动化评估）
- 提示词版本管理和团队协作
- 成本分析和优化（Token 消耗、API 调用次数）

**不适用场景**：
- 本地开发和原型（可以用但不是必须）
- 对数据隐私要求极高的场景（追踪数据会发送到 LangSmith 云端，可考虑自托管）
- 不需要可观测性的极简应用

**最佳实践**：
1. **生产环境必须启用**：设置 LANGCHAIN_TRACING_V2=true，所有调用自动追踪
2. **使用项目隔离**：不同应用/环境使用不同的 LANGCHAIN_PROJECT
3. **添加 tags 和 metadata**：为调用添加环境、版本、用户 ID 等标签
4. **建立评估数据集**：为核心功能建立测试数据集，每次变更后运行评估
5. **设置监控告警**：监控错误率、延迟、成本等指标，设置告警阈值
6. **提示词版本管理**：使用 Prompt Hub 管理提示词版本，支持 A/B 测试和回滚
7. **定期审查追踪**：定期审查错误追踪和低质量回答，持续优化
8. **控制追踪数据量**：高频调用可以采样追踪（如 10%），降低成本

**性能建议**：
- LangSmith 追踪是异步发送的，对应用延迟影响很小（<10ms）
- 高频应用可以使用采样追踪，减少数据量和成本
- 评估运行可以异步执行，不影响线上服务
- 使用 LangSmith SDK 的批量接口上传数据，提升效率
- 定期清理旧的追踪数据（设置数据保留策略）

#### 常见坑点

**坑点1：LangSmith 追踪不显示或数据缺失**
- **错误现象**：设置了环境变量并调用了 LangChain，但 LangSmith 平台上没有显示追踪记录
- **根本原因**：① API Key 错误或过期；② LANGCHAIN_TRACING_V2 未设置为 "true"；③ 网络问题无法连接 LangSmith API；④ 自定义 Runnable 没有正确传播回调
- **正确做法**：
  ```python
  import os

  # ✅ 验证环境变量
  print(f"TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
  print(f"API_KEY: {os.getenv('LANGCHAIN_API_KEY', '')[:10]}...")
  print(f"PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")

  # ✅ 使用 tracing_v2_enabled 上下文管理器
  from langchain_core.tracers.context import tracing_v2_enabled
  with tracing_v2_enabled(project_name="my-project"):
      result = chain.invoke({"question": "测试"})

  # ✅ 验证 API Key 有效性
  from langsmith import Client
  client = Client()
  try:
      projects = list(client.list_projects())
      print(f"连接成功，可访问 {len(projects)} 个项目")
  except Exception as e:
      print(f"连接失败: {e}")

  # ✅ 自定义 Runnable 传播回调
  from langchain_core.runnables import Runnable, RunnableConfig
  class MyRunnable(Runnable):
      def invoke(self, input, config: RunnableConfig = None):
          with self.get_config_list(config) as configs:
              return self._invoke(input, configs)
  ```
- **预防措施**：部署后验证 LangSmith 连接；使用 tracing_v2_enabled 确保关键调用被追踪；检查网络连接和防火墙；为自定义 Runnable 正确传播回调配置

**坑点2：评估结果不准确或评估器报错**
- **错误现象**：LangSmith 评估分数与人工评估差异很大，或评估器运行时报错
- **根本原因**：① 评估 Prompt 不清晰，LLM 评估标准不一致；② 参考答案质量差；③ 评估器配置错误；④ 被评估的链输出格式与评估器期望不符；⑤ 评估超时
- **正确做法**：
  ```python
  # ✅ 使用清晰的评估标准
  from langsmith.evaluation import LangChainStringEvaluator
  accuracy_evaluator = LangChainStringEvaluator(
      "labeled_score_string",
      config={
          "criteria": {"accuracy": "回答是否准确，是否基于参考信息，是否有事实错误"},
          "score_threshold": 4,
      },
      prepare_data=lambda run, example: {
          "prediction": run.outputs["output"],
          "reference": example.outputs["answer"],
          "input": example.inputs["question"],
      }
  )

  # ✅ 使用多个评估器综合评估
  evaluators = [
      LangChainStringEvaluator("qa", config={"criteria": {"accuracy": "准确性"}}),
      LangChainStringEvaluator("qa", config={"criteria": {"completeness": "完整性"}}),
      LangChainStringEvaluator("qa", config={"criteria": {"relevance": "相关性"}}),
      LangChainStringEvaluator("conciseness"),
  ]

  # ✅ 设置合理的超时和并发
  from langsmith.evaluation import evaluate
  results = evaluate(
      chain.invoke,
      data="test-dataset",
      evaluators=evaluators,
      max_concurrency=3,  # 降低并发，减少超时
  )

  # ✅ 提供高质量的参考答案
  # 数据集的 reference 应该完整、准确、无歧义
  # 避免模糊的参考答案（如"RAG 是一种技术"）
  ```
- **预防措施**：定义清晰的评估标准；提供高质量的参考答案；使用多个评估器综合评估；设置合理的超时和并发；定期人工验证评估结果，校准评估器；建立评估结果的基线，对比不同版本

---

> 💡 **深度讲解**
>
> 从 LCEL 到生产部署是 LLM 应用开发的"最后一公里"。本地开发时，你只需要关注链的逻辑和效果；但要部署到生产环境，需要考虑 API 服务、认证授权、可观测性、评估监控、性能优化、成本控制等诸多问题。LangServe 和 LangSmith 是 LangChain 生态中解决这些问题的核心工具。
>
> LangServe 让部署变得简单——你不需要手动编写 FastAPI 路由、请求解析、响应格式化、流式传输等样板代码，只需要调用 `add_routes(app, chain, path="/api")` 就能将链部署为完整的 REST API 服务。LangServe 自动生成 /invoke、/stream、/batch 等端点，自动生成 OpenAPI 文档和 Playground 调试界面。但 LangServe 不是万能的——对于需要复杂业务逻辑、自定义认证、WebSocket 通信的场景，还是需要直接使用 FastAPI 编写。
>
> LangSmith 解决了 LLM 应用的"黑盒"问题。传统软件应用有完善的可观测性工具（日志、指标、链路追踪），但 LLM 应用长期缺乏这样的工具。LangSmith 填补了这个空白——它自动追踪每次调用的完整链路（每个组件的输入输出、耗时、Token），提供结构化日志、自动化评估、数据集管理、实时监控、提示词版本管理等功能。有了 LangSmith，你可以：① 调试问题（查看哪一步出错、输入输出是什么）；② 优化性能（识别耗时最长的步骤、Token 消耗最高的调用）；③ 评估质量（自动化评估回答质量，A/B 测试不同版本）；④ 监控生产（错误率、延迟、成本的实时监控和告警）。
>
> 生产部署的最佳实践包括：① 使用环境变量管理配置（API Key、模型名称、密钥）；② 添加认证和授权（API Key、OAuth）；③ 设置速率限制和超时；④ 启用 LangSmith 追踪和监控；⑤ 建立评估数据集和自动化评估流程；⑥ 使用多 worker 部署提升并发；⑦ 添加健康检查端点；⑧ 定期备份和清理数据；⑨ 建立告警机制（错误率、延迟、成本超阈值）；⑩ 持续优化（基于追踪数据优化提示词、链结构、模型选择）。
>
> 从原型到生产是一个持续优化的过程——不要试图一次性做到完美，先部署最小可用版本，然后基于 LangSmith 的追踪和评估数据持续迭代优化。

> **📝 精简总结**
>
> LangServe 是将 LCEL 链部署为 REST API 的工具，基于 FastAPI 和 Pydantic，自动生成 /invoke（同步）、/stream（流式SSE）、/batch（批量）、/ainvoke（异步）、/playground（调试界面）、/docs（OpenAPI文档）等端点；核心价值是无需手动编写 API 层代码，一键部署；最佳实践包括环境变量配置、添加认证、设置超时限流、启用 LangSmith、多 worker 部署、健康检查。LangSmith 是 LLM 应用可观测性和评估平台，核心功能包括链路追踪（Tracing）、日志记录（Logging）、评估（Evaluation）、数据集（Datasets）、监控（Monitoring）、提示词管理（Prompt Hub）；启用方法是设置 LANGCHAIN_TRACING_V2=true 和 LANGCHAIN_API_KEY；核心价值是解决 LLM 应用的黑盒问题，支持调试、评估、监控、优化；最佳实践包括生产环境必须启用、项目隔离、添加 tags/metadata、建立评估数据集、设置监控告警、提示词版本管理。常见坑点包括 LangServe 流式输出不工作（反向代理缓冲/客户端处理/组件不支持流式）和 LangSmith 追踪不显示（API Key/环境变量/网络/回调传播）。

> **🎯 梯度练习题**
>
> **入门级**：
> 1. 将一个简单的 LCEL 链用 LangServe 部署为 API，测试 /invoke 和 /stream 端点
> 2. 启用 LangSmith 追踪，调用链后在 LangSmith 平台查看追踪记录
> 3. 解释 LangServe 自动生成的 API 端点有哪些，各自的作用是什么
>
> **进阶级**：
> 1. 为 LangServe API 添加 API Key 认证、健康检查端点、请求日志中间件
> 2. 使用 LangSmith 创建一个包含 10 个测试用例的数据集，定义 2 个评估器，运行评估并分析结果
> 3. 使用 langserve RemoteRunnable 客户端调用远程 API，测试同步、流式、批量、异步四种调用方式
>
> **实战级**：
> 1. 构建一个生产级 LangServe 部署：多个链、API Key 认证、速率限制、LangSmith 追踪、健康检查、多 worker 部署配置、Docker 化部署
> 2. 建立完整的 LangSmith 评估体系：3 个数据集、5 个评估器、自动化评估脚本、评估报告生成、版本对比分析
> 3. 设计一个 LLM 应用的生产监控方案：使用 LangSmith API 采集监控数据，构建监控仪表盘，设置告警规则（错误率>5%/延迟>10s/成本超预算），实现告警通知

---

## 十、实战篇：最佳实践、迁移指南与生态全景

### 10.1 LangChain 最佳实践汇总

#### 概念解释

**正式定义**：LangChain 最佳实践是社区和官方总结的、经过生产验证的开发规范和推荐做法，涵盖项目结构、链设计、提示词工程、工具定义、记忆管理、错误处理、性能优化、安全防护、可观测性、测试评估等各个方面。遵循最佳实践可以提升代码质量、减少常见错误、提高开发效率、确保生产稳定性。

**生活化比喻**：最佳实践就像老厨师的菜谱和经验——新手做菜可能会犯各种错误（盐放多了、火太大了、食材顺序错了），而老厨师的菜谱告诉你每一步该怎么做、用多少料、注意什么。遵循菜谱，你就能做出稳定好吃的菜；不遵循菜谱，你可能每次做出来的味道都不一样，还经常翻车。

**核心价值**：避免重复踩坑，提升开发效率和代码质量；确保应用的可维护性、可测试性、可扩展性；降低生产环境的故障率和安全风险；是团队协作和代码审查的标准依据。

#### 原理说明

```mermaid
graph TB
    subgraph LangChain 最佳实践体系
        subgraph 开发规范
            STRUCT[项目结构]
            CONFIG[配置外置]
            TYPE[类型注解]
            DOC[文档注释]
        end
        subgraph 链设计
            LCEL[使用 LCEL]
            SINGLE[单一职责]
            REUSE[组件复用]
        end
        subgraph 提示词工程
            SYSTEM[系统提示]
            FEWSHOT[Few-shot]
            OUTPUT[输出格式]
        end
        subgraph 生产保障
            ERROR[错误处理]
            RETRY[重试回退]
            MONITOR[监控告警]
            TEST[测试评估]
            SECURITY[安全防护]
        end
    end
    style STRUCT fill:#e3f2fd
    style LCEL fill:#f3e5f5
    style SYSTEM fill:#e8f5e9
    style ERROR fill:#fff3e0
```

**最佳实践分类汇总**：

| 类别 | 最佳实践 | 说明 |
|------|---------|------|
| **项目结构** | 模块化组织 | 按功能模块组织代码（chains/、tools/、prompts/、utils/） |
| **项目结构** | 配置外置 | 使用 .env 和配置文件管理 API Key、模型参数 |
| **项目结构** | 依赖锁定 | 使用 requirements.txt 或 poetry.lock 锁定依赖版本 |
| **链设计** | 使用 LCEL | 新代码一律用 `\|` 运算符，不用旧版 Chain 类 |
| **链设计** | 单一职责 | 每个链/组件只做一件事，复杂逻辑拆分为多个链 |
| **链设计** | 组件复用 | 公共组件（模型、提示词、工具）定义为可复用模块 |
| **链设计** | 类型安全 | 使用 TypedDict/Pydantic 定义链的输入输出类型 |
| **提示词** | 系统提示 | 使用 SystemMessage 设定角色、约束、输出格式 |
| **提示词** | Few-shot | 提供 2-5 个示例引导模型输出格式和风格 |
| **提示词** | 输出格式 | 使用 Output Parser + format_instructions 确保结构化输出 |
| **提示词** | 迭代优化 | 基于 LangSmith 追踪数据持续优化提示词 |
| **工具** | 描述清晰 | 工具 description 包含用途、何时使用、何时不使用 |
| **工具** | 参数详细 | 使用 Pydantic Field 为每个参数添加 description、examples |
| **工具** | 错误处理 | 工具内部添加参数校验和错误处理 |
| **记忆** | 选择策略 | 短对话用 Buffer，长对话用 SummaryBuffer |
| **记忆** | 控制大小 | 设置 max_tokens 或 max_messages，防止上下文溢出 |
| **记忆** | 外部存储 | 生产环境将记忆存储在数据库/Redis |
| **错误处理** | 重试机制 | 使用 .with_retry() 应对 API 临时故障 |
| **错误处理** | 回退机制 | 使用 .with_fallbacks() 实现主备模型切换 |
| **错误处理** | 异常捕获 | 链外层添加 try/except，返回友好的错误信息 |
| **性能** | 模型分级 | 简单任务用小模型，复杂任务用大模型 |
| **性能** | 并行执行 | 无依赖任务用 RunnableParallel 并行执行 |
| **性能** | 批量处理 | 多个输入用 .batch() 提升吞吐量 |
| **性能** | 流式输出 | 用户交互场景用 .stream() 提升体验 |
| **安全** | 输入校验 | 校验用户输入，防止 Prompt 注入 |
| **安全** | 工具白名单 | 只注册必要的工具，高风险工具加人工确认 |
| **安全** | 密钥管理 | 使用环境变量/密钥管理服务，不硬编码 API Key |
| **可观测性** | LangSmith | 生产环境启用 LangSmith 追踪 |
| **可观测性** | 日志记录 | 记录关键调用的输入输出、耗时、Token |
| **可观测性** | 监控告警 | 监控错误率、延迟、成本，设置告警 |
| **测试** | 单元测试 | 为每个组件/链编写单元测试 |
| **测试** | 评估数据集 | 建立测试数据集，自动化评估回答质量 |
| **测试** | 回归测试 | 每次变更后运行评估，确保质量不退化 |

> 🎯 **面试高频考点**：LangChain 生产部署的最佳实践有哪些？答：① 使用 LCEL 而非旧版 Chain 类；② 配置外置（环境变量管理 API Key 和模型参数）；③ 添加重试（with_retry）和回退（with_fallbacks）机制；④ 启用 LangSmith 追踪和监控；⑤ 建立评估数据集和自动化评估流程；⑥ 记忆外部化存储（数据库/Redis）；⑦ 添加认证和速率限制；⑧ 设置超时和 max_iterations 防止无限循环；⑨ 输入校验防止 Prompt 注入；⑩ 高风险工具加 Human-in-the-loop 确认；⑪ 使用多 worker 部署提升并发；⑫ 定期备份和清理数据。

#### 代码示例

**示例1：基础——规范的 LangChain 项目结构**

```
my-rag-project/
├── .env                          # 环境变量（不提交到 Git）
├── .env.example                  # 环境变量示例（提交到 Git）
├── .gitignore
├── requirements.txt              # 依赖锁定
├── README.md                     # 项目说明
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI 应用入口
│   ├── config.py                 # 配置管理
│   ├── chains/                   # 链定义
│   │   ├── rag_chain.py          # RAG 链
│   │   └── summary_chain.py      # 摘要链
│   ├── prompts/                  # 提示词模板
│   │   └── rag_prompts.py        # RAG 提示词
│   ├── tools/                    # 工具定义
│   │   └── search_tool.py        # 搜索工具
│   ├── memory/                   # 记忆管理
│   │   └── conversation_memory.py
│   ├── retrievers/               # 检索器
│   │   └── vector_retriever.py
│   └── utils/                    # 工具函数
│       ├── logging.py            # 日志配置
│       └── validators.py         # 输入校验
├── tests/                        # 测试
│   ├── test_chains.py            # 链的单元测试
│   └── evaluation/               # 评估
│       ├── datasets/             # 评估数据集
│       └── run_evaluation.py     # 评估脚本
├── data/                         # 数据文件
│   └── documents/                # 原始文档
└── scripts/                      # 脚本
    └── ingest_docs.py            # 文档索引脚本
```

**示例2：进阶——生产级链的完整实现（含错误处理、重试、回退、配置）**

```python
# app/chains/rag_chain.py
import os
from typing import TypedDict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# 1. 输入类型定义
class RAGInput(TypedDict):
    question: str
    user_id: str

class RAGOutput(TypedDict):
    answer: str
    sources: List[str]

# 2. 组件初始化（配置外置）
def get_embeddings():
    return OpenAIEmbeddings(model=settings.EMBEDDING_MODEL)

def get_vectorstore():
    return Chroma(
        persist_directory=settings.VECTORSTORE_PATH,
        embedding_function=get_embeddings(),
        collection_name=settings.COLLECTION_NAME,
    )

def get_retriever():
    return get_vectorstore().as_retriever(search_kwargs={"k": settings.RETRIEVER_K})

def get_primary_model():
    return ChatOpenAI(
        model=settings.PRIMARY_MODEL, temperature=0,
        timeout=settings.LLM_TIMEOUT, max_retries=2,
    )

def get_fallback_model():
    return ChatOpenAI(
        model=settings.FALLBACK_MODEL, temperature=0,
        timeout=settings.LLM_TIMEOUT,
    )

# 3. 提示词模板
RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的知识问答助手。请根据以下上下文回答用户问题。
规则：
1. 只根据上下文中的信息回答，不要编造
2. 如果上下文中没有相关信息，回答"根据现有知识库无法回答该问题"
3. 回答时引用相关文档编号（如[文档1]）
4. 用简洁清晰的语言回答，不超过 500 字"""),
    ("human", """上下文：
{context}

问题：{question}

回答：""")
])

# 4. 辅助函数
def format_docs(docs):
    formatted = []
    sources = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "未知")
        formatted.append(f"[文档{i} | 来源:{source}]\n{doc.page_content}")
        sources.append(source)
    return "\n\n".join(formatted), sources

# 5. 构建链（含重试、回退、错误处理）
def build_rag_chain():
    retriever = get_retriever()
    retrieve_and_format = (
        RunnableLambda(lambda x: x["question"])
        | retriever
        | RunnableLambda(lambda docs: format_docs(docs))
    )
    parallel_step = RunnableParallel({
        "context_and_sources": retrieve_and_format,
        "question": lambda x: x["question"],
    })
    def prepare_input(data):
        context, sources = data["context_and_sources"]
        return {"context": context, "question": data["question"], "_sources": sources}

    model_chain = (
        RAG_PROMPT
        | get_primary_model().with_fallbacks([get_fallback_model()])
        | StrOutputParser()
    )

    chain = (
        parallel_step
        | RunnableLambda(prepare_input)
        | RunnablePassthrough.assign(answer=model_chain)
        | RunnableLambda(lambda x: {"answer": x["answer"], "sources": x["_sources"]})
    )
    return chain

# 6. 带错误处理的调用函数
def query_rag(question: str, user_id: str) -> RAGOutput:
    try:
        chain = build_rag_chain()
        result = chain.invoke({"question": question, "user_id": user_id})
        logger.info(f"RAG 查询成功 | user={user_id} | q={question[:50]}")
        return result
    except Exception as e:
        logger.error(f"RAG 查询失败 | user={user_id} | q={question[:50]} | error={str(e)}")
        return {"answer": "抱歉，系统暂时无法回答您的问题，请稍后重试。", "sources": []}
```

**示例3：完整场景——LangChain 项目的测试与评估体系**

```python
# tests/test_chains.py
import pytest
from app.chains.rag_chain import build_rag_chain, query_rag
from app.chains.summary_chain import build_summary_chain

# 1. 单元测试：链的基本功能
class TestRAGChain:
    def test_chain_invoke_returns_dict(self):
        chain = build_rag_chain()
        result = chain.invoke({"question": "什么是 RAG？", "user_id": "test"})
        assert isinstance(result, dict)
        assert "answer" in result
        assert "sources" in result
        assert isinstance(result["answer"], str)

    def test_chain_with_unknown_question(self):
        result = query_rag("如何制作红烧肉？", "test")
        assert "无法回答" in result["answer"] or len(result["answer"]) > 0

    def test_chain_error_handling(self):
        result = query_rag("测试", "test")
        assert "answer" in result
        assert "sources" in result

    def test_chain_stream(self):
        chain = build_rag_chain()
        chunks = []
        for chunk in chain.stream({"question": "什么是 LangChain？", "user_id": "test"}):
            chunks.append(chunk)
        assert len(chunks) > 0

# 2. 单元测试：摘要链
class TestSummaryChain:
    def test_summary_reduces_length(self):
        chain = build_summary_chain()
        long_text = "这是一段很长的文本... " * 100
        result = chain.invoke({"text": long_text})
        assert len(result) < len(long_text)

    def test_summary_preserves_key_info(self):
        chain = build_summary_chain()
        text = "LangChain 是由 Harrison Chase 于 2022 年创建的 LLM 应用开发框架，核心是 LCEL。"
        result = chain.invoke({"text": text})
        assert "LangChain" in result or "框架" in result

# 3. 集成测试
class TestEndToEnd:
    def test_full_rag_workflow(self):
        result = query_rag("LangChain 的核心抽象有哪些？", "integration_test")
        assert result["answer"]
        assert len(result["sources"]) > 0

# 4. 评估脚本
# tests/evaluation/run_evaluation.py
def run_evaluation():
    from langsmith import Client
    from langsmith.evaluation import evaluate, LangChainStringEvaluator

    client = Client()
    dataset_name = "RAG-生产评估集"

    evaluators = [
        LangChainStringEvaluator("qa", config={"criteria": {"accuracy": "准确性"}}),
        LangChainStringEvaluator("qa", config={"criteria": {"completeness": "完整性"}}),
        LangChainStringEvaluator("qa", config={"criteria": {"relevance": "相关性"}}),
        LangChainStringEvaluator("conciseness"),
    ]

    results = evaluate(
        lambda x: query_rag(x["question"], "evaluation"),
        data=dataset_name,
        evaluators=evaluators,
        experiment_prefix="rag-production-eval",
        max_concurrency=5,
    )

    print(f"评估完成: {results.experiment_name}")
    return results

if __name__ == "__main__":
    run_evaluation()
```

#### 使用场景与最佳实践

**适用场景**：
- 所有 LangChain 项目的开发和维护
- 团队协作和代码审查的标准依据
- 从原型到生产的升级改造
- 代码质量提升和技术债务清理
- 新人培训和知识传承

**不适用场景**：
- 一次性的极简脚本（不需要完整的项目结构和测试体系）
- 快速原型验证（可以先快速实现，再按最佳实践重构）

**最佳实践**（汇总 Top 20）：
1. **使用 LCEL**：新代码一律用 `|` 运算符，不用旧版 Chain 类
2. **配置外置**：API Key、模型名称、参数通过环境变量注入
3. **类型注解**：为链的输入输出添加 TypedDict/Pydantic 类型
4. **错误处理**：链外层添加 try/except，返回友好错误信息
5. **重试回退**：使用 .with_retry() 和 .with_fallbacks() 提升健壮性
6. **LangSmith 追踪**：生产环境必须启用，添加 tags 和 metadata
7. **评估数据集**：建立测试数据集，每次变更后运行评估
8. **记忆外部化**：生产环境将记忆存储在数据库/Redis
9. **工具描述清晰**：description 包含何时使用/不使用，参数用 Pydantic Field
10. **提示词迭代**：基于 LangSmith 数据持续优化提示词
11. **模型分级**：简单任务用小模型，复杂任务用大模型
12. **并行执行**：无依赖任务用 RunnableParallel 并行
13. **流式输出**：用户交互场景用 .stream()
14. **输入校验**：校验用户输入，防止 Prompt 注入
15. **安全防护**：工具白名单，高风险操作加 HITL
16. **监控告警**：监控错误率、延迟、成本，设置告警
17. **依赖锁定**：使用 requirements.txt 锁定版本
18. **模块化组织**：按功能模块组织代码，组件可复用
19. **单元测试**：为每个组件/链编写单元测试
20. **文档注释**：为公共组件编写 docstring 和使用示例

**性能建议**：
- 模型选择：gpt-4o-mini 处理 80% 的任务，gpt-4o 处理复杂推理
- 缓存：高频查询的检索结果和模型响应可以缓存（Redis）
- 批量：离线处理用 .batch()，吞吐量提升 2-5x
- 异步：高并发服务用 ainvoke/abatch
- 向量数据库：小规模用 Chroma，中规模用 Weaviate，大规模用 Pinecone/Milvus
- Embedding：text-embedding-3-small 性价比最高，批量 Embedding 提升吞吐量

#### 常见坑点

**坑点1：项目结构混乱导致难以维护**
- **错误现象**：所有代码写在一个文件里，链定义、工具定义、提示词、API 路由混在一起，修改一个功能要找半天
- **根本原因**：没有按照模块化原则组织代码，关注点没有分离，组件没有复用
- **正确做法**：
  ```
  # ✅ 模块化组织
  # app/
  # ├── main.py              # FastAPI 入口（只负责路由和启动）
  # ├── config.py            # 配置管理
  # ├── chains/
  # │   ├── rag_chain.py     # RAG 链定义
  # │   └── agent_chain.py   # Agent 链定义
  # ├── prompts/
  # │   └── rag_prompts.py   # RAG 提示词
  # ├── tools/
  # │   ├── search.py         # 搜索工具
  # │   └── calculator.py     # 计算工具
  # ├── memory/
  # │   └── conversation.py   # 对话记忆
  # └── utils/
  #     ├── logging.py        # 日志
  #     └── validators.py     # 输入校验
  ```
- **预防措施**：项目启动时就建立规范的目录结构；每个模块职责单一；公共组件抽取为可复用模块；定期代码审查；使用 Cookiecutter 等工具生成项目模板

**坑点2：缺少测试和评估导致质量不可控**
- **错误现象**：修改提示词或链结构后，不知道效果是变好还是变差；上线后发现某些问题回答质量下降；无法量化回答质量
- **根本原因**：没有建立测试数据集和自动化评估流程；没有单元测试覆盖核心功能；修改后没有回归测试
- **正确做法**：
  ```python
  # ✅ 建立评估数据集
  # 在 LangSmith 中创建数据集，包含 20-50 个代表性测试用例

  # ✅ 编写单元测试
  import pytest
  def test_rag_chain_basic():
      result = query_rag("什么是 LangChain？", "test")
      assert "answer" in result
      assert len(result["answer"]) > 0

  def test_rag_chain_unknown():
      result = query_rag("如何登录火星？", "test")
      assert "无法回答" in result["answer"] or result["sources"] == []

  def test_tool_calculator():
      result = calculator.invoke({"expression": "2 + 3 * 4"})
      assert "14" in result

  # ✅ CI/CD 中自动运行评估
  # .github/workflows/evaluation.yml
  # name: Evaluation
  # on: [push, pull_request]
  # jobs:
  #   evaluate:
  #     runs-on: ubuntu-latest
  #     steps:
  #       - uses: actions/checkout@v4
  #       - run: pip install -r requirements.txt
  #       - run: python tests/evaluation/run_evaluation.py
  #       - run: python tests/test_chains.py

  # ✅ 建立质量基线和告警
  # - 记录每次评估的平均分
  # - 如果新版本的平均分比基线低 5% 以上，告警并阻止合并
  ```
- **预防措施**：项目早期就建立评估数据集（即使只有 10 个用例）；每次功能变更后运行评估；CI/CD 中集成自动化测试和评估；建立质量基线，对比不同版本；定期审查低质量回答，补充到评估数据集中

---

### 10.2 LangChain 生态全景与框架对比

#### 概念解释

**正式定义**：LangChain 生态是由 LangChain 核心框架、周边工具（LangGraph、LangServe、LangSmith）、第三方集成（100+ 模型、50+ 向量数据库、100+ 工具）、社区资源（模板、教程、示例）组成的完整生态系统。框架对比是将 LangChain 与其他 LLM 应用开发框架（LlamaIndex、AutoGen、CrewAI、Semantic Kernel、Dify 等）在定位、核心优势、适用场景等维度进行对比，帮助开发者选择合适的框架。

**生活化比喻**：LangChain 生态就像一个完整的城市——LangChain 核心是市中心（主要商业区），LangGraph 是工业园区（重型制造业），LangServe 是物流中心（货物分发），LangSmith 是监控中心（城市管理），第三方集成是各种商店和服务（餐厅、银行、医院），社区资源是图书馆和学校。框架对比就像选择不同的城市生活——有的城市商业发达（LangChain），有的城市学术氛围浓（LlamaIndex），有的城市社交活跃（AutoGen），有的城市分工明确（CrewAI），你需要根据自己的需求选择合适的城市。

**核心价值**：了解 LangChain 生态的完整能力，充分利用周边工具和第三方集成；通过框架对比，根据项目需求选择最合适的框架（或组合使用多个框架）；避免"所有问题都用 LangChain"的思维定式，选择最适合的工具。

#### 原理说明

```mermaid
graph TB
    subgraph LangChain 生态全景
        subgraph 核心框架
            LC[LangChain<br/>核心抽象与链]
            LG[LangGraph<br/>多Agent编排]
        end
        subgraph 周边工具
            LS[LangServe<br/>API部署]
            LSM[LangSmith<br/>可观测性]
            LH[LangChain Hub<br/>提示词分享]
            LT[LangChain Templates<br/>应用模板]
        end
        subgraph 第三方集成
            MODELS[100+ 模型<br/>OpenAI/Anthropic/Google]
            VECTOR[50+ 向量库<br/>Chroma/Pinecone/Weaviate]
            TOOLS[100+ 工具<br/>搜索/代码/数据库]
        end
    end
    LC --> LG
    LC --> LS
    LC --> LSM
    LC --> MODELS
    LC --> VECTOR
    LC --> TOOLS
    style LC fill:#e3f2fd
    style LG fill:#f3e5f5
    style LS fill:#e8f5e9
    style LSM fill:#fff3e0
```

**主流 LLM 框架对比**：

| 维度 | LangChain | LlamaIndex | LangGraph | AutoGen | CrewAI | Semantic Kernel | Dify |
|------|-----------|------------|-----------|---------|--------|----------------|------|
| **定位** | 通用 LLM 框架 | RAG 优先框架 | 多 Agent 编排 | 对话式多 Agent | 角色化多 Agent | 企业级 AI 框架 | 低代码 AI 平台 |
| **核心优势** | 生态丰富、抽象标准 | RAG 能力极强 | 流程控制灵活 | 对话协作、代码执行 | 角色定义直观 | 企业集成、插件化 | 可视化、开箱即用 |
| **RAG** | 强 | 极强 | 中 | 弱 | 中 | 中 | 强 |
| **Agent** | 中 | 中 | 极强 | 强 | 强 | 中 | 中 |
| **工作流** | 中 | 弱 | 极强 | 中 | 中 | 中 | 强 |
| **多Agent** | 中 | 弱 | 极强 | 极强 | 强 | 中 | 弱 |
| **学习曲线** | 中 | 缓 | 陡 | 中 | 缓 | 中 | 极缓 |
| **生产就绪** | 高 | 高 | 高 | 中 | 中 | 高 | 高 |
| **生态规模** | 极大 | 大 | 大 | 中 | 中 | 中 | 中 |
| **灵活度** | 高 | 中 | 极高 | 中 | 中 | 高 | 低 |
| **适用场景** | 通用 AI 应用 | 知识库问答 | 复杂 Agent 流程 | 对话协作 | 角色分工 | 企业集成 | 快速原型 |

**框架选择决策树**：
1. **需要 RAG 为主** → LlamaIndex（RAG 能力最强）或 LangChain（生态更丰富）
2. **需要复杂 Agent 流程** → LangGraph（状态机、持久化、HITL）
3. **需要多 Agent 对话协作** → AutoGen（对话式协作）或 CrewAI（角色分工）
4. **需要企业级集成** → Semantic Kernel（微软生态、插件化）
5. **需要快速原型/非技术人员** → Dify（低代码、可视化）
6. **通用 LLM 应用开发** → LangChain（最通用、生态最丰富）
7. **组合使用** → LangChain（核心抽象）+ LangGraph（Agent 编排）+ LlamaIndex（高级 RAG）

> 🎯 **面试高频考点**：LangChain 和 LlamaIndex 的区别是什么？如何选择？答：LangChain 是通用 LLM 应用开发框架，核心优势是生态丰富（100+ 模型、50+ 向量库、100+ 工具）、抽象标准化（Runnable/LCEL）、通用性强（RAG/Agent/工作流都支持）；LlamaIndex 是 RAG 优先框架，核心优势是 RAG 能力极强（高级索引、查询引擎、路由、重排序）、数据连接器丰富、专注于知识库问答。选择建议：① 如果项目以 RAG 为主，需要高级检索能力，选 LlamaIndex；② 如果项目需要通用能力（RAG + Agent + 工作流），选 LangChain；③ 可以组合使用——用 LangChain 做核心框架和 Agent，用 LlamaIndex 做高级 RAG 检索；④ LangChain 的生态更丰富，长期维护更有保障。

#### 代码示例

**示例1：基础——LangChain 生态工具组合使用**

```python
# 组合使用 LangChain 生态的多个工具
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-key"
os.environ["LANGCHAIN_PROJECT"] = "eco-demo"

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnableParallel
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

# 1. LangChain 核心：链
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_template("根据上下文回答：{context}\n\n问题：{question}")
chain = prompt | model | StrOutputParser()

# 2. LangChain 集成：向量数据库
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(embedding_function=embeddings, collection_name="demo")
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 3. LangGraph：Agent 编排
class State(TypedDict):
    messages: Annotated[list, operator.add]
    question: str

def retrieve_node(state):
    docs = retriever.invoke(state["question"])
    context = "\n".join(doc.page_content for doc in docs)
    return {"messages": [f"[检索结果] {context}"]}

def generate_node(state):
    context = state["messages"][-1] if state["messages"] else ""
    answer = chain.invoke({"context": context, "question": state["question"]})
    return {"messages": [f"[回答] {answer}"]}

workflow = StateGraph(State)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)
app = workflow.compile()

# 4. LangSmith：自动追踪（已通过环境变量启用）
result = app.invoke({"question": "什么是 LangChain 生态？", "messages": []})
print(result["messages"][-1])

# 5. LangServe：部署为 API（在 server.py 中）
# from fastapi import FastAPI
# from langserve import add_routes
# app_api = FastAPI()
# add_routes(app_api, chain, path="/qa")
# add_routes(app_api, app, path="/agent")

print("✅ LangChain 生态工具组合使用完成")
print("- LangChain 核心：链（Prompt + Model + Parser）")
print("- LangChain 集成：Chroma 向量数据库")
print("- LangGraph：Agent 编排（检索 → 生成）")
print("- LangSmith：可观测性（自动追踪）")
print("- LangServe：API 部署（可选）")
```

**示例2：进阶——LangChain 与 LlamaIndex 组合使用**

```python
# 安装：pip install llama-index
# LangChain 负责核心框架和 Agent，LlamaIndex 负责高级 RAG

# 1. 使用 LlamaIndex 构建高级检索引擎
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from llama_index.embeddings.openai import OpenAIEmbedding as LlamaEmbedding

Settings.llm = LlamaOpenAI(model="gpt-4o-mini")
Settings.embed_model = LlamaEmbedding(model="text-embedding-3-small")

documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(
    documents,
    transformations=[SentenceSplitter(chunk_size=500, chunk_overlap=50)]
)

# 使用高级检索器（查询融合 + 重排序）
retriever = QueryFusionRetriever(
    retrievers=[index.as_retriever(similarity_top_k=5)],
    num_queries=3,
    use_async=True,
)

# 2. 将 LlamaIndex 检索器包装为 LangChain Retriever
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document as LCDocument
from typing import List

class LlamaIndexRetriever(BaseRetriever):
    def __init__(self, llama_retriever):
        super().__init__()
        self.llama_retriever = llama_retriever

    def _get_relevant_documents(self, query: str) -> List[LCDocument]:
        nodes = self.llama_retriever.retrieve(query)
        return [
            LCDocument(page_content=node.text, metadata={"score": node.score, **node.metadata})
            for node in nodes
        ]

langchain_retriever = LlamaIndexRetriever(retriever)

# 3. 使用 LangChain 构建 RAG 链和 Agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableParallel

lc_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
rag_prompt = ChatPromptTemplate.from_template("根据上下文回答：{context}\n\n问题：{question}")
rag_chain = (
    RunnableParallel({
        "context": langchain_retriever | (lambda docs: "\n".join(d.page_content for d in docs)),
        "question": lambda x: x["question"],
    })
    | rag_prompt | lc_model | StrOutputParser()
)

# 4. 使用 LangGraph Agent（使用 LlamaIndex 检索作为工具）
from langchain_core.tools import tool

@tool
def search_knowledge_base(query: str) -> str:
    """搜索知识库获取相关信息。当需要回答专业问题时使用此工具。"""
    docs = langchain_retriever.invoke(query)
    return "\n\n".join(f"[文档{i+1}] {d.page_content}" for i, d in enumerate(docs))

from langgraph.prebuilt import create_react_agent
agent = create_react_agent(lc_model, [search_knowledge_base])
result = agent.invoke({"messages": [{"role": "user", "content": "什么是 RAG？"}]})
print(result["messages"][-1].content)

print("✅ LangChain + LlamaIndex 组合使用完成")
print("- LlamaIndex：高级 RAG 检索（查询融合、重排序、高级索引）")
print("- LangChain：核心框架、链组合、Agent 编排")
```

**示例3：完整场景——多框架对比的实际选型案例**

```python
# 场景：为一个企业级 AI 客服系统选择技术栈

# 需求分析：
# 1. 基于企业知识库的问答（RAG）
# 2. 多轮对话（记忆）
# 3. 工具调用（查询订单、提交工单、转接人工）
# 4. 复杂工作流（问题分类 → 检索 → 回答 → 满意度调查）
# 5. 人机协作（复杂问题转人工）
# 6. 生产级部署（API、监控、评估）
# 7. 未来扩展（多 Agent 协作）

# 技术栈选型：

# ✅ 核心框架：LangChain
# - 理由：生态最丰富，集成了所有需要的模型、向量库、工具
# - 用途：核心抽象（Prompt/Model/Parser/Tool/Memory）、链组合

# ✅ Agent 编排：LangGraph
# - 理由：需要复杂工作流、人机协作、持久化、状态管理
# - 用途：客服工作流（分类→检索→回答→工单→转接）、HITL、多轮对话状态

# ✅ RAG 检索：LangChain Retriever + 高级优化
# - 理由：RAG 需求中等，LangChain 的 Retriever 足够
# - 用途：向量检索、混合检索、重排序
# - 备选：如果 RAG 需求变得复杂，可引入 LlamaIndex

# ✅ 可观测性：LangSmith
# - 理由：LangChain 原生集成，追踪、评估、监控一站式
# - 用途：链路追踪、回答质量评估、生产监控、告警

# ✅ API 部署：LangServe + FastAPI
# - 理由：LangServe 快速部署链，FastAPI 处理自定义业务逻辑
# - 用途：REST API、流式输出、认证、限流

# ❌ 不选 AutoGen：对话式多 Agent 不是核心需求，客服系统是流程驱动
# ❌ 不选 CrewAI：角色化 Agent 不是核心需求，需要精确的流程控制
# ❌ 不选 Dify：需要高度定制化和代码控制，低代码平台灵活度不够
# ❌ 不选 Semantic Kernel：企业不是微软技术栈，LangChain 生态更匹配

# 技术栈架构：
"""
┌─────────────────────────────────────────────────┐
│                   前端（Web/App）                 │
└────────────────────┬────────────────────────────┘
                     │ REST API / SSE
┌────────────────────▼────────────────────────────┐
│              LangServe + FastAPI                  │
│         （认证、限流、路由、流式输出）             │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│               LangGraph 状态机                    │
│  （客服工作流：分类→检索→回答→工单→转接）        │
│  （持久化、HITL、多轮对话状态）                   │
└─────────┬───────────────────┬───────────────────┘
          │                   │
┌─────────▼─────────┐ ┌─────▼───────────────────┐
│  LangChain 核心    │ │  LangChain Retriever    │
│ （Prompt/Model/    │ │ （向量检索+混合检索+    │
│  Parser/Tool/      │ │  重排序）               │
│  Memory）          │ │                         │
└─────────┬─────────┘ └───────────┬─────────────┘
          │                         │
┌─────────▼─────────────────────────▼─────────────┐
│              第三方集成                            │
│ （OpenAI/Anthropic、Chroma/Pinecone、            │
│  搜索/订单/工单工具、数据库）                      │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              LangSmith 可观测性                    │
│  （追踪、评估、监控、告警、数据集）                │
└──────────────────────────────────────────────────┘
"""

print("✅ 企业级 AI 客服系统技术栈选型完成")
print("核心：LangChain + LangGraph + LangSmith + LangServe")
print("RAG：LangChain Retriever（备选 LlamaIndex）")
print("不选：AutoGen/CrewAI/Dify/Semantic Kernel（需求不匹配）")
```

#### 使用场景与最佳实践

**适用场景**：
- 新项目的技术选型（了解各框架的优劣势，选择最合适的）
- 现有项目的技术栈评估（是否需要引入新框架或迁移）
- 多框架组合使用（发挥各框架的优势）
- 团队技术培训（了解 LLM 框架生态）
- 技术调研和方案设计

**不适用场景**：
- 已经确定技术栈的项目（不需要再对比）
- 极简项目（一个框架足够，不需要组合）

**最佳实践**：
1. **按需选择**：根据项目需求选择框架，不要盲目追新或盲目追求大而全
2. **组合使用**：发挥各框架的优势，如 LangChain（核心）+ LangGraph（Agent）+ LlamaIndex（高级 RAG）
3. **LangChain 为核心**：大多数项目以 LangChain 为核心框架，其他框架作为补充
4. **复杂 Agent 用 LangGraph**：需要复杂流程、持久化、HITL 时，用 LangGraph 替代 AgentExecutor
5. **高级 RAG 用 LlamaIndex**：RAG 需求复杂时，引入 LlamaIndex 的高级检索能力
6. **快速原型用 Dify**：非技术人员或快速验证想法时，用 Dify 等低代码平台
7. **关注框架演进**：LLM 框架发展很快，定期关注各框架的更新和最佳实践
8. **避免框架锁定**：核心逻辑尽量基于标准接口（Runnable），便于框架间迁移

**性能建议**：
- 框架本身的 overhead 很小（微秒级），性能瓶颈主要在 LLM 调用和检索
- 多框架组合时注意数据转换的开销（如 LlamaIndex Document → LangChain Document）
- 选择活跃维护、社区大的框架（长期支持和问题解决更有保障）
- 生产环境选择经过验证的稳定版本，不要盲目追最新版本

#### 常见坑点

**坑点1：盲目选择框架或盲目追新**
- **错误现象**：看到新框架就想迁移，或盲目使用最热门的框架，导致项目技术栈频繁变更，维护成本高
- **根本原因**：没有根据项目需求选择框架，盲目追热点；对各框架的优劣势不了解
- **正确做法**：
  ```python
  # ✅ 基于需求的框架选型

  # 1. 明确项目需求（列出核心需求和优先级）
  requirements = {
      "RAG 问答": "高",
      "多轮对话": "高",
      "工具调用": "中",
      "复杂工作流": "中",
      "多 Agent 协作": "低",
      "快速原型": "低",
      "企业集成": "中",
  }

  # 2. 根据需求选择框架
  # - RAG 为主 → LlamaIndex 或 LangChain
  # - 复杂 Agent → LangGraph
  # - 多 Agent 对话 → AutoGen
  # - 角色化 Agent → CrewAI
  # - 快速原型 → Dify
  # - 企业集成 → Semantic Kernel
  # - 通用 → LangChain

  # 3. 推荐组合（大多数项目）
  recommended_stack = {
      "核心框架": "LangChain",
      "Agent 编排": "LangGraph（如果需要复杂流程）",
      "RAG": "LangChain Retriever（简单）或 LlamaIndex（复杂）",
      "可观测性": "LangSmith",
      "部署": "LangServe + FastAPI",
  }

  # 4. 避免频繁迁移
  # - 选定技术栈后，至少稳定使用 3-6 个月
  # - 新框架出现时，先在小项目/分支中评估
  # - 迁移前评估成本和收益，只有收益明显大于成本时才迁移
  ```
- **预防措施**：建立技术选型流程（需求分析→框架调研→原型验证→决策）；定期（每季度）评估技术栈是否需要调整；关注框架的长期维护状态（GitHub stars、贡献者活跃度、版本更新频率）；避免在项目中期频繁更换核心框架

**坑点2：多框架组合时数据格式不兼容**
- **错误现象**：LangChain 和 LlamaIndex 组合使用时，Document 格式不兼容，检索结果无法直接传递给 LangChain 的链；或 LangGraph 的 State 格式与 LangChain 的链输入不匹配
- **根本原因**：不同框架有自己的数据结构定义（Document、Message、State），格式不完全兼容，需要转换
- **正确做法**：
  ```python
  # ✅ 编写适配器转换数据格式

  # LlamaIndex Document → LangChain Document
  from llama_index.core.schema import Document as LlamaDocument
  from langchain_core.documents import Document as LCDocument

  def llama_to_langchain_doc(llama_doc: LlamaDocument) -> LCDocument:
      return LCDocument(
          page_content=llama_doc.text,
          metadata=llama_doc.metadata,
      )

  # LangChain Document → LlamaIndex Document
  def langchain_to_llama_doc(lc_doc: LCDocument) -> LlamaDocument:
      return LlamaDocument(
          text=lc_doc.page_content,
          metadata=lc_doc.metadata,
      )

  # ✅ 使用框架提供的集成层
  # LangChain 提供了 LlamaIndex 集成
  # from langchain_llama_index import LlamaIndexRetriever
  # retriever = LlamaIndexRetriever(index=index)

  # ✅ 在边界处统一转换
  # 设计清晰的边界：LlamaIndex 负责检索，返回 LangChain Document
  class RAGService:
      def __init__(self, llama_index):
          self.llama_index = llama_index

      def retrieve(self, query: str, k: int = 5) -> list[LCDocument]:
          """检索，返回 LangChain Document 格式"""
          nodes = self.llama_index.retrieve(query, k)
          return [llama_to_langchain_doc(node) for node in nodes]

  # ✅ LangGraph 与 LangChain 链的集成
  # LangGraph 的节点中可以直接调用 LangChain 链
  from langgraph.graph import StateGraph

  def agent_node(state):
      # state 是 LangGraph 的 State 格式
      # 调用 LangChain 链时，转换为链期望的输入格式
      chain_input = {"question": state["question"], "context": state["context"]}
      result = rag_chain.invoke(chain_input)
      return {"answer": result}  # 返回 LangGraph State 格式
  ```
- **预防措施**：多框架组合时设计清晰的边界和接口；编写适配器/转换函数统一数据格式；优先使用框架官方提供的集成层；在边界处进行数据转换，内部保持各自的原生格式；添加集成测试验证数据格式转换的正确性

---

> 💡 **深度讲解**
>
> 最佳实践和生态全景是 LangChain 学习的"集大成"部分。前面的章节讲解了 LangChain 的各个组件和用法，这一章将这些知识整合为可操作的最佳实践，并将 LangChain 放在整个 LLM 框架生态中进行定位和对比。
>
> LangChain 最佳实践涵盖了从项目结构、链设计、提示词工程、工具定义、记忆管理、错误处理、性能优化、安全防护、可观测性到测试评估的完整开发流程。这些最佳实践不是凭空产生的，而是 LangChain 社区在大量生产项目中总结出来的经验。遵循最佳实践可以帮助你避免常见的坑、提升代码质量、确保生产稳定性。其中最重要的几条是：① 使用 LCEL 而非旧版 Chain 类；② 配置外置（环境变量管理敏感信息）；③ 启用 LangSmith 追踪（可观测性是生产级应用的基础）；④ 建立评估数据集（质量可控）；⑤ 添加重试和回退机制（健壮性）。
>
> LangChain 生态是一个完整的生态系统——LangChain 核心是基础，LangGraph 是 Agent 编排，LangServe 是 API 部署，LangSmith 是可观测性，第三方集成是能力扩展，社区资源是学习支持。这个生态的优势是"一站式"——你不需要自己集成各种工具，LangChain 生态已经帮你做好了。但生态大也意味着学习成本高，需要了解各个组件的定位和用法。
>
> 框架对比是技术选型的重要参考。LangChain、LlamaIndex、LangGraph、AutoGen、CrewAI、Semantic Kernel、Dify 各有定位和优劣势。没有"最好的框架"，只有"最合适的框架"——你需要根据项目需求选择。大多数项目的推荐组合是：LangChain（核心框架）+ LangGraph（复杂 Agent）+ LangSmith（可观测性）+ LangServe（部署）。如果 RAG 需求特别复杂，可以引入 LlamaIndex；如果需要快速原型，可以用 Dify。
>
> 从零基础到实战老手的学习路径是：① 掌握 LangChain 核心抽象（Model/Prompt/Parser/Retriever/Tool/Memory）；② 熟练使用 LCEL 和 Runnable 组合链；③ 构建 RAG 和 Agent 应用；④ 掌握生产部署（LangServe/LangSmith）；⑤ 了解生态和框架对比，能够进行技术选型；⑥ 遵循最佳实践，构建高质量的生产级应用。到达第⑥步，你就是 LangChain 的实战老手了。

> **📝 精简总结**
>
> LangChain 最佳实践涵盖项目结构（模块化组织、配置外置、依赖锁定）、链设计（LCEL、单一职责、组件复用、类型安全）、提示词工程（系统提示、Few-shot、输出格式、迭代优化）、工具定义（描述清晰、参数详细、错误处理）、记忆管理（选择策略、控制大小、外部存储）、错误处理（重试、回退、异常捕获）、性能优化（模型分级、并行执行、批量处理、流式输出）、安全防护（输入校验、工具白名单、密钥管理）、可观测性（LangSmith、日志记录、监控告警）、测试评估（单元测试、评估数据集、回归测试）等方面；核心原则是使用 LCEL、配置外置、启用 LangSmith、建立评估体系、添加重试回退。LangChain 生态包括核心框架（LangChain）、周边工具（LangGraph/LangServe/LangSmith/Hub/Templates）、第三方集成（100+模型/50+向量库/100+工具）、社区资源（文档/教程/社区/GitHub）。框架对比：LangChain（通用）、LlamaIndex（RAG优先）、LangGraph（多Agent编排）、AutoGen（对话式多Agent）、CrewAI（角色化多Agent）、Semantic Kernel（企业级）、Dify（低代码）；推荐组合是 LangChain + LangGraph + LangSmith + LangServe，复杂 RAG 引入 LlamaIndex。常见坑点是项目结构混乱（模块化组织）和多框架数据不兼容（编写适配器/边界转换）。

> **🎯 梯度练习题**
>
> **入门级**：
> 1. 列出 LangChain 最佳实践的 Top 10，说明每条的作用
> 2. 描述 LangChain 生态的主要组成部分（核心框架、周边工具、第三方集成）
> 3. 对比 LangChain 和 LlamaIndex 的区别，说明各自的适用场景
>
> **进阶级**：
> 1. 按照最佳实践重构一个 LangChain 项目（模块化组织、配置外置、错误处理、单元测试）
> 2. 实现 LangChain + LlamaIndex 组合使用，LlamaIndex 负责高级检索，LangChain 负责链和 Agent
> 3. 为一个 LangChain 应用建立完整的评估体系（数据集、评估器、自动化脚本、报告）
>
> **实战级**：
> 1. 为一个企业级 AI 应用进行完整的技术选型：分析需求、对比框架、设计技术栈架构、说明选型理由、制定实施计划
> 2. 构建一个生产级 LangChain 项目模板：包含规范的项目结构、配置管理、错误处理、重试回退、LangSmith 追踪、单元测试、评估体系、Docker 部署、CI/CD
> 3. 对比 5 个主流 LLM 框架（LangChain/LlamaIndex/LangGraph/AutoGen/CrewAI），从 10 个维度进行详细对比，并给出 5 种典型场景的选型建议

---

## 🔗 关联笔记

- [[LangGraph-状态机Agent]] — LangGraph 多 Agent 编排框架
- [[LangGraph-State状态管理核心]] — LangGraph State 状态管理
- [[LangGraph-Node节点与执行流]] — LangGraph Node 节点与执行流
- [[LangGraph-Conditional-Edge条件边与路由]] — LangGraph 条件边与路由
- [[LangGraph-Checkpoint检查点与持久化]] — LangGraph 检查点与持久化
- [[LangGraph-HITL人机交互]] — LangGraph 人机交互
- [[LangGraph-Streaming流式输出与事件]] — LangGraph 流式输出
- [[LlamaIndex-数据框架]] — RAG 优先的数据框架
- [[Agent核心概念-ReAct规划]] — ReAct 推理循环
- [[Agent工具调用FunctionCalling]] — Function Calling 基础
- [[FunctionCalling工具生态]] — 工具生态
- [[MCP协议与工具生态]] — 工具标准化协议
- [[自研Agent框架设计]] — 自研框架设计参考
- [[AutoGen-多Agent框架]] — 对话式多 Agent 框架
- [[CrewAI-角色化多Agent]] — 角色化多 Agent 框架
- [[Dify-低代码AI应用平台]] — 低代码 AI 平台
- [[AI Agent开发框架知识点系统梳理_优化版]] — Agent 框架系统梳理

## 📖 前置知识

- [[LLM大模型入门概念]]
- [[Prompt工程进阶]]
- [[Transformer架构核心]]
- [[Embedding模型选型]]
- [[Python-语法基础与数据结构]]
- [[Python-面向对象与异常处理]]

## 🏷️ 相关标签

`#AI应用` `#AI工程化` `#Agent` `#LLM` `#核心` `#LCEL` `#RAG`

---

[[Home|🏠 返回首页]] · [[MOC-AI与效率工具|📚 返回分类]]

## 十一、附录：代码模式速查与面试考点汇总

### 11.1 LCEL 代码模式速查

#### 模式1：基础管道组合

```python
# 模式1-1：最基础的 prompt | model | parser 管道
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template("用一句话解释 {concept}")
model = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()
chain = prompt | model | parser
result = chain.invoke({"concept": "LCEL"})
print(result)
# 预期输出: LCEL是LangChain的表达式语言，用管道符|组合可运行组件...
```

```python
# 模式1-2：带 SystemMessage 的管道
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，用{style}风格回答"),
    ("human", "{question}"),
])
chain = prompt | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()
result = chain.invoke({
    "role": "Python专家",
    "style": "简洁",
    "question": "什么是装饰器？"
})
print(result)
```

```python
# 模式1-3：多变量模板管道
from langchain_core.prompts import ChatPromptTemplate

template = """请根据以下信息生成摘要：
标题：{title}
作者：{author}
内容：{content}
要求：{requirement}"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0.3) | StrOutputParser()
result = chain.invoke({
    "title": "AI发展趋势",
    "author": "张三",
    "content": "人工智能正在快速发展...",
    "requirement": "不超过100字"
})
print(result)
```

#### 模式2：RunnableParallel 并行

```python
# 模式2-1：基础并行执行
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

chain1 = ChatPromptTemplate.from_template("用中文解释 {topic}") | model | parser
chain2 = ChatPromptTemplate.from_template("用英文解释 {topic}") | model | parser
chain3 = ChatPromptTemplate.from_template("用代码示例解释 {topic}") | model | parser

parallel_chain = RunnableParallel(
    chinese=chain1,
    english=chain2,
    code=chain3,
)
result = parallel_chain.invoke({"topic": "递归"})
print(f"中文: {result['chinese'][:50]}...")
print(f"英文: {result['english'][:50]}...")
print(f"代码: {result['code'][:50]}...")
```

```python
# 模式2-2：并行后合并
from langchain_core.runnables import RunnableParallel, RunnableLambda

def merge_results(inputs: dict) -> str:
    return f"【中文】{inputs['chinese']}\n\n【英文】{inputs['english']}"

parallel = RunnableParallel(
    chinese=ChatPromptTemplate.from_template("中文解释{topic}") | model | parser,
    english=ChatPromptTemplate.from_template("English explanation of {topic}") | model | parser,
)
merged_chain = parallel | RunnableLambda(merge_results)
result = merged_chain.invoke({"topic": "闭包"})
print(result)
```

```python
# 模式2-3：并行分支 + 条件选择
from langchain_core.runnables import RunnableParallel, RunnableBranch

def choose_best(inputs: dict) -> str:
    scores = {k: len(v) for k, v in inputs.items()}
    best = max(scores, key=scores.get)
    return f"最佳回答（{best}）:\n{inputs[best]}"

parallel = RunnableParallel(
    concise=ChatPromptTemplate.from_template("用20字解释{topic}") | model | parser,
    detailed=ChatPromptTemplate.from_template("用200字详细解释{topic}") | model | parser,
    analogy=ChatPromptTemplate.from_template("用比喻解释{topic}") | model | parser,
)
chain = parallel | RunnableLambda(choose_best)
result = chain.invoke({"topic": "多态"})
print(result)
```

#### 模式3：RunnableBranch 条件分支

```python
# 模式3-1：基于输入的条件分支
from langchain_core.runnables import RunnableBranch, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate

def is_code_question(x: dict) -> bool:
    return any(kw in x["question"].lower() for kw in ["代码", "code", "函数", "bug", "报错"])

def is_math_question(x: dict) -> bool:
    return any(kw in x["question"].lower() for kw in ["计算", "数学", "math", "公式", "方程"])

code_chain = ChatPromptTemplate.from_template("作为编程专家回答：{question}") | model | parser
math_chain = ChatPromptTemplate.from_template("作为数学专家回答：{question}") | model | parser
default_chain = ChatPromptTemplate.from_template("回答：{question}") | model | parser

branch = RunnableBranch(
    (is_code_question, code_chain),
    (is_math_question, math_chain),
    default_chain,
)
result = branch.invoke({"question": "如何用Python实现快速排序？"})
print(result)
```

```python
# 模式3-2：基于模型输出的条件分支
from langchain_core.runnables import RunnableBranch, RunnableLambda
from langchain_core.output_parsers import JsonOutputParser

classify_prompt = ChatPromptTemplate.from_template(
    "判断以下问题的类别，返回JSON：{{\"category\": \"code|math|general\"}}\n问题：{question}"
)
classify_chain = classify_prompt | model | JsonOutputParser()

def route_by_category(x: dict) -> str:
    cat = x.get("category", "general")
    if cat == "code":
        return "作为编程专家回答"
    elif cat == "math":
        return "作为数学专家回答"
    return "通用回答"

routing_chain = classify_chain | RunnableLambda(route_by_category)
result = routing_chain.invoke({"question": "什么是递归函数？"})
print(result)
```

```python
# 模式3-3：多级嵌套分支
from langchain_core.runnables import RunnableBranch

def is_urgent(x): return "紧急" in x.get("priority", "")
def is_high(x): return "高" in x.get("priority", "")
def is_medium(x): return "中" in x.get("priority", "")

urgent_chain = ChatPromptTemplate.from_template("【紧急处理】{task}") | model | parser
high_chain = ChatPromptTemplate.from_template("【高优先级】{task}") | model | parser
medium_chain = ChatPromptTemplate.from_template("【中优先级】{task}") | model | parser
low_chain = ChatPromptTemplate.from_template("【低优先级】{task}") | model | parser

nested_branch = RunnableBranch(
    (is_urgent, urgent_chain),
    (is_high, high_chain),
    RunnableBranch(
        (is_medium, medium_chain),
        low_chain,
    )
)
result = nested_branch.invoke({"task": "修复生产环境bug", "priority": "紧急"})
print(result)
```

#### 模式4：RunnableLambda 自定义函数

```python
# 模式4-1：基础自定义函数
from langchain_core.runnables import RunnableLambda

def clean_text(text: str) -> str:
    import re
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
    return text

clean_chain = RunnableLambda(clean_text)
result = clean_chain.invoke("  你好，  世界！  这是   测试。  ")
print(result)
# 预期输出: 你好世界这是测试
```

```python
# 模式4-2：带参数的自定义函数（使用闭包）
from langchain_core.runnables import RunnableLambda

def truncate(max_length: int):
    def _truncate(text: str) -> str:
        return text[:max_length] + "..." if len(text) > max_length else text
    return _truncate

truncate_chain = RunnableLambda(truncate(50))
result = truncate_chain.invoke("这是一段非常长的文本" * 20)
print(result)
```

```python
# 模式4-3：异步自定义函数
from langchain_core.runnables import RunnableLambda
import asyncio

async def async_process(text: str) -> str:
    await asyncio.sleep(0.1)
    return f"处理结果: {text.upper()}"

async_chain = RunnableLambda(async_process)
result = asyncio.run(async_chain.ainvoke("hello"))
print(result)
```

#### 模式5：RunnablePassthrough 透传

```python
# 模式5-1：基础透传
from langchain_core.runnables import RunnablePassthrough

chain = RunnablePassthrough()
result = chain.invoke({"key": "value"})
print(result)
# 预期输出: {'key': 'value'}
```

```python
# 模式5-2：透传 + 额外字段
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

add_timestamp = RunnableLambda(lambda x: {**x, "timestamp": "2026-09-09"})
chain = RunnablePassthrough.assign(extra=lambda x: f"processed_{x['id']}")
result = chain.invoke({"id": "123", "name": "test"})
print(result)
# 预期输出: {'id': '123', 'name': 'test', 'extra': 'processed_123'}
```

```python
# 模式5-3：RAG 中的经典用法
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

retriever = ...  # 你的检索器
prompt = ChatPromptTemplate.from_template("根据上下文回答：{context}\n\n问题：{question}")
model = ChatOpenAI(model="gpt-4o-mini")

rag_chain = (
    RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
    | prompt
    | model
    | StrOutputParser()
)
result = rag_chain.invoke("什么是RAG？")
print(result)
```

#### 模式6：批量与流式

```python
# 模式6-1：批量执行
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

chain = ChatPromptTemplate.from_template("翻译为英文：{text}") | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()
results = chain.batch([
    {"text": "你好世界"},
    {"text": "人工智能"},
    {"text": "机器学习"},
], config={"max_concurrency": 3})
for r in results:
    print(r)
```

```python
# 模式6-2：流式输出
chain = ChatPromptTemplate.from_template("写一首关于{topic}的短诗") | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()
for chunk in chain.stream({"topic": "秋天"}):
    print(chunk, end="", flush=True)
```

```python
# 模式6-3：流式 + 批量组合
async def stream_multiple():
    chain = ChatPromptTemplate.from_template("解释{topic}") | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()
    async for chunk in chain.astream({"topic": "并发编程"}):
        print(chunk, end="", flush=True)

import asyncio
asyncio.run(stream_multiple())
```

#### 模式7：配置与重试

```python
# 模式7-1：运行时配置
from langchain_core.runnables import RunnableConfig

chain = ChatPromptTemplate.from_template("解释{topic}") | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()
result = chain.invoke(
    {"topic": "配置管理"},
    config=RunnableConfig(
        tags=["production", "v2"],
        metadata={"user_id": "123", "session_id": "abc"},
        run_name="explain_concept",
    )
)
print(result)
```

```python
# 模式7-2：with_config 预设配置
configured_chain = chain.with_config(
    tags=["preset"],
    metadata={"version": "1.0"},
)
result = configured_chain.invoke({"topic": "预设配置"})
print(result)
```

```python
# 模式7-3：with_retry 重试机制
from langchain_core.runnables import RunnableRetry

retry_chain = chain.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True,
)
try:
    result = retry_chain.invoke({"topic": "重试机制"})
    print(result)
except Exception as e:
    print(f"重试3次后失败: {e}")
```

#### 模式8：OutputParser 模式

```python
# 模式8-1：StrOutputParser
from langchain_core.output_parsers import StrOutputParser
parser = StrOutputParser()
result = parser.invoke(AIMessage(content="你好"))
print(result)  # 你好
```

```python
# 模式8-2：JsonOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

parser = JsonOutputParser()
prompt = ChatPromptTemplate.from_template(
    "返回JSON：{format_instructions}\n问题：{question}"
).partial(format_instructions=parser.get_format_instructions())
chain = prompt | ChatOpenAI(model="gpt-4o-mini") | parser
result = chain.invoke({"question": "列出3个水果"})
print(result)
```

```python
# 模式8-3：PydanticOutputParser
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class Person(BaseModel):
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    hobbies: list[str] = Field(description="爱好列表")

parser = PydanticOutputParser(pydantic_object=Person)
prompt = ChatPromptTemplate.from_template(
    "提取人物信息：{format_instructions}\n文本：{text}"
).partial(format_instructions=parser.get_format_instructions())
chain = prompt | ChatOpenAI(model="gpt-4o-mini") | parser
result = chain.invoke({"text": "小明今年25岁，喜欢编程和篮球"})
print(f"姓名: {result.name}, 年龄: {result.age}, 爱好: {result.hobbies}")
```

```python
# 模式8-4：CommaSeparatedListOutputParser
from langchain_core.output_parsers import CommaSeparatedListOutputParser
parser = CommaSeparatedListOutputParser()
result = parser.invoke("苹果, 香蕉, 橙子, 葡萄")
print(result)  # ['苹果', '香蕉', '橙子', '葡萄']
```

```python
# 模式8-5：DatetimeOutputParser
from langchain_core.output_parsers import DatetimeOutputParser
parser = DatetimeOutputParser()
result = parser.invoke("2026年9月9日下午3点")
print(result)  # 2026-09-09 15:00:00
```

#### 模式9：Memory 集成模式

```python
# 模式9-1：ConversationBufferMemory
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=ChatOpenAI(model="gpt-4o-mini"),
    memory=memory,
    verbose=False,
)
conversation.predict(input="你好，我叫小明")
conversation.predict(input="我叫什么名字？")
print(memory.load_memory_variables({}))
```

```python
# 模式9-2：ConversationBufferWindowMemory
from langchain.memory import ConversationBufferWindowMemory
memory = ConversationBufferWindowMemory(k=3)  # 只保留最近3轮
for i in range(5):
    memory.save_context({"input": f"问题{i}"}, {"output": f"回答{i}"})
print(memory.load_memory_variables({}))
```

```python
# 模式9-3：ConversationSummaryMemory
from langchain.memory import ConversationSummaryMemory
memory = ConversationSummaryMemory(llm=ChatOpenAI(model="gpt-4o-mini"))
memory.save_context({"input": "我喜欢Python"}, {"output": "Python是一门优秀的语言"})
memory.save_context({"input": "我也喜欢Java"}, {"output": "Java也是一门流行的语言"})
print(memory.load_memory_variables({}))
```

#### 模式10：Callback 模式

```python
# 模式10-1：StdOutCallbackHandler
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate

chain = ChatPromptTemplate.from_template("解释{topic}") | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()
result = chain.invoke({"topic": "回调"}, config={"callbacks": [StdOutCallbackHandler()]})
```

```python
# 模式10-2：自定义CallbackHandler
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

class TokenCounter(BaseCallbackHandler):
    def __init__(self):
        self.tokens = 0
    def on_llm_end(self, response: LLMResult, **kwargs):
        if response.llm_output and "token_usage" in response.llm_output:
            self.tokens += response.llm_output["token_usage"]["total_tokens"]

counter = TokenCounter()
result = chain.invoke({"topic": "Token计数"}, config={"callbacks": [counter]})
print(f"总Token: {counter.tokens}")
```

```python
# 模式10-3：异步Callback
from langchain_core.callbacks import AsyncCallbackHandler
class AsyncLogger(AsyncCallbackHandler):
    async def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"[异步] LLM开始: {prompts[0][:50]}...")
    async def on_llm_end(self, response, **kwargs):
        print(f"[异步] LLM结束")
```

---

### 11.2 面试高频考点汇总

> 🎯 **面试高频考点 1**：LCEL 是什么？它解决了什么问题？
> 答：LCEL（LangChain Expression Language）是 LangChain 的声明式组合语言，用管道符 `|` 组合 Runnable 组件。它解决了三个核心问题：① 统一接口——所有组件实现 Runnable 接口，支持 invoke/stream/batch/ainvoke 四种执行方式；② 组合灵活——支持管道、并行、分支、自定义函数等多种组合方式；③ 生产就绪——原生支持流式、批量、异步、回调、配置、重试、追踪等生产特性。LCEL 是 LangChain 从"链式调用"到"声明式编排"的范式升级。

> 🎯 **面试高频考点 2**：Runnable 接口的核心方法有哪些？区别是什么？
> 答：Runnable 接口有 4 个核心方法：① `invoke(input)`——同步执行，返回完整结果；② `stream(input)`——同步流式输出，逐块返回结果；③ `batch(inputs)`——同步批量执行，并行处理多个输入；④ `ainvoke/astream/abatch`——对应的异步版本。区别：invoke 适合简单同步场景，stream 适合需要实时反馈的用户交互，batch 适合批量处理提升吞吐量，异步版本适合高并发服务端场景。所有方法都接受 config 参数用于配置回调、标签、元数据等。

> 🎯 **面试高频考点 3**：RunnableParallel 和 RunnableSequence 的区别？
> 答：RunnableSequence（管道 `|`）是顺序执行，前一个组件的输出作为后一个的输入，适用于有依赖关系的步骤；RunnableParallel 是并行执行，所有分支接收相同的输入，输出为字典（key 为分支名，value 为分支输出），适用于无依赖的并行任务。两者可以组合使用：并行结果可以通过管道传给下一个组件，管道中的某个步骤也可以是并行分支。核心区别在于执行顺序和数据流向：Sequence 是单向数据流，Parallel 是扇出数据流。

> 🎯 **面试高频考点 4**：LLM 和 ChatModel 的区别？
> 答：① 输入格式——LLM 接收纯文本字符串，ChatModel 接收 Message 列表（SystemMessage/HumanMessage/AIMessage）；② 输出格式——LLM 返回字符串，ChatModel 返回 AIMessage 对象（包含 content、tool_calls 等结构化字段）；③ 功能支持——ChatModel 支持工具调用（tool_calls）、多模态输入、结构化输出等现代 LLM 特性，LLM 是更基础的文本补全接口；④ 推荐使用——新项目应优先使用 ChatModel，LLM 主要用于兼容旧代码和简单文本补全场景。两者都实现了 Runnable 接口，可以无缝替换。

> 🎯 **面试高频考点 5**：Message 类型有哪些？各自的作用？
> 答：LangChain 有 5 种核心 Message 类型：① SystemMessage——系统消息，设置 AI 的角色、行为规则、输出格式等，在对话最前面；② HumanMessage——用户消息，代表用户输入，可包含文本、图片、工具调用结果等；③ AIMessage——AI 消息，代表模型输出，包含 content 和 tool_calls（工具调用请求）；④ ToolMessage——工具消息，代表工具执行结果，必须包含 tool_call_id 与 AIMessage.tool_calls 对应；⑤ FunctionMessage——函数消息，旧版函数调用的消息类型，已被 ToolMessage 替代。核心设计是通过消息类型区分对话角色和内容语义。

> 🎯 **面试高频考点 6**：PromptTemplate 和 ChatPromptTemplate 的区别？
> 答：① 输入输出——PromptTemplate 生成字符串，ChatPromptTemplate 生成 Message 列表；② 适用场景——PromptTemplate 配合 LLM 使用，ChatPromptTemplate 配合 ChatModel 使用；③ 功能——ChatPromptTemplate 支持多种消息角色（system/human/ai）、消息占位符、少量示例（FewShot）等，功能更丰富；④ 推荐——新项目优先使用 ChatPromptTemplate，因为它与现代 ChatModel 生态完全兼容。两者都支持变量插值、部分赋值（partial）、模板序列化等功能。

> 🎯 **面试高频考点 7**：OutputParser 的作用？常见类型有哪些？
> 答：OutputParser 用于将 LLM 的原始输出（字符串/AIMessage）解析为结构化数据（JSON、Pydantic 对象、列表、日期等）。核心价值是让 LLM 输出可被程序直接使用，而不是需要手动解析。常见类型：① StrOutputParser——最简单，提取文本内容；② JsonOutputParser——解析为 JSON 字典；③ PydanticOutputParser——解析为 Pydantic 模型，带类型校验；④ CommaSeparatedListOutputParser——解析为列表；⑤ DatetimeOutputParser——解析为日期时间；⑥ EnumOutputParser——解析为枚举值。设计模式是 Parser 提供 get_format_instructions() 生成格式提示，注入到 Prompt 中引导 LLM 按格式输出。

> 🎯 **面试高频考点 8**：传统 Chain（LLMChain 等）和 LCEL 的区别？如何迁移？
> 答：① 设计理念——传统 Chain 是继承式设计（继承 Chain 基类），LCEL 是组合式设计（用管道组合 Runnable）；② 灵活性——传统 Chain 扩展需要写新类，LCEL 扩展只需组合组件；③ 功能——LCEL 原生支持流式、并行、分支、异步等，传统 Chain 支持有限；④ 迁移——LLMChain → `prompt | model | parser`；SequentialChain → 管道 `|`；RouterChain → RunnableBranch；TransformChain → RunnableLambda。LangChain 官方已将传统 Chain 标记为 legacy，推荐全部迁移到 LCEL。

> 🎯 **面试高频考点 9**：LangChain 的记忆系统有哪些类型？适用场景？
> 答：LangChain 记忆系统核心类型：① ConversationBufferMemory——完整保存所有对话历史，适合短对话和需要完整上下文的场景，缺点是 Token 消耗随对话增长；② ConversationBufferWindowMemory——只保留最近 K 轮对话，适合长对话，平衡上下文和 Token 消耗；③ ConversationSummaryMemory——用 LLM 对历史对话生成摘要，适合超长对话，Token 消耗稳定但可能丢失细节；④ ConversationSummaryBufferMemory——结合窗口和摘要，最近 K 轮保留原文，更早的对话生成摘要；⑤ ConversationEntityMemory——提取对话中的实体信息，适合需要记住用户信息的场景。选择依据是对话长度、Token 预算、信息保留需求。

> 🎯 **面试高频考点 10**：Callback 系统的作用？如何自定义？
> 答：Callback 系统是 LangChain 的事件监听机制，在执行流程的各个关键节点（LLM 开始/结束、工具调用开始/结束、链开始/结束等）触发回调函数。核心作用：① 日志记录——记录执行过程和输入输出；② 监控指标——统计 Token 消耗、延迟、错误率等；③ 调试追踪——结合 LangSmith 进行可视化追踪；④ 自定义逻辑——在特定事件点插入业务逻辑。自定义方式是继承 BaseCallbackHandler，重写需要的事件方法（如 on_llm_start、on_llm_end、on_tool_start 等），通过 config={"callbacks": [handler]} 传入。异步场景继承 AsyncCallbackHandler。

> 🎯 **面试高频考点 11**：LangChain 和 LangGraph 的关系？
> 答：LangChain 和 LangGraph 是互补关系，不是替代关系：① LangChain 是基础组件库——提供 LLM 封装、Prompt 模板、OutputParser、工具定义、Retriever、Memory、Callback 等原子组件；② LangGraph 是编排框架——基于状态机模型，用 StateGraph 将 LangChain 组件编排为复杂的 Agent 工作流；③ 关系——LangGraph 构建在 LangChain 之上，大量使用 LangChain 的组件（ChatModel、Tool、Message 等），LangChain 的 LCEL 组件可以直接作为 LangGraph 的节点；④ 选择——简单的链/管道用 LangChain LCEL，需要循环、条件分支、持久化、HITL 的复杂 Agent 用 LangGraph。两者协同构成完整的 LLM 应用开发栈。

> 🎯 **面试高频考点 12**：LangSmith 的作用？如何集成？
> 答：LangSmith 是 LangChain 生态的可观测性和评估平台，核心功能：① 追踪（Tracing）——记录每次 LLM 调用、工具调用、链执行的完整链路，包括输入输出、延迟、Token 消耗、错误等；② 评估（Evaluation）——对 LLM 应用进行自动化评估，支持自定义评估器、数据集管理、实验对比；③ 调试（Debugging）——可视化查看执行链路，定位问题节点；④ 监控（Monitoring）——生产环境的性能和质量监控。集成方式：设置环境变量 LANGCHAIN_TRACING_V2=true、LANGCHAIN_API_KEY=your-key、LANGCHAIN_PROJECT=project-name，LangChain 会自动将追踪数据发送到 LangSmith。评估通过 langsmith SDK 的 evaluate 函数实现。

> 🎯 **面试高频考点 13**：LangServe 的作用？如何部署？
> 答：LangServe 是将 LangChain LCEL 链部署为 REST API 的工具，基于 FastAPI。核心功能：① 自动生成 API——将 Runnable 链暴露为 /invoke、/stream、/batch 等端点；② 内置 Playground——提供交互式 Web UI 用于测试；③ 输入输出 Schema——自动生成 OpenAPI 文档；④ 异步支持——原生支持异步处理。部署方式：用 add_routes(app, chain, path="/chain") 将链注册到 FastAPI 应用，然后用 uvicorn 启动。生产环境用 Docker 容器化，配合 Nginx 反向代理和 Gunicorn/Uvicorn 多进程。LangServe 适合简单的链部署，复杂 Agent 推荐用 LangGraph Platform。

> 🎯 **面试高频考点 14**：RAG 的完整流程？LangChain 中如何实现？
> 答：RAG（检索增强生成）完整流程：① 文档加载——用 DocumentLoader 加载各种格式文档（PDF、Markdown、HTML 等）；② 文档分割——用 TextSplitter 将长文档切分为合适大小的 Chunk；③ 向量化——用 Embedding 模型将 Chunk 转换为向量；④ 存储——将向量存入向量数据库（Chroma、FAISS、Pinecone 等）；⑤ 检索——用户查询时，用 Retriever 从向量数据库检索相关 Chunk；⑥ 生成——将检索到的上下文和用户问题一起传给 LLM 生成回答。LangChain 实现：`RunnableParallel({"context": retriever, "question": RunnablePassthrough()}) | prompt | model | parser`。高级 RAG 包括混合检索、多查询、重排序、父文档检索等。

> 🎯 **面试高频考点 15**：Agent 的核心组件？ReAct 和 Tool Calling 的区别？
> 答：Agent 核心组件：① LLM——推理和决策引擎；② Tools——Agent 可调用的外部工具（搜索、计算、数据库等）；③ Prompt——引导 Agent 行为的系统提示；④ Memory——对话历史和状态；⑤ 执行循环——思考→行动→观察的循环。ReAct 和 Tool Calling 的区别：① ReAct——基于文本提示，LLM 输出"Thought/Action/Action Input/Observation"格式的文本，需要正则解析提取工具调用，灵活但解析不稳定；② Tool Calling——基于模型原生的 function calling 能力，LLM 输出结构化的 tool_calls 字段（包含 name、arguments、id），解析稳定可靠，是现代推荐方式；③ 选择——支持 function calling 的模型优先用 Tool Calling，不支持的模型用 ReAct。LangGraph 中 create_react_agent 支持两种模式自动切换。

> 🎯 **面试高频考点 16**：RunnableLambda 和 RunnablePassthrough 的区别？
> 答：① RunnableLambda——将任意 Python 函数（同步或异步）包装为 Runnable，函数接收输入返回输出，可以包含任意业务逻辑（数据清洗、格式转换、API 调用等），是 LCEL 中接入自定义逻辑的主要方式；② RunnablePassthrough——透传组件，将输入原样返回，主要用于两个场景：一是在并行分支中透传原始输入（如 RAG 中的 question 透传），二是用 assign 方法在透传的同时添加额外字段。核心区别：RunnableLambda 会转换输入（有副作用/逻辑），RunnablePassthrough 不转换输入（原样透传）。两者经常配合使用：RunnablePassthrough 透传原始数据，RunnableLambda 处理衍生数据。

> 🎯 **面试高频考点 17**：如何处理 LCEL 中的错误？
> 答：LCEL 错误处理有多层机制：① with_retry——自动重试，支持指数退避和抖动，适合临时性错误（API 限流、网络超时）；② with_fallbacks——降级策略，主链失败时切换到备用链（如从 GPT-4 降级到 GPT-4o-mini，或从在线 API 降级到本地模型）；③ 节点内 try/except——在 RunnableLambda 中捕获异常，返回友好错误或默认值；④ Callback 监听——用 CallbackHandler 监听错误事件，记录日志和告警；⑤ 配置 max_concurrency——批量执行时限制并发数，避免触发限流。生产环境建议组合使用：with_retry 处理临时错误 + with_fallbacks 处理持久错误 + 节点内异常处理 + Callback 监控告警。

> 🎯 **面试高频考点 18**：LangChain 项目的最佳目录结构？
> 答：推荐的 LangChain 项目结构：`project/` 下包含 `.env`（环境变量）、`requirements.txt`（依赖）、`README.md`、`app/`（应用代码）、`app/main.py`（FastAPI 入口）、`app/config.py`（配置管理）、`app/chains/`（链定义）、`app/prompts/`（提示词模板）、`app/tools/`（工具定义）、`app/retrievers/`（检索器）、`app/parsers/`（输出解析器）、`app/memory/`（记忆）、`app/callbacks/`（回调）、`app/utils/`（工具函数）、`tests/`（单元测试）、`evaluation/`（评估数据集和评估器）、`scripts/`（脚本）、`Dockerfile`（容器化）。核心原则是按功能模块组织，每个模块职责单一，便于测试和维护。

> 🎯 **面试高频考点 19**：如何评估 LangChain 应用的质量？
> 答：LangChain 应用评估体系：① 建立评估数据集——收集典型输入和期望输出，覆盖正常场景、边界场景、错误场景，至少 20-50 个用例；② 定义多维度评估器——工具准确率（是否调用正确工具）、任务成功率（输出是否满足需求）、回答质量（相关性、准确性、完整性）、延迟（P50/P95/P99）、Token 效率（消耗 Token 数）、错误率；③ 自动化评估——用 LangSmith 的 evaluate 函数或自定义脚本，每次代码变更后自动运行评估；④ 实验对比——用 LangSmith 实验功能对比不同版本（提示词、模型、参数）的效果；⑤ 持续优化——定期审查低质量回答，补充到评估数据集，优化提示词和工具。核心是数据驱动的持续改进。

> 🎯 **面试高频考点 20**：LangChain 生态全景？各组件的作用？
> 答：LangChain 生态包含：① LangChain（核心库）——LLM 封装、Prompt、Parser、Tool、Retriever、Memory、Callback、LCEL 等原子组件；② LangGraph（编排框架）——基于状态机的复杂 Agent 编排，支持持久化、HITL、流式；③ LangSmith（可观测性平台）——追踪、评估、调试、监控；④ LangServe（部署工具）——将链部署为 REST API；⑤ LangGraph Platform（Agent 平台）——生产级 Agent 部署和管理，支持持久化、HITL、流式、任务队列；⑥ 集成生态——数百个第三方集成（模型提供商、向量数据库、工具、数据源等）。各组件关系：LangChain 提供原子组件 → LangGraph 编排复杂工作流 → LangServe/LangGraph Platform 部署 → LangSmith 监控评估，构成完整的开发-部署-运维闭环。

---

> 💡 **深度讲解**
>
> 本附录汇总了 LangChain 最常用的 10 类代码模式和 20 个面试高频考点，是前面 10 章内容的浓缩和补充。代码模式速查覆盖了从基础管道、并行执行、条件分支、自定义函数、透传、批量流式、配置重试、输出解析、记忆集成到回调系统的完整开发场景，每个模式都提供了可直接运行的代码示例。面试高频考点汇总了 LCEL 原理、Runnable 接口、组件对比、迁移指南、生产部署等核心知识点，每个考点都给出了结构化的回答要点。
>
> 掌握这些代码模式和面试考点，你就具备了 LangChain 的实战能力和面试竞争力。建议在实际项目中反复使用这些模式，形成肌肉记忆；在面试准备中重点理解每个考点的"为什么"，而不仅仅是"是什么"。

> **📝 精简总结**
>
> 附录包含 10 类代码模式（基础管道/并行/分支/自定义函数/透传/批量流式/配置重试/OutputParser/Memory/Callback）共 30+ 可运行代码示例，以及 20 个面试高频考点（LCEL/Runnable/组件对比/迁移/记忆/回调/LangGraph关系/LangSmith/LangServe/RAG/Agent/错误处理/项目结构/评估/生态全景），每个考点给出结构化回答要点。

> **🎯 梯度练习题**
>
> **入门级**：
> 1. 默写 LCEL 最基础的 prompt | model | parser 管道代码
> 2. 列出 5 种 OutputParser 类型及适用场景
> 3. 用自己的话解释 RunnableParallel 和 RunnableSequence 的区别
>
> **进阶级**：
> 1. 实现一个完整的 RAG 链，包含检索、提示词、模型、解析器，支持流式输出
> 2. 实现一个带条件分支的链，根据问题类型自动路由到不同的处理链
> 3. 实现一个自定义 CallbackHandler，统计 LLM 调用的 Token 消耗和延迟
>
> **实战级**：
> 1. 构建一个完整的 LangChain 项目，包含规范的目录结构、配置管理、错误处理、重试降级、单元测试、评估体系、Docker 部署
> 2. 准备一份 LangChain 面试指南，覆盖 30 个高频考点，每个考点包含问题、回答要点、代码示例、延伸问题

## 十二、附录二：实战代码模板库

### 12.1 LangChain 常用代码模板

#### 模板1：配置管理

```python
# config.py - 统一配置管理
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # LLM 配置
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))

    # Embedding 配置
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))

    # 向量数据库
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "knowledge_base")

    # LangSmith
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "default")

    # 应用
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))

config = Config()
```

```python
# .env.example - 环境变量模板
# LLM
OPENAI_API_KEY=your-api-key
MODEL_NAME=gpt-4o-mini
TEMPERATURE=0
LLM_TIMEOUT=30
MAX_RETRIES=2

# Embedding
EMBEDDING_MODEL=text-embedding-3-small

# 向量数据库
CHROMA_PERSIST_DIR=./chroma_db
COLLECTION_NAME=knowledge_base

# LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=my-project

# 应用
APP_HOST=0.0.0.0
APP_PORT=8000
```

#### 模板2：模型工厂

```python
# models.py - 模型工厂模式
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from config import config

def get_chat_model(temperature=None, model_name=None):
    """获取 ChatModel 实例"""
    return ChatOpenAI(
        model=model_name or config.MODEL_NAME,
        temperature=temperature if temperature is not None else config.TEMPERATURE,
        timeout=config.LLM_TIMEOUT,
        max_retries=config.MAX_RETRIES,
    )

def get_embedding_model():
    """获取 Embedding 实例"""
    return OpenAIEmbeddings(model=config.EMBEDDING_MODEL)

def get_fast_model():
    """快速模型（用于简单任务）"""
    return ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=15)

def get_strong_model():
    """强模型（用于复杂推理）"""
    return ChatOpenAI(model="gpt-4o", temperature=0.2, timeout=60)
```

```python
# 使用示例
from models import get_chat_model, get_fast_model, get_strong_model

# 默认模型
model = get_chat_model()

# 简单任务用快速模型
fast_model = get_fast_model()

# 复杂任务用强模型
strong_model = get_strong_model()
```

#### 模板3：提示词管理

```python
# prompts.py - 集中管理提示词模板
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# RAG 问答提示
RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的知识问答助手。
请根据以下上下文回答用户问题。
如果上下文中没有相关信息，请如实告知，不要编造。
回答要简洁、准确、有条理。

上下文：
{context}"""),
    ("human", "{question}"),
])

# 摘要提示
SUMMARY_PROMPT = ChatPromptTemplate.from_template(
    "请将以下内容总结为{length}字的摘要，保留关键信息：\n\n{text}"
)

# 翻译提示
TRANSLATE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业翻译，将文本从{source_lang}翻译为{target_lang}，保持原意和风格。"),
    ("human", "{text}"),
])

# Agent 系统提示
AGENT_SYSTEM_PROMPT = """你是一个智能助手，可以使用以下工具解决问题：
{tool_descriptions}

规则：
1. 先分析问题，确定是否需要工具
2. 需要工具时调用合适的工具
3. 根据工具结果给出最终回答
4. 不要编造信息"""

# 带对话历史的提示
CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的助手。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])
```

```python
# 使用示例
from prompts import RAG_PROMPT, SUMMARY_PROMPT

# RAG 链
rag_chain = RAG_PROMPT | model | parser

# 摘要链
summary_chain = SUMMARY_PROMPT | model | parser
result = summary_chain.invoke({"length": "100", "text": long_text})
```

#### 模板4：RAG 完整实现

```python
# rag.py - 完整 RAG 实现
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from models import get_embedding_model, get_chat_model
from prompts import RAG_PROMPT
from config import config
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

class RAGSystem:
    def __init__(self):
        self.embeddings = get_embedding_model()
        self.vectorstore = None
        self.retriever = None
        self.chain = None

    def ingest(self, directory: str):
        """加载文档并建立索引"""
        loader = DirectoryLoader(directory, glob="**/*.md", loader_cls=TextLoader)
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", "。", "！", "？", " ", ""],
        )
        splits = splitter.split_documents(documents)
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=config.CHROMA_PERSIST_DIR,
            collection_name=config.COLLECTION_NAME,
        )
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4},
        )
        self._build_chain()
        return len(splits)

    def load_existing(self):
        """加载已有索引"""
        self.vectorstore = Chroma(
            persist_directory=config.CHROMA_PERSIST_DIR,
            embedding_function=self.embeddings,
            collection_name=config.COLLECTION_NAME,
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
        self._build_chain()

    def _build_chain(self):
        """构建 RAG 链"""
        self.chain = (
            RunnableParallel({
                "context": self.retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
                "question": RunnablePassthrough(),
            })
            | RAG_PROMPT
            | get_chat_model()
            | StrOutputParser()
        )

    def query(self, question: str) -> str:
        """查询"""
        return self.chain.invoke(question)

    def stream_query(self, question: str):
        """流式查询"""
        return self.chain.stream(question)
```

```python
# 使用示例
from rag import RAGSystem

# 初始化并导入文档
rag = RAGSystem()
count = rag.ingest("./docs")
print(f"导入了 {count} 个文档块")

# 查询
answer = rag.query("什么是LCEL？")
print(answer)

# 流式查询
for chunk in rag.stream_query("解释Runnable接口"):
    print(chunk, end="", flush=True)
```

#### 模板5：工具定义模板

```python
# tools.py - 工具定义模板
from langchain_core.tools import tool, StructuredTool
from pydantic import BaseModel, Field
from typing import Optional

# 方式1：@tool 装饰器（最简单）
@tool
def search_web(query: str, max_results: int = 5) -> str:
    """搜索互联网获取信息。

    当用户询问实时信息、新闻、或需要外部知识时使用此工具。
    不要用于计算或常识性问题。

    Args:
        query: 搜索关键词
        max_results: 最大返回结果数，默认5

    Returns:
        搜索结果文本
    """
    # 实际实现调用搜索 API
    return f"搜索'{query}'的结果：..."

@tool
def calculate(expression: str) -> str:
    """计算数学表达式。当需要进行数学计算时使用。

    Args:
        expression: 数学表达式，如 '2+3*4'

    Returns:
        计算结果
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"

# 方式2：StructuredTool（更详细的参数定义）
class WeatherInput(BaseModel):
    city: str = Field(description="城市名称，如'北京'")
    date: Optional[str] = Field(default=None, description="日期，格式'YYYY-MM-DD'，默认今天")

def get_weather_func(city: str, date: Optional[str] = None) -> str:
    return f"{city}{date or '今天'}的天气：晴，25°C"

get_weather = StructuredTool.from_function(
    func=get_weather_func,
    name="get_weather",
    description="获取指定城市的天气信息",
    args_schema=WeatherInput,
)

# 方式3：BaseTool 子类（最灵活）
from langchain_core.tools import BaseTool

class DatabaseQueryTool(BaseTool):
    name: str = "database_query"
    description: str = "查询数据库获取业务数据"

    def _run(self, query: str) -> str:
        # 实际数据库查询
        return f"查询结果：..."

    async def _arun(self, query: str) -> str:
        return self._run(query)

db_tool = DatabaseQueryTool()

# 工具列表
ALL_TOOLS = [search_web, calculate, get_weather, db_tool]
```

```python
# 使用示例
from tools import ALL_TOOLS, search_web

# 直接调用
result = search_web.invoke({"query": "LangChain"})
print(result)

# 绑定到模型
from models import get_chat_model
model_with_tools = get_chat_model().bind_tools(ALL_TOOLS)
```

#### 模板6：输出解析器模板

```python
# parsers.py - 输出解析器模板
from langchain_core.output_parsers import (
    StrOutputParser, JsonOutputParser,
    PydanticOutputParser, CommaSeparatedListOutputParser,
    DatetimeOutputParser, EnumOutputParser,
)
from pydantic import BaseModel, Field
from enum import Enum

# 1. 字符串解析
str_parser = StrOutputParser()

# 2. JSON 解析
json_parser = JsonOutputParser()

# 3. Pydantic 解析
class Article(BaseModel):
    title: str = Field(description="文章标题")
    summary: str = Field(description="文章摘要")
    tags: list[str] = Field(description="标签列表")
    word_count: int = Field(description="字数")

article_parser = PydanticOutputParser(pydantic_object=Article)

# 4. 列表解析
list_parser = CommaSeparatedListOutputParser()

# 5. 日期解析
datetime_parser = DatetimeOutputParser()

# 6. 枚举解析
class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

sentiment_parser = EnumOutputParser(enum=Sentiment)

# 使用示例
from langchain_core.prompts import ChatPromptTemplate
from models import get_chat_model

# Pydantic 解析完整示例
prompt = ChatPromptTemplate.from_template(
    "分析文章并提取信息：{format_instructions}\n\n文章：{article}"
).partial(format_instructions=article_parser.get_format_instructions())

chain = prompt | get_chat_model() | article_parser
result = chain.invoke({"article": "这是一篇关于AI的文章..."})
print(f"标题: {result.title}")
print(f"标签: {result.tags}")
print(f"字数: {result.word_count}")
```

#### 模板7：回调处理器模板

```python
# callbacks.py - 回调处理器模板
from langchain_core.callbacks import BaseCallbackHandler, AsyncCallbackHandler
from langchain_core.outputs import LLMResult
import time
import logging

logger = logging.getLogger(__name__)

# 1. Token 统计回调
class TokenStatsCallback(BaseCallbackHandler):
    def __init__(self):
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.call_count = 0

    def on_llm_end(self, response: LLMResult, **kwargs):
        self.call_count += 1
        if response.llm_output and "token_usage" in response.llm_output:
            usage = response.llm_output["token_usage"]
            self.total_tokens += usage.get("total_tokens", 0)
            self.prompt_tokens += usage.get("prompt_tokens", 0)
            self.completion_tokens += usage.get("completion_tokens", 0)

    def get_stats(self):
        return {
            "call_count": self.call_count,
            "total_tokens": self.total_tokens,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
        }

# 2. 延迟统计回调
class LatencyCallback(BaseCallbackHandler):
    def __init__(self):
        self.start_times = {}
        self.latencies = []

    def on_llm_start(self, serialized, prompts, **kwargs):
        self.start_times[id(serialized)] = time.time()

    def on_llm_end(self, response, **kwargs):
        # 简化实现
        pass

    def on_chain_start(self, serialized, inputs, **kwargs):
        self.start_times["chain"] = time.time()

    def on_chain_end(self, outputs, **kwargs):
        if "chain" in self.start_times:
            latency = time.time() - self.start_times.pop("chain")
            self.latencies.append(latency)

# 3. 日志回调
class LoggingCallback(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        logger.info(f"LLM 开始: {prompts[0][:100]}...")

    def on_llm_end(self, response, **kwargs):
        text = response.generations[0][0].text[:100]
        logger.info(f"LLM 结束: {text}...")

    def on_tool_start(self, serialized, input_str, **kwargs):
        logger.info(f"工具调用: {serialized.get('name')} - {input_str[:50]}")

    def on_tool_end(self, output, **kwargs):
        logger.info(f"工具结果: {output[:50]}")

    def on_chain_error(self, error, **kwargs):
        logger.error(f"链错误: {error}")

# 4. 成本估算回调
class CostCallback(BaseCallbackHandler):
    PRICING = {
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4o": {"input": 0.005, "output": 0.015},
    }

    def __init__(self):
        self.total_cost = 0.0

    def on_llm_end(self, response, **kwargs):
        if response.llm_output and "token_usage" in response.llm_output:
            usage = response.llm_output["token_usage"]
            model = response.llm_output.get("model_name", "gpt-4o-mini")
            pricing = self.PRICING.get(model, self.PRICING["gpt-4o-mini"])
            cost = (usage["prompt_tokens"] / 1000 * pricing["input"] +
                    usage["completion_tokens"] / 1000 * pricing["output"])
            self.total_cost += cost
```

```python
# 使用示例
from callbacks import TokenStatsCallback, LoggingCallback, CostCallback
from langchain_core.prompts import ChatPromptTemplate
from models import get_chat_model

token_stats = TokenStatsCallback()
cost_tracker = CostCallback()

chain = ChatPromptTemplate.from_template("解释{topic}") | get_chat_model()

result = chain.invoke(
    {"topic": "回调机制"},
    config={"callbacks": [token_stats, LoggingCallback(), cost_tracker]}
)

print(f"Token 统计: {token_stats.get_stats()}")
print(f"估算成本: ${cost_tracker.total_cost:.4f}")
```

#### 模板8：错误处理与重试

```python
# error_handling.py - 错误处理与重试模板
from langchain_core.runnables import RunnableRetry, RunnableWithFallbacks
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 基础重试
primary_model = ChatOpenAI(model="gpt-4o", temperature=0, timeout=30)
retry_model = primary_model.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True,
)

chain = ChatPromptTemplate.from_template("解释{topic}") | retry_model | StrOutputParser()

try:
    result = chain.invoke({"topic": "重试机制"})
    print(result)
except Exception as e:
    print(f"重试3次后失败: {e}")

# 2. 降级策略（Fallbacks）
fast_model = ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=15)
strong_model = ChatOpenAI(model="gpt-4o", temperature=0, timeout=60)

# 主链用快速模型，失败时降级到强模型
primary_chain = ChatPromptTemplate.from_template("解释{topic}") | fast_model | StrOutputParser()
fallback_chain = ChatPromptTemplate.from_template("解释{topic}") | strong_model | StrOutputParser()

chain_with_fallback = primary_chain.with_fallbacks([fallback_chain])
result = chain_with_fallback.invoke({"topic": "降级策略"})
print(result)

# 3. 组合重试和降级
robust_chain = (
    ChatPromptTemplate.from_template("解释{topic}")
    | primary_model.with_retry(stop_after_attempt=2)
    | StrOutputParser()
).with_fallbacks([
    ChatPromptTemplate.from_template("解释{topic}") | fast_model | StrOutputParser()
])

# 4. 自定义异常处理
from langchain_core.runnables import RunnableLambda

def safe_invoke(chain, input_data, default="抱歉，处理失败，请稍后重试"):
    try:
        return chain.invoke(input_data)
    except Exception as e:
        logging.error(f"链执行失败: {e}")
        return default

# 5. 批量执行的错误隔离
def safe_batch(chain, inputs, max_concurrency=3):
    results = []
    for i in range(0, len(inputs), max_concurrency):
        batch = inputs[i:i+max_concurrency]
        try:
            batch_results = chain.batch(batch, config={"max_concurrency": max_concurrency})
            results.extend(batch_results)
        except Exception as e:
            logging.error(f"批量执行失败: {e}")
            results.extend([None] * len(batch))
    return results
```

#### 模板9：评估体系

```python
# evaluation.py - 评估体系模板
from langsmith.evaluation import evaluate
from langsmith import Client
import json

# 1. 创建评估数据集
def create_eval_dataset(dataset_name: str, examples: list[dict]):
    client = Client()
    try:
        dataset = client.create_dataset(dataset_name)
    except Exception:
        dataset = client.read_dataset(dataset_name=dataset_name)

    for ex in examples:
        client.create_example(
            inputs={"question": ex["question"]},
            outputs=ex.get("expected", {}),
            dataset_id=dataset.id,
        )
    return dataset

# 2. 评估器定义
def accuracy_evaluator(run, example):
    """准确率评估"""
    expected = example.outputs.get("answer", "")
    actual = run.outputs.get("output", "")
    score = 1.0 if expected.lower() in actual.lower() else 0.0
    return {"key": "accuracy", "score": score}

def relevance_evaluator(run, example):
    """相关性评估（基于关键词）"""
    question = example.inputs.get("question", "")
    answer = run.outputs.get("output", "")
    keywords = [w for w in question.split() if len(w) > 1]
    if not keywords:
        return {"key": "relevance", "score": 1.0}
    hits = sum(1 for kw in keywords if kw.lower() in answer.lower())
    return {"key": "relevance", "score": hits / len(keywords)}

def tool_usage_evaluator(run, example):
    """工具使用评估"""
    expected_tool = example.outputs.get("expected_tool")
    # 从追踪中获取工具调用
    tool_calls = []
    for event in run.events:
        if event.get("name") == "tools":
            tool_calls.append(event.get("metadata", {}).get("tool_name"))
    if expected_tool:
        score = 1.0 if expected_tool in tool_calls else 0.0
    else:
        score = 1.0 if not tool_calls else 0.0
    return {"key": "tool_usage", "score": score}

# 3. 运行评估
def run_evaluation(chain, dataset_name: str):
    def agent_invoke(inputs):
        return {"output": chain.invoke(inputs["question"])}

    results = evaluate(
        agent_invoke,
        data=dataset_name,
        evaluators=[accuracy_evaluator, relevance_evaluator],
        experiment_prefix="v1.0",
        max_concurrency=3,
    )
    return results

# 4. 评估数据集示例
eval_examples = [
    {
        "question": "什么是LCEL？",
        "expected": {"answer": "表达式语言", "expected_tool": None},
    },
    {
        "question": "计算 15*23",
        "expected": {"answer": "345", "expected_tool": "calculator"},
    },
    # 更多用例...
]
```

#### 模板10：FastAPI 部署

```python
# main.py - FastAPI 部署模板
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 请求/响应模型
class QueryRequest(BaseModel):
    question: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    stream: bool = False

class QueryResponse(BaseModel):
    answer: str
    metadata: dict = {}

# 应用初始化
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    logger.info("应用启动中...")
    app.state.rag = None  # 延迟初始化
    yield
    # 关闭时清理
    logger.info("应用关闭")

app = FastAPI(title="LangChain RAG API", version="1.0.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

# 查询接口
@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        # 延迟初始化 RAG
        if app.state.rag is None:
            from rag import RAGSystem
            app.state.rag = RAGSystem()
            app.state.rag.load_existing()

        answer = app.state.rag.query(request.question)
        return QueryResponse(answer=answer, metadata={"model": "gpt-4o-mini"})
    except Exception as e:
        logger.error(f"查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 流式查询接口
from fastapi.responses import StreamingResponse

@app.post("/query/stream")
async def query_stream(request: QueryRequest):
    if app.state.rag is None:
        from rag import RAGSystem
        app.state.rag = RAGSystem()
        app.state.rag.load_existing()

    async def generate():
        for chunk in app.state.rag.stream_query(request.question):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

# 批量查询
class BatchRequest(BaseModel):
    questions: list[str]

@app.post("/batch")
async def batch_query(request: BatchRequest):
    if app.state.rag is None:
        from rag import RAGSystem
        app.state.rag = RAGSystem()
        app.state.rag.load_existing()
    results = [app.state.rag.query(q) for q in request.questions]
    return {"answers": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
```

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LANGCHAIN_TRACING_V2=true
      - LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY}
    volumes:
      - ./chroma_db:/app/chroma_db
    restart: unless-stopped
```

---

> 💡 **深度讲解**
>
> 本附录提供了 10 类 LangChain 实战代码模板，覆盖配置管理、模型工厂、提示词管理、RAG 完整实现、工具定义、输出解析器、回调处理器、错误处理与重试、评估体系、FastAPI 部署等生产开发的全流程。这些模板是从大量生产项目中提炼出来的最佳实践，可以直接复制到项目中使用，也可以根据具体需求进行修改和扩展。
>
> 掌握这些模板的核心价值在于：① 提高开发效率——不需要从零开始编写基础架构代码；② 保证代码质量——模板经过生产验证，遵循最佳实践；③ 统一团队规范——团队使用相同的模板，代码风格一致；④ 降低维护成本——标准化的代码结构便于理解和维护。建议在实际项目中根据这些模板建立自己的代码脚手架，持续迭代优化。

> **📝 精简总结**
>
> 附录二提供 10 类 LangChain 实战代码模板：配置管理（Config类+.env）、模型工厂（get_chat_model/get_fast_model/get_strong_model）、提示词管理（集中管理Prompt模板）、RAG完整实现（RAGSystem类含ingest/query/stream）、工具定义（@tool/StructuredTool/BaseTool三种方式）、输出解析器（6种Parser完整示例）、回调处理器（Token统计/延迟/日志/成本估算）、错误处理（with_retry/with_fallbacks/异常隔离）、评估体系（数据集+评估器+运行评估）、FastAPI部署（REST API+流式+Docker+docker-compose）。

> **🎯 梯度练习题**
>
> **入门级**：
> 1. 使用配置管理模板，创建一个包含 5 个配置项的 Config 类
> 2. 使用工具定义模板，用 @tool 装饰器定义 3 个工具
> 3. 使用 FastAPI 部署模板，创建一个 /health 和 /query 接口
>
> **进阶级**：
> 1. 使用 RAG 完整实现模板，搭建一个文档问答系统，支持文档导入和查询
> 2. 使用回调处理器模板，实现一个组合回调（Token统计+延迟+成本估算）
> 3. 使用评估体系模板，为一个 RAG 系统建立评估数据集和 3 个评估器
>
> **实战级**：
> 1. 综合使用所有模板，构建一个完整的生产级 RAG 应用：配置管理+模型工厂+提示词管理+RAG+工具+回调+错误处理+评估+Docker部署，包含完整的项目结构和测试
> 2. 将模板中的 RAG 系统升级为高级 RAG：添加混合检索、多查询、重排序、父文档检索，并用评估体系对比基础 RAG 和高级 RAG 的效果差异

## 十三、附录三：常用代码片段速查

### 13.1 LangChain 代码片段

```python
# 片段1：环境变量快速设置
import os
os.environ["OPENAI_API_KEY"] = "your-key"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-key"
os.environ["LANGCHAIN_PROJECT"] = "my-project"
```

```python
# 片段2：最简 LCEL 链
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

chain = ChatPromptTemplate.from_template("解释{topic}") | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()
print(chain.invoke({"topic": "LCEL"}))
```

```python
# 片段3：流式输出
for chunk in chain.stream({"topic": "流式输出"}):
    print(chunk, end="", flush=True)
```

```python
# 片段4：批量执行
results = chain.batch([{"topic": "A"}, {"topic": "B"}, {"topic": "C"}])
```

```python
# 片段5：异步执行
import asyncio
result = asyncio.run(chain.ainvoke({"topic": "异步"}))
```

```python
# 片段6：RunnableParallel 并行
from langchain_core.runnables import RunnableParallel
parallel = RunnableParallel(a=chain, b=chain)
result = parallel.invoke({"topic": "并行"})
```

```python
# 片段7：RunnableLambda 自定义函数
from langchain_core.runnables import RunnableLambda
custom = RunnableLambda(lambda x: x.upper())
print(custom.invoke("hello"))
```

```python
# 片段8：RunnablePassthrough 透传
from langchain_core.runnables import RunnablePassthrough
chain = RunnablePassthrough.assign(extra=lambda x: f"processed_{x['topic']}")
print(chain.invoke({"topic": "test"}))
```

```python
# 片段9：with_retry 重试
retry_chain = chain.with_retry(stop_after_attempt=3)
```

```python
# 片段10：with_fallbacks 降级
fallback_chain = chain.with_fallbacks([other_chain])
```

```python
# 片段11：JsonOutputParser
from langchain_core.output_parsers import JsonOutputParser
parser = JsonOutputParser()
chain = prompt | model | parser
result = chain.invoke({"question": "返回JSON"})
```

```python
# 片段12：PydanticOutputParser
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class Person(BaseModel):
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")

parser = PydanticOutputParser(pydantic_object=Person)
```

### 13.2 LangGraph 代码片段

```python
# 片段1：最简 StateGraph
from langgraph.graph import StateGraph, END
from typing import TypedDict

class State(TypedDict):
    input: str

def node(state): return {"input": state["input"] + "!"}
wf = StateGraph(State)
wf.add_node("n", node)
wf.set_entry_point("n")
wf.add_edge("n", END)
graph = wf.compile()
print(graph.invoke({"input": "hello"}))
```

```python
# 片段2：带 Reducer 的 State
from typing import Annotated
import operator
from langchain_core.messages import BaseMessage

class MsgState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
```

```python
# 片段3：条件边
def router(state): return "a" if state["x"] > 0 else "b"
wf.add_conditional_edges("start", router, {"a": "node_a", "b": "node_b"})
```

```python
# 片段4：Tool Calling Agent（最简）
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def calc(expr: str) -> str:
    """计算"""
    return str(eval(expr))

agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), [calc])
result = agent.invoke({"messages": [{"role": "user", "content": "1+1"}]})
```

```python
# 片段5：MemorySaver 持久化
from langgraph.checkpoint.memory import MemorySaver
graph = wf.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "user-1"}}
```

```python
# 片段6：PostgresSaver 持久化
from langgraph.checkpoint.postgres import PostgresSaver
cp = PostgresSaver.from_conn_string("postgresql://user:pass@localhost/db")
with cp as c: c.setup()
graph = wf.compile(checkpointer=cp)
```

```python
# 片段7：HITL interrupt
from langgraph.types import interrupt, Command

def review_node(state):
    decision = interrupt({"type": "review", "content": state["draft"]})
    return {"approved": decision.get("approved", False)}

# 恢复
graph.invoke(Command(resume={"approved": True}), config)
```

```python
# 片段8：流式输出 messages 模式
for msg, meta in graph.stream(state, config, stream_mode="messages"):
    if msg.content:
        print(msg.content, end="", flush=True)
```

```python
# 片段9：流式输出 updates 模式
for node, update in graph.stream(state, config, stream_mode="updates"):
    print(f"{node}: {update}")
```

```python
# 片段10：查看状态历史
history = list(graph.get_state_history(config))
print(f"检查点数: {len(history)}")
```

```python
# 片段11：ToolNode
from langgraph.prebuilt import ToolNode, tools_condition
wf.add_node("tools", ToolNode(tools))
wf.add_conditional_edges("agent", tools_condition)
wf.add_edge("tools", "agent")
```

```python
# 片段12：recursion_limit 防循环
config = {"recursion_limit": 50, "configurable": {"thread_id": "t1"}}
```

```python
# 片段13：最大迭代控制
class IterState(TypedDict):
    messages: Annotated[list, operator.add]
    iteration: Annotated[int, operator.add]

def agent_node(state):
    if state["iteration"] >= 10:
        return {"messages": [AIMessage(content="超限")], "iteration": 1}
    # ... 正常逻辑
```

```python
# 片段14：并行分支
wf.add_edge("start", "branch_a")
wf.add_edge("start", "branch_b")
wf.add_edge("branch_a", "merge")
wf.add_edge("branch_b", "merge")
```

```python
# 片段15：循环回到入口
wf.add_conditional_edges("process", lambda s: "process" if s["count"] < 3 else "end",
    {"process": "process", "end": END})
```

```python
# 片段16：LangServe 部署
from fastapi import FastAPI
from langserve import add_routes
app = FastAPI()
add_routes(app, graph, path="/agent")
```

```python
# 片段17：获取当前状态
state = graph.get_state(config)
print(state.values)
print(state.next)
```

```python
# 片段18：更新状态
graph.update_state(config, {"key": "value"})
```

```python
# 片段19：@tool 定义工具
from langchain_core.tools import tool

@tool
def search(query: str) -> str:
    """搜索知识库"""
    return f"结果: {query}"
```

```python
# 片段20：StructuredTool 定义
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

class Input(BaseModel):
    x: int = Field(description="参数x")

def func(x: int) -> str: return str(x * 2)
tool = StructuredTool.from_function(func=func, name="double", description="翻倍", args_schema=Input)
```

```python
# 片段21：ToolMessage 构造
from langchain_core.messages import ToolMessage
msg = ToolMessage(content="结果", tool_call_id="call_abc123")
```

```python
# 片段22：AIMessage 带 tool_calls
from langchain_core.messages import AIMessage
msg = AIMessage(content="", tool_calls=[{"name": "search", "args": {"query": "test"}, "id": "call_1"}])
```

```python
# 片段23：图可视化
graph.get_graph().print_ascii()
```

```python
# 片段24：Mermaid 图导出
mermaid_code = graph.get_graph().draw_mermaid()
print(mermaid_code)
```

---

> **📝 精简总结**
>
> 附录三提供 LangChain 12 个 + LangGraph 24 个常用代码片段速查，覆盖环境设置、最简链、流式、批量、异步、并行、自定义函数、透传、重试、降级、输出解析器、StateGraph、Reducer、条件边、Tool Calling、持久化、HITL、流式、状态历史、ToolNode、防循环、迭代控制、并行分支、循环、部署、状态管理、工具定义、消息构造、图可视化等高频开发场景。每个片段都是可直接复制运行的最小代码。
