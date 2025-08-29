"""
LLM Router for multi-model parameter switching and management
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncGenerator, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import time
import asyncio
from django.conf import settings

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Supported model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    AZURE = "azure"


@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    provider: ModelProvider
    model_id: str
    display_name: str
    context_window: int
    supports_functions: bool = False
    supports_streaming: bool = True
    temperature_range: tuple = (0.0, 2.0)
    max_tokens_default: int = 1000
    cost_per_1k_tokens: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['provider'] = self.provider.value
        return result


@dataclass
class ChatMessage:
    """Chat message for LLM"""
    role: str
    content: str
    tool_calls: List[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {"role": self.role, "content": self.content}
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        return result


@dataclass
class LLMRequest:
    """Request to LLM"""
    messages: List[ChatMessage]
    model: str
    temperature: float = 0.7
    max_tokens: int = 1000
    stream: bool = False
    tools: List[Dict[str, Any]] = None
    system_prompt: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "messages": [msg.to_dict() for msg in self.messages],
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": self.stream
        }
        
        if self.tools:
            result["tools"] = self.tools
            
        if self.system_prompt and self.messages and self.messages[0].role != "system":
            # Prepend system message
            result["messages"].insert(0, {"role": "system", "content": self.system_prompt})
            
        return result


@dataclass
class LLMResponse:
    """Response from LLM"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    tool_calls: List[Dict[str, Any]] = None
    response_time_ms: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, api_key: str = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @property
    @abstractmethod
    def provider_name(self) -> ModelProvider:
        """Provider name"""
        pass
    
    @property
    @abstractmethod
    def supported_models(self) -> List[ModelConfig]:
        """List of supported models"""
        pass
    
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response"""
        pass
    
    @abstractmethod
    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        pass
    
    def get_model_config(self, model_id: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model"""
        for model in self.supported_models:
            if model.model_id == model_id:
                return model
        return None


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation"""
    
    @property
    def provider_name(self) -> ModelProvider:
        return ModelProvider.OPENAI
    
    @property
    def supported_models(self) -> List[ModelConfig]:
        return [
            ModelConfig(
                provider=ModelProvider.OPENAI,
                model_id="gpt-3.5-turbo",
                display_name="GPT-3.5 Turbo",
                context_window=4096,
                supports_functions=True,
                cost_per_1k_tokens=0.0015
            ),
            ModelConfig(
                provider=ModelProvider.OPENAI,
                model_id="gpt-4",
                display_name="GPT-4",
                context_window=8192,
                supports_functions=True,
                cost_per_1k_tokens=0.03
            ),
            ModelConfig(
                provider=ModelProvider.OPENAI,
                model_id="gpt-4-turbo-preview",
                display_name="GPT-4 Turbo",
                context_window=128000,
                supports_functions=True,
                cost_per_1k_tokens=0.01
            )
        ]
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI API"""
        # Mock implementation - in real scenario, use openai library
        start_time = time.time()
        
        # Simulate API call
        await asyncio.sleep(0.1)
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        return LLMResponse(
            content="This is a mock response from OpenAI API",
            model=request.model,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            finish_reason="stop",
            response_time_ms=response_time_ms
        )
    
    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        chunks = ["This ", "is ", "a ", "mock ", "streaming ", "response"]
        for chunk in chunks:
            await asyncio.sleep(0.05)  # Simulate streaming delay
            yield chunk


