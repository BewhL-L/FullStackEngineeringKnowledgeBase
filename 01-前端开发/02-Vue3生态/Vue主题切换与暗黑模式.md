---
title: Vue主题切换与暗黑模式
tags: [Vue3, 主题切换, 暗黑模式, Dark Mode, CSS变量, 原子笔记]
category: 前端开发
created: 2026-08-12
updated: 2026-09-01
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: []
aliases: [Vue主题切换与暗黑模式]
---



# Vue主题切换与暗黑模式

> **文档说明**：系统讲解 Vue3 主题切换与暗黑模式实现方案，包括 CSS 变量、class 切换、系统主题检测、持久化、防闪烁、多主题、UI 库主题集成、图片图表适配，以及最佳实践和常见问题。
>
> **适用人群**：前端开发者、全栈开发者、需要实现主题切换的 Vue 开发者
>
> **前置知识**：[[Vue3-组合式API设计模式]]、[[Vue3-性能优化实战]]、[[Vue-i18n国际化方案]]

---

## 一、概述

### 1. 为什么需要暗黑模式

```text
暗黑模式（Dark Mode）的价值：

用户体验：
- 减少眼睛疲劳（暗光环境下）
- 节省 OLED 屏幕电量（黑色像素不发光）
- 提升内容对比度和可读性
- 符合用户系统偏好（macOS/iOS/Android 都支持）

商业价值：
- 用户期望（现代应用标配）
- 提升用户满意度和留存
- 差异化竞争（精致的暗黑模式体现品质）

技术挑战：
- 颜色系统设计（不能简单反色）
- 图片和图表适配
- 第三方组件库主题
- 防止切换闪烁
- 性能和可维护性
```

### 2. 主题切换方案对比

| 方案 | 原理 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|---------|
| **CSS 变量** | 切换 :root 的变量值 | 灵活、性能好、易维护 | 需要统一变量体系 | 推荐方案 |
| **class 切换** | body 添加 .dark class | 简单、兼容性好 | 样式重复、难维护 | 简单项目 |
| **data-theme** | html[data-theme="dark"] | 语义化、多主题 | 类似 class | 多主题 |
| **CSS 滤镜** | filter: invert(1) | 最简单 | 图片也会反色、效果差 | 临时方案 |
| **多套样式** | 切换不同 CSS 文件 | 完全隔离 | 体积大、切换慢 | 主题差异大 |
| **Shadow DOM** | 隔离样式 | 完全隔离 | 复杂、兼容性 | 组件级 |

推荐：CSS 变量 + class/data-theme 切换

---

## 二、CSS 变量方案

### 1. 定义主题变量

```css
/* src/styles/variables.css */

/* 默认（亮色）主题 */
:root {
  /* 背景色 */
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f5f7fa;
  --color-bg-tertiary: #eef1f6;
  --color-bg-elevated: #ffffff;

  /* 文字色 */
  --color-text-primary: #1a1a2e;
  --color-text-secondary: #4a5568;
  --color-text-tertiary: #718096;
  --color-text-inverse: #ffffff;
  --color-text-disabled: #a0aec0;

  /* 边框色 */
  --color-border-primary: #e2e8f0;
  --color-border-secondary: #edf2f7;
  --color-border-focus: #3b82f6;

  /* 品牌色 */
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-primary-light: #dbeafe;
  --color-primary-dark: #1d4ed8;

  /* 功能色 */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;

  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);

  /* 其他 */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --transition-fast: 0.15s ease;
  --transition-normal: 0.3s ease;
}

/* 暗黑主题 */
html.dark {
  /* 背景色（暗黑模式背景不是纯黑，而是深灰） */
  --color-bg-primary: #0f172a;
  --color-bg-secondary: #1e293b;
  --color-bg-tertiary: #334155;
  --color-bg-elevated: #1e293b;

  /* 文字色（暗黑模式文字不是纯白，而是浅灰，减少刺眼） */
  --color-text-primary: #f1f5f9;
  --color-text-secondary: #cbd5e1;
  --color-text-tertiary: #94a3b8;
  --color-text-inverse: #0f172a;
  --color-text-disabled: #64748b;

  /* 边框色 */
  --color-border-primary: #334155;
  --color-border-secondary: #1e293b;
  --color-border-focus: #60a5fa;

  /* 品牌色（暗黑模式下品牌色可以稍亮） */
  --color-primary: #60a5fa;
  --color-primary-hover: #3b82f6;
  --color-primary-light: #1e3a5f;
  --color-primary-dark: #93c5fd;

  /* 功能色 */
  --color-success: #34d399;
  --color-warning: #fbbf24;
  --color-error: #f87171;
  --color-info: #60a5fa;

  /* 阴影（暗黑模式阴影更柔和） */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
}
```

