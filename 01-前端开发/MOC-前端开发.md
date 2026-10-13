---
title: 前端开发 MOC
tags: [JavaScript, Vue3, TypeScript, AI前端, MOC, 前端, CSS, 工程化]
category: 前端开发
created: 2026-08-12
updated: 2026-09-01
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: []
aliases: [MOC-前端开发]
---

# 🎨 前端开发 MOC

> 基于 Vue3 + TypeScript 的现代前端技术栈，覆盖基础语言、Vue3生态、工程化构建、AI前端集成、性能与安全、组件与UI六大领域，共 86 篇文档。
>
> **学习建议**：先掌握 HTML/CSS/JavaScript 基础，再深入 Vue3 + TypeScript，然后学习工程化构建，最后探索 AI 前端集成和性能优化。

---

## 📚 学习路线

```text
入门阶段：HTML/CSS基础 → JavaScript基础 → Vue3快速上手 → TypeScript入门
进阶阶段：Vue3深入(组合式API/响应式原理) → Pinia状态管理 → VueRouter → ElementPlus
高级阶段：工程化(Vite/ESLint/Monorepo) → 性能优化 → 安全防护 → 组件库设计
专家阶段：AI前端集成(SSE流式/对话UI/RAG展示) → 微前端 → 架构设计 → 源码原理
```

---

## 📂 文档索引

### 一、基础语言

| 文档 | 说明 | 难度 |
|------|------|------|
| [[HTML5与CSS3基础入门]] | HTML5语义化标签、CSS3选择器、盒模型、布局基础 | 🟢入门 |
| [[HTML5语义化与基础标签]] | HTML5语义化标签、SEO优化、无障碍访问、表单元素 | 🟢入门 |
| [[CSS 进阶知识点系统梳理_优化版\|CSS进阶知识点系统梳理]] | Flexbox、Grid、BFC、定位、动画、响应式、性能优化 | 🟡进阶 |
| [[CSS3布局与样式基础]] | CSS3布局、Flexbox、Grid、渐变、变换、过渡动画 | 🟢入门 |
| [[UnoCSS-Tailwind原子化CSS]] | 原子化CSS、Tailwind CSS、UnoCSS、按需生成、设计系统 | 🟡进阶 |
| [[JavaScript 核心知识点系统梳理_优化版\|JavaScript核心知识点系统梳理]] | ES6+、原型链、闭包、异步编程、事件循环、面试考点 | 🟡进阶 |
| [[JavaScript-ES6核心语法]] | ES6新特性、let/const、箭头函数、解构、Promise、模块化 | 🟢入门 |
| [[JavaScript核心语法与ES6+]] | JavaScript核心语法、ES6+新特性、异步编程、面向对象 | 🟡进阶 |
| [[TypeScript-类型系统进阶]] | TypeScript类型系统、高级类型、条件类型、映射类型、类型推断 | 🔴高级 |
| [[TypeScript-泛型与条件类型]] | 泛型、条件类型、infer、分布式条件类型、类型体操 | 🔴高级 |
| [[TypeScript-模块与声明文件]] | ES模块、CommonJS、声明文件、.d.ts、模块解析、类型导出 | 🟡进阶 |
| [[TypeScript-类型声明文件编写实战]] | 声明文件编写实战、为JS库添加类型、模块声明、全局声明 | 🟡进阶 |
| [[TypeScript-装饰器与元数据]] | 装饰器原理、类装饰器、方法装饰器、属性装饰器、元数据反射 | 🔴高级 |
| [[TS-严格模式与类型体操]] | TypeScript严格模式、类型体操实战、复杂类型推导、类型安全 | 🔴高级 |
| [[tsconfig配置详解]] | tsconfig.json配置、编译选项、严格模式、路径映射、项目引用 | 🟡进阶 |
| [[Vue3+TypeScript核心知识点总结_优化版\|Vue3+TypeScript核心知识点总结]] | 类型安全的Vue3开发实践、组合式API类型、Props类型、Emits类型 | 🟡进阶 |
| [[TypeScript AI Agent开发知识点系统梳理_优化版\|TypeScript AI Agent开发]] | LangChain.js、Vercel AI SDK、OpenAI Node SDK、多Agent协作 | 🟡进阶 |
| [[TypeScript AIGC应用开发知识点系统梳理_优化版\|TypeScript AIGC应用开发]] | 文本/图像/语音/视频/音乐生成、浏览器端AI、内容水印 | 🟡进阶 |
| [[ECharts-AI数据可视化]] | ECharts图表库、AI数据可视化、动态图表、大屏、图表优化 | 🟡进阶 |
| [[前端框架与TypeScript知识点完整整合大全_优化版\|前端框架与TypeScript知识点完整整合大全]] | React/Angular/Svelte横向对比、Vite/Next/Nuxt、TypeScript类型系统 | 🔴高级 |

