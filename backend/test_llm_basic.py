"""
基础测试 - 验证 LLM 服务基本功能
"""
from django.test import TestCase, Client
from django.urls import reverse
import json

class LLMServiceTestCase(TestCase):
    """LLM 服务测试用例"""
    
    def setUp(self):
        self.client = Client()
    
    def test_health_check(self):
        """测试健康检查端点"""
        response = self.client.get('/api/v1/llm/health/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('device', data)
    
    def test_models_list(self):
        """测试模型列表端点"""
        response = self.client.get('/api/v1/llm/models/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('available_models', data)
        self.assertIn('loaded_models', data)
        self.assertIn('qwen', data['available_models'])
        self.assertIn('llama', data['available_models'])
    
    def test_model_detail(self):
        """测试模型详情端点"""
        response = self.client.get('/api/v1/llm/models/qwen/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['name'], 'qwen')
        self.assertIn('loaded', data)
    
    def test_model_load_without_dependencies(self):
        """测试在没有 ML 依赖时加载模型"""
        response = self.client.post('/api/v1/llm/models/qwen/load/')
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertIn('error', data)
    
    def test_generate_without_dependencies(self):
        """测试在没有 ML 依赖时生成文本"""
        payload = {
            'prompt': 'Hello, world!',
            'parameters': {
                'temperature': 0.7,
                'max_length': 100
            }
        }
        
        response = self.client.post(
            '/api/v1/llm/generate/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('response', data)
        self.assertIn('ML dependencies not available', data['response'])
    
    def test_generate_with_invalid_data(self):
        """测试使用无效数据生成文本"""
        # 测试空提示
        response = self.client.post(
            '/api/v1/llm/generate/',
            data=json.dumps({'prompt': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # 测试无效参数
        payload = {
            'prompt': 'Hello',
            'parameters': {
                'temperature': 5.0  # 超出范围
            }
        }
        response = self.client.post(
            '/api/v1/llm/generate/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_streaming_generate(self):
        """测试流式生成端点"""
        payload = {
            'prompt': 'Tell me a story',
            'parameters': {
                'temperature': 0.8
            }
        }
        
        response = self.client.post(
            '/api/v1/llm/generate/stream/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/event-stream')

class LLMGatewayTestCase(TestCase):
    """LLM Gateway 测试用例"""
    
    def test_gateway_initialization(self):
        """测试 Gateway 初始化"""
        from app.llm.gateway import get_llm_gateway
        
        gateway = get_llm_gateway()
        self.assertIsNotNone(gateway)
        self.assertEqual(gateway.device, 'unavailable')  # 没有 ML 依赖
        self.assertEqual(len(gateway.models), 0)
    
    def test_model_info(self):
        """测试模型信息获取"""
        from app.llm.gateway import get_llm_gateway
        
        gateway = get_llm_gateway()
        info = gateway.get_model_info()
        
        self.assertIn('current_model', info)
        self.assertIn('loaded_models', info)
        self.assertIn('device', info)
        self.assertIn('available_models', info)

if __name__ == '__main__':
    import os
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    # 设置 Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
    django.setup()
    
    # 运行测试
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['__main__'])
    
    if failures:
        exit(1)