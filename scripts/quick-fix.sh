#!/bin/bash

# YYC³ EasyVizAI 快速修复脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "=== YYC³ EasyVizAI 快速修复工具 ==="
echo

# 检查是否在正确的目录
if [ ! -f "docker-compose.production.yml" ]; then
    log_error "未找到docker-compose.production.yml文件，请在项目根目录运行此脚本"
    exit 1
fi

# 1. 停止所有服务
log_info "步骤 1/8: 停止所有服务..."
docker-compose -f docker-compose.production.yml down 2>/dev/null || log_warning "部分服务停止失败，继续..."
log_success "服务已停止"

# 2. 清理Docker资源
log_info "步骤 2/8: 清理Docker资源..."
docker system prune -f >/dev/null 2>&1 || log_warning "Docker清理失败，继续..."
log_success "Docker资源已清理"

# 3. 清理大日志文件
log_info "步骤 3/8: 清理大日志文件..."
if [ -d "deployment/logs" ]; then
    find deployment/logs -name "*.log" -size +50M -delete 2>/dev/null || true
    find deployment/logs -name "*.log" -mtime +7 -exec gzip {} \; 2>/dev/null || true
    log_success "日志文件已清理"
else
    log_warning "日志目录不存在，跳过日志清理"
fi

# 4. 修复目录权限
log_info "步骤 4/8: 修复目录权限..."
if [ -d "deployment" ]; then
    chmod -R 755 deployment/ 2>/dev/null || log_warning "权限修复失败，可能需要sudo权限"
    log_success "目录权限已修复"
else
    log_warning "deployment目录不存在"
fi

# 5. 检查并创建必要目录
log_info "步骤 5/8: 检查必要目录..."
mkdir -p deployment/{nginx,ssl,data/{postgres,redis,neo4j,minio,qdrant},logs,backups} 2>/dev/null || true
mkdir -p deployment/data/postgres/{data,init} 2>/dev/null || true
mkdir -p deployment/logs/{nginx,app,celery} 2>/dev/null || true
log_success "必要目录已创建"

# 6. 检查环境配置
log_info "步骤 6/8: 检查环境配置..."
if [ ! -f ".env.production" ]; then
    log_warning "环境配置文件不存在，需要重新运行部署脚本"
    log_info "请运行: ./deploy.sh"
else
    log_success "环境配置文件存在"
fi

# 7. 重建并启动服务
log_info "步骤 7/8: 重建并启动服务..."
if [ -f ".env.production" ]; then
    log_info "启动基础服务..."
    docker-compose -f docker-compose.production.yml up -d postgres redis 2>/dev/null || log_warning "基础服务启动失败"
    
    log_info "等待基础服务就绪..."
    sleep 15
    
    log_info "启动应用服务..."
    docker-compose -f docker-compose.production.yml up -d 2>/dev/null || log_warning "应用服务启动失败"
    
    log_success "服务启动完成"
else
    log_error "缺少环境配置文件，跳过服务启动"
fi

# 8. 健康检查
log_info "步骤 8/8: 执行健康检查..."
sleep 30

# 检查服务状态
log_info "检查服务状态..."
docker-compose -f docker-compose.production.yml ps

# 检查关键端口
log_info "检查关键端口..."
for port in 80 5432 6379; do
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        log_success "端口 $port: 正常"
    else
        log_warning "端口 $port: 异常"
    fi
done

# 检查应用响应
log_info "检查应用响应..."
if curl -f -s http://localhost/health >/dev/null 2>&1; then
    log_success "应用健康检查: 通过"
else
    log_warning "应用健康检查: 失败"
fi

echo
log_success "=== 快速修复完成 ==="
echo

# 显示服务信息
echo "服务访问地址:"
echo "  前端应用: http://localhost"
echo "  后端API:  http://localhost/api"
echo "  管理后台: http://localhost/admin"
echo "  健康检查: http://localhost/health"
echo

echo "常用管理命令:"
echo "  查看状态: docker-compose -f docker-compose.production.yml ps"
echo "  查看日志: docker-compose -f docker-compose.production.yml logs -f"
echo "  重启服务: docker-compose -f docker-compose.production.yml restart"
echo "  停止服务: docker-compose -f docker-compose.production.yml down"
echo

# 检查是否需要进一步操作
need_action=false

if ! curl -f -s http://localhost/health >/dev/null 2>&1; then
    log_warning "健康检查失败，可能需要："
    echo "  1. 检查日志: docker-compose -f docker-compose.production.yml logs"
    echo "  2. 重新部署: ./deploy.sh"
    echo "  3. 手动诊断: ./scripts/diagnose.sh"
    need_action=true
fi

if ! docker-compose -f docker-compose.production.yml ps | grep -q "Up"; then
    log_warning "服务未正常启动，建议："
    echo "  1. 查看详细错误: docker-compose -f docker-compose.production.yml logs"
    echo "  2. 逐个启动服务进行调试"
    need_action=true
fi

if [ "$need_action" = false ]; then
    log_success "🎉 系统运行正常！"
else
    log_warning "⚠️  系统可能存在问题，请查看上述建议"
fi