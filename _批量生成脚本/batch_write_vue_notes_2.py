# -*- coding: utf-8 -*-
"""批量写入 Vue3TS 板块后 4 篇高质量原子笔记"""
import os

BASE = r"C:\Users\23981\Desktop\AI文档\DouBao Document\全栈工程MarkDown文档\10-四级知识框架\03-Vue3TS前端"

notes = {}

# ============ 笔记15：多模态文件上传与预览 ============
notes["多模态文件上传与预览.md"] = r'''---
title: 多模态文件上传与预览
category: Vue3TS前端
subcategory: AI交互组件
tags: [#Vue3TS/AI交互, #AI结合/多模态, #难度/进阶, #类型/实战]
difficulty: 进阶
pre: [[Vue3-ElementPlus组件封装]], [[TypeScript-类型体操高级]]
related: [[语音交互ASR与TTS]], [[RAG检索页面设计与实现]]
update: 2026-08-13
status: 完善
---

# 多模态文件上传与预览

## 1. 核心概述

AI 应用支持多模态输入：文本、图片、音频、视频、文档。文件上传组件需要处理：拖拽上传、大文件分片、断点续传、进度显示、格式校验、预览。不同文件类型有不同的处理逻辑：图片压缩、音频转码、文档解析。

**解决的场景问题**：
- 用户需要上传图片让 AI 识别
- 大文件（视频、PDF）上传慢，需要分片
- 上传中断后需要断点续传
- 上传前需要预览和确认
- 多种文件类型需要不同的处理

## 2. 底层原理/核心逻辑

### 文件类型处理策略

| 类型 | 扩展名 | 处理方式 | 预览方式 |
|------|--------|----------|----------|
| 图片 | jpg/png/webp/gif | 压缩、生成缩略图 | 直接显示 |
| 音频 | mp3/wav/m4a | 转码、时长检测 | 音频播放器 |
| 视频 | mp4/webm | 截取封面、压缩 | 视频播放器 |
| 文档 | pdf/docx/txt/md | 解析文本、分块 | 文档预览 |
| 代码 | py/js/java/ts | 语法高亮 | 代码编辑器 |

### 大文件分片上传原理

```
文件 → 按固定大小切片（如 5MB）
    ↓
每个切片计算 MD5（用于秒传和校验）
    ↓
并发上传多个切片（控制并发数，如 3）
    ↓
全部上传完成 → 通知后端合并
    ↓
断点续传：记录已上传的切片，跳过已上传的
```

### 上传状态机

```
pending → uploading → paused → uploading → success
                    ↓
                  error → retrying → uploading
```

## 3. 实操示例

### useFileUpload Composable

```typescript
import { ref, computed } from 'vue'

export interface UploadFile {
  id: string
  file: File
  name: string
  size: number
  type: string
  progress: number
  status: 'pending' | 'uploading' | 'paused' | 'success' | 'error'
  url?: string
  error?: string
  chunks?: string[]  // 已上传的切片 MD5
}

interface UseFileUploadOptions {
  chunkSize?: number
  concurrency?: number
  uploadUrl: string
  mergeUrl: string
  onSuccess?: (file: UploadFile) => void
  onError?: (file: UploadFile) => void
}

export function useFileUpload(options: UseFileUploadOptions) {
  const {
    chunkSize = 5 * 1024 * 1024,
    concurrency = 3,
    uploadUrl,
    mergeUrl,
  } = options

  const files = ref<UploadFile[]>([])
  const isDragging = ref(false)

  const totalProgress = computed(() => {
    if (files.value.length === 0) return 0
    const total = files.value.reduce((sum, f) => sum + f.progress, 0)
    return Math.round(total / files.value.length)
  })

  const pendingCount = computed(() =>
    files.value.filter(f => f.status === 'pending' || f.status === 'uploading').length
  )

  // 生成文件 ID
  const genId = () => `file-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`

  // 添加文件
  const addFiles = (fileList: FileList | File[]) => {
    const list = Array.from(fileList)
    for (const file of list) {
      files.value.push({
        id: genId(),
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        progress: 0,
        status: 'pending',
        chunks: [],
      })
    }
  }

  // 计算 MD5（简化版，实际用 spark-md5）
  const calculateMD5 = async (chunk: Blob): Promise<string> => {
    const buffer = await chunk.arrayBuffer()
    // 简化：实际应该用 spark-md5 增量计算
    return `md5-${buffer.byteLength}-${Math.random().toString(36).slice(2, 10)}`
  }

  // 上传单个文件（分片）
  const uploadFile = async (uploadFile: UploadFile) => {
    uploadFile.status = 'uploading'

    try {
      const totalChunks = Math.ceil(uploadFile.size / chunkSize)
      const uploadedChunks = new Set(uploadFile.chunks || [])

      // 生成所有切片
      const chunks: { index: number; blob: Blob; md5: string }[] = []
      for (let i = 0; i < totalChunks; i++) {
        const start = i * chunkSize
        const end = Math.min(start + chunkSize, uploadFile.size)
        const blob = uploadFile.file.slice(start, end)
        const md5 = await calculateMD5(blob)
        if (!uploadedChunks.has(md5)) {
          chunks.push({ index: i, blob, md5 })
        }
      }

      // 并发上传
      let uploaded = uploadedChunks.size
      const queue = [...chunks]

      const worker = async () => {
        while (queue.length > 0) {
          const chunk = queue.shift()!
          try {
            const formData = new FormData()
            formData.append('chunk', chunk.blob)
            formData.append('chunkIndex', chunk.index.toString())
            formData.append('fileId', uploadFile.id)
            formData.append('md5', chunk.md5)

            await fetch(uploadUrl, { method: 'POST', body: formData })

            uploadedChunks.add(chunk.md5)
            uploaded++
            uploadFile.progress = Math.round((uploaded / totalChunks) * 100)
            uploadFile.chunks = [...uploadedChunks]
          } catch (e) {
            // 失败重新入队
            queue.push(chunk)
          }
        }
      }

      // 启动并发 worker
      await Promise.all(
        Array.from({ length: Math.min(concurrency, chunks.length) }, () => worker())
      )

      // 通知后端合并
      const mergeRes = await fetch(mergeUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fileId: uploadFile.id,
          fileName: uploadFile.name,
          totalChunks,
        }),
      })
      const { url } = await mergeRes.json()

      uploadFile.status = 'success'
      uploadFile.url = url
      uploadFile.progress = 100
      options.onSuccess?.(uploadFile)
    } catch (e) {
      uploadFile.status = 'error'
      uploadFile.error = (e as Error).message
      options.onError?.(uploadFile)
    }
  }

  // 开始上传所有 pending 文件
  const startUpload = async () => {
    const pending = files.value.filter(f => f.status === 'pending')
    await Promise.all(pending.map(f => uploadFile(f)))
  }

  // 暂停
  const pauseUpload = (fileId: string) => {
    const file = files.value.find(f => f.id === fileId)
    if (file) file.status = 'paused'
  }

  // 移除文件
  const removeFile = (fileId: string) => {
    files.value = files.value.filter(f => f.id !== fileId)
  }

  // 清空
  const clear = () => {
    files.value = []
  }

  // 拖拽处理
  const handleDrop = (e: DragEvent) => {
    e.preventDefault()
    isDragging.value = false
    if (e.dataTransfer?.files) {
      addFiles(e.dataTransfer.files)
    }
  }

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault()
    isDragging.value = true
  }

  const handleDragLeave = () => {
    isDragging.value = false
  }

  return {
    files,
    isDragging,
    totalProgress,
    pendingCount,
    addFiles,
    uploadFile,
    startUpload,
    pauseUpload,
    removeFile,
    clear,
    handleDrop,
    handleDragOver,
    handleDragLeave,
  }
}
```

### 文件上传组件

```vue
<template>
  <div class="file-uploader">
    <!-- 拖拽区域 -->
    <div
      class="drop-zone"
      :class="{ dragging: isDragging }"
      @drop="handleDrop"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @click="triggerInput"
    >
      <el-icon :size="48" color="#409eff"><UploadFilled /></el-icon>
      <div class="drop-text">拖拽文件到此处，或点击选择</div>
      <div class="drop-hint">支持图片、音频、视频、文档，单个文件最大 500MB</div>
      <input
        ref="fileInput"
        type="file"
        multiple
        hidden
        @change="onFileSelect"
      />
    </div>

    <!-- 文件列表 -->
    <div v-if="files.length" class="file-list">
      <div v-for="file in files" :key="file.id" class="file-item">
        <!-- 缩略图/图标 -->
        <div class="file-thumb">
          <img v-if="isImage(file.type) && file.url" :src="file.url" />
          <el-icon v-else :size="32"><component :is="getFileIcon(file.type)" /></el-icon>
        </div>

        <!-- 文件信息 -->
        <div class="file-info">
          <div class="file-name">{{ file.name }}</div>
          <div class="file-size">{{ formatSize(file.size) }}</div>

          <!-- 进度条 -->
          <el-progress
            v-if="file.status === 'uploading' || file.status === 'paused'"
            :percentage="file.progress"
            :stroke-width="4"
            :status="file.status === 'paused' ? 'warning' : undefined"
          />
          <div v-else-if="file.status === 'success'" class="status success">
            <el-icon><CircleCheck /></el-icon> 上传成功
          </div>
          <div v-else-if="file.status === 'error'" class="status error">
            <el-icon><CircleClose /></el-icon> {{ file.error }}
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="file-actions">
          <el-button
            v-if="file.status === 'uploading'"
            size="small"
            text
            @click="pauseUpload(file.id)"
          >暂停</el-button>
          <el-button
            v-if="file.status === 'paused'"
            size="small"
            type="primary"
            text
            @click="uploadFile(file)"
          >继续</el-button>
          <el-button
            v-if="file.status === 'error'"
            size="small"
            type="primary"
            text
            @click="uploadFile(file)"
          >重试</el-button>
          <el-button size="small" text type="danger" @click="removeFile(file.id)">
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 底部操作 -->
    <div v-if="files.length" class="upload-footer">
      <span>共 {{ files.length }} 个文件，总进度 {{ totalProgress }}%</span>
      <el-button type="primary" @click="startUpload" :disabled="pendingCount === 0">
        开始上传
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  UploadFilled, CircleCheck, CircleClose,
  Picture, VideoPlay, Microphone, Document, Files,
} from '@element-plus/icons-vue'
import { useFileUpload, type UploadFile } from './useFileUpload'

const emit = defineEmits<{ success: [file: UploadFile] }>()

const fileInput = ref<HTMLInputElement>()

const {
  files, isDragging, totalProgress, pendingCount,
  addFiles, uploadFile, startUpload, pauseUpload, removeFile,
  handleDrop, handleDragOver, handleDragLeave,
} = useFileUpload({
  uploadUrl: '/api/upload/chunk',
  mergeUrl: '/api/upload/merge',
  onSuccess: (file) => emit('success', file),
})

const triggerInput = () => fileInput.value?.click()

const onFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files) addFiles(target.files)
  target.value = ''
}

const isImage = (type: string) => type.startsWith('image/')

const getFileIcon = (type: string) => {
  if (type.startsWith('image/')) return Picture
  if (type.startsWith('video/')) return VideoPlay
  if (type.startsWith('audio/')) return Microphone
  if (type.includes('pdf') || type.includes('document')) return Document
  return Files
}

const formatSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + ' MB'
  return (bytes / 1024 / 1024 / 1024).toFixed(2) + ' GB'
}
</script>
```

### 图片压缩

```typescript
/**
 * 图片压缩：在上传前压缩图片，减少上传时间和存储成本
 */
export async function compressImage(
  file: File,
  options: { maxWidth?: number; quality?: number; maxSize?: number } = {}
): Promise<Blob> {
  const { maxWidth = 1920, quality = 0.8, maxSize = 2 * 1024 * 1024 } = options

  // 小文件不压缩
  if (file.size <= maxSize) return file

  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')!

      // 计算缩放比例
      let { width, height } = img
      if (width > maxWidth) {
        height = (height * maxWidth) / width
        width = maxWidth
      }

      canvas.width = width
      canvas.height = height
      ctx.drawImage(img, 0, 0, width, height)

      canvas.toBlob(
        (blob) => {
          if (blob) resolve(blob)
          else reject(new Error('压缩失败'))
        },
        'image/jpeg',
        quality
      )
    }
    img.onerror = reject
    img.src = URL.createObjectURL(file)
  })
}
```

### 图片大图预览组件

```vue
<template>
  <el-image-viewer
    v-if="visible"
    :url-list="images"
    :initial-index="initialIndex"
    @close="visible = false"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const visible = ref(false)
const images = ref<string[]>([])
const initialIndex = ref(0)

const preview = (urlList: string[], index = 0) => {
  images.value = urlList
  initialIndex.value = index
  visible.value = true
}

defineExpose({ preview })
</script>
```

### 粘贴上传

```typescript
/**
 * 支持粘贴板上传：Ctrl+V 粘贴图片直接上传
 */
export function usePasteUpload(onFile: (file: File) => void) {
  const handlePaste = (e: ClipboardEvent) => {
    const items = e.clipboardData?.items
    if (!items) return

    for (const item of items) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile()
        if (file) onFile(file)
      }
    }
  }

  const enable = () => {
    document.addEventListener('paste', handlePaste)
  }

  const disable = () => {
    document.removeEventListener('paste', handlePaste)
  }

  return { enable, disable }
}
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 大文件上传超时 | 单次上传太大 | 分片上传，每片 5MB |
| 上传中断后要重头来 | 没有记录进度 | 断点续传，记录已上传切片 |
| 图片上传后旋转 | EXIF 方向信息 | 上传前用 canvas 修正方向 |
| MD5 计算慢 | 大文件全量计算 | 用 spark-md5 增量计算，Web Worker |
| 并发上传导致浏览器卡死 | 并发数太高 | 控制并发数（3-5） |

### 踩坑点

1. **File.slice 是 Blob 的方法**：不是 File 独有的
2. **FormData  append 文件时要指定文件名**：否则后端可能拿不到
3. **拖拽时要 preventDefault**：否则浏览器会打开文件
4. **图片压缩后格式可能变化**：PNG 转 JPEG 会丢失透明通道

### 优化方案

- **秒传**：上传前计算 MD5，后端已存在则直接返回 URL
- **Web Worker 计算 MD5**：大文件 MD5 计算不阻塞主线程
- **上传预签名 URL**：直传 OSS/COS，不经过后端
- **图片懒加载**：文件列表中的缩略图懒加载

## 5. 延伸拓展方向

- [[语音交互ASR与TTS]]：音频文件的后续处理
- [[RAG检索页面设计与实现]]：文档上传后的 RAG
- [[流式Markdown渲染与代码高亮]]：代码文件的预览
- [[AI生成内容Loading与错误态设计]]：上传中的状态展示
- [[多模态文件上传与预览]]：本笔记

## 6. 参考资料

- [MDN: File API](https://developer.mozilla.org/en-US/docs/Web/API/File)
- [MDN: FormData](https://developer.mozilla.org/en-US/docs/Web/API/FormData)
- [spark-md5](https://github.com/satazor/js-spark-md5)
- [Element Plus Upload](https://element-plus.org/zh-CN/component/upload.html)
- [vue-simple-uploader](https://github.com/simple-uploader/vue-uploader)

#待完善
'''

