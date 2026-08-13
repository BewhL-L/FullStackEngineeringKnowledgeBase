---
title: RAG 文本分块策略与实践
category: Python全栈
subcategory: AI应用开发
tags: [#Python全栈/AI应用, #AI结合/RAG, #难度/高级, #类型/实战]
difficulty: 高级
pre: [[Python-LLM接口封装与统一SDK]], [[Python-向量数据库客户端]]
related: [[GraphRAG知识图谱增强检索]], [[SpringAI-RAG检索增强实现]]
update: 2026-08-13
status: 完善
---

# RAG 文本分块策略与实践

## 1. 核心概述

文本分块（Chunking）是 RAG 系统的第一步，也是影响检索质量最关键的环节。分块太大→检索不精准、上下文冗余；分块太小→语义不完整、丢失上下文。好的分块策略需要在"语义完整性"和"检索精准度"之间找到平衡，并根据文档类型（代码/表格/长文）选择不同的分块算法。

**解决的场景问题**：
- 检索结果总是包含大量无关内容
- 长文档被切碎后语义断裂
- 代码块被切散导致无法运行
- 表格数据分块后结构丢失
- 不同类型文档用同一种分块策略效果差

## 2. 底层原理/核心逻辑

### 分块的核心矛盾

```
语义完整性 ←──────────→ 检索精准度
   (大块)                    (小块)

chunk_size 太大：
  ✓ 上下文完整
  ✗ 检索到的块包含大量无关内容
  ✗ 单次输入 Token 浪费

chunk_size 太小：
  ✓ 检索精准
  ✗ 语义不完整，模型无法理解
  ✗ 块之间关联丢失

chunk_overlap（重叠）：
  相邻块之间共享部分内容，避免边界处的语义断裂
```

### 常见分块算法对比

| 算法 | 原理 | 适用场景 | 优点 | 缺点 |
|------|------|----------|------|------|
| 固定大小分块 | 按字符数/Tokens 切 | 通用 | 简单快速 | 可能切断句子 |
| 递归字符分块 | 按分隔符递归切（\n\n→\n→。→空格） | 通用文本 | 保持段落完整 | 参数需调优 |
| 语义分块 | 按语义相似度切 | 高质量需求 | 语义边界准确 | 慢，需 Embedding |
| 结构化分块 | 按 Markdown/HTML 标题切 | 结构化文档 | 保留文档结构 | 依赖格式规范 |
| 代码分块 | 按函数/类/AST 切 | 代码文档 | 保留代码完整性 | 需语法解析 |

### 关键参数

- **chunk_size**：每块的最大大小（字符数或 Token 数），常用 500-2000
- **chunk_overlap**：相邻块重叠大小，常用 chunk_size 的 10-20%
- **分隔符优先级**：递归分块时的分隔符顺序

## 3. 实操示例

### 递归字符分块（最常用）

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 通用文本分块
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", "。", "！", "？", ";", ".", " ", ""],
    length_function=len,
)

with open("document.txt", "r", encoding="utf-8") as f:
    text = f.read()

chunks = splitter.split_text(text)
print(f"分块数量：{len(chunks)}")
for i, chunk in enumerate(chunks[:3]):
    print(f"\n--- 块 {i+1} ({len(chunk)} 字符) ---")
    print(chunk[:200] + "...")
```

### 按 Token 分块（更精确）

```python
from langchain.text_splitter import TokenTextSplitter
import tiktoken

# 使用 tiktoken 精确计算 Token
token_splitter = TokenTextSplitter(
    encoding_name="cl100k_base",  # GPT-4/GPT-3.5 的编码
    chunk_size=500,   # 500 tokens
    chunk_overlap=50,
)

chunks = token_splitter.split_text(text)

# 验证 Token 数
encoder = tiktoken.get_encoding("cl100k_base")
for chunk in chunks[:3]:
    tokens = len(encoder.encode(chunk))
    print(f"Token 数：{tokens}, 字符数：{len(chunk)}")
```

### 语义分块（Semantic Chunking）

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings

# 语义分块：根据 Embedding 相似度判断边界
semantic_splitter = SemanticChunker(
    OpenAIEmbeddings(model="text-embedding-3-small"),
    breakpoint_threshold_type="percentile",  # percentile / standard_deviation / interquartile
    breakpoint_threshold_amount=95,  # 95 百分位作为阈值
)

chunks = semantic_splitter.split_text(text)
print(f"语义分块数量：{len(chunks)}")

# 语义分块适合：内容主题切换频繁的长文
# 缺点：需要调用 Embedding API，慢且有成本
```

