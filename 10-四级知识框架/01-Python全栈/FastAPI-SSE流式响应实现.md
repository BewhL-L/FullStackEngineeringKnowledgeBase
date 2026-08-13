---
title: FastAPI SSE 流式响应实现
category: Python全栈
subcategory: AI应用开发
tags: [#Python全栈/AI应用, #AI结合/流式响应, #难度/高级, #类型/实战]
difficulty: 高级
pre: [[Python-异步编程asyncio]], [[FastAPI-中间件与异常处理]]
related: [[useSSE自定义Hook封装]], [[SpringAI-FunctionCalling工具调用]]
update: 2026-08-13
status: 完善
---

# FastAPI SSE 流式响应实现

## 1. 核心概述

Server-Sent Events (SSE) 是一种基于 HTTP 的服务器推送技术，允许服务器向客户端单向推送事件流。在 AI 对话场景中，SSE 是实现"打字机效果"的核心技术——模型生成一个 token 就推一个 token，用户无需等待完整响应。FastAPI 通过 StreamingResponse 可以原生支持 SSE。

**解决的场景问题**：
- LLM 生成完整回答需要 10-30 秒，用户等待焦虑
- 传统 HTTP 请求-响应模式无法展示中间过程
- WebSocket 对 AI 对话场景过重，SSE 更轻量
- 需要对接 OpenAI 兼容 API 的流式输出并转发给前端
- 长对话需要管理对话历史和流式输出的结合

## 2. 底层原理/核心逻辑

### SSE 协议规范

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no  # 禁用 Nginx 缓冲

data: {"content": "你"}

data: {"content": "好"}

data: {"content": "，"}

data: [DONE]
```

**关键特性**：
- 基于 HTTP，无需升级协议
- 服务器单向推送，客户端用 EventSource 接收
- 自动重连（浏览器内置）
- 支持事件类型和 ID
- 纯文本格式，调试简单

### FastAPI 流式响应原理

```
客户端请求 → FastAPI 路由 → StreamingResponse
                              ↓
                        异步生成器 (async generator)
                              ↓
                        yield 每个数据块 → 逐块发送给客户端
```

`StreamingResponse` 接受一个异步生成器，每次 `yield` 都会立即将数据刷到客户端，不需要等待生成器完成。

### 对接 LLM 流式 API 的架构

```
前端 (EventSource/fetch)
    ↓ SSE
FastAPI /chat 端点
    ↓ 转发流式请求
OpenAI 兼容 API (stream=true)
    ↓ 逐 token 返回
FastAPI 异步迭代 → 解析 SSE → yield 给前端
```

## 3. 实操示例

### 基础 SSE 端点

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

@app.get("/api/chat/sse")
async def chat_sse(message: str):
    """基础 SSE 流式响应"""
    async def event_generator():
        # 模拟 LLM 逐 token 生成
        words = list(message)
        for word in words:
            # SSE 格式：data: 内容\n\n
            yield f"data: {json.dumps({'content': word}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.1)  # 模拟生成延迟
        # 结束标记
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
```

### 对接 OpenAI 兼容 API 流式转发

```python
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import List, Optional

client = AsyncOpenAI(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 2000

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """对接 OpenAI 流式 API 并转发"""
    async def event_generator():
        try:
            stream = await client.chat.completions.create(
                model=request.model,
                messages=[m.model_dump() for m in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
```

### 带对话历史管理的流式端点

```python
from collections import defaultdict
import uuid

# 内存存储对话历史（生产环境用 Redis）
conversation_history = defaultdict(list)

@app.post("/api/conversation/{conv_id}/stream")
async def conversation_stream(conv_id: str, request: ChatRequest):
    """带对话历史的流式对话"""
    # 读取历史
    history = conversation_history.get(conv_id, [])

    # 拼接历史 + 当前消息
    all_messages = history + [m.model_dump() for m in request.messages]

    full_response = ""

    async def event_generator():
        nonlocal full_response
        try:
            stream = await client.chat.completions.create(
                model=request.model,
                messages=all_messages,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"

            # 保存到历史
            conversation_history[conv_id].append({"role": "user", "content": request.messages[-1].content})
            conversation_history[conv_id].append({"role": "assistant", "content": full_response})

            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### 心跳保活与背压控制

```python
@app.post("/api/chat/robust-stream")
async def robust_chat_stream(request: ChatRequest):
    """健壮的流式响应：心跳 + 背压 + 中止处理"""
    from starlette.requests import Request as StarletteRequest

    async def event_generator(starlette_request: StarletteRequest):
        try:
            stream = await client.chat.completions.create(
                model=request.model,
                messages=[m.model_dump() for m in request.messages],
                stream=True,
            )

            last_heartbeat = asyncio.get_event_loop().time()

            async for chunk in stream:
                # 检查客户端是否断开
                if await starlette_request.is_disconnected():
                    break

                # 心跳：超过 15 秒没数据就发注释行
                now = asyncio.get_event_loop().time()
                if now - last_heartbeat > 15:
                    yield ": heartbeat\n\n"
                    last_heartbeat = now

                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"

            yield "data: [DONE]\n\n"

        except asyncio.CancelledError:
            # 客户端断开，清理资源
            pass
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    from starlette.requests import Request as StarletteReq
    # 需要在路由中注入 request
    pass
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 前端收不到流式数据，等到全部完成才显示 | Nginx/反向代理缓冲了响应 | 添加 `X-Accel-Buffering: no` 头，Nginx 配置 `proxy_buffering off` |
| SSE 连接几分钟后自动断开 | 网关/负载均衡超时 | 发心跳包保活，配置网关超时时间 |
| EventSource 不支持 POST 请求 | SSE 规范只支持 GET | 用 fetch + ReadableStream 替代 EventSource，或用 GET 传参 |
| 中文乱码 | 编码问题 | 确保 `Content-Type: text/event-stream; charset=utf-8` |
| 内存泄漏 | 生成器未正确关闭 | 用 try/finally 或 async context manager 清理 |

### 踩坑点

1. **不要用 `print` 调试流式接口**：print 会缓冲，影响实时性
2. **`yield` 之间不要有阻塞操作**：否则会卡住整个流
3. **SSE 数据必须以 `\n\n` 结尾**：否则浏览器不会触发事件
4. **生产环境必须加超时和重试**：网络不稳定时连接会断

### 优化方案

- **用 `sse-starlette` 库**：更规范的 SSE 实现，支持事件类型和 ID
- **Redis 存储对话历史**：多实例部署时共享状态
- **流式输出提前终止**：检测到完整回答后及时停止 API 调用

```python
# sse-starlette 用法
from sse_starlette.sse import EventSourceResponse

@app.get("/api/chat/sse-v2")
async def chat_sse_v2(message: str):
    async def event_generator():
        yield {"event": "start", "data": "开始生成"}
        for word in message:
            yield {"event": "token", "data": word}
            await asyncio.sleep(0.1)
        yield {"event": "done", "data": "完成"}

    return EventSourceResponse(event_generator())
```

## 5. 延伸拓展方向

- [[useSSE自定义Hook封装]]：前端接收 SSE 的最佳实践
- [[Python-异步编程asyncio]]：异步生成器底层原理
- [[FastAPI-中间件与异常处理]]：流式响应的异常处理
- [[Agent记忆机制设计与实现]]：对话历史管理的进阶方案
- [[AI网关与多模型路由设计]]：生产级 AI 网关中的流式处理

## 6. 参考资料

- [MDN: Server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [FastAPI: StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [sse-starlette](https://github.com/sysid/sse-starlette)
- [OpenAI: Streaming API](https://platform.openai.com/docs/api-reference/streaming)

#待完善
