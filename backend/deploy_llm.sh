#!/usr/bin/env bash
# 本地大模型部署脚本 (Local LLM Deployment Script)
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== YYC³ EasyVizAI 本地大模型部署脚本 ===${NC}"

# Check Python version
echo -e "${YELLOW}检查 Python 版本...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# Check if Python version is >= 3.8
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo -e "${GREEN}✓ Python 版本符合要求${NC}"
else
    echo -e "${RED}✗ Python 版本需要 >= 3.8${NC}"
    exit 1
fi

# Check CUDA availability
echo -e "${YELLOW}检查 CUDA 支持...${NC}"
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓ NVIDIA GPU 已检测到${NC}"
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader
    DEVICE="cuda"
else
    echo -e "${YELLOW}⚠ 未检测到 NVIDIA GPU，将使用 CPU 推理${NC}"
    DEVICE="cpu"
fi

# Create models directory
MODELS_DIR="./models"
echo -e "${YELLOW}创建模型目录...${NC}"
mkdir -p $MODELS_DIR
echo "模型目录: $(pwd)/$MODELS_DIR"

# Create virtual environment if not exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    python3 -m venv .venv
fi

# Activate virtual environment
echo -e "${YELLOW}激活虚拟环境...${NC}"
source .venv/bin/activate

# Install requirements
echo -e "${YELLOW}安装依赖包...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Install PyTorch with appropriate CUDA support
if [ "$DEVICE" == "cuda" ]; then
    echo -e "${YELLOW}安装 CUDA 版本的 PyTorch...${NC}"
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
else
    echo -e "${YELLOW}安装 CPU 版本的 PyTorch...${NC}"
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Create environment file
echo -e "${YELLOW}创建环境配置文件...${NC}"
cat > .env << EOF
# LLM Configuration
LLM_DEFAULT_MODEL=qwen
LLM_MODEL_PATH=$MODELS_DIR
LLM_DEVICE=$DEVICE
LLM_MAX_LENGTH=2048
LLM_TEMPERATURE=0.7
LLM_TOP_P=0.9

# Django Settings
SECRET_KEY=django-insecure-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Redis (for WebSocket)
REDIS_URL=redis://localhost:6379

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
EOF

echo -e "${GREEN}✓ 环境配置文件已创建${NC}"

# Run Django migrations
echo -e "${YELLOW}运行数据库迁移...${NC}"
python manage.py migrate

# Create superuser script
cat > create_superuser.py << 'EOF'
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser 'admin' created with password 'admin123'")
else:
    print("Superuser 'admin' already exists")
EOF

python create_superuser.py
rm create_superuser.py

echo -e "${GREEN}=== 部署完成! ===${NC}"
echo -e "${YELLOW}使用说明:${NC}"
echo "1. 启动服务: python manage.py runserver 0.0.0.0:8000"
echo "2. API 文档: http://localhost:8000/api/v1/llm/health/"
echo "3. 管理界面: http://localhost:8000/admin/ (用户名: admin, 密码: admin123)"
echo "4. 模型将在首次使用时自动下载到 $MODELS_DIR 目录"
echo ""
echo -e "${YELLOW}注意事项:${NC}"
echo "- 首次下载模型可能需要较长时间"
echo "- Qwen2-7B 模型约需要 14GB 存储空间"
echo "- Llama-2-7b 模型需要 HuggingFace 授权"
echo "- 建议至少 16GB 内存用于模型推理"

if [ "$DEVICE" == "cuda" ]; then
    echo "- CUDA 环境已配置，将使用 GPU 加速"
else
    echo "- 当前配置为 CPU 推理，速度较慢"
fi