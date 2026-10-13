---
title: Vue-i18n国际化方案
tags: [Vue3/i18n, 国际化, vue-i18n, 多语言, 原子笔记]
category: 前端开发
created: 2026-08-12
updated: 2026-09-01
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: []
aliases: [Vue-i18n国际化方案]
---



# Vue-i18n国际化方案

> **文档说明**：系统讲解 Vue3 国际化（i18n）完整方案，包括 vue-i18n 配置、基本用法、语言切换、复数处理、日期数字格式化、异步加载语言包、与 Router/UI 库集成，以及最佳实践和常见问题。
>
> **适用人群**：前端开发者、全栈开发者、需要构建多语言 Vue 应用的开发者
>
> **前置知识**：[[Vue3-组合式API设计模式]]、[[Vue3-性能优化实战]]、[[前端工程化与构建工具]]

---

## 一、概述

### 1. 什么是国际化

```text
国际化（Internationalization，i18n）：
- 让应用支持多种语言、地区、文化
- 不修改代码即可切换语言
- 包括：文本翻译、日期格式、数字格式、货币、复数、文字方向

本地化（Localization，l10n）：
- 针对特定地区调整应用
- 是国际化的具体实现

i18n 涉及的内容：
1. 界面文本翻译
2. 日期和时间格式
3. 数字和货币格式
4. 复数规则（不同语言复数规则不同）
5. 文字方向（LTR/RTL，如阿拉伯语、希伯来语）
6. 排序和搜索
7. 图片和图标本地化
```

### 2. Vue 国际化方案

```text
Vue 生态主流 i18n 方案：
1. vue-i18n（官方推荐，最主流）
   - Vue 官方国际化插件
   - 支持 Vue2/Vue3
   - 功能完整：翻译、复数、日期、数字
   - 支持组合式 API

2. vue-i18n-next（Vue3 版本）
   - vue-i18n 的 Vue3 版本
   - 完全支持 Composition API
   - 更好的 TypeScript 支持

3. 其他方案：
   - vuex-i18n（基于 Vuex）
   - rosetta（轻量级）
   - lingui（React 生态，可用于 Vue）
   - FormatJS（formatjs.io，企业级）

推荐：vue-i18n（Vue3 用 vue-i18n@9.x）
```

---

## 二、安装与配置

### 1. 安装

```bash
# Vue3 安装 vue-i18n@9.x
npm install vue-i18n@9
# 或
yarn add vue-i18n@9
pnpm add vue-i18n@9
```

### 2. 基本配置

```javascript
// src/i18n/index.js
import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN.json'
import enUS from './locales/en-US.json'
import jaJP from './locales/ja-JP.json'

const i18n = createI18n({
  legacy: false,           // 使用 Composition API 模式（Vue3 推荐）
  locale: 'zh-CN',         // 默认语言
  fallbackLocale: 'en-US', // 回退语言（找不到翻译时用）
  globalInjection: true,    // 全局注入 $t 等方法
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS,
    'ja-JP': jaJP
  },
  datetimeFormats: {
    'zh-CN': {
      short: { year: 'numeric', month: 'short', day: 'numeric' },
      long: { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
    },
    'en-US': {
      short: { year: 'numeric', month: 'short', day: 'numeric' },
      long: { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
    }
  },
  numberFormats: {
    'zh-CN': {
      currency: { style: 'currency', currency: 'CNY' }
    },
    'en-US': {
      currency: { style: 'currency', currency: 'USD' }
    }
  }
})

export default i18n
```

```javascript
// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import i18n from './i18n'

const app = createApp(App)
app.use(i18n)
app.mount('#app')
```

### 3. 语言包文件

```json
// src/i18n/locales/zh-CN.json
{
  "common": {
    "confirm": "确认",
    "cancel": "取消",
    "save": "保存",
    "delete": "删除",
    "edit": "编辑",
    "search": "搜索",
    "loading": "加载中...",
    "success": "操作成功",
    "error": "操作失败"
  },
  "home": {
    "title": "首页",
    "welcome": "欢迎，{name}！",
    "description": "这是一个国际化示例应用"
  },
  "user": {
    "profile": "个人资料",
    "settings": "设置",
    "logout": "退出登录",
    "login": "登录",
    "register": "注册"
  },
  "message": {
    "unread": "你有 {count} 条未读消息",
    "unread_zero": "你没有未读消息",
    "unread_one": "你有 1 条未读消息",
    "unread_other": "你有 {count} 条未读消息"
  }
}
```

