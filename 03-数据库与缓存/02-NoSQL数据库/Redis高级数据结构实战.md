---
title: Redis 高级数据结构实战
tags: [后端, Redis, 数据结构, 原子笔记]
category: 数据库与缓存
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[Redis缓存设计与优化]]", "[[Redis持久化与高可用]]"]
aliases: [Redis高级数据结构实战]
---

# Redis 高级数据结构实战

> **文档说明**：系统讲解 Redis 全部数据结构的高级用法与实战场景，包括 String（位图/计数器/分布式锁）、Hash（对象缓存/购物车）、List（队列/栈/最新列表）、Set（标签/共同好友/抽奖）、ZSet（排行榜/延时队列/范围查询）、Bitmap（签到/布隆过滤器）、HyperLogLog（UV 统计）、GEO（地理位置）、Stream（消息队列），以及底层编码原理和生产最佳实践。
>
> **适用人群**：Java 后端开发工程师、全栈开发者、需要深入使用 Redis 的工程师
>
> **前置知识**：[[Redis缓存设计与优化]]、[[Redis持久化与高可用]]、[[数据库优化知识点系统梳理_优化版]]

---

## 一、数据结构总览

### 1. Redis 数据结构分类

| 分类 | 数据结构 | 说明 |
|------|---------|------|
| **基础结构** | String | 字符串，最基础的数据类型 |
| | Hash | 哈希表，适合存储对象 |
| | List | 列表，双向链表 |
| | Set | 无序集合，自动去重 |
| | ZSet | 有序集合，带分数的 Set |
| **高级结构** | Bitmap | 位图，基于 String 的位操作 |
| | HyperLogLog | 基数统计，极小内存统计 UV |
| | GEO | 地理位置，基于 ZSet 实现 |
| | Stream | 消息队列，5.0+ 新增 |
| **模块扩展** | RedisJSON | JSON 文档存储（Redis Stack） |
| | RediSearch | 全文搜索引擎（Redis Stack） |
| | RedisBloom | 布隆过滤器（Redis Stack） |
| | RedisTimeSeries | 时序数据库（Redis Stack） |

### 2. 数据结构选型指南

| 场景 | 推荐结构 | 原因 |
|------|---------|------|
| 缓存对象 | Hash / String(JSON) | Hash 字段更新方便，String 序列化简单 |
| 计数器 | String(INCR) | 原子递增，高性能 |
| 分布式锁 | String(SET NX) | 原子设置，带过期时间 |
| 消息队列 | List / Stream | List 简单，Stream 功能完整（ACK/消费组） |
| 最新列表 | List(LPUSH+LTRIM) | 链表头部插入，保留最新 N 条 |
| 标签系统 | Set | 自动去重，交集并集运算 |
| 共同好友 | Set(SINTER) | 交集运算 |
| 抽奖系统 | Set(SPOP/SRANDMEMBER) | 随机弹出/获取 |
| 排行榜 | ZSet | 按分数排序，范围查询 |
| 延时队列 | ZSet(score=时间戳) | 按时间排序，轮询取到期任务 |
| 签到统计 | Bitmap | 位存储，极小内存 |
| UV 统计 | HyperLogLog | 12KB 内存统计海量基数 |
| 附近的人 | GEO | 地理位置半径查询 |
| 布隆过滤器 | Bitmap / RedisBloom | 快速判断元素是否存在 |

---

## 二、String 高级用法

### 1. 基本操作

```bash
# 基本读写
SET user:1:name "张三"
GET user:1:name
# "张三"

# 批量操作
MSET user:1:age 25 user:1:city "北京"
MGET user:1:name user:1:age user:1:city

# 不存在才设置（分布式锁基础）
SET lock:order:123 "uuid" NX EX 30
# NX: 不存在才设置，EX: 过期时间秒

# 追加
APPEND user:1:name "先生"
# "张三先生"

# 获取长度
STRLEN user:1:name
```

### 2. 计数器

```bash
# 文章阅读数
INCR article:1001:views
# (integer) 1
INCR article:1001:views
# (integer) 2

# 指定增量
INCRBY article:1001:views 10
# (integer) 12

# 浮点数
INCRBYFLOAT product:1:price 0.5
# "99.5"

# 递减
DECR stock:product:1
DECRBY stock:product:1 5
```

