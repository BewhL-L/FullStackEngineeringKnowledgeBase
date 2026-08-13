---
title: GraphRAG 知识图谱增强检索
category: Python全栈
subcategory: AI应用开发
tags: [#Python全栈/AI应用, #AI结合/RAG, #难度/高级, #类型/实战]
difficulty: 高级
pre: [[RAG文本分块策略与实践]], [[Python-向量数据库客户端]]
related: [[Agent记忆机制设计与实现]], [[Python-AI应用可观测性]]
update: 2026-08-13
status: 完善
---

# GraphRAG 知识图谱增强检索

## 1. 核心概述

传统向量 RAG 只能做"语义相似度"检索，无法回答需要跨文档关联、多跳推理的问题。GraphRAG 通过从文档中抽取实体和关系构建知识图谱，将向量检索与图遍历结合，支持多跳推理、全局摘要和关联查询，显著提升复杂问题的回答质量。

**解决的场景问题**：
- 用户问"对比 A 和 B 的异同"，传统 RAG 只能分别检索
- 需要总结整个知识库的全局信息
- 文档之间存在隐含关系，纯向量检索发现不了
- 多跳问题（"A 的创始人之前在哪家公司？"）
- 需要可追溯的知识来源

## 2. 底层原理/核心逻辑

### GraphRAG vs 传统 RAG

```
传统 RAG：
Query → Embedding → 向量相似度 Top-K → 拼接上下文 → LLM 回答

GraphRAG：
Query → 实体识别 → 图谱检索（多跳遍历）+ 向量检索 → 融合排序 → LLM 回答
```

### 知识图谱构建流程

```
原始文档 → 文本分块 → 实体抽取 → 关系抽取 → 实体消歧
→ 构建图谱 → 社区检测 → 社区摘要
```

### 检索策略

| 策略 | 适用场景 | 实现方式 |
|------|----------|----------|
| 局部检索 | 具体实体相关问题 | 查询实体 → 遍历邻居 → 取关联文档 |
| 全局检索 | 总结性、概览性问题 | 查询社区摘要 → 聚合多个社区 |
| 混合检索 | 通用场景 | 向量检索 + 图谱检索 + RRF 融合 |
| 多跳推理 | 复杂关联问题 | 沿图谱边遍历 N 跳 |

## 3. 实操示例

### 实体与关系抽取

```python
from typing import List
from pydantic import BaseModel, Field

class Entity(BaseModel):
    name: str = Field(description="实体名称")
    type: str = Field(description="实体类型：人物/组织/产品/概念/地点/技术")
    description: str = Field(description="实体的一句话描述")

class Relation(BaseModel):
    source: str = Field(description="源实体名称")
    target: str = Field(description="目标实体名称")
    type: str = Field(description="关系类型")
    description: str = Field(description="关系的详细描述")

class ExtractionResult(BaseModel):
    entities: List[Entity]
    relations: List[Relation]

EXTRACTION_PROMPT = """你是一个知识图谱构建专家。请从以下文本中抽取实体和关系。
规则：
1. 实体要具体，不要抽取太泛的概念
2. 关系要明确，源和目标必须是已抽取的实体
3. 只抽取文本中明确提到的信息，不要推测

文本：
{text}

请以 JSON 格式输出。"""

def extract_entities_and_relations(text: str, llm_client, chunk_id: str) -> ExtractionResult:
    prompt = EXTRACTION_PROMPT.format(text=text)
    response = llm_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    result = ExtractionResult.model_validate_json(response.choices[0].message.content)
    for entity in result.entities:
        entity.source_chunks = [chunk_id]
    for relation in result.relations:
        relation.source_chunks = [chunk_id]
    return result
```

### 图存储（NetworkX）

```python
import networkx as nx
import json
from typing import List, Dict, Optional

class KnowledgeGraph:
    """知识图谱存储与查询"""

    def __init__(self):
        self.graph = nx.Graph()
        self.entity_index = {}

    def add_entity(self, entity: Entity):
        name = entity.name.strip()
        if name in self.entity_index:
            node_id = self.entity_index[name]
            existing = self.graph.nodes[node_id].get("source_chunks", [])
            self.graph.nodes[node_id]["source_chunks"] = list(set(existing + entity.source_chunks))
        else:
            node_id = f"entity_{len(self.entity_index)}"
            self.entity_index[name] = node_id
            self.graph.add_node(node_id, **entity.model_dump())

    def add_relation(self, relation: Relation):
        source_id = self.entity_index.get(relation.source.strip())
        target_id = self.entity_index.get(relation.target.strip())
        if not source_id or not target_id:
            return
        if self.graph.has_edge(source_id, target_id):
            existing = self.graph.edges[source_id, target_id]
            existing["source_chunks"] = list(set(existing.get("source_chunks", []) + relation.source_chunks))
        else:
            self.graph.add_edge(source_id, target_id, type=relation.type,
                              description=relation.description, weight=0.8,
                              source_chunks=relation.source_chunks)

    def get_neighbors(self, entity_name: str, hops: int = 1) -> List[Dict]:
        node_id = self.entity_index.get(entity_name.strip())
        if not node_id:
            return []
        visited = {node_id}
        current_level = [node_id]
        result = []
        for hop in range(hops):
            next_level = []
            for node in current_level:
                for neighbor in self.graph.neighbors(node):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_level.append(neighbor)
                        result.append({"entity": self.graph.nodes[neighbor],
                                      "relation": self.graph.edges[node, neighbor],
                                      "hop": hop + 1})
            current_level = next_level
        return result

    def get_related_chunks(self, entity_name: str, hops: int = 1) -> List[str]:
        neighbors = self.get_neighbors(entity_name, hops)
        chunks = set()
        node_id = self.entity_index.get(entity_name.strip())
        if node_id:
            chunks.update(self.graph.nodes[node_id].get("source_chunks", []))
        for item in neighbors:
            chunks.update(item["entity"].get("source_chunks", []))
            chunks.update(item["relation"].get("source_chunks", []))
        return list(chunks)

    def save(self, path: str):
        data = {"nodes": dict(self.graph.nodes(data=True)),
                "edges": [(u, v, d) for u, v, d in self.graph.edges(data=True)],
                "entity_index": self.entity_index}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def stats(self) -> Dict:
        return {"entities": self.graph.number_of_nodes(),
                "relations": self.graph.number_of_edges()}
```

### 社区检测与摘要

```python
from community import community_louvain

class CommunityDetector:
    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def detect_communities(self, resolution: float = 1.0) -> Dict[str, List[str]]:
        partition = community_louvain.best_partition(
            self.graph.graph, resolution=resolution, weight="weight")
        communities = {}
        for node_id, comm_id in partition.items():
            key = f"community_{comm_id}"
            communities.setdefault(key, []).append(node_id)
            self.graph.graph.nodes[node_id]["community_id"] = key
        return communities

    def generate_summaries(self, communities: Dict, llm_client) -> Dict[str, str]:
        summaries = {}
        for comm_id, node_ids in communities.items():
            if len(node_ids) < 2:
                continue
            entities_info = []
            for node_id in node_ids[:20]:
                node = self.graph.graph.nodes[node_id]
                entities_info.append(f"- {node.get('name', node_id)}：{node.get('description', '')}")
            prompt = f"请为以下知识图谱社区生成 200 字以内摘要：\n{chr(10).join(entities_info)}\n摘要："
            response = llm_client.chat.completions.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0)
            summaries[comm_id] = response.choices[0].message.content.strip()
        return summaries
```

### GraphRAG 检索器

```python
class GraphRAGRetriever:
    """GraphRAG 检索器：融合图谱检索和向量检索"""

    def __init__(self, graph, vector_store, embedding_model, llm_client, community_summaries=None):
        self.graph = graph
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.llm = llm_client
        self.community_summaries = community_summaries or {}

    def retrieve(self, query: str, top_k: int = 5, mode: str = "hybrid") -> Dict:
        if mode == "local":
            return self._local_search(query, top_k)
        elif mode == "global":
            return self._global_search(query, top_k)
        return self._hybrid_search(query, top_k)

    def _extract_query_entities(self, query: str) -> List[str]:
        prompt = f"从以下问题中提取 1-3 个关键实体，每行一个：\n{query}\n实体："
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0)
        return [l.strip() for l in response.choices[0].message.content.strip().split("\n") if l.strip()]

    def _local_search(self, query: str, top_k: int) -> Dict:
        query_entities = self._extract_query_entities(query)
        graph_chunks = set()
        graph_context = []
        for entity_name in query_entities:
            neighbors = self.graph.get_neighbors(entity_name, hops=2)
            chunks = self.graph.get_related_chunks(entity_name, hops=2)
            graph_chunks.update(chunks)
            node_id = self.graph.entity_index.get(entity_name.strip())
            if node_id:
                graph_context.append(f"实体：{self.graph.graph.nodes[node_id].get('name')}")
            for item in neighbors[:10]:
                graph_context.append(f"[{item['hop']}跳] {item['entity'].get('name')}")
        vector_results = self.vector_store.similarity_search(query, k=top_k)
        vector_chunks = [r.metadata.get("chunk_id") for r in vector_results]
        all_chunks = list(graph_chunks) + [c for c in vector_chunks if c not in graph_chunks]
        return {"chunks": all_chunks[:top_k * 2], "graph_context": graph_context, "mode": "local"}

    def _global_search(self, query: str, top_k: int) -> Dict:
        if not self.community_summaries:
            return self._local_search(query, top_k)
        query_emb = self.embedding_model.embed(query)
        community_scores = []
        for comm_id, summary in self.community_summaries.items():
            summary_emb = self.embedding_model.embed(summary)
            score = self._cosine_similarity(query_emb, summary_emb)
            community_scores.append((comm_id, score, summary))
        community_scores.sort(key=lambda x: x[1], reverse=True)
        top_communities = community_scores[:top_k]
        all_chunks = set()
        context_parts = []
        for comm_id, score, summary in top_communities:
            context_parts.append(f"[社区摘要 {score:.2f}] {summary}")
            for node_id, attrs in self.graph.graph.nodes(data=True):
                if attrs.get("community_id") == comm_id:
                    all_chunks.update(attrs.get("source_chunks", []))
        return {"chunks": list(all_chunks)[:top_k * 3], "graph_context": context_parts, "mode": "global"}

    def _hybrid_search(self, query: str, top_k: int) -> Dict:
        local = self._local_search(query, top_k)
        global_r = self._global_search(query, top_k)
        return {"chunks": list(set(local["chunks"] + global_r["chunks"]))[:top_k * 3],
                "graph_context": local["graph_context"] + global_r["graph_context"], "mode": "hybrid"}

    @staticmethod
    def _cosine_similarity(a, b):
        import numpy as np
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 实体抽取不准确 | LLM 幻觉或信息不足 | 用更强模型，人工校验关键实体 |
| 图谱构建太慢 | 每个 chunk 都调 LLM | 批处理，用 mini 模型，缓存 |
| 实体消歧困难 | "苹果"可能是公司或水果 | 抽取时要求输出类型，按类型消歧 |
| 多跳遍历引入噪声 | 2 跳以上邻居可能不相关 | 限制跳数，按关系权重过滤 |
| 全局检索效果差 | 社区摘要质量不高 | 调整 Louvain resolution |

### 踩坑点

1. **不要对太短的文本做抽取**：少于 50 字的 chunk 抽不出有意义实体
2. **关系抽取要限制类型**：预定义关系类型表
3. **图谱更新是增量的**：新文档加入时不要重建整个图谱
4. **存储要考虑规模**：大规模用 Neo4j / NebulaGraph 替代 NetworkX

### 优化方案

- **增量更新**：新文档只抽取新实体，合并到已有图谱
- **关系权重学习**：根据共现频率调整边权重
- **多层级社区**：不同层级摘要适配不同粒度问题
- **图数据库**：大规模用 Neo4j

## 5. 延伸拓展方向

- [[RAG文本分块策略与实践]]：GraphRAG 的基础
- [[高级RAG-Hybrid检索与重排序]]：混合检索
- [[Agent记忆机制设计与实现]]：长期记忆用图谱存储
- [[Python-向量数据库客户端]]：向量检索部分
- [[AI应用可观测性与Langfuse集成]]：GraphRAG 检索追踪

## 6. 参考资料

- [Microsoft GraphRAG](https://github.com/microsoft/graphrag)
- [GraphRAG: From Local to Global](https://arxiv.org/abs/2404.16130)
- [Neo4j + LLM GraphRAG](https://neo4j.com/developer-blog/genai-app-how-to-build-graphrag/)

#待完善
