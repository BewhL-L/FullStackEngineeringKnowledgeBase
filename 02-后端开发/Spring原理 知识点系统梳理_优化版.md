---
title: Spring 原理知识点系统梳理
tags: [后端, Spring, 原理, IoC, AOP]
created: 2026-08-12
updated: 2026-08-12
---

# Spring 原理知识点系统梳理（优化版）

> **文档说明**：本文档参照《Java知识点完整整合大全》排版风格，系统梳理 Spring 框架核心原理。包含概述、核心特性、常用用法、注意事项四大模块，辅以动态可视化解析图、深度讲解与精简总结。**优化版**在原有内容基础上，为每个知识点补充了作用、原理、用法的深度解析，并新增了知识点图解。

---

## 1. 概述

Spring 是一个轻量级的 Java 企业级开发框架，核心是**控制反转（IoC）**和**面向切面编程（AOP）**。它通过容器管理对象的生命周期和依赖关系，降低组件间耦合，提供声明式事务、数据访问、Web 开发等一站式企业级解决方案。

**核心定位**：
- IoC 容器：管理 Bean 的创建、依赖注入和生命周期
- AOP 框架：声明式事务、日志、权限等横切关注点
- 一站式平台：整合数据访问、Web、消息、安全等模块
- 非侵入式：业务代码不依赖 Spring API，便于测试和替换

**版本演进**：

| 版本 | 关键特性 |
|------|---------|
| Spring 1.x | 基础 IoC、AOP、JDBC 模板 |
| Spring 2.x | XML 命名空间、@AspectJ、集成 JPA |
| Spring 3.x | 注解驱动配置（@Configuration）、SpEL、REST 支持 |
| Spring 4.x | 泛型注入、条件注解、WebSocket、Spring Boot 1.x |
| Spring 5.x | 响应式编程（WebFlux）、Kotlin 支持、JDK 8+ 基线 |
| Spring 6.x | Jakarta EE 9+、AOT 编译、JDK 17+ 基线（Spring Boot 3.x） |

---


---
## 2. 核心特性

<div style="background:linear-gradient(135deg,#43e97b,#38f9d7);border-radius:16px;padding:24px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#1a1a2e;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes springBean{0%,100%{transform:scale(1);opacity:.9}50%{transform:scale(1.05);opacity:1}}.spring-step{background:rgba(255,255,255,.5);border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:8px 12px;margin:5px auto;font-size:12px;text-align:center;animation:springBean 2.5s ease-in-out infinite;font-weight:600}.spring-step:nth-child(1){animation-delay:0s;width:90%}.spring-step:nth-child(2){animation-delay:.3s;width:85%}.spring-step:nth-child(3){animation-delay:.6s;width:80%}.spring-step:nth-child(4){animation-delay:.9s;width:75%}.spring-step:nth-child(5){animation-delay:1.2s;width:70%}.spring-step:nth-child(6){animation-delay:1.5s;width:65%}.spring-step:nth-child(7){animation-delay:1.8s;width:60%}</style>
<div style="text-align:center;font-size:16px;font-weight:700;margin-bottom:16px;padding-bottom:12px;border-bottom:1.5px solid rgba(0,0,0,.1);letter-spacing:1px">Spring Bean 生命周期（七步）</div>
<div class="spring-step">① 实例化（Instantiation）— 调用构造方法</div>
<div class="spring-step">② 属性赋值（Populate）— 依赖注入</div>
<div class="spring-step">③ Aware 接口回调 — BeanName/BeanFactory/ApplicationContext</div>
<div class="spring-step">④ BeanPostProcessor 前置处理 — postProcessBeforeInitialization</div>
<div class="spring-step">⑤ 初始化（Initialization）— @PostConstruct / InitializingBean / init-method</div>
<div class="spring-step">⑥ BeanPostProcessor 后置处理 — postProcessAfterInitialization（AOP 代理生成）</div>
<div class="spring-step">⑦ 销毁（Destruction）— @PreDestroy / DisposableBean / destroy-method</div>
</div>

### 2.1 IoC（控制反转）

IoC 是将对象的创建和依赖管理交给容器，而非代码中手动 new。核心是**依赖注入（DI）**：

- **控制反转**：对象创建控制权从应用代码转移到 Spring 容器
- **依赖注入**：容器自动将依赖对象注入到需要它的 Bean 中
- **BeanFactory**：IoC 容器顶层接口，懒加载（getBean 时才创建）
- **ApplicationContext**：BeanFactory 子接口，国际化、事件、AOP，启动时预加载单例

