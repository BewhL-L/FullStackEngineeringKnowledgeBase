---
title: 分布式 ID 生成方案
tags: [分布式, 雪花算法, 原子笔记]
category: 分布式与中间件
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[分布式锁原理与实现]]", "[[微服务架构核心概念]]"]
aliases: [分布式ID生成方案]
---

# 分布式 ID 生成方案

> **文档说明**：系统讲解分布式系统中唯一 ID 生成的各种方案，包括 UUID、数据库自增、号段模式、Redis 原子操作、雪花算法（Snowflake）、美团 Leaf、百度 UidGenerator，以及各方案的优缺点对比、选型建议和生产环境实践。
>
> **适用人群**：后端开发工程师、分布式系统架构师、需要设计分布式 ID 方案的开发者
>
> **前置知识**：[[分布式锁原理与实现]]、[[微服务架构核心概念]]、[[高并发系统设计案例]]

---

## 一、概述

在分布式系统中，多个服务实例同时运行，传统的数据库自增 ID 无法满足全局唯一的需求。**分布式 ID 生成**是分布式系统的基础组件，用于生成全局唯一、趋势递增、高性能的 ID。

### 1. 分布式 ID 的核心要求

| 要求 | 说明 | 重要性 |
|------|------|--------|
| **全局唯一** | ID 在整个分布式系统中唯一，不重复 | 必须 |
| **高性能** | 生成速度快，延迟低，支持高并发 | 必须 |
| **高可用** | ID 生成服务不能成为单点故障 | 必须 |
| **趋势递增** | ID 整体趋势递增（不一定严格连续），利于数据库索引 | 重要 |
| **单调递增** | 下一个 ID 一定大于上一个（严格递增） | 可选 |
| **信息安全** | ID 不暴露业务信息（如订单量、用户量），不被猜测 | 重要 |
| **可读性** | ID 有一定含义（如包含时间、业务标识） | 可选 |
| **长度适中** | ID 不宜过长，存储和传输成本低 | 重要 |

### 2. ID 类型选择

| ID 类型 | 示例 | 优点 | 缺点 | 适用场景 |
|---------|------|------|------|---------|
| **纯数字长整型** | 1234567890123456 | 存储小（8字节）、索引快、趋势递增 | 信息暴露（可推断数量） | 数据库主键、订单号 |
| **UUID 字符串** | 550e8400-e29b-41d4-a716-446655440000 | 全局唯一、无中心、生成快 | 无序（索引性能差）、长度大（36字符）、不可读 | 非数据库主键、日志ID、消息ID |
| **带业务前缀** | ORD202608270001 | 可读性强、含业务信息 | 长度大、需业务编码 | 订单号、流水号、工单号 |
| **短ID/编码ID** | aZ3kL9 | 短、URL友好 | 容量有限、需编码 | 短链接、分享链接、邀请码 |

---

## 二、主流方案详解

### 1. UUID（Universally Unique Identifier）

**UUID** 是一种标准化的 128 位全局唯一标识符，无需中心节点即可生成。

**UUID 版本**：

| 版本 | 算法 | 说明 |
|------|------|------|
| **UUID v1** | 时间戳 + MAC 地址 | 基于时间和机器MAC，趋势递增，但暴露MAC |
| **UUID v2** | DCE 安全版本 | 很少使用 |
| **UUID v3** | MD5 哈希 | 基于命名空间和名称的 MD5 哈希 |
| **UUID v4** | 随机数 | 完全随机，最常用 |
| **UUID v5** | SHA-1 哈希 | 基于命名空间和名称的 SHA-1 哈希 |
| **UUID v6/v7/v8** | 新提案 | 时间有序的 UUID（v7 基于 Unix 时间戳） |

**Java 生成 UUID**：
```java
// v4 随机 UUID（最常用）
UUID uuid = UUID.randomUUID();
String id = uuid.toString(); // "550e8400-e29b-41d4-a716-446655440000"

// 去掉横线
String compactId = uuid.toString().replace("-", ""); // "550e8400e29b41d4a716446655440000"

// v3（基于名称）
UUID nameUuid = UUID.nameUUIDFromBytes("user:1001".getBytes());
```

