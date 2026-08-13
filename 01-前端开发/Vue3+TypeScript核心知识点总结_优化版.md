---
title: Vue3 + TypeScript 核心知识点总结
tags: [前端, Vue3, TypeScript, 工程化]
created: 2026-08-12
updated: 2026-08-12
---

# Vue3 + TypeScript 核心知识点总结（优化版）

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。


> 基于学习笔记系统整理，涵盖从基础语法到项目工程化的完整知识体系。按「基础 → 组件 → 状态路由 → 工程化 → UI样式 → 数据请求 → 业务实战 → 进阶」八大篇章组织，逻辑递进，便于系统学习和快速查阅

---

# 第一篇：基础篇

## 第1章 TypeScript 基础

TypeScript 是 JavaScript 的超集，为其添加了类型系统。Vue3 完全使用 TypeScript 重写，掌握 TS 是 Vue3 开发的基础。

### 1.1 基本类型

| 类型 | 例子 | 描述 |
|------|------|------|
| `number` | `1, -33, 2.5` | 任意数字 |
| `string` | `'hi', "hi", \`hi\`` | 任意字符串 |
| `boolean` | `true, false` | 布尔值 |
| 字面量 | 其本身 | 限制变量的值就是该字面量的值 |
| `any` | `*` | 任意类型（不推荐，放弃类型检查） |
| `unknown` | `*` | 类型安全的 any |
| `void` | `undefined` | 没有返回值 |
| `never` | 没有值 | 永远不会返回结果 |
| `object` | `{name:'孙悟空'}` | 任意对象 |
| `array` | `[1,2,3]` | 任意数组 |
| `tuple` | `[4,5]` | 固定长度和类型的数组 |
| `enum` | `enum{A, B}` | 枚举 |

#### any 与 unknown 的区别

```typescript
// any：可以赋值给任何类型，也可以接收任何类型（完全放弃类型检查）
let notSure: any = 4
notSure = "maybe a string"
notSure.myMethod()  // 不会报错，但运行时可能出错

// unknown：类型安全的 any，不能直接赋值给其他确定类型，也不能直接调用方法
let value: unknown = 10
let str: string = value  // ❌ 错误
let str: string = value as string  // ✅ 需要类型断言
```


> 🔍 **知识点深度解析**
>
> **作用**：TS基本类型在编译时做静态类型检查，运行时擦除类型。
>
> **原理**：tuple固定长度类型，enum编译为对象（推荐const enum减少体积）。
>
> **用法要点**：① TS基本类型在编译时做静态类型检查，运行时擦除类型 ② any完全放弃检查（不推荐），unknown是类型安全的any（需断言后使用） ③ never用于永不到达的分支（抛异常/死循环） ④ tuple固定长度类型，enum编译为对象（推荐const enum减少体积）

### 1.2 接口 interface

接口用于定义对象的形状，是 TypeScript 中最核心的概念之一。

```typescript
interface Person {
  readonly id: number   // 只读属性
  name: string
  age?: number          // 可选属性
  [propName: string]: any  // 索引签名：任意额外属性
}

// 接口继承
interface Animal {
  name: string
}
interface Dog extends Animal {
  breed: string
}
```


> 🔍 **知识点深度解析**
>
> **作用**：interface定义对象形状，支持声明合并（同名接口自动合并）、继承（extends）、只读（readonly）、可选（?）、索引签名。
>
> **原理**：是Vue3中定义props、API响应数据、组件状态的标准方式。
>
> **用法要点**：① interface定义对象形状，支持声明合并（同名接口自动合并）、继承（extends）、只读（readonly）、可选（?）、索引签名 ② 是Vue3中定义props、API响应数据、组件状态的标准方式 ③ 优先用interface定义对象类型

### 1.3 类型别名 type

类型别名用来给一个类型起个新名字，比 interface 更灵活。

```typescript
// 联合类型
type Status = "success" | "error" | "loading"

// 交叉类型
type A = { a: number }
type B = { b: string }
type C = A & B  // { a: number; b: string }

// 元组
type Point = [number, number]
```

#### type vs interface 对比

| 特性 | interface | type |
|------|-----------|------|
| 定义对象类型 | ✅ 推荐 | ✅ |
| 定义联合类型 | ❌ | ✅ |
| 定义交叉类型 | ❌ | ✅ |
| 定义元组 | ❌ | ✅ |
| 声明合并 | ✅ | ❌ |
| 继承方式 | extends | &（交叉类型） |


> 🔍 **知识点深度解析**
>
> **作用**：type别名比interface更灵活，支持联合类型（A|B）、交叉类型（A&B）、元组、条件类型、映射类型。
>
> **原理**：不能声明合并。
>
> **用法要点**：① type别名比interface更灵活，支持联合类型（A|B）、交叉类型（A&B）、元组、条件类型、映射类型 ② 不能声明合并 ③ 对象类型推荐interface，联合/交叉/工具类型用type ④ 两者可混合使用

### 1.4 泛型

泛型是指在定义函数、接口或类的时候，不预先指定具体的类型，而在使用的时候再指定类型的一种特性。

```typescript
// 泛型函数
function identity<T>(arg: T): T {
  return arg
}

// 泛型约束
interface Lengthwise {
  length: number
}
function loggingIdentity<T extends Lengthwise>(arg: T): T {
  console.log(arg.length)
  return arg
}

// 在 Vue3 中使用泛型
const count = ref<number>(0)
const user = reactive<User>({ name: '张三', age: 18 })
defineProps<{ list: User[]; title?: string }>()
```


> 🔍 **知识点深度解析**
>
> **作用**：泛型在使用时指定类型，实现类型复用与安全。
>
> **原理**：T extends约束泛型范围。
>
> **用法要点**：① 泛型在使用时指定类型，实现类型复用与安全 ② T extends约束泛型范围 ③ Vue3中ref<T>、reactive<T>、defineProps<T>()、defineEmits<T>()大量使用泛型 ④ 掌握泛型是写好Vue3+TS的关键

### 1.5 类型断言与类型守卫

```typescript
// 类型断言（推荐用 as）
let someValue: any = "this is a string"
let strLength: number = (someValue as string).length

// 类型守卫
function padLeft(value: string, padding: string | number) {
  if (typeof padding === "number") {  // typeof 守卫
    return Array(padding + 1).join(" ") + value
  }
  if (typeof padding === "string") {
    return padding + value
  }
}
```

---

## 第2章 Vue3 响应式核心

Vue3 的响应式系统基于 Proxy 实现，比 Vue2 的 Object.defineProperty 更强大、性能更好。


> 🔍 **知识点深度解析**
>
> **作用**：类型断言（as）告诉编译器我比你更清楚类型，不做运行时检查。
>
> **原理**：类型守卫（typeof/instanceof/in/自定义is）在运行时缩窄类型。
>
> **用法要点**：① 类型断言（as）告诉编译器我比你更清楚类型，不做运行时检查 ② 类型守卫（typeof/instanceof/in/自定义is）在运行时缩窄类型 ③ unknown必须先断言或守卫才能使用 ④ 避免滥用as，优先用类型守卫

### 2.1 ref 与 reactive

Vue3 提供了两种创建响应式数据的方式：`ref` 和 `reactive`。

#### ref — 基本类型和对象都支持

```typescript
import { ref } from 'vue'

// 基本类型
const count = ref(0)
console.log(count.value)  // 0

// 对象类型
const person = ref({ name: '张三', age: 18 })
console.log(person.value.name)  // 张三

// 可以整体替换
person.value = { name: '李四', age: 90 }
```

#### reactive — 仅对象类型，直接访问

```typescript
import { reactive } from 'vue'

const person = reactive({
  name: '张三',
  age: 18
})

// 直接访问，不需要 .value
console.log(person.name)  // 张三

// ❌ 不能整体替换（会丢失响应式）
// person = { name: '李四', age: 80 }

// ✅ 正确方式：Object.assign
Object.assign(person, { name: '李四', age: 80 })
```

#### ref vs reactive 对比

| 特性 | ref | reactive |
|------|-----|----------|
| 支持基本类型 | ✅ | ❌ |
| 支持对象类型 | ✅ | ✅ |
| 访问方式 | `.value` | 直接访问 |
| 整体替换 | ✅ | ❌（需 Object.assign） |
| 模板中自动解包 | ✅ | ✅ |

#### 最佳实践

```typescript
// 基本类型用 ref
const count = ref(0)
const message = ref('hello')

// 对象/数组用 reactive
const form = reactive({ username: '', password: '' })
const list = reactive<User[]>([])
```


> 🔍 **知识点深度解析**
>
> **作用**：ref创建RefImpl（.value响应式），支持基本和对象类型（对象内部调reactive）。
>
> **原理**：reactive创建Proxy代理（深层响应式），仅对象类型。
>
> **用法要点**：① ref创建RefImpl（.value响应式），支持基本和对象类型（对象内部调reactive） ② reactive创建Proxy代理（深层响应式），仅对象类型 ③ ref可整体替换，reactive不行（用Object.assign） ④ 基本类型必须ref，对象类型推荐reactive或统一用ref

### 2.2 computed 计算属性

计算属性用于根据已有响应式数据派生出新的数据，**具有缓存特性**，只有依赖变化时才重新计算。

```typescript
import { ref, computed } from 'vue'

const firstName = ref('张')
const lastName = ref('三')

// 只读计算属性
const fullName = computed(() => firstName.value + lastName.value)

// 可写计算属性（getter/setter）
const fullNameWritable = computed({
  get() { return firstName.value + lastName.value },
  set(val: string) {
    const names = val.split('')
    firstName.value = names[0]
    lastName.value = names.slice(1).join('')
  }
})
```


> 🔍 **知识点深度解析**
>
> **作用**：computed基于依赖缓存（dirty标记），依赖不变直接返回缓存值。
>
> **原理**：比methods高效（methods每次调用都执行）。
>
> **用法要点**：① computed基于依赖缓存（dirty标记），依赖不变直接返回缓存值 ② getter只读，get/set可写 ③ 比methods高效（methods每次调用都执行） ④ 不要在computed中写副作用（修改state/发请求），会导致无限循环

### 2.3 watch 侦听器

`watch` 用于监听响应式数据的变化，执行副作用操作。

```typescript
import { ref, reactive, watch } from 'vue'

const count = ref(0)
const person = reactive({ name: '张三', age: 18 })

// 监听 ref
watch(count, (newVal, oldVal) => {
  console.log(`count: ${oldVal} -> ${newVal}`)
})

// 监听 reactive 的某个属性
watch(
  () => person.name,
  (newVal, oldVal) => {
    console.log(`name: ${oldVal} -> ${newVal}`)
  }
)

// 监听多个数据源
watch([firstName, lastName], ([newFirst, newLast], [oldFirst, oldLast]) => {
  console.log('都变化了')
})

// 配置选项
watch(source, callback, {
  deep: true,       // 深度监听
  immediate: true,  // 立即执行一次
  flush: 'post'     // 回调时机：pre(默认) / sync / post
})
```


> 🔍 **知识点深度解析**
>
> **作用**：watch监听指定数据源，支持ref/reactive/getter/数组。
>
> **原理**：监听对象属性用getter函数。
>
> **用法要点**：① watch监听指定数据源，支持ref/reactive/getter/数组 ② ref对象类型需deep:true，reactive默认深度 ③ 监听对象属性用getter函数 ④ immediate立即执行，flush控制回调时机（pre默认/post DOM更新后/sync同步） ⑤ 返回停止函数

### 2.4 watchEffect

`watchEffect` 会立即执行传入的函数，并自动追踪其依赖，当依赖变化时重新执行。

```typescript
import { ref, watchEffect } from 'vue'

const count = ref(0)
const name = ref('张三')

// 立即执行，自动追踪所有依赖
watchEffect(() => {
  console.log(`count: ${count.value}, name: ${name.value}`)
})

// 停止监听
const stop = watchEffect(() => { /* ... */ })
stop()
```

#### watch vs watchEffect 对比

| 特性 | watch | watchEffect |
|------|-------|-------------|
| 明确指定监听源 | ✅ | ❌（自动追踪） |
| 获取旧值 | ✅ | ❌ |
| 立即执行 | 需配置 `immediate` | 默认立即执行 |
| 懒执行 | ✅（默认） | ❌ |


> 🔍 **知识点深度解析**
>
> **作用**：watchEffect自动收集依赖（函数中用到的响应式数据），立即执行一次，不需要指定监听源。
>
> **原理**：适合依赖多个数据的场景。
>
> **用法要点**：① watchEffect自动收集依赖（函数中用到的响应式数据），立即执行一次，不需要指定监听源 ② 适合依赖多个数据的场景 ③ watch可获取oldValue且懒执行 ④ onCleanup清理副作用（取消请求/定时器）

### 2.5 生命周期钩子

Vue3 组合式 API 中的生命周期钩子需要从 `vue` 中导入。

| 选项式 API | 组合式 API | 说明 |
|-----------|-----------|------|
| `beforeCreate` | - | setup 本身就是 |
| `created` | - | setup 本身就是 |
| `beforeMount` | `onBeforeMount` | 挂载前 |
| `mounted` | `onMounted` | 挂载后 |
| `beforeUpdate` | `onBeforeUpdate` | 更新前 |
| `updated` | `onUpdated` | 更新后 |
| `beforeUnmount` | `onBeforeUnmount` | 卸载前 |
| `unmounted` | `onUnmounted` | 卸载后 |
| `activated` | `onActivated` | keep-alive 激活 |
| `deactivated` | `onDeactivated` | keep-alive 失活 |

```typescript
import { onMounted, onUpdated, onUnmounted } from 'vue'

onMounted(() => {
  console.log('组件已挂载')
  // 常用于：DOM 操作、获取数据、初始化第三方库
})

onUnmounted(() => {
  console.log('组件已卸载')
  // 常用于：清除定时器、取消订阅、移除事件监听
})
```

---

# 第二篇：组件篇

## 第3章 组件通信

Vue3 组件通信方式丰富，从父子到跨层级都有对应方案。


> 🔍 **知识点深度解析**
>
> **作用**：Vue3生命周期用onXxx命名，在setup中调用。
>
> **原理**：onMounted访问DOM/ref，onBeforeUnmount清理副作用（定时器/事件监听/订阅）。
>
> **用法要点**：① Vue3生命周期用onXxx命名，在setup中调用 ② setup替代beforeCreate/created ③ onMounted访问DOM/ref，onBeforeUnmount清理副作用（定时器/事件监听/订阅） ④ keep-alive组件用onActivated/onDeactivated

### 3.1 Props — 父传子

`defineProps` 是 `<script setup>` 中声明 props 的编译器宏。

#### 基本用法

```typescript
// 子组件
const props = defineProps({
  title: String,
  count: {
    type: Number,
    default: 0,
    required: true,
    validator: (value) => value >= 0
  }
})
```

#### TypeScript 泛型写法（推荐）

```typescript
// 定义类型
interface User {
  id: number
  name: string
  age?: number
}

// 泛型写法
const props = defineProps<{
  list: User[]
  title?: string
  count: number
}>()

// 带默认值（withDefaults）
const props = withDefaults(defineProps<{
  title?: string
  size?: 'small' | 'default' | 'large'
}>(), {
  title: '默认标题',
  size: 'default'
})
```

#### 导入类型

```typescript
// 使用 import type 导入类型，避免运行时引入
import type { User } from '@/types/user'

defineProps<{
  user: User
}>()
```


> 🔍 **知识点深度解析**
>
> **作用**：defineProps是编译器宏（不需import），TS泛型写法推荐。
>
> **原理**：import type导入类型避免运行时引入。
>
> **用法要点**：① defineProps是编译器宏（不需import），TS泛型写法推荐 ② withDefaults设置默认值（对象/数组默认值用函数） ③ props只读（单向数据流），子组件不要修改，用emit通知父组件 ④ import type导入类型避免运行时引入

### 3.2 Emits — 子传父

`defineEmits` 用于声明组件可以触发的自定义事件。

#### 基本用法

```typescript
// 子组件
const emit = defineEmits(['update', 'delete'])

// 触发事件
emit('update', newValue)
emit('delete', id)
```

#### TypeScript 类型写法（推荐）

```typescript
const emit = defineEmits<{
  (e: 'update', value: string): void
  (e: 'delete', id: number): void
  (e: 'change', oldVal: string, newVal: string): void
}>()

// 使用
emit('update', '新值')
emit('change', '旧值', '新值')
```

#### 父组件监听

```vue
<!-- 父组件 -->
<ChildComponent
  @update="handleUpdate"
  @delete="handleDelete"
/>
```


> 🔍 **知识点深度解析**
>
> **作用**：defineEmits声明自定义事件，TS写法用函数签名定义参数类型。
>
> **原理**：emit触发时父组件@事件名监听。
>
> **用法要点**：① defineEmits声明自定义事件，TS写法用函数签名定义参数类型 ② 事件名推荐kebab-case ③ emit触发时父组件@事件名监听 ④ 原生事件event是事件对象，自定义事件event是emit传的数据 ⑤ 子传父标准方式

### 3.3 v-model — 双向绑定

`v-model` 是 props + emits 的语法糖，用于实现双向绑定。

#### 基本用法

```vue
<!-- 父组件 -->
<Child v-model="message" />
<!-- 等价于 -->
<Child :modelValue="message" @update:modelValue="message = $event" />
```

```typescript
// 子组件
const props = defineProps<{
  modelValue: string
}>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

// 更新值
emit('update:modelValue', '新值')
```

#### 多个 v-model

```vue
<!-- 父组件 -->
<UserForm
  v-model:username="name"
  v-model:email="email"
/>
```

```typescript
// 子组件
const props = defineProps<{
  username: string
  email: string
}>()
const emit = defineEmits<{
  (e: 'update:username', value: string): void
  (e: 'update:email', value: string): void
}>()
```

#### v-model 修饰符

```typescript
const props = defineProps<{
  modelValue: string
  modelModifiers?: { capitalize?: boolean }
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

function emitValue(e: Event) {
  let value = (e.target as HTMLInputElement).value
  if (props.modelModifiers?.capitalize) {
    value = value.charAt(0).toUpperCase() + value.slice(1)
  }
  emit('update:modelValue', value)
}
```


> 🔍 **知识点深度解析**
>
> **作用**：组件v-model本质是:modelValue+@update:modelValue。
>
> **原理**：自定义组件需defineProps接收modelValue，defineEmits触发update:modelValue。
>
> **用法要点**：① 组件v-model本质是:modelValue+@update:modelValue ② 自定义组件需defineProps接收modelValue，defineEmits触发update:modelValue ③ 支持v-model:xxx多个双向绑定（替代Vue2的.sync） ④ 修饰符通过modelModifiers接收

### 3.4 Provide / Inject — 跨层级通信

用于祖先组件向后代组件传递数据，不需要逐层传递 props。

#### 基本用法

```typescript
// 祖先组件（提供数据）
import { provide, ref } from 'vue'

const theme = ref('dark')
provide('theme', theme)

// 后代组件（注入数据）
import { inject } from 'vue'

const theme = inject('theme')  // 可能是 undefined
```

#### 设置默认值

```typescript
// 注入时提供默认值
const theme = inject('theme', 'light')  // 默认值 'light'
```

#### 类型安全写法（InjectionKey）

```typescript
// src/keys/theme.ts
import type { InjectionKey, Ref } from 'vue'

// 定义注入键的类型
export const themeKey: InjectionKey<Ref<string>> = Symbol('theme')

// 祖先组件
import { provide, ref } from 'vue'
import { themeKey } from '@/keys/theme'

const theme = ref('dark')
provide(themeKey, theme)

// 后代组件
import { inject } from 'vue'
import { themeKey } from '@/keys/theme'

const theme = inject(themeKey)  // 类型安全：Ref<string> | undefined
```

#### 响应式数据传递

```typescript
// 提供响应式数据
const count = ref(0)
provide('count', count)  // 传入 ref，后代可响应式更新

// 提供方法
function increment() {
  count.value++
}
provide('increment', increment)
```


