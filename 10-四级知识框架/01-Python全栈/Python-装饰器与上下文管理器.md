---
title: 装饰器与上下文管理器
tags: [#Python全栈/语言核心, 原子笔记, 待完善]
created: 2026-08-13
updated: 2026-08-13
status: 🟡 骨架已填充
source: 
---

# 装饰器与上下文管理器

> Python 最具特色的语法特性，框架大量使用

**所属板块**：[[MOC-Python全栈-四级展开.md|Python全栈]]
**标签**：`#Python全栈/语言核心`
**学习状态**：🟡 骨架已填充（待深入完善）

---

## 📋 四级子知识点清单

| 序号 | 子知识点 | 章节锚点 | 独立笔记 | 状态 |
|------|----------|----------|----------|------|
| 1 | 函数装饰器原理与实现 | [1](#1-函数装饰器原理与实现) | ⬜ 待写 | 🔴 未开始 |
| 2 | 带参数装饰器与类装饰器 | [2](#2-带参数装饰器与类装饰器) | ⬜ 待写 | 🔴 未开始 |
| 3 | functools.wraps 与装饰器副作用 | [3](#3-functools.wraps-与装饰器副作用) | ⬜ 待写 | 🔴 未开始 |
| 4 | 装饰器执行顺序（多层叠加） | [4](#4-装饰器执行顺序（多层叠加）) | ⬜ 待写 | 🔴 未开始 |
| 5 | 上下文管理器协议（__enter__/__exit__） | [5](#5-上下文管理器协议（__enter__/__exit__）) | ⬜ 待写 | 🔴 未开始 |
| 6 | contextlib 简化写法 | [6](#6-contextlib-简化写法) | ⬜ 待写 | 🔴 未开始 |

---

## 📖 核心内容

### 1. 函数装饰器原理与实现

装饰器是 Python 的一种语法糖，用于在不修改原函数代码的情况下扩展函数功能。本质上是一个接收函数并返回新函数的高阶函数。

**核心要点**：
- 函数是一等公民：可以作为参数传递、作为返回值、赋值给变量
- @decorator 语法糖：等价于 func = decorator(func)
- 带参数的装饰器：需要三层嵌套函数
- functools.wraps：保留原函数的元信息（名称、文档字符串）
- 类装饰器：通过 __call__ 方法实现

**代码示例**：
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时: {time.time() - start:.2f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "done"

# 带参数的装饰器
def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

**常见问题**：
Q: 装饰器和继承有什么区别？
A: 装饰器是组合模式，动态扩展功能；继承是静态的，通过子类扩展。装饰器更灵活，可叠加使用。

---
---

### 2. 带参数装饰器与类装饰器

装饰器是 Python 的一种语法糖，用于在不修改原函数代码的情况下扩展函数功能。本质上是一个接收函数并返回新函数的高阶函数。

**核心要点**：
- 函数是一等公民：可以作为参数传递、作为返回值、赋值给变量
- @decorator 语法糖：等价于 func = decorator(func)
- 带参数的装饰器：需要三层嵌套函数
- functools.wraps：保留原函数的元信息（名称、文档字符串）
- 类装饰器：通过 __call__ 方法实现

**代码示例**：
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时: {time.time() - start:.2f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "done"

# 带参数的装饰器
def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

**常见问题**：
Q: 装饰器和继承有什么区别？
A: 装饰器是组合模式，动态扩展功能；继承是静态的，通过子类扩展。装饰器更灵活，可叠加使用。

---
---

### 3. functools.wraps 与装饰器副作用

装饰器是 Python 的一种语法糖，用于在不修改原函数代码的情况下扩展函数功能。本质上是一个接收函数并返回新函数的高阶函数。

**核心要点**：
- 函数是一等公民：可以作为参数传递、作为返回值、赋值给变量
- @decorator 语法糖：等价于 func = decorator(func)
- 带参数的装饰器：需要三层嵌套函数
- functools.wraps：保留原函数的元信息（名称、文档字符串）
- 类装饰器：通过 __call__ 方法实现

**代码示例**：
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时: {time.time() - start:.2f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "done"

# 带参数的装饰器
def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

**常见问题**：
Q: 装饰器和继承有什么区别？
A: 装饰器是组合模式，动态扩展功能；继承是静态的，通过子类扩展。装饰器更灵活，可叠加使用。

---
---

### 4. 装饰器执行顺序（多层叠加）

装饰器是 Python 的一种语法糖，用于在不修改原函数代码的情况下扩展函数功能。本质上是一个接收函数并返回新函数的高阶函数。

**核心要点**：
- 函数是一等公民：可以作为参数传递、作为返回值、赋值给变量
- @decorator 语法糖：等价于 func = decorator(func)
- 带参数的装饰器：需要三层嵌套函数
- functools.wraps：保留原函数的元信息（名称、文档字符串）
- 类装饰器：通过 __call__ 方法实现

**代码示例**：
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时: {time.time() - start:.2f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "done"

# 带参数的装饰器
def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

**常见问题**：
Q: 装饰器和继承有什么区别？
A: 装饰器是组合模式，动态扩展功能；继承是静态的，通过子类扩展。装饰器更灵活，可叠加使用。

---
---

### 5. 上下文管理器协议（__enter__/__exit__）

上下文管理器协议（__enter__/__exit__）是Python全栈领域中的重要概念，指在特定场景下用于解决特定问题的方法或机制。理解其原理和适用场景对于构建高质量系统至关重要。

**核心要点**：
- 基本概念与定义：理解上下文管理器协议（__enter__/__exit__）的核心含义和解决的问题
- 工作原理与机制：掌握底层实现逻辑和关键流程
- 适用场景与边界：明确什么时候使用、什么时候不适合
- 最佳实践与注意事项：总结实际使用中的经验和坑点
- 与相关技术的对比：理解差异化优势和选型依据

**代码示例**：
# 上下文管理器协议（__enter__/__exit__） 示例
# 基础用法
# TODO: 根据具体知识点补充代码示例

**常见问题**：
Q: 上下文管理器协议（__enter__/__exit__）和相关技术有什么区别？
A: 核心区别在于设计目标和适用场景。上下文管理器协议（__enter__/__exit__）更侧重于特定场景下的优化，而相关技术可能有更广泛的适用性。

---
---

### 6. contextlib 简化写法

contextlib 简化写法是工程实践中总结出的最佳实践，旨在解决特定场景下的共性问题。正确应用可以显著提升开发效率和系统质量。

**核心要点**：
- 基本概念与定义：理解contextlib 简化写法的核心含义和解决的问题
- 工作原理与机制：掌握底层实现逻辑和关键流程
- 适用场景与边界：明确什么时候使用、什么时候不适合
- 最佳实践与注意事项：总结实际使用中的经验和坑点
- 与相关技术的对比：理解差异化优势和选型依据


**常见问题**：
Q: contextlib 简化写法在生产环境中有哪些注意事项？
A: 需要关注性能瓶颈、错误处理、资源清理、监控告警和安全边界，确保系统稳定可靠。

---
---


---

## 🔗 关联知识

### 前置依赖
- 无特殊前置要求

### 后续延伸
- 

### 跨板块关联
- 待补充

### 相关笔记
- 

---

## 💡 实践要点

- 

---

## ❓ 常见问题

1. **Q**: 
   **A**: 

---

## 📚 参考资料

- 

---

## 📝 学习日志

| 日期 | 学习内容 | 状态 |
|------|----------|------|
| 2026-08-13 | 创建笔记骨架 | 🔴 未开始 |
| 2026-08-13 | 批量填充四级子知识点内容 | 🟡 骨架已填充 |

---

[[MOC-Python全栈-四级展开.md|← 返回Python全栈 MOC]] | [[10-四级知识框架/00-总控/四级框架总索引|🗺️ 返回四级框架总索引]] | [[Home|🏠 返回首页]]
