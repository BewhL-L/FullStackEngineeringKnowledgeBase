---
title: Vue3 自定义Hooks封装
tags: [前端, Hooks, 组合式API, 原子笔记]
category: 前端开发
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[Vue3-组合式API设计模式]]", "[[Vue3-响应式原理Proxy]]"]
aliases: [Vue3-自定义Hooks封装]
---

# Vue3 自定义Hooks封装

> **文档说明**：系统讲解 Vue3 自定义 Hooks 的设计原则、命名规范、常用 Hooks 封装（防抖/节流/事件监听/本地存储/鼠标位置/媒体查询/标题/剪贴板/暗黑模式/请求/倒计时/分页/表格/表单等）、Hooks 组合与复用、最佳实践，以及常见问题排查。
>
> **适用人群**：前端开发工程师、全栈开发者、使用 Vue3 构建复杂应用的工程师
>
> **前置知识**：[[Vue3-组合式API设计模式]]、[[Vue3-响应式原理Proxy]]、[[Vue3-组件通信全方案]]

---

## 一、概述

### 1. 什么是 Hooks

**Hooks** 是 Vue3 组合式 API（Composition API）中的核心概念，是将可复用的逻辑封装成函数的一种模式。Hooks 通常以 `use` 开头，内部使用 Vue 的响应式 API（ref、reactive、computed、watch 等），返回响应式状态和方法。

### 2. Hooks vs Mixins

| 维度 | Mixins（Vue2） | Hooks（Vue3） |
|------|----------------|---------------|
| **数据来源** | 不清晰，可能来自多个 mixin | 清晰，从 Hook 返回值解构 |
| **命名冲突** | 容易冲突，后引入的覆盖先引入的 | 可重命名解构，避免冲突 |
| **类型支持** | 差，TypeScript 难以推断 | 好，天然支持 TypeScript |
| **复用性** | 中等，逻辑分散 | 高，逻辑集中封装 |
| **可维护性** | 差，难以追踪数据来源 | 好，逻辑内聚 |
| **测试** | 困难 | 容易，纯函数可单独测试 |

### 3. Hooks 设计原则

- [ ] **单一职责**：一个 Hook 只做一件事，功能单一明确
- [ ] **use 前缀**：所有 Hook 函数以 `use` 开头，如 `useDebounce`、`useLocalStorage`
- [ ] **返回响应式**：返回 ref/reactive 包装的响应式状态
- [ ] **自动清理**：组件卸载时自动清理定时器、事件监听等副作用
- [ ] **参数灵活**：支持 ref 或原始值作为参数，使用 `unref` 统一处理
- [ ] **类型安全**：使用 TypeScript 泛型，提供完整的类型定义
- [ ] **可组合**：Hooks 之间可以相互组合，构建复杂逻辑
- [ ] **无副作用调用**：Hooks 应在 setup 顶层调用，不要在条件/循环中调用

### 4. Hooks 分类

| 分类 | 说明 | 示例 |
|------|------|------|
| **状态管理** | 管理响应式状态 | useLocalStorage、useSessionStorage |
| **工具函数** | 通用工具逻辑 | useDebounce、useThrottle、useInterval |
| **浏览器 API** | 封装浏览器 API | useEventListener、useClipboard、useMediaQuery |
| **DOM 操作** | 操作 DOM 元素 | useElementSize、useMouseInElement |
| **网络请求** | 封装 HTTP 请求 | useFetch、useRequest、useAsync |
| **UI 交互** | 界面交互逻辑 | useModal、usePagination、useTable |
| **表单处理** | 表单验证和提交 | useForm、useFormValidation |
| **传感器** | 设备传感器 | useMouse、useGeolocation、useDeviceOrientation |

---

## 二、常用 Hooks 封装

### 1. useDebounce（防抖）

