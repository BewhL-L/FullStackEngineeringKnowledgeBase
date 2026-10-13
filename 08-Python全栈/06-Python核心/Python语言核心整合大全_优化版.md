---
title: Python 语言核心整合大全
tags: [MOC, Python, 语言核心, 实战, 性能优化, 工程化]
category: Python全栈
created: 2026-08-25
updated: 2026-09-09
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[Python语言基础与进阶知识点系统梳理_优化版]]"]
aliases: [Python语言核心整合大全_优化版]
---

# Python 语言核心整合大全

> **适用人群**：已掌握 Python 基础语法与进阶特性（装饰器、生成器、上下文管理器、面向对象、并发编程等），希望从"会写代码"跃迁到"写好代码、写快代码、写可维护代码"的开发者。
>
> **前置知识**：建议先完成 [[Python-语法基础与数据结构]] 与 [[Python语言基础与进阶知识点系统梳理_优化版]] 的学习。本文档不再重复语法入门，直接在进阶基础上讲解整合与实战。
>
> **与前两篇的衔接**：第一篇解决"语法是什么"，第二篇解决"特性怎么用"，本篇解决"在真实工程中如何把所有特性组合起来、用对、用快、用稳"。
>
> **老手思维方式**：
> - **先测量，后优化** — 不靠直觉猜瓶颈，用 profiler 说话
> - **可读性优先，性能按需** — 先写对，再写快；可读性是长期性能
> - **显式优于隐式** — 依赖注入优于全局状态，类型注解优于动态魔法
> - **防御性编程** — 假设输入会坏、网络会断、磁盘会满
> - **工程素养** — 测试、文档、CI、版本管理不是可选项，是交付的一部分

---

## 1. Pythonic编程风格

Pythonic 不是"用了某个语法糖"，而是一种**利用 Python 语言特性写出简洁、可读、高效代码的思维方式**。老手写的代码，一眼就能看出"这是 Python 该有的样子"。

### 1.1 Python之禅与编程哲学

#### import this 逐条解读

```python
>>> import this
The Zen of Python, by Tim Peters

Beautiful is better than ugly.             # 代码美学：格式、命名、结构都要美
Explicit is better than implicit.          # 显式优于隐式：别靠副作用传递信息
Simple is better than complex.             # 简单优于复杂：能用函数解决就别上类
Complex is better than complicated.        # 复杂优于费解：必要的复杂可以，绕弯子不行
Flat is better than nested.                # 扁平优于嵌套：提前返回，少写 if 套 if
Sparse is better than dense.               # 稀疏优于密集：留白和空行是可读性
Readability counts.                        # 可读性最重要：代码是写给人看的
Special cases aren't special enough to break the rules.  # 规则优先，别为特例开后门
Although practicality beats purity.        # 但实用主义胜过纯粹教条
Errors should never pass silently.         # 错误不该静默吞掉：要么处理，要么抛出
Unless explicitly silenced.                # 除非你明确知道为什么要静默
In the face of ambiguity, refuse the temptation to guess. # 有歧义就别猜，抛异常
There should be one-- and preferably only one --obvious way to do it. # 最好只有一种显然的做法
Although that way may not be obvious at first unless you're Dutch.     # 但显然性需要学习
Now is better than never.                  # 现在动手胜过永不开始
Although never is often better than *right* now. # 但仓促上线不如不做
If the implementation is hard to explain, it's a bad idea.  # 难解释的实现就是坏方案
If the implementation is easy to explain, it may be a good idea. # 好解释的才可能是好方案
Namespaces are one honking great idea -- let's do more of those! # 命名空间是好东西，多用
```

#### Pythonic vs 非Pythonic对比

| 场景 | 非 Pythonic（新手写法） | Pythonic（老手写法） |
|------|------------------------|---------------------|
| 遍历索引 | `for i in range(len(items)): x = items[i]` | `for x in items:` |
| 同时要索引 | `for i in range(len(items)): print(i, items[i])` | `for i, x in enumerate(items):` |
| 反向遍历 | `for i in range(len(items)-1, -1, -1):` | `for x in reversed(items):` |
| 字典安全取值 | `if key in d: v = d[key] else: v = default` | `v = d.get(key, default)` |
| 字符串拼接 | `s = ''; for x in items: s += x` | `s = ''.join(items)` |
| 文件读取 | `f = open(path); data = f.read(); f.close()` | `with open(path) as f: data = f.read()` |
| 交换变量 | `tmp = a; a = b; b = tmp` | `a, b = b, a` |
| 真值判断 | `if len(items) > 0:` | `if items:` |
| 条件赋值 | `if x: result = x else: result = y` | `result = x or y` |
| 三目运算 | `if cond: a = 1 else: a = 2` | `a = 1 if cond else 2` |

> 🏆 **老手经验**：Pythonic 不是炫技。`join` 比 `+=` 快是因为字符串不可变，`+=` 每次都创建新对象；`with` 比手动 `close` 安全是因为异常时也能释放资源。每一个 Pythonic 写法背后都有工程理由。

#### 社区文化与PEP

- **PEP 8**：代码风格指南，是底线不是天花板
- **PEP 20**：Python 之禅
- **PEP 257**：文档字符串规范
- **PEP 484**：类型提示
- **PEP 621**：pyproject.toml 项目元数据
- **PEP 8000系列**：治理模型

> 💡 **提示**：提交 PR 前跑一遍 `ruff check .` 和 `black --check .`，比在 review 里被人挑格式问题高效得多。

---

### 1.2 优雅的数据结构用法

#### 推导式进阶

推导式是 Python 最具辨识度的语法之一，但老手知道**什么时候该用、什么时候不该用**。

```python
# 列表推导式 — 适合简单转换
squares = [x**2 for x in range(100) if x % 2 == 0]

# 字典推导式 — 构建映射
word_counts = {word: len(word) for word in text.split()}

# 集合推导式 — 去重
unique_lengths = {len(word) for word in text.split()}

# 生成器表达式 — 大数据量时省内存
total = sum(x**2 for x in range(10_000_000))  # 不创建中间列表

# 嵌套推导式 — 注意可读性，超过两层就拆开
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = [x for row in matrix for x in row]  # 顺序：外层循环在前
```

> ⚠️ **反模式**：不要在推导式里写复杂逻辑或副作用。
> ```python
> # 坏：推导式里有副作用
> [print(x) for x in items]  # 这不是在构建列表，是在滥用语法
>
> # 好：用普通循环
> for x in items:
>     print(x)
> ```

#### 解包技巧

```python
# 基础解包
a, b, c = [1, 2, 3]

# * 收集剩余元素
first, *rest = [1, 2, 3, 4, 5]  # first=1, rest=[2,3,4,5]
*head, last = [1, 2, 3, 4, 5]   # head=[1,2,3,4], last=5
first, *middle, last = [1, 2, 3, 4, 5]  # middle=[2,3,4]

# ** 解包字典
defaults = {"host": "localhost", "port": 8080}
config = {**defaults, "port": 9090, "debug": True}
# {'host': 'localhost', 'port': 9090, 'debug': True}

# 嵌套解包
data = {"user": {"name": "Alice", "roles": ["admin", "user"]}}
(user_info,) = [data["user"]]  # 从单元素列表中解包
name, (role1, role2) = data["user"]["name"], data["user"]["roles"]

# walrus 运算符（海象运算符）— 在表达式中赋值
# 场景：读取文件直到空行，避免重复调用
while (line := f.readline()) != "":
    process(line)

# 场景：正则匹配后直接使用匹配对象
if (match := re.search(pattern, text)) is not None:
    print(match.group(1))
```

> 🔥 **面试高频考点**：`*args` 和 `**kwargs` 的区别？`*` 收集位置参数为元组，`**` 收集关键字参数为字典。函数定义中 `*` 之后的参数必须用关键字传递（keyword-only arguments）。

#### 枚举与zip的优雅用法

```python
# enumerate — 同时获取索引和值
for idx, item in enumerate(items, start=1):  # start 指定起始索引
    print(f"{idx}. {item}")

# zip — 并行遍历多个可迭代对象
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name} is {age}")

# zip 不等长时以最短为准；用 zip_longest 填充
from itertools import zip_longest
for name, score in zip_longest(names, [90, 85], fillvalue=0):
    print(name, score)

# zip 转置矩阵
transposed = list(zip(*matrix))  # [(1,4,7), (2,5,8), (3,6,9)]

# 同时用 enumerate 和 zip
for i, (name, age) in enumerate(zip(names, ages)):
    print(f"{i}: {name}={age}")
```

#### any()/all()/sum()的函数式风格

```python
# any — 任一为真即真，短路求值
has_admin = any(user.role == "admin" for user in users)

# all — 全部为真才真，短路求值
all_valid = all(user.is_active for user in users)

# sum — 求和，可指定起始值
total_score = sum(user.score for user in users)
# 注意：sum 对字符串拼接会报错，用 ''.join()

# 组合使用：检查所有用户的邮箱都已验证，且至少有一个管理员
is_valid_team = (
    all(user.email_verified for user in users)
    and any(user.role == "admin" for user in users)
)

# 实战：配置校验
required_fields = ["name", "email", "password"]
config = {"name": "Alice", "email": "alice@example.com"}
missing = [f for f in required_fields if f not in config]
if missing:
    raise ValueError(f"Missing required fields: {missing}")
```

> 🏆 **老手经验**：`any()` 和 `all()` 用生成器表达式作为参数时是**短路求值**的——找到第一个满足/不满足的元素就停止，不会遍历整个集合。这在大数据集上性能差异巨大。

---

### 1.3 优雅的控制流

#### 字典替代switch（映射表模式）

Python 3.10+ 有 `match/case`，但在更广泛的版本兼容场景中，**字典映射表**是更 Pythonic 的 switch 替代。

```python
# 新手写法：长 if-elif 链
def handle_action(action: str, data: dict) -> None:
    if action == "create":
        create_item(data)
    elif action == "update":
        update_item(data)
    elif action == "delete":
        delete_item(data)
    elif action == "list":
        list_items(data)
    else:
        raise ValueError(f"Unknown action: {action}")

# 老手写法：映射表 + 默认处理
from typing import Callable, Dict

def handle_action(action: str, data: dict) -> None:
    handlers: Dict[str, Callable[[dict], None]] = {
        "create": create_item,
        "update": update_item,
        "delete": delete_item,
        "list": list_items,
    }
    handler = handlers.get(action)
    if handler is None:
        raise ValueError(f"Unknown action: {action}")
    handler(data)

# 进阶：带参数的映射表（partial 绑定参数）
from functools import partial

handlers = {
    "create": partial(create_item, audit=True),
    "delete": partial(delete_item, soft_delete=True),
}

# Python 3.10+ match/case（适合复杂模式匹配）
def handle_command(cmd: str) -> str:
    match cmd.split():
        case ["go", direction]:
            return f"Moving {direction}"
        case ["attack", target] if target in enemies:
            return f"Attacking {target}"
        case ["quit" | "exit"]:
            return "Goodbye"
        case _:
            return "Unknown command"
```

#### 提前返回替代深层嵌套

```python
# 反模式：深层嵌套（箭头代码）
def calculate_discount(user: User, order: Order) -> float:
    if user.is_active:
        if order.total > 100:
            if user.has_membership:
                if user.membership_level == "gold":
                    return 0.2
                else:
                    return 0.1
            else:
                return 0.05
        else:
            return 0
    else:
        return 0

# Pythonic：提前返回（卫语句）
def calculate_discount(user: User, order: Order) -> float:
    if not user.is_active:
        return 0
    if order.total <= 100:
        return 0
    if not user.has_membership:
        return 0.05
    if user.membership_level == "gold":
        return 0.2
    return 0.1
```

> 🏆 **老手经验**：嵌套深度超过 3 层就该考虑重构。提前返回（early return / guard clause）让主逻辑保持在最外层，阅读时不需要在脑子里维护"当前在哪个 if 里"的状态栈。

#### 上下文管理器替代try/finally

```python
# 基础：文件操作
with open("data.txt") as f:
    data = f.read()
# 离开 with 块时自动关闭，即使发生异常

# 多个上下文管理器
with open("input.txt") as fin, open("output.txt", "w") as fout:
    fout.write(fin.read())

# 自定义上下文管理器 — 基于类
class Timer:
    """计时上下文管理器，记录代码块执行时间"""
    def __init__(self, name: str = "operation") -> None:
        self.name = name
        self.elapsed: float = 0.0

    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.elapsed = time.perf_counter() - self.start
        logger.info("%s took %.3fs", self.name, self.elapsed)
        return False  # 不吞异常

# 使用
with Timer("database query") as t:
    results = db.execute("SELECT ...")
print(f"Query took {t.elapsed:.3f}s")

# 自定义上下文管理器 — 基于生成器（更简洁）
from contextlib import contextmanager

@contextmanager
def temporary_change(obj, attr, value):
    """临时修改对象属性，退出时恢复"""
    old_value = getattr(obj, attr)
    setattr(obj, attr, value)
    try:
        yield
    finally:
        setattr(obj, attr, old_value)

# 使用
with temporary_change(settings, "debug", True):
    run_debug_operation()
# settings.debug 自动恢复
```

#### 迭代器替代索引循环

```python
# 反模式：用索引遍历
for i in range(len(data)):
    process(data[i])

# Pythonic：直接迭代
for item in data:
    process(item)

# 需要修改元素时，用 enumerate
for i, item in enumerate(data):
    if item.is_expired():
        data[i] = item.refresh()

# 迭代器协议 — 自定义可迭代对象
class ChunkReader:
    """按块读取大文件的可迭代对象"""
    def __init__(self, filepath: str, chunk_size: int = 8192) -> None:
        self.filepath = filepath
        self.chunk_size = chunk_size

    def __iter__(self):
        with open(self.filepath, "rb") as f:
            while chunk := f.read(self.chunk_size):
                yield chunk

# 使用：不需要把整个文件读入内存
for chunk in ChunkReader("huge_file.bin"):
    process_chunk(chunk)
```

---

### 1.4 常用Pythonic惯用法

#### EAFP风格（先斩后奏）

EAFP（Easier to Ask for Forgiveness than Permission）是 Python 社区推崇的编程风格：**先尝试操作，失败了再处理异常**，而不是先检查条件再操作。

```python
# LBYL（Look Before You Leap）— 先检查
def get_item_lbyl(d: dict, key: str, default=None):
    if key in d:          # 第一次查找
        return d[key]     # 第二次查找（竞态条件窗口）
    return default

# EAFP — 先尝试
def get_item_eafp(d: dict, key: str, default=None):
    try:
        return d[key]     # 一次查找
    except KeyError:
        return default

# 实战场景：文件操作
# LBYL：检查文件是否存在（TOCTOU 竞态：检查后文件可能被删除）
if os.path.exists("config.json"):
    with open("config.json") as f:
        config = json.load(f)
else:
    config = {}

# EAFP：直接尝试打开（更安全，无竞态）
try:
    with open("config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}

# 实战场景：类型转换
def parse_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
```

> ⚠️ **注意**：EAFP 不是"用异常做正常控制流"。异常应该用于**异常情况**，如果某个分支在正常流程中频繁触发（比如 50% 的概率），用条件判断更合适。经验法则：异常路径触发率 < 10% 时 EAFP 性能更好。

#### 管道式数据处理

```python
# 管道式：每个步骤清晰，数据单向流动
result = (
    raw_data
    .filter(lambda x: x is not None)
    .map(lambda x: x.strip())
    .filter(lambda x: len(x) > 0)
    .map(lambda x: x.lower())
    .collect()
)

# Python 原生实现管道（生成器链）
def pipe(data, *funcs):
    """将多个函数串联成管道"""
    result = data
    for func in funcs:
        result = func(result)
    return result

# 使用
cleaned = pipe(
    raw_text,
    str.lower,
    lambda s: re.sub(r'[^\w\s]', '', s),
    str.split,
    set,
)

# 更实用的：生成器管道处理大数据
def read_lines(filepath):
    with open(filepath, encoding="utf-8") as f:
        yield from f

def remove_comments(lines):
    return (line for line in lines if not line.strip().startswith("#"))

def strip_lines(lines):
    return (line.strip() for line in lines)

def filter_nonempty(lines):
    return (line for line in lines if line)

# 组合：整个管道是惰性的，内存占用恒定
lines = filter_nonempty(strip_lines(remove_comments(read_lines("config.txt"))))
for line in lines:
    process(line)
```

#### 函数组合

```python
from functools import reduce
from typing import Callable, Any

def compose(*funcs: Callable) -> Callable:
    """函数组合：compose(f, g, h)(x) == f(g(h(x)))"""
    def composed(x: Any) -> Any:
        return reduce(lambda acc, f: f(acc), reversed(funcs), x)
    return composed

# 使用
sanitize = compose(
    str.lower,
    lambda s: re.sub(r'\s+', ' ', s),
    str.strip,
)
clean = sanitize("  Hello   World  ")  # "hello world"
```

#### 不可变优先

```python
# 可变对象的陷阱
def append_item(item, target=[]):  # 可变默认参数！
    target.append(item)
    return target
# 多次调用会累积：append_item(1) -> [1], append_item(2) -> [1, 2]

# 正确做法：不可变默认参数
def append_item(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target

# 不可变数据类
from dataclasses import dataclass

@dataclass(frozen=True)  # frozen=True 使实例不可变
class Point:
    x: float
    y: float

    def move(self, dx: float, dy: float) -> "Point":
        """不可变对象的修改返回新实例"""
        return Point(self.x + dx, self.y + dy)

# 使用：不可变对象天然线程安全，可作为字典键
p1 = Point(1, 2)
p2 = p1.move(3, 4)  # p1 不变，p2 是新对象
```

#### 命名即文档

```python
# 坏命名：需要注释解释
def process(d):
    for i in d:
        if i[2] > 100:  # 什么是 i[2]？什么是 100？
            ...

# 好命名：自解释
MIN_ORDER_TOTAL = 100

def process_high_value_orders(orders: list[Order]) -> None:
    for order in orders:
        if order.total > MIN_ORDER_TOTAL:
            ...

# 布尔变量/函数用 is/has/can/should 前缀
is_valid = user.email_verified and user.is_active
has_permission = user.role in ("admin", "editor")
can_delete = is_valid and has_permission

# 复杂条件提取为命名函数
def is_eligible_for_discount(user: User, order: Order) -> bool:
    return (
        user.is_active
        and order.total > 100
        and user.has_membership
        and not user.has_unpaid_balance()
    )

if is_eligible_for_discount(user, order):
    apply_discount(order)
```

---

### 本章总结

Pythonic 风格的核心不是记住语法糖清单，而是理解每个写法背后的**工程理由**：
- 推导式和生成器表达式平衡了简洁性与内存效率
- 解包和 `enumerate/zip` 消除了索引操作，减少 off-by-one 错误
- 提前返回和上下文管理器降低了认知负担和资源泄漏风险
- EAFP 风格利用了 Python 异常机制的高效性，同时避免了竞态条件
- 不可变优先和良好命名是长期可维护性的基石

### 思考题/实战练习

1. **重构练习**：找一段你写的嵌套超过 3 层的代码，用提前返回重构，对比可读性。
2. **性能对比**：用 `timeit` 对比 `for` 循环拼接字符串 vs `''.join()`，在 10 万次拼接下差异是多少？
3. **EAFP vs LBYL**：写一个函数读取 JSON 配置文件，分别用两种风格实现，分析在文件不存在、JSON 格式错误两种异常下的行为差异。
4. **上下文管理器**：实现一个 `retry_on_exception` 上下文管理器，支持指定重试次数和异常类型，在数据库操作场景中使用。
5. **映射表模式**：将一个 5 个分支以上的 `if-elif` 链重构为字典映射表，并支持通过装饰器注册新的处理函数。

---

## 2. 性能优化

性能优化是老手区别于新手的核心能力之一。但优化的第一原则是：**不要过早优化**。Donald Knuth 的名言"过早优化是万恶之源"在 Python 社区被反复强调，因为 Python 的可读性和开发效率本身就是最大的性能优势。

### 2.1 性能分析方法论

#### 不要过早优化

> 🏆 **老手经验**：90% 的性能问题集中在 10% 的代码里。在没有测量之前，你对瓶颈的猜测大概率是错的。先写出清晰正确的代码，再用 profiler 找到真正的热点，最后只优化热点。

优化的优先级排序：
1. **算法优化** — O(n²) → O(n log n)，数量级提升
2. **数据结构优化** — list 查找 → set/dict 查找，O(n) → O(1)
3. **I/O 优化** — 同步 → 异步/批量，减少等待
4. **语言层面优化** — 内置函数、生成器、C 扩展
5. **硬件/部署优化** — 缓存、CDN、负载均衡

#### 性能分析流程

```text
定位（Find） → 测量（Measure） → 优化（Optimize） → 验证（Verify）
     ↑                                          ↓
     └──────── 回归监控（持续测量）──────────────┘
```

1. **定位**：用 cProfile 找到耗时最多的函数
2. **测量**：用 timeit/line_profiler 精确测量目标代码
3. **优化**：针对瓶颈应用优化策略
4. **验证**：重新测量，确认优化有效且没有引入回归

#### 测量工具

```python
# timeit — 微基准测试，精确测量小段代码
import timeit

# 命令行方式
# python -m timeit -s "text = 'hello world'" "text.upper()"

# 编程方式
setup = "from collections import Counter; import random; data = [random.randint(1,100) for _ in range(10000)]"
stmt = "Counter(data)"
result = timeit.timeit(stmt, setup=setup, number=100)
print(f"Average: {result/100*1000:.2f}ms")

# cProfile — 函数级性能分析
import cProfile
import pstats
from io import StringIO

def profile_function(func, *args, **kwargs):
    """装饰器：分析函数性能"""
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()

    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative")  # 按累计时间排序
    stats.print_stats(20)  # 打印前20个
    print(stream.getvalue())
    return result

# line_profiler — 行级性能分析（需要 pip install line_profiler）
# 用 @profile 装饰目标函数，然后运行 kernprof -l -v script.py
@profile
def slow_function(data):
    result = []
    for item in data:          # 每一行的耗时都会被统计
        processed = item * 2   #
        result.append(processed)  #
    return result

# memory_profiler — 内存分析（pip install memory_profiler）
# python -m memory_profiler script.py
from memory_profiler import profile

@profile
def load_large_file():
    with open("large.txt") as f:
        data = f.readlines()  # 这一行会显示内存跳增
    return data
```

#### 火焰图（py-spy）

```bash
# py-spy — 非侵入式采样 profiler，不需要修改代码
# 安装：pip install py-spy

# 对正在运行的进程采样（需要 PID）
py-spy record -o profile.svg --pid 12345

# 运行脚本并生成火焰图
py-spy record -o profile.svg -- python my_script.py

# 实时查看（top 模式）
py-spy top --pid 12345

# dump 调用栈（调试卡死的进程）
py-spy dump --pid 12345
```

> 💡 **提示**：火焰图的阅读方法——横轴是采样占比（越宽越耗时），纵轴是调用栈深度。找"平顶"（顶部宽的方块），那就是实际执行耗时的函数。

---

### 2.2 算法与数据结构优化

#### 时间复杂度选择

| 操作 | list | dict | set | tuple |
|------|------|------|-----|-------|
| 索引访问 | O(1) | O(1) | - | O(1) |
| 成员检查 `in` | O(n) | O(1) | O(1) | O(n) |
| 插入末尾 | O(1) | O(1) | O(1) | - |
| 删除元素 | O(n) | O(1) | O(1) | - |
| 排序 | O(n log n) | - | - | O(n log n) |

#### 用set/dict替代list查找

```python
# 反模式：在 list 中反复查找
def find_duplicates(items: list) -> list:
    seen = []
    duplicates = []
    for item in items:
        if item in seen:       # O(n) 查找
            duplicates.append(item)
        else:
            seen.append(item)
    return duplicates
# 总时间复杂度 O(n²)

# Pythonic：用 set
def find_duplicates(items: list) -> list:
    seen = set()
    duplicates = []
    for item in items:
        if item in seen:       # O(1) 查找
            duplicates.append(item)
        else:
            seen.add(item)
    return duplicates
# 总时间复杂度 O(n)

# 基准测试对比（10万元素）
# list 版本：~5 秒
# set 版本：~0.01 秒
# 性能提升：500 倍
```

#### 用生成器节省内存

```python
# 反模式：构建巨大的中间列表
def process_file(filepath: str) -> list:
    with open(filepath) as f:
        lines = f.readlines()  # 全部读入内存
    results = []
    for line in lines:
        if line.startswith("#"):
            continue
        results.append(line.strip().upper())
    return results

# Pythonic：生成器管道，内存恒定
def process_file(filepath: str):
    with open(filepath) as f:
        for line in f:                    # 逐行读取
            if line.startswith("#"):
                continue
            yield line.strip().upper()

# 内存对比：处理 1GB 文件
# list 版本：内存峰值 > 1GB
# 生成器版本：内存峰值 < 10MB
```

#### 缓存结果（lru_cache/functools.cache）

```python
from functools import lru_cache, cache
from typing import List

# 斐波那契：无缓存 O(2^n)，有缓存 O(n)
@lru_cache(maxsize=128)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

# Python 3.9+：cache 是 lru_cache(maxsize=None) 的简写
@cache
def expensive_query(user_id: int) -> dict:
    """模拟数据库查询，结果缓存"""
    return db.fetch_user(user_id)

# 带缓存失效的场景：手动清除
def update_user(user_id: int, data: dict) -> None:
    db.update_user(user_id, data)
    expensive_query.cache_clear()  # 清除所有缓存
    # 或精确清除：expensive_query.cache_clear() 不支持单个清除
    # 需要单个清除时用自定义缓存

# 自定义 TTL 缓存
from functools import wraps
import time

def ttl_cache(seconds: int = 60):
    """带过期时间的缓存装饰器"""
    def decorator(func):
        cache = {}
        @wraps(func)
        def wrapper(*args):
            now = time.time()
            if args in cache:
                result, timestamp = cache[args]
                if now - timestamp < seconds:
                    return result
            result = func(*args)
            cache[args] = (result, now)
            return result
        return wrapper
    return decorator
```

> 🔥 **面试高频考点**：`lru_cache` 的原理？用字典存储参数→结果的映射，基于最近最少使用策略淘汰。注意：参数必须是可哈希的，因此不能传 list/dict 作为参数。

#### 内置函数优先（C实现）

```python
# 内置函数用 C 实现，比 Python 循环快得多
numbers = list(range(1_000_000))

# 慢：Python 循环
total = 0
for n in numbers:
    total += n

# 快：内置 sum（C 实现）
total = sum(numbers)

# 慢：Python 循环找最大
max_val = numbers[0]
for n in numbers:
    if n > max_val:
        max_val = n

# 快：内置 max
max_val = max(numbers)

# 慢：手动过滤
evens = []
for n in numbers:
    if n % 2 == 0:
        evens.append(n)

# 快：列表推导式（仍在 Python 层，但比 append 循环快）
evens = [n for n in numbers if n % 2 == 0]

# 更快：filter + lambda（略慢于推导式，但适合函数式风格）
evens = list(filter(lambda n: n % 2 == 0, numbers))

# 字符串处理：用 str 方法而非正则
# 简单替换用 str.replace，复杂模式才用 re
text = "hello world"
result = text.replace("world", "python")  # 比 re.sub 快 5-10 倍
```

---

### 2.3 内存优化

#### __slots__大规模对象

```python
# 普通对象：每个实例有 __dict__，内存开销大
class Point:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z

# 100万个 Point 实例：约 200MB+（每个实例 ~200B 字典开销）

# 使用 __slots__：禁止动态属性，节省内存
class Point:
    __slots__ = ("x", "y", "z")  # 预声明属性
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z

# 100万个 Point 实例：约 56MB（每个实例 ~56B）
# 内存节省：约 70%
# 同时属性访问更快（不需要哈希查找）

# 注意事项：
# 1. __slots__ 的类不能动态添加属性
# 2. 继承时子类也需要定义 __slots__
# 3. 不能与 __dict__ 同时使用（除非在 __slots__ 中包含 '__dict__'）
# 4. 不能使用弱引用（除非在 __slots__ 中包含 '__weakref__'）
```

#### array模块

```python
import array

# list 存储的是 PyObject 指针，每个 int 元素实际占 28B（对象）+ 8B（指针）
# array 存储的是原始 C 类型，紧凑排列

# 'i' = signed int (4B), 'f' = float (4B), 'd' = double (8B)
int_array = array.array("i", range(1_000_000))  # 约 4MB
float_array = array.array("d", [1.0, 2.0, 3.0])  # 约 24B

# list of int：100万元素约 36MB（28B对象 + 8B指针）
# array of int：100万元素约 4MB
# 内存节省：约 90%

# 适用场景：大量数值数据、需要传递给 C 库、二进制文件读写
# 不适用：需要混合类型、需要频繁插入删除（array 插入是 O(n)）
```

#### 数据类优化

```python
from dataclasses import dataclass

# 普通 dataclass（有 __dict__）
@dataclass
class User:
    id: int
    name: str
    email: str

# 优化：slots=True（Python 3.10+）
@dataclass(slots=True)
class User:
    id: int
    name: str
    email: str
# 自动生成 __slots__，内存节省约 40-50%

# 进一步：用更紧凑的类型
from typing import Final

@dataclass(slots=True)
class User:
    id: int
    name: str
    email: str
    is_active: bool = True  # bool 只占 1B（在 CPython 中是单例）
```

#### 流式处理大文件

```python
# 反模式：一次性读取
with open("10gb_file.txt", encoding="utf-8") as f:
    content = f.read()  # 内存爆炸
    for line in content.split("\n"):
        process(line)

# 正确：逐行迭代（文件对象本身就是迭代器）
with open("10gb_file.txt", encoding="utf-8") as f:
    for line in f:  # 每次只读一行到内存
        process(line.strip())

# 二进制文件：按块读取
def process_binary(filepath: str, chunk_size: int = 1024*1024) -> None:
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):  # 每次读 1MB
            process_chunk(chunk)

# CSV 大文件：用 csv 模块的迭代器
import csv
with open("large.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:  # 逐行解析，不加载全部
        process_row(row)

# JSON 大文件：用 ijson 流式解析（pip install ijson）
import ijson
with open("large.json", "rb") as f:
    for item in ijson.items(f, "items.item"):
        process(item)
```

#### 内存映射mmap

