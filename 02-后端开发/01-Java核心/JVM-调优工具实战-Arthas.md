---
title: JVM-调优工具实战-Arthas
tags: [Java, Arthas, 性能优化, 问题排查, 原子笔记]
category: 后端开发
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["JVM-内存模型与GC调优", "Java问题排查手册", "Java-并发编程JUC"]
aliases: [JVM-调优工具实战-Arthas]
---

# JVM-调优工具实战-Arthas

> **文档说明**：系统讲解 Alibaba Arthas JVM 诊断工具的安装、核心命令、实战场景、高级功能，包括 CPU 飙高、内存泄漏、慢方法追踪、死锁排查、热更新代码等生产级问题排查方案。
>
> **适用人群**：后端开发工程师、运维工程师、架构师、需要排查 JVM 生产问题的开发者
>
> **前置知识**：[[JVM-内存模型与GC调优]]、[[Java问题排查手册]]、[[Java-并发编程JUC]]、[[JVM-类加载机制详解]]

---

## 一、概述

### 1. 什么是 Arthas

**Arthas** 是 Alibaba 开源的 Java 诊断工具，支持在线排查问题、动态跟踪 Java 代码、实时监控 JVM 状态，无需重启应用，是生产环境问题排查的利器。

### 2. Arthas 能做什么

| 能力 | 说明 |
|------|------|
| **实时监控** | 仪表盘查看线程、内存、GC、JVM 状态 |
| **方法追踪** | 查看方法入参、返回值、异常、耗时 |
| **调用链追踪** | trace 方法内部调用路径和耗时 |
| **热更新代码** | 反编译、修改、重新加载类（redefine） |
| **类加载查看** | 查看类加载信息、方法信息 |
| **内存分析** | heapdump、内存对象统计 |
| **火焰图** | async-profiler 生成 CPU/内存火焰图 |
| **表达式求值** | OGNL 表达式执行任意代码 |

### 3. Arthas vs 其他工具

| 工具 | 特点 | 适用场景 |
|------|------|---------|
| **Arthas** | 在线诊断、无需重启、命令行交互 | 生产环境实时排查 |
| **jstack/jmap/jstat** | JDK 自带、基础功能 | 简单问题快速查看 |
| **VisualVM** | GUI、可视化 | 开发环境分析 |
| **JProfiler/YourKit** | 商业、功能强大 | 深度性能分析 |
| **MAT** | 堆内存分析 | 内存泄漏分析 |
| **async-profiler** | 火焰图、低开销 | CPU/内存性能分析 |

---

## 二、安装与启动

### 1. 安装

```bash
# 方式1：一键安装（推荐）
curl -O https://arthas.aliyun.com/arthas-boot.jar
java -jar arthas-boot.jar

# 方式2：全量安装
curl -L https://arthas.aliyun.com/download/latest_version?mirror=aliyun -o arthas.zip
unzip arthas.zip -d arthas
cd arthas
./as.sh

# 方式3：Docker
docker exec -it <container> /bin/bash
curl -O https://arthas.aliyun.com/arthas-boot.jar
java -jar arthas-boot.jar
```

### 2. 启动

```bash
# 启动后会列出所有 Java 进程，选择要诊断的进程
java -jar arthas-boot.jar
# [1]: 12345 com.example.Application
# [2]: 67890 org.apache.catalina.startup.Bootstrap
# 输入 1 连接到第一个进程

# 直接指定 PID
java -jar arthas-boot.jar 12345

# 指定目标进程的 JVM 名称
java -jar arthas-boot.jar --select com.example.Application

# 远程连接（需先在目标机器启动 arthas tunnel server）
java -jar arthas-boot.jar --tunnel-server ws://arthas-server:7777/ws
```

### 3. 常用启动参数

```bash
# 指定 arthas 端口（默认 3658）
java -jar arthas-boot.jar --telnet-port 3658 --http-port 8563

# 以 attach 模式启动（不进入交互）
java -jar arthas-boot.jar --attach-only

# 指定 JDK 路径
java -jar arthas-boot.jar --jdk-home /path/to/jdk

# 退出后保留会话
java -jar arthas-boot.jar --session-timeout 3600
```

---

## 三、核心命令

### 1. dashboard：实时仪表盘