### 二、Vue3生态

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Vue3快速上手_优化版\|Vue3快速上手]] | 零基础入门，从环境搭建到第一个组件 | 🟢入门 |
| [[Vue3 知识点系统梳理_优化版\|Vue3知识点系统梳理]] | Composition API、Proxy响应式、编译优化深度解析 | 🟡进阶 |
| [[Vue3-组合式API设计模式]] | 组合式API设计模式、setup、ref/reactive、computed/watch、最佳实践 | 🟡进阶 |
| [[Vue3-响应式原理Proxy]] | Vue3响应式原理、Proxy代理、依赖收集、触发更新、effect、ref实现 | 🔴高级 |
| [[Vue3-编译优化与PatchFlags]] | Vue3编译优化、PatchFlags、静态提升、缓存事件、Block Tree、Diff优化 | 🔴高级 |
| [[Vue3-组件通信全方案]] | Props/Emits、provide/inject、v-model、Pinia、事件总线、ref暴露 | 🟡进阶 |
| [[Vue3-自定义Hooks封装]] | 自定义Hooks封装、useFetch/useDebounce/useThrottle、组合式函数设计 | 🟡进阶 |
| [[Vue3-Teleport与Suspense]] | Teleport传送门、Suspense异步组件、异步依赖、加载状态、错误处理 | 🟡进阶 |
| [[Vue3-性能优化实战]] | Vue3性能优化、虚拟列表、懒加载、keep-alive、computed缓存、打包优化 | 🔴高级 |
| [[Pinia 知识点系统梳理_优化版\|Pinia知识点系统梳理]] | Vue3官方状态管理，替代Vuex，Store定义、State/Getters/Actions/Plugins | 🟡进阶 |
| [[Pinia-状态管理核心]] | Pinia核心概念、Store设计、组合式Store、持久化、DevTools、最佳实践 | 🟡进阶 |
| [[VueRouter-动态路由与权限]] | Vue Router动态路由、权限控制、路由守卫、懒加载、导航故障、滚动行为 | 🟡进阶 |
| [[Element Plus 知识点系统梳理_优化版\|ElementPlus知识点系统梳理]] | Vue3中后台标准组件库，组件使用、主题定制、国际化、按需引入 | 🟡进阶 |
| [[ElementPlus-二次封装]] | ElementPlus二次封装、业务组件、表格封装、表单封装、弹窗封装、主题定制 | 🟡进阶 |
| [[Nuxt3-SSR全栈框架]] | Nuxt3全栈框架、SSR/SSG/ISR、文件路由、自动导入、Nitro服务端引擎 | 🟡进阶 |
| [[VueUse-工具函数库]] | VueUse工具函数库、常用组合式函数、useMouse/useDark/useStorage、最佳实践 | 🟢入门 |
| [[Vue-i18n国际化方案]] | Vue i18n国际化、多语言切换、消息格式、日期数字格式化、懒加载 | 🟡进阶 |
| [[Vue表单解决方案-VeeValidate]] | VeeValidate表单验证、Schema验证、错误提示、自定义规则、异步验证 | 🟡进阶 |
| [[Vue主题切换与暗黑模式]] | Vue主题切换、暗黑模式、CSS变量、系统主题检测、持久化、过渡动画 | 🟢入门 |
| [[Vue3 AI Agent前端集成知识点系统梳理_优化版\|Vue3 AI Agent前端集成]] | useChat、流式渲染、工具调用可视化、对话管理、Agent前端集成 | 🟡进阶 |
| [[Vue3 AIGC前端应用知识点系统梳理_优化版\|Vue3 AIGC前端应用]] | AI写作助手、图像生成器、语音交互、多模态上传、PWA离线 | 🟡进阶 |

