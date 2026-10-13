# 工业 AI 缺陷检测系统

基于 Flask + OpenCV + SQLite 的工业缺陷检测全栈系统，核心算法为连通域分析（岛屿问题的工程化落地）。

说明：当前模型为**模拟分割模式**（用阈值法模拟缺陷检出），用于全链路功能验证。后续接入真实分割模型时，只需替换 `models/segment_model.py` 中的推理逻辑即可。

## 项目结构

```
工业 AI 缺陷检测系统/
├── requirements.txt        # 依赖清单
├── config.py               # 全局配置
├── app.py                  # 主程序（Flask后端）
├── models/
│   └── segment_model.py    # 分割模型封装
├── db/
│   └── database.py         # 数据库操作
├── deploy/
│   ├── gunicorn.conf.py    # 生产服务配置
│   ├── nginx.conf          # 反向代理配置
│   └── Dockerfile         # 容器化配置
├── templates/
│   └── index.html         # 前端页面
└── static/
    └── uploads/           # 上传图片存储
```

## 快速启动

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动服务
```bash
python app.py
```

### 3. 访问系统
浏览器打开：http://127.0.0.1:5000

## 功能说明

- 上传工业图片，自动识别缺陷并标注
- 缺陷等级自动判定（轻微/一般/严重）
- 历史检测记录自动存储
- 全局统计看板（总检测数、合格率）

## 核心算法

- 连通域分析：对应 LeetCode 岛屿问题
- OpenCV `connectedComponentsWithStats` 高速实现
- 时间复杂度：O(rows × cols)
