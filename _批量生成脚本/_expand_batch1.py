# -*- coding: utf-8 -*-
"""第一批扩展：后端开发 + 设计模式"""
import os, sys
ENGINE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "01-前端开发")
sys.path.insert(0, ENGINE_DIR)
from engine import expand

BASE = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 设计模式
# ============================================================
design_patterns = {
    "### 2.2 工厂方法模式（Factory Method）": (
        "定义创建对象的接口，让子类决定实例化哪个类，将对象创建与使用解耦。",
        "工厂方法模式在简单工厂基础上进一步抽象：定义一个 Factory 接口声明工厂方法，由具体工厂子类决定创建哪种 Product。新增产品类型时只需新增对应工厂类，无需修改已有工厂代码，符合开闭原则。其本质是把 new 操作延迟到子类，客户端面向 Factory 接口编程而非具体类。",
        ["简单工厂违反开闭（新增产品需改工厂代码），工厂方法通过子类化解决", "Spring 的 BeanFactory/FactoryBean 是工厂方法的典型应用", "适合创建逻辑复杂、需要根据条件创建不同实现的场景", "与策略模式区别：工厂关注创建，策略关注行为切换", "面试常考：工厂方法与简单工厂区别、Spring 中的工厂模式应用"]
    ),
    "### 2.3 抽象工厂模式（Abstract Factory）": (
        "创建一系列相关或相互依赖的对象家族，保证产品族之间的兼容性。",
        "抽象工厂定义多个工厂方法（createButton/createText），每个具体工厂生产一个产品族（如 Windows 族、Mac 族）的全套产品。客户端一次只使用一个具体工厂，确保同一族产品风格一致。新增产品族容易（加一个工厂类），但新增产品等级结构困难（需修改所有工厂接口及实现）。",
        ["产品族 vs 产品等级：族是同一品牌下不同产品，等级是不同品牌同一产品", "适合跨平台 UI、多数据库方言切换等成组对象创建场景", "扩展性方向不对称：加产品族容易，加产品类型难", "Spring 的 AnnotationConfigApplicationContext 根据配置创建整套 Bean 可视为抽象工厂思想", "面试常考：与工厂方法区别、产品族概念、开闭原则的倾斜性"]
    ),
    "### 2.4 建造者模式（Builder）": (
        "将复杂对象的构建与表示分离，支持链式调用分步构建，解决多参数构造器问题。",
        "Builder 模式在目标类中定义静态内部类 Builder，持有与目标类相同的字段，每个 setter 返回 this 实现链式调用，最终 build() 调用私有构造方法创建不可变对象。它把构造过程拆成清晰步骤，避免 telescoping constructor（重叠构造器），也比 JavaBean setter 方式更安全（对象可一次性构造为不可变）。Lombok @Builder 注解自动生成建造者代码。",
        ["链式调用 builder().name(x).age(y).build() 可读性极强", "适合参数多（≥4个）、部分参数可选的场景", "构建与表示分离：相同构建过程可创建不同表示", "StringBuilder/StringBuffer 是建造者模式在 JDK 中的经典应用", "面试常考：与工厂模式区别、Lombok @Builder 原理、不可变对象构建"]
    ),
    "### 2.5 原型模式（Prototype）": (
        "通过复制现有对象创建新对象，避免重复执行昂贵的初始化逻辑。",
        "原型模式让对象实现 Cloneable 接口并重写 clone()，通过 super.clone() 进行位拷贝（浅拷贝）。Object.clone() 是 native 方法，直接在内存中复制二进制数据，不走构造方法，因此比 new 后逐字段赋值快。深拷贝需自行实现（序列化/反序列化或逐层 clone）。",
        ["super.clone() 是浅拷贝，引用类型字段仍指向原对象", "深拷贝实现：实现 Cloneable 逐层 clone，或序列化反序列化", "原型模式适合初始化成本高（如查库、加载配置）的对象", "Java 数组的 clone()、ArrayList.clone() 都是原型模式应用", "面试常考：浅拷贝 vs 深拷贝、clone 为什么不走构造方法、Serializable 实现深拷贝"]
    ),
    "### 3.2 装饰器模式（Decorator）": (
        "动态地给对象添加额外职责，比继承更灵活，是组合优于继承的体现。",
        "装饰器与被装饰对象实现同一接口，装饰器内部持有被装饰对象的引用，在调用委托前后增加增强逻辑。可以多层嵌套装饰，每层只关注一个增强点。装饰器模式在编译期不确定增强组合，运行时动态叠加；而继承是编译期静态确定的。Java IO 流体系（InputStream 嵌套 BufferedInputStream 嵌套 DataInputStream）是装饰器最经典的应用。",
        ["装饰器与被装饰者实现同一接口，持有被装饰者引用", "可多层嵌套，每层一个增强点，灵活组合", "与代理模式区别：装饰器关注功能增强叠加，代理关注访问控制", "Java IO 流是装饰器模式教科书级案例", "面试常考：装饰器 vs 代理 vs 继承、IO 流设计、多层嵌套顺序"]
    ),
    "### 3.3 适配器模式（Adapter）": (
        "将不兼容的接口转换为客户端期望的接口，让原本因接口不匹配而无法协作的类一起工作。",
        "适配器模式分三种：类适配器（继承 Adaptee 实现 Target，Java 单继承限制大）、对象适配器（持有 Adaptee 引用实现 Target，推荐）、接口适配器（用抽象类默认实现接口所有方法，子类只重写需要的）。适配器在不修改原有代码的前提下做接口转换，符合开闭原则。Spring MVC 的 HandlerAdapter 就是典型的适配器模式，它让不同类型的 Controller 都能被统一调用。",
        ["对象适配器（组合）优于类适配器（继承），符合组合复用原则", "适合老系统对接、第三方库接口转换、统一不同实现", "Spring MVC HandlerAdapter 适配不同 Controller 类型", "与装饰器区别：适配器改变接口，装饰器增强同接口功能", "面试常考：适配器三种形式、HandlerAdapter 原理、何时使用适配器"]
    ),
    "### 3.4 桥接模式（Bridge）": (
        "将抽象与实现分离，使两者可独立变化，避免多层继承导致的类爆炸。",
        "桥接模式把一个类的两个变化维度（如形状×颜色、消息类型×消息通道）拆成抽象层和实现层两个独立继承结构，抽象层持有实现层引用（桥接），两者通过组合连接而非继承绑定。新增一个维度的子类无需在另一个维度创建对应子类，类数量从 m×n 降为 m+n。JDBC 的 Driver 与 Connection 体系是桥接模式经典应用。",
        ["识别两个独立变化维度是使用桥接的前提", "组合代替多层继承，类数量从乘积变加和", "JDBC DriverManager 桥接不同数据库驱动", "与适配器区别：桥接在设计时分离抽象与实现，适配器在运行时兼容已有接口", "理解桥接关键：抽象层和实现层各自有继承树，中间用组合连接"]
    ),
    "### 3.5 外观模式（Facade）": (
        "为子系统的一组接口提供统一入口，简化客户端调用，降低客户端与子系统的耦合。",
        "外观模式在复杂子系统之上封装一个 Facade 类，内部编排多个子系统对象的调用顺序，客户端只需与 Facade 交互。外观不封装子系统功能，子系统仍可直接使用；外观只是提供一个更简单的入口。Spring 的 JdbcTemplate、String 类的 intern() 都体现了外观思想。",
        ["外观模式是迪米特法则（最少知识）的典型应用", "不阻止客户端直接使用子系统，只是提供更简单的选择", "适合复杂子系统入口、分层架构中的层间封装", "SLF4J 对各日志框架的封装可视为外观模式", "面试常考：外观 vs 中介者、外观在分层架构中的作用"]
    ),
    "### 3.6 组合模式（Composite）": (
        "将对象组合成树形结构表示部分-整体层次，使客户端对单个对象和组合对象的使用具有一致性。",
        "组合模式定义统一 Component 接口声明叶子和容器的共同行为，Leaf 实现叶子节点行为，Composite 持有子 Component 集合并实现 add/remove/操作委托。客户端面向 Component 编程，无需区分叶子还是容器，递归调用天然处理树形结构。文件系统（文件/文件夹）、菜单树、组织架构是典型应用。",
        ["透明式（Component 声明 add/remove）vs 安全式（只有 Composite 声明）", "递归遍历是组合模式的核心操作", "适合树形结构：菜单、目录、组织架构、DOM 树", "MyBatis 的 SqlNode（动态 SQL 节点）使用了组合模式", "面试常考：组合模式结构、透明 vs 安全、递归遍历实现"]
    ),
    "### 3.7 享元模式（Flyweight）": (
        "共享细粒度对象，减少内存占用，通过区分内部状态和外部状态实现复用。",
        "享元模式把对象状态分为内部状态（不变、可共享，如字符的字体内码）和外部状态（变化、由客户端传入，如字符位置）。享元工厂用 HashMap 缓存已创建的享元对象，请求时先查缓存。String 常量池、Integer 缓存池（-128~127）、数据库连接池都是享元思想的应用。",
        ["内部状态共享不变，外部状态由客户端传入不共享", "享元工厂用 Map 缓存，类似对象池但重点是共享而非复用", "String 常量池、Integer.valueOf 缓存是 JDK 中的享元", "线程池/连接池更接近对象池，享元侧重细粒度共享", "面试常考：内部 vs 外部状态、String 常量池、Integer 缓存范围"]
    ),
    "### 4.1 策略模式（Strategy）": (
        "定义一系列可互换的算法并分别封装，使算法可独立于使用它的客户端变化，消除大量 if-else。",
        "策略模式定义 Strategy 接口声明算法方法，具体策略类各自实现，Context 持有当前 Strategy 引用并委托执行。运行时可动态切换策略。策略模式把算法选择与算法实现分离，客户端通过设置不同策略改变行为，比继承和条件分支更灵活。Spring 中把所有策略实现注入 Map 按 key 选择是企业开发常用写法。",
        ["策略模式核心用途：消除多重 if-else/switch 分支", "Spring 中可注入 List<Strategy> 或 Map<String,Strategy> 动态选择", "与工厂模式区别：策略关注运行时行为切换，工厂关注对象创建", "与模板方法区别：策略用组合委托，模板用继承覆写", "面试常考：策略模式消除 if-else、Spring 中策略注入、与工厂/状态模式区别"]
    ),
    "### 4.2 观察者模式（Observer）": (
        "定义对象间一对多依赖，当一个对象状态变化时所有依赖者自动收到通知并更新，实现发布-订阅解耦。",
        "Subject 维护 Observer 列表并提供 attach/detach/notify 方法，状态变化时遍历调用每个 Observer 的 update。推模型主动传数据，拉模型 Observer 自己从 Subject 获取。JDK 有 Observable/Observer（已废弃），Spring ApplicationEvent/EventListener、Guava EventBus 是生产级实现。观察者模式解耦了事件发布者和消费者，但注意通知顺序、异常处理和内存泄漏（忘记注销）。",
        ["推模型（Subject 推送数据）vs 拉模型（Observer 主动拉取）", "Spring Event：ApplicationEvent + @EventListener 注解驱动", "异步事件用 @Async，注意异常不会传播给发布者", "注意注销观察者，防止内存泄漏", "面试常考：观察者 vs 发布订阅、Spring Event 实现、同步异步事件"]
    ),
    "### 4.3 模板方法模式（Template Method）": (
        "在抽象类中定义算法骨架（固定步骤顺序），将某些步骤延迟到子类实现，骨架不可变而步骤可定制。",
        "模板方法在抽象类中用 final 方法定义算法骨架（按固定顺序调用步骤方法），步骤方法分抽象方法（子类必须实现）、钩子方法（子类可选覆写）和具体方法（父类已实现）。子类通过覆写步骤定制行为但不能改变骨架顺序。这是好莱坞原则（Don't call us, we'll call you）的体现。Spring 的 JdbcTemplate、RedisTemplate、AbstractApplicationContext.refresh() 都是模板方法经典应用。",
        ["骨架方法用 final 修饰防止子类改变执行顺序", "钩子方法（hook）给子类可选的扩展点，返回 boolean 控制流程", "JdbcTemplate 把获取连接/Statement/关闭等固定步骤模板化，子类只处理结果映射", "与策略模式区别：模板用继承（静态），策略用组合（动态）", "面试常考：模板方法结构、JdbcTemplate 原理、钩子方法作用"]
    ),
    "### 4.4 责任链模式（Chain of Responsibility）": (
        "将请求沿处理器链传递，每个处理器决定处理或传给下一个，避免请求发送者与接收者耦合。",
        "每个 Handler 持有下一个 Handler 引用，handle 方法中若自己能处理则处理，否则调用 next.handle() 传递。链可在运行时动态组装。纯责任链（一个处理器处理或传递）与不纯责任链（每个处理器都可处理一部分，如 Filter）。Servlet Filter Chain、Spring Interceptor、Netty ChannelPipeline、MyBatis Plugin 都是责任链应用。",
        ["Servlet FilterChain 是不纯责任链：每个 Filter 处理后继续 chain.doFilter", "Spring Interceptor preHandle 返回 false 可中断链", "Netty ChannelPipeline 是双向链表结构的责任链", "注意链尾兜底处理，避免请求静默丢失", "面试常考：Filter vs Interceptor 区别、责任链组装方式、Netty Pipeline 原理"]
    ),
    "### 4.5 命令模式（Command）": (
        "将请求封装为对象，从而可用不同请求参数化客户端、支持排队、撤销和日志记录。",
        "命令模式把调用操作的对象（Invoker）与执行操作的对象（Receiver）解耦：Command 接口声明 execute()，具体命令持有 Receiver 并在 execute 中调用其方法。Invoker 只与 Command 交互，可把命令放入队列、记录日志或实现 undo。Runnable/Callable 是命令模式在 JDK 中的典型应用，Spring JdbcTemplate、线程池提交任务也体现了命令模式思想。",
        ["Command 对象封装了接收者和动作，可排队、记录、撤销", "Runnable/Callable 是最常见的命令模式接口", "宏命令（MacroCommand）可组合多个命令批量执行", "事务回滚、编辑器 Ctrl+Z 撤销是命令模式典型场景", "面试常考：命令模式结构、Runnable 与命令模式、撤销实现"]
    ),
    "### 4.6 状态模式（State）": (
        "对象内部状态改变时改变其行为，看起来像是改变了类，将状态判断逻辑分散到各状态类中。",
        "状态模式把每个状态封装为独立 State 类，Context 持有当前 State 引用并委托给它处理请求，状态切换由 State 内部决定（设置 Context 的下一个状态）。它消除了大量 if-else 状态判断，新增状态只需加类。与策略模式结构几乎相同，但语义不同：策略由客户端选择可互换，状态由上下文自动切换、状态间有依赖流转关系。订单状态机、工作流引擎是典型应用。",
        ["状态模式与策略模式结构相同，语义不同：状态自动流转，策略外部选择", "状态切换逻辑放在 State 类内部（持有 Context 引用）", "适合状态多（≥3个）且状态行为复杂的场景", "Spring StateMachine 是状态模式的框架级实现", "面试常考：状态 vs 策略区别、状态机实现、消除状态 if-else"]
    ),
    "### 4.7 迭代器模式（Iterator）": (
        "顺序访问集合元素而不暴露集合内部结构，统一不同集合的遍历方式。",
        "迭代器模式定义 Iterator 接口（hasNext/next/remove），具体集合实现自己的 Iterator（通常作为内部类），聚合对象提供 createIterator 工厂方法。客户端面向 Iterator 编程，无需关心底层是数组、链表还是树。Java 的 Iterator/Iterable、增强 for 循环都是迭代器模式应用。",
        ["Iterable 接口的 iterator() 是工厂方法，返回 Iterator", "增强 for 循环要求对象实现 Iterable", "fail-fast 机制：modCount 检测并发修改抛 ConcurrentModificationException", "fail-safe：CopyOnWriteArrayList 迭代器使用快照不抛异常", "面试常考：fail-fast vs fail-safe、Iterator vs ListIterator、Iterable 与 Iterator 区别"]
    ),
    "### 4.8 中介者模式（Mediator）": (
        "用中介对象封装一组对象的交互，使对象间不显式引用，降低多对多耦合。",
        "中介者模式把多个 Colleague 之间的网状通信改为星型通信：所有 Colleague 只与 Mediator 通信，由 Mediator 协调转发。Colleague 之间不直接依赖，依赖关系集中到 Mediator。MVC 中 Controller 是 View 和 Model 的中介者，聊天室服务端是各客户端的中介者。但中介者容易膨胀为上帝对象。",
        ["将网状依赖改为星型依赖，Colleague 之间解耦", "MVC Controller 是 View 与 Model 的中介者", "中介者本身可能变得复杂（上帝对象风险），需注意职责边界", "与外观模式区别：中介者封装同事间双向交互，外观单向简化子系统入口", "适合多对象紧密耦合形成网状依赖的场景"]
    ),
    "### 4.9 备忘录模式（Memento）": (
        "在不破坏封装性的前提下捕获并保存对象内部状态，以便之后恢复，实现撤销/回滚。",
        "备忘录模式有三个角色：Originator（原发器，创建备忘录并可从备忘录恢复）、Memento（备忘录，存储状态，对外部不可读）、Caretaker（管理者，持有备忘录但不修改内容）。Java 中可用序列化实现深拷贝备忘录。Spring Webflow 的 state、数据库事务回滚、编辑器撤销栈都是备忘录思想。",
        ["备忘录对外部封装状态细节，只有原发器能读写", "宽接口（原发器可访问全部状态）vs 窄接口（管理者只能传递）", "序列化实现备忘录：ObjectOutputStream 深拷贝", "注意备忘录内存开销，可只保存增量状态", "应用：事务回滚、游戏存档、编辑器撤销、Spring Webflow"]
    ),
    "### 4.10 访问者模式（Visitor）": (
        "在不改变元素类的前提下定义作用于这些元素的新操作，将数据结构与操作解耦。",
        "访问者模式利用双重分派（double dispatch）：Element 定义 accept(Visitor) 在方法中调用 visitor.visit(this)（this 是具体类型），Visitor 为每种 Element 定义 visit 方法。新增操作只需加 Visitor 实现类，无需改 Element；但新增 Element 类型需改所有 Visitor。适合元素结构稳定但操作频繁变化的场景，如编译器 AST 处理、ASM 字节码操作。",
        ["双重分派：accept 调 visit(this)，两次多态确定具体方法", "加操作容易（新 Visitor），加元素困难（改所有 Visitor）", "ASM ClassReader/ClassVisitor 是访问者模式经典应用", "与注解处理器配合用于代码生成和静态分析", "面试常考：双重分派原理、访问者适用场景、ASM 中的 Visitor"]
    ),
    "### 4.11 解释器模式（Interpreter）": (
        "定义语言的文法表示并构建解释器来解释语言中的句子，适合简单文法解析。",
        "解释器模式将文法规则表示为抽象表达式类层次：TerminalExpression（终结符，如变量/常量）和 NonterminalExpression（非终结符，如加减运算），通过组合表达式构建抽象语法树（AST），context 存储全局信息。正则表达式 Pattern/Matcher、SQL 解析器、SpEL 表达式、规则引擎都使用了解释器模式思想。实际开发中一般用表达式引擎库（Aviator、QLExpress）而非手写。",
        ["终结符表达式（变量/常量）vs 非终结符表达式（运算/逻辑）", "通过组合模式构建 AST，递归解释执行", "Pattern/Matcher、SpEL、Spring ExpressionParser 是应用案例", "复杂文法维护困难，生产中优先用 Aviator/QLExpress/Drools", "面试常考：解释器模式结构、正则表达式引擎、表达式语言"]
    ),
}

