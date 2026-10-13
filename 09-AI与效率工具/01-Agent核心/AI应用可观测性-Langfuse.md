---
title: AI 应用可观测性 - Langfuse
tags: [AI应用, AI工程化, 可观测性, 效率工具]
category: AI与效率工具
created: 2026-08-13
updated: 2026-09-08
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[LLM接口封装与统一SDK]]", "[[AI网关与多模型路由]]"]
aliases: [AI应用可观测性-Langfuse, AI应用可观测性与Langfuse集成]
---

# AI 应用可观测性 - Langfuse

> **文档说明**：系统讲解 AI 应用可观测性的核心概念、Langfuse 的架构与功能、集成方式、追踪分析、评估评分、成本监控，以及在生产环境中的最佳实践。
>
> **适用人群**：AI 应用开发者、需要监控和优化 LLM 应用的全栈工程师、MLOps 工程师
>
> **前置知识**：[[LLM接口封装与统一SDK]]、[[AI网关与多模型路由]]、[[RAG架构设计与流程]]

---

## 一、概述

**AI 应用可观测性（AI Observability）** 是对 LLM 应用的全链路进行监控、追踪、分析和评估的能力。传统 APM（应用性能监控）关注 HTTP 请求、数据库查询等，而 AI 可观测性需要额外关注：Prompt 内容、模型响应、Token 消耗、Embedding 检索、Agent 决策链等 AI 特有维度。

**Langfuse** 是一个开源的 LLM 应用可观测性平台，提供追踪、评估、提示词管理、成本分析等功能，支持自部署和云服务，是目前最流行的 AI 可观测性工具之一。

### 1. 为什么 AI 应用需要可观测性

| 痛点 | 没有可观测性 | 有可观测性 |
|------|------------|-----------|
| 调试困难 | 不知道 LLM 为什么输出错误 | 完整追踪 Prompt、上下文、响应，快速定位 |
| 成本失控 | 不知道 Token 花在哪里 | 按模型/应用/用户维度分析成本 |
| 质量波动 | 不知道输出质量是否下降 | 自动评分 + 人工标注，监控质量趋势 |
| 延迟问题 | 不知道哪个环节慢 | 全链路追踪，定位瓶颈（检索/模型/后处理） |
| 用户反馈 | 无法关联用户反馈到具体调用 | 给 Trace 打标签，关联用户反馈 |
| 模型对比 | 难以量化不同模型的效果 | A/B 测试，对比质量/成本/延迟 |

### 2. AI 可观测性的核心维度

```mermaid
graph TB
    subgraph AI可观测性
        A[追踪 Tracing] --> A1[全链路调用链]
        A --> A2[Prompt/Response记录]
        A --> A3[Token消耗统计]
        B[评估 Evaluation] --> B1[自动评分]
        B --> B2[人工标注]
        B --> B3[质量趋势]
        C[成本 Cost] --> C1[按维度分析]
        C --> C2[预算告警]
        C --> C3[成本优化]
        D[提示词管理 Prompt Management] --> D1[版本管理]
        D --> D2[A/B测试]
        D --> D3[线上发布]
        E[用户反馈 Feedback] --> E1[点赞/点踩]
        E --> E2[问题标注]
        E --> E3[反馈分析]
    end
```

### 3. 主流 AI 可观测性工具对比

