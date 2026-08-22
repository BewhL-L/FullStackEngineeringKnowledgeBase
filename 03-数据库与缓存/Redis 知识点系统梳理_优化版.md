---
title: Redis 知识点系统梳理
tags: [数据库, Redis, 缓存, 分布式锁]
created: 2026-08-12
updated: 2026-08-12
---

# Redis 知识点系统梳理（优化版）

> **文档说明**：本文档参照《Java知识点完整整合大全》排版风格，系统梳理 Redis 技术栈。包含概述、核心特性、常用用法、注意事项四大模块，辅以动态可视化解析图、深度讲解与精简总结。**优化版**在原有内容基础上，为每个知识点补充了作用、原理、用法的深度解析，并新增了知识点图解。

---

## 1. 概述

Redis（Remote Dictionary Server）是一个开源的、基于内存的**键值对（Key-Value）数据库**，由意大利开发者 Salvatore Sanfilippo 开发。它以极高的读写性能、丰富的数据结构和灵活的持久化方案，成为缓存、会话存储、排行榜、消息队列等场景的首选。

**核心定位**：
- 纯内存操作，单线程模型（6.0 引入多线程 IO），QPS 可达 10 万+
- 支持丰富数据结构：String、Hash、List、Set、ZSet、Bitmap、HyperLogLog、Geo、Stream
- 支持 RDB/AOF 两种持久化，数据可持久化到磁盘
- 支持主从复制、哨兵（Sentinel）、Cluster 集群三种高可用方案

**版本演进**：

| 版本 | 发布年份 | 关键特性 |
|------|---------|---------|
| Redis 3.x | 2015 | Redis Cluster 集群正式发布 |
| Redis 4.x | 2017 | 模块化系统，混合持久化（RDB+AOF） |
| Redis 5.x | 2018 | Stream 数据结构，新的客户端管理 |
| Redis 6.x | 2020 | 多线程 IO，ACL 权限控制，SSL 支持 |
| Redis 7.x | 2022 | 多部分 AOF，函数（Functions），Sharded Pub/Sub |

---


---
## 2. 核心特性

<div style="background:linear-gradient(135deg,#ff9a9e,#fecfef);border-radius:16px;padding:24px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#1a1a2e;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes redisData{0%,100%{transform:scale(1);opacity:.85}50%{transform:scale(1.03);opacity:1}}.redis-ds{display:inline-block;width:18%;vertical-align:top;margin:0 1%;background:rgba(255,255,255,.45);border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:10px 6px;font-size:10px;text-align:center;animation:redisData 3s ease-in-out infinite}.redis-ds:nth-child(2){animation-delay:.4s}.redis-ds:nth-child(3){animation-delay:.8s}.redis-ds:nth-child(4){animation-delay:1.2s}.redis-ds:nth-child(5){animation-delay:1.6s}.redis-icon{font-size:20px;margin-bottom:4px}.redis-name{font-weight:700;font-size:12px;margin-bottom:2px}</style>
<div style="text-align:center;font-size:16px;font-weight:700;margin-bottom:16px;padding-bottom:12px;border-bottom:1.5px solid rgba(0,0,0,.1);letter-spacing:1px">Redis 五大数据结构</div>
<div style="text-align:center">
<div class="redis-ds"><div class="redis-icon">🔤</div><div class="redis-name">String</div><div style="font-size:9px;opacity:.75">字符串/数字/二进制<br>SET/GET/INCR</div></div>
<div class="redis-ds"><div class="redis-icon">🗂️</div><div class="redis-name">Hash</div><div style="font-size:9px;opacity:.75">键值对集合<br>HSET/HGET</div></div>
<div class="redis-ds"><div class="redis-icon">📋</div><div class="redis-name">List</div><div style="font-size:9px;opacity:.75">双向链表<br>LPUSH/RPOP</div></div>
<div class="redis-ds"><div class="redis-icon">🔢</div><div class="redis-name">Set</div><div style="font-size:9px;opacity:.75">无序不重复集合<br>SADD/SMEMBERS</div></div>
<div class="redis-ds"><div class="redis-icon">📊</div><div class="redis-name">ZSet</div><div style="font-size:9px;opacity:.75">有序集合(带score)<br>ZADD/ZRANGE</div></div>
</div>
</div>

### 2.1 数据结构

**String**：最基础类型，二进制安全，最大 512MB。常用：缓存、计数器（INCR）、分布式锁（SET NX EX）。

**Hash**：键值对集合，适合存储对象。常用：用户信息、商品信息。

**List**：双向链表，可做队列/栈。常用：消息队列（LPUSH+BRPOP）、最新列表。

**Set**：无序不重复集合，支持交并差集。常用：标签、共同好友、去重。

**ZSet（Sorted Set）**：有序集合，每个元素带 score，按 score 排序。常用：排行榜、延迟队列。

**高级结构**：Bitmap（位图，签到/活跃统计）、HyperLogLog（基数统计，UV）、Geo（地理位置）、Stream（消息流，5.0+）。