**Java 示例**：
```java
// 文章阅读数 +1（原子操作）
redisTemplate.opsForValue().increment("article:1001:views");

// 库存扣减（带判断，防止超卖）
Long stock = redisTemplate.opsForValue().decrement("stock:product:1");
if (stock != null && stock < 0) {
    // 库存不足，回滚
    redisTemplate.opsForValue().increment("stock:product:1");
    throw new BusinessException("库存不足");
}
```

### 3. 分布式锁

```bash
# 加锁（SET NX EX 原子操作）
SET lock:order:123 "unique-uuid" NX EX 30
# 成功返回 OK，失败返回 nil

# 释放锁（需校验 owner，Lua 脚本保证原子性）
EVAL "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end" 1 lock:order:123 "unique-uuid"
```

**Java 示例（Redisson）**：
```java
// Redisson 分布式锁（推荐，自动续期）
RLock lock = redissonClient.getLock("order:123");
try {
    // 尝试加锁，等待 10 秒，锁持有 30 秒
    boolean acquired = lock.tryLock(10, 30, TimeUnit.SECONDS);
    if (acquired) {
        // 执行业务逻辑
        processOrder("123");
    }
} finally {
    if (lock.isHeldByCurrentThread()) {
        lock.unlock();
    }
}
```

### 4. 对象缓存（JSON 序列化）

```java
// 缓存用户对象
User user = userService.getUser(1L);
redisTemplate.opsForValue().set("user:1", JSON.toJSONString(user), 1, TimeUnit.HOURS);

// 读取缓存
String json = (String) redisTemplate.opsForValue().get("user:1");
User user = JSON.parseObject(json, User.class);
```

---

## 三、Hash

### 1. 基本操作

```bash
# 设置字段
HSET user:1 name "张三" age 25 city "北京"
# (integer) 3

# 获取字段
HGET user:1 name
# "张三"

# 获取所有字段
HGETALL user:1
# 1) "name" 2) "张三" 3) "age" 4) "25" 5) "city" 6) "北京"

# 获取所有字段名
HKEYS user:1
# 获取所有值
HVALS user:1

# 字段数量
HLEN user:1
# (integer) 3

# 字段是否存在
HEXISTS user:1 age
# (integer) 1

# 删除字段
HDEL user:1 city

# 字段递增
HINCRBY user:1 age 1
HINCRBYFLOAT user:1 balance 10.5
```

### 2. 对象缓存

```java
// 使用 Hash 缓存用户对象（字段级更新）
Map<String, Object> userMap = new HashMap<>();
userMap.put("name", "张三");
userMap.put("age", 25);
userMap.put("city", "北京");
redisTemplate.opsForHash().putAll("user:1", userMap);

// 字段级更新（不需读取整个对象）
redisTemplate.opsForHash().put("user:1", "city", "上海");

// 读取
String name = (String) redisTemplate.opsForHash().get("user:1", "name");
Map<Object, Object> user = redisTemplate.opsForHash().entries("user:1");
```

**Hash vs String(JSON) 对比**：
| 维度 | Hash | String(JSON) |
|------|------|-------------|
| 字段更新 | 只需更新单个字段，性能高 | 需读取-修改-写回整个对象 |
| 内存占用 | 小（ziplist 编码） | 大（JSON 字符串） |
| 序列化 | 不需序列化 | 需 JSON 序列化/反序列化 |
| 复杂对象 | 不支持嵌套对象 | 支持任意复杂对象 |
| 过期时间 | 只能对整个 key 设置 TTL | 只能对整个 key 设置 TTL |
| 适用场景 | 扁平对象、字段经常单独更新 | 复杂对象、整体读写 |

### 3. 购物车

```bash
# 用户 1 的购物车：商品 ID -> 数量
HSET cart:1 product:1001 2 product:1002 1

# 添加商品
HINCRBY cart:1 product:1003 1

# 修改数量
HSET cart:1 product:1001 5

# 删除商品
HDEL cart:1 product:1002

# 购物车商品数量
HLEN cart:1

# 查看购物车
HGETALL cart:1
```