> 🔍 **知识点深度解析**
>
> **作用**：provide/inject跨层级通信（祖到孙），不需逐层传props。
>
> **原理**：可传响应式数据（ref/reactive）和方法。
>
> **用法要点**：① provide/inject跨层级通信（祖到孙），不需逐层传props ② provide提供数据，inject接收 ③ 可传响应式数据（ref/reactive）和方法 ④ InjectionKey保证类型安全 ⑤ 适合主题/用户信息等全局数据，复杂状态用Pinia

### 3.5 $attrs — 属性透传

`$attrs` 包含父组件传入但未被 props 声明的所有属性和事件。

#### 基本用法

```vue
<!-- 子组件 -->
<template>
  <!-- 将所有未声明的属性透传到内部元素 -->
  <div v-bind="$attrs">
    子组件内容
  </div>
</template>
```

#### 禁用继承

```typescript
// 禁用默认的属性继承（属性不会自动加到根元素上）
defineOptions({
  inheritAttrs: false
})
```

#### 透传到指定元素

```vue
<template>
  <div class="wrapper">
    <!-- 将 attrs 透传到 input 而不是根 div -->
    <input v-bind="$attrs" />
  </div>
</template>

<script setup lang="ts">
defineOptions({
  inheritAttrs: false
})
</script>
```


> 🔍 **知识点深度解析**
>
> **作用**：attrs包含未声明为props的属性（含class/style/事件），自动继承到根元素。
>
> **原理**：inheritAttrs:false阻止自动继承。
>
> **用法要点**：① attrs包含未声明为props的属性（含class/style/事件），自动继承到根元素 ② v-bind=attrs透传给子组件 ③ inheritAttrs:false阻止自动继承 ④ 封装高阶组件（包装el-input）时常用，将attrs透传到内部原生元素

### 3.6 ref / expose — 父组件调用子组件方法

父组件通过 `ref` 获取子组件实例，调用子组件暴露的方法和属性。

#### 子组件暴露方法

```typescript
// 子组件
import { ref, defineExpose } from 'vue'

const count = ref(0)

function increment() {
  count.value++
}

function reset() {
  count.value = 0
}

// 暴露给父组件的属性和方法
defineExpose({
  count,
  increment,
  reset
})
```

#### 父组件获取子组件实例

```typescript
// 父组件
import { ref, onMounted } from 'vue'
import Child from './Child.vue'

// 获取子组件实例（需要标注类型）
const childRef = ref<InstanceType<typeof Child>>()

onMounted(() => {
  childRef.value?.increment()  // 调用子组件方法
  console.log(childRef.value?.count)  // 访问子组件属性
})
```


> 🔍 **知识点深度解析**
>
> **作用**：ref属性获取子组件实例，script setup中组件默认封闭，需defineExpose暴露数据/方法。
>
> **原理**：TS中用泛型ref<InstanceType<typeof Child>>()获取类型。
>
> **用法要点**：① ref属性获取子组件实例，script setup中组件默认封闭，需defineExpose暴露数据/方法 ② 父组件onMounted后才能访问ref（挂载前为null） ③ TS中用泛型ref<InstanceType<typeof Child>>()获取类型 ④ 耦合性强，优先用props/emit

### 3.7 组件通信方式总结

| 通信方式 | 方向 | 适用场景 | 类型安全 |
|---------|------|---------|---------|
| Props | 父 → 子 | 父子组件传值 | ✅ 泛型写法 |
| Emits | 子 → 父 | 子组件通知父组件 | ✅ 泛型写法 |
| v-model | 双向 | 表单类组件双向绑定 | ✅ |
| Provide/Inject | 祖先 → 后代 | 跨层级共享数据 | ⚠️ 需 InjectionKey |
| $attrs | 父 → 子 | 属性透传 | ❌ |
| ref/expose | 父 → 子 | 父组件调用子组件方法 | ✅ InstanceType |
| Pinia | 全局 | 跨组件状态共享 | ✅ |

---

## 第4章 插槽与动态组件


> 🔍 **知识点深度解析**
>
> **作用**：组件通信选型：父子用props+emit，双向绑定用v-model，跨层级用provide/inject，兄弟/任意用mitt或Pinia，全局状态用Pinia。
>
> **原理**：attrs用于属性透传，ref/expose用于父调用子方法。
>
> **用法要点**：① 组件通信选型：父子用props+emit，双向绑定用v-model，跨层级用provide/inject，兄弟/任意用mitt或Pinia，全局状态用Pinia ② attrs用于属性透传，ref/expose用于父调用子方法 ③ 根据场景选择，避免滥用ref/parent

### 4.1 插槽 Slots

插槽是 Vue 组件内容分发的机制，让父组件可以向子组件传入模板内容。

#### 默认插槽

```vue
<!-- 子组件：Card.vue -->
<template>
  <div class="card">
    <div class="card-header">
      <slot name="header">默认标题</slot>  <!-- 具名插槽 -->
    </div>
    <div class="card-body">
      <slot>默认内容</slot>  <!-- 默认插槽 -->
    </div>
  </div>
</template>
```

```vue
<!-- 父组件使用 -->
<Card>
  <template #header>
    <h2>自定义标题</h2>
  </template>
  <p>这是卡片内容</p>
</Card>
```

#### 具名插槽

```vue
<!-- 子组件 -->
<div class="layout">
  <header><slot name="header" /></header>
  <main><slot /></main>           <!-- 默认插槽 name 为 default -->
  <footer><slot name="footer" /></footer>
</div>
```

```vue
<!-- 父组件 -->
<BaseLayout>
  <template #header>
    <h1>页面标题</h1>
  </template>
  
  <p>主要内容</p>  <!-- 默认插槽内容 -->
  
  <template #footer>
    <p>© 2024</p>
  </template>
</BaseLayout>
```

#### 作用域插槽

作用域插槽让子组件可以向插槽传递数据，父组件可以访问子组件的数据。

```vue
<!-- 子组件：List.vue -->
<template>
  <ul>
    <li v-for="item in items" :key="item.id">
      <!-- 将 item 传递给插槽 -->
      <slot :item="item" :index="item.id">
        {{ item.name }}  <!-- 默认渲染 -->
      </slot>
    </li>
  </ul>
</template>

<script setup lang="ts">
interface ListItem {
  id: number
  name: string
}

defineProps<{
  items: ListItem[]
}>()
</script>
```

```vue
<!-- 父组件使用 -->
<List :items="userList">
  <template #default="{ item, index }">
    <!-- 自定义渲染方式 -->
    <div class="user-item">
      <span>{{ index }}.</span>
      <strong>{{ item.name }}</strong>
    </div>
  </template>
</List>
```

#### 作用域插槽类型定义

```typescript
// 子组件中定义插槽类型
defineSlots<{
  default(props: { item: ListItem; index: number }): void
  header(props: { title: string }): void
}>()
```


> 🔍 **知识点深度解析**
>
> **作用**：插槽是组件内容分发机制。
>
> **原理**：默认slot分发任意内容，具名slot name分发到指定位置（#xxx简写），作用域slot :data将子组件数据传给父（父决定渲染结构）。
>
> **用法要点**：① 插槽是组件内容分发机制 ② 默认slot分发任意内容，具名slot name分发到指定位置（#xxx简写），作用域slot :data将子组件数据传给父（父决定渲染结构） ③ 作用域插槽TS类型用defineSlots定义 ④ 是Vue组件复用的核心手段

### 4.2 动态组件

动态组件用于在同一个位置根据条件渲染不同的组件。

#### 基本用法

```vue
<template>
  <!-- 根据 currentTab 的值切换组件 -->
  <component :is="currentTab" />
</template>

<script setup lang="ts">
import { ref, markRaw } from 'vue'
import Home from './Home.vue'
import About from './About.vue'
import Contact from './Contact.vue'

// 使用 markRaw 避免不必要的响应式代理
const tabs = {
  home: markRaw(Home),
  about: markRaw(About),
  contact: markRaw(Contact)
}

const currentTab = ref(tabs.home)
</script>
```

#### 切换组件时传 props

```vue
<component
  :is="currentComponent"
  :prop1="value1"
  :prop2="value2"
  @event1="handleEvent"
/>
```


> 🔍 **知识点深度解析**
>
> **作用**：动态组件component :is=xxx根据is值切换组件。
>
> **原理**：切换时组件默认销毁重建，用keep-alive缓存。
>
> **用法要点**：① 动态组件component :is=xxx根据is值切换组件 ② is可传组件对象或字符串（注册名） ③ 切换时组件默认销毁重建，用keep-alive缓存 ④ 切换时可通过props传参 ⑤ 适合Tab切换、权限控制渲染等场景

### 4.3 keep-alive 缓存组件

`keep-alive` 用于缓存动态组件，避免重复创建和销毁，提升性能。

#### 基本用法

```vue
<keep-alive>
  <component :is="currentTab" />
</keep-alive>
```

#### include / exclude

```vue
<!-- 只缓存 name 为 Home 和 About 的组件 -->
<keep-alive include="Home,About">
  <component :is="currentTab" />
</keep-alive>

<!-- 不缓存 Contact 组件 -->
<keep-alive exclude="Contact">
  <component :is="currentTab" />
</keep-alive>
```

#### 最大缓存数量

```vue
<keep-alive :max="10">
  <component :is="currentTab" />
</keep-alive>
```

#### 激活/失活生命周期

```typescript
import { onActivated, onDeactivated } from 'vue'

onActivated(() => {
  // 组件被激活时调用
  // 常用于：重新获取数据、启动动画
})

onDeactivated(() => {
  // 组件失活时调用
  // 常用于：暂停定时器、取消请求
})
```

#### 配合 router-view 使用

```vue
<router-view v-slot="{ Component, route }">
  <transition name="fade" mode="out-in">
    <keep-alive :include="cachedViews">
      <component :is="Component" :key="route.fullPath" />
    </keep-alive>
  </transition>
</router-view>
```


> 🔍 **知识点深度解析**
>
> **作用**：keep-alive缓存组件实例（不销毁），include/exclude指定缓存组件名，max限制最大缓存数（LRU淘汰）。
>
> **原理**：缓存组件用onActivated/onDeactivated替代mounted/unmounted。
>
> **用法要点**：① keep-alive缓存组件实例（不销毁），include/exclude指定缓存组件名，max限制最大缓存数（LRU淘汰） ② 缓存组件用onActivated/onDeactivated替代mounted/unmounted ③ 配合router-view缓存页面 ④ 注意内存占用

### 4.4 Teleport 传送门

`Teleport` 可以将组件的 DOM 渲染到指定的目标元素中，不受父组件样式和层级限制。

#### 基本用法

```vue
<template>
  <button @click="showModal = true">打开弹窗</button>
  
  <!-- 将弹窗渲染到 body 下 -->
  <teleport to="body">
    <div v-if="showModal" class="modal">
      <div class="modal-content">
        <h2>弹窗标题</h2>
        <p>弹窗内容</p>
        <button @click="showModal = false">关闭</button>
      </div>
    </div>
  </teleport>
</template>
```

#### 常见使用场景

1. **模态框/对话框**：避免父级 `overflow: hidden` 或 `z-index` 限制
2. **全屏遮罩**：确保覆盖整个视口
3. **Tooltip/下拉菜单**：避免被父容器裁剪
4. **fixed 定位元素**：解决父级 `transform` 影响 fixed 定位的问题

#### 解决的典型问题

```css
/* 父级有 transform 会导致 fixed 定位失效 */
.parent {
  transform: translateZ(0);  /* 这会让子元素的 fixed 变成 relative */
}
```

使用 `Teleport` 将元素传送到 `body`，就可以避开这个问题。

---

## 第5章 自定义指令与全局属性


> 🔍 **知识点深度解析**
>
> **作用**：Teleport将HTML渲染到指定DOM位置（to=body或选择器），组件逻辑仍在当前树。
>
> **原理**：解决弹窗被父元素overflow:hidden/z-index遮挡。
>
> **用法要点**：① Teleport将HTML渲染到指定DOM位置（to=body或选择器），组件逻辑仍在当前树 ② 解决弹窗被父元素overflow:hidden/z-index遮挡 ③ 模态框/Toast/Tooltip常用 ④ disabled属性可禁用传送

### 5.1 自定义指令

自定义指令用于对普通 DOM 元素进行底层操作。

#### 指令钩子函数

```typescript
const myDirective = {
  // 在绑定元素的 attribute 前或事件监听器应用前调用
  created(el, binding, vnode, prevVnode) {},
  
  // 在元素被插入到 DOM 前调用
  beforeMount(el, binding) {},
  
  // 在绑定元素的父组件及他自己的所有子节点都挂载完成后调用
  mounted(el, binding) {},
  
  // 绑定元素的父组件更新前调用
  beforeUpdate(el, binding) {},
  
  // 在绑定元素的父组件及他自己的所有子节点都更新后调用
  updated(el, binding) {},
  
  // 绑定元素的父组件卸载前调用
  beforeUnmount(el, binding) {},
  
  // 绑定元素的父组件卸载后调用
  unmounted(el, binding) {}
}
```

#### 常用示例：v-focus

```typescript
// src/directives/focus.ts
import type { Directive } from 'vue'

const focus: Directive = {
  mounted(el: HTMLInputElement) {
    el.focus()
  }
}

export default focus
```

```typescript
// main.ts 全局注册
import { createApp } from 'vue'
import focus from '@/directives/focus'

const app = createApp(App)
app.directive('focus', focus)
```

```vue
<!-- 使用 -->
<input v-focus />
```

#### 常用示例：v-permission 权限指令

```typescript
// src/directives/permission.ts
import type { Directive, DirectiveBinding } from 'vue'
import { useUserStore } from '@/store/modules/user'

const permission: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding<string[]>) {
    const userStore = useUserStore()
    const requiredPermissions = binding.value
    const userPermissions = userStore.permissions
    
    // 检查用户是否拥有所需权限
    const hasPermission = requiredPermissions.some(
      perm => userPermissions.includes(perm)
    )
    
    if (!hasPermission) {
      el.parentNode?.removeChild(el)
    }
  }
}

export default permission
```

```vue
<!-- 使用 -->
<button v-permission="['user:delete']">删除用户</button>
```

#### 常用示例：v-lazy 图片懒加载

```typescript
// src/directives/lazy.ts
import type { Directive, DirectiveBinding } from 'vue'

const lazy: Directive = {
  mounted(el: HTMLImageElement, binding: DirectiveBinding<string>) {
    // 初始显示占位图
    el.src = 'placeholder.png'
    
    // 使用 IntersectionObserver 监听
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // 进入视口，加载真实图片
          el.src = binding.value
          observer.unobserve(el)
        }
      })
    })
    
    observer.observe(el)
  }
}

export default lazy
```

#### 批量注册指令

```typescript
// src/directives/index.ts
import type { App } from 'vue'
import focus from './focus'
import permission from './permission'
import lazy from './lazy'

const directives = {
  focus,
  permission,
  lazy
}

export default {
  install(app: App) {
    Object.keys(directives).forEach(key => {
      app.directive(key, directives[key as keyof typeof directives])
    })
  }
}
```

```typescript
// main.ts
import directives from '@/directives'
app.use(directives)
```


> 🔍 **知识点深度解析**
>
> **作用**：自定义指令有created/beforeMount/mounted/beforeUpdate/updated/beforeUnmount/unmounted钩子。
>
> **原理**：常用v-focus（自动聚焦）、v-permission（权限控制）、v-lazy（图片懒加载）。
>
> **用法要点**：① 自定义指令有created/beforeMount/mounted/beforeUpdate/updated/beforeUnmount/unmounted钩子 ② 局部directives注册，全局app.directive注册 ③ 常用v-focus（自动聚焦）、v-permission（权限控制）、v-lazy（图片懒加载） ④ 复杂逻辑优先用组件

### 5.2 全局属性挂载

通过 `app.config.globalProperties` 挂载全局属性和方法。

#### 基本用法

```typescript
// main.ts
import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App)

// 挂载全局属性
app.config.globalProperties.$api = api
app.config.globalProperties.$message = ElMessage
app.config.globalProperties.$formatDate = (date: Date) => {
  return date.toLocaleDateString()
}
```

#### TypeScript 类型扩展

```typescript
// src/types/global.d.ts
import { ComponentCustomProperties } from 'vue'
import type { Api } from '@/api'

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $api: Api
    $message: typeof ElMessage
    $formatDate: (date: Date) => string
  }
}
```

#### 在组件中使用

```typescript
import { getCurrentInstance } from 'vue'

const { proxy } = getCurrentInstance()!

// 访问全局属性
proxy?.$api.user.getUserList()
proxy?.$message.success('操作成功')
```

> **注意**：在 `<script setup>` 中推荐直接导入需要的函数，而不是通过 `globalProperties` 访问。全局属性更适合选项式 API。


> 🔍 **知识点深度解析**
>
> **作用**：app.config.globalProperties挂载全局属性（如axios/api），TS需扩展ComponentCustomProperties类型。
>
> **原理**：组件中getCurrentInstance().proxy访问。
>
> **用法要点**：① app.config.globalProperties挂载全局属性（如axios/api），TS需扩展ComponentCustomProperties类型 ② 组件中getCurrentInstance().proxy访问 ③ Vue3推荐用provide/inject或组合函数替代全局属性（更类型安全、可测试）

### 5.3 插件开发

插件是一种为 Vue 添加全局功能的方式。

#### 插件的类型

1. 添加全局方法或 property
2. 添加全局资源：指令/过滤器/过渡等
3. 通过全局注入来添加一些组件选项
4. 添加全局实例方法
5. 一个库，提供自己的 API

#### 插件开发示例

```typescript
// src/plugins/myPlugin.ts
import type { App } from 'vue'

interface PluginOptions {
  prefix?: string
}

export default {
  install(app: App, options: PluginOptions = {}) {
    const prefix = options.prefix || ''
    
    // 1. 添加全局方法
    app.config.globalProperties.$myMethod = (msg: string) => {
      console.log(prefix + msg)
    }
    
    // 2. 添加全局指令
    app.directive('my-directive', {
      mounted(el, binding) {
        el.textContent = prefix + binding.value
      }
    })
    
    // 3. 提供全局数据
    app.provide('pluginOptions', options)
  }
}
```

```typescript
// main.ts 使用插件
import myPlugin from '@/plugins/myPlugin'

app.use(myPlugin, { prefix: '[MyPlugin] ' })
```

---

# 第三篇：状态与路由篇

## 第6章 Pinia 状态管理

Pinia 是 Vue3 官方推荐的状态管理库，替代了 Vuex。它支持 TypeScript、组合式 API，且模块化设计更清晰。


> 🔍 **知识点深度解析**
>
> **作用**：插件是含install(app, options)的对象，app.use(plugin, options)安装。
>
> **原理**：自定义插件封装通用能力。
>
> **用法要点**：① 插件是含install(app, options)的对象，app.use(plugin, options)安装 ② 可注册全局组件、指令、挂载全局属性、provide全局数据 ③ Vue Router/Pinia/Element Plus都是插件 ④ 自定义插件封装通用能力

### 6.1 概述与安装

#### Pinia vs Vuex

| 特性 | Pinia | Vuex |
|------|-------|------|
| Vue3 支持 | ✅ 原生支持 | ⚠️ Vuex4 |
| TypeScript | ✅ 完美支持 | ⚠️ 配置复杂 |
| 组合式 API | ✅ 支持 | ❌ |
| Mutations | ❌ 不需要 | ✅ 必须 |
| 模块化 | ✅ 自动模块化 | ✅ 手动配置 |
| 体积 | 更小 | 较大 |
| DevTools | ✅ 支持 | ✅ 支持 |

#### 安装

```bash
pnpm add pinia
```

```typescript
// main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.mount('#app')
```


