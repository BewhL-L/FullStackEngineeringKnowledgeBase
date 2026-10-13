---
title: Spring事务管理与传播机制
tags: [Spring, 事务管理, 传播机制, 隔离级别, 声明式事务, 分布式事务]
category: 后端开发
created: 2026-09-07
updated: 2026-09-07
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: [[SpringBoot实战]], [[数据库设计范式与ER建模]]
aliases: [Spring事务, 事务传播机制, @Transactional]
---

> Spring事务管理是企业级开发的核心能力，通过声明式事务（@Transactional）将事务管理与业务代码解耦。理解传播机制、隔离级别、回滚规则是正确使用Spring事务的基础，也是面试高频考点。
>
> **核心问题**：7种传播行为的适用场景、事务失效的常见原因、分布式事务方案。

---

## 一、概述：Spring事务管理体系

### 1.1 事务的ACID特性

| 特性 | 说明 | 实现方式 |
|------|------|---------|
| 原子性(Atomicity) | 事务中所有操作要么全部成功，要么全部失败 | 回滚机制（undo log） |
| 一致性(Consistency) | 事务执行前后数据保持一致状态 | 约束+索引+原子性+隔离性 |
| 隔离性(Isolation) | 并发事务之间互不干扰 | 锁机制+MVCC |
| 持久性(Durability) | 事务提交后数据永久保存 | redo log + 刷盘 |

### 1.2 Spring事务管理架构

```
Spring事务管理
├── 平台事务管理器（PlatformTransactionManager）
│   ├── DataSourceTransactionManager    — JDBC/MyBatis
│   ├── HibernateTransactionManager     — Hibernate
│   ├── JpaTransactionManager           — JPA
│   └── JtaTransactionManager           — JTA分布式事务
├── 事务定义（TransactionDefinition）
│   ├── 传播行为（Propagation）— 7种
│   ├── 隔离级别（Isolation）— 5种
│   ├── 超时时间（Timeout）
│   └── 只读标志（readOnly）
└── 事务状态（TransactionStatus）
    └── 当前事务运行状态（是否新事务、是否仅回滚等）
```

### 1.3 声明式事务 vs 编程式事务

| 维度 | 声明式（@Transactional） | 编程式（TransactionTemplate） |
|------|--------------------------|-------------------------------|
| 代码侵入 | 低，注解即可 | 高，需手动管理 |
| 灵活性 | 低，方法级 | 高，代码块级 |
| 适用场景 | 大多数业务场景 | 复杂事务逻辑、细粒度控制 |
| 性能 | 略有AOP开销 | 直接调用，开销小 |

---

## 二、底层原理：AOP代理与传播机制

### 2.1 @Transactional实现原理

```
调用方 → 代理对象（CGLIB/JDK动态代理）
              ↓
         事务拦截器（TransactionInterceptor）
              ↓
         事务管理器获取事务（getTransaction）
              ↓
         目标方法执行
              ↓
         成功 → commit / 异常 → rollback
```

**关键**：@Transactional只对public方法生效，且必须通过代理对象调用（同类内调用不生效）。

### 2.2 7种传播行为

| 传播行为 | 说明 | 适用场景 |
|---------|------|---------|
| REQUIRED（默认） | 有事务则加入，无则新建 | 大多数业务方法 |
| REQUIRES_NEW | 总是新建事务，挂起当前事务 | 日志记录、独立操作 |
| SUPPORTS | 有事务则加入，无则非事务执行 | 查询方法 |
| NOT_SUPPORTED | 非事务执行，挂起当前事务 | 不需要事务的操作 |
| MANDATORY | 必须在事务中执行，否则抛异常 | 被事务方法调用的内部方法 |
| NEVER | 必须非事务执行，否则抛异常 | 不允许事务的操作 |
| NESTED | 嵌套事务（保存点），外层回滚则内层回滚 | 子操作可独立回滚 |

### 2.3 传播行为示例

