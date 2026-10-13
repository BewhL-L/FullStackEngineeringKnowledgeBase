---
title: Linux 内核基础概念
tags: [计算机基础, Linux, 内核, 原子笔记]
category: 计算机基础
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[操作系统核心概念]]", "[[计算机网络分层模型速查]]"]
aliases: [Linux内核基础概念]
---

# Linux 内核基础概念

> **文档说明**：系统讲解 Linux 内核的核心架构与基础概念，包括内核设计哲学、进程管理与调度、内存管理（虚拟内存/分页/伙伴系统/Slab）、文件系统（VFS/ext4）、设备驱动模型、系统调用与中断、网络协议栈、并发与同步（锁/原子操作/RCU），以及内核调试与性能分析工具，含丰富的命令示例和常见问题排查。
>
> **适用人群**：全栈工程师、后端开发者、运维工程师、希望深入理解 Linux 系统的开发者
>
> **前置知识**：[[操作系统核心概念]]、[[计算机网络分层模型速查]]

---

## 一、概述

**Linux 内核**是 Linux 操作系统的核心，负责管理硬件资源、提供系统调用接口、调度进程、管理内存和文件系统等。它是一个宏内核（Monolithic Kernel）设计，同时借鉴了微内核的一些思想（如可加载内核模块）。

### 1. Linux 内核是什么

| 特性 | 说明 |
|------|------|
| **类型** | 宏内核（Monolithic Kernel）+ 可加载模块 |
| **语言** | C（核心）+ 汇编（架构相关） |
| **许可证** | GPL v2 |
| **创始人** | Linus Torvalds（1991 年） |
| **最新稳定版** | 6.x（2026） |
| **代码量** | 约 3000 万行（含驱动） |
| **支持架构** | x86/x86_64、ARM、ARM64、RISC-V、PowerPC、MIPS 等 |

### 2. 内核 vs 用户空间

```text
┌─────────────────────────────────────────┐
│              用户空间 (User Space)        │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │ Shell│ │  Web │ │  App │ │  DB  │  │
│  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘  │
│     └─────────┴─────────┴─────────┘      │
│              glibc / 系统库                │
└───────────────────┬───────────────────────┘
                    │ 系统调用 (syscall)
┌───────────────────▼───────────────────────┐
│              内核空间 (Kernel Space)        │
│  ┌──────────────────────────────────────┐  │
│  │  系统调用接口 (syscall interface)    │  │
│  ├──────────────────────────────────────┤  │
│  │  进程管理  │  内存管理  │  文件系统  │  │
│  │  (Scheduler)│ (VM)     │  (VFS)    │  │
│  ├──────────────────────────────────────┤  │
│  │  网络协议栈  │  设备驱动  │  中断管理 │  │
│  │  (TCP/IP)   │  (Drivers)│  (IRQ)   │  │
│  ├──────────────────────────────────────┤  │
│  │  架构相关代码 (x86/ARM/...)          │  │
│  └──────────────────────────────────────┘  │
└───────────────────────────────────────────┘
                    │
┌───────────────────▼───────────────────────┐
│                硬件 (Hardware)              │
│   CPU  │  内存  │  磁盘  │  网卡  │ 外设  │
└───────────────────────────────────────────┘
```

| 维度 | 用户空间 | 内核空间 |
|------|---------|---------|
| **权限** | Ring 3（非特权） | Ring 0（特权） |
| **可访问资源** | 受限，需通过系统调用 | 全部硬件资源 |
| **内存** | 独立虚拟地址空间 | 共享内核地址空间 |
| **崩溃影响** | 只影响当前进程 | 系统崩溃（Kernel Panic） |
| **示例** | Shell、浏览器、数据库 | 进程调度、内存管理、驱动 |

### 3. 内核设计哲学

| 原则 | 说明 |
|------|------|
| **一切皆文件** | 设备、管道、套接字都通过文件接口访问 |
| **机制与策略分离** | 内核提供机制（如调度器），策略由用户空间决定 |
| **可移植性** | 架构相关代码与通用代码分离，支持多种 CPU 架构 |
| **模块化** | 功能可编译为内核模块，按需加载 |
| **性能优先** | 高度优化的数据结构和算法，追求极致性能 |
| **向后兼容** | 系统调用接口保持稳定，不破坏用户空间程序 |

---

## 二、进程管理与调度

### 1. 进程与线程

