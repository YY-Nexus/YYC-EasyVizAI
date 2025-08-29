#!/bin/bash

# YYC³ EasyVizAI 系统诊断脚本

echo "=== YYC³ EasyVizAI 系统诊断报告 ==="
echo "诊断时间: $(date)"
echo "========================================"
echo

# 1. 系统基本信息
echo "📋 1. 系统基本信息"
echo "----------------------------------------"
echo "操作系统: $(uname -o)"
echo "内核版本: $(uname -r)"
echo "架构: $(uname -m)"
echo "主机名: $(hostname)"
echo "运行时间: $(uptime -p 2>/dev/null || uptime)"
echo

# 2. 硬件资源
echo "💻 2. 硬件资源状态"
echo "----------------------------------------"
echo "CPU信息: $(nproc) 核心"
echo "CPU使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')%"
echo "内存信息:"
free -h
echo
echo "磁盘使用:"
df -h | grep -E '^/dev|^tmpfs|Filesystem'
echo

# 3. Docker环境
echo "🐳 3. Docker环境检查"
echo "----------------------------------------"
if command -v docker &> /dev/null; then
    echo "Docker版本: $(docker --version)"
    echo "Docker状态: $(systemctl is-active docker 2>/dev/null || echo '未知')"
    echo "Docker根目录: $(docker info 2>/dev/null | grep 'Docker Root Dir' | awk '{print $4}' || echo '未知')"
else
    echo "❌ Docker未安装"
fi

if command -v docker-compose &> /dev/null; then
    echo "Docker Compose版本: $(docker-compose --version)"
else
    echo "❌ Docker Compose未安装"
fi
echo

# 4. 服务状态
echo "🔧 4. 服务运行状态"
echo "----------------------------------------"
if [ -f "docker-compose.production.yml" ]; then
    echo "Docker Compose服务状态:"
    docker-compose -f docker-compose.production.yml ps 2>/dev/null || echo "无法获取服务状态"
    echo
    
    echo "容器资源使用:"
    docker stats --no-stream 2>/dev/null || echo "无法获取容器资源信息"
else
    echo "❌ 未找到docker-compose.production.yml文件"
fi
echo

# 5. 网络和端口
echo "🌐 5. 网络和端口检查"
echo "----------------------------------------"
echo "关键端口状态:"
for port in 80 443 5432 6379 7687 9000 6333; do
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo "✅ 端口 $port: 已使用"
    else
        echo "❌ 端口 $port: 未使用"
    fi
done
echo

echo "网络连接测试:"
if curl -s --connect-timeout 5 http://localhost/health >/dev/null 2>&1; then
    echo "✅ 本地健康检查: 正常"
else
    echo "❌ 本地健康检查: 失败"
fi

if curl -s --connect-timeout 5 http://www.google.com >/dev/null 2>&1; then
    echo "✅ 外网连接: 正常"
else
    echo "❌ 外网连接: 失败"
fi
echo

# 6. 配置文件检查
echo "📝 6. 配置文件检查"
echo "----------------------------------------"
if [ -f ".env.production" ]; then
    echo "✅ 环境配置文件存在"
    echo "配置项数量: $(grep -c '=' .env.production 2>/dev/null || echo 0)"
else
    echo "❌ 环境配置文件不存在"
fi

if [ -f "docker-compose.production.yml" ]; then
    echo "✅ Docker Compose配置存在"
    echo "服务数量: $(grep -c 'image:\|build:' docker-compose.production.yml 2>/dev/null || echo 0)"
else
    echo "❌ Docker Compose配置不存在"
fi
echo