```typescript
// composables/useDebounce.ts
import { ref, watch, type Ref, type UnwrapRef } from 'vue'

/**
 * 防抖 Hook：延迟执行，期间再次触发则重新计时
 * @param value 要防抖的值
 * @param delay 延迟时间（毫秒），默认 300ms
 * @returns 防抖后的值
 */
export function useDebounce<T>(value: Ref<T> | T, delay: number = 300): Ref<UnwrapRef<T>> {
  const debouncedValue = ref(unref(value)) as Ref<UnwrapRef<T>>
  let timer: ReturnType<typeof setTimeout> | null = null

  watch(
    () => unref(value),
    (newValue) => {
      if (timer) clearTimeout(timer)
      timer = setTimeout(() => {
        debouncedValue.value = newValue as UnwrapRef<T>
      }, delay)
    },
    { immediate: true }
  )

  return debouncedValue
}

// 使用示例
// const searchKeyword = ref('')
// const debouncedKeyword = useDebounce(searchKeyword, 500)
// watch(debouncedKeyword, (val) => { searchAPI(val) })
```

### 2. useThrottle（节流）

```typescript
// composables/useThrottle.ts
import { ref, watch, type Ref, type UnwrapRef } from 'vue'

/**
 * 节流 Hook：指定时间内只执行一次
 * @param value 要节流的值
 * @param delay 节流间隔（毫秒），默认 300ms
 * @returns 节流后的值
 */
export function useThrottle<T>(value: Ref<T> | T, delay: number = 300): Ref<UnwrapRef<T>> {
  const throttledValue = ref(unref(value)) as Ref<UnwrapRef<T>>
  let lastTime = 0
  let timer: ReturnType<typeof setTimeout> | null = null

  watch(
    () => unref(value),
    (newValue) => {
      const now = Date.now()
      const remaining = delay - (now - lastTime)

      if (remaining <= 0) {
        if (timer) {
          clearTimeout(timer)
          timer = null
        }
        lastTime = now
        throttledValue.value = newValue as UnwrapRef<T>
      } else if (!timer) {
        timer = setTimeout(() => {
          lastTime = Date.now()
          timer = null
          throttledValue.value = newValue as UnwrapRef<T>
        }, remaining)
      }
    }
  )

  return throttledValue
}
```

### 3. useEventListener（事件监听）

```typescript
// composables/useEventListener.ts
import { onMounted, onUnmounted, watch, type Ref } from 'vue'

type WindowEventName = keyof WindowEventMap
type DocumentEventName = keyof DocumentEventMap
type ElementEventName = keyof HTMLElementEventMap

/**
 * 事件监听 Hook：自动管理事件监听的添加和移除
 * @param target 事件目标（window/document/HTMLElement/ref）
 * @param event 事件名
 * @param handler 事件处理函数
 * @param options 事件选项
 */
export function useEventListener(
  target: Window | Document | HTMLElement | Ref<HTMLElement | null>,
  event: string,
  handler: (event: any) => void,
  options?: AddEventListenerOptions
) {
  const remove = () => {
    const el = unref(target)
    if (el) el.removeEventListener(event, handler, options)
  }

  const add = () => {
    const el = unref(target)
    if (el) el.addEventListener(event, handler, options)
  }

  onMounted(add)
  onUnmounted(remove)

  // 如果 target 是 ref，监听变化
  if (isRef(target)) {
    watch(target, () => {
      remove()
      add()
    })
  }

  return { remove, add }
}

// 使用示例
// useEventListener(window, 'resize', () => { console.log('resize') })
// useEventListener(document, 'click', () => { console.log('click') })
// const el = ref<HTMLElement>()
// useEventListener(el, 'scroll', () => {})
```

### 4. useLocalStorage（本地存储）

```typescript
// composables/useLocalStorage.ts
import { ref, watch, type Ref, type UnwrapRef } from 'vue'

/**
 * 本地存储 Hook：响应式数据与 localStorage 同步
 * @param key 存储键名
 * @param defaultValue 默认值
 * @returns 响应式数据
 */
export function useLocalStorage<T>(key: string, defaultValue: T): Ref<UnwrapRef<T>> {
  const storedValue = localStorage.getItem(key)
  const data = ref(
    storedValue ? JSON.parse(storedValue) : defaultValue
  ) as Ref<UnwrapRef<T>>

  // 数据变化时同步到 localStorage
  watch(
    data,
    (newValue) => {
      if (newValue === null || newValue === undefined) {
        localStorage.removeItem(key)
      } else {
        localStorage.setItem(key, JSON.stringify(newValue))
      }
    },
    { deep: true }
  )

  // 监听其他标签页的存储变化
  window.addEventListener('storage', (e) => {
    if (e.key === key && e.newValue) {
      data.value = JSON.parse(e.newValue)
    }
  })

  return data
}

// 使用示例
// const token = useLocalStorage('app-token', '')
// const userInfo = useLocalStorage('user-info', { name: '', age: 0 })
// token.value = 'new-token'  // 自动同步到 localStorage
```

