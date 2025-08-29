# YYC³ EasyVizAI - 本地大模型集成平台

[![ci](https://github.com/YY-Nexus/YYC-EasyVizAI/actions/workflows/buid.yml/badge.svg)](https://github.com/YY-Nexus/YYC-EasyVizAI/actions/workflows/buid.yml)

YYC³ EasyVizAI 是一个强大的本地大语言模型集成平台，支持 Qwen、Llama 等主流模型的本地部署和 API 服务。

## ✨ 核心特性

- 🚀 **本地模型部署**: 支持 Qwen2-7B、Llama-2-7b 等主流开源模型
- 🔄 **实时推理**: 提供同步和流式文本生成 API
- 🌐 **多协议支持**: RESTful API + WebSocket 实时通信
- ⚡ **智能设备检测**: 自动 CUDA/CPU 环境适配
- 🎯 **易于集成**: 完善的 API 文档和客户端示例
- 📊 **监控友好**: 健康检查和性能指标接口

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端应用       │────│   API 网关       │────│   LLM 核心服务   │
│ React/Vue/...   │    │ Django REST     │    │ PyTorch/HF     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                               │
                    ┌─────────────────┐
                    │   WebSocket     │
                    │  实时通信层      │
                    └─────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 16GB+ RAM（推荐）
- CUDA 11.8+（可选，GPU 加速）
- 20GB+ 可用磁盘空间

### 一键部署

```bash
# 克隆项目
git clone https://github.com/YY-Nexus/YYC-EasyVizAI.git
cd YYC-EasyVizAI/backend

# 运行自动部署脚本
chmod +x deploy_llm.sh
./deploy_llm.sh

# 启动服务
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### 验证部署

```bash
# 检查服务状态
curl http://localhost:8000/api/v1/llm/health/

# 查看可用模型
curl http://localhost:8000/api/v1/llm/models/
```

## 📚 API 文档

### 核心端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/llm/health/` | GET | 健康检查 |
| `/api/v1/llm/models/` | GET | 模型列表 |
| `/api/v1/llm/generate/` | POST | 文本生成 |
| `/api/v1/llm/generate/stream/` | POST | 流式生成 |
| `/ws/chat/{session_id}/` | WebSocket | 实时聊天 |

### 使用示例

```python
import requests

# 生成文本
response = requests.post('http://localhost:8000/api/v1/llm/generate/', json={
    "prompt": "请介绍一下人工智能",
    "parameters": {
        "temperature": 0.7,
        "max_length": 200
    }
})

print(response.json()['response'])
```

详细文档：[API 文档](docs/api/local_llm_api.md) | [使用示例](docs/examples/usage_examples.md)

## 🛠️ 模型管理

### 支持的模型

| 模型 | 大小 | 说明 |
|------|------|------|
| Qwen2-7B-Instruct | ~14GB | 阿里云通义千问，中文优化 |
| Llama-2-7b-chat-hf | ~13GB | Meta Llama2，需要授权 |

### 模型操作

```bash
# 使用模型管理工具
python manage_models.py list          # 列出可用模型
python manage_models.py download qwen # 下载模型
python manage_models.py test qwen     # 测试模型
python manage_models.py check         # 检查系统要求
```

## 🎯 集成指南

### Django 项目集成

```python
# settings.py
LLM_CONFIG = {
    'DEFAULT_MODEL': 'qwen',
    'MODEL_PATH': BASE_DIR / 'models',
    'DEVICE': 'auto',  # auto/cpu/cuda
}

# views.py
from app.llm.gateway import get_llm_gateway

async def my_view(request):
    gateway = get_llm_gateway()
    response = ""
    async for chunk in gateway.generate_response("Hello"):
        response += chunk
    return JsonResponse({'response': response})
```

### 前端集成

```javascript
// React 组件示例
const ChatComponent = () => {
  const [messages, setMessages] = useState([]);
  
  const sendMessage = async (text) => {
    const response = await fetch('/api/v1/llm/generate/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({prompt: text})
    });
    
    const data = await response.json();
    setMessages([...messages, {user: text, ai: data.response}]);
  };
  
  // ... 渲染逻辑
};
```

## 🔧 配置选项

### 环境变量

```bash
# 模型配置
LLM_DEFAULT_MODEL=qwen        # 默认模型
LLM_DEVICE=auto              # 设备选择: auto/cpu/cuda
LLM_MODEL_PATH=./models      # 模型存储路径
LLM_MAX_LENGTH=2048          # 最大生成长度
LLM_TEMPERATURE=0.7          # 生成温度

# 性能优化
LLM_BATCH_SIZE=1             # 批处理大小
LLM_NUM_THREADS=4            # CPU 线程数
```

详细配置：[集成指南](docs/deployment/local_llm_integration.md)

## 🎨 示例项目

### 简单聊天机器人

```bash
# 启动聊天演示
cd examples/
python chat_demo.py
```

### WebSocket 实时聊天

打开 `examples/websocket_chat.html` 体验实时聊天功能。

## 📊 性能指标

| 配置 | 首次加载 | 推理速度 | 内存占用 |
|------|----------|----------|----------|
| CPU (16 核心) | ~30s | ~2 tokens/s | ~8GB |
| GPU (RTX 3080) | ~10s | ~15 tokens/s | ~6GB |
| GPU (A100) | ~5s | ~50 tokens/s | ~8GB |

## 🔍 故障排除

### 常见问题

1. **模型下载失败**
   ```bash
   # 设置 HuggingFace 镜像
   export HF_ENDPOINT=https://hf-mirror.com
   ```

2. **CUDA 内存不足**
   ```bash
   # 使用 CPU 模式
   export LLM_DEVICE=cpu
   ```

3. **权限问题**
   ```bash
   # 检查模型目录权限
   chmod -R 755 models/
   ```

更多解决方案：[故障排除指南](docs/deployment/local_llm_integration.md#故障排除)

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Qwen](https://github.com/QwenLM/Qwen) - 阿里云通义千问模型
- [Llama](https://github.com/facebookresearch/llama) - Meta Llama 模型
- [Transformers](https://github.com/huggingface/transformers) - HuggingFace 库
- [Django](https://www.djangoproject.com/) - Web 框架

## 📞 联系我们

- 项目主页: [YY-Nexus/YYC-EasyVizAI](https://github.com/YY-Nexus/YYC-EasyVizAI)
- 问题反馈: [Issues](https://github.com/YY-Nexus/YYC-EasyVizAI/issues)
- 讨论交流: [Discussions](https://github.com/YY-Nexus/YYC-EasyVizAI/discussions)

---

⭐ 如果这个项目对你有帮助，请给个 Star！
