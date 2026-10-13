---
title: 大模型训练范式 PT-SFT-RLHF
tags: [AI应用, AI工程化, LLM, 效率工具]
category: AI与效率工具
created: 2026-08-13
updated: 2026-09-08
difficulty: ⭐⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[[LLM大模型入门概念]]", "[[Transformer架构核心]]"]
aliases: [大模型训练范式, PT-SFT-RLHF, 预训练-微调-对齐, LLM训练三阶段]
---

# 大模型训练范式 PT-SFT-RLHF

> **一句话定义**：现代大语言模型的训练遵循"预训练（Pre-training）→ 监督微调（SFT）→ 人类反馈强化学习（RLHF）"三阶段范式，预训练获得通用语言能力，SFT 学会遵循指令，RLHF 对齐人类价值观，三者共同将基础模型转化为可用的对话助手。
>
> **核心价值**：系统化地将大规模无标注文本中的语言知识转化为可控、有用、安全的对话能力，每个阶段解决不同层次的问题，是当前 LLM 训练的标准流程，直接决定了模型的能力上限和对齐质量。
>
> **适用场景**：大模型训练、模型定制、领域适配、对齐研究、训练流程设计、成本估算、能力评估。

---

## 一、概述

### 1.1 三阶段训练范式总览

```mermaid
graph TB
    subgraph 第一阶段：预训练 PT
        A1[海量无标注文本<br/>万亿级 Token<br/>互联网/书籍/代码] --> A2[自监督学习<br/>预测下一个 Token<br/>因果语言建模]
        A2 --> A3[基础模型<br/>Base Model<br/>通用语言能力<br/>只会续写文本]
    end

    subgraph 第二阶段：监督微调 SFT
        B1[高质量指令-回答对<br/>数万~数十万条<br/>人工/AI生成] --> B2[有监督学习<br/>交叉熵损失<br/>只算回答部分]
        B2 --> B3[指令微调模型<br/>SFT Model<br/>学会遵循指令<br/>对话格式]
    end

    subgraph 第三阶段：对齐 RLHF/DPO
        C1[人类偏好数据<br/>数万~数十万对<br/>chosen/rejected] --> C2[奖励模型训练<br/>RM<br/>学习人类偏好]
        C2 --> C3[PPO 强化学习<br/>用RM优化策略<br/>KL约束防偏离]
        C3 --> C4[对齐模型<br/>Aligned Model<br/>有用/无害/诚实<br/>对话助手]
    end

    A3 --> B1
    B3 --> C1

    Note over A1,A3: 成本极高（数百万美元）<br/>只有大公司能做
    Note over B1,B3: 成本中等（数千~数万美元）<br/>小团队可做（LoRA）
    Note over C1,C4: 成本中低（数千美元）<br/>小团队可做（DPO简化）

    style A3 fill:#e1bee7
    style B3 fill:#bbdefb
    style C4 fill:#c8e6c9
```

### 1.2 三阶段对比

| 维度 | 预训练（PT） | 监督微调（SFT） | 对齐（RLHF/DPO） |
|------|-------------|----------------|-----------------|
| **目标** | 通用语言建模能力 | 遵循指令、对话格式 | 有用、无害、诚实、符合人类偏好 |
| **数据** | 海量无标注文本（万亿 Token） | 指令-回答对（1万~100万） | 偏好数据（1万~10万对） |
| **学习方式** | 自监督（预测下一个 Token） | 有监督（交叉熵损失） | 强化学习（PPO）/ 偏好优化（DPO） |
| **成本** | 极高（数百万~数千万美元） | 中等（数千~数万美元） | 中低（数千美元） |
| **训练时间** | 数周~数月（数千 GPU） | 数小时~数天（单卡~数卡） | 数小时~数天 |
| **谁能做** | 大公司（OpenAI/Google/Meta） | 小团队（LoRA/QLoRA） | 小团队（DPO 简化） |
| **能力上限** | 决定模型的知识和能力天花板 | 释放预训练能力，学会任务 | 优化行为，提升用户体验 |
| **关键指标** | 困惑度（PPL）、基准测试 | 指令遵循率、任务准确率 | 偏好胜率、有用性、无害性 |
| **数据质量要求** | 中等（海量但需清洗去重） | 高（质量 > 数量） | 高（偏好差异要明显） |
| **典型失败** | 学到偏见/有害内容、知识错误 | 格式错误、不遵循指令、过拟合 | 对齐税、奖励黑客、过度保守 |

### 1.3 核心概念

| 概念 | 说明 |
|------|------|
| **预训练（Pre-training, PT）** | 在海量无标注文本上进行自监督学习（预测下一个 Token），获得通用语言能力，是 LLM 能力的基础 |
| **基础模型（Base Model）** | 预训练完成但未经微调的模型，只会"续写文本"，不会"回答问题" |
| **继续预训练（Continued Pre-training, CPT）** | 在预训练基础上，用领域数据继续预训练，注入领域知识，适用于领域专用模型 |
| **监督微调（Supervised Fine-Tuning, SFT）** | 用高质量指令-回答对进行有监督训练，让模型学会遵循指令和对话格式 |
| **指令微调（Instruction Tuning）** | SFT 的一种，专门用指令数据微调，提升零样本/少样本任务能力 |
| **奖励模型（Reward Model, RM）** | 学习人类偏好的模型，输入 prompt+response，输出奖励分数，用于 RLHF 的 PPO 训练 |
| **RLHF（Reinforcement Learning from Human Feedback）** | 基于人类反馈的强化学习，用奖励模型作为奖励信号，用 PPO 优化策略，对齐人类价值观 |
| **PPO（Proximal Policy Optimization）** | 近端策略优化，RLHF 中最常用的强化学习算法，通过 clip 限制策略更新幅度，保证训练稳定 |
| **DPO（Direct Preference Optimization）** | 直接偏好优化，RLHF 的简化替代，绕过奖励模型和 PPO，直接在偏好数据上优化策略 |
| **对齐税（Alignment Tax）** | 对齐后模型通用能力下降的现象，是 RLHF/DPO 需要平衡的问题 |
| **奖励黑客（Reward Hacking）** | 策略模型找到奖励模型的漏洞，生成看似高分但实际质量差的输出，欺骗奖励模型 |
| **KL 散度约束** | RLHF 中约束策略模型与参考模型（SFT 模型）的 KL 散度，防止策略偏离太远导致语言质量下降 |
| **红队测试（Red Teaming）** | 专门尝试诱导模型生成有害输出的测试，用于评估和提升模型安全性 |


<div style="background:linear-gradient(135deg,#f093fb,#f5576c);border-radius:16px;padding:20px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#fff;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes flow{0%{transform:translateX(-10px);opacity:0}15%{transform:translateX(0);opacity:1}85%{transform:translateX(0);opacity:1}100%{transform:translateX(10px);opacity:0}}.flow-step{display:inline-block;background:rgba(255,255,255,.2);border:2px solid rgba(255,255,255,.5);border-radius:8px;padding:10px 14px;margin:4px;text-align:center;font-weight:600;font-size:13px;animation:flow 4s ease-in-out infinite;min-width:90px}.flow-step:nth-child(2){animation-delay:.5s}.flow-step:nth-child(4){animation-delay:1s}.flow-step:nth-child(6){animation-delay:1.5s}.flow-step:nth-child(8){animation-delay:2s}.flow-arrow{display:inline-block;font-size:20px;animation:flow 4s ease-in-out infinite;vertical-align:middle}.flow-code{background:rgba(0,0,0,.2);border-radius:6px;padding:8px 12px;margin-top:10px;font-family:monospace;font-size:12px;text-align:center}</style>
<div style="text-align:center;font-size:15px;font-weight:700;margin-bottom:14px;padding-bottom:10px;border-bottom:1.5px solid rgba(255,255,255,.22);letter-spacing:1px">🏋️ LLM 三阶段训练范式</div>
<div style="text-align:center;white-space:nowrap;overflow-x:auto">
<span class="flow-step">预训练PT</span><span class="flow-arrow">→</span><span class="flow-step">监督微调SFT</span><span class="flow-arrow">→</span><span class="flow-step">对齐RLHF/DPO</span><span class="flow-arrow">→</span><span class="flow-step">部署应用</span>
</div>
<div class="flow-code">海量文本自监督→指令-回答对有监督→偏好数据对齐人类价值观→API/RAG/Agent部署</div>
</div>
> 🔍 **知识点深度解析**
>
> **作用**：PT-SFT-RLHF 三阶段范式是现代 LLM 训练的标准流程，系统化地将大规模无标注文本中的语言知识转化为可控、有用、安全的对话能力。预训练获得通用语言能力（知识和推理的基础），SFT 学会遵循指令和对话格式（将能力转化为可用的交互），RLHF/DPO 对齐人类价值观（让模型的行为符合人类偏好：有用、无害、诚实）。
>
> **原理**：三阶段范式的核心思想是"分而治之"——不同阶段解决不同层次的问题。预训练用海量无标注数据（互联网上几乎无限的文本）通过自监督学习（预测下一个 Token）获得通用语言能力，这一阶段数据量大但标注成本为零，适合学习语言的统计规律和世界知识。SFT 用高质量的指令-回答对（人工编写或 AI 生成）进行有监督学习，教模型"看到指令后如何生成回答"，这一阶段数据量小但质量要求高，适合学习交互格式和任务模式。RLHF 用人类偏好数据（chosen/rejected 对）训练奖励模型，再用 PPO 强化学习优化策略，让模型的输出更符合人类偏好（有用、无害、诚实），这一阶段解决的是"模型能做"和"模型应该做"之间的差距——SFT 后的模型可能生成有害、不诚实、不符合人类价值观的内容，RLHF 通过人类偏好对齐来修正这些问题。DPO 是 RLHF 的简化替代，绕过奖励模型和 PPO，直接在偏好数据上优化策略，更简单更稳定。
>
> **用法要点**：① 预训练成本极高，通常直接使用开源基础模型（Llama/Qwen/Mistral），不需要自己做 ② SFT 是小团队定制模型的主要手段——用 LoRA/QLoRA 在领域数据上微调，成本低效果好 ③ 对齐可以用 DPO 替代 RLHF——DPO 更简单稳定，不需要奖励模型和 PPO，效果相当 ④ 数据质量是关键——SFT 和对齐的数据质量远比数量重要，1 万条高质量数据通常优于 100 万条低质量数据 ⑤ 三阶段不是必须全部做——如果使用已经经过 SFT 和对齐的指令微调模型（如 Llama-3-Instruct、Qwen2.5-Instruct），可以直接使用，或只做领域 SFT ⑥ 警惕对齐税——对齐后通用能力可能下降，需要在领域任务和通用任务上同时评估 ⑦ 成本估算——预训练数百万美元，SFT 数千~数万美元（LoRA 数百美元），DPO 数千美元 ⑧ 持续迭代——收集用户反馈，持续优化 SFT 数据和偏好数据，迭代模型

---

