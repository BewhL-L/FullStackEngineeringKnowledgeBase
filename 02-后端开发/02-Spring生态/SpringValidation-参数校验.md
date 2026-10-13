---
title: SpringValidation-参数校验
tags: [Spring Boot, 参数校验, Validation, JSR-303, Bean Validation, 原子笔记]
category: 后端开发
created: 2026-08-12
updated: 2026-09-01
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: []
aliases: [SpringValidation-参数校验]
---



# SpringValidation-参数校验

> **文档说明**：系统讲解 Spring Boot 参数校验，包括 JSR-303 规范、常用校验注解、分组校验、自定义注解、级联校验、集合校验、全局异常处理、手动校验，以及最佳实践和常见问题。
>
> **适用人群**：Java 后端开发者、Spring Boot 开发者、需要构建健壮 API 的开发者
>
> **前置知识**：[[SpringBoot-核心原理与自动配置]]、[[Java-异常体系与最佳实践]]、[[RESTfulAPI设计原则]]

---

## 一、概述

### 1. 为什么需要参数校验

```
参数校验的重要性：

安全层面：
- 防止非法输入导致 SQL 注入、XSS、命令注入
- 防止越权访问（ID 篡改）
- 防止恶意数据破坏系统

业务层面：
- 保证数据完整性和一致性
- 提前发现错误，减少业务逻辑中的判断
- 提供清晰的错误提示

性能层面：
- 尽早拒绝无效请求，避免浪费计算资源
- 减少数据库查询和业务处理

用户体验：
- 清晰的错误信息，告诉用户哪里错了、怎么改
- 前端友好的错误格式

不做参数校验的后果：
- NullPointerException（空指针）
- 数据不一致（脏数据入库）
- 安全漏洞（注入攻击）
- 难以排查的 Bug
- 糟糕的用户体验
```

### 2. JSR-303 / Bean Validation

```
Bean Validation 规范：
- JSR-303（Bean Validation 1.0）
- JSR-349（Bean Validation 1.1）
- JSR-380（Bean Validation 2.0）
- Jakarta Bean Validation 3.0（Jakarta EE 9+）

参考实现：
- Hibernate Validator（最主流，Spring Boot 默认）
- Apache BVal

Spring Boot 集成：
- spring-boot-starter-validation 自动引入 Hibernate Validator
- 在 Controller 方法参数上加 @Valid 或 @Validated 触发校验
- 校验失败抛出 MethodArgumentNotValidException 或 ConstraintViolationException

校验层级：
1. 前端校验：用户体验，即时反馈（可被绕过，不可依赖）
2. Controller 层校验：参数格式、基本规则（本文重点）
3. Service 层校验：业务规则校验
4. 数据库层校验：约束（唯一键、非空、外键）

原则：不信任任何外部输入，每层都做校验
```

---

## 二、常用校验注解

### 1. 空值检查

```java
// 空值检查注解
public class UserDTO {

    // @NotNull：不能为 null，但可以为空字符串 ""
    @NotNull(message = "ID 不能为空")
    private Long id;

    // @NotBlank：不能为 null，且去除首尾空格后长度 > 0
    @NotBlank(message = "用户名不能为空")
    private String username;

    // @NotEmpty：不能为 null，且长度 > 0（集合/数组/字符串）
    @NotEmpty(message = "角色列表不能为空")
    private List<String> roles;

    // 区别：
    // @NotNull: " "  ✓（空格通过）
    // @NotEmpty: " "  ✓（空格通过，长度>0）
    // @NotBlank: " "  ✗（去除空格后为空）
}
```

### 2. 数值检查