```bash
# 查看实时仪表盘（线程、内存、GC、JVM）
dashboard

# 每 5 秒刷新一次
dashboard -n 5

# 输出：
# - ID   NAME         GROUP    PRIORITY  STATE   %CPU  TIME    INTERRUPTED DAEMON
# - 1    main         main     5         RUNNABLE 12    0:30    false       false
# - 2    GC Thread    system   9         RUNNABLE 5     0:10    false       true
#
# - Memory        used     total    max      usage
# - heap          512M     1024M    2048M    25.0%
# - nonheap       128M     128M     -        100%
#
# - GC            count    time
# - gc.ps_scavenge 100      500ms
# - gc.ps_marksweep 10      2000ms
```

### 2. thread：线程分析

```bash
# 查看所有线程
thread

# 查看 CPU 占用最高的前 3 个线程
thread -n 3

# 查看指定线程的栈
thread 123

# 查看阻塞状态的线程
thread --state BLOCKED

# 查找死锁
thread -b

# 查看线程池状态
thread --state WAITING | grep pool

# 输出示例（CPU 最高线程）：
# "http-nio-8080-exec-1" Id=123 RUNNABLE
#     at com.example.service.UserService.queryUser(UserService.java:45)
#     at com.example.controller.UserController.getUser(UserController.java:23)
#     ...
```

### 3. watch：方法观测

```bash
# 观察方法入参和返回值
watch com.example.service.UserService getUser '{params, returnObj}' -x 2

# 只观察返回值
watch com.example.service.UserService getUser returnObj

# 观察方法执行耗时
watch com.example.service.UserService getUser '{params, returnObj, cost}' -x 2

# 条件过滤：只观察耗时超过 100ms 的
watch com.example.service.UserService getUser '{params, returnObj}' '#cost>100'

# 观察异常
watch com.example.service.UserService getUser '{params, throwExp}' -e

# -x 2：展开深度为 2（对象属性层级）
# -n 10：只执行 10 次
# -b：方法调用前观察
# -s：方法返回后观察（默认）
# -f：方法结束后（包含异常）
```

### 4. trace：方法调用追踪

```bash
# 追踪方法内部调用路径和耗时
trace com.example.service.UserService getUser

# 只追踪耗时超过 50ms 的调用
trace com.example.service.UserService getUser '#cost>50'

# 包含 JDK 方法（默认排除）
trace --skipJDKMethod false com.example.service.UserService getUser

# 输出示例：
# `---[120ms] com.example.service.UserService:getUser()
#     +---[10ms] com.example.dao.UserMapper:selectById()
#     +---[80ms] com.example.cache.RedisCache:get()  # 慢调用
#     `---[30ms] com.example.util.JsonUtil:toJson()
```

### 5. stack：方法调用栈

```bash
# 查看方法被谁调用
stack com.example.service.UserService getUser

# 条件过滤
stack com.example.service.UserService getUser 'params[0]=123'

# 输出示例：
# com.example.controller.UserController.getUser(UserController.java:23)
#   com.example.service.UserService.getUser(UserService.java:45)
#     com.example.dao.UserMapper.selectById(UserMapper.java:12)
```

### 6. monitor：方法监控

```bash
# 监控方法调用统计（每 60 秒输出一次）
monitor -c 60 com.example.service.UserService getUser

# 输出：
#  timestamp            class         method        total  success  fail  avg(ms)  fail-rate
#  2026-08-27 10:00:00  UserService   getUser       100    98       2     45.2     2.0%
```

### 7. tt：时间隧道（记录方法调用，可回放）

```bash
# 记录方法调用
tt -t com.example.service.UserService getUser

# 查看所有记录
tt -l

# 查看指定索引的详情
tt -i 1000

# 回放某次调用（重新执行）
tt -i 1000 -p

# 回放并修改入参
tt -i 1000 -p 'params[0]=999'

# 删除记录
tt --delete-all
```

---

## 四、类与代码相关

### 1. sc：查看类信息

```bash
# 搜索类
sc com.example.*UserService

# 查看类的详细信息（类加载器、代码源）
sc -d com.example.service.UserService

# 查看类的所有方法
sm com.example.service.UserService

# 查看指定方法
sm com.example.service.UserService getUser

