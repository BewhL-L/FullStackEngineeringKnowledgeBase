"""
RAG 分层指标（确定性、可复算，不依赖模型）
- 检索层：Hit@K、MRR、Context Precision(平均精确率 AP)、Context Recall
- 生成层：答案关键词覆盖率（关键事实是否出现在答案中）

相关性判定：片段来源命中文档名，或片段文本命中关键事实词，即视为相关。
若用例未提供 expected_document_names / must_contain_keywords，则检索指标无法判定（返回 None）。
"""
from typing import List, Dict, Optional


def expected_docs(case: Dict) -> List[str]:
    return [d.strip() for d in case.get("expected_document_names", []) if d and d.strip()]


def expected_keywords(case: Dict) -> List[str]:
    return [k.strip() for k in case.get("must_contain_keywords", []) if k and k.strip()]


def is_relevant(chunk: Dict, case: Dict) -> Optional[bool]:
    docs = expected_docs(case)
    kws = expected_keywords(case)
    if not docs and not kws:
        return None
    name = chunk.get("document_name", "") or ""
    text = chunk.get("text", "") or ""
    doc_hit = any(d in name for d in docs)
    kw_hit = any(k in text for k in kws)
    return doc_hit or kw_hit


def relevance_flags(retrieved: List[Dict], case: Dict) -> List[int]:
    flags = []
    for c in retrieved:
        r = is_relevant(c, case)
        flags.append(1 if r is True else 0)
    return flags


def hit_at_k(retrieved: List[Dict], case: Dict, k: int = None) -> float:
    """gold chunk 是否进入 Top-K（1/0）"""
    flags = relevance_flags(retrieved, case)
    window = flags[:k] if k else flags
    return 1.0 if any(window) else 0.0


def mrr(retrieved: List[Dict], case: Dict) -> float:
    """第一个相关片段排名的倒数"""
    flags = relevance_flags(retrieved, case)
    for i, f in enumerate(flags, 1):
        if f:
            return 1.0 / i
    return 0.0


def average_precision(retrieved: List[Dict], case: Dict) -> Optional[float]:
    """Context Precision：考虑排名的平均精确率"""
    flags = relevance_flags(retrieved, case)
    total_rel = sum(flags)
    if total_rel == 0:
        # 无法判定相关性时（全 None→0）区分：若没有任何期望信息则 None
        if not expected_docs(case) and not expected_keywords(case):
            return None
        return 0.0
    hits = 0
    score = 0.0
    for i, f in enumerate(flags, 1):
        if f:
            hits += 1
            score += hits / i
    return score / total_rel


def context_recall(retrieved: List[Dict], case: Dict) -> Optional[float]:
    """期望的文档/关键事实有多少被检索覆盖"""
    docs = expected_docs(case)
    kws = expected_keywords(case)
    total = len(docs) + len(kws)
    if total == 0:
        return None
    names = [c.get("document_name", "") or "" for c in retrieved]
    joined_text = "\n".join(c.get("text", "") or "" for c in retrieved)
    hit = 0
    for d in docs:
        if any(d in n for n in names):
            hit += 1
    for k in kws:
        if k in joined_text:
            hit += 1
    return hit / total


def answer_keyword_coverage(answer: str, case: Dict) -> Optional[float]:
    """答案中关键事实词的覆盖率"""
    kws = expected_keywords(case)
    if not kws:
        return None
    hit = sum(1 for k in kws if k in answer)
    return hit / len(kws)