> 🔍 **知识点深度解析**
>
> **作用**：丰富的数据结构是 Redis 的核心优势，不同场景选合适结构能极大简化实现。String 通用，Hash 存对象，List 做队列，Set 做去重/集合运算，ZSet 做排序/排行榜。
>
> **原理**：Redis 底层用多种编码实现数据结构，根据数据量和类型自动选择（encoding）。String：int（整数）、embstr（短字符串，<=44字节，连续内存）、raw（长字符串，SDS 简单动态字符串）。Hash：ziplist（小数据量，连续内存压缩列表）、hashtable（大数据量，哈希表）。List：quicklist（3.2+，ziplist 节点的双向链表，兼顾空间和性能）。Set：intset（整数集合，小数据量）、hashtable。ZSet：ziplist（小数据量）、skiplist+hashtable（跳表+哈希表，跳表实现范围查询，哈希表实现 O(1) 查找）。编码转换是自动的（如 ziplist 元素超过阈值转 hashtable）。
>
> **用法要点**：① String 存对象用 JSON 序列化，或用 Hash（字段可单独更新，更省带宽）；② Hash 适合字段多的对象，字段少用 String+JSON 也可；③ List 做消息队列用 LPUSH+BRPOP（阻塞弹出），但不支持多消费组（用 Stream）；④ Set 交并差集：SINTER/SUNION/SDIFF（共同好友、推荐）；⑤ ZSet 排行榜：ZADD 加分数，ZRANGE/ZREVRANGE 取排名，ZRANK 取名次；⑥ 大数据量注意编码转换（ziplist→hashtable 内存增加）；⑦ 不要用 String 存大对象（>10KB），考虑拆分或用 Hash。

### 2.2 持久化：RDB 与 AOF

**RDB（Redis Database）**：快照持久化，定时将内存数据保存到 dump.rdb。
- 触发：save（阻塞）、bgsave（fork子进程，非阻塞）、配置 save 900 1（900秒内1次修改）
- 优点：文件小，恢复快
- 缺点：可能丢数据（两次快照之间的数据）

**AOF（Append Only File）**：追加写命令到 appendonly.aof。
- 同步策略：always（每条命令刷盘，最安全最慢）、everysec（每秒，默认，推荐）、no（OS 决定）
- 重写（BGREWRITEAOF）：压缩 AOF 文件，只保留最终状态
- 优点：数据安全（最多丢1秒）
- 缺点：文件大，恢复慢

**混合持久化（4.0+）**：AOF 重写时用 RDB 格式 + AOF 增量，兼顾恢复速度和数据安全。

> 🔍 **知识点深度解析**
>
> **作用**：持久化保证 Redis 重启后数据不丢失。RDB 是快照（恢复快但可能丢数据），AOF 是日志（数据安全但文件大）。生产用 AOF everysec + RDB 备份。
>
> **原理**：RDB：bgsave fork 子进程，子进程遍历内存写 RDB 文件（Copy-On-Write，父进程修改数据时复制页，子进程看到 fork 时的快照）。RDB 文件是二进制压缩格式，恢复时直接加载到内存。AOF：每条写命令追加到 AOF 文件（RESP 协议格式），重启时重新执行所有命令恢复数据。AOF 重写：fork 子进程，遍历内存生成最小命令集（如 INCR 100次→SET 100），写新 AOF 文件后替换旧文件。混合持久化：AOF 重写时前半段是 RDB 格式（快照），后半段是 AOF 增量命令，恢复时先加载 RDB 再执行增量（又快又安全）。
>
> **用法要点**：① 生产用 AOF everysec（最多丢1秒，性能好）+ RDB 定时备份；② 不要用 save（阻塞主线程），用 bgsave；③ AOF 文件会持续增长，配置 auto-aof-rewrite-percentage 100（增长100%自动重写）；④ 混合持久化（aof-use-rdb-preamble yes，4.0+默认开启）兼顾速度和安全；⑤ RDB 文件用于跨机房备份/迁移（文件小）；⑥ 恢复优先级：AOF > RDB（AOF 数据更全）；⑦ 持久化会影响性能（fork 耗时、IO），大内存实例注意 fork 耗时（可能秒级阻塞）。

### 2.3 过期策略与内存淘汰

**过期键删除**：
- 惰性删除：访问时检查是否过期，过期则删除
- 定期删除：每隔一段时间随机抽查过期键删除

**内存淘汰策略（maxmemory-policy）**：
- noeviction（默认）：内存满了拒绝写
- allkeys-lru：所有键 LRU 淘汰（推荐）
- volatile-lru：过期键中 LRU 淘汰
- allkeys-lfu：所有键 LFU 淘汰（4.0+，访问频率）
- volatile-lfu：过期键中 LFU
- allkeys-random / volatile-random：随机淘汰
- volatile-ttl：快过期的淘汰

> 🔍 **知识点深度解析**
>
> **作用**：过期策略自动清理过期键（释放内存），内存淘汰策略在内存满时选择淘汰哪些键（保证 Redis 不 OOM）。是缓存系统的核心机制。
>
> **原理**：过期键：Redis 用 expires 字典存键的过期时间。惰性删除：每次访问键时检查是否过期，过期则删除并返回 nil（CPU 友好，但过期键不访问就一直占内存）。定期删除：每 100ms（默认 hz=10）随机抽查 20 个过期键，删除其中过期的，如果过期比例>25% 则继续抽查（限制时间，避免长时间阻塞）。两种策略配合：定期删除清理大部分，惰性删除清理漏网的。内存淘汰：达到 maxmemory 时，根据策略选择淘汰键。LRU（最近最少使用）：Redis 用近似 LRU（随机采样 N 个键，淘汰最久未用的，不是全量 LRU，节省内存）。LFU（最不经常使用）：记录访问频率，低频淘汰（4.0+，比 LRU 更合理，热点数据不被淘汰）。
>
> **用法要点**：① 缓存场景用 allkeys-lru 或 allkeys-lfu（热点数据保留）；② 不要用默认 noeviction（内存满了写报错，缓存场景不可用）；③ LFU 比 LRU 好（访问频率比最近使用更能体现热度，4.0+推荐）；④ 过期键设置合理 TTL（不要永久缓存，内存泄漏）；⑤ 大 key 过期删除可能阻塞（异步删除 lazyfree-lazy-expire yes）；⑥ maxmemory 设置为物理内存的 70-80%（留内存给 OS 和 fork）；⑦ 监控 evicted_keys（淘汰键数），持续增长说明内存不够。

