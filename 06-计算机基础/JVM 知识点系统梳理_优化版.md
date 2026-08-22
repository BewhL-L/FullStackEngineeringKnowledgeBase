---
title: JVM 知识点系统梳理
tags: [计算机基础, JVM, GC, 内存模型, 面试]
created: 2026-08-12
updated: 2026-08-12
---

# JVM知识点系统梳理（优化版）

> **文档说明**：本文档参照《Java知识点完整整合大全》排版风格，系统梳理 JVM（Java 虚拟机）技术栈。包含概述、核心特性、常用用法、注意事项四大模块，辅以动态可视化解析图、深度讲解与精简总结。**优化版**在原有内容基础上，为每个知识点补充了作用、原理、用法的深度解析，并新增了知识点图解。

---

## 1. 概述

JVM（Java Virtual Machine）是 Java 程序的运行环境，它实现了"一次编写，到处运行"的跨平台能力。JVM 负责字节码加载、内存管理、垃圾回收、即时编译等核心功能，是 Java 生态的基石。

**核心定位**：
- 跨平台执行：字节码在不同 OS 的 JVM 上运行
- 自动内存管理：GC 自动回收无用对象，无需手动 free
- 安全沙箱：字节码校验、安全管理器
- 性能优化：JIT 即时编译、逃逸分析、锁优化

**版本演进**：

| 版本 | 关键特性 |
|------|---------|
| JDK 1.2 | 分代 GC、Exact VM |
| JDK 1.3 | HotSpot 成为默认 VM |
| JDK 1.5 | 原子类、并发包、Instrumentation |
| JDK 1.7 | G1 收集器（实验）、invokedynamic |
| JDK 8 | Metaspace 替代永久代、Lambda |
| JDK 11 | ZGC（实验）、Epsilon、Flight Recorder |
| JDK 17 | ZGC 正式、密封类、模式匹配 |
| JDK 21 | 分代 ZGC、虚拟线程、记录模式 |

---


---
## 2. 核心特性

<div style="background:linear-gradient(135deg,#f093fb,#f5576c);border-radius:16px;padding:24px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#fff;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes jvmPulse{0%,100%{transform:scale(1);opacity:.85}50%{transform:scale(1.04);opacity:1}}.jvm-area{display:inline-block;width:30%;vertical-align:top;margin:0 1% 8px;background:rgba(255,255,255,.15);border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.08);padding:12px;font-size:11px;text-align:center;animation:jvmPulse 3s ease-in-out infinite}.jvm-area:nth-child(2){animation-delay:.5s}.jvm-area:nth-child(3){animation-delay:1s}.jvm-area:nth-child(4){animation-delay:1.5s}.jvm-area:nth-child(5){animation-delay:2s}.jvm-icon{font-size:24px;margin-bottom:6px}.jvm-name{font-weight:700;font-size:13px;margin-bottom:4px}</style>
<div style="text-align:center;font-size:16px;font-weight:700;margin-bottom:16px;padding-bottom:12px;border-bottom:1.5px solid rgba(255,255,255,.22);letter-spacing:1px;text-shadow:0 1px 3px rgba(0,0,0,.12)">JVM 运行时内存区域</div>
<div style="text-align:center">
<div class="jvm-area"><div class="jvm-icon">🗄️</div><div class="jvm-name">堆</div><div style="font-size:10px;opacity:.85">对象实例<br>线程共享/GC主区</div></div>
<div class="jvm-area"><div class="jvm-icon">📚</div><div class="jvm-name">方法区</div><div style="font-size:10px;opacity:.85">类信息/常量<br>线程共享/元空间</div></div>
<div class="jvm-area"><div class="jvm-icon">📋</div><div class="jvm-name">虚拟机栈</div><div style="font-size:10px;opacity:.85">栈帧/局部变量<br>线程私有</div></div>
<div class="jvm-area"><div class="jvm-icon">📍</div><div class="jvm-name">程序计数器</div><div style="font-size:10px;opacity:.85">当前字节码行号<br>线程私有/无OOM</div></div>
<div class="jvm-area"><div class="jvm-icon">🔗</div><div class="jvm-name">本地方法栈</div><div style="font-size:10px;opacity:.85">Native方法<br>线程私有</div></div>
</div>
</div>

### 2.1 内存区域详解

