---
title: Java-数据库性能优化
tags: [Java, 性能优化, SQL优化, MOC, 连接池, 原子笔记]
category: 后端开发
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["Java-应用性能调优实战", "Java-异常体系与最佳实践", "SpringValidation-参数校验"]
aliases: [Java-数据库性能优化]
---

# Java-数据库性能优化

> **文档说明**：系统讲解 Java 数据库性能优化的完整体系，包括 SQL 优化、索引设计、连接池、缓存、分库分表、读写分离、ORM 优化，以及慢查询排查和生产级最佳实践。
>
> **适用人群**：Java 后端开发者、数据库工程师、需要优化数据库性能的开发者
>
> **前置知识**：[[Java-应用性能调优实战]]、[[Java-异常体系与最佳实践]]、[[SpringValidation-参数校验]]

---

## 一、概述

### 1. 数据库性能优化层次

```
数据库性能优化层次（从应用到硬件）：

1. SQL 与索引优化（成本最低，收益最大）
   - 慢 SQL 优化
   - 索引设计与优化
   - 查询结构优化

2. 数据库连接优化
   - 连接池配置
   - 连接复用
   - 超时设置

3. 缓存优化
   - 一级缓存（Session）
   - 二级缓存（应用级）
   - 分布式缓存（Redis）

4. 架构优化
   - 读写分离
   - 分库分表
   - 数据归档

5. 数据库配置优化
   - 缓冲池大小
   - 连接数
   - 日志配置

6. 硬件与基础设施
   - CPU/内存/磁盘
   - SSD
   - 网络
```

### 2. 性能优化原则

```
优化原则：
1. 先测量再优化：用数据说话，不要凭感觉
2. 定位瓶颈：CPU/IO/网络/锁，找到真正瓶颈
3. 最小改动：优先改 SQL 和索引，不改架构
4. 渐进式：小步迭代，每次验证效果
5. 权衡：一致性 vs 性能，成本 vs 收益
6. 可回滚：优化方案要有回滚预案
7. 持续监控：优化后持续监控，防止退化
```

---

## 二、SQL 优化

### 1. 执行计划分析

```sql
-- 查看执行计划（MySQL）
EXPLAIN SELECT * FROM orders WHERE user_id = 123;

-- 查看详细执行计划
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 123;

-- 执行计划关键字段：
-- id：查询序号
-- select_type：查询类型（SIMPLE/PRIMARY/SUBQUERY等）
-- table：表名
-- type：访问类型（system/const/eq_ref/ref/range/index/ALL）
-- possible_keys：可能使用的索引
-- key：实际使用的索引
-- key_len：索引长度
-- ref：索引比较的列
-- rows：估算扫描行数
-- Extra：额外信息（Using index/Using where/Using filesort/Using temporary）

-- 访问类型性能从好到差：
-- system > const > eq_ref > ref > range > index > ALL
-- 目标：至少达到 range，最好是 ref/eq_ref
-- 避免：ALL（全表扫描）、index（全索引扫描）
```

```sql
-- 危险信号：
-- type=ALL：全表扫描，需要加索引
-- Extra=Using filesort：文件排序，需要优化索引
-- Extra=Using temporary：使用临时表，需要优化分组/排序
-- rows 很大：扫描行数过多
-- key=NULL：没有使用索引
```

### 2. 查询优化技巧

