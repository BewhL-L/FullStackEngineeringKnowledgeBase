# -*- coding: utf-8 -*-
"""第二批扩展：前端 + 数据库 + 中间件"""
import os, sys
ENGINE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "01-前端开发")
sys.path.insert(0, ENGINE_DIR)
from engine import expand

BASE = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# Element Plus
# ============================================================
element_plus = {
    "### 2.1 安装与引入": (
        "在 Vue3 项目中安装并引入 Element Plus 组件库，支持全量引入和按需引入两种方式。",
        "全量引入在 main.ts 中 app.use(ElementPlus) 注册所有组件，打包体积大但简单。按需引入借助 unplugin-vue-components/unplugin-auto-import 自动解析组件和 API，Vite/Webpack 插件在编译时自动引入用到的组件和样式，显著减小打包体积。还支持通过 unplugin-element-plus 按需引入样式和自定义主题（SCSS 变量覆盖）。",
        ["npm install element-plus @element-plus/icons-vue", "按需引入推荐 unplugin-vue-components + ElementPlusResolver", "全局配置：app.use(ElementPlus, { size: 'default', zIndex: 3000 })", "中文语言包：import zhCn from 'element-plus/es/locale/lang/zh-cn'", "面试常考：按需引入原理、Vite 插件自动导入机制、主题定制方案"]
    ),
    "### 2.2 表单组件（Form）": (
        "el-form 提供数据收集、校验和提交功能，配合 el-form-item 和表单控件实现完整表单。",
        "el-form 通过 model 属性绑定数据对象，rules 定义校验规则，el-form-item 的 prop 关联 model 字段和规则。校验基于 async-validator 库，支持 required/pattern/validator 自定义校验。validate 方法返回 Promise，validateField 校验单个字段。resetFields 重置到初始值并清除校验状态。",
        ["model 绑定数据对象，ref 调用 validate/resetFields/clearValidate", "rules 支持 required/pattern/min/max/validator 自定义校验函数", "prop 必须与 model 字段路径对应，嵌套对象用 'user.name'", "动态表单用 prop 绑定数组索引：`domains.${index}.value`", "面试常考：表单校验原理、async-validator、动态表单、自定义校验器"]
    ),
    "### 2.3 表格组件（Table）": (
        "el-table 展示结构化数据，支持排序、筛选、分页、固定列、展开行等企业级表格功能。",
        "el-table 通过 data 绑定数组，el-table-column 用 prop 指定字段、label 定义列标题。列支持 sortable 排序、filters 筛选、fixed 固定左右列、formatter 格式化显示。大数据量可使用虚拟滚动（el-table-v2）。通过 slot 自定义单元格模板，selection 列实现多选。",
        ["el-table-column prop 绑定字段，label 列标题，width 固定列宽", "sortable='custom' 配合后端排序，sortable 前端排序", "fixed='left'/'right' 固定列，用于操作列和关键列", "el-table-v2 虚拟滚动解决万级数据卡顿", "面试常考：表格性能优化、虚拟滚动原理、自定义列模板、后端排序筛选"]
    ),
    "### 2.4 弹窗组件（Dialog）": (
        "el-dialog 模态对话框，用于表单编辑、确认操作、详情展示等浮层交互。",
        "el-dialog 基于 Teleport 将 DOM 渲染到 body 下（避免父级 overflow/transform 影响），v-model 控制显隐，title 定义标题。内部使用遮罩层和居中定位，支持 before-close 拦截关闭（如表单未保存提示）。append-to-body 解决嵌套弹窗层级问题，destroy-on-close 关闭时销毁内容释放资源。",
        ["v-model 控制显隐，title 设置标题，width 控制宽度", "before-close 拦截关闭：(done) => { confirm ? done() : null }", "append-to-body 解决嵌套 Dialog 层级和定位问题", "destroy-on-close 关闭时销毁内部组件状态", "面试常考：Dialog  Teleport 原理、弹窗嵌套层级、before-close 用法"]
    ),
    "### 2.5 反馈组件（Message/Notification/Loading）": (
        "Message 消息提示、Notification 通知、Loading 加载等反馈组件，为用户操作提供即时状态反馈。",
        "ElMessage 用于顶部居中简短提示（成功/错误/警告），ElNotification 用于右上角可持久化通知（可带标题和关闭按钮），ElLoading 用于区域或全屏加载遮罩（v-loading 指令或服务式调用）。这些组件以函数式 API 调用，内部动态创建 Vue 组件实例并挂载到 body，自动管理销毁。",
        ["ElMessage.success/error/warning/info 顶部居中，3s 自动关闭", "ElNotification 右上角通知，支持 title/message/duration/onClick", "v-loading='loading' 指令绑定布尔值，element-loading-text 自定义文字", "服务式调用：const loading = ElLoading.service({ fullscreen: true })", "面试常考：函数式组件实现原理、动态挂载、Loading 指令实现"]
    ),
    "### 3.1 表格+分页+搜索（标准中后台页面）": (
        "组合 el-table + el-pagination + el-form 实现中后台标准列表页：搜索表单、数据表格、分页联动。",
        "标准模式：el-form 搜索栏绑定 queryParams，el-table 展示 tableData，el-pagination 绑定 total/page/pageSize。watch 或搜索按钮触发 getList()，调用 API 传分页和搜索参数，返回数据更新 tableData 和 total。loading 状态绑定 el-table v-loading，搜索时重置 page=1。",
        ["分页参数：pageNum/pageSize/total，搜索时重置到第一页", "el-pagination layout='total, sizes, prev, pager, next, jumper'", "搜索表单和分页共享 queryParams 对象", "切换每页条数时 current-change 和 size-change 都要重新请求", "面试常考：中后台列表页标准结构、分页性能、搜索重置、表格二次封装"]
    ),
    "### 3.2 表单封装与自定义校验": (
        "封装通用表单组件和自定义校验规则，提高表单开发效率和一致性。",
        "封装思路：用配置数组（fields）驱动表单渲染，每个 field 配置 label/prop/type/rules/options，表单组件内部遍历生成 el-form-item。自定义校验通过 validator 函数实现（如确认密码、手机号格式、身份证校验）。封装暴露 validate/resetFields 方法给父组件通过 ref 调用。",
        ["配置驱动：fields 数组定义 label/prop/component/rules/options", "validator 校验函数 (rule, value, callback)，callback(new Error('msg'))", "密码确认校验：validator 中比较 value 与 form.password", "封装组件用 defineExpose 暴露 validate/resetFields", "面试常考：表单封装方案、动态校验规则、跨字段校验、配置驱动表单"]
    ),
    "### 3.3 上传组件（Upload）": (
        "el-upload 支持文件选择、拖拽上传、进度显示、图片预览和文件类型限制。",
        "el-upload 通过 action 指定上传地址或 http-request 自定义上传（覆盖默认行为，用 axios 上传）。before-upload 钩子做文件类型和大小校验，on-progress 显示进度，on-success/on-error 处理结果。图片上传用 list-type='picture-card' 配合预览，文件数量限制用 limit。",
        ["http-request 覆盖默认上传，用自己封装的 axios 请求", "before-upload 返回 false 或 Promise.reject 阻止上传", "图片格式校验：file.type === 'image/jpeg'，大小 file.size / 1024 / 1024 < 2", "on-remove 同步删除服务端文件，file-list 受控管理", "面试常考：大文件分片上传、断点续传、图片压缩上传、上传进度"]
    ),
    "### 3.5 日期选择器（DatePicker）": (
        "el-date-picker 提供日期、日期范围、时间等选择功能，支持快捷选项和禁用日期。",
        "DatePicker 基于 dayjs 处理日期，v-model 绑定 Date 对象或字符串（value-format 控制绑定格式）。daterange 类型选择日期范围绑定数组。disabled-date 函数禁用特定日期（如只能选今天之后），shortcuts 配置快捷选项（今天/最近一周/最近三个月）。",
        ["value-format='YYYY-MM-DD' 让 v-model 绑定字符串而非 Date 对象", "daterange 绑定 [startDate, endDate] 数组", "disabled-date: (date) => date.getTime() < Date.now() 禁用过去日期", "shortcuts 配置快捷选项，点击直接设置日期范围", "面试常考：日期格式化、禁用日期逻辑、范围选择器、时区处理"]
    ),
}

