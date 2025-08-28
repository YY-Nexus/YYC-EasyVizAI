# 本地开发快速开始

## 1. 系统要求

| 项 | 最低版本 | 推荐 |
|----|----------|------|
| OS | macOS 13 / Linux | Linux (Ubuntu 22.04) |
| Python | 3.11 | 3.11.x |
| Node.js | 18 | 20 LTS |
| Docker | 24+ | 最新 |
| PostgreSQL | 14 | 15 |
| Redis | 6 | 7 |
| Neo4j | 5.x | 5.x |
| MinIO / S3 | 任意 | MinIO 最新 |
| 向量库 | Qdrant 1.x | Qdrant 1.x |

## 2. 克隆与初始化

```bash
git clone https://github.com/<org>/easyvizai.git
cd easyvizai
make bootstrap  # 或 scripts/dev_bootstrap.sh
```

## 3. 环境变量（.env 示例）

```
# 通用
APP_ENV=dev
SECRET_KEY=dev-secret
DEBUG=1

# 数据库
DB_HOST=localhost
DB_PORT=5432
DB_USER=easyviz
DB_PASS=easyviz
DB_NAME=easyviz

# Redis/Celery
REDIS_URL=redis://localhost:6379/0

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_pass

# MinIO
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minio
S3_SECRET_KEY=minio123
S3_BUCKET=easyviz

# Qdrant
VECTOR_HOST=localhost
VECTOR_PORT=6333

# Feature Flags (文件/远端服务)
FEATURE_FLAGS_SOURCE=file

# Emotion / LLM 模型网关
LLM_GATEWAY_URL=http://localhost:8089
EMOTION_MODEL_PATH=./models/emotion.onnx

# Miyu 加密
KMS_ENDPOINT=http://localhost:8200
KMS_KEY_ID=easyviz-master
MIYU_CLIENT_SIDE_ENCRYPTION=1

# WebSocket
WS_ORIGIN=http://localhost:5173
```

## 4. 启动依赖（Docker）

```bash
docker compose -f docker/docker-compose.yml up -d
```

## 5. 后端安装与运行

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
celery -A app.core.tasks worker -Q default,report,code --loglevel=INFO
```

## 6. 前端启动

```bash
cd frontend
pnpm install   # 或 npm/yarn
pnpm dev
```

访问 <http://localhost:5173>

## 7. 运行测试

```bash
make test       # 后端 pytest + 前端 vitest
make lint       # ruff + eslint
```

## 8. 常用 Make 命令

| 命令 | 说明 |
|------|------|
| make bootstrap | 安装工具/钩子 |
| make migrate | 数据库迁移 |
| make dev | 启动后端 + 前端（tmux） |
| make test | 运行全部测试 |
| make lint | 代码规范检查 |
| make fmt | 自动格式化 |
| make openapi | 生成 OpenAPI |
| make seed | 生成演示数据 |
| make clean | 清理缓存 |

## 9. 访问 API

- OpenAPI：`/openapi/v1.yaml` 或 `http://localhost:8000/api/docs`（若集成 swagger）
- 示例：

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
 -H 'Content-Type: application/json' \
 -d '{"username":"demo","password":"demo"}'
```

## 10. 常见问题

| 问题 | 解决 |
|------|------|
| 端口冲突 | 修改 .env 中端口或 compose 映射 |
| WebSocket 403 | 确认 WS_ORIGIN 与前端访问域一致 |
| Celery 无消费 | 检查 Redis URL / 队列名称一致 |
| ONNX 模型加载报错 | 确认路径 / Python & onnxruntime 版本 |

## 11. 下一步阅读

- 架构：architecture_walkthrough.md
- 事件/实时：realtime_and_events.md
- 安全：security_privacy.m
