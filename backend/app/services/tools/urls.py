"""
Tools API URL configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_tools, name='list_tools'),
    path('schemas/', views.get_tool_schemas, name='get_tool_schemas'),
    path('execute/', views.execute_tool, name='execute_tool'),
    path('<str:tool_name>/', views.get_tool_info, name='get_tool_info'),
]