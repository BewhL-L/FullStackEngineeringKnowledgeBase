---
title: 计网 OS 八股知识点系统梳理
tags: [计算机基础, 计算机网络, 操作系统, 面试]
created: 2026-08-12
updated: 2026-08-12
---

# 计网/OS 八股知识点系统梳理（优化版）

> **文档说明**：本文档参照《Java知识点完整整合大全》排版风格，系统梳理计算机网络与操作系统核心八股知识点。包含概述、核心特性、常用用法、注意事项四大模块，辅以动态可视化解析图、深度讲解与精简总结。**优化版**在原有内容基础上，为每个知识点补充了作用、原理、用法的深度解析，并新增了知识点图解。

---

## 1. 概述

计算机网络是将分散的计算机通过通信链路连接起来，实现资源共享和信息交换的系统；操作系统是管理计算机硬件与软件资源的系统软件。两者是后端开发的基础理论，也是面试高频考点。

**核心定位**：
- 计算机网络：解决跨主机通信问题，定义数据传输的规则和协议
- 操作系统：管理 CPU、内存、I/O 等硬件资源，为应用提供运行环境
- 后端开发必须掌握：理解网络协议栈才能排查连接问题，理解 OS 才能优化性能

**知识体系**：

| 领域 | 核心考点 |
|------|---------|
| 计算机网络 | OSI 七层/TCP-IP 四层、TCP 三次握手/四次挥手、流量控制/拥塞控制、HTTP/HTTPS、DNS、WebSocket |
| 操作系统 | 进程/线程、进程调度、内存管理（分页/虚拟内存）、IO 模型、进程间通信、死锁 |

---


---
## 2. 核心特性

<div style="background:linear-gradient(135deg,#4facfe,#00f2fe);border-radius:16px;padding:24px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#1a1a2e;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes osiFlow{0%,100%{opacity:.7}50%{opacity:1}}.osi-layer{background:rgba(255,255,255,.35);border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.08);padding:8px 12px;margin:4px auto;font-size:12px;text-align:center;animation:osiFlow 2s ease-in-out infinite;font-weight:600}.osi-layer:nth-child(1){animation-delay:0s;width:85%}.osi-layer:nth-child(2){animation-delay:.2s;width:80%}.osi-layer:nth-child(3){animation-delay:.4s;width:75%}.osi-layer:nth-child(4){animation-delay:.6s;width:70%}.osi-layer:nth-child(5){animation-delay:.8s;width:65%}.osi-layer:nth-child(6){animation-delay:1s;width:60%}.osi-layer:nth-child(7){animation-delay:1.2s;width:55%}</style>
<div style="text-align:center;font-size:16px;font-weight:700;margin-bottom:16px;padding-bottom:12px;border-bottom:1.5px solid rgba(0,0,0,.1);letter-spacing:1px">OSI 七层模型（自上而下）</div>
<div class="osi-layer">应用层 — HTTP/FTP/DNS/SMTP</div>
<div class="osi-layer">表示层 — 加密/压缩/格式转换</div>
<div class="osi-layer">会话层 — 建立/管理/终止会话</div>
<div class="osi-layer">传输层 — TCP/UDP，端口寻址</div>
<div class="osi-layer">网络层 — IP/ICMP，路由选择</div>
<div class="osi-layer">数据链路层 — MAC/以太网，帧传输</div>
<div class="osi-layer">物理层 — 比特流，电气/光学信号</div>
</div>

### 2.1 TCP/IP 四层模型

实际应用中使用 TCP/IP 四层模型（将 OSI 上三层合并为应用层）：

| 层级 | 协议 | 数据单位 | 功能 |
|------|------|---------|------|
| 应用层 | HTTP、HTTPS、FTP、DNS、SMTP | 报文（Message） | 为应用提供网络服务 |
| 传输层 | TCP、UDP | 段（Segment）/ 数据报（Datagram） | 端到端通信，端口寻址 |
| 网络层 | IP、ICMP、ARP | 包（Packet） | 路由选择，IP 寻址 |
| 网络接口层 | Ethernet、Wi-Fi | 帧（Frame） | 物理传输，MAC 寻址 |

> 🔍 **知识点深度解析**
>
> **作用**：网络分层模型是理解计算机网络的基础，它将复杂的通信过程分解为独立的层次，每层只关注自己的职责，通过标准化接口与上下层交互。这使得不同厂商的设备可以互操作，也便于问题定位（哪层出问题就查哪层）。
>
> **原理**：数据发送时自上而下逐层封装（应用层数据→传输层加TCP头→网络层加IP头→链路层加MAC头→物理层转比特流），接收时自下而上逐层解封装。每层的数据单位不同：应用层报文、传输层段、网络层包、链路层帧。TCP/IP 四层是 OSI 七层的简化（应用层=OSI应用+表示+会话，网络接口层=OSI数据链路+物理）。封装的核心是"每层在数据前面加自己的头部"，解封装则逐层剥离头部。
>
> **用法要点**：① 面试常考 OSI 七层和 TCP/IP 四层的对应关系；② 数据封装过程是重点（发送方封装、接收方解封装）；③ 每层的典型协议和设备要记住：应用层(HTTP/DNS)、传输层(TCP/UDP/端口)、网络层(IP/路由器)、链路层(MAC/交换机)、物理层(网线/集线器)；④ 排查网络问题按层来：ping 测网络层、telnet 测传输层、curl 测应用层；⑤ MTU（最大传输单元）是链路层概念，以太网默认1500字节，超过则IP层分片。

