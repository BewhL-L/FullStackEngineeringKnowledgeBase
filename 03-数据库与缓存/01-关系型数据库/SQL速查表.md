---
title: SQL速查表
tags: [速查表, SQL, MySQL, 数据库, 后端]
category: 数据库
created: 2026-08-27
updated: 2026-08-27
difficulty: ⭐
status: ✅ 内容已完善
priority: 一般
pre: []
aliases: [SQL速查表]
---

# SQL速查表

> **文档说明**：SQL常用语法速查表，覆盖查询、过滤、排序、聚合、连接、子查询、窗口函数、数据操作。
>
> **适用人群**：所有使用数据库的开发者
>
> **使用方式**：快速查阅SQL语法

---

## 一、基础查询

```sql
-- 查询所有列
SELECT * FROM users;

-- 查询指定列
SELECT id, name, email FROM users;

-- 别名
SELECT name AS 用户名, email AS 邮箱 FROM users;

-- 去重
SELECT DISTINCT city FROM users;

-- 限制行数
SELECT * FROM users LIMIT 10;           -- 前10条
SELECT * FROM users LIMIT 10, 20;       -- 跳过10条，取20条
SELECT * FROM users LIMIT 20 OFFSET 10; -- 同上
```

---

## 二、WHERE过滤

```sql
-- 比较
SELECT * FROM users WHERE age > 18;
SELECT * FROM users WHERE age >= 18 AND age <= 30;
SELECT * FROM users WHERE age BETWEEN 18 AND 30;

-- 模糊查询
SELECT * FROM users WHERE name LIKE '张%';   -- 以张开头
SELECT * FROM users WHERE name LIKE '%明%';  -- 包含明
SELECT * FROM users WHERE name LIKE '张_';   -- 张开头共2字

-- IN / NOT IN
SELECT * FROM users WHERE city IN ('北京', '上海', '广州');
SELECT * FROM users WHERE id NOT IN (1, 2, 3);

-- NULL判断
SELECT * FROM users WHERE email IS NULL;
SELECT * FROM users WHERE email IS NOT NULL;

-- 逻辑运算
SELECT * FROM users WHERE age > 18 OR (city = '北京' AND status = 1);
```

---

## 三、排序与分组

```sql
-- 排序
SELECT * FROM users ORDER BY age ASC;       -- 升序（默认）
SELECT * FROM users ORDER BY age DESC;      -- 降序
SELECT * FROM users ORDER BY age DESC, id ASC;  -- 多字段排序

-- 聚合函数
SELECT COUNT(*) FROM users;                  -- 总行数
SELECT COUNT(email) FROM users;              -- 非NULL列数
SELECT SUM(amount) FROM orders;              -- 求和
SELECT AVG(age) FROM users;                  -- 平均值
SELECT MAX(age), MIN(age) FROM users;        -- 最大/最小

-- GROUP BY分组
SELECT city, COUNT(*) AS cnt FROM users GROUP BY city;
SELECT city, AVG(age) AS avg_age FROM users GROUP BY city;

-- HAVING过滤分组结果
SELECT city, COUNT(*) AS cnt FROM users
GROUP BY city HAVING cnt > 100;
```

---

## 四、连接查询

```sql
-- 内连接（只返回匹配的行）
SELECT u.name, o.order_no
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- 左连接（左表全部，右表匹配）
SELECT u.name, o.order_no
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- 右连接
SELECT u.name, o.order_no
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- 全连接（MySQL不支持，用UNION模拟）
SELECT * FROM users u LEFT JOIN orders o ON u.id = o.user_id
UNION
SELECT * FROM users u RIGHT JOIN orders o ON u.id = o.user_id;

-- 自连接
SELECT e.name AS 员工, m.name AS 经理
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;

-- 多表连接
SELECT u.name, o.order_no, p.product_name
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id;
```

---

## 五、子查询

```sql
-- 标量子查询
SELECT name, (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS order_count
FROM users u;

-- IN子查询
SELECT * FROM users WHERE id IN (
    SELECT user_id FROM orders WHERE amount > 1000
);

-- EXISTS子查询
SELECT * FROM users u WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id AND o.amount > 1000
);

-- FROM子查询（派生表）
SELECT avg_age FROM (
    SELECT city, AVG(age) AS avg_age FROM users GROUP BY city
) AS city_avg WHERE avg_age > 25;
```

