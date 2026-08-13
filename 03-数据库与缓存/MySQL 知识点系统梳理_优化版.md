---
title: MySQL 知识点系统梳理
tags: [数据库, MySQL, 索引, 事务, 面试]
created: 2026-08-12
updated: 2026-08-12
---

# MySQL 知识点系统梳理（优化版）

> **文档说明**：本文档参照《Java知识点完整整合大全》排版风格，系统梳理 MySQL 技术栈。包含概述、核心特性、常用用法、注意事项四大模块，辅以动态可视化解析图、深度讲解与精简总结。**优化版**在原有内容基础上，为每个知识点补充了作用、原理、用法的深度解析，并新增了知识点图解。

---

## 1. 概述

MySQL 是一款开源的**关系型数据库管理系统（RDBMS）**，由瑞典 MySQL AB 公司开发，现属 Oracle 旗下。它以体积小、速度快、成本低、开源免费等特点成为 Web 应用最流行的数据库，是 LAMP/LNMP 架构的核心组件。

**核心定位**：
- 关系型数据库，支持标准 SQL（ANSI SQL 92/99）
- 默认存储引擎 InnoDB，支持事务、行锁、外键、MVCC
- 支持主从复制、读写分离、分库分表等扩展方案
- 广泛应用于互联网、电商、金融等各类业务系统

**版本演进**：

| 版本 | 发布年份 | 关键特性 |
|------|---------|---------|
| MySQL 5.6 | 2013 | InnoDB 性能优化，全文索引，GTID 复制 |
| MySQL 5.7 | 2015 | JSON 类型，生成列，sys schema，性能大幅提升 |
| MySQL 8.0 | 2018 | 窗口函数，CTE，原子 DDL，新字符集 utf8mb4_0900_ai_ci，隐藏索引 |

---

## 2. 核心特性

<div style="background:linear-gradient(135deg,#ffecd2,#fcb69f);border-radius:16px;padding:24px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#1a1a2e;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes mysqlArch{0%,100%{transform:scale(1);opacity:.85}50%{transform:scale(1.03);opacity:1}}.mysql-layer{border-radius:10px;padding:12px 18px;margin:8px auto;text-align:center;font-weight:600;animation:mysqlArch 3s ease-in-out infinite;max-width:400px}.mysql-conn{background:rgba(255,255,255,.45);border:2px solid rgba(255,255,255,.6);animation-delay:0s}.mysql-sql{background:rgba(255,255,255,.55);border:2px solid rgba(255,255,255,.7);animation-delay:.5s}.mysql-engine{background:rgba(255,255,255,.65);border:2px solid rgba(255,255,255,.8);animation-delay:1s}.mysql-arrow{text-align:center;font-size:18px;margin:4px 0;animation:mysqlArch 1.5s ease-in-out infinite}.mysql-label{font-size:11px;opacity:.75;font-weight:400;margin-top:4px}</style>
<div style="text-align:center;font-size:16px;font-weight:700;margin-bottom:16px;padding-bottom:12px;border-bottom:1.5px solid rgba(0,0,0,.1);letter-spacing:1px">MySQL 三层架构</div>
<div class="mysql-layer mysql-conn">连接层（Connection Layer）<div class="mysql-label">连接池 / 认证授权 / 线程处理</div></div>
<div class="mysql-arrow">▼</div>
<div class="mysql-layer mysql-sql">SQL 层（Server Layer）<div class="mysql-label">解析器 → 优化器 → 执行器 / 查询缓存 / 权限</div></div>
<div class="mysql-arrow">▼</div>
<div class="mysql-layer mysql-engine">存储引擎层（Engine Layer）<div class="mysql-label">InnoDB（默认）/ MyISAM / Memory / CSV</div></div>
</div>

### 2.1 InnoDB 存储引擎

**核心特性**：
- 支持事务（ACID），默认 REPEATABLE READ 隔离级别
- 行级锁（Row Lock），并发性能好
- MVCC（多版本并发控制），读写不阻塞
- 聚簇索引（主键索引即数据）
- 支持外键、崩溃恢复、自动故障恢复

**InnoDB vs MyISAM**：

| 特性 | InnoDB | MyISAM |
|------|--------|--------|
| 事务 | 支持 | 不支持 |
| 锁粒度 | 行锁 | 表锁 |
| 外键 | 支持 | 不支持 |
| 全文索引 | 5.6+ 支持 | 支持 |
| 崩溃恢复 | 支持 | 不支持 |
| 计数 | COUNT(*) 全表扫 | 存储行数，快 |

