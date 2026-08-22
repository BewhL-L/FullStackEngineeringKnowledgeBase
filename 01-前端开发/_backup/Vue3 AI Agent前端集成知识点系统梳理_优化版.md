---
title: Vue3 AI Agent 前端集成知识点系统梳理
tags: [前端, Vue3, AIAgent, 前端集成, useChat, 流式渲染, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# Vue3 AI Agent 前端集成知识点系统梳理（优化版）

> **文档说明**：系统梳理 Vue 3 框架下 AI Agent 前端集成的核心技术，涵盖 Vercel AI SDK 集成、流式渲染、对话管理、工具调用可视化、Markdown 渲染、代码高亮、状态管理、性能优化等实战内容。

---

## 1. 概述

Vue 3 与 AI Agent 集成的核心是构建流畅的对话式交互界面。前端负责：对话状态管理、流式输出渲染、工具调用可视化、Markdown/代码高亮、用户输入处理、错误处理与重试。后端（Node.js/Java/Python）负责 LLM 调用和工具执行，前后端通过 SSE 流式通信。

**前后端架构**：

```
┌─────────────┐     SSE 流式      ┌──────────────┐     API      ┌──────────┐
│  Vue 3 前端  │ ◄──────────────► │  后端 API     │ ◄──────────► │  LLM     │
│  (useChat)  │   对话/工具状态   │ (streamText) │              │  Agent   │
└─────────────┘                  └──────────────┘              └──────────┘
       │                                │
       │ 工具结果展示                     │ 工具调用执行
       ▼                                ▼
  工具UI组件                      天气/搜索/数据库等
```

---

## 2. Vercel AI SDK + Vue 3 集成

### 2.1 安装与配置

```bash
pnpm add ai @ai-sdk/vue @ai-sdk/openai
```

### 2.2 useChat 核心用法

```vue
<script setup lang="ts">
import { useChat } from '@ai-sdk/vue';
import { ref } from 'vue';

const {
  messages,           // 消息列表（响应式）
  input,              // 输入框绑定值
  handleInputChange,  // input 事件处理
  handleSubmit,       // 表单提交处理
  isLoading,          // 是否正在生成
  error,              // 错误信息
  reload,             // 重新生成上一条
  stop,               // 停止生成
  append,             // 手动追加消息
  setMessages,        // 设置消息列表
} = useChat({
  api: '/api/chat',   // 后端 API 地址
  headers: { 'Authorization': 'Bearer xxx' },
  body: { userId: '123' },  // 额外请求体
  initialMessages: [
    { id: '1', role: 'system', content: '你是一个有用的助手' }
  ],
  onFinish: (message) => {
    console.log('生成完成:', message);
  },
  onError: (error) => {
    console.error('出错:', error);
  },
});

// 发送消息
function send() {
  handleSubmit();
}

// 清空对话
function clearChat() {
  setMessages([]);
}
</script>

<template>
  <div class="chat-container">
    <!-- 消息列表 -->
    <div class="messages">
      <div
        v-for="msg in messages"
        :key="msg.id"
        :class="['message', msg.role]"
      >
        <div class="avatar">{{ msg.role === 'user' ? '我' : 'AI' }}</div>
        <div class="content">
          <!-- Markdown 渲染 -->
          <MarkdownRenderer :content="msg.content" />
          <!-- 工具调用展示 -->
          <ToolCalls v-if="msg.toolInvocations" :invocations="msg.toolInvocations" />
        </div>
      </div>
      <!-- 加载指示器 -->
      <div v-if="isLoading" class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    </div>

    <!-- 输入区域 -->
    <form @submit.prevent="handleSubmit" class="input-area">
      <input
        :value="input"
        @input="handleInputChange"
        placeholder="输入消息..."
        :disabled="isLoading"
        @keydown.enter.exact.prevent="handleSubmit"
      />
      <button type="submit" :disabled="isLoading || !input.trim()">
        {{ isLoading ? '生成中...' : '发送' }}
      </button>
      <button v-if="isLoading" @click="stop" type="button">停止</button>
    </form>

    <!-- 错误提示 -->
    <div v-if="error" class="error-banner">
      {{ error.message }}
      <button @click="reload">重试</button>
    </div>
  </div>
</template>
```

### 2.3 useCompletion（补全模式）

```typescript
import { useCompletion } from '@ai-sdk/vue';

const {
  completion,    // 当前补全文本
  complete,      // 触发补全
  isLoading,
  stop,
} = useCompletion({
  api: '/api/completion',
});

// 代码补全示例
function autoComplete(prefix: string) {
  complete(prefix);
}
```

> 🔍 **知识点深度解析**
>
> **作用**：useChat 是 Vue 3 AI 对话应用的核心钩子，封装了消息管理、流式接收、输入处理、错误处理等全部逻辑。
>
> **原理**：useChat 内部维护响应式的 messages 数组，调用 handleSubmit 时向 api 发送 POST 请求（body 含 messages），后端返回 SSE 数据流。useChat 通过 fetch + ReadableStream 逐块解析响应，每收到一个 token 就更新对应 AI 消息的 content，触发 Vue 响应式重新渲染。工具调用通过消息的 toolInvocations 字段传递，前端可展示工具名称、参数和结果。isLoading 在请求期间为 true，error 捕获异常，reload 重新发送上一条用户消息，stop 中止 fetch 请求。
>
> **用法要点**：① 后端必须用 streamText + toDataStreamResponse 返回；② messages 是 UIMessage 类型，含 id/role/content/toolInvocations；③ 输入框用 :value + @input 而非 v-model（handleInputChange 内部处理）；④ Enter 发送用 @keydown.enter.exact.prevent，Shift+Enter 换行；⑤ 面试常考：useChat 核心属性、流式渲染原理、工具调用展示、错误重试。

---

## 3. 流式渲染优化

### 3.1 自定义流式 Hook（不依赖 SDK）

```typescript
import { ref } from 'vue';

export function useStreamChat(api: string) {
  const messages = ref<Array<{ id: string; role: string; content: string }>>([]);
  const isLoading = ref(false);
  const abortController = ref<AbortController | null>(null);

  async function send(userMessage: string) {
    const userMsg = { id: Date.now().toString(), role: 'user', content: userMessage };
    const aiMsg = { id: (Date.now() + 1).toString(), role: 'assistant', content: '' };
    messages.value.push(userMsg, aiMsg);
    isLoading.value = true;

    abortController.value = new AbortController();
    try {
      const response = await fetch(api, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [...messages.value.slice(0, -1), userMsg] }),
        signal: abortController.value.signal,
      });

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        // 解析 SSE 格式
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;
            try {
              const parsed = JSON.parse(data);
              aiMsg.content += parsed.content || '';
            } catch {}
          }
        }
      }
    } finally {
      isLoading.value = false;
    }
  }

  function stop() {
    abortController.value?.abort();
    isLoading.value = false;
  }

  return { messages, isLoading, send, stop };
}
```

### 3.2 打字机效果

```vue
<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';

const props = defineProps<{ text: string; speed?: number }>();
const displayed = ref('');
let timer: number | null = null;

watch(() => props.text, (newText) => {
  if (timer) clearInterval(timer);
  let i = displayed.value.length;
  timer = window.setInterval(() => {
    if (i < newText.length) {
      displayed.value = newText.slice(0, i + 1);
      i++;
    } else {
      clearInterval(timer!);
    }
  }, props.speed || 20);
}, { immediate: true });

onUnmounted(() => { if (timer) clearInterval(timer); });
</script>

<template>
  <span>{{ displayed }}<span v-if="text !== displayed" class="cursor">|</span></span>
</template>
```

---

## 4. Markdown 渲染与代码高亮

### 4.1 markdown-it + highlight.js

```bash
pnpm add markdown-it highlight.js
pnpm add -D @types/markdown-it
```

```vue
<script setup lang="ts">
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import 'highlight.js/styles/github-dark.css';

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  highlight: (str, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="hljs"><code>${hljs.highlight(str, { language: lang }).value}</code></pre>`;
      } catch {}
    }
    return `<pre class="hljs"><code>${md.utils.escapeHtml(str)}</code></pre>`;
  },
});