JVM 运行时数据区分为线程共享和线程私有两部分：

**线程共享**：
- 堆（Heap）：对象实例和数组，GC 主要区域，分新生代/老年代
- 方法区（Method Area）：类信息、常量、静态变量、JIT 编译代码，JDK 8 后为元空间（Metaspace，使用本地内存）

**线程私有**：
- 虚拟机栈（VM Stack）：每个方法调用创建栈帧（局部变量表、操作数栈、动态链接、返回地址）
- 程序计数器（PC Register）：当前线程执行的字节码行号，唯一不会 OOM 的区域
- 本地方法栈（Native Method Stack）：为 Native 方法服务

> 🔍 **知识点深度解析**
>
> **作用**：JVM 内存区域划分是理解 Java 内存管理和 GC 的基础。不同区域有不同的生命周期、存储内容和回收策略，也是 OOM 排查的起点。
>
> **原理**：堆是 JVM 启动时创建的最大一块内存，所有线程共享，用于存储几乎所有对象实例（逃逸分析优化后，标量替换的对象可能分配在栈上）。方法区在 JDK 7 及之前是"永久代"（在堆中），JDK 8 改为"元空间"（使用本地内存，不受堆大小限制，但受 -XX:MaxMetaspaceSize 限制）。虚拟机栈是线程私有，每个方法调用创建一个栈帧，方法返回时栈帧出栈。局部变量表存放基本类型和对象引用，在编译期确定大小。程序计数器是唯一不会 OOM 的区域。
>
> **用法要点**：① 堆 OOM：对象无法回收或创建过多，用 -Xmx 调大或排查内存泄漏；② 栈溢出：递归过深或方法调用链过长，用 -Xss 调大；③ 元空间 OOM：类加载过多（动态代理/CGLIB/热部署），用 -XX:MaxMetaspaceSize 调大；④ 直接内存 OOM：NIO DirectByteBuffer 分配过多，用 -XX:MaxDirectMemorySize 限制；⑤ 用 jmap -heap 查看各区域使用情况，jstat -gcutil 查看 GC 统计。

<div style="background:linear-gradient(135deg,#f093fb,#f5576c);border-radius:14px;padding:18px;margin:14px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#fff;overflow:hidden;box-shadow:0 6px 20px rgba(0,0,0,.12)">
<style>@keyframes memFlow{0%{opacity:.5}50%{opacity:1}100%{opacity:.5}}.mem-shared{background:rgba(255,255,255,.2);border-radius:8px;padding:8px;margin-bottom:6px;text-align:center;animation:memFlow 2.5s ease-in-out infinite}.mem-private{background:rgba(255,255,255,.12);border-radius:8px;padding:6px;margin:3px 0;text-align:center;font-size:10px}</style>
<div style="text-align:center;font-size:13px;font-weight:700;margin-bottom:10px">JVM 内存区域划分</div>
<div class="mem-shared"><b>线程共享</b>：堆（新生代Eden/S0/S1 + 老年代）| 方法区/元空间</div>
<div style="display:flex;justify-content:space-around;margin-top:8px">
<div style="width:30%"><div class="mem-private"><b>线程1</b><br>栈+PC+本地栈</div></div>
<div style="width:30%"><div class="mem-private"><b>线程2</b><br>栈+PC+本地栈</div></div>
<div style="width:30%"><div class="mem-private"><b>线程N</b><br>栈+PC+本地栈</div></div>
</div>
</div>

### 2.2 类加载机制

类加载过程分为 5 个阶段：

1. **加载**：通过类全限定名获取二进制字节流，转换为方法区运行时数据结构，生成 Class 对象
2. **验证**：文件格式验证、元数据验证、字节码验证、符号引用验证
3. **准备**：为静态变量分配内存并设置零值（final static 直接赋值）
4. **解析**：符号引用转换为直接引用（类/字段/方法）
5. **初始化**：执行 `<clinit>()` 方法（静态变量赋值 + 静态代码块）

**双亲委派模型**：Bootstrap ClassLoader → Extension ClassLoader → Application ClassLoader → 自定义 ClassLoader。先委托父加载器加载，父加载器找不到才自己加载。