> 🔍 **知识点深度解析**
>
> **作用**：InnoDB 是 MySQL 默认存储引擎，支持事务、行锁、MVCC，是 OLTP（在线事务处理）场景的首选。理解 InnoDB 原理是 MySQL 性能优化的基础。
>
> **原理**：InnoDB 架构：内存（Buffer Pool 缓存数据页和索引页、Change Buffer 缓存二级索引变更、Adaptive Hash Index 自适应哈希、Log Buffer 缓存 redo log）+ 磁盘（表空间 .ibd、redo log、undo log）。事务通过 redo log（WAL 预写日志，崩溃恢复）和 undo log（MVCC 多版本和回滚）保证 ACID。行锁通过索引实现（没索引会升级为表锁）。MVCC：每行有隐藏列（DB_TRX_ID 事务ID、DB_ROLL_PTR 回滚指针），SELECT 时根据 ReadView 判断可见版本，实现读写不阻塞。聚簇索引：主键索引的叶子节点存整行数据，二级索引叶子节点存主键值（回表查询）。
>
> **用法要点**：① 生产用 InnoDB（不要用 MyISAM，不支持事务和崩溃恢复）；② 每张表必须有主键（InnoDB 聚簇索引，没主键会自动生成隐藏行ID）；③ 主键用自增 ID（顺序插入，避免页分裂），不要用 UUID（随机插入，页分裂严重）；④ 行锁基于索引，更新/删除没索引会锁全表；⑤ COUNT(*) 在 InnoDB 是全表扫（大表慢），用近似值或单独计数表；⑥ Buffer Pool 设置为物理内存的 50-70%（innodb_buffer_pool_size）；⑦ redo log 大小设 1-4GB（innodb_log_file_size），减少 checkpoint。

### 2.2 索引原理与优化

**索引类型**：
- 主键索引（聚簇索引）：叶子节点存整行数据
- 二级索引（非聚簇）：叶子节点存主键值，需回表
- 唯一索引：索引值唯一
- 联合索引：多列组合，最左前缀匹配
- 覆盖索引：查询字段都在索引中，无需回表

**索引数据结构**：B+ Tree（多路平衡查找树，叶子节点链表连接，范围查询高效）。

**最左前缀原则**：联合索引 (a,b,c)，查询条件 a、a+b、a+b+c 走索引，b、b+c 不走。

> 🔍 **知识点深度解析**
>
> **作用**：索引是数据库性能优化的核心，将全表扫描（O(n)）变为索引查找（O(log n)）。正确的索引设计能将查询性能提升几个数量级。
>
> **原理**：InnoDB 用 B+ Tree 存储索引：非叶子节点存索引键+子节点指针，叶子节点存数据（聚簇索引）或主键值（二级索引），叶子节点用双向链表连接（范围查询高效）。B+ Tree 高度通常 3-4 层（千万级数据），每次查询只需 3-4 次 IO。联合索引按列顺序排序，最左前缀匹配：WHERE a=? AND b=? 走索引，WHERE b=? 不走（因为 B+ Tree 先按 a 排序，a 不确定无法定位）。覆盖索引：查询的列都在索引中，不需要回表查询聚簇索引，性能好。索引下推（ICP，MySQL 5.6+）：在存储引擎层用索引条件过滤，减少回表次数。
>
> **用法要点**：① 高频查询字段加索引（WHERE/JOIN/ORDER BY/GROUP BY）；② 联合索引按区分度从高到低排列，遵循最左前缀；③ 覆盖索引：SELECT 的列都在索引中（避免回表）；④ 不要在索引列上用函数/运算（如 WHERE DATE(create_time)=?，索引失效）；⑤ 字符串不加引号可能索引失效（隐式类型转换）；⑥ LIKE '%xxx' 不走索引（前缀模糊），LIKE 'xxx%' 走；⑦ OR 条件两边都有索引才走，否则全表扫；⑧ 用 EXPLAIN 查看执行计划（type=ref/range 好，ALL 全表扫差）。

### 2.3 事务与隔离级别

**ACID**：原子性（Atomicity）、一致性（Consistency）、隔离性（Isolation）、持久性（Durability）。

**隔离级别**：

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|---------|------|-----------|------|
| READ UNCOMMITTED | 可能 | 可能 | 可能 |
| READ COMMITTED | 不可能 | 可能 | 可能 |
| REPEATABLE READ（默认） | 不可能 | 不可能 | 可能（InnoDB用MVCC+间隙锁解决） |
| SERIALIZABLE | 不可能 | 不可能 | 不可能 |

**InnoDB 默认 REPEATABLE READ**，通过 MVCC + Next-Key Lock 解决幻读。

> 🔍 **知识点深度解析**
>
> **作用**：事务保证一组操作要么全成功要么全失败，隔离级别定义并发事务间的可见性。理解隔离级别和 MVCC 是并发编程和数据库优化的基础。
>
> **原理**：原子性由 undo log（回滚）保证，持久性由 redo log（WAL，崩溃恢复）保证，隔离性由锁+MVCC保证。脏读：读到其他事务未提交的数据。不可重复读：同一事务内两次读同一行结果不同（其他事务更新并提交）。幻读：同一事务内两次范围查询结果行数不同（其他事务插入新行）。MVCC：每行有 DB_TRX_ID（创建/删除该行的事务ID）和 DB_ROLL_PTR（指向 undo log 版本链），SELECT 时生成 ReadView（当前活跃事务列表），根据可见性规则判断哪个版本可见。InnoDB RR 级别用 Next-Key Lock（记录锁+间隙锁）防止幻读（当前读如 SELECT FOR UPDATE）。
>
> **用法要点**：① 默认 RR 级别够用，不要随意改隔离级别；② 避免长事务（持有锁时间长，undo log 膨胀，影响性能）；③ 死锁：固定加锁顺序、减少事务大小、用 SELECT FOR UPDATE 显式加锁；④ 当前读（SELECT FOR UPDATE/UPDATE/DELETE）加锁，快照读（普通 SELECT）不加锁（MVCC）；⑤ 间隙锁（Gap Lock）可能导致死锁（RR 级别），可改 RC 级别减少；⑥ 事务内不要有远程调用/用户输入（持锁时间长）；⑦ 用 SHOW ENGINE INNODB STATUS 查看死锁日志。

