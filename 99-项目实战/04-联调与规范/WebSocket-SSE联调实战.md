---
title: WebSocket-SSE联调实战
tags: [联调, 实时通信, 原子笔记]
category: 项目实战
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[前后端联调规范与流程]]", "[[CORS跨域解决方案实战]]", "[[SpringBoot-Web层设计]]"]
aliases: [WebSocket-SSE联调实战]
---

# WebSocket-SSE联调实战

> **文档说明**：系统讲解 WebSocket 和 SSE（Server-Sent Events）的原理、使用场景、Spring Boot 后端实现、Vue3 前端实现、心跳重连机制、联调要点、安全与性能优化，以及常见问题排查。
>
> **适用人群**：全栈开发者、后端开发工程师、前端开发工程师、需要实现实时通信的开发者
>
> **前置知识**：[[前后端联调规范与流程]]、[[CORS跨域解决方案实战]]、[[SpringBoot-Web层设计]]、[[Vue3-组合式API设计模式]]

---

## 一、概述

### 1. 实时通信方案对比

| 方案 | 通信方向 | 协议 | 延迟 | 连接数 | 适用场景 |
|------|---------|------|------|--------|---------|
| **轮询（Polling）** | 客户端→服务端 | HTTP | 高 | 多 | 简单、低实时性 |
| **长轮询（Long Polling）** | 客户端→服务端 | HTTP | 中 | 中 | 兼容旧浏览器 |
| **SSE** | 服务端→客户端（单向） | HTTP | 低 | 1 | 服务端推送、通知、流式输出 |
| **WebSocket** | 双向全双工 | WS/WSS | 极低 | 1 | 聊天、协作、游戏、实时数据 |

### 2. WebSocket vs SSE

| 维度 | WebSocket | SSE |
|------|-----------|-----|
| **通信方向** | 双向全双工 | 单向（服务端→客户端） |
| **协议** | 独立 WS 协议 | 基于 HTTP |
| **数据格式** | 文本/二进制 | 仅文本（UTF-8） |
| **重连** | 需手动实现 | 浏览器自动重连 |
| **兼容性** | 现代浏览器均支持 | 现代浏览器均支持（IE 不支持） |
| **代理兼容** | 部分代理不支持 | HTTP 协议，兼容性好 |
| **实现复杂度** | 较高（需管理连接） | 简单（基于 HTTP） |
| **断线恢复** | 需自定义 | 内置 Last-Event-ID |

### 3. 选型建议

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| **聊天/即时通讯** | WebSocket | 需要双向通信 |
| **实时通知/消息推送** | SSE | 只需服务端推送，简单 |
| **AI 流式输出** | SSE | 流式文本输出，单向 |
| **实时数据看板** | SSE 或 WebSocket | 看是否需要交互 |
| **协同编辑/白板** | WebSocket | 需要双向实时同步 |
| **在线游戏** | WebSocket | 低延迟双向通信 |
| **股票/行情推送** | SSE | 服务端单向推送 |
| **进度条/任务状态** | SSE | 服务端推送进度 |

---

## 二、SSE 实战

### 1. SSE 原理

**SSE（Server-Sent Events）** 基于 HTTP 协议，服务端通过 `Content-Type: text/event-stream` 持续向客户端推送数据，客户端通过 `EventSource` API 接收。

```text
SSE 响应格式：
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: 消息内容\n\n

data: 第二条消息\n
id: 2\n
event: custom\n
data: 自定义事件消息\n\n
```

### 2. Spring Boot SSE 实现

