---
title: AI 成本控制与 Token 计费优化
category: Python全栈
subcategory: AI应用开发
tags: [#Python全栈/AI应用, #AI结合/成本优化, #难度/进阶, #类型/实战]
difficulty: 进阶
pre: [[Python-LLM接口封装与统一SDK]], [[AI网关与多模型路由设计]]
related: [[Python-AI应用可观测性]], [[模型量化与本地部署实践]]
update: 2026-08-13
status: 完善
---

# AI 成本控制与 Token 计费优化

## 1. 核心概述

大模型 API 按 Token 计费，随着调用量增长，成本可能成为最大的运营支出。成本控制不是简单"少调用"，而是在保证效果的前提下，通过模型选型、缓存、压缩、批处理等手段将单位有效输出的成本降到最低。Token 计费需要精确到用户、功能、模型维度，才能发现成本黑洞。

**解决的场景问题**：
- 月底账单远超预期，不知道花在哪里
- 某些功能 Token 消耗巨大但价值低
- 多模型混用，无法统一统计成本
- 用户滥用导致成本失控
- Prompt 越来越长，单次调用成本飙升

## 2. 底层原理/核心逻辑

### Token 计费规则

```
总费用 = 输入 Token × 输入单价 + 输出 Token × 输出单价

示例（GPT-4o）：
输入：$0.005 / 1K tokens
输出：$0.015 / 1K tokens

一次调用：输入 2000 tokens，输出 500 tokens
费用 = 2000/1000 × 0.005 + 500/1000 × 0.015 = 0.01 + 0.0075 = $0.0175
```

### 成本优化策略矩阵

| 策略 | 原理 | 成本节省 | 效果影响 | 实施难度 |
|------|------|----------|----------|----------|
| 模型降级 | 简单任务用小模型 | 50-90% | 小 | 低 |
| Prompt 压缩 | 精简系统提示和示例 | 20-50% | 小 | 中 |
| 响应缓存 | 相同问题复用回答 | 30-80% | 无 | 中 |
| 输出限制 | 限制 max_tokens | 10-40% | 小 | 低 |
| 批处理 | 多个请求合并 | 20-50% | 小 | 中 |
| 本地模型 | 私有化部署 | 70-95% | 中 | 高 |
| 知识蒸馏 | 用大模型教小模型 | 60-90% | 中 | 高 |

### 成本黑洞常见来源

1. **RAG 检索注入过多上下文**：每次都塞 10 篇文档，输入 Token 爆炸
2. **Agent 多轮循环**：工具调用失败反复重试，Token 消耗翻倍
3. **全量历史记录**：每次都把所有对话历史发给模型
4. **长文本总结**：用户上传 100 页 PDF，直接全量输入
5. **流式输出无限制**：模型一直输出直到 max_tokens

### 计费维度

```
按用户：user_id → 本月消耗多少
按功能：feature → 哪个功能最费钱
按模型：model → 各模型占比
按租户：tenant_id → B 端多租户计费
按时间：hour/day → 成本趋势
```

## 3. 实操示例

### Token 精确计数器

```python
import tiktoken
from typing import List, Dict

class TokenCounter:
    """精确 Token 计数器"""

    MODEL_ENCODING = {
        "gpt-4o": "o200k_base",
        "gpt-4-turbo": "cl100k_base",
        "gpt-3.5-turbo": "cl100k_base",
        "text-embedding-3-small": "cl100k_base",
    }

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        encoding_name = self.MODEL_ENCODING.get(model, "cl100k_base")
        self.encoder = tiktoken.get_encoding(encoding_name)

    def count_text(self, text: str) -> int:
        return len(self.encoder.encode(text))

    def count_messages(self, messages: List[Dict]) -> int:
        tokens = 0
        for msg in messages:
            tokens += 4
            tokens += self.count_text(msg.get("role", ""))
            tokens += self.count_text(msg.get("content", ""))
            if "name" in msg:
                tokens += self.count_text(msg["name"]) + 1
        tokens += 2
        return tokens

    def count_functions(self, functions: List[Dict]) -> int:
        tokens = 0
        for func in functions:
            tokens += self.count_text(func.get("name", ""))
            tokens += self.count_text(func.get("description", ""))
            if "parameters" in func:
                tokens += self.count_text(str(func["parameters"]))
        return tokens
```

### 成本计费器

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict

@dataclass
class ModelPricing:
    input_price: float
    output_price: float

MODEL_PRICING = {
    "gpt-4o": ModelPricing(0.005, 0.015),
    "gpt-4o-mini": ModelPricing(0.00015, 0.0006),
    "gpt-4-turbo": ModelPricing(0.01, 0.03),
    "gpt-3.5-turbo": ModelPricing(0.0005, 0.0015),
    "claude-3-5-sonnet": ModelPricing(0.003, 0.015),
    "qwen2-72b": ModelPricing(0.0008, 0.002),
}

class CostTracker:
    """成本追踪器"""

    def __init__(self):
        self.usage_records = []
        self.daily_budget = {}

    def record_call(self, user_id: str, model: str, feature: str,
                    input_tokens: int, output_tokens: int,
                    latency_ms: int, success: bool = True):
        pricing = MODEL_PRICING.get(model, ModelPricing(0.01, 0.03))
        cost = (input_tokens / 1000 * pricing.input_price +
                output_tokens / 1000 * pricing.output_price)

        record = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "model": model,
            "feature": feature,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": round(cost, 6),
            "latency_ms": latency_ms,
            "success": success,
        }
        self.usage_records.append(record)
        return record

    def get_user_cost(self, user_id: str, days: int = 30) -> dict:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        user_records = [r for r in self.usage_records
                       if r["user_id"] == user_id and r["timestamp"] >= cutoff]

        total_cost = sum(r["cost_usd"] for r in user_records)
        by_model = defaultdict(lambda: {"cost": 0, "tokens": 0, "calls": 0})
        for r in user_records:
            by_model[r["model"]]["cost"] += r["cost_usd"]
            by_model[r["model"]]["tokens"] += r["total_tokens"]
            by_model[r["model"]]["calls"] += 1

        return {
            "user_id": user_id,
            "period_days": days,
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": sum(r["total_tokens"] for r in user_records),
            "total_calls": len(user_records),
            "by_model": dict(by_model),
        }

    def get_feature_cost_ranking(self, days: int = 30) -> list:
        feature_cost = defaultdict(lambda: {"cost": 0, "calls": 0, "tokens": 0})
        for r in self.usage_records:
            feature_cost[r["feature"]]["cost"] += r["cost_usd"]
            feature_cost[r["feature"]]["calls"] += 1
            feature_cost[r["feature"]]["tokens"] += r["total_tokens"]
        ranking = sorted(feature_cost.items(), key=lambda x: x[1]["cost"], reverse=True)
        return [{"feature": k, **v} for k, v in ranking]

    def check_budget(self, user_id: str) -> bool:
        daily_cost = self.get_user_cost(user_id, days=1)["total_cost_usd"]
        budget = self.daily_budget.get(user_id, 1.0)
        return daily_cost < budget
