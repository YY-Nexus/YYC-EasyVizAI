"""
Core app URL configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.core.views import SearchViewSet, LearningLoopViewSet

router = DefaultRouter()
router.register(r'search', SearchViewSet, basename='search')
router.register(r'learning', LearningLoopViewSet, basename='learning')

urlpatterns = [
    path('', include(router.urls)),
]