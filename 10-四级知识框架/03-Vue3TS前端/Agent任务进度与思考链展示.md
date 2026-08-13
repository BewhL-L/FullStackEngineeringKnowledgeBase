---
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