```

### LLM 响应缓存

```python
import hashlib
import json
from typing import Optional
from cachetools import TTLCache

class LLMCache:
    """LLM 响应缓存（相同输入复用输出）"""

    def __init__(self, max_size: int = 10000, ttl: int = 3600):
        self.cache = TTLCache(maxsize=max_size, ttl=ttl)

    def _make_key(self, model: str, messages: list,
                  temperature: float = 0, **kwargs) -> str:
        key_data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **{k: v for k, v in kwargs.items()
               if k in ["max_tokens", "top_p", "frequency_penalty"]}
        }
        key_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, model: str, messages: list,
            temperature: float = 0, **kwargs) -> Optional[str]:
        if temperature > 0:
            return None
        key = self._make_key(model, messages, temperature, **kwargs)
        return self.cache.get(key)

    def set(self, response: str, model: str, messages: list,
            temperature: float = 0, **kwargs):
        if temperature > 0:
            return
        key = self._make_key(model, messages, temperature, **kwargs)
        self.cache[key] = response
```

### 智能模型路由

```python
class SmartModelRouter:
    """智能模型路由：简单任务用便宜模型，复杂任务用强模型"""

    def __init__(self):
        self.models = {
            "cheap": "gpt-4o-mini",
            "medium": "gpt-3.5-turbo",
            "strong": "gpt-4o",
        }

    def classify_task_complexity(self, user_input: str) -> str:
        complex_keywords = ["代码", "debug", "架构", "设计", "分析", "推理", "数学", "论文"]
        simple_keywords = ["你好", "谢谢", "翻译", "总结", "格式", "分类"]

        if any(kw in user_input for kw in complex_keywords):
            return "strong"
        if any(kw in user_input for kw in simple_keywords):
            return "cheap"
        if len(user_input) > 500:
            return "medium"
        return "medium"

    def route(self, user_input: str) -> str:
        complexity = self.classify_task_complexity(user_input)
        return self.models[complexity]
