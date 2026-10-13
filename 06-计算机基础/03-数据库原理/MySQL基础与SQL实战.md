---
title: MySQL基础与SQL实战
category: 计算机基础
tags: [MySQL, SQL, 数据库, 关系型数据库, CRUD, 事务, JOIN, 索引, 计算机基础]
priority: P1
status: completed
created: 2026-09-11
updated: 2026-09-11
version: 2.0
author: BewhY_L
pre: ["[[数据结构与算法知识点系统梳理_优化版]]", "[[计算机网络-TCP-IP]]"]
description: 从安装、数据类型、DDL/DML/DQL、多表查询、索引、事务到Python集成与性能优化的MySQL实战全景手册
---

# MySQL 基础与 SQL 实战：从入门到生产优化

> **文档定位**：这是一份面向后端工程师与全栈开发者的 MySQL 系统性实战手册。它不教你"背命令"，而是带你理解"为什么这样写、为什么会慢、为什么会错"。全文按"概念 → 原理 → 代码 → 场景 → 坑点"五要素组织，每一章末尾都有深度讲解、精简总结与梯度练习题。
>
> **学习目标**：读完本文，你应当能够独立设计一张电商订单表、写出带索引的高效查询、用 EXPLAIN 定位慢 SQL、在 Python 中安全地操作数据库，并能自信应对"为什么索引失效""MVCC 怎么解决幻读"这类面试题。
>
> **前置知识**：[[数据结构与算法知识点系统梳理_优化版]]（理解 B+ 树、链表、复杂度分析）、[[计算机网络-TCP-IP]]（理解连接、网络延迟）。

---

## 一、MySQL 概述、安装与学习路径

### 1.1 什么是 MySQL

**概念解释**：MySQL 是当前世界上最流行的开源**关系型数据库管理系统（RDBMS）**，由瑞典 MySQL AB 公司开发，目前归属 Oracle。它用"表（Table）"组织结构化数据，用"SQL"语言操作数据，用"InnoDB"存储引擎保证事务安全。

**生活化比喻**：如果把数据比作一座图书馆的藏书，那么 MySQL 就是图书馆的"总管理系统"——书架就是表，每本书就是一行记录，每本书的分类号、作者、出版社就是列；SQL 就是你告诉管理员"我要什么书"的查询语言；索引就是图书馆门口的检索卡片柜。

**核心价值**：它把"如何高效存、如何并发读、如何保证不丢"这三件原本需要程序员手写的复杂工作，封装成一个稳定、可移植、生态成熟的底座。几乎所有 Web 后端（Java、Python、Go、Node.js）最终都要落一张表到 MySQL 上。

### 1.2 为什么选择 MySQL 而不是其他

```mermaid
graph TB
    A[存储系统选型] --> B[关系型 RDBMS]
    A --> C[NoSQL]
    A --> D[NewSQL]
    B --> B1[MySQL]
    B --> B2[PostgreSQL]
    B --> B3[Oracle]
    C --> C1[Redis 内存KV]
    C --> C2[MongoDB 文档]
    D --> D1[TiDB]
    B1 --> B1a[开源免费/生态最大/互联网标配]
    B2 --> B2a[语法严谨/复杂SQL强]
    B3 --> B3a[商业授权贵]
    style B1 fill:#00758f,color:#fff
```

| 维度 | MySQL | PostgreSQL | Oracle |
|------|-------|-----------|--------|
| 授权成本 | 社区版免费 | 免费 | 昂贵商业授权 |
| 互联网生态 | 极广（阿里/字节/美团主用） | 增长中 | 传统金融/大型企业 |
| 运维成熟度 | 主从、分库分表、中间件极多 | 中等 | 极高 |
| 复杂查询能力 | 够用 | 更强 | 最强 |
| 学习曲线 | 平缓 | 略陡 | 陡峭 |

> ✅ **最佳实践**：互联网业务（电商、社交、内容）优先 MySQL；以复杂报表、GIS、全文检索为主的分析型需求可评估 PostgreSQL。本文专注 MySQL。

### 1.3 在三大平台安装 MySQL

**Windows（推荐 MySQL Installer）**：

```bash
# 通过 Chocolatey 安装（管理员 PowerShell）
choco install mysql -y
# 安装后服务名通常为 MySQL80，启动服务
net start MySQL80
# 登录（首次会提示输入临时密码，在安装日志中）
mysql -u root -p
```

**macOS（推荐 Homebrew）**：

```bash
# 安装
brew install mysql
# 启动服务
brew services start mysql
# 无密码登录后修改密码
mysql -u root
```

**Linux（Ubuntu/Debian 推荐 apt）**：

```bash
# 安装服务端与客户端
sudo apt update
sudo apt install -y mysql-server
# 启动并设置开机自启
sudo systemctl start mysql
sudo systemctl enable mysql
# 安全初始化（移除匿名用户、禁远程 root、删测试库）
sudo mysql_secure_installation
# 登录
sudo mysql -u root
```

**Docker 一键起（最推荐用于学习与测试）**：

```bash
# 起一个 MySQL 8 容器，端口 3306，root 密码 root123
docker run -d --name mysql-lab \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=root123 \
  -e MYSQL_DATABASE=lab \
  mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 进入容器执行 SQL
docker exec -it mysql-lab mysql -uroot -proot123 lab
```

```bash
# 验证安装版本与字符集
SELECT VERSION();
-- 预期输出：8.0.36（或其他 8.0.x）
SHOW VARIABLES LIKE 'character_set%';
-- 预期输出：character_set_server = utf8mb4
```

### 1.4 SQL 语言的五大分类

| 分类 | 全称 | 代表命令 | 作用 |
|------|------|----------|------|
| **DDL** | 数据定义语言 | CREATE / ALTER / DROP / TRUNCATE | 改"表结构" |
| **DML** | 数据操作语言 | INSERT / UPDATE / DELETE | 改"数据行" |
| **DQL** | 数据查询语言 | SELECT（含 WHERE/GROUP/ORDER） | 查"数据" |
| **DCL** | 数据控制语言 | GRANT / REVOKE | 管"权限" |
| **TCL** | 事务控制语言 | COMMIT / ROLLBACK / SAVEPOINT | 管"事务" |

> 🎯 **面试高频**：请区分 DDL 与 DML，并说出 TRUNCATE 属于哪一类。答案：TRUNCATE 是 DDL（它直接删除数据文件重建表，不走逐行删除，无法回滚），这是新手高频错点。

### 1.5 学习路线图

```mermaid
graph LR
    A[安装+SQL基础] --> B[DDL建表]
    B --> C[DML增删改]
    C --> D[DQL单表查询]
    D --> E[多表JOIN+子查询]
    E --> F[索引+EXPLAIN]
    F --> G[事务+隔离级别]
    G --> H[Python集成+性能优化]
    H --> I[分库分表/高可用进阶]
    style A fill:#43e97b,color:#333
    style F fill:#feca57,color:#333
    style H fill:#667eea,color:#fff
```

> 💡 **本章深度讲解**：MySQL 学习的最大误区是"把它当成 SQL 语法词典来背"。真正拉开差距的是你对三个底层机制的理解：B+ 树索引（决定查询快不快）、MVCC 与锁（决定并发安不安全）、查询优化器（决定 SQL 实际怎么执行）。安装只是起点，本文后续章节会逐层揭开这三个机制。本章也是全书地基——理解 RDBMS 的"表/行/列/约束"心智模型，后面所有章节都建立在其上。
>
> 📝 **本章精简总结**：① MySQL 是开源关系型数据库，InnoDB 为默认引擎；② 用 Docker 起环境最快，字符集必须 utf8mb4；③ SQL 分 DDL/DML/DQL/DCL/TCL 五类；④ 学习路线：建表 → CRUD → 多表 → 索引 → 事务 → 集成优化；⑤ 选型上互联网业务 MySQL 性价比最高。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：① TRUNCATE 属于 DDL 还是 DML？为什么它不能回滚？（答案：DDL，因为它直接 drop+rebuild 表，不产生 undo log）。② `SELECT` 属于哪一类？（DQL）。
> - ⭐⭐ **进阶题**：为什么 MySQL 在互联网公司比 PostgreSQL 更主流？从生态、运维、人才市场三个角度思考。
> - ⭐⭐⭐ **实战题**：背景：团队新入职，需要在一台干净的 Linux 服务器上 30 分钟内搭好一个可登录、字符集正确、带远程账号的 MySQL 8 环境。要求：root 只允许本机登录，新建应用账号 `app` 可从 `10.0.0.%` 网段登录并只能访问 `shop` 库，`sudo mysql_secure_installation` 全部执行。验收：`mysql -uapp -p -h 10.0.0.5 shop` 能连上，`SELECT 1` 成功。提示：参考 1.3 的 apt 流程 + 第十一章的 GRANT 语法。

---

## 二、数据类型体系：数值、字符串、日期与 JSON

### 2.1 为什么数据类型选择很重要

**概念解释**：数据类型是"给每一列贴上的存储规格标签"，它决定了这一列占多少字节、能存什么值、MySQL 如何比较与排序。选错类型轻则浪费存储、拖慢查询，重则精度丢失、业务算错钱。

**生活化比喻**：数据类型就像厨房里的容器——装油用油罐（DECIMAL 精确），装水用水桶（VARCHAR 够用），装汤用汤碗（TEXT）。你不会拿量杯去装整桶油，也不会用洗脸盆去量一茶匙盐。

**核心价值**：正确的类型让索引更紧凑（占字节少 → 单页能放更多键 → B+ 树更矮 → 查询更快），也让存储引擎的比较与排序语义符合业务预期。

### 2.2 数值类型全景

| 类型 | 字节 | 有符号范围 | 典型用途 |
|------|------|-----------|----------|
| TINYINT | 1 | -128 ~ 127 | 状态位、性别、是否删除 |
| SMALLINT | 2 | -32768 ~ 32767 | 小计数 |
| MEDIUMINT | 3 | ±838 万 | 不常用 |
| INT | 4 | ±21 亿 | 普通自增主键 |
| BIGINT | 8 | ±9.2×10¹⁸ | 雪花 ID、未来防溢出主键 |
| FLOAT | 4 | 单精度约 7 位有效数字 | **禁止用于金额** |
| DOUBLE | 8 | 双精度约 15 位 | 科学计算 |
| DECIMAL(M,D) | 变长 | 精确十进制 | **金额必用** |
| BIT / BOOLEAN | 1 | 0/1 | 布尔标志 |

```sql
-- ⚠️ 新手注意：金额字段的类型选择
CREATE TABLE wallet_bad (
  user_id BIGINT PRIMARY KEY,
  balance DOUBLE            -- 错误：浮点有精度误差
);
CREATE TABLE wallet_good (
  user_id BIGINT PRIMARY KEY,
  balance DECIMAL(12,2)    -- 正确：12位总长，2位小数，最大 9999999999.99
);

-- 演示浮点精度问题
INSERT INTO wallet_bad(user_id, balance) VALUES(1, 0.1), (2, 0.2);
SELECT SUM(balance) FROM wallet_bad;
-- 错误结果示例：0.300000011920929（不是 0.3）
SELECT SUM(balance) FROM wallet_good;
-- 正确结果：0.30
```

```sql
-- UNSIGNED 无符号：把范围全部让给正数，年龄、状态等非负字段推荐
CREATE TABLE users_demo (
  age TINYINT UNSIGNED DEFAULT 0,        -- 0~255
  gender TINYINT UNSIGNED DEFAULT 0      -- 0未知 1男 2女
);
INSERT INTO users_demo(age) VALUES(300);
-- 报错 Out of range value，因为 TINYINT UNSIGNED 最大 255
```

> ❌ **常见坑点**：① 用 FLOAT/DOUBLE 存金额 → 财务对账时出现 0.30000000004 这种幽灵尾数，根因是 IEEE754 二进制浮点无法精确表示 0.1/0.2；正确做法一律 DECIMAL。② 用 INT 做自增主键，在分库分表后总量很快超 21 亿；正确做法用 BIGINT 存雪花 ID。③ 误以为 INT(N) 中的 N 是长度——N 只是"显示宽度"，5.7 后已废弃，不影响取值范围。

### 2.3 字符串类型

| 类型 | 上限 | 特点 | 适用 |
|------|------|------|------|
| CHAR(N) | 255 字符 | 定长，不足补空格，读取时去尾空格 | 长度恒定：MD5、UUID、手机号、性别码 |
| VARCHAR(N) | 65535 字节 | 变长，额外 1~2 字节存长度 | 用户名、标题、地址（最常用） |
| TINYTEXT/TEXT | 255/65535 字节 | 不能设默认值 | 文章摘要、简介 |
| MEDIUMTEXT/LONGTEXT | 16MB/4GB | 同上 | 文章正文、大 JSON |
| ENUM | - | 单选枚举 | 订单状态（8.0 前推荐，8.0.16 后可用 CHECK 替代） |
| SET | - | 多选集合 | 不推荐，扩展性差 |
| JSON | - | 原生 JSON 文档 | 半结构化字段 |

```sql
-- VARCHAR(N) 的 N 是"字符数"不是"字节数"，utf8mb4 下每字符最多 4 字节
CREATE TABLE articles (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(200) NOT NULL,        -- 最多 200 个字符
  content TEXT,                       -- 最多 64KB
  tags JSON,                          -- 原生 JSON
  md5 CHAR(32) NOT NULL UNIQUE        -- 定长 32 字符
) ENGINE=InnoDB;

INSERT INTO articles(title, content, tags)
VALUES('MySQL 入门', '正文内容……', '["数据库","MySQL","教程"]');

-- JSON 字段的读取
SELECT tags->"$[0]" FROM articles;       -- 第一个标签 → "数据库"
SELECT JSON_EXTRACT(tags, '$[1]') FROM articles;
-- 5.7+ 支持 JSON 函数索引与路径查询
```

> ❌ **常见坑点**：① 把身份证、手机号用 INT 存——手机号以 1 开头看似数字，但前导零、超长号段、与字母混排都会出问题，永远用 VARCHAR。② VARCHAR(255) 一刀切——长度过短会截断业务数据，过长浪费联合索引容量；按"业务最大长度 ×1.3"取并对齐到常用档位（50/100/255）。③ CHAR 与 VARCHAR 混用做连接条件时，前导/尾随空格导致 JOIN 不上。

### 2.4 日期时间类型

| 类型 | 范围 | 时区 | 字节 | 说明 |
|------|------|------|------|------|
| DATE | 1000~9999 年 | - | 3 | 仅日期 |
| TIME | -838:59:59 ~ 838:59:59 | - | 3 | 仅时间 |
| YEAR | 1901~2155 | - | 1 | 年份 |
| DATETIME | 1000~9999 年 | **不带时区** | 8 | 业务时间首选 |
| TIMESTAMP | 1970~2038（UTC 秒） | **随时区转换** | 4 | 自动转换，2038 问题 |

```sql
CREATE TABLE events (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(100),
  event_at DATETIME DEFAULT CURRENT_TIMESTAMP,       -- 业务时间，不随时区变
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 常用日期函数
SELECT NOW();                                  -- 2026-09-11 14:30:00
SELECT DATE_ADD(NOW(), INTERVAL 7 DAY);        -- 7 天后
SELECT DATE_SUB(NOW(), INTERVAL 1 HOUR);       -- 1 小时前
SELECT DATEDIFF('2026-12-31', '2026-01-01');   -- 364
SELECT DATE_FORMAT(NOW(), '%Y年%m月%d日');      -- 2026年09月11日
```

> 🎯 **面试高频**：DATETIME 和 TIMESTAMP 区别？答：① 存储范围不同（TIMESTAMP 到 2038 年）；② TIMESTAMP 存的是 UTC 秒，读取时按会话时区转换，跨时区部署会出"时间自动偏移"问题；③ 字节数 8 vs 4。业务系统统一用 DATETIME，时间戳到应用层或 BIGINT 存毫秒。

> ❌ **常见坑点**：① 用字符串存日期（"2026/09/11"），导致无法用日期函数、无法走时间索引范围扫描。② TIMESTAMP 字段跨时区服务器迁移后时间"莫名偏移 8 小时"。③ `ON UPDATE CURRENT_TIMESTAMP` 会让字段在任何 UPDATE 时自动刷新，审计日志字段慎用。

### 2.5 JSON 类型实战

```sql
-- 场景：商品表中用 JSON 存规格属性，避免宽表
CREATE TABLE products_json (
  id BIGINT PRIMARY KEY,
  name VARCHAR(200),
  attrs JSON,                       -- {"color":"red","size":"XL","weight":1.2}
  INDEX idx_color ((CAST(attrs->>'$.color' AS CHAR(20))))   -- 5.7+ 函数索引
) ENGINE=InnoDB;

INSERT INTO products_json VALUES
(1, 'T恤', '{"color":"red","size":"XL","weight":1.2}'),
(2, '牛仔裤', '{"color":"blue","size":"32","weight":0.8}');

-- 取值：-> 返回带引号 JSON，->> 返回去引号字符串
SELECT id, name, attrs->>'$.color' AS color FROM products_json;
-- 预期：1 T恤 red / 2 牛仔裤 blue

-- 条件查询
SELECT * FROM products_json WHERE attrs->>'$.size' = 'XL';
```

