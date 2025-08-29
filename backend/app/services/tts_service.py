"""
Text-to-Speech (TTS) Service
Provides text to audio conversion with multiple voice options and emotional context awareness.
"""
import os
import tempfile
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# TTS Libraries
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class TTSService:
    """
    Text-to-Speech service with multi-provider support
    """
    
    SUPPORTED_EMOTIONS = {
        'neutral': {'speed': 1.0, 'pitch': 1.0},
        'happy': {'speed': 1.1, 'pitch': 1.2},
        'sad': {'speed': 0.8, 'pitch': 0.9},
        'excited': {'speed': 1.3, 'pitch': 1.3},
        'calm': {'speed': 0.9, 'pitch': 0.95},
        'urgent': {'speed': 1.4, 'pitch': 1.1},
    }
    
    VOICE_MAPPING = {
        'zh-CN': {
            'female': 'zh-CN-XiaoxiaoNeural',
            'male': 'zh-CN-YunxiNeural',
            'child': 'zh-CN-XiaoyiNeural',
        },
        'en-US': {
            'female': 'en-US-AriaNeural',
            'male': 'en-US-GuyNeural',
            'child': 'en-US-JennyNeural',
        }
    }
    
    def __init__(self):
        self.config = getattr(settings, 'TTS_CONFIG', {})
        self.default_language = self.config.get('DEFAULT_LANGUAGE', 'zh-CN')
        self.audio_format = self.config.get('AUDIO_FORMAT', 'mp3')
        self.cache_dir = Path(settings.MEDIA_ROOT) / 'tts_cache'
        self.cache_dir.mkdir(exist_ok=True)
    
    def generate_cache_key(self, text: str, language: str, voice: str, emotion: str) -> str:
        """Generate cache key for TTS audio"""
        content = f"{text}_{language}_{voice}_{emotion}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_audio(self, cache_key: str) -> Optional[str]:
        """Get cached audio file URL if exists"""
        cache_path = self.cache_dir / f"{cache_key}.{self.audio_format}"
        if cache_path.exists():
            return f"/media/tts_cache/{cache_key}.{self.audio_format}"
        return None
    
    async def text_to_speech(
        self,
        text: str,
        language: Optional[str] = None,
        voice_type: Optional[str] = None,
        emotion: str = 'neutral',
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Convert text to speech audio
        
        Args:
            text: Text to convert
            language: Language code (zh-CN, en-US)
            voice_type: Voice type (female, male, child)
            emotion: Emotional tone
            use_cache: Whether to use cached audio
            
        Returns:
            Dict containing audio URL, duration, and metadata
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Set defaults
        language = language or self.default_language
        voice_type = voice_type or 'female'
        
        # Get voice name
        voice_name = self.VOICE_MAPPING.get(language, {}).get(voice_type)
        if not voice_name:
            raise ValueError(f"Unsupported language/voice: {language}/{voice_type}")
        
        # Generate cache key
        cache_key = self.generate_cache_key(text, language, voice_name, emotion)
        
        # Check cache
        if use_cache:
            cached_url = self.get_cached_audio(cache_key)
            if cached_url:
                logger.info(f"Using cached TTS audio: {cache_key}")
                return {
                    'audio_url': cached_url,
                    'cache_key': cache_key,
                    'cached': True,
                    'language': language,
                    'voice_type': voice_type,
                    'emotion': emotion
                }
        
        # Generate new audio
        try:
            audio_data = await self._generate_audio(text, language, voice_name, emotion)
            
            # Save to cache
            cache_path = self.cache_dir / f"{cache_key}.{self.audio_format}"
            with open(cache_path, 'wb') as f:
                f.write(audio_data)
            
            audio_url = f"/media/tts_cache/{cache_key}.{self.audio_format}"
            
            logger.info(f"Generated new TTS audio: {cache_key}")
            return {
                'audio_url': audio_url,
                'cache_key': cache_key,
                'cached': False,
                'language': language,
                'voice_type': voice_type,
                'emotion': emotion
            }
            
        except Exception as e:
            logger.error(f"TTS generation failed: {str(e)}")
            raise
    
    async def _generate_audio(self, text: str, language: str, voice_name: str, emotion: str) -> bytes:
        """Generate audio using available TTS provider"""
        
        # Try Edge TTS first (better quality)
        if EDGE_TTS_AVAILABLE:
            try:
                return await self._generate_with_edge_tts(text, voice_name, emotion)
            except Exception as e:
                logger.warning(f"Edge TTS failed, falling back to Google TTS: {str(e)}")
        
        # Fallback to Google TTS
        if GTTS_AVAILABLE:
            try:
                return await self._generate_with_gtts(text, language)
            except Exception as e:
                logger.warning(f"Google TTS failed, using demo audio: {str(e)}")
        
        # Final fallback: create a demo audio file
        return await self._generate_demo_audio(text)
    
    async def _generate_with_edge_tts(self, text: str, voice_name: str, emotion: str) -> bytes:
        """Generate audio using Edge TTS"""
        try:
            # Get emotion parameters
            emotion_params = self.SUPPORTED_EMOTIONS.get(emotion, self.SUPPORTED_EMOTIONS['neutral'])
            
            # Create SSML with emotion parameters
            ssml_text = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
                <voice name="{voice_name}">
                    <prosody rate="{emotion_params['speed']}" pitch="{emotion_params['pitch']}">
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            # Generate audio
            communicate = edge_tts.Communicate(ssml_text, voice_name)
            audio_data = b""
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Edge TTS generation failed: {str(e)}")
            raise
    
    async def _generate_with_gtts(self, text: str, language: str) -> bytes:
        """Generate audio using Google TTS (fallback)"""
        try:
            tts = gTTS(text=text, lang=language.split('-')[0], slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                
                # Read audio data
                with open(tmp_file.name, 'rb') as f:
                    audio_data = f.read()
                
                # Clean up
                os.unlink(tmp_file.name)
                
                return audio_data
                
        except Exception as e:
            logger.error(f"Google TTS generation failed: {str(e)}")
            raise
    
    async def _generate_demo_audio(self, text: str) -> bytes:
        """Generate demo audio file for development/testing"""
        try:
            import io
            import wave
            import struct
            import math
            
            # Generate a simple sine wave tone as demo audio
            sample_rate = 22050
            duration = min(len(text) * 0.1 + 1.0, 5.0)  # Based on text length, max 5 seconds
            frames = int(duration * sample_rate)
            
            # Create audio data
            audio_data = []
            for i in range(frames):
                # Generate a simple tone pattern
                t = i / sample_rate
                frequency = 200 + (i % 1000) * 0.5  # Varying frequency
                value = int(16384 * math.sin(2 * math.pi * frequency * t))
                audio_data.append(struct.pack('<h', value))
            
            # Create WAV file in memory
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes per sample
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(b''.join(audio_data))
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Demo audio generation failed: {str(e)}")
            # Return minimal WAV file
            return b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"V\x00\x00D\xac\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'

    def get_available_voices(self) -> Dict[str, List[str]]:
        """Get list of available voices by language"""
        return {
            lang: list(voices.keys()) 
            for lang, voices in self.VOICE_MAPPING.items()
        }
    
    def get_supported_emotions(self) -> List[str]:
        """Get list of supported emotions"""
        return list(self.SUPPORTED_EMOTIONS.keys())


# Global TTS service instance
tts_service = TTSService()