### 2.2 TCP 协议核心机制

**三次握手（建立连接）**：
1. 客户端 → 服务端：SYN（seq=x），客户端进入 SYN_SENT
2. 服务端 → 客户端：SYN+ACK（seq=y, ack=x+1），服务端进入 SYN_RCVD
3. 客户端 → 服务端：ACK（ack=y+1），双方进入 ESTABLISHED

**为什么三次？** 两次无法确认客户端接收能力，四次浪费（服务端 SYN+ACK 可合并）。

**四次挥手（断开连接）**：
1. 客户端 → 服务端：FIN，客户端进入 FIN_WAIT_1
2. 服务端 → 客户端：ACK，服务端进入 CLOSE_WAIT，客户端进入 FIN_WAIT_2
3. 服务端 → 客户端：FIN，服务端进入 LAST_ACK
4. 客户端 → 服务端：ACK，客户端进入 TIME_WAIT（2MSL），服务端收到后关闭

> 🔍 **知识点深度解析**
>
> **作用**：TCP 是面向连接的可靠传输协议，三次握手确保双方都具备发送和接收能力，四次挥手确保双方数据都传输完毕再断开。这些机制是 TCP 可靠性的基础，也是面试必考点。
>
> **原理**：三次握手的本质是"双方各发一个 SYN 并确认对方的 SYN"，需要三次是因为服务端的 SYN 和 ACK 可以合并发送（第二次），而客户端只需单独发 ACK（第三次）。两次握手的问题：服务端无法确认客户端是否收到了 SYN+ACK（可能客户端已失效，服务端却建立了连接，浪费资源）。四次挥手是因为 TCP 是全双工的，双方都要单独关闭自己的发送通道：客户端发 FIN 表示"我发完了"，服务端发 ACK 确认，然后服务端发 FIN 表示"我也发完了"，客户端发 ACK 确认。TIME_WAIT（2MSL，约1-4分钟）是为了：① 确保最后一个 ACK 能到达（丢了则服务端重发 FIN）；② 让本次连接的所有数据包在网络中消失，避免影响新连接。
>
> **用法要点**：① 三次握手为什么不是两次/四次——经典面试题；② 四次挥手为什么不能三次——因为服务端可能还有数据要发，FIN 和 ACK 不能合并；③ TIME_WAIT 过多的问题：高并发服务端可能出现大量 TIME_WAIT 占用端口，用 net.ipv4.tcp_tw_reuse=1 解决；④ SYN Flood 攻击：攻击者发大量 SYN 不回 ACK，服务端 SYN_RCVD 队列耗尽，用 syncookies 防御；⑤ 服务端 CLOSE_WAIT 过多说明应用没关闭连接（代码 bug）。

<div style="background:linear-gradient(135deg,#4facfe,#00f2fe);border-radius:14px;padding:18px;margin:14px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#1a1a2e;overflow:hidden;box-shadow:0 6px 20px rgba(0,0,0,.12)">
<style>@keyframes handshake{0%{transform:translateX(-10px);opacity:0}50%{opacity:1}100%{transform:translateX(10px);opacity:0}}.hs-msg{background:rgba(255,255,255,.35);border-radius:6px;padding:4px 10px;font-size:11px;margin:3px 0;display:inline-block;animation:handshake 2.5s ease-in-out infinite;font-weight:600}.hs-msg:nth-child(2){animation-delay:.5s}.hs-msg:nth-child(3){animation-delay:1s}</style>
<div style="text-align:center;font-size:13px;font-weight:700;margin-bottom:10px">TCP 三次握手</div>
<div style="display:flex;justify-content:space-between;font-size:11px;font-weight:700;margin-bottom:6px"><span>客户端</span><span>服务端</span></div>
<div style="text-align:center"><span class="hs-msg">① SYN seq=x →</span></div>
<div style="text-align:center"><span class="hs-msg">← SYN+ACK seq=y,ack=x+1 ②</span></div>
<div style="text-align:center"><span class="hs-msg">③ ACK ack=y+1 →</span></div>
<div style="text-align:center;font-size:10px;opacity:.7;margin-top:6px">双方进入 ESTABLISHED，连接建立</div>
</div>

### 2.3 TCP 流量控制与拥塞控制

**流量控制（滑动窗口）**：接收方通过 TCP 头的窗口字段告知发送方自己的接收能力，发送方不能发送超过窗口大小的数据。零窗口时发送方启动持续计时器，定时探测。

**拥塞控制**：
- 慢启动：cwnd 从 1 开始指数增长（1→2→4→8），达到 ssthresh 后进入拥塞避免
- 拥塞避免：cwnd 线性增长（每个 RTT +1）
- 快重传：收到 3 个重复 ACK 立即重传（不等超时）
- 快恢复：快重传后 ssthresh=cwnd/2，cwnd=ssthresh，进入拥塞避免