| 概念 | 说明 |
|------|------|
| **进程（Process）** | 资源分配的最小单位，拥有独立的地址空间、文件描述符、信号处理等 |
| **线程（Thread）** | CPU 调度的最小单位，同一进程内的线程共享地址空间和资源 |
| **轻量级进程（LWP）** | Linux 中线程的实现方式，每个线程对应一个 task_struct |
| **PID** | 进程 ID，全局唯一 |
| **TGID** | 线程组 ID，同一进程的线程 TGID 相同（等于主线程 PID） |

**进程状态**：
| 状态 | 符号 | 说明 |
|------|------|------|
| 运行态 | R | 正在 CPU 上运行或在运行队列中等待 |
| 可中断睡眠 | S | 等待事件，可被信号唤醒 |
| 不可中断睡眠 | D | 等待 I/O 完成，不可被信号唤醒 |
| 停止态 | T | 被信号（如 SIGSTOP）停止 |
| 僵尸态 | Z | 进程已结束，但父进程未回收资源 |
| 死亡态 | X | 进程即将被销毁 |

```bash
# 查看进程状态
ps aux
ps -eo pid,ppid,state,comm --sort=-pid | head -20

# 查看进程树
pstree -p

# 查看线程
ps -eLf | grep <pid>
top -H -p <pid>
```

### 2. task_struct 内核结构

Linux 中每个进程/线程由 `task_struct` 描述（定义在 `include/linux/sched.h`）：

```c
struct task_struct {
    volatile long state;          // 进程状态
    void *stack;                  // 栈指针
    pid_t pid;                    // 进程 ID
    pid_t tgid;                   // 线程组 ID
    struct task_struct __rcu *parent;  // 父进程
    struct list_head children;    // 子进程链表
    struct list_head sibling;     // 兄弟进程链表
    struct mm_struct *mm;         // 内存描述符（用户空间地址空间）
    struct files_struct *files;   // 文件描述符表
    struct fs_struct *fs;         // 文件系统信息
    struct signal_struct *signal; // 信号处理
    struct sighand_struct *sighand;
    const struct sched_class *sched_class;  // 调度器类
    struct sched_entity se;       // 调度实体（CFS）
    struct sched_rt_entity rt;    // 实时调度实体
    int prio;                     // 动态优先级
    int static_prio;              // 静态优先级
    int normal_prio;              // 正常优先级
    unsigned int rt_priority;     // 实时优先级
    cpumask_t cpus_allowed;       // 允许运行的 CPU
    unsigned int time_slice;      // 时间片
    struct cred *cred;            // 凭证（UID/GID/权限）
    char comm[TASK_COMM_LEN];     // 进程名
    // ... 还有很多字段
};
```

### 3. 进程调度器

Linux 内核使用**模块化调度器**，不同类型的进程使用不同的调度类：

| 调度类 | 优先级 | 说明 | 适用进程 |
|--------|--------|------|---------|
| **stop_sched_class** | 最高 | 停止类，用于 CPU 热插拔 | 内核线程 |
| **dl_sched_class** | 高 | 截止时间调度（Deadline） | 有明确截止时间的实时任务 |
| **rt_sched_class** | 高 | 实时调度（FIFO/RR） | 实时进程 |
| **fair_sched_class（CFS）** | 普通 | 完全公平调度器 | 普通进程（默认） |
| **idle_sched_class** | 最低 | 空闲调度 | idle 进程（CPU 空闲时运行） |

**CFS（完全公平调度器）**：
- 核心思想：每个进程公平分享 CPU 时间
- 使用红黑树（rbtree）管理调度实体，按 `vruntime`（虚拟运行时间）排序
- `vruntime` 越小，优先级越高，越先被调度
-  nice 值影响 `vruntime` 增长速度（nice 越低，增长越慢，获得 CPU 越多）

```bash
# 查看调度策略
chrt -p <pid>

# 设置实时调度策略
chrt -f -p 99 <pid>   # SCHED_FIFO，优先级 99
chrt -r -p 50 <pid>   # SCHED_RR，优先级 50

# 查看 CFS 调度信息
cat /proc/<pid>/sched

# nice 值调整
nice -n 10 command      # 启动时设置 nice
renice -n 5 -p <pid>    # 运行中调整
```

### 4. 进程创建

Linux 进程创建通过 `fork()`（复制）和 `exec()`（替换）组合实现：

