---
title: Vue3+TypeScript MOC（四级展开）
tags: [MOC, Vue3TS, 枢纽]
created: 2026-08-13
updated: 2026-08-13
hub: true
---

# 🎨 Vue3 + TypeScript 前端体系 MOC

> 现代前端工程化体系，以 Vue3 + TypeScript 为核心，覆盖框架原理、工程化、组件生态与 AI 产品前端交互。
> **标签前缀**：`#Vue3TS/`
> **枢纽核心笔记**：[[Vue3TS-前端技术枢纽]]

---

## 📐 知识层级总览

```
一级：Vue3+TypeScript前端体系
├── 二级：3.1 TypeScript核心
│   ├── 三级：TypeScript-类型系统进阶
│   │   ├── 四级：基础类型与接口
│   │   ├── 四级：联合类型与类型守卫
│   │   ├── 四级：交叉类型与类型别名
│   │   └── 四级：字面量类型与模板字面量
│   ├── 三级：TypeScript-泛型与条件类型
│   ├── 三级：TypeScript-装饰器与元数据
│   ├── 三级：TypeScript-模块与声明文件
│   └── 三级：TS-严格模式与类型体操
├── 二级：3.2 Vue3核心原理
├── 二级：3.3 前端工程化
├── 二级：3.4 组件与状态管理
├── 二级：3.5 路由与权限
└── 二级：3.6 AI产品前端交互
```

---

## 📚 3.1 TypeScript 核心

### [[TypeScript-类型系统进阶|类型系统进阶]]
> TypeScript 类型体系地基

- **四级子知识点**：
  - 基础类型与 any/unknown/never
  - 接口（interface）与类型别名（type）
  - 联合类型与类型守卫
  - 交叉类型
  - 字面量类型与模板字面量类型
  - 索引类型与映射类型
  - 可选链与空值合并
- **标签**：`#Vue3TS/TypeScript`

### [[TypeScript-泛型与条件类型|泛型与条件类型]]
> 类型编程核心，高级类型工具基础

- **四级子知识点**：
  - 泛型函数与泛型接口
  - 泛型约束（extends）
  - 条件类型（T extends U ? X : Y）
  - infer 关键字与类型提取
  - 内置工具类型（Partial/Pick/Record等）
  - 分布式条件类型
  - 逆变与协变
- **标签**：`#Vue3TS/TypeScript`

### [[TypeScript-装饰器与元数据|装饰器与元数据]]
> 框架底层和 NestJS 等的关键特性

- **四级子知识点**：
  - 类装饰器
  - 方法装饰器
  - 属性装饰器
  - 参数装饰器
  - reflect-metadata 元数据
  - 装饰器执行顺序
  - 与 Vue3 组合式 API 的关系
- **标签**：`#Vue3TS/TypeScript`

### [[TypeScript-模块与声明文件|模块与声明文件]]
> 大型项目模块化与类型声明

- **四级子知识点**：
  - ES Module 与 CommonJS
  - 模块解析策略
  - 声明文件（.d.ts）编写
  - 三斜线指令
  - 命名空间与模块
  - 第三方库类型缺失处理
- **标签**：`#Vue3TS/TypeScript`

### [[TS-严格模式与类型体操|严格模式与类型体操]]
> 类型安全最大化与高级类型技巧

- **四级子知识点**：
  - strict 模式各选项详解
  - 类型体操常见模式
  - 递归类型与尾递归优化
  - 类型安全的事件总线
  - 类型安全的表单
  - 类型推导优化技巧
- **标签**：`#Vue3TS/TypeScript`

---

## 📚 3.2 Vue3 核心原理

### [[Vue3-响应式原理Proxy|响应式原理 Proxy]]
> Vue3 最核心的机制

- **四级子知识点**：
  - Proxy vs Object.defineProperty
  - reactive 与 ref 底层实现
  - 依赖收集与触发更新
  - effect 与 scheduler
  - computed 与 watch 原理
  - 响应式丢失场景与解决
- **标签**：`#Vue3TS/Vue3核心`

### [[Vue3-组合式API设计模式|组合式 API 设计模式]]
> Vue3 开发的标准方式