### 5. useMouse（鼠标位置）

```typescript
// composables/useMouse.ts
import { ref, onMounted, onUnmounted } from 'vue'

/**
 * 鼠标位置 Hook：实时跟踪鼠标坐标
 * @returns 鼠标位置（x, y）和是否在窗口内
 */
export function useMouse() {
  const x = ref(0)
  const y = ref(0)
  const isInside = ref(false)

  function handleMove(e: MouseEvent) {
    x.value = e.clientX
    y.value = e.clientY
  }

  function handleEnter() {
    isInside.value = true
  }

  function handleLeave() {
    isInside.value = false
  }

  onMounted(() => {
    window.addEventListener('mousemove', handleMove)
    window.addEventListener('mouseenter', handleEnter)
    window.addEventListener('mouseleave', handleLeave)
  })

  onUnmounted(() => {
    window.removeEventListener('mousemove', handleMove)
    window.removeEventListener('mouseenter', handleEnter)
    window.removeEventListener('mouseleave', handleLeave)
  })

  return { x, y, isInside }
}

// 使用示例
// const { x, y } = useMouse()
// <div>鼠标位置: {{ x }}, {{ y }}</div>
```

### 6. useMediaQuery（媒体查询）

```typescript
// composables/useMediaQuery.ts
import { ref, onMounted, onUnmounted } from 'vue'

/**
 * 媒体查询 Hook：响应式匹配 CSS 媒体查询
 * @param query 媒体查询字符串
 * @returns 是否匹配
 */
export function useMediaQuery(query: string) {
  const matches = ref(false)
  let mediaQueryList: MediaQueryList | null = null

  function handleChange(e: MediaQueryListEvent) {
    matches.value = e.matches
  }

  onMounted(() => {
    mediaQueryList = window.matchMedia(query)
    matches.value = mediaQueryList.matches
    mediaQueryList.addEventListener('change', handleChange)
  })

  onUnmounted(() => {
    mediaQueryList?.removeEventListener('change', handleChange)
  })

  return matches
}

// 使用示例
// const isDark = useMediaQuery('(prefers-color-scheme: dark)')
// const isMobile = useMediaQuery('(max-width: 768px)')
// const isTablet = useMediaQuery('(min-width: 768px) and (max-width: 1024px)')
```

### 7. useTitle（页面标题）

```typescript
// composables/useTitle.ts
import { watch, type Ref } from 'vue'

/**
 * 页面标题 Hook：响应式设置 document.title
 * @param title 标题（字符串或 ref）
 * @returns 标题 ref
 */
export function useTitle(title: string | Ref<string>) {
  const titleRef = ref(unref(title)) as Ref<string>

  watch(
    titleRef,
    (newTitle) => {
      document.title = newTitle
    },
    { immediate: true }
  )

  // 如果传入的是 ref，同步变化
  if (isRef(title)) {
    watch(title, (val) => {
      titleRef.value = val
    })
  }

  return titleRef
}

// 使用示例
// const pageTitle = useTitle('首页')
// pageTitle.value = '新标题'  // 自动更新 document.title
```

### 8. useClipboard（剪贴板）