```sql
-- ✅ 避免 SELECT *，只查需要的列
SELECT id, name, email FROM users WHERE id = 1;
-- ❌ SELECT * FROM users WHERE id = 1;

-- ✅ 用 EXISTS 替代 IN（子查询结果大时）
SELECT * FROM orders o WHERE EXISTS (
  SELECT 1 FROM users u WHERE u.id = o.user_id AND u.status = 'active'
);
-- ❌ SELECT * FROM orders WHERE user_id IN (SELECT id FROM users WHERE status='active');

-- ✅ 用 UNION ALL 替代 OR（索引利用率高）
SELECT * FROM orders WHERE status = 'pending'
UNION ALL
SELECT * FROM orders WHERE status = 'processing';
-- ❌ SELECT * FROM orders WHERE status = 'pending' OR status = 'processing';

-- ✅ 避免在索引列上使用函数/运算
SELECT * FROM users WHERE YEAR(created_at) = 2024;  -- ❌ 索引失效
SELECT * FROM users WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';  -- ✅

-- ✅ 避免隐式类型转换
SELECT * FROM users WHERE phone = 13800138000;  -- ❌ phone是varchar，隐式转换
SELECT * FROM users WHERE phone = '13800138000';  -- ✅

-- ✅ 分页优化（深分页）
SELECT * FROM orders ORDER BY id LIMIT 10000, 20;  -- ❌ 慢
-- 用游标分页
SELECT * FROM orders WHERE id > 10000 ORDER BY id LIMIT 20;  -- ✅
-- 或延迟关联
SELECT o.* FROM orders o
INNER JOIN (SELECT id FROM orders ORDER BY id LIMIT 10000, 20) t ON o.id = t.id;

-- ✅ 批量操作替代循环
INSERT INTO users (name, email) VALUES ('a', 'a@x.com'), ('b', 'b@x.com');
-- ❌ 循环单条 INSERT

-- ✅ 合理使用 LIMIT
SELECT * FROM orders WHERE user_id = 1 LIMIT 1;  -- 只取一条
```

### 3. 聚合查询优化

```sql
-- ✅ 用覆盖索引避免回表
-- 索引包含查询所需的所有列
CREATE INDEX idx_user_status ON orders(user_id, status, amount);
SELECT user_id, status, SUM(amount) FROM orders GROUP BY user_id, status;
-- Using index（覆盖索引）

-- ✅ 预计算/汇总表
-- 高频统计查询，创建汇总表
CREATE TABLE daily_order_summary (
  date DATE,
  total_amount DECIMAL(12,2),
  order_count INT,
  PRIMARY KEY (date)
);
-- 定时任务汇总，查询直接读汇总表

-- ✅ 避免 SELECT DISTINCT（去重开销大）
-- 用 GROUP BY 或 EXISTS 替代
```

---

## 三、索引优化

### 1. 索引类型

```
MySQL 索引类型：
1. B+Tree 索引：最常用，InnoDB 默认
   - 聚簇索引（主键索引）：数据和索引在一起
   - 二级索引（非主键）：存主键值，需要回表

2. 哈希索引：Memory 引擎，等值查询快，不支持范围
3. 全文索引：文本搜索（FULLTEXT）
4. 空间索引：地理数据（SPATIAL）
5. 前缀索引：字符串前 N 个字符建索引
6. 联合索引：多列组合索引
```

### 2. 索引设计原则

```
索引设计原则：
1. 高频查询字段建索引：WHERE/JOIN/ORDER BY/GROUP BY
2. 联合索引遵循最左前缀：(a,b,c) 支持 a, a+b, a+b+c
3. 区分度高的字段优先：性别、状态等低区分度不适合单独建索引
4. 避免过多索引：每个索引都增加写入开销
5. 覆盖索引优先：索引包含查询所有列，避免回表
6. 字符串用前缀索引：长字符串只索引前 N 个字符
7. 避免在索引列上做运算/函数
8. 定期清理无用索引
```

```sql
-- 联合索引示例
CREATE INDEX idx_user_status_created ON orders(user_id, status, created_at);
-- 支持：
-- WHERE user_id = 1
-- WHERE user_id = 1 AND status = 'pending'
-- WHERE user_id = 1 AND status = 'pending' AND created_at > '2024-01-01'
-- 不支持（不满足最左前缀）：
-- WHERE status = 'pending'
-- WHERE created_at > '2024-01-01'

-- 前缀索引
CREATE INDEX idx_email_prefix ON users(email(20));

-- 覆盖索引
CREATE INDEX idx_user_amount ON orders(user_id, amount);
SELECT user_id, SUM(amount) FROM orders WHERE user_id = 1 GROUP BY user_id;
-- Using index（不需要回表）
```