---

## 四、List

### 1. 基本操作

```bash
# 左侧插入（头部）
LPUSH queue:task "task1" "task2" "task3"
# 列表变为：task3, task2, task1

# 右侧插入（尾部）
RPUSH queue:task "task4"
# 列表变为：task3, task2, task1, task4

# 左侧弹出
LPOP queue:task
# "task3"

# 右侧弹出
RPOP queue:task
# "task4"

# 阻塞弹出（队列消费）
BRPOP queue:task 30
# 等待最多 30 秒，有元素立即返回

# 范围查询
LRANGE queue:task 0 -1  # 所有元素
LRANGE queue:task 0 9   # 前 10 个

# 长度
LLEN queue:task

# 保留前 N 个（最新列表）
LTRIM queue:task 0 99  # 只保留前 100 个

# 按索引获取
LINDEX queue:task 0

# 按索引设置
LSET queue:task 0 "new-task"
```

### 2. 消息队列（简单）

```bash
# 生产者：右侧插入
RPUSH queue:order "order-001"
RPUSH queue:order "order-002"

# 消费者：左侧阻塞弹出
BRPOP queue:order 0  # 0 表示无限等待
# 1) "queue:order" 2) "order-001"
```

**Java 示例**：
```java
// 生产者
redisTemplate.opsForList().rightPush("queue:order", "order-001");

// 消费者（阻塞）
List<String> result = redisTemplate.opsForList().brpop(30, TimeUnit.SECONDS, "queue:order");
if (result != null && result.size() == 2) {
    String orderId = result.get(1);
    processOrder(orderId);
}
```

### 3. 最新列表（时间线）

```bash
# 用户发布动态，左侧插入 + 修剪保留最新 100 条
LPUSH timeline:user:1 "动态内容1"
LTRIM timeline:user:1 0 99

# 查看最新 10 条
LRANGE timeline:user:1 0 9
```

### 4. 栈与队列

| 操作组合 | 数据结构 | 说明 |
|---------|---------|------|
| LPUSH + LPOP | 栈（Stack） | 后进先出 LIFO |
| LPUSH + RPOP | 队列（Queue） | 先进先出 FIFO |
| RPUSH + LPOP | 队列（Queue） | 先进先出 FIFO |
| RPUSH + RPOP | 栈（Stack） | 后进先出 LIFO |

---

## 五、Set

### 1. 基本操作

```bash
# 添加元素
SADD tags:article:1 "Java" "Spring" "Redis"
# (integer) 3

# 所有元素
SMEMBERS tags:article:1

# 元素数量
SCARD tags:article:1

# 是否存在
SISMEMBER tags:article:1 "Java"
# (integer) 1

# 删除元素
SREM tags:article:1 "Redis"

# 随机获取（不删除）
SRANDMEMBER tags:article:1
SRANDMEMBER tags:article:1 3  # 随机 3 个

# 随机弹出（删除）
SPOP tags:article:1
```

### 2. 集合运算

```bash
# 交集
SINTER tags:article:1 tags:article:2
# 共同标签

# 并集
SUNION tags:article:1 tags:article:2
# 所有标签（去重）

# 差集
SDIFF tags:article:1 tags:article:2
# article:1 有但 article:2 没有的标签

# 交集并存储到新 key
SINTERSTORE tags:common tags:article:1 tags:article:2

# 并集并存储
SUNIONSTORE tags:all tags:article:1 tags:article:2
```

### 3. 实战场景

**共同好友**：
```bash
# 用户好友列表
SADD friends:user1 "user2" "user3" "user4"
SADD friends:user2 "user1" "user3" "user5"

# 共同好友
SINTER friends:user1 friends:user2
# "user3"
```

**抽奖系统**：
```bash
# 奖池
SADD lottery:pool "user1" "user2" "user3" "user4" "user5"

# 随机抽 3 个中奖者（不删除）
SRANDMEMBER lottery:pool 3

# 抽取并移除（不重复中奖）
SPOP lottery:pool 3
```

