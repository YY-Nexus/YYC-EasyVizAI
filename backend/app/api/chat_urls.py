"""
Chat API URLs - placeholder for chat functionality
"""
from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ChatSessionView(APIView):
    """Basic chat session endpoint"""
    
    def post(self, request):
        return Response({
            'message': 'Chat session created - use WebSocket for real-time chat',
            'websocket_url': '/ws/chat/<session_id>/',
            'session_id': 'demo_session'
        }, status=status.HTTP_201_CREATED)

urlpatterns = [
    path('session/', ChatSessionView.as_view(), name='chat-session'),
]