**注入方式**：构造器注入（推荐）、Setter 注入、字段注入（@Autowired，不推荐）。

> 🔍 **知识点深度解析**
>
> **作用**：IoC 是 Spring 的核心，它将对象创建和依赖管理从业务代码中解耦出来，让业务代码只关注业务逻辑。依赖注入让组件之间通过接口依赖，具体实现由容器注入，便于测试（Mock）和替换。
>
> **原理**：Spring 启动时读取配置（XML/注解/JavaConfig），解析 BeanDefinition（Bean 的元数据：类名、作用域、依赖关系），注册到 BeanDefinitionRegistry。然后 BeanFactory 根据 BeanDefinition 创建 Bean 实例，通过反射调用构造方法，再通过反射设置属性（依赖注入）。依赖注入的解析过程：先按类型找（有多个则按名称@Qualifier），找不到则抛异常。循环依赖通过三级缓存解决（singletonObjects/earlySingletonObjects/singletonFactories）。
>
> **用法要点**：① 构造器注入是 Spring 推荐方式（依赖不可变、确保依赖不为空、便于测试）；② 字段注入（@Autowired）不推荐（无法 final、测试不便、循环依赖隐藏）；③ @Resource（JSR-250）按名称注入，@Autowired 按类型注入；④ 循环依赖只支持单例 Bean 的字段注入（构造器注入循环依赖无法解决）；⑤ ApplicationContext 启动时预加载所有单例 Bean（可配置懒加载@Lazy）；⑥ BeanFactory 和 ApplicationContext 的区别是面试重点。

### 2.2 Bean 生命周期

Bean 从创建到销毁的完整过程：

1. **实例化**：调用构造方法创建对象
2. **属性赋值**：依赖注入（@Autowired 字段/Setter）
3. **Aware 回调**：BeanNameAware、BeanFactoryAware、ApplicationContextAware
4. **BeanPostProcessor 前置**：postProcessBeforeInitialization
5. **初始化**：@PostConstruct → InitializingBean.afterPropertiesSet → init-method
6. **BeanPostProcessor 后置**：postProcessAfterInitialization（AOP 代理在此生成）
7. **使用**：Bean 就绪，可被使用
8. **销毁**：@PreDestroy → DisposableBean.destroy → destroy-method

> 🔍 **知识点深度解析**
>
> **作用**：Bean 生命周期是理解 Spring 扩展机制的基础。BeanPostProcessor 允许在 Bean 初始化前后做自定义处理（AOP 代理、@Autowired 注入、@PostConstruct 执行都是通过它实现的），Aware 接口让 Bean 获取容器资源。
>
> **原理**：生命周期由 AbstractAutowireCapableBeanFactory.doCreateBean() 实现。实例化用反射（CGLIB 或构造器），属性赋值通过 InstantiationAwareBeanPostProcessor 处理 @Autowired。初始化的执行顺序：@PostConstruct（CommonAnnotationBeanPostProcessor）→ InitializingBean → init-method（XML/注解）。AOP 代理在 postProcessAfterInitialization 中生成（AnnotationAwareAspectJAutoProxyCreator），如果 Bean 有切面则返回代理对象，否则返回原对象。销毁在容器关闭时触发，执行顺序：@PreDestroy → DisposableBean → destroy-method。
>
> **用法要点**：① 初始化方法优先级：@PostConstruct > InitializingBean > init-method；② 销毁方法优先级：@PreDestroy > DisposableBean > destroy-method；③ BeanPostProcessor 是 Spring 最重要的扩展点，@Autowired、@Value、AOP、@PostConstruct 都通过它实现；④ 多例 Bean（prototype）的销毁方法不会被容器调用（容器不管理其完整生命周期）；⑤ Aware 接口让 Bean 感知容器（如 ApplicationContextAware 获取 ApplicationContext）；⑥ 面试常考 Bean 生命周期完整流程和 BeanPostProcessor 的作用。

### 2.3 AOP（面向切面编程）

AOP 将横切关注点（日志、事务、权限）从业务逻辑中分离，通过动态代理在运行时织入。

**核心概念**：
- 切面（Aspect）：横切关注点的模块化（如日志切面）
- 连接点（JoinPoint）：程序执行的某个点（方法调用）
- 切点（Pointcut）：匹配连接点的表达式（execution(* com.example..*.*(..))）
- 通知（Advice）：在切点执行的代码（@Before/@After/@Around）
- 织入（Weaving）：将切面应用到目标对象创建代理的过程

**动态代理**：JDK 动态代理（接口，默认）、CGLIB 动态代理（类，spring.aop.proxy-target-class=true）。

