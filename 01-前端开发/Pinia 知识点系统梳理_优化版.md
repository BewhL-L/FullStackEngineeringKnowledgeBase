---
title: Pinia 知识点系统梳理
tags: [前端, Pinia, 状态管理, Vue3]
created: 2026-08-12
updated: 2026-08-12
---

# Pinia 知识点系统梳理（优化版）

> **文档说明**：本文档参照《Java知识点完整整合大全》排版风格，系统梳理 Pinia 技术栈。包含概述、核心特性、常用用法、注意事项四大模块，辅以动态可视化解析图、深度讲解与精简总结。**优化版**在原有内容基础上，为每个知识点补充了作用、原理、用法的深度解析，并新增了知识点图解。

---

## 1. 概述

Pinia 是 **Vue 官方推荐的状态管理库**，由 Vue 核心团队成员 Eduardo San Martin Morote 开发，是 Vuex 的官方继任者。Pinia 于 2021 年正式发布，2022 年被 Vue 官方列为推荐状态管理方案，完全适配 Vue3 的 Composition API 和 TypeScript。

**核心定位**：
- Vue 官方状态管理库，替代 Vuex
- 完整 TypeScript 支持，类型推断开箱即用
- Composition API 风格，API 简洁直观
- 支持 DevTools、时间旅行调试、SSR

**Vuex vs Pinia 核心差异**：

| 对比项 | Vuex | Pinia |
|--------|------|-------|
| 设计风格 | Options API 风格（state/mutations/actions/getters） | Composition API 风格（Setup Store） |
| Mutations | 必须通过 mutations 修改 state | 移除 mutations，直接修改或用 actions |
| 模块化 | 需手动嵌套 modules，命名空间复杂 | 天然模块化，每个 store 独立 |
| TypeScript | 需额外类型声明，体验一般 | 原生 TS，类型自动推导 |
| 异步操作 | actions 支持异步 | actions 直接支持 async/await |
| 学习成本 | 较高（概念多） | 极低（API 少） |
| 打包体积 | 较大 | 更小（Tree-shaking 友好） |

---


---
## 2. 核心特性

<div style="background:linear-gradient(135deg,#f093fb,#f5576c);border-radius:16px;padding:24px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#fff;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes piniaStore{0%,100%{transform:scale(1);opacity:.85}50%{transform:scale(1.03);opacity:1}}.pinia-core{display:inline-block;width:28%;vertical-align:top;margin:0 2%;background:rgba(255,255,255,.18);border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.08);padding:12px;font-size:11px;text-align:center;animation:piniaStore 3s ease-in-out infinite}.pinia-core:nth-child(2){animation-delay:.5s}.pinia-core:nth-child(3){animation-delay:1s}.pinia-icon{font-size:22px;margin-bottom:6px}.pinia-name{font-weight:700;font-size:13px;margin-bottom:4px}</style>
<div style="text-align:center;font-size:16px;font-weight:700;margin-bottom:16px;padding-bottom:12px;border-bottom:1.5px solid rgba(255,255,255,.22);letter-spacing:1px;text-shadow:0 1px 3px rgba(0,0,0,.12)">Pinia Store 三大核心</div>
<div style="text-align:center">
<div class="pinia-core"><div class="pinia-icon">📦</div><div class="pinia-name">State</div><div style="font-size:10px;opacity:.85">响应式状态<br>ref/reactive 定义<br>可直接读写</div></div>
<div class="pinia-core"><div class="pinia-icon">🧮</div><div class="pinia-name">Getters</div><div style="font-size:10px;opacity:.85">计算属性<br>computed 定义<br>有缓存，可传参</div></div>
<div class="pinia-core"><div class="pinia-icon">⚡</div><div class="pinia-name">Actions</div><div style="font-size:10px;opacity:.85">业务方法<br>普通函数定义<br>同步异步均可</div></div>
</div>
</div>

### 2.1 安装与创建 Store

```bash
npm install pinia
```

```javascript
// main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.mount('#app')
```

**Options Store（类似 Vuex）**：

```javascript
// stores/counter.js
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', {
  state: () => ({ count: 0 }),
  getters: {
    doubleCount: (state) => state.count * 2
  },
  actions: {
    increment() {
      this.count++
    }
  }
})
```

**Setup Store（推荐，Composition API 风格）**：

```javascript
// stores/counter.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const doubleCount = computed(() => count.value * 2)
  function increment() {
    count.value++
  }
  return { count, doubleCount, increment }
})
```

