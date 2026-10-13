---
title: SpringCache 缓存抽象
tags: [后端, 缓存, Cache, 原子笔记]
category: 后端开发
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["SpringBoot-自动装配原理", "Redis数据结构与应用场景"]
aliases: [SpringCache-缓存抽象]
---

# SpringCache 缓存抽象

> **文档说明**：系统讲解 Spring Cache 抽象层的核心概念、注解使用（@Cacheable/@CachePut/@CacheEvict/@Caching）、缓存管理器配置（Redis/Caffeine/Ehcache/Guava）、缓存键生成策略、条件缓存、缓存同步与一致性、缓存穿透/击穿/雪崩解决方案，以及生产级缓存最佳实践和常见问题排查。
>
> **适用人群**：后端开发工程师、全栈开发者、需要在 Spring 项目中使用缓存的开发者
>
> **前置知识**：[[SpringBoot-自动装配原理]]、[[Redis数据结构与应用场景]]、[[高并发系统设计案例]]

---

## 一、概述

**Spring Cache** 是 Spring 框架提供的缓存抽象层，它不是具体的缓存实现，而是一套统一的缓存 API 和注解，通过简单的注解即可为方法添加缓存能力，底层可切换不同的缓存实现（Redis、Caffeine、Ehcache 等）。

### 1. 核心思想

Spring Cache 的核心是**基于 AOP 的方法级缓存**：在方法调用前检查缓存，命中则直接返回缓存结果，不命中则执行方法并将结果存入缓存。开发者只需添加注解，不需编写缓存读写的样板代码。

**解决的问题**：
- 缓存读写代码重复，散落在各处
- 切换缓存实现需要修改大量代码
- 缓存键、过期时间、条件等管理混乱
- 缓存与数据库一致性难以保证

### 2. 为什么需要缓存

| 缓存收益 | 说明 |
|---------|------|
| **提升性能** | 减少数据库查询，内存访问比磁盘快 100-1000 倍 |
| **降低数据库压力** | 热点数据缓存，减少数据库 QPS |
| **提升并发能力** | 缓存可支撑更高并发，数据库成为瓶颈时缓存兜底 |
| **降低成本** | 减少数据库资源消耗，可能降低硬件成本 |

**缓存适用场景**：
- 读多写少的热点数据（商品信息、用户信息、配置数据）
- 计算成本高的结果（复杂查询、聚合计算、AI 模型推理结果）
- 短时间内重复请求的数据（排行榜、统计数据）

**缓存不适用场景**：
- 写多读少，数据频繁变化
- 对数据一致性要求极高（金融交易、库存扣减）
- 数据量小且查询快（缓存开销大于收益）

### 3. Spring Cache 架构

```mermaid
graph TB
    subgraph 应用层
        A[业务方法<br/>@Cacheable/@CachePut/@CacheEvict]
    end

    subgraph Spring Cache 抽象层
        B[CacheInterceptor<br/>AOP 拦截器]
        C[CacheManager<br/>缓存管理器]
        D[KeyGenerator<br/>键生成器]
        E[CacheResolver<br/>缓存解析器]
    end

    subgraph 缓存实现层
        F[Redis Cache]
        G[Caffeine Cache]
        H[Ehcache Cache]
        I[ConcurrentMap Cache]
    end

    A -->|AOP 拦截| B
    B -->|获取/操作| C
    C -->|创建/管理| F
    C -->|创建/管理| G
    C -->|创建/管理| H
    C -->|创建/管理| I
    B -->|生成键| D
    B -->|解析缓存| E
```

| 组件 | 说明 |
|------|------|
| **CacheInterceptor** | AOP 拦截器，拦截带缓存注解的方法 |
| **CacheManager** | 缓存管理器，创建和管理 Cache 实例 |
| **Cache** | 缓存接口，定义缓存操作（get/put/evict/clear） |
| **KeyGenerator** | 缓存键生成器，默认使用方法参数生成 |
| **CacheResolver** | 缓存解析器，解析方法使用的缓存名称 |

---

## 二、核心注解详解

### 1. @Cacheable（查询缓存）

**最常用的注解**，方法调用前检查缓存，命中则返回缓存值，不命中则执行方法并缓存结果。

