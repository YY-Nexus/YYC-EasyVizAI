#!/usr/bin/env python3
"""
模型管理脚本 - Model Management Script
用于下载、验证和管理本地大模型
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from app.llm.gateway import get_llm_gateway

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_model(model_key: str):
    """下载指定模型"""
    print(f"开始下载模型: {model_key}")
    
    if model_key not in settings.LLM_CONFIG['MODELS']:
        print(f"错误: 未知的模型 '{model_key}'")
        print(f"可用模型: {list(settings.LLM_CONFIG['MODELS'].keys())}")
        return False
    
    try:
        # 使用 transformers 预下载模型
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        model_config = settings.LLM_CONFIG['MODELS'][model_key]
        model_name = model_config['name']
        
        print(f"下载模型: {model_name}")
        print(f"保存路径: {settings.LLM_CONFIG['MODEL_PATH']}")
        
        # 下载 tokenizer
        print("下载 tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir=settings.LLM_CONFIG['MODEL_PATH']
        )
        
        # 下载模型
        print("下载模型权重...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir=settings.LLM_CONFIG['MODEL_PATH'],
            torch_dtype='auto'  # 让系统自动选择数据类型
        )
        
        print(f"✓ 模型 {model_key} 下载完成")
        return True
        
    except Exception as e:
        print(f"✗ 下载失败: {str(e)}")
        return False

def list_models():
    """列出所有可用模型"""
    print("可用模型配置:")
    for key, config in settings.LLM_CONFIG['MODELS'].items():
        print(f"  {key}: {config['name']}")
        print(f"    类型: {config['type']}")
        print(f"    需要授权: {'是' if config.get('requires_auth') else '否'}")
        print()

async def test_model(model_key: str):
    """测试模型加载和推理"""
    print(f"测试模型: {model_key}")
    
    try:
        gateway = get_llm_gateway()
        
        # 尝试加载模型
        print("加载模型...")
        success = await gateway.load_model(model_key)
        
        if not success:
            print("✗ 模型加载失败")
            return False
        
        print("✓ 模型加载成功")
        
        # 测试推理
        print("测试推理...")
        test_prompt = "你好，请介绍一下你自己。"
        
        response_text = ""
        async for chunk in gateway.generate_response(
            prompt=test_prompt,
            model_key=model_key,
            stream=False,
            max_length=100
        ):
            response_text += chunk
        
        print(f"测试输入: {test_prompt}")
        print(f"模型回复: {response_text.strip()}")
        print("✓ 推理测试成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False

def check_requirements():
    """检查系统要求"""
    print("检查系统要求...")
    
    try:
        import torch
        print(f"✓ PyTorch 版本: {torch.__version__}")
        
        if torch.cuda.is_available():
            print(f"✓ CUDA 可用: {torch.version.cuda}")
            print(f"  GPU 数量: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                print(f"  GPU {i}: {gpu_name} ({memory:.1f}GB)")
        else:
            print("⚠ CUDA 不可用，将使用 CPU")
        
        import transformers
        print(f"✓ Transformers 版本: {transformers.__version__}")
        
        # 检查磁盘空间
        models_path = Path(settings.LLM_CONFIG['MODEL_PATH'])
        if models_path.exists():
            import shutil
            free_space = shutil.disk_usage(models_path).free / 1024**3
            print(f"✓ 模型目录可用空间: {free_space:.1f}GB")
            
            if free_space < 20:
                print("⚠ 磁盘空间不足，建议至少保留 20GB")
        
        print("✓ 系统要求检查完成")
        return True
        
    except ImportError as e:
        print(f"✗ 缺少依赖: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='YYC³ EasyVizAI 模型管理工具')
    parser.add_argument('command', choices=['list', 'download', 'test', 'check'], 
                       help='要执行的命令')
    parser.add_argument('--model', type=str, help='模型名称 (用于 download 和 test 命令)')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_models()
    
    elif args.command == 'download':
        if not args.model:
            print("错误: download 命令需要指定 --model 参数")
            return 1
        
        if not check_requirements():
            return 1
            
        success = download_model(args.model)
        return 0 if success else 1
    
    elif args.command == 'test':
        if not args.model:
            print("错误: test 命令需要指定 --model 参数")
            return 1
        
        if not check_requirements():
            return 1
            
        import asyncio
        success = asyncio.run(test_model(args.model))
        return 0 if success else 1
    
    elif args.command == 'check':
        success = check_requirements()
        return 0 if success else 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())