# ============================================================
# MyBatis-Plus
# ============================================================
mybatis_plus = {
    "### 2.5 代码生成器（AutoGenerator）": (
        "根据数据库表自动生成 Entity/Mapper/Service/Controller 全套代码，消除重复 CRUD 样板代码。",
        "AutoGenerator 读取数据库元数据（表名、列名、类型、注释），通过模板引擎（Freemarker/Velocity）按预设模板生成各层代码文件。新版（3.5.1+）使用 FastAutoGenerator 流式配置，支持自定义模板、命名策略、字段填充策略。生成后可在生成的基础上修改，避免从零搭建。",
        ["FastAutoGenerator.create() 流式配置，比旧版更简洁", "可自定义模板路径和输出目录，支持多表批量生成", "命名策略：下划线转驼峰、表名前缀过滤、逻辑删除字段配置", "建议首次生成后手动维护，避免重复生成覆盖自定义代码", "面试常考：代码生成器配置、自动填充字段、逻辑删除实现"]
    ),
    "### 3.2 增删改查": (
        "BaseMapper/IService 提供开箱即用的 CRUD 方法，单表操作零 SQL 实现。",
        "BaseMapper 提供 insert/deleteById/updateById/selectById/selectList 等方法，方法名根据泛型 Entity 解析表名和主键。IService 在 Mapper 之上封装了批量操作（saveBatch）、链式查询（lambdaQuery）和分页。方法命名通过 MyBatis 的 MapperProxy 动态代理转发到 SqlSession，最终由 MyBatis-Plus 的 SqlInjector 在启动时注入通用 CRUD 的 MappedStatement。",
        ["BaseMapper 是 Mapper 层通用方法，IService 是 Service 层增强", "lambdaQuery/lambdaUpdate 用方法引用避免硬编码字段名", "saveBatch 默认 1000 条一批，可配置 batchSize", "Wrapper 条件构造器：QueryWrapper/LambdaQueryWrapper/UpdateWrapper", "面试常考：BaseMapper 与 IService 区别、lambda 链式查询原理、批量插入优化"]
    ),
    "### 3.4 自定义 SQL（XML）": (
        "复杂查询在 XML 中手写 SQL，与 MP 通用方法共存，兼顾便捷与灵活。",
        "MP 完全兼容原生 MyBatis XML 映射：在 mapper 目录下编写 XML，namespace 指向 Mapper 接口，手写 resultMap 和 SQL。MP 的 Wrapper 条件可通过 ${ew.customSqlSegment} 拼接到自定义 SQL 中，实现通用条件 + 自定义查询的组合。分页查询可传入 Page 对象配合自定义 SQL。",
        ["XML 放 resources/mapper 目录，application.yml 配置 mapper-locations", "Wrapper 条件可通过 @Param(Constants.WRAPPER) 传入 XML 用 ${ew.customSqlSegment}", "自定义 SQL 也能使用 MP 分页插件，传入 Page 参数即可", "复杂联表查询建议用 XML 而非注解 SQL，可读性更好", "面试常考：MP 与原生 MyBatis 共存、Wrapper 传入 XML、多表分页"]
    ),
    "### 3.6 多数据源": (
        "通过 @DS 注解在不同数据源间动态切换，适用于多库、读写分离场景。",
        "dynamic-datasource-spring-boot-starter 基于 AbstractRoutingDataSource 实现动态路由：启动时配置多个数据源并放入 Map，@DS 注解通过 AOP 拦截，在方法执行前将数据源 key 放入 ThreadLocal，determineCurrentLookupKey() 读取 ThreadLocal 决定使用哪个数据源。支持 @DS 加在类或方法上（方法优先），支持嵌套切换和事务内切换（需注意事务管理器配置）。",
        ["@DS(\"slave\") 注解切换数据源，可标注在 Service 方法或类上", "底层基于 AbstractRoutingDataSource + ThreadLocal", "读写分离：写操作 @DS(\"master\")，查询 @DS(\"slave\")", "跨数据源事务需用 seata 或不保证强一致性", "面试常考：动态数据源原理、@DS 实现、读写分离方案、事务问题"]
    ),
}