```java
public class ProductDTO {

    // @Min / @Max：最小值/最大值（适用于数值类型）
    @Min(value = 0, message = "价格不能小于 0")
    @Max(value = 999999, message = "价格不能超过 999999")
    private BigDecimal price;

    // @DecimalMin / @DecimalMax：支持小数
    @DecimalMin(value = "0.01", message = "折扣不能小于 0.01")
    @DecimalMax(value = "1.0", message = "折扣不能大于 1.0")
    private BigDecimal discount;

    // @Positive / @PositiveOrZero：正数/非负数
    @Positive(message = "数量必须为正数")
    private Integer quantity;

    // @Negative / @NegativeOrZero：负数/非正数
    @NegativeOrZero(message = "余额不能为正")
    private Integer balance;

    // @Range（Hibernate Validator 扩展）：范围
    @Range(min = 1, max = 100, message = "页码必须在 1-100 之间")
    private Integer page;
}
```

### 3. 字符串检查

```java
public class ArticleDTO {

    // @Size：长度范围（字符串/集合/数组/Map）
    @Size(min = 2, max = 50, message = "标题长度必须在 2-50 之间")
    private String title;

    @Size(max = 2000, message = "内容不能超过 2000 字符")
    private String content;

    // @Pattern：正则表达式
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phone;

    @Pattern(regexp = "^[a-zA-Z0-9_-]{4,16}$", message = "用户名格式不正确")
    private String username;

    // @Email：邮箱格式（Hibernate Validator 扩展）
    @Email(message = "邮箱格式不正确")
    private String email;

    // @URL：URL 格式（Hibernate Validator 扩展）
    @URL(message = "链接格式不正确")
    private String website;

    // @Length（Hibernate Validator 扩展）：字符串长度
    @Length(min = 6, max = 20, message = "密码长度必须在 6-20 之间")
    private String password;
}
```

### 4. 日期与布尔检查

```java
public class EventDTO {

    // @Future：必须是未来的日期
    @Future(message = "开始时间必须是未来")
    private LocalDateTime startTime;

    // @FutureOrPresent：现在或未来
    @FutureOrPresent(message = "报名截止时间不能是过去")
    private LocalDateTime deadline;

    // @Past：必须是过去的日期
    @Past(message = "出生日期必须是过去")
    private LocalDate birthday;

    // @PastOrPresent：过去或现在
    @PastOrPresent(message = "创建时间不能是未来")
    private LocalDateTime createdAt;

    // @AssertTrue：必须为 true
    @AssertTrue(message = "必须同意用户协议")
    private Boolean agreed;

    // @AssertFalse：必须为 false
    @AssertFalse(message = "不能勾选此选项")
    private Boolean blocked;
}
```

### 5. 完整示例

```java
// 完整的用户注册 DTO
public class UserRegisterDTO {

    @NotBlank(message = "用户名不能为空")
    @Size(min = 4, max = 20, message = "用户名长度必须在 4-20 之间")
    @Pattern(regexp = "^[a-zA-Z0-9_-]+$", message = "用户名只能包含字母、数字、下划线、连字符")
    private String username;

    @NotBlank(message = "密码不能为空")
    @Size(min = 8, max = 32, message = "密码长度必须在 8-32 之间")
    @Pattern(regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).*$",
             message = "密码必须包含大小写字母和数字")
    private String password;

    @NotBlank(message = "确认密码不能为空")
    private String confirmPassword;

    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;

    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phone;

    @NotNull(message = "年龄不能为空")
    @Min(value = 1, message = "年龄不能小于 1")
    @Max(value = 150, message = "年龄不能大于 150")
    private Integer age;

    @AssertTrue(message = "必须同意用户协议和隐私政策")
    private Boolean agreed;

    @Past(message = "出生日期必须是过去的日期")
    private LocalDate birthday;

    // getters and setters...
}
```

---

## 三、Spring Boot 集成

### 1. Controller 层校验