### 2.4 高可用：主从复制与哨兵

**主从复制**：
- 一主多从，主库写，从库读
- 全量复制：从库首次连接，主库生成 RDB 发送
- 增量复制：断线重连，从库发送 offset，主库发送积压的命令（repl_backlog）

**哨兵（Sentinel）**：
- 监控主从节点健康
- 自动故障转移：主库挂了，选举新主库
- 配置中心：客户端连接哨兵获取主库地址
- 至少 3 个哨兵节点（选举需要多数派）

> 🔍 **知识点深度解析**
>
> **作用**：主从复制实现读写分离和数据备份，哨兵实现自动故障转移（高可用）。是中小规模 Redis 的标准高可用方案。
>
> **原理**：主从复制：从库执行 SLAVEOF 主库地址，发送 PSYNC 命令。首次全量复制：主库 bgsave 生成 RDB，发送给从库，同时将期间的写命令存到 repl_backlog（环形缓冲区），从库加载 RDB 后执行积压命令。增量复制：断线重连时从库发送 last_repl_offset，主库从 repl_backlog 找到偏移量后的命令发送（如果偏移量已被覆盖则全量复制）。哨兵：多个 Sentinel 节点监控主库，通过 PING 检测主库是否存活。主观下线（sdown）：一个哨兵认为主库挂了。客观下线（odown）：超过 quorum（通常 N/2+1）个哨兵认为主库挂了，开始故障转移。选举领头哨兵（Raft 协议），领头哨兵选择最优从库（优先级高→offset大→runid小）提升为主库，其他从库指向新主库。
>
> **用法要点**：① 哨兵至少3节点（奇数，选举需要多数派），部署在不同机器；② 主库不要开 AOF（从库开即可，主库性能优先），或都开；③ 从库设 replica-read-only yes（防止误写）；④ 客户端连接哨兵获取主库地址（不是直连主库，故障转移后自动切换）；⑤ 全量复制期间主库性能下降（fork+网络传输），避免高峰期；⑥ repl_backlog_size 设大些（如 64MB），减少断线后全量复制；⑦ 哨兵监控多个主库时，注意哨兵数量和网络分区。

### 2.5 Redis Cluster 集群

**数据分片**：16384 个哈希槽（hash slot），每个节点负责一部分槽。
- key 的槽位 = CRC16(key) % 16384
- 至少 3 主 3 从（6节点），每个主库有从库备份

**核心特性**：
- 去中心化，无中心节点
- 客户端路由（重定向 MOVED/ASK）
- 支持在线扩缩容（迁移槽）
- 故障自动转移（类似哨兵，集群内选举）

**Hash Tag**：`{user:1}:profile`，只对 {} 内的部分计算槽，实现相关 key 同槽（支持多键操作）。

> 🔍 **知识点深度解析**
>
> **作用**：Cluster 是 Redis 官方分布式集群方案，解决单实例内存和并发瓶颈。数据分片到 16384 个槽，分布在多个主节点，实现水平扩展。
>
> **原理**：16384 个哈希槽分配给各主节点（如 3主：0-5460、5461-10922、10923-16383）。key 的槽位 = CRC16(key) & 16383。客户端请求时，先计算槽位，发送到负责该槽的节点。如果发错节点，节点返回 MOVED 重定向（告诉客户端正确节点）。ASK 重定向：槽正在迁移时，临时重定向到目标节点。故障转移：每个主节点有从节点，主节点故障时，从节点通过 Gossip 协议检测，选举新主（类似哨兵 Raft）。扩缩容：redis-cli --cluster add-node 添加节点，reshard 迁移槽（在线迁移，不中断服务）。Hash Tag：{tag}key 只对 tag 计算槽，让相关 key 在同一槽（支持 MGET/事务等多键操作）。
>
> **用法要点**：① 生产至少 3主3从（6节点），部署在不同机器；② 多键操作（MGET/事务/Lua）要求 key 同槽，用 Hash Tag `{prefix}:key`；③ 客户端用 Cluster 客户端（JedisCluster/Lettuce），自动处理 MOVED 重定向；④ 大 key 迁移慢，避免超大 key；⑤ 扩缩容用 redis-cli --cluster reshard（在线迁移）；⑥ 不支持跨槽事务（用 Hash Tag 或应用层协调）；⑦ 监控：cluster info（集群状态）、cluster nodes（节点状态）。

### 2.6 缓存问题：穿透、击穿、雪崩

**缓存穿透**：查询不存在的数据，缓存和数据库都没有，每次请求都打数据库。
- 解决：缓存空值（短 TTL）、布隆过滤器（Bloom Filter）拦截不存在的 key

**缓存击穿**：热点 key 过期瞬间，大量并发请求打数据库。
- 解决：互斥锁（SET NX）、热点 key 永不过期（逻辑过期）

**缓存雪崩**：大量 key 同时过期，或 Redis 宕机，请求全部打数据库。
- 解决：过期时间加随机值、Redis 高可用（哨兵/集群）、限流降级、多级缓存