```typescript
// composables/useClipboard.ts
import { ref } from 'vue'

/**
 * 剪贴板 Hook：复制文本到剪贴板
 * @returns 复制方法、复制状态、错误信息
 */
export function useClipboard() {
  const copied = ref(false)
  const error = ref<Error | null>(null)
  let timer: ReturnType<typeof setTimeout> | null = null

  async function copy(text: string, duration: number = 1500) {
    error.value = null
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text)
      } else {
        // 降级方案
        const textarea = document.createElement('textarea')
        textarea.value = text
        textarea.style.position = 'fixed'
        textarea.style.opacity = '0'
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
      }
      copied.value = true
      if (timer) clearTimeout(timer)
      timer = setTimeout(() => {
        copied.value = false
      }, duration)
    } catch (e) {
      error.value = e as Error
      copied.value = false
    }
  }

  return { copied, error, copy }
}

// 使用示例
// const { copied, copy } = useClipboard()
// <button @click="copy('要复制的文本')">{{ copied ? '已复制' : '复制' }}</button>
```

### 9. useDarkMode（暗黑模式）

```typescript
// composables/useDarkMode.ts
import { ref, watch, onMounted } from 'vue'
import { useMediaQuery } from './useMediaQuery'
import { useLocalStorage } from './useLocalStorage'

/**
 * 暗黑模式 Hook：管理暗黑模式切换
 * @returns 暗黑模式状态、切换方法
 */
export function useDarkMode() {
  const isDark = useLocalStorage('app-dark-mode', false)
  const systemDark = useMediaQuery('(prefers-color-scheme: dark)')

  // 初始化：如果用户未设置，跟随系统
  onMounted(() => {
    if (isDark.value === undefined || isDark.value === null) {
      isDark.value = systemDark.value
    }
    applyDarkMode(isDark.value)
  })

  // 监听变化，应用到 DOM
  watch(isDark, (val) => {
    applyDarkMode(val)
  })

  function applyDarkMode(dark: boolean) {
    if (dark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  function toggle() {
    isDark.value = !isDark.value
  }

  return { isDark, toggle }
}

// 使用示例
// const { isDark, toggle } = useDarkMode()
// <button @click="toggle">{{ isDark ? '☀️ 浅色' : '🌙 暗黑' }}</button>
```

### 10. useFetch（网络请求）

```typescript
// composables/useFetch.ts
import { ref, shallowRef } from 'vue'

interface UseFetchOptions {
  immediate?: boolean      // 是否立即执行，默认 true
  initialData?: any        // 初始数据
  onSuccess?: (data: any) => void
  onError?: (error: Error) => void
}

/**
 * 网络请求 Hook：封装 fetch，提供加载状态、错误处理、手动刷新
 * @param url 请求 URL
 * @param options 请求选项
 * @returns 数据、加载状态、错误、执行方法、刷新方法
 */
export function useFetch<T = any>(url: string, options: UseFetchOptions = {}) {
  const { immediate = true, initialData = null, onSuccess, onError } = options

  const data = shallowRef<T | null>(initialData)
  const isLoading = ref(false)
  const error = ref<Error | null>(null)

  async function execute(fetchOptions?: RequestInit) {
    isLoading.value = true
    error.value = null
    try {
      const response = await fetch(url, fetchOptions)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      data.value = result
      onSuccess?.(result)
      return result
    } catch (e) {
      error.value = e as Error
      onError?.(e as Error)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function refresh() {
    return execute()
  }

  if (immediate) {
    execute()
  }

  return { data, isLoading, error, execute, refresh }
}

// 使用示例
// const { data, isLoading, error, refresh } = useFetch<User>('/api/user/1')
// <div v-if="isLoading">加载中...</div>
// <div v-else-if="error">{{ error.message }}</div>
// <div v-else>{{ data?.name }}</div>
// <button @click="refresh">刷新</button>
```

### 11. useCountdown（倒计时）