# 输出示例：
# class-info        com.example.service.UserService
# code-source       /app/app.jar!/BOOT-INF/classes!/
# name              com.example.service.UserService
# isInterface       false
# isAnnotation      false
# isEnum            false
# isAnonymousClass  false
# isArray           false
# isLocalClass      false
# isMemberClass     false
# isPrimitive       false
# isSynthetic       false
# simple-name       UserService
# modifier          public
# annotation        org.springframework.stereotype.Service
# interfaces
# super-class       +-java.lang.Object
# class-loader      +-org.springframework.boot.loader.LaunchedURLClassLoader
```

### 2. jad：反编译

```bash
# 反编译类
jad com.example.service.UserService

# 反编译指定方法
jad --source-only com.example.service.UserService getUser

# 反编译并保存到文件
jad --source-only com.example.service.UserService > /tmp/UserService.java
```

### 3. mc + redefine：热更新代码

```bash
# 1. 反编译获取源码
jad --source-only com.example.service.UserService > /tmp/UserService.java

# 2. 修改源码（修复 bug）
vim /tmp/UserService.java

# 3. 编译修改后的代码
mc /tmp/UserService.java -d /tmp/

# 4. 热加载（redefine）
redefine /tmp/com/example/service/UserService.class

# 注意：
# - redefine 不能修改方法签名、字段、类结构
# - 只能修改方法体内部逻辑
# - Spring Bean 需要重新获取或刷新上下文
```

### 4. classloader：类加载器

```bash
# 查看所有类加载器
classloader -l

# 查看类加载器的继承树
classloader -t

# 查看指定类加载器加载的类
classloader -a -c 1f234567

# 用指定类加载器查找资源
classloader -c 1f234567 -r META-INF/MANIFEST.MF
```

---

## 五、JVM 与内存

### 1. jvm：JVM 信息

```bash
# 查看 JVM 信息
jvm

# 输出：
# - RUNTIME
#   MACHINE-NAME    localhost
#   JVM-START-TIME  2026-08-27 09:00:00
#   MANAGEMENT-SPEC 1.2
#   SPEC-NAME       Java Virtual Machine Specification
#   ...
# - CLASS-LOADING
#   LOADED-COUNT    5000
#   TOTAL-LOADED    6000
#   UNLOADED-COUNT  1000
# - COMPILATION
#   NAME            HotSpot 64-Bit Tiered Compilers
#   TOTAL-COMPILE-TIME 120000
# - GARBAGE-COLLECTORS
#   PS Scavenge     100 collections, 500ms
#   PS MarkSweep    10 collections, 2000ms
```

### 2. memory：内存信息

```bash
# 查看内存使用
memory

# 输出：
# - heap
#   PS Eden Space          used 256M, max 512M
#   PS Survivor Space      used 32M, max 64M
#   PS Old Gen             used 512M, max 1024M
# - nonheap
#   Metaspace              used 128M, max -1
#   Code Cache             used 64M, max 240M
```

### 3. heapdump：堆转储

```bash
# 生成堆转储文件
heapdump /tmp/heap.hprof

# 只 dump live 对象（推荐，文件更小）
heapdump --live /tmp/heap_live.hprof

# 下载后用 MAT（Eclipse Memory Analyzer）分析
```

### 4. vmoption：JVM 参数

```bash
# 查看所有 JVM 参数
vmoption

# 查看指定参数
vmoption PrintGC

# 动态修改 JVM 参数（运行时）
vmoption PrintGC true
vmoption HeapDumpOnOutOfMemoryError true
```

### 5. ognl：表达式执行

```bash
# 执行 OGNL 表达式
ognl '@java.lang.System@out.println("hello")'

# 调用静态方法
ognl '@com.example.util.ConfigUtil@getConfig("key")'

# 调用 Spring Bean 的方法
ognl '@com.example.ApplicationContext@getApplicationContext().getBean("userService").getUser(1)'

# 查看静态字段
ognl '@com.example.service.UserService@CACHE_SIZE'

# 执行多行代码
ognl '#value=@com.example.util.ConfigUtil@getConfig("key"), #value'
```

---

## 六、实战场景

### 1. CPU 飙高排查

```bash
# 步骤1：dashboard 查看整体 CPU
dashboard

# 步骤2：找到 CPU 最高的线程
thread -n 3

# 步骤3：查看该线程的栈，定位代码
thread <thread_id>

# 步骤4：trace 追踪慢方法
trace com.example.service.SlowService processMethod '#cost>100'