### 三、工程化构建

| 文档 | 说明 | 难度 |
|------|------|------|
| [[前端工程化知识点系统梳理_优化版\|前端工程化知识点系统梳理]] | Vite/Webpack、ESLint/Prettier、Husky、CI/CD、性能优化、Monorepo | 🟡进阶 |
| [[Vite-构建原理与插件开发]] | Vite构建原理、ESM、依赖预构建、HMR、插件开发、Rollup、构建优化 | 🔴高级 |
| [[ESLint+Prettier+Stylelint规范]] | 代码规范、ESLint配置、Prettier格式化、Stylelint、保存自动修复、规则配置 | 🟢入门 |
| [[Husky+Commitlint提交规范]] | Git Hooks、Husky、lint-staged、Commitlint、Conventional Commits、提交规范 | 🟢入门 |
| [[pnpm-monorepo架构]] | pnpm包管理、Monorepo架构、workspace、Turborepo/Nx、依赖管理、发布 | 🔴高级 |
| [[Vitest-单元测试与组件测试]] | Vitest测试框架、单元测试、Vue组件测试、@vue/test-utils、Mock、覆盖率 | 🟡进阶 |
| [[环境变量与多环境构建]] | 环境变量、.env文件、多环境构建、开发/测试/生产、Vite环境变量、动态配置 | 🟢入门 |
| [[前端构建产物分析与优化]] | 构建产物分析、bundle分析、代码分割、Tree Shaking、懒加载、体积优化 | 🔴高级 |
| [[组件库设计与发布]] | 组件库设计、组件文档、按需引入、主题定制、版本管理、npm发布、CI/CD | 🔴高级 |

### 四、AI前端集成

| 文档 | 说明 | 难度 |
|------|------|------|
| [[SSE-流式响应对接LLM]] | SSE流式响应、EventSource、对接LLM流式输出、流式渲染、错误重连 | 🟡进阶 |
| [[useSSE自定义Hook封装]] | useSSE自定义Hook、流式数据处理、加载状态、错误处理、取消请求、类型安全 | 🟡进阶 |
| [[对话式UI组件设计]] | 对话式UI组件、消息气泡、输入框、打字动画、消息状态、滚动定位、主题 | 🟡进阶 |
| [[Markdown渲染与代码高亮]] | Markdown渲染、代码高亮、marked/highlight.js/shiki、数学公式、安全过滤 | 🟡进阶 |
| [[流式Markdown渲染与代码高亮]] | 流式Markdown渲染、增量解析、代码块高亮、实时渲染、性能优化、防抖 | 🔴高级 |
| [[RAG检索来源与引用展示]] | RAG检索来源展示、引用标注、来源卡片、相似度展示、点击跳转、原文预览 | 🟡进阶 |
| [[RAG检索页面设计与实现]] | RAG检索页面设计、搜索框、结果列表、筛选排序、详情展示、相关推荐、交互设计 | 🟡进阶 |
| [[Agent思考链与任务进度展示]] | Agent思考链展示、推理过程可视化、任务进度、步骤状态、工具调用展示、时间线 | 🟡进阶 |
| [[Agent任务进度与思考链展示]] | Agent任务进度、思考链可视化、步骤展开折叠、工具调用详情、错误展示 | 🟡进阶 |
| [[AI生成内容Loading与错误态设计]] | AI生成Loading态、骨架屏、打字动画、错误态、重试机制、空状态、用户体验 | 🟡进阶 |
| [[AI生成内容的Loading与错误态]] | AI内容加载状态、错误处理、流式加载中断、降级方案、用户引导、最佳实践 | 🟡进阶 |
| [[多模态文件上传与预览]] | 多模态文件上传、拖拽上传、图片/视频/音频预览、进度显示、格式校验、压缩 | 🟡进阶 |
| [[文件上传与多模态交互]] | 文件上传组件、多模态交互、图片OCR、语音识别、视频处理、AI分析、交互设计 | 🟡进阶 |
| [[语音交互ASR与TTS]] | 语音交互、ASR语音识别、TTS语音合成、Web Speech API、流式识别、语音唤醒 | 🟡进阶 |