# ============ 笔记18：语音交互 ASR 与 TTS ============
notes["语音交互ASR与TTS.md"] = r'''---
title: 语音交互 ASR 与 TTS
category: Vue3TS前端
subcategory: AI交互组件
tags: [#Vue3TS/AI交互, #AI结合/语音, #难度/进阶, #类型/实战]
difficulty: 进阶
pre: [[Vue3-CompositionAPI深入]], [[多模态文件上传与预览]]
related: [[useSSE自定义Hook封装]], [[AI生成内容Loading与错误态设计]]
update: 2026-08-13
status: 完善
---

# 语音交互 ASR 与 TTS

## 1. 核心概述

语音交互让用户可以用语音和 AI 对话：说话→ASR 转文字→AI 处理→TTS 转语音→播放。前端需要处理：录音、流式语音识别、语音合成播放、VAD 端点检测、长文本分段朗读。浏览器原生 Web Speech API 能力有限，生产环境通常对接云端 ASR/TTS 服务。

**解决的场景问题**：
- 用户不想打字，想用语音输入
- AI 回答需要朗读出来（无障碍、驾驶场景）
- 实时语音对话，低延迟
- 长文本朗读需要分段
- 录音质量差导致识别不准

## 2. 底层原理/核心逻辑

### 语音交互技术栈

```
输入：
  麦克风 → MediaRecorder → 音频流 → ASR（语音识别）→ 文本

输出：
  文本 → TTS（语音合成）→ 音频流 → Audio 播放

双向：
  WebRTC → 实时语音对话
```

### ASR 方案对比

| 方案 | 特点 | 延迟 | 准确率 | 成本 |
|------|------|------|--------|------|
| Web Speech API | 浏览器原生，免费 | 中 | 中 | 免费 |
| 阿里云 ASR | 云端，支持流式 | 低 | 高 | 低 |
| 腾讯云 ASR | 云端，支持热词 | 低 | 高 | 低 |
| OpenAI Whisper | 本地/云端，多语言 | 中 | 高 | 中 |
| FunASR | 本地部署，开源 | 低 | 高 | 免费 |

### TTS 方案对比

| 方案 | 特点 | 自然度 | 多语言 | 成本 |
|------|------|--------|--------|------|
| SpeechSynthesis | 浏览器原生 | 低 | 有限 | 免费 |
| 阿里云 TTS | 云端，多音色 | 高 | 多 | 低 |
| 微软 Azure TTS | 云端，神经语音 | 极高 | 多 | 中 |
| OpenAI TTS | 云端，自然 | 高 | 多 | 中 |
| Edge TTS | 免费，微软语音 | 高 | 多 | 免费 |

### 流式语音识别原理

```
麦克风 → 音频分片（如 100ms）
    ↓
WebSocket 发送到 ASR 服务
    ↓
服务端实时返回部分识别结果
    ↓
前端展示实时字幕（可能修正）
    ↓
VAD 检测到静音 → 发送结束标记 → 返回最终结果
```

## 3. 实操示例

### 录音 Composable

```typescript
import { ref, onUnmounted } from 'vue'

export function useAudioRecorder() {
  const isRecording = ref(false)
  const audioBlob = ref<Blob | null>(null)
  const audioUrl = ref('')
  const duration = ref(0)
  const volume = ref(0)

  let mediaRecorder: MediaRecorder | null = null
  let audioContext: AudioContext | null = null
  let analyser: AnalyserNode | null = null
  let stream: MediaStream | null = null
  let timer: number | null = null
  let volumeTimer: number | null = null

  const start = async () => {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorder = new MediaRecorder(stream)
      const chunks: BlobPart[] = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data)
      }

      mediaRecorder.onstop = () => {
        audioBlob.value = new Blob(chunks, { type: 'audio/webm' })
        audioUrl.value = URL.createObjectURL(audioBlob.value)
      }

      mediaRecorder.start()
      isRecording.value = true
      duration.value = 0

      // 计时器
      timer = window.setInterval(() => {
        duration.value++
      }, 1000)

      // 音量检测
      audioContext = new AudioContext()
      const source = audioContext.createMediaStreamSource(stream)
      analyser = audioContext.createAnalyser()
      analyser.fftSize = 256
      source.connect(analyser)

      const dataArray = new Uint8Array(analyser.frequencyBinCount)
      const updateVolume = () => {
        if (!analyser || !isRecording.value) return
        analyser.getByteFrequencyData(dataArray)
        const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length
        volume.value = avg / 255
        volumeTimer = requestAnimationFrame(updateVolume)
      }
      updateVolume()

    } catch (e) {
      console.error('录音失败:', e)
      throw e
    }
  }

  const stop = () => {
    mediaRecorder?.stop()
    stream?.getTracks().forEach(t => t.stop())
    audioContext?.close()
    isRecording.value = false
    if (timer) clearInterval(timer)
    if (volumeTimer) cancelAnimationFrame(volumeTimer)
    volume.value = 0
  }

  const reset = () => {
    audioBlob.value = null
    audioUrl.value = ''
    duration.value = 0
  }

  onUnmounted(() => {
    if (isRecording.value) stop()
  })

  return {
    isRecording,
    audioBlob,
    audioUrl,
    duration,
    volume,
    start,
    stop,
    reset,
  }
}
```

### 语音识别 Composable（Web Speech API）

```typescript
import { ref } from 'vue'

interface SpeechRecognitionOptions {
  lang?: string
  continuous?: boolean
  interimResults?: boolean
}

export function useSpeechRecognition(options: SpeechRecognitionOptions = {}) {
  const { lang = 'zh-CN', continuous = false, interimResults = true } = options

  const transcript = ref('')
  const interimTranscript = ref('')
  const isListening = ref(false)
  const error = ref<string | null>(null)

  // 兼容 webkit 前缀
  const SpeechRecognition = (window as any).SpeechRecognition
    || (window as any).webkitSpeechRecognition

  let recognition: any = null

  const supported = !!SpeechRecognition

  const start = () => {
    if (!supported) {
      error.value = '浏览器不支持语音识别'
      return
    }

    recognition = new SpeechRecognition()
    recognition.lang = lang
    recognition.continuous = continuous
    recognition.interimResults = interimResults

    recognition.onresult = (event: any) => {
      let interim = ''
      let final = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) {
          final += result[0].transcript
        } else {
          interim += result[0].transcript
        }
      }
      if (final) transcript.value += final
      interimTranscript.value = interim
    }

    recognition.onerror = (e: any) => {
      error.value = e.error
      isListening.value = false
    }

    recognition.onend = () => {
      isListening.value = false
      interimTranscript.value = ''
    }

    transcript.value = ''
    recognition.start()
    isListening.value = true
  }

  const stop = () => {
    recognition?.stop()
    isListening.value = false
  }

  const reset = () => {
    transcript.value = ''
    interimTranscript.value = ''
    error.value = null
  }

  return {
    supported,
    transcript,
    interimTranscript,
    isListening,
    error,
    start,
    stop,
    reset,
  }
}
```

### 语音合成 Composable

```typescript
import { ref, onUnmounted } from 'vue'

interface SpeakOptions {
  lang?: string
  rate?: number      // 语速 0.1-10
  pitch?: number     // 音调 0-2
  volume?: number    // 音量 0-1
  voice?: string     // 嗓音名称
  onBoundary?: (charIndex: number) => void
  onEnd?: () => void
}

export function useSpeechSynthesis() {
  const isSpeaking = ref(false)
  const isPaused = ref(false)
  const currentText = ref('')
  const voices = ref<SpeechSynthesisVoice[]>([])

  const synth = window.speechSynthesis
  let currentUtterance: SpeechSynthesisUtterance | null = null

  // 加载可用嗓音
  const loadVoices = () => {
    voices.value = synth.getVoices()
  }

  // 初始化
  if (synth) {
    loadVoices()
    synth.onvoiceschanged = loadVoices
  }

  const speak = (text: string, options: SpeakOptions = {}) => {
    if (!text) return

    // 长文本分段
    const segments = splitLongText(text)

    let segmentIndex = 0
    const speakNext = () => {
      if (segmentIndex >= segments.length) {
        isSpeaking.value = false
        options.onEnd?.()
        return
      }

      const utterance = new SpeechSynthesisUtterance(segments[segmentIndex])
      utterance.lang = options.lang || 'zh-CN'
      utterance.rate = options.rate || 1
      utterance.pitch = options.pitch || 1
      utterance.volume = options.volume || 1

      if (options.voice) {
        const voice = voices.value.find(v => v.name === options.voice)
        if (voice) utterance.voice = voice
      }

      utterance.onboundary = (e) => {
        options.onBoundary?.(e.charIndex)
      }

      utterance.onend = () => {
        segmentIndex++
        speakNext()
      }

      currentUtterance = utterance
      currentText.value = segments[segmentIndex]
      synth.speak(utterance)
    }

    isSpeaking.value = true
    speakNext()
  }

  const pause = () => {
    synth.pause()
    isPaused.value = true
  }

  const resume = () => {
    synth.resume()
    isPaused.value = false
  }

  const stop = () => {
    synth.cancel()
    isSpeaking.value = false
    isPaused.value = false
  }

  // 长文本分段：按标点符号切分，每段不超过 200 字
  const splitLongText = (text: string): string[] => {
    if (text.length <= 200) return [text]

    const segments: string[] = []
    const sentences = text.split(/([。！？，；])/)
    let current = ''

    for (let i = 0; i < sentences.length; i += 2) {
      const sentence = sentences[i] + (sentences[i + 1] || '')
      if (current.length + sentence.length > 200 && current) {
        segments.push(current)
        current = sentence
      } else {
        current += sentence
      }
    }
    if (current) segments.push(current)
    return segments
  }

  onUnmounted(() => {
    stop()
  })

  return {
    isSpeaking,
    isPaused,
    currentText,
    voices,
    speak,
    pause,
    resume,
    stop,
  }
}
```

### 云端流式 ASR（WebSocket）

```typescript
import { ref } from 'vue'

export function useCloudASR(wsUrl: string) {
  const transcript = ref('')
  const isListening = ref(false)
  const isConnected = ref(false)

  let ws: WebSocket | null = null
  let mediaRecorder: MediaRecorder | null = null
  let stream: MediaStream | null = null

  const start = async () => {
    // 建立 WebSocket
    ws = new WebSocket(wsUrl)
    ws.binaryType = 'arraybuffer'

    ws.onopen = () => {
      isConnected.value = true
      // 发送配置
      ws?.send(JSON.stringify({
        type: 'config',
        encoding: 'webm',
        sampleRate: 16000,
        language: 'zh-CN',
      }))
    }

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        if (data.type === 'partial') {
          transcript.value = data.text  // 实时结果（可能变化）
        } else if (data.type === 'final') {
          transcript.value = data.text  // 最终结果
        }
      } catch { /* ignore */ }
    }

    ws.onclose = () => {
      isConnected.value = false
    }

    // 开始录音
    stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0 && ws?.readyState === WebSocket.OPEN) {
        ws.send(e.data)
      }
    }

    // 每 100ms 发送一次音频
    mediaRecorder.start(100)
    isListening.value = true
  }

  const stop = () => {
    mediaRecorder?.stop()
    stream?.getTracks().forEach(t => t.stop())
    ws?.send(JSON.stringify({ type: 'end' }))
    setTimeout(() => ws?.close(), 500)
    isListening.value = false
  }

  return { transcript, isListening, isConnected, start, stop }
}
```

### 语音对话整合组件

```vue
<template>
  <div class="voice-chat">
    <!-- 对话消息 -->
    <div class="messages">
      <div v-for="(msg, i) in messages" :key="i" class="message">
        <div v-if="msg.role === 'user'" class="user-msg">
          <el-icon><Microphone /></el-icon>
          {{ msg.content }}
        </div>
        <div v-else class="assistant-msg">
          <StreamingMarkdown :content="msg.content" />
          <div class="voice-actions">
            <el-button size="small" @click="speakText(msg.content)" :icon="VideoPlay">
              朗读
            </el-button>
          </div>
        </div>
      </div>

      <!-- 实时识别中 -->
      <div v-if="isListening" class="user-msg recognizing">
        <el-icon class="pulse"><Microphone /></el-icon>
        {{ transcript }}<span class="cursor">|</span>
      </div>
    </div>

    <!-- 语音控制栏 -->
    <div class="voice-bar">
      <!-- 录音按钮 -->
      <button
        class="mic-btn"
        :class="{ recording: isListening }"
        @click="toggleRecording"
      >
        <el-icon :size="24"><Microphone /></el-icon>
      </button>

      <!-- 音量波形 -->
      <div v-if="isListening" class="waveform">
        <div
          v-for="i in 20"
          :key="i"
          class="wave-bar"
          :style="{ height: Math.random() * volume * 100 + '%' }"
        ></div>
      </div>

      <!-- TTS 控制 -->
      <div v-if="isSpeaking" class="tts-control">
        <el-button size="small" @click="isPaused ? resume() : pause()">
          {{ isPaused ? '继续' : '暂停' }}
        </el-button>
        <el-button size="small" @click="stopSpeak">停止</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Microphone, VideoPlay } from '@element-plus/icons-vue'
import { useAudioRecorder } from './useAudioRecorder'
import { useSpeechRecognition } from './useSpeechRecognition'
import { useSpeechSynthesis } from './useSpeechSynthesis'
import StreamingMarkdown from './StreamingMarkdown.vue'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const messages = ref<Message[]>([])

const { volume, start: startRecorder, stop: stopRecorder } = useAudioRecorder()
const { transcript, isListening, start: startASR, stop: stopASR } = useSpeechRecognition()
const { isSpeaking, isPaused, speak, pause, resume, stop: stopSpeak } = useSpeechSynthesis()

const toggleRecording = async () => {
  if (isListening.value) {
    stopASR()
    stopRecorder()
    // 发送识别结果
    if (transcript.value.trim()) {
      messages.value.push({ role: 'user', content: transcript.value })
      await sendToAI(transcript.value)
    }
  } else {
    await startRecorder()
    startASR()
  }
}

const sendToAI = async (text: string) => {
  // 调用 AI 接口
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text }),
  })
  const { answer } = await response.json()
  messages.value.push({ role: 'assistant', content: answer })
  // 自动朗读
  speak(answer)
}

const speakText = (text: string) => {
  stopSpeak()
  speak(text)
}
</script>
```

### VAD 端点检测

```typescript
/**
 * 简单的 VAD（语音活动检测）：基于音量阈值检测静音
 */
export function useVAD(options: { silenceThreshold?: number; silenceDuration?: number } = {}) {
  const { silenceThreshold = 0.02, silenceDuration = 1500 } = options

  const onSpeechEnd = (callback: () => void) => {
    let silenceStart = 0
    let isSilent = false

    return (volume: number) => {
      if (volume < silenceThreshold) {
        if (!isSilent) {
          isSilent = true
          silenceStart = Date.now()
        } else if (Date.now() - silenceStart > silenceDuration) {
          callback()
          isSilent = false
        }
      } else {
        isSilent = false
      }
    }
  }

  return { onSpeechEnd }
}
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 录音权限被拒绝 | 用户没授权 | 提示用户在浏览器设置中允许 |
| 识别准确率低 | 麦克风质量差/噪音 | 用降噪算法，提示用户安静环境 |
| TTS 发音不自然 | 浏览器内置语音质量差 | 用云端 TTS（Azure/阿里云） |
| 长文本朗读中断 | SpeechSynthesis 长文本 bug | 分段朗读，每段 < 200 字 |
| iOS Safari 不支持 | 兼容性问题 | 降级方案，提示用户用 Chrome |

### 踩坑点

1. **SpeechSynthesis 在 Chrome 有长文本 bug**：超过 200 字可能中断，必须分段
2. **MediaRecorder 的 mimeType 要检查支持**：Safari 不支持 webm
3. **语音识别需要 HTTPS 或 localhost**：HTTP 环境下不可用
4. **iOS 需要用户交互后才能播放音频**：不能自动播放 TTS

### 优化方案

- **降噪处理**：用 Web Audio API 做噪声抑制
- **回声消除**：开启 echoCancellation
- **热词识别**：ASR 服务支持自定义热词提升准确率
- **情感 TTS**：选择带情感的语音合成服务

## 5. 延伸拓展方向

- [[多模态文件上传与预览]]：音频文件上传
- [[useSSE自定义Hook封装]]：AI 响应的流式接收
- [[AI生成内容Loading与错误态设计]]：语音识别中的状态
- [[Agent任务进度与思考链展示]]：语音 Agent 的执行展示
- [[流式Markdown渲染与代码高亮]]：识别结果的渲染

## 6. 参考资料

- [MDN: Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [MDN: MediaRecorder](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [阿里云 ASR](https://help.aliyun.com/product/30413.html)
- [Azure TTS](https://azure.microsoft.com/services/cognitive-services/text-to-speech/)

#待完善
'''