---

## 六、窗口函数（MySQL 8.0+）

```sql
-- ROW_NUMBER: 行号（不重复）
SELECT name, salary, dept,
       ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn
FROM employees;

-- RANK: 排名（并列跳号：1,1,3）
SELECT name, salary, RANK() OVER (ORDER BY salary DESC) AS rnk
FROM employees;

-- DENSE_RANK: 密集排名（并列不跳号：1,1,2）
SELECT name, salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
FROM employees;

-- 聚合窗口函数
SELECT name, salary, dept,
       AVG(salary) OVER (PARTITION BY dept) AS dept_avg,
       SUM(salary) OVER (ORDER BY id) AS running_total
FROM employees;

-- LAG/LEAD: 前后行
SELECT name, salary,
       LAG(salary) OVER (ORDER BY salary) AS prev_salary,
       LEAD(salary) OVER (ORDER BY salary) AS next_salary
FROM employees;

-- NTILE: 分桶
SELECT name, salary, NTILE(4) OVER (ORDER BY salary DESC) AS quartile
FROM employees;
```

---

## 七、数据操作

```sql
-- 插入
INSERT INTO users (name, email, age) VALUES ('张三', 'zhang@test.com', 25);
INSERT INTO users (name, email) VALUES ('张三', 'zhang@test.com'), ('李四', 'li@test.com');
INSERT INTO users_backup SELECT * FROM users WHERE status = 0;

-- 更新
UPDATE users SET age = 26 WHERE id = 1;
UPDATE users SET status = 1 WHERE age > 18;
-- 多表更新
UPDATE users u JOIN orders o ON u.id = o.user_id SET u.vip = 1 WHERE o.amount > 1000;

-- 删除
DELETE FROM users WHERE id = 1;
DELETE FROM users WHERE status = 0 AND created_at < '2024-01-01';
-- 清空表（更快，不可回滚）
TRUNCATE TABLE users;
```

---

## 八、表操作

```sql
-- 创建表
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    age INT DEFAULT 0,
    status TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_status_created (status, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 修改表
ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email;
ALTER TABLE users MODIFY COLUMN name VARCHAR(100) NOT NULL;
ALTER TABLE users DROP COLUMN phone;
ALTER TABLE users ADD INDEX idx_email (email);
ALTER TABLE users DROP INDEX idx_email;
ALTER TABLE users RENAME TO user_info;

-- 删除表
DROP TABLE users;
DROP TABLE IF EXISTS users;
```

---

## 九、常用函数

```sql
-- 字符串
CONCAT(a, b)           -- 拼接
SUBSTRING(str, 1, 3)   -- 截取
LENGTH(str)            -- 字节长度
CHAR_LENGTH(str)       -- 字符长度
UPPER(str) / LOWER(str)
TRIM(str)              -- 去空格
REPLACE(str, 'a', 'b') -- 替换
LEFT(str, n) / RIGHT(str, n)

-- 日期
NOW()                  -- 当前日期时间
CURDATE()              -- 当前日期
YEAR(date) / MONTH(date) / DAY(date)
DATE_FORMAT(date, '%Y-%m-%d')
DATEDIFF(d1, d2)       -- 天数差
DATE_ADD(date, INTERVAL 1 DAY)
TIMESTAMPDIFF(DAY, d1, d2)

-- 数值
ROUND(x, 2)            -- 四舍五入
CEIL(x) / FLOOR(x)
ABS(x)
MOD(a, b)              -- 取余

-- 条件
IF(cond, a, b)         -- 三元
IFNULL(x, default)     -- NULL替换
COALESCE(a, b, c)      -- 第一个非NULL
CASE WHEN cond THEN a WHEN cond2 THEN b ELSE c END
```

---

## 十、高级技巧

