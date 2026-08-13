---
title: Agent 记忆机制设计与实现
category: Python全栈
subcategory: AI应用开发
tags: [#Python全栈/AI应用, #AI结合/Agent, #难度/高级, #类型/实战]
difficulty: 高级
pre: [[Python-LLM接口封装与统一SDK]], [[RAG文本分块策略与实践]]
related: [[多Agent协作模式实现]], [[AI工作流编排引擎设计]]
update: 2026-08-13
status: 完善
---

# Agent 记忆机制设计与实现

## 1. 核心概述

没有记忆的 Agent 每次对话都是"失忆"的，无法积累经验、无法记住用户偏好、无法处理需要多轮上下文的复杂任务。Agent 记忆机制分为短期记忆（对话上下文）和长期记忆（持久化知识），通过滑动窗口、摘要压缩、向量检索等技术，在有限的上下文窗口内保留最有价值的信息。

**解决的场景问题**：
- 多轮对话中 Agent 忘记之前说过什么
- 用户偏好（如"用中文回答"、"代码加注释"）每次都要重新说
- 长对话超出 Token 限制，早期信息丢失
- Agent 无法从历史对话中学习经验
- 需要记住用户的个人信息（项目、技术栈、目标）

## 2. 底层原理/核心逻辑

### 记忆类型分层

```
┌─────────────────────────────────────────────┐
│  短期记忆 (Short-term Memory)                 │
│  - 当前对话的上下文                            │
│  - 滑动窗口 / 摘要压缩                         │
│  - 存在内存或 Redis 中                        │
├─────────────────────────────────────────────┤
│  长期记忆 (Long-term Memory)                  │
│  - 历史对话、用户画像、知识库                   │
│  - 向量检索 + 结构化存储                       │
│  - 持久化到数据库                              │
├─────────────────────────────────────────────┤
│  情景记忆 (Episodic Memory)                   │
│  - 具体事件的记忆（"上次部署失败是因为..."）    │
│  - 带时间戳的事件记录                          │
├─────────────────────────────────────────────┤
│  语义记忆 (Semantic Memory)                   │
│  - 抽象知识（"Docker 是容器化工具"）           │
│  - 知识图谱 / 事实表                          │
└─────────────────────────────────────────────┘
```

### 短期记忆策略

| 策略 | 原理 | Token 节省 | 信息丢失 |
|------|------|-----------|----------|
| 全量保留 | 保留所有历史 | 0% | 无 |
| 滑动窗口 | 只保留最近 N 轮 | 50-80% | 早期信息丢失 |
| 摘要压缩 | 早期对话摘要化 | 60-90% | 细节丢失 |
| 混合策略 | 最近 N 轮全量 + 更早摘要 | 70-85% | 平衡 |

### 长期记忆检索流程

```
用户输入
    ↓
1. 意图识别（是否需要检索记忆？）
    ↓
2. 记忆检索（向量相似度 + 时间衰减 + 重要性评分）
    ↓
3. 记忆排序（相关度 × 时间衰减 × 重要性）
    ↓
4. 注入 Prompt（作为上下文的一部分）
    ↓
Agent 生成回答
    ↓
5. 记忆写入（判断是否值得记住）
```

## 3. 实操示例

### 短期记忆：滑动窗口 + 摘要压缩

```python
from typing import List, Dict
from dataclasses import dataclass
import tiktoken

@dataclass
class Message:
    role: str
    content: str
    timestamp: float

class ConversationMemory:
    """对话短期记忆：滑动窗口 + 摘要压缩"""

    def __init__(self, max_tokens: int = 3000, summary_model: str = "gpt-4o-mini"):
        self.messages: List[Message] = []
        self.max_tokens = max_tokens
        self.summary_model = summary_model
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.summary = ""  # 早期对话的摘要

    def add(self, role: str, content: str):
        self.messages.append(Message(role, content, __import__("time").time()))

    def get_messages(self) -> List[Dict]:
        """获取适合发送给 LLM 的消息列表"""
        result = []

        # 如果有摘要，作为系统消息加入
        if self.summary:
            result.append({
                "role": "system",
                "content": f"[历史对话摘要]\n{self.summary}"
            })

        # 从后往前取，直到达到 token 限制
        current_tokens = 0
        recent_messages = []

        for msg in reversed(self.messages):
            tokens = len(self.encoder.encode(msg.content)) + 4  # +4 是格式开销
            if current_tokens + tokens > self.max_tokens:
                break
            recent_messages.insert(0, {"role": msg.role, "content": msg.content})
            current_tokens += tokens

        result.extend(recent_messages)
        return result

    async def compress(self, llm_client):
        """将超出窗口的早期对话压缩为摘要"""
        # 找出需要压缩的消息（超出最近窗口的部分）
        recent_tokens = 0
        split_idx = 0
        for i in range(len(self.messages) - 1, -1, -1):
            tokens = len(self.encoder.encode(self.messages[i].content))
            if recent_tokens + tokens > self.max_tokens // 2:
                split_idx = i
                break
            recent_tokens += tokens

        if split_idx == 0:
            return  # 不需要压缩

        to_summarize = self.messages[:split_idx]
        if not to_summarize:
            return

        # 构建摘要 Prompt
        history_text = "\n".join(
            f"{m.role}: {m.content}" for m in to_summarize
        )

        prompt = f"""请将以下对话历史压缩为简洁的摘要（200字以内），
保留关键信息：用户需求、决策、重要事实。

对话历史：
{history_text}

摘要："""

        response = await llm_client.chat.completions.create(
            model=self.summary_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        self.summary = response.choices[0].message.content.strip()
        # 移除已压缩的消息
        self.messages = self.messages[split_idx:]
```

### 长期记忆：基于向量库的记忆存储

```python
import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime
import uuid

class LongTermMemory:
    """长期记忆：基于向量数据库的记忆存储与检索"""

    def __init__(self, persist_dir: str = "./memory_db", api_key: str = None):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name="text-embedding-3-small",
        )
        self.collection = self.client.get_or_create_collection(
            name="agent_memory",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, content: str, memory_type: str = "fact",
            importance: float = 0.5, metadata: dict = None):
        """添加记忆"""
        mem_id = str(uuid.uuid4())
        meta = {
            "type": memory_type,
            "importance": importance,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0,
        }
        if metadata:
            meta.update(metadata)

        self.collection.add(
            ids=[mem_id],
            documents=[content],
            metadatas=[meta],
        )
        return mem_id

    def search(self, query: str, top_k: int = 5, memory_type: str = None) -> List[Dict]:
        """检索相关记忆"""
        where = {"type": memory_type} if memory_type else None
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where,
        )

        memories = []
        for i in range(len(results["ids"][0])):
            # 更新访问计数
            self.collection.update(
                ids=[results["ids"][0][i]],
                metadatas=[{"access_count": results["metadatas"][0][i].get("access_count", 0) + 1}],
            )

            memories.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if results["distances"] else None,
            })

        return memories

    def get_recent(self, limit: int = 10) -> List[Dict]:
        """获取最近的记忆"""
        # Chroma 没有直接按时间排序，这里简化处理
        all_results = self.collection.get(limit=100)
        sorted_items = sorted(
            zip(all_results["ids"], all_results["documents"], all_results["metadatas"]),
            key=lambda x: x[2].get("timestamp", ""),
            reverse=True,
        )[:limit]
        return [{"id": i, "content": d, "metadata": m} for i, d, m in sorted_items]
```

### 用户画像记忆

```python
class UserProfile:
    """用户画像：结构化的用户信息记忆"""

    def __init__(self, long_term_memory: LongTermMemory):
        self.ltm = long_term_memory

    async def extract_and_store(self, conversation: str, llm_client):
        """从对话中提取用户画像信息并存储"""
        prompt = f"""请从以下对话中提取用户的关键信息，输出 JSON 格式：
{{
    "preferences": ["偏好1", "偏好2"],
    "skills": ["技能1"],
    "projects": ["项目1"],
    "goals": ["目标1"],
    "constraints": ["约束1"]
}}

只输出 JSON，不要解释。

对话：
{conversation}"""

        response = await llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0,
        )

        import json
        profile = json.loads(response.choices[0].message.content)

        # 存储每个信息点为独立记忆
        for category, items in profile.items():
            for item in items:
                self.ltm.add(
                    content=f"用户{category}：{item}",
                    memory_type="user_profile",
                    importance=0.8,
                    metadata={"category": category},
                )

    def get_profile_context(self, query: str) -> str:
        """获取与当前查询相关的用户画像"""
        memories = self.ltm.search(query, top_k=5, memory_type="user_profile")
        if not memories:
            return ""
        return "用户相关信息：\n" + "\n".join(f"- {m['content']}" for m in memories)
```

### 带记忆的 Agent

```python
class AgentWithMemory:
    """整合短期记忆和长期记忆的 Agent"""

    def __init__(self, llm_client, api_key: str):
        self.llm = llm_client
        self.short_term = ConversationMemory(max_tokens=2000)
        self.long_term = LongTermMemory(api_key=api_key)
        self.user_profile = UserProfile(self.long_term)

    async def chat(self, user_input: str) -> str:
        # 1. 检索长期记忆
        relevant_memories = self.long_term.search(user_input, top_k=3)
        profile_context = self.user_profile.get_profile_context(user_input)

        # 2. 构建记忆上下文
        memory_context = ""
        if relevant_memories:
            memory_context = "\n相关记忆：\n" + "\n".join(
                f"- {m['content']}" for m in relevant_memories
            )
        if profile_context:
            memory_context += "\n" + profile_context

        # 3. 构建系统 Prompt
        system_prompt = f"""你是一个有记忆的 AI 助手。
{memory_context}

请基于以上记忆和当前对话回答用户问题。"""

        # 4. 获取短期记忆
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.short_term.get_messages())
        messages.append({"role": "user", "content": user_input})

        # 5. 调用 LLM
        response = await self.llm.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        answer = response.choices[0].message.content

        # 6. 更新短期记忆
        self.short_term.add("user", user_input)
        self.short_term.add("assistant", answer)

        # 7. 压缩短期记忆（如果太长）
        await self.short_term.compress(self.llm)

        # 8. 判断是否需要写入长期记忆
        await self._maybe_store_memory(user_input, answer)

        return answer

    async def _maybe_store_memory(self, user_input: str, answer: str):
        """判断是否值得记住当前对话"""
        # 简单规则：用户提到偏好、项目、重要决策时存储
        keywords = ["我喜欢", "我偏好", "我的项目", "我决定", "记住", "我的目标"]
        if any(kw in user_input for kw in keywords):
            self.long_term.add(
                content=f"用户说：{user_input}\n助手回答：{answer[:200]}",
                memory_type="conversation",
                importance=0.7,
            )
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| Agent 忘记早期对话 | 短期记忆窗口太小 | 用摘要压缩，或增大 max_tokens |
| 检索到不相关的记忆 | 向量相似度不够准确 | 加元数据过滤（类型、时间），用重排序 |
| Token 超限 | 记忆注入太多 | 限制 top_k，或对记忆再做摘要 |
| 记忆注入导致回答偏移 | 旧记忆干扰当前问题 | 加时间衰减，降低旧记忆权重 |
| 重复存储相同记忆 | 没有去重 | 存储前做相似度检查，>0.95 则更新而非新增 |

### 踩坑点

1. **不要把所有历史都塞进 Prompt**：成本高且可能干扰当前回答
2. **记忆写入要有筛选**：不是每句话都值得记住，否则记忆库充满噪声
3. **摘要压缩会丢失细节**：重要信息（如代码、配置）不要只存摘要
4. **长期记忆要定期清理**：过时的记忆（如"我正在用 Vue2"）会误导

### 优化方案

- **记忆重要性评分**：用 LLM 评估每条记忆的重要性（1-10分），低分时自动遗忘
- **时间衰减**：越久的记忆权重越低，模拟人类遗忘
- **记忆关联**：新记忆与旧记忆关联，形成记忆网络

```python
# 记忆重要性评分
async def score_importance(content: str, llm_client) -> float:
    prompt = f"""请对以下信息的重要性评分（1-10），
1=无关紧要，10=非常重要（如用户密码、核心需求、关键决策）。
只输出数字。

信息：{content}
评分："""
    response = await llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    try:
        return float(response.choices[0].message.content.strip()) / 10
    except:
        return 0.5
```

## 5. 延伸拓展方向

- [[多Agent协作模式实现]]：多 Agent 之间的记忆共享
- [[GraphRAG知识图谱增强检索]]：用知识图谱做长期记忆
- [[AI工作流编排引擎设计]]：记忆作为工作流节点
- [[Prompt工程与版本管理]]：记忆注入的 Prompt 设计
- [[AI成本控制与Token计费优化]]：记忆带来的 Token 成本

## 6. 参考资料

- [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560)
- [LangChain: Memory](https://python.langchain.com/docs/modules/memory/)
- [Letta (MemGPT): Memory Management](https://github.com/letta-ai/letta)
- [Generative Agents: Interactive Simulacra](https://arxiv.org/abs/2304.03442)

#待完善