**标签系统**：
```bash
# 文章标签
SADD tags:article:1 "Java" "Spring"
SADD tags:article:2 "Java" "Redis"

# 反向索引：标签 -> 文章
SADD tag:Java:articles article:1 article:2
SADD tag:Spring:articles article:1
SADD tag:Redis:articles article:2

# 查找同时包含 Java 和 Spring 的文章
SINTER tag:Java:articles tag:Spring:articles
# article:1
```

---

## 六、ZSet（有序集合）

### 1. 基本操作

```bash
# 添加元素（score 为分数）
ZADD ranking 100 "user1" 200 "user2" 150 "user3"
# (integer) 3

# 分数递增排序（从小到大）
ZRANGE ranking 0 -1 WITHSCORES
# 1) "user1" 2) "100" 3) "user3" 4) "150" 5) "user2" 6) "200"

# 分数递减排序（从大到小）
ZREVRANGE ranking 0 -1 WITHSCORES
# 1) "user2" 2) "200" 3) "user3" 4) "150" 5) "user1" 6) "100"

# 元素数量
ZCARD ranking

# 获取分数
ZSCORE ranking "user1"
# "100"

# 获取排名（从 0 开始）
ZRANK ranking "user1"     # 递增排名：0
ZREVRANK ranking "user1"  # 递减排名：2

# 分数递增
ZINCRBY ranking 50 "user1"
# "150"

# 删除元素
ZREM ranking "user1"

# 按分数范围查询
ZRANGEBYSCORE ranking 100 200 WITHSCORES
ZREVRANGEBYSCORE ranking 200 100

# 按分数范围删除
ZREMRANGEBYSCORE ranking 100 150

# 按排名范围删除
ZREMRANGEBYRANK ranking 0 1

# 分数范围内元素数量
ZCOUNT ranking 100 200
```

### 2. 排行榜

```bash
# 文章点赞排行榜
ZADD article:likes 100 article:1 200 article:2 150 article:3

# 点赞 +1
ZINCRBY article:likes 1 article:1

# Top 10 文章（按点赞数降序）
ZREVRANGE article:likes 0 9 WITHSCORES

# 查看某文章排名
ZREVRANK article:likes article:1

# 今日排行榜（按日期分 key）
ZADD ranking:20260827 100 user1 200 user2
```

**Java 示例**：
```java
// 点赞 +1
redisTemplate.opsForZSet().incrementScore("article:likes", "article:1", 1);

// Top 10
Set<ZSetOperations.TypedTuple<String>> top10 =
    redisTemplate.opsForZSet().reverseRangeWithScores("article:likes", 0, 9);

for (ZSetOperations.TypedTuple<String> tuple : top10) {
    System.out.println(tuple.getValue() + ": " + tuple.getScore());
}
```

### 3. 延时队列

```bash
# 延时队列：score = 执行时间戳（毫秒）
ZADD delay:queue 1724745600000 "task1"  # 2026-08-27 00:00:00 执行
ZADD delay:queue 1724832000000 "task2"  # 2026-08-28 00:00:00 执行

# 消费者：轮询获取到期任务
ZRANGEBYSCORE delay:queue 0 1724745600000  # 获取当前时间之前的任务
# 取出后删除（需用 Lua 保证原子性）
EVAL "local tasks = redis.call('ZRANGEBYSCORE', KEYS[1], 0, ARGV[1]) if #tasks > 0 then redis.call('ZREM', KEYS[1], unpack(tasks)) end return tasks" 1 delay:queue 1724745600000
```

**Java 示例**：
```java
// 添加延时任务（30 分钟后执行）
long executeTime = System.currentTimeMillis() + 30 * 60 * 1000;
redisTemplate.opsForZSet().add("delay:queue", "task:001", executeTime);

// 消费者轮询
@Scheduled(fixedDelay = 1000)
public void consumeDelayQueue() {
    long now = System.currentTimeMillis();
    // 原子地获取并删除到期任务
    Set<String> tasks = redisTemplate.opsForZSet().rangeByScore("delay:queue", 0, now);
    if (tasks != null && !tasks.isEmpty()) {
        for (String task : tasks) {
            // 先删除再处理（避免重复消费）
            Long removed = redisTemplate.opsForZSet().remove("delay:queue", task);
            if (removed != null && removed > 0) {
                processTask(task);
            }
        }
    }
}
```

