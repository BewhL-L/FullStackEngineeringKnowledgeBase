---
title: 数据库与缓存 MOC
tags: [MOC, 数据库, MySQL, Redis, 缓存]
category: 数据库与缓存
created: 2026-08-12
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: []
aliases: [MOC-数据库与缓存]
updated: 2026-09-07

---

# 💾 数据库与缓存 MOC

> 关系型数据库 MySQL 与内存缓存 Redis，是后端数据存储与性能优化的核心组件。

---

## 📚 核心文档

### 关系型数据库
- [[MySQL 知识点系统梳理_优化版|MySQL 知识点系统梳理]] — InnoDB 引擎、B+树索引、事务、MVCC、锁机制、性能优化
- [[PostgreSQL核心知识点系统梳理|PostgreSQL 核心知识点]] — 架构、MVCC、索引类型、JSONB、分区表、性能调优
- [[SQL速查表|SQL 速查表]] — 查询/过滤/聚合/连接/窗口函数/数据操作高频语法
- [[数据库设计范式与ER建模|数据库设计范式与ER建模]] — 三大范式、ER图、反范式、表设计规范、命名规范、实战案例
- [[TiDB NewSQL数据库入门|TiDB NewSQL 数据库入门]] — 分布式NewSQL、MySQL兼容、HTAP、架构原理、迁移方案

### 内存缓存
- [[Redis 知识点系统梳理_优化版|Redis 知识点系统梳理]] — 五大数据结构、持久化、高可用、缓存三大问题、分布式锁
- [[Redis高级数据结构实战|Redis 高级数据结构实战]] — Stream/Bitmap/HyperLogLog/GEO/布隆过滤器原理与实战
- [[缓存穿透击穿雪崩解决方案|缓存穿透击穿雪崩解决方案]] — 三大问题原理、布隆过滤器、互斥锁、热点key、实战方案
- [[多级缓存架构设计|多级缓存架构设计]] — CDN/Nginx/本地/Redis/DB五级缓存、一致性保障、热点key处理

### 搜索引擎
- [[Elasticsearch 知识点系统梳理_优化版|Elasticsearch 知识点系统梳理]] — 倒排索引、查询DSL、聚合分析、集群高可用、性能优化
- [[Elasticsearch深度实战|Elasticsearch 深度实战]] — 索引设计、DSL查询、聚合分析、性能调优、集群运维、MySQL同步

### NoSQL 文档数据库
- [[MongoDB 知识点系统梳理_优化版|MongoDB 知识点系统梳理]] — BSON文档、索引、聚合管道、副本集、分片集群
- [[MongoDB实战指南|MongoDB 实战指南]] — CRUD、聚合管道、索引、Spring Boot集成、高可用、与MySQL对比
- [[Neo4j图数据库实战|Neo4j 图数据库实战]] — 图数据模型、Cypher查询、知识图谱、推荐系统、GDS算法、Spring Boot集成
- [[Cassandra列式数据库实战|Cassandra 列式数据库实战]] — 无主P2P架构、高写入、时间序列、多数据中心、CQL、一致性级别

### OLAP与数据仓库
- [[ClickHouse OLAP引擎实战|ClickHouse OLAP 引擎实战]] — 列式存储、MergeTree表引擎、物化视图、Kafka实时导入、性能调优、与Doris对比

### 时序与向量数据库
- [[时序数据库入门与实战|时序数据库入门与实战]] — InfluxDB/Prometheus/TDengine对比、数据模型、降采样、保留策略
- [[向量数据库选型与实战|向量数据库选型与实战]] — ANN索引(HNSW/IVF)、Milvus/Pinecone/Qdrant对比、RAG应用、Python实战

### 数据同步与迁移
- [[CDC数据同步实战|CDC 数据同步实战]] — Canal/Debezium架构、binlog监听、MySQL→ES实时同步、最佳实践
- [[数据库迁移工具实战|数据库迁移工具实战]] — Flyway/Liquibase配置、版本管理、回滚、命名规范、最佳实践

### 数据库实战与排查
- [[分库分表实战指南|分库分表实战指南]] — 垂直/水平拆分、分片策略、中间件选型、跨分片查询、扩容方案
- [[MySQL问题排查手册|MySQL 问题排查手册]] — 慢SQL/死锁/连接数满/主从延迟/CPU高排查流程与解决方案
- [[数据库备份恢复实战|数据库备份恢复实战]] — MySQL/Redis/MongoDB备份、3-2-1原则、恢复演练、容灾方案

### 数据库安全
- [[数据库安全与审计实战|数据库安全与审计实战]] — 权限管理、数据加密、敏感脱敏、SQL注入防护、审计日志、等保合规

