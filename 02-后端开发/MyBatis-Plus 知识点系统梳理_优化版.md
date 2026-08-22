---
title: MyBatis-Plus 知识点系统梳理
tags: [后端, MyBatisPlus, ORM, 数据库]
created: 2026-08-12
updated: 2026-08-12
---

# MyBatis-Plus 知识点系统梳理（优化版）

> **文档说明**：本文档参照《Java知识点完整整合大全》排版风格，系统梳理 MyBatis-Plus 技术栈。包含概述、核心特性、常用用法、注意事项四大模块，辅以动态可视化解析图、深度讲解与精简总结。**优化版**在原有内容基础上，为每个知识点补充了作用、原理、用法的深度解析，并新增了知识点图解。

---

## 1. 概述

MyBatis-Plus（简称 MP）是一个 **MyBatis 的增强工具**，在 MyBatis 的基础上只做增强不做改变，为简化开发、提高效率而生。它由国内团队苞米豆（baomidou）开发维护，是目前国内最流行的 ORM 框架之一。

**核心定位**：
- 只做增强，不做改变：引入 MP 不会影响现有 MyBatis 项目
- 内置通用 Mapper 和通用 Service，单表 CRUD 零 SQL
- 提供代码生成器、分页插件、条件构造器等实用功能

**与 MyBatis 的关系**：

| 对比项 | MyBatis | MyBatis-Plus |
|--------|---------|-------------|
| 单表 CRUD | 需手写 XML/注解 SQL | 继承 BaseMapper 即可，零 SQL |
| 条件查询 | 手写动态 SQL | LambdaQueryWrapper 链式调用 |
| 分页 | 需手写 limit 或插件 | 内置分页插件，自动 count |
| 代码生成 | 无 | 内置代码生成器（AutoGenerator） |
| 学习成本 | 需掌握 XML 映射 | 复用 MyBatis 知识，增量学习 |

---


---
## 2. 核心特性

<div style="background:linear-gradient(135deg,#84fab0,#8fd3f4);border-radius:16px;padding:24px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#1a1a2e;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes mpFlow{0%,100%{transform:scale(1);opacity:.85}50%{transform:scale(1.03);opacity:1}}.mp-feat{display:inline-block;width:30%;vertical-align:top;margin:0 1%;background:rgba(255,255,255,.45);border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:10px;font-size:11px;text-align:center;animation:mpFlow 3s ease-in-out infinite}.mp-feat:nth-child(2){animation-delay:.5s}.mp-feat:nth-child(3){animation-delay:1s}.mp-feat:nth-child(4){animation-delay:1.5s}.mp-feat:nth-child(5){animation-delay:2s}.mp-feat:nth-child(6){animation-delay:2.5s}.mp-icon{font-size:22px;margin-bottom:4px}.mp-name{font-weight:700;font-size:12px;margin-bottom:2px}</style>
<div style="text-align:center;font-size:16px;font-weight:700;margin-bottom:16px;padding-bottom:12px;border-bottom:1.5px solid rgba(0,0,0,.1);letter-spacing:1px">MyBatis-Plus 六大核心特性</div>
<div style="text-align:center">
<div class="mp-feat"><div class="mp-icon">🛡️</div><div class="mp-name">无侵入</div><div style="font-size:9px;opacity:.8">只增强不改变<br>原生MyBatis兼容</div></div>
<div class="mp-feat"><div class="mp-icon">⚡</div><div class="mp-name">损耗小</div><div style="font-size:9px;opacity:.8">启动自动注入<br>CRUD零性能损耗</div></div>
<div class="mp-feat"><div class="mp-icon">🔨</div><div class="mp-name">强大CRUD</div><div style="font-size:9px;opacity:.8">BaseMapper通用Mapper<br>单表操作零SQL</div></div>
<div class="mp-feat"><div class="mp-icon">🔗</div><div class="mp-name">Lambda条件</div><div style="font-size:9px;opacity:.8">LambdaQueryWrapper<br>防误写字段名</div></div>
<div class="mp-feat"><div class="mp-icon">📄</div><div class="mp-name">分页插件</div><div style="font-size:9px;opacity:.8">PaginationInnerInterceptor<br>自动count查询</div></div>
<div class="mp-feat"><div class="mp-icon">🏷️</div><div class="mp-name">通用枚举</div><div style="font-size:9px;opacity:.8">@EnumValue注解<br>数据库映射枚举</div></div>
</div>
</div>

### 2.1 BaseMapper 通用 Mapper

**内置方法**：insert、deleteById、deleteBatchIds、updateById、selectById、selectBatchIds、selectList、selectPage、selectCount 等。

```java
public interface UserMapper extends BaseMapper<User> {
    // 无需写任何方法，自动获得 CRUD 能力
}
```