### 4. 范围查询（带分数过滤）

```bash
# 分数在 [100, 200] 的元素，跳过前 2 个，取 3 个
ZRANGEBYSCORE ranking 100 200 WITHSCORES LIMIT 2 3

# 按字典序范围查询（需分数相同）
ZRANGEBYLEX ranking [a [z
```

---

## 七、Bitmap（位图）

### 1. 基本操作

```bash
# 设置位（offset 从 0 开始）
SETBIT sign:user:1:202608 0 1   # 8月1日签到
SETBIT sign:user:1:202608 1 1   # 8月2日签到
SETBIT sign:user:1:202608 2 0   # 8月3日未签到

# 获取位
GETBIT sign:user:1:202608 0
# (integer) 1

# 统计 1 的数量（签到天数）
BITCOUNT sign:user:1:202608
# (integer) 2

# 位运算（AND/OR/XOR/NOT）
BITOP AND sign:common sign:user:1:202608 sign:user:2:202608
BITCOUNT sign:common  # 共同签到天数

# 第一个 1 或 0 的位置
BITPOS sign:user:1:202608 1   # 第一个签到的日期
BITPOS sign:user:1:202608 0   # 第一个未签到的日期
```

### 2. 签到系统

```java
// 用户签到（今天）
LocalDate today = LocalDate.now();
int dayOfMonth = today.getDayOfMonth() - 1;  // 0-based
String key = "sign:user:" + userId + ":" + today.format(DateTimeFormatter.ofPattern("yyyyMM"));
redisTemplate.opsForValue().setBit(key, dayOfMonth, true);

// 统计本月签到天数
long signDays = redisTemplate.execute((RedisCallback<Long>) conn ->
    conn.bitCount(key.getBytes())
);

// 连续签到天数（从今天往前数）
int continuousDays = 0;
for (int i = dayOfMonth; i >= 0; i--) {
    Boolean signed = redisTemplate.opsForValue().getBit(key, i);
    if (Boolean.TRUE.equals(signed)) {
        continuousDays++;
    } else {
        break;
    }
}
```

### 3. 布隆过滤器（简易版）

```java
// 添加元素（多个 hash 函数设置位）
public void addBloom(String key, String value) {
    int[] offsets = getHashOffsets(value, 10000, 3);  // 3 个 hash 函数
    for (int offset : offsets) {
        redisTemplate.opsForValue().setBit(key, offset, true);
    }
}

// 判断元素是否可能存在（可能误判，不会漏判）
public boolean mightContainBloom(String key, String value) {
    int[] offsets = getHashOffsets(value, 10000, 3);
    for (int offset : offsets) {
        if (!Boolean.TRUE.equals(redisTemplate.opsForValue().getBit(key, offset))) {
            return false;  // 一定不存在
        }
    }
    return true;  // 可能存在
}
```

**Bitmap 内存占用**：1 亿用户的签到数据只需 `100000000 / 8 = 12.5 MB`，非常节省内存。

---

## 八、HyperLogLog

### 1. 基本操作

```bash
# 添加元素
PFADD uv:page:20260827 "user1" "user2" "user3" "user1"  # user1 重复，自动去重
# (integer) 1

# 统计基数（不重复元素数量）
PFCOUNT uv:page:20260827
# (integer) 3

# 合并多个 HyperLogLog
PFMERGE uv:week uv:page:20260821 uv:page:20260822 uv:page:20260823
PFCOUNT uv:week  # 一周总 UV
```

### 2. UV 统计

```java
// 记录用户访问（每次访问都添加，HyperLogLog 自动去重）
redisTemplate.opsForHyperLogLog().add("uv:page:" + today, userId);

// 统计今日 UV
long uv = redisTemplate.opsForHyperLogLog().size("uv:page:" + today);

// 合并一周 UV
redisTemplate.opsForHyperLogLog().union("uv:week",
    "uv:page:20260821", "uv:page:20260822", "uv:page:20260823",
    "uv:page:20260824", "uv:page:20260825", "uv:page:20260826", "uv:page:20260827");
long weekUv = redisTemplate.opsForHyperLogLog().size("uv:week");
```