| 优点 | 缺点 |
|------|------|
| 生成简单，本地生成无网络开销 | 无序，数据库索引性能差（B+Tree 频繁分裂） |
| 全局唯一（概率上） | 长度大（36字符），存储和传输成本高 |
| 无中心节点，无单点故障 | v4 完全随机，无业务含义 |
| 各语言都有标准库支持 | v1 暴露 MAC 地址，有安全风险 |

**适用场景**：非数据库主键的场景，如日志 ID、消息 ID、追踪 ID、临时文件名。

**不适用**：数据库主键（无序导致索引性能差）、需要趋势递增的场景。

### 2. 数据库自增 ID

利用数据库的自增主键特性生成 ID。

**方案1：单库自增**
```sql
CREATE TABLE id_generator (
    id BIGINT NOT NULL AUTO_INCREMENT,
    stub CHAR(1) NOT NULL DEFAULT '',
    PRIMARY KEY (id),
    UNIQUE KEY uk_stub (stub)
) ENGINE=InnoDB;

-- 生成 ID
INSERT INTO id_generator (stub) VALUES ('a');
SELECT LAST_INSERT_ID(); -- 获取自增 ID
```

**方案2：多库多实例（步长递增）**

为避免单点，部署多个数据库实例，每个实例设置不同的起始值和步长：

```sql
-- 实例1
SET @@auto_increment_offset = 1;
SET @@auto_increment_increment = 3;  -- 步长3
-- 生成：1, 4, 7, 10, ...

-- 实例2
SET @@auto_increment_offset = 2;
SET @@auto_increment_increment = 3;
-- 生成：2, 5, 8, 11, ...

-- 实例3
SET @@auto_increment_offset = 3;
SET @@auto_increment_increment = 3;
-- 生成：3, 6, 9, 12, ...
```

| 优点 | 缺点 |
|------|------|
| 实现简单，ID 单调递增 | 数据库成为瓶颈，高并发下性能差 |
| ID 连续，无空洞 | 单点故障（单库），多库扩容复杂 |
| 数字类型，索引性能好 | 水平扩展困难（需提前规划实例数） |
| | 暴露业务信息（ID 可推断订单量） | |

**适用场景**：并发量不高、对 ID 连续性要求高的中小型系统。

### 3. Redis 原子操作

利用 Redis 的 `INCR` 命令原子递增生成 ID。

```java
// 简单自增
Long id = redisTemplate.opsForValue().increment("id:order");

// 带前缀的自增（按日期/业务分类）
String key = "id:order:" + LocalDate.now().format(DateTimeFormatter.BASIC_ISO_DATE);
Long id = redisTemplate.opsForValue().increment(key);
// 生成：20260827000001 格式的订单号

// 带过期时间（每天重置）
redisTemplate.opsForValue().increment(key);
redisTemplate.expire(key, 2, TimeUnit.DAYS);
```

**Redis 集群模式下的 ID 生成**：
Redis Cluster 不支持跨节点的原子操作，需要使用 Hash Tag 确保同一个 key 落在同一个节点：
```text
key = "{id}:order"  // {id} 是 hash tag，确保路由到同一 slot
```

| 优点 | 缺点 |
|------|------|
| 性能极高（Redis 10万+ QPS） | Redis 宕机可能导致 ID 丢失或重复 |
| 原子操作，无并发问题 | 需要持久化（AOF/RDB），但仍有丢失风险 |
| 可按业务/日期分类生成 | 依赖 Redis，增加运维成本 |
| 实现简单 | ID 不全局唯一（需配合业务前缀） |

**适用场景**：高并发、对 ID 唯一性要求不是绝对严格的场景（如流水号、订单号）。

**注意**：Redis 生成的 ID 需要配合业务前缀（如日期+业务码）才能保证全局唯一。

### 4. 号段模式（Segment）

号段模式是数据库自增的优化版：每次从数据库获取一个号段（如 1000 个 ID），在内存中分配，用完再取下一个号段。

**原理**：
```text
数据库表：max_id 记录当前最大 ID，step 记录号段大小
1. 服务启动时，从数据库获取号段：UPDATE max_id = max_id + step
2. 内存中持有 [max_id - step + 1, max_id] 号段
3. 服务从号段中依次分配 ID
4. 号段用完后，再次从数据库获取新号段
```

