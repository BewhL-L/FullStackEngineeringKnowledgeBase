---
title: Vue3 知识点系统梳理
tags: [前端, Vue3, CompositionAPI, 进阶]
created: 2026-08-12
updated: 2026-08-12
---

# Vue3 知识点系统梳理（优化版）

> **文档说明**：本文档参照《Java知识点完整整合大全》排版风格，系统梳理 Vue3 技术栈。包含概述、核心特性、常用用法、注意事项四大模块，辅以动态可视化解析图、深度讲解与精简总结。**优化版**在原有内容基础上，为每个知识点补充了作用、原理、用法的深度解析，并新增了知识点图解。

---

## 1. 概述

Vue.js 是一套用于构建用户界面的**渐进式 JavaScript 框架**，由尤雨溪（Evan You）创建。Vue3 于 2020 年 9 月正式发布，是 Vue 的重大版本升级，采用 TypeScript 重写，引入 Composition API、Proxy 响应式、Fragment、Teleport、Suspense 等新特性，性能和开发体验全面提升。

**核心定位**：
- 渐进式：可从简单页面逐步扩展到完整 SPA
- 组件化：可复用、可组合的组件体系
- 响应式：数据驱动视图，声明式编程
- 生态丰富：Vue Router、Pinia、Vite、Element Plus 等

**Vue2 vs Vue3 核心差异**：

| 对比项 | Vue2 | Vue3 |
|--------|------|------|
| 响应式原理 | Object.defineProperty | Proxy（代理整个对象） |
| API 风格 | Options API 为主 | Composition API（推荐）+ Options API |
| 源码语言 | JavaScript | TypeScript |
| 组件根节点 | 只能有一个根节点 | 支持 Fragment（多根节点） |
| 生命周期 | beforeDestroy/destroyed | beforeUnmount/unmounted |
| 打包体积 | 较大 | Tree-shaking 优化，更小 |
| 自定义指令 | bind/inserted... | created/beforeMount/mounted... |
| 过滤器 | 支持 filters | 移除，用方法/计算属性替代 |

---


---
## 2. 核心特性

<div style="background:linear-gradient(135deg,#4facfe,#00f2fe);border-radius:16px;padding:24px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#fff;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes vueReactive{0%,100%{transform:scale(1);opacity:.85}50%{transform:scale(1.03);opacity:1}}.vue-box{display:inline-block;width:28%;vertical-align:top;margin:0 2%;background:rgba(255,255,255,.18);border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.08);padding:12px;font-size:11px;text-align:center;animation:vueReactive 3s ease-in-out infinite}.vue-box:nth-child(2){animation-delay:.5s}.vue-box:nth-child(3){animation-delay:1s}.vue-icon{font-size:22px;margin-bottom:6px}.vue-name{font-weight:700;font-size:13px;margin-bottom:4px}.vue-arrow{display:inline-block;font-size:18px;vertical-align:middle;animation:vueReactive 1.5s ease-in-out infinite}</style>
<div style="text-align:center;font-size:16px;font-weight:700;margin-bottom:16px;padding-bottom:12px;border-bottom:1.5px solid rgba(255,255,255,.22);letter-spacing:1px;text-shadow:0 1px 3px rgba(0,0,0,.12)">Vue3 响应式数据流</div>
<div style="text-align:center">
<div class="vue-box"><div class="vue-icon">📝</div><div class="vue-name">数据变更</div><div style="font-size:10px;opacity:.85">ref/reactive<br>修改响应式数据</div></div>
<span class="vue-arrow">→</span>
<div class="vue-box"><div class="vue-icon">⚡</div><div class="vue-name">Proxy 拦截</div><div style="font-size:10px;opacity:.85">get/set 拦截<br>触发依赖收集/更新</div></div>
<span class="vue-arrow">→</span>
<div class="vue-box"><div class="vue-icon">🖼️</div><div class="vue-name">视图更新</div><div style="font-size:10px;opacity:.85">虚拟DOM Diff<br>高效更新真实DOM</div></div>
</div>
</div>

### 2.1 响应式原理（Proxy）

**Vue2**：`Object.defineProperty` 劫持属性的 getter/setter，无法监听新增/删除属性、数组索引变化（需要 $set）。

**Vue3**：`Proxy` 代理整个对象，可拦截 get/set/deleteProperty/has/ownKeys 等13种操作，天然支持新增属性、数组变化。

**核心 API**：
- `ref`：基本类型响应式（也可对象，内部转 reactive），通过 `.value` 访问
- `reactive`：对象类型响应式，直接访问属性
- `readonly`：只读代理
- `shallowRef`/`shallowReactive`：浅响应式（只第一层）
- `toRef`/`toRefs`：将 reactive 属性转为 ref（解构不丢失响应式）