### 2.4 锁机制

**锁类型**：
- 全局锁：FTWRL（Flush Tables With Read Lock），全库只读，备份用
- 表级锁：表锁、元数据锁（MDL）、意向锁
- 行级锁：记录锁（Record Lock）、间隙锁（Gap Lock）、Next-Key Lock（记录+间隙）

**MDL 锁**：访问表时自动加，DDL 会等所有 MDL 释放，可能导致阻塞。

**死锁**：两个事务互相等待对方释放锁。InnoDB 自动检测死锁，回滚代价小的事务。

> 🔍 **知识点深度解析**
>
> **作用**：锁保证并发事务的数据一致性。InnoDB 行锁性能好（只锁需要的行），但没索引会升级为表锁。理解锁机制是排查死锁和慢查询的关键。
>
> **原理**：InnoDB 行锁是加在索引上的（不是记录本身），UPDATE/DELETE 没走索引会扫描全表并对每行加锁（相当于表锁）。记录锁（Record Lock）：锁索引记录。间隙锁（Gap Lock）：锁索引记录之间的间隙，防止插入（RR 级别解决幻读）。Next-Key Lock：记录锁+间隙锁，左开右闭区间。意向锁（IS/IX）：表级锁，表明事务打算加行锁，快速判断表锁冲突。MDL（元数据锁）：SELECT/INSERT 加 MDL 读锁，ALTER TABLE 加 MDL 写锁，读写互斥，DDL 会等所有读锁释放（长查询会阻塞 DDL，进而阻塞后续所有查询）。
>
> **用法要点**：① 更新/删除必须走索引（否则表锁，并发灾难）；② 避免长事务（持有锁时间长）；③ MDL 锁：DDL 前检查长查询，用 ALGORITHM=INPLACE/ONLINE 减少锁表；④ 死锁排查：SHOW ENGINE INNODB STATUS 看 LATEST DETECTED DEADLOCK；⑤ 死锁预防：固定加锁顺序、事务尽量小、避免批量更新加锁过多；⑥ 热点行更新用乐观锁（CAS：UPDATE ... WHERE version=?）或排队；⑦ 间隙锁在 RC 级别关闭（减少死锁，但可能幻读）。

### 2.5 主从复制

**复制模式**：
- 异步复制（默认）：主库提交后不等待从库，性能好但可能丢数据
- 半同步复制：至少一个从库确认收到 relay log，兼顾性能和安全
- 组复制（MGR）：Paxos 协议，多数派确认，强一致

**复制原理**：主库写 binlog → 从库 IO 线程拉取 binlog 存 relay log → SQL 线程重放 relay log。

**binlog 格式**：STATEMENT（SQL语句）、ROW（行变更，推荐）、MIXED（混合）。

> 🔍 **知识点深度解析**
>
> **作用**：主从复制实现数据备份、读写分离、高可用（主库挂了切从库）。是 MySQL 高可用架构的基础。
>
> **原理**：主库提交事务时写 binlog（二进制日志，记录数据变更）。从库 IO 线程连接主库，订阅 binlog 变更，拉取到本地存为 relay log。从库 SQL 线程读取 relay log 并重放（执行变更），实现数据同步。异步复制：主库提交后立即返回，不等待从库（主库宕机可能丢数据）。半同步：主库等待至少一个从库收到 relay log 后返回（rpl_semi_sync_master_timeout 超时降级为异步）。ROW 格式 binlog 记录每行变更前后的值，数据一致但日志大；STATEMENT 记录 SQL，日志小但可能不一致（如 NOW()、UUID()）。
>
> **用法要点**：① 生产用半同步复制（至少一个从库确认，兼顾性能和安全）；② binlog 格式用 ROW（数据一致性好，支持闪回）；③ 从库设 read_only=1（防止误写），超级用户也只读用 super_read_only；④ 延迟从库（延迟1小时）用于误操作恢复（CHANGE MASTER TO MASTER_DELAY=3600）；⑤ 主从延迟监控：Seconds_Behind_Master 或 pt-heartbeat；⑥ 读写分离：写主库读从库，注意主从延迟（刚写就读可能读不到）；⑦ 高可用：MHA/Orchestrator/InnoDB Cluster 自动主从切换。

### 2.6 SQL 优化

**EXPLAIN 执行计划关键字段**：
- type：访问类型（system > const > eq_ref > ref > range > index > ALL，越左越好）
- key：实际使用的索引
- rows：预估扫描行数
- Extra：Using index（覆盖索引）、Using where（回表过滤）、Using filesort（文件排序，需优化）、Using temporary（临时表，需优化）

