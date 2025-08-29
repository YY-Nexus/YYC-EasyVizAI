"""
LLM Router API URL configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('models/', views.list_models, name='list_models'),
    path('models/<str:model_id>/', views.get_model_info, name='get_model_info'),
    path('models/suggestions/', views.get_model_suggestions, name='get_model_suggestions'),
    path('models/test/', views.test_model, name='test_model'),
    path('providers/', views.get_providers, name='get_providers'),
]