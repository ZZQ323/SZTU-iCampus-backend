FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 最小化系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 暴露端口
EXPOSE 8001

# 设置环境变量
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

# 启动命令
CMD ["python", "main.py"] 