```text
fork() → 子进程复制父进程地址空间（写时复制 COW）
  ↓
exec() → 子进程加载新程序，替换地址空间
  ↓
新程序运行
```

```bash
# 系统调用跟踪
strace -f -e trace=process ls

# 查看进程系统调用
strace -p <pid>
```

---

## 三、内存管理

### 1. 虚拟内存

Linux 使用**虚拟内存**机制，每个进程拥有独立的虚拟地址空间，通过页表映射到物理内存。

| 地址空间 | 大小（64位） | 说明 |
|---------|-------------|------|
| 用户空间 | 0 ~ 0x00007FFFFFFFFFFF（128TB） | 进程独立，互不可见 |
| 内核空间 | 0xFFFF800000000000 ~ （128TB） | 所有进程共享 |

**用户空间内存布局**（从低地址到高地址）：
```text
┌─────────────────────┐ 高地址
│   命令行参数和环境变量  │
├─────────────────────┤
│       栈 (Stack)       │ ← 向下增长
│                       │
├─────────────────────┤
│     共享库映射区        │
├─────────────────────┤
│       堆 (Heap)        │ ← 向上增长
├─────────────────────┤
│   BSS 段（未初始化数据） │
├─────────────────────┤
│   数据段（已初始化数据） │
├─────────────────────┤
│   代码段（Text）       │
└─────────────────────┘ 低地址
```

```bash
# 查看进程内存映射
cat /proc/<pid>/maps
pmap -x <pid>

# 查看内存使用
free -h
cat /proc/meminfo

# 查看进程内存状态
cat /proc/<pid>/status | grep -E "Vm|Threads"
```

### 2. 分页机制

虚拟内存通过**分页**管理，虚拟地址分为页号和页内偏移，通过页表查找物理页框。

| 概念 | 说明 |
|------|------|
| **页（Page）** | 虚拟内存的最小单位，通常 4KB |
| **页框（Page Frame）** | 物理内存的最小单位，与页大小相同 |
| **页表（Page Table）** | 虚拟页号到物理页框号的映射表 |
| **TLB** |  Translation Lookaside Buffer，页表缓存，加速地址翻译 |
| **大页（HugePage）** | 2MB/1GB 页，减少 TLB miss，提升性能 |

**多级页表**（x86_64 使用 4 级页表）：
```text
虚拟地址 → PGD → PUD → PMD → PTE → 物理页框
         (全局目录)(上级目录)(中间目录)(页表项)
```

```bash
# 查看页大小
getconf PAGESIZE

# 大页配置
cat /proc/meminfo | grep Huge
echo 1024 > /proc/sys/vm/nr_hugepages  # 设置大页数量

# 查看 TLB 信息（需 perf）
perf stat -e dTLB-load-misses,iTLB-load-misses <command>
```

### 3. 伙伴系统（Buddy System）

物理内存分配使用**伙伴系统**，以 2 的幂次大小分配页框，减少外部碎片。

| 概念 | 说明 |
|------|------|
| **分配粒度** | 2^n 个连续页框（0~10 阶，即 4KB~4MB） |
| **伙伴合并** | 释放时如果相邻的伙伴块也空闲，则合并为更大的块 |
| **优点** | 快速分配连续物理页，减少外部碎片 |
| **缺点** | 内部碎片（分配 2^n 但只用一部分） |

```bash
# 查看伙伴系统信息
cat /proc/buddyinfo
cat /proc/pagetypeinfo
```

### 4. Slab 分配器

Slab 分配器用于**小对象**的内存分配（如 task_struct、inode 等内核数据结构），在伙伴系统之上构建。

| 概念 | 说明 |
|------|------|
| **Slab** | 由一个或多个连续页框组成，包含多个相同大小的对象 |
| **Cache** | 同类对象的 Slab 集合（如 task_struct_cache） |
| **对象** | 缓存的具体数据结构 |
| **优点** | 避免伙伴系统的内部碎片，对象复用，构造/析构开销小 |
| **SLUB** | Linux 默认的 Slab 实现（2.6.23+），更简单高效 |

```bash
# 查看 Slab 信息
cat /proc/slabinfo
slabtop  # 实时显示 Slab 使用情况

# 查看内存分配统计
cat /proc/vmstat
```

### 5. 页面回收与交换

当内存不足时，内核通过以下方式回收内存：

