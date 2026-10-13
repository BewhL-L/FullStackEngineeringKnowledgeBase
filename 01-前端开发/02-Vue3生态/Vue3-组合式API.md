---
title: Vue3-组合式API
tags: [Vue3, 组合式API, CompositionAPI, setup, ref, reactive, computed, watch]
category: 前端开发
created: 2026-08-12
updated: 2026-09-01
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: []
aliases: [Vue3-组合式API]
---

# 🎯 Vue3 组合式 API

> Composition API（组合式 API）是 Vue3 引入的全新 API 风格，通过 `setup` 函数将相关逻辑组织在一起，解决了选项式 API 在大型组件中逻辑分散、复用困难的问题，是 Vue3 的核心特性之一。

---

## 一、什么是组合式 API

### 核心概念
组合式 API 是 Vue3 提供的一套基于函数的 API，核心思想是：
1. **`setup` 函数**：组件的逻辑入口，在组件创建前执行
2. **响应式 API**：`ref`、`reactive`、`computed`、`watch` 等创建响应式数据
3. **生命周期钩子**：`onMounted`、`onUpdated`、`onUnmounted` 等
4. **逻辑组合**：将相关逻辑封装为可复用的组合式函数（Composables）

### 解决的问题
| 问题 | 选项式 API（Options API） | 组合式 API（Composition API） |
|------|--------------------------|-------------------------------|
| 逻辑组织 | 按选项分散（data/methods/computed），相关逻辑割裂 | 按功能组织，相关逻辑聚合在一起 |
| 逻辑复用 | mixins 容易冲突、来源不清晰 | 组合式函数，清晰可控 |
| TypeScript 支持 | 类型推断困难 | 天然类型友好 |
| 代码压缩 | 选项名不可压缩 | 函数和变量可压缩，产物体积更小 |
| 大型组件维护 | 逻辑分散，跳转频繁 | 逻辑内聚，易于理解 |

### 选项式 API vs 组合式 API

**选项式 API（Vue2/Vue3 兼容）**
```vue
<script>
export default {
  data() {
    return { count: 0, name: '' }
  },
  computed: {
    doubleCount() { return this.count * 2 }
  },
  methods: {
    increment() { this.count++ }
  },
  mounted() {
    console.log('mounted')
  }
}
</script>
```

**组合式 API（Vue3 推荐）**
```vue
<script setup>
import { ref, computed, onMounted } from 'vue'

const count = ref(0)
const name = ref('')
const doubleCount = computed(() => count.value * 2)

function increment() {
  count.value++
}

onMounted(() => {
  console.log('mounted')
})
</script>
```

---

## 二、setup 函数

### 基本用法
`setup` 是组合式 API 的入口函数，在组件创建之前、props 解析之后执行。

```vue
<script>
export default {
  props: {
    title: {
      type: String,
      required: true
    }
  },
  emits: ['change'],
  setup(props, context) {
    // props 是响应式的，可以通过 watch 监听
    console.log(props.title)
    
    // context 包含 attrs、slots、emit、expose
    const { attrs, slots, emit, expose } = context
    
    // 返回的数据和方法可在模板中使用
    const message = ref('Hello')
    function sayHello() {
      emit('change', message.value)
    }
    
    return {
      message,
      sayHello
    }
  }
}
</script>
```

### `<script setup>` 语法糖
`<script setup>` 是组合式 API 的编译时语法糖，更简洁：

```vue
<script setup>
// 所有顶层变量和函数自动暴露给模板
import { ref, computed } from 'vue'

const count = ref(0)
const double = computed(() => count.value * 2)

function increment() {
  count.value++
}

// props 声明
const props = defineProps({
  title: String
})

// emits 声明
const emit = defineEmits(['change'])

// 暴露给父组件
defineExpose({
  count,
  increment
})
</script>

<template>
  <div>
    <h1>{{ title }}</h1>
    <p>Count: {{ count }}, Double: {{ double }}</p>
    <button @click="increment">+1</button>
  </div>
</template>
```

