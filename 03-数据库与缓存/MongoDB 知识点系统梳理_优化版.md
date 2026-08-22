---
title: MongoDB 知识点系统梳理
tags: [数据库, MongoDB, NoSQL, 文档数据库, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# MongoDB 知识点系统梳理（优化版）

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。


> **文档说明**：系统梳理 MongoDB 核心知识，涵盖文档模型、CRUD、索引、聚合、复制、分片、性能优化等内容。

---

## 1. 概述

MongoDB 是最流行的**文档型 NoSQL 数据库**，以 BSON（Binary JSON）格式存储数据，灵活的 schema 适合快速迭代和非结构化数据。

**核心特性**：
- 文档模型：BSON 格式，支持嵌套文档和数组
- 灵活 schema：同一集合文档结构可不同
- 高性能：内存映射存储引擎（WiredTiger）
- 高可用：副本集（Replica Set）自动故障转移
- 水平扩展：自动分片（Sharding）
- 丰富查询：支持 CRUD、聚合管道、全文搜索

**与关系型数据库对比**：
| MongoDB | MySQL |
|---------|-------|
| Database | Database |
| Collection | Table |
| Document | Row |
| Field | Column |
| Index | Index |
| _id（自动生成） | Primary Key |
| 嵌入文档/引用 | JOIN |

---

## 2. 数据类型

| 类型 | 说明 | 示例 |
|------|------|------|
| String | UTF-8 字符串 | "hello" |
| Integer | 32/64 位整数 | 100 |
| Double | 浮点数 | 99.5 |
| Boolean | 布尔 | true |
| Date | 日期（ISODate） | ISODate("2024-01-01") |
| ObjectId | 12 字节唯一 ID | ObjectId("5f...") |
| Array | 数组 | [1, 2, 3] |
| Object | 嵌套文档 | { "a": 1 } |
| Null | 空 | null |
| Binary Data | 二进制 | BinData(...) |

> 🔍 **知识点深度解析**
>
> **作用**：理解 BSON 数据类型是正确使用 MongoDB 的基础。
>
> **原理**：BSON 是 JSON 的二进制扩展，比 JSON 支持更多类型（Date、ObjectId、Binary、正则等）。`_id` 是 MongoDB 自动生成的主键，12 字节组成：4 字节时间戳 + 5 字节随机数 + 3 字节自增计数器，保证全局唯一且有序（可按时间排序）。文档大小限制 16MB，超过需用 GridFS 存储。
>
> **用法要点**：① _id 自动生成，也可手动指定（必须唯一）；② 日期用 ISODate，不要用字符串（影响查询和排序）；③ 数字默认 Double，整数用 NumberInt()/NumberLong()；④ 面试常考：BSON vs JSON、_id 结构、文档大小限制。

---

## 3. 数据库与集合操作

```javascript
// 切换/创建数据库（插入数据后才真正创建）
use mydb;

// 创建集合
db.createCollection("users", {
  capped: false,
  size: 1000000,  // capped 集合大小上限
  max: 1000       // capped 集合文档数上限
});

// 查看集合
show collections;

// 删除集合
db.users.drop();

// 删除数据库
db.dropDatabase();
```

---

## 4. 文档 CRUD

### 4.1 插入（Create）

```javascript
// 插入单条
db.users.insertOne({
  name: "张三",
  age: 25,
  email: "zhangsan@example.com",
  address: { city: "北京", district: "海淀" },
  hobbies: ["读书", "编程"],
  createTime: new Date()
});

// 插入多条
db.users.insertMany([
  { name: "李四", age: 30 },
  { name: "王五", age: 28 }
]);
```

> 🔍 **知识点深度解析**
>
> **作用**：insertOne/insertMany 向集合写入文档，是 CRUD 的第一步；MongoDB 文档为 BSON，支持嵌套与数组，写入即自动建集合。
>
> **原理**：插入时若集合不存在则隐式创建；文档必须有唯一 _id（未指定时驱动自动生成 ObjectId）。写入经 WiredTiger 落到数据文件，并按 writeConcern 决定写确认级别（w:1 主节点确认，w:"majority" 多数派确认）。嵌套文档与数组以 BSON 子结构存储，无需预先定义 schema。
>
> **用法要点**：① 批量插入用 insertMany（一次网络往返，性能高）；② _id 可手动指定（需全局唯一），否则自动生成 ObjectId；③ 重要数据写用 writeConcern w:"majority"；④ 无序批量（ordered:false）并行更快，出错不中断；⑤ 关注文档 16MB 上限，超大用 GridFS。

### 4.2 查询（Read）

```javascript
// 查询所有
db.users.find();

// 条件查询
db.users.find({ age: { $gt: 25 } }); // age > 25

// 比较运算符：$gt $gte $lt $lte $ne $in $nin
db.users.find({ age: { $in: [25, 30] } });

// 逻辑运算符：$and $or $not $nor
db.users.find({ $or: [{ age: 25 }, { name: "李四" }] });

// 嵌套文档查询
db.users.find({ "address.city": "北京" });

// 数组查询
db.users.find({ hobbies: "编程" }); // 包含"编程"
db.users.find({ hobbies: { $size: 2 } }); // 数组长度为2

// 投影（指定返回字段）
db.users.find({}, { name: 1, age: 1, _id: 0 });

// 排序、分页
db.users.find().sort({ age: -1 }).skip(10).limit(10);

// 计数
db.users.countDocuments({ age: { $gt: 25 } });
```

> 🔍 **知识点深度解析**
>
> **作用**：find 是 MongoDB 最常用操作，支持条件、逻辑、嵌套、数组、投影、排序分页等丰富查询，是数据读取核心。
>
> **原理**：find 返回游标（Cursor），结果分批拉取而非一次性加载。查询条件用操作符：$gt/$gte/$lt/$lte/$in 比较，$and/$or/$nor 逻辑，点号 "address.city" 访问嵌套字段，数组字段直接匹配元素或 $size 匹配长度。投影 {field:1} 只返回指定字段（_id 默认返回，需显式 0 排除）。sort/skip/limit 用于排序分页。
>
> **用法要点**：① 条件查询用比较/逻辑操作符，避免全表扫；② 嵌套字段用点号，数组用元素匹配；③ 投影减少网络与内存（如需关闭 _id 设 0）；④ 分页用 sort+skip+limit，大数据量改用 _id 游标分页；⑤ 计数用 countDocuments（带过滤）或 estimatedDocumentCount（快但忽略过滤）；⑥ 为高频查询字段建索引以加速。

### 4.3 更新（Update）

```javascript
// 更新单条
db.users.updateOne(
  { name: "张三" },
  { $set: { age: 26, "address.city": "上海" } }
);

// 更新多条
db.users.updateMany(
  { age: { $lt: 25 } },
  { $inc: { age: 1 } } // age 自增 1
);

// 替换文档（整个替换）
db.users.replaceOne({ name: "张三" }, { name: "张三", age: 27 });

// 更新运算符：$set $unset $inc $mul $rename $push $pull $addToSet
db.users.updateOne({ name: "张三" }, { $push: { hobbies: "游泳" } });
db.users.updateOne({ name: "张三" }, { $pull: { hobbies: "读书" } });
```

> 🔍 **知识点深度解析**
>
> **作用**：updateOne/updateMany/replaceOne 修改文档，更新运算符是 MongoDB 强大之处，可精准修改字段、数组，而非整体替换。
>
> **原理**：更新运算符在存储引擎层原地修改（WiredTiger 靠文档级锁与 MVCC）。$set 设置字段（不存在则创建），$unset 删除字段，$inc/$mul 数值增减，$rename 改名；$push/$pull/$addToSet 操作数组（追加/移除/去重追加）。replaceOne 用新文档整体替换（保留 _id）。默认只更新匹配的第一条（updateOne），updateMany 更新全部匹配。
>
> **用法要点**：① 更新务必用 $set 等运算符，直接传对象会整体替换；② 嵌套字段用 "address.city" 语法；③ 数组用 $push/$pull/$addToSet 而非读改写；④ 数值自增用 $inc（并发安全）；⑤ 更新条件务必走索引，否则扫描全集合；⑥ 大批量更新注意性能与锁，分批进行。

### 4.4 删除（Delete）

```javascript
db.users.deleteOne({ name: "张三" });
db.users.deleteMany({ age: { $lt: 20 } });
```

> 🔍 **知识点深度解析**
>
> **作用**：CRUD 是 MongoDB 基础操作，更新运算符是重点。
>
> **原理**：`find()` 返回游标（Cursor），不是一次性加载所有数据，而是分批获取。`updateOne/updateMany` 用更新运算符修改字段，`replaceOne` 整个替换文档（保留 _id）。`$set` 更新字段（不存在则创建），`$unset` 删除字段，`$inc` 数值增减，`$push` 数组追加，`$pull` 数组移除，`$addToSet` 数组去重追加。写操作默认是安全写入（write concern w:1），可配置 w:majority 确保大多数节点确认。
>
> **用法要点**：① 更新用 $set，不要直接传对象（会替换整个文档）；② 嵌套字段用点号 "address.city"；③ 分页用 skip+limit，大数据量用 _id 游标分页（避免 skip 性能问题）；④ 面试常考：更新运算符、find 游标、分页优化、write concern。

---

## 5. 索引

### 5.1 索引类型

| 类型 | 说明 |
|------|------|
| 单字段索引 | `{ name: 1 }` |
| 复合索引 | `{ age: 1, name: -1 }` |
| 多键索引 | 数组字段自动创建 |
| 文本索引 | 全文搜索 `{ content: "text" }` |
| 地理空间索引 | `{ location: "2dsphere" }` |
| 哈希索引 | 分片用 `{ _id: "hashed" }` |
| TTL 索引 | 自动过期 `{ createTime: 1 }, expireAfterSeconds: 86400` |
| 唯一索引 | `{ email: 1 }, unique: true` |

> 🔍 **知识点深度解析**
>
> **作用**：索引类型决定 MongoDB 能高效支撑哪些查询场景（单字段、复合、数组、全文、地理、TTL 等），是查询性能的基础。
>
> **原理**：单字段索引只加速该字段查询；复合索引按字段顺序构建 B-Tree，遵循最左前缀；多键索引对数组字段自动为多元素建索引；文本索引支持全文检索（可多字段加权）；2dsphere 用于地理空间；hashed 索引用于分片路由（哈希分布）；TTL 索引基于时间字段自动删除过期文档（后台线程轮询）；唯一索引强制字段值唯一。
>
> **用法要点**：① 等值/排序/范围高频字段建索引；② 数组字段自动多键索引，注意索引膨胀；③ 全文检索用 text 索引（可指定权重与语言）；④ 过期数据（日志、验证码）用 TTL 索引自动清理；⑤ 分片键可用 hashed 索引均化分布；⑥ 唯一索引防止重复（如 email），但会使写入变慢。

### 5.2 索引操作

```javascript
// 创建索引
db.users.createIndex({ name: 1 });
db.users.createIndex({ age: 1, name: -1 }); // 复合索引
db.users.createIndex({ email: 1 }, { unique: true }); // 唯一索引
db.users.createIndex({ createTime: 1 }, { expireAfterSeconds: 86400 }); // TTL

// 查看索引
db.users.getIndexes();

// 查看执行计划
db.users.find({ age: 25 }).explain("executionStats");

// 删除索引
db.users.dropIndex("name_1");
```

> 🔍 **知识点深度解析**
>
> **作用**：createIndex / getIndexes / dropIndex / explain 是索引的日常运维操作，用于创建、查看、删除索引与分析命中情况。
>
> **原理**：createIndex 扫描集合、按索引键排序构建 B-Tree（4.2+ 默认在线构建、不长时间锁表）。getIndexes 列出已有索引（含 _id 默认索引）。explain("executionStats") 返回执行计划，含 totalKeysExamined（扫描索引项）与 totalDocsExamined（扫描文档数）、executionTimeMillis 等，用以判断是否走索引。dropIndex 删除无用索引。
>
> **用法要点**：① 建索引用 createIndex，复合索引按 ESR 排字段顺序；② 大集合建索引注意资源（4.2+ 默认可在线）；③ 用 explain 检查是否 IXSCAN 而非 COLLSCAN；④ 删除无用索引前先观察影响或用隐藏索引思路评估；⑤ 唯一/稀疏索引按业务选型；⑥ 定期 review 索引，避免过度索引拖慢写入。

### 5.3 索引优化原则

- 等值查询字段 + 排序字段 + 范围查询字段（ESR 原则）
- 复合索引遵循最左前缀
- 避免在低选择性字段建索引（如性别）
- 索引不是越多越好，影响写入性能
- 用 explain() 分析查询是否走索引

> 🔍 **知识点深度解析**
>
> **作用**：索引是查询性能的关键，合理索引能大幅提升查询速度。
>
> **原理**：MongoDB 默认用 WiredTiger 存储引擎，索引是 B-Tree 结构（与 MySQL 类似）。复合索引遵循最左前缀原则：查询条件必须包含索引的第一个字段才能命中。ESR 原则：等值（Equality）字段放前，排序（Sort）字段居中，范围（Range）字段放后。索引覆盖（Covered Query）：查询字段和返回字段都在索引中，不需要回表查文档，性能最好。
>
> **用法要点**：① 复合索引顺序很重要，等值在前、范围在后；② 用 explain() 看 executionStats，检查 totalDocsExamined（扫描文档数）和 totalKeysExamined（扫描索引数）；③ 索引字段选择：高选择性、查询频繁、排序字段；④ TTL 索引用于日志、验证码等自动过期数据；⑤ 面试常考：索引类型、复合索引最左前缀、ESR 原则、explain 分析。

---

## 6. 聚合管道（Aggregation）

```javascript
db.orders.aggregate([
  // $match：过滤（相当于 WHERE）
  { $match: { status: "paid", createTime: { $gte: ISODate("2024-01-01") } } },
  
  // $group：分组（相当于 GROUP BY）
  {
    $group: {
      _id: "$userId",
      totalAmount: { $sum: "$amount" },
      orderCount: { $sum: 1 },
      avgAmount: { $avg: "$amount" }
    }
  },
  
  // $sort：排序
  { $sort: { totalAmount: -1 } },
  
  // $limit：限制
  { $limit: 10 },
  
  // $project：投影（相当于 SELECT）
  { $project: { userId: "$_id", totalAmount: 1, orderCount: 1, _id: 0 } }
]);
```

**常用阶段**：`$match`、`$group`、`$sort`、`$project`、`$limit`、`$skip`、`$unwind`（拆分数组）、`$lookup`（关联查询）、`$facet`（多面聚合）

---

## 7. 副本集（Replica Set）

### 7.1 架构

- **Primary**：主节点，处理所有写请求
- **Secondary**：从节点，复制主节点数据，可处理读请求
- **Arbiter**：仲裁节点，不存数据，只参与选举

> 🔍 **知识点深度解析**
>
> **作用**：副本集由 Primary + 多个 Secondary（+ 可选 Arbiter）组成，提供数据冗余、高可用与读扩展，是生产必备。
>
> **原理**：Primary 接收所有写请求，将写操作记录 oplog（操作日志）；Secondary 异步拉取 oplog 并重放，保持与 Primary 数据一致。Arbiter 只参与选举投票、不存数据，用于在节点数为偶数时凑成奇数票。客户端写走 Primary，读可配置 readPreference 路由到 Secondary 分担压力。副本集通过选举保证始终最多一个 Primary。
>
> **用法要点**：① 生产至少 1 主 2 从（或加 Arbiter 凑奇数）；② Primary 唯一，所有写走它；③ Secondary 默认不可写（readPreference 可读）；④ Arbiter 不存数据，仅投票，部署轻量；⑤ 副本集提供自动故障转移，但需多数派存活才能选举；⑥ 用副本集 connection string 连接，自动感知主节点变化。

### 7.2 选举机制

- 主节点故障时，从节点自动选举新主节点
- 需要大多数节点存活才能选举（避免脑裂）
- 优先级（priority）高的节点优先成为主节点

> 🔍 **知识点深度解析**
>
> **作用**：选举机制在主节点故障时自动从 Secondary 中选出新 Primary，保障服务连续性，是副本集高可用的核心。
>
> **原理**：副本集节点间通过心跳检测彼此存活。Primary 失联后，存活节点发起选举，需获得多数派（>N/2）选票才能成为 Primary（避免脑裂）。优先级（priority）高的节点更可能当选；同优先级比较最新 oplog 时间戳（数据最新者优先）。选举期间集群短暂不可写（通常秒级）。Arbiter 提供关键一票帮助凑成多数派。
>
> **用法要点**：① 节点数取奇数，确保能形成多数派；② 用 priority 指定首选主节点（如配置更高的机器 priority 高）；③ 多数派存活才能选举，故网络分区可能导致无主（保护一致性）；④ 选举期间写入失败，应用应重试；⑤ 隐藏/延迟节点不参与选举但可用于备份；⑥ 监控 rs.status 与主从延迟。

### 7.3 读写策略

```javascript
// 读偏好：从节点读
db.users.find().readPref("secondaryPreferred");

// 写关注：大多数节点确认
db.users.insertOne(doc, { writeConcern: { w: "majority" } });
```

---

> 🔍 **知识点深度解析**
>
> **作用**：读写策略（readPreference / writeConcern）控制读请求路由与写确认强度，在性能与数据一致性之间权衡。
>
> **原理**：readPreference 决定读请求发往哪个节点：primary（只主，强一致）、primaryPreferred、secondary（只从，可能读旧数据）、secondaryPreferred、nearest（最近节点）。writeConcern 决定写操作需多少节点确认：w:1（主节点确认即返回，快但可能丢）、w:"majority"（多数派持久化，安全）。配合 readConcern（local/majority）可控制读到已提交数据，避免脏读。
>
> **用法要点**：① 读一致性要求高用 primary；读多写少用 secondaryPreferred 分摊；② 跨地域用 nearest 降低延迟；③ 重要数据写用 w:"majority"（防主宕丢数据）；④ 配合 readConcern:"majority" 避免读到回滚的数据；⑤ 从节点读有复制延迟，关键读别依赖从节点；⑥ 因果一致会话保证会话内读写顺序。

## 8. 分片（Sharding）

### 8.1 架构

- **Shard**：数据分片，每个分片是一个副本集
- **Mongos**：路由节点，客户端连接入口
- **Config Server**：配置服务器，存储元数据（3个副本集）

> 🔍 **知识点深度解析**
>
> **作用**：分片将超大数据集水平拆分到多个 Shard，实现存储与吞吐的水平扩展，突破单机容量与性能上限。
>
> **原理**：Shard 是真正存数据的副本集；Mongos 是查询路由层，客户端只连 Mongos，由它解析查询、定位目标分片并合并结果；Config Server（3 节点副本集）存储集群元数据（分片与 chunk 映射）。数据按分片键切成 chunk 分布到各 Shard，chunk 过大触发自动分裂（split），再迁移（balance）到负载低的 Shard，保持均衡。
>
> **用法要点**：① 三大角色：Shard（存数据）/Mongos（路由）/Config（元数据）；② 客户端只连 Mongos，勿直连 Shard；③ 分片是应对海量数据的方案，数据量不大先垂直优化；④ Config Server 必须 3 节点且高可用（元数据丢失集群不可用）；⑤ chunk 自动分裂与均衡，无需手动干预；⑥ 监控 balancing 状态与 chunk 分布。

### 8.2 分片键（Shard Key）

- 范围分片：按分片键范围分配
- 哈希分片：按分片键哈希分配（更均匀）

**分片键选择原则**：
- 高基数（值多）
- 分布均匀（避免热点）
- 查询常用（减少跨分片查询）

---

> 🔍 **知识点深度解析**
>
> **作用**：分片键决定数据如何路由到各分片，是分片集群设计成败的关键，直接影响分布均匀性与查询效率。
>
> **原理**：分片键是集合中的某个字段，文档按分片键值路由到对应 chunk。范围分片：按分片键的值范围分配（连续数据在一片，范围查询好但易热点）；哈希分片：对分片键做哈希后取模分配（数据均匀、避免热点，但范围查询需扫多片）。分片键一旦指定不可更改，需提前慎重选择。
>
> **用法要点**：① 分片键选高基数（值多）、分布均匀的字段（如 user_id），避免热点；② 范围分片适合范围查询，哈希分片适合均匀分布；③ 查询尽量带分片键（定向到单/少分片），否则广播到所有分片（scatter-gather，慢）；④ 复合哈希/范围可按业务组合；⑤ 分片键不可更改，建集合前规划好；⑥ 热点写入（如自增 _id 范围分片）会集中单分片，优先哈希分片。

## 9. 性能优化

- 合理设计索引，用 explain 分析
- 避免大文档（< 16MB，建议 < 256KB）
- 嵌入 vs 引用：一对多用嵌入，多对多用引用
- 分页用游标分页，避免大 skip
- 批量操作用 bulkWrite
- 热点数据放内存（WiredTiger 缓存）
- 监控慢查询（profiler）

---

## 10. 面试高频考点

1. **MongoDB 特点**：文档模型、灵活 schema、与 MySQL 区别
2. **_id 结构**：12 字节组成、全局唯一
3. **CRUD**：更新运算符、查询运算符
4. **索引**：类型、复合索引最左前缀、ESR 原则、explain
5. **聚合管道**：常用阶段、与 SQL 对应
6. **副本集**：架构、选举、读写策略
7. **分片**：架构、分片键选择、哈希 vs 范围
8. **WiredTiger**：存储引擎、MVCC、文档级锁
9. **嵌入 vs 引用**：数据建模原则
10. **性能优化**：索引、分页、文档设计

---

## 📝 精简总结

- MongoDB 是文档型 NoSQL，BSON 存储，灵活 schema
- _id 是 12 字节自动生成主键，全局唯一
- CRUD 操作丰富，更新运算符功能强大
- 索引是 B-Tree，复合索引遵循最左前缀和 ESR 原则
- 聚合管道强大，$match+$group+$sort 是常用组合
- 副本集保证高可用，分片实现水平扩展
- 适用场景：非结构化数据、快速迭代、高并发读写、日志存储

---

[[03-数据库与缓存/MOC-数据库与缓存|← 返回数据库 MOC]] | [[Home|🏠 返回首页]]