```python
# Python 侧把 dict 直接当 JSON 写入（pymysql 自动序列化）
import json
import pymysql

conn = pymysql.connect(host='127.0.0.1', user='root',
                       password='root123', database='lab', charset='utf8mb4')
with conn.cursor() as cur:
    cur.execute("INSERT INTO products_json(id,name,attrs) VALUES(%s,%s,%s)",
                (3, '帽子', json.dumps({'color': 'black', 'size': 'M'})))
conn.commit()
# 预期：插入成功，SELECT attrs->>'$.color' 返回 black
```

> ❌ **常见坑点**：① 把整个 JSON 当黑盒存，连 `attrs->>'$.color' = 'red'` 都建不上索引，结果全表扫描；正确做法对高频查询路径建生成列 + 索引。② JSON 字段不能直接设默认值（5.7），要写 `DEFAULT ('{}')`。③ 频繁用 `JSON_SET` 更新整个 JSON，性能差且并发冲突大，高频变更字段应拆成独立列。

> 💡 **本章深度讲解**：数据类型是"表设计的第一道防线"。记住三条铁律：金额 DECIMAL、时间 DATETIME、字符串按业务长度取 VARCHAR。类型选对了，后面索引、压缩、对比才有意义；类型选错，加再多索引也救不回来。本章与第三章 DDL 是一体两面——建表时就是在做类型决策。
>
> 📝 **本章精简总结**：① 金额 DECIMAL(M,D)，禁用 FLOAT/DOUBLE；② 主键 BIGINT，状态 TINYINT，非负加 UNSIGNED；③ 字符串 VARCHAR 按业务长度选，定长短码用 CHAR；④ 时间用 DATETIME，避开 TIMESTAMP 的 2038 与时区问题；⑤ 半结构化属性用 JSON 但要为高频查询路径建函数索引。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：① 余额 99999999.99 用什么 DECIMAL？（DECIMAL(12,2)）。② 用户年龄用 TINYINT 还是 INT？（TINYINT UNSIGNED）。
> - ⭐⭐ **进阶题**：为什么 VARCHAR(255) 是"互联网默认值"？它与联合索引的"最大长度 768 字节 / 3072 字节"有什么关系？（提示：InnoDB 索引键长度限制）。
> - ⭐⭐⭐ **实战题**：设计一张 `sku` 表，含 id、sku_code（定长18位）、price、stock、attrs(JSON 颜色/尺码/重量)、创建时间。要求 price 能精确存到分、stock 不为负、sku_code 唯一、创建时间自动填充。验收：能 INSERT 一条 T 恤 S 码记录，price=99.50，attrs 含 color/size，`attrs->>'$.color'` 返回 red。


---

## 三、DDL：数据库、表与六大约束

### 3.1 数据库级操作

**概念解释**：DDL（Data Definition Language）用于定义"数据容器的结构"——建库、建表、改表、删表。它的操作对象是"元数据"（数据字典），一旦执行立即生效且（多数情况下）不可回滚。

**生活化比喻**：DDL 就像盖房子时"打地基、砌墙、隔房间"——墙一旦砌好，再改格局就是大工程；DML 才是"往里搬家具"。所以建表前一定要把字段、类型、约束想清楚。

```sql
-- 1. 建库：必须显式指定 utf8mb4 与排序规则
CREATE DATABASE IF NOT EXISTS shop
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

-- 2. 查看所有库
SHOW DATABASES;

-- 3. 切换当前库
USE shop;

-- 4. 查看建库语句
SHOW CREATE DATABASE shop;

-- 5. 删除库（危险！会删掉里面所有表）
DROP DATABASE IF EXISTS shop;
```

> ❌ **常见坑点**：① 不指定字符集建库，结果默认 `latin1`，存中文直接乱码。② 5.7 时代的 `utf8` 实际是 `utf8mb3`（3 字节），存不了 emoji（4 字节）；必须用 `utf8mb4`。③ 排序规则 `utf8mb4_general_ci` vs `utf8mb4_unicode_ci`：前者快但校对不严谨，后者更标准；跨库 JOIN 时两表排序规则不同会报 "Illegal mix of collations"。

### 3.2 建表：一张规范表长什么样

```sql
CREATE TABLE users (
  -- 主键：BIGINT 自增，注释必备
  id            BIGINT       NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  -- 业务字段：非空、唯一、注释
  username      VARCHAR(50)  NOT NULL COMMENT '登录名',
  nickname      VARCHAR(50)  NOT NULL DEFAULT '' COMMENT '昵称',
  email         VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
  phone         VARCHAR(20)  DEFAULT NULL COMMENT '手机号',
  password_hash VARCHAR(255) NOT NULL COMMENT 'bcrypt 密码哈希',
  age           TINYINT UNSIGNED DEFAULT 0 COMMENT '年龄',
  status        TINYINT      NOT NULL DEFAULT 1 COMMENT '1正常 0禁用',
  -- 审计字段：创建/更新时间自动维护
  created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                 ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  -- 主键与索引
  PRIMARY KEY (id),
  UNIQUE KEY uk_username (username),
  UNIQUE KEY uk_email (email),
  KEY idx_phone (phone),
  KEY idx_status_created (status, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='用户表';
```

```sql
-- 查看表结构（字段、类型、键）
DESC users;
-- 或看完整建表语句
SHOW CREATE TABLE users\G

-- 表存在性判断（MySQL 8.0+ 支持）
CREATE TABLE IF NOT EXISTS users (...) ENGINE=InnoDB;
```

### 3.3 ALTER TABLE 的常用姿势

```sql
-- 加列：AFTER 指定位置，避免加在末尾
ALTER TABLE users ADD COLUMN gender TINYINT NOT NULL DEFAULT 0 AFTER age;

-- 改列类型/定义
ALTER TABLE users MODIFY COLUMN nickname VARCHAR(100) NOT NULL DEFAULT '';

-- 重命名列（8.0）
ALTER TABLE users RENAME COLUMN phone TO mobile;

-- 删列（谨慎！）
ALTER TABLE users DROP COLUMN gender;

-- 加索引
ALTER TABLE users ADD INDEX idx_status (status);

-- 删索引
ALTER TABLE users DROP INDEX idx_status;

-- 重命名表
RENAME TABLE users TO user_account;
```

```sql
-- ⚠️ 大表加列的现代写法（8.0）：INSTANT 算法，不锁表
ALTER TABLE huge_table ADD COLUMN remark VARCHAR(255), ALGORITHM=INSTANT, LOCK=NONE;
-- 对比：老版本 COPY 算法会重建整张表，千万行要锁表几十分钟
```

> ❌ **常见坑点**：① 在千万行大表上直接 `ALTER TABLE ADD COLUMN`，8.0 之前会锁表全表重建；正确做法优先 8.0 的 INSTANT，或 pt-online-schema-change、gh-ost。② 改列类型时"悄悄截断数据"——把 VARCHAR(100) 改成 VARCHAR(10) 会把超长数据截断或报错，先清洗再改。③ 频繁 ALTER 导致表碎片化，定期 `OPTIMIZE TABLE`（但会锁表，业务低峰做）。

### 3.4 六大约束：数据库层的最后防线

| 约束 | 关键字 | 保证什么 | 一个生活类比 |
|------|--------|----------|-------------|
| 主键 | PRIMARY KEY | 每行唯一且非空 | 身份证号 |
| 外键 | FOREIGN KEY | 引用完整性 | 你只能选存在的国家 |
| 唯一 | UNIQUE | 列不重复（可 NULL） | 用户名不能重 |
| 非空 | NOT NULL | 必须有值 | 姓名不能为空 |
| 默认 | DEFAULT | 插入缺省值 | 新账号默认 status=1 |
| 检查 | CHECK | 值满足表达式 | age > 0 |

```sql
CREATE TABLE orders (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_no     VARCHAR(32)  NOT NULL UNIQUE COMMENT '订单号',
  user_id      BIGINT       NOT NULL COMMENT '下单用户',
  amount       DECIMAL(12,2) NOT NULL CHECK (amount > 0),   -- 8.0.16+ 生效
  status       VARCHAR(20)  NOT NULL DEFAULT 'pending'
               CHECK (status IN ('pending','paid','shipped','done')),
  created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  -- 外键：user_id 必须引用存在的 users.id
  CONSTRAINT fk_order_user FOREIGN KEY (user_id)
    REFERENCES users(id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB;

-- ON DELETE 行为：
-- CASCADE      删用户时级联删订单
-- RESTRICT     有订单引用时禁止删用户（默认）
-- SET NULL     删用户时把 user_id 置 NULL
-- NO ACTION    同 RESTRICT
```

> 🎯 **面试高频**：外键要不要用？答：互联网高并发场景**通常不用物理外键**——外键在高并发写入时会成为性能瓶颈（每次 INSERT 都要校验引用），且分库分表后跨库外键根本不存在。引用完整性交给应用层 + 定时校对任务。但中小规模、强一致要求高的内部系统，物理外键是最便宜的防线。

> ❌ **常见坑点**：① 5.7 时代 CHECK 约束被"解析但忽略"，业务方以为生效了实际没拦住；8.0.16 才真正实现。② 用 ENUM 存状态，加新状态要 ALTER TABLE 锁表；推荐 VARCHAR + CHECK 或字典表。③ 外键列和被引用列类型必须严格一致（一个 INT 一个 BIGINT 会建不上）。

### 3.5 TRUNCATE vs DELETE vs DROP

| 操作 | 作用对象 | 速度 | 回滚 | 自增 | 触发器 |
|------|---------|------|------|------|--------|
| DELETE | 行（可 WHERE） | 慢 | ✅ | 不重置 | 触发 |
| TRUNCATE | 全表 | 极快 | ❌ | 重置 | 不触发 |
| DROP | 表结构+数据 | 极快 | ❌ | - | 不触发 |

```sql
-- DELETE：逐行删，可带条件，可回滚
START TRANSACTION;
DELETE FROM orders WHERE status = 'cancelled' AND created_at < '2026-01-01';
ROLLBACK;   -- 数据回来了

-- TRUNCATE：清空表，不可回滚，自增归零
TRUNCATE TABLE orders;

-- DROP：连表带结构一起删
DROP TABLE IF EXISTS orders;
```

> 💡 **本章深度讲解**：DDL 的核心心智是"结构即契约"。表一旦上线，每一次 ALTER 都是一次"对线上数据结构的手术"。本章最重要的不是记住 ALTER 语法，而是建立"宁可一开始多想半小时，也不要在线上加列加索引"的工程直觉。六大约束是数据库给你的最后一道防线——能在数据库层拦住的脏数据，就不要指望应用层永远写对。
>
> 📝 **本章精简总结**：① 建库必带 utf8mb4/utf8mb4_unicode_ci；② 建表三件套：主键 BIGINT、审计时间戳、字段注释；③ 六大约束按业务需要选，外键在高并发下慎用；④ 大表 ALTER 用 8.0 INSTANT 或 gh-ost；⑤ DELETE 可回滚，TRUNCATE/DROP 不可回滚。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：① 为什么用 utf8mb4 而不是 utf8？② TRUNCATE 为什么不能回滚？
> - ⭐⭐ **进阶题**：给一张 5000 万行的订单表加一列 `remark VARCHAR(255)`，请说出至少两种不锁表方案的取舍。
> - ⭐⭐⭐ **实战题**：在 shop 库中建 `products` 表：id、sku（定长18位唯一）、name、price(>0)、stock(>=0)、status(枚举在在售/下架/预售)、created_at。验收：插入一条 sku=SKU000000000000001 的 T 恤 price=59.9 成功；插入 price=-1 被 CHECK 拒绝。

---

## 四、DML：INSERT、UPDATE、DELETE 与安全更新

### 4.1 INSERT：单行、多行与 INSERT ... SELECT

```sql
-- 单行插入
INSERT INTO users(username, email, password_hash)
VALUES('alice', 'alice@example.com', '$2a$10$xxxx');

-- 多行插入（比循环单插快几十倍）
INSERT INTO users(username, email, age) VALUES
  ('bob',   'bob@example.com',   25),
  ('carol', 'carol@example.com', 30),
  ('dave',  'dave@example.com',  28);

-- 插入查询结果（常用于数据迁移/归档）
INSERT INTO users_archive(id, username, email, created_at)
SELECT id, username, email, created_at
FROM users
WHERE created_at < '2025-01-01';

-- 幂等插入：存在则忽略
INSERT IGNORE INTO users(username, email) VALUES('alice', 'a@b.com');
-- 存在则更新（upsert）
INSERT INTO users(username, email, age)
VALUES('alice', 'a@b.com', 26)
ON DUPLICATE KEY UPDATE age = VALUES(age), updated_at = NOW();
```

> 🎯 **面试高频**：`INSERT ... ON DUPLICATE KEY UPDATE` 的原理是什么？答：依赖唯一键冲突——若插入违反主键/唯一键约束，就转为 UPDATE。它常用于"存在即更新"的幂等写入，但要注意 VALUES() 函数在 8.0.20 后被废弃，应改用别名：`INSERT ... AS new ON DUPLICATE KEY UPDATE age = new.age`。

### 4.2 UPDATE：永远带上 WHERE

```sql
-- ⚠️ 新手注意：下面这句是生产事故重灾区
UPDATE users SET status = 0;     -- 把全表都禁用了！

-- 正确：永远带 WHERE
UPDATE users SET status = 0 WHERE id = 1001;

-- 带表达式的更新
UPDATE products SET stock = stock - 1 WHERE id = 2001 AND stock > 0;

-- 基于 JOIN 的多表更新
UPDATE users u
JOIN orders o ON o.user_id = u.id
SET u.total_orders = u.total_orders + 1
WHERE o.id = 9001;
```

```sql
-- 安全更新模式：让忘写 WHERE 的 UPDATE/DELETE 直接报错
SET SQL_SAFE_UPDATES = 1;
UPDATE users SET status = 0;
-- 报错：You are using safe update mode...
-- 必须改成
UPDATE users SET status = 0 WHERE id = 1001;
```

> ❌ **常见坑点**：① UPDATE 不带 WHERE 全表更新——预防：始终开 `SQL_SAFE_UPDATES=1`，生产账号禁用无 WHERE 的批量操作。② 在事务里大事务 UPDATE 多行，长事务持有大量行锁导致后续请求阻塞；正确做法分批 `WHERE id BETWEEN ? AND ?`。③ `UPDATE ... JOIN` 时两表 JOIN 条件写错，导致误更新一大批行——先 SELECT 确认影响行数，再开事务改。

### 4.3 DELETE：逻辑删除 vs 物理删除

```sql
-- 物理删除（真删）
DELETE FROM users WHERE id = 1001;

-- 逻辑删除（推荐！业务上"删"了其实是打标）
ALTER TABLE users ADD COLUMN is_deleted TINYINT NOT NULL DEFAULT 0;
UPDATE users SET is_deleted = 1 WHERE id = 1001;
-- 查询时统一过滤
SELECT * FROM users WHERE id = 1001 AND is_deleted = 0;
```

| 维度 | 物理删除 DELETE | 逻辑删除 is_deleted |
|------|----------------|---------------------|
| 数据可恢复 | 难（靠 binlog/备份） | 改回 0 即可 |
| 外键引用 | 易破坏 | 无影响 |
| 审计/合规 | 不满足 | 满足"不可篡改"要求 |
| 查询复杂度 | 简单 | 每个查询都要带条件 |
| 存储成本 | 省 | 表越积越大 |

> ✅ **最佳实践**：互联网业务几乎一律用逻辑删除。配合 `is_deleted` + `deleted_at` 两列，既能恢复又能审计。真正的物理删除交给定时任务，把"3 年前已逻辑删"的数据归档到冷存储。

### 4.4 影响行数与事务回滚

```sql
START TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
SELECT ROW_COUNT();          -- 受影响行数（1）

UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- 模拟异常：如果第二条失败
-- SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '余额不足';

COMMIT;   -- 或 ROLLBACK
```

> ❌ **常见坑点**：① 误以为 `SELECT ROW_COUNT()` 拿到的是"查询行数"——它是上一条语句影响的行数，SELECT 请用 FOUND_ROWS() 或直接拿结果集长度。② 多步 DML 忘记 COMMIT，连接被释放时隐式回滚，业务方以为成功了实际没生效。③ 长事务中先 SELECT 再 UPDATE，中间其他事务改了数据，出现"幻读/丢失更新"——后续章节讲乐观锁/悲观锁。

> 💡 **本章深度讲解**：DML 的本质是"在事务上下文中修改数据行"。新手学 INSERT/UPDATE/DELETE 语法半小时就能上手，但真正的生产能力体现在三点：① 永远先 SELECT 看影响范围再 UPDATE；② 用逻辑删除保留可恢复性；③ 把多步写操作包在事务里。这一章和第九章事务是紧密关联的——你现在写的每条 UPDATE，将来都要理解它加了什么锁、和 MVCC 怎么交互。
>
> 📝 **本章精简总结**：① 多行 INSERT 一次写完，比循环单插快；② upsert 用 ON DUPLICATE KEY UPDATE；③ UPDATE/DELETE 必带 WHERE，常开 SQL_SAFE_UPDATES；④ 业务删除用 is_deleted 逻辑删；⑤ 多步写包事务，COMMIT 前 SELECT 验证行数。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：① 一次插入 1000 行用单条 INSERT 还是 1000 条单插？为什么？② DELETE 错写为 UPDATE 后怎么回滚？
> - ⭐⭐ **进阶题**：为什么 `INSERT ... ON DUPLICATE KEY UPDATE` 在高并发下仍可能出问题？（提示：唯一键冲突的死锁）。
> - ⭐⭐⭐ **实战题**：用户下单时要做三件事——扣库存（products.stock -= 1）、插订单（orders）、记流水（order_log）。请写出事务版本的 SQL，要求任何一步失败全部回滚，且 stock 不扣成负数。


