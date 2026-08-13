---
title: Vue3 AIGC 前端应用知识点系统梳理
tags: [前端, Vue3, AIGC, 文生图, 语音, 多模态, 前端应用, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# Vue3 AIGC 前端应用知识点系统梳理（优化版）

> **文档说明**：系统梳理 Vue 3 框架下 AIGC 前端应用开发的核心技术，涵盖 AI 写作助手、图像生成器、语音交互、多模态上传、内容编辑器、Prompt 管理、导出分享等典型场景的实战实现。

---

## 1. 概述

Vue 3 是构建 AIGC 前端应用的优秀选择，Composition API 适合管理复杂的 AI 交互状态，Element Plus 等组件库可快速搭建界面。典型 AIGC 前端应用包括：AI 写作助手、图像生成器、语音对话、多模态分析、内容编辑器等。

**典型 AIGC 前端应用类型**：

| 应用类型 | 核心能力 | 关键技术 |
|----------|----------|----------|
| **AI 写作助手** | 文本生成、润色、续写、翻译 | 流式渲染、Markdown 编辑器、Prompt 模板 |
| **图像生成器** | 文生图、图生图、风格迁移 | 图像上传、Canvas 处理、画廊展示 |
| **语音助手** | 语音输入、语音输出 | Web Speech API、音频播放、波形可视化 |
| **多模态分析** | 图像/视频/文档理解 | 文件上传、预览、多模态 API |
| **内容编辑器** | AI 辅助写作、智能补全 | 富文本编辑器、Slate/Tiptap、AI 工具栏 |

---

## 2. AI 写作助手

### 2.1 写作助手核心布局

```vue
<script setup lang="ts">
import { ref, computed } from 'vue';
import { useChat } from '@ai-sdk/vue';

const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
  api: '/api/writer',
});

const writingMode = ref<'article' | 'summary' | 'translate' | 'polish'>('article');
const tone = ref('professional');
const wordCount = ref(800);

const systemPrompt = computed(() => {
  const prompts = {
    article: `你是一位${tone.value}风格的作家，请撰写约${wordCount.value}字的文章`,
    summary: '你是一位编辑，请将以下内容精简为摘要',
    translate: '你是一位翻译，请将以下内容翻译为英文',
    polish: '你是一位文字润色专家，请优化以下文本的表达',
  };
  return prompts[writingMode.value];
});
</script>

<template>
  <div class="writer-app">
    <!-- 左侧控制面板 -->
    <aside class="control-panel">
      <h3>写作模式</h3>
      <el-radio-group v-model="writingMode">
        <el-radio-button value="article">写文章</el-radio-button>
        <el-radio-button value="summary">摘要</el-radio-button>
        <el-radio-button value="translate">翻译</el-radio-button>
        <el-radio-button value="polish">润色</el-radio-button>
      </el-radio-group>

      <h3>风格</h3>
      <el-select v-model="tone">
        <el-option label="专业" value="professional" />
        <el-option label="通俗" value="casual" />
        <el-option label="幽默" value="humorous" />
      </el-select>

      <h3>字数</h3>
      <el-slider v-model="wordCount" :min="200" :max="3000" :step="100" />
    </aside>

    <!-- 中间编辑区 -->
    <main class="editor-area">
      <textarea
        :value="input"
        @input="handleInputChange"
        placeholder="输入写作主题或内容..."
        class="editor"
      />
      <button @click="handleSubmit" :disabled="isLoading">
        {{ isLoading ? '生成中...' : '✨ AI 生成' }}
      </button>
    </main>

    <!-- 右侧结果区 -->
    <aside class="result-panel">
      <div v-for="msg in messages.filter(m => m.role === 'assistant')" :key="msg.id">
        <MarkdownRenderer :content="msg.content" />
        <button @click="copyToClipboard(msg.content)">复制</button>
        <button @click="exportMarkdown(msg.content)">导出</button>
      </div>
    </aside>
  </div>
</template>
```

### 2.2 智能续写（Inline Completion）

```vue
<script setup lang="ts">
import { ref } from 'vue';
import { useCompletion } from '@ai-sdk/vue';

const { completion, complete, isLoading } = useCompletion({ api: '/api/complete' });
const editorRef = ref<HTMLTextAreaElement | null>(null);

async function inlineComplete() {
  const text = editorRef.value?.value || '';
  const cursorPos = editorRef.value?.selectionStart || text.length;
  const prefix = text.slice(0, cursorPos);
  await complete(prefix);
}
</script>

<template>
  <div class="inline-editor">
    <textarea ref="editorRef" class="editor" />
    <button @click="inlineComplete" :disabled="isLoading">
      {{ isLoading ? '续写中...' : 'Tab 续写' }}
    </button>
    <!-- 灰色预览补全 -->
    <div v-if="completion" class="completion-preview">{{ completion }}</div>
  </div>
</template>
```

---

## 3. AI 图像生成器

### 3.1 文生图核心组件

```vue
<script setup lang="ts">
import { ref } from 'vue';

const prompt = ref('');
const negativePrompt = ref('low quality, blurry');
const imageSize = ref('1024x1024');
const style = ref('vivid');
const generatedImages = ref<string[]>([]);
const isGenerating = ref(false);

async function generate() {
  isGenerating.value = true;
  try {
    const res = await fetch('/api/generate-image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: prompt.value,
        negative_prompt: negativePrompt.value,
        size: imageSize.value,
        style: style.value,
        n: 4,  // 一次生成4张
      }),
    });
    const data = await res.json();
    generatedImages.value = data.urls;
  } finally {
    isGenerating.value = false;
  }
}

function downloadImage(url: string) {
  const a = document.createElement('a');
  a.href = url;
  a.download = `ai-image-${Date.now()}.png`;
  a.click();
}
</script>

<template>
  <div class="image-generator">
    <!-- Prompt 输入区 -->
    <div class="prompt-section">
      <el-input
        v-model="prompt"
        type="textarea"
        :rows="3"
        placeholder="描述你想生成的图像，越详细越好..."
      />
      <el-input
        v-model="negativePrompt"
        type="textarea"
        :rows="2"
        placeholder="负面提示词（不想出现的内容）..."
      />
      <div class="controls">
        <el-select v-model="imageSize">
          <el-option label="1:1 (1024x1024)" value="1024x1024" />
          <el-option label="16:9 (1792x1024)" value="1792x1024" />
          <el-option label="9:16 (1024x1792)" value="1024x1792" />
        </el-select>
        <el-select v-model="style">
          <el-option label="生动" value="vivid" />
          <el-option label="自然" value="natural" />
        </el-select>
        <el-button type="primary" @click="generate" :loading="isGenerating">
          🎨 生成图像
        </el-button>
      </div>
    </div>

    <!-- 图像画廊 -->
    <div class="image-gallery">
      <div v-for="(img, idx) in generatedImages" :key="idx" class="image-card">
        <img :src="img" :alt="prompt" />
        <div class="image-actions">
          <el-button size="small" @click="downloadImage(img)">下载</el-button>
          <el-button size="small" @click="prompt = img">用作参考</el-button>
        </div>
      </div>
      <!-- 加载骨架屏 -->
      <div v-if="isGenerating" class="skeleton-card" v-for="i in 4" :key="i">
        <el-skeleton :rows="5" animated />
      </div>
    </div>
  </div>
</template>
```

### 3.2 图生图（图像上传 + 编辑）

```vue
<script setup lang="ts">
import { ref } from 'vue';

const sourceImage = ref<string | null>(null);
const editPrompt = ref('');

function handleFileUpload(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      sourceImage.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
}

async function editImage() {
  const formData = new FormData();
  formData.append('image', dataURLtoBlob(sourceImage.value!));
  formData.append('prompt', editPrompt.value);

  const res = await fetch('/api/edit-image', {
    method: 'POST',
    body: formData,
  });
  const data = await res.json();
  return data.url;
}

function dataURLtoBlob(dataURL: string): Blob {
  const arr = dataURL.split(',');
  const mime = arr[0].match(/:(.*?);/)?.[1];
  const bstr = atob(arr[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);
  while (n--) u8arr[n] = bstr.charCodeAt(n);
  return new Blob([u8arr], { type: mime });
}
</script>

<template>
  <div class="image-editor">
    <!-- 上传区域 -->
    <div class="upload-area" @click="$refs.fileInput.click()">
      <input ref="fileInput" type="file" accept="image/*" hidden @change="handleFileUpload" />
      <img v-if="sourceImage" :src="sourceImage" />
      <div v-else class="upload-placeholder">
        点击或拖拽上传图片
      </div>
    </div>
    <!-- 编辑提示 -->
    <el-input v-model="editPrompt" placeholder="描述你想如何修改这张图..." />
    <el-button @click="editImage">✨ AI 编辑</el-button>
  </div>
</template>
```

---

## 4. 语音交互

### 4.1 语音输入（ASR）

```vue
<script setup lang="ts">
import { ref, onUnmounted } from 'vue';

const isRecording = ref(false);
const transcript = ref('');
let recognition: any = null;

function startRecording() {
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert('浏览器不支持语音识别');
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = 'zh-CN';
  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.onresult = (event: any) => {
    transcript.value = Array.from(event.results)
      .map((r: any) => r[0].transcript)
      .join('');
  };

  recognition.onerror = (e: any) => {
    console.error('语音识别错误:', e.error);
    stopRecording();
  };

  recognition.start();
  isRecording.value = true;
}

function stopRecording() {
  recognition?.stop();
  isRecording.value = false;
}

onUnmounted(() => recognition?.stop());
</script>

<template>
  <div class="voice-input">
    <button
      :class="['mic-btn', { recording: isRecording }]"
      @click="isRecording ? stopRecording() : startRecording()"
    >
      <span class="mic-icon">🎤</span>
      {{ isRecording ? '正在录音...' : '点击说话' }}
    </button>
    <div class="transcript">{{ transcript }}</div>
  </div>
</template>

<style scoped>
.recording {
  background: #ef4444;
  animation: pulse 1s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
</style>
```

### 4.2 语音输出（TTS）

```typescript
// composables/useSpeech.ts
import { ref } from 'vue';

export function useSpeech() {
  const isSpeaking = ref(false);
  const voices = ref<SpeechSynthesisVoice[]>([]);

  // 加载可用语音
  function loadVoices() {
    voices.value = speechSynthesis.getVoices();
  }
  speechSynthesis.onvoiceschanged = loadVoices;
  loadVoices();

  function speak(text: string, options?: {
    lang?: string;
    rate?: number;
    pitch?: number;
    voice?: SpeechSynthesisVoice;
  }) {
    speechSynthesis.cancel();  // 停止之前的
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = options?.lang || 'zh-CN';
    utterance.rate = options?.rate || 1.0;
    utterance.pitch = options?.pitch || 1.0;
    if (options?.voice) utterance.voice = options.voice;

    utterance.onstart = () => { isSpeaking.value = true; };
    utterance.onend = () => { isSpeaking.value = false; };

    speechSynthesis.speak(utterance);
  }

  function stop() {
    speechSynthesis.cancel();
    isSpeaking.value = false;
  }

  return { isSpeaking, voices, speak, stop };
}
```

### 4.3 音频波形可视化

```vue
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const canvasRef = ref<HTMLCanvasElement | null>(null);
let audioContext: AudioContext | null = null;
let analyser: AnalyserNode | null = null;
let animationId: number;

async function startVisualization(stream: MediaStream) {
  audioContext = new AudioContext();
  const source = audioContext.createMediaStreamSource(stream);
  analyser = audioContext.createAnalyser();
  analyser.fftSize = 256;
  source.connect(analyser);
  draw();
}

function draw() {
  if (!canvasRef.value || !analyser) return;
  const canvas = canvasRef.value;
  const ctx = canvas.getContext('2d')!;
  const bufferLength = analyser.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);
  analyser.getByteFrequencyData(dataArray);

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const barWidth = canvas.width / bufferLength;
  let x = 0;
  for (let i = 0; i < bufferLength; i++) {
    const barHeight = (dataArray[i] / 255) * canvas.height;
    ctx.fillStyle = `hsl(${i * 2}, 70%, 50%)`;
    ctx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight);
    x += barWidth;
  }
  animationId = requestAnimationFrame(draw);
}

onUnmounted(() => {
  cancelAnimationFrame(animationId);
  audioContext?.close();
});
</script>

<template>
  <canvas ref="canvasRef" width="400" height="100" class="waveform" />
</template>
```

---

## 5. 多模态文件上传与预览

### 5.1 拖拽上传组件

```vue
<script setup lang="ts">
import { ref } from 'vue';

const isDragging = ref(false);
const files = ref<File[]>([]);
const previews = ref<string[]>([]);

function handleDragOver(e: DragEvent) {
  e.preventDefault();
  isDragging.value = true;
}

function handleDragLeave() {
  isDragging.value = false;
}

function handleDrop(e: DragEvent) {
  e.preventDefault();
  isDragging.value = false;
  const droppedFiles = Array.from(e.dataTransfer?.files || []);
  addFiles(droppedFiles);
}

function addFiles(newFiles: File[]) {
  files.value.push(...newFiles);
  newFiles.forEach(file => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => previews.value.push(e.target?.result as string);
      reader.readAsDataURL(file);
    }
  });
}

const emit = defineEmits<{ upload: [files: File[]] }>();

async function upload() {
  const formData = new FormData();
  files.value.forEach(f => formData.append('files', f));
  await fetch('/api/multimodal', { method: 'POST', body: formData });
  emit('upload', files.value);
}
</script>

<template>
  <div
    :class="['drop-zone', { dragging: isDragging }]"
    @dragover="handleDragOver"
    @dragleave="handleDragLeave"
    @drop="handleDrop"
  >
    <input type="file" multiple accept="image/*,audio/*,video/*,.pdf" hidden
           @change="addFiles(Array.from(($event.target as HTMLInputElement).files || []))" />
    <div class="drop-hint">
      📁 拖拽文件到此处，或点击选择
      <small>支持图片、音频、视频、PDF</small>
    </div>
    <!-- 预览 -->
    <div class="preview-grid">
      <img v-for="(p, i) in previews" :key="i" :src="p" class="preview-thumb" />
    </div>
    <el-button v-if="files.length" type="primary" @click="upload">
      上传并分析 ({{ files.length }})
    </el-button>
  </div>
</template>
```

### 5.2 PDF 预览

```bash
pnpm add pdfjs-dist
```

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import * as pdfjsLib from 'pdfjs-dist';

const pdfUrl = ref('');
const numPages = ref(0);
const currentPage = ref(1);
const canvasRef = ref<HTMLCanvasElement | null>(null);

onMounted(async () => {
  pdfjsLib.GlobalWorkerOptions.workerSrc = 'pdfjs-dist/build/pdf.worker.min.js';
  const pdf = await pdfjsLib.getDocument(pdfUrl.value).promise;
  numPages.value = pdf.numPages;
  renderPage(1);
});

async function renderPage(pageNum: number) {
  const pdf = await pdfjsLib.getDocument(pdfUrl.value).promise;
  const page = await pdf.getPage(pageNum);
  const viewport = page.getViewport({ scale: 1.5 });
  const canvas = canvasRef.value!;
  const context = canvas.getContext('2d')!;
  canvas.height = viewport.height;
  canvas.width = viewport.width;
  await page.render({ canvasContext: context, viewport }).promise;
}
</script>
```

---

## 5.3 图像编辑（Inpaint / Outpaint）

```vue
<script setup lang="ts">
import { ref } from 'vue';

const sourceImage = ref<string | null>(null);
const maskImage = ref<string | null>(null);
const isDrawing = ref(false);
const canvasRef = ref<HTMLCanvasElement | null>(null);
const ctx = ref<CanvasRenderingContext2D | null>(null);

// 初始化画布
function initCanvas() {
  const canvas = canvasRef.value!;
  ctx.value = canvas.getContext('2d');
  // 加载原图
  const img = new Image();
  img.onload = () => {
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.value!.drawImage(img, 0, 0);
  };
  img.src = sourceImage.value!;
}

// 绘制遮罩（Inpaint 区域）
function startDraw(e: MouseEvent) {
  isDrawing.value = true;
  ctx.value!.beginPath();
  ctx.value!.moveTo(e.offsetX, e.offsetY);
}

function draw(e: MouseEvent) {
  if (!isDrawing.value) return;
  ctx.value!.strokeStyle = 'rgba(255, 0, 0, 0.5)';
  ctx.value!.lineWidth = 20;
  ctx.value!.lineTo(e.offsetX, e.offsetY);
  ctx.value!.stroke();
}

function endDraw() {
  isDrawing.value = false;
  // 生成 mask
  maskImage.value = canvasRef.value!.toDataURL();
}

// Inpaint：局部重绘
async function inpaint(prompt: string) {
  const formData = new FormData();
  formData.append('image', dataURLtoBlob(sourceImage.value!));
  formData.append('mask', dataURLtoBlob(maskImage.value!));
  formData.append('prompt', prompt);

  const res = await fetch('/api/inpaint', { method: 'POST', body: formData });
  return (await res.json()).url;
}

// Outpaint：扩图
async function outpaint(prompt: string, direction: 'left' | 'right' | 'up' | 'down') {
  const res = await fetch('/api/outpaint', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: sourceImage.value, prompt, direction }),
  });
  return (await res.json()).url;
}
</script>

