# -*- coding: utf-8 -*-
"""安全扩展引擎：只插入新内容，绝不删除/改写/重排原文。
用于在 Markdown 知识点文档中：
  1) 顶部插入「优化版说明」（若缺失）
  2) 为每个知识点标题（### / #### / ## N.N 子节）在其内容末尾（下一个同级或更高级标题前）插入「🔍 知识点深度解析」块（若该标题区域尚不存在）
  3) 顶级 ## 小节之间补 --- 分隔线（若缺失）
  4) 文末补 📝 精简总结（若缺失）
原始每一行均被原样保留，仅做插入。
"""
import re
import sys

NOTE_TEXT = "> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。"


def is_any_heading(line):
    m = re.match(r'^(#{1,6})\s', line)
    return m


def heading_level(line):
    m = re.match(r'^(#{1,6})\s', line)
    return len(m.group(1)) if m else 0


def is_kp(line):
    """知识点标题：### / #### 或 ## N.N 形式的子节"""
    m = re.match(r'^(#{3,4})\s', line)
    if m:
        return True, len(m.group(1))
    # ## 数字.数字 子节（如 ## 6.1 模型路由）
    if re.match(r'^##\s+\d+\.\d+\s', line):
        return True, 2
    return False, 0


def is_major_section(line):
    """顶级 ## 小节（非 ## N.N 子节，非 📝 精简总结以外的也算顶级）"""
    if not line.startswith('## '):
        return False
    if re.match(r'^##\s+\d+\.\d+\s', line):
        return False
    return True


def make_block(content):
    """content: (作用, 原理, [要点...]) 返回块行列表（不含首尾空行）"""
    if content is None:
        return None
    role, principle, points = content
    block = ["> 🔍 **知识点深度解析**", ">"]
    block.append("> **作用**：" + role)
    block.append(">")
    block.append("> **原理**：" + principle)
    block.append(">")
    pts = "  ".join("①" if i == 0 else "②" if i == 1 else "③" if i == 2 else "④" if i == 3 else "⑤" if i == 4 else "⑥" for i in range(len(points)))
    # 用法要点格式：① x  ② y  ③ z
    point_str = "  ".join(
        ("① " if i == 0 else "② " if i == 1 else "③ " if i == 2 else "④ " if i == 3 else "⑤ " if i == 4 else "⑥ ")
        + p for i, p in enumerate(points)
    )
    block.append("> **用法要点**：" + point_str)
    return block


def expand(path, content_map, add_top_note, add_summary, summary_text):
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')

    has_note = any('优化版说明' in l for l in lines)
    has_summary = any('📝 精简总结' in l for l in lines)

    # ---- 解析 frontmatter ----
    fm_end = 0
    if lines and lines[0].strip() == '---':
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                fm_end = i + 1
                break

    result = []
    i = 0
    n = len(lines)
    if fm_end > 0:
        result.extend(lines[:fm_end])
        i = fm_end
        # 跳过 frontmatter 后的空行
        while i < n and lines[i].strip() == '':
            result.append(lines[i])
            i += 1
    else:
        # 无 frontmatter：可能有顶部标题，仍跳过前导空行
        while i < n and lines[i].strip() == '':
            result.append(lines[i])
            i += 1

    # ---- 主循环：遍历并插入深度解析块 ----
    pending = None  # {'level':int, 'title':str, 'start':int}
    note_inserted = False

    def flush_pending(end_idx, target):
        nonlocal pending
        if pending is None:
            return
        region = lines[pending['start']:end_idx]
        if any('知识点深度解析' in r for r in region):
            pending = None
            return
        block = make_block(content_map.get(pending['title']))
        if block:
            target.append('')
            target.extend(block)
            target.append('')
        pending = None

    while i < n:
        line = lines[i]
        kp, lvl = is_kp(line)
        if kp:
            # 新知识点标题：先尝试 flush 上一个 pending
            flush_pending(i, result)
            pending = {'level': lvl, 'title': line.strip(), 'start': i + 1}
            result.append(line)
            i += 1
            continue
        # 一般标题（含 ## 顶级）：若比 pending 级别高/相等则 flush
        hl = heading_level(line)
        if hl > 0 and pending is not None and hl <= pending['level']:
            flush_pending(i, result)
        result.append(line)
        # 在 H1 标题之后插入顶部「优化版说明」
        if (add_top_note and not has_note and not note_inserted
                and line.startswith('# ') and not line.startswith('## ')):
            result.append('')
            result.extend(NOTE_TEXT.split('\n'))
            result.append('')
            note_inserted = True
        i += 1
    # 文件末尾 flush
    flush_pending(n, result)

    # ---- 顶级 ## 之间补 --- 分隔 ----
    out = []
    major_count = 0
    for idx, line in enumerate(result):
        if is_major_section(line):
            major_count += 1
            if major_count > 1:
                # 前一行若不是 --- 则插入
                prev = out[-1] if out else ''
                if prev.strip() != '---':
                    out.append('')
                    out.append('---')
        out.append(line)
    result = out

    # ---- 文末补 📝 精简总结 ----
    if add_summary and not has_summary:
        summary_block = ['## 📝 精简总结', '']
        summary_block.extend(summary_text.split('\n'))
        if not summary_block[-1].strip() == '':
            summary_block.append('')
        # 若文末已有 优化版说明（底部），插在其前；否则追加
        note_idx = None
        for k in range(len(result) - 1, -1, -1):
            if result[k].strip().startswith('> **优化版说明') or '优化版说明' in result[k]:
                note_idx = k
                break
        if note_idx is not None:
            # 在 note 前插入，并保证分隔
            insert = ['', '---', ''] + summary_block
            result = result[:note_idx] + insert + result[note_idx:]
        else:
            # 追加到末尾
            if result and result[-1].strip() != '':
                result.append('')
            result.append('---')
            result.append('')
            result.extend(summary_block)

    # 写回
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result))

    # 统计
    new_lines = len(result)
    added = 0
    for l in result:
        if l.startswith('> 🔍 **知识点深度解析**'):
            added += 1
    return new_lines, added


if __name__ == '__main__':
    # 直接运行仅用于测试
    print("engine loaded")