> 🔍 **知识点深度解析**
>
> **作用**：流量控制防止发送方发太快导致接收方处理不过来（点对点），拥塞控制防止发送方发太快导致网络过载（全局网络）。两者配合保证 TCP 在各种网络条件下的稳定传输。
>
> **原理**：滑动窗口的核心是接收方通告窗口（rwnd），发送方的发送窗口=min(cwnd, rwnd)。流量控制是接收方主导的（我能收多少你就发多少）。拥塞控制是发送方主导的，通过 ACK 返回情况推断网络拥塞程度：慢启动阶段指数增长探测网络带宽，达到阈值后线性增长避免过快，丢包（超时或3个重复ACK）时判断为拥塞，降低 cwnd。快重传+快恢复是优化：收到3个重复ACK说明个别包丢失但网络还通，不需要降到1（慢启动），而是减半后继续线性增长。
>
> **用法要点**：① 流量控制和拥塞控制的区别是面试重点（点对点vs全局、接收方主导vs发送方主导）；② 滑动窗口大小由接收方 TCP 头 window 字段决定（最大65535，窗口缩放因子可扩大）；③ 零窗口探测：接收方窗口为0时，发送方定时发1字节探测；④ 拥塞控制四个阶段要记住：慢启动（指数）、拥塞避免（线性）、快重传（3重复ACK）、快恢复（减半+线性）；⑤ 超时重传比快重传更严重（超时说明网络可能很差），超时后 cwnd 降到1，ssthresh=cwnd/2。

### 2.4 HTTP 与 HTTPS

**HTTP 方法**：GET（查询）、POST（创建）、PUT（更新）、DELETE（删除）、PATCH（部分更新）、HEAD、OPTIONS

**HTTP 状态码**：
- 2xx 成功：200 OK、201 Created、204 No Content
- 3xx 重定向：301 永久、302 临时、304 Not Modified
- 4xx 客户端错误：400 参数错误、401 未认证、403 禁止、404 未找到
- 5xx 服务端错误：500 内部错误、502 网关错误、503 不可用、504 网关超时

**HTTPS = HTTP + TLS/SSL**：
1. 客户端 → 服务端：ClientHello（支持的加密套件、随机数）
2. 服务端 → 客户端：ServerHello（选定加密套件、随机数）+ 数字证书
3. 客户端验证证书，生成预主密钥，用服务端公钥加密发送
4. 双方用随机数+预主密钥生成会话密钥
5. 后续通信用会话密钥对称加密

> 🔍 **知识点深度解析**
>
> **作用**：HTTP 是应用层最广泛的协议（Web/API），HTTPS 在 HTTP 基础上加了 TLS 加密，保证数据机密性、完整性和身份认证。理解 HTTP 是 Web 开发的基础，HTTPS 是安全通信的标配。
>
> **原理**：HTTP 是无状态协议（每次请求独立），基于 TCP 传输。HTTP/1.1 引入持久连接（Connection: keep-alive）和管道化，但存在队头阻塞。HTTP/2 用二进制分帧+多路复用解决队头阻塞，头部压缩（HPACK），服务器推送。HTTPS 的 TLS 握手：非对称加密（RSA/ECC）用于身份认证和密钥交换，对称加密（AES）用于后续数据传输（非对称慢，对称快）。数字证书由 CA 签发，包含服务端公钥，客户端用 CA 根证书验证签名确认真伪。
>
> **用法要点**：① GET 和 POST 的区别：GET 参数在 URL（有长度限制、可缓存），POST 在 body（无长度限制、不可缓存）；② 幂等性：GET/PUT/DELETE 幂等，POST 不幂等；③ 301 vs 302：301 永久重定向（搜索引擎更新索引），302 临时；④ HTTPS 握手耗时（1-2 RTT），TLS 1.3 优化为 1 RTT 甚至 0 RTT；⑤ 证书链验证：客户端验证服务端证书→验证签发CA→直到根证书（浏览器内置）；⑥ HTTP 无状态用 Cookie/Session/Token 保持状态。

### 2.5 进程与线程

**进程**：资源分配的最小单位，拥有独立的地址空间、文件描述符、PCB（进程控制块）。
**线程**：CPU 调度的最小单位，共享进程的地址空间和资源，有独立的栈、寄存器、TCB。

**进程状态**：新建 → 就绪 → 运行 → 阻塞 → 终止（就绪和运行可互相转换）。

**进程调度算法**：FCFS（先来先服务）、SJF（短作业优先）、优先级调度、时间片轮转（RR）、多级反馈队列。

> 🔍 **知识点深度解析**
>
> **作用**：进程和线程是操作系统并发的基础。进程提供隔离（一个进程崩溃不影响其他），线程提供轻量并发（同一进程内线程切换开销小）。理解两者区别是理解并发编程和操作系统的基础。
>
> **原理**：进程切换需要切换页表（TLB 刷新）、刷新缓存、保存/恢复 PCB，开销大（微秒级）；线程切换只需保存/恢复寄存器和栈，不需要切换地址空间，开销小（纳秒级）。进程间通信（IPC）需要内核介入（管道/消息队列/共享内存/信号量/Socket），线程间通信直接读写共享内存（但需同步）。进程调度由 OS 内核完成，调度算法的目标是：高吞吐量、短响应时间、公平性、无饥饿。多级反馈队列是最实用的算法：多个队列优先级递减、时间片递增，新进程进高优先级队列，用完时间片降级，IO密集型 stays 高优先级。
>
> **用法要点**：① 进程和线程的区别是必考题（资源分配vs调度、地址空间、切换开销、通信方式）；② 进程间通信方式：管道（半双工、父子进程）、命名管道（FIFO、无关进程）、消息队列、共享内存（最快、需同步）、信号量（同步）、Socket（跨主机）；③ 线程同步：互斥锁、条件变量、信号量、读写锁；④ 上下文切换开销：进程>线程，所以高并发用线程而非进程；⑤ 僵尸进程：子进程退出父进程没 wait，需父进程处理或用 signal(SIGCHLD, SIG_IGN)；⑥ 孤儿进程：父进程退出子进程还在，被 init 收养。