# ============================================================
# Spring Boot
# ============================================================
spring_boot = {
    "### 2.7 参数校验": (
        "通过 JSR-303/JSR-380 注解声明式校验请求参数，避免在业务代码中编写大量 if 判空逻辑。",
        "Spring Boot 集成 Hibernate Validator 作为 JSR-303 实现：Controller 参数加 @Valid/@Validated 触发校验，字段上标注 @NotNull/@NotBlank/@Size/@Email 等约束注解。校验失败抛 MethodArgumentNotValidException，由全局异常处理器统一返回错误信息。支持分组校验（groups）、嵌套校验（@Valid 标注在嵌套对象上）和自定义校验注解。",
        ["@Valid 用在 @RequestBody，@Validated 用在 @RequestParam/@PathVariable", "分组校验：接口定义 Update/Insert 分组，@Validated(Update.class)", "嵌套校验需在嵌套对象字段上加 @Valid", "自定义校验：实现 ConstraintValidator 接口 + 自定义注解", "面试常考：@Valid vs @Validated、分组校验、全局异常处理校验错误"]
    ),
    "### 3.1 项目结构与启动类": (
        "约定优于配置的项目结构和启动类是 Spring Boot 应用的入口，自动扫描和自动配置的基础。",
        "@SpringBootApplication 是组合注解，包含 @SpringBootConfiguration（标识配置类）、@EnableAutoConfiguration（启用自动配置）、@ComponentScan（组件扫描）。启动类放在根包下，默认扫描所在包及子包。SpringApplication.run() 启动嵌入式容器、执行 ApplicationContextInitializer 和 ApplicationListener、刷新 IoC 容器。",
        ["启动类放根包，@ComponentScan 默认扫描启动类所在包及子包", "@SpringBootApplication = @Configuration + @EnableAutoConfiguration + @ComponentScan", "分层结构：controller/service/mapper/entity/config/common", "可通过 @SpringBootApplication(scanBasePackages=...) 自定义扫描包", "面试常考：启动类注解组成、自动扫描原理、Bean 注册流程"]
    ),
    "### 3.2 RESTful API 开发": (
        "用 HTTP 方法语义化表达 CRUD 操作，@RestController 统一返回 JSON，构建规范的 REST 接口。",
        "@RestController = @Controller + @ResponseBody，所有方法返回值通过 HttpMessageConverter 序列化为 JSON（默认 Jackson）。@GetMapping/@PostMapping/@PutMapping/@DeleteMapping 映射 HTTP 方法，@PathVariable 取路径参数，@RequestParam 取查询参数，@RequestBody 取请求体。Spring MVC 通过 DispatcherServlet 统一分发，HandlerMapping 找到对应 Controller 方法，HandlerAdapter 执行。",
        ["@RestController 返回值自动转 JSON，无需每个方法加 @ResponseBody", "RESTful 语义：GET 查询、POST 新增、PUT 更新、DELETE 删除", "统一响应体 Result<T>（code/message/data）+ 全局异常处理器", "接口版本管理：/api/v1/xxx 或 Header 版本", "面试常考：@RestController 原理、HttpMessageConverter、RESTful 规范"]
    ),
    "### 3.6 单元测试与集成测试": (
        "通过 @SpringBootTest 等注解分层测试，确保代码质量，支持切片测试和 Mock 依赖。",
        "spring-boot-starter-test 集成 JUnit 5、Mockito、AssertJ、Spring Test。@SpringBootTest 启动完整 Spring 上下文做集成测试；@WebMvcTest 只加载 Web 层切片测试 Controller；@DataJpaTest/@MybatisPlusTest 测试持久层。@MockBean 替换容器中的 Bean 为 Mock 对象，@Mock 纯单元测试不启动 Spring。测试类用 @Test 标注，断言用 AssertJ 的 assertThat 流式 API。",
        ["@SpringBootTest 启动完整容器（慢），切片测试（@WebMvcTest）只加载部分（快）", "@MockBean 替换 Spring Bean，@Mock 纯 Mockito 不启动容器", "AssertJ assertThat 流式断言比 JUnit assertEquals 更可读", "TestRestTemplate/WebTestClient 做端到端 HTTP 测试", "面试常考：@SpringBootTest vs @WebMvcTest、@MockBean vs @Mock、集成测试配置"]
    ),
    "### 3.8 常用配置项": (
        "application.yml 集中管理服务器端口、数据源、日志、Jackson 等配置，支持多环境切换。",
        "Spring Boot 加载 application.yml/properties 顺序：命令行参数 > 操作系统环境变量 > jar 外 config 目录 > jar 内配置。spring.profiles.active 激活特定环境配置（application-dev.yml）。配置项通过 @Value(\"${key:default}\") 或 @ConfigurationProperties 批量绑定到对象。宽松绑定规则（kebab-case 自动映射 camelCase）。",
        ["多环境配置：application-{profile}.yml + spring.profiles.active=dev", "@ConfigurationProperties(prefix=\"xxx\") 批量绑定，优于散落的 @Value", "配置优先级：命令行 > 环境变量 > 外部 config > 内部配置", "随机值：${random.int}，占位符：${app.name:默认值}", "面试常考：配置加载顺序、多环境切换、@ConfigurationProperties vs @Value"]
    ),
}