**常见优化**：
- 避免 SELECT *，只查需要的列
- 分页优化：深翻页用游标（WHERE id > lastId LIMIT 10）
- JOIN 优化：小表驱动大表，关联字段加索引
- ORDER BY 用索引排序，避免 filesort

> 🔍 **知识点深度解析**
>
> **作用**：SQL 优化是数据库性能调优的核心。通过 EXPLAIN 分析执行计划，找到慢查询原因（全表扫、文件排序、临时表），针对性优化（加索引、改写 SQL）。
>
> **原理**：MySQL 查询执行流程：SQL 解析（语法树）→ 预处理器（检查表/列权限）→ 优化器（选择执行计划：全表扫还是索引，哪个索引，JOIN 顺序）→ 执行器（调用存储引擎）。优化器基于成本（Cost）选择执行计划：估算不同方案的 IO 和 CPU 成本，选最低的。统计信息（innodb_stats_persistent）影响优化器决策，统计信息不准会选错索引（ANALYZE TABLE 更新）。filesort：排序字段没索引时，在内存或磁盘文件中排序（性能差）。Using temporary：GROUP BY/DISTINCT 没索引时用临时表。
>
> **用法要点**：① 慢查询日志：slow_query_log=1, long_query_time=1，定位慢 SQL；② EXPLAIN 看 type（ALL 全表扫要优化）、key（是否走索引）、rows（扫描行数）、Extra（filesort/temporary 要优化）；③ 深翻页优化：LIMIT 100000,10 → WHERE id>100000 LIMIT 10（游标分页）；④ JOIN：小表驱动大表（Nested Loop），关联字段必须加索引；⑤ GROUP BY/ORDER BY 字段加联合索引（避免 filesort/temporary）；⑥ OR 改 UNION ALL（各自走索引）；⑦ 用 pt-query-digest 分析慢查询日志。

### 2.7 分库分表

**垂直分库**：按业务拆分（用户库、订单库、商品库）。

**垂直分表**：大字段拆分到扩展表（用户基本信息 + 用户详情）。

**水平分表**：按规则拆分数据（user_0、user_1...user_63）。
- 范围分片：按 ID 范围（1-1000万在表1），扩容方便但热点
- 哈希分片：hash(user_id) % 64，数据均匀但扩容麻烦
- 一致性哈希：扩容只迁移部分数据

**中间件**：ShardingSphere、MyCat、Vitess。

> 🔍 **知识点深度解析**
>
> **作用**：分库分表解决单库单表数据量过大（千万级以上）导致的性能问题（查询慢、索引大、写入瓶颈）。是大规模系统的必经之路。
>
> **原理**：垂直分库：按业务领域拆分数据库，减少单库压力和耦合。水平分表：将一张大表按分片键（sharding key）拆成多张结构相同的小表，数据按规则路由到不同表。哈希分片：hash(shardingKey) % tableCount，数据均匀但扩容需重新哈希（迁移大量数据）。范围分片：按 shardingKey 范围分表，扩容方便（加新范围）但可能热点（新数据都在最后一个表）。一致性哈希：分片键映射到哈希环，每个表负责环上一段，扩容只迁移相邻表的数据。跨分片查询（非分片键查询）需要扫描所有分片（性能差），可用冗余表或搜索引擎（ES）解决。
>
> **用法要点**：① 先优化（索引+SQL+缓存），数据量确实大再分库分表（增加复杂度）；② 分片键选查询最频繁的字段（如 user_id），尽量避免跨分片查询；③ 分片数用 2 的幂（64/128/256），便于扩容（翻倍）；④ 全局唯一 ID：雪花算法（Snowflake）、号段模式（Leaf）、UUID（不推荐，无序）；⑤ 跨分片 JOIN：用冗余字段、宽表、或应用层组装；⑥ 分布式事务：分库后跨库事务用 Seata AT/TCC 或本地消息表；⑦ 中间件：ShardingSphere-JDBC（客户端分片，推荐）或 ShardingSphere-Proxy（代理层）。

---

## 3. 常用用法

### 3.1 建表规范

```sql
CREATE TABLE `sys_user` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `password` varchar(100) NOT NULL COMMENT '密码',
  `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
  `status` tinyint NOT NULL DEFAULT 1 COMMENT '状态 1正常 0禁用',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` tinyint NOT NULL DEFAULT 0 COMMENT '逻辑删除 0未删 1已删',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  KEY `idx_status_create` (`status`,`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
