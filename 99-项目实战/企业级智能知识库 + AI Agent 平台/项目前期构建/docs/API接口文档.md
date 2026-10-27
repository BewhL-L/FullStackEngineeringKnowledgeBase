# API 接口文档

- 基础路径：`/api`（例外：`/embed/*` 与 `/a2a/*` 不带 `/api` 前缀）
- 认证：除注册/登录、嵌入页、A2A 外，请求头带 `Authorization: Bearer <token>`
- Token 有效期：`ACCESS_TOKEN_EXPIRE_MINUTES`（默认 7 天），无 refresh token
- 交互式文档：启动后访问 `/docs`（Swagger），本文档与之保持一致

---

## 一、认证 `/api/auth`

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /auth/register | 注册，body `{username, password, email?}`，成功直接返回 token |
| POST | /auth/login | 登录，body `{username, password}` |
| GET | /auth/me | 当前用户 |
| PUT | /auth/password | 改密，body `{old_password, new_password}` |
| PUT | /auth/model | 切换模型，body `{model}` |

响应（register / login）：

```json
{
  "access_token": "xxx",
  "token_type": "bearer",
  "user": { "id": 1, "username": "test", "email": "a@b.com", "role": "editor" }
}
```

> `role` 是**系统级**角色（admin/editor/viewer），与知识库内的 owner/editor/viewer 是两套，别混。

---

## 二、知识库与协作 `/api/kb`

| 方法 | 路径 | 所需库内角色 | 说明 |
|---|---|---|---|
| POST | /kb | — | 创建，body `{name, description}` |
| GET | /kb | 登录即可 | 列表：**我创建的 + 共享给我的**，query `page/page_size/keyword` |
| GET | /kb/{id} | viewer | 详情 |
| PUT | /kb/{id} | editor | 改名/描述 |
| DELETE | /kb/{id} | owner | 删库（级联文档/向量/成员） |
| GET | /kb/{id}/embed-code | owner | 嵌入代码（泄露即公开，仅 owner） |

知识库响应新增 `role` 字段（当前用户在该库的角色），前端据此控制按钮显隐：

```json
{
  "id": 1, "name": "客服知识库", "description": "",
  "embed_code": "a1b2c3", "document_count": 8,
  "role": "editor",
  "created_at": "...", "updated_at": "..."
}
```

### 成员管理（RBAC）

| 方法 | 路径 | 所需角色 | 说明 |
|---|---|---|---|
| GET | /kb/{id}/members | viewer | 成员列表（含 owner 虚拟行）+ `my_role` |
| POST | /kb/{id}/members | owner | 邀请，body `{username, role}`，role ∈ editor/viewer |
| DELETE | /kb/{id}/members/{member_id} | owner | 移除 |

```json
{
  "items": [
    { "id": null, "user_id": 1, "username": "owner",  "role": "owner",  "is_owner": true },
    { "id": 7,    "user_id": 9, "username": "同事",   "role": "editor", "is_owner": false }
  ],
  "my_role": "owner"
}
```

> `owner` 不写入 `kb_members` 表，由 `knowledge_bases.user_id` 体现，所以 `id` 为 `null`。
> 权限判定：读=viewer，写=editor，邀请/删库/嵌入码=owner。

---

## 三、文档 `/api`

| 方法 | 路径 | 所需角色 | 说明 |
|---|---|---|---|
| POST | /kb/{id}/upload | editor | 上传（multipart，字段 `file`），异步处理 |
| PUT | /docs/{id} | editor | 增量更新（同 ID 替换，先删旧向量再重建） |
| GET | /kb/{id}/docs | viewer | 文档列表（分页） |
| GET | /docs/{id} | viewer | 处理状态 |
| GET | /docs/{id}/preview | viewer | 预览：文本类返回解析内容，PDF 返回 `file_url` |
| DELETE | /docs/{id} | editor | 删除（同步删向量与 Wiki 引用） |

`status`：`processing` / `completed` / `failed`。上传后走 解析 → 切片 → Embedding → 入库，前端轮询 `GET /docs/{id}`。

---

## 四、问答 `/api`

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /chat | 普通问答（非流式） |
| POST | /chat/reasoning | 推理模型问答，返回 `reasoning` 思考链 |
| POST | /chat/stream | SSE 流式 |
| POST | /chat/global | 跨知识库问答，body `{question, kb_ids?}` |
| POST | /feedback | 点赞/点踩，body `{message_id, feedback}` |

### POST /chat

```json
{ "kb_id": 1, "question": "退货政策是什么？", "conversation_id": 1, "use_agent": false }
```

```json
{
  "conversation_id": 1,
  "answer": "根据资料……",
  "sources": [{ "document_name": "售后政策.pdf", "text": "...", "score": 0.89 }],
  "grounding": {
    "checked": true,
    "coverage": 0.75,
    "threshold": 0.3,
    "supported": ["……"],
    "unsupported": ["……"],
    "citations": [{ "sentence": "……", "score": 0.82, "source_index": 0 }],
    "low_coverage": false
  },
  "message_id": 12
}
```

> `grounding` 是**句子级溯源校验**：`coverage` = 有依据的句子占比；`unsupported` 列出没有依据的句子。
> 没有检索结果时 `checked=false`、`coverage=null`——此时不代表幻觉，只是没资料可对。
> 它用字符二元组对齐，零成本可复现；对大幅改写的句子偏保守，所以是**提示**不是**判决**。

### POST /chat/stream

`text/event-stream`，每条 `data:` 为 JSON：

- 状态：`{"status": "正在检索知识库…"}`
- 增量：`{"token": "你"}`
- 结束：`{"done": true, "conversation_id": 1, "message_id": 12, "sources": [...]}`
- 错误：`{"error": "..."}`