> 🔍 **知识点深度解析**
>
> **作用**：defineStore 创建 store 定义，返回 useXxxStore 函数。两种风格：Options Store（类似 Vuex，state/getters/actions）和 Setup Store（Composition API 风格，ref/computed/function，推荐）。
>
> **原理**：createPinia() 创建 Pinia 实例（包含所有 store 的注册表），app.use(pinia) 安装（通过 provide 注入到应用）。defineStore(id, options/setup)：id 是 store 唯一标识（不能重复），返回 useStore 函数。第一次调用 useStore() 时，Pinia 创建 store 实例（单例，全局唯一），后续调用返回同一实例。Options Store：state 用 reactive 包裹，getters 转 computed，actions 绑定 this 到 store。Setup Store：执行 setup 函数，返回的 ref 转 state，computed 转 getters，函数转 actions。两种风格底层一致，Setup Store 更灵活（可使用组合函数、自由组织逻辑）。
>
> **用法要点**：① 新项目用 Setup Store（Composition API 风格，更灵活，TS 类型更好）；② store id 唯一（不能重复，否则覆盖）；③ useXxxStore 命名规范（use + 名称 + Store）；④ store 必须在 setup 中或之后调用（不能在组件外直接调用，Pinia 未安装）；⑤ 多个 store 可互相调用（在 actions 中 useOtherStore()）；⑥ 全局状态放 store，组件局部状态用 ref/reactive；⑦ 按功能分 store（user/cart/order/app），不要一个大 store。

### 2.2 State（状态）

```javascript
// 定义
export const useUserStore = defineStore('user', () => {
  const userInfo = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  return { userInfo, token }
})

// 组件中使用
<script setup>
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

const userStore = useUserStore()

// 方式1：直接使用（不解构）
console.log(userStore.token)

// 方式2：解构保持响应式（用 storeToRefs）
const { token, userInfo } = storeToRefs(userStore)

// 修改 state
userStore.token = 'new-token'  // 直接修改
userStore.$patch({ token: 'new' })  // $patch 批量修改
userStore.$patch((state) => {      // $patch 函数式
  state.token = 'new'
  state.userInfo = { name: '张三' }
})
userStore.$reset()  // 重置到初始状态
</script>
```

> 🔍 **知识点深度解析**
>
> **作用**：State 是 store 的核心数据，响应式的（组件中使用会自动更新）。可直接修改，也可用 $patch 批量修改，$reset 重置。
>
> **原理**：Setup Store 中返回的 ref 会被 Pinia 解包（store.count 不需要 .value，直接访问），内部用 reactive 包裹整个 store（所以 store 本身是响应式的）。直接修改 store.count = 1 会触发响应式更新（因为底层是 ref/reactive）。$patch(object)：浅合并对象到 state（批量修改，只触发一次更新，比多次直接修改性能好）。$patch(function)：函数接收 state，可进行复杂修改（如数组 push/splice）。$reset()：重新执行 state 初始函数，重置所有状态（Setup Store 中需要自己实现，Pinia 2.x 支持）。storeToRefs：将 store 的 state/getters 转为 ref（解构时保持响应式），类似 toRefs。
>
> **用法要点**：① 组件中直接用 store.xxx（不需要 .value，Pinia 自动解包）；② 解构用 storeToRefs（保持响应式），普通解构会丢失响应式；③ 简单修改直接赋值（store.count++）；④ 批量修改用 $patch（减少更新次数，性能好）；⑤ 复杂修改用 $patch 函数（state => { state.list.push(item) }）；⑥ 重置用 $reset()（Options Store 自动支持，Setup Store 需 Pinia 2.x+）；⑦ 不要在组件外直接修改 store（用 actions 封装业务逻辑）；⑧ 注意：storeToRefs 只包含 state 和 getters，actions 可直接解构（不是响应式的）。

### 2.3 Getters（计算属性）

```javascript
export const useCartStore = defineStore('cart', () => {
  const items = ref([])
  
  // 基本 getter
  const totalCount = computed(() => 
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )
  
  // 带参数的 getter（返回函数）
  const getItemById = computed(() => (id) => 
    items.value.find(item => item.id === id)
  )
  
  // 访问其他 getter
  const totalPrice = computed(() => 
    items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )
  
  return { items, totalCount, totalPrice, getItemById }
})

// 使用
const cartStore = useCartStore()
console.log(cartStore.totalCount)  // 直接访问
console.log(cartStore.getItemById(1))  // 带参数
```

> 🔍 **知识点深度解析**
>
> **作用**：Getters 是派生状态（基于 state 计算），有缓存（依赖不变不重新计算），类似 computed。可访问其他 getter，可带参数（返回函数）。
>
> **原理**：Setup Store 中返回的 computed 被 Pinia 识别为 getter，store.getterName 自动解包（不需要 .value）。computed 内部有 dirty 标记，依赖变更时 dirty=true，第一次访问时重新计算并缓存，后续访问直接返回缓存（依赖不变）。带参数 getter：computed 返回一个函数（闭包），每次调用函数执行计算（这种没有缓存，因为参数不同结果不同；如果需要缓存用 Map 缓存结果）。访问其他 getter：在 computed 中直接用其他 getter 变量（Setup Store 中是闭包变量）。Options Store 中 getter 接收 state 参数，this 指向 store（可访问其他 getter）。
>
> **用法要点**：① 派生状态用 getter（有缓存，不要用方法每次计算）；② getter 中不要写副作用（如修改 state、发请求）；③ 带参数 getter 返回函数（computed(() => (param) => ...)），但这种没有缓存；④ 需要缓存的带参数 getter 用 Map 缓存结果（或用计算属性+参数变化触发）；⑤ getter 可访问其他 getter（直接用变量）；⑥ 组件中用 store.getterName（自动解包）；⑦ 解构 getter 用 storeToRefs（保持响应式）；⑧ 注意：getter 是只读的，不要直接修改（修改 state 即可）。

