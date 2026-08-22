---
title: Vue3 AIGC 前端应用知识点系统梳理
tags: [前端, Vue3, AIGC, 文生图, 语音, 多模态, 前端应用, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# Vue3 AIGC 前端应用知识点系统梳理（优化版）

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。


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


> 🔍 **知识点深度解析**
>
> **作用**：搭建 AI 写作助手的三栏式工作界面，将写作模式/风格/字数的控制、文本编辑输入、AI 结果展示三块职责分离，配合 @ai-sdk/vue 的 useChat 实现流式对话式写作。
>
> **原理**：基于 Vue 3 Composition API 用 ref 管理 writingMode/tone/wordCount 等状态，computed 根据状态拼出 systemPrompt；useChat 封装了 messages/input/handleSubmit 等，内部通过 SSE 流式接收 assistant 消息并渲染 Markdown，整个布局用 flex 三栏隔离关注点。
>
> **用法要点**：① 三栏结构：左侧 control-panel（模式/风格/字数）、中间 editor-area（textarea+提交）、右侧 result-panel（结果列表），职责清晰易维护。  ② useChat 的 api 指向后端 /api/writer，input 与 handleInputChange 双向绑定 textarea，handleSubmit 触发生成。  ③ computed 的 systemPrompt 把 写作模式/风格/字数 映射为不同系统提示词，实现「同一输入框切换多种任务」。  ④ 结果区用 messages.filter(m => m.role === 'assistant') 过滤助手消息，配合 MarkdownRenderer 渲染并支持复制/导出。  ⑤ el-radio-group/el-select/el-slider 等 Element Plus 组件快速搭建控制面板，降低样式与交互成本。  ⑥ 可扩展：把 writingMode 与后端流式接口解耦，便于接入不同模型或多轮改写。

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


> 🔍 **知识点深度解析**
>
> **作用**：在编辑器内实现「光标处自动补全」式智能续写：把光标前文本作为前缀发给模型，生成的内容以灰色预览叠加，用户按 Tab 接受。
>
> **原理**：useCompletion 提供 completion/complete/isLoading 等状态，complete(prefix) 把光标前文本提交给 /api/complete；前端拿到 completion 后作为灰色预览展示，不直接替换正文，由用户决定是否采用，从而不打断原有写作流。
>
> **用法要点**：① editorRef 用 ref 绑定 textarea，selectionStart 取出光标位置，slice(0, cursorPos) 得到前缀 prompt。  ② useCompletion 的 complete(prefix) 触发补全请求，isLoading 控制按钮文案（续写中/ Tab 续写）。  ③ completion-preview 用弱提示样式（灰色）展示，避免与已写正文混淆，体现「非侵入式补全」。  ④ 接受逻辑：用户按 Tab 时把 completion 插入光标处并清空预览，体验接近 IDE 的 Copilot。  ⑤ 可结合防抖：停止输入 N 秒后再自动 complete，减少请求频次与 token 消耗。  ⑥ 可扩展多候选：后端返回多个 completion，用户左右切换选择。


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


> 🔍 **知识点深度解析**
>
> **作用**：实现文生图（Text-to-Image）的完整前端流程：收集正/负提示词与尺寸风格参数，调用后端批量生成，画廊展示并支持下载/用作参考。
>
> **原理**：组件用 ref 收集 prompt/negativePrompt/imageSize/style，generate() 以 JSON POST 到 /api/generate-image，后端返回 urls 数组后填充 generatedImages；同时用 isGenerating 切换 el-button 的 loading 与 el-skeleton 骨架屏，提升等待体验。
>
> **用法要点**：① 正向 prompt 描述想要内容，negativePrompt（如 low quality, blurry）描述要规避内容，二者共同约束生成质量。  ② imageSize 提供 1:1/16:9/9:16 三档，style 切换 vivid/natural，对应不同模型参数。  ③ 一次 n:4 生成多张，generatedImages 数组驱动 v-for 画廊，每张可下载或「用作参考」回填 prompt。  ④ isGenerating 控制加载态：el-button :loading 与 v-if 骨架屏（el-skeleton）同步展示。  ⑤ downloadImage 用临时 a 标签 + a.click() 触发浏览器下载，文件名带 Date.now() 防重名。  ⑥ 可扩展：加种子(seed)、采样步数、refiner 等高级参数，满足专业出图需求。

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


> 🔍 **知识点深度解析**
>
> **作用**：实现图生图（Image-to-Image）：用户上传原图后，用自然语言描述修改意图，把原图与 prompt 一起提交给后端做可控编辑。
>
> **原理**：handleFileUpload 用 FileReader.readAsDataURL 把文件读成 base64 预览；提交时 dataURLtoBlob 把 base64 还原为 Blob 放入 FormData（图片二进制），连同 editPrompt 一起 POST 到 /api/edit-image，后端返回编辑后的 url。
>
> **用法要点**：① FileReader.readAsDataURL 实现本地即时预览，无需先上传即可展示原图。  ② dataURLtoBlob 解析 dataURL 的 mime 与 base64，转成 Blob 才能走 FormData 二进制上传。  ③ FormData.append('image', blob) + append('prompt', text)，后端据此做 Instruct-Image 类编辑。  ④ 上传区支持点击（input file）与拖拽（$refs.fileInput.click()）两种交互。  ⑤ editPrompt 描述「如何修改」，区别于文生图的正向 prompt，是图生图的核心输入。  ⑥ 可扩展：预览裁切框、保留蒙版区域、多轮编辑历史回溯。


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


> 🔍 **知识点深度解析**
>
> **作用**：把用户语音实时转成文字（ASR），用于替代键盘输入或作为对话入口。
>
> **原理**：基于浏览器原生 Web Speech API 的 SpeechRecognition：构造实例后设 lang='zh-CN'、continuous=true（持续识别）、interimResults=true（返回中间结果）；onresult 把 event.results 拼接成 transcript，onerror 与 onUnmounted 负责清理，避免组件卸载后麦克风仍占用。
>
> **用法要点**：① 兼容性处理：(window).SpeechRecognition || (window).webkitSpeechRecognition 适配不同浏览器前缀。  ② continuous=true 支持长句连续识别；interimResults=true 让文字随说话实时出现，体验更顺滑。  ③ onresult 中 Array.from(event.results).map(r => r[0].transcript).join('') 累积所有识别片段。  ④ 录音按钮用 :class 绑定 recording 状态，配合 CSS 脉冲动画提示正在收音。  ⑤ onUnmounted 中 recognition.stop() 防止内存泄漏与麦克风常驻。  ⑥ 降级方案：不支持时 alert 提示，并可回退到键盘输入或第三方 ASR SDK。

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


> 🔍 **知识点深度解析**
>
> **作用**：把文本合成为语音播放（TTS），让 AI 回复「读」出来，提升无障碍与陪伴感。
>
> **原理**：封装 useSpeech：用 SpeechSynthesisUtterance 承载文本与 lang/rate/pitch/voice 参数，speechSynthesis.speak() 播放；onvoiceschanged 监听语音列表加载，speak 前 cancel 上一条避免叠加，isSpeaking 反映播放状态。
>
> **用法要点**：① SpeechSynthesisUtterance(text) 构造语音任务，可设 lang/rate(语速)/pitch(音高)/voice(具体嗓音)。  ② speechSynthesis.getVoices() 获取可用嗓音，须监听 onvoiceschanged（部分浏览器异步加载）。  ③ speak 前调用 speechSynthesis.cancel() 取消上一段，避免多段语音叠播。  ④ utterance.onstart/onend 同步 isSpeaking，便于 UI 显示「正在朗读」与停止按钮。  ⑤ stop() 调 cancel() 并复位 isSpeaking，提供打断能力。  ⑥ 可扩展：根据内容情感选择不同 voice，或接入云端高质量 TTS 提升音色。

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


> 🔍 **知识点深度解析**
>
> **作用**：把麦克风或音频流的频谱实时绘制成动态波形/柱状图，提供直观的「声音可视化」反馈。
>
> **原理**：借助 Web Audio 的 AudioContext 创建 MediaStreamSource 接入 AnalyserNode（fftSize=256 决定频域分辨率）；draw() 中 getByteFrequencyData 取出各频段能量，用 Canvas 的 fillRect 按能量高低画柱状条，requestAnimationFrame 形成逐帧动画。
>
> **用法要点**：① AudioContext + createMediaStreamSource(stream) 把麦克风流接入分析链路。  ② AnalyserNode.fftSize=256 时 frequencyBinCount=128，即 128 根频谱柱。  ③ getByteFrequencyData(dataArray) 填充 0~255 的频域强度，dataArray[i]/255 归一化柱高。  ④ Canvas 用 hsl(i*2,70%,50%) 做彩虹渐变着色，波形更美观。  ⑤ requestAnimationFrame(draw) 每帧重绘，cancelAnimationFrame 在卸载时停止，audioContext.close() 释放资源。  ⑥ 可扩展：改为时域波形（getByteTimeDomainData）或圆形/粒子可视化。


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


> 🔍 **知识点深度解析**
>
> **作用**：实现支持拖拽与点击的多文件上传区，覆盖图片/音频/视频/PDF，并在上传前生成图片预览。
>
> **原理**：用 dragover/dragleave/drop 三事件管理 isDragging 高亮态，dataTransfer.files 取拖入文件；图片类文件用 FileReader 生成 base64 缩略图，非图片不预览；upload() 用 FormData 多文件 append 后 POST，并通过 defineEmits 向父级 emit('upload') 通知。
>
> **用法要点**：① dragover 必须 e.preventDefault() 才能触发 drop，否则浏览器会直接打开文件。  ② isDragging 控制拖拽高亮样式，dragleave 复位，drop 取 e.dataTransfer.files。  ③ addFiles 中对 image/* 用 FileReader.readAsDataURL 生成预览，其他类型仅入列不预览。  ④ input type=file multiple 提供点击备选上传，accept 限制可选类型。  ⑤ upload() 用 FormData 一次 append 多个文件，POST 到 /api/multimodal 做多模态分析。  ⑥ emit('upload', files) 解耦上传逻辑与父组件后续处理（如进入分析流程）。

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


> 🔍 **知识点深度解析**
>
> **作用**：在前端直接渲染 PDF 文档页面到 Canvas，支持多页浏览，避免依赖后端转换或下载打开。
>
> **原理**：引入 pdfjs-dist，设置 GlobalWorkerOptions.workerSrc 指向 worker 脚本；getDocument(pdfUrl).promise 加载文档，getPage(n) 取页，page.getViewport({scale}) 决定清晰度，page.render({canvasContext, viewport}) 把页面绘制到 canvas。
>
> **用法要点**：① pdfjs-dist 是 Mozilla 的纯前端 PDF 解析库，无需服务端即可渲染。  ② workerSrc 必须正确指向 pdf.worker.min.js，否则渲染会阻塞主线程或报错。  ③ getDocument(...).promise 返回带 numPages 的 PDFDocumentProxy，据此做分页控制。  ④ scale 参数（如 1.5）决定渲染分辨率，越大越清晰但越耗性能。  ⑤ render 返回 promise，需 await 完成后再切下一页，避免渲染竞态。  ⑥ 可扩展：加缩放、旋转、文本层选择、缩略图侧边栏。

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


> 🔍 **知识点深度解析**
>
> **作用**：提供局部重绘（Inpaint）与扩图（Outpaint）能力：用户在画布上涂出遮罩区域，模型据此重绘或向指定方向延展画面。
>
> **原理**：Canvas 上监听鼠标事件绘制红色遮罩（需 isDrawing 标志），endDraw 时 toDataURL 导出 mask；inpaint 把原图+mask+prompt 以 FormData 提交后端重绘，outpaint 则把方向参数以 JSON 提交做扩图。
>
> **用法要点**：① initCanvas 加载原图到 canvas 并保存 ctx，作为绘制遮罩的底图。  ② startDraw/moveTo 与 draw/lineTo 在 mousedown→mousemove 期间画出半透明红色遮罩。  ③ endDraw 调 canvas.toDataURL() 把遮罩区导出为图像（maskImage）。  ④ inpaint 用 dataURLtoBlob 把原图与 mask 转 Blob，FormData 提交 /api/inpaint。  ⑤ outpaint 传 direction（left/right/up/down），后端按方向扩展画布并生成新内容。  ⑥ 遮罩即「告诉模型哪里要改」，是 Inpaint 可控生成的关键输入。

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


> 🔍 **知识点深度解析**
>
> **作用**：记录每次生成的完整参数与结果，并提供一组风格预设，方便快速复用与一致性出图。
>
> **原理**：usePromptHistory 用 ref 从 localStorage 读取历史数组，addRecord 用 unshift 把新记录放最前并限长（MAX_HISTORY=50），变更后 save() 持久化；STYLE_PRESETS 是导出的一组预设 prompt 常量，供 UI 直接选用。
>
> **用法要点**：① PromptRecord 结构保存 prompt/negativePrompt/style/size/timestamp/resultImage，便于一键回填复现。  ② localStorage 做本地持久化，刷新不丢失，无需服务端存储。  ③ MAX_HISTORY=50 限制数组长度，超出 slice(0,50) 防止无限增长占用空间。  ④ addRecord 自动补 id(时间戳) 与 timestamp，unshift 使最新记录在最前。  ⑤ STYLE_PRESETS 集中管理 8 种风格 prompt（写实/动漫/油画/水彩/赛博朋克/极简/3D/像素），降低输入成本。  ⑥ 可扩展：历史支持搜索、收藏、按风格筛选、导出/导入配置。

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


> 🔍 **知识点深度解析**
>
> **作用**：把多个 prompt 放入任务队列，按并发上限逐个生成，实时展示各任务状态与进度。
>
> **原理**：tasks ref 数组保存每个任务（pending/generating/done/error）；batchGenerate 把 prompts 入队后调用 processQueue，后者在 generating 数 < maxConcurrent 时取一个 pending 任务置为 generating 并 generateSingle，完成时 finally 里再次 processQueue，形成自驱动队列。
>
> **用法要点**：① GenerateTask 状态机：pending→generating→done/error，驱动 UI 着色与进度。  ② maxConcurrent=2 限制同时进行的请求数，防止把后端/显卡打满。  ③ computed 的 pendingCount/generatingCount 实时统计，供顶部队列状态展示。  ④ processQueue 用 while 循环「有空位且有待处理」就开新任务，实现并发节流。  ⑤ generateSingle 的 finally 调 processQueue() 处理下一个，保证队列持续推进不卡死。  ⑥ 可扩展：加单任务重试、失败指数退避、进度百分比（由 SSE 或轮询获得）。

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


> 🔍 **知识点深度解析**
>
> **作用**：把 Web 应用打包成可安装、可离线的 PWA，并集成系统级分享能力，提升移动端可用性。
>
> **原理**：vite-plugin-pwa 的 VitePWA 在构建时生成 Service Worker 与 manifest：manifest 定义名称/图标/主题色，workbox.globPatterns 预缓存静态资源、runtimeCaching 对 API 用 NetworkFirst 做离线优先缓存；shareContent 用 navigator.share 调起原生分享，不支持时降级为复制链接。
>
> **用法要点**：① VitePWA registerType:'autoUpdate' 让 SW 更新后自动激活，用户无感知。  ② manifest 的 icons/theme_color 决定安装到桌面后的图标与状态栏配色。  ③ workbox.globPatterns 缓存 js/css/html 等，离线也能打开首屏。  ④ runtimeCaching 对 api.example.com 用 NetworkFirst：先请求网络，失败回退缓存，兼顾实时与离线。  ⑤ navigator.share({title,text,url}) 调起移动端系统分享面板（微信/短信等）。  ⑥ 降级：无 navigator.share 时用 clipboard.writeText 复制链接并提示，保证可用性。


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


> 🔍 **知识点深度解析**
>
> **作用**：用带变量的模板统一管理常用 Prompt，支持占位符填充与本地保存，提升复用与协作效率。
>
> **原理**：usePromptTemplates 维护 templates ref 数组（含 category/variables）；fillTemplate 用正则 /\{(\w+)\}/g 把模板中的 {var} 替换为传入变量值，未提供则保留占位；saveTemplate 把新模板 push 进 localStorage 持久化。
>
> **用法要点**：① PromptTemplate 含 id/name/category/template/variables，模板本身即「带占位符的提示词」。  ② fillTemplate 正则 /\{(\w+)\}/g 全局替换 {style}/{topic} 等变量，缺省回退 {key} 不破坏结构。  ③ variables 数组声明模板需要的入参，前端据此动态生成填表 UI。  ④ category 字段支持按「写作/编程」等分类管理，方便检索。  ⑤ saveTemplate 读 localStorage 现有数组→push→写回，实现自定义模板持久化。  ⑥ 可扩展：模板导入导出、团队协作共享、基于历史的模板推荐。


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


> 🔍 **知识点深度解析**
>
> **作用**：把 AI 生成内容导出为 Markdown 或 PDF 文件，方便留存、排版与分享。
>
> **原理**：exportMarkdown 用 Blob([content], {type:'text/markdown'}) + URL.createObjectURL 触发下载；exportPDF 用 html2canvas 把 DOM 截成 canvas，再交给 jsPDF 的 addImage 按 A4 尺寸铺满生成 PDF 并 save。
>
> **用法要点**：① Blob + URL.createObjectURL 是前端「内存文件→下载」的标准做法，用完 revokeObjectURL 释放。  ② exportMarkdown 直接以 .md 下载纯文本，保留 Markdown 结构。  ③ html2canvas(element, {scale:2}) 提高截图清晰度，把元素渲染到 canvas。  ④ jsPDF('p','mm','a4') 创建纵向 A4，imgWidth=210mm，按宽高比算 imgHeight 防拉伸。  ⑤ pdf.addImage(imgData,'PNG',0,0,imgWidth,imgHeight) 把截图写入 PDF 再 save('x.pdf')。  ⑥ 可扩展：分页截断长内容、加页眉页脚、直接打印 window.print()。

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


> 🔍 **知识点深度解析**
>
> **作用**：把生成内容直接编码进 URL，生成可一键打开/还原的分享链接，无需后端存储。
>
> **原理**：generateShareLink 用 encodeURIComponent+btoa 把 UTF-8 内容安全地 base64 进 URL path；parseShareLink 反向用 atob+decodeURIComponent(escape()) 还原，实现「链接即内容」的轻量分享。
>
> **用法要点**：① btoa(unescape(encodeURIComponent(content))) 正确处理中文等多字节字符，避免 base64 乱码。  ② 链接形如 /share/{encoded}，打开分享页时从路径或 hash 取编码串再解码。  ③ parseShareLink 用 decodeURIComponent(escape(atob(hash))) 反向还原原始文本。  ④ 优点：零后端存储，链接自带内容，适合临时/轻量分享。  ⑤ 缺点：URL 长度受浏览器限制，过长内容需改为「先上传拿 id 再分享」。  ⑥ 可扩展：对编码内容做压缩（如 lz-string）以缩短链接，或加过期签名。


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