```json
// src/i18n/locales/en-US.json
{
  "common": {
    "confirm": "Confirm",
    "cancel": "Cancel",
    "save": "Save",
    "delete": "Delete",
    "edit": "Edit",
    "search": "Search",
    "loading": "Loading...",
    "success": "Operation successful",
    "error": "Operation failed"
  },
  "home": {
    "title": "Home",
    "welcome": "Welcome, {name}!",
    "description": "This is an i18n example app"
  },
  "user": {
    "profile": "Profile",
    "settings": "Settings",
    "logout": "Logout",
    "login": "Login",
    "register": "Register"
  },
  "message": {
    "unread": "You have {count} unread messages",
    "unread_zero": "You have no unread messages",
    "unread_one": "You have 1 unread message",
    "unread_other": "You have {count} unread messages"
  }
}
```

---

## 三、基本用法

### 1. 模板中使用

```vue
<template>
  <!-- 基本翻译 -->
  <h1>{{ $t('home.title') }}</h1>

  <!-- 带参数 -->
  <p>{{ $t('home.welcome', { name: userName }) }}</p>

  <!-- 复数 -->
  <p>{{ $tc('message.unread', unreadCount, { count: unreadCount }) }}</p>

  <!-- 日期格式化 -->
  <p>{{ $d(new Date(), 'short') }}</p>
  <p>{{ $d(new Date(), 'long') }}</p>

  <!-- 数字/货币格式化 -->
  <p>{{ $n(12345.67, 'currency') }}</p>

  <!-- 组合式 API -->
  <p>{{ t('common.confirm') }}</p>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t, tc, d, n, locale } = useI18n()
const userName = '张三'
const unreadCount = 5
</script>
```

### 2. 组合式 API 用法

```vue
<script setup>
import { useI18n } from 'vue-i18n'

const {
  t,           // 翻译函数
  tc,          // 复数翻译
  te,          // 检查翻译是否存在
  d,           // 日期格式化
  n,           // 数字格式化
  locale,      // 当前语言（ref）
  locales,     // 可用语言列表
  fallbackLocale,
  setLocale,   // 设置语言
  mergeLocaleMessage,  // 合并语言包
  setLocaleMessage     // 设置语言包
} = useI18n()

// 使用
const title = t('home.title')
const welcome = t('home.welcome', { name: '张三' })

// 检查翻译是否存在
if (te('home.non_existent')) {
  // 翻译存在
}
</script>
```

### 3. 选项式 API 用法

```vue
<script>
export default {
  computed: {
    title() {
      return this.$t('home.title')
    }
  },
  methods: {
    showMessage() {
      alert(this.$t('common.success'))
    }
  }
}
</script>
```

---

## 四、语言切换

### 1. 基本切换

```vue
<template>
  <div class="lang-switcher">
    <select v-model="currentLocale" @change="changeLocale">
      <option value="zh-CN">简体中文</option>
      <option value="en-US">English</option>
      <option value="ja-JP">日本語</option>
    </select>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()
const currentLocale = locale  // 直接绑定

function changeLocale() {
  // locale 是 ref，直接赋值即可
  // 切换后所有 $t 自动更新
  localStorage.setItem('locale', locale.value)
}
</script>
```

### 2. 持久化语言设置

```javascript
// src/i18n/index.js
import { createI18n } from 'vue-i18n'

// 从 localStorage 读取，或从浏览器语言检测
function getDefaultLocale() {
  const saved = localStorage.getItem('locale')
  if (saved) return saved

  // 浏览器语言检测
  const browserLang = navigator.language
  if (browserLang.startsWith('zh')) return 'zh-CN'
  if (browserLang.startsWith('ja')) return 'ja-JP'
  return 'en-US'
}

const i18n = createI18n({
  legacy: false,
  locale: getDefaultLocale(),
  fallbackLocale: 'en-US',
  messages: { /* ... */ }
})

// 监听语言变化，保存到 localStorage
i18n.global.locale.value && (() => {
  // Vue3 composition 模式
})()

export default i18n
```