**数据库表设计**：
```sql
CREATE TABLE id_segment (
    biz_type VARCHAR(64) NOT NULL COMMENT '业务类型',
    max_id BIGINT NOT NULL DEFAULT 0 COMMENT '当前最大ID',
    step INT NOT NULL DEFAULT 1000 COMMENT '号段大小',
    description VARCHAR(255) COMMENT '描述',
    update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (biz_type)
) ENGINE=InnoDB COMMENT='号段模式ID生成表';
```

**Java 实现**：
```java
public class SegmentIdGenerator {
    private final String bizType;
    private final JdbcTemplate jdbcTemplate;
    private volatile Segment currentSegment;
    private volatile Segment nextSegment;
    private final AtomicBoolean loading = new AtomicBoolean(false);

    public SegmentIdGenerator(String bizType, JdbcTemplate jdbcTemplate) {
        this.bizType = bizType;
        this.jdbcTemplate = jdbcTemplate;
        this.currentSegment = loadNextSegment();
    }

    public long nextId() {
        // 当前号段还有 ID
        if (currentSegment.hasNext()) {
            return currentSegment.next();
        }
        // 当前号段用完，切换到下一个号段
        synchronized (this) {
            if (currentSegment.hasNext()) {
                return currentSegment.next();
            }
            if (nextSegment != null) {
                currentSegment = nextSegment;
                nextSegment = null;
            } else {
                currentSegment = loadNextSegment();
            }
        }
        return currentSegment.next();
    }

    // 双buffer：当前号段用到 10% 时，异步加载下一个号段
    private void tryLoadNextSegment() {
        if (currentSegment.getUsageRatio() > 0.9 && nextSegment == null && loading.compareAndSet(false, true)) {
            CompletableFuture.runAsync(() -> {
                try {
                    nextSegment = loadNextSegment();
                } finally {
                    loading.set(false);
                }
            });
        }
    }

    private Segment loadNextSegment() {
        // 事务内更新 max_id 并获取新号段
        return jdbcTemplate.execute((Connection conn) -> {
            conn.setAutoCommit(false);
            try {
                // 行锁，防止并发获取相同号段
                jdbcTemplate.update("UPDATE id_segment SET max_id = max_id + step WHERE biz_type = ?", bizType);
                Map<String, Object> row = jdbcTemplate.queryForMap(
                    "SELECT max_id, step FROM id_segment WHERE biz_type = ?", bizType);
                long maxId = ((Number) row.get("max_id")).longValue();
                int step = ((Number) row.get("step")).intValue();
                conn.commit();
                return new Segment(maxId - step + 1, maxId);
            } catch (Exception e) {
                conn.rollback();
                throw e;
            }
        });
    }
}

class Segment {
    private final long start;
    private final long end;
    private final AtomicLong current;

    public Segment(long start, long end) {
        this.start = start;
        this.end = end;
        this.current = new AtomicLong(start);
    }

    public boolean hasNext() {
        return current.get() <= end;
    }

    public long next() {
        return current.getAndIncrement();
    }

    public double getUsageRatio() {
        return (double)(current.get() - start) / (end - start + 1);
    }
}
```

| 优点 | 缺点 |
|------|------|
| 性能高（内存分配，只有号段用完才查DB） | 服务重启可能丢失号段（ID 不连续） |
| ID 趋势递增 | 数据库仍可能成为瓶颈（号段用完时） |
| 数据库压力小（每 1000 个 ID 才查一次 DB） | 实现稍复杂 |
| 支持多业务类型（按 biz_type 分类） | 号段大小需合理设置（太大浪费，太小频繁查DB） |
| 高可用（数据库主从+多服务实例） | |

**适用场景**：中大型系统，对 ID 趋势递增有要求，并发量较高。美团 Leaf、百度 UidGenerator 都基于号段模式。

### 5. 雪花算法（Snowflake）

**雪花算法**是 Twitter 开源的分布式 ID 生成算法，生成 64 位的 long 型 ID，是目前最主流的分布式 ID 方案。

**64 位结构**：
```text
0 | 0000000000 0000000000 0000000000 0000000000 0 | 00000 | 00000 | 000000000000
│                     │                                    │       │       │
│  41位时间戳（毫秒级）                                  5位    5位    12位序列号
│                     │                               数据中心  机器ID  (每毫秒4096个)
1位符号位(0，正数)    │                               (最多32) (最多32)
                  可用约69年
```