### 2.6 内存管理

**虚拟内存**：每个进程有独立的虚拟地址空间，OS 通过页表将虚拟地址映射到物理地址。进程看到的是连续的地址空间，实际物理内存可以不连续。

**分页**：虚拟内存和物理内存都分成固定大小的页（4KB），通过页表映射。多级页表（如 x86 四级页表）减少页表内存占用。

**页面置换算法**：FIFO、LRU（最近最少使用）、LFU（最不经常使用）、Clock（时钟算法，近似 LRU）。

**缺页中断**：访问的页不在物理内存时触发，OS 从磁盘加载页面到内存，可能触发页面置换。

> 🔍 **知识点深度解析**
>
> **作用**：虚拟内存让每个进程以为自己独占全部内存，提供了进程隔离（地址空间独立）、内存扩展（可用磁盘空间）、简化内存管理（进程看到连续地址）。分页是虚拟内存的实现方式，页面置换保证物理内存不足时仍能运行。
>
> **原理**：虚拟地址到物理地址的转换由 MMU（内存管理单元）硬件完成：虚拟地址=页号+页内偏移，MMU 查页表（TLB 加速）得到物理页号，拼上页内偏移得到物理地址。如果页表项中"存在位"为0，触发缺页中断（异常），OS 内核处理：分配物理页、从磁盘读入、更新页表、恢复指令。LRU 置换算法的原理是"最近最少用的页面未来也最不可能用"，实现用链表（访问时移到头部，淘汰尾部）。TLB（Translation Lookaside Buffer）是页表缓存，命中时直接得物理地址，不命中才查内存页表（慢100倍）。
>
> **用法要点**：① 虚拟内存的三大作用：进程隔离、内存扩容、简化管理；② 分页 vs 分段：分页固定大小（内部碎片），分段逻辑单位（外部碎片），现代 OS 用分页；③ 页面置换算法 LRU 是重点，实现用哈希表+双向链表（O(1)）；④ 缺页中断是异常不是中断，处理后重新执行触发异常的指令；⑤ 工作集模型：进程频繁访问的页面集合，工作集>物理内存则抖动（thrashing，频繁缺页）；⑥ Java 的堆是在虚拟内存上分配的，JVM 自己管理堆内的对象分配和 GC。

### 2.7 IO 模型

**五种 IO 模型**（UNIX）：
1. 阻塞 IO：调用后阻塞直到数据就绪并拷贝完成
2. 非阻塞 IO：调用立即返回（没就绪则 EAGAIN），需轮询
3. IO 多路复用：select/poll/epoll 同时监控多个 fd，任一就绪则返回
4. 信号驱动 IO：数据就绪时发 SIGIO 信号通知
5. 异步 IO（AIO）：调用后立即返回，数据就绪+拷贝完成后回调通知

**Linux IO 多路复用**：
- select：最多 1024 fd，线性扫描，O(n)
- poll：无数量限制，仍线性扫描
- epoll：红黑树+就绪链表，事件通知，O(1)，ET/LT 两种模式

> 🔍 **知识点深度解析**
>
> **作用**：IO 模型决定了程序处理 IO 的效率。阻塞 IO 简单但并发低，IO 多路复用是高并发网络编程的基础（Reactor 模式），异步 IO 是最高效的（Proactor 模式）。理解 IO 模型是理解 Netty/Nginx/Redis 高性能的基础。
>
> **原理**：Linux 下 IO 分两阶段：① 数据就绪（等待数据从网络/磁盘到达内核缓冲区）；② 数据拷贝（从内核缓冲区拷贝到用户空间）。阻塞 IO 在两个阶段都阻塞；非阻塞 IO 在第一阶段不阻塞（轮询），第二阶段阻塞；IO 多路复用在第一阶段阻塞（但同时等多个 fd），第二阶段阻塞；信号驱动 IO 第一阶段不阻塞（信号通知），第二阶段阻塞；异步 IO 两个阶段都不阻塞（全部完成后回调）。epoll 的高性能来自：① 用红黑树管理 fd（增删改 O(logn)）；② 就绪 fd 用链表（不需要扫描全部）；③ 内存映射（mmap，避免内核到用户的拷贝）；④ ET 模式（边缘触发，只通知一次，需非阻塞+循环读）。
>
> **用法要点**：① select/poll/epoll 的区别是面试重点（数量限制、效率、实现）；② epoll ET（边缘触发）vs LT（水平触发）：ET 只在状态变化时通知一次（需非阻塞+循环读到 EAGAIN），LT 只要有数据就通知（简单但可能多次）；③ Java NIO 用的是 epoll（Linux），Netty 基于 NIO 封装；④ Redis 单线程用 epoll 实现高并发（6万QPS）；⑤ Nginx 用 epoll + 多进程（master+worker）；⑥ 异步 IO（AIO）在 Linux 上支持不完善，Windows 上成熟（IOCP）。