> 🔍 **知识点深度解析**
>
> **作用**：缓存三大问题是缓存系统最常见的故障，理解原理和解决方案是后端开发必备。穿透是查不存在的数据，击穿是热点 key 过期，雪崩是大量 key 同时过期或 Redis 故障。
>
> **原理**：缓存穿透：恶意请求查询 id=-1 等不存在的数据，缓存 miss 后查数据库，数据库也没有，无法缓存，每次都打数据库。布隆过滤器：用位数组+多个哈希函数，判断 key 一定不存在或可能存在（不存在的一定拦截，存在的可能误判），在缓存前加一层布隆过滤器，不存在的直接返回。缓存击穿：热点 key（如秒杀商品）过期瞬间，上千请求同时缓存 miss，全部查数据库（数据库压力骤增）。互斥锁：第一个 miss 的请求 SET NX 加锁，查数据库并写缓存，其他请求等待重试。逻辑过期：热点 key 不设 TTL，value 中存逻辑过期时间，后台异步更新缓存（读时发现过期则异步刷新，返回旧值）。缓存雪崩：大量 key TTL 相同（如都设1小时），同时过期；或 Redis 宕机。TTL 加随机值（如 1小时±10分钟）打散过期时间。
>
> **用法要点**：① 缓存穿透：布隆过滤器（适合数据量固定的场景，如用户ID）+ 缓存空值（TTL 短，如30秒）；② 缓存击穿：热点 key 用互斥锁（Redisson 分布式锁）或逻辑过期（后台异步刷新）；③ 缓存雪崩：TTL 加随机值（base + random(0, 300s)）、Redis 高可用（哨兵/集群）、限流降级（Hystrix/Sentinel）；④ 多级缓存：本地缓存（Caffeine）+ Redis（减少 Redis 压力）；⑤ 预热：系统启动时提前加载热点数据到缓存；⑥ 监控缓存命中率（keyspace_hits/(hits+misses)），低于 90% 排查原因；⑦ 缓存和数据库一致性：先更新数据库再删缓存（Cache Aside Pattern），延迟双删。

### 2.7 分布式锁

**基础实现**：`SET lock:user:1 1 NX EX 30`（原子操作，不存在才设置，30秒过期）。

**释放锁**：Lua 脚本判断 value 是自己的才删除（防止误删别人的锁）。

**Redisson 分布式锁**：
- 可重入（Hash 结构记录重入次数）
- 看门狗（Watchdog）自动续期（默认每10秒检查，业务未完成则续期到30秒）
- 支持公平锁、读写锁、联锁、红锁

**RedLock**：多节点 Redis 加锁，多数派成功才算加锁成功（解决单点故障，但有争议）。

> 🔍 **知识点深度解析**
>
> **作用**：分布式锁在分布式环境中实现互斥（同一资源同时只有一个线程操作）。Redis 分布式锁性能好、实现简单，是最常用的分布式锁方案。
>
> **原理**：SET key value NX EX timeout：NX 保证互斥（不存在才设置），EX 保证死锁（超时自动释放）。value 设为唯一 ID（如 UUID），释放时用 Lua 脚本判断 value 相等才 DEL（防止锁过期后被别人获取，自己误删）。Redisson 可重入锁：用 Hash 结构，field 是线程标识，value 是重入次数，加锁时次数+1，解锁时-1，到0则删除。看门狗：加锁成功后启动后台线程，每 lockTime/3（默认10秒）检查业务是否还持有锁，是则续期到30秒（防止业务执行时间超过锁超时）。RedLock：在 N 个独立 Redis 节点上加锁，超过 N/2+1 成功且总耗时小于锁超时才算成功（解决单点故障，但 Martin Kleppmann 与 antirez 有争议，生产用 Redisson 单锁+主从足够）。
>
> **用法要点**：① 用 Redisson（不要自己实现，处理了续期、重入、释放等问题）；② 锁超时时间要大于业务执行时间（或用看门狗自动续期）；③ 释放锁用 Lua 脚本（判断 value 是自己的）；④ 锁粒度要小（锁用户ID而不是锁整个表）；⑤ 加锁失败要有重试或降级策略；⑥ RedLock 有争议，一般场景用单节点 Redisson 锁+主从高可用即可；⑦ 数据库唯一索引是最终兜底（分布式锁失败也不会重复插入）。

---


---
## 3. 常用用法

### 3.1 缓存使用模式

```java
// Cache Aside Pattern（旁路缓存，最常用）
public User getUserById(Long id) {
    String key = "user:" + id;
    // 1. 查缓存
    User user = redisTemplate.opsForValue().get(key);
    if (user != null) {
        return user;
    }
    // 2. 查数据库
    user = userMapper.selectById(id);
    if (user != null) {
        // 3. 写缓存（随机TTL防雪崩）
        int ttl = 3600 + new Random().nextInt(600);
        redisTemplate.opsForValue().set(key, user, ttl, TimeUnit.SECONDS);
    } else {
        // 缓存空值防穿透（短TTL）
        redisTemplate.opsForValue().set(key, NullUser.INSTANCE, 60, TimeUnit.SECONDS);
    }
    return user;
}

// 更新：先更新数据库，再删除缓存
@Transactional
public void updateUser(User user) {
    userMapper.updateById(user);
    redisTemplate.delete("user:" + user.getId());
}
```