```java
@Service
public class UserService {

    // 基础用法：缓存名称为 user，键为方法参数 id
    @Cacheable("user")
    public User getUserById(Long id) {
        // 方法逻辑（查询数据库）
        return userRepository.findById(id);
    }

    // 指定多个缓存名称
    @Cacheable({"user", "userCache"})
    public User getUserById(Long id) { ... }

    // 自定义键（使用 SpEL）
    @Cacheable(value = "user", key = "#id")
    public User getUserById(Long id) { ... }

    // 复合键
    @Cacheable(value = "user", key = "#id + '_' + #type")
    public User getUser(Long id, String type) { ... }

    // 条件缓存（满足条件才缓存）
    @Cacheable(value = "user", key = "#id", condition = "#id > 0")
    public User getUserById(Long id) { ... }

    // 条件不缓存（unless 条件满足则不缓存）
    @Cacheable(value = "user", key = "#id", unless = "#result == null")
    public User getUserById(Long id) { ... }

    // 同步缓存（多线程同时访问时只执行一次方法）
    @Cacheable(value = "user", key = "#id", sync = true)
    public User getUserById(Long id) { ... }
}
```

**@Cacheable 属性说明**：

| 属性 | 说明 | 示例 |
|------|------|------|
| `value`/`cacheNames` | 缓存名称（必填） | `"user"` |
| `key` | 缓存键（SpEL 表达式） | `"#id"` |
| `condition` | 缓存条件（满足才缓存） | `"#id > 0"` |
| `unless` | 不缓存条件（满足则不缓存） | `"#result == null"` |
| `sync` | 同步模式（防止缓存击穿） | `true` |
| `keyGenerator` | 自定义键生成器 | `"myKeyGenerator"` |
| `cacheManager` | 指定缓存管理器 | `"redisCacheManager"` |
| `cacheResolver` | 指定缓存解析器 | `"myCacheResolver"` |

### 2. @CachePut（更新缓存）

方法始终执行，并将结果更新到缓存。用于更新操作，确保缓存与数据库一致。

```java
@Service
public class UserService {

    // 更新用户信息，同时更新缓存
    @CachePut(value = "user", key = "#user.id")
    public User updateUser(User user) {
        return userRepository.save(user);
    }

    // 条件更新
    @CachePut(value = "user", key = "#user.id", condition = "#user.id != null")
    public User updateUser(User user) { ... }
}
```

**注意**：
- `@CachePut` 方法**始终执行**，不会检查缓存
- `@CachePut` 和 `@Cacheable` 应使用**相同的缓存名称和键**，才能更新同一个缓存
- `@CachePut` 的返回值会存入缓存，方法必须有返回值

### 3. @CacheEvict（清除缓存）

清除缓存，用于删除操作或数据变更后使缓存失效。

```java
@Service
public class UserService {

    // 删除用户，同时清除缓存
    @CacheEvict(value = "user", key = "#id")
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }

    // 清除整个缓存（所有键）
    @CacheEvict(value = "user", allEntries = true)
    public void clearAllCache() { ... }

    // 方法执行前清除缓存（默认方法执行后清除）
    @CacheEvict(value = "user", key = "#id", beforeInvocation = true)
    public void deleteUser(Long id) { ... }
}
```

**@CacheEvict 属性**：

| 属性 | 说明 | 默认值 |
|------|------|--------|
| `allEntries` | 是否清除整个缓存（所有键） | `false` |
| `beforeInvocation` | 是否在方法执行前清除 | `false`（方法执行后） |

### 4. @Caching（组合注解）

组合多个缓存注解，用于一个方法需要多种缓存操作的场景。

```java
@Service
public class UserService {

    // 同时操作多个缓存
    @Caching(
        cacheable = {
            @Cacheable(value = "user", key = "#id")
        },
        put = {
            @CachePut(value = "userByName", key = "#result.name", condition = "#result != null")
        },
        evict = {
            @CacheEvict(value = "userList", allEntries = true)
        }
    )
    public User getUserById(Long id) { ... }
}
```

### 5. @CacheConfig（类级配置）

在类级别统一配置缓存名称、键生成器等，避免每个方法重复配置。