---


---
## 3. 常用用法

### 3.1 TCP 编程（Java Socket）

```java
// 服务端
ServerSocket server = new ServerSocket(8080);
while (true) {
    Socket socket = server.accept(); // 阻塞等待连接
    new Thread(() -> {
        try (BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
             PrintWriter out = new PrintWriter(socket.getOutputStream(), true)) {
            String line;
            while ((line = in.readLine()) != null) {
                out.println("Echo: " + line);
            }
        } catch (IOException e) { e.printStackTrace(); }
    }).start();
}

// 客户端
Socket socket = new Socket("localhost", 8080);
PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
out.println("Hello");
System.out.println(in.readLine());
```

> 🔍 **知识点深度解析**
>
> **作用**：Socket 是 TCP 编程的 API 抽象，服务端用 ServerSocket 监听端口，客户端用 Socket 连接。BIO（阻塞IO）模型简单但并发低（每连接一线程），是理解网络编程的基础。
>
> **原理**：ServerSocket.accept() 阻塞等待三次握手完成，返回已建立连接的 Socket。Socket 封装了 InputStream/OutputStream，读写对应 TCP 的收发缓冲区。TCP 是面向流的（没有消息边界），所以应用层需要自己处理粘包/拆包（用固定长度、分隔符、或长度字段）。Java Socket 默认是阻塞的，setSoTimeout() 设置读超时。NIO 用 Channel+Selector 实现非阻塞多路复用。
>
> **用法要点**：① 必须处理粘包拆包（TCP 是流协议）；② 服务端每连接一线程模型并发低，生产用 NIO/Netty；③ 用完必须 close()（try-with-resources）；④ setSoTimeout() 防止读阻塞永久挂起；⑤ setTcpNoDelay(true) 禁用 Nagle 算法（小包立即发送，延迟敏感场景）；⑥ setSoLinger() 控制 close 时是否等待发送缓冲区数据。

### 3.2 HTTP 客户端（Java）

```java
// Java 11+ HttpClient
HttpClient client = HttpClient.newBuilder()
    .connectTimeout(Duration.ofSeconds(5))
    .build();

HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .header("Content-Type", "application/json")
    .timeout(Duration.ofSeconds(10))
    .GET()
    .build();

HttpResponse<String> response = client.send(request, 
    HttpResponse.BodyHandlers.ofString());
System.out.println(response.statusCode());
System.out.println(response.body());

// 异步发送
CompletableFuture<HttpResponse<String>> future = 
    client.sendAsync(request, HttpResponse.BodyHandlers.ofString());
```

> 🔍 **知识点深度解析**
>
> **作用**：HttpClient 是 Java 11 引入的标准 HTTP 客户端，替代了老旧的 HttpURLConnection，支持 HTTP/1.1、HTTP/2、同步/异步、WebSocket。是调用外部 API 的标准方式。
>
> **原理**：HttpClient 内部基于 NIO 实现，连接池复用 TCP 连接（HTTP keep-alive）。HTTP/2 支持多路复用（一个 TCP 连接并发多个请求）。同步 send() 阻塞等待响应，异步 sendAsync() 返回 CompletableFuture。BodyHandlers 提供了字符串、字节数组、文件、输入流等多种响应体处理方式。
>
> **用法要点**：① 必须设置连接超时和读取超时（防止永久阻塞）；② 生产用连接池（HttpClient 内部默认有连接池）；③ 大响应体用 BodyHandlers.ofInputStream() 或 ofFile()，不要全部加载到内存；④ 异步用 sendAsync() 配合 CompletableFuture 链式处理；⑤ 重试要考虑幂等性（GET 可重试，POST 谨慎）；⑥ 生产环境常用 OkHttp/Retrofit（更丰富的功能）或 Spring WebClient（响应式）。

### 3.3 进程与线程（Java）

```java
// 创建进程
ProcessBuilder pb = new ProcessBuilder("ls", "-la");
pb.directory(new File("/tmp"));
Process process = pb.start();
try (BufferedReader reader = new BufferedReader(
        new InputStreamReader(process.getInputStream()))) {
    reader.lines().forEach(System.out::println);
}
int exitCode = process.waitFor();

// 创建线程
Thread thread = new Thread(() -> {
    System.out.println("线程: " + Thread.currentThread().getName());
});
thread.start();

// 线程池（推荐）
ExecutorService pool = Executors.newFixedThreadPool(10);
pool.submit(() -> doWork());
pool.shutdown();
```