### Markdown 结构化分块

```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

# 按 Markdown 标题分块
markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
)

with open("doc.md", "r", encoding="utf-8") as f:
    md_text = f.read()

md_chunks = markdown_splitter.split_text(md_text)
for chunk in md_chunks:
    print(f"元数据：{chunk.metadata}")
    print(f"内容：{chunk.page_content[:100]}...")
    print("---")
```

### 代码分块（按函数切分）

```python
import ast

def split_python_code_by_function(code: str) -> list:
    """按函数/类切分 Python 代码"""
    tree = ast.parse(code)
    chunks = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            # 获取代码片段
            start = node.lineno
            end = node.end_lineno if hasattr(node, 'end_lineno') else start
            lines = code.split('\n')
            chunk = '\n'.join(lines[start-1:end])
            chunks.append({
                "name": node.name,
                "type": type(node).__name__,
                "content": chunk,
            })

    return chunks

# 使用
with open("module.py", "r") as f:
    code = f.read()

code_chunks = split_python_code_by_function(code)
for chunk in code_chunks:
    print(f"[{chunk['type']}] {chunk['name']} ({len(chunk['content'])} 字符)")
```

### 父子分块（Parent-Child Chunking）

```python
"""
父子分块：小块用于检索，大块用于生成回答
- Child Chunk：小而精准，用于向量检索
- Parent Chunk：大而完整，检索到 child 后返回对应的 parent
"""

class ParentChildChunker:
    def __init__(self, parent_size=2000, child_size=500, overlap=100):
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_size, chunk_overlap=overlap
        )
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_size, chunk_overlap=50
        )

    def split(self, text: str):
        parents = self.parent_splitter.split_text(text)
        result = []

        for parent_idx, parent in enumerate(parents):
            children = self.child_splitter.split_text(parent)
            for child_idx, child in enumerate(children):
                result.append({
                    "parent_id": f"parent_{parent_idx}",
                    "child_id": f"parent_{parent_idx}_child_{child_idx}",
                    "parent_content": parent,
                    "child_content": child,
                })

        return result

# 使用
chunker = ParentChildChunker(parent_size=2000, child_size=500)
chunks = chunker.split(text)

# 检索时：用 child_content 做向量检索
# 回答时：返回对应的 parent_content 给 LLM
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 检索到的块截断了关键信息 | chunk_size 太小 | 增大 chunk_size 或用父子分块 |
| 检索结果包含大量无关内容 | chunk_size 太大 | 减小 chunk_size，增加 overlap |
| 表格被切散 | 固定分块不识别表格 | 用结构化分块，或预处理提取表格 |
| 代码块被切断 | 按字符分块破坏代码结构 | 用 AST 按函数/类分块 |
| 元数据丢失 | 分块时没保留来源信息 | 每个 chunk 携带 doc_id、page、section 等元数据 |

### 踩坑点

1. **不要对所有文档用同一套参数**：代码文档 chunk_size 可以大些，对话记录要小些
2. **overlap 不是越大越好**：太大会导致重复检索，浪费 Token
3. **分块前要清洗文本**：去除多余空行、HTML 标签、页眉页脚
4. **中文分块要注意标点**：默认分隔符可能不包含中文句号，需手动添加

### 优化方案

- **混合分块**：先按结构（标题）粗分，再按大小细分
- **动态 chunk_size**：根据文档类型自动选择参数
- **分块质量评估**：用检索命中率（Hit Rate）反推分块效果

## 5. 延伸拓展方向

- [[GraphRAG知识图谱增强检索]]：分块后构建知识图谱
- [[Python-向量数据库客户端]]：分块后的向量存储
- [[SpringAI-RAG检索增强实现]]：Java 端的 RAG 实现
- [[高级RAG-Hybrid检索与重排序]]：分块后的检索优化
- [[Prompt工程与版本管理]]：RAG Prompt 的设计

## 6. 参考资料

- [LangChain: Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [Chunking Strategies for LLM Applications](https://www.pinecone.io/learn/chunking-strategies/)
- [Semantic Chunking](https://python.langchain.com/docs/extras/experimental/text_splitter/semantic_chunker)

#待完善