```

> 🔍 **知识点深度解析**
>
> **作用**：建表规范是数据库设计的基础，合理的表结构和索引设计避免后期性能问题。命名规范、字段类型、索引设计都影响长期可维护性和性能。
>
> **原理**：InnoDB 表是聚簇索引组织表，主键即数据。自增 BIGINT 主键顺序插入，B+ Tree 页分裂少，性能好。utf8mb4 支持完整 Unicode（包括 emoji），是 MySQL 8.0 默认字符集。ON UPDATE CURRENT_TIMESTAMP 自动更新时间字段。联合索引 (status, create_time) 支持 WHERE status=? ORDER BY create_time（最左前缀+索引排序）。唯一索引 uk_username 保证用户名唯一，同时加速按用户名查询。
>
> **用法要点**：① 主键用 BIGINT AUTO_INCREMENT（不要用 UUID，随机插入页分裂）；② 字符集 utf8mb4（支持 emoji），排序规则 utf8mb4_unicode_ci 或 utf8mb4_0900_ai_ci（8.0）；③ 必须有 create_time/update_time（审计用），update_time 用 ON UPDATE CURRENT_TIMESTAMP；④ 逻辑删除字段 deleted（tinyint 默认0）；⑤ 字段 NOT NULL 尽量设默认值（NULL 影响索引和统计）；⑥ 索引命名：uk_唯一索引、idx_普通索引、uk_字段名；⑦ 不要用 TEXT/BLOB 存常用查询字段（影响性能，单独扩展表）。

### 3.2 索引操作

```sql
-- 创建索引
CREATE INDEX idx_username ON sys_user(username);
CREATE UNIQUE INDEX uk_email ON sys_user(email);
CREATE INDEX idx_status_create ON sys_user(status, create_time);

-- 查看索引
SHOW INDEX FROM sys_user;

-- 删除索引
DROP INDEX idx_username ON sys_user;

-- 隐藏索引（MySQL 8.0，先隐藏确认无影响再删除）
ALTER TABLE sys_user ALTER INDEX idx_username INVISIBLE;
ALTER TABLE sys_user ALTER INDEX idx_username VISIBLE;

-- 查看执行计划
EXPLAIN SELECT * FROM sys_user WHERE username = 'zhangsan';
EXPLAIN ANALYZE SELECT * FROM sys_user WHERE status = 1;  -- MySQL 8.0，实际执行
```

> 🔍 **知识点深度解析**
>
> **作用**：索引操作是日常 DBA 工作，创建合适的索引提升查询性能，删除无用索引减少写入开销和存储。隐藏索引（8.0）安全删除索引（先隐藏观察，确认无影响再删）。
>
> **原理**：CREATE INDEX 本质是构建 B+ Tree：扫描表数据，按索引键排序，构建非叶子节点和叶子节点。在线 DDL（MySQL 5.6+ INPLACE）创建索引时不锁表（允许 DML），但有 metadata lock。EXPLAIN 显示优化器选择的执行计划（不实际执行），EXPLAIN ANALYZE（8.0）实际执行并显示真实耗时和行数。索引基数（Cardinality）是索引中唯一值的数量，基数高的索引区分度好（优化器更倾向选）。ANALYZE TABLE 更新索引统计信息。
>
> **用法要点**：① 加索引前用 EXPLAIN 确认查询能走索引；② 大表加索引用 ALGORITHM=INPLACE, LOCK=NONE（不锁表）；③ 删除索引前先隐藏（INVISIBLE），观察慢查询日志确认无影响再删；④ 联合索引列顺序：等值查询列在前，范围查询列在后；⑤ 索引不是越多越好（增加写入开销和存储），无用索引定期清理；⑥ 用 sys.schema_unused_indexes 查看未使用的索引；⑦ 前缀索引：字符串前 N 个字符建索引（节省空间），但不能 ORDER BY/GROUP BY。

### 3.3 事务使用

```sql
-- 开启事务
START TRANSACTION;  -- 或 BEGIN

-- 执行操作
UPDATE account SET balance = balance - 100 WHERE id = 1;
UPDATE account SET balance = balance + 100 WHERE id = 2;

-- 提交
COMMIT;

-- 回滚
-- ROLLBACK;

-- 保存点（部分回滚）
START TRANSACTION;
INSERT INTO t1 VALUES (1);
SAVEPOINT sp1;
INSERT INTO t1 VALUES (2);
ROLLBACK TO SAVEPOINT sp1;  -- 回滚到 sp1，第一条 INSERT 保留
COMMIT;
```

> 🔍 **知识点深度解析**
>
> **作用**：事务保证多操作的原子性。显式事务（START TRANSACTION）将多个 SQL 包裹在一个事务中，要么全提交要么全回滚。保存点支持部分回滚。
>
> **原理**：START TRANSACTION 后，后续 SQL 在同一事务中执行，修改写入 undo log（用于回滚）和 redo log（用于持久化）。COMMIT 时：刷 redo log 到磁盘（持久化），释放锁，事务可见。ROLLBACK 时：根据 undo log 反向操作，恢复数据，释放锁。自动提交（autocommit=1，默认）：每条 SQL 是一个独立事务（自动提交）。长事务：事务长时间不提交，持有锁、undo log 无法清理（影响 MVCC 性能）、主从延迟。
>
> **用法要点**：① 事务尽量短（不要在事务内有远程调用、用户输入、循环）；② 避免长事务（information_schema.innodb_trx 查看长事务）；③ 死锁后重试（应用层捕获死锁异常重试）；④ 不要在事务中混合事务性和非事务性操作（如发邮件，回滚了邮件已发）；⑤ 保存点用于复杂事务的部分回滚；⑥ 批量操作用事务（一次提交比每条提交快很多）；⑦ Spring @Transactional 默认 RuntimeException 回滚，用 rollbackFor=Exception.class。

### 3.4 备份与恢复

```bash
# 逻辑备份（mysqldump）
mysqldump -u root -p --single-transaction --routines --triggers --all-databases > backup.sql

