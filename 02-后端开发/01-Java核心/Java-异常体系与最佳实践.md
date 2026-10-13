---
title: Java-异常体系与最佳实践
tags: [Java, 异常处理, 自定义异常, 最佳实践, 原子笔记]
category: 后端开发
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["Java-应用性能调优实战", "SpringValidation-参数校验", "Java-数据加密与脱敏"]
aliases: [Java-异常体系与最佳实践]
---

# Java-异常体系与最佳实践

> **文档说明**：系统讲解 Java 异常体系的完整知识，包括异常分类、处理机制、自定义异常、异常链、Spring 全局异常处理，以及生产级最佳实践和常见反模式。
>
> **适用人群**：Java 开发者、后端工程师、需要编写健壮 Java 代码的开发者
>
> **前置知识**：[[Java-应用性能调优实战]]、[[SpringValidation-参数校验]]、[[Java-数据加密与脱敏]]

---

## 一、概述

### 1. 异常体系结构

```
java.lang.Throwable（所有异常和错误的父类）
├── Error（错误，程序无法处理，不建议捕获）
│   ├── OutOfMemoryError
│   ├── StackOverflowError
│   ├── NoClassDefFoundError
│   ├── LinkageError
│   └── VirtualMachineError
│
└── Exception（异常，程序可以处理）
    ├── RuntimeException（运行时异常/非受检异常）
    │   ├── NullPointerException
    │   ├── IllegalArgumentException
    │   ├── IllegalStateException
    │   ├── IndexOutOfBoundsException
    │   ├── ClassCastException
    │   ├── ArithmeticException
    │   ├── ConcurrentModificationException
    │   └── UnsupportedOperationException
    │
    └── 受检异常（Checked Exception，必须处理）
        ├── IOException
        ├── SQLException
        ├── InterruptedException
        ├── FileNotFoundException
        ├── ParseException
        └── 自定义受检异常
```

### 2. 受检 vs 非受检异常

| 维度 | 受检异常（Checked） | 非受检异常（Unchecked） |
|------|---------------------|------------------------|
| **继承** | Exception（非 RuntimeException） | RuntimeException / Error |
| **编译检查** | 编译器强制处理（try-catch 或 throws） | 不强制 |
| **代表** | IOException、SQLException | NullPointerException、IllegalArgumentException |
| **可恢复性** | 通常可恢复（重试、降级） | 通常是程序错误（bug） |
| **设计哲学** | 期望调用者处理 | 不期望调用者处理 |
| **使用场景** | 外部资源失败（IO、网络、数据库） | 编程错误（参数非法、状态错误） |

### 3. 异常处理的基本原则

```
异常处理核心原则：
1. 异常只用于异常情况，不要用异常控制流程
2. 要么捕获处理，要么抛出，不要吞掉异常
3. 捕获具体异常，不要捕获 Exception/Throwable
4. 异常信息要包含上下文，便于排查
5. 清理资源用 finally 或 try-with-resources
6. 不要在 finally 中 return（会覆盖 try 的返回）
7. 异常转换时保留 cause（异常链）
8. 性能敏感场景避免频繁抛异常（异常创建有开销）
```

---

## 二、异常处理机制

### 1. try-catch-finally

```java
// 基本结构
try {
    // 可能抛出异常的代码
    int result = divide(10, 0);
} catch (ArithmeticException e) {
    // 捕获特定异常
    System.err.println("除数不能为零: " + e.getMessage());
} catch (Exception e) {
    // 兜底（放在最后）
    log.error("未知错误", e);
} finally {
    // 无论是否异常都会执行（清理资源）
    System.out.println("清理资源");
}

// 多异常合并捕获（Java 7+）
try {
    process();
} catch (IOException | SQLException e) {
    log.error("IO或数据库错误", e);
}
```

### 2. try-with-resources（推荐）

```java
// Java 7+ 自动关闭实现 AutoCloseable 的资源
try (FileInputStream fis = new FileInputStream("file.txt");
     BufferedReader reader = new BufferedReader(new InputStreamReader(fis))) {
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
} catch (IOException e) {
    log.error("读取文件失败", e);
}
// 自动关闭 reader 和 fis（逆序关闭）

// 自定义资源实现 AutoCloseable
public class MyResource implements AutoCloseable {
    @Override
    public void close() throws Exception {
        // 清理逻辑
    }
}
```

### 3. throws 声明