```python
import mmap

# mmap 将文件映射到虚拟内存，由 OS 管理页面换入换出
# 比 read() 更高效：不需要在内核空间和用户空间之间复制数据
def search_large_file(filepath: str, pattern: bytes) -> list[int]:
    """在大文件中搜索模式，使用 mmap"""
    positions = []
    with open(filepath, "rb") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
            start = 0
            while True:
                pos = mm.find(pattern, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
    return positions

# mmap 的优势：
# 1. 内存占用低：OS 只加载访问到的页面（通常 4KB）
# 2. 随机访问快：像操作 bytearray 一样操作文件
# 3. 可共享：多个进程可以映射同一个文件，共享内存
# 适用场景：大文件随机访问、进程间共享数据、数据库索引
```

#### 弱引用与循环引用

```python
import weakref

# 循环引用导致内存泄漏的典型场景
class Node:
    def __init__(self, value):
        self.value = value
        self.children = []
        self.parent = None  # 指向父节点，形成循环引用

    def add_child(self, child):
        child.parent = self  # 循环引用：child.parent -> self, self.children -> child
        self.children.append(child)

# 虽然 Python 有分代垃圾回收器可以回收循环引用，
# 但如果对象定义了 __del__，循环引用将无法被回收！

# 解决方案：用弱引用打破循环
class Node:
    def __init__(self, value):
        self.value = value
        self.children = []
        self._parent_ref = None  # 存储弱引用

    @property
    def parent(self):
        if self._parent_ref is not None:
            return self._parent_ref()  # 弱引用调用返回对象或 None
        return None

    @parent.setter
    def parent(self, value):
        if value is not None:
            self._parent_ref = weakref.ref(value)
        else:
            self._parent_ref = None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

# weakref 的其他用途：
# - 缓存：不阻止对象被回收
# - 观察者模式：观察者不持有被观察者的强引用
# - 大型对象的索引：字典值用弱引用

cache = weakref.WeakValueDictionary()  # 值是弱引用，对象可被回收
def get_object(obj_id):
    obj = cache.get(obj_id)
    if obj is None:
        obj = create_expensive_object(obj_id)
        cache[obj_id] = obj
    return obj
```

---

### 2.4 解释器与运行时优化

#### 选择更快的解释器（PyPy）

```bash
# PyPy 是 Python 的 JIT 编译器实现，对纯 Python 代码有显著加速
# 安装：从 pypy.org 下载，或 conda install pypy

# 运行脚本
pypy3 my_script.py

# 性能对比（纯计算密集型）：
# CPython: 10.0s
# PyPy:    0.8s  (约 12 倍加速)

# 性能对比（大量调用 C 扩展，如 NumPy）：
# CPython: 2.0s
# PyPy:    2.5s  (可能更慢，因为 C 扩展兼容性开销)

# PyPy 的适用场景：
# ✅ 纯 Python 计算密集型（算法、模拟、解析）
# ✅ 长时间运行的服务（JIT 预热后性能稳定）
# ✅ 大量循环和函数调用
# ❌ 大量使用 C 扩展（NumPy、Pandas、PyTorch）
# ❌ 短生命周期脚本（JIT 预热开销大于收益）
# ❌ 需要 CPython 特定行为（如某些调试工具）
```

#### 编译选项

```bash
# CPython 编译时的优化选项
# --enable-optimizations：启用 PGO（Profile-Guided Optimization）
# 编译过程会运行测试套件收集性能数据，再用数据优化编译
./configure --enable-optimizations --with-lto
make -j$(nproc)

# PGO 通常能带来 5-15% 的性能提升
# LTO（Link-Time Optimization）带来额外 5-10%

# 运行时优化：PYTHONHASHSEED
# 默认哈希随机化（安全考虑），固定种子可减少哈希冲突波动
PYTHONHASHSEED=0 python script.py  # 仅用于基准测试，生产环境保持随机
```

#### 字节码优化

```python
# Python 代码先编译为字节码，再由解释器执行
# 理解字节码有助于写出更高效的代码

import dis

def simple_loop():
    total = 0
    for i in range(100):
        total += i
    return total

dis.dis(simple_loop)
# 输出字节码指令，每条指令对应一个 C 函数调用
# 优化方向：减少字节码指令数量

# 示例：属性访问的字节码开销
class Point:
    __slots__ = ("x", "y")

def access_attributes(p):
    return p.x + p.y  # 两次 LOAD_ATTR，__slots__ 优化为 LOAD_FAST 级

# 局部变量访问最快（LOAD_FAST），全局变量最慢（LOAD_GLOBAL）
# 优化技巧：在函数内将全局变量绑定为局部变量
import math

def slow_sin_sum(n):
    return sum(math.sin(i) for i in range(n))  # 每次查找 math.sin

def fast_sin_sum(n):
    sin = math.sin  # 绑定为局部变量
    return sum(sin(i) for i in range(n))  # LOAD_FAST 查找
# 性能提升约 10-15%
```

#### GIL规避策略

```python
# GIL（Global Interpreter Lock）是 CPython 的全局解释器锁
# 同一时刻只有一个线程执行 Python 字节码
# 影响：CPU 密集型任务无法通过多线程加速

# 策略1：多进程（multiprocessing）
from multiprocessing import Pool

def cpu_bound_task(n):
    return sum(i*i for i in range(n))

with Pool(processes=4) as pool:
    results = pool.map(cpu_bound_task, [10**6]*4)
# 4核机器上接近 4 倍加速

# 策略2：C 扩展释放 GIL
# NumPy、Pandas 等库在 C 层操作时会释放 GIL
# 因此多线程 + NumPy 可以并行

# 策略3：asyncio（I/O 密集型）
# GIL 在等待 I/O 时会自动释放，asyncio 适合 I/O 密集场景

# 策略4：concurrent.futures
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(cpu_bound_task, n) for n in [10**6]*4]
    results = [f.result() for f in futures]

# 🔥 面试高频考点：GIL 是什么？如何影响性能？如何绕过？
# GIL 是 CPython 中用于保护对象引用计数的互斥锁
# 影响：CPU 密集型多线程无法并行；I/O 密集型影响小（I/O 时释放GIL）
# 绕过：多进程、C扩展释放GIL、asyncio、使用无GIL的解释器（如 PyPy 的 STM 分支、GraalPython）
```

---

### 2.5 C扩展与性能突破

#### Cython入门

```python
# Cython 是 Python 的超集，添加了类型声明，可编译为 C 扩展
# 安装：pip install cython

# hello.pyx
def fib(int n):
    """Cython 版本的斐波那契，带类型声明"""
    cdef int a = 0, b = 1
    cdef int i
    for i in range(n):
        a, b = b, a + b
    return a

# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("hello.pyx", compiler_directives={"language_level": "3"})
)

# 编译
# python setup.py build_ext --inplace

# 使用
from hello import fib
fib(100)

# 性能对比（计算 fib(100) 100万次）：
# 纯 Python: 12.5s
# Cython:    0.03s  (约 400 倍加速)

# Cython 优化技巧：
# 1. 用 cdef 声明 C 类型变量
# 2. 用 @cython.boundscheck(False) 关闭边界检查
# 3. 用 @cython.wraparound(False) 关闭负索引支持
# 4. 用 typed memoryview 操作 NumPy 数组
```

#### ctypes调用C库

```python
# ctypes 是标准库，可直接调用 C 动态库，无需编译扩展
import ctypes
from ctypes import c_int, c_double, POINTER

# 加载 C 标准库
libc = ctypes.CDLL("libc.so.6")  # Linux
# libc = ctypes.CDLL("msvcrt.dll")  # Windows

# 调用 printf
libc.printf(b"Hello from C: %d\n", 42)

# 调用自定义 C 库
# 编译：gcc -shared -o libmath_utils.so math_utils.c
lib = ctypes.CDLL("./libmath_utils.so")

# 声明函数签名（重要：不声明可能导致段错误）
lib.fast_sum.argtypes = [POINTER(c_double), c_int]
lib.fast_sum.restype = c_double

# 调用
data = (c_double * 5)(1.0, 2.0, 3.0, 4.0, 5.0)
result = lib.fast_sum(data, 5)
print(result)  # 15.0

# ctypes 的适用场景：
# ✅ 调用已有的 C 库（不需要写 C 代码）
# ✅ 快速原型验证
# ❌ 频繁调用（每次调用有参数转换开销）
# ❌ 需要复杂数据结构交互
```

#### cffi

```python
# cffi 是 ctypes 的现代替代，API 更友好，性能更好
# 安装：pip install cffi

from cffi import FFI

ffi = FFI()
ffi.cdef("""
    double fast_sum(double* data, int n);
""")

lib = ffi.dlopen("./libmath_utils.so")

# 分配内存并调用
data = ffi.new("double[]", [1.0, 2.0, 3.0, 4.0, 5.0])
result = lib.fast_sum(data, 5)

# cffi 比 ctypes 的优势：
# 1. 更好的类型安全
# 2. 更低的调用开销
# 3. 支持内联 C 代码（API 模式）
```

#### C扩展的适用场景与风险

| 方案 | 开发成本 | 性能提升 | 兼容性 | 适用场景 |
|------|---------|---------|--------|---------|
| Cython | 中 | 高（10-400x） | 好 | 计算密集型循环、NumPy操作 |
| ctypes | 低 | 中（受调用开销限制） | 好 | 调用已有C库 |
| cffi | 低 | 中高 | 好 | 调用已有C库、需要更好API |
| 手写C扩展 | 高 | 最高 | 中 | 极致性能、Python/C深度交互 |
| Numba | 极低 | 高（10-100x） | 中 | 数值计算、NumPy代码 |

> ⚠️ **风险提示**：C 扩展会丧失 Python 的跨平台可移植性，需要为每个平台编译。调试 C 扩展比调试 Python 代码困难得多（段错误、内存泄漏）。只有在 profiler 确认瓶颈且纯 Python 优化无效时才考虑。

#### Numba JIT编译

```python
# Numba 用 LLVM 将 Python 函数即时编译为机器码
# 安装：pip install numba

from numba import jit, njit, prange
import numpy as np

# 基础用法：@njit 等同于 @jit(nopython=True)
@njit
def fast_matrix_multiply(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """矩阵乘法，Numba JIT 编译"""
    m, k = A.shape
    k2, n = B.shape
    C = np.zeros((m, n))
    for i in range(m):
        for j in range(n):
            s = 0.0
            for l in range(k):
                s += A[i, l] * B[l, j]
            C[i, j] = s
    return C

# 并行加速：prange 替代 range，自动并行化
@njit(parallel=True)
def parallel_sum(data: np.ndarray) -> float:
    total = 0.0
    for i in prange(len(data)):  # 自动并行
        total += data[i] ** 2
    return total

# 性能对比（1000x1000 矩阵乘法）：
# 纯 Python 三重循环: > 60s
# NumPy (@): 0.05s
# Numba @njit: 0.02s
# Numba @njit(parallel=True): 0.005s (8核)

# Numba 的限制：
# 1. 只支持数值计算和 NumPy 操作
# 2. nopython 模式下不能用 Python 对象
# 3. 首次调用有编译开销（JIT 预热）
# 4. 不支持所有 Python 特性（如类的复杂用法）
```

---

### 2.6 并发性能优化

#### 线程池/进程池选择

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# 选择决策树：
# 任务类型？
# ├── I/O 密集型（网络请求、文件读写、数据库查询）
# │   └── 用 ThreadPoolExecutor（GIL 在 I/O 时释放）
# ├── CPU 密集型（数值计算、图像处理、加密）
# │   └── 用 ProcessPoolExecutor（绕过 GIL）
# └── 混合
#     └── 分析瓶颈，通常 I/O 用线程，CPU 用进程

# I/O 密集型：线程池
def fetch_url(url: str) -> str:
    return requests.get(url, timeout=10).text

urls = [f"https://api.example.com/item/{i}" for i in range(100)]

with ThreadPoolExecutor(max_workers=20) as executor:
    responses = list(executor.map(fetch_url, urls))
# 100个请求：串行 50s，20线程 3s

# CPU 密集型：进程池
def compute_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

data_list = [os.urandom(1024) for _ in range(100)]

with ProcessPoolExecutor(max_workers=4) as executor:
    hashes = list(executor.map(compute_hash, data_list))
# 100次哈希：串行 8s，4进程 2s
```

#### asyncio高并发模式

```python
import asyncio
import aiohttp

async def fetch_all(urls: list[str]) -> list[str]:
    """高并发抓取，限制并发数避免被封"""
    semaphore = asyncio.Semaphore(50)  # 最多50个并发

    async def fetch_one(url: str) -> str:
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    return await resp.text()

    tasks = [fetch_one(url) for url in urls]
    return await asyncio.gather(*tasks)  # 同时启动所有任务

# 运行
results = asyncio.run(fetch_all(urls))

# asyncio vs 线程池对比（1000个HTTP请求）：
# 线程池(100线程): 内存 ~50MB，上下文切换开销大
# asyncio: 内存 ~10MB，单线程无切换开销，吞吐量更高
# 但 asyncio 要求所有库都是异步的（aiohttp 而非 requests）
```

#### 生产者消费者模式

```python
import asyncio
from dataclasses import dataclass

@dataclass
class Task:
    id: int
    payload: dict

async def producer(queue: asyncio.Queue, tasks: list[Task]) -> None:
    """生产者：往队列放任务"""
    for task in tasks:
        await queue.put(task)
        print(f"Produced task {task.id}")
    # 发送结束信号
    for _ in range(NUM_CONSUMERS):
        await queue.put(None)

async def consumer(queue: asyncio.Queue, consumer_id: int) -> None:
    """消费者：从队列取任务处理"""
    while True:
        task = await queue.get()
        if task is None:  # 结束信号
            queue.task_done()
            break
        try:
            await process_task(task)
            print(f"Consumer {consumer_id} processed task {task.id}")
        finally:
            queue.task_done()

async def main():
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)  # 背压：限制队列大小
    tasks = [Task(id=i, payload={}) for i in range(1000)]

    producers = [asyncio.create_task(producer(queue, tasks))]
    consumers = [asyncio.create_task(consumer(queue, i)) for i in range(NUM_CONSUMERS)]

    await asyncio.gather(*producers)
    await queue.join()  # 等待所有任务处理完成
    await asyncio.gather(*consumers)

NUM_CONSUMERS = 4
asyncio.run(main())
```

#### 批处理优化

```python
# 场景：逐条插入数据库 vs 批量插入
def insert_one_by_one(records):
    for record in records:
        db.execute("INSERT INTO table VALUES (?, ?, ?)", record)
# 10000条：约 10s（每次都有网络往返和事务开销）

def insert_batch(records, batch_size=1000):
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        db.executemany("INSERT INTO table VALUES (?, ?, ?)", batch)
# 10000条：约 0.5s（20倍加速）

# 通用批处理装饰器
from functools import wraps
from collections import deque

def batch_processor(batch_size: int = 100, flush_interval: float = 1.0):
    """将逐条调用攒批处理，兼顾延迟和吞吐量"""
    def decorator(func):
        buffer = deque()
        last_flush = time.time()

        @wraps(func)
        def wrapper(item):
            buffer.append(item)
            nonlocal last_flush
            if len(buffer) >= batch_size or time.time() - last_flush > flush_interval:
                func(list(buffer))
                buffer.clear()
                last_flush = time.time()
        return wrapper
    return decorator

@batch_processor(batch_size=50, flush_interval=0.5)
def write_logs(logs: list) -> None:
    db.executemany("INSERT INTO logs VALUES (?)", [(log,) for log in logs])
```

#### 连接池

```python
# 数据库连接池：避免每次请求都建立连接（TCP握手+认证 ~10ms）
import psycopg2.pool

# 创建连接池
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=5,      # 最小连接数（常驻）
    maxconn=20,     # 最大连接数（峰值）
    dsn="postgresql://user:pass@localhost/db"
)

def query_database(sql: str, params: tuple = ()):
    conn = connection_pool.getconn()  # 从池获取（复用连接）
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        connection_pool.putconn(conn)  # 归还连接

# Redis 连接池
import redis
redis_pool = redis.ConnectionPool(host="localhost", port=6379, max_connections=50)
r = redis.Redis(connection_pool=redis_pool)

# HTTP 连接池（requests 自动管理）
import requests
session = requests.Session()  # Session 内部有连接池
# 复用 TCP 连接，避免每次请求的握手开销
for url in urls:
    session.get(url)
```

---

### 本章总结

性能优化是一个**测量驱动**的过程，而非经验驱动：
- 先用 cProfile/py-spy 定位瓶颈，不要靠猜测
- 优先优化算法和数据结构（数量级提升），再考虑语言层面技巧
- 内存优化的核心是"流式处理"和"紧凑表示"（生成器、`__slots__`、array、mmap）
- C 扩展是最后手段，Numba 和 Cython 是性价比最高的选择
- 并发优化要区分 I/O 密集（线程/asyncio）和 CPU 密集（进程）

### 思考题/实战练习

1. **性能分析实战**：写一个函数统计 100 万条文本中每个单词的出现次数，用 cProfile 分析瓶颈，然后用 `collections.Counter` 优化，对比性能。
2. **内存优化**：实现一个逐行处理 1GB 日志文件的程序，分别用 `readlines()` 和生成器实现，用 `memory_profiler` 对比内存峰值。
3. **__slots__ 实验**：创建 100 万个普通对象和 `__slots__` 对象，用 `sys.getsizeof()` 和 `tracemalloc` 对比内存占用。
4. **并发选择**：分别用线程池、进程池、asyncio 实现 100 个 HTTP 请求的并发抓取，对比耗时和内存，分析各自的适用场景。
5. **Numba 加速**：用纯 Python 实现一个图像卷积函数，用 Numba `@njit` 加速，对比 NumPy 向量化版本的性能。

---


## 3. 设计模式在Python中

设计模式不是"必须套用的模板"，而是**经过验证的问题解决方案的词汇表**。Python 的语言特性（一等函数、装饰器、元类、描述符）让很多经典模式变得极其简洁，甚至"消失"在语法中。老手知道什么时候该用模式、什么时候该用更简单的方案。

### 3.1 创建型模式

#### 单例模式

单例是最被滥用的模式。在 Python 中，**模块级变量天然就是单例**，大多数场景不需要刻意实现单例类。

```python
# 方式1：模块单例（最 Pythonic，推荐）
# singleton_config.py
class _Config:
    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value

config = _Config()  # 模块导入时创建一次，全局共享

# 使用
from singleton_config import config
config.set("debug", True)

# 方式2：装饰器实现
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class DatabaseConnection:
    def __init__(self, dsn: str):
        self.dsn = dsn

# 方式3：元类实现（最"正统"，但最重）
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class AppState(metaclass=SingletonMeta):
    def __init__(self):
        self.users_online = 0

# 方式4：__new__ 实现
class Logger:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

> 🏆 **老手经验**：单例的本质是"全局共享一个实例"，但这会引入全局状态和隐式依赖。更好的做法是**依赖注入**——在应用启动时创建实例，通过参数传递给需要的组件。这样代码更可测试、更显式。只有在确实需要全局唯一且创建成本极高的场景（如数据库连接池）才考虑单例。

#### 工厂模式

```python
# 简单工厂：一个函数根据参数创建不同对象
from typing import Protocol

class Notification(Protocol):
    def send(self, message: str) -> None: ...

class EmailNotification:
    def send(self, message: str) -> None:
        print(f"Email: {message}")

class SMSNotification:
    def send(self, message: str) -> None:
        print(f"SMS: {message}")

class PushNotification:
    def send(self, message: str) -> None:
        print(f"Push: {message}")

def create_notification(channel: str) -> Notification:
    """简单工厂：根据渠道创建通知对象"""
    factories = {
        "email": EmailNotification,
        "sms": SMSNotification,
        "push": PushNotification,
    }
    if channel not in factories:
        raise ValueError(f"Unknown channel: {channel}")
    return factories[channel]()

# 工厂方法：定义创建对象的接口，让子类决定实例化哪个类
from abc import ABC, abstractmethod

class NotificationFactory(ABC):
    @abstractmethod
    def create(self) -> Notification: ...

    def notify(self, message: str) -> None:
        notification = self.create()
        notification.send(message)

class EmailFactory(NotificationFactory):
    def create(self) -> Notification:
        return EmailNotification()

class SMSFactory(NotificationFactory):
    def create(self) -> Notification:
        return SMSNotification()

# 抽象工厂：创建一系列相关对象
class DatabaseFactory(ABC):
    @abstractmethod
    def create_connection(self): ...
    @abstractmethod
    def create_query_builder(self): ...

class PostgreSQLFactory(DatabaseFactory):
    def create_connection(self):
        return PostgreSQLConnection()
    def create_query_builder(self):
        return PostgreSQLQueryBuilder()

class MySQLFactory(DatabaseFactory):
    def create_connection(self):
        return MySQLConnection()
    def create_query_builder(self):
        return MySQLQueryBuilder()
```

#### 建造者模式

```python
# 建造者模式：分步构建复杂对象，分离构建和表示
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Pizza:
    size: str
    crust: str
    toppings: list[str] = field(default_factory=list)
    extra_cheese: bool = False
    delivery: bool = False

class PizzaBuilder:
    """披萨建造者：链式调用，分步配置"""
    def __init__(self) -> None:
        self._size = "medium"
        self._crust = "regular"
        self._toppings: list[str] = []
        self._extra_cheese = False
        self._delivery = False

    def size(self, size: str) -> "PizzaBuilder":
        self._size = size
        return self

    def crust(self, crust: str) -> "PizzaBuilder":
        self._crust = crust
        return self

    def add_topping(self, topping: str) -> "PizzaBuilder":
        self._toppings.append(topping)
        return self

    def extra_cheese(self) -> "PizzaBuilder":
        self._extra_cheese = True
        return self

    def delivery(self) -> "PizzaBuilder":
        self._delivery = True
        return self

    def build(self) -> Pizza:
        return Pizza(
            size=self._size,
            crust=self._crust,
            toppings=self._toppings,
            extra_cheese=self._extra_cheese,
            delivery=self._delivery,
        )

# 使用：链式调用，可读性强
pizza = (
    PizzaBuilder()
    .size("large")
    .crust("thin")
    .add_topping("pepperoni")
    .add_topping("mushrooms")
    .extra_cheese()
    .delivery()
    .build()
)

# Python 替代方案：dataclass + 默认参数（大多数场景足够）
@dataclass
class Pizza:
    size: str = "medium"
    crust: str = "regular"
    toppings: list[str] = field(default_factory=list)
    extra_cheese: bool = False
    delivery: bool = False

pizza = Pizza(size="large", crust="thin", toppings=["pepperoni", "mushrooms"], extra_cheese=True)
```

#### 原型模式（copy模块）

```python
import copy
from dataclasses import dataclass

@dataclass
class Document:
    title: str
    content: str
    metadata: dict

# 浅拷贝：只复制顶层，嵌套对象共享引用
original = Document("Report", "Content", {"author": "Alice", "tags": ["draft"]})
shallow = copy.copy(original)
shallow.metadata["tags"].append("reviewed")
# original.metadata["tags"] 也变成 ["draft", "reviewed"]！共享嵌套对象

# 深拷贝：递归复制所有嵌套对象
deep = copy.deepcopy(original)
deep.metadata["tags"].append("approved")
# original.metadata["tags"] 不受影响

# 原型模式实战：基于模板创建新对象
class DocumentPrototype:
    def __init__(self):
        self._prototypes = {}

    def register(self, name: str, doc: Document) -> None:
        self._prototypes[name] = doc

    def clone(self, name: str, **overrides) -> Document:
        if name not in self._prototypes:
            raise KeyError(f"Unknown prototype: {name}")
        cloned = copy.deepcopy(self._prototypes[name])
        for key, value in overrides.items():
            setattr(cloned, key, value)
        return cloned

# 使用
protos = DocumentPrototype()
protos.register("report", Document("Report", "Template content", {"author": "", "tags": []}))

doc1 = protos.clone("report", title="Q3 Report")
doc2 = protos.clone("report", title="Q4 Report", content="Custom content")
```

---

### 3.2 结构型模式

#### 适配器模式

```python
# 适配器：将不兼容的接口转换为期望的接口
class ThirdPartyPaymentGateway:
    """第三方支付网关，接口与我们的系统不兼容"""
    def make_payment(self, amount_cents: int, card_details: dict) -> dict:
        # 第三方接口：金额用分，参数名不同
        return {"transaction_id": "txn_123", "status": "success"}

class PaymentProcessor(ABC):
    """我们系统期望的接口"""
    @abstractmethod
    def charge(self, amount: float, card_token: str) -> str: ...

class PaymentAdapter(PaymentProcessor):
    """适配器：将第三方接口转换为我们的接口"""
    def __init__(self, gateway: ThirdPartyPaymentGateway):
        self.gateway = gateway

    def charge(self, amount: float, card_token: str) -> str:
        # 转换：元 → 分，card_token → card_details
        amount_cents = int(amount * 100)
        card_details = {"token": card_token}
        result = self.gateway.make_payment(amount_cents, card_details)
        if result["status"] != "success":
            raise PaymentError(result.get("error", "Unknown error"))
        return result["transaction_id"]
```

#### 装饰器模式（Python原生支持）

Python 的函数装饰器语法就是装饰器模式的语言级实现。

```python
# 基础装饰器：日志记录
import functools
import time
import logging

logger = logging.getLogger(__name__)

def log_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        logger.info("Starting %s", func.__name__)
        try:
            result = func(*args, **kwargs)
            logger.info("Finished %s in %.3fs", func.__name__, time.perf_counter() - start)
            return result
        except Exception as e:
            logger.error("Failed %s: %s", func.__name__, e)
            raise
    return wrapper

# 带参数的装饰器：重试
def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning("Attempt %d failed, retrying in %.1fs: %s", attempt, delay, e)
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

# 类装饰器：给类添加方法
def add_repr(cls):
    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{cls.__name__}({attrs})"
    cls.__repr__ = __repr__
    return cls

@add_repr
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

#### 代理模式

```python
# 虚拟代理：延迟创建昂贵对象
class HeavyObject:
    """创建成本很高的对象"""
    def __init__(self):
        print("HeavyObject initialized (expensive!)")
        self.data = self._load_huge_dataset()

    def _load_huge_dataset(self):
        time.sleep(2)  # 模拟加载
        return list(range(1_000_000))

    def process(self):
        return len(self.data)

class LazyProxy:
    """虚拟代理：首次访问时才创建真实对象"""
    def __init__(self):
        self._real_object = None

    def __getattr__(self, name):
        if self._real_object is None:
            print("Lazy loading HeavyObject...")
            self._real_object = HeavyObject()
        return getattr(self._real_object, name)

# 使用：对象创建被延迟到首次使用
proxy = LazyProxy()  # 不打印 "HeavyObject initialized"
result = proxy.process()  # 此时才创建

# 保护代理：控制访问权限
class ProtectedResource:
    def delete(self, user):
        if user.role != "admin":
            raise PermissionError("Only admin can delete")
        print("Deleted")

# 远程代理：访问远程服务（如 XML-RPC、gRPC stub）
import xmlrpc.client
proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")
result = proxy.add(3, 5)  # 远程调用，看起来像本地方法
```

#### 外观模式

```python
# 外观模式：为复杂子系统提供统一的简化接口
class VideoFile:
    def __init__(self, filename):
        self.filename = filename

class CodecFactory:
    def extract(self, file): ...
    def create(self, format): ...

class BitrateReader:
    def read(self, file, codec): ...
    def convert(self, buffer, codec): ...

class AudioMixer:
    def fix(self, result): ...

class VideoConverter:
    """外观类：封装复杂的视频转换流程"""
    def convert(self, filename: str, target_format: str) -> str:
        file = VideoFile(filename)
        source_codec = CodecFactory().extract(file)
        target_codec = CodecFactory().create(target_format)
        buffer = BitrateReader().read(file, source_codec)
        result = BitrateReader().convert(buffer, target_codec)
        result = AudioMixer().fix(result)
        return f"converted_{filename}.{target_format}"

# 客户端：只需要调用一个方法
converter = VideoConverter()
converter.convert("video.avi", "mp4")
```

#### 组合模式

```python
# 组合模式：树形结构，统一处理单个对象和组合
from abc import ABC, abstractmethod

class FileSystemComponent(ABC):
    @abstractmethod
    def get_size(self) -> int: ...
    @abstractmethod
    def display(self, indent: int = 0) -> None: ...

class File(FileSystemComponent):
    def __init__(self, name: str, size: int):
        self.name = name
        self._size = size

    def get_size(self) -> int:
        return self._size

    def display(self, indent: int = 0) -> None:
        print(" " * indent + f"📄 {self.name} ({self._size}KB)")

class Directory(FileSystemComponent):
    def __init__(self, name: str):
        self.name = name
        self.children: list[FileSystemComponent] = []

    def add(self, component: FileSystemComponent) -> None:
        self.children.append(component)

    def remove(self, component: FileSystemComponent) -> None:
        self.children.remove(component)

    def get_size(self) -> int:
        return sum(child.get_size() for child in self.children)

    def display(self, indent: int = 0) -> None:
        print(" " * indent + f"📁 {self.name}/ ({self.get_size()}KB)")
        for child in self.children:
            child.display(indent + 2)

# 使用：统一处理文件和目录
root = Directory("project")
root.add(File("main.py", 5))
src = Directory("src")
src.add(File("module1.py", 10))
src.add(File("module2.py", 8))
root.add(src)
root.display()
print(f"Total: {root.get_size()}KB")
```

---

### 3.3 行为型模式

#### 观察者模式（事件系统）

```python
# 观察者模式：一对多依赖，状态变化时自动通知
from typing import Callable, Any
from collections import defaultdict

class EventBus:
    """通用事件总线：支持注册、注销、发布"""
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable) -> None:
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        self._subscribers[event_type].remove(handler)

    def publish(self, event_type: str, **kwargs: Any) -> None:
        for handler in self._subscribers.get(event_type, []):
            try:
                handler(**kwargs)
            except Exception:
                logger.exception("Handler failed for event %s", event_type)

# 使用
bus = EventBus()

def send_welcome_email(user):
    print(f"Sending welcome email to {user['email']}")

def create_default_profile(user):
    print(f"Creating profile for {user['name']}")

bus.subscribe("user_registered", send_welcome_email)
bus.subscribe("user_registered", create_default_profile)

# 发布事件，所有订阅者自动被调用
bus.publish("user_registered", user={"name": "Alice", "email": "alice@example.com"})

# 异步事件总线（生产环境常用）
import asyncio

class AsyncEventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event_type, handler):
        self._subscribers[event_type].append(handler)

    async def publish(self, event_type, **kwargs):
        handlers = self._subscribers.get(event_type, [])
        await asyncio.gather(*[handler(**kwargs) for handler in handlers])
