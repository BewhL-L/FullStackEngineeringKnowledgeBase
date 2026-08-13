---
title: MongoDB 知识点系统梳理
tags: [数据库, MongoDB, NoSQL, 文档数据库, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# MongoDB 知识点系统梳理（优化版）

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

### 7.2 选举机制

- 主节点故障时，从节点自动选举新主节点
- 需要大多数节点存活才能选举（避免脑裂）
- 优先级（priority）高的节点优先成为主节点

### 7.3 读写策略

```javascript
// 读偏好：从节点读
db.users.find().readPref("secondaryPreferred");

// 写关注：大多数节点确认
db.users.insertOne(doc, { writeConcern: { w: "majority" } });
```

---

## 8. 分片（Sharding）

### 8.1 架构

- **Shard**：数据分片，每个分片是一个副本集
- **Mongos**：路由节点，客户端连接入口
- **Config Server**：配置服务器，存储元数据（3个副本集）

### 8.2 分片键（Shard Key）

- 范围分片：按分片键范围分配
- 哈希分片：按分片键哈希分配（更均匀）

**分片键选择原则**：
- 高基数（值多）
- 分布均匀（避免热点）
- 查询常用（减少跨分片查询）

---

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