> 🔍 **知识点深度解析**
>
> **作用**：响应式是 Vue 的核心，数据变更自动更新视图。Vue3 用 Proxy 替代 Object.defineProperty，解决了 Vue2 的局限性（新增属性、数组索引、性能）。
>
> **原理**：reactive(obj) 返回一个 Proxy，拦截 get（收集依赖 track）、set（触发更新 trigger）、deleteProperty 等操作。ref(value) 内部创建一个有 value 属性的对象（RefImpl），通过类的 getter/setter 拦截 .value 访问。依赖收集：组件渲染时，访问响应式数据触发 get，将当前副作用函数（组件更新函数 effect）收集到该属性的依赖集合（Set）中。数据变更触发 set，遍历依赖集合调用所有 effect（重新渲染组件）。Vue3 用 effect + track + trigger 实现，比 Vue2 的 Watcher 更轻量。数组：Proxy 直接拦截数组索引和 length 变化，不需要 Vue2 的数组方法重写。
>
> **用法要点**：① 基本类型用 ref（.value 访问），对象用 reactive（直接访问）；② 解构 reactive 会丢失响应式，用 toRefs 解构；③ ref 在模板中自动解包（不需要 .value）；④ reactive 不能替换整个对象（赋值新对象丢失代理），用 Object.assign 或 ref；⑤ 浅响应式（shallowRef/shallowReactive）用于大对象优化（只监听第一层）；⑥ 不需要响应式的数据用普通对象（减少开销）；⑦ 面试常考：Proxy vs Object.defineProperty 区别、ref 和 reactive 区别、依赖收集原理。

### 2.2 Composition API

**Options API（Vue2 风格）**：data/methods/computed/watch 分散在不同选项，逻辑复用靠 mixins（命名冲突、来源不清）。

**Composition API（Vue3 推荐）**：`setup()` 函数中组织逻辑，可抽离为可复用的组合函数（composables），逻辑内聚、类型友好。

**核心 API**：
- `setup()`：组件创建前执行，返回数据和方法供模板使用
- `<script setup>`：语法糖，自动暴露顶层变量，更简洁（推荐）
- `computed`：计算属性（有缓存）
- `watch`：侦听器（监听数据变化执行副作用）
- `watchEffect`：自动收集依赖，立即执行

> 🔍 **知识点深度解析**
>
> **作用**：Composition API 是 Vue3 的核心升级，解决了 Options API 在复杂组件中逻辑分散、复用困难的问题。逻辑按功能组织（而非按选项类型），可抽离为 composables 复用，TypeScript 类型推导更好。
>
> **原理**：setup() 在 beforeCreate 和 created 之间执行（组件实例已创建但数据未初始化），没有 this。返回的对象暴露给模板（变量、方法、computed）。<script setup> 是编译时语法糖，编译器自动将顶层变量/导入暴露给模板，不需要 return。组合函数（useXxx）：将相关逻辑封装为函数，内部用 ref/computed/watch，返回响应式数据和方法，在 setup 中调用。如 useMouse() 返回 x,y，useFetch(url) 返回 data,loading,error。逻辑复用比 mixins 好：来源清晰（从哪个函数来）、无命名冲突、可传参、类型安全。
>
> **用法要点**：① 新项目用 <script setup>（最简洁，官方推荐）；② 逻辑复用用组合函数（useXxx），不要用 mixins（Vue3 不推荐）；③ 组合函数放在 composables/ 目录，命名 use 开头；④ computed 有缓存（依赖不变不重新计算），方法每次调用都执行；⑤ watch 监听特定数据（可配置 immediate/deep），watchEffect 自动收集依赖（立即执行）；⑥ setup 中没有 this，用 getCurrentInstance() 获取实例（不推荐常用）；⑦ 生命周期在 setup 中用 onMounted/onUnmounted 等（加 on 前缀）。

### 2.3 虚拟 DOM 与 Diff 算法

**虚拟 DOM**：用 JS 对象描述真实 DOM，数据变更时生成新 VNode，与旧 VNode Diff 比较，最小化更新真实 DOM。

**Vue3 Diff 优化**：
- 静态提升（hoistStatic）：静态节点提升到 render 外，不参与 Diff
- 补丁标记（patchFlag）：动态节点标记类型（TEXT/CLASS/PROPS），Diff 时只比较标记部分
- 缓存事件处理函数（cacheHandlers）：事件函数缓存，避免每次渲染新建
- 最长递增子序列：移动节点时用最长递增子序列减少 DOM 操作

> 🔍 **知识点深度解析**
>
> **作用**：虚拟 DOM 是 Vue 性能的核心，通过 JS 对象描述 DOM，Diff 算法计算最小变更，减少真实 DOM 操作（真实 DOM 操作很慢）。Vue3 的编译时优化比 Vue2 更快。
>
> **原理**：编译器将模板编译为 render 函数，render 函数返回 VNode（虚拟节点，描述标签、属性、子节点）。数据变更时重新执行 render 生成新 VNode，patch(oldVNode, newVNode) 比较：同类型则递归比较子节点和属性，不同类型则替换。Vue3 编译优化：静态提升（不变化的节点提到 render 函数外，每次渲染复用，不参与 Diff）；patchFlag（动态节点标记哪些部分是动态的，如 TEXT 只比较文本，Diff 时跳过静态部分）；cacheHandlers（事件函数缓存，避免每次渲染创建新函数导致子组件不必要更新）。列表 Diff：双端比较（头头、尾尾、头尾、尾头）+ 最长递增子序列（需要移动的节点中，找出不需要移动的最长序列，其他节点移动），比 Vue2 的双端比较更少 DOM 操作。
>
> **用法要点**：① 列表渲染必须加 key（唯一稳定标识，不要用 index），帮助 Diff 正确识别节点；② 大列表用 v-memo（缓存子树，依赖不变时跳过 Diff）；③ 静态节点会自动提升，不需要手动优化；④ 不要用随机数/时间戳作为 key（每次都变，导致全量重建）；⑤ 组件上的 key 变化会强制重新创建组件（用于重置状态）；⑥ v-if 和 v-for 不要同时用在同一元素（v-if 优先级高，访问不到 v-for 变量）；⑦ 理解虚拟 DOM 原理有助于排查性能问题（不必要的重新渲染）。

