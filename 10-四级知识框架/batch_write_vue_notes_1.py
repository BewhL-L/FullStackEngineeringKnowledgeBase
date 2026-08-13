# -*- coding: utf-8 -*-
"""批量写入 Vue3TS 板块前 4 篇高质量原子笔记"""
import os

BASE = r"C:\Users\23981\Desktop\AI文档\DouBao Document\全栈工程MarkDown文档\10-四级知识框架\03-Vue3TS前端"

notes = {}

# ============ 笔记3：useSSE 自定义 Hook 封装 ============
notes["useSSE自定义Hook封装.md"] = r'''---
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
'''

# ============ 笔记6：流式 Markdown 渲染与代码高亮 ============
notes["流式Markdown渲染与代码高亮.md"] = r'''---
title: 流式 Markdown 渲染与代码高亮
category: Vue3TS前端
subcategory: AI交互组件
tags: [#Vue3TS/AI交互, #AI结合/流式渲染, #难度/进阶, #类型/实战]
difficulty: 进阶
pre: [[useSSE自定义Hook封装]], [[Vue3-自定义指令与插件]]
related: [[AI生成内容Loading与错误态设计]], [[RAG检索页面设计与实现]]
update: 2026-08-13
status: 完善
---

# 流式 Markdown 渲染与代码高亮

## 1. 核心概述

AI 输出的内容通常是 Markdown 格式，需要实时渲染。流式渲染的难点在于：内容是逐字到达的，Markdown 解析器可能遇到不完整的语法（未闭合的代码块、未完成的表格），导致渲染闪烁或报错。需要特殊处理：增量渲染、不完整代码块检测、代码高亮、复制按钮。

**解决的场景问题**：
- AI 输出 Markdown，需要实时渲染为富文本
- 代码块未闭合时渲染异常
- 代码需要语法高亮
- 用户需要复制代码
- 流式内容渲染时闪烁

## 2. 底层原理/核心逻辑

### 流式渲染策略对比

| 策略 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| 全量重渲染 | 每次新 token 都重新解析整个内容 | 简单 | 大内容时性能差，闪烁 |
| 增量渲染 | 只渲染新增部分 | 性能好 | 实现复杂 |
| 分块渲染 | 按段落/代码块分割，分别渲染 | 平衡 | 需检测块边界 |
| 防抖渲染 | 攒一批再渲染 | 减少渲染次数 | 有延迟 |

### 不完整代码块处理

```
流式到达的内容可能是：
```python
def hello():
    print("Hello

此时代码块未闭合（缺少 ```），如果直接渲染会导致后面的内容都被当作代码。

解决方案：
1. 检测未闭合的代码块，临时补全 ```
2. 渲染后移除临时补全的标记
3. 或者等代码块闭合后再渲染该部分
```

### 技术选型

| 库 | 用途 | 特点 |
|----|------|------|
| marked | Markdown 解析 | 轻量、可扩展 |
| markdown-it | Markdown 解析 | 插件生态丰富 |
| highlight.js | 代码高亮 | 语言多、自动检测 |
| Prism.js | 代码高亮 | 轻量、主题多 |
| Shiki | 代码高亮 | VSCode 同款、质量高 |
| DOMPurify | XSS 防护 | 必须，防止恶意 HTML |

## 3. 实操示例

### 流式 Markdown 渲染组件

```vue
<template>
  <div class="streaming-markdown" ref="containerRef">
    <div v-html="renderedHtml" class="markdown-body"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import typescript from 'highlight.js/lib/languages/typescript'
import python from 'highlight.js/lib/languages/python'
import bash from 'highlight.js/lib/languages/bash'

// 注册需要的语言
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('js', javascript)
hljs.registerLanguage('ts', typescript)
hljs.registerLanguage('py', python)
hljs.registerLanguage('sh', bash)

const props = defineProps<{
  content: string
}>()

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
  highlight: (code, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch {
        return code
      }
    }
    return hljs.highlightAuto(code).value
  },
})

// 处理不完整的代码块
const processIncompleteCodeBlocks = (text: string): string => {
  const codeBlockRegex = /```(\w*)\n?([\s\S]*?)$/
  const match = text.match(codeBlockRegex)

  if (match && !text.endsWith('```')) {
    // 代码块未闭合，临时补全
    const lang = match[1] || ''
    const code = match[2]
    const before = text.slice(0, text.length - match[0].length)
    return before + '```' + lang + '\n' + code + '\n```'
  }
  return text
}

const renderedHtml = computed(() => {
  if (!props.content) return ''

  // 处理不完整代码块
  const processed = processIncompleteCodeBlocks(props.content)

  // 解析 Markdown
  const html = marked.parse(processed) as string

  // XSS 防护
  return DOMPurify.sanitize(html, {
    ADD_ATTR: ['target', 'rel'],
  })
})

// 渲染后高亮代码块（处理动态添加的）
const containerRef = ref<HTMLElement>()
watch(renderedHtml, () => {
  requestAnimationFrame(() => {
    containerRef.value?.querySelectorAll('pre code').forEach(block => {
      if (!(block as HTMLElement).dataset.highlighted) {
        hljs.highlightElement(block as HTMLElement)
        ;(block as HTMLElement).dataset.highlighted = 'true'
      }
    })
  })
})
</script>

<style>
.markdown-body {
  line-height: 1.6;
  word-wrap: break-word;
}
.markdown-body pre {
  background: #1e1e1e;
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  position: relative;
}
.markdown-body code {
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 14px;
}
.markdown-body pre code {
  color: #d4d4d4;
}
</style>
```

### 带复制按钮的代码块

```vue
<template>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="language">{{ language }}</span>
      <button class="copy-btn" @click="copyCode" :class="{ copied: isCopied }">
        {{ isCopied ? '已复制' : '复制' }}
      </button>
    </div>
    <pre><code :class="language" v-html="highlightedCode"></code></pre>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import hljs from 'highlight.js/lib/core'

const props = defineProps<{
  code: string
  language: string
}>()

const isCopied = ref(false)

const highlightedCode = computed(() => {
  try {
    if (props.language && hljs.getLanguage(props.language)) {
      return hljs.highlight(props.code, { language: props.language }).value
    }
    return hljs.highlightAuto(props.code).value
  } catch {
    return props.code
  }
})

const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(props.code)
    isCopied.value = true
    setTimeout(() => { isCopied.value = false }, 2000)
  } catch {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = props.code
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    isCopied.value = true
    setTimeout(() => { isCopied.value = false }, 2000)
  }
}
</script>
```

### 增量渲染 Composable

```typescript
import { ref, watch, nextTick } from 'vue'
import { marked } from 'marked'

/**
 * 增量 Markdown 渲染：按块分割，避免全量重渲染
 */
export function useIncrementalMarkdown() {
  const blocks = ref<{ type: 'text' | 'code'; content: string; lang?: string }[]>([])

  const parseBlocks = (text: string) => {
    const result: typeof blocks.value = []
    const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g

    let lastIndex = 0
    let match

    while ((match = codeBlockRegex.exec(text)) !== null) {
      // 代码块前的文本
      if (match.index > lastIndex) {
        const textBefore = text.slice(lastIndex, match.index)
        if (textBefore.trim()) {
          result.push({ type: 'text', content: textBefore })
        }
      }

      // 代码块
      result.push({
        type: 'code',
        lang: match[1] || 'text',
        content: match[2],
      })

      lastIndex = match.index + match[0].length
    }

    // 剩余文本
    if (lastIndex < text.length) {
      const remaining = text.slice(lastIndex)
      if (remaining.trim()) {
        // 检查是否有未闭合的代码块
        const unclosedMatch = remaining.match(/```(\w*)\n?([\s\S]*)$/)
        if (unclosedMatch) {
          result.push({
            type: 'code',
            lang: unclosedMatch[1] || 'text',
            content: unclosedMatch[2] + '\n',
          })
        } else {
          result.push({ type: 'text', content: remaining })
        }
      }
    }

    return result
  }

  const render = (content: string) => {
    blocks.value = parseBlocks(content)
  }

  return { blocks, render }
}
```

### 流式渲染组件（使用增量渲染）

```vue
<template>
  <div class="streaming-md">
    <template v-for="(block, i) in blocks" :key="i">
      <!-- 文本块 -->
      <div v-if="block.type === 'text'" class="text-block" v-html="renderText(block.content)"></div>

      <!-- 代码块 -->
      <CodeBlock
        v-else
        :code="block.content"
        :language="block.lang || 'text'"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { marked } from 'marked'
import { useIncrementalMarkdown } from './useIncrementalMarkdown'
import CodeBlock from './CodeBlock.vue'

const props = defineProps<{ content: string }>()

const { blocks, render } = useIncrementalMarkdown()

const renderText = (text: string) => {
  return marked.parse(text) as string
}

watch(() => props.content, (newContent) => {
  render(newContent)
}, { immediate: true })
</script>
```

### 安全过滤配置

```typescript
import DOMPurify from 'dompurify'

// 配置 DOMPurify 允许的标签和属性
DOMPurify.setConfig({
  ALLOWED_TAGS: [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'br', 'hr',
    'a', 'strong', 'em', 'del', 'u',
    'ul', 'ol', 'li',
    'blockquote', 'code', 'pre',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'img', 'div', 'span',
  ],
  ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class', 'target', 'rel'],
  ALLOW_DATA_ATTR: false,
})

// 添加自定义钩子：为链接添加 target="_blank"
DOMPurify.addHook('afterSanitizeAttributes', (node) => {
  if (node.tagName === 'A') {
    node.setAttribute('target', '_blank')
    node.setAttribute('rel', 'noopener noreferrer')
  }
})
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 代码块未闭合导致样式错乱 | 流式内容不完整 | 检测未闭合代码块，临时补全 |
| 渲染闪烁 | 每次都全量重渲染 | 用增量渲染或防抖 |
| XSS 安全风险 | Markdown 渲染为 HTML | 必须用 DOMPurify 过滤 |
| 代码高亮慢 | 大代码块高亮耗时 | Web Worker 中高亮，或用 Shiki |
| 表格渲染错位 | 表格语法不完整 | 等表格完整后再渲染 |

### 踩坑点

1. **marked 的 highlight 选项已废弃**：新版本要用 marked-highlight 扩展
2. **highlight.js 全量引入太大**：只注册需要的语言
3. **v-html 有 XSS 风险**：必须配合 DOMPurify
4. **流式内容中的表格**：表格需要完整的语法才能正确渲染，可能需要延迟渲染

### 优化方案

- **虚拟滚动**：长对话用虚拟列表渲染
- **Web Worker 高亮**：大代码块在 Worker 中处理
- **Shiki 高亮**：质量更高，支持 VSCode 主题
- **缓存渲染结果**：相同内容的渲染结果缓存

## 5. 延伸拓展方向

- [[useSSE自定义Hook封装]]：流式数据来源
- [[AI生成内容Loading与错误态设计]]：渲染中的状态
- [[RAG检索页面设计与实现]]：RAG 场景的渲染
- [[Agent任务进度与思考链展示]]：Agent 输出的特殊渲染
- [[多模态文件上传与预览]]：图片等多媒体渲染

## 6. 参考资料

- [marked](https://github.com/markedjs/marked)
- [markdown-it](https://github.com/markdown-it/markdown-it)
- [highlight.js](https://github.com/highlightjs/highlight.js)
- [Shiki](https://github.com/shikijs/shiki)
- [DOMPurify](https://github.com/cure53/DOMPurify)

#待完善
'''

