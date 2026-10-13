---
title: Elasticsearch 全文检索引擎
tags: [后端, Elasticsearch, 全文检索, 原子笔记]
category: 后端开发
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["Elasticsearch 知识点系统梳理_优化版", "Elasticsearch深度实战"]
aliases: [Elasticsearch-全文检索引擎]
---

# Elasticsearch 全文检索引擎

> **文档说明**：系统讲解 Elasticsearch 的核心架构、倒排索引原理、文档 CRUD、查询 DSL（全文查询/Term 查询/复合查询/聚合分析）、分词器与映射、集群高可用机制（分片/副本/节点角色）、性能调优与常见问题排查，含丰富的 REST API 示例和生产级配置。
>
> **适用人群**：后端开发工程师、全栈开发者、搜索工程师、需要使用 Elasticsearch 的架构师
>
> **前置知识**：[[Elasticsearch 知识点系统梳理_优化版]]、[[Elasticsearch深度实战]]

---

## 一、概述

**Elasticsearch（ES）** 是一个基于 Apache Lucene 的分布式、RESTful 风格的搜索和分析引擎，由 Elastic 公司开发。它能够快速存储、搜索和分析海量数据，广泛应用于全文检索、日志分析、指标监控、安全分析等场景。

### 1. 核心特性

| 特性 | 说明 |
|------|------|
| **分布式** | 自动分片，水平扩展，支持 PB 级数据 |
| **高可用** | 多副本机制，节点故障自动切换 |
| **近实时** | 文档写入后 1 秒内可搜索（近实时 NRT） |
| **RESTful API** | 基于 HTTP/JSON 的 API，简单易用 |
| **全文检索** | 基于倒排索引，支持复杂查询和相关性评分 |
| **聚合分析** | 支持指标聚合、桶聚合、管道聚合等复杂分析 |
| **多租户** | Index 隔离，支持多租户场景 |
| **生态丰富** | Kibana（可视化）、Logstash（数据采集）、Beats（轻量采集） |

### 2. 核心概念

| 概念 | 说明 | 类比 |
|------|------|------|
| **Cluster** | 集群，一个或多个节点组成 | 数据库集群 |
| **Node** | 节点，一个 ES 实例 | 数据库实例 |
| **Index** | 索引，文档的逻辑集合 | 数据库表 |
| **Document** | 文档，最小数据单元，JSON 格式 | 数据库行 |
| **Field** | 字段，文档中的属性 | 数据库列 |
| **Mapping** | 映射，字段类型定义 | 数据库 Schema |
| **Shard** | 分片，Index 的物理分片，分布在不同节点 | 分库分表 |
| **Replica** | 副本，分片的备份，保证高可用和读扩展 | 主从复制 |
| **Analyzer** | 分词器，文本分析为词条 | - |
| **Inverted Index** | 倒排索引，词条到文档的映射 | - |

### 3. 集群架构

```mermaid
graph TB
    subgraph ES Cluster
        subgraph Node 1 (Master + Data)
            P0[Shard P0<br/>Primary]
            R1[Shard R1<br/>Replica]
        end
        subgraph Node 2 (Data)
            P1[Shard P1<br/>Primary]
            R2[Shard R2<br/>Replica]
        end
        subgraph Node 3 (Data)
            P2[Shard P2<br/>Primary]
            R0[Shard R0<br/>Replica]
        end
    end

    C[客户端] -->|REST API| Node1
    C -->|REST API| Node2
    C -->|REST API| Node3
```

**节点角色**：
| 角色 | 配置 | 职责 |
|------|------|------|
| **Master** | `node.master: true` | 集群管理、元数据管理、分片分配 |
| **Data** | `node.data: true` | 存储数据、执行查询和聚合 |
| **Ingest** | `node.ingest: true` | 数据预处理（管道） |
| **Coordinating** | 所有节点默认 | 请求路由、结果合并 |
| **ML** | `node.ml: true` | 机器学习（X-Pack） |

**生产环境推荐**：
- 3 个专用 Master 节点（避免脑裂）
- 多个 Data 节点（根据数据量）
- 独立 Coordinating 节点（高查询负载）
- 独立 Ingest 节点（高写入负载）