```

#### 策略模式（函数即策略）

Python 中函数是一等公民，策略模式可以简化为"传入不同的函数"。

```python
# 经典策略模式（类实现）
class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, amount: float) -> float: ...

class NoDiscount(DiscountStrategy):
    def calculate(self, amount): return amount

class PercentageDiscount(DiscountStrategy):
    def __init__(self, percent): self.percent = percent
    def calculate(self, amount): return amount * (1 - self.percent / 100)

class FixedDiscount(DiscountStrategy):
    def __init__(self, fixed): self.fixed = fixed
    def calculate(self, amount): return max(0, amount - self.fixed)

class Order:
    def __init__(self, amount, strategy: DiscountStrategy):
        self.amount = amount
        self.strategy = strategy

    def total(self):
        return self.strategy.calculate(self.amount)

# Pythonic 策略模式（函数即策略，更简洁）
def no_discount(amount): return amount
def percentage_discount(percent):
    return lambda amount: amount * (1 - percent / 100)
def fixed_discount(fixed):
    return lambda amount: max(0, amount - fixed)

class Order:
    def __init__(self, amount, strategy: Callable[[float], float]):
        self.amount = amount
        self.strategy = strategy

    def total(self):
        return self.strategy(self.amount)

# 使用
order1 = Order(100, no_discount)
order2 = Order(100, percentage_discount(20))
order3 = Order(100, fixed_discount(30))

# 策略注册：运行时动态选择
strategies = {
    "none": no_discount,
    "percent20": percentage_discount(20),
    "fixed30": fixed_discount(30),
}
strategy = strategies[user.discount_type]
```

#### 命令模式

```python
# 命令模式：将请求封装为对象，支持撤销、排队、日志
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...
    @abstractmethod
    def undo(self) -> None: ...

class CreateUserCommand(Command):
    def __init__(self, user_repo, user_data):
        self.user_repo = user_repo
        self.user_data = user_data
        self.created_user = None

    def execute(self):
        self.created_user = self.user_repo.create(self.user_data)
        return self.created_user

    def undo(self):
        if self.created_user:
            self.user_repo.delete(self.created_user.id)

class CommandInvoker:
    """命令调用器：支持执行、撤销、重做、历史记录"""
    def __init__(self):
        self._history: list[Command] = []
        self._redo_stack: list[Command] = []

    def execute(self, command: Command):
        result = command.execute()
        self._history.append(command)
        self._redo_stack.clear()  # 新命令清空重做栈
        return result

    def undo(self):
        if not self._history:
            return
        command = self._history.pop()
        command.undo()
        self._redo_stack.append(command)

    def redo(self):
        if not self._redo_stack:
            return
        command = self._redo_stack.pop()
        command.execute()
        self._history.append(command)

# 使用
invoker = CommandInvoker()
invoker.execute(CreateUserCommand(repo, {"name": "Alice"}))
invoker.undo()  # 撤销创建
invoker.redo()  # 重做
```

#### 迭代器模式（Python原生）

Python 的 `for` 循环、生成器、`iter()`/`next()` 就是迭代器模式的语言级实现。

```python
# 自定义迭代器：实现 __iter__ 和 __next__
class Range:
    """模拟 range 的自定义迭代器"""
    def __init__(self, start, stop, step=1):
        self.start = start
        self.stop = stop
        self.step = step
        self.current = start

    def __iter__(self):
        return self  # 返回迭代器自身

    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += self.step
        return value

# 更简洁：生成器函数
def range_gen(start, stop, step=1):
    current = start
    while current < stop:
        yield current
        current += step

# 迭代器工具：itertools
from itertools import islice, chain, groupby, tee

# islice：切片迭代器（不创建副本）
for item in islice(huge_iterator, 10, 20):
    process(item)

# chain：连接多个迭代器
for item in chain(iter1, iter2, iter3):
    process(item)

# groupby：分组（注意：需要先排序）
data = sorted(items, key=lambda x: x.category)
for category, group in groupby(data, key=lambda x: x.category):
    print(category, list(group))
```

#### 状态模式

```python
# 状态模式：对象内部状态改变时改变行为
from abc import ABC, abstractmethod

class OrderState(ABC):
    @abstractmethod
    def pay(self, order): ...
    @abstractmethod
    def ship(self, order): ...
    @abstractmethod
    def cancel(self, order): ...

class PendingState(OrderState):
    def pay(self, order):
        print("Payment received")
        order.state = PaidState()
    def ship(self, order):
        raise InvalidStateError("Cannot ship unpaid order")
    def cancel(self, order):
        print("Order cancelled")
        order.state = CancelledState()

class PaidState(OrderState):
    def pay(self, order):
        raise InvalidStateError("Already paid")
    def ship(self, order):
        print("Order shipped")
        order.state = ShippedState()
    def cancel(self, order):
        print("Refund initiated")
        order.state = RefundedState()

class ShippedState(OrderState):
    def pay(self, order): raise InvalidStateError("Already paid")
    def ship(self, order): raise InvalidStateError("Already shipped")
    def cancel(self, order): raise InvalidStateError("Cannot cancel shipped order, return instead")

class CancelledState(OrderState):
    def pay(self, order): raise InvalidStateError("Order cancelled")
    def ship(self, order): raise InvalidStateError("Order cancelled")
    def cancel(self, order): raise InvalidStateError("Already cancelled")

class Order:
    def __init__(self):
        self.state = PendingState()
    def pay(self): self.state.pay(self)
    def ship(self): self.state.ship(self)
    def cancel(self): self.state.cancel(self)
```

#### 模板方法模式

```python
# 模板方法：定义算法骨架，子类实现具体步骤
from abc import ABC, abstractmethod

class DataPipeline(ABC):
    """数据处理管道模板"""
    def run(self, input_data):
        """模板方法：定义处理流程，子类不重写"""
        data = self.extract(input_data)
        data = self.validate(data)
        data = self.transform(data)
        self.load(data)
        return data

    @abstractmethod
    def extract(self, input_data): ...

    def validate(self, data):
        """默认实现，子类可覆盖"""
        if data is None:
            raise ValueError("Data is None")
        return data

    @abstractmethod
    def transform(self, data): ...

    @abstractmethod
    def load(self, data): ...

class CSVPipeline(DataPipeline):
    def extract(self, filepath):
        with open(filepath) as f:
            return list(csv.DictReader(f))

    def transform(self, data):
        return [self._clean_row(row) for row in data]

    def _clean_row(self, row):
        return {k: v.strip() for k, v in row.items()}

    def load(self, data):
        db.insert_many(data)

# Pythonic 替代：用回调/钩子函数
def run_pipeline(input_data, extract_fn, transform_fn, load_fn, validate_fn=None):
    data = extract_fn(input_data)
    if validate_fn:
        data = validate_fn(data)
    data = transform_fn(data)
    load_fn(data)
    return data
```

#### 访问者模式

```python
# 访问者模式：在不修改类的前提下为类添加新操作
from abc import ABC, abstractmethod

class ASTNode(ABC):
    @abstractmethod
    def accept(self, visitor): ...

class NumberNode(ASTNode):
    def __init__(self, value): self.value = value
    def accept(self, visitor): return visitor.visit_number(self)

class BinaryOpNode(ASTNode):
    def __init__(self, op, left, right):
        self.op = op; self.left = left; self.right = right
    def accept(self, visitor): return visitor.visit_binary_op(self)

class ASTVisitor(ABC):
    @abstractmethod
    def visit_number(self, node): ...
    @abstractmethod
    def visit_binary_op(self, node): ...

class Evaluator(ASTVisitor):
    """访问者1：计算表达式值"""
    def visit_number(self, node): return node.value
    def visit_binary_op(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        return {"+": left+right, "-": left-right, "*": left*right}[node.op]

class PrettyPrinter(ASTVisitor):
    """访问者2：打印表达式"""
    def visit_number(self, node): return str(node.value)
    def visit_binary_op(self, node):
        return f"({node.left.accept(self)} {node.op} {node.right.accept(self)})"

# 使用：不修改 AST 节点类，就能添加新操作
ast = BinaryOpNode("+", NumberNode(3), BinaryOpNode("*", NumberNode(4), NumberNode(5)))
print(ast.accept(Evaluator()))      # 23
print(ast.accept(PrettyPrinter()))  # (3 + (4 * 5))
```

---

### 3.4 Python特有模式

#### 注册表模式

```python
# 注册表模式：运行时动态注册，通过名称查找
class Registry:
    """通用注册表：支持装饰器注册"""
    def __init__(self, name: str):
        self.name = name
        self._items = {}

    def register(self, name: str = None):
        def decorator(cls):
            key = name or cls.__name__
            self._items[key] = cls
            return cls
        return decorator

    def get(self, name: str):
        if name not in self._items:
            raise KeyError(f"{name} not registered in {self.name}")
        return self._items[name]

    def list(self):
        return list(self._items.keys())

# 使用：序列化器注册表
serializers = Registry("serializers")

@serializers.register("json")
class JSONSerializer:
    def serialize(self, data): return json.dumps(data)

@serializers.register("yaml")
class YAMLSerializer:
    def serialize(self, data): return yaml.dump(data)

# 动态获取
serializer = serializers.get(format_name)()
output = serializer.serialize(data)
```

#### 中间件模式

```python
# 中间件模式：请求/响应经过一系列中间件处理
from typing import Callable

class Middleware:
    """中间件基类"""
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        # 请求处理前
        response = self.get_response(request)
        # 响应处理后
        return response

class LoggingMiddleware(Middleware):
    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        logger.info("Request %s took %.3fs", request.path, time.perf_counter() - start)
        return response

class AuthMiddleware(Middleware):
    def __call__(self, request):
        if not request.user.is_authenticated:
            return Response(status=401)
        return self.get_response(request)

class MiddlewareChain:
    """中间件链：按顺序包装"""
    def __init__(self, middlewares: list[type[Middleware]]):
        self.middlewares = middlewares

    def build(self, handler: Callable) -> Callable:
        for middleware in reversed(self.middlewares):
            handler = middleware(handler)
        return handler

# 使用
chain = MiddlewareChain([LoggingMiddleware, AuthMiddleware])
app = chain.build(final_handler)
response = app(request)  # 经过 Logging → Auth → handler
```

#### 插件模式

```python
# 插件模式：通过入口点动态发现和加载插件
# setup.py / pyproject.toml 中定义入口点
# [project.entry-points."myapp.plugins"]
# csv = "myapp_csv:CSVPlugin"
# json = "myapp_json:JSONPlugin"

import importlib.metadata

class PluginManager:
    """插件管理器：通过入口点发现插件"""
    def __init__(self, entry_point_group: str):
        self.entry_point_group = entry_point_group
        self._plugins = {}

    def load_all(self):
        for entry_point in importlib.metadata.entry_points(group=self.entry_point_group):
            plugin_class = entry_point.load()
            self._plugins[entry_point.name] = plugin_class()

    def get(self, name):
        return self._plugins.get(name)

    def list(self):
        return list(self._plugins.keys())

# 插件接口
class Plugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...
    @abstractmethod
    def execute(self, *args, **kwargs): ...

# 使用
manager = PluginManager("myapp.plugins")
manager.load_all()
plugin = manager.get("csv")
plugin.execute(data)
```

#### 描述符模式

```python
# 描述符模式：将属性访问逻辑封装为可复用的类
class ValidatedAttribute:
    """验证属性描述符：类型检查 + 范围验证"""
    def __init__(self, name: str, attr_type: type, min_value=None, max_value=None):
        self.name = name
        self.attr_type = attr_type
        self.min_value = min_value
        self.max_value = max_value

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if not isinstance(value, self.attr_type):
            raise TypeError(f"{self.name} must be {self.attr_type.__name__}")
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.name} must be >= {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.name} must be <= {self.max_value}")
        instance.__dict__[self.name] = value

class Product:
    price = ValidatedAttribute("price", float, min_value=0.0)
    quantity = ValidatedAttribute("quantity", int, min_value=0, max_value=10000)

    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

# 使用
p = Product("Widget", 9.99, 100)
p.price = -5  # ValueError: price must be >= 0.0
```

#### Mixin模式

```python
# Mixin：为类提供可复用的方法，不单独实例化
class JSONMixin:
    """提供 JSON 序列化能力的 Mixin"""
    def to_json(self) -> str:
        return json.dumps(self.__dict__, default=str)

    @classmethod
    def from_json(cls, data: str):
        return cls(**json.loads(data))

class TimestampMixin:
    """提供时间戳的 Mixin"""
    created_at = None
    updated_at = None

    def save(self):
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        self.updated_at = now
        super().save()  # 调用下一个 MRO 中的 save

class User(JSONMixin, TimestampMixin, BaseModel):
    def __init__(self, name, email):
        self.name = name
        self.email = email

# MRO: User → JSONMixin → TimestampMixin → BaseModel → object
# super().save() 在 TimestampMixin 中会调用 BaseModel.save()

# Mixin 的规则：
# 1. Mixin 不单独实例化，没有自己的 __init__（或调用 super().__init__）
# 2. Mixin 放在继承列表的前面（先被查找）
# 3. 用 super() 协作，不硬编码父类名
# 4. Mixin 之间不应有状态依赖
```

---

### 3.5 设计模式实战

#### Web框架中的模式应用

```python
# FastAPI/Flask 中的模式：
# 1. 路由注册 → 注册表模式
# 2. 中间件 → 中间件模式
# 3. 依赖注入 → 工厂模式 + 装饰器
# 4. 请求/响应对象 → 适配器模式
# 5. 异常处理 → 观察者模式（全局异常处理器）

# FastAPI 依赖注入示例
from fastapi import Depends, FastAPI

app = FastAPI()

def get_db():
    """依赖：数据库会话（工厂模式）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).get(user_id)
```

#### ORM中的模式应用

```python
# SQLAlchemy 中的模式：
# 1. Session → 工作单元模式（Unit of Work）
# 2. Query → 建造者模式（链式调用）
# 3. Relationship → 代理模式（懒加载）
# 4. Declarative Base → 元类模式
# 5. Event listeners → 观察者模式

# 工作单元模式
with Session() as session:
    user = session.get(User, 1)
    user.email = "new@example.com"
    session.add(Order(user=user, total=100))
    session.commit()  # 所有变更在一个事务中提交
```

#### 模式选择的权衡

| 模式 | 解决的问题 | 增加的复杂度 | Python 替代方案 |
|------|-----------|-------------|----------------|
| 单例 | 全局唯一实例 | 全局状态、难测试 | 模块变量、依赖注入 |
| 工厂 | 封装对象创建 | 额外的类/函数 | 字典映射、函数参数 |
| 建造者 | 分步构建复杂对象 | Builder 类 | dataclass + 默认参数 |
| 策略 | 运行时切换算法 | 策略类层次 | 传入函数/可调用对象 |
| 观察者 | 一对多通知 | 事件管理 | 回调列表、信号库 |
| 命令 | 封装请求为对象 | Command 类 | 函数 + 参数 |
| 装饰器 | 动态添加行为 | 包装层 | Python 装饰器语法 |
| 访问者 | 不修改类添加操作 | Visitor 层次 | 函数 + isinstance |

> 🏆 **老手经验**：设计模式的目标是**降低复杂度**，不是增加复杂度。如果一个模式让代码更难理解，就不要用。Python 的一等函数、装饰器、上下文管理器等特性已经内置了很多模式，优先用语言特性，模式是最后的选择。

---

### 本章总结

设计模式在 Python 中不是"必须套用的模板"，而是**解决特定问题的词汇表**：
- 创建型模式关注对象创建，Python 中模块变量和字典映射常能替代单例和工厂
- 结构型模式关注类和对象的组合，装饰器语法原生支持装饰器模式
- 行为型模式关注对象间通信，一等函数让策略、命令等模式极其简洁
- Python 特有模式（注册表、中间件、Mixin、描述符）是 Python 生态的核心设计手段
- 模式选择的核心原则：**用最简单的方案解决问题，模式是手段不是目的**

### 思考题/实战练习

1. **单例 vs 依赖注入**：将一个使用单例数据库连接的类重构为依赖注入方式，写测试对比两种方式的可测试性。
2. **策略模式实战**：实现一个折扣计算器，支持无折扣、百分比折扣、满减折扣三种策略，用函数和类两种方式实现，对比代码量。
3. **观察者模式**：实现一个支持异步事件的事件总线，包含异常隔离（一个订阅者失败不影响其他）和事件优先级。
4. **描述符模式**：实现一个 `EncryptedAttribute` 描述符，存储时自动加密，读取时自动解密，支持自定义加密算法。
5. **模式识别**：阅读 Flask 或 FastAPI 的源码，找出其中使用的 5 种设计模式，分析为什么在那个场景使用该模式。

---


## 4. 元编程

元编程是"编写能操作代码的代码"。Python 的元编程能力极强——装饰器、元类、描述符、AST 操作让你可以在运行时修改类的行为、动态生成代码、实现框架级别的抽象。但元编程也是一把双刃剑：**能力越强，调试越难，维护成本越高**。老手知道什么时候该用元编程，什么时候该用更简单的方案。

### 4.1 装饰器高级

#### 装饰器类（带状态）

```python
import functools
import time
from collections import defaultdict

class CountCalls:
    """带状态的装饰器类：统计函数调用次数"""
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.call_count = 0

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        return self.func(*args, **kwargs)

@CountCalls
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

fibonacci(20)
print(fibonacci.call_count)  # 调用次数

# 带参数的装饰器类
class Retry:
    """重试装饰器：支持指定次数、延迟、异常类型"""
    def __init__(self, max_attempts=3, delay=1.0, exceptions=(Exception,)):
        self.max_attempts = max_attempts
        self.delay = delay
        self.exceptions = exceptions

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, self.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except self.exceptions as e:
                    last_exception = e
                    if attempt < self.max_attempts:
                        time.sleep(self.delay * attempt)  # 指数退避
            raise last_exception
        return wrapper

@Retry(max_attempts=5, delay=0.5, exceptions=(ConnectionError, TimeoutError))
def call_api(url):
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()
```

#### 装饰器参数深入

```python
# 装饰器参数的三种形式

# 形式1：无参数装饰器
@decorator
def func(): ...
# 等价于 func = decorator(func)

# 形式2：带参数装饰器
@decorator(arg1, arg2)
def func(): ...
# 等价于 func = decorator(arg1, arg2)(func)

# 形式3：可选参数装饰器（既可 @decorator 也可 @decorator(args)）
def retry(func=None, *, max_attempts=3, delay=1.0):
    """支持两种调用方式的装饰器"""
    if func is None:
        # 被当作 @retry(max_attempts=5) 调用
        return lambda f: retry(f, max_attempts=max_attempts, delay=delay)
    # 被当作 @retry 直接调用
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception:
                if attempt == max_attempts - 1:
                    raise
                time.sleep(delay)
    return wrapper

@retry  # 无参数
def func1(): ...

@retry(max_attempts=5, delay=2)  # 带参数
def func2(): ...
```

#### 装饰器与类型注解

```python
from typing import TypeVar, Callable, Any, ParamSpec

P = ParamSpec("P")  # 参数规格
R = TypeVar("R")    # 返回值类型

def log_execution(func: Callable[P, R]) -> Callable[P, R]:
    """保留类型注解的装饰器"""
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.info("Calling %s", func.__name__)
        return func(*args, **kwargs)
    return wrapper

@log_execution
def add(a: int, b: int) -> int:
    return a + b

# mypy 能正确推断 add 的类型
result = add(1, 2)  # int
add("a", "b")  # mypy 报错：Argument 1 to "add" has incompatible type "str"
```

#### 装饰器的性能开销

```python
# 装饰器的开销：每次调用多一层函数调用
import timeit

def original(x):
    return x * 2

@functools.wraps(original)
def decorated(x):
    return original(x)

# 基准测试（1000万次调用）
# original:   0.35s
# decorated:  0.55s  (约 57% 开销)

# 优化：对于性能敏感的热点函数，避免多层装饰器嵌套
# 或者用 functools.lru_cache 等 C 实现的装饰器

# 装饰器堆叠顺序（从下往上应用，从上往下执行）
@decorator1
@decorator2
@decorator3
def func():
    pass
# 等价于 func = decorator1(decorator2(decorator3(func)))
# 执行顺序：decorator1 入口 → decorator2 入口 → decorator3 入口 → func → decorator3 出口 → decorator2 出口 → decorator1 出口
```

#### 标准库装饰器大全

```python
from functools import (
    lru_cache, cache, cached_property, wraps,
    total_ordering, singledispatch, partial, reduce
)
from contextlib import contextmanager, suppress
from dataclasses import dataclass, field
from abc import abstractmethod, abstractproperty
from typing import overload

# lru_cache：最近最少使用缓存
@lru_cache(maxsize=128)
def get_user(user_id): ...

# cache：无界缓存（Python 3.9+）
@cache
def factorial(n): ...

# cached_property：属性值计算一次后缓存
class DataSet:
    @cached_property
    def summary(self):
        return expensive_computation(self.data)

# total_ordering：自动补全比较运算符
@total_ordering
class Version:
    def __init__(self, major, minor):
        self.major = major
        self.minor = minor
    def __eq__(self, other):
        return (self.major, self.minor) == (other.major, other.minor)
    def __lt__(self, other):
        return (self.major, self.minor) < (other.major, other.minor)
# 自动生成 __le__, __gt__, __ge__

# singledispatch：单分派泛型函数
@singledispatch
def serialize(obj):
    raise TypeError(f"Cannot serialize {type(obj)}")

@serialize.register(int)
def _(obj):
    return str(obj)

@serialize.register(list)
def _(obj):
    return [serialize(item) for item in obj]

# contextmanager：将生成器转为上下文管理器
@contextmanager
def transaction(db):
    db.begin()
    try:
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise

# suppress：静默指定异常
with suppress(FileNotFoundError):
    os.remove("temp.tmp")
```

---

### 4.2 元类深入

#### 元类的执行流程

```python
# 元类是创建类的类。默认元类是 type。
# 类的创建过程：
# 1. 收集类体中的代码，构建命名空间字典
# 2. 调用元类的 __new__ 创建类对象
# 3. 调用元类的 __init__ 初始化类
# 4. 调用元类的 __call__ 创建实例（当类被调用时）

class MyMeta(type):
    def __new__(mcs, name, bases, namespace):
        """创建类对象（类还不存在）"""
        print(f"Creating class {name}")
        # 可以修改 namespace
        namespace["class_id"] = name.lower()
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        """初始化类对象（类已创建）"""
        print(f"Initializing class {name}")
        super().__init__(name, bases, namespace)

    def __call__(cls, *args, **kwargs):
        """创建实例（MyClass() 时调用）"""
        print(f"Creating instance of {cls.__name__}")
        instance = super().__call__(*args, **kwargs)
        return instance

class MyClass(metaclass=MyMeta):
    pass

# 输出：
# Creating class MyClass
# Initializing class MyClass

obj = MyClass()
# 输出：Creating instance of MyClass
```

#### 元类实现ORM

```python
# 简化版 ORM：用元类自动注册字段和表名
class Field:
    def __init__(self, column_type, primary_key=False):
        self.column_type = column_type
        self.primary_key = primary_key
        self.name = None  # 由元类设置

class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        if name == "Model":  # 基类不处理
            return super().__new__(mcs, name, bases, namespace)

        # 收集字段
        fields = {}
        primary_key = None
        for key, value in namespace.items():
            if isinstance(value, Field):
                value.name = key
                fields[key] = value
                if value.primary_key:
                    primary_key = key

        # 存储元信息
        namespace["_fields"] = fields
        namespace["_primary_key"] = primary_key
        namespace["_table_name"] = name.lower() + "s"

        return super().__new__(mcs, name, bases, namespace)

class Model(metaclass=ModelMeta):
    @classmethod
    def create_table_sql(cls):
        columns = []
        for name, field in cls._fields.items():
            col = f"{name} {field.column_type}"
            if field.primary_key:
                col += " PRIMARY KEY"
            columns.append(col)
        return f"CREATE TABLE {cls._table_name} ({', '.join(columns)})"

    def save(self):
        columns = ", ".join(self._fields.keys())
        values = ", ".join(repr(getattr(self, k)) for k in self._fields)
        return f"INSERT INTO {self._table_name} ({columns}) VALUES ({values})"

# 使用
class User(Model):
    id = Field("INTEGER", primary_key=True)
    name = Field("VARCHAR(100)")
    email = Field("VARCHAR(255)")

print(User.create_table_sql())
# CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(100), email VARCHAR(255))

user = User()
user.id = 1
user.name = "Alice"
user.email = "alice@example.com"
print(user.save())
# INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')
```

#### 元类实现单例

```python
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

# 线程安全版本
import threading

class ThreadSafeSingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:  # 双重检查锁定
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
```

#### 元类实现接口检查

```python
class InterfaceMeta(type):
    """接口元类：检查子类是否实现了所有抽象方法"""
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        # 收集抽象方法
        abstract_methods = set()
        for base in bases:
            abstract_methods.update(getattr(base, "_abstract_methods", set()))
        for key, value in namespace.items():
            if getattr(value, "_is_abstract", False):
                abstract_methods.add(key)
        cls._abstract_methods = abstract_methods
        return cls

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        # 非抽象类必须实现所有抽象方法
        if not namespace.get("_is_abstract_class", False):
            unimplemented = cls._abstract_methods - set(namespace.keys())
            if unimplemented:
                raise TypeError(
                    f"Class {name} must implement abstract methods: {unimplemented}"
                )

def abstractmethod(func):
    func._is_abstract = True
    return func

# 使用
class Animal(metaclass=InterfaceMeta):
    _is_abstract_class = True
    @abstractmethod
    def speak(self): ...

class Dog(Animal):
    def speak(self):
        return "Woof"

class Cat(Animal):
    pass  # TypeError: Class Cat must implement abstract methods: {'speak'}
```

#### 元类的替代方案（__init_subclass__）

```python
# Python 3.6+：__init_subclass__ 是元类的轻量替代
class PluginBase:
    _plugins = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # 子类定义时自动调用
        PluginBase._plugins[cls.__name__] = cls
        print(f"Registered plugin: {cls.__name__}")

class PluginA(PluginBase):
    pass  # Registered plugin: PluginA

class PluginB(PluginBase):
    pass  # Registered plugin: PluginB

# __set_name__：描述符获取属性名（Python 3.6+）
class Validated:
    def __set_name__(self, owner, name):
        self.name = name  # 自动获取属性名，不需要手动传入

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        self.validate(value)
        instance.__dict__[self.name] = value

    def validate(self, value):
        pass

# 对比：元类 vs __init_subclass__
# 元类：强大但复杂，影响类创建的整个过程，可能与其他元类冲突
# __init_subclass__：简单，只在子类创建时调用，不影响类创建过程
# 经验法则：能用 __init_subclass__ 解决的，就不要用元类
```

---

### 4.3 描述符深入

#### 描述符查找优先级

```python
# 属性查找顺序（对 instance.attr）：
# 1. 类的 __getattribute__ 方法（可自定义）
# 2. 数据描述符（同时定义了 __get__ 和 __set__/__delete__）
# 3. 实例 __dict__
# 4. 非数据描述符（只定义了 __get__）
# 5. 类 __dict__（包括继承链）
# 6. 父类的非数据描述符
# 7. __getattr__（如果定义了）

# 数据描述符 vs 非数据描述符
class DataDescriptor:
    """数据描述符：定义了 __set__，优先级高于实例 __dict__"""
    def __get__(self, instance, owner):
        return instance.__dict__.get("_value", 0)
    def __set__(self, instance, value):
        instance.__dict__["_value"] = value * 2

class NonDataDescriptor:
    """非数据描述符：只定义了 __get__，实例 __dict__ 会覆盖它"""
    def __get__(self, instance, owner):
        return 42

class MyClass:
    data = DataDescriptor()
    nondata = NonDataDescriptor()

obj = MyClass()
obj.data = 10
print(obj.data)  # 20（数据描述符生效，实例 __dict__ 不覆盖）

obj.nondata = 100  # 写入实例 __dict__
print(obj.nondata)  # 100（实例 __dict__ 覆盖非数据描述符）
del obj.nondata
print(obj.nondata)  # 42（恢复非数据描述符）
```

#### 实现验证描述符

```python
class TypedAttribute:
    """类型验证描述符：支持类型检查和默认值"""
    def __init__(self, expected_type, default=None):
        self.expected_type = expected_type
        self.default = default

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name, self.default)

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        instance.__dict__[self.name] = value

class RangeAttribute(TypedAttribute):
    """范围验证描述符"""
    def __init__(self, expected_type, min_value=None, max_value=None, **kwargs):
        super().__init__(expected_type, **kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def __set__(self, instance, value):
        super().__set__(instance, value)
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.name} must be >= {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.name} must be <= {self.max_value}")

class Product:
    name = TypedAttribute(str, default="")
    price = RangeAttribute(float, min_value=0.0, default=0.0)
    quantity = RangeAttribute(int, min_value=0, max_value=10000, default=0)
```

#### 实现懒加载描述符

```python
class LazyAttribute:
    """懒加载描述符：首次访问时计算，之后缓存"""
    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        # 计算值
        value = self.func(instance)
        # 缓存到实例 __dict__（非数据描述符会被覆盖）
        instance.__dict__[self.name] = value
        return value

class DataProcessor:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    @LazyAttribute
    def cleaned_data(self):
        """耗时的数据清洗，只在首次访问时执行"""
        print("Cleaning data...")
        return [x.strip().lower() for x in self.raw_data if x]

    @LazyAttribute
    def statistics(self):
        """基于清洗后数据的统计"""
        print("Computing statistics...")
        return {"count": len(self.cleaned_data), "unique": len(set(self.cleaned_data))}

# 使用
processor = DataProcessor(["  Hello ", "World", "", "hello"])
print(processor.cleaned_data)  # Cleaning data... ['hello', 'world', 'hello']
print(processor.cleaned_data)  # 直接返回缓存，不重复计算
print(processor.statistics)    # Computing statistics... {'count': 3, 'unique': 2}

# Python 内置：functools.cached_property 实现同样功能
from functools import cached_property

class DataProcessor:
    @cached_property
    def cleaned_data(self):
        return expensive_computation()
```

#### 描述符与__slots__

```python
# __slots__ 本身就是描述符！
# 当类定义了 __slots__，CPython 为每个 slot 创建一个 member_descriptor
# 这些描述符直接操作实例的内存布局，不经过 __dict__

class Point:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Point.x 是一个 <member 'x' of 'Point' objects>
# 访问 p.x 直接从内存偏移量读取，比 __dict__ 查找快

# 自定义描述符与 __slots__ 共存
class ValidatedSlot:
    """可以与 __slots__ 共存的描述符"""
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        self.validate(value)
        setattr(instance, self.private_name, value)

    def validate(self, value):
        pass

class Point:
    __slots__ = ("_x", "_y")  # 存储私有属性
    x = ValidatedSlot()
    y = ValidatedSlot()
```

---

### 4.4 动态属性与钩子

#### __getattr__ vs __getattribute__

```python
# __getattr__：只在属性找不到时调用（兜底）
class SafeDict:
    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        """当正常查找失败时调用"""
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

obj = SafeDict({"key": "value"})
print(obj.key)   # value（通过 __getattr__）
print(obj.other) # AttributeError

# __getattribute__：每次属性访问都调用（拦截所有）
class LoggingAttributes:
    def __init__(self):
        self.x = 10

    def __getattribute__(self, name):
        """每次属性访问都经过这里"""
        print(f"Accessing attribute: {name}")
        # 必须调用父类的 __getattribute__，否则无限递归
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        print(f"Setting attribute: {name} = {value}")
        super().__setattr__(name, value)

# 区别：
# __getattr__：只在正常查找失败时调用，适合实现"虚拟属性"
# __getattribute__：所有访问都调用，适合日志、权限控制，但要小心无限递归
# 调用 super().__getattribute__(name) 是必须的，否则会死循环
```

#### __setattr__与__delattr__

```python
class Immutable:
    """创建后不可修改的对象"""
    def __init__(self, **kwargs):
        # 直接操作 __dict__ 绕过 __setattr__
        object.__setattr__(self, "_frozen", False)
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False):
            raise AttributeError(f"Cannot modify immutable attribute '{name}'")
        super().__setattr__(name, value)

    def __delattr__(self, name):
        if getattr(self, "_frozen", False):
            raise AttributeError(f"Cannot delete immutable attribute '{name}'")
        super().__delattr__(name)

# 使用
obj = Immutable(x=1, y=2)
obj.x = 3  # AttributeError: Cannot modify immutable attribute 'x'
```

#### property工厂

```python
def validated_property(name, validator):
    """创建带验证的 property 工厂"""
    storage_name = f"_{name}"

    @property
    def prop(self):
        return getattr(self, storage_name)

    @prop.setter
    def prop(self, value):
        validator(value)
        setattr(self, storage_name, value)

    return prop

def non_empty_string(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Must be non-empty string")

def positive_number(value):
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError("Must be positive number")

class Product:
    name = validated_property("name", non_empty_string)
    price = validated_property("price", positive_number)

    def __init__(self, name, price):
        self.name = name
        self.price = price
```

#### 动态类创建（type三参数）

```python
# type(name, bases, namespace) 可以动态创建类
def init(self, name):
    self.name = name

def greet(self):
    return f"Hello, {self.name}!"

# 动态创建类
Person = type("Person", (object,), {
    "__init__": init,
    "greet": greet,
    "species": "Homo sapiens",
})

# 等价于：
# class Person:
#     species = "Homo sapiens"
#     def __init__(self, name): self.name = name
#     def greet(self): return f"Hello, {self.name}!"

p = Person("Alice")
print(p.greet())  # Hello, Alice!

# 实战：根据配置动态创建模型类
def create_model_class(table_name, fields):
    """根据字段定义动态创建 ORM 模型类"""
    namespace = {"_table_name": table_name}
    for field_name, field_type in fields.items():
        namespace[field_name] = Field(field_type)
    return type(table_name, (BaseModel,), namespace)

User = create_model_class("users", {"id": "INTEGER", "name": "VARCHAR(100)"})
```

---

### 4.5 AST与代码生成

#### ast模块基础

```python
import ast

# 解析 Python 代码为 AST
code = """
x = 1 + 2
print(x)
"""
tree = ast.parse(code)
print(ast.dump(tree, indent=2))
# Module(
#   body=[
#     Assign(
#       targets=[Name(id='x', ctx=Store())],
#       value=BinOp(
#         left=Constant(value=1),
#         op=Add(),
#         right=Constant(value=2))),
#     Expr(value=Call(
#       func=Name(id='print', ctx=Load()),
#       args=[Name(id='x', ctx=Load())],
#       keywords=[]))])

# AST 节点类型：
# Module → 整个模块
# FunctionDef/AsyncFunctionDef → 函数定义
# ClassDef → 类定义
# Assign → 赋值
# BinOp → 二元运算
# Call → 函数调用
# Name → 变量引用
# Constant → 常量
```

#### 解析/修改/编译AST

```python
import ast
import astunparse  # pip install astunparse

# 修改 AST：给所有函数添加计时
code = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
"""