### 2.4 Actions（业务方法）

```javascript
export const useUserStore = defineStore('user', () => {
  const userInfo = ref(null)
  const token = ref('')
  
  // 同步 action
  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }
  
  // 异步 action
  async function login(credentials) {
    try {
      const res = await api.login(credentials)
      token.value = res.token
      userInfo.value = res.user
      localStorage.setItem('token', res.token)
      return res
    } catch (error) {
      throw error
    }
  }
  
  // 调用其他 store
  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    // 调用其他 store
    const cartStore = useCartStore()
    cartStore.clear()
  }
  
  return { userInfo, token, setToken, login, logout }
})

// 使用
const userStore = useUserStore()
await userStore.login({ username, password })
```

> 🔍 **知识点深度解析**
>
> **作用**：Actions 封装业务逻辑（同步/异步），修改 state、调用 API、调用其他 store。是 store 中唯一应该包含业务逻辑的地方。
>
> **原理**：Setup Store 中返回的普通函数被 Pinia 识别为 action，绑定 this 到 store（Options Store 中 this 是 store，Setup Store 中用闭包变量）。actions 可直接 async/await（不需要像 Vuex 那样区分 mutations/actions）。actions 中可直接修改 state（ref.value = xxx），不需要 mutation。actions 可调用其他 store 的 actions（在函数内 useOtherStore()）。actions 返回 Promise（async 函数），组件中可 await。Pinia DevTools 会记录 actions 调用（支持时间旅行调试）。
>
> **用法要点**：① 业务逻辑写在 actions（不要在组件中直接修改 state，除非简单场景）；② 异步操作直接用 async/await（不需要 mutations）；③ actions 中可调用其他 store（useOtherStore()）；④ actions 返回数据或 Promise（组件中 await）；⑤ 错误处理：actions 中 try-catch 或抛出让组件处理；⑥ 复杂流程拆分为多个 actions（单一职责）；⑦ actions 中不要访问 DOM（store 应该是纯逻辑，与视图无关）；⑧ 注意：Setup Store 中 actions 用普通函数（不要用箭头函数，否则 this 不对，但 Setup Store 中一般不用 this）。

### 2.5 组件中使用 Store

```vue
<script setup>
import { useCounterStore } from '@/stores/counter'
import { storeToRefs } from 'pinia'

const counterStore = useCounterStore()

// 解构 state/getters（保持响应式）
const { count, doubleCount } = storeToRefs(counterStore)
// 解构 actions（直接解构，不是响应式）
const { increment, decrement } = counterStore

// 也可以直接用 counterStore.count
</script>

<template>
  <div>
    <p>Count: {{ count }}</p>
    <p>Double: {{ doubleCount }}</p>
    <button @click="increment">+</button>
    <button @click="decrement">-</button>
  </div>
</template>
```

> 🔍 **知识点深度解析**
>
> **作用**：组件中通过 useXxxStore() 获取 store 实例，访问 state/getters，调用 actions。storeToRefs 解构保持响应式。
>
> **原理**：useCounterStore() 从 Pinia 注册表获取或创建 store 实例（单例），返回 store 对象。store 对象是响应式的（reactive 包裹），直接访问 store.count 会触发依赖收集（组件重新渲染）。直接解构 const { count } = store 会丢失响应式（因为解构的是值，不是 ref）。storeToRefs(store) 将 store 的 state/getters 转为 ref 对象（类似 toRefs），解构后保持响应式。actions 是函数，不需要响应式，可直接解构（const { increment } = store）。模板中 store.count 自动解包（不需要 .value）。
>
> **用法要点**：① 在 setup 中调用 useXxxStore()（不能在 setup 外，Pinia 未安装）；② 简单场景直接用 store.xxx（不解构）；③ 解构 state/getters 用 storeToRefs（保持响应式）；④ actions 直接解构（不需要 storeToRefs）；⑤ 模板中直接用 {{ store.count }} 或解构后的 {{ count }}；⑥ 多个 store 在组件中分别调用（useUserStore(), useCartStore()）；⑦ 路由守卫中用 store：在守卫函数内调用 useStore()（Pinia 已安装）；⑧ 注意：store 是单例，所有组件共享同一个实例（修改一处处处更新）。

