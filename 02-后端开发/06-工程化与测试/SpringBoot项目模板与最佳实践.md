---
title: SpringBoot项目模板与最佳实践
tags: [代码模板, SpringBoot, Java, 后端, 脚手架, 最佳实践]
category: 后端
created: 2026-08-27
updated: 2026-08-27
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 常规
pre: []
aliases: [SpringBoot项目模板与最佳实践]
---

# SpringBoot项目模板与最佳实践

> **文档说明**：企业级SpringBoot项目模板，包含标准目录结构、统一响应、异常处理、参数校验、日志规范、配置管理、代码规范。
>
> **适用人群**：Java后端开发者、需要快速搭建项目的工程师
>
> **前置知识**：SpringBoot基础

---

## 一、项目目录结构

```
src/main/java/com/example/project/
├── ProjectApplication.java          # 启动类
├── common/                          # 公共模块
│   ├── constant/                    # 常量
│   ├── enums/                       # 枚举
│   ├── exception/                   # 异常定义
│   ├── result/                      # 统一响应
│   └── util/                        # 工具类
├── config/                          # 配置类
│   ├── MybatisPlusConfig.java
│   ├── RedisConfig.java
│   ├── WebMvcConfig.java
│   └── ThreadPoolConfig.java
├── controller/                      # 控制层
│   └── UserController.java
├── service/                         # 业务层
│   ├── UserService.java
│   └── impl/
│       └── UserServiceImpl.java
├── mapper/                          # 数据访问层
│   └── UserMapper.java
├── entity/                          # 实体类
│   ├── User.java
│   └── dto/                         # 数据传输对象
│   └── vo/                          # 视图对象
├── interceptor/                     # 拦截器
├── filter/                          # 过滤器
└── aspect/                          # 切面

src/main/resources/
├── application.yml                  # 主配置
├── application-dev.yml              # 开发环境
├── application-prod.yml             # 生产环境
├── mapper/                          # MyBatis XML
└── logback-spring.xml               # 日志配置
```

---

## 二、统一响应封装

```java
// 统一响应结果
@Data
@AllArgsConstructor
@NoArgsConstructor
public class Result<T> {
    private Integer code;
    private String message;
    private T data;

    public static <T> Result<T> success() {
        return new Result<>(200, "success", null);
    }

    public static <T> Result<T> success(T data) {
        return new Result<>(200, "success", data);
    }

    public static <T> Result<T> error(String message) {
        return new Result<>(500, message, null);
    }

    public static <T> Result<T> error(Integer code, String message) {
        return new Result<>(code, message, null);
    }
}

// 业务状态码枚举
@Getter
@AllArgsConstructor
public enum ResultCode {
    SUCCESS(200, "操作成功"),
    PARAM_ERROR(400, "参数错误"),
    UNAUTHORIZED(401, "未授权"),
    FORBIDDEN(403, "禁止访问"),
    NOT_FOUND(404, "资源不存在"),
    SERVER_ERROR(500, "服务器内部错误"),
    BUSINESS_ERROR(1000, "业务异常");

    private final Integer code;
    private final String message;
}
```

---

## 三、全局异常处理

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    // 业务异常
    @ExceptionHandler(BusinessException.class)
    public Result<Void> handleBusinessException(BusinessException e) {
        log.warn("业务异常: {}", e.getMessage());
        return Result.error(e.getCode(), e.getMessage());
    }

    // 参数校验异常
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<Void> handleValidException(MethodArgumentNotValidException e) {
        String msg = e.getBindingResult().getFieldErrors().stream()
                .map(FieldError::getDefaultMessage)
                .collect(Collectors.joining(", "));
        return Result.error(ResultCode.PARAM_ERROR.getCode(), msg);
    }

    // 未知异常
    @ExceptionHandler(Exception.class)
    public Result<Void> handleException(Exception e) {
        log.error("系统异常", e);
        return Result.error(ResultCode.SERVER_ERROR);
    }
}

// 自定义业务异常
@Getter
public class BusinessException extends RuntimeException {
    private final Integer code;

    public BusinessException(String message) {
        super(message);
        this.code = ResultCode.BUSINESS_ERROR.getCode();
    }

    public BusinessException(Integer code, String message) {
        super(message);
        this.code = code;
    }
}
```

---

## 四、参数校验

```java
// DTO使用校验注解
@Data
public class UserCreateDTO {
    @NotBlank(message = "用户名不能为空")
    @Size(min = 2, max = 20, message = "用户名长度2-20")
    private String username;

    @NotBlank(message = "密码不能为空")
    @Pattern(regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).{8,20}$",
             message = "密码需包含大小写字母和数字，8-20位")
    private String password;

    @Email(message = "邮箱格式错误")
    private String email;

    @NotNull(message = "年龄不能为空")
    @Min(value = 0, message = "年龄不能小于0")
    @Max(value = 150, message = "年龄不能大于150")
    private Integer age;
}

