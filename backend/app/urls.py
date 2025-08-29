"""
URL configuration for YYC³ EasyVizAI project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/chat/', include('app.services.chat.urls')),
    path('api/v1/tools/', include('app.services.tools.urls')),
    path('api/v1/llm/', include('app.services.llm_router.urls')),
]