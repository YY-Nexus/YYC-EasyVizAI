# YYC³ EasyVizAI 本地大模型使用示例

## 基础使用

### 1. Python 客户端示例

```python
#!/usr/bin/env python3
"""
YYC³ EasyVizAI 本地大模型 Python 客户端示例
"""
import requests
import json
import time

class LLMClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1/llm"
    
    def health_check(self):
        """检查服务健康状态"""
        response = requests.get(f"{self.api_base}/health/")
        return response.json()
    
    def list_models(self):
        """获取模型列表"""
        response = requests.get(f"{self.api_base}/models/")
        return response.json()
    
    def load_model(self, model_key):
        """加载指定模型"""
        response = requests.post(f"{self.api_base}/models/{model_key}/load/")
        return response.json()
    
    def generate_text(self, prompt, model=None, **params):
        """生成文本（非流式）"""
        data = {
            "prompt": prompt,
            "parameters": params
        }
        if model:
            data["model"] = model
        
        response = requests.post(f"{self.api_base}/generate/", json=data)
        return response.json()
    
    def generate_streaming(self, prompt, model=None, **params):
        """生成文本（流式）"""
        data = {
            "prompt": prompt,
            "parameters": params
        }
        if model:
            data["model"] = model
        
        response = requests.post(
            f"{self.api_base}/generate/stream/", 
            json=data, 
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    if 'chunk' in data:
                        yield data['chunk']
                    elif data.get('done'):
                        break
                    elif 'error' in data:
                        raise RuntimeError(data['error'])

def main():
    client = LLMClient()
    
    # 1. 检查服务状态
    print("=== 服务状态检查 ===")
    health = client.health_check()
    print(f"状态: {health['status']}")
    print(f"设备: {health['device']}")
    print(f"当前模型: {health['current_model']}")
    
    # 2. 获取可用模型
    print("\\n=== 可用模型 ===")
    models = client.list_models()
    print(f"可用模型: {models['available_models']}")
    print(f"已加载模型: {models['loaded_models']}")
    
    # 3. 文本生成测试
    print("\\n=== 文本生成测试 ===")
    response = client.generate_text(
        "请介绍一下人工智能的发展历史",
        temperature=0.7,
        max_length=200
    )
    print(f"生成结果: {response}")

if __name__ == "__main__":
    main()
```

### 2. cURL 命令行示例

```bash
#!/bin/bash
# API 测试脚本

BASE_URL="http://localhost:8000/api/v1/llm"

echo "=== YYC³ EasyVizAI LLM API 测试 ==="

# 1. 健康检查
echo "1. 健康检查"
curl -s "$BASE_URL/health/" | python3 -m json.tool

# 2. 生成文本
echo -e "\\n2. 文本生成"
curl -s -X POST -H "Content-Type: application/json" \\
  -d '{
    "prompt": "请用一句话介绍人工智能",
    "parameters": {
      "temperature": 0.7,
      "max_length": 100
    }
  }' \\
  "$BASE_URL/generate/" | python3 -m json.tool
```

这些示例展示了如何使用 YYC³ EasyVizAI 本地大模型 API 进行文本生成和模型管理。