tree = ast.parse(code)

class TimingTransformer(ast.NodeTransformer):
    """给所有函数添加计时逻辑"""
    def visit_FunctionDef(self, node):
        # 递归处理子节点
        self.generic_visit(node)

        # 创建：start = time.perf_counter()
        start_assign = ast.Assign(
            targets=[ast.Name(id="__start", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="time", ctx=ast.Load()),
                    attr="perf_counter",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
        )

        # 创建：print(f"{func.__name__} took {time.perf_counter()-start:.3f}s")
        # （简化版）

        # 在函数体开头插入
        node.body.insert(0, ast.parse("import time").body[0])
        node.body.insert(1, start_assign)

        # 修复行号和列偏移
        ast.fix_missing_locations(node)
        return node

transformer = TimingTransformer()
new_tree = transformer.visit(tree)

# 编译并执行
code_obj = compile(new_tree, "<string>", "exec")
namespace = {}
exec(code_obj, namespace)
namespace["add"](3, 4)  # 自动计时
```

#### 代码注入与装饰器

```python
# 用 AST 实现的装饰器：静态检查函数是否有文档字符串
import ast
import inspect

def require_docstring(func):
    """装饰器：静态检查函数是否有文档字符串"""
    source = inspect.getsource(func)
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node)
            if not docstring:
                raise ValueError(f"Function {func.__name__} must have a docstring")
    return func

@require_docstring
def good_func():
    """This is a docstring."""
    pass

@require_docstring
def bad_func():  # ValueError: Function bad_func must have a docstring
    pass
```

#### 实际应用（代码检查、转换）

```python
# 应用1：代码检查 — 检测硬编码的密码
class SecurityChecker(ast.NodeVisitor):
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) and "password" in target.id.lower():
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    print(f"Warning: Hardcoded password at line {node.lineno}")
        self.generic_visit(node)

# 应用2：代码转换 — Python 2 → Python 3 风格（lib2to3 的简化版）
class PrintTransformer(ast.NodeTransformer):
    """将 print 语句转为 print 函数调用"""
    def visit_Print(self, node):
        # Python 2 的 print 语句（在 Python 3 AST 中不存在，这里是概念示例）
        return ast.Call(
            func=ast.Name(id="print", ctx=ast.Load()),
            args=node.values,
            keywords=[],
        )

# 应用3：领域特定语言（DSL）— 用 Python 语法定义配置
config_code = """
database = {
    "host": "localhost",
    "port": 5432,
}
debug = True
"""
tree = ast.parse(config_code)
config = {}
for node in tree.body:
    if isinstance(node, ast.Assign):
        name = node.targets[0].id
        value = ast.literal_eval(node.value)  # 安全求值
        config[name] = value
print(config)  # {'database': {'host': 'localhost', 'port': 5432}, 'debug': True}
```

> ⚠️ **注意**：AST 操作是元编程中最强大也最危险的技术。修改 AST 后必须调用 `ast.fix_missing_locations()` 修复位置信息，否则编译会报错。AST 转换的代码很难调试，建议只在框架级别的工具中使用，普通业务代码不要碰。

---

### 本章总结

元编程是 Python 最强大的能力，但也是**最需要克制**的能力：
- 装饰器是最常用的元编程工具，标准库提供了丰富的装饰器
- 元类影响类的创建过程，适用于框架级别的抽象（ORM、接口检查），但 `__init_subclass__` 是更轻量的替代
- 描述符是 property、classmethod、staticmethod 的底层机制，理解查找优先级是关键
- `__getattr__` 和 `__getattribute__` 的区别在于"兜底" vs "拦截所有"
- AST 操作是终极元编程手段，只适用于代码检查、转换、DSL 等工具场景

> 🏆 **老手经验**：元编程的复杂度和调试难度呈指数增长。能用普通函数/类解决的，不要用装饰器；能用装饰器解决的，不要用元类；能用元类解决的，不要用 AST。每提升一个元编程层级，维护成本翻一倍。

### 思考题/实战练习

1. **装饰器实战**：实现一个 `@rate_limit(calls, period)` 装饰器，限制函数在指定时间窗口内的调用次数，支持线程安全。
2. **元类 vs __init_subclass__**：用元类和 `__init_subclass__` 两种方式实现插件注册表，对比代码复杂度和灵活性。
3. **描述符实现**：实现一个 `ObservableAttribute` 描述符，属性值变化时自动触发回调函数，支持多个观察者。
4. **懒加载对比**：对比 `@property`、`@cached_property`、自定义 `LazyAttribute` 描述符三种懒加载实现的性能和适用场景。
5. **AST 代码检查**：写一个 AST 检查器，检测代码中是否有 `except:` 裸异常捕获（应该指定异常类型），并输出行号和代码片段。

---


## 5. 调试与测试

调试和测试是老手工程素养的核心体现。新手靠 `print` 碰运气，老手用系统化的方法定位问题；新手觉得测试是"额外工作"，老手知道测试是**最快的开发方式**——它让你在写代码时就确认正确性，而不是在上线后追 bug。

### 5.1 调试技巧

#### print调试的进阶用法

```python
# 基础 print 调试（新手）
def calculate(items):
    total = 0
    for item in items:
        print(item)  # 临时调试
        total += item
    return total

# 进阶：f-string 调试变量名和值（Python 3.8+）
x = 42
print(f"{x=}")  # x=42（自动输出变量名和值）
print(f"{x = }")  # x = 42（带空格）

# 进阶：print 到 stderr（不干扰 stdout）
import sys
print("Debug info", file=sys.stderr)

# 进阶：带时间戳和调用位置
import inspect
def debug_print(*args):
    frame = inspect.currentframe().f_back
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    func = frame.f_code.co_name
    print(f"[{filename}:{lineno} {func}]", *args, file=sys.stderr)

# 进阶：icecream 库（pip install icecream）
from icecream import ic
ic(x)  # ic| x: 42（自动包含文件名、行号、变量名）
ic.configureOutput(prefix="DEBUG| ", includeContext=True)

# 进阶：条件 print（只在特定条件下输出）
if user.id == 42:  # 只调试特定用户
    print(f"Debug user: {user}")
```

#### pdb调试器

```python
# pdb 是 Python 内置调试器，功能强大但常被忽视

# 方式1：代码中设置断点
import pdb

def buggy_function(data):
    result = []
    for item in data:
        pdb.set_trace()  # 程序执行到这里会暂停
        processed = item.transform()
        result.append(processed)
    return result

# Python 3.7+：breakpoint() 更简洁
def buggy_function(data):
    for item in data:
        breakpoint()  # 等价于 pdb.set_trace()
        ...

# 方式2：命令行启动调试
# python -m pdb script.py

# pdb 常用命令：
# n (next)       → 执行下一行（不进入函数）
# s (step)       → 执行下一行（进入函数）
# c (continue)   → 继续执行到下一个断点
# l (list)       → 显示当前代码上下文
# p (print)      → 打印变量值：p x, p locals()
# pp (prettyprint) → 美化打印
# w (where)      → 显示调用栈
# u (up)         → 上移调用栈帧
# d (down)       → 下移调用栈帧
# b (break)      → 设置断点：b file.py:42, b function_name
# cl (clear)     → 清除断点
# r (return)     → 执行到当前函数返回
# q (quit)       → 退出调试器
# !              → 执行 Python 语句：!x = 10（修改变量）

# 实战：在循环中条件断点
for i, item in enumerate(data):
    if i == 42:  # 只在第43次迭代时暂停
        breakpoint()
    process(item)
```

#### 条件断点

```python
# pdb 条件断点
# 在 pdb 交互中：
# (pdb) b 42, x > 100  # 第42行，当 x > 100 时中断
# (pdb) b process_item, item.id == 42  # 函数中条件中断

# 代码中条件断点
def process_order(order):
    if order.total > 10000:  # 大额订单才调试
        breakpoint()
    ...

# 更优雅：用装饰器实现条件断点
def debug_if(condition):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if condition(*args, **kwargs):
                breakpoint()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@debug_if(lambda order: order.total > 10000)
def process_order(order):
    ...
```

#### 远程调试

```python
# 远程调试：调试运行在服务器/容器中的代码
# 方案1：debugpy（VS Code 官方推荐）
# pip install debugpy
import debugpy
debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()  # 阻塞直到调试器连接
# 然后在 VS Code 中配置 launch.json 连接到 5678 端口

# 方案2：rpdb（远程 pdb）
# pip install rpdb
import rpdb
rpdb.set_trace(addr="0.0.0.0", port=4444)
# 然后在另一台机器：nc server_ip 4444

# 方案3：pydevd（PyCharm 远程调试）
import pydevd_pycharm
pydevd_pycharm.settrace("localhost", port=12345, stdoutToServer=True, stderrToServer=True)
```

#### 日志调试策略

```python
import logging
from logging.handlers import RotatingFileHandler

# 配置日志：同时输出到控制台和文件
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 控制台处理器（INFO 级别）
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter("%(levelname)s: %(message)s")
console_handler.setFormatter(console_format)

# 文件处理器（DEBUG 级别，轮转）
file_handler = RotatingFileHandler(
    "app.log", maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter(
    "%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s"
)
file_handler.setFormatter(file_format)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 日志级别选择策略：
# DEBUG   → 详细的调试信息（变量值、函数入口/出口）
# INFO    → 正常运行信息（请求处理、任务完成）
# WARNING → 异常但可恢复的情况（重试、降级）
# ERROR   → 错误（异常捕获、操作失败）
# CRITICAL → 严重错误（系统不可用）

# 结构化日志（生产环境推荐）
# pip install python-json-logger
from pythonjsonlogger import jsonlogger
json_handler = logging.StreamHandler()
json_handler.setFormatter(jsonlogger.JsonFormatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(user_id)s"
))

# 在日志中添加上下文
class ContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = getattr(threading.local(), "request_id", "N/A")
        record.user_id = getattr(threading.local(), "user_id", "N/A")
        return True
```

#### 调试工具（py-spy, pyrasite）

```bash
# py-spy：非侵入式调试，不需要修改代码
# 查看正在运行的 Python 进程的调用栈
py-spy dump --pid 12345

# 实时查看函数执行时间（类似 top）
py-spy top --pid 12345

# 生成火焰图
py-spy record -o profile.svg --pid 12345 --duration 60

# pyrasite：注入代码到运行中的进程
# pip install pyrasite
# 创建注入脚本 debug_script.py
# import pdb; pdb.set_trace()
pyrasite 12345 debug_script.py

# 调试卡死的进程：
# 1. py-spy dump 查看当前调用栈
# 2. 如果是死锁，看多个线程的栈
# 3. 如果是无限循环，看哪个函数在顶部
```

---

### 5.2 单元测试

#### unittest框架

```python
import unittest

class TestStringMethods(unittest.TestCase):
    """测试用例类：继承 unittest.TestCase"""

    @classmethod
    def setUpClass(cls):
        """所有测试开始前执行一次（如创建数据库连接）"""
        cls.db = create_test_database()

    @classmethod
    def tearDownClass(cls):
        """所有测试结束后执行一次"""
        cls.db.close()

    def setUp(self):
        """每个测试方法执行前运行（如准备测试数据）"""
        self.test_data = [1, 2, 3]

    def tearDown(self):
        """每个测试方法执行后运行（如清理数据）"""
        pass

    def test_upper(self):
        """测试方法必须以 test_ 开头"""
        self.assertEqual("hello".upper(), "HELLO")

    def test_split(self):
        s = "hello world"
        self.assertEqual(s.split(), ["hello", "world"])
        with self.assertRaises(TypeError):
            s.split(2)  # 必须传字符串

    @unittest.skip("demonstrating skipping")
    def test_skip(self):
        self.fail("shouldn't happen")

    @unittest.skipIf(sys.version_info < (3, 8), "requires Python 3.8+")
    def test_walrus(self):
        ...

# 运行：python -m unittest test_module.py
# 运行所有：python -m unittest discover
```

#### pytest框架（推荐）

```python
# pytest 是更 Pythonic 的测试框架，功能更强大
# 安装：pip install pytest

# 简单测试（不需要类）
def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

# 测试类（不需要继承）
class TestCalculator:
    def test_add(self):
        assert Calculator().add(2, 3) == 5

    def test_divide_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            Calculator().divide(1, 0)

# pytest 断言比 unittest 更强大（自动显示详细差异）
def test_list_comparison():
    expected = [1, 2, 3, 4, 5]
    actual = [1, 2, 3, 4, 6]
    assert actual == expected
# 输出：assert [1, 2, 3, 4, 6] == [1, 2, 3, 4, 5]
#   At index 4 diff: 6 != 5

# 运行方式：
# pytest test_file.py           # 运行指定文件
# pytest -k "add"               # 按名称筛选
# pytest -v                     # 详细输出
# pytest -x                     # 第一个失败就停止
# pytest --tb=short             # 简短的回溯信息
# pytest --cov=src --cov-report=html  # 覆盖率
```

#### fixture与依赖注入

```python
import pytest

# fixture：测试的依赖注入机制
@pytest.fixture
def sample_data():
    """提供测试数据，每个测试函数独立"""
    return {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}

def test_user_count(sample_data):
    assert len(sample_data["users"]) == 2

# fixture 的作用域
@pytest.fixture(scope="function")  # 默认：每个测试函数创建一次
def function_scope_fixture(): ...

@pytest.fixture(scope="class")     # 每个测试类创建一次
def class_scope_fixture(): ...

@pytest.fixture(scope="module")    # 每个模块创建一次
def module_scope_fixture(): ...

@pytest.fixture(scope="session")   # 整个测试会话创建一次
def session_scope_fixture():
    """如数据库连接，整个测试会话共享"""
    db = create_test_database()
    yield db  # yield 之前是 setup，之后是 teardown
    db.close()

# fixture 的 teardown（用 yield）
@pytest.fixture
def temp_file():
    """创建临时文件，测试后自动删除"""
    path = "/tmp/test_file.txt"
    with open(path, "w") as f:
        f.write("test data")
    yield path  # 测试函数在这里执行
    os.remove(path)  # teardown

# fixture 可以依赖其他 fixture
@pytest.fixture
def db_connection():
    conn = create_connection()
    yield conn
    conn.close()

@pytest.fixture
def test_user(db_connection):
    user = create_user(db_connection, name="test")
    yield user
    delete_user(db_connection, user.id)

# conftest.py：共享 fixture 的配置文件
# tests/conftest.py 中定义的 fixture 可被所有测试使用
```

#### 参数化测试

```python
# @pytest.mark.parametrize：用多组输入测试同一逻辑
@pytest.mark.parametrize("input_val, expected", [
    (0, 0),
    (1, 1),
    (5, 120),
    (10, 3628800),
])
def test_factorial(input_val, expected):
    assert factorial(input_val) == expected

# 参数化测试用例命名
@pytest.mark.parametrize(
    "input_val, expected",
    [
        pytest.param(0, 0, id="zero"),
        pytest.param(1, 1, id="one"),
        pytest.param(5, 120, id="five"),
    ],
)
def test_factorial_named(input_val, expected):
    assert factorial(input_val) == expected

# 多参数组合
@pytest.mark.parametrize("a", [1, 2])
@pytest.mark.parametrize("b", [10, 20])
def test_multiplication(a, b):
    assert multiply(a, b) == a * b
# 生成 4 个测试：(1,10), (1,20), (2,10), (2,20)

# 从文件加载测试数据
def load_test_cases():
    with open("test_cases.json") as f:
        cases = json.load(f)
    return [(case["input"], case["expected"]) for case in cases]

@pytest.mark.parametrize("input_data, expected", load_test_cases())
def test_from_file(input_data, expected):
    assert process(input_data) == expected
```

#### 测试组织与命名

```text
# 推荐的测试目录结构
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── models.py
│       └── services.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # 共享 fixture
│   ├── unit/
│   │   ├── test_models.py
│   │   └── test_services.py
│   ├── integration/
│   │   ├── test_api.py
│   │   └── test_database.py
│   └── e2e/
│       └── test_user_flow.py
├── pyproject.toml
└── pytest.ini

# 命名规范：
# 测试文件：test_*.py 或 *_test.py
# 测试类：Test*（无 __init__）
# 测试函数：test_*
# 测试名称应描述行为：test_user_can_login_with_valid_credentials
# 而非：test_login_1, test_login_2
```

---

### 5.3 测试高级技术

#### Mock与patch

```python
from unittest.mock import Mock, patch, MagicMock, call

# Mock：创建模拟对象
mock_service = Mock()
mock_service.get_user.return_value = {"id": 1, "name": "Alice"}
mock_service.get_user(1)  # {'id': 1, 'name': 'Alice'}

# 验证调用
mock_service.get_user.assert_called_once_with(1)
mock_service.get_user.assert_called()
mock_service.get_user.assert_called_once()

# 模拟异常
mock_service.delete.side_effect = PermissionError("Not allowed")
mock_service.delete(1)  # raises PermissionError

# side_effect 可以是函数（动态返回值）
def side_effect(user_id):
    if user_id == 1:
        return {"id": 1}
    raise NotFoundError()
mock_service.get_user.side_effect = side_effect

# patch：替换模块中的对象
@patch("myapp.services.requests.get")
def test_api_call(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"data": "test"}

    result = myapp.services.fetch_data("http://example.com")

    mock_get.assert_called_once_with("http://example.com", timeout=10)
    assert result == {"data": "test"}

# patch 的多种用法
# 1. 装饰器
@patch("module.ClassName")
def test_func(mock_class): ...

# 2. 上下文管理器
def test_func():
    with patch("module.ClassName") as mock_class:
        ...

# 3. 手动 start/stop
def test_func():
    mock = patch("module.ClassName").start()
    try:
        ...
    finally:
        patch.stopall()

# patch.object：替换对象的方法
@patch.object(UserService, "get_user")
def test_user_service(mock_get_user):
    mock_get_user.return_value = User(id=1)
    ...

# MagicMock：支持魔术方法的 Mock
mock = MagicMock()
len(mock)  # 0（Mock 不支持，MagicMock 支持）
mock[0]    # 支持索引
iter(mock) # 支持迭代
```

#### 测试异常与边界

```python
import pytest

# 测试异常
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError) as exc_info:
        divide(1, 0)
    assert "division by zero" in str(exc_info.value)

# 测试异常类型和消息
def test_invalid_input():
    with pytest.raises(ValueError, match="must be positive"):
        process(-1)

# 边界值测试
@pytest.mark.parametrize("value", [
    0,           # 最小值
    1,           # 最小值+1
    99,          # 最大值-1
    100,         # 最大值
    -1,          # 越界（应抛异常）
    101,         # 越界（应抛异常）
])
def test_boundary_values(value):
    if 0 <= value <= 100:
        assert validate(value) == value
    else:
        with pytest.raises(ValueError):
            validate(value)

# 空值测试
def test_empty_input():
    assert process([]) == []
    assert process("") == ""
    assert process({}) == {}

# 大输入测试
def test_large_input():
    large_list = list(range(1000000))
    result = process(large_list)
    assert len(result) == 1000000
```

#### 属性测试（hypothesis）

```python
# hypothesis：自动生成大量测试用例，发现边界 bug
# 安装：pip install hypothesis

from hypothesis import given, strategies as st, settings, example

# 基础：自动生成整数
@given(st.integers())
def test_absolute_value(x):
    result = abs(x)
    assert result >= 0
    assert result == abs(-x)

# 生成复杂数据
@given(
    st.lists(st.integers(min_value=0, max_value=100), min_size=1, max_size=50)
)
@settings(max_examples=1000)  # 生成1000个测试用例
def test_sort_idempotent(data):
    """排序应该是幂等的：sort(sort(x)) == sort(x)"""
    sorted_once = sorted(data)
    sorted_twice = sorted(sorted_once)
    assert sorted_once == sorted_twice

# 生成自定义对象
user_strategy = st.fixed_dictionaries({
    "id": st.integers(min_value=1),
    "name": st.text(min_size=1, max_size=50),
    "email": st.from_regex(r"[^@]+@[^@]+\.[^@]+"),
})

@given(user_strategy)
def test_user_validation(user):
    assert validate_user(user) is True

# 重现特定用例
@example(x=0)  # 总是测试这个用例
@given(st.integers())
def test_with_example(x):
    ...

# hypothesis 的优势：
# 1. 自动发现你想不到的边界用例
# 2. 失败时自动缩小到最小复现用例（shrinking）
# 3. 适合测试纯函数和数据转换
```

#### 测试覆盖率

```bash
# coverage.py：测量测试覆盖率
# 安装：pip install coverage pytest-cov

# 运行测试并收集覆盖率
coverage run -m pytest tests/

# 查看报告
coverage report  # 终端报告
coverage html    # HTML 报告（htmlcov/index.html）
coverage xml     # XML 报告（CI 用）

# pytest-cov 插件（更方便）
pytest --cov=src --cov-report=term-missing --cov-report=html
# --cov=src：只统计 src 目录
# --cov-report=term-missing：终端显示未覆盖的行号
# --cov-report=html：生成 HTML 报告

# 覆盖率配置（pyproject.toml）
# [tool.coverage.run]
# source = ["src"]
# omit = ["*/tests/*", "*/migrations/*"]
#
# [tool.coverage.report]
# exclude_lines = [
#     "pragma: no cover",
#     "if __name__ == .__main__.:",
# ]
# fail_under = 80  # 覆盖率低于 80% 时失败

# 覆盖率的正确理解：
# 100% 覆盖率 ≠ 没有 bug（只说明每行都执行过，不说明逻辑正确）
# 但 < 50% 覆盖率通常意味着有未测试的关键路径
# 目标：核心业务逻辑 80%+，工具函数 90%+
```

#### 测试金字塔

```text
        /\           ← E2E 测试（少量，慢，贵）
       /  \          端到端：模拟真实用户操作
      /____\
     /      \        ← 集成测试（中等）
    /        \       模块间交互：API、数据库
   /__________\
  /            \     ← 单元测试（大量，快，便宜）
 /______________\    单个函数/类：纯逻辑，无外部依赖
```

```python
# 单元测试：快、隔离、大量
def test_calculate_discount():
    assert calculate_discount(100, "gold") == 20

# 集成测试：需要外部依赖，用 fixture 管理
@pytest.fixture
def test_db():
    db = create_test_database()
    migrate(db)
    yield db
    drop_test_database(db)

def test_user_creation_integration(test_db):
    user = UserRepository(test_db).create(name="Alice")
    assert user.id is not None
    assert test_db.query(User).get(user.id).name == "Alice"

# E2E 测试：用 Playwright/Selenium 模拟浏览器
# def test_user_login_flow(page):
#     page.goto("http://localhost:3000/login")
#     page.fill("#email", "test@example.com")
#     page.fill("#password", "password")
#     page.click("#login-button")
#     page.wait_for_url("**/dashboard")
#     assert "Welcome" in page.content()
```

---

### 5.4 测试驱动开发TDD

#### TDD循环（红-绿-重构）

```text
     红（Red）           绿（Green）        重构（Refactor）
  ┌────────────┐     ┌────────────┐     ┌────────────┐
  │ 写一个失败  │ ──→ │ 写最少代码  │ ──→ │ 优化代码结构 │
  │ 的测试      │     │ 让测试通过  │     │ 保持测试通过 │
  └────────────┘     └────────────┘     └────────────┘
        ↑                                      │
        └──────────────────────────────────────┘
```

#### 实战示例

```python
# 需求：实现一个函数，判断字符串是否是有效的密码
# 规则：至少8位，包含大小写字母和数字

# 步骤1：红 — 写失败的测试
def test_password_validation():
    assert is_valid_password("Abcdefg1") is True
    assert is_valid_password("short1") is False       # 太短
    assert is_valid_password("alllowercase1") is False  # 无大写
    assert is_valid_password("ALLUPPERCASE1") is False  # 无小写
    assert is_valid_password("NoNumbers") is False     # 无数字

# 运行：NameError: name 'is_valid_password' is not defined（红）

# 步骤2：绿 — 写最少代码让测试通过
import re
def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True

# 运行：全部通过（绿）

# 步骤3：重构 — 优化代码，保持测试通过
def is_valid_password(password: str) -> bool:
    """验证密码：至少8位，包含大小写字母和数字"""
    if len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_upper and has_lower and has_digit

# 运行：仍然全部通过（重构完成）

# 继续循环：添加新需求（特殊字符）
def test_password_special_char():
    assert is_valid_password("Abcdefg1!") is True  # 新规则：特殊字符可选

# 测试通过，不需要修改代码
```

#### TDD的适用场景

| 适合 TDD | 不适合 TDD |
|---------|-----------|
| 业务逻辑清晰的函数 | 探索性编程（不知道要做什么） |
| 算法和数据处理 | UI 布局和交互 |
| 重构已有代码 | 一次性脚本 |
| 库和框架开发 | 原型验证（先跑通再补测试） |
| Bug 修复（先写复现测试） | 性能优化（先测量再优化） |

> 🏆 **老手经验**：TDD 不是"必须先写所有测试"，而是"先写一个测试，看到它失败，再写代码让它通过"。关键是**小步快跑**，每次只加一个测试，每次只写让它通过的最少代码。对于复杂系统，可以先写集成测试定义行为，再用单元测试驱动内部实现。

---

### 5.5 性能测试与基准

#### 基准测试（pytest-benchmark）

```python
# pytest-benchmark：在 pytest 中做基准测试
# 安装：pip install pytest-benchmark

def test_fibonacci_benchmark(benchmark):
    # benchmark 会自动运行多次并统计
    result = benchmark(fibonacci, 30)
    assert result == 832040

# 对比两种实现
def test_list_comprehension_vs_loop(benchmark):
    data = list(range(10000))

    def with_comprehension():
        return [x * 2 for x in data]

    def with_loop():
        result = []
        for x in data:
            result.append(x * 2)
        return result

    # 对比两个函数
    benchmark(with_comprehension)
    benchmark(with_loop)