### 2.6 持久化（pinia-plugin-persistedstate）

```bash
npm install pinia-plugin-persistedstate
```

```javascript
// main.js
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)
```

```javascript
// store 中配置
export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const userInfo = ref(null)
  return { token, userInfo }
}, {
  persist: {
    key: 'user-store',  // localStorage key
    storage: localStorage,  // 存储位置
    paths: ['token']  // 只持久化 token，不持久化 userInfo
  }
})
```

> 🔍 **知识点深度解析**
>
> **作用**：持久化插件自动将 store state 存到 localStorage/sessionStorage，刷新页面后自动恢复。适合 token、用户信息、主题等需要持久化的数据。
>
> **原理**：pinia-plugin-persistedstate 是 Pinia 插件，通过 pinia.use(plugin) 注册。插件监听 store 的 $subscribe（state 变化时触发），将 state 序列化（JSON.stringify）存到 storage（localStorage/sessionStorage/cookie）。store 初始化时，从 storage 读取数据，用 $patch 恢复到 state。paths 配置只持久化指定字段（白名单），减少存储量。key 配置 storage 的键名（默认是 store id）。可自定义 storage（如 cookie、IndexedDB）和序列化方式。
>
> **用法要点**：① 安装：npm install pinia-plugin-persistedstate，pinia.use(plugin)；② store 配置 persist: true（默认全部持久化到 localStorage）；③ 只持久化部分字段：paths: ['token', 'userInfo.id']；④ 用 sessionStorage：storage: sessionStorage（关闭浏览器清除）；⑤ 自定义 key：key: 'my-app-user'（避免冲突）；⑥ 敏感数据不要持久化到 localStorage（如密码，用 cookie+HttpOnly）；⑦ 大数据不要持久化（localStorage 限制 5MB）；⑧ 注意：持久化的数据是 JSON 序列化的（Date/Map/Set 等特殊类型要自定义序列化）。

### 2.7 插件与高级用法

**自定义插件**：

```javascript
// 插件：给所有 store 添加 $reset 方法（Setup Store）
function resetPlugin({ store }) {
  const initialState = JSON.parse(JSON.stringify(store.$state))
  store.$reset = () => {
    store.$patch(initialState)
  }
}
pinia.use(resetPlugin)

// 插件：添加全局属性
function globalPropertiesPlugin({ store }) {
  store.$api = api  // 所有 store 可访问 this.$api
}
```

**订阅 state 变化**：

```javascript
const userStore = useUserStore()
userStore.$subscribe((mutation, state) => {
  console.log('State changed:', mutation, state)
  localStorage.setItem('user', JSON.stringify(state))
})
```

**订阅 actions**：

```javascript
userStore.$onAction(({ name, store, args, after, onError }) => {
  console.log(`Action ${name} called with`, args)
  after((result) => {
    console.log(`Action ${name} finished with`, result)
  })
  onError((error) => {
    console.error(`Action ${name} error:`, error)
  })
})
```

> 🔍 **知识点深度解析**
>
> **作用**：插件扩展 Pinia 功能（如持久化、日志、重置），$subscribe 监听 state 变化，$onAction 监听 actions 调用（用于日志、错误处理、性能监控）。
>
> **原理**：Pinia 插件是一个函数，接收 context（{ pinia, app, store, options }），可修改 store（添加属性/方法）。pinia.use(plugin) 注册插件，每个 store 创建时都会执行插件。$subscribe(callback, options)：订阅 state 变化，callback 接收 mutation（{ type, storeId, events }）和 state，detached: true 时组件卸载不自动停止订阅。$onAction(callback, detached)：订阅 actions，callback 接收 { name, store, args, after, onError }，after 在 action 完成后调用（可获取返回值），onError 在 action 抛错时调用。这些是 Pinia 的扩展点，可实现日志、持久化、错误追踪等横切关注点。
>
> **用法要点**：① 插件用 pinia.use(plugin) 注册，影响所有 store；② 插件中添加 store 属性：store.$xxx = value；③ $subscribe 监听 state 变化（可用于自定义持久化、日志）；④ $onAction 监听 actions（可用于错误上报、性能监控、审计日志）；⑤ detached: true 时订阅不随组件卸载停止（全局订阅）；⑥ Setup Store 的 $reset 不自动支持，用插件实现（深拷贝初始状态）；⑦ 插件中可访问 app（Vue 应用实例）和 pinia；⑧ 注意：插件中不要做耗时操作（影响所有 store 创建）。

---


---
## 3. 常用用法

### 3.1 用户认证 Store

