# YYC³ EasyVizAI Frontend Dockerfile
FROM node:18-alpine as builder

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY frontend/package*.json ./
RUN npm ci --only=production

# 复制源代码
COPY frontend/ ./

# 构建生产版本
ENV NODE_ENV=production
RUN npm run build

# 生产镜像
FROM nginx:1.25-alpine

# 复制构建产物
COPY --from=builder /app/build /usr/share/nginx/html

# 复制nginx配置
COPY deployment/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# 创建健康检查
RUN echo '#!/bin/sh' > /usr/local/bin/healthcheck.sh && \
    echo 'curl -f http://localhost/health || exit 1' >> /usr/local/bin/healthcheck.sh && \
    chmod +x /usr/local/bin/healthcheck.sh

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]