> 🔍 **知识点深度解析**
>
> **作用**：类加载机制是 Java 动态性的基础，实现了类的按需加载、热部署、代码热替换、隔离。双亲委派模型保证了核心类库的安全性。
>
> **原理**：类加载的触发时机（主动引用）：new 对象、访问静态变量/方法、反射、初始化子类、主类。被动引用不会触发初始化。`<clinit>()` 方法由编译器自动生成，合并所有静态变量赋值和静态代码块。JVM 会保证 `<clinit>()` 在多线程下正确加锁同步。双亲委派的破坏：① SPI（线程上下文类加载器）；② OSGi（网状加载）；③ Tomcat（每个 Webapp 先自己加载再委派）。
>
> **用法要点**：① 自定义类加载器继承 ClassLoader，重写 findClass()（不要重写 loadClass()）；② 热部署用自定义类加载器实现（卸载旧 ClassLoader，创建新加载器）；③ 类卸载条件：所有实例已回收、ClassLoader 已回收、Class 对象无引用；④ 两个类相同=全限定名相同+类加载器相同；⑤ SPI 用 Thread.currentThread().getContextClassLoader() 打破双亲委派。

### 2.3 垃圾回收（GC）

**垃圾判定**：
- 引用计数法（无法解决循环引用，Python 用）
- 可达性分析（Java 用）：从 GC Roots 出发，不可达的对象可回收

**四种引用**：

| 引用类型 | 说明 | 回收时机 | 用途 |
|---------|------|---------|------|
| 强引用 | new 对象 | 不回收 | 普通对象 |
| 软引用 SoftReference | 内存不足时回收 | OOM 前 | 缓存 |
| 弱引用 WeakReference | 下次 GC 必回收 | GC 时 | 缓存（ThreadLocal key） |
| 虚引用 PhantomReference | 仅用于跟踪回收 | 任意 | 堆外内存回收 |

**GC 算法**：标记-清除、标记-复制、标记-整理、分代收集。

> 🔍 **知识点深度解析**
>
> **作用**：GC 是 JVM 自动内存管理的核心，自动回收不再使用的对象，避免了手动内存管理的内存泄漏和野指针问题。
>
> **原理**：可达性分析从 GC Roots 开始遍历引用链，标记所有存活对象，未被标记的即为垃圾。GC Roots 包括：虚拟机栈引用、方法区静态变量引用、方法区常量引用、本地方法栈 JNI 引用。finalize() 可让对象自救一次但已废弃。分代收集基于"弱分代假说"（绝大多数对象朝生夕死）和"强分代假说"，新生代用复制算法（Eden:S0:S1=8:1:1），老年代用标记-整理。
>
> **用法要点**：① 软引用适合内存敏感的缓存；② 弱引用比软引用更弱，ThreadLocal 的 key 就是弱引用；③ 虚引用必须配合 ReferenceQueue，用于管理堆外内存；④ 不要用 finalize()，用 try-with-resources；⑤ 大对象直接进入老年代（-XX:PretenureSizeThreshold）；⑥ 长期存活对象晋升老年代（MaxTenuringThreshold 默认15）。

### 2.4 垃圾收集器

| 收集器 | 代 | 算法 | 特点 |
|--------|-----|------|------|
| Serial | 新生代 | 复制 | 单线程，Client 模式 |
| ParNew | 新生代 | 复制 | Serial 多线程版，配合 CMS |
| Parallel Scavenge | 新生代 | 复制 | 吞吐量优先，自适应 |
| CMS | 老年代 | 标记-清除 | 低延迟，有碎片，已废弃 |
| G1 | 全堆 | Region+复制 | 可预测停顿，JDK 9+ 默认 |
| ZGC | 全堆 | 着色指针+读屏障 | 极低延迟，JDK 15+ |

> 🔍 **知识点深度解析**
>
> **作用**：垃圾收集器是 GC 的具体实现，不同收集器在吞吐量和延迟之间有不同权衡。批处理任务用吞吐量优先（Parallel），在线服务用低延迟优先（G1/ZGC）。
>
> **原理**：CMS 分四步：初始标记（STW）→ 并发标记 → 重新标记（STW）→ 并发清除。缺点：内存碎片、占用CPU、浮动垃圾。G1 把堆分成大小相等的 Region（1-32MB），跟踪每个 Region 的垃圾价值，优先回收价值最高的 Region，实现可预测停顿。ZGC 用着色指针（指针高位存标记）和读屏障实现几乎全程并发，停顿与堆大小无关。
>
> **用法要点**：① JDK 8 默认 Parallel，JDK 9+ 默认 G1；② 低延迟服务用 G1/ZGC，大堆推荐 G1，超大堆（>32G）推荐 ZGC；③ CMS 已废弃（JDK 14 移除）；④ G1 不要设置 -Xmn，会破坏自适应；⑤ ZGC JDK 21 支持分代；⑥ 选择后需压测验证，GC 日志是调优最重要依据。