```java
@Service
public class OrderService {

    @Transactional(propagation = Propagation.REQUIRED)
    public void createOrder(Order order) {
        // 1. 创建订单（当前事务）
        orderMapper.insert(order);
        // 2. 扣减库存（REQUIRES_NEW：独立事务，即使订单回滚库存也不回滚）
        inventoryService.deduct(order.getProductId(), order.getQuantity());
        // 3. 记录日志（REQUIRES_NEW：日志必须持久化）
        logService.record("CREATE_ORDER", order.getId());
    }
}

@Service
public class InventoryService {
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void deduct(Long productId, int quantity) {
        // 独立事务，不受外层事务回滚影响
        inventoryMapper.updateStock(productId, quantity);
    }
}
```

### 2.4 隔离级别

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 性能 |
|---------|------|-----------|------|------|
| READ_UNCOMMITTED | ✅ | ✅ | ✅ | 最高 |
| READ_COMMITTED（Oracle默认） | ❌ | ✅ | ✅ | 高 |
| REPEATABLE_READ（MySQL默认） | ❌ | ❌ | ✅(MVCC解决) | 中 |
| SERIALIZABLE | ❌ | ❌ | ❌ | 最低 |

```java
@Transactional(isolation = Isolation.READ_COMMITTED)
public void transfer(String from, String to, BigDecimal amount) {
    // 读已提交：避免脏读，允许不可重复读
}
```

---

## 三、实操：正确使用@Transactional

### 3.1 基础用法

```java
@Service
public class UserService {

    @Autowired
    private UserMapper userMapper;
    @Autowired
    private AccountMapper accountMapper;

    /**
     * 注册用户并初始化账户
     * 默认传播行为REQUIRED，默认隔离级别跟随数据库
     * 默认只对RuntimeException和Error回滚
     */
    @Transactional(rollbackFor = Exception.class)
    public void register(User user) {
        // 1. 创建用户
        userMapper.insert(user);
        // 2. 初始化账户（如果失败，整个事务回滚）
        Account account = new Account();
        account.setUserId(user.getId());
        account.setBalance(BigDecimal.ZERO);
        accountMapper.insert(account);
    }
}
```

### 3.2 回滚规则配置

```java
// 对所有异常回滚（推荐）
@Transactional(rollbackFor = Exception.class)

// 指定回滚异常
@Transactional(rollbackFor = {SQLException.class, BusinessException.class})

// 指定不回滚的异常
@Transactional(noRollbackFor = BusinessException.class)

// 只读事务（查询优化，提示数据库优化）
@Transactional(readOnly = true)

// 超时设置（秒）
@Transactional(timeout = 30)
```

### 3.3 事务失效的常见原因

```java
@Service
public class OrderService {

    // ❌ 失效原因1：方法非public
    @Transactional
    private void createOrder() { }

    // ❌ 失效原因2：同类内调用（this调用不走代理）
    public void outerMethod() {
        this.innerMethod(); // 事务不生效！
    }
    @Transactional
    public void innerMethod() { }

    // ✅ 解决：注入自身或通过AopContext
    @Autowired
    private OrderService self; // 注入代理对象

    public void outerMethodFixed() {
        self.innerMethod(); // 事务生效
    }

    // ❌ 失效原因3：异常被catch吞掉
    @Transactional
    public void methodWithCatch() {
        try {
            // 业务操作
        } catch (Exception e) {
            e.printStackTrace(); // 异常被捕获，事务不回滚！
        }
    }

    // ✅ 解决：catch后重新抛出或手动回滚
    @Transactional
    public void methodWithCatchFixed() {
        try {
            // 业务操作
        } catch (Exception e) {
            // 方式1：重新抛出
            throw new RuntimeException(e);
            // 方式2：手动标记回滚
            // TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
        }
    }

    // ❌ 失效原因4：rollbackFor配置错误（默认只回滚RuntimeException）
    @Transactional // 只对RuntimeException回滚，IOException不回滚！
    public void methodWithCheckedException() throws IOException {
        throw new IOException("IO异常");
    }
}
```

### 3.4 编程式事务（TransactionTemplate）