<template>
  <div class="image-editor">
    <canvas
      ref="canvasRef"
      @mousedown="startDraw"
      @mousemove="draw"
      @mouseup="endDraw"
      @mouseleave="endDraw"
    />
    <div class="edit-controls">
      <el-input v-model="editPrompt" placeholder="描述你想修改的内容..." />
      <el-button @click="inpaint(editPrompt)">🎨 局部重绘</el-button>
      <el-button @click="outpaint(editPrompt, 'right')">➡️ 向右扩图</el-button>
    </div>
  </div>
</template>
```

---

## 5.4 Prompt 历史与风格预设

```typescript
// composables/usePromptHistory.ts
import { ref, watch } from 'vue';

interface PromptRecord {
  id: string;
  prompt: string;
  negativePrompt?: string;
  style?: string;
  size?: string;
  timestamp: number;
  resultImage?: string;
}

const MAX_HISTORY = 50;

export function usePromptHistory() {
  const history = ref<PromptRecord[]>(
    JSON.parse(localStorage.getItem('prompt_history') || '[]')
  );

  function addRecord(record: Omit<PromptRecord, 'id' | 'timestamp'>) {
    history.value.unshift({
      ...record,
      id: Date.now().toString(),
      timestamp: Date.now(),
    });
    if (history.value.length > MAX_HISTORY) {
      history.value = history.value.slice(0, MAX_HISTORY);
    }
    save();
  }

  function clearHistory() {
    history.value = [];
    save();
  }

  function save() {
    localStorage.setItem('prompt_history', JSON.stringify(history.value));
  }

  return { history, addRecord, clearHistory };
}