> 💡 **深度讲解**：PT-SFT-RLHF 三阶段范式是现代 LLM 训练的核心方法论，它的出现是 LLM 技术成熟的重要标志。在这个范式确立之前，训练一个好用的对话模型是非常困难的——纯预训练模型只会续写文本，不会回答问题；纯监督微调需要大量高质量标注数据，且难以覆盖所有场景；纯强化学习训练不稳定，容易崩溃。三阶段范式通过"分阶段解决不同问题"的思路，系统化地解决了这些挑战。预训练（PT）是整个范式的基础——它利用互联网上海量的无标注文本（万亿级 Token），通过简单的"预测下一个 Token"目标，让模型学习到语言的语法、语义、世界知识、推理能力。这一阶段的核心是"规模"——大规模参数（数十亿到数千亿）、大规模数据（万亿 Token）、大规模计算（数千 GPU 训练数周）。Scaling Law 表明，在一定范围内，模型性能与这三个因素呈幂律关系，规模越大性能越好。预训练的成本极高（数百万到数千万美元），只有大公司能负担，因此大多数团队直接使用开源基础模型（Llama、Qwen、Mistral 等）。预训练的输出是"基础模型"（Base Model），它有强大的语言能力但只会"续写文本"——给它一个问题，它可能会续写更多问题，而不是回答问题。监督微调（SFT）是将基础模型转化为"对话助手"的关键步骤——用高质量的指令-回答对（instruction-response pairs）进行有监督训练，教模型"看到指令后生成回答"。InstructGPT 论文的一个重要发现是：仅 1.3 万条高质量人工标注的 SFT 数据就能带来显著的效果提升，数据质量远比数量重要。SFT 的训练目标与预训练相同（预测下一个 Token），但有两个关键区别：① 数据是指令-回答对而非无标注文本；② 只对回答部分计算损失（指令部分 mask 掉），避免模型学习重复指令。SFT 后的模型学会了遵循指令和对话格式，但仍然存在问题——它可能生成有害内容、不诚实的回答、不符合人类价值观的输出。这是因为 SFT 只教模型"如何回答"，没有教模型"应该回答什么"。RLHF（基于人类反馈的强化学习）是解决"应该回答什么"的关键——通过人类偏好数据（chosen/rejected 对）训练奖励模型（Reward Model），让奖励模型学会"什么样的回答是人类偏好的"，然后用 PPO 强化学习优化策略模型，最大化奖励模型的分数，同时用 KL 散度约束防止策略偏离 SFT 模型太远（避免语言质量下降）。RLHF 的效果显著——InstructGPT/GPT-3.5/ChatGPT 都使用了 RLHF，用户体验大幅提升。但 RLHF 也有缺点：① 训练复杂——需要训练奖励模型，再用 PPO 优化，超参数多，训练不稳定；② 计算成本高——PPO 训练需要同时维护策略模型、参考模型、奖励模型、价值模型四个模型；③ 奖励黑客（Reward Hacking）——策略模型可能找到奖励模型的漏洞，生成看似高分但实际质量差的输出。DPO（直接偏好优化）是 RLHF 的重要简化——它证明了奖励模型和策略优化可以合并为一个目标，直接在偏好数据上优化策略，不需要单独训练奖励模型，也不需要 PPO。DPO 的损失函数是一个带参考模型的对比损失，形式简洁，训练稳定，计算成本接近 SFT。多个研究和实践表明，DPO 的对齐效果与 RLHF 相当甚至更好，正在成为对齐的主流方法。三阶段范式不是僵化的——不同的模型和场景可能有不同的变体：① 有些模型跳过 RLHF，只用 SFT（如早期的 Alpaca），效果尚可但对齐质量不如 RLHF/DPO；② 有些模型用 DPO 替代 RLHF（如 Zephyr、Tulu），更简单稳定；③ 有些模型在预训练后直接做 RLHF（跳过 SFT），但效果通常不如先 SFT 再 RLHF；④ 领域专用模型可能在预训练后先做继续预训练（CPT）注入领域知识，再做 SFT 和对齐；⑤ 有些模型用 RLAIF（AI 反馈而非人类反馈）替代 RLHF，用 AI 模型生成偏好数据，降低成本。理解三阶段范式对于 LLM 应用开发非常重要——它告诉我们：① 不需要自己做预训练（成本太高，直接用开源基础模型）；② SFT 是定制模型的主要手段（成本低、效果好）；③ 对齐可以用 DPO 简化（不需要复杂的 RLHF）；④ 数据质量是关键（特别是 SFT 和对齐数据）；⑤ 三阶段可以灵活组合（根据场景和资源选择）。
>
> **📝 精简总结**：PT-SFT-RLHF三阶段范式是现代LLM训练标准流程——预训练PT（海量无标注文本万亿Token/自监督预测下一个Token/获得通用语言能力/基础模型只会续写文本/成本极高数百万美元/大公司做）→监督微调SFT（高质量指令回答对1万-100万/有监督交叉熵只算回答部分/学会遵循指令和对话格式/成本中等数千-数万/小团队LoRA可做）→对齐RLHF/DPO（人类偏好数据1万-10万对/奖励模型+PPO或直接DPO/对齐人类价值观有用无害诚实/成本中低数千/小团队DPO可做）；三阶段对比——PT（目标通用语言建模/数据海量无标注/自监督/成本极高/数周数月/大公司/决定能力天花板/PPL和基准/数据质量中等/学到偏见有害）、SFT（目标遵循指令/数据指令回答对/有监督/成本中等/数小时数天/小团队/释放预训练能力/指令遵循率/数据质量高/格式错误不遵循指令过拟合）、RLHF/DPO（目标对齐人类偏好/数据偏好对/强化学习或偏好优化/成本中低/数小时数天/小团队/优化行为提升体验/偏好胜率有用无害/数据质量高/对齐税奖励黑客过度保守）；核心概念包括预训练PT/基础模型Base Model/继续预训练CPT/监督微调SFT/指令微调Instruction Tuning/奖励模型RM/RLHF/PPO近端策略优化/DPO直接偏好优化/对齐税Alignment Tax/奖励黑客Reward Hacking/KL散度约束/红队测试Red Teaming；核心原理是分而治之——PT用海量无标注数据自监督学通用能力（数据量大标注成本为零学统计规律和世界知识）、SFT用高质量指令回答对有监督学交互格式（数据量小质量高学任务模式）、RLHF用人类偏好学价值观（解决模型能做vs应该做的差距，奖励模型+PPO或DPO简化）；用法要点包括预训练直接用开源基础模型不自己做/SFT是小团队定制主要手段用LoRA/对齐用DPO替代RLHF更简单稳定/数据质量远比数量重要/三阶段不必全做（指令微调模型可直接用或只做领域SFT）/警惕对齐税需领域+通用双评估/成本估算（PT数百万/SFT数千数万LoRA数百/DPO数千）/持续迭代收集用户反馈优化数据。

---

## 二、原理

### 2.1 预训练（PT）原理

```mermaid
graph TB
    subgraph 预训练数据流水线
        A1[原始数据<br/>互联网/书籍/代码/论文] --> A2[数据清洗<br/>去重/过滤/去毒]
        A2 --> A3[质量分级<br/>高质量高权重<br/>低质量低权重]
        A3 --> A4[Tokenization<br/>BPE/SentencePiece]
        A4 --> A5[训练样本<br/>随机截取固定长度<br/>如 4K/8K Token]
    end

    subgraph 预训练目标
        B1[输入: x1, x2, ..., xn] --> B2[Transformer<br/>前向传播]
        B2 --> B3[输出: P(x_{t+1}|x1...xt)]
        B3 --> B4[交叉熵损失<br/>L = -Σ log P(x_{t+1}|x<t)]
        B4 --> B5[反向传播<br/>更新所有参数]
    end

    A5 --> B1

    Note over B4: 自监督学习——文本本身就是标签<br/>不需要人工标注
    style B4 fill:#fff9c4
```

#### 预训练目标

预训练使用因果语言建模（Causal Language Modeling）目标：

```text
$$
\mathcal{L}_{PT} = -\sum_{t=1}^{N} \log P_\theta(x_{t+1} | x_1, x_2, ..., x_t)
$$
```

给定前面的 Token，预测下一个 Token。这是一个自监督目标——文本本身就是标签，不需要人工标注，因此可以利用互联网上海量的无标注数据。

#### 预训练关键技术

| 技术 | 说明 | 作用 |
|------|------|------|
| **数据清洗** | 去重、过滤低质量、去毒、去除个人信息 | 提升数据质量，减少有害内容 |
| **数据混合** | 不同来源数据按比例混合（网页/书籍/代码/论文） | 平衡各领域能力，避免偏科 |
| **课程学习** | 先训练简单数据，再训练复杂数据 | 训练更稳定，效果更好 |
| **余弦学习率** | 学习率先 warmup 上升，再余弦衰减 | 稳定训练，提升收敛 |
| **混合精度** | BF16/FP16 训练，梯度用 FP32 | 加速训练，节省显存 |
| **分布式训练** | 数据并行/张量并行/流水线并行/ZeRO | 支持超大模型和数据 |
| **梯度检查点** | 前向不保存激活，反向重新计算 | 节省显存（以速度换空间） |
| **Flash Attention** | IO 感知注意力实现 | 加速注意力，节省显存 |
| **权重衰减** | AdamW 优化器，权重衰减解耦 | 防止过拟合，提升泛化 |

#### Scaling Law（缩放定律）

```text
$$
L(N, D, C) = \left( \frac{N_c}{N} \right)^{\alpha_N} + \left( \frac{D_c}{D} \right)^{\alpha_D} + L_0
$$
```

模型性能（损失 L）与三个因素呈幂律关系：
- **N（参数量）**：参数越多，性能越好
- **D（数据量）**：数据越多，性能越好
- **C（计算量）**：计算越多，性能越好

这意味着在一定范围内，扩大规模可以可预测地提升性能，这是大模型"越大越好"的理论基础。

### 2.2 监督微调（SFT）原理

```mermaid
graph TB
    subgraph SFT 数据
        C1[指令-回答对<br/>{"instruction": "翻译", "input": "你好", "output": "Hello"}] --> C2[应用对话模板<br/>system/user/assistant]
        C2 --> C3[Tokenization]
        C3 --> C4[创建 labels<br/>回答部分正常<br/>指令部分 mask=-100]
    end

    subgraph SFT 训练
        D1[输入序列<br/>指令+回答] --> D2[预训练模型<br/>前向传播]
        D2 --> D3[输出 logits]
        D3 --> D4[交叉熵损失<br/>只计算回答部分<br/>指令部分忽略]
        D4 --> D5[反向传播<br/>全参数或LoRA]
    end

    C4 --> D1

    Note over D4: 关键——只对回答部分计算损失<br/>避免模型学习重复指令
    style D4 fill:#c8e6c9
```

#### SFT 损失函数

```text
$$
\mathcal{L}_{SFT} = -\sum_{t \in \text{response}} \log P_\theta(x_t | x_{<t})
$$
```

与预训练目标相同（因果语言建模），但：
1. **数据不同**：指令-回答对而非无标注文本
2. **损失 mask 不同**：只对回答部分计算损失，指令部分 mask 掉（label=-100）

#### 为什么只计算回答部分损失？

- 模型应该学习"给定指令后生成回答"，而非"学习重复指令"
- 如果对指令部分也计算损失，模型可能学会重复用户的指令
- 只计算回答部分，训练更高效，梯度信号更集中

#### SFT 数据构建方法

| 方法 | 说明 | 成本 | 质量 |
|------|------|------|------|
| **人工编写** | 人工编写指令和回答 | 高 | 最高 |
| **AI 生成** | 用强模型（GPT-4o/Claude）生成 | 低 | 高 |
| **真实用户数据** | 从产品日志收集真实对话 | 中 | 高（需隐私处理） |
| **开源数据集** | 直接使用开源 SFT 数据 | 极低 | 中高 |
| **进化指令** | Evol-Instruct，用 AI 进化指令难度 | 低 | 高（WizardLM） |

### 2.3 RLHF 原理

```mermaid
graph TB
    subgraph RLHF 三步骤
        subgraph 步骤1：SFT
            S1[SFT 模型<br/>指令微调]
        end

        subgraph 步骤2：奖励模型 RM
            R1[偏好数据<br/>prompt + chosen + rejected] --> R2[奖励模型训练<br/>对比损失<br/>chosen分数 > rejected分数]
            R2 --> R3[训练好的 RM<br/>输入prompt+response<br/>输出奖励分数]
        end

        subgraph 步骤3：PPO 强化学习
            P1[SFT 模型<br/>初始策略] --> P2[生成回答]
            P2 --> P3[RM 打分<br/>奖励信号]
            P3 --> P4[PPO 更新策略<br/>最大化奖励<br/>KL约束防偏离]
            P4 --> P5[对齐后的模型]
        end

        S1 --> R1
        S1 --> P1
        R3 --> P3
    end

    style R3 fill:#fff9c4
    style P5 fill:#c8e6c9
```