```java
@RestController
@RequestMapping("/api/users")
@Validated  // 类级别，用于方法参数校验（@RequestParam 等）
public class UserController {

    @PostMapping
    public ResponseEntity<UserVO> createUser(
            @RequestBody @Valid UserRegisterDTO dto) {  // @Valid 触发校验
        // 校验通过才会进入方法
        UserVO user = userService.create(dto);
        return ResponseEntity.ok(user);
    }

    @PutMapping("/{id}")
    public ResponseEntity<UserVO> updateUser(
            @PathVariable @Min(1) Long id,  // 路径参数校验
            @RequestBody @Valid UserUpdateDTO dto) {
        UserVO user = userService.update(id, dto);
        return ResponseEntity.ok(user);
    }

    @GetMapping
    public ResponseEntity<PageVO<UserVO>> listUsers(
            @RequestParam(defaultValue = "1") @Min(1) Integer page,
            @RequestParam(defaultValue = "10") @Min(1) @Max(100) Integer size,
            @RequestParam(required = false) @Size(max = 50) String keyword) {
        PageVO<UserVO> pageResult = userService.list(page, size, keyword);
        return ResponseEntity.ok(pageResult);
    }
}
```

### 2. @Valid vs @Validated

```
@Valid（javax.validation.Valid）：
- JSR-303 标准注解
- 支持级联校验（嵌套对象加 @Valid）
- 不支持分组校验（需要配合 groups 属性）
- 用于方法参数、字段

@Validated（org.springframework.validation.annotation.Validated）：
- Spring 提供的注解
- 支持分组校验（value 属性指定分组）
- 支持类级别（用于 @RequestParam/@PathVariable 校验）
- 不支持级联校验（嵌套对象需要 @Valid）
- 用于类、方法、参数

选择：
- Controller @RequestBody → @Valid（支持级联）或 @Validated（支持分组）
- 方法参数（@RequestParam）→ 类上加 @Validated
- 需要分组校验 → @Validated
- 需要级联校验 → @Valid（嵌套字段加 @Valid）
```

### 3. 级联校验

```java
// 嵌套对象校验
public class OrderDTO {

    @NotBlank(message = "订单号不能为空")
    private String orderNo;

    @NotNull(message = "用户信息不能为空")
    @Valid  // 级联校验：触发 UserInfoDTO 内部的校验
    private UserInfoDTO user;

    @NotEmpty(message = "订单项不能为空")
    @Valid  // 集合级联校验：每个元素都校验
    private List<OrderItemDTO> items;

    @Valid
    private AddressDTO address;
}

public class UserInfoDTO {
    @NotBlank(message = "用户名不能为空")
    private String name;

    @Email(message = "邮箱格式不正确")
    private String email;
}

public class OrderItemDTO {
    @NotNull(message = "商品 ID 不能为空")
    private Long productId;

    @Min(value = 1, message = "数量至少为 1")
    private Integer quantity;

    @DecimalMin(value = "0.01", message = "价格必须大于 0")
    private BigDecimal price;
}
```

---

## 四、分组校验

### 1. 分组定义

```java
// 定义分组接口（标记接口）
public interface ValidationGroups {
    interface Create {}   // 创建时校验
    interface Update {}   // 更新时校验
    interface Delete {}   // 删除时校验
    interface Query {}    // 查询时校验
}
```

### 2. 使用分组

