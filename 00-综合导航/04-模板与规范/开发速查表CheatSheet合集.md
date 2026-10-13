---
title: 开发速查表CheatSheet合集
tags: [学习路径]
category: 学习路径
created: 2026-08-27
updated: 2026-08-27
difficulty: ⭐
status: ✅ 内容已完善
priority: 一般
pre: []
aliases: [开发速查表CheatSheet合集]
---

# 开发速查表 CheatSheet 合集

> **文档说明**：常用命令和语法速查，遇到忘记的语法直接查这里。

---

## 一、Git 速查

```bash
# 基础
git init                          # 初始化仓库
git clone <url>                   # 克隆仓库
git status                        # 查看状态
git add .                         # 添加所有文件
git commit -m "message"           # 提交
git push origin main              # 推送到远程
git pull origin main              # 拉取远程

# 分支
git branch                        # 查看分支
git branch dev                    # 创建分支
git checkout dev                  # 切换分支
git switch dev                    # 切换分支（新命令）
git merge dev                     # 合并分支
git branch -d dev                 # 删除分支

# 撤销
git reset --soft HEAD~1           # 撤销最后一次提交（保留修改）
git reset --hard HEAD~1           # 撤销最后一次提交（丢弃修改）
git checkout -- file.txt          # 撤销文件修改
git stash                         # 暂存修改
git stash pop                     # 恢复暂存

# 查看历史
git log --oneline --graph         # 图形化提交历史
git diff                          # 查看未暂存的修改
git reflog                        # 查看所有操作记录（救命用）

# 远程
git remote -v                     # 查看远程仓库
git remote add origin <url>       # 添加远程
git fetch                         # 拉取远程信息不合并
```

---

## 二、Linux 命令速查

```bash
# 文件操作
ls -la                            # 列出所有文件详细信息
cd /path                          # 切换目录
pwd                               # 当前路径
mkdir -p a/b/c                    # 创建多级目录
cp -r src dst                     # 复制目录
mv old new                        # 移动/重命名
rm -rf dir                        # 强制删除（危险！）
find / -name "*.log"              # 查找文件

# 查看文件
cat file.txt                      # 查看全部
less file.txt                     # 分页查看（q退出，/搜索）
head -n 20 file.txt               # 前20行
tail -f app.log                   # 实时跟踪日志
tail -n 100 file.txt              # 最后100行
grep "keyword" file.txt           # 搜索
grep -rn "TODO" src/              # 递归搜索

# 进程
ps aux                            # 所有进程
ps aux | grep java                # 查找Java进程
top                               # 实时监控
kill 1234                         # 终止进程
kill -9 1234                      # 强制杀死

# 系统
free -h                           # 内存
df -h                             # 磁盘
du -sh *                          # 当前目录各文件大小
uptime                            # 运行时间和负载
uname -a                          # 系统信息

# 网络
ip addr                           # IP地址
ping google.com                   # 连通性
curl -I https://example.com       # HTTP请求
ss -tlnp                          # 监听端口
lsof -i :8080                     # 占用8080的进程
wget https://example.com/file.zip # 下载

# 权限
chmod 755 file.sh                 # 修改权限
chmod +x file.sh                  # 添加执行权限
chown user:group file             # 修改所有者
sudo command                      # 管理员执行

# 软件包（Ubuntu）
apt update                        # 更新源
apt install nginx                 # 安装
apt remove nginx                  # 卸载
systemctl start nginx             # 启动服务
systemctl enable nginx            # 开机自启
systemctl status nginx            # 查看状态
journalctl -u nginx -f            # 查看服务日志
```

---

## 三、SQL 速查