### 2. 使用变量

```css
/* 组件样式中使用变量 */
.button {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md);
  padding: 8px 16px;
  transition: all var(--transition-fast);
}

.button:hover {
  background-color: var(--color-primary-hover);
}

.card {
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: 24px;
}

.title {
  color: var(--color-text-primary);
  font-size: 24px;
  font-weight: 600;
}

.description {
  color: var(--color-text-secondary);
  font-size: 14px;
  line-height: 1.6;
}
```

---

## 三、主题切换实现

### 1. 主题管理 Composable

```typescript
// src/composables/useTheme.ts
import { ref, watch, computed } from 'vue'

export type Theme = 'light' | 'dark' | 'system'

const STORAGE_KEY = 'app-theme'
const theme = ref<Theme>('system')

// 系统主题是否为暗黑
const systemDark = ref(false)

// 实际应用的主题
const isDark = computed(() => {
  if (theme.value === 'system') {
    return systemDark.value
  }
  return theme.value === 'dark'
})

// 初始化系统主题监听
function initSystemTheme() {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  systemDark.value = mediaQuery.matches

  mediaQuery.addEventListener('change', (e) => {
    systemDark.value = e.matches
    applyTheme()
  })
}

// 应用主题到 DOM
function applyTheme() {
  const html = document.documentElement
  if (isDark.value) {
    html.classList.add('dark')
    html.setAttribute('data-theme', 'dark')
  } else {
    html.classList.remove('dark')
    html.setAttribute('data-theme', 'light')
  }
}

// 从 localStorage 加载
function loadTheme() {
  const saved = localStorage.getItem(STORAGE_KEY) as Theme | null
  if (saved && ['light', 'dark', 'system'].includes(saved)) {
    theme.value = saved
  }
}

// 保存到 localStorage
function saveTheme() {
  localStorage.setItem(STORAGE_KEY, theme.value)
}

// 设置主题
function setTheme(newTheme: Theme) {
  theme.value = newTheme
  saveTheme()
  applyTheme()
}

// 切换明暗
function toggleTheme() {
  if (isDark.value) {
    setTheme('light')
  } else {
    setTheme('dark')
  }
}

// 初始化
function init() {
  loadTheme()
  initSystemTheme()
  applyTheme()
}

export function useTheme() {
  return {
    theme,
    isDark,
    setTheme,
    toggleTheme,
    init
  }
}
```

### 2. 防止闪烁（FOUC）

```html
<!-- index.html 中内联脚本，在 Vue 加载前执行 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>My App</title>

  <!-- 关键：在渲染前设置主题，防止闪烁 -->
  <script>
    (function() {
      try {
        var saved = localStorage.getItem('app-theme');
        var systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        var isDark = saved === 'dark' || (saved === 'system' && systemDark) || (!saved && systemDark);

        if (isDark) {
          document.documentElement.classList.add('dark');
          document.documentElement.setAttribute('data-theme', 'dark');
        }
      } catch (e) {
        // localStorage 不可用时忽略
      }
    })();
  </script>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

### 3. 主题切换组件

```vue
<!-- src/components/ThemeToggle.vue -->
<template>
  <div class="theme-toggle">
    <!-- 三态切换：亮色 / 暗黑 / 跟随系统 -->
    <div class="theme-options">
      <button
        v-for="option in options"
        :key="option.value"
        class="theme-btn"
        :class="{ active: theme === option.value }"
        @click="setTheme(option.value)"
        :title="option.label"
      >
        <component :is="option.icon" :size="18" />
      </button>
    </div>

    <!-- 或简单的切换按钮 -->
    <button class="toggle-btn" @click="toggleTheme">
      <SunIcon v-if="isDark" :size="20" />
      <MoonIcon v-else :size="20" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'
