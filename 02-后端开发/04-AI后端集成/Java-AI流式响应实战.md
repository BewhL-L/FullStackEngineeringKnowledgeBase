---
title: Java-AI流式响应实战
tags: [Java, 流式响应, 实时通信, SpringAI, 原子笔记]
category: 后端开发
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["SpringWebFlux-响应式编程", "WebSocket-SSE联调实战", "大模型应用开发实战"]
aliases: [Java-AI流式响应实战]
---

# Java-AI流式响应实战

> **文档说明**：系统讲解 Java 后端实现 AI 大模型流式响应的完整方案，包括 SSE 原理、OpenAI 流式 API、Spring MVC SSE、Spring WebFlux 响应式流、Spring AI 集成、前端接收、流式 RAG、错误处理与中断，以及生产级最佳实践。
>
> **适用人群**：后端开发工程师、全栈开发者、需要构建 AI 流式输出应用的开发者
>
> **前置知识**：[[SpringWebFlux-响应式编程]]、[[WebSocket-SSE联调实战]]、[[大模型应用开发实战]]、[[SpringBoot-Web层设计]]

---

## 一、概述

### 1. 为什么需要流式响应

大模型生成内容是逐 Token 生成的，如果等待完整响应再返回，用户需要等待数秒到数十秒，体验极差。**流式响应（Streaming）** 将生成的内容实时推送给客户端，实现"打字机"效果。

| 方式 | 用户等待时间 | 体验 | 适用场景 |
|------|------------|------|---------|
| **非流式** | 完整生成后返回 | 差（长时间白屏） | 短文本、API 调用 |
| **流式** | 首 Token 即返回 | 好（打字机效果） | 聊天、长文本生成、AI 对话 |

### 2. 流式响应技术方案

| 方案 | 协议 | 特点 | 适用场景 |
|------|------|------|---------|
| **SSE** | HTTP | 服务端单向推送、简单、自动重连 | AI 文本流式输出 |
| **WebSocket** | WS | 双向通信、复杂 | 需要交互的实时应用 |
| **gRPC 流** | HTTP/2 | 高性能、强类型 | 微服务间流式通信 |
| **Chunked Transfer** | HTTP | 分块传输编码 | 大文件、通用流 |

> **AI 流式输出首选 SSE**：简单、单向、浏览器原生支持（EventSource）。

### 3. OpenAI 流式 API 原理

```
OpenAI Chat Completions 流式响应：
- 请求时设置 stream: true
- 响应 Content-Type: text/event-stream
- 每个事件是一个 JSON 对象（增量内容）
- 以 data: [DONE] 结束

事件格式：
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","choices":[{"delta":{"content":"你"},"finish_reason":null}]}

data: {"choices":[{"delta":{"content":"好"},"finish_reason":null}]}

data: [DONE]
```

---

## 二、Spring MVC SSE 实现

### 1. 基础 SSE 控制器

```java
@RestController
@RequestMapping("/api/ai")
public class AiController {

    @Autowired
    private OpenAiService openAiService;

    @GetMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter chatStream(@RequestParam String message) {
        SseEmitter emitter = new SseEmitter(0L);  // 0 表示永不超时

        // 异步执行 AI 调用
        CompletableFuture.runAsync(() -> {
            try {
                openAiService.streamChat(message, chunk -> {
                    try {
                        emitter.send(SseEmitter.event()
                            .name("message")
                            .data(chunk));
                    } catch (IOException e) {
                        emitter.completeWithError(e);
                    }
                });
                emitter.complete();
            } catch (Exception e) {
                emitter.completeWithError(e);
            }
        });

        return emitter;
    }
}
```

### 2. OpenAI 流式客户端

```java
@Service
public class OpenAiService {

    private final WebClient webClient;

    public OpenAiService(@Value("${openai.api-key}") String apiKey) {
        this.webClient = WebClient.builder()
            .baseUrl("https://api.openai.com/v1")
            .defaultHeader("Authorization", "Bearer " + apiKey)
            .build();
    }

    public void streamChat(String message, Consumer<String> onChunk) {
        String requestBody = """
            {
                "model": "gpt-4o",
                "stream": true,
                "messages": [{"role": "user", "content": "%s"}]
            }
            """.formatted(message);

        webClient.post()
            .uri("/chat/completions")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(requestBody)
            .retrieve()
            .bodyToFlux(String.class)  // 按行读取 SSE
            .filter(line -> line.startsWith("data: "))
            .map(line -> line.substring(6))  // 去掉 "data: "
            .filter(data -> !"[DONE]".equals(data))
            .map(this::extractContent)
            .filter(Objects::nonNull)
            .doOnNext(onChunk)
            .blockLast();  // 等待完成
    }

    private String extractContent(String json) {
        try {
            JsonNode node = new ObjectMapper().readTree(json);
            JsonNode content = node.path("choices").get(0).path("delta").path("content");
            return content.isMissingNode() ? null : content.asText();
        } catch (Exception e) {
            return null;
        }
    }
}
```