### 3. 索引失效场景

```sql
-- 索引失效的常见场景：

-- 1. 索引列上使用函数/运算
WHERE YEAR(created_at) = 2024           -- ❌
WHERE created_at >= '2024-01-01'         -- ✅

-- 2. 隐式类型转换
WHERE varchar_col = 123                   -- ❌
WHERE varchar_col = '123'                 -- ✅

-- 3. LIKE 以 % 开头
WHERE name LIKE '%张'                      -- ❌ 全表扫描
WHERE name LIKE '张%'                      -- ✅ 可用索引

-- 4. OR 条件有非索引列
WHERE indexed_col = 1 OR no_index_col = 2  -- ❌ 全表扫描
-- 解决：给 no_index_col 也建索引，或用 UNION

-- 5. != 或 <> 操作（可能失效）
WHERE status != 'active'                   -- 可能全表扫描
-- 解决：用 IN 列举所有值，或改写查询

-- 6. IS NOT NULL（可能失效）
WHERE col IS NOT NULL                       -- 可能全表扫描

-- 7. 联合索引不满足最左前缀
WHERE b = 1 AND c = 2  -- 索引(a,b,c) ❌

-- 8. 优化器选择全表扫描
-- 数据量小，或返回行数比例大，优化器认为全表扫描更快
```

### 4. 索引维护

```sql
-- 查看索引使用情况
SELECT * FROM sys.schema_unused_indexes;  -- 未使用的索引
SELECT * FROM sys.schema_index_statistics;  -- 索引统计

-- 分析表（更新索引统计信息）
ANALYZE TABLE orders;

-- 检查索引碎片
SHOW INDEX FROM orders;
-- Cardinality 列：索引基数（区分度）

-- 优化表（重建索引，减少碎片）
OPTIMIZE TABLE orders;

-- 查看慢查询日志
SHOW VARIABLES LIKE 'slow_query_log';
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;  -- 超过1秒记录
```

---

## 四、连接池优化

### 1. HikariCP 配置

```yaml
# Spring Boot HikariCP 配置
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: secret
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      maximum-pool-size: 20        # 最大连接数（核心参数）
      minimum-idle: 5              # 最小空闲连接
      connection-timeout: 30000    # 获取连接超时（ms）
      idle-timeout: 600000         # 空闲连接超时（ms）
      max-lifetime: 1800000        # 连接最大生命周期（ms）
      leak-detection-threshold: 60000  # 连接泄漏检测（ms）
      pool-name: MyHikariCP
      connection-test-query: SELECT 1
```

### 2. 连接池大小计算

```
连接池大小计算公式（PostgreSQL 提供）：
连接数 = ((核心数 * 2) + 有效磁盘数)

示例：
- 4 核 CPU，SSD（1 块有效磁盘）
- 连接数 = (4 * 2) + 1 = 9

实际经验：
- 小应用：10-20 个连接
- 中应用：20-50 个连接
- 大应用：50-100 个连接
- 不要盲目设大：连接过多会增加数据库负担和上下文切换

注意：
- 最大连接数 ≤ 数据库 max_connections
- 多实例部署时，总连接数 ≤ 数据库连接数
- 监控活跃连接数，根据实际调整
```

### 3. 连接池监控

```
关键监控指标：
- activeConnections：活跃连接数
- idleConnections：空闲连接数
- threadsAwaitingConnection：等待连接的线程数
- connectionCreationTime：连接创建时间
- connectionTimeoutCount：连接超时次数

如果 threadsAwaitingConnection > 0：
- 连接池不够用，需要增大 maximum-pool-size
- 或优化 SQL，减少连接持有时间

如果连接泄漏：
- 开启 leak-detection-threshold
- 检查是否有未关闭的连接
- 确保用 try-with-resources
```