#### 奖励模型（RM）训练

奖励模型学习人类偏好，输入 prompt + response，输出奖励分数：

```text
$$
\mathcal{L}_{RM} = -\mathbb{E}_{(x, y_w, y_l) \sim D} \left[ \log \sigma(r_\phi(x, y_w) - r_\phi(x, y_l)) \right]
$$
```

其中：
- $r_\phi(x, y)$：奖励模型对 prompt x 和回答 y 的分数
- $y_w$：人类偏好的回答（chosen/win）
- $y_l$：人类不偏好的回答（rejected/lose）
- $\sigma$：sigmoid 函数

目标是让 chosen 的分数高于 rejected 的分数。

#### PPO 强化学习

PPO 用奖励模型作为奖励信号，优化策略模型：

```text
$$
\mathcal{L}_{PPO} = \mathbb{E} \left[ r_t - \beta \cdot D_{KL}(\pi_\theta \| \pi_{ref}) \right]
$$
```

其中：
- $r_t$：奖励模型的分数
- $D_{KL}(\pi_\theta \| \pi_{ref})$：策略模型与参考模型（SFT 模型）的 KL 散度
- $\beta$：KL 惩罚系数，控制策略偏离程度

**PPO 关键组件**：
1. **策略模型（πθ）**：正在优化的模型
2. **参考模型（πref）**：冻结的 SFT 模型，用于 KL 约束
3. **奖励模型（rφ）**：冻结的奖励模型，提供奖励信号
4. **价值模型（V）**：估计状态价值，用于 GAE（广义优势估计）
5. **PPO Clip**：限制策略更新幅度，保证训练稳定

#### KL 约束的作用

- 防止策略模型偏离 SFT 模型太远
- 避免语言质量下降（策略可能为了高奖励而生成不自然的文本）
- 防止奖励黑客（策略找到 RM 漏洞）
- β 控制偏离程度——β 大，策略接近参考模型；β 小，策略可以更大胆地优化奖励

### 2.4 DPO 原理（RLHF 简化替代）

```mermaid
graph TB
    subgraph DPO vs RLHF
        subgraph RLHF（复杂）
            RL1[SFT 模型] --> RL2[奖励模型训练]
            RL2 --> RL3[PPO 强化学习]
            RL3 --> RL4[对齐模型]
        end
        subgraph DPO（简单）
            D1[SFT 模型] --> D2[直接偏好优化<br/>对比损失<br/>无需奖励模型/PPO]
            D2 --> D3[对齐模型]
        end
    end

    Note over RL1,RL4: 三步骤，复杂不稳定<br/>需要4个模型
    Note over D1,D3: 单步骤，简单稳定<br/>只需要2个模型

    style D2 fill:#c8e6c9
```

#### DPO 损失函数

```text
$$
\mathcal{L}_{DPO} = -\mathbb{E}_{(x,y_w,y_l)} \left[ \log \sigma \left( \beta \log \frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)} \right) \right]
$$
```

其中：
- $\pi_\theta$：策略模型（正在训练）
- $\pi_{ref}$：参考模型（冻结的 SFT 模型）
- $y_w$：chosen 回答
- $y_l$：rejected 回答
- $\beta$：温度参数，控制 KL 约束强度

#### DPO 的核心洞察

DPO 证明了：在最优策略下，奖励函数可以从策略中解析推导：

```text
$$
r(x, y) = \beta \log \frac{\pi_\theta(y|x)}{\pi_{ref}(y|x)}
$$
```

这意味着不需要单独训练奖励模型——可以直接将奖励函数的表达式代入 RLHF 的目标，得到一个只依赖策略模型和参考模型的损失函数（DPO 损失）。

#### DPO 的优势

| 优势 | 说明 |
|------|------|
| **简单** | 不需要训练奖励模型，不需要 PPO，实现接近 SFT |
| **稳定** | 训练更稳定，不会出现 PPO 的训练崩溃 |
| **低成本** | 只需要策略模型和参考模型（不需要奖励模型和价值模型），计算量接近 SFT |
| **超参数少** | 主要是学习率和 β，不需要调 PPO 的一堆超参数 |
| **效果好** | 多个研究表明 DPO 效果与 RLHF 相当甚至更好 |
| **不容易奖励黑客** | 隐式奖励，不容易被策略找到漏洞 |

---

> 💡 **深度讲解**：三阶段范式的原理可以用"能力逐层释放"来理解——预训练获得"潜在能力"（知识、推理、语言理解），SFT 将潜在能力转化为"可用能力"（遵循指令、对话交互），RLHF/DPO 将可用能力优化为"优质能力"（有用、无害、诚实、符合人类偏好）。每个阶段都建立在前一阶段的基础上，解决不同层次的问题。预训练的原理是"规模涌现"——通过海量数据和大规模参数的自监督学习，模型涌现出各种能力（推理、知识、代码、多语言等）。预训练的目标非常简单（预测下一个 Token），但在大规模下催生了惊人的智能。预训练的关键是数据质量和规模——数据需要清洗（去重、过滤低质量、去毒）、混合（不同来源按比例）、分级（高质量高权重）；规模需要足够大（参数、数据、计算），才能触发涌现能力。Scaling Law 告诉我们，在一定范围内，扩大规模可以可预测地提升性能，这是大模型"越大越好"的理论基础。但预训练也有局限性——它只会"续写文本"，不会"回答问题"，因为预训练数据中没有"问答"的格式（或者说问答格式只是众多文本格式之一，模型没有被明确教导"看到问题要回答"）。SFT 的原理是"格式对齐"——通过指令-回答对的有监督训练，让模型学会"看到指令后生成回答"的交互格式。SFT 的训练目标与预训练相同（预测下一个 Token），但数据和损失计算不同——数据是指令-回答对，损失只计算回答部分（指令部分 mask 掉）。这个看似简单的改变却有显著效果——InstructGPT 表明仅 1.3 万条高质量 SFT 数据就能让模型从"续写器"变成"助手"。SFT 的关键是数据质量——高质量的小数据集通常优于低质量的大数据集，因为 SFT 是在教模型"应该如何回答"，如果数据质量差，模型会学到不好的回答模式。SFT 数据的构建方法包括人工编写（质量最高但成本高）、AI 生成（用强模型生成，成本低质量高，是目前最常用的方法）、真实用户数据（质量高但需隐私处理）、开源数据集（免费但可能质量参差）。SFT 后的模型虽然学会了遵循指令，但仍然存在对齐问题——它可能生成有害内容、不诚实的回答、不符合人类价值观的输出。这是因为 SFT 只教模型"如何回答"（格式和内容），没有教模型"应该回答什么"（价值观和偏好）。例如，SFT 数据中可能包含有害内容的回答（因为互联网上有大量有害内容），模型会学到这些内容；或者 SFT 模型可能为了"回答问题"而编造信息（幻觉），因为它没有被教导"不知道就说不知道"。RLHF 的原理是"偏好对齐"——通过人类偏好数据让模型的输出更符合人类偏好。RLHF 分为三步：① SFT（获得初始策略）；② 训练奖励模型（学习人类偏好，输入 prompt+response 输出奖励分数）；③ PPO 强化学习（用奖励模型作为奖励信号优化策略，同时用 KL 约束防止偏离 SFT 模型太远）。奖励模型的训练使用对比损失——让 chosen 的分数高于 rejected 的分数。PPO 优化的目标是最大化奖励模型分数，同时最小化与参考模型的 KL 散度（防止策略偏离太远导致语言质量下降）。RLHF 的效果显著（ChatGPT 的成功很大程度上归功于 RLHF），但也有缺点：① 训练复杂（需要训练奖励模型，再用 PPO，超参数多）；② 不稳定（PPO 训练容易崩溃，需要仔细调参）；③ 计算成本高（PPO 需要同时维护 4 个模型）；④ 奖励黑客（策略可能找到 RM 漏洞，生成看似高分但实际质量差的输出）。DPO 的原理是"隐式奖励"——DPO 证明了在最优策略下，奖励函数可以从策略中解析推导（r = β·log(πθ/πref)），因此不需要单独训练奖励模型，可以直接将奖励函数代入 RLHF 目标，得到一个只依赖策略模型和参考模型的对比损失。DPO 的损失函数本质上是"增加 chosen 的相对概率，减少 rejected 的相对概率"（相对于参考模型），形式简洁，训练稳定，计算成本接近 SFT。DPO 正在成为对齐的主流方法——Zephyr、Tulu、OpenHermes 等优秀开源模型都使用了 DPO，效果与 RLHF 相当甚至更好。DPO 的优势是简单、稳定、低成本、超参数少、效果好、不容易奖励黑客。三阶段范式的成本分布是极不均衡的——预训练占 95%+ 的成本（数百万到数千万美元），SFT 占 3-5%（数千到数万美元，LoRA 仅数百美元），RLHF/DPO 占 1-2%（数千美元）。这意味着对于大多数团队来说，预训练是不可承受的，应该直接使用开源基础模型；SFT 和对齐是可承受的，是定制模型的主要手段。理解这个成本分布对于技术选型和资源规划非常重要。
>
> **📝 精简总结**：预训练PT原理——数据流水线（原始数据→清洗去重过滤去毒→质量分级→Tokenization→随机截取固定长度样本），目标是因果语言建模L=-Σlog P(x_{t+1}|x<t)，自监督学习文本本身就是标签无需人工标注；关键技术包括数据清洗/数据混合/课程学习/余弦学习率/混合精度BF16/分布式训练/梯度检查点/Flash Attention/权重衰减AdamW；Scaling Law缩放定律L(N,D,C)=(Nc/N)^αN+(Dc/D)^αD+L0，性能与参数量/数据量/计算量幂律关系，越大越好理论基础；SFT原理——数据（指令回答对→应用对话模板→Tokenization→创建labels回答部分正常指令部分mask=-100），训练（输入序列→预训练模型前向→输出logits→交叉熵损失只算回答部分→反向传播全参数或LoRA），损失函数L=-Σ_{t∈response}log P(xt|x<t)与预训练相同但数据和mask不同；只算回答部分避免学重复指令，训练更高效梯度更集中；数据构建方法包括人工编写（高成本最高质量）、AI生成（低成本高质量最常用）、真实用户数据（中成本高需隐私）、开源数据集（极低成本中高质量）、进化指令Evol-Instruct（低成本高）；RLHF原理——三步骤（SFT→奖励模型RM训练→PPO强化学习）；RM训练用对比损失L_RM=-E[log σ(r(x,yw)-r(x,yl))]，目标chosen分数>rejected；PPO优化目标L_PPO=E[r_t-β·D_KL(πθ||πref)]，最大化奖励+KL约束防偏离；关键组件包括策略模型πθ/参考模型πref/奖励模型rφ/价值模型V/PPO Clip；KL约束防止偏离太远/语言质量下降/奖励黑客，β控制偏离程度；DPO原理（RLHF简化替代）——RLHF三步骤复杂不稳定需4模型，DPO单步骤简单稳定只需2模型；损失函数L_DPO=-E[log σ(β log(πθ(yw)/πref(yw))-β log(πθ(yl)/πref(yl)))]；核心洞察是最优策略下奖励函数可解析推导r(x,y)=β log(πθ/πref)，无需单独训练奖励模型；优势是简单（无需RM/PPO实现接近SFT）、稳定（不会PPO崩溃）、低成本（只需策略+参考模型计算量接近SFT）、超参数少（学习率+β）、效果好（相当甚至优于RLHF）、不容易奖励黑客（隐式奖励）；核心原理是能力逐层释放——PT获得潜在能力（知识推理语言理解，规模涌现）、SFT转化为可用能力（遵循指令对话交互，格式对齐）、RLHF/DPO优化为优质能力（有用无害诚实符合偏好，偏好对齐）；成本分布极不均衡——PT占95%+数百万数千万、SFT占3-5%数千数万LoRA数百、RLHF/DPO占1-2%数千，大多数团队直接用开源基础模型，SFT和对齐是定制主要手段。