```java
@Service
@CacheConfig(cacheNames = "user", keyGenerator = "myKeyGenerator")
public class UserService {

    // 继承类级配置，不需再写 cacheNames
    @Cacheable(key = "#id")
    public User getUserById(Long id) { ... }

    @CachePut(key = "#user.id")
    public User updateUser(User user) { ... }

    @CacheEvict(key = "#id")
    public void deleteUser(Long id) { ... }
}
```

---

## 三、SpEL 键表达式

Spring Cache 使用 SpEL（Spring Expression Language）生成缓存键。

### 1. 常用 SpEL 表达式

| 表达式 | 说明 | 示例 |
|--------|------|------|
| `#参数名` | 方法参数 | `#id`、`#user.id` |
| `#p0`/`#a0` | 第 N 个参数（索引从0） | `#p0`、`#a0` |
| `#result` | 方法返回值（仅 @CachePut/@Cacheable 的 unless） | `#result.id` |
| `#root.method` | 方法对象 | `#root.method.name` |
| `#root.target` | 目标对象 | `#root.target.class` |
| `#root.args` | 方法参数数组 | `#root.args[0]` |
| `#root.caches` | 缓存集合 | `#root.caches[0].name` |
| 字符串拼接 | `+` 拼接 | `#id + '_' + #type` |
| 方法调用 | 调用对象方法 | `#user.getName()` |
| 条件判断 | 三元表达式 | `#id > 0 ? #id : 'default'` |

### 2. 键生成示例

```java
// 简单键
@Cacheable(value = "user", key = "#id")
// → 缓存键：1

// 复合键
@Cacheable(value = "user", key = "#id + '_' + #type")
// → 缓存键：1_admin

// 方法名+参数（避免不同方法键冲突）
@Cacheable(value = "user", key = "#root.methodName + ':' + #id")
// → 缓存键：getUserById:1

// 对象属性
@Cacheable(value = "user", key = "#user.id")
public User createUser(User user) { ... }

// 条件键
@Cacheable(value = "user", key = "#id", condition = "#id > 0")
```

### 3. 自定义 KeyGenerator

```java
@Component("myKeyGenerator")
public class MyKeyGenerator implements KeyGenerator {
    @Override
    public Object generate(Object target, Method method, Object... params) {
        // 生成格式：类名:方法名:参数1_参数2
        StringBuilder sb = new StringBuilder();
        sb.append(target.getClass().getSimpleName()).append(":");
        sb.append(method.getName()).append(":");
        sb.append(StringUtils.arrayToDelimitedString(params, "_"));
        return sb.toString();
    }
}

// 使用
@Cacheable(value = "user", keyGenerator = "myKeyGenerator")
public User getUserById(Long id) { ... }
// → 缓存键：UserService:getUserById:1
```

---

## 四、缓存管理器配置

### 1. Redis 缓存（最常用）

```xml
<!-- Maven 依赖 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-cache</artifactId>
</dependency>
```

```yaml
# application.yaml
spring:
  cache:
    type: redis
    redis:
      time-to-live: 3600000       # 缓存过期时间（毫秒），默认不过期
      key-prefix: "cache:"         # 键前缀
      use-key-prefix: true         # 是否使用前缀
      cache-null-values: false     # 是否缓存 null 值（防穿透）
      enable-statistics: true      # 启用统计
  data:
    redis:
      host: localhost
      port: 6379
      password: your-password
      database: 0
      lettuce:
        pool:
          max-active: 8
          max-idle: 8
          min-idle: 0
```

```java
// 自定义 RedisCacheManager（不同缓存不同过期时间）
@Configuration
@EnableCaching
public class RedisCacheConfig {

    @Bean
    public CacheManager cacheManager(RedisConnectionFactory factory) {
        // 默认配置
        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofHours(1))
            .serializeKeysWith(RedisCacheSerializationPair.fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(RedisCacheSerializationPair.fromSerializer(new GenericJackson2JsonRedisSerializer()))
            .disableCachingNullValues();

        // 不同缓存的特殊配置
        Map<String, RedisCacheConfiguration> cacheConfigurations = new HashMap<>();
        cacheConfigurations.put("user", defaultConfig.entryTtl(Duration.ofMinutes(30)));
        cacheConfigurations.put("product", defaultConfig.entryTtl(Duration.ofHours(2)));
        cacheConfigurations.put("config", defaultConfig.entryTtl(Duration.ofDays(1)));

        return RedisCacheManager.builder(factory)
            .cacheDefaults(defaultConfig)
            .withInitialCacheConfigurations(cacheConfigurations)
            .transactionAware()  // 事务感知
            .build();
    }
}
```