# 运行：pytest --benchmark-only
# 输出：
# Name (time in us)          Min      Max    Mean  StdDev  Median
# with_comprehension      210.50   350.20  230.10   20.50  225.30
# with_loop               380.10   520.80  400.20   25.30  395.60

# 保存基准用于回归对比
# pytest --benchmark-save=baseline
# 后续运行：pytest --benchmark-compare=baseline
```

#### 负载测试

```python
# locust：Python 编写的负载测试工具
# 安装：pip install locust

from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)  # 每个请求间隔1-3秒

    @task(3)  # 权重：3倍概率执行
    def view_items(self):
        self.client.get("/api/items")

    @task(1)
    def create_item(self):
        self.client.post("/api/items", json={"name": "test"})

    @task
    def view_item_detail(self):
        item_id = 1
        self.client.get(f"/api/items/{item_id}")

# 运行：locust -f locustfile.py --host=http://localhost:8000
# 打开 http://localhost:8089 设置并发用户数和加速时间

# 无界面模式（CI 用）
# locust -f locustfile.py --host=http://localhost:8000 \
#   --users 100 --spawn-rate 10 --run-time 5m --headless \
#   --html report.html
```

#### A/B性能对比

```python
import timeit
import statistics

def benchmark(func, *args, repeat=5, number=1000):
    """A/B 性能对比工具"""
    times = timeit.repeat(lambda: func(*args), repeat=repeat, number=number)
    return {
        "min": min(times) / number * 1000,  # ms
        "mean": statistics.mean(times) / number * 1000,
        "max": max(times) / number * 1000,
        "stddev": statistics.stdev(times) / number * 1000,
    }

# 对比两种实现
result_a = benchmark(implementation_a, data)
result_b = benchmark(implementation_b, data)

print(f"{'Implementation':<20} {'Min(ms)':<10} {'Mean(ms)':<10} {'StdDev':<10}")
print(f"{'A':<20} {result_a['min']:<10.3f} {result_a['mean']:<10.3f} {result_a['stddev']:<10.3f}")
print(f"{'B':<20} {result_b['min']:<10.3f} {result_b['mean']:<10.3f} {result_b['stddev']:<10.3f}")

speedup = result_a['mean'] / result_b['mean']
print(f"\nB is {speedup:.1f}x faster than A")
```

#### 性能回归监控

```python
# 在 CI 中集成性能回归检测
# 1. 保存基准数据
# 2. 每次 PR 运行基准测试
# 3. 对比历史数据，性能下降超过阈值则失败

# 简单实现
import json
import os

BASELINE_FILE = "benchmark_baseline.json"
THRESHOLD = 1.2  # 性能下降超过 20% 则失败

def save_baseline(results):
    with open(BASELINE_FILE, "w") as f:
        json.dump(results, f, indent=2)

def check_regression(current_results):
    if not os.path.exists(BASELINE_FILE):
        print("No baseline found, saving current as baseline")
        save_baseline(current_results)
        return

    with open(BASELINE_FILE) as f:
        baseline = json.load(f)

    for test_name, current in current_results.items():
        if test_name in baseline:
            baseline_time = baseline[test_name]["mean"]
            current_time = current["mean"]
            ratio = current_time / baseline_time
            if ratio > THRESHOLD:
                raise AssertionError(
                    f"Performance regression in {test_name}: "
                    f"{baseline_time:.3f}ms → {current_time:.3f}ms "
                    f"({ratio:.1f}x slower)"
                )
```

---

### 本章总结

调试和测试是**工程素养的核心**：
- 调试从 `print` 到 `pdb` 到 `py-spy`，逐步升级工具，但核心是"缩小范围、验证假设"
- pytest 的 fixture 和参数化是组织测试的利器，测试名称应描述行为而非实现
- Mock 用于隔离外部依赖，但不要过度 mock（mock 太多等于没测）
- TDD 的核心是"红-绿-重构"小步循环，适合逻辑清晰的代码
- 性能测试要和功能测试一样纳入 CI，防止性能回归

### 思考题/实战练习

1. **调试实战**：写一个包含 bug 的函数（如 off-by-one 错误），分别用 `print`、`pdb`、`py-spy` 三种方式定位 bug，记录每种方式的耗时。
2. **pytest fixture**：为一个需要数据库连接的服务编写测试，用 fixture 管理连接的创建和清理，对比 `setUp/tearDown` 方式的代码量。
3. **Mock 实战**：为一个调用外部 API 的函数编写测试，用 `patch` 模拟 API 响应，测试成功、超时、错误响应三种情况。
4. **hypothesis 属性测试**：用 hypothesis 测试一个字符串反转函数，自动生成包含 Unicode、空字符串、超长字符串的测试用例。
5. **TDD 实战**：用 TDD 实现一个罗马数字转整数的函数，先写测试（包含边界用例），再实现，最后重构。

---


## 6. 工程化最佳实践

工程化是"代码"变成"产品"的关键。一个人写的脚本可以随意，但团队协作的项目必须有规范——项目结构、代码风格、类型检查、CI/CD、安全实践，这些不是"可选项"，而是**交付质量的保障**。老手写的代码，别人能看懂、能维护、能安全上线。

### 6.1 项目结构

#### 标准项目目录结构

```text
myproject/
├── src/                          # 源代码（src 布局）
│   └── myproject/
│       ├── __init__.py
│       ├── __main__.py           # python -m myproject 入口
│       ├── config.py             # 配置管理
│       ├── models/               # 数据模型
│       │   ├── __init__.py
│       │   └── user.py
│       ├── services/             # 业务逻辑
│       │   ├── __init__.py
│       │   └── user_service.py
│       ├── api/                  # API 层
│       │   ├── __init__.py
│       │   └── routes.py
│       └── utils/                # 工具函数
│           ├── __init__.py
│           └── helpers.py
├── tests/                        # 测试
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── docs/                         # 文档
│   ├── index.md
│   └── api.md
├── scripts/                      # 运维脚本
│   ├── deploy.sh
│   └── migrate.py
├── data/                         # 数据文件（不入库）
├── .github/                      # GitHub 配置
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml                # 项目配置（统一入口）
├── README.md
├── CHANGELOG.md
├── LICENSE
└── Makefile                      # 常用命令快捷方式
```

#### src布局vs扁平布局

```python
# src 布局（推荐用于库和应用）
# 优点：测试时导入的是安装后的包，不是本地源码，能发现打包问题
# 缺点：需要 pip install -e . 才能运行

myproject/
├── src/
│   └── myproject/
│       └── __init__.py
└── tests/

# 扁平布局（适合简单脚本和小型项目）
# 优点：简单，不需要安装就能运行
# 缺点：测试可能导入本地源码而非安装的包，打包问题难发现

myproject/
├── myproject/
│   └── __init__.py
└── tests/
```

> 🏆 **老手经验**：发布到 PyPI 的库必须用 src 布局，因为它能确保测试的是"用户安装后得到的包"，而不是源码目录。内部应用可以用扁平布局降低复杂度，但项目一旦超过 3 个模块就应该迁移到 src 布局。

#### 单仓vs多仓

| 维度 | 单仓（Monorepo） | 多仓（Polyrepo） |
|------|-----------------|-----------------|
| 代码共享 | 容易，直接 import | 需要发布私有包 |
| 依赖管理 | 统一版本 | 各自独立 |
| CI/CD | 可能变慢（全量测试） | 各自独立，快速 |
| 权限控制 | 粗粒度（整个仓库） | 细粒度（每个仓库） |
| 适合场景 | 中小团队、紧密耦合的服务 | 大团队、独立部署的服务 |
| 工具 | Turborepo、Nx、Bazel | 各自独立 |

#### 配置管理

```python
# pydantic-settings：类型安全的配置管理
# 安装：pip install pydantic-settings

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    """应用配置：从环境变量、.env 文件、默认值加载"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # 忽略多余的环境变量
    )

    # 应用
    app_name: str = "myproject"
    debug: bool = False
    environment: str = Field(default="development", pattern="^(development|staging|production)$")

    # 数据库
    database_url: str = "postgresql://localhost/db"
    database_pool_size: int = Field(default=10, ge=1, le=100)

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # 安全
    secret_key: str = Field(default="change-me-in-production")
    api_rate_limit: int = Field(default=100, ge=1)

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if v == "change-me-in-production" and cls.environment == "production":
            raise ValueError("secret_key must be set in production")
        return v

settings = Settings()  # 全局单例

# 使用
print(settings.database_url)
print(settings.debug)

# .env 文件示例
# DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
# DEBUG=true
# SECRET_KEY=my-secret-key-12345
```

```python
# python-dotenv：轻量级配置（简单项目）
# 安装：pip install python-dotenv

from dotenv import load_dotenv
import os

load_dotenv()  # 加载 .env 文件

database_url = os.getenv("DATABASE_URL", "postgresql://localhost/db")
debug = os.getenv("DEBUG", "false").lower() == "true"
```

---

### 6.2 代码质量

#### PEP 8规范

```python
# PEP 8 核心规则（不是全部，是最常被违反的）

# 命名
# 变量/函数：snake_case
user_name = "Alice"
def calculate_total(): ...

# 类：PascalCase
class UserProfile: ...

# 常量：UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# 私有：_single_leading_underscore
_internal_state = {}

# 行长度：最大 79（代码），72（注释/docstring）
# 现代实践：black 默认 88，ruff 可配置

# 缩进：4 个空格，不用 tab
def function():
    if condition:
        do_something()

# 空行：函数之间 2 行，方法之间 1 行
def func1():
    pass


def func2():
    pass

class MyClass:
    def method1(self):
        pass

    def method2(self):
        pass

# 导入顺序：标准库 → 第三方 → 本地
import os
import sys

import requests
import numpy as np

from myproject import utils
from myproject.models import User

# 空格：运算符两侧、逗号后
x = a + b
result = func(arg1, arg2, arg3)
```

#### 代码格式化（black, autopep8）

```bash
# black：不妥协的代码格式化器（"你不需要决定格式，black 帮你决定"）
# 安装：pip install black

black src/ tests/           # 格式化
black --check src/          # 只检查不修改（CI 用）
black --diff src/           # 显示差异不修改

# black 配置（pyproject.toml）
# [tool.black]
# line-length = 88
# target-version = ["py311"]
# include = '\.pyi?$'
# extend-exclude = '''
# /(
#   \.eggs
# | \.git
# | build
# | dist
# )/
# '''

# autopep8：更温和的格式化器（只修复 PEP 8 问题，不改变代码结构）
# 安装：pip install autopep8
autopep8 --in-place --aggressive --aggressive src/
```

#### 代码检查（ruff, flake8, pylint）

```bash
# ruff：极速 Python linter（用 Rust 写的，比 flake8 快 10-100 倍）
# 安装：pip install ruff

ruff check src/ tests/      # 检查
ruff check --fix src/       # 自动修复
ruff format src/            # 格式化（替代 black）

# ruff 配置（pyproject.toml）
# [tool.ruff]
# line-length = 88
# target-version = "py311"
#
# [tool.ruff.lint]
# select = [
#   "E",   # pycodestyle errors
#   "W",   # pycodestyle warnings
#   "F",   # pyflakes
#   "I",   # isort (import sorting)
#   "B",   # flake8-bugbear
#   "UP",  # pyupgrade
#   "C4",  # flake8-comprehensions
#   "SIM", # flake8-simplify
# ]
# ignore = [
#   "E501",  # line too long（black 处理）
# ]
#
# [tool.ruff.lint.per-file-ignores]
# "tests/*" = ["B011", "S101"]  # 测试中允许 assert

# flake8：经典 linter（插件生态丰富）
# 安装：pip install flake8 flake8-bugbear flake8-comprehensions
flake8 src/

# pylint：最严格的 linter（代码评分、深度分析）
# 安装：pip install pylint
pylint src/
# 输出：Your code has been rated at 9.50/10
```

#### 类型检查（mypy, pyright）

```python
# mypy：静态类型检查器
# 安装：pip install mypy

# 基础类型注解
def greet(name: str) -> str:
    return f"Hello, {name}"

# 复杂类型
from typing import Optional, Union, List, Dict, Callable
from typing import TypedDict, Literal, Final

# Python 3.9+：内置泛型
def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# Optional
def find_user(user_id: int) -> Optional[User]:
    return users.get(user_id)  # 可能返回 None

# Literal：限定取值
def set_status(status: Literal["active", "inactive", "pending"]) -> None:
    ...

# TypedDict：字典结构
class UserData(TypedDict):
    name: str
    age: int
    email: str  # required
    phone: NotRequired[str]  # optional (Python 3.11+)

# Final：常量
MAX_RETRIES: Final = 3

# mypy 配置（pyproject.toml）
# [tool.mypy]
# python_version = "3.11"
# strict = true              # 严格模式
# warn_return_any = true
# warn_unused_configs = true
# disallow_untyped_defs = true
# ignore_missing_imports = true  # 忽略没有类型存根的第三方库

# 运行：mypy src/
# pyright：微软出品的类型检查器（更快，VS Code 内置）
# 安装：pip install pyright
# pyright src/
```

#### pre-commit钩子

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ["--maxkb=500"]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-redis]

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
```

```bash
# 安装和使用
pip install pre-commit
pre-commit install           # 安装 git 钩子
pre-commit run --all-files   # 手动运行所有检查
pre-commit run ruff          # 只运行特定钩子
pre-commit autoupdate        # 更新钩子版本
```

---

### 6.3 文档与API

#### docstring规范

```python
# Google 风格（推荐：简洁易读）
def calculate_discount(price: float, discount_rate: float) -> float:
    """计算折扣后的价格。

    Args:
        price: 原始价格，必须大于 0。
        discount_rate: 折扣率，0 到 1 之间的小数。

    Returns:
        折扣后的价格。

    Raises:
        ValueError: 如果 price 小于等于 0，或 discount_rate 不在 [0, 1] 范围内。

    Examples:
        >>> calculate_discount(100, 0.2)
        80.0
    """
    if price <= 0:
        raise ValueError("price must be positive")
    if not 0 <= discount_rate <= 1:
        raise ValueError("discount_rate must be between 0 and 1")
    return price * (1 - discount_rate)

# NumPy 风格（详细，适合科学计算）
def matrix_multiply(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    矩阵乘法。

    Parameters
    ----------
    a : np.ndarray
        第一个矩阵，形状为 (m, k)。
    b : np.ndarray
        第二个矩阵，形状为 (k, n)。

    Returns
    -------
    np.ndarray
        结果矩阵，形状为 (m, n)。

    Raises
    ------
    ValueError
        如果矩阵形状不兼容。
    """

# reStructuredText 风格（Sphinx 原生支持）
def connect(host: str, port: int) -> Connection:
    """连接到服务器。

    :param host: 服务器地址
    :type host: str
    :param port: 端口号
    :type port: int
    :returns: 连接对象
    :rtype: Connection
    :raises ConnectionError: 连接失败时
    """
```

#### 自动文档生成

```bash
# MkDocs + mkdocstrings：现代文档生成（推荐）
# 安装：pip install mkdocs mkdocstrings[python] mkdocs-material

# mkdocs.yml
# site_name: My Project
# theme:
#   name: material
# plugins:
#   - search
#   - mkdocstrings:
#       handlers:
#         python:
#           options:
#             show_source: true
#             show_signature_annotations: true

# docs/index.md
# # My Project
# ::: myproject.services.user_service.UserService
#     options:
#       members: true

# 构建和预览
mkdocs serve          # 本地预览 http://127.0.0.1:8000
mkdocs build          # 构建到 site/
mkdocs gh-deploy      # 部署到 GitHub Pages

# Sphinx：经典文档生成（更强大，配置更复杂）
# 安装：pip install sphinx sphinx-rtd-theme
# sphinx-quickstart    # 初始化
# sphinx-apidoc -o docs/ src/  # 自动生成 API 文档
# make html            # 构建
```

#### API设计原则

```python
# RESTful API 设计原则

# 1. 资源命名：用名词复数，不用动词
# ✅ GET /api/users
# ❌ GET /api/getUsers
# ✅ POST /api/users
# ❌ POST /api/createUser

# 2. HTTP 方法语义
# GET    /api/users       → 列表
# GET    /api/users/123   → 详情
# POST   /api/users       → 创建
# PUT    /api/users/123   → 全量更新
# PATCH  /api/users/123   → 部分更新
# DELETE /api/users/123   → 删除

# 3. 版本控制
# URL 版本：/api/v1/users（推荐，简单直观）
# Header 版本：Accept: application/vnd.myapp.v1+json
# 查询参数：/api/users?version=1（不推荐）

# 4. 统一响应格式
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""
    success: bool
    data: Optional[T] = None
    error: Optional[dict] = None
    meta: Optional[dict] = None  # 分页信息等

# 成功响应
# {"success": true, "data": {"id": 1, "name": "Alice"}, "error": null}
# 错误响应
# {"success": false, "data": null, "error": {"code": "NOT_FOUND", "message": "User not found"}}

# 5. 分页
# GET /api/users?page=1&page_size=20
# 响应 meta: {"page": 1, "page_size": 20, "total": 150, "total_pages": 8}

# 6. 错误码：用有意义的字符串，不用数字
# ✅ "USER_NOT_FOUND", "INVALID_EMAIL"
# ❌ 1001, 1002
```

#### 版本管理（语义化版本）

```text
版本号格式：MAJOR.MINOR.PATCH

MAJOR（主版本）：不兼容的 API 变更
MINOR（次版本）：向后兼容的功能新增
PATCH（修订号）：向后兼容的问题修复

示例：
1.0.0 → 1.0.1  修复 bug（PATCH）
1.0.1 → 1.1.0  新增功能，不破坏现有 API（MINOR）
1.1.0 → 2.0.0  破坏兼容性的变更（MAJOR）

预发布版本：
1.0.0-alpha.1   内部测试
1.0.0-beta.1    公开测试
1.0.0-rc.1      发布候选

依赖版本约束（pyproject.toml）：
"requests>=2.28.0,<3.0.0"   # 兼容范围
"requests==2.31.0"          # 精确版本
"requests~=2.31.0"          # 等价于 >=2.31.0,<3.0.0
"requests^2.31.0"           # 等价于 >=2.31.0,<3.0.0 (poetry)
```

---

### 6.4 CI/CD

#### GitHub Actions for Python

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    name: Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Lint with ruff
        run: ruff check src/ tests/

      - name: Type check with mypy
        run: mypy src/

      - name: Test with pytest
        run: |
          pytest tests/ --cov=src --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json

      - name: Run pip-audit
        run: |
          pip install pip-audit
          pip-audit
```

#### 自动化测试/lint/类型检查

```makefile
# Makefile：统一常用命令
.PHONY: install lint format test type-check coverage clean

install:
	pip install -e ".[dev]"
	pre-commit install

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

type-check:
	mypy src/

test:
	pytest tests/ -v

test-watch:
	pytest tests/ -v --lf --pdb

coverage:
	pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo "Open htmlcov/index.html"

security:
	bandit -r src/
	pip-audit

all: lint type-check test security

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage
```

#### 自动发布

```yaml
# .github/workflows/release.yml
name: Release

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install build tools
        run: pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

#### 代码覆盖率报告

```yaml
# 覆盖率门禁：低于阈值失败
- name: Test with coverage
  run: |
    pytest tests/ --cov=src --cov-report=xml --cov-fail-under=80
# --cov-fail-under=80：覆盖率低于 80% 时退出码非零，CI 失败

# 覆盖率徽章（README 中显示）
# [![codecov](https://codecov.io/gh/user/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/user/repo)
```

---

### 6.5 安全实践

#### 依赖安全

```bash
# pip-audit：检查依赖中的已知漏洞
# 安装：pip install pip-audit
pip-audit                    # 检查已安装的包
pip-audit -r requirements.txt  # 检查 requirements 文件
pip-audit --desc on          # 显示漏洞描述
pip-audit --fix              # 自动升级有漏洞的包

# safety：另一个依赖安全检查工具
# 安装：pip install safety
safety check                 # 检查
safety check --json          # JSON 输出（CI 用）

# 依赖锁定：确保所有环境使用相同版本
# pip-tools：pip-compile requirements.in → requirements.txt
# poetry：poetry.lock
# uv：uv.lock
```

#### 代码安全（bandit）

```bash
# bandit：Python 代码安全扫描器
# 安装：pip install bandit

bandit -r src/                    # 递归扫描
bandit -r src/ -f json -o report.json  # JSON 输出
bandit -r src/ --severity-level high   # 只显示高危问题

# bandit 常见检测项：
# B101：assert 用在生产代码（assert 在优化模式下被移除）
# B102：exec 使用（代码注入风险）
# B103：set_bad_file_permissions（文件权限过宽）
# B105/B106：硬编码密码/密钥
# B108：硬编码临时目录（竞态条件）
# B110：try/except 吞异常
# B301：pickle 反序列化（任意代码执行）
# B303：MD5/SHA1（弱哈希）
# B307：eval 使用（代码注入）
# B324：hashlib 弱哈希
```

#### 输入验证

```python
from pydantic import BaseModel, field_validator, EmailStr, constr
import re

# 永远不要信任用户输入！所有外部输入必须验证

class UserCreate(BaseModel):
    """用户创建请求：所有字段严格验证"""
    name: constr(min_length=1, max_length=50, pattern=r"^[a-zA-Z0-9_\- ]+$")
    email: EmailStr  # 自动验证邮箱格式
    password: constr(min_length=8, max_length=128)
    age: int = Field(ge=0, le=150)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("password must contain uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("password must contain lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("password must contain digit")
        return v

# SQL 注入防护：永远用参数化查询
# ❌ 危险：字符串拼接
query = f"SELECT * FROM users WHERE email = '{email}'"
db.execute(query)

# ✅ 安全：参数化查询
query = "SELECT * FROM users WHERE email = ?"
db.execute(query, (email,))

# XSS 防护：输出时转义
from html import escape
user_input = "<script>alert('xss')</script>"
safe_output = escape(user_input)  # &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;
```

#### secrets管理

```python
# 永远不要把密钥提交到代码仓库！

# 1. 环境变量（最常用）
import os
api_key = os.environ["API_KEY"]  # 生产环境从环境变量读取

# 2. .env 文件（开发环境，加入 .gitignore）
# .env
# API_KEY=sk-1234567890abcdef
# DATABASE_URL=postgresql://user:pass@localhost/db

# .gitignore
# .env
# *.key
# *.pem

# 3. 密钥管理服务（生产环境推荐）
# AWS Secrets Manager、HashiCorp Vault、Azure Key Vault
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name: str) -> dict:
    """从 AWS Secrets Manager 获取密钥"""
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager")
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except ClientError as e:
        logger.error("Failed to get secret: %s", e)
        raise

# 4. 检查代码中是否有硬编码密钥
# pip install detect-secrets
# detect-secrets scan > .secrets.baseline
# detect-secrets audit .secrets.baseline
```

#### 常见安全漏洞

```python
# 1. SQL 注入（已在上面讲过）

# 2. XSS（跨站脚本）
# 模板引擎自动转义（Jinja2 默认开启）
# 但 |safe 过滤器会禁用转义，慎用

# 3. 反序列化漏洞
# ❌ 危险：pickle 反序列化不可信数据
import pickle
data = pickle.loads(user_input)  # 可能执行任意代码！

# ✅ 安全：用 JSON 替代
import json
data = json.loads(user_input)  # 只能解析 JSON，不能执行代码

# 4. 路径遍历
# ❌ 危险：用户输入直接拼接到文件路径
filename = request.args.get("file")
with open(f"/data/{filename}") as f:  # 可能读到 /etc/passwd
    ...

# ✅ 安全：验证路径，用 os.path.realpath 检查
base_dir = "/data/"
file_path = os.path.realpath(os.path.join(base_dir, filename))
if not file_path.startswith(base_dir):
    raise PermissionError("Invalid file path")

# 5. 命令注入
# ❌ 危险：shell=True + 用户输入
import subprocess
subprocess.run(f"ping {host}", shell=True)  # host = "8.8.8.8; rm -rf /"

# ✅ 安全：参数列表，不用 shell
subprocess.run(["ping", "-c", "1", host])  # host 被当作单个参数

# 6. 不安全的随机数
# ❌ 危险：random 模块不是密码学安全的
import random
token = random.randint(0, 10**20)  # 可预测

# ✅ 安全：secrets 模块
import secrets
token = secrets.token_urlsafe(32)  # 密码学安全的随机 token
```

---

### 6.6 生产级监控与可观测性

> 🏆 **老手经验**：没有监控的系统就是在裸奔。可观测性不是"上线后再加"，而是和功能代码一起写的。老手在写业务逻辑时就会想：这个操作需要什么指标？出了问题怎么排查？需要什么日志？

#### 可观测性三支柱

| 支柱 | 回答的问题 | 工具 | 特点 |
|------|-----------|------|------|
| **日志（Logging）** | 发生了什么？ | ELK、Loki、CloudWatch | 离散事件，详细但量大 |
| **指标（Metrics）** | 系统现在怎么样？ | Prometheus、Datadog、Graphite | 数值聚合，可告警，成本低 |
| **追踪（Tracing）** | 请求经过了哪些服务？耗时在哪？ | Jaeger、Zipkin、OpenTelemetry | 跨服务调用链，定位瓶颈 |

三者关系：**指标发现问题 → 追踪定位问题 → 日志排查根因**。

```python
# OpenTelemetry：统一的可观测性标准（日志+指标+追踪）
# pip install opentelemetry-api opentelemetry-sdk
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider

# 初始化追踪
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# 初始化指标
metrics.set_meter_provider(MeterProvider())
meter = metrics.get_meter(__name__)

# 在业务代码中埋点
with tracer.start_as_current_span("process_order") as span:
    span.set_attribute("order_id", order.id)
    span.set_attribute("user_id", user.id)
    try:
        result = process(order)
        span.set_status(trace.StatusCode.OK)
        return result
    except Exception as e:
        span.record_exception(e)
        span.set_status(trace.StatusCode.ERROR, str(e))
        raise
```

#### Prometheus指标采集

```python
# prometheus_client：Python 官方 Prometheus 客户端
# pip install prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
import time
import functools

# 四种核心指标类型

# 1. Counter（计数器）：只增不减，适合统计请求数、错误数
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],  # 标签维度
)

# 2. Histogram（直方图）：统计分布，适合延迟、响应大小
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# 3. Gauge（仪表盘）：可增可减，适合当前连接数、队列长度
ACTIVE_CONNECTIONS = Gauge(
    "active_connections",
    "Current active database connections",
)

# 4. Summary（摘要）：类似 Histogram，但计算分位数在客户端
REQUEST_SIZE = Summary("http_request_size_bytes", "Request size")

# 装饰器：自动统计请求数和延迟
def monitor(endpoint: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            status = "200"
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "500"
                raise
            finally:
                latency = time.perf_counter() - start
                REQUEST_COUNT.labels(method="GET", endpoint=endpoint, status=status).inc()
                REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
        return wrapper
    return decorator

# 启动指标暴露端点（通常在独立端口 9090）
start_http_server(9090)
# Prometheus 配置 scrape 这个端点即可采集

# FastAPI 集成示例
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    latency = time.perf_counter() - start
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=str(response.status_code),
    ).inc()
    REQUEST_LATENCY.labels(endpoint=request.url.path).observe(latency)
    return response
```

```yaml
# prometheus.yml — Prometheus 采集配置
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "python-app"
    static_configs:
      - targets: ["app:9090"]  # 应用的指标端点

  - job_name: "nginx"
    static_configs:
      - targets: ["nginx:9113"]
```

#### Grafana仪表盘

Grafana 是可视化面板工具，从 Prometheus 等数据源读取指标，构建仪表盘。

**核心面板类型**：
- **Time series**：指标随时间变化（QPS、延迟、错误率）
- **Stat**：单个关键数字（当前在线用户、今日订单数）
- **Gauge**：仪表盘（CPU 使用率、内存占用）
- **Table**：表格（Top N 慢查询、错误排行）
- **Heatmap**：热力图（延迟分布）

**老手仪表盘设计原则**：
1. **RED 方法**（服务级别）：Rate（请求率）、Errors（错误率）、Duration（延迟）
2. **USE 方法**（资源级别）：Utilization（利用率）、Saturation（饱和度）、Errors（错误）
3. **每个服务至少有**：QPS 面板、P50/P95/P99 延迟面板、错误率面板、资源使用面板
4. **设置告警阈值**：P99 延迟 > 1s 告警，错误率 > 1% 告警

#### 日志聚合

```python
# 结构化日志（JSON 格式），方便日志系统解析
import logging
import json
from pythonjsonlogger import jsonlogger

class ContextFilter(logging.Filter):
    """注入请求上下文到日志"""
    def filter(self, record):
        record.request_id = getattr(threading.local(), "request_id", "N/A")
        record.user_id = getattr(threading.local(), "user_id", "N/A")
        return True

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(user_id)s"
)
handler.setFormatter(formatter)
handler.addFilter(ContextFilter())
logger.addHandler(handler)

# 日志输出（JSON 格式，Loki/ELK 可直接解析）
# {"asctime": "2026-09-09 10:00:00", "levelname": "INFO", "message": "User login", "request_id": "abc123", "user_id": "42"}
```

**日志聚合方案对比**：

| 方案 | 组件 | 适用场景 | 特点 |
|------|------|---------|------|
| **ELK** | Elasticsearch + Logstash + Kibana | 中大型团队 | 功能强大，资源消耗高 |
| **Loki** | Loki + Promtail + Grafana | 中小团队/K8s | 轻量，与 Grafana 集成好，按标签索引 |
| **EFK** | Elasticsearch + Fluentd + Kibana | K8s 环境 | Fluentd 采集能力强 |
| **云服务** | CloudWatch、SLS、CLS | 云上部署 | 免运维，成本高 |

> 💡 **提示**：Loki 的设计理念是"日志就是日志"——不为全文建索引，只索引标签（类似 Prometheus），因此存储成本只有 ELK 的 1/10。中小团队优先选 Loki + Grafana。

#### 告警机制基础

```yaml
# alerting.yml — Prometheus 告警规则
groups:
  - name: python_app_alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m]))
          > 0.05
        for: 2m  # 持续2分钟才触发
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.endpoint }}"
          description: "Error rate is {{ $value | humanizePercentage }} for more than 2 minutes"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.99,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P99 latency > 1s on {{ $labels.endpoint }}"

      - alert: ServiceDown
        expr: up{job="python-app"} == 0
        for: 1m
        labels:
          severity: critical