- **四级子知识点**：
  - setup 函数与 script setup
  - 响应式 API（ref/reactive/computed）
  - 生命周期钩子
  - 自定义 Hooks 封装原则
  - 组合式函数 vs Mixins
  - 逻辑复用最佳实践
- **标签**：`#Vue3TS/Vue3核心`

### [[Vue3-编译优化与PatchFlags|编译优化与 PatchFlags]]
> Vue3 性能优势的来源

- **四级子知识点**：
  - 虚拟 DOM 与 Diff 算法
  - PatchFlags 静态标记
  - 静态提升（hoistStatic）
  - 缓存事件处理
  - 块级优化（Block Tree）
  - 编译器与运行时协作
- **标签**：`#Vue3TS/Vue3核心`

### [[Vue3-自定义Hooks封装|自定义 Hooks 封装]]
> 逻辑复用的核心手段

- **四级子知识点**：
  - Hooks 命名与设计原则
  - 常用 Hooks 库（VueUse）
  - 异步请求 Hooks
  - 表单验证 Hooks
  - 权限控制 Hooks
  - Hooks 测试方法
- **标签**：`#Vue3TS/Vue3核心`

### [[Vue3-组件通信全方案|组件通信全方案]]
> 组件间数据传递的完整方案

- **四级子知识点**：
  - Props / Emits
  - v-model 自定义
  - Provide / Inject
  - 事件总线（mitt）
  - Pinia 跨组件
  - 插槽（Slots）与作用域插槽
  - 父组件调用子组件方法
- **标签**：`#Vue3TS/Vue3核心`

### [[Vue3-Teleport与Suspense|Teleport 与 Suspense]]
> Vue3 新增的高级组件

- **四级子知识点**：
  - Teleport 传送门
  - Suspense 异步组件
  - 异步组件与代码分割
  - 加载状态与错误处理
  - 与路由懒加载配合
  - 实际应用场景
- **标签**：`#Vue3TS/Vue3核心`

---

## 📚 3.3 前端工程化

### [[Vite-构建原理与插件开发|Vite 构建原理与插件开发]]
> 现代前端构建工具标准

- **四级子知识点**：
  - Vite 开发服务器原理（esbuild）
  - 依赖预构建
  - HMR 热更新机制
  - Rollup 生产构建
  - Vite 插件开发
  - 环境变量与模式
  - 与 Webpack 对比
- **标签**：`#Vue3TS/工程化`

### [[pnpm-monorepo架构|pnpm Monorepo 架构]]
> 现代前端项目管理方案

- **四级子知识点**：
  - pnpm 硬链接与符号链接
  - workspace 配置
  - 依赖提升与幽灵依赖
  - Monorepo 目录结构
  - 包版本管理（changesets）
  - 与 npm/yarn 对比
  - Turborepo 任务编排
- **标签**：`#Vue3TS/工程化`

### [[ESLint+Prettier+Stylelint规范|ESLint + Prettier + Stylelint 规范]]
> 代码质量与格式统一

- **四级子知识点**：
  - ESLint 规则配置
  - Prettier 格式化
  - Stylelint CSS 规范
  - 三者冲突解决
  - 编辑器集成
  - 团队规范落地
- **标签**：`#Vue3TS/工程化`

### [[Husky+Commitlint提交规范|Husky + Commitlint 提交规范]]
> Git 提交质量管控

- **四级子知识点**：
  - Husky Git Hooks
  - Commitlint 规则
  - Conventional Commits 规范
  - commitizen 交互式提交
  - lint-staged 增量检查
  - 与 CI/CD 配合
- **标签**：`#Vue3TS/工程化`

### [[Vitest-单元测试与组件测试|Vitest 单元测试与组件测试]]
> Vite 原生测试框架

- **四级子知识点**：
  - Vitest 基础用法
  - 组件测试（@vue/test-utils）
  - Mock 与 Stub
  - 测试覆盖率
  - 快照测试
  - 与 Jest 对比迁移
- **标签**：`#Vue3TS/工程化`

### [[环境变量与多环境构建|环境变量与多环境构建]]
> 多环境部署配置

- **四级子知识点**：
  - .env 文件规范
  - 开发/测试/生产环境
  - 构建时注入 vs 运行时配置
  - 动态配置方案
  - Docker 环境变量
  - 配置安全（敏感信息）
- **标签**：`#Vue3TS/工程化`