### 数据治理
- [[数据治理与数据质量|数据治理与数据质量]] — 质量六维度、元数据管理、数据血缘、数据标准、主数据管理、分类分级、落地路线

---

## 🔗 知识关联

```text
MySQL（持久化存储）
   ↑ 读写
   ↓ 缓存
Redis（内存加速）
```

- [[MySQL 知识点系统梳理_优化版|MySQL]] 是数据持久化的核心，[[Redis 知识点系统梳理_优化版|Redis]] 作为缓存层减轻数据库压力
- 缓存一致性：Cache Aside 模式（先更新 DB 再删缓存），详见 [[Redis 知识点系统梳理_优化版|Redis]] 文档
- [[MyBatis-Plus 知识点系统梳理_优化版|MyBatis-Plus]] 是 MySQL 的 ORM 框架
- Redis 可用于分布式锁，与 [[并发编程 知识点系统梳理_优化版|并发编程]] 中的分布式场景相关

---

## 📖 学习顺序

1. **数据库设计**：[[数据库设计范式与ER建模|数据库设计范式与ER建模]] — 范式、ER图、表设计
2. **MySQL 基础**：[[MySQL 知识点系统梳理_优化版|MySQL 知识点梳理]] — 索引、事务、锁
3. **SQL 语法**：[[SQL速查表|SQL 速查表]] — 高频语法速查
4. **PostgreSQL**：[[PostgreSQL核心知识点系统梳理|PostgreSQL]] — 进阶关系型数据库
5. **NewSQL**：[[TiDB NewSQL数据库入门|TiDB]] — 分布式数据库、HTAP
6. **Redis 基础**：[[Redis 知识点系统梳理_优化版|Redis 知识点梳理]] — 数据结构、持久化
7. **Redis 高级**：[[Redis高级数据结构实战|Redis 高级数据结构]] — Stream/Bitmap/HLL/GEO
8. **缓存进阶**：[[缓存穿透击穿雪崩解决方案|缓存三大问题]] → [[多级缓存架构设计|多级缓存架构]]
9. **搜索引擎**：[[Elasticsearch 知识点系统梳理_优化版|Elasticsearch]] → [[Elasticsearch深度实战|ES 深度实战]]
10. **NoSQL**：[[MongoDB 知识点系统梳理_优化版|MongoDB]] → [[MongoDB实战指南|MongoDB 实战]] → [[Neo4j图数据库实战|Neo4j 图数据库]] → [[Cassandra列式数据库实战|Cassandra 列式数据库]]
11. **OLAP分析**：[[ClickHouse OLAP引擎实战|ClickHouse]] — 列式分析引擎
12. **数据同步**：[[CDC数据同步实战|CDC 数据同步]] — binlog实时同步
13. **数据库迁移**：[[数据库迁移工具实战|数据库迁移工具]] — Flyway/Liquibase
14. **时序与向量**：[[时序数据库入门与实战|时序数据库]] → [[向量数据库选型与实战|向量数据库]]
15. **高级实战**：[[分库分表实战指南|分库分表]] → [[MySQL问题排查手册|问题排查]] → [[数据库备份恢复实战|备份恢复]]
16. **安全与治理**：[[数据库安全与审计实战|数据库安全]] → [[数据治理与数据质量|数据治理]]

---

## 🚀 新增：知识域旗舰全集

- [[数据库知识点完整整合大全_优化版|数据库知识点完整整合大全]] — MySQL / Redis / MongoDB / PostgreSQL / 向量库 / 分库分表 / 主从复制 / 备份恢复 的统一全集（参照 Java 大全格式）

## 🧩 六维补充文档

- [[数据库设计模板与排查手册_优化版|数据库设计模板与排查手册]] — Schema 模板 / 迁移脚本 / 慢查询巡检 / 死锁 / 缓存雪崩·击穿·穿透 / 连接池耗尽（维度二 + 三）

## 🏷️ 相关标签

`#数据库` `#MySQL` `#Redis` `#Elasticsearch` `#MongoDB` `#PostgreSQL` `#TiDB` `#Neo4j` `#Cassandra` `#ClickHouse` `#缓存` `#索引` `#事务` `#分布式锁` `#分库分表` `#CDC` `#向量数据库` `#时序数据库` `#Flyway` `#数据备份` `#ER建模` `#数据库设计` `#数据库安全` `#数据治理` `#数据质量`

---

[[Home|🏠 返回首页]]
---

## 📝 新增文档（2026-09）

- [[数据库分库分表策略|数据库分库分表策略]]
- [[分布式缓存一致性|分布式缓存一致性]]