import { SunIcon, MoonIcon, MonitorIcon } from '@/components/icons'

const { theme, isDark, setTheme, toggleTheme } = useTheme()

const options = [
  { value: 'light' as const, label: '亮色模式', icon: SunIcon },
  { value: 'dark' as const, label: '暗黑模式', icon: MoonIcon },
  { value: 'system' as const, label: '跟随系统', icon: MonitorIcon }
]
</script>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
}

.theme-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md);
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.theme-btn:hover {
  color: var(--color-text-primary);
  border-color: var(--color-primary);
}

.theme-btn.active {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: var(--color-primary);
}

.toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.toggle-btn:hover {
  background: var(--color-bg-tertiary);
  transform: rotate(15deg);
}
</style>
```

---

## 四、多主题支持

### 1. 多主题变量

```css
/* 扩展多主题 */
html[data-theme="light"] {
  --color-bg-primary: #ffffff;
  --color-text-primary: #1a1a2e;
  /* ... 亮色变量 */
}

html[data-theme="dark"] {
  --color-bg-primary: #0f172a;
  --color-text-primary: #f1f5f9;
  /* ... 暗黑变量 */
}

/* 自定义主题：护眼绿 */
html[data-theme="eye-care"] {
  --color-bg-primary: #c7edcc;
  --color-bg-secondary: #b8e6bf;
  --color-text-primary: #1a3a1a;
  --color-text-secondary: #2d5a2d;
  --color-primary: #2d8a4e;
  /* ... */
}

/* 自定义主题：暖色 */
html[data-theme="warm"] {
  --color-bg-primary: #fef7ed;
  --color-bg-secondary: #fdecd8;
  --color-text-primary: #451a03;
  --color-primary: #ea580c;
  /* ... */
}

/* 高对比度主题（无障碍） */
html[data-theme="high-contrast"] {
  --color-bg-primary: #000000;
  --color-text-primary: #ffffff;
  --color-border-primary: #ffffff;
  --color-primary: #ffff00;
  /* ... */
}
```

### 2. 主题管理扩展

```typescript
// src/composables/useTheme.ts 扩展
export type Theme = 'light' | 'dark' | 'eye-care' | 'warm' | 'high-contrast'

const themeList = [
  { value: 'light', label: '亮色', icon: 'sun' },
  { value: 'dark', label: '暗黑', icon: 'moon' },
  { value: 'eye-care', label: '护眼', icon: 'eye' },
  { value: 'warm', label: '暖色', icon: 'flame' },
  { value: 'high-contrast', label: '高对比', icon: 'contrast' }
]

function applyTheme() {
  const html = document.documentElement
  html.setAttribute('data-theme', theme.value)
  // 同时设置 class 用于兼容
  html.classList.toggle('dark', theme.value === 'dark')
}
```

---

## 五、UI 库主题集成

### 1. Element Plus 暗黑模式

```typescript
// main.ts
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 暗黑模式样式
import 'element-plus/theme-chalk/dark/css-vars.css'
import App from './App.vue'

const app = createApp(App)
app.use(ElementPlus)
app.mount('#app')
```

```vue
<!-- App.vue 中用 el-config-provider 动态切换 -->
<template>
  <el-config-provider :locale="locale" :size="size">
    <router-view />
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { useTheme } from '@/composables/useTheme'

const { isDark } = useTheme()
const locale = zhCn