---

## 五、缓存优化

### 1. MyBatis 缓存

```
MyBatis 一级缓存（SqlSession 级）：
- 默认开启，同一个 SqlSession 内有效
- 执行 INSERT/UPDATE/DELETE 或 commit 时清空
- 不同 SqlSession 不共享

MyBatis 二级缓存（Mapper 级）：
- 需要手动开启，跨 SqlSession 共享
- 缓存以 namespace 为单位
- 适用：查询多、修改少的场景
- 不适用：频繁修改、多表关联查询

<!-- 开启二级缓存 -->
<cache eviction="LRU" flushInterval="60000" size="512" readOnly="true"/>
```

### 2. Redis 分布式缓存

```java
@Service
public class UserService {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    private static final String USER_CACHE_KEY = "user:";
    private static final long CACHE_TTL = 3600; // 1小时

    // 缓存查询（Cache-Aside 模式）
    public User getUserById(Long id) {
        String key = USER_CACHE_KEY + id;

        // 1. 先查缓存
        User user = (User) redisTemplate.opsForValue().get(key);
        if (user != null) {
            return user;
        }

        // 2. 缓存未命中，查数据库
        user = userRepository.findById(id).orElse(null);
        if (user != null) {
            // 3. 写入缓存
            redisTemplate.opsForValue().set(key, user, CACHE_TTL, TimeUnit.SECONDS);
        }
        return user;
    }

    // 更新时清除缓存
    @Transactional
    public void updateUser(User user) {
        userRepository.save(user);
        // 先更新数据库，再删除缓存
        redisTemplate.delete(USER_CACHE_KEY + user.getId());
    }
}
```

### 3. 缓存常见问题

```
缓存穿透：
- 问题：查询不存在的数据，缓存永远不命中，请求直达数据库
- 解决：
  1. 缓存空值（短 TTL）
  2. 布隆过滤器（Bloom Filter）
  3. 参数校验

缓存击穿：
- 问题：热点 key 过期瞬间，大量请求直达数据库
- 解决：
  1. 互斥锁（只让一个请求查库）
  2. 逻辑过期（不设 TTL，异步更新）
  3. 热点数据永不过期

缓存雪崩：
- 问题：大量 key 同时过期，或 Redis 宕机
- 解决：
  1. 过期时间加随机值
  2. 多级缓存（本地缓存 + Redis）
  3. Redis 高可用（哨兵/集群）
  4. 服务降级/熔断
```

```java
// 互斥锁解决缓存击穿
public User getUserWithLock(Long id) {
    String key = USER_CACHE_KEY + id;
    User user = (User) redisTemplate.opsForValue().get(key);
    if (user != null) return user;

    String lockKey = "lock:user:" + id;
    Boolean locked = redisTemplate.opsForValue()
        .setIfAbsent(lockKey, "1", 10, TimeUnit.SECONDS);

    if (Boolean.TRUE.equals(locked)) {
        try {
            // 双重检查
            user = (User) redisTemplate.opsForValue().get(key);
            if (user != null) return user;

            user = userRepository.findById(id).orElse(null);
            if (user != null) {
                redisTemplate.opsForValue().set(key, user, CACHE_TTL, TimeUnit.SECONDS);
            }
            return user;
        } finally {
            redisTemplate.delete(lockKey);
        }
    } else {
        // 等待后重试
        try { Thread.sleep(100); } catch (InterruptedException e) {}
        return getUserWithLock(id);
    }
}
```

---

## 六、架构优化

### 1. 读写分离

```
读写分离架构：
- 主库（Master）：处理写操作
- 从库（Slave）：处理读操作，异步同步主库数据
- 一主一从 / 一主多从

适用场景：
- 读多写少（大多数 Web 应用）
- 查询性能瓶颈

注意事项：
- 主从延迟：刚写入的数据可能在从库读不到
- 解决方案：
  1. 关键查询走主库
  2. 写后读走主库（一段时间内）
  3. 半同步复制
```