### 2. Caffeine 缓存（本地高性能缓存）

Caffeine 是 Java 高性能本地缓存库，Guava Cache 的改进版，适合单机应用或作为 Redis 的二级缓存。

```xml
<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>caffeine</artifactId>
</dependency>
```

```yaml
spring:
  cache:
    type: caffeine
    caffeine:
      spec: maximumSize=10000,expireAfterWrite=3600s,recordStats
```

```java
@Configuration
@EnableCaching
public class CaffeineCacheConfig {

    @Bean
    public CacheManager cacheManager() {
        CaffeineCacheManager manager = new CaffeineCacheManager();
        manager.setCaffeine(Caffeine.newBuilder()
            .maximumSize(10000)
            .expireAfterWrite(Duration.ofHours(1))
            .expireAfterAccess(Duration.ofMinutes(30))
            .recordStats()
        );
        return manager;
    }
}
```

### 3. 多级缓存（Caffeine + Redis）

```java
// 自定义多级缓存：先查本地 Caffeine，再查 Redis
public class MultiLevelCache implements Cache {
    private final Cache localCache;   // Caffeine
    private final Cache remoteCache;  // Redis

    @Override
    public ValueWrapper get(Object key) {
        // 先查本地
        ValueWrapper result = localCache.get(key);
        if (result != null) return result;
        // 再查远程
        result = remoteCache.get(key);
        if (result != null) {
            localCache.put(key, result.get());  // 回填本地
        }
        return result;
    }

    @Override
    public void put(Object key, Object value) {
        localCache.put(key, value);
        remoteCache.put(key, value);
    }

    @Override
    public void evict(Object key) {
        localCache.evict(key);
        remoteCache.evict(key);
    }
    // ... 其他方法
}
```

### 4. 缓存实现对比

| 实现 | 类型 | 性能 | 持久化 | 分布式 | 适用场景 |
|------|------|------|--------|--------|---------|
| **ConcurrentMap** | 本地 | 极高 | ❌ | ❌ | 开发测试、简单缓存 |
| **Caffeine** | 本地 | 极高 | ❌ | ❌ | 单机应用、二级缓存 |
| **Guava Cache** | 本地 | 高 | ❌ | ❌ | 遗留项目（推荐迁移 Caffeine） |
| **Ehcache** | 本地/分布式 | 高 | ✅ | ⚠️ | 需要持久化的本地缓存 |
| **Redis** | 远程 | 高 | ✅ | ✅ | 分布式系统、生产环境首选 |
| **Hazelcast** | 分布式 | 中 | ✅ | ✅ | 嵌入式分布式缓存 |
| **Memcached** | 远程 | 高 | ❌ | ✅ | 简单 KV 缓存（功能少） |

---

## 五、缓存三大问题与解决方案

### 1. 缓存穿透

**问题**：查询一个不存在的数据，缓存不命中，请求直接打到数据库，恶意攻击者利用这个漏洞大量查询不存在的数据，压垮数据库。

**解决方案**：

| 方案 | 说明 | 优缺点 |
|------|------|--------|
| **缓存空值** | 查询结果为 null 也缓存，设置较短过期时间 | 简单有效，但可能缓存无效数据 |
| **布隆过滤器** | 查询前用布隆过滤器判断数据是否存在，不存在直接返回 | 高效，但有一定误判率 |
| **参数校验** | 对请求参数进行合法性校验，拦截明显非法请求 | 简单，但不能完全防止 |

```java
// 方案1：缓存空值（Spring Cache 配置）
@Cacheable(value = "user", key = "#id", unless = "#result == null")
// 注意：unless = "#result == null" 表示不缓存 null，要缓存 null 需去掉 unless
// 并配置 cache-null-values: true

// 方案2：布隆过滤器
@Service
public class UserService {
    @Autowired
    private BloomFilter<Long> userBloomFilter;  // 启动时加载所有用户ID

    @Cacheable(value = "user", key = "#id")
    public User getUserById(Long id) {
        // 布隆过滤器判断是否可能存在
        if (!userBloomFilter.mightContain(id)) {
            return null;  // 一定不存在，直接返回
        }
        return userRepository.findById(id);
    }
}
```