| 机制 | 说明 |
|------|------|
| **页面回收（Page Reclaim）** | 回收不活跃的文件页和匿名页 |
| **交换（Swap）** | 将不活跃的匿名页写入交换分区/文件 |
| **OOM Killer** | 内存严重不足时，杀死进程释放内存 |
| **kswapd** | 内核线程，后台异步回收内存 |
| **direct reclaim** | 进程直接回收内存（同步，可能导致卡顿） |

```bash
# 查看 Swap 使用
swapon -s
free -h

# 创建 Swap 文件
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# OOM 配置
cat /proc/sys/vm/oom_kill_allocating_task
echo 1 > /proc/<pid>/oom_score_adj  # 调整进程 OOM 优先级（-1000~1000）

# 查看内存回收统计
grep -E "pgscan|pgsteal|pgfault" /proc/vmstat
```

---

## 四、文件系统

### 1. VFS（虚拟文件系统）

VFS 是 Linux 文件系统的抽象层，为用户空间提供统一的文件操作接口，同时支持多种具体文件系统（ext4、xfs、btrfs、nfs 等）。

```text
用户空间 → open()/read()/write()
    ↓
VFS（虚拟文件系统）
    ↓
┌──────┬──────┬──────┬──────┐
│ ext4 │ xfs  │ btrfs│ nfs  │ ... 具体文件系统
└──────┴──────┴──────┴──────┘
    ↓
块设备层 → 磁盘驱动 → 硬件
```

**VFS 核心对象**：
| 对象 | 说明 |
|------|------|
| **super_block** | 文件系统超级块，描述整个文件系统 |
| **inode** | 索引节点，描述文件的元数据（大小、权限、时间、数据块位置） |
| **dentry** | 目录项，描述文件名与 inode 的映射 |
| **file** | 打开的文件，描述进程与文件的交互状态 |

```bash
# 查看文件系统类型
df -T
mount | column -t

# 查看 inode 使用
df -i
stat <filename>  # 查看文件 inode 信息

# 查看挂载的文件系统
cat /proc/mounts
cat /proc/filesystems  # 支持的文件系统类型
```

### 2. ext4 文件系统

ext4 是 Linux 最常用的文件系统，是 ext3 的改进版。

| 特性 | 说明 |
|------|------|
| **最大文件大小** | 16TB（4KB 块） |
| **最大文件系统大小** | 1EB |
| **日志** | 日志式文件系统，崩溃后快速恢复 |
| **Extents** | 连续数据块管理，减少碎片，提升大文件性能 |
| **延迟分配** | 先分配空间，实际写入时才分配块，减少碎片 |
| **多块分配** | 一次分配多个块，提升分配效率 |
| **纳秒时间戳** | 时间精度从秒提升到纳秒 |

```bash
# 创建 ext4 文件系统
mkfs.ext4 /dev/sdX
mkfs.ext4 -b 4096 -L mylabel /dev/sdX  # 指定块大小和标签

# 检查修复
fsck /dev/sdX
e2fsck -f /dev/sdX

# 查看文件系统信息
dumpe2fs /dev/sdX | head -50
tune2fs -l /dev/sdX

# 调整参数
tune2fs -m 1 /dev/sdX  # 调整保留块百分比
tune2fs -O ^has_journal /dev/sdX  # 关闭日志
```

### 3. 文件描述符

文件描述符（File Descriptor）是进程打开文件的索引，指向内核中的 file 结构。

| FD | 说明 |
|----|------|
| 0 | stdin（标准输入） |
| 1 | stdout（标准输出） |
| 2 | stderr（标准错误） |
| 3+ | 其他打开的文件/套接字/管道 |

```bash
# 查看进程打开的文件描述符
ls -la /proc/<pid>/fd
lsof -p <pid>

# 查看文件描述符限制
ulimit -n
cat /proc/sys/fs/file-max  # 系统级最大文件描述符数

# 修改限制
ulimit -n 65535  # 当前会话
# 永久修改：/etc/security/limits.conf
# * soft nofile 65535
# * hard nofile 65535
```

---

## 五、系统调用与中断

### 1. 系统调用

系统调用是用户空间程序请求内核服务的接口，通过软中断（x86 上为 `syscall` 指令）从用户态陷入内核态。

| 类别 | 示例系统调用 |
|------|------------|
| **进程控制** | fork, exec, exit, wait, clone |
| **文件操作** | open, read, write, close, lseek, stat |
| **内存管理** | mmap, munmap, brk, mprotect |
| **网络** | socket, bind, listen, accept, connect, send, recv |
| **信号** | kill, sigaction, sigprocmask |
| **时间** | time, gettimeofday, clock_gettime |
| **其他** | ioctl, fcntl, pipe, dup |