```java
// 受检异常必须声明 throws，或在方法内捕获
public void readFile(String path) throws IOException, FileNotFoundException {
    FileInputStream fis = new FileInputStream(path);
    // ...
}

// 调用者必须处理
try {
    readFile("test.txt");
} catch (IOException e) {
    log.error("读取失败", e);
}

// 非受检异常不需要声明（但可以声明，文档作用）
public void validate(String input) throws IllegalArgumentException {
    if (input == null) {
        throw new IllegalArgumentException("input 不能为空");
    }
}
```

---

## 三、自定义异常

### 1. 自定义运行时异常（推荐）

```java
// 业务异常基类
public class BusinessException extends RuntimeException {
    private final String errorCode;

    public BusinessException(String errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }

    public BusinessException(String errorCode, String message, Throwable cause) {
        super(message, cause);
        this.errorCode = errorCode;
    }

    public String getErrorCode() {
        return errorCode;
    }
}

// 具体业务异常
public class UserNotFoundException extends BusinessException {
    public UserNotFoundException(Long userId) {
        super("USER_NOT_FOUND", "用户不存在: " + userId);
    }
}

public class InsufficientBalanceException extends BusinessException {
    public InsufficientBalanceException(BigDecimal balance, BigDecimal amount) {
        super("INSUFFICIENT_BALANCE",
            String.format("余额不足: 余额=%s, 需要=%s", balance, amount));
    }
}

// 使用
public User getUser(Long userId) {
    User user = userRepository.findById(userId);
    if (user == null) {
        throw new UserNotFoundException(userId);
    }
    return user;
}
```

### 2. 自定义受检异常

```java
// 受检异常（用于可恢复的外部错误）
public class PaymentException extends Exception {
    public PaymentException(String message) {
        super(message);
    }

    public PaymentException(String message, Throwable cause) {
        super(message, cause);
    }
}

// 使用时必须声明 throws
public void processPayment(Order order) throws PaymentException {
    try {
        paymentGateway.charge(order);
    } catch (GatewayException e) {
        throw new PaymentException("支付失败: " + e.getMessage(), e);
    }
}
```

### 3. 异常枚举（统一错误码）

```java
public enum ErrorCode {
    // 通用错误 1xxxx
    SUCCESS("0", "成功"),
    PARAM_INVALID("10001", "参数无效"),
    UNAUTHORIZED("10002", "未授权"),
    FORBIDDEN("10003", "禁止访问"),
    NOT_FOUND("10004", "资源不存在"),
    INTERNAL_ERROR("10005", "系统内部错误"),

    // 用户模块 2xxxx
    USER_NOT_FOUND("20001", "用户不存在"),
    USER_ALREADY_EXISTS("20002", "用户已存在"),
    PASSWORD_INCORRECT("20003", "密码错误"),

    // 订单模块 3xxxx
    ORDER_NOT_FOUND("30001", "订单不存在"),
    ORDER_STATUS_INVALID("30002", "订单状态无效");

    private final String code;
    private final String message;

    ErrorCode(String code, String message) {
        this.code = code;
        this.message = message;
    }

    public String getCode() { return code; }
    public String getMessage() { return message; }
}

// 统一异常
public class AppException extends RuntimeException {
    private final ErrorCode errorCode;

    public AppException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
    }

    public AppException(ErrorCode errorCode, String detail) {
        super(errorCode.getMessage() + ": " + detail);
        this.errorCode = errorCode;
    }

    public AppException(ErrorCode errorCode, Throwable cause) {
        super(errorCode.getMessage(), cause);
        this.errorCode = errorCode;
    }
}
```

---

## 四、异常链与转换

### 1. 异常链（cause）

```java
// 异常转换时保留原始异常（cause）
try {
    userRepository.save(user);
} catch (DataAccessException e) {
    // 包装为业务异常，保留原始异常
    throw new BusinessException("DB_ERROR", "数据库操作失败", e);
}

// 打印完整异常链
catch (Exception e) {
    log.error("操作失败", e);  // 自动打印 cause 链
}

// 手动遍历异常链
Throwable cause = e;
while (cause != null) {
    System.out.println(cause.getClass().getName() + ": " + cause.getMessage());
    cause = cause.getCause();
}
```

### 2. 异常转换模式

```java
// 受检异常转非受检异常（Spring 风格）
public User findById(Long id) {
    try {
        return userRepository.findById(id).orElseThrow();
    } catch (SQLException e) {
        // 受检异常转为运行时异常
        throw new DataAccessException("查询用户失败", e);
    }
}

// 统一异常包装
@Service
public class OrderService {
    public Order createOrder(OrderRequest request) {
        try {
            // 业务逻辑
        } catch (BusinessException e) {
            throw e;  // 业务异常直接抛出
        } catch (Exception e) {
            // 其他异常包装为系统异常
            throw new SystemException("创建订单失败", e);
        }
    }
}
```