### 五、性能与安全

| 文档 | 说明 | 难度 |
|------|------|------|
| [[前端性能优化实战]] | 前端性能优化、加载性能、运行性能、渲染性能、网络优化、缓存策略、性能监控 | 🔴高级 |
| [[首屏加载优化]] | 首屏加载优化、关键渲染路径、资源预加载、代码分割、懒加载、骨架屏、CDN | 🟡进阶 |
| [[懒加载与预加载策略]] | 懒加载、预加载、preload/prefetch、图片懒加载、路由懒加载、组件懒加载、优先级 | 🟡进阶 |
| [[Web性能指标与监控-LCP-FID-CLS\|Web性能指标与监控]] | Web性能指标、LCP/FID/CLS/TTFB、Core Web Vitals、性能监控、RUM、性能预算 | 🔴高级 |
| [[前端安全-XSS-CSRF防护]] | XSS跨站脚本、CSRF跨站请求伪造、攻击原理、防御措施、CSP、输入验证、输出编码 | 🟡进阶 |
| [[CSP内容安全策略]] | CSP内容安全策略、指令配置、nonce/hash、违规报告、防止XSS、资源加载限制 | 🔴高级 |
| [[前端敏感数据保护]] | 前端敏感数据保护、Token存储、XSS防护、加密存储、数据脱敏、安全传输、最佳实践 | 🟡进阶 |
| [[SourceMap管理与错误追踪]] | SourceMap原理、生产环境管理、错误追踪、Sentry、堆栈还原、版本管理、安全 | 🟡进阶 |
| [[前端排查与进阶手册_优化版\|前端排查与进阶手册]] | useEffect死循环、水合mismatch、CORS、内存泄漏、Web Vitals、构建体积、微前端 | 🔴高级 |

### 六、组件与UI

| 文档 | 说明 | 难度 |
|------|------|------|
| [[路由守卫与鉴权流程]] | 路由守卫、鉴权流程、登录拦截、权限路由、动态路由、token刷新、403处理 | 🟡进阶 |
| [[菜单与按钮级权限控制]] | 权限控制、菜单权限、按钮权限、指令权限、动态路由、权限树、RBAC、前端权限 | 🟡进阶 |
| [[WebSocket-实时通信]] | WebSocket实时通信、连接管理、心跳重连、消息收发、二进制数据、房间机制、断线重连 | 🟡进阶 |
| [[ObsidianAI插件开发入门]] | Obsidian插件开发、API使用、AI集成、命令面板、侧边栏、设置页、发布插件 | 🟡进阶 |

---

## 🔗 知识关联

