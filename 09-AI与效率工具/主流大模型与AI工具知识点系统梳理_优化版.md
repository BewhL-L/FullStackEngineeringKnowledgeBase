---
title: 主流大模型与AI工具知识点系统梳理
tags: [AI与效率工具, 大模型, AI工具, GPT, Claude, Gemini, 文心, 通义, 豆包, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# 主流大模型与 AI 工具知识点系统梳理（优化版）

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。


> **文档说明**：系统梳理当前主流大语言模型与 AI 工具，涵盖国际/国内大模型对比、AI 编程工具、内容创作工具、效率工具、选型建议。

---

## 1. 概述

大模型（LLM）已形成国际与国内双轨发展格局，AI 工具渗透到编程、内容创作、办公、设计等各个领域。了解各模型特点和工具生态，是高效使用 AI 的基础。

**大模型分类**：
- **闭源商业模型**：GPT-4o、Claude 3.5、Gemini 1.5、文心一言、通义千问、豆包
- **开源模型**：Llama 3、Qwen（通义开源）、DeepSeek、Mistral、Phi
- **小模型/端侧**：Phi-3、Qwen2.5-0.5B、MobileLLM

---


---
## 2. 国际主流大模型

### 2.1 OpenAI GPT 系列

| 模型 | 特点 | 上下文 | 适用场景 |
|------|------|--------|----------|
| GPT-4o | 多模态（图文音视频），速度快，推理强 | 128K | 通用最强，复杂推理、多模态 |
| GPT-4 Turbo | 文本强，成本较低 | 128K | 长文本、代码、分析 |
| GPT-3.5 Turbo | 速度快，成本低 | 16K | 日常对话、简单任务 |

**优势**：综合能力最强，生态最完善（API、插件、Custom GPT），工具调用成熟。
**劣势**：价格较高，国内访问需特殊网络。


> 🔍 **知识点深度解析**
>
> **作用**：OpenAI GPT 系列是最具影响力的 LLM 产品线，从 GPT-1 到 GPT-4o 持续引领行业。
>
> **原理**：GPT-1/2/3 验证了规模定律（Scaling Law）。GPT-3.5（ChatGPT）引爆对话式 AI。GPT-4 提升推理能力。GPT-4 Turbo 支持 128K 上下文。GPT-4o（omni）实现原生多模态和实时语音。GPT-4o-mini 是高性价比小模型。o1 系列引入推理模型（思维链强化学习，慢思考）。API 提供 Chat Completions/Assistants/Batch/Realtime 等接口。
>
> **用法要点**：① GPT-4o：旗舰多模态，实时语音视觉  ② o1/o3：推理模型，强化学习训练思维链，科学/数学强  ③ GPT-4o-mini：高性价比，适合简单任务  ④ 128K 上下文，Batch API 半价，Function Calling 支持  ⑤ 面试常考：GPT 系列演进、o1 推理模型、GPT-4o 多模态

### 2.2 Anthropic Claude

| 模型 | 特点 | 上下文 |
|------|------|--------|
| Claude 3.5 Sonnet | 性价比极高，代码和推理强 | 200K |
| Claude 3 Opus | 最强推理，适合复杂任务 | 200K |
| Claude 3 Haiku | 速度快，成本低 | 200K |

**优势**：长上下文（200K）、安全性好、写作质量高、不易拒绝合理请求。
**劣势**：多模态能力弱于 GPT-4o，国内访问需特殊网络。


> 🔍 **知识点深度解析**
>
> **作用**：Anthropic Claude 以安全性、长上下文和强写作能力著称，Constitutional AI 方法论代表。
>
> **原理**：Claude 3 系列（Haiku/ Sonnet/Opus）分三档：Haiku 快速轻量、Sonnet 性价比平衡、Opus 最强推理。Claude 3.5 Sonnet 在编码和视觉方面表现突出。支持 200K 上下文（约 15 万词）。Constitutional AI：用一组原则指导模型对齐，减少有害输出。Claude API 支持 Messages 格式、Tool Use、Vision、PDF 直接处理。以长文档分析和代码能力闻名。
>
> **用法要点**：① 三档模型：Haiku（快/便宜）、Sonnet（平衡）、Opus（最强）  ② 200K 长上下文，适合长文档和代码库分析  ③ Constitutional AI：原则驱动对齐，安全性高  ④ Claude 3.5 Sonnet 编码能力强，性价比高  ⑤ 面试常考：Claude 模型档位、Constitutional AI、长上下文

### 2.3 Google Gemini

| 模型 | 特点 | 上下文 |
|------|------|--------|
| Gemini 1.5 Pro | 超长上下文（1M+），多模态 | 1M-2M |
| Gemini 1.5 Flash | 速度快，成本低 | 1M |
| Gemini 2.0 | 新一代，多模态增强 | - |

**优势**：超长上下文（可处理整本书/代码库）、Google 搜索集成、多模态强。
**劣势**：中文能力略弱，国内访问需特殊网络。


> 🔍 **知识点深度解析**
>
> **作用**：Google Gemini 是原生多模态模型系列，深度集成 Google 搜索和 Workspace 生态。
>
> **原理**：Gemini 从设计上原生支持多模态（非拼接），在 TPU 上训练。型号：Gemini 2.5 Pro（旗舰，1M 上下文）、Gemini Flash（快速高性价比）。深度集成 Google 搜索（实时信息）、Google Workspace（Docs/Gmail/Calendar）。Gemini Advanced 消费端产品。Google 还提供开源模型 Gemma。Vertex AI 是企业级平台。长上下文（1M-2M token）是其差异化优势。
>
> **用法要点**：① 原生多模态架构（非文本+视觉拼接）  ② Gemini 2.5 Pro 支持 1M+ token 超长上下文  ③ 深度集成 Google 搜索获取实时信息  ④ Gemma 是开源版本，Vertex AI 企业平台  ⑤ 面试常考：Gemini 原生多模态、长上下文、Google 生态

### 2.4 Meta Llama（开源）

- Llama 3 / Llama 3.1：开源模型标杆，8B/70B/405B
- 支持商用（需申请），可本地部署和微调
- 社区生态丰富，是开源微调的基础模型
- 上下文最高 128K（Llama 3.1）

---


> 🔍 **知识点深度解析**
>
> **作用**：Meta Llama 系列是最有影响力的开源 LLM，Llama 2/3/4 推动了开源 AI 生态繁荣。
>
> **原理**：Llama 1（研究）→ Llama 2（免费商用）→ Llama 3（8B/70B，性能接近 GPT-4 级别）→ Llama 4（MoE 架构）。Llama 开源权重允许微调、量化和本地部署，催生了庞大的微调模型生态（Alpaca/Vicuna 等）。Llama 3.1 405B 是最大开源稠密模型。开源模型优势：数据隐私、成本可控、可定制，适合企业私有部署和边缘设备。
>
> **用法要点**：① Llama 3/3.1：8B/70B/405B，开源权重可商用  ② 开源生态最活跃：Alpaca/Vicuna/CodeLlama 等微调  ③ MoE 架构（Llama 4）降低推理成本  ④ 开源优势：隐私/成本/定制，适合私有部署  ⑤ 面试常考：Llama 版本演进、开源 vs 闭源、MoE、本地部署


---
## 3. 国内主流大模型

### 3.1 模型对比

| 模型 | 厂商 | 特点 | 上下文 |
|------|------|------|--------|
| **豆包（Doubao）** | 字节跳动 | 综合能力强，多模态，生态丰富（抖音/飞书集成） | 128K |
| **通义千问（Qwen）** | 阿里 | 开源+闭源双线，代码能力强，Qwen2.5 性能优秀 | 128K |
| **文心一言（ERNIE）** | 百度 | 中文理解强，搜索增强，文心一格画图 | 128K |
| **DeepSeek** | 深度求索 | 开源，代码和推理强，性价比高 | 128K |
| **智谱清言（GLM）** | 智谱 AI | 开源 GLM 系列，学术背景强 | 128K |
| **Kimi** | 月之暗面 | 超长上下文（2M），长文档处理强 | 2M |
| **讯飞星火** | 科大讯飞 | 语音能力强，教育领域深耕 | - |


> 🔍 **知识点深度解析**
>
> **作用**：从能力、速度、成本、上下文长度和开源/闭源等维度对比主流模型，按场景选型。
>
> **原理**：GPT-4o/Claude 3.5 Opus 能力最强但最贵最慢，适合复杂推理和多模态。Claude 3.5 Sonnet/GPT-4o-mini 性价比高，适合日常开发和写作。开源模型（Llama 3/Qwen/DeepSeek）可私有部署，适合数据敏感场景。选型维度：推理能力（MMLU/GSM8K）、编码（HumanEval/SWE-bench）、上下文长度、延迟、价格、隐私要求。简单任务用小模型，复杂任务用大模型，路由策略降本。
>
> **用法要点**：① 旗舰模型：GPT-4o/Claude Opus/Gemini Pro，复杂任务  ② 性价比模型：GPT-4o-mini/Claude Sonnet/Haiku，日常任务  ③ 开源模型：Llama 3/Qwen2.5/DeepSeek，私有部署  ④ 选型看：能力基准+延迟+价格+上下文+隐私  ⑤ 模型路由：简单任务小模型，复杂任务大模型，降本 50%+

### 3.2 选型建议

- **日常使用/多模态**：豆包、文心一言（国内访问方便）
- **长文档处理**：Kimi（2M 上下文）、通义千问
- **代码开发**：DeepSeek-Coder、通义千问、GPT-4o
- **本地部署/微调**：Qwen2.5、Llama 3、DeepSeek
- **企业私有化**：Qwen、GLM、DeepSeek（开源可商用）

> 🔍 **知识点深度解析**
>
> **作用**：大模型选型是 AI 应用的第一步，不同模型各有所长。
>
> **原理**：大模型能力主要由三个因素决定：参数量（规模）、训练数据（质量和数量）、对齐方法（SFT/RLHF）。闭源模型通过 API 提供服务，持续迭代优化，能力最强但成本高、数据需上传。开源模型可本地部署、数据不出域、可定制微调，但能力略逊于顶尖闭源模型。上下文窗口决定能处理的文本长度，128K 约 10 万字，1M 约 80 万字。推理速度与模型大小、量化、硬件相关。国内模型在中文理解、合规性、访问便利性上有优势。
>
> **用法要点**：① 简单任务用便宜模型（GPT-3.5/Haiku/Flash），复杂任务用强模型；② 敏感数据用本地部署开源模型；③ 长文档用长上下文模型（Kimi/Gemini）；④ 多模型组合用，各取所长；⑤ 面试常考：主流模型对比、开源vs闭源、上下文窗口、模型选型、国内大模型特点。

---


---
## 4. AI 编程工具

### 4.1 代码补全与生成

| 工具 | 特点 |
|------|------|
| **GitHub Copilot** | VS Code/JetBrains 插件，实时代码补全，GPT-4 驱动 |
| **Cursor** | AI 原生 IDE，支持代码库级理解、Agent 模式、多文件编辑 |
| **Codeium** | 免费代码补全，支持多 IDE |
| **通义灵码** | 阿里出品，中文友好，支持 VS Code/JetBrains |
| **豆包 MarsCode** | 字节出品，AI 编程助手 |
| **Amazon Q Developer** | AWS 出品，AWS 集成 |


> 🔍 **知识点深度解析**
>
> **作用**：AI 代码工具从自动补全发展到 Agent 化编程，覆盖补全、生成、调试、测试和重构全流程。
>
> **原理**：代码补全：GitHub Copilot（GPT  Codex）基于上下文实时建议行/块补全。代码生成：Cursor Composer/Agent 可根据自然语言生成多文件代码。代码解释：CodeLlama/StarCoder 开源代码模型。AI 编程工具理解整个代码库（代码 RAG），提供上下文感知的建议。从辅助工具向自主编程 Agent 演进（Devin/SWE-agent）。
>
> **用法要点**：① GitHub Copilot：行级/块级补全，IDE 集成  ② Cursor：AI-first IDE，Composer 多文件编辑，Agent 模式  ③ 代码模型：CodeLlama/StarCoder/DeepSeek-Coder 开源  ④ 代码 RAG：检索仓库相关代码作为上下文  ⑤ 面试常考：Copilot 原理、Cursor Agent、代码模型、AI 编程趋势

### 4.2 Cursor 核心功能

- **Cmd+K**：选中代码，AI 编辑/解释/优化
- **Cmd+L**：对话模式，基于代码库上下文问答
- **Agent 模式**：自动理解需求，多文件修改，运行测试
- **@ 引用**：@文件、@函数、@文档，精准提供上下文
- **Composer**：多文件同时编辑


> 🔍 **知识点深度解析**
>
> **作用**：Cursor 是 AI-first 代码编辑器，核心功能包括 Tab 补全、Cmd+K 内联编辑、Composer 多文件和 Agent 模式。
>
> **原理**：Tab 智能补全：根据最近编辑预测下一处修改（copilot++）。Cmd+K：选中代码用自然语言指令修改。Cmd+L：对话提问（可引用代码/文件/文档）。Composer：生成和修改多个文件，自动创建/编辑文件。Agent 模式：自主执行终端命令、运行测试、根据错误修正。Cursor 索引整个代码库提供仓库级上下文。支持 .cursorrules 文件定义项目规范。
>
> **用法要点**：① Tab 补全：预测下一处编辑，不只是当前行  ② Cmd+K 内联编辑，Cmd+L 对话引用代码  ③ Composer：多文件生成和编辑  ④ Agent：执行命令+运行测试+自动调试  ⑤ .cursorrules 定义项目编码规范和技术栈

### 4.3 代码审查与优化

- **CodeRabbit**：AI 代码审查，PR 自动评论
- **Sourcery**：代码质量优化建议
- **SonarQube + AI**：传统代码质量 + AI 增强

---


> 🔍 **知识点深度解析**
>
> **作用**：AI 辅助代码审查可自动检测 Bug、安全漏洞、性能问题和风格问题，提升代码质量。
>
> **原理**：AI 审查工具（Copilot Review/Cursor Review/CodeRabbit）分析 PR diff，标注潜在问题：空指针、资源泄漏、SQL 注入、XSS、竞态条件、复杂度。AI 优化建议：识别重复代码、提出更高效算法、建议设计模式。最佳实践：AI 审查作为人工审查的补充而非替代，AI 标注的问题需人工确认，关注 AI 漏报（false negative）。
>
> **用法要点**：① AI 审查 PR diff：Bug/安全/性能/风格  ② 安全漏洞检测：SQL 注入/XSS/硬编码密钥  ③ AI 建议需人工确认，存在误报和漏报  ④ 结合静态分析工具（SonarQube）效果更好  ⑤ AI 审查是辅助，最终责任在开发者


---
## 5. AI 内容创作工具

### 5.1 文本创作

| 工具 | 用途 |
|------|------|
| **ChatGPT / Claude** | 通用文案、文章、邮件 |
| **Notion AI** | 笔记内 AI 写作、总结、翻译 |
| **Jasper** | 营销文案专业工具 |
| **秘塔写作猫** | 中文写作纠错、润色 |


> 🔍 **知识点深度解析**
>
> **作用**：AI 文本创作工具覆盖写作、润色、翻译、摘要和营销文案，提升内容生产效率。
>
> **原理**：ChatGPT/Claude 通用写作：文章/邮件/报告/方案。Notion AI：文档内写作和润色。Jasper/Copy.ai：营销文案专用。润色工具：GrammarlyGO（语法+风格）。长文写作：用 Prompt Chaining（大纲→分段→润色）质量更高。AI 写作关键：给足上下文（受众/目的/风格）、迭代修改、人工审核事实。AI 是草稿生成器，人类负责最终质量。
>
> **用法要点**：① 通用写作：ChatGPT/Claude/Doubao  ② Notion AI：文档内嵌写作，适合知识库  ③ 营销文案：Jasper/Copy.ai 模板化  ④ 长文用链式 Prompt：大纲→分段→润色  ⑤ AI 生成草稿，人工审核事实和风格

### 5.2 图像生成

| 工具 | 特点 |
|------|------|
| **Midjourney** | 画质最高，艺术风格，Discord 交互 |
| **Stable Diffusion** | 开源免费，可本地部署，LoRA/ControlNet 生态 |
| **DALL·E 3** | ChatGPT 集成，提示词理解强 |
| **即梦 AI** | 字节出品，文生图/视频，国内访问方便 |
| **通义万相** | 阿里出品，图像生成 |
| **可画（Canva）AI** | 设计模板 + AI 生成 |


> 🔍 **知识点深度解析**
>
> **作用**：AI 图像生成基于扩散模型，代表工具包括 Midjourney、Stable Diffusion、DALL-E 和 ComfyUI。
>
> **原理**：扩散模型原理：从噪声图像逐步去噪生成清晰图像（Stable Diffusion）。Midjourney：商业产品，艺术质量最高，Discord/Web 操作。Stable Diffusion：开源，可本地部署，ControlNet 控制构图/姿态，LoRA 微调风格。DALL-E 3：ChatGPT 集成，提示词理解好。ComfyUI：节点式工作流，精确控制生成流程。提示词技巧：主体+风格+光影+构图+质量词。
>
> **用法要点**：① 扩散模型：噪声→去噪→图像，Stable Diffusion 开源  ② Midjourney：艺术质量最高，商业 API  ③ ControlNet：线稿/姿态/深度图控制生成构图  ④ LoRA：少量数据训练特定风格/人物/物体  ⑤ 面试常考：扩散模型原理、SD 生态、ControlNet、提示词技巧

### 5.3 视频生成

| 工具 | 特点 |
|------|------|
| **Sora** | OpenAI，文生视频，画质和逻辑强 |
| **Runway Gen-3** | 专业视频生成，图生视频 |
| **Pika** | 简单易用，风格化视频 |
| **即梦 AI** | 国内视频生成，支持图文生视频 |
| **剪映 AI** | 视频剪辑 + AI 功能（数字人、字幕、配乐） |


> 🔍 **知识点深度解析**
>
> **作用**：AI 视频生成从文生视频到图生视频和视频编辑，代表有 Sora、Runway、Pika 和可灵。
>
> **原理**：技术路线：扩散模型视频版（Sora/Runway Gen-3）、自回归 Transformer（视频 token 预测）。Sora（OpenAI）使用 DiT（Diffusion Transformer）生成高一致性长视频。Runway Gen-3：专业视频生成和编辑。Pika：动画/创意视频。可灵（快手）：国产视频生成。当前限制：时长（几秒到几十秒）、物理一致性、复杂动作。应用：广告/短视频/原型/故事板。
>
> **用法要点**：① Sora：DiT 架构，时空 patch，高一致性长视频  ② Runway Gen-3：专业级视频生成+编辑  ③ 可灵/即梦：国产视频模型，中文理解好  ④ 当前限制：时长/物理规律/复杂交互  ⑤ 应用：广告创意/故事板/短视频素材

### 5.4 音频生成

| 工具 | 用途 |
|------|------|
| **Suno** | AI 音乐生成（词曲唱一体） |
| **ElevenLabs** | 语音合成，音色克隆 |
| **剪映** | 文字转语音、AI 配音 |

---


> 🔍 **知识点深度解析**
>
> **作用**：AI 音频包括语音合成（TTS）、语音识别（ASR）、音乐生成和声音克隆。
>
> **原理**：TTS：ElevenLabs（最自然语音，支持声音克隆）、OpenAI TTS API、Azure TTS。ASR：Whisper（OpenAI 开源，多语言识别+翻译）。音乐生成：Suno/Udio（文生歌曲，含人声）。声音克隆：几秒参考音频即可克隆音色（伦理风险）。实时语音：GPT-4o Realtime API 端到端低延迟语音对话。
>
> **用法要点**：① TTS：ElevenLabs 质量最高，OpenAI TTS 性价比好  ② ASR：Whisper 开源，多语言，可本地部署  ③ 音乐：Suno/Udio 文生完整歌曲  ④ 声音克隆伦理风险：需授权同意  ⑤ 实时语音：端到端模型延迟 <500ms


---
## 6. AI 效率工具

### 6.1 办公效率

| 工具 | 用途 |
|------|------|
| **Microsoft Copilot** | Office 全家桶 AI（Word/Excel/PPT/Outlook） |
| **WPS AI** | 国内办公 AI，文档/表格/PPT |
| **飞书智能伙伴** | 飞书文档/会议/多维表格 AI |
| **Notion AI** | 笔记 + AI 写作/总结 |
| **Gamma** | AI 生成 PPT，输入主题自动生成 |
| **Tome** | AI 演示文稿 |


> 🔍 **知识点深度解析**
>
> **作用**：AI 办公工具集成到文档/表格/邮件/会议流程，自动化重复性知识工作。
>
> **原理**：Microsoft Copilot：嵌入 Word/Excel/PowerPoint/Outlook/Teams，基于文档数据生成内容和分析。Google Duet AI：Workspace 集成。WPS AI：国产办公套件 AI。会议：Otter.ai/飞书妙记 自动转写和总结。邮件：AI 起草回复和摘要。PPT：Gamma/Tome AI 生成演示文稿。Excel：AI 公式生成和数据分析。关键：AI 访问企业数据需注意权限和安全。
>
> **用法要点**：① Microsoft Copilot：M365 全家桶深度集成  ② 会议转写：Otter/飞书妙记/Teams Premium  ③ PPT 生成：Gamma/Tome 一键生成演示  ④ Excel/Sheets：自然语言生成公式和分析  ⑤ 企业数据安全：权限控制和数据隔离

### 6.2 搜索与研究

| 工具 | 用途 |
|------|------|
| **Perplexity** | AI 搜索引擎，带引用来源 |
| **秘塔 AI 搜索** | 国内 AI 搜索，学术搜索强 |
| **Felo** | AI 搜索，多语言 |
| **Elicit** | 学术论文 AI 搜索与分析 |
| **Consensus** | 学术研究 AI 问答 |


> 🔍 **知识点深度解析**
>
> **作用**：AI 搜索引擎和研究工具改变信息获取方式，从关键词匹配到问答式研究。
>
> **原理**：Perplexity：AI 搜索引擎，给出带引用的直接答案而非链接列表。Google AI Overviews：搜索结果中嵌入 AI 摘要。Consensus：学术论文搜索，基于研究证据回答。Elicit：AI 文献综述助手。Deep Research：多步搜索+阅读+综合报告（GPT/Perplexity/Gemini）。AI 搜索核心：检索+阅读+综合+引用，比传统搜索更高效但需验证来源。
>
> **用法要点**：① Perplexity：带引用的 AI 答案，对话式搜索  ② Consensus/Elicit：学术文献 AI 检索和综述  ③ Deep Research：自动多步搜索+长报告（30 分钟级）  ④ AI 搜索仍需验证来源和事实  ⑤ 面试常考：AI 搜索 vs 传统搜索、RAG 搜索、引用验证

### 6.3 知识管理

| 工具 | 用途 |
|------|------|
| **Obsidian + 插件** | 本地知识库 + AI 插件 |
| **Notion AI** | 云端知识库 + AI |
| **Logseq** | 大纲式笔记 + AI |
| **飞书知识库** | 企业知识库 + AI 问答 |

---


> 🔍 **知识点深度解析**
>
> **作用**：AI 增强知识管理工具实现智能笔记、自动标签、语义搜索和知识问答。
>
> **原理**：Notion AI：文档内写作/摘要/翻译/问答。Obsidian + AI 插件：Copilot/ Smart Composer 实现笔记问答和写作辅助。Mem：AI 笔记自动组织和关联。AI 知识管理核心：RAG over personal notes（向量化笔记库，自然语言查询）。AI 自动标签和摘要减少手动整理负担。企业知识库+RAG 构建内部问答助手。
>
> **用法要点**：① Notion AI：写作+摘要+问答一体化  ② Obsidian Copilot/Smart Composer：本地笔记 RAG  ③ AI 自动标签/摘要/关联，减少整理成本  ④ 个人知识库 RAG：自然语言查询自己的笔记  ⑤ 企业知识库：RAG+权限控制构建内部问答


---
## 7. AI Agent 平台

- **Dify**：开源 LLMOps 平台，可视化搭建 AI 应用和 Agent
- **Coze（扣子）**：字节出品，Bot 搭建平台，支持插件/工作流
- **LangChain**：AI 应用开发框架
- **n8n + AI**：工作流自动化 + AI 节点
- **Zapier AI**：无代码 AI 自动化

---


---
## 8. 工具选型原则

1. **任务匹配**：简单对话用免费工具，专业任务用付费强模型
2. **数据安全**：敏感数据用本地部署/私有化，不用云端 API
3. **成本控制**：按 Token 计费的 API 注意用量，简单任务用小模型
4. **生态集成**：选择与现有工作流集成好的工具（VS Code→Copilot/Cursor，飞书→智能伙伴）
5. **多工具组合**：不同工具各有所长，组合使用效果最佳

---

## 8.1 模型评测基准

| 基准 | 评测维度 | 说明 |
|------|----------|------|
| **MMLU** | 综合知识 | 57个学科多选题 |
| **GSM8K** | 数学推理 | 小学应用题 |
| **HumanEval** | 代码生成 | Python函数生成 |
| **MT-Bench** | 对话质量 | 多轮对话GPT-4打分 |
| **MMLU-Pro** | 高级知识 | 更难的专业题 |
| **AGIEval** | 人类考试 | 高考/公考等 |

---


> 🔍 **知识点深度解析**
>
> **作用**：LLM 评测基准从知识、推理、代码、数学和多维度评估模型能力，指导模型选型。
>
> **原理**：通用能力：MMLU（多任务知识）、C-Eval（中文）、AGIEval。推理：GSM8K（数学）、MATH、ARC、BBH（BIG-Bench Hard）。代码：HumanEval、MBPP、SWE-bench（真实 Issue）。长上下文：Needle-in-Haystack、LongBench。多模态：MMMU、MMBench。Agent：AgentBench、GAIA。聊天：Chatbot Arena（人类盲评 Elo）。注意：基准成绩≠实际体验，需结合具体任务测试。
>
> **用法要点**：① MMLU：57 学科知识，C-Eval：中文学科  ② GSM8K/MATH：数学推理，HumanEval：代码生成  ③ Chatbot Arena：人类盲评 Elo 排名，最贴近体验  ④ SWE-bench：真实 GitHub Issue 修复  ⑤ 选型建议：看相关基准+自己任务测试，不唯分数

## 8.2 开源模型本地部署

| 工具 | 特点 |
|------|------|
| **Ollama** | 最简单，一行命令拉取运行，支持量化 |
| **vLLM** | 高性能推理，PagedAttention，连续批处理，生产首选 |
| **LM Studio** | 图形界面，适合非技术用户 |
| **text-generation-inference** | HuggingFace 出品，生产级 |

```bash

> 🔍 **知识点深度解析**
>
> **作用**：开源模型本地部署通过 Ollama/llama.cpp/vLLM 等工具实现，兼顾隐私、成本和定制。
>
> **原理**：Ollama：最简单的本地运行方案（ollama run llama3），自动下载量化模型。llama.cpp：C/C++ 实现，CPU/GPU 混合推理，GGUF 格式，支持 CPU 推理。vLLM：生产级服务，PagedAttention 高吞吐，OpenAI 兼容 API。LM Studio：图形界面，适合非技术用户。硬件选择：7B 模型需 8GB 显存（INT4），70B 需 40GB+。Mac M 系列统一内存效果好。
>
> **用法要点**：① Ollama：一行命令本地运行，开发测试首选  ② llama.cpp：CPU 可跑，GGUF 量化，边缘设备  ③ vLLM：生产部署，高吞吐，OpenAI 兼容 API  ④ 7B INT4 约 5GB 显存，70B INT4 约 35GB  ⑤ Mac M 系列统一内存跑大模型性价比高

# Ollama 示例
ollama run qwen2.5:7b        # 拉取并运行通义千问7B
ollama run llama3.1:8b       # 运行 Llama 3.1 8B

# vLLM 启动 OpenAI 兼容 API
python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-7B-Instruct
```

---

## 8.3 模型量化与推理加速

| 量化方法 | 精度 | 显存节省 | 质量损失 |
|----------|------|----------|----------|
| **FP16/BF16** | 16位 | 基准 | 无 |
| **INT8** | 8位 | ~50% | 极小 |
| **INT4（GPTQ）** | 4位 | ~75% | 小 |
| **INT4（AWQ）** | 4位 | ~75% | 更小（激活感知） |

**推理加速技术**：
- **PagedAttention**（vLLM）：分页管理 KV Cache，显存利用率提升
- **连续批处理**（Continuous Batching）：动态合并请求，吞吐量提升
- **KV Cache**：缓存历史 Key/Value，避免重复计算
- **投机解码**：小模型草稿 + 大模型验证，加速推理

---


> 🔍 **知识点深度解析**
>
> **作用**：模型量化降低权重精度减少显存和计算，配合推理引擎实现低成本高效部署。
>
> **原理**：量化精度：FP32→FP16/BF16→INT8→INT4，显存成倍降低。量化方法：GPTQ（训练后量化，需校准数据）、AWQ（激活感知量化）、GGUF（llama.cpp 格式）、bitsandbytes（NF4）。推理引擎：vLLM（PagedAttention）、TensorRT-LLM（NVIDIA 优化）、TGI（HuggingFace）、SGLang。量化精度损失：7B INT4 通常损失 <5%，可接受。
>
> **用法要点**：① INT4 量化：显存降 75%，精度损失通常可接受  ② GPTQ/AWQ：训练后量化，GGUF：llama.cpp 格式  ③ vLLM PagedAttention：吞吐量提升 5-20 倍  ④ TensorRT-LLM：NVIDIA 官方极致优化  ⑤ 面试常考：量化原理、GPTQ/AWQ/GGUF、vLLM、精度损失


---
## 9. 面试高频考点

1. **主流大模型对比**：GPT/Claude/Gemini/国内模型特点
2. **开源 vs 闭源**：优缺点、适用场景
3. **上下文窗口**：含义、各模型对比、长上下文价值
4. **AI 编程工具**：Cursor/Copilot 功能与使用
5. **图像生成工具**：Midjourney vs Stable Diffusion
6. **国内大模型**：豆包/通义/文心/DeepSeek 特点
7. **AI 效率工具**：办公/搜索/知识管理工具
8. **模型选型**：根据场景选择合适模型
9. **多模态模型**：GPT-4o/Gemini 能力
10. **AI Agent 平台**：Dify/Coze/LangChain
11. **评测基准**：MMLU/GSM8K/HumanEval/MT-Bench
12. **本地部署**：Ollama/vLLM/LM Studio 对比
13. **模型量化**：GPTQ/AWQ/INT4/INT8，质量与显存权衡
14. **推理加速**：PagedAttention/连续批处理/KV Cache/投机解码
15. **API成本**：按Token计费，输入/输出价格差异，成本估算

---


---
## 📝 精简总结

- 国际大模型：GPT-4o（综合最强）、Claude 3.5（长文+安全）、Gemini（超长上下文）、Llama（开源标杆）
- 国内大模型：豆包（综合）、通义千问（代码+开源）、文心一言（中文+搜索）、DeepSeek（开源代码强）、Kimi（超长上下文）
- 编程工具：Cursor（AI原生IDE）、GitHub Copilot（补全）、通义灵码（国内）
- 图像：Midjourney（画质最高）、Stable Diffusion（开源可控）、即梦（国内）
- 视频：Sora/Runway/Pika/即梦，音频：Suno/ElevenLabs
- 办公：Microsoft Copilot/WPS AI/飞书智能伙伴/Gamma（PPT）
- 搜索：Perplexity/秘塔AI搜索，研究：Elicit/Consensus
- 评测基准：MMLU（综合知识）、GSM8K（数学）、HumanEval（代码）、MT-Bench（对话）
- 本地部署：Ollama（最简单）、vLLM（高性能生产首选，PagedAttention+连续批处理）
- 模型量化：INT8损失极小，INT4（GPTQ/AWQ）省75%显存，AWQ质量更好
- 推理加速：KV Cache、PagedAttention、连续批处理、投机解码
- 选型：任务匹配、数据安全、成本控制、生态集成、多工具组合

---

[[09-AI与效率工具/MOC-AI与效率工具|← 返回 AI 与效率工具 MOC]] | [[Home|🏠 返回首页]]