### 3. SseEmitter 事件类型

```java
// 发送不同类型的事件
emitter.send(SseEmitter.event()
    .name("message")      // 事件名
    .id("1")              // 事件 ID（断线重连用）
    .data("内容片段")      // 数据
    .comment("注释"));    // 注释

// 发送完成信号
emitter.send(SseEmitter.event()
    .name("done")
    .data("[DONE]"));
emitter.complete();

// 发送错误
emitter.completeWithError(new RuntimeException("AI 服务异常"));
```

### 4. 完整的 AI 流式控制器

```java
@RestController
@RequestMapping("/api/ai")
public class AiStreamController {

    @Autowired
    private OpenAiService openAiService;

    @GetMapping(value = "/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter chat(
            @RequestParam String message,
            @RequestHeader(value = "Authorization", required = false) String auth) {

        // 认证校验
        if (auth == null || !auth.startsWith("Bearer ")) {
            SseEmitter error = new SseEmitter();
            error.completeWithError(new ResponseStatusException(HttpStatus.UNAUTHORIZED));
            return error;
        }

        SseEmitter emitter = new SseEmitter(120_000L);  // 120秒超时

        // 客户端断开回调
        emitter.onCompletion(() -> log.info("SSE 连接完成"));
        emitter.onTimeout(() -> log.warn("SSE 连接超时"));
        emitter.onError(e -> log.error("SSE 连接错误", e));

        // 发送连接成功事件
        try {
            emitter.send(SseEmitter.event().name("connected").data("ok"));
        } catch (IOException e) {
            emitter.completeWithError(e);
            return emitter;
        }

        // 异步流式调用 AI
        CompletableFuture.runAsync(() -> {
            try {
                StringBuilder fullContent = new StringBuilder();
                openAiService.streamChat(message, chunk -> {
                    try {
                        emitter.send(SseEmitter.event()
                            .name("message")
                            .data(chunk));
                        fullContent.append(chunk);
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }
                });

                // 保存完整对话（异步，不阻塞流）
                saveConversationAsync(message, fullContent.toString());

                emitter.send(SseEmitter.event().name("done").data("[DONE]"));
                emitter.complete();
            } catch (Exception e) {
                try {
                    emitter.send(SseEmitter.event()
                        .name("error")
                        .data(e.getMessage()));
                } catch (IOException ignored) {}
                emitter.completeWithError(e);
            }
        }, aiExecutor);  // 专用线程池

        return emitter;
    }

    @Bean
    public Executor aiExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(50);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("ai-stream-");
        executor.initialize();
        return executor;
    }
}
```

---

## 三、Spring WebFlux 响应式实现

### 1. WebFlux 流式控制器

```java
@RestController
@RequestMapping("/api/ai")
public class AiReactiveController {

    @Autowired
    private OpenAiReactiveService aiService;

    @GetMapping(value = "/chat/flux", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<String>> chatFlux(@RequestParam String message) {
        return aiService.streamChat(message)
            .map(chunk -> ServerSentEvent.<String>builder()
                .event("message")
                .data(chunk)
                .build())
            .concatWithValues(
                ServerSentEvent.<String>builder()
                    .event("done")
                    .data("[DONE]")
                    .build()
            )
            .onErrorResume(e -> Flux.just(
                ServerSentEvent.<String>builder()
                    .event("error")
                    .data(e.getMessage())
                    .build()
            ));
    }
}
```

### 2. 响应式 AI 服务

```java
@Service
public class OpenAiReactiveService {

    private final WebClient webClient;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public Flux<String> streamChat(String message) {
        Map<String, Object> request = Map.of(
            "model", "gpt-4o",
            "stream", true,
            "messages", List.of(Map.of("role", "user", "content", message))
        );

        return webClient.post()
            .uri("/chat/completions")
            .bodyValue(request)
            .retrieve()
            .bodyToFlux(String.class)
            .filter(line -> line.startsWith("data: "))
            .map(line -> line.substring(6))
            .filter(data -> !"[DONE]".equals(data))
            .handle((data, sink) -> {
                try {
                    JsonNode node = objectMapper.readTree(data);
                    String content = node.path("choices").get(0)
                        .path("delta").path("content").asText(null);
                    if (content != null) {
                        sink.next(content);
                    }
                } catch (Exception e) {
                    sink.error(e);
                }
            });
    }
}
```