| 位段 | 位数 | 说明 | 取值范围 |
|------|------|------|---------|
| **符号位** | 1位 | 固定为 0，表示正数 | 0 |
| **时间戳** | 41位 | 毫秒级时间戳（相对于起始时间） | 可用约 69 年（2^41 / (365×24×3600×1000) ≈ 69.7年） |
| **数据中心 ID** | 5位 | 数据中心/机房标识 | 0~31（最多 32 个数据中心） |
| **机器 ID** | 5位 | 机器/实例标识 | 0~31（每个数据中心最多 32 台机器） |
| **序列号** | 12位 | 同一毫秒内的序列号 | 0~4095（每毫秒最多 4096 个 ID） |

**理论性能**：
- 单台机器：4096 ID/毫秒 = 409.6 万 ID/秒
- 32 数据中心 × 32 机器 = 1024 台机器
- 总理论峰值：1024 × 409.6万 ≈ 41.9 亿 ID/秒

**Java 实现**：
```java
public class SnowflakeIdGenerator {
    // 起始时间戳（2020-01-01 00:00:00），可使用约69年到2089年
    private static final long START_TIMESTAMP = 1577836800000L;

    // 各部分位数
    private static final long WORKER_ID_BITS = 5L;
    private static final long DATACENTER_ID_BITS = 5L;
    private static final long SEQUENCE_BITS = 12L;

    // 最大值
    private static final long MAX_WORKER_ID = ~(-1L << WORKER_ID_BITS);  // 31
    private static final long MAX_DATACENTER_ID = ~(-1L << DATACENTER_ID_BITS);  // 31

    // 左移位数
    private static final long WORKER_ID_SHIFT = SEQUENCE_BITS;  // 12
    private static final long DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS;  // 17
    private static final long TIMESTAMP_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS;  // 22

    // 序列号掩码
    private static final long SEQUENCE_MASK = ~(-1L << SEQUENCE_BITS);  // 4095

    private final long workerId;
    private final long datacenterId;
    private long sequence = 0L;
    private long lastTimestamp = -1L;

    public SnowflakeIdGenerator(long workerId, long datacenterId) {
        if (workerId > MAX_WORKER_ID || workerId < 0) {
            throw new IllegalArgumentException("workerId 超出范围");
        }
        if (datacenterId > MAX_DATACENTER_ID || datacenterId < 0) {
            throw new IllegalArgumentException("datacenterId 超出范围");
        }
        this.workerId = workerId;
        this.datacenterId = datacenterId;
    }

    public synchronized long nextId() {
        long timestamp = currentTimeMillis();

        // 时钟回拨检测
        if (timestamp < lastTimestamp) {
            long offset = lastTimestamp - timestamp;
            if (offset <= 5) {
                // 回拨小于5ms，等待
                try {
                    wait(offset << 1);
                    timestamp = currentTimeMillis();
                    if (timestamp < lastTimestamp) {
                        throw new RuntimeException("时钟回拨，拒绝生成ID");
                    }
                } catch (InterruptedException e) {
                    throw new RuntimeException("等待时钟恢复被中断", e);
                }
            } else {
                throw new RuntimeException("时钟回拨超过5ms，拒绝生成ID");
            }
        }

        // 同一毫秒内，序列号递增
        if (timestamp == lastTimestamp) {
            sequence = (sequence + 1) & SEQUENCE_MASK;
            // 序列号溢出（超过4095），等待下一毫秒
            if (sequence == 0) {
                timestamp = tilNextMillis(lastTimestamp);
            }
        } else {
            // 不同毫秒，序列号重置
            sequence = 0L;
        }

        lastTimestamp = timestamp;

        // 拼接 ID
        return ((timestamp - START_TIMESTAMP) << TIMESTAMP_SHIFT)
                | (datacenterId << DATACENTER_ID_SHIFT)
                | (workerId << WORKER_ID_SHIFT)
                | sequence;
    }

    private long tilNextMillis(long lastTimestamp) {
        long timestamp = currentTimeMillis();
        while (timestamp <= lastTimestamp) {
            timestamp = currentTimeMillis();
        }
        return timestamp;
    }

    private long currentTimeMillis() {
        return System.currentTimeMillis();
    }
}
```

