"""
LLM Gateway Service - Core abstraction for local model management
"""
import os
import logging
from typing import Dict, Any, Optional, AsyncIterator
from pathlib import Path
from dataclasses import dataclass
from django.conf import settings

# Optional imports for ML dependencies
try:
    import torch
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    torch = None

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    name: str
    model_path: str
    type: str
    device: str
    requires_auth: bool = False
    max_length: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9

class LLMGateway:
    """
    Central gateway for managing local LLM models
    Supports both Qwen and Llama models with automatic device detection
    """
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.current_model: Optional[str] = None
        
        if not ML_AVAILABLE:
            logger.warning("ML dependencies not available. Install torch and transformers for full functionality.")
            self.device = 'unavailable'
        else:
            self.device = self._detect_device()
        
        logger.info(f"LLM Gateway initialized with device: {self.device}")
    
    def _detect_device(self) -> str:
        """Detect available device (CUDA/CPU)"""
        if not ML_AVAILABLE:
            return 'unavailable'
            
        device_setting = settings.LLM_CONFIG.get('DEVICE', 'auto')
        
        if device_setting == 'auto':
            if torch.cuda.is_available():
                return 'cuda'
            else:
                return 'cpu'
        return device_setting
    
    async def load_model(self, model_key: str) -> bool:
        """
        Load a model by key
        
        Args:
            model_key: Key from LLM_CONFIG.MODELS
            
        Returns:
            bool: True if model loaded successfully
        """
        if not ML_AVAILABLE:
            logger.error("ML dependencies not available. Cannot load models.")
            return False
            
        try:
            if model_key in self.models:
                logger.info(f"Model {model_key} already loaded")
                return True
                
            model_config = settings.LLM_CONFIG['MODELS'].get(model_key)
            if not model_config:
                logger.error(f"Model configuration not found for {model_key}")
                return False
            
            logger.info(f"Loading model {model_key}: {model_config['name']}")
            
            # Import here to avoid loading transformers at startup
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM
            except ImportError:
                logger.error("transformers library not available")
                return False
            
            model_name = model_config['name']
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True,
                cache_dir=settings.LLM_CONFIG['MODEL_PATH']
            )
            
            # Load model with appropriate settings
            model_kwargs = {
                'trust_remote_code': True,
                'cache_dir': settings.LLM_CONFIG['MODEL_PATH'],
                'torch_dtype': torch.float16 if self.device == 'cuda' else torch.float32,
            }
            
            if self.device == 'cuda':
                model_kwargs['device_map'] = 'auto'
            
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                **model_kwargs
            )
            
            if self.device == 'cpu':
                model = model.to('cpu')
            
            self.models[model_key] = {
                'model': model,
                'tokenizer': tokenizer,
                'config': ModelConfig(
                    name=model_name,
                    model_path=str(settings.LLM_CONFIG['MODEL_PATH']),
                    type=model_config['type'],
                    device=self.device,
                    requires_auth=model_config.get('requires_auth', False),
                    max_length=settings.LLM_CONFIG.get('MAX_LENGTH', 2048),
                    temperature=settings.LLM_CONFIG.get('TEMPERATURE', 0.7),
                    top_p=settings.LLM_CONFIG.get('TOP_P', 0.9),
                )
            }
            
            self.current_model = model_key
            logger.info(f"Successfully loaded model {model_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_key}: {str(e)}")
            return False
    
    async def generate_response(
        self, 
        prompt: str, 
        model_key: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate response from the model
        
        Args:
            prompt: Input text prompt
            model_key: Specific model to use (defaults to current)
            stream: Whether to stream the response
            **kwargs: Additional generation parameters
            
        Yields:
            str: Generated text chunks
        """
        if not ML_AVAILABLE:
            yield "Error: ML dependencies not available. Please install torch and transformers."
            return
            
        model_key = model_key or self.current_model
        
        if not model_key or model_key not in self.models:
            if not await self.load_model(model_key or settings.LLM_CONFIG['DEFAULT_MODEL']):
                yield f"Error: Failed to load model: {model_key}"
                return
            model_key = model_key or self.current_model
        
        model_data = self.models[model_key]
        model = model_data['model']
        tokenizer = model_data['tokenizer']
        config = model_data['config']
        
        # Prepare generation parameters
        generation_kwargs = {
            'max_length': kwargs.get('max_length', config.max_length),
            'temperature': kwargs.get('temperature', config.temperature),
            'top_p': kwargs.get('top_p', config.top_p),
            'do_sample': True,
            'pad_token_id': tokenizer.eos_token_id,
        }
        
        # Tokenize input
        inputs = tokenizer.encode(prompt, return_tensors='pt').to(model.device)
        
        try:
            if stream:
                # Streaming generation
                for chunk in self._generate_streaming(model, tokenizer, inputs, **generation_kwargs):
                    yield chunk
            else:
                # Non-streaming generation
                with torch.no_grad():
                    outputs = model.generate(inputs, **generation_kwargs)
                    response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
                    yield response
                    
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            yield f"Error: {str(e)}"
    
    def _generate_streaming(self, model, tokenizer, inputs, **kwargs):
        """Generator for streaming text output"""
        if not ML_AVAILABLE:
            yield "Error: ML dependencies not available"
            return
            
        # Simple implementation - in production, use more sophisticated streaming
        try:
            with torch.no_grad():
                outputs = model.generate(inputs, **kwargs)
                response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
                
                # Simulate streaming by yielding words
                words = response.split()
                for word in words:
                    yield word + " "
                    
        except Exception as e:
            yield f"Streaming error: {str(e)}"
    
    async def unload_model(self, model_key: str) -> bool:
        """Unload a model to free memory"""
        if model_key in self.models:
            del self.models[model_key]
            if ML_AVAILABLE and torch and torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info(f"Unloaded model {model_key}")
            
            if self.current_model == model_key:
                self.current_model = None
            return True
        return False
    
    def get_model_info(self, model_key: Optional[str] = None) -> Dict[str, Any]:
        """Get information about loaded model(s)"""
        if model_key:
            if model_key in self.models:
                return {
                    'name': model_key,
                    'config': self.models[model_key]['config'].__dict__,
                    'loaded': True
                }
            else:
                return {'name': model_key, 'loaded': False}
        
        return {
            'current_model': self.current_model,
            'loaded_models': list(self.models.keys()),
            'device': self.device,
            'available_models': list(settings.LLM_CONFIG['MODELS'].keys())
        }

# Global instance
_gateway = None

def get_llm_gateway() -> LLMGateway:
    """Get the global LLM gateway instance"""
    global _gateway
    if _gateway is None:
        _gateway = LLMGateway()
    return _gateway