```sql
-- 查询
SELECT * FROM users;
SELECT id, name FROM users WHERE age > 18;
SELECT * FROM users ORDER BY age DESC LIMIT 10;
SELECT COUNT(*) FROM users GROUP BY status;

-- 条件
WHERE age BETWEEN 18 AND 30
WHERE name IN ('张三', '李四')
WHERE email LIKE '%@gmail.com'
WHERE age IS NOT NULL

-- 关联
SELECT u.name, o.amount
FROM users u
JOIN orders o ON u.id = o.user_id;

-- 增删改
INSERT INTO users (name, age) VALUES ('张三', 25);
UPDATE users SET age = 26 WHERE id = 1;
DELETE FROM users WHERE id = 1;  -- 永远加WHERE！

-- 聚合
COUNT(*) / SUM(amount) / AVG(age) / MAX(age) / MIN(age)
GROUP BY ... HAVING COUNT(*) > 1

-- 事务
START TRANSACTION;
-- SQL语句
COMMIT;  -- 或 ROLLBACK;

-- 表操作
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE users ADD COLUMN email VARCHAR(100);
DROP TABLE users;

-- 索引
CREATE INDEX idx_name ON users(name);
EXPLAIN SELECT * FROM users WHERE name = '张三';
```

---

## 四、CSS 速查

```css
/* Flexbox */
.container {
    display: flex;
    justify-content: center;      /* 主轴：center/flex-start/space-between/space-around */
    align-items: center;          /* 交叉轴 */
    flex-direction: row;          /* row/column */
    flex-wrap: wrap;              /* 换行 */
    gap: 16px;                    /* 间距 */
}
.item { flex: 1; }                /* 等分 */

/* Grid */
.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);  /* 3列等分 */
    gap: 20px;
}
.item-large { grid-column: span 2; }       /* 占2列 */

/* 居中 */
.center {
    display: flex;
    justify-content: center;
    align-items: center;
}

/* 常用属性 */
color: #333;
font-size: 16px;
font-weight: 600;
line-height: 1.6;
text-align: center;

background: linear-gradient(135deg, #667eea, #764ba2);
border-radius: 12px;
box-shadow: 0 4px 12px rgba(0,0,0,0.1);

/* 响应式 */
@media (max-width: 768px) {
    .container { padding: 16px; }
}

/* 动画 */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.animate { animation: fadeIn 0.5s ease-out; }
```

---

## 五、TypeScript 速查

```typescript
// 基础类型
let name: string = "张三";
let age: number = 25;
let isActive: boolean = true;
let list: number[] = [1, 2, 3];
let tuple: [string, number] = ["张三", 25];

// 接口
interface User {
    id: number;
    name: string;
    age?: number;           // 可选
    readonly email: string; // 只读
}

// 类型别名
type Status = "active" | "inactive" | "pending";

// 泛型
function identity<T>(arg: T): T { return arg; }
interface ApiResponse<T> {
    code: number;
    data: T;
}

// 联合类型
let value: string | number;

// 类型守卫
function isString(x: any): x is string {
    return typeof x === "string";
}

// 工具类型
Partial<User>       // 所有属性可选
Required<User>      // 所有属性必选
Pick<User, "id"|"name">  // 选取部分
Omit<User, "email">      // 排除部分
Record<string, number>   // 键值对类型

// 可选链和空值合并
let city = user?.address?.city ?? "未知";

// 枚举
enum Direction { Up, Down, Left, Right }

// as断言
let input = document.getElementById("input") as HTMLInputElement;
```

---

## 六、JavaScript 数组方法速查

```javascript
const arr = [1, 2, 3, 4, 5];

arr.map(x => x * 2)          // [2,4,6,8,10] 映射
arr.filter(x => x > 2)       // [3,4,5] 过滤
arr.reduce((a,b) => a+b, 0)  // 15 归约
arr.find(x => x > 2)         // 3 找第一个
arr.findIndex(x => x > 2)    // 2
arr.some(x => x > 4)         // true 任一满足
arr.every(x => x > 0)        // true 全部满足
arr.forEach(x => console.log(x))  // 遍历
arr.includes(3)              // true
arr.sort((a,b) => a-b)       // 排序
arr.reverse()                // 反转
[...arr, 6]                  // 展开
```

---

## 关联笔记
[[Linux系统管理与常用命令]] · [[MySQL基础与SQL实战]] · [[JavaScript-ES6核心语法]] · [[CSS3布局与样式基础]]

> 💡 **提示**：速查表用来快速回忆，深入学习请参考对应专题笔记。
