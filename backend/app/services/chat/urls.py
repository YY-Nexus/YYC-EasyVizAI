"""
Chat API URL configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('session/', views.create_session, name='create_session'),
    path('session/<str:session_id>/', views.get_session, name='get_session'),
    path('sessions/', views.list_sessions, name='list_sessions'),
    path('session/<str:session_id>/message/', views.send_message, name='send_message'),
    path('session/<str:session_id>/history/', views.get_history, name='get_history'),
    path('session/<str:session_id>/tool-call/', views.tool_call, name='tool_call'),
    path('session/<str:session_id>/', views.delete_session, name='delete_session'),
]