---

## 📚 3.4 组件与状态管理

### [[Pinia-状态管理核心|Pinia 状态管理核心]]
> Vue3 官方状态管理

- **四级子知识点**：
  - Store 定义（Options/Setup）
  - State / Getters / Actions
  - 持久化插件
  - 模块化与组合
  - 服务端渲染支持
  - 与 Vuex 对比迁移
  - TypeScript 类型支持
- **标签**：`#Vue3TS/组件状态`

### [[ElementPlus-二次封装|Element Plus 二次封装]]
> 中后台组件库定制

- **四级子知识点**：
  - 按需引入与主题定制
  - 全局配置（ConfigProvider）
  - 表单组件封装
  - 表格组件封装
  - 弹窗/抽屉封装
  - 业务组件库搭建
  - 组件文档（VitePress）
- **标签**：`#Vue3TS/组件状态`

### [[VueUse-工具函数库|VueUse 工具函数库]]
> Vue 组合式工具集

- **四级子知识点**：
  - 常用工具函数分类
  - 浏览器 API 封装
  - 传感器（useMouse/useGeolocation）
  - 状态工具（useDebounce/useThrottle）
  - 自定义工具函数
  - 与 Lodash 的区别
- **标签**：`#Vue3TS/组件状态`

### [[UnoCSS-Tailwind原子化CSS|UnoCSS / Tailwind 原子化 CSS]]
> 原子化 CSS 方案

- **四级子知识点**：
  - 原子化 CSS 理念
  - UnoCSS 配置与预设
  - Tailwind CSS 核心
  - 自定义主题与设计令牌
  - 与 SCSS/CSS Modules 对比
  - 性能与可维护性
- **标签**：`#Vue3TS/组件状态`

### [[组件库设计与发布|组件库设计与发布]]
> 从 0 到 1 搭建组件库

- **四级子知识点**：
  - 组件设计原则
  - Monorepo 组件库结构
  - 构建与打包
  - 文档站点
  - 版本管理与发布
  - 按需加载实现
- **标签**：`#Vue3TS/组件状态`

---

## 📚 3.5 路由与权限

### [[VueRouter-动态路由与权限|Vue Router 动态路由与权限]]
> 前端路由与权限控制

- **四级子知识点**：
  - 路由配置与嵌套
  - 动态路由添加（addRoute）
  - 路由元信息（meta）
  - 路由懒加载
  - 路由过渡动画
  - 与 Pinia 配合权限
- **标签**：`#Vue3TS/路由权限`

### [[路由守卫与鉴权流程|路由守卫与鉴权流程]]
> 前端安全控制

- **四级子知识点**：
  - 全局守卫/路由守卫/组件守卫
  - 登录态校验
  - Token 刷新机制
  - 403/404 处理
  - 路由级权限
  - 与后端权限配合
- **标签**：`#Vue3TS/路由权限`

### [[菜单与按钮级权限控制|菜单与按钮级权限控制]]
> 细粒度权限管理

- **四级子知识点**：
  - 动态菜单生成
  - 按钮权限指令（v-permission）
  - 权限码管理
  - 角色与权限映射
  - 前端权限 vs 后端权限
  - 权限变更热更新
- **标签**：`#Vue3TS/路由权限`

---

## 📚 3.6 AI 产品前端交互

### [[SSE-流式响应对接LLM|SSE 流式响应对接 LLM]]
> AI 对话产品的核心技术

- **四级子知识点**：
  - SSE 协议原理
  - EventSource API
  - 流式文本渲染
  - 断线重连
  - 与 Fetch ReadableStream
  - 取消请求
  - 与 WebSocket 对比
- **标签**：`#Vue3TS/AI交互`
- **跨板块关联**：[[06-AI工程化/MOC-AI工程化|AI工程化]]

### [[WebSocket-实时通信|WebSocket 实时通信]]
> 双向实时通信方案

- **四级子知识点**：
  - WebSocket 协议
  - 连接管理与心跳
  - 消息序列化
  - 断线重连
  - 与 SSE 选型对比
  - 多房间/多频道
- **标签**：`#Vue3TS/AI交互`

### [[Markdown渲染与代码高亮|Markdown 渲染与代码高亮]]
> AI 输出内容展示