# ============ 笔记9：RAG 检索页面设计与实现 ============
notes["RAG检索页面设计与实现.md"] = r'''---
title: RAG 检索页面设计与实现
category: Vue3TS前端
subcategory: AI交互组件
tags: [#Vue3TS/AI交互, #AI结合/RAG, #难度/进阶, #类型/实战]
difficulty: 进阶
pre: [[流式Markdown渲染与代码高亮]], [[Vue3-ElementPlus组件封装]]
related: [[SpringAI-RAG检索增强实现]], [[RAG文本分块策略与实践]]
update: 2026-08-13
status: 完善
---

# RAG 检索页面设计与实现

## 1. 核心概述

RAG 检索页面是 AI 知识库的核心交互界面，需要同时展示：文档列表、检索来源、对话区、引用标注。用户提问后，系统检索相关文档，AI 基于文档回答，并标注答案来自哪些文档片段，点击引用可以跳转到原文。

**解决的场景问题**：
- 用户需要知道 AI 的回答来自哪些文档
- 需要查看原文验证答案准确性
- 文档库需要浏览和管理
- 检索过程需要可视化（检索了哪些文档、相似度多少）
- 多轮对话中保持文档上下文

## 2. 底层原理/核心逻辑

### 页面布局

```
┌─────────────────────────────────────────────────┐
│  左侧：文档列表          │  右侧：对话区          │
│  - 文档树/列表          │  - 对话消息            │
│  - 搜索/筛选            │  - 引用标注 [1][2]     │
│  - 上传文档            │  - 来源面板（可折叠）   │
│                        │  - 检索时间线          │
└─────────────────────────────────────────────────┘
```

### 引用标注机制

```
AI 回答：
"Spring AI 支持多种向量数据库 [1]，包括 Milvus、PgVector 等 [2]。"

点击 [1] → 高亮显示来源文档片段
来源面板：
[1] doc-spring-ai.md (相似度 0.92)
    "Spring AI 提供了 VectorStore 抽象，支持..."
[2] doc-vectordb-comparison.md (相似度 0.88)
    "主流向量数据库对比：Milvus、PgVector、Chroma..."
```

### 数据流

```
用户提问
    ↓
前端发送请求（问题 + 对话历史）
    ↓
后端：Embedding → 向量检索 Top-K → Rerank
    ↓
返回：回答 + 引用来源（文档ID、片段、相似度）
    ↓
前端：渲染回答 + 标注引用 + 来源面板
```

## 3. 实操示例

### 引用标注组件

```vue
<template>
  <div class="cited-answer">
    <!-- 回答内容，引用标注为可点击的上标 -->
    <div class="answer-content" v-html="renderedContent"></div>

    <!-- 来源面板 -->
    <div v-if="sources.length" class="sources-panel">
      <div class="sources-header" @click="expanded = !expanded">
        <span>参考来源 ({{ sources.length }})</span>
        <el-icon><CaretBottom v-if="expanded" /><CaretRight v-else /></el-icon>
      </div>
      <div v-show="expanded" class="sources-list">
        <div
          v-for="(source, i) in sources"
          :key="i"
          class="source-item"
          :class="{ active: activeIndex === i }"
          @mouseenter="activeIndex = i"
          @click="jumpToSource(source)"
        >
          <span class="source-index">[{{ i + 1 }}]</span>
          <div class="source-info">
            <div class="source-title">{{ source.title }}</div>
            <div class="source-meta">
              <span>相似度 {{ (source.similarity * 100).toFixed(0) }}%</span>
              <span>{{ source.page ? `第 ${source.page} 页` : '' }}</span>
            </div>
            <div class="source-snippet">{{ source.snippet }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { CaretBottom, CaretRight } from '@element-plus/icons-vue'

interface Source {
  id: string
  title: string
  snippet: string
  similarity: number
  page?: number
  url?: string
}

const props = defineProps<{
  answer: string
  sources: Source[]
}>()

const expanded = ref(true)
const activeIndex = ref(-1)

// 将回答中的 [1] [2] 替换为可点击的上标
const renderedContent = computed(() => {
  let html = props.answer
  // 替换 [数字] 为上标链接
  html = html.replace(/\[(\d+)\]/g, (_, num) => {
    const index = parseInt(num) - 1
    if (index >= 0 && index < props.sources.length) {
      return `<sup class="citation" data-index="${index}">[${num}]</sup>`
    }
    return `[${num}]`
  })
  return html
})

const jumpToSource = (source: Source) => {
  if (source.url) {
    window.open(source.url, '_blank')
  }
}
</script>

<style scoped>
.cited-answer { line-height: 1.8; }
.citation {
  color: #409eff;
  cursor: pointer;
  font-size: 0.85em;
  vertical-align: super;
}
.citation:hover { text-decoration: underline; }
.sources-panel {
  margin-top: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}
.sources-header {
  padding: 10px 16px;
  background: #f5f7fa;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}
.source-item {
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  cursor: pointer;
  display: flex;
  gap: 12px;
  transition: background 0.2s;
}
.source-item:hover, .source-item.active { background: #ecf5ff; }
.source-index { color: #409eff; font-weight: 600; flex-shrink: 0; }
.source-title { font-weight: 500; color: #303133; }
.source-meta { font-size: 12px; color: #909399; margin: 4px 0; display: flex; gap: 12px; }
.source-snippet { font-size: 13px; color: #606266; line-height: 1.5; }
</style>
```

### 文档列表面板

```vue
<template>
  <div class="doc-panel">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input v-model="searchQuery" placeholder="搜索文档..." clearable>
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-button type="primary" @click="uploadVisible = true">
        <el-icon><Upload /></el-icon> 上传
      </el-button>
    </div>

    <!-- 文档列表 -->
    <div class="doc-list">
      <div
        v-for="doc in filteredDocs"
        :key="doc.id"
        class="doc-item"
        :class="{ active: selectedDocId === doc.id }"
        @click="selectDoc(doc)"
      >
        <el-icon class="doc-icon"><Document /></el-icon>
        <div class="doc-info">
          <div class="doc-name">{{ doc.name }}</div>
          <div class="doc-meta">
            <span>{{ doc.chunkCount }} 块</span>
            <span>{{ formatSize(doc.size) }}</span>
          </div>
        </div>
        <el-tag v-if="doc.status === 'indexing'" size="small" type="warning">索引中</el-tag>
        <el-tag v-else-if="doc.status === 'ready'" size="small" type="success">已就绪</el-tag>
      </div>
    </div>

    <!-- 上传对话框 -->
    <el-dialog v-model="uploadVisible" title="上传文档" width="500px">
      <el-upload
        drag
        action="/api/documents/upload"
        :multiple="true"
        :on-success="onUploadSuccess"
        accept=".pdf,.doc,.docx,.txt,.md"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽文件到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 PDF、Word、TXT、Markdown，单个文件不超过 50MB</div>
        </template>
      </el-upload>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search, Upload, Document, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

interface DocItem {
  id: string
  name: string
  size: number
  chunkCount: number
  status: 'indexing' | 'ready' | 'error'
}

const emit = defineEmits<{ select: [doc: DocItem] }>()

const docs = ref<DocItem[]>([])
const searchQuery = ref('')
const selectedDocId = ref('')
const uploadVisible = ref(false)

const filteredDocs = computed(() => {
  if (!searchQuery.value) return docs.value
  return docs.value.filter(d =>
    d.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const selectDoc = (doc: DocItem) => {
  selectedDocId.value = doc.id
  emit('select', doc)
}

const formatSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

const onUploadSuccess = () => {
  ElMessage.success('上传成功，正在索引...')
  uploadVisible.value = false
  // 刷新列表
}
</script>
```

### 检索时间线组件

```vue
<template>
  <div class="retrieval-timeline">
    <div class="timeline-header">
      <el-icon><Loading v-if="isLoading" class="spin" /></el-icon>
      <span>检索过程</span>
      <span class="duration" v-if="!isLoading">{{ totalDuration }}ms</span>
    </div>

    <el-timeline>
      <el-timeline-item
        v-for="(step, i) in steps"
        :key="i"
        :timestamp="step.duration + 'ms'"
        :type="step.status === 'done' ? 'success' : step.status === 'active' ? 'primary' : 'info'"
        :hollow="step.status === 'pending'"
      >
        <div class="step-content">
          <div class="step-title">{{ step.title }}</div>
          <div class="step-detail" v-if="step.detail">{{ step.detail }}</div>
          <div v-if="step.docs" class="step-docs">
            <el-tag
              v-for="doc in step.docs"
              :key="doc.id"
              size="small"
              class="doc-tag"
            >
              {{ doc.title }} ({{ (doc.similarity * 100).toFixed(0) }}%)
            </el-tag>
          </div>
        </div>
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Loading } from '@element-plus/icons-vue'

interface TimelineStep {
  title: string
  detail?: string
  duration?: number
  status: 'pending' | 'active' | 'done'
  docs?: { id: string; title: string; similarity: number }[]
}

defineProps<{
  steps: TimelineStep[]
  isLoading: boolean
  totalDuration: number
}>()
</script>
```

### RAG 主页面整合

```vue
<template>
  <div class="rag-page">
    <!-- 左侧文档面板 -->
    <div class="left-panel">
      <DocPanel @select="onDocSelect" />
    </div>

    <!-- 右侧对话区 -->
    <div class="right-panel">
      <!-- 消息列表 -->
      <div class="messages" ref="messagesRef">
        <div v-for="(msg, i) in messages" :key="i" class="message-item">
          <div v-if="msg.role === 'user'" class="user-message">
            {{ msg.content }}
          </div>
          <div v-else class="assistant-message">
            <CitedAnswer
              v-if="msg.sources"
              :answer="msg.content"
              :sources="msg.sources"
            />
            <StreamingMarkdown v-else :content="msg.content" />
          </div>
        </div>

        <!-- 流式输出中 -->
        <div v-if="isStreaming" class="assistant-message">
          <StreamingMarkdown :content="streamedContent" />
          <RetrievalTimeline
            v-if="showTimeline"
            :steps="retrievalSteps"
            :is-loading="isRetrieving"
            :total-duration="retrievalDuration"
          />
        </div>
      </div>

      <!-- 输入区 -->
      <div class="input-area">
        <el-input
          v-model="input"
          type="textarea"
          :rows="2"
          placeholder="输入问题，基于知识库回答..."
          @keydown.enter.exact.prevent="send"
        />
        <div class="input-actions">
          <el-checkbox v-model="useRag">使用知识库</el-checkbox>
          <el-button type="primary" @click="send" :loading="isStreaming">
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import DocPanel from './DocPanel.vue'
import CitedAnswer from './CitedAnswer.vue'
import StreamingMarkdown from './StreamingMarkdown.vue'
import RetrievalTimeline from './RetrievalTimeline.vue'
import { useStreamChat } from './useStreamChat'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
}

interface Source {
  id: string
  title: string
  snippet: string
  similarity: number
}

const messages = ref<Message[]>([])
const input = ref('')
const useRag = ref(true)
const isStreaming = ref(false)
const streamedContent = ref('')
const showTimeline = ref(true)
const isRetrieving = ref(false)
const retrievalDuration = ref(0)
const retrievalSteps = ref<any[]>([])
const messagesRef = ref<HTMLElement>()

const { send: streamSend } = useStreamChat({ url: '/api/rag/chat' })

const send = async () => {
  if (!input.value.trim()) return

  messages.value.push({ role: 'user', content: input.value })
  const question = input.value
  input.value = ''
  isStreaming.value = true
  isRetrieving.value = true
  streamedContent.value = ''

  // 模拟检索步骤
  retrievalSteps.value = [
    { title: '问题理解', status: 'done', duration: 50 },
    { title: '向量检索', status: 'active', detail: '检索 Top-10 相关文档' },
    { title: '重排序', status: 'pending' },
    { title: '生成回答', status: 'pending' },
  ]

  try {
    const response = await fetch('/api/rag/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        use_rag: useRag.value,
        history: messages.value.slice(0, -1),
      }),
    })

    // 处理流式响应...
    // 实际实现参考 useSSE

    messages.value.push({
      role: 'assistant',
      content: streamedContent.value,
      sources: [], // 从响应中提取
    })
  } finally {
    isStreaming.value = false
    isRetrieving.value = false
    await nextTick()
    messagesRef.value?.scrollTo({ top: messagesRef.value.scrollHeight })
  }
}

const onDocSelect = (doc: any) => {
  // 选中文档后，可以限定检索范围
}
</script>
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 引用标注错位 | 回答中的 [1] 和来源不对应 | 后端返回时带引用位置，前端精确渲染 |
| 来源面板太占空间 | 每次都展开 | 默认折叠，点击展开 |
| 长文档加载慢 | 一次性加载所有文档 | 分页/虚拟滚动 |
| 检索过程不透明 | 用户不知道在做什么 | 展示检索时间线 |
| 回答和来源对不上 | 检索到的文档没用上 | 后端返回实际使用的文档 |

### 踩坑点

1. **引用标注要和来源一一对应**：后端返回的引用顺序要稳定
2. **来源片段要截断**：太长的片段会撑爆面板
3. **流式输出时引用可能变化**：最终回答的引用可能和中间状态不同
4. **文档上传后要轮询索引状态**：索引是异步的

### 优化方案

- **文档预览**：点击来源后侧边栏预览原文
- **高亮匹配**：在原文中高亮和问题相关的句子
- **反馈机制**：用户可以标记引用是否有用
- **检索调试模式**：展示检索的详细过程（相似度分数、重排序前后对比）

## 5. 延伸拓展方向

- [[流式Markdown渲染与代码高亮]]：回答内容的渲染
- [[useSSE自定义Hook封装]]：流式数据接收
- [[SpringAI-RAG检索增强实现]]：后端 RAG 实现
- [[RAG文本分块策略与实践]]：分块质量影响检索
- [[Agent任务进度与思考链展示]]：Agent 模式的检索展示

## 6. 参考资料

- [Element Plus](https://element-plus.org/)
- [LangChain Chat UI](https://github.com/langchain-ai/langchain-nextjs-template)
- [Dify: Knowledge Base UI](https://github.com/langgenius/dify)
- [Notion AI: Citation UI](https://www.notion.so/product/ai)

#待完善
'''