### 2.5 执行引擎

JVM 执行引擎负责执行字节码，有三种方式：

- **解释执行**：逐条解释字节码，启动快但执行慢
- **JIT 编译**：将热点代码编译为本地机器码
  - C1（Client Compiler）：快速编译，简单优化
  - C2（Server Compiler）：深度优化（逃逸分析、标量替换）
- **AOT 编译**：JDK 9+ 支持，运行前提前编译（GraalVM Native Image）

**JIT 优化技术**：逃逸分析、标量替换、栈上分配、锁消除、锁粗化、内联、循环展开。

> 🔍 **知识点深度解析**
>
> **作用**：执行引擎决定了 Java 程序的运行性能。JIT 编译让 Java 从"解释执行的慢语言"变成了"可与 C++ 媲美的高性能语言"。
>
> **原理**：JVM 启动时先用解释器执行（启动快），JIT 编译器在后台监控代码执行频率。超过阈值（C1默认1500，C2默认10000）触发编译。C1 做轻量优化，编译快；C2 做重量优化（逃逸分析、标量替换、循环向量化），编译慢但代码快。JDK 7+ 分层编译：先 C1，热度更高再 C2。逃逸分析：对象不逃逸则可标量替换（栈上分配）、锁消除。
>
> **用法要点**：① 微基准测试要预热，用 JMH；② 方法调用深度影响内联（MaxInlineLevel 默认9）；③ 不要写 final 以为能帮助 JIT（JIT 有 CHA 分析）；④ AOT（GraalVM Native Image）启动快但不支持反射（需配置元数据）；⑤ 用 -XX:+PrintCompilation 查看编译情况；⑥ JIT 编译线程数默认=CPU核数，容器环境注意限制。

---


---
## 3. 常用用法

### 3.1 JVM 启动参数

```bash

> 🔍 **知识点深度解析**
>
> **作用**：JVM 启动参数控制堆内存、垃圾回收器、日志和调试选项，是性能调优的入口。
>
> **原理**：堆内存：-Xms 初始堆、-Xmx 最大堆（生产设相同值避免动态扩缩）、-Xmn 新生代、-XX:MetaspaceSize 元空间。GC：-XX:+UseG1GC（JDK9+ 默认）、-XX:MaxGCPauseMillis 目标暂停时间。日志：-Xlog:gc*（JDK9+ 统一日志）。诊断：-XX:+HeapDumpOnOutOfMemoryError 自动 dump、-XX:HeapDumpPath 指定路径。
>
> **用法要点**：① -Xms 和 -Xmx 设相同值，避免堆动态扩缩开销  ② -XX:+UseG1GC JDK9+ 默认，低延迟；ZGC/Shenandoah 超低延迟  ③ -XX:+HeapDumpOnOutOfMemoryError OOM 时自动 dump  ④ -Xlog:gc*:file=gc.log:time,uptime,level,tags JDK9+ GC 日志  ⑤ 面试常考：堆参数配置、GC 选择、OOM dump、JDK9+ 日志参数

# 堆设置
-Xms2g -Xmx2g                    # 初始堆=最大堆=2G
-Xmn512m                         # 新生代512M（G1不建议设置）
-XX:SurvivorRatio=8              # Eden:Survivor = 8:1
-XX:MetaspaceSize=256m
-XX:MaxMetaspaceSize=512m

# GC 收集器
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:+UseZGC                      # JDK 15+

# GC 日志（JDK 9+）
-Xlog:gc*:file=/var/log/gc.log:time,uptime,level,tags:filecount=10,filesize=100m

# OOM 自动 dump
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/heapdump.hprof

# 性能调优
-XX:+UseStringDeduplication
```