```bash
# 跟踪系统调用
strace -c ls  # 统计系统调用
strace -e trace=open,read,write cat file  # 跟踪特定系统调用
strace -f -p <pid>  # 跟踪进程及其子进程

# 查看系统调用号
ausyscall --dump | head -20
```

### 2. 中断

中断是硬件或软件向 CPU 发送的信号，要求 CPU 暂停当前工作处理中断事件。

| 类型 | 说明 | 示例 |
|------|------|------|
| **硬件中断** | 外设发送的中断 | 网卡收包、磁盘 I/O 完成、键盘输入 |
| **软中断** | 内核延迟处理的中断下半部 | 网络协议栈处理、定时器 |
| **异常** | CPU 执行指令时产生的错误 | 缺页异常、除零错误、非法指令 |
| **系统调用** | 用户态主动陷入内核态 | syscall 指令 |

**中断处理分为两部分**：
- **上半部（Top Half）**：快速响应，记录硬件状态，触发下半部
- **下半部（Bottom Half）**：延迟处理耗时操作，可被中断
  - softirq（软中断）：高优先级，可并发
  - tasklet：基于 softirq，同类型不并发
  - workqueue：进程上下文，可睡眠

```bash
# 查看中断统计
cat /proc/interrupts
cat /proc/softirqs

# 查看中断亲和性
cat /proc/irq/<irq_number>/smp_affinity

# 设置中断亲和性（将中断绑定到指定 CPU）
echo 2 > /proc/irq/<irq_number>/smp_affinity  # 绑定到 CPU1

# 查看软中断统计
cat /proc/stat | grep softirq
```

---

## 六、网络协议栈

Linux 内核实现了完整的 TCP/IP 协议栈，从网卡驱动到应用层 Socket 接口。

```text
应用层 → Socket API (syscall)
    ↓
传输层 → TCP / UDP / SCTP
    ↓
网络层 → IP (IPv4/IPv6) / ICMP / 路由
    ↓
链路层 → ARP / 邻居子系统 / 网卡驱动
    ↓
物理层 → 网卡硬件
```

### 1. 关键数据结构

| 结构 | 说明 |
|------|------|
| **socket** | 套接字，网络通信的端点 |
| **sock** | 内核中的 socket 表示 |
| **sk_buff（skb）** | 套接字缓冲区，描述网络数据包 |
| **net_device** | 网络设备，描述网卡 |
| **rtable** | 路由表项 |
| **neighbour** | 邻居表项（ARP 缓存） |

### 2. 数据包接收流程

```text
网卡收到数据包 → DMA 到内存 → 硬件中断
    ↓
上半部：分配 skb，标记有数据到达，触发软中断
    ↓
软中断（NET_RX_SOFTIRQ）：NAPI 轮询收包
    ↓
链路层：解析以太网头，VLAN 处理
    ↓
网络层：IP 头解析，路由查找，防火墙（iptables/nftables）
    ↓
传输层：TCP/UDP 头解析，查找对应 socket
    ↓
放入 socket 接收队列
    ↓
应用程序通过 recv/read 读取
```

### 3. 网络性能优化

```bash
# 查看网络统计
cat /proc/net/dev
ss -s
netstat -s

# 查看 TCP 连接状态
ss -tan state established
ss -tan state time-wait | wc -l

# TCP 参数调优
cat /proc/sys/net/ipv4/tcp_tw_reuse      # TIME_WAIT 复用
cat /proc/sys/net/core/somaxconn          # 监听队列长度
cat /proc/sys/net/ipv4/tcp_max_syn_backlog  # SYN 队列长度

# 网卡多队列
ethtool -l eth0    # 查看队列数
ethtool -L eth0 combined 8  # 设置队列数

# RPS/RFS（软件接收包 Steering）
echo 7 > /sys/class/net/eth0/queues/rx-0/rps_cpus

# 网络带宽测试
iperf3 -s  # 服务端
iperf3 -c <server_ip>  # 客户端
```

---

## 七、并发与同步

### 1. 同步机制

Linux 内核提供多种同步机制，适用于不同场景：

