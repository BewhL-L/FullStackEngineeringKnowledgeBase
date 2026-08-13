---
title: AI工程化技术枢纽
tags: [枢纽, AI工程, hub]
created: 2026-08-13
updated: 2026-08-13
hub: true
hub_type: 技术枢纽
---

# 🤖 AI 工程化技术枢纽

> 大模型应用工程化的核心节点，连接 LLM 原理、RAG、Agent 框架、向量数据库、模型部署与应用工程化。
> **所属板块**：[[06-AI工程化/MOC-AI工程化-四级展开|AI工程化]]
> **标签前缀**：`#AI工程/`

---

## 📌 枢纽定位

| 维度 | 说明 |
|------|------|
| 定位 | LLM 应用从原理到生产的知识汇聚点 |
| 覆盖范围 | LLM原理 → RAG → Agent → 向量库 → 模型部署 → 工程化 |
| 上游依赖 | [[Python-全栈技术枢纽|Python全栈]]、[[CS-基础原理枢纽|CS基础]] |
| 下游延伸 | [[项目实战-枢纽|项目实战]]、[[AIGC-Obsidian-应用枢纽|AIGC应用]] |
| 核心能力 | 构建生产级 LLM 应用（RAG/Agent/模型服务） |

---

## 🔑 核心知识节点

### 第一层：必须掌握

- [[Transformer架构核心|Transformer 架构]] — 大模型基础
- [[RAG架构设计与流程|RAG 架构设计]] — 私有知识问答标准方案
- [[LangChain-核心抽象与链|LangChain]] — 最流行的 LLM 应用框架
- [[Embedding模型选型|Embedding 模型]] — 向量化质量关键

### 第二层：深入理解

- [[LangGraph-状态机Agent|LangGraph]] — 可控 Agent 编排
- [[Milvus-架构与部署|Milvus]] — 向量数据库标杆
- [[vLLM-高吞吐推理引擎|vLLM]] — 高吞吐推理引擎
- [[高级RAG-Hybrid检索与重排序|高级 RAG]] — 混合检索与重排序

### 第三层：拓展延伸

- [[Dify-低代码AI应用平台|Dify]] — 低代码 AI 应用平台
- [[模型量化-GPTQ-AWQ-GGUF|模型量化]] — 显存优化
- [[AI应用可观测性-Langfuse|可观测性]] — Langfuse 监控
- [[AI网关与多模型路由|AI 网关]] — 多模型统一接入

---

## 🕸️ 知识网络

```
LLM原理（Transformer）
    │
    ├── RAG
    │     ├── 分块策略
    │     ├── Embedding
    │     ├── 向量库（Milvus/PgVector）
    │     └── 高级RAG（Hybrid/Rerank/GraphRAG）
    │
    ├── Agent
    │     ├── LangChain
    │     ├── LangGraph
    │     ├── LlamaIndex
    │     └── AutoGen / Dify
    │
    ├── 模型部署
    │     ├── vLLM
    │     ├── Ollama
    │     └── 量化（GPTQ/AWQ/GGUF）
    │
    └── 工程化
          ├── 统一SDK
          ├── 可观测性（Langfuse）
          ├── AI网关
          └── 成本控制
```

---

## 🔗 上下游横向关联

### 入向依赖
- [[Python-全栈技术枢纽|Python全栈]] — AI 开发主语言
- [[CS-基础原理枢纽|CS基础]] — 神经网络、GPU 计算

### 出向延伸
- [[项目实战-枢纽|项目实战]] — RAG 系统、Agent 应用
- [[Vue3TS-前端技术枢纽|Vue3TS前端]] — AI 产品前端交互
- [[Java-全栈技术枢纽|Java全栈]] — Spring AI 集成

---

## 🌐 跨板块枢纽连接

| 连接枢纽 | 关联点 | 关键笔记 |
|----------|--------|----------|
| [[Python-全栈技术枢纽|Python全栈]] | FastAPI 封装模型服务 | [[LLM接口封装与统一SDK]] |
| [[Java-全栈技术枢纽|Java全栈]] | Spring AI / LangChain4j | [[SpringAI-框架入门与模型抽象]] |
| [[Vue3TS-前端技术枢纽|Vue3TS前端]] | SSE 流式输出前端展示 | [[SSE-流式响应对接LLM]] |
| [[DevOps-工程化枢纽|DevOps]] | GPU 服务器、模型服务容器化 | [[模型服务化-OpenAI兼容API]] |
| [[AIGC-Obsidian-应用枢纽|AIGC应用]] | 从工具使用到深度开发 | [[Agent核心概念-ReAct规划]] |

---

## 📝 维护日志

| 日期 | 变更 |
|------|------|
| 2026-08-13 | 初始创建 |

---

## ⚠️ 知识边界

- AI 工具的简单使用归入 [[AIGC-Obsidian-应用枢纽|AIGC应用]]
- 模型训练（预训练/SFT/RLHF）仅做原理了解，不深入训练工程
- 传统机器学习（非 LLM）暂不包含

---

[[10-四级知识框架/00-总控/四级框架总索引|← 返回四级框架总索引]] | [[06-AI工程化/MOC-AI工程化-四级展开|📂 返回板块MOC]] | [[Home|🏠 返回首页]]