```java
// SSE 控制器
@RestController
@RequestMapping("/api/sse")
public class SseController {

    private final Map<String, SseEmitter> emitters = new ConcurrentHashMap<>();

    // 建立 SSE 连接
    @GetMapping(value = "/connect", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter connect(@RequestParam String userId) {
        // 设置超时时间（0 表示永不超时，或设置较大值）
        SseEmitter emitter = new SseEmitter(0L);

        // 连接完成回调
        emitter.onCompletion(() -> {
            emitters.remove(userId);
            log.info("SSE 连接完成: {}", userId);
        });

        // 连接超时回调
        emitter.onTimeout(() -> {
            emitters.remove(userId);
            log.info("SSE 连接超时: {}", userId);
        });

        // 连接错误回调
        emitter.onError(e -> {
            emitters.remove(userId);
            log.error("SSE 连接错误: {}", userId, e);
        });

        emitters.put(userId, emitter);

        // 立即发送一条连接成功消息
        try {
            emitter.send(SseEmitter.event()
                .name("connected")
                .data(Map.of("message", "连接成功", "userId", userId)));
        } catch (IOException e) {
            emitter.completeWithError(e);
        }

        return emitter;
    }

    // 向指定用户推送消息
    @PostMapping("/send/{userId}")
    public ResponseEntity<Void> sendToUser(@PathVariable String userId,
                                           @RequestBody Message message) {
        SseEmitter emitter = emitters.get(userId);
        if (emitter != null) {
            try {
                emitter.send(SseEmitter.event()
                    .name(message.getType())
                    .id(String.valueOf(System.currentTimeMillis()))
                    .data(message));
                return ResponseEntity.ok().build();
            } catch (IOException e) {
                emitters.remove(userId);
                return ResponseEntity.status(500).build();
            }
        }
        return ResponseEntity.notFound().build();
    }

    // 广播消息
    @PostMapping("/broadcast")
    public ResponseEntity<Void> broadcast(@RequestBody Message message) {
        List<String> disconnected = new ArrayList<>();
        emitters.forEach((userId, emitter) -> {
            try {
                emitter.send(SseEmitter.event()
                    .name(message.getType())
                    .data(message));
            } catch (IOException e) {
                disconnected.add(userId);
            }
        });
        disconnected.forEach(emitters::remove);
        return ResponseEntity.ok().build();
    }
}
```

### 3. SSE 心跳机制

```java
// 定时发送心跳，防止连接被代理断开
@Component
public class SseHeartbeatScheduler {

    @Autowired
    private Map<String, SseEmitter> emitters;

    @Scheduled(fixedRate = 30000)  // 每 30 秒发送心跳
    public void sendHeartbeat() {
        List<String> disconnected = new ArrayList<>();
        emitters.forEach((userId, emitter) -> {
            try {
                emitter.send(SseEmitter.event()
                    .name("heartbeat")
                    .data(Map.of("timestamp", System.currentTimeMillis())));
            } catch (IOException e) {
                disconnected.add(userId);
            }
        });
        disconnected.forEach(emitters::remove);
    }
}
```

### 4. Vue3 SSE 前端实现

```typescript
// composables/useSSE.ts
import { ref, onUnmounted } from 'vue'

export function useSSE(url: string) {
  const messages = ref<any[]>([])
  const connected = ref(false)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 10
  let eventSource: EventSource | null = null

  const connect = () => {
    eventSource = new EventSource(url)

    // 连接成功
    eventSource.onopen = () => {
      connected.value = true
      reconnectAttempts.value = 0
      console.log('SSE 连接成功')
    }

    // 默认消息（无 event 名）
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        messages.value.push(data)
      } catch (e) {
        messages.value.push({ raw: event.data })
      }
    }

    // 自定义事件
    eventSource.addEventListener('connected', (event: any) => {
      console.log('连接确认:', JSON.parse(event.data))
    })

    eventSource.addEventListener('notification', (event: any) => {
      const data = JSON.parse(event.data)
      // 处理通知
    })

    eventSource.addEventListener('heartbeat', () => {
      // 心跳，无需处理
    })

    // 连接错误（浏览器会自动重连）
    eventSource.onerror = () => {
      connected.value = false
      reconnectAttempts.value++
      if (reconnectAttempts.value >= maxReconnectAttempts) {
        eventSource?.close()
        console.error('SSE 重连次数超限')
      }
    }
  }

  const disconnect = () => {
    eventSource?.close()
    connected.value = false
  }

  onUnmounted(() => {
    disconnect()
  })

  return { messages, connected, connect, disconnect }
}
```