> 🔍 **知识点深度解析**
>
> **作用**：JVM 启动参数是调优的直接手段，合理设置能显著提升性能和稳定性。
>
> **原理**：-Xms=-Xmx 避免堆动态扩容（扩容需 STW）。G1 自动调节新生代大小，设置 -Xmn 会禁用自适应。GC 日志 JDK 9 后用 -Xlog 统一格式。HeapDumpOnOutOfMemoryError 在 OOM 时自动生成堆转储。StringDeduplication 在 GC 时共享相同字符串的 char[]，节省内存。
>
> **用法要点**：① 生产环境必须 -Xms=-Xmx；② 必须开启 GC 日志（滚动文件）；③ 必须设置 HeapDumpOnOutOfMemoryError；④ 容器环境 JDK 8u191+ 支持 UseContainerSupport；⑤ 不要盲目调大堆（堆越大 Full GC 停顿越长）；⑥ 元空间默认无上限，生产应设 MaxMetaspaceSize。

### 3.2 自定义类加载器

```java
public class MyClassLoader extends ClassLoader {
    private String classPath;
    public MyClassLoader(String classPath) { this.classPath = classPath; }

    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        try {
            String filePath = classPath + "/" + name.replace('.', '/') + ".class";
            byte[] bytes = Files.readAllBytes(Paths.get(filePath));
            return defineClass(name, bytes, 0, bytes.length);
        } catch (IOException e) {
            throw new ClassNotFoundException(name, e);
        }
    }
}

MyClassLoader loader = new MyClassLoader("/path/to/classes");
Class<?> clazz = loader.loadClass("com.example.MyClass");
```

> 🔍 **知识点深度解析**
>
> **作用**：自定义类加载器实现类的灵活加载：从非标准位置加载、热部署、代码隔离、版本共存。是 Tomcat、OSGi、Spring Boot DevTools 的基础。
>
> **原理**：loadClass() 默认实现双亲委派：先检查→委托父→findClass()。重写 findClass() 保留双亲委派。defineClass() 将字节数组转为 Class 对象。热部署原理：创建新 ClassLoader 加载新版本，旧 ClassLoader 和旧类一起卸载。不同 ClassLoader 加载的同名类是不同的类。
>
> **用法要点**：① 重写 findClass() 而非 loadClass()；② 加密 class 在 findClass() 中解密；③ 热部署确保旧 ClassLoader 可回收；④ 重写 getResource()；⑤ Tomcat WebappClassLoader 打破双亲委派（先自己加载）；⑥ 不要加载 JDK 核心类。

### 3.3 GC 调优

```bash

> 🔍 **知识点深度解析**
>
> **作用**：GC 调优目标是降低停顿时间和提高吞吐量，核心是调整堆大小、新生代比例和 GC 器参数。
>
> **原理**：调优步骤：① 开启 GC 日志分析停顿频率和耗时 ② 根据场景选 GC（Web 应用 G1/ZGC 低延迟，批处理 ParallelGC 高吞吐）③ 调整堆大小（Xmx 设为物理内存 70%，留元空间和直接内存）④ 调整新生代比例（G1 不用手动设新生代，用 MaxGCPauseMillis 自适应）⑤ 避免 Full GC（大对象直接进老年代、元空间不足、System.gc()）。
>
> **用法要点**：① 先监控再调优：GC 日志+APM 工具分析，不盲目调参  ② G1 调 MaxGCPauseMillis 和 ParallelGCThreads  ③ 避免 Full GC：控制大对象、元空间大小、禁用显式 GC  ④ ZGC/Shenandoah 适合 TB 级堆和亚毫秒停顿  ⑤ 面试常考：GC 调优流程、G1 参数、Full GC 原因、停顿 vs 吞吐

# G1 调优
-XX:+UseG1GC
-XX:MaxGCPauseMillis=100
-XX:G1HeapRegionSize=16m
-XX:InitiatingHeapOccupancyPercent=45

# ZGC 调优（JDK 15+）
-XX:+UseZGC
-XX:ZCollectionInterval=120

# Parallel 调优（吞吐量优先）
-XX:+UseParallelGC
-XX:GCTimeRatio=99
-XX:+UseAdaptiveSizePolicy
```