// Controller使用@Valid
@PostMapping
public Result<UserVO> createUser(@Valid @RequestBody UserCreateDTO dto) {
    return Result.success(userService.create(dto));
}
```

---

## 五、配置管理

```yaml
# application.yml
spring:
  profiles:
    active: dev
  application:
    name: project-name

server:
  port: 8080
  servlet:
    context-path: /api

mybatis-plus:
  mapper-locations: classpath:mapper/*.xml
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
  global-config:
    db-config:
      logic-delete-field: deleted
      logic-delete-value: 1
      logic-not-delete-value: 0

# application-dev.yml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/db_dev?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
    username: root
    password: root
  redis:
    host: localhost
    port: 6379

logging:
  level:
    com.example.project: debug
```

---

## 六、日志规范

```xml
<!-- logback-spring.xml -->
<configuration>
    <springProperty scope="context" name="APP_NAME" source="spring.application.name"/>

    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n</pattern>
        </encoder>
    </appender>

    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/${APP_NAME}.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>logs/${APP_NAME}.%d{yyyy-MM-dd}.%i.log</fileNamePattern>
            <maxFileSize>100MB</maxFileSize>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n</pattern>
        </encoder>
    </appender>

    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
    </root>
</configuration>
```

### 日志使用规范

```java
// 正确：使用占位符，避免字符串拼接
log.info("用户登录成功, userId={}, username={}", userId, username);

// 错误：字符串拼接（性能差）
log.info("用户登录成功, userId=" + userId + ", username=" + username);

// 异常日志必须带异常对象
log.error("用户注册失败, userId={}", userId, e);  // e必须最后一个参数
```

---

## 七、Controller模板

```java
@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
@Validated
public class UserController {

    private final UserService userService;

    @PostMapping
    public Result<UserVO> create(@Valid @RequestBody UserCreateDTO dto) {
        return Result.success(userService.create(dto));
    }

    @GetMapping("/{id}")
    public Result<UserVO> getById(@PathVariable Long id) {
        return Result.success(userService.getById(id));
    }

    @GetMapping
    public Result<PageResult<UserVO>> page(
            @RequestParam(defaultValue = "1") Integer pageNum,
            @RequestParam(defaultValue = "10") Integer pageSize,
            UserQueryDTO query) {
        return Result.success(userService.page(pageNum, pageSize, query));
    }

    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id,
                               @Valid @RequestBody UserUpdateDTO dto) {
        userService.update(id, dto);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        userService.delete(id);
        return Result.success();
    }
}
```

---

## 八、Service模板

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class UserServiceImpl implements UserService {

    private final UserMapper userMapper;
    private final RedisTemplate<String, Object> redisTemplate;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public UserVO create(UserCreateDTO dto) {
        // 1. 校验
        User exist = userMapper.selectByUsername(dto.getUsername());
        if (exist != null) {
            throw new BusinessException("用户名已存在");
        }
        // 2. 转换
        User user = new User();
        BeanUtils.copyProperties(dto, user);
        user.setPassword(BCrypt.hashpw(dto.getPassword()));
        // 3. 保存
        userMapper.insert(user);
        // 4. 返回
        return convertToVO(user);
    }

    @Override
    public UserVO getById(Long id) {
        // 缓存优先
        String key = "user:" + id;
        UserVO cached = (UserVO) redisTemplate.opsForValue().get(key);
        if (cached != null) return cached;

        User user = userMapper.selectById(id);
        if (user == null) throw new BusinessException(ResultCode.NOT_FOUND);

        UserVO vo = convertToVO(user);
        redisTemplate.opsForValue().set(key, vo, 30, TimeUnit.MINUTES);
        return vo;
    }

    private UserVO convertToVO(User user) {
        UserVO vo = new UserVO();
        BeanUtils.copyProperties(user, vo);
        return vo;
    }
}
```

---

## 九、代码规范

| 规范 | 说明 |
|------|------|
| 命名 | 类名大驼峰，方法/变量小驼峰，常量全大写下划线 |
| 分层 | Controller不写业务逻辑，Service不直接返回Entity |
| 事务 | @Transactional加在Service方法，rollbackFor=Exception.class |
| 异常 | 业务异常抛BusinessException，系统异常全局捕获 |
| 日志 | 关键操作必须记录日志，异常日志带异常对象 |
| 注释 | 类/公共方法必须有JavaDoc，复杂逻辑行内注释 |
| 工具类 | 抽象到util包，构造方法私有 |
| 魔法值 | 用常量或枚举替代 |

---

## 关联文档

- [[SpringBoot知识点系统梳理_优化版]] — SpringBoot完整知识
- [[Java问题排查手册]] — 问题排查
- [[后端开发面试题库与答案解析]] — 面试题
- [[Dockerfile最佳实践]] — 容器化

---

> 💡 项目模板是团队效率的基础。建议将此模板推送到Git作为脚手架，新项目直接clone使用。统一的代码规范和异常处理能大幅降低维护成本。