| 机制 | 上下文 | 说明 | 适用场景 |
|------|--------|------|---------|
| **原子操作** | 任意 | 不可中断的单步操作 | 计数器、标志位 |
| **自旋锁（spinlock）** | 中断/原子 | 忙等待，不睡眠 | 短时间临界区，中断上下文 |
| **读写自旋锁（rwlock）** | 中断/原子 | 读共享、写独占 | 读多写少 |
| **信号量（semaphore）** | 进程 | 可睡眠，计数锁 | 长时间临界区 |
| **互斥锁（mutex）** | 进程 | 二值信号量，可睡眠 | 进程上下文互斥 |
| **读写信号量（rwsem）** | 进程 | 读共享、写独占，可睡眠 | 读多写少的进程上下文 |
| **RCU** | 读端任意/写端进程 | 读无锁，写延迟回收 | 读多写极少，读性能要求高 |
| **seqlock** | 读端任意/写端中断 | 写优先，读端重试 | 读多写少，写不能被读阻塞 |
| **completion** | 进程 | 等待事件完成 | 同步等待 |
| **wait_queue** | 进程 | 等待队列，条件等待 | 等待资源可用 |

### 2. 原子操作

```c
// 原子计数器
atomic_t counter = ATOMIC_INIT(0);
atomic_inc(&counter);       // 加 1
atomic_dec(&counter);       // 减 1
atomic_add(5, &counter);    // 加 5
int val = atomic_read(&counter);  // 读取

// 原子位操作
unsigned long flags = 0;
set_bit(0, &flags);    // 设置第 0 位
clear_bit(0, &flags);  // 清除第 0 位
test_bit(0, &flags);   // 测试第 0 位
```

### 3. 自旋锁

```c
// 基本自旋锁
spinlock_t lock;
spin_lock_init(&lock);

spin_lock(&lock);
// 临界区（短，不睡眠）
spin_unlock(&lock);

// 中断安全的自旋锁
unsigned long flags;
spin_lock_irqsave(&lock, flags);  // 保存中断状态并禁用中断
// 临界区
spin_unlock_irqrestore(&lock, flags);  // 恢复中断状态
```

### 4. Mutex

```c
struct mutex lock;
mutex_init(&lock);

mutex_lock(&lock);      // 获取锁（可睡眠）
// 临界区（可睡眠）
mutex_unlock(&lock);    // 释放锁

// 非阻塞获取
if (mutex_trylock(&lock)) {
    // 获取成功
    mutex_unlock(&lock);
}
```

```text
### 5. RCU（Read-Copy Update）
```

RCU 是 Linux 内核特有的高性能同步机制，读端完全无锁，写端通过复制修改、延迟回收实现。

```c
// 读端（无锁）
rcu_read_lock();
struct data *p = rcu_dereference(gp);
// 读取 p（不能睡眠）
rcu_read_unlock();

// 写端（复制-修改-替换）
struct data *new = kmalloc(sizeof(*new), GFP_KERNEL);
struct data *old = rcu_dereference_protected(gp, ...);
*new = *old;           // 复制
new->field = value;    // 修改
rcu_assign_pointer(gp, new);  // 原子替换
synchronize_rcu();     // 等待所有读端完成
kfree(old);            // 安全释放旧数据
```

```bash
# 查看锁竞争统计
cat /proc/lock_stat
lockstat  # 需内核开启 CONFIG_LOCK_STAT

# 查看 RCU 信息
cat /proc/rcu
```

---

## 八、内核模块

### 1. 模块基础

内核模块是可动态加载到内核的代码，扩展内核功能而不需重新编译内核。

```c
// hello.c - 最简单的内核模块
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

static int __init hello_init(void) {
    printk(KERN_INFO "Hello, Kernel!\n");
    return 0;
}

static void __exit hello_exit(void) {
    printk(KERN_INFO "Goodbye, Kernel!\n");
}

module_init(hello_init);
module_exit(hello_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("A simple kernel module");
```

```makefile
# Makefile
obj-m += hello.o
all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
```

```bash
# 编译
make

# 加载模块
insmod hello.ko
modprobe hello  # 自动处理依赖

# 查看已加载模块
lsmod
cat /proc/modules

# 查看模块信息
modinfo hello.ko

# 卸载模块
rmmod hello
modprobe -r hello

# 查看模块参数
ls /sys/module/hello/parameters/

# 查看模块日志
dmesg | tail -10
journalctl -k | tail -10
```

---

## 九、内核调试与性能分析

### 1. 内核日志