> 🔍 **知识点深度解析**
>
> **作用**：AOP 解决了横切关注点的代码重复问题（日志、事务、权限在每个业务方法中都写一遍）。通过动态代理在运行时自动织入，业务代码完全无感知，是声明式事务（@Transactional）的底层实现。
>
> **原理**：Spring AOP 基于动态代理实现。JDK 动态代理：目标类有接口时，用 Proxy.newProxyInstance() 生成实现了目标接口的代理类，调用方法时通过 InvocationHandler.invoke() 拦截。CGLIB 动态代理：目标类无接口时，用 ASM 生成目标类的子类，重写方法拦截。Spring Boot 2.x+ 默认 CGLIB（proxyTargetClass=true）。织入时机：编译期（AspectJ 编译器）、类加载期（AspectJ load-time weaving）、运行期（Spring AOP，BeanPostProcessor 后置处理时生成代理）。
>
> **用法要点**：① 同一个类内方法调用不会触发 AOP（this 调用不走代理），用 AopContext.currentProxy() 或注入自身解决；② @Transactional 是 AOP 的典型应用（基于动态代理+ThreadLocal）；③ 切面执行顺序用 @Order 控制（数字越小越先执行，@Around 包裹其他通知）；④ 切点表达式：execution（方法签名）、within（类）、@annotation（注解）、args（参数）；⑤ JDK 代理只能代理接口，CGLIB 不能代理 final 类/方法；⑥ AspectJ 是编译期织入（功能更强，支持字段/构造器拦截），Spring AOP 是运行期代理（只支持方法拦截）。

### 2.4 事务管理

Spring 事务分为**编程式事务**（TransactionTemplate）和**声明式事务**（@Transactional）。

**@Transactional 参数**：
- propagation：传播行为（REQUIRED 默认、REQUIRES_NEW、NESTED、SUPPORTS、NOT_SUPPORTED、MANDATORY、NEVER）
- isolation：隔离级别（DEFAULT、READ_UNCOMMITTED、READ_COMMITTED、REPEATABLE_READ、SERIALIZABLE）
- timeout：超时时间（秒）
- readOnly：只读（优化，不能写）
- rollbackFor：回滚异常（默认只回滚 RuntimeException 和 Error）
- noRollbackFor：不回滚异常

> 🔍 **知识点深度解析**
>
> **作用**：声明式事务让业务代码无需写 commit/rollback，通过 @Transactional 注解自动管理事务，是 Spring 最常用的功能之一。理解传播行为和隔离级别是正确使用事务的关键。
>
> **原理**：@Transactional 基于 AOP 动态代理实现。代理对象在方法执行前：开启事务（DataSourceTransactionManager.doBegin()，设置 autoCommit=false，绑定 Connection 到 ThreadLocal）；方法正常返回：提交事务；方法抛异常：判断是否需要回滚（默认 RuntimeException/Error 回滚，受检异常不回滚），回滚或提交。事务传播行为通过事务状态（TransactionStatus）控制：REQUIRED 有事务则加入，没有则新建；REQUIRES_NEW 总是新建事务（挂起当前事务）；NESTED 在当前事务内创建保存点（savepoint），子事务回滚不影响父事务。
>
> **用法要点**：① @Transactional 只对 public 方法生效（代理只能拦截 public）；② 同类内调用不生效（this 调用不走代理）；③ 默认只回滚 RuntimeException 和 Error，受检异常（Exception）需 rollbackFor=Exception.class；④ 传播行为 REQUIRES_NEW 会新建连接（可能导致死锁），慎用；⑤ 只读事务（readOnly=true）不能写操作，会优化（FlushMode=MANUAL）；⑥ 事务超时是从事务开始到最后一条 SQL 执行的时间，不是方法总时间；⑦ 用 try-catch 捕获异常后事务不会回滚（异常没抛到代理层），需手动设置 rollback。

### 2.5 Spring MVC 原理

Spring MVC 基于**前端控制器模式**，核心是 DispatcherServlet：

1. 请求到达 DispatcherServlet
2. HandlerMapping 查找 Handler（Controller 方法）
3. HandlerAdapter 调用 Handler（参数解析、返回值处理）
4. ViewResolver 解析视图（逻辑视图名→View 对象）
5. View 渲染（模板引擎/JSON）
6. 返回响应

**核心组件**：DispatcherServlet、HandlerMapping、HandlerAdapter、ViewResolver、HandlerExceptionResolver。