> 🔍 **知识点深度解析**
>
> **作用**：BaseMapper 是 MP 的核心，继承它就获得单表 CRUD 能力，零 SQL。极大减少样板代码（每个表的 insert/update/delete/select 都不用写）。
>
> **原理**：MP 启动时通过 AutoSqlInjector（ISqlInjector）扫描所有继承 BaseMapper 的接口，根据实体类的 @TableName、@TableId、@TableField 注解解析表名和字段，自动生成对应的 SQL（INSERT、UPDATE、SELECT、DELETE）并注入到 MyBatis 的 MappedStatement 中。运行时调用 BaseMapper 方法时，MyBatis 执行这些自动生成的 SQL。实体类与表的映射：@TableName 指定表名（默认类名驼峰转下划线），@TableId 指定主键（默认 id），@TableField 指定字段映射（默认属性名驼峰转下划线）。
>
> **用法要点**：① Mapper 接口继承 BaseMapper<实体类>，无需写任何方法；② 实体类用 @TableName("表名") 映射表，@TableId(type=IdType.AUTO) 映射主键；③ 字段名默认驼峰转下划线（userName→user_name），全局配置 map-underscore-to-camel-case；④ 非数据库字段用 @TableField(exist=false) 排除；⑤ 自定义复杂查询仍写 XML（MP 不影响原生 MyBatis）；⑥ 批量操作：insertBatchSomeColumn（需 SQL 注入器）、selectBatchIds；⑦ 注意：BaseMapper 的 updateById 只更新非 null 字段（null 字段不更新）。

### 2.2 条件构造器（QueryWrapper / LambdaQueryWrapper）

```java
// QueryWrapper（字符串字段名）
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("age", 18).like("name", "张").orderByDesc("create_time");

// LambdaQueryWrapper（方法引用，类型安全，推荐）
LambdaQueryWrapper<User> lambda = new LambdaQueryWrapper<>();
lambda.eq(User::getAge, 18)
      .like(User::getName, "张")
      .gt(User::getAge, 18)
      .in(User::getStatus, 1, 2)
      .orderByDesc(User::getCreateTime)
      .last("LIMIT 10");

List<User> users = userMapper.selectList(lambda);
```

> 🔍 **知识点深度解析**
>
> **作用**：条件构造器用链式调用构建动态 SQL，替代 MyBatis XML 中的 <if> 标签。LambdaQueryWrapper 用方法引用（User::getName），编译期检查字段名，避免字符串拼写错误。
>
> **原理**：QueryWrapper 维护一个条件片段列表（SqlSegment），每个方法（eq/like/gt/in）向列表添加 SQL 片段（如 age = ?）和参数。执行查询时，MP 将条件片段拼接成 WHERE 子句，参数传给 PreparedStatement。LambdaQueryWrapper 通过 SerializedLambda 解析方法引用（User::getName）对应的字段名（getName→name→user_name），实现类型安全。条件方法支持 null 自动忽略（eq(boolean condition, column, val)，condition 为 false 则不拼接）。
>
> **用法要点**：① 优先用 LambdaQueryWrapper（类型安全，重构友好），不用 QueryWrapper（字符串易拼错）；② 常用条件：eq(等于)、ne(不等)、gt/ge(大于/大于等于)、lt/le、like/likeLeft/likeRight、in、between、isNull、orderByDesc/Asc；③ 动态条件：eq(StringUtils.isNotBlank(name), User::getName, name)（null 自动忽略）；④ .last("LIMIT 10") 追加 SQL 末尾（只能调用一次，有 SQL 注入风险，慎用）；⑤ .select(User::getId, User::getName) 指定查询字段（避免 select *）；⑥ 复杂 OR 嵌套：and(w -> w.eq().or().eq())；⑦ 不要用条件构造器做复杂多表关联查询（用 XML）。

### 2.3 分页插件

```java
@Configuration
public class MybatisPlusConfig {
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        // 分页插件，指定数据库类型
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
        return interceptor;
    }
}

// 使用
Page<User> page = new Page<>(1, 10); // 第1页，每页10条
LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
wrapper.eq(User::getStatus, 1);
Page<User> result = userMapper.selectPage(page, wrapper);

long total = result.getTotal();       // 总记录数
long pages = result.getPages();       // 总页数
List<User> records = result.getRecords(); // 当前页数据
```

> 🔍 **知识点深度解析**
>
> **作用**：分页插件自动实现物理分页（MySQL LIMIT）和 count 查询，不需要手写两条 SQL（一条查数据，一条查总数）。是 MP 最常用的功能之一。
>
> **原理**：PaginationInnerInterceptor 是 MyBatis 拦截器（Interceptor），在 SQL 执行前拦截：① 检测参数中是否有 IPage 对象；② 自动生成 count SQL（在原 SQL 外包 SELECT COUNT(*)）并执行，获取总数；③ 根据数据库类型改写原 SQL 为分页 SQL（MySQL 加 LIMIT offset, size，Oracle 用 ROWNUM，PostgreSQL 用 LIMIT/OFFSET）；④ 执行分页 SQL 获取当前页数据；⑤ 封装到 IPage 对象返回。count SQL 优化：自动去掉 ORDER BY（count 不需要排序），可配置 countSqlParser 优化。
>
> **用法要点**：① 必须配置 PaginationInnerInterceptor（指定 DbType，否则分页不生效）；② Page<T> 作为参数传入 selectPage，返回值也是 Page（包含 total/records/pages）；③ 不需要 count 时用 page.setSearchCount(false)（提升性能）；④ 多表分页查询：在 XML 写 SQL，方法参数加 IPage（MP 自动分页）；⑤ 大表 count 慢：用自定义 count SQL 或缓存总数；⑥ 页码从1开始（不是0）；⑦ 最大分页限制：maxLimit 防止一次查太多（如 maxLimit=500）。

### 2.4 通用 Service（IService / ServiceImpl）

```java
public interface UserService extends IService<User> {
}

@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {
    // 自动获得 save/saveBatch/getById/list/page 等方法
}

// 使用
userService.save(user);                    // 新增
userService.saveBatch(users);              // 批量新增
userService.updateById(user);              // 更新
userService.removeById(id);                // 删除
userService.getById(id);                   // 查询单条
userService.list(wrapper);                 // 查询列表
userService.page(page, wrapper);           // 分页
userService.count(wrapper);                // 计数
```

> 🔍 **知识点深度解析**
>
> **作用**：IService 在 BaseMapper 之上封装了业务层常用方法（批量操作、链式查询、事务等），ServiceImpl 提供默认实现。Service 层继承后无需写基础 CRUD。
>
> **原理**：ServiceImpl 实现了 IService 接口，内部持有 baseMapper（继承的 Mapper），大部分方法委托给 baseMapper 执行。额外提供：批量操作（saveBatch 分批 INSERT，默认每批1000条）、链式查询（lambdaQuery().eq().list()）、链式更新（lambdaUpdate().eq().update()）、事务方法（@Transactional 标注的 tx 方法）。批量插入底层用 JDBC Batch（addBatch/executeBatch），比循环单条插入性能好。
>
> **用法要点**：① Service 接口继承 IService<实体>，实现类继承 ServiceImpl<Mapper, 实体>；② 简单 CRUD 直接用 IService 方法，不需要在 Service 写代码；③ 批量插入 saveBatch 默认每批1000条，可调整（saveBatch(list, 500)）；④ 链式查询：userService.lambdaQuery().eq(User::getStatus,1).list()；⑤ 链式更新：userService.lambdaUpdate().eq(User::getId,id).set(User::getStatus,0).update()；⑥ 复杂业务逻辑在 Service 层写，不要在 Controller 直接调 Mapper；⑦ 注意：ServiceImpl 的方法是 public，不要在实现类中覆盖为 private。

### 2.5 代码生成器（AutoGenerator）

```java
public class CodeGenerator {
    public static void main(String[] args) {
        AutoGenerator generator = new AutoGenerator();
        
        // 数据源配置
        DataSourceConfig dsc = new DataSourceConfig();
        dsc.setUrl("jdbc:mysql://localhost:3306/app");
        dsc.setUsername("root");
        dsc.setPassword("password");
        dsc.setDbType(DbType.MYSQL);
        generator.setDataSource(dsc);
        
        // 包配置
        PackageConfig pc = new PackageConfig();
        pc.setParent("com.example.app");
        pc.setModuleName("user");
        generator.setPackageInfo(pc);
        
        // 策略配置
        StrategyConfig strategy = new StrategyConfig();
        strategy.setInclude("user", "order"); // 要生成的表
        strategy.setNaming(NamingStrategy.underline_to_camel);
        strategy.setColumnNaming(NamingStrategy.underline_to_camel);
        strategy.setEntityLombokModel(true);  // 用 Lombok
        strategy.setRestControllerStyle(true); // @RestController
        generator.setStrategy(strategy);
        
        generator.execute();
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：代码生成器根据数据库表自动生成 Entity、Mapper、Service、Controller 代码，极大减少样板代码。新项目搭架子时特别高效。
>
> **原理**：AutoGenerator 通过 JDBC 连接数据库，读取表结构（DatabaseMetaData 获取表名、字段名、字段类型、注释），根据策略配置（命名转换、Lombok、父类等）用 Velocity/FreeMarker 模板引擎渲染生成 Java 代码文件。生成的 Entity 带 @TableName/@TableId/@TableField 注解和 Lombok @Data，Mapper 继承 BaseMapper，Service 继承 IService，Controller 带基础 CRUD 接口。
>
> **用法要点**：① MP 3.5+ 用 FastAutoGenerator（新 API，更简洁），旧版用 AutoGenerator；② 生成前配置好包名、表名、策略；③ 生成后检查代码，根据业务修改（不要直接用生成的 Controller）；④ 模板可自定义（继承 AbstractTemplateEngine 或修改模板文件）；⑤ 生成的 Entity 用 Lombok @Data（需引入 lombok 依赖）；⑥ 字段注释自动生成 @ApiModelProperty（Swagger）；⑦ 不要反复生成覆盖已修改的代码（生成后手动维护）。

### 2.6 逻辑删除

```yaml
mybatis-plus:
  global-config:
    db-config:
      logic-delete-field: deleted   # 逻辑删除字段
      logic-delete-value: 1         # 删除值
      logic-not-delete-value: 0     # 未删除值
```

```java
@Data
@TableName("user")
public class User {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String name;
    @TableLogic  // 也可注解标注
    private Integer deleted;
}
```

> 🔍 **知识点深度解析**
>
> **作用**：逻辑删除将 DELETE 转为 UPDATE（标记删除状态），保留数据便于恢复和审计。查询自动过滤已删除数据。是业务系统的常用需求。
>
> **原理**：配置 logic-delete-field 后，MP 自动处理：① 查询（select）自动加 WHERE deleted=0（未删除）；② 删除（deleteById/removeById）转为 UPDATE SET deleted=1 WHERE id=?；③ 联合查询的逻辑删除需手动处理（MP 只处理主表）。@TableLogic 注解标注在字段上也可实现（与全局配置二选一）。逻辑删除的字段不会出现在 INSERT 和 UPDATE 的字段中（自动排除）。
>
> **用法要点**：① 全局配置后所有表都要有 deleted 字段，或用 @TableLogic 注解单独标注；② 查询自动过滤已删除，不需要手动加 WHERE deleted=0；③ 需要查已删除数据时用自定义 SQL（XML 或 @Select）；④ 物理删除用自定义 SQL（MP 的 delete 都是逻辑删除）；⑤ 唯一索引要包含 deleted 字段（否则逻辑删除后不能再插入相同唯一键）；⑥ 逻辑删除字段不要在业务代码中手动修改；⑦ 注意：MP 的 count/list/page 都自动过滤已删除。

### 2.7 自动填充（MetaObjectHandler）

```java
@Component
public class MyMetaObjectHandler implements MetaObjectHandler {
    @Override
    public void insertFill(MetaObject metaObject) {
        this.strictInsertFill(metaObject, "createTime", LocalDateTime.class, LocalDateTime.now());
        this.strictInsertFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
        this.strictInsertFill(metaObject, "createBy", Long.class, SecurityUtils.getCurrentUserId());
    }
    
    @Override
    public void updateFill(MetaObject metaObject) {
        this.strictUpdateFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
        this.strictUpdateFill(metaObject, "updateBy", Long.class, SecurityUtils.getCurrentUserId());
    }
}

// 实体类字段标注
@TableField(fill = FieldFill.INSERT)
private LocalDateTime createTime;
@TableField(fill = FieldFill.INSERT_UPDATE)
private LocalDateTime updateTime;
```

> 🔍 **知识点深度解析**
>
> **作用**：自动填充在 insert/update 时自动设置公共字段（createTime、updateTime、createBy、updateBy），不需要业务代码手动设置。是审计字段的标准实现。
>
> **原理**：MetaObjectHandler 是 MP 的扩展点，insertFill 在 INSERT 前调用，updateFill 在 UPDATE 前调用。通过 MetaObject（对象元数据，类似反射但更高效）设置字段值。@TableField(fill=FieldFill.INSERT/INSERT_UPDATE) 标注需要自动填充的字段。strictInsertFill/strictUpdateFill 是严格模式（字段有值则不覆盖，null 才填充），setFieldValByName 是直接覆盖。
>
> **用法要点**：① 实现 MetaObjectHandler 并注册为 @Component；② 实体类字段用 @TableField(fill=FieldFill.INSERT) 或 INSERT_UPDATE 标注；③ 常用字段：createTime（INSERT）、updateTime（INSERT_UPDATE）、createBy（INSERT）、updateBy（INSERT_UPDATE）；④ strict 模式：字段有值时不覆盖（业务手动设置了就用业务值）；⑤ 自动填充只在 MP 的 insert/update 方法生效，自定义 XML SQL 不生效；⑥ 获取当前用户 ID：从 SecurityContext 或 ThreadLocal 获取；⑦ 注意：updateById 的自动填充需要实体对象有值（null 字段不更新也不填充）。

---


---
## 3. 常用用法

### 3.1 实体类定义

```java
@Data
@TableName("sys_user")
public class User {
    @TableId(type = IdType.AUTO)
    private Long id;
    
    @TableField("username")
    private String username;
    
    private String password;  // 自动映射 password
    
    @TableField(exist = false)
    private String token;     // 非数据库字段
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
    