```text
### `<script setup>` 特性
```
| 特性 | 说明 |
|------|------|
| 自动暴露 | 顶层变量、函数、import 自动暴露给模板 |
| 响应式 | `ref` 在模板中自动解包，无需 `.value` |
| TypeScript | 原生支持类型推导，`defineProps` 支持泛型 |
| 组件注册 | import 的组件自动注册，无需 `components` 选项 |
| 自定义指令 | import 的自定义指令自动注册 |
| 顶层 await | 支持顶层 `await`，组件自动变为 `async` |
| 编译优化 | 编译时优化，运行时开销更小 |

---

## 三、响应式 API

### 1. ref — 基本类型响应式
`ref` 用于创建基本类型（字符串、数字、布尔值）的响应式数据，返回一个带有 `.value` 属性的对象。

```javascript
import { ref } from 'vue'

// 创建响应式数据
const count = ref(0)
const name = ref('Vue3')
const isActive = ref(true)

// 读取和修改（JS 中需要 .value）
console.log(count.value) // 0
count.value++
console.log(count.value) // 1

// 模板中自动解包，无需 .value
// <p>{{ count }}</p>
```

**ref 的本质**：
- `ref` 内部通过 `class RefImpl` 实现，带有 `get value()` 和 `set value()` 拦截器
- 读取时触发依赖收集（track），修改时触发更新（trigger）
- 对于对象类型，`ref` 内部会调用 `reactive` 进行深层响应式转换

**isRef / unref / toRef / toValue**
```javascript
import { ref, isRef, unref, toRef, toValue } from 'vue'

const count = ref(0)

// 判断是否为 ref
console.log(isRef(count)) // true
console.log(isRef(0)) // false

// 如果是 ref 返回 .value，否则返回原值
console.log(unref(count)) // 0
console.log(unref(0)) // 0

// Vue3.3+：toValue 是 unref 的别名，支持函数
console.log(toValue(count)) // 0
console.log(toValue(() => 42)) // 42

// 从响应式对象创建单个 ref
const state = reactive({ count: 0 })
const countRef = toRef(state, 'count')
countRef.value++
console.log(state.count) // 1
```

### 2. reactive — 对象类型响应式
`reactive` 用于创建对象类型（对象、数组、Map、Set）的响应式数据，返回原始对象的响应式代理。

```javascript
import { reactive } from 'vue'

// 创建响应式对象
const state = reactive({
  count: 0,
  name: 'Vue3',
  nested: {
    value: 100
  }
})

// 直接访问和修改，无需 .value
console.log(state.count) // 0
state.count++
state.nested.value = 200

// 响应式数组
const list = reactive([1, 2, 3])
list.push(4)
list[0] = 100

// reactive 会递归转换嵌套对象为响应式
console.log(isReactive(state.nested)) // true
```

**reactive 的本质**：
- `reactive` 内部通过 `Proxy` 实现，拦截对象的 `get`、`set`、`deleteProperty` 等操作
- 读取时触发依赖收集，修改时触发更新
- 深层响应式：递归转换嵌套对象
- 只能用于对象类型，基本类型需要用 `ref`

**reactive 的局限性**：
```javascript
// 1. 不能直接替换整个对象（会丢失响应式）
let state = reactive({ count: 0 })
state = reactive({ count: 1 }) // 旧的 state 失去响应式

// 2. 解构会丢失响应式
const { count } = reactive({ count: 0 })
count++ // 不会触发更新

// 3. 基本类型不能用 reactive
const num = reactive(0) // 无效

// 解决方案：使用 ref 或 toRefs
const state = reactive({ count: 0 })
const { count } = toRefs(state) // count 是 ref，保持响应式
```

### 3. computed — 计算属性
`computed` 用于创建基于其他响应式数据计算得出的值，具有缓存特性。

```javascript
import { ref, computed } from 'vue'

const firstName = ref('张')
const lastName = ref('三')

// 只读计算属性
const fullName = computed(() => {
  return firstName.value + lastName.value
})

console.log(fullName.value) // 张三

// 可写计算属性（getter + setter）
const fullNameWritable = computed({
  get() {
    return firstName.value + lastName.value
  },
  set(value) {
    firstName.value = value[0]
    lastName.value = value.slice(1)
  }
})

fullNameWritable.value = '李四'
console.log(firstName.value) // 李
console.log(lastName.value) // 四
```

**computed 的特性**：
- **惰性求值**：只有被访问时才计算
- **缓存**：依赖不变时，直接返回缓存结果，不重复计算
- **依赖追踪**：自动追踪依赖，依赖变化时重新计算
- **可写**：支持 getter + setter，创建可写计算属性

**computed vs methods**：
| 特性 | computed | methods |
|------|----------|---------|
| 缓存 | 有缓存，依赖不变不重复计算 | 每次调用都执行 |
| 调用方式 | 像属性一样访问（`{{ fullName }}`） | 像函数一样调用（`{{ getFullName() }}`） |
| 适用场景 | 基于其他数据计算的值 | 事件处理、复杂逻辑、有副作用的操作 |

### 4. watch — 侦听器
`watch` 用于监听响应式数据的变化，执行副作用操作。

```javascript
import { ref, watch, watchEffect } from 'vue'

const count = ref(0)
const name = ref('Vue')

// 监听单个 ref
watch(count, (newVal, oldVal) => {
  console.log(`count 变化: ${oldVal} -> ${newVal}`)
})

// 监听多个源
watch([count, name], ([newCount, newName], [oldCount, oldName]) => {
  console.log(`count: ${oldCount} -> ${newCount}`)
  console.log(`name: ${oldName} -> ${newName}`)
})

// 监听 reactive 对象的属性（需要用函数）
const state = reactive({ count: 0 })
watch(
  () => state.count,
  (newVal, oldVal) => {
    console.log(`state.count 变化: ${oldVal} -> ${newVal}`)
  }
)

// 深度监听（监听对象的所有嵌套属性）
watch(
  () => state,
  (newVal) => {
    console.log('state 变化', newVal)
  },
  { deep: true }
)

// 立即执行（immediate）
watch(
  count,
  (newVal) => {
    console.log('立即执行', newVal)
  },
  { immediate: true }
)

// watchEffect：自动追踪依赖，立即执行
watchEffect(() => {
  console.log(`count: ${count.value}, name: ${name.value}`)
})
```

**watch 的选项**：
| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `deep` | boolean | false | 是否深度监听对象嵌套属性 |
| `immediate` | boolean | false | 是否立即执行回调 |
| `flush` | string | 'pre' | 回调执行时机：'pre'（组件更新前）、'post'（更新后）、'sync'（同步） |
| `onTrigger` | function | - | 调试用，侦听器触发时调用 |

**watch vs watchEffect**：
| 特性 | watch | watchEffect |
|------|-------|-------------|
| 依赖追踪 | 显式指定监听源 | 自动追踪回调中的依赖 |
| 访问旧值 | 可以获取旧值（oldVal） | 不能获取旧值 |
| 执行时机 | 默认惰性（变化时才执行） | 立即执行 |
| 适用场景 | 需要旧值、需要控制监听源 | 自动追踪多个依赖、副作用 |

### 5. 其他响应式 API

**readonly — 只读响应式**
```javascript
import { reactive, readonly } from 'vue'

const original = reactive({ count: 0 })
const copy = readonly(original)

// original 可以修改
original.count++

// copy 不能修改（开发环境会警告）
copy.count++ // 警告：Set operation on key "count" failed: target is readonly.
```

**shallowRef / shallowReactive — 浅层响应式**
```javascript
import { shallowRef, shallowReactive, triggerRef } from 'vue'

// shallowRef：只有 .value 的变化是响应式的，嵌套对象不响应式
const state = shallowRef({ count: 0 })
state.value.count++ // 不会触发更新
state.value = { count: 1 } // 会触发更新
triggerRef(state) // 手动触发更新

// shallowReactive：只有第一层属性是响应式的
const obj = shallowReactive({
  count: 0,
  nested: { value: 0 }
})
obj.count++ // 响应式
obj.nested.value++ // 不响应式
```

**toRefs — 解构保持响应式**
```javascript
import { reactive, toRefs } from 'vue'

const state = reactive({
  count: 0,
  name: 'Vue'
})

// 直接解构会丢失响应式
// const { count, name } = state // 不响应式

// 使用 toRefs 保持响应式
const { count, name } = toRefs(state)
count.value++ // 响应式，state.count 也会变化
```

---

## 四、生命周期钩子

组合式 API 中使用 `onXxx` 函数注册生命周期钩子，必须在 `setup` 同步执行期间调用。

```javascript
import {
  onBeforeMount,
  onMounted,
  onBeforeUpdate,
  onUpdated,
  onBeforeUnmount,
  onUnmounted,
  onActivated,
  onDeactivated,
  onErrorCaptured,
  onRenderTracked,
  onRenderTriggered
} from 'vue'

export default {
  setup() {
    // 挂载前
    onBeforeMount(() => {
      console.log('组件挂载前，DOM 还未创建')
    })

    // 挂载后（常用：发起请求、操作 DOM、初始化第三方库）
    onMounted(() => {
      console.log('组件挂载后，DOM 已创建')
    })

    // 更新前
    onBeforeUpdate(() => {
      console.log('组件更新前，DOM 还未更新')
    })

    // 更新后
    onUpdated(() => {
      console.log('组件更新后，DOM 已更新')
    })

    // 卸载前
    onBeforeUnmount(() => {
      console.log('组件卸载前，实例还可用')
    })

    // 卸载后（常用：清除定时器、取消订阅、移除事件监听）
    onUnmounted(() => {
      console.log('组件卸载后，实例已销毁')
    })

    // keep-alive 激活时
    onActivated(() => {
      console.log('keep-alive 组件激活')
    })

    // keep-alive 停用时
    onDeactivated(() => {
      console.log('keep-alive 组件停用')
    })

    // 捕获子孙组件错误
    onErrorCaptured((err, instance, info) => {
      console.error('捕获到错误:', err)
      return false // 阻止错误继续向上传播
    })

    // 调试：渲染追踪（开发环境）
    onRenderTracked((event) => {
      console.log('渲染追踪:', event)
    })

    // 调试：渲染触发（开发环境）
    onRenderTriggered((event) => {
      console.log('渲染触发:', event)
    })
  }
}
```

### 生命周期对比
| 选项式 API | 组合式 API | 说明 |
|------------|-----------|------|
| `beforeCreate` | -（setup 本身） | 组件创建前 |
| `created` | -（setup 本身） | 组件创建后 |
| `beforeMount` | `onBeforeMount` | 挂载前 |
| `mounted` | `onMounted` | 挂载后 |
| `beforeUpdate` | `onBeforeUpdate` | 更新前 |
| `updated` | `onUpdated` | 更新后 |
| `beforeUnmount` | `onBeforeUnmount` | 卸载前 |
| `unmounted` | `onUnmounted` | 卸载后 |
| `activated` | `onActivated` | keep-alive 激活 |
| `deactivated` | `onDeactivated` | keep-alive 停用 |
| `errorCaptured` | `onErrorCaptured` | 捕获错误 |

---

## 五、组合式函数（Composables）

### 什么是组合式函数
组合式函数是利用 Vue 组合式 API 封装和复用有状态逻辑的函数，命名约定为 `useXxx`。

### 示例：useCounter
```javascript
// composables/useCounter.js
import { ref, computed } from 'vue'

export function useCounter(initialValue = 0) {
  // 状态
  const count = ref(initialValue)
  
  // 计算属性
  const double = computed(() => count.value * 2)
  const isEven = computed(() => count.value % 2 === 0)
  
  // 方法
  function increment() {
    count.value++
  }
  
  function decrement() {
    count.value--
  }
  
  function reset() {
    count.value = initialValue
  }
  
  // 返回状态和方法
  return {
    count,
    double,
    isEven,
    increment,
    decrement,
    reset
  }
}
```

**在组件中使用**
```vue
<script setup>
import { useCounter } from '@/composables/useCounter'

// 使用组合式函数
const { count, double, increment, decrement, reset } = useCounter(10)

// 可以多次使用，状态独立
const { count: count2, increment: increment2 } = useCounter(0)
</script>

<template>
  <div>
    <p>Count: {{ count }}, Double: {{ double }}</p>
    <button @click="increment">+1</button>
    <button @click="decrement">-1</button>
    <button @click="reset">重置</button>
  </div>
</template>
```

### 示例：useFetch（异步请求）
```javascript
// composables/useFetch.js
import { ref, shallowRef, watchEffect, toValue } from 'vue'

export function useFetch(url, options = {}) {
  const data = shallowRef(null)
  const error = ref(null)
  const isLoading = ref(false)
  const isFinished = ref(false)

  async function execute() {
    isLoading.value = true
    error.value = null
    isFinished.value = false

    try {
      const response = await fetch(toValue(url), options)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      data.value = await response.json()
    } catch (err) {
      error.value = err
    } finally {
      isLoading.value = false
      isFinished.value = true
    }
  }

  // 如果 url 是响应式的，自动重新请求
  watchEffect(() => {
    execute()
  })

  return {
    data,
    error,
    isLoading,
    isFinished,
    execute,
    refresh: execute
  }
}
```

**使用**
```vue
<script setup>
import { ref } from 'vue'
import { useFetch } from '@/composables/useFetch'

const userId = ref(1)
const { data, error, isLoading, refresh } = useFetch(
  () => `https://api.example.com/users/${userId.value}`
)
</script>

<template>
  <div v-if="isLoading">加载中...</div>
  <div v-else-if="error">错误: {{ error.message }}</div>
  <div v-else>
    <pre>{{ data }}</pre>
    <button @click="refresh">刷新</button>
  </div>
</template>
```

### 示例：useMouse（鼠标位置）
```javascript
// composables/useMouse.js
import { ref, onMounted, onUnmounted } from 'vue'

export function useMouse() {
  const x = ref(0)
  const y = ref(0)

  function update(event) {
    x.value = event.pageX
    y.value = event.pageY
  }

  onMounted(() => {
    window.addEventListener('mousemove', update)
  })

  onUnmounted(() => {
    window.removeEventListener('mousemove', update)
  })

  return { x, y }
}
```

### 组合式函数最佳实践
1. **命名约定**：使用 `use` 前缀，如 `useCounter`、`useFetch`、`useMouse`
2. **返回对象**：返回响应式状态和方法的对象，支持解构
3. **状态封装**：状态定义在函数内部，不污染外部作用域
4. **生命周期管理**：在函数内部注册和清理生命周期钩子
5. **参数设计**：支持响应式参数（使用 `toValue` 处理 ref 和原始值）
6. **类型安全**：使用 TypeScript 定义参数和返回值类型
7. **单一职责**：每个组合式函数只负责一个逻辑领域

---

## 六、依赖注入（Provide / Inject）

组合式 API 中使用 `provide` 和 `inject` 实现跨层级组件通信。

```javascript
// 父组件
<script setup>
import { provide, ref, readonly } from 'vue'

const theme = ref('light')
const user = reactive({ name: '张三', role: 'admin' })

// provide 响应式数据
provide('theme', theme)
provide('user', readonly(user)) // 使用 readonly 防止子组件修改

// provide 方法
provide('toggleTheme', () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
})

// 使用 Symbol 作为 key，避免命名冲突
const ThemeKey = Symbol('theme')
provide(ThemeKey, theme)
</script>

// 子孙组件
<script setup>
import { inject } from 'vue'

// inject 数据
const theme = inject('theme')
const user = inject('user')
const toggleTheme = inject('toggleTheme')