---

## 四、Spring AI 集成

### 1. Spring AI 流式调用

```java
// Spring AI 依赖
// <dependency>
//     <groupId>org.springframework.ai</groupId>
//     <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
// </dependency>

@Service
public class SpringAiService {

    @Autowired
    private ChatClient chatClient;

    // 流式输出
    public Flux<String> streamChat(String message) {
        return chatClient.prompt()
            .user(message)
            .stream()
            .content();  // 返回 Flux<String>，每个元素是一个 Token 片段
    }

    // 带系统提示的流式对话
    public Flux<String> streamChatWithSystem(String systemPrompt, String userMessage) {
        return chatClient.prompt()
            .system(systemPrompt)
            .user(userMessage)
            .stream()
            .content();
    }

    // 流式 + 完整结果
    public Flux<String> streamChatWithFullResult(String message) {
        Flux<String> stream = chatClient.prompt()
            .user(message)
            .stream()
            .content();

        // 收集完整内容用于日志/保存
        stream.collectList().subscribe(chunks -> {
            String full = String.join("", chunks);
            log.info("完整回复: {}", full);
        });

        return stream;
    }
}
```

### 2. Spring AI + WebFlux 控制器

```java
@RestController
@RequestMapping("/api/ai/spring")
public class SpringAiController {

    @Autowired
    private SpringAiService aiService;

    @GetMapping(value = "/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<String>> chat(@RequestParam String message) {
        return aiService.streamChat(message)
            .map(chunk -> ServerSentEvent.<String>builder()
                .event("message")
                .data(chunk)
                .build())
            .concatWithValues(
                ServerSentEvent.<String>builder()
                    .event("done")
                    .data("[DONE]")
                    .build()
            );
    }
}
```

---

## 五、前端接收流式响应

### 1. EventSource（原生 SSE）

```javascript
// 简单 SSE 连接
const eventSource = new EventSource('/api/ai/chat?message=你好');

eventSource.addEventListener('message', (event) => {
  // 接收内容片段，追加到页面
  outputElement.textContent += event.data;
});

eventSource.addEventListener('done', () => {
  eventSource.close();  // 关闭连接
});

eventSource.addEventListener('error', (event) => {
  console.error('SSE 错误:', event);
  eventSource.close();
});
```

### 2. Fetch + ReadableStream（推荐，支持 POST）

```javascript
// Fetch 流式读取（支持 POST 和自定义头）
async function streamChat(message) {
  const response = await fetch('/api/ai/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({ message })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // 按 SSE 事件分割（\n\n）
    const events = buffer.split('\n\n');
    buffer = events.pop();  // 保留不完整的事件

    for (const event of events) {
      const lines = event.split('\n');
      let eventType = 'message';
      let data = '';

      for (const line of lines) {
        if (line.startsWith('event:')) {
          eventType = line.slice(6).trim();
        } else if (line.startsWith('data:')) {
          data += line.slice(5).trim();
        }
      }

      if (eventType === 'message' && data) {
        outputElement.textContent += data;  // 打字机效果
      } else if (eventType === 'done') {
        console.log('流式输出完成');
      } else if (eventType === 'error') {
        console.error('AI 错误:', data);
      }
    }
  }
}
```

### 3. Vue3 组合式封装

```typescript
// composables/useAiStream.ts
import { ref } from 'vue'

export function useAiStream() {
  const content = ref('')
  const loading = ref(false)
  const error = ref('')
  let abortController: AbortController | null = null

  const stream = async (message: string) => {
    loading.value = true
    error.value = ''
    content.value = ''
    abortController = new AbortController()

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
        signal: abortController.signal
      })

      const reader = response.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const events = buffer.split('\n\n')
        buffer = events.pop() || ''

        for (const event of events) {
          const dataLine = event.split('\n').find(l => l.startsWith('data:'))
          const eventLine = event.split('\n').find(l => l.startsWith('event:'))
          const eventType = eventLine?.slice(6).trim() || 'message'
          const data = dataLine?.slice(5).trim() || ''

          if (eventType === 'message' && data) {
            content.value += data
          } else if (eventType === 'error') {
            error.value = data
          }
        }
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        error.value = e.message
      }
    } finally {
      loading.value = false
    }
  }

  const stop = () => {
    abortController?.abort()
    loading.value = false
  }

  return { content, loading, error, stream, stop }
}
```

---

## 六、流式 RAG 实现

### 1. RAG + 流式输出