### 2.4 组件通信

**父子通信**：
- 父→子：props（单向数据流）
- 子→父：emit 事件
- 父访问子：ref + defineExpose

**跨层级通信**：
- provide/inject：祖先→后代（依赖注入）
- Pinia：全局状态管理（推荐）
- eventBus：Vue3 移除了 $on，用 mitt 等第三方库

**v-model**：组件上的 v-model 是 props（modelValue）+ emit（update:modelValue）的语法糖。

> 🔍 **知识点深度解析**
>
> **作用**：组件通信是 Vue 开发的基础，不同场景选不同方式。props/emit 是父子通信标准，provide/inject 跨层级，Pinia 全局状态。
>
> **原理**：props：父组件传递数据给子组件，子组件用 defineProps 声明，单向数据流（子不能直接修改 props，要 emit 事件让父修改）。emit：子组件用 defineEmits 声明事件，调用 emit('eventName', data) 触发父组件的 @eventName 处理函数。v-model：默认对应 props modelValue + emit update:modelValue，可自定义 v-model:title（props title + emit update:title）。provide/inject：祖先组件 provide('key', value)，后代组件 inject('key')，实现跨层级传递（类似 React Context），可传响应式数据（ref/reactive）。ref：父组件给子组件加 ref，通过 ref.value 访问子组件实例，子组件用 defineExpose 暴露方法/数据（<script setup> 默认不暴露）。
>
> **用法要点**：① 父子用 props（父→子）+ emit（子→父），标准方式；② props 是只读的，子组件不要修改（要修改 emit 事件）；③ 跨层级用 provide/inject（不要用 props 层层传递）；④ 全局状态用 Pinia（比 Vuex 简单，推荐）；⑤ 兄弟组件通信：通过父组件中转或 Pinia；⑥ v-model 可自定义多个（v-model:title v-model:content）；⑦ 父访问子用 ref + defineExpose（不要依赖子组件内部实现，只暴露必要接口）。

### 2.5 生命周期

**Vue3 生命周期（setup 中用 onXxx）**：

| 选项式 API | setup 中 | 调用时机 |
|-----------|---------|---------|
| beforeCreate | - | 实例创建前（setup 本身就是此时） |
| created | - | 实例创建后（setup 本身就是此时） |
| beforeMount | onBeforeMount | 挂载前 |
| mounted | onMounted | 挂载后（DOM 可用） |
| beforeUpdate | onBeforeUpdate | 更新前 |
| updated | onUpdated | 更新后 |
| beforeUnmount | onBeforeUnmount | 卸载前（清理定时器/事件） |
| unmounted | onUnmounted | 卸载后 |

**注意**：setup 中没有 beforeCreate 和 created（setup 本身就在这两个阶段之间执行）。

> 🔍 **知识点深度解析**
>
> **作用**：生命周期钩子让开发者在组件不同阶段执行逻辑（如 mounted 中请求数据、onUnmounted 中清理资源）。理解生命周期是排查问题的基础。
>
> **原理**：Vue 组件创建流程：创建实例→初始化 props/slots→执行 setup→编译模板→挂载（创建 VNode→patch 到真实 DOM）→mounted。数据变更→beforeUpdate→重新渲染 Diff→updated。组件卸载→beforeUnmount→移除 DOM/清理 effect→unmounted。setup 在 beforeCreate 和 created 之间执行，所以 setup 中没有 this，也不需要 beforeCreate/created 钩子（初始化逻辑直接写在 setup 中）。onMounted 等钩子在 setup 中调用，内部将回调注册到当前组件实例，对应阶段时执行。onUnmounted 用于清理：清除定时器、移除事件监听、取消请求、关闭 WebSocket（防止内存泄漏）。
>
> **用法要点**：① 数据请求在 onMounted 中（SSR 中用 onServerPrefetch）；② 清理资源在 onBeforeUnmount 或 onUnmounted（定时器、事件监听、订阅）；③ onMounted 中 DOM 已挂载（可访问 ref DOM）；④ updated 中不要修改响应式数据（可能导致无限循环）；⑤ 父子生命周期顺序：挂载 父beforeMount→子beforeMount→子mounted→父mounted；卸载 父beforeUnmount→子beforeUnmount→子unmounted→父unmounted；⑥ keep-alive 组件用 onActivated/onDeactivated（不是 mounted/unmounted）；⑦ setup 中生命周期钩子加 on 前缀（onMounted 不是 mounted）。

### 2.6 内置组件：Fragment、Teleport、Suspense