# ============================================================
# Pinia
# ============================================================
pinia = {
    "### 2.1 安装与创建 Store": (
        "安装 Pinia 并通过 defineStore 定义状态仓库，是 Vue3 官方推荐的状态管理方案。",
        "createPinia() 创建 pinia 实例，app.use(pinia) 注册。defineStore('id', options) 定义 Store：选项式写法传 state/getters/actions 对象，组合式写法传 setup 函数（ref 是 state，computed 是 getters，function 是 actions）。useXxxStore() 在组件中获取 store 实例，store 是 reactive 代理，可直接解构但丢失响应式（需 storeToRefs）。",
        ["app.use(createPinia()) 注册，defineStore('唯一id', options/setup)", "选项式：state/getters/actions；组合式：ref/computed/function", "useStore() 必须在 setup 或组件内调用，Pinia 实例已注入后", "storeToRefs(store) 解构保持响应式，方法直接解构", "面试常考：Pinia vs Vuex、组合式 Store、storeToRefs 原理"]
    ),
    "### 2.2 State（状态）": (
        "State 是 Store 的核心数据，用 ref（组合式）或箭头函数返回对象（选项式）定义，支持直接修改和 $patch 批量更新。",
        "Pinia 的 state 本质是 reactive 包裹的对象，可直接通过 store.xxx = value 修改（无需 mutations）。$patch 支持对象或函数两种方式批量修改（函数方式适合对数组操作如 push/splice）。$reset() 重置到初始状态（选项式支持，组合式需自己实现）。$subscribe 订阅 state 变化。",
        ["直接修改：store.count++，无需 mutation", "$patch({ count: 2, name: 'x' }) 批量修改，只触发一次订阅", "$patch((state) => { state.list.push(item) }) 函数式适合数组操作", "$reset() 重置 state（选项式），组合式需自定义 $reset", "面试常考：Pinia 直接修改 state 原理、$patch 批量更新、$reset 实现"]
    ),
    "### 2.3 Getters（计算属性）": (
        "Getters 等同于 Store 的 computed，用于派生状态，具有缓存特性。",
        "选项式中 getters 是函数，接收 state 为参数，this 指向 store 实例可访问其他 getters。组合式中用 computed() 定义。Getters 内部基于 Vue 的 computed 实现，依赖不变时缓存结果。可返回函数实现传参 getter（此时不缓存）。",
        ["getters: { doubleCount: (state) => state.count * 2 }", "this 访问其他 getter：this.doubleCount", "组合式：const doubleCount = computed(() => count.value * 2)", "传参 getter 返回函数：(id) => state.list.find(i => i.id === id)，不缓存", "面试常考：getter 缓存原理、传参 getter、与 computed 关系"]
    ),
    "### 2.4 Actions（业务方法）": (
        "Actions 封装业务逻辑，支持同步和异步操作，可通过 this 直接访问 state 和 getters。",
        "选项式 actions 中 this 指向 store 实例，可直接读写 state、调用其他 action。组合式中定义普通函数，闭包访问 ref/computed。Actions 天然支持 async/await，调用方可以 await action。Pinia 没有 mutations，所有修改都在 actions 中或直接修改。",
        ["actions 中 this.count++ 直接修改 state，无需 commit", "async action 内可 await API 调用，组件中 await store.fetchData()", "组合式：async function fetchData() { const data = await api(); list.value = data }", "一个 action 可调用其他 action：this.otherAction()", "面试常考：Pinia actions vs Vuex mutations、异步 action、this 指向"]
    ),
    "### 2.6 持久化（pinia-plugin-persistedstate）": (
        "通过插件将 Pinia state 自动持久化到 localStorage/sessionStorage，刷新页面不丢失。",
        "pinia-plugin-persistedstate 在 store 初始化时从 storage 读取数据合并到 state，通过 $subscribe 监听 state 变化自动写入 storage。支持配置 key（存储键名）、storage（localStorage/sessionStorage）、paths（指定持久化字段）。序列化默认 JSON.stringify/parse，可自定义 serializer。",
        ["pinia.use(piniaPluginPersistedstate) 注册插件", "persist: true 开启，或 persist: { key: 'my-store', paths: ['token'] }", "paths 指定持久化部分字段，避免存储大对象", "storage: sessionStorage 关闭浏览器即清除", "面试常考：持久化插件原理、$subscribe、SSR 持久化、部分持久化"]
    ),
    "### 2.7 插件与高级用法": (
        "Pinia 插件通过 pinia.use() 扩展 Store 能力，可添加全局 state、getters、actions 或包装现有功能。",
        "Pinia 插件是一个函数，接收 context（包含 store/options/pinia/app），可在函数内给 store 添加属性（store.xxx = ...）、用 store.$subscribe 监听变化、用 store.$onAction 拦截 action。插件返回的对象会合并到 store。Vue DevTools 可调试 Pinia，支持时间旅行。",
        ["插件函数 ({ store }) => { store.globalProp = ... } 返回对象自动合并", "$onAction 拦截 action：after/onError 回调做日志和错误处理", "可添加全局选项（如路由守卫中统一重置 store）", "SSR 中需为每个请求创建新 pinia 实例避免状态污染", "面试常考：Pinia 插件开发、$onAction、SSR 状态隔离、DevTools"]
    ),
    "### 3.1 用户认证 Store": (
        "管理用户登录态、token、用户信息的 Store，配合路由守卫实现认证流程。",
        "authStore 存储 token 和 userInfo，login action 调用登录 API 获取 token 并持久化，getUserInfo 获取用户信息，logout 清除状态并跳转登录。token 持久化到 localStorage，路由守卫检查 token 是否存在决定是否放行。401 拦截器触发 logout。",
        ["token 持久化到 localStorage，刷新后自动从 storage 恢复", "login action: await api.login → token 存储 → 获取用户信息", "路由守卫 beforeEach 检查 isAuthenticated getter", "axios 拦截器自动添加 Authorization Header，401 触发 logout", "面试常考：登录态管理、token 刷新、路由守卫、权限控制"]
    ),
    "### 3.2 购物车 Store": (
        "管理购物车商品列表、数量计算和选中状态，是电商场景的经典状态管理案例。",
        "cartStore 用数组存储购物项（id/name/price/quantity/selected），getters 计算总价（选中商品 price*quantity 求和）、总数、选中数量。actions 实现 addToCart（已存在则 quantity+1）、removeItem、updateQuantity、toggleSelect、clearCart。",
        ["addToCart：findIndex 判断是否已存在，存在则 quantity++", "totalPrice getter: selectedItems.reduce((sum, i) => sum + i.price * i.quantity, 0)", "全选/反选：setAllSelected(boolean) 设置每项 selected", "持久化购物车数据，刷新不丢失", "面试常考：购物车状态设计、计算属性缓存、数量边界处理"]
    ),
    "### 3.3 应用配置 Store（主题/语言）": (
        "管理全局应用配置如主题色、暗黑模式、语言切换等 UI 偏好设置。",
        "appStore 存储 theme（light/dark）、primaryColor、locale 等配置，切换主题时通过 document.documentElement.classList 添加 dark 类或设置 CSS 变量。语言切换时修改 i18n 的 locale。配置变更持久化到 localStorage，初始化时读取并应用。",
        ["暗黑模式：document.documentElement.classList.toggle('dark')", "CSS 变量：document.documentElement.style.setProperty('--primary', color)", "i18n 语言切换：i18n.global.locale.value = locale", "watch 配置变化自动持久化和应用副作用", "面试常考：主题切换实现、CSS 变量、i18n 集成、配置持久化"]
    ),
    "### 3.4 跨 Store 调用": (
        "在一个 Store 的 action 中获取并使用另一个 Store，实现 Store 间的组合与复用。",
        "在 action 内部直接调用 useOtherStore() 获取其他 store 实例（Pinia 注册后可在任意位置调用）。组合式 Store 中可直接 import 其他 store 的 use 函数。跨 Store 调用避免循环依赖：若 A 调 B、B 调 A，在 action 内部延迟调用而非顶层调用。",
        ["action 内调用 useOtherStore() 获取实例，读取 state/getters 或调用 action", "避免在 store 顶层（setup 函数体）调用其他 store，可能未初始化", "循环依赖时在 action 内部延迟获取其他 store", "也可用 pinia 实例的 storeToRefs 或直接 import", "面试常考：跨 Store 调用方式、循环依赖处理、Store 组合模式"]
    ),
    "### 3.6 与 Vue Router 配合（路由守卫）": (
        "在路由守卫中访问 Pinia Store 做权限控制，根据用户角色动态添加路由。",
        "全局前置守卫 beforeEach 中获取 authStore，检查 token 和用户权限。首次进入时若有 token 但无用户信息，先调用 getUserInfo 获取角色，再根据角色动态 addRoute 添加权限路由。白名单（登录页/404）直接放行。动态路由添加后需 next({ ...to, replace: true }) 重新导航。",
        ["守卫中 useAuthStore() 必须在 app.use(pinia) 之后调用", "动态路由：router.addRoute() 根据角色过滤路由表后添加", "addRoute 后 next({ ...to, replace: true }) 确保新路由生效", "白名单路径数组，登录页直接放行", "面试常考：动态路由、路由守卫执行时机、按钮权限、刷新后路由丢失"]
    ),
}