> 🔍 **知识点深度解析**
>
> **作用**：Pinia是Vue3官方状态管理（替代Vuex），TS支持完善，无mutations，支持Options和Setup两种Store风格。
>
> **原理**：createPinia()创建实例，app.use(pinia)安装。
>
> **用法要点**：① Pinia是Vue3官方状态管理（替代Vuex），TS支持完善，无mutations，支持Options和Setup两种Store风格 ② createPinia()创建实例，app.use(pinia)安装 ③ DevTools支持时间旅行 ④ 比Vuex更简洁、类型更安全

### 6.2 Store 定义

Pinia 支持两种定义 Store 的方式：选项式 API 和组合式 API。

#### 选项式写法

```typescript
// src/store/modules/counter.ts
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', {
  // State
  state: () => ({
    count: 0,
    name: '计数器'
  }),
  
  // Getters
  getters: {
    doubleCount: (state) => state.count * 2,
    doubleCountPlusOne(): number {
      return this.doubleCount + 1
    }
  },
  
  // Actions
  actions: {
    increment() {
      this.count++
    },
    decrement() {
      this.count--
    },
    async fetchCount() {
      // 支持异步操作
      const res = await fetch('/api/count')
      this.count = await res.json()
    }
  }
})
```

#### 组合式写法（推荐）

```typescript
// src/store/modules/counter.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCounterStore = defineStore('counter', () => {
  // State —— 用 ref 定义
  const count = ref(0)
  const name = ref('计数器')
  
  // Getters —— 用 computed 定义
  const doubleCount = computed(() => count.value * 2)
  
  // Actions —— 用普通函数定义
  function increment() {
    count.value++
  }
  
  function decrement() {
    count.value--
  }
  
  async function fetchCount() {
    const res = await fetch('/api/count')
    count.value = await res.json()
  }
  
  // 必须 return 出去
  return {
    count,
    name,
    doubleCount,
    increment,
    decrement,
    fetchCount
  }
})
```


> 🔍 **知识点深度解析**
>
> **作用**：defineStore(id, options)定义Store，id唯一标识。
>
> **原理**：useXxxStore()获取单例（首次调用创建）。
>
> **用法要点**：① defineStore(id, options)定义Store，id唯一标识 ② Options风格：state函数、getters、actions ③ Setup风格：ref/reactive/computed/函数 ④ useXxxStore()获取单例（首次调用创建） ⑤ 推荐Setup风格（TS类型自动推导）

### 6.3 State 操作

#### 读取 State

```typescript
import { useCounterStore } from '@/store/modules/counter'

const counterStore = useCounterStore()

// 直接读取
console.log(counterStore.count)
```

#### 修改 State

```typescript
// 方式1：直接修改
counterStore.count++

// 方式2：$patch 批量修改
counterStore.$patch({
  count: 10,
  name: '新名称'
})

// 方式3：$patch 函数式（适合数组操作）
counterStore.$patch((state) => {
  state.items.push({ name: '新物品' })
  state.count++
})

// 方式4：$state 整体替换
counterStore.$state = { count: 100, name: '替换后' }

// 方式5：通过 action 修改（推荐，逻辑更清晰）
counterStore.increment()
```

#### 重置 State

```typescript
// 重置到初始状态
counterStore.$reset()
```


> 🔍 **知识点深度解析**
>
> **作用**：State操作三种方式：直接修改store.xxx=yyy；。
>
> **原理**：patch批量修改（对象/函数，减少更新）；。
>
> **用法要点**：① State操作三种方式：直接修改store.xxx=yyy ② patch批量修改（对象/函数，减少更新） ③ actions封装业务逻辑（推荐，可异步） ④ state必须是函数（避免实例共享） ⑤ 复杂业务用actions，简单修改直接赋值

### 6.4 storeToRefs 解构

直接从 store 解构会丢失响应式，需要用 `storeToRefs` 保持响应式。

```typescript
import { storeToRefs } from 'pinia'
import { useCounterStore } from '@/store/modules/counter'

const counterStore = useCounterStore()

// ❌ 错误：解构后丢失响应式
const { count, doubleCount } = counterStore

// ✅ 正确：保持响应式
const { count, doubleCount } = storeToRefs(counterStore)

// 方法可以直接解构，不需要 storeToRefs
const { increment, decrement } = counterStore
```


> 🔍 **知识点深度解析**
>
> **作用**：storeToRefs将state/getters转为ref（解构保持响应式），只转数据不转actions（actions可直接解构）。
>
> **原理**：类似Vue的toRefs但更精准。
>
> **用法要点**：① storeToRefs将state/getters转为ref（解构保持响应式），只转数据不转actions（actions可直接解构） ② 类似Vue的toRefs但更精准 ③ 模板中直接用解构后的变量，不需store.xxx前缀

### 6.5 Getters

Getters 相当于 store 的计算属性，具有缓存特性。

```typescript
export const useUserStore = defineStore('user', () => {
  const users = ref<User[]>([])
  
  // 基本 getter
  const userCount = computed(() => users.value.length)
  
  // 带参数的 getter（返回函数）
  const getUserById = computed(() => {
    return (id: number) => users.value.find(u => u.id === id)
  })
  
  // 访问其他 getter
  const activeUserCount = computed(() => {
    return users.value.filter(u => u.active).length
  })
  
  return { users, userCount, getUserById, activeUserCount }
})
```

```typescript
// 使用
const userStore = useUserStore()
console.log(userStore.userCount)        // 直接访问
console.log(userStore.getUserById(1))   // 带参数访问
```


> 🔍 **知识点深度解析**
>
> **作用**：getters是计算属性（基于state派生，有缓存）。
>
> **原理**：Options风格接收state参数，this指向store（可访问其他getter）。
>
> **用法要点**：① getters是计算属性（基于state派生，有缓存） ② Options风格接收state参数，this指向store（可访问其他getter） ③ Setup风格用computed ④ 适合总价、过滤列表、格式化等派生数据 ⑤ 组件中用storeToRefs解构

### 6.6 Actions

Actions 用于修改 state 和处理业务逻辑，支持同步和异步。

```typescript
export const useUserStore = defineStore('user', () => {
  const userList = ref<User[]>([])
  const loading = ref(false)
  
  // 同步 action
  function addUser(user: User) {
    userList.value.push(user)
  }
  
  // 异步 action
  async function fetchUsers() {
    loading.value = true
    try {
      const res = await api.user.getUserList()
      userList.value = res.data.list
    } finally {
      loading.value = false
    }
  }
  
  // 调用其他 action
  async function refreshUsers() {
    await fetchUsers()
    console.log('刷新完成')
  }
  
  return { userList, loading, addUser, fetchUsers, refreshUsers }
})
```


> 🔍 **知识点深度解析**
>
> **作用**：actions封装业务逻辑，可同步/异步（发请求）。
>
> **原理**：不要在组件中散落复杂修改逻辑。
>
> **用法要点**：① actions封装业务逻辑，可同步/异步（发请求） ② Options风格this指向store，Setup风格直接访问ref ③ 是修改state的推荐方式（集中管理、可复用、可测试） ④ 不要在组件中散落复杂修改逻辑

### 6.7 $subscribe 数据持久化

监听 state 的变化，常用于数据持久化到 localStorage。

```typescript
import { useUserStore } from '@/store/modules/user'

const userStore = useUserStore()

// 订阅 state 变化
userStore.$subscribe((mutation, state) => {
  // mutation.type: 'direct' | 'patch object' | 'patch function'
  // 将 state 保存到 localStorage
  localStorage.setItem('user-store', JSON.stringify(state))
}, {
  detached: true,  // 组件卸载后继续监听
  deep: true       // 深度监听
})
```

#### 封装持久化插件

```typescript
// src/store/plugins/persist.ts
import type { PiniaPluginContext } from 'pinia'

export function persistPlugin({ store }: PiniaPluginContext) {
  // 从 localStorage 恢复
  const saved = localStorage.getItem(`pinia-${store.$id}`)
  if (saved) {
    store.$patch(JSON.parse(saved))
  }
  
  // 订阅变化并保存
  store.$subscribe((_, state) => {
    localStorage.setItem(`pinia-${store.$id}`, JSON.stringify(state))
  })
}
```

```typescript
// main.ts
import { createPinia } from 'pinia'
import { persistPlugin } from '@/store/plugins/persist'

const pinia = createPinia()
pinia.use(persistPlugin)
```


> 🔍 **知识点深度解析**
>
> **作用**：subscribe监听state变化，回调接收mutation（type/storeId/events）和state。
>
> **原理**：比watch更适合监听整个store。
>
> **用法要点**：① subscribe监听state变化，回调接收mutation（type/storeId/events）和state ② 用于持久化（变化时存localStorage）、日志、审计 ③ detached:true组件卸载不停止 ④ 比watch更适合监听整个store ⑤ pinia-plugin-persistedstate可自动持久化

### 6.8 Store 模块化

Pinia 天然支持模块化，每个 store 都是独立的模块。

#### 目录结构

```
src/
├── store/
│   ├── index.ts          # Pinia 入口
│   ├── modules/          # 各模块 store
│   │   ├── user.ts       # 用户模块
│   │   ├── app.ts        # 应用配置模块
│   │   ├── permission.ts # 权限模块
│   │   └── tagsView.ts   # 标签页模块
```

#### 模块间互相调用

```typescript
// src/store/modules/permission.ts
import { defineStore } from 'pinia'
import { useUserStore } from './user'

export const usePermissionStore = defineStore('permission', () => {
  const routes = ref<RouteRecordRaw[]>([])
  
  async function generateRoutes() {
    const userStore = useUserStore()  // 调用其他 store
    const roles = userStore.roles
    // 根据角色生成路由...
    routes.value = filterAsyncRoutes(asyncRoutes, roles)
  }
  
  return { routes, generateRoutes }
})
```

---

## 第7章 Vue Router 路由

Vue Router 是 Vue.js 的官方路由管理器，与 Vue3 核心深度集成。


> 🔍 **知识点深度解析**
>
> **作用**：Store模块化按功能拆分（userStore/cartStore/appStore），每个Store独立。
>
> **原理**：Store间可互相调用（import其他useStore）。
>
> **用法要点**：① Store模块化按功能拆分（userStore/cartStore/appStore），每个Store独立 ② 不需要Vuex的modules嵌套 ③ Store间可互相调用（import其他useStore） ④ 按业务领域划分，保持单一职责

### 7.1 基础配置

#### 安装

```bash
pnpm add vue-router
```

#### 创建路由实例

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/home/index.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/about/index.vue'),
    meta: { title: '关于' }
  },
  {
    path: '/:pathMatch(.*)*',  // 404 路由
    name: 'NotFound',
    component: () => import('@/views/error/404.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),  // HTML5 模式
  routes,
  scrollBehavior: () => ({ top: 0 })  // 滚动行为
})

export default router
```

#### 路由模式

| 模式 | 创建函数 | URL 形式 | 特点 |
|------|---------|---------|------|
| HTML5 模式 | `createWebHistory()` | `/home` | 美观，需后端配置 |
| Hash 模式 | `createWebHashHistory()` | `/#/home` | 兼容性好，丑 |
| 内存模式 | `createMemoryHistory()` | 无 URL | SSR 用 |

#### 注册路由

```typescript
// main.ts
import { createApp } from 'vue'
import router from './router'
import App from './App.vue'

const app = createApp(App)
app.use(router)
app.mount('#app')
```


> 🔍 **知识点深度解析**
>
> **作用**：createRouter创建路由实例，history模式（createWebHistory，URL美观需服务端配置）或hash模式（createWebHashHistory，兼容性好）。
>
> **原理**：routes配置path/component。
>
> **用法要点**：① createRouter创建路由实例，history模式（createWebHistory，URL美观需服务端配置）或hash模式（createWebHashHistory，兼容性好） ② routes配置path/component ③ app.use(router)安装 ④ RouterLink导航，RouterView显示 ⑤ 4.x支持TS类型

### 7.2 路由传参

#### 动态路由参数

```typescript
// 路由配置
const routes = [
  {
    path: '/user/:id',
    name: 'User',
    component: () => import('@/views/user/index.vue')
  }
]
```

```typescript
// 组件中获取参数
import { useRoute } from 'vue-router'

const route = useRoute()
console.log(route.params.id)  // 动态参数
```

#### Query 参数

```typescript
// 跳转时传参
import { useRouter } from 'vue-router'

const router = useRouter()

// 方式1：字符串路径
router.push('/user?id=1&name=张三')

// 方式2：对象形式
router.push({
  path: '/user',
  query: { id: 1, name: '张三' }
})
```

```typescript
// 组件中获取 query
import { useRoute } from 'vue-router'

const route = useRoute()
console.log(route.query.id)
console.log(route.query.name)
```

#### Params 传参（命名路由）

```typescript
// 方式1：命名路由 + params
router.push({
  name: 'User',
  params: { id: 1 }
})

// 方式2：路径拼接
router.push({
  path: '/user/1'
})
```

> **注意**：`params` 只能与 `name` 配合使用，不能与 `path` 一起用。

#### Props 传参（推荐）

```typescript
// 路由配置：开启 props
const routes = [
  {
    path: '/user/:id',
    name: 'User',
    component: () => import('@/views/user/index.vue'),
    props: true  // 将 params 转为 props
  }
]
```

```vue
<!-- 组件中通过 props 接收 -->
<script setup lang="ts">
const props = defineProps<{
  id: string
}>()

console.log(props.id)
</script>
```


> 🔍 **知识点深度解析**
>
> **作用**：query参数在URL?后（/detail?id=1），route.query接收，可选参数。
>
> **原理**：params参数在路径中（/detail/1），需路由占位:id，route.params接收，必填标识。
>
> **用法要点**：① query参数在URL?后（/detail?id=1），route.query接收，可选参数 ② params参数在路径中（/detail/1），需路由占位:id，route.params接收，必填标识 ③ params对象写法必须用name（不能用path） ④ 路由props配置可将参数转组件props

### 7.3 编程式导航

```typescript
import { useRouter } from 'vue-router'

const router = useRouter()

// 跳转到新页面（添加历史记录）
router.push('/home')
router.push({ name: 'Home' })
router.push({ path: '/home', query: { id: 1 } })

// 替换当前页面（不添加历史记录）
router.replace('/home')

// 前进/后退
router.go(1)    // 前进一步
router.go(-1)   // 后退一步
router.back()   // 后退（等价于 go(-1)）
router.forward() // 前进（等价于 go(1)）
```


> 🔍 **知识点深度解析**
>
> **作用**：useRouter获取router实例，push/replace/go编程式跳转。
>
> **原理**：useRoute获取当前路由信息。
>
> **用法要点**：① useRouter获取router实例，push/replace/go编程式跳转 ② useRoute获取当前路由信息 ③ push返回Promise可await（捕获导航失败） ④ replace不留下历史记录 ⑤ 适合按钮点击、逻辑判断后跳转

### 7.4 嵌套路由

```typescript
const routes = [
  {
    path: '/user',
    component: () => import('@/views/user/layout.vue'),
    children: [
      {
        path: '',           // /user
        name: 'UserIndex',
        component: () => import('@/views/user/index.vue')
      },
      {
        path: 'profile',    // /user/profile
        name: 'UserProfile',
        component: () => import('@/views/user/profile.vue')
      },
      {
        path: 'settings',   // /user/settings
        name: 'UserSettings',
        component: () => import('@/views/user/settings.vue')
      }
    ]
  }
]
```

```vue
<!-- 父组件中需要 router-view -->
<template>
  <div class="user-layout">
    <nav>
      <router-link to="/user">首页</router-link>
      <router-link to="/user/profile">资料</router-link>
      <router-link to="/user/settings">设置</router-link>
    </nav>
    <router-view />
  </div>
</template>
```


> 🔍 **知识点深度解析**
>
> **作用**：嵌套路由用children配置，子路径不加/（相对路径）。
>
> **原理**：跳转用完整路径或命名路由。
>
> **用法要点**：① 嵌套路由用children配置，子路径不加/（相对路径） ② 父组件预留RouterView显示子组件 ③ 跳转用完整路径或命名路由 ④ 适合列表+详情、布局+内容的嵌套结构 ⑤ 子路由默认path为空时显示默认子路由

### 7.5 路由元信息 meta

#### 类型扩展

```typescript
// src/router/types.ts
import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string          // 页面标题
    icon?: string           // 菜单图标
    hidden?: boolean        // 是否隐藏菜单
    keepAlive?: boolean     // 是否缓存
    requiresAuth?: boolean  // 是否需要登录
    roles?: string[]        // 角色权限
    breadcrumb?: boolean    // 是否显示面包屑
    affix?: boolean         // 是否固定标签页
  }
}
```

#### 使用 meta

```typescript
const routes = [
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/dashboard/index.vue'),
    meta: {
      title: '仪表盘',
      icon: 'HomeFilled',
      requiresAuth: true,
      keepAlive: true,
      affix: true
    }
  }
]
```

```typescript
// 组件中访问 meta
import { useRoute } from 'vue-router'

const route = useRoute()
console.log(route.meta.title)
```


> 🔍 **知识点深度解析**
>
> **作用**：meta路由元信息存储自定义数据（title/requiresAuth/icon/roles），route.meta访问。
>
> **原理**：常用于权限控制（requiresAuth）、页面标题（document.title）、面包屑、过渡动画。
>
> **用法要点**：① meta路由元信息存储自定义数据（title/requiresAuth/icon/roles），route.meta访问 ② 常用于权限控制（requiresAuth）、页面标题（document.title）、面包屑、过渡动画 ③ TS扩展RouteMeta类型

### 7.6 导航守卫

导航守卫用于控制路由的跳转，常用于权限验证、页面标题设置等。

#### 全局前置守卫