---

## 三、实操

### 3.1 三阶段训练完整流程

```python
# 完整的三阶段训练流程（使用开源工具）
# 阶段1：预训练（通常跳过，直接使用开源基础模型）
# 阶段2：SFT 监督微调
# 阶段3：DPO 对齐（用 DPO 替代复杂的 RLHF）

# ============================================================
# 阶段2：SFT 监督微调
# ============================================================
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig

# 1. 加载基础模型（已经过预训练）
base_model = "Qwen/Qwen2.5-7B-Instruct"  # 也可以用基础版非Instruct
tokenizer = AutoTokenizer.from_pretrained(base_model)
tokenizer.pad_token = tokenizer.eos_token

# 4bit 量化（QLoRA）
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    base_model,
    quantization_config=bnb_config,
    device_map="auto",
)
model = prepare_model_for_kbit_training(model)

# 2. LoRA 配置
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
)
model = get_peft_model(model, lora_config)

# 3. 加载 SFT 数据（指令-回答对）
sft_dataset = load_dataset("json", data_files="sft_data.jsonl", split="train")

# 4. SFT 训练配置
sft_args = SFTConfig(
    output_dir="./sft-output",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    logging_steps=10,
    save_steps=100,
    bf16=True,
    gradient_checkpointing=True,
    optim="paged_adamw_8bit",
    max_seq_length=2048,
    report_to="none",
)

# 5. SFT 训练
sft_trainer = SFTTrainer(
    model=model,
    args=sft_args,
    train_dataset=sft_dataset,
    tokenizer=tokenizer,
)
sft_trainer.train()
sft_trainer.save_model("./sft-final")

# ============================================================
# 阶段3：DPO 对齐（用 DPO 替代 RLHF）
# ============================================================
from trl import DPOTrainer, DPOConfig

# 1. 加载 SFT 模型（作为策略模型和参考模型）
sft_model_path = "./sft-final"
model = AutoModelForCausalLM.from_pretrained(
    sft_model_path,
    quantization_config=bnb_config,
    device_map="auto",
)
model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, lora_config)

# 2. 加载 DPO 偏好数据（chosen/rejected 对）
dpo_dataset = load_dataset("json", data_files="preference_data.jsonl", split="train")
# 格式: {"prompt": "...", "chosen": "...", "rejected": "..."}

# 3. DPO 训练配置
dpo_args = DPOConfig(
    output_dir="./dpo-output",
    num_train_epochs=1,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=5e-7,              # DPO 学习率比 SFT 小
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,
    logging_steps=10,
    save_steps=50,
    bf16=True,
    gradient_checkpointing=True,
    optim="paged_adamw_8bit",
    beta=0.1,                         # DPO β 参数
    max_length=1024,
    max_prompt_length=512,
    report_to="none",
)

# 4. DPO 训练
dpo_trainer = DPOTrainer(
    model=model,
    ref_model=None,                   # 自动创建参考模型
    args=dpo_args,
    train_dataset=dpo_dataset,
    tokenizer=tokenizer,
)
dpo_trainer.train()
dpo_trainer.save_model("./dpo-final")

print("三阶段训练完成！最终模型保存在 ./dpo-final")
```

### 3.2 SFT 数据构建实战

```python
# SFT 数据构建：用 AI 生成高质量指令-回答对
import json
from openai import OpenAI

client = OpenAI()

def generate_sft_data(topic: str, n: int = 50) -> list:
    """用 AI 生成特定主题的 SFT 数据"""
    # 1. 生成指令
    prompt = f"""请生成 {n} 个关于{topic}的多样化用户指令，涵盖：
- 知识问答（是什么/为什么/怎么样）
- 操作指导（如何做/步骤）
- 对比分析（A和B的区别）
- 问题解决（遇到X问题怎么办）
- 创意生成（写一首诗/设计一个方案）

每行一个指令，不要编号，不要解释。"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    instructions = [line.strip() for line in response.choices[0].message.content.split('\n') if line.strip()]

    # 2. 为每个指令生成回答
    sft_data = []
    for instruction in instructions[:n]:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一个专业、有帮助的助手。请用中文详细、准确地回答用户的问题。"},
                {"role": "user", "content": instruction}
            ],
            temperature=0.7
        )
        answer = response.choices[0].message.content

        sft_data.append({
            "messages": [
                {"role": "system", "content": "你是一个专业、有帮助的助手。"},
                {"role": "user", "content": instruction},
                {"role": "assistant", "content": answer}
            ]
        })

    return sft_data

# 生成多个主题的数据
all_data = []
topics = ["Python编程", "机器学习", "数据分析", "产品设计", "项目管理"]
for topic in topics:
    data = generate_sft_data(topic, n=30)
    all_data.extend(data)
    print(f"生成 {topic}: {len(data)} 条")

# 数据清洗和过滤
def clean_sft_data(data: list) -> list:
    """清洗 SFT 数据"""
    cleaned = []
    seen = set()
    for item in data:
        messages = item["messages"]
        user_msg = next(m["content"] for m in messages if m["role"] == "user")
        assistant_msg = next(m["content"] for m in messages if m["role"] == "assistant")

        # 去重
        if user_msg in seen:
            continue
        seen.add(user_msg)

        # 长度过滤
        if len(assistant_msg) < 20 or len(assistant_msg) > 2000:
            continue

        # 过滤拒绝回答
        if any(kw in assistant_msg for kw in ["我无法回答", "我不能回答", "作为AI语言模型"]):
            continue

        cleaned.append(item)
    return cleaned

cleaned_data = clean_sft_data(all_data)
print(f"原始: {len(all_data)}, 清洗后: {len(cleaned_data)}")

# 保存为 JSONL
with open("sft_data.jsonl", 'w', encoding='utf-8') as f:
    for item in cleaned_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')
```

### 3.3 偏好数据构建与 DPO 训练

```python
# 偏好数据构建：用 AI 生成 chosen/rejected 对
def generate_preference_data(prompts: list, n: int = 50) -> list:
    """生成偏好数据：强模型生成 chosen，弱模型生成 rejected"""
    preference_data = []

    for prompt in prompts[:n]:
        # chosen: 强模型生成
        chosen = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        ).choices[0].message.content

        # rejected: 弱模型生成（或强模型低温度/限制长度）
        rejected = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        ).choices[0].message.content

        # 确保 chosen 和 rejected 不同
        if chosen != rejected:
            preference_data.append({
                "prompt": prompt,
                "chosen": chosen,
                "rejected": rejected
            })

    return preference_data

# 用奖励模型排序生成偏好数据
def generate_preference_with_rm(prompts: list, n_responses: int = 4) -> list:
    """生成多个回答，用奖励模型排序，取最好和最差"""
    preference_data = []
    for prompt in prompts:
        # 生成多个回答
        responses = []
        for _ in range(n_responses):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=1.0  # 高温度增加多样性
            ).choices[0].message.content
            responses.append(response)

        # 用奖励模型打分（或用 LLM-as-Judge）
        scores = []
        for r in responses:
            score = judge_quality(prompt, r)  # 用 LLM 打分 1-5
            scores.append(score)

        # 取最高分和最低分
        best_idx = scores.index(max(scores))
        worst_idx = scores.index(min(scores))

        if best_idx != worst_idx:
            preference_data.append({
                "prompt": prompt,
                "chosen": responses[best_idx],
                "rejected": responses[worst_idx]
            })

    return preference_data

def judge_quality(prompt: str, response: str) -> int:
    """用 LLM 评估回答质量（1-5分）"""
    judge_prompt = f"""请评估以下回答的质量，从有用性、准确性、完整性三个维度打分（1-5分），只返回总分。

问题：{prompt}
回答：{response}

总分（1-5）："""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": judge_prompt}],
        temperature=0
    )
    try:
        return int(response.choices[0].message.content.strip())
    except:
        return 3

# 保存偏好数据
with open("preference_data.jsonl", 'w', encoding='utf-8') as f:
    for item in preference_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')
```

### 3.4 继续预训练（CPT）实战

```python
# 继续预训练（Continued Pre-training）：在领域数据上继续预训练，注入领域知识
# 适用于领域专用模型（医疗/法律/金融等）

from transformers import DataCollatorForLanguageModeling, TrainingArguments, Trainer

# 1. 加载基础模型（非 Instruct 版本）
base_model = "Qwen/Qwen2.5-7B"  # 基础版，非 Instruct
tokenizer = AutoTokenizer.from_pretrained(base_model)

model = AutoModelForCausalLM.from_pretrained(
    base_model,
    quantization_config=bnb_config,
    device_map="auto",
)
model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, lora_config)

# 2. 加载领域文本数据（无标注，纯文本）
cpt_dataset = load_dataset("text", data_files="domain_corpus.txt", split="train")

# 3. 数据整理：因果语言建模的数据整理器
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,  # 因果语言建模，不是掩码语言建模
)

# 4. CPT 训练配置
cpt_args = TrainingArguments(
    output_dir="./cpt-output",
    num_train_epochs=1,                    # CPT 通常 1 个 epoch
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=2e-5,                    # CPT 学习率小（比 SFT 小）
    lr_scheduler_type="cosine",
    warmup_ratio=0.05,
    logging_steps=10,
    save_steps=200,
    bf16=True,
    gradient_checkpointing=True,
    optim="paged_adamw_8bit",
    report_to="none",
)

# 5. CPT 训练
cpt_trainer = Trainer(
    model=model,
    args=cpt_args,
    train_dataset=cpt_dataset,
    data_collator=data_collator,
)
cpt_trainer.train()
cpt_trainer.save_model("./cpt-final")

# CPT 后再做 SFT 和 DPO
print("CPT 完成，接下来可以做 SFT 和 DPO")
```

### 3.5 模型评估与对比

```python
# 三阶段模型评估：基础模型 vs SFT vs DPO
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def evaluate_model(model_path: str, eval_prompts: list, model_name: str = "model") -> dict:
    """评估模型效果"""
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, torch_dtype=torch.bfloat16, device_map="auto"
    )
    model.eval()

    results = {
        "model_name": model_name,
        "instruction_following": [],   # 指令遵循率
        "response_quality": [],         # 回答质量（LLM-as-Judge 1-5）
        "response_length": [],          # 回答长度
        "refusal_rate": [],             # 拒绝率
    }

    for prompt in eval_prompts:
        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to("cuda")

        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.7, do_sample=True)

        response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

        results["response_length"].append(len(response))
        # 指令遵循率、回答质量可用 LLM-as-Judge 自动评估
        # results["instruction_following"].append(...)
        # results["response_quality"].append(...)

    avg_length = sum(results["response_length"]) / len(results["response_length"])
    print(f"\n=== {model_name} ===")
    print(f"平均回答长度: {avg_length:.1f}")
    # print(f"指令遵循率: {sum(results['instruction_following'])/len(...):.2%}")
    # print(f"平均质量分: {sum(results['response_quality'])/len(...):.2f}")

    return results

# 对比三个阶段的模型
eval_prompts = [
    "什么是大语言模型？",
    "用 Python 写一个快速排序",
    "解释一下量子计算",
    "如何提高工作效率？",
    "写一首关于秋天的诗",
]

base_results = evaluate_model("Qwen/Qwen2.5-7B", eval_prompts, "基础模型（PT）")
sft_results = evaluate_model("./sft-final", eval_prompts, "SFT 模型")
dpo_results = evaluate_model("./dpo-final", eval_prompts, "DPO 对齐模型")

# 对比总结
print("\n=== 三阶段对比总结 ===")
print("基础模型（PT）：有语言能力，但不会遵循指令，只会续写文本")
print("SFT 模型：学会遵循指令和对话格式，能回答问题")
print("DPO 模型：对齐人类偏好，回答更有用、无害、诚实")
print("\n能力提升路径：PT（潜在能力）→ SFT（可用能力）→ DPO（优质能力）")
```