---

## 二、倒排索引原理

### 1. 倒排索引结构

倒排索引是 Elasticsearch 的核心数据结构，将文档中的词条映射到包含该词条的文档列表。

```
文档1："Java 并发编程"
文档2："Java 虚拟机"
文档3："并发编程实战"

正排索引（文档 → 词条）：
文档1 → [Java, 并发, 编程]
文档2 → [Java, 虚拟机]
文档3 → [并发, 编程, 实战]

倒排索引（词条 → 文档）：
Java   → [文档1, 文档2]
并发   → [文档1, 文档3]
编程   → [文档1, 文档3]
虚拟机 → [文档2]
实战   → [文档3]
```

**倒排索引组成**：
| 组成 | 说明 |
|------|------|
| **Term Dictionary** | 词条字典，存储所有词条 |
| **Posting List** | 倒排表，存储包含该词条的文档 ID 列表 |
| **Term Index** | 词条索引（FST），加速词条查找 |
| **Doc Values** | 列式存储，用于排序和聚合 |
| **Stored Fields** | 存储原始文档内容 |

### 2. 分词过程

文本经过分词器（Analyzer）处理后生成词条：

```
原文："The Quick Brown Foxes Jump Over Lazy Dogs"
    ↓
Character Filter（字符过滤）：→ "The Quick Brown Foxes Jump Over Lazy Dogs"
    ↓
Tokenizer（分词器）：→ [The, Quick, Brown, Foxes, Jump, Over, Lazy, Dogs]
    ↓
Token Filter（词条过滤）：
  - Lowercase：→ [the, quick, brown, foxes, jump, over, lazy, dogs]
  - Stop Words：→ [quick, brown, foxes, jump, lazy, dogs]（移除 the, over）
  - Stemmer：→ [quick, brown, fox, jump, lazy, dog]（词干提取）
    ↓
最终词条：[quick, brown, fox, jump, lazy, dog]
```

### 3. 内置分词器

| 分词器 | 说明 | 适用场景 |
|--------|------|---------|
| **standard** | 默认分词器，按 Unicode 文本分割，小写化 | 英文通用 |
| **simple** | 按非字母分割，小写化 | 简单英文 |
| **whitespace** | 按空格分割，不小写化 | 已预处理文本 |
| **keyword** | 不分词，整个文本作为一个词条 | 精确匹配（ID、枚举） |
| **language** | 语言分词器（english/french/german 等） | 特定语言 |
| **ik_max_word** | IK 分词器，最细粒度切分 | 中文（需安装 IK 插件） |
| **ik_smart** | IK 分词器，智能切分 | 中文（需安装 IK 插件） |
| **pinyin** | 拼音分词器 | 中文拼音搜索（需安装插件） |

```json
// 创建 Index 时指定分词器
PUT /my-index
{
  "settings": {
    "analysis": {
      "analyzer": {
        "my_analyzer": {
          "type": "custom",
          "tokenizer": "ik_max_word",
          "filter": ["lowercase", "my_stop"]
        }
      },
      "filter": {
        "my_stop": {
          "type": "stop",
          "stopwords": ["的", "了", "是", "在"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "ik_max_word",
        "search_analyzer": "ik_smart"
      },
      "content": {
        "type": "text",
        "analyzer": "my_analyzer"
      }
    }
  }
}

// 测试分词器
POST /_analyze
{
  "analyzer": "ik_max_word",
  "text": "Elasticsearch 全文检索引擎"
}
```

---

## 三、文档 CRUD

### 1. 创建文档

