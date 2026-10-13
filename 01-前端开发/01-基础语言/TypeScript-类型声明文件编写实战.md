---
title: TypeScript-类型声明文件编写实战
tags: [TypeScript, .d.ts, 类型定义, 原子笔记]
category: 前端开发
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[TypeScript-高级类型与泛型]]", "[[Vue3-组合式API设计模式", "前端工程化与构建工具]]"]
aliases: [TypeScript-类型声明文件编写实战]
---

# TypeScript-类型声明文件编写实战

> **文档说明**：系统讲解 TypeScript 类型声明文件（.d.ts）的编写方法，包括全局声明、模块声明、命名空间、函数重载、泛型、类声明、模块扩展，以及发布到 DefinitelyTyped 和最佳实践。
>
> **适用人群**：前端开发者、全栈开发者、需要为 JS 库编写类型声明的开发者
>
> **前置知识**：[[TypeScript-高级类型与泛型]]、[[Vue3-组合式API设计模式]]、[[前端工程化与构建工具]]

---

## 一、概述

### 1. 什么是类型声明文件

**类型声明文件（.d.ts）** 是 TypeScript 用于描述 JavaScript 代码类型信息的文件，不包含实现，只包含类型定义。

```css
.d.ts 文件的作用：
- 为纯 JavaScript 库提供类型信息
- 描述全局变量和 API
- 扩展已有模块的类型
- 声明第三方模块
- 让 TypeScript 编译器理解 JS 代码的类型
```

### 2. 类型声明的来源