// Element Plus 暗黑模式通过 html.dark class 控制
// 在 useTheme 的 applyTheme 中已经添加/移除 dark class
</script>
```

```css
/* 覆盖 Element Plus 暗黑模式变量 */
html.dark {
  /* Element Plus 内置变量覆盖 */
  --el-bg-color: var(--color-bg-primary);
  --el-bg-color-page: var(--color-bg-secondary);
  --el-bg-color-overlay: var(--color-bg-elevated);
  --el-text-color-primary: var(--color-text-primary);
  --el-text-color-regular: var(--color-text-secondary);
  --el-border-color: var(--color-border-primary);
  --el-color-primary: var(--color-primary);
}
```

### 2. Ant Design Vue 暗黑模式

```vue
<template>
  <a-config-provider :locale="locale" :theme="antTheme">
    <router-view />
  </a-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { theme } from 'ant-design-vue'
import { useTheme } from '@/composables/useTheme'

const { isDark } = useTheme()
const locale = zhCN

const antTheme = computed(() => ({
  algorithm: isDark.value ? theme.darkAlgorithm : theme.defaultAlgorithm,
  token: {
    colorPrimary: '#3b82f6',
    borderRadius: 8,
    // 自定义 token
  }
}))
</script>
```

### 3. Tailwind CSS 暗黑模式

```javascript
// tailwind.config.js
export default {
  darkMode: 'class',  // 用 class 切换
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        // 可以用 CSS 变量
        primary: 'var(--color-primary)',
        'bg-primary': 'var(--color-bg-primary)',
        'text-primary': 'var(--color-text-primary)',
      }
    }
  }
}
```

```vue
<!-- Tailwind 用法 -->
<template>
  <div class="bg-bg-primary text-text-primary">
    <button class="bg-primary text-white dark:bg-blue-400">
      按钮
    </button>
  </div>
</template>
```

---

## 六、图片与图表适配

### 1. 图片适配

```css
/* 方案1：CSS 滤镜（简单图片） */
html.dark .invert-on-dark {
  filter: invert(1) hue-rotate(180deg);
  /* invert 反色，hue-rotate 修正色相 */
}

/* 方案2：不同主题不同图片 */
<img src="logo-light.png" class="light-only" />
<img src="logo-dark.png" class="dark-only" />

.light-only { display: block; }
.dark-only { display: none; }
html.dark .light-only { display: none; }
html.dark .dark-only { display: block; }

/* 方案3：SVG 用 CSS 变量 */
svg {
  fill: var(--color-text-primary);
  stroke: var(--color-border-primary);
}
```

```vue
<!-- Vue 组件中动态切换图片 -->
<template>
  <img :src="isDark ? darkLogo : lightLogo" alt="Logo" />
</template>

<script setup>
import { computed } from 'vue'
import { useTheme } from '@/composables/useTheme'
import lightLogo from '@/assets/logo-light.svg'
import darkLogo from '@/assets/logo-dark.svg'

const { isDark } = useTheme()
</script>
```

### 2. 图表适配（ECharts）

```typescript
// src/composables/useChartTheme.ts
import { computed } from 'vue'
import { useTheme } from './useTheme'

export function useChartTheme() {
  const { isDark } = useTheme()

  const chartTheme = computed(() => ({
    backgroundColor: 'transparent',
    textStyle: {
      color: isDark.value ? '#cbd5e1' : '#4a5568'
    },
    title: {
      textStyle: { color: isDark.value ? '#f1f5f9' : '#1a1a2e' }
    },
    legend: {
      textStyle: { color: isDark.value ? '#cbd5e1' : '#4a5568' }
    },
    xAxis: {
      axisLine: { lineStyle: { color: isDark.value ? '#334155' : '#e2e8f0' } },
      axisLabel: { color: isDark.value ? '#94a3b8' : '#718096' },
      splitLine: { lineStyle: { color: isDark.value ? '#1e293b' : '#edf2f7' } }
    },
    yAxis: {
      axisLine: { lineStyle: { color: isDark.value ? '#334155' : '#e2e8f0' } },
      axisLabel: { color: isDark.value ? '#94a3b8' : '#718096' },
      splitLine: { lineStyle: { color: isDark.value ? '#1e293b' : '#edf2f7' } }
    },
    tooltip: {
      backgroundColor: isDark.value ? '#1e293b' : '#ffffff',
      borderColor: isDark.value ? '#334155' : '#e2e8f0',
      textStyle: { color: isDark.value ? '#f1f5f9' : '#1a1a2e' }
    }
  }))

  return { chartTheme }
}
```

```vue
<!-- ECharts 组件 -->
<template>
  <div ref="chartRef" class="chart"></div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { useChartTheme } from '@/composables/useChartTheme'