```vue
<!-- 使用 SSE 的组件 -->
<template>
  <div>
    <button @click="connect">连接</button>
    <button @click="disconnect">断开</button>
    <p>状态: {{ connected ? '已连接' : '未连接' }}</p>
    <ul>
      <li v-for="(msg, i) in messages" :key="i">{{ msg }}</li>
    </ul>
  </div>
</template>

<script setup>
import { useSSE } from '@/composables/useSSE'
const { messages, connected, connect, disconnect } = useSSE('/api/sse/connect?userId=123')
</script>
```

---

## 三、WebSocket 实战

### 1. WebSocket 原理

**WebSocket** 通过 HTTP 握手升级为 WS 协议，建立持久化的全双工连接，客户端和服务端可随时互相发送数据。

```text
WebSocket 握手：
客户端 → 服务端：
GET /ws HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

服务端 → 客户端：
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

### 2. Spring Boot WebSocket 实现

```java
// WebSocket 配置
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        // 注册端点，客户端连接地址
        registry.addEndpoint("/ws")
            .setAllowedOriginPatterns("*")  // 生产环境明确指定域名
            .withSockJS();  // 支持 SockJS 降级
    }

    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        // 客户端发送消息的前缀
        registry.setApplicationDestinationPrefixes("/app");
        // 服务端推送消息的前缀
        registry.enableSimpleBroker("/topic", "/queue");
        // 用户点对点消息前缀
        registry.setUserDestinationPrefix("/user");
    }
}
```

```java
// WebSocket 控制器
@Controller
public class WebSocketController {

    @Autowired
    private SimpMessagingTemplate messagingTemplate;

    // 客户端发送到 /app/chat
    @MessageMapping("/chat")
    @SendTo("/topic/messages")  // 广播到所有订阅者
    public ChatMessage handleChat(ChatMessage message) {
        message.setTimestamp(LocalDateTime.now());
        return message;
    }

    // 点对点消息
    @MessageMapping("/private")
    public void handlePrivate(PrivateMessage message) {
        // 推送到指定用户
        messagingTemplate.convertAndSendToUser(
            message.getToUserId(),
            "/queue/messages",
            message
        );
    }

    // 服务端主动推送
    public void pushNotification(String userId, Notification notification) {
        messagingTemplate.convertAndSendToUser(
            userId,
            "/queue/notifications",
            notification
        );
    }
}
```

### 3. WebSocket 拦截器（认证）

```java
// 握手拦截器，获取用户信息
public class AuthHandshakeInterceptor implements HandshakeInterceptor {

    @Override
    public boolean beforeHandshake(ServerHttpRequest request,
                                   ServerHttpResponse response,
                                   WebSocketHandler wsHandler,
                                   Map<String, Object> attributes) {
        // 从 URL 参数或 Cookie 获取 Token
        String token = request.getURI().getQuery();
        // 解析 Token，获取用户信息
        String userId = parseToken(token);
        if (userId == null) {
            return false;  // 拒绝连接
        }
        attributes.put("userId", userId);
        return true;
    }

    @Override
    public void afterHandshake(ServerHttpRequest request,
                               ServerHttpResponse response,
                               WebSocketHandler wsHandler,
                               Exception exception) {
    }
}

// 注册拦截器
@Override
public void registerStompEndpoints(StompEndpointRegistry registry) {
    registry.addEndpoint("/ws")
        .addInterceptors(new AuthHandshakeInterceptor())
        .withSockJS();
}
```

### 4. Vue3 WebSocket 前端实现

```typescript
// composables/useWebSocket.ts
import { ref, onUnmounted } from 'vue'
import SockJS from 'sockjs-client'
import { Client, IMessage } from '@stomp/stompjs'