# ============ 笔记12：Agent 任务进度与思考链展示 ============
notes["Agent任务进度与思考链展示.md"] = r'''---
title: Agent 任务进度与思考链展示
category: Vue3TS前端
subcategory: AI交互组件
tags: [#Vue3TS/AI交互, #AI结合/Agent, #难度/高级, #类型/实战]
difficulty: 高级
pre: [[useSSE自定义Hook封装]], [[Vue3-ElementPlus组件封装]]
related: [[多Agent协作模式实现]], [[AI生成内容Loading与错误态设计]]
update: 2026-08-13
status: 完善
---

# Agent 任务进度与思考链展示

## 1. 核心概述

Agent 执行任务是多步骤的：思考→调用工具→观察结果→再思考→最终回答。用户需要看到 Agent 的执行过程，而不是干等。思考链展示让用户理解 Agent 在做什么、为什么这么做、调用了什么工具、得到了什么结果，提升信任感和可解释性。

**解决的场景问题**：
- Agent 执行时间长，用户不知道进度
- 用户想知道 Agent 调用了哪些工具
- 调试时需要看 Agent 的思考过程
- 工具调用失败时需要展示错误
- 多步骤任务需要进度指示

## 2. 底层原理/核心逻辑

### Agent 执行流程

```
用户输入
    ↓
[思考] Agent 分析任务，决定下一步
    ↓
[工具调用] 调用搜索/代码/数据库等工具
    ↓
[观察] 获取工具返回结果
    ↓
[思考] 基于结果决定下一步（可能循环多次）
    ↓
[最终回答] 输出最终答案
```

### SSE 事件类型

```
event: thought
data: {"content": "我需要先搜索相关资料..."}

event: tool_call
data: {"name": "web_search", "args": {"query": "..."}}

event: tool_result
data: {"name": "web_search", "result": "...", "status": "success"}

event: token
data: {"content": "根据搜索结果..."}

event: done
data: {"content": "最终回答"}
```

### 展示模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| 折叠式 | 思考链默认折叠，点击展开 | 普通用户，简洁 |
| 时间线式 | 每步一个时间线节点 | 调试、高级用户 |
| 控制台式 | 类似终端输出 | 开发者 |
| 步骤指示器 | 顶部进度条 + 当前步骤 | 简单任务 |

## 3. 实操示例

### Agent 状态 Composable

```typescript
import { ref, computed } from 'vue'

export type StepType = 'thought' | 'tool_call' | 'tool_result' | 'answer' | 'error'

export interface AgentStep {
  id: string
  type: StepType
  content: string
  toolName?: string
  toolArgs?: Record<string, any>
  toolResult?: any
  status?: 'pending' | 'running' | 'success' | 'error'
  timestamp: number
  duration?: number
}

export function useAgent() {
  const steps = ref<AgentStep[]>([])
  const isRunning = ref(false)
  const currentAnswer = ref('')
  const error = ref<string | null>(null)

  const progress = computed(() => {
    const total = steps.value.length
    const completed = steps.value.filter(s =>
      s.status === 'success' || s.type === 'answer'
    ).length
    return total > 0 ? Math.round((completed / total) * 100) : 0
  })

  const toolCalls = computed(() =>
    steps.value.filter(s => s.type === 'tool_call')
  )

  const thoughts = computed(() =>
    steps.value.filter(s => s.type === 'thought')
  )

  const addStep = (step: Omit<AgentStep, 'id' | 'timestamp'>) => {
    steps.value.push({
      ...step,
      id: `step-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      timestamp: Date.now(),
    })
  }

  const updateLastStep = (patch: Partial<AgentStep>) => {
    const last = steps.value[steps.value.length - 1]
    if (last) {
      Object.assign(last, patch)
      if (patch.status === 'success' || patch.status === 'error') {
        last.duration = Date.now() - last.timestamp
      }
    }
  }

  const handleSseEvent = (event: string, data: any) => {
    switch (event) {
      case 'thought':
        addStep({ type: 'thought', content: data.content, status: 'success' })
        break
      case 'tool_call':
        addStep({
          type: 'tool_call',
          content: `调用工具: ${data.name}`,
          toolName: data.name,
          toolArgs: data.args,
          status: 'running',
        })
        break
      case 'tool_result':
        updateLastStep({
          type: 'tool_result',
          toolResult: data.result,
          status: data.status === 'error' ? 'error' : 'success',
        })
        break
      case 'token':
        currentAnswer.value += data.content
        break
      case 'done':
        addStep({ type: 'answer', content: data.content, status: 'success' })
        isRunning.value = false
        break
      case 'error':
        addStep({ type: 'error', content: data.message, status: 'error' })
        error.value = data.message
        isRunning.value = false
        break
    }
  }

  const reset = () => {
    steps.value = []
    currentAnswer.value = ''
    error.value = null
    isRunning.value = false
  }

  return {
    steps,
    isRunning,
    currentAnswer,
    error,
    progress,
    toolCalls,
    thoughts,
    addStep,
    updateLastStep,
    handleSseEvent,
    reset,
  }
}
```

### 思考链时间线组件

```vue
<template>
  <div class="thought-chain">
    <div class="chain-header">
      <span class="title">执行过程</span>
      <el-tag size="small" :type="isRunning ? 'primary' : 'success'">
        {{ isRunning ? '执行中...' : '已完成' }}
      </el-tag>
    </div>

    <el-timeline>
      <el-timeline-item
        v-for="step in steps"
        :key="step.id"
        :type="getStepType(step)"
        :icon="getStepIcon(step)"
        :hollow="step.status === 'pending'"
      >
        <div class="step-card" :class="step.type">
          <!-- 思考步骤 -->
          <template v-if="step.type === 'thought'">
            <div class="step-label">
              <el-icon><ChatDotRound /></el-icon> 思考
            </div>
            <div class="step-content thought-content">{{ step.content }}</div>
          </template>

          <!-- 工具调用步骤 -->
          <template v-else-if="step.type === 'tool_call' || step.type === 'tool_result'">
            <ToolCallCard :step="step" />
          </template>

          <!-- 错误步骤 -->
          <template v-else-if="step.type === 'error'">
            <div class="step-label error">
              <el-icon><Warning /></el-icon> 错误
            </div>
            <div class="step-content error-content">{{ step.content }}</div>
          </template>

          <!-- 最终回答 -->
          <template v-else-if="step.type === 'answer'">
            <div class="step-label success">
              <el-icon><CircleCheck /></el-icon> 最终回答
            </div>
          </template>
        </div>
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<script setup lang="ts">
import { ChatDotRound, Warning, CircleCheck, Loading, Tools, Search, Code } from '@element-plus/icons-vue'
import type { AgentStep } from './useAgent'
import ToolCallCard from './ToolCallCard.vue'

defineProps<{
  steps: AgentStep[]
  isRunning: boolean
}>()

const getStepType = (step: AgentStep) => {
  if (step.status === 'error') return 'danger'
  if (step.status === 'success' || step.type === 'answer') return 'success'
  if (step.status === 'running') return 'primary'
  return 'info'
}

const getStepIcon = (step: AgentStep) => {
  if (step.status === 'running') return Loading
  if (step.type === 'tool_call') return Tools
  if (step.type === 'thought') return ChatDotRound
  return undefined
}
</script>
```

### 工具调用卡片

```vue
<template>
  <div class="tool-call-card">
    <div class="tool-header" @click="expanded = !expanded">
      <el-icon class="tool-icon"><component :is="toolIcon" /></el-icon>
      <span class="tool-name">{{ step.toolName }}</span>
      <el-tag size="small" :type="statusType">{{ statusText }}</el-tag>
      <span class="duration" v-if="step.duration">{{ step.duration }}ms</span>
      <el-icon class="expand-icon"><CaretBottom v-if="expanded" /><CaretRight v-else /></el-icon>
    </div>

    <div v-show="expanded" class="tool-body">
      <!-- 输入参数 -->
      <div class="tool-section">
        <div class="section-label">输入参数</div>
        <pre class="code-block">{{ JSON.stringify(step.toolArgs, null, 2) }}</pre>
      </div>

      <!-- 输出结果 -->
      <div v-if="step.toolResult" class="tool-section">
        <div class="section-label">执行结果</div>
        <pre class="code-block result">{{ formatResult(step.toolResult) }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { CaretBottom, CaretRight, Search, Code, Database, Tools } from '@element-plus/icons-vue'
import type { AgentStep } from './useAgent'

const props = defineProps<{ step: AgentStep }>()

const expanded = ref(false)

const toolIcon = computed(() => {
  const name = props.step.toolName?.toLowerCase() || ''
  if (name.includes('search')) return Search
  if (name.includes('code') || name.includes('python')) return Code
  if (name.includes('db') || name.includes('query')) return Database
  return Tools
})

const statusType = computed(() => {
  if (props.step.status === 'running') return 'primary'
  if (props.step.status === 'error') return 'danger'
  return 'success'
})

const statusText = computed(() => {
  if (props.step.status === 'running') return '执行中'
  if (props.step.status === 'error') return '失败'
  return '成功'
})

const formatResult = (result: any) => {
  if (typeof result === 'string') return result
  return JSON.stringify(result, null, 2)
}
</script>

<style scoped>
.tool-call-card { border: 1px solid #e4e7ed; border-radius: 8px; overflow: hidden; }
.tool-header {
  padding: 10px 12px; background: #f5f7fa; cursor: pointer;
  display: flex; align-items: center; gap: 8px;
}
.tool-icon { color: #409eff; }
.tool-name { font-weight: 500; flex: 1; }
.duration { font-size: 12px; color: #909399; }
.tool-body { padding: 12px; }
.tool-section { margin-bottom: 12px; }
.section-label { font-size: 12px; color: #909399; margin-bottom: 6px; }
.code-block {
  background: #1e1e1e; color: #d4d4d4; padding: 10px; border-radius: 6px;
  font-size: 12px; overflow-x: auto; margin: 0; max-height: 200px;
}
</style>
```

### Agent 对话主组件

```vue
<template>
  <div class="agent-chat">
    <!-- 进度条 -->
    <div v-if="isRunning" class="progress-bar">
      <el-progress :percentage="progress" :show-text="false" :stroke-width="4" />
    </div>

    <!-- 消息区 -->
    <div class="messages">
      <div v-for="(msg, i) in messages" :key="i" class="message">
        <div v-if="msg.role === 'user'" class="user-msg">{{ msg.content }}</div>
        <div v-else class="assistant-msg">
          <!-- 思考链（可折叠） -->
          <ThoughtChain
            v-if="msg.steps && msg.steps.length"
            :steps="msg.steps"
            :is-running="false"
            class="thought-chain-inline"
          />
          <!-- 最终回答 -->
          <StreamingMarkdown :content="msg.content" />
        </div>
      </div>

      <!-- 当前执行中 -->
      <div v-if="isRunning" class="assistant-msg">
        <ThoughtChain :steps="steps" :is-running="true" />
        <div v-if="currentAnswer" class="streaming-answer">
          <StreamingMarkdown :content="currentAnswer" />
        </div>
      </div>
    </div>

    <!-- 输入区 -->
    <div class="input-area">
      <el-input v-model="input" placeholder="描述任务，Agent 会自动规划执行..." @keyup.enter="run" />
      <el-button type="primary" @click="run" :loading="isRunning">执行</el-button>
      <el-button v-if="isRunning" @click="stop">停止</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ThoughtChain from './ThoughtChain.vue'
import StreamingMarkdown from './StreamingMarkdown.vue'
import { useAgent, type AgentStep } from './useAgent'

interface Message {
  role: 'user' | 'assistant'
  content: string
  steps?: AgentStep[]
}

const messages = ref<Message[]>([])
const input = ref('')

const {
  steps, isRunning, currentAnswer, progress,
  handleSseEvent, reset,
} = useAgent()

const run = async () => {
  if (!input.value.trim()) return
  messages.value.push({ role: 'user', content: input.value })
  const task = input.value
  input.value = ''
  reset()
  isRunning.value = true

  try {
    const response = await fetch('/api/agent/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task }),
    })

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
        const eventType = event.match(/event: (\w+)/)?.[1] || 'message'
        const dataLine = event.split('\n').find(l => l.startsWith('data: '))
        if (dataLine) {
          try {
            const data = JSON.parse(dataLine.slice(6))
            handleSseEvent(eventType, data)
          } catch { /* ignore */ }
        }
      }
    }

    messages.value.push({
      role: 'assistant',
      content: currentAnswer.value,
      steps: [...steps.value],
    })
  } finally {
    isRunning.value = false
  }
}

const stop = () => {
  // 中止请求
}
</script>
```

### 思考链自动摘要

```typescript
/**
 * 思考链摘要：长思考链自动生成摘要，避免占用太多空间
 */
export function summarizeThoughts(steps: AgentStep[]): string {
  const thoughts = steps.filter(s => s.type === 'thought').map(s => s.content)
  const tools = steps.filter(s => s.type === 'tool_call').map(s => s.toolName)

  if (thoughts.length === 0 && tools.length === 0) return ''

  const parts: string[] = []
  if (tools.length > 0) {
    parts.push(`调用了 ${tools.length} 个工具：${[...new Set(tools)].join(', ')}`)
  }
  if (thoughts.length > 0) {
    const lastThought = thoughts[thoughts.length - 1]
    parts.push(`最后思考：${lastThought.slice(0, 100)}${lastThought.length > 100 ? '...' : ''}`)
  }

  return parts.join('；')
}
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 思考链太长占满屏幕 | Agent 思考步骤多 | 默认折叠，只展示工具调用 |
| 工具参数显示混乱 | 参数是复杂 JSON | 格式化展示，支持折叠 |
| 用户看不懂思考内容 | 思考内容太技术化 | 提供"简单模式"，只展示关键步骤 |
| 流式事件顺序错乱 | 网络延迟 | 按 event 类型和时间戳排序 |
| 工具调用结果太大 | 搜索结果返回太多 | 截断展示，支持展开查看全部 |

### 踩坑点

1. **思考内容可能包含敏感信息**：生产环境要过滤或不展示思考
2. **tool_call 和 tool_result 要配对**：用 call_id 关联
3. **流式输出时步骤会动态增加**：用 key 保证 Vue 正确更新
4. **错误步骤要醒目**：用户需要知道哪里出错了

### 优化方案

- **思考链搜索**：长思考链支持搜索定位
- **导出执行记录**：将完整执行过程导出为 JSON/Markdown
- **重放功能**：可以逐步回放 Agent 执行过程
- **性能分析**：统计每个工具的耗时，找出瓶颈

## 5. 延伸拓展方向

- [[多Agent协作模式实现]]：多 Agent 的思考链
- [[useSSE自定义Hook封装]]：SSE 事件处理
- [[AI生成内容Loading与错误态设计]]：加载和错误状态
- [[流式Markdown渲染与代码高亮]]：最终回答渲染
- [[AI工作流编排引擎设计]]：工作流的进度展示

## 6. 参考资料

- [LangChain: Agent Tracing](https://docs.smith.langchain.com/)
- [OpenAI: Assistants API](https://platform.openai.com/docs/assistants/overview)
- [LangGraph: Streaming](https://langchain-ai.github.io/langgraph/how-tos/streaming/)
- [Element Plus Timeline](https://element-plus.org/zh-CN/component/timeline.html)

#待完善
'''

# 写入文件
for filename, content in notes.items():
    filepath = os.path.join(BASE, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
    print(f"已写入: {filename} ({len(content)} 字节)")

print(f"\n共写入 {len(notes)} 篇笔记")
