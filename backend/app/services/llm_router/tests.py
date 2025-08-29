"""
Tests for LLM Router and multi-model support
"""
from django.test import TestCase
import asyncio
from .router import (
    LLMRouter, LLMService, ModelProvider, ModelConfig, 
    LLMRequest, ChatMessage, OpenAIProvider, AnthropicProvider
)


class LLMRouterTestCase(TestCase):
    def setUp(self):
        self.router = LLMRouter()
        self.service = LLMService(self.router)
    
    def test_available_models(self):
        """Test getting available models"""
        models = self.router.get_available_models()
        self.assertGreater(len(models), 0)
        
        # Check that we have models from different providers
        providers = set(model.provider for model in models)
        self.assertIn(ModelProvider.OPENAI, providers)
        self.assertIn(ModelProvider.ANTHROPIC, providers)
    
    def test_model_config_retrieval(self):
        """Test getting model configuration"""
        config = self.router.get_model_config('gpt-3.5-turbo')
        self.assertIsNotNone(config)
        self.assertEqual(config.model_id, 'gpt-3.5-turbo')
        self.assertEqual(config.provider, ModelProvider.OPENAI)
        self.assertTrue(config.supports_functions)
    
    def test_provider_for_model(self):
        """Test getting provider for a model"""
        provider = self.router.get_provider_for_model('gpt-4')
        self.assertIsNotNone(provider)
        self.assertEqual(provider.provider_name, ModelProvider.OPENAI)
        
        provider = self.router.get_provider_for_model('claude-3-sonnet-20240229')
        self.assertIsNotNone(provider)
        self.assertEqual(provider.provider_name, ModelProvider.ANTHROPIC)
    
    def test_request_validation(self):
        """Test LLM request validation"""
        # Valid request
        request = LLMRequest(
            messages=[ChatMessage(role='user', content='Hello')],
            model='gpt-3.5-turbo',
            temperature=0.7
        )
        self.assertTrue(self.router.validate_request(request))
        
        # Invalid temperature
        request.temperature = 5.0
        self.assertFalse(self.router.validate_request(request))
        
        # Invalid model
        request.temperature = 0.7
        request.model = 'invalid-model'
        self.assertFalse(self.router.validate_request(request))
    
    def test_model_suggestions(self):
        """Test model suggestions based on requirements"""
        # Test function calling requirement
        suggestions = self.router.get_model_suggestions({
            'needs_functions': True
        })
        self.assertGreater(len(suggestions), 0)
        for model in suggestions:
            if model.provider == ModelProvider.OPENAI:
                self.assertTrue(model.supports_functions)
        
        # Test large context requirement
        suggestions = self.router.get_model_suggestions({
            'needs_large_context': True
        })
        self.assertGreater(len(suggestions), 0)
        for model in suggestions:
            if model.context_window > 32000:
                # Found at least one large context model
                break
        else:
            self.fail("No large context models found in suggestions")


class LLMServiceTestCase(TestCase):
    def setUp(self):
        self.service = LLMService()
    
    def test_chat_completion(self):
        """Test chat completion"""
        async def run_test():
            response = await self.service.chat_completion(
                session_id='test',
                messages=[{'role': 'user', 'content': 'Hello'}],
                model='gpt-3.5-turbo'
            )
            return response
        
        response = asyncio.run(run_test())
        
        self.assertIsNotNone(response.content)
        self.assertEqual(response.model, 'gpt-3.5-turbo')
        self.assertIn('total_tokens', response.usage)
    
    def test_chat_completion_stream(self):
        """Test streaming chat completion"""
        async def run_test():
            chunks = []
            async for chunk in self.service.chat_completion_stream(
                session_id='test',
                messages=[{'role': 'user', 'content': 'Hello'}],
                model='gpt-3.5-turbo'
            ):
                chunks.append(chunk)
            return chunks
        
        chunks = asyncio.run(run_test())
        
        self.assertGreater(len(chunks), 0)
        # All chunks should be strings
        for chunk in chunks:
            self.assertIsInstance(chunk, str)
    
    def test_available_models_service(self):
        """Test getting available models through service"""
        models = self.service.get_available_models()
        self.assertGreater(len(models), 0)
        
        # Check that models are dictionaries
        for model in models:
            self.assertIsInstance(model, dict)
            self.assertIn('model_id', model)
            self.assertIn('provider', model)
            self.assertIn('display_name', model)


class OpenAIProviderTestCase(TestCase):
    def setUp(self):
        self.provider = OpenAIProvider()
    
    def test_supported_models(self):
        """Test OpenAI supported models"""
        models = self.provider.supported_models
        self.assertGreater(len(models), 0)
        
        # Check for expected models
        model_ids = [model.model_id for model in models]
        self.assertIn('gpt-3.5-turbo', model_ids)
        self.assertIn('gpt-4', model_ids)
    
    def test_model_config_retrieval(self):
        """Test getting model config"""
        config = self.provider.get_model_config('gpt-3.5-turbo')
        self.assertIsNotNone(config)
        self.assertEqual(config.model_id, 'gpt-3.5-turbo')
        self.assertTrue(config.supports_functions)
    
    def test_mock_generation(self):
        """Test mock response generation"""
        async def run_test():
            request = LLMRequest(
                messages=[ChatMessage(role='user', content='Hello')],
                model='gpt-3.5-turbo'
            )
            response = await self.provider.generate(request)
            return response
        
        response = asyncio.run(run_test())
        
        self.assertIsNotNone(response.content)
        self.assertEqual(response.model, 'gpt-3.5-turbo')
        self.assertGreater(response.response_time_ms, 0)


class AnthropicProviderTestCase(TestCase):
    def setUp(self):
        self.provider = AnthropicProvider()
    
    def test_supported_models(self):
        """Test Anthropic supported models"""
        models = self.provider.supported_models
        self.assertGreater(len(models), 0)
        
        # Check for expected models
        model_ids = [model.model_id for model in models]
        self.assertIn('claude-3-haiku-20240307', model_ids)
        self.assertIn('claude-3-sonnet-20240229', model_ids)
    
    def test_large_context_windows(self):
        """Test that Anthropic models have large context windows"""
        models = self.provider.supported_models
        for model in models:
            self.assertGreaterEqual(model.context_window, 200000)