| 工具 | 开源 | 自部署 | 特点 | 适用场景 |
|------|------|--------|------|---------|
| **Langfuse** | ✅ | ✅ | 功能全面，提示词管理，活跃社区 | 生产环境首选 |
| **LangSmith** | ❌ | ❌ | LangChain 生态深度集成 | LangChain 用户 |
| **Helicone** | ✅ | ✅ | 轻量，专注日志和成本 | 简单需求 |
| **PromptLayer** | ❌ | ❌ | 专注 Prompt 管理和版本 | Prompt 工程 |
| **Arize Phoenix** | ✅ | ✅ | 专注评估和监控 | 模型评估 |
| **Braintrust** | ✅ | ✅ | 评估驱动，实验管理 | 实验对比 |
| **OpenTelemetry + LLM** | ✅ | ✅ | 标准协议，需自建 | 企业级定制 |
<div style="background:linear-gradient(135deg,#667eea,#764ba2);border-radius:16px;padding:20px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#fff;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes pulse{0%,100%{transform:scale(1);opacity:.9}50%{transform:scale(1.03);opacity:1}}.dk-layer{border-radius:8px;padding:12px 16px;margin:6px auto;text-align:center;font-weight:600;animation:pulse 3s ease-in-out infinite}.dk-outer{background:rgba(255,255,255,.15);border:2px solid rgba(255,255,255,.5);max-width:340px;animation-delay:0s}.dk-middle{background:rgba(255,255,255,.2);border:2px solid rgba(255,255,255,.6);max-width:280px;animation-delay:.5s}.dk-inner{background:rgba(255,255,255,.25);border:2px solid rgba(255,255,255,.7);max-width:220px;animation-delay:1s}.dk-arrow{text-align:center;font-size:18px;margin:2px 0}.dk-label{font-size:12px;opacity:.85;font-weight:400;margin-top:4px}</style>
<div style="text-align:center;font-size:15px;font-weight:700;margin-bottom:14px;padding-bottom:10px;border-bottom:1.5px solid rgba(255,255,255,.22);letter-spacing:1px">🔍 Langfuse 可观测性五层体系</div>
<div class="dk-layer dk-outer">追踪 Tracing<div class="dk-label">全链路调用链 + Prompt/Response记录 + Token统计</div></div>
<div class="dk-arrow">▼ 包含</div>
<div class="dk-layer dk-middle">评估 Evaluation<div class="dk-label">LLM-as-Judge自动评分 + 人工标注 + 质量趋势</div></div>
<div class="dk-arrow">▼ 包含</div>
<div class="dk-layer dk-inner">成本 Cost<div class="dk-label">按模型/用户/时间维度分析 + 预算告警</div></div>
</div>


---

> 💡 **深度讲解**：AI 应用可观测性与传统 APM 的本质区别在于"观测对象的非确定性"。传统应用的每次调用路径是确定的——给定相同输入，程序走相同的代码路径，产生相同的输出。因此传统 APM 只需要记录请求的入口、出口、耗时、错误码，就能定位问题。而 LLM 应用的调用路径是非确定的——相同的输入在不同时间可能触发不同的工具调用、不同的检索结果、不同的生成内容。这意味着可观测性必须记录"完整的语义上下文"——不仅是耗时和错误码，还包括每一步 LLM 调用的完整 Prompt 和 Response、检索到的文档片段、工具调用的参数和返回值。Langfuse 等专门的 LLM 可观测性工具就是为这种需求设计的，它们提供了比传统 APM 更丰富的语义记录能力和更适合 AI 场景的分析界面。
>
> **📝 精简总结**：AI 可观测性是对 LLM 应用全链路的监控、追踪、分析和评估；核心维度包括追踪（Tracing）、评估（Evaluation）、成本（Cost）、提示词管理（Prompt Management）、用户反馈（Feedback）；Langfuse 是开源首选，功能全面且支持自部署；与传统 APM 的区别在于观测对象的非确定性，需要记录完整语义上下文。

---

## 二、Langfuse 核心概念

### 1. 数据模型

```mermaid
erDiagram
    TRACE ||--o{ OBSERVATION : contains
    TRACE ||--o{ SCORE : has
    OBSERVATION ||--o{ OBSERVATION : nested
    TRACE {
        string id
        string name
        string userId
        string sessionId
        json metadata
        datetime timestamp
    }
    OBSERVATION {
        string id
        string traceId
        string parentObservationId
        string type "GENERATION/SPAN/EVENT"
        string name
        json input
        json output
        string model
        int promptTokens
        int completionTokens
        float latency
    }
    SCORE {
        string id
        string traceId
        string name
        float value
        string comment
        string userId
    }
```