> 🔍 **知识点深度解析**
>
> **作用**：Cache Aside（旁路缓存）是最常用的缓存模式，读时先缓存后数据库，写时更新数据库再删缓存。简单实用，适合大多数缓存场景。
>
> **原理**：读：缓存命中直接返回，miss 则查数据库，查到则写缓存（设 TTL），查不到则缓存空值（防穿透）。写：先更新数据库，再删除缓存（不是更新缓存，因为缓存可能是复杂计算的结果，删除更简单）。为什么删缓存而不是更新缓存：并发场景下更新缓存可能导致脏数据（A更新DB→B更新DB→B更新缓存→A更新缓存，缓存是A的旧值）。删除缓存则下次读时重新加载最新值。延迟双删：更新DB前删缓存→更新DB→延迟(如500ms)再删缓存（解决读写并发导致的缓存脏数据）。
>
> **用法要点**：① 读：缓存 miss 查 DB，查到写缓存，查不到缓存空值（短 TTL）；② 写：先更新 DB 再删缓存（不要更新缓存）；③ TTL 加随机值防雪崩（3600 + random(0,600)）；④ 一致性要求高用延迟双删或 binlog 监听删缓存（Canal）；⑤ 不要用缓存存强一致数据（如账户余额，用数据库）；⑥ 缓存预热：启动时加载热点数据；⑦ 监控命中率，低于预期排查（key 设计、TTL、穿透）。

### 3.2 排行榜（ZSet）

```java
// 添加分数
redisTemplate.opsForZSet().add("rank:daily", "user:1", 100);
redisTemplate.opsForZSet().add("rank:daily", "user:2", 200);

// 增加分数
redisTemplate.opsForZSet().incrementScore("rank:daily", "user:1", 50);

// 获取 Top 10（按分数降序）
Set<ZSetOperations.TypedTuple<Object>> top10 = 
    redisTemplate.opsForZSet().reverseRangeWithScores("rank:daily", 0, 9);

// 获取用户排名
Long rank = redisTemplate.opsForZSet().reverseRank("rank:daily", "user:1");

// 获取分数
Double score = redisTemplate.opsForZSet().score("rank:daily", "user:1");

// 每日排行榜：用不同 key（rank:20240101），过期自动清理
redisTemplate.expire("rank:20240101", 7, TimeUnit.DAYS);
```

> 🔍 **知识点深度解析**
>
> **作用**：ZSet 是排行榜的完美数据结构，自带排序（按 score），支持 Top N、排名查询、分数增减。比数据库 ORDER BY 性能好几个数量级。
>
> **原理**：ZSet 底层用跳表（skiplist）+ 哈希表。跳表实现按 score 排序的范围查询（O(log n)），哈希表实现 O(1) 的 score 查找。ZADD 添加/更新元素，ZINCRBY 增加分数，ZRANGE/ZREVRANGE 按排名范围获取，ZRANK/ZREVRANK 获取元素排名，ZSCORE 获取分数。排行榜按天/周/月：用不同 key（rank:daily:20240101），设置 TTL 自动清理历史数据。总榜：所有数据累加（或用定时任务聚合日榜到总榜）。
>
> **用法要点**：① 排行榜用 ZSet（不要用数据库 ORDER BY，性能差）；② Top N 用 reverseRange(0, N-1)（降序）；③ 排名用 reverseRank（从0开始，+1是实际名次）；④ 分数相同按插入顺序（可用时间戳作为 score 小数部分区分）；⑤ 周期排行榜：不同 key + TTL（日榜 rank:yyyyMMdd）；⑥ 大排行榜（百万级）ZSet 内存占用大，考虑分页或精简；⑦ 实时排行榜直接用 ZSet，离线统计用数据库/Spark。

### 3.3 消息队列（List/Stream）

```java
// List 实现简单队列（生产者）
redisTemplate.opsForList().leftPush("queue:order", orderJson);

// 消费者（阻塞弹出）
String msg = redisTemplate.opsForList().rightPop("queue:order", 30, TimeUnit.SECONDS);

// Stream（5.0+，支持消费组、ACK，推荐）
// 生产消息
MapRecord<String, String, String> record = StreamRecords.newRecord()
    .ofMap(Map.of("orderId", "123", "type", "create"))
    .withStreamKey("stream:order");
redisTemplate.opsForStream().add(record);

// 创建消费组
redisTemplate.opsForStream().createGroup("stream:order", "group1");

// 消费（消费组，自动ACK）
List<MapRecord<String, Object, Object>> messages = 
    redisTemplate.opsForStream().read(Consumer.from("group1", "consumer1"),
        StreamOffset.create("stream:order", ReadOffset.lastConsumed()));

// 手动 ACK
redisTemplate.opsForStream().acknowledge("stream:order", "group1", recordId);
```

> 🔍 **知识点深度解析**
>
> **作用**：Redis 可做轻量级消息队列，List 适合简单场景（无 ACK、无消费组），Stream 是专业消息队列（支持消费组、ACK、重试、历史消息）。
>
> **原理**：List 队列：LPUSH 入队，BRPOP 阻塞弹出（无消息时等待，避免轮询）。缺点：消息被消费即删除（无 ACK，消费者宕机丢消息）、不支持消费组（一条消息只能一个消费者）。Stream（5.0+）：借鉴 Kafka，消息是带 ID 的条目（ID 格式 时间戳-序号），支持消费组（Consumer Group），每个消费组独立消费进度（last_delivered_id），消息需 XACK 确认（未 ACK 的消息在 PEL 待确认列表，可重试）。XPENDING 查看未确认消息，XCLAIM 转移消息给其他消费者（处理消费者宕机）。Stream 用 Radix Tree 存储，支持范围查询和修剪。
>
> **用法要点**：① 简单队列用 List（LPUSH+BRPOP），但不保证不丢消息（消费者宕机）；② 可靠消息用 Stream（消费组+ACK）或专业 MQ（Kafka/RabbitMQ）；③ Stream 消费组：多消费者分摊消息（类似 Kafka Consumer Group）；④ 消息处理完必须 XACK（否则重复消费）；⑤ 死信：XPENDING 超时未 ACK 的消息用 XCLAIM 转移或单独处理；⑥ 不要用 Redis 做高吞吐消息队列（不如 Kafka），适合中小规模；⑦ Stream 消息要定期修剪（XTRIM），否则内存持续增长。