```json
// 指定 ID 创建（PUT）
PUT /my-index/_doc/1
{
  "title": "Elasticsearch 入门",
  "content": "Elasticsearch 是一个分布式搜索和分析引擎",
  "author": "张三",
  "tags": ["Elasticsearch", "搜索", "大数据"],
  "views": 1000,
  "created_at": "2026-01-01T00:00:00Z"
}

// 自动生成 ID 创建（POST）
POST /my-index/_doc
{
  "title": "Elasticsearch 进阶",
  "content": "深入理解 Elasticsearch 内部原理",
  "author": "李四",
  "tags": ["Elasticsearch", "进阶"],
  "views": 500,
  "created_at": "2026-01-02T00:00:00Z"
}

// 批量创建（Bulk API）
POST /_bulk
{"index": {"_index": "my-index", "_id": "1"}}
{"title": "文档1", "content": "内容1"}
{"index": {"_index": "my-index", "_id": "2"}}
{"title": "文档2", "content": "内容2"}
{"create": {"_index": "my-index", "_id": "3"}}
{"title": "文档3", "content": "内容3"}
```

### 2. 查询文档

```json
// 根据 ID 查询
GET /my-index/_doc/1

// 查询所有文档
GET /my-index/_search
{
  "query": {
    "match_all": {}
  }
}

// 分页查询
GET /my-index/_search
{
  "query": {"match_all": {}},
  "from": 0,
  "size": 10,
  "sort": [{"created_at": "desc"}]
}
```

### 3. 更新文档

```json
// 全量更新（覆盖）
PUT /my-index/_doc/1
{
  "title": "Elasticsearch 入门（更新版）",
  "content": "更新后的内容",
  "author": "张三",
  "views": 1500
}

// 部分更新（Update API）
POST /my-index/_update/1
{
  "doc": {
    "views": 2000
  }
}

// 脚本更新
POST /my-index/_update/1
{
  "script": {
    "source": "ctx._source.views += params.count",
    "lang": "painless",
    "params": {
      "count": 100
    }
  }
}

// Upsert（不存在则创建，存在则更新）
POST /my-index/_update/1
{
  "doc": {"views": 100},
  "doc_as_upsert": true
}
```

### 4. 删除文档

```json
// 根据 ID 删除
DELETE /my-index/_doc/1

// 根据查询条件删除（Delete By Query）
POST /my-index/_delete_by_query
{
  "query": {
    "match": {
      "author": "张三"
    }
  }
}

// 删除整个 Index
DELETE /my-index
```

---

## 四、查询 DSL

### 1. 查询类型概览

| 类别 | 查询类型 | 说明 |
|------|---------|------|
| **全文查询** | match、match_phrase、multi_match、query_string | 对文本进行分词后查询 |
| **Term 查询** | term、terms、range、exists、prefix、wildcard、regexp | 精确匹配，不分词 |
| **复合查询** | bool、constant_score、function_score、dis_max、boosting | 组合多个查询 |
| **连接查询** | nested、has_child、has_parent | 嵌套/父子文档查询 |
| **地理位置** | geo_distance、geo_bounding_box、geo_polygon | 地理位置查询 |
| **特殊查询** | match_all、match_none、ids、percolate | 特殊用途 |

### 2. 全文查询

```json
// match 查询：分词后匹配（OR 关系）
GET /my-index/_search
{
  "query": {
    "match": {
      "title": {
        "query": "Elasticsearch 入门",
        "operator": "or",        // or（默认）/ and
        "minimum_should_match": "75%"  // 至少匹配 75% 的词条
      }
    }
  }
}

// match_phrase 查询：短语匹配（词条顺序和位置必须匹配）
GET /my-index/_search
{
  "query": {
    "match_phrase": {
      "content": {
        "query": "分布式搜索",
        "slop": 2  // 允许词条间间隔 2 个位置
      }
    }
  }
}

// multi_match 查询：多字段匹配
GET /my-index/_search
{
  "query": {
    "multi_match": {
      "query": "Elasticsearch",
      "fields": ["title^3", "content", "tags^2"],  // ^ 表示权重
      "type": "best_fields"  // best_fields/most_fields/cross_fields/phrase
    }
  }
}

// query_string 查询：支持 Lucene 查询语法
GET /my-index/_search
{
  "query": {
    "query_string": {
      "query": "title:(Elasticsearch AND 入门) OR content:分布式",
      "default_field": "content"
    }
  }
}
```

### 3. Term 查询