// 风格预设
export const STYLE_PRESETS = [
  { name: '写实摄影', prompt: 'photorealistic, 8k, professional photography, DSLR' },
  { name: '动漫风格', prompt: 'anime style, studio ghibli, vibrant colors' },
  { name: '油画风格', prompt: 'oil painting, classical art, textured brushstrokes' },
  { name: '水彩风格', prompt: 'watercolor painting, soft colors, artistic' },
  { name: '赛博朋克', prompt: 'cyberpunk, neon lights, futuristic, dystopian' },
  { name: '极简主义', prompt: 'minimalist, clean, simple, white background' },
  { name: '3D 渲染', prompt: '3d render, octane render, cinematic lighting' },
  { name: '像素艺术', prompt: 'pixel art, 16-bit, retro game style' },
];
```

---

## 5.5 批量生成与队列管理

```vue
<script setup lang="ts">
import { ref, computed } from 'vue';

interface GenerateTask {
  id: string;
  prompt: string;
  status: 'pending' | 'generating' | 'done' | 'error';
  result?: string;
  progress?: number;
}

const tasks = ref<GenerateTask[]>([]);
const maxConcurrent = 2;

const pendingCount = computed(() => tasks.value.filter(t => t.status === 'pending').length);
const generatingCount = computed(() => tasks.value.filter(t => t.status === 'generating').length);