> 🔍 **知识点深度解析**
>
> **作用**：Spring MVC 是 Spring 的 Web 框架，通过 DispatcherServlet 统一处理所有请求，将请求分发到对应的 Controller 方法，处理参数绑定、视图渲染、异常处理。是 Java Web 开发的标准框架。
>
> **原理**：DispatcherServlet 是一个 Servlet，在 web.xml 或 ServletContainerInitializer 中注册。请求到达时，doDispatch() 方法处理：① getHandler() 通过 HandlerMapping（RequestMappingHandlerMapping 处理 @RequestMapping）找到 HandlerExecutionChain（Handler+拦截器）；② getHandlerAdapter() 找到对应的 HandlerAdapter（RequestMappingHandlerAdapter）；③ 拦截器 preHandle → adapter.handle()（反射调用 Controller 方法，参数解析器解析参数，返回值处理器处理返回值）→ 拦截器 postHandle；④ 异常则 HandlerExceptionResolver 处理；⑤ processDispatchResult() 渲染视图（ViewResolver 解析，View.render）。@ResponseBody 用 RequestResponseBodyMethodProcessor 处理（HttpMessageConverter 转 JSON）。
>
> **用法要点**：① Spring Boot 自动配置 DispatcherServlet（DispatcherServletAutoConfiguration）；② 参数解析器（HandlerMethodArgumentResolver）可自定义（如当前登录用户）；③ 返回值处理器（HandlerMethodReturnValueHandler）可自定义；④ 拦截器（HandlerInterceptor）用于登录校验、日志等，preHandle 返回 false 则中断；⑤ 全局异常处理用 @ControllerAdvice + @ExceptionHandler；⑥ 静态资源映射由 ResourceHttpRequestHandler 处理，Spring Boot 默认映射 /static、/public、/resources、/META-INF/resources。

---


---
## 3. 常用用法

### 3.1 依赖注入

```java
// 构造器注入（推荐）
@Service
public class UserService {
    private final UserRepository userRepository;
    private final OrderService orderService;
    
    public UserService(UserRepository userRepository, OrderService orderService) {
        this.userRepository = userRepository;
        this.orderService = orderService;
    }
}

// @RequiredArgsConstructor（Lombok，自动生成构造器）
@Service
@RequiredArgsConstructor
public class ProductService {
    private final ProductRepository productRepository;
}

// 条件注入
@Service
@ConditionalOnProperty(name = "cache.enabled", havingValue = "true")
public class RedisCacheService implements CacheService {}

@Service
@ConditionalOnMissingBean(CacheService.class)
public class DefaultCacheService implements CacheService {}
```

> 🔍 **知识点深度解析**
>
> **作用**：依赖注入是 IoC 的具体实现，让组件之间松耦合。构造器注入确保依赖不可变且不为空，条件注入实现按需装配（Spring Boot 自动配置的核心）。
>
> **原理**：@Autowired 由 AutowiredAnnotationBeanPostProcessor 处理，在属性赋值阶段通过反射注入。构造器注入时，Spring 先解析构造器参数的依赖，创建依赖 Bean，再调用构造器。条件注入由 @Conditional 注解和 Condition 接口实现，ConfigurationClassParser 在解析配置类时评估条件，不满足则跳过该 Bean 的注册。Spring Boot 的 @ConditionalOnProperty/@ConditionalOnClass/@ConditionalOnMissingBean 都是 @Conditional 的具体实现。
>
> **用法要点**：① 构造器注入是 Spring 4.3+ 推荐，单构造器时 @Autowired 可省略；② Lombok @RequiredArgsConstructor 自动为 final 字段生成构造器，配合构造器注入最简洁；③ 多个实现类用 @Qualifier("beanName") 指定；④ @Primary 指定首选实现；⑤ 循环依赖：构造器注入无法解决，字段/Setter 注入可解决（三级缓存）；⑥ @ConditionalOnMissingBean 是 Spring Boot 自动配置"用户配置优先"的实现。

### 3.2 Bean 作用域

```java
// 单例（默认）
@Bean
@Scope("singleton")
public MyBean singletonBean() { return new MyBean(); }

// 多例
@Bean
@Scope("prototype")
public MyBean prototypeBean() { return new MyBean(); }

// Web 作用域
@Bean
@Scope(value = "request", proxyMode = ScopedProxyMode.TARGET_CLASS)
public MyBean requestBean() { return new MyBean(); }

@Bean
@Scope(value = "session", proxyMode = ScopedProxyMode.TARGET_CLASS)
public MyBean sessionBean() { return new MyBean(); }

// 自定义作用域
@Bean
@Scope("thread")  // 需注册自定义 Scope
public MyBean threadBean() { return new MyBean(); }
```