> 🔍 **知识点深度解析**
>
> **作用**：Java 中 ProcessBuilder 创建外部进程（调用系统命令），Thread 创建线程。实际开发中线程池是首选（复用线程、控制并发），手动创建线程仅在简单场景使用。
>
> **原理**：ProcessBuilder.start() 通过 fork+exec 创建子进程，子进程有独立的地址空间，通过输入输出流与父进程通信（管道）。Java 线程映射到 OS 内核线程（1:1 模型），start() 调用 native start0() 创建 OS 线程。线程池通过 Worker 复用线程，避免频繁创建销毁开销。Java 21 虚拟线程是用户态线程（M:N 模型），由 JVM 调度。
>
> **用法要点**：① 外部进程必须读取输出流和错误流（否则缓冲区满会阻塞），用 redirectErrorStream(true) 合并；② waitFor() 阻塞等待进程退出，可设超时；③ 不要手动创建大量线程，用线程池；④ 线程必须命名（方便排查）；⑤ 未捕获异常用 UncaughtExceptionHandler 处理；⑥ 虚拟线程（Java 21）适合 IO 密集型，用 Executors.newVirtualThreadPerTaskExecutor()。

### 3.4 进程间通信

```java
// 1. 管道（Java 中用 ProcessBuilder 的输入输出流）
ProcessBuilder pb = new ProcessBuilder("grep", "error");
Process p = pb.start();
// 父进程写数据到子进程 stdin
try (OutputStream stdin = p.getOutputStream()) {
    stdin.write("error message\n".getBytes());
}

// 2. Socket（本地回环，可跨进程）
ServerSocket server = new ServerSocket(9999);
Socket client = new Socket("127.0.0.1", 9999);

// 3. 共享内存（Java NIO MappedByteBuffer）
FileChannel fc = FileChannel.open(Paths.get("/tmp/shared"), 
    StandardOpenOption.READ, StandardOpenOption.WRITE);
MappedByteBuffer buf = fc.map(FileChannel.MapMode.READ_WRITE, 0, 1024);
buf.put("hello".getBytes());
```

> 🔍 **知识点深度解析**
>
> **作用**：进程间通信（IPC）是多进程架构的基础。不同 IPC 方式有不同的适用场景：管道适合父子进程简单数据传递，Socket 适合跨主机/跨进程通用通信，共享内存适合大数据量高速传输。
>
> **原理**：管道是内核缓冲区（4KB），半双工，数据先进先出。命名管道（FIFO）是文件系统中的特殊文件，可用于无关进程。Socket 是全双工的，基于 TCP/UDP，本地回环（127.0.0.1）不走网卡，在内核协议栈中直接回环。共享内存通过 mmap 将同一块物理内存映射到多个进程的虚拟地址空间，进程直接读写（最快的 IPC），但需要信号量/互斥锁同步。消息队列是内核维护的消息链表，有类型和优先级。
>
> **用法要点**：① 管道只能用于有亲缘关系的进程（父子），命名管道可用于无关进程；② Socket 是最通用的 IPC（可跨主机），但有序列化/网络开销；③ 共享内存最快但需手动同步（信号量）；④ 微服务架构中，进程间通信通常用 HTTP/RPC（Socket 的上层封装）；⑤ Java 中 RMI 是远程方法调用（基于 Socket），但已过时；⑥ 消息队列（Kafka/RabbitMQ）是分布式系统的 IPC，解耦+异步+削峰。

### 3.5 内存映射文件

```java
// 大文件读写（零拷贝）
try (FileChannel fc = FileChannel.open(Paths.get("large.dat"),
        StandardOpenOption.READ, StandardOpenOption.WRITE)) {
    // 映射 1GB 文件到内存
    MappedByteBuffer buf = fc.map(FileChannel.MapMode.READ_WRITE, 0, 1024 * 1024 * 1024);
    
    // 直接读写（不需要 read/write 系统调用）
    byte b = buf.get(0);
    buf.put(0, (byte) 1);
    
    // 强制刷盘
    buf.force();
}

// 零拷贝传输（文件到 Socket）
try (FileChannel fc = FileChannel.open(Paths.get("file.txt"));
     SocketChannel sc = SocketChannel.open(new InetSocketAddress("host", 8080))) {
    fc.transferTo(0, fc.size(), sc); // sendfile 零拷贝
}
```

> 🔍 **知识点深度解析**
>
> **作用**：内存映射文件（mmap）将文件直接映射到进程虚拟地址空间，读写文件像读写内存一样，不需要 read/write 系统调用（减少内核态/用户态切换和数据拷贝）。零拷贝（sendfile）直接从文件传输到 Socket，是高性能文件传输的基础。
>
> **原理**：传统 IO 流程：read() → 内核缓冲区 → 用户缓冲区 → write() → Socket 缓冲区 → 网卡，共4次拷贝+4次上下文切换。mmap 把文件映射到用户空间，用户直接读写，OS 自动同步到磁盘（缺页中断时加载），减少了内核到用户的拷贝。sendfile 直接从内核缓冲区传到 Socket 缓冲区（2次拷贝），配合 DMA Gather 可实现真正的零拷贝（1次拷贝，DMA 直接从文件到网卡）。Java NIO 的 transferTo() 底层用 sendfile。
>
> **用法要点**：① mmap 适合大文件随机读写（如数据库、搜索引擎）；② mmap 的内存不是堆内存（是堆外/直接内存），不受 GC 管理；③ mmap 大小限制：32位系统最大1.5-2G，64位系统理论很大但受文件大小限制；④ 大文件分块映射（一次映射不要太大，避免虚拟内存压力）；⑤ force() 强制刷盘（类似 fsync），性能开销大；⑥ Kafka 用 mmap 实现高吞吐消息持久化，Netty 用零拷贝传输文件。