- **四级子知识点**：
  - markdown-it 配置
  - 代码高亮（Shiki/Prism）
  - 数学公式（KaTeX）
  - Mermaid 图表
  - XSS 防护
  - 自定义渲染规则
- **标签**：`#Vue3TS/AI交互`

### [[对话式UI组件设计|对话式 UI 组件设计]]
> AI 产品的核心交互组件

- **四级子知识点**：
  - 消息列表与滚动
  - 输入框与快捷键
  - 消息状态（发送中/成功/失败）
  - 流式打字效果
  - 消息操作（复制/重新生成/编辑）
  - 多轮对话管理
- **标签**：`#Vue3TS/AI交互`

### [[文件上传与多模态交互|文件上传与多模态交互]]
> 多模态 AI 产品前端

- **四级子知识点**：
  - 大文件分片上传
  - 上传进度与取消
  - 图片预览与裁剪
  - 音频录制与播放
  - 拖拽上传
  - 多模态消息展示
- **标签**：`#Vue3TS/AI交互`

### [[AI生成内容的Loading与错误态|AI 生成内容的 Loading 与错误态]]
> AI 产品体验细节

- **四级子知识点**：
  - 骨架屏与占位
  - 流式加载状态
  - 超时与重试
  - 错误提示与降级
  - 空状态设计
  - 用户引导
- **标签**：`#Vue3TS/AI交互`

### [[ECharts-AI数据可视化|ECharts AI 数据可视化]]
> AI 数据分析展示

- **四级子知识点**：
  - ECharts 核心概念
  - 常用图表类型
  - 动态数据更新
  - 大数据量优化
  - 与 Vue3 封装
  - AI 生成图表配置
- **标签**：`#Vue3TS/AI交互`

---

## 🔗 学习依赖路径

```
TypeScript → Vue3核心 → 工程化 → 组件/状态 → AI交互
     ↓           ↓          ↓          ↓
  类型系统    响应式      Vite       Pinia
     ↓           ↓          ↓          ↓
     └──── AI 产品前端（→ 06 AI工程化）────┘
```

| 阶段 | 知识点 | 预计耗时 | 前置条件 |
|------|--------|----------|----------|
| 地基 | TypeScript 全套 | 16h | JS 基础 |
| 框架 | Vue3 核心原理 | 16h | TypeScript |
| 工程化 | Vite + pnpm + 规范 | 10h | 框架 |
| 组件 | Pinia + Element Plus | 10h | 工程化 |
| AI交互 | SSE + 对话UI | 12h | 组件 + AI基础 |
| 实战 | AI 对话产品前端 | 24h | 全部 |

---

## 🌐 跨板块关联

| 关联板块 | 关联点 | 连接笔记 |
|----------|--------|----------|
| [[01-Python全栈/MOC-Python全栈|Python全栈]] | 对接 FastAPI 的 SSE/WebSocket 流式接口 | [[Vue3对接FastAPI-SSE]] |
| [[02-Java全栈/MOC-Java全栈|Java全栈]] | 对接 SpringBoot/Gateway 的 REST API | [[Vue3对接SpringBoot-API]] |
| [[06-AI工程化/MOC-AI工程化|AI工程化]] | 前端是 AI 产品的交互层，消费 LLM 流式输出 | [[SSE-流式响应对接LLM]] |
| [[09-效率工具链/MOC-效率工具|效率工具]] | VSCode 插件、前端调试工具链 | [[VSCode-前端开发配置]] |

---

## 🌱 持续扩充方向

- [ ] Vue 3.5+ 新特性（Reactivity Transform 正式化）
- [ ] Vite 6 与 Rolldown 构建器
- [ ] Nuxt 3 SSR 全栈
- [ ] SolidJS / Svelte 对比学习
- [ ] WebGPU 前端推理
- [ ] 微前端（qiankun/wujie）
- [ ] 低代码平台前端架构
- [ ] WebAssembly 前端高性能计算

---

## 📊 板块统计

- 二级分类：6 个
- 三级知识点（原子笔记）：27 篇
- 四级子知识点：约 145 个
- 枢纽笔记：1 篇
- 跨板块关联：4 条

---

[[10-四级知识框架/00-总控/四级框架总索引|← 返回四级框架总索引]] | [[Home|🏠 返回首页]]