| 概念 | 说明 |
|------|------|
| **Trace（追踪）** | 一次完整的用户请求/交互，包含所有子操作 |
| **Observation（观测）** | Trace 中的单个操作，有三种类型 |
| ├ Generation（生成） | LLM 调用，记录 model/input/output/tokens |
| ├ Span（跨度） | 非 LLM 操作，如检索、数据库查询、API 调用 |
| └ Event（事件） | 瞬时事件，如用户点击、错误发生 |
| **Score（评分）** | 对 Trace 的质量评分，可自动或人工 |
| **Session（会话）** | 多个 Trace 组成的对话/会话 |
| **User（用户）** | 关联 Trace 的用户标识 |
> 🔍 **知识点深度解析**
>
> **作用**：Langfuse 通过 Trace-Observation-Score 数据模型实现 LLM 应用的全链路可观测性，解决传统 APM 无法记录语义上下文（Prompt/Response/检索片段）的问题，支持追踪、评估、成本分析、提示词管理等核心能力。
>
> **原理**：Trace 代表一次完整用户请求，包含多个嵌套的 Observation（Generation/Span/Event三种类型），Score 关联 Trace 进行多维度质量评分。数据模型借鉴分布式追踪但针对 LLM 场景扩展了语义记录能力，Generation 类型专门记录 LLM 调用的完整 input/output/model/tokens。
>
> **用法要点**：① LLM 调用使用 Generation 类型并设置 usage 字段才能统计 Token 成本 ② 非 LLM 操作用 Span，瞬时事件用 Event ③ 流式响应结束后必须手动更新 output 和 usage ④ 进程退出前调用 langfuse.flush() ⑤ 生产环境用 SSE/HTTP 传输独立部署


### 2. 一个 RAG 请求的 Trace 结构

```text
Trace: "RAG问答请求"
├── Span: "接收HTTP请求" (2ms)
├── Span: "查询重写" (调用LLM)
│   └── Generation: "gpt-4o-mini" (120ms, 45→30 tokens)
├── Span: "向量检索" (45ms)
│   ├── Span: "Embedding生成" (30ms)
│   │   └── Generation: "bge-large-zh" (25ms, 15→1024 tokens)
│   └── Span: "Milvus搜索" (12ms, top-5)
├── Span: "重排序" (80ms)
│   └── Generation: "bge-reranker" (75ms)
├── Span: "LLM生成回答" (2500ms)
│   └── Generation: "gpt-4o" (2450ms, 850→320 tokens, 流式)
├── Span: "后处理" (5ms)
└── Score: "用户满意度" (0.8, 人工)
```

---

> 💡 **深度讲解**：Langfuse 的数据模型设计借鉴了分布式追踪（OpenTelemetry）的 Trace/Span 模型，但针对 LLM 场景做了重要扩展。传统追踪的 Span 主要记录服务间调用的耗时和状态，而 Langfuse 的 Observation 分为三种类型：Generation（LLM 调用，记录完整的 input/output/model/tokens）、Span（非 LLM 操作，记录耗时和元数据）、Event（瞬时事件，记录时间点和描述）。这种分类使得 Langfuse 既能像传统 APM 一样分析性能瓶颈，又能深入 LLM 内部分析语义内容。Trace 的树状结构（Observation 可以嵌套）完美对应了 LLM 应用的调用链——根 Trace 是用户请求，子 Span 是检索、重排序等阶段，Generation 嵌套在 Span 中表示该阶段的 LLM 调用。这种结构在 Langfuse 面板中以瀑布图和火焰图的形式展示，非常直观。
>
> **📝 精简总结**：Langfuse 数据模型包括 Trace（一次请求）、Observation（单个操作，分 Generation/Span/Event 三种）、Score（质量评分）、Session（会话）、User（用户）；RAG 请求的 Trace 包含查询重写、向量检索、重排序、LLM 生成、后处理等多个 Span，每个 LLM 调用是嵌套的 Generation；数据模型借鉴分布式追踪但针对 LLM 场景扩展了语义记录能力。

---

## 三、Langfuse 集成

### 1. 安装与配置

```python
# 安装 Langfuse SDK
pip install langfuse

# 环境变量配置
export LANGFUSE_PUBLIC_KEY="pk-lf-xxx"
export LANGFUSE_SECRET_KEY="sk-lf-xxx"
export LANGFUSE_HOST="https://cloud.langfuse.com"  # 或自部署地址
```

```python
# 初始化 Langfuse
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk-lf-xxx",
    secret_key="sk-lf-xxx",
    host="https://cloud.langfuse.com",
)
```

### 2. 基础追踪（装饰器方式）

