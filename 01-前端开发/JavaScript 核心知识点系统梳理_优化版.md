---
title: JavaScript 核心知识点系统梳理
tags: [前端, JavaScript, ES6, 异步, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# JavaScript 核心知识点系统梳理（优化版）

> **文档说明**：系统梳理 JavaScript 核心知识点，涵盖 ES6+ 新特性、原型链、闭包、异步编程、作用域、事件循环等面试高频考点。

---

## 1. 概述

JavaScript 是一种轻量级、解释型的编程语言，是 Web 开发的核心技术之一。从最初的表单验证脚本，发展到如今支持服务端（Node.js）、桌面端（Electron）、移动端（React Native）的全场景语言。

**发展历程**：
- ES5（2009）：基础功能完善，严格模式
- ES6/ES2015：革命性更新，let/const、箭头函数、Promise、模块化
- ES2016-ES2024：持续迭代，可选链、空值合并、顶层 await等

---

## 2. 数据类型

### 2.1 基本类型（7种）

`undefined`、`null`、`boolean`、`number`、`string`、`symbol`、`bigint`

**存储方式**：栈内存，按值访问。

### 2.2 引用类型

`Object`、`Array`、`Function`、`Date`、`RegExp` 等

**存储方式**：堆内存，栈中保存引用地址，按引用访问。

> 🔍 **知识点深度解析**
>
> **作用**：理解数据类型是掌握 JS 的基础，面试必考。
>
> **原理**：基本类型值直接存在栈中，赋值是值的拷贝；引用类型值存在堆中，栈中存的是内存地址，赋值是地址的拷贝（浅拷贝）。所以 `let a = {x:1}; let b = a; b.x = 2` 会改变 a.x，因为 a 和 b 指向同一个堆内存地址。
>
> **用法要点**：① `typeof null === 'object'` 是历史遗留 bug；② `typeof undefined === 'undefined'`；③ 数组用 `Array.isArray()` 判断，不要用 typeof；④ `Symbol()` 创建唯一值，用于对象属性防止冲突；⑤ `BigInt` 用于大整数，后面加 n；⑥ 深拷贝用 `structuredClone()` 或 `JSON.parse(JSON.stringify())`（后者不能拷贝函数/undefined/循环引用）。

### 2.3 类型转换

**隐式转换规则**：
- `+` 运算符：有字符串则拼接，否则转数字
- `==` 比较：对象转原始值，null == undefined
- `if` 条件：转 boolean，假值有 `0, '', null, undefined, NaN, false`

**显式转换**：`Number()`、`String()`、`Boolean()`、`parseInt()`、`parseFloat()`

---

## 3. 作用域与闭包

### 3.1 作用域类型

- **全局作用域**：最外层，整个程序可访问
- **函数作用域**：函数内部，外部不可访问
- **块级作用域**：`{}` 内，let/const 声明的变量
- **模块作用域**：ES Module 内部

### 3.2 作用域链

变量查找时，先在当前作用域找，找不到则向上级作用域查找，直到全局作用域。**词法作用域**由代码书写位置决定，不是调用位置。

### 3.3 闭包

**定义**：函数能够记住并访问它的词法作用域，即使函数在当前词法作用域之外执行。

```javascript
function createCounter() {
  let count = 0;
  return function() {
    return ++count;
  };
}
const counter = createCounter();
counter(); // 1
counter(); // 2
```

> 🔍 **知识点深度解析**
>
> **作用**：闭包是 JS 最核心的概念之一，用于数据私有化、函数柯里化、模块化、防抖节流等。
>
> **原理**：当内部函数被返回并在外部调用时，它仍然持有对外部函数作用域的引用（通过 `[[Scope]]` 属性），导致外部函数的变量不会被垃圾回收。这就是闭包的本质——函数+其词法环境的组合。
>
> **用法要点**：① 闭包会导致内存泄漏（变量不被回收），不用时手动置 null；② 循环中用 var 创建闭包会共享同一个变量，用 let 或立即执行函数解决；③ 模块化是闭包的经典应用（IIFE 暴露公共方法）；④ 防抖节流本质是闭包保存定时器 ID；⑤ 面试常考：闭包定义、内存泄漏、循环闭包问题。

---

## 4. 原型与原型链

### 4.1 原型（prototype）

每个函数都有 `prototype` 属性，指向一个对象，这个对象是通过该构造函数创建的实例的原型。

每个对象（除了 null）都有 `__proto__` 属性，指向创建它的构造函数的 `prototype`。

### 4.2 原型链

对象查找属性时，先在自身找，找不到则通过 `__proto__` 向上找原型，直到 `Object.prototype.__proto__ === null`，形成原型链。

```javascript
function Person(name) { this.name = name; }
Person.prototype.say = function() { console.log(this.name); };
const p = new Person('Tom');
p.say(); // 'Tom' — 通过原型链找到 say 方法
p.__proto__ === Person.prototype; // true
Person.prototype.__proto__ === Object.prototype; // true
```

> 🔍 **知识点深度解析**
>
> **作用**：原型链是 JS 实现继承的核心机制，理解原型链才能理解 JS 的面向对象。
>
> **原理**：JS 是基于原型的语言，没有类（ES6 class 是语法糖）。每个对象都有 `[[Prototype]]` 内部槽（通过 `__proto__` 访问），指向其原型对象。属性访问时，引擎先查对象自身，找不到则沿 `__proto__` 链向上查找，这就是原型链。`new` 操作符做了四件事：创建空对象 → 设置 `__proto__` 指向构造函数 prototype → 绑定 this → 返回对象（或构造函数返回的对象）。
>
> **用法要点**：① `__proto__` 是访问器属性（getter/setter），推荐用 `Object.getPrototypeOf()` / `Object.setPrototypeOf()`；② `Object.create(null)` 创建无原型的纯净对象；③ 继承用 `class extends`（ES6）或 `Child.prototype = Object.create(Parent.prototype)`；④ 不要直接修改 `__proto__`，性能差；⑤ `instanceof` 检查原型链上是否有构造函数的 prototype；⑥ 面试常考：new 过程、原型链图、继承实现。

---

## 5. 执行上下文与 this

### 5.1 执行上下文

JS 代码执行时创建执行上下文，包含：
- **变量环境**：var 声明、函数声明
- **词法环境**：let/const 声明
- **this 绑定**

**执行栈**：全局上下文先入栈，函数调用时新上下文入栈，执行完出栈。

### 5.2 this 绑定规则

| 调用方式 | this 指向 |
|----------|-----------|
| 普通函数调用 | 全局对象（严格模式 undefined） |
| 对象方法调用 | 调用方法的对象 |
| call/apply/bind | 第一个参数 |
| new 调用 | 新创建的实例 |
| 箭头函数 | 外层作用域的 this（继承） |

```javascript
const obj = {
  value: 42,
  getValue: () => this.value, // 箭头函数，this 指向外层（全局）
  getValue2: function() { return this.value; } // 普通函数，this 指向 obj
};
obj.getValue(); // undefined
obj.getValue2(); // 42
```

> 🔍 **知识点深度解析**
>
> **作用**：this 是 JS 中最容易混淆的概念，理解 this 绑定规则是写好 JS 的基础。
>
> **原理**：this 是在函数调用时绑定的，不是定义时。绑定优先级：new > call/apply/bind > 对象方法 > 普通调用。箭头函数没有自己的 this，它的 this 继承自外层词法作用域，且无法通过 call/apply/bind 修改。执行上下文创建时确定 this，全局上下文 this 是全局对象（浏览器 window，Node.js globalThis）。
>
> **用法要点**：① 回调函数中 this 容易丢失，用箭头函数或 bind 固定；② 事件处理函数中 this 指向绑定事件的元素；③ 严格模式下普通函数调用 this 是 undefined；④ `bind` 返回新函数，`call/apply` 立即执行；⑤ 面试常考：this 指向判断、箭头函数 this 特点、bind 实现。

---

## 6. 异步编程

### 6.1 事件循环（Event Loop）

JS 是单线程的，通过事件循环处理异步。

**执行顺序**：
1. 执行同步代码（调用栈）
2. 清空微任务队列（Promise.then、MutationObserver、queueMicrotask）
3. 取一个宏任务执行（setTimeout、setInterval、I/O、UI渲染）
4. 重复 2-3

```javascript
console.log('1');
setTimeout(() => console.log('2'), 0);
Promise.resolve().then(() => console.log('3'));
console.log('4');
// 输出: 1, 4, 3, 2
```

### 6.2 Promise

**三种状态**：pending（进行中）、fulfilled（已成功）、rejected（已失败），状态一旦改变不可逆。

**常用方法**：
- `Promise.all()`：全部成功才成功，任一失败则失败
- `Promise.race()`：第一个完成的决定状态
- `Promise.allSettled()`：等待全部完成，返回每个结果
- `Promise.any()`：第一个成功就成功，全部失败才失败

### 6.3 async/await

`async` 函数返回 Promise，`await` 暂停执行等待 Promise 结果。

```javascript
async function fetchData() {
  try {
    const res = await fetch('/api/data');
    const data = await res.json();
    return data;
  } catch (err) {
    console.error(err);
  }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：异步编程是 JS 的核心能力，事件循环、Promise、async/await 是现代 JS 必备知识。
>
> **原理**：JS 运行时包含调用栈、堆、任务队列。宏任务队列（macrotask）存 setTimeout 等回调，微任务队列（microtask）存 Promise.then 等。每个宏任务执行完后，必须清空所有微任务才执行下一个宏任务。Promise 是对异步操作的封装，then/catch 回调进入微任务队列。async/await 是 Promise 的语法糖，await 后面的代码相当于在 then 回调中。
>
> **用法要点**：① 微任务比宏任务先执行，面试常考输出顺序；② `Promise.all` 适合并行请求，`for await` 适合顺序处理；③ await 只能在 async 函数中使用（ES2022 支持顶层 await）；④ 错误处理用 try/catch 或 .catch()；⑤ 避免在循环中用 await 串行（可用 Promise.all 并行）；⑥ 面试常考：事件循环机制、Promise 输出顺序、async/await 原理。

---

## 7. ES6+ 核心特性

### 7.1 let/const 与块级作用域

- `let`：块级作用域，可重新赋值，不存在变量提升（暂时性死区）
- `const`：块级作用域，声明时必须赋值，不可重新赋值（对象属性可改）

### 7.2 箭头函数

```javascript
const sum = (a, b) => a + b;
const double = n => n * 2; // 单参数可省略括号
const getObj = () => ({ a: 1 }); // 返回对象需括号
```

**特点**：无 this、无 arguments、不能 new、无 prototype。

### 7.3 解构赋值

```javascript
const { name, age } = user;
const [first, second] = arr;
const { name: userName, ...rest } = user; // 重命名 + 剩余
```

### 7.4 模板字符串

```javascript
const msg = `Hello, ${name}! 今年 ${age} 岁。`;
```

### 7.5 展开运算符

```javascript
const arr3 = [...arr1, ...arr2]; // 数组合并
const obj2 = { ...obj1, age: 20 }; // 对象合并（浅拷贝）
```

### 7.6 可选链与空值合并（ES2020）

```javascript
const city = user?.address?.city; // 可选链，避免报错
const name = inputName ?? '匿名'; // 空值合并，只在 null/undefined 时生效
```

> 🔍 **知识点深度解析**
>
> **作用**：ES6+ 特性极大提升了 JS 开发效率和代码可读性，是现代前端开发的基础。
>
> **原理**：let/const 通过词法环境实现块级作用域，存在暂时性死区（TDZ）——在声明前访问会报 ReferenceError。箭头函数的 this 继承自外层词法作用域，本质是没有自己的 this 绑定。解构赋值是语法糖，编译后是逐个赋值。可选链 `?.` 编译后是三元表达式判断，空值合并 `??` 只判断 null/undefined（与 `||` 不同，`||` 对 0、''、false 也生效）。
>
> **用法要点**：① 默认用 const，需要重新赋值才用 let，不要用 var；② 箭头函数适合回调，不适合对象方法和构造函数；③ 解构时设置默认值 `const { name = '匿名' } = user`；④ 展开运算符是浅拷贝，嵌套对象需注意；⑤ `??` 和 `||` 区别：`0 ?? 1` 是 0，`0 || 1` 是 1；⑥ 面试常考：var/let/const 区别、箭头函数特点、可选链原理。

---

## 8. 数组常用方法

### 8.1 遍历方法

| 方法 | 作用 | 返回值 |
|------|------|--------|
| `forEach` | 遍历，无返回 | undefined |
| `map` | 映射转换 | 新数组 |
| `filter` | 过滤 | 新数组 |
| `reduce` | 累计 | 单个值 |
| `find` | 找第一个满足 | 元素或 undefined |
| `some` | 任一满足 | boolean |
| `every` | 全部满足 | boolean |

### 8.2 其他常用

`push/pop/shift/unshift`、`slice`（不修改原数组）、`splice`（修改原数组）、`concat`、`join`、`sort`、`reverse`、`flat`、`flatMap`

```javascript
// reduce 高级用法
const sum = arr.reduce((acc, cur) => acc + cur, 0);
const groupBy = arr.reduce((acc, item) => {
  (acc[item.type] ||= []).push(item);
  return acc;
}, {});
```

---

## 9. 内存管理与垃圾回收

### 9.1 垃圾回收机制

- **引用计数**：记录被引用次数，为 0 则回收（循环引用问题）
- **标记清除**：从根对象出发标记可达对象，未标记的回收（现代浏览器主流）

### 9.2 常见内存泄漏

1. 意外的全局变量
2. 未清除的定时器/事件监听
3. 闭包持有大对象引用
4. DOM 引用未释放

```javascript
// 避免内存泄漏
element.addEventListener('click', handler);
// 组件销毁时
element.removeEventListener('click', handler);
clearInterval(timerId);
```

---

## 10. 面试高频考点

1. **原型链**：画出原型链图，new 过程
2. **闭包**：定义、应用、内存泄漏
3. **this**：四种绑定规则、箭头函数 this
4. **事件循环**：宏任务/微任务、输出顺序
5. **Promise**：状态、方法、async/await 原理
6. **var/let/const**：区别、暂时性死区
7. **深拷贝**：实现方式、JSON 方法局限性
8. **防抖节流**：实现代码、应用场景
9. **继承**：ES6 class、原型链继承
10. **数组方法**：reduce 高级用法、数组去重

---

## 📝 精简总结

- JS 是单线程、基于原型、动态类型的语言
- 作用域链和原型链是两大核心查找机制
- 闭包 = 函数 + 词法环境，用于数据私有化
- this 在调用时绑定，箭头函数继承外层 this
- 事件循环：同步 → 微任务 → 宏任务，循环往复
- ES6+ 让 JS 更现代化，优先使用 let/const、箭头函数、解构、可选链

---

[[01-前端开发/MOC-前端开发|← 返回前端开发 MOC]] | [[Home|🏠 返回首页]]
