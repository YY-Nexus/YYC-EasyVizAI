#!/bin/bash

# YYC³ EasyVizAI 一键部署脚本
# 适用于低门槛服务器环境的轻量化部署

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查系统要求
check_requirements() {
    log_info "检查系统要求..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    # 检查端口占用
    check_ports=("80" "443" "5432" "6379" "7687" "9000" "6333")
    for port in "${check_ports[@]}"; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            log_warning "端口 $port 已被占用，可能会导致冲突"
        fi
    done
    
    log_success "系统要求检查完成"
}

# 创建必要的目录
create_directories() {
    log_info "创建部署目录..."
    
    mkdir -p deployment/{nginx,ssl,data/{postgres,redis,neo4j,minio,qdrant},logs,backups}
    mkdir -p deployment/data/postgres/{data,init}
    mkdir -p deployment/logs/{nginx,app,celery}
    
    log_success "目录创建完成"
}

# 生成环境配置文件
generate_env() {
    log_info "生成环境配置文件..."
    
    if [ ! -f ".env.production" ]; then
        cat > .env.production << EOF
# 生产环境配置
APP_ENV=production
DEBUG=0
SECRET_KEY=$(openssl rand -hex 32)

# 服务端口配置
BACKEND_PORT=8000
FRONTEND_PORT=3000
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443

# 数据库配置
DB_HOST=postgres
DB_PORT=5432
DB_USER=easyviz
DB_PASS=$(openssl rand -hex 16)
DB_NAME=easyviz

# Redis配置
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379

# Neo4j配置
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=$(openssl rand -hex 16)

# MinIO配置
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minio
S3_SECRET_KEY=$(openssl rand -hex 16)
S3_BUCKET=easyviz

# Qdrant配置
VECTOR_HOST=qdrant
VECTOR_PORT=6333

# 特性标志配置
FEATURE_FLAGS_SOURCE=file

# LLM网关配置
LLM_GATEWAY_URL=http://localhost:8089

# 健康检查配置
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
HEALTH_CHECK_RETRIES=3

# 日志配置
LOG_LEVEL=INFO
LOG_BACKUP_DAYS=30
EOF
        log_success "环境配置文件已生成: .env.production"
    else
        log_warning "环境配置文件已存在，跳过生成"
    fi
}

# 初始化数据库
init_database() {
    log_info "初始化数据库脚本..."
    
    cat > deployment/data/postgres/init/01-init.sql << 'EOF'
-- 创建数据库和用户
CREATE DATABASE easyviz;
CREATE USER easyviz WITH ENCRYPTED PASSWORD 'REPLACE_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE easyviz TO easyviz;
ALTER USER easyviz CREATEDB;
EOF
    
    log_success "数据库初始化脚本已创建"
}

# 部署应用
deploy_application() {
    log_info "开始部署应用..."
    
    # 加载环境变量
    source .env.production
    
    # 替换数据库密码
    sed -i "s/REPLACE_PASSWORD/$DB_PASS/g" deployment/data/postgres/init/01-init.sql
    
    # 构建和启动服务
    log_info "启动Docker服务..."
    docker-compose -f docker-compose.production.yml up -d --build
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 数据库迁移
    log_info "执行数据库迁移..."
    docker-compose -f docker-compose.production.yml exec -T backend python manage.py migrate
    
    # 创建超级用户（如果不存在）
    log_info "创建管理员账户..."
    docker-compose -f docker-compose.production.yml exec -T backend python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("管理员账户已创建: admin/admin123")
else:
    print("管理员账户已存在")
EOF
    
    log_success "应用部署完成！"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查各服务状态
    services=("nginx" "backend" "frontend" "postgres" "redis" "neo4j" "minio" "qdrant")
    
    for service in "${services[@]}"; do
        if docker-compose -f docker-compose.production.yml ps "$service" | grep -q "Up"; then
            log_success "$service 服务运行正常"
        else
            log_error "$service 服务未正常运行"
        fi
    done
    
    # 检查应用响应
    log_info "检查应用响应..."
    if curl -f http://localhost/health &> /dev/null; then
        log_success "应用健康检查通过"
    else
        log_warning "应用健康检查失败，请检查服务状态"
    fi
}

# 显示部署信息
show_deployment_info() {
    log_success "=== 部署完成 ==="
    echo ""
    echo "访问地址："
    echo "  前端应用: http://localhost"
    echo "  后端API:  http://localhost/api"
    echo "  管理后台: http://localhost/admin"
    echo ""
    echo "默认账户："
    echo "  用户名: admin"
    echo "  密码:   admin123"
    echo ""
    echo "服务管理命令："
    echo "  查看状态: docker-compose -f docker-compose.production.yml ps"
    echo "  查看日志: docker-compose -f docker-compose.production.yml logs [service]"
    echo "  停止服务: docker-compose -f docker-compose.production.yml down"
    echo "  重启服务: docker-compose -f docker-compose.production.yml restart"
    echo ""
    echo "日志文件位置: ./deployment/logs/"
    echo "数据备份位置: ./deployment/backups/"
    echo ""
}

# 主函数
main() {
    echo "=== YYC³ EasyVizAI 一键部署脚本 ==="
    echo ""
    
    check_requirements
    create_directories
    generate_env
    init_database
    deploy_application
    health_check
    show_deployment_info
    
    log_success "部署流程完成！"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi