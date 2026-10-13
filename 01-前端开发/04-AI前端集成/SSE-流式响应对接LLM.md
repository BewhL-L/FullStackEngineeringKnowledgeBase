---
title: SSE 流式响应对接 LLM
tags: [AI, 实时通信, LLM, 原子笔记]
category: 前端开发
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[JavaScript核心语法与ES6+]]", "[[统一AI网关设计与实现]]"]
aliases: [SSE-流式响应对接LLM, 流式响应与SSE, FastAPI-SSE流式响应实现]
---

# SSE 流式响应对接 LLM

> **文档说明**：系统讲解 Server-Sent Events（SSE）技术原理，以及如何在前后端对接大语言模型（LLM）时实现流式响应输出，涵盖 SSE 协议规范、前端 EventSource 与 Fetch 流式读取、后端 Spring Boot/Node.js SSE 实现、OpenAI 兼容 API 流式对接、流式响应的错误处理与重连、打字机效果实现，以及 SSE vs WebSocket 对比。
>
> **适用人群**：前端开发工程师、后端开发工程师、AI 应用开发者、需要实现 LLM 流式输出的全栈开发者
>
> **前置知识**：[[JavaScript核心语法与ES6+]]、[[统一AI网关设计与实现]]、[[Agent工具调用FunctionCalling]]

---

## 一、概述

**Server-Sent Events（SSE）** 是一种基于 HTTP 的服务器推送技术，允许服务器向客户端单向推送实时数据。在 LLM 应用中，SSE 是实现"打字机效果"（Token 逐个输出）的主流方案，用户无需等待完整响应即可看到模型逐步生成的内容。

### 1. 为什么 LLM 需要流式响应

| 痛点 | 说明 |
|------|------|
| **响应时间长** | LLM 生成完整回答可能需要 5~30 秒，用户等待体验差 |
| **首字延迟高** | 传统方式需等全部生成完才返回，首字延迟 = 总生成时间 |
| **用户体验差** | 长时间空白等待，用户不确定系统是否在工作 |
| **输出不可控** | 无法在生成过程中中断或修改 |

**流式响应的优势**：
- **首字延迟低**：模型生成第一个 Token 后立即推送，用户很快看到内容
- **体验流畅**：类似人类打字的效果，用户感知响应快
- **可中断**：用户可在生成过程中停止
- **进度可见**：用户能看到生成进度，减少焦虑

### 2. SSE vs WebSocket vs 轮询

| 特性 | SSE | WebSocket | 长轮询 |
|------|-----|-----------|--------|
| **通信方向** | 服务器→客户端（单向） | 双向 | 客户端→服务器（请求-响应） |
| **协议** | HTTP/HTTPS | 独立协议（ws/wss） | HTTP/HTTPS |
| **连接方式** | 长连接，自动重连 | 长连接，需手动重连 | 每次请求新建连接 |
| **数据格式** | 文本（UTF-8） | 文本/二进制 | 文本/二进制 |
| **浏览器支持** | ✅ 原生 EventSource | ✅ 原生 WebSocket | ✅ 原生支持 |
| **断线重连** | ✅ 内置自动重连 | ❌ 需手动实现 | ❌ 无 |
| **事件类型** | ✅ 支持自定义事件 | ❌ 需自定义协议 | ❌ 无 |
| **兼容性** | IE 不支持 | 所有现代浏览器 | 所有浏览器 |
| **代理/防火墙** | ✅ HTTP 友好 | ⚠️ 部分代理不支持 | ✅ HTTP 友好 |
| **适用场景** | LLM 流式输出、实时通知、股票行情 | 聊天室、协同编辑、游戏 | 简单实时需求 |
| **LLM 流式输出** | ✅ **首选** | 可用但过重 | ❌ 不适合 |

**为什么 LLM 流式输出首选 SSE**：
1. LLM 输出是单向的（服务器推 Token 给客户端），不需要双向通信
2. SSE 基于 HTTP，无需额外协议升级，代理/防火墙友好
3. SSE 内置自动重连，网络波动时自动恢复
4. SSE 支持自定义事件类型，可区分 content/done/error 等
5. 实现简单，前后端都有成熟的库支持

### 3. SSE 协议规范

**响应头**：
```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no  # Nginx 关闭缓冲（重要！）
```

**数据格式**：
```text
event: message\n
data: {"content":"你"}\n\n

data: {"content":"好"}\n\n

id: 123\n
event: done\n
data: {"finish_reason":"stop"}\n\n
```

| 字段 | 说明 |
|------|------|
| `data:` | 消息数据（可多行，以 `\n\n` 结尾表示消息结束） |
| `event:` | 自定义事件类型（默认 message） |
| `id:` | 消息 ID，断线重连时通过 `Last-Event-ID` 头传递 |
| `retry:` | 重连间隔（毫秒），通知客户端重连等待时间 |
| `:` | 注释行（心跳保活，防止连接超时） |

---

## 二、前端实现

### 1. EventSource API（原生）

**基础用法**：
```javascript
// 创建 SSE 连接
const eventSource = new EventSource('/api/chat/stream?prompt=你好');

// 监听默认 message 事件
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到数据:', data);
  // 追加到页面
  appendContent(data.content);
};

// 监听自定义事件
eventSource.addEventListener('done', (event) => {
  const data = JSON.parse(event.data);
  console.log('生成完成:', data.finish_reason);
  eventSource.close();
});

eventSource.addEventListener('error', (event) => {
  console.error('SSE 错误:', event);
  if (eventSource.readyState === EventSource.CLOSED) {
    console.log('连接已关闭');
  }
});

// 关闭连接
// eventSource.close();
```

**EventSource 状态**：
| 状态 | 值 | 说明 |
|------|-----|------|
| `EventSource.CONNECTING` | 0 | 连接中 |
| `EventSource.OPEN` | 1 | 已打开 |
| `EventSource.CLOSED` | 2 | 已关闭 |

**EventSource 的局限性**：
- ❌ 只支持 GET 请求（无法在 body 中传参数）
- ❌ 无法自定义请求头（如 Authorization）
- ❌ 只支持文本数据，不支持二进制
- ❌ IE 不支持

**解决方案**：使用 **Fetch API + ReadableStream** 手动解析 SSE，支持 POST、自定义头。

### 2. Fetch API 流式读取（推荐）

Fetch API 支持读取响应体流，可以手动解析 SSE 格式，支持 POST 请求和自定义头。

```javascript
/**
 * 使用 Fetch 实现 SSE 流式读取（支持 POST 和自定义头）
 */
async function streamChat(messages, onMessage, onDone, onError) {
  const controller = new AbortController();

  try {
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ messages, stream: true }),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    // 获取响应体读取器
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // 解码字节为文本
      buffer += decoder.decode(value, { stream: true });

      // 按 \n\n 分割 SSE 消息
      const messages = buffer.split('\n\n');
      buffer = messages.pop(); // 保留不完整的消息

      for (const msg of messages) {
        if (!msg.trim()) continue;

        // 解析 SSE 消息
        const parsed = parseSSEMessage(msg);
        if (parsed.event === 'done') {
          onDone?.(parsed.data);
          return;
        } else if (parsed.event === 'error') {
          throw new Error(parsed.data?.message || '流式响应错误');
        } else {
          onMessage?.(parsed.data);
        }
      }
    }

    // 处理缓冲区剩余内容
    if (buffer.trim()) {
      const parsed = parseSSEMessage(buffer);
      onMessage?.(parsed.data);
    }

    onDone?.({ finish_reason: 'completed' });
  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('请求已中止');
    } else {
      onError?.(error);
    }
  }

  return () => controller.abort(); // 返回中止函数
}

/**
 * 解析单条 SSE 消息
 */
function parseSSEMessage(msg) {
  const lines = msg.split('\n');
  let event = 'message';
  let data = '';
  let id = null;

  for (const line of lines) {
    if (line.startsWith('event:')) {
      event = line.slice(6).trim();
    } else if (line.startsWith('data:')) {
      data += line.slice(5).trim();
    } else if (line.startsWith('id:')) {
      id = line.slice(3).trim();
    }
  }

  try {
    data = data ? JSON.parse(data) : null;
  } catch {
    // 非 JSON 数据保持原样
  }

  return { event, data, id };
}
```

**使用示例**：
```javascript
let abortFn = null;

// 开始流式对话
abortFn = await streamChat(
  [{ role: 'user', content: '用一句话介绍自己' }],
  (data) => {
    // 逐个 Token 追加
    appendToChat(data.content);
  },
  (data) => {
    console.log('生成完成:', data);
  },
  (error) => {
    console.error('错误:', error);
    showError(error.message);
  }
);

// 停止生成
// abortFn();
```

### 3. 打字机效果实现

```javascript
/**
 * 打字机效果：逐字显示内容
 */
class Typewriter {
  constructor(element, options = {}) {
    this.element = element;
    this.speed = options.speed || 20; // 每个字符显示间隔（ms）
    this.queue = [];
    this.isTyping = false;
  }

  // 追加文本到队列
  append(text) {
    for (const char of text) {
      this.queue.push(char);
    }
    if (!this.isTyping) {
      this.type();
    }
  }

  // 直接设置完整文本（跳过打字效果）
  setText(text) {
    this.queue = [];
    this.element.textContent = text;
  }

  async type() {
    this.isTyping = true;
    while (this.queue.length > 0) {
      const char = this.queue.shift();
      this.element.textContent += char;
      await this.sleep(this.speed);
    }
    this.isTyping = false;
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // 清空
  clear() {
    this.queue = [];
    this.element.textContent = '';
  }
}

// 使用
const outputEl = document.getElementById('chat-output');
const typewriter = new Typewriter(outputEl, { speed: 15 });

streamChat(messages, (data) => {
  typewriter.append(data.content);
});
```

### 4. Vue3 组合式封装

```javascript
// useSSEChat.js
import { ref, onUnmounted } from 'vue';

export function useSSEChat() {
  const content = ref('');
  const isStreaming = ref(false);
  const isDone = ref(false);
  const error = ref(null);
  let abortController = null;

  const startStream = async (messages) => {
    content.value = '';
    isStreaming.value = true;
    isDone.value = false;
    error.value = null;
    abortController = new AbortController();

    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages, stream: true }),
        signal: abortController.signal,
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        buffer = events.pop();

        for (const evt of events) {
          const dataLine = evt.split('\n').find(l => l.startsWith('data:'));
          if (dataLine) {
            const data = JSON.parse(dataLine.slice(5).trim());
            if (data.content) {
              content.value += data.content;
            }
            if (data.finish_reason) {
              isDone.value = true;
            }
          }
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        error.value = err.message;
      }
    } finally {
      isStreaming.value = false;
    }
  };

  const stopStream = () => {
    abortController?.abort();
    isStreaming.value = false;
  };

  onUnmounted(() => {
    abortController?.abort();
  });

  return { content, isStreaming, isDone, error, startStream, stopStream };
}
```

```vue
<!-- ChatComponent.vue -->
<template>
  <div class="chat-container">
    <div class="messages">
      <div class="message assistant">
        <span>{{ content }}</span>
        <span v-if="isStreaming" class="cursor">|</span>
      </div>
    </div>
    <div class="controls">
      <button v-if="!isStreaming" @click="send">发送</button>
      <button v-else @click="stopStream">停止</button>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup>
import { useSSEChat } from './useSSEChat';

const { content, isStreaming, error, startStream, stopStream } = useSSEChat();

const send = () => {
  startStream([{ role: 'user', content: '你好' }]);
};
</script>
```

---

## 三、后端实现

### 1. Spring Boot SSE 实现

**方式1：SseEmitter（Spring 原生）**

```java
@RestController
@RequestMapping("/api/chat")
public class ChatController {

    @Autowired
    private ChatService chatService;

    @PostMapping("/stream")
    public SseEmitter streamChat(@RequestBody ChatRequest request) {
        // 设置超时时间（0 表示不超时）
        SseEmitter emitter = new SseEmitter(0L);

        // 异步执行流式生成
        CompletableFuture.runAsync(() -> {
            try {
                chatService.streamGenerate(request.getMessages(), token -> {
                    try {
                        // 发送 Token
                        emitter.send(SseEmitter.event()
                            .name("message")
                            .data(Map.of("content", token)));
                    } catch (IOException e) {
                        throw new RuntimeException("发送失败", e);
                    }
                });

                // 发送完成事件
                emitter.send(SseEmitter.event()
                    .name("done")
                    .data(Map.of("finish_reason", "stop")));

                emitter.complete();
            } catch (Exception e) {
                try {
                    emitter.send(SseEmitter.event()
                        .name("error")
                        .data(Map.of("message", e.getMessage())));
                } catch (IOException ignored) {}
                emitter.completeWithError(e);
            }
        });

        return emitter;
    }
}
```

**方式2：直接写 OutputStream（更底层）**

```java
@GetMapping("/api/chat/stream")
public void streamChat(HttpServletResponse response) throws IOException {
    response.setContentType("text/event-stream");
    response.setCharacterEncoding("UTF-8");
    response.setHeader("Cache-Control", "no-cache");
    response.setHeader("Connection", "keep-alive");
    response.setHeader("X-Accel-Buffering", "no");

    PrintWriter writer = response.getWriter();

    // 模拟流式输出
    String text = "这是一段流式输出的文本内容";
    for (char c : text.toCharArray()) {
        writer.write("data: " + JSON.toJSONString(Map.of("content", String.valueOf(c))) + "\n\n");
        writer.flush();
        Thread.sleep(50);
    }

    writer.write("event: done\ndata: {\"finish_reason\":\"stop\"}\n\n");
    writer.flush();
}
```