---

## 五、Spring 全局异常处理

### 1. @ControllerAdvice + @ExceptionHandler

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    // 处理业务异常
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(BusinessException e) {
        log.warn("业务异常: code={}, message={}", e.getErrorCode(), e.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
            .body(ApiResponse.error(e.getErrorCode(), e.getMessage()));
    }

    // 处理参数校验异常
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidationException(
            MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
            .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
            .collect(Collectors.joining("; "));
        log.warn("参数校验失败: {}", message);
        return ResponseEntity.badRequest()
            .body(ApiResponse.error("PARAM_INVALID", message));
    }

    // 处理未授权
    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ApiResponse<Void>> handleAccessDenied(AccessDeniedException e) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN)
            .body(ApiResponse.error("FORBIDDEN", "无权限访问"));
    }

    // 兜底处理（放最后）
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleException(Exception e) {
        log.error("系统异常", e);  // 完整堆栈日志
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(ApiResponse.error("INTERNAL_ERROR", "系统繁忙，请稍后重试"));
    }
}

// 统一响应
@Data
@AllArgsConstructor
public class ApiResponse<T> {
    private String code;
    private String message;
    private T data;

    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>("0", "成功", data);
    }

    public static <T> ApiResponse<T> error(String code, String message) {
        return new ApiResponse<>(code, message, null);
    }
}
```

### 2. 自定义响应状态码

```java
// 异常携带 HTTP 状态码
@ResponseStatus(HttpStatus.NOT_FOUND)
public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String message) {
        super(message);
    }
}

// 或在 @ExceptionHandler 中指定
@ExceptionHandler(ResourceNotFoundException.class)
@ResponseStatus(HttpStatus.NOT_FOUND)
public ApiResponse<Void> handleNotFound(ResourceNotFoundException e) {
    return ApiResponse.error("NOT_FOUND", e.getMessage());
}
```

---

## 六、常见异常与排查

### 1. NullPointerException（NPE）

```java
// NPE 的常见原因和预防

// ❌ 可能 NPE
String name = user.getAddress().getCity().toUpperCase();

// ✅ 防御性编程
if (user != null && user.getAddress() != null && user.getAddress().getCity() != null) {
    String city = user.getAddress().getCity().toUpperCase();
}

// ✅ Optional（Java 8+）
String city = Optional.ofNullable(user)
    .map(User::getAddress)
    .map(Address::getCity)
    .map(String::toUpperCase)
    .orElse("未知");

// ✅ Objects.requireNonNull（参数校验）
public void setName(String name) {
    this.name = Objects.requireNonNull(name, "name 不能为空");
}

// ✅ 工具类
String city = StringUtils.defaultIfBlank(user.getAddress().getCity(), "未知");
```

### 2. OutOfMemoryError（OOM）

```
OOM 常见原因：
1. 堆内存不足：大集合、缓存无上限
2. 元空间不足：动态生成类过多
3. 直接内存溢出：NIO/Netty
4. 线程栈溢出：线程数过多
5. GC 开销过大：对象创建频繁

排查工具：
- jmap -heap <pid>：查看堆使用
- jmap -dump:format=b,file=heap.hprof <pid>：堆转储
- jstat -gcutil <pid> 1000：GC 统计
- jstack <pid>：线程栈
- MAT / VisualVM：分析堆转储