```

**告警设计原则**：
1. **可操作**：每个告警都应该有明确的处理步骤，不能"告警了但不知道怎么办"
2. **分级**：critical（立即处理）、warning（关注）、info（记录）
3. **抑制**：服务宕机时不要同时告警 100 个依赖它的指标
4. **降噪**：设置 `for` 持续时间，避免瞬时波动误报
5. **复盘**：每次告警都要回顾是否合理，定期清理无效告警

---

### 6.7 消息队列基础

消息队列是分布式系统的"神经系统"——解耦服务、削峰填谷、异步处理。老手知道什么时候该用队列、该选哪种队列。

#### 使用场景

```text
1. 异步解耦
   用户注册 → 发消息到队列 → [邮件服务] [积分服务] [数据分析服务] 各自消费
   好处：注册接口不需要等所有下游完成，下游挂了不影响注册

2. 削峰填谷
   秒杀活动 → 瞬时 10万 QPS → 队列缓冲 → 消费者按 1000 QPS 平稳处理
   好处：保护下游服务不被冲垮

3. 最终一致性
   订单服务 → 发"订单已创建"消息 → 库存服务扣库存 → 支付服务创建支付单
   好处：分布式事务的替代方案，保证最终一致

4. 广播通知
   配置更新 → 发消息 → 所有服务实例刷新本地缓存
   好处：一对多通知，不需要逐个调用
```

#### RabbitMQ基础概念

```python
# pika：RabbitMQ 的 Python 客户端
# pip install pika
import pika
import json

# RabbitMQ 核心概念：
# Producer（生产者）→ Exchange（交换机）→ Queue（队列）→ Consumer（消费者）
#
# Exchange 类型：
# - direct：按 routing_key 精确匹配路由
# - fanout：广播到所有绑定的队列
# - topic：按模式匹配（支持 * 和 # 通配符）
# - headers：按消息头匹配

class RabbitMQProducer:
    """RabbitMQ 生产者：连接管理 + 消息发布"""
    def __init__(self, host: str = "localhost", port: int = 5672):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port, heartbeat=60)
        )
        self.channel = self.connection.channel()
        # 声明交换机（持久化）
        self.channel.exchange_declare(
            exchange="events", exchange_type="topic", durable=True
        )

    def publish(self, routing_key: str, payload: dict):
        """发布消息，delivery_mode=2 表示持久化"""
        self.channel.basic_publish(
            exchange="events",
            routing_key=routing_key,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,  # 持久化消息
                content_type="application/json",
            ),
        )

    def close(self):
        self.connection.close()

class RabbitMQConsumer:
    """RabbitMQ 消费者：手动确认 + 死信队列"""
    def __init__(self, host: str = "localhost"):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host)
        )
        self.channel = self.connection.channel()
        # 声明死信队列
        self.channel.exchange_declare(exchange="dlx", exchange_type="fanout")
        self.channel.queue_declare(queue="dead_letter", durable=True)
        self.channel.queue_bind(queue="dead_letter", exchange="dlx")

        # 声明业务队列，绑定死信交换机
        self.channel.queue_declare(
            queue="order_events",
            durable=True,
            arguments={"x-dead-letter-exchange": "dlx"},
        )
        self.channel.queue_bind(
            queue="order_events", exchange="events", routing_key="order.*"
        )
        # prefetch_count=1：公平调度，一次只处理一条
        self.channel.basic_qos(prefetch_count=1)

    def start_consuming(self, handler):
        def callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                handler(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)  # 手动确认
            except Exception as e:
                # 处理失败，拒绝消息（进入死信队列）
                logger.error("处理消息失败: %s", e)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        self.channel.basic_consume(queue="order_events", on_message_callback=callback)
        self.channel.start_consuming()
```

#### Celery任务队列

```python
# Celery：Python 生态最流行的分布式任务队列
# pip install celery redis
from celery import Celery
from celery.schedules import crontab

# 初始化 Celery 应用
app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",       # 消息代理
    backend="redis://localhost:6379/1",      # 结果存储
)

# 配置
app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_acks_late=True,           # 任务执行完再确认（worker 崩溃不丢任务）
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,  # 公平调度
    task_default_retry_delay=30,   # 默认重试延迟30秒
    task_max_retries=3,            # 最大重试3次
)

# 定义任务
@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(ConnectionError, TimeoutError),
)
def send_welcome_email(self, user_id: int):
    """发送欢迎邮件，失败自动重试"""
    try:
        user = get_user(user_id)
        email_service.send(user.email, "欢迎加入", template="welcome")
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)  # 60秒后重试

@app.task
def generate_report(report_id: int):
    """生成报表（耗时任务）"""
    report = Report.objects.get(id=report_id)
    data = fetch_large_dataset(report.params)
    report.file = render_pdf(data)
    report.status = "completed"
    report.save()

# 定时任务
app.conf.beat_schedule = {
    "daily-cleanup": {
        "task": "tasks.cleanup_old_data",
        "schedule": crontab(hour=3, minute=0),  # 每天凌晨3点
    },
    "health-check": {
        "task": "tasks.health_check",
        "schedule": 300.0,  # 每5分钟
    },
}

# 调用任务
result = send_welcome_email.delay(42)  # 异步执行
result = send_welcome_email.apply_async(
    args=[42], countdown=10  # 10秒后执行
)
result.get(timeout=10)  # 等待结果（阻塞）

# 启动 worker
# celery -A tasks worker --loglevel=info --concurrency=4
# 启动定时任务调度器
# celery -A tasks beat
```

#### Kafka适用场景对比

| 维度 | RabbitMQ | Kafka | Redis Stream |
|------|----------|-------|-------------|
| 定位 | 传统消息代理 | 分布式流平台 | 内存消息队列 |
| 吞吐量 | 万级 QPS | 百万级 QPS | 十万级 QPS |
| 消息保留 | 消费后删除 | 按时间/大小保留 | 按容量裁剪 |
| 路由能力 | 强大（4种交换机） | 简单（按partition） | 简单 |
| 顺序保证 | 单队列有序 | 单partition有序 | 单流有序 |
| 协议 | AMQP | 自定义TCP | RESP |
| 适用场景 | 业务解耦、任务调度 | 日志收集、事件流、大数据 | 简单异步、实时通知 |
| 运维复杂度 | 中 | 高（依赖ZooKeeper/KRaft） | 低 |

> 🏆 **选择建议**：
> - **业务异步任务**（发邮件、生成报表）→ Celery + Redis/RabbitMQ
> - **服务间解耦**（订单→库存→支付）→ RabbitMQ
> - **日志/事件流**（用户行为、系统日志）→ Kafka
> - **实时通知**（WebSocket推送）→ Redis Stream/Pub/Sub
> - **大数据管道**（Spark/Flink消费）→ Kafka

---

### 本章总结

工程化是**代码质量的基础设施**：
- 项目结构用 src 布局，配置用 pydantic-settings 类型安全管理
- 代码质量工具链：ruff（lint+format）+ mypy（类型检查）+ pre-commit（自动执行）
- 文档用 Google 风格 docstring + MkDocs 自动生成
- CI/CD 用 GitHub Actions 自动化测试、lint、类型检查、安全扫描、发布
- 安全是每个人的责任：输入验证、参数化查询、密钥管理、依赖扫描

> 🏆 **老手经验**：工程化的目标不是"遵守规则"，而是"减少意外"。每一个工具（lint、类型检查、测试、CI）都是在帮你在问题到达用户之前发现它。投入工程化的时间，会在减少 bug 和加速开发中十倍赚回来。

### 思考题/实战练习

1. **项目脚手架**：为一个新的 Python 项目创建完整的工程化配置（pyproject.toml、pre-commit、CI、目录结构），确保 `make all` 一条命令完成所有检查。
2. **类型检查实践**：给一个没有类型注解的项目添加 mypy 严格模式，修复所有类型错误，记录修复过程中发现的潜在 bug。
3. **CI 流水线**：配置一个 GitHub Actions 流水线，包含多 Python 版本测试、覆盖率报告、安全扫描，覆盖率低于 80% 时失败。
4. **安全审计**：用 bandit 和 pip-audit 扫描一个现有项目，修复所有高危问题，写一份安全审计报告。
5. **API 设计**：为一个用户管理系统设计 RESTful API，包含版本控制、统一响应格式、分页、错误码，用 FastAPI 实现并自动生成 OpenAPI 文档。

---


## 7. 常见面试题精讲

面试题不是"背答案"，而是**检验理解深度**。老手回答面试题时，不仅说"是什么"，还说"为什么"、"在什么场景下用"、"有什么坑"。本章精选 Python 面试中最高频的题目，每个题目给出原理、代码和回答思路。

### 7.1 语言基础面试题

#### GIL相关

> 🔥 **面试高频考点**：GIL 是什么？对性能有什么影响？如何绕过？

**GIL（Global Interpreter Lock，全局解释器锁）** 是 CPython 中的一把互斥锁，确保同一时刻只有一个线程执行 Python 字节码。

**为什么需要 GIL？**
- CPython 的内存管理使用引用计数，引用计数变量需要线程安全保护
- 如果不用 GIL，需要给所有对象加细粒度锁，性能开销更大且容易死锁
- GIL 是"一把大锁"，实现简单，单线程性能好

**对性能的影响：**
- CPU 密集型任务：多线程无法并行，因为 GIL 只让一个线程跑
- I/O 密集型任务：影响小，因为等待 I/O 时 GIL 会释放
- 多进程：每个进程有独立的 GIL，可以真正并行

```python
# 验证 GIL 对 CPU 密集型的影响
import threading
import time

def cpu_bound(n):
    return sum(i*i for i in range(n))

# 单线程
start = time.time()
cpu_bound(10**7)
cpu_bound(10**7)
print(f"Single thread: {time.time()-start:.2f}s")  # ~2.0s

# 多线程（不会更快！）
start = time.time()
t1 = threading.Thread(target=cpu_bound, args=(10**7,))
t2 = threading.Thread(target=cpu_bound, args=(10**7,))
t1.start(); t2.start()
t1.join(); t2.join()
print(f"Two threads: {time.time()-start:.2f}s")  # ~2.0s（没有加速）
```

**绕过 GIL 的方法：**
1. **多进程**（multiprocessing）：每个进程独立 GIL，适合 CPU 密集
2. **C 扩展释放 GIL**：NumPy、Pandas 在 C 层操作时释放 GIL
3. **asyncio**：单线程并发，适合 I/O 密集
4. **无 GIL 解释器**：PyPy（部分版本）、GraalPython、PEP 703（Python 3.13 实验性 free-threaded）

> 🏆 **回答思路**：先定义 GIL → 解释为什么需要（引用计数）→ 分析影响（CPU 密集 vs I/O 密集）→ 给出解决方案（多进程/C扩展/asyncio）→ 提到 PEP 703 无 GIL 趋势。

#### 装饰器相关

> 🔥 **面试高频考点**：手写装饰器、带参数的装饰器、装饰器的应用场景

```python
# 基础装饰器
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter()-start:.3f}s")
        return result
    return wrapper

# 带参数的装饰器（三层嵌套）
def retry(max_attempts=3, delay=1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

# 类装饰器
class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0
    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)
```

**常见应用场景**：日志记录、性能计时、重试、缓存（lru_cache）、权限验证、输入验证、事务管理、路由注册（Flask/FastAPI）。

> 🏆 **回答思路**：先写基础装饰器（两层）→ 再写带参数的（三层）→ 说明 `functools.wraps` 的作用（保留元信息）→ 列举应用场景 → 提到装饰器的性能开销和堆叠顺序。

#### 可变/不可变相关

> 🔥 **面试高频考点**：哪些类型可变/不可变？可变默认参数的坑？

| 类型 | 可变/不可变 | 说明 |
|------|-----------|------|
| int, float, bool | 不可变 | 数值类型 |
| str, bytes | 不可变 | 字符串 |
| tuple | 不可变 | 元组（但元素可能可变） |
| frozenset | 不可变 | 不可变集合 |
| list | 可变 | 列表 |
| dict | 可变 | 字典 |
| set | 可变 | 集合 |
| bytearray | 可变 | 可变字节数组 |

```python
# 可变默认参数的经典坑
def append_to(item, target=[]):
    target.append(item)
    return target

print(append_to(1))  # [1]
print(append_to(2))  # [1, 2]  ← 不是预期的 [2]！
print(append_to(3))  # [1, 2, 3]

# 原因：默认参数在函数定义时创建一次，不是每次调用时创建
# 正确做法
def append_to(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

> 🏆 **回答思路**：列举可变/不可变类型 → 解释不可变的含义（对象创建后值不能改，"修改"实际是创建新对象）→ 重点讲可变默认参数坑 → 提到不可变对象可哈希、可作字典键。

#### 深拷贝浅拷贝

```python
import copy

a = [1, 2, [3, 4]]
b = a              # 引用：同一个对象
c = copy.copy(a)   # 浅拷贝：顶层复制，嵌套对象共享引用
d = copy.deepcopy(a)  # 深拷贝：递归复制所有对象

a[0] = 99
a[2].append(5)

print(a)  # [99, 2, [3, 4, 5]]
print(b)  # [99, 2, [3, 4, 5]]  ← 引用，完全同步
print(c)  # [1, 2, [3, 4, 5]]   ← 浅拷贝，顶层独立，嵌套共享
print(d)  # [1, 2, [3, 4]]      ← 深拷贝，完全独立
```

**浅拷贝的方式**：`copy.copy()`、`list[:]`、`dict.copy()`、`list.copy()`、工厂函数 `list(d)`。

**深拷贝的注意事项**：
- 递归对象（循环引用）不会无限递归，deepcopy 会记录已复制对象
- 可以通过 `__deepcopy__` 自定义深拷贝行为
- 深拷贝比浅拷贝慢得多，大数据量时注意性能

#### is vs ==

```python
# == 比较值（调用 __eq__）
# is 比较身份（内存地址，即 id()）

a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)  # True（值相等）
print(a is b)  # False（不同对象）

c = a
print(a is c)  # True（同一个对象）

# 小整数缓存（CPython 实现细节，-5 到 256）
x = 256
y = 256
print(x is y)  # True（小整数被缓存复用）

x = 257
y = 257
print(x is y)  # False（大整数不缓存，可能是 True 也可能是 False，取决于实现）

# 正确用法：
# is None / is not None  ← 推荐用 is
# == 比较值              ← 推荐用 ==
# 永远不要用 is 比较整数/字符串的值！
```

---

### 7.2 数据结构面试题

#### 列表vs元组vs数组

| 特性 | list | tuple | array.array |
|------|------|-------|-------------|
| 可变性 | 可变 | 不可变 | 可变 |
| 元素类型 | 任意 | 任意 | 单一 C 类型 |
| 内存 | 大（PyObject 指针） | 中 | 小（原始 C 类型） |
| 方法 | 丰富（append/pop等） | 少（count/index） | 少 |
| 可哈希 | 否 | 是（元素可哈希时） | 否 |
| 适用场景 | 通用序列 | 固定数据、字典键 | 大量数值数据 |

```python
# 内存对比（100万元素）
import sys
import array

list_of_ints = list(range(1_000_000))
tuple_of_ints = tuple(range(1_000_000))
array_of_ints = array.array("i", range(1_000_000))

print(sys.getsizeof(list_of_ints))   # ~8MB（指针）+ 28MB（int对象）= 36MB
print(sys.getsizeof(tuple_of_ints))  # ~8MB（指针）+ 28MB（int对象）= 36MB
print(sys.getsizeof(array_of_ints))  # ~4MB（原始 int）
```

#### 字典底层实现

> 🔥 **面试高频考点**：字典的底层实现？为什么查找是 O(1)？哈希冲突怎么解决？

**CPython 字典底层是哈希表（开放寻址法）**：

```text
字典结构：
┌─────────────────────────────────────┐
│ 哈希表（连续数组）                    │
├──────┬──────┬──────┬──────┬─────────┤
│ 索引 │ hash │ key  │ value│ 状态    │
├──────┼──────┼──────┼──────┼─────────┤
│  0   │  ... │  ... │  ... │  占用   │
│  1   │  ... │  ... │  ... │  空闲   │
│  2   │  ... │  ... │  ... │  占用   │
│ ...  │  ... │  ... │  ... │  ...    │
└──────┴──────┴──────┴──────┴─────────┘
```

**查找过程：**
1. 计算 `hash(key)`
2. 用哈希值的低几位作为初始索引：`index = hash & mask`
3. 如果该位置空闲 → KeyError
4. 如果该位置的 key 相等 → 返回 value
5. 如果哈希冲突（位置被占但 key 不同）→ 用探测序列找下一个位置（开放寻址）
6. 重复 3-5 直到找到或遍历完

**Python 3.6+ 字典是有序的**（插入顺序），通过分离的 entries 数组和 indices 数组实现，更省内存。

**扩容机制**：当负载因子（已用/总数组大小）超过 2/3 时，字典会扩容为原来的 2 倍，重新哈希所有元素。

```python
# 字典的 O(1) 查找验证
d = {i: i*2 for i in range(1_000_000)}
import timeit
print(timeit.timeit(lambda: d[999999], number=100000))  # 恒定时间，与字典大小无关
```

#### 集合去重原理

集合（set）底层也是哈希表，和字典类似，只是只存储 key 不存储 value。

**去重原理**：
1. 插入元素时计算 `hash(element)`
2. 查找哈希表中是否已有相同哈希且相等的元素
3. 如果有 → 不插入（去重）
4. 如果没有 → 插入

**注意**：元素必须是可哈希的（不可变类型）。自定义类需要实现 `__hash__` 和 `__eq__`。

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __hash__(self):
        return hash((self.name, self.age))

    def __eq__(self, other):
        return self.name == other.name and self.age == other.age

people = {Person("Alice", 25), Person("Alice", 25), Person("Bob", 30)}
print(len(people))  # 2（两个 Alice 被去重）
```

#### LRU缓存实现

> 🔥 **面试高频考点**：手写 LRU 缓存

```python
from collections import OrderedDict

class LRUCache:
    """LRU（最近最少使用）缓存：用 OrderedDict 实现"""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return None
        # 移到末尾（最近使用）
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        # 超过容量，删除最久未使用的（头部）
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

# 双向链表 + 哈希表实现（更底层，面试常考）
class DLinkedNode:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key → node
        self.size = 0
        # 伪头和伪尾，简化边界处理
        self.head = DLinkedNode()
        self.tail = DLinkedNode()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _add_to_head(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _move_to_head(self, node):
        self._remove_node(node)
        self._add_to_head(node)

    def get(self, key):
        if key not in self.cache:
            return None
        node = self.cache[key]
        self._move_to_head(node)
        return node.value

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            node = DLinkedNode(key, value)
            self.cache[key] = node
            self._add_to_head(node)
            self.size += 1
            if self.size > self.capacity:
                removed = self.tail.prev
                self._remove_node(removed)
                del self.cache[removed.key]
                self.size -= 1
```

---

### 7.3 面向对象面试题

#### MRO与super

> 🔥 **面试高频考点**：MRO 是什么？super() 的工作原理？钻石继承问题？

**MRO（Method Resolution Order，方法解析顺序）** 决定了多继承时方法的查找顺序。Python 使用 C3 线性化算法。

```python
class A:
    def hello(self):
        print("A")

class B(A):
    def hello(self):
        print("B")
        super().hello()

class C(A):
    def hello(self):
        print("C")
        super().hello()

class D(B, C):
    def hello(self):
        print("D")
        super().hello()

print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)

D().hello()
# D → B → C → A
# super() 不是调用父类，而是调用 MRO 中的下一个类！
```

**super() 的本质**：`super()` 返回一个代理对象，它在 MRO 链中查找当前类的下一个类。不是简单的"父类"，在多继承中尤其重要。

```python
# super() 的完整形式
class B(A):
    def hello(self):
        super(B, self).hello()  # 显式指定：在 self 的 MRO 中找 B 的下一个
```

**钻石继承**：B 和 C 都继承 A，D 同时继承 B 和 C。由于 MRO 的存在，A 只会被调用一次（不会重复初始化）。

#### 魔术方法大全

| 分类 | 方法 | 触发时机 |
|------|------|---------|
| 创建/销毁 | `__new__`, `__init__`, `__del__` | 对象创建、初始化、销毁 |
| 字符串表示 | `__str__`, `__repr__`, `__format__`, `__bytes__` | str(), repr(), format(), bytes() |
| 比较 | `__eq__`, `__ne__`, `__lt__`, `__le__`, `__gt__`, `__ge__` | ==, !=, <, <=, >, >= |
| 算术 | `__add__`, `__sub__`, `__mul__`, `__truediv__` | +, -, *, / |
| 反向算术 | `__radd__`, `__rsub__` | 左操作数不支持时 |
| 增量赋值 | `__iadd__`, `__isub__` | +=, -= |
| 属性访问 | `__getattr__`, `__getattribute__`, `__setattr__`, `__delattr__` | 属性访问 |
| 描述符 | `__get__`, `__set__`, `__delete__`, `__set_name__` | 描述符协议 |
| 容器 | `__len__`, `__getitem__`, `__setitem__`, `__delitem__`, `__contains__` | len(), [], in |
| 迭代 | `__iter__`, `__next__`, `__reversed__` | iter(), next(), reversed() |
| 可调用 | `__call__` | 对象像函数一样调用 |
| 上下文 | `__enter__`, `__exit__` | with 语句 |
| 哈希 | `__hash__` | hash(), 作为字典键 |
| 布尔 | `__bool__` | bool(), if 语句 |

```python
# 实战：实现一个支持比较、算术、上下文的自定义类
@total_ordering
class Money:
    def __init__(self, amount: float, currency: str = "CNY"):
        self.amount = amount
        self.currency = currency

    def __repr__(self):
        return f"Money({self.amount}, {self.currency!r})"

    def __str__(self):
        return f"{self.amount:.2f} {self.currency}"

    def __eq__(self, other):
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other):
        return self.amount < other.amount

    def __add__(self, other):
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)

    def __bool__(self):
        return self.amount > 0
```

#### 元类的理解

> 🔥 **面试高频考点**：什么是元类？元类的应用场景？

**元类是创建类的类**。默认元类是 `type`。

```python
# 类也是对象，创建类的"东西"就是元类
class MyClass:
    pass

print(type(MyClass))  # <class 'type'>  ← MyClass 是 type 的实例
print(type(MyClass()))  # <class 'MyClass'>  ← 实例是 MyClass 的实例
```

**元类的执行流程**：`type(name, bases, namespace)` → `__new__` 创建类 → `__init__` 初始化类 → `__call__` 创建实例。

**应用场景**：ORM（自动注册字段）、单例、接口检查、API 框架（自动注册路由）、插件系统。

**替代方案**：`__init_subclass__`（Python 3.6+）更简单，大多数场景不需要元类。

> 🏆 **回答思路**：定义（类的类）→ 执行流程 → 与 `type` 的关系 → 应用场景 → 提到 `__init_subclass__` 替代方案 → 强调"99%的场景不需要元类"。

#### 描述符原理

> 🔥 **面试高频考点**：描述符是什么？property 的底层原理？

**描述符是实现了 `__get__`、`__set__`、`__delete__` 中至少一个方法的类**。

```python
# property 就是描述符
class MyProperty:
    """简化版 property 实现"""
    def __init__(self, fget=None, fset=None, fdel=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(instance)

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(instance, value)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel)

# 使用
class C:
    def __init__(self):
        self._x = 0

    @MyProperty
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
```

**数据描述符 vs 非数据描述符**：
- 数据描述符：同时有 `__get__` 和 `__set__`（如 property），优先级高于实例 `__dict__`
- 非数据描述符：只有 `__get__`（如方法），实例 `__dict__` 会覆盖它

#### __new__ vs __init__

```python
# __new__：创建对象（静态方法，返回实例）
# __init__：初始化对象（实例方法，不返回值）

class MyClass:
    def __new__(cls, *args, **kwargs):
        print("__new__ called")
        instance = super().__new__(cls)  # 创建对象
        return instance  # 必须返回实例

    def __init__(self, value):
        print("__init__ called")
        self.value = value  # 初始化属性

obj = MyClass(42)
# 输出：
# __new__ called
# __init__ called

# __new__ 的应用：不可变类的自定义（如 int、str 的子类）
class PositiveInt(int):
    def __new__(cls, value):
        if value < 0:
            raise ValueError("Must be positive")
        return super().__new__(cls, value)
    # __init__ 不能修改不可变对象，所以在 __new__ 中验证

# __new__ 的应用：单例
class Singleton:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

---

### 7.4 并发面试题

#### 进程线程协程区别

| 维度 | 进程 | 线程 | 协程 |
|------|------|------|------|
| 资源 | 独立地址空间 | 共享进程地址空间 | 用户态，共享线程 |
| 切换开销 | 大（内核态） | 中（内核态） | 小（用户态） |
| 并行 | 多核并行 | 受 GIL 限制 | 单线程并发 |
| 通信 | IPC（管道/队列/共享内存） | 共享内存（需锁） | 直接共享变量 |
| 稳定性 | 高（独立崩溃） | 低（一个崩溃影响全部） | 低 |
| 适用 | CPU 密集、隔离要求高 | I/O 密集、共享数据 | 高并发 I/O |
| Python 模块 | multiprocessing | threading | asyncio |

#### 线程安全与锁

```python
import threading

# 线程不安全的计数器
counter = 0
def increment():
    global counter
    for _ in range(100000):
        counter += 1  # 不是原子操作！读-改-写三步

threads = [threading.Thread(target=increment) for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)  # 不是 1000000！有竞态条件

# 线程安全：加锁
counter = 0
lock = threading.Lock()
def increment():
    global counter
    for _ in range(100000):
        with lock:  # 自动获取和释放
            counter += 1

# 锁的类型：
# threading.Lock()       → 互斥锁（不能重复获取，会死锁）
# threading.RLock()      → 可重入锁（同一线程可重复获取）
# threading.Semaphore(n) → 信号量（允许 n 个线程同时访问）
# threading.Event()      → 事件（线程间通信）
# threading.Condition()  → 条件变量（生产者消费者）
```

#### asyncio原理

> 🔥 **面试高频考点**：asyncio 的原理？事件循环？协程如何切换？

**asyncio 核心概念**：
- **协程（coroutine）**：用 `async def` 定义的函数，调用返回协程对象，不立即执行
- **事件循环（event loop）**：调度协程执行的核心循环
- **任务（Task）**：协程的包装，加入事件循环调度
- **await**：挂起当前协程，让出控制权给事件循环

```python
import asyncio

async def fetch_data(url):
    print(f"Start fetching {url}")
    await asyncio.sleep(1)  # 模拟 I/O，挂起协程
    print(f"Finished {url}")
    return f"data from {url}"

async def main():
    # 顺序执行（慢）
    r1 = await fetch_data("url1")
    r2 = await fetch_data("url2")

    # 并发执行（快）
    task1 = asyncio.create_task(fetch_data("url1"))
    task2 = asyncio.create_task(fetch_data("url2"))
    r1, r2 = await asyncio.gather(task1, task2)

asyncio.run(main())
```

**协程切换时机**：只有在 `await` 处才会切换。如果协程中有 CPU 密集的同步代码（如 `time.sleep`），会阻塞整个事件循环。

#### 并发场景选择

```text
任务类型？
├── CPU 密集（计算、加密、图像处理）
│   └── multiprocessing / ProcessPoolExecutor
├── I/O 密集（网络、数据库、文件）
│   ├── 少量并发（<100）
│   │   └── threading / ThreadPoolExecutor
│   └── 大量并发（>1000）
│       └── asyncio（需要异步库支持）
└── 混合
    └── 分析瓶颈，I/O 用 asyncio，CPU 用进程池
```

#### 死锁排查

```python
# 死锁的四个必要条件（Coffman 条件）：
# 1. 互斥：资源不能共享
# 2. 持有并等待：持有资源同时等待其他资源
# 3. 不可剥夺：资源不能被强制收回
# 4. 循环等待：A等B，B等A

# 典型死锁
lock_a = threading.Lock()
lock_b = threading.Lock()

def thread1():
    with lock_a:
        time.sleep(0.1)
        with lock_b:  # 等待 lock_b
            pass

def thread2():
    with lock_b:
        time.sleep(0.1)
        with lock_a:  # 等待 lock_a → 死锁！
            pass

# 预防死锁：
# 1. 固定加锁顺序（所有线程先 a 后 b）
# 2. 超时获取（lock.acquire(timeout=1)）
# 3. 用 RLock 避免同一线程重复获取死锁
# 4. 减少锁的使用（用队列代替共享状态）

# 排查工具：
# py-spy dump --pid <pid>  → 查看所有线程的调用栈
# faulthandler.dump_traceback_later()  → 定时打印线程栈
```

---

### 7.5 内存与性能面试题

#### 垃圾回收机制

> 🔥 **面试高频考点**：Python 垃圾回收机制？引用计数？分代回收？

**Python 垃圾回收 = 引用计数（主） + 分代回收（辅）**

**引用计数**：
- 每个对象维护 `ob_refcnt` 计数
- 引用增加时 `+1`（赋值、传参、存入容器）
- 引用减少时 `-1`（离开作用域、del、从容器移除）
- 计数为 0 时立即回收
- 优点：实时回收、简单
- 缺点：循环引用无法回收、计数更新有开销

```python
import sys
a = [1, 2, 3]
print(sys.getrefcount(a))  # 2（a + getrefcount 的临时引用）
b = a
print(sys.getrefcount(a))  # 3
del b
print(sys.getrefcount(a))  # 2
```

**分代回收**：
- 解决循环引用问题
- 对象分为 3 代（0代、1代、2代）
- 新对象在 0 代，存活越久代数越高
- 0 代回收最频繁，2 代最少（弱分代假说：多数对象朝生夕死）
- 回收时检测循环引用：从根对象出发，不可达的循环引用对象被回收

```python
import gc
gc.get_threshold()  # (700, 10, 10) → 各代回收阈值
gc.collect()        # 手动触发全量回收
gc.set_debug(gc.DEBUG_LEAK)  # 调试内存泄漏
```

#### 内存泄漏排查

```python
# 常见内存泄漏原因：
# 1. 全局容器（list/dict）不断增长不清理
# 2. 循环引用且对象有 __del__ 方法（无法被回收）
# 3. 闭包引用了大对象
# 4. C 扩展的内存泄漏（Python GC 管不到）
# 5. 未关闭的文件/连接

# 排查工具：
# tracemalloc（标准库）
import tracemalloc
tracemalloc.start()
# ... 运行代码 ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")
for stat in top_stats[:10]:
    print(stat)  # 显示分配内存最多的代码行

# objgraph（第三方）
# pip install objgraph
import objgraph
objgraph.show_most_common_types(limit=10)  # 显示实例最多的类型
objgraph.show_growth()  # 显示增长的对象类型

# memory_profiler（逐行内存分析）
# pip install memory_profiler
# python -m memory_profiler script.py
```

