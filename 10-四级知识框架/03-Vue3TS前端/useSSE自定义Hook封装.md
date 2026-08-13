---
title: useSSE 自定义 Hook 封装
category: Vue3TS前端
subcategory: AI交互组件
tags: [#Vue3TS/AI交互, #AI结合/流式响应, #难度/进阶, #类型/实战]
difficulty: 进阶
pre: [[Vue3-CompositionAPI深入]], [[TypeScript-类型体操高级]]
related: [[流式Markdown渲染与代码高亮]], [[FastAPI-SSE流式响应实现]]
update: 2026-08-13
status: 完善
---

# useSSE 自定义 Hook 封装

## 1. 核心概述

SSE（Server-Sent Events）是 AI 对话"打字机效果"的核心技术。前端需要一个健壮的 useSSE Hook 来处理：流式数据接收、增量拼接、错误重试、连接中止、自动清理。EventSource API 只支持 GET，生产环境通常用 fetch + ReadableStream 实现，支持 POST、自定义 Header、请求体。

**解决的场景问题**：
- AI 回答逐字显示，提升用户体验
- EventSource 不支持 POST 和自定义 Header
- 流式数据需要增量解析和拼接
- 组件卸载时需要正确中止连接
- 网络断开后需要自动重连

## 2. 底层原理/核心逻辑

### fetch + ReadableStream vs EventSource

| 特性 | EventSource | fetch + ReadableStream |
|------|-------------|------------------------|
| 请求方法 | 仅 GET | GET/POST/PUT 等 |
| 自定义 Header | 不支持 | 支持 |
| 请求体 | 不支持 | 支持（JSON） |
| 自动重连 | 支持 | 需手动实现 |
| 浏览器兼容 | 好 | 好（现代浏览器） |
| 中止连接 | close() | AbortController |

### 流式数据处理流程

```
fetch 请求 → Response.body (ReadableStream)
    ↓
getReader() → ReadableStreamDefaultReader
    ↓
reader.read() → { value: Uint8Array, done: boolean }
    ↓
TextDecoder 解码 → 字符串
    ↓
按 \n\n 分割 SSE 事件
    ↓
解析 data: 字段 → JSON
    ↓
增量拼接到响应式变量
```

### SSE 事件格式

```
data: {"content": "你"}

data: {"content": "好"}

data: [DONE]
```

## 3. 实操示例

### 基础版 useSSE

```typescript
import { ref, onUnmounted } from 'vue'

interface SSEOptions {
  url: string
  method?: 'GET' | 'POST'
  headers?: Record<string, string>
  body?: any
  onMessage?: (data: string) => void
  onError?: (error: Error) => void
  onDone?: () => void
}

export function useSSE() {
  const data = ref<string>('')
  const isLoading = ref(false)
  const error = ref<Error | null>(null)
  const isDone = ref(false)

  let abortController: AbortController | null = null

  const start = async (options: SSEOptions) => {
    data.value = ''
    error.value = null
    isDone.value = false
    isLoading.value = true

    abortController = new AbortController()

    try {
      const response = await fetch(options.url, {
        method: options.method || 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        body: options.body ? JSON.stringify(options.body) : undefined,
        signal: abortController.signal,
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // 按 SSE 事件分割（\n\n）
        const events = buffer.split('\n\n')
        buffer = events.pop() || ''

        for (const event of events) {
          const lines = event.split('\n')
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const payload = line.slice(6)
              if (payload === '[DONE]') {
                isDone.value = true
                options.onDone?.()
                break
              }
              try {
                const parsed = JSON.parse(payload)
                if (parsed.content) {
                  data.value += parsed.content
                  options.onMessage?.(parsed.content)
                }
                if (parsed.error) {
                  throw new Error(parsed.error)
                }
              } catch (e) {
                // 非 JSON 数据，直接追加
                data.value += payload
              }
            }
          }
        }
      }

      isDone.value = true
      options.onDone?.()
    } catch (e) {
      if ((e as Error).name === 'AbortError') {
        // 用户主动中止，不算错误
      } else {
        error.value = e as Error
        options.onError?.(e as Error)
      }
    } finally {
      isLoading.value = false
    }
  }

  const abort = () => {
    abortController?.abort()
    isLoading.value = false
  }

  // 组件卸载时自动中止
  onUnmounted(() => {
    abort()
  })

  return {
    data,
    isLoading,
    error,
    isDone,
    start,
    abort,
  }
}
```

### 使用示例

```vue
<template>
  <div class="chat-container">
    <div class="messages">
      <div v-for="(msg, i) in messages" :key="i" class="message">
        <div class="role">{{ msg.role }}</div>
        <div class="content">{{ msg.content }}</div>
      </div>
      <div v-if="isLoading" class="message assistant">
        <div class="content">
          {{ streamedData }}
          <span class="cursor">|</span>
        </div>
      </div>
    </div>

    <div class="input-area">
      <input v-model="input" @keyup.enter="send" placeholder="输入消息..." />
      <button @click="send" :disabled="isLoading">发送</button>
      <button v-if="isLoading" @click="abort">停止</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useSSE } from './useSSE'

const { data: streamedData, isLoading, start, abort } = useSSE()
const input = ref('')
const messages = ref<{ role: string; content: string }[]>([])

const send = async () => {
  if (!input.value.trim()) return

  const userMessage = input.value
  messages.value.push({ role: 'user', content: userMessage })
  input.value = ''

  await start({
    url: '/api/chat/stream',
    method: 'POST',
    body: {
      messages: [...messages.value, { role: 'user', content: userMessage }],
    },
    onDone: () => {
      messages.value.push({ role: 'assistant', content: streamedData.value })
    },
  })
}
</script>
```

### 增强版：支持动态参数和重试

```typescript
import { ref, onUnmounted, shallowRef } from 'vue'

interface StreamMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

interface UseStreamChatOptions {
  url: string
  model?: string
  temperature?: number
  maxTokens?: number
  headers?: Record<string, string>
  onToken?: (token: string) => void
  onComplete?: (fullText: string) => void
  onError?: (error: Error) => void
  maxRetries?: number
}

interface StreamState {
  messages: StreamMessage[]
  input: string
  isLoading: boolean
  error: Error | null
}

export function useStreamChat(defaultOptions: Partial<UseStreamChatOptions> = {}) {
  const messages = ref<StreamMessage[]>([])
  const input = ref('')
  const isLoading = ref(false)
  const error = ref<Error | null>(null)
  const streamedContent = ref('')

  let abortController: AbortController | null = null
  const maxRetries = defaultOptions.maxRetries ?? 2

  const send = async (userInput?: string, options: Partial<UseStreamChatOptions> = {}) => {
    const content = userInput ?? input.value
    if (!content.trim() || isLoading.value) return

    messages.value.push({ role: 'user', content })
    input.value = ''
    streamedContent.value = ''
    error.value = null
    isLoading.value = true

    const mergedOptions = { ...defaultOptions, ...options }
    let retries = 0

    const attempt = async (): Promise<void> => {
      abortController = new AbortController()

      try {
        const response = await fetch(mergedOptions.url!, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...mergedOptions.headers,
          },
          body: JSON.stringify({
            messages: messages.value,
            model: mergedOptions.model,
            temperature: mergedOptions.temperature,
            max_tokens: mergedOptions.maxTokens,
            stream: true,
          }),
          signal: abortController.signal,
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        const reader = response.body!.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { value, done } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const events = buffer.split('\n\n')
          buffer = events.pop() || ''

          for (const event of events) {
            const dataLine = event.split('\n').find(l => l.startsWith('data: '))
            if (!dataLine) continue

            const payload = dataLine.slice(6)
            if (payload === '[DONE]') continue

            try {
              const parsed = JSON.parse(payload)
              const token = parsed.choices?.[0]?.delta?.content ?? parsed.content ?? ''
              if (token) {
                streamedContent.value += token
                mergedOptions.onToken?.(token)
              }
            } catch {
              // 忽略解析错误
            }
          }
        }

        messages.value.push({ role: 'assistant', content: streamedContent.value })
        mergedOptions.onComplete?.(streamedContent.value)
      } catch (e) {
        if ((e as Error).name === 'AbortError') return

        if (retries < maxRetries) {
          retries++
          await new Promise(r => setTimeout(r, 1000 * retries))
          return attempt()
        }

        error.value = e as Error
        mergedOptions.onError?.(e as Error)
      } finally {
        isLoading.value = false
      }
    }

    await attempt()
  }

  const stop = () => {
    abortController?.abort()
    isLoading.value = false
  }

  const clear = () => {
    messages.value = []
    streamedContent.value = ''
    error.value = null
  }

  onUnmounted(() => {
    abortController?.abort()
  })

  return {
    messages,
    input,
    isLoading,
    error,
    streamedContent,
    send,
    stop,
    clear,
  }
}
```

### 默认解析器适配不同后端

```typescript
// 不同后端的 SSE 格式可能不同，用解析器适配
interface SSEParser {
  (rawEvent: string): { content?: string; done?: boolean; error?: string } | null
}

// OpenAI 格式解析器
export const openAIParser: SSEParser = (rawEvent) => {
  const dataLine = rawEvent.split('\n').find(l => l.startsWith('data: '))
  if (!dataLine) return null
  const payload = dataLine.slice(6)
  if (payload === '[DONE]') return { done: true }
  try {
    const parsed = JSON.parse(payload)
    return { content: parsed.choices?.[0]?.delta?.content ?? '' }
  } catch {
    return null
  }
}

// 自定义格式解析器
export const customParser: SSEParser = (rawEvent) => {
  const dataLine = rawEvent.split('\n').find(l => l.startsWith('data: '))
  if (!dataLine) return null
  const payload = dataLine.slice(6)
  if (payload === '[DONE]') return { done: true }
  try {
    const parsed = JSON.parse(payload)
    return { content: parsed.content, error: parsed.error }
  } catch {
    return { content: payload }
  }
}

// 使用
export function useSSEWithParser(parser: SSEParser = customParser) {
  // ... 在解析时调用 parser(event)
}
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 数据等到全部完成才显示 | 反向代理缓冲了响应 | 后端加 X-Accel-Buffering: no |
| 中文乱码 | 解码方式不对 | 用 TextDecoder('utf-8')，stream: true |
| 组件卸载后还在更新 | 没有中止连接 | onUnmounted 中调用 abort |
| 重试时重复追加 | 没有清空 streamedContent | 重试前重置状态 |
| 大段文字一次性出现 | 后端缓冲了输出 | 后端确保每次 yield 立即刷新 |

### 踩坑点

1. **AbortError 要单独处理**：用户主动中止不应该显示为错误
2. **buffer 要保留不完整的事件**：TCP 分片可能把一个事件拆成两包
3. **不要用 EventSource 做 POST**：它不支持，必须用 fetch
4. **流式响应的 Content-Type 要是 text/event-stream**：否则某些浏览器会缓冲

### 优化方案

- **打字机延迟**：如果 token 来得太快，可以加节流，让显示更平滑
- **预连接**：页面加载时提前建立 SSE 连接
- **离线检测**：网络断开时提示用户
- **流式 Markdown 渲染**：配合流式 Markdown 组件实时渲染

## 5. 延伸拓展方向

- [[流式Markdown渲染与代码高亮]]：流式数据的渲染
- [[AI生成内容Loading与错误态设计]]：加载和错误状态
- [[Agent任务进度与思考链展示]]：Agent 流式事件处理
- [[FastAPI-SSE流式响应实现]]：后端 SSE 实现
- [[多模态文件上传与预览]]：上传后的流式处理

## 6. 参考资料

- [MDN: Server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [MDN: ReadableStream](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream)
- [Vueuse: useFetch](https://vueuse.org/core/useFetch/)
- [SSE.js](https://github.com/mpetazzoni/sse.js)

#待完善