```java
// Spring 动态数据源切换
@Service
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    // 读操作走从库
    @ReadOnly
    public Order getOrder(Long id) {
        return orderRepository.findById(id).orElse(null);
    }

    // 写操作走主库
    @Transactional
    public Order createOrder(Order order) {
        return orderRepository.save(order);
    }
}
```

### 2. 分库分表

```
分库分表（Sharding）：

垂直分库：按业务模块分库
- 用户库、订单库、商品库

垂直分表：按字段分表
- 订单主表（常用字段）+ 订单详情表（大字段）

水平分库：按规则分库
- user_id % 2 = 0 → 库1，= 1 → 库2

水平分表：按规则分表
- order_id % 4 → orders_0, orders_1, orders_2, orders_3

分片策略：
1. 范围分片：按时间/ID 范围（易热点）
2. 哈希分片：取模/一致性哈希（均匀分布）
3. 查表法：路由表映射

中间件：
- ShardingSphere（Sharding-JDBC / Sharding-Proxy）
- MyCat
- Vitess
```

```yaml
# ShardingSphere 配置示例
spring:
  shardingsphere:
    datasource:
      names: ds0,ds1
      ds0:
        url: jdbc:mysql://localhost:3306/db0
      ds1:
        url: jdbc:mysql://localhost:3306/db1
    rules:
      sharding:
        tables:
          orders:
            actual-data-nodes: ds${0..1}.orders_${0..3}
            database-strategy:
              standard:
                sharding-column: user_id
                sharding-algorithm-name: db-inline
            table-strategy:
              standard:
                sharding-column: id
                sharding-algorithm-name: table-inline
        sharding-algorithms:
          db-inline:
            type: INLINE
            props:
              algorithm-expression: ds${user_id % 2}
          table-inline:
            type: INLINE
            props:
              algorithm-expression: orders_${id % 4}
```

### 3. 数据归档

```
数据归档策略：
- 冷数据归档：历史数据移到归档表/归档库
- 按时间归档：每月/每季度归档
- 保持热表数据量在可控范围（建议 < 5000万行）

示例：
- orders：近 3 个月订单（热数据）
- orders_history：3 个月前订单（冷数据）
- 查询时先查热表，查不到再查冷表
```

---

## 七、ORM 优化

### 1. MyBatis 优化

```xml
<!-- 1. 避免 N+1 查询：用 JOIN 替代循环查询 -->
<!-- ❌ 循环查询每个订单的用户 -->
<select id="findOrders" resultMap="orderMap">
  SELECT * FROM orders
</select>
<!-- 然后循环查 user -->

<!-- ✅ 一次 JOIN 查询 -->
<select id="findOrdersWithUser" resultMap="orderWithUserMap">
  SELECT o.*, u.name as user_name, u.email as user_email
  FROM orders o
  LEFT JOIN users u ON o.user_id = u.id
</select>

<!-- 2. 批量操作 -->
<insert id="batchInsert">
  INSERT INTO users (name, email) VALUES
  <foreach collection="list" item="item" separator=",">
    (#{item.name}, #{item.email})
  </foreach>
</insert>

<!-- 3. 分页查询 -->
<select id="findByPage">
  SELECT * FROM orders
  ORDER BY id
  LIMIT #{offset}, #{size}
</select>

<!-- 4. 动态 SQL 优化 -->
<select id="findByCondition">
  SELECT * FROM orders
  <where>
    <if test="userId != null">AND user_id = #{userId}</if>
    <if test="status != null">AND status = #{status}</if>
    <if test="startDate != null">AND created_at >= #{startDate}</if>
  </where>
  ORDER BY id DESC
</select>
```

### 2. JPA/Hibernate 优化