```json
// term 查询：精确匹配单个值（不分词）
GET /my-index/_search
{
  "query": {
    "term": {
      "author.keyword": "张三"  // keyword 字段精确匹配
    }
  }
}

// terms 查询：匹配多个值
GET /my-index/_search
{
  "query": {
    "terms": {
      "tags.keyword": ["Elasticsearch", "搜索"]
    }
  }
}

// range 查询：范围查询
GET /my-index/_search
{
  "query": {
    "range": {
      "views": {
        "gte": 100,
        "lte": 1000,
        "format": "yyyy-MM-dd"  // 日期格式
      }
    }
  }
}

// exists 查询：字段存在
GET /my-index/_search
{
  "query": {
    "exists": {
      "field": "author"
    }
  }
}

// prefix 查询：前缀匹配
GET /my-index/_search
{
  "query": {
    "prefix": {
      "title.keyword": "Elastic"
    }
  }
}

// wildcard 查询：通配符匹配（* 任意字符，? 单个字符）
GET /my-index/_search
{
  "query": {
    "wildcard": {
      "title.keyword": "Elastic*"
    }
  }
}
```

### 4. 复合查询（Bool Query）

Bool Query 是最常用的复合查询，通过逻辑组合多个查询条件：

| 子句 | 逻辑 | 说明 |
|------|------|------|
| **must** | AND | 必须匹配，参与评分 |
| **should** | OR | 至少匹配 N 个，参与评分 |
| **must_not** | NOT | 必须不匹配，不参与评分（过滤上下文） |
| **filter** | AND | 必须匹配，不参与评分（过滤上下文，可缓存） |

```json
GET /my-index/_search
{
  "query": {
    "bool": {
      "must": [
        {"match": {"title": "Elasticsearch"}}
      ],
      "should": [
        {"match": {"content": "分布式"}},
        {"match": {"tags": "搜索"}}
      ],
      "must_not": [
        {"term": {"author.keyword": "黑名单作者"}}
      ],
      "filter": [
        {"range": {"views": {"gte": 100}}},
        {"term": {"status": "published"}}
      ],
      "minimum_should_match": 1  // should 至少匹配 1 个
    }
  },
  "from": 0,
  "size": 20,
  "sort": [
    {"views": "desc"},
    {"_score": "desc"}
  ],
  "_source": ["title", "author", "views", "created_at"]  // 只返回指定字段
}
```

### 5. 聚合分析

| 聚合类型 | 说明 | 示例 |
|---------|------|------|
| **指标聚合** | 计算指标值 | avg、sum、min、max、stats、extended_stats、value_count、cardinality |
| **桶聚合** | 文档分桶 | terms、range、date_range、histogram、date_histogram、filter、nested |
| **管道聚合** | 对聚合结果再聚合 | avg_bucket、sum_bucket、max_bucket、min_bucket、derivative、moving_avg |

```json
// 指标聚合 + 桶聚合
GET /my-index/_search
{
  "size": 0,  // 不返回文档，只返回聚合结果
  "aggs": {
    "by_author": {
      "terms": {
        "field": "author.keyword",
        "size": 10,
        "order": {"avg_views": "desc"}
      },
      "aggs": {
        "avg_views": {
          "avg": {"field": "views"}
        },
        "total_views": {
          "sum": {"field": "views"}
        },
        "views_stats": {
          "stats": {"field": "views"}
        }
      }
    },
    "views_histogram": {
      "histogram": {
        "field": "views",
        "interval": 500,
        "min_doc_count": 0
      }
    },
    "by_date": {
      "date_histogram": {
        "field": "created_at",
        "calendar_interval": "month",
        "format": "yyyy-MM"
      }
    }
  }
}
```

---

## 五、映射（Mapping）