> 🔍 **知识点深度解析**
>
> **作用**：GC 调优目标是在吞吐量和延迟间找平衡点。基于 GC 日志分析定位瓶颈，针对性优化。
>
> **原理**：G1 调优核心是 MaxGCPauseMillis，G1 根据目标自动调整新生代大小。IHOP（默认45%）控制何时启动并发标记。Mixed GC 回收新生代+部分老年代 Region。ZGC 几乎不需调优，停顿与堆无关，主要关注堆是否足够（浮动垃圾需要更多空间）。Parallel 自适应调节 Eden/Survivor 大小。
>
> **用法要点**：① 先开 GC 日志用 GCEasy 分析，不盲目调参；② Full GC 频繁原因：内存泄漏、大对象、元空间不足、System.gc()；③ 停顿过长：调小 MaxGCPauseMillis、增大堆、减少大对象；④ 吞吐量低：用 Parallel 或增大停顿目标；⑤ 不设 -Xmn 让 G1 自适应；⑥ 迭代调优每次改一个参数。

### 3.4 内存分析工具

```bash
jps -l                           # 查看 Java 进程
jstat -gcutil <pid> 1000 10      # GC 统计
jmap -heap <pid>                 # 堆配置
jmap -dump:format=b,file=heap.hprof <pid>  # 堆转储
jmap -histo <pid> | head -20     # 对象统计
jstack <pid> > thread.txt        # 线程栈
jstack -l <pid>                  # 含锁信息（检测死锁）
jcmd <pid> Thread.print          # jcmd 综合工具（推荐）
jcmd <pid> GC.heap_dump heap.hprof
jcmd <pid> VM.flags
```

> 🔍 **知识点深度解析**
>
> **作用**：JDK 命令行工具是排查 JVM 问题的瑞士军刀。jps 定位进程，jstat 监控 GC，jmap 分析堆，jstack 分析线程，jcmd 是综合工具。
>
> **原理**：基于 Attach API 或 JMX 与目标 JVM 连接。jstack 通过 ThreadMXBean 获取线程栈，能自动检测死锁。jmap -histo 触发 GC 后统计存活对象，-dump 生成 HPROF 文件（MAT 分析）。jcmd 是 JDK 8 统一诊断命令，整合 jmap/jstack/jstat。jmap -dump 会触发 STW。
>
> **用法要点**：① 生产优先用 jcmd；② jstack 多次采样对比线程状态；③ jmap -histo:live 触发 Full GC 注意影响；④ 堆转储用 MAT 分析支配树、泄漏嫌疑、GC Roots；⑤ 容器内执行；⑥ jcmd <pid> help 查看命令。

### 3.5 反射与类操作

```java
Class<?> clazz = Class.forName("com.example.User");
User user = (User) clazz.getDeclaredConstructor().newInstance();

Field field = clazz.getDeclaredField("name");
field.setAccessible(true);
field.set(user, "张三");

Method method = clazz.getDeclaredMethod("setName", String.class);
method.setAccessible(true);
method.invoke(user, "李四");

if (clazz.isAnnotationPresent(Component.class)) {
    Component anno = clazz.getAnnotation(Component.class);
}
```

> 🔍 **知识点深度解析**
>
> **作用**：反射是 Java 动态性核心，运行时获取类信息、创建对象、调用方法、访问字段。是 Spring、MyBatis、JUnit 等框架的基础。
>
> **原理**：Class 对象是方法区类信息入口，包含所有元数据。反射调用先做安全检查（setAccessible 跳过），再通过本地方法访问。反射比直接调用慢10-100倍（安全检查、查找、装箱、无法内联）。JVM 有 Inflation 优化：前15次 JNI 调用，之后生成字节码转为直接调用。MethodHandle 更轻量。
>
> **用法要点**：① 缓存 Method/Field 但注意阻止类卸载；② setAccessible 只是跳过访问检查，不修改修饰符；③ 业务代码避免反射；④ GraalVM Native Image 需 reflect-config；⑤ 性能敏感用 MethodHandle 或 ByteBuddy；⑥ 泛型用 getGenericReturnType()。

### 3.6 字节码操作

```java
ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_FRAMES);
cw.visit(Opcodes.V1_8, Opcodes.ACC_PUBLIC, "com/example/Generated",
         null, "java/lang/Object", null);

MethodVisitor mv = cw.visitMethod(Opcodes.ACC_PUBLIC, "<init>", "()V", null, null);
mv.visitVarInsn(Opcodes.ALOAD, 0);
mv.visitMethodInsn(Opcodes.INVOKESPECIAL, "java/lang/Object", "<init>", "()V", false);
mv.visitInsn(Opcodes.RETURN);
mv.visitMaxs(1, 1);
mv.visitEnd();

byte[] bytes = cw.toByteArray();
```