```typescript
import router from './router'
import { useUserStore } from '@/store/modules/user'

// 白名单
const whiteList = ['/login', '/404']

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const token = userStore.token
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 后台管理` : '后台管理'
  
  // 有 token
  if (token) {
    if (to.path === '/login') {
      // 已登录访问登录页，跳首页
      next('/')
    } else {
      // 检查是否有用户信息
      if (!userStore.userInfo) {
        try {
          await userStore.getUserInfo()
          next({ ...to, replace: true })
        } catch (error) {
          // 获取用户信息失败，清除 token 跳登录
          userStore.resetToken()
          next(`/login?redirect=${to.path}`)
        }
      } else {
        next()
      }
    }
  } else {
    // 无 token
    if (whiteList.includes(to.path)) {
      next()  // 白名单直接放行
    } else {
      next(`/login?redirect=${to.path}`)  // 否则跳登录
    }
  }
})
```

#### 全局解析守卫

```typescript
router.beforeResolve((to, from) => {
  // 在导航被确认之前，所有组件内守卫和异步路由组件被解析之后调用
})
```

#### 全局后置钩子

```typescript
router.afterEach((to, from) => {
  // 导航完成后调用，没有 next 函数
  // 常用于：页面埋点、滚动到顶部
  window.scrollTo(0, 0)
})
```

#### 路由独享守卫

```typescript
const routes = [
  {
    path: '/admin',
    component: () => import('@/views/admin/index.vue'),
    beforeEnter: (to, from, next) => {
      // 只在进入这个路由时触发
      if (isAdmin()) {
        next()
      } else {
        next('/403')
      }
    }
  }
]
```

#### 组件内守卫

```typescript
import { onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'

// 离开当前路由前
onBeforeRouteLeave((to, from) => {
  // 常用于：提示未保存的修改
  if (hasUnsavedChanges.value) {
    return confirm('有未保存的修改，确定要离开吗？')
  }
})

// 路由更新但组件复用时
onBeforeRouteUpdate((to, from) => {
  // 常用于：同一个组件不同参数时重新获取数据
  fetchData(to.params.id)
})
```


> 🔍 **知识点深度解析**
>
> **作用**：导航守卫控制路由跳转：全局beforeEach（权限校验）、beforeResolve、afterEach；。
>
> **原理**：路由独享beforeEnter；。
>
> **用法要点**：① 导航守卫控制路由跳转：全局beforeEach（权限校验）、beforeResolve、afterEach ② 路由独享beforeEnter ③ 组件内beforeRouteEnter/Update/Leave ④ next()继续，next(false)取消，next(path)重定向 ⑤ 权限系统核心 ⑥ 返回Promise替代next

### 7.7 动态路由

动态路由用于根据用户权限动态添加路由。

#### 添加路由

```typescript
import router from './router'

// 添加单个路由
router.addRoute({
  path: '/new-page',
  name: 'NewPage',
  component: () => import('@/views/new-page/index.vue')
})

// 添加嵌套路由（第一个参数是父路由的 name）
router.addRoute('Parent', {
  path: 'child',
  name: 'Child',
  component: () => import('@/views/child.vue')
})
```

#### 移除路由

```typescript
// 按 name 移除
router.removeRoute('RouteName')

// 添加一个同名路由会覆盖旧的
router.addRoute({ path: '/about', name: 'About', component: A })
router.addRoute({ path: '/about', name: 'About', component: B })  // 覆盖
```

#### 检查路由是否存在

```typescript
// 检查是否有某个 name 的路由
router.hasRoute('RouteName')

// 获取所有路由记录
router.getRoutes()
```

#### 权限路由完整示例

```typescript
// src/store/modules/permission.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import router, { asyncRoutes, constantRoutes } from '@/router'

export const usePermissionStore = defineStore('permission', () => {
  const routes = ref<RouteRecordRaw[]>([])
  const addRoutes = ref<RouteRecordRaw[]>([])
  
  // 根据角色过滤路由
  function filterAsyncRoutes(routes: RouteRecordRaw[], roles: string[]) {
    const res: RouteRecordRaw[] = []
    routes.forEach(route => {
      const tmp = { ...route }
      if (hasPermission(roles, tmp)) {
        if (tmp.children) {
          tmp.children = filterAsyncRoutes(tmp.children, roles)
        }
        res.push(tmp)
      }
    })
    return res
  }
  
  function hasPermission(roles: string[], route: RouteRecordRaw) {
    if (route.meta?.roles) {
      return roles.some(role => route.meta!.roles!.includes(role))
    }
    return true
  }
  
  // 生成路由
  async function generateRoutes(roles: string[]) {
    let accessedRoutes
    if (roles.includes('admin')) {
      accessedRoutes = asyncRoutes
    } else {
      accessedRoutes = filterAsyncRoutes(asyncRoutes, roles)
    }
    
    addRoutes.value = accessedRoutes
    routes.value = constantRoutes.concat(accessedRoutes)
    
    // 动态添加路由
    accessedRoutes.forEach(route => {
      router.addRoute(route)
    })
    
    return accessedRoutes
  }
  
  return { routes, addRoutes, generateRoutes }
})
```

---

# 第四篇：工程化基础篇

## 第8章 项目工程化配置


> 🔍 **知识点深度解析**
>
> **作用**：动态路由router.addRoute()运行时添加路由（权限系统根据用户角色动态注册菜单路由）。
>
> **原理**：常用于后端返回权限菜单，前端动态生成路由。
>
> **用法要点**：① 动态路由router.addRoute()运行时添加路由（权限系统根据用户角色动态注册菜单路由） ② removeRoute删除 ③ 常用于后端返回权限菜单，前端动态生成路由 ④ 刷新后需重新添加（在路由守卫中判断）

### 8.1 Vite 配置

Vite 是新一代前端构建工具，基于原生 ES 模块，开发服务器启动极快。

#### 基础配置

```typescript
// vite.config.ts
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd())
  
  return {
    plugins: [vue()],
    
    // 路径别名
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    },
    
    // 开发服务器配置
    server: {
      host: '0.0.0.0',
      port: 3000,
      open: true,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    },
    
    // 构建配置
    build: {
      outDir: 'dist',
      sourcemap: false,
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: true,   // 生产环境移除 console
          drop_debugger: true   // 移除 debugger
        }
      },
      rollupOptions: {
        output: {
          // 静态资源分类打包
          chunkFileNames: 'static/js/[name]-[hash].js',
          entryFileNames: 'static/js/[name]-[hash].js',
          assetFileNames: 'static/[ext]/[name]-[hash].[ext]',
          // 手动分包
          manualChunks: {
            vue: ['vue', 'vue-router', 'pinia'],
            elementPlus: ['element-plus'],
            echarts: ['echarts']
          }
        }
      }
    }
  }
})
```

#### 常用插件

| 插件 | 用途 |
|------|------|
| `@vitejs/plugin-vue` | Vue3 支持 |
| `@vitejs/plugin-vue-jsx` | JSX 支持 |
| `unplugin-vue-components` | 组件自动导入 |
| `unplugin-auto-import` | API 自动导入 |
| `vite-plugin-mock` | Mock 数据 |
| `vite-plugin-compression` | gzip 压缩 |
| `vite-plugin-imagemin` | 图片压缩 |


> 🔍 **知识点深度解析**
>
> **作用**：Vite配置vite.config.ts，plugins注册插件（@vitejs/plugin-vue、VueSetupExtend等），resolve.alias路径别名，server代理，build构建配置。
>
> **原理**：defineConfig提供TS类型提示。
>
> **用法要点**：① Vite配置vite.config.ts，plugins注册插件（@vitejs/plugin-vue、VueSetupExtend等），resolve.alias路径别名，server代理，build构建配置 ② defineConfig提供TS类型提示 ③ 比webpack配置简洁，启动快

### 8.2 环境变量

#### 环境变量文件

```
.env                # 所有环境加载
.env.development    # 开发环境
.env.production     # 生产环境
.env.test           # 测试环境
```

#### 定义环境变量

```bash
# .env.development
VITE_APP_TITLE = 开发环境
VITE_API_BASE_URL = http://localhost:3000/api
VITE_USE_MOCK = true
```

> **注意**：只有以 `VITE_` 开头的变量才会暴露到客户端代码中。

#### 使用环境变量

```typescript
// 在代码中使用
console.log(import.meta.env.VITE_API_BASE_URL)
console.log(import.meta.env.MODE)        // 模式：development/production
console.log(import.meta.env.DEV)         // 是否开发环境
console.log(import.meta.env.PROD)        // 是否生产环境
```

#### TypeScript 类型提示

```typescript
// src/env.d.ts
interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string
  readonly VITE_API_BASE_URL: string
  readonly VITE_USE_MOCK: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```


> 🔍 **知识点深度解析**
>
> **作用**：环境变量.env.development/.env.production，VITE_前缀暴露给客户端。
>
> **原理**：可创建.env.[mode]自定义模式。
>
> **用法要点**：① 环境变量.env.development/.env.production，VITE_前缀暴露给客户端 ② import.meta.env访问 ③ 自定义变量需VITE_前缀 ④ 可创建.env.[mode]自定义模式 ⑤ 区分API地址、功能开关等 ⑥ 类型在env.d.ts中扩展ImportMetaEnv

### 8.3 项目目录结构

```
src/
├── api/                  # API 接口
│   ├── index.ts
│   └── modules/
├── assets/               # 静态资源
│   ├── images/
│   ├── icons/
│   └── fonts/
├── components/           # 公共组件
│   ├── common/
│   └── business/
├── composables/          # 组合式函数 (Hooks)
│   ├── useRequest.ts
│   └── useTable.ts
├── directives/           # 自定义指令
│   ├── index.ts
│   └── permission.ts
├── hooks/                # 通用 Hooks
│   ├── useDebounce.ts
│   └── useThrottle.ts
├── layout/               # 布局组件
│   ├── index.vue
│   └── components/
├── plugins/              # 插件
│   └── index.ts
├── router/               # 路由
│   ├── index.ts
│   ├── modules/
│   └── types.ts
├── store/                # 状态管理
│   ├── index.ts
│   ├── modules/
│   └── plugins/
├── styles/               # 样式
│   ├── index.scss
│   ├── variables.scss
│   ├── mixins.scss
│   └── reset.scss
├── utils/                # 工具函数
│   ├── request.ts
│   ├── validate.ts
│   ├── storage.ts
│   └── date.ts
├── types/                # 类型定义
│   ├── global.d.ts
│   └── api.d.ts
├── views/                # 页面
│   ├── login/
│   ├── dashboard/
│   └── error/
├── App.vue
└── main.ts
```


> 🔍 **知识点深度解析**
>
> **作用**：标准目录：src/api（接口）、components（通用组件）、views/pages（页面）、router（路由）、store（Pinia）、utils（工具）、types（类型）、styles（样式）、assets（静态资源）。
>
> **原理**：按功能组织优于按类型组织（大型项目）。
>
> **用法要点**：① 标准目录：src/api（接口）、components（通用组件）、views/pages（页面）、router（路由）、store（Pinia）、utils（工具）、types（类型）、styles（样式）、assets（静态资源） ② 按功能组织优于按类型组织（大型项目）

### 8.4 类型定义文件

#### 全局类型

```typescript
// src/types/global.d.ts

// 通用响应类型
interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页响应类型
interface PageResponse<T = any> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

// 分页参数
interface PageParams {
  page: number
  pageSize: number
  keyword?: string
}
```

#### 模块类型

```typescript
// src/types/user.d.ts
interface User {
  id: number
  username: string
  email: string
  avatar?: string
  role: string
  status: number
  createTime: string
}

interface LoginParams {
  username: string
  password: string
}

interface LoginResult {
  token: string
  userInfo: User
}
```


> 🔍 **知识点深度解析**
>
> **作用**：类型定义文件.d.ts存放全局类型、第三方库类型扩展、API响应类型。
>
> **原理**：declare module声明模块类型。
>
> **用法要点**：① 类型定义文件.d.ts存放全局类型、第三方库类型扩展、API响应类型 ② declare module声明模块类型 ③ Vue的env.d.ts声明*.vue模块和ImportMetaEnv ④ 类型集中管理，import type导入 ⑤ 避免any

### 8.5 路径别名配置

#### Vite 配置

```typescript
// vite.config.ts
import path from 'path'

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  }
})
```

#### TypeScript 配置

```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

---

## 第9章 代码规范与 Git 工作流


> 🔍 **知识点深度解析**
>
> **作用**：路径别名@指向src，vite.config.ts中resolve.alias配置，tsconfig.json中paths同步配置（IDE识别）。
>
> **原理**：简化导入路径（@/components/xxx），避免相对路径地狱。
>
> **用法要点**：① 路径别名@指向src，vite.config.ts中resolve.alias配置，tsconfig.json中paths同步配置（IDE识别） ② 简化导入路径（@/components/xxx），避免相对路径地狱 ③ 必须两处都配置才生效

### 9.1 ESLint 配置

ESLint 用于检查代码质量和风格问题。

#### 安装依赖

```bash
pnpm add -D eslint eslint-plugin-vue @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

#### 配置文件

```javascript
// .eslintrc.cjs
module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
    es2021: true
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended',
    'plugin:@typescript-eslint/recommended'
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  rules: {
    // Vue 规则
    'vue/multi-word-component-names': 'off',
    'vue/no-v-html': 'off',
    
    // TypeScript 规则
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    
    // 通用规则
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'prefer-const': 'error',
    'no-var': 'error'
  }
}
```


> 🔍 **知识点深度解析**
>
> **作用**：ESLint代码质量检查，.eslintrc配置规则。
>
> **原理**：Vue3用eslint-plugin-vue，TS用@typescript-eslint。
>
> **用法要点**：① ESLint代码质量检查，.eslintrc配置规则 ② Vue3用eslint-plugin-vue，TS用@typescript-eslint ③ extends推荐配置 ④ prettier集成用eslint-config-prettier关闭冲突规则 ⑤ 保存自动修复 ⑥ 提前发现bug和不规范代码

### 9.2 Prettier 配置

Prettier 用于统一代码格式。

#### 安装依赖

```bash
pnpm add -D prettier eslint-config-prettier eslint-plugin-prettier
```

#### 配置文件

```json
// .prettierrc
{
  "semi": false,
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "trailingComma": "none",
  "bracketSpacing": true,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

```javascript
// .eslintrc.cjs 中添加
module.exports = {
  extends: [
    // ...
    'plugin:prettier/recommended'  // 放在最后
  ],
  rules: {
    'prettier/prettier': 'error'
  }
}
```


> 🔍 **知识点深度解析**
>
> **作用**：Prettier代码格式化，.prettierrc配置（printWidth/semi/singleQuote/tabWidth等）。
>
> **原理**：与ESLint配合：ESLint管质量，Prettier管格式。
>
> **用法要点**：① Prettier代码格式化，.prettierrc配置（printWidth/semi/singleQuote/tabWidth等） ② 与ESLint配合：ESLint管质量，Prettier管格式 ③ 保存自动格式化 ④ 团队统一代码风格，减少格式争论

### 9.3 Husky 配置

Husky 用于管理 Git hooks，在提交代码前自动执行检查。

#### 安装与初始化

```bash
# 安装
pnpm add -D husky

# 初始化
npx husky install

# 添加 prepare 脚本（package.json）
# "prepare": "husky install"
```

#### pre-commit 钩子

```bash
# 创建 pre-commit 钩子
npx husky add .husky/pre-commit "npx lint-staged"
```

```bash
# .husky/pre-commit
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx lint-staged
```

#### commit-msg 钩子

```bash
# 创建 commit-msg 钩子
npx husky add .husky/commit-msg 'npx --no -- commitlint --edit "$1"'
```

```bash
# .husky/commit-msg
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx --no -- commitlint --edit "$1"
```


> 🔍 **知识点深度解析**
>
> **作用**：Husky Git钩子，pre-commit提交前运行lint-staged，commit-msg运行commitlint。
>
> **原理**：.husky目录存放钩子脚本。
>
> **用法要点**：① Husky Git钩子，pre-commit提交前运行lint-staged，commit-msg运行commitlint ② .husky目录存放钩子脚本 ③ 安装后自动创建.git/hooks ④ 确保提交代码符合规范 ⑤ npx husky install初始化，prepare脚本自动安装

### 9.4 CommitLint 配置

CommitLint 用于规范 Git 提交信息格式。

#### 安装依赖

```bash
pnpm add -D @commitlint/cli @commitlint/config-conventional
```

#### 配置文件

```javascript
// commitlint.config.cjs
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',      // 新功能
        'fix',       // 修复 bug
        'docs',      // 文档更新
        'style',     // 代码格式（不影响功能）
        'refactor',  // 代码重构
        'perf',      // 性能优化
        'test',      // 测试相关
        'chore',     // 构建/工具变动
        'revert',    // 回滚
        'build',     // 构建相关
        'ci'         // CI/CD 相关
      ]
    ],
    'subject-case': [0],     // 主题大小写不限制
    'subject-full-stop': [0], // 主题结尾不需要句号
    'type-case': [0]          // type 大小写不限制
  }
}
```

#### Commit 规范详解

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

**type 类型说明**：

| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | `feat: 添加用户登录功能` |
| fix | 修复 bug | `fix: 修复列表分页错误` |
| docs | 文档更新 | `docs: 更新 README 说明` |
| style | 代码格式 | `style: 统一代码缩进` |
| refactor | 代码重构 | `refactor: 重构请求封装` |
| perf | 性能优化 | `perf: 优化列表渲染性能` |
| test | 测试相关 | `test: 添加单元测试` |
| chore | 构建/工具 | `chore: 更新依赖版本` |


> 🔍 **知识点深度解析**
>
> **作用**：CommitLint校验commit message格式，Conventional Commits规范（feat/fix/docs/style/refactor/perf/test/chore + scope + subject）。
>
> **原理**：配合Husky的commit-msg钩子。
>
> **用法要点**：① CommitLint校验commit message格式，Conventional Commits规范（feat/fix/docs/style/refactor/perf/test/chore + scope + subject） ② commitlint.config.js配置 ③ 配合Husky的commit-msg钩子 ④ 规范提交历史，便于生成changelog和版本管理

### 9.5 lint-staged 配置

lint-staged 只对暂存区的文件执行检查，提高提交速度。

#### 安装依赖

```bash
pnpm add -D lint-staged
```

#### 配置文件

```json
// .lintstagedrc
{
  "*.{js,ts,vue}": [
    "eslint --fix",
    "prettier --write"
  ],
  "*.{css,scss,less}": [
    "prettier --write"
  ],
  "*.{json,md}": [
    "prettier --write"
  ]
}
```


> 🔍 **知识点深度解析**
>
> **作用**：lint-staged只对暂存区（git add）的文件运行lint，速度快。
>
> **原理**：.lintstagedrc配置（*.{js,ts,vue}: eslint --fix，*.{css,md}: prettier --write）。
>
> **用法要点**：① lint-staged只对暂存区（git add）的文件运行lint，速度快 ② .lintstagedrc配置（*.{js,ts,vue}: eslint --fix，*.{css,md}: prettier --write） ③ 配合Husky pre-commit ④ 提交前自动修复格式问题

### 9.6 完整配置流程

```bash
# 1. 安装所有依赖
pnpm add -D eslint eslint-plugin-vue @typescript-eslint/parser @typescript-eslint/eslint-plugin
pnpm add -D prettier eslint-config-prettier eslint-plugin-prettier
pnpm add -D husky lint-staged
pnpm add -D @commitlint/cli @commitlint/config-conventional

# 2. 初始化 Husky
npx husky install

# 3. 添加 prepare 脚本到 package.json
# "prepare": "husky install"

# 4. 添加 pre-commit 钩子
npx husky add .husky/pre-commit "npx lint-staged"

# 5. 添加 commit-msg 钩子
npx husky add .husky/commit-msg 'npx --no -- commitlint --edit "$1"'

# 6. 创建配置文件
# .eslintrc.cjs
# .prettierrc
# commitlint.config.cjs
# .lintstagedrc
```


> 🔍 **知识点深度解析**
>
> **作用**：完整流程：安装ESLint+Prettier+Husky+CommitLint+lint-staged到配置各工具到package.json添加prepare脚本到npx husky install到添加pre-commit和commit-msg钩子。
>
> **原理**：一次配置，团队共享，自动保障代码质量。
>
> **用法要点**：① 完整流程：安装ESLint+Prettier+Husky+CommitLint+lint-staged到配置各工具到package.json添加prepare脚本到npx husky install到添加pre-commit和commit-msg钩子 ② 一次配置，团队共享，自动保障代码质量

### 9.7 package.json 脚本

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .vue,.js,.ts --fix",
    "format": "prettier --write .",
    "prepare": "husky install"
  }
}
```

---

# 第五篇：UI 与样式篇

## 第10章 Element Plus UI 组件库

Element Plus 是 Vue3 官方推荐的 UI 组件库，提供了丰富的企业级组件。


> 🔍 **知识点深度解析**
>
> **作用**：package.json脚本：dev（开发）、build（构建）、preview（预览构建）、lint（检查）、lint:fix（修复）、format（格式化）、prepare（Husky安装）。
>
> **原理**：npm run xxx执行。
>
> **用法要点**：① package.json脚本：dev（开发）、build（构建）、preview（预览构建）、lint（检查）、lint:fix（修复）、format（格式化）、prepare（Husky安装） ② npm run xxx执行 ③ 统一项目操作入口

### 10.1 安装与配置

#### 安装

```bash
pnpm add element-plus
pnpm add @element-plus/icons-vue
```

#### 完整引入（不推荐，体积大）

```typescript
// main.ts
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import App from './App.vue'

const app = createApp(App)
app.use(ElementPlus, {
  locale: zhCn,
  size: 'default',
  zIndex: 3000
})
app.mount('#app')
```

#### 按需引入（推荐）

使用 `unplugin-vue-components` 和 `unplugin-auto-import` 实现自动按需引入。

```bash
pnpm add -D unplugin-vue-components unplugin-auto-import
```

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
      // 自动导入 Vue 相关函数
      imports: ['vue', 'vue-router', 'pinia'],
      dts: 'src/auto-import.d.ts'
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts'
    })
  ]
})
```


