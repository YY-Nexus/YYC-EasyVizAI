"""
TTS API Views
Provides REST API endpoints for text-to-speech functionality
"""
import asyncio
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .tts_service import tts_service

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TTSGenerateView(APIView):
    """
    Generate TTS audio from text
    """
    
    def post(self, request):
        """
        Generate speech audio from text
        
        POST /api/tts/generate/
        {
            "text": "要转换的文本",
            "language": "zh-CN",  // optional, default: zh-CN
            "voice_type": "female",  // optional: female, male, child
            "emotion": "neutral",  // optional: neutral, happy, sad, excited, calm, urgent
            "use_cache": true  // optional: whether to use cached audio
        }
        """
        try:
            data = request.data
            text = data.get('text', '').strip()
            
            if not text:
                return Response({
                    'error': 'Text is required',
                    'code': 'MISSING_TEXT'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get parameters
            language = data.get('language', 'zh-CN')
            voice_type = data.get('voice_type', 'female')
            emotion = data.get('emotion', 'neutral')
            use_cache = data.get('use_cache', True)
            
            # Validate emotion
            if emotion not in tts_service.get_supported_emotions():
                return Response({
                    'error': f'Unsupported emotion: {emotion}',
                    'supported_emotions': tts_service.get_supported_emotions(),
                    'code': 'INVALID_EMOTION'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate TTS (run async function in sync context)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    tts_service.text_to_speech(
                        text=text,
                        language=language,
                        voice_type=voice_type,
                        emotion=emotion,
                        use_cache=use_cache
                    )
                )
            finally:
                loop.close()
            
            return Response({
                'success': True,
                'data': result,
                'message': 'TTS audio generated successfully'
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'error': str(e),
                'code': 'VALIDATION_ERROR'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"TTS generation error: {str(e)}")
            return Response({
                'error': 'Failed to generate TTS audio',
                'code': 'GENERATION_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TTSVoicesView(APIView):
    """
    Get available TTS voices
    """
    
    def get(self, request):
        """
        Get list of available voices
        
        GET /api/tts/voices/
        """
        try:
            voices = tts_service.get_available_voices()
            emotions = tts_service.get_supported_emotions()
            
            return Response({
                'success': True,
                'data': {
                    'voices': voices,
                    'emotions': emotions,
                    'default_language': tts_service.default_language
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting TTS voices: {str(e)}")
            return Response({
                'error': 'Failed to get voice information',
                'code': 'VOICES_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TTSPreviewView(APIView):
    """
    Generate TTS preview for testing voices
    """
    
    def post(self, request):
        """
        Generate preview audio with sample text
        
        POST /api/tts/preview/
        {
            "language": "zh-CN",
            "voice_type": "female",
            "emotion": "happy"
        }
        """
        try:
            data = request.data
            language = data.get('language', 'zh-CN')
            voice_type = data.get('voice_type', 'female')
            emotion = data.get('emotion', 'neutral')
            
            # Sample texts for different languages
            sample_texts = {
                'zh-CN': '您好，我是EasyVizAI智能助手，很高兴为您服务！',
                'en-US': 'Hello, I am EasyVizAI intelligent assistant, nice to serve you!'
            }
            
            sample_text = sample_texts.get(language, sample_texts['zh-CN'])
            
            # Generate preview
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    tts_service.text_to_speech(
                        text=sample_text,
                        language=language,
                        voice_type=voice_type,
                        emotion=emotion,
                        use_cache=True
                    )
                )
            finally:
                loop.close()
            
            return Response({
                'success': True,
                'data': {
                    **result,
                    'sample_text': sample_text
                },
                'message': 'Preview generated successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"TTS preview error: {str(e)}")
            return Response({
                'error': 'Failed to generate preview',
                'code': 'PREVIEW_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)