// inject 带默认值
const locale = inject('locale', 'zh-CN')

// 使用 Symbol key
const ThemeKey = Symbol('theme')
const theme2 = inject(ThemeKey)
</script>
```

---

## 七、组合式 API 设计模式

### 1. 逻辑关注点分离
将组件按逻辑关注点拆分，每个关注点使用组合式函数封装。

```vue
<script setup>
// 用户逻辑
const { user, login, logout, isLoggedIn } = useAuth()

// 数据逻辑
const { list, loading, error, fetchList, refresh } = useList('/api/items')

// 表单逻辑
const { form, errors, validate, submit, reset } = useForm({
  name: '',
  email: ''
})

// UI 状态
const { isModalOpen, openModal, closeModal } = useModal()
</script>
```

### 2. 响应式状态管理
使用组合式函数实现简单的状态管理（替代 Pinia 的轻量方案）。

```javascript
// stores/useCounterStore.js
import { reactive, computed } from 'vue'

// 模块级状态（单例）
const state = reactive({
  count: 0
})

export function useCounterStore() {
  const double = computed(() => state.count * 2)
  
  function increment() {
    state.count++
  }
  
  function decrement() {
    state.count--
  }
  
  function reset() {
    state.count = 0
  }
  
  return {
    state,
    double,
    increment,
    decrement,
    reset
  }
}
```

### 3. 模板引用（Template Refs）
```vue
<script setup>
import { ref, onMounted } from 'vue'

// 模板引用
const inputRef = ref(null)
const listRef = ref([])

onMounted(() => {
  // 访问 DOM 元素
  inputRef.value.focus()
  console.log(listRef.value) // [li, li, li]
})

// v-for 中的模板引用
const items = ref([1, 2, 3])
function setItemRef(el, index) {
  listRef.value[index] = el
}
</script>

<template>
  <input ref="inputRef" type="text" />
  <ul>
    <li
      v-for="(item, index) in items"
      :key="item"
      :ref="(el) => setItemRef(el, index)"
    >
      {{ item }}
    </li>
  </ul>
</template>
```

---

## 八、常见问题与最佳实践

### 1. ref vs reactive 如何选择？
| 场景 | 推荐 | 原因 |
|------|------|------|
| 基本类型（string/number/boolean） | `ref` | `reactive` 不支持基本类型 |
| 单个对象 | `ref` 或 `reactive` | 都可以，`ref` 需要 `.value`，`reactive` 不能解构 |
| 多个相关状态 | `reactive` | 组织在一个对象中，语义清晰 |
| 需要解构/展开 | `ref` + `toRefs` | `reactive` 解构会丢失响应式 |
| 函数参数/返回值 | `ref` | 更灵活，可单独传递 |
| 大型表单对象 | `reactive` | 直接访问属性，无需 `.value` |

**经验法则**：默认使用 `ref`，需要组织多个相关状态时使用 `reactive`。

### 2. 为什么 ref 在模板中不需要 .value？
Vue 编译器在编译模板时，会自动对 `ref` 进行解包（unref）。这是编译时优化，不是运行时特性。

```vue
<script setup>
const count = ref(0)
</script>

<template>
  <!-- 模板中自动解包，等价于 count.value -->
  <p>{{ count }}</p>
  <button @click="count++">+1</button>
</template>
```

注意：只有顶层 `ref` 会自动解包，嵌套在对象中的 `ref` 不会。

### 3. 如何避免响应式丢失？
```javascript
// 错误：解构 reactive 对象
const state = reactive({ count: 0 })
const { count } = state // count 失去响应式

// 正确：使用 toRefs
const { count } = toRefs(state) // count 是 ref，保持响应式

// 错误：替换整个 reactive 对象
let state = reactive({ count: 0 })
state = reactive({ count: 1 }) // 旧的失去响应式

