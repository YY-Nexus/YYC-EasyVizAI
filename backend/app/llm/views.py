"""
LLM API Views
"""
import asyncio
import json
import logging
from typing import Dict, Any

from django.http import HttpResponse, StreamingHttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .gateway import get_llm_gateway
from .serializers import GenerateRequestSerializer

logger = logging.getLogger(__name__)

class ModelListView(APIView):
    """List available and loaded models"""
    permission_classes = [AllowAny]  # For demo - add proper auth in production
    
    def get(self, request):
        try:
            gateway = get_llm_gateway()
            model_info = gateway.get_model_info()
            return Response(model_info, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting model list: {str(e)}")
            return Response(
                {'error': 'Failed to get model information'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ModelDetailView(APIView):
    """Get details about a specific model"""
    permission_classes = [AllowAny]
    
    def get(self, request, model_key):
        try:
            gateway = get_llm_gateway()
            model_info = gateway.get_model_info(model_key)
            return Response(model_info, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting model details for {model_key}: {str(e)}")
            return Response(
                {'error': f'Failed to get model details for {model_key}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoadModelView(APIView):
    """Load a specific model"""
    permission_classes = [AllowAny]
    
    def post(self, request, model_key):
        try:
            gateway = get_llm_gateway()
            
            # Run async function in sync context
            import asyncio
            success = asyncio.run(gateway.load_model(model_key))
            
            if success:
                return Response(
                    {'message': f'Model {model_key} loaded successfully'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': f'Failed to load model {model_key}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Error loading model {model_key}: {str(e)}")
            return Response(
                {'error': f'Failed to load model {model_key}: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UnloadModelView(APIView):
    """Unload a specific model"""
    permission_classes = [AllowAny]
    
    def post(self, request, model_key):
        try:
            gateway = get_llm_gateway()
            
            # Run async function in sync context
            import asyncio
            success = asyncio.run(gateway.unload_model(model_key))
            
            if success:
                return Response(
                    {'message': f'Model {model_key} unloaded successfully'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': f'Model {model_key} was not loaded'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Error unloading model {model_key}: {str(e)}")
            return Response(
                {'error': f'Failed to unload model {model_key}: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GenerateView(APIView):
    """Generate text response (non-streaming)"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = GenerateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            data = serializer.validated_data
            gateway = get_llm_gateway()
            
            # Run async function in sync context
            import asyncio
            
            async def _generate():
                response_text = ""
                async for chunk in gateway.generate_response(
                    prompt=data['prompt'],
                    model_key=data.get('model'),
                    stream=False,
                    **data.get('parameters', {})
                ):
                    response_text += chunk
                return response_text
            
            response_text = asyncio.run(_generate())
            
            return Response({
                'response': response_text.strip(),
                'model': data.get('model') or gateway.current_model,
                'prompt': data['prompt']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return Response(
                {'error': f'Failed to generate response: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StreamGenerateView(APIView):
    """Generate text response (streaming)"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = GenerateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            data = serializer.validated_data
            gateway = get_llm_gateway()
            
            import asyncio
            
            def generate_stream():
                try:
                    async def _async_generate():
                        async for chunk in gateway.generate_response(
                            prompt=data['prompt'],
                            model_key=data.get('model'),
                            stream=True,
                            **data.get('parameters', {})
                        ):
                            yield f"data: {json.dumps({'chunk': chunk})}\\n\\n"
                        yield f"data: {json.dumps({'done': True})}\\n\\n"
                    
                    # Run async generator in sync context
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    async_gen = _async_generate()
                    try:
                        while True:
                            chunk = loop.run_until_complete(async_gen.__anext__())
                            yield chunk
                    except StopAsyncIteration:
                        pass
                    finally:
                        loop.close()
                        
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\\n\\n"
            
            response = StreamingHttpResponse(
                generate_stream(),
                content_type='text/event-stream'
            )
            response['Cache-Control'] = 'no-cache'
            response['Connection'] = 'keep-alive'
            return response
            
        except Exception as e:
            logger.error(f"Error in streaming generation: {str(e)}")
            return Response(
                {'error': f'Failed to start streaming generation: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class HealthCheckView(APIView):
    """Health check endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            gateway = get_llm_gateway()
            model_info = gateway.get_model_info()
            
            return Response({
                'status': 'healthy',
                'device': model_info['device'],
                'loaded_models': model_info['loaded_models'],
                'current_model': model_info['current_model']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return Response(
                {'status': 'unhealthy', 'error': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )