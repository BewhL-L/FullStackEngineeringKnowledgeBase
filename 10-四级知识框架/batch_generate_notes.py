"""
批量生成三级原子笔记骨架
从各板块 MOC 文件中解析三级笔记标题和四级子知识点，生成骨架文件
"""
import re
import os
from pathlib import Path

BASE_DIR = r"C:\Users\23981\Desktop\AI文档\DouBao Document\全栈工程MarkDown文档\10-四级知识框架"

# 板块配置：目录名 -> (标签前缀, 板块名)
SECTIONS = {
    "01-Python全栈": ("#Python全栈/", "Python全栈"),
    "02-Java全栈": ("#Java全栈/", "Java全栈"),
    "03-Vue3TS前端": ("#Vue3TS/", "Vue3TS前端"),
    "04-AIGC与Obsidian": ("#AIGC应用/", "AIGC与Obsidian"),
    "05-CS基础": ("#CS基础/", "CS基础"),
    "06-AI工程化": ("#AI工程/", "AI工程化"),
    "07-DevOps": ("#DevOps/", "DevOps"),
    "08-知识管理方法论": ("#知识管理/", "知识管理方法论"),
    "09-效率工具链": ("#效率工具/", "效率工具链"),
    "10-项目实战": ("#项目实战/", "项目实战"),
}

def parse_moc(filepath):
    """解析 MOC 文件，提取三级笔记列表"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    notes = []
    # 匹配三级笔记块：### [[标题|显示名]] 或 ### [[标题]]
    # 然后捕获到下一个 ### 或 ## 之间的内容
    pattern = r'###\s+\[\[([^\]|]+)(?:\|([^\]]+))?\]\](.*?)(?=\n###\s+\[\[|\n##\s|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for note_id, display_name, body in matches:
        title = display_name.strip() if display_name else note_id.strip()
        filename = note_id.strip()
        
        # 提取一句话说明（> 后面的内容）
        desc_match = re.search(r'>\s*(.+?)(?:\n|$)', body)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # 提取四级子知识点
        sub_points = []
        # 匹配 "- **四级子知识点**：" 后面的缩进列表
        sub_section = re.search(r'\*\*四级子知识点\*\*[：:]\s*\n((?:\s+[-*]\s+.+\n?)+)', body)
        if sub_section:
            sub_lines = sub_section.group(1)
            for line in sub_lines.strip().split('\n'):
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    sub_points.append(line[2:].strip())
        
        # 提取标签
        tag_match = re.search(r'\*\*标签\*\*[：:]\s*`([^`]+)`', body)
        tag = tag_match.group(1).strip() if tag_match else ""
        
        # 提取前置依赖
        dep_match = re.search(r'\*\*前置依赖\*\*[：:]\s*(.+?)(?:\n|$)', body)
        dependency = dep_match.group(1).strip() if dep_match else ""
        
        # 提取跨板块关联
        cross_match = re.search(r'\*\*跨板块关联\*\*[：:]\s*(.+?)(?:\n|$)', body)
        cross_ref = cross_match.group(1).strip() if cross_match else ""
        
        notes.append({
            "filename": filename,
            "title": title,
            "description": description,
            "sub_points": sub_points,
            "tag": tag,
            "dependency": dependency,
            "cross_ref": cross_ref,
        })
    
    return notes

def generate_note_content(note, tag_prefix, section_name, moc_filename):
    """生成单篇笔记的内容"""
    title = note["title"]
    description = note["description"]
    sub_points = note["sub_points"]
    tag = note["tag"] or tag_prefix.rstrip('/')
    dependency = note["dependency"]
    cross_ref = note["cross_ref"]
    
    # 生成四级子知识点章节
    sub_sections = []
    for i, point in enumerate(sub_points, 1):
        sub_sections.append(f"""### {i}. {point}

> 待补充：{point}的核心概念、原理、实践要点。

**核心要点**：
- 

**代码示例**：
```
// 待补充
```

**常见问题**：
- 

---
""")
    
    sub_content = "\n".join(sub_sections) if sub_sections else "> 待补充四级子知识点\n"
    
    # 生成子知识点清单表格
    table_rows = []
    for i, point in enumerate(sub_points, 1):
        anchor = f"#{i}-{point.replace(' ', '-')}"
        table_rows.append(f"| {i} | {point} | [{i}](#{i}-{point.replace(' ', '-')}) | ⬜ 待写 | 🔴 未开始 |")
    
    table_content = "\n".join(table_rows) if table_rows else "| 1 | 待补充 | - | ⬜ | 🔴 |"
    
    content = f"""---
title: {title}
tags: [{tag}, 原子笔记, 待完善]
created: 2026-08-13
updated: 2026-08-13
status: 🔴 未开始
source: 
---

# {title}

> {description}

**所属板块**：[[{moc_filename}|{section_name}]]
**标签**：`{tag}`
**学习状态**：🔴 未开始

---

## 📋 四级子知识点清单

| 序号 | 子知识点 | 章节锚点 | 独立笔记 | 状态 |
|------|----------|----------|----------|------|
{table_content}

---

## 📖 核心内容

{sub_content}

---

## 🔗 关联知识

### 前置依赖
- {dependency if dependency else '无特殊前置要求'}

### 后续延伸
- 

### 跨板块关联
- {cross_ref if cross_ref else '待补充'}

### 相关笔记
- 

---

## 💡 实践要点

- 

---

## ❓ 常见问题

1. **Q**: 
   **A**: 

---

## 📚 参考资料

- 

---

## 📝 学习日志

| 日期 | 学习内容 | 状态 |
|------|----------|------|
| 2026-08-13 | 创建笔记骨架 | 🔴 未开始 |

---

[[{moc_filename}|← 返回{section_name} MOC]] | [[10-四级知识框架/00-总控/四级框架总索引|🗺️ 返回四级框架总索引]] | [[Home|🏠 返回首页]]
"""
    return content

def main():
    total_created = 0
    total_skipped = 0
    
    for section_dir, (tag_prefix, section_name) in SECTIONS.items():
        section_path = os.path.join(BASE_DIR, section_dir)
        moc_files = list(Path(section_path).glob("MOC-*-四级展开.md"))
        
        if not moc_files:
            print(f"⚠️  {section_dir}: 未找到 MOC 文件")
            continue
        
        moc_file = moc_files[0]
        moc_filename = moc_file.name
        print(f"\n📂 处理 {section_dir} ({moc_filename})")
        
        notes = parse_moc(str(moc_file))
        print(f"   解析到 {len(notes)} 篇三级笔记")
        
        for note in notes:
            # 跳过枢纽笔记和MOC本身
            if "枢纽" in note["filename"] or "MOC" in note["filename"]:
                total_skipped += 1
                continue
            
            filepath = os.path.join(section_path, note["filename"] + ".md")
            
            # 如果文件已存在，跳过
            if os.path.exists(filepath):
                total_skipped += 1
                print(f"   ⏭️  已存在: {note['filename']}.md")
                continue
            
            content = generate_note_content(note, tag_prefix, section_name, moc_filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            total_created += 1
            print(f"   ✅ 创建: {note['filename']}.md ({len(note['sub_points'])} 个四级知识点)")
    
    print(f"\n{'='*50}")
    print(f"🎉 完成！创建 {total_created} 篇，跳过 {total_skipped} 篇")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