# 单库备份
mysqldump -u root -p --single-transaction app_db > app_db.sql

# 恢复
mysql -u root -p app_db < app_db.sql

# 物理备份（xtrabackup，在线热备）
xtrabackup --backup --target-dir=/data/backup
xtrabackup --prepare --target-dir=/data/backup  # 准备（应用 redo log）
xtrabackup --copy-back --target-dir=/data/backup  # 恢复

# binlog 闪回（误操作恢复）
mysqlbinlog --start-datetime="2024-01-01 10:00:00" --stop-datetime="2024-01-01 10:05:00" binlog.000001 | mysql -u root -p
```

> 🔍 **知识点深度解析**
>
> **作用**：备份是数据安全的最后防线。逻辑备份（mysqldump）适合小库和迁移，物理备份（xtrabackup）适合大库在线热备。binlog 用于时间点恢复（PITR）和误操作闪回。
>
> **原理**：mysqldump --single-transaction 在 RR 隔离级别下开启一致性快照读，导出数据时不锁表（InnoDB），保证数据一致性。物理备份（xtrabackup）：复制 InnoDB 数据文件+redo log，prepare 阶段应用 redo log 达到一致性状态，copy-back 恢复数据文件。binlog 记录所有数据变更，配合全量备份可恢复到任意时间点（全量恢复 + binlog 重放到故障前）。ROW 格式 binlog 可用闪回工具（MyFlash、binlog2sql）反向生成回滚 SQL。
>
> **用法要点**：① 生产必须有备份策略（全量+增量，定期恢复演练）；② 小库用 mysqldump --single-transaction（不锁表），大库用 xtrabackup（物理备份快）；③ binlog 必须开启（log_bin=1, binlog_format=ROW），用于 PITR 和闪回；④ 误操作：不要直接覆盖，先用 binlog2sql 生成回滚 SQL；⑤ 延迟从库（延迟1小时）是误操作恢复的利器；⑥ 备份文件要异地存储（不要和数据库同机）；⑦ 定期做恢复演练（备份不可用等于没备份）。

### 3.5 常用监控

```sql
-- 查看连接数
SHOW PROCESSLIST;
SHOW STATUS LIKE 'Threads_connected';

-- 查看 InnoDB 状态（死锁、锁等待）
SHOW ENGINE INNODB STATUS;

-- 查看当前事务
SELECT * FROM information_schema.innodb_trx;

-- 查看锁等待
SELECT * FROM performance_schema.data_lock_waits;

-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query%';
SELECT * FROM mysql.slow_log;

-- 查看主从状态
SHOW SLAVE STATUS\G
```

> 🔍 **知识点深度解析**
>
> **作用**：监控是数据库运维的基础，及时发现连接数过高、锁等待、慢查询、主从延迟等问题。performance_schema 是 MySQL 性能监控的核心。
>
> **原理**：information_schema.innodb_trx 显示当前运行的事务（trx_started 开始时间，trx_rows_locked 锁行数）。performance_schema.data_locks 和 data_lock_waits 显示当前持有的锁和等待的锁（MySQL 8.0 替代了旧的 innodb_locks）。慢查询日志记录执行时间超过 long_query_time 的 SQL。主从状态：Seconds_Behind_Master 显示从库延迟秒数（不准确，用 pt-heartbeat 更准）。Threads_connected 是当前连接数，Threads_running 是活跃连接数（高则负载大）。
>
> **用法要点**：① 连接数过高：SHOW PROCESSLIST 看是否有长查询/锁等待，max_connections 合理设置；② 死锁：SHOW ENGINE INNODB STATUS 看 LATEST DETECTED DEADLOCK；③ 锁等待：performance_schema.data_lock_waits 看谁等谁；④ 慢查询：开启 slow_query_log，用 pt-query-digest 分析；⑤ 主从延迟：Seconds_Behind_Master 或更准确的 pt-heartbeat；⑥ 用 Prometheus + mysqld_exporter + Grafana 做可视化监控；⑦ 告警：连接数>80%、慢查询突增、主从延迟>30s、磁盘>80%。

### 3.6 常用函数

```sql
-- 字符串
SELECT CONCAT('Hello', ' ', 'World');       -- 拼接
SELECT SUBSTRING('abcdef', 2, 3);            -- 截取 bcd
SELECT REPLACE('abc', 'b', 'x');             -- 替换 axc
SELECT LENGTH('中文');                        -- 字节数 6（utf8mb4）
SELECT CHAR_LENGTH('中文');                   -- 字符数 2

-- 日期
SELECT NOW(), CURDATE(), CURTIME();
SELECT DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s');
SELECT DATE_ADD(NOW(), INTERVAL 7 DAY);      -- 加7天
SELECT DATEDIFF('2024-12-31', '2024-01-01'); -- 天数差
SELECT UNIX_TIMESTAMP();                      -- 时间戳