### 1. 字段类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **text** | 全文文本，分词，可搜索 | 文章内容、标题 |
| **keyword** | 精确值，不分词，用于聚合/排序/过滤 | ID、标签、状态 |
| **long/integer/short/byte** | 整数 | 年龄、数量 |
| **float/double/half_float/scaled_float** | 浮点数 | 价格、评分 |
| **boolean** | 布尔值 | 是否发布 |
| **date** | 日期 | 创建时间 |
| **binary** | 二进制（Base64） | 文件内容 |
| **object** | 对象（嵌套 JSON） | 用户信息 |
| **nested** | 嵌套对象（独立索引，保持数组内对象关系） | 评论列表、订单商品 |
| **geo_point** | 地理坐标 | 经纬度 |
| **geo_shape** | 地理形状 | 多边形、线路 |
| **ip** | IP 地址 | 192.168.1.1 |
| **completion** | 自动补全 | 搜索建议 |
| **join** | 父子关系 | 父文档-子文档 |
| **rank_feature/rank_features** | 排名特征 | 相关性评分增强 |

### 2. 映射定义

```json
PUT /my-index
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "ik_max_word",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      },
      "content": {
        "type": "text",
        "analyzer": "ik_max_word"
      },
      "author": {
        "type": "keyword"
      },
      "tags": {
        "type": "keyword"
      },
      "views": {
        "type": "integer"
      },
      "price": {
        "type": "scaled_float",
        "scaling_factor": 100
      },
      "status": {
        "type": "keyword"
      },
      "created_at": {
        "type": "date",
        "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
      },
      "location": {
        "type": "geo_point"
      },
      "user": {
        "type": "object",
        "properties": {
          "id": {"type": "long"},
          "name": {"type": "keyword"}
        }
      },
      "comments": {
        "type": "nested",
        "properties": {
          "user": {"type": "keyword"},
          "content": {"type": "text"},
          "created_at": {"type": "date"}
        }
      }
    }
  }
}
```

### 3. 动态映射

Elasticsearch 默认开启动态映射，写入文档时自动推断字段类型：

| JSON 类型 | 自动映射为 |
|-----------|-----------|
| string | text + keyword（多字段） |
| integer/long | long |
| float/double | float |
| boolean | boolean |
| date（可识别格式） | date |
| object | object |

```json
// 关闭动态映射
PUT /my-index
{
  "mappings": {
    "dynamic": "strict",  // true（默认）/ false（忽略新字段）/ strict（新字段报错）
    "properties": {...}
  }
}

// 动态模板（自定义新字段映射规则）
PUT /my-index
{
  "mappings": {
    "dynamic_templates": [
      {
        "strings_as_keyword": {
          "match_mapping_type": "string",
          "mapping": {
            "type": "keyword"
          }
        }
      },
      {
        "longs_as_integer": {
          "match_mapping_type": "long",
          "mapping": {
            "type": "integer"
          }
        }
      }
    ]
  }
}
```

---

## 六、集群高可用

### 1. 分片与副本

| 概念 | 说明 |
|------|------|
| **Primary Shard** | 主分片，文档写入先到主分片 |
| **Replica Shard** | 副本分片，主分片的备份，可提供读服务 |
| **分片数** | `number_of_shards`，创建 Index 时指定，不可修改（除非 reindex） |
| **副本数** | `number_of_replicas`，可动态修改 |

```json
// 创建 Index 时指定分片和副本
PUT /my-index
{
  "settings": {
    "number_of_shards": 5,      // 5 个主分片
    "number_of_replicas": 1     // 每个主分片 1 个副本
  }
}

// 动态修改副本数
PUT /my-index/_settings
{
  "number_of_replicas": 2
}
```

**分片数选择建议**：
- 每个分片大小建议 10GB-50GB
- 分片数过多：增加元数据开销，查询变慢
- 分片数过少：无法水平扩展，单分片过大
- 公式：预计数据量 / 30GB ≈ 主分片数

### 2. 集群健康状态

| 状态 | 颜色 | 说明 |
|------|------|------|
| **Green** | 绿色 | 所有主分片和副本都正常分配 |
| **Yellow** | 黄色 | 所有主分片正常，但部分副本未分配（单节点集群默认 Yellow） |
| **Red** | 红色 | 部分主分片未分配，数据不完整 |

