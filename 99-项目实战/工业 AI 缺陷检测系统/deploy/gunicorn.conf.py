import multiprocessing

# 监听地址端口
bind = "0.0.0.0:8000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1
# 工作模式
worker_class = "gthread"
# 每个进程线程数
threads = 4

# 请求超时
timeout = 120
# 长连接保持
keepalive = 5

# 日志配置
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