**Fragment**：组件支持多个根节点（Vue2 只能一个根），模板中不需要包裹 div。

**Teleport**：将组件内容渲染到 DOM 树的其他位置（如 body），适合模态框、弹窗（避免父组件 overflow:hidden 影响）。

**Suspense**：异步组件加载时显示 fallback 内容，支持 async setup（组件 setup 返回 Promise）。

```vue
<Teleport to="body">
  <Modal v-if="show">弹窗内容</Modal>
</Teleport>

<Suspense>
  <template #default>
    <AsyncComponent />
  </template>
  <template #fallback>
    <Loading />
  </template>
</Suspense>
```

> 🔍 **知识点深度解析**
>
> **作用**：Fragment 简化模板（不需要多余根 div），Teleport 解决弹窗层级问题，Suspense 优雅处理异步加载。三者提升开发体验。
>
> **原理**：Fragment：Vue3 的 VNode 支持 Fragment 类型（多子节点），编译器自动将多根节点模板包裹为 Fragment，渲染时渲染所有子节点（不创建额外 DOM 元素）。Teleport：to 属性指定目标选择器（如 body），渲染时将子节点移动到目标 DOM 元素下，但组件的逻辑/数据/事件仍在原组件上下文中（不影响父子通信）。适合 Modal/Drawer/Toast（避免被父组件 overflow:hidden 或 z-index 截断）。Suspense：异步组件（defineAsyncComponent 或 async setup）加载时，Suspense 显示 fallback 内容，加载完成后显示默认内容。内部跟踪异步组件的 Promise 状态，resolve 后切换。支持嵌套 Suspense。
>
> **用法要点**：① Fragment 直接写多根节点（不需要 template 包裹），但要注意 v-for 的 key；② Teleport 用于 Modal/Toast（to="body"），避免层级问题；③ Teleport 的目标元素必须存在（body 一定存在，自定义元素要确保已渲染）；④ Suspense 配合 defineAsyncComponent 懒加载组件；⑤ async setup 中可以 await（组件返回 Promise），但要注意错误处理；⑥ Suspense 目前是实验性（Vue 3.3+ 稳定），生产可用但注意边界情况；⑦ 多个 Teleport 可以到同一目标（按顺序追加）。

### 2.7 自定义指令与插件

**自定义指令**：v-focus、v-permission 等，在元素的特定生命周期执行逻辑。

Vue3 指令钩子：created、beforeMount、mounted、beforeUpdate、updated、beforeUnmount、unmounted。

**插件**：通过 app.use() 安装，可注册全局组件、指令、原型方法、provide 全局数据。

```javascript
// 自定义指令
const vFocus = {
  mounted(el) {
    el.focus();
  }
}

// 插件
const myPlugin = {
  install(app, options) {
    app.component('MyButton', MyButton);
    app.directive('focus', vFocus);
    app.provide('config', options);
  }
}
app.use(myPlugin, { option1: 'value' });
```

> 🔍 **知识点深度解析**
>
> **作用**：自定义指令封装 DOM 操作逻辑（如自动聚焦、权限控制、防抖），插件封装全局功能（组件库、路由、状态管理）。两者是 Vue 扩展机制。
>
> **原理**：自定义指令：在元素的生命周期钩子中执行逻辑。mounted 时元素已插入 DOM（可操作 DOM），updated 时组件更新后调用（可比较 binding.value 变化）。指令钩子接收 el（元素）、binding（指令信息：value/oldValue/arg/modifiers）、vnode。插件：install(app, options) 方法接收 app 实例和选项，可调用 app.component/directive/provide/config.globalProperties 注册全局功能。app.use(plugin, options) 调用 install（同一个插件只安装一次）。Vue Router、Pinia、Element Plus 都是插件。
>
> **用法要点**：① 自定义指令用于纯 DOM 操作（如 v-focus 自动聚焦），逻辑复杂用组件；② 指令钩子：mounted 初始化，updated 响应值变化，unmounted 清理；③ 指令值变化时在 updated 中处理（比较 binding.value 和 binding.oldValue）；④ 插件 install 中注册全局组件/指令/provide；⑤ 全局方法用 app.config.globalProperties（Vue2 的 Vue.prototype 替代），但推荐用 provide/inject 或 composables；⑥ 插件要写类型声明（TypeScript 中扩展 ComponentCustomProperties）；⑦ 不要滥用全局注册（增加打包体积，用按需引入更好）。

---


---
## 3. 常用用法

### 3.1 响应式 API 使用

```vue
<script setup>
import { ref, reactive, computed, watch, watchEffect, toRefs } from 'vue'

// ref：基本类型
const count = ref(0)
const increment = () => count.value++

// reactive：对象
const user = reactive({ name: '张三', age: 18 })
// 解构用 toRefs 保持响应式
const { name, age } = toRefs(user)

// computed：计算属性（有缓存）
const doubleCount = computed(() => count.value * 2)
const fullName = computed({
  get: () => `${user.firstName} ${user.lastName}`,
  set: (val) => { [user.firstName, user.lastName] = val.split(' ') }
})

// watch：监听特定数据
watch(count, (newVal, oldVal) => {
  console.log(`count: ${oldVal} → ${newVal}`)
}, { immediate: true, deep: true })

// watchEffect：自动收集依赖
watchEffect(() => {
  console.log(`count is ${count.value}, name is ${user.name}`)
})
</script>
```