```sql
-- 分页优化（深分页）
-- 慢：SELECT * FROM orders ORDER BY id LIMIT 100000, 20;
-- 快：延迟关联
SELECT o.* FROM orders o
INNER JOIN (SELECT id FROM orders ORDER BY id LIMIT 100000, 20) t ON o.id = t.id;

-- 游标分页
SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20;

-- 批量插入优化
INSERT INTO t VALUES (...), (...), (...);  -- 批量比单条快10倍+

-- 覆盖索引（Extra: Using index）
SELECT id, name FROM users WHERE name = '张三';  -- id和name都在索引中

-- 强制索引
SELECT * FROM users USE INDEX (idx_name) WHERE name = '张三';
SELECT * FROM users FORCE INDEX (idx_name) WHERE name = '张三';

-- 查看执行计划
EXPLAIN SELECT * FROM users WHERE age > 18;
EXPLAIN ANALYZE SELECT * FROM users WHERE age > 18;  -- MySQL 8.0实际执行
```

---

## 关联文档

- [[MySQL 知识点系统梳理_优化版]] — MySQL完整知识
- [[关系型数据库索引原理]] — 索引优化
- [[MySQL问题排查手册]] — 问题排查
- [[分库分表实战指南]] — 分库分表

---

> 💡 SQL优化核心：避免全表扫描（type=ALL）、使用覆盖索引、避免索引失效、深分页用游标/延迟关联。写完SQL一定EXPLAIN看执行计划。



## 补充：概述

SQL（Structured Query Language，结构化查询语言）是关系型数据库的标准查询语言，是后端开发者和数据分析师的必备技能。SQL 分为四大类：**DDL**（数据定义语言，CREATE/ALTER/DROP）、**DML**（数据操作语言，SELECT/INSERT/UPDATE/DELETE）、**DCL**（数据控制语言，GRANT/REVOKE）、**TCL**（事务控制语言，COMMIT/ROLLBACK/SAVEPOINT）。

| SQL 类别 | 命令 | 作用 |
|---------|------|------|
| **DDL** | CREATE, ALTER, DROP, TRUNCATE, RENAME | 定义数据库结构（表、索引、视图） |
| **DML** | SELECT, INSERT, UPDATE, DELETE | 操作表中的数据 |
| **DCL** | GRANT, REVOKE | 管理用户权限 |
| **TCL** | COMMIT, ROLLBACK, SAVEPOINT | 事务控制 |

**SQL 执行顺序**（重要！理解执行顺序是写对 SQL 的关键）：
```python
FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT
```

这意味着：
- `WHERE` 中不能用 `SELECT` 中定义的别名（因为 WHERE 先执行）
- `HAVING` 用于过滤分组后的结果（聚合后），`WHERE` 用于过滤行（聚合前）
- `ORDER BY` 可以用 `SELECT` 别名（因为 ORDER BY 后执行）

---

## 补充：进阶与最佳实践

### 1. 高级查询技巧