**使用示例**：
```java
// 数据中心0，机器1
SnowflakeIdGenerator generator = new SnowflakeIdGenerator(1, 0);
long id = generator.nextId();
// 输出：1234567890123456789（64位 long 型）
```

**从 ID 反解析信息**：
```java
public static void parseId(long id) {
    long sequence = id & 4095;
    long workerId = (id >> 12) & 31;
    long datacenterId = (id >> 17) & 31;
    long timestamp = (id >> 22) + START_TIMESTAMP;
    System.out.printf("时间: %s, 数据中心: %d, 机器: %d, 序列号: %d%n",
        new Date(timestamp), datacenterId, workerId, sequence);
}
```

| 优点 | 缺点 |
|------|------|
| 高性能（本地生成，无网络开销，409万/秒/机器） | 时钟回拨问题（需处理） |
| ID 趋势递增（时间戳在前，数据库索引性能好） | 机器 ID 需手动分配或借助注册中心 |
| 64位 long 型，存储小（8字节） | ID 可反解析时间/机器，有信息暴露风险 |
| 无中心节点，无单点故障 | 单机序列号有限（4096/毫秒），超高并发需多机器 |
| 可反解析生成时间/机器，便于排查 | 起始时间需统一，否则 ID 不唯一 |

**适用场景**：大多数分布式系统的数据库主键、订单号、消息 ID 等。是目前最主流的方案。

**时钟回拨问题处理**：
| 方案 | 说明 |
|------|------|
| **等待** | 回拨时间短（<5ms），等待时钟恢复 |
| **拒绝** | 回拨时间长，拒绝生成 ID，抛异常 |
| **备用号段** | 时钟回拨时使用预分配的号段 |
| **NTP 同步** | 配置 NTP 时间同步，减少回拨概率 |
| **关闭 NTP 校时** | 关闭自动校时，避免时钟跳变（但时钟会漂移） |

**机器 ID 分配方案**：
| 方案 | 说明 |
|------|------|
| **手动配置** | 配置文件写死 workerId，简单但扩容麻烦 |
| **注册中心** | 启动时从 ZooKeeper/Nacos/Consul 获取 workerId |
| **数据库** | 启动时从数据库获取自增 workerId |
| **IP 映射** | 根据 IP 地址后 5 位作为 workerId（需确保不冲突） |
| **容器环境** | K8s 中用 StatefulSet 的序号作为 workerId |

### 6. 美团 Leaf

**Leaf** 是美团开源的分布式 ID 生成服务，支持两种模式：号段模式（Leaf-segment）和雪花模式（Leaf-snowflake）。

| 特性 | 说明 |
|------|------|
| **Leaf-segment** | 号段模式，双 buffer 预加载，DB 号段表 |
| **Leaf-snowflake** | 雪花算法模式，借助 ZooKeeper 分配 workerId，时钟回拨处理 |
| **高可用** | 服务集群部署，数据库主从 |
| **HTTP API** | 提供 RESTful API 获取 ID |
| **监控告警** | 内置监控指标 |

### 7. 百度 UidGenerator

**UidGenerator** 是百度开源的分布式 ID 生成器，基于雪花算法改进，使用 RingBuffer 缓存预生成的 ID，性能极高（600万+/秒）。

| 特性 | 说明 |
|------|------|
| **RingBuffer** | 环形缓冲区预生成 ID，消费时直接取 |
| **时间精度** | 可配置为秒级（默认）或毫秒级 |
| **workerId** | 启动时从数据库获取，自动分配 |
| **性能** | 单实例 600万 ID/秒 |
| **时钟回拨** | 基于 RingBuffer，天然避免时钟回拨问题 |

---

## 三、方案对比与选型

### 1. 综合对比

