# Docker 部署指南 / Docker Deployment Guide

## 概述 / Overview

本文档提供了 YYC³ EasyVizAI 项目的 Docker 部署解决方案，包括开发和生产环境的配置。

This document provides Docker deployment solutions for the YYC³ EasyVizAI project, including configurations for development and production environments.

## 快速开始 / Quick Start

### 1. 构建 Docker 镜像 / Build Docker Image

```bash
# 开发环境 / Development
docker build -t yyc-easyvizai:dev .

# 生产环境 / Production  
docker build -f Dockerfile.production -t yyc-easyvizai:prod .
```

### 2. 运行容器 / Run Container

```bash
# 简单运行 / Simple run
docker run -p 8000:8000 yyc-easyvizai:dev

# 使用环境变量 / With environment variables
docker run -p 8000:8000 \
  -e DEBUG=True \
  -e SECRET_KEY=your-secret-key \
  -e ALLOWED_HOSTS=localhost,127.0.0.1 \
  yyc-easyvizai:dev
```

### 3. 使用 Docker Compose (推荐 / Recommended)

```bash
# 启动完整堆栈 / Start full stack
docker-compose up -d

# 查看日志 / View logs
docker-compose logs -f

# 停止服务 / Stop services
docker-compose down
```

## 环境变量 / Environment Variables

### 基础配置 / Basic Configuration

| 变量名 / Variable | 默认值 / Default | 说明 / Description |
|------------------|------------------|-------------------|
| `DEBUG` | `False` | Django 调试模式 / Django debug mode |
| `SECRET_KEY` | 需要设置 / Required | Django 密钥 / Django secret key |
| `ALLOWED_HOSTS` | `localhost` | 允许的主机 / Allowed hosts |

### 数据库配置 / Database Configuration

| 变量名 / Variable | 默认值 / Default | 说明 / Description |
|------------------|------------------|-------------------|
| `DATABASE_URL` | `sqlite:///db.sqlite3` | 数据库连接URL / Database connection URL |
| `POSTGRES_DB` | `easyvizai` | PostgreSQL 数据库名 / PostgreSQL database name |
| `POSTGRES_USER` | `easyvizai` | PostgreSQL 用户名 / PostgreSQL username |
| `POSTGRES_PASSWORD` | `easyvizai_password` | PostgreSQL 密码 / PostgreSQL password |

### Redis 配置 / Redis Configuration

| 变量名 / Variable | 默认值 / Default | 说明 / Description |
|------------------|------------------|-------------------|
| `REDIS_URL` | `redis://redis:6379/0` | Redis 连接URL / Redis connection URL |
| `CELERY_BROKER_URL` | `redis://redis:6379/0` | Celery 消息队列 / Celery message broker |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/0` | Celery 结果存储 / Celery result backend |

### AI/LLM 配置 / AI/LLM Configuration

| 变量名 / Variable | 默认值 / Default | 说明 / Description |
|------------------|------------------|-------------------|
| `LLM_DEFAULT_MODEL` | `qwen` | 默认LLM模型 / Default LLM model |
| `LLM_MODEL_PATH` | `./models` | 模型存储路径 / Model storage path |
| `LLM_DEVICE` | `auto` | 推理设备 / Inference device |
| `LLM_MAX_LENGTH` | `2048` | 最大生成长度 / Maximum generation length |

## 文件结构 / File Structure

```
YYC-EasyVizAI/
├── Dockerfile                    # 开发环境 Dockerfile / Development Dockerfile
├── Dockerfile.production         # 生产环境 Dockerfile / Production Dockerfile
├── docker-compose.yml           # Docker Compose 配置 / Docker Compose configuration
├── .dockerignore                # Docker 忽略文件 / Docker ignore file
├── backend/
│   ├── requirements.txt         # Python 依赖 / Python dependencies
│   ├── requirements.minimal.txt # 最小依赖 / Minimal dependencies
│   └── manage.py               # Django 管理脚本 / Django management script
└── docs/
    └── docker-deployment.md    # 本文档 / This document
