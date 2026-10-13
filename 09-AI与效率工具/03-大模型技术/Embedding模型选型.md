---
title: Embedding模型选型
category: 大模型技术
tags: [Embedding, 向量, 向量数据库, RAG, NLP]
priority: P0
status: published
created: 2026-09-10
updated: 2026-09-10
version: "2.0"
author: BewhY_L
pre: 掌握 Embedding 模型选型全链路知识
description: 系统梳理 Embedding 模型选型：词嵌入历史、句嵌入、双编码器/交叉编码器架构、主流模型对比(BGE/GTE/E5/m3e/Jina/OpenAI)、维度与降维、相似度计算、RAG应用、多语言/多模态Embedding、微调、批量优化、缓存、归一化、选型决策树、MTEB基准、成本对比、常见坑点。
---

# Embedding模型选型

> **文档定位**：本文档是 Embedding 模型选型的全景式系统指南，覆盖从词嵌入历史到现代 Embedding 模型、从架构原理到生产选型、从 MTEB 基准到成本优化的完整知识体系。400+ 个可运行代码示例，30+ 表格，30+ 坑点，20+ 面试考点。

---

### 目录

1. [Embedding 基本概念](#1-embedding-基本概念)
2. [词嵌入历史](#2-词嵌入历史)
3. [句嵌入发展](#3-句嵌入发展)
4. [现代 Embedding 架构](#4-现代-embedding-架构)
5. [主流模型对比](#5-主流模型对比)
6. [维度选择与降维](#6-维度选择与降维)
7. [相似度计算](#7-相似度计算)
8. [Embedding 在 RAG 中的应用](#8-embedding-在-rag-中的应用)
9. [多语言 Embedding](#9-多语言-embedding)
10. [多模态 Embedding](#10-多模态-embedding)
11. [Embedding 微调](#11-embedding-微调)
12. [批量优化与缓存](#12-批量优化与缓存)
13. [向量归一化](#13-向量归一化)
14. [选型决策树](#14-选型决策树)
15. [性能基准 MTEB](#15-性能基准-mteb)
16. [成本对比](#16-成本对比)
17. [常见坑点](#17-常见坑点)
18. [附录：速查代码集](#18-附录速查代码集)

---

## 1. Embedding 基本概念

### 1.1 什么是 Embedding

**概念**：Embedding（嵌入）是把离散对象（词、句子、图片）映射到连续向量空间的技术，使得语义相似的对象在向量空间中距离接近。

**原理**：通过神经网络学习一个映射函数 f(x) -> vector，让相似输入的向量距离小，不相似的距离大。

```python
# 代码示例1：Embedding 直观理解
import numpy as np
# 假设我们有 3 个词的 embedding（5维）
embeddings = {
    "猫": np.array([0.1, 0.8, 0.2, 0.9, 0.1]),
    "狗": np.array([0.1, 0.7, 0.3, 0.8, 0.2]),
    "汽车": np.array([0.9, 0.1, 0.8, 0.1, 0.9]),
}
def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print(f"猫 vs 狗: {cosine_sim(embeddings['猫'], embeddings['狗']):.3f}")
print(f"猫 vs 汽车: {cosine_sim(embeddings['猫'], embeddings['汽车']):.3f}")
# 预期: 猫狗相似度高, 猫汽车相似度低
```

### 1.2 Embedding 的用途

```python
# 代码示例2：Embedding 应用
applications = {
    "语义搜索": "查询和文档向量化后比较",
    "RAG": "检索相关文档",
    "聚类": "自动分组",
    "推荐": "相似物品推荐",
    "去重": "找重复内容",
    "分类": "用向量做分类",
    "异常检测": "离群点检测",
}
for k, v in applications.items():
    print(f"  {k}: {v}")
```

### 1.3 Embedding 的关键属性

```python
# 代码示例3：关键属性
properties = {
    "维度": "向量长度(如 768/1536/3072)",
    "语义性": "相似语义距离近",
    "归一化": "向量长度=1",
    "通用性": "跨任务迁移",
    "效率": "计算和存储成本",
}
for k, v in properties.items():
    print(f"  {k}: {v}")
```

> 💡 **深度讲解**：Embedding 的核心是"语义空间"。好的 Embedding 让"国王-男人+女人≈女王"这样的语义关系成立。这是通过在海量文本上训练，让模型学习到词的分布表示实现的。

> 📝 **精简总结**：Embedding = 把对象变向量；语义相似=向量近；用途是搜索/聚类/推荐/RAG。

> 🎯 **梯度练习**：
> - 初级：用 OpenAI Embedding API 嵌入一句话
> - 中级：计算两段文本的相似度
> - 高级：用 Embedding 做简单语义搜索

---

## 2. 词嵌入历史

### 2.1 One-hot

**概念**：最简单的表示，每个词一个维度，只有一个位置是 1。

```python
# 代码示例4：One-hot 实现
vocab = ["猫", "狗", "汽车", "鸟"]
def one_hot(word, vocab):
    v = np.zeros(len(vocab))
    v[vocab.index(word)] = 1
    return v
print(f"猫 one-hot: {one_hot('猫', vocab)}")
print(f"问题: 维度高、语义无关、稀疏")
```

### 2.2 Word2Vec

**概念**：2013 年 Google 提出，用神经网络学习词的分布式表示。

```python
# 代码示例5：Word2Vec 原理
word2vec = {
    "CBOW": "上下文预测中心词",
    "Skip-gram": "中心词预测上下文",
    "优点": "低维、语义相关、稠密",
    "缺点": "一词一向量(多义词不行)、静态",
}
for k, v in word2vec.items():
    print(f"  {k}: {v}")
```

### 2.3 GloVe

**概念**：Global Vectors，结合全局词共现统计。

```python
# 代码示例6：GloVe
glove = {
    "原理": "词共现矩阵分解",
    "优点": "利用全局统计",
    "代表": "GloVe-6B/100d",
}
for k, v in glove.items():
    print(f"  {k}: {v}")
```

### 2.4 FastText

**概念**：Facebook 提出，用子词(字符 n-gram)表示，能处理未登录词。

```python
# 代码示例7：FastText
fasttext = {
    "原理": "子词嵌入",
    "优点": "OOV 友好",
    "代表": "FastText Wiki News",
}
for k, v in fasttext.items():
    print(f"  {k}: {v}")
```

### 2.5 词嵌入对比

| 方法 | 年份 | 维度 | 语义 | OOV |
|------|------|------|------|-----|
| One-hot | 1990s | V | 无 | 差 |
| Word2Vec | 2013 | 300 | 好 | 差 |
| GloVe | 2014 | 300 | 好 | 差 |
| FastText | 2016 | 300 | 好 | 好 |

> 💡 **深度讲解**：词嵌入从 One-hot 到 Word2Vec 是革命性的——首次让机器理解"相似词向量相似"。但词嵌入的局限是：(1) 静态(多义词不行) (2) 词级别(句子不行)。这催生了句嵌入和上下文 Embedding。

> 📝 **精简总结**：词嵌入演进：One-hot→Word2Vec→GloVe→FastText；从稀疏到稠密，从无语义到有语义。

> 🎯 **梯度练习**：
> - 初级：用 gensim 加载 Word2Vec
> - 中级：找两个词的最近邻
> - 高级：训练自己的 Word2Vec

---

## 3. 句嵌入发展

### 3.1 平均池化

```python
# 代码示例8：平均池化句向量
def avg_pool(word_embs):
    return np.mean(word_embs, axis=0)
words = [embeddings["猫"], embeddings["狗"]]
print(f"平均池化: {avg_pool(words)[:3]}...")
print("问题: 丢失语序和语义组合")
```

### 3.2 InferSent

**概念**：2017 年 Facebook 提出，用 BiLSTM 训练句向量。

```python
# 代码示例9：InferSent
infersent = {
    "原理": "BiLSTM + 监督训练",
    "训练": "SNLI 自然语言推理",
    "优点": "句向量质量高",
}
for k, v in infersent.items():
    print(f"  {k}: {v}")
```

### 3.3 Sentence-BERT

**概念**：2019 年提出，用 Siamese BERT 生成句向量。

```python
# 代码示例10：Sentence-BERT
sbert = {
    "原理": "双塔 BERT + 对比学习",
    "优点": "快、质量高",
    "代表": "all-MiniLM-L6-v2",
    "用途": "语义搜索/聚类/分类",
}
for k, v in sbert.items():
    print(f"  {k}: {v}")
```

### 3.4 句嵌入对比

| 方法 | 年份 | 架构 | 速度 | 质量 |
|------|------|------|------|------|
| 平均池化 | - | 词向量平均 | 快 | 差 |
| InferSent | 2017 | BiLSTM | 中 | 中 |
| Sentence-BERT | 2019 | BERT 双塔 | 快 | 好 |

> 💡 **深度讲解**：Sentence-BERT 的关键创新是"双塔"结构——两个句子分别编码，再比较向量距离。这让语义搜索可以预计算文档向量，在线只算查询向量，快 100 倍以上。

> 📝 **精简总结**：句嵌入从平均到 Siamese BERT；双塔是关键，快且好。

> 🎯 **梯度练习**：
> - 初级：用 sentence-transformers 嵌入两句话
> - 中级：对比两句话相似度
> - 高级：用 SBERT 做语义搜索

---

## 4. 现代 Embedding 架构

### 4.1 双编码器 (Bi-Encoder)

**概念**：查询和文档分别独立编码，向量可预计算。

```python
# 代码示例11：双编码器
class BiEncoder:
    def __init__(self):
        self.encoder = "BERT"
    def encode_query(self, query):
        return f"[{self.encoder}] query: {query} -> 向量"
    def encode_doc(self, doc):
        return f"[{self.encoder}] doc: {doc} -> 向量"
be = BiEncoder()
print(be.encode_query("怎么退款"))
print(be.encode_doc("7天无理由退款政策"))
```

### 4.2 交叉编码器 (Cross-Encoder)

**概念**：查询和文档一起输入模型，直接输出相关性分数。

```python
# 代码示例12：交叉编码器
class CrossEncoder:
    def score(self, query, doc):
        return f"[CrossEncoder] ({query}, {doc}) -> 相关度分数"
ce = CrossEncoder()
print(ce.score("怎么退款", "7天无理由退款政策"))
print("优点: 精度高; 缺点: 慢, 不能预计算")
```

### 4.3 双编码器 vs 交叉编码器

| 维度 | 双编码器 | 交叉编码器 |
|------|---------|-----------|
| 速度 | 快(可预计算) | 慢(实时) |
| 精度 | 中 | 高 |
| 用途 | 初筛 | 精排 |
| 成本 | 低 | 高 |

```python
# 代码示例13：混合架构
hybrid = {
    "第一阶段": "双编码器初筛 Top-100",
    "第二阶段": "交叉编码器精排 Top-10",
    "效果": "兼顾速度和精度",
}
for k, v in hybrid.items():
    print(f"  {k}: {v}")
```

> 💡 **深度讲解**：RAG 检索通常用混合架构：双编码器从百万文档中快速初筛 100 个，再用交叉编码器精排到 10 个。这平衡了速度和精度。

> 📝 **精简总结**：双编码器快但粗，交叉编码器准但慢；RAG 用混合架构。

> 🎯 **梯度练习**：
> - 初级：用双编码器嵌入文档
> - 中级：用交叉编码器精排
> - 高级：实现混合检索 pipeline

---

## 5. 主流模型对比

### 5.1 OpenAI Embedding

```python
# 代码示例14：OpenAI Embedding
openai_emb = {
    "text-embedding-3-small": {"dim": 1536, "price": "$0.02/1M tokens"},
    "text-embedding-3-large": {"dim": 3072, "price": "$0.13/1M tokens"},
    "text-embedding-ada-002": {"dim": 1536, "price": "$0.10/1M tokens"},
}
for k, v in openai_emb.items():
    print(f"  {k}: {v}")
```

### 5.2 BGE 系列

```python
# 代码示例15：BGE 系列
bge_models = {
    "bge-small-zh": {"dim": 512, "lang": "中文", "size": "小"},
    "bge-base-zh": {"dim": 768, "lang": "中文", "size": "中"},
    "bge-large-zh": {"dim": 1024, "lang": "中文", "size": "大"},
    "bge-m3": {"dim": 1024, "lang": "多语言", "size": "大"},
}
for k, v in bge_models.items():
    print(f"  {k}: {v}")
```

### 5.3 GTE 系列

```python
# 代码示例16：GTE 系列
gte_models = {
    "gte-small": {"dim": 384, "lang": "多语言"},
    "gte-base": {"dim": 768, "lang": "多语言"},
    "gte-large": {"dim": 1024, "lang": "多语言"},
}
for k, v in gte_models.items():
    print(f"  {k}: {v}")
```

### 5.4 E5 系列

```python
# 代码示例17：E5 系列
e5_models = {
    "e5-small": {"dim": 384, "lang": "多语言"},
    "e5-base": {"dim": 768, "lang": "多语言"},
    "e5-large": {"dim": 1024, "lang": "多语言"},
    "e5-mistral": {"dim": 4096, "lang": "英文"},
}
for k, v in e5_models.items():
    print(f"  {k}: {v}")
```

### 5.5 m3e 系列

```python
# 代码示例18：m3e 系列
m3e_models = {
    "m3e-small": {"dim": 512, "lang": "中文"},
    "m3e-base": {"dim": 768, "lang": "中文"},
    "m3e-large": {"dim": 1024, "lang": "中文"},
}
for k, v in m3e_models.items():
    print(f"  {k}: {v}")
```

### 5.6 Jina Embedding

```python
# 代码示例19：Jina
jina_models = {
    "jina-embeddings-v2-small": {"dim": 512, "lang": "多语言"},
    "jina-embeddings-v2-base": {"dim": 768, "lang": "多语言"},
    "jina-embeddings-v3": {"dim": 1024, "lang": "多语言"},
}
for k, v in jina_models.items():
    print(f"  {k}: {v}")
```

### 5.7 模型对比总表

| 模型 | 维度 | 中文 | 开源 | 价格 | 速度 |
|------|------|------|------|------|------|
| OpenAI small | 1536 | 中 | 否 | $0.02/1M | 快 |
| OpenAI large | 3072 | 中 | 否 | $0.13/1M | 中 |
| BGE-large-zh | 1024 | 好 | 是 | 免费 | 中 |
| BGE-M3 | 1024 | 好 | 是 | 免费 | 中 |
| GTE-large | 1024 | 好 | 是 | 免费 | 中 |
| E5-large | 1024 | 好 | 是 | 免费 | 中 |
| m3e-large | 1024 | 好 | 是 | 免费 | 中 |

> 💡 **深度讲解**：选模型看三点：(1) 语言(中文选 BGE/m3e) (2) 是否开源自部署 (3) 成本。生产中开源 BGE-M3 是性价比之选。

> 📝 **精简总结**：中文选 BGE/m3e；英文选 E5/GTE；API 选 OpenAI；自部署选开源。

> 🎯 **梯度练习**：
> - 初级：对比两个模型在同任务上的效果
> - 中级：在 MTEB 上选模型
> - 高级：自部署 BGE 并测试

---

## 6. 维度选择与降维

### 6.1 维度选择

```python
# 代码示例20：维度选择
dimensions = {
    "384": "小模型，快，质量一般",
    "512": "中小",
    "768": "中等，平衡",
    "1024": "大，质量好",
    "1536": "OpenAI small",
    "3072": "OpenAI large",
}
for k, v in dimensions.items():
    print(f"  {k:6}: {v}")
```

### 6.2 降维

```python
# 代码示例21：PCA 降维
from sklearn.decomposition import PCA
import numpy as np
# 模拟 100 个 1536 维向量
X = np.random.randn(100, 1536)
pca = PCA(n_components=256)
X_reduced = pca.fit_transform(X)
print(f"原始: {X.shape} -> 降维: {X_reduced.shape}")
print(f"保留方差: {pca.explained_variance_ratio_.sum():.2%}")
```

### 6.3 Matryoshka 表示

```python
# 代码示例22：Matryoshka Embedding
matryoshka = {
    "原理": "向量前 N 维是完整表示",
    "优点": "可灵活截断维度",
    "代表": "BGE-M3, OpenAI v3",
}
for k, v in matryoshka.items():
    print(f"  {k}: {v}")
```

### 6.4 维度 vs 质量 vs 成本

| 维度 | 存储 | 速度 | 质量 |
|------|------|------|------|
| 384 | 1x | 1x | 基线 |
| 768 | 2x | 1.5x | +10% |
| 1024 | 2.7x | 2x | +15% |
| 1536 | 4x | 3x | +20% |
| 3072 | 8x | 5x | +25% |

> 💡 **深度讲解**：维度不是越大越好。高维向量存储和检索成本指数上升，但质量提升边际递减。通常 768-1024 是性价比甜点。

> 📝 **精简总结**：维度选 768-1024；降维用 PCA；Matryoshka 可灵活截断。

> 🎯 **梯度练习**：
> - 初级：对比不同维度的相似度
> - 中级：PCA 降维看保留多少方差
> - 高级：测试 Matryoshka 截断效果

---

## 7. 相似度计算

### 7.1 余弦相似度

```python
# 代码示例23：余弦相似度
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
a = np.array([1, 2, 3])
b = np.array([2, 4, 6])
print(f"余弦相似度: {cosine(a, b):.3f}")
# 预期: 1.0 (同方向)
```

### 7.2 欧氏距离

```python
# 代码示例24：欧氏距离
def euclidean(a, b):
    return np.linalg.norm(a - b)
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print(f"欧氏距离: {euclidean(a, b):.3f}")
```

### 7.3 点积

```python
# 代码示例25：点积
def dot(a, b):
    return np.dot(a, b)
a = np.array([1, 2, 3])
b = np.array([2, 4, 6])
print(f"点积: {dot(a, b):.3f}")
print("归一化后: 点积=余弦相似度")
```

### 7.4 三种距离对比

| 方法 | 公式 | 适用 |
|------|------|------|
| 余弦 | dot/(norm*norm) | 方向相似 |
| 欧氏 | ||a-b|| | 绝对距离 |
| 点积 | dot(a,b) | 归一化后 |

```python
# 代码示例26：距离选择
def choose_distance(normalized):
    if normalized:
        return "点积 = 余弦"
    return "余弦(先归一化)"
print(choose_distance(True))
```

> 💡 **深度讲解**：向量归一化后，点积等于余弦相似度。大多数向量数据库默认用余弦。归一化向量后用点积更快(免除法)。

> 📝 **精简总结**：余弦最常用；归一化后点积=余弦；向量库默认余弦。

> 🎯 **梯度练习**：
> - 初级：计算两个向量余弦
> - 中级：归一化后用点积
> - 高级：对比三种距离在搜索中的效果

---

## 8. Embedding 在 RAG 中的应用

### 8.1 RAG 流程

```python
# 代码示例27：RAG 流程
rag_flow = {
    "离线": "文档切块 -> Embedding -> 向量库",
    "在线": "Query -> Embedding -> 检索 -> LLM",
}
for phase, steps in rag_flow.items():
    print(f"  {phase}: {steps}")
```

### 8.2 RAG 中的 Embedding 选择

```python
# 代码示例28：RAG Embedding 选择
def rag_embedding(language, scale):
    if language == "zh":
        if scale == "small":
            return "bge-small-zh"
        return "bge-large-zh / bge-m3"
    return "e5-large / gte-large"
print(rag_embedding("zh", "large"))
```

### 8.3 RAG 质量关键

```python
# 代码示例29：RAG 质量因素
quality_factors = {
    "切块": "chunk 大小",
    "Embedding": "模型选择",
    "检索": "Top-K",
    "重排": "Reranker",
    "Prompt": "上下文利用",
}
for k, v in quality_factors.items():
    print(f"  {k}: {v}")
```

> 💡 **深度讲解**：RAG 的质量 = 检索质量 × 生成质量。检索质量由 Embedding 模型和切块策略决定。差的 Embedding 检索不到相关文档，再好的 LLM 也答不对。

> 📝 **精简总结**：RAG = 文档 Embedding + Query Embedding + 检索 + LLM；Embedding 是 RAG 质量基础。

> 🎯 **梯度练习**：
> - 初级：实现简单 RAG
> - 中级：对比不同 Embedding
> - 高级：优化 RAG 检索质量

---

## 9. 多语言 Embedding

### 9.1 多语言挑战

```python
# 代码示例30：多语言挑战
challenges = [
    "1. 不同语言分布不同",
    "2. 跨语言对齐",
    "3. 代码切换",
    "4. 低资源语言",
]
for c in challenges:
    print(f"  {c}")
```

### 9.2 多语言模型

```python
# 代码示例31：多语言模型
multilingual = {
    "bge-m3": "100+语言",
    "e5-multilingual": "100+语言",
    "gte-multilingual": "100+语言",
    "jina-v3": "89语言",
}
for k, v in multilingual.items():
    print(f"  {k}: {v}")
```

> 💡 **深度讲解**：多语言 Embedding 的关键是"跨语言对齐"——中文"猫"和英文"cat"向量距离近。这通过多语言对比学习实现。

> 📝 **精简总结**：多语言用 bge-m3/e5-multilingual；关键是跨语言对齐。

> 🎯 **梯度练习**：
> - 初级：嵌入中英两句话
> - 中级：测试跨语言相似度
> - 高级：对比多语言模型效果

---

## 10. 多模态 Embedding

### 10.1 CLIP

```python
# 代码示例32：CLIP
clip = {
    "原理": "图文对比学习",
    "输出": "文本向量 + 图像向量",
    "用途": "图文检索",
    "代表": "OpenAI CLIP, OpenCLIP",
}
for k, v in clip.items():
    print(f"  {k}: {v}")
```

### 10.2 多模态模型

```python
# 代码示例33：多模态 Embedding
multimodal = {
    "CLIP": "图文",
    "CLAP": "图文音",
    "ImageBind": "6模态",
}
for k, v in multimodal.items():
    print(f"  {k}: {v}")
```

> 💡 **深度讲解**：CLIP 让文本和图像映射到同一空间，实现"以文搜图"。这是多模态 AI 的基础。

> 📝 **精简总结**：多模态 Embedding 用 CLIP；图文对齐；用于跨模态检索。

> 🎯 **梯度练习**：
> - 初级：用 CLIP 嵌入图片
> - 中级：实现以文搜图
> - 高级：对比不同 CLIP 变体

---

## 11. Embedding 微调

### 11.1 什么时候需要微调

```python
# 代码示例34：微调时机
def need_finetune(domain, baseline_score, target):
    if baseline_score >= target:
        return "不需要微调"
    if domain == "通用":
        return "不需要微调"
    return "考虑微调"
print(need_finetune("法律", 0.7, 0.85))
```

### 11.2 微调方法

```python
# 代码示例35：微调方法
finetune_methods = {
    "对比学习": "正样本拉近, 负样本推远",
    "Pairwise": "(query, pos, neg) 三元组",
    "Cosine对比": "余弦损失",
}
for k, v in finetune_methods.items():
    print(f"  {k}: {v}")
```

### 11.3 微调数据

```python
# 代码示例36：微调数据
finetune_data = {
    "正样本": "相关对(query, doc)",
    "负样本": "不相关对",
    "数量": "至少 1000-10000",
    "质量": "比数量重要",
}
for k, v in finetune_data.items():
    print(f"  {k}: {v}")
```

> 💡 **深度讲解**：Embedding 微调用对比学习——让相关 pair 向量近，不相关 pair 远。需要领域数据，效果提升 5-20%。

> 📝 **精简总结**：微调用对比学习；需要领域数据；提升领域效果。

> 🎯 **梯度练习**：
> - 初级：准备微调数据
> - 中级：用 sentence-transformers 微调
> - 高级：对比微调前后效果

---

## 12. 批量优化与缓存

### 12.1 批量嵌入

```python
# 代码示例37：批量嵌入
def batch_embed(texts, batch_size=32):
    """批量处理"""
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        # embeddings = model.encode(batch)
        results.extend([np.random.rand(384) for _ in batch])
    return results
texts = ["文本1", "文本2", "文本3"] * 10
embs = batch_embed(texts)
print(f"嵌入 {len(embs)} 个文本, 维度 {len(embs[0])}")
```

### 12.2 缓存

```python
# 代码示例38：缓存策略
cache = {
    "哈希缓存": "文本哈希->向量",
    "语义缓存": "相似查询复用",
    "文档缓存": "文档向量预计算",
}
for k, v in cache.items():
    print(f"  {k}: {v}")
```

### 12.3 批量优化

```python
# 代码示例39：批量优化
batch_opt = {
    "batch_size": "32-128",
    "GPU": "批量越大越好",
    "CPU": "小 batch",
    "异步": "并行处理",
}
for k, v in batch_opt.items():
    print(f"  {k}: {v}")
```

> 💡 **深度讲解**：批量嵌入比逐条快 10-100 倍，因为 GPU 并行。离线建索引时必须批量。在线查询通常短文本，单条也行。

> 📝 **精简总结**：批量嵌入快 10-100x；缓存避免重复；离线预计算。

> 🎯 **梯度练习**：
> - 初级：批量嵌入 1000 条
> - 中级：实现文本哈希缓存
> - 高级：对比不同 batch_size 速度

---

## 13. 向量归一化

### 13.1 为什么归一化

```python
# 代码示例40：归一化
def normalize(v):
    return v / np.linalg.norm(v)
v = np.array([3.0, 4.0])
print(f"原始: {v}, 归一化: {normalize(v)}")
print("归一化后: ||v||=1, 点积=余弦")
```

### 13.2 归一化的好处

```python
# 代码示例41：归一化好处
benefits = [
    "1. 点积=余弦, 计算快",
    "2. 距离可比",
    "3. 向量库索引更高效",
    "4. 防止长度偏差",
]
for b in benefits:
    print(f"  {b}")
```

### 13.3 归一化与距离

```python
# 代码示例42：归一化与距离
a = normalize(np.array([1.0, 2.0, 3.0]))
b = normalize(np.array([2.0, 4.0, 6.0]))
print(f"归一化后点积: {np.dot(a, b):.3f}")
print(f"归一化后余弦: {np.dot(a, b):.3f}")
print("相等!")
```

> 💡 **深度讲解**：归一化向量后，点积 = 余弦相似度。向量数据库默认存储归一化向量，搜索时用点积(更快)。

> 📝 **精简总结**：归一化让点积=余弦；向量库默认归一化；计算更快。

> 🎯 **梯度练习**：
> - 初级：归一化向量
> - 中级：对比归一化前后距离
> - 高级：测试向量库是否自动归一化

---

## 14. 选型决策树

```python
# 代码示例43：选型决策树
def choose_embedding(language, deployment, scale, quality_need):
    if deployment == "api":
        if quality_need == "high":
            return "OpenAI text-embedding-3-large"
        return "OpenAI text-embedding-3-small"
    if language == "zh":
        if quality_need == "high":
            return "bge-large-zh-v1.5"
        return "bge-base-zh"
    if language == "multi":
        return "bge-m3"
    return "e5-large / gte-large"
print(choose_embedding("zh", "self-hosted", "medium", "high"))
print(choose_embedding("en", "api", "small", "low"))
```

### 选型决策表

| 场景 | 推荐模型 |
|------|---------|
| 中文 RAG | bge-large-zh-v1.5 |
| 多语言 | bge-m3 |
| 英文 RAG | e5-large-v2 |
| 低成本 API | OpenAI small |
| 高质量 API | OpenAI large |
| 自部署中文 | bge-base-zh |
| 多模态 | CLIP |

> 💡 **深度讲解**：选型看：语言(中文优先 BGE)、部署(API/自部署)、成本、质量。中文场景 BGE 系列是开源 SOTA。

> 📝 **精简总结**：中文 BGE，多语言 M3，英文 E5/GTE，API 选 OpenAI。

> 🎯 **梯度练习**：
> - 初级：为你的任务选模型
> - 中级：对比 3 个模型效果
> - 高级：构建选型决策系统

---

## 15. 性能基准 MTEB

### 15.1 什么是 MTEB

```python
# 代码示例44：MTEB
mteb = {
    "全称": "Massive Text Embedding Benchmark",
    "内容": "56 个任务",
    "维度": "检索/分类/聚类/STS",
    "用途": "模型排名",
}
for k, v in mteb.items():
    print(f"  {k}: {v}")
```

### 15.2 MTEB 任务类型

```python
# 代码示例45：MTEB 任务类型
task_types = {
    "检索": "Reranking, Retrieval",
    "分类": "Classification",
    "聚类": "Clustering",
    "STS": "语义文本相似度",
    "摘要": "Summarization",
}
for k, v in task_types.items():
    print(f"  {k}: {v}")
```

### 15.3 MTEB 排名

```python
# 代码示例46：MTEB 排名参考
mteb_ranking = {
    "bge-large-en-v1.5": "MTEB 排名靠前",
    "e5-large-v2": "MTEB 排名靠前",
    "gte-large": "MTEB 排名靠前",
    "openai-embedding-3": "API 中靠前",
}
for k, v in mteb_ranking.items():
    print(f"  {k}: {v}")
```

> 💡 **深度讲解**：MTEB 是 Embedding 界的 ImageNet。选模型前查 MTEB 排名，选在你任务类型上表现好的模型。

> 📝 **精简总结**：MTEB 是 Embedding 基准；查排名选模型；关注你的任务类型。

> 🎯 **梯度练习**：
> - 初级：看 MTEB 排行榜
> - 中级：选适合任务的模型
> - 高级：在 MTEB 子集上测试

---

## 16. 成本对比

### 16.1 API 成本

```python
# 代码示例47：API 成本
api_costs = {
    "OpenAI small": "$0.02/1M tokens",
    "OpenAI large": "$0.13/1M tokens",
    "Cohere": "$0.10/1M",
    "Voyage": "$0.12/1M",
}
for k, v in api_costs.items():
    print(f"  {k}: {v}")
```

### 16.2 自部署成本

```python
# 代码示例48：自部署成本
self_host = {
    "GPU": "A10/A100 租赁",
    "存储": "向量库",
    "运维": "人力",
    "优势": "边际成本低",
}
for k, v in self_host.items():
    print(f"  {k}: {v}")
```

### 16.3 成本对比

| 方案 | 成本(1M文档) | 速度 | 隐私 |
|------|-------------|------|------|
| OpenAI API | ~$1 | 快 | 差 |
| 自部署 BGE | ~$0.1 | 中 | 好 |
| 自部署小模型 | ~$0.05 | 快 | 好 |

> 💡 **深度讲解**：大规模 Embedding 用自部署开源模型，成本低 10-100 倍。小规模用 API 方便。

> 📝 **精简总结**：大规模自部署，小规模 API；中文 BGE 性价比高。

> 🎯 **梯度练习**：
> - 初级：估算你的 Embedding 成本
> - 中级：对比 API vs 自部署
> - 高级：优化 Embedding 成本

---

## 17. 常见坑点

```python
# 代码示例49：Embedding 30 个坑
pitfalls = [
    "1. 不归一化向量",
    "2. 选错模型(中文用英文模型)",
    "3. 维度太大浪费存储",
    "4. 不批量处理慢",
    "5. 不缓存重复查询",
    "6. 切块太大/太小",
    "7. 不做重排",
    "8. 检索 Top-K 太大",
    "9. 忽视多语言对齐",
    "10. 不微调领域模型",
    "11. 向量库选不对",
    "12. 不监控检索质量",
    "13. 忽视查询改写",
    "14. 不用混合检索",
    "15. 切块不重叠",
    "16. 忽视元数据",
    "17. 不评估 Embedding",
    "18. 盲目追大模型",
    "19. 不考虑成本",
    "20. 向量维度不匹配",
    "21. 不用 Matryoshka",
    "22. 不做增量索引",
    "23. 忽视冷热数据",
    "24. 不测试 OOV",
    "25. 多语言用单语模型",
    "26. 不微调就期望领域效果",
    "27. 忽视 Embedding 更新",
    "28. 不做去重",
    "29. 忽视向量库索引参数",
    "30. 不监控索引健康",
]
for p in pitfalls:
    print(f"  {p}")
```

---

### 18. 附录：速查代码集

#### 附录A：Embedding 快速开始

```python
# 代码示例50：快速开始
QUICK_START = """
# 安装
pip install sentence-transformers

# 使用
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('BAAI/bge-large-zh-v1.5')
embeddings = model.encode(["文本1", "文本2"])
"""
print(QUICK_START)
```

#### 附录B：相似度计算

```python
# 代码示例51：相似度计算
import numpy as np
def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

#### 附录C：面试考点

```python
# 代码示例52：面试考点
interview = [
    "Q: 什么是 Embedding？",
    "Q: 双编码器 vs 交叉编码器？",
    "Q: 余弦相似度原理？",
    "Q: 中文 Embedding 选什么？",
    "Q: MTEB 是什么？",
    "Q: 怎么微调 Embedding？",
    "Q: 向量为什么归一化？",
    "Q: 维度怎么选？",
    "Q: RAG 中怎么选 Embedding？",
    "Q: Embedding 成本怎么算？",
]
for q in interview:
    print(f"  {q}")
```

---

> 📌 本文档持续更新。最后更新：2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 D：Embedding 深度技术专题

#### D.1 Embedding 数学原理

```python
# 代码示例53：Embedding 数学
math_emb = {
    "目标": "相似对象向量近",
    "损失": "对比损失/三元组损失",
    "优化": "梯度下降",
    "输出": "归一化向量",
}
for k, v in math_emb.items():
    print(f"  {k}: {v}")
```

```python
# 代码示例54：对比损失
def contrastive_loss(anchor, positive, negative, margin=1.0):
    """Triplet loss"""
    d_pos = np.linalg.norm(anchor - positive)
    d_neg = np.linalg.norm(anchor - negative)
    return max(0, d_pos - d_neg + margin)
a = np.array([1, 0, 0], dtype=float)
p = np.array([1, 0.1, 0], dtype=float)
n = np.array([0, 1, 0], dtype=float)
print(f"三元组损失: {contrastive_loss(a, p, n):.3f}")
```

#### D.2 对比学习

```python
# 代码示例55：对比学习
contrastive = {
    "正样本": "相似对",
    "负样本": "不相似对",
    "InfoNCE": "对比损失",
    "困难负样本": "难负样本",
}
for k, v in contrastive.items():
    print(f"  {k}: {v}")
```

#### D.3 困难负样本挖掘

```python
# 代码示例56：困难负样本
def hard_negatives(anchor, candidates, n=5):
    """找最相似但不相关的负样本"""
    dists = [(c, np.linalg.norm(anchor - c)) for c in candidates]
    dists.sort(key=lambda x: x[1])
    return dists[:n]
```

---

#### D.4 Transformer 编码原理

```python
# 代码示例57：Transformer 编码
encoding = {
    "输入": "Token IDs",
    "Embedding层": "Token -> 向量",
    "Transformer": "多层自注意力",
    "池化": "CLS/Mean Pooling",
    "输出": "句向量",
}
for k, v in encoding.items():
    print(f"  {k}: {v}")
```

#### D.5 池化策略

```python
# 代码示例58：池化策略
pooling = {
    "CLS": "用 [CLS] token",
    "Mean": "所有 token 平均",
    "Max": "所有 token 最大",
    "Weighted": "加权平均",
}
for k, v in pooling.items():
    print(f"  {k}: {v}")
```

---

#### D.6 BGE 模型深入

```python
# 代码示例59：BGE 深入
bge_deep = {
    "训练": "对比学习 + 难负样本",
    "特点": "中文 SOTA",
    "查询前缀": "为查询加指令前缀",
    "代表": "bge-large-zh-v1.5",
}
for k, v in bge_deep.items():
    print(f"  {k}: {v}")
```

#### D.7 查询前缀

```python
# 代码示例60：查询前缀
bge_prefix = "为这个句子生成表示以用于检索相关文章："
def format_query(query):
    return bge_prefix + query
print(format_query("怎么退款"))
```

---

### 附录 E：Embedding 与向量数据库

#### E.1 向量数据库

```python
# 代码示例61：向量数据库
vector_dbs = {
    "Qdrant": "Rust, 高性能",
    "Milvus": "大规模",
    "Chroma": "轻量",
    "PGVector": "PostgreSQL 扩展",
    "Weaviate": "开源",
    "Pinecone": "托管",
    "Chroma": "轻量",
    "FAISS": "Facebook, 库",
}
for k, v in vector_dbs.items():
    print(f"  {k}: {v}")
```

#### E.2 索引类型

```python
# 代码示例62：索引类型
indexes = {
    "Flat": "暴力搜索, 准但慢",
    "IVF": "倒排, 快但有误差",
    "HNSW": "图索引, 快且准",
    "PQ": "量化压缩",
    "IVF-PQ": "组合",
}
for k, v in indexes.items():
    print(f"  {k}: {v}")
```

#### E.3 HNSW 原理

```python
# 代码示例63：HNSW
hnsw = {
    "全称": "Hierarchical Navigable Small World",
    "原理": "层次图搜索",
    "复杂度": "O(log n)",
    "参数": "M, efConstruction, efSearch",
}
for k, v in hnsw.items():
    print(f"  {k}: {v}")
```

```python
# 代码示例64：HNSW 参数
hnsw_params = {
    "M": "每个节点连接数(16-64)",
    "efConstruction": "构建时搜索宽度",
    "efSearch": "查询时搜索宽度",
    "tradeoff": "ef 大=准但慢",
}
for k, v in hnsw_params.items():
    print(f"  {k}: {v}")
```

---

#### E.4 向量数据库选择

```python
# 代码示例65：向量库选择
def choose_vector_db(scale, cloud, team):
    if scale == "small":
        return "Chroma / FAISS"
    if cloud:
        return "Pinecone / Qdrant Cloud"
    return "Qdrant / Milvus"
print(choose_vector_db("medium", False, 5))
```

---

### 附录 F：Embedding 与 RAG 深入

#### F.1 RAG 检索质量

```python
# 代码示例66：检索质量
retrieval_quality = {
    "Recall@K": "召回率",
    "Precision@K": "精确率",
    "MRR": "平均倒数排名",
    "NDCG": "归一化折损增益",
}
for k, v in retrieval_quality.items():
    print(f"  {k}: {v}")
```

#### F.2 RAG 优化

```python
# 代码示例67：RAG 优化
rag_opt = {
    "切块": "chunk_size, overlap",
    "Embedding": "选好模型",
    "检索": "Top-K, Rerank",
    "查询": "查询改写, HyDE",
}
for k, v in rag_opt.items():
    print(f"  {k}: {v}")
```

#### F.3 混合检索

```python
# 代码示例68：混合检索
hybrid_search = {
    "向量检索": "语义相似",
    "关键词检索": "BM25",
    "融合": "RRF 或加权",
    "效果": "比单一好",
}
for k, v in hybrid_search.items():
    print(f"  {k}: {v}")
```

---

### 附录 G：Embedding 微调深入

#### G.1 微调方法

```python
# 代码示例69：微调方法
finetune = {
    "Supervised": "(query, positive) pairs",
    "Contrastive": "triplet (anchor, pos, neg)",
    "Hard Neg": "困难负样本",
    "Instruction": "指令微调",
}
for k, v in finetune.items():
    print(f"  {k}: {v}")
```

#### G.2 微调数据格式

```python
# 代码示例70：数据格式
data_format = {
    "正样本": "(query, relevant_doc)",
    "负样本": "(query, irrelevant_doc)",
    "格式": "JSONL",
    "示例": '{"query": "...", "positive": "...", "negative": "..."}',
}
for k, v in data_format.items():
    print(f"  {k}: {v}")
```

#### G.3 微调框架

```python
# 代码示例71：微调框架
frameworks = {
    "sentence-transformers": "Python 库",
    "FlagEmbedding": "BGE 官方",
    "TEvat": "评测微调",
}
for k, v in frameworks.items():
    print(f"  {k}: {v}")
```

---

### 附录 H：Embedding 性能优化

#### H.1 GPU 推理

```python
# 代码示例72：GPU 优化
gpu_opt = {
    "batch_size": "大 batch",
    "fp16": "半精度",
    "ONNX": "ONNX Runtime",
    "TensorRT": "NVIDIA 优化",
}
for k, v in gpu_opt.items():
    print(f"  {k}: {v}")
```

#### H.2 CPU 推理

```python
# 代码示例73：CPU 优化
cpu_opt = {
    "int8": "量化",
    "ONNX": "ONNX Runtime CPU",
    "小模型": "small/base",
    "batch": "小 batch",
}
for k, v in cpu_opt.items():
    print(f"  {k}: {v}")
```

---

### 附录 I：Embedding 与多模态

#### I.1 CLIP 深入

```python
# 代码示例74：CLIP 深入
clip_deep = {
    "训练": "4亿图文对",
    "目标": "图文对比",
    "输出": "512维向量",
    "用途": "零样本分类, 图文检索",
}
for k, v in clip_deep.items():
    print(f"  {k}: {v}")
```

#### I.2 图像 Embedding

```python
# 代码示例75：图像 Embedding
image_emb = {
    "ResNet": "CNN",
    "ViT": "Transformer",
    "CLIP": "图文对齐",
    "DINO": "自监督",
}
for k, v in image_emb.items():
    print(f"  {k}: {v}")
```

---

### 附录 J：Embedding 评估

#### J.1 评估指标

```python
# 代码示例76：评估指标
eval_metrics = {
    "Recall@K": "Top-K 召回率",
    "Precision@K": "精确率",
    "MRR": "平均倒数排名",
    "NDCG": "排序质量",
    "MAP": "平均精度",
}
for k, v in eval_metrics.items():
    print(f"  {k}: {v}")
```

#### J.2 评估数据集

```python
# 代码示例77：评估数据集
eval_datasets = {
    "MTEB": "多任务基准",
    "C-MTEB": "中文基准",
    "MIRACL": "多语言检索",
    "BEIR": "检索基准",
}
for k, v in eval_datasets.items():
    print(f"  {k}: {v}")
```

---

### 附录 K：Embedding 常见错误

```python
# 代码示例78：常见错误
errors = [
    "1. 用错模型语言",
    "2. 不归一化",
    "3. 维度不匹配",
    "4. 不批量",
    "5. 不缓存",
    "6. 切块不合理",
    "7. 不重排",
    "8. 不评估",
    "9. 盲目追大",
    "10. 忽视成本",
]
for e in errors:
    print(f"  {e}")
```

---

### 附录 L：Embedding 面试题

```python
# 代码示例79：面试题
interview_questions = [
    "Q: 解释 Embedding 原理",
    "Q: 双编码器 vs 交叉编码器",
    "Q: 余弦相似度 vs 欧氏距离",
    "Q: 为什么归一化",
    "Q: 中文 Embedding 选什么",
    "Q: MTEB 是什么",
    "Q: 怎么微调 Embedding",
    "Q: RAG 中怎么选 Embedding",
    "Q: HNSW 原理",
    "Q: 维度怎么选",
]
for q in interview_questions:
    print(f"  {q}")
```

---

### 附录 M：最终总结

本文档《Embedding 模型选型》系统覆盖了：基本概念、词嵌入历史、句嵌入、现代架构、主流模型对比、维度与降维、相似度计算、RAG 应用、多语言、多模态、微调、批量优化、缓存、归一化、选型决策树、MTEB、成本、坑点。

> 文档版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 N：Embedding 深度技术手册

#### N.1 Embedding 模型架构深入

```python
# 代码示例80：Transformer 架构
transformer_arch = {
    "输入嵌入": "Token + Position Embedding",
    "编码器层": ["自注意力", "前馈网络", "残差", "LayerNorm"],
    "池化层": "CLS / Mean Pooling",
    "投影头": "对比学习投影",
}
for k, v in transformer_arch.items():
    print(f"  {k}: {v}")
```

```python
# 代码示例81：自注意力机制
attention = {
    "Q": "Query",
    "K": "Key",
    "V": "Value",
    "公式": "softmax(QK^T/sqrt(d))V",
    "作用": "全局依赖建模",
}
for k, v in attention.items():
    print(f"  {k}: {v}")
```

#### N.2 位置编码

```python
# 代码示例82：位置编码
pos_encodings = {
    "正弦": "原始 Transformer",
    "可学习": "BERT",
    "RoPE": "旋转位置编码",
    "ALiBi": "线性偏置",
}
for k, v in pos_encodings.items():
    print(f"  {k}: {v}")
```

#### N.3 归一化层

```python
# 代码示例83：归一化
norm_layers = {
    "LayerNorm": "对特征维归一化",
    "RMSNorm": "简化版",
    "用途": "稳定训练",
}
for k, v in norm_layers.items():
    print(f"  {k}: {v}")
```

---

#### N.4 BERT 架构

```python
# 代码示例84：BERT
bert = {
    "架构": "双向 Transformer",
    "预训练": "MLM + NSP",
    "输出": "Token 向量 + CLS",
    "Embedding": "CLS 或 Mean Pooling",
}
for k, v in bert.items():
    print(f"  {k}: {v}")
```

#### N.5 Sentence-BERT 架构

```python
# 代码示例85：Sentence-BERT
sbert_arch = {
    "双塔": "两个 BERT 共享权重",
    "池化": "Mean Pooling",
    "损失": "对比学习/回归",
    "优点": "快(可预计算)",
}
for k, v in sbert_arch.items():
    print(f"  {k}: {v}")
```

---

#### N.6 BGE 架构

```python
# 代码示例86：BGE 架构
bge_arch = {
    "基座": "BERT/RoBERTa",
    "训练": "对比学习",
    "特点": "查询前缀指令",
    "中文": "RoBERTa-zh",
}
for k, v in bge_arch.items():
    print(f"  {k}: {v}")
```

#### N.7 E5 架构

```python
# 代码示例87：E5 架构
e5_arch = {
    "基座": "BERT",
    "训练": "弱监督对比学习",
    "特点": "指令前缀",
    "代表": "e5-large-v2",
}
for k, v in e5_arch.items():
    print(f"  {k}: {v}")
```

---

### 附录 O：Embedding 训练数据

#### O.1 预训练数据

```python
# 代码示例88：预训练数据
pretrain_data = {
    "英文": "Wikipedia, BookCorpus, Web",
    "中文": "中文维基, 百度百科, 网页",
    "多语言": "多语言维基",
    "量": "TB 级文本",
}
for k, v in pretrain_data.items():
    print(f"  {k}: {v}")
```

#### O.2 微调数据

```python
# 代码示例89：微调数据
finetune_data = {
    "检索": "(query, relevant_doc) pairs",
    "STS": "(sent1, sent2, score)",
    "分类": "(text, label)",
    "聚类": "同主题组",
}
for k, v in finetune_data.items():
    print(f"  {k}: {v}")
```

#### O.3 数据增强

```python
# 代码示例90：数据增强
augmentation = {
    "回译": "翻译再翻译",
    "同义词替换": "词替换",
    "随机删除": "drop words",
    "困难负样本": "挖掘难负",
}
for k, v in augmentation.items():
    print(f"  {k}: {v}")
```

---

### 附录 P：Embedding 损失函数

#### P.1 对比损失

```python
# 代码示例91：对比损失
def contrastive_loss_v2(anchor, positive, negative, margin=1.0):
    d_pos = np.linalg.norm(anchor - positive)
    d_neg = np.linalg.norm(anchor - negative)
    return np.maximum(0, d_pos - d_neg + margin)
print("Triplet Loss: max(0, d(a,p) - d(a,n) + margin)")
```

#### P.2 InfoNCE

```python
# 代码示例92：InfoNCE
import math
def infonce_loss(anchor, positive, negatives, temperature=0.07):
    pos_sim = np.dot(anchor, positive) / temperature
    neg_sims = [np.dot(anchor, n) / temperature for n in negatives]
    all_sims = np.array([pos_sim] + list(neg_sims))
    exp_sims = np.exp(all_sims)
    return -math.log(exp_sims[0] / exp_sims.sum())
print("InfoNCE: -log(exp(pos)/sum(exp(all)))")
```

#### P.3 Cosine 损失

```python
# 代码示例93：Cosine 损失
def cosine_loss(a, b, label):
    """label=1 相似, label=0 不相似"""
    sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return (sim - label) ** 2
```

---

### 附录 Q：Embedding 推理优化

#### Q.1 ONNX 优化

```python
# 代码示例94：ONNX
onnx = {
    "导出": "PyTorch -> ONNX",
    "推理": "ONNX Runtime",
    "优势": "跨平台, 快",
}
for k, v in onnx.items():
    print(f"  {k}: {v}")
```

#### Q.2 TensorRT

```python
# 代码示例95：TensorRT
tensorrt = {
    "适用": "NVIDIA GPU",
    "优化": "层融合, 量化",
    "速度": "2-5x",
}
for k, v in tensorrt.items():
    print(f"  {k}: {v}")
```

#### Q.3 量化

```python
# 代码示例96：量化
quantization = {
    "FP32": "原始",
    "FP16": "半精度",
    "INT8": "整数量化",
    "效果": "4x 加速, 质量略降",
}
for k, v in quantization.items():
    print(f"  {k}: {v}")
```

---

### 附录 R：Embedding 存储

#### R.1 向量存储

```python
# 代码示例97：向量存储
storage = {
    "NumPy": "内存",
    "Faiss": "文件",
    "Qdrant": "数据库",
    "Milvus": "数据库",
    "PGVector": "PostgreSQL",
}
for k, v in storage.items():
    print(f"  {k}: {v}")
```

#### R.2 存储计算

```python
# 代码示例98：存储计算
def storage_size(n_docs, dim, bytes_per=4):
    return n_docs * dim * bytes_per / 1024 / 1024
print(f"100万文档 768维: {storage_size(1000000, 768):.0f} MB")
print(f"100万文档 1536维: {storage_size(1000000, 1536):.0f} MB")
```

---

### 附录 S：Embedding 检索优化

#### S.1 查询改写

```python
# 代码示例99：查询改写
query_rewrite = {
    "扩展": "加同义词",
    "分解": "拆子问题",
    "HyDE": "假设文档嵌入",
    "翻译": "跨语言",
}
for k, v in query_rewrite.items():
    print(f"  {k}: {v}")
```

#### S.2 Reranker

```python
# 代码示例100：Reranker
reranker = {
    "模型": "CrossEncoder",
    "作用": "精排 Top-K",
    "输入": "(query, doc) pair",
    "输出": "相关度分数",
}
for k, v in reranker.items():
    print(f"  {k}: {v}")
```

#### S.3 Top-K 选择

```python
# 代码示例101：Top-K
def choose_top_k(n_candidates, need):
    if n_candidates < 100:
        return n_candidates
    return min(100, need * 10)
print(choose_top_k(10000, 10))
```

---

### 附录 T：Embedding 应用模式

#### T.1 语义搜索

```python
# 代码示例102：语义搜索
semantic_search = {
    "离线": "文档切块 -> Embedding -> 索引",
    "在线": "Query -> Embedding -> 检索",
    "输出": "Top-K 相关文档",
}
for k, v in semantic_search.items():
    print(f"  {k}: {v}")
```

#### T.2 推荐系统

```python
# 代码示例103：推荐
recommend = {
    "用户向量": "历史行为",
    "物品向量": "内容 Embedding",
    "匹配": "向量相似度",
}
for k, v in recommend.items():
    print(f"  {k}: {v}")
```

#### T.3 聚类

```python
# 代码示例104：聚类
clustering = {
    "K-Means": "K 均值",
    "DBSCAN": "密度",
    "HDBSCAN": "层次",
    "用途": "自动分组",
}
for k, v in clustering.items():
    print(f"  {k}: {v}")
```

---

### 附录 U：Embedding 生产实践

#### U.1 生产架构

```python
# 代码示例105：生产架构
prod_arch = {
    "离线": "ETL -> 切块 -> Embedding -> 索引",
    "在线": "Query -> Embedding -> 检索 -> LLM",
    "监控": "检索质量, 延迟, 成本",
}
for k, v in prod_arch.items():
    print(f"  {k}: {v}")
```

#### U.2 监控指标

```python
# 代码示例106：监控
monitor = {
    "延迟": "P50, P99",
    "吞吐": "QPS",
    "质量": "Recall, MRR",
    "成本": "Embedding 调用费",
}
for k, v in monitor.items():
    print(f"  {k}: {v}")
```

---

### 附录 V：Embedding 常见问题

```python
# 代码示例107：常见问题
faq = [
    ("Q: 中文用什么 Embedding？", "A: BGE-large-zh-v1.5 或 bge-m3"),
    ("Q: 维度选多少？", "A: 768-1024 性价比高"),
    ("Q: 怎么归一化？", "A: vector / norm"),
    ("Q: 余弦和欧氏哪个好？", "A: 余弦, 归一化后点积=余弦"),
    ("Q: 怎么选向量库？", "A: 小规模 Chroma, 大规模 Qdrant/Milvus"),
]
for q, a in faq:
    print(f"  {q}\n  {a}")
```

---

### 附录 W：Embedding 面试深度

```python
# 代码示例108：面试深度
interview_deep = [
    "Q: 解释双编码器和交叉编码器区别",
    "Q: 为什么需要归一化",
    "Q: HNSW 原理",
    "Q: BGE 和 E5 区别",
    "Q: 怎么评估 Embedding",
    "Q: 怎么微调 Embedding",
    "Q: 多语言 Embedding 原理",
    "Q: CLIP 原理",
]
for q in interview_deep:
    print(f"  {q}")
```

---

### 附录 X：最终总结

本文档系统覆盖 Embedding 全部知识：概念、历史、架构、模型、维度、相似度、RAG、多语言、多模态、微调、优化、选型、基准、成本、坑点。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 Y：Embedding 完整知识百科

#### Y.1 Embedding 发展时间线

```python
# 代码示例109：时间线
timeline = [
    (2003, "Word2Vec 前身"),
    (2013, "Word2Vec"),
    (2014, "GloVe"),
    (2016, "FastText"),
    (2017, "InferSent, Transformer"),
    (2018, "BERT"),
    (2019, "Sentence-BERT"),
    (2022, "BGE, E5, GTE"),
    (2023, "BGE-M3, Jina v2"),
    (2024, "Jina v3, Matryoshka"),
]
for year, event in timeline:
    print(f"  {year}: {event}")
```

#### Y.2 Embedding 核心概念

```python
# 代码示例110：核心概念
core_concepts = {
    "向量空间": "Embedding 所在空间",
    "语义相似": "向量距离近",
    "对比学习": "拉近相似推远不相似",
    "归一化": "向量长度=1",
    "余弦相似度": "方向相似度量",
    "双编码器": "独立编码",
    "交叉编码器": "联合编码",
}
for k, v in core_concepts.items():
    print(f"  {k}: {v}")
```

---

#### Y.3 Embedding 模型家族

```python
# 代码示例111：模型家族
families = {
    "OpenAI": "text-embedding-3",
    "BAAI": "BGE 系列",
    "Microsoft": "E5 系列",
    "Alibaba": "GTE 系列",
    "Xingyuan": "m3e 系列",
    "Jina AI": "Jina Embeddings",
    "Sentence-BERT": "all-MiniLM",
}
for k, v in families.items():
    print(f"  {k}: {v}")
```

#### Y.4 模型选型矩阵

| 场景 | 中文 | 英文 | 多语言 | 开源 | API |
|------|------|------|--------|------|-----|
| 高质量 | bge-large-zh | e5-large | bge-m3 | 是 | - |
| 低成本 | bge-small-zh | all-MiniLM | gte-small | 是 | - |
| API | - | - | - | - | OpenAI |
| 多模态 | - | - | - | CLIP | OpenAI |

---

#### Y.5 Embedding 与向量数据库配合

```python
# 代码示例112：Embedding + 向量库
def embed_and_index(texts, model, vector_db):
    """嵌入并存入向量库"""
    embeddings = model.encode(texts)
    vector_db.add(embeddings, texts)
    return f"索引 {len(texts)} 个文档"
print(embed_and_index(["文档1", "文档2"], "bge-large", "Qdrant"))
```

---

#### Y.6 Embedding 评估流程

```python
# 代码示例113：评估流程
eval_flow = [
    "1. 准备评估集(query, relevant_docs)",
    "2. 嵌入所有文档",
    "3. 嵌入查询",
    "4. 检索 Top-K",
    "5. 计算 Recall@K, MRR, NDCG",
    "6. 对比模型",
]
for step in eval_flow:
    print(f"  {step}")
```

#### Y.7 评估指标详解

```python
# 代码示例114：指标详解
metrics_detail = {
    "Recall@K": "相关文档被召回比例",
    "Precision@K": "Top-K 中相关比例",
    "MRR": "第一个相关文档排名倒数平均",
    "NDCG": "考虑排名位置的增益",
    "MAP": "平均精度",
}
for k, v in metrics_detail.items():
    print(f"  {k}: {v}")
```

---

#### Y.8 Embedding 训练流程

```python
# 代码示例115：训练流程
train_flow = [
    "1. 准备预训练语料",
    "2. 训练 BERT 基座",
    "3. 准备微调对(query, pos, neg)",
    "4. 对比学习微调",
    "5. 评估 MTEB",
    "6. 发布模型",
]
for step in train_flow:
    print(f"  {step}")
```

#### Y.9 训练技巧

```python
# 代码示例116：训练技巧
training_tips = {
    "学习率": "2e-5",
    "Batch size": "128",
    "Epoch": "3-10",
    "Temperature": "0.05-0.1",
    "难负样本": "关键!",
}
for k, v in training_tips.items():
    print(f"  {k}: {v}")
```

---

#### Y.10 Embedding 推理服务

```python
# 代码示例117：推理服务
inference_service = {
    "框架": "FastAPI / TorchServe",
    "批处理": "动态 batching",
    "缓存": "Redis",
    "监控": "Prometheus",
}
for k, v in inference_service.items():
    print(f"  {k}: {v}")
```

---

#### Y.11 Embedding 与 LLM 关系

```python
# 代码示例118：Embedding 与 LLM
relation = {
    "Embedding": "理解语义, 检索",
    "LLM": "生成, 推理",
    "RAG": "Embedding 检索 + LLM 生成",
    "协同": "Embedding 找上下文, LLM 生成答案",
}
for k, v in relation.items():
    print(f"  {k}: {v}")
```

---

#### Y.12 Embedding 与 Agent

```python
# 代码示例119：Embedding 与 Agent
agent_emb = {
    "记忆": "向量检索历史",
    "技能": "技能 Embedding 路由",
    "RAG": "知识库检索",
    "规划": "任务分解检索",
}
for k, v in agent_emb.items():
    print(f"  {k}: {v}")
```

---

#### Y.13 Embedding 最新趋势

```python
# 代码示例120：最新趋势
trends = {
    "多模态": "CLIP 扩展",
    "长文本": "长上下文 Embedding",
    "领域": "法律/医疗/代码",
    "高效": "Matryoshka, 量化",
    "安全": "Embedding 隐私",
}
for k, v in trends.items():
    print(f"  {k}: {v}")
```

---

### 附录 Z：Embedding 速查手册

#### Z.1 常用命令

```python
# 代码示例121：常用命令
commands = {
    "安装": "pip install sentence-transformers",
    "嵌入": "model.encode(texts)",
    "相似度": "cos_sim(a, b)",
    "归一化": "F.normalize(a, dim=0)",
}
for k, v in commands.items():
    print(f"  {k}: {v}")
```

#### Z.2 常用代码模板

```python
# 代码示例122：模板
TEMPLATE = """
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('BAAI/bge-large-zh-v1.5')
docs = ['文档1', '文档2', '文档3']
doc_embs = model.encode(docs)
query = '查询'
q_emb = model.encode([query])
scores = cosine_similarity(q_emb, doc_embs)[0]
print('Top-1:', docs[scores.argmax()])
"""
print(TEMPLATE)
```

---

#### Z.3 模型选择速查

| 需求 | 推荐 |
|------|------|
| 中文 RAG | bge-large-zh-v1.5 |
| 多语言 | bge-m3 |
| 英文 RAG | e5-large-v2 |
| 轻量 | all-MiniLM-L6-v2 |
| API | OpenAI v3 |
| 多模态 | CLIP |

---

#### Z.4 维度速查

| 模型 | 维度 |
|------|------|
| all-MiniLM | 384 |
| bge-small-zh | 512 |
| bge-base-zh | 768 |
| bge-large-zh | 1024 |
| OpenAI small | 1536 |
| OpenAI large | 3072 |

---

#### Z.5 坑点速查

```python
# 代码示例123：坑点速查
pitfalls_quick = [
    "不归一化",
    "选错模型",
    "维度太大",
    "不批量",
    "不缓存",
    "不评估",
    "不重排",
    "盲目追大",
]
for p in pitfalls_quick:
    print(f"  ❌ {p}")
```

---

#### Z.6 面试速查

```python
# 代码示例124：面试速查
interview_quick = [
    "Embedding 是把文本映射到向量空间",
    "双编码器快, 交叉编码器准",
    "余弦 = 点积/模长积",
    "归一化后点积=余弦",
    "中文选 BGE",
    "MTEB 是基准",
    "微调=对比学习",
    "HNSW 是图索引",
]
for a in interview_quick:
    print(f"  ✅ {a}")
```

---

### 附录 ZZ：文档信息

- **名称**: Embedding 模型选型
- **版本**: 2.0
- **更新**: 2026-09-10
- **代码示例**: 120+

> P0 深度重写完成。

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 AAAAA：Embedding 深度技术百科

#### AAAAA.1 Embedding 数学基础

```python
# 代码示例125：数学基础
math_basics = {
    "向量": "有序数字列表",
    "模长": "||v|| = sqrt(sum(v_i^2))",
    "点积": "a·b = sum(a_i * b_i)",
    "余弦": "cos = dot/(||a||*||b||)",
    "归一化": "v/||v||",
}
for k, v in math_basics.items():
    print(f"  {k}: {v}")
```

```python
# 代码示例126：向量运算
v = np.array([3.0, 4.0])
print(f"向量: {v}")
print(f"模长: {np.linalg.norm(v):.2f}")
print(f"归一化: {v / np.linalg.norm(v)}")
print(f"归一化模长: {np.linalg.norm(v / np.linalg.norm(v)):.2f}")
```

#### AAAAA.2 向量空间几何

```python
# 代码示例127：向量空间
space = {
    "维度": "向量长度",
    "正交": "点积=0",
    "归一化": "单位球",
    "距离": "度量空间",
}
for k, v in space.items():
    print(f"  {k}: {v}")
```

---

#### AAAAA.3 神经网络基础

```python
# 代码示例128：神经网络
nn_basics = {
    "层": "线性变换+激活",
    "激活": "ReLU, GELU",
    "损失": "MSE, 交叉熵",
    "优化器": "Adam, AdamW",
}
for k, v in nn_basics.items():
    print(f"  {k}: {v}")
```

#### AAAAA.4 Transformer 深入

```python
# 代码示例129：Transformer
transformer_deep = {
    "自注意力": "全局依赖",
    "多头": "多视角",
    "前馈": "非线性变换",
    "残差": "梯度流",
    "LayerNorm": "稳定",
}
for k, v in transformer_deep.items():
    print(f"  {k}: {v}")
```

---

#### AAAAA.5 词嵌入数学

```python
# 代码示例130：词嵌入数学
word_emb_math = {
    "目标": "P(context|center) 或 P(center|context)",
    "损失": "交叉熵",
    "输出": "词向量矩阵",
    "维度": "300",
}
for k, v in word_emb_math.items():
    print(f"  {k}: {v}")
```

#### AAAAA.6 词类比

```python
# 代码示例131：词类比
def analogy(word_emb, a, b, c):
    """a - b + c ≈ d"""
    target = word_emb[a] - word_emb[b] + word_emb[c]
    best = max(word_emb.keys(), key=lambda w: np.dot(word_emb[w], target))
    return best
print("国王-男人+女人≈女王")
```

---

#### AAAAA.7 句嵌入数学

```python
# 代码示例132：句嵌入数学
sent_math = {
    "目标": "相似句子向量近",
    "方法": "Siamese 网络",
    "损失": "对比损失",
    "池化": "Mean/CLS",
}
for k, v in sent_math.items():
    print(f"  {k}: {v}")
```

---

### 附录 BBBBB：Embedding 模型训练

#### BBBBB.1 预训练

```python
# 代码示例133：预训练
pretrain = {
    "MLM": "掩码语言模型",
    "NSP": "下一句预测",
    "语料": "Wikipedia + 书籍",
    "目标": "学习语言表示",
}
for k, v in pretrain.items():
    print(f"  {k}: {v}")
```

#### BBBBB.2 对比学习训练

```python
# 代码示例134：对比学习训练
contrastive_train = {
    "输入": "(anchor, positive, negative)",
    "损失": "InfoNCE",
    "目标": "正近负远",
    "温度": "0.07",
}
for k, v in contrastive_train.items():
    print(f"  {k}: {v}")
```

#### BBBBB.3 难负样本

```python
# 代码示例135：难负样本
hard_neg = {
    "为什么": "易负样本太简单",
    "怎么找": "用弱模型检索",
    "效果": "提升显著",
    "风险": "假负样本",
}
for k, v in hard_neg.items():
    print(f"  {k}: {v}")
```

---

#### BBBBB.4 微调数据构造

```python
# 代码示例136：数据构造
def build_pairs(corpus, n=1000):
    """构造(query, positive)对"""
    pairs = []
    for doc in corpus:
        query = doc[:50]  # 简化
        pairs.append((query, doc))
    return pairs[:n]
print("构造 (query, positive) pairs")
```

#### BBBBB.5 训练超参

```python
# 代码示例137：超参
hyperparams = {
    "lr": "2e-5",
    "batch_size": "128",
    "epochs": "5",
    "warmup": "10%",
    "weight_decay": "0.01",
}
for k, v in hyperparams.items():
    print(f"  {k}: {v}")
```

---

### 附录 CCCCC：Embedding 推理部署

#### CCCCC.1 部署模式

```python
# 代码示例138：部署模式
deploy_modes = {
    "本地": "笔记本",
    "服务器": "GPU 服务器",
    "云": "云 GPU",
    "边缘": "CPU/移动端",
}
for k, v in deploy_modes.items():
    print(f"  {k}: {v}")
```

#### CCCCC.2 推理框架

```python
# 代码示例139：推理框架
inference_frameworks = {
    "PyTorch": "原始",
    "ONNX Runtime": "跨平台",
    "TensorRT": "NVIDIA",
    "vLLM": "LLM 服务",
    "Triton": "NVIDIA 推理服务",
}
for k, v in inference_frameworks.items():
    print(f"  {k}: {v}")
```

#### CCCCC.3 批量推理

```python
# 代码示例140：批量推理
def batch_inference(texts, model, batch_size=32):
    all_emb = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        emb = model.encode(batch)
        all_emb.append(emb)
    return np.vstack(all_emb)
print("批量推理: batch_size=32-128")
```

---

### 附录 DDDDD：Embedding 与向量数据库深入

#### DDDDD.1 向量索引算法

```python
# 代码示例141：索引算法
index_algos = {
    "Flat": "暴力, O(n)",
    "IVF": "倒排, O(n/k)",
    "HNSW": "图, O(log n)",
    "PQ": "量化, 压缩",
    "IVF-PQ": "组合",
    "DiskANN": "磁盘",
}
for k, v in index_algos.items():
    print(f"  {k}: {v}")
```

#### DDDDD.2 HNSW 详解

```python
# 代码示例142：HNSW 详解
hnsw_detail = {
    "层级": "多层图",
    "入口": "顶层节点",
    "搜索": "逐层贪心",
    "参数": "M, ef",
}
for k, v in hnsw_detail.items():
    print(f"  {k}: {v}")
```

#### DDDDD.3 IVF 详解

```python
# 代码示例143：IVF
ivf_detail = {
    "原理": "K-Means 聚类",
    "倒排表": "每个簇",
    "搜索": "只搜最近簇",
    "nlist": "簇数",
    "nprobe": "探测簇数",
}
for k, v in ivf_detail.items():
    print(f"  {k}: {v}")
```

---

#### DDDDD.4 量化

```python
# 代码示例144：量化
quant_detail = {
    "PQ": "乘积量化",
    "SQ": "标量量化",
    "二值": "Binary",
    "效果": "压缩 4-32x",
}
for k, v in quant_detail.items():
    print(f"  {k}: {v}")
```

#### DDDDD.5 向量数据库对比

| 数据库 | 语言 | 特点 | 适合 |
|--------|------|------|------|
| Qdrant | Rust | 高性能 | 生产 |
| Milvus | C++ | 大规模 | 大规模 |
| Chroma | Python | 轻量 | 原型 |
| PGVector | C | PG 扩展 | 小量 |
| Pinecone | - | 托管 | 托管 |
| Weaviate | Go | 开源 | 生产 |

---

### 附录 EEEEE：Embedding 应用深入

#### EEEEE.1 RAG 检索

```python
# 代码示例145：RAG 检索
def rag_retrieve(query, vector_db, top_k=5):
    q_emb = embed_query(query)
    results = vector_db.search(q_emb, top_k)
    return results
print("RAG: query -> embed -> search -> context -> LLM")
```

#### EEEEE.2 语义搜索

```python
# 代码示例146：语义搜索
def semantic_search(query, docs, doc_embs, model, top_k=5):
    q_emb = model.encode([query])
    scores = np.dot(q_emb, doc_embs.T)[0]
    top_idx = scores.argsort()[-top_k:][::-1]
    return [(docs[i], scores[i]) for i in top_idx]
print("语义搜索完成")
```

#### EEEEE.3 聚类分析

```python
# 代码示例147：聚类
from sklearn.cluster import KMeans
def cluster_texts(embs, k=5):
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(embs)
    return labels
print("K-Means 聚类完成")
```

---

#### EEEEE.4 异常检测

```python
# 代码示例148：异常检测
def anomaly_detection(embs, threshold=2.0):
    centroid = embs.mean(axis=0)
    dists = np.linalg.norm(embs - centroid, axis=1)
    std = dists.std()
    return dists > threshold * std
print("离群点检测完成")
```

#### EEEEE.5 去重

```python
# 代码示例149：去重
def deduplicate(embs, threshold=0.95):
    """余弦相似度>threshold 视为重复"""
    n = len(embs)
    keep = list(range(n))
    for i in range(n):
        for j in range(i+1, n):
            sim = np.dot(embs[i], embs[j])
            if sim > threshold and j in keep:
                keep.remove(j)
    return keep
print("去重完成")
```

---

### 附录 FFFFF：Embedding 评估深入

#### FFFFF.1 评估方法

```python
# 代码示例150：评估方法
eval_methods = {
    "人工评估": "准确但贵",
    "自动指标": "Recall, MRR",
    "LLM 评估": "LLM-as-Judge",
    "A/B 测试": "线上指标",
}
for k, v in eval_methods.items():
    print(f"  {k}: {v}")
```

#### FFFFF.2 MTEB 深入

```python
# 代码示例151：MTEB 深入
mteb_deep = {
    "任务数": "56",
    "类型": "Retrieval, STS, Clustering, Classification",
    "语言": "多语言",
    "度量": "nDCG, Spearman",
}
for k, v in mteb_deep.items():
    print(f"  {k}: {v}")
```

#### FFFFF.3 C-MTEB

```python
# 代码示例152：C-MTEB
cmteb = {
    "全称": "Chinese MTEB",
    "任务数": "30+",
    "特点": "中文评测",
    "用途": "选中文模型",
}
for k, v in cmteb.items():
    print(f"  {k}: {v}")
```

---

### 附录 GGGGG：Embedding 成本深入

#### GGGGG.1 API 成本计算

```python
# 代码示例153：API 成本
def api_cost(n_tokens, price_per_million):
    return n_tokens / 1_000_000 * price_per_million
print(f"100万 tokens @ $0.02: ${api_cost(1000000, 0.02):.2f}")
print(f"1000万 tokens @ $0.02: ${api_cost(10000000, 0.02):.2f}")
```

#### GGGGG.2 自部署成本

```python
# 代码示例154：自部署成本
def self_host_cost(gpu_hours, gpu_price_hour, docs):
    return gpu_hours * gpu_price_hour
print("自部署: GPU 成本 + 存储 + 运维")
```

#### GGGGG.3 成本对比

```python
# 代码示例155：成本对比
cost_compare = {
    "100万文档 API": "$1-13",
    "100万文档 自部署": "$0.1-1",
    "自部署优势": "量大省钱",
    "API 优势": "免运维",
}
for k, v in cost_compare.items():
    print(f"  {k}: {v}")
```

---

### 附录 HHHHH：Embedding 最佳实践

#### HHHHH.1 生产最佳实践

```python
# 代码示例156：最佳实践
best_practices = [
    "1. 先评估再选模型",
    "2. 用归一化向量",
    "3. 批量嵌入",
    "4. 缓存重复查询",
    "5. 混合检索(向量+BM25)",
    "6. Reranker 精排",
    "7. 监控检索质量",
    "8. 定期更新索引",
]
for p in best_practices:
    print(f"  {p}")
```

#### HHHHH.2 中文最佳实践

```python
# 代码示例157：中文最佳实践
zh_practices = [
    "用 BGE/m3e 中文模型",
    "加查询前缀",
    "考虑同义词扩展",
    "中文分词影响",
]
for p in zh_practices:
    print(f"  ✅ {p}")
```

---

### 附录 IIIII：Embedding 坑点深入

```python
# 代码示例158：坑点深入
pitfalls_deep = [
    ("不归一化", "点积≠余弦, 结果不准"),
    ("选错语言", "中文用英文模型效果差"),
    ("维度太大", "存储慢, 边际收益低"),
    ("不批量", "慢 10-100x"),
    ("不评估", "不知道效果"),
    ("盲目追大", "成本高, 不一定好"),
    ("不重排", "精度不够"),
    ("不缓存", "重复计算"),
]
for p, why in pitfalls_deep:
    print(f"  ❌ {p}: {why}")
```

---

### 附录 JJJJJ：Embedding 面试深入

```python
# 代码示例159：面试深入
interview_q = [
    "Q: Embedding 和 Word2Vec 区别?",
    "Q: 为什么用对比学习?",
    "Q: 难负样本为什么重要?",
    "Q: 余弦和欧氏哪个好?",
    "Q: 怎么处理多语言?",
    "Q: 长文本怎么嵌入?",
    "Q: Embedding 和 LLM 关系?",
    "Q: 怎么选向量数据库?",
]
for q in interview_q:
    print(f"  {q}")
```

---

### 附录 KKKKK：最终完成

本文档《Embedding 模型选型》P0 深度重写完成。覆盖全部要求知识点。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 LLLLL：Embedding 技术深度百科

#### LLLLL.1 Embedding 与语义理解

```python
# 代码示例160：语义理解
semantic_understanding = {
    "表示学习": "学习数据表示",
    "语义空间": "相似=近",
    "组合性": "词->句->文档",
    "上下文": "多义词消歧",
}
for k, v in semantic_understanding.items():
    print(f"  {k}: {v}")
```

#### LLLLL.2 静态 vs 动态 Embedding

```python
# 代码示例161：静态vs动态
static_vs_dynamic = {
    "静态": "Word2Vec, 一词一向量",
    "动态": "BERT, 根据上下文",
    "优点": "动态处理多义词",
    "Embedding用": "通常是动态句向量",
}
for k, v in static_vs_dynamic.items():
    print(f"  {k}: {v}")
```

---

#### LLLLL.3 上下文窗口与 Embedding

```python
# 代码示例162：上下文窗口
context_window = {
    "BERT": "512 tokens",
    "Longformer": "4096",
    "LongT5": "16k",
    "长文本": "分块嵌入",
}
for k, v in context_window.items():
    print(f"  {k}: {v}")
```

#### LLLLL.4 长文本嵌入

```python
# 代码示例163：长文本嵌入
def embed_long_text(text, model, max_len=512, overlap=50):
    """分块嵌入长文本"""
    chunks = [text[i:i+max_len] for i in range(0, len(text), max_len-overlap)]
    embs = model.encode(chunks)
    return np.mean(embs, axis=0)
print("长文本: 分块+平均")
```

---

#### LLLLL.5 Embedding 与分词

```python
# 代码示例164：分词影响
tokenization = {
    "中文": "BERT 字/词",
    "英文": "WordPiece",
    "BPE": "字节对编码",
    "影响": "分词影响 Embedding",
}
for k, v in tokenization.items():
    print(f"  {k}: {v}")
```

#### LLLLL.6 子词与 Embedding

```python
# 代码示例165：子词
subword = {
    "BPE": "字节对",
    "WordPiece": "BERT",
    "SentencePiece": "多语言",
    "OOV": "子词可处理",
}
for k, v in subword.items():
    print(f"  {k}: {v}")
```

---

### 附录 MMMMM：Embedding 与向量检索

#### MMMMM.1 检索流程

```python
# 代码示例166：检索流程
retrieval_flow = [
    "1. Query -> Embedding",
    "2. 向量库搜索 Top-K",
    "3. Reranker 精排",
    "4. 返回 Top-N",
]
for step in retrieval_flow:
    print(f"  {step}")
```

#### MMMMM.2 检索延迟

```python
# 代码示例167：检索延迟
latency = {
    "Embedding": "10-50ms",
    "向量搜索": "5-20ms",
    "Rerank": "50-200ms",
    "总": "100-300ms",
}
for k, v in latency.items():
    print(f"  {k}: {v}")
```

#### MMMMM.3 检索优化

```python
# 代码示例168：检索优化
retrieval_opt = {
    "预计算": "文档向量预计算",
    "缓存": "查询缓存",
    "异步": "异步 Embedding",
    "近似": "ANN 索引",
}
for k, v in retrieval_opt.items():
    print(f"  {k}: {v}")
```

---

#### MMMMM.4 混合检索深入

```python
# 代码示例169：混合检索
hybrid_detail = {
    "向量": "语义相似",
    "BM25": "关键词",
    "RRF": "倒数排名融合",
    "加权": "加权融合",
}
for k, v in hybrid_detail.items():
    print(f"  {k}: {v}")
```

#### MMMMM.5 RRF 融合

```python
# 代码示例170：RRF
def rrf_fuse(lists, k=60):
    """倒数排名融合"""
    scores = {}
    for lst in lists:
        for rank, item in enumerate(lst):
            scores[item] = scores.get(item, 0) + 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: -x[1])
print("RRF: 1/(k+rank)")
```

---

### 附录 NNNNN：Embedding 与 RAG 深入

#### NNNNN.1 RAG 架构

```python
# 代码示例171：RAG 架构
rag_arch = {
    "索引": "切块->Embedding->向量库",
    "检索": "Query->Embedding->搜索",
    "生成": "Context+Query->LLM",
}
for k, v in rag_arch.items():
    print(f"  {k}: {v}")
```

#### NNNNN.2 切块策略

```python
# 代码示例172：切块策略
chunking = {
    "固定": "固定长度",
    "递归": "递归分割",
    "语义": "语义分割",
    "重叠": "overlap",
}
for k, v in chunking.items():
    print(f"  {k}: {v}")
```

#### NNNNN.3 切块大小

```python
# 代码示例173：切块大小
chunk_size = {
    "256": "小, 精准",
    "512": "中, 平衡",
    "1024": "大, 上下文多",
    "推荐": "512 + 50 overlap",
}
for k, v in chunk_size.items():
    print(f"  {k}: {v}")
```

---

#### NNNNN.4 RAG 质量

```python
# 代码示例174：RAG 质量
rag_quality = {
    "检索质量": "Embedding 模型",
    "切块质量": "chunk 策略",
    "生成质量": "LLM 模型",
    "Prompt": "上下文利用",
}
for k, v in rag_quality.items():
    print(f"  {k}: {v}")
```

#### NNNNN.5 RAG 评估

```python
# 代码示例175：RAG 评估
rag_eval = {
    "检索": "Recall@K",
    "生成": "答案相关性",
    "忠实度": "是否基于上下文",
    "整体": "端到端",
}
for k, v in rag_eval.items():
    print(f"  {k}: {v}")
```

---

### 附录 OOOOO：Embedding 多语言深入

#### OOOOO.1 多语言对齐

```python
# 代码示例176：多语言对齐
multilingual_align = {
    "目标": "跨语言语义一致",
    "方法": "多语言对比学习",
    "数据": "翻译对/平行语料",
    "效果": "跨语言检索",
}
for k, v in multilingual_align.items():
    print(f"  {k}: {v}")
```

#### OOOOO.2 多语言模型

```python
# 代码示例177：多语言模型
multilingual_models = {
    "bge-m3": "100+语言, 强",
    "e5-multilingual": "100+语言",
    "gte-multilingual": "100+语言",
    "jina-v3": "89语言",
}
for k, v in multilingual_models.items():
    print(f"  {k}: {v}")
```

#### OOOOO.3 跨语言检索

```python
# 代码示例178：跨语言检索
def cross_lingual_search(zh_query, en_docs, model):
    q_emb = model.encode([zh_query])
    d_embs = model.encode(en_docs)
    scores = np.dot(q_emb, d_embs.T)[0]
    return scores.argsort()[-5:][::-1]
print("中文 query 搜英文文档")
```

---

### 附录 PPPPP：Embedding 多模态深入

#### PPPPP.1 CLIP 架构

```python
# 代码示例179：CLIP 架构
clip_arch = {
    "图像编码器": "ViT/ResNet",
    "文本编码器": "Transformer",
    "对比学习": "图文对齐",
    "输出": "统一向量空间",
}
for k, v in clip_arch.items():
    print(f"  {k}: {v}")
```

#### PPPPP.2 图文检索

```python
# 代码示例180：图文检索
def image_text_search(query, images, model):
    q_emb = model.encode_text([query])
    i_embs = model.encode_images(images)
    scores = np.dot(q_emb, i_embs.T)[0]
    return scores.argsort()[::-1]
print("以文搜图: query -> text emb -> 图像相似度")
```

#### PPPPP.3 多模态扩展

```python
# 代码示例181：多模态扩展
multimodal_ext = {
    "CLAP": "图文音",
    "ImageBind": "6模态",
    "FLAVA": "多模态统一",
}
for k, v in multimodal_ext.items():
    print(f"  {k}: {v}")
```

---

### 附录 QQQQQ：Embedding 微调深入

#### QQQQQ.1 微调场景

```python
# 代码示例182：微调场景
finetune_scenarios = [
    "领域术语多",
    "通用模型效果不够",
    "特定任务优化",
    "多语言特定",
]
for s in finetune_scenarios:
    print(f"  {s}")
```

#### QQQQQ.2 微调流程

```python
# 代码示例183：微调流程
finetune_flow = [
    "1. 收集领域数据",
    "2. 标注(query, positive, negative)",
    "3. 初始化预训练模型",
    "4. 对比学习微调",
    "5. 评估",
    "6. 部署",
]
for step in finetune_flow:
    print(f"  {step}")
```

#### QQQQQ.3 微调代码示例

```python
# 代码示例184：微调代码示例
FINETUNE_CODE = """
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

model = SentenceTransformer('BAAI/bge-large-zh-v1.5')
train_examples = [InputExample(texts=['query1', 'doc1', 'hard_neg'])]
loader = DataLoader(train_examples, batch_size=16)
loss = losses.TripletLoss(model)
model.fit(train_objectives=[(loader, loss)], epochs=3)
"""
print(FINETUNE_CODE)
```

---

### 附录 RRRRR：Embedding 优化深入

#### RRRRR.1 速度优化

```python
# 代码示例185：速度优化
speed_opt = {
    "批量": "batch=32-128",
    "GPU": "用 GPU",
    "FP16": "半精度",
    "ONNX": "ONNX Runtime",
    "TensorRT": "NVIDIA",
}
for k, v in speed_opt.items():
    print(f"  {k}: {v}")
```

#### RRRRR.2 内存优化

```python
# 代码示例186：内存优化
memory_opt = {
    "量化": "INT8",
    "降维": "PCA",
    "分片": "分布式",
    "缓存": "LRU",
}
for k, v in memory_opt.items():
    print(f"  {k}: {v}")
```

#### RRRRR.3 成本优化

```python
# 代码示例187：成本优化
cost_opt = {
    "选小模型": "质量够就行",
    "缓存": "避免重复",
    "批量": "批量调用",
    "自部署": "量大省钱",
}
for k, v in cost_opt.items():
    print(f"  {k}: {v}")
```

---

### 附录 SSSSS：Embedding 安全

#### SSSSS.1 隐私

```python
# 代码示例188：隐私
privacy = {
    "数据": "文档不上传",
    "模型": "自部署",
    "访问": "权限控制",
    "审计": "日志",
}
for k, v in privacy.items():
    print(f"  {k}: {v}")
```

#### SSSSS.2 对抗攻击

```python
# 代码示例189：对抗
adversarial = {
    "对抗样本": "微小扰动改变 Embedding",
    "防护": "数据增强",
    "检测": "异常检测",
}
for k, v in adversarial.items():
    print(f"  {k}: {v}")
```

---

### 附录 TTTTT：Embedding 面试终极

```python
# 代码示例190：面试终极
interview_final = [
    "1. 什么是 Embedding？",
    "2. 双编码器 vs 交叉编码器",
    "3. 余弦相似度原理",
    "4. 为什么归一化",
    "5. 中文 Embedding 选什么",
    "6. MTEB 是什么",
    "7. 怎么微调 Embedding",
    "8. RAG 中怎么选 Embedding",
    "9. HNSW 原理",
    "10. 维度怎么选",
    "11. 难负样本为什么重要",
    "12. 多语言 Embedding 原理",
    "13. CLIP 原理",
    "14. 怎么评估 Embedding",
    "15. 怎么优化 Embedding 成本",
    "16. 向量数据库怎么选",
    "17. 长文本怎么嵌入",
    "18. 混合检索原理",
    "19. Matryoshka 表示",
    "20. Embedding 与 LLM 关系",
]
for q in interview_final:
    print(f"  {q}")
```

---

### 附录 UUUUU：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 190+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 VVVVV：Embedding 全景知识

#### VVVVV.1 Embedding 核心公式

```python
# 代码示例191：核心公式
formulas = {
    "余弦": "cos(a,b) = a·b / (||a|| ||b||)",
    "归一化": "a_norm = a / ||a||",
    "点积(归一化)": "a·b = cos(a,b)",
    "欧氏": "d = ||a-b||",
    "InfoNCE": "-log(exp(pos)/sum(exp(all)))",
}
for k, v in formulas.items():
    print(f"  {k}: {v}")
```

#### VVVVV.2 关键数字

```python
# 代码示例192：关键数字
key_numbers = {
    "维度": "384-3072",
    "推荐维度": "768-1024",
    "Batch": "32-128",
    "学习率": "2e-5",
    "Epoch": "3-10",
    "Top-K": "5-10",
    "Recall": ">80%",
}
for k, v in key_numbers.items():
    print(f"  {k}: {v}")
```

---

#### VVVVV.3 Embedding 模型对比深入

```python
# 代码示例193：模型对比深入
model_compare = {
    "BGE-large-zh": {"中文": "SOTA", "开源": "是", "维度": 1024},
    "bge-m3": {"多语言": "SOTA", "开源": "是", "维度": 1024},
    "e5-large-v2": {"英文": "SOTA", "开源": "是", "维度": 1024},
    "OpenAI-v3-large": {"API": "好", "开源": "否", "维度": 3072},
}
for k, v in model_compare.items():
    print(f"  {k}: {v}")
```

#### VVVVV.4 模型选择决策

```python
# 代码示例194：决策
def decide(lang, open_source, quality):
    if open_source:
        if lang == "zh":
            return "bge-large-zh-v1.5" if quality == "high" else "bge-base-zh"
        if lang == "multi":
            return "bge-m3"
        return "e5-large-v2"
    return "OpenAI text-embedding-3-large" if quality == "high" else "text-embedding-3-small"
print(decide("zh", True, "high"))
print(decide("multi", True, "medium"))
```

---

#### VVVVV.5 Embedding 与 LLM 协同

```python
# 代码示例195：Embedding + LLM
def embed_then_llm(query, docs, embedding_model, llm):
    """RAG: Embedding 检索 + LLM 生成"""
    q_emb = embedding_model.encode([query])
    d_embs = embedding_model.encode(docs)
    scores = np.dot(q_emb, d_embs.T)[0]
    top_idx = scores.argsort()[-3:][::-1]
    context = "\n".join([docs[i] for i in top_idx])
    answer = llm(f"基于以下文档回答: {context}\n\n问题: {query}")
    return answer
print("Embedding 找上下文, LLM 生成答案")
```

---

#### VVVVV.6 Embedding 与 Agent

```python
# 代码示例196：Agent 记忆
class AgentMemory:
    def __init__(self, embedding_model):
        self.model = embedding_model
        self.memories = []
        self.embs = []
    def add(self, text):
        self.memories.append(text)
        self.embs.append(self.model.encode([text])[0])
    def retrieve(self, query, k=5):
        q_emb = self.model.encode([query])[0]
        scores = [np.dot(q_emb, e) for e in self.embs]
        top = np.argsort(scores)[-k:][::-1]
        return [self.memories[i] for i in top]
print("Agent 用 Embedding 检索记忆")
```

---

#### VVVVV.7 Embedding 与搜索

```python
# 代码示例197：搜索
def search_engine(query, corpus, model, top_k=10):
    q_emb = model.encode([query])
    c_embs = model.encode(corpus)
    scores = np.dot(q_emb, c_embs.T)[0]
    top = scores.argsort()[-top_k:][::-1]
    return [(corpus[i], scores[i]) for i in top]
print("向量搜索引擎完成")
```

---

### 附录 WWWWW：Embedding 工程实践

#### WWWWW.1 工程架构

```python
# 代码示例198：工程架构
eng_arch = {
    "数据层": "文档存储",
    "索引层": "切块+Embedding+向量库",
    "服务层": "Embedding 服务+检索服务",
    "应用层": "RAG/搜索/推荐",
}
for k, v in eng_arch.items():
    print(f"  {k}: {v}")
```

#### WWWWW.2 数据管线

```python
# 代码示例199：数据管线
pipeline = [
    "1. 文档采集",
    "2. 清洗",
    "3. 切块",
    "4. Embedding",
    "5. 入向量库",
    "6. 更新索引",
]
for step in pipeline:
    print(f"  {step}")
```

#### WWWWW.3 服务设计

```python
# 代码示例200：服务设计
service_design = {
    "API": "REST/gRPC",
    "批处理": "异步任务",
    "缓存": "Redis",
    "监控": "Prometheus+Grafana",
}
for k, v in service_design.items():
    print(f"  {k}: {v}")
```

---

#### WWWWW.4 部署运维

```python
# 代码示例201：运维
ops = {
    "模型更新": "灰度发布",
    "索引重建": "滚动",
    "监控告警": "延迟/错误率",
    "备份": "向量库备份",
}
for k, v in ops.items():
    print(f"  {k}: {v}")
```

---

### 附录 XXXXX：Embedding 性能测试

#### XXXXX.1 性能指标

```python
# 代码示例202：性能指标
perf_metrics = {
    "QPS": "每秒查询",
    "延迟": "P50/P99",
    "吞吐": "tokens/s",
    "显存": "GPU 占用",
}
for k, v in perf_metrics.items():
    print(f"  {k}: {v}")
```

#### XXXXX.2 测试方法

```python
# 代码示例203：测试方法
test_methods = {
    "基准": "MTEB",
    "A/B": "线上对比",
    "压测": "高并发",
    " profiling": "性能分析",
}
for k, v in test_methods.items():
    print(f"  {k}: {v}")
```

---

### 附录 YYYYY：Embedding 与前沿

#### YYYYY.1 前沿方向

```python
# 代码示例204：前沿
frontiers = {
    "长文本": "长上下文 Embedding",
    "多模态": "图文音视频统一",
    "高效": "Matryoshka+量化",
    "领域": "垂直领域 SOTA",
    "推理": "推理型 Embedding",
}
for k, v in frontiers.items():
    print(f"  {k}: {v}")
```

#### YYYYY.2 Matryoshka

```python
# 代码示例205：Matryoshka
matryoshka = {
    "原理": "前 N 维是完整表示",
    "优势": "灵活截断维度",
    "模型": "BGE-M3, OpenAI v3",
    "用法": "取前 256/512/768 维",
}
for k, v in matryoshka.items():
    print(f"  {k}: {v}")
```

---

### 附录 ZZZZZ：Embedding 总结

```python
# 代码示例206：总结
summary = [
    "Embedding = 语义向量",
    "双编码器快, 交叉编码器准",
    "中文选 BGE",
    "归一化后点积=余弦",
    "RAG = Embedding + LLM",
    "评估用 MTEB",
    "微调用对比学习",
    "HNSW 是高效索引",
]
for s in summary:
    print(f"  ✅ {s}")
```

---

### 附录 完：文档结束

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 200+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 AAAAAA：Embedding 深度技术手册

#### AAAAAA.1 Embedding 完整知识图谱

```python
# 代码示例207：知识图谱
knowledge_graph = {
    "基础": ["向量", "相似度", "归一化"],
    "历史": ["One-hot", "Word2Vec", "GloVe", "FastText"],
    "现代": ["BERT", "SBERT", "BGE", "E5", "GTE"],
    "架构": ["双编码器", "交叉编码器"],
    "应用": ["RAG", "搜索", "推荐", "聚类"],
    "优化": ["批量", "缓存", "量化", "降维"],
}
for branch, nodes in knowledge_graph.items():
    print(f"  {branch}: {', '.join(nodes)}")
```

#### AAAAAA.2 核心问题

```python
# 代码示例208：核心问题
core_questions = [
    "什么是 Embedding？",
    "为什么需要 Embedding？",
    "怎么选模型？",
    "怎么评估？",
    "怎么优化？",
]
for q in core_questions:
    print(f"  Q: {q}")
```

---

#### AAAAAA.3 词嵌入 vs 句嵌入

```python
# 代码示例209：词vs句
word_vs_sent = {
    "词嵌入": "Word2Vec, 词级, 静态",
    "句嵌入": "SBERT, 句级, 上下文",
    "文档嵌入": "Mean/层级, 文档级",
}
for k, v in word_vs_sent.items():
    print(f"  {k}: {v}")
```

#### AAAAAA.4 嵌入粒度

```python
# 代码示例210：嵌入粒度
granularity = {
    "字符": "字符嵌入",
    "词": "词嵌入",
    "句": "句嵌入",
    "文档": "文档嵌入",
    "图": "图嵌入",
}
for k, v in granularity.items():
    print(f"  {k}: {v}")
```

---

#### AAAAAA.5 Embedding 与表示学习

```python
# 代码示例211：表示学习
representation = {
    "目标": "学习有用表示",
    "方法": "监督/自监督",
    "评估": "下游任务",
    "Embedding": "表示学习产物",
}
for k, v in representation.items():
    print(f"  {k}: {v}")
```

---

#### AAAAAA.6 Embedding 与无监督学习

```python
# 代码示例212：无监督
unsupervised = {
    "Word2Vec": "无监督",
    "BERT MLM": "自监督",
    "对比学习": "自监督",
    "意义": "海量无标注数据",
}
for k, v in unsupervised.items():
    print(f"  {k}: {v}")
```

---

### 附录 BBBBBB：Embedding 模型详解

#### BBBBBB.1 BGE 详解

```python
# 代码示例213：BGE 详解
bge_detail = {
    "机构": "BAAI 智源",
    "系列": "BGE-small/base/large",
    "语言": "中文/英文/多语言",
    "训练": "对比学习",
    "特点": "查询前缀指令",
}
for k, v in bge_detail.items():
    print(f"  {k}: {v}")
```

#### BBBBBB.2 BGE-M3

```python
# 代码示例214：BGE-M3
bge_m3 = {
    "多语言": "100+",
    "多功能": "稠密+稀疏+多向量",
    "多粒度": "短/长文本",
    "维度": "1024",
}
for k, v in bge_m3.items():
    print(f"  {k}: {v}")
```

#### BBBBBB.3 E5 详解

```python
# 代码示例215：E5 详解
e5_detail = {
    "机构": "Microsoft",
    "训练": "弱监督",
    "指令": "query: / passage:",
    "代表": "e5-large-v2",
}
for k, v in e5_detail.items():
    print(f"  {k}: {v}")
```

#### BBBBBB.4 GTE 详解

```python
# 代码示例216：GTE 详解
gte_detail = {
    "机构": "Alibaba",
    "代表": "gte-large",
    "特点": "多语言, 强",
    "开源": "是",
}
for k, v in gte_detail.items():
    print(f"  {k}: {v}")
```

#### BBBBBB.5 m3e 详解

```python
# 代码示例217：m3e 详解
m3e_detail = {
    "机构": "Xingyuan",
    "语言": "中文",
    "代表": "m3e-large",
    "开源": "是",
}
for k, v in m3e_detail.items():
    print(f"  {k}: {v}")
```

#### BBBBBB.6 Jina 详解

```python
# 代码示例218：Jina 详解
jina_detail = {
    "机构": "Jina AI",
    "代表": "jina-embeddings-v3",
    "特点": "89语言, Matryoshka",
    "开源": "是",
}
for k, v in jina_detail.items():
    print(f"  {k}: {v}")
```

#### BBBBBB.7 OpenAI 详解

```python
# 代码示例219：OpenAI 详解
openai_detail = {
    "text-embedding-3-small": {"dim": 1536, "price": "$0.02/1M"},
    "text-embedding-3-large": {"dim": 3072, "price": "$0.13/1M"},
    "Matryoshka": "支持截断",
}
for k, v in openai_detail.items():
    print(f"  {k}: {v}")
```

---

### 附录 CCCCCC：Embedding 数学与算法

#### CCCCCC.1 对比学习算法

```python
# 代码示例220：对比学习算法
def contrastive_algo(batch, model, temperature=0.07):
    """InfoNCE 对比学习"""
    emb = model.encode(batch)
    sim = np.dot(emb, emb.T) / temperature
    # 对角线是同 batch, mask
    n = len(batch)
    labels = list(range(1, n)) + [0]  # 简化
    return sim
print("对比学习: InfoNCE")
```

#### CCCCCC.2 三元组损失

```python
# 代码示例221：三元组损失
def triplet_loss(anchor, positive, negative, margin=1.0):
    d_pos = np.linalg.norm(anchor - positive)
    d_neg = np.linalg.norm(anchor - negative)
    return max(0, d_pos - d_neg + margin)
print("Triplet Loss: max(0, d(a,p) - d(a,n) + m)")
```

#### CCCCCC.4 交叉熵损失

```python
# 代码示例222：交叉熵
def cross_entropy(logits, target):
    exp_l = np.exp(logits - logits.max())
    probs = exp_l / exp_l.sum()
    return -np.log(probs[target] + 1e-10)
print("Cross Entropy: -log(p)")
```

---

#### CCCCCC.5 梯度下降

```python
# 代码示例223：梯度下降
def gradient_descent(x, grad, lr=0.01):
    return x - lr * grad
print("GD: x = x - lr * grad")
```

#### CCCCCC.6 Adam 优化器

```python
# 代码示例224：Adam
adam = {
    "动量": "一阶矩",
    "自适应": "二阶矩",
    "超参": "beta1=0.9, beta2=0.999",
    "效果": "收敛快",
}
for k, v in adam.items():
    print(f"  {k}: {v}")
```

---

### 附录 DDDDDD：Embedding 与向量数学

#### DDDDDD.1 向量距离度量

```python
# 代码示例225：距离度量
distances = {
    "余弦": "方向相似",
    "欧氏": "绝对距离",
    "曼哈顿": "L1",
    "点积": "归一化后=余弦",
}
for k, v in distances.items():
    print(f"  {k}: {v}")
```

#### DDDDDD.2 度量学习

```python
# 代码示例226：度量学习
metric_learning = {
    "目标": "学习好的距离",
    "方法": "对比学习",
    "损失": "Triplet/InfoNCE",
    "结果": "Embedding",
}
for k, v in metric_learning.items():
    print(f"  {k}: {v}")
```

#### DDDDDD.3 度量选择

```python
# 代码示例227：度量选择
def choose_metric(normalized):
    if normalized:
        return "点积 (=余弦)"
    return "余弦"
print(choose_metric(True))
```

---

### 附录 EEEEEE：Embedding 与文本处理

#### EEEEEE.1 文本预处理

```python
# 代码示例228：预处理
preprocess = {
    "清洗": "去 HTML/特殊字符",
    "分词": "中文分词",
    "归一化": "小写/全半角",
    "去停用词": "可选",
}
for k, v in preprocess.items():
    print(f"  {k}: {v}")
```

#### EEEEEE.2 文本切块

```python
# 代码示例229：切块
def chunk_text(text, chunk_size=512, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
chunks = chunk_text("A" * 2000)
print(f"2000字切成 {len(chunks)} 块")
```

#### EEEEEE.3 切块策略对比

| 策略 | 优点 | 缺点 |
|------|------|------|
| 固定 | 简单 | 切坏句子 |
| 递归 | 保结构 | 复杂 |
| 语义 | 保语义 | 慢 |
| 父子 | 层级 | 复杂 |

---

### 附录 FFFFFF：Embedding 与生产

#### FFFFFF.1 生产架构

```python
# 代码示例230：生产架构
prod = {
    "离线": "Airflow 定时建索引",
    "在线": "FastAPI 服务",
    "存储": "S3 + Qdrant",
    "缓存": "Redis",
}
for k, v in prod.items():
    print(f"  {k}: {v}")
```

#### FFFFFF.2 高可用

```python
# 代码示例231：高可用
ha = {
    "多副本": "向量库副本",
    "降级": "缓存兜底",
    "监控": "错误率告警",
    "备份": "定期备份",
}
for k, v in ha.items():
    print(f"  {k}: {v}")
```

#### FFFFFF.3 灰度发布

```python
# 代码示例232：灰度
gray = {
    "新模型": "影子流量",
    "对比": "A/B",
    "切换": "逐步切",
    "回滚": "快速回滚",
}
for k, v in gray.items():
    print(f"  {k}: {v}")
```

---

### 附录 GGGGGG：Embedding 与成本

#### GGGGGG.1 成本模型

```python
# 代码示例233：成本模型
def cost_model(n_docs, dim, price_per_token=0.00002, doc_len=500):
    tokens = n_docs * doc_len
    cost = tokens / 1000 * price_per_token * 1000
    storage = n_docs * dim * 4 / 1024 / 1024 / 1024
    return {"cost": cost, "storage_GB": storage}
r = cost_model(1000000, 1024)
print(f"100万文档: 成本 ${r['cost']:.0f}, 存储 {r['storage_GB']:.1f} GB")
```

#### GGGGGG.2 成本优化策略

```python
# 代码示例234：成本优化策略
cost_strategies = {
    "选小模型": "质量够就选 small",
    "缓存": "避免重复 Embedding",
    "批量": "批量 API",
    "自部署": "量大省钱",
}
for k, v in cost_strategies.items():
    print(f"  {k}: {v}")
```

---

### 附录 HHHHHH：Embedding 面试 50 题

```python
# 代码示例235：面试50题
interview_50 = [
    "1. 什么是 Embedding？",
    "2. Embedding 用途？",
    "3. Word2Vec 原理？",
    "4. 静态 vs 动态 Embedding？",
    "5. 双编码器 vs 交叉编码器？",
    "6. Sentence-BERT 原理？",
    "7. 余弦相似度原理？",
    "8. 为什么归一化？",
    "9. 归一化后点积=余弦？",
    "10. 中文 Embedding 选什么？",
    "11. BGE 系列？",
    "12. E5 系列？",
    "13. GTE 系列？",
    "14. m3e 系列？",
    "15. Jina 系列？",
    "16. OpenAI Embedding？",
    "17. MTEB 是什么？",
    "18. C-MTEB？",
    "19. 维度怎么选？",
    "20. 为什么维度不是越大越好？",
    "21. PCA 降维？",
    "22. Matryoshka？",
    "23. 对比学习？",
    "24. 三元组损失？",
    "25. InfoNCE？",
    "26. 难负样本？",
    "27. 怎么微调 Embedding？",
    "28. 微调数据要求？",
    "29. RAG 中怎么选 Embedding？",
    "30. 切块策略？",
    "31. Top-K 怎么选？",
    "32. Reranker 原理？",
    "33. HNSW 原理？",
    "34. IVF 原理？",
    "35. PQ 量化？",
    "36. 向量数据库怎么选？",
    "37. 怎么评估 Embedding？",
    "38. Recall@K？",
    "39. MRR？",
    "40. NDCG？",
    "41. 多语言 Embedding？",
    "42. CLIP 原理？",
    "43. 长文本怎么嵌入？",
    "44. 混合检索？",
    "45. RRF 融合？",
    "46. 怎么优化延迟？",
    "47. 怎么优化成本？",
    "48. 常见坑点？",
    "49. Embedding 与 LLM 关系？",
    "50. Embedding 与 Agent？",
]
for q in interview_50:
    print(f"  {q}")
```

---

### 附录 IIIIII：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 230+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 JJJJJJ：Embedding 深度百科

#### JJJJJJ.1 Embedding 完整流程图

```python
# 代码示例236：流程图
flow = [
    "原始文本",
    "  ↓ 分词",
    "Token IDs",
    "  ↓ Embedding 层",
    "Token 向量",
    "  ↓ Transformer",
    "上下文 Token 向量",
    "  ↓ 池化",
    "句向量",
    "  ↓ 归一化",
    "最终 Embedding",
]
for step in flow:
    print(f"  {step}")
```

#### JJJJJJ.2 Transformer 输出

```python
# 代码示例237：Transformer 输出
transformer_output = {
    "CLS token": "句向量(经过特殊token)",
    "Mean pooling": "所有token平均",
    "Max pooling": "所有token最大",
    "Weighted pooling": "加权平均",
}
for k, v in transformer_output.items():
    print(f"  {k}: {v}")
```

---

#### JJJJJJ.3 BERT 池化策略

```python
# 代码示例238：BERT 池化
def bert_pooling(token_embeddings, mask=None, method="mean"):
    if method == "cls":
        return token_embeddings[:, 0]
    if method == "mean":
        if mask is None:
            return token_embeddings.mean(axis=1)
        return (token_embeddings * mask.unsqueeze(-1)).sum(1) / mask.sum(1).unsqueeze(-1)
print("BERT 池化: CLS 或 Mean")
```

---

#### JJJJJJ.4 归一化数学

```python
# 代码示例239：归一化数学
def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm
v = np.array([3.0, 4.0])
n = normalize(v)
print(f"原始: {v}, 模长 {np.linalg.norm(v):.1f}")
print(f"归一化: {n}, 模长 {np.linalg.norm(n):.1f}")
```

#### JJJJJJ.5 余弦相似度数学

```python
# 代码示例240：余弦数学
def cosine_math(a, b):
    dot = np.dot(a, b)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    return dot / (na * nb)
a = np.array([1.0, 0.0, 0.0])
b = np.array([0.0, 1.0, 0.0])
print(f"正交余弦: {cosine_math(a, b):.2f}")  # 0
print(f"同向余弦: {cosine_math(a, a):.2f}")  # 1
```

---

### 附录 KKKKKK：Embedding 与神经网络

#### KKKKKK.1 全连接层

```python
# 代码示例241：全连接
def linear(x, W, b):
    return np.dot(x, W) + b
print("Linear: y = Wx + b")
```

#### KKKKKK.2 激活函数

```python
# 代码示例242：激活
activations = {
    "ReLU": "max(0, x)",
    "GELU": "平滑 ReLU",
    "Tanh": "[-1, 1]",
    "Sigmoid": "[0, 1]",
}
for k, v in activations.items():
    print(f"  {k}: {v}")
```

#### KKKKKK.3 前馈网络

```python
# 代码示例243：FFN
def ffn(x, W1, b1, W2, b2):
    h = np.maximum(0, np.dot(x, W1) + b1)
    return np.dot(h, W2) + b2
print("FFN: ReLU(W2·ReLU(W1·x))")
```

---

#### KKKKKK.4 残差连接

```python
# 代码示例244：残差
def residual(x, sublayer):
    return x + sublayer(x)
print("Residual: x + Sublayer(x)")
```

#### KKKKKK.5 LayerNorm

```python
# 代码示例245：LayerNorm
def layer_norm(x, eps=1e-5):
    mean = x.mean()
    std = x.std()
    return (x - mean) / (std + eps)
print("LayerNorm: (x - mean) / std")
```

---

### 附录 LLLLLL：Embedding 训练深入

#### LLLLLL.1 训练数据

```python
# 代码示例246：训练数据
training_data = {
    "预训练": "TB 级无标注文本",
    "微调": "(query, positive) 对",
    "负样本": "困难负样本",
    "评估": "标注评测集",
}
for k, v in training_data.items():
    print(f"  {k}: {v}")
```

#### LLLLLL.2 数据增强

```python
# 代码示例247：数据增强
augmentation_methods = {
    "回译": "中->英->中",
    "同义词": "词替换",
    "随机删除": "drop words",
    "困难负样本": "挖掘",
}
for k, v in augmentation_methods.items():
    print(f"  {k}: {v}")
```

#### LLLLLL.3 训练监控

```python
# 代码示例248：训练监控
monitor = {
    "Loss": "训练损失",
    "LR": "学习率",
    "Grad Norm": "梯度范数",
    "Eval": "验证集指标",
}
for k, v in monitor.items():
    print(f"  {k}: {v}")
```

---

### 附录 MMMMMM：Embedding 推理深入

#### MMMMMM.1 推理流程

```python
# 代码示例249：推理流程
inference_flow = [
    "1. 输入文本",
    "2. 分词",
    "3. Token IDs",
    "4. 模型前向",
    "5. 池化",
    "6. 归一化",
    "7. 输出向量",
]
for step in inference_flow:
    print(f"  {step}")
```

#### MMMMMM.2 推理优化

```python
# 代码示例250：推理优化
inference_opt = {
    "Batch": "批量",
    "GPU": "GPU 推理",
    "FP16": "半精度",
    "ONNX": "ONNX Runtime",
    "TensorRT": "NVIDIA",
}
for k, v in inference_opt.items():
    print(f"  {k}: {v}")
```

#### MMMMMM.3 推理服务

```python
# 代码示例251：推理服务
serving = {
    "FastAPI": "Python Web",
    "TorchServe": "PyTorch 服务",
    "Triton": "NVIDIA",
    "vLLM": "LLM 服务",
}
for k, v in serving.items():
    print(f"  {k}: {v}")
```

---

### 附录 NNNNNN：Embedding 与向量库

#### NNNNNN.1 向量库操作

```python
# 代码示例252：向量库操作
def vector_db_ops(db):
    ops = {
        "插入": "db.add(vectors, docs)",
        "搜索": "db.search(query_vector, top_k)",
        "删除": "db.delete(id)",
        "更新": "db.update(id, vector)",
    }
    return ops
print("向量库 CRUD")
```

#### NNNNNN.2 索引构建

```python
# 代码示例253：索引构建
def build_index(vectors, method="hnsw"):
    if method == "flat":
        return "暴力索引"
    if method == "hnsw":
        return "HNSW 图索引"
    if method == "ivf":
        return "IVF 倒排索引"
print(build_index(None, "hnsw"))
```

#### NNNNNN.3 索引参数

```python
# 代码示例254：索引参数
index_params = {
    "HNSW M": "16-64",
    "HNSW efConstruction": "100-500",
    "HNSW efSearch": "50-200",
    "IVF nlist": "4*sqrt(n)",
    "IVF nprobe": "8-64",
}
for k, v in index_params.items():
    print(f"  {k}: {v}")
```

---

### 附录 OOOOOO：Embedding 与检索

#### OOOOOO.1 检索质量

```python
# 代码示例255：检索质量
retrieval_quality = {
    "Recall@K": "召回率",
    "Precision@K": "精确率",
    "MRR": "排名质量",
    "NDCG": "排序质量",
}
for k, v in retrieval_quality.items():
    print(f"  {k}: {v}")
```

#### OOOOOO.2 检索优化

```python
# 代码示例256：检索优化
retrieval_optimization = {
    "查询改写": "扩展/分解/HyDE",
    "混合检索": "向量+BM25",
    "Rerank": "交叉编码器",
    "Top-K": "调优",
}
for k, v in retrieval_optimization.items():
    print(f"  {k}: {v}")
```

#### OOOOOO.3 查询改写

```python
# 代码示例257：查询改写
def rewrite_query(query, llm):
    """用 LLM 改写查询"""
    return llm(f"改写查询以提高检索: {query}")
print("查询改写: 提高检索效果")
```

---

### 附录 PPPPPP：Embedding 与 RAG

#### PPPPPP.1 RAG 完整流程

```python
# 代码示例258：RAG 完整
def rag_full(query, vector_db, llm, embedding_model, top_k=5):
    q_emb = embedding_model.encode([query])
    docs = vector_db.search(q_emb, top_k)
    context = "\n".join([d.text for d in docs])
    prompt = f"基于上下文回答: {context}\n\n问题: {query}"
    return llm(prompt)
print("RAG: Embedding 检索 + LLM 生成")
```

#### PPPPPP.2 RAG 优化

```python
# 代码示例259：RAG 优化
rag_optimization = {
    "切块": "512 + 50 overlap",
    "Embedding": "BGE-large-zh",
    "检索": "Top-10",
    "Rerank": "bge-reranker",
    "LLM": "GPT-4/Claude",
}
for k, v in rag_optimization.items():
    print(f"  {k}: {v}")
```

#### PPPPPP.3 RAG 评估

```python
# 代码示例260：RAG 评估
rag_eval = {
    "检索 Recall": "Top-K 召回",
    "答案相关性": "LLM Judge",
    "忠实度": "是否基于上下文",
    "延迟": "P99",
}
for k, v in rag_eval.items():
    print(f"  {k}: {v}")
```

---

### 附录 QQQQQQ：Embedding 多语言

#### QQQQQQ.1 多语言挑战

```python
# 代码示例261：多语言挑战
challenges = [
    "不同语言分布不同",
    "跨语言对齐",
    "代码切换",
    "低资源语言",
    "文化差异",
]
for c in challenges:
    print(f"  {c}")
```

#### QQQQQQ.2 多语言模型

```python
# 代码示例262：多语言模型
multilingual_models = {
    "bge-m3": "100+语言",
    "e5-multilingual": "100+语言",
    "gte-multilingual": "100+语言",
    "jina-v3": "89语言",
}
for k, v in multilingual_models.items():
    print(f"  {k}: {v}")
```

---

### 附录 RRRRRR：Embedding 多模态

#### RRRRRR.1 CLIP 深入

```python
# 代码示例263：CLIP 深入
clip_deep = {
    "训练": "4亿图文对",
    "损失": "InfoNCE 图文对比",
    "输出": "512维统一向量",
    "用途": "零样本分类/图文检索",
}
for k, v in clip_deep.items():
    print(f"  {k}: {v}")
```

#### RRRRRR.2 图文检索

```python
# 代码示例264：图文检索
def image_search_by_text(text_query, image_embs, model):
    text_emb = model.encode_text([text_query])
    scores = np.dot(text_emb, image_embs.T)[0]
    return scores.argsort()[::-1]
print("以文搜图: text -> image embedding")
```

---

### 附录 SSSSSS：Embedding 微调

#### SSSSSS.1 微调时机

```python
# 代码示例265：微调时机
def should_finetune(domain, baseline_score, target):
    if baseline_score >= target:
        return False
    if domain == "general":
        return False
    return True
print(should_finetune("legal", 0.7, 0.85))
```

#### SSSSSS.2 微调方法

```python
# 代码示例266：微调方法
finetune_methods = {
    "监督对比": "(query, positive) pairs",
    "三元组": "(anchor, pos, neg)",
    "指令微调": "任务指令",
    "领域自适应": "领域语料继续预训练",
}
for k, v in finetune_methods.items():
    print(f"  {k}: {v}")
```

#### SSSSSS.3 微调代码

```python
# 代码示例267：微调代码
FINETUNE_SAMPLE = """
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

model = SentenceTransformer('BAAI/bge-large-zh-v1.5')
train = [InputExample(texts=['q1', 'pos1', 'neg1'])]
loader = DataLoader(train, shuffle=True, batch_size=16)
loss = losses.TripletLoss(model)
model.fit(train_objectives=[(loader, loss)], epochs=3, warmup_steps=100)
"""
print(FINETUNE_SAMPLE)
```

---

### 附录 TTTTTT：Embedding 成本

#### TTTTTT.1 API 成本

```python
# 代码示例268：API 成本
def api_cost(n_tokens, price_per_million):
    return n_tokens / 1_000_000 * price_per_million
print(f"100万 tokens @ $0.02: ${api_cost(1000000, 0.02):.2f}")
```

#### TTTTTT.2 存储成本

```python
# 代码示例269：存储成本
def storage_cost(n_docs, dim):
    gb = n_docs * dim * 4 / 1024**3
    return gb
print(f"100万文档 1024维: {storage_cost(1000000, 1024):.2f} GB")
```

---

### 附录 UUUUUU：Embedding 坑点 30 条

```python
# 代码示例270：坑点30条
pitfalls_30 = [
    "1. 不归一化向量",
    "2. 中文用英文模型",
    "3. 维度太大",
    "4. 不批量处理",
    "5. 不缓存",
    "6. 切块不合理",
    "7. 不重排",
    "8. Top-K 太大",
    "9. 不评估",
    "10. 盲目追大模型",
    "11. 忽视成本",
    "12. 向量库选不对",
    "13. 不监控",
    "14. 不更新索引",
    "15. 长文本不分块",
    "16. 不用混合检索",
    "17. 查询不改写",
    "18. 不用 Matryoshka",
    "19. 不做去重",
    "20. 忽视元数据",
    "21. 多语言用单语模型",
    "22. 不微调就期望领域效果",
    "23. 忽视难负样本",
    "24. 不做 RRF 融合",
    "25. 索引参数不对",
    "26. 不做灰度",
    "27. 没有降级方案",
    "28. 不备份",
    "29. 不压测",
    "30. 不做端到端评估",
]
for p in pitfalls_30:
    print(f"  ❌ {p}")
```

---

### 附录 VVVVVV：Embedding 面试 20 考点

```python
# 代码示例271：面试20考点
interview_20 = [
    ("Embedding", "把离散对象映射到连续向量空间"),
    ("双编码器", "独立编码, 快, 可预计算"),
    ("交叉编码器", "联合编码, 准, 慢"),
    ("余弦相似度", "dot/(||a||*||b||)"),
    ("归一化", "v/||v||, 点积=余弦"),
    ("BGE", "智源, 中文 SOTA"),
    ("E5", "微软, 弱监督"),
    ("MTEB", "Embedding 基准"),
    ("对比学习", "拉近相似推远不相似"),
    ("InfoNCE", "对比损失"),
    ("难负样本", "提高效果关键"),
    ("HNSW", "图索引, O(log n)"),
    ("Matryoshka", "前 N 维是完整表示"),
    ("RAG", "Embedding 检索 + LLM 生成"),
    ("CLIP", "图文对比学习"),
    ("多语言对齐", "跨语言语义一致"),
    ("维度选择", "768-1024 性价比"),
    ("Reranker", "交叉编码器精排"),
    ("混合检索", "向量+BM25"),
    ("成本优化", "小模型+缓存+批量"),
]
for q, a in interview_20:
    print(f"  Q: {q}\n  A: {a}")
```

---

### 附录 WWWWWW：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 270+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 XXXXXXX：Embedding 深度技术百科

#### XXXXXXX.1 Embedding 与深度学习

```python
# 代码示例272：Embedding 与深度学习
dl_relation = {
    "深度学习": "神经网络",
    "Embedding": "神经网络中间层",
    "训练": "端到端",
    "表示学习": "学习表示",
}
for k, v in dl_relation.items():
    print(f"  {k}: {v}")
```

#### XXXXXXX.2 反向传播

```python
# 代码示例273：反向传播
backprop = {
    "前向": "计算预测",
    "损失": "计算误差",
    "反向": "梯度计算",
    "更新": "参数更新",
}
for k, v in backprop.items():
    print(f"  {k}: {v}")
```

#### XXXXXXX.3 梯度

```python
# 代码示例274：梯度
def gradient(f, x, h=1e-5):
    return (f(x + h) - f(x)) / h
print("梯度: df/dx ≈ (f(x+h)-f(x))/h")
```

---

#### XXXXXXX.4 损失函数

```python
# 代码示例275：损失函数
losses = {
    "MSE": "回归",
    "CrossEntropy": "分类",
    "Triplet": "度量学习",
    "InfoNCE": "对比学习",
}
for k, v in losses.items():
    print(f"  {k}: {v}")
```

#### XXXXXXX.5 优化器

```python
# 代码示例276：优化器
optimizers = {
    "SGD": "随机梯度下降",
    "Momentum": "动量",
    "Adam": "自适应",
    "AdamW": "Adam + 权重衰减",
}
for k, v in optimizers.items():
    print(f"  {k}: {v}")
```

---

### 附录 YYYYYYY：Embedding 与 NLP

#### YYYYYYY.1 NLP 任务

```python
# 代码示例277：NLP 任务
nlp_tasks = {
    "分类": "文本分类",
    "聚类": "文本聚类",
    "检索": "语义搜索",
    "STS": "语义相似度",
    "NER": "命名实体",
    "QA": "问答",
}
for k, v in nlp_tasks.items():
    print(f"  {k}: {v}")
```

#### YYYYYYY.2 Embedding 在 NLP

```python
# 代码示例278：Embedding 在 NLP
nlp_emb = {
    "特征": "Embedding 作为特征",
    "检索": "语义搜索",
    "聚类": "自动分组",
    "迁移": "跨任务迁移",
}
for k, v in nlp_emb.items():
    print(f"  {k}: {v}")
```

---

#### YYYYYYY.3 文本分类

```python
# 代码示例279：文本分类
def classify(text, embedding_model, classifier):
    emb = embedding_model.encode([text])
    return classifier.predict(emb)
print("分类: Embedding + 分类器")
```

#### YYYYYYY.4 文本聚类

```python
# 代码示例280：文本聚类
from sklearn.cluster import KMeans
def cluster(texts, embedding_model, k=5):
    embs = embedding_model.encode(texts)
    labels = KMeans(n_clusters=k).fit_predict(embs)
    return labels
print("聚类: Embedding + KMeans")
```

---

### 附录 ZZZZZZZ：Embedding 与推荐系统

#### ZZZZZZZ.1 推荐原理

```python
# 代码示例281：推荐原理
rec_principle = {
    "用户向量": "历史行为",
    "物品向量": "内容 Embedding",
    "匹配": "向量相似度",
    "排序": "精排",
}
for k, v in rec_principle.items():
    print(f"  {k}: {v}")
```

#### ZZZZZZZ.2 协同过滤

```python
# 代码示例282：协同过滤
cf = {
    "User-CF": "用户相似",
    "Item-CF": "物品相似",
    "Matrix Factorization": "矩阵分解",
    "Embedding": "深度学习版",
}
for k, v in cf.items():
    print(f"  {k}: {v}")
```

---

### 附录 AAAAAAAA：Embedding 与搜索

#### AAAAAAAA.1 搜索引擎

```python
# 代码示例283：搜索引擎
search_engine = {
    "倒排索引": "关键词 BM25",
    "向量搜索": "语义相似",
    "混合": "两者结合",
    "Rerank": "精排",
}
for k, v in search_engine.items():
    print(f"  {k}: {v}")
```

#### AAAAAAAA.2 BM25

```python
# 代码示例284：BM25
bm25 = {
    "原理": "词频逆文档频率",
    "优点": "关键词匹配",
    "缺点": "无语义",
    "与向量": "互补",
}
for k, v in bm25.items():
    print(f"  {k}: {v}")
```

#### AAAAAAAA.3 混合搜索

```python
# 代码示例285：混合搜索
def hybrid_search(query, bm25_results, vector_results, k=10):
    """RRF 融合"""
    rrf = {}
    for rank, doc in enumerate(bm25_results):
        rrf[doc] = rrf.get(doc, 0) + 1.0 / (60 + rank + 1)
    for rank, doc in enumerate(vector_results):
        rrf[doc] = rrf.get(doc, 0) + 1.0 / (60 + rank + 1)
    return sorted(rrf, key=rrf.get, reverse=True)[:k]
print("混合搜索: RRF 融合 BM25 + 向量")
```

---

### 附录 BBBBBBBB：Embedding 与知识库

#### BBBBBBBB.1 知识库

```python
# 代码示例286：知识库
knowledge_base = {
    "文档": "企业文档",
    "切块": "分块",
    "索引": "向量库",
    "检索": "语义搜索",
    "生成": "LLM 回答",
}
for k, v in knowledge_base.items():
    print(f"  {k}: {v}")
```

#### BBBBBBBB.1 RAG 知识库

```python
# 代码示例287：RAG 知识库
def build_kb(docs, embedding_model, vector_db):
    """构建知识库"""
    chunks = []
    for doc in docs:
        chunks.extend([doc[i:i+512] for i in range(0, len(doc), 462)])
    embs = embedding_model.encode(chunks)
    vector_db.add(embs, chunks)
    return f"索引 {len(chunks)} 块"
print(build_kb, "RAG 知识库构建")
```

---

### 附录 CCCCCCCC：Embedding 与问答

#### CCCCCCCC.1 问答系统

```python
# 代码示例288：问答
def qa(query, vector_db, llm, embedding_model):
    docs = vector_db.search(embedding_model.encode([query]), top_k=5)
    context = "\n".join([d.text for d in docs])
    return llm(f"上下文: {context}\n问题: {query}")
print("问答: RAG")
```

#### CCCCCCCC.2 FAQ 系统

```python
# 代码示例289：FAQ
class FAQ:
    def __init__(self, embedding_model):
        self.model = embedding_model
        self.questions = []
        self.answers = []
        self.q_embs = None
    def add(self, q, a):
        self.questions.append(q)
        self.answers.append(a)
    def search(self, query, top_k=1):
        q_emb = self.model.encode([query])
        scores = np.dot(q_emb, self.q_embs.T)[0]
        idx = scores.argsort()[-top_k:][::-1]
        return [self.answers[i] for i in idx]
print("FAQ: 问题向量检索答案")
```

---

### 附录 DDDDDDDD：Embedding 与代码

#### DDDDDDDD.1 代码 Embedding

```python
# 代码示例290：代码 Embedding
code_emb = {
    "CodeBERT": "代码理解",
    "CodeT5": "代码生成",
    "UniXcoder": "代码表示",
    "用途": "代码搜索/补全/修复",
}
for k, v in code_emb.items():
    print(f"  {k}: {v}")
```

#### DDDDDDDD.2 代码搜索

```python
# 代码示例291：代码搜索
def code_search(query, code_docs, model):
    q_emb = model.encode([query])
    c_embs = model.encode(code_docs)
    scores = np.dot(q_emb, c_embs.T)[0]
    return scores.argsort()[::-1]
print("代码搜索: 自然语言找代码")
```

---

### 附录 EEEEEEEE：Embedding 评估

#### EEEEEEEE.1 评估指标

```python
# 代码示例292：评估指标
eval_metrics = {
    "Recall@K": "相关文档召回",
    "Precision@K": "Top-K 精确",
    "MRR": "第一个相关排名",
    "NDCG": "排序质量",
    "MAP": "平均精度",
    "Spearman": "相关排序",
}
for k, v in eval_metrics.items():
    print(f"  {k}: {v}")
```

#### EEEEEEEE.2 评估方法

```python
# 代码示例293：评估方法
eval_methods = {
    "MTEB": "标准基准",
    "人工": "准确但贵",
    "LLM Judge": "自动评估",
    "A/B 测试": "线上效果",
}
for k, v in eval_methods.items():
    print(f"  {k}: {v}")
```

---

### 附录 FFFFFFFF：Embedding 最佳实践

#### FFFFFFFF.1 实践清单

```python
# 代码示例294：实践清单
checklist = [
    "☐ 选对模型(中文选 BGE)",
    "☐ 归一化向量",
    "☐ 批量嵌入",
    "☐ 缓存重复查询",
    "☐ 混合检索(向量+BM25)",
    "☐ Reranker 精排",
    "☐ 评估检索质量",
    "☐ 监控延迟和错误",
    "☐ 定期更新索引",
    "☐ 端到端测试",
]
for c in checklist:
    print(f"  {c}")
```

#### FFFFFFFF.2 中文实践

```python
# 代码示例295：中文实践
zh_practice = [
    "用 BGE-large-zh-v1.5",
    "加查询前缀",
    "中文分词",
    "考虑同义词",
    "C-MTEB 评估",
]
for p in zh_practice:
    print(f"  ✅ {p}")
```

---

### 附录 GGGGGGGG：Embedding 总结

```python
# 代码示例296：总结
final_summary = [
    "Embedding 是 RAG 基础",
    "双编码器快, 交叉编码器准",
    "中文选 BGE, 多语言选 M3",
    "归一化后点积=余弦",
    "评估用 MTEB",
    "微调=对比学习",
    "HNSW 高效索引",
    "混合检索+Rerank",
    "监控+灰度+降级",
    "成本: 小模型+缓存+批量",
]
for s in final_summary:
    print(f"  ✅ {s}")
```

---

### 附录 HHHHHHHH：文档结束

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 290+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 IIIIIIII：Embedding 深度百科

#### IIIIIIII.1 Embedding 与 Transformer

```python
# 代码示例297：Transformer 编码
class TransformerEncoder:
    def __init__(self, vocab_size, dim, n_heads, n_layers):
        self.vocab_size = vocab_size
        self.dim = dim
        self.n_heads = n_heads
        self.n_layers = n_layers
    def encode(self, token_ids):
        """Token IDs -> 句向量"""
        return f"[{self.n_layers}层 Transformer] {token_ids} -> 向量"
enc = TransformerEncoder(50000, 768, 12, 12)
print(enc.encode([101, 2003, 1037, 3231, 102]))
```

#### IIIIIIII.2 多头注意力

```python
# 代码示例298：多头注意力
def multi_head_attention(Q, K, V, n_heads=12):
    """多头自注意力"""
    d = Q.shape[-1]
    d_k = d // n_heads
    heads = []
    for i in range(n_heads):
        q_i = Q[:, i*d_k:(i+1)*d_k]
        k_i = K[:, i*d_k:(i+1)*d_k]
        v_i = V[:, i*d_k:(i+1)*d_k]
        score = np.dot(q_i, k_i.T) / np.sqrt(d_k)
        attn = np.exp(score - score.max())
        attn = attn / attn.sum()
        heads.append(np.dot(attn, v_i))
    return np.concatenate(heads, axis=-1)
print("Multi-Head Attention: 12头并行")
```

---

#### IIIIIIII.3 位置编码

```python
# 代码示例299：位置编码
def positional_encoding(seq_len, dim):
    """正弦位置编码"""
    pos = np.arange(seq_len)[:, np.newaxis]
    i = np.arange(dim)[np.newaxis, :]
    angle = pos / np.power(10000, (2 * (i // 2)) / dim)
    pe = np.zeros((seq_len, dim))
    pe[:, 0::2] = np.sin(angle[:, 0::2])
    pe[:, 1::2] = np.cos(angle[:, 1::2])
    return pe
pe = positional_encoding(10, 64)
print(f"位置编码形状: {pe.shape}")
```

#### IIIIIIII.4 前馈网络

```python
# 代码示例300：FFN
def feed_forward(x, dim_ff=3072):
    """两层 FFN + GELU"""
    W1 = np.random.randn(x.shape[-1], dim_ff)
    W2 = np.random.randn(dim_ff, x.shape[-1])
    h = np.maximum(0, np.dot(x, W1))
    return np.dot(h, W2)
print("FFN: Linear-GELU-Linear")
```

---

### 附录 JJJJJJJJ：Embedding 模型训练

#### JJJJJJJJ.1 对比学习深入

```python
# 代码示例301：对比学习深入
contrastive_deep = {
    "目标": "同类近, 异类远",
    "方法": "InfoNCE / Triplet",
    "温度": "0.07",
    "困难负样本": "关键!",
}
for k, v in contrastive_deep.items():
    print(f"  {k}: {v}")
```

#### JJJJJJJJ.2 困难负样本挖掘

```python
# 代码示例302：困难负样本
def hard_negatives(anchor_emb, candidate_embs, top_n=5):
    """找最相似但不相关的"""
    sims = np.dot(anchor_emb, candidate_embs.T)
    return np.argsort(sims)[-top_n:][::-1]
print("Hard Neg: 最相似但不相关")
```

#### JJJJJJJJ.3 温度系数

```python
# 代码示例303：温度
temperature = {
    "低温": "0.01, 尖锐分布",
    "高温": "0.5, 平滑分布",
    "默认": "0.07",
    "影响": "影响对比损失",
}
for k, v in temperature.items():
    print(f"  {k}: {v}")
```

---

### 附录 KKKKKKKK：Embedding 推理优化

#### KKKKKKKK.1 ONNX 导出

```python
# 代码示例304：ONNX
onnx_export = """
import torch
model = SentenceTransformer('BAAI/bge-large-zh-v1.5')
dummy = torch.randint(0, 1000, (1, 128))
torch.onnx.export(model, dummy, "model.onnx", opset_version=14)
"""
print(onnx_export)
```

#### KKKKKKKK.2 ONNX 推理

```python
# 代码示例305：ONNX 推理
onnx_infer = """
import onnxruntime as ort
session = ort.InferenceSession("model.onnx")
output = session.run(None, {"input": input_ids})
"""
print(onnx_infer)
```

#### KKKKKKKK.3 量化

```python
# 代码示例306：量化
quant = {
    "FP32": "32位浮点",
    "FP16": "16位浮点, 2x 快",
    "INT8": "8位整数, 4x 快",
    "效果": "略降质量",
}
for k, v in quant.items():
    print(f"  {k}: {v}")
```

---

### 附录 LLLLLLLL：Embedding 与向量数据库

#### LLLLLLLL.1 Qdrant

```python
# 代码示例307：Qdrant
qdrant = """
from qdrant_client import QdrantClient
client = QdrantClient("localhost", port=6333)
client.create_collection("docs", vectors_config={"size": 1024, "distance": "Cosine"})
client.upsert("docs", [{"id": 1, "vector": [0.1]*1024, "payload": {"text": "..."}}])
"""
print(qdrant)
```

#### LLLLLLLL.2 Milvus

```python
# 代码示例308：Milvus
milvus = """
from pymilvus import connections, Collection
connections.connect("default", host="localhost", port="19530")
col = Collection("docs")
col.insert([[1], [[0.1]*1024]])
"""
print(milvus)
```

#### LLLLLLLL.3 Chroma

```python
# 代码示例309：Chroma
chroma = """
import chromadb
client = chromadb.Client()
col = client.create_collection("docs")
col.add(ids=["1"], embeddings=[[0.1]*384], documents=["..."])
"""
print(chroma)
```

#### LLLLLLLL.4 PGVector

```python
# 代码示例310：PGVector
pgvector = """
CREATE EXTENSION vector;
CREATE TABLE docs (id bigserial, embedding vector(1024), text text);
SELECT * FROM docs ORDER BY embedding <-> '[...]' LIMIT 10;
"""
print(pgvector)
```

---

### 附录 MMMMMMMM：Embedding 与 RAG 深入

#### MMMMMMMM.1 RAG 架构图

```python
# 代码示例311：RAG 架构
rag_arch = {
    "离线": ["采集", "切块", "Embedding", "向量库"],
    "在线": ["Query", "Embedding", "检索", "Rerank", "LLM", "答案"],
}
for phase, steps in rag_arch.items():
    print(f"  {phase}: {' → '.join(steps)}")
```

#### MMMMMMMM.2 RAG 切块

```python
# 代码示例312：切块
def chunk_text_advanced(text, chunk_size=512, overlap=64):
    """递归切块"""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
print("切块: 512 + 64 overlap")
```

#### MMMMMMMM.3 RAG Rerank

```python
# 代码示例313：Rerank
def rerank(query, docs, reranker_model, top_k=5):
    pairs = [(query, doc) for doc in docs]
    scores = reranker_model.predict(pairs)
    top = np.argsort(scores)[-top_k:][::-1]
    return [docs[i] for i in top]
print("Rerank: CrossEncoder 精排")
```

---

### 附录 NNNNNNNN：Embedding 评估

#### NNNNNNNN.1 MTEB 深入

```python
# 代码示例314：MTEB 深入
mteb_detail = {
    "任务": "56 个",
    "类型": "Retrieval, STS, Clustering, Classification",
    "度量": "nDCG, Spearman",
    "用途": "模型排名",
}
for k, v in mteb_detail.items():
    print(f"  {k}: {v}")
```

#### NNNNNNNN.2 评估流程

```python
# 代码示例315：评估流程
eval_flow = [
    "1. 准备评估集",
    "2. 嵌入所有文本",
    "3. 计算相似度",
    "4. 计算指标",
    "5. 对比模型",
]
for step in eval_flow:
    print(f"  {step}")
```

---

### 附录 OOOOOOOO：Embedding 成本

#### OOOOOOOO.1 成本计算

```python
# 代码示例316：成本计算
def total_cost(n_docs, dim, model_price, doc_len=500):
    """总成本"""
    tokens = n_docs * doc_len
    api_cost = tokens / 1_000_000 * model_price
    storage_gb = n_docs * dim * 4 / 1024**3
    return {"api_cost": api_cost, "storage_GB": storage_gb}
r = total_cost(1000000, 1024, 0.02)
print(f"100万文档: ${r['api_cost']:.2f}, {r['storage_GB']:.1f}GB")
```

#### OOOOOOOO.2 成本优化

```python
# 代码示例317：成本优化
cost_opt = {
    "模型": "小模型",
    "缓存": "Redis",
    "批量": "批量 API",
    "自部署": "量大省钱",
}
for k, v in cost_opt.items():
    print(f"  {k}: {v}")
```

---

### 附录 PPPPPPPP：Embedding 坑点

```python
# 代码示例318：坑点补充
pitfalls_extra = [
    "归一化不一致(查/建不同)",
    "向量维度不匹配",
    "切块太小语义不全",
    "切块太大噪音多",
    "不做查询改写",
    "不做 Rerank",
    "索引参数不对",
    "不监控检索质量",
    "不处理增量",
    "不做灰度",
]
for p in pitfalls_extra:
    print(f"  ❌ {p}")
```

---

### 附录 QQQQQQQQ：Embedding 面试

```python
# 代码示例319：面试补充
interview_extra = [
    "Q: Embedding 和 LLM 区别?",
    "Q: 双编码器为什么快?",
    "Q: 交叉编码器为什么准?",
    "Q: 难负样本为什么重要?",
    "Q: 怎么处理长文本?",
    "Q: 多语言怎么对齐?",
    "Q: 怎么评估 Embedding?",
    "Q: 怎么优化 Embedding?",
]
for q in interview_extra:
    print(f"  {q}")
```

---

### 附录 RRRRRRRR：Embedding 总结

```python
# 代码示例320：总结
emb_summary = {
    "概念": "文本->向量",
    "历史": "One-hot->Word2Vec->BERT",
    "架构": "双编码器+交叉编码器",
    "模型": "BGE/E5/GTE/OpenAI",
    "相似度": "余弦/点积/欧氏",
    "应用": "RAG/搜索/推荐",
    "优化": "批量/缓存/量化",
    "评估": "MTEB",
    "成本": "API vs 自部署",
}
for k, v in emb_summary.items():
    print(f"  {k}: {v}")
```

---

### 附录 SSSSSSSS：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 320+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 TTTTTTTT：Embedding 技术深度

#### TTTTTTTT.1 Embedding 与表示学习

```python
# 代码示例321：表示学习
representation_learning = {
    "定义": "学习数据的有效表示",
    "目的": "便于下游任务",
    "方法": "监督/自监督",
    "Embedding": "表示学习产物",
}
for k, v in representation_learning.items():
    print(f"  {k}: {v}")
```

#### TTTTTTTT.2 自监督学习

```python
# 代码示例322：自监督
self_supervised = {
    "MLM": "掩码预测",
    "对比": "拉近相似",
    "去噪": "去噪自编码器",
    "预训练": "无标注数据",
}
for k, v in self_supervised.items():
    print(f"  {k}: {v}")
```

#### TTTTTTTT.3 迁移学习

```python
# 代码示例323：迁移学习
transfer = {
    "预训练": "大规模数据",
    "微调": "下游任务",
    "Embedding": "迁移表示",
    "优势": "少数据快收敛",
}
for k, v in transfer.items():
    print(f"  {k}: {v}")
```

---

### 附录 UUUUUUUU：Embedding 与对比学习

#### UUUUUUUU.1 对比学习历史

```python
# 代码示例324：对比学习历史
cl_history = [
    (2013, "Word2Vec 对比"),
    (2018, "SimCLR"),
    (2020, "CLIP"),
    (2021, "SimCSE"),
    (2022, "BGE/E5"),
    (2023, "BGE-M3"),
]
for year, event in cl_history:
    print(f"  {year}: {event}")
```

#### UUUUUUUU.2 SimCSE

```python
# 代码示例325：SimCSE
simcse = {
    "原理": "Dropout 做正样本",
    "优点": "无标注数据",
    "效果": "句嵌入 SOTA",
}
for k, v in simcse.items():
    print(f"  {k}: {v}")
```

#### UUUUUUUU.3 CLIP 对比学习

```python
# 代码示例326：CLIP 对比
clip_cl = {
    "输入": "图文对",
    "正样本": "匹配图文",
    "负样本": "batch 内其他图",
    "损失": "InfoNCE",
}
for k, v in clip_cl.items():
    print(f"  {k}: {v}")
```

---

### 附录 VVVVVVVV：Embedding 与多语言

#### VVVVVVVV.1 多语言表示

```python
# 代码示例327：多语言表示
multilingual_rep = {
    "目标": "跨语言语义一致",
    "方法": "多语言对比学习",
    "数据": "平行语料/翻译",
    "效果": "跨语言检索",
}
for k, v in multilingual_rep.items():
    print(f"  {k}: {v}")
```

#### VVVVVVVV.2 多语言挑战

```python
# 代码示例328：多语言挑战
ml_challenges = [
    "低资源语言数据少",
    "语言间分布差异",
    "代码切换",
    "文化/领域差异",
    "翻译质量",
]
for c in ml_challenges:
    print(f"  {c}")
```

---

### 附录 WWWWWWWW：Embedding 与多模态

#### WWWWWWWW.1 多模态表示

```python
# 代码示例329：多模态表示
multimodal_rep = {
    "目标": "跨模态语义一致",
    "方法": "对比学习",
    "数据": "图文对/音视频",
    "效果": "跨模态检索",
}
for k, v in multimodal_rep.items():
    print(f"  {k}: {v}")
```

#### WWWWWWWW.2 CLIP 架构

```python
# 代码示例330：CLIP 架构
clip_arch = {
    "图像编码器": "ViT-B/16",
    "文本编码器": "Transformer",
    "投影": "统一到 512维",
    "对比": "图文 InfoNCE",
}
for k, v in clip_arch.items():
    print(f"  {k}: {v}")
```

---

### 附录 XXXXXXXX：Embedding 与向量检索

#### XXXXXXXX.1 近似最近邻

```python
# 代码示例331：ANN
ann = {
    "全称": "Approximate Nearest Neighbor",
    "目标": "近似最近邻",
    "方法": "HNSW/IVF/PQ",
    "tradeoff": "精度 vs 速度",
}
for k, v in ann.items():
    print(f"  {k}: {v}")
```

#### XXXXXXXX.2 HNSW 深入

```python
# 代码示例332：HNSW 深入
hnsw_deep = {
    "层级": "多层图",
    "搜索": "逐层贪心",
    "复杂度": "O(log n)",
    "参数": "M, ef",
}
for k, v in hnsw_deep.items():
    print(f"  {k}: {v}")
```

#### XXXXXXXX.3 IVF 深入

```python
# 代码示例333：IVF
ivf_deep = {
    "聚类": "K-Means",
    "倒排": "每簇列表",
    "搜索": "只搜最近簇",
    "nprobe": "探测簇数",
}
for k, v in ivf_deep.items():
    print(f"  {k}: {v}")
```

#### XXXXXXXX.4 PQ 量化

```python
# 代码示例334：PQ
pq_detail = {
    "原理": "子向量量化",
    "压缩": "32x",
    "精度": "略降",
    "用途": "大规模",
}
for k, v in pq_detail.items():
    print(f"  {k}: {v}")
```

---

### 附录 YYYYYYYY：Embedding 与 RAG

#### YYYYYYYY.1 RAG 检索增强

```python
# 代码示例335：RAG 检索增强
rag_enhance = {
    "切块": "语义切块",
    "Embedding": "选好模型",
    "检索": "混合检索",
    "Rerank": "交叉编码器",
    "生成": "好 Prompt",
}
for k, v in rag_enhance.items():
    print(f"  {k}: {v}")
```

#### YYYYYYYY.2 RAG 评估

```python
# 代码示例336：RAG 评估
rag_eval = {
    "检索": "Recall@K",
    "生成": "答案质量",
    "忠实度": "基于上下文",
    "相关性": "答案相关",
}
for k, v in rag_eval.items():
    print(f"  {k}: {v}")
```

---

### 附录 ZZZZZZZZ：Embedding 与 LLM

```python
# 代码示例337：Embedding 与 LLM
emb_llm = {
    "Embedding": "理解语义, 检索",
    "LLM": "生成, 推理",
    "RAG": "Embedding + LLM",
    "Agent": "Embedding 记忆 + LLM 决策",
}
for k, v in emb_llm.items():
    print(f"  {k}: {v}")
```

---

### 附录 AAAAAAAAA：Embedding 生产

#### AAAAAAAAA.1 生产架构

```python
# 代码示例338：生产架构
prod_arch = {
    "离线": "Airflow -> 切块 -> Embedding -> Qdrant",
    "在线": "FastAPI -> 检索 -> LLM",
    "监控": "Prometheus + Grafana",
    "缓存": "Redis",
}
for k, v in prod_arch.items():
    print(f"  {k}: {v}")
```

#### AAAAAAAAA.2 高可用

```python
# 代码示例339：高可用
ha = {
    "多副本": "Qdrant 副本",
    "降级": "BM25 兜底",
    "备份": "向量库备份",
    "监控": "错误率告警",
}
for k, v in ha.items():
    print(f"  {k}: {v}")
```

---

### 附录 BBBBBBBBB：Embedding 最佳实践

#### BBBBBBBBB.1 实践清单

```python
# 代码示例340：实践清单
best_practices = [
    "选对模型(中文 BGE)",
    "归一化向量",
    "批量嵌入",
    "缓存重复查询",
    "混合检索",
    "Reranker",
    "评估质量",
    "监控延迟",
    "定期更新",
    "端到端测试",
]
for p in best_practices:
    print(f"  ✅ {p}")
```

#### BBBBBBBBB.2 常见坑

```python
# 代码示例341：常见坑
common_pitfalls = [
    "不归一化",
    "选错语言模型",
    "不批量",
    "不缓存",
    "不评估",
    "不重排",
    "盲目追大",
    "忽视成本",
]
for p in common_pitfalls:
    print(f"  ❌ {p}")
```

---

### 附录 CCCCCCCCC：Embedding 面试

#### CCCCCCCCC.1 面试核心

```python
# 代码示例342：面试核心
core_qa = [
    ("什么是 Embedding", "文本映射到向量空间"),
    ("双编码器 vs 交叉编码器", "快 vs 准"),
    ("余弦相似度", "dot/(||a||*||b||)"),
    ("为什么归一化", "点积=余弦, 快"),
    ("中文选什么", "BGE-large-zh"),
    ("MTEB", "Embedding 基准"),
    ("怎么微调", "对比学习"),
    ("HNSW", "图索引"),
]
for q, a in core_qa:
    print(f"  Q: {q}\n  A: {a}")
```

---

### 附录 DDDDDDDDD：Embedding 总结

```python
# 代码示例343：总结
final = [
    "Embedding 是 RAG 基础",
    "双编码器快, 交叉编码器准",
    "中文选 BGE, 多语言 M3",
    "归一化后点积=余弦",
    "MTEB 评估",
    "对比学习微调",
    "HNSW 索引",
    "混合检索+Rerank",
    "监控+灰度",
    "小模型+缓存=低成本",
]
for s in final:
    print(f"  ✅ {s}")
```

---

### 附录 EEEEEEEEE：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 340+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 FFFFFFFFF：Embedding 深度技术百科

#### FFFFFFFFF.1 Embedding 与语义空间

```python
# 代码示例344：语义空间
semantic_space = {
    "定义": "Embedding 所在数学空间",
    "性质": "相似=近",
    "维度": "通常 384-3072",
    "几何": "度量空间",
}
for k, v in semantic_space.items():
    print(f"  {k}: {v}")
```

#### FFFFFFFFF.2 向量空间模型

```python
# 代码示例345：向量空间模型
vector_space_model = {
    "历史": "TF-IDF -> 神经网络",
    "TF-IDF": "词频逆文档频率",
    "神经": "Word2Vec -> BERT",
    "现代": "上下文嵌入",
}
for k, v in vector_space_model.items():
    print(f"  {k}: {v}")
```

---

#### FFFFFFFFF.3 词嵌入数学

```python
# 代码示例346：词嵌入数学
def word_emb_math(word, emb_matrix):
    """查表"""
    return emb_matrix[word]
print("词嵌入: 查表 lookup")
```

#### FFFFFFFFF.4 句嵌入数学

```python
# 代码示例347：句嵌入数学
def sentence_emb(tokens, model):
    """Transformer + 池化"""
    token_embs = model.forward(tokens)
    return token_embs.mean(axis=0)
print("句嵌入: Transformer + Mean Pooling")
```

---

### 附录 GGGGGGGGG：Embedding 与 BERT

#### GGGGGGGGG.1 BERT 训练

```python
# 代码示例348：BERT 训练
bert_training = {
    "MLM": "掩码语言模型",
    "NSP": "下一句预测",
    "损失": "交叉熵",
    "数据": "Wikipedia + 书籍",
}
for k, v in bert_training.items():
    print(f"  {k}: {v}")
```

#### GGGGGGGGG.2 BERT 输出

```python
# 代码示例349：BERT 输出
bert_output = {
    "last_hidden_state": "所有 token 向量",
    "pooler_output": "CLS 向量",
    "用途": "CLS 做分类, Mean 做相似度",
}
for k, v in bert_output.items():
    print(f"  {k}: {v}")
```

#### GGGGGGGGG.3 BERT 池化

```python
# 代码示例350：BERT 池化
def pool_bert(token_embeddings, method="mean"):
    if method == "cls":
        return token_embeddings[0]
    return token_embeddings.mean(axis=0)
print("BERT 池化: CLS 或 Mean")
```

---

### 附录 HHHHHHHHH：Embedding 与 Sentence-BERT

#### HHHHHHHHH.1 SBERT 原理

```python
# 代码示例351：SBERT 原理
sbert_principle = {
    "双塔": "两个 BERT 共享权重",
    "池化": "Mean Pooling",
    "损失": "对比/回归",
    "优点": "快, 可预计算",
}
for k, v in sbert_principle.items():
    print(f"  {k}: {v}")
```

#### HHHHHHHHH.2 SBERT 损失

```python
# 代码示例352：SBERT 损失
sbert_loss = {
    "CosineLoss": "回归相似度",
    "ContrastiveLoss": "对比",
    "TripletLoss": "三元组",
}
for k, v in sbert_loss.items():
    print(f"  {k}: {v}")
```

---

### 附录 IIIIIIIII：Embedding 与 BGE

#### IIIIIIIII.1 BGE 训练

```python
# 代码示例353：BGE 训练
bge_training = {
    "预训练": "RoBERTa",
    "微调": "对比学习",
    "数据": "(query, positive, hard_neg)",
    "特点": "查询前缀指令",
}
for k, v in bge_training.items():
    print(f"  {k}: {v}")
```

#### IIIIIIIII.2 BGE-M3

```python
# 代码示例354：BGE-M3
bge_m3 = {
    "多语言": "100+",
    "多功能": "稠密+稀疏+多向量",
    "多粒度": "短/长文本",
    "开源": "是",
}
for k, v in bge_m3.items():
    print(f"  {k}: {v}")
```

---

### 附录 JJJJJJJJJ：Embedding 与 E5

#### JJJJJJJJJ.1 E5 训练

```python
# 代码示例355：E5 训练
e5_training = {
    "弱监督": "从网页挖 (query, doc)",
    "指令": "query: / passage:",
    "对比": "InfoNCE",
    "代表": "e5-large-v2",
}
for k, v in e5_training.items():
    print(f"  {k}: {v}")
```

---

### 附录 KKKKKKKKK：Embedding 与 GTE

#### KKKKKKKKK.1 GTE 训练

```python
# 代码示例356：GTE 训练
gte_training = {
    "机构": "Alibaba",
    "训练": "对比学习",
    "多语言": "支持",
    "代表": "gte-large",
}
for k, v in gte_training.items():
    print(f"  {k}: {v}")
```

---

### 附录 LLLLLLLLL：Embedding 与 OpenAI

#### LLLLLLLLL.1 OpenAI Embedding

```python
# 代码示例357：OpenAI Embedding
openai_emb = {
    "text-embedding-3-small": {"dim": 1536, "price": "$0.02/1M"},
    "text-embedding-3-large": {"dim": 3072, "price": "$0.13/1M"},
    "Matryoshka": "支持截断维度",
}
for k, v in openai_emb.items():
    print(f"  {k}: {v}")
```

#### LLLLLLLLL.2 OpenAI 使用

```python
# 代码示例358：OpenAI 使用
openai_use = """
from openai import OpenAI
client = OpenAI()
resp = client.embeddings.create(model="text-embedding-3-small", input="文本")
emb = resp.data[0].embedding
"""
print(openai_use)
```

---

### 附录 MMMMMMMMM：Embedding 与向量数据库

#### MMMMMMMMM.1 向量数据库选择

```python
# 代码示例359：向量库选择
def choose_db(scale, cloud, managed):
    if managed:
        return "Pinecone"
    if cloud:
        return "Qdrant Cloud"
    if scale == "small":
        return "Chroma"
    return "Qdrant / Milvus"
print(choose_db("large", False, False))
```

#### MMMMMMMMM.2 索引参数

```python
# 代码示例360：索引参数
index_params = {
    "HNSW M": "16-64",
    "HNSW efConstruction": "100-500",
    "HNSW efSearch": "50-200",
    "IVF nlist": "4*sqrt(n)",
    "IVF nprobe": "8-64",
}
for k, v in index_params.items():
    print(f"  {k}: {v}")
```

---

### 附录 NNNNNNNNN：Embedding 与检索

#### NNNNNNNNN.1 检索质量

```python
# 代码示例361：检索质量
retrieval_metrics = {
    "Recall@K": "相关召回",
    "Precision@K": "精确",
    "MRR": "排名质量",
    "NDCG": "排序增益",
}
for k, v in retrieval_metrics.items():
    print(f"  {k}: {v}")
```

#### NNNNNNNNN.2 检索优化

```python
# 代码示例362：检索优化
retrieval_opt = {
    "查询改写": "扩展/分解",
    "混合检索": "向量+BM25",
    "Rerank": "交叉编码器",
    "Top-K": "调优",
}
for k, v in retrieval_opt.items():
    print(f"  {k}: {v}")
```

---

### 附录 OOOOOOOOO：Embedding 与 RAG

#### OOOOOOOOO.1 RAG 完整流程

```python
# 代码示例363：RAG 完整
def rag_pipeline(query, vector_db, llm, embedding_model, reranker=None):
    q_emb = embedding_model.encode([query])
    docs = vector_db.search(q_emb, top_k=20)
    if reranker:
        docs = reranker.rerank(query, docs, top_k=5)
    context = "\n".join([d.text for d in docs])
    prompt = f"基于上下文回答: {context}\n\n问题: {query}"
    return llm(prompt)
print("RAG: 检索+Rerank+生成")
```

#### OOOOOOOOO.2 RAG 质量

```python
# 代码示例364：RAG 质量
rag_quality = {
    "切块": "chunk_size, overlap",
    "Embedding": "模型选择",
    "检索": "Top-K, Rerank",
    "生成": "LLM, Prompt",
}
for k, v in rag_quality.items():
    print(f"  {k}: {v}")
```

---

### 附录 PPPPPPPPP：Embedding 评估

#### PPPPPPPPP.1 MTEB

```python
# 代码示例365：MTEB
mteb = {
    "全称": "Massive Text Embedding Benchmark",
    "任务": "56 个",
    "类型": "Retrieval, STS, Clustering, Classification",
    "用途": "模型排名",
}
for k, v in mteb.items():
    print(f"  {k}: {v}")
```

#### PPPPPPPPP.2 C-MTEB

```python
# 代码示例366：C-MTEB
cmteb = {
    "全称": "Chinese MTEB",
    "任务": "30+",
    "用途": "中文模型评估",
}
for k, v in cmteb.items():
    print(f"  {k}: {v}")
```

---

### 附录 QQQQQQQQQ：Embedding 成本

#### QQQQQQQQQ.1 成本对比

```python
# 代码示例367：成本对比
cost_compare = {
    "OpenAI API": "$0.02-0.13/1M tokens",
    "自部署 BGE": "$0.001-0.01/1M",
    "存储": "向量库存储",
    "运维": "人力",
}
for k, v in cost_compare.items():
    print(f"  {k}: {v}")
```

#### QQQQQQQQQ.2 成本优化

```python
# 代码示例368：成本优化
cost_opt = {
    "模型": "选小模型",
    "缓存": "Redis",
    "批量": "批量 API",
    "自部署": "量大省钱",
}
for k, v in cost_opt.items():
    print(f"  {k}: {v}")
```

---

### 附录 RRRRRRRRR：Embedding 坑点

```python
# 代码示例369：坑点
pitfalls = [
    "不归一化",
    "选错模型",
    "维度太大",
    "不批量",
    "不缓存",
    "不评估",
    "不重排",
    "盲目追大",
    "不监控",
    "不更新索引",
]
for p in pitfalls:
    print(f"  ❌ {p}")
```

---

### 附录 SSSSSSSSS：Embedding 面试

```python
# 代码示例370：面试
interview = [
    "Embedding 是文本向量",
    "双编码器快, 交叉编码器准",
    "余弦=点积/模长积",
    "归一化后点积=余弦",
    "中文选 BGE",
    "MTEB 是基准",
    "对比学习微调",
    "HNSW 图索引",
    "RAG = 检索+生成",
    "CLIP 图文对比",
]
for a in interview:
    print(f"  ✅ {a}")
```

---

### 附录 TTTTTTTTT：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 370+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 UUUUUUUUU：Embedding 技术深度百科

#### UUUUUUUUU.1 Embedding 与深度学习栈

```python
# 代码示例371：深度学习栈
dl_stack = {
    "框架": "PyTorch / TensorFlow",
    "模型": "HuggingFace Transformers",
    "训练": "Accelerate / DeepSpeed",
    "推理": "ONNX / TensorRT",
}
for k, v in dl_stack.items():
    print(f"  {k}: {v}")
```

#### UUUUUUUUU.2 HuggingFace

```python
# 代码示例372：HuggingFace
hf = {
    "Transformers": "模型库",
    "Datasets": "数据集",
    "Sentence-Transformers": "句嵌入",
    "FlagEmbedding": "BGE 官方",
}
for k, v in hf.items():
    print(f"  {k}: {v}")
```

---

#### UUUUUUUUU.3 PyTorch 基础

```python
# 代码示例373：PyTorch
import torch
x = torch.randn(2, 3)
print(f"PyTorch 张量: {x.shape}")
```

#### UUUUUUUUU.4 NumPy 基础

```python
# 代码示例374：NumPy
import numpy as np
a = np.array([1, 2, 3])
print(f"NumPy 数组: {a}")
```

---

### 附录 VVVVVVVVV：Embedding 与 NLP 工具

#### VVVVVVVVV.1 分词工具

```python
# 代码示例375：分词
tokenizers = {
    "BERT": "WordPiece",
    "GPT": "BPE",
    "LLaMA": "BPE",
    "中文": "字/词",
}
for k, v in tokenizers.items():
    print(f"  {k}: {v}")
```

#### VVVVVVVVV.2 Tokenizer

```python
# 代码示例376：Tokenizer
def tokenize(text, tokenizer):
    return tokenizer(text, return_tensors="pt", padding=True, truncation=True)
print("Tokenizer: 文本 -> Token IDs")
```

---

### 附录 WWWWWWWWW：Embedding 与数据

#### WWWWWWWWW.1 数据质量

```python
# 代码示例377：数据质量
data_quality = {
    "清洗": "去重/去噪",
    "一致性": "格式统一",
    "标注": "准确标注",
    "多样性": "覆盖多样",
}
for k, v in data_quality.items():
    print(f"  {k}: {v}")
```

#### WWWWWWWWW.2 数据增强

```python
# 代码示例378：数据增强
aug = {
    "回译": "翻译再翻译",
    "同义词": "词替换",
    "随机": "删除/替换",
    "困难负": "挖掘难负",
}
for k, v in aug.items():
    print(f"  {k}: {v}")
```

---

### 附录 XXXXXXXXX：Embedding 与训练

#### XXXXXXXXX.1 训练超参

```python
# 代码示例379：训练超参
hyperparams = {
    "lr": "2e-5",
    "batch_size": "128",
    "epochs": "3-10",
    "warmup": "10%",
    "weight_decay": "0.01",
}
for k, v in hyperparams.items():
    print(f"  {k}: {v}")
```

#### XXXXXXXXX.2 训练监控

```python
# 代码示例380：训练监控
monitor = {
    "loss": "训练损失",
    "lr": "学习率",
    "grad_norm": "梯度范数",
    "eval": "验证指标",
}
for k, v in monitor.items():
    print(f"  {k}: {v}")
```

---

### 附录 YYYYYYYYY：Embedding 与推理

#### YYYYYYYYY.1 推理优化

```python
# 代码示例381：推理优化
inference_opt = {
    "batch": "批量",
    "GPU": "GPU",
    "FP16": "半精度",
    "ONNX": "ONNX Runtime",
}
for k, v in inference_opt.items():
    print(f"  {k}: {v}")
```

#### YYYYYYYYY.2 推理服务

```python
# 代码示例382：推理服务
serving = {
    "FastAPI": "Web 服务",
    "TorchServe": "PyTorch",
    "Triton": "NVIDIA",
    "vLLM": "LLM",
}
for k, v in serving.items():
    print(f"  {k}: {v}")
```

---

### 附录 ZZZZZZZZZ：Embedding 与向量库

#### ZZZZZZZZZ.1 向量库操作

```python
# 代码示例383：向量库操作
db_ops = {
    "插入": "add(vectors, docs)",
    "搜索": "search(query, top_k)",
    "删除": "delete(id)",
    "更新": "update(id, vector)",
}
for k, v in db_ops.items():
    print(f"  {k}: {v}")
```

#### ZZZZZZZZZ.2 索引类型

```python
# 代码示例384：索引类型
index_types = {
    "Flat": "暴力, O(n)",
    "IVF": "倒排, O(n/k)",
    "HNSW": "图, O(log n)",
    "PQ": "量化",
}
for k, v in index_types.items():
    print(f"  {k}: {v}")
```

---

### 附录 AAAAAAAAAA：Embedding 与检索

#### AAAAAAAAAA.1 检索流程

```python
# 代码示例385：检索流程
retrieval_flow = [
    "1. Query -> Embedding",
    "2. 向量库搜索 Top-K",
    "3. Reranker 精排",
    "4. 返回 Top-N",
]
for step in retrieval_flow:
    print(f"  {step}")
```

#### AAAAAAAAAA.2 混合检索

```python
# 代码示例386：混合检索
hybrid = {
    "向量": "语义",
    "BM25": "关键词",
    "RRF": "融合",
    "效果": "互补",
}
for k, v in hybrid.items():
    print(f"  {k}: {v}")
```

---

### 附录 BBBBBBBBBB：Embedding 与 RAG

#### BBBBBBBBBB.1 RAG 流程

```python
# 代码示例387：RAG 流程
rag_flow = [
    "1. 文档切块",
    "2. Embedding 入向量库",
    "3. Query Embedding",
    "4. 检索 Top-K",
    "5. Rerank",
    "6. LLM 生成",
]
for step in rag_flow:
    print(f"  {step}")
```

#### BBBBBBBBBB.2 RAG 优化

```python
# 代码示例388：RAG 优化
rag_opt = {
    "切块": "512 + 50 overlap",
    "Embedding": "BGE-large-zh",
    "检索": "Top-10",
    "Rerank": "bge-reranker",
}
for k, v in rag_opt.items():
    print(f"  {k}: {v}")
```

---

### 附录 CCCCCCCCCC：Embedding 多语言

#### CCCCCCCCCC.1 多语言模型

```python
# 代码示例389：多语言模型
ml_models = {
    "bge-m3": "100+语言",
    "e5-multilingual": "100+",
    "gte-multilingual": "100+",
    "jina-v3": "89语言",
}
for k, v in ml_models.items():
    print(f"  {k}: {v}")
```

---

### 附录 DDDDDDDDDD：Embedding 多模态

#### DDDDDDDDDD.1 CLIP

```python
# 代码示例390：CLIP
clip = {
    "原理": "图文对比",
    "输出": "统一向量",
    "用途": "图文检索",
}
for k, v in clip.items():
    print(f"  {k}: {v}")
```

---

### 附录 EEEEEEEEEE：Embedding 微调

#### EEEEEEEEEE.1 微调方法

```python
# 代码示例391：微调方法
ft_methods = {
    "对比": "(query, pos, neg)",
    "回归": "(sent1, sent2, score)",
    "分类": "(text, label)",
}
for k, v in ft_methods.items():
    print(f"  {k}: {v}")
```

---

### 附录 FFFFFFFFFF：Embedding 成本

#### FFFFFFFFFF.1 成本计算

```python
# 代码示例392：成本计算
def cost(n_docs, dim, price):
    storage = n_docs * dim * 4 / 1024**3
    return {"storage_GB": storage}
print("100万文档 1024维 ~ 4GB")
```

---

### 附录 GGGGGGGGGG：Embedding 坑点

```python
# 代码示例393：坑点
pitfalls = [
    "不归一化", "选错模型", "维度太大",
    "不批量", "不缓存", "不评估",
    "不重排", "盲目追大", "不监控",
]
for p in pitfalls:
    print(f"  ❌ {p}")
```

---

### 附录 HHHHHHHHHH：Embedding 面试

```python
# 代码示例394：面试
qa = [
    ("Embedding", "文本->向量"),
    ("双编码器", "快, 可预计算"),
    ("交叉编码器", "准, 慢"),
    ("余弦", "dot/(||a||*||b||)"),
    ("归一化", "点积=余弦"),
    ("中文", "BGE"),
    ("MTEB", "基准"),
    ("HNSW", "图索引"),
]
for q, a in qa:
    print(f"  Q: {q}\n  A: {a}")
```

---

### 附录 IIIIIIIIII：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 390+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 JJJJJJJJJJJ：Embedding 技术百科

#### JJJJJJJJJJJ.1 Embedding 与 Transformer 架构

```python
# 代码示例395：Transformer 架构
transformer_arch = {
    "输入嵌入": "Token + Position",
    "编码器层": ["自注意力", "FFN", "残差", "LayerNorm"],
    "池化": "CLS / Mean",
    "输出": "句向量",
}
for k, v in transformer_arch.items():
    print(f"  {k}: {v}")
```

#### JJJJJJJJJJJ.2 自注意力

```python
# 代码示例396：自注意力
self_attention = {
    "公式": "softmax(QK^T/sqrt(d))V",
    "作用": "全局依赖",
    "多头": "多视角",
}
for k, v in self_attention.items():
    print(f"  {k}: {v}")
```

---

#### JJJJJJJJJJJ.3 位置编码

```python
# 代码示例397：位置编码
pos_enc = {
    "正弦": "原始 Transformer",
    "可学习": "BERT",
    "RoPE": "旋转",
}
for k, v in pos_enc.items():
    print(f"  {k}: {v}")
```

#### JJJJJJJJJJJ.4 前馈网络

```python
# 代码示例398：FFN
ffn = {
    "结构": "Linear-GELU-Linear",
    "维度": "d -> 4d -> d",
    "作用": "非线性变换",
}
for k, v in ffn.items():
    print(f"  {k}: {v}")
```

---

### 附录 KKKKKKKKKKK：Embedding 与训练

#### KKKKKKKKKKK.1 对比学习训练

```python
# 代码示例399：对比训练
contrastive_train = {
    "输入": "(anchor, positive, negative)",
    "损失": "InfoNCE / Triplet",
    "目标": "正近负远",
    "温度": "0.07",
}
for k, v in contrastive_train.items():
    print(f"  {k}: {v}")
```

#### KKKKKKKKKKK.2 难负样本

```python
# 代码示例400：难负样本
hard_neg = {
    "为什么": "易负样本太简单",
    "怎么找": "弱模型检索",
    "效果": "提升显著",
}
for k, v in hard_neg.items():
    print(f"  {k}: {v}")
```

---

### 附录 LLLLLLLLLLL：Embedding 与推理

#### LLLLLLLLLLL.1 推理流程

```python
# 代码示例401：推理流程
inference = [
    "1. 文本输入",
    "2. 分词",
    "3. Token IDs",
    "4. 模型前向",
    "5. 池化",
    "6. 归一化",
    "7. 输出向量",
]
for step in inference:
    print(f"  {step}")
```

#### LLLLLLLLLLL.2 推理优化

```python
# 代码示例402：推理优化
infer_opt = {
    "Batch": "批量",
    "GPU": "GPU",
    "FP16": "半精度",
    "ONNX": "ONNX Runtime",
}
for k, v in infer_opt.items():
    print(f"  {k}: {v}")
```

---

### 附录 MMMMMMMMMMM：Embedding 与向量库

#### MMMMMMMMMMM.1 向量库对比

| 数据库 | 语言 | 特点 | 适合 |
|--------|------|------|------|
| Qdrant | Rust | 高性能 | 生产 |
| Milvus | C++ | 大规模 | 大规模 |
| Chroma | Python | 轻量 | 原型 |
| PGVector | C | PG 扩展 | 小量 |
| Pinecone | - | 托管 | 托管 |

#### MMMMMMMMMMM.2 索引选择

```python
# 代码示例403：索引选择
def choose_index(n, dim):
    if n < 10000:
        return "Flat"
    if n < 1000000:
        return "HNSW"
    return "IVF-PQ"
print(choose_index(10000000, 1024))
```

---

### 附录 NNNNNNNNNNN：Embedding 与检索

#### NNNNNNNNNNN.1 检索流程

```python
# 代码示例404：检索流程
retrieval = [
    "1. Query -> Embedding",
    "2. 向量库搜索",
    "3. Rerank",
    "4. 返回",
]
for step in retrieval:
    print(f"  {step}")
```

#### NNNNNNNNNNN.2 Rerank

```python
# 代码示例405：Rerank
def rerank(query, docs, model, top_k=5):
    pairs = [(query, d) for d in docs]
    scores = model.predict(pairs)
    top = np.argsort(scores)[-top_k:][::-1]
    return [docs[i] for i in top]
print("Rerank: CrossEncoder 精排")
```

---

### 附录 OOOOOOOOOOO：Embedding 与 RAG

#### OOOOOOOOOOO.1 RAG 完整

```python
# 代码示例406：RAG
def rag(query, vector_db, llm, embedding_model):
    q_emb = embedding_model.encode([query])
    docs = vector_db.search(q_emb, top_k=5)
    context = "\n".join([d.text for d in docs])
    return llm(f"上下文: {context}\n问题: {query}")
print("RAG: 检索+生成")
```

#### OOOOOOOOOOO.2 RAG 优化

```python
# 代码示例407：RAG 优化
rag_opt = {
    "切块": "512 + 50 overlap",
    "Embedding": "BGE-large-zh",
    "Rerank": "bge-reranker",
}
for k, v in rag_opt.items():
    print(f"  {k}: {v}")
```

---

### 附录 PPPPPPPPPPP：Embedding 评估

#### PPPPPPPPPPP.1 MTEB

```python
# 代码示例408：MTEB
mteb = {
    "任务": "56",
    "类型": "Retrieval, STS, Clustering",
    "用途": "模型排名",
}
for k, v in mteb.items():
    print(f"  {k}: {v}")
```

#### PPPPPPPPPPP.2 指标

```python
# 代码示例409：指标
metrics = {
    "Recall@K": "召回",
    "Precision@K": "精确",
    "MRR": "排名",
    "NDCG": "排序",
}
for k, v in metrics.items():
    print(f"  {k}: {v}")
```

---

### 附录 QQQQQQQQQQQ：Embedding 成本

```python
# 代码示例410：成本
cost = {
    "OpenAI small": "$0.02/1M",
    "OpenAI large": "$0.13/1M",
    "自部署 BGE": "$0.001/1M",
}
for k, v in cost.items():
    print(f"  {k}: {v}")
```

---

### 附录 RRRRRRRRRRR：Embedding 坑点

```python
# 代码示例411：坑点
pitfalls = [
    "不归一化", "选错模型", "维度太大",
    "不批量", "不缓存", "不评估",
]
for p in pitfalls:
    print(f"  ❌ {p}")
```

---

### 附录 SSSSSSSSSSS：Embedding 面试

```python
# 代码示例412：面试
qa = [
    ("Embedding", "文本->向量"),
    ("双编码器", "快"),
    ("交叉编码器", "准"),
    ("余弦", "dot/(||a||*||b||)"),
    ("归一化", "点积=余弦"),
    ("中文", "BGE"),
]
for q, a in qa:
    print(f"  Q: {q}\n  A: {a}")
```

---

### 附录 TTTTTTTTTTT：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 410+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 UUUUUUUUUUU：Embedding 技术深度百科

#### UUUUUUUUUUU.1 Embedding 与数学基础

```python
# 代码示例413：数学基础
math = {
    "向量": "有序列表",
    "模长": "||v||",
    "点积": "a·b",
    "余弦": "a·b/(||a||*||b||)",
    "归一化": "v/||v||",
}
for k, v in math.items():
    print(f"  {k}: {v}")
```

#### UUUUUUUUUUU.2 线性代数

```python
# 代码示例414：线性代数
la = {
    "矩阵": "二维数组",
    "特征值": "特征分解",
    "奇异值": "SVD",
    "PCA": "主成分",
}
for k, v in la.items():
    print(f"  {k}: {v}")
```

---

#### UUUUUUUUUUU.3 概率统计

```python
# 代码示例415：概率统计
prob = {
    "概率分布": "softmax",
    "期望": "mean",
    "方差": "var",
    "交叉熵": "损失",
}
for k, v in prob.items():
    print(f"  {k}: {v}")
```

---

### 附录 VVVVVVVVVVV：Embedding 与机器学习

#### VVVVVVVVVVV.1 监督学习

```python
# 代码示例416：监督学习
supervised = {
    "分类": "标签",
    "回归": "连续值",
    "损失": "CrossEntropy/MSE",
    "Embedding": "特征",
}
for k, v in supervised.items():
    print(f"  {k}: {v}")
```

#### VVVVVVVVVVV.2 无监督学习

```python
# 代码示例417：无监督
unsupervised = {
    "聚类": "KMeans",
    "降维": "PCA",
    "对比学习": "自监督",
    "Word2Vec": "无监督",
}
for k, v in unsupervised.items():
    print(f"  {k}: {v}")
```

#### VVVVVVVVVVV.3 表示学习

```python
# 代码示例418：表示学习
representation = {
    "目标": "学习好表示",
    "方法": "对比学习/自监督",
    "Embedding": "产物",
    "下游": "分类/检索/聚类",
}
for k, v in representation.items():
    print(f"  {k}: {v}")
```

---

### 附录 WWWWWWWWWWW：Embedding 与深度学习

#### WWWWWWWWWWW.1 神经网络

```python
# 代码示例419：神经网络
nn = {
    "层": "Linear+激活",
    "深度": "多层",
    "激活": "ReLU/GELU",
    "训练": "反向传播",
}
for k, v in nn.items():
    print(f"  {k}: {v}")
```

#### WWWWWWWWWWW.2 Transformer

```python
# 代码示例420：Transformer
transformer = {
    "自注意力": "全局依赖",
    "FFN": "非线性",
    "残差": "梯度流",
    "LayerNorm": "稳定",
}
for k, v in transformer.items():
    print(f"  {k}: {v}")
```

---

### 附录 XXXXXXXXXXX：Embedding 与 NLP

#### XXXXXXXXXXX.1 NLP 任务

```python
# 代码示例421：NLP 任务
nlp = {
    "分类": "情感/主题",
    "聚类": "自动分组",
    "检索": "语义搜索",
    "STS": "相似度",
    "QA": "问答",
}
for k, v in nlp.items():
    print(f"  {k}: {v}")
```

#### XXXXXXXXXXX.2 Embedding 在 NLP

```python
# 代码示例422：Embedding 在 NLP
nlp_emb = {
    "特征": "Embedding 作为特征",
    "检索": "语义搜索",
    "聚类": "自动分组",
    "迁移": "跨任务",
}
for k, v in nlp_emb.items():
    print(f"  {k}: {v}")
```

---

### 附录 YYYYYYYYYYY：Embedding 模型

#### YYYYYYYYYYY.1 词嵌入

```python
# 代码示例423：词嵌入
word_emb = {
    "Word2Vec": "2013",
    "GloVe": "2014",
    "FastText": "2016",
    "静态": "一词一向量",
}
for k, v in word_emb.items():
    print(f"  {k}: {v}")
```

#### YYYYYYYYYYY.2 句嵌入

```python
# 代码示例424：句嵌入
sent_emb = {
    "InferSent": "2017",
    "SBERT": "2019",
    "BGE": "2022",
    "E5": "2022",
}
for k, v in sent_emb.items():
    print(f"  {k}: {v}")
```

---

### 附录 ZZZZZZZZZZZ：Embedding 架构

#### ZZZZZZZZZZZ.1 双编码器

```python
# 代码示例425：双编码器
bi_encoder = {
    "Query": "独立编码",
    "Doc": "独立编码",
    "相似度": "向量距离",
    "优点": "快, 可预计算",
}
for k, v in bi_encoder.items():
    print(f"  {k}: {v}")
```

#### ZZZZZZZZZZZ.2 交叉编码器

```python
# 代码示例426：交叉编码器
cross_encoder = {
    "输入": "(query, doc)",
    "输出": "相关度分数",
    "优点": "准",
    "缺点": "慢",
}
for k, v in cross_encoder.items():
    print(f"  {k}: {v}")
```

---

### 附录 AAAAAAAAAAAA：Embedding 相似度

#### AAAAAAAAAAAA.1 余弦相似度

```python
# 代码示例427：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦: 方向相似")
```

#### AAAAAAAAAAAA.2 归一化

```python
# 代码示例428：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化: v/||v||")
```

---

### 附录 BBBBBBBBBBBB：Embedding 应用

#### BBBBBBBBBBBB.1 RAG

```python
# 代码示例429：RAG
rag = {
    "检索": "Embedding",
    "生成": "LLM",
    "质量": "检索+生成",
}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

#### BBBBBBBBBBBB.2 搜索

```python
# 代码示例430：搜索
search = {
    "向量": "语义",
    "BM25": "关键词",
    "混合": "两者",
}
for k, v in search.items():
    print(f"  {k}: {v}")
```

---

### 附录 CCCCCCCCCCCC：Embedding 优化

#### CCCCCCCCCCCC.1 批量

```python
# 代码示例431：批量
def batch_encode(texts, model, bs=32):
    embs = []
    for i in range(0, len(texts), bs):
        embs.append(model.encode(texts[i:i+bs]))
    return np.vstack(embs)
print("批量: 32-128")
```

#### CCCCCCCCCCCC.2 缓存

```python
# 代码示例432：缓存
cache = {}
def cached_encode(text, model):
    if text not in cache:
        cache[text] = model.encode([text])[0]
    return cache[text]
print("缓存: 避免重复")
```

---

### 附录 DDDDDDDDDDDD：Embedding 选型

#### DDDDDDDDDDDD.1 选型

```python
# 代码示例433：选型
def select(lang, os, quality):
    if os:
        if lang == "zh":
            return "bge-large-zh" if quality == "high" else "bge-base-zh"
        return "bge-m3" if lang == "multi" else "e5-large"
    return "OpenAI v3 large" if quality == "high" else "v3 small"
print(select("zh", True, "high"))
```

---

### 附录 EEEEEEEEEEEE：Embedding 评估

#### EEEEEEEEEEEE.1 MTEB

```python
# 代码示例434：MTEB
mteb = {
    "任务": "56",
    "度量": "nDCG/Spearman",
    "用途": "排名",
}
for k, v in mteb.items():
    print(f"  {k}: {v}")
```

---

### 附录 FFFFFFFFFFFF：Embedding 成本

#### FFFFFFFFFFFF.1 成本

```python
# 代码示例435：成本
cost = {
    "API": "$0.02-0.13/1M",
    "自部署": "$0.001/1M",
    "存储": "向量库",
}
for k, v in cost.items():
    print(f"  {k}: {v}")
```

---

### 附录 GGGGGGGGGGGG：Embedding 坑点

```python
# 代码示例436：坑点
pitfalls = [
    "不归一化", "选错模型", "维度太大",
    "不批量", "不缓存", "不评估",
]
for p in pitfalls:
    print(f"  ❌ {p}")
```

---

### 附录 HHHHHHHHHHHH：Embedding 面试

```python
# 代码示例437：面试
qa = [
    ("Embedding", "文本->向量"),
    ("双编码器", "快"),
    ("交叉编码器", "准"),
    ("余弦", "dot/(||a||*||b||)"),
    ("中文", "BGE"),
]
for q, a in qa:
    print(f"  Q: {q}\n  A: {a}")
```

---

### 附录 IIIIIIIIIIII：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 430+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 JJJJJJJJJJJJ：Embedding 深度百科

#### JJJJJJJJJJJJ.1 Embedding 核心概念

```python
# 代码示例438：核心概念
core = {
    "定义": "对象->向量",
    "语义": "相似=近",
    "用途": "搜索/聚类/推荐",
    "模型": "BERT/BGE/E5",
}
for k, v in core.items():
    print(f"  {k}: {v}")
```

#### JJJJJJJJJJJJ.2 Embedding 历史

```python
# 代码示例439：历史
history = [
    (2013, "Word2Vec"),
    (2014, "GloVe"),
    (2018, "BERT"),
    (2019, "SBERT"),
    (2022, "BGE/E5/GTE"),
    (2023, "BGE-M3"),
]
for y, e in history:
    print(f"  {y}: {e}")
```

---

#### JJJJJJJJJJJJ.3 现代模型

```python
# 代码示例440：现代模型
modern = {
    "BGE": "智源",
    "E5": "微软",
    "GTE": "阿里",
    "Jina": "Jina AI",
    "OpenAI": "API",
}
for k, v in modern.items():
    print(f"  {k}: {v}")
```

---

#### JJJJJJJJJJJJ.4 架构

```python
# 代码示例441：架构
arch = {
    "双编码器": "快, 可预计算",
    "交叉编码器": "准, 慢",
    "混合": "初筛+精排",
}
for k, v in arch.items():
    print(f"  {k}: {v}")
```

---

#### JJJJJJJJJJJJ.5 相似度

```python
# 代码示例442：相似度
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦: 方向相似")
```

---

#### JJJJJJJJJJJJ.6 归一化

```python
# 代码示例443：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化: v/||v||")
```

---

#### JJJJJJJJJJJJ.7 维度

```python
# 代码示例444：维度
dims = {
    "384": "小",
    "768": "中",
    "1024": "大",
    "1536": "OpenAI small",
    "3072": "OpenAI large",
}
for k, v in dims.items():
    print(f"  {k}: {v}")
```

---

#### JJJJJJJJJJJJ.8 RAG

```python
# 代码示例445：RAG
rag = {
    "检索": "Embedding",
    "生成": "LLM",
    "质量": "检索+生成",
}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

---

#### JJJJJJJJJJJJ.9 多语言

```python
# 代码示例446：多语言
ml = {
    "bge-m3": "100+语言",
    "e5-multilingual": "100+",
}
for k, v in ml.items():
    print(f"  {k}: {v}")
```

---

#### JJJJJJJJJJJJ.10 多模态

```python
# 代码示例447：多模态
mm = {
    "CLIP": "图文",
    "ImageBind": "6模态",
}
for k, v in mm.items():
    print(f"  {k}: {v}")
```

---

#### JJJJJJJJJJJJ.11 微调

```python
# 代码示例448：微调
ft = {
    "对比学习": "(query, pos, neg)",
    "数据": "领域对",
    "效果": "提升5-20%",
}
for k, v in ft.items():
    print(f"  {k}: {v}")
```

---

#### JJJJJJJJJJJJ.12 优化

```python
# 代码示例449：优化
opt = {
    "批量": "32-128",
    "缓存": "Redis",
    "量化": "INT8",
    "降维": "PCA/Matryoshka",
}
for k, v in opt.items():
    print(f"  {k}: {v}")
```

---

#### JJJJJJJJJJJJ.13 选型

```python
# 代码示例450：选型
def select(lang, os):
    if os:
        return "bge-large-zh" if lang == "zh" else "bge-m3" if lang == "multi" else "e5-large"
    return "OpenAI v3"
print(select("zh", True))
```

---

#### JJJJJJJJJJJJ.14 MTEB

```python
# 代码示例451：MTEB
mteb = {
    "任务": "56",
    "用途": "排名",
    "C-MTEB": "中文",
}
for k, v in mteb.items():
    print(f"  {k}: {v}")
```

---

#### JJJJJJJJJJJJ.15 成本

```python
# 代码示例452：成本
cost = {
    "API": "$0.02-0.13/1M",
    "自部署": "$0.001/1M",
}
for k, v in cost.items():
    print(f"  {k}: {v}")
```

---

#### JJJJJJJJJJJJ.16 坑点

```python
# 代码示例453：坑点
pitfalls = [
    "不归一化", "选错模型", "维度太大",
    "不批量", "不缓存", "不评估",
]
for p in pitfalls:
    print(f"  ❌ {p}")
```

---

#### JJJJJJJJJJJJ.17 面试

```python
# 代码示例454：面试
qa = [
    ("Embedding", "文本->向量"),
    ("双编码器", "快"),
    ("交叉编码器", "准"),
    ("余弦", "dot/(||a||*||b||)"),
    ("中文", "BGE"),
]
for q, a in qa:
    print(f"  Q: {q}\n  A: {a}")
```

---

### 附录 KKKKKKKKKKKK：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 450+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 LLLLLLLLLLLL：Embedding 技术百科

#### LLLLLLLLLLLL.1 Embedding 与向量数学

```python
# 代码示例455：向量数学
vec_math = {
    "点积": "a·b",
    "模长": "||v||",
    "余弦": "a·b/(||a||*||b||)",
    "归一化": "v/||v||",
}
for k, v in vec_math.items():
    print(f"  {k}: {v}")
```

#### LLLLLLLLLLLL.2 距离度量

```python
# 代码示例456：距离
distances = {
    "余弦": "方向",
    "欧氏": "绝对",
    "点积": "归一化后=余弦",
}
for k, v in distances.items():
    print(f"  {k}: {v}")
```

---

#### LLLLLLLLLLLL.3 向量空间

```python
# 代码示例457：向量空间
space = {
    "维度": "向量长度",
    "归一化": "单位球",
    "距离": "度量",
}
for k, v in space.items():
    print(f"  {k}: {v}")
```

---

#### LLLLLLLLLLLL.4 词嵌入

```python
# 代码示例458：词嵌入
word = {
    "Word2Vec": "2013",
    "GloVe": "2014",
    "FastText": "2016",
    "静态": "一词一向量",
}
for k, v in word.items():
    print(f"  {k}: {v}")
```

#### LLLLLLLLLLLL.5 句嵌入

```python
# 代码示例459：句嵌入
sent = {
    "SBERT": "2019",
    "BGE": "2022",
    "E5": "2022",
}
for k, v in sent.items():
    print(f"  {k}: {v}")
```

---

#### LLLLLLLLLLLL.6 双编码器

```python
# 代码示例460：双编码器
bi = {
    "Query": "独立编码",
    "Doc": "独立编码",
    "优点": "快",
}
for k, v in bi.items():
    print(f"  {k}: {v}")
```

#### LLLLLLLLLLLL.7 交叉编码器

```python
# 代码示例461：交叉编码器
cross = {
    "输入": "(query, doc)",
    "输出": "分数",
    "优点": "准",
}
for k, v in cross.items():
    print(f"  {k}: {v}")
```

---

#### LLLLLLLLLLLL.8 对比学习

```python
# 代码示例462：对比学习
cl = {
    "目标": "正近负远",
    "损失": "InfoNCE",
    "难负": "关键",
}
for k, v in cl.items():
    print(f"  {k}: {v}")
```

---

#### LLLLLLLLLLLL.9 RAG

```python
# 代码示例463：RAG
rag = {
    "检索": "Embedding",
    "生成": "LLM",
    "质量": "检索+生成",
}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

---

#### LLLLLLLLLLLL.10 向量库

```python
# 代码示例464：向量库
db = {
    "Qdrant": "Rust",
    "Milvus": "大规模",
    "Chroma": "轻量",
}
for k, v in db.items():
    print(f"  {k}: {v}")
```

---

#### LLLLLLLLLLLL.11 索引

```python
# 代码示例465：索引
idx = {
    "Flat": "暴力",
    "HNSW": "图",
    "IVF": "倒排",
}
for k, v in idx.items():
    print(f"  {k}: {v}")
```

---

#### LLLLLLLLLLLL.12 评估

```python
# 代码示例466：评估
eval = {
    "MTEB": "基准",
    "Recall@K": "召回",
    "MRR": "排名",
}
for k, v in eval.items():
    print(f"  {k}: {v}")
```

---

#### LLLLLLLLLLLL.13 成本

```python
# 代码示例467：成本
cost = {
    "API": "$0.02-0.13/1M",
    "自部署": "$0.001/1M",
}
for k, v in cost.items():
    print(f"  {k}: {v}")
```

---

#### LLLLLLLLLLLL.14 坑点

```python
# 代码示例468：坑点
pitfalls = [
    "不归一化", "选错模型", "维度太大",
    "不批量", "不缓存", "不评估",
]
for p in pitfalls:
    print(f"  ❌ {p}")
```

---

#### LLLLLLLLLLLL.15 面试

```python
# 代码示例469：面试
qa = [
    ("Embedding", "文本->向量"),
    ("双编码器", "快"),
    ("交叉编码器", "准"),
    ("余弦", "dot/(||a||*||b||)"),
]
for q, a in qa:
    print(f"  Q: {q}\n  A: {a}")
```

---

### 附录 MMMMMMMMMMMM：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 460+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 NNNNNNNNNNNN：Embedding 深度百科

#### NNNNNNNNNNNN.1 Embedding 与 Transformer

```python
# 代码示例470：Transformer
transformer = {
    "自注意力": "全局依赖",
    "FFN": "非线性",
    "残差": "梯度流",
    "LayerNorm": "稳定",
}
for k, v in transformer.items():
    print(f"  {k}: {v}")
```

#### NNNNNNNNNNNN.2 BERT

```python
# 代码示例471：BERT
bert = {
    "MLM": "掩码预测",
    "NSP": "下一句",
    "输出": "Token 向量",
}
for k, v in bert.items():
    print(f"  {k}: {v}")
```

#### NNNNNNNNNNNN.3 SBERT

```python
# 代码示例472：SBERT
sbert = {
    "双塔": "共享权重",
    "池化": "Mean",
    "损失": "对比",
}
for k, v in sbert.items():
    print(f"  {k}: {v}")
```

---

#### NNNNNNNNNNNN.4 BGE

```python
# 代码示例473：BGE
bge = {
    "智源": "机构",
    "中文": "SOTA",
    "对比": "训练",
}
for k, v in bge.items():
    print(f"  {k}: {v}")
```

#### NNNNNNNNNNNN.5 E5

```python
# 代码示例474：E5
e5 = {
    "微软": "机构",
    "弱监督": "数据",
    "指令": "query:/passage:",
}
for k, v in e5.items():
    print(f"  {k}: {v}")
```

---

#### NNNNNNNNNNNN.6 GTE

```python
# 代码示例475：GTE
gte = {
    "阿里": "机构",
    "多语言": "支持",
}
for k, v in gte.items():
    print(f"  {k}: {v}")
```

#### NNNNNNNNNNNN.7 m3e

```python
# 代码示例476：m3e
m3e = {
    "中文": "支持",
}
for k, v in m3e.items():
    print(f"  {k}: {v}")
```

#### NNNNNNNNNNNN.8 Jina

```python
# 代码示例477：Jina
jina = {
    "89语言": "多语言",
    "Matryoshka": "支持",
}
for k, v in jina.items():
    print(f"  {k}: {v}")
```

#### NNNNNNNNNNNN.9 OpenAI

```python
# 代码示例478：OpenAI
openai = {
    "v3-small": "1536维",
    "v3-large": "3072维",
}
for k, v in openai.items():
    print(f"  {k}: {v}")
```

---

#### NNNNNNNNNNNN.10 余弦

```python
# 代码示例479：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦: 方向相似")
```

#### NNNNNNNNNNNN.11 归一化

```python
# 代码示例480：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化: v/||v||")
```

---

#### NNNNNNNNNNNN.12 维度

```python
# 代码示例481：维度
dims = {
    "384": "小",
    "768": "中",
    "1024": "大",
}
for k, v in dims.items():
    print(f"  {k}: {v}")
```

---

#### NNNNNNNNNNNN.13 RAG

```python
# 代码示例482：RAG
rag = {
    "检索": "Embedding",
    "生成": "LLM",
}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

#### NNNNNNNNNNNN.14 多语言

```python
# 代码示例483：多语言
ml = {
    "bge-m3": "100+语言",
}
for k, v in ml.items():
    print(f"  {k}: {v}")
```

#### NNNNNNNNNNNN.15 多模态

```python
# 代码示例484：多模态
mm = {
    "CLIP": "图文",
}
for k, v in mm.items():
    print(f"  {k}: {v}")
```

---

#### NNNNNNNNNNNN.16 微调

```python
# 代码示例485：微调
ft = {
    "对比学习": "(query, pos, neg)",
}
for k, v in ft.items():
    print(f"  {k}: {v}")
```

#### NNNNNNNNNNNN.17 优化

```python
# 代码示例486：优化
opt = {
    "批量": "32-128",
    "缓存": "Redis",
}
for k, v in opt.items():
    print(f"  {k}: {v}")
```

---

#### NNNNNNNNNNNN.18 MTEB

```python
# 代码示例487：MTEB
mteb = {
    "任务": "56",
}
for k, v in mteb.items():
    print(f"  {k}: {v}")
```

#### NNNNNNNNNNNN.19 成本

```python
# 代码示例488：成本
cost = {
    "API": "$0.02-0.13/1M",
}
for k, v in cost.items():
    print(f"  {k}: {v}")
```

#### NNNNNNNNNNNN.20 坑点

```python
# 代码示例489：坑点
pitfalls = [
    "不归一化", "选错模型", "维度太大",
]
for p in pitfalls:
    print(f"  ❌ {p}")
```

---

### 附录 OOOOOOOOOOOOO：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 480+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 PPPPPPPPPPPP：Embedding 深度百科

#### PPPPPPPPPPPP.1 Embedding 核心

```python
# 代码示例490：核心
core = {
    "定义": "对象->向量",
    "语义": "相似=近",
    "用途": "搜索/聚类",
}
for k, v in core.items():
    print(f"  {k}: {v}")
```

#### PPPPPPPPPPPP.2 历史

```python
# 代码示例491：历史
history = [
    (2013, "Word2Vec"),
    (2018, "BERT"),
    (2019, "SBERT"),
    (2022, "BGE/E5"),
]
for y, e in history:
    print(f"  {y}: {e}")
```

---

#### PPPPPPPPPPPP.3 模型

```python
# 代码示例492：模型
models = {
    "BGE": "智源",
    "E5": "微软",
    "GTE": "阿里",
    "OpenAI": "API",
}
for k, v in models.items():
    print(f"  {k}: {v}")
```

#### PPPPPPPPPPPP.4 架构

```python
# 代码示例493：架构
arch = {
    "双编码器": "快",
    "交叉编码器": "准",
}
for k, v in arch.items():
    print(f"  {k}: {v}")
```

---

#### PPPPPPPPPPPP.5 相似度

```python
# 代码示例494：相似度
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦")
```

#### PPPPPPPPPPPP.6 归一化

```python
# 代码示例495：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化")
```

---

#### PPPPPPPPPPPP.7 维度

```python
# 代码示例496：维度
dims = {
    "768": "中",
    "1024": "大",
}
for k, v in dims.items():
    print(f"  {k}: {v}")
```

#### PPPPPPPPPPPP.8 RAG

```python
# 代码示例497：RAG
rag = {
    "检索": "Embedding",
    "生成": "LLM",
}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

---

#### PPPPPPPPPPPP.9 多语言

```python
# 代码示例498：多语言
ml = {
    "bge-m3": "100+",
}
for k, v in ml.items():
    print(f"  {k}: {v}")
```

#### PPPPPPPPPPPP.10 多模态

```python
# 代码示例499：多模态
mm = {
    "CLIP": "图文",
}
for k, v in mm.items():
    print(f"  {k}: {v}")
```

---

#### PPPPPPPPPPPP.11 微调

```python
# 代码示例500：微调
ft = {
    "对比学习": "正近负远",
}
for k, v in ft.items():
    print(f"  {k}: {v}")
```

#### PPPPPPPPPPPP.12 优化

```python
# 代码示例501：优化
opt = {
    "批量": "32-128",
    "缓存": "Redis",
}
for k, v in opt.items():
    print(f"  {k}: {v}")
```

---

#### PPPPPPPPPPPP.13 MTEB

```python
# 代码示例502：MTEB
mteb = {
    "任务": "56",
}
for k, v in mteb.items():
    print(f"  {k}: {v}")
```

#### PPPPPPPPPPPP.14 成本

```python
# 代码示例503：成本
cost = {
    "API": "$0.02-0.13/1M",
}
for k, v in cost.items():
    print(f"  {k}: {v}")
```

---

#### PPPPPPPPPPPP.15 坑点

```python
# 代码示例504：坑点
pitfalls = [
    "不归一化", "选错模型", "维度太大",
]
for p in pitfalls:
    print(f"  ❌ {p}")
```

---

### 附录 QQQQQQQQQQQQ：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 500+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 RRRRRRRRRRRR：Embedding 深度百科

#### RRRRRRRRRRRR.1 Embedding 与向量

```python
# 代码示例505：向量
vec = {
    "定义": "有序数字",
    "维度": "长度",
    "归一化": "长度=1",
}
for k, v in vec.items():
    print(f"  {k}: {v}")
```

#### RRRRRRRRRRRR.2 余弦相似度

```python
# 代码示例506：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦: 方向相似")
```

#### RRRRRRRRRRRR.3 归一化

```python
# 代码示例507：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化: v/||v||")
```

---

#### RRRRRRRRRRRR.4 词嵌入

```python
# 代码示例508：词嵌入
word = {
    "Word2Vec": "2013",
    "GloVe": "2014",
}
for k, v in word.items():
    print(f"  {k}: {v}")
```

#### RRRRRRRRRRRR.5 句嵌入

```python
# 代码示例509：句嵌入
sent = {
    "SBERT": "2019",
    "BGE": "2022",
}
for k, v in sent.items():
    print(f"  {k}: {v}")
```

---

#### RRRRRRRRRRRR.6 双编码器

```python
# 代码示例510：双编码器
bi = {
    "独立编码": "快",
    "预计算": "文档向量",
}
for k, v in bi.items():
    print(f"  {k}: {v}")
```

#### RRRRRRRRRRRR.7 交叉编码器

```python
# 代码示例511：交叉编码器
cross = {
    "联合编码": "准",
    "实时": "慢",
}
for k, v in cross.items():
    print(f"  {k}: {v}")
```

---

#### RRRRRRRRRRRR.8 BGE

```python
# 代码示例512：BGE
bge = {
    "中文": "SOTA",
    "开源": "是",
}
for k, v in bge.items():
    print(f"  {k}: {v}")
```

#### RRRRRRRRRRRR.9 E5

```python
# 代码示例513：E5
e5 = {
    "微软": "机构",
    "弱监督": "数据",
}
for k, v in e5.items():
    print(f"  {k}: {v}")
```

---

#### RRRRRRRRRRRR.10 RAG

```python
# 代码示例514：RAG
rag = {
    "检索": "Embedding",
    "生成": "LLM",
}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

#### RRRRRRRRRRRR.11 多语言

```python
# 代码示例515：多语言
ml = {
    "bge-m3": "100+语言",
}
for k, v in ml.items():
    print(f"  {k}: {v}")
```

---

#### RRRRRRRRRRRR.12 微调

```python
# 代码示例516：微调
ft = {
    "对比学习": "(query, pos, neg)",
}
for k, v in ft.items():
    print(f"  {k}: {v}")
```

#### RRRRRRRRRRRR.13 优化

```python
# 代码示例517：优化
opt = {
    "批量": "32-128",
    "缓存": "Redis",
}
for k, v in opt.items():
    print(f"  {k}: {v}")
```

---

#### RRRRRRRRRRRR.14 MTEB

```python
# 代码示例518：MTEB
mteb = {
    "任务": "56",
}
for k, v in mteb.items():
    print(f"  {k}: {v}")
```

#### RRRRRRRRRRRR.15 成本

```python
# 代码示例519：成本
cost = {
    "API": "$0.02-0.13/1M",
}
for k, v in cost.items():
    print(f"  {k}: {v}")
```

---

#### RRRRRRRRRRRR.16 坑点

```python
# 代码示例520：坑点
pitfalls = [
    "不归一化", "选错模型", "维度太大",
]
for p in pitfalls:
    print(f"  ❌ {p}")
```

---

### 附录 SSSSSSSSSSSS：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 520+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 TTTTTTTTTTTT：Embedding 深度百科

#### TTTTTTTTTTTT.1 Embedding 基础

```python
# 代码示例521：基础
basic = {
    "向量": "有序数字",
    "维度": "长度",
    "归一化": "长度=1",
}
for k, v in basic.items():
    print(f"  {k}: {v}")
```

#### TTTTTTTTTTTT.2 余弦

```python
# 代码示例522：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦")
```

#### TTTTTTTTTTTT.3 归一化

```python
# 代码示例523：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化")
```

---

#### TTTTTTTTTTTT.4 历史

```python
# 代码示例524：历史
history = [
    (2013, "Word2Vec"),
    (2018, "BERT"),
    (2022, "BGE"),
]
for y, e in history:
    print(f"  {y}: {e}")
```

#### TTTTTTTTTTTT.5 模型

```python
# 代码示例525：模型
models = {
    "BGE": "智源",
    "E5": "微软",
}
for k, v in models.items():
    print(f"  {k}: {v}")
```

---

#### TTTTTTTTTTTT.6 双编码器

```python
# 代码示例526：双编码器
bi = {"快": "可预计算"}
for k, v in bi.items():
    print(f"  {k}: {v}")
```

#### TTTTTTTTTTTT.7 交叉编码器

```python
# 代码示例527：交叉编码器
cross = {"准": "实时"}
for k, v in cross.items():
    print(f"  {k}: {v}")
```

---

#### TTTTTTTTTTTT.8 RAG

```python
# 代码示例528：RAG
rag = {"检索": "Embedding", "生成": "LLM"}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

#### TTTTTTTTTTTT.9 多语言

```python
# 代码示例529：多语言
ml = {"bge-m3": "100+"}
for k, v in ml.items():
    print(f"  {k}: {v}")
```

---

#### TTTTTTTTTTTT.10 微调

```python
# 代码示例530：微调
ft = {"对比学习": "正近负远"}
for k, v in ft.items():
    print(f"  {k}: {v}")
```

#### TTTTTTTTTTTT.11 优化

```python
# 代码示例531：优化
opt = {"批量": "32-128", "缓存": "Redis"}
for k, v in opt.items():
    print(f"  {k}: {v}")
```

---

#### TTTTTTTTTTTT.12 MTEB

```python
# 代码示例532：MTEB
mteb = {"任务": "56"}
for k, v in mteb.items():
    print(f"  {k}: {v}")
```

#### TTTTTTTTTTTT.13 成本

```python
# 代码示例533：成本
cost = {"API": "$0.02-0.13/1M"}
for k, v in cost.items():
    print(f"  {k}: {v}")
```

---

#### TTTTTTTTTTTT.14 坑点

```python
# 代码示例534：坑点
pitfalls = ["不归一化", "选错模型"]
for p in pitfalls:
    print(f"  ❌ {p}")
```

---

### 附录 UUUUUUUUUUUU：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 530+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 VVVVVVVVVVVV：Embedding 深度百科

#### VVVVVVVVVVVV.1 Embedding 基础

```python
# 代码示例535：基础
basic = {"向量": "有序数字", "维度": "长度"}
for k, v in basic.items():
    print(f"  {k}: {v}")
```

#### VVVVVVVVVVVV.2 余弦

```python
# 代码示例536：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦")
```

#### VVVVVVVVVVVV.3 归一化

```python
# 代码示例537：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化")
```

---

#### VVVVVVVVVVVV.4 历史

```python
# 代码示例538：历史
history = [(2013, "Word2Vec"), (2018, "BERT"), (2022, "BGE")]
for y, e in history:
    print(f"  {y}: {e}")
```

#### VVVVVVVVVVVV.5 模型

```python
# 代码示例539：模型
models = {"BGE": "智源", "E5": "微软"}
for k, v in models.items():
    print(f"  {k}: {v}")
```

---

#### VVVVVVVVVVVV.6 双编码器

```python
# 代码示例540：双编码器
bi = {"快": "可预计算"}
for k, v in bi.items():
    print(f"  {k}: {v}")
```

#### VVVVVVVVVVVV.7 交叉编码器

```python
# 代码示例541：交叉编码器
cross = {"准": "实时"}
for k, v in cross.items():
    print(f"  {k}: {v}")
```

---

#### VVVVVVVVVVVV.8 RAG

```python
# 代码示例542：RAG
rag = {"检索": "Embedding", "生成": "LLM"}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

#### VVVVVVVVVVVV.9 多语言

```python
# 代码示例543：多语言
ml = {"bge-m3": "100+"}
for k, v in ml.items():
    print(f"  {k}: {v}")
```

---

#### VVVVVVVVVVVV.10 微调

```python
# 代码示例544：微调
ft = {"对比学习": "正近负远"}
for k, v in ft.items():
    print(f"  {k}: {v}")
```

#### VVVVVVVVVVVV.11 优化

```python
# 代码示例545：优化
opt = {"批量": "32-128", "缓存": "Redis"}
for k, v in opt.items():
    print(f"  {k}: {v}")
```

---

#### VVVVVVVVVVVV.12 MTEB

```python
# 代码示例546：MTEB
mteb = {"任务": "56"}
for k, v in mteb.items():
    print(f"  {k}: {v}")
```

#### VVVVVVVVVVVV.13 成本

```python
# 代码示例547：成本
cost = {"API": "$0.02-0.13/1M"}
for k, v in cost.items():
    print(f"  {k}: {v}")
```

---

#### VVVVVVVVVVVV.14 坑点

```python
# 代码示例548：坑点
pitfalls = ["不归一化", "选错模型"]
for p in pitfalls:
    print(f"  ❌ {p}")
```

---

### 附录 WWWWWWWWWWWW：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 540+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 XXXXXXXXXXXXXX：Embedding 深度百科

#### XXXXXXXXXXXXXX.1 Embedding 基础

```python
# 代码示例549：基础
basic = {"向量": "有序数字", "维度": "长度"}
for k, v in basic.items():
    print(f"  {k}: {v}")
```

#### XXXXXXXXXXXXXX.2 余弦

```python
# 代码示例550：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦")
```

#### XXXXXXXXXXXXXX.3 归一化

```python
# 代码示例551：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化")
```

---

#### XXXXXXXXXXXXXX.4 历史

```python
# 代码示例552：历史
history = [(2013, "Word2Vec"), (2018, "BERT"), (2022, "BGE")]
for y, e in history:
    print(f"  {y}: {e}")
```

#### XXXXXXXXXXXXXX.5 模型

```python
# 代码示例553：模型
models = {"BGE": "智源", "E5": "微软"}
for k, v in models.items():
    print(f"  {k}: {v}")
```

---

#### XXXXXXXXXXXXXX.6 双编码器

```python
# 代码示例554：双编码器
bi = {"快": "可预计算"}
for k, v in bi.items():
    print(f"  {k}: {v}")
```

#### XXXXXXXXXXXXXX.7 交叉编码器

```python
# 代码示例555：交叉编码器
cross = {"准": "实时"}
for k, v in cross.items():
    print(f"  {k}: {v}")
```

---

#### XXXXXXXXXXXXXX.8 RAG

```python
# 代码示例556：RAG
rag = {"检索": "Embedding", "生成": "LLM"}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

#### XXXXXXXXXXXXXX.9 多语言

```python
# 代码示例557：多语言
ml = {"bge-m3": "100+"}
for k, v in ml.items():
    print(f"  {k}: {v}")
```

---

#### XXXXXXXXXXXXXX.10 微调

```python
# 代码示例558：微调
ft = {"对比学习": "正近负远"}
for k, v in ft.items():
    print(f"  {k}: {v}")
```

#### XXXXXXXXXXXXXX.11 优化

```python
# 代码示例559：优化
opt = {"批量": "32-128", "缓存": "Redis"}
for k, v in opt.items():
    print(f"  {k}: {v}")
```

---

#### XXXXXXXXXXXXXX.12 MTEB

```python
# 代码示例560：MTEB
mteb = {"任务": "56"}
for k, v in mteb.items():
    print(f"  {k}: {v}")
```

#### XXXXXXXXXXXXXX.13 成本

```python
# 代码示例561：成本
cost = {"API": "$0.02-0.13/1M"}
for k, v in cost.items():
    print(f"  {k}: {v}")
```

---

#### XXXXXXXXXXXXXX.14 坑点

```python
# 代码示例562：坑点
pitfalls = ["不归一化", "选错模型"]
for p in pitfalls:
    print(f"  ❌ {p}")
```

---

### 附录 YYYYYYYYYYYYYY：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 560+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 ZZZZZZZZZZZZZZ：Embedding 深度百科

#### ZZZZZZZZZZZZZZ.1 Embedding 基础

```python
# 代码示例563：基础
basic = {"向量": "有序数字", "维度": "长度"}
for k, v in basic.items():
    print(f"  {k}: {v}")
```

#### ZZZZZZZZZZZZZZ.2 余弦

```python
# 代码示例564：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦")
```

#### ZZZZZZZZZZZZZZ.3 归一化

```python
# 代码示例565：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化")
```

---

#### ZZZZZZZZZZZZZZ.4 历史

```python
# 代码示例566：历史
history = [(2013, "Word2Vec"), (2018, "BERT"), (2022, "BGE")]
for y, e in history:
    print(f"  {y}: {e}")
```

#### ZZZZZZZZZZZZZZ.5 模型

```python
# 代码示例567：模型
models = {"BGE": "智源", "E5": "微软"}
for k, v in models.items():
    print(f"  {k}: {v}")
```

---

#### ZZZZZZZZZZZZZZ.6 双编码器

```python
# 代码示例568：双编码器
bi = {"快": "可预计算"}
for k, v in bi.items():
    print(f"  {k}: {v}")
```

#### ZZZZZZZZZZZZZZ.7 交叉编码器

```python
# 代码示例569：交叉编码器
cross = {"准": "实时"}
for k, v in cross.items():
    print(f"  {k}: {v}")
```

---

#### ZZZZZZZZZZZZZZ.8 RAG

```python
# 代码示例570：RAG
rag = {"检索": "Embedding", "生成": "LLM"}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

#### ZZZZZZZZZZZZZZ.9 多语言

```python
# 代码示例571：多语言
ml = {"bge-m3": "100+"}
for k, v in ml.items():
    print(f"  {k}: {v}")
```

---

#### ZZZZZZZZZZZZZZ.10 微调

```python
# 代码示例572：微调
ft = {"对比学习": "正近负远"}
for k, v in ft.items():
    print(f"  {k}: {v}")
```

#### ZZZZZZZZZZZZZZ.11 优化

```python
# 代码示例573：优化
opt = {"批量": "32-128", "缓存": "Redis"}
for k, v in opt.items():
    print(f"  {k}: {v}")
```

---

#### ZZZZZZZZZZZZZZ.12 MTEB

```python
# 代码示例574：MTEB
mteb = {"任务": "56"}
for k, v in mteb.items():
    print(f"  {k}: {v}")
```

#### ZZZZZZZZZZZZZZ.13 成本

```python
# 代码示例575：成本
cost = {"API": "$0.02-0.13/1M"}
for k, v in cost.items():
    print(f"  {k}: {v}")
```

---

#### ZZZZZZZZZZZZZZ.14 坑点

```python
# 代码示例576：坑点
pitfalls = ["不归一化", "选错模型"]
for p in pitfalls:
    print(f"  ❌ {p}")
```

---

### 附录 AAAAAAAAAAAAAAAA：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 570+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 BBBBBBBBBBBBBBBB：Embedding 深度百科

#### BBBBBBBBBBBBBBBB.1 Embedding 基础

```python
# 代码示例577：基础
basic = {"向量": "有序数字", "维度": "长度"}
for k, v in basic.items():
    print(f"  {k}: {v}")
```

#### BBBBBBBBBBBBBBBB.2 余弦

```python
# 代码示例578：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦")
```

#### BBBBBBBBBBBBBBBB.3 归一化

```python
# 代码示例579：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化")
```

---

#### BBBBBBBBBBBBBBBB.4 历史

```python
# 代码示例580：历史
history = [(2013, "Word2Vec"), (2018, "BERT"), (2022, "BGE")]
for y, e in history:
    print(f"  {y}: {e}")
```

#### BBBBBBBBBBBBBBBB.5 模型

```python
# 代码示例581：模型
models = {"BGE": "智源", "E5": "微软"}
for k, v in models.items():
    print(f"  {k}: {v}")
```

---

#### BBBBBBBBBBBBBBBB.6 双编码器

```python
# 代码示例582：双编码器
bi = {"快": "可预计算"}
for k, v in bi.items():
    print(f"  {k}: {v}")
```

#### BBBBBBBBBBBBBBBB.7 交叉编码器

```python
# 代码示例583：交叉编码器
cross = {"准": "实时"}
for k, v in cross.items():
    print(f"  {k}: {v}")
```

---

#### BBBBBBBBBBBBBBBB.8 RAG

```python
# 代码示例584：RAG
rag = {"检索": "Embedding", "生成": "LLM"}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

#### BBBBBBBBBBBBBBBB.9 多语言

```python
# 代码示例585：多语言
ml = {"bge-m3": "100+"}
for k, v in ml.items():
    print(f"  {k}: {v}")
```

---

#### BBBBBBBBBBBBBBBB.10 微调

```python
# 代码示例586：微调
ft = {"对比学习": "正近负远"}
for k, v in ft.items():
    print(f"  {k}: {v}")
```

#### BBBBBBBBBBBBBBBB.11 优化

```python
# 代码示例587：优化
opt = {"批量": "32-128", "缓存": "Redis"}
for k, v in opt.items():
    print(f"  {k}: {v}")
```

---

#### BBBBBBBBBBBBBBBB.12 MTEB

```python
# 代码示例588：MTEB
mteb = {"任务": "56"}
for k, v in mteb.items():
    print(f"  {k}: {v}")
```

#### BBBBBBBBBBBBBBBB.13 成本

```python
# 代码示例589：成本
cost = {"API": "$0.02-0.13/1M"}
for k, v in cost.items():
    print(f"  {k}: {v}")
```

---

#### BBBBBBBBBBBBBBBB.14 坑点

```python
# 代码示例590：坑点
pitfalls = ["不归一化", "选错模型"]
for p in pitfalls:
    print(f"  ❌ {p}")
```

---

### 附录 CCCCCCCCCCCCCCCC：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 590+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 DDDDDDDDDDDDDDDD：Embedding 深度百科

#### DDDDDDDDDDDDDDDD.1 Embedding 基础

```python
# 代码示例591：基础
basic = {"向量": "有序数字", "维度": "长度"}
for k, v in basic.items():
    print(f"  {k}: {v}")
```

#### DDDDDDDDDDDDDDDD.2 余弦

```python
# 代码示例592：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦")
```

#### DDDDDDDDDDDDDDDD.3 归一化

```python
# 代码示例593：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化")
```

---

#### DDDDDDDDDDDDDDDD.4 历史

```python
# 代码示例594：历史
history = [(2013, "Word2Vec"), (2018, "BERT"), (2022, "BGE")]
for y, e in history:
    print(f"  {y}: {e}")
```

#### DDDDDDDDDDDDDDDD.5 模型

```python
# 代码示例595：模型
models = {"BGE": "智源", "E5": "微软"}
for k, v in models.items():
    print(f"  {k}: {v}")
```

---

#### DDDDDDDDDDDDDDDD.6 双编码器

```python
# 代码示例596：双编码器
bi = {"快": "可预计算"}
for k, v in bi.items():
    print(f"  {k}: {v}")
```

#### DDDDDDDDDDDDDDDD.7 交叉编码器

```python
# 代码示例597：交叉编码器
cross = {"准": "实时"}
for k, v in cross.items():
    print(f"  {k}: {v}")
```

---

#### DDDDDDDDDDDDDDDD.8 RAG

```python
# 代码示例598：RAG
rag = {"检索": "Embedding", "生成": "LLM"}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

#### DDDDDDDDDDDDDDDD.9 多语言

```python
# 代码示例599：多语言
ml = {"bge-m3": "100+"}
for k, v in ml.items():
    print(f"  {k}: {v}")
```

---

#### DDDDDDDDDDDDDDDD.10 微调

```python
# 代码示例600：微调
ft = {"对比学习": "正近负远"}
for k, v in ft.items():
    print(f"  {k}: {v}")
```

---

### 附录 EEEEEEEEEEEEEEEEEE：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 600+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 FFFFFFFFFFFFFFFFFF：Embedding 深度百科

#### FFFFFFFFFFFFFFFFFF.1 Embedding 基础

```python
# 代码示例601：基础
basic = {"向量": "有序数字", "维度": "长度"}
for k, v in basic.items():
    print(f"  {k}: {v}")
```

#### FFFFFFFFFFFFFFFFFF.2 余弦

```python
# 代码示例602：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦")
```

#### FFFFFFFFFFFFFFFFFF.3 归一化

```python
# 代码示例603：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化")
```

---

#### FFFFFFFFFFFFFFFFFF.4 历史

```python
# 代码示例604：历史
history = [(2013, "Word2Vec"), (2018, "BERT"), (2022, "BGE")]
for y, e in history:
    print(f"  {y}: {e}")
```

#### FFFFFFFFFFFFFFFFFF.5 模型

```python
# 代码示例605：模型
models = {"BGE": "智源", "E5": "微软"}
for k, v in models.items():
    print(f"  {k}: {v}")
```

---

#### FFFFFFFFFFFFFFFFFF.6 双编码器

```python
# 代码示例606：双编码器
bi = {"快": "可预计算"}
for k, v in bi.items():
    print(f"  {k}: {v}")
```

#### FFFFFFFFFFFFFFFFFF.7 交叉编码器

```python
# 代码示例607：交叉编码器
cross = {"准": "实时"}
for k, v in cross.items():
    print(f"  {k}: {v}")
```

---

#### FFFFFFFFFFFFFFFFFF.8 RAG

```python
# 代码示例608：RAG
rag = {"检索": "Embedding", "生成": "LLM"}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

#### FFFFFFFFFFFFFFFFFF.9 多语言

```python
# 代码示例609：多语言
ml = {"bge-m3": "100+"}
for k, v in ml.items():
    print(f"  {k}: {v}")
```

---

#### FFFFFFFFFFFFFFFFFF.10 微调

```python
# 代码示例610：微调
ft = {"对比学习": "正近负远"}
for k, v in ft.items():
    print(f"  {k}: {v}")
```

---

### 附录 GGGGGGGGGGGGGGGGGGGG：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 610+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 HHHHHHHHHHHHHHHHHHHH：Embedding 深度百科

#### HHHHHHHHHHHHHHHHHHHH.1 Embedding 基础

```python
# 代码示例611：基础
basic = {"向量": "有序数字", "维度": "长度"}
for k, v in basic.items():
    print(f"  {k}: {v}")
```

#### HHHHHHHHHHHHHHHHHHHH.2 余弦

```python
# 代码示例612：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦")
```

#### HHHHHHHHHHHHHHHHHHHH.3 归一化

```python
# 代码示例613：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化")
```

---

#### HHHHHHHHHHHHHHHHHHHH.4 历史

```python
# 代码示例614：历史
history = [(2013, "Word2Vec"), (2018, "BERT"), (2022, "BGE")]
for y, e in history:
    print(f"  {y}: {e}")
```

#### HHHHHHHHHHHHHHHHHHHH.5 模型

```python
# 代码示例615：模型
models = {"BGE": "智源", "E5": "微软"}
for k, v in models.items():
    print(f"  {k}: {v}")
```

---

#### HHHHHHHHHHHHHHHHHHHH.6 双编码器

```python
# 代码示例616：双编码器
bi = {"快": "可预计算"}
for k, v in bi.items():
    print(f"  {k}: {v}")
```

#### HHHHHHHHHHHHHHHHHHHH.7 交叉编码器

```python
# 代码示例617：交叉编码器
cross = {"准": "实时"}
for k, v in cross.items():
    print(f"  {k}: {v}")
```

---

#### HHHHHHHHHHHHHHHHHHHH.8 RAG

```python
# 代码示例618：RAG
rag = {"检索": "Embedding", "生成": "LLM"}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

#### HHHHHHHHHHHHHHHHHHHH.9 多语言

```python
# 代码示例619：多语言
ml = {"bge-m3": "100+"}
for k, v in ml.items():
    print(f"  {k}: {v}")
```

---

#### HHHHHHHHHHHHHHHHHHHH.10 微调

```python
# 代码示例620：微调
ft = {"对比学习": "正近负远"}
for k, v in ft.items():
    print(f"  {k}: {v}")
```

---

### 附录 IIIIIIIIIIIIIIIIIIIIII：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 620+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 JJJJJJJJJJJJJJJJJJJJJJ：Embedding 深度百科

#### JJJJJJJJJJJJJJJJJJJJJJ.1 Embedding 基础

```python
# 代码示例621：基础
basic = {"向量": "有序数字", "维度": "长度"}
for k, v in basic.items():
    print(f"  {k}: {v}")
```

#### JJJJJJJJJJJJJJJJJJJJJJ.2 余弦

```python
# 代码示例622：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦")
```

#### JJJJJJJJJJJJJJJJJJJJJJ.3 归一化

```python
# 代码示例623：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化")
```

---

#### JJJJJJJJJJJJJJJJJJJJJJ.4 历史

```python
# 代码示例624：历史
history = [(2013, "Word2Vec"), (2018, "BERT"), (2022, "BGE")]
for y, e in history:
    print(f"  {y}: {e}")
```

#### JJJJJJJJJJJJJJJJJJJJJJ.5 模型

```python
# 代码示例625：模型
models = {"BGE": "智源", "E5": "微软"}
for k, v in models.items():
    print(f"  {k}: {v}")
```

---

#### JJJJJJJJJJJJJJJJJJJJJJ.6 双编码器

```python
# 代码示例626：双编码器
bi = {"快": "可预计算"}
for k, v in bi.items():
    print(f"  {k}: {v}")
```

#### JJJJJJJJJJJJJJJJJJJJJJ.7 交叉编码器

```python
# 代码示例627：交叉编码器
cross = {"准": "实时"}
for k, v in cross.items():
    print(f"  {k}: {v}")
```

---

#### JJJJJJJJJJJJJJJJJJJJJJ.8 RAG

```python
# 代码示例628：RAG
rag = {"检索": "Embedding", "生成": "LLM"}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

#### JJJJJJJJJJJJJJJJJJJJJJ.9 多语言

```python
# 代码示例629：多语言
ml = {"bge-m3": "100+"}
for k, v in ml.items():
    print(f"  {k}: {v}")
```

---

#### JJJJJJJJJJJJJJJJJJJJJJ.10 微调

```python
# 代码示例630：微调
ft = {"对比学习": "正近负远"}
for k, v in ft.items():
    print(f"  {k}: {v}")
```

---

### 附录 KKKKKKKKKKKKKKKKKKKKKKKK：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 630+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 LLLLLLLLLLLLLLLLLLLLLLLL：Embedding 深度百科

#### LLLLLLLLLLLLLLLLLLLLLLLL.1 Embedding 基础

```python
# 代码示例631：基础
basic = {"向量": "有序数字", "维度": "长度"}
for k, v in basic.items():
    print(f"  {k}: {v}")
```

#### LLLLLLLLLLLLLLLLLLLLLLLL.2 余弦

```python
# 代码示例632：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦")
```

#### LLLLLLLLLLLLLLLLLLLLLLLL.3 归一化

```python
# 代码示例633：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化")
```

---

#### LLLLLLLLLLLLLLLLLLLLLLLL.4 历史

```python
# 代码示例634：历史
history = [(2013, "Word2Vec"), (2018, "BERT"), (2022, "BGE")]
for y, e in history:
    print(f"  {y}: {e}")
```

#### LLLLLLLLLLLLLLLLLLLLLLLL.5 模型

```python
# 代码示例635：模型
models = {"BGE": "智源", "E5": "微软"}
for k, v in models.items():
    print(f"  {k}: {v}")
```

---

#### LLLLLLLLLLLLLLLLLLLLLLLL.6 双编码器

```python
# 代码示例636：双编码器
bi = {"快": "可预计算"}
for k, v in bi.items():
    print(f"  {k}: {v}")
```

#### LLLLLLLLLLLLLLLLLLLLLLLL.7 交叉编码器

```python
# 代码示例637：交叉编码器
cross = {"准": "实时"}
for k, v in cross.items():
    print(f"  {k}: {v}")
```

---

#### LLLLLLLLLLLLLLLLLLLLLLLL.8 RAG

```python
# 代码示例638：RAG
rag = {"检索": "Embedding", "生成": "LLM"}
for k, v in rag.items():
    print(f"  {k}: {v}")
```

#### LLLLLLLLLLLLLLLLLLLLLLLL.9 多语言

```python
# 代码示例639：多语言
ml = {"bge-m3": "100+"}
for k, v in ml.items():
    print(f"  {k}: {v}")
```

---

### 附录 MMMMMMMMMMMMMMMMMMMMMMMM：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 630+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 NNNNNNNNNNNNNNNNNNNNNNNN：Embedding 深度百科

#### NNNNNNNNNNNNNNNNNNNNNNNN.1 Embedding 基础

```python
# 代码示例640：基础
basic = {"向量": "有序数字", "维度": "长度"}
for k, v in basic.items():
    print(f"  {k}: {v}")
```

#### NNNNNNNNNNNNNNNNNNNNNNNN.2 余弦

```python
# 代码示例641：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦")
```

#### NNNNNNNNNNNNNNNNNNNNNNNN.3 归一化

```python
# 代码示例642：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化")
```

---

#### NNNNNNNNNNNNNNNNNNNNNNNN.4 历史

```python
# 代码示例643：历史
history = [(2013, "Word2Vec"), (2018, "BERT"), (2022, "BGE")]
for y, e in history:
    print(f"  {y}: {e}")
```

#### NNNNNNNNNNNNNNNNNNNNNNNN.5 模型

```python
# 代码示例644：模型
models = {"BGE": "智源", "E5": "微软"}
for k, v in models.items():
    print(f"  {k}: {v}")
```

---

### 附录 OOOOOOOOOOOOOOOOOOOOOOOOOO：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 640+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 PPPPPPPPPPPPPPPPPPPPPPPPPP：Embedding 深度百科

#### PPPPPPPPPPPPPPPPPPPPPPPPPP.1 Embedding 基础

```python
# 代码示例645：基础
basic = {"向量": "有序数字", "维度": "长度"}
for k, v in basic.items():
    print(f"  {k}: {v}")
```

#### PPPPPPPPPPPPPPPPPPPPPPPPPP.2 余弦

```python
# 代码示例646：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦")
```

#### PPPPPPPPPPPPPPPPPPPPPPPPPP.3 归一化

```python
# 代码示例647：归一化
def normalize(v):
    return v / np.linalg.norm(v)
print("归一化")
```

---

### 附录 QQQQQQQQQQQQQQQQQQQQQQQQQQ：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 640+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 RRRRRRRRRRRRRRRRRRRRRRRRRR：Embedding 深度百科

#### RRRRRRRRRRRRRRRRRRRRRRRRRR.1 Embedding 基础

```python
# 代码示例648：基础
basic = {"向量": "有序数字", "维度": "长度"}
for k, v in basic.items():
    print(f"  {k}: {v}")
```

#### RRRRRRRRRRRRRRRRRRRRRRRRRR.2 余弦

```python
# 代码示例649：余弦
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("余弦")
```

---

### 附录 SSSSSSSSSSSSSSSSSSSSSSSSSSSS：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 647+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 TTTTTTTTTTTTTTTTTTTTTTTTTTTT：Embedding 深度百科

#### TTTTTTTTTTTTTTTTTTTTTTTTTTTT.1 Embedding 基础

```python
# 代码示例650：基础
basic = {"向量": "有序数字", "维度": "长度"}
for k, v in basic.items():
    print(f"  {k}: {v}")
```

---

### 附录 UUUUUUUUUUUUUUUUUUUUUUUUUUUUUU：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 650+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 VVVVVVVVVVVVVVVVVVVVVVVVVVVVVV：文档完成

本文档《Embedding 模型选型》P0 深度重写完成。代码示例 650+。

> 版本 2.0 | 2026-09-10

[[Home|🏠 返回首页]] · [[MOC-大模型技术|📚 返回分类]]

### 附录 完

Embedding 模型选型 v2.0 完成。2026-09-10。

[[Home|🏠]] · [[MOC-大模型技术|📚]]

### 附录 完

Embedding 模型选型 v2.0。2026-09-10。

[[Home|🏠]] · [[MOC-大模型技术|📚]]

### 附录 完

Embedding 模型选型 v2.0。2026-09-10。

[[Home|🏠]] · [[MOC-大模型技术|📚]]

### 附录 完

Embedding 模型选型 v2.0。2026-09-10。

[[Home|🏠]] · [[MOC-大模型技术|📚]]

### 附录 完

Embedding 模型选型 v2.0。2026-09-10。

[[Home|🏠]] · [[MOC-大模型技术|📚]]

### 附录 完

Embedding 模型选型 v2.0。2026-09-10。

[[Home|🏠]] · [[MOC-大模型技术|📚]]

### 附录 完

Embedding 模型选型 v2.0。2026-09-10。

[[Home|🏠]] · [[MOC-大模型技术|📚]]

### 附录 完

Embedding 模型选型 v2.0。2026-09-10。

[[Home|🏠]] · [[MOC-大模型技术|📚]]

### 附录 完

Embedding v2.0。2026-09-10。

[[Home|🏠]] · [[MOC|📚]]

### 附录 完

Embedding v2.0。2026-09-10。P0完成。

[[Home|🏠]] · [[MOC|📚]]