### 2. 对接 OpenAI 兼容 API（流式）

```java
@Service
public class ChatService {

    private final WebClient webClient;

    public ChatService(@Value("${llm.api-key}") String apiKey,
                       @Value("${llm.base-url}") String baseUrl) {
        this.webClient = WebClient.builder()
            .baseUrl(baseUrl)
            .defaultHeader("Authorization", "Bearer " + apiKey)
            .build();
    }

    /**
     * 流式调用 LLM，通过回调逐个返回 Token
     */
    public void streamGenerate(List<Message> messages, Consumer<String> tokenCallback) {
        // 构建 OpenAI 兼容请求
        Map<String, Object> requestBody = Map.of(
            "model", "gpt-4o",
            "messages", messages,
            "stream", true,
            "temperature", 0.7
        );

        webClient.post()
            .uri("/v1/chat/completions")
            .bodyValue(requestBody)
            .retrieve()
            .bodyToFlux(String.class)  // 流式读取响应
            .filter(line -> line.startsWith("data: "))
            .map(line -> line.substring(6).trim())
            .filter(data -> !"[DONE]".equals(data))  // OpenAI 结束标记
            .map(data -> {
                try {
                    return JSON.parseObject(data);
                } catch (Exception e) {
                    return null;
                }
            })
            .filter(Objects::nonNull)
            .subscribe(json -> {
                // 解析 Delta 内容
                String content = json.getJSONArray("choices")
                    .getJSONObject(0)
                    .getJSONObject("delta")
                    .getString("content");
                if (content != null) {
                    tokenCallback.accept(content);
                }
            });
    }
}
```

```text
### 3. Node.js (Express) SSE 实现
```

```javascript
const express = require('express');
const app = express();

app.post('/api/chat/stream', async (req, res) => {
  // 设置 SSE 响应头
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('X-Accel-Buffering', 'no');
  res.flushHeaders();

  try {
    // 调用 LLM 流式 API
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4o',
        messages: req.body.messages,
        stream: true,
      }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            res.write(`event: done\ndata: {"finish_reason":"stop"}\n\n`);
            res.end();
            return;
          }
          try {
            const json = JSON.parse(data);
            const content = json.choices?.[0]?.delta?.content;
            if (content) {
              res.write(`data: ${JSON.stringify({ content })}\n\n`);
            }
          } catch (e) {
            console.error('解析失败:', e);
          }
        }
      }
    }
  } catch (error) {
    res.write(`event: error\ndata: ${JSON.stringify({ message: error.message })}\n\n`);
    res.end();
  }

  // 客户端断开时清理
  req.on('close', () => {
    console.log('客户端断开连接');
  });
});

app.listen(3000);
```

---

## 四、关键问题与最佳实践

### 1. Nginx 反向代理配置

Nginx 默认会缓冲响应，导致 SSE 数据不能实时推送。必须关闭缓冲：

```nginx
location /api/chat/stream {
    proxy_pass http://backend;
    proxy_buffering off;          # 关闭代理缓冲（关键）
    proxy_cache off;               # 关闭缓存
    proxy_read_timeout 300s;       # 长连接超时（LLM 生成可能较慢）
    proxy_send_timeout 300s;
    chunked_transfer_encoding on;  # 启用分块传输
    proxy_set_header Connection ''; # 保持长连接
}
```

### 2. 心跳保活

SSE 连接长时间没有数据时，可能被中间代理（Nginx、负载均衡器）超时断开。需要定期发送心跳：

```java
// 后端：每 15 秒发送一次心跳注释
ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
scheduler.scheduleAtFixedRate(() -> {
    try {
        emitter.send(": heartbeat\n\n");  // 注释行，客户端忽略
    } catch (IOException e) {
        // 连接已断开
    }
}, 15, 15, TimeUnit.SECONDS);
```

### 3. 断线重连

**EventSource 自动重连**：
- EventSource 内置自动重连，断线后默认 3 秒后重连
- 重连时会带上 `Last-Event-ID` 请求头（最后收到的消息 ID）
- 后端可根据 `Last-Event-ID` 从断点继续推送

**Fetch 手动重连**：
```javascript
async function streamWithRetry(messages, maxRetries = 3) {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      await streamChat(messages, onMessage, onDone, onError);
      return; // 成功完成
    } catch (error) {
      if (attempt === maxRetries) throw error;
      console.log(`重试 ${attempt + 1}/${maxRetries}...`);
      await new Promise(r => setTimeout(r, 1000 * Math.pow(2, attempt))); // 指数退避
    }
  }
}
```