    @TableLogic
    private Integer deleted;
}
```

> 🔍 **知识点深度解析**
>
> **作用**：实体类是 MP 的映射基础，注解控制表名、主键、字段映射、自动填充、逻辑删除。正确定义实体类是 MP 正常工作的前提。
>
> **原理**：MP 通过反射读取实体类注解构建表结构元数据（TableInfo）。@TableName 指定表名（默认类名驼峰转下划线：SysUser→sys_user）。@TableId 指定主键，IdType.AUTO（数据库自增）、ASSIGN_ID（雪花算法，MP默认）、INPUT（手动输入）、ASSIGN_UUID。@TableField 指定字段映射，exist=false 表示非数据库字段（查询时不包含）。fill 指定自动填充时机。@TableLogic 标记逻辑删除字段。
>
> **用法要点**：① 表名与类名不一致时用 @TableName；② 主键策略：数据库自增用 IdType.AUTO，分布式 ID 用 ASSIGN_ID（雪花算法，默认）；③ 字段名默认驼峰转下划线，不需要每个字段加 @TableField；④ 非数据库字段必须加 @TableField(exist=false)（否则查询报错）；⑤ 用 Lombok @Data 减少 getter/setter 样板；⑥ 敏感字段（password）查询时用 .select() 排除或用 @TableField(select=false)；⑦ 日期用 LocalDateTime（Java 8+，比 Date 好）。

### 3.2 增删改查

```java
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserMapper userMapper;
    
    // 新增
    public void create(User user) {
        userMapper.insert(user);  // 主键自动回填
    }
    
    // 更新（非 null 字段更新）
    public void update(User user) {
        userMapper.updateById(user);
    }
    
    // 条件更新
    public void updateStatus(Long id, Integer status) {
        LambdaUpdateWrapper<User> wrapper = new LambdaUpdateWrapper<>();
        wrapper.eq(User::getId, id).set(User::getStatus, status);
        userMapper.update(null, wrapper);
    }
    
    // 删除（逻辑删除）
    public void delete(Long id) {
        userMapper.deleteById(id);
    }
    
    // 查询单条
    public User getById(Long id) {
        return userMapper.selectById(id);
    }
    
    // 条件查询列表
    public List<User> listByStatus(Integer status) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getStatus, status).orderByDesc(User::getCreateTime);
        return userMapper.selectList(wrapper);
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：基础 CRUD 是 MP 最常用的操作。insert 后主键自动回填，updateById 只更新非 null 字段，条件构造器构建动态查询。
>
> **原理**：insert 时 MP 根据实体类非 null 字段生成 INSERT SQL（INSERT INTO table (col1, col2) VALUES (?, ?)），主键回填用 JDBC getGeneratedKeys。updateById 生成 UPDATE SET col1=? WHERE id=?（只包含非 null 字段，null 字段不更新）。deleteById 生成 DELETE（或逻辑删除 UPDATE）。selectById 生成 SELECT * FROM table WHERE id=?。条件构造器的方法最终拼接成 WHERE 子句。
>
> **用法要点**：① insert 后实体对象的主键字段自动有值（可直接 user.getId()）；② updateById 只更新非 null 字段（要更新为 null 需用 LambdaUpdateWrapper.set()）；③ 条件更新用 LambdaUpdateWrapper（不需要实体对象）；④ 查询一条用 selectOne（结果多于一条报错，用 last("LIMIT 1")）；⑤ 批量查询用 selectBatchIds（IN 查询）；⑥ 不要 select *（用 .select() 指定字段，减少 IO）；⑦ 复杂查询（多表/子查询）用 XML，不要硬套条件构造器。

### 3.3 分页查询

```java
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserMapper userMapper;
    
    public Page<UserVO> page(Integer pageNum, Integer pageSize, String keyword) {
        Page<User> page = new Page<>(pageNum, pageSize);
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(StringUtils.isNotBlank(keyword), User::getUsername, keyword)
               .eq(User::getStatus, 1)
               .orderByDesc(User::getCreateTime);
        
        Page<User> result = userMapper.selectPage(page, wrapper);
        
        // 转换为 VO
        Page<UserVO> voPage = new Page<>(pageNum, pageSize, result.getTotal());
        voPage.setRecords(result.getRecords().stream()
            .map(this::toVO).collect(Collectors.toList()));
        return voPage;
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：分页查询是列表接口的标准实现。MP 自动处理 count 和 limit，业务代码只需要构建条件。
>
> **原理**：selectPage(IPage, Wrapper) 被 PaginationInnerInterceptor 拦截：先执行 count SQL（SELECT COUNT(*) FROM table WHERE ...）获取总数，再执行分页 SQL（SELECT * FROM table WHERE ... LIMIT offset, size）。Page 对象包含 current（当前页）、size（每页条数）、total（总数）、pages（总页数）、records（数据列表）。offset = (current-1)*size。
>
> **用法要点**：① 页码从1开始（Page(1, 10) 是第一页）；② 动态条件用 boolean 参数（like(condition, column, val)）；③ 返回 VO 不要直接返回 Entity（脱敏、字段过滤）；④ 不需要总数时 page.setSearchCount(false)（性能优化）；⑤ 大表分页深翻页慢（LIMIT 100000,10），用游标分页或 id 范围查询；⑥ 排序字段要加索引（ORDER BY create_time 需要 create_time 索引）；⑦ 多表分页：XML 写 SQL，方法参数加 IPage（MP 自动拦截分页）。

### 3.4 自定义 SQL（XML）

```java
// Mapper 接口
public interface UserMapper extends BaseMapper<User> {
    // 注解方式（简单 SQL）
    @Select("SELECT u.*, d.dept_name FROM sys_user u LEFT JOIN sys_dept d ON u.dept_id=d.id WHERE u.id=#{id}")
    UserDetailVO selectDetailById(@Param("id") Long id);
    
