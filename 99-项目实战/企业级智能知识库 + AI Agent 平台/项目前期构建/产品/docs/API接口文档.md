# API 接口文档

基础路径：`/api`
认证方式：除注册登录外，请求头携带 `Authorization: Bearer <token>`

---

## 一、认证模块

### POST /auth/register
用户注册，注册成功直接返回 Token。

请求体：
```json
{ "username": "test", "password": "123456", "email": "test@example.com" }
```

### POST /auth/login
用户登录。

请求体：
```json
{ "username": "test", "password": "123456" }
```

响应：
```json
{
  "access_token": "xxx",
  "token_type": "bearer",
  "user": { "id": 1, "username": "test", "email": "..." }
}
```

### GET /auth/me
获取当前登录用户信息。

### PUT /auth/password
修改密码。请求体：`{ "old_password": "", "new_password": "" }`

### PUT /auth/model
切换当前使用的模型。请求体：`{ "model": "模型名" }`

---

## 二、知识库模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /kb | 创建知识库，body：`{ name, description }` |
| GET | /kb | 列表，query：`page`、`page_size`、`keyword` |
| GET | /kb/{id} | 知识库详情 |
| PUT | /kb/{id} | 更新名称/描述 |
| DELETE | /kb/{id} | 删除（级联删除文档、向量） |
| GET | /kb/{id}/embed-code | 获取嵌入代码 |

---

## 三、文档模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /kb/{id}/upload | 上传文档（multipart/form-data，字段名 file） |
| GET | /kb/{id}/docs | 文档列表，分页 |
| GET | /docs/{id} | 查询文档处理状态 |
| DELETE | /docs/{id} | 删除文档（同步删向量） |

文档状态 status：`processing`（处理中）/ `completed`（完成）/ `failed`（失败）

上传后后台异步执行：解析 → 切片 → Embedding → 入库，前端可轮询状态。

---

## 四、智能问答模块

### POST /chat
普通问答（非流式）。

请求体：
```json
{
  "kb_id": 1,
  "question": "退货政策是什么？",
  "conversation_id": 1,
  "use_agent": false
}
```

响应：
```json
{
  "conversation_id": 1,
  "answer": "根据资料...",
  "sources": [
    { "document_name": "售后政策.pdf", "text": "...", "score": 0.89 }
  ],
  "message_id": 12
}
```

### POST /chat/stream
流式问答（SSE）。返回 `text/event-stream`，每条 `data:` 为 JSON：

- 增量 Token：`{"token": "你"}`
- 结束标记：`{"done": true, "conversation_id": 1, "message_id": 12, "sources": [...]}`
- 错误：`{"error": "错误信息"}`

### POST /feedback
回答点赞/点踩：`{ "message_id": 12, "feedback": 1, "comment": "" }`
feedback：1 点赞，-1 点踩。

---

## 五、对话历史模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /conversations | 创建对话，body：`{ kb_id, title }` |
| GET | /conversations | 列表，可按 `kb_id` 筛选 |
| GET | /conversations/{id} | 对话详情（含全部消息） |
| PUT | /conversations/{id} | 更新标题 |
| DELETE | /conversations/{id} | 删除对话（级联删除消息） |

---

## 六、AI Agent 模块

### GET /agent/tools
获取 Agent 可用工具列表。

### POST /agent/chat
Agent 对话（自动工具调用）。

请求体：
```json
{ "question": "现在几点了？", "history": [] }
```

模型会根据问题自动决定是否调用 `get_current_time`、`calculator` 等工具。

---

## 七、统计模块

### GET /stats
返回数据看板：
```json
{
  "overview": {
    "kb_count": 3,
    "doc_count": 15,
    "conversation_count": 8,
    "qa_count": 42
  },
  "weekly_trend": [{ "date": "2026-09-13", "count": 5 }],
  "kb_distribution": [{ "name": "客服知识库", "doc_count": 8 }]
}
```

---

## 八、评测模块

### POST /evaluation/run
触发对 golden QA 数据集的评测（检索 + 生成 + LLM 裁判）。
- 请求体（可选）：`{ "kb_id": 1, "use_judge": true }`
- 逐用例执行检索、检索指标、生成、生成指标与 LLM 裁判，返回汇总报告。

### GET /evaluation/latest
获取最近一次评测报告（`latest.json`），核心字段：
```json
{
  "summary": {
    "hit_at_k": 0.9,
    "mrr": 0.85,
    "context_precision": 0.8,
    "context_recall": 0.75,
    "answer_keyword_coverage": 0.88,
    "judge_faithfulness": 0.95,
    "judge_relevancy": 0.9
  },
  "cases": []
}
```

> 也可用 CLI：`python -m app.evaluation.run_eval [--kb-id N] [--no-judge]`，详见 `高级能力与可选依赖.md`。

---

## 通用错误格式

HTTP 状态码：
- 400：参数错误
- 401：未登录 / Token 过期
- 403：无权操作（访问他人数据）
- 404：资源不存在
- 500：服务器错误

错误体：`{ "detail": "错误描述" }`