```typescript
// composables/useCountdown.ts
import { ref, computed, onUnmounted } from 'vue'

/**
 * 倒计时 Hook
 * @param seconds 倒计时秒数
 * @returns 剩余时间、是否结束、开始、暂停、重置
 */
export function useCountdown(seconds: number) {
  const remaining = ref(seconds)
  const isRunning = ref(false)
  let timer: ReturnType<typeof setInterval> | null = null

  const isFinished = computed(() => remaining.value <= 0)
  const minutes = computed(() => Math.floor(remaining.value / 60))
  const secs = computed(() => remaining.value % 60)
  const formatted = computed(() =>
    `${String(minutes.value).padStart(2, '0')}:${String(secs.value).padStart(2, '0')}`
  )

  function start() {
    if (isRunning.value || isFinished.value) return
    isRunning.value = true
    timer = setInterval(() => {
      remaining.value--
      if (remaining.value <= 0) {
        stop()
      }
    }, 1000)
  }

  function stop() {
    isRunning.value = false
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  function reset(newSeconds?: number) {
    stop()
    remaining.value = newSeconds ?? seconds
  }

  onUnmounted(stop)

  return { remaining, isRunning, isFinished, formatted, start, stop, reset }
}

// 使用示例（发送验证码倒计时）
// const { remaining, isRunning, start, formatted } = useCountdown(60)
// <button @click="start" :disabled="isRunning">
//   {{ isRunning ? `${remaining}s 后重发` : '发送验证码' }}
// </button>
```

### 12. usePagination（分页）

```typescript
// composables/usePagination.ts
import { ref, computed } from 'vue'

interface UsePaginationOptions {
  page?: number          // 当前页，默认 1
  pageSize?: number      // 每页条数，默认 10
  total?: number         // 总条数
}

/**
 * 分页 Hook：管理分页状态和逻辑
 * @param options 分页选项
 * @returns 分页状态和方法
 */
export function usePagination(options: UsePaginationOptions = {}) {
  const { page = 1, pageSize = 10, total = 0 } = options

  const currentPage = ref(page)
  const currentPageSize = ref(pageSize)
  const totalCount = ref(total)

  // 总页数
  const totalPages = computed(() =>
    Math.max(1, Math.ceil(totalCount.value / currentPageSize.value))
  )

  // 是否有上一页/下一页
  const hasPrev = computed(() => currentPage.value > 1)
  const hasNext = computed(() => currentPage.value < totalPages.value)

  // 数据起始索引
  const startIndex = computed(() => (currentPage.value - 1) * currentPageSize.value)
  const endIndex = computed(() => Math.min(startIndex.value + currentPageSize.value, totalCount.value))

  function goToPage(page: number) {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
    }
  }

  function nextPage() {
    if (hasNext.value) currentPage.value++
  }

  function prevPage() {
    if (hasPrev.value) currentPage.value--
  }

  function changePageSize(size: number) {
    currentPageSize.value = size
    currentPage.value = 1  // 切换每页条数时回到第一页
  }

  function setTotal(total: number) {
    totalCount.value = total
  }

  function reset() {
    currentPage.value = 1
    totalCount.value = 0
  }

  return {
    currentPage,
    pageSize: currentPageSize,
    total: totalCount,
    totalPages,
    hasPrev,
    hasNext,
    startIndex,
    endIndex,
    goToPage,
    nextPage,
    prevPage,
    changePageSize,
    setTotal,
    reset
  }
}
```

### 13. useTable（表格）

```typescript
// composables/useTable.ts
import { ref, reactive, onMounted } from 'vue'
import { usePagination } from './usePagination'

interface UseTableOptions<T> {
  fetchData: (params: any) => Promise<{ list: T[]; total: number }>
  immediate?: boolean
  defaultParams?: Record<string, any>
}

/**
 * 表格 Hook：整合搜索、分页、加载状态
 * @param options 表格选项
 * @returns 表格数据、加载状态、分页、搜索、刷新
 */
export function useTable<T = any>(options: UseTableOptions<T>) {
  const { fetchData, immediate = true, defaultParams = {} } = options

  const tableData = ref<T[]>([])
  const loading = ref(false)
  const searchParams = reactive({ ...defaultParams })
  const pagination = usePagination()

  async function loadData() {
    loading.value = true
    try {
      const { list, total } = await fetchData({
        ...searchParams,
        page: pagination.currentPage.value,
        pageSize: pagination.pageSize.value
      })
      tableData.value = list
      pagination.setTotal(total)
    } catch (error) {
      console.error('加载数据失败:', error)
    } finally {
      loading.value = false
    }
  }

  function handleSearch() {
    pagination.currentPage.value = 1
    loadData()
  }

  function handleReset() {
    Object.assign(searchParams, defaultParams)
    handleSearch()
  }

  function handlePageChange(page: number) {
    pagination.goToPage(page)
    loadData()
  }

  function handleSizeChange(size: number) {
    pagination.changePageSize(size)
    loadData()
  }

  function refresh() {
    loadData()
  }

  if (immediate) {
    onMounted(loadData)
  }

  return {
    tableData,
    loading,
    searchParams,
    pagination,
    loadData,
    handleSearch,
    handleReset,
    handlePageChange,
    handleSizeChange,
    refresh
  }
}
```

