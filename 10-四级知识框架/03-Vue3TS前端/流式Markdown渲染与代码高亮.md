---
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
