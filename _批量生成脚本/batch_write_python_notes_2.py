# -*- coding: utf-8 -*-
"""批量写入 Python 板块剩余 3 篇高质量原子笔记"""
import os

BASE = r"C:\Users\23981\Desktop\AI文档\DouBao Document\全栈工程MarkDown文档\10-四级知识框架\01-Python全栈"

notes = {}

# ============ 笔记16：模型量化与本地部署实践 ============
notes["模型量化与本地部署实践.md"] = r'''---
title: 模型量化与本地部署实践
category: Python全栈
subcategory: AI应用开发
tags: [#Python全栈/AI应用, #AI结合/模型部署, #难度/高级, #类型/实战]
difficulty: 高级
pre: [[Python-LLM接口封装与统一SDK]], [[Python-性能优化与C扩展]]
related: [[AI成本控制与Token计费优化]], [[AI网关与多模型路由设计]]
update: 2026-08-13
status: 完善
---

# 模型量化与本地部署实践

## 1. 核心概述

大模型参数巨大（7B 模型 FP16 需要 14GB 显存），普通消费级显卡跑不起来。模型量化通过降低参数精度（FP16→INT8→INT4），在保持效果的同时大幅降低显存占用和推理延迟。本地部署让数据不出本机，保护隐私，且无需支付 API 费用。Ollama、vLLM、llama.cpp 是当前最主流的本地部署方案。

**解决的场景问题**：
- 数据敏感，不能调用云端 API
- API 费用太高，想用本地模型降低成本
- 没有高端显卡，想在普通电脑上跑大模型
- 需要离线环境使用 AI
- 想自定义模型行为（微调后的模型部署）

## 2. 底层原理/核心逻辑

### 模型量化原理

```
FP32 (32位浮点) → FP16 (16位浮点) → INT8 (8位整数) → INT4 (4位整数)

显存占用对比（7B 模型）：
FP32: 28GB
FP16: 14GB
INT8: 7GB
INT4: 3.5GB

精度损失：
FP16 → 几乎无损
INT8 → 轻微损失，大多数场景不可感知
INT4 → 有一定损失，但 7B 以上模型仍可用
```

### 量化方式对比

| 方式 | 原理 | 显存节省 | 质量损失 | 推理速度 | 适用场景 |
|------|------|----------|----------|----------|----------|
| GGUF (llama.cpp) | 混合精度量化，支持多种位宽 | 50-75% | 小-中 | CPU/GPU | 本地桌面部署 |
| GPTQ | 基于校准数据的量化 | 50-75% | 小 | GPU快 | GPU 服务器部署 |
| AWQ | 激活感知量化 | 50-75% | 极小 | GPU快 | 高质量 GPU 部署 |
| INT8 动态 | 运行时动态量化 | 50% | 极小 | 一般 | 快速部署 |

### 本地部署方案对比

| 方案 | 特点 | 安装难度 | 性能 | 生态 |
|------|------|----------|------|------|
| Ollama | 一键部署，OpenAI 兼容 API | 极低 | 中 | 好 |
| vLLM | 高吞吐推理引擎，PagedAttention | 中 | 极高 | 好 |
| llama.cpp | 纯 C++ 实现，CPU 也能跑 | 中 | 中 | 中 |
| TGI (HuggingFace) | 生产级推理服务 | 高 | 高 | 好 |
| LMDeploy | 国产，支持多种量化 | 中 | 高 | 中 |

### Ollama 架构

```
Ollama CLI / API
    ↓
Ollama Server (后台服务)
    ↓
模型 Runner (基于 llama.cpp)
    ↓
GPU / CPU 推理
```

### vLLM PagedAttention 原理

传统推理中，KV Cache 是连续分配的，导致内存碎片和浪费。PagedAttention 像操作系统的虚拟内存一样，将 KV Cache 分成固定大小的块（page），按需分配，大幅提高显存利用率和批处理能力。

## 3. 实操示例

### Ollama 安装与使用

```bash
# 1. 安装 Ollama（Windows/Mac/Linux）
# 下载：https://ollama.com/download

# 2. 拉取模型
ollama pull llama3.1:8b           # Llama 3.1 8B (4.7GB)
ollama pull qwen2:7b              # 通义千问 7B
ollama pull deepseek-coder:6.7b   # DeepSeek 代码模型
ollama pull nomic-embed-text      # Embedding 模型

# 3. 列出已安装模型
ollama list

# 4. 命令行对话
ollama run llama3.1:8b

# 5. 查看模型信息
ollama show llama3.1:8b
```

### Ollama OpenAI 兼容 API 调用

```python
from openai import OpenAI

# Ollama 默认运行在 http://localhost:11434
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # 任意值
)

# 聊天
response = client.chat.completions.create(
    model="llama3.1:8b",
    messages=[
        {"role": "system", "content": "你是一个有用的助手"},
        {"role": "user", "content": "用 Python 写一个快速排序"},
    ],
    temperature=0.7,
)
print(response.choices[0].message.content)

# 流式输出
stream = client.chat.completions.create(
    model="llama3.1:8b",
    messages=[{"role": "user", "content": "讲个笑话"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

# Embedding
embedding = client.embeddings.create(
    model="nomic-embed-text",
    input="Hello world",
)
print(embedding.data[0].embedding)
```

### ollama-python 原生 API

```python
import ollama

# 列出模型
models = ollama.list()
for model in models.models:
    print(f"{model.name} - {model.size / 1e9:.1f}GB")

# 生成（非流式）
response = ollama.generate(
    model="llama3.1:8b",
    prompt="什么是 RAG？",
)
print(response.response)

# 生成（流式）
stream = ollama.generate(
    model="llama3.1:8b",
    prompt="写一首诗",
    stream=True,
)
for chunk in stream:
    print(chunk["response"], end="", flush=True)

# 聊天
messages = [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！有什么可以帮你的？"},
    {"role": "user", "content": "Python 和 Java 哪个好？"},
]
response = ollama.chat(model="llama3.1:8b", messages=messages)
print(response["message"]["content"])

# Embedding
embeddings = ollama.embeddings(model="nomic-embed-text", prompt="Hello world")
print(embeddings["embedding"])
```

### 自定义 Modelfile

```dockerfile
# Modelfile：自定义模型配置
FROM llama3.1:8b

# 设置系统提示词
SYSTEM """你是一个专业的 Python 开发助手。
- 回答简洁，代码有注释
- 优先使用 Python 3.10+ 语法
- 遇到问题先分析原因再给解决方案"""

# 参数设置
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER stop "```"

# 模板（可选，自定义对话格式）
TEMPLATE """{{ if .System }}<|start_header_id|>system<|end_header_id|>
{{ .System }}<|eot_id|>{{ end }}
{{ if .Prompt }}<|start_header_id|>user<|end_header_id|>
{{ .Prompt }}<|eot_id|>{{ end }}
<|start_header_id|>assistant<|end_header_id|>
{{ .Response }}<|eot_id|>"""
```

```bash
# 构建自定义模型
ollama create python-assistant -f Modelfile

# 使用
ollama run python-assistant
```

### vLLM 部署

```bash
# 安装
pip install vllm

# 启动 vLLM 服务（OpenAI 兼容 API）
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2-7B-Instruct \
    --quantization awq \          # 使用 AWQ 量化
    --gpu-memory-utilization 0.9 \
    --max-model-len 4096 \
    --port 8000

# 调用（和 OpenAI API 完全兼容）
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2-7B-Instruct",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

### GPTQ 量化脚本

```python
"""GPTQ 量化脚本：将 HuggingFace 模型量化为 4bit"""
from transformers import AutoTokenizer, AutoModelForCausalLM
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
import logging

logging.basicConfig(level=logging.INFO)

model_name = "Qwen/Qwen2-7B-Instruct"
output_dir = "./qwen2-7b-gptq-4bit"

# 1. 量化配置
quantize_config = BaseQuantizeConfig(
    bits=4,                    # 4bit 量化
    group_size=128,            # 分组大小
    desc_act=False,            # 是否使用激活描述
    model_file_base_name="model",
)

# 2. 加载模型
print("加载模型...")
model = AutoGPTQForCausalLM.from_pretrained(
    model_name,
    quantize_config=quantize_config,
    device_map="auto",
)

tokenizer = AutoTokenizer.from_pretrained(model_name)

# 3. 准备校准数据（128 个样本）
print("准备校准数据...")
examples = [
    tokenizer(
        "人工智能是计算机科学的一个分支，它企图了解智能的实质，"
        "并生产出一种新的能以人类智能相似的方式做出反应的智能机器。"
    )
    for _ in range(128)
]

# 4. 执行量化
print("开始量化...")
model.quantize(examples)

# 5. 保存量化模型
print(f"保存到 {output_dir}...")
model.save_quantized(output_dir, use_safetensors=True)
tokenizer.save_pretrained(output_dir)

print("量化完成！")
```

### 模型选型推荐

```python
def recommend_model(use_case: str, gpu_memory_gb: int = 8) -> dict:
    """根据使用场景和显存推荐模型"""
    models = {
        "通用对话": [
            {"name": "llama3.1:8b", "size": 4.7, "quality": "高", "lang": "中英"},
            {"name": "qwen2:7b", "size": 4.4, "quality": "高", "lang": "中文优"},
            {"name": "gemma2:9b", "size": 5.5, "quality": "高", "lang": "中英"},
        ],
        "代码生成": [
            {"name": "deepseek-coder:6.7b", "size": 3.8, "quality": "高", "lang": "代码优"},
            {"name": "codellama:7b", "size": 3.8, "quality": "中", "lang": "代码"},
            {"name": "qwen2-coder:7b", "size": 4.4, "quality": "高", "lang": "代码优"},
        ],
        "中文优化": [
            {"name": "qwen2:7b", "size": 4.4, "quality": "高", "lang": "中文优"},
            {"name": "glm4:9b", "size": 5.5, "quality": "高", "lang": "中文优"},
            {"name": "yi:9b", "size": 5.5, "quality": "高", "lang": "中文优"},
        ],
        "Embedding": [
            {"name": "nomic-embed-text", "size": 0.3, "quality": "高", "dim": 768},
            {"name": "bge-m3", "size": 1.2, "quality": "极高", "dim": 1024},
        ],
    }

    available = [m for m in models.get(use_case, []) if m["size"] <= gpu_memory_gb]
    return {
        "use_case": use_case,
        "gpu_memory": gpu_memory_gb,
        "recommended": available,
        "best": available[0] if available else None,
    }

# 使用
print(recommend_model("通用对话", gpu_memory_gb=6))
```

## 4. 常见问题、踩坑点、优化方案

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 显存不足 (OOM) | 模型太大或上下文太长 | 用更小的量化版本，降低 num_ctx |
| 推理速度慢 | CPU 推理或量化质量差 | 用 GPU，用 GPTQ/AWQ 量化，降低 batch |
| 输出质量差 | 量化损失或模型太小 | 用更大的模型或更高位宽（INT8） |
| Ollama 服务无法访问 | 服务未启动或端口被占 | `ollama serve`，检查 11434 端口 |
| 模型下载慢 | 网络问题 | 用国内镜像，或手动下载 GGUF 文件 |

### 踩坑点

1. **量化不是万能的**：小模型（<3B）量化后质量下降明显，7B 以上才适合 INT4
2. **不同框架的量化格式不兼容**：GGUF 用于 llama.cpp/Ollama，GPTQ/AWQ 用于 vLLM
3. **上下文长度影响显存**：num_ctx 越大，KV Cache 占用越多
4. **CPU 推理很慢**：7B 模型 CPU 推理可能只有 2-5 tokens/s，有 GPU 尽量用 GPU

### 优化方案

- **GPU 分层卸载**：部分层放 GPU，部分放 CPU（Ollama: OLLAMA_GPU_LAYERS）
- **投机解码**：用小模型做草稿，大模型验证，提升速度
- **连续批处理**：vLLM 的 Continuous Batching 提升吞吐
- **模型预热**：启动后先跑几个请求，避免首次请求慢

```bash
# Ollama GPU 分层卸载（显存不够时用）
set OLLAMA_GPU_LAYERS=20    # 只把 20 层放 GPU
ollama serve

# 查看 GPU 使用
nvidia-smi
```

## 5. 延伸拓展方向

- [[AI成本控制与Token计费优化]]：本地部署降低成本
- [[Python-LLM接口封装与统一SDK]]：统一 API 封装
- [[AI网关与多模型路由设计]]：本地模型和云端模型混合路由
- [[RAG文本分块策略与实践]]：本地模型 + 本地 RAG
- [[模型量化与本地部署实践]]：模型微调

## 6. 参考资料

- [Ollama 官方文档](https://github.com/ollama/ollama)
- [vLLM: Easy, Fast, LLM Serving](https://github.com/vllm-project/vllm)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [GPTQ: Accurate Post-Training Quantization](https://arxiv.org/abs/2210.17323)
- [AWQ: Activation-aware Weight Quantization](https://arxiv.org/abs/2306.00978)

#待完善
'''

# ============ 笔记19：AI 成本控制与 Token 计费优化 ============
notes["AI成本控制与Token计费优化.md"] = r'''---
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
'''

# ============ 笔记22：GraphRAG 知识图谱增强检索 ============
notes["GraphRAG知识图谱增强检索.md"] = r'''---
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
'''

# 写入文件
for filename, content in notes.items():
    filepath = os.path.join(BASE, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
    print(f"已写入: {filename} ({len(content)} 字节)")

print(f"\n共写入 {len(notes)} 篇笔记")
