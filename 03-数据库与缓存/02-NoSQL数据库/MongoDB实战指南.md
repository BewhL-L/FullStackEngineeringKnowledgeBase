---
title: MongoDB实战指南
tags: [MongoDB, NoSQL, 文档数据库, 聚合管道, 后端, 数据库]
category: 数据库
created: 2026-08-27
updated: 2026-08-27
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 重要
pre: []
aliases: [MongoDB实战指南]
---

# MongoDB实战指南

> **文档说明**：MongoDB是最流行的文档型NoSQL数据库，以BSON文档存储，灵活Schema适合快速迭代。本文档覆盖数据模型、CRUD、聚合管道、索引、分片集群、与MySQL对比。
>
> **适用人群**：后端工程师、需要使用文档数据库的开发者
>
> **前置知识**：数据库基础、JSON/BSON

---

## 一、MongoDB核心概念

### 1.1 与关系型数据库对比

| MySQL | MongoDB | 说明 |
|-------|---------|------|
| Database | Database | 数据库 |
| Table | Collection | 表→集合 |
| Row | Document | 行→文档（BSON） |
| Column | Field | 列→字段 |
| Join | $lookup / 嵌入 | 关联查询 |
| Primary Key | _id | 主键（自动生成ObjectId） |
| Index | Index | 索引 |

### 1.2 BSON文档

```json
{
  "_id": ObjectId("5f5e..."),
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "age": 28,
  "address": {
    "city": "上海",
    "district": "浦东新区",
    "street": "世纪大道100号"
  },
  "hobbies": ["编程", "阅读", "跑步"],
  "orders": [
    { "orderId": "O001", "amount": 99.9, "date": ISODate("2024-01-01") },
    { "orderId": "O002", "amount": 199.0, "date": ISODate("2024-01-15") }
  ],
  "createdAt": ISODate("2024-01-01T00:00:00Z")
}
```

### 1.3 适用场景

| 适合 | 不适合 |
|------|--------|
| 灵活Schema，字段经常变化 | 强事务（金融转账） |
| 嵌套数据结构（文档内嵌） | 复杂多表关联查询 |
| 高并发读写 | 需要严格ACID的场景 |
| 大数据量，水平扩展 | 传统报表/复杂SQL分析 |
| 内容管理、用户画像、IoT | 数据一致性要求极高 |

---

## 二、CRUD操作

### 2.1 插入

```javascript
// 插入单条
db.users.insertOne({
  username: "zhangsan",
  age: 28,
  address: { city: "上海" },
  hobbies: ["编程", "阅读"],
  createdAt: new Date()
})

// 批量插入
db.users.insertMany([
  { username: "lisi", age: 25, city: "北京" },
  { username: "wangwu", age: 30, city: "广州" }
])
```

### 2.2 查询

```javascript
// 基础查询
db.users.find({ age: { $gte: 25 } })
db.users.findOne({ username: "zhangsan" })

// 条件操作符
db.users.find({
  age: { $in: [25, 28, 30] },
  city: { $ne: "北京" }
})

// 逻辑操作符
db.users.find({
  $and: [
    { age: { $gte: 25 } },
    { age: { $lte: 35 } }
  ],
  $or: [
    { city: "上海" },
    { city: "北京" }
  ]
})

// 嵌套字段查询
db.users.find({ "address.city": "上海" })

// 数组查询
db.users.find({ hobbies: "编程" })           // 包含
db.users.find({ hobbies: { $size: 3 } })      // 数组长度
db.users.find({ hobbies: { $all: ["编程", "阅读"] } })  // 全部包含

// 投影（字段筛选）
db.users.find({}, { username: 1, age: 1, _id: 0 })

// 排序、分页
db.users.find().sort({ age: -1 }).skip(10).limit(10)

// 计数
db.users.countDocuments({ city: "上海" })
```

### 2.3 更新