| 方案 | 唯一性 | 性能 | 趋势递增 | 高可用 | 复杂度 | 信息安全 | 适用规模 |
|------|--------|------|---------|--------|--------|---------|---------|
| **UUID v4** | 概率唯一 | 极高（本地） | ❌ 无序 | ✅ 无中心 | 低 | ✅ 随机 | 任意 |
| **数据库自增** | ✅ 唯一 | 低（DB瓶颈） | ✅ 严格递增 | ⚠️ 单点 | 低 | ❌ 暴露数量 | 小型 |
| **多库步长** | ✅ 唯一 | 中 | ✅ 趋势递增 | ⚠️ 扩容难 | 中 | ❌ 暴露数量 | 中型 |
| **Redis INCR** | ✅ 唯一（加前缀） | 高 | ✅ 趋势递增 | ⚠️ 依赖Redis | 低 | ⚠️ 可推断 | 中大型 |
| **号段模式** | ✅ 唯一 | 高（内存分配） | ✅ 趋势递增 | ✅ 集群 | 中 | ❌ 暴露数量 | 中大型 |
| **雪花算法** | ✅ 唯一 | 极高（本地） | ✅ 趋势递增 | ✅ 无中心 | 中 | ⚠️ 可反解析 | 大型 |
| **美团 Leaf** | ✅ 唯一 | 高 | ✅ 趋势递增 | ✅ 集群 | 高 | ⚠️ 可反解析 | 大型 |
| **百度 UidGenerator** | ✅ 唯一 | 极高 | ✅ 趋势递增 | ✅ 集群 | 高 | ⚠️ 可反解析 | 超大型 |

### 2. 选型建议

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| **数据库主键（通用）** | 雪花算法 | 趋势递增、性能高、无中心、long 型索引好 |
| **高并发订单号** | 雪花算法 + 业务前缀 | 雪花 ID 保证唯一，前缀增加可读性 |
| **中小系统** | 数据库自增 / 号段模式 | 简单够用，ID 连续 |
| **日志/消息/追踪 ID** | UUID v4 | 无需数据库索引，本地生成简单 |
| **短链接/邀请码** | 雪花 ID + Base62 编码 | 数字 ID 编码为短字符串 |
| **金融/流水号** | 号段模式 + 日期前缀 | ID 连续可追溯，含日期信息 |
| **超大规模（亿级并发）** | 百度 UidGenerator / 美团 Leaf | 专业级 ID 服务，性能极高 |
| **K8s 容器环境** | 雪花算法（StatefulSet 序号作 workerId） | 容器环境天然有序号 |
| **需要 ID 可排序** | 雪花算法 / 号段模式 | 趋势递增，时间有序 |

### 3. 推荐组合方案

生产环境推荐使用**雪花算法作为基础**，配合以下增强：

```text
最终 ID = 业务前缀（可选） + 雪花算法 ID

示例：
- 纯数字主键：1234567890123456789（雪花 ID）
- 订单号：ORD202608271234567890（前缀+日期+雪花ID）
- 流水号：LS202608271234567890
- 用户ID：1000000000000000001（雪花ID，起始偏移）
```

**workerId 分配推荐**：
- K8s 环境：StatefulSet 序号（0~31）
- 虚拟机环境：启动时从 Nacos/ZooKeeper 获取
- 简单场景：配置文件手动分配（确保不重复）

---

## 四、生产环境实践

### 1. 雪花算法生产注意事项

- [ ] **统一起始时间**：所有服务使用相同的 START_TIMESTAMP，否则 ID 可能重复
- [ ] **workerId 唯一**：确保每个实例的 workerId 唯一，否则 ID 可能重复
- [ ] **时钟同步**：配置 NTP 时间同步，同时处理时钟回拨
- [ ] **序列号溢出**：同一毫秒超过 4096 个 ID 时等待下一毫秒
- [ ] **ID 长度**：long 型 ID 前端 JavaScript 可能精度丢失（JS Number 最大 2^53），需转字符串
- [ ] **监控告警**：监控 ID 生成速度、时钟回拨次数、号段使用情况

### 2. 前端 ID 精度问题

JavaScript 的 Number 类型最大安全整数是 `2^53 - 1 = 9007199254740991`，而雪花 ID 通常超过这个值，会导致精度丢失。

**解决方案**：
```java
// 方案1：后端将 ID 序列化为字符串（Jackson 注解）
@JsonSerialize(using = ToStringSerializer.class)
private Long id;

// 方案2：全局配置 Long 转 String
@Configuration
public class JacksonConfig {
    @Bean
    public Jackson2ObjectMapperBuilderCustomizer jacksonCustomizer() {
        return builder -> builder.serializerByType(Long.class, ToStringSerializer.instance);
    }
}

// 方案3：使用 String 类型 ID（但数据库索引性能稍差）
private String id;
```