# ============================================================
# Vue3 知识点
# ============================================================
vue3_kp = {
    "### 3.1 响应式 API 使用": (
        "ref/reactive/computed/watch/watchEffect 等响应式 API 是 Vue3 组合式 API 的核心，实现数据驱动视图。",
        "ref 用 Object.defineProperty 式的 getter/setter 包裹 .value（基本类型），reactive 用 Proxy 代理整个对象（引用类型）。track 在 getter 中收集依赖（当前 effect），trigger 在 setter 中通知更新。computed 基于 effect 实现带缓存的派生值。watch 显式指定数据源并能拿到新旧值，watchEffect 自动收集依赖立即执行。",
        ["ref 基本类型用 .value，模板中自动解包；reactive 代理对象不需要 .value", "reactive 不能直接替换整个对象（丢失响应式），用 Object.assign 或 ref", "computed 有缓存，依赖不变不重新计算；可写 computed 提供 get/set", "watch 显式指定源，watchEffect 自动收集；watch 默认懒执行，watchEffect 立即执行", "面试常考：ref vs reactive、Proxy vs defineProperty、track/trigger 原理、watch vs watchEffect"]
    ),
    "### 3.2 组件定义与 Props/Emit": (
        "Vue3 用 defineProps/defineEmits 编译器宏声明组件输入输出，配合 setup 语法糖简化组件定义。",
        "<script setup> 中 defineProps 声明 props（编译时宏，无需导入），支持运行时声明（类型数组/对象）和 TypeScript 类型声明。defineEmits 声明事件。props 是只读的 shallowReactive，修改会警告。emit 触发自定义事件，父组件用 @event 监听。defineExpose 暴露子组件方法/属性给父组件 ref。",
        ["defineProps<{ msg: string; list?: Item[] }>() TS 类型声明", "withDefaults(defineProps<{msg?:string}>(), { msg: 'hi' }) 设置默认值", "defineEmits<{ (e: 'change', id: number): void }>() 类型化事件", "props 只读，子组件不直接修改，通过 emit 通知父组件修改", "面试常考：defineProps 原理、props 单向数据流、defineExpose、v-model 实现"]
    ),
    "### 3.3 路由（Vue Router 4）": (
        "Vue Router 4 为 Vue3 提供客户端路由，支持动态路由、导航守卫、懒加载等 SPA 路由能力。",
        "createRouter 创建路由实例（history: createWebHistory/createWebHashHistory），routes 定义路由表（path/component/children/meta）。<router-view> 渲染匹配组件，<router-link> 导航。导航守卫分全局（beforeEach）、路由独享（beforeEnter）、组件内（onBeforeRouteLeave）。动态路由 addRoute/removeRoute 支持权限路由。",
        ["createWebHistory（History 模式，需服务端配置 fallback）vs createWebHashHistory（Hash 模式）", "路由懒加载：component: () => import('./Foo.vue') 实现代码分割", "全局守卫 beforeEach(to, from, next)，next 在 Vue Router 4 可省略直接返回 false/路由地址", "动态路由 addRoute 用于权限控制，meta 存自定义信息（title/requiresAuth）", "面试常考：History vs Hash、导航守卫解析流程、动态路由、路由传参"]
    ),
    "### 3.4 状态管理（Pinia）": (
        "Pinia 是 Vue3 官方状态管理库，用组合式 API 风格定义 Store，替代 Vuex。",
        "Pinia 没有 mutations，直接修改 state；支持选项式和组合式两种 Store 写法；完整的 TypeScript 类型推断；模块化通过多个 Store 实现（无需嵌套模块）。底层利用 Vue3 的 reactive/computed 实现响应式，通过 provide/inject 注入 pinia 实例。devtools 支持时间旅行调试。",
        ["defineStore('id', () => { const count = ref(0); const double = computed(...); function inc(){} return {count, double, inc} })", "直接修改 store.count++，无需 commit/dispatch", "storeToRefs 解构保持响应式", "Pinia 天然模块化，每个 store 独立，可跨 store 调用", "面试常考：Pinia vs Vuex、组合式 Store、持久化插件、DevTools"]
    ),
    "### 3.5 组合函数（Composables）": (
        "组合函数是以 use 开头的函数，封装有状态逻辑，利用 Vue 组合式 API 实现逻辑复用，替代 Mixin。",
        "组合函数内部使用 ref/reactive/computed/watch/watchEffect/生命周期钩子管理状态和副作用，返回需要暴露的响应式数据和方法。命名约定 useXxx（如 useMouse、useFetch、useDebounce）。与 Mixin 相比，组合函数显式导入、数据来源清晰、无命名冲突、可传递参数。",
        ["use 开头命名，内部使用 ref/computed/watch 等响应式 API", "return { x, y, ... } 暴露数据和方法，组件中 const { x } = useMouse()", "可接收参数：useFetch(url, options)，参数变化时 watch 重新请求", "生命周期钩子在组合函数中直接调用（onMounted 等）", "面试常考：组合函数 vs Mixin、逻辑复用模式、useEvent/useFetch 封装"]
    ),
    "### 3.7 TypeScript 支持": (
        "Vue3 原生支持 TypeScript，<script setup lang='ts'> 提供组件 props/emits/ref 等完整类型推导。",
        "defineProps/defineEmits 支持泛型类型参数，编译器根据类型自动生成运行时校验。ref<Type>()、reactive<Type>()、computed<Type>() 显式标注类型。模板中也支持类型检查（Volar）。组件类型通过 defineComponent 或 <script setup> 自动推导，父组件 ref 子组件用 InstanceType<typeof Child>。",
        ["<script setup lang='ts'> 启用 TS，defineProps<{...}>() 类型声明", "ref<number>(0) 显式类型，reactive<User>({...})", "defineEmits<{ (e:'submit', data:FormData):void }>()", "父组件获取子组件类型：const child = ref<InstanceType<typeof Child>>()", "面试常考：Vue3 + TS 类型推导、defineProps 泛型、组件类型导出"]
    ),
    "### 3.8 构建工具（Vite）": (
        "Vite 利用浏览器原生 ESM 和 esbuild 实现极速冷启动，Rollup 生产打包，是 Vue3 官方构建工具。",
        "开发模式：Vite 启动一个 Connect 服务器，浏览器请求模块时 Vite 按需编译返回 ESM（不打包），esbuild 预构建依赖（将 CJS 转 ESM）。冷启动极快因为不需要全量打包。HMR 基于 ESM 精准更新，修改模块只需让浏览器重新请求该模块。生产构建用 Rollup 打包优化（tree-shaking、代码分割、压缩）。",
        ["开发时利用浏览器原生 ESM，按需编译，冷启动 O(1) 不随项目增大变慢", "esbuild 预构建 node_modules（Go 编写，比 JS 快 10-100 倍）", "HMR：修改模块后精准更新，保留应用状态", "生产构建 Rollup：tree-shaking、code splitting、asset 优化", "面试常考：Vite 为什么快、ESM 预构建、HMR 原理、Vite vs Webpack"]
    ),
}