-- 聚合
SELECT COUNT(*), SUM(amount), AVG(amount), MAX(amount), MIN(amount) FROM orders;
SELECT status, COUNT(*) FROM orders GROUP BY status WITH ROLLUP;  -- 汇总行

-- 条件
SELECT IF(status=1, '正常', '禁用') FROM user;
SELECT CASE WHEN age<18 THEN '未成年' WHEN age<60 THEN '成年' ELSE '老年' END FROM user;
SELECT COALESCE(NULL, '默认值');              -- 取第一个非null
```

> 🔍 **知识点深度解析**
>
> **作用**：内置函数简化 SQL 编写，字符串、日期、聚合、条件函数是最常用的。但要注意函数用在索引列上会导致索引失效。
>
> **原理**：函数在 SQL 执行时逐行计算（WHERE 中用函数是过滤时计算，SELECT 中是结果计算）。WHERE DATE(create_time)='2024-01-01' 会对每行计算 DATE()，索引失效（应改为 create_time BETWEEN '2024-01-01 00:00:00' AND '2024-01-01 23:59:59'）。聚合函数（COUNT/SUM/AVG）在 GROUP BY 分组后计算，WITH ROLLUP 生成多层汇总。COALESCE 返回第一个非 NULL 参数，常用于默认值。
>
> **用法要点**：① 不要在 WHERE 的索引列上用函数（索引失效）；② 日期范围查询用 BETWEEN 或 >= AND <，不要用 DATE() 包裹；③ COUNT(*) 统计行数（InnoDB 全表扫，大表慢），COUNT(列) 统计非 NULL 行数；④ 字符串模糊匹配用 LIKE 'xxx%'（前缀走索引），不要用 '%xxx'；⑤ 用 CASE WHEN 替代多个 IF 嵌套；⑥ 聚合+GROUP BY 时，SELECT 的非聚合列必须在 GROUP BY 中（ONLY_FULL_GROUP_BY 模式）；⑦ MySQL 8.0 窗口函数（ROW_NUMBER/RANK/SUM OVER）解决分组排名等复杂需求。

### 3.7 性能调优参数

```ini
[mysqld]
# 内存
innodb_buffer_pool_size = 4G           # 缓冲池，物理内存50-70%
innodb_buffer_pool_instances = 4       # 缓冲池实例数（减少锁竞争）

# 日志
innodb_log_file_size = 1G              # redo log 大小
innodb_log_buffer_size = 64M           # redo log 缓冲区
innodb_flush_log_at_trx_commit = 1     # 1=每次提交刷盘（最安全），0/2=性能好但可能丢数据
sync_binlog = 1                        # 1=每次提交刷 binlog（最安全）

# 连接
max_connections = 500
wait_timeout = 600
interactive_timeout = 600

# 排序/临时表
sort_buffer_size = 4M
tmp_table_size = 64M
max_heap_table_size = 64M