```sql
-- 窗口函数（分析函数）—— 不减少行数，每行附加聚合结果
SELECT user_id, amount,
       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY amount DESC) AS rn,
       RANK() OVER (PARTITION BY user_id ORDER BY amount DESC) AS rk,
       DENSE_RANK() OVER (PARTITION BY user_id ORDER BY amount DESC) AS dr,
       SUM(amount) OVER (PARTITION BY user_id) AS user_total,
       AVG(amount) OVER (PARTITION BY user_id) AS user_avg,
       LAG(amount, 1) OVER (ORDER BY created_at) AS prev_amount,
       LEAD(amount, 1) OVER (ORDER BY created_at) AS next_amount,
       FIRST_VALUE(amount) OVER (PARTITION BY user_id ORDER BY created_at) AS first_amount,
       NTILE(4) OVER (ORDER BY amount DESC) AS quartile  -- 分位数
FROM orders;

-- CTE（公用表表达式）—— 提高可读性，支持递归
WITH user_stats AS (
    SELECT user_id, COUNT(*) AS order_count, SUM(amount) AS total
    FROM orders
    WHERE created_at >= '2026-01-01'
    GROUP BY user_id
),
top_users AS (
    SELECT user_id, total
    FROM user_stats
    ORDER BY total DESC
    LIMIT 10
)
SELECT u.name, tu.total, us.order_count
FROM top_users tu
JOIN users u ON u.id = tu.user_id
JOIN user_stats us ON us.user_id = tu.user_id;

-- 递归 CTE（查询树形结构）
WITH RECURSIVE org_tree AS (
    SELECT id, name, manager_id, 1 AS level
    FROM employees WHERE manager_id IS NULL  -- 根节点
    UNION ALL
    SELECT e.id, e.name, e.manager_id, ot.level + 1
    FROM employees e
    JOIN org_tree ot ON e.manager_id = ot.id
)
SELECT * FROM org_tree ORDER BY level, id;

-- PIVOT 行转列（用 CASE WHEN 实现）
SELECT user_id,
       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_count,
       SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending_count,
       SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_count
FROM orders
GROUP BY user_id;

--  EXISTS vs IN（EXISTS 通常更快，尤其子查询结果大时）
SELECT * FROM users u
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id AND o.amount > 1000);

-- 自连接（查询同表内的关联关系）
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

### 2. 性能优化要点

| 优化点 | 说明 | 示例 |
|--------|------|------|
| **避免 SELECT *** | 只查需要的列，减少 IO 和网络传输 | `SELECT id, name FROM users` |
| **合理使用索引** | WHERE/JOIN/ORDER BY 字段建索引，复合索引遵循最左前缀 | `CREATE INDEX idx_orders_user ON orders(user_id, created_at)` |
| **避免函数操作索引列** | 函数会导致索引失效 | ❌ `WHERE DATE(created_at) = '2026-01-01'` ✅ `WHERE created_at >= '2026-01-01' AND created_at < '2026-01-02'` |
| **避免 LIKE 前导通配符** | `%keyword` 无法用索引 | ❌ `LIKE '%abc%'` ✅ `LIKE 'abc%'`（可用索引）或全文搜索 |
| **LIMIT 分页优化** | 深分页 OFFSET 慢，用游标分页 | ❌ `LIMIT 100000, 20` ✅ `WHERE id > last_id LIMIT 20` |
| **JOIN 顺序** | 小表驱动大表，确保 JOIN 字段有索引 | `FROM small_table s JOIN big_table b ON s.id = b.s_id` |
| **避免隐式类型转换** | 类型不匹配导致索引失效 | ❌ `WHERE phone = 13800138000`（phone 是字符串）✅ `WHERE phone = '13800138000'` |
| **批量操作** | 批量 INSERT/UPDATE 比逐条快 10-100 倍 | `INSERT INTO t VALUES (1),(2),(3)` |
| **用 EXISTS 替代 IN** | 子查询结果集大时 EXISTS 更快 | `WHERE EXISTS (SELECT 1 FROM ...)` |
| **避免 ORDER BY RAND()** | 全表排序，性能极差 | 用 `WHERE id >= RAND() * max_id LIMIT 1` 替代 |

### 3. EXPLAIN 执行计划解读

```sql
-- 查看执行计划
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 123 ORDER BY created_at DESC LIMIT 20;

-- 关键节点解读：
-- Seq Scan        : 全表扫描（需要加索引）
-- Index Scan      : 索引扫描（好）
-- Index Only Scan : 覆盖索引（最好，不需要回表）
-- Bitmap Heap Scan: 位图扫描（多个索引组合）
-- Nested Loop     : 嵌套循环连接（小表驱动）
-- Hash Join       : 哈希连接（大表连接）
-- Merge Join      : 合并连接（已排序数据）
-- Sort            : 排序操作（注意是否用了索引避免排序）
-- Aggregate       : 聚合操作
-- Limit           : 限制返回行数
```

### 4. 事务与隔离级别

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 性能 |
|---------|------|-----------|------|------|
| **Read Uncommitted** | ❌ 可能 | ❌ 可能 | ❌ 可能 | 最高 |
| **Read Committed**（PG/MySQL默认） | ✅ 避免 | ❌ 可能 | ❌ 可能 | 高 |
| **Repeatable Read**（MySQL默认） | ✅ 避免 | ✅ 避免 | ❌ 可能（MySQL InnoDB 用间隙锁避免） | 中 |
| **Serializable** | ✅ 避免 | ✅ 避免 | ✅ 避免 | 最低 |

```sql
-- 设置隔离级别
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- 事务模板
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
-- 检查业务规则
IF balance < 0 THEN ROLLBACK; ELSE COMMIT; END IF;
```
