"""
URL configuration for YYC³ EasyVizAI project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('app.core.urls')),
]