#### 性能优化思路

> 🏆 **老手回答框架**：
> 1. **测量**：用 cProfile/py-spy 找到瓶颈，不要靠猜
> 2. **算法**：O(n²) → O(n log n)，数量级提升最有效
> 3. **数据结构**：list 查找 → set/dict，O(n) → O(1)
> 4. **I/O**：同步 → 异步/批量，减少等待
> 5. **语言层面**：内置函数、生成器、`__slots__`
> 6. **C 扩展**：Numba/Cython，最后手段
> 7. **架构**：缓存、CDN、负载均衡

#### 大文件处理

```python
# 核心原则：流式处理，不要一次性读入内存

# 文本文件：逐行迭代
with open("large.txt", encoding="utf-8") as f:
    for line in f:  # 文件对象是迭代器，逐行读取
        process(line)

# 二进制文件：按块读取
with open("large.bin", "rb") as f:
    while chunk := f.read(1024*1024):  # 每次读 1MB
        process(chunk)

# CSV：csv 模块迭代器
import csv
with open("large.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        process(row)

# JSON：ijson 流式解析
import ijson
with open("large.json", "rb") as f:
    for item in ijson.items(f, "items.item"):
        process(item)

# Pandas：分块读取
import pandas as pd
for chunk in pd.read_csv("large.csv", chunksize=10000):
    process(chunk)
```

---

### 7.6 工程化面试题

#### 虚拟环境原理

```python
# 虚拟环境的本质：隔离的 Python 解释器 + 独立的 site-packages
# 原理：
# 1. 复制/链接系统 Python 解释器
# 2. 创建独立的 lib/pythonX.Y/site-packages
# 3. 修改 sys.path 优先使用虚拟环境的包
# 4. 激活脚本修改 PATH 和 VIRTUAL_ENV 环境变量

# 创建
python -m venv .venv

# 激活
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# 目录结构
.venv/
├── bin/ (Scripts on Windows)   # 可执行文件和激活脚本
│   ├── python
│   ├── pip
│   └── activate
├── include/                     # C 头文件
├── lib/
│   └── python3.11/
│       └── site-packages/       # 独立的包目录
└── pyvenv.cfg                   # 配置文件（指向系统 Python）

# 工具对比：
# venv（标准库）→ 轻量，适合简单项目
# virtualenv → venv 的前身，功能更多
# poetry → 依赖管理 + 虚拟环境
# conda → 数据科学常用，支持非 Python 依赖
# uv → 极速替代（Rust 写的）
```

#### 包管理机制

```python
# pip 安装流程：
# 1. 解析依赖（依赖解析器）
# 2. 下载 wheel/sdist 到缓存
# 3. 如果是 sdist，构建 wheel
# 4. 安装到 site-packages
# 5. 记录到 RECORD 文件

# pyproject.toml（现代 Python 项目配置标准，PEP 621）
# [project]
# name = "myproject"
# version = "0.1.0"
# dependencies = [
#     "requests>=2.28.0",
#     "pydantic>=2.0",
# ]
#
# [project.optional-dependencies]
# dev = ["pytest", "ruff", "mypy"]

# 依赖锁定：
# requirements.txt（pip）→ pip freeze > requirements.txt
# poetry.lock（poetry）→ 自动生成
# uv.lock（uv）→ 自动生成
# Pipfile.lock（pipenv）→ 自动生成
```

#### 项目结构设计

> 🏆 **回答要点**：
> - src 布局（库项目）或扁平布局（简单应用）
> - 分层架构：API 层 → 业务层 → 数据层
> - 配置与代码分离（环境变量、.env）
> - 测试目录与源码平级
> - 统一入口（pyproject.toml）
> - 关注点分离：models、services、api、utils 各自独立

#### 测试策略

> 🏆 **回答要点**：
> - 测试金字塔：大量单元测试 + 适量集成测试 + 少量 E2E 测试
> - 单元测试：纯逻辑，无外部依赖，快（毫秒级）
> - 集成测试：模块间交互，用测试数据库/容器
> - E2E 测试：模拟用户操作，慢但覆盖完整流程
> - Mock 用于隔离外部依赖，但不要过度 mock
> - 覆盖率目标：核心逻辑 80%+，不是追求 100%
> - CI 中自动运行，防止回归

---

### 本章总结

面试题的核心是**理解深度**，不是背诵：
- 语言基础题要讲清原理（GIL、装饰器、可变/不可变）
- 数据结构题要讲到底层（哈希表、开放寻址、LRU 实现）
- 面向对象题要讲清机制（MRO、描述符、元类）
- 并发题要能区分场景（进程/线程/协程的选择）
- 内存与性能题要有方法论（测量→算法→数据结构→语言层面）
- 工程化题要体现实战经验（项目结构、测试策略、CI/CD）

> 🏆 **老手经验**：面试时回答问题用"定义→原理→代码→场景→坑"的结构。先给结论，再展开细节，最后说实际应用中的注意事项。不要只背概念，要体现你真的用过、踩过坑、解决过问题。

### 思考题/实战练习

1. **GIL 深入**：写一个 CPU 密集型函数，分别用单线程、多线程、多进程运行，在 4 核机器上对比耗时，解释结果。
2. **LRU 实现**：不使用 `OrderedDict`，用双向链表 + 哈希表手写 LRU 缓存，支持 `get` 和 `put` 操作，时间复杂度 O(1)。
3. **MRO 分析**：设计一个复杂的多继承层次（至少 5 个类），手动计算 MRO，然后用 `Class.__mro__` 验证。
4. **死锁复现与排查**：写一个会产生死锁的程序，用 `py-spy dump` 查看线程栈定位死锁，然后修复。
5. **内存泄漏排查**：写一个有内存泄漏的程序（如全局列表不断增长），用 `tracemalloc` 定位泄漏位置并修复。

---


## 8. AI/数据科学Python高效用法

数据科学和 AI 是 Python 最重要的应用领域之一。但很多人用 NumPy/Pandas 的方式是"能用但慢"——用 Python 循环操作数组，用 `iterrows` 遍历 DataFrame。老手知道**向量化**和**批处理**才是这些库的正确打开方式，性能差距可达 100 倍以上。

> 📌 **本章定位**：本章聚焦**数据科学场景下的 Python 语言层面高效用法**——向量化思维、内存优化、管道设计、工程化实践。NumPy/Pandas/Scikit-learn 的完整 API 请参考官方文档，本章不重复罗列函数签名，而是讲透"怎么用才快、才对、才稳"。

### 8.1 NumPy高效操作

#### 向量化编程思想

```python
import numpy as np

# 反模式：Python 循环操作数组（慢）
def slow_add(arr1, arr2):
    result = np.empty_like(arr1)
    for i in range(len(arr1)):
        result[i] = arr1[i] + arr2[i]
    return result

# Pythonic：向量化操作（C 层执行，快 100 倍）
def fast_add(arr1, arr2):
    return arr1 + arr2  # 整个数组一次操作

# 基准测试（100万元素）
a = np.random.rand(1_000_000)
b = np.random.rand(1_000_000)
# slow_add: ~0.3s
# fast_add: ~0.003s (100x faster)

# 向量化条件操作
data = np.random.randn(1000)
# 反模式
result = np.where(data > 0, data, 0)  # 向量化：大于0保留，否则置0

# 向量化函数：np.vectorize（注意：只是语法糖，不会加速！）
# 真正的加速需要用 NumPy 内置函数或 numba
```

#### 广播机制

```python
# 广播：不同形状的数组进行运算时的自动扩展规则

# 规则1：维度右对齐，不足的补1
# (3, 4) + (4,) → (3, 4) + (1, 4) → (3, 4)
a = np.ones((3, 4))
b = np.arange(4)  # shape (4,)
c = a + b  # b 被广播为 (1, 4)，然后复制为 (3, 4)

# 规则2：维度为1的可以复制
# (3, 1) + (1, 4) → (3, 4)
a = np.arange(3).reshape(3, 1)  # [[0], [1], [2]]
b = np.arange(4).reshape(1, 4)  # [[0, 1, 2, 3]]
c = a + b  # 结果 (3, 4)，a 的列复制4次，b 的行复制3次

# 规则3：维度不匹配且都不为1 → 报错
# (3, 4) + (5,) → ValueError

# 实战：标准化（均值为0，方差为1）
data = np.random.rand(1000, 10)  # 1000个样本，10个特征
mean = data.mean(axis=0)  # shape (10,)
std = data.std(axis=0)    # shape (10,)
normalized = (data - mean) / std  # 广播：(1000,10) - (10,) → (1000,10)

# 实战：距离计算
points = np.random.rand(100, 2)  # 100个2D点
centroid = np.array([0.5, 0.5])  # shape (2,)
distances = np.sqrt(((points - centroid) ** 2).sum(axis=1))  # shape (100,)
```

#### 避免Python循环

```python
# 场景1：逐元素操作 → 用向量化运算
# 反模式
result = np.array([x * 2 + 1 for x in data])
# 好
result = data * 2 + 1

# 场景2：条件赋值 → 用 np.where / 布尔索引
# 反模式
for i in range(len(data)):
    if data[i] < 0:
        data[i] = 0
# 好
data[data < 0] = 0
# 或
data = np.where(data < 0, 0, data)

# 场景3：多条件 → 用 & | ~（注意加括号）
mask = (data > 0) & (data < 1)  # 0 < data < 1
filtered = data[mask]

# 场景4：累积操作 → 用 cumsum / cumprod
# 反模式
result = []
total = 0
for x in data:
    total += x
    result.append(total)
# 好
result = np.cumsum(data)

# 场景5：矩阵运算 → 用 @ 或 np.dot
# 反模式
result = np.zeros((a.shape[0], b.shape[1]))
for i in range(a.shape[0]):
    for j in range(b.shape[1]):
        for k in range(a.shape[1]):
            result[i, j] += a[i, k] * b[k, j]
# 好
result = a @ b  # 或 np.dot(a, b)
```

#### 内存布局（C顺序vs Fortran顺序）

```python
# C 顺序（行优先，默认）：内存中按行连续存储
# Fortran 顺序（列优先）：内存中按列连续存储

a = np.ones((1000, 1000), order="C")  # C 顺序
b = np.ones((1000, 1000), order="F")  # Fortran 顺序

# 按行求和：C 顺序快（内存连续）
# 按列求和：Fortran 顺序快
# 基准测试：
# a.sum(axis=1)（C顺序按行）: ~0.5ms
# a.sum(axis=0)（C顺序按列）: ~1.5ms（不连续，缓存不友好）
# b.sum(axis=0)（F顺序按列）: ~0.5ms

# 转置不复制数据，只是改变步长
c = a.T  # 视图，不是副本
c.flags["C_CONTIGUOUS"]  # False（转置后变成列优先）

# 需要连续内存时用 np.ascontiguousarray
d = np.ascontiguousarray(a.T)  # 复制为 C 顺序
```

#### 视图vs副本

```python
# 视图：共享数据，修改会影响原数组
# 副本：独立数据，修改不影响原数组

# 切片是视图
a = np.array([1, 2, 3, 4, 5])
b = a[1:4]  # 视图
b[0] = 99
print(a)  # [1, 99, 3, 4, 5] ← 原数组被修改！

# 布尔索引/花式索引是副本
c = a[a > 2]  # 副本
c[0] = 100
print(a)  # 不受影响

# 转置/重塑是视图（如果可能）
d = a.reshape(5, 1)  # 视图
e = a.T  # 视图

# 显式复制
f = a.copy()  # 副本

# 判断是否共享内存
np.shares_memory(a, b)  # True
np.shares_memory(a, c)  # False

# 实战：大数组操作时注意意外复制
# 坏：每次操作都创建副本
data = data[data > 0]  # 副本
data = data * 2        # 副本
data = data + 1        # 副本
# 好：原地操作
data *= 2  # 原地修改，不创建副本
data += 1
```

#### 常用性能技巧

```python
# 1. 预分配数组，避免动态增长
# 坏
result = np.array([])
for x in data:
    result = np.append(result, x * 2)  # 每次都重新分配内存

# 好
result = np.empty(len(data))
for i, x in enumerate(data):
    result[i] = x * 2

# 2. 用 out 参数避免分配
np.multiply(a, b, out=c)  # 结果写入 c，不分配新数组
np.add(a, b, out=c)

# 3. 用 np.einsum 做复杂张量运算（比多次 transpose+dot 快）
# 矩阵乘法
c = np.einsum("ij,jk->ik", a, b)
# 批量矩阵乘法
c = np.einsum("bij,bjk->bik", a, b)

# 4. 用 np.bincount 做快速计数
values = np.random.randint(0, 100, 1000000)
counts = np.bincount(values)  # O(n)，比 Counter 快

# 5. 用 np.searchsorted 做二分查找
sorted_data = np.sort(np.random.rand(1000000))
indices = np.searchsorted(sorted_data, [0.3, 0.5, 0.7])  # O(log n)
```

---

### 8.2 Pandas最佳实践

#### 避免iterrows（用apply/向量化）

```python
import pandas as pd

df = pd.DataFrame({"a": range(100000), "b": range(100000, 200000)})

# 反模式：iterrows（最慢，每次创建 Series）
def slow_calculate(df):
    result = []
    for idx, row in df.iterrows():
        result.append(row["a"] * 2 + row["b"])
    return result
# ~3秒

# 稍好：apply（仍在 Python 层循环）
def medium_calculate(df):
    return df.apply(lambda row: row["a"] * 2 + row["b"], axis=1)
# ~1秒

# 最好：向量化（C 层执行）
def fast_calculate(df):
    return df["a"] * 2 + df["b"]
# ~0.002秒（1500倍加速！）

# 复杂逻辑：用 np.where / np.select
# 反模式
def slow_classify(df):
    result = []
    for _, row in df.iterrows():
        if row["a"] > 50000:
            result.append("high")
        elif row["a"] > 20000:
            result.append("medium")
        else:
            result.append("low")
    return result

# 好：np.select
conditions = [
    df["a"] > 50000,
    df["a"] > 20000,
]
choices = ["high", "medium"]
df["category"] = np.select(conditions, choices, default="low")

# 好：pd.cut（分箱）
df["category"] = pd.cut(
    df["a"],
    bins=[-float("inf"), 20000, 50000, float("inf")],
    labels=["low", "medium", "high"],
)
```

#### 分类数据节省内存

```python
# 低基数字符串列用 category 类型，大幅节省内存
df = pd.DataFrame({
    "city": np.random.choice(["Beijing", "Shanghai", "Guangzhou", "Shenzhen"], 1000000),
    "gender": np.random.choice(["M", "F"], 1000000),
    "status": np.random.choice(["active", "inactive", "pending"], 1000000),
})

# 转换前
print(df.memory_usage(deep=True).sum())  # ~180MB（字符串存储）

# 转换为 category
df["city"] = df["city"].astype("category")
df["gender"] = df["gender"].astype("category")
df["status"] = df["status"].astype("category")

print(df.memory_usage(deep=True).sum())  # ~3MB（60倍节省！）

# 自动转换低基数字符串列
def optimize_categories(df, threshold=0.5):
    """将基数低于阈值的字符串列转为 category"""
    for col in df.select_dtypes(include="object"):
        n_unique = df[col].nunique()
        if n_unique / len(df) < threshold:
            df[col] = df[col].astype("category")
    return df
```

#### 链式操作与方法链

```python
# Pandas 支持方法链，让数据处理流程清晰可读
result = (
    df
    .query("age >= 18 and age <= 65")           # 过滤
    .assign(income_level=lambda x: pd.cut(      # 新增列
        x["income"], bins=3, labels=["low", "mid", "high"]
    ))
    .groupby(["city", "income_level"])          # 分组
    .agg({"age": "mean", "income": ["sum", "count"]})  # 聚合
    .reset_index()                              # 重置索引
    .sort_values("income", ascending=False)     # 排序
    .head(10)                                   # 取前10
)

# 方法链的优势：
# 1. 每个步骤清晰，数据流向明确
# 2. 不需要中间变量
# 3. 易于注释和调试（注释掉某一步即可）

# 注意：方法链中用 lambda 引用当前 DataFrame
# .assign(new_col=lambda x: x["a"] + x["b"])
# x 就是链中当前的 DataFrame
```

#### 分组聚合优化

```python
# 反模式：逐组循环
def slow_groupby(df):
    result = {}
    for city, group in df.groupby("city"):
        result[city] = group["income"].mean()
    return result

# 好：内置聚合
result = df.groupby("city")["income"].mean()

# 多列聚合
result = df.groupby("city").agg({
    "income": ["mean", "sum", "count"],
    "age": ["min", "max", "mean"],
})

# 命名聚合（Pandas 0.25+）
result = df.groupby("city").agg(
    avg_income=("income", "mean"),
    total_income=("income", "sum"),
    avg_age=("age", "mean"),
    count=("id", "count"),
)

# 自定义聚合函数（慢，尽量用内置）
def custom_agg(group):
    return group["income"].max() - group["income"].min()
result = df.groupby("city").apply(custom_agg)  # 慢

# 更好：用内置函数组合
result = df.groupby("city")["income"].agg(lambda x: x.max() - x.min())
# 最好：向量化
g = df.groupby("city")["income"]
result = g.max() - g.min()

# 大数据量分组：用 observed=True 减少类别组合
df.groupby("city", observed=True)["income"].mean()
```

#### 大文件分块读取

```python
# read_csv 的 chunksize 参数
chunk_iter = pd.read_csv(
    "large_file.csv",
    chunksize=10000,  # 每次读 10000 行
    usecols=["id", "name", "value"],  # 只读需要的列
    dtype={"id": "int32", "value": "float32"},  # 指定类型省内存
    parse_dates=["timestamp"],
)

results = []
for chunk in chunk_iter:
    # 处理每个块
    chunk["processed"] = chunk["value"] * 2
    results.append(chunk[["id", "processed"]])

# 合并结果（如果内存够）
final = pd.concat(results, ignore_index=True)

# 或者：边处理边写入
for i, chunk in enumerate(chunk_iter):
    processed = process_chunk(chunk)
    processed.to_csv(
        "output.csv",
        mode="a" if i > 0 else "w",  # 第一块写，后续追加
        header=(i == 0),
        index=False,
    )

# Parquet 格式：比 CSV 快 10 倍，体积小 5 倍
# 读取
df = pd.read_parquet("data.parquet")
# 写入
df.to_parquet("data.parquet", engine="pyarrow", compression="snappy")
```

#### 数据类型优化

```python
# 数值类型降级：在不损失精度的前提下用更小的类型
def optimize_numeric_dtypes(df):
    """优化数值列的数据类型"""
    for col in df.select_dtypes(include=["int64"]):
        col_min, col_max = df[col].min(), df[col].max()
        if col_min >= 0:
            if col_max <= 255:
                df[col] = df[col].astype("uint8")
            elif col_max <= 65535:
                df[col] = df[col].astype("uint16")
            elif col_max <= 4294967295:
                df[col] = df[col].astype("uint32")
        else:
            if col_min >= -128 and col_max <= 127:
                df[col] = df[col].astype("int8")
            elif col_min >= -32768 and col_max <= 32767:
                df[col] = df[col].astype("int16")

    for col in df.select_dtypes(include=["float64"]):
        df[col] = df[col].astype("float32")  # 通常精度足够

    return df

# 优化前：100万行 x 10列 int64 → ~80MB
# 优化后：合适的类型 → ~10-20MB
```

---

### 8.3 机器学习工程实践

#### 数据管道（Pipeline）

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# 定义预处理管道
numeric_features = ["age", "income", "score"]
numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

categorical_features = ["city", "gender", "occupation"]
categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore")),
])

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ]
)

# 完整管道：预处理 + 模型
model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(n_estimators=100, random_state=42)),
])

# 训练（管道自动处理预处理，避免数据泄漏）
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model.fit(X_train, y_train)
print(f"Accuracy: {model.score(X_test, y_test):.3f}")

# 交叉验证（管道确保每折都独立预处理）
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
print(f"CV Accuracy: {scores.mean():.3f} ± {scores.std():.3f}")
```

#### 特征工程效率

```python
# 特征工程的向量化实现

# 1. 时间特征提取（向量化）
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.hour
df["dayofweek"] = df["timestamp"].dt.dayofweek
df["is_weekend"] = df["dayofweek"].isin([5, 6]).astype(int)
df["month"] = df["timestamp"].dt.month

# 2. 交叉特征（向量化）
df["income_per_age"] = df["income"] / (df["age"] + 1)  # +1 避免除零
df["score_x_income"] = df["score"] * df["income"]

# 3. 目标编码（Target Encoding，注意数据泄漏！）
# 用 K 折目标编码避免泄漏
from sklearn.model_selection import KFold

def target_encode(train, test, col, target, n_splits=5):
    """K 折目标编码"""
    encoder = train.groupby(col)[target].mean()
    global_mean = train[target].mean()

    train_encoded = pd.Series(global_mean, index=train.index)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    for train_idx, val_idx in kf.split(train):
        fold_mean = train.iloc[train_idx].groupby(col)[target].mean()
        train_encoded.iloc[val_idx] = train[col].iloc[val_idx].map(fold_mean).fillna(global_mean)

    test_encoded = test[col].map(encoder).fillna(global_mean)
    return train_encoded, test_encoded

# 4. 特征选择
from sklearn.feature_selection import SelectFromModel
selector = SelectFromModel(RandomForestClassifier(n_estimators=100))
X_selected = selector.fit_transform(X, y)
selected_features = X.columns[selector.get_support()]
```

#### 模型序列化

```python
import joblib
import pickle

# joblib：适合大型 NumPy 数组（sklearn 模型推荐）
# 保存
joblib.dump(model, "model.joblib", compress=3)
# 加载
model = joblib.load("model.joblib")

# pickle：通用 Python 对象序列化
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# ONNX：跨平台、跨语言的模型格式（推理优化）
# pip install skl2onnx onnxruntime
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

initial_type = [("float_input", FloatTensorType([None, X.shape[1]]))]
onnx_model = convert_sklearn(model, initial_types=initial_type)

with open("model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())

# ONNX 推理
import onnxruntime as ort
session = ort.InferenceSession("model.onnx")
input_name = session.get_inputs()[0].name
predictions = session.run(None, {input_name: X_test.values.astype(np.float32)})
```

#### 推理优化

```python
# 1. 批量推理（Batch Inference）
def batch_predict(model, data, batch_size=1000):
    """批量推理，减少开销"""
    predictions = []
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        predictions.extend(model.predict(batch))
    return np.array(predictions)

# 2. ONNX Runtime（比 sklearn 快 2-10 倍）
import onnxruntime as ort

# 选择最优执行提供者
options = ort.SessionOptions()
options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
session = ort.InferenceSession(
    "model.onnx",
    sess_options=options,
    providers=["CPUExecutionProvider"],  # 或 "CUDAExecutionProvider"
)

# 3. TensorRT（NVIDIA GPU，极致性能）
# 需要 TensorRT 环境，将 ONNX 模型转为 TensorRT 引擎

# 4. 模型量化（减少模型大小，加速推理）
# 动态量化：权重从 float32 → int8
from sklearn.ensemble import RandomForestClassifier
# ONNX 量化
from onnxruntime.quantization import quantize_dynamic, QuantType
quantize_dynamic("model.onnx", "model_quantized.onnx", weight_type=QuantType.QInt8)
# 模型大小减少 75%，推理速度提升 2-3 倍，精度损失极小
```

#### 批量推理

```python
# 生产环境批量推理服务
from concurrent.futures import ThreadPoolExecutor
import queue
import threading

class BatchInferenceService:
    """批量推理服务：攒批处理，提高吞吐量"""
    def __init__(self, model, max_batch_size=32, max_wait_time=0.01):
        self.model = model
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.queue = queue.Queue()
        self.results = {}
        self.worker = threading.Thread(target=self._worker, daemon=True)
        self.worker.start()

    def predict(self, data):
        """提交单个请求，等待结果"""
        request_id = id(data)
        event = threading.Event()
        self.queue.put((request_id, data, event))
        event.wait(timeout=10)
        return self.results.pop(request_id, None)

    def _worker(self):
        while True:
            batch = []
            # 攒批：最多等 max_wait_time 或攒满 max_batch_size
            deadline = time.time() + self.max_wait_time
            while len(batch) < self.max_batch_size and time.time() < deadline:
                try:
                    remaining = deadline - time.time()
                    item = self.queue.get(timeout=max(0, remaining))
                    batch.append(item)
                except queue.Empty:
                    break

            if not batch:
                continue

            # 批量推理
            data_batch = np.array([item[1] for item in batch])
            predictions = self.model.predict(data_batch)

            # 返回结果
            for (request_id, _, event), pred in zip(batch, predictions):
                self.results[request_id] = pred
                event.set()
```

---

### 8.4 数据处理管道设计

#### 生成器管道

```python
# 生成器管道：内存恒定，适合大数据流

def read_csv(filepath):
    """读取 CSV，逐行产出字典"""
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        yield from reader

def filter_valid(records):
    """过滤无效记录"""
    for record in records:
        if record.get("email") and "@" in record["email"]:
            yield record

def transform(records):
    """转换字段"""
    for record in records:
        record["name"] = record["name"].strip().title()
        record["age"] = int(record["age"]) if record["age"] else None
        yield record

def deduplicate(records, key="email"):
    """去重（需要内存存储已见的 key）"""
    seen = set()
    for record in records:
        if record[key] not in seen:
            seen.add(record[key])
            yield record

def write_output(records, output_path):
    """写入输出"""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "email", "age"])
        writer.writeheader()
        writer.writerows(records)

# 组合管道：整个流程内存恒定
pipeline = deduplicate(transform(filter_valid(read_csv("input.csv"))))
write_output(pipeline, "output.csv")
```

#### Dask并行处理

```python
# Dask：并行处理超出内存的大数据
# 安装：pip install dask[dataframe]

import dask.dataframe as dd

# 读取大文件（自动分块）
ddf = dd.read_csv(
    "large_file_*.csv",  # 支持通配符
    blocksize="64MB",   # 每个分块大小
    dtype={"id": "int32", "value": "float32"},
)

# 操作和 Pandas 几乎一样，但延迟执行
result = (
    ddf
    .query("value > 0")
    .groupby("category")
    .agg({"value": ["mean", "sum", "count"]})
    .compute()  # 触发实际计算
)

# Dask 的优势：
# 1. 处理超出内存的数据（分块加载）
# 2. 自动并行（多核/多机）
# 3. API 和 Pandas 一致，学习成本低
# 4. 支持分布式集群

# Dask Array：并行 NumPy
import dask.array as da
x = da.random.random((10000, 10000), chunks=(1000, 1000))
result = (x + x.T).mean(axis=0).compute()
```

#### 数据流设计模式

```python
# 1. 扇出-扇入（Fan-out/Fan-in）
# 一个数据源 → 多个处理节点 → 合并结果
def fan_out_fan_in(data, processors, merger):
    results = [processor(data) for processor in processors]
    return merger(results)

# 2. 管道-过滤器（Pipe-and-Filter）
# 数据经过一系列过滤器，每个过滤器独立处理
class Pipeline:
    def __init__(self):
        self.filters = []

    def add_filter(self, filter_func):
        self.filters.append(filter_func)
        return self

    def execute(self, data):
        for f in self.filters:
            data = f(data)
        return data

pipeline = Pipeline()
pipeline.add_filter(validate).add_filter(transform).add_filter(load)
result = pipeline.execute(raw_data)

# 3. 发布-订阅（Pub/Sub）
# 数据源发布事件，多个订阅者处理
class DataStream:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def publish(self, data):
        for subscriber in self.subscribers:
            subscriber(data)
```

#### 错误处理与重试

```python
# 数据管道中的错误处理

from dataclasses import dataclass, field
from typing import Callable, Any
import time

@dataclass
class ProcessingResult:
    success: list = field(default_factory=list)
    failed: list = field(default_factory=list)
    errors: list = field(default_factory=list)

def process_with_retry(
    records: list,
    processor: Callable,
    max_retries: int = 3,
    delay: float = 1.0,
) -> ProcessingResult:
    """带重试和错误隔离的批处理"""
    result = ProcessingResult()

    for record in records:
        for attempt in range(max_retries):
            try:
                processed = processor(record)
                result.success.append(processed)
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    result.failed.append(record)
                    result.errors.append({"record": record, "error": str(e)})
                else:
                    time.sleep(delay * (2 ** attempt))  # 指数退避

    return result

# 死信队列（Dead Letter Queue）：失败的记录单独存储
def save_dead_letters(failed_records, filepath="dead_letters.json"):
    with open(filepath, "a") as f:
        for record in failed_records:
            f.write(json.dumps(record) + "\n")

# 监控：处理进度和速率
from tqdm import tqdm
for record in tqdm(records, desc="Processing", unit="records"):
    process(record)
```

---

### 8.5 Jupyter高效用法

#### 魔法命令

```python
# %timeit：测量单行代码执行时间
%timeit sum(range(1000000))

# %%timeit：测量整个单元格
%%timeit
total = 0
for i in range(1000000):
    total += i

# %time：单次执行时间（含系统时间）
%time slow_function()

# %prun：代码分析（cProfile）
%prun -s cumulative expensive_function()

# %lprun：行级分析（需要 line_profiler）
%load_ext line_profiler
%lprun -f function_name function_name()

# %memit：内存使用（需要 memory_profiler）
%load_ext memory_profiler
%memit big_list = list(range(1000000))

# %mprun：行级内存分析
%mprun -f function_name function_name()

# %run：运行外部脚本
%run script.py

# %load：加载外部文件到单元格
%load utils.py

# %who：列出当前变量
%who
%who list  # 只列出 list 类型

# %reset：清除所有变量
%reset -f

# %%bash：运行 bash 命令
%%bash
ls -la
head -5 data.csv

# %%writefile：将单元格内容写入文件
%%writefile utils.py
def helper():
    return "hello"

# %env：查看/设置环境变量
%env
%env MY_VAR=value
```

#### 性能分析

```python
# 在 Jupyter 中做性能分析的完整流程

# 1. 先用 %timeit 确认是否有性能问题
%timeit process_data(df)

# 2. 用 %prun 找到耗时函数
%prun -s cumulative process_data(df)

# 3. 用 %lprun 找到耗时的行
%load_ext line_profiler
%lprun -f process_data process_data(df)