# ============================================================
# MySQL
# ============================================================
mysql_kp = {
    "### 3.7 性能调优参数": (
        "通过调整 MySQL 配置参数优化内存使用、连接管理、日志刷盘等，提升数据库整体性能。",
        "关键参数：innodb_buffer_pool_size（缓冲池大小，建议物理内存 50%-70%，缓存数据页和索引页）、innodb_log_file_size（redo log 大小，影响崩溃恢复时间和写入性能）、max_connections（最大连接数，过大会消耗内存）、innodb_flush_log_at_trx_commit（redo 刷盘策略，1 最安全，0/2 性能好但可能丢数据）、sync_binlog（binlog 刷盘策略）。调优需结合硬件和 workload，用 SHOW STATUS/VARIABLES 监控。",
        ["innodb_buffer_pool_size 设为物理内存 50%-70%（专用数据库服务器）", "innodb_flush_log_at_trx_commit=1 + sync_binlog=1 是双1配置，最安全", "max_connections 根据应用连接池配置，不宜过大（每连接占内存）", "innodb_log_file_size 通常 256M-1G，大写入场景适当增大", "面试常考：缓冲池配置、双1参数、连接数调优、SHOW PROFILE/EXPLAIN 分析"]
    ),
}

# ============================================================
# Redis
# ============================================================
redis_kp = {
    "### 3.1 缓存使用模式": (
        "Cache Aside、Read Through、Write Through、Write Behind 等缓存模式决定了缓存与数据库的交互策略。",
        "Cache Aside（最常用）：读时先查缓存，未命中查 DB 并回填；写时先更新 DB 再删除缓存（而非更新缓存，避免并发脏数据）。Read Through/Write Through 由缓存层统一代理读写。Write Behind（写回）先写缓存异步批量写 DB，性能高但可能丢数据。延迟双删：更新 DB 前后各删一次缓存（中间 sleep），解决并发读写导致的脏缓存。",
        ["Cache Aside：读缓存→未命中读 DB→回填；写 DB→删缓存", "删除缓存而非更新缓存，避免并发写导致旧值覆盖新值", "延迟双删：删缓存→更新 DB→延迟→再删缓存，解决读写并发脏数据", "Write Behind 异步批量落盘性能好但有数据丢失风险", "面试常考：缓存模式对比、为什么删缓存不更新、延迟双删、缓存一致性"]
    ),
    "### 3.4 分布式限流": (
        "利用 Redis 实现分布式限流，控制请求速率，保护后端服务不被突发流量击垮。",
        "常用算法：固定窗口（INCR + EXPIRE，简单但有临界突刺）、滑动窗口（ZSET 按时间戳排序，ZREMRANGEBYSCORE 清理窗口外记录）、令牌桶（Lua 脚本原子操作：往桶放令牌+取令牌，允许突发流量）、漏桶（队列匀速流出，平滑输出）。Redis + Lua 保证原子性，适合分布式场景。Redisson 提供 RRateLimiter 开箱即用。",
        ["固定窗口：INCR key，超过阈值拒绝，EXPIRE 重置窗口", "滑动窗口：ZADD 记录请求时间戳，ZREMRANGEBYSCORE 删旧记录，ZCARD 计数", "令牌桶允许突发（桶满可快速取），漏桶平滑输出（匀速）", "Lua 脚本保证判断+计数原子性，避免竞态条件", "面试常考：限流算法对比、滑动窗口 ZSET 实现、令牌桶 Lua、Redisson RRateLimiter"]
    ),
}