```python
from langfuse.decorators import observe, langfuse_context

# 使用 @observe 装饰器自动追踪
@observe()
def rag_question(question: str, user_id: str) -> str:
    # 设置用户标识
    langfuse_context.update_current_trace(
        user_id=user_id,
        metadata={"source": "web", "version": "1.2.0"}
    )

    # 1. 查询重写
    rewritten = rewrite_query(question)

    # 2. 向量检索
    docs = vector_search(rewritten, top_k=5)

    # 3. LLM 生成
    answer = generate_answer(question, docs)

    return answer

@observe(name="查询重写")
def rewrite_query(question: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"优化查询: {question}"}]
    )
    return response.choices[0].message.content

@observe(name="向量检索")
def vector_search(query: str, top_k: int = 5) -> list:
    # 检索逻辑
    return results

@observe(name="LLM生成")
def generate_answer(question: str, docs: list) -> str:
    context = "\n".join([d.content for d in docs])
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"基于以下文档回答: {context}"},
            {"role": "user", "content": question}
        ],
        stream=True
    )
    # 流式响应处理
    answer = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content
    return answer
```

### 3. 手动追踪（细粒度控制）

```python
def rag_question_manual(question: str, user_id: str):
    # 创建 Trace
    trace = langfuse.trace(
        name="RAG问答",
        user_id=user_id,
        metadata={"question": question}
    )

    # Span: 查询重写
    rewrite_span = trace.span(name="查询重写")
    rewritten = rewrite_query(question)
    rewrite_span.end(output={"rewritten": rewritten})

    # Span: 向量检索
    search_span = trace.span(name="向量检索")
    docs = vector_search(rewritten)
    search_span.end(output={"count": len(docs)})

    # Generation: LLM 调用（详细记录）
    generation = trace.generation(
        name="LLM生成回答",
        model="gpt-4o",
        input=[{"role": "user", "content": question}],
        metadata={"temperature": 0.7, "max_tokens": 512}
    )

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": question}],
        temperature=0.7,
        max_tokens=512
    )

    # 结束 Generation，记录输出和 Token
    generation.end(
        output=response.choices[0].message.content,
        usage={
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
    )

    # 给 Trace 打分
    trace.score(
        name="回答质量",
        value=0.85,
        comment="回答准确但不够详细"
    )

    return response.choices[0].message.content
```

### 4. OpenAI 集成（自动追踪）

```python
# 使用 Langfuse 的 OpenAI 包装器，自动追踪所有 LLM 调用
from langfuse.openai import openai

# 直接使用，无需修改调用代码
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "你好"}],
    temperature=0.7,
    # Langfuse 特定参数
    langfuse_trace_id="trace-123",
    langfuse_name="问候调用",
    langfuse_metadata={"env": "production"}
)
```

### 5. LangChain 集成

```python
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler(
    public_key="pk-lf-xxx",
    secret_key="sk-lf-xxx",
    host="https://cloud.langfuse.com",
    session_id="session-123",
    user_id="user-456",
)

# LangChain 调用时传入 handler
chain.invoke({"input": "你好"}, config={"callbacks": [langfuse_handler]})
```

### 6. 流式响应追踪

```python
@observe()
def stream_answer(question: str):
    stream = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": question}],
        stream=True,
    )

    answer = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            answer += content
            yield content

    # 流式结束后更新当前 generation 的输出
    langfuse_context.update_current_observation(
        output=answer,
        usage={"total_tokens": estimate_tokens(answer)}
    )
```

---

> 💡 **深度讲解**：Langfuse 提供了三种集成方式，适用于不同场景：① 装饰器方式（`@observe()`）最简单，适合函数级追踪，自动创建 Span 并记录入参出参，但细粒度控制不足；② 手动追踪（`trace.span()` / `trace.generation()`）最灵活，可以精确控制每个 Span 的名称、输入输出、元数据、usage，适合生产环境的精细追踪；③ OpenAI/LangChain 包装器最便捷，自动追踪所有 LLM 调用，适合快速接入，但自定义能力有限。生产环境推荐"装饰器 + 手动"混合方式——用 `@observe()` 装饰入口函数自动创建 Trace，在函数内部用 `langfuse_context.update_current_observation()` 手动补充 LLM 调用的 usage 和元数据。关键注意事项：① 必须在进程退出前调用 `langfuse.flush()` 确保数据上报完成；② Generation 类型的 Span 必须设置 `usage` 字段才能统计 Token 成本；③ 流式响应需要在流结束后手动更新 output 和 usage。
>
> **📝 精简总结**：Langfuse 集成有三种方式：装饰器（`@observe()`，简单自动）、手动追踪（`trace.span()`/`generation()`，灵活精细）、框架包装器（OpenAI/LangChain，便捷自动）；生产环境推荐装饰器+手动混合方式；必须注意 flush 调用、usage 设置、流式响应更新；支持环境变量配置和自部署。