---

## 五、DQL 基础：SELECT、WHERE、ORDER BY 与 LIMIT

### 5.1 SELECT 子句的完整形态

**概念解释**：SELECT 是 SQL 中使用频率最高的语句，它从表里"投影+筛选"出你要的列和行。理解 SELECT 的关键不是背语法，而是理解它的**逻辑执行顺序**。

**生活化比喻**：SELECT 就像点奶茶——你先选基底（FROM 哪张表），再加料筛选（WHERE），再按口味分组（GROUP BY），最后选要哪几款（SELECT 列）并排序打包（ORDER BY/LIMIT）。

```sql
-- 一条"完整"的 SELECT
SELECT
  u.status,                              -- ⑤ 投影列
  COUNT(*) AS cnt,                       -- ⑤ 聚合
  AVG(u.age) AS avg_age
FROM users u                              -- ① 数据源
WHERE u.status = 1                        -- ② 行过滤
GROUP BY u.status                         -- ③ 分组
HAVING cnt > 5                            -- ④ 分组过滤
ORDER BY cnt DESC                         -- ⑥ 排序
LIMIT 0, 10;                              -- ⑦ 分页
```

**逻辑执行顺序**（不是书写顺序！）：

```
FROM/JOIN → WHERE → GROUP BY → 聚合 → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT
```

> 🎯 **面试高频**：为什么 WHERE 里不能用 SELECT 中起的别名？因为逻辑上 WHERE 在 SELECT 之前执行，别名还不存在。HAVING 也不能直接用别名（MySQL 例外允许），ORDER BY 可以。

### 5.2 WHERE 条件大全

```sql
-- 比较运算
SELECT * FROM users WHERE age > 25;
SELECT * FROM users WHERE age >= 18 AND age <= 60;
SELECT * FROM users WHERE age BETWEEN 18 AND 60;     -- 闭区间
SELECT * FROM users WHERE status <> 0;               -- !=

-- 逻辑组合
SELECT * FROM users WHERE age > 20 AND status = 1;
SELECT * FROM users WHERE age < 18 OR age > 60;
SELECT * FROM users WHERE NOT (age < 18);

-- IN / NOT IN
SELECT * FROM users WHERE status IN (1, 2, 3);

-- LIKE 模糊
SELECT * FROM users WHERE username LIKE '张%';    -- 张开头（走索引）
SELECT * FROM users WHERE username LIKE '%三';    -- 三结尾（不走索引）
SELECT * FROM users WHERE username LIKE '%三%';   -- 包含（不走索引）
SELECT * FROM users WHERE username LIKE '张_';    -- 张+一个字

-- NULL 判断（不能用 = NULL）
SELECT * FROM users WHERE phone IS NULL;
SELECT * FROM users WHERE phone IS NOT NULL;

-- 安全的 NULL 比较：把 NULL 当 0
SELECT * FROM users WHERE IFNULL(age, 0) >= 18;
```

> ❌ **常见坑点**：① `WHERE phone = NULL` 永远返回空——NULL 的比较要用 IS NULL，因为 NULL = NULL 结果是 UNKNOWN。② `LIKE '%xxx'` 左模糊导致索引失效，前文索引章节会详述。③ `NOT IN` 子查询中只要有一个 NULL，整个结果为空——这是新手最经典的 bug。

### 5.3 ORDER BY 排序

```sql
-- 单列排序（ASC 升序默认，DESC 降序）
SELECT * FROM users ORDER BY created_at DESC;

-- 多列排序：先按 status 升序，同 status 按 created_at 降序
SELECT * FROM users ORDER BY status ASC, created_at DESC;

-- 按表达式排序
SELECT username, age*12 AS months FROM users ORDER BY months DESC;

-- 按 FIELD 自定义顺序
SELECT * FROM orders
ORDER BY FIELD(status, 'paid', 'shipped', 'done', 'pending');
-- 让 paid 排最前，pending 排最后
```

> ❌ **常见坑点**：① ORDER BY 的列没有索引，会出现 `Using filesort`（文件排序），大数据量时 CPU 飙高。② 多列排序方向与联合索引不一致（索引是 `(a ASC, b ASC)`，查询写成 `ORDER BY a ASC, b DESC`），无法用索引顺序。③ 对 TEXT/BLOB 列排序会用临时表，更慢。

### 5.4 LIMIT 分页与深分页问题

```sql
-- 经典分页：第 1 页，每页 10 条
SELECT * FROM users ORDER BY id LIMIT 0, 10;
-- 第 1000 页
SELECT * FROM users ORDER BY id LIMIT 9990, 10;   -- ⚠️ 深分页慢

-- MySQL 8.4+ 推荐 OFFSET 写法
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 9990;

-- ✅ 优化：游标分页（记住上一页最后一个 id）
SELECT * FROM users WHERE id > 9990 ORDER BY id LIMIT 10;
-- 预期：直接从 id=9991 开始扫 10 行，不扫前面 9990 行
```

```sql
-- ✅ 另一种优化：子查询先定位主键，再 JOIN 回表
SELECT u.* FROM users u
JOIN (SELECT id FROM users ORDER BY id LIMIT 9990, 10) t
  ON u.id = t.id;
-- 子查询走覆盖索引，不回表，速度提升数十倍
```

> 🎯 **面试高频**：MySQL 深分页为什么慢？怎么优化？答：`LIMIT 100000, 10` 会先扫前 10 万行再丢弃，扫描行数与 OFFSET 成正比。优化：① 游标分页 `WHERE id > last_id LIMIT n`；② 子查询先定位主键再 JOIN 回表；③ 业务上禁止跳页，只允许"上一页/下一页"。

### 5.5 DISTINCT 与别名

```sql
-- DISTINCT 去重：所有列组合去重
SELECT DISTINCT status FROM users;
SELECT DISTINCT status, age FROM users;     -- 按(status,age)组合去重

-- 别名：AS 可省略，但别用关键字
SELECT username AS 用户名, age * 12 AS age_months FROM users;
```

> ❌ **常见坑点**：① `COUNT(DISTINCT col)` 与 `DISTINCT col` 语义不同——前者是聚合去重计数，后者是投影去重行。② 别名与列名冲突时 SELECT 中可能引用错。③ DISTINCT 与 ORDER BY 一起用时，ORDER BY 的列必须在 SELECT 列表里。

> 💡 **本章深度讲解**：SELECT 的核心不是语法，而是"逻辑执行顺序"。一旦你能在脑子里把一条 SQL 拆成 FROM→WHERE→GROUP→HAVING→SELECT→ORDER→LIMIT，你就理解了为什么 HAVING 能过滤聚合结果而 WHERE 不能、为什么 ORDER BY 可以用别名而 WHERE 不能。深分页是这一章的实战重点——它是所有后台系统"翻到最后一页就卡死"的元凶。
>
> 📝 **本章精简总结**：① 执行顺序 FROM→WHERE→GROUP→HAVING→SELECT→ORDER→LIMIT；② WHERE 不能用别名，ORDER BY 可以；③ NULL 比较用 IS NULL；④ ORDER BY 要走索引避免 filesort；⑤ 深分页用游标分页或子查询定位主键。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：① `WHERE age = NULL` 为什么查不出任何行？② `LIMIT 20, 10` 是第几页？
> - ⭐⭐ **进阶题**：为什么 MySQL 的 SQL 允许 `ORDER BY` 用 SELECT 别名，而 `WHERE` 不允许？从执行顺序解释。
> - ⭐⭐⭐ **实战题**：后台要做"用户列表"分页，按注册时间倒序，每页 20 条，数据量 500 万行。请写出第一页和第十页的 SQL，并对比 `LIMIT 20000, 20` 与游标分页两种写法的性能差异。

---

## 六、聚合函数、GROUP BY 与 HAVING

### 6.1 五大聚合函数

| 函数 | 作用 | 注意 |
|------|------|------|
| COUNT(*) | 统计行数（含 NULL） | 推荐 |
| COUNT(列) | 统计该列非 NULL 行数 | 别与 COUNT(*) 混 |
| SUM(列) | 求和 | 忽略 NULL |
| AVG(列) | 平均值 | 忽略 NULL |
| MAX / MIN | 最大/最小 | - |
| GROUP_CONCAT | 行拼字符串 | 有长度限制 1024 |

```sql
-- 基础统计
SELECT
  COUNT(*)           AS total,         -- 总用户数
  COUNT(phone)       AS has_phone,     -- 有手机号的用户数
  AVG(age)           AS avg_age,
  MAX(created_at)    AS latest_signup,
  MIN(created_at)    AS earliest_signup
FROM users
WHERE status = 1;
```

```sql
-- ⚠️ COUNT(*) vs COUNT(1) vs COUNT(列)
SELECT COUNT(*) FROM users;       -- 统计所有行
SELECT COUNT(1) FROM users;       -- 与 COUNT(*) 等价（InnoDB 优化后无差）
SELECT COUNT(phone) FROM users;   -- 只统计 phone 非 NULL 的行
```

> 🎯 **面试高频**：COUNT(*)、COUNT(1)、COUNT(列) 的区别？答：① COUNT(*) 与 COUNT(1) 在 InnoDB 中性能等价，统计所有行；② COUNT(列) 不统计该列为 NULL 的行；③ MyISAM 的 COUNT(*) 是 O(1)（有计数器），InnoDB 没有，需要扫索引；④ 大表精确 COUNT 很慢，业务上可用近似值 `EXPLAIN` 估算或维护计数表。

### 6.2 GROUP BY 分组

```sql
-- 按状态分组统计
SELECT status, COUNT(*) AS cnt, AVG(age) AS avg_age
FROM users
GROUP BY status;

-- 按多个列分组
SELECT status, YEAR(created_at) AS yr, COUNT(*) AS cnt
FROM users
GROUP BY status, YEAR(created_at);

-- WITH ROLLUP：额外汇总行（8.0 用 GROUPING SETS）
SELECT status, COUNT(*) FROM users GROUP BY status WITH ROLLUP;
-- 结果末尾多一行 status=NULL, COUNT=总行数
```

```sql
-- GROUP_CONCAT：把多行拼成一个字符串
SELECT
  status,
  GROUP_CONCAT(username ORDER BY created_at DESC SEPARATOR ',') AS users
FROM users
GROUP BY status;
-- 结果：1, alice,bob,carol
```

### 6.3 HAVING：分组后的过滤

```sql
-- WHERE 分组前过滤行，HAVING 分组后过滤组
SELECT status, COUNT(*) AS cnt, AVG(age) AS avg_age
FROM users
WHERE age IS NOT NULL        -- 先过滤掉 age 为 NULL 的行
GROUP BY status
HAVING cnt > 10              -- 再过滤"组内数量 > 10"的组
   AND avg_age > 25
ORDER BY cnt DESC;
```

| 维度 | WHERE | HAVING |
|------|-------|--------|
| 时机 | 分组前 | 分组后 |
| 能否用聚合函数 | ❌ | ✅ |
| 能否用列别名 | ❌ | ✅（MySQL 扩展） |
| 性能 | 先过滤减少分组量 | 后过滤，数据量已经大了 |

> ❌ **常见坑点**：① SELECT 中的非聚合列不在 GROUP BY 中——8.0 默认 `ONLY_FULL_GROUP_BY` 模式会直接报错，5.7 之前会"随机返回一行"。② 把过滤条件写在 HAVING 而不是 WHERE，导致先全量分组再过滤，慢；能在 WHERE 过滤就别放 HAVING。③ GROUP_CONCAT 默认 1024 字符截断，长结果要先 `SET group_concat_max_len = 100000`。

### 6.4 实战：电商运营日报

```sql
-- 统计每个用户的订单数、总金额、客单价
SELECT
  o.user_id,
  COUNT(o.id)                    AS order_cnt,
  SUM(o.total_amount)            AS total_paid,
  ROUND(SUM(o.total_amount) / COUNT(o.id), 2) AS avg_order,
  MAX(o.created_at)              AS last_order_at
FROM orders o
WHERE o.status = 'paid'
  AND o.created_at >= '2026-09-01'
GROUP BY o.user_id
HAVING order_cnt >= 3
ORDER BY total_paid DESC
LIMIT 100;
```

```sql
-- 用 HAVING 找"重复注册的邮箱"
SELECT email, COUNT(*) AS cnt
FROM users
GROUP BY email
HAVING cnt > 1;
```

> 💡 **本章深度讲解**：聚合的本质是"把多行折叠成一行"。GROUP BY 决定了按什么维度折叠，HAVING 决定了折叠后哪些组留下来。生产中最常见的性能问题是"先全量 GROUP BY 再 HAVING"——其实 WHERE 能提前过滤的行一定要提前过滤，减少分组输入。COUNT(*) 与 COUNT(列) 的区别、GROUP_CONCAT 截断、ONLY_FULL_GROUP_BY 是三个高频面试坑。
>
> 📝 **本章精简总结**：① COUNT(*) 统计所有行，COUNT(列) 排除 NULL；② WHERE 在分组前，HAVING 在分组后；③ 聚合函数忽略 NULL；④ 8.0 默认 ONLY_FULL_GROUP_BY，SELECT 非聚合列必须进 GROUP BY；⑤ GROUP_CONCAT 默认 1024 截断。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：① `SELECT status, COUNT(*) FROM users GROUP BY status` 中 COUNT(*) 是什么？② WHERE 和 HAVING 哪个先执行？
> - ⭐⭐ **进阶题**：为什么 8.0 开启 ONLY_FULL_GROUP_BY 是好事？它避免了什么历史 bug？
> - ⭐⭐⭐ **实战题**：统计 9 月每天的下单量与 GMV，要求只看已支付订单，结果按日期倒序，超过 100 单的日期才输出。写出完整 SQL。

---

## 七、多表查询：JOIN、子查询与 UNION

### 7.1 JOIN 的四种类型

**概念解释**：JOIN 把多张表按"关联条件"拼成一张宽表。它的本质是"嵌套循环"——驱动表的每一行去被驱动表里找匹配行。

**生活化比喻**：JOIN 就像相亲——INNER JOIN 是"双方都看上才见面"；LEFT JOIN 是"我把所有认识的人都列出来，你看上的标注上，没看上的留空"。

```mermaid
graph LR
    A[INNER 交集] --> B[LEFT 左全部+右匹配]
    B --> C[RIGHT 右全部+左匹配]
    C --> D[FULL 双方全部]
    style A fill:#43e97b,color:#333
    style B fill:#667eea,color:#fff
    style C fill:#feca57,color:#333
    style D fill:#ff9f43,color:#fff
```

```sql
-- 准备两张表演示
-- users(id, username)   orders(id, user_id, amount, status)

-- INNER JOIN：只返回两表都匹配的行
SELECT u.username, o.amount, o.status
FROM users u
INNER JOIN orders o ON o.user_id = u.id
WHERE o.status = 'paid';

-- LEFT JOIN：左表全部，右表没匹配就 NULL
SELECT u.username, o.amount
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.status = 1;
-- 没下过单的用户也会出现，amount 为 NULL

-- 找"从没下过单"的用户（LEFT JOIN + IS NULL 反模式）
SELECT u.id, u.username
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.id IS NULL;

-- 自连接：表自己连自己（员工-上级）
SELECT e.username AS 员工, m.username AS 上级
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

### 7.2 JOIN 的底层：Nested Loop Join

```mermaid
graph TB
    A[驱动表 users] -->|取一行| B[在 orders 索引上查 user_id=?]
    B --> C[匹配行拼结果]
    C --> D[驱动表下一行]
    D -->|循环| B
    style A fill:#ff6b6b,color:#fff
    style B fill:#43e97b,color:#333
```

**为什么"小表驱动大表"**：驱动表每一行都要在被驱动表上做一次索引查找，驱动表越大，循环次数越多。所以让小表当驱动表，循环次数最少。

```sql
-- 反例：把大表 orders 当驱动表
SELECT * FROM orders o JOIN users u ON o.user_id = u.id;
-- 假设 orders 100 万行、users 10 万行，循环 100 万次

-- 优化：优化器通常会自动选小表驱动，但你可以用 STRAIGHT_JOIN 强制
SELECT STRAIGHT_JOIN u.username, o.amount
FROM users u JOIN orders o ON o.user_id = u.id;
```

### 7.3 子查询的四种形态

```sql
-- 1. 标量子查询：返回单值
SELECT * FROM users
WHERE age > (SELECT AVG(age) FROM users);

-- 2. 行子查询：返回一行多列
SELECT * FROM users
WHERE (age, status) = (SELECT age, status FROM users WHERE id = 1);

-- 3. 表子查询：返回多行多列，常配合 IN
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000);