async function batchGenerate(prompts: string[]) {
  prompts.forEach(prompt => {
    tasks.value.push({
      id: Date.now().toString() + Math.random(),
      prompt,
      status: 'pending',
    });
  });
  processQueue();
}

async function processQueue() {
  while (generatingCount.value < maxConcurrent && pendingCount.value > 0) {
    const task = tasks.value.find(t => t.status === 'pending');
    if (!task) break;
    task.status = 'generating';
    generateSingle(task);
  }
}

async function generateSingle(task: GenerateTask) {
  try {
    const res = await fetch('/api/generate-image', {
      method: 'POST',
      body: JSON.stringify({ prompt: task.prompt }),
    });
    const data = await res.json();
    task.result = data.url;
    task.status = 'done';
  } catch (e) {
    task.status = 'error';
  } finally {
    processQueue();  // 处理下一个
  }
}
</script>

<template>
  <div class="batch-generator">
    <div class="queue-stats">
      等待: {{ pendingCount }} | 生成中: {{ generatingCount }} | 完成: {{ tasks.filter(t => t.status === 'done').length }}
    </div>
    <div class="task-list">
      <div v-for="task in tasks" :key="task.id" :class="['task', task.status]">
        <span class="prompt">{{ task.prompt.slice(0, 50) }}...</span>
        <span class="status">{{ task.status }}</span>
        <img v-if="task.result" :src="task.result" class="thumb" />
      </div>
    </div>
  </div>