```java
@Service
public class RagStreamService {

    @Autowired
    private VectorStore vectorStore;
    @Autowired
    private ChatClient chatClient;

    public Flux<String> streamRagChat(String question) {
        // 1. 检索相关文档
        List<Document> docs = vectorStore.similaritySearch(question);

        // 2. 构建上下文
        String context = docs.stream()
            .map(Document::getContent)
            .collect(Collectors.joining("\n\n"));

        // 3. 构建提示词
        String prompt = """
            基于以下参考资料回答问题。如果资料中没有答案，请说"根据现有资料无法回答"。

            参考资料：
            %s

            问题：%s
            """.formatted(context, question);

        // 4. 流式生成
        return chatClient.prompt()
            .user(prompt)
            .stream()
            .content();
    }
}
```

### 2. 流式引用来源

```java
// 在流式输出中包含引用来源
@GetMapping(value = "/rag/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<ServerSentEvent<String>> ragChat(@RequestParam String question) {
    List<Document> docs = vectorStore.similaritySearch(question);

    // 先发送来源事件
    Flux<ServerSentEvent<String>> sources = Flux.fromIterable(docs)
        .map(doc -> ServerSentEvent.<String>builder()
            .event("source")
            .data(doc.getMetadata().get("source").toString())
            .build());

    // 再发送流式回答
    Flux<ServerSentEvent<String>> answer = ragService.streamRagChat(question)
        .map(chunk -> ServerSentEvent.<String>builder()
            .event("message")
            .data(chunk)
            .build());

    return sources.concatWith(answer)
        .concatWithValues(ServerSentEvent.<String>builder()
            .event("done").data("[DONE]").build());
}
```

---

## 七、错误处理与中断

### 1. 客户端中断处理

```java
// SseEmitter 检测客户端断开
@GetMapping(value = "/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public SseEmitter chat(@RequestParam String message) {
    SseEmitter emitter = new SseEmitter(120_000L);
    AtomicBoolean cancelled = new AtomicBoolean(false);

    emitter.onCompletion(() -> cancelled.set(true));
    emitter.onTimeout(() -> cancelled.set(true));
    emitter.onError(e -> cancelled.set(true));

    CompletableFuture.runAsync(() -> {
        openAiService.streamChat(message, chunk -> {
            if (cancelled.get()) {
                throw new RuntimeException("客户端已断开");
            }
            emitter.send(SseEmitter.event().data(chunk));
        });
        emitter.complete();
    });

    return emitter;
}
```

### 2. AI 服务异常处理

```java
public void streamChatWithRetry(String message, Consumer<String> onChunk) {
    int maxRetries = 2;
    for (int attempt = 0; attempt <= maxRetries; attempt++) {
        try {
            streamChat(message, onChunk);
            return;
        } catch (WebClientResponseException.TooManyRequests e) {
            // 429 限流，退避重试
            if (attempt < maxRetries) {
                try {
                    Thread.sleep((long) Math.pow(2, attempt) * 1000);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException(ie);
                }
            }
        } catch (Exception e) {
            throw new RuntimeException("AI 服务异常: " + e.getMessage(), e);
        }
    }
}
```

### 3. 超时控制

```java
// WebFlux 超时控制
public Flux<String> streamChatWithTimeout(String message) {
    return aiService.streamChat(message)
        .timeout(Duration.ofSeconds(60))  // 60秒总超时
        .onErrorResume(TimeoutException.class, e ->
            Flux.just("[响应超时，请重试]"));
}

// 首 Token 超时（更精细）
public Flux<String> streamChatWithFirstTokenTimeout(String message) {
    return aiService.streamChat(message)
        .timeout(Duration.ofSeconds(15))  // 首 Token 15秒超时
        .onErrorResume(TimeoutException.class, e ->
            Flux.error(new RuntimeException("AI 响应超时")));
}
```

---

## 八、性能优化

### 1. 线程池配置

```java
@Configuration
public class AiStreamConfig {

    @Bean("aiStreamExecutor")
    public ThreadPoolTaskExecutor aiStreamExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(Runtime.getRuntime().availableProcessors() * 2);
        executor.setMaxPoolSize(100);
        executor.setQueueCapacity(200);
        executor.setThreadNamePrefix("ai-stream-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }
}
```

### 2. 连接池配置

```java
// WebClient 连接池配置
@Bean
public WebClient aiWebClient() {
    HttpClient httpClient = HttpClient.create()
        .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 5000)
        .responseTimeout(Duration.ofSeconds(120))
        .connectionProvider(ConnectionProvider.builder("ai-connection-pool")
            .maxConnections(100)
            .pendingAcquireTimeout(Duration.ofSeconds(30))
            .build());

    return WebClient.builder()
        .clientConnector(new ReactorClientHttpConnector(httpClient))
        .baseUrl("https://api.openai.com/v1")
        .build();
}
```