# 慢查询
slow_query_log = 1
long_query_time = 1
slow_query_log_file = /var/log/mysql/slow.log
```

> 🔍 **知识点深度解析**
>
> **作用**：参数调优提升 MySQL 性能，核心是内存分配（Buffer Pool）和日志刷盘策略。合理配置减少 IO、提升并发能力。
>
> **原理**：innodb_buffer_pool_size 是 InnoDB 最重要的参数，缓存数据页和索引页，命中率越高性能越好（生产通常物理内存 50-70%）。innodb_flush_log_at_trx_commit=1：每次 COMMIT 刷 redo log 到磁盘（最安全，性能稍差）；=0：每秒刷一次（崩溃丢1秒数据）；=2：每次提交写到 OS 缓存，每秒刷盘（崩溃丢1秒，性能好）。sync_binlog=1：每次提交刷 binlog（配合半同步复制安全）。sort_buffer_size：每个排序会话分配的内存，太大反而消耗内存。tmp_table_size：内存临时表上限，超过则转磁盘临时表（性能差）。
>
> **用法要点**：① innodb_buffer_pool_size 设为物理内存 50-70%（留给 OS 和其他进程）；② innodb_log_file_size 设 1-4GB（减少 checkpoint，大事务不卡顿）；③ 数据安全：innodb_flush_log_at_trx_commit=1 + sync_binlog=1（双1，最安全）；④ 性能优先可设 =2（崩溃可能丢1秒，金融场景不要）；⑤ max_connections 根据应用连接池设置（不要设太大，内存不够）；⑥ 慢查询日志必开（long_query_time=1，定位慢 SQL）；⑦ 用 mysqltuner.pl 或 tuning-primer.sh 辅助调优（参考，不要全信）。

### 3.8 高可用方案

**主从复制 + 读写分离**：主库写，从库读，主库挂了手动/自动切换。

**MHA（Master High Availability）**：自动检测主库故障，自动切换，VIP 漂移。

**InnoDB Cluster**：MySQL 官方高可用方案，组复制（MGR）+ MySQL Router，自动故障转移。

**云数据库**：RDS（阿里云/腾讯云/AWS），自带高可用、备份、监控。

> 🔍 **知识点深度解析**
>
> **作用**：高可用保证数据库服务不中断（SLA 99.99%）。主从复制是基础，MHA/InnoDB Cluster 实现自动故障转移，云数据库省心但成本高。
>
> **原理**：MHA：Manager 节点监控主库，检测到主库故障后，选择最新的从库（relay log 最新）提升为主库，其他从库指向新主库，VIP 漂移到新主库。需要 SSH 互信和半同步复制。InnoDB Cluster：基于组复制（MGR，Paxos 协议），至少3节点，写操作需多数派确认，自动选主和故障转移，MySQL Router 作为代理自动路由到新主库。云数据库 RDS：主从架构+自动故障转移+备份+监控，运维省心。
>
> **用法要点**：① 生产必须高可用（单实例有单点故障风险）；② 简单方案：主从+MHA（自动切换），或直接用云 RDS；③ MySQL 官方方案：InnoDB Cluster（MGR+Router），适合不想引入第三方工具；④ 读写分离注意主从延迟（刚写马上读可能读不到，用强制读主或缓存）；⑤ 切换后检查：新主库 read_only=0、从库指向新主、应用连接串/VIP 更新；⑥ 定期演练故障切换（确保切换流程可用）；⑦ 数据一致性：半同步复制减少主从数据不一致。

---

## 4. 注意事项

1. **必须有主键**：InnoDB 聚簇索引表，没主键会用隐藏行ID，影响性能和复制。用自增 BIGINT。

2. **索引列不要用函数**：WHERE DATE(create_time)=?、WHERE YEAR(create_time)=2024 索引失效，改用范围查询。

3. **避免 SELECT ***：只查需要的列，减少网络传输和内存，可能用到覆盖索引。

4. **深翻页优化**：LIMIT 100000,10 很慢，用游标分页（WHERE id > lastId LIMIT 10）。

5. **避免大事务**：长事务持有锁、undo log 膨胀、主从延迟。事务内不要有远程调用。

6. **UPDATE/DELETE 必须走索引**：没索引会锁全表，并发灾难。用 EXPLAIN 确认。

7. **字符集用 utf8mb4**：支持 emoji 和完整 Unicode，MySQL 8.0 默认。不要用 utf8（utf8mb3，不完整）。

8. **NULL 值影响**：NULL 列索引统计不准、NOT IN 查询结果异常、COUNT(列) 不统计 NULL。尽量 NOT NULL + 默认值。

9. **ORDER BY/GROUP BY 用索引**：没索引会 filesort/temporary，性能差。联合索引覆盖排序字段。

10. **连接池配置**：HikariCP 最大连接数不要太大（公式：connections = ((core_count * 2) + effective_spindle_count)）。

11. **定期备份和演练**：备份必须有，且定期恢复演练（备份不可用等于没备份）。

12. **慢查询治理**：开启慢查询日志，定期分析优化。慢查询是性能问题的主要来源。

---

> 💡 **深度讲解**：MySQL 是最流行的关系型数据库，InnoDB 是默认存储引擎，核心是聚簇索引+MVCC+事务。架构分连接层、SQL层（解析器→优化器→执行器）、存储引擎层。索引用 B+ Tree，聚簇索引叶子节点存数据，二级索引存主键值（回表），联合索引遵循最左前缀，覆盖索引避免回表。事务 ACID 由 redo log（持久化）+ undo log（原子性/MVCC）+ 锁（隔离性）保证，默认 RR 隔离级别用 MVCC+Next-Key Lock 解决幻读。锁机制：行锁基于索引，没索引升级表锁，间隙锁防止幻读，MDL 锁可能阻塞 DDL。性能优化核心是索引设计和 SQL 优化：用 EXPLAIN 分析执行计划，避免全表扫、filesort、temporary，深翻页用游标，JOIN 小表驱动大表。主从复制实现高可用和读写分离，半同步减少数据丢失。数据量大了分库分表（垂直分库+水平分表，哈希/范围分片），但增加复杂度（分布式事务、跨分片查询）。生产环境必须有备份（mysqldump/xtrabackup）、监控（Prometheus+Grafana）、高可用（MHA/InnoDB Cluster/RDS）。理解了 InnoDB 原理和索引机制，就能设计高性能的数据库架构。
>
> **📝 精简总结**：MySQL=InnoDB(聚簇索引+MVCC+事务)；索引=B+Tree，聚簇(存数据)/二级(存主键需回表)，最左前缀，覆盖索引；事务=ACID，redo(持久化)+undo(回滚/MVCC)，默认RR，MVCC读写不阻塞；锁=行锁(基于索引)/间隙锁/MDL，没索引表锁；优化=EXPLAIN+索引+避免函数/深翻页/SELECT*；高可用=主从复制+半同步+MHA/InnoDB Cluster；大数据=分库分表(哈希/范围分片)；必做=主键自增BIGINT+utf8mb4+备份+慢查询监控。

---

> 📋 **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 知识点深度解析」模块（作用+原理+用法要点），原有内联图已统一风格化美化（圆角、阴影、渐变、动画）。所有原有内容完整保留，未做任何修改。
