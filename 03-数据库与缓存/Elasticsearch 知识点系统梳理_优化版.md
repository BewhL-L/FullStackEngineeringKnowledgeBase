---
title: Elasticsearch 知识点系统梳理
tags: [数据库, Elasticsearch, 搜索引擎, 全文检索, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# Elasticsearch 知识点系统梳理（优化版）

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

## 7. 性能优化

### 7.1 写入优化

- 批量写入（Bulk API），每批 5-15MB
- 增加 refresh_interval（如 30s），减少段合并
- 写入时设置 `number_of_replicas: 0`，写完再恢复
- 使用自动生成 ID（避免版本检查）
- 禁用 _source（不需要原始文档时）

### 7.2 查询优化

- 用 filter 代替 query（不打分、可缓存）
- 避免深度分页（from+size），用 search_after
- 只查询需要的字段（_source 过滤）
- 合理设置分片数（单分片 20-50GB）
- 预热（warmup）常用查询

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

### 8.2 脑裂问题

- 配置 `discovery.zen.minimum_master_nodes: (master_nodes / 2) + 1`
- 7.x 后自动处理，需配置 `cluster.initial_master_nodes`

### 8.3 分片分配

- 主分片和副本分片不在同一节点
- 节点故障时自动在其他节点提升副本为主分片

---

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
