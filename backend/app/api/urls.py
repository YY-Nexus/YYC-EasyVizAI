"""
API URLs for YYC EasyVizAI
"""
from django.urls import path, include

urlpatterns = [
    path('llm/', include('app.llm.urls')),
    path('chat/', include('app.api.chat_urls')),
]