### 2. 缓存击穿

**问题**：某个热点 Key 过期的瞬间，大量并发请求同时打到数据库，导致数据库压力骤增。

**解决方案**：

| 方案 | 说明 | 优缺点 |
|------|------|--------|
| **互斥锁** | 缓存失效时，只允许一个请求查询数据库并重建缓存，其他请求等待 | 简单有效，但可能阻塞 |
| **永不过期** | 热点数据不设置过期时间，后台异步更新 | 避免击穿，但可能数据不一致 |
| **@Cacheable sync=true** | Spring Cache 内置同步模式 | 简单，Spring 内置支持 |

```java
// 方案1：互斥锁
@Service
public class UserService {
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    public User getUserById(Long id) {
        String key = "user:" + id;
        User user = (User) redisTemplate.opsForValue().get(key);
        if (user != null) return user;

        // 获取互斥锁
        String lockKey = "lock:user:" + id;
        Boolean locked = redisTemplate.opsForValue()
            .setIfAbsent(lockKey, "1", Duration.ofSeconds(10));

        if (Boolean.TRUE.equals(locked)) {
            try {
                // 双重检查
                user = (User) redisTemplate.opsForValue().get(key);
                if (user == null) {
                    user = userRepository.findById(id);
                    redisTemplate.opsForValue().set(key, user, Duration.ofHours(1));
                }
            } finally {
                redisTemplate.delete(lockKey);  // 释放锁
            }
        } else {
            // 等待后重试
            try { Thread.sleep(100); } catch (InterruptedException e) {}
            return getUserById(id);
        }
        return user;
    }
}

// 方案2：Spring Cache sync=true
@Cacheable(value = "user", key = "#id", sync = true)
public User getUserById(Long id) {
    return userRepository.findById(id);
}
```

### 3. 缓存雪崩

**问题**：大量缓存 Key 在同一时间集中过期，或缓存服务宕机，导致大量请求同时打到数据库，压垮数据库。

**解决方案**：

| 方案 | 说明 |
|------|------|
| **过期时间加随机值** | 在基础过期时间上加上随机值，避免集中过期 |
| **多级缓存** | 本地缓存 + 远程缓存，远程挂了本地兜底 |
| **缓存高可用** | Redis 集群部署，哨兵/集群模式，避免单点 |
| **限流降级** | 数据库压力过大时，限流或返回默认值/降级数据 |
| **预热缓存** | 系统启动前预热热点数据，避免启动时大量请求打到数据库 |

```java
// 过期时间加随机值
@Configuration
public class CacheConfig {
    @Bean
    public CacheManager cacheManager(RedisConnectionFactory factory) {
        Map<String, RedisCacheConfiguration> configs = new HashMap<>();
        // 不同缓存不同过期时间，且加随机偏移
        configs.put("user", defaultConfig.entryTtl(Duration.ofMinutes(30 + new Random().nextInt(10))));
        configs.put("product", defaultConfig.entryTtl(Duration.ofHours(2 + new Random().nextInt(30))));
        // ...
    }
}

// 限流降级（Sentinel/Hystrix）
@SentinelResource(value = "getUser", fallback = "getUserFallback")
@Cacheable(value = "user", key = "#id")
public User getUserById(Long id) {
    return userRepository.findById(id);
}

// 降级方法
public User getUserFallback(Long id, Throwable e) {
    return User.defaultUser();  // 返回默认值
}
```

---

## 六、缓存一致性

### 1. 缓存与数据库一致性策略

| 策略 | 说明 | 一致性 | 复杂度 |
|------|------|--------|--------|
| **Cache Aside（旁路缓存）** | 读：先查缓存，没有查数据库并回填；写：先更新数据库，再删除缓存 | 最终一致 | 低 |
| **Read/Write Through** | 读：缓存代理查数据库；写：缓存代理同步写数据库和缓存 | 强一致 | 中 |
| **Write Behind（异步写）** | 写：只写缓存，异步批量写数据库 | 弱一致 | 高 |
| **双写** | 同时写数据库和缓存 | 可能不一致 | 低 |