### 4. 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| **网络断开** | 自动重连（EventSource）或手动重试（Fetch） |
| **HTTP 错误** | 检查 response.status，显示错误信息 |
| **LLM 超时** | 后端设置合理超时，前端提示用户 |
| **Token 超限** | 后端捕获 400 错误，提示上下文过长 |
| **API Key 失效** | 后端捕获 401 错误，引导重新登录 |
| **限流** | 后端捕获 429 错误，提示稍后重试 |
| **解析错误** | 前端 try-catch JSON.parse，跳过异常数据 |

### 5. 性能优化

| 优化点 | 说明 |
|--------|------|
| **减少发送频率** | LLM Token 生成很快时，可累积几个 Token 一起发送，减少 IO |
| **gzip 压缩** | SSE 响应可启用 gzip 压缩（但需注意实时性） |
| **连接复用** | 同一用户的多次对话可复用连接（需协议设计） |
| **后端线程池** | 流式处理使用独立线程池，避免阻塞主线程 |
| **超时设置** | 合理设置读取超时，避免连接泄漏 |
| **资源清理** | 客户端断开时及时清理后端资源（取消 LLM 请求） |

### 6. 安全考虑

- [ ] **鉴权**：SSE 请求需携带 Token（Fetch 方式可自定义头，EventSource 需用 URL 参数或 Cookie）
- [ ] **限流**：防止用户频繁发起流式请求消耗 LLM Token
- [ ] **输入校验**：校验用户输入，防止 Prompt 注入
- [ ] **输出过滤**：对 LLM 输出进行敏感内容过滤
- [ ] **CORS**：配置正确的 CORS 策略，允许 SSE 跨域
- [ ] **HTTPS**：生产环境必须使用 HTTPS，防止数据泄露

---

## 五、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 前端收不到数据 | Nginx 缓冲未关闭 / 响应头不对 | 设置 `X-Accel-Buffering: no`，`proxy_buffering off` |
| 连接很快断开 | 代理超时 / 无心跳 | 增加 `proxy_read_timeout`，定期发送心跳 |
| EventSource 无法传 POST 参数 | EventSource 只支持 GET | 改用 Fetch + ReadableStream |
| EventSource 无法传 Authorization 头 | EventSource 不支持自定义头 | 改用 Fetch，或用 Cookie/URL 参数传 Token |
| 数据不完整 | TCP 分包，一次 read 可能收到部分数据 | 使用 buffer 累积，按 `\n\n` 分割 |
| 中文乱码 | 编码不一致 | 统一 UTF-8，`Content-Type: text/event-stream; charset=utf-8` |
| 重连后重复数据 | 未使用 Last-Event-ID | 后端根据 Last-Event-ID 从断点继续 |
| 后端内存泄漏 | 客户端断开后未清理资源 | 监听 `req.on('close')` 或 emitter.onCompletion/onTimeout |
| 浏览器显示 [object Object] | 未 JSON.parse 直接显示 | 解析 data 后取 content 字段 |
| 打字机效果卡顿 | DOM 频繁更新 | 使用 DocumentFragment 或虚拟列表，减少重排 |
| 移动端后台断开 | 浏览器后台标签页限制 | 重新进入页面时自动重连 |
| CORS 错误 | 跨域未配置 | 后端配置 CORS 允许对应域名 |

---

## 六、关联笔记

### AI 工程
- [[统一AI网关设计与实现]] · [[Agent工具调用FunctionCalling]] · [[Agent记忆机制设计]]
- [[RAG架构设计与流程]] · [[高级RAG-Hybrid检索与重排序]] · [[向量库选型对比表]]
- [[AI应用可观测性-Langfuse]] · [[成本控制与Token计费]]

### 前端
- [[JavaScript核心语法与ES6+]] · [[Vue3-组合式API设计模式]] · [[TypeScript-类型系统进阶_backup_skeleton]]
- [[前端性能优化实战]] · [[Pinia-状态管理核心]]

### 后端
- [[SpringBoot-自动装配原理]] · [[Gateway-网关路由与鉴权]] · [[SpringCache-缓存抽象]]

### 实战
- [[实战-RAG企业知识库问答系统]] · [[实战-AI智能客服系统]] · [[AI网关与多模型路由]]

### 导航
- [[MOC-AI工程化]] · [[MOC-前端开发]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[JavaScript核心语法与ES6+]] 异步编程 → 学习本文 SSE 流式响应 → 深入 [[统一AI网关设计与实现]] AI 后端 → 实践 [[实战-RAG企业知识库问答系统]] 完整项目 → 研究 [[Agent工具调用FunctionCalling]] 和 [[Agent记忆机制设计]] 高级 Agent。