```java
public class UserDTO {

    // 创建时必须为空（由系统生成），更新时必须有值
    @Null(message = "创建时 ID 必须为空", groups = ValidationGroups.Create.class)
    @NotNull(message = "更新时 ID 不能为空", groups = ValidationGroups.Update.class)
    private Long id;

    // 创建和更新都需要校验
    @NotBlank(message = "用户名不能为空", groups = {ValidationGroups.Create.class, ValidationGroups.Update.class})
    @Size(min = 4, max = 20, message = "用户名长度必须在 4-20 之间",
          groups = {ValidationGroups.Create.class, ValidationGroups.Update.class})
    private String username;

    // 创建时必须有密码，更新时可选
    @NotBlank(message = "密码不能为空", groups = ValidationGroups.Create.class)
    @Size(min = 8, max = 32, message = "密码长度必须在 8-32 之间",
          groups = ValidationGroups.Create.class)
    private String password;

    @Email(message = "邮箱格式不正确",
           groups = {ValidationGroups.Create.class, ValidationGroups.Update.class})
    private String email;
}
```

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @PostMapping
    public ResponseEntity<UserVO> create(
            @RequestBody @Validated(ValidationGroups.Create.class) UserDTO dto) {
        // 只校验 Create 分组的字段
        return ResponseEntity.ok(userService.create(dto));
    }

    @PutMapping("/{id}")
    public ResponseEntity<UserVO> update(
            @PathVariable Long id,
            @RequestBody @Validated(ValidationGroups.Update.class) UserDTO dto) {
        // 只校验 Update 分组的字段
        dto.setId(id);
        return ResponseEntity.ok(userService.update(dto));
    }
}
```

---

## 五、自定义校验注解

### 1. 定义注解

```java
// 自定义校验注解：手机号格式
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Constraint(validatedBy = {PhoneValidator.class})  // 指定校验器
public @interface Phone {

    // 校验失败的默认消息
    String message() default "手机号格式不正确";

    // 分组
    Class<?>[] groups() default {};

    // 负载（可以携带额外信息）
    Class<? extends Payload>[] payload() default {};
}
```

### 2. 实现校验器

```java
// 手机号校验器
public class PhoneValidator implements ConstraintValidator<Phone, String> {

    private static final Pattern PHONE_PATTERN = Pattern.compile("^1[3-9]\\d{9}$");

    @Override
    public void initialize(Phone constraintAnnotation) {
        // 初始化，可以读取注解的属性
    }

    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        // 空值由 @NotNull/@NotBlank 处理，这里直接通过
        if (value == null) {
            return true;
        }

        return PHONE_PATTERN.matcher(value).matches();
    }
}
```

### 3. 复杂自定义校验

```java
// 自定义注解：两次密码一致
@Target({ElementType.TYPE})  // 类级别注解
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Constraint(validatedBy = {PasswordMatchValidator.class})
public @interface PasswordMatch {
    String message() default "两次输入的密码不一致";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

// 校验器
public class PasswordMatchValidator implements ConstraintValidator<PasswordMatch, UserRegisterDTO> {

    @Override
    public boolean isValid(UserRegisterDTO dto, ConstraintValidatorContext context) {
        if (dto == null) return true;

        boolean valid = dto.getPassword() != null
                && dto.getPassword().equals(dto.getConfirmPassword());

        if (!valid) {
            // 自定义错误字段（默认是类级别，改为字段级别）
            context.disableDefaultConstraintViolation();
            context.buildConstraintViolationWithTemplate("两次输入的密码不一致")
                    .addPropertyNode("confirmPassword")
                    .addConstraintViolation();
        }

        return valid;
    }
}

// 使用
@PasswordMatch
public class UserRegisterDTO {
    private String password;
    private String confirmPassword;
    // ...
}
```

### 4. 常用自定义校验场景

```java
// 1. 枚举值校验
public class EnumValidator implements ConstraintValidator<EnumValue, String> {
    private Set<String> acceptedValues;

    @Override
    public void initialize(EnumValue annotation) {
        acceptedValues = Arrays.stream(annotation.enumClass().getEnumConstants())
                .map(Enum::name)
                .collect(Collectors.toSet());
    }

    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        return value == null || acceptedValues.contains(value);
    }
}