> 🔍 **知识点深度解析**
>
> **作用**：Bean 作用域决定了 Bean 实例的生命周期和可见范围。单例全局共享，多例每次获取新建，Web 作用域绑定到请求/会话。正确选择作用域是避免并发问题的关键。
>
> **原理**：singleton 在容器中只有一个实例，存储在 singletonObjects 缓存中。prototype 每次 getBean 都新建实例，容器不管理其销毁。request/session 作用域通过 Scope 接口实现，RequestScope 从当前 Request 的 attribute 中获取（没有则创建并存入），SessionScope 从 HttpSession 中获取。Web 作用域注入到单例 Bean 时需要 proxyMode（生成代理，每次调用代理方法时从当前作用域获取真实对象），否则会注入时就创建（作用域不存在则报错）。
>
> **用法要点**：① 默认 singleton，绝大多数 Bean 用单例（无状态服务）；② 有状态的 Bean 用 prototype（每次使用独立实例）；③ Web 作用域必须配 proxyMode，否则注入到单例时报错；④ 单例 Bean 注入多例 Bean 时，多例只注入一次（不是每次调用都新的），需用 lookup-method 或 ObjectFactory；⑤ 自定义作用域实现 Scope 接口，用 ConfigurableBeanFactory.registerScope() 注册；⑥ 线程作用域（SimpleThreadScope）Spring 提供但默认未注册，需手动注册。

### 3.3 事件机制

```java
// 自定义事件
public class OrderCreatedEvent extends ApplicationEvent {
    private final Order order;
    public OrderCreatedEvent(Object source, Order order) {
        super(source);
        this.order = order;
    }
    public Order getOrder() { return order; }
}

// 发布事件
@Service
@RequiredArgsConstructor
public class OrderService {
    private final ApplicationEventPublisher publisher;
    public void createOrder(Order order) {
        // 保存订单
        publisher.publishEvent(new OrderCreatedEvent(this, order));
    }
}

// 监听事件
@Component
public class OrderListener {
    @EventListener
    public void onOrderCreated(OrderCreatedEvent event) {
        // 发送通知、扣减库存等
    }
    
    @Async  // 异步监听
    @EventListener
    public void onOrderCreatedAsync(OrderCreatedEvent event) {}
}
```

> 🔍 **知识点深度解析**
>
> **作用**：Spring 事件机制实现了观察者模式，用于模块间解耦通信（订单创建后触发通知、库存、积分等）。发布者不需要知道监听者，监听者可动态增减。
>
> **原理**：ApplicationEventPublisher.publishEvent() 最终调用 ApplicationEventMulticaster.multicastEvent()。SimpleApplicationEventMulticaster 遍历所有匹配的 ApplicationListener，调用 onApplicationEvent()。@EventListener 由 EventListenerMethodProcessor 处理，将方法包装为 ApplicationListener。同步监听在发布线程执行，异步监听（@Async）提交到 TaskExecutor 执行。事件可以是任意对象（不一定继承 ApplicationEvent），Spring 会自动包装为 PayloadApplicationEvent。
>
> **用法要点**：① 默认同步监听（在发布线程执行），异步需 @Async + @EnableAsync；② 监听方法抛异常会传播到发布者（同步），异步则不会；③ 事件可以继承，监听父事件会收到所有子类事件；④ @EventListener(condition = "#event.order.amount > 100") 支持 SpEL 条件过滤；⑤ 事务事件（@TransactionalEventListener）在事务提交后/回滚后执行（AFTER_COMMIT/AFTER_ROLLBACK）；⑥ 事件机制适合解耦，但不适合需要返回值的场景（用回调或直接调用）。

### 3.4 条件注解与自动配置

```java
// 条件注解
@Configuration
public class MyAutoConfig {
    @Bean
    @ConditionalOnClass(RedisTemplate.class)
    @ConditionalOnMissingBean
    @ConditionalOnProperty(prefix = "my.redis", name = "enabled", havingValue = "true", matchIfMissing = true)
    public RedisTemplate redisTemplate() { return new RedisTemplate(); }
}

// spring.factories（Spring Boot 2.x）
// org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
// com.example.MyAutoConfig

// META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports（Spring Boot 3.x）
// com.example.MyAutoConfig
```