**推荐：Cache Aside（旁路缓存）**，这是最常用的策略。

### 2. Cache Aside 正确流程

```
读操作：
1. 先查缓存
2. 缓存命中 → 直接返回
3. 缓存未命中 → 查数据库
4. 数据库有数据 → 写入缓存 → 返回
5. 数据库无数据 → 返回 null（可缓存空值防穿透）

写操作：
1. 先更新数据库
2. 再删除缓存（不是更新缓存！）
```

**为什么是删除缓存而不是更新缓存？**
- 更新缓存可能导致并发写时缓存值错误
- 删除缓存简单，下次读取时自动回填最新值
- 某些值计算成本高，更新缓存浪费

**为什么先更新数据库再删除缓存？**
- 先删缓存再更新数据库：并发读可能在数据库更新前回填旧值
- 先更新数据库再删缓存：即使并发读回填旧值，缓存过期后也会更新
- 极端情况仍可能不一致，但概率极低，可接受最终一致

### 3. 延迟双删

对于一致性要求较高的场景，使用延迟双删：

```java
@Service
public class UserService {
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Transactional
    public void updateUser(User user) {
        // 1. 先删除缓存
        redisTemplate.delete("user:" + user.getId());

        // 2. 更新数据库
        userRepository.save(user);

        // 3. 延迟一段时间后再次删除缓存（防止并发回填旧值）
        CompletableFuture.runAsync(() -> {
            try {
                Thread.sleep(500);  // 延迟 500ms
                redisTemplate.delete("user:" + user.getId());
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
    }
}
```

### 4. 基于消息队列的最终一致性

```
更新数据库 → 发送消息到 MQ → 消费者删除缓存
```

```java
// 生产者
@Transactional
public void updateUser(User user) {
    userRepository.save(user);
    // 发送缓存失效消息
    rabbitTemplate.convertAndSend("cache.exchange", "cache.invalidate",
        new CacheEvictMessage("user", user.getId()));
}

// 消费者
@RabbitListener(queues = "cache.invalidate.queue")
public void handleCacheEvict(CacheEvictMessage message) {
    redisTemplate.delete(message.getCacheName() + ":" + message.getKey());
}
```

---

## 七、生产级最佳实践

### 1. 缓存使用规范

- [ ] **缓存名称规范**：使用业务域命名，如 `user`、`product`、`order`
- [ ] **缓存键规范**：`缓存名:方法名:参数`，如 `user:getUserById:1`
- [ ] **过期时间必设**：所有缓存必须设置过期时间，避免永久缓存
- [ ] **空值缓存**：对可能不存在的数据缓存空值，防穿透
- [ ] **大对象不缓存**：超过 1MB 的对象不建议缓存，考虑压缩或拆分
- [ ] **缓存键前缀**：使用统一前缀，便于管理和清理
- [ ] **监控统计**：监控缓存命中率、QPS、内存使用

### 2. 缓存键设计

```
好的键设计：
- user:1                    （简洁）
- user:getById:1            （含方法名，避免冲突）
- product:detail:1001:zh    （含语言/环境）

不好的键设计：
- 1                          （无业务含义，易冲突）
- user_1_detail_zh_admin    （下划线混用，不规范）
- user:getUserById(Long id) （含方法签名，冗余）
```

### 3. 过期时间设计

| 数据类型 | 推荐过期时间 | 说明 |
|---------|------------|------|
| 配置数据 | 1-7 天 | 变化少，可长缓存 |
| 用户信息 | 30 分钟-2 小时 | 变化中等 |
| 商品信息 | 1-6 小时 | 变化中等 |
| 订单信息 | 5-30 分钟 | 变化频繁 |
| 热点数据 | 不过期+异步更新 | 极高并发 |
| 临时数据 | 1-5 分钟 | 短期缓存 |
| 空值 | 1-5 分钟 | 防穿透，短过期 |