```text
前端开发体系
├── 基础语言 ← 所有前端开发的基础
│   ├── HTML/CSS → 页面结构与样式
│   ├── JavaScript → 交互逻辑、异步编程
│   └── TypeScript → 类型安全、工程化
├── Vue3生态 ← 核心框架
│   ├── 组合式API → 组件逻辑复用
│   ├── 响应式原理 → 数据驱动视图
│   ├── Pinia → 全局状态管理
│   ├── VueRouter → 路由管理
│   └── ElementPlus → UI组件库
├── 工程化构建 ← 开发效率与质量
│   ├── Vite → 构建工具
│   ├── ESLint/Prettier → 代码规范
│   ├── Husky → Git提交规范
│   └── Monorepo → 大型项目管理
├── AI前端集成 ← AI应用前端
│   ├── SSE流式 → LLM流式输出
│   ├── 对话UI → 聊天界面
│   ├── RAG展示 → 检索来源
│   └── Agent可视化 → 思考链/进度
├── 性能与安全 ← 质量保障
│   ├── 性能优化 → 加载/运行/渲染
│   └── 安全防护 → XSS/CSRF/CSP
└── 组件与UI ← 业务组件
    ├── 权限控制 → 路由/按钮级
    └── WebSocket → 实时通信
```

- **Vue3** 是核心框架，[[Pinia 知识点系统梳理_优化版|Pinia]] 管理全局状态，[[Element Plus 知识点系统梳理_优化版|ElementPlus]] 提供UI组件
- **TypeScript** 贯穿整个前端技术栈，[[Vue3+TypeScript核心知识点总结_优化版|Vue3+TS]] 是工程化标配
- **工程化** 是现代前端开发的基础，[[Vite-构建原理与插件开发|Vite]] 是构建工具的首选
- **AI前端集成** 是新兴领域，[[SSE-流式响应对接LLM|SSE流式]] 和对话式UI是核心
- 前端通过 API 与后端 [[MOC-后端开发|Spring Boot]] 交互

---

## 📖 学习顺序

1. **基础语言**：[[HTML5与CSS3基础入门|HTML/CSS基础]] → [[JavaScript 核心知识点系统梳理_优化版|JavaScript核心]] → [[TypeScript-类型系统进阶|TypeScript]]
2. **Vue3入门**：[[Vue3快速上手_优化版|Vue3快速上手]] → [[Vue3-组合式API设计模式|组合式API]]
3. **Vue3深入**：[[Vue3 知识点系统梳理_优化版|Vue3知识点梳理]] → [[Vue3-响应式原理Proxy|响应式原理]] → [[Vue3-编译优化与PatchFlags|编译优化]]
4. **生态**：[[Pinia 知识点系统梳理_优化版|Pinia]] → [[VueRouter-动态路由与权限|VueRouter]] → [[Element Plus 知识点系统梳理_优化版|ElementPlus]]
5. **工程化**：[[Vite-构建原理与插件开发|Vite]] → [[ESLint+Prettier+Stylelint规范|ESLint/Prettier]] → [[pnpm-monorepo架构|Monorepo]]
6. **AI前端**：[[SSE-流式响应对接LLM|SSE流式]] → [[对话式UI组件设计|对话UI]] → [[RAG检索来源与引用展示|RAG展示]]
7. **性能安全**：[[前端性能优化实战|性能优化]] → [[前端安全-XSS-CSRF防护|安全防护]]
8. **实战**：[[MOC-项目实战|全栈项目实战]]

---

## 🚀 知识域旗舰全集

- [[前端框架与TypeScript知识点完整整合大全_优化版|前端框架与TypeScript知识点完整整合大全]] — React/Angular/Svelte横向对比 + Vite/Next/Nuxt构建与元框架 + TypeScript类型系统 + JavaScript核心能力速查

## 🧩 排查与进阶手册

- [[前端排查与进阶手册_优化版|前端排查与进阶手册]] — useEffect死循环 / 水合mismatch / CORS / 内存泄漏 + Web Vitals / 构建体积 / 微前端

## 🏷️ 相关标签

`#前端` `#JavaScript` `#CSS` `#HTML` `#Vue3` `#TypeScript` `#Pinia` `#ElementPlus` `#Vite` `#工程化` `#CompositionAPI` `#AI前端` `#SSE` `#性能优化` `#前端安全`

---

[[Home|🏠 返回首页]] · [[MOC-综合导航|📚 综合导航]] · [[学习路线总览|🗺️ 学习路线]]
---

## 📝 新增文档（2026-09）

- [[Axios网络请求封装|Axios网络请求封装]]