> 🔍 **知识点深度解析**
>
> **作用**：ref/reactive 创建响应式数据，computed 派生状态，watch/watchEffect 监听变化执行副作用。掌握这些是 Composition API 的基础。
>
> **原理**：ref 内部创建 RefImpl 实例，get value() 时 track 收集依赖，set value() 时 trigger 触发更新。reactive 返回 Proxy，get 拦截 track，set 拦截 trigger。computed 内部创建 ComputedRefImpl，有 dirty 标记（依赖变更时 dirty=true），第一次访问时计算并缓存，依赖不变则直接返回缓存（不重新计算）。watch 内部创建 effect，监听指定数据源（ref/reactive/函数），变化时执行回调。watchEffect 创建 effect，立即执行回调，执行过程中访问的响应式数据自动收集为依赖，依赖变化时重新执行回调。
>
> **用法要点**：① 基本类型用 ref，对象/数组用 reactive（也可用 ref，内部转 reactive）；② computed 有缓存，适合派生状态（不要在 computed 中写副作用）；③ watch 适合需要旧值或条件执行的场景，watchEffect 适合自动收集依赖立即执行；④ watch 监听 reactive 对象默认 deep=true（深度监听），监听 ref 对象需手动 deep:true；⑤ 停止监听：watch/watchEffect 返回停止函数，调用则停止（组件卸载自动停止）；⑥ toRefs 解构 reactive（保持响应式），toRef 转单个属性；⑦ 不要在 watch 回调中修改监听的数据源（可能无限循环，除非有条件）。

### 3.2 组件定义与 Props/Emit

```vue
<!-- 子组件 Child.vue -->
<script setup>
// 定义 props
const props = defineProps({
  title: {
    type: String,
    required: true,
    default: '默认标题'
  },
  count: {
    type: Number,
    default: 0
  }
})

// 定义 emit
const emit = defineEmits(['update', 'delete'])

const handleClick = () => {
  emit('update', props.count + 1)
}

// 暴露给父组件
defineExpose({
  reset: () => { /* 重置逻辑 */ }
})
</script>

<!-- 父组件 -->
<Child 
  :title="title" 
  :count="count" 
  @update="count = $event"
  @delete="handleDelete"
/>
```

> 🔍 **知识点深度解析**
>
> **作用**：defineProps/defineEmits/defineExpose 是 <script setup> 中的组件通信 API，替代 Vue2 的 props/emits 选项。类型安全，简洁。
>
> **原理**：defineProps 是编译器宏（编译时处理，不需要导入），声明组件的 props，返回 props 对象（响应式，父组件传值变化时更新）。defineEmits 声明组件可触发的事件，返回 emit 函数，调用 emit('event', payload) 触发父组件的事件监听。defineExpose 暴露组件的方法/属性给父组件（<script setup> 默认封闭，父组件通过 ref 访问不到，必须用 defineExpose 暴露）。TypeScript 中可用类型声明：defineProps<{title: string; count?: number}>()，更类型安全。
>
> **用法要点**：① defineProps/defineEmits/defineExpose 是编译器宏，不需要 import；② props 是只读的，子组件不要修改（要修改 emit 事件）；③ emit 事件名用 kebab-case（模板中 @update-count）或 camelCase（@updateCount），Vue 自动转换；④ 父组件用 ref 访问子组件暴露的方法（childRef.value.reset()）；⑤ TypeScript 推荐用类型声明 props（defineProps<Props>()），配合 withDefaults 设置默认值；⑥ props 校验：type/required/default/validator；⑦ 不要把 props 直接赋值给 ref（会丢失响应式，用 computed 或 toRef）。

### 3.3 路由（Vue Router 4）

```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'), // 懒加载
    meta: { title: '首页', requiresAuth: true }
  },
  {
    path: '/user/:id',
    name: 'User',
    component: () => import('@/views/User.vue'),
    props: true // 路由参数作为 props
  }
]

const router = createRouter({
  history: createWebHistory(), // HTML5 History 模式
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isLoggedIn()) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

```vue
<!-- 组件中使用 -->
<script setup>
import { useRoute, useRouter } from 'vue-router'
const route = useRoute()  // 当前路由信息（params/query/meta）
const router = useRouter() // 路由实例（push/replace/back）