// 2. 身份证号校验
// 3. 统一社会信用代码校验
// 4. 银行卡号校验（Luhn 算法）
// 5. IP 地址校验
// 6. 日期范围校验（开始时间 < 结束时间）
// 7. 文件大小/类型校验
```

---

## 六、全局异常处理

### 1. 统一异常处理器

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    /**
     * 处理 @RequestBody @Valid 校验失败
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidationException(
            MethodArgumentNotValidException e) {

        // 获取所有校验错误
        List<FieldError> fieldErrors = e.getBindingResult().getFieldErrors();

        // 转换为字段 -> 错误消息的 Map
        Map<String, String> errors = fieldErrors.stream()
                .collect(Collectors.toMap(
                        FieldError::getField,
                        FieldError::getDefaultMessage,
                        (existing, replacement) -> existing  // 同字段取第一个
                ));

        // 取第一条错误消息作为提示
        String message = fieldErrors.isEmpty()
                ? "参数校验失败"
                : fieldErrors.get(0).getDefaultMessage();

        log.warn("参数校验失败: {}", errors);

        return ResponseEntity.badRequest()
                .body(ApiResponse.fail(400, message, errors));
    }

    /**
     * 处理 @Validated 方法参数校验失败（@RequestParam/@PathVariable）
     */
    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<ApiResponse<Void>> handleConstraintViolation(
            ConstraintViolationException e) {

        Map<String, String> errors = e.getConstraintViolations().stream()
                .collect(Collectors.toMap(
                        violation -> violation.getPropertyPath().toString(),
                        violation -> violation.getMessage(),
                        (existing, replacement) -> existing
                ));

        String message = e.getConstraintViolations().iterator().next().getMessage();

        log.warn("约束校验失败: {}", errors);

        return ResponseEntity.badRequest()
                .body(ApiResponse.fail(400, message, errors));
    }

    /**
     * 处理绑定异常（类型转换失败等）
     */
    @ExceptionHandler(BindException.class)
    public ResponseEntity<ApiResponse<Void>> handleBindException(BindException e) {
        Map<String, String> errors = e.getFieldErrors().stream()
                .collect(Collectors.toMap(
                        FieldError::getField,
                        FieldError::getDefaultMessage,
                        (existing, replacement) -> existing
                ));

        return ResponseEntity.badRequest()
                .body(ApiResponse.fail(400, "参数绑定失败", errors));
    }

    /**
     * 处理其他异常
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleException(Exception e) {
        log.error("系统异常", e);
        return ResponseEntity.status(500)
                .body(ApiResponse.fail(500, "系统繁忙，请稍后重试"));
    }
}
```

### 2. 统一响应格式

```java
// 统一响应结构
public class ApiResponse<T> {
    private Integer code;
    private String message;
    private T data;
    private Map<String, String> errors;  // 校验错误详情

    public static <T> ApiResponse<T> success(T data) {
        ApiResponse<T> response = new ApiResponse<>();
        response.setCode(200);
        response.setMessage("success");
        response.setData(data);
        return response;
    }

    public static <T> ApiResponse<T> fail(Integer code, String message) {
        ApiResponse<T> response = new ApiResponse<>();
        response.setCode(code);
        response.setMessage(message);
        return response;
    }

    public static <T> ApiResponse<T> fail(Integer code, String message,
                                            Map<String, String> errors) {
        ApiResponse<T> response = fail(code, message);
        response.setErrors(errors);
        return response;
    }
}
```

---

## 七、手动校验

### 1. 编程式校验

```java
@Service
public class UserService {

    private final Validator validator;

    public UserService(Validator validator) {
        this.validator = validator;
    }

    public void createUser(UserDTO dto) {
        // 手动校验
        Set<ConstraintViolation<UserDTO>> violations = validator.validate(dto);

        if (!violations.isEmpty()) {
            Map<String, String> errors = violations.stream()
                    .collect(Collectors.toMap(
                            v -> v.getPropertyPath().toString(),
                            ConstraintViolation::getMessage
                    ));
            throw new ValidationException("参数校验失败: " + errors);
        }

        // 业务逻辑...
    }

    // 校验指定分组
    public void updateUser(UserDTO dto) {
        Set<ConstraintViolation<UserDTO>> violations =
                validator.validate(dto, ValidationGroups.Update.class);

        if (!violations.isEmpty()) {
            throw new ValidationException("更新参数校验失败");
        }
    }

    // 校验单个属性
    public void validateUsername(String username) {
        Set<ConstraintViolation<UserDTO>> violations =
                validator.validateProperty(new UserDTO(), "username");
        // ...
    }
}
```