> 流式不返回 `grounding`（答案还没生成完，无法逐句校验）。

---

## 五、对话历史 `/api/conversations`

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /conversations | 创建，body `{kb_id, title}` |
| GET | /conversations | 列表，可 `kb_id` 筛选 |
| GET | /conversations/{id} | 详情（含消息） |
| PUT | /conversations/{id} | 改标题 |
| DELETE | /conversations/{id} | 删除（级联消息） |

---

## 六、AI Agent `/api/agent`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /agent/tools | 可用工具列表 |
| POST | /agent/chat | 单 Agent 工具调用，body `{question, history, kb_id?}` |
| POST | /agent/multi-agent | 多 Agent 状态机，body `{question, kb_id, backend}` |

`multi-agent` 返回 `steps`（planner / researcher / writer / supervisor），前端时间线数据来源：

```json
{
  "answer": "...",
  "sources": [],
  "steps": [{ "agent": "planner", "title": "规划任务", "output": ["子问题1"] }],
  "backend": "native-multi-agent"
}
```

---

## 七、知识编译与图谱

### LLM Wiki `/api/wiki`

| 方法 | 路径 | 所需角色 | 说明 |
|---|---|---|---|
| GET | /kb/{kb_id}/pages | viewer | 页面列表，可 `entity_type` / `keyword` 筛选 |
| POST | /kb/{kb_id}/recompile | editor | 重编译，query `wait=true` 可同步等待 |
| GET | /kb/{kb_id}/graph | viewer | 页面关联图（节点+边） |
| GET | /pages/{page_id} | viewer | 页面详情 |
| PUT | /pages/{page_id} | editor | 人工编辑（自动存历史版本） |
| GET | /pages/{page_id}/versions | viewer | 历史版本 |
| POST | /pages/{page_id}/rollback/{version_id} | editor | 回滚 |
| DELETE | /pages/{page_id} | editor | 删除页面 |

### GraphRAG `/api/graphrag`

| 方法 | 路径 | 所需角色 | 说明 |
|---|---|---|---|
| POST | /kb/{kb_id}/build | editor | 构建图谱（后台线程），body `{doc_ids?}` |
| GET | /kb/{kb_id}/status | viewer | 构建状态 |
| GET | /kb/{kb_id}/graph | viewer | 节点与边（可视化） |
| POST | /kb/{kb_id}/local | viewer | 局部检索（实体→邻居→子图） |
| POST | /kb/{kb_id}/global | viewer | 全局检索（社区 map-reduce） |

> `GRAPHRAG_ENABLED=false` 时，build/local/global 返回 **503**。
> 注意：图谱是**独立能力**，没有接入 `/api/chat` 的主检索链路。

---

## 八、结构化回答 `/api/structured`

### POST /structured/generate

```json
{ "question": "对比 A 和 B", "template": "comparison", "kb_id": 1 }
```

`template` ∈ `bullets` / `comparison` / `timeline`；传 `kb_id` 时先检索再生成。

```json
{
  "template": "comparison",
  "result": { "title": "...", "headers": ["维度","A","B"], "rows": [["价格","12","18"]] },
  "raw": "模型原始输出",
  "degraded": false
}
```

> 模型没返回合法 JSON 时 `degraded=true`，`result` 会被降级成 `bullets` 结构，**接口始终 200**。

---

## 九、统计与评测

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /stats | 看板：概览、周趋势、知识库分布 |
| GET | /stats/cost | LLM 用量与费用（按模型/用途聚合） |
| GET | /stats/active-learning | 负反馈归因与优化建议 |
| POST | /evaluation/run | 跑评测，body `{kb_id?, use_judge?}` |
| GET | /evaluation/latest | 最近一次报告 |

评测汇总字段（与代码一致）：

```json
{
  "summary": {
    "hit@k": 0.9, "mrr": 0.85,
    "context_precision": 0.8, "context_recall": 0.75,
    "answer_keyword_coverage": 0.88,
    "citation_coverage": 0.72,
    "faithfulness": 0.95, "answer_relevancy": 0.9,
    "refusal_recall": 0.8, "false_refusal_rate": 0.05,
    "case_count": 20, "avg_latency_s": 1.8,
    "should_refuse_cases": 2, "refused_cases": 3
  },
  "cases": []
}
```

CLI：`python -m app.evaluation.run_eval [--kb-id N] [--no-judge]`

---

## 十、微调数据 `/api/finetune`

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /finetune/export | 导出 golden QA 为 jsonl（需 editor） |
| POST | /finetune/preview | 预览导出内容 |

---

## 十一、公开接口（不带 `/api`）

### 网站嵌入

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /embed/{code} | 自包含聊天页（供 iframe） |
| POST | /embed/{code}/chat | 匿名问答，body `{question, history}` |

嵌入码为 16 位随机串，泄露即等于把该库对外公开——这也是为什么只有 owner 能查看。

### A2A（默认关闭）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /a2a/.well-known/agent.json | Agent Card（`A2A_ENABLED=false` 时 404） |
| POST | /a2a/ | JSON-RPC，`message/send`；需 `Authorization: Bearer <A2A_TOKEN>` |

未配置 `A2A_TOKEN` 时一律 503；`kb_id` 必须显式放在 `message.metadata.kb_id`，不再默认取 1 号库。

---

## 通用错误格式

| 状态码 | 含义 |
|---|---|
| 400 | 参数错误 / 业务校验失败 |
| 401 | 未登录或 Token 过期 |
| 403 | 无权访问（库内角色不足） |
| 404 | 资源不存在 |
| 429 | 触发限流（`Retry-After` 头给出等待秒数） |
| 503 | 能力被配置关闭（如 GraphRAG / A2A） |

错误体：`{ "detail": "错误描述" }`