// 正确：修改属性或使用 ref
state.count = 1 // 保持响应式
// 或
const state = ref({ count: 0 })
state.value = { count: 1 } // 保持响应式
```

### 4. 组合式函数中如何使用生命周期钩子？
生命周期钩子必须在 `setup` 同步执行期间调用，包括在组合式函数内部调用。只要组合式函数是在 `setup` 中同步调用的，内部的 `onMounted` 等钩子就能正确绑定到当前组件。

```javascript
// 正确：在 setup 中同步调用组合式函数
<script setup>
// useMouse 内部的 onMounted/onUnmounted 会正确绑定到当前组件
const { x, y } = useMouse()
</script>

// 错误：在异步回调中调用
<script setup>
onMounted(() => {
  const { x, y } = useMouse() // 错误：生命周期钩子无法绑定
})
</script>
```

### 5. 性能优化建议
1. **使用 `shallowRef` / `shallowReactive`**：对于大型对象，不需要深层响应式时使用浅层 API，减少响应式转换开销
2. **使用 `shallowRef` 存储大型数据**：从 API 获取的大型列表，使用 `shallowRef` 避免深层响应式转换
3. **合理使用 `computed`**：复杂计算使用 `computed` 缓存，避免每次渲染都计算
4. **避免在模板中调用函数**：模板中调用函数每次渲染都会执行，改用 `computed`
5. **使用 `v-memo`**：对于大型列表，使用 `v-memo` 缓存渲染结果
6. **合理拆分组件**：将大型组件拆分为小组件，减少重新渲染范围
7. **使用 `defineProps` 的类型声明**：TypeScript 类型声明比运行时声明更高效

---

## 🔗 关联笔记

**Vue3 核心**
- [[Vue3 知识点系统梳理_优化版]] — Vue3 完整知识体系
- [[Vue3快速上手_优化版]] — Vue3 零基础入门
- [[Vue3-响应式原理Proxy]] — Vue3 响应式原理深度解析
- [[Vue3-编译优化与PatchFlags]] — Vue3 编译优化深度解析

**组合式 API 实践**
- [[Vue3-自定义Hooks封装]] — 自定义 Hooks（组合式函数）封装实践
- [[Vue3-组件通信全方案]] — Vue3 组件通信全方案
- [[Vue3-组合式API设计模式]] — 组合式 API 设计模式

**相关技术**
- [[Vue3+TypeScript核心知识点总结_优化版]] — Vue3 + TypeScript 类型安全开发
- [[Pinia 知识点系统梳理_优化版]] — Pinia 状态管理
- [[前端工程化知识点系统梳理_优化版]] — 前端工程化

---

## 📖 学习路径建议

1. **入门**：理解组合式 API 基本概念，掌握 `setup`、`ref`、`reactive`、`computed`、`watch` 的基本用法
2. **进阶**：深入响应式原理，掌握生命周期钩子、依赖注入、组合式函数封装
3. **高级**：研究组合式 API 设计模式，掌握性能优化、TypeScript 类型安全、大型组件架构
4. **专家**：阅读 Vue3 源码，理解组合式 API 的编译时和运行时实现，参与开源贡献

---

## 💡 精简总结

组合式 API（Composition API）是 Vue3 的核心特性，通过 `setup` 函数将相关逻辑组织在一起，解决了选项式 API 在大型组件中逻辑分散、复用困难的问题。核心 API 包括：`ref`（基本类型响应式）、`reactive`（对象类型响应式）、`computed`（计算属性，带缓存）、`watch`（侦听器，执行副作用）。`<script setup>` 是编译时语法糖，让组合式 API 更简洁。组合式函数（Composables）是复用有状态逻辑的最佳方式，命名约定为 `useXxx`。组合式 API 具有更好的逻辑组织、更灵活的代码复用、更友好的 TypeScript 支持和更小的产物体积，是 Vue3 开发的推荐方式。

---

> **组合式 API 的本质不是新语法，而是一种新的组织代码的思维方式——按逻辑关注点组织，而不是按选项类型组织。**

[[Home|🏠 返回首页]] · [[MOC-前端开发|🎨 前端开发]] · [[学习路线总览|🗺️ 学习路线]]