### 3.6 IO 多路复用（Java NIO）

```java
Selector selector = Selector.open();

// 服务端通道
ServerSocketChannel server = ServerSocketChannel.open();
server.bind(new InetSocketAddress(8080));
server.configureBlocking(false); // 非阻塞
server.register(selector, SelectionKey.OP_ACCEPT);

while (true) {
    selector.select(); // 阻塞，直到有事件就绪
    Set<SelectionKey> keys = selector.selectedKeys();
    for (SelectionKey key : keys) {
        if (key.isAcceptable()) {
            SocketChannel client = server.accept();
            client.configureBlocking(false);
            client.register(selector, SelectionKey.OP_READ);
        } else if (key.isReadable()) {
            SocketChannel client = (SocketChannel) key.channel();
            ByteBuffer buf = ByteBuffer.allocate(1024);
            client.read(buf);
            buf.flip();
            client.write(buf); // echo
        }
    }
    keys.clear();
}
```

> 🔍 **知识点深度解析**
>
> **作用**：Java NIO（New IO）实现了 IO 多路复用，一个线程可以管理多个 Channel（连接），是高并发网络编程的基础。Netty 就是基于 NIO 封装的。
>
> **原理**：Selector 是多路复用器，底层 Linux 用 epoll（Windows 用 select）。Channel 注册到 Selector 时指定感兴趣的事件（ACCEPT/READ/WRITE/CONNECT）。select() 阻塞直到有事件就绪，返回就绪的 SelectionKey 集合。SelectionKey 关联了 Channel 和对应的就绪事件。NIO 用 ByteBuffer（非 byte[]）作为数据容器，有 position/limit/capacity 三个指针，flip() 切换读写模式。
>
> **用法要点**：① 必须 configureBlocking(false)，否则不能注册到 Selector；② selectedKeys 处理完必须 clear()（否则下次还会返回）；③ 写事件（OP_WRITE）通常不需要注册（缓冲区可写时一直触发，CPU 100%），只在写不完时临时注册；④ 必须处理半包/粘包（TCP 流协议）；⑤ 直接 ByteBuffer（allocateDirect）用堆外内存，减少拷贝，适合 IO；⑥ 生产用 Netty 而非原生 NIO（Netty 解决了 NIO 的很多坑：空轮询 bug、半包处理、Reactor 模式）。

### 3.7 死锁排查与避免

```java
// 死锁示例（两个线程互相等待对方的锁）
Object lockA = new Object();
Object lockB = new Object();

new Thread(() -> {
    synchronized (lockA) {
        Thread.sleep(100);
        synchronized (lockB) { /* 死锁：等待 lockB */ }
    }
}).start();

new Thread(() -> {
    synchronized (lockB) {
        Thread.sleep(100);
        synchronized (lockA) { /* 死锁：等待 lockA */ }
    }
}).start();

// 排查：jstack 检测死锁
// jstack <pid> | grep -A 20 "Found one Java-level deadlock"
```

> 🔍 **知识点深度解析**
>
> **作用**：死锁是并发编程中最严重的问题之一（线程永久阻塞，服务假死）。理解死锁的四个必要条件和避免方法是并发编程的基础，jstack 是排查死锁的标准工具。
>
> **原理**：死锁的四个必要条件（Coffman 条件）：① 互斥（资源不能共享）；② 持有并等待（持有一个资源等另一个）；③ 不可剥夺（资源不能被强行夺走）；④ 循环等待（A等B，B等A）。四个条件同时满足才会死锁，破坏任意一个即可避免。jstack 能自动检测死锁是因为 JVM 维护了锁等待图（ThreadMXBean.findDeadlockedThreads()），通过图的环检测算法发现循环等待。
>
> **用法要点**：① 避免死锁最有效的方法：固定加锁顺序（所有线程按相同顺序获取锁）；② 用 tryLock 超时（ReentrantLock.tryLock(timeout)，获取失败则释放已持有的锁）；③ 减少锁嵌套（能用一个锁就不用两个）；④ 用并发集合替代手动锁；⑤ jstack 是排查死锁的标准工具（自动检测并打印死锁线程和锁信息）；⑥ 死锁 vs 活锁：死锁是都不执行，活锁是都在执行但都无法推进（如两个线程都释放锁让对方，结果都拿不到）。

### 3.8 DNS 解析

```java
// Java DNS 解析
InetAddress[] addresses = InetAddress.getAllByName("www.example.com");
for (InetAddress addr : addresses) {
    System.out.println(addr.getHostAddress());
}

// 自定义 DNS 缓存
// JVM 默认缓存 DNS 结果（-Dnetworkaddress.cache.ttl=30 秒）
// security 文件中 networkaddress.cache.ttl=-1 表示永久缓存
```