```javascript
// stores/user.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginApi, getUserInfoApi } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)
  const roles = ref([])
  
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => roles.value.includes('admin'))
  
  async function login(credentials) {
    const res = await loginApi(credentials)
    token.value = res.token
    localStorage.setItem('token', res.token)
    await fetchUserInfo()
    return res
  }
  
  async function fetchUserInfo() {
    const res = await getUserInfoApi()
    userInfo.value = res
    roles.value = res.roles
  }
  
  function logout() {
    token.value = ''
    userInfo.value = null
    roles.value = []
    localStorage.removeItem('token')
  }
  
  return { token, userInfo, roles, isLoggedIn, isAdmin, login, fetchUserInfo, logout }
}, {
  persist: {
    paths: ['token']  // 只持久化 token
  }
})
```

> 🔍 **知识点深度解析**
>
> **作用**：用户认证 Store 是最常见的 Pinia 应用，管理 token、用户信息、角色，提供登录/登出/获取用户信息等方法。配合持久化插件实现刷新不丢失登录态。
>
> **原理**：token 存 ref，初始化时从 localStorage 读取（持久化）。login action 调用登录 API，保存 token，然后获取用户信息。isLoggedIn/isAdmin 是 computed（基于 token/roles 派生）。logout 清除所有状态和 localStorage。persist.paths 只持久化 token（userInfo 每次启动重新获取，避免数据过期）。路由守卫中用 userStore.isLoggedIn 判断是否登录，未登录跳转登录页。请求拦截器中用 userStore.token 添加 Authorization 头。
>
> **用法要点**：① token 持久化（localStorage 或 cookie），userInfo 不持久化（每次启动重新获取）；② 登录后立即获取用户信息（fetchUserInfo）；③ 登出清除所有状态（token/userInfo/roles）；④ 路由守卫：beforeEach 中判断 isLoggedIn 和 roles（权限控制）；⑤ 请求拦截器：config.headers.Authorization = `Bearer ${token}`；⑥ 响应拦截器：401 时清除 token 跳转登录；⑦ 角色权限：isAdmin 或 hasRole(role) 计算属性；⑧ 注意：token 过期处理（401 时刷新 token 或重新登录）。

### 3.2 购物车 Store

```javascript
// stores/cart.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])
  
  const totalCount = computed(() => 
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )
  
  const totalPrice = computed(() => 
    items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )
  
  function addItem(product) {
    const existing = items.value.find(item => item.id === product.id)
    if (existing) {
      existing.quantity++
    } else {
      items.value.push({ ...product, quantity: 1 })
    }
  }
  
  function removeItem(id) {
    const index = items.value.findIndex(item => item.id === id)
    if (index > -1) items.value.splice(index, 1)
  }
  
  function updateQuantity(id, quantity) {
    const item = items.value.find(item => item.id === id)
    if (item) item.quantity = quantity
  }
  
  function clear() {
    items.value = []
  }
  
  return { items, totalCount, totalPrice, addItem, removeItem, updateQuantity, clear }
}, {
  persist: true  // 持久化整个购物车
})
```

> 🔍 **知识点深度解析**
>
> **作用**：购物车 Store 管理商品列表、数量、总价，提供增删改查方法。持久化保存（刷新不丢失）。是电商应用的核心 store。
>
> **原理**：items 是商品数组（每个商品含 id/price/quantity）。totalCount/totalPrice 是 computed（reduce 累加，有缓存，items 变化时重新计算）。addItem：查找是否已存在，存在则数量+1，不存在则添加。removeItem：findIndex + splice 删除。updateQuantity：修改数量。clear：清空数组。persist: true 持久化整个购物车到 localStorage（用户关闭浏览器后再打开，购物车还在）。结算后调用 clear() 清空购物车。
>
> **用法要点**：① 购物车持久化（localStorage，用户体验好）；② 商品用 id 唯一标识（添加时判断是否已存在）；③ 数量更新用 updateQuantity（输入框绑定）；④ 删除用 removeItem（splice 或 filter）；⑤ 总价/总数用 computed（有缓存，不要用方法）；⑥ 结算后 clear() 清空；⑦ 同步到后端：登录后合并本地购物车和服务端购物车；⑧ 注意：购物车数据量大时考虑只持久化 id+quantity（商品信息从接口获取）。

### 3.3 应用配置 Store（主题/语言）

```javascript
// stores/app.js
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useAppStore = defineStore('app', () => {
  const theme = ref(localStorage.getItem('theme') || 'light')
  const locale = ref(localStorage.getItem('locale') || 'zh-CN')
  const sidebarCollapsed = ref(false)
  
  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }
  
  function setLocale(lang) {
    locale.value = lang
  }
  
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
  
  // 监听变化，应用到 DOM
  watch(theme, (val) => {
    document.documentElement.classList.toggle('dark', val === 'dark')
    localStorage.setItem('theme', val)
  })
  
  watch(locale, (val) => {
    localStorage.setItem('locale', val)
  })
  
  return { theme, locale, sidebarCollapsed, toggleTheme, setLocale, toggleSidebar }
})
```