```vue
<!-- App.vue 监听语言变化 -->
<script setup>
import { useI18n } from 'vue-i18n'
import { watch } from 'vue'

const { locale } = useI18n()

watch(locale, (newLocale) => {
  localStorage.setItem('locale', newLocale)
  // 更新 HTML lang 属性
  document.documentElement.lang = newLocale
  // 更新文字方向（RTL 语言）
  document.documentElement.dir = isRTL(newLocale) ? 'rtl' : 'ltr'
})

function isRTL(locale) {
  return ['ar', 'he', 'fa'].some(lang => locale.startsWith(lang))
}
</script>
```

---

## 五、高级特性

### 1. 复数处理

```text
复数规则：
- 不同语言复数规则不同
- 英语：zero/one/other（实际是 one/other）
- 中文：没有复数变化
- 俄语：复杂的复数规则
- vue-i18n 使用 CLDR 复数规则

复数翻译定义：
key_zero / key_one / key_two / key_few / key_many / key_other
或用 | 分隔：
key: "no items | one item | {count} items"
```

```json
// en-US.json
{
  "items": {
    "count_zero": "No items",
    "count_one": "One item",
    "count_other": "{count} items"
  }
}

// 或简写
{
  "items": {
    "count": "No items | One item | {count} items"
  }
}
```

```vue
<template>
  <!-- 复数翻译 -->
  <p>{{ $tc('items.count', itemCount, { count: itemCount }) }}</p>
  <!-- itemCount=0 → "No items" -->
  <!-- itemCount=1 → "One item" -->
  <!-- itemCount=5 → "5 items" -->
</template>
```

### 2. 日期和数字格式化

```vue
<template>
  <!-- 日期格式化 -->
  <p>{{ $d(new Date(), 'short') }}</p>
  <!-- zh-CN: 2024年1月15日 -->
  <!-- en-US: Jan 15, 2024 -->

  <p>{{ $d(new Date(), 'long') }}</p>
  <!-- zh-CN: 2024年1月15日星期一 -->
  <!-- en-US: Monday, January 15, 2024 -->

  <!-- 自定义格式 -->
  <p>{{ $d(new Date(), { year: 'numeric', month: '2-digit', day: '2-digit' }) }}</p>

  <!-- 数字格式化 -->
  <p>{{ $n(1234567.89) }}</p>
  <!-- zh-CN: 1,234,567.89 -->
  <!-- en-US: 1,234,567.89 -->

  <!-- 货币 -->
  <p>{{ $n(99.99, 'currency') }}</p>
  <!-- zh-CN: ¥99.99 -->
  <!-- en-US: $99.99 -->

  <!-- 百分比 -->
  <p>{{ $n(0.85, 'percent') }}</p>
  <!-- 85% -->
</template>
```

### 3. 命名空间和模块

```text
大型应用语言包组织：
- 按功能模块拆分语言文件
- 避免单个文件过大
- 便于团队协作

目录结构：
src/i18n/locales/
├── zh-CN/
│   ├── index.json      # 通用
│   ├── home.json       # 首页
│   ├── user.json       # 用户
│   └── product.json    # 产品
└── en-US/
    ├── index.json
    ├── home.json
    ├── user.json
    └── product.json
```

```javascript
// 动态加载模块
const modules = import.meta.glob('./locales/**/*.json')

async function loadLocaleMessages(locale) {
  const messages = {}
  for (const path in modules) {
    if (path.includes(`/${locale}/`)) {
      const moduleName = path.split('/').pop().replace('.json', '')
      const mod = await modules[path]()
      messages[moduleName] = mod.default
    }
  }
  return messages
}
```

---

## 六、异步加载语言包

### 1. 懒加载语言包