```bash
# 查看集群健康状态
curl -X GET "localhost:9200/_cluster/health?pretty"

# 查看集群状态
curl -X GET "localhost:9200/_cluster/state?pretty"

# 查看节点信息
curl -X GET "localhost:9200/_cat/nodes?v"

# 查看分片分配
curl -X GET "localhost:9200/_cat/shards?v"

# 查看 Index 健康状态
curl -X GET "localhost:9200/_cat/indices?v"
```

### 3. 脑裂与 Master 选举

**脑裂（Split Brain）**：网络分区导致集群出现多个 Master，数据不一致。

**避免脑裂**：
- `discovery.zen.minimum_master_nodes`（ES 6.x）：设置为 `(master_eligible_nodes / 2) + 1`
- ES 7.x+：自动管理，无需手动配置

**生产环境推荐**：3 个 Master 节点（奇数），保证多数派选举。

---

## 七、性能调优

### 1. 写入性能调优

| 优化项 | 建议 | 说明 |
|--------|------|------|
| **批量写入** | Bulk API，每批 5-15MB | 减少网络往返 |
| **刷新间隔** | `index.refresh_interval: 30s` 或 `-1` | 减少段合并，写入完成后恢复 |
| **副本数** | 写入时设为 0，完成后恢复 | 避免副本同步开销 |
| **事务日志** | `index.translog.durability: async` | 异步刷盘，提升性能（有丢失风险） |
| **分词器** | 避免复杂分词器 | 分词是写入瓶颈 |
| **磁盘** | SSD/NVMe | 随机写入性能 |
| **内存** | 堆外内存（页缓存） | ES 严重依赖文件系统缓存 |
| **并发** | 多线程/多进程写入 | 充分利用 CPU 和 IO |

```json
// 写入优化设置
PUT /my-index/_settings
{
  "index.refresh_interval": "-1",
  "index.number_of_replicas": 0,
  "index.translog.durability": "async",
  "index.translog.sync_interval": "30s"
}

// 写入完成后恢复
PUT /my-index/_settings
{
  "index.refresh_interval": "1s",
  "index.number_of_replicas": 1
}

// 强制刷新和段合并
POST /my-index/_refresh
POST /my-index/_forcemerge?max_num_segments=1
```

### 2. 查询性能调优

| 优化项 | 建议 | 说明 |
|--------|------|------|
| **过滤上下文** | 使用 filter 而非 must | 不计算评分，可缓存 |
| **避免深度分页** | 使用 search_after 或 scroll | from+size 深度分页性能差 |
| **字段裁剪** | `_source` 只返回需要的字段 | 减少网络和序列化开销 |
| **Doc Values** | 排序/聚合字段开启 doc_values | 列式存储，加速排序聚合 |
| **避免 wildcard/regexp** | 前缀过宽的通配符查询慢 | 使用 ngram 或 completion 替代 |
| **路由** | 使用自定义路由 | 查询只扫描相关分片 |
| **预热** | 预热查询和字段数据 | 减少冷查询延迟 |
| **缓存** | 开启查询缓存、分片请求缓存 | 重复查询加速 |

```json
// search_after 深度分页（替代 from+size）
GET /my-index/_search
{
  "size": 10,
  "query": {"match_all": {}},
  "sort": [
    {"created_at": "desc"},
    {"_id": "asc"}  // 必须包含唯一值字段
  ],
  "search_after": ["2026-01-01T00:00:00Z", "123"]  // 上一页最后一条的排序值
}
```

### 3. JVM 调优

| 参数 | 建议 | 说明 |
|------|------|------|
| **堆大小** | 不超过 31GB（避免指针压缩失效） | 留足够内存给页缓存 |
| **Xms = Xmx** | 初始堆 = 最大堆 | 避免堆动态扩展 |
| **GC** | G1 或 ZGC | 低延迟 |
| **元空间** | 256MB-512MB | 避免元空间 OOM |
| **直接内存** | 足够大 | ES 使用大量堆外内存 |

```bash
# jvm.options 示例
-Xms16g
-Xmx16g
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:MetaspaceSize=256m
-XX:MaxMetaspaceSize=512m
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/es/heapdump.hprof
```

---