> 🔍 **知识点深度解析**
>
> **作用**：应用配置 Store 管理全局 UI 状态（主题、语言、侧边栏折叠），持久化保存。主题切换影响整个应用样式，语言切换影响 i18n。
>
> **原理**：theme/locale/sidebarCollapsed 是全局 UI 状态。toggleTheme 切换明暗主题，watch 监听 theme 变化，给 html 添加/移除 dark 类（CSS 变量切换暗黑模式），同时存 localStorage。setLocale 修改语言（配合 vue-i18n）。sidebarCollapsed 控制侧边栏展开/折叠（中后台布局常用）。这些状态是全局的（所有组件共享），适合放 Pinia。持久化保存用户偏好（下次打开保持上次设置）。
>
> **用法要点**：① 主题/语言等用户偏好持久化（localStorage）；② 主题切换：CSS 变量 + html.dark 类（Element Plus 暗黑模式）；③ 语言切换：配合 vue-i18n 的 locale.value = lang；④ 侧边栏状态：sidebarCollapsed 控制布局（中后台常见）；⑤ watch 中应用副作用（DOM 操作、localStorage）；⑥ 初始化时从 localStorage 读取（ref 初始值）；⑦ 主题切换要考虑第三方组件（Element Plus 暗黑模式 CSS）；⑧ 注意：SSR 中不能访问 document/localStorage（用 onMounted 或 process.client 判断）。

### 3.4 跨 Store 调用

```javascript
// stores/order.js
import { defineStore } from 'pinia'
import { useCartStore } from './cart'
import { useUserStore } from './user'

export const useOrderStore = defineStore('order', () => {
  const orders = ref([])
  
  async function createOrder() {
    const cartStore = useCartStore()
    const userStore = useUserStore()
    
    if (!userStore.isLoggedIn) {
      throw new Error('请先登录')
    }
    
    const orderData = {
      items: cartStore.items,
      total: cartStore.totalPrice,
      userId: userStore.userInfo.id
    }
    
    const res = await api.createOrder(orderData)
    orders.value.push(res)
    cartStore.clear()  // 清空购物车
    return res
  }
  
  return { orders, createOrder }
})
```

> 🔍 **知识点深度解析**
>
> **作用**：跨 Store 调用实现业务流程串联（如创建订单需要购物车数据和用户信息，完成后清空购物车）。Pinia 天然支持，在 action 中调用其他 store。
>
> **原理**：在 action 函数内调用 useOtherStore() 获取其他 store 实例（单例，与组件中是同一个）。可访问其他 store 的 state/getters，调用其他 store 的 actions。因为 store 是单例，修改其他 store 的 state 会全局生效（如 cartStore.clear() 清空购物车，所有组件更新）。跨 store 调用要注意循环依赖（A 调用 B，B 调用 A 可能导致问题，用延迟调用或重构）。Pinia 不限制跨 store 调用（比 Vuex 模块化简单）。
>
> **用法要点**：① 在 action 中调用 useOtherStore()（不要在 store 顶层调用，可能循环依赖）；② 可访问其他 store 的 state/getters/actions；③ 业务流程串联（订单→购物车→用户）；④ 避免循环依赖（A→B→A，重构或用事件）；⑤ 跨 store 数据传递用方法参数或直接访问；⑥ 复杂业务可引入 service 层（不是所有逻辑都放 store）；⑦ 注意：useOtherStore() 必须在 Pinia 安装后调用（setup 或 action 中都可以）。

### 3.5 SSR 中的 Pinia

```javascript
// entry-client.js / entry-server.js
import { createPinia } from 'pinia'

export function createApp() {
  const app = createSSRApp(App)
  const pinia = createPinia()
  app.use(pinia)
  return { app, pinia }
}

// server.js
const { app, pinia } = createApp()
// 渲染后序列化 state
const state = JSON.stringify(pinia.state.value)

// client.js
const { app, pinia } = createApp()
// 注水：用服务端的 state 初始化
pinia.state.value = JSON.parse(window.__PINIA_STATE__)
app.mount('#app')
```

> 🔍 **知识点深度解析**
>
> **作用**：SSR（服务端渲染）中 Pinia 需要处理状态注水（hydration）：服务端渲染时填充 state，客户端激活时用服务端的 state 初始化，避免客户端重新请求导致不一致。
>
> **原理**：服务端：创建 Pinia 实例，渲染过程中 store 被填充（调用 actions 获取数据），渲染完成后将 pinia.state.value（所有 store 的 state 序列）序列化到 HTML 的 window.__PINIA_STATE__。客户端：创建 Pinia 实例，在 mount 前将 window.__PINIA_STATE__ 赋值给 pinia.state.value（注水），这样客户端激活时 store 已有数据，不需要重新请求。Nuxt 3 内置处理 Pinia SSR（useState/useAsyncData）。
>
> **用法要点**：① SSR 中每次请求创建新的 Pinia 实例（不要共享，避免用户数据污染）；② 服务端渲染后序列化 pinia.state.value 到 HTML；③ 客户端激活前注水（pinia.state.value = window.__PINIA_STATE__）；④ 用 Nuxt 3 时自动处理（不需要手动配置）；⑤ 数据预取：onServerPrefetch 中调用 actions（服务端执行）；⑥ 注意：localStorage 在服务端不可用（持久化插件要判断环境）；⑦ 注意：store 单例在 SSR 中是每次请求一个实例（不是全局单例）。