```javascript
// src/i18n/index.js
import { createI18n } from 'vue-i18n'

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'en-US',
  messages: {
    'zh-CN': await import('./locales/zh-CN.json').then(m => m.default)
    // 只加载默认语言，其他语言按需加载
  }
})

// 异步加载语言
export async function loadLocale(locale) {
  // 检查是否已加载
  if (i18n.global.availableLocales.includes(locale)) {
    i18n.global.locale.value = locale
    return
  }

  // 动态加载
  const messages = await import(`./locales/${locale}.json`)
  i18n.global.setLocaleMessage(locale, messages.default)
  i18n.global.locale.value = locale
}

export default i18n
```

```vue
<!-- 语言切换组件 -->
<script setup>
import { loadLocale } from '@/i18n'

async function changeLocale(locale) {
  await loadLocale(locale)
  localStorage.setItem('locale', locale)
}
</script>
```

### 2. Vite 代码分割

```javascript
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        // 语言包单独打包
        manualChunks: {
          'lang-zh': ['./src/i18n/locales/zh-CN.json'],
          'lang-en': ['./src/i18n/locales/en-US.json'],
          'lang-ja': ['./src/i18n/locales/ja-JP.json']
        }
      }
    }
  }
}
```

---

## 七、与 Vue Router 集成

### 1. 路由前缀国际化

```javascript
// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { i18n } from '@/i18n'

const routes = [
  {
    path: '/:locale?',  // 可选语言前缀
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('@/views/Home.vue') },
      { path: 'about', name: 'about', component: () => import('@/views/About.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：根据 URL 设置语言
router.beforeEach((to, from, next) => {
  const locale = to.params.locale || localStorage.getItem('locale') || 'zh-CN'
  i18n.global.locale.value = locale
  next()
})

export default router
```

```vue
<!-- 生成带语言前缀的链接 -->
<router-link :to="{ name: 'about', params: { locale: $i18n.locale } }">
  {{ $t('nav.about') }}
</router-link>
```

---

## 八、与 UI 库集成

### 1. Element Plus 国际化

```javascript
// main.js
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import en from 'element-plus/dist/locale/en.mjs'
import App from './App.vue'
import i18n from './i18n'

const app = createApp(App)

// 根据当前语言设置 Element Plus 语言
const elementLocales = { 'zh-CN': zhCn, 'en-US': en }
app.use(ElementPlus, { locale: elementLocales[i18n.global.locale.value] })

app.use(i18n)
app.mount('#app')
```

```vue
<!-- 监听语言变化，动态切换 Element Plus 语言 -->
<script setup>
import { useI18n } from 'vue-i18n'
import { watch } from 'vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import en from 'element-plus/dist/locale/en.mjs'

const { locale } = useI18n()
const elementLocale = ref(zhCn)

const locales = { 'zh-CN': zhCn, 'en-US': en }
watch(locale, (newLocale) => {
  elementLocale.value = locales[newLocale] || en
})
</script>

<template>
  <el-config-provider :locale="elementLocale">
    <router-view />
  </el-config-provider>
</template>
```

### 2. Ant Design Vue 国际化

```vue
<template>
  <a-config-provider :locale="antLocale">
    <router-view />
  </a-config-provider>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import enUS from 'ant-design-vue/es/locale/en_US'

const { locale } = useI18n()
const antLocale = ref(zhCN)
const locales = { 'zh-CN': zhCN, 'en-US': enUS }

watch(locale, (newLocale) => {
  antLocale.value = locales[newLocale] || enUS
})
</script>
```

---

## 九、最佳实践

### 1. 翻译管理规范

- [ ] **统一 key 命名**：用点分隔的命名空间，如 `user.profile.title`
- [ ] **key 用英文**：key 本身用英文，避免中文 key
- [ ] **避免硬编码**：所有用户可见文本都走 i18n
- [ ] **参数化**：动态内容用 `{name}` 参数，不要拼接
- [ ] **复数处理**：不同语言复数规则不同，用 $tc
- [ ] **注释说明**：复杂翻译加注释说明上下文
- [ ] **翻译完整性检查**：构建时检查缺失的翻译 key
- [ ] **翻译管理工具**：大型项目用 Crowdin/Transifex/Weblate