> 🔍 **知识点深度解析**
>
> **作用**：DNS（域名系统）将域名解析为 IP 地址，是互联网的"电话簿"。理解 DNS 解析过程有助于排查域名解析问题、CDN 调度、DNS 缓存等。
>
> **原理**：DNS 解析过程（递归+迭代）：① 客户端查本地缓存（浏览器/OS）；② 没命中则查本地 DNS 服务器（运营商）；③ 本地 DNS 查根域名服务器（.）→ 顶级域名服务器（.com）→ 权威域名服务器（example.com）→ 返回 IP。DNS 记录类型：A（IPv4）、AAAA（IPv6）、CNAME（别名）、MX（邮件）、TXT（文本）、NS（域名服务器）。DNS 缓存层级：浏览器缓存→OS缓存→本地DNS缓存→权威DNS TTL。DNS 负载均衡：一个域名配置多个 A 记录，DNS 轮询返回。
>
> **用法要点**：① Java 默认永久缓存 DNS 解析结果（安全考虑），用 -Dnetworkaddress.cache.ttl=30 设置缓存时间；② DNS 解析慢会拖慢 HTTP 请求，可预热（应用启动时解析一次）；③ CDN 基于 DNS 调度（不同地区返回不同边缘节点 IP）；④ DNS 污染/劫持：返回错误 IP，用 DNS over HTTPS（DoH）解决；⑤ nslookup/dig 命令排查 DNS 问题；⑥ 生产环境注意 DNS TTL 设置（太短增加 DNS 压力，太长变更生效慢）。

---


---
## 4. 注意事项

1. **TCP 粘包拆包**：TCP 是面向流的协议，没有消息边界。应用层必须用固定长度、分隔符、或长度字段（如 LengthFieldBasedFrameDecoder）处理。

2. **TIME_WAIT 过多**：高并发服务端可能出现大量 TIME_WAIT 占用端口。用 net.ipv4.tcp_tw_reuse=1、net.ipv4.tcp_fin_timeout 调小、或服务端主动不关闭连接解决。

3. **HTTP 幂等性**：GET/PUT/DELETE 是幂等的（多次调用结果相同），POST 不幂等。重试机制只应对幂等接口使用，POST 重试可能导致重复创建。

4. **HTTPS 性能**：TLS 握手增加 1-2 RTT 延迟，非对称加密慢。用 TLS 会话恢复（Session ID/Ticket）、HTTP/2 多路复用、OCSP Stapling 优化。

5. **进程 vs 线程选择**：需要隔离用进程（如微服务），需要轻量并发用线程。进程切换开销大但安全隔离好，线程切换快但一个线程崩溃可能影响整个进程。

6. **虚拟内存不是无限的**：32位系统进程虚拟地址空间只有 4G（用户空间 2-3G），64位系统理论很大但受物理内存+交换空间限制。mmap 大文件注意虚拟内存占用。

7. **IO 模型选择**：简单用阻塞 IO，高并发用 IO 多路复用（NIO/Netty），极致性能用异步 IO。不要用非阻塞 IO 轮询（CPU 100%）。

8. **epoll ET 模式**：边缘触发只通知一次，必须用非阻塞 IO + 循环读直到 EAGAIN，否则会丢事件。LT 模式简单但效率略低。

9. **死锁预防**：固定加锁顺序、tryLock 超时、减少锁嵌套、用并发集合。jstack 自动检测死锁，是排查利器。

10. **DNS 缓存**：Java 默认永久缓存 DNS，生产必须设置 networkaddress.cache.ttl。DNS 变更后注意缓存生效时间。

11. **HTTP/2 优势**：多路复用解决队头阻塞、头部压缩、服务器推送。但 HTTP/2 仍有 TCP 层队头阻塞，HTTP/3（QUIC）用 UDP 解决。

12. **零拷贝场景**：大文件传输用 sendfile（transferTo），大文件随机读写用 mmap。注意 mmap 是堆外内存，不受 GC 管理。

---

> 💡 **深度讲解**：计算机网络和操作系统是后端开发的"内功"。TCP 的三次握手/四次挥手、流量控制/拥塞控制保证了可靠传输，理解这些机制才能排查连接超时、TIME_WAIT 过多、传输慢等问题。HTTP/HTTPS 是 Web 开发的基础，HTTPS 的 TLS 握手用非对称加密做密钥交换、对称加密做数据传输，兼顾安全和性能。操作系统的虚拟内存让每个进程有独立地址空间，分页+缺页中断实现了内存的"按需分配"和"超量使用"。IO 模型决定了并发能力：阻塞 IO 简单但并发低，IO 多路复用（epoll）是高并发的基础（Nginx/Redis/Netty 都基于此）。死锁的四个必要条件是理解和避免死锁的关键。这些知识不仅是面试八股，更是排查线上问题、做性能优化的理论基础。
>
> **📝 精简总结**：网络：TCP/IP 四层、TCP 三次握手四次挥手、滑动窗口+拥塞控制（慢启动/拥塞避免/快重传/快恢复）、HTTP 方法状态码、HTTPS=TLS 非对称+对称加密；OS：进程（资源分配）vs 线程（调度）、虚拟内存+分页+缺页中断、五种 IO 模型（epoll 最优）、死锁四条件+避免（固定顺序/tryLock）、IPC 方式（管道/Socket/共享内存）。

---

> 📋 **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 知识点深度解析」模块（作用+原理+用法要点），新增了 TCP 三次握手图解，原有内联图已统一风格化美化（圆角、阴影、渐变、动画）。所有原有内容完整保留，未做任何修改。