### 3.6 与 Vue Router 配合（路由守卫）

```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  { path: '/login', component: Login },
  { 
    path: '/admin', 
    component: Admin,
    meta: { requiresAuth: true, roles: ['admin'] }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()  // 在守卫内调用
  
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.roles && !to.meta.roles.some(r => userStore.roles.includes(r))) {
    next('/403')
  } else {
    next()
  }
})

export default router
```

> 🔍 **知识点深度解析**
>
> **作用**：路由守卫中用 Pinia 做权限控制（登录校验、角色校验）。to.meta 配置路由权限要求，守卫中检查 userStore 的登录态和角色。
>
> **原理**：router.beforeEach 全局前置守卫，每次路由切换时执行。在守卫函数内调用 useUserStore()（Pinia 已安装，可获取 store 实例）。to.meta.requiresAuth 判断是否需要登录，userStore.isLoggedIn 判断是否已登录。to.meta.roles 判断需要的角色，userStore.roles 判断用户角色。不满足则跳转登录页或403。注意：useStore() 必须在守卫函数内调用（不能在模块顶层调用，此时 Pinia 可能未安装）。
>
> **用法要点**：① 路由 meta 配置权限：requiresAuth（需要登录）、roles（需要的角色）；② 守卫中 useUserStore()（在函数内调用，不要在顶层）；③ 未登录跳转登录页（带 redirect 参数，登录后跳回）；④ 无权限跳转403页；⑤ 动态路由：根据用户角色 addRoute（权限菜单）；⑥ 登录后获取用户信息（fetchUserInfo）再判断权限；⑦ token 过期：401 响应时清除 token 跳转登录；⑧ 注意：路由守卫中调用异步 actions（如 fetchUserInfo）要 await（确保数据加载完再判断）。

### 3.7 测试 Pinia Store

```javascript
// stores/counter.test.js
import { setActivePinia, createPinia } from 'pinia'
import { useCounterStore } from './counter'
import { describe, it, expect, beforeEach } from 'vitest'

describe('Counter Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())  // 每个测试前创建新 Pinia
  })
  
  it('increments count', () => {
    const store = useCounterStore()
    expect(store.count).toBe(0)
    store.increment()
    expect(store.count).toBe(1)
  })
  
  it('doubleCount getter', () => {
    const store = useCounterStore()
    store.count = 5
    expect(store.doubleCount).toBe(10)
  })
})
```

> 🔍 **知识点深度解析**
>
> **作用**：测试 Pinia store 保证业务逻辑正确。用 Vitest/Jest + setActivePinia 创建独立的 Pinia 实例（测试隔离）。
>
> **原理**：setActivePinia(pinia) 设置当前活动的 Pinia 实例（useStore() 会从活动实例获取/创建 store）。每个测试前 createPinia() 创建新实例（测试隔离，不共享状态）。测试中直接调用 useStore()，修改 state，调用 actions，断言结果。getters 直接访问（computed 自动解包）。异步 actions 用 await。模拟 API：vi.mock('@/api/user') 模拟接口返回。Pinia 测试比 Vuex 简单（不需要 mutations，直接修改 state 或调用 actions）。
>
> **用法要点**：① 每个测试前 setActivePinia(createPinia())（隔离）；② 直接修改 state 或调用 actions 准备测试数据；③ 断言 state 和 getters 的值；④ 异步 actions 用 await；⑤ 模拟 API 依赖（vi.mock）；⑥ 测试 actions 的业务逻辑（如 addItem 后 items 变化）；⑦ 测试 getters 的计算结果；⑧ 注意：测试中 store 是独立实例（不会影响其他测试）。

### 3.8 从 Vuex 迁移到 Pinia

```javascript
// Vuex
const store = createStore({
  state: { count: 0 },
  mutations: {
    INCREMENT(state) { state.count++ }
  },
  actions: {
    increment({ commit }) { commit('INCREMENT') }
  },
  getters: {
    double: state => state.count * 2
  }
})

// Pinia（Setup Store）
export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const double = computed(() => count.value * 2)
  function increment() { count.value++ }  // 不需要 mutation
  return { count, double, increment }
})
```

