---
title: 生成式AI原理与应用知识点系统梳理
tags: [AI与效率工具, AIGC, 生成式AI, Transformer, 扩散模型, 多模态, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# 生成式AI原理与应用知识点系统梳理（优化版）

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。


> **文档说明**：系统梳理生成式 AI（AIGC）的核心技术原理与应用场景，涵盖 Transformer、大语言模型、扩散模型、多模态、AIGC 产业链与行业落地。

---

## 1. 概述

生成式 AI（Generative AI）是能够生成文本、图像、音频、代码、视频等新内容的人工智能技术。2022 年底 ChatGPT 发布标志着 AIGC 时代到来，大语言模型（LLM）成为核心驱动力。

**AIGC 技术路线**：
- **文本生成**：大语言模型（GPT、Claude、Llama、文心、通义、豆包）
- **图像生成**：扩散模型（Stable Diffusion、Midjourney、DALL·E）
- **音频生成**：TTS（语音合成）、音乐生成（Suno）
- **视频生成**：Sora、Runway、Pika
- **代码生成**：GitHub Copilot、Cursor
- **多模态**：GPT-4V、Gemini、文心一言（图文音视频统一）

---


---
## 2. Transformer 架构

### 2.1 核心地位

Transformer（2017 年《Attention Is All You Need》）是现代大模型的基础架构，取代了 RNN/LSTM，通过自注意力机制实现并行计算和长距离依赖建模。


> 🔍 **知识点深度解析**
>
> **作用**：Transformer 是现代大语言模型的基础架构，其自注意力机制是 GPT/Claude/Gemini 等模型的核心。
>
> **原理**：Transformer（2017 'Attention Is All You Need'）用自注意力（Self-Attention）替代 RNN 的顺序处理，支持并行计算和长距离依赖建模。编码器（Encoder）理解输入（BERT 类），解码器（Decoder）生成输出（GPT 类）。自注意力让每个 token 直接关注序列中所有其他 token，计算 Q/K/V 点积得到注意力权重。多头注意力从不同子空间关注不同关系。
>
> **用法要点**：① Transformer = Encoder（理解）+ Decoder（生成），GPT 只用 Decoder  ② 自注意力：Q·K^T/√d_k → softmax → 加权 V，并行计算  ③ 位置编码注入序列顺序信息（正弦/RoPE/ALiBi）  ④ 多头注意力：多组 Q/K/V 关注不同语义关系  ⑤ 面试常考：Transformer 结构、自注意力公式、QKV、位置编码、多头注意力

### 2.2 核心组件

```
输入 → Embedding + 位置编码
     → 多头自注意力（Multi-Head Self-Attention）
     → 前馈神经网络（FFN）
     → 残差连接 + LayerNorm
     → 重复 N 层
     → 输出
```


> 🔍 **知识点深度解析**
>
> **作用**：Transformer 核心组件包括自注意力、前馈网络、层归一化、残差连接和位置编码。
>
> **原理**：自注意力（MHA）：token 间信息交互。前馈网络（FFN）：两层 MLP 做特征变换（通常 4 倍扩展），是模型存储知识的主要位置。层归一化（LayerNorm）：稳定训练，Pre-LN（GPT）vs Post-LN。残差连接：缓解深层梯度消失。位置编码：注入位置信息（RoPE 是当前主流，支持外推）。每个 Decoder 层还有交叉注意力（Encoder-Decoder Attention）。
>
> **用法要点**：① MHA 负责 token 间交互，FFN 负责知识存储和特征变换  ② 残差连接+LayerNorm 保证深层网络可训练  ③ FFN 通常 4 倍隐藏维度（如 4096→16384→4096）  ④ RoPE 旋转位置编码是 LLaMA/GPT-NeoX 主流  ⑤ 面试常考：FFN 作用、LayerNorm、残差连接、Pre-LN vs Post-LN

### 2.3 自注意力机制

```python

> 🔍 **知识点深度解析**
>
> **作用**：自注意力（Self-Attention）让序列中每个 token 关注所有其他 token，并行计算加权表示，是 Transformer 的核心。
>
> **原理**：每个 token 映射为 Query、Key、Value 三个向量。Attention(Q,K,V) = softmax(QK^T/√d_k)V：Q 与所有 K 计算点积得到注意力分数，除以 √d_k 防止梯度消失，softmax 归一化为权重，对 V 加权求和。多头注意力将 Q/K/V 分成多组并行计算不同子空间的注意力，拼接后线性变换。自注意力复杂度 O(n²)，但可并行（RNN 是 O(n) 串行）。
>
> **用法要点**：① QK^T 计算 token 间相关性，softmax 归一化  ② 除以 √d_k 防止点积过大导致 softmax 梯度消失  ③ 多头注意力：多组 Q/K/V 关注不同语义关系  ④ O(n²) 复杂度，长序列优化：FlashAttention/稀疏注意力  ⑤ 面试常考：QKV 含义、注意力公式、多头注意力、复杂度

# 简化的自注意力计算
import numpy as np

def self_attention(Q, K, V):
    # Q: 查询, K: 键, V: 值
    d_k = Q.shape[-1]
    scores = np.dot(Q, K.T) / np.sqrt(d_k)  # 缩放点积
    weights = softmax(scores)  # 注意力权重
    return np.dot(weights, V)
```

**关键概念**：
- **Q（Query）**：当前词的查询向量
- **K（Key）**：所有词的键向量
- **V（Value）**：所有词的值向量
- **注意力权重**：Q·K 归一化，表示词与词之间的关联度
- **多头注意力**：多组 Q/K/V 并行，捕捉不同语义关系

### 2.4 位置编码

- Transformer 没有递归结构，无法感知顺序
- 用正弦/余弦位置编码或可学习位置编码注入位置信息
- RoPE（旋转位置编码）是现代 LLM 的主流

> 🔍 **知识点深度解析**
>
> **作用**：Transformer 是所有现代大模型的基础，理解自注意力是理解 LLM 的关键。
>
> **原理**：自注意力让每个词都能直接关注序列中所有其他词，解决了 RNN 的长距离依赖问题（梯度消失）。计算过程：每个词生成 Q/K/V 三个向量，Q 与所有 K 做点积得到注意力分数，softmax 归一化后加权求和 V。多头注意力将 Q/K/V 分成多组，每组学习不同的注意力模式（语法、语义、指代等）。位置编码弥补 Transformer 无顺序感知的缺陷。Decoder-only 架构（GPT 系列）只用解码器，是当前 LLM 的主流；Encoder-Decoder（T5）和 Encoder-only（BERT）各有适用场景。
>
> **用法要点**：① 注意力计算复杂度 O(n²)，长文本是挑战（FlashAttention 优化）；② Decoder-only 是 LLM 主流（GPT/Llama/Claude）；③ 面试常考：Transformer 架构、自注意力原理、多头注意力、位置编码、为什么比 RNN 好、Decoder-only vs Encoder-Decoder。

---


---
## 3. 大语言模型（LLM）

### 3.1 训练流程

```
预训练（Pre-training）→ 监督微调（SFT）→ 人类反馈强化学习（RLHF）
```

1. **预训练**：海量文本（万亿 Token），学习语言规律和世界知识，目标是"预测下一个词"
2. **SFT（监督微调）**：用高质量问答对微调，让模型学会按指令回答
3. **RLHF**：用人类偏好数据训练奖励模型，再用 PPO 强化学习优化，让回答更符合人类偏好（有用、诚实、无害）


> 🔍 **知识点深度解析**
>
> **作用**：大模型训练分预训练、监督微调（SFT）和对齐（RLHF/DPO）三阶段，从通用语料到指令遵循。
>
> **原理**：预训练：在海量文本（万亿 token）上做下一个 token 预测，学习语言知识和世界知识（算力需求巨大，数千 GPU 数月）。SFT：在高质量指令-回答对上微调，学会遵循指令。RLHF：训练奖励模型（RM）学习人类偏好，用 PPO 优化 LLM 使输出符合人类偏好。DPO 是 RLHF 的简化替代，直接用偏好数据优化策略模型，无需单独 RM 和 PPO。
>
> **用法要点**：① 预训练：next token prediction，学习知识，算力最大  ② SFT：指令微调，学会遵循指令和对话格式  ③ RLHF：奖励模型+PPO，对齐人类偏好  ④ DPO：直接偏好优化，简化 RLHF，无需 RM 和 PPO  ⑤ 面试常考：三阶段训练、预训练目标、SFT、RLHF/DPO

### 3.2 关键技术

- **Scaling Law**：模型性能随参数量、数据量、计算量增加而可预测地提升
- **涌现能力**：模型规模达到一定阈值后，突然获得新能力（推理、翻译等）
- **思维链（CoT）**：让模型分步推理，提升复杂问题准确率
- **上下文学习（In-context Learning）**：通过示例提示，无需微调即可完成任务


> 🔍 **知识点深度解析**
>
> **作用**：大模型训练关键技术包括数据清洗、混合精度训练、分布式训练和梯度累积。
>
> **原理**：数据质量 >> 数据数量：去重、去毒、质量过滤、课程学习（从易到难）。混合精度：BF16/FP16 计算+FP32 主权重，节省显存加速训练。分布式：数据并行（DP/ZeRO）、张量并行（TP）、流水线并行（PP），3D 并行组合训练超大模型。梯度累积：多 micro-batch 梯度累加等效大 batch。FlashAttention 优化注意力计算和显存。
>
> **用法要点**：① 数据质量决定模型上限：去重/过滤/配比  ② BF16 混合精度训练，ZeRO 分片优化器状态  ③ 3D 并行：DP（数据）+TP（张量）+PP（流水线）  ④ FlashAttention：IO 感知的注意力算法，省显存加速  ⑤ 面试常考：分布式训练并行策略、混合精度、ZeRO、FlashAttention

### 3.3 推理优化

- **KV Cache**：缓存历史 Key/Value，避免重复计算
- **量化**：INT8/INT4 降低显存和计算量
- **批处理（Batching）**：合并多个请求，提升吞吐量
- **投机解码**：小模型草稿 + 大模型验证，加速推理

---


> 🔍 **知识点深度解析**
>
> **作用**：推理优化技术降低大模型部署成本和延迟，包括 KV Cache、量化、连续批处理和投机采样。
>
> **原理**：KV Cache：缓存已计算 token 的 K/V，避免重复计算（自回归生成关键优化）。量化：INT8/INT4 降低权重精度减少显存和计算（GPTQ/AWQ/GGUF）。连续批处理（Continuous Batching）：请求级动态批处理，提高 GPU 利用率。投机采样（Speculative Decoding）：小模型起草、大模型验证，加速生成。PagedAttention（vLLM）：像虚拟内存一样管理 KV Cache。
>
> **用法要点**：① KV Cache 是自回归推理的基础优化，显存随序列长度增长  ② 量化：GPTQ/AWQ（INT4）、GGUF（llama.cpp），精度损失小  ③ PagedAttention（vLLM）：KV Cache 分页管理，吞吐量提升数倍  ④ 连续批处理：动态插入新请求，提高 GPU 利用率  ⑤ 面试常考：KV Cache、量化、vLLM/PagedAttention、投机采样

## 3.4 Tokenizer（分词器）

将文本转换为模型可处理的 Token 序列。

| 算法 | 原理 | 代表模型 |
|------|------|----------|
| **BPE**（字节对编码） | 迭代合并高频字节对 | GPT、Llama |
| **WordPiece** | 基于概率的子词分割 | BERT、Gemini |
| **SentencePiece** | 直接处理字节，无需预分词 | T5、LLaMA |

**关键概念**：
- 1 个 Token ≈ 0.75 个英文单词，中文约 1-2 字/Token
- 词汇表大小通常 32K-128K
- 中文分词挑战：中文无空格，需更细粒度切分

---


> 🔍 **知识点深度解析**
>
> **作用**：Tokenizer 将文本切分为 token（子词单元），是 LLM 处理文本的第一步，影响模型表现和效率。
>
> **原理**：主流分词方法：BPE（字节对编码，GPT 系列）、WordPiece（BERT）、Unigram（T5/LLaMA）。BPE 从字符开始，迭代合并最高频的相邻 token 对，形成词表（通常 32K-100K）。分词粒度影响：词表大→序列短但模型大，词表小→序列长但覆盖差。中文分词效率低（一个汉字常占 1-2 token），多语言模型需平衡。
>
> **用法要点**：① BPE：从字符迭代合并高频对，GPT 系列使用  ② WordPiece：BERT 使用，Unigram：SentencePiece 支持  ③ 词表大小通常 32K-128K，中英文 token 效率不同  ④ 特殊 token：<s>/</s>/<pad>/<unk>，各模型不同  ⑤ 面试常考：BPE 原理、token 与字符区别、词表大小影响

## 3.5 采样策略（解码策略）

| 策略 | 原理 | 特点 |
|------|------|------|
| **Greedy** | 每次选概率最高的词 | 确定但可能重复/平庸 |
| **Beam Search** | 保留 Top-K 候选路径 | 质量高但计算量大 |
| **Temperature** | 调整概率分布锐度 | 高=多样，低=确定 |
| **Top-K** | 只从概率最高的 K 个词中采样 | 控制候选范围 |
| **Top-P（核采样）** | 累计概率达到 P 的词中采样 | 动态调整候选数 |
| **重复惩罚** | 降低已生成词的概率 | 减少重复 |

**常用组合**：temperature=0.7 + top_p=0.9，平衡质量和多样性。

---


> 🔍 **知识点深度解析**
>
> **作用**：采样策略控制 LLM 生成文本的随机性和多样性，包括 Temperature、Top-p、Top-k 和 Beam Search。
>
> **原理**：Temperature 缩放 logits：T→0 贪心解码（确定性），T>1 更随机。Top-k：只从概率最高的 k 个 token 采样。Top-p（nucleus）：从累积概率达到 p 的最小 token 集合采样。频率惩罚（frequency_presence_penalty）减少重复。Beam Search 保留 k 个最优序列（适合翻译/摘要，不适合创作）。停止词（stop sequences）控制终止。
>
> **用法要点**：① Temperature 低=确定/保守，高=随机/创造  ② Top-p 比 Top-k 更自适应（动态调整候选数）  ③ Beam Search 适合确定性任务，创作类用采样  ④ 重复惩罚：frequency_penalty 降低已出现 token 概率  ⑤ 面试常考：Temperature/Top-p/Top-k、贪心 vs 采样、Beam Search

## 3.6 模型微调方法

| 方法 | 原理 | 参数量 | 适用场景 |
|------|------|--------|----------|
| **全量微调** | 更新所有参数 | 100% | 数据充足、算力充足 |
| **LoRA** | 低秩矩阵适配 | 0.1-1% | 通用微调，主流 |
| **QLoRA** | 量化+LoRA | 0.1% | 单GPU微调大模型 |
| **Adapter** | 插入小适配器层 | 1-5% | 多任务切换 |
| **Prefix Tuning** | 只训练前缀向量 | <0.1% | 轻量调整 |

---


> 🔍 **知识点深度解析**
>
> **作用**：微调方法包括全参数微调、LoRA/QLoRA 参数高效微调和 P-Tuning 等提示微调。
>
> **原理**：全参数微调：更新所有参数，效果好但显存需求大（7B 模型需 ~80GB+）。LoRA：冻结原权重，注入低秩矩阵（A×B），只训练 0.1%-1% 参数，显存大幅降低，可合并回原权重。QLoRA：4-bit 量化基础模型+LoRA，单卡可微调 65B 模型。P-Tuning/Prefix-Tuning：只训练连续提示向量。Adapter：在 Transformer 层间插入小模块。
>
> **用法要点**：① LoRA：低秩分解 W'=W+BA，只训练 A/B，r 通常 8-64  ② QLoRA：4-bit NF4 量化+LoRA，单卡微调大模型  ③ 全参数微调效果最好但成本高，LoRA 性价比最高  ④ LoRA 可合并（merge）到原模型，无推理开销  ⑤ 面试常考：LoRA 原理、QLoRA、PEFT 方法对比、秩选择

## 3.7 RLHF 与对齐

```
SFT（监督微调）→ 奖励模型训练 → PPO强化学习
                        ↑
                   人类偏好标注（A vs B 哪个好）
```

- **PPO**：近端策略优化，经典 RLHF 算法
- **DPO**（直接偏好优化）：无需奖励模型，直接用偏好数据优化，更简单稳定
- **RLAIF**：用 AI 反馈替代人类反馈，降低标注成本
- **目标**：让模型回答更有用（Helpful）、诚实（Honest）、无害（Harmless）—— 3H 原则

---


> 🔍 **知识点深度解析**
>
> **作用**：RLHF 通过人类反馈强化学习对齐 LLM 行为，使其有用、无害、诚实（HHH）。
>
> **原理**：RLHF 三步：① SFT：在示范数据上监督微调 ② 训练奖励模型（RM）：对同一 prompt 的多个回答，人类排序，RM 学习评分 ③ PPO 优化：用 RM 评分作为奖励，PPO 算法优化 LLM 策略，同时加 KL 散度惩罚防止偏离 SFT 模型太远。DPO 跳过 RM 和 PPO，直接用偏好对优化策略，更简单稳定。对齐目标：Helpful（有用）、Harmless（无害）、Honest（诚实）。
>
> **用法要点**：① 三步：SFT→RM 训练→PPO 强化学习  ② RM 学习人类偏好排序，PPO 最大化 RM 奖励  ③ KL 惩罚防止模型为讨好 RM 而偏离太远  ④ DPO 直接偏好优化，无需 RM/PPO，更简单稳定  ⑤ 面试常考：RLHF 三阶段、PPO+KL、DPO 优势、HHH 对齐


---
## 4. 扩散模型（图像生成）

### 4.1 核心原理

扩散模型通过两步生成图像：
1. **前向过程**：逐步向图像添加高斯噪声，直到变成纯噪声
2. **反向过程**：训练神经网络逐步去噪，从纯噪声还原出图像


> 🔍 **知识点深度解析**
>
> **作用**：Embedding 模型将文本映射为稠密向量，语义相似的文本向量距离近，是语义检索和 RAG 的基础。
>
> **原理**：Embedding 模型（如 text-embedding-3、BGE、E5）通过对比学习训练：正样本对（相关文本）向量靠近，负样本对向量远离。输出固定维度向量（768/1024/1536/3072），用余弦相似度或点积衡量语义相似度。Embedding 质量取决于训练数据、维度和对比学习策略。MTEB 是 Embedding 模型的标准评测基准。
>
> **用法要点**：① 对比学习：正样本靠近，负样本远离  ② 固定维度向量，余弦相似度衡量语义距离  ③ 维度越高表达能力越强但存储计算成本越大  ④ BGE/E5 是开源优秀模型，MTEB 评测排行  ⑤ 面试常考：Embedding 原理、对比学习、余弦相似度、MTEB

### 4.2 主流模型

| 模型 | 特点 |
|------|------|
| Stable Diffusion | 开源，可本地部署，生态丰富（LoRA/ControlNet） |
| Midjourney | 闭源，画质极高，艺术风格强 |
| DALL·E 3 | OpenAI，与 ChatGPT 集成，理解提示词能力强 |
| Flux | 新一代开源模型，画质和文字渲染优秀 |


> 🔍 **知识点深度解析**
>
> **作用**：主流 Embedding 模型包括 OpenAI text-embedding-3、开源 BGE/M3E/E5/GTE 和多模态 CLIP。
>
> **原理**：OpenAI text-embedding-3-large（3072 维，可降维）：API 调用，质量高。BGE（智源，bge-large/m3）：开源最强之一，支持中英文和多语言。M3E：中文社区流行。E5（微软）：多语言。GTE（阿里）：轻量高效。CLIP：文本-图像跨模态 Embedding。选型考虑：维度、语言、是否可私有部署、MTEB 得分。
>
> **用法要点**：① OpenAI text-embedding-3：API，质量高，支持降维  ② BGE-m3：开源，多语言/多功能/多粒度  ③ 中文场景：BGE/M3E/GTE 表现优秀  ④ CLIP：跨模态文本-图像 Embedding  ⑤ 选型维度：MTEB 得分、维度、语言、部署方式

### 4.3 关键技术

- **Text-to-Image**：文本提示词生成图像
- **LoRA**：轻量微调，用少量数据训练特定风格/角色
- **ControlNet**：控制图像结构（线稿、深度、姿态）
- **Img2Img**：基于参考图生成新图
- **Inpainting**：局部重绘

---


> 🔍 **知识点深度解析**
>
> **作用**：Embedding 关键技术包括对比学习、难负样本挖掘、指令感知和 Matryoshka 降维。
>
> **原理**：对比学习损失（InfoNCE）：batch 内负样本 + 温度系数。难负样本挖掘：选择与正样本相似但不相关的负样本（如 BM25 高分但不相关），提升区分度。指令感知 Embedding（BGE/E5）：在查询前加指令（'为这个句子生成表示用于检索：'）提升任务表现。Matryoshka Embedding：截断向量仍保持语义，支持灵活降维。
>
> **用法要点**：① InfoNCE 损失 + 温度系数控制分布锐度  ② 难负样本（Hard Negatives）显著提升检索质量  ③ 指令感知：查询前加任务指令提升领域表现  ④ Matryoshka：截断前 N 维仍可用，灵活平衡精度和成本  ⑤ 面试常考：对比学习、难负样本、指令 Embedding、Matryoshka


---
## 5. 多模态

### 5.1 定义

多模态模型能同时理解和生成多种模态（文本、图像、音频、视频），实现跨模态理解和生成。


> 🔍 **知识点深度解析**
>
> **作用**：多模态大模型能同时理解和生成文本、图像、音频、视频等多种模态信息。
>
> **原理**：多模态模型通过统一的 Token 空间处理不同模态：图像用 ViT（Vision Transformer）切为 patch 编码为 token，音频用 Whisper 式编码器，与文本 token 一起输入 LLM。架构类型：早期融合（编码后直接拼接）、交叉注意力（模态间用 cross-attention）、统一架构（Gemini 原生多模态）。生成端：图像用扩散模型（DALL-E/Stable Diffusion）或离散 VQ token。
>
> **用法要点**：① ViT 将图像切 patch 编码为 token 序列  ② 模态对齐：不同模态映射到统一语义空间  ③ 架构：Encoder-Decoder / 交叉注意力 / 原生统一  ④ 图像生成：扩散模型（Stable Diffusion）或自回归 token  ⑤ 面试常考：多模态架构、ViT、模态对齐、CLIP

### 5.2 代表模型

- **GPT-4V / GPT-4o**：图文理解，GPT-4o 支持实时音视频
- **Gemini**：Google 原生多模态，支持超长上下文
- **文心一言 / 通义千问**：国内多模态大模型
- **LLaVA**：开源多模态，基于 LLaMA + ViT


> 🔍 **知识点深度解析**
>
> **作用**：多模态代表模型包括 GPT-4V/GPT-4o、Claude 3.5、Gemini、Qwen-VL 和 Stable Diffusion。
>
> **原理**：GPT-4o：OpenAI 全模态模型，实时语音/视觉/文本。Claude 3.5 Sonnet：Anthropic，强视觉理解和长上下文。Gemini：Google 原生多模态。Qwen-VL：阿里开源视觉语言模型。Stable Diffusion：开源图像生成（扩散模型）。Whisper：开源语音识别。模型选型按任务：视觉理解选 GPT-4V/Claude，图像生成选 SD/DALL-E，语音选 Whisper/GPT-4o。
>
> **用法要点**：① GPT-4o：全模态实时交互（文本/视觉/语音）  ② Claude 3.5 Sonnet：强视觉理解+200K 上下文  ③ Qwen-VL/LLaVA：开源视觉语言模型  ④ Stable Diffusion：开源图像生成生态最丰富  ⑤ Whisper：开源语音识别，多语言支持

### 5.3 应用

- 图像理解（OCR、图表分析、视觉问答）
- 图文生成（文生图、图生文）
- 视频理解与生成
- 语音对话（实时语音交互）

---


> 🔍 **知识点深度解析**
>
> **作用**：多模态大模型应用包括图文问答、文档理解、图像生成、视频分析和语音助手。
>
> **原理**：图文问答：上传图片提问（GPT-4V 识别截图/图表/手写）。文档理解：OCR+版面分析+表格提取（Claude/GPT-4V 直接处理 PDF）。图像生成：文生图（Midjourney/SD）、图生图、ControlNet 控制姿态。视频理解：分析视频内容（Gemini/GPT-4o）。语音：ASR（Whisper）+ TTS + 实时对话（GPT-4o Realtime API）。多模态 RAG：图文混合检索。
>
> **用法要点**：① 文档理解：直接上传 PDF/截图，提取表格和手写内容  ② 图像生成：文生图/图生图/ControlNet/IP-Adapter  ③ 多模态 RAG：图片+文本混合检索和问答  ④ 实时语音：ASR+LLM+TTS 端到端低延迟  ⑤ 应用选型：理解用 VLM，生成用扩散模型，语音用 Whisper


---
## 6. AIGC 产业链

```
上游（基础设施）→ 中游（模型层）→ 下游（应用层）
  算力（GPU/TPU）     基础大模型         垂直应用
  云计算              微调/部署           AI Agent
  数据服务            向量数据库          内容创作
                      MLOps              编程助手
```

**商业模式**：
- **API 调用**：按 Token 计费（OpenAI、Anthropic）
- **订阅制**：ChatGPT Plus、Claude Pro、Midjourney
- **私有化部署**：企业定制（Llama、Qwen 开源模型）
- **应用层**：Cursor、Notion AI、Duolingo Max

---


---
## 7. 行业落地应用

| 行业 | 应用场景 |
|------|----------|
| **内容创作** | 文案、营销、剧本、短视频脚本 |
| **编程开发** | 代码生成、代码审查、Bug 修复、文档生成 |
| **教育** | 个性化辅导、作业批改、知识问答 |
| **医疗** | 病历整理、辅助诊断、医学文献分析 |
| **金融** | 研报生成、风险分析、智能客服 |
| **设计** | UI 设计、海报生成、产品原型 |
| **客服** | 智能问答、工单处理、多语言支持 |
| **办公** | 文档总结、PPT 生成、邮件撰写、会议纪要 |

---


---
## 8. 挑战与局限

- **幻觉（Hallucination）**：模型会生成看似合理但错误的内容
- **上下文窗口限制**：长文本处理能力有限（虽在快速提升）
- **知识时效性**：训练数据有截止日期，实时信息需 RAG
- **推理成本**：大模型推理算力消耗大
- **安全与对齐**：防止生成有害内容、偏见、隐私泄露
- **可解释性**：模型决策过程不透明

---


---
## 10. 面试高频考点

1. **Transformer 架构**：自注意力、多头注意力、位置编码
2. **自注意力原理**：Q/K/V、计算过程、复杂度 O(n²)
3. **LLM 训练流程**：预训练 → SFT → RLHF
4. **Scaling Law**：规模与性能关系
5. **涌现能力**：定义与实例
6. **扩散模型**：前向/反向过程、去噪原理
7. **多模态**：架构、应用、代表模型
8. **AIGC 产业链**：上中下游、商业模式
9. **幻觉问题**：原因、缓解方法（RAG、CoT）
10. **AI 安全与对齐**：RLHF、3H 原则、有害内容防护
11. **Tokenizer**：BPE/WordPiece/SentencePiece，Token 与字数关系
12. **采样策略**：greedy/beam/temperature/top-k/top-p 区别
13. **微调方法**：LoRA/QLoRA/Adapter/全量微调对比
14. **RLHF 细节**：PPO/DPO/RLAIF，奖励模型
15. **位置编码**：绝对/相对/RoPE/ALiBi 对比

---


---
## 📝 精简总结

- AIGC 以 Transformer 为基础，LLM 是核心驱动力
- Transformer：自注意力（Q/K/V，softmax(QK^T/√d_k)×V）+ 多头注意力 + 位置编码，复杂度 O(n²)
- 位置编码：绝对正弦/可学习、相对位置、RoPE旋转位置编码（主流）、ALiBi
- Tokenizer：BPE（GPT）/WordPiece（BERT）/SentencePiece，1 Token ≈ 0.75 英文词
- 采样策略：greedy确定、beam质量高、temperature控随机性、top-k/top-p控候选范围
- LLM 训练：预训练（预测下一个词）→ SFT（指令微调）→ RLHF（人类偏好对齐）
- 微调方法：LoRA（低秩适配，主流）/QLoRA（量化+LoRA）/Adapter/全量微调
- RLHF：PPO经典、DPO直接偏好优化（更简单）、RLAIF（AI反馈），目标3H（有用/诚实/无害）
- 图像生成：扩散模型（加噪→去噪），Stable Diffusion 开源生态丰富
- 多模态：图文音视频统一理解与生成，GPT-4o/Gemini 为代表
- 推理优化：KV Cache、量化INT8/INT4、批处理、投机解码
- 产业链：算力 → 模型 → 应用，API/订阅/私有化三种模式
- 应用：内容创作、编程、教育、医疗、金融、设计、办公全覆盖
- 挑战：幻觉、上下文限制、时效性、成本、安全对齐

---

[[09-AI与效率工具/MOC-AI与效率工具|← 返回 AI 与效率工具 MOC]] | [[Home|🏠 返回首页]]