# 4. 优化后重新测量
%timeit process_data_optimized(df)

# 5. 内存分析
%load_ext memory_profiler
%memit process_data(df)
%mprun -f process_data process_data(df)

# 6. 对比优化前后
import timeit
setup = "from __main__ import process_data, process_data_optimized, df"
original = timeit.timeit("process_data(df)", setup=setup, number=10)
optimized = timeit.timeit("process_data_optimized(df)", setup=setup, number=10)
print(f"Speedup: {original/optimized:.1f}x")
```

#### 并行计算

```python
# Jupyter 中的并行计算

# 1. IPython parallel（ipyparallel）
# pip install ipyparallel
import ipyparallel as ipp
client = ipp.Client()
view = client[:]  # 使用所有引擎

@view.parallel(block=True)
def parallel_square(x):
    return x ** 2

results = parallel_square.map(range(1000))

# 2. multiprocessing（标准库）
from multiprocessing import Pool
with Pool(4) as pool:
    results = pool.map(expensive_function, data)

# 3. Dask（大数据）
import dask.dataframe as dd
ddf = dd.from_pandas(df, npartitions=8)
result = ddf.groupby("key").value.mean().compute()

# 4. %%px：在所有引擎上执行
%%px
import numpy as np  # 在所有并行引擎上导入
```

#### 最佳实践与反模式

```python
# ✅ 最佳实践

# 1. 单元格职责单一
# In [1]: 导入和配置
# In [2]: 数据加载
# In [3]: 数据清洗
# In [4]: 探索性分析
# In [5]: 可视化
# In [6]: 建模

# 2. 用函数封装可复用逻辑
def clean_data(df):
    """数据清洗函数"""
    df = df.dropna()
    df = df[df["value"] > 0]
    return df

# 3. 用参数化单元格（papermill）
# pip install papermill
# 在单元格顶部添加标签 "parameters"
input_file = "data.csv"  # 参数
output_file = "result.csv"

# 4. 版本控制：用 jupytext 把 notebook 存为 .py
# pip install jupytext
# jupytext --set-formats ipynb,py notebook.ipynb

# ❌ 反模式

# 1. 隐藏状态：依赖之前单元格的变量，但不重新运行
# 解决：定期 "Restart & Run All" 验证可复现

# 2. 单元格执行顺序混乱
# 解决：保持线性执行，不要跳着跑

# 3. 在 notebook 中写生产代码
# 解决：notebook 用于探索，成熟代码移到 .py 模块

# 4. 输出过多导致 notebook 巨大
# 解决：用 ; 抑制输出，用 head() 限制行数

# 5. 硬编码路径
# 解决：用参数或环境变量
data_path = os.environ.get("DATA_PATH", "default.csv")
```

---

### 本章总结

数据科学和 AI 领域的 Python 高效用法核心是**向量化和批处理**：
- NumPy：避免 Python 循环，用向量化运算和广播，注意视图/副本和内存布局
- Pandas：避免 `iterrows`，用向量化和 `np.select`，用 category 省内存，用方法链组织流程
- 机器学习：用 Pipeline 避免数据泄漏，用 ONNX/量化优化推理，批量推理提高吞吐
- 数据管道：生成器管道内存恒定，Dask 处理超大数据，错误隔离和重试是生产必备
- Jupyter：魔法命令做性能分析，保持单元格职责单一，定期验证可复现

> 🏆 **老手经验**：数据科学代码的性能瓶颈 90% 在 Python 循环。看到 `for` 循环操作数组/DataFrame，第一反应就是"能不能向量化"。向量化不仅是快，更是简洁——一行向量化代码比十行循环更易读、更不易错。

### 思考题/实战练习

1. **NumPy 向量化**：用纯 Python 循环实现一个矩阵乘法，然后用 NumPy 向量化重写，对比 1000x1000 矩阵的性能差异。
2. **Pandas 优化**：给一个 100 万行的 DataFrame 添加一个复杂的分类列（3 个以上条件），分别用 `iterrows`、`apply`、`np.select` 实现，对比耗时。
3. **内存优化**：读取一个 1GB 的 CSV 文件，通过指定 dtype、category 类型、只读需要的列，将内存占用降到最低，记录优化前后的内存对比。
4. **ML Pipeline**：用 sklearn Pipeline 构建一个完整的分类模型，包含数值/类别特征的不同预处理，用交叉验证评估，确保没有数据泄漏。
5. **生成器管道**：实现一个处理 10GB 日志文件的管道，包含读取、过滤、转换、聚合，全程内存不超过 100MB。

---


## 9. 综合实战项目

前八章讲了各种知识点和技巧，本章将它们整合到三个真实的实战项目中：高性能 Web API、数据处理 ETL 管道、命令行工具。每个项目都体现老手的工程思维——架构设计、性能优化、错误处理、可维护性。最后给出老手成长路线图。

### 9.1 项目一：高性能Web API

#### FastAPI框架

```python
# main.py — 高性能异步 Web API
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import aioredis
import asyncpg

from .config import settings
from .routes import items, users, auth

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """应用生命周期：启动时初始化资源，关闭时清理"""
    # 启动：创建数据库连接池和 Redis 连接
    app.state.db = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=5,
        max_size=20,
    )
    app.state.redis = aioredis.from_url(
        settings.redis_url,
        max_connections=20,
    )
    yield
    # 关闭：释放资源
    await app.state.db.close()
    await app.state.redis.close()

app = FastAPI(
    title="High Performance API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(items.router, prefix="/api/items", tags=["items"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "version": "1.0.0"}
```

#### 异步处理

```python
# routes/items.py — 异步路由
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import json

router = APIRouter()

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None

class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    description: Optional[str] = Field(default=None, max_length=500)

async def get_db():
    """依赖注入：获取数据库连接池"""
    from main import app
    return app.state.db

async def get_redis():
    from main import app
    return app.state.redis

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    db=Depends(get_db),
    redis=Depends(get_redis),
):
    """获取商品：先查缓存，未命中查数据库，回写缓存"""
    # 1. 查 Redis 缓存
    cache_key = f"item:{item_id}"
    cached = await redis.get(cache_key)
    if cached:
        return ItemResponse(**json.loads(cached))

    # 2. 查数据库
    row = await db.fetchrow(
        "SELECT id, name, price, description FROM items WHERE id = $1",
        item_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")

    # 3. 回写缓存（TTL 5分钟）
    item = ItemResponse(**dict(row))
    await redis.setex(cache_key, 300, item.model_dump_json())
    return item

@router.post("", response_model=ItemResponse, status_code=201)
async def create_item(
    item: ItemCreate,
    db=Depends(get_db),
    redis=Depends(get_redis),
):
    """创建商品：写数据库，失效相关缓存"""
    row = await db.fetchrow(
        "INSERT INTO items (name, price, description) VALUES ($1, $2, $3) RETURNING *",
        item.name, item.price, item.description,
    )
    # 失效列表缓存
    await redis.delete("items:list")
    return ItemResponse(**dict(row))
```

#### 缓存策略

```python
# services/cache.py — 缓存服务
from functools import wraps
import json
import time

class CacheService:
    """缓存服务：支持 TTL、缓存穿透防护、缓存雪崩防护"""
    def __init__(self, redis, default_ttl=300):
        self.redis = redis
        self.default_ttl = default_ttl

    async def get_or_set(self, key: str, fetch_func, ttl=None):
        """缓存旁路模式（Cache-Aside）"""
        ttl = ttl or self.default_ttl
        cached = await self.redis.get(key)
        if cached is not None:
            return json.loads(cached)

        # 缓存未命中：获取数据
        data = await fetch_func()
        if data is not None:
            # 缓存雪崩防护：TTL 加随机偏移
            actual_ttl = ttl + hash(key) % 60
            await self.redis.setex(key, actual_ttl, json.dumps(data))
        return data

    async def invalidate(self, *keys):
        """失效缓存"""
        if keys:
            await self.redis.delete(*keys)

    async def invalidate_pattern(self, pattern: str):
        """按模式失效缓存"""
        keys = []
        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await self.redis.delete(*keys)

# 缓存装饰器
def cached(key_prefix: str, ttl: int = 300):
    """函数结果缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            cache_key = f"{key_prefix}:{':'.join(map(str, args))}"
            cache_service = self.cache
            return await cache_service.get_or_set(
                cache_key,
                lambda: func(self, *args, **kwargs),
                ttl=ttl,
            )
        return wrapper
    return decorator
```

#### 连接池

```python
# db/database.py — 数据库连接池管理
import asyncpg
from contextlib import asynccontextmanager

class DatabasePool:
    """数据库连接池封装"""
    def __init__(self, dsn: str, min_size: int = 5, max_size: int = 20):
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self._pool = None

    async def connect(self):
        self._pool = await asyncpg.create_pool(
            dsn=self.dsn,
            min_size=self.min_size,
            max_size=self.max_size,
            command_timeout=30,  # 查询超时
        )

    async def close(self):
        if self._pool:
            await self._pool.close()

    @asynccontextmanager
    async def transaction(self):
        """事务上下文管理器"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                yield conn

    async def execute(self, query: str, *args):
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetch(self, query: str, *args):
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)
```

#### 完整架构

```text
high-performance-api/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI 应用入口
│       ├── config.py            # 配置管理（pydantic-settings）
│       ├── routes/              # 路由层
│       │   ├── __init__.py
│       │   ├── items.py
│       │   ├── users.py
│       │   └── auth.py
│       ├── services/            # 业务逻辑层
│       │   ├── __init__.py
│       │   ├── item_service.py
│       │   ├── cache.py
│       │   └── auth_service.py
│       ├── db/                  # 数据访问层
│       │   ├── __init__.py
│       │   ├── database.py
│       │   └── repositories.py
│       ├── models/              # Pydantic 模型
│       │   ├── __init__.py
│       │   ├── item.py
│       │   └── user.py
│       └── middleware/          # 中间件
│           ├── __init__.py
│           ├── logging.py
│           └── rate_limit.py
├── tests/
├── migrations/                  # 数据库迁移
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

```dockerfile
# Dockerfile — 多阶段构建，优化镜像大小
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user .

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src/ .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Nginx反向代理与负载均衡

生产环境中，uvicorn/gunicorn 不直接暴露给公网，前面必须有 Nginx 做反向代理——处理 TLS 终止、静态文件、负载均衡、连接缓冲。

```nginx
# /etc/nginx/conf.d/app.conf — 生产级 Nginx 配置
# 上游服务：多个 uvicorn worker 实例
upstream python_app {
    least_conn;                       # 最少连接负载均衡
    server app:8000 max_fails=3 fail_timeout=30s;
    server app2:8000 max_fails=3 fail_timeout=30s backup;  # 备用节点
    keepalive 32;                     # 保持长连接，减少握手开销
}

# HTTP → HTTPS 重定向
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$host$request_uri;
}

# HTTPS 主配置
server {
    listen 443 ssl http2;
    server_name api.example.com;

    # TLS 证书（Let's Encrypt）
    ssl_certificate     /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache   shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全响应头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # 客户端请求体大小限制
    client_max_body_size 10m;

    # 静态文件（Nginx 直接服务，不经过 Python）
    location /static/ {
        alias /app/static/;
        expires 30d;                    # 静态资源缓存30天
        add_header Cache-Control "public, immutable";
    }

    # 健康检查（不记录日志）
    location = /health {
        proxy_pass http://python_app;
        access_log off;
    }

    # 反向代理到 Python 应用
    location / {
        proxy_pass http://python_app;
        proxy_http_version 1.1;

        # 传递真实客户端信息
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持（如果需要）
        proxy_set_header Upgrade    $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时配置
        proxy_connect_timeout 5s;
        proxy_send_timeout    30s;
        proxy_read_timeout    30s;

        # 缓冲（Nginx 先收完响应再发给客户端，保护后端）
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # 限流：防止暴力攻击
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    location /api/auth/login {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://python_app;
    }
}
```

> 🏆 **老手经验**：Nginx 和 uvicorn 的分工要明确——Nginx 负责 TLS、静态文件、限流、负载均衡、连接缓冲；uvicorn 只负责业务逻辑。不要让 Python 处理静态文件或 TLS，那是 C 语言的 Nginx 擅长的事。

#### Docker Compose 完整编排

```yaml
# docker-compose.yml — 生产级完整编排
version: "3.9"

services:
  # Nginx 反向代理
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_volume:/app/static:ro
    depends_on:
      - app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  # Python Web 应用（uvicorn）
  app:
    build:
      context: .
      dockerfile: Dockerfile
    expose:
      - "8000"
    environment:
      - DATABASE_URL=postgresql://app_user:app_pass@postgres:5432/appdb
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=production
    volumes:
      - static_volume:/app/static
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      replicas: 2          # 运行2个实例，Nginx负载均衡
      resources:
        limits:
          cpus: "2"
          memory: 1G

  # PostgreSQL 数据库
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: app_pass
      POSTGRES_DB: appdb
    volumes:
      - pg_data:/var/lib/postgresql/data
    expose:
      - "5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app_user -d appdb"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis 缓存/消息代理
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    expose:
      - "6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # Celery Worker（异步任务）
  celery_worker:
    build: .
    command: celery -A app.worker worker --loglevel=info --concurrency=4
    environment:
      - DATABASE_URL=postgresql://app_user:app_pass@postgres:5432/appdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  # Prometheus 指标采集
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    restart: unless-stopped

  # Grafana 可视化
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    restart: unless-stopped

volumes:
  pg_data:
  redis_data:
  static_volume:
  prometheus_data:
  grafana_data:
```

> 💡 **提示**：生产环境中 secrets（数据库密码、API key）不要硬编码在 docker-compose.yml 里，用 `.env` 文件（加入 `.gitignore`）或 Docker Secrets / Vault 管理。上面的配置仅为示例。

---

### 9.2 项目二：数据处理ETL管道

#### 数据抽取/转换/加载

```python
# etl/pipeline.py — ETL 管道主流程
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generator
import logging
import time

logger = logging.getLogger(__name__)

@dataclass
class ETLPipeline:
    """ETL 管道：抽取 → 转换 → 加载"""
    extractor: "Extractor"
    transformer: "Transformer"
    loader: "Loader"
    batch_size: int = 1000
    stats: dict = field(default_factory=dict)

    def run(self) -> dict:
        """运行完整 ETL 流程"""
        start_time = time.perf_counter()
        records_processed = 0
        errors = 0

        try:
            # 抽取
            logger.info("Starting extraction...")
            raw_data = self.extractor.extract()

            # 转换 + 加载（流式批处理）
            batch = []
            for record in raw_data:
                try:
                    transformed = self.transformer.transform(record)
                    if transformed:
                        batch.append(transformed)
                        if len(batch) >= self.batch_size:
                            self.loader.load(batch)
                            records_processed += len(batch)
                            batch = []
                except Exception as e:
                    errors += 1
                    logger.error("Transform error: %s", e, exc_info=True)

            # 加载剩余数据
            if batch:
                self.loader.load(batch)
                records_processed += len(batch)

            elapsed = time.perf_counter() - start_time
            self.stats = {
                "records_processed": records_processed,
                "errors": errors,
                "elapsed_seconds": round(elapsed, 2),
                "records_per_second": round(records_processed / elapsed, 2) if elapsed > 0 else 0,
            }
            logger.info("ETL completed: %s", self.stats)
            return self.stats

        except Exception as e:
            logger.error("ETL pipeline failed: %s", e, exc_info=True)
            raise

class Extractor(ABC):
    @abstractmethod
    def extract(self) -> Generator[dict, None, None]: ...

class Transformer(ABC):
    @abstractmethod
    def transform(self, record: dict) -> dict | None: ...

class Loader(ABC):
    @abstractmethod
    def load(self, batch: list[dict]) -> None: ...
```

#### 增量处理

```python
# etl/extractors.py — 增量抽取
class DatabaseExtractor(Extractor):
    """数据库增量抽取：基于水位线（watermark）"""
    def __init__(self, db, table: str, watermark_column: str, state_store):
        self.db = db
        self.table = table
        self.watermark_column = watermark_column
        self.state_store = state_store

    def extract(self) -> Generator[dict, None, None]:
        # 读取上次处理的水位线
        last_watermark = self.state_store.get(f"watermark:{self.table}")
        logger.info("Extracting from %s since %s", self.table, last_watermark)

        query = f"""
            SELECT * FROM {self.table}
            WHERE {self.watermark_column} > $1
            ORDER BY {self.watermark_column}
        """
        current_watermark = last_watermark

        async for row in self.db.fetch(query, last_watermark):
            record = dict(row)
            current_watermark = record[self.watermark_column]
            yield record

        # 更新水位线
        self.state_store.set(f"watermark:{self.table}", current_watermark)
        logger.info("Watermark updated to %s", current_watermark)

class FileExtractor(Extractor):
    """文件抽取：支持大文件流式读取"""
    def __init__(self, filepath: str, format: str = "csv"):
        self.filepath = filepath
        self.format = format

    def extract(self) -> Generator[dict, None, None]:
        if self.format == "csv":
            import csv
            with open(self.filepath, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                yield from reader
        elif self.format == "jsonl":
            with open(self.filepath, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
```

#### 错误恢复

```python
# etl/error_handler.py — 错误处理与恢复
class ErrorHandler:
    """错误处理器：死信队列 + 重试 + 告警"""
    def __init__(self, dead_letter_path: str, max_retries: int = 3):
        self.dead_letter_path = dead_letter_path
        self.max_retries = max_retries
        self.failed_records = []

    def handle(self, record: dict, error: Exception, context: str) -> bool:
        """处理错误，返回是否可以重试"""
        retry_count = record.get("_retry_count", 0)

        if retry_count < self.max_retries and self._is_retryable(error):
            record["_retry_count"] = retry_count + 1
            logger.warning("Retry %d for record: %s", retry_count + 1, error)
            return True  # 可以重试

        # 超过重试次数，写入死信队列
        self._to_dead_letter(record, error, context)
        return False

    def _is_retryable(self, error: Exception) -> bool:
        """判断错误是否可重试"""
        retryable = (ConnectionError, TimeoutError, asyncpg.PostgresConnectionError)
        return isinstance(error, retryable)

    def _to_dead_letter(self, record: dict, error: Exception, context: str):
        """写入死信队列"""
        dead_record = {
            "record": record,
            "error": str(error),
            "error_type": type(error).__name__,
            "context": context,
            "timestamp": datetime.now().isoformat(),
        }
        self.failed_records.append(dead_record)

        with open(self.dead_letter_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(dead_record) + "\n")

    def get_failed_count(self) -> int:
        return len(self.failed_records)
```

#### 性能监控

```python
# etl/monitoring.py — 性能监控
import time
from collections import defaultdict

class ETLPipelineMonitor:
    """ETL 管道监控：各阶段耗时、吞吐量、错误率"""
    def __init__(self):
        self.timings = defaultdict(list)
        self.counters = defaultdict(int)
        self.start_time = None

    def start(self):
        self.start_time = time.perf_counter()

    def time_stage(self, stage: str):
        """阶段计时上下文管理器"""
        class Timer:
            def __enter__(inner):
                inner.start = time.perf_counter()
                return inner
            def __exit__(inner, *args):
                elapsed = time.perf_counter() - inner.start
                self.timings[stage].append(elapsed)
        return Timer()

    def increment(self, metric: str, value: int = 1):
        self.counters[metric] += value

    def report(self) -> dict:
        """生成监控报告"""
        total_time = time.perf_counter() - self.start_time if self.start_time else 0
        return {
            "total_time_seconds": round(total_time, 2),
            "stage_timings": {
                stage: {
                    "count": len(times),
                    "total": round(sum(times), 3),
                    "avg": round(sum(times) / len(times), 4) if times else 0,
                    "max": round(max(times), 4) if times else 0,
                }
                for stage, times in self.timings.items()
            },
            "counters": dict(self.counters),
            "throughput": round(self.counters.get("records", 0) / total_time, 2) if total_time > 0 else 0,
        }
```

---

### 9.3 项目三：命令行工具开发

#### argparse/click/typer

```python
# 方案1：argparse（标准库，零依赖）
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="数据处理命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 子命令：process
    process_parser = subparsers.add_parser("process", help="处理数据文件")
    process_parser.add_argument("input", help="输入文件路径")
    process_parser.add_argument("-o", "--output", help="输出文件路径")
    process_parser.add_argument("--format", choices=["csv", "json"], default="csv")
    process_parser.add_argument("-v", "--verbose", action="store_true")

    # 子命令：validate
    validate_parser = subparsers.add_parser("validate", help="验证数据")
    validate_parser.add_argument("input", help="输入文件路径")

    args = parser.parse_args()

    if args.command == "process":
        process_file(args.input, args.output, args.format, args.verbose)
    elif args.command == "validate":
        validate_file(args.input)

# 方案2：click（装饰器风格，功能丰富）
import click

@click.group()
@click.option("--config", default="config.yaml", help="配置文件路径")
@click.pass_context
def cli(ctx, config):
    """数据处理命令行工具"""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config)

@cli.command()
@click.argument("input")
@click.option("-o", "--output", help="输出文件")
@click.option("--format", type=click.Choice(["csv", "json"]), default="csv")
@click.option("--verbose", is_flag=True)
def process(input, output, format, verbose):
    """处理数据文件"""
    if verbose:
        click.echo(f"Processing {input}...")
    process_file(input, output, format)

@cli.command()
@click.argument("input")
def validate(input):
    """验证数据"""
    result = validate_file(input)
    click.echo(f"Valid: {result}")

# 方案3：typer（基于 click，类型注解驱动，推荐）
import typer
from typing import Optional
from enum import Enum

app = typer.Typer(help="数据处理命令行工具")

class OutputFormat(str, Enum):
    csv = "csv"
    json = "json"

@app.command()
def process(
    input_file: str = typer.Argument(..., help="输入文件路径"),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="输出文件路径"),
    format: OutputFormat = typer.Option(OutputFormat.csv, "--format", help="输出格式"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="详细输出"),
):
    """处理数据文件"""
    if verbose:
        typer.echo(f"Processing {input_file}...")
    process_file(input_file, output, format.value)
    typer.echo("Done!")

@app.command()
def validate(input_file: str = typer.Argument(..., help="输入文件路径")):
    """验证数据文件"""
    result = validate_file(input_file)
    if result.valid:
        typer.echo("✅ Valid")
        raise typer.Exit(code=0)
    else:
        typer.echo(f"❌ Invalid: {result.errors}", err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
```

#### 子命令设计

```python
# 完整的 CLI 工具结构
import typer
from typing import Optional

app = typer.Typer(name="datatool", help="数据处理工具集", no_args_is_help=True)

# 子命令组
config_app = typer.Typer(help="配置管理")
app.add_typer(config_app, name="config")

@config_app.command("show")
def config_show():
    """显示当前配置"""
    config = load_config()
    typer.echo(config.model_dump_json(indent=2))

@config_app.command("set")
def config_set(key: str, value: str):
    """设置配置项"""
    config = load_config()
    setattr(config, key, value)
    save_config(config)
    typer.echo(f"Set {key} = {value}")

# 数据处理子命令组
data_app = typer.Typer(help="数据处理")
app.add_typer(data_app, name="data")

@data_app.command("import")
def data_import(
    source: str = typer.Argument(..., help="数据源路径或URL"),
    table: str = typer.Option(..., "--table", "-t", help="目标表名"),
    batch_size: int = typer.Option(1000, "--batch-size", help="批处理大小"),
):
    """导入数据到数据库"""
    with typer.progressbar(length=100, label="Importing") as progress:
        for i in range(100):
            # 导入逻辑
            progress.update(1)

@data_app.command("export")
def data_export(
    query: str = typer.Option(..., "--query", "-q", help="SQL查询"),
    output: str = typer.Option(..., "--output", "-o", help="输出文件"),
):
    """导出查询结果"""
    ...

# 工具命令
@app.command()
def version():
    """显示版本信息"""
    typer.echo("datatool v1.0.0")

@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="详细模式"),
    config_path: str = typer.Option("config.yaml", "--config", "-c", help="配置文件"),
):
    """datatool - 数据处理工具集"""
    if verbose:
        typer.echo(f"Using config: {config_path}")
```

#### 配置管理

```python
# config.py — CLI 工具配置管理
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
import os

class ToolConfig(BaseSettings):
    """工具配置：环境变量 > 配置文件 > 默认值"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DATATOOL_",
        extra="ignore",
    )

    database_url: str = Field(default="postgresql://localhost/db")
    default_batch_size: int = Field(default=1000, ge=1, le=100000)
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR)$")
    output_dir: Path = Field(default=Path("./output"))

    @classmethod
    def load(cls, config_path: str | None = None) -> "ToolConfig":
        """从配置文件加载，环境变量覆盖"""
        if config_path and os.path.exists(config_path):
            import yaml
            with open(config_path) as f:
                file_config = yaml.safe_load(f) or {}
            return cls(**file_config)
        return cls()

# 使用
config = ToolConfig.load("config.yaml")
print(config.database_url)
print(config.default_batch_size)
```

#### 打包发布

```toml
# pyproject.toml — 命令行工具打包配置
[project]
name = "datatool"
version = "1.0.0"
description = "数据处理命令行工具"
requires-python = ">=3.10"
dependencies = [
    "typer>=0.9.0",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "rich>=13.0",
    "pyyaml>=6.0",
]

[project.scripts]
datatool = "datatool.cli:app"  # 命令入口

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/datatool"]
```

```bash
# 本地安装（开发模式）
pip install -e .

# 构建发布
python -m build
twine upload dist/*

# 测试安装
pip install datatool
datatool --help
datatool data import data.csv --table users
datatool config show
```

---

### 9.4 老手成长路线图

#### 持续学习资源

**书籍（进阶必读）：**
- 《Fluent Python》（流畅的Python）— Python 进阶圣经
- 《Effective Python》— 90 条具体建议
- 《Python Cookbook》— 实战技巧合集
- 《Architecture Patterns with Python》— 架构模式
- 《Designing Data-Intensive Applications》— 数据密集型应用

**在线资源：**
- Python 官方文档（docs.python.org）— 最权威的参考
- Real Python（realpython.com）— 高质量教程
- PyCon 演讲（YouTube）— 社区前沿
- Python Weekly 邮件列表 — 每周资讯
- Hacker News / Reddit r/Python — 社区讨论

**核心库源码阅读：**
- `requests` — API 设计典范
- `flask` — 微框架架构
- `fastapi` — 现代 Web 框架
- `pydantic` — 数据验证
- `pandas` — 数据处理（C 扩展部分）
- `sqlalchemy` — ORM 设计

#### 开源贡献

```text
开源贡献路径：
1. 从文档开始：修复 typo、改进文档、添加示例
2. 修复小 bug：good first issue / help wanted 标签
3. 实现小功能：讨论后实现，写测试
4. 代码审查：review 别人的 PR，学习代码风格
5. 成为维护者：持续贡献，获得合并权限

推荐贡献的项目：
- 自己日常使用的库（最有动力）
- scikit-learn（数据科学，代码质量高）
- fastapi（Web 框架，活跃）
- pandas（数据处理，issue 多）
- pytest（测试框架，代码优雅）
```

#### 技术博客

```text
写技术博客的价值：
1. 深化理解 — 教是最好的学
2. 建立个人品牌 — 面试官会看你的博客
3. 社区影响力 — 被更多人认识
4. 知识沉淀 — 一年后回看自己的成长

博客主题建议：
- 踩坑记录："我如何调试这个诡异的 Python 内存泄漏"
- 源码解读："深入 requests 库的连接池实现"
- 性能优化："将 Python 脚本从 10 分钟优化到 10 秒"
- 最佳实践："我们团队的 Python 工程化规范"
- 项目实战："用 FastAPI 构建高并发 API 的完整记录"

平台选择：
- 个人博客（Hugo/Next.js + GitHub Pages）
- 掘金 / 知乎 / 思否（中文社区）
- Medium / Dev.to（英文社区）
- GitHub README（项目文档即博客）
```

#### 社区参与

```text
Python 社区参与方式：
1. 本地 Meetup：参加 Python 用户组（PUG）活动
2. 技术大会：PyCon China、PyData、QCon
3. 线上社区：Python 中文社区、V2EX、掘金
4. 开源项目：贡献代码、回答 issue、帮助新手
5. 技术分享：在公司/社区做技术分享

老手的终极标志：
- 能独立设计和落地中型系统架构
- 能指导初级开发者，做代码审查
- 能在团队中推广最佳实践
- 能在社区中输出有价值的内容
- 持续学习，保持对新技术的敏感度

成长不是线性的，是阶梯式的：
- 新手 → 能写代码（语法）
- 熟手 → 能写好代码（风格、测试）
- 老手 → 能设计系统（架构、性能、工程化）
- 专家 → 能影响社区（开源、布道、标准制定）
```

---

### 本章总结

三个实战项目整合了前八章的所有知识点：
- **高性能 Web API**：FastAPI 异步框架、连接池、缓存策略、分层架构、Docker 部署
- **数据处理 ETL**：流式管道、增量抽取、错误恢复、死信队列、性能监控
- **命令行工具**：typer 子命令设计、配置管理、进度条、打包发布

老手的核心能力不是"知道更多语法"，而是**能把各种知识整合成可交付的工程产品**——有架构、有测试、有监控、有文档、可维护。

### 思考题/实战练习

1. **Web API 实战**：用 FastAPI 实现一个用户管理 API，包含注册/登录/CRUD，使用 JWT 认证、Redis 缓存、PostgreSQL 存储，编写完整的测试和 Docker 部署配置。
2. **ETL 管道实战**：实现一个从 CSV 文件抽取数据、清洗转换、加载到 PostgreSQL 的 ETL 管道，支持增量处理、错误重试、死信队列和性能监控。
3. **CLI 工具实战**：用 typer 开发一个文件批量重命名工具，支持正则匹配、预览模式、撤销功能，打包为可执行命令并发布到 PyPI。
4. **架构设计**：为一个日处理 1 亿条日志的系统设计数据处理架构，考虑吞吐量、容错、监控、扩展性。
5. **成长计划**：制定你自己的 6 个月 Python 老手成长计划，包含学习资源、开源贡献目标、博客写作计划。

---

> **全文总结**：从 Pythonic 风格到性能优化，从设计模式到元编程，从调试测试到工程化，从面试题到数据科学，再到综合实战——这份文档覆盖了 Python 实战老手所需的全部核心能力。但知识只有在实践中才能真正掌握。选一个项目，动手写，踩坑，调试，优化，你就已经在成为老手的路上了。