> 🔍 **知识点深度解析**
>
> **作用**：从 Vuex 迁移到 Pinia 是 Vue3 项目的标准升级。核心变化：移除 mutations（直接修改或 actions）、模块化简化（每个 store 独立）、TypeScript 支持更好。
>
> **原理**：Vuex 的 state → Pinia state（ref/reactive）。Vuex 的 mutations → 移除（直接修改 state 或在 actions 中修改）。Vuex 的 actions → Pinia actions（普通函数，async/await）。Vuex 的 getters → Pinia getters（computed）。Vuex 的 modules → 多个独立 store（useUserStore/useCartStore，不需要命名空间）。Vuex 的 mapState/mapGetters/mapActions → Pinia 的 storeToRefs + 直接解构。迁移可逐步进行（Vuex 和 Pinia 可共存）。
>
> **用法要点**：① 新项目直接用 Pinia（不要用 Vuex）；② 迁移：每个 Vuex module 转为一个 Pinia store；③ mutations 逻辑移到 actions（或直接修改 state）；④ mapState/mapGetters → storeToRefs 解构；⑤ mapActions → 直接解构 actions；⑥ 命名空间：Pinia 用 store id 区分（不需要 namespaced）；⑦ Vuex 和 Pinia 可共存（逐步迁移，不要求一次性）；⑧ 注意：Pinia 没有 mutations 概念，不要保留（直接修改 state 是允许的）。

---


---
## 4. 注意事项

1. **store 调用时机**：useXxxStore() 必须在 setup 中或之后调用（Pinia 安装后），不能在模块顶层直接调用。

2. **解构响应式**：解构 state/getters 用 storeToRefs（保持响应式），普通解构会丢失响应式。actions 可直接解构。

3. **Setup vs Options**：新项目用 Setup Store（Composition API 风格，更灵活，TS 更好）。Options Store 适合从 Vuex 迁移。

4. **直接修改 state**：Pinia 允许直接修改 state（不需要 mutations），但复杂业务逻辑建议封装到 actions。

5. **持久化数据**：敏感数据（密码）不要存 localStorage，用 cookie+HttpOnly。大数据不要持久化（localStorage 5MB 限制）。

6. **跨 store 调用**：在 action 中调用其他 store，避免循环依赖（A→B→A）。

7. **$reset**：Setup Store 的 $reset 需要 Pinia 2.x+ 或自定义插件实现（Options Store 自动支持）。

8. **TypeScript**：Pinia 原生支持 TS，Setup Store 类型自动推导。定义 state 时用 ref<T>() 指定类型。

9. **性能**：getter 有缓存（用 computed），不要用方法替代。大列表的 getter 注意性能（避免每次都遍历大数组）。

10. **SSR**：每次请求创建新 Pinia 实例，服务端序列化 state，客户端注水。localStorage 在服务端不可用。

11. **DevTools**：Pinia 支持 Vue DevTools（查看 state、getters、actions，时间旅行调试）。开发时安装 Vue DevTools。

12. **不要滥用**：组件局部状态用 ref/reactive，只有全局共享状态才放 Pinia。不要把所有数据都放 store。

---

> 💡 **深度讲解**：Pinia 是 Vue3 官方状态管理（替代 Vuex），核心是 state（响应式数据）、getters（计算属性，有缓存）、actions（业务方法，同步异步）。两种风格：Options Store（类似 Vuex）和 Setup Store（Composition API，推荐）。defineStore(id, setup) 创建 store，useXxxStore() 获取单例实例。组件中用 storeToRefs 解构 state/getters（保持响应式），actions 直接解构。state 可直接修改（不需要 mutations），批量用 $patch，重置用 $reset。getters 用 computed（有缓存），可带参数（返回函数）。actions 封装业务逻辑，可 async/await，可调用其他 store。持久化用 pinia-plugin-persistedstate（自动存 localStorage）。插件扩展 Pinia（$subscribe 监听 state，$onAction 监听 actions）。典型应用：用户认证（token+用户信息+登录登出）、购物车（商品列表+总价+增删改）、应用配置（主题+语言+侧边栏）。路由守卫中用 store 做权限控制。SSR 中需要状态注水。从 Vuex 迁移：mutations 移除，modules 转为独立 store。Pinia 比 Vuex 简单（API 少、无 mutations、TS 友好），新项目首选。注意：store 在 setup 后调用，解构用 storeToRefs，不要滥用（局部状态不用放 store）。
>
> **📝 精简总结**：Pinia=Vue3状态管理(替代Vuex)；核心=state(ref)+getters(computed缓存)+actions(函数async)；定义=defineStore(id, setup/options)；使用=useXxxStore()+storeToRefs解构；修改=直接赋值/$patch批量/$reset重置；持久化=pinia-plugin-persistedstate；扩展=插件/$subscribe/$onAction；典型=用户认证/购物车/应用配置；迁移=Vuex mutations移除/modules转独立store；注意=setup后调用/storeToRefs/不滥用局部状态。

---

> 📋 **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 知识点深度解析」模块（作用+原理+用法要点），原有内联图已统一风格化美化（圆角、阴影、渐变、动画）。所有原有内容完整保留，未做任何修改。