### 2. 性能优化

- [ ] **懒加载语言包**：只加载当前语言，其他按需加载
- [ ] **默认语言内联**：默认语言打包进主包，减少请求
- [ ] **语言包压缩**：JSON 压缩，CDN 分发
- [ ] **避免运行时翻译**：静态内容构建时翻译（SSG）
- [ ] **缓存语言包**：Service Worker 缓存语言文件
- [ ] **预加载下一个语言**：用户可能切换的语言预加载

### 3. 开发体验

- [ ] **TypeScript 支持**：为翻译 key 生成类型定义
- [ ] **ESLint 插件**：检查未使用/缺失的翻译 key
- [ ] **VSCode 插件**：i18n Ally 等插件，实时预览翻译
- [ ] **翻译提取**：自动从代码提取翻译 key
- [ ] **翻译校验**：CI 中检查翻译完整性
- [ ] **Mock 翻译**：开发环境用伪翻译测试 UI 溢出

---

## 十、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **翻译不更新** | 语言未正确切换/非响应式 | 检查 locale 是否是 ref、用 useI18n |
| **$t is not defined** | 未全局注入/未导入 | globalInjection: true 或导入 useI18n |
| **缺失翻译警告** | 语言包缺少 key | 补全翻译或设置 fallbackLocale |
| **复数不正确** | 复数规则配置错误 | 检查 key 后缀（zero/one/other）、用 $tc |
| **日期格式不对** | datetimeFormats 未配置 | 配置 datetimeFormats、用 Intl.DateTimeFormat |
| **货币符号不对** | numberFormats 未配置 | 配置 currency、用 $n |
| **语言切换闪烁** | 异步加载语言包 | 预加载、加载指示器、默认语言内联 |
| **RTL 布局错乱** | 未处理文字方向 | 切换 dir="rtl"、CSS 逻辑属性 |
| **翻译 key 冲突** | 命名空间不清晰 | 用模块前缀、按功能拆分 |
| **构建体积大** | 所有语言包打包 | 懒加载语言包、代码分割 |
| **SSR 不工作** | 服务端语言检测 | 从 Accept-Language 头检测、cookie |
| **翻译参数不生效** | 参数名不匹配 | 检查 {name} 与传入对象的 key |
| **Element Plus 不切换** | 未动态更新 locale | 用 el-config-provider 动态绑定 |
| **深嵌套 key 找不到** | 路径错误/对象结构不对 | 检查 JSON 结构、用点分隔路径 |
| **翻译包含 HTML** | 直接输出会转义 | 用 v-html（注意 XSS 风险）或组件插值 |
| **语言持久化失效** | localStorage 被清除/隐私模式 | 用 cookie、URL 参数、后端存储 |
| **翻译质量差** | 机器翻译/上下文不足 | 人工校对、提供上下文注释、翻译工具 |
| **数字格式不统一** | 未用 $n 格式化 | 统一用 $n，不要手动 toLocaleString |

---

## 十一、关联笔记

### Vue3 生态
- [[Vue3-组合式API设计模式]] · [[Vue3-性能优化实战]] · [[Vue3-响应式原理源码解析]]
- [[Vue主题切换与暗黑模式]] · [[Pinia-状态管理核心]]

### 前端工程
- [[前端工程化与构建工具]] · [[Vite-构建原理与插件开发]] · [[TypeScript-类型声明文件编写实战]]
- [[前端构建产物分析与优化]]

### 前端性能与安全
- [[首屏加载优化]] · [[前端安全-XSS-CSRF防护]] · [[懒加载与预加载策略]]
- [[Web性能指标与监控-LCP-FID-CLS]]

### 导航
- [[MOC-前端开发]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[Vue3-组合式API设计模式]] Vue3 基础 → 深入本文国际化方案 → 学习 [[Vue主题切换与暗黑模式]] 主题切换 → 实践 [[Vue3-性能优化实战]] 性能优化 → 研究 [[Vite-构建原理与插件开发]] 构建优化 → 构建完整的 Vue3 企业级应用开发能力。