### 2. 工具类封装

```java
// 校验工具类
@Component
public class ValidationUtils {

    private static Validator validator;

    @Autowired
    public void setValidator(Validator validator) {
        ValidationUtils.validator = validator;
    }

    /**
     * 校验对象，失败抛出异常
     */
    public static <T> void validate(T obj, Class<?>... groups) {
        Set<ConstraintViolation<T>> violations = validator.validate(obj, groups);
        if (!violations.isEmpty()) {
            String message = violations.iterator().next().getMessage();
            throw new BusinessException(400, message);
        }
    }

    /**
     * 校验对象，返回错误列表
     */
    public static <T> Map<String, String> validateAndReturn(T obj, Class<?>... groups) {
        Set<ConstraintViolation<T>> violations = validator.validate(obj, groups);
        return violations.stream()
                .collect(Collectors.toMap(
                        v -> v.getPropertyPath().toString(),
                        ConstraintViolation::getMessage,
                        (a, b) -> a
                ));
    }

    /**
     * 校验是否通过
     */
    public static <T> boolean isValid(T obj, Class<?>... groups) {
        return validator.validate(obj, groups).isEmpty();
    }
}
```

---

## 八、最佳实践

### 1. 设计规范

- [ ] **DTO 分层**：请求用 RequestDTO，响应用 ResponseVO，不复用实体类
- [ ] **注解优先**：能用注解校验的不用代码判断
- [ ] **message 清晰**：错误消息要具体，告诉用户怎么改（"密码长度必须在8-32之间"而非"密码无效"）
- [ ] **分组校验**：创建/更新/查询用不同分组，避免字段冗余
- [ ] **级联校验**：嵌套对象加 @Valid，确保深度校验
- [ ] **自定义注解**：重复使用的校验逻辑封装为自定义注解
- [ ] **空值处理**：自定义校验器中空值返回 true（由 @NotNull 处理）
- [ ] **前端配合**：前端也做校验提升体验，但后端必须校验
- [ ] **统一异常处理**：全局捕获校验异常，返回统一格式
- [ ] **国际化**：错误消息支持 i18n（ValidationMessages.properties）

### 2. 性能与安全

- [ ] **避免过度校验**：不要对内部调用的方法也做校验（浪费性能）
- [ ] **校验顺序**：先做简单的格式校验，再做复杂的业务校验
- [ ] **正则安全**：避免灾难性回溯的正则（ReDoS 攻击）
- [ ] **文件校验**：上传文件校验大小、类型、内容（不只看扩展名）
- [ ] **SQL 注入防护**：参数校验 + 参数化查询，双重防护
- [ ] **XSS 防护**：字符串长度限制 + 输出编码
- [ ] **越权防护**：ID 参数校验 + 服务端权限校验

### 3. 常见校验模式

```
常用校验模式：

1. 字符串：
   - @NotBlank + @Size + @Pattern（格式）
   - 用户名：@NotBlank @Size(min=4,max=20) @Pattern(字母数字下划线)
   - 手机号：@Pattern(^1[3-9]\d{9}$)
   - 邮箱：@Email

2. 数值：
   - @NotNull + @Min + @Max
   - 价格：@NotNull @DecimalMin("0.01")
   - 数量：@NotNull @Positive
   - 分页：@Min(1) @Max(100)

3. 日期：
   - @NotNull + @Future/@Past
   - 开始时间：@Future
   - 结束时间：自定义注解（> 开始时间）

4. 集合：
   - @NotEmpty + @Valid（级联）+ @Size
   - 列表：@NotEmpty @Valid List<ItemDTO>

5. 布尔：
   - @AssertTrue（必须同意协议）
```

