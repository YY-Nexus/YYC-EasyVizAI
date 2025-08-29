"""
LLM Router API views and endpoints
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import asyncio

from .router import llm_router, LLMService

llm_service = LLMService()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_models(request):
    """List available LLM models"""
    try:
        models = llm_router.get_available_models()
        
        return Response({
            'models': [model.to_dict() for model in models]
        })
    except Exception as e:
        return Response({
            'error': f'Failed to list models: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_model_info(request, model_id):
    """Get information about a specific model"""
    try:
        model_config = llm_router.get_model_config(model_id)
        if not model_config:
            return Response({
                'error': 'Model not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(model_config.to_dict())
    except Exception as e:
        return Response({
            'error': f'Failed to get model info: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_model_suggestions(request):
    """Get model suggestions based on requirements"""
    data = request.data
    requirements = {
        'needs_functions': data.get('needs_functions', False),
        'needs_large_context': data.get('needs_large_context', False),
        'budget_conscious': data.get('budget_conscious', False)
    }
    
    try:
        suggestions = llm_router.get_model_suggestions(requirements)
        
        return Response({
            'suggestions': [model.to_dict() for model in suggestions],
            'requirements': requirements
        })
    except Exception as e:
        return Response({
            'error': f'Failed to get model suggestions: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_model(request):
    """Test a model with a simple message"""
    data = request.data
    model = data.get('model')
    test_message = data.get('message', 'Hello, this is a test message.')
    
    if not model:
        return Response({
            'error': 'Model is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    async def _test_model():
        try:
            response = await llm_service.chat_completion(
                session_id='test',
                messages=[{'role': 'user', 'content': test_message}],
                model=model,
                max_tokens=100
            )
            return {
                'success': True,
                'response': response.to_dict()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    try:
        result = asyncio.run(_test_model())
        return Response(result)
    except Exception as e:
        return Response({
            'error': f'Model test failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_providers(request):
    """Get available LLM providers"""
    try:
        providers = {}
        for provider_name, provider in llm_router.providers.items():
            providers[provider_name.value] = {
                'name': provider_name.value,
                'models': [model.to_dict() for model in provider.supported_models]
            }
        
        return Response({
            'providers': providers
        })
    except Exception as e:
        return Response({
            'error': f'Failed to get providers: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)