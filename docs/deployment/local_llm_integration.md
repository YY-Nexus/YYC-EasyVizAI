# 本地大模型集成指南

## 概述

本文档描述如何将本地大模型服务集成到 YYC³ EasyVizAI Web 应用中。

## 系统架构

```
┌─────────────────────────────────────────────────┐
│                前端应用                          │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │   聊天界面   │  │  实时组件    │  │ 模型管理  │ │
│  └─────────────┘  └─────────────┘  └──────────┘ │
└─────────────────────────────────────────────────┘
                        │
                   HTTP/WebSocket
                        │
┌─────────────────────────────────────────────────┐
│                API 网关                          │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │  RESTful API │  │  WebSocket   │  │ 事件总线  │ │
│  └─────────────┘  └─────────────┘  └──────────┘ │
└─────────────────────────────────────────────────┘
                        │
                   Django Channels
                        │
┌─────────────────────────────────────────────────┐
│               LLM 核心服务                       │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │ LLM Gateway │  │ 模型管理器    │  │ 推理引擎  │ │
│  └─────────────┘  └─────────────┘  └──────────┘ │
└─────────────────────────────────────────────────┘
                        │
                PyTorch/Transformers
                        │
┌─────────────────────────────────────────────────┐
│               模型层                             │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │    Qwen2    │  │    Llama2   │  │ 自定义模型 │ │
│  └─────────────┘  └─────────────┘  └──────────┘ │
└─────────────────────────────────────────────────┘
```

## 快速开始

### 1. 环境部署

```bash
# 克隆项目
git clone https://github.com/YY-Nexus/YYC-EasyVizAI.git
cd YYC-EasyVizAI/backend

# 运行部署脚本
chmod +x deploy_llm.sh
./deploy_llm.sh

# 激活虚拟环境
source .venv/bin/activate
```

### 2. 启动服务

```bash
# 启动 Django 服务
python manage.py runserver 0.0.0.0:8000

# 或使用 Makefile
cd ..
make backend
```

### 3. 验证部署

```bash
# 检查服务状态
curl http://localhost:8000/api/v1/llm/health/

# 列出可用模型
curl http://localhost:8000/api/v1/llm/models/
```

## 详细配置

### 环境变量

在 `.env` 文件中配置以下变量：

```bash
# LLM 核心配置
LLM_DEFAULT_MODEL=qwen          # 默认模型
LLM_MODEL_PATH=./models         # 模型存储路径
LLM_DEVICE=auto                 # 设备类型: auto/cpu/cuda
LLM_MAX_LENGTH=2048            # 最大生成长度
LLM_TEMPERATURE=0.7            # 生成温度
LLM_TOP_P=0.9                  # Top-p 采样

# 性能优化
LLM_BATCH_SIZE=1               # 批处理大小
LLM_NUM_THREADS=4              # CPU 线程数
LLM_MEMORY_FRACTION=0.8        # GPU 内存使用比例

# 缓存配置
LLM_ENABLE_CACHE=true          # 启用结果缓存
LLM_CACHE_TTL=3600            # 缓存过期时间(秒)

# 安全配置
LLM_MAX_REQUESTS_PER_MINUTE=60 # 每分钟最大请求数
LLM_MAX_PROMPT_LENGTH=4096     # 最大输入长度
```

This is the local LLM integration guide for the YYC³ EasyVizAI project with complete deployment instructions and examples.