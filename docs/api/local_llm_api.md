# 本地大模型 API 文档

## 概述

YYC³ EasyVizAI 本地大模型 API 提供了完整的本地 LLM 推理服务，支持 Qwen 和 Llama 等主流模型。

## 基础信息

- **基础 URL**: `http://localhost:8000/api/v1/`
- **认证**: 暂时使用 AllowAny（生产环境需要添加认证）
- **内容类型**: `application/json`

## API 端点

### 1. 健康检查

**GET** `/api/v1/llm/health/`

检查 LLM 服务状态和当前加载的模型。

**响应示例**:
```json
{
  "status": "healthy",
  "device": "cuda",
  "loaded_models": ["qwen"],
  "current_model": "qwen"
}
```

### 2. 模型管理

#### 列出所有模型
**GET** `/api/v1/llm/models/`

**响应示例**:
```json
{
  "current_model": "qwen",
  "loaded_models": ["qwen"],
  "device": "cuda",
  "available_models": ["qwen", "llama"]
}
```

#### 获取模型详情
**GET** `/api/v1/llm/models/{model_key}/`

**响应示例**:
```json
{
  "name": "qwen",
  "loaded": true,
  "config": {
    "name": "Qwen/Qwen2-7B-Instruct",
    "model_path": "/path/to/models",
    "type": "causal_lm",
    "device": "cuda",
    "max_length": 2048,
    "temperature": 0.7,
    "top_p": 0.9
  }
}
```

#### 加载模型
**POST** `/api/v1/llm/models/{model_key}/load/`

**响应示例**:
```json
{
  "message": "Model qwen loaded successfully"
}
```

#### 卸载模型
**POST** `/api/v1/llm/models/{model_key}/unload/`

**响应示例**:
```json
{
  "message": "Model qwen unloaded successfully"
}
```

### 3. 文本生成

#### 非流式生成
**POST** `/api/v1/llm/generate/`

**请求体**:
```json
{
  "prompt": "你好，请介绍一下你自己。",
  "model": "qwen",
  "parameters": {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_length": 512
  }
}
```

**响应示例**:
```json
{
  "response": "你好！我是Qwen，一个由阿里云开发的大型语言模型...",
  "model": "qwen",
  "prompt": "你好，请介绍一下你自己。"
}
```

#### 流式生成
**POST** `/api/v1/llm/generate/stream/`

**请求体**: 同上

**响应格式**: Server-Sent Events (SSE)
```
data: {"chunk": "你好！"}

data: {"chunk": "我是"}

data: {"chunk": "Qwen..."}

data: {"done": true}
```

### 4. WebSocket 实时聊天

**WebSocket URL**: `ws://localhost:8000/ws/chat/{session_id}/`

#### 发送消息
```json
{
  "type": "chat_message",
  "message": "你好，请介绍一下你自己。",
  "model": "qwen",
  "stream": true,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 接收消息
```json
{
  "type": "assistant_chunk",
  "chunk": "你好！",
  "model": "qwen"
}
```

#### 模型切换
```json
{
  "type": "model_switch",
  "model": "llama"
}
```

## 参数说明

### 生成参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `temperature` | float | 0.7 | 控制生成随机性 (0.0-2.0) |
| `top_p` | float | 0.9 | 核采样参数 (0.0-1.0) |
| `max_length` | int | 2048 | 最大生成长度 (1-4096) |
| `do_sample` | bool | true | 是否使用采样 |

## 错误处理

所有 API 错误都以 JSON 格式返回：

```json
{
  "error": "错误描述信息"
}
```

常见错误码：
- `400 Bad Request`: 请求参数错误
- `500 Internal Server Error`: 服务器内部错误
- `503 Service Unavailable`: 服务不可用

## 使用示例

### Python 客户端示例

```python
import requests
import json

# 检查服务状态
response = requests.get('http://localhost:8000/api/v1/llm/health/')
print(response.json())

# 生成文本
data = {
    "prompt": "请写一首关于春天的诗",
    "model": "qwen",
    "parameters": {
        "temperature": 0.8,
        "max_length": 256
    }
}

response = requests.post(
    'http://localhost:8000/api/v1/llm/generate/',
    json=data
)
print(response.json()['response'])
```

### JavaScript 客户端示例

```javascript
// 流式生成
const response = await fetch('/api/v1/llm/generate/stream/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    prompt: '请介绍一下人工智能的发展历史',
    model: 'qwen',
    parameters: {
      temperature: 0.7
    }
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      if (data.chunk) {
        console.log(data.chunk);
      }
    }
  }
}
```

### WebSocket 客户端示例

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/demo_session/');

ws.onopen = function() {
  console.log('WebSocket 连接已建立');
  
  // 发送消息
  ws.send(JSON.stringify({
    type: 'chat_message',
    message: '你好，请介绍一下你自己',
    stream: true
  }));
};

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  if (data.type === 'assistant_chunk') {
    console.log(data.chunk);
  } else if (data.type === 'error') {
    console.error(data.error);
  }
};
```

## 部署注意事项

1. **模型下载**: 首次使用时会自动下载模型，可能需要较长时间
2. **内存要求**: 7B 模型至少需要 16GB 内存
3. **GPU 加速**: 建议使用 CUDA 环境以获得更好性能
4. **网络连接**: 需要访问 HuggingFace 下载模型权重
5. **授权要求**: Llama 模型需要 HuggingFace 授权令牌

## 监控和日志

- 应用日志位于 `django.log`
- WebSocket 连接状态可通过健康检查端点获取
- 模型推理性能指标建议通过自定义监控系统收集