---

## 九、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **校验不生效** | 未加 @Valid/@Validated / 依赖未引入 | 加 @Valid、引入 spring-boot-starter-validation |
| **嵌套对象不校验** | 未加 @Valid 级联注解 | 嵌套字段加 @Valid |
| **分组校验不生效** | 用了 @Valid 而非 @Validated | 分组校验用 @Validated(Group.class) |
| **@RequestParam 不校验** | 类上未加 @Validated | Controller 类上加 @Validated |
| **校验异常未被捕获** | 异常类型不对 | MethodArgumentNotValidException（@RequestBody）/ ConstraintViolationException（@RequestParam） |
| **自定义注解不生效** | @Constraint 未指定校验器 | 加 @Constraint(validatedBy = XxxValidator.class) |
| **message 不显示** | 未配置 message / 国际化文件 | 注解加 message 属性、配置 ValidationMessages.properties |
| **@NotBlank 不生效** | 用在非 String 类型 | @NotBlank 只能用在 String，其他用 @NotNull/@NotEmpty |
| **@Email 不严格** | 默认正则较宽松 | 用 @Pattern 自定义更严格的邮箱正则 |
| **校验顺序不确定** | 注解校验无固定顺序 | 用 @GroupSequence 定义校验顺序，或分层次校验 |
| **集合元素不校验** | 未加 @Valid | 集合字段加 @Valid（如 List<@Valid ItemDTO>） |
| **校验性能差** | 校验逻辑复杂 / 重复校验 | 优化正则、缓存校验器、避免重复校验 |
| **文件上传不校验** | MultipartFile 无标准注解 | 自定义 @FileSize/@FileType 注解、手动校验 |
| **日期校验不通过** | 时区/格式问题 | 统一时区、@JsonFormat 指定格式、用 LocalDateTime |
| **跨字段校验** | 单字段注解无法实现 | 类级别自定义注解（如密码一致、日期范围） |
| **校验消息国际化** | 硬编码中文 message | 用 {key} 占位符、配置 ValidationMessages_zh_CN.properties |
| **@Valid 和 @Validated 混淆** | 不清楚区别 | @Valid 支持级联、@Validated 支持分组和类级别 |
| **校验通过但业务报错** | 只做了格式校验，没做业务校验 | Service 层做业务规则校验（如用户名是否已存在） |
| **ReDoS 攻击** | 正则有灾难性回溯 | 优化正则、限制输入长度、用原子组/占有量词 |
| **校验错误信息泄露** | 返回了堆栈/内部信息 | 全局异常处理只返回用户友好的消息，详细错误记日志 |

---

## 十、关联笔记

### 后端开发
- [[SpringBoot-核心原理与自动配置]] · [[Java-异常体系与最佳实践]] · [[RESTfulAPI设计原则]]
- [[SpringSecurity-认证授权实战]] · [[Java-数据库性能优化]] · [[Java-应用性能调优实战]]
- [[API安全最佳实践]]

### 计算机基础
- [[常见攻击与防御手段]] · [[密码学基础-对称非对称哈希]] · [[正则表达式与文本处理]]

### 前端
- [[Vue表单解决方案-VeeValidate]] · [[前端安全-XSS-CSRF防护]] · [[TypeScript-类型声明文件编写实战]]

### 导航
- [[MOC-后端开发]] · [[MOC-计算机基础]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[SpringBoot-核心原理与自动配置]] Spring Boot 基础 → 深入本文参数校验 → 学习 [[Java-异常体系与最佳实践]] 异常处理 → 实践 [[RESTfulAPI设计原则]] API 设计 → 研究 [[SpringSecurity-认证授权实战]] 安全认证 → 构建完整的企业级后端开发能力。
