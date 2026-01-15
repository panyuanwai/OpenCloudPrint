# Stage 1: 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖 (包含 LibreOffice 用于文档转换)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libreoffice \
    libreoffice-writer \
    libpng16-16 \
    libjpeg62-turbo \
    && rm -rf /var/lib/apt/lists/*

# 设置 LibreOffice 无头模式
RUN echo "export DISPLAY=:99" >> /root/.bashrc

# 复制 requirements 文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/uploads /app/converted /app/logs

# 暴露端口 (虽然 worker 通常不需要暴露端口)
EXPOSE 5555

# 默认启动 Celery Worker
CMD ["celery", "-A", "app.tasks.celery_app", "worker", "--loglevel=info", "--concurrency=2"]