### 3.4 分布式限流

```java
// 固定窗口（简单但有临界问题）
public boolean tryAcquire(String key, int limit, int windowSeconds) {
    Long count = redisTemplate.opsForValue().increment("rate:" + key);
    if (count == 1) {
        redisTemplate.expire("rate:" + key, windowSeconds, TimeUnit.SECONDS);
    }
    return count <= limit;
}

// 滑动窗口（ZSet 实现，精确）
public boolean slidingWindow(String key, int limit, long windowMs) {
    long now = System.currentTimeMillis();
    String member = now + ":" + UUID.randomUUID(); // 唯一成员
    redisTemplate.opsForZSet().add(key, member, now);
    redisTemplate.opsForZSet().removeRangeByScore(key, 0, now - windowMs); // 移除窗口外
    Long count = redisTemplate.opsForZSet().zCard(key);
    redisTemplate.expire(key, windowMs * 2, TimeUnit.MILLISECONDS);
    return count <= limit;
}

// 令牌桶（Lua 脚本原子操作，推荐）
// Redisson RRateLimiter 内置实现
RRateLimiter limiter = redissonClient.getRateLimiter("my:limiter");
limiter.trySetRate(RateType.OVERALL, 10, 1, RateIntervalUnit.SECONDS); // 每秒10个
boolean acquired = limiter.tryAcquire();
```

> 🔍 **知识点深度解析**
>
> **作用**：分布式限流保护系统不被流量打垮，Redis 实现的限流是分布式环境的标准方案。固定窗口简单，滑动窗口精确，令牌桶平滑。
>
> **原理**：固定窗口：key=rate:资源，INCR 计数，第一次设过期时间（窗口），超过 limit 拒绝。问题：窗口边界可能 2 倍流量（如 0:59 发100，1:00 发100，1秒内200）。滑动窗口：用 ZSet 存请求时间戳，移除窗口外的元素，zCard 统计窗口内请求数。精确但内存占用大（每个请求一个元素）。令牌桶：桶里有固定数量令牌，请求取一个令牌，令牌不够则拒绝，令牌按速率补充。用 Lua 脚本原子操作（取令牌+补充令牌）。Redisson RRateLimiter 内置令牌桶实现，支持整体/客户端限流。漏桶：请求进桶，桶满则拒绝，按固定速率流出（平滑输出）。
>
> **用法要点**：① 简单限流用固定窗口（可接受临界问题）；② 精确限流用滑动窗口（ZSet）或令牌桶；③ 生产用 Redisson RRateLimiter（内置令牌桶，不用自己写）；④ 限流维度：用户ID、IP、接口、全局；⑤ 限流降级：被限流返回友好提示或排队；⑥ 集群限流用 Redis（本地限流 Guava RateLimiter 只限单实例）；⑦ 注意 Redis 限流的原子性（用 Lua 脚本，不要多次命令）。

### 3.5 会话与共享存储

```java
// Spring Session + Redis（分布式 Session）
@Configuration
@EnableRedisHttpSession(maxInactiveIntervalInSeconds = 1800)
public class SessionConfig {
    @Bean
    public RedisConnectionFactory redisConnectionFactory() {
        return new LettuceConnectionFactory();
    }
}

// 使用：标准 HttpSession
@GetMapping("/login")
public String login(HttpSession session, String username) {
    session.setAttribute("user", username);
    return "success";
}

// 共享数据：验证码
redisTemplate.opsForValue().set("sms:code:" + phone, code, 5, TimeUnit.MINUTES);

// 共享数据：用户 Token
redisTemplate.opsForValue().set("token:" + token, userId, 7, TimeUnit.DAYS);
```

> 🔍 **知识点深度解析**
>
> **作用**：Redis 是分布式环境下 Session 和共享数据的标准存储。Spring Session 透明替换 HttpSession，实现多实例 Session 共享。验证码、Token 等临时数据也存在 Redis。
>
> **原理**：Spring Session 通过 Filter 包装 HttpSession，将 Session 数据存到 Redis（key=spring:session:sessions:sessionId，Hash 结构存属性）。每个请求从 Redis 加载 Session，响应时写回。Session 过期由 Redis TTL 管理（maxInactiveIntervalInSeconds）。多实例部署时，所有实例共享同一个 Redis，Session 不丢失（不需要粘性会话）。验证码：key=sms:code:手机号，value=验证码，TTL=5分钟，验证后删除。Token：key=token:uuid，value=userId，TTL=7天，实现无状态登录（JWT 也可，但 Redis Token 可主动失效）。
>
> **用法要点**：① 分布式 Session 用 Spring Session + Redis（不要用容器 Session，多实例不共享）；② Session 中不要存大对象（序列化开销大）；③ 验证码用 Redis（TTL 自动过期，不需要定时清理）；④ 登录 Token 用 Redis（可主动踢人下线，JWT 做不到）；⑤ Session 序列化用 JSON（默认 JDK 序列化，可读性差）；⑥ Redis 高可用（哨兵/集群），否则 Session 丢失影响登录；⑦ 敏感数据（密码）不要存 Session/Redis。