```java
@Service
public class ComplexService {

    @Autowired
    private TransactionTemplate transactionTemplate;

    public void complexOperation() {
        // 第一段事务
        transactionTemplate.execute(status -> {
            // 操作A
            return null;
        });

        // 非事务操作

        // 第二段事务（独立）
        transactionTemplate.execute(status -> {
            // 操作B
            return null;
        });
    }

    // 带返回值
    public Order createWithReturn() {
        return transactionTemplate.execute(status -> {
            Order order = new Order();
            orderMapper.insert(order);
            return order;
        });
    }
}
```

---

## 四、常见问题与排查

### 4.1 事务不回滚排查清单

```
1. 检查方法是否为public
2. 检查是否通过代理对象调用（非this调用）
3. 检查异常类型是否在rollbackFor范围内
4. 检查异常是否被catch吞掉
5. 检查数据库引擎是否为InnoDB（MyISAM不支持事务）
6. 检查是否被final方法/类修饰（CGLIB无法代理）
7. 检查Spring是否扫描到该类（@Service注解）
8. 检查是否多数据源且事务管理器配置错误
```

### 4.2 大事务问题

**现象**：事务执行时间长，持有锁时间长，导致并发性能下降。

**优化方案**：
```java
// ❌ 大事务：查询+更新+远程调用都在一个事务中
@Transactional
public void bigTransaction() {
    List<User> users = userMapper.selectAll(); // 长查询
    for (User user : users) {
        remoteService.notify(user); // 远程调用（慢）
        userMapper.update(user);
    }
}

// ✅ 优化：事务外做查询和远程调用，事务内只做更新
public void optimized() {
    // 事务外：查询+远程调用
    List<User> users = userMapper.selectAll();
    List<User> toUpdate = new ArrayList<>();
    for (User user : users) {
        remoteService.notify(user);
        toUpdate.add(user);
    }
    // 事务内：批量更新（短事务）
    batchUpdate(toUpdate);
}

@Transactional
public void batchUpdate(List<User> users) {
    userMapper.batchUpdate(users);
}
```

### 4.3 分布式事务

| 方案 | 一致性 | 性能 | 适用场景 |
|------|--------|------|---------|
| 2PC/XA | 强一致 | 低 | 金融核心、跨库事务 |
| TCC | 最终一致 | 中 | 可补偿业务 |
| 本地消息表 | 最终一致 | 高 | 异步解耦 |
| Saga | 最终一致 | 高 | 长事务编排 |
| Seata AT | 最终一致 | 中 | 微服务架构（推荐） |

```java
// Seata AT模式示例
@GlobalTransactional(name = "create-order", rollbackFor = Exception.class)
public void createOrder(Order order) {
    // 跨服务事务：订单服务 + 库存服务 + 账户服务
    orderService.create(order);
    inventoryService.deduct(order.getProductId(), order.getQuantity());
    accountService.debit(order.getUserId(), order.getAmount());
}
```

---

## 五、进阶与最佳实践

### 5.1 事务最佳实践

- [ ] 总是指定 `rollbackFor = Exception.class`
- [ ] 事务方法尽量短，避免大事务
- [ ] 查询方法使用 `readOnly = true`
- [ ] 避免在事务中做远程调用、消息发送
- [ ] 同类内调用需注入自身代理
- [ ] 批量操作使用编程式事务控制提交点
- [ ] 高并发场景考虑乐观锁替代悲观锁
- [ ] 分布式事务优先考虑最终一致性（消息队列），强一致用Seata

### 5.2 事务监控

```yaml
# Spring Boot Actuator + 事务监控
management:
  endpoints:
    web:
      exposure:
        include: health,metrics,transactions
  endpoint:
    transactions:
      enabled: true
```

关键监控指标：
- 事务提交/回滚比率
- 事务平均执行时间
- 慢事务TOP N
- 死锁次数

---

## 关联笔记

- [[SpringBoot实战]] — Spring Boot基础
- [[数据库设计范式与ER建模]] — 数据库设计
- [[事务隔离级别与MVCC]] — 事务隔离原理
- [[分布式事务]] — 分布式事务方案
- [[线上故障排查手册]] — 故障排查
