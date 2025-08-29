# YYC³ EasyVizAI Backend Dockerfile
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    postgresql-client \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 创建应用用户
RUN groupadd -g 1001 app && \
    useradd -r -u 1001 -g app app

# 创建应用目录
WORKDIR /app

# 复制并安装Python依赖
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/ ./

# 创建必要的目录
RUN mkdir -p logs media static backups && \
    chown -R app:app /app

# 复制启动脚本
COPY deployment/backend/entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python manage.py check --deploy || exit 1

# 切换到应用用户
USER app

# 暴露端口
EXPOSE 8000

# 设置入口点
ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "gevent", "--worker-connections", "1000", "--max-requests", "1000", "--max-requests-jitter", "100", "--timeout", "30", "--keep-alive", "2", "--access-logfile", "-", "--error-logfile", "-", "app.wsgi:application"]