---

> 💡 **深度讲解**：三阶段训练的实操核心是"数据 + 配置 + 评估"。数据是三阶段训练的核心——每个阶段的数据类型和质量要求不同。预训练数据是海量无标注文本（万亿 Token），需要清洗、去重、过滤、混合，但数据质量要求中等（因为量大，少量低质量数据影响有限）。SFT 数据是指令-回答对（1万-100万条），数据质量要求高——InstructGPT 表明 1.3 万条高质量人工标注数据的效果优于 100 万条低质量 AI 生成数据。SFT 数据的构建方法包括：① 人工编写（质量最高但成本高，适合关键场景）；② AI 生成（用强模型 GPT-4o/Claude 生成，成本低质量高，是目前最常用的方法）；③ 真实用户数据（从产品日志收集，质量高但需隐私处理）；④ 开源数据集（Alpaca/OpenHermes/ShareGPT 等，免费但质量参差）；⑤ 进化指令（Evol-Instruct，用 AI 进化指令难度，WizardLM 方法）。SFT 数据需要清洗——去重、长度过滤、过滤拒绝回答、格式统一。偏好数据（RLHF/DPO）是 chosen/rejected 对（1万-10万对），数据质量要求最高——chosen 和 rejected 的差异要明显且有意义，如果差异太小，DPO 学不到有意义的偏好信号。偏好数据的构建方法包括：① 人类标注（质量最高但成本高）；② AI 反馈（强模型生成 chosen，弱模型生成 rejected，成本低质量尚可）；③ 奖励模型排序（生成多个回答用奖励模型排序取最好最差）；④ LLM-as-Judge（用强模型评估多个回答的质量取最好最差）。偏好数据需要确保 chosen 明显优于 rejected，差异太小的样本应该过滤。配置是三阶段训练的另一个核心——每个阶段的超参数不同。预训练的学习率通常是 1e-4 到 3e-4（大 batch，余弦调度，warmup 3-5%），训练数千到数万步；SFT 的学习率通常是 1e-5 到 5e-5（全参数）或 1e-4 到 3e-4（LoRA），训练 2-3 个 epoch；DPO 的学习率通常是 5e-7 到 5e-6（比 SFT 小，因为是在 SFT 模型基础上微调），β=0.1-0.3，训练 1 个 epoch。继续预训练（CPT）的学习率通常是 1e-5 到 2e-5（比 SFT 小，因为是继续预训练而非微调），训练 1 个 epoch。LoRA/QLoRA 是小团队训练的标配——可以将显存需求降低 75%+，7B 模型可以在单张 24GB 显卡上训练，成本从数万美元降到数百美元。LoRA 的 r=16-32，target_modules 包含所有注意力层和 MLP 层，效果接近全参数微调。评估是三阶段训练的重要环节——需要在每个阶段后评估模型效果，确认能力提升。评估方法包括：① 自动基准测试（MMLU 知识、GSM8K 数学、HumanEval 代码、MT-Bench 对话）；② LLM-as-Judge（用强模型评估回答质量，1-5 分）；③ 人工评估（小规模高质量验证集，人工打分）；④ 对比评估（基础模型 vs SFT vs DPO，确认每阶段的提升）。评估需要同时看领域任务（提升）和通用任务（对齐税），警惕过拟合和灾难性遗忘。三阶段训练的完整流程是：① 选择基础模型（开源预训练模型，如 Llama/Qwen/Mistral）；② （可选）继续预训练 CPT（如果需要领域知识注入）；③ SFT 监督微调（用指令-回答对教模型遵循指令）；④ DPO 对齐（用偏好数据对齐人类价值观，替代复杂的 RLHF）；⑤ 评估和迭代（评估效果，收集 bad case，优化数据和配置，重新训练）。对于大多数应用场景，使用已经经过 SFT 和对齐的指令微调模型（如 Llama-3-Instruct、Qwen2.5-Instruct）可以跳过②③④，直接使用或只做领域 SFT。
>
> **📝 精简总结**：三阶段训练完整流程——阶段1预训练（通常跳过，直接用开源基础模型）；阶段2 SFT（加载基础模型+4bit NF4量化+LoRA配置r16全注意力+MLP→加载SFT数据指令回答对→SFTConfig学习率2e-4/cosine/3epoch/bf16/梯度检查点/paged_adamw_8bit/max_seq2048→SFTTrainer训练→保存）；阶段3 DPO（加载SFT模型作为策略+参考模型→加载偏好数据prompt/chosen/rejected→DPOConfig学习率5e-7比SFT小/β=0.1/1epoch/bf16→DPOTrainer训练→保存）；SFT数据构建实战——用AI生成（先生成多样化指令涵盖知识问答/操作指导/对比分析/问题解决/创意生成，再为每个指令用gpt-4o生成详细回答，messages格式system/user/assistant），多主题数据（Python/机器学习/数据分析/产品设计/项目管理），数据清洗（去重/长度过滤20-2000/过滤拒绝回答关键词），保存JSONL；偏好数据构建——AI反馈法（强模型gpt-4o生成chosen，弱模型gpt-4o-mini生成rejected，确保不同），奖励模型排序法（生成4个回答高温度增多样性→LLM-as-Judge打分1-5→取最高分best和最低分worst作为chosen/rejected），LLM-as-Judge用gpt-4o评估有用性/准确性/完整性只返回总分；继续预训练CPT实战——加载基础模型非Instruct版本→加载领域纯文本数据→DataCollatorForLanguageModeling(mlm=False因果LM)→TrainingArguments学习率2e-5比SFT小/1epoch/cosine/warmup0.05→Trainer训练→保存，CPT后再做SFT和DPO；模型评估与对比——evaluate_model函数（加载模型→对每个eval_prompt用apply_chat_template+generate生成回答→统计响应长度/指令遵循率/回答质量LLM-as-Judge/拒绝率），对比基础模型PT vs SFT vs DPO，能力提升路径PT潜在能力→SFT可用能力→DPO优质能力；实操核心是数据（PT海量无标注中等质量/SFT指令回答对高质量1万-100万/偏好chosen-rejected对最高质量1万-10万，构建方法人工/AI生成/真实用户/开源/进化指令，清洗去重/长度/过滤/格式）+配置（PT学习率1e-4~3e-4/SFT全参数1e-5~5e-5 LoRA1e-4~3e-4/DPO 5e-7~5e-6 β0.1-0.3/CPT 1e-5~2e-5，LoRA/QLoRA标配降显存75%+）+评估（自动基准MMLU/GSM8K/HumanEval/MT-Bench+LLM-as-Judge+人工评估+对比评估，领域+通用双评估警惕对齐税）；完整流程是选基础模型→可选CPT→SFT→DPO→评估迭代，大多数场景用指令微调模型可跳过CPT/SFT/DPO直接用或只做领域SFT。

---

## 四、问题

### 4.1 常见错误与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **SFT 后模型不遵循指令** | 数据格式错误 / 对话模板不匹配 / 学习率太小 / epoch太少 | 检查数据格式（messages），用 apply_chat_template 验证模板，增大学习率，增加 epoch，检查是否只算回答损失 |
| **SFT 后模型重复用户指令** | 对指令部分也计算了损失 / 未正确 mask | 确保只对回答部分计算损失（SFTTrainer 自动处理，自定义训练需手动 mask 指令部分 label=-100） |
| **SFT 过拟合（训练好验证差）** | 数据量小 / epoch太多 / 学习率太大 / r太大 | 增加数据，减少 epoch（1-2），降低学习率，减小 r（8-16），加 dropout，早停 |
| **灾难性遗忘（通用能力下降）** | 学习率太大 / epoch太多 / 数据分布偏移 / 全参数微调 | 降低学习率/epoch，混合 10-30% 通用数据，用 LoRA 而非全参数，知识蒸馏，评估通用任务 |
| **DPO 对齐效果不明显** | β太小 / 偏好数据差异太小 / 学习率太小 / epoch太少 | 增大 β（0.1→0.3），确保 chosen 明显优于 rejected，增大学习率，增加 epoch，增加偏好数据量 |
| **DPO 后语言质量下降（对齐税）** | β太大 / 学习率太大 / epoch太多 / 偏好数据单一 | 减小 β（0.3→0.1），降低学习率，减少 epoch（1个），多样化偏好数据，混合通用数据，监控困惑度 |
| **RLHF 训练不稳定（PPO崩溃）** | 学习率太大 / PPO clip范围不当 / KL系数不当 / 奖励模型过拟合 | 降低学习率，调整 clip_range（0.1-0.2），调整 KL 系数，检查奖励模型质量，用 DPO 替代 RLHF |
| **奖励黑客（Reward Hacking）** | 奖励模型有漏洞 / 策略过度优化奖励 / KL约束太弱 | 增强奖励模型（更多数据/定期更新），增大 KL 系数，用 DPO（隐式奖励不容易被黑），人工审核高奖励输出 |
| **CPT 后模型能力下降** | 学习率太大 / 数据质量差 / 训练太多 / 灾难性遗忘 | 降低学习率（1e-5~2e-5），提升数据质量，减少训练步数，混合通用数据，用 LoRA |
| **训练显存不足（OOM）** | 模型太大 / batch太大 / 未用4bit量化 / 未用梯度检查点 | 用 QLoRA 4bit，减小 batch，开启 gradient_checkpointing，用 paged_adamw_8bit，减小序列长度，梯度累积 |
| **数据质量差导致效果差** | AI生成数据质量低 / 未清洗 / 有噪声 / 重复多 | 用强模型生成数据，人工抽检，数据清洗（去重/过滤/格式统一），用 LLM-as-Judge 评估数据质量，过滤低分数据 |
| **评估结果不可靠** | 验证集太小 / 评估方法主观 / 未对比基线 | 增大验证集（50-200条），用 LLM-as-Judge 自动评估，训练前评估基线做对比，多次评估取平均 |
| **三阶段顺序错误** | 跳过 SFT 直接做 RLHF / 预训练后直接部署 | 必须先 SFT 再 RLHF/DPO（SFT 是对齐的基础），预训练模型需要 SFT+对齐才能成为对话助手，不要跳步 |
| **用指令微调模型做 SFT 导致冲突** | 已经 Instruct 的模型再做 SFT，格式冲突 / 过拟合 | 如果用 Instruct 模型，只做领域 SFT（领域数据），不要重复通用 SFT，减小学习率和 epoch，确认对话模板一致 |

### 4.2 性能优化策略

