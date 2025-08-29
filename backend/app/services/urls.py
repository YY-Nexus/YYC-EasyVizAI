"""
URL Configuration for Services
"""
from django.urls import path, include
from .tts_views import TTSGenerateView, TTSVoicesView, TTSPreviewView

# TTS URLs
tts_urlpatterns = [
    path('generate/', TTSGenerateView.as_view(), name='tts-generate'),
    path('voices/', TTSVoicesView.as_view(), name='tts-voices'),
    path('preview/', TTSPreviewView.as_view(), name='tts-preview'),
]

urlpatterns = [
    path('tts/', include(tts_urlpatterns)),
]