**HyperLogLog 特点**：
- 固定内存：每个 key 只需 12KB
- 标准误差：0.81%（统计 100 万 UV，误差约 8100）
- 不存储原始数据：无法获取具体元素列表
- 适用场景：UV 统计、海量数据基数估算

---

## 九、GEO（地理位置）

### 1. 基本操作

```bash
# 添加地理位置（经度 纬度 名称）
GEOADD stores 116.404 39.915 "store1" 116.414 39.925 "store2" 116.424 39.935 "store3"

# 获取坐标
GEOPOS stores "store1"
# 1) 1) "116.40400046110153" 2) "39.91500058150189"

# 计算两点距离
GEODIST stores "store1" "store2" km
# "1.4014" (公里)
GEODIST stores "store1" "store2" m
# "1401.3552" (米)

# 附近的人（半径查询）
GEORADIUS stores 116.404 39.915 5 km WITHDIST WITHCOORD ASC
# 查找 (116.404, 39.915) 半径 5 公里内的门店，按距离升序

# 根据成员查找附近
GEORADIUSBYMEMBER stores "store1" 5 km WITHDIST ASC

# 获取 GeoHash
GEOHASH stores "store1"
# "wx4g0b5x6u0"
```

### 2. 附近的人

```java
// 添加用户位置
redisTemplate.opsForGeo().add("users:location",
    new Point(116.404, 39.915), "user1");

// 查找附近 5 公里内的用户
Distance radius = new Distance(5, Metrics.KILOMETERS);
Circle circle = new Circle(new Point(116.404, 39.915), radius);
GeoResults<GeoLocation<String>> results =
    redisTemplate.opsForGeo().radius("users:location", circle,
        GeoRadiusCommandArgs.newGeoRadiusArgs()
            .includeDistance()
            .sortAscending()
            .limit(10));

for (GeoResult<GeoLocation<String>> result : results) {
    System.out.println(result.getContent().getName() + ": " + result.getDistance().getValue() + "km");
}
```

---

## 十、Stream（消息队列）

### 1. 基本操作

```bash
# 添加消息（* 表示自动生成 ID）
XADD orders * orderId "001" userId "user1" amount "100"
# "1724745600000-0"

# 查看消息
XRANGE orders - +  # 所有消息
XRANGE orders 1724745600000-0 +  # 从指定 ID 开始
XREVRANGE orders + -  # 逆序

# 消息长度
XLEN orders

# 删除消息
XDEL orders 1724745600000-0

# 修剪（保留最新 N 条）
XTRIM orders MAXLEN 1000
```

### 2. 消费组

```bash
# 创建消费组
XGROUP CREATE orders order-group 0  # 从开始消费
XGROUP CREATE orders order-group $  # 从最新开始消费（只消费新消息）

# 消费组读取消息
XREADGROUP GROUP order-group consumer1 COUNT 10 BLOCK 5000 STREAMS orders >
# > 表示读取未消费的消息

# 确认消息（ACK）
XACK orders order-group 1724745600000-0

# 查看消费组信息
XINFO GROUPS orders
XINFO CONSUMERS orders order-group

# 查看待处理消息（PEL）
XPENDING orders order-group

# 转移消息（消费者宕机后转移给其他消费者）
XCLAIM orders order-group consumer2 3600000 1724745600000-0
```

### 3. Stream vs List vs Kafka

| 维度 | List | Stream | Kafka |
|------|------|--------|-------|
| 消息持久化 | 是（Redis） | 是（Redis） | 是（磁盘） |
| 消费确认 | 不支持 | 支持（ACK） | 支持（Offset） |
| 消费组 | 不支持 | 支持 | 支持 |
| 消息回溯 | 不支持 | 支持（ID 范围） | 支持（Offset） |
| 死信队列 | 不支持 | 支持（PEL+转移） | 支持 |
| 吞吐量 | 高 | 高 | 极高 |
| 适用场景 | 简单队列 | 中等复杂度队列 | 大规模消息系统 |

---

## 十一、底层编码原理

### 1. 编码类型

| 数据结构 | 编码方式 | 说明 |
|---------|---------|------|
| String | int / embstr / raw | 整数用 int，短字符串用 embstr，长字符串用 raw |
| List | quicklist | 3.2+ 版本，ziplist + linkedlist 混合 |
| Hash | ziplist / hashtable | 元素少且值短用 ziplist，否则 hashtable |
| Set | intset / hashtable | 全是整数且数量少用 intset，否则 hashtable |
| ZSet | ziplist / skiplist | 元素少用 ziplist，否则 skiplist + hashtable |

### 2. 编码转换阈值

```bash
# 查看编码
OBJECT ENCODING user:1
# "ziplist" / "hashtable" / "skiplist" 等

# Hash 转换阈值（默认）
hash-max-ziplist-entries 512   # 元素超过 512 个
hash-max-ziplist-value 64       # 值长度超过 64 字节

# ZSet 转换阈值
zset-max-ziplist-entries 128
zset-max-ziplist-value 64

# Set 转换阈值
set-max-intset-entries 512
```

### 3. 跳表（Skiplist）

ZSet 使用跳表实现有序集合，跳表是一种多层链表结构，查找复杂度 O(log N)：

```text
Level 3: 1 ----------------> 10
Level 2: 1 ------> 5 ------> 10
Level 1: 1 -> 3 -> 5 -> 7 -> 10
```

- 查找：从最高层开始，比目标大则下降一层，比目标小则前进
- 插入：找到位置后插入，并随机决定新节点的层数
- 删除：找到节点后从各层删除

---

## 十二、生产最佳实践

### 1. Key 命名规范

- [ ] **统一前缀**：`业务:模块:ID`，如 `user:profile:1`、`order:detail:123`
- [ ] **使用冒号分隔**：Redis 约定使用 `:` 作为分隔符
- [ ] **避免过长**：Key 过长占用内存，建议不超过 100 字节
- [ ] **避免特殊字符**：不要使用空格、换行、特殊符号
- [ ] **包含时间维度**：按天/周/月分 key，如 `uv:page:20260827`
- [ ] **统一 TTL**：缓存数据必须设置过期时间

### 2. 内存优化

- [ ] **使用 Hash 代替 String**：小对象使用 Hash，ziplist 编码节省内存
- [ ] **合理设置编码阈值**：根据业务调整 `hash-max-ziplist-entries` 等参数
- [ ] **使用整数**：整数类型使用 int 编码，更省内存
- [ ] **避免大 Key**：单个 key 不超过 10KB，Hash/Set/ZSet 元素不超过 5000
- [ ] **定期清理**：设置合理 TTL，避免冷数据堆积
- [ ] **使用 Bitmap/HyperLogLog**：海量统计使用 Bitmap/HyperLogLog，极小内存

### 3. 性能优化

- [ ] **批量操作**：使用 MGET/MSET/HMSET 等批量命令，减少网络往返
- [ ] **Pipeline**：多条命令使用 Pipeline，减少 RTT
- [ ] **避免大 Key 操作**：HGETALL、SMEMBERS、LRANGE 全量查询可能阻塞
- [ ] **使用 UNLINK 代替 DEL**：大 key 异步删除，不阻塞主线程
- [ ] **合理选择数据结构**：根据场景选择最合适的数据结构
- [ ] **连接池优化**：合理设置 Redis 连接池大小

### 4. 常见坑

| 坑 | 说明 | 解决方案 |
|----|------|---------|
| **缓存穿透** | 查询不存在的数据，请求直达 DB | 布隆过滤器 / 缓存空值 |
| **缓存击穿** | 热点 key 过期，大量请求直达 DB | 互斥锁 / 永不过期 + 异步更新 |
| **缓存雪崩** | 大量 key 同时过期 | 随机过期时间 / 多级缓存 |
| **Big Key** | 单个 key 过大，操作阻塞 Redis | 拆分大 key / 异步删除 |
| **热 Key** | 单个 key 访问量过大 | 本地缓存 / 读写分离 / key 分片 |
| **事务不支持回滚** | Redis 事务中命令语法错误不回滚 | 命令执行前检查 / 使用 Lua 脚本 |
| **过期时间精度** | EXPIRE 精度为秒，PEXPIRE 精度为毫秒 | 需要毫秒精度用 PEXPIRE |
| **Hash 无法单独设置 TTL** | Hash 字段不能单独过期 | 拆分 key / 使用 ZSet 存储过期时间 |