| 优化点 | 策略 | 预期效果 |
|--------|------|---------|
| **训练效率** | LoRA/QLoRA、4bit量化、梯度检查点、混合精度、Flash Attention 2 | 显存降75%+，7B单卡可训 |
| **数据效率** | 高质量数据、数据增强、主动学习、进化指令（Evol-Instruct） | 数据需求降50-70%，效果提升 |
| **对齐效率** | DPO替代RLHF、AI反馈（RLAIF）、在线学习、少样本对齐 | 对齐成本降80%+，效果相当 |
| **推理效率** | 合并LoRA、vLLM/TGI推理、连续批处理、PagedAttention、量化 | 推理吞吐量5-20倍 |
| **分布式训练** | DeepSpeed/FSDP、多卡数据并行、张量并行、流水线并行 | 支持更大模型，训练速度提升 |
| **超参数优化** | 学习率扫描、β扫描、早停、验证集选择、超参数搜索 | 找到最优配置，避免过拟合 |
| **模型选择** | 合适大小模型（不是越大越好）、领域预训练模型、指令微调模型 | 成本降低，效果提升 |
| **缓存优化** | KV缓存、前缀缓存、数据缓存、Embedding缓存 | 训练/推理速度20-50% |
| **评估效率** | 自动化评估、LLM-as-Judge、小规模验证集、早停、持续监控 | 评估成本降80%+，及时发现问题 |
| **成本优化** | LoRA替代全参数、DPO替代RLHF、AI生成替代人工标注、开源模型替代闭源API | 总成本降90%+ |
| **持续学习** | 增量训练、在线学习、用户反馈闭环、数据飞轮 | 模型持续提升，适应新场景 |
| **混合精度** | BF16训练（推荐）、FP8推理、梯度FP32、优化器状态8bit | 训练稳定，显存降50% |

### 4.3 安全风险与防护

| 风险 | 说明 | 防护措施 |
|------|------|---------|
| **对齐不足** | 模型仍生成有害/有偏见/不诚实内容 | 增加无害性偏好数据，红队测试，安全过滤，持续监控，DPO/RLHF充分对齐 |
| **过度对齐（对齐税）** | 模型过于保守，拒绝合理请求，通用能力下降 | 平衡有用性和无害性，多样化偏好数据，减小β，混合通用数据，评估拒绝率和通用能力 |
| **数据投毒** | 训练数据被恶意注入，导致模型行为异常 | 数据审核，来源验证，异常检测，人工抽检，数据清洗，供应链安全 |
| **隐私泄露** | 训练数据包含敏感信息，模型记忆并输出 | 数据脱敏，隐私过滤，差分隐私，记忆检测，合规审查，用户数据不用于训练 |
| **偏见放大** | 训练数据中的偏见被模型放大 | 偏见检测，去偏数据，公平性评估，多样化数据，人工审核，持续监控 |
| **奖励黑客** | 策略找到奖励模型漏洞，生成看似高分但质量差的输出 | 增强奖励模型，定期更新RM，增大KL约束，用DPO（隐式奖励），人工审核高奖励输出 |
| **模型滥用** | 模型被用于恶意目的（诈骗/虚假信息/恶意代码） | 使用限制，访问控制，速率限制，滥用检测，内容审核，用户认证，法律条款 |
| **知识产权** | 训练数据包含受版权保护内容，模型输出侵权 | 数据版权审查，合理使用评估，来源标注，输出查重，合规审查 |
| **供应链安全** | 依赖第三方模型/库/数据有安全漏洞 | 供应商审查，版本锁定，安全扫描，漏洞监控，应急响应，模型签名验证 |
| **合规风险** | AI应用违反数据保护法（GDPR/个保法）、行业监管 | 合规评估，数据治理，用户同意，可解释性，审计日志，本地化部署，行业合规认证 |

### 4.4 生产环境踩坑记录

**踩坑1：跳过 SFT 直接做 DPO 导致对齐效果极差**
- **现象**：为了"节省时间"，跳过 SFT 阶段，直接在基础模型（Base Model，非 Instruct）上做 DPO 对齐，结果 DPO 训练损失正常下降，但模型完全不会遵循指令，输出随机文本，对齐效果几乎为零
- **原因**：① DPO（和 RLHF）是在 SFT 模型基础上做的偏好对齐，它优化的是"在遵循指令的前提下，输出更符合人类偏好"；② 基础模型只会"续写文本"，不会"回答问题"，没有 SFT 教模型对话格式和指令遵循，DPO 无法在一个"不会对话"的模型上做对话对齐；③ DPO 的参考模型通常是 SFT 模型，如果参考模型是基础模型，策略模型也只会学习基础模型的行为（续写文本）
- **方案**：① 必须先做 SFT 再做 DPO/RLHF——SFT 是对齐的必要前置步骤，不能跳过；② SFT 不需要太多数据——1万-5万条高质量指令-回答对通常足够让模型学会遵循指令和对话格式；③ 如果使用已经经过 SFT 的指令微调模型（如 Llama-3-Instruct、Qwen2.5-Instruct），可以跳过 SFT 直接做领域 DPO，但不能在非 Instruct 的基础模型上跳过 SFT；④ 验证 SFT 效果——SFT 后用几个测试 prompt 验证模型能正常遵循指令和对话格式，确认 SFT 成功后再做 DPO；⑤ DPO 的参考模型应该用 SFT 模型（而非基础模型），确保策略模型从"会对话"的状态开始优化偏好

**踩坑2：DPO 偏好数据中 chosen 和 rejected 差异太小导致对齐无效**
- **现象**：DPO 训练损失正常下降，但评估发现对齐效果几乎没有提升（偏好胜率 50%，和随机一样），模型输出与 SFT 模型几乎没有区别
- **原因**：① 偏好数据中 chosen 和 rejected 是同一个模型用不同随机种子生成的，差异很小（只是措辞不同，质量相当），DPO 学不到有意义的偏好信号；② 没有对偏好数据进行质量过滤，很多样本的 chosen 并不明显优于 rejected；③ 偏好数据量太少（只有几百对），不足以让模型学习到稳定的偏好；④ β 太小（0.01），策略几乎不偏离参考模型
- **方案**：① 确保 chosen 明显优于 rejected——用强模型（GPT-4o/Claude）生成 chosen，弱模型（GPT-4o-mini/旧模型）生成 rejected，或者用人类标注确保质量差异；② 对偏好数据进行质量过滤——用奖励模型或 LLM-as-Judge 计算 chosen 和 rejected 的分数差，只保留差异大的样本（差异 > 阈值，如 chosen 分数 4+，rejected 分数 2-）；③ 增加偏好数据量到几千到几万对，多样化偏好数据（覆盖各种任务类型和偏好维度：有用性、无害性、诚实性、格式等）；④ 增大 β 到 0.1-0.3（β 太小对齐效果弱）；⑤ 用奖励模型排序法生成偏好数据——生成多个回答（4-8个），用奖励模型打分，取最高分作为 chosen，最低分作为 rejected，这样差异通常比较明显；⑥ 评估偏好数据质量——随机抽取 50-100 对偏好数据人工审核，确认 chosen 确实优于 rejected，差异率应该 > 90%

**踩坑3：全参数 SFT 导致严重灾难性遗忘，模型"只会领域任务"**
- **现象**：用医疗数据全参数微调 7B 模型（学习率 5e-5，3 个 epoch），医疗任务准确率提升 20%，但通用知识测试（MMLU）下降 15%，数学推理（GSM8K）下降 12%，代码能力（HumanEval）下降 10%，模型变得"只会医疗，其他都不会"
- **原因**：① 全参数微调更新了所有参数，包括存储通用知识的 MLP 层和注意力层，通用知识被"覆盖"；② 学习率太大（5e-5 对于全参数 SFT 偏大），参数更新过猛；③ epoch 太多（3 个），过拟合医疗数据；④ 训练数据只有医疗数据，没有混合通用数据，数据分布严重偏移；⑤ 没有在通用任务上评估，只关注医疗任务，发现问题时已经严重过拟合
- **方案**：① 用 LoRA/QLoRA 而非全参数微调——LoRA 只更新少量参数（0.1-1%），对原权重的干扰小，灾难性遗忘通常比全参数小很多；② 如果必须全参数微调，降低学习率到 1e-5 到 2e-5，减少 epoch 到 1-2 个；③ 在 SFT 数据中混合 10-30% 的通用指令数据（如 Alpaca、OpenHermes、GPT4-LLM），保持模型的通用能力；④ 用知识蒸馏——在 SFT 损失中加入对基础模型输出的 KL 散度约束，防止策略偏离太远；⑤ 选择性微调——只在注意力层加 LoRA，不加 MLP 层（MLP 层存储了大量知识，不更新可以减少遗忘）；⑥ 训练过程中定期评估通用任务（MMLU/GSM8K/HumanEval），发现下降及时停止或调整；⑦ 用持续学习方法——Elastic Weight Consolidation（EWC）保护重要参数，或经验回放（Replay）混合旧数据；⑧ 如果已经过拟合，可以用基础模型 + LoRA 重新微调（而非全参数），或在通用数据上继续微调恢复通用能力

---