const props = defineProps<{ content: string }>();
</script>

<template>
  <div class="markdown-body" v-html="md.render(content)" />
</template>

<style scoped>
.markdown-body {
  line-height: 1.7;
  word-wrap: break-word;
}
.markdown-body :deep(pre) {
  background: #1e1e1e;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
}
.markdown-body :deep(code) {
  font-family: 'Fira Code', monospace;
}
</style>
```

### 4.2 代码复制按钮

```vue
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const copied = ref(false);
const code = ref('');

function copyCode() {
  navigator.clipboard.writeText(code.value);
  copied.value = true;
  setTimeout(() => { copied.value = false; }, 2000);
}
</script>

<template>
  <div class="code-block">
    <button class="copy-btn" @click="copyCode">
      {{ copied ? '已复制' : '复制' }}
    </button>
    <pre><code>{{ code }}</code></pre>
  </div>
</template>
```

---

## 5. 工具调用可视化

### 5.1 工具调用状态展示

```vue
<script setup lang="ts">
import { computed } from 'vue';

interface ToolInvocation {
  toolName: string;
  toolCallId: string;
  state: 'call' | 'result';
  args?: Record<string, any>;
  result?: any;
}

const props = defineProps<{ invocations: ToolInvocation[] }>();

const toolIcons: Record<string, string> = {
  weather: '🌤️',
  search: '🔍',
  calculator: '🧮',
  code_interpreter: '💻',
};
</script>

