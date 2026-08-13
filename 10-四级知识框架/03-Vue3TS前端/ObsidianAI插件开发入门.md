---
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