---

## 四、评估与评分

### 1. 自动评分（LLM-as-Judge）

```python
from langfuse import Langfuse

langfuse = Langfuse()

def evaluate_answer(question: str, answer: str, trace_id: str):
    """使用 LLM 作为评判者自动评分"""
    # 1. LLM 评分
    eval_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """你是一个严格的答案质量评判者。
请从以下维度评分（0-1分）：
1. 准确性：答案是否正确
2. 完整性：是否覆盖问题的所有方面
3. 相关性：是否紧扣问题
4. 清晰度：表达是否清晰易懂

输出JSON格式：{"accuracy": 0.x, "completeness": 0.x, "relevance": 0.x, "clarity": 0.x, "overall": 0.x}"""},
            {"role": "user", "content": f"问题: {question}\n答案: {answer}"}
        ],
        response_format={"type": "json_object"}
    )

    import json
    scores = json.loads(eval_response.choices[0].message.content)

    # 2. 写入 Langfuse 评分
    for dimension, value in scores.items():
        langfuse.score(
            trace_id=trace_id,
            name=f"质量_{dimension}",
            value=value,
            comment="LLM自动评分"
        )

    return scores["overall"]
```

### 2. 人工评分与标注

```python
# 用户反馈接口
@app.post("/api/feedback")
async def user_feedback(trace_id: str, rating: int, comment: str = ""):
    """用户点赞/点踩反馈"""
    langfuse.score(
        trace_id=trace_id,
        name="用户满意度",
        value=rating,  # 1=点赞, 0=点踩
        comment=comment,
    )
    return {"status": "ok"}
```

### 3. 评分维度设计

| 维度 | 说明 | 评分方式 |
|------|------|---------|
| **准确性** | 答案是否正确，有无幻觉 | LLM 评判 / 人工 |
| **完整性** | 是否覆盖问题所有方面 | LLM 评判 / 人工 |
| **相关性** | 是否紧扣问题，不跑题 | LLM 评判 |
| **检索质量** | 检索到的文档是否相关 | 人工标注 / 自动评估 |
| **格式合规** | 输出是否符合指定格式 | 正则校验 / JSON Schema |
| **安全性** | 是否有有害内容 | 内容审核 API |
| **用户满意度** | 用户主观评价 | 点赞/点踩 |
| **延迟** | 响应时间 | 自动采集 |
| **成本** | Token 消耗 | 自动采集 |

---

> 💡 **深度讲解**：Langfuse 的评分系统设计非常灵活——Score 关联到 Trace（而非 Observation），可以对一次完整的用户请求进行多维度评分。评分来源可以是自动（LLM-as-Judge、规则校验、内容审核）或人工（用户反馈、运营标注）。关键设计是"多维度评分"——不是给一个总分，而是按准确性、完整性、相关性、安全性等维度分别打分，这样可以定位质量问题出在哪个维度。例如，如果准确性分数持续下降但相关性分数稳定，说明模型在"答非所问"方面没问题，但"事实正确性"在下降，可能是模型升级导致的幻觉增加。LLM-as-Judge 的实现需要注意：① 用比被评估模型更强的模型做裁判（如用 GPT-4o 评估 GPT-4o-mini 的输出）；② 设置 temperature=0 确保评分稳定；③ 建立人工标注校准集，验证裁判与人类的一致性（Cohen's Kappa）。
>
> **📝 精简总结**：Langfuse 评分系统通过 Score 关联 Trace，支持多维度评分（准确性/完整性/相关性/检索质量/格式/安全/满意度/延迟/成本）；评分来源包括自动（LLM-as-Judge/规则/审核）和人工（用户反馈/运营标注）；LLM-as-Judge 需用更强模型、temperature=0、人工校准；多维度评分可以定位质量问题的具体维度。

---

## 五、提示词管理

### 1. Langfuse Prompt Management

Langfuse 提供内置的提示词管理功能，支持版本管理、A/B 测试、线上发布：