const chartRef = ref()
const { chartTheme } = useChartTheme()
let chart: echarts.ECharts

onMounted(() => {
  chart = echarts.init(chartRef.value)
  updateChart()
})

// 主题变化时重新渲染
watch(chartTheme, () => {
  updateChart()
}, { deep: true })

function updateChart() {
  chart.setOption({
    ...chartTheme.value,
    series: [{ type: 'bar', data: [10, 20, 30] }]
  })
}

onUnmounted(() => chart?.dispose())
</script>
```

---

## 七、性能优化

### 1. 过渡动画

```css
/* 平滑过渡（但注意性能） */
/* 方案1：所有属性过渡（简单但可能卡） */
* {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

/* 方案2：只过渡需要的属性（推荐） */
.theme-transition,
.theme-transition * {
  transition: background-color var(--transition-normal),
              color var(--transition-normal),
              border-color var(--transition-normal),
              fill var(--transition-normal),
              stroke var(--transition-normal) !important;
}

/* 切换时临时添加过渡类，切换后移除 */
```

```typescript
// 平滑切换（避免全局 * 选择器影响性能）
function toggleTheme() {
  // 添加过渡类
  document.documentElement.classList.add('theme-transition')

  // 切换主题
  isDark.value = !isDark.value
  applyTheme()

  // 过渡结束后移除类
  setTimeout(() => {
    document.documentElement.classList.remove('theme-transition')
  }, 300)
}
```

### 2. 其他优化

```text
性能优化要点：

1. CSS 变量性能
   - CSS 变量本身性能很好
   - 避免在 :root 上定义过多变量（影响所有元素）
   - 变量变化会触发重绘，但不触发重排

2. 避免 layout thrashing
   - 主题切换只改颜色，不改布局
   - 确保暗黑模式下元素尺寸不变

3. 图片优化
   - 用 SVG（矢量，用 CSS 变量着色）
   - 避免用大位图做主题切换
   - 暗黑模式图片预加载

4. 字体优化
   - 暗黑模式下字体可以稍粗（增加可读性）
   - 但不要切换字体（避免重排）

5. 避免闪烁
   - index.html 内联脚本提前设置主题
   - 关键 CSS 内联
   - 预加载暗黑模式样式
```

---

## 八、最佳实践

### 1. 颜色系统设计

- [ ] **不要简单反色**：暗黑模式背景用深灰（#0f172a），文字用浅灰（#f1f5f9），不是纯黑纯白
- [ ] **降低饱和度**：暗黑模式下品牌色饱和度稍降，避免刺眼
- [ ] **层级用明度区分**：暗黑模式下用不同明度的背景表示层级（卡片比页面背景亮）
- [ ] **阴影柔和**：暗黑模式下阴影更暗、更柔和
- [ ] **对比度达标**：文字与背景对比度 ≥ 4.5:1（WCAG AA）
- [ ] **统一变量命名**：用语义化命名（--color-bg-primary），不用具体颜色名

### 2. 实现规范

- [ ] **CSS 变量优先**：用 CSS 变量实现主题，不用多套样式文件
- [ ] **防闪烁**：index.html 内联脚本提前设置主题
- [ ] **持久化**：用户选择保存到 localStorage
- [ ] **跟随系统**：支持 system 选项，监听 prefers-color-scheme
- [ ] **三态切换**：亮色 / 暗黑 / 跟随系统
- [ ] **UI 库集成**：正确配置 Element Plus / Ant Design / Tailwind 暗黑模式
- [ ] **图片适配**：Logo、图标、图表都要适配暗黑模式
- [ ] **过渡动画**：平滑过渡，但避免全局 * 选择器

### 3. 测试检查

- [ ] **所有页面检查**：每个页面在亮/暗模式下都正常
- [ ] **表单状态**：输入框、按钮、禁用状态、错误状态
- [ ] **弹窗和抽屉**：Modal、Drawer、Tooltip、Popover
- [ ] **表格和列表**：斑马纹、hover、选中状态
- [ ] **图片和图表**：Logo、图标、ECharts/Chart.js
- [ ] **代码块**：代码高亮主题切换
- [ ] **打印样式**：打印时强制亮色模式
- [ ] **无障碍**：屏幕阅读器、键盘导航、对比度

---

## 九、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **切换时闪烁** | Vue 加载前是默认主题 | index.html 内联脚本提前设置主题 |
| **部分组件不变色** | 组件用了固定颜色，没用 CSS 变量 | 全部改用 CSS 变量、检查 UI 库主题配置 |
| **Element Plus 暗黑不生效** | 未引入暗黑样式 / dark class 未添加 | 引入 dark/css-vars.css、确保 html.dark class |
| **图片在暗黑模式看不清** | 图片是为亮色设计的 | 用 SVG + CSS 变量、准备暗黑版图片、CSS 滤镜 |
| **图表文字看不清** | 图表颜色固定 | 监听主题变化、动态更新图表配置 |
| **切换卡顿** | 全局 * 过渡 / 大量元素重绘 | 只过渡颜色属性、临时添加过渡类、避免布局变化 |
| **暗黑模式下刺眼** | 用了纯白文字/纯黑背景 | 文字用浅灰（#f1f5f9）、背景用深灰（#0f172a） |
| **系统主题不跟随** | 未监听 prefers-color-scheme | matchMedia 监听 change 事件 |
| **刷新后主题丢失** | 未持久化 | 保存到 localStorage、启动时读取 |
| **第三方 iframe 不变** | iframe 隔离样式 | 给 iframe 也传递主题参数、postMessage 通信 |
| **代码块高亮不变** | 代码高亮主题固定 | 准备亮/暗两套高亮主题、切换时重新渲染 |
| **打印是暗黑的** | 打印时继承暗黑模式 | 打印媒体查询强制亮色、@media print 覆盖 |
| **CSS 变量不生效** | 变量未定义 / 作用域错 | 检查 :root 定义、检查选择器优先级、用 DevTools 查看 |
| **过渡动画不流畅** | 过渡了布局属性 | 只过渡颜色相关属性、避免 transition: all |
| **移动端状态栏不变** | 未设置 meta theme-color | 动态设置 <meta name="theme-color"> |
| **多主题切换混乱** | class 和 data-theme 混用 | 统一用 data-theme、一套切换逻辑 |
| **暗黑模式下阴影看不见** | 阴影颜色太暗 | 暗黑模式阴影用更暗的颜色、增加不透明度 |
| **输入框光标看不见** | 光标颜色固定 | 设置 caret-color: var(--color-text-primary) |
| **选中文字看不清** | 选区颜色固定 | 设置 ::selection { background: var(--color-primary-light) } |
| **滚动条样式不变** | 滚动条样式固定 | 自定义滚动条用 CSS 变量、webkit-scrollbar |

---

## 十、关联笔记

### Vue3 生态
- [[Vue3-组合式API设计模式]] · [[Vue3-性能优化实战]] · [[Vue-i18n国际化方案]]
- [[Vue3-响应式原理源码解析]] · [[Pinia-状态管理核心]] · [[Vue表单解决方案-VeeValidate]]

### 前端工程
- [[前端工程化与构建工具]] · [[Vite-构建原理与插件开发]] · [[TypeScript-类型声明文件编写实战]]
- [[前端构建产物分析与优化]]

### 前端性能与安全
- [[首屏加载优化]] · [[懒加载与预加载策略]] · [[Web性能指标与监控-LCP-FID-CLS]]
- [[前端安全-XSS-CSRF防护]]

### 导航
- [[MOC-前端开发]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[Vue3-组合式API设计模式]] Vue3 基础 → 学习本文主题切换 → 深入 [[Vue-i18n国际化方案]] 国际化 → 实践 [[Vue3-性能优化实战]] 性能优化 → 研究 [[Vite-构建原理与插件开发]] 构建优化 → 构建完整的 Vue3 企业级应用开发能力。