> 🔍 **知识点深度解析**
>
> **作用**：条件注解是 Spring Boot 自动配置的核心，它让配置类/Bean 在满足条件时才生效。自动配置通过 spring.factories 或 AutoConfiguration.imports 注册，实现"引入 starter 即自动配置"。
>
> **原理**：@Conditional 是元注解，@ConditionalOnClass/@ConditionalOnProperty/@ConditionalOnMissingBean 等都是组合了 @Conditional 和具体 Condition 实现。ConfigurationClassParser 在解析 @Configuration 类时评估条件，不满足则跳过。@ConditionalOnClass 通过 ASM 读取类元数据（不加载类，避免 ClassNotFoundException）。@ConditionalOnMissingBean 在 Bean 注册阶段检查容器中是否已有该类型 Bean。自动配置类通过 SpringFactoriesLoader 加载（Spring Boot 2.x 读 spring.factories，3.x 读 AutoConfiguration.imports），且配置为自动配置类（@AutoConfiguration）。
>
> **用法要点**：① @ConditionalOnMissingBean 让用户配置优先（用户定义了就不用自动配置的）；② @ConditionalOnClass 检查类是否在 classpath 中（引入依赖才生效）；③ @ConditionalOnProperty 检查配置属性（matchIfMissing=true 表示没配置也生效）；④ 自动配置类要放在自动配置包，不要被 @ComponentScan 扫描到（否则条件可能失效）；⑤ Spring Boot 3.x 用 AutoConfiguration.imports 替代 spring.factories；⑥ 调试自动配置用 --debug 或 actuator/conditions 端点查看生效/未生效的配置。

### 3.5 AOP 切面开发

```java
@Aspect
@Component
public class LogAspect {
    // 切点：所有 Controller 方法
    @Pointcut("execution(* com.example.controller..*.*(..))")
    public void controllerPointcut() {}

    @Before("controllerPointcut()")
    public void before(JoinPoint joinPoint) {
        log.info("方法执行前: {}", joinPoint.getSignature());
    }

    @AfterReturning(pointcut = "controllerPointcut()", returning = "result")
    public void afterReturning(JoinPoint joinPoint, Object result) {
        log.info("方法返回: {}", result);
    }

    @Around("controllerPointcut()")
    public Object around(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = pjp.proceed(); // 执行目标方法
        long cost = System.currentTimeMillis() - start;
        log.info("方法耗时: {}ms", cost);
        return result;
    }

    @AfterThrowing(pointcut = "controllerPointcut()", throwing = "ex")
    public void afterThrowing(Exception ex) {
        log.error("方法异常", ex);
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：AOP 切面用于将横切逻辑（日志、性能监控、权限校验、事务）从业务代码中抽离。@Around 是最强大的通知（可控制是否执行目标方法、修改参数/返回值）。
>
> **原理**：@Aspect 注解的类由 AnnotationAwareAspectJAutoProxyCreator（BeanPostProcessor）处理，在 postProcessAfterInitialization 中为匹配切点的 Bean 生成动态代理。代理对象的方法调用会被拦截，按通知顺序执行：@Around（前半部分）→ @Before → 目标方法 → @AfterReturning/@AfterThrowing → @After → @Around（后半部分）。切点表达式由 AspectJ 表达式解析器解析，匹配方法签名。
>
> **用法要点**：① @Around 必须调用 pjp.proceed() 执行目标方法，否则目标方法不执行；② @Around 可以修改参数（pjp.proceed(newArgs)）和返回值；③ 多个切面用 @Order 控制顺序（数字小的先执行，@Around 外层包裹）；④ 切点表达式组合：&&（与）、||（或）、!（非）；⑤ @annotation(com.example.Log) 匹配标注了 @Log 注解的方法（最常用）；⑥ 性能监控/日志用 AOP 实现，但注意 AOP 本身有性能开销（代理调用），高频方法慎用。

### 3.6 声明式事务

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;
    private final InventoryService inventoryService;

    @Transactional(rollbackFor = Exception.class)
    public void createOrder(Order order) {
        orderRepository.save(order);
        inventoryService.deduct(order.getProductId(), order.getQuantity());
        // 异常则回滚
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logOrder(Order order) {
        // 独立事务，即使外层回滚这里也提交
    }

    @Transactional(readOnly = true, timeout = 5)
    public Order getOrder(Long id) {
        return orderRepository.findById(id).orElse(null);
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：@Transactional 是声明式事务的标准用法，通过 AOP 自动管理事务的开启/提交/回滚。正确配置传播行为和回滚规则是保证数据一致性的关键。
>
> **原理**：@Transactional 由 TransactionInterceptor（AOP 通知）拦截。方法执行前：TransactionManager.getTransaction() 开启事务（根据传播行为决定新建或加入），将 Connection 绑定到 ThreadLocal（DataSourceTransactionManager）。方法执行中：所有 SQL 用同一个 Connection（事务同步）。方法返回：commit()；方法抛异常：判断 rollbackFor，匹配则 rollback()，否则 commit()。REQUIRES_NEW 会挂起当前事务（保存当前 Connection，新建 Connection），方法结束后恢复。
>
> **用法要点**：① 必须 rollbackFor = Exception.class（默认只回滚 RuntimeException）；② 同类内调用不生效（用 AopContext.currentProxy() 或拆分类）；③ try-catch 后异常不传播，事务不回滚（需 TransactionAspectSupport.currentTransactionStatus().setRollbackOnly()）；④ REQUIRES_NEW 会用新连接，注意连接池耗尽；⑤ 只读事务（readOnly=true）中写操作会报错；⑥ 超时是指最后一条 SQL 执行时间，不是方法总时间；⑦ 事务方法中不要做远程调用（超时/不可控），远程调用放在事务外。

### 3.7 统一异常处理

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public Result<?> handleBusiness(BusinessException e) {
        return Result.fail(e.getCode(), e.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<?> handleValidation(MethodArgumentNotValidException e) {
        String msg = e.getBindingResult().getFieldErrors().stream()
            .map(FieldError::getDefaultMessage)
            .collect(Collectors.joining(", "));
        return Result.fail(400, msg);
    }

    @ExceptionHandler(Exception.class)
    public Result<?> handleException(Exception e) {
        log.error("系统异常", e);
        return Result.fail(500, "系统异常");
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：@RestControllerAdvice 实现全局异常处理，将异常处理逻辑从 Controller 中抽离，统一返回格式。是 RESTful API 的标准实践。
>
> **原理**：@ControllerAdvice 由 ControllerAdviceBean 注册，ExceptionHandlerExceptionResolver 在处理异常时查找匹配的 @ExceptionHandler 方法。匹配规则：异常类型继承关系（精确匹配优先，父类后匹配）。@RestControllerAdvice = @ControllerAdvice + @ResponseBody，返回值自动转 JSON。异常处理方法的参数可以是异常对象、HttpServletRequest、Model 等，返回值可以是 ResponseEntity、ModelAndView、任意对象（转 JSON）。
>
> **用法要点**：① @ExceptionHandler 按异常类型匹配，子类优先于父类；② 多个 @ControllerAdvice 用 @Order 控制优先级；③ 异常处理方法本身抛异常会被默认异常处理器处理；④ 业务异常继承 RuntimeException（不需要 throws 声明）；⑤ 参数校验异常（MethodArgumentNotValidException）单独处理，返回友好提示；⑥ 系统异常（Exception）兜底，记录日志但不暴露详细信息给前端（安全考虑）。

### 3.8 Spring 扩展点

```java
// BeanPostProcessor：Bean 初始化前后处理
@Component
public class MyBeanPostProcessor implements BeanPostProcessor {
    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) {
        if (bean instanceof MyService) {
            // 初始化前处理
        }
        return bean;
    }
    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) {
        return bean; // 可返回代理对象
    }
}