```python
# 从 Langfuse 获取提示词（支持版本管理）
@observe()
def generate_answer(question: str, docs: list):
    # 获取最新生产版本的提示词
    prompt = langfuse.get_prompt("rag_answer_prompt")

    # 编译提示词（填充变量）
    system_prompt = prompt.compile(
        context="\n".join([d.content for d in docs]),
        question=question
    )

    response = openai.chat.completions.create(
        model=prompt.model,  # 提示词可绑定模型
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=prompt.config.get("temperature", 0.7),
    )
    return response.choices[0].message.content
```

### 2. 提示词 A/B 测试

```python
@observe()
def ab_test_answer(question: str, user_id: str):
    """提示词 A/B 测试"""
    import hashlib
    # 根据用户 ID 分流（50/50）
    bucket = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % 2

    if bucket == 0:
        prompt_name = "rag_answer_v1"  # 对照组
    else:
        prompt_name = "rag_answer_v2"  # 实验组

    prompt = langfuse.get_prompt(prompt_name)

    # 记录使用的提示词版本
    langfuse_context.update_current_trace(
        metadata={"prompt_version": prompt_name, "ab_bucket": bucket}
    )

    # 生成回答...
```

---

> 💡 **深度讲解**：Langfuse 的提示词管理将 Prompt 从代码中抽离出来，作为独立的版本化资源管理。这解决了传统 Prompt 管理的三大痛点：① 版本混乱——Prompt 散落在代码各处，修改需要发版，无法追溯历史版本；② A/B 测试困难——需要在代码中硬编码分流逻辑，无法快速切换；③ 发布风险高——Prompt 修改直接上线，无法灰度验证。Langfuse Prompt Management 支持：在面板中编辑 Prompt（支持变量占位符）、版本管理（每次修改创建新版本，可回滚）、标签管理（production/staging/dev）、A/B 测试（通过 metadata 记录版本，在面板中对比不同版本的质量评分和成本）、线上发布（将指定版本标记为 production，代码自动获取最新 production 版本）。这种"Prompt 即配置"的设计使得非工程人员（产品、运营）也可以直接修改和测试 Prompt，大大提升了迭代效率。
>
> **📝 精简总结**：Langfuse Prompt Management 将 Prompt 从代码抽离为版本化资源；支持版本管理（可回滚）、标签管理（production/staging）、A/B 测试（metadata 记录版本+面板对比）、线上发布（标记 production 自动获取）；通过 `langfuse.get_prompt()` + `prompt.compile()` 获取和编译提示词；解决了版本混乱、A/B 测试困难、发布风险高等痛点。

---

## 六、成本监控与分析

### 1. 成本仪表盘

Langfuse 自动按以下维度统计成本：
- **按模型**：每个模型的 Token 消耗和费用
- **按应用/项目**：不同应用的成本分布
- **按用户**：高成本用户识别
- **按时间**：成本趋势（日/周/月）
- **按 Trace 类型**：RAG/Agent/代码生成等

### 2. 自定义成本追踪

```python
# 自定义模型价格（Langfuse 内置主流模型价格，自定义模型需配置）
from langfuse import Langfuse

langfuse = Langfuse()

# 创建自定义模型价格配置
langfuse.create_model(
    model_name="qwen2-72b-selfhost",
    start_date="2026-01-01",
    input_price=0.0008,   # 每 1000 token
    output_price=0.002,
    unit="TOKENS",
)

# 在 Generation 中使用自定义模型
generation = trace.generation(
    name="自部署模型调用",
    model="qwen2-72b-selfhost",  # 匹配自定义价格
    input=messages,
    output=answer,
    usage={"prompt_tokens": 500, "completion_tokens": 200, "total_tokens": 700}
)
```

### 3. 成本告警

```python
# 成本监控与告警
def check_daily_cost(project_id: str, threshold: float = 100.0):
    """检查每日成本，超过阈值告警"""
    daily_cost = langfuse.get_metrics(
        project_id=project_id,
        metric_name="total_cost",
        time_range="today"
    )

    if daily_cost > threshold:
        # 发送告警（钉钉/飞书/邮件）
        send_alert(f"⚠️ 今日 AI 成本已达 ${daily_cost:.2f}，超过阈值 ${threshold}")
```

---