```bash
# 查看内核日志
dmesg
dmesg -T  # 带时间戳
dmesg -w  # 实时跟踪
dmesg --level=err,warn  # 只看错误和警告

# 系统日志
journalctl -k  # 内核日志
journalctl -k -f  # 实时跟踪
```

### 2. proc 文件系统

`/proc` 是内核暴露运行时信息的虚拟文件系统：

```bash
# 进程信息
/proc/<pid>/status    # 进程状态
/proc/<pid>/maps      # 内存映射
/proc/<pid>/fd        # 文件描述符
/proc/<pid>/io        # IO 统计
/proc/<pid>/sched     # 调度信息

# 系统信息
/proc/cpuinfo         # CPU 信息
/proc/meminfo         # 内存信息
/proc/version         # 内核版本
/proc/uptime          # 运行时间
/proc/loadavg         # 负载均衡
/proc/interrupts      # 中断统计
/proc/net/dev         # 网络统计
/proc/slabinfo        # Slab 信息
/proc/buddyinfo       # 伙伴系统信息
/proc/vmstat          # 虚拟内存统计
```

### 3. sysctl 内核参数

```bash
# 查看所有内核参数
sysctl -a | less

# 查看特定参数
sysctl kernel.hostname
sysctl net.ipv4.tcp_syncookies

# 临时修改
sysctl -w net.ipv4.tcp_syncookies=1

# 永久修改（/etc/sysctl.conf）
echo "net.ipv4.tcp_syncookies=1" >> /etc/sysctl.conf
sysctl -p  # 生效
```

### 4. 性能分析工具

| 工具 | 说明 | 示例 |
|------|------|------|
| **perf** | Linux 性能分析工具 | `perf top`, `perf record`, `perf report` |
| **ftrace** | 内核函数跟踪 | `trace-cmd`, `/sys/kernel/debug/tracing` |
| **bpftrace** | eBPF 高级跟踪 | `bpftrace -e 'tracepoint:syscalls:sys_enter_open { printf("%s\n", comm); }'` |
| **strace** | 系统调用跟踪 | `strace -c ls` |
| **ltrace** | 库函数跟踪 | `ltrace ls` |
| **gdb** | 调试器 | `gdb /usr/bin/ls` |
| **crash** | 内核崩溃转储分析 | `crash /usr/lib/debug/boot/vmlinux-$(uname -r) /var/crash/...` |
| **kdump** | 内核崩溃转储 | `systemctl status kdump` |
| **top/htop** | 进程监控 | `top`, `htop` |
| **vmstat** | 虚拟内存统计 | `vmstat 1` |
| **iostat** | IO 统计 | `iostat -xz 1` |
| **sar** | 系统活动报告 | `sar -u 1`, `sar -n DEV 1` |
| **free** | 内存使用 | `free -h` |
| **pidstat** | 进程统计 | `pidstat 1`, `pidstat -d 1` |

```bash
# perf 常用命令
perf top                      # 实时查看 CPU 热点函数
perf record -g -p <pid>      # 记录进程调用图
perf report                   # 分析记录结果
perf stat ls                  # 统计性能计数器
perf list                     # 列出可用事件

# bpftrace 示例（需安装 bpftrace）
bpftrace -e 'tracepoint:syscalls:sys_enter_read { @[comm] = count(); }'  # 统计 read 调用
bpftrace -e 'kprobe:do_sys_open { printf("%s: %s\n", comm, str(arg1)); }'  # 跟踪打开文件

# ftrace 示例
cd /sys/kernel/debug/tracing
echo function > current_tracer
echo do_fork > set_ftrace_filter
cat trace_pipe
```

### 5. Kernel Panic 排查

```bash
# 查看内核崩溃转储
ls /var/crash/
crash /usr/lib/debug/boot/vmlinux-$(uname -r) /var/crash/<timestamp>/vmcore

# kdump 配置
cat /etc/kdump.conf
systemctl status kdump
kdumpctl status

# 查看内核日志中的 Oops
dmesg | grep -i "oom\|panic\|oops\|bug"
journalctl -k | grep -i "oom\|panic\|oops"
```

---