### 14. useInterval（定时器）

```typescript
// composables/useInterval.ts
import { ref, onUnmounted } from 'vue'

/**
 * 定时器 Hook：自动管理 setInterval
 * @param callback 回调函数
 * @param delay 间隔时间（毫秒），null 表示暂停
 * @param immediate 是否立即执行一次
 */
export function useInterval(callback: () => void, delay: number | null, immediate = false) {
  const isActive = ref(false)
  let timer: ReturnType<typeof setInterval> | null = null

  function start() {
    if (isActive.value || delay === null) return
    isActive.value = true
    if (immediate) callback()
    timer = setInterval(callback, delay)
  }

  function stop() {
    isActive.value = false
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  start()
  onUnmounted(stop)

  return { isActive, start, stop }
}
```

---

## 三、Hooks 组合与复用

### 1. Hooks 组合示例

```typescript
// useUserProfile.ts：组合多个 Hook
import { useFetch } from './useFetch'
import { useLocalStorage } from './useLocalStorage'
import { useTitle } from './useTitle'

export function useUserProfile(userId: string) {
  // 组合 useFetch
  const { data: user, isLoading, error, refresh } = useFetch(`/api/users/${userId}`)

  // 组合 useLocalStorage 缓存
  const cachedUser = useLocalStorage(`user-${userId}`, null)

  // 组合 useTitle
  const title = useTitle(user.value?.name ? `${user.value.name} - 个人中心` : '个人中心')

  return { user, isLoading, error, refresh, cachedUser, title }
}
```

### 2. 通用 Hooks 库推荐

| 库名 | 说明 | Star |
|------|------|------|
| **VueUse** | 最流行的 Vue3 Hooks 库，200+ 常用 Hooks | ⭐ 18k+ |
| **ahooks-vue** | 阿里出品的 Vue Hooks 库 | ⭐ 1k+ |
| **radix-vue** | 无样式组件 + Hooks | ⭐ 3k+ |

```bash
# 安装 VueUse
npm install @vueuse/core
```

```typescript
// VueUse 使用示例
import { useDebounce, useLocalStorage, useMouse, useDark, useToggle } from '@vueuse/core'

// 防抖
const debounced = useDebounce(searchText, 500)

// 本地存储
const token = useLocalStorage('token', '')

// 鼠标位置
const { x, y } = useMouse()

// 暗黑模式
const isDark = useDark()
const toggleDark = useToggle(isDark)
```

---

## 四、最佳实践

### 1. 命名规范

- [ ] **use 前缀**：所有 Hook 以 `use` 开头，如 `useDebounce`、`useFetch`
- [ ] **驼峰命名**：使用 camelCase，如 `useUserProfile`
- [ ] **动词+名词**：`use` + 动词/名词，如 `useFetch`、`usePagination`
- [ ] **文件命名**：与 Hook 名一致，如 `useDebounce.ts`
- [ ] **目录组织**：统一放在 `composables/` 或 `hooks/` 目录

### 2. 设计规范

- [ ] **单一职责**：一个 Hook 只做一件事
- [ ] **返回对象**：统一返回对象，便于解构和扩展
- [ ] **自动清理**：onUnmounted 中清理副作用
- [ ] **类型安全**：使用 TypeScript 泛型
- [ ] **参数灵活**：支持 ref 或原始值，使用 `unref` 处理
- [ ] **可组合**：Hooks 之间可以相互调用组合
- [ ] **无副作用调用**：在 setup 顶层调用，不在条件/循环中调用

### 3. 性能优化