> 💡 **深度讲解**：三阶段训练生产环境的核心挑战是"数据质量、训练稳定性、效果保持"。数据质量是三阶段训练的生命线——每个阶段的数据质量直接决定最终效果。预训练数据需要清洗（去重、过滤低质量、去毒、去除个人信息）、混合（不同来源按比例）、分级（高质量高权重），但因为数据量大，少量低质量数据影响有限。SFT 数据质量要求高——1 万条高质量人工标注数据的效果通常优于 100 万条低质量 AI 生成数据，因为 SFT 是在教模型"应该如何回答"，低质量数据会教模型不好的回答模式。SFT 数据的常见质量问题包括：① 回答错误（事实错误、逻辑错误）；② 格式混乱（对话模板不统一、角色标记错误）；③ 重复数据（相同或相似的指令-回答对）；④ 拒绝回答（"我无法回答"、"作为AI..."）；⑤ 长度不当（太短信息量不足，太长浪费计算）；⑥ 分布偏移（只覆盖特定任务类型，缺乏多样性）。SFT 数据质量控制应该包括：自动过滤（去重、长度过滤、拒绝回答过滤、格式校验）、LLM-as-Judge 质量评估（用强模型评估每条数据的质量，过滤低分）、人工抽检（随机抽取 5-10% 人工审核）、多样性检查（统计任务类型分布、长度分布、难度分布）。偏好数据（DPO/RLHF）质量要求最高——chosen 和 rejected 的差异必须明显且有意义，如果差异太小（只是措辞不同，质量相当），DPO 学不到有意义的偏好信号，对齐效果几乎为零。偏好数据的质量控制应该包括：① 确保 chosen 明显优于 rejected（用强模型 vs 弱模型，或人类标注）；② 质量过滤（用奖励模型/LLM-as-Judge 计算分数差，只保留差异大的样本）；③ 多样性（覆盖有用性、无害性、诚实性、格式等多种偏好维度）；④ 人工审核（随机抽检确认差异明显）。训练稳定性是三阶段训练的基本要求——特别是 RLHF 的 PPO 训练非常不稳定，容易崩溃。DPO 比 RLHF 稳定得多（训练更像监督学习），这也是 DPO 正在成为主流的原因之一。训练稳定性保障包括：① 合理的学习率（SFT 全参数 1e-5~5e-5，LoRA 1e-4~3e-4，DPO 5e-7~5e-6）；② 充分的 warmup（3-10% steps，防止训练初期梯度不稳定）；③ 梯度裁剪（max_norm=1.0，防止梯度爆炸）；④ BF16 混合精度（比 FP16 动态范围大，不会下溢）；⑤ Pre-LN（比 Post-LN 训练更稳定）；⑥ LoRA/QLoRA（比全参数训练更稳定，参数更新幅度小）；⑦ 检查点保存和恢复（每 100-500 step 保存，训练中断后能恢复）；⑧ 日志和监控（损失、学习率、梯度范数、显存、奖励分数，及时发现异常）。效果保持是三阶段训练的核心目标——每个阶段都应该提升目标能力，同时不显著降低其他能力。过拟合和灾难性遗忘是效果保持的主要敌人。过拟合防控包括：① 验证集早停（验证损失不再下降时停止）；② 减少 epoch（SFT 2-3 个，DPO 1 个）；③ 降低学习率；④ 减小 LoRA r（8-16）；⑤ 加 dropout（0.05-0.1）；⑥ 数据增强（增加数据多样性）。灾难性遗忘防控包括：① LoRA 优先（比全参数遗忘小）；② 混合通用数据（10-30%）；③ 知识蒸馏（KL 约束）；④ 选择性微调（只注意力层，不加 MLP 层）；⑤ 持续评估通用任务（MMLU/GSM8K/HumanEval），发现下降及时调整；⑥ 减小学习率和 epoch。三阶段训练的成本优化是生产环境的重要考量——预训练占 95%+ 成本（不可承受，用开源模型），SFT 和对齐占 5%（可承受，是定制主要手段）。成本优化策略包括：① LoRA/QLoRA（显存降 75%+，单卡可训，成本从数万降到数百）；② DPO 替代 RLHF（不需要奖励模型和 PPO，计算量接近 SFT，成本降 80%+）；③ AI 生成数据替代人工标注（成本降 90%+，质量尚可）；④ 开源模型替代闭源 API（一次性成本 vs 持续 API 费用，大规模使用更划算）；⑤ 批量处理和梯度累积（模拟大 batch，不需要多卡）；⑥ 4bit/8bit 量化推理（降低部署成本）；⑦ 自动化评估（LLM-as-Judge 替代人工评估，成本降 80%+）。理解这些挑战和优化策略对于生产环境的三阶段训练非常重要——没有"万能"的配置，需要根据具体场景（领域、数据、资源、目标）选择合适的方法和参数，持续迭代优化。
>
> **📝 精简总结**：常见问题包括SFT后不遵循指令（数据格式/模板不匹配/学习率小/epoch少，检查格式+apply_chat_template验证+增学习率+增epoch+确认只算回答损失）、SFT后重复用户指令（指令部分也算损失/未mask，只算回答部分SFTTrainer自动或自定义label=-100）、SFT过拟合（数据小/epoch多/学习率大/r大，增数据+减epoch1-2+降学习率+减r8-16+dropout+早停）、灾难性遗忘（学习率大/epoch多/数据偏移/全参数，降学习率epoch+混合10-30%通用数据+LoRA+知识蒸馏+选择性只注意力+评估通用）、DPO对齐效果不明显（β小/偏好差异小/学习率小/epoch少，增β0.1→0.3+确保chosen明显优于rejected+增学习率+增epoch+增数据）、DPO后语言质量下降对齐税（β大/学习率大/epoch多/数据单一，减β0.3→0.1+降学习率+减epoch1个+多样化数据+混合通用+监控困惑度）、RLHF训练不稳定PPO崩溃（学习率大/clip不当/KL不当/RM过拟合，降学习率+调clip0.1-0.2+调KL+检查RM+用DPO替代）、奖励黑客（RM漏洞/策略过度优化/KL太弱，增强RM+定期更新+增KL+DPO隐式奖励+人工审核高奖励）、CPT后能力下降（学习率大/数据差/训练多/遗忘，降学习率1e-5~2e-5+提升数据质量+减步数+混合通用+LoRA）、显存OOM（模型大/batch大/无4bit/无梯度检查点，QLoRA4bit+减batch+gradient_checkpointing+paged_adamw_8bit+减序列+梯度累积）、数据质量差效果差（AI生成低质/未清洗/噪声/重复，强模型生成+人工抽检+清洗去重过滤格式+LLM-as-Judge评估+过滤低分）、评估不可靠（验证集小/主观/未对比基线，增验证集50-200+LLM-as-Judge+训练前评估基线+多次评估取平均）、三阶段顺序错误（跳过SFT直接RLHF/预训练直接部署，必须先SFT再对齐+预训练需SFT+对齐才成对话助手+不要跳步）、用指令微调模型做SFT冲突（已Instruct再SFT格式冲突/过拟合，用Instruct模型只做领域SFT+减学习率epoch+确认模板一致）；性能优化采用训练效率（LoRA/QLoRA/4bit/梯度检查点/混合精度/FlashAttention2，显存降75%+）、数据效率（高质量/增强/主动学习/进化指令，数据需求降50-70%）、对齐效率（DPO替代RLHF/RLAIF/在线学习/少样本对齐，成本降80%+）、推理效率（合并LoRA/vLLM/TGI/连续批处理/PagedAttention/量化，5-20倍）、分布式训练（DeepSpeed/FSDP/多卡/张量并行/流水线并行）、超参数优化（学习率扫描/β扫描/早停/验证集/搜索）、模型选择（合适大小/领域预训练/指令微调）、缓存优化（KV/前缀/数据/Embedding，20-50%）、评估效率（自动化/LLM-as-Judge/小规模验证集/早停/监控，成本降80%+）、成本优化（LoRA替代全参数/DPO替代RLHF/AI生成替代人工/开源替代API，总成本降90%+）、持续学习（增量训练/在线学习/用户反馈闭环/数据飞轮）、混合精度（BF16推荐/FP8推理/梯度FP32/优化器8bit）；安全风险包括对齐不足（增无害数据/红队/安全过滤/监控）、过度对齐对齐税（平衡有用无害/多样化数据/减β/混合通用/评估拒绝率）、数据投毒（审核/验证/检测/抽检/清洗）、隐私泄露（脱敏/过滤/差分隐私/记忆检测/合规）、偏见放大（检测/去偏/公平评估/多样化/审核）、奖励黑客（增强RM/更新/增KL/DPO/人工审核）、模型滥用（限制/访问控制/速率/检测/审核/认证）、知识产权（版权审查/合理使用/标注/查重）、供应链安全（审查/版本锁定/扫描/监控/应急/签名）、合规风险（评估/治理/同意/可解释/审计/本地化/认证）；生产踩坑集中在跳过SFT直接DPO对齐极差（必须先SFT再DPO/SFT 1万-5万条足够/用Instruct模型可跳过SFT/验证SFT效果/参考模型用SFT模型）、偏好数据差异太小DPO无效（强模型vs弱模型/质量过滤差异大/增数据几千几万/增β0.1-0.3/奖励模型排序取最好最差/人工审核差异率>90%）、全参数SFT灾难性遗忘（LoRA优先/全参数降学习率1e-5~2e-5减epoch1-2/混合10-30%通用数据/知识蒸馏KL约束/选择性只注意力/定期评估通用任务/持续学习EWC+回放/过拟合后用LoRA重训或通用数据恢复）；核心挑战是数据质量（PT中等/SFT高/偏好最高，构建方法+清洗+质量控制）、训练稳定性（学习率/warmup/梯度裁剪/BF16/Pre-LN/LoRA/检查点/监控，PPO不稳定用DPO）、效果保持（过拟合防控早停+减epoch+降学习率+减r+dropout+数据增强，灾难性遗忘防控LoRA+混合通用+知识蒸馏+选择性微调+持续评估），成本优化（LoRA/DPO/AI生成/开源模型/批量/量化/自动化评估，总成本降90%+）。

---

## 五、拓展

### 5.1 训练范式演进

| 范式 | 说明 | 代表 | 特点 |
|------|------|------|------|
| **预训练 + 微调** | 预训练后全参数微调特定任务 | BERT 微调 | 简单，但每个任务一个模型 |
| **预训练 + 提示学习** | 预训练后用 Prompt 零样本/少样本 | GPT-3 | 不需要微调，但效果依赖 Prompt |
| **预训练 + 指令微调** | 预训练后用指令数据微调，提升零样本 | FLAN、T0 | 一个模型处理多个任务 |
| **预训练 + SFT + RLHF** | 三阶段，对齐人类价值观 | InstructGPT、ChatGPT | 对话助手标准范式 |
| **预训练 + SFT + DPO** | 用 DPO 替代 RLHF，简化对齐 | Zephyr、Tulu | 更简单稳定，效果相当 |
| **预训练 + RLAIF** | 用 AI 反馈替代人类反馈 | Constitutional AI | 降低标注成本，可扩展 |
| **预训练 + 自我对齐** | 模型自我生成偏好数据，自我对齐 | Self-Align、Self-Instruct | 完全自动化，不需要人类 |
| **预训练 + 在线学习** | 部署后持续从用户反馈学习 | 在线 RLHF | 持续改进，适应新场景 |
| **预训练 + 多任务联合** | 多个任务联合训练，共享表示 | FLAN、T0、Flan-T5 | 提升泛化能力 |
| **预训练 + 领域 CPT + SFT + DPO** | 四阶段，领域专用模型 | 领域 LLM | 领域知识注入 + 对齐 |
| **预训练 + 思维链微调** | 用 CoT 数据微调，提升推理 | Chain-of-Thought | 提升推理能力 |
| **预训练 + 工具使用微调** | 用工具调用数据微调，提升工具使用 | Toolformer、Gorilla | 提升 Agent 能力 |

### 5.2 对齐方法对比

| 方法 | 原理 | 数据需求 | 计算成本 | 训练稳定性 | 对齐效果 | 代表 |
|------|------|---------|---------|-----------|---------|------|
| **RLHF (PPO)** | 奖励模型 + PPO 强化学习 | 偏好对 + 奖励数据 | 极高 | 低（不稳定） | 高 | InstructGPT、ChatGPT |
| **DPO** | 直接偏好优化，对比损失 | 偏好对 | 中（接近 SFT） | 高（稳定） | 高 | Zephyr、Tulu |
| **IPO** | Identity Policy Optimization，二次损失 | 偏好对 | 中 | 极高 | 中高 | IPO |
| **KTO** | 单样本标签，不需要成对 | 单样本好坏标签 | 中 | 高 | 中 | KTO |
| **ORPO** | 合并 SFT + 偏好，不需要参考模型 | 偏好对 | 低 | 高 | 高 | ORPO |
| **SimPO** | 去掉参考模型，长度归一化 | 偏好对 | 低 | 高 | 高 | SimPO |
| **RLAIF** | AI 生成偏好数据 + RLHF | AI 生成偏好 | 中高 | 中 | 高 | Constitutional AI |
| **Constitutional AI** | 基于原则的自我批评和修订 | 原则 + 自我批评 | 中高 | 中 | 高 | Claude |
| **安全微调** | 用安全数据微调，拒绝有害请求 | 安全数据 | 低 | 高 | 中（安全但可能过度保守） | 安全模型 |
| **红队微调** | 用红队攻击数据微调，提升安全性 | 红队数据 | 低 | 高 | 中高 | 安全增强 |

### 5.3 各阶段成本估算

| 阶段 | 模型规模 | 硬件 | 时间 | 成本（美元） | 备注 |
|------|---------|------|------|------------|------|
| **预训练** | 7B | 256×A100 80GB | 1-2 周 | 50万-200万 | 万亿 Token，完整预训练 |
| **预训练** | 70B | 1024×A100 80GB | 1-2 月 | 500万-2000万 | 完整预训练 |
| **CPT** | 7B | 8×A100 | 1-3 天 | 5000-2万 | 领域数据，LoRA 可更低 |
| **SFT（全参数）** | 7B | 8×A100 | 1-2 天 | 3000-1万 | 数万条指令数据 |
| **SFT（LoRA）** | 7B | 1×RTX 4090 24GB | 2-6 小时 | 50-500 | QLoRA 4bit，单卡可训 |
| **SFT（LoRA）** | 70B | 1×A100 40GB | 6-12 小时 | 200-1000 | QLoRA 4bit，单卡可训 |
| **RLHF（PPO）** | 7B | 8×A100 | 1-2 天 | 5000-2万 | 奖励模型 + PPO，4个模型 |
| **DPO** | 7B | 1×RTX 4090 | 1-3 小时 | 50-300 | QLoRA，接近 SFT 成本 |
| **DPO** | 70B | 1×A100 40GB | 3-6 小时 | 100-500 | QLoRA 4bit |
| **评估** | 任意 | 1×GPU/API | 数小时 | 100-1000 | 基准测试 + LLM-as-Judge |
| **部署（推理）** | 7B | 1×A10G 24GB | 持续 | 500-2000/月 | vLLM，4bit 量化可更低 |
| **部署（推理）** | 70B | 2×A100 80GB | 持续 | 3000-8000/月 | vLLM，量化可降低 |