```javascript
// 更新单条
db.users.updateOne(
  { username: "zhangsan" },
  { $set: { age: 29, "address.city": "杭州" } }
)

// 更新多条
db.users.updateMany(
  { city: "上海" },
  { $set: { region: "华东" } }
)

// 替换文档
db.users.replaceOne(
  { username: "zhangsan" },
  { username: "zhangsan", age: 30, city: "深圳" }
)

// 更新操作符
db.users.updateOne({ username: "zhangsan" }, {
  $inc: { age: 1 },              // 自增
  $push: { hobbies: "游泳" },    // 数组追加
  $pull: { hobbies: "阅读" },    // 数组删除
  $addToSet: { hobbies: "编程" }, // 数组去重追加
  $unset: { oldField: "" }       // 删除字段
})

//  upsert（不存在则插入）
db.users.updateOne(
  { username: "newuser" },
  { $set: { age: 20 } },
  { upsert: true }
)
```

### 2.4 删除

```javascript
db.users.deleteOne({ username: "zhangsan" })
db.users.deleteMany({ age: { $lt: 18 } })
```

---

## 三、聚合管道

### 3.1 常用阶段

| 阶段 | 说明 |
|------|------|
| **$match** | 过滤文档（类似WHERE） |
| **$group** | 分组聚合（类似GROUP BY） |
| **$sort** | 排序 |
| **$project** | 字段投影/计算 |
| **$limit/$skip** | 分页 |
| **$lookup** | 关联查询（类似JOIN） |
| **$unwind** | 展开数组 |
| **$facet** | 多面聚合（一次计算多个聚合） |

### 3.2 聚合示例

```javascript
// 按城市分组统计用户数和平均年龄
db.users.aggregate([
  { $match: { age: { $gte: 18 } } },
  { $group: {
      _id: "$city",
      userCount: { $sum: 1 },
      avgAge: { $avg: "$age" },
      maxAge: { $max: "$age" }
  }},
  { $sort: { userCount: -1 } },
  { $limit: 10 }
])

// 展开数组后统计
db.users.aggregate([
  { $unwind: "$hobbies" },
  { $group: {
      _id: "$hobbies",
      count: { $sum: 1 }
  }},
  { $sort: { count: -1 } }
])

// 关联查询（$lookup）
db.orders.aggregate([
  { $match: { status: "paid" } },
  { $lookup: {
      from: "users",
      localField: "userId",
      foreignField: "_id",
      as: "userInfo"
  }},
  { $unwind: "$userInfo" },
  { $project: {
      orderId: 1,
      amount: 1,
      "userInfo.username": 1,
      "userInfo.city": 1
  }}
])
```

---

## 四、索引

### 4.1 索引类型

```javascript
// 单字段索引
db.users.createIndex({ username: 1 })  // 1升序，-1降序

// 复合索引
db.users.createIndex({ city: 1, age: -1 })

// 唯一索引
db.users.createIndex({ email: 1 }, { unique: true })

// 数组索引（多键索引）
db.users.createIndex({ hobbies: 1 })

// 文本索引（全文搜索）
db.articles.createIndex({ title: "text", content: "text" })
db.articles.find({ $text: { $search: "MongoDB 索引" } })

// TTL索引（自动过期）
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })

// 地理空间索引
db.places.createIndex({ location: "2dsphere" })
db.places.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [121.47, 31.23] },
      $maxDistance: 5000
    }
  }
})
```

### 4.2 索引优化

```javascript
// 查看执行计划
db.users.find({ city: "上海" }).explain("executionStats")

// 查看索引
db.users.getIndexes()

// 删除索引
db.users.dropIndex("city_1_age_-1")
```

---

## 五、Spring Boot集成

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-mongodb</artifactId>
</dependency>
```

```yaml
spring:
  data:
    mongodb:
      uri: mongodb://user:password@mongo1:27017,mongo2:27017/mydb?replicaSet=rs0
      auto-index-creation: true
```

```java
// 实体类
@Data
@Document(collection = "users")
public class User {
    @Id
    private String id;
    @Indexed(unique = true)
    private String username;
    private Integer age;
    private Address address;
    private List<String> hobbies;
    @CreatedDate
    private LocalDateTime createdAt;
}