# 步骤5：watch 查看入参
watch com.example.service.SlowService processMethod '{params, cost}' '#cost>100'
```

### 2. 内存泄漏排查

```bash
# 步骤1：查看内存趋势
dashboard  # 观察 heap 使用是否持续增长

# 步骤2：生成堆转储
heapdump --live /tmp/heap.hprof

# 步骤3：下载到本地用 MAT 分析
# 或在 Arthas 中查看大对象
ognl '@java.lang.Runtime@getRuntime().totalMemory()'

# 步骤4：查看类实例统计
sc -d com.example.cache.*Cache

# 步骤5：watch 观察缓存是否清理
watch com.example.cache.UserCache put 'params[0]' -n 100
```

### 3. 接口响应慢排查

```bash
# 步骤1：trace 追踪接口入口
trace com.example.controller.UserController getUser

# 步骤2：找到最慢的内部调用
# 输出会显示每个调用的耗时占比

# 步骤3：深入追踪慢方法
trace com.example.dao.UserMapper selectById

# 步骤4：watch 查看入参和返回值
watch com.example.dao.UserMapper selectById '{params, returnObj, cost}' -x 2

# 步骤5：monitor 监控统计
monitor -c 60 com.example.dao.UserMapper selectById
```

### 4. 死锁排查

```bash
# 步骤1：查找死锁
thread -b

# 输出会显示：
# "thread-1" Id=101 BLOCKED
#     at com.example.service.AccountService.transfer(AccountService.java:30)
#     - 等待锁 <0x1234> (被 thread-2 持有)
# "thread-2" Id=102 BLOCKED
#     at com.example.service.AccountService.transfer(AccountService.java:35)
#     - 等待锁 <0x5678> (被 thread-1 持有)

# 步骤2：查看两个线程的完整栈
thread 101
thread 102
```

### 5. 方法异常排查

```bash
# 步骤1：watch 观察异常
watch com.example.service.UserService getUser '{params, throwExp}' -e -x 2

# 步骤2：stack 查看调用来源
stack com.example.service.UserService getUser

# 步骤3：tt 记录异常调用，回放分析
tt -t com.example.service.UserService getUser
tt -l  # 查看记录
tt -i <index>  # 查看详情
```

### 6. 热修复线上 Bug

```bash
# 步骤1：反编译有问题的类
jad --source-only com.example.service.PaymentService > /tmp/PaymentService.java

# 步骤2：修改代码（修复 bug）
vim /tmp/PaymentService.java

# 步骤3：编译
mc /tmp/PaymentService.java -d /tmp/

# 步骤4：热加载
redefine /tmp/com/example/service/PaymentService.class

# 步骤5：验证修复
watch com.example.service.PaymentService pay '{params, returnObj}' -n 5
```

---

## 七、高级功能

### 1. profiler：火焰图

```bash
# 启动 CPU 火焰图采样
profiler start

# 等待一段时间后停止并生成 SVG
profiler stop --format svg

# 生成内存分配火焰图
profiler start --event alloc
profiler stop --format svg -f /tmp/alloc.svg

# 生成锁竞争火焰图
profiler start --event lock
profiler stop --format svg

# 查看支持的事件
profiler list

# 生成的 SVG 文件可在浏览器中打开，交互式查看
```

### 2. 异步任务与后台执行

```bash
# 后台执行命令（不阻塞）
trace com.example.service.UserService getUser &

# 查看后台任务
jobs

# 停止后台任务
kill 1  # 停止 job id 为 1 的任务

# 异步保存结果到文件
trace com.example.service.UserService getUser > /tmp/trace.log &
```

### 3. 批量执行脚本

```bash
# 执行脚本文件
cat /tmp/arthas-script.txt | java -jar arthas-boot.jar --batch