### 4. 缓存监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|---------|
| **命中率** | 缓存命中次数/总请求次数 | < 80% 告警 |
| **QPS** | 每秒缓存操作次数 | 根据容量设定 |
| **内存使用率** | 缓存内存使用比例 | > 80% 告警 |
| **平均响应时间** | 缓存操作平均耗时 | > 10ms 告警 |
| **Key 数量** | 缓存中 Key 总数 | 突增告警 |
| **驱逐次数** | 缓存驱逐（淘汰）次数 | 突增告警 |

### 5. 常见反模式

| 反模式 | 说明 | 正确做法 |
|--------|------|---------|
| **缓存一切** | 不管什么数据都缓存 | 只缓存读多写少的热点数据 |
| **不过期** | 缓存不设过期时间 | 必须设过期，或有更新机制 |
| **大对象缓存** | 缓存几 MB 的大对象 | 拆分或压缩，或不缓存 |
| **双写不一致** | 同时更新数据库和缓存 | Cache Aside：更新数据库+删除缓存 |
| **缓存穿透不防护** | 不处理不存在数据的查询 | 缓存空值+布隆过滤器 |
| **热点 Key 无保护** | 热点 Key 过期无保护 | 互斥锁/永不过期/sync=true |
| **缓存雪崩无预案** | 无随机过期/多级缓存 | 随机过期+多级缓存+限流降级 |

---

## 八、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 缓存不生效 | 未加 @EnableCaching / 同类方法调用（AOP 不生效） | 启动类加 @EnableCaching，避免同类内部调用 |
| 缓存键冲突 | 不同方法使用相同缓存名和键 | 键中包含方法名，或使用不同缓存名 |
| 缓存数据不一致 | 更新数据库后未删除缓存 / 双写 | 使用 Cache Aside 模式，更新数据库+删除缓存 |
| 缓存穿透 | 大量查询不存在的数据 | 缓存空值 + 布隆过滤器 |
| 缓存击穿 | 热点 Key 过期瞬间大量请求 | 互斥锁 / sync=true / 永不过期 |
| 缓存雪崩 | 大量 Key 同时过期 / Redis 宕机 | 随机过期时间 + 多级缓存 + 限流降级 |
| 内存溢出 | 缓存数据过多 / 大对象 | 设置最大内存 + 淘汰策略 + 不缓存大对象 |
| 序列化异常 | 缓存对象未实现 Serializable / Jackson 序列化失败 | 对象实现 Serializable，配置 Jackson 序列化器 |
| 同类调用缓存不生效 | Spring AOP 代理问题，this 调用不走代理 | 注入自身代理 / 拆分到不同类 / 使用 AopContext |
| @CachePut 不更新 | @CachePut 和 @Cacheable 键不一致 | 确保使用相同的缓存名称和键 |
| @CacheEvict 不清除 | 方法异常导致未执行 / beforeInvocation 配置 | 关键操作设 beforeInvocation=true |
| Redis 连接超时 | 网络问题 / 连接池耗尽 | 检查网络，调整连接池配置 |
| 缓存命中率低 | 过期时间太短 / 键设计不合理 | 延长过期时间，优化键设计 |

---

## 九、关联笔记

### 后端
- [[SpringBoot-自动装配原理]] · [[Gateway-网关路由与鉴权]] · [[配置中心实战]]
- [[MyBatis-核心原理与插件]] · [[Spring事务管理与传播机制]]

### 中间件
- [[Redis数据结构与应用场景]] · [[消息队列-Kafka与RabbitMQ]] · [[分布式锁原理与实现]]

### 架构
- [[高并发系统设计案例]] · [[高可用架构设计]] · [[秒杀系统架构设计]]
- [[架构设计原则-SOLID]] · [[设计模式-策略模式]] · [[设计模式-工厂模式]]

### 数据库
- [[关系型数据库索引原理]] · [[数据库分库分表策略]] · [[事务隔离级别与MVCC]]

### 导航
- [[MOC-后端开发]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[SpringBoot-自动装配原理]] Spring 基础 → 学习 [[Redis数据结构与应用场景]] Redis 基础 → 深入本文 SpringCache 缓存抽象 → 实践 [[高并发系统设计案例]] 缓存应用 → 研究 [[秒杀系统架构设计]] 缓存三大问题解决方案 → 学习 [[分布式锁原理与实现]] 缓存击穿互斥锁实现。