> 💡 **深度讲解**：Langfuse 的成本监控核心是"基于 usage 的自动计费"。每个 Generation 类型的 Observation 记录了 prompt_tokens 和 completion_tokens，Langfuse 根据内置的模型价格表自动计算费用。对于自部署模型或 Langfuse 未内置价格的模型，需要通过 `create_model` API 手动配置价格。成本分析的关键是"多维度下钻"——不是只看总成本，而是按模型、用户、Trace 类型、时间等维度下钻，找到成本异常的来源。例如，如果总成本突然上升 3 倍，按模型下钻可能发现是某个新上线的模型（context window 大）导致每轮调用的 prompt_tokens 暴增；按用户下钻可能发现是某个用户的异常请求（如无限循环调用）导致的。成本告警应该设置"相对阈值"而非"绝对阈值"——不是固定"每天超过 $100 告警"，而是"今日成本超过 7 日均值的 3 倍告警"，这样能适应业务量的自然增长。
>
> **📝 精简总结**：Langfuse 成本监控基于 Generation 的 usage 自动计费，内置主流模型价格；自定义模型需通过 `create_model` 配置价格；成本仪表盘支持按模型/应用/用户/时间/Trace类型多维度统计；关键是多维度下钻定位成本异常来源；告警建议用相对阈值（如超过7日均值3倍）而非绝对阈值。

---

## 七、自部署 Langfuse

### 1. Docker Compose 部署

