# -*- coding: utf-8 -*-
import os, re
from collections import Counter
sys_path = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, sys_path)
from _content_data import CONTENT

BASE = sys_path
FILES = [
 "Python Web开发框架知识点系统梳理_优化版.md",
 "Python中间件与异步任务知识点系统梳理_优化版.md",
 "Python全栈前端集成知识点系统梳理_优化版.md",
 "Python安全防护知识点系统梳理_优化版.md",
 "Python性能优化知识点系统梳理_优化版.md",
 "Python接口设计与文档知识点系统梳理_优化版.md",
 "Python数据库与缓存知识点系统梳理_优化版.md",
 "Python测试工程知识点系统梳理_优化版.md",
 "Python语言基础与进阶知识点系统梳理_优化版.md",
 "Python部署运维知识点系统梳理_优化版.md",
]

NOTE = "> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。"
CIRCLED = ["①","②","③","④","⑤","⑥","⑦","⑧","⑨"]

def is_heading(line, level=None):
    if not line.startswith("#"):
        return None
    m = re.match(r"^(#{1,6})\s", line)
    if not m:
        return None
    lvl = len(m.group(1))
    if level is not None and lvl != level:
        return None
    return lvl

def toggle_fence(state, line):
    s = line.strip()
    if s.startswith("```") or s.startswith("~~~"):
        return not state
    return state

def insert_note(lines):
    for l in lines[:40]:
        if "优化版说明" in l:
            return lines, False
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return lines[:i+1] + ["", NOTE, ""] + lines[i+1:], True
        return [NOTE, ""] + lines, True
    return [NOTE, ""] + lines, True

def add_hr_between_h2(lines):
    out = []
    in_code = False
    first_h2 = True
    for line in lines:
        in_code = toggle_fence(in_code, line)
        if not in_code and is_heading(line, 2):
            if first_h2:
                first_h2 = False
                out.append(line)
                continue
            j = len(out) - 1
            while j >= 0 and out[j].strip() == "":
                j -= 1
            if j >= 0 and out[j].strip() == "---":
                out.append(line)
            else:
                out.append("")
                out.append("---")
                out.append("")
                out.append(line)
        else:
            out.append(line)
    return out

def count_h3(lines):
    c = 0
    in_code = False
    for line in lines:
        in_code = toggle_fence(in_code, line)
        if not in_code and is_heading(line, 3):
            c += 1
    return c

def add_analysis(lines, basename):
    content_map = CONTENT.get(basename, {})
    out = []
    inserted = 0
    i = 0
    n = len(lines)
    in_code = False
    while i < n:
        line = lines[i]
        in_code = toggle_fence(in_code, line)
        h = is_heading(line, 3) if not in_code else None
        if h == 3:
            heading_text = line[4:].strip()
            j = i + 1
            inc = in_code
            ins_point = n
            while j < n:
                inc = toggle_fence(inc, lines[j])
                if not inc and is_heading(lines[j], 3):
                    ins_point = j
                    break
                if not inc and is_heading(lines[j], 2):
                    ins_point = j
                    break
                if not inc and is_heading(lines[j], 1):
                    ins_point = j
                    break
                j += 1
            has_block = any("🔍 **知识点深度解析**" in lines[k] for k in range(i+1, ins_point))
            out.append(line)
            if not has_block:
                entry = content_map.get(heading_text)
                if entry:
                    role, principle, points = entry
                    pt = " ".join(CIRCLED[t] + " " + p for t, p in enumerate(points))
                    block = [
                        "> 🔍 **知识点深度解析**",
                        ">",
                        "> **作用**：" + role,
                        ">",
                        "> **原理**：" + principle,
                        ">",
                        "> **用法要点**：" + pt,
                    ]
                    out.append("")
                    out.extend(block)
                    out.append("")
                    inserted += 1
                else:
                    print("  [WARN] missing content for H3:", heading_text, "in", basename)
            i += 1
        else:
            out.append(line)
            i += 1
    return out, inserted

def verify_no_deletion(orig_lines, new_lines):
    oc = Counter(orig_lines)
    nc = Counter(new_lines)
    for line, cnt in oc.items():
        if nc.get(line, 0) < cnt:
            return False, line
    return True, None

def main():
    for f in FILES:
        path = os.path.join(BASE, f)
        with open(path, encoding="utf-8-sig") as fh:
            data = fh.read()
        has_bom = data.startswith("\ufeff")
        if has_bom:
            data = data.lstrip("\ufeff")
        orig = data.split("\n")
        orig_count = len(orig)
        lines, added_note = insert_note(orig)
        lines = add_hr_between_h2(lines)
        lines, inserted = add_analysis(lines, f)
        text = "\n".join(lines)
        with open(path, "w", encoding="utf-8-sig" if has_bom else "utf-8") as fh:
            fh.write(text)
        h3 = count_h3(orig)
        ok, bad = verify_no_deletion(orig, lines)
        status = "OK(0删除)" if ok else "FAIL(疑似删除): " + repr(bad[:40])
        print(f"{f}\n  原行数={orig_count} 新行数={len(lines)} 知识点(###)={h3} 新增解析块={inserted} 说明新增={added_note} 校验={status}")

if __name__ == "__main__":
    main()