// Repository
public interface UserRepository extends MongoRepository<User, String> {
    List<User> findByCity(String city);
    List<User> findByAgeBetween(Integer min, Integer max);
    Page<User> findByCity(String city, Pageable pageable);
}

// 聚合查询
@Autowired
private MongoTemplate mongoTemplate;

public List<CityStats> getCityStats() {
    return mongoTemplate.aggregate(
        Aggregation.newAggregation(
            Aggregation.match(Criteria.where("age").gte(18)),
            Aggregation.group("city").count().as("userCount")
                .avg("age").as("avgAge"),
            Aggregation.sort(Sort.Direction.DESC, "userCount")
        ),
        User.class, CityStats.class
    ).getMappedResults();
}
```

---

## 六、高可用与分片

### 6.1 副本集（Replica Set）

```mermaid
flowchart LR
    P[Primary主节点] -->|同步| S1[Secondary从节点1]
    P -->|同步| S2[Secondary从节点2]
    S1 -.->|选举| P
    S2 -.->|选举| P
```

- 一主多从，主节点写入，从节点同步
- 主节点宕机自动选举新主
- 读偏好：primary/primaryPreferred/secondary/secondaryPreferred/nearest

### 6.2 分片集群

```mermaid
flowchart TB
    R[Router mongos] --> S1[Shard1 副本集]
    R --> S2[Shard2 副本集]
    R --> S3[Shard3 副本集]
    C[Config Server] <--> R