</template>
```

---

## 5.6 PWA 离线与分享

```typescript
// PWA 配置（vite-plugin-pwa）
// vite.config.ts
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico'],
      manifest: {
        name: 'AIGC 创作平台',
        short_name: 'AIGC',
        description: 'AI 生成内容创作平台',
        theme_color: '#4f46e5',
        icons: [
          { src: 'icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.example\.com\/.*/,
            handler: 'NetworkFirst',
            options: { cacheName: 'api-cache' },
          },
        ],
      },
    }),
  ],
});

// 分享功能（Web Share API）
async function shareContent(title: string, text: string, url?: string) {
  if (navigator.share) {
    // 原生分享（移动端）
    await navigator.share({ title, text, url });
  } else {
    // 复制链接
    await navigator.clipboard.writeText(url || text);
    alert('链接已复制到剪贴板');
  }
}
```

---

## 6. Prompt 模板管理

### 6.1 Prompt 模板库

```typescript
// composables/usePromptTemplates.ts
import { ref } from 'vue';

interface PromptTemplate {
  id: string;
  name: string;
  category: string;
  template: string;
  variables: string[];
}

const templates = ref<PromptTemplate[]>([
  {
    id: '1',
    name: '技术文章生成',
    category: '写作',
    template: '你是一位资深技术作家。请以{style}风格写一篇关于{topic}的文章，约{wordCount}字。',
    variables: ['style', 'topic', 'wordCount'],
  },
  {
    id: '2',
    name: '代码审查',
    category: '编程',
    template: '请审查以下代码，指出潜在问题和优化建议：\n\n{code}',
    variables: ['code'],
  },
]);