# ============================================================
# Spring Cloud
# ============================================================
spring_cloud = {
    "### 3.2 OpenFeign 服务调用": (
        "声明式 HTTP 客户端，用注解接口替代 RestTemplate 手写调用，像调用本地方法一样调用远程服务。",
        "OpenFeign 在启动时通过 @EnableFeignClients 扫描 @FeignClient 接口，JDK 动态代理生成代理实例。调用方法时，根据 @RequestMapping 注解构造 RequestTemplate，经 Encoder 序列化请求体、拦截器添加 Header，由 HTTP 客户端（默认 URLConnection，可替换 OkHttp/HttpClient）发送请求，Decoder 反序列化响应。集成 Ribbon/LoadBalancer 做客户端负载均衡，集成 Sentinel 做熔断降级。",
        ["@FeignClient(name=\"service-name\") 声明接口，启动时动态代理生成实现", "Spring Cloud LoadBalancer 做客户端负载均衡（轮询/随机）", "可配置 OkHttp/HttpClient 连接池提升性能", "fallback/fallbackFactory 实现熔断降级，Sentinel 集成更完善", "面试常考：Feign 动态代理原理、负载均衡、超时配置、传参方式"]
    ),
    "### 3.3 Sentinel 熔断限流": (
        "阿里巴巴开源的流量控制组件，提供限流、熔断降级、系统保护等能力，保障微服务稳定性。",
        "Sentinel 通过 Sentinel-Aspect 切面拦截 @SentinelResource 注解或 SphU.entry() 调用，构建 ProcessorSlotChain 责任链：NodeSelectorSlot 建立调用链树、ClusterBuilderSlot 构建集群节点、StatisticSlot 滑动窗口实时统计、FlowSlot 根据规则判断限流、DegradeSlot 判断熔断、SystemSlot 判断系统保护。限流算法支持滑动窗口和漏桶，熔断支持慢调用比例/异常比例/异常数策略。Dashboard 提供实时监控和规则推送。",
        ["限流算法：滑动窗口（LeapArray）统计 QPS，支持直接/关联/链路流控", "熔断策略：慢调用比例（RT 阈值）、异常比例、异常数，有熔断时长和探测恢复", "@SentinelResource 定义资源，blockHandler 处理限流，fallback 处理异常", "规则持久化：Nacos/Apollo 配置中心推送，避免 Dashboard 重启丢失", "面试常考：Sentinel 限流算法、SlotChain 责任链、熔断与 Hystrix 区别、规则持久化"]
    ),
    "### 3.4 Gateway 网关配置": (
        "Spring Cloud Gateway 基于 WebFlux 的响应式 API 网关，统一处理路由、鉴权、限流、跨域。",
        "Gateway 基于 Spring WebFlux + Reactor Netty，核心是三条组件：Route（路由：ID+目标 URI+Predicate+Filter）、Predicate（断言：匹配请求的 Path/Header/Method 等）、Filter（过滤器：修改请求/响应）。请求到达后由 RoutePredicateHandlerMapping 匹配路由，经 FilteringWebHandler 组装 GatewayFilter 责任链处理。全局过滤器（GlobalFilter）对所有路由生效，可实现鉴权、限流。",
        ["基于 Netty 响应式非阻塞，不要在 Gateway 中写阻塞代码", "Route = Predicate（断言匹配）+ Filter（过滤处理）+ URI（目标地址）", "全局 Filter 实现 GlobalFilter + @Order 做鉴权、日志、限流", "跨域配置：globalcors 或 CorsWebFilter", "面试常考：Gateway vs Zuul、Predicate/Filter 原理、响应式模型、网关鉴权"]
    ),
    "### 3.5 Nacos 配置中心": (
        "Nacos Config 集中管理各环境配置，支持动态刷新，配置变更实时推送到服务实例。",
        "Nacos Config 启动时根据 spring.application.name 和 profile 拉取配置（DataId = name-profile.yml），通过长轮询（Long Polling）监听配置变更：客户端发起超时 30s 的 HTTP 请求，服务端有变更立即返回，无变更挂起直到超时。配置变更后发布 RefreshEvent，@RefreshScope 标注的 Bean 重新创建以注入新值，@NacosValue 也支持自动刷新。",
        ["DataId 格式：${prefix}-${spring.profiles.active}.${file-extension}", "长轮询（Long Polling）：客户端 30s 挂起，服务端变更立即返回", "@RefreshScope 让配置 Bean 支持动态刷新（代理模式，访问时重新创建）", "配置共享：spring.cloud.nacos.config.shared-configs 引入公共配置", "面试常考：长轮询原理、@RefreshScope 机制、配置热更新、与 Apollo 对比"]
    ),
    "### 3.7 网关鉴权": (
        "在网关层统一处理身份认证和权限校验，避免每个微服务重复实现鉴权逻辑。",
        "网关鉴权通常基于 JWT：客户端登录获取 Token，后续请求在 Header 携带 Authorization: Bearer <token>。Gateway 全局过滤器拦截请求，用 JWT 解析库验证签名和过期时间，将用户 ID/角色解析后放入请求 Header 转发给下游服务。白名单路径（登录/注册）跳过鉴权。细粒度按钮权限由下游服务根据角色判断。也可在网关集成 OAuth2 资源服务器。",
        ["JWT 结构：Header.Payload.Signature，无状态、服务端无需存储 Session", "全局过滤器解析 Token 并将用户信息放入 Header 透传下游", "白名单路径配置在 Nacos 或配置文件，支持 Path 匹配", "网关只做认证（你是谁），下游服务做授权（你能做什么）", "面试常考：JWT 原理、网关统一鉴权、Token 刷新、与 Session 区别"]
    ),
    "### 3.8 微服务监控": (
        "通过 Spring Boot Actuator + Prometheus + Grafana 实现指标采集、存储和可视化监控。",
        "Actuator 暴露 /actuator/prometheus 端点输出 Micrometer 格式指标（JVM、HTTP、CPU、自定义业务指标）。Prometheus 定时拉取（pull）这些指标存入时序数据库，通过 PromQL 查询聚合。Grafana 配置 Prometheus 为数据源，用 Dashboard 可视化。链路追踪用 Spring Cloud Sleuth（或 Micrometer Tracing）+ Zipkin/Jaeger，日志聚合用 ELK。",
        ["Actuator 暴露健康/指标/信息端点，生产环境注意安全（只暴露必要端点）", "Micrometer 是指标门面，支持 Counter/Gauge/Timer/Summary", "Prometheus pull 模式拉取指标，Grafana 可视化", "链路追踪：TraceId 贯穿全链路，Span 记录每跳耗时", "面试常考：监控体系架构、Micrometer 指标类型、链路追踪原理、Prometheus pull vs push"]
    ),
}