```java
// 1. 避免 N+1：用 JOIN FETCH
@Query("SELECT o FROM Order o JOIN FETCH o.user WHERE o.status = :status")
List<Order> findByStatusWithUser(@Param("status") String status);

// 2. 用 EntityGraph
@EntityGraph(attributePaths = {"user", "items"})
List<Order> findByStatus(String status);

// 3. 批量操作
@Modifying
@Query("UPDATE Order o SET o.status = :status WHERE o.id IN :ids")
int batchUpdateStatus(@Param("ids") List<Long> ids, @Param("status") String status);

// 4. 投影查询（只查需要的字段）
public interface OrderSummary {
    Long getId();
    String getStatus();
    BigDecimal getAmount();
}
List<OrderSummary> findByUserId(Long userId);

// 5. 脏检查优化
@DynamicUpdate  // 只更新变化的字段
@Entity
public class Order { ... }

// 6. 批量配置
// application.yml
spring:
  jpa:
    properties:
      hibernate:
        jdbc:
          batch_size: 50        # 批量大小
        order_inserts: true     # 排序插入
        order_updates: true     # 排序更新
```

---

## 八、慢查询排查

### 1. 排查流程

```
慢查询排查步骤：
1. 开启慢查询日志，收集慢 SQL
2. 用 EXPLAIN 分析执行计划
3. 识别问题：全表扫描/文件排序/临时表/扫描行数多
4. 优化：加索引/改写 SQL/调整结构
5. 验证：再次 EXPLAIN，确认优化效果
6. 监控：持续监控，防止退化
```

### 2. 常用排查命令

```sql
-- 查看当前慢查询配置
SHOW VARIABLES LIKE '%slow%';
SHOW VARIABLES LIKE 'long_query_time';

-- 开启慢查询
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;  -- 1秒
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';

-- 分析慢查询日志
mysqldumpslow -s t -t 10 /var/log/mysql/slow.log
-- -s t：按时间排序
-- -t 10：显示前10条

-- 查看正在执行的查询
SHOW PROCESSLIST;
SHOW FULL PROCESSLIST;

-- 查看 InnoDB 状态（锁等待等）
SHOW ENGINE INNODB STATUS;

-- 查看表状态
SHOW TABLE STATUS LIKE 'orders';

-- 查看索引
SHOW INDEX FROM orders;
```

### 3. 锁问题排查

```sql
-- 查看当前锁等待
SELECT * FROM information_schema.INNODB_LOCK_WAITS;
SELECT * FROM information_schema.INNODB_LOCKS;

-- 查看事务
SELECT * FROM information_schema.INNODB_TRX;

-- 死锁日志
SHOW ENGINE INNODB STATUS\G
-- 查看 LATEST DETECTED DEADLOCK 部分

-- 优化锁：
-- 1. 缩短事务时间
-- 2. 避免大事务
-- 3. 合理使用索引（减少锁范围）
-- 4. 降低隔离级别（READ COMMITTED）
-- 5. 避免长事务中混合操作
```

---

## 九、最佳实践清单

### SQL 与索引
- [ ] **避免 SELECT ***：只查需要的列
- [ ] **合理使用索引**：高频查询字段建索引
- [ ] **联合索引最左前缀**：按查询频率排序
- [ ] **避免索引失效**：不在索引列用函数/运算
- [ ] **覆盖索引**：索引包含查询所有列
- [ ] **深分页优化**：用游标分页或延迟关联
- [ ] **批量操作**：替代循环单条操作
- [ ] **定期分析表**：更新索引统计信息
- [ ] **清理无用索引**：减少写入开销

### 连接与事务
- [ ] **合理配置连接池**：根据实际负载调整
- [ ] **监控连接等待**：threadsAwaitingConnection
- [ ] **缩短事务时间**：减少锁持有时间
- [ ] **避免大事务**：拆分大事务
- [ ] **合理隔离级别**：大多数场景 READ COMMITTED
- [ ] **try-with-resources**：确保连接关闭
- [ ] **连接泄漏检测**：开启 leak-detection

