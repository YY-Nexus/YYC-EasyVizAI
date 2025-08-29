#!/bin/bash

set -e

# 等待数据库服务启动
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "Database is ready!"

# 等待Redis服务启动
echo "Waiting for Redis..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 1
done
echo "Redis is ready!"

# 收集静态文件
echo "Collecting static files..."
python manage.py collectstatic --noinput

# 执行数据库迁移
echo "Running database migrations..."
python manage.py migrate --noinput

# 创建默认数据
echo "Loading initial data..."
python manage.py loaddata initial_data.json || echo "No initial data found, skipping..."

# 启动应用
echo "Starting application..."
exec "$@"