# ============ 笔记21：AI 生成内容 Loading 与错误态设计 ============
notes["AI生成内容Loading与错误态设计.md"] = r'''---
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
'''

# ============ 笔记24：Obsidian AI 插件开发入门 ============
notes["ObsidianAI插件开发入门.md"] = r'''---
title: Obsidian AI 插件开发入门
category: Vue3TS前端
subcategory: AI交互组件
tags: [#Vue3TS/AI交互, #AI结合/Obsidian, #难度/高级, #类型/实战]
difficulty: 高级
pre: [[Vue3-CompositionAPI深入]], [[TypeScript-类型体操高级]]
related: [[AIGC-Obsidian-应用枢纽]], [[Prompt工程与版本管理]]
update: 2026-08-13
status: 完善
---

# Obsidian AI 插件开发入门

## 1. 核心概述

Obsidian 是基于 Electron 的本地 Markdown 知识库，插件用 TypeScript 开发，可以直接操作笔记、添加命令、创建侧边栏、集成 AI 能力。AI 插件可以实现：选中文本润色/翻译/总结、对话侧边栏、本地 RAG、自动标签生成。掌握 Obsidian Plugin API 是开发 AI 知识管理工具的基础。

**解决的场景问题**：
- 想在 Obsidian 中直接调用 AI 处理笔记
- 需要自定义 AI 工作流，现有插件不满足
- 想做本地 RAG，基于自己的笔记问答
- 需要批量处理笔记（自动标签、摘要）
- 想学习 Obsidian 插件开发

## 2. 底层原理/核心逻辑

### Obsidian 插件架构

```
Obsidian (Electron + CodeMirror 6)
    ↓
Plugin API (obsidian module)
    ├── Plugin: 插件主入口
    ├── Vault: 笔记库操作
    ├── Workspace: 工作区（面板、布局）
    ├── Modal: 弹窗
    ├── SettingTab: 设置页
    ├── Command: 命令
    ├── Editor: 编辑器操作
    └── Notice: 通知
```

### 核心 API 模块

| 模块 | 作用 | 常用方法 |
|------|------|----------|
| Vault | 文件操作 | create, read, modify, delete, getAbstractFileByPath |
| Workspace | 布局管理 | getLeaf, setActiveLeaf, openLinkText |
| Editor | 编辑器 | getValue, setValue, replaceSelection, getSelection |
| PluginSettingTab | 设置页 | display, addToggle, addText |
| ItemView | 自定义视图 | getViewType, onOpen |
| Notice | 通知 | new Notice(message, duration) |
| Modal | 弹窗 | onOpen, onClose, contentEl |

### 插件文件结构

```
my-ai-plugin/
├── manifest.json          # 插件元数据
├── main.ts                # 插件主入口
├── styles.css             # 样式
├── esbuild.config.mjs     # 构建配置
├── package.json
├── tsconfig.json
└── src/
    ├── ai-service.ts      # AI 服务封装
    ├── settings.ts        # 设置定义
    ├── commands/          # 命令
    │   ├── polish.ts
    │   ├── translate.ts
    │   └── summarize.ts
    └── views/             # 视图
        └── chat-sidebar.ts
```

## 3. 实操示例

### 项目初始化

```bash
# 克隆官方模板
git clone https://github.com/obsidianmd/obsidian-sample-plugin.git my-ai-plugin
cd my-ai-plugin

# 安装依赖
npm install

# 安装 AI 相关依赖
npm install openai

# 构建
npm run dev  # 开发模式，监听文件变化
```

### manifest.json

```json
{
  "id": "my-ai-plugin",
  "name": "My AI Plugin",
  "version": "1.0.0",
  "minAppVersion": "1.0.0",
  "description": "AI 助手插件，支持润色、翻译、总结、对话",
  "author": "Your Name",
  "authorUrl": "https://yourwebsite.com",
  "isDesktopOnly": false
}
```

### 插件主入口 main.ts

```typescript
import { Plugin, Notice } from 'obsidian'
import { AISettingTab, DEFAULT_SETTINGS, AISettings } from './settings'
import { AIService } from './ai-service'
import { polishText, translateText, summarizeText } from './commands/text-actions'
import { ChatSidebarView, VIEW_TYPE_CHAT } from './views/chat-sidebar'

export default class AIPlugin extends Plugin {
  settings: AISettings
  aiService: AIService

  async onload() {
    await this.loadSettings()

    // 初始化 AI 服务
    this.aiService = new AIService(this.settings)

    // 注册设置页
    this.addSettingTab(new AISettingTab(this.app, this))

    // 注册命令：润色选中文本
    this.addCommand({
      id: 'polish-selection',
      name: '润色选中文本',
      editorCallback: async (editor) => {
        const selected = editor.getSelection()
        if (!selected) {
          new Notice('请先选中文本')
          return
        }
        try {
          const result = await polishText(this.aiService, selected)
          editor.replaceSelection(result)
          new Notice('润色完成')
        } catch (e) {
          new Notice('润色失败: ' + (e as Error).message)
        }
      },
    })

    // 注册命令：翻译选中文本
    this.addCommand({
      id: 'translate-selection',
      name: '翻译选中文本',
      editorCallback: async (editor) => {
        const selected = editor.getSelection()
        if (!selected) {
          new Notice('请先选中文本')
          return
        }
        try {
          const result = await translateText(this.aiService, selected)
          editor.replaceSelection(result)
          new Notice('翻译完成')
        } catch (e) {
          new Notice('翻译失败: ' + (e as Error).message)
        }
      },
    })

    // 注册命令：总结当前笔记
    this.addCommand({
      id: 'summarize-note',
      name: '总结当前笔记',
      editorCallback: async (editor) => {
        const content = editor.getValue()
        try {
          const summary = await summarizeText(this.aiService, content)
          // 在笔记开头插入摘要
          editor.setValue('## 摘要\n\n' + summary + '\n\n---\n\n' + content)
          new Notice('总结完成')
        } catch (e) {
          new Notice('总结失败: ' + (e as Error).message)
        }
      },
    })

    // 注册侧边栏视图
    this.registerView(VIEW_TYPE_CHAT, (leaf) => new ChatSidebarView(leaf, this))

    // 添加侧边栏图标
    this.addRibbonIcon('message-square', 'AI 对话', () => {
      this.activateChatView()
    })

    console.log('AI Plugin loaded')
  }

  async activateChatView() {
    let leaf = this.app.workspace.getLeavesOfType(VIEW_TYPE_CHAT)[0]
    if (!leaf) {
      leaf = this.app.workspace.getRightLeaf(false)
      await leaf.setViewState({ type: VIEW_TYPE_CHAT })
    }
    this.app.workspace.revealLeaf(leaf)
  }

  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData())
  }

  async saveSettings() {
    await this.saveData(this.settings)
  }

  onunload() {
    console.log('AI Plugin unloaded')
  }
}
```

### 设置页 settings.ts

```typescript
import { App, PluginSettingTab, Setting } from 'obsidian'
import AIPlugin from './main'

export interface AISettings {
  apiKey: string
  apiBase: string
  model: string
  temperature: number
  maxTokens: number
  stream: boolean
}

export const DEFAULT_SETTINGS: AISettings = {
  apiKey: '',
  apiBase: 'https://api.openai.com/v1',
  model: 'gpt-4o-mini',
  temperature: 0.7,
  maxTokens: 2000,
  stream: true,
}

export class AISettingTab extends PluginSettingTab {
  plugin: AIPlugin

  constructor(app: App, plugin: AIPlugin) {
    super(app, plugin)
    this.plugin = plugin
  }

  display(): void {
    const { containerEl } = this
    containerEl.empty()

    containerEl.createEl('h2', { text: 'AI 插件设置' })

    // API Key
    new Setting(containerEl)
      .setName('API Key')
      .setDesc('输入你的 AI 服务 API Key')
      .addText((text) =>
        text
          .setPlaceholder('sk-...')
          .setValue(this.plugin.settings.apiKey)
          .onChange(async (value) => {
            this.plugin.settings.apiKey = value
            await this.plugin.saveSettings()
          })
      )

    // API Base URL
    new Setting(containerEl)
      .setName('API Base URL')
      .setDesc('API 接口地址，支持自定义代理')
      .addText((text) =>
        text
          .setPlaceholder('https://api.openai.com/v1')
          .setValue(this.plugin.settings.apiBase)
          .onChange(async (value) => {
            this.plugin.settings.apiBase = value
            await this.plugin.saveSettings()
          })
      )

    // 模型选择
    new Setting(containerEl)
      .setName('模型')
      .setDesc('选择使用的 AI 模型')
      .addDropdown((dropdown) =>
        dropdown
          .addOption('gpt-4o-mini', 'GPT-4o Mini')
          .addOption('gpt-4o', 'GPT-4o')
          .addOption('gpt-3.5-turbo', 'GPT-3.5 Turbo')
          .setValue(this.plugin.settings.model)
          .onChange(async (value) => {
            this.plugin.settings.model = value
            await this.plugin.saveSettings()
          })
      )

    // Temperature
    new Setting(containerEl)
      .setName('Temperature')
      .setDesc('控制输出随机性，0 更确定，1 更创意')
      .addSlider((slider) =>
        slider
          .setLimits(0, 1, 0.1)
          .setValue(this.plugin.settings.temperature)
          .setDynamicTooltip()
          .onChange(async (value) => {
            this.plugin.settings.temperature = value
            await this.plugin.saveSettings()
          })
      )

    // 流式输出
    new Setting(containerEl)
      .setName('流式输出')
      .setDesc('开启后逐字显示 AI 回复')
      .addToggle((toggle) =>
        toggle
          .setValue(this.plugin.settings.stream)
          .onChange(async (value) => {
            this.plugin.settings.stream = value
            await this.plugin.saveSettings()
          })
      )
  }
}
```

### AI 服务封装 ai-service.ts

```typescript
import { AISettings } from './settings'

interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export class AIService {
  private settings: AISettings

  constructor(settings: AISettings) {
    this.settings = settings
  }

  async chat(messages: ChatMessage[]): Promise<string> {
    if (!this.settings.apiKey) {
      throw new Error('请先在设置中配置 API Key')
    }

    const response = await fetch(`${this.settings.apiBase}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.settings.apiKey}`,
      },
      body: JSON.stringify({
        model: this.settings.model,
        messages,
        temperature: this.settings.temperature,
        max_tokens: this.settings.maxTokens,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error?.message || `HTTP ${response.status}`)
    }

    const data = await response.json()
    return data.choices[0].message.content
  }

  // 流式聊天
  async streamChat(
    messages: ChatMessage[],
    onToken: (token: string) => void
  ): Promise<string> {
    const response = await fetch(`${this.settings.apiBase}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.settings.apiKey}`,
      },
      body: JSON.stringify({
        model: this.settings.model,
        messages,
        temperature: this.settings.temperature,
        max_tokens: this.settings.maxTokens,
        stream: true,
      }),
    })

    const reader = response.body!.getReader()
    const decoder = new TextDecoder()
    let fullText = ''
    let buffer = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const payload = line.slice(6)
          if (payload === '[DONE]') continue
          try {
            const data = JSON.parse(payload)
            const token = data.choices?.[0]?.delta?.content
            if (token) {
              fullText += token
              onToken(token)
            }
          } catch { /* ignore */ }
        }
      }
    }

    return fullText
  }

  // 润色
  async polish(text: string): Promise<string> {
    return this.chat([
      { role: 'system', content: '你是一个专业的文字编辑，请润色以下文本，保持原意，使表达更流畅、专业。只输出润色后的文本，不要解释。' },
      { role: 'user', content: text },
    ])
  }

  // 翻译
  async translate(text: string, targetLang = '中文'): Promise<string> {
    return this.chat([
      { role: 'system', content: `你是一个专业翻译，请将以下文本翻译成${targetLang}。只输出翻译结果，不要解释。` },
      { role: 'user', content: text },
    ])
  }

  // 总结
  async summarize(text: string): Promise<string> {
    return this.chat([
      { role: 'system', content: '请为以下文本生成简洁的摘要，突出核心要点。用 3-5 个要点的形式输出。' },
      { role: 'user', content: text },
    ])
  }

  // 生成标签
  async generateTags(text: string): Promise<string[]> {
    const result = await this.chat([
      { role: 'system', content: '请为以下文本生成 3-5 个标签，用逗号分隔，不要加 # 号。' },
      { role: 'user', content: text },
    ])
    return result.split(/[,，]/).map(t => t.trim()).filter(Boolean)
  }
}
```

### 文本操作命令 commands/text-actions.ts

```typescript
import { AIService } from '../ai-service'

export async function polishText(aiService: AIService, text: string): Promise<string> {
  return aiService.polish(text)
}

export async function translateText(aiService: AIService, text: string): Promise<string> {
  return aiService.translate(text)
}

export async function summarizeText(aiService: AIService, text: string): Promise<string> {
  return aiService.summarize(text)
}
```

### 对话侧边栏 views/chat-sidebar.ts

```typescript
import { ItemView, WorkspaceLeaf, Notice } from 'obsidian'
import AIPlugin from '../main'

export const VIEW_TYPE_CHAT = 'ai-chat-view'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export class ChatSidebarView extends ItemView {
  plugin: AIPlugin
  messages: ChatMessage[] = []
  inputEl: HTMLTextAreaElement
  messagesEl: HTMLElement

  constructor(leaf: WorkspaceLeaf, plugin: AIPlugin) {
    super(leaf)
    this.plugin = plugin
  }

  getViewType(): string {
    return VIEW_TYPE_CHAT
  }

  getDisplayText(): string {
    return 'AI 对话'
  }

  getIcon(): string {
    return 'message-square'
  }

  async onOpen() {
    const container = this.containerEl.children[1]
    container.empty()
    container.addClass('ai-chat-container')

    // 消息区域
    this.messagesEl = container.createDiv('ai-chat-messages')

    // 输入区域
    const inputContainer = container.createDiv('ai-chat-input-container')
    this.inputEl = inputContainer.createEl('textarea', {
      cls: 'ai-chat-input',
      placeholder: '输入消息... (Shift+Enter 换行)',
    })

    const sendBtn = inputContainer.createEl('button', {
      cls: 'ai-chat-send',
      text: '发送',
    })

    sendBtn.addEventListener('click', () => this.sendMessage())
    this.inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        this.sendMessage()
      }
    })

    this.renderMessages()
  }

  async sendMessage() {
    const text = this.inputEl.value.trim()
    if (!text) return

    this.inputEl.value = ''
    this.messages.push({ role: 'user', content: text })
    this.renderMessages()

    // 显示 AI 思考中
    const thinkingEl = this.messagesEl.createDiv('ai-message ai-thinking')
    thinkingEl.setText('AI 正在思考...')

    try {
      const response = await this.plugin.aiService.chat([
        { role: 'system', content: '你是一个有帮助的 AI 助手。' },
        ...this.messages.map(m => ({ role: m.role, content: m.content })),
      ])

      thinkingEl.remove()
      this.messages.push({ role: 'assistant', content: response })
      this.renderMessages()
    } catch (e) {
      thinkingEl.remove()
      new Notice('出错了: ' + (e as Error).message)
    }
  }

  renderMessages() {
    this.messagesEl.empty()
    for (const msg of this.messages) {
      const msgEl = this.messagesEl.createDiv(`ai-message ai-${msg.role}`)
      msgEl.setText(msg.content)
    }
    this.messagesEl.scrollTop = this.messagesEl.scrollHeight
  }

  async onClose() {
    // 清理
  }
}
```

### styles.css

```css
.ai-chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 12px;
}

.ai-chat-messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 12px;
}

.ai-message {
  padding: 8px 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  max-width: 90%;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.ai-message.ai-user {
  background: var(--interactive-accent);
  color: var(--text-on-accent);
  margin-left: auto;
}

.ai-message.ai-assistant {
  background: var(--background-secondary);
}

.ai-message.ai-thinking {
  color: var(--text-muted);
  font-style: italic;
}

.ai-chat-input-container {
  display: flex;
  gap: 8px;
}

.ai-chat-input {
  flex: 1;
  resize: none;
  min-height: 60px;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid var(--background-modifier-border);
  background: var(--background-primary);
  color: var(--text-normal);
}

.ai-chat-send {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  background: var(--interactive-accent);
  color: var(--text-on-accent);
  cursor: pointer;
  align-self: flex-end;
}

.ai-chat-send:hover {
  opacity: 0.9;
}
```

### 本地 RAG 服务（进阶）

```typescript
import { Vault, TFile } from 'obsidian'
import { AIService } from './ai-service'

export class LocalRAGService {
  private vault: Vault
  private aiService: AIService
  private noteEmbeddings: Map<string, { content: string; embedding: number[] }> = new Map()

  constructor(vault: Vault, aiService: AIService) {
    this.vault = vault
    this.aiService = aiService
  }

  // 索引所有笔记（简化版，实际用向量数据库）
  async indexAllNotes() {
    const files = this.vault.getFiles().filter(f => f.extension === 'md')
    for (const file of files) {
      const content = await this.vault.cachedRead(file as TFile)
      // 简化：只存内容，实际应该计算 embedding
      this.noteEmbeddings.set(file.path, { content, embedding: [] })
    }
  }

  // 简单关键词检索（实际应该用向量相似度）
  searchNotes(query: string, limit = 5): string[] {
    const results: { path: string; score: number }[] = []
    const queryWords = query.toLowerCase().split(/\s+/)

    for (const [path, data] of this.noteEmbeddings) {
      const contentLower = data.content.toLowerCase()
      let score = 0
      for (const word of queryWords) {
        if (contentLower.includes(word)) score++
      }
      if (score > 0) {
        results.push({ path, score })
      }
    }

    return results
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map(r => r.path)
  }

  // 基于笔记回答问题
  async answerWithNotes(question: string): Promise<string> {
    const relevantPaths = this.searchNotes(question)
    let context = ''

    for (const path of relevantPaths) {
      const data = this.noteEmbeddings.get(path)
      if (data) {
        context += `\n\n--- 笔记: ${path} ---\n${data.content.slice(0, 2000)}`
      }
    }

    return this.aiService.chat([
      { role: 'system', content: '请基于以下笔记内容回答用户问题。如果笔记中没有相关信息，请说"在笔记中未找到相关信息"。' },
      { role: 'user', content: `参考笔记：${context}\n\n问题：${question}` },
    ])
  }
}
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 插件不显示 | manifest.json 格式错或放错位置 | 检查 .obsidian/plugins/ 目录 |
| API 调用失败 | CORS 限制 | Obsidian 是 Electron，没有 CORS 限制 |
| 编辑器替换不生效 | 用错了 API | 用 editor.replaceSelection 或 editor.setValue |
| 设置不保存 | 没调用 saveSettings | onChange 中调用 await this.saveSettings() |
| 样式不生效 | CSS 选择器不对 | 用 Obsidian 的 CSS 变量（--background-primary 等） |

### 踩坑点

1. **Obsidian 用的是 CodeMirror 6**：编辑器 API 和传统 textarea 不同
2. **插件开发需要热重载插件**：安装 "Hot Reload" 插件，或用 npm run dev
3. **API Key 存在 data.json 中**：是明文存储，注意安全
4. **移动端插件要注意兼容性**：有些 API 在移动端不可用

### 优化方案

- **流式输出**：在侧边栏中实现逐字显示
- **命令面板集成**：所有功能都注册为命令，方便快捷键调用
- **模板系统**：用户可以自定义 Prompt 模板
- **批量处理**：支持对整个文件夹的笔记批量生成标签/摘要

## 5. 延伸拓展方向

- [[AIGC-Obsidian-应用枢纽]]：Obsidian AI 应用全景
- [[Prompt工程与版本管理]]：插件中的 Prompt 管理
- [[RAG文本分块策略与实践]]：本地 RAG 的分块
- [[GraphRAG知识图谱增强检索]]：基于 Obsidian 双链的 GraphRAG
- [[流式Markdown渲染与代码高亮]]：对话中的 Markdown 渲染

## 6. 参考资料

- [Obsidian Plugin API](https://docs.obsidian.md/Home)
- [Obsidian Sample Plugin](https://github.com/obsidianmd/obsidian-sample-plugin)
- [Obsidian API Type Definitions](https://github.com/obsidianmd/obsidian-api)
- [Awesome Obsidian Plugins](https://github.com/kmaasrud/awesome-obsidian)
- [Copilot for Obsidian](https://github.com/logancyang/obsidian-copilot)

#待完善
'''

# 写入文件
for filename, content in notes.items():
    filepath = os.path.join(BASE, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
    print(f"已写入: {filename} ({len(content)} 字节)")

print(f"\n共写入 {len(notes)} 篇笔记")