> 🔍 **知识点深度解析**
>
> **作用**：字节码操作允许动态生成/修改类，是 AOP、ORM、热部署、代码混淆、性能监控的底层技术。ASM 是最流行的库。
>
> **原理**：.class 文件格式严格定义（魔数、版本、常量池、字段、方法、属性）。ASM 用访问者模式逐段生成。字节码是基于栈的指令集（ALOAD、INVOKESPECIAL、ARETURN）。COMPUTE_FRAMES 自动计算 StackMapTable。
>
> **用法要点**：① ASM Core API 轻量，Tree API 方便修改；② 动态生成类用自定义 ClassLoader 加载；③ 用 ASMifier 反编译学习；④ CGLIB 基于 ASM，生成子类实现 AOP（不能代理 final）；⑤ Spring 5+ 用 ByteBuddy；⑥ Java Agent + Instrumentation 实现加载时增强。

### 3.7 OOM 与 StackOverflow 排查

```bash

> 🔍 **知识点深度解析**
>
> **作用**：OOM 和 StackOverflow 是 JVM 常见内存错误，需根据错误类型定位原因并修复。
>
> **原理**：OOM 类型：Java heap space（堆内存不足，内存泄漏或堆太小，用 MAT 分析 dump）、Metaspace（类加载过多/泄漏，检查动态类生成）、GC overhead limit（GC 耗时占比>98% 但回收<2%）、Direct buffer memory（直接内存不足，NIO/Netty）、unable to create native thread（线程数超限）。StackOverflow：递归过深或方法调用链太长。排查：jmap dump + MAT 分析 dominator tree，jstack 看线程。
>
> **用法要点**：① Heap OOM：MAT 分析 dominator tree 找大对象和泄漏点  ② Metaspace OOM：检查 CGLIB/动态代理/热部署类加载泄漏  ③ GC overhead：98% 时间 GC 但只回收 2%，通常是堆快满了  ④ StackOverflow：检查递归终止条件和调用深度  ⑤ 面试常考：OOM 类型、MAT 分析、jstack/jmap 用法、内存泄漏定位

# 堆 OOM：jmap -dump 生成堆转储，MAT 分析支配树
# 元空间 OOM：jmap -clstats 查看类加载统计
# 栈溢出：看异常栈重复方法（递归死循环），增大 -Xss
# 直接内存 OOM：检查 DirectByteBuffer/Netty，-XX:MaxDirectMemorySize
```

> 🔍 **知识点深度解析**
>
> **作用**：OOM 是生产最常见 JVM 问题，快速定位类型和原因是必备技能。
>
> **原理**：堆 OOM=对象分配不足且 GC 后无法回收。元空间 OOM=类元数据超限。StackOverflow=栈深度超 -Xss。直接内存 OOM=DirectByteBuffer 超 MaxDirectMemorySize（默认=-Xmx）。排查核心：HeapDumpOnOutOfMemoryError 保留现场，MAT 支配树找内存大户，Path to GC Roots 分析无法回收原因。
>
> **用法要点**：① 必设 HeapDumpOnOutOfMemoryError；② 大堆转储用 MAT 注意内存；③ 内存泄漏特征：每次操作内存上涨 GC 不降；④ StackOverflow 看重复方法（99%递归）；⑤ 容器 OOM 可能是 limits 限制；⑥ OOM 后进程可能还在。

### 3.8 JFR 飞行记录器