-- 4. EXISTS：存在性判断（相关子查询，外循环驱动）
SELECT u.username
FROM users u
WHERE EXISTS (
  SELECT 1 FROM orders o
  WHERE o.user_id = u.id AND o.amount > 1000
);
```

```sql
-- ANY / ALL
SELECT * FROM users WHERE age > ANY  (SELECT age FROM users WHERE status=1);
-- 大于 status=1 中任意一个 → 大于最小值
SELECT * FROM users WHERE age > ALL  (SELECT age FROM users WHERE status=0);
-- 大于 status=0 中所有 → 大于最大值
```

### 7.4 UNION 与 UNION ALL

```sql
-- UNION：合并并去重（要排序去重，慢）
SELECT username FROM users WHERE status = 1
UNION
SELECT username FROM users WHERE age > 30;

-- UNION ALL：合并不去重（快，推荐）
SELECT username FROM users WHERE status = 1
UNION ALL
SELECT username FROM users WHERE age > 30;
```

| 维度 | UNION | UNION ALL |
|------|-------|-----------|
| 去重 | ✅ 排序去重 | ❌ |
| 性能 | 慢（多一步排序） | 快 |
| 适用 | 明确需要去重 | 业务上本就不重复 / 可接受重复 |

> ❌ **常见坑点**：① UNION 各分支列数、类型、顺序必须一致。② 把 UNION ALL 当 UNION 用，结果有重复行没人发现；反过来把 UNION 当 UNION ALL，白白多了排序开销。③ 子查询中用 `NOT IN (subquery containing NULL)` 结果永远为空——前面 WHERE 章节讲过。

### 7.5 三表 JOIN 实战：电商订单查询

```sql
-- 查某用户的订单明细：订单 → 明细 → 商品
SELECT
  o.order_no,
  o.total_amount,
  o.status,
  p.name        AS product_name,
  oi.quantity,
  oi.price      AS unit_price,
  (oi.quantity * oi.price) AS subtotal
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p      ON p.id = oi.product_id
WHERE o.user_id = 1001
ORDER BY o.created_at DESC
LIMIT 20;
```

> 💡 **本章深度讲解**：多表查询的核心心智是"JOIN = 嵌套循环 + 索引查找"。理解了这一点，你就明白为什么小表驱动大表、为什么被驱动表的 JOIN 列必须有索引、为什么三表 JOIN 顺序很重要。子查询在 MySQL 5.6 之后有"半连接优化"，很多 IN 子查询会自动改写成 JOIN，性能差距没你想象的大；但 EXISTS 在"外层过滤后只剩少量行"时往往比 IN 快。
>
> 📝 **本章精简总结**：① INNER 交集、LEFT 左全部、RIGHT 右全部；② JOIN 本质嵌套循环，被驱动表 JOIN 列必须有索引；③ 小表驱动大表；④ 子查询分标量/行/表/EXISTS；⑤ 优先 UNION ALL，必要时才 UNION。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：① LEFT JOIN 后右表没匹配的行，右表列显示什么？② UNION 和 UNION ALL 区别？
> - ⭐⭐ **进阶题**：为什么 `NOT IN (SELECT ... WHERE ...)` 子查询里只要有一个 NULL 就返回空？写出反例 SQL。
> - ⭐⭐⭐ **实战题**：查"买过 T 恤但没买过牛仔裤"的用户。提示：用 LEFT JOIN + IS NULL 反连接，或 NOT EXISTS。


---

## 八、索引原理与使用：B+ 树、最左前缀与失效场景

### 8.1 索引是什么

**概念解释**：索引是"帮助 MySQL 高效查找数据的数据结构"。它本质是一份"排好序的目录"，让 MySQL 不必从第一行开始逐行扫描。

**生活化比喻**：索引就像字典的拼音目录——没有目录你只能一页页翻（全表扫描 O(n)），有目录你直接翻到对应页（树查找 O(log n)）。但目录本身要占额外纸张（索引占磁盘），每次改字典内容还要同步更新目录（写放大）。

### 8.2 InnoDB 为什么用 B+ 树

```mermaid
graph TB
    R[根节点] --> A[内部节点1]
    R --> B[内部节点2]
    A --> C[叶子页1]
    A --> D[叶子页2]
    B --> E[叶子页3]
    B --> F[叶子页4]
    C <--> D <--> E <--> F
    style R fill:#ff6b6b,color:#fff
    style C fill:#43e97b,color:#333
```

| 数据结构 | 为什么不选 | B+ 树为什么合适 |
|---------|-----------|----------------|
| 哈希表 | 不支持范围查询 | B+ 树叶子有序链表，范围扫描快 |
| 二叉树 | 树太高，IO 次数多 | B+ 树扇出大（一页放几百键），3~4 层 |
| B 树 | 内部节点也存数据，扇出小 | B+ 树内部不存数据，扇出更大更矮 |
| 跳表 | 内存级结构，磁盘随机读不友好 | B+ 树按页组织，契合磁盘预读 |

**B+ 树三大特点**：① 非叶子节点只存键和指针，不存数据（扇出大）；② 叶子节点存全部数据/主键，且双向链表相连（范围查询 O(树高+结果数)）；③ 树高通常 3~4 层，千万行表只需 3~4 次磁盘 IO。

### 8.3 聚簇索引 vs 二级索引 vs 回表

| 类型 | 叶子节点存什么 | InnoDB 中 |
|------|---------------|-----------|
| **聚簇索引** | 整行数据 | 主键索引（每张表必须有） |
| **二级索引（非聚簇）** | 主键值 | 其他所有索引 |

```mermaid
graph LR
    A[二级索引 username=张三] -->|叶子存| B[主键 id=1001]
    B -->|回表| C[聚簇索引查 id=1001]
    C --> D[拿到整行数据]
    style A fill:#feca57,color:#333
    style C fill:#667eea,color:#fff
```

**覆盖索引**：如果 SELECT 的列都在二级索引里，就不需要回表——Extra 显示 `Using index`，性能提升数倍。

```sql
-- 假设联合索引 idx_username_age(username, age)
-- ✅ 覆盖索引：只查 username 和 age，不用回表
SELECT username, age FROM users WHERE username = 'alice';

-- ❌ 需要回表：查了 status
SELECT username, age, status FROM users WHERE username = 'alice';
```

### 8.4 索引的创建与删除

```sql
-- 建表时建索引
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  username VARCHAR(50),
  age TINYINT,
  UNIQUE KEY uk_username(username),       -- 唯一索引
  KEY idx_age(age),                       -- 普通索引
  KEY idx_name_age(username, age)         -- 联合索引
);

-- 事后加索引
CREATE INDEX idx_status ON users(status);
CREATE UNIQUE INDEX uk_email ON users(email);

-- 查看索引
SHOW INDEX FROM users;

-- 删除索引
DROP INDEX idx_status ON users;
```

### 8.5 联合索引与最左前缀

**概念解释**：联合索引 `(a, b, c)` 按"先 a、再 b、后 c"排序。查询条件必须从最左列开始，才能用上这个索引。

```sql
-- 索引 (username, age, status)
SELECT * FROM users WHERE username = 'alice';              -- ✅ 用 username
SELECT * FROM users WHERE username = 'alice' AND age = 25; -- ✅ 用 username+age
SELECT * FROM users WHERE username = 'alice' AND status = 1; -- ⚠️ 只用 username（中间断了 age）
SELECT * FROM users WHERE age = 25;                        -- ❌ 跳过 username，完全不用
SELECT * FROM users WHERE username = 'alice' AND age > 20 AND status = 1;
-- ⚠️ range 后的 age 用了索引，status 用不上（因为 age 是范围，b 之后断序）
```

> 🎯 **面试高频**：最左前缀原则是什么？范围查询为什么会"断掉"后面的索引？答：B+ 树按 (a,b,c) 排序，一旦 a 确定、b 是范围 `>`，c 在 b 相同区间内就不再有序，所以 c 无法利用索引定位。

### 8.6 索引失效的 10 种场景

| 场景 | 错误示例 | 正确做法 |
|------|---------|----------|
| 对索引列用函数 | `WHERE YEAR(created_at)=2026` | `WHERE created_at BETWEEN '2026-01-01' AND '2026-12-31'` |
| 隐式类型转换 | `WHERE phone = 13800000000`（phone 是 VARCHAR） | `WHERE phone = '13800000000'` |
| LIKE 左模糊 | `WHERE name LIKE '%张'` | 业务改造，用 `'张%'` 或全文索引 |
| OR 连接非索引列 | `WHERE a=1 OR b=2`（b 无索引） | 改 UNION ALL 或给 b 加索引 |
| 不满足最左前缀 | 见 8.5 | 按查询条件设计索引列顺序 |
| != / NOT IN | `WHERE status != 1` | 评估改写为 IN |
| IS NULL / IS NOT NULL | 数据分布决定 | 小表无所谓，大表看选择性 |
| 优化器认为全表更快 | 表小或索引区分度低 | 正常现象，别强行加索引 |
| 字符串与数字比较 | 见隐式转换 | 类型严格一致 |
| 函数/运算在列上 | `WHERE age + 1 = 26` | `WHERE age = 25` |

```sql
-- 错误 vs 正确：时间范围查询
-- ❌ 失效：对 created_at 用 YEAR()
SELECT * FROM orders WHERE YEAR(created_at) = 2026;
-- ✅ 走索引：范围扫描
SELECT * FROM orders
WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01';
```

### 8.7 一张表到底建多少索引合适

> ✅ **最佳实践**：
> 1. 只为**高频 WHERE / JOIN / ORDER BY** 列建索引，别"能加就加"。
> 2. 优先建联合索引，把高频查询条件拼进去，而不是单列索引满天飞。
> 3. 区分度低的列（如 status 只有 0/1/2）单独建索引意义不大，要和高频列组成联合索引。
> 4. 每个索引都要付出 INSERT/UPDATE/DELETE 时的维护成本（B+ 树分裂）。
> 5. 索引不是越多越好——一张表 5~10 个索引是常见上限。

> ❌ **常见坑点**：① 给区分度极低的列（性别、是否删除）单独建索引——优化器大概率放弃它。② 在已经有 `(a,b)` 联合索引的情况下再单列建 `(a)`，浪费空间，因为 `(a,b)` 已经能服务 `a` 的查询。③ 把字符串长列建进联合索引，导致索引页数变多，树变高。

> 💡 **本章深度讲解**：索引是 MySQL 性能优化的"第一性原理"。理解 B+ 树结构，你就理解了为什么范围查询快、为什么最左前缀、为什么回表、为什么覆盖索引快。生产中 80% 的慢 SQL 都是"没走索引"或"走错索引"。EXPLAIN（第十一章）就是验证你索引是否生效的工具。这一章是全书的"性能基石"。
>
> 📝 **本章精简总结**：① InnoDB 用 B+ 树，3~4 层搞定千万行；② 聚簇索引存整行，二级索引存主键需回表；③ 覆盖索引免回表；④ 联合索引最左前缀，range 后断；⑤ 索引失效：函数、隐式转换、左模糊、OR、非最左前缀；⑥ 索引不是越多越好，写放大要权衡。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：① 为什么 InnoDB 不用二叉树？② 什么是回表？
> - ⭐⭐ **进阶题**：联合索引 `(a,b,c)`，查询 `WHERE a=1 AND c=3` 能用几个？为什么？
> - ⭐⭐⭐ **实战题**：一张 orders 表 1000 万行，常用查询是"按 user_id 查订单、按 status+created_at 查后台列表"。请设计索引方案，并说明如何用 EXPLAIN 验证。

---

## 九、事务、ACID 与隔离级别

### 9.1 为什么需要事务

**概念解释**：事务（Transaction）是"一组 SQL 操作的逻辑执行单元"——这组操作要么全部成功提交，要么全部失败回滚，对外表现为一个不可分割的整体。

**生活化比喻**：事务就像银行转账——A 给 B 转 100 元，必须同时做到"A 扣 100、B 加 100"。如果扣完 A 之后系统崩了，B 没收到，钱就凭空消失了。事务保证这种"多步操作"的原子性。

### 9.2 ACID 四大特性

| 特性 | 含义 | 实现机制 |
|------|------|----------|
| **原子性 Atomicity** | 事务内操作要么全做要么全不做 | undo log（回滚日志） |
| **一致性 Consistency** | 事务前后数据库从一个一致状态到另一个一致状态 | 由 AID 共同保证 |
| **隔离性 Isolation** | 并发事务之间互不干扰 | 锁 + MVCC |
| **持久性 Durability** | 提交后永久生效，宕机不丢 | redo log（重做日志） |

### 9.3 事务操作

```sql
-- 开启事务
START TRANSACTION;     -- 或 BEGIN

-- 扣款
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- 加钱
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- 检查异常（示例）
-- IF (SELECT balance FROM accounts WHERE id=1) < 0 THEN ROLLBACK; END IF;

-- 提交
COMMIT;

-- 或回滚
ROLLBACK;

-- 保存点：部分回滚
SAVEPOINT sp1;
UPDATE accounts SET balance = balance - 50 WHERE id = 1;
ROLLBACK TO sp1;   -- 回滚到 sp1，不影响 sp1 之前的操作
```

### 9.4 三种并发问题与四种隔离级别

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|---------|------|-----------|------|
| 读未提交 Read Uncommitted | ✅ 会 | ✅ 会 | ✅ 会 |
| 读已提交 Read Committed | ❌ | ✅ 会 | ✅ 会 |
| **可重复读 Repeatable Read（InnoDB 默认）** | ❌ | ❌ | ⚠️ InnoDB 用 MVCC+间隙锁基本解决 |
| 串行化 Serializable | ❌ | ❌ | ❌ |

**三种并发问题**：

- **脏读**：事务 A 读到了事务 B **未提交**的数据，B 回滚后 A 读到的就是"脏数据"。
- **不可重复读**：事务 A 两次读同一行，中间 B 修改并提交，A 两次结果不同。
- **幻读**：事务 A 两次按范围查询，中间 B 插入/删除了符合条件的行，A 第二次多/少了几行。

```sql
-- 查看当前隔离级别
SELECT @@transaction_isolation;
-- MySQL 8.0 输出：REPEATABLE-READ

-- 设置会话级隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

### 9.5 MVCC 与锁：InnoDB 怎么解决幻读

```mermaid
graph TB
    A[每行隐藏版本列 trx_id/roll_ptr] --> B[Undo Log 版本链]
    B --> C[ReadView 可见性判断]
    C --> D[RC: 每次 SELECT 生成新 ReadView]
    C --> E[RR: 事务启动时生成一次 ReadView]
    style A fill:#667eea,color:#fff
    style E fill:#43e97b,color:#333
```

**MVCC（多版本并发控制）**：每行数据有隐藏的事务 ID 和回滚指针，通过 Undo Log 形成版本链。读操作顺着版本链找"当前事务可见的版本"，写操作才加锁。这样读不阻塞写、写不阻塞读，并发性能大幅提升。

**当前读 vs 快照读**：

- **快照读**：普通 `SELECT`，走 MVCC 读历史版本，不加锁。
- **当前读**：`SELECT ... FOR UPDATE`、`SELECT ... LOCK IN SHARE MODE`、`UPDATE`、`DELETE`，读最新版本并加锁。

```sql
-- 快照读
SELECT * FROM users WHERE id = 1;
-- 当前读（加行锁）
SELECT * FROM users WHERE id = 1 FOR UPDATE;
-- 当前读（加共享锁）
SELECT * FROM users WHERE id = 1 LOCK IN SHARE MODE;
```

### 9.6 死锁：成因与预防

```sql
-- 死锁场景：两个事务以相反顺序锁定两行
-- 事务 A
START TRANSACTION;
UPDATE accounts SET balance = balance - 10 WHERE id = 1;
UPDATE accounts SET balance = balance + 10 WHERE id = 2;  -- 等待 B 释放 id=2

-- 事务 B
START TRANSACTION;
UPDATE accounts SET balance = balance - 10 WHERE id = 2;
UPDATE accounts SET balance = balance + 10 WHERE id = 1;  -- 等待 A 释放 id=1
-- 互相等待 → 死锁，InnoDB 检测到后回滚其中一个
```

> ✅ **最佳实践（防死锁）**：① 所有业务 SQL 按相同顺序访问表和行（例如永远先锁 user 表再锁 order 表）；② 大事务拆小，缩短锁持有时间；③ 索引设计合理，避免行锁升级为表锁；④ 必要时显式 `SELECT ... FOR UPDATE` 提前锁；⑤ 重试机制：应用层捕获 1213 死锁错误并重试。

> ❌ **常见坑点**：① 在事务里做 RPC、发邮件等慢操作，长事务持锁导致其他请求阻塞。② RR 隔离级别下用普通 `SELECT` 读最新数据——它读的是快照，要最新数据必须 `FOR UPDATE` 当前读。③ 把事务范围扩得过大（一个事务里既改订单又写日志又发 MQ），应拆分。