// BeanFactoryPostProcessor：BeanDefinition 注册后、实例化前处理
@Component
public class MyBeanFactoryPostProcessor implements BeanFactoryPostProcessor {
    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory bf) {
        BeanDefinition bd = bf.getBeanDefinition("myBean");
        bd.getPropertyValues().add("name", "modified");
    }
}

// ApplicationListener：容器事件监听
@Component
public class MyListener implements ApplicationListener<ContextRefreshedEvent> {
    @Override
    public void onApplicationEvent(ContextRefreshedEvent event) {
        // 容器刷新完成后执行（初始化数据、预热缓存）
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：Spring 提供了丰富的扩展点，允许在容器启动和 Bean 生命周期的各个阶段插入自定义逻辑。BeanPostProcessor 是最常用的扩展点（@Autowired、AOP、@PostConstruct 都基于它）。
>
> **原理**：BeanFactoryPostProcessor 在所有 BeanDefinition 加载完成后、Bean 实例化前执行，可以修改 BeanDefinition。BeanPostProcessor 在每个 Bean 初始化前后执行，可以修改 Bean 或返回代理。ApplicationContext 事件在容器生命周期的关键节点发布：ContextRefreshedEvent（刷新完成）、ContextStartedEvent（启动）、ContextStoppedEvent（停止）、ContextClosedEvent（关闭）。这些扩展点是 Spring 框架本身功能（@Autowired、AOP、事务）的实现基础，也是第三方框架整合 Spring 的方式。
>
> **用法要点**：① BeanPostProcessor 返回 null 会导致后续 BeanPostProcessor 不执行（必须返回 bean）；② BeanFactoryPostProcessor 中不要 getBean（会导致 Bean 提前实例化，绕过后续处理）；③ ContextRefreshedEvent 会触发多次（父子容器各一次），注意幂等；④ 用 @EventListener 替代 ApplicationListener 更简洁；⑤ ImportBeanDefinitionRegistrar 用于动态注册 Bean（MyBatis @MapperScan）；⑥ FactoryBean 用于创建复杂 Bean（如 MyBatis Mapper、代理对象）。

---


---
## 4. 注意事项

1. **构造器注入优先**：构造器注入保证依赖不可变、不为空、便于测试。字段注入（@Autowired）不推荐，Lombok @RequiredArgsConstructor 是最佳实践。

2. **循环依赖**：Spring 只解决单例 Bean 的字段/Setter 循环依赖（三级缓存）。构造器循环依赖无法解决，会抛 BeanCurrentlyInCreationException。

3. **@Transactional 失效场景**：非 public 方法、同类内调用、try-catch 吞异常、受检异常未配置 rollbackFor、多线程调用（事务不传播）。

4. **AOP 同类调用失效**：this.method() 不走代理，AOP 不生效。用 AopContext.currentProxy()、注入自身、或拆分类解决。

5. **单例 Bean 线程安全**：单例 Bean 全局共享，不要有可变成员变量（状态）。需要状态用 ThreadLocal 或 prototype 作用域。

6. **@Value 注入静态字段**：@Value 不能注入 static 字段（静态字段在类加载时初始化，Spring 还没启动）。用非静态 setter 注入或 @PostConstruct 赋值。

7. **事务传播行为**：REQUIRES_NEW 会新建数据库连接，注意连接池耗尽。NESTED 依赖 JDBC savepoint，部分数据库不支持。

8. **Bean 初始化顺序**：不要依赖 Bean 的初始化顺序（除非用 @DependsOn 或 Ordered）。需要初始化逻辑用 @PostConstruct 或 InitializingBean。

9. **@Async 失效**：同类内调用不生效、方法非 public、返回值不是 void/Future。需 @EnableAsync 开启。

10. **配置属性绑定**：@ConfigurationProperties 比 @Value 更适合批量配置（支持元数据、校验、宽松绑定）。@Value 适合单个简单值。

11. **过滤器 vs 拦截器 vs AOP**：Filter（Servlet 规范，最早，可改请求响应）、Interceptor（Spring MVC，可访问 Handler）、AOP（方法级，最灵活）。按需求选择。

12. **Spring Boot 自动配置排查**：用 --debug 查看自动配置报告，或 actuator/conditions 端点。常见问题：依赖没引入、条件不满足、被用户配置覆盖。

---

> 💡 **深度讲解**：Spring 的核心是 IoC 和 AOP。IoC 通过 BeanDefinition → 反射实例化 → 依赖注入 → 生命周期回调的流程管理 Bean，三级缓存解决循环依赖。AOP 通过动态代理（JDK/CGLIB）在运行时织入切面，@Transactional、@Async、日志监控都是 AOP 的应用。Bean 生命周期是理解 Spring 扩展机制的关键：BeanPostProcessor 在初始化前后处理（@Autowired 注入、AOP 代理生成都在此），Aware 接口让 Bean 感知容器。声明式事务基于 AOP+ThreadLocal，传播行为控制事务的嵌套关系。Spring MVC 的 DispatcherServlet 通过 HandlerMapping→HandlerAdapter→ViewResolver 的流程处理请求。自动配置通过条件注解+spring.factories 实现"引入即配置"。理解了这些原理，就能正确使用 Spring，也能在遇到问题（事务不生效、AOP 不拦截、循环依赖）时快速定位。
>
> **📝 精简总结**：Spring 核心=IoC（Bean 容器+依赖注入）+AOP（动态代理）；Bean 生命周期7步，BeanPostProcessor 是核心扩展点；AOP 用 JDK/CGLIB 动态代理，同类调用失效；@Transactional 基于 AOP，默认回滚 RuntimeException，需 rollbackFor=Exception；Spring MVC 用 DispatcherServlet 前端控制器；自动配置=条件注解+spring.factories；注意循环依赖、事务失效、AOP 同类调用、单例线程安全。

---

> 📋 **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 知识点深度解析」模块（作用+原理+用法要点），原有内联图已统一风格化美化（圆角、阴影、渐变、动画）。所有原有内容完整保留，未做任何修改。