## 十、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 系统负载高但 CPU 使用率低 | 进程处于 D 状态（不可中断睡眠，等待 I/O） | `ps aux | grep " D"`，检查磁盘 I/O（iostat） |
| 内存不足 OOM | 进程占用内存过多 / 内存泄漏 / 缓存未回收 | 查看 `dmesg | grep -i oom`，调整 `vm.swappiness`，增加内存 |
| 磁盘 I/O 瓶颈 | 磁盘性能不足 / 大量随机读写 | `iostat -xz 1` 查看 await/%util，使用 SSD，优化 IO 调度 |
| 网络丢包 | 网卡队列满 / 缓冲区不足 / 网络拥塞 | `cat /proc/net/dev` 查看 drop，调整 `net.core.rmem_max`，增加网卡队列 |
| TIME_WAIT 过多 | 短连接频繁关闭 | 启用 `tcp_tw_reuse`，调整 `tcp_fin_timeout`，使用长连接 |
| 进程僵死（D 状态） | 等待 I/O 完成（NFS/磁盘故障） | 检查存储设备，`cat /proc/<pid>/stack` 查看内核栈 |
| 僵尸进程（Z 状态） | 子进程结束父进程未 wait | 修复父进程代码，或重启父进程 |
| 文件描述符耗尽 | 进程打开文件过多未关闭 | `ulimit -n` 调整限制，检查 `lsof -p <pid>` 泄漏 |
| 内核 panic | 内核 bug / 硬件故障 / 驱动问题 | 查看 `kdump` 转储，`dmesg` 日志，升级内核/驱动 |
| 时钟漂移 | NTP 未同步 / 硬件时钟问题 | `chronyc tracking`，配置 NTP 同步 |
| 中断不均衡 | 中断都绑定到 CPU0 | 配置 `smp_affinity`，启用 irqbalance |
| 内存泄漏 | 内核模块/驱动泄漏 | `cat /proc/meminfo` 观察 Slab 增长，`slabtop` 定位 |
| 系统卡顿 | direct reclaim / 内存碎片 / 锁竞争 | `vmstat 1` 查看 si/so，`perf lock` 分析锁竞争 |
| 升级内核后无法启动 | 驱动不兼容 / initramfs 问题 | 回退旧内核，`dracut` 重建 initramfs |

---

## 十一、关联笔记

### 计算机基础
- [[操作系统核心概念]] · [[计算机网络分层模型速查]] · [[数据结构与算法核心]]
- [[计算机组成原理]] · [[进程与线程核心概念]] · [[虚拟内存与地址翻译]]

### 云原生与运维
- [[Docker-核心原理与镜像优化]] · [[K8s-核心概念与架构]] · [[Prometheus监控体系]]
- [[日志ELK栈]] · [[链路追踪-SkyWalking与Zipkin]] · [[Nginx-反向代理与负载均衡]]
- [[Linux常用命令速查]] · [[Linux性能调优实战]] · [[Shell脚本编程]]

### 后端
- [[高并发系统设计案例]] · [[高可用架构设计]] · [[Redis数据结构与应用场景]]
- [[消息队列-Kafka与RabbitMQ]]

### 安全
- [[Web安全-XSS-CSRF-SQL注入]] · [[JWT与OAuth2认证授权]]

### 导航
- [[MOC-计算机基础]] · [[MOC-云原生与运维]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[操作系统核心概念]] 操作系统基础 → 深入本文 Linux 内核基础概念 → 学习 [[计算机网络分层模型速查]] 网络协议栈 → 实践 [[Linux常用命令速查]] 和 [[Linux性能调优实战]] → 研究 [[Docker-核心原理与镜像优化]] 和 [[K8s-核心概念与架构]] 容器化技术 → 应用于 [[高并发系统设计案例]] 生产环境排查。

---

## 💡 全文深度讲解

本文系统梳理了Linux 内核基础概念的核心知识体系，从概述入手，深入进程管理与调度的底层机制，再通过内存管理掌握实战应用，最后涵盖常见问题与排查与关联笔记。学习时建议先建立整体认知，再动手实践，最后结合常见问题深化理解。

## 📝 全文精简总结

- **概述**：掌握本模块的核心概念与关键要点
- **进程管理与调度**：掌握本模块的核心概念与关键要点
- **内存管理**：掌握本模块的核心概念与关键要点
- **文件系统**：掌握本模块的核心概念与关键要点
- **系统调用与中断**：掌握本模块的核心概念与关键要点
- **网络协议栈**：掌握本模块的核心概念与关键要点
- **并发与同步**：掌握本模块的核心概念与关键要点
- **内核模块**：掌握本模块的核心概念与关键要点
- 其余3个模块涵盖进阶主题与拓展内容