export function usePromptTemplates() {
  function fillTemplate(template: PromptTemplate, variables: Record<string, string>): string {
    return template.template.replace(/\{(\w+)\}/g, (_, key) => variables[key] || `{${key}}`);
  }

  function saveTemplate(template: PromptTemplate) {
    const saved = JSON.parse(localStorage.getItem('prompt_templates') || '[]');
    saved.push(template);
    localStorage.setItem('prompt_templates', JSON.stringify(saved));
  }

  return { templates, fillTemplate, saveTemplate };
}
```

---

## 7. 导出与分享

### 7.1 导出 Markdown/PDF

```typescript
// 导出 Markdown
function exportMarkdown(content: string, filename: string) {
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${filename}.md`;
  a.click();
  URL.revokeObjectURL(url);
}

// 导出 PDF（html2canvas + jspdf）
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

async function exportPDF(elementId: string, filename: string) {
  const element = document.getElementById(elementId)!;
  const canvas = await html2canvas(element, { scale: 2 });
  const imgData = canvas.toDataURL('image/png');
  const pdf = new jsPDF('p', 'mm', 'a4');
  const imgWidth = 210;
  const imgHeight = (canvas.height * imgWidth) / canvas.width;
  pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
  pdf.save(`${filename}.pdf`);
}
```

### 7.2 分享链接

```typescript
// 生成分享链接（内容编码到 URL）
function generateShareLink(content: string): string {
  const encoded = btoa(unescape(encodeURIComponent(content)));
  return `${window.location.origin}/share/${encoded}`;
}

// 解析分享内容
function parseShareLink(hash: string): string {
  return decodeURIComponent(escape(atob(hash)));
}
```

---

## 8. 面试高频考点

1. **AI 写作助手架构**：三栏布局、模式切换、流式生成、导出
2. **图像生成器**：Prompt/负面Prompt、尺寸选择、多图生成、画廊展示、下载
3. **图生图**：文件上传、FileReader、base64 预览、FormData 提交
4. **图像编辑**：Inpaint 局部重绘（Canvas遮罩）、Outpaint 扩图、mask 生成
5. **语音输入**：Web Speech API、SpeechRecognition、continuous/interimResults
6. **语音输出**：SpeechSynthesisUtterance、voices、rate/pitch、cancel
7. **音频可视化**：AudioContext、AnalyserNode、getByteFrequencyData、Canvas
8. **多模态上传**：拖拽上传、DragEvent、文件预览、PDF.js
9. **Prompt 模板**：变量替换、模板库管理、localStorage 持久化
10. **Prompt 历史**：记录生成参数、localStorage 存储、风格预设、快速复用
11. **批量生成**：任务队列、并发控制、状态管理、进度展示
12. **智能续写**：useCompletion、Inline 补全、灰色预览
13. **导出功能**：Blob/URL.createObjectURL 导出 MD、html2canvas+jsPDF 导出 PDF
14. **PWA 离线**：vite-plugin-pwa、Service Worker、离线缓存、可安装
15. **分享功能**：Web Share API（移动端原生）、复制链接降级
16. **内容编辑器**：Tiptap/Slate 富文本、AI 工具栏、协同编辑
17. **性能优化**：图片懒加载、虚拟滚动、防抖、Web Worker
18. **错误处理**：生成失败重试、超时提示、降级方案
19. **响应式设计**：移动端适配、Element Plus 组件、断点布局
20. **安全**：XSS 防护、文件类型校验、大小限制、用户输入转义

---

## 📝 精简总结

- Vue3 AIGC 前端应用五大类型：AI写作助手、图像生成器、语音助手、多模态分析、内容编辑器
- AI写作助手：三栏布局（控制面板+编辑器+结果）、模式切换（文章/摘要/翻译/润色）、useChat流式生成、Markdown渲染导出
- 图像生成器：Prompt+负面Prompt、尺寸/风格选择、一次生成多图、画廊展示、下载/用作参考、el-skeleton加载态
- 图生图：拖拽/点击上传、FileReader base64预览、dataURLtoBlob、FormData提交编辑
- 图像编辑：Inpaint局部重绘（Canvas绘制遮罩mask）、Outpaint扩图（上下左右方向）、mask与原图一起提交API
- 语音输入：Web Speech API SpeechRecognition、zh-CN、continuous+interimResults、录音按钮脉冲动画
- 语音输出：SpeechSynthesisUtterance、onvoiceschanged加载语音、rate/pitch/voice、speak/cancel
- 音频可视化：AudioContext+AnalyserNode+getByteFrequencyData、Canvas绘制频谱柱状图、requestAnimationFrame
- 多模态上传：拖拽（dragover/dragleave/drop）、文件预览（图片base64）、PDF.js预览、FormData多文件上传
- Prompt模板管理：变量替换（正则{var}）、模板分类、localStorage持久化、自定义模板
- Prompt历史与风格预设：记录生成参数+结果图、localStorage存储（最多50条）、8种风格预设（写实/动漫/油画/水彩/赛博朋克/极简/3D/像素）、一键复用
- 批量生成：任务队列（pending/generating/done/error）、maxConcurrent并发控制、自动处理下一个、进度展示
- 智能续写：useCompletion、光标位置prefix、灰色预览补全、Tab接受
- 导出分享：Blob导出Markdown、html2canvas+jsPDF导出PDF、Web Share API移动端原生分享、复制链接降级
- PWA离线：vite-plugin-pwa、Service Worker、NetworkFirst缓存API、可安装到桌面、离线访问
- 性能优化：图片懒加载、虚拟滚动、防抖输入、Web Worker处理大文件
- 安全：XSS防护（不直接v-html用户内容）、文件类型/大小校验、输入转义
- 最佳实践：Element Plus快速搭界面、Composition API管理状态、流式输出提升体验、错误重试降级、PWA+批量生成+风格预设提升体验

---

[[01-前端开发/MOC-前端开发|← 返回前端开发 MOC]] | [[Home|🏠 返回首页]]