# ============================================================
# Spring 原理
# ============================================================
spring_principle = {
    "### 3.1 依赖注入": (
        "IoC 容器管理 Bean 的创建和依赖关系，对象不自己 new 依赖而是由容器注入，实现解耦。",
        "依赖注入有三种方式：构造器注入（推荐，不可变、易测试、循环依赖启动即报错）、Setter 注入（可选依赖）、字段注入（@Autowired 字段，不推荐）。Spring 在 Bean 创建后通过 BeanPostProcessor 的 postProcessProperties（AutowiredAnnotationBeanPostProcessor）解析 @Autowired，在 DefaultListableBeanFactory 中查找匹配 Bean 并反射注入。构造器注入的循环依赖无法解决（对象还没创建完），Setter/字段注入的单例循环依赖通过三级缓存解决。",
        ["构造器注入推荐：final 字段不可变、强制依赖不遗漏、便于单元测试", "@Autowired byType，@Resource byName，@Inject（JSR-330）", "循环依赖：三级缓存（singletonObjects/earlySingletonObjects/singletonFactories）", "@Lazy 延迟注入可打破循环依赖", "面试常考：三种注入方式对比、三级缓存原理、为什么构造器注入循环依赖无法解决"]
    ),
    "### 3.3 事件机制": (
        "基于观察者模式实现 ApplicationEvent 发布订阅，让 Bean 之间松耦合通信。",
        "ApplicationEventPublisher.publishEvent() 发布事件，SimpleApplicationEventMulticaster  multicastEvent() 遍历 ApplicationListener（或 @EventListener 注解的方法）执行。默认同步执行（发布者线程阻塞直到所有监听者完成），配置 @Async 或自定义线程池可异步。事件支持泛型（ApplicationEvent<T>）和条件（@EventListener(condition=\"...\")）。Spring 内部大量使用事件（ContextRefreshedEvent、ApplicationReadyEvent）。",
        ["@EventListener 注解驱动，无需实现 ApplicationListener 接口", "默认同步：监听者异常会影响发布者，异步需 @Async + 线程池", "事务绑定事件：@TransactionalEventListener(phase=AFTER_COMMIT)", "适合解耦：注册后发短信、下单后扣库存等跨模块通知", "面试常考：事件同步异步、@TransactionalEventListener、事件机制实现原理"]
    ),
    "### 3.5 AOP 切面开发": (
        "通过切面把日志、事务、权限等横切逻辑从业务代码中抽离，声明式地织入目标方法。",
        "Spring AOP 基于动态代理：有接口用 JDK 动态代理（Proxy.newProxyInstance），无接口用 CGLIB（生成子类字节码）。@Aspect 切面定义 @Pointcut 切点（execution 表达式）和通知（@Before/@After/@AfterReturning/@AfterThrowing/Around）。Spring 启动时由 AnnotationAwareAspectJAutoProxyCreator（BeanPostProcessor）扫描切面，为匹配的 Bean 创建代理对象，调用时拦截方法执行拦截器链（MethodInterceptor 责任链）。",
        ["@Around 环绕通知最强大，可控制是否执行目标方法、修改参数和返回值", "JDK 代理基于接口，CGLIB 基于继承（不能代理 final 类/方法）", "同类内方法调用不走代理（this 调用），需 AopContext.currentProxy() 或自注入", "Spring AOP 是运行时织入，AspectJ 是编译时/类加载时织入（功能更强）", "面试常考：JDK vs CGLIB、AOP 代理创建时机、通知执行顺序、this 调用失效"]
    ),
    "### 3.8 Spring 扩展点": (
        "Spring 提供丰富的扩展接口，允许在 Bean 生命周期各阶段插入自定义逻辑，是框架集成和二次开发的基础。",
        "主要扩展点按生命周期顺序：BeanFactoryPostProcessor（BeanDefinition 加载后、实例化前修改定义，如 PropertySourcesPlaceholderConfigurer）、BeanPostProcessor（Bean 初始化前后拦截，如 AOP 代理创建、@Autowired 处理）、InitializingBean/@PostConstruct（初始化回调）、SmartLifecycle（容器启动/停止回调）、ApplicationListener（事件监听）。Spring Boot 的自动配置大量使用这些扩展点。",
        ["BeanFactoryPostProcessor 在 Bean 实例化前修改 BeanDefinition", "BeanPostProcessor 在初始化前后处理 Bean，AOP 和依赖注入都基于它", "@PostConstruct 是 JSR-250 注解，afterPropertiesSet 是 Spring 接口", "FactoryBean 可自定义复杂 Bean 的创建逻辑（如 MyBatis MapperFactoryBean）", "面试常考：BeanPostProcessor 作用、BeanFactoryPostProcessor vs BeanPostProcessor、Spring 扩展点顺序"]
    ),
}

