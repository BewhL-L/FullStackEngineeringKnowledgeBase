---
title: AI 生成内容 Loading 与错误态设计
category: Vue3TS前端
subcategory: AI交互组件
tags: [#Vue3TS/AI交互, #AI结合/状态设计, #难度/进阶, #类型/实战]
difficulty: 进阶
pre: [[Vue3-ElementPlus组件封装]], [[useSSE自定义Hook封装]]
related: [[流式Markdown渲染与代码高亮]], [[Agent任务进度与思考链展示]]
update: 2026-08-13
status: 完善
---

# AI 生成内容 Loading 与错误态设计

## 1. 核心概述

AI 生成内容是异步的、非确定性的，Loading 和错误态设计直接影响用户体验。好的设计让用户知道"系统在工作"、"做到哪一步了"、"出了什么问题、怎么解决"。需要处理：思考中、生成中、流式输出、网络错误、模型超时、内容审核失败、自动重试等多种状态。

**解决的场景问题**：
- AI 响应慢，用户不知道是否在正常工作
- 网络中断后用户不知道发生了什么
- 错误信息太技术化，用户看不懂
- 重试机制不清晰，用户重复点击
- 流式输出中断后状态混乱

## 2. 底层原理/核心逻辑

### AI 请求生命周期

```
idle → submitting → thinking → generating → streaming → done
                ↓          ↓           ↓
              error      error       error
                ↓          ↓           ↓
              retrying → ...
```

### 状态分类

| 状态 | 说明 | 用户感知 |
|------|------|----------|
| submitting | 请求已发送，等待响应 | 按钮 loading |
| thinking | 模型正在思考（首 token 延迟） | 思考动画/三点 |
| generating | 正在生成内容 | 打字机效果 |
| streaming | 流式输出中 | 逐字显示 + 光标 |
| done | 完成 | 显示完整内容 + 操作按钮 |
| error | 出错 | 错误提示 + 重试按钮 |

### 错误分类

| 错误类型 | 原因 | 用户提示 | 处理策略 |
|----------|------|----------|----------|
| 网络错误 | 断网/超时 | "网络连接失败" | 自动重试 + 检查网络 |
| 限流错误 | 429 Too Many Requests | "请求过于频繁" | 倒计时后重试 |
| 模型错误 | 500/模型异常 | "服务暂时不可用" | 切换备用模型 |
| 内容审核 | 输出被过滤 | "内容不符合规范" | 提示修改输入 |
| 超时 | 响应时间过长 | "响应超时" | 延长超时或简化问题 |
| Token 超限 | 输入太长 | "内容过长" | 提示缩短输入 |

## 3. 实操示例

### 统一状态管理 Composable

```typescript
import { ref, computed } from 'vue'

export type AIStatus = 'idle' | 'submitting' | 'thinking' | 'streaming' | 'done' | 'error'

export interface AIError {
  type: 'network' | 'rate_limit' | 'model' | 'content_filter' | 'timeout' | 'token_limit' | 'unknown'
  message: string
  retryable: boolean
  retryAfter?: number
}

export function useAIState() {
  const status = ref<AIStatus>('idle')
  const error = ref<AIError | null>(null)
  const streamedContent = ref('')
  const retryCount = ref(0)
  const maxRetries = 3

  const isLoading = computed(() =>
    ['submitting', 'thinking', 'streaming'].includes(status.value)
  )

  const isError = computed(() => status.value === 'error')
  const isDone = computed(() => status.value === 'done')

  const setStatus = (s: AIStatus) => {
    status.value = s
  }

  const setError = (e: AIError) => {
    error.value = e
    status.value = 'error'
  }

  const appendContent = (chunk: string) => {
    streamedContent.value += chunk
    if (status.value === 'thinking') {
      status.value = 'streaming'
    }
  }

  const reset = () => {
    status.value = 'idle'
    error.value = null
    streamedContent.value = ''
    retryCount.value = 0
  }

  // 分类错误
  const classifyError = (err: any): AIError => {
    const status = err?.response?.status || err?.status
    const message = err?.message || '未知错误'

    if (status === 429) {
      return {
        type: 'rate_limit',
        message: '请求过于频繁，请稍后再试',
        retryable: true,
        retryAfter: err?.response?.headers?.['retry-after']
          ? parseInt(err.response.headers['retry-after']) * 1000
          : 3000,
      }
    }
    if (status === 400 && message.includes('maximum context length')) {
      return {
        type: 'token_limit',
        message: '输入内容过长，请缩短后重试',
        retryable: false,
      }
    }
    if (status === 403 && message.includes('content_filter')) {
      return {
        type: 'content_filter',
        message: '内容不符合规范，请修改后重试',
        retryable: false,
      }
    }
    if (status >= 500) {
      return {
        type: 'model',
        message: 'AI 服务暂时不可用',
        retryable: true,
      }
    }
    if (message.includes('timeout') || message.includes('aborted')) {
      return {
        type: 'timeout',
        message: '响应超时，请检查网络或简化问题',
        retryable: true,
      }
    }
    if (!navigator.onLine) {
      return {
        type: 'network',
        message: '网络连接失败，请检查网络设置',
        retryable: true,
      }
    }
    return { type: 'unknown', message, retryable: true }
  }

  return {
    status,
    error,
    streamedContent,
    retryCount,
    maxRetries,
    isLoading,
    isError,
    isDone,
    setStatus,
    setError,
    appendContent,
    reset,
    classifyError,
  }
}
```

### 思考动画组件

```vue
<template>
  <div class="thinking-indicator">
    <div class="thinking-dots">
      <span></span>
      <span></span>
      <span></span>
    </div>
    <span class="thinking-text">{{ text }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{ text?: string }>()
</script>

<style scoped>
.thinking-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: #909399;
}
.thinking-dots {
  display: flex;
  gap: 4px;
}
.thinking-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #409eff;
  animation: bounce 1.4s infinite ease-in-out both;
}
.thinking-dots span:nth-child(1) { animation-delay: -0.32s; }
.thinking-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>
```

### 骨架屏组件

```vue
<template>
  <div class="ai-skeleton">
    <div class="skeleton-header">
      <div class="skeleton-avatar"></div>
      <div class="skeleton-name"></div>
    </div>
    <div class="skeleton-content">
      <div class="skeleton-line" style="width: 90%"></div>
      <div class="skeleton-line" style="width: 80%"></div>
      <div class="skeleton-line" style="width: 85%"></div>
      <div class="skeleton-line" style="width: 60%"></div>
    </div>
  </div>
</template>

<style scoped>
.ai-skeleton { padding: 16px; }
.skeleton-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.skeleton-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.skeleton-name {
  width: 80px; height: 16px; border-radius: 4px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.skeleton-line {
  height: 14px; border-radius: 4px; margin-bottom: 10px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
```

### 错误提示组件

```vue
<template>
  <div class="ai-error" v-if="error">
    <el-alert
      :title="errorTitle"
      :description="error.message"
      :type="alertType"
      :closable="false"
      show-icon
    >
      <template #default>
        <div class="error-actions">
          <el-button
            v-if="error.retryable && !isRetrying"
            size="small"
            type="primary"
            @click="$emit('retry')"
          >
            重试
          </el-button>
          <el-button
            v-if="isRetrying"
            size="small"
            type="primary"
            disabled
          >
            {{ countdown }}秒后自动重试...
          </el-button>
          <el-button
            v-if="error.type === 'token_limit'"
            size="small"
            @click="$emit('shorten')"
          >
            缩短上下文
          </el-button>
          <el-button
            size="small"
            @click="$emit('copy-error')"
          >
            复制错误详情
          </el-button>
        </div>
      </template>
    </el-alert>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onUnmounted } from 'vue'
import type { AIError } from './useAIState'

const props = defineProps<{
  error: AIError | null
  isRetrying?: boolean
}>()

defineEmits<{
  retry: []
  shorten: []
  'copy-error': []
}>()

const countdown = ref(0)
let timer: number | null = null

const errorTitle = computed(() => {
  switch (props.error?.type) {
    case 'network': return '网络错误'
    case 'rate_limit': return '请求限流'
    case 'model': return '服务异常'
    case 'content_filter': return '内容审核'
    case 'timeout': return '响应超时'
    case 'token_limit': return '内容过长'
    default: return '出错了'
  }
})

const alertType = computed(() => {
  return props.error?.type === 'content_filter' ? 'warning' : 'error'
})

// 自动重试倒计时
watch(() => props.error, (err) => {
  if (err?.retryable && err.retryAfter && props.isRetrying) {
    countdown.value = Math.ceil(err.retryAfter / 1000)
    timer = window.setInterval(() => {
      countdown.value--
      if (countdown.value <= 0 && timer) {
        clearInterval(timer)
      }
    }, 1000)
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>
```

### 流式光标组件

```vue
<template>
  <span class="streaming-cursor" v-if="visible">|</span>
</template>

<script setup lang="ts">
defineProps<{ visible?: boolean }>()
</script>

<style scoped>
.streaming-cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background: #409eff;
  margin-left: 2px;
  animation: blink 1s step-end infinite;
  vertical-align: text-bottom;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
</style>
```

### 自动重试 Composable

```typescript
import { ref } from 'vue'
import type { AIError } from './useAIState'

export function useAutoRetry(maxRetries = 3) {
  const retryCount = ref(0)
  const isRetrying = ref(false)

  const shouldRetry = (error: AIError) => {
    return error.retryable && retryCount.value < maxRetries
  }

  const retry = async (fn: () => Promise<void>, error: AIError) => {
    if (!shouldRetry(error)) return false

    isRetrying.value = true
    retryCount.value++

    const delay = error.retryAfter || Math.min(1000 * Math.pow(2, retryCount.value), 10000)
    await new Promise(r => setTimeout(r, delay))

    try {
      await fn()
      isRetrying.value = false
      return true
    } catch {
      isRetrying.value = false
      return false
    }
  }

  const reset = () => {
    retryCount.value = 0
    isRetrying.value = false
  }

  return { retryCount, isRetrying, shouldRetry, retry, reset }
}
```

### AI 消息完整组件

```vue
<template>
  <div class="ai-message">
    <!-- 思考中 -->
    <ThinkingIndicator v-if="status === 'thinking'" text="AI 正在思考..." />

    <!-- 骨架屏（提交中） -->
    <AISkeleton v-else-if="status === 'submitting'" />

    <!-- 流式输出中 -->
    <div v-else-if="status === 'streaming'" class="streaming-content">
      <StreamingMarkdown :content="content" />
      <StreamingCursor :visible="true" />
    </div>

    <!-- 完成 -->
    <div v-else-if="status === 'done'" class="done-content">
      <StreamingMarkdown :content="content" />
      <div class="message-actions">
        <el-button size="small" text @click="$emit('copy')">复制</el-button>
        <el-button size="small" text @click="$emit('regenerate')">重新生成</el-button>
        <el-button size="small" text @click="$emit('like')">
          <el-icon><Star /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 错误 -->
    <AIErrorMessage
      v-else-if="status === 'error'"
      :error="error"
      :is-retrying="isRetrying"
      @retry="$emit('retry')"
      @shorten="$emit('shorten')"
    />
  </div>
</template>

<script setup lang="ts">
import ThinkingIndicator from './ThinkingIndicator.vue'
import AISkeleton from './AISkeleton.vue'
import StreamingMarkdown from './StreamingMarkdown.vue'
import StreamingCursor from './StreamingCursor.vue'
import AIErrorMessage from './AIErrorMessage.vue'
import { Star } from '@element-plus/icons-vue'
import type { AIStatus, AIError } from './useAIState'

defineProps<{
  status: AIStatus
  content: string
  error: AIError | null
  isRetrying?: boolean
}>()

defineEmits<{
  copy: []
  regenerate: []
  like: []
  retry: []
  shorten: []
}>()
</script>
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 用户以为卡死了 | 只有 loading 没有进度反馈 | 展示思考/生成步骤，加超时提示 |
| 错误后用户不知道怎么办 | 错误信息太技术化 | 分类错误，给具体操作建议 |
| 重复点击发送 | 按钮没禁用 | loading 时禁用按钮，加防抖 |
| 重试后内容重复 | 没清空之前的流式内容 | 重试前重置状态 |
| 流式中断后残留光标 | 连接断开没清理 | 错误时隐藏光标，标记中断 |

### 踩坑点

1. **首 token 延迟可能很长**：不要用普通 loading，要用"思考中"动画
2. **429 限流要读 Retry-After 头**：不要立即重试，会加剧限流
3. **AbortError 不应该显示为错误**：用户主动中止是正常操作
4. **内容审核错误不要让用户重试**：重试也会被过滤，要提示修改输入

### 优化方案

- **乐观 UI**：用户消息立即显示，不等服务端响应
- **渐进式加载**：先显示标题，再显示内容
- **离线检测**：断网时提前提示，不等请求失败
- **错误归因**：区分是用户问题还是系统问题，给不同提示

## 5. 延伸拓展方向

- [[useSSE自定义Hook封装]]：流式状态的来源
- [[流式Markdown渲染与代码高亮]]：内容渲染
- [[Agent任务进度与思考链展示]]：Agent 的进度展示
- [[语音交互ASR与TTS]]：语音场景的状态
- [[多模态文件上传与预览]]：上传场景的状态

## 6. 参考资料

- [Loading States in AI Products](https://www.nngroup.com/articles/ai-loading-states/)
- [Error Handling Best Practices](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch#error_handling)
- [Element Plus Loading](https://element-plus.org/zh-CN/component/loading.html)
- [React Query: Retry](https://tanstack.com/query/latest/docs/react/guides/query-retries)

#待完善