> 🔍 **知识点深度解析**
>
> **作用**：Element Plus Vue3组件库，npm install安装，app.use(ElementPlus)全量引入或按需引入（unplugin-vue-components自动导入，减小体积）。
>
> **原理**：TS支持完善。
>
> **用法要点**：① Element Plus Vue3组件库，npm install安装，app.use(ElementPlus)全量引入或按需引入（unplugin-vue-components自动导入，减小体积） ② TS支持完善 ③ 中文文档 ④ 后台管理系统首选

### 10.2 常用组件

#### 表单组件

```vue
<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="80px"
  >
    <el-form-item label="用户名" prop="username">
      <el-input v-model="form.username" placeholder="请输入用户名" />
    </el-form-item>
    
    <el-form-item label="密码" prop="password">
      <el-input v-model="form.password" type="password" show-password />
    </el-form-item>
    
    <el-form-item label="性别" prop="gender">
      <el-radio-group v-model="form.gender">
        <el-radio value="male">男</el-radio>
        <el-radio value="female">女</el-radio>
      </el-radio-group>
    </el-form-item>
    
    <el-form-item label="爱好" prop="hobbies">
      <el-checkbox-group v-model="form.hobbies">
        <el-checkbox value="reading">阅读</el-checkbox>
        <el-checkbox value="music">音乐</el-checkbox>
        <el-checkbox value="sports">运动</el-checkbox>
      </el-checkbox-group>
    </el-form-item>
    
    <el-form-item label="状态" prop="status">
      <el-switch v-model="form.status" />
    </el-form-item>
    
    <el-form-item>
      <el-button type="primary" @click="onSubmit">提交</el-button>
      <el-button @click="onReset">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

const formRef = ref<FormInstance>()

const form = reactive({
  username: '',
  password: '',
  gender: 'male',
  hobbies: [] as string[],
  status: true
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const onSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid) => {
    if (valid) {
      console.log('表单校验通过', form)
    }
  })
}

const onReset = () => {
  formRef.value?.resetFields()
}
</script>
```

#### 表格组件

```vue
<template>
  <el-table :data="tableData" border stripe v-loading="loading">
    <el-table-column type="selection" width="55" />
    <el-table-column prop="id" label="ID" width="80" />
    <el-table-column prop="name" label="姓名" width="120" />
    <el-table-column prop="age" label="年龄" width="80" />
    <el-table-column prop="address" label="地址" />
    <el-table-column label="状态" width="100">
      <template #default="{ row }">
        <el-tag :type="row.status ? 'success' : 'danger'">
          {{ row.status ? '启用' : '禁用' }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column label="操作" width="200" fixed="right">
      <template #default="{ row }">
        <el-button size="small" @click="handleEdit(row)">编辑</el-button>
        <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>
  
  <!-- 分页 -->
  <el-pagination
    v-model:current-page="page"
    v-model:page-size="pageSize"
    :total="total"
    :page-sizes="[10, 20, 50, 100]"
    layout="total, sizes, prev, pager, next, jumper"
    @size-change="fetchData"
    @current-change="fetchData"
  />
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'

interface User {
  id: number
  name: string
  age: number
  address: string
  status: boolean
}

const tableData = ref<User[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const fetchData = async () => {
  loading.value = true
  try {
    // 调用 API 获取数据
    // const res = await api.user.getUserList({ page: page.value, pageSize: pageSize.value })
    // tableData.value = res.data.list
    // total.value = res.data.total
  } finally {
    loading.value = false
  }
}

const handleEdit = (row: User) => {
  console.log('编辑', row)
}

const handleDelete = (row: User) => {
  console.log('删除', row)
}

onMounted(() => {
  fetchData()
})
</script>
```

#### 消息提示

```typescript
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'

// 普通消息
ElMessage('这是一条消息')
ElMessage.success('成功消息')
ElMessage.warning('警告消息')
ElMessage.error('错误消息')

// 确认弹窗
ElMessageBox.confirm('确定要删除吗？', '提示', {
  confirmButtonText: '确定',
  cancelButtonText: '取消',
  type: 'warning'
}).then(() => {
  ElMessage.success('删除成功')
}).catch(() => {
  ElMessage.info('已取消删除')
})

// 通知
ElNotification({
  title: '通知',
  message: '这是一条通知',
  type: 'success'
})
```


> 🔍 **知识点深度解析**
>
> **作用**：常用组件：el-form表单（校验）、el-table表格（排序/筛选/分页）、el-pagination分页、el-dialog弹窗、el-message提示、el-select选择器、el-date-picker日期。
>
> **原理**：v-model绑定数据。
>
> **用法要点**：① 常用组件：el-form表单（校验）、el-table表格（排序/筛选/分页）、el-pagination分页、el-dialog弹窗、el-message提示、el-select选择器、el-date-picker日期 ② v-model绑定数据 ③ 事件处理用户交互 ④ 查看文档获取完整API

### 10.3 全局配置

```typescript
// main.ts
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import App from './App.vue'

const app = createApp(App)

app.use(ElementPlus, {
  locale: zhCn,           // 中文语言包
  size: 'default',        // 全局组件大小
  zIndex: 3000            // 弹框 z-index
})

app.mount('#app')
```


> 🔍 **知识点深度解析**
>
> **作用**：app.use(ElementPlus, { size: small, zIndex: 3000 })全局配置默认尺寸、zIndex。
>
> **原理**：ElMessage配置全局duration。
>
> **用法要点**：① app.use(ElementPlus, { size: small, zIndex: 3000 })全局配置默认尺寸、zIndex ② ElMessage配置全局duration ③ locale国际化 ④ CSS变量自定义主题（--el-color-primary） ⑤ dark类名暗色模式

### 10.4 图标使用

```bash
pnpm add @element-plus/icons-vue
```

```vue
<template>
  <!-- 方式1：直接使用 -->
  <el-icon><Edit /></el-icon>
  
  <!-- 方式2：动态渲染 -->
  <el-icon :size="20" color="red">
    <component :is="iconName" />
  </el-icon>
  
  <!-- 方式3：按钮中使用 -->
  <el-button type="primary">
    <el-icon><Search /></el-icon>
    搜索
  </el-button>
</template>

<script setup lang="ts">
import { Edit, Search, Delete, Plus } from '@element-plus/icons-vue'
import { ref } from 'vue'

const iconName = ref('Edit')
</script>
```

---

## 第11章 Sass 样式方案

Sass 是 CSS 的预处理器，提供了变量、嵌套、混入、函数等高级特性。


> 🔍 **知识点深度解析**
>
> **作用**：@element-plus/icons-vue图标库，el-icon包裹Search组件使用。
>
> **原理**：unplugin-icons自动导入图标。
>
> **用法要点**：① @element-plus/icons-vue图标库，el-icon包裹Search组件使用 ② unplugin-icons自动导入图标 ③ 可自定义SVG图标 ④ 图标尺寸用font-size控制，颜色用color ⑤ 按钮、菜单、输入框前缀常用

### 11.1 安装与配置

#### 安装 Sass

```bash
pnpm add -D sass
```

#### Vite 全局配置

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  css: {
    preprocessorOptions: {
      scss: {
        // 全局注入变量和 mixin
        additionalData: `
          @use "@/styles/variables.scss" as *;
          @use "@/styles/mixins.scss" as *;
        `
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  }
})
```


> 🔍 **知识点深度解析**
>
> **作用**：Sass/SCSS CSS预处理器，npm install sass安装（Vite内置支持），style lang=scss使用。
>
> **原理**：变量、嵌套、混合、函数、继承。
>
> **用法要点**：① Sass/SCSS CSS预处理器，npm install sass安装（Vite内置支持），style lang=scss使用 ② 变量、嵌套、混合、函数、继承 ③ 提升CSS开发效率和可维护性 ④ 推荐SCSS语法（兼容CSS）

### 11.2 样式目录结构

```
src/
├── styles/
│   ├── index.scss          # 全局样式入口
│   ├── variables.scss      # 变量定义
│   ├── mixins.scss         # 混入函数
│   ├── reset.scss          # 样式重置
│   ├── common.scss         # 公共样式
│   └── element-ui.scss     # Element Plus 覆盖样式
```


> 🔍 **知识点深度解析**
>
> **作用**：样式目录：styles/variables.scss（变量）、mixins.scss（混合）、reset.scss（重置）、index.scss（入口）。
>
> **原理**：变量通过additionalData自动注入每个组件。
>
> **用法要点**：① 样式目录：styles/variables.scss（变量）、mixins.scss（混合）、reset.scss（重置）、index.scss（入口） ② 组件内style scoped局部样式 ③ 全局样式在main.ts引入 ④ 变量通过additionalData自动注入每个组件

### 11.3 变量定义

```scss
// src/styles/variables.scss

// ========== 颜色变量 ==========
$primary-color: #409eff;
$success-color: #67c23a;
$warning-color: #e6a23c;
$danger-color: #f56c6c;
$info-color: #909399;

// 文字颜色
$text-primary: #303133;
$text-regular: #606266;
$text-secondary: #909399;
$text-placeholder: #c0c4cc;

// 边框颜色
$border-color: #dcdfe6;
$border-color-light: #e4e7ed;

// 背景颜色
$bg-color: #ffffff;
$bg-color-page: #f2f3f5;

// ========== 尺寸变量 ==========
$header-height: 60px;
$sidebar-width: 200px;
$sidebar-width-collapse: 64px;

// ========== 字体变量 ==========
$font-size-xs: 12px;
$font-size-sm: 13px;
$font-size-base: 14px;
$font-size-lg: 16px;
$font-size-xl: 18px;

// ========== 间距变量 ==========
$spacing-xs: 4px;
$spacing-sm: 8px;
$spacing-md: 16px;
$spacing-lg: 24px;
$spacing-xl: 32px;

// ========== 圆角变量 ==========
$border-radius-sm: 2px;
$border-radius-base: 4px;
$border-radius-lg: 8px;
$border-radius-circle: 50%;

// ========== 阴影变量 ==========
$box-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
$box-shadow-base: 0 2px 4px rgba(0, 0, 0, .12), 0 0 6px rgba(0, 0, 0, .04);
$box-shadow-dark: 0 2px 8px rgba(0, 0, 0, .15);
```


> 🔍 **知识点深度解析**
>
> **作用**：SCSS变量名定义（颜色、尺寸、间距）。
>
> **原理**：:root定义CSS变量（运行时可改，主题切换用）。
>
> **用法要点**：① SCSS变量名定义（颜色、尺寸、间距） ② :root定义CSS变量（运行时可改，主题切换用） ③ 两者结合：SCSS变量编译时，CSS变量运行时 ④ Element Plus主题用CSS变量 ⑤ 统一设计token

### 11.4 Mixin 混入

```scss
// src/styles/mixins.scss

// ========== 文本省略 ==========
@mixin ellipsis($line: 1) {
  @if $line == 1 {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  } @else {
    display: -webkit-box;
    -webkit-line-clamp: $line;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

// ========== Flex 布局 ==========
@mixin flex($direction: row, $justify: flex-start, $align: stretch) {
  display: flex;
  flex-direction: $direction;
  justify-content: $justify;
  align-items: $align;
}

@mixin flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

@mixin flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

// ========== 绝对定位居中 ==========
@mixin absolute-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

// ========== 清除浮动 ==========
@mixin clearfix {
  &::after {
    content: '';
    display: table;
    clear: both;
  }
}

// ========== 滚动条样式 ==========
@mixin scrollbar {
  &::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #c0c4cc;
    border-radius: 3px;
    
    &:hover {
      background: #909399;
    }
  }
}
```


> 🔍 **知识点深度解析**
>
> **作用**：@mixin定义可复用样式块，@include引用，支持参数。
>
> **原理**：@extend继承样式。
>
> **用法要点**：① @mixin定义可复用样式块，@include引用，支持参数 ② @extend继承样式 ③ 常用mixin：flex布局、文本省略、滚动条、响应式断点 ④ 减少重复代码 ⑤ 注意mixin会展开（增加体积），公共样式用@extend更优

### 11.5 样式重置

```scss
// src/styles/reset.scss
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  width: 100%;
  height: 100%;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: $font-size-base;
  color: $text-primary;
  background-color: $bg-color-page;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a {
  color: $primary-color;
  text-decoration: none;
  
  &:hover {
    opacity: 0.8;
  }
}

ul,
ol {
  list-style: none;
}

img {
  max-width: 100%;
  vertical-align: middle;
}

button {
  cursor: pointer;
  border: none;
  outline: none;
  background: none;
}

input,
textarea {
  outline: none;
  border: none;
}
```


> 🔍 **知识点深度解析**
>
> **作用**：样式重置消除浏览器默认样式差异，normalize.css或自定义reset。
>
> **原理**：* { margin:0; padding:0; box-sizing:border-box }。
>
> **用法要点**：① 样式重置消除浏览器默认样式差异，normalize.css或自定义reset ② * { margin:0; padding:0; box-sizing:border-box } ③ a标签去下划线，ul去列表符号 ④ 统一基线样式 ⑤ 不要过度重置（影响可访问性）

### 11.6 在组件中使用

```vue
<template>
  <div class="card">
    <h3 class="title" :title="title">{{ title }}</h3>
    <p class="desc">{{ description }}</p>
    <div class="actions">
      <button class="btn-primary">确认</button>
      <button class="btn-default">取消</button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description: string
}>()
</script>