```

### Prompt 自动压缩

```python
class PromptCompressor:
    """Prompt 压缩器"""

    def __init__(self, llm_client):
        self.llm = llm_client

    def compress_system_prompt(self, prompt: str) -> str:
        compress_prompt = f"""请将以下系统提示词压缩到原长度的 50%，
保持所有关键指令和规则不变，删除冗余表述。

原提示词：
{prompt}

压缩后的提示词："""
        return self.llm.complete(compress_prompt)

    def compress_history(self, messages: list, max_tokens: int = 1000) -> list:
        counter = TokenCounter()
        result = []
        recent_messages = []

        for msg in reversed(messages):
            tokens = counter.count_messages([msg])
            if sum(counter.count_messages([m]) for m in recent_messages) + tokens > max_tokens:
                break
            recent_messages.insert(0, msg)

        earlier = messages[:-len(recent_messages)] if recent_messages else messages
        if earlier:
            summary = self.summarize_history(earlier)
            result.append({"role": "system", "content": f"历史对话摘要：{summary}"})
        result.extend(recent_messages)
        return result

    def summarize_history(self, messages: list) -> str:
        text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        return self.llm.complete(f"请用 100 字以内总结以下对话：\n{text}\n摘要：")
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| Token 估算和实际账单不符 | 用字符数估算不准 | 使用 tiktoken 精确计算 |
| 缓存命中率低 | 用户输入每次都不同 | 用语义缓存（Embedding 相似度） |
| 模型降级后质量下降 | 简单分类规则不准 | 用小模型做分类器，A/B 测试 |
| RAG 上下文太长 | 每次都检索 Top-10 | 用 Rerank 取 Top-3 |
| 流式调用无法统计 Token | 流式响应没有 usage 字段 | 结束后用 tiktoken 计算输出 |

### 踩坑点

1. **不要只看输入 Token**：输出 Token 单价通常是输入的 2-3 倍
2. **Embedding 也计费**：RAG 场景大量文档向量化，成本可能超过对话
3. **Function Calling 定义算输入 Token**：工具定义很长时，每次调用都要算
4. **缓存要考虑数据时效性**：知识库更新后，旧缓存可能返回过时信息
5. **成本统计要包含失败请求**：超时、被拒的请求也可能计费（输入部分）

### 优化方案

- **语义缓存**：用 Embedding 相似度匹配缓存
- **批处理 Embedding**：文档向量化时批量调用
- **流式输出提前终止**：检测到完整回答后及时停止
- **用户配额系统**：免费用户限制每日调用次数

## 5. 延伸拓展方向

- [[AI网关与多模型路由设计]]：网关层统一计费和限流
- [[Python-AI应用可观测性]]：成本数据的可视化
- [[模型量化与本地部署实践]]：用本地模型降低成本
- [[Prompt工程与版本管理]]：Prompt 优化减少 Token
- [[RAG文本分块策略与实践]]：RAG 场景的输入 Token 优化

## 6. 参考资料

- [OpenAI: Pricing](https://openai.com/pricing)
- [tiktoken: Fast BPE tokenizer](https://github.com/openai/tiktoken)
- [GPTCache: Semantic Cache for LLM](https://github.com/zilliztech/GPTCache)

#待完善