const goUser = (id) => router.push({ name: 'User', params: { id } })
</script>
```

> 🔍 **知识点深度解析**
>
> **作用**：Vue Router 是 Vue 官方路由，实现 SPA 页面切换。Vue Router 4 适配 Vue3，用 createRouter/createWebHistory 替代 Vue2 的 new VueRouter。
>
> **原理**：路由模式：createWebHistory（HTML5 History API，URL 无 #，需要服务端配置 fallback）、createWebHashHistory（hash 模式，URL 带 #，不需要服务端配置）。路由匹配：路径匹配规则（静态/参数:id/通配*），匹配到对应组件渲染到 <router-view>。导航守卫：beforeEach（全局前置，鉴权）、beforeResolve（全局解析）、afterEach（全局后置，埋点）、beforeEnter（路由独享）、beforeRouteEnter/Update/Leave（组件内）。懒加载：component: () => import()，Webpack/Vite 自动代码分割，按需加载。<router-link> 渲染为 a 标签，点击触发路由切换（不刷新页面）。
>
> **用法要点**：① 用 createWebHistory（URL 美观），服务端配置 fallback 到 index.html；② 路由组件懒加载（() => import()），减少首屏体积；③ 鉴权用 beforeEach 全局守卫（检查 token/权限）；④ 路由参数用 props: true 传入组件（解耦，组件不需要用 useRoute）；⑤ 动态路由 addRoute（权限控制：根据用户角色动态添加路由）；⑥ 路由元信息 meta（title/requiresAuth/roles）；⑦ 导航重复报错（NavigationDuplicated）用 catch 或 router.push().catch(()=>{})；⑧ keep-alive 缓存路由组件（<router-view v-slot="{Component}"><keep-alive><component :is="Component"/></keep-alive></router-view>）。

### 3.4 状态管理（Pinia）

```javascript
// stores/user.js
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null,
    token: localStorage.getItem('token') || ''
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    userName: (state) => state.userInfo?.name || '游客'
  },
  actions: {
    async login(credentials) {
      const res = await api.login(credentials)
      this.token = res.token
      this.userInfo = res.user
      localStorage.setItem('token', res.token)
    },
    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
    }
  }
})
```

```vue
<!-- 组件中使用 -->
<script setup>
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

const userStore = useUserStore()
// 解构保持响应式（用 storeToRefs）
const { isLoggedIn, userName } = storeToRefs(userStore)
// 方法直接解构
const { login, logout } = userStore
</script>
```

> 🔍 **知识点深度解析**
>
> **作用**：Pinia 是 Vue3 官方推荐的状态管理（替代 Vuex），更简洁、TypeScript 友好、支持 Composition API。核心概念：state/getters/actions。
>
> **原理**：defineStore(id, options) 创建 store，返回 useXxxStore 函数。第一次调用 useXxxStore 时创建 store 实例（单例，全局唯一），后续调用返回同一实例。state 是响应式数据（内部用 reactive），getters 是计算属性（有缓存），actions 是方法（可同步/异步，修改 state 直接 this.xxx = yyy，不需要 mutation）。Pinia 没有 mutations（Vuex 的 mutation 被移除，actions 可直接修改 state）。storeToRefs 解构 state/getters 保持响应式（类似 toRefs），actions 可直接解构（不是响应式的）。
>
> **用法要点**：① 新项目用 Pinia（不要用 Vuex，Vue3 官方推荐）；② store 命名 useXxxStore，放在 stores/ 目录；③ state 用函数返回（避免多个实例共享引用，虽然 store 是单例但是规范）；④ getters 有缓存（类似 computed），不要写副作用；⑤ actions 可直接修改 state（不需要 commit mutation），异步操作写在 actions；⑥ 解构 state 用 storeToRefs（保持响应式），方法直接解构；⑦ 持久化用 pinia-plugin-persistedstate（自动存 localStorage）；⑧ 模块化：按功能分 store（user/cart/order），不要一个大 store。

### 3.5 组合函数（Composables）

```javascript
// composables/useFetch.js
import { ref, watchEffect } from 'vue'

export function useFetch(url) {
  const data = ref(null)
  const error = ref(null)
  const loading = ref(false)
  
  const fetchData = async () => {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(url)
      data.value = await res.json()
    } catch (e) {
      error.value = e
    } finally {
      loading.value = false
    }
  }
  
  // url 变化时重新请求
  watchEffect(() => {
    if (url) fetchData()
  })
  
  return { data, error, loading, refetch: fetchData }
}

// 组件中使用
<script setup>
import { useFetch } from '@/composables/useFetch'
const { data, loading, error, refetch } = useFetch('/api/user')
</script>
```

> 🔍 **知识点深度解析**
>
> **作用**：组合函数（Composables）是 Vue3 逻辑复用的标准方式，替代 Vue2 的 mixins。将相关逻辑封装为函数，返回响应式数据和方法，可在多个组件中复用。
>
> **原理**：组合函数就是一个普通函数（约定 use 开头），内部用 ref/reactive/computed/watch 管理状态，返回响应式数据和方法。在 setup 中调用时，函数内部的响应式数据绑定到当前组件的作用域（组件卸载时自动清理 effect）。与 mixins 对比：mixins 数据来源不清、命名冲突、不能传参；composables 来源清晰（从哪个函数返回）、无命名冲突（可重命名）、可传参、类型安全。可组合多个 composables（如 useUser + usePermission）。
>
> **用法要点**：① 逻辑复用用 composables（useXxx），不要用 mixins；② 放在 composables/ 目录，文件名 useXxx.js；③ 返回响应式数据（ref/reactive）和方法；④ 组件中调用后解构使用；⑤ 可传参（如 useFetch(url)），参数变化时用 watch 重新执行；⑥ 清理资源（定时器/事件监听）在 composable 内部用 onUnmounted；⑦ 常用 composables：useMouse、useFetch、useDebounce、useLocalStorage、usePermission；⑧ VueUse 库提供大量常用 composables（推荐使用）。

### 3.6 性能优化

```vue
<!-- 1. v-memo：缓存子树，依赖不变时跳过 Diff -->
<div v-memo="[item.id, item.name]">
  <!-- 复杂内容 -->
