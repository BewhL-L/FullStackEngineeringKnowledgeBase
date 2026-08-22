---
title: Elasticsearch 知识点系统梳理
tags: [数据库, Elasticsearch, 搜索引擎, 全文检索, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# Elasticsearch 知识点系统梳理（优化版）

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。


> **文档说明**：系统梳理 Elasticsearch 核心知识，涵盖架构、索引、搜索、聚合、性能优化、集群等内容。

---

## 1. 概述

Elasticsearch（ES）是基于 Lucene 的分布式搜索引擎，提供近实时的全文检索、结构化搜索和数据分析能力。

**核心特性**：
- 分布式、高可用、可水平扩展
- RESTful API，JSON 格式交互
- 近实时（NRT）搜索，写入后 1 秒可搜索
- 支持全文检索、结构化查询、聚合分析
- 与 Kibana（可视化）、Logstash（数据采集）组成 ELK 栈

---

## 2. 核心概念

| 概念 | 说明 | 类比关系型数据库 |
|------|------|------------------|
| Cluster | 集群，多个节点组成 | - |
| Node | 节点，单个 ES 实例 | - |
| Index | 索引，同类文档集合 | Database |
| Type | 类型（7.x 后废弃，统一 _doc） | Table |
| Document | 文档，JSON 格式数据 | Row |
| Field | 字段，文档中的属性 | Column |
| Shard | 分片，索引的水平拆分 | 分表 |
| Replica | 副本，分片的备份 | 从库 |

> 🔍 **知识点深度解析**
>
> **作用**：理解核心概念是使用 ES 的基础。
>
> **原理**：ES 集群由多个节点组成，索引被分成多个主分片（primary shard）分布在不同节点，每个主分片可有多个副本分片（replica shard）。主分片负责读写，副本分片负责读和故障转移。主分片数量在创建索引时确定，不可修改；副本分片数量可动态调整。文档通过 `_id` 的哈希值取模决定落在哪个主分片：`shard = hash(_id) % number_of_primary_shards`。
>
> **用法要点**：① 7.x 后一个索引只能有一个 type（_doc）；② 主分片数创建后不可改，需提前规划（一般单分片 20-50GB）；③ 副本数至少 1（高可用），搜索密集可增加副本提升读性能；④ 面试常考：分片原理、主副分片区别、文档路由算法。

---

## 3. 倒排索引

**ES 的核心数据结构，实现快速全文检索。**

```
文档1: "Java 编程思想"
文档2: "Java 并发编程"

倒排索引：
Java  → [文档1, 文档2]
编程  → [文档1, 文档2]
思想  → [文档1]
并发  → [文档2]
```

**组成**：
- **Term Dictionary**：词项字典，存储所有词
- **Posting List**：倒排列表，存储包含该词的文档 ID
- **Term Index**：词项索引（FST），加速词项查找

> 🔍 **知识点深度解析**
>
> **作用**：倒排索引是搜索引擎的核心，实现毫秒级全文检索。
>
> **原理**：正排索引是文档→词的映射（查文档有哪些词），倒排索引是词→文档的映射（查哪些文档包含这个词）。文档写入时经过分析（Analyzer）：分词 → 小写化 → 停用词过滤 → 词干提取，生成词项（term），然后更新倒排索引。搜索时对查询词做同样的分析，在倒排索引中查找对应的文档列表，合并结果并按相关性打分（BM25 算法）排序。
>
> **用法要点**：① text 类型字段会分词建立倒排索引，keyword 类型不分词（精确匹配）；② 分词器选择：中文用 IK 分词器（ik_max_word 细粒度、ik_smart 粗粒度）；③ 面试常考：倒排索引原理、正排 vs 倒排、分词器、BM25 打分。

---

## 4. 索引操作

### 4.1 创建索引

```json
PUT /products
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "ik_max": { "type": "ik_max_word" }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": { "type": "text", "analyzer": "ik_max" },
      "price": { "type": "double" },
      "category": { "type": "keyword" },
      "createTime": { "type": "date", "format": "yyyy-MM-dd HH:mm:ss" }
    }
  }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：创建索引是写入数据的前提，需在创建时指定分片数、副本数和字段映射（mappings），决定数据如何存储与分词。
>
> **原理**：PUT /index 通过 settings 配置 number_of_shards（主分片数，创建后不可改）和 number_of_replicas（副本数，可动态改）；mappings 定义每个字段的 type（text/keyword/date/double 等）及 analyzer。text 字段分词建倒排索引，keyword 不分词用于精确匹配与聚合。分词器（如 IK）决定中文如何切词入库。
>
> **用法要点**：① 主分片数创建后不可改，需按数据量提前规划（单分片 20-50GB）；② 全文检索字段用 text + 分词器，精确匹配/聚合字段用 keyword；③ 日期字段指定 format 避免解析错误；④ 中文检索配置 IK 分词器（ik_max_word 细粒度）；⑤ 索引名用小写，避免下划线开头（系统保留前缀）。

### 4.2 文档 CRUD

```json
// 新增（指定 ID）
PUT /products/_doc/1
{ "title": "Java 编程思想", "price": 99.0, "category": "图书" }

// 新增（自动生成 ID）
POST /products/_doc
{ "title": "并发编程实战" }

// 查询
GET /products/_doc/1

// 更新（部分更新）
POST /products/_update/1
{ "doc": { "price": 89.0 } }

// 删除
DELETE /products/_doc/1
```

> 🔍 **知识点深度解析**
>
> **作用**：文档是 ES 最小数据单元（JSON），CRUD 是日常开发核心，掌握增删改查 API 是入门基础。
>
> **原理**：文档通过 _id 唯一标识，写入时按 hash(_id) % 主分片数路由到对应主分片。PUT /_doc/{id} 指定 ID 新增（存在则全量替换）；POST /_doc 自动生成 ID。部分更新 POST /_update/{id} 用 doc 字段增量合并（内部先取旧文档再合并）。删除是标记删除（.del），由段合并真正回收。
>
> **用法要点**：① 批量写用 Bulk API（每批 5-15MB），性能远高于单条；② 更新尽量用 _update 部分更新，避免先查再全量覆盖；③ 大批量导入用自动生成 ID，可避免版本检查开销；④ 删除单文档用 DELETE /_doc/{id}；⑤ _id 建议业务可控（如订单号），便于定向查询与去重。

### 4.3 批量操作（Bulk）

```json
POST /_bulk
{ "index": { "_index": "products", "_id": "1" } }
{ "title": "Java 编程思想", "price": 99 }
{ "delete": { "_index": "products", "_id": "2" } }
{ "update": { "_index": "products", "_id": "3" } }
{ "doc": { "price": 79 } }
```

---

> 🔍 **知识点深度解析**
>
> **作用**：Bulk 在一次 HTTP 请求中执行多条增删改，大幅减少网络往返，是海量数据导入与同步的首选方式。
>
> **原理**：Bulk 请求体采用 action/metadata 与 source 交替的 NDJSON 行格式，每行一个 JSON。节点收到后按操作路由到对应分片并行执行，将 N 次网络往返压缩为 1 次，吞吐可提升一个数量级。失败行返回在响应 items 中（status 非 2xx），不中断整体。
>
> **用法要点**：① 批量大小控制在 5-15MB（过大会 OOM、超时）；② 用 BulkProcessor（Java 客户端）按阈值/时间自动 flush；③ 监控 items 中失败 status 并做好重试；④ 大批量导入临时关闭副本（replicas=0）与 refresh 提升速度；⑤ 同批操作尽量落在相近分片以减少开销。

## 5. 查询 DSL

### 5.1 全文查询

```json
GET /products/_search
{
  "query": {
    "match": {
      "title": {
        "query": "Java 编程",
        "operator": "and"
      }
    }
  }
}

// 短语匹配（词序一致）
{ "match_phrase": { "title": "Java 编程" } }

// 多字段匹配
{ "multi_match": { "query": "Java", "fields": ["title", "description"] } }
```

> 🔍 **知识点深度解析**
>
> **作用**：全文查询（match / match_phrase / multi_match）对 text 字段做分词检索，是搜索引擎最常用查询类型，支持相关性打分。
>
> **原理**：match 先对查询字符串分词，再用分词后的 term 在倒排索引查找，默认 OR 关系（任一 term 命中即匹配），operator:and 要求全部命中。match_phrase 要求 term 顺序与位置连续（短语匹配）。multi_match 在多个字段间检索，可用 best_fields/most_fields/cross_fields 控制打分。相关性由 BM25 算法打分（基于词频、逆文档频率、字段长度）。
>
> **用法要点**：① 全文检索用 match，短语/顺序敏感用 match_phrase；② 多字段检索用 multi_match（如 title+description）；③ 需全部词命中设 operator:"and"；④ 中文务必配置 IK 分词器，否则按单字切分效果差；⑤ 结合 boost 提升重要字段权重。

### 5.2 精确查询

```json
// term 精确匹配（不分词）
{ "term": { "category": "图书" } }

// terms 多值匹配
{ "terms": { "category": ["图书", "电子"] } }

// range 范围
{ "range": { "price": { "gte": 50, "lte": 100 } } }

// exists 存在
{ "exists": { "field": "description" } }
```

> 🔍 **知识点深度解析**
>
> **作用**：精确查询（term / terms / range / exists）不对查询词分词，用于 keyword、数值、日期、布尔等字段的精准匹配与范围过滤。
>
> **原理**：term 直接拿查询值去匹配已存储的确切 term（不做 analysis），因此对 keyword 有效；对 text 字段因已分词通常匹配不到。terms 相当于多个 term 的 OR。range 基于字段值区间（gt/gte/lt/lte）。exists 判断字段是否存在（过滤 null/缺失字段）。这类查询放 filter 上下文时不计算相关性、结果可缓存。
>
> **用法要点**：① 精确值（状态、分类、枚举）用 term/terms，字段用 keyword；② 区间用 range（价格、时间）；③ 过滤缺失字段用 exists；④ 精确查询尽量放 filter（不打分、可缓存、性能更好）；⑤ 不要在 text 字段用 term（分词导致失败），改用 .keyword 子字段。

### 5.3 组合查询（bool）

```json
{
  "bool": {
    "must":     [{ "match": { "title": "Java" } }],      // 必须满足，影响打分
    "filter":   [{ "term": { "category": "图书" } }],     // 必须满足，不打分，可缓存
    "should":   [{ "match": { "description": "编程" } }], // 至少满足一个（有 must 时不强制）
    "must_not": [{ "range": { "price": { "gt": 200 } } }] // 必须不满足
  }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：Query DSL 是 ES 的查询语言，功能强大。
>
> **原理**：`match` 查询会对查询词分词，然后在倒排索引中查找，默认 OR 关系（任一匹配），设 operator: and 则全部匹配。`term` 精确匹配，不分析查询词，适合 keyword/数字/日期。`bool` 组合查询：must 算分，filter 不算分且结果可缓存（性能更好），should 增加相关性，must_not 排除。查询分为 Query Context（算分）和 Filter Context（不算分，可缓存），能用 filter 就用 filter。
>
> **用法要点**：① 全文搜索用 match，精确值用 term/terms；② 过滤条件放 filter（不打分、可缓存、性能好）；③ 深度分页用 search_after 或 scroll，不要用 from+size（深度分页性能差）；④ 高亮用 highlight；⑤ 面试常考：match vs term、bool 查询、filter vs query、深度分页。

---

## 6. 聚合分析

### 6.1 桶聚合（Bucket）

```json
// 按分类分组，统计每组数量
{
  "aggs": {
    "by_category": {
      "terms": { "field": "category", "size": 10 }
    }
  }
}

// 价格区间
{
  "aggs": {
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          { "to": 50 },
          { "from": 50, "to": 100 },
          { "from": 100 }
        ]
      }
    }
  }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：桶聚合（terms / range / date_histogram 等）按字段或区间将文档分组，类似 SQL 的 GROUP BY，是数据分析的基础。
>
> **原理**：terms 按字段每个唯一值分桶（近似结果，靠 shard_size 控制精度）；range 按自定义区间分桶（如价格 0-50、50-100）；date_histogram 按时间粒度（天/周/月）分桶，常用于时序分析。每个桶独立统计文档数，可嵌套子聚合进一步下钻。分桶结果由各数据节点局部计算后由协调节点汇总。
>
> **用法要点**：① 分组统计用 terms（如按 category 分组算数量）；② 数值/时间区间用 range/date_histogram；③ 高基数字段 terms 聚合设 size 限制返回桶数，shard_size 提升精度；④ 对 text 字段聚合需开启 fielddata（耗内存，建议用 keyword）；⑤ 桶聚合常配合指标聚合（avg/sum）做多维分析。

### 6.2 指标聚合（Metric）

```json
{
  "aggs": {
    "avg_price": { "avg": { "field": "price" } },
    "max_price": { "max": { "field": "price" } },
    "stats_price": { "stats": { "field": "price" } } // 同时返回 min/max/avg/sum/count
  }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：指标聚合（avg / max / min / sum / stats / cardinality）对数值字段做统计计算，类似 SQL 聚合函数，用于求均值、极值、总数等。
>
> **原理**：avg/max/min/sum 在分桶或全局范围内计算单值指标；stats 一次返回 min/max/avg/sum/count 五项；extended_stats 额外返回方差、标准差。cardinality 用 HyperLogLog++ 近似计算唯一值数量（UV 等），有可控误差。这些聚合在 Leaf 节点本地计算后由协调节点合并。
>
> **用法要点**：① 单指标用 avg/sum/max，多指标用 stats 减少请求；② 去重计数用 cardinality（近似，误差约 1-2%，省内存）；③ 指标聚合通常嵌套在桶聚合内（按组求均值）；④ 大数量级 stats 计算有开销，必要时下采样；⑤ 百分比用 percentile 聚合（如 P95 响应时间）。

### 6.3 嵌套聚合

```json
// 按分类分组，每组统计平均价格
{
  "aggs": {
    "by_category": {
      "terms": { "field": "category" },
      "aggs": {
        "avg_price": { "avg": { "field": "price" } }
      }
    }
  }
}
```

---

> 🔍 **知识点深度解析**
>
> **作用**：嵌套聚合（在 aggs 内再放 aggs）实现多层级下钻分析，如“按分类分组后再算每组平均价 / Top N”，类似 SQL 分组内再分组。
>
> **原理**：聚合可无限嵌套，外层桶聚合的每个桶内可再执行子聚合（桶或指标）。执行时从外层向内层逐层计算：先分桶，再在每桶文档子集上计算子聚合。支持 pipeline 聚合（derivative、cumulative_sum、bucket_selector）基于兄弟聚合结果二次计算。深度嵌套会增加内存与计算开销。
>
> **用法要点**：① 在 aggs 的某桶内再写 aggs 即可嵌套；② 常用模式：terms 分桶 + avg/sum 指标；③ 取每组 Top N 用 top_hits 或 terms 的 size；④ 过滤特定桶用 bucket_selector（脚本筛选）；⑤ 控制嵌套深度与分桶数，避免内存爆炸（indices.breaker 限制）。

## 7. 性能优化

### 7.1 写入优化

- 批量写入（Bulk API），每批 5-15MB
- 增加 refresh_interval（如 30s），减少段合并
- 写入时设置 `number_of_replicas: 0`，写完再恢复
- 使用自动生成 ID（避免版本检查）
- 禁用 _source（不需要原始文档时）

> 🔍 **知识点深度解析**
>
> **作用**：写入优化提升 ES 批量导入与高并发写入的吞吐与稳定性，是日志、埋点等写密集场景的关键。
>
> **原理**：写入先进入内存 buffer 与 translog，refresh_interval（默认 1s）到点生成可搜索的 segment；增大 refresh 间隔可减少段生成频率与合并压力。副本在写入时也要同步，临时置 0 可省去这部分开销（完成后恢复）。自动生成 ID 避免版本冲突检查。禁用 _source 可省存储但丧失部分重建能力。
>
> **用法要点**：① 大批量导入临时设 refresh_interval:-1、number_of_replicas:0，导入完再恢复；② 用 Bulk 批量写入（5-15MB/批）；③ 能用自动 ID 就用，减少版本检查；④ translog 设 async 可再提速（牺牲少量持久性）；⑤ 避免单文档过大，合理设计字段；⑥ 写入后手动 refresh 或等待间隔使数据可查。

### 7.2 查询优化

- 用 filter 代替 query（不打分、可缓存）
- 避免深度分页（from+size），用 search_after
- 只查询需要的字段（_source 过滤）
- 合理设置分片数（单分片 20-50GB）
- 预热（warmup）常用查询

> 🔍 **知识点深度解析**
>
> **作用**：查询优化降低延迟、提升吞吐，保证高并发检索与聚合的响应速度。
>
> **原理**：filter 上下文只判断匹配与否、不打分且结果可缓存，比 query 上下文更快；深度分页 from+size 在分布式下需各分片取前 N 再协调节点排序，越深越慢（from=100000 需每分片取 100000+size）。search_after 用上一页最后一个文档的排序值作为游标，避免全局排序。_source 过滤减少网络与序列化开销。
>
> **用法要点**：① 过滤条件一律放 filter（缓存+不打分）；② 深分页用 search_after 或 scroll，禁止大 from；③ 只取所需字段（_source 过滤）；④ 合理分片（单分片 20-50GB），过少过多都影响性能；⑤ 对常用查询用 ILM/warmup 预热；⑥ 用 profile:true 分析慢查询瓶颈。

### 7.3 索引设计

- 时间序列索引用 ILM（索引生命周期管理），按天/周滚动
- 冷热分离：热数据 SSD，冷数据普通磁盘
- 别名（alias）实现索引切换无感知

> 🔍 **知识点深度解析**
>
> **作用**：ES 性能优化是生产环境的关键，写入和查询都有优化空间。
>
> **原理**：ES 写入是先写内存 buffer 和 translog（事务日志），每隔 refresh_interval（默认 1s）将 buffer 中的数据生成新的 segment（段），此时数据可搜索。segment 是不可变的，删除是标记删除（.del 文件），更新是删除+新增。后台会进行 segment merge（段合并），将小 segment 合并成大 segment，真正删除已标记数据。translog 用于故障恢复，每 5s 或每次请求 fsync 到磁盘。
>
> **用法要点**：① 大批量导入时临时设 refresh_interval=-1 和 replicas=0；② translog durability 设 async 提升写入性能（有数据丢失风险）；③ 查询用 keyword 字段做聚合（text 字段聚合需 fielddata，耗内存）；④ 面试常考：写入流程、segment 不可变、refresh vs flush、translog 作用。

---

## 8. 集群与高可用

### 8.1 节点类型

| 节点类型 | 作用 |
|----------|------|
| Master | 管理集群状态、元数据、分片分配 |
| Data | 存储数据、执行查询和写入 |
| Coordinating | 路由请求、合并结果（每个节点默认都是） |
| Ingest | 数据预处理（pipeline） |
| Machine Learning | 机器学习（需 License） |

> 🔍 **知识点深度解析**
>
> **作用**：ES 集群由多种角色节点组成，合理划分角色可提升性能、稳定性与运维便利。
>
> **原理**：Master 节点负责集群元数据与分片分配（不处理数据读写，选主靠 Zen2/raft）；Data 节点存储数据并执行读写与聚合；Coordinating（协调节点）接收请求、分发到数据节点、合并结果——每个节点默认都扮演协调角色；Ingest 节点执行 pipeline 预处理；ML 节点跑机器学习任务（需 License）。生产环境常将 Master 与 Data 分离，避免互相影响。
>
> **用法要点**：① 专用 Master 节点（3 个，不存数据）保证选主稳定；② Data 节点按数据量横向扩展；③ 高吞吐网关可设专用 coordinating 节点（node.master/data/ingest 全 false）；④ 用 node.roles 显式指定角色（7.x+）；⑤ 避免 Master 节点兼做重负载 Data，防止脑裂与性能抖动。

### 8.2 脑裂问题

- 配置 `discovery.zen.minimum_master_nodes: (master_nodes / 2) + 1`
- 7.x 后自动处理，需配置 `cluster.initial_master_nodes`

> 🔍 **知识点深度解析**
>
> **作用**：脑裂指集群因网络分区出现多个 Master，导致数据不一致，是分布式系统的高危故障，需从配置与架构上规避。
>
> **原理**：当半数以上 Master 候选节点失联，其余节点可能各自选主形成多个“小集群”同时对外服务，恢复后数据冲突。旧版用 discovery.zen.minimum_master_nodes = 候选数/2+1 保证只有多数派能选主；7.x 后默认使用 Zen2（基于 raft 的类一致性），通过 cluster.initial_master_nodes 引导初始主节点，并依赖节点间协调，基本消除脑裂。
>
> **用法要点**：① 7.x 之前务必正确设置 minimum_master_nodes（N/2+1）；② 7.x 用 Zen2，配置 cluster.initial_master_nodes 完成首次引导；③ Master 候选节点数为奇数（3/5）；④ 网络分区用奇数+多数派机制防范；⑤ 部署跨可用区时控制单区节点不过半；⑥ 监控 master 节点健康与选举日志。

### 8.3 分片分配

- 主分片和副本分片不在同一节点
- 节点故障时自动在其他节点提升副本为主分片

---

> 🔍 **知识点深度解析**
>
> **作用**：分片分配决定主/副本分片落在哪些节点，直接影响高可用、容量与读写性能。
>
> **原理**：索引创建时按 number_of_shards 切分主分片，路由算法 hash(_id)%主分片数决定文档归属。副本分片不会与主分片同节点（保证节点宕机不丢数据）。某节点失效时，Master 将该节点主分片对应的副本提升为主分片，并重新分配副本，实现自动故障转移。分配策略受 shard allocation awareness（机架/区域感知）与过滤规则影响。
>
> **用法要点**：① 主副分片不在同一节点（默认保证）；② 节点故障后 ES 自动提升副本为主并再均衡；③ 用 shard allocation awareness 让分片跨机架/可用区分布；④ 控制单节点分片总数（避免过多小分片拖垮元数据）；⑤ 冷热架构用 node.attr 标注 + ILM 实现数据分层；⑥ 扩容增加节点后 ES 自动 rebalance。

## 9. 面试高频考点

1. **倒排索引**：原理、正排 vs 倒排、分词器
2. **分片机制**：主副分片、文档路由、分片数规划
3. **写入流程**：buffer → segment → translog → refresh/flush
4. **查询 DSL**：match vs term、bool 查询、filter vs query
5. **深度分页**：问题、search_after、scroll
6. **性能优化**：写入优化、查询优化、索引设计
7. **segment**：不可变、段合并、删除机制
8. **集群**：节点类型、脑裂、高可用
9. **ES vs 数据库**：适用场景、不能替代数据库的原因
10. **IK 分词器**：ik_max_word vs ik_smart

---

## 📝 精简总结

- ES 是分布式搜索引擎，核心是倒排索引
- 索引分主分片和副本分片，主分片数创建后不可改
- 写入：内存 buffer → refresh 生成 segment → translog 保证持久化
- 查询：match 全文、term 精确、bool 组合、filter 不打分可缓存
- 聚合：桶聚合（分组）+ 指标聚合（统计），支持嵌套
- 优化：批量写入、filter 查询、避免深分页、合理分片
- 适用场景：全文检索、日志分析、监控告警、电商搜索

---

[[03-数据库与缓存/MOC-数据库与缓存|← 返回数据库 MOC]] | [[Home|🏠 返回首页]]