```

| 组件 | 说明 |
|------|------|
| **mongos** | 路由节点，客户端连接入口 |
| **Shard** | 数据分片，每个分片是副本集 |
| **Config Server** | 配置服务器，存储元数据 |

---

## 七、MySQL vs MongoDB

| 维度 | MySQL | MongoDB |
|------|-------|---------|
| 数据模型 | 表/行/列 | 集合/文档/字段 |
| Schema | 固定 | 灵活（动态Schema） |
| 事务 | ACID完整支持 | 4.0+支持多文档事务 |
| 关联查询 | JOIN强大 | $lookup（较弱） |
| 扩展性 | 垂直为主，分库分表复杂 | 原生分片，水平扩展容易 |
| 查询语言 | SQL | MQL（JSON风格） |
| 聚合 | GROUP BY | 聚合管道（更强大） |
| 适用 | 传统业务、强一致 | 灵活Schema、高并发、大数据 |

---

## 关联文档

- [[数据库知识点完整整合大全_优化版]] — 数据库全景
- [[MySQL 知识点系统梳理_优化版]] — MySQL对比
- [[Redis 知识点系统梳理_优化版]] — NoSQL对比
- [[分库分表实战指南]] — 水平扩展
- [[高并发系统设计案例]] — 高并发应用

---

> 💡 **选型建议**：MongoDB适合Schema灵活、嵌套数据多、需要水平扩展的场景（用户画像、内容管理、IoT、日志）。不适合强事务和复杂关联查询。数据模型设计是关键：优先考虑嵌入（1对1/1对少），引用用于1对多/多对多。生产环境必须用副本集，大数据量用分片集群。



## 补充：概述

MongoDB 是最流行的**文档型 NoSQL 数据库**，以 BSON（Binary JSON）格式存储数据，具有灵活的文档模型、水平扩展能力和强大的查询功能。与传统关系型数据库相比，MongoDB 不需要预定义表结构，文档可以有不同的字段，非常适合敏捷开发、内容管理、物联网、实时分析等场景。

| 特性 | 说明 |
|------|------|
| **文档模型** | 以 BSON 文档存储，类似 JSON，支持嵌套结构 |
| **灵活 Schema** | 集合中的文档不需要相同的字段，支持动态 Schema |
| **丰富查询** | 支持 CRUD、聚合管道、全文搜索、地理空间查询 |
| **水平扩展** | 通过分片（Sharding）实现水平扩展，支持 PB 级数据 |
| **高可用** | 副本集（Replica Set）自动故障转移，数据冗余 |
| **索引支持** | 支持单字段、复合、多键、文本、地理空间、哈希索引 |
| **ACID 事务** | 4.0+ 支持多文档 ACID 事务 |

**适用场景**：内容管理系统、电商产品目录、用户 profile、物联网数据、实时分析、移动应用后端。
**不适用场景**：复杂多表 JOIN、强事务要求的金融系统、传统报表系统。

---

## 补充：底层原理

### BSON 存储格式

BSON（Binary JSON）是 MongoDB 的数据存储格式，在 JSON 的基础上增加了更多数据类型和高效的二进制编码：

| 数据类型 | BSON 类型 | 说明 |
|---------|----------|------|
| 字符串 | `string` | UTF-8 编码 |
| 整数 | `int32`/`int64` | 32/64 位整数 |
| 浮点数 | `double` | 64 位 IEEE 浮点 |
| 日期 | `date` | 64 位毫秒时间戳 |
| 二进制 | `binData` | 任意二进制数据 |
| 对象ID | `objectId` | 12 字节唯一 ID |
| 布尔 | `bool` | true/false |
| 数组 | `array` | 有序列表 |
| 嵌套文档 | `object` | 嵌套 BSON 对象 |
| 正则 | `regex` | 正则表达式 |
| Null | `null` | 空值 |

**ObjectId 结构**（12 字节）：
```text
| 4字节时间戳 | 5字节随机数 | 3字节自增计数器 |
```
这保证了在分布式环境下的全局唯一性，且包含创建时间信息。

### WiredTiger 存储引擎

MongoDB 3.2+ 默认使用 WiredTiger 存储引擎：

| 特性 | 实现 |
|------|------|
| **文档级并发** | MVCC（多版本并发控制），读写不阻塞 |
| **压缩** | Snappy（默认）/Zlib，压缩率 30-50% |
| **缓存** | 内存缓存，默认 50% RAM（减 1GB） |
| **预写日志** | WAL（Write Ahead Log），保证持久性 |
| **检查点** | 每 60 秒或 2GB 数据做一次检查点 |
| **B-tree** | 内部使用 B-tree 组织数据页 |

写入流程：
```text
客户端写入 → WiredTiger 缓存 → WAL 日志（持久化）→ 后台异步刷盘 → Checkpoint
```

### 副本集原理

副本集（Replica Set）是一组维护相同数据集的 MongoDB 进程：

```mermaid
graph LR
    A[Primary 主节点] -->|异步复制| B[Secondary 从节点1]
    A -->|异步复制| C[Secondary 从节点2]
    D[客户端] -->|读写| A
    B -.->|选举| A
    C -.->|选举| A
```

| 角色 | 职责 |
|------|------|
| **Primary** | 接收所有写操作，记录 oplog |
| **Secondary** | 从 Primary 复制 oplog 并应用，可提供读 |
| **Arbiter** | 不存数据，只参与选举（奇数节点用） |

**故障转移**：Primary 宕机后，剩余节点通过 Raft 协议选举新 Primary，通常 10-30 秒完成。

### 分片原理

分片（Sharding）将数据分布到多台机器上，实现水平扩展：

| 组件 | 职责 |
|------|------|
| **Shard** | 存储数据的 MongoDB 实例（通常是副本集） |
| **mongos** | 查询路由，对客户端透明 |
| **Config Server** | 存储元数据（分片键、chunk 分布） |

**分片键选择原则**：高基数、均匀分布、查询友好。常见错误：使用低基数字段（如性别）导致数据倾斜，使用单调递增字段（如时间戳）导致写热点。

---

## 补充：常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 查询慢 | 缺少索引或索引未命中 | `explain("executionStats")` 分析，创建合适索引 |
| 内存不足 | 工作集超过物理内存 | 增加内存、优化索引、使用分片 |
| 连接数满 | 应用未正确关闭连接 | 检查连接池配置，`db.serverStatus().connections` |
| 复制延迟 | 从节点性能不足或网络慢 | 优化从节点硬件，检查网络，使用 `rs.printSecondaryReplicationInfo()` |
| 分片数据倾斜 | 分片键选择不当 | 重新选择分片键，使用 `refineCollectionShardKey` |
| 锁等待 | 长事务或大文档更新 | 优化事务大小，使用 `db.currentOp()` 查看慢操作 |
| 磁盘空间不足 | 数据增长或未释放删除空间 | 扩容、`compact` 命令、归档历史数据 |
| Oplog 太小 | 从节点停机时间超过 oplog 窗口 | 增大 oplog 大小（`replSetResizeOplog`） |

### 慢查询排查流程

```javascript
// 1. 开启慢查询日志（超过 100ms）
db.setProfilingLevel(1, { slowms: 100 })

