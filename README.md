[![ci](https://github.com/YY-Nexus/YYC-EasyVizAI/actions/workflows/buid.yml/badge.svg)](https://github.com/YY-Nexus/YYC-EasyVizAI/actions/workflows/buid.yml)

# YYC³ EasyVizAI 项目

基于 AI 驱动的可视化智能分析平台，提供端到端的数据分析和可视化解决方案。

## 🚀 快速部署

### 一键部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/YY-Nexus/YYC-EasyVizAI.git
cd YYC-EasyVizAI

# 2. 一键部署
chmod +x deploy.sh
./deploy.sh
```

部署完成后访问：
- **前端应用**: http://localhost
- **后端API**: http://localhost/api  
- **管理后台**: http://localhost/admin

### 系统要求

- **OS**: Linux/macOS/Windows (推荐 Ubuntu 22.04)
- **内存**: 4GB+ (推荐 8GB)
- **存储**: 20GB+ 可用空间
- **软件**: Docker 20.10+, Docker Compose 2.0+

## 📚 文档

- [本地部署指南](docs/deployment/本地部署指南.md) - 完整部署流程
- [常见问题解决](docs/deployment/常见问题解决.md) - 故障排除指南
- [开发者指南](docs/developer/getting_started.md) - 开发环境搭建

## 🛠️ 管理工具

```bash
# 诊断系统状态
./scripts/diagnose.sh

# 快速修复常见问题
./scripts/quick-fix.sh

# 查看服务状态
docker-compose -f docker-compose.production.yml ps

# 查看日志
docker-compose -f docker-compose.production.yml logs -f
```

## 🏗️ 架构

- **前端**: React 18 + TypeScript + Ant Design
- **后端**: Django 4.2 + DRF + Celery
- **数据库**: PostgreSQL + Redis + Neo4j + Qdrant
- **存储**: MinIO (S3 Compatible)
- **部署**: Docker + Nginx

## 📞 技术支持

- [GitHub Issues](https://github.com/YY-Nexus/YYC-EasyVizAI/issues)
- [部署文档](docs/deployment/)
- [开发文档](docs/developer/)
