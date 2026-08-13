---
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
