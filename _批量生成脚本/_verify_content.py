# -*- coding: utf-8 -*-
import os

base = os.path.dirname(os.path.abspath(__file__))

pairs = [
    (r'01-前端开发\_backup\CSS 进阶知识点系统梳理_优化版.md', r'01-前端开发\CSS 进阶知识点系统梳理_优化版.md'),
    (r'01-前端开发\_backup\Element Plus 知识点系统梳理_优化版.md', r'01-前端开发\Element Plus 知识点系统梳理_优化版.md'),
    (r'08-Python全栈\_backup\Python语言基础与进阶知识点系统梳理_优化版.md', r'08-Python全栈\Python语言基础与进阶知识点系统梳理_优化版.md'),
    (r'08-Python全栈\_backup\Python部署运维知识点系统梳理_优化版.md', r'08-Python全栈\Python部署运维知识点系统梳理_优化版.md'),
]

for backup_path, expanded_path in pairs:
    with open(os.path.join(base, backup_path), encoding='utf-8') as f:
        orig_lines = f.read().split('\n')
    with open(os.path.join(base, expanded_path), encoding='utf-8') as f:
        expanded = f.read()
    
    # Only check non-blockquote, non-empty original lines (actual content)
    content_lines = [l for l in orig_lines if l.strip() and not l.strip().startswith('>')]
    missing = [l for l in content_lines if l not in expanded]
    
    if not missing:
        print(f'  OK  All original content preserved: {os.path.basename(expanded_path)} ({len(content_lines)} content lines checked)')
    else:
        print(f'  WARNING  {len(missing)} original content lines not found: {os.path.basename(expanded_path)}')
        for l in missing[:10]:
            print(f'    -> {l[:100]}')