<style scoped lang="scss">
.card {
  padding: $spacing-lg;
  background: $bg-color;
  border-radius: $border-radius-lg;
  box-shadow: $box-shadow-base;
  
  .title {
    font-size: $font-size-lg;
    color: $text-primary;
    margin-bottom: $spacing-md;
    @include ellipsis;
  }
  
  .desc {
    font-size: $font-size-base;
    color: $text-regular;
    line-height: 1.6;
    margin-bottom: $spacing-lg;
    @include ellipsis(2);
  }
  
  .actions {
    @include flex(flex-end);
    gap: $spacing-sm;
  }
  
  .btn-primary {
    padding: $spacing-sm $spacing-md;
    background: $primary-color;
    color: #fff;
    border-radius: $border-radius-base;
  }
  
  .btn-default {
    padding: $spacing-sm $spacing-md;
    background: $bg-color-page;
    color: $text-regular;
    border-radius: $border-radius-base;
  }
}
</style>
```

---

# 第六篇：数据请求篇

## 第12章 Axios 封装与 API 管理


> 🔍 **知识点深度解析**
>
> **作用**：组件内style scoped样式只作用于当前组件（data-v-hash属性）。
>
> **原理**：深度选择器:deep(.el-xxx)修改子组件/第三方库样式。
>
> **用法要点**：① 组件内style scoped样式只作用于当前组件（data-v-hash属性） ② 深度选择器:deep(.el-xxx)修改子组件/第三方库样式 ③ :global()定义全局样式 ④ :slotted()插槽内容样式 ⑤ scoped避免样式污染，deep穿透必要时用

### 12.1 Axios 基础封装

#### 安装

```bash
pnpm add axios
```

#### 创建请求实例

```typescript
// src/utils/request.ts
import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL, // 基础 URL
  timeout: 10000,                             // 超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 在发送请求之前做些什么
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    // 对请求错误做些什么
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    // 2xx 范围内的状态码都会触发该函数
    const res = response.data
    
    // 根据后端约定的状态码处理
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      
      // 401: 未登录或 token 过期
      if (res.code === 401) {
        // 清除 token，跳转到登录页
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
      
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    
    return res
  },
  (error) => {
    // 超出 2xx 范围的状态码都会触发该函数
    let message = '网络错误'
    
    if (error.response) {
      switch (error.response.status) {
        case 400:
          message = '请求错误'
          break
        case 401:
          message = '未授权，请重新登录'
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求地址不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        case 502:
          message = '网关错误'
          break
        case 503:
          message = '服务不可用'
          break
        case 504:
          message = '网关超时'
          break
      }
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default service
```


> 🔍 **知识点深度解析**
>
> **作用**：Axios封装：create实例（baseURL/timeout/headers），请求拦截器（加token/loading），响应拦截器（统一处理错误/解包data/刷新token）。
>
> **原理**：统一错误处理。
>
> **用法要点**：① Axios封装：create实例（baseURL/timeout/headers），请求拦截器（加token/loading），响应拦截器（统一处理错误/解包data/刷新token） ② TS定义请求响应类型 ③ 取消请求（AbortController） ④ 统一错误处理

### 12.2 请求方法封装

```typescript
// src/utils/request.ts

// 通用响应类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页响应类型
export interface PageResponse<T = any> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

/**
 * GET 请求
 */
export function get<T = any>(url: string, params?: object, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  return service.get(url, { params, ...config })
}

/**
 * POST 请求
 */
export function post<T = any>(url: string, data?: object, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  return service.post(url, data, config)
}

/**
 * PUT 请求
 */
export function put<T = any>(url: string, data?: object, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  return service.put(url, data, config)
}

/**
 * DELETE 请求
 */
export function del<T = any>(url: string, params?: object, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  return service.delete(url, { params, ...config })
}

/**
 * 上传文件
 */
export function upload<T = any>(url: string, file: File, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  const formData = new FormData()
  formData.append('file', file)
  return service.post(url, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    ...config
  })
}
```


> 🔍 **知识点深度解析**
>
> **作用**：封装get/post/put/delete方法，支持泛型T指定响应类型。
>
> **原理**：统一处理params序列化、文件上传（FormData）、下载（responseType:blob）。
>
> **用法要点**：① 封装get/post/put/delete方法，支持泛型T指定响应类型 ② request<T>(config): Promise<T> ③ 统一处理params序列化、文件上传（FormData）、下载（responseType:blob） ④ 业务代码不直接用axios，用封装的request

### 12.3 API 统一管理

#### 目录结构

```
src/
├── api/
│   ├── index.ts          # API 统一出口
│   ├── user.ts           # 用户相关接口
│   ├── product.ts        # 商品相关接口
│   └── order.ts          # 订单相关接口
```

#### 用户模块 API

```typescript
// src/api/user.ts
import { get, post, put, del } from '@/utils/request'
import type { ApiResponse, PageResponse } from '@/utils/request'

// 用户信息类型
export interface User {
  id: number
  username: string
  email: string
  avatar?: string
  role: string
}

// 登录参数类型
export interface LoginParams {
  username: string
  password: string
}

// 登录返回类型
export interface LoginResult {
  token: string
  userInfo: User
}

/**
 * 用户登录
 */
export const login = (data: LoginParams) => {
  return post<LoginResult>('/user/login', data)
}

/**
 * 获取用户信息
 */
export const getUserInfo = () => {
  return get<User>('/user/info')
}

/**
 * 获取用户列表
 */
export const getUserList = (params: { page: number; pageSize: number; keyword?: string }) => {
  return get<PageResponse<User>>('/user/list', params)
}

/**
 * 修改用户信息
 */
export const updateUser = (data: Partial<User>) => {
  return put<User>('/user/update', data)
}

/**
 * 删除用户
 */
export const deleteUser = (id: number) => {
  return del(`/user/${id}`)
}
```

#### API 统一出口

```typescript
// src/api/index.ts
import * as userApi from './user'
import * as productApi from './product'
import * as orderApi from './order'

export default {
  user: userApi,
  product: productApi,
  order: orderApi
}
```

#### 在组件中使用

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'
import type { User } from '@/api/user'

const userList = ref<User[]>([])
const loading = ref(false)

const fetchUserList = async () => {
  loading.value = true
  try {
    const res = await api.user.getUserList({
      page: 1,
      pageSize: 10
    })
    userList.value = res.data.list
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUserList()
})
</script>
```

---

## 第13章 Mock 接口模拟


> 🔍 **知识点深度解析**
>
> **作用**：API统一管理：src/api/模块.ts，每个接口函数封装request调用，定义请求参数和响应类型。
>
> **原理**：组件中import { getUserList } from @/api/user。
>
> **用法要点**：① API统一管理：src/api/模块.ts，每个接口函数封装request调用，定义请求参数和响应类型 ② 组件中import { getUserList } from @/api/user ③ 按业务模块拆分，类型安全，便于维护和Mock替换

### 13.1 Mock 方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **vite-plugin-mock** | 配置简单，开发环境直接使用 | 仅开发环境可用 | 前端独立开发 |
| **Mock.js** | 数据生成能力强 | 需要拦截请求 | 纯前端 Mock |
| **MSW** | 真实网络请求，支持浏览器和 Node | 配置较复杂 | 接近真实后端 |
| **后端 Mock 服务** | 最接近真实环境 | 需要后端配合 | 联调阶段 |


> 🔍 **知识点深度解析**
>
> **作用**：Mock方案：vite-plugin-mock（开发环境拦截请求）、Mock.js（生成随机数据）、MSW（Service Worker拦截，更真实）。
>
> **原理**：前后端并行开发时用。
>
> **用法要点**：① Mock方案：vite-plugin-mock（开发环境拦截请求）、Mock.js（生成随机数据）、MSW（Service Worker拦截，更真实） ② 前后端并行开发时用 ③ 生产环境不引入 ④ 接口文档驱动Mock数据

### 13.2 vite-plugin-mock 配置

#### 安装

```bash
pnpm add -D vite-plugin-mock mockjs
```

#### Vite 配置

```typescript
// vite.config.ts
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { viteMockServe } from 'vite-plugin-mock'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  
  return {
    plugins: [
      vue(),
      viteMockServe({
        mockPath: 'mock',           // mock 文件目录
        enable: env.VITE_USE_MOCK === 'true', // 是否启用 mock
        logger: true,               // 是否显示日志
        watchFiles: true            // 监听文件变化
      })
    ]
  }
})
```

#### Mock 文件编写

```typescript
// mock/user.ts
import type { MockMethod } from 'vite-plugin-mock'

export default [
  // 用户登录
  {
    url: '/api/user/login',
    method: 'post',
    response: ({ body }) => {
      const { username, password } = body
      if (username === 'admin' && password === '123456') {
        return {
          code: 200,
          message: '登录成功',
          data: {
            token: 'mock-token-' + Date.now(),
            userInfo: {
              id: 1,
              username: 'admin',
              email: 'admin@example.com',
              role: 'admin'
            }
          }
        }
      }
      return {
        code: 400,
        message: '用户名或密码错误',
        data: null
      }
    }
  },
  
  // 获取用户列表
  {
    url: '/api/user/list',
    method: 'get',
    response: ({ query }) => {
      const { page = 1, pageSize = 10, keyword = '' } = query
      
      // 生成模拟数据
      const list = Array.from({ length: pageSize }, (_, i) => ({
        id: (page - 1) * pageSize + i + 1,
        username: `user_${(page - 1) * pageSize + i + 1}`,
        email: `user${i + 1}@example.com`,
        role: i % 3 === 0 ? 'admin' : 'user',
        createTime: new Date().toISOString()
      }))
      
      return {
        code: 200,
        message: 'success',
        data: {
          list,
          total: 100,
          page: Number(page),
          pageSize: Number(pageSize)
        }
      }
    }
  }
] as MockMethod[]
```


> 🔍 **知识点深度解析**
>
> **作用**：vite-plugin-mock在vite.config.ts中注册，mock目录下写接口定义（url/method/response）。
>
> **原理**：开发时自动拦截，不需要改请求地址。
>
> **用法要点**：① vite-plugin-mock在vite.config.ts中注册，mock目录下写接口定义（url/method/response） ② 支持动态响应（根据参数返回不同数据） ③ 开发时自动拦截，不需要改请求地址 ④ 生产构建自动排除

### 13.3 Mock.js 数据生成

#### 常用数据生成方法

```typescript
import Mock from 'mockjs'

// 基本类型
Mock.mock('@string')          // 随机字符串
Mock.mock('@integer(1, 100)') // 1-100 随机整数
Mock.mock('@float(0, 100)')   // 随机浮点数
Mock.mock('@boolean')         // 随机布尔值
Mock.mock('@date')            // 随机日期
Mock.mock('@time')            // 随机时间
Mock.mock('@datetime')        // 随机日期时间

// 文本
Mock.mock('@cname')           // 中文名字
Mock.mock('@name')            // 英文名字
Mock.mock('@ctitle(5, 10)')   // 中文标题
Mock.mock('@csentence')       // 中文句子
Mock.mock('@cparagraph')      // 中文段落

// 网络
Mock.mock('@url')             // 随机 URL
Mock.mock('@email')           // 随机邮箱
Mock.mock('@ip')              // 随机 IP
Mock.mock('@domain')          // 随机域名

// 图片
Mock.mock('@image("200x100")') // 随机图片

// 地址
Mock.mock('@region')          // 大区
Mock.mock('@province')        // 省份
Mock.mock('@city')            // 城市
Mock.mock('@county')          // 区县
Mock.mock('@zip')             // 邮编
```

#### 生成列表数据

```typescript
// mock/product.ts
import Mock from 'mockjs'
import type { MockMethod } from 'vite-plugin-mock'

export default [
  {
    url: '/api/product/list',
    method: 'get',
    response: ({ query }) => {
      const { page = 1, pageSize = 10 } = query
      
      const list = Mock.mock({
        [`list|${pageSize}`]: [{
          'id|+1': (page - 1) * pageSize + 1,
          name: '@ctitle(4, 10)',
          'price|10-1000.2': 0,
          'stock|0-500': 0,
          image: '@image("200x200")',
          description: '@csentence(10, 30)',
          createTime: '@datetime'
        }]
      })
      
      return {
        code: 200,
        message: 'success',
        data: {
          list: list.list,
          total: 86,
          page: Number(page),
          pageSize: Number(pageSize)
        }
      }
    }
  }
] as MockMethod[]
```


> 🔍 **知识点深度解析**
>
> **作用**：Mock.js生成随机数据：@id/@cname/@email/@integer/@datetime/@cparagraph。
>
> **原理**：Mock.mock(@cname)生成中文名。
>
> **用法要点**：① Mock.js生成随机数据：@id/@cname/@email/@integer/@datetime/@cparagraph ② Mock.mock(@cname)生成中文名 ③ 数据模板生成列表 ④ 模拟真实API数据结构，前后端并行

### 13.4 环境切换

```bash
# .env.development
VITE_USE_MOCK = true
VITE_API_BASE_URL = /api

# .env.production
VITE_USE_MOCK = false
VITE_API_BASE_URL = https://api.example.com
```

```typescript
// vite.config.ts
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  
  return {
    plugins: [
      vue(),
      viteMockServe({
        mockPath: 'mock',
        enable: env.VITE_USE_MOCK === 'true'
      })
    ]
  }
})
```

---

# 第七篇：业务实战篇

## 第14章 表单校验


> 🔍 **知识点深度解析**
>
> **作用**：环境切换：.env.development用Mock，.env.production用真实API。
>
> **原理**：请求拦截器中判断环境切换baseURL。
>
> **用法要点**：① 环境切换：.env.development用Mock，.env.production用真实API ② VITE_USE_MOCK变量控制 ③ 请求拦截器中判断环境切换baseURL ④ 联调时切真实API，不改动业务代码

### 14.1 Element Plus 表单校验基础

```vue
<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="100px"
  >
    <el-form-item label="用户名" prop="username">
      <el-input v-model="form.username" placeholder="请输入用户名" />
    </el-form-item>
    
    <el-form-item label="密码" prop="password">
      <el-input v-model="form.password" type="password" show-password />
    </el-form-item>
    
    <el-form-item label="确认密码" prop="confirmPassword">
      <el-input v-model="form.confirmPassword" type="password" />
    </el-form-item>
    
    <el-form-item label="手机号" prop="phone">
      <el-input v-model="form.phone" />
    </el-form-item>
    
    <el-form-item label="邮箱" prop="email">
      <el-input v-model="form.email" />
    </el-form-item>
    
    <el-form-item>
      <el-button type="primary" @click="onSubmit">提交</el-button>
      <el-button @click="onReset">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

const formRef = ref<FormInstance>()

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  phone: '',
  email: ''
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

const onSubmit = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    console.log('校验通过', form)
  } catch (error) {
    console.log('校验失败', error)
  }
}

const onReset = () => {
  formRef.value?.resetFields()
}
</script>
```


> 🔍 **知识点深度解析**
>
> **作用**：el-form校验：rules配置规则（required/message/trigger/type/min/max/pattern/validator），ref调用validate()。
>
> **原理**：prop绑定字段名。
>
> **用法要点**：① el-form校验：rules配置规则（required/message/trigger/type/min/max/pattern/validator），ref调用validate() ② prop绑定字段名 ③ 校验模式：blur失焦、change变化 ④ resetFields重置 ⑤ TS中ref<FormInstance>()

### 14.2 自定义校验规则

```typescript
// src/utils/validate.ts
import type { FormItemRule } from 'element-plus'

/**
 * 手机号校验
 */
export const validatePhone: FormItemRule['validator'] = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入手机号'))
  } else if (!/^1[3-9]\d{9}$/.test(value)) {
    callback(new Error('手机号格式不正确'))
  } else {
    callback()
  }
}

/**
 * 邮箱校验
 */
export const validateEmail: FormItemRule['validator'] = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入邮箱'))
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    callback(new Error('邮箱格式不正确'))
  } else {
    callback()
  }
}

/**
 * 身份证号校验
 */
export const validateIdCard: FormItemRule['validator'] = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入身份证号'))
  } else if (!/(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/.test(value)) {
    callback(new Error('身份证号格式不正确'))
  } else {
    callback()
  }
}

/**
 * 密码强度校验
 */
export const validatePasswordStrength: FormItemRule['validator'] = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else if (!/[a-zA-Z]/.test(value) || !/\d/.test(value)) {
    callback(new Error('密码必须包含字母和数字'))
  } else {
    callback()
  }
}
```

```typescript
// 组件中使用
import { validatePhone, validateEmail } from '@/utils/validate'

const rules: FormRules = {
  phone: [{ validator: validatePhone, trigger: 'blur' }],
  email: [{ validator: validateEmail, trigger: 'blur' }]
}
```


> 🔍 **知识点深度解析**
>
> **作用**：自定义校验validator(rule, value, callback)，callback()通过，callback(new Error(msg))失败。
>
> **原理**：异步校验（检查用户名是否存在）中调callback。
>
> **用法要点**：① 自定义校验validator(rule, value, callback)，callback()通过，callback(new Error(msg))失败 ② 异步校验（检查用户名是否存在）中调callback ③ 校验函数抽离到utils复用 ④ 注意必须调用callback（否则校验挂起）

### 14.3 关联字段校验

```vue
<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { FormInstance, FormRules, FormItemRule } from 'element-plus'

const formRef = ref<FormInstance>()

const form = reactive({
  password: '',
  confirmPassword: ''
})

// 确认密码校验
const validateConfirmPassword: FormItemRule['validator'] = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 监听密码变化，重新校验确认密码
watch(
  () => form.password,
  () => {
    formRef.value?.validateField('confirmPassword')
  }
)
</script>
```


> 🔍 **知识点深度解析**
>
> **作用**：关联字段校验：确认密码需访问password字段，用validator中this或闭包引用。
>
> **原理**：整个表单校验validate()返回Promise。
>
> **用法要点**：① 关联字段校验：确认密码需访问password字段，用validator中this或闭包引用 ② 整个表单校验validate()返回Promise ③ 部分字段validateField(field) ④ 动态增减表单项需动态rules

### 14.4 常用校验正则

```typescript
// src/utils/validate.ts

// 手机号
export const PHONE_REG = /^1[3-9]\d{9}$/

// 邮箱
export const EMAIL_REG = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

// 身份证号
export const ID_CARD_REG = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/

// 邮政编码
export const ZIP_CODE_REG = /^\d{6}$/

// URL
export const URL_REG = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/

// IP 地址
export const IP_REG = /^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$/

// 中文字符
export const CHINESE_REG = /^[\u4e00-\u9fa5]+$/

// 英文和数字
export const ALPHANUMERIC_REG = /^[A-Za-z0-9]+$/

// 整数
export const INTEGER_REG = /^-?[1-9]\d*$/

// 正整数
export const POSITIVE_INTEGER_REG = /^[1-9]\d*$/

// 金额（两位小数）
export const MONEY_REG = /^([1-9]\d*|0)(\.\d{1,2})?$/

// 日期 YYYY-MM-DD
export const DATE_REG = /^\d{4}-\d{2}-\d{2}$/

// 时间 HH:mm:ss
export const TIME_REG = /^\d{2}:\d{2}:\d{2}$/
```

---

## 第15章 Layout 布局组件


> 🔍 **知识点深度解析**
>
> **作用**：常用正则：手机号、邮箱、身份证、URL、IP地址。
>
> **原理**：封装正则常量文件统一管理。
>
> **用法要点**：① 常用正则：手机号、邮箱、身份证、URL、IP地址 ② pattern规则直接用正则 ③ 封装正则常量文件统一管理 ④ 注意正则转义

### 15.1 整体布局结构

```
┌─────────────────────────────────────────┐
│              Header                     │
├──────┬──────────────────────────────────┤
│      │                                  │
│      │                                  │
│Side  │           AppMain                │
│bar   │         (router-view)            │
│      │                                  │
│      │                                  │
└──────┴──────────────────────────────────┘
```

#### 目录结构

```
src/
├── layout/
│   ├── index.vue              # Layout 入口
│   └── components/
│       ├── Logo.vue           # Logo 组件
│       ├── Sidebar.vue        # 侧边栏
│       ├── SidebarItem.vue    # 侧边栏菜单项（递归）
│       ├── Header.vue         # 顶部导航
│       ├── Breadcrumb.vue     # 面包屑
│       └── AppMain.vue        # 主内容区
```


> 🔍 **知识点深度解析**
>
> **作用**：后台布局结构：Layout父组件包含Sidebar（侧边导航）+ Header（顶部栏）+ AppMain（主内容router-view）。
>
> **原理**：响应式折叠侧边栏。
>
> **用法要点**：① 后台布局结构：Layout父组件包含Sidebar（侧边导航）+ Header（顶部栏）+ AppMain（主内容router-view） ② el-container/el-aside/el-header/el-main布局 ③ 响应式折叠侧边栏 ④ 固定/流式布局

### 15.2 Logo 组件

```vue
<!-- src/layout/components/Logo.vue -->
<template>
  <div class="logo" @click="goHome">
    <img src="@/assets/images/logo.png" alt="logo" class="logo-img" />
    <span v-if="!isCollapse" class="logo-text">后台管理系统</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/store/modules/app'

const appStore = useAppStore()
const router = useRouter()

const isCollapse = computed(() => appStore.sidebarCollapse)

const goHome = () => {
  router.push('/')
}
</script>

<style scoped lang="scss">
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: #001529;
  
  .logo-img {
    width: 32px;
    height: 32px;
  }
  
  .logo-text {
    margin-left: 12px;
    color: #fff;
    font-size: 18px;
    font-weight: bold;
    white-space: nowrap;
  }
}
</style>
```


> 🔍 **知识点深度解析**
>
> **作用**：Logo组件显示系统名称和图标，点击跳转首页。
>
> **原理**：侧边栏折叠时只显示图标。
>
> **用法要点**：① Logo组件显示系统名称和图标，点击跳转首页 ② 侧边栏折叠时只显示图标 ③ 配合Pinia的appStore控制折叠状态 ④ SVG图标或el-icon ⑤ transition动画

### 15.3 Sidebar 侧边栏

```vue
<!-- src/layout/components/Sidebar.vue -->
<template>
  <div class="sidebar">
    <Logo />
    <el-scrollbar class="sidebar-scroll">
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :unique-opened="true"
        router
        background-color="#001529"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <SidebarItem
          v-for="route in menuRoutes"
          :key="route.path"
          :item="route"
          :base-path="route.path"
        />
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/store/modules/app'
import { usePermissionStore } from '@/store/modules/permission'
import Logo from './Logo.vue'
import SidebarItem from './SidebarItem.vue'

const route = useRoute()
const appStore = useAppStore()
const permissionStore = usePermissionStore()

const isCollapse = computed(() => appStore.sidebarCollapse)
const menuRoutes = computed(() => permissionStore.routes)
const activeMenu = computed(() => route.path)
</script>

<style scoped lang="scss">
.sidebar {
  width: 200px;
  height: 100vh;
  background: #001529;
  transition: width 0.3s;
  
  &.collapse {
    width: 64px;
  }
  
  .sidebar-scroll {
    height: calc(100vh - 60px);
  }
}
</style>
```

#### 递归菜单项

```vue
<!-- src/layout/components/SidebarItem.vue -->
<template>
  <template v-if="hasChildren(item)">
    <el-sub-menu :index="resolvePath(item.path)">
      <template #title>
        <el-icon v-if="item.meta?.icon">
          <component :is="item.meta.icon" />
        </el-icon>
        <span>{{ item.meta?.title }}</span>
      </template>
      <SidebarItem
        v-for="child in item.children"
        :key="child.path"
        :item="child"
        :base-path="resolvePath(child.path)"
      />
    </el-sub-menu>
  </template>
  
  <template v-else>
    <el-menu-item :index="resolvePath(item.path)">
      <el-icon v-if="item.meta?.icon">
        <component :is="item.meta.icon" />
      </el-icon>
      <template #title>{{ item.meta?.title }}</template>
    </el-menu-item>
  </template>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { RouteRecordRaw } from 'vue-router'

const props = defineProps<{
  item: RouteRecordRaw
  basePath: string
}>()

// 判断是否有子菜单
const hasChildren = (item: RouteRecordRaw) => {
  return item.children && item.children.length > 0 && !item.meta?.hidden
}

// 解析路径
const resolvePath = (path: string) => {
  if (path.startsWith('/')) return path
  return `${props.basePath}/${path}`.replace(/\/+/g, '/')
}
</script>
```


> 🔍 **知识点深度解析**
>
> **作用**：Sidebar侧边栏根据路由配置动态生成菜单（el-menu/el-sub-menu/el-menu-item），递归组件处理嵌套路由。
>
> **原理**：active菜单高亮，折叠模式。
>
> **用法要点**：① Sidebar侧边栏根据路由配置动态生成菜单（el-menu/el-sub-menu/el-menu-item），递归组件处理嵌套路由 ② active菜单高亮，折叠模式 ③ 权限过滤（只显示有权限的菜单） ④ el-scrollbar滚动

### 15.4 Header 顶部导航

```vue
<!-- src/layout/components/Header.vue -->
<template>
  <div class="header">
    <!-- 折叠按钮 -->
    <div class="left">
      <el-icon class="collapse-btn" @click="toggleSidebar">
        <Fold v-if="!isCollapse" />
        <Expand v-else />
      </el-icon>
      <Breadcrumb />
    </div>
    
    <!-- 右侧菜单 -->
    <div class="right">
      <!-- 全屏 -->
      <el-icon class="icon-btn" @click="toggleFullscreen">
        <FullScreen v-if="!isFullscreen" />
        <Aim v-else />
      </el-icon>
      
      <!-- 用户下拉 -->
      <el-dropdown @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="32" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
          <span class="username">{{ userStore.userInfo?.username }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人中心</el-dropdown-item>
            <el-dropdown-item command="settings">设置</el-dropdown-item>
            <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Fold, Expand, FullScreen, Aim, ArrowDown } from '@element-plus/icons-vue'
import { useAppStore } from '@/store/modules/app'
import { useUserStore } from '@/store/modules/user'
import Breadcrumb from './Breadcrumb.vue'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

const isCollapse = computed(() => appStore.sidebarCollapse)
const isFullscreen = ref(false)

// 切换侧边栏
const toggleSidebar = () => {
  appStore.toggleSidebar()
}

// 切换全屏
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

// 下拉菜单命令
const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        type: 'warning'
      }).then(() => {
        userStore.logout()
        router.push('/login')
      })
      break
  }
}
</script>

<style scoped lang="scss">
.header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  
  .left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .right {
    display: flex;
    align-items: center;
    gap: 20px;
  }
  
  .collapse-btn,
  .icon-btn {
    font-size: 20px;
    cursor: pointer;
    color: #606266;
    
    &:hover {
      color: #409eff;
    }
  }
  
  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    
    .username {
      font-size: 14px;
      color: #303133;
    }
  }
}
</style>
```


> 🔍 **知识点深度解析**
>
> **作用**：Header顶部导航：面包屑（当前路由路径）、用户信息下拉、全屏按钮、主题切换、通知。
>
> **原理**：el-dropdown用户菜单。
>
> **用法要点**：① Header顶部导航：面包屑（当前路由路径）、用户信息下拉、全屏按钮、主题切换、通知 ② el-dropdown用户菜单 ③ 折叠按钮控制Sidebar ④ 固定定位

### 15.5 AppMain 主内容区

```vue
<!-- src/layout/components/AppMain.vue -->
<template>
  <div class="app-main">
    <router-view v-slot="{ Component, route }">
      <transition name="fade-transform" mode="out-in">
        <keep-alive :include="cachedViews">
          <component :is="Component" :key="route.path" />
        </keep-alive>
      </transition>
    </router-view>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTagsViewStore } from '@/store/modules/tagsView'

const tagsViewStore = useTagsViewStore()
const cachedViews = computed(() => tagsViewStore.cachedViews)
</script>

<style scoped lang="scss">
.app-main {
  flex: 1;
  padding: 20px;
  overflow: auto;
  background: #f0f2f5;
}

/* 页面过渡动画 */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
```


> 🔍 **知识点深度解析**
>
> **作用**：AppMain主内容区router-view包裹keep-alive缓存页面，transition过渡动画。
>
> **原理**：多标签页（tags-view）可在此实现。
>
> **用法要点**：① AppMain主内容区router-view包裹keep-alive缓存页面，transition过渡动画 ② 固定高度滚动（el-scrollbar） ③ 多标签页（tags-view）可在此实现 ④ 内容区自适应

### 15.6 Layout 入口组件

```vue
<!-- src/layout/index.vue -->
<template>
  <div class="layout">
    <Sidebar class="sidebar" />
    <div class="main-container">
      <Header />
      <TagsView v-if="showTagsView" />
      <AppMain />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/store/modules/app'
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'
import AppMain from './components/AppMain.vue'
import TagsView from './components/TagsView.vue'

const appStore = useAppStore()
const showTagsView = computed(() => appStore.showTagsView)
</script>

<style scoped lang="scss">
.layout {
  display: flex;
  height: 100vh;
  
  .main-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
}
</style>
```

---

## 第16章 权限管理与动态路由


> 🔍 **知识点深度解析**
>
> **作用**：Layout入口组件组合Sidebar+Header+AppMain，el-container布局。
>
> **原理**：路由配置中component: Layout，子路由为具体页面。
>
> **用法要点**：① Layout入口组件组合Sidebar+Header+AppMain，el-container布局 ② 路由配置中component: Layout，子路由为具体页面 ③ 权限路由动态添加 ④ 整体布局骨架

### 16.1 路由类型扩展

```typescript
// src/router/types.ts
import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string          // 页面标题
    icon?: string           // 菜单图标
    hidden?: boolean        // 是否隐藏菜单
    keepAlive?: boolean     // 是否缓存
    requiresAuth?: boolean  // 是否需要登录
    roles?: string[]        // 角色权限
    breadcrumb?: boolean    // 是否显示面包屑
    affix?: boolean         // 是否固定标签页
  }
}
```


> 🔍 **知识点深度解析**
>
> **作用**：路由类型扩展：RouteMeta添加roles/title/icon等字段，declare module vue-router扩展。
>
> **原理**：异步路由表asyncRoutes定义需要权限的路由。
>
> **用法要点**：① 路由类型扩展：RouteMeta添加roles/title/icon等字段，declare module vue-router扩展 ② 异步路由表asyncRoutes定义需要权限的路由 ③ 常量路由constantRoutes不需要权限 ④ 根据用户角色过滤asyncRoutes

### 16.2 常量路由与异步路由

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import Layout from '@/layout/index.vue'

/**
 * 常量路由：所有用户都可以访问
 */
export const constantRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', hidden: true }
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { hidden: true }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '仪表盘', icon: 'HomeFilled', affix: true }
      }
    ]
  }
]

