---
title: Axios网络请求封装
tags: [Axios, 前端, HTTP, 网络请求, 拦截器, TypeScript, Vue3]
category: 前端开发
created: 2026-09-07
updated: 2026-09-07
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 重要
pre: ["[[TypeScript基础语法]]]]", "[[[[Vue3-组件通信全方案]]"]
aliases: [Axios封装, Axios请求封装, 前端HTTP封装]
---

# Axios网络请求封装


> Axios是基于Promise的HTTP客户端，支持浏览器和Node.js。在企业级前端项目中，直接使用Axios会导致重复的错误处理、Token注入、 loading 控制散落在各处。统一封装是前端工程化的基础步骤。
>
> **封装目标**：统一baseURL、请求/响应拦截器、错误处理、Token刷新、取消请求、类型安全。

---

## 一、概述：为什么要封装Axios

### 1.1 直接使用的痛点

| 痛点 | 表现 |
|------|------|
| Token管理重复 | 每个请求手动加 `headers.Authorization` |
| 错误处理散落 | 每个 `.catch()` 里重复写401/403/500处理 |
| Loading不统一 | 每个组件自己控制loading状态 |
| 接口类型缺失 | 返回数据是 `any`，无类型提示 |
| 无法取消请求 | 路由切换时旧请求仍在执行 |
|  baseURL硬编码 | 开发/测试/生产环境切换困难 |

### 1.2 封装架构

```text
src/api/
├── request.ts          — Axios实例 + 拦截器（核心）
├── types.ts            — 通用响应类型定义
├── modules/
│   ├── user.ts         — 用户相关接口
│   ├── order.ts        — 订单相关接口
│   └── product.ts      — 商品相关接口
└── index.ts            — 统一导出
```

---

## 二、底层原理：拦截器与适配器

### 2.1 Axios请求流程

```text
调用 axios(config)
    ↓
请求拦截器（request interceptor）— 可修改config、加Token
    ↓
适配器（adapter）— 浏览器用XMLHttpRequest，Node用http
    ↓
服务器响应
    ↓
响应拦截器（response interceptor）— 统一处理数据/错误
    ↓
Promise resolve/reject
```

### 2.2 拦截器执行顺序

```text
请求拦截器：后添加的先执行（栈结构，LIFO）
响应拦截器：先添加的先执行（队列结构，FIFO）

示例：
axios.interceptors.request.use(A)  // 后执行
axios.interceptors.request.use(B)  // 先执行
→ 实际顺序：B → A → 服务器 → A → B
```

---

## 三、实操：TypeScript完整封装

### 3.1 通用类型定义

```typescript
// src/api/types.ts
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface RequestConfig {
  showLoading?: boolean      // 是否显示全局loading
  showError?: boolean        // 是否自动提示错误
  retry?: number             // 失败重试次数
  retryDelay?: number        // 重试间隔(ms)
}

export type ApiPromise<T = any> = Promise<ApiResponse<T>>
```

### 3.2 核心封装（request.ts）

```typescript
// src/api/request.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage, ElLoading } from 'element-plus'
import type { ApiResponse, RequestConfig } from './types'

// 全局loading计数
let loadingCount = 0
let loadingInstance: any = null

const showLoading = () => {
  if (loadingCount === 0) {
    loadingInstance = ElLoading.service({ fullscreen: true, text: '加载中...' })
  }
  loadingCount++
}

const hideLoading = () => {
  loadingCount--
  if (loadingCount <= 0) {
    loadingInstance?.close()
    loadingCount = 0
  }
}

// 创建Axios实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig & RequestConfig) => {
    // 显示loading
    if (config.showLoading !== false) showLoading()

    // 注入Token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // GET请求加时间戳防缓存
    if (config.method === 'get') {
      config.params = { ...config.params, _t: Date.now() }
    }

    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const config = response.config as RequestConfig
    if (config.showLoading !== false) hideLoading()

    const res = response.data

    // 业务成功
    if (res.code === 200) {
      return res as any
    }

    // 业务失败
    if (config.showError !== false) {
      ElMessage.error(res.message || '请求失败')
    }

    // Token过期
    if (res.code === 401) {
      handleTokenExpired()
    }

    return Promise.reject(new Error(res.message || 'Error'))
  },
  async (error) => {
    const config = error.config as RequestConfig
    if (config?.showLoading !== false) hideLoading()

    // HTTP错误处理
    if (error.response) {
      const { status } = error.response
      const messages: Record<number, string> = {
        400: '请求参数错误',
        401: '未授权，请重新登录',
        403: '拒绝访问',
        404: '请求资源不存在',
        500: '服务器内部错误',
        502: '网关错误',
        503: '服务不可用',
        504: '网关超时',
      }
      if (config?.showError !== false) {
        ElMessage.error(messages[status] || `请求错误(${status})`)
      }
      if (status === 401) handleTokenExpired()
    } else if (error.code === 'ECONNABORTED') {
      if (config?.showError !== false) ElMessage.error('请求超时，请稍后重试')
    } else {
      if (config?.showError !== false) ElMessage.error('网络异常，请检查网络连接')
    }

    return Promise.reject(error)
  }
)

// Token过期处理
let isRefreshing = false
let refreshSubscribers: ((token: string) => void)[] = []

const handleTokenExpired = () => {
  localStorage.removeItem('token')
  window.location.href = '/login'
}

// 封装请求方法
export function request<T = any>(config: AxiosRequestConfig & RequestConfig): ApiPromise<T> {
  return service(config) as unknown as ApiPromise<T>
}

export function get<T = any>(url: string, params?: any, config?: RequestConfig): ApiPromise<T> {
  return request<T>({ method: 'get', url, params, ...config })
}

export function post<T = any>(url: string, data?: any, config?: RequestConfig): ApiPromise<T> {
  return request<T>({ method: 'post', url, data, ...config })
}

export function put<T = any>(url: string, data?: any, config?: RequestConfig): ApiPromise<T> {
  return request<T>({ method: 'put', url, data, ...config })
}

export function del<T = any>(url: string, params?: any, config?: RequestConfig): ApiPromise<T> {
  return request<T>({ method: 'delete', url, params, ...config })
}

export default service
```