### 3. 号段模式生产注意事项

- [ ] **号段大小合理**：step 太大浪费 ID，太小频繁查 DB（推荐 1000~10000）
- [ ] **双 buffer 预加载**：当前号段用到 10% 时异步加载下一个号段
- [ ] **数据库行锁**：获取号段时使用行锁防止并发冲突
- [ ] **服务重启**：重启后旧号段丢失（ID 不连续，但不影响唯一性）
- [ ] **监控号段使用率**：号段快用完时告警

---

## 五、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| ID 重复 | workerId 冲突 / 起始时间不一致 / 时钟回拨严重 | 确保 workerId 唯一，统一起始时间，处理时钟回拨 |
| ID 不递增 | 多机器生成 / 时钟回拨 | 雪花 ID 是趋势递增（非严格），单机器严格递增 |
| 前端 ID 精度丢失 | JS Number 精度不足（>2^53） | 后端将 Long 序列化为 String |
| 时钟回拨 | NTP 校时导致时钟跳变 | 等待/拒绝/备用号段，关闭 NTP 或配置平滑校时 |
| 号段模式 DB 压力大 | step 太小 / 并发获取号段 | 增大 step，双 buffer 预加载，数据库行锁 |
| Redis ID 丢失 | Redis 宕机 / 持久化不及时 | AOF 持久化，主从高可用，配合业务前缀 |
| UUID 索引性能差 | UUID 无序导致 B+Tree 频繁分裂 | 用雪花 ID 替代，或用 UUID v6/v7（时间有序） |
| workerId 不够用 | 5位 workerId 最多32台机器 | 调整位数分配（减少时间戳/序列号位数），或用数据中心+机器ID |
| ID 暴露业务信息 | 自增 ID 可推断订单量/用户量 | 用雪花 ID（不易推断），或 ID 加密/混淆 |
| 高并发下序列号溢出 | 单毫秒超过 4096 个请求 | 多机器负载均衡，或调整序列号位数 |

---

## 六、关联笔记

### 分布式
- [[分布式锁原理与实现]] · [[分布式事务解决方案]] · [[微服务架构核心概念]]
- [[配置中心实战]] · [[消息队列-Kafka与RabbitMQ]]

### 架构
- [[高可用架构设计]] · [[高并发系统设计案例]] · [[秒杀系统架构设计]]
- [[技术选型决策指南]]

### 后端
- [[SpringBoot-自动装配原理]] · [[MyBatis-核心原理与插件]] · [[Gateway-网关路由与鉴权]]
- [[数据库分库分表策略]] · [[关系型数据库索引原理]]

### 数据库
- [[Redis数据结构与应用场景]] · [[事务隔离级别与MVCC]] · [[MySQL-性能优化实战]]

### 实战
- [[秒杀系统架构设计]] · [[支付系统架构设计]] · [[统一AI网关设计与实现]]

### 导航
- [[MOC-后端开发]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[微服务架构核心概念]] 理解分布式系统 → 学习本文分布式 ID 生成 → 深入 [[分布式锁原理与实现]] 和 [[分布式事务解决方案]] 分布式核心 → 实践 [[高并发系统设计案例]] 和 [[秒杀系统架构设计]] 高并发场景 → 研究 [[高可用架构设计]] 系统稳定性。

---

## 💡 全文深度讲解

本文系统梳理了分布式 ID 生成方案的核心知识体系，从概述入手，深入主流方案详解的底层机制，再通过方案对比与选型掌握实战应用，最后涵盖常见问题与排查与关联笔记。学习时建议先建立整体认知，再动手实践，最后结合常见问题深化理解。

## 📝 全文精简总结

- **概述**：掌握本模块的核心概念与关键要点
- **主流方案详解**：掌握本模块的核心概念与关键要点
- **方案对比与选型**：掌握本模块的核心概念与关键要点
- **生产环境实践**：掌握本模块的核心概念与关键要点
- **常见问题与排查**：掌握本模块的核心概念与关键要点
- **关联笔记**：掌握本模块的核心概念与关键要点