| 来源 | 说明 | 示例 |
|------|------|------|
| **内置** | TypeScript 自带的 lib | DOM、ES2020、Node.js |
| **库自带** | npm 包中包含 .d.ts | Vue、React、Axios |
| **DefinitelyTyped** | 社区维护的类型库 | @types/lodash、@types/node |
| **自定义** | 项目中自己编写 | src/types/*.d.ts |

### 3. 类型声明 vs 实现文件

```typescript
// 实现文件（.ts）- 包含类型和实现
export function add(a: number, b: number): number {
    return a + b;
}

// 声明文件（.d.ts）- 只包含类型，无实现
export declare function add(a: number, b: number): number;

// 编译后 .ts 会生成 .d.ts（declaration: true）
```

---

## 二、全局声明

### 1. 全局变量和函数

```typescript
// global.d.ts

// 全局变量
declare const APP_VERSION: string;
declare let isDebug: boolean;
declare var globalConfig: {
    apiUrl: string;
    timeout: number;
};

// 全局函数
declare function log(message: string, level?: 'info' | 'warn' | 'error'): void;
declare function formatDate(date: Date | string | number): string;

// 全局类
declare class EventBus {
    constructor();
    on(event: string, handler: (...args: any[]) => void): void;
    emit(event: string, ...args: any[]): void;
    off(event: string, handler: (...args: any[]) => void): void;
}

// 全局枚举
declare enum LogLevel {
    Debug = 0,
    Info = 1,
    Warn = 2,
    Error = 3
}

// 全局命名空间
declare namespace MyApp {
    interface User {
        id: number;
        name: string;
    }
    function getUser(id: number): User;
    const version: string;
}
```

### 2. 全局接口扩展

```typescript
// 扩展 Window 接口
interface Window {
    myApp: {
        version: string;
        init(): void;
    };
    __INITIAL_STATE__: Record<string, any>;
    gtag: (...args: any[]) => void;
}

// 扩展全局对象
interface Global {
    __APP_CONFIG__: {
        env: 'development' | 'production';
    };
}

// Node.js 环境
declare namespace NodeJS {
    interface ProcessEnv {
        NODE_ENV: 'development' | 'production' | 'test';
        API_URL: string;
        PORT?: string;
    }
}
```

### 3. 模块声明（非模块文件）

```typescript
// 声明没有类型的模块
declare module '*.css' {
    const classes: { [key: string]: string };
    export default classes;
}

declare module '*.scss' {
    const content: { [className: string]: string };
    export default content;
}

declare module '*.svg' {
    const content: string;
    export default content;
    export const ReactComponent: React.FC<React.SVGProps<SVGSVGElement>>;
}

declare module '*.png' {
    const value: string;
    export default value;
}

declare module '*.json' {
    const value: any;
    export default value;
}

declare module '*.vue' {
    import type { DefineComponent } from 'vue';
    const component: DefineComponent<{}, {}, any>;
    export default component;
}
```

---

## 三、模块声明

### 1. 导出函数和变量

```typescript
// my-library.d.ts
export function createApp(options: AppOptions): App;
export const version: string;
export const defaultConfig: Config;
```

### 2. 导出接口和类型

```typescript
export interface User {
    id: number;
    name: string;
    email: string;
    role: 'admin' | 'user';
    createdAt: Date;
}

export type UserRole = 'admin' | 'user' | 'guest';

export type Status = 'pending' | 'active' | 'inactive';

export interface Pagination<T> {
    data: T[];
    total: number;
    page: number;
    pageSize: number;
}
```

### 3. 导出类

```typescript
export class HttpClient {
    constructor(baseURL: string, options?: HttpClientOptions);
    
    get<T = any>(url: string, config?: RequestConfig): Promise<HttpResponse<T>>;
    post<T = any>(url: string, data?: any, config?: RequestConfig): Promise<HttpResponse<T>>;
    put<T = any>(url: string, data?: any, config?: RequestConfig): Promise<HttpResponse<T>>;
    delete<T = any>(url: string, config?: RequestConfig): Promise<HttpResponse<T>>;
    
    setHeader(key: string, value: string): void;
    interceptors: {
        request: InterceptorManager<RequestConfig>;
        response: InterceptorManager<HttpResponse>;
    };
}

export interface HttpClientOptions {
    timeout?: number;
    headers?: Record<string, string>;
    withCredentials?: boolean;
}
```

### 4. 函数重载

```typescript
// 函数重载声明
export function parse(input: string): number;
export function parse(input: number): string;
export function parse(input: string | number): number | string;

// 实际实现（在 .ts 文件中）
export function parse(input: string | number): number | string {
    if (typeof input === 'string') return parseInt(input);
    return input.toString();
}
```

### 5. 泛型声明

```typescript
// 泛型函数
export function useRequest<T>(url: string): {
    data: T | null;
    loading: boolean;
    error: Error | null;
    refetch: () => void;
};

// 泛型类
export class EventEmitter<T extends Record<string, any[]>> {
    on<K extends keyof T>(event: K, handler: (...args: T[K]) => void): void;
    emit<K extends keyof T>(event: K, ...args: T[K]): void;
    off<K extends keyof T>(event: K, handler: (...args: T[K]) => void): void;
}

// 泛型接口
export interface Repository<T, ID = number> {
    findById(id: ID): Promise<T | null>;
    findAll(): Promise<T[]>;
    save(entity: T): Promise<T>;
    delete(id: ID): Promise<void>;
}
```

---

## 四、命名空间

### 1. 命名空间声明

```typescript
// validator.d.ts
declare namespace Validator {
    interface Rules {
        required?: boolean;
        minLength?: number;
        maxLength?: number;
        pattern?: RegExp;
        custom?: (value: any) => boolean | string;
    }
    
    interface ValidationResult {
        valid: boolean;
        errors: string[];
    }
    
    function validate(value: any, rules: Rules): ValidationResult;
    function required(value: any): boolean;
    function email(value: string): boolean;
}

// 使用
const result = Validator.validate(email, { required: true, pattern: /@/ });
```

### 2. 命名空间与模块混合

```typescript
// 既可以作为函数调用，又有命名空间属性
declare function myLib(options: myLib.Options): myLib.Instance;
declare namespace myLib {
    interface Options {
        name: string;
        debug?: boolean;
    }
    interface Instance {
        start(): void;
        stop(): void;
    }
    const version: string;
    function create(options: Options): Instance;
}

// 使用
const app = myLib({ name: 'app' });
const app2 = myLib.create({ name: 'app2' });
console.log(myLib.version);
```

---

## 五、模块扩展

### 1. 扩展已有模块

```typescript
// 扩展 Vue 的 ComponentCustomProperties
import { ComponentCustomProperties } from 'vue';

declare module 'vue' {
    interface ComponentCustomProperties {
        $api: ApiClient;
        $auth: AuthService;
        $formatDate: (date: Date) => string;
    }
}

// 扩展 axios
import 'axios';

declare module 'axios' {
    interface AxiosRequestConfig {
        skipAuth?: boolean;
        retryCount?: number;
    }
    interface AxiosResponse {
        traceId?: string;
    }
}

// 扩展 express
import 'express';

declare module 'express' {
    interface Request {
        user?: {
            id: number;
            role: string;
        };
        requestId: string;
    }
}
```

### 2. 全局模块扩展

```typescript
// 扩展 Array
interface Array<T> {
    chunk(size: number): T[][];
    unique(): T[];
    groupBy<K extends keyof T>(key: K): Record<string, T[]>;
}

// 扩展 String
interface String {
    capitalize(): string;
    truncate(maxLength: number): string;
    toCamelCase(): string;
}

// 扩展 Promise
interface Promise<T> {
    timeout(ms: number): Promise<T>;
}
```

---

## 六、为 JS 库编写声明

### 1. 完整示例：工具库

```typescript
// utils.d.ts

// 配置类型
export interface DebounceOptions {
    leading?: boolean;
    trailing?: boolean;
    maxWait?: number;
}

export interface ThrottleOptions {
    leading?: boolean;
    trailing?: boolean;
}

// 防抖函数
export function debounce<T extends (...args: any[]) => any>(
    fn: T,
    wait?: number,
    options?: DebounceOptions
): T & { cancel: () => void; flush: () => void };

// 节流函数
export function throttle<T extends (...args: any[]) => any>(
    fn: T,
    wait?: number,
    options?: ThrottleOptions
): T & { cancel: () => void };

// 深拷贝
export function deepClone<T>(obj: T): T;

// 防抖 hook（Vue/React）
export function useDebounce<T>(value: T, delay: number): { value: T };
```

### 2. 完整示例：HTTP 客户端

```typescript
// http-client.d.ts
export interface RequestConfig {
    url: string;
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
    params?: Record<string, any>;
    data?: any;
    headers?: Record<string, string>;
    timeout?: number;
    responseType?: 'json' | 'text' | 'blob' | 'arraybuffer';
}

export interface HttpResponse<T = any> {
    data: T;
    status: number;
    statusText: string;
    headers: Record<string, string>;
    config: RequestConfig;
}

export interface HttpError extends Error {
    response?: HttpResponse;
    status?: number;
    config: RequestConfig;
}

export interface Interceptor<T> {
    onFulfilled?: (value: T) => T | Promise<T>;
    onRejected?: (error: any) => any;
}

export interface InterceptorManager<T> {
    use(
        onFulfilled?: (value: T) => T | Promise<T>,
        onRejected?: (error: any) => any
    ): number;
    eject(id: number): void;
}

export declare class HttpClient {
    constructor(config?: Partial<RequestConfig>);
    request<T = any>(config: RequestConfig): Promise<HttpResponse<T>>;
    get<T = any>(url: string, config?: Partial<RequestConfig>): Promise<HttpResponse<T>>;
    post<T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<HttpResponse<T>>;
    put<T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<HttpResponse<T>>;
    delete<T = any>(url: string, config?: Partial<RequestConfig>): Promise<HttpResponse<T>>;
    interceptors: {
        request: InterceptorManager<RequestConfig>;
        response: InterceptorManager<HttpResponse>;
    };
}

export declare function createHttpClient(config?: Partial<RequestConfig>): HttpClient;
```

---

## 七、发布类型声明

### 1. 库自带类型

```json
// package.json
{
    "name": "my-library",
    "version": "1.0.0",
    "main": "dist/index.js",
    "types": "dist/index.d.ts",  // 类型声明入口
    "scripts": {
        "build": "tsc"
    },
    "devDependencies": {
        "typescript": "^5.0.0"
    }
}
```

```json
// tsconfig.json
{
    "compilerOptions": {
        "declaration": true,       // 生成 .d.ts
        "declarationMap": true,    // 生成 sourcemap
        "outDir": "dist",
        "rootDir": "src"
    }
}
```

### 2. 发布到 DefinitelyTyped

```text
DefinitelyTyped（@types）提交流程：
1. Fork DefinitelyTyped 仓库
2. 创建 types/your-package/ 目录
3. 编写 index.d.ts
4. 编写 your-package-tests.ts（测试类型）
5. 配置 tslint.json
6. 提交 PR
7. 等待审核合并

要求：
- 类型必须准确，不能有 any（除非必要）
- 必须有测试文件验证类型
- 遵循 DT 风格指南
- 版本号与包版本对应
```

### 3. 测试类型声明

```typescript
// my-library-tests.ts
import { createApp, AppOptions } from 'my-library';

// $ExpectType App
const app = createApp({ name: 'test' });

// $ExpectError
createApp({});  // 缺少必填字段

// $ExpectType string
const version = app.version;

// 验证泛型
const result = useRequest<{ id: number }>('/api/user');
// $ExpectType { id: number } | null
result.data;
```

---

## 八、工具类型

### 1. 内置工具类型

```typescript
// Partial<T>：所有属性可选
type PartialUser = Partial<User>;
// { id?: number; name?: string; ... }

// Required<T>：所有属性必填
type RequiredConfig = Required<Config>;

// Readonly<T>：所有属性只读
type ReadonlyUser = Readonly<User>;

// Pick<T, K>：选取部分属性
type UserBasic = Pick<User, 'id' | 'name'>;

// Omit<T, K>：排除部分属性
type UserWithoutPassword = Omit<User, 'password'>;

// Record<K, T>：键类型为 K，值类型为 T
type UserMap = Record<number, User>;

// ReturnType<T>：函数返回值类型
type AppReturn = ReturnType<typeof createApp>;

// Parameters<T>：函数参数类型
type AppParams = Parameters<typeof createApp>;

// Awaited<T>：解包 Promise
type UserData = Awaited<Promise<User>>;  // User
```

### 2. 自定义工具类型

```typescript
// 可空类型
type Nullable<T> = T | null;

// 可能为 undefined
type Maybe<T> = T | undefined;

// 深度只读
type DeepReadonly<T> = {
    readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};

// 深度可选
type DeepPartial<T> = {
    [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K];
};

// 提取 Promise 内的类型
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;

// 函数参数的第一个参数
type FirstArg<T> = T extends (first: infer F, ...args: any[]) => any ? F : never;
```

---

## 九、最佳实践

### 1. 编写规范

- [ ] **避免 any**：尽量用具体类型，any 是最后手段
- [ ] **使用 unknown**：不确定类型时用 unknown 而非 any
- [ ] **函数重载**：不同参数类型用重载而非联合类型
- [ ] **泛型约束**：用 extends 约束泛型，增加类型安全
- [ ] **导出类型**：公共 API 的类型都要导出
- [ ] **文档注释**：用 JSDoc 注释类型，生成文档
- [ ] **版本对应**：类型声明版本与库版本一致

### 2. 项目配置

```json
// tsconfig.json 推荐配置
{
    "compilerOptions": {
        "strict": true,              // 严格模式
        "noImplicitAny": true,       // 禁止隐式 any
        "strictNullChecks": true,    // 严格空检查
        "declaration": true,         // 生成声明文件
        "declarationMap": true,      // 声明 sourcemap
        "skipLibCheck": false,       // 检查 .d.ts（库开发时设 false）
        "forceConsistentCasingInFileNames": true
    }
}
```

### 3. 调试技巧

```bash
# 检查类型错误
tsc --noEmit

# 查看编译后的声明文件
tsc --emitDeclarationOnly

# 查看类型展开
# 在 VS Code 中悬停查看类型
# 使用 tsc --traceResolution 查看模块解析

# 类型测试工具
# tsd：类型断言测试
# expect-type：类型期望测试
```

---

## 十、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **找不到模块声明** | 缺少 .d.ts / @types 未安装 | 安装 @types/xxx 或编写声明 |
| **类型不匹配** | 声明与实现不一致 | 检查参数、返回值类型 |
| **any 太多** | 类型定义不精确 | 逐步替换 any 为具体类型 |
| **全局变量报错** | 未声明全局变量 | 在 .d.ts 中 declare |
| **模块扩展不生效** | 导入方式不对 / tsconfig 配置 | 确保 import 模块、检查 include |
| **Vue 组件类型丢失** | 缺少 shims-vue.d.ts | 添加 .vue 模块声明 |
| **CSS 模块报错** | 未声明样式模块 | 添加 *.css 模块声明 |
| **第三方库类型过时** | @types 版本旧 | 更新 @types 或提 PR 到 DefinitelyTyped |
| **函数重载不工作** | 实现签名不兼容 | 确保实现签名兼容所有重载 |
| **泛型推断失败** | 类型参数无法推断 | 显式指定泛型参数 |
| **循环引用类型** | 类型互相引用 | 用 type 而非 interface、延迟引用 |
| **声明文件不发布** | package.json 未配置 types | 配置 types/typings 字段 |
| **tsc 报错但运行正常** | 类型声明不准确 | 修正类型声明，不要用 @ts-ignore 掩盖 |
| **命名空间冲突** | 全局命名空间重名 | 使用模块作用域、重命名 |
| **d.ts 中写实现** | 声明文件包含代码 | .d.ts 只能有类型，不能有实现 |

---

## 十一、关联笔记

### TypeScript
- [[TypeScript-高级类型与泛型]] · [[TypeScript-装饰器原理与应用]] · [[TypeScript-类型体操实战]]

### 前端工程
- [[Vue3-组合式API设计模式]] · [[前端工程化与构建工具]] · [[Vite-构建原理与插件开发]]

### 导航
- [[MOC-前端开发]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[TypeScript-高级类型与泛型]] 类型基础 → 深入本文类型声明文件编写 → 实践 [[Vue3-组合式API设计模式]] 类型应用 → 研究 [[前端工程化与构建工具]] 工程化 → 构建完整的 TypeScript 类型体系。