**总成本估算（7B 模型定制，LoRA + DPO）**：
- 数据构建（AI 生成）：$100-500
- SFT（LoRA，单卡）：$50-500
- DPO（LoRA，单卡）：$50-300
- 评估：$100-1000
- **总计：$300-2300**（对比全参数 + RLHF 的 $1万-5万，成本降低 90%+）

### 5.4 学习资源

- [InstructGPT 论文](https://arxiv.org/abs/2203.02155) 🔗 — Training language models to follow instructions
- [RLHF 论文](https://arxiv.org/abs/2203.02155) 🔗 — InstructGPT 包含 RLHF
- [DPO 论文](https://arxiv.org/abs/2305.18290) 🔗 — Direct Preference Optimization
- [Training language models to follow instructions](https://arxiv.org/abs/2203.02155) 🔗
- [Constitutional AI 论文](https://arxiv.org/abs/2212.08073) 🔗 — AI 反馈对齐
- [Llama 2 论文](https://arxiv.org/abs/2307.09288) 🔗 — 开源 LLM 训练细节
- [Scaling Law 论文](https://arxiv.org/abs/2001.08361) 🔗 — Scaling Laws for Neural Language Models
- [TRL 库文档](https://huggingface.co/docs/trl) 🔗 — SFT/DPO/PPO 训练
- [Axolotl GitHub](https://github.com/axolotl-ai-cloud/axolotl) 🔗 — 开箱即用训练框架
- [LLaMA-Factory GitHub](https://github.com/hiyouga/LLaMA-Factory) 🔗 — WebUI 训练框架
- [[LLM大模型入门概念]] — LLM 基础
- [[Transformer架构核心]] — Transformer 架构
- [[SFT监督微调实战]] — SFT 详细实战
- [[DPO直接偏好优化]] — DPO 详细原理和实战
- [[LoRA-QLoRA参数高效微调]] — 参数高效微调
- [[模型量化-GPTQ-AWQ-GGUF]] — 模型量化
- [[主流开源模型架构对比]] — 主流模型对比
- [[Agent安全与护栏设计]] — AI 安全和对齐
- [[生成式AI原理与应用知识点系统梳理_优化版]] — 生成式 AI 系统梳理
- [[主流大模型与AI工具知识点系统梳理_优化版]] — 大模型与工具系统梳理

---

> 💡 **深度讲解**：三阶段训练范式的未来发展方向是"更简单、更高效、更自动化、更安全"。更简单——DPO 已经大大简化了对齐流程（绕过奖励模型和 PPO），未来可能出现更简单的对齐方法。ORPO（Odds Ratio Preference Optimization）将 SFT 和偏好优化合并为一个阶段，不需要参考模型，进一步简化；SimPO（Simple Preference Optimization）去掉参考模型，用长度归一化，更简单。未来可能出现"端到端对齐"——从基础模型直接进行偏好优化，不需要单独的 SFT 阶段。更高效——数据高效对齐是重要方向。主动学习（Active Learning）选择模型不确定的样本进行标注，用更少的数据达到更好的效果；AI 反馈（RLAIF，Constitutional AI）用 AI 模型生成偏好数据，替代昂贵的人类标注，大幅降低成本；少样本对齐（Few-shot alignment）用少量偏好数据就能达到好的对齐效果；在线学习（Online Learning）部署后持续从用户反馈学习，形成数据飞轮。这些方法使得对齐的成本持续降低，小团队也能做高质量对齐。更自动化——全自动训练流水线是未来趋势。从数据收集（AI 生成）、数据清洗（自动过滤+LLM-as-Judge 评估）、训练（自动超参数搜索）、评估（自动化基准+LLM-as-Judge）、部署（CI/CD）、监控（持续质量监控）全流程自动化。自我对齐（Self-Align）是更激进的方向——模型自己生成指令、自己生成回答、自己生成偏好数据、自己对齐，完全不需要人类干预。虽然目前自我对齐的效果还不如人类监督，但未来可能成为重要方向。更安全——安全对齐是三阶段训练的重要发展方向。传统的 RLHF/DPO 主要对齐"有用性"，对"无害性"和"诚实性"的对齐不够充分。未来的对齐方法需要更全面地对齐人类价值观——有用性、无害性、诚实性、公平性、透明度、可控性等。Constitutional AI（基于原则的对齐）用一组宪法原则指导模型的自我批评和修订，是安全对齐的重要方法。红队测试（Red Teaming）和持续安全监控也是安全对齐的重要环节。多目标对齐（Multi-objective alignment）同时优化多个目标（有用性、无害性、诚实性），在多个目标之间找到帕累托最优。三阶段范式的成本分布正在发生变化——预训练成本仍然极高（但开源模型使得大多数团队不需要自己预训练），SFT 和对齐的成本正在快速降低（LoRA/QLoRA 降低硬件门槛，DPO 降低对齐复杂度，AI 生成降低数据成本，自动化评估降低评估成本）。现在一个 7B 模型的完整定制（SFT + DPO + 评估）成本可以低到 300-2300 美元（用 LoRA + 单卡 + AI 生成数据），这在几年前是不可想象的。这意味着 LLM 定制正在民主化——个人和小团队也能定制高质量的领域模型，AI 应用的开发门槛持续降低。对于从业者来说，理解三阶段范式的原理和实践是必备技能——不需要自己做预训练（用开源模型），但需要掌握 SFT 和 DPO 的数据构建、训练配置、评估方法，能够根据场景选择合适的方法和参数，持续迭代优化模型。建议的学习路径：① 理解三阶段范式的原理（PT/SFT/RLHF/DPO 的目标、数据、方法、成本）；② 实践 SFT（用 LoRA + 开源模型 + AI 生成数据，跑通完整流程）；③ 实践 DPO（用偏好数据 + DPO 训练，对比 SFT 效果）；④ 学习评估方法（自动基准 + LLM-as-Judge + 人工评估，对比不同阶段的效果）；⑤ 实践领域定制（选择一个领域，构建领域数据，SFT + DPO，评估效果）；⑥ 关注前沿进展（新的对齐方法、更高效的训练技术、安全对齐）。三阶段范式是 LLM 技术的核心方法论，理解它对于理解现代 AI 应用的开发和优化至关重要。
>
> **📝 精简总结**：训练范式演进——预训练+微调（BERT微调，每任务一模型）、预训练+提示学习（GPT-3零样本少样本，依赖Prompt）、预训练+指令微调（FLAN/T0，一模型多任务）、预训练+SFT+RLHF（InstructGPT/ChatGPT，对话助手标准范式）、预训练+SFT+DPO（Zephyr/Tulu，更简单稳定效果相当）、预训练+RLAIF（Constitutional AI，AI反馈降成本可扩展）、预训练+自我对齐（Self-Align/Self-Instruct，完全自动化无人类）、预训练+在线学习（在线RLHF，持续改进适应新场景）、预训练+多任务联合（FLAN/T0/Flan-T5，提升泛化）、预训练+领域CPT+SFT+DPO（四阶段领域专用模型）、预训练+思维链微调（CoT提升推理）、预训练+工具使用微调（Toolformer/Gorilla提升Agent）；对齐方法对比——RLHF-PPO（奖励模型+PPO/偏好对+奖励数据/极高成本/低不稳定/高效果/InstructGPT）、DPO（直接偏好优化对比损失/偏好对/中接近SFT/高稳定/高效果/Zephyr）、IPO（二次损失/偏好对/中/极高稳定/中高效果）、KTO（单样本标签不需要成对/单样本好坏/中/高稳定/中效果）、ORPO（合并SFT+偏好无参考模型/偏好对/低成本/高稳定/高效果）、SimPO（去参考模型长度归一化/偏好对/低成本/高稳定/高效果）、RLAIF（AI生成偏好+RLHF/AI生成偏好/中高/中稳定/高效果/Constitutional AI）、Constitutional AI（原则+自我批评/原则+批评/中高/中稳定/高效果/Claude）、安全微调（安全数据拒绝有害/安全数据/低成本/高稳定/中效果可能过度保守）、红队微调（红队攻击数据/红队数据/低成本/高稳定/中高效果）；成本估算——预训练7B（256×A100/1-2周/50万-200万美元）、预训练70B（1024×A100/1-2月/500万-2000万）、CPT 7B（8×A100/1-3天/5000-2万）、SFT全参数7B（8×A100/1-2天/3000-1万）、SFT LoRA 7B（1×4090/2-6小时/50-500）、SFT LoRA 70B（1×A100/6-12小时/200-1000）、RLHF PPO 7B（8×A100/1-2天/5000-2万）、DPO 7B（1×4090/1-3小时/50-300）、DPO 70B（1×A100/3-6小时/100-500）、评估（1×GPU/API/数小时/100-1000）、部署推理7B（1×A10G/500-2000/月）、部署推理70B（2×A100/3000-8000/月）；7B模型LoRA+DPO完整定制总成本300-2300美元（数据100-500+SFT50-500+DPO50-300+评估100-1000），对比全参数+RLHF的1万-5万降90%+；学习资源包括 InstructGPT/RLHF/DPO/Constitutional AI/Llama2/Scaling Law论文、TRL/Axolotl/LLaMA-Factory文档和本知识库大量相关专题；发展方向是更简单（ORPO/SimPO合并阶段去参考模型/端到端对齐）、更高效（主动学习/RLAIF/少样本对齐/在线学习数据飞轮，成本持续降低）、更自动化（全自动流水线数据收集→清洗→训练→评估→部署→监控/自我对齐完全自动化）、更安全（全面对齐有用无害诚实公平透明可控/Constitutional AI/红队测试/多目标对齐帕累托最优）；成本分布变化——预训练仍极高但开源模型免做，SFT和对齐成本快速降低（LoRA/DPO/AI生成/自动化评估），7B定制可低至数百美元，LLM定制民主化个人小团队可做；学习路径是理解原理→实践SFT→实践DPO→学习评估→领域定制实践→关注前沿。

---

## 🔗 关联笔记

- [[LLM大模型入门概念]] — LLM 基础概念
- [[Transformer架构核心]] — Transformer 架构（模型基础）
- [[SFT监督微调实战]] — SFT 详细实战指南
- [[DPO直接偏好优化]] — DPO 详细原理和实战
- [[LoRA-QLoRA参数高效微调]] — 参数高效微调（三阶段训练常用）
- [[模型量化-GPTQ-AWQ-GGUF]] — 模型量化（推理优化）
- [[主流开源模型架构对比]] — 主流开源模型对比
- [[Agent安全与护栏设计]] — AI 安全和对齐
- [[Embedding模型选型]] — Embedding 模型
- [[Tokenization与词表]] — Tokenization
- [[注意力机制详解]] — 注意力机制
- [[位置编码进阶-RoPE-ALiBi]] — 位置编码
- [[生成式AI原理与应用知识点系统梳理_优化版]] — 生成式 AI 系统梳理
- [[主流大模型与AI工具知识点系统梳理_优化版]] — 大模型与工具系统梳理
- [[AI Agent核心概念与架构知识点系统梳理_优化版]] — Agent 核心概念

## 📖 前置知识

- [[LLM大模型入门概念]]
- [[Transformer架构核心]]
- [[注意力机制详解]]
- [[Tokenization与词表]]

## 🏷️ 相关标签

`#AI应用` `#AI工程化` `#LLM` `#效率工具`

---

[[Home|🏠 返回首页]] · [[MOC-AI与效率工具|📚 返回分类]]