export function useWebSocket(url: string) {
  const connected = ref(false)
  const messages = ref<any[]>([])
  let client: Client | null = null
  let reconnectTimer: number | null = null
  const maxReconnectAttempts = 10
  let reconnectAttempts = 0

  const connect = (token: string) => {
    client = new Client({
      webSocketFactory: () => new SockJS(`${url}?token=${token}`),
      reconnectDelay: 5000,  // 自动重连间隔
      heartbeatIncoming: 10000,  // 接收心跳
      heartbeatOutgoing: 10000,  // 发送心跳
      onConnect: () => {
        connected.value = true
        reconnectAttempts = 0
        console.log('WebSocket 连接成功')

        // 订阅广播消息
        client?.subscribe('/topic/messages', (message: IMessage) => {
          messages.value.push(JSON.parse(message.body))
        })

        // 订阅个人消息
        client?.subscribe('/user/queue/messages', (message: IMessage) => {
          messages.value.push(JSON.parse(message.body))
        })

        // 订阅个人通知
        client?.subscribe('/user/queue/notifications', (message: IMessage) => {
          // 处理通知
        })
      },
      onDisconnect: () => {
        connected.value = false
        console.log('WebSocket 断开')
      },
      onStompError: (frame) => {
        console.error('STOMP 错误:', frame.headers['message'])
      },
      onWebSocketClose: () => {
        connected.value = false
        attemptReconnect(token)
      },
      onWebSocketError: (error) => {
        console.error('WebSocket 错误:', error)
      }
    })

    client.activate()
  }

  const attemptReconnect = (token: string) => {
    if (reconnectAttempts >= maxReconnectAttempts) {
      console.error('重连次数超限')
      return
    }
    reconnectAttempts++
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000)  // 指数退避
    reconnectTimer = window.setTimeout(() => {
      connect(token)
    }, delay)
  }

  // 发送消息
  const send = (destination: string, body: any) => {
    if (client?.connected) {
      client.publish({
        destination,
        body: JSON.stringify(body)
      })
    }
  }

  const disconnect = () => {
    if (reconnectTimer) clearTimeout(reconnectTimer)
    client?.deactivate()
    connected.value = false
  }

  onUnmounted(() => {
    disconnect()
  })

  return { connected, messages, connect, disconnect, send }
}
```

```vue
<!-- 聊天组件 -->
<template>
  <div>
    <div>状态: {{ connected ? '已连接' : '未连接' }}</div>
    <input v-model="input" @keyup.enter="sendMessage" />
    <button @click="sendMessage">发送</button>
    <ul>
      <li v-for="(msg, i) in messages" :key="i">
        {{ msg.from }}: {{ msg.content }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useWebSocket } from '@/composables/useWebSocket'

const { connected, messages, connect, send } = useWebSocket('/ws')
const input = ref('')

const sendMessage = () => {
  send('/app/chat', { content: input.value, from: 'user1' })
  input.value = ''
}