### 3.6 发布订阅（Pub/Sub）

```java
// 发布
redisTemplate.convertAndSend("channel:news", "Hello Redis!");

// 订阅（消息监听器）
@Configuration
public class PubSubConfig {
    @Bean
    public RedisMessageListenerContainer container(RedisConnectionFactory factory) {
        RedisMessageListenerContainer container = new RedisMessageListenerContainer();
        container.setConnectionFactory(factory);
        container.addMessageListener(new MessageListenerAdapter(new NewsSubscriber()), 
            new PatternTopic("channel:*"));
        return container;
    }
}

@Component
public class NewsSubscriber {
    public void handleMessage(String message) {
        System.out.println("收到消息: " + message);
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：Pub/Sub 实现发布订阅模式，一对多消息广播。适合实时通知、配置刷新、事件广播等场景。但消息不持久化（订阅者不在线就丢了）。
>
> **原理**：Redis Pub/Sub：发布者 PUBLISH channel message，所有订阅该 channel 的订阅者收到消息。Redis 维护频道订阅字典（channel→订阅者列表），发布时遍历列表发送。模式订阅（PSUBSCRIBE channel:*）用模式匹配。消息不持久化：发布时订阅者在线才收到，不在线则丢失（不像 MQ 有队列存储）。7.0+ Sharded Pub/Sub：分片发布订阅，消息只在负责该 slot 的节点传播（Cluster 模式下更高效）。
>
> **用法要点**：① Pub/Sub 适合实时通知（不要求可靠送达）；② 不要用 Pub/Sub 做可靠消息队列（消息不持久化，订阅者离线丢）；③ 配置刷新：Spring Cloud Bus 用 Redis Pub/Sub 广播配置变更；④ 事件广播：多实例缓存失效通知（删本地缓存）；⑤ 订阅者要处理异常（异常不影响其他订阅者）；⑥ Cluster 模式用 Sharded Pub/Sub（7.0+）或普通 Pub/Sub（全节点广播）；⑦ 可靠消息用 Stream 或专业 MQ。

### 3.7 位图与基数统计

```java
// Bitmap 签到
String key = "sign:user:1:202401";
redisTemplate.opsForValue().setBit(key, 1, true);  // 1号签到
redisTemplate.opsForValue().setBit(key, 2, true);  // 2号签到
boolean signed = redisTemplate.opsForValue().getBit(key, 1); // 检查是否签到

// 统计签到天数（BITCOUNT）
Long signDays = redisTemplate.execute((RedisCallback<Long>) conn -> 
    conn.bitCount(key.getBytes()));

// HyperLogLog 统计 UV（不精确，误差0.81%，但极省内存）
redisTemplate.opsForHyperLogLog().add("uv:page:home", "user:1", "user:2", "user:1");
long uv = redisTemplate.opsForHyperLogLog().size("uv:page:home"); // 结果=2

// 合并多个 HLL
redisTemplate.opsForHyperLogLog().union("uv:total", "uv:page:home", "uv:page:detail");
```

> 🔍 **知识点深度解析**
>
> **作用**：Bitmap 用位存储布尔状态（签到/活跃），极省内存（1亿用户每天签到约12MB）。HyperLogLog 用极小内存统计基数（UV），误差可接受（0.81%），适合大规模统计。
>
> **原理**：Bitmap：String 的位操作，SETBIT key offset value 设置第 offset 位为 0/1，GETBIT 获取，BITCOUNT 统计 1 的个数，BITOP 做位运算（AND/OR/XOR）。1亿个布尔值只需 12.5MB（1亿/8字节）。HyperLogLog：基于概率算法，用 16384 个寄存器（每个6位，共12KB），通过哈希值前导零个数估计基数。无论数据量多大，固定 12KB 内存，标准误差 0.81%。PFMERGE 合并多个 HLL（求并集基数）。适合统计 UV、DAU 等不需要精确值的场景。
>
> **用法要点**：① 签到/活跃用 Bitmap（offset=日期或用户ID，1位=1个状态）；② 连续签到：BITMAP 按天存，用 BITOP AND 计算连续签到天数；③ UV 统计用 HyperLogLog（12KB 统计任意量级，误差0.81%可接受）；④ 需要精确计数用 Set（但内存大）或数据库；⑤ HLL 合并：PFMERGE 求多页面总 UV；⑥ Bitmap 的 offset 是无符号整数（最大 2^32-1，约512MB）；⑦ 不要用 HLL 做精确统计（有误差，财务/计费不能用）。

### 3.8 性能优化

```java
// 1. 批量操作（减少网络往返）
redisTemplate.opsForValue().multiSet(map);  // 批量 SET
List<Object> values = redisTemplate.opsForValue().multiGet(keys); // 批量 GET

// 2. Pipeline（管道，批量发送命令）
List<Object> results = redisTemplate.executePipelined((RedisCallback<Object>) conn -> {
    keys.forEach(k -> conn.get(k.getBytes()));
    return null;
});

// 3. Lua 脚本（原子操作，减少网络往返）
DefaultRedisScript<Long> script = new DefaultRedisScript<>();
script.setScriptText("if redis.call('get', KEYS[1]) == ARGV[1] then " +
    "return redis.call('del', KEYS[1]) else return 0 end");
script.setResultType(Long.class);
Long result = redisTemplate.execute(script, List.of("lock:1"), "uuid");

// 4. 连接池配置（Lettuce）
LettuceClientConfiguration config = LettuceClientConfiguration.builder()
    .commandTimeout(Duration.ofSeconds(3))
    .build();