> 💡 **本章深度讲解**：事务是 MySQL 区别于 NoSQL 的核心壁垒。ACID 中，真正理解门槛最高的是隔离级别和 MVCC。记住：InnoDB 默认 RR，靠 MVCC 解决了不可重复读，靠"当前读 + 间隙锁"基本解决幻读。死锁不是 bug，是并发系统的常态——你无法消除它，只能通过"固定加锁顺序 + 短事务 + 重试"来降低它的影响。
>
> 📝 **本章精简总结**：① ACID 由 undo/redo/锁/MVCC 分别保证；② 四种隔离级别逐级收紧；③ InnoDB 默认 RR；④ 快照读走 MVCC，当前读加锁；⑤ 死锁靠固定顺序、短事务、重试解决。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：① 脏读和不可重复读区别？② InnoDB 默认隔离级别？
> - ⭐⭐ **进阶题**：为什么 RC 比 RR 并发性能好？（提示：ReadView 生成时机）。
> - ⭐⭐⭐ **实战题**：设计一个"库存扣减"逻辑，要求在并发下单时不能超卖。提示：用 `UPDATE ... WHERE stock > 0` 乐观锁，或 `SELECT ... FOR UPDATE` 悲观锁，对比两种方案。


---

## 十、视图、存储过程、函数与触发器

### 10.1 视图（VIEW）

**概念解释**：视图是一张"虚拟表"——它不存数据，只存一段 SELECT 定义。每次查询视图时，MySQL 动态执行这段底层 SQL。

**生活化比喻**：视图就像"报表模板"——业务方不用关心你怎么 JOIN 七张表，他们只需要 `SELECT * FROM 月度销售报表`。

```sql
-- 创建视图：用户订单汇总
CREATE OR REPLACE VIEW v_user_order_summary AS
SELECT
  u.id          AS user_id,
  u.username,
  COUNT(o.id)   AS order_cnt,
  IFNULL(SUM(o.total_amount), 0) AS total_amount
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.username;

-- 像查表一样查视图
SELECT * FROM v_user_order_summary WHERE order_cnt > 5 ORDER BY total_amount DESC;

-- 查看视图定义
SHOW CREATE VIEW v_user_order_summary;

-- 删除视图
DROP VIEW IF EXISTS v_user_order_summary;
```

| 优点 | 缺点 |
|------|------|
| 简化复杂查询，对业务方透明 | 视图本身不存储，性能取决于底层 SQL |
| 权限控制：只暴露部分列给某角色 | 视图套视图，调试困难 |
| 逻辑复用：同一套 JOIN 不用写多遍 | 更新视图有限制（含 GROUP BY/聚合不能直接 UPDATE） |

> ❌ **常见坑点**：① 在视图上再套视图，多层嵌套后优化器很难下推过滤条件，慢得离谱。② 误以为视图有缓存——它没有，每次都是实时执行。③ 对含 GROUP BY 的视图做 INSERT/UPDATE 会报错。

### 10.2 存储过程（PROCEDURE）

**概念解释**：存储过程是"预编译并存放在数据库里的一段 SQL 程序"，可以带输入输出参数，被应用直接调用。

```sql
DELIMITER //

CREATE PROCEDURE p_create_order(
  IN  p_user_id    BIGINT,
  IN  p_product_id BIGINT,
  IN  p_quantity   INT,
  OUT p_order_id   BIGINT
)
BEGIN
  -- 声明变量
  DECLARE v_price DECIMAL(12,2);
  DECLARE v_total DECIMAL(12,2);

  -- 查商品价格
  SELECT price INTO v_price FROM products WHERE id = p_product_id;
  SET v_total = v_price * p_quantity;

  -- 扣库存（原子）
  UPDATE products SET stock = stock - p_quantity
  WHERE id = p_product_id AND stock >= p_quantity;

  IF ROW_COUNT() = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '库存不足';
  END IF;

  -- 插订单
  INSERT INTO orders(user_id, total_amount, status)
  VALUES(p_user_id, v_total, 'pending');
  SET p_order_id = LAST_INSERT_ID();
END //

DELIMITER ;
```

```sql
-- 调用存储过程
CALL p_create_order(1001, 2001, 2, @order_id);
SELECT @order_id;   -- 拿到新订单 ID
```

### 10.3 自定义函数（FUNCTION）

```sql
DELIMITER //

CREATE FUNCTION f_age_group(p_age INT)
RETURNS VARCHAR(10)
DETERMINISTIC
BEGIN
  IF p_age < 18 THEN RETURN '未成年';
  ELSEIF p_age < 60 THEN RETURN '成年';
  ELSE RETURN '老年';
  END IF;
END //

DELIMITER ;

-- 在 SELECT 中使用
SELECT username, age, f_age_group(age) AS age_group FROM users;
```

> 🎯 **面试高频**：存储过程 vs 应用层代码？答：存储过程把业务逻辑下沉到 DB，优点是减少网络往返、预编译快；缺点是① 业务逻辑藏在 DB 里，版本管理、测试、跨团队协作困难；② 数据库成为单点，扩展差；③ 调试困难。现代互联网架构**基本弃用存储过程**，逻辑放应用层。

> ❌ **常见坑点**：① 存储过程里写复杂业务循环，一行行调用 UPDATE，性能极差（应该用集合操作）。② 函数未声明 DETERMINISTIC，导致从表/复制时结果不确定。③ 在高并发写场景用存储过程，DB 进程被打满。

### 10.4 触发器（TRIGGER）

**概念解释**：触发器是"在 INSERT/UPDATE/DELETE 前后自动执行的一段 SQL"，常用于审计日志、冗余字段自动维护。

```sql
-- 建审计表
CREATE TABLE users_audit (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT,
  action VARCHAR(20),
  old_value VARCHAR(255),
  new_value VARCHAR(255),
  changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建触发器：users 表更新时记日志
DELIMITER //
CREATE TRIGGER trg_users_after_update
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
  IF OLD.status <> NEW.status THEN
    INSERT INTO users_audit(user_id, action, old_value, new_value)
    VALUES(NEW.id, 'UPDATE_STATUS', OLD.status, NEW.status);
  END IF;
END //
DELIMITER ;
```

```sql
-- 触发验证
UPDATE users SET status = 0 WHERE id = 1001;
SELECT * FROM users_audit WHERE user_id = 1001;
-- 预期：看到一条 action=UPDATE_STATUS 的审计记录
```

> ❌ **常见坑点**：① 触发器逻辑隐式执行，业务方不知道，排查问题时"我没改这个字段它怎么变了"。② 每行触发一次，百万行 UPDATE 会触发百万次 INSERT，性能雪崩。③ 触发器在主从复制时可能因 SQL_MODE 差异表现不一致。现代推荐用 CDC（如 Canal 订阅 binlog）替代触发器做审计。

> 💡 **本章深度讲解**：视图、存储过程、函数、触发器是 MySQL 的"可编程能力"。现代互联网架构的趋势是**能不用就不用**——视图除外（做权限隔离和报表抽象很合适），存储过程和触发器正在被应用层逻辑 + CDC 替代。理解它们的原理有助于读老项目代码，但新项目不要再往这个方向走。
>
> 📝 **本章精简总结**：① 视图是虚拟表，适合权限抽象与报表；② 存储过程把逻辑放 DB，现代已不推荐；③ 函数可在 SELECT 中调用；④ 触发器自动审计，但性能差、隐蔽；⑤ 现代方案：应用层逻辑 + Canal 订阅 binlog。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：视图存数据吗？存储过程和函数区别？
> - ⭐⭐ **进阶题**：为什么大厂新项目基本不用存储过程？从可维护性、扩展性、调试三个角度分析。
> - ⭐⭐⭐ **实战题**：用视图封装"管理员看到的用户列表"，对普通角色只暴露 username/email，不暴露 password_hash。写出 CREATE VIEW 与 GRANT。

---

## 十一、用户权限、备份恢复与 EXPLAIN 性能优化

### 11.1 用户与权限

```sql
-- 创建用户：'用户名'@'主机' 是一个完整身份
CREATE USER 'app'@'%' IDENTIFIED BY 'StrongPass!2026';
CREATE USER 'app'@'10.0.0.%' IDENTIFIED BY 'StrongPass!2026';  -- 限制网段
CREATE USER 'report'@'localhost' IDENTIFIED BY 'Report#2026';

-- 授权：库.表 TO 用户@主机
GRANT SELECT, INSERT, UPDATE ON shop.* TO 'app'@'%';
GRANT RELOAD, PROCESS ON *.* TO 'ops'@'%';
GRANT ALL PRIVILEGES ON shop.* TO 'admin'@'%' WITH GRANT OPTION;

-- 刷新权限
FLUSH PRIVILEGES;

-- 查看权限
SHOW GRANTS FOR 'app'@'%';

-- 撤销权限
REVOKE INSERT ON shop.* FROM 'app'@'%';

-- 修改密码
ALTER USER 'app'@'%' IDENTIFIED BY 'NewPass!2026';

-- 删除用户
DROP USER 'app'@'%';
```

| 权限 | 用途 |
|------|------|
| SELECT / INSERT / UPDATE / DELETE | 业务读写 |
| CREATE / ALTER / DROP | DDL |
| REPLICATION SLAVE | 主从复制从库 |
| PROCESS / SUPER | 运维诊断 |
| ALL PRIVILEGES | 全部（谨慎） |

> ❌ **常见坑点**：① 用 `'root'@'%'` 让 root 从任意主机登录——生产事故标配。② 权限粒度粗：应用账号直接 ALL PRIVILEGES，被脱库时损失巨大。③ `WITH GRANT OPTION` 让被授权者还能再授权，权限失控。密码用 `IDENTIFIED BY PASSWORD '...'` 旧语法在 8.0 已废弃。

### 11.2 备份与恢复

```bash
# 逻辑备份：mysqldump 导出 SQL（最常用）
# 备份单库
mysqldump -uroot -p shop > shop_20260911.sql
# 备份单表
mysqldump -uroot -p shop orders order_items > orders.sql
# 带事务一致性快照（InnoDB）
mysqldump -uroot -p --single-transaction --routines --triggers shop > shop.sql
# 只备份结构不备份数据
mysqldump -uroot -p --no-data shop > schema.sql
```

```bash
# 恢复：把 SQL 灌回去
mysql -uroot -p shop < shop_20260911.sql
# 或在 mysql 客户端里
# mysql> SOURCE /path/to/shop_20260911.sql;
```

```bash
# 物理备份：直接拷贝数据文件（速度快，但要停库或用 LVM/xtrabackup）
# Percona XtraBackup 热备（不停机）
xtrabackup --backup --user=root --password=xxx --target-dir=/backup/full
# 恢复时 prepare + copy-back
```

```mermaid
graph LR
    A[备份策略] --> B[全量备份 每周]
    A --> C[增量/binlog 每日]
    A --> D[恢复演练 每月]
    style A fill:#667eea,color:#fff
    style D fill:#ff6b6b,color:#fff
```

> ✅ **最佳实践**：① 备份必须定期做"恢复演练"，否则备份就是心理安慰；② 备份文件异地存储，防止机房整体故障；③ binlog 必开，用于"时间点恢复"（PITR）；④ 大库用 xtrabackup 物理备份，小库用 mysqldump 逻辑备份。

### 11.3 EXPLAIN 执行计划

**概念解释**：EXPLAIN 让你在真正执行 SQL 之前，先看 MySQL 打算怎么执行——走哪个索引、扫多少行、用什么 JOIN 算法。

```sql
EXPLAIN
SELECT u.username, o.amount
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.status = 1;
```

| 列 | 含义 | 关注 |
|----|------|------|
| id | 查询序号 | 越大越先执行 |
| select_type | 查询类型 | SIMPLE/PRIMARY/SUBQUERY |
| table | 当前表 | - |
| **type** | **访问类型** | system > const > eq_ref > ref > range > index > **ALL（必须避免）** |
| **key** | **实际用的索引** | NULL 表示没用索引 |
| key_len | 索引使用长度 | 判断联合索引用了几列 |
| **rows** | **预估扫描行数** | 越小越好 |
| filtered | 过滤后剩余比例 | - |
| **Extra** | **额外信息** | 避免 Using filesort / Using temporary |

```sql
-- type 等级示例
-- system: 表只有一行
-- const: 主键/唯一索引等值匹配，最多一行
-- eq_ref: JOIN 用主键/唯一索引
-- ref: 普通索引等值匹配
-- range: 索引范围扫描（BETWEEN/IN/>）
-- index: 扫整个索引树（比 ALL 好一点）
-- ALL: 全表扫描（必须优化！）

-- Extra 重点关注
-- Using index: 覆盖索引，好事
-- Using where: 引擎层过滤
-- Using filesort: 额外排序，要优化
-- Using temporary: 用临时表（常见于 GROUP BY），要优化
```

```sql
-- 实战：分析一条慢 SQL
EXPLAIN SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at DESC LIMIT 10;
-- 若 type=ALL、key=NULL → 没走索引
-- 修复：
ALTER TABLE orders ADD INDEX idx_status_created(status, created_at);
-- 再 EXPLAIN：type 应变 ref/range，key 显示 idx_status_created，Extra 无 filesort
```

### 11.4 性能优化清单

> ✅ **八条优化铁律**：
> 1. **避免 SELECT \***：只查需要的列，让覆盖索引生效。
> 2. **小表驱动大表**：JOIN 顺序让小表当驱动表。
> 3. **索引命中**：WHERE/JOIN/ORDER BY 列都要有合适索引。
> 4. **深分页**：用游标分页替代 `LIMIT 100000, 10`。
> 5. **批量写**：用 `INSERT ... VALUES (...),(...),(...)` 一次写多行。
> 6. **事务要短**：不要在事务里做 RPC、慢操作。
> 7. **拆大表**：垂直拆分（按列）、水平拆分（按 user_id 哈希）。
> 8. **读写分离**：写走主库，读走从库（注意主从延迟）。

> ❌ **常见坑点**：① EXPLAIN 的 rows 是"预估"不是"精确"，统计信息过期会导致优化器选错索引；`ANALYZE TABLE` 更新统计信息。② 误以为加了索引就万事大吉——索引也要随业务演进调整，定期 review。③ 把"慢查询"全部归为"加索引"——有时是数据量本身太大，需要缓存或预计算。

> 💡 **本章深度讲解**：权限和备份是"运维能力"，EXPLAIN 是"开发能力"。EXPLAIN 是你和优化器对话的窗口——读懂 type/key/rows/Extra 四列，就能定位 80% 的慢 SQL。备份是"平时不需要，需要时救命"的能力，一定要定期演练。这一章是从"会写 SQL"到"会运维 SQL"的跨越。
>
> 📝 **本章精简总结**：① 权限最小化，禁 root 远程；② mysqldump 逻辑备份 + xtrabackup 物理备份；③ EXPLAIN 看 type（避免 ALL）、key、rows、Extra（避免 filesort/temporary）；④ 优化八条：别 SELECT*、小表驱动、索引命中、游标分页、批量写、短事务、拆表、读写分离。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：① EXPLAIN 中 type=ALL 意味着什么？② mysqldump 怎么备份 InnoDB 不锁表？
> - ⭐⭐ **进阶题**：为什么 `SELECT *` 会阻止覆盖索引生效？改写成什么能触发？
> - ⭐⭐⭐ **实战题**：给你一条慢 SQL `SELECT * FROM orders WHERE status='pending' AND user_id=123 ORDER BY created_at DESC LIMIT 20`，请写 EXPLAIN 分析步骤，并给出最优索引设计。


---

## 十二、与 Python 集成、最佳实践与面试高频

### 12.1 PyMySQL：最基础的连接

```bash
# 安装
pip install pymysql cryptography
```

```python
import pymysql

# 建立连接
conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='app',
    password='StrongPass!2026',
    database='shop',
    charset='utf8mb4',
    autocommit=False,        # 手动事务
    cursorclass=pymysql.cursors.DictCursor  # 行以 dict 返回
)

try:
    with conn.cursor() as cur:
        # 参数化查询：永远不要字符串拼接！防 SQL 注入
        cur.execute(
            "SELECT id, username, email FROM users WHERE id = %s",
            (1001,)
        )
        row = cur.fetchone()
        print(row)
        # 预期：{'id': 1001, 'username': 'alice', 'email': 'a@b.com'}

        # 插入并拿到自增 ID
        cur.execute(
            "INSERT INTO orders(user_id, total_amount, status) VALUES(%s,%s,%s)",
            (1001, 99.90, 'pending')
        )
        new_id = cur.lastrowid
        print(f"new order id = {new_id}")

        # 批量插入
        cur.executemany(
            "INSERT INTO order_items(order_id, product_id, quantity, price) VALUES(%s,%s,%s,%s)",
            [
                (new_id, 2001, 2, 59.90),
                (new_id, 2002, 1, 39.90),
            ]
        )
    conn.commit()
except Exception as e:
    conn.rollback()
    print("回滚：", e)
finally:
    conn.close()
```

> ❌ **常见坑点（SQL 注入）**：
> ```python
> # ❌ 错误：字符串拼接，用户输入 `'; DROP TABLE users; --` 直接脱库
> sql = f"SELECT * FROM users WHERE username = '{username}'"
> cur.execute(sql)
>
> # ✅ 正确：参数化查询，驱动自动转义
> cur.execute("SELECT * FROM users WHERE username = %s", (username,))
> ```

### 12.2 上下文管理器与连接封装

```python
from contextlib import contextmanager
import pymysql
import logging

logger = logging.getLogger(__name__)