    // XML 方式（复杂 SQL）
    Page<UserVO> selectUserPage(Page<UserVO> page, @Param("keyword") String keyword);
}
```

```xml
<!-- UserMapper.xml -->
<select id="selectUserPage" resultType="com.example.app.vo.UserVO">
    SELECT u.id, u.username, d.dept_name
    FROM sys_user u
    LEFT JOIN sys_dept d ON u.dept_id = d.id
    <where>
        u.deleted = 0
        <if test="keyword != null and keyword != ''">
            AND u.username LIKE CONCAT('%', #{keyword}, '%')
        </if>
    </where>
    ORDER BY u.create_time DESC
</select>
```

> 🔍 **知识点深度解析**
>
> **作用**：MP 不替代 MyBatis 的自定义 SQL，复杂查询（多表关联、子查询、聚合）仍用 XML 或注解。MP 与原生 MyBatis 完全兼容。
>
> **原理**：继承 BaseMapper 的 Mapper 接口可以同时定义自定义方法，MP 自动注入通用方法，自定义方法按 MyBatis 原生方式解析（@Select 注解或 XML 映射）。XML 文件放在 mapper-locations 配置的路径下（默认 classpath*:/mapper/**/*.xml）。自定义分页查询：方法参数加 IPage（或 Page），MP 的分页插件自动拦截并添加 LIMIT 和 count。
>
> **用法要点**：① 简单单表用 BaseMapper + 条件构造器，复杂多表用 XML；② XML 中逻辑删除要手动加 WHERE deleted=0（MP 不处理自定义 SQL）；③ 自定义分页：方法第一个参数是 IPage，MP 自动分页；④ 参数用 @Param 标注（多参数时必须）；⑤ resultType 用 VO（不要返回 Map，可读性差）；⑥ 动态 SQL 用 <if>/<where>/<foreach>（MyBatis 原生）；⑦ XML 文件名与 Mapper 接口名一致（UserMapper.xml ↔ UserMapper.java）。

### 3.5 批量操作

```java
// 批量插入（IService）
userService.saveBatch(userList);           // 默认每批1000
userService.saveBatch(userList, 500);      // 每批500

// 批量更新（IService）
userService.updateBatchById(userList);

// 自定义批量插入（性能更好，需 SQL 注入器）
public interface UserMapper extends BaseMapper<User> {
    int insertBatchSomeColumn(List<User> list);
}

// 使用
userMapper.insertBatchSomeColumn(userList);  // 单条 INSERT 多值
```

> 🔍 **知识点深度解析**
>
> **作用**：批量操作比循环单条操作性能好很多（减少网络往返和事务开销）。saveBatch 是 IService 提供的，insertBatchSomeColumn 是真正的批量 INSERT（单条 SQL 多值）。
>
> **原理**：saveBatch 底层是循环调用 insert（每批在一个事务中），不是真正的批量 SQL，但比循环单条（每次一个事务）性能好。insertBatchSomeColumn 通过 SQL 注入器（InsertBatchSomeColumn）生成 INSERT INTO table (col1,col2) VALUES (?,?),(?,?),(?,?) 单条 SQL 多值，性能最好。MySQL 的批量 INSERT 受 max_allowed_packet 限制（默认4MB，大数据量需分批）。
>
> **用法要点**：① 简单批量用 saveBatch（IService 自带）；② 高性能批量用 insertBatchSomeColumn（需配置 SQL 注入器）；③ 批量大小：500-1000 条/批（太多可能超 max_allowed_packet）；④ 批量操作要在事务中（@Transactional）；⑤ 批量插入后主键回填：insertBatchSomeColumn 支持主键回填；⑥ 批量更新用 updateBatchById（循环更新，不是批量 SQL）；⑦ 大数据量导入用 JDBC Batch 或 Load Data（性能更好）。

### 3.6 多数据源

```java
@Configuration
public class DataSourceConfig {
    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.master")
    public DataSource masterDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean
    @ConfigurationProperties("spring.datasource.slave")
    public DataSource slaveDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean
    public DynamicDataSource dynamicDataSource(DataSource master, DataSource slave) {
        Map<Object, Object> map = new HashMap<>();
        map.put("master", master);
        map.put("slave", slave);
        DynamicDataSource ds = new DynamicDataSource();
        ds.setTargetDataSources(map);
        ds.setDefaultTargetDataSource(master);
        return ds;
    }
}

// 使用 @DS 注解切换（dynamic-datasource-spring-boot-starter）
@DS("slave")
public List<User> listFromSlave() {
    return userMapper.selectList(null);
}
```

> 🔍 **知识点深度解析**
>
> **作用**：多数据源用于读写分离、分库、多业务库。dynamic-datasource 是 MP 官方推荐的多数据源框架，用 @DS 注解切换。
>
> **原理**：DynamicDataSource 继承 AbstractRoutingDataSource，通过 determineCurrentLookupKey() 决定当前用哪个数据源。@DS 注解通过 AOP 在方法前设置数据源 key（ThreadLocal），方法后清除。读写分离：写操作走 master，读操作走 slave。@DS 可以标注在类或方法上，方法优先于类。事务中数据源切换要注意（事务内数据源在事务开始时确定，中间切换不生效）。
>
> **用法要点**：① 用 dynamic-datasource-spring-boot-starter（MP 官方，配置简单）；② @DS("数据源名") 标注在 Service 方法或类上；③ 读写分离：读方法 @DS("slave")，写方法默认 master；④ 事务中不要切换数据源（@Transactional 内 @DS 不生效）；⑤ 多数据源事务用 @DSTransactional（dynamic-datasource 提供）；⑥ 数据源配置：spring.datasource.dynamic.master/slave；⑦ 注意：Mapper 是单例，数据源切换通过 ThreadLocal（请求隔离）。

### 3.7 性能优化

```java
// 1. 查询指定字段（避免 select *）
LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
wrapper.select(User::getId, User::getUsername, User::getEmail)
       .eq(User::getStatus, 1);

// 2. 流式查询（大数据量，避免 OOM）
userMapper.selectList(new QueryWrapper<User>().last("LIMIT 100000"), 
    resultContext -> {
        User user = resultContext.getResultObject();
        // 逐条处理
    });

// 3. 只查 count（不需要数据）
long count = userMapper.selectCount(wrapper);

// 4. 分页关闭 count（不需要总数时）
Page<User> page = new Page<>(1, 10);
page.setSearchCount(false);
```

> 🔍 **知识点深度解析**
>
> **作用**：MP 性能优化包括减少查询字段、避免大结果集 OOM、减少不必要的 count 查询。合理优化能显著提升接口性能。
>
> **原理**：select 指定字段生成 SELECT id, username, email 而非 SELECT *，减少网络传输和内存占用。流式查询（selectList with ResultHandler）使用 JDBC 流式结果集（fetchSize=-2 for MySQL），逐条处理不加载到内存，避免大结果集 OOM。selectCount 生成 SELECT COUNT(*)，比 selectList 后 size() 高效（不传输数据）。setSearchCount(false) 跳过 count 查询，只查分页数据（用于不需要总数的滚动加载场景）。
>
> **用法要点**：① 列表查询用 .select() 指定需要的字段（不要 select *）；② 大数据量导出用流式查询（ResultHandler）或分页分批处理；③ 只判断存在用 selectCount 或 selectOne(last("LIMIT 1"))；④ 不需要总数的分页（如无限滚动）setSearchCount(false)；⑤ 条件查询字段加索引（eq/like 的字段）；⑥ 避免在循环中查询数据库（N+1 问题，用批量查询或 JOIN）；⑦ 慢 SQL 用 p6spy 打印实际 SQL 和耗时。

### 3.8 常见问题排查

```bash

> 🔍 **知识点深度解析**
>
> **作用**：汇总 MyBatis-Plus 开发中的常见问题及解决方案，提升排错效率。
>
> **原理**：常见问题：① 字段不对应（驼峰映射未开启或字段名不匹配，检查 map-underscore-to-camel-case 和 @TableField）；② 逻辑删除不生效（未配置 logic-delete-field 或注解）；③ 分页不生效（未配置 MybatisPlusInterceptor 分页插件）；④ 主键策略错误（@TableId type 设为 IdType.AUTO/ASSIGN_ID）；⑤ 批量插入慢（saveBatch 本质是循环单条，真正批量用 rewriteBatchedStatements=true）。
>
> **用法要点**：① 分页必须配置 MybatisPlusInterceptor + PaginationInnerInterceptor  ② map-underscore-to-camel-case 默认开启，字段不匹配检查 @TableField  ③ 逻辑删除需配置 logic-delete-field 和 logic-delete-value  ④ JDBC URL 加 rewriteBatchedStatements=true 让批量插入真正合并  ⑤ 面试常考：分页插件原理、逻辑删除实现、批量插入优化

# 1. 打印 SQL（开发环境）
mybatis-plus:
  configuration:
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl

# 2. 生产用 p6spy 格式化 SQL
# 3. 分页不生效：检查是否配置 PaginationInnerInterceptor
# 4. 逻辑删除不生效：检查全局配置或 @TableLogic 注解
# 5. 自动填充不生效：检查 @TableField(fill=...) 和 MetaObjectHandler 注册
```

> 🔍 **知识点深度解析**
>
> **作用**：MP 问题排查是开发必备技能。常见问题有分页不生效、逻辑删除不生效、自动填充不生效、SQL 报错等。快速定位能节省时间。
>
> **原理**：分页不生效最常见原因是没配置 PaginationInnerInterceptor（MP 3.4+ 用 MybatisPlusInterceptor，旧版用 PaginationInterceptor）。逻辑删除不生效：全局配置的字段名与实体类字段不一致，或实体类没该字段。自动填充不生效：@TableField(fill) 没加，或 MetaObjectHandler 没注册为 Bean，或 updateById 时字段为 null（null 不更新也不填充）。SQL 报错：字段名映射错误（exist=false 漏加）、表名错误（@TableName）、关键字冲突（用 @TableField 加反引号）。
>
> **用法要点**：① 开发环境开启 SQL 日志（log-impl: StdOutImpl），看实际执行的 SQL；② 分页不生效：检查 MybatisPlusInterceptor + PaginationInnerInterceptor 配置；③ 逻辑删除：全局配置 logic-delete-field 或字段加 @TableLogic；④ 自动填充：字段加 @TableField(fill=FieldFill.INSERT)，实现类加 @Component；⑤ updateById null 字段不更新：用 LambdaUpdateWrapper.set() 强制更新；⑥ 关键字冲突：@TableField("`order`") 加反引号；⑦ 生产用 p6spy 格式化 SQL（带参数和耗时），不要用 StdOutImpl（性能差）。

---


---
## 4. 注意事项

1. **updateById 只更新非 null 字段**：null 字段不会被更新。要更新为 null 用 LambdaUpdateWrapper.set(column, null)。

2. **分页插件必须配置**：MP 3.4+ 用 MybatisPlusInterceptor + PaginationInnerInterceptor，不配置则分页不生效（返回全部数据）。

3. **逻辑删除的唯一索引**：逻辑删除后相同唯一键不能再插入。唯一索引要包含 deleted 字段（如 UNIQUE(username, deleted)）。

4. **自动填充只对 MP 方法生效**：自定义 XML SQL 不会自动填充，需要手动设置或在 XML 中处理。

5. **LambdaQueryWrapper 序列化**：方法引用（User::getName）必须可序列化，实体类实现 Serializable（MP 实体类默认实现）。

6. **大表分页深翻页**：LIMIT 100000,10 很慢。用游标分页（WHERE id > lastId ORDER BY id LIMIT 10）或 id 范围查询。

7. **事务中切换数据源不生效**：@Transactional 内数据源在事务开始时确定，@DS 切换不生效。用 @DSTransactional。

8. **批量插入大小限制**：MySQL max_allowed_packet 默认 4MB，批量插入数据量大时需分批或调大参数。

9. **selectOne 结果多于一条报错**：用 .last("LIMIT 1") 或确保条件唯一。

10. **代码生成器版本**：MP 3.5+ 用 FastAutoGenerator（新 API），旧版 AutoGenerator 已废弃。

11. **多表查询逻辑删除**：MP 只自动处理主表逻辑删除，关联表需手动加 WHERE deleted=0。

12. **性能监控**：生产用 p6spy 或 Druid 监控慢 SQL，及时优化索引和查询。

---

> 💡 **深度讲解**：MyBatis-Plus 是 MyBatis 的增强工具，核心价值是单表 CRUD 零 SQL。BaseMapper 提供通用 CRUD，IService 封装业务层常用方法，条件构造器（LambdaQueryWrapper）用类型安全的链式调用构建动态 SQL，分页插件自动处理 count 和物理分页。原理上，MP 启动时通过 ISqlInjector 扫描 BaseMapper 接口，根据实体类注解（@TableName/@TableId/@TableField）自动生成 SQL 并注入 MyBatis。条件构造器维护 SQL 片段列表，执行时拼接成 WHERE 子句。分页插件是 MyBatis Interceptor，拦截 SQL 自动加 count 和 LIMIT。高级特性包括逻辑删除（DELETE 转 UPDATE）、自动填充（createTime/updateTime）、代码生成器（根据表生成代码）、多数据源（@DS 切换）。使用时注意：updateById 只更新非 null 字段、分页插件必须配置、逻辑删除唯一索引要含 deleted 字段、大表深翻页优化、自定义 SQL 不自动处理逻辑删除和填充。MP 不替代 MyBatis，复杂多表查询仍用 XML，两者完全兼容。
>
> **📝 精简总结**：MP=MyBatis增强，单表CRUD零SQL；核心=BaseMapper(通用CRUD)+IService(业务层封装)+LambdaQueryWrapper(类型安全条件)+PaginationInnerInterceptor(分页)；原理=启动时自动生成SQL注入MyBatis+拦截器分页；高级=逻辑删除(@TableLogic)+自动填充(MetaObjectHandler)+代码生成器+多数据源(@DS)；注意=updateById非null更新/分页必须配置/逻辑删除唯一索引/大表深翻页/自定义SQL不自动填充。

---

> 📋 **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 知识点深度解析」模块（作用+原理+用法要点），原有内联图已统一风格化美化（圆角、阴影、渐变、动画）。所有原有内容完整保留，未做任何修改。