<template>
  <div class="tool-calls">
    <div
      v-for="inv in invocations"
      :key="inv.toolCallId"
      class="tool-call"
    >
      <div class="tool-header">
        <span class="tool-icon">{{ toolIcons[inv.toolName] || '🔧' }}</span>
        <span class="tool-name">{{ inv.toolName }}</span>
        <span class="tool-status" :class="inv.state">
          {{ inv.state === 'call' ? '调用中...' : '已完成' }}
        </span>
      </div>
      <!-- 调用参数 -->
      <div v-if="inv.args" class="tool-args">
        <strong>参数：</strong>
        <code>{{ JSON.stringify(inv.args, null, 2) }}</code>
      </div>
      <!-- 执行结果 -->
      <div v-if="inv.result" class="tool-result">
        <strong>结果：</strong>
        <pre>{{ typeof inv.result === 'string' ? inv.result : JSON.stringify(inv.result, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>
```

### 5.2 人工确认工具（Human-in-the-loop）

```vue
<script setup lang="ts">
const props = defineProps<{
  toolName: string;
  args: Record<string, any>;
}>();
const emit = defineEmits<{
  approve: [];
  reject: [];
}>();
</script>

<template>
  <div class="tool-approval">
    <div class="warning">
      ⚠️ 工具「{{ toolName }}」需要确认
    </div>
    <div class="args">
      参数：<code>{{ JSON.stringify(args, null, 2) }}</code>
    </div>
    <div class="actions">
      <button class="approve" @click="emit('approve')">允许执行</button>
      <button class="reject" @click="emit('reject')">拒绝</button>
    </div>
  </div>
</template>
```

---

## 6. 对话管理与状态持久化

### 6.1 Pinia 对话状态管理

```typescript
// stores/chat.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
}

export const useChatStore = defineStore('chat', () => {
  const conversations = ref<Conversation[]>([]);
  const currentId = ref<string | null>(null);

  const currentConversation = computed(() =>
    conversations.value.find(c => c.id === currentId.value)
  );

  function createConversation() {
    const conv: Conversation = {
      id: Date.now().toString(),
      title: '新对话',
      messages: [],
      createdAt: Date.now(),
    };
    conversations.value.unshift(conv);
    currentId.value = conv.id;
    return conv;
  }

  function addMessage(convId: string, message: Message) {
    const conv = conversations.value.find(c => c.id === convId);
    if (conv) {
      conv.messages.push(message);
      if (conv.messages.length === 1) {
        conv.title = message.content.slice(0, 20);
      }
    }
  }

  function deleteConversation(convId: string) {
    const index = conversations.value.findIndex(c => c.id === convId);
    if (index > -1) conversations.value.splice(index, 1);
  }

  // 持久化到 localStorage
  function save() {
    localStorage.setItem('chat_conversations', JSON.stringify(conversations.value));
  }

  function load() {
    const saved = localStorage.getItem('chat_conversations');
    if (saved) conversations.value = JSON.parse(saved);
  }

  return {
    conversations, currentId, currentConversation,
    createConversation, addMessage, deleteConversation, save, load,
  };
});
```

### 6.2 对话历史侧边栏

```vue
<script setup lang="ts">
import { useChatStore } from '@/stores/chat';

const chatStore = useChatStore();
</script>

<template>
  <aside class="sidebar">
    <button class="new-chat" @click="chatStore.createConversation()">
      + 新建对话
    </button>
    <div class="conversation-list">
      <div
        v-for="conv in chatStore.conversations"
        :key="conv.id"
        :class="['conversation-item', { active: conv.id === chatStore.currentId }]"
        @click="chatStore.currentId = conv.id"
      >
        <span class="title">{{ conv.title }}</span>
        <button class="delete" @click.stop="chatStore.deleteConversation(conv.id)">
          ×
        </button>
      </div>
    </div>
  </aside>
</template>
```

---

## 6.3 WebSocket 实时通信

```typescript
// composables/useWebSocketChat.ts
import { ref, onUnmounted } from 'vue';

export function useWebSocketChat(url: string) {
  const messages = ref<any[]>([]);
  const isConnected = ref(false);
  const isLoading = ref(false);
  let ws: WebSocket | null = null;
  let currentAiMessage: any = null;

  function connect() {
    ws = new WebSocket(url);

    ws.onopen = () => {
      isConnected.value = true;
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'token') {
        // 流式 token
        if (!currentAiMessage) {
          currentAiMessage = { id: Date.now().toString(), role: 'assistant', content: '' };
          messages.value.push(currentAiMessage);
        }
        currentAiMessage.content += data.content;
      } else if (data.type === 'done') {
        currentAiMessage = null;
        isLoading.value = false;
      } else if (data.type === 'tool_call') {
        // 工具调用事件
        messages.value.push({
          id: Date.now().toString(),
          role: 'assistant',
          content: '',
          toolInvocations: [{ toolName: data.tool, args: data.args, state: 'call' }],
        });
      }
    };

    ws.onclose = () => {
      isConnected.value = false;
      // 自动重连
      setTimeout(connect, 3000);
    };
  }

  function send(message: string) {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    messages.value.push({ id: Date.now().toString(), role: 'user', content: message });
    isLoading.value = true;
    ws.send(JSON.stringify({ type: 'message', content: message }));
  }

  function disconnect() {
    ws?.close();
  }

  onUnmounted(disconnect);

  return { messages, isConnected, isLoading, connect, send, disconnect };
}
```

---

## 6.4 消息搜索与过滤

```vue
<script setup lang="ts">
import { ref, computed } from 'vue';
import { useChatStore } from '@/stores/chat';

const chatStore = useChatStore();
const searchQuery = ref('');

const filteredMessages = computed(() => {
  if (!searchQuery.value) return chatStore.currentConversation?.messages || [];
  const query = searchQuery.value.toLowerCase();
  return (chatStore.currentConversation?.messages || []).filter(
    msg => msg.content.toLowerCase().includes(query)
  );
});

// 高亮匹配文本
function highlight(text: string, query: string): string {
  if (!query) return text;
  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
}
</script>

<template>
  <div class="message-search">
    <input v-model="searchQuery" placeholder="搜索消息..." />
    <div class="search-results">
      <div v-for="msg in filteredMessages" :key="msg.id">
        <span v-html="highlight(msg.content, searchQuery)" />
      </div>
    </div>
  </div>
</template>
```

---

## 6.5 键盘快捷键

```typescript
// composables/useChatShortcuts.ts
import { onMounted, onUnmounted } from 'vue';

export function useChatShortcuts(handlers: {
  onSend: () => void;
  onNewChat: () => void;
  onStop: () => void;
  onFocusInput: () => void;
}) {
  function handleKeydown(e: KeyboardEvent) {
    // Ctrl/Cmd + Enter: 发送
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handlers.onSend();
    }
    // Ctrl/Cmd + K: 聚焦输入框
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      handlers.onFocusInput();
    }
    // Ctrl/Cmd + N: 新对话
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
      e.preventDefault();
      handlers.onNewChat();
    }
    // Escape: 停止生成
    if (e.key === 'Escape') {
      handlers.onStop();
    }
    // Ctrl/Cmd + Shift + C: 复制最后一条回复
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
      e.preventDefault();
      // 复制逻辑
    }
  }

  onMounted(() => window.addEventListener('keydown', handleKeydown));
  onUnmounted(() => window.removeEventListener('keydown', handleKeydown));
}
```

---

## 6.6 拖拽文件上传

```vue
<script setup lang="ts">
import { ref } from 'vue';