@contextmanager
def get_db():
    """业务方用 with 调用，自动 commit/rollback/close"""
    conn = pymysql.connect(
        host='127.0.0.1', user='app', password='StrongPass!2026',
        database='shop', charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        logger.exception("DB 操作失败，已回滚")
        raise
    finally:
        conn.close()

# 使用
with get_db() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM users")
        print(cur.fetchone())
```

### 12.3 SQLAlchemy ORM 简介

```bash
pip install sqlalchemy
```

```python
from sqlalchemy import create_engine, Column, BigInteger, String, Numeric
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id    = Column(BigInteger, primary_key=True, autoincrement=True)
    sku   = Column(String(18), unique=True, nullable=False)
    name  = Column(String(200), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)

engine = create_engine('mysql+pymysql://app:StrongPass!2026@127.0.0.1:3306/shop?charset=utf8mb4')
Session = sessionmaker(bind=engine)

with Session() as s:
    p = Product(sku='SKU000000000000099', name='帽子', price=29.90)
    s.add(p)
    s.commit()

    # 查询
    products = s.query(Product).filter(Product.price < 100).order_by(Product.price.desc()).all()
    for p in products:
        print(p.sku, p.name, p.price)
```

> ❌ **常见坑点**：① ORM 的 lazy loading 在循环里 N+1 查询，性能灾难；用 `joinedload` 预加载。② 忘了 `session.commit()`，数据没落库。③ 长 session 持连接，高并发时连接池耗尽。

### 12.4 连接池：为什么必须用

```python
# 每次请求都 pymysql.connect() 建 TCP + 鉴权，开销 10ms+
# 连接池复用连接，降到亚毫秒
from dbutils.pooled_db import PooledDB

pool = PooledDB(
    creator=pymysql,
    maxconnections=20,    # 池上限
    mincached=5,          # 初始空闲
    blocking=True,        # 满了等待而非报错
    host='127.0.0.1', user='app', password='StrongPass!2026',
    database='shop', charset='utf8mb4',
)

def query_one(sql, args):
    conn = pool.connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(sql, args)
            return cur.fetchone()
    finally:
        conn.close()   # 归还连接，不是真关
```

### 12.5 生产环境最佳实践清单

> ✅ **十条最佳实践**：
> 1. 永远用参数化查询，杜绝 SQL 注入。
> 2. 用连接池，禁止每次新建连接。
> 3. 小事务、短事务，业务逻辑别放事务里。
> 4. 大查询加 `LIMIT`，禁止无 LIMIT 的 `SELECT *` 上生产。
> 5. 索引定期 review（`pt-query-digest` 分析慢日志）。
> 6. 读写分离：报表/搜索走从库，关键写走主库。
> 7. 逻辑删除，物理删除归档到冷存储。
> 8. 分库分表：单表超过 2000 万行就要考虑拆分。
> 9. 监控：慢查询日志、连接数、缓冲池命中率。
> 10. 备份演练：每月恢复一次，验证备份可用。

### 12.6 常见坑点 Top 20

| # | 坑点 | 现象 | 根因 | 解法 |
|---|------|------|------|------|
| 1 | 金额用 FLOAT | 对账差 0.01 元 | 浮点精度 | 改 DECIMAL |
| 2 | 字符集 utf8 存不了 emoji | 插入报截断 | utf8=mb3 | 改 utf8mb4 |
| 3 | UPDATE 忘 WHERE | 全表被改 | 无保护 | 开 SQL_SAFE_UPDATES |
| 4 | 索引失效 | 慢 SQL | 函数/隐式转换/左模糊 | 改写法或建函数索引 |
| 5 | 深分页 | 翻页卡死 | LIMIT 大 OFFSET | 游标分页 |
| 6 | COUNT(*) 慢 | 大表统计超时 | InnoDB 无计数器 | 近似值或计数表 |
| 7 | 幻读 | 范围查询行数变 | RR 隔离下插入 | 当前读 + 间隙锁 |
| 8 | 死锁 | 偶发报错 1213 | 加锁顺序不一致 | 固定顺序 + 重试 |
| 9 | 隐式类型转换 | 手机号查不出 | 字符串列用数字查 | 类型严格一致 |
| 10 | 最左前缀断 | 联合索引用不上 | range 列后断序 | 调整列顺序 |
| 11 | 临时表/filesort | GROUP BY 慢 | 索引未覆盖 | 建覆盖索引 |
| 12 | 主从延迟 | 刚写就读不到 | 异步复制 | 关键读走主库 |
| 13 | 大事务 | 长锁阻塞 | 事务范围过大 | 拆小事务 |
| 14 | N+1 查询 | ORM 循环查询 | lazy loading | joinedload |
| 15 | 连接泄漏 | 连接数打满 | 未 close | 用上下文管理器 |
| 16 | GROUP BY 报错 | 8.0 ONLY_FULL | 非聚合列未分组 | 列都进 GROUP BY 或 ANY_VALUE |
| 17 | 自增 ID 不连续 | 业务方抱怨 | 回滚/删除跳号 | 属正常，别依赖连续 |
| 18 | NULL 比较 | `= NULL` 查不出 | 三值逻辑 | IS NULL |
| 19 | 时间错位 | 跨时区时间变 | TIMESTAMP 时区 | 用 DATETIME |
| 20 | 外键性能差 | 写入慢 | 每次校验引用 | 互联网业务去外键 |

### 12.7 面试高频考点汇总（15 题）

1. **MySQL 索引为什么用 B+ 树而不是 B 树/哈希？**（B+ 树扇出大、范围查询快）
2. **聚簇索引和二级索引区别？什么是回表？**（叶子节点存整行 vs 主键；覆盖索引免回表）
3. **联合索引最左前缀原则？**（从最左列开始，range 后断）
4. **索引失效的场景？**（函数、隐式转换、左模糊、OR、不满足最左）
5. **事务 ACID 及实现机制？**（undo 原子、redo 持久、锁+MVCC 隔离）
6. **四种隔离级别解决哪些并发问题？**（脏读/不可重复读/幻读）
7. **MVCC 原理？RC 与 RR 区别？**（ReadView 生成时机）
8. **InnoDB 默认隔离级别？怎么解决幻读？**（RR；MVCC + 间隙锁）
9. **MySQL 死锁怎么产生？怎么预防？**（交叉加锁；固定顺序、短事务、重试）
10. **EXPLAIN 看哪几列？**（type/key/rows/Extra）
11. **深分页为什么慢？怎么优化？**（游标分页、子查询定位）
12. **CHAR 与 VARCHAR 区别？**（定长补空格 vs 变长）
13. **DATETIME 与 TIMESTAMP 区别？**（范围、时区、字节）
14. **TRUNCATE 与 DELETE 区别？**（DDL vs DML，不可回滚）
15. **MySQL 主从同步原理？主从延迟怎么处理？**（binlog dump → relay log；关键读走主库）

### 12.8 进阶学习路线

```mermaid
graph LR
    A[本文档] --> B[主从复制/读写分离]
    B --> C[分库分表 ShardingSphere]
    C --> D[MySQL 8 新特性]
    D --> E[InnoDB 源码/参数调优]
    style A fill:#43e97b,color:#333
    style C fill:#feca57,color:#333
```

- **主从复制**：binlog 三种格式（STATEMENT/ROW/MIXED）、半同步、并行复制。
- **分库分表**：垂直拆分 vs 水平拆分、分片键选择、分布式 ID（雪花）、分布式事务。
- **MySQL 8.0 新特性**：原子 DDL、隐藏索引、降序索引、CTE、窗口函数。
- **InnoDB 参数调优**：`innodb_buffer_pool_size`（物理内存 50%~70%）、`innodb_log_file_size`、`innodb_flush_log_at_trx_commit`。

> 💡 **本章深度讲解**：从 SQL 到 Python 集成，你完成了"会写 SQL"到"会用 SQL 做产品"的跨越。这一章最重要的三件事：① 参数化查询防注入，② 连接池复用连接，③ ORM 要警惕 N+1。面试高频考点全部来自前九章的底层原理——如果你理解了 B+ 树、MVCC、JOIN 算法，这些题就是送分题。
>
> 📝 **本章精简总结**：① PyMySQL 参数化查询，上下文管理器管理连接；② 连接池必用；③ ORM 警惕 N+1；④ 二十个常见坑点按表过一遍；⑤ 15 个面试题覆盖索引/事务/优化/隔离；⑥ 进阶：主从、分库分表、8.0 新特性。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：① 为什么不能用字符串拼接 SQL？② 连接池解决什么问题？
> - ⭐⭐ **进阶题**：SQLAlchemy 中 N+1 查询是怎么产生的？怎么用 `joinedload` 解决？
> - ⭐⭐⭐ **实战题**：用 Python 实现一个"安全的用户注册函数"：接收 username/email/password，要求①参数化查询防注入；②唯一键冲突时捕获报错并返回友好提示；③密码用 bcrypt 哈希后再入库；④用连接池。给出完整代码。

---

> **结语**：MySQL 的本质是"用关系模型和 SQL 把数据管理复杂性封装起来，用索引和事务在性能与可靠性之间取得平衡"。掌握本文档，你就拿到了后端开发的"数据基座"。从今天起，不要再满足于"能写出正确的 SQL"，要追求"写出高效的 SQL、设计合理的表结构、排查出性能问题"——这才是 MySQL 能力的真正分水岭。


---

## 十三、常用内置函数速查与实战

### 13.1 字符串函数

```sql
-- 拼接
SELECT CONCAT('Hello', ' ', 'World');                 -- Hello World
SELECT CONCAT_WS('-', '2026', '09', '11');            -- 2026-09-11（自动加分隔符）

-- 截取
SELECT SUBSTRING('HelloWorld', 1, 5);                 -- Hello（MySQL 从 1 开始）
SELECT LEFT('HelloWorld', 5);                          -- Hello
SELECT RIGHT('HelloWorld', 5);                         -- World

-- 长度
SELECT LENGTH('你好');          -- 6（utf8mb4 字节数，每汉字3字节）
SELECT CHAR_LENGTH('你好');     -- 2（字符数）

-- 大小写与去空格
SELECT UPPER('hello');          -- HELLO
SELECT LOWER('HELLO');         -- hello
SELECT TRIM('  hi  ');         -- hi
SELECT LTRIM('  hi');           -- hi
SELECT RTRIM('hi  ');           -- hi

-- 替换与查找
SELECT REPLACE('hello world', 'world', 'mysql');       -- hello mysql
SELECT LOCATE('world', 'hello world');                 -- 7（从1开始）
SELECT INSERT('hello', 1, 2, 'xx');                    -- xxllo（从位置1替换2个字符）

-- 填充与格式化
SELECT LPAD('5', 3, '0');       -- 005（左填充到3位）
SELECT RPAD('5', 3, '0');       -- 500
SELECT FORMAT(1234567.891, 2);  -- 1,234,567.89（千分位）
```

### 13.2 日期时间函数

```sql
-- 当前时间
SELECT NOW();                   -- 2026-09-11 14:30:00
SELECT CURDATE();               -- 2026-09-11
SELECT CURTIME();               -- 14:30:00
SELECT SYSDATE();               -- 同 NOW，但取执行瞬间

-- 提取分量
SELECT YEAR(NOW()), MONTH(NOW()), DAY(NOW());
SELECT HOUR(NOW()), MINUTE(NOW()), SECOND(NOW());
SELECT QUARTER(NOW());          -- 季度 1~4
SELECT WEEK(NOW());             -- 一年中的第几周
SELECT DAYOFWEEK(NOW());        -- 星期几（1=周日）
SELECT DAYOFMONTH(NOW());       -- 本月第几天
SELECT DAYOFYEAR(NOW());        -- 本年第几天

-- 加减
SELECT DATE_ADD(NOW(), INTERVAL 7 DAY);
SELECT DATE_ADD(NOW(), INTERVAL -3 MONTH);
SELECT DATE_SUB(NOW(), INTERVAL 1 YEAR);
SELECT ADDDATE('2026-01-31', INTERVAL 1 MONTH);   -- 2026-02-28（自动处理月末）

-- 差
SELECT DATEDIFF('2026-12-31', '2026-01-01');      -- 364（天）
SELECT TIMESTAMPDIFF(MONTH, '2026-01-01', '2026-09-11');  -- 8

-- 格式化
SELECT DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s');
SELECT DATE_FORMAT(NOW(), '%Y年%m月%d日');
SELECT TIME_FORMAT('14:30:00', '%H点%i分');
-- str_to_date 解析字符串为日期
SELECT STR_TO_DATE('2026-09-11 14:30', '%Y-%m-%d %H:%i');
```

```sql
-- 实战：统计本月注册用户数（走 created_at 索引）
SELECT COUNT(*) FROM users
WHERE created_at >= DATE_FORMAT(NOW(), '%Y-%m-01')
  AND created_at <  DATE_ADD(DATE_FORMAT(NOW(), '%Y-%m-01'), INTERVAL 1 MONTH);
```

### 13.3 数值与数学函数

```sql
SELECT ABS(-5);            -- 5
SELECT CEIL(3.2);          -- 4
SELECT FLOOR(3.8);         -- 3
SELECT ROUND(3.14159, 2);  -- 3.14
SELECT TRUNCATE(3.14159, 2);  -- 3.14（不四舍五入）
SELECT MOD(10, 3);         -- 1（取余）
SELECT POWER(2, 10);       -- 1024
SELECT SQRT(16);           -- 4
SELECT RAND();             -- 0~1 随机数
SELECT FLOOR(1 + RAND() * 100);  -- 1~100 随机整数

-- 实战：随机抽 5 个用户
SELECT id, username FROM users
ORDER BY RAND() LIMIT 5;
-- ⚠️ 数据量大时 ORDER BY RAND() 很慢，大数据量建议用主键随机：
SELECT * FROM users WHERE id >= (SELECT FLOOR(RAND() * (SELECT MAX(id) FROM users))) LIMIT 5;
```

### 13.4 条件与流程控制函数

```sql
-- IF：三元
SELECT username, IF(age >= 18, '成年', '未成年') AS stage FROM users;

-- IFNULL：NULL 替换
SELECT username, IFNULL(phone, '未填写') FROM users;

-- COALESCE：第一个非 NULL
SELECT username, COALESCE(phone, email, '无联系方式') FROM users;

-- NULLIF：两值相等返回 NULL
SELECT NULLIF(10, 10);     -- NULL
SELECT NULLIF(10, 20);     -- 10

-- CASE WHEN：多分支
SELECT
  username,
  age,
  CASE
    WHEN age < 18 THEN '未成年'
    WHEN age < 30 THEN '青年'
    WHEN age < 50 THEN '中年'
    ELSE '老年'
  END AS age_group
FROM users;

-- 实战：行转列（每个用户的状态数）
SELECT
  user_id,
  SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END)  AS pending_cnt,
  SUM(CASE WHEN status='paid'    THEN 1 ELSE 0 END)  AS paid_cnt,
  SUM(CASE WHEN status='shipped' THEN 1 ELSE 0 END)  AS shipped_cnt
FROM orders
GROUP BY user_id;
```

### 13.5 聚合与分组辅助函数

```sql
-- GROUP_CONCAT：行转字符串
SELECT user_id, GROUP_CONCAT(DISTINCT status ORDER BY created_at DESC SEPARATOR '→')
FROM orders
GROUP BY user_id;

-- WITH ROLLUP：层级汇总
SELECT status, COUNT(*) FROM orders GROUP BY status WITH ROLLUP;

-- 8.0 窗口函数：排名、环比
SELECT
  username,
  age,
  ROW_NUMBER() OVER (ORDER BY age DESC) AS rn,   -- 1,2,3...
  RANK()       OVER (ORDER BY age DESC) AS rk,   -- 并列同名次，跳号
  DENSE_RANK() OVER (ORDER BY age DESC) AS drk,   -- 并列同名次，不跳号
  LAG(age, 1)  OVER (ORDER BY age)      AS prev_age,
  LEAD(age, 1) OVER (ORDER BY age)      AS next_age