```yaml
# docker-compose.yml
version: "3.8"

services:
  langfuse:
    image: langfuse/langfuse:latest
    restart: always
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://langfuse:password@postgres:5432/langfuse
      - NEXTAUTH_SECRET=your-secret-key-change-in-production
      - SALT=your-salt-change-in-production
      - NEXTAUTH_URL=http://localhost:3000
      - TELEMETRY_ENABLED=false
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:16-alpine
    restart: always
    environment:
      - POSTGRES_USER=langfuse
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=langfuse
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 启动
docker-compose up -d

## 访问 http://localhost:3000，注册管理员账号

### 2. 生产部署建议

| 组件 | 建议 |
|------|------|
| PostgreSQL | 托管数据库（RDS/Cloud SQL），至少 4C8G，开启备份 |
| Redis | 托管 Redis，用于会话和队列 |
| Langfuse | 至少 2 个实例，前置负载均衡 |
| 存储 | 对象存储（S3/OSS）用于导出和备份 |
| 监控 | 接入 Prometheus + Grafana，监控 API 延迟和错误率 |
| 备份 | 数据库每日备份，保留 30 天 |

---

> 💡 **深度讲解**：Langfuse 自部署的架构非常简洁——Next.js 应用 + PostgreSQL（主数据存储）+ Redis（会话和队列）。Docker Compose 一键部署适合开发和测试环境，但生产环境需要考虑高可用和数据安全。关键建议：① PostgreSQL 必须用托管数据库（RDS/Cloud SQL），开启自动备份和只读副本，因为 Langfuse 的所有数据（Trace、Score、Prompt 版本）都存在 PostgreSQL 中，数据库故障等于数据丢失；② Langfuse 应用至少部署 2 个实例，前置负载均衡，避免单点故障；③ 开启 S3/OSS 对象存储用于数据导出和备份，PostgreSQL 的 pg_dump 可以定期导出到对象存储；④ 监控 Langfuse 自身的 API 延迟和错误率，因为 Langfuse 故障会导致 Agent 应用的追踪数据丢失（虽然 SDK 有本地缓存和重试，但长时间不可用仍会丢数据）；⑤ 生产环境务必修改默认的 NEXTAUTH_SECRET 和 SALT，否则存在安全风险。
>
> **📝 精简总结**：Langfuse 自部署采用 Next.js + PostgreSQL + Redis 架构；Docker Compose 一键部署适合开发测试；生产环境建议托管 PostgreSQL（开启备份+只读副本）、2+ Langfuse 实例（负载均衡）、对象存储（导出备份）、监控自身 API；务必修改默认密钥（NEXTAUTH_SECRET/SALT）。

---

## 八、最佳实践

### 1. 追踪最佳实践

- [ ] **每个用户请求创建一个 Trace**，关联 user_id 和 session_id
- [ ] **LLM 调用使用 Generation 类型**，记录 model/input/output/usage
- [ ] **非 LLM 操作使用 Span**，如检索、数据库、外部 API
- [ ] **重要事件使用 Event**，如错误、用户操作
- [ ] **添加 metadata**，记录版本、环境、特征等
- [ ] **流式响应正确处理**，结束后更新 output 和 usage
- [ ] **敏感信息脱敏**，Prompt 中的密码、API Key 等不记录

### 2. 评估最佳实践

- [ ] **建立评分体系**，定义明确的评分维度和标准
- [ ] **自动+人工结合**，自动评分监控趋势，人工标注校准
- [ ] **定期审查低分 Trace**，分析原因并优化
- [ ] **A/B 测试新提示词/模型**，用数据驱动决策
- [ ] **建立质量基线**，监控质量是否下降
- [ ] **关联用户反馈**，将用户点赞/点踩与 Trace 关联

### 3. 成本优化最佳实践

- [ ] **监控成本趋势**，设置日/月预算告警
- [ ] **识别高成本 Trace**，分析是否可以优化
- [ ] **模型分级**，简单任务用小模型
- [ ] **语义缓存**，减少重复调用
- [ ] **限制 max_tokens**，避免不必要的长输出
- [ ] **定期审查**，删除未使用的高成本功能

### 4. 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Trace 不显示 | SDK 未正确初始化 / 网络不通 | 检查环境变量、网络连接、SDK 版本 |
| Token 计数不准 | 未传入 usage / 自定义模型无价格 | 确保传入 usage，配置自定义模型价格 |
| 流式响应无 output | 未在流结束后更新 | 流结束后调用 update_current_observation |
| 延迟高 | Langfuse 上报阻塞主线程 | 使用异步上报，设置采样率 |
| 数据丢失 | 进程退出时未 flush | 调用 langfuse.flush() 确保上报完成 |
| 成本显示为 0 | 模型名称不匹配价格表 | 检查模型名称，配置自定义价格 |

---

> 💡 **深度讲解**：Langfuse 生产环境最佳实践的核心是"平衡可观测性与性能/成本"。全量追踪所有请求、记录完整的 Prompt/Response、100% 采样，理论上可观测性最好，但会带来三个问题：① 性能影响——Langfuse SDK 异步上报，但大量数据仍会占用网络和 CPU；② 存储成本——完整的 Prompt/Response 可能很大（尤其是长上下文场景），存储成本随流量线性增长；③ 数据隐私——记录完整的用户输入和模型输出可能涉及敏感信息，需要合规处理。最佳实践是"差异化追踪"：① 错误 Trace 100% 全量记录（用于排查问题），正常 Trace 按 5-20% 采样（用于趋势分析）；② LLM 调用记录完整 input/output（核心调试信息），非 LLM 操作只记录耗时和元数据（不记录详细内容）；③ 敏感信息在上报前脱敏（密码、API Key、身份证号等不记录）；④ 高成本场景设置 Trace 数据保留期限（如只保留 30 天，过期自动删除）。
>
> **📝 精简总结**：追踪最佳实践包括每个请求创建 Trace、LLM 用 Generation、非 LLM 用 Span、关联 user_id/session_id、流式响应更新、敏感信息脱敏；评估最佳实践包括多维度评分、自动+人工结合、低分 Trace 审查、A/B 测试、质量基线；成本优化包括模型分级、语义缓存、限制 max_tokens；常见问题包括 Trace 不显示（初始化/网络）、Token 不准（usage/价格）、数据丢失（flush）；核心是平衡可观测性与性能/成本，采用差异化追踪策略。

---

## 🔗 关联笔记

- [[Agent评测与可观测性]] — Agent 场景的评测与可观测性实践
- [[Agent核心概念-ReAct规划]] — ReAct Agent，Langfuse 追踪的典型应用
- [[Agent记忆机制设计]] — 记忆系统，影响 Token 成本和上下文
- [[LLM接口封装与统一SDK]] — LLM API 封装，Langfuse 集成的基础
- [[AI网关与多模型路由]] — AI 网关，多模型场景的成本监控
- [[RAG架构设计与流程]] — RAG 应用，Langfuse 追踪的典型场景
- [[成本控制与Token计费]] — Token 成本控制与计费

## 📖 前置知识

- [[LLM接口封装与统一SDK]]
- [[AI网关与多模型路由]]
- [[RAG架构设计与流程]]
- [[LLM大模型入门概念]]

## 🏷️ 相关标签

`#AI应用` `#AI工程化` `#可观测性` `#效率工具`

---

[[Home|🏠 返回首页]] · [[MOC-AI与效率工具|📚 返回分类]]