const isDragging = ref(false);
const attachedFiles = ref<File[]>([]);

function handleDragOver(e: DragEvent) {
  e.preventDefault();
  isDragging.value = true;
}

function handleDragLeave(e: DragEvent) {
  // 只在真正离开容器时触发
  if (e.currentTarget === e.target) {
    isDragging.value = false;
  }
}

function handleDrop(e: DragEvent) {
  e.preventDefault();
  isDragging.value = false;
  const files = Array.from(e.dataTransfer?.files || []);
  attachedFiles.value.push(...files);
}

function removeFile(index: number) {
  attachedFiles.value.splice(index, 1);
}

// 粘贴图片
function handlePaste(e: ClipboardEvent) {
  const items = e.clipboardData?.items;
  if (!items) return;
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      const file = item.getAsFile();
      if (file) attachedFiles.value.push(file);
    }
  }
}
</script>

<template>
  <div
    :class="['chat-input-container', { 'drag-over': isDragging }]"
    @dragover="handleDragOver"
    @dragleave="handleDragLeave"
    @drop="handleDrop"
    @paste="handlePaste"
  >
    <!-- 附件预览 -->
    <div v-if="attachedFiles.length" class="attachments">
      <div v-for="(file, i) in attachedFiles" :key="i" class="attachment">
        <span>{{ file.name }}</span>
        <button @click="removeFile(i)">×</button>
      </div>
    </div>
    <textarea placeholder="输入消息，拖拽或粘贴文件..." />
  </div>