</div>

<!-- 2. 懒加载组件 -->
<script setup>
import { defineAsyncComponent } from 'vue'
const HeavyComponent = defineAsyncComponent(() => import('./Heavy.vue'))
</script>

<!-- 3. keep-alive 缓存组件 -->
<keep-alive :include="['Home', 'List']">
  <component :is="currentComponent" />
</keep-alive>

<!-- 4. 非响应式大数据 -->
<script setup>
import { markRaw, shallowRef } from 'vue'
// markRaw：标记为非响应式（不被 reactive 代理）
const bigData = markRaw(hugeObject)
// shallowRef：只监听 .value 替换，不深度响应
const list = shallowRef([])
</script>
```

> 🔍 **知识点深度解析**
>
> **作用**：Vue3 性能优化包括减少不必要的渲染、懒加载、缓存组件、减少响应式开销。合理优化提升大列表/复杂页面的流畅度。
>
> **原理**：v-memo：缓存组件/元素的 VNode 子树，依赖数组（[item.id]）不变时直接复用旧 VNode，跳过 Diff（大列表性能提升明显）。defineAsyncComponent：异步加载组件（代码分割），首屏不加载，需要时才加载（配合 Suspense 显示 loading）。keep-alive：缓存组件实例（不卸载），切换时保留状态（表单输入、滚动位置），include/exclude 指定缓存哪些组件，max 限制缓存数量（LRU 淘汰）。markRaw：标记对象为非响应式（reactive 不代理它），减少大对象的响应式开销（不需要响应的数据用）。shallowRef/shallowReactive：浅响应式（只第一层响应式，深层不代理），大列表/大对象优化。
>
> **用法要点**：① 大列表用 v-memo（依赖不变时跳过 Diff，性能提升明显）；② 重型组件/路由懒加载（defineAsyncComponent / 路由懒加载），减少首屏体积；③ 表单/列表页用 keep-alive 缓存（返回时保留状态），注意 max 限制；④ 不需要响应式的大数据用 markRaw（如从接口获取的静态配置）；⑤ 大列表用 shallowRef（只监听整个数组替换，不监听每个元素）；⑥ 虚拟滚动：超大数据量（1000+）用虚拟滚动组件（vue-virtual-scroller），只渲染可视区域；⑦ 事件函数用 cacheHandlers（Vue3 自动优化），不需要手动 useMemo；⑧ 避免在模板中调用复杂方法（每次渲染都执行），用 computed 缓存。

### 3.7 TypeScript 支持

```vue
<script setup lang="ts">
import { ref, reactive, computed } from 'vue'

// 类型化 ref
const count = ref<number>(0)
const user = ref<User | null>(null)

// 类型化 reactive
interface User {
  id: number
  name: string
  age: number
}
const state = reactive<User>({ id: 1, name: '张三', age: 18 })

// 类型化 props（推荐）
interface Props {
  title: string
  count?: number
}
const props = withDefaults(defineProps<Props>(), {
  count: 0
})

// 类型化 emit
interface Emits {
  (e: 'update', value: number): void
  (e: 'delete', id: number): void
}
const emit = defineEmits<Emits>()

// 类型化 ref（DOM/组件）
const inputRef = ref<HTMLInputElement | null>(null)
const childRef = ref<InstanceType<typeof ChildComponent> | null>(null)
</script>
```

> 🔍 **知识点深度解析**
>
> **作用**：Vue3 用 TypeScript 重写，对 TS 支持比 Vue2 好很多。<script setup lang="ts"> 提供类型安全的 props/emit/ref，减少运行时错误。
>
> **原理**：defineProps<Props>() 用泛型声明 props 类型，编译器生成运行时校验（type 从 TS 类型推导）。withDefaults 给可选 props 设置默认值。defineEmits<Emits>() 用调用签名类型声明 emit，调用 emit 时参数类型检查。ref<T>() 指定 ref 的 value 类型。ref<HTMLInputElement>() 类型化 DOM 引用，访问 .value 时有 input 元素的方法（focus/value）。ref<InstanceType<typeof Child>>() 类型化组件引用，可访问组件暴露的方法（defineExpose 的类型）。reactive<T>() 类型化响应式对象。
>
> **用法要点**：① 新项目用 TypeScript + <script setup lang="ts">；② props 用类型声明（defineProps<Props>()），配合 withDefaults 默认值；③ emit 用类型声明（defineEmits<Emits>()），调用时参数类型检查；④ DOM ref 用 ref<HTMLInputElement | null>(null)，访问时判空；⑤ 组件 ref 用 InstanceType<typeof Child>，可访问 defineExpose 的类型；⑥ 复杂类型定义在 types/ 目录，接口用 interface，联合类型用 type；⑦ 第三方库要装 @types/xxx（如 @types/lodash）；⑧ Volar（Vue 官方 TS 插件）提供模板内类型检查，推荐使用。

### 3.8 构建工具（Vite）

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'element-plus': ['element-plus']
        }
      }
    }
  }
})
```