class AnthropicProvider(BaseLLMProvider):
    """Anthropic provider implementation"""
    
    @property
    def provider_name(self) -> ModelProvider:
        return ModelProvider.ANTHROPIC
    
    @property
    def supported_models(self) -> List[ModelConfig]:
        return [
            ModelConfig(
                provider=ModelProvider.ANTHROPIC,
                model_id="claude-3-haiku-20240307",
                display_name="Claude 3 Haiku",
                context_window=200000,
                supports_functions=False,
                cost_per_1k_tokens=0.00025
            ),
            ModelConfig(
                provider=ModelProvider.ANTHROPIC,
                model_id="claude-3-sonnet-20240229",
                display_name="Claude 3 Sonnet",
                context_window=200000,
                supports_functions=False,
                cost_per_1k_tokens=0.003
            ),
            ModelConfig(
                provider=ModelProvider.ANTHROPIC,
                model_id="claude-3-opus-20240229",
                display_name="Claude 3 Opus",
                context_window=200000,
                supports_functions=False,
                cost_per_1k_tokens=0.015
            )
        ]
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Anthropic API"""
        # Mock implementation
        start_time = time.time()
        await asyncio.sleep(0.1)
        response_time_ms = int((time.time() - start_time) * 1000)
        
        return LLMResponse(
            content="This is a mock response from Anthropic API",
            model=request.model,
            usage={"prompt_tokens": 12, "completion_tokens": 18, "total_tokens": 30},
            finish_reason="end_turn",
            response_time_ms=response_time_ms
        )
    
    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        chunks = ["Mock ", "Anthropic ", "streaming ", "response"]
        for chunk in chunks:
            await asyncio.sleep(0.05)
            yield chunk


class LLMRouter:
    """Router for managing multiple LLM providers and models"""
    
    def __init__(self):
        self.providers: Dict[ModelProvider, BaseLLMProvider] = {}
        self._load_providers()
    
    def _load_providers(self):
        """Load and initialize providers"""
        # Initialize OpenAI provider
        try:
            openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
            self.providers[ModelProvider.OPENAI] = OpenAIProvider(api_key=openai_api_key)
        except Exception as e:
            logger.warning(f"Failed to load OpenAI provider: {e}")
        
        # Initialize Anthropic provider
        try:
            anthropic_api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
            self.providers[ModelProvider.ANTHROPIC] = AnthropicProvider(api_key=anthropic_api_key)
        except Exception as e:
            logger.warning(f"Failed to load Anthropic provider: {e}")
    
    def get_available_models(self) -> List[ModelConfig]:
        """Get all available models from all providers"""
        models = []
        for provider in self.providers.values():
            models.extend(provider.supported_models)
        return models
    
    def get_model_config(self, model_id: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model"""
        for provider in self.providers.values():
            config = provider.get_model_config(model_id)
            if config:
                return config
        return None
    
    def get_provider_for_model(self, model_id: str) -> Optional[BaseLLMProvider]:
        """Get provider that supports the given model"""
        for provider in self.providers.values():
            if provider.get_model_config(model_id):
                return provider
        return None
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using appropriate provider"""
        provider = self.get_provider_for_model(request.model)
        if not provider:
            raise ValueError(f"No provider found for model: {request.model}")
        
        try:
            return await provider.generate(request)
        except Exception as e:
            logger.exception(f"Failed to generate response with {request.model}")
            # Fallback to default model if available
            default_model = getattr(settings, 'EASYVIZ_SETTINGS', {}).get('DEFAULT_LLM_MODEL', 'gpt-3.5-turbo')
            if request.model != default_model:
                logger.info(f"Falling back to default model: {default_model}")
                request.model = default_model
                return await self.generate(request)
            raise e
    
    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response using appropriate provider"""
        provider = self.get_provider_for_model(request.model)
        if not provider:
            raise ValueError(f"No provider found for model: {request.model}")
        
        async for chunk in provider.generate_stream(request):
            yield chunk
    
    def validate_request(self, request: LLMRequest) -> bool:
        """Validate request parameters"""
        model_config = self.get_model_config(request.model)
        if not model_config:
            return False
        
        # Validate temperature
        min_temp, max_temp = model_config.temperature_range
        if not (min_temp <= request.temperature <= max_temp):
            return False
        
        # Validate max_tokens
        if request.max_tokens > model_config.context_window:
            return False
        
        # Validate tools support
        if request.tools and not model_config.supports_functions:
            return False
        
        return True
    
    def get_model_suggestions(self, requirements: Dict[str, Any]) -> List[ModelConfig]:
        """Get model suggestions based on requirements"""
        available_models = self.get_available_models()
        suggestions = []
        
        for model in available_models:
            score = 0
            
            # Score based on requirements
            if requirements.get('needs_functions') and model.supports_functions:
                score += 10
            
            if requirements.get('needs_large_context') and model.context_window > 32000:
                score += 10
            
            if requirements.get('budget_conscious') and model.cost_per_1k_tokens < 0.002:
                score += 5
            
            if score > 0:
                suggestions.append(model)
        
        # Sort by score (would need to add score to model or create separate scoring)
        return suggestions


# Global router instance
llm_router = LLMRouter()


class LLMService:
    """High-level service for LLM operations"""
    
    def __init__(self, router: LLMRouter = None):
        self.router = router or llm_router
    
    async def chat_completion(self, session_id: str, messages: List[Dict[str, str]], 
                            model: str = None, **kwargs) -> LLMResponse:
        """Generate chat completion"""
        if not model:
            model = getattr(settings, 'EASYVIZ_SETTINGS', {}).get('DEFAULT_LLM_MODEL', 'gpt-3.5-turbo')
        
        # Convert messages to ChatMessage objects
        chat_messages = [ChatMessage(role=msg['role'], content=msg['content']) for msg in messages]
        
        request = LLMRequest(
            messages=chat_messages,
            model=model,
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1000),
            stream=kwargs.get('stream', False),
            tools=kwargs.get('tools'),
            system_prompt=kwargs.get('system_prompt', '')
        )
        
        if not self.router.validate_request(request):
            raise ValueError("Invalid request parameters")
        
        return await self.router.generate(request)
    
    async def chat_completion_stream(self, session_id: str, messages: List[Dict[str, str]], 
                                   model: str = None, **kwargs) -> AsyncGenerator[str, None]:
        """Generate streaming chat completion"""
        if not model:
            model = getattr(settings, 'EASYVIZ_SETTINGS', {}).get('DEFAULT_LLM_MODEL', 'gpt-3.5-turbo')
        
        chat_messages = [ChatMessage(role=msg['role'], content=msg['content']) for msg in messages]
        
        request = LLMRequest(
            messages=chat_messages,
            model=model,
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1000),
            stream=True,
            tools=kwargs.get('tools'),
            system_prompt=kwargs.get('system_prompt', '')
        )
        
        if not self.router.validate_request(request):
            raise ValueError("Invalid request parameters")
        
        async for chunk in self.router.generate_stream(request):
            yield chunk
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available models as dictionaries"""
        return [model.to_dict() for model in self.router.get_available_models()]