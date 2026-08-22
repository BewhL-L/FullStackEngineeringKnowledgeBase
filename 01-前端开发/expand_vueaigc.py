# -*- coding: utf-8 -*-
"""扩展 Vue3 AIGC 前端应用知识点系统梳理_优化版.md
只为 16 个 ### 知识点插入「🔍 知识点深度解析」块，并补充顶部「优化版说明」。
原文 100% 保留（不删除、不改写、不重排）。
"""
import os
from engine import expand

BASE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(BASE, "Vue3 AIGC前端应用知识点系统梳理_优化版.md")

content_map = {
    "### 2.1 写作助手核心布局": (
        "搭建 AI 写作助手的三栏式工作界面，将写作模式/风格/字数的控制、文本编辑输入、AI 结果展示三块职责分离，配合 @ai-sdk/vue 的 useChat 实现流式对话式写作。",
        "基于 Vue 3 Composition API 用 ref 管理 writingMode/tone/wordCount 等状态，computed 根据状态拼出 systemPrompt；useChat 封装了 messages/input/handleSubmit 等，内部通过 SSE 流式接收 assistant 消息并渲染 Markdown，整个布局用 flex 三栏隔离关注点。",
        [
            "三栏结构：左侧 control-panel（模式/风格/字数）、中间 editor-area（textarea+提交）、右侧 result-panel（结果列表），职责清晰易维护。",
            "useChat 的 api 指向后端 /api/writer，input 与 handleInputChange 双向绑定 textarea，handleSubmit 触发生成。",
            "computed 的 systemPrompt 把 写作模式/风格/字数 映射为不同系统提示词，实现「同一输入框切换多种任务」。",
            "结果区用 messages.filter(m => m.role === 'assistant') 过滤助手消息，配合 MarkdownRenderer 渲染并支持复制/导出。",
            "el-radio-group/el-select/el-slider 等 Element Plus 组件快速搭建控制面板，降低样式与交互成本。",
            "可扩展：把 writingMode 与后端流式接口解耦，便于接入不同模型或多轮改写。",
        ],
    ),
    "### 2.2 智能续写（Inline Completion）": (
        "在编辑器内实现「光标处自动补全」式智能续写：把光标前文本作为前缀发给模型，生成的内容以灰色预览叠加，用户按 Tab 接受。",
        "useCompletion 提供 completion/complete/isLoading 等状态，complete(prefix) 把光标前文本提交给 /api/complete；前端拿到 completion 后作为灰色预览展示，不直接替换正文，由用户决定是否采用，从而不打断原有写作流。",
        [
            "editorRef 用 ref 绑定 textarea，selectionStart 取出光标位置，slice(0, cursorPos) 得到前缀 prompt。",
            "useCompletion 的 complete(prefix) 触发补全请求，isLoading 控制按钮文案（续写中/ Tab 续写）。",
            "completion-preview 用弱提示样式（灰色）展示，避免与已写正文混淆，体现「非侵入式补全」。",
            "接受逻辑：用户按 Tab 时把 completion 插入光标处并清空预览，体验接近 IDE 的 Copilot。",
            "可结合防抖：停止输入 N 秒后再自动 complete，减少请求频次与 token 消耗。",
            "可扩展多候选：后端返回多个 completion，用户左右切换选择。",
        ],
    ),
    "### 3.1 文生图核心组件": (
        "实现文生图（Text-to-Image）的完整前端流程：收集正/负提示词与尺寸风格参数，调用后端批量生成，画廊展示并支持下载/用作参考。",
        "组件用 ref 收集 prompt/negativePrompt/imageSize/style，generate() 以 JSON POST 到 /api/generate-image，后端返回 urls 数组后填充 generatedImages；同时用 isGenerating 切换 el-button 的 loading 与 el-skeleton 骨架屏，提升等待体验。",
        [
            "正向 prompt 描述想要内容，negativePrompt（如 low quality, blurry）描述要规避内容，二者共同约束生成质量。",
            "imageSize 提供 1:1/16:9/9:16 三档，style 切换 vivid/natural，对应不同模型参数。",
            "一次 n:4 生成多张，generatedImages 数组驱动 v-for 画廊，每张可下载或「用作参考」回填 prompt。",
            "isGenerating 控制加载态：el-button :loading 与 v-if 骨架屏（el-skeleton）同步展示。",
            "downloadImage 用临时 a 标签 + a.click() 触发浏览器下载，文件名带 Date.now() 防重名。",
            "可扩展：加种子(seed)、采样步数、refiner 等高级参数，满足专业出图需求。",
        ],
    ),
    "### 3.2 图生图（图像上传 + 编辑）": (
        "实现图生图（Image-to-Image）：用户上传原图后，用自然语言描述修改意图，把原图与 prompt 一起提交给后端做可控编辑。",
        "handleFileUpload 用 FileReader.readAsDataURL 把文件读成 base64 预览；提交时 dataURLtoBlob 把 base64 还原为 Blob 放入 FormData（图片二进制），连同 editPrompt 一起 POST 到 /api/edit-image，后端返回编辑后的 url。",
        [
            "FileReader.readAsDataURL 实现本地即时预览，无需先上传即可展示原图。",
            "dataURLtoBlob 解析 dataURL 的 mime 与 base64，转成 Blob 才能走 FormData 二进制上传。",
            "FormData.append('image', blob) + append('prompt', text)，后端据此做 Instruct-Image 类编辑。",
            "上传区支持点击（input file）与拖拽（$refs.fileInput.click()）两种交互。",
            "editPrompt 描述「如何修改」，区别于文生图的正向 prompt，是图生图的核心输入。",
            "可扩展：预览裁切框、保留蒙版区域、多轮编辑历史回溯。",
        ],
    ),
    "### 4.1 语音输入（ASR）": (
        "把用户语音实时转成文字（ASR），用于替代键盘输入或作为对话入口。",
        "基于浏览器原生 Web Speech API 的 SpeechRecognition：构造实例后设 lang='zh-CN'、continuous=true（持续识别）、interimResults=true（返回中间结果）；onresult 把 event.results 拼接成 transcript，onerror 与 onUnmounted 负责清理，避免组件卸载后麦克风仍占用。",
        [
            "兼容性处理：(window).SpeechRecognition || (window).webkitSpeechRecognition 适配不同浏览器前缀。",
            "continuous=true 支持长句连续识别；interimResults=true 让文字随说话实时出现，体验更顺滑。",
            "onresult 中 Array.from(event.results).map(r => r[0].transcript).join('') 累积所有识别片段。",
            "录音按钮用 :class 绑定 recording 状态，配合 CSS 脉冲动画提示正在收音。",
            "onUnmounted 中 recognition.stop() 防止内存泄漏与麦克风常驻。",
            "降级方案：不支持时 alert 提示，并可回退到键盘输入或第三方 ASR SDK。",
        ],
    ),
    "### 4.2 语音输出（TTS）": (
        "把文本合成为语音播放（TTS），让 AI 回复「读」出来，提升无障碍与陪伴感。",
        "封装 useSpeech：用 SpeechSynthesisUtterance 承载文本与 lang/rate/pitch/voice 参数，speechSynthesis.speak() 播放；onvoiceschanged 监听语音列表加载，speak 前 cancel 上一条避免叠加，isSpeaking 反映播放状态。",
        [
            "SpeechSynthesisUtterance(text) 构造语音任务，可设 lang/rate(语速)/pitch(音高)/voice(具体嗓音)。",
            "speechSynthesis.getVoices() 获取可用嗓音，须监听 onvoiceschanged（部分浏览器异步加载）。",
            "speak 前调用 speechSynthesis.cancel() 取消上一段，避免多段语音叠播。",
            "utterance.onstart/onend 同步 isSpeaking，便于 UI 显示「正在朗读」与停止按钮。",
            "stop() 调 cancel() 并复位 isSpeaking，提供打断能力。",
            "可扩展：根据内容情感选择不同 voice，或接入云端高质量 TTS 提升音色。",
        ],
    ),
    "### 4.3 音频波形可视化": (
        "把麦克风或音频流的频谱实时绘制成动态波形/柱状图，提供直观的「声音可视化」反馈。",
        "借助 Web Audio 的 AudioContext 创建 MediaStreamSource 接入 AnalyserNode（fftSize=256 决定频域分辨率）；draw() 中 getByteFrequencyData 取出各频段能量，用 Canvas 的 fillRect 按能量高低画柱状条，requestAnimationFrame 形成逐帧动画。",
        [
            "AudioContext + createMediaStreamSource(stream) 把麦克风流接入分析链路。",
            "AnalyserNode.fftSize=256 时 frequencyBinCount=128，即 128 根频谱柱。",
            "getByteFrequencyData(dataArray) 填充 0~255 的频域强度，dataArray[i]/255 归一化柱高。",
            "Canvas 用 hsl(i*2,70%,50%) 做彩虹渐变着色，波形更美观。",
            "requestAnimationFrame(draw) 每帧重绘，cancelAnimationFrame 在卸载时停止，audioContext.close() 释放资源。",
            "可扩展：改为时域波形（getByteTimeDomainData）或圆形/粒子可视化。",
        ],
    ),
    "### 5.1 拖拽上传组件": (
        "实现支持拖拽与点击的多文件上传区，覆盖图片/音频/视频/PDF，并在上传前生成图片预览。",
        "用 dragover/dragleave/drop 三事件管理 isDragging 高亮态，dataTransfer.files 取拖入文件；图片类文件用 FileReader 生成 base64 缩略图，非图片不预览；upload() 用 FormData 多文件 append 后 POST，并通过 defineEmits 向父级 emit('upload') 通知。",
        [
            "dragover 必须 e.preventDefault() 才能触发 drop，否则浏览器会直接打开文件。",
            "isDragging 控制拖拽高亮样式，dragleave 复位，drop 取 e.dataTransfer.files。",
            "addFiles 中对 image/* 用 FileReader.readAsDataURL 生成预览，其他类型仅入列不预览。",
            "input type=file multiple 提供点击备选上传，accept 限制可选类型。",
            "upload() 用 FormData 一次 append 多个文件，POST 到 /api/multimodal 做多模态分析。",
            "emit('upload', files) 解耦上传逻辑与父组件后续处理（如进入分析流程）。",
        ],
    ),
    "### 5.2 PDF 预览": (
        "在前端直接渲染 PDF 文档页面到 Canvas，支持多页浏览，避免依赖后端转换或下载打开。",
        "引入 pdfjs-dist，设置 GlobalWorkerOptions.workerSrc 指向 worker 脚本；getDocument(pdfUrl).promise 加载文档，getPage(n) 取页，page.getViewport({scale}) 决定清晰度，page.render({canvasContext, viewport}) 把页面绘制到 canvas。",
        [
            "pdfjs-dist 是 Mozilla 的纯前端 PDF 解析库，无需服务端即可渲染。",
            "workerSrc 必须正确指向 pdf.worker.min.js，否则渲染会阻塞主线程或报错。",
            "getDocument(...).promise 返回带 numPages 的 PDFDocumentProxy，据此做分页控制。",
            "scale 参数（如 1.5）决定渲染分辨率，越大越清晰但越耗性能。",
            "render 返回 promise，需 await 完成后再切下一页，避免渲染竞态。",
            "可扩展：加缩放、旋转、文本层选择、缩略图侧边栏。",
        ],
    ),
    "## 5.3 图像编辑（Inpaint / Outpaint）": (
        "提供局部重绘（Inpaint）与扩图（Outpaint）能力：用户在画布上涂出遮罩区域，模型据此重绘或向指定方向延展画面。",
        "Canvas 上监听鼠标事件绘制红色遮罩（需 isDrawing 标志），endDraw 时 toDataURL 导出 mask；inpaint 把原图+mask+prompt 以 FormData 提交后端重绘，outpaint 则把方向参数以 JSON 提交做扩图。",
        [
            "initCanvas 加载原图到 canvas 并保存 ctx，作为绘制遮罩的底图。",
            "startDraw/moveTo 与 draw/lineTo 在 mousedown→mousemove 期间画出半透明红色遮罩。",
            "endDraw 调 canvas.toDataURL() 把遮罩区导出为图像（maskImage）。",
            "inpaint 用 dataURLtoBlob 把原图与 mask 转 Blob，FormData 提交 /api/inpaint。",
            "outpaint 传 direction（left/right/up/down），后端按方向扩展画布并生成新内容。",
            "遮罩即「告诉模型哪里要改」，是 Inpaint 可控生成的关键输入。",
        ],
    ),
    "## 5.4 Prompt 历史与风格预设": (
        "记录每次生成的完整参数与结果，并提供一组风格预设，方便快速复用与一致性出图。",
        "usePromptHistory 用 ref 从 localStorage 读取历史数组，addRecord 用 unshift 把新记录放最前并限长（MAX_HISTORY=50），变更后 save() 持久化；STYLE_PRESETS 是导出的一组预设 prompt 常量，供 UI 直接选用。",
        [
            "PromptRecord 结构保存 prompt/negativePrompt/style/size/timestamp/resultImage，便于一键回填复现。",
            "localStorage 做本地持久化，刷新不丢失，无需服务端存储。",
            "MAX_HISTORY=50 限制数组长度，超出 slice(0,50) 防止无限增长占用空间。",
            "addRecord 自动补 id(时间戳) 与 timestamp，unshift 使最新记录在最前。",
            "STYLE_PRESETS 集中管理 8 种风格 prompt（写实/动漫/油画/水彩/赛博朋克/极简/3D/像素），降低输入成本。",
            "可扩展：历史支持搜索、收藏、按风格筛选、导出/导入配置。",
        ],
    ),
    "## 5.5 批量生成与队列管理": (
        "把多个 prompt 放入任务队列，按并发上限逐个生成，实时展示各任务状态与进度。",
        "tasks ref 数组保存每个任务（pending/generating/done/error）；batchGenerate 把 prompts 入队后调用 processQueue，后者在 generating 数 < maxConcurrent 时取一个 pending 任务置为 generating 并 generateSingle，完成时 finally 里再次 processQueue，形成自驱动队列。",
        [
            "GenerateTask 状态机：pending→generating→done/error，驱动 UI 着色与进度。",
            "maxConcurrent=2 限制同时进行的请求数，防止把后端/显卡打满。",
            "computed 的 pendingCount/generatingCount 实时统计，供顶部队列状态展示。",
            "processQueue 用 while 循环「有空位且有待处理」就开新任务，实现并发节流。",
            "generateSingle 的 finally 调 processQueue() 处理下一个，保证队列持续推进不卡死。",
            "可扩展：加单任务重试、失败指数退避、进度百分比（由 SSE 或轮询获得）。",
        ],
    ),
    "## 5.6 PWA 离线与分享": (
        "把 Web 应用打包成可安装、可离线的 PWA，并集成系统级分享能力，提升移动端可用性。",
        "vite-plugin-pwa 的 VitePWA 在构建时生成 Service Worker 与 manifest：manifest 定义名称/图标/主题色，workbox.globPatterns 预缓存静态资源、runtimeCaching 对 API 用 NetworkFirst 做离线优先缓存；shareContent 用 navigator.share 调起原生分享，不支持时降级为复制链接。",
        [
            "VitePWA registerType:'autoUpdate' 让 SW 更新后自动激活，用户无感知。",
            "manifest 的 icons/theme_color 决定安装到桌面后的图标与状态栏配色。",
            "workbox.globPatterns 缓存 js/css/html 等，离线也能打开首屏。",
            "runtimeCaching 对 api.example.com 用 NetworkFirst：先请求网络，失败回退缓存，兼顾实时与离线。",
            "navigator.share({title,text,url}) 调起移动端系统分享面板（微信/短信等）。",
            "降级：无 navigator.share 时用 clipboard.writeText 复制链接并提示，保证可用性。",
        ],
    ),
    "### 6.1 Prompt 模板库": (
        "用带变量的模板统一管理常用 Prompt，支持占位符填充与本地保存，提升复用与协作效率。",
        "usePromptTemplates 维护 templates ref 数组（含 category/variables）；fillTemplate 用正则 /\\{(\\w+)\\}/g 把模板中的 {var} 替换为传入变量值，未提供则保留占位；saveTemplate 把新模板 push 进 localStorage 持久化。",
        [
            "PromptTemplate 含 id/name/category/template/variables，模板本身即「带占位符的提示词」。",
            "fillTemplate 正则 /\\{(\\w+)\\}/g 全局替换 {style}/{topic} 等变量，缺省回退 {key} 不破坏结构。",
            "variables 数组声明模板需要的入参，前端据此动态生成填表 UI。",
            "category 字段支持按「写作/编程」等分类管理，方便检索。",
            "saveTemplate 读 localStorage 现有数组→push→写回，实现自定义模板持久化。",
            "可扩展：模板导入导出、团队协作共享、基于历史的模板推荐。",
        ],
    ),
    "### 7.1 导出 Markdown/PDF": (
        "把 AI 生成内容导出为 Markdown 或 PDF 文件，方便留存、排版与分享。",
        "exportMarkdown 用 Blob([content], {type:'text/markdown'}) + URL.createObjectURL 触发下载；exportPDF 用 html2canvas 把 DOM 截成 canvas，再交给 jsPDF 的 addImage 按 A4 尺寸铺满生成 PDF 并 save。",
        [
            "Blob + URL.createObjectURL 是前端「内存文件→下载」的标准做法，用完 revokeObjectURL 释放。",
            "exportMarkdown 直接以 .md 下载纯文本，保留 Markdown 结构。",
            "html2canvas(element, {scale:2}) 提高截图清晰度，把元素渲染到 canvas。",
            "jsPDF('p','mm','a4') 创建纵向 A4，imgWidth=210mm，按宽高比算 imgHeight 防拉伸。",
            "pdf.addImage(imgData,'PNG',0,0,imgWidth,imgHeight) 把截图写入 PDF 再 save('x.pdf')。",
            "可扩展：分页截断长内容、加页眉页脚、直接打印 window.print()。",
        ],
    ),
    "### 7.2 分享链接": (
        "把生成内容直接编码进 URL，生成可一键打开/还原的分享链接，无需后端存储。",
        "generateShareLink 用 encodeURIComponent+btoa 把 UTF-8 内容安全地 base64 进 URL path；parseShareLink 反向用 atob+decodeURIComponent(escape()) 还原，实现「链接即内容」的轻量分享。",
        [
            "btoa(unescape(encodeURIComponent(content))) 正确处理中文等多字节字符，避免 base64 乱码。",
            "链接形如 /share/{encoded}，打开分享页时从路径或 hash 取编码串再解码。",
            "parseShareLink 用 decodeURIComponent(escape(atob(hash))) 反向还原原始文本。",
            "优点：零后端存储，链接自带内容，适合临时/轻量分享。",
            "缺点：URL 长度受浏览器限制，过长内容需改为「先上传拿 id 再分享」。",
            "可扩展：对编码内容做压缩（如 lz-string）以缩短链接，或加过期签名。",
        ],
    ),
}

NEW_LINES, ADDED = expand(
    PATH,
    content_map,
    add_top_note=True,
    add_summary=False,
    summary_text="",
)

print(f"Vue3 AIGC: new_lines={NEW_LINES}, added_blocks={ADDED}")
