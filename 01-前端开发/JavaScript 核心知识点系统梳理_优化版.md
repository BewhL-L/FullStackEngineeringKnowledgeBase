---
title: JavaScript 核心知识点系统梳理
tags: [前端, JavaScript, ES6, 异步, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# JavaScript 核心知识点系统梳理（优化版）

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。


> **文档说明**：系统梳理 JavaScript 核心知识点，涵盖 ES6+ 新特性、原型链、闭包、异步编程、作用域、事件循环等面试高频考点。

---

## 1. 概述

JavaScript 是一种轻量级、解释型的编程语言，是 Web 开发的核心技术之一。从最初的表单验证脚本，发展到如今支持服务端（Node.js）、桌面端（Electron）、移动端（React Native）的全场景语言。

**发展历程**：
- ES5（2009）：基础功能完善，严格模式
- ES6/ES2015：革命性更新，let/const、箭头函数、Promise、模块化
- ES2016-ES2024：持续迭代，可选链、空值合并、顶层 await等

---


---
## 2. 数据类型

### 2.1 基本类型（7种）

`undefined`、`null`、`boolean`、`number`、`string`、`symbol`、`bigint`

**存储方式**：栈内存，按值访问。


> 🔍 **知识点深度解析**
>
> **作用**：基本类型是 JS 数据的基础分类，理解其存储与判据是避免类型相关 bug 的前提。
>
> **原理**：7 种基本类型（undefined/null/boolean/number/string/symbol/bigint）值直接存放在栈中按值访问，复制时拷贝值本身，彼此独立。
>
> **用法要点**：① Symbol 创建唯一值，常用于对象私有属性键  ② BigInt 用数字加 n 表示大整数，不能与 number 直接运算  ③ typeof 可区分基本类型，但 typeof null 返回 'object'（历史 bug）  ④ number 采用 IEEE754 双精度，存在 0.1+0.2!==0.3 的精度问题  ⑤ 基本类型没有方法，调用时临时包装成对象

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


> 🔍 **知识点深度解析**
>
> **作用**：掌握类型转换规则能正确预测 ==、运算与条件判断结果，避免隐式转换陷阱。
>
> **原理**：JS 在运算/比较/条件处按规则自动转类型：+ 遇字符串转拼接，== 先 ToPrimitive 再比较，if/逻辑运算转 boolean（假值仅 0、''、null、undefined、NaN、false）。
>
> **用法要点**：① 推荐用 ===/!== 避免隐式转换  ② == 下 null==undefined 为 true，且与其它不相等  ③ 对象转原始值先调 valueOf 再 toString  ④ 显式转换用 Number()/String()/Boolean()/parseInt()  ⑤ + 一元运算符可快速转数字，但 +[] 为 0、+{} 为 NaN 需注意


---
## 3. 作用域与闭包

### 3.1 作用域类型

- **全局作用域**：最外层，整个程序可访问
- **函数作用域**：函数内部，外部不可访问
- **块级作用域**：`{}` 内，let/const 声明的变量
- **模块作用域**：ES Module 内部


> 🔍 **知识点深度解析**
>
> **作用**：作用域决定变量的可见范围与生命周期，是理解变量查找与闭包的基础。
>
> **原理**：全局作用域跨整个程序；函数作用域由 function 创建；块级作用域由 {} 配合 let/const 创建（ES6 引入）；模块作用域在 ESM 文件内隔离。
>
> **用法要点**：① var 只有函数/全局作用域，会提升并泄漏到块外  ② let/const 有块级作用域且存在暂时性死区  ③ 模块作用域中顶层变量不污染全局  ④ 函数作用域是最经典的作用域形式  ⑤ 作用域在代码书写时已确定（词法作用域）

### 3.2 作用域链

变量查找时，先在当前作用域找，找不到则向上级作用域查找，直到全局作用域。**词法作用域**由代码书写位置决定，不是调用位置。


> 🔍 **知识点深度解析**
>
> **作用**：作用域链解释“在某个位置访问变量时 JS 去哪里找”，是变量解析的核心机制。
>
> **原理**：每个作用域都有指向上一级作用域的引用，变量查找从当前逐级向上直到全局；这条链由函数定义时的词法位置决定（词法作用域），与调用位置无关。
>
> **用法要点**：① 查找顺序：当前→上级→…→全局，找不到报 ReferenceError  ② 词法作用域是“写在哪里”决定，不是“在哪里调用”  ③ 作用域链嵌套形成闭包的环境基础  ④ with/eval 会动态改变作用域链（不推荐）  ⑤ 全局变量在整条链末端，访问成本略高

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


---
## 4. 原型与原型链

### 4.1 原型（prototype）

每个函数都有 `prototype` 属性，指向一个对象，这个对象是通过该构造函数创建的实例的原型。

每个对象（除了 null）都有 `__proto__` 属性，指向创建它的构造函数的 `prototype`。


> 🔍 **知识点深度解析**
>
> **作用**：prototype 是 JS 实现共享属性/方法与“类式”行为的基石。
>
> **原理**：每个函数都有 prototype 属性（普通函数默认指向含 constructor 的对象）；每个对象有内部 [[Prototype]]（经 __proto__ 访问）指向其构造函数的 prototype，由此实例共享原型上的方法。
>
> **用法要点**：① 构造函数 prototype 上的方法被所有实例共享  ② 实例.__proto__ === 构造函数.prototype  ③ prototype.constructor 指回构造函数本身  ④ ES6 class 的方法也挂在原型上  ⑤ 修改 prototype 会影响已创建实例（引用），一般应在定义阶段设定

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


---
## 5. 执行上下文与 this

### 5.1 执行上下文

JS 代码执行时创建执行上下文，包含：
- **变量环境**：var 声明、函数声明
- **词法环境**：let/const 声明
- **this 绑定**

**执行栈**：全局上下文先入栈，函数调用时新上下文入栈，执行完出栈。


> 🔍 **知识点深度解析**
>
> **作用**：执行上下文是 JS 代码运行时的“环境快照”，理解它才能看懂变量提升、this 与调用栈。
>
> **原理**：代码执行前创建执行上下文，包含变量环境（var/函数声明）、词法环境（let/const）、this 绑定与外部引用；全局上下文先入执行栈，函数调用时新建上下文入栈，执行完出栈。
>
> **用法要点**：① 创建阶段先扫描函数声明与 var（提升），let/const 进入 TDZ  ② 执行栈（调用栈）LIFO，栈溢出会 RangeError  ③ 全局上下文的变量环境即全局对象  ④ this 在上下文创建时确定  ⑤ 闭包本质是外部上下文未出栈被内部引用

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


> 🔍 **知识点深度解析**
>
> **作用**：事件循环让单线程的 JS 能“并发”处理异步任务，是理解输出顺序与卡顿的关键。
>
> **原理**：JS 单线程，同步代码在调用栈执行；异步回调放入宏任务/微任务队列；每执行完一个宏任务后清空全部微任务，再取下一个宏任务，循环往复。
>
> **用法要点**：① 微任务（Promise.then、queueMicrotask、MutationObserver）先于下一个宏任务  ② 宏任务含 setTimeout/setInterval/I/O/UI 渲染  ③ 经典输出：同步→微任务→宏任务  ④ requestAnimationFrame 时机介于两者之间  ⑤ 大量微任务会阻塞渲染，需避免递归 Promise

### 6.2 Promise

**三种状态**：pending（进行中）、fulfilled（已成功）、rejected（已失败），状态一旦改变不可逆。

**常用方法**：
- `Promise.all()`：全部成功才成功，任一失败则失败
- `Promise.race()`：第一个完成的决定状态
- `Promise.allSettled()`：等待全部完成，返回每个结果
- `Promise.any()`：第一个成功就成功，全部失败才失败


> 🔍 **知识点深度解析**
>
> **作用**：Promise 是对异步操作的标准封装，解决回调地狱、统一异步错误处理。
>
> **原理**：Promise 代表一个未来才会完成的值，有 pending/fulfilled/rejected 三态且不可逆；then/catch 注册回调进入微任务队列，返回新 Promise 以支持链式调用。
>
> **用法要点**：① 状态一旦 settled 不可逆  ② all 全成功才成功、任一失败即失败  ③ race 取最先完成（成功或失败）  ④ allSettled 等待全部并给出每项状态  ⑤ any 取首个成功、全部失败才失败；链式 then 中返回 Promise 会自动展平

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


---
## 7. ES6+ 核心特性

### 7.1 let/const 与块级作用域

- `let`：块级作用域，可重新赋值，不存在变量提升（暂时性死区）
- `const`：块级作用域，声明时必须赋值，不可重新赋值（对象属性可改）


> 🔍 **知识点深度解析**
>
> **作用**：let/const 修复了 var 的变量提升与无块级作用域缺陷，是现代 JS 变量声明首选。
>
> **原理**：let/const 绑定在块级词法环境，存在暂时性死区（声明前访问报错）；const 声明后绑定不可重新赋值（对象内部属性仍可改）。
>
> **用法要点**：① 默认用 const，需重赋值才用 let，避免 var  ② const 声明必须初始化  ③ 块级作用域杜绝循环变量泄漏  ④ TDZ 期间访问抛 ReferenceError  ⑤ for 循环中 let 每次迭代创建独立绑定，修复循环闭包问题

### 7.2 箭头函数

```javascript
const sum = (a, b) => a + b;
const double = n => n * 2; // 单参数可省略括号
const getObj = () => ({ a: 1 }); // 返回对象需括号
```

**特点**：无 this、无 arguments、不能 new、无 prototype。


> 🔍 **知识点深度解析**
>
> **作用**：箭头函数提供简洁语法并固定 this，特别适合回调与函数式写法。
>
> **原理**：箭头函数没有自己的 this/arguments/prototype，其 this 继承自定义处的外层词法作用域，无法通过 call/apply/bind 改变。
>
> **用法要点**：① 单参数可省括号，单表达式可省 return 与 {}  ② 返回对象字面量需用 () 包裹  ③ 不能作为构造函数（不能 new）  ④ 无 arguments，用剩余参数 ...args 代替  ⑤ 适合回调；对象方法若用箭头函数会丢失 this 指向

### 7.3 解构赋值

```javascript
const { name, age } = user;
const [first, second] = arr;
const { name: userName, ...rest } = user; // 重命名 + 剩余
```


> 🔍 **知识点深度解析**
>
> **作用**：解构赋值为从数组/对象中批量提取值提供了简洁语法，大幅提升可读性。
>
> **原理**：编译器将解构转换为逐个按位置（数组）或按属性名（对象）的赋值；可配合默认值、重命名、剩余运算符使用。
>
> **用法要点**：① 对象解构按属性名匹配，可重命名 {a: x}  ② 设置默认值 {a = 1} 仅在 undefined 时生效  ③ 剩余 ...rest 收集剩余项（数组/对象）  ④ 嵌套解构可深入子结构  ⑤ 常用于函数参数与 import 具名导出

### 7.4 模板字符串

```javascript
const msg = `Hello, ${name}! 今年 ${age} 岁。`;
```


> 🔍 **知识点深度解析**
>
> **作用**：模板字符串让字符串插值多行文本更直观，是拼接复杂字符串的首选。
>
> **原理**：用反引号界定，通过 ${} 嵌入任意表达式（其值经 toString 插入）；支持天然换行，编译为字符串拼接。
>
> **用法要点**：① ${expr} 中可写变量、运算、函数调用  ② 多行字符串不再需要 \n 拼接  ③ 可嵌套模板字符串  ④ 配合标签函数（tag`...`）实现自定义模板（i18n、CSS-in-JS）  ⑤ 避免直接拼接用户输入以防 XSS

### 7.5 展开运算符

```javascript
const arr3 = [...arr1, ...arr2]; // 数组合并
const obj2 = { ...obj1, age: 20 }; // 对象合并（浅拷贝）
```


> 🔍 **知识点深度解析**
>
> **作用**：展开运算符用 ... 把可迭代对象“铺开”，常用于复制、合并与传参。
>
> **原理**：在数组/对象字面量中，... 将其元素/可枚举属性逐个展开；复制是浅拷贝，仅复制一层引用。
>
> **用法要点**：① 数组合并 [...a, ...b]，去重 [...new Set(arr)]  ② 对象合并 {...a, ...b} 后者覆盖前者  ③ 函数调用 fn(...args) 替代 apply  ④ 是浅拷贝，嵌套对象共享引用  ⑤ 常与解构剩余配合做“剔除/提取”字段

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


> 🔍 **知识点深度解析**
>
> **作用**：数组遍历方法是函数式处理集合数据的基础，选对方法能让代码更声明式。
>
> **原理**：forEach 纯遍历；map/filter 返回新数组；reduce 按累加器收敛为单值；find/some/every 做查找与判定；它们都不改变原数组（除回调内手动改）。
>
> **用法要点**：① map 用于转换、filter 用于筛选、reduce 最通用  ② forEach 无法用 return/break 中断  ③ find 返回首个匹配元素  ④ some/every 返回布尔  ⑤ reduce 第二参数为初始值，避免空数组无值出错

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


> 🔍 **知识点深度解析**
>
> **作用**：掌握增删改、截取与扁平化等数组方法，才能高效处理日常数据结构。
>
> **原理**：数组是带 length 与整数键的对象；部分方法修改原数组（push/pop/splice/sort/reverse），部分返回新数组（slice/concat/flat 等），理解这一点避免副作用。
>
> **用法要点**：① slice(start,end) 返回子数组、不改原数组  ② splice 原地删除/插入、返回被删项  ③ sort 默认按字符串排序，需传比较函数  ④ flat(n)/flatMap 用于降维  ⑤ 修改原数组的方法在不可变场景需先拷贝；join 转字符串、concat 合并


---
## 9. 内存管理与垃圾回收

### 9.1 垃圾回收机制

- **引用计数**：记录被引用次数，为 0 则回收（循环引用问题）
- **标记清除**：从根对象出发标记可达对象，未标记的回收（现代浏览器主流）


> 🔍 **知识点深度解析**
>
> **作用**：理解 GC 机制有助于写出低内存占用、少泄漏的代码。
>
> **原理**：JS 自动内存管理，主流用“标记-清除”：从根对象（全局、栈上引用）出发标记可达对象，未标记的不可达对象被回收；早期引用计数因循环引用易漏回收，已基本淘汰。
>
> **用法要点**：① 可达性（reachability）是回收判据，而非引用计数  ② 标记-清除会有停顿，V8 用分代/增量回收优化  ③ 新生代（Scavenge）与老生代（Mark-Sweep/Compact）策略不同  ④ WeakMap/WeakSet 的键为弱引用，不阻止回收  ⑤ 手动置 null 可帮助回收

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


> 🔍 **知识点深度解析**
>
> **作用**：识别常见泄漏来源，才能在生产中排查并修复内存增长问题。
>
> **原理**：当本应被回收的对象因仍被引用（全局、闭包、定时器、DOM）而长期存活，就产生内存泄漏，最终拖慢甚至崩溃页面。
>
> **用法要点**：① 意外全局变量（未声明赋值）常驻全局  ② 未 removeEventListener/clearInterval 持续持有  ③ 闭包误持大对象/定时器引用  ④ 游离 DOM 虽移除但 JS 仍引用  ⑤ 用 DevTools Memory 快照对比定位泄漏点


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
