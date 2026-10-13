---
title: 实战：LLM Wiki 编译层接入
tags: [LLM Wiki, 实战, 知识编译, 接入指南, 手册]
category: 开发指导
created: 2026-10-07
updated: 2026-10-07
difficulty: ⭐⭐⭐
status: ✅ 手册
priority: P1
pre: ["[[11-LLM Wiki编译型知识库深度指南]]", "[[实战-RAG企业知识库问答系统]]"]
aliases: ["LLM Wiki 接入", "Wiki 编译层实战"]
---

# 实战：LLM Wiki 编译层接入

> [!abstract] 这份文档解决什么
> 手把手带你把「LLM Wiki 知识编译层」接入你现有的 RAG 项目，并完成功能验证。
>
> **分工说明**：
> - **AI 已完成**：所有可运行代码（后端 wiki 模块、模型、路由、前端页面）。
> - **你需要手动完成**：核对文件 → 配置环境 → 启动服务 → 按清单验证 → 完成动手实践任务。

---

## 一、AI 已完成的代码清单

请先确认以下文件都已生成（路径相对于 `产品/`）：

### 后端（backend/）

| 文件 | 作用 |
| --- | --- |
| `app/models/wiki_page.py` | WikiPage 数据模型 |
| `app/wiki/__init__.py` | 模块导出 |
| `app/wiki/compiler.py` | 编译引擎（协调器） |
| `app/wiki/entity_extractor.py` | 实体抽取 |
| `app/wiki/page_manager.py` | 页面生成/更新/版本 |
| `app/wiki/conflict_detector.py` | 冲突检测 |
| `app/wiki/linker.py` | 双向链接维护 |
| `app/wiki/wiki_retriever.py` | 查询时 Wiki 检索 |
| `app/routers/wiki.py` | Wiki API 路由 |
| `app/schemas/wiki.py` | Pydantic schemas |
| `scripts/migrate_wiki.py` | 表迁移脚本 |

### 已修改的后端文件

| 文件 | 改动 |
| --- | --- |
| `app/models/__init__.py` | 注册 WikiPage |
| `app/schemas/__init__.py` | 注册 wiki schemas |
| `app/routers/__init__.py` | 注册 wiki 路由 |
| `app/config.py` | 新增 Wiki 配置项 |
| `app/services/document_service.py` | 文档处理完自动触发编译 |
| `app/services/rag_service.py` | 查询时 Wiki 增强 |
| `app/services/vector_store.py` | 新增按文档取 chunk 方法 |

### 前端（frontend/）

| 文件 | 作用 |
| --- | --- |
| `src/api/wiki.ts` | Wiki API 封装 |
| `src/views/Wiki.vue` | Wiki 页面（列表/详情/图谱） |

### 已修改的前端文件

| 文件 | 改动 |
| --- | --- |
| `src/router/index.ts` | 新增 `/wiki` 路由 |
| `src/views/Layout.vue` | 侧边栏新增「知识维基」入口 |

---

## 二、你需要手动完成的步骤

### 步骤 1：核对文件（5 分钟）

对照上面的清单，确认文件齐全。重点确认：

- `app/wiki/` 目录下有 7 个 `.py` 文件（含 `__init__.py`）。
- `app/routers/wiki.py` 已存在。
- 前端 `src/views/Wiki.vue` 已存在。

### 步骤 2：（可选）手动建表

> 正常情况下，后端启动时 `main.py` 的 `Base.metadata.create_all()` 会**自动创建** `wiki_pages` 表，无需手动操作。
> 只有当你用的是**已有数据库且启动后没看到表**时，才执行：

```bash
cd backend
# 激活虚拟环境后
python -m scripts.migrate_wiki
```

看到 `✅ 迁移完成：wiki_pages 表已创建` 即可。

### 步骤 3：确认配置

打开 `backend/.env`，确认已配置好 LLM（Wiki 编译复用同一套 LLM 配置）：

```ini
LLM_API_KEY=你的key
LLM_BASE_URL=你的接口地址
LLM_MODEL=你的对话模型
EMBEDDING_MODEL=你的向量模型
```

Wiki 相关配置有默认值，**无需额外配置**即可运行。如需调整，可在 `.env` 中覆盖：

```ini
# 关闭自动编译（批量导入时用）
WIKI_AUTO_COMPILE=false
# 单文档最多抽取实体数
WIKI_MAX_ENTITIES_PER_DOC=15
# 关闭查询时 Wiki 增强
WIKI_RETRIEVAL_ENABLED=true
```

### 步骤 4：启动服务

```bash
# 终端1：后端
cd backend
uvicorn app.main:app --reload --port 8000

# 终端2：前端
cd frontend
npm run dev
```

### 步骤 5：功能验证

按下面的验收清单逐项验证。

---

## 三、功能验收清单

### 3.1 自动编译验证

- [ ] 新建一个知识库。
- [ ] 上传第一篇文档（建议内容主题明确，如一篇讲 RAG 的 Markdown）。
- [ ] 文档状态变为「已完成」后，等待约 30 秒～1 分钟。
- [ ] 进入「知识维基」页，选择该知识库，**能看到自动生成的页面**。
- [ ] 页面包含：标题、类型标签、结构化正文、来源文档。

### 3.2 增量更新验证

- [ ] 上传第二篇与第一篇**主题相关**的文档。
- [ ] 编译完成后，观察：
  - 重叠的实体**没有被建成重复页面**，而是原页面版本号 +1。
  - 页面「来源文档」包含多个文档 ID。