FROM users;
```

> 🎯 **面试高频**：ROW_NUMBER、RANK、DENSE_RANK 区别？答：① ROW_NUMBER 不重复，并列也给不同号；② RANK 并列同名次，下一个跳号（1,1,3）；③ DENSE_RANK 并列同名次，不跳号（1,1,2）。窗口函数是 MySQL 8.0 重点新特性。

> ❌ **常见坑点**：① GROUP_CONCAT 默认 1024 字符截断，长结果要 `SET group_concat_max_len=1048576`。② DATE_FORMAT 大小写敏感：`%m` 是月，`%M` 是月份名；`%i` 是分钟，`%I` 是 12 小时制。③ ORDER BY RAND() 在百万行表上会先全表排序再 LIMIT，慢得离谱。

> 💡 **本章深度讲解**：内置函数是 SQL 的"工具箱"。字符串函数处理清洗、日期函数处理时间窗口、条件函数做行列转换、窗口函数做排名。窗口函数是 8.0 最实用的新特性——以前要写自连接+子查询才能做的排名，现在一行搞定。生产报表场景大量使用。
>
> 📝 **本章精简总结**：① 字符串 CONCAT/SUBSTRING/REPLACE；② 日期 DATE_ADD/DATEDIFF/DATE_FORMAT；③ IF/COALESCE/CASE WHEN；④ 聚合 GROUP_CONCAT；⑤ 窗口函数 ROW_NUMBER/RANK/LAG。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：① DATEDIFF 和 TIMESTAMPDIFF 区别？② CHAR_LENGTH 和 LENGTH 区别？
> - ⭐⭐ **进阶题**：为什么 GROUP_CONCAT 会"静默截断"？怎么避免？
> - ⭐⭐⭐ **实战题**：用窗口函数找出"每个状态下 age 最大的 3 个用户"。提示：RANK() OVER (PARTITION BY status ORDER BY age DESC)。

---

## 十四、电商数据库设计与综合实战

### 14.1 整体 ER 模型

```mermaid
erDiagram
    users ||--o{ orders : places
    users ||--o{ user_address : has
    categories ||--o{ products : contains
    products ||--o{ order_items : "sold as"
    orders ||--|{ order_items : includes
    products ||--o{ product_stock_log : tracks

    users {
        bigint id PK
        varchar username
        varchar email
        tinyint status
    }
    orders {
        bigint id PK
        varchar order_no
        bigint user_id FK
        decimal total_amount
        varchar status
    }
    products {
        bigint id PK
        varchar sku
        varchar name
        decimal price
        int stock
    }
    order_items {
        bigint id PK
        bigint order_id FK
        bigint product_id FK
        int quantity
        decimal price
    }
```

### 14.2 完整建表 SQL

```sql
-- 1. 用户表
CREATE TABLE users (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  username      VARCHAR(50)  NOT NULL COMMENT '登录名',
  nickname      VARCHAR(50)  NOT NULL DEFAULT '',
  email         VARCHAR(100) DEFAULT NULL,
  phone         VARCHAR(20)  DEFAULT NULL,
  password_hash VARCHAR(255) NOT NULL,
  status        TINYINT      NOT NULL DEFAULT 1 COMMENT '1正常 0禁用',
  is_deleted    TINYINT      NOT NULL DEFAULT 0,
  created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_username (username),
  KEY idx_phone (phone),
  KEY idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 收货地址表
CREATE TABLE user_address (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id    BIGINT UNSIGNED NOT NULL,
  receiver   VARCHAR(50)  NOT NULL,
  phone      VARCHAR(20)  NOT NULL,
  province   VARCHAR(20)  NOT NULL,
  city       VARCHAR(20)  NOT NULL,
  detail     VARCHAR(255) NOT NULL,
  is_default TINYINT      NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  KEY idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 分类表
CREATE TABLE categories (
  id       BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name     VARCHAR(50) NOT NULL,
  parent_id BIGINT UNSIGNED NOT NULL DEFAULT 0,
  sort     INT NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  KEY idx_parent (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 商品表
CREATE TABLE products (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  sku         VARCHAR(18)  NOT NULL,
  name        VARCHAR(200) NOT NULL,
  subtitle    VARCHAR(255) NOT NULL DEFAULT '',
  price       DECIMAL(12,2) NOT NULL,
  stock       INT NOT NULL DEFAULT 0,
  category_id BIGINT UNSIGNED NOT NULL,
  status      TINYINT NOT NULL DEFAULT 1 COMMENT '1在售 0下架',
  is_deleted  TINYINT NOT NULL DEFAULT 0,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_sku (sku),
  KEY idx_category (category_id, status),
  KEY idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 订单表
CREATE TABLE orders (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  order_no      VARCHAR(32)  NOT NULL,
  user_id       BIGINT UNSIGNED NOT NULL,
  address_id    BIGINT UNSIGNED NOT NULL,
  total_amount  DECIMAL(12,2) NOT NULL,
  pay_amount    DECIMAL(12,2) NOT NULL DEFAULT 0,
  status        VARCHAR(20)  NOT NULL DEFAULT 'pending'
                COMMENT 'pending/paid/shipping/done/cancelled',
  paid_at       DATETIME DEFAULT NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_deleted    TINYINT NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uk_order_no (order_no),
  KEY idx_user_status (user_id, status),
  KEY idx_status_created (status, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. 订单明细表
CREATE TABLE order_items (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  order_id   BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  sku        VARCHAR(18) NOT NULL,
  name       VARCHAR(200) NOT NULL COMMENT '快照商品名',
  price      DECIMAL(12,2) NOT NULL COMMENT '快照单价',
  quantity   INT NOT NULL,
  PRIMARY KEY (id),
  KEY idx_order (order_id),
  KEY idx_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 14.3 下单事务完整流程

```sql
-- 业务：用户下单，扣库存 + 建订单 + 写明细（必须在一个事务里）
START TRANSACTION;

-- 1. 扣库存（乐观：stock > 0 才扣）
UPDATE products
SET stock = stock - 2
WHERE id = 2001 AND stock >= 2;

-- 库存不足则回滚
-- IF ROW_COUNT() = 0 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='库存不足'; END IF;

-- 2. 建订单
INSERT INTO orders(order_no, user_id, address_id, total_amount, status)
VALUES('20260911143000001', 1001, 501, 119.80, 'pending');
SET @oid = LAST_INSERT_ID();

-- 3. 写明细（商品名/价格快照，防止商品改价后历史订单对不上）
INSERT INTO order_items(order_id, product_id, sku, name, price, quantity)
VALUES(@oid, 2001, 'SKU000000000000001', '纯棉T恤', 59.90, 2);

-- 4. 提交
COMMIT;
```

> ✅ **最佳实践：订单快照**：order_items 中冗余了商品名和单价——商品后来改价/改名后，历史订单仍显示当时的价格。这是电商表设计的"反范式"案例，用空间换一致性。

### 14.4 核心业务查询

```sql
-- 1. 我的订单列表（分页）
SELECT o.order_no, o.total_amount, o.status, o.created_at
FROM orders o
WHERE o.user_id = 1001 AND o.is_deleted = 0
ORDER BY o.created_at DESC
LIMIT 0, 20;

-- 2. 订单详情（订单 + 明细 + 商品）
SELECT o.order_no, o.total_amount, oi.sku, oi.name, oi.price, oi.quantity
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
WHERE o.order_no = '20260911143000001';

-- 3. 后台：今日 GMV 与订单数
SELECT
  COUNT(*)                          AS order_cnt,
  IFNULL(SUM(pay_amount), 0)        AS gmv
FROM orders
WHERE status = 'paid'
  AND paid_at >= CURDATE();

-- 4. 热销商品 Top 10
SELECT p.id, p.name, SUM(oi.quantity) AS sold
FROM order_items oi
JOIN products p ON p.id = oi.product_id
JOIN orders o   ON o.id = oi.order_id
WHERE o.status = 'paid'
  AND o.paid_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY p.id, p.name
ORDER BY sold DESC
LIMIT 10;

-- 5. 用户复购分析：下单 >= 2 次的用户
SELECT user_id, COUNT(*) AS cnt
FROM orders
WHERE status IN ('paid','done')
GROUP BY user_id
HAVING cnt >= 2
ORDER BY cnt DESC;
```

### 14.5 分库分表前瞻

```mermaid
graph LR
    A[orders 单表] -->|数据量超2000万| B[水平分片]
    B --> C[按 user_id 哈希分16片]
    C --> D[orders_0 ... orders_15]
    D --> E[ShardingSphere 路由]
    style A fill:#ff6b6b,color:#fff
    style C fill:#43e97b,color:#333
```

> ❌ **常见坑点**：① 订单表用自增 ID，分库后 ID 冲突——改用雪花算法或号段模式。② 跨分片 JOIN——分片键要选对，尽量让同一用户的订单落在同一分片。③ 非分片键查询（如按 order_no 查）路由到所有分片扫描，慢；可以用"基因法"把 user_id 后缀嵌入 order_no。

> 💡 **本章深度讲解**：电商表设计是 MySQL 综合能力的试金石。一张 orders 表背后牵扯：金额类型（DECIMAL）、订单号唯一（uk_order_no）、状态机（pending→paid→shipping→done）、逻辑删除、订单快照、分库分表。把这一章跑通，你就具备了设计真实业务表的能力。
>
> 📝 **本章精简总结**：① 用户/地址/分类/商品/订单/明细六张核心表；② 下单事务：扣库存→建订单→写明细；③ order_items 冗余商品名价格做快照；④ 常用查询：我的订单、订单详情、GMV、热销 Top、复购分析；⑤ 数据量大了按 user_id 哈希分表。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：① 为什么 order_items 要冗余商品名和价格？② 订单号为什么要建唯一索引？
> - ⭐⭐ **进阶题**：如果用自增 ID 做订单主键，分库分表后会出什么问题？怎么解决？
> - ⭐⭐⭐ **实战题**：设计一个"库存预警"功能——products.stock 低于 10 时，向预警表插一条记录。要求：① 用视图或查询实现；② 不影响下单主流程；③ 给出完整 SQL 与 Python 定时任务调用代码。

---

> **全文结语**：MySQL 基础与 SQL 实战到此结束。回顾全篇：从安装、数据类型、DDL/DML/DQL，到多表 JOIN、索引 B+ 树、事务 MVCC、视图存储过程、权限备份 EXPLAIN，再到 Python 集成、内置函数、电商实战——这 14 章构成了一个后端工程师的"MySQL 闭环"。记住：**SQL 是声明式语言，性能藏在索引和执行计划里，可靠性藏在事务和隔离级别里**。多写 EXPLAIN、多读慢日志、多做备份演练，你就会从"会写 SQL"成长为"能扛生产流量"的数据库工程师。


---

## 十五、存储引擎、锁机制、主从复制与监控

### 15.1 存储引擎对比

```sql
-- 查看当前默认引擎
SHOW ENGINES;
-- 查看表使用的引擎
SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'shop';

-- 建表时指定引擎
CREATE TABLE t_memory (id INT, data VARCHAR(100)) ENGINE=MEMORY;
-- 改引擎（大表谨慎）
ALTER TABLE t_memory ENGINE=InnoDB;
```

| 特性 | InnoDB | MyISAM | Memory |
|------|--------|--------|--------|
| 事务 | ✅ | ❌ | ❌ |
| 外键 | ✅ | ❌ | ❌ |
| 锁粒度 | 行级 | 表级 | 表级 |
| 崩溃恢复 | ✅ | ❌ | ❌ |
| 全文索引 | ✅(5.6+) | ✅ | ❌ |
| 数据存储 | 表空间 ibd | .MYD/.MYI | 内存 |
| 适用 | 通用/OLTP | 已淘汰 | 临时表/缓存 |

> 🎯 **面试高频**：InnoDB 和 MyISAM 区别？答：① InnoDB 支持事务、行锁、外键、崩溃恢复；MyISAM 表锁、无事务、不支持外键，但 COUNT(*) 是 O(1)。MySQL 5.5.5 起默认 InnoDB，MyISAM 基本只在历史项目里见。

### 15.2 锁机制全景

```mermaid
graph TB
    A[MySQL 锁] --> B[全局锁]
    A --> C[表级锁]
    A --> D[行级锁 InnoDB]
    C --> C1[表锁 LOCK TABLES]
    C --> C2[元数据锁 MDL]
    C --> C3[意向锁 IS/IX]
    D --> D1[记录锁 Record Lock]
    D --> D2[间隙锁 Gap Lock]
    D --> D3[Next-Key Lock]
    style A fill:#667eea,color:#fff
    style D fill:#43e97b,color:#333
```

**行锁的三种形态**：

| 锁 | 作用 | 加锁范围 |
|----|------|---------|
| Record Lock | 锁一条索引记录 | 单行 |
| Gap Lock | 锁索引间隙，防插入 | 间隙（不开任何行） |
| Next-Key Lock | Record + Gap | 左开右闭区间 |

```sql
-- 快照读不加锁；当前读加 Next-Key Lock（RR 下）
-- 假设 id 索引上有 10, 20, 30
SELECT * FROM orders WHERE id = 20 FOR UPDATE;
-- 加 Record Lock：锁 id=20

SELECT * FROM orders WHERE id > 15 AND id < 25 FOR UPDATE;
-- 加 Next-Key Lock：锁 (10,20] 和 (20,30) 的左边界
-- 目的：防止别的事务在间隙插入 id=15~25 的新行，导致幻读
```

```sql
-- 意向锁：表级，快速判断表中是否有行被锁
SELECT * FROM users WHERE id = 1 FOR UPDATE;
-- 同时在表上加 IX 意向排他锁，其他事务想加表锁时一眼就知道"里面有行锁"
```

```sql
-- 查看当前锁
SELECT * FROM information_schema.INNODB_TRX;          -- 当前事务
SELECT * FROM performance_schema.data_locks;          -- 8.0 锁详情
SHOW ENGINE INNODB STATUS\G                          -- 死锁日志
```

### 15.3 主从复制原理

```mermaid
graph LR
    M[Master 主库] -->|1.写 binlog| B[(binlog)]
    B -->|2.dump 线程发送| S1[Slave 从库]
    S1 -->|3.relay log| R[(relay log)]
    R -->|4.SQL 线程重放| S2[从库数据]
    style M fill:#ff6b6b,color:#fff
    style S2 fill:#43e97b,color:#333
```

**复制三线程**（从库）：
- **IO 线程**：拉主库 binlog 写到 relay log。
- **SQL 线程**：重放 relay log。
- **并行复制**（5.7+）：按组并行回放，减少延迟。

```sql
-- 主库配置（my.cnf）
-- server-id=1
-- log-bin=mysql-bin
-- binlog-format=ROW
-- 创建复制账号
CREATE USER 'repl'@'%' IDENTIFIED BY 'Repl#2026';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';

-- 从库配置
-- server-id=2
-- relay-log=relay-bin
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='10.0.0.1',
  SOURCE_USER='repl',
  SOURCE_PASSWORD='Repl#2026',
  SOURCE_LOG_FILE='mysql-bin.000001',
  SOURCE_LOG_POS=4;
START REPLICA;
SHOW REPLICA STATUS\G
```

| binlog 格式 | 原理 | 优缺点 |
|-------------|------|--------|
| STATEMENT | 记 SQL 原文 | 日志小，但 NOW()/UUID() 等导致主从不一致 |
| ROW | 记每行变更前后镜像 | 安全，但日志大 |
| MIXED | 混合 | 折中 |

> ✅ **最佳实践**：生产用 `binlog-format=ROW`。主从延迟处理：① 关键读走主库；② 从库只读，避免误写；③ 半同步复制（`rpl_semi_sync_master_enabled`）至少一个从库收到才返回。

### 15.4 慢查询日志与监控

```ini
# my.cnf 开启慢查询日志
slow_query_log = 1
long_query_time = 1           # 超过 1 秒记为慢查询
slow_query_log_file = /var/log/mysql/slow.log
log_queries_not_using_indexes = 1   # 记录没走索引的查询
```

```bash
# 用 mysqldumpslow 分析慢日志（官方自带）
mysqldumpslow -s t -t 10 /var/log/mysql/slow.log
# -s t 按时间排序，-t 10 取前 10 条

# 用 pt-query-digest（Percona Toolkit，更强）
pt-query-digest /var/log/mysql/slow.log | less
```

```sql
-- 实时看当前正在执行的 SQL
SELECT id, user, host, db, command, time, state, info
FROM information_schema.PROCESSLIST
WHERE command != 'Sleep'
ORDER BY time DESC;

-- KILL 慢查询
KILL 12345;
```

### 15.5 关键监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|---------|
| Threads_connected | 当前连接数 | 接近 max_connections |
| Threads_running | 活跃线程数 | > 80 需关注 |
| Innodb_buffer_pool_hit | 缓冲池命中率 | < 99% 警告 |
| Slow_queries | 慢查询数 | 持续上涨告警 |
| Bytes_sent/received | 网络流量 | 突增告警 |
| Open_tables | 打开表数 | 接近 table_open_cache |
| Seconds_behind_master | 主从延迟 | > 10s 告警 |

```sql
SHOW GLOBAL STATUS LIKE 'Threads_running';
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%';
-- 命中率 = 1 - Innodb_buffer_pool_reads / Innodb_buffer_pool_read_requests
SHOW GLOBAL VARIABLES LIKE 'max_connections';
```

> ❌ **常见坑点**：① `max_connections` 默认 151，高并发应用直接打满——调到 500~1000。② 缓冲池命中率不看，磁盘 IO 飙高才发现——`innodb_buffer_pool_size` 设为物理内存 50%~70%。③ 主从延迟没人监控，业务方"刚下单就查不到"投诉。④ 慢查询日志开了但从不分析，日志堆积无人问津——必须用 pt-query-digest 定期 review。

### 15.6 FAQ 高频问题

| 问题 | 答案要点 |
|------|---------|
| 自增 ID 为什么不连续？ | 事务回滚、批量插入失败都会跳号，属正常 |
| COUNT(*) 为什么慢？ | InnoDB 无计数器，要扫索引；大表用近似值 |
| 怎么修改 root 密码？ | `ALTER USER 'root'@'localhost' IDENTIFIED BY '...'` |
| 忘记 root 密码怎么办？ | `--skip-grant-tables` 启动后改密码再重启 |
| 中文乱码怎么排查？ | 库/表/连接三层字符集都要 utf8mb4 |
| 怎么看表碎片？ | `information_schema.TABLES.DATA_FREE` |
| 大表 ALTER 怎么办？ | 8.0 INSTANT 或 gh-ost/pt-online-schema-change |
| 8.0 客户端连不上？ | 默认 caching_sha2_password，旧客户端升级或改插件 |

> 💡 **本章深度讲解**：这一章是从"SQL 开发"到"MySQL 运维"的桥梁。存储引擎决定数据怎么落盘，锁机制决定并发怎么排队，主从复制决定数据怎么复制，慢日志和监控决定你怎么发现问题。面试中问"InnoDB 锁""主从复制""慢查询优化"基本都来自这一章。
>
> 📝 **本章精简总结**：① InnoDB 默认引擎（事务/行锁/外键）；② 行锁分 Record/Gap/Next-Key，RR 下用 Next-Key 防幻读；③ 主从复制三线程，binlog 用 ROW 格式；④ 慢查询日志 + pt-query-digest 定期分析；⑤ 监控连接数、缓冲池命中率、主从延迟。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：① InnoDB 行锁锁在什么上？（索引记录）② 主从复制 binlog 三种格式？
> - ⭐⭐ **进阶题**：为什么 RR 隔离级别下用 `SELECT ... FOR UPDATE` 能防幻读，而普通 SELECT 不能？
> - ⭐⭐⭐ **实战题**：线上突然所有请求变慢，CPU 飙高。请给出排查步骤：① 怎么定位是慢 SQL？② 怎么 KILL 掉？③ 怎么预防？提示：PROCESSLIST + 慢日志 + 索引 review。



### 15.7 常用 SQL 速查表

```sql
-- 库表元信息
SHOW DATABASES;
SHOW TABLES;
SHOW CREATE TABLE users;
DESC users;
SHOW STATUS;
SHOW VARIABLES LIKE 'max_connections';

-- 索引
SHOW INDEX FROM users;
ANALYZE TABLE users;          -- 更新统计信息

-- 进程与锁
SHOW PROCESSLIST;
KILL <id>;
SHOW ENGINE INNODB STATUS;

-- 复制
SHOW MASTER STATUS;
SHOW REPLICA STATUS\G;
```

```sql
-- 建表模板（生产可直接套用）
CREATE TABLE IF NOT EXISTS `{{table}}` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `created_at`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted`  TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除',
  PRIMARY KEY (`id`),
  KEY `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{{注释}}';
```

### 15.8 my.cnf 关键参数模板

```ini
# /etc/my.cnf 生产参考
[mysqld]
# 基础
port = 3306
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
default-storage-engine = InnoDB
max_connections = 1000

# InnoDB
innodb_buffer_pool_size = 4G          # 物理内存 50%~70%
innodb_log_file_size = 1G
innodb_flush_log_at_trx_commit = 1    # 最安全
sync_binlog = 1                       # 与上者合称"双1"，最安全
innodb_flush_method = O_DIRECT

# 慢查询
slow_query_log = 1
long_query_time = 1
log_queries_not_using_indexes = 1

# binlog
server-id = 1
log-bin = mysql-bin
binlog_format = ROW
expire_logs_days = 7
```

### 15.9 一张图总结 MySQL 知识体系

```mermaid
mindmap
  root((MySQL))
    基础
      数据类型
      DDL
      DML
      DQL
    查询
      WHERE
      GROUP BY
      JOIN
      子查询
      UNION
    性能
      B+树索引
      最左前缀
      覆盖索引
      EXPLAIN
      深分页
    可靠性
      事务 ACID
      隔离级别
      MVCC
      锁
      主从复制
    工程
      Python集成
      连接池
      备份恢复
      权限
      监控
```

### 15.10 常见面试场景题详解

**场景题 1：线上一条 UPDATE 把全表改了怎么办？**
答：① 立刻 `STOP` 应用入口；② 如果在事务里，立刻 ROLLBACK；③ 已 COMMIT 的，用 binlog 反向回滚（`mysqlbinlog` 解析出反向 SQL）；④ 从最近备份恢复；⑤ 复盘：为什么没开 `SQL_SAFE_UPDATES`，为什么不加 WHERE。

**场景题 2：数据库 CPU 突然 100% 怎么排查？**
答：① `SHOW PROCESSLIST` 找 Time 长的 SQL；② 慢日志找最近慢查询；③ EXPLAIN 看是否走索引；④ 检查是否有大事务、锁等待；⑤ KILL 紧急慢查询；⑥ 补索引或改 SQL。

**场景题 3：大表加字段导致锁表怎么办？**
答：① MySQL 8.0 用 `ALGORITHM=INSTANT`；② 5.7 用 gh-ost/pt-online-schema-change；③ 业务低峰做；④ 提前压测评估时长。

**场景题 4：主库写、从库读，用户刚下单查不到订单？**
答：主从延迟。方案：① 下单后跳转前强制走主库读一次；② 关键读走主库；③ 半同步复制降低延迟；④ 业务上给"加载中"提示。

**场景题 5：一张 5000 万行的表 COUNT(*) 要 10 秒？**
答：① 业务上用近似值（`EXPLAIN` 估算）；② 维护一张计数表，INSERT/DELETE 时同步 +1/-1；③ 严格 COUNT 走从库；④ 考虑 ClickHouse 等分析库。

### 15.11 字符集与排序规则深入

```sql
-- 查看所有字符集
SHOW CHARACTER SET;
-- 查看排序规则
SHOW COLLATION LIKE 'utf8mb4%';

-- 列级字符集
CREATE TABLE t (
  name VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
);

-- 常见 collation 含义
-- utf8mb4_general_ci    不区分大小写，速度快，校对粗糙
-- utf8mb4_unicode_ci   不区分大小写，校对标准（Unicode）
-- utf8mb4_bin           二进制，区分大小写，按字节比较
```

| 操作 | 用 ci | 用 bin |
|------|-------|--------|
| 用户名登录 | `='Alice'` 与 `='alice'` 视为相同 | 严格区分大小写 |
| 密码 | - | 必须 bin |
| 排序 | 中文按拼音/笔画 | 按字节 |

> ❌ **常见坑点**：JOIN 两表字符集不一致报 `Illegal mix of collations`——统一库/表/连接三层 collation。密码字段必须 bin，否则 `password='ABC'` 和 `password='abc'` 被判相等。

### 15.12 MySQL 8.0 实用新特性

```sql
-- 1. 隐藏索引：先把索引设为不可见，观察一段时间再删
ALTER TABLE users ALTER INDEX idx_old INVISIBLE;
-- 优化器不再使用它，但索引维护仍在；观察无影响后 DROP

-- 2. 降序索引（以前索引都是 ASC，DESC 查询 filesort）
CREATE INDEX idx_created_desc ON orders(created_at DESC);

-- 3. 窗口函数（已在第十三章演示）
SELECT *, ROW_NUMBER() OVER (PARTITION BY status ORDER BY age DESC) rn FROM users;

-- 4. CTE 公用表表达式
WITH recent AS (
  SELECT * FROM orders WHERE created_at >= '2026-09-01'
)
SELECT user_id, COUNT(*) FROM recent GROUP BY user_id;

-- 5. 原子 DDL：DROP TABLE 失败不会残留部分状态
DROP TABLE IF EXISTS a, b, c;
```

> 💡 **本章深度讲解**：这一章把存储引擎、锁、主从、监控、字符集、8.0 新特性串成"运维闭环"。前面章节教你"怎么写 SQL"，这一章教你"怎么跑得稳、出问题救得回"。生产事故 90% 不是 SQL 写错，而是没监控、没备份演练、没慢日志分析、没主从延迟告警。把 15.4~15.6 落到实处，你就超过了一半只会写 CRUD 的后端。
>
> 📝 **本章精简总结**：① InnoDB 默认引擎；② 行锁三形态 Record/Gap/Next-Key；③ 主从复制三线程，binlog 用 ROW；④ 慢日志 + pt-query-digest 定期分析；⑤ 监控连接数、缓冲池命中率、主从延迟；⑥ collation 统一，密码用 bin；⑦ 8.0 隐藏索引、降序索引、CTE、窗口函数。
>
> 🎯 **梯度练习题**：
> - ⭐ **基础题**：① 意向锁解决什么问题？② `innodb_flush_log_at_trx_commit=1` 为什么最安全？
> - ⭐⭐ **进阶题**：Next-Key Lock 在 RR 下如何同时解决"不可重复读"和"幻读"？用一个插入场景说明。
> - ⭐⭐⭐ **实战题**：设计一个 MySQL 监控告警清单，覆盖连接数、慢查询数、缓冲池命中率、主从延迟、磁盘空间五项，每项给出指标来源 SQL 与告警阈值。


### 15.13 分布式 ID 方案

```mermaid
graph LR
    A[分布式ID] --> B[UUID]
    A --> C[数据库号段]
    A --> D[雪花 Snowflake]
    A --> E[Redis INCR]
    D --> D1[时间戳+机器ID+序列号]
    style D fill:#43e97b,color:#333
```

| 方案 | 优点 | 缺点 | 适用 |
|------|------|------|------|
| UUID | 本地生成无依赖 | 太长、无序、做主键索引差 | 非主键 |
| 数据库号段 | 简单、趋势递增 | 依赖 DB | 中小系统 |
| 雪花算法 | 趋势递增、本地生成 | 时钟回拨问题 | 互联网主流 |
| Redis INCR | 原子递增 | 依赖 Redis | 订单号 |

```python
# 雪花算法 Python 简化实现
import time

class Snowflake:
    def __init__(self, machine_id=1):
        self.machine_id = machine_id & 0x3FF      # 10位机器
        self.sequence   = 0
        self.last_ts    = 0

    def next_id(self):
        ts = int(time.time() * 1000)
        if ts == self.last_ts:
            self.sequence = (self.sequence + 1) & 0xFFF
            if self.sequence == 0:
                while ts <= self.last_ts:
                    ts = int(time.time() * 1000)
        else:
            self.sequence = 0
        self.last_ts = ts
        return ((ts - 1288834974657) << 22) | (self.machine_id << 12) | self.sequence

sf = Snowflake(1)
print(sf.next_id())
# 预期：一个 64 位长整数，趋势递增，约 19 位
```

> ❌ **常见坑点**：① 时钟回拨导致雪花 ID 重复——NTP 同步时检测回拨，暂停或换机器。② UUID 做主键导致 B+ 树页分裂频繁，写入慢——趋势递增的 ID 对索引友好。③ 号段模式单点号段库挂了——双号段备用。

### 15.14 分库分表策略详解

| 策略 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| 垂直分库 | 按业务拆库（用户库/订单库） | 业务解耦 | 跨库 JOIN 难 |
| 垂直分表 | 把宽表按列拆冷热 | 单表行变小 | 高频字段仍要 JOIN |
| 水平分表 | 按 user_id 哈希拆 N 张表 | 单表数据量降 | 路由、扩容复杂 |
| 水平分库 | 分表 + 分库 | 分散到多机 | 运维复杂 |

```sql
-- 按 user_id 哈希分 16 张表
-- orders_0 ... orders_15
-- 路由规则：shard = user_id % 16
INSERT INTO orders_3 (order_no, user_id, ...) VALUES (...);

-- 非分片键查询（如按 order_no 查）怎么定位分片？
-- 方案：order_no 内嵌 user_id 基因（低 4 位存 user_id % 16）
-- 从 order_no 算出 shard，直接路由
```

> ✅ **最佳实践**：① 能不分就不分，单表 2000~5000 万行再考虑；② 分片键选最常用的查询维度（user_id）；③ 用 ShardingSphere/Vitess 中间件路由，不要业务代码硬写；④ 全局唯一 ID 用雪花；⑤ 跨片事务用最终一致性（本地消息表 + MQ）。

> ❌ **常见坑点**：① 分片键选错（如按 order_id 分片，但常用按 user_id 查），导致每次全片扫描。② 扩容时数据要 rehash 迁移，停机或双写迁移成本高——一开始就预留足够分片数（如 64/128），先逻辑分、后物理分。③ 跨片 JOIN 性能差，冗余字段或用宽表。

### 15.15 推荐学习资源与 FAQ 补遗

**进阶书单与文档**：
- 《高性能 MySQL》第三版——MySQL 优化圣经。
- 《MySQL 技术内幕：InnoDB 存储引擎》——理解底层实现。
- MySQL 官方手册 dev.mysql.com/doc——最权威。
- 极客时间《MySQL 实战 45 讲》——适合快速入门进阶。

**FAQ 补遗**：

```sql
-- Q：如何批量造测试数据？
-- A：用存储过程递归插
DELIMITER //
CREATE PROCEDURE gen_test_data(IN n INT)
BEGIN
  DECLARE i INT DEFAULT 0;
  WHILE i < n DO
    INSERT INTO users(username, email)
    VALUES(CONCAT('user_', i), CONCAT('user_', i, '@test.com'));
    SET i = i + 1;
  END WHILE;
END //
DELIMITER ;
CALL gen_test_data(100000);
```

```sql
-- Q：如何找出两张表中差异的行？
SELECT a.id FROM a LEFT JOIN b ON a.id = b.id WHERE b.id IS NULL;   -- a有b没有
SELECT b.id FROM a RIGHT JOIN b ON a.id = b.id WHERE a.id IS NULL;  -- b有a没有

-- Q：如何删除重复数据只保留一条？
DELETE u1 FROM users u1 JOIN users u2
WHERE u1.id > u2.id AND u1.email = u2.email;
```

```sql
-- Q：如何查看表大小？
SELECT
  TABLE_NAME,
  ROUND(DATA_LENGTH/1024/1024, 2)  AS data_mb,
  ROUND(INDEX_LENGTH/1024/1024, 2) AS index_mb,
  TABLE_ROWS
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'shop'
ORDER BY DATA_LENGTH DESC;
```



### 15.16 高频 SQL 练习题（附答案）

**练习 1：查询每个部门工资最高的员工**

```sql
-- 表：employees(id, name, dept_id, salary)
SELECT e.name, e.dept_id, e.salary
FROM employees e
JOIN (
  SELECT dept_id, MAX(salary) AS max_sal
  FROM employees GROUP BY dept_id
) t ON e.dept_id = t.dept_id AND e.salary = t.max_sal;

-- 窗口函数写法（更简洁）
SELECT name, dept_id, salary
FROM (
  SELECT *, RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) rk
  FROM employees
) x
WHERE rk = 1;
```

**练习 2：查询第二高的薪水**

```sql
-- 表：salaries(id, salary)
SELECT MAX(salary) AS SecondHighestSalary
FROM salaries
WHERE salary < (SELECT MAX(salary) FROM salaries);

-- 窗口函数写法
SELECT DISTINCT salary
FROM (SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) rk FROM salaries) x
WHERE rk = 2;
```

**练习 3：连续登录 N 天的用户**

```sql
-- 表：login_log(user_id, login_date)
-- 思路：(user_id, login_date - 行号) 相同即连续
SELECT DISTINCT user_id
FROM (
  SELECT user_id, login_date,
         DATE_SUB(login_date,
                  INTERVAL ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) DAY) AS grp
  FROM (SELECT DISTINCT user_id, login_date FROM login_log) d
) x
GROUP BY user_id, grp
HAVING COUNT(*) >= 3;
-- 预期：输出连续登录至少 3 天的用户 ID
```

**练习 4：删除重复邮箱只保留最早一条**

```sql
DELETE e1 FROM emails e1
JOIN emails e2
  ON e1.email = e2.email AND e1.id > e2.id;
-- 预期：每个 email 只保留 id 最小的那行
```

> 💡 这四道题覆盖了"分组取 TopN、排名、连续区间、去重"四类高频面试题型。把窗口函数（RANK/DENSE_RANK/ROW_NUMBER）和"日期减行号找连续区间"的技巧练熟，SQL 笔试基本不会卡壳。

**学习建议**：以上题目建议在本地 MySQL 8.0 容器中亲手敲一遍，配合 EXPLAIN 观察执行计划的变化。刷题平台推荐 LeetCode 数据库题库、牛客 SQL 篇，按"简单→中等→困难"顺序刷满 50 题，SQL 能力会有质的飞跃。同时把本文每章末尾的梯度练习题全部做完，再回看一遍索引与事务两章，就形成了完整的知识闭环。学有余力可以继续深入《高性能 MySQL》《MySQL 技术内幕》，并在真实项目中实践读写分离、分库分表与慢查询治理。记住：数据库能力的天花板不在语法，而在你对存储引擎、优化器、锁与并发的理解深度。愿这份文档成为你后端路上的可靠底座。后续可以结合 Redis、消息队列与分布式事务，构建完整的高并发数据存储体系。至此本文档全部内容结束，祝学习愉快、技术精进、前程似锦，在数据库工程的道路上越走越远。

---

> **全文结语**：MySQL 基础与 SQL 实战到此结束。回顾全篇：从安装、数据类型、DDL/DML/DQL，到多表 JOIN、索引 B+ 树、事务 MVCC、视图存储过程、权限备份 EXPLAIN、Python 集成、内置函数、电商实战、存储引擎锁与主从复制、分布式 ID 与分库分表——这 15 章构成了一个后端工程师的"MySQL 闭环"。记住：**SQL 是声明式语言，性能藏在索引和执行计划里，可靠性藏在事务和隔离级别里**。多写 EXPLAIN、多读慢日志、多做备份演练，你就会从"会写 SQL"成长为"能扛生产流量"的数据库工程师。