# 7. 数据和日志
echo "📊 7. 数据和日志状态"
echo "----------------------------------------"
if [ -d "deployment" ]; then
    echo "部署目录大小:"
    du -sh deployment/* 2>/dev/null | sort -hr
    echo
    
    echo "日志文件状态:"
    if [ -d "deployment/logs" ]; then
        find deployment/logs -name "*.log" -type f -exec ls -lh {} \; 2>/dev/null | head -10
    else
        echo "日志目录不存在"
    fi
    echo
    
    echo "数据目录状态:"
    if [ -d "deployment/data" ]; then
        du -sh deployment/data/* 2>/dev/null
    else
        echo "数据目录不存在"
    fi
else
    echo "❌ 部署目录不存在"
fi
echo

# 8. 系统负载和性能
echo "⚡ 8. 系统性能指标"
echo "----------------------------------------"
echo "系统负载:"
uptime
echo

echo "进程排序 (CPU使用率前5):"
ps aux --sort=-%cpu | head -6
echo

echo "进程排序 (内存使用率前5):"
ps aux --sort=-%mem | head -6
echo

# 9. 安全检查
echo "🔒 9. 安全状态检查"
echo "----------------------------------------"
echo "防火墙状态:"
if command -v ufw &> /dev/null; then
    ufw status 2>/dev/null || echo "UFW未配置或无权限查看"
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --state 2>/dev/null || echo "firewalld未运行或无权限查看"
else
    echo "未检测到防火墙工具"
fi
echo

echo "SSH配置检查:"
if [ -f "/etc/ssh/sshd_config" ]; then
    echo "SSH端口: $(grep -E '^Port' /etc/ssh/sshd_config 2>/dev/null | awk '{print $2}' || echo '22 (默认)')"
    echo "密码认证: $(grep -E '^PasswordAuthentication' /etc/ssh/sshd_config 2>/dev/null | awk '{print $2}' || echo '未明确配置')"
else
    echo "SSH配置文件不存在或无权限访问"
fi
echo

# 10. 最近错误和警告
echo "⚠️  10. 最近错误和警告"
echo "----------------------------------------"
echo "系统日志中的错误 (最近20条):"
if command -v journalctl &> /dev/null; then
    journalctl --no-pager -p err -n 20 --since "1 hour ago" 2>/dev/null | tail -10 || echo "无法访问系统日志"
else
    echo "journalctl不可用"
fi
echo

echo "应用错误日志:"
if [ -d "deployment/logs" ]; then
    find deployment/logs -name "*error*.log" -type f -exec tail -5 {} \; -exec echo "---" \; 2>/dev/null | head -20
else
    echo "应用日志目录不存在"
fi
echo

# 11. 建议和总结
echo "💡 11. 诊断建议"
echo "----------------------------------------"

# 检查关键问题并给出建议
issues_found=false

# 检查内存使用
memory_usage=$(free | grep Mem | awk '{printf("%.1f"), $3/$2 * 100.0}')
if (( $(echo "$memory_usage > 80" | bc -l 2>/dev/null || echo 0) )); then
    echo "⚠️  内存使用率过高 (${memory_usage}%)，建议释放内存或增加内存"
    issues_found=true
fi

# 检查磁盘使用
disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$disk_usage" -gt 80 ]; then
    echo "⚠️  磁盘使用率过高 (${disk_usage}%)，建议清理磁盘空间"
    issues_found=true
fi

# 检查Docker状态
if ! systemctl is-active docker >/dev/null 2>&1; then
    echo "⚠️  Docker服务未运行，需要启动Docker服务"
    issues_found=true
fi

# 检查配置文件
if [ ! -f ".env.production" ]; then
    echo "⚠️  缺少环境配置文件，需要运行部署脚本"
    issues_found=true
fi

if [ "$issues_found" = false ]; then
    echo "✅ 系统状态良好，未发现明显问题"
fi

echo
echo "========================================"
echo "诊断完成时间: $(date)"
echo "========================================"

# 生成快速修复建议
echo
echo "🔧 快速修复命令:"
echo "----------------------------------------"
echo "# 重启所有服务"
echo "docker-compose -f docker-compose.production.yml restart"
echo
echo "# 清理系统资源"
echo "docker system prune -f"
echo
echo "# 检查服务状态"
echo "docker-compose -f docker-compose.production.yml ps"
echo
echo "# 查看服务日志"
echo "docker-compose -f docker-compose.production.yml logs -f"