---

## 十三、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **OOM 内存溢出** | 数据量过大 / 大 key 过多 / 未设置 TTL | 检查内存使用、清理大 key、设置 TTL、增加内存 |
| **慢查询** | 大 key 全量操作 / 复杂集合运算 / 命令使用不当 | 使用 SLOWLOG 查看、优化命令、拆分大 key |
| **连接超时** | 网络问题 / Redis 阻塞 / 连接池耗尽 | 检查网络、查看慢查询、调整连接池 |
| **主从延迟** | 网络延迟 / 从库性能差 / 大 key 同步 | 优化网络、提升从库配置、避免大 key |
| **数据丢失** | RDB/AOF 配置不当 / 未开启持久化 | 开启 AOF + RDB 混合持久化、合理配置 fsync |
| **集群槽位迁移慢** | 大 key 迁移阻塞 | 拆分大 key、在线迁移工具、低峰期迁移 |
| **缓存不一致** | 先删缓存再更新 DB / 并发问题 | 延迟双删 / 订阅 binlog 异步更新 / 设置短 TTL |
| **分布式锁失效** | 锁过期但业务未完成 / 未校验 owner 释放锁 | 使用 Redisson（自动续期）/ Lua 脚本释放锁 |
| **List 队列消息丢失** | 消费者宕机，已弹出消息未处理 | 使用 Stream（支持 ACK）/ 消息确认机制 |
| **ZSet 排行榜不准确** | 并发更新 / 分数计算错误 | 使用 ZINCRBY 原子递增 / 定期校准 |
| **Bitmap 签到统计错误** | 日期计算错误 / offset 越界 | 检查日期计算、offset 从 0 开始 |
| **HyperLogLog 误差大** | 数据量过小 / 合并误差累积 | 数据量小时用 Set / 接受 0.81% 误差 |
| **GEO 查询结果不准** | 坐标错误 / 半径单位错误 | 检查经纬度顺序（经度在前）/ 确认单位 km/m |
| **Stream 消息堆积** | 消费者处理慢 / 消费组不均衡 | 增加消费者 / 优化处理逻辑 / 监控 PEL |
| **编码转换导致性能下降** | 元素超过阈值从 ziplist 转为 hashtable | 合理设置阈值 / 监控编码变化 |

---

## 十四、关联笔记

### Redis
- [[Redis缓存设计与优化]] · [[Redis持久化与高可用]] · [[Redis集群架构与运维]]
- [[Redis分布式锁实战]] · [[Redis高级数据结构实战]] · [[Redis应用场景案例]]

### 数据库
- [[数据库优化知识点系统梳理_优化版]] · [[MySQL-事务与锁机制]] · [[分库分表实战指南]]
- [[MongoDB-文档数据库入门]] · [[Elasticsearch-全文检索引擎]]

### 后端
- [[SpringCache-缓存抽象]] · [[SpringBoot-自动装配原理]] · [[高并发系统设计案例]]
- [[高可用架构设计]] · [[秒杀系统设计与实现]]

### 分布式
- [[分布式锁知识点系统梳理_优化版]] · [[分布式ID生成方案]] · [[分布式任务调度实战]]
- [[分布式缓存架构设计]]

### 导航
- [[MOC-数据库与缓存]] · [[MOC-后端开发]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[Redis缓存设计与优化]] Redis 基础 → 学习 [[Redis持久化与高可用]] 持久化和高可用 → 深入本文高级数据结构实战 → 实践 [[Redis分布式锁实战]] 分布式锁 → 研究 [[Redis集群架构与运维]] 集群运维 → 应用于 [[高并发系统设计案例]] 生产缓存架构。