## 八、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **集群 Red** | 主分片未分配 / 节点故障 / 磁盘满 | 检查节点状态、磁盘空间、分片分配日志 |
| **集群 Yellow** | 副本未分配（单节点） | 增加节点或接受 Yellow（单节点测试环境） |
| **写入慢** | refresh 太频繁 / 副本同步 / 磁盘 IO 瓶颈 | 调整 refresh_interval、批量写入、SSD |
| **查询慢** | 分片过多 / 深度分页 / 复杂查询 / 冷数据 | 优化查询、search_after、预热、增加节点 |
| **OOM** | 堆内存不足 / 聚合查询过大 / fielddata 占用 | 增大堆、限制聚合 size、使用 doc_values |
| **磁盘满** | 数据增长过快 / 保留策略不当 | 调整保留策略、增加磁盘、删除旧数据、ILM |
| **脑裂** | 网络分区 / Master 节点数不足 | 3 个 Master 节点、检查网络 |
| **段数过多** | refresh 频繁 / 写入量小但频繁 | 增大 refresh_interval、forcemerge |
| **Mapping 冲突** | 同名字段类型不一致 | 使用 index template、reindex |
| **分词不准确** | 分词器选择不当 / 自定义词库缺失 | 选择合适分词器、维护自定义词库 |
| **相关性差** | 评分算法不匹配 / 字段权重不当 | 调整 boost、function_score、BM25 参数 |
| **数据丢失** | 副本数为 0 / 节点故障 / 误删除 | 副本数 >= 1、快照备份、谨慎删除 |

### 常用排查命令

```bash
# 集群健康
curl -X GET "localhost:9200/_cluster/health?pretty"

# 未分配分片原因
curl -X GET "localhost:9200/_cluster/allocation/explain?pretty"

# 节点统计
curl -X GET "localhost:9200/_nodes/stats?pretty"

# 索引统计
curl -X GET "localhost:9200/my-index/_stats?pretty"

# 慢查询日志
# elasticsearch.yml 配置：
# index.search.slowlog.threshold.query.warn: 10s
# index.search.slowlog.threshold.query.info: 5s
# index.indexing.slowlog.threshold.index.warn: 10s

# 线程池状态
curl -X GET "localhost:9200/_cat/thread_pool?v"

# 挂起任务
curl -X GET "localhost:9200/_cluster/pending_tasks?pretty"

# 索引恢复状态
curl -X GET "localhost:9200/_recovery?pretty"

# 段信息
curl -X GET "localhost:9200/my-index/_segments?pretty"
```

---

## 九、关联笔记

### 搜索引擎
- [[Elasticsearch 知识点系统梳理_优化版]] · [[Elasticsearch深度实战]] · [[Elasticsearch-全文检索引擎]]

### 数据库
- [[MySQL 知识点系统梳理_优化版]] · [[Redis 知识点系统梳理_优化版]] · [[MongoDB 知识点系统梳理_优化版]]
- [[向量数据库选型与实战]] · [[Milvus-架构与部署]]

### 大数据
- [[Kafka-消息队列与消费模型]] · [[Flink实时计算入门]] · [[ClickHouse OLAP引擎实战]]

### 后端
- [[高并发系统设计案例]] · [[高可用架构设计]] · [[SpringBoot-自动装配原理]]

### 云原生
- [[Docker-核心原理与镜像优化]] · [[K8s-核心概念与架构]] · [[Prometheus监控体系]]

### AI 工程化
- [[RAG架构设计与流程]] · [[高级RAG-Hybrid检索与重排序]] · [[Embedding模型选型]]

### 导航
- [[MOC-后端开发]] · [[MOC-数据库与缓存]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[Elasticsearch 知识点系统梳理_优化版]] ES 基础 → 深入本文 Elasticsearch 架构与查询 → 实践 [[Elasticsearch深度实战]] 生产部署 → 研究 [[RAG架构设计与流程]] 向量+全文混合检索 → 学习 [[Kafka-消息队列与消费模型]] 数据管道 → 应用于 [[高并发系统设计案例]] 搜索场景。