/**
 * 异步路由：根据角色动态添加
 */
export const asyncRoutes: RouteRecordRaw[] = [
  {
    path: '/user',
    component: Layout,
    redirect: '/user/list',
    meta: { title: '用户管理', icon: 'User', roles: ['admin'] },
    children: [
      {
        path: 'list',
        name: 'UserList',
        component: () => import('@/views/user/list.vue'),
        meta: { title: '用户列表', icon: 'UserFilled' }
      },
      {
        path: 'role',
        name: 'RoleList',
        component: () => import('@/views/user/role.vue'),
        meta: { title: '角色管理', icon: 'UserFilled', roles: ['admin'] }
      }
    ]
  },
  {
    path: '/system',
    component: Layout,
    redirect: '/system/menu',
    meta: { title: '系统管理', icon: 'Setting', roles: ['admin'] },
    children: [
      {
        path: 'menu',
        name: 'MenuManage',
        component: () => import('@/views/system/menu.vue'),
        meta: { title: '菜单管理', icon: 'Menu' }
      },
      {
        path: 'log',
        name: 'LogManage',
        component: () => import('@/views/system/log.vue'),
        meta: { title: '日志管理', icon: 'Document' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
    meta: { hidden: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: constantRoutes
})

export default router
```


> 🔍 **知识点深度解析**
>
> **作用**：常量路由（登录/404/首页）所有人可访问。
>
> **原理**：异步路由根据用户角色（roles）动态过滤后addRoute。
>
> **用法要点**：① 常量路由（登录/404/首页）所有人可访问 ② 异步路由根据用户角色（roles）动态过滤后addRoute ③ 后端返回权限标识，前端匹配路由meta.roles ④ 刷新后重新生成（路由守卫中处理）

### 16.3 权限 Store

```typescript
// src/store/modules/permission.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { RouteRecordRaw } from 'vue-router'
import router, { asyncRoutes, constantRoutes } from '@/router'

export const usePermissionStore = defineStore('permission', () => {
  const routes = ref<RouteRecordRaw[]>([])
  const addRoutes = ref<RouteRecordRaw[]>([])
  
  /**
   * 判断是否有权限
   */
  function hasPermission(roles: string[], route: RouteRecordRaw): boolean {
    if (route.meta?.roles) {
      return roles.some(role => route.meta!.roles!.includes(role))
    }
    return true
  }
  
  /**
   * 过滤异步路由
   */
  function filterAsyncRoutes(routes: RouteRecordRaw[], roles: string[]): RouteRecordRaw[] {
    const res: RouteRecordRaw[] = []
    
    routes.forEach(route => {
      const tmp = { ...route }
      
      if (hasPermission(roles, tmp)) {
        if (tmp.children) {
          tmp.children = filterAsyncRoutes(tmp.children, roles)
        }
        res.push(tmp)
      }
    })
    
    return res
  }
  
  /**
   * 生成路由
   */
  function generateRoutes(roles: string[]) {
    let accessedRoutes: RouteRecordRaw[]
    
    if (roles.includes('admin')) {
      // admin 拥有所有权限
      accessedRoutes = asyncRoutes
    } else {
      // 其他角色过滤
      accessedRoutes = filterAsyncRoutes(asyncRoutes, roles)
    }
    
    addRoutes.value = accessedRoutes
    routes.value = constantRoutes.concat(accessedRoutes)
    
    // 动态添加路由
    accessedRoutes.forEach(route => {
      router.addRoute(route)
    })
    
    return accessedRoutes
  }
  
  /**
   * 重置路由
   */
  function resetRoutes() {
    addRoutes.value.forEach(route => {
      if (route.name) {
        router.removeRoute(route.name)
      }
    })
    routes.value = []
    addRoutes.value = []
  }
  
  return {
    routes,
    addRoutes,
    generateRoutes,
    resetRoutes
  }
})
```


> 🔍 **知识点深度解析**
>
> **作用**：权限Store（userStore）存储用户信息、token、roles、权限按钮标识。
>
> **原理**：login action发请求存token，getInfo获取用户信息和权限，logout清除。
>
> **用法要点**：① 权限Store（userStore）存储用户信息、token、roles、权限按钮标识 ② login action发请求存token，getInfo获取用户信息和权限，logout清除 ③ 持久化token（localStorage/cookie）

### 16.4 路由守卫完整流程

```typescript
// src/router/permission.ts
import router from './index'
import { useUserStore } from '@/store/modules/user'
import { usePermissionStore } from '@/store/modules/permission'
import { ElMessage } from 'element-plus'

// 白名单
const whiteList = ['/login', '/404']

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const permissionStore = usePermissionStore()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 后台管理` : '后台管理'
  
  const token = userStore.token
  
  if (token) {
    // 已登录
    if (to.path === '/login') {
      // 已登录访问登录页，跳首页
      next('/')
    } else {
      // 检查是否有用户信息
      if (userStore.roles.length === 0) {
        try {
          // 获取用户信息
          const { roles } = await userStore.getUserInfo()
          
          // 生成可访问路由
          const accessRoutes = permissionStore.generateRoutes(roles)
          
          // 动态添加路由后，重新跳转
          next({ ...to, replace: true })
        } catch (error) {
          // 获取用户信息失败，清除 token 跳登录
          userStore.resetToken()
          ElMessage.error((error as Error).message || '获取用户信息失败')
          next(`/login?redirect=${to.path}`)
        }
      } else {
        next()
      }
    }
  } else {
    // 未登录
    if (whiteList.includes(to.path)) {
      next()  // 白名单直接放行
    } else {
      next(`/login?redirect=${to.path}`)  // 否则跳登录
    }
  }
})
```


> 🔍 **知识点深度解析**
>
> **作用**：路由守卫完整流程：beforeEach到判断token到无token跳登录到有token判断是否已获取用户信息到未获取则调getInfo到根据roles生成可访问路由到addRoute到next({...to, replace})。
>
> **原理**：白名单（登录页）直接放行。
>
> **用法要点**：① 路由守卫完整流程：beforeEach到判断token到无token跳登录到有token判断是否已获取用户信息到未获取则调getInfo到根据roles生成可访问路由到addRoute到next({...to, replace}) ② 白名单（登录页）直接放行

### 16.5 按钮级权限

```typescript
// src/directives/permission.ts
import type { Directive, DirectiveBinding } from 'vue'
import { useUserStore } from '@/store/modules/user'

/**
 * v-permission 指令
 * 用法：v-permission="'admin'" 或 v-permission="['admin', 'editor']"
 */
export const permission: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding) {
    const { value } = binding
    const userStore = useUserStore()
    const roles = userStore.roles
    
    if (value && value.length > 0) {
      const permissionRoles = Array.isArray(value) ? value : [value]
      
      const hasPermission = roles.some(role => permissionRoles.includes(role))
      
      if (!hasPermission) {
        el.parentNode?.removeChild(el)
      }
    } else {
      throw new Error('v-permission 指令需要传入角色值')
    }
  }
}
```

```vue
<!-- 使用示例 -->
<template>
  <!-- 只有 admin 可以看到删除按钮 -->
  <el-button v-permission="'admin'" type="danger">删除</el-button>
  
  <!-- admin 或 editor 都可以看到编辑按钮 -->
  <el-button v-permission="['admin', 'editor']">编辑</el-button>
</template>
```

---

# 第八篇：进阶篇

## 第17章 进阶响应式 API


> 🔍 **知识点深度解析**
>
> **作用**：按钮级权限：v-permission自定义指令，根据用户权限标识判断是否显示/禁用元素。
>
> **原理**：或封装hasPerm函数v-if判断。
>
> **用法要点**：① 按钮级权限：v-permission自定义指令，根据用户权限标识判断是否显示/禁用元素 ② 或封装hasPerm函数v-if判断 ③ 权限标识从userStore获取 ④ 细粒度控制（增删改查按钮）

### 17.1 shallowRef / shallowReactive

浅层响应式，只有第一层是响应式的，深层数据变化不会触发更新。

#### shallowRef

```typescript
import { shallowRef, triggerRef } from 'vue'

const state = shallowRef({
  count: 0,
  nested: { value: 1 }
})

// 修改第一层 → 触发更新
state.value = { count: 1, nested: { value: 2 } }

// 修改深层 → 不会触发更新
state.value.count++        // ❌ 不触发
state.value.nested.value++ // ❌ 不触发

// 手动触发更新
triggerRef(state)  // ✅ 强制触发
```

#### shallowReactive

```typescript
import { shallowReactive } from 'vue'

const state = shallowReactive({
  count: 0,
  nested: { value: 1 }
})

// 修改第一层 → 触发更新
state.count++  // ✅

// 修改深层 → 不会触发更新
state.nested.value++  // ❌
```

#### 使用场景

- 大型列表/对象，不需要深层响应式，提升性能
- 第三方库实例，不需要代理
- 明确知道只操作顶层数据


> 🔍 **知识点深度解析**
>
> **作用**：shallowRef/shallowReactive只顶层响应式（嵌套不响应式），减少大对象性能开销。
>
> **原理**：shallowRef修改.value触发，shallowReactive修改顶层属性触发。
>
> **用法要点**：① shallowRef/shallowReactive只顶层响应式（嵌套不响应式），减少大对象性能开销 ② shallowRef修改.value触发，shallowReactive修改顶层属性触发 ③ triggerRef手动触发shallowRef更新 ④ 适合大列表、第三方对象

### 17.2 readonly / shallowReadonly

创建只读的响应式对象，防止数据被意外修改。

```typescript
import { readonly, shallowReadonly, reactive } from 'vue'

const original = reactive({
  count: 0,
  nested: { value: 1 }
})

// 深层只读
const copy = readonly(original)
copy.count++  // ❌ 警告，不能修改

// 浅层只读
const shallowCopy = shallowReadonly(original)
shallowCopy.count++          // ❌ 警告
shallowCopy.nested.value++   // ✅ 深层可以修改
```

#### 使用场景

- 传递给子组件的数据，防止子组件修改
- 暴露给外部的只读数据
- 保护配置对象


> 🔍 **知识点深度解析**
>
> **作用**：readonly深只读（嵌套都只读，修改警告），shallowReadonly只顶层只读。
>
> **原理**：保护状态不被意外修改（传给子组件的props、全局配置）。
>
> **用法要点**：① readonly深只读（嵌套都只读，修改警告），shallowReadonly只顶层只读 ② 保护状态不被意外修改（传给子组件的props、全局配置） ③ readonly包裹的对象传递，子组件无法修改

### 17.3 toRef / toRefs

将响应式对象的属性转为 ref，保持响应式连接。

#### toRef

```typescript
import { reactive, toRef } from 'vue'

const state = reactive({
  count: 0,
  name: 'Vue'
})

// 将单个属性转为 ref
const countRef = toRef(state, 'count')

console.log(countRef.value)  // 0
countRef.value++             // 修改 ref
console.log(state.count)     // 1 → 原对象也变了

state.count++                // 修改原对象
console.log(countRef.value)  // 2 → ref 也变了
```

#### toRefs

```typescript
import { reactive, toRefs } from 'vue'

const state = reactive({
  count: 0,
  name: 'Vue',
  age: 18
})

// 将所有属性转为 ref
const { count, name, age } = toRefs(state)

console.log(count.value)  // 0
count.value++             // ✅ 修改后原对象也变
```

#### 使用场景

- 解构响应式对象，保持响应式
- 从组合式函数返回多个 ref
- 避免每次都写 `state.xxx`


> 🔍 **知识点深度解析**
>
> **作用**：toRef将reactive对象单个属性转ref（保持响应式），toRefs批量转换。
>
> **原理**：解构reactive必须用toRefs（否则丢失响应式）。
>
> **用法要点**：① toRef将reactive对象单个属性转ref（保持响应式），toRefs批量转换 ② 解构reactive必须用toRefs（否则丢失响应式） ③ 原理：创建ObjectRefImpl，get/set代理原对象属性

### 17.4 markRaw

标记一个对象，使其永远不会被转为响应式。

```typescript
import { markRaw, reactive } from 'vue'

// 标记为原始对象
const foo = markRaw({
  count: 0
})

// 放入 reactive 中，foo 仍然是原始对象
const state = reactive({
  foo
})

console.log(isReactive(state.foo))  // false

state.foo.count++  // 修改不会触发更新
```

#### 使用场景

- 第三方类的实例，不需要响应式
- 大型不可变数据，跳过代理提升性能
- 渲染函数中的静态对象


> 🔍 **知识点深度解析**
>
> **作用**：markRaw标记对象永远不转为响应式（reactive/ref包裹无效），用于第三方库实例、大数组、不需要响应式的复杂对象，减少性能开销。
>
> **原理**：isReactive/isProxy检测。
>
> **用法要点**：① markRaw标记对象永远不转为响应式（reactive/ref包裹无效），用于第三方库实例、大数组、不需要响应式的复杂对象，减少性能开销 ② isReactive/isProxy检测 ③ 注意markRaw后对象的属性也不响应式

### 17.5 toRaw

获取响应式对象的原始对象。

```typescript
import { reactive, toRaw } from 'vue'

const reactiveObj = reactive({ count: 0 })
const rawObj = toRaw(reactiveObj)

console.log(rawObj === reactiveObj)  // false
console.log(isReactive(rawObj))      // false

// 直接修改原始对象，不会触发更新
rawObj.count++  // 不触发视图更新
```

#### 使用场景

- 需要将数据传给不支持响应式的第三方库
- 性能优化：批量修改时用原始对象，改完再赋值回去
- 调试时查看真实数据


> 🔍 **知识点深度解析**
>
> **作用**：toRaw获取响应式对象的原始对象（不再响应式，不触发更新），用于临时读取（避免代理开销）或传给第三方库。
>
> **原理**：不建议持久引用。
>
> **用法要点**：① toRaw获取响应式对象的原始对象（不再响应式，不触发更新），用于临时读取（避免代理开销）或传给第三方库 ② 不建议持久引用 ③ 与markRaw配合：markRaw标记后toRaw也返回原对象

### 17.6 各 API 使用场景对比

| API | 作用 | 使用场景 |
|-----|------|---------|
| `shallowRef` | 浅层 ref | 大型对象、第三方实例 |
| `shallowReactive` | 浅层 reactive | 只操作顶层数据 |
| `readonly` | 深层只读 | 保护数据不被修改 |
| `shallowReadonly` | 浅层只读 | 保护顶层数据 |
| `toRef` | 单属性转 ref | 解构单个属性 |
| `toRefs` | 全部属性转 ref | 解构整个对象 |
| `markRaw` | 标记为原始对象 | 跳过响应式代理 |
| `toRaw` | 获取原始对象 | 操作原始数据 |

---

## 第18章 性能优化


> 🔍 **知识点深度解析**
>
> **作用**：API选型：基本类型ref，对象reactive，大对象shallow系列，只读保护readonly，解构保持响应式toRefs，第三方对象markRaw，临时读原始toRaw，自定义响应式customRef。
>
> **原理**：根据场景选择，避免过度响应式。
>
> **用法要点**：① API选型：基本类型ref，对象reactive，大对象shallow系列，只读保护readonly，解构保持响应式toRefs，第三方对象markRaw，临时读原始toRaw，自定义响应式customRef ② 根据场景选择，避免过度响应式

### 18.1 虚拟列表

当列表数据量很大时，只渲染可视区域的内容。

```vue
<template>
  <div class="virtual-list" ref="listRef" @scroll="handleScroll">
    <!-- 占位元素，撑开高度 -->
    <div :style="{ height: totalHeight + 'px' }">
      <!-- 可视区域的列表项 -->
      <div
        class="list-item"
        :style="{ transform: `translateY(${startOffset}px)` }"
      >
        <div
          v-for="item in visibleList"
          :key="item.id"
          class="item"
          :style="{ height: itemHeight + 'px' }"
        >
          {{ item.name }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface ListItem {
  id: number
  name: string
}

const props = defineProps<{
  list: ListItem[]
  itemHeight?: number
}>()

const listRef = ref<HTMLElement>()
const itemHeight = props.itemHeight || 50

// 可视区域起始索引
const startIndex = ref(0)

// 可视区域能显示的数量
const visibleCount = computed(() => {
  const viewHeight = listRef.value?.clientHeight || 600
  return Math.ceil(viewHeight / itemHeight) + 2  // 多渲染2个，防止滚动白屏
})

// 结束索引
const endIndex = computed(() => startIndex.value + visibleCount.value)

// 可视列表
const visibleList = computed(() => {
  return props.list.slice(startIndex.value, endIndex.value)
})

// 总高度
const totalHeight = computed(() => props.list.length * itemHeight)

// 偏移量
const startOffset = computed(() => startIndex.value * itemHeight)

// 滚动处理
const handleScroll = (e: Event) => {
  const target = e.target as HTMLElement
  const scrollTop = target.scrollTop
  startIndex.value = Math.floor(scrollTop / itemHeight)
}
</script>

<style scoped>
.virtual-list {
  height: 600px;
  overflow-y: auto;
}

.item {
  padding: 0 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
}
</style>
```


> 🔍 **知识点深度解析**
>
> **作用**：虚拟列表只渲染可视区域元素（大量数据列表优化）。
>
> **原理**：计算可视范围（scrollTop/itemHeight），动态渲染子集。
>
> **用法要点**：① 虚拟列表只渲染可视区域元素（大量数据列表优化） ② 计算可视范围（scrollTop/itemHeight），动态渲染子集 ③ el-table-v2或vue-virtual-scroller库 ④ 固定高度简单，动态高度需计算 ⑤ 万级数据必备

### 18.2 图片懒加载

```typescript
// src/directives/lazy.ts
import type { Directive, DirectiveBinding } from 'vue'

/**
 * v-lazy 图片懒加载指令
 * 用法：v-lazy="图片地址"
 */
export const lazy: Directive = {
  mounted(el: HTMLImageElement, binding: DirectiveBinding) {
    const src = binding.value
    
    // 默认占位图
    el.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
    
    // 创建 IntersectionObserver
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            // 进入可视区域，加载图片
            el.src = src
            // 加载完成后停止观察
            observer.unobserve(el)
          }
        })
      },
      {
        rootMargin: '100px'  // 提前100px加载
      }
    )
    
    observer.observe(el)
  }
}
```

```vue
<!-- 使用 -->
<template>
  <img v-lazy="imageUrl" alt="图片" />
</template>
```


> 🔍 **知识点深度解析**
>
> **作用**：图片懒加载：IntersectionObserver监听可视区域，进入视口才加载src。
>
> **原理**：v-lazy自定义指令或vue-lazyload库。
>
> **用法要点**：① 图片懒加载：IntersectionObserver监听可视区域，进入视口才加载src ② v-lazy自定义指令或vue-lazyload库 ③ 占位图+渐显动画 ④ 减少首屏请求和带宽 ⑤ 注意SSR不支持（用loading=lazy原生属性）

### 18.3 防抖与节流

```typescript
// src/utils/index.ts

/**
 * 防抖
 * @param fn 要执行的函数
 * @param delay 延迟时间（毫秒）
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout> | null = null
  
  return function (this: any, ...args: Parameters<T>) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流
 * @param fn 要执行的函数
 * @param delay 间隔时间（毫秒）
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300
): (...args: Parameters<T>) => void {
  let lastTime = 0
  
  return function (this: any, ...args: Parameters<T>) {
    const now = Date.now()
    if (now - lastTime >= delay) {
      lastTime = now
      fn.apply(this, args)
    }
  }
}
```


> 🔍 **知识点深度解析**
>
> **作用**：防抖（debounce）n秒后执行，期间再次触发则重新计时（搜索输入）。
>
> **原理**：节流（throttle）n秒内只执行一次（滚动/resize）。
>
> **用法要点**：① 防抖（debounce）n秒后执行，期间再次触发则重新计时（搜索输入） ② 节流（throttle）n秒内只执行一次（滚动/resize） ③ lodash提供，或自定义hook useDebounce/useThrottle ④ 避免频繁触发事件

### 18.4 组件懒加载

```typescript
import { defineAsyncComponent } from 'vue'

// 异步组件
const HeavyComponent = defineAsyncComponent(() =>
  import('./HeavyComponent.vue')
)

// 带加载状态和错误状态
const AsyncComponent = defineAsyncComponent({
  loader: () => import('./HeavyComponent.vue'),
  loadingComponent: LoadingComponent,  // 加载中显示
  errorComponent: ErrorComponent,      // 加载失败显示
  delay: 200,                          // 延迟显示加载状态
  timeout: 3000                        // 超时时间
})
```


> 🔍 **知识点深度解析**
>
> **作用**：组件懒加载defineAsyncComponent(() => import(./Big.vue))，按需加载（减少首屏体积）。
>
> **原理**：配合Suspense显示加载状态。
>
> **用法要点**：① 组件懒加载defineAsyncComponent(() => import(./Big.vue))，按需加载（减少首屏体积） ② 配合Suspense显示加载状态 ③ 大组件、弹窗、表格用懒加载 ④ webpackChunkName命名分包

### 18.5 路由懒加载

```typescript
const routes = [
  {
    path: '/home',
    component: () => import('@/views/home/index.vue')
  },
  {
    path: '/about',
    component: () => import('@/views/about/index.vue')
  }
]
```


> 🔍 **知识点深度解析**
>
> **作用**：路由懒加载component: () => import(@/views/xxx.vue)，每个路由单独分包，访问时才加载。
>
> **原理**：Vite自动代码分割。
>
> **用法要点**：① 路由懒加载component: () => import(@/views/xxx.vue)，每个路由单独分包，访问时才加载 ② Vite自动代码分割 ③ 减少首屏JS体积 ④ 配合webpackChunkName分组 ⑤ 后台系统必备

### 18.6 keep-alive 缓存

```vue
<template>
  <router-view v-slot="{ Component }">
    <keep-alive :include="cachedViews">
      <component :is="Component" />
    </keep-alive>
  </router-view>
</template>
```


> 🔍 **知识点深度解析**
>
> **作用**：keep-alive缓存页面组件（不重复创建），include指定缓存组件名，max限制数量。
>
> **原理**：列表页缓存滚动位置和筛选条件。
>
> **用法要点**：① keep-alive缓存页面组件（不重复创建），include指定缓存组件名，max限制数量 ② 列表页缓存滚动位置和筛选条件 ③ onActivated重新获取数据 ④ 注意内存占用，不需要的页面不缓存

### 18.7 v-for key 优化

```vue
<!-- ❌ 不好：用 index 作为 key -->
<div v-for="(item, index) in list" :key="index">
  {{ item.name }}
</div>

<!-- ✅ 好：用唯一 id 作为 key -->
<div v-for="item in list" :key="item.id">
  {{ item.name }}
</div>
```


> 🔍 **知识点深度解析**
>
> **作用**：v-for key用唯一稳定id（不用index），Diff算法基于key复用节点。
>
> **原理**：index作为key在列表排序/增删时会导致状态错乱和性能问题。
>
> **用法要点**：① v-for key用唯一稳定id（不用index），Diff算法基于key复用节点 ② index作为key在列表排序/增删时会导致状态错乱和性能问题 ③ key是虚拟DOM Diff的核心优化

### 18.8 生产构建优化

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    // 压缩
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,   // 移除 console
        drop_debugger: true   // 移除 debugger
      }
    },
    
    // 分包
    rollupOptions: {
      output: {
        manualChunks: {
          vue: ['vue', 'vue-router', 'pinia'],
          elementPlus: ['element-plus'],
          echarts: ['echarts']
        }
      }
    },
    
    // 源映射
    sourcemap: false
  }
})
```

---

## 第19章 常用工具函数与 Hooks


> 🔍 **知识点深度解析**
>
> **作用**：生产构建优化：Vite build自动Tree-Shaking/压缩/分包。
>
> **原理**：manualChunks手动分包（vendor/element-plus/echarts）。
>
> **用法要点**：① 生产构建优化：Vite build自动Tree-Shaking/压缩/分包 ② manualChunks手动分包（vendor/element-plus/echarts） ③ gzip/brotli压缩（vite-plugin-compression） ④ CDN引入大库 ⑤ 分析包体积（rollup-plugin-visualizer）

### 19.1 常用工具函数

```typescript
// src/utils/index.ts