### 3.3 业务模块封装

```typescript
// src/api/modules/user.ts
import { get, post } from '../request'
import type { ApiResponse } from '../types'

export interface UserInfo {
  id: number
  username: string
  email: string
  avatar: string
  roles: string[]
}

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResult {
  token: string
  refreshToken: string
  expiresIn: number
}

// 用户登录
export const login = (data: LoginParams) =>
  post<LoginResult>('/auth/login', data, { showLoading: false })

// 获取用户信息
export const getUserInfo = () =>
  get<UserInfo>('/user/info')

// 修改密码
export const changePassword = (data: { oldPassword: string; newPassword: string }) =>
  post<void>('/user/password', data)

// 上传头像（FormData）
export const uploadAvatar = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return post<{ url: string }>('/user/avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
```

### 3.4 取消请求（AbortController）

```typescript
// 方式1：使用AbortController
const controller = new AbortController()
get('/data', {}, { signal: controller.signal })
// 取消
controller.abort()

// 方式2：封装可取消的请求
export function createRequest<T = any>() {
  let controller: AbortController | null = null
  return {
    send: (config: AxiosRequestConfig & RequestConfig) => {
      controller = new AbortController()
      return request<T>({ ...config, signal: controller.signal })
    },
    cancel: () => controller?.abort(),
  }
}

// Vue组件中使用
import { onBeforeUnmount } from 'vue'
const searchRequest = createRequest()
const handleSearch = async () => {
  searchRequest.cancel() // 取消上一次请求
  const res = await searchRequest.send({ url: '/search', method: 'get', params: query })
}
onBeforeUnmount(() => searchRequest.cancel())
```

### 3.5 下载文件封装

```typescript
export const downloadFile = (url: string, params?: any, filename?: string) => {
  return request<Blob>({
    method: 'get',
    url,
    params,
    responseType: 'blob',
    showLoading: true,
  }).then((res) => {
    const blob = new Blob([res as unknown as BlobPart])
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename || 'download'
    link.click()
    URL.revokeObjectURL(link.href)
  })
}
```

---

## 四、常见问题与排查

### 4.1 Token刷新（401自动刷新）

```typescript
// 响应拦截器中处理401
if (res.code === 401 || error.response?.status === 401) {
  const config = error.config
  if (!isRefreshing) {
    isRefreshing = true
    refreshToken()
      .then((newToken) => {
        localStorage.setItem('token', newToken)
        refreshSubscribers.forEach((cb) => cb(newToken))
        refreshSubscribers = []
      })
      .catch(() => {
        handleTokenExpired()
      })
      .finally(() => { isRefreshing = false })
  }
  // 将当前请求加入重试队列
  return new Promise((resolve) => {
    refreshSubscribers.push((token: string) => {
      config.headers.Authorization = `Bearer ${token}`
      resolve(service(config))
    })
  })
}
```

### 4.2 跨域问题

**开发环境**（Vite代理）：
```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

**生产环境**：Nginx反向代理或后端配置CORS。

### 4.3 大文件上传进度

```typescript
export const uploadLargeFile = (file: File, onProgress?: (percent: number) => void) => {
  const formData = new FormData()
  formData.append('file', file)
  return request('/upload', {
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      const percent = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1))
      onProgress?.(percent)
    },
  })
}
```

---

## 五、进阶与最佳实践

### 5.1 接口自动生成（OpenAPI → TypeScript）

使用 `openapi-typescript` 或 `swagger-typescript-api` 根据后端OpenAPI文档自动生成类型定义和接口函数，避免手动维护类型。

```bash
npx swagger-typescript-api -p http://localhost:8080/v3/api-docs -o ./src/api -n generated.ts
```

### 5.2 请求重试机制

```typescript
// 响应拦截器错误处理中添加重试
if (config.retry && config.retry > 0) {
  config.retry--
  await new Promise((resolve) => setTimeout(resolve, config.retryDelay || 1000))
  return service(config)
}
```

### 5.3 最佳实践清单

- [ ] 统一baseURL通过环境变量管理
- [ ] 请求拦截器注入Token、处理loading
- [ ] 响应拦截器统一处理业务码和HTTP错误
- [ ] 401自动刷新Token或跳转登录
- [ ] 所有接口定义TypeScript类型（入参+出参）
- [ ] 按业务模块组织接口文件
- [ ] 路由切换时取消未完成请求
- [ ] 文件上传/下载单独封装
- [ ] 接口错误有统一的日志上报

---

## 关联笔记

- [[Vue3-组件通信全方案]] — Vue3组件通信
- [[TypeScript基础语法]] — TypeScript基础
- [[ESLint+Prettier+Stylelint规范]] — 代码规范
- [[Husky+Commitlint提交规范]] — 提交规范
- [[Vite构建工具原理与实践]] — Vite构建