// 2. 查看慢查询
db.system.profile.find().sort({ ts: -1 }).limit(10).pretty()

// 3. 分析具体查询
db.collection.find({ status: "active" }).explain("executionStats")

// 4. 查看当前正在执行的操作
db.currentOp({ "active": true, "secs_running": { $gt: 5 } })

// 5. 杀掉慢查询
db.killOp(opid)
```

---

## 补充：进阶与最佳实践

### 1. 数据建模原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **嵌入优先** | 一对一/一对少关系用嵌入 | 用户文档中嵌入地址列表 |
| **引用次之** | 一对多/多对多用引用 | 文章引用评论（评论量大） |
| **避免无界数组** | 数组不要无限增长 | 评论单独集合，用文章ID关联 |
| **预聚合** | 频繁计算的结果预存 | 文章文档中存 `commentCount` |
| **查询驱动建模** | 根据查询模式设计 Schema | 先确定查询，再设计文档结构 |

### 2. 索引最佳实践

```javascript
// 复合索引遵循 ESR 原则：Equality(等值) → Sort(排序) → Range(范围)
db.orders.createIndex({ status: 1, createdAt: -1, total: 1 })
// status 是等值查询，createdAt 是排序，total 是范围查询

// 部分索引：只索引满足条件的文档，节省空间
db.users.createIndex(
  { email: 1 },
  { partialFilterExpression: { email: { $exists: true } } }
)

// 稀疏索引：只索引包含字段的文档
db.users.createIndex({ mobile: 1 }, { sparse: true })

// TTL 索引：自动过期删除（适合日志、会话）
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })

// 文本索引：全文搜索
db.articles.createIndex({ title: "text", content: "text" })
```

### 3. 聚合管道常用模式

```javascript
// 分组统计：按状态统计订单数和总金额
db.orders.aggregate([
  { $match: { createdAt: { $gte: new Date("2026-01-01") } } },
  { $group: {
      _id: "$status",
      count: { $sum: 1 },
      totalAmount: { $sum: "$total" }
  }},
  { $sort: { totalAmount: -1 } }
])

// 关联查询（$lookup 替代 JOIN）
db.orders.aggregate([
  { $match: { userId: ObjectId("xxx") } },
  { $lookup: {
      from: "users",
      localField: "userId",
      foreignField: "_id",
      as: "user"
  }},
  { $unwind: "$user" }
])

// 窗口函数：计算移动平均
db.sales.aggregate([
  { $sort: { date: 1 } },
  { $setWindowFields: {
      partitionBy: "$product",
      sortBy: { date: 1 },
      output: {
          avg7day: { $avg: "$amount", window: { documents: [-6, 0] } }
      }
  }}
])
```

### 4. 性能优化检查清单

- [ ] 所有高频查询都有合适的索引（`explain` 验证）
- [ ] 复合索引遵循 ESR 原则
- [ ] 查询避免 `$ne`、`$not`、`$exists`（难以用索引）
- [ ] 分页使用 `_id` 范围查询而非 `skip`（大偏移量慢）
- [ ] 文档大小控制在 1MB 以内（BSON 上限）
- [ ] 数组不无限增长（超过几百条考虑引用）
- [ ] 定期运行 `compact` 回收空间
- [ ] 监控连接数、内存、磁盘 IO、复制延迟
- [ ] 重要操作使用 `writeConcern: "majority"` 保证数据安全