> 🔍 **知识点深度解析**
>
> **作用**：Vite 是 Vue3 官方推荐的构建工具，开发服务器基于原生 ESM（秒级启动），构建基于 Rollup（快速打包）。替代 Webpack，开发体验大幅提升。
>
> **原理**：开发模式：Vite 用 esbuild 预构建依赖（node_modules 中的第三方包，CommonJS 转 ESM，缓存到 node_modules/.vite），源码用浏览器原生 ESM（浏览器请求时按需编译，不需要打包整个项目），启动极快（秒级），热更新（HMR）只更新变更的模块。生产构建：用 Rollup 打包（Tree-shaking、代码分割、压缩），输出静态文件。插件：@vitejs/plugin-vue 处理 .vue 文件（编译 SFC）。代理：开发时 proxy 转发 API 请求（解决跨域）。manualChunks：手动分包（将第三方库单独打包，利用浏览器缓存）。
>
> **用法要点**：① Vue3 项目用 Vite（不要用 Vue CLI，已进入维护模式）；② 路径别名 @ 指向 src（vite.config 配置 + tsconfig paths）；③ 开发代理：/api 转发到后端，changeOrigin: true 修改 Host；④ 生产构建：sourcemap 关闭（减小体积），manualChunks 分包（第三方库单独打包，缓存友好）；⑤ 环境变量：.env.development/.env.production，VITE_ 前缀暴露给客户端；⑥ 依赖预构建：vite --force 强制重新预构建（依赖变更后）；⑦ 大项目注意：Vite 开发时请求多（原生 ESM），但现代浏览器支持 HTTP/2 多路复用，性能没问题。

---


---
## 4. 注意事项

1. **ref 和 reactive 选择**：基本类型用 ref，对象用 reactive。ref 在模板中自动解包，JS 中用 .value。

2. **解构丢失响应式**：reactive 解构会丢失响应式，用 toRefs 或 toRef。Pinia 用 storeToRefs。

3. **v-if 和 v-for 优先级**：Vue3 中 v-if 比 v-for 优先级高（Vue2 相反），不要同时用在同一元素。

4. **列表 key**：必须用唯一稳定标识（如 id），不要用 index（列表排序/插入时 Diff 错误）。

5. **props 只读**：子组件不要直接修改 props，要 emit 事件让父组件修改（单向数据流）。

6. **清理副作用**：onUnmounted 中清除定时器、事件监听、取消请求，防止内存泄漏。

7. **避免不必要的响应式**：不需要响应式的大数据用 markRaw 或 shallowRef，减少性能开销。

8. **异步组件错误处理**：defineAsyncComponent 要配置 errorComponent 和 loadingComponent，提升用户体验。

9. **TypeScript 类型**：用 <script setup lang="ts">，props/emit 用类型声明，安装 Volar 插件。

10. **Vue2 迁移**：用 @vue/compat 兼容构建逐步迁移，注意移除的 API（filters、$on、$set 等）。

11. **全局状态**：用 Pinia（不要用 Vuex），按功能分模块，不要一个大 store。

12. **性能监控**：用 Vue DevTools 查看组件渲染次数，优化不必要的重新渲染（v-memo、computed、shallowRef）。

---

> 💡 **深度讲解**：Vue3 是 Vue 的重大升级，核心是 Composition API（逻辑组织和复用）、Proxy 响应式（解决 Vue2 局限性）、编译时优化（静态提升/patchFlag/最长递增子序列）。响应式原理：reactive 用 Proxy 拦截 get/set，ref 用类的 getter/setter，依赖收集通过 track/trigger 实现。Composition API 用 setup() 组织逻辑，组合函数（useXxx）替代 mixins 实现复用，<script setup> 是语法糖（最简洁）。组件通信：props（父→子）+ emit（子→父）+ provide/inject（跨层级）+ Pinia（全局）。性能优化：v-memo 缓存大列表、defineAsyncComponent 懒加载、keep-alive 缓存组件、markRaw/shallowRef 减少响应式开销。生态：Vue Router 4（createRouter）、Pinia（defineStore）、Vite（秒级启动）、Element Plus。TypeScript 支持完善，推荐 <script setup lang="ts">。Vue3 比 Vue2 性能更好（Tree-shaking 更小、Diff 更快）、开发体验更好（Composition API、TS 支持），新项目直接用 Vue3。
>
> **📝 精简总结**：Vue3=Composition API+Proxy响应式+编译优化；响应式=ref(.value)/reactive(Proxy)+computed(缓存)+watch/watchEffect；组件=defineProps/defineEmits/defineExpose+Fragment/Teleport/Suspense；通信=props+emit+provide/inject+Pinia；复用=composables(useXxx)替代mixins；路由=Vue Router4(createRouter)；状态=Pinia(defineStore)；构建=Vite(ESM开发+Rollup构建)；优化=v-memo+懒加载+keep-alive+markRaw/shallowRef；注意=ref.value/解构响应式/key/单向数据流/清理副作用。

---

> 📋 **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 知识点深度解析」模块（作用+原理+用法要点），原有内联图已统一风格化美化（圆角、阴影、渐变、动画）。所有原有内容完整保留，未做任何修改。
