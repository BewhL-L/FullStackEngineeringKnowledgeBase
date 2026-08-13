---
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
