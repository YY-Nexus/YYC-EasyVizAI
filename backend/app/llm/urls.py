"""
LLM API URLs
"""
from django.urls import path
from . import views

urlpatterns = [
    path('models/', views.ModelListView.as_view(), name='model-list'),
    path('models/<str:model_key>/', views.ModelDetailView.as_view(), name='model-detail'),
    path('models/<str:model_key>/load/', views.LoadModelView.as_view(), name='model-load'),
    path('models/<str:model_key>/unload/', views.UnloadModelView.as_view(), name='model-unload'),
    path('generate/', views.GenerateView.as_view(), name='generate'),
    path('generate/stream/', views.StreamGenerateView.as_view(), name='generate-stream'),
    path('health/', views.HealthCheckView.as_view(), name='health'),
]