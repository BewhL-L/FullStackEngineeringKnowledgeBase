# 企业智能知识库助手 · AI Agent + RAG 全栈平台

> 基于 RAG 检索增强生成和 Function Calling 的企业级智能知识库系统，支持文档上传、智能问答、多轮对话、来源引用、AI Agent 工具调用、SSE 流式输出，并内置**混合检索、上下文工程、RAG 评测体系、MCP / A2A 协议、Agent 编排、可观测性**等生产级能力。

## 项目简介

这是一个完整的 **AI 全栈项目**，把企业的 PDF / Word / TXT 文档构建成向量知识库，员工用自然语言提问，系统自动检索相关内容并由大模型生成带来源的回答。还内置了 AI Agent，能自动调用工具（查时间、数学计算等）。

**两套业务包装（一套代码，两地通吃）：**
- 投杭州电商公司：电商客服知识库 + 商品问答助手
- 投上海企业服务公司：企业内部知识管理 + 智能助手平台

## 技术栈

| 分层 | 技术 |
|------|------|
| 前端 | Vue3 + TypeScript + Vite + Element Plus（按需）+ Pinia + Vue Router |
| 后端 | Python + FastAPI + SQLAlchemy + Pydantic v2 |
| 数据库 | SQLite（开发）/ 可切换 PostgreSQL |
| 向量库 | Chroma DB |
| 检索 | 向量检索 + BM25 关键词检索（混合，RRF 融合 + Rerank 重排 + 查询改写） |
| AI 能力 | LLM（OpenAI 兼容接口，支持豆包/通义/DeepSeek）+ Embedding |
| Agent | 原生 ReAct 循环；可选 LangGraph（ReAct / Plan-and-Execute / 多智能体） |
| 协议 | MCP（stdio / HTTP）、A2A（JSON-RPC） |
| 评测 | 确定性检索/生成指标 + LLM 裁判 + 可选 RAGAS |
| 可观测 | 可选 Langfuse（trace / span / 延迟） |
| 核心技术 | RAG / Agentic RAG、Function Calling、SSE 流式、JWT、限流、缓存、Prompt 注入防护 |
| 部署 | Docker + docker-compose + Nginx；可选 Redis + Celery 异步任务 |
| 可视化 | ECharts（按需引入） |

## 核心功能

**基础能力**
- 用户注册登录、JWT 鉴权、bcrypt 密码加密、多租户行级数据隔离
- 知识库创建、删除、编辑（多知识库隔离）
- 文档上传（PDF/Word/TXT/MD），后台异步解析、切片、向量化
- 文档增量更新（同 ID 替换，自动删除旧向量并重建）
- 朴素 RAG 问答 + 来源引用 + 相似度展示
- Agentic RAG：Agent 自主决定是否检索、检索什么、资料不足自动换关键词重查
- SSE 流式输出（含 Agent“正在检索/计算”状态）
- 多轮对话、历史管理、消息复制、重新生成、Markdown 渲染 + 代码高亮
- 回答点赞 / 点踩反馈
- 数据统计看板（问答趋势、文档分布，ECharts）
- 网站嵌入：公开免登录问答窗口，iframe 可直接嵌入外部网站
- 多模型切换：按用户选择的模型真正生效

**生产级高级能力（详见 `docs/高级能力与可选依赖.md`）**
- **混合检索**：向量 + 自研 BM25（jieba 分词，缺依赖自动降级），RRF 融合、LLM/Cohere Rerank、Multi-Query 查询改写、HyDE
- **上下文工程**：短期滑动窗口记忆、长期事实记忆、历史 LLM 压缩、Token 预算裁剪、工具数量预算
- **RAG 评测体系**：golden QA 数据集、Hit@K / MRR / Context Precision/Recall / 关键词覆盖、LLM 忠实度与相关性裁判、RAGAS 对接、一键跑分与报告
- **MCP Server**：把知识库检索/问答暴露为 MCP 工具（stdio / streamable-http），可被 Claude Desktop、IDE 等接入
- **Agent 编排**：LangGraph 版 ReAct、Plan-and-Execute、Supervisor 多智能体（可选切换）
- **可观测性**：Langfuse 全链路 trace（检索 span + 生成 + 延迟）
- **A2A 协议**：Agent Card + JSON-RPC，支持 Agent 间互操作
- **多模态解析**：图片 OCR、VLM 图像描述、PDF 表格抽取
- **微调示例**：golden QA → jsonl → OpenAI 兼容微调脚本，附 RAG/微调选型文档
- **安全防护**：Prompt 注入启发式检测、检索资料边界包裹、危险工具 AST 白名单
- **生产化**：Redis 缓存、Celery 异步任务、PostgreSQL 切换、GitHub Actions CI

## 目录结构

```
产品/
├── backend/
│   ├── app/
│   │   ├── main.py            # 应用入口
│   │   ├── config.py          # 配置（含检索/上下文/评测/编排等开关）
│   │   ├── database.py        # 数据库连接
│   │   ├── models/ schemas/ routers/
│   │   ├── services/          # LLM / RAG / 向量库 / Agent / 文档 / 缓存
│   │   ├── retrieval/         # 混合检索：BM25 / 查询改写 / Rerank / RRF
│   │   ├── context_engine/    # 上下文工程：记忆 / 压缩 / 组装
│   │   ├── evaluation/        # 评测：golden QA / 指标 / LLM 裁判 / RAGAS
│   │   ├── mcp_server/        # MCP Server（stdio / http）
│   │   ├── orchestration/     # LangGraph：ReAct / Plan-Execute / 多智能体
│   │   ├── observability/     # Langfuse 追踪
│   │   ├── protocols/         # A2A Server
│   │   ├── multimodal/        # OCR / VLM / 表格抽取
│   │   ├── tasks/             # Celery 异步任务
│   │   └── utils/             # 安全工具、注入防护、依赖
│   ├── scripts/finetune/      # 微调数据准备与训练脚本
│   ├── tests/                 # pytest（47 个用例）
│   └── requirements.txt
├── frontend/
│   ├── src/（api / stores / router / views / assets）
│   └── package.json
├── .github/workflows/ci.yml   # CI：后端 pytest + 前端 build
├── docker/                    # 部署参考配置
├── docs/                      # 文档（API、部署、面试、高级能力）
└── docker-compose.yml
```

## 快速开始（本地开发）

### 后端

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt

# 配置环境变量
copy .env.example .env   # 编辑 .env，填入 LLM_API_KEY

# 启动
uvicorn app.main:app --reload --port 8000
```

访问 API 文档（Swagger）：http://localhost:8000/docs

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173 （已配置代理转发 /api 到后端）。

### Docker 一键部署

```bash
docker-compose up -d --build
```

## 评测驱动（本项目的核心方法论）

```bash
cd backend
# 跑 golden QA 评测（检索 + 生成指标 + LLM 裁判）
python -m app.evaluation.run_eval
# 或通过接口：POST /api/evaluation/run，GET /api/evaluation/latest
```

每做一次检索 / Prompt / 模型优化，都先用评测跑出量化指标，形成 **「发现问题 → 定位到层 → 优化 → 指标提升」** 的闭环。

## 学习提示

- 主干：`backend/app/services/`（rag_service / vector_store / agent_service）
- 进阶：`retrieval/`、`context_engine/`、`evaluation/` 三个包是面试差异化重点
- 前端流式：`src/api/chat.ts`（fetch + ReadableStream）
- 各可选模块如何启用见 `docs/高级能力与可选依赖.md`
- 面试问题与简历话术见 `docs/面试材料.md`

## License

MIT