### 3. Nginx 代理配置

```nginx
location /api/ai/ {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Connection '';
    proxy_buffering off;           # 关键：关闭缓冲
    proxy_cache off;
    proxy_read_timeout 120s;       # 长时间连接
    chunked_transfer_encoding on;
}
```

---

## 九、最佳实践

### 1. 设计规范

- [ ] **使用 SSE**：AI 文本流式输出首选 SSE
- [ ] **事件分类**：message（内容）、done（完成）、error（错误）、source（来源）
- [ ] **超时设置**：合理设置连接超时和首 Token 超时
- [ ] **客户端中断**：检测客户端断开，及时停止 AI 调用
- [ ] **错误事件**：AI 异常通过 error 事件通知前端，不直接断开
- [ ] **完整结果**：异步保存完整对话，不阻塞流式输出
- [ ] **专用线程池**：AI 流式调用使用独立线程池，不占用 Web 线程

### 2. 安全规范

- [ ] **认证授权**：流式接口也需要认证
- [ ] **输入过滤**：用户输入检测注入攻击
- [ ] **输出审核**：AI 输出内容安全审核
- [ ] **速率限制**：限制用户调用频率
- [ ] **敏感信息**：不将敏感信息传入 AI 或输出
- [ ] **日志脱敏**：日志中不记录完整对话内容

### 3. 体验优化

- [ ] **打字机效果**：前端逐字显示，模拟打字机
- [ ] **光标动画**：输出时显示闪烁光标
- [ ] **停止按钮**：允许用户中断生成
- [ ] **重试机制**：失败后可一键重试
- [ ] **加载状态**：等待首 Token 时显示加载动画
- [ ] **引用来源**：RAG 场景显示引用来源

---

## 十、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **前端收不到流** | Nginx 缓冲开启 / SSE 头不对 | proxy_buffering off、Content-Type: text/event-stream |
| **连接很快断开** | 超时时间短 / 代理超时 | 增大 proxy_read_timeout、SseEmitter 超时设 0 |
| **首 Token 慢** | 模型推理慢 / 网络延迟 | 使用更快模型、就近部署、预热连接 |
| **内容乱码** | 编码问题 | 确保 UTF-8、TextDecoder 使用 stream 模式 |
| **客户端断开后端仍运行** | 未检测断开 | onCompletion/onError 回调中停止生成 |
| **AI 调用阻塞 Web 线程** | 未用异步线程 | 使用专用线程池 / WebFlux 响应式 |
| **流式输出不完整** | 缓冲区未正确处理 | 按 \n\n 分割事件，保留不完整部分 |
| **EventSource 不支持 POST** | EventSource 仅支持 GET | 使用 fetch + ReadableStream |
| **跨域 SSE 失败** | CORS 未配置 | 配置 CORS、withCredentials |
| **Token 拼接错误** | delta 可能为空 | 过滤空 content、正确拼接 |
| **内存泄漏** | SseEmitter 未完成 / 线程未释放 | onCompletion 清理、超时机制 |
| **大模型 API 限流** | 调用频率过高 | 限流、排队、退避重试 |
| **流式 RAG 来源丢失** | 未在流中发送来源 | 先发送 source 事件，再发送 message |
| **生产环境不安全** | 未认证 / 输入未过滤 | 认证、输入过滤、输出审核 |
| **Spring AI 不支持流** | 版本过低 | 升级 Spring AI 1.0+、使用 stream() 方法 |

---

## 十一、关联笔记

### 实时通信
- [[WebSocket-SSE联调实战]] · [[SpringWebFlux-响应式编程]] · [[SpringBoot-Web层设计]]

### AI 应用
- [[大模型应用开发实战]] · [[RAG检索增强生成]] · [[提示词工程核心技巧]]
- [[图像理解与视觉问答]] · [[Python-向量数据库客户端]]

### 前端
- [[Vue3-组合式API设计模式]] · [[Vue3-自定义Hooks封装]] · [[Axios网络请求封装]]

### 导航
- [[MOC-后端开发]] · [[MOC-AI与效率工具]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[WebSocket-SSE联调实战]] SSE 基础 → 学习 [[SpringWebFlux-响应式编程]] 响应式编程 → 深入本文 Java AI 流式响应 → 实践 [[RAG检索增强生成]] 流式 RAG → 研究 [[大模型应用开发实战]] AI 应用 → 构建完整的 AI 流式对话应用。