### 缓存
- [ ] **Cache-Aside 模式**：先查缓存，再查库
- [ ] **设置合理 TTL**：根据数据更新频率
- [ ] **防穿透**：缓存空值/布隆过滤器
- [ ] **防击穿**：互斥锁/逻辑过期
- [ ] **防雪崩**：随机 TTL/多级缓存
- [ ] **更新策略**：先更库，再删缓存
- [ ] **热点数据**：永不过期/本地缓存

### 架构
- [ ] **读写分离**：读多写少场景
- [ ] **分库分表**：单表数据量大时
- [ ] **数据归档**：冷数据移到归档表
- [ ] **数据库高可用**：主从/集群
- [ ] **监控告警**：慢查询/连接数/锁等待

### ORM
- [ ] **避免 N+1 查询**：用 JOIN FETCH/关联查询
- [ ] **批量操作**：batch_size 配置
- [ ] **投影查询**：只查需要的字段
- [ ] **@DynamicUpdate**：只更新变化字段
- [ ] **合理使用缓存**：一级/二级缓存

---

## 十、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **查询慢** | 缺索引/SQL 差/数据量大 | EXPLAIN 分析、加索引、改写 SQL |
| **全表扫描** | 无索引/索引失效 | 加索引、避免索引列运算/函数 |
| **Using filesort** | 排序无索引 | 建联合索引覆盖 ORDER BY |
| **Using temporary** | 分组/排序用临时表 | 优化索引、调整查询 |
| **连接池满** | 连接泄漏/慢SQL占连接 | 检查泄漏、优化SQL、增大池 |
| **死锁** | 事务加锁顺序不一致 | 统一加锁顺序、缩短事务 |
| **锁等待超时** | 长事务/大事务 | 拆分事务、优化索引 |
| **缓存穿透** | 查询不存在数据 | 缓存空值、布隆过滤器 |
| **缓存击穿** | 热点key过期 | 互斥锁、逻辑过期 |
| **缓存雪崩** | 大量key同时过期 | 随机TTL、多级缓存、降级 |
| **主从延迟** | 从库同步慢 | 半同步、关键查询走主库 |
| **内存不足** | 缓冲池太小/连接多 | 增大innodb_buffer_pool_size |
| **CPU高** | 慢SQL/排序/计算 | 优化SQL、加索引、减少计算 |
| **IO高** | 全表扫描/频繁刷盘 | 加索引、调整innodb_flush_log_at_trx_commit |
| **数据量大查询慢** | 单表数据过多 | 分表、归档、读写分离 |
| **插入慢** | 索引多/逐条插入 | 批量插入、减少索引、调整参数 |
| **更新慢** | 行锁/索引更新 | 优化索引、缩短事务 |
| **ORM N+1** | 循环查询关联对象 | JOIN FETCH、EntityGraph、批量加载 |
| **连接超时** | 网络/数据库负载/连接池满 | 检查网络、优化负载、调整超时 |

---

## 十一、关联笔记

### Java 后端
- [[Java-应用性能调优实战]] · [[Java-异常体系与最佳实践]] · [[Java-并发编程实战]]
- [[Java-数据加密与脱敏]] · [[Java-网络编程与NIO]]

### 数据库与中间件
- [[消息队列-RabbitMQ-Kafka]] · [[分布式系统-高可用架构设计]] · [[Redis缓存实战]]

### 运维
- [[APM应用性能监控-SkyWalking]] · [[容器安全与镜像扫描]] · [[K8s-核心概念与架构]]

### 导航
- [[MOC-后端开发]] · [[MOC-云原生与运维]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[Java-应用性能调优实战]] JVM 调优 → 深入本文数据库性能优化 → 学习 [[Redis缓存实战]] 缓存优化 → 实践 [[消息队列-RabbitMQ-Kafka]] 异步解耦 → 研究 [[分布式系统-高可用架构设计]] 架构设计 → 构建完整的后端性能优化能力。