# 脚本内容示例：
# dashboard -n 1
# thread -n 3
# heapdump /tmp/heap.hprof
# quit
```

---

## 八、最佳实践

### 1. 使用规范

- [ ] **生产环境谨慎**：redefine、heapdump 等操作有性能影响，低峰期执行
- [ ] **及时退出**：排查完成后执行 `stop` 或 `quit`，释放资源
- [ ] **限制次数**：watch/trace 加 `-n` 参数，避免无限执行
- [ ] **条件过滤**：加条件表达式，减少输出量
- [ ] **heapdump 注意**：大堆 heapdump 可能导致 STW，评估影响
- [ ] **redefine 限制**：不能修改方法签名和字段，只能改方法体
- [ ] **权限控制**：生产环境 Arthas 访问需权限控制

### 2. 常用命令速查

| 场景 | 命令 |
|------|------|
| 整体状态 | `dashboard` |
| CPU 高 | `thread -n 3` |
| 死锁 | `thread -b` |
| 方法耗时 | `trace Class method` |
| 方法入参返回 | `watch Class method '{params,returnObj}'` |
| 调用来源 | `stack Class method` |
| 方法统计 | `monitor -c 60 Class method` |
| 反编译 | `jad Class` |
| 热更新 | `mc` + `redefine` |
| 堆转储 | `heapdump --live /tmp/heap.hprof` |
| 火焰图 | `profiler start` / `profiler stop` |
| JVM 参数 | `vmoption` |
| 执行代码 | `ognl 'expression'` |

### 3. 与其他工具配合

```
排查流程：
1. Arthas dashboard → 发现 CPU/内存异常
2. Arthas thread -n → 定位问题线程
3. Arthas trace → 定位慢方法
4. Arthas watch → 查看入参返回值
5. jmap/MAT → 深度内存分析
6. async-profiler → 火焰图分析性能瓶颈
7. jstack → 线程快照对比
```

---

## 九、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **连接不上目标进程** | 权限不足 / JDK 版本不匹配 / 进程已退出 | 用相同用户启动、检查 JDK 版本、确认进程存活 |
| **命令无输出** | 类名/方法名错误 / 条件不匹配 | 用 sc 确认类存在、检查方法签名、放宽条件 |
| **redefine 失败** | 修改了方法签名/字段 / 类被锁 | 只能修改方法体、确保类未被 JIT 特殊优化 |
| **heapdump 卡住** | 堆太大 / STW 时间长 | 用 --live、低峰期执行、评估堆大小 |
| **watch 输出太多** | 未加限制 / 未加条件 | 加 -n 限制次数、加条件表达式 |
| **trace 不显示某些调用** | 默认跳过 JDK 方法 / 异步调用 | --skipJDKMethod false、异步需单独 trace |
| **性能影响大** | 命令开销大 / 高频方法追踪 | 加条件过滤、限制次数、低峰期执行 |
| **ognl 执行失败** | 表达式错误 / 类加载器问题 | 检查表达式、指定 classloader |
| **Docker 中无法使用** | 容器内无 JDK / 权限问题 | 安装 JDK、--jdk-home 指定、特权模式 |
| **Arthas 自己占资源** | 长时间运行 / 命令未停止 | 及时 quit、jobs 查看并 kill 后台任务 |
| **Spring Bean 热更不生效** | Bean 已被代理 / 缓存 | 清除缓存、重新获取 Bean、或重启 |
| **tt 回放失败** | 方法有副作用 / 依赖外部状态 | 无状态方法可回放，有副作用需谨慎 |
| **profiler 不支持** | 内核版本低 / 权限不足 | 升级内核、--event 选择支持的事件 |
| **中文乱码** | 终端编码问题 | 设置终端 UTF-8、用 --encoding utf-8 |
| **类找不到** | 类加载器不同 / 未加载 | sc 搜索、指定 classloader、触发类加载 |

---

## 十、关联笔记

### JVM 核心
- [[JVM-内存模型与GC调优]] · [[JVM-类加载机制详解]] · [[JVM-字节码与执行引擎]]
- [[Java-并发编程JUC]]

### 问题排查
- [[Java问题排查手册]] · [[后端性能优化实战]] · [[SkyWalking-分布式链路追踪]]

### 工具链
- [[Docker容器化实战]] · [[K8s-核心概念与架构]] · [[Linux常用命令与运维]]

### 导航
- [[MOC-后端开发]] · [[MOC-云原生与运维]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[JVM-内存模型与GC调优]] JVM 基础 → 学习 [[Java问题排查手册]] 排查思路 → 深入本文 Arthas 实战 → 实践 [[SkyWalking-分布式链路追踪]] 全链路追踪 → 研究 [[后端性能优化实战]] 性能优化 → 构建完整的 JVM 问题排查与性能调优能力。