# ============================================================
# 分布式事务
# ============================================================
dist_tx = {
    "### 3.1 Seata AT 模式": (
        "Seata AT（Auto Transaction）是无侵入的分布式事务方案，通过二阶段提交 + undo_log 自动回滚。",
        "一阶段：拦截业务 SQL，解析 SQL 语义，查询前镜像（before image），执行业务 SQL，查询后镜像（after image），存入 undo_log，本地事务提交（行锁由 Seata 管理）。二阶段提交：异步删除 undo_log。二阶段回滚：根据 undo_log 中的 before image 反向补偿恢复数据（校验 after image 与当前数据一致才回滚，防止脏写）。",
        ["一阶段本地事务就提交，不锁定资源太久（持有全局行锁）", "undo_log 表记录前后镜像，回滚时自动反向补偿", "before image 查询修改前数据，after image 查询修改后数据", "回滚前校验 after image 与当前数据一致，不一致需人工介入", "面试常考：AT 模式原理、undo_log、全局锁、AT vs TCC、脏写防护"]
    ),
    "### 3.2 Seata TCC 模式": (
        "TCC（Try-Confirm-Cancel）是业务层面的二阶段提交，需要自己实现三个方法，性能高但侵入性强。",
        "Try：预留资源（冻结金额、锁定库存）；Confirm：确认执行业务（实际扣款、扣减库存）；Cancel：取消释放预留资源（解冻金额、释放库存）。TCC 不依赖数据库本地事务，性能好，但需为每个操作实现三个方法，开发成本高。需处理空回滚（Try 未执行就收到 Cancel）、幂等（Confirm/Cancel 可能重复调用）、悬挂（Cancel 先于 Try 执行）。",
        ["Try 预留资源，Confirm 确认提交，Cancel 取消回滚", "需处理空回滚：记录事务状态，Cancel 时 Try 未执行则直接成功", "幂等：Confirm/Cancel 可能重复调用，用事务状态表防重", "悬挂：Cancel 比 Try 先到，Try 需检查是否已 Cancel", "面试常考：TCC 三阶段、空回滚/幂等/悬挂、TCC vs AT、Seata TCC 实现"]
    ),
    "### 3.3 本地消息表实现": (
        "本地消息表方案将分布式事务拆为本地事务 + 消息异步投递，保证最终一致性。",
        "业务操作和消息记录在同一个本地事务中写入业务表和消息表（状态待发送）。后台任务定时扫描消息表，将待发送消息投递到 MQ，投递成功后标记已发送。消费者消费消息完成下游操作，保证幂等。消息表和业务表在同一数据库，本地事务保证原子性，MQ 保证消息可达，最终一致。",
        ["业务数据和消息数据在同一本地事务写入", "定时任务扫描 status=待发送 的消息投递 MQ", "消费者必须幂等（消息可能重复投递）", "消息表需定期清理已完成消息，注意消息重试次数", "面试常考：本地消息表原理、与事务消息对比、最终一致性、消息幂等"]
    ),
    "### 3.4 RocketMQ 事务消息": (
        "RocketMQ 事务消息通过半消息 + 本地事务 + 回查机制，保证消息发送与本地事务的原子性。",
        "流程：① 发送半消息（half message，消费者不可见）② Broker 存储半消息返回确认 ③ 生产者执行本地事务 ④ 根据本地事务结果提交（commit，消息对消费者可见）或回滚（rollback，删除消息）⑤ 若未收到 commit/rollback，Broker 回查生产者本地事务状态。这样保证本地事务成功则消息一定投递，失败则消息不投递。",
        ["半消息对消费者不可见，直到 commit", "本地事务执行后发送 commit/rollback 给 Broker", "Broker 长时间未收到状态会回查生产者（checkLocalTransaction）", "消费者仍需幂等，事务消息只保证生产端一致性", "面试常考：事务消息流程、半消息、回查机制、与本地消息表对比"]
    ),
    "### 3.5 分布式锁": (
        "分布式锁保证分布式环境下同一时间只有一个实例执行临界区代码，常见实现有 Redis/ZooKeeper/数据库。",
        "Redis 分布式锁：SET key value NX PX timeout（原子加锁），value 用唯一 ID（UUID），释放锁用 Lua 脚本校验 value 后删除（防误删）。Redisson 提供可重入锁、看门狗续期、红锁算法。ZooKeeper 临时顺序节点：最小节点获得锁，监听前一节点删除事件，无锁超时问题但性能低于 Redis。",
        ["SET lock_key uuid NX PX 30000 原子加锁，Lua 脚本比较 value 后删除", "Redisson 看门狗：锁过期前自动续期（默认 30s，每 10s 续期）", "Redis 主从切换可能丢锁，RedLock 向多个独立 Redis 实例加锁", "ZK 临时顺序节点天然防死锁（会话断开节点删除），但性能较低", "面试常考：Redis 锁原子性、看门狗续期、RedLock 争议、Redis vs ZK 锁"]
    ),
    "### 3.6 接口幂等性": (
        "幂等性保证同一请求执行一次和多次的效果相同，防止重复提交、消息重投导致的数据异常。",
        "常用方案：① 数据库唯一索引（插入重复数据报错）② 乐观锁版本号（update ... where version=x）③ 状态机（只允许特定状态流转）④ 分布式锁/Token 机制（提交前获取 token，提交时校验删除）⑤ 全局请求 ID + 去重表。查询天然幂等，删除通常幂等，新增和修改需额外保证。",
        ["唯一索引：INSERT 重复键冲突，防重复创建", "乐观锁：UPDATE ... SET version=version+1 WHERE version=旧值", "Token 机制：进入页面获取 token，提交时校验并删除（Redis 原子操作）", "状态机：订单 待支付→已支付，已支付不能再支付", "面试常考：幂等方案、Token 防重提交、乐观锁、消息幂等消费"]
    ),
    "### 3.7 数据一致性对账": (
        "通过定时对账检测分布式系统间的数据不一致，是最终一致性的兜底保障手段。",
        "对账系统定时（如每日凌晨）拉取上下游系统数据进行比对：全量对账（比对所有记录，适合数据量小）或增量对账（按时间窗口比对）。发现差异后生成对账差异记录，触发自动补偿（重试/修复）或人工处理。对账需考虑时序差异（数据在途），设置缓冲时间窗口。",
        ["定时任务按时间窗口拉取双方数据比对", "全量对账适合数据量小，增量对账按 update_time 窗口", "差异类型：多账（对方有我方无）、少账、金额不一致", "自动补偿 + 人工处理兜底，对账结果需记录和告警", "面试常考：对账方案、最终一致性兜底、补偿机制、在途数据处理"]
    ),
}