# ============================================================
# 并发编程
# ============================================================
concurrency = {
    "### 3.2 synchronized 与 ReentrantLock": (
        "两种最核心的互斥锁机制，保证原子性和可见性，ReentrantLock 提供更灵活的锁控制。",
        "synchronized 是 JVM 层面的内置锁：基于 Monitor 对象（monitorenter/monitorexit 字节码），锁升级路径为无锁→偏向锁→轻量级锁（CAS 自旋）→重量级锁（操作系统互斥量），可重入、自动释放。ReentrantLock 是 JDK 层面的 AQS 锁：基于 AQS 同步器（volatile state + CLH 队列），支持公平/非公平、可中断（lockInterruptibly）、超时尝试（tryLock）、多条件变量（Condition）。",
        ["synchronized 自动释放锁，ReentrantLock 必须在 finally 中 unlock", "锁升级：偏向锁（单线程）→轻量级锁（CAS 自旋）→重量级锁（线程挂起）", "ReentrantLock 支持公平锁（按等待队列顺序）、可中断、超时、多 Condition", "synchronized 锁对象：this（实例方法）、Class（静态方法）、任意对象（代码块）", "面试常考：锁升级过程、AQS 原理、synchronized vs ReentrantLock、偏向锁撤销"]
    ),
    "### 3.5 CompletableFuture 异步编程": (
        "Java 8 引入的异步编程工具，支持链式调用、组合编排和异常处理，简化多步骤异步任务。",
        "CompletableFuture 实现 Future 和 CompletionStage 接口，默认使用 ForkJoinPool.commonPool()（也可指定线程池）。thenApply/thenAccept/thenRun 链式处理结果，thenCompose 扁平化异步结果（类似 flatMap），thenCombine 合并两个独立任务，allOf/anyOf 等待多个任务。每个操作返回新的 CompletableFuture，操作间通过无锁栈（Treiber stack）管理依赖，前置任务完成后通过 postComplete 触发后续任务。",
        ["thenApply 有返回值，thenAccept 消费无返回，thenRun 不关心结果", "thenCompose vs thenCombine：前者串联依赖，后者合并独立", "allOf 等待全部完成，anyOf 等待任一完成", "自定义线程池避免 commonPool 被阻塞任务占满", "面试常考：CompletableFuture 常用方法、线程池选择、异常处理（exceptionally/handle）、异步回调原理"]
    ),
}


def run():
    tasks = [
        (os.path.join(BASE, "02-后端开发", "设计模式知识点系统梳理_优化版.md"), design_patterns, True, False, ""),
        (os.path.join(BASE, "02-后端开发", "MyBatis-Plus 知识点系统梳理_优化版.md"), mybatis_plus, False, False, ""),
        (os.path.join(BASE, "02-后端开发", "Spring Boot 知识点系统梳理_优化版.md"), spring_boot, False, False, ""),
        (os.path.join(BASE, "02-后端开发", "Spring Cloud微服务 知识点系统梳理_优化版.md"), spring_cloud, False, False, ""),
        (os.path.join(BASE, "02-后端开发", "Spring原理 知识点系统梳理_优化版.md"), spring_principle, False, False, ""),
        (os.path.join(BASE, "02-后端开发", "并发编程 知识点系统梳理_优化版.md"), concurrency, False, False, ""),
    ]
    for path, cmap, add_note, add_summary, summary in tasks:
        lines, added = expand(path, cmap, add_note, add_summary, summary)
        print(f"  {os.path.basename(path)}: {lines} lines, {added} blocks added")


if __name__ == "__main__":
    run()