</template>
```

---

## 7. 性能优化

### 7.1 虚拟滚动（长对话列表）

```bash
pnpm add vue-virtual-scroller
```

```vue
<script setup lang="ts">
import { DynamicScroller, DynamicScrollerItem } from 'vue-virtual-scroller';
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css';
</script>

<template>
  <DynamicScroller
    :items="messages"
    :min-item-size="80"
    class="message-list"
  >
    <template #default="{ item, index, active }">
      <DynamicScrollerItem :item="item" :active="active" :size-dependencies="[item.content.length]">
        <MessageBubble :message="item" />
      </DynamicScrollerItem>
    </template>
  </DynamicScroller>
</template>
```

### 7.2 防抖输入与自动调整高度

```typescript
import { ref } from 'vue';

export function useAutoResizeTextarea() {
  const textareaRef = ref<HTMLTextAreaElement | null>(null);

  function autoResize() {
    const el = textareaRef.value;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 200) + 'px';
  }

  return { textareaRef, autoResize };
}
```

### 7.3 消息懒加载 Markdown

```vue
<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{ content: string; visible: boolean }>();
const rendered = ref('');

watch(() => props.visible, (visible) => {
  if (visible && !rendered.value) {
    // 仅在可见时渲染 Markdown
    rendered.value = expensiveMarkdownRender(props.content);
  }
});
</script>
```

---

## 8. 面试高频考点

1. **useChat 核心**：messages/input/handleSubmit/isLoading/error/reload/stop
2. **流式渲染原理**：SSE、ReadableStream、fetch 流式读取、响应式更新
3. **Markdown 渲染**：markdown-it + highlight.js、v-html、XSS 防护
4. **代码高亮**：highlight.js、复制功能、深色主题
5. **工具调用展示**：toolInvocations、调用中/已完成状态、参数与结果展示
6. **人工确认**：Human-in-the-loop、敏感操作审批
7. **对话管理**：多会话切换、Pinia 状态管理、localStorage 持久化
8. **停止生成**：AbortController、stop 方法
9. **错误处理**：error 展示、reload 重试、降级提示
10. **性能优化**：虚拟滚动、Markdown 懒渲染、防抖输入
11. **WebSocket 通信**：实时双向通信、自动重连、流式 token、工具调用事件
12. **消息搜索**：全文搜索、高亮匹配、过滤显示
13. **键盘快捷键**：Ctrl+Enter发送、Ctrl+K聚焦、Ctrl+N新对话、Escape停止
14. **拖拽上传**：DragEvent、文件预览、粘贴图片、附件管理
15. **输入处理**：Enter 发送、Shift+Enter 换行、自动调整高度
16. **多模态输入**：图片上传、语音输入、文件附件
17. **响应式设计**：移动端适配、侧边栏折叠
18. **安全防护**：XSS 过滤（markdown-it html:false）、用户输入转义
19. **全栈联调**：前端 useChat → 后端 streamText → toDataStreamResponse
20. **状态持久化**：对话列表存 localStorage、刷新不丢失、定期 save

---

## 📝 精简总结

- Vue3 AI Agent 前端集成核心：`@ai-sdk/vue` 的 useChat 钩子，一套 API 搞定对话全流程
- useChat 属性：messages（消息列表）、input/handleInputChange（输入）、handleSubmit（发送）、isLoading、error、reload（重试）、stop（中止）、append/setMessages
- 流式渲染：后端 SSE 数据流 → fetch ReadableStream 逐块解析 → 响应式更新消息 content → Vue 自动重渲染
- 自定义流式：AbortController 控制中止、TextDecoder 解码、while 循环读取 reader
- Markdown 渲染：markdown-it 解析 + highlight.js 代码高亮 + 复制按钮，html:false 防 XSS
- 工具调用可视化：toolInvocations 字段展示工具名/参数/状态/结果，调用中动画，敏感操作人工确认
- 对话管理：Pinia store 管理多会话、currentId 切换、localStorage 持久化、自动生成标题
- WebSocket 实时通信：双向通信、自动重连（onclose 3秒后重连）、流式 token 事件、工具调用事件、心跳保活
- 消息搜索：computed 过滤、正则高亮（<mark>标签）、全文搜索、搜索结果定位
- 键盘快捷键：Ctrl+Enter发送、Ctrl+K聚焦输入、Ctrl+N新对话、Escape停止生成、Ctrl+Shift+C复制
- 拖拽上传：dragover/dragleave/drop事件、文件预览、粘贴图片（paste事件+clipboardData）、附件列表管理
- 状态持久化：对话列表存 localStorage，刷新不丢失，定期 save
- 性能优化：vue-virtual-scroller 虚拟滚动（长列表）、Markdown 懒渲染（可见时才渲染）、输入防抖
- 输入体验：Enter 发送（@keydown.enter.exact.prevent）、Shift+Enter 换行、textarea 自动调整高度
- 错误处理：error 展示错误信息、reload 重新生成、stop 中止当前生成
- 安全：markdown-it html:false 防 XSS、用户输入不直接 v-html、工具调用人工确认
- 最佳实践：useChat + Pinia 多会话 + markdown-it 渲染 + 虚拟滚动 + 工具可视化 + localStorage 持久化 + WebSocket实时 + 快捷键

---

[[01-前端开发/MOC-前端开发|← 返回前端开发 MOC]] | [[Home|🏠 返回首页]]