/**
 * 深拷贝
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as any
  }
  
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as any
  }
  
  if (typeof obj === 'object') {
    const clonedObj = {} as T
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
  
  return obj
}

/**
 * 日期格式化
 */
export function formatDate(date: Date | string | number, format: string = 'YYYY-MM-DD HH:mm:ss'): string {
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 金额格式化
 */
export function formatMoney(amount: number, decimals: number = 2): string {
  return amount.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/**
 * 文件下载
 */
export function downloadFile(url: string, filename: string) {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * 复制到剪贴板
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    const result = document.execCommand('copy')
    document.body.removeChild(textarea)
    return result
  }
}

/**
 * 本地存储封装
 */
export const storage = {
  get<T = any>(key: string): T | null {
    try {
      const value = localStorage.getItem(key)
      return value ? JSON.parse(value) : null
    } catch {
      return null
    }
  },
  
  set(key: string, value: any) {
    try {
      localStorage.setItem(key, JSON.stringify(value))
    } catch (e) {
      console.error('localStorage 写入失败', e)
    }
  },
  
  remove(key: string) {
    localStorage.removeItem(key)
  },
  
  clear() {
    localStorage.clear()
  }
}
```


> 🔍 **知识点深度解析**
>
> **作用**：常用工具函数：日期格式化（dayjs）、防抖节流、深拷贝（structuredClone/JSON）、类型判断、数组去重、对象合并、URL参数解析。
>
> **原理**：封装到utils/，TS类型完善。
>
> **用法要点**：① 常用工具函数：日期格式化（dayjs）、防抖节流、深拷贝（structuredClone/JSON）、类型判断、数组去重、对象合并、URL参数解析 ② 封装到utils/，TS类型完善 ③ 纯函数易测试 ④ 避免重复造轮子（lodash-es按需引入）

### 19.2 常用 Hooks

#### useRequest 请求 Hook

```typescript
// src/hooks/useRequest.ts
import { ref, onMounted } from 'vue'

interface UseRequestOptions<T> {
  immediate?: boolean
  defaultData?: T
  onSuccess?: (data: T) => void
  onError?: (error: Error) => void
}

export function useRequest<T>(
  requestFn: () => Promise<T>,
  options: UseRequestOptions<T> = {}
) {
  const { immediate = true, defaultData, onSuccess, onError } = options
  
  const data = ref<T | undefined>(defaultData)
  const loading = ref(false)
  const error = ref<Error | null>(null)
  
  const run = async () => {
    loading.value = true
    error.value = null
    try {
      const result = await requestFn()
      data.value = result
      onSuccess?.(result)
      return result
    } catch (e) {
      error.value = e as Error
      onError?.(e as Error)
      throw e
    } finally {
      loading.value = false
    }
  }
  
  if (immediate) {
    onMounted(run)
  }
  
  return { data, loading, error, run }
}
```

```vue
<!-- 使用 -->
<script setup lang="ts">
import { useRequest } from '@/hooks/useRequest'
import api from '@/api'

const { data, loading, run } = useRequest(
  () => api.user.getUserList({ page: 1, pageSize: 10 }),
  {
    onSuccess: (res) => {
      console.log('请求成功', res)
    }
  }
)
</script>
```

#### useDebounce 防抖 Hook

```typescript
// src/hooks/useDebounce.ts
import { ref, watch, onUnmounted } from 'vue'

export function useDebounce<T>(value: T, delay: number = 300) {
  const debouncedValue = ref(value) as { value: T }
  let timer: ReturnType<typeof setTimeout> | null = null
  
  watch(
    () => value,
    (newVal) => {
      if (timer) clearTimeout(timer)
      timer = setTimeout(() => {
        debouncedValue.value = newVal
      }, delay)
    }
  )
  
  onUnmounted(() => {
    if (timer) clearTimeout(timer)
  })
  
  return debouncedValue
}
```

#### useThrottle 节流 Hook

```typescript
// src/hooks/useThrottle.ts
import { ref, watch, onUnmounted } from 'vue'

export function useThrottle<T>(value: T, delay: number = 300) {
  const throttledValue = ref(value) as { value: T }
  let lastTime = 0
  let timer: ReturnType<typeof setTimeout> | null = null
  
  watch(
    () => value,
    (newVal) => {
      const now = Date.now()
      if (now - lastTime >= delay) {
        lastTime = now
        throttledValue.value = newVal
      } else {
        if (timer) clearTimeout(timer)
        timer = setTimeout(() => {
          lastTime = Date.now()
          throttledValue.value = newVal
        }, delay - (now - lastTime))
      }
    }
  )
  
  onUnmounted(() => {
    if (timer) clearTimeout(timer)
  })
  
  return throttledValue
}
```

#### useTable 表格 Hook

```typescript
// src/hooks/useTable.ts
import { ref, reactive, onMounted } from 'vue'

interface UseTableOptions<T> {
  requestFn: (params: any) => Promise<{ list: T[]; total: number }>
  immediate?: boolean
}

export function useTable<T>(options: UseTableOptions<T>) {
  const { requestFn, immediate = true } = options
  
  const tableData = ref<T[]>([])
  const loading = ref(false)
  const total = ref(0)
  
  const pagination = reactive({
    page: 1,
    pageSize: 10
  })
  
  const queryParams = reactive<Record<string, any>>({})
  
  const fetchData = async () => {
    loading.value = true
    try {
      const res = await requestFn({
        ...queryParams,
        page: pagination.page,
        pageSize: pagination.pageSize
      })
      tableData.value = res.list
      total.value = res.total
    } finally {
      loading.value = false
    }
  }
  
  const handleSizeChange = (size: number) => {
    pagination.pageSize = size
    pagination.page = 1
    fetchData()
  }
  
  const handleCurrentChange = (page: number) => {
    pagination.page = page
    fetchData()
  }
  
  const handleSearch = () => {
    pagination.page = 1
    fetchData()
  }
  
  const handleReset = () => {
    Object.keys(queryParams).forEach(key => {
      queryParams[key] = ''
    })
    pagination.page = 1
    fetchData()
  }
  
  if (immediate) {
    onMounted(fetchData)
  }
  
  return {
    tableData,
    loading,
    total,
    pagination,
    queryParams,
    fetchData,
    handleSizeChange,
    handleCurrentChange,
    handleSearch,
    handleReset
  }
}
```

---

# 附录：Vue3 组合式 API 速查表

## 响应式 API

| API | 说明 | 示例 |
|-----|------|------|
| `ref` | 创建基本类型响应式 | `const count = ref(0)` |
| `reactive` | 创建对象类型响应式 | `const state = reactive({})` |
| `computed` | 计算属性 | `const double = computed(() => count.value * 2)` |
| `watch` | 监听数据变化 | `watch(count, (val) => {})` |
| `watchEffect` | 自动追踪依赖 | `watchEffect(() => {})` |
| `shallowRef` | 浅层 ref | `const state = shallowRef({})` |
| `shallowReactive` | 浅层 reactive | `const state = shallowReactive({})` |
| `readonly` | 只读 | `const copy = readonly(state)` |
| `toRef` | 单属性转 ref | `const count = toRef(state, 'count')` |
| `toRefs` | 全部属性转 ref | `const { count } = toRefs(state)` |
| `markRaw` | 标记为原始对象 | `const obj = markRaw({})` |
| `toRaw` | 获取原始对象 | `const raw = toRaw(state)` |
| `isRef` | 判断是否是 ref | `isRef(count)` |
| `isReactive` | 判断是否是 reactive | `isReactive(state)` |
| `isReadonly` | 判断是否是只读 | `isReadonly(copy)` |
| `isProxy` | 判断是否是代理 | `isProxy(state)` |

## 生命周期

| API | 说明 | 对应选项式 |
|-----|------|-----------|
| `onMounted` | 挂载后 | `mounted` |
| `onUpdated` | 更新后 | `updated` |
| `onUnmounted` | 卸载后 | `beforeUnmount` |
| `onBeforeMount` | 挂载前 | `beforeMount` |
| `onBeforeUpdate` | 更新前 | `beforeUpdate` |
| `onBeforeUnmount` | 卸载前 | `beforeUnmount` |
| `onActivated` | keep-alive 激活 | `activated` |
| `onDeactivated` | keep-alive 失活 | `deactivated` |
| `onErrorCaptured` | 捕获子组件错误 | `errorCaptured` |

## 依赖注入

| API | 说明 | 示例 |
|-----|------|------|
| `provide` | 提供数据 | `provide('key', value)` |
| `inject` | 注入数据 | `const value = inject('key')` |

## 工具函数

| API | 说明 | 示例 |
|-----|------|------|
| `nextTick` | 下次 DOM 更新后 | `await nextTick()` |
| `defineComponent` | 定义组件 | `defineComponent({})` |
| `defineAsyncComponent` | 异步组件 | `defineAsyncComponent(() => import(...))` |
| `defineProps` | 定义 props | `defineProps<{...}>()` |
| `defineEmits` | 定义 emits | `defineEmits<{...}>()` |
| `defineExpose` | 暴露属性 | `defineExpose({...})` |
| `defineSlots` | 定义插槽 | `defineSlots<{...}>()` |
| `useSlots` | 获取插槽 | `const slots = useSlots()` |
| `useAttrs` | 获取 attrs | `const attrs = useAttrs()` |
| `useCssModule` | CSS Modules | `const styles = useCssModule()` |
| `useCssVars` | CSS 变量 | `useCssVars(() => ({}))` |

## 路由 API

| API | 说明 | 示例 |
|-----|------|------|
| `useRoute` | 获取路由对象 | `const route = useRoute()` |
| `useRouter` | 获取路由实例 | `const router = useRouter()` |
| `onBeforeRouteLeave` | 离开路由前 | `onBeforeRouteLeave(() => {})` |
| `onBeforeRouteUpdate` | 路由更新前 | `onBeforeRouteUpdate(() => {})` |

## Pinia API

| API | 说明 | 示例 |
|-----|------|------|
| `defineStore` | 定义 Store | `defineStore('id', () => {})` |
| `storeToRefs` | 解构保持响应式 | `const { count } = storeToRefs(store)` |
| `store.$patch` | 批量修改 | `store.$patch({...})` |
| `store.$reset` | 重置 | `store.$reset()` |
| `store.$subscribe` | 订阅变化 | `store.$subscribe(() => {})` |
| `store.$onAction` | 订阅 action | `store.$onAction(() => {})` |


> 🔍 **知识点深度解析**
>
> **作用**：常用Hooks：useDebounce/useThrottle（防抖节流）、useEventListener（自动解绑事件）、useLocalStorage（响应式本地存储）、useMouse/useWindowSize（响应式DOM信息）、useRequest（请求状态管理）。
>
> **原理**：VueUse库提供大量高质量hooks。
>
> **用法要点**：① 常用Hooks：useDebounce/useThrottle（防抖节流）、useEventListener（自动解绑事件）、useLocalStorage（响应式本地存储）、useMouse/useWindowSize（响应式DOM信息）、useRequest（请求状态管理） ② VueUse库提供大量高质量hooks


---

> 📋 **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」模块（作用+原理+用法要点）。所有原有内容完整保留，未做任何修改。