预防：
- 合理设置 -Xmx/-Xms
- 缓存设置上限（Caffeine/Guava Cache）
- 流式处理大文件，不要全量加载
- 监控内存使用，告警
```

### 3. 其他常见异常

| 异常 | 原因 | 解决方案 |
|------|------|---------|
| **ClassCastException** | 类型转换错误 | 用 instanceof 检查、泛型 |
| **IndexOutOfBoundsException** | 数组/集合越界 | 检查 size/length、边界判断 |
| **IllegalArgumentException** | 参数非法 | 参数校验、@Valid |
| **IllegalStateException** | 状态错误 | 检查对象状态、状态机 |
| **ConcurrentModificationException** | 遍历时修改集合 | 用 Iterator.remove()、并发集合 |
| **UnsupportedOperationException** | 调用不支持的方法 | 检查集合类型（如 Arrays.asList） |
| **InterruptedException** | 线程被中断 | 正确处理中断、恢复中断状态 |
| **NumberFormatException** | 字符串转数字失败 | 正则校验、try-catch |
| **DateTimeParseException** | 日期解析失败 | 校验格式、指定时区 |

---

## 七、最佳实践

### 1. 异常设计规范

- [ ] **优先用非受检异常**：业务异常继承 RuntimeException
- [ ] **异常要有意义**：异常名能说明问题（UserNotFoundException）
- [ ] **异常信息包含上下文**：如 "用户不存在: userId=123"
- [ ] **异常层次清晰**：基类 + 具体异常
- [ ] **统一错误码**：用枚举管理错误码
- [ ] **不要过度使用异常**：正常流程不要用异常控制

### 2. 异常处理规范

- [ ] **具体异常优先**：catch 具体异常，不要 catch Exception
- [ ] **不要吞异常**：catch 后至少要日志记录
- [ ] **不要只 printStackTrace**：用日志框架（slf4j）
- [ ] **资源用 try-with-resources**：自动关闭
- [ ] **finally 不要 return**：会覆盖 try 的返回值
- [ ] **异常转换保留 cause**：便于排查根因
- [ ] **不要在循环中 try-catch**：性能差，提前校验

### 3. 日志规范

```java
// ✅ 正确的异常日志
catch (UserNotFoundException e) {
    log.warn("用户不存在: userId={}", userId, e);  // 带参数和异常
}

catch (Exception e) {
    log.error("处理订单失败: orderId={}", orderId, e);  // 最后一个参数是异常，自动打印堆栈
}

// ❌ 错误的日志
catch (Exception e) {
    log.error("错误: " + e.getMessage());  // 没有堆栈，字符串拼接
    e.printStackTrace();  // 不用日志框架
}

catch (Exception e) {
    log.error("错误", e.getMessage());  // 第二个参数是 String，不会打印堆栈
}
```

### 4. 性能注意事项

```
异常的性能开销：
- 创建异常对象会收集堆栈（Throwable.fillInStackTrace()）
- 堆栈收集开销较大（微秒级）
- 频繁抛异常会影响性能

优化建议：
1. 正常流程用返回值/Optional，不要用异常
2. 可预期的错误用错误码，不用异常
3. 重写 fillInStackTrace 减少开销（仅在不需要堆栈时）
4. 热点代码避免异常驱动
5. JIT 会优化频繁抛出的异常（栈顶替换）

// 不需要堆栈的异常（性能优化）
public class FastException extends RuntimeException {
    @Override
    public Throwable fillInStackTrace() {
        return this;  // 不收集堆栈
    }
}
```

---

## 八、常见反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| **catch (Exception e) {}** | 吞掉异常，问题被隐藏 | 至少记录日志，或重新抛出 |
| **catch (Throwable t)** | 捕获 Error（如 OOM），不应处理 | 只捕获 Exception |
| **e.printStackTrace()** | 输出到 stderr，不可控 | 用日志框架 |
| **finally { return; }** | 覆盖 try 的返回值 | finally 只做清理，不 return |
| **用异常控制流程** | 性能差，代码难读 | 用条件判断/返回值 |
| **catch 后抛 new Exception(e.getMessage())** | 丢失原始堆栈 | 保留 cause: new Exception(msg, e) |
| **方法 throws Exception** | 太宽泛，调用者无法处理 | 抛出具体异常 |
| **catch 后继续执行** | 状态可能不一致 | 失败后应该终止或回滚 |
| **异常信息太泛** | "操作失败"无法排查 | 包含上下文参数 |
| **过度包装异常** | 异常链太深，难读 | 只在必要时包装 |

---

## 九、关联笔记

### Java 核心
- [[Java-应用性能调优实战]] · [[Java-数据加密与脱敏]] · [[Java-异常体系与最佳实践]]
- [[Java-并发编程实战]] · [[Java-网络编程与NIO]]

### Spring 生态
- [[SpringValidation-参数校验]] · [[认证与授权原理-OAuth2-JWT]] · [[API安全最佳实践]]

### 通用
- [[Python-异常处理与错误体系]] · [[常见攻击与防御手段]] · [[密码学基础-对称非对称哈希]]

### 导航
- [[MOC-后端开发]] · [[MOC-计算机基础]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握本文 Java 异常体系 → 深入 [[SpringValidation-参数校验]] 参数校验 → 学习 [[认证与授权原理-OAuth2-JWT]] 安全认证 → 实践 [[Java-并发编程实战]] 并发异常处理 → 研究 [[Java-应用性能调优实战]] 性能优化 → 构建健壮的 Java 后端开发能力。
