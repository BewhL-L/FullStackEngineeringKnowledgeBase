FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目全部文件
COPY . .

# 创建必要目录
RUN mkdir -p logs static/uploads db

# 复制Nginx配置
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf

# 初始化数据库
RUN python -c "from db.database import init_db; init_db()"

# 暴露80端口
EXPOSE 80

# 启动命令：先启动Nginx，再启动Gunicorn
CMD service nginx start && gunicorn -c deploy/gunicorn.conf.py app:app
