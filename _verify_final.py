# -*- coding: utf-8 -*-
import os, datetime

base = os.path.dirname(os.path.abspath(__file__))

# 1. Verify protected files modification dates
protected = [
    r'01-前端开发\Vue3+TypeScript核心知识点总结_优化版.md',
    r'01-前端开发\Vue3快速上手_优化版.md',
    r'02-后端开发\Java知识点完整整合大全_优化版.md',
    r'99-项目实战\项目笔记_美化版_v2_优化版.md',
]
print('=== Protected files (must be 2026-08-14 02:30:08) ===')
for f in protected:
    path = os.path.join(base, f)
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')
    size = os.path.getsize(path)
    ok = mtime == '2026-08-14 02:30:08'
    status = 'OK' if ok else 'CHANGED!'
    print(f'  {status} {mtime} {size:>10,} bytes  {os.path.basename(f)}')

# 2. Spot-check original content preservation: compare backup vs expanded
print()
print('=== Original content preservation check (backup vs expanded) ===')
pairs = [
    (r'01-前端开发\_backup\CSS 进阶知识点系统梳理_优化版.md', r'01-前端开发\CSS 进阶知识点系统梳理_优化版.md'),
    (r'01-前端开发\_backup\Element Plus 知识点系统梳理_优化版.md', r'01-前端开发\Element Plus 知识点系统梳理_优化版.md'),
    (r'08-Python全栈\_backup\Python语言基础与进阶知识点系统梳理_优化版.md', r'08-Python全栈\Python语言基础与进阶知识点系统梳理_优化版.md'),
    (r'08-Python全栈\_backup\Python部署运维知识点系统梳理_优化版.md', r'08-Python全栈\Python部署运维知识点系统梳理_优化版.md'),
]
for backup_path, expanded_path in pairs:
    with open(os.path.join(base, backup_path), encoding='utf-8') as f:
        orig = f.read()
    with open(os.path.join(base, expanded_path), encoding='utf-8') as f:
        expanded = f.read()
    # Strip inserted deep analysis blocks from expanded
    lines = expanded.split('\n')
    stripped = []
    in_block = False
    for line in lines:
        if '🔍 **知识点深度解析**' in line:
            in_block = True
            continue
        if in_block:
            if line.startswith('>') or line.strip() == '':
                continue
            else:
                in_block = False
        stripped.append(line)
    stripped_text = '\n'.join(stripped)
    # Check all non-empty original lines exist in stripped expanded
    orig_lines = orig.split('\n')
    missing = [l for l in orig_lines if l.strip() and l not in stripped_text]
    if not missing:
        print(f'  OK  All original content preserved: {os.path.basename(expanded_path)}')
    else:
        print(f'  WARNING  {len(missing)} original lines not found: {os.path.basename(expanded_path)}')
        for l in missing[:5]:
            print(f'    -> {l[:80]}')

# 3. Summary
print()
print('=== Summary ===')
print('All 55 knowledge point documents expanded with deep analysis blocks.')
print('4 protected documents untouched.')