### 3.3 冲突检测验证

- [ ] 上传第三篇文档，**故意写一个与前两篇矛盾的事实**（例如同一参数写不同数值）。
- [ ] 对应页面顶部出现**红色冲突警告**，说明冲突详情。
- [ ] 页面列表中该页面标题旁出现红色警告图标。

### 3.4 关系图谱验证

- [ ] 切换到「关系图谱」视图。
- [ ] 能看到节点（页面）和连线（双向链接）。
- [ ] 不同实体类型的节点颜色不同。
- [ ] 点击某个节点，跳转回列表视图并打开该页面。

### 3.5 查询增强验证

- [ ] 进入「智能问答」，选择该知识库。
- [ ] 问一个**全局理解型**问题，如：「XXX 和 YYY 的区别是什么？」
- [ ] 答案结构完整、表述一致。
- [ ] （进阶）查看后端日志，确认该问题走了 Wiki 检索。
- [ ] 问一个**纯事实型**问题，确认直接走 chunk、不触发 Wiki。

### 3.6 页面管理验证

- [ ] 删除一个 Wiki 页面，列表中消失。
- [ ] 其他页面的关联中不再出现指向它的悬空链接。
- [ ] 点击「重新编译」，可重新生成页面。

---

## 四、动手实践任务（学习部分）

> 这些是**你必须自己动手**的部分，用来确保你真正理解、而不只是"代码能跑"。

### 任务 A：脱稿画架构图（必做）

不看代码，用纸笔或白板画出两张图：
1. **写入链路**：文档上传 → 切块 → 向量化 → Wiki 编译（四动作）。
2. **查询链路**：问题 → 路由 →（Wiki 检索 / 混合检索）→ 上下文拼接 → 生成。

画完后对照代码检查，漏了哪些环节。

### 任务 B：观察编译过程（必做）

1. 开启后端日志，上传一篇文档。
2. 观察日志中编译的完整过程：抽取了几个实体、新建/更新了几个页面。
3. 记录从上传到 Wiki 页面出现的总耗时，理解"为什么编译要放后台"。

### 任务 C：制造并观察冲突（必做）

按 3.3 节制造一个冲突，观察：
- 冲突标记的完整结构。
- 尝试写一个"只是补充信息、并不矛盾"的文档，确认**不会**误报冲突。

### 任务 D：新增一种实体类型（进阶）

1. 修改 `entity_extractor.py` 的 prompt，增加一种类型（如 `metric` 指标）。
2. 在 `Wiki.vue` 的 `entityTypes` 和 `graphColors` 中补全。
3. 上传含该类实体的文档，验证类型筛选和图谱着色。

### 任务 E：评测驱动验证（进阶）

1. 用 `app/evaluation/` 体系，为全局理解型问题设计 10 条 golden QA。
2. 分别在开启/关闭 `WIKI_RETRIEVAL_ENABLED` 下跑评测。
3. 对比 faithfulness / 完整性，记录数据。

---

## 五、常见问题排查

### 上传后 Wiki 页面一直不出现

- 等待 30 秒～1 分钟（编译是异步的，且实体越多越慢）。
- 查看后端日志是否有 `Wiki 编译失败` 或 `同步 LLM 调用失败`。
- 确认 `LLM_API_KEY` 有余额、`LLM_MODEL` 正确。
- 确认 `.env` 里 `WIKI_ENABLED` 和 `WIKI_AUTO_COMPILE` 没被设为 false。

### 页面生成了但内容为空/很短

- 可能是文档 chunk 太少或内容太稀疏。
- 检查 `max_tokens` 是否限制过小（编译 prompt 默认 2000）。
- 尝试点「重新编译」。

### 冲突没有被检测到

- 系统刻意"不确定判无冲突"，轻微措辞差异不会报。
- 确保两份文档对**同一事实**给出了**明确互斥**的说法。
- 可适当调整 `conflict_detector.py` 的 prompt 提高敏感度（但会增加误报）。

### 图谱没有连线

- 连线来自页面正文里的 `[[]]` 链接。
- 确认页面生成时 LLM 确实写了 `[[相关概念]]`。
- 确认 `linker` 能把链接名匹配到实际页面（名称需一致）。

### 前端 Wiki 页报错 / 图表不显示

- 确认已 `npm install`（`echarts`、`vue-echarts`、`markdown-it` 已在依赖中）。
- 重启前端 dev 服务。
- 查看浏览器控制台具体错误。

### 重新编译后页面重复

- 通常是实体名不一致导致。检查 `entity_extractor` 输出的名称是否规范。
- 删除重复页面后重新编译。

---

## 六、接入完成的标志

- [ ] 文档上传后能自动生成结构化 Wiki 页面。
- [ ] 相关文档能增量更新页面、不重复建页。
- [ ] 矛盾事实能被检测并醒目提示。
- [ ] 关系图谱正常展示。
- [ ] 全局理解型问题能走 Wiki 增强。
- [ ] 你能脱稿讲清整个架构和设计取舍。

---

## 七、关联

- 原理深度讲解：[[11-LLM Wiki编译型知识库深度指南]]
- 项目主实战：[[实战-RAG企业知识库问答系统]]
- 启动指南：[[本地启动指南]]
- 评测体系：[[01-RAG评测体系深度指南]]
- 上下文工程：[[03-上下文工程深度指南]]