```

> 🔍 **知识点深度解析**
>
> **作用**：Redis 性能优化核心是减少网络往返（批量/Pipeline/Lua）和合理配置连接池。单条命令很快，但大量小命令的网络开销是瓶颈。
>
> **原理**：批量操作（MSET/MGET）：一条命令处理多个 key，一次网络往返。Pipeline：客户端批量发送多条命令，不等待每条响应，最后一次性收响应（减少网络往返，非原子，命令之间无依赖时用）。Lua 脚本：EVAL 执行 Lua 脚本，脚本在 Redis 服务端原子执行（不会被其他命令打断），可实现复杂原子逻辑（如分布式锁释放：判断 value 再 del），同时减少网络往返。连接池：Lettuce 默认共享连接（异步非阻塞，一个连接足够），Jedis 用连接池（同步阻塞，需要多连接）。大 key：单个 key value 过大（>10KB）会阻塞网络和删除，要拆分。
>
> **用法要点**：① 批量操作用 MSET/MGET（同类型命令）；② 多条不同命令用 Pipeline（非原子，无依赖）；③ 原子复杂逻辑用 Lua 脚本（如限流、锁释放、扣库存）；④ 不要用大 key（>10KB），Hash/List/ZSet 元素过多也要拆分；⑤ 不要用 KEYS *（阻塞主线程），用 SCAN 迭代；⑥ 连接超时设合理值（3秒左右，不要太长）；⑦ 客户端用 Lettuce（Spring Boot 默认，异步非阻塞，性能好）或 Redisson（功能丰富）；⑧ 监控慢查询（SLOWLOG GET），优化大 key 和复杂命令。

---


---
## 4. 注意事项

1. **缓存和数据库一致性**：用 Cache Aside（先更新 DB 再删缓存），一致性要求高用延迟双删或 binlog 监听。

2. **避免大 key**：单个 key value >10KB 或 Hash/List/ZSet 元素过多，会阻塞网络和删除。拆分或用合适结构。

3. **避免热 key**：某个 key 访问量极大（如秒杀商品），单节点瓶颈。本地缓存（Caffeine）+ Redis，或 key 分片（hotkey:1, hotkey:2）。

4. **不要用 KEYS ***：阻塞主线程，生产禁用。用 SCAN 迭代（非阻塞）。

5. **过期键删除阻塞**：大 key 过期删除可能阻塞主线程，开启 lazyfree-lazy-expire yes（异步删除）。

6. **持久化 fork 阻塞**：大内存实例 bgsave/bgrewriteaof fork 耗时（可能秒级），注意 maxmemory 和 fork 内存。

7. **Cluster 多键操作**：跨槽的多键操作（MGET/事务）不支持，用 Hash Tag 让相关 key 同槽。

8. **内存设置**：maxmemory 设为物理内存 70-80%，留内存给 OS 和 fork。不要设满（OOM 风险）。

9. **连接数限制**：maxclients 默认 10000，应用连接池总和不要超过。监控 connected_clients。

10. **慢查询监控**：SLOWLOG GET 查看慢命令，优化大 key、复杂 Lua、全量遍历。

11. **不要用 Redis 存强一致数据**：缓存是最终一致，账户余额、库存等用数据库（Redis 可做辅助计数但最终以 DB 为准）。

12. **安全配置**：生产必须设密码（requirepass）、绑定内网 IP（bind）、禁用危险命令（rename-command FLUSHALL ""）。

---

> 💡 **深度讲解**：Redis 是基于内存的高性能 KV 数据库，核心是丰富的数据结构（String/Hash/List/Set/ZSet+Bitmap/HLL/Geo/Stream）和高可用方案（主从/哨兵/Cluster）。数据结构底层用多种编码（ziplist/quicklist/skiplist/hashtable）自动优化，小数据量用压缩编码省内存，大数据量转高效结构。持久化用 RDB（快照，恢复快）+ AOF（日志，数据安全），4.0+ 混合持久化兼顾两者。过期策略用惰性删除+定期删除，内存淘汰用 LRU/LFU（缓存场景用 allkeys-lfu）。缓存三大问题：穿透（布隆过滤器+空值）、击穿（互斥锁+逻辑过期）、雪崩（TTL随机+高可用+限流）。分布式锁用 Redisson（可重入+看门狗续期），不要自己实现。高可用：中小规模用哨兵（自动故障转移），大规模用 Cluster（16384槽分片，水平扩展）。性能优化核心是减少网络往返（批量/Pipeline/Lua）和避免大 key/热 key。生产注意：缓存一致性、持久化 fork 阻塞、内存设置、安全配置、慢查询监控。Redis 是缓存首选，但不要用它做存储（数据安全不如数据库）和强一致场景。
>
> **📝 精简总结**：Redis=内存KV+丰富数据结构+高可用；结构=String/Hash/List/Set/ZSet+Bitmap/HLL/Geo/Stream；持久化=RDB(快照)+AOF(日志)+混合；高可用=主从+哨兵(中小)/Cluster(16384槽,大规模)；缓存=Cache Aside(先DB后删缓存)，穿透(布隆+空值)/击穿(锁+逻辑过期)/雪崩(TTL随机+限流)；锁=Redisson(可重入+看门狗)；优化=批量/Pipeline/Lua+避免大key热key；注意=缓存一致性/内存设置/安全/慢查询。

---

> 📋 **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 知识点深度解析」模块（作用+原理+用法要点），原有内联图已统一风格化美化（圆角、阴影、渐变、动画）。所有原有内容完整保留，未做任何修改。