- [ ] **使用 shallowRef**：大对象不需要深度响应式时使用 shallowRef
- [ ] **避免过度响应式**：不需要响应式的数据不要用 ref/reactive
- [ ] **合理使用 watch**：避免不必要的深度监听，使用 `immediate` 控制初始化
- [ ] **及时清理**：定时器、事件监听在 onUnmounted 中清理
- [ ] **懒加载**：非必要的 Hook 可以延迟初始化

### 4. 测试

```typescript
// useDebounce.test.ts
import { ref } from 'vue'
import { useDebounce } from './useDebounce'

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should debounce value changes', () => {
    const value = ref('')
    const debounced = useDebounce(value, 300)

    value.value = 'a'
    expect(debounced.value).toBe('')

    vi.advanceTimersByTime(200)
    value.value = 'ab'
    expect(debounced.value).toBe('')

    vi.advanceTimersByTime(300)
    expect(debounced.value).toBe('ab')
  })
})
```

---

## 五、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **Hooks 失去响应式** | 直接解构 ref 对象 | 使用 `toRefs` 或 `storeToRefs` 解构 |
| **定时器不停止** | 未在 onUnmounted 中清理 | 在 onUnmounted 中 clearInterval/clearTimeout |
| **事件监听器内存泄漏** | 未移除事件监听 | 在 onUnmounted 中 removeEventListener |
| **Hooks 在条件中调用** | 违反 Hooks 调用规则 | 将条件移到 Hook 内部，或在 setup 顶层调用 |
| **TypeScript 类型错误** | 未使用泛型 / 类型推断失败 | 显式指定泛型类型，如 `useFetch<User>()` |
| **useLocalStorage 数据不同步** | 未设置 deep watch / JSON 序列化错误 | 使用 `{ deep: true }` 监听，处理循环引用 |
| **useFetch 重复请求** | immediate 默认 true，组件重挂载重复请求 | 控制 immediate，或使用缓存 |
| **Hooks 之间循环依赖** | A 调用 B，B 调用 A | 重构 Hooks，提取公共逻辑到第三个 Hook |
| **SSR 环境报错** | 使用了 window/document 等浏览器 API | 判断 `typeof window !== 'undefined'`，使用 onMounted |
| **useEventListener target 为 null** | 组件未挂载时 target ref 为空 | 使用 watch 监听 target 变化，动态添加/移除监听 |
| **防抖/节流不生效** | 每次渲染创建新的函数引用 | 使用 useCallback 或在 Hook 内部维护稳定引用 |
| **Hooks 返回值过多** | 职责不清晰，返回太多内容 | 拆分 Hook，每个 Hook 只返回相关的状态和方法 |
| **性能问题** | 深度监听大对象 / 不必要的响应式 | 使用 shallowRef、shallowReactive，避免 deep watch |
| **Hooks 命名冲突** | 多个 Hook 返回同名变量 | 解构时重命名，如 `const { data: user } = useFetch()` |

---

## 六、关联笔记

### Vue3 生态
- [[Vue3-组合式API设计模式]] · [[Vue3-响应式原理Proxy]] · [[Vue3-组件通信全方案]]
- [[Vue3-性能优化实战]] · [[Vue3-自定义Hooks封装]] · [[Vue3-路由与状态管理]]
- [[Pinia-状态管理核心]]

### 前端工程化
- [[前端工程化知识点系统梳理_优化版]] · [[Vite-构建原理与插件开发]] · [[TypeScript-类型系统进阶]]
- [[组件库设计与发布]] · [[前端性能优化实战]]

### 前端框架
- [[React-Hooks核心原理与实战]] · [[React-状态管理方案对比]] · [[Svelte-响应式框架入门]]

### 导航
- [[MOC-前端开发]] · [[MOC-Vue3TS-四级展开]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[Vue3-组合式API设计模式]] 组合式 API 基础 → 学习 [[Vue3-响应式原理Proxy]] 响应式原理 → 深入本文自定义 Hooks 封装 → 实践常用 Hooks（防抖/节流/请求/分页等）→ 研究 VueUse 等成熟 Hooks 库 → 应用于实际项目的逻辑复用。