connect('user-token')
</script>
```

---

## 四、联调要点

### 1. CORS 配置

```java
// SSE CORS 配置（SSE 是 HTTP，需要 CORS）
@Configuration
public class CorsConfig {
    @Bean
    public CorsFilter corsFilter() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of("https://app.example.com"));
        config.setAllowedMethods(List.of("GET", "POST"));
        config.setAllowedHeaders(List.of("*"));
        config.setAllowCredentials(true);
        // SSE 需要暴露的响应头
        config.setExposedHeaders(List.of("Content-Type", "Cache-Control"));

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/sse/**", config);
        return new CorsFilter(source);
    }
}

// WebSocket CORS（握手时配置）
registry.addEndpoint("/ws")
    .setAllowedOriginPatterns("https://app.example.com")  // 不要用 *
    .withSockJS();
```

### 2. Nginx 代理配置

```nginx
# SSE 代理配置
location /api/sse/ {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Connection '';  # 重要：不关闭连接
    proxy_buffering off;             # 重要：关闭缓冲，实时推送
    proxy_cache off;
    proxy_read_timeout 86400s;       # 长时间连接不超时
    chunked_transfer_encoding off;
}

# WebSocket 代理配置
location /ws {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;      # 重要：升级协议
    proxy_set_header Connection "upgrade";       # 重要：升级连接
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;
}
```

### 3. 认证方式

| 方式 | SSE | WebSocket | 说明 |
|------|-----|-----------|------|
| **URL 参数 Token** | ✅ | ✅ | 简单，但 Token 暴露在 URL/日志 |
| **Cookie** | ✅ | ✅ | 自动携带，需 SameSite 配置 |
| **Authorization 头** | ❌（EventSource 不支持自定义头） | ✅（STOMP 头） | SSE 不支持 |
| **查询参数** | ✅ | ✅ | 最常用，需 HTTPS |

> **SSE 认证注意**：原生 EventSource 不支持自定义请求头，只能通过 URL 参数或 Cookie 传递 Token。

### 4. 消息格式约定

```json
// 统一消息格式
{
  "type": "notification",      // 消息类型
  "id": "msg_001",             // 消息 ID（用于去重/断点续传）
  "timestamp": 1693000000000,  // 时间戳
  "data": {                    // 消息内容
    "title": "新消息",
    "content": "您有一条新通知"
  }
}
```

---

## 五、心跳与重连

### 1. 心跳机制

| 方案 | 说明 | 间隔 |
|------|------|------|
| **服务端心跳** | 服务端定期发送心跳包 | 20-30 秒 |
| **客户端心跳** | 客户端定期发送 ping | 20-30 秒 |
| **STOMP 心跳** | STOMP 协议内置心跳 | 可配置 |

```java
// WebSocket 心跳（STOMP 配置）
@Override
public void configureWebSocketTransport(WebSocketTransportRegistration registry) {
    registry.setHeartbeatValue(new long[]{10000, 10000});  // 读写心跳 10 秒
    registry.setTimeToFirstMessage(60000);
}
```

### 2. 断线重连策略

```typescript
// 指数退避重连
function calculateDelay(attempt: number): number {
  const base = 1000           // 基础 1 秒
  const max = 30000           // 最大 30 秒
  const delay = Math.min(base * Math.pow(2, attempt), max)
  return delay + Math.random() * 1000  // 加随机抖动，避免惊群
}
```

### 3. 消息补发

```text
断线重连后消息补发：
1. 客户端记录最后收到的消息 ID（lastEventId）
2. 重连时携带 lastEventId
3. 服务端查询 lastEventId 之后的消息
4. 补发缺失消息

SSE 原生支持：
- 服务端发送 id 字段
- 断线重连时浏览器自动发送 Last-Event-ID 头
- 服务端根据 Last-Event-ID 补发消息
```

---

## 六、安全与性能

### 1. 安全措施

- [ ] **认证授权**：连接时验证 Token，未认证拒绝连接
- [ ] **消息鉴权**：每条消息验证用户权限
- [ ] **输入验证**：验证消息内容，防止注入
- [ ] **消息大小限制**：限制单条消息大小（如 64KB）
- [ ] **频率限制**：限制用户发送消息频率
- [ ] **连接数限制**：限制单用户连接数（如 3 个）
- [ ] **WSS/HTTPS**：生产环境使用加密传输
- [ ] **Origin 校验**：校验请求 Origin，防止跨站 WebSocket

### 2. 性能优化

- [ ] **连接池管理**：定期清理失效连接
- [ ] **消息批量**：高频消息合并发送
- [ ] **消息压缩**：大消息使用压缩（permessage-deflate）
- [ ] **房间/主题**：按主题订阅，避免全量广播
- [ ] **离线消息**：用户离线时消息存数据库，上线补发
- [ ] **水平扩展**：使用 Redis Pub/Sub 实现多实例消息同步
- [ ] **连接数监控**：监控连接数，异常告警

### 3. 分布式 WebSocket

```text
多实例 WebSocket 架构：
    Nginx (IP Hash 负载均衡)
    ├── 实例 A（用户 1, 2 连接）
    ├── 实例 B（用户 3, 4 连接）
    └── 实例 C（用户 5, 6 连接）
            ↕ Redis Pub/Sub
    实例 A 收到用户 1 发消息给用户 4
    → 发布到 Redis Channel
    → 实例 B 收到，推送给用户 4
```

```java
// Redis Pub/Sub 实现分布式消息
@Service
public class RedisMessagePublisher {
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    public void publish(WebSocketMessage message) {
        redisTemplate.convertAndSend("ws-messages", message);
    }
}

// 订阅 Redis 消息，推送到本地连接
@Service
public class RedisMessageSubscriber {
    @Autowired
    private SimpMessagingTemplate messagingTemplate;

    @RedisListener(channel = "ws-messages")
    public void onMessage(WebSocketMessage message) {
        // 检查目标用户是否在本实例连接
        if (localConnections.containsKey(message.getToUserId())) {
            messagingTemplate.convertAndSendToUser(
                message.getToUserId(),
                "/queue/messages",
                message
            );
        }
    }
}
```

---

## 七、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **SSE 连接立即断开** | 代理缓冲 / 超时设置短 | Nginx 关闭 proxy_buffering，增大 proxy_read_timeout |
| **SSE 浏览器不自动重连** | 非 200 响应 / CORS 错误 | 检查状态码、CORS 配置、Content-Type |
| **EventSource 无法传 Token** | 原生 API 不支持自定义头 | Token 放 URL 参数或 Cookie |
| **WebSocket 握手失败** | 代理未配置 Upgrade 头 | Nginx 配置 Upgrade/Connection 头 |
| **WebSocket 连接频繁断开** | 心跳间隔太长 / 代理超时 | 缩短心跳、增大代理超时 |
| **消息丢失** | 断线期间消息未补发 | 实现消息补发（lastEventId） |
| **跨域连接失败** | CORS 未配置 / Origin 不匹配 | 配置 allowedOrigins，不要用 *（带凭证时） |
| **多实例消息不同步** | 本地内存存储连接 | Redis Pub/Sub 分布式同步 |
| **消息顺序错乱** | 异步发送 / 多线程 | 单用户单线程发送、消息序号 |
| **内存泄漏** | 连接未清理 / 监听器未移除 | onCompletion/onClose 中清理资源 |
| **SSE 中文乱码** | 编码问题 | 确保 UTF-8，Content-Type 含 charset |
| **STOMP 订阅不生效** | 路径前缀不匹配 | 检查 @MessageMapping 和 subscribe 路径 |
| **连接数暴涨** | 前端未关闭连接 / 重连风暴 | 组件卸载关闭、指数退避重连 |
| **大消息传输慢** | 消息过大 | 限制消息大小、压缩、分片传输 |
| **生产环境不安全** | 未加密 / 未认证 | WSS/HTTPS、Token 认证、权限校验 |

---

## 八、关联笔记

### 联调规范
- [[前后端联调规范与流程]] · [[CORS跨域解决方案实战]] · [[接口测试与Postman实战]]

### 后端
- [[SpringBoot-Web层设计]] · [[SpringBoot-配置管理与多环境]] · [[SpringSecurity-认证授权]]
- [[Kafka-消息队列与消费模型]] · [[Redis高级数据结构实战]]

### 前端
- [[Vue3-组合式API设计模式]] · [[Vue3-自定义Hooks封装]] · [[Axios网络请求封装]]
- [[前端工程化知识点系统梳理_优化版]]

### 安全
- [[API安全最佳实践]] · [[CSP内容安全策略]] · [[Web安全-XSS-CSRF-SQL注入]]

### 导航
- [[MOC-项目实战]] · [[MOC-前端开发]] · [[MOC-后端开发]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[前后端联调规范与流程]] 联调基础 → 学习 [[CORS跨域解决方案实战]] 跨域处理 → 深入本文 WebSocket-SSE 联调实战 → 实践 SSE 或 WebSocket 项目 → 研究 [[Kafka-消息队列与消费模型]] 异步消息 → 应用于实时通信和 AI 流式输出场景。

---

## 🔗 关联笔记

- [[MOC-项目实战]] — 返回本分类知识地图，查看更多相关文档

## 📖 前置知识

- [[前后端联调规范与流程]]
- [[CORS跨域解决方案实战]]
- [[SpringBoot-Web层设计]]

## 🏷️ 相关标签

`#联调` `#实时通信` `#原子笔记`

[[Home|🏠 返回首页]] · [[MOC-项目实战|📚 返回分类]]