```bash

> 🔍 **知识点深度解析**
>
> **作用**：JFR（Java Flight Recorder）是 JDK 内置的低开销性能采集工具，持续记录 JVM 运行时事件用于诊断。
>
> **原理**：JFR 采集线程调度、GC、锁竞争、IO、方法采样等事件，开销 <1%，可在生产环境常开。启动时 -XX:StartFlightRecording=duration=60s,filename=app.jfr，运行时 jcmd <pid> JFR.start/start/dump。用 JMC（JDK Mission Control）可视化分析。JFR 适合生产环境性能分析，比传统 profiler 开销低得多。
>
> **用法要点**：① -XX:StartFlightRecording 启动时开启，jcmd 运行时控制  ② 开销 <1%，可生产环境常开  ③ JMC 可视化分析：GC/锁/IO/方法热点  ④ jcmd <pid> JFR.dump 导出当前记录  ⑤ 面试常考：JFR 原理、与 async-profiler 对比、生产性能分析

# 启动时开启
java -XX:StartFlightRecording:filename=recording.jfr,duration=60s -jar app.jar

# 运行时录制
jcmd <pid> JFR.start name=myrec duration=60s filename=recording.jfr
jcmd <pid> JFR.dump name=myrec filename=recording.jfr
jcmd <pid> JFR.stop name=myrec
jcmd <pid> JFR.check
```

> 🔍 **知识点深度解析**
>
> **作用**：JFR 是 JVM 内置低开销性能分析工具，记录 CPU/内存/GC/线程/锁/IO 近百种事件，开销<1%，可生产长时间运行。
>
> **原理**：基于 JVM 事件系统，关键执行点埋点，数据写入环形缓冲区，定时 dump 到 .jfr。优化：紧凑二进制、异步写入、采样而非全量。JDK 11 开源。JMC 可视化分析（火焰图、GC 时间线、锁竞争、热点方法）。
>
> **用法要点**：① 开销<1% 可生产持续运行；② jcmd 动态开启不需重启；③ 性能问题用 profile 配置；④ 定位 CPU 热点/GC/锁竞争/内存分配/线程阻塞；⑤ JMC 打开 .jfr；⑥ 持续录制设 maxAge/maxSize。

---


---
## 4. 注意事项

1. **堆大小 Xms=Xmx**：避免动态扩容 STW。根据业务对象存活量和 GC 停顿目标合理设置。

2. **GC 收集器选择**：JDK 8 默认 Parallel，JDK 9+ 默认 G1。低延迟用 G1/ZGC，大堆 G1，超大堆 ZGC。CMS 已废弃。

3. **OOM 自动 dump**：必设 -XX:+HeapDumpOnOutOfMemoryError 和 HeapDumpPath。

4. **元空间上限**：JDK 8+ 元空间用本地内存默认无上限，生产必设 MaxMetaspaceSize。

5. **System.gc() 影响**：触发 Full GC（STW），用 -XX:+DisableExplicitGC 禁用。

6. **类加载器内存泄漏**：自定义加载器/热部署/CGLIB 可能导致类无法卸载，确保 ClassLoader 可回收。

7. **finalize 已废弃**：JDK 9 @Deprecated，用 try-with-resources 或 Cleaner 替代。

8. **TLAB 优化**：每个线程 Eden 私有分配区，避免分配锁竞争。默认开启。

9. **GC 日志必开**：JDK 9+ 用 -Xlog:gc*，滚动文件。没有日志等于盲调。

10. **直接内存监控**：NIO DirectByteBuffer 用堆外内存，设 MaxDirectMemorySize 限制。

11. **JIT 编译阈值**：C1默认1500次，C2默认10000次。微基准要预热，用 JMH。

12. **对象晋升年龄**：Survivor 熬过 GC 年龄+1，MaxTenuringThreshold 默认15晋升。动态年龄：相同年龄对象超 Survivor 50% 则≥该年龄直接晋升。

---

> 💡 **深度讲解**：JVM 核心价值是"自动内存管理+跨平台执行"。分代 GC 基于绝大多数对象朝生夕死，新生代复制算法，老年代标记整理。G1 把堆分成 Region，按可预测停顿优先回收垃圾最多的 Region。ZGC 用着色指针+读屏障实现亚毫秒停顿。双亲委派保证核心类库安全。JIT 编译+逃逸分析让 Java 性能媲美 C++。
>
> **📝 精简总结**：JVM 内存分线程共享（堆+方法区/元空间）和私有（栈+PC+本地栈）；类加载五阶段+双亲委派；GC 可达性分析+分代收集，选 G1/ZGC；调优靠堆大小+GC日志+MAT/jcmd；注意 OOM dump、元空间上限、System.gc 禁用、直接内存监控、JIT 预热。

---

> 📋 **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 知识点深度解析」模块（作用+原理+用法要点），新增了 JVM 内存区域划分图解，原有内联图已统一风格化美化。所有原有内容完整保留，未做任何修改。