```

## 服务架构 / Service Architecture

### Docker Compose 服务 / Docker Compose Services

- **web**: Django 应用服务器 / Django application server
- **db**: PostgreSQL 数据库 / PostgreSQL database
- **redis**: Redis 缓存和消息队列 / Redis cache and message queue
- **celery**: Celery 后台任务处理 / Celery background task processing

### 端口映射 / Port Mapping

| 服务 / Service | 容器端口 / Container Port | 主机端口 / Host Port |
|---------------|--------------------------|---------------------|
| Django Web | 8000 | 8000 |
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6379 |

## 故障排除 / Troubleshooting

### 常见问题 / Common Issues

1. **构建失败 - SSL 证书错误 / Build fails - SSL certificate error**
   ```bash
   # 解决方案：使用信任的主机 / Solution: Use trusted hosts
   pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org
   ```

2. **requirements.txt 找不到 / requirements.txt not found**
   ```bash
   # 确保从正确目录构建 / Ensure building from correct directory
   docker build -t yyc-easyvizai .
   ```

3. **数据库连接失败 / Database connection fails**
   ```bash
   # 检查 Docker Compose 服务状态 / Check Docker Compose service status
   docker-compose ps
   docker-compose logs db
   ```

4. **内存不足 / Out of memory**
   ```bash
   # AI/ML 依赖需要大量内存 / AI/ML dependencies require substantial memory
   # 考虑使用 requirements.minimal.txt / Consider using requirements.minimal.txt
   ```

### 调试命令 / Debug Commands

```bash
# 进入容器 / Enter container
docker exec -it yyc-easyvizai-web bash

# 查看日志 / View logs
docker-compose logs -f web

# 重启服务 / Restart service
docker-compose restart web

# 清理并重建 / Clean and rebuild
docker-compose down --volumes
docker-compose build --no-cache
docker-compose up -d
```

## 生产部署建议 / Production Deployment Recommendations

### 安全考虑 / Security Considerations

1. **设置强密码 / Set strong passwords**
   ```bash
   # 生成随机密钥 / Generate random secret key
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **使用环境文件 / Use environment file**
   ```bash
   # 创建 .env 文件 / Create .env file
   cp .env.example .env
   # 编辑配置 / Edit configuration
   nano .env
   ```

3. **启用 HTTPS / Enable HTTPS**
   - 使用反向代理 (Nginx/Traefik) / Use reverse proxy (Nginx/Traefik)
   - 配置 SSL 证书 / Configure SSL certificates

### 性能优化 / Performance Optimization

1. **使用生产服务器 / Use production server**
   ```dockerfile
   # 替换开发服务器 / Replace development server
   CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi:application"]
   ```

2. **配置资源限制 / Configure resource limits**
   ```yaml
   # docker-compose.yml
   services:
     web:
       deploy:
         resources:
           limits:
             memory: 2G
             cpus: '1.0'
   ```

3. **启用静态文件服务 / Enable static file serving**
   - 使用 Nginx 服务静态文件 / Use Nginx for static files
   - 配置 CDN / Configure CDN

## 监控和日志 / Monitoring and Logging

### 健康检查 / Health Checks

```bash
# 检查应用状态 / Check application status
curl -f http://localhost:8000/health/ || echo "Service down"

# 检查数据库连接 / Check database connection
docker exec yyc-easyvizai-web python manage.py check --database default
```

### 日志管理 / Log Management

```bash
# 实时查看日志 / Real-time log viewing
docker-compose logs -f --tail=100

# 导出日志 / Export logs
docker-compose logs > app.log
```

## 更新和维护 / Updates and Maintenance

### 应用更新 / Application Updates

```bash
# 拉取最新代码 / Pull latest code
git pull origin main

# 重建镜像 / Rebuild image
docker-compose build --no-cache

# 滚动更新 / Rolling update
docker-compose up -d --force-recreate
```

### 数据备份 / Data Backup

```bash
# 备份数据库 / Backup database
docker exec yyc-easyvizai-db pg_dump -U easyvizai easyvizai > backup.sql

# 备份媒体文件 / Backup media files
docker cp yyc-easyvizai-web:/app/media ./media-backup
```

---

## 支持 / Support

如遇问题，请参考：/ For issues, please refer to:
- [项目文档 / Project Documentation](../README.md)
- [问题跟踪 / Issue Tracker](https://github.com/YY-Nexus/YYC-EasyVizAI/issues)
- [开发指南 / Development Guide](../docs/architecture/developer_guide.md)