# ============================================================
# 消息队列
# ============================================================
mq = {
    "### 3.1 Kafka 生产者": (
        "Kafka Producer 将消息发送到指定 Topic 的分区，支持异步发送、批量压缩和确认机制。",
        "Producer 发送流程：序列化 key/value → 分区器选择分区（有 key 按 key hash，无 key 轮询/粘性）→ 发送到 RecordAccumulator 累积批量 → Sender 线程按 batch 发送到 Broker。acks 参数控制持久性：0（不等确认）、1（Leader 确认）、all（ISR 全部确认）。支持重试、压缩（snappy/lz4/zstd）、幂等生产者（enable.idempotence）。",
        ["acks=all 配合 min.insync.replicas≥2 保证不丢数据", "RecordAccumulator 批量累积，batch.size 和 linger.ms 控制批量大小", "幂等生产者：PID + Sequence Number 防止重试导致重复", "压缩在 Producer 端完成，Broker 保存压缩数据，Consumer 解压", "面试常考：Kafka 发送流程、acks 机制、批量发送、幂等生产者、分区策略"]
    ),
    "### 3.2 Kafka 消费者": (
        "Kafka Consumer 以消费组方式订阅 Topic，通过 offset 管理消费进度，支持手动提交和再均衡。",
        "Consumer Group 中每个分区只分配给一个消费者（组内），不同组互不影响。消费者轮询 poll() 获取消息，处理后提交 offset（自动提交 enable.auto.commit 或手动 commitSync/commitAsync）。Rebalance 发生在消费者增减或分区变化时，期间消费暂停。消费者数超过分区数时多余消费者空闲。",
        ["消费组：同组内分区独占，不同组各自消费全量", "auto.offset.reset=earliest/latest 控制无 offset 时起点", "手动提交 commitSync（阻塞重试）/commitAsync（不重试）", "Rebalance 期间不可消费，可使用 ConsumerRebalanceListener 提交 offset", "面试常考：消费组模型、offset 管理、Rebalance、消费者数与分区数关系"]
    ),
    "### 3.3 RabbitMQ 生产者": (
        "RabbitMQ Producer 将消息发送到 Exchange，由 Exchange 根据路由规则投递到 Queue。",
        "Producer 发送消息到 Exchange（不直接到 Queue），Exchange 类型决定路由：direct（精确匹配 routing key）、fanout（广播到所有绑定队列）、topic（通配符匹配）、headers（头属性匹配）。消息可设持久化（deliveryMode=2）、TTL、优先级。Publisher Confirm 确认消息到达 Broker，Returns 处理无法路由的消息。",
        ["Exchange 类型：direct 精确、fanout 广播、topic 通配符、headers 属性", "消息持久化：durable queue + deliveryMode=2 + 持久化 Exchange", "Publisher Confirm 异步确认消息到达 Broker", "mandatory + ReturnListener 处理无法路由的消息", "面试常考：Exchange 类型、消息持久化、Publisher Confirm、路由机制"]
    ),
    "### 3.5 RocketMQ 生产者": (
        "RocketMQ Producer 发送消息到 NameServer 路由的 Broker，支持同步/异步/单向发送和事务消息。",
        "Producer 从 NameServer 获取 Topic 路由信息（队列列表），选择 MessageQueue 发送（轮询或选择算法）。同步发送等待 Broker 确认（可靠），异步发送回调处理，单向发送不等确认（日志类）。消息包含 topic/tag/key/body，tag 用于消费端过滤。重试机制默认 2 次，失败进入死信队列。",
        ["同步发送 send() 等待确认，适合重要通知；异步 send(callback) 适合吞吐", "NameServer 无状态，Producer 定期拉取路由，Broker 注册到所有 NameServer", "tag 用于服务端过滤，SQL92 表达式支持更复杂过滤", "发送失败重试 2 次，超时可配置", "面试常考：RocketMQ 架构、NameServer vs ZooKeeper、消息过滤、发送模式"]
    ),
    "### 3.6 RocketMQ 消费者": (
        "RocketMQ Consumer 以推/拉模式消费消息，支持集群消费和广播消费，offset 存储在 Broker。",
        "DefaultMQPushConsumer 实际是长轮询拉取（Broker  hold 请求直到有消息或超时），封装成推模式。MessageListenerConcurrently 并发消费（不保证顺序），MessageListenerOrderly 顺序消费（对同一 MessageQueue 加锁）。消费成功返回 CONSUME_SUCCESS，失败返回 RECONSUME_LATER 触发重试（默认 16 次后进死信队列）。集群消费同组分摊，广播消费每个消费者都消费全量。",
        ["Push 模式底层是长轮询 Pull，实时性好且降低 Broker 压力", "集群消费（CLUSTERING）同组分摊，广播（BROADCASTING）每人全量", "顺序消费：MessageListenerOrderly 对 Queue 加锁，保证同一队列顺序", "消费失败重试 16 次，进度从 Broker 查，超过进死信队列 %DLQ%consumerGroup", "面试常考：推模式长轮询、顺序消费、重试与死信队列、集群 vs 广播"]
    ),
    "### 3.7 事务消息": (
        "RocketMQ 事务消息通过半消息+回查保证本地事务与消息发送的原子性，是最终一致性方案。",
        "两阶段提交：第一阶段发送半消息（Prepared），Broker 存储但不对消费者可见；Producer 执行本地事务；第二阶段根据本地事务结果发送 Commit（消息可见）或 Rollback（删除）。若 Producer 未发送第二阶段状态，Broker 定期回查 Producer 的本地事务状态（checkLocalTransaction）。",
        ["半消息（Half Message）消费者不可见，直到 Commit", "Broker 回查：长时间未收到状态时回调 Producer 查询事务结果", "事务消息保证生产端一致性，消费端仍需幂等", "适用于下单扣库存等跨服务最终一致性场景", "面试常考：事务消息流程、半消息与回查、与本地消息表对比、适用场景"]
    ),
}


def run():
    tasks = [
        (os.path.join(BASE, "01-前端开发", "Element Plus 知识点系统梳理_优化版.md"), element_plus),
        (os.path.join(BASE, "01-前端开发", "Pinia 知识点系统梳理_优化版.md"), pinia),
        (os.path.join(BASE, "01-前端开发", "Vue3 知识点系统梳理_优化版.md"), vue3_kp),
        (os.path.join(BASE, "03-数据库与缓存", "MySQL 知识点系统梳理_优化版.md"), mysql_kp),
        (os.path.join(BASE, "03-数据库与缓存", "Redis 知识点系统梳理_优化版.md"), redis_kp),
        (os.path.join(BASE, "04-分布式与中间件", "分布式事务 知识点系统梳理_优化版.md"), dist_tx),
        (os.path.join(BASE, "04-分布式与中间件", "消息队列深度 知识点系统梳理_优化版.md"), mq),
    ]
    for path, cmap in tasks:
        lines, added = expand(path, cmap, False, False, "")
        print(f"  {os.path.basename(path)}: {lines} lines, {added} blocks added")


if __name__ == "__main__":
    run()
