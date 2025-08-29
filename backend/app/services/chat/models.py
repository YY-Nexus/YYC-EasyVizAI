"""
Chat session and message models for persistence
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import uuid
import json


class ChatSession(models.Model):
    """Chat session model for conversation persistence"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Session metadata
    model_config = models.JSONField(default=dict, help_text="LLM model configuration")
    context_window = models.IntegerField(default=4000, help_text="Context window size")
    system_prompt = models.TextField(blank=True, help_text="System prompt for the session")
    
    # Status and retention
    is_active = models.BooleanField(default=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    retention_days = models.IntegerField(default=90)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"ChatSession {self.id} - {self.title or 'Untitled'}"
    
    @property
    def message_count(self):
        """Get total message count in session"""
        return self.messages.count()
    
    @property
    def total_tokens(self):
        """Get total tokens used in session"""
        return self.messages.aggregate(
            total=models.Sum('tokens')
        )['total'] or 0
    
    def get_messages_for_context(self, limit=None):
        """Get messages suitable for LLM context"""
        messages = self.messages.filter(
            role__in=['user', 'assistant', 'system']
        ).order_by('created_at')
        
        if limit:
            messages = messages[:limit]
            
        return messages
    
    def archive(self):
        """Archive the session"""
        self.is_active = False
        self.archived_at = timezone.now()
        self.save()


class ChatMessage(models.Model):
    """Individual message in a chat session"""
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
        ('tool', 'Tool'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    
    # Token usage and metadata
    tokens = models.IntegerField(default=0, help_text="Token count for this message")
    model_used = models.CharField(max_length=100, blank=True, help_text="LLM model used for generation")
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    generation_time_ms = models.IntegerField(null=True, blank=True, help_text="Generation time in milliseconds")
    
    # Tool calling and emotion
    tool_calls = models.JSONField(default=list, help_text="Tool calls made in this message")
    emotion_snapshot = models.CharField(max_length=50, blank=True, help_text="Emotion detected in message")
    
    # Metadata
    metadata = models.JSONField(default=dict, help_text="Additional message metadata")
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['role', 'created_at']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.role}: {content_preview}"
    
    def to_llm_format(self):
        """Convert to format suitable for LLM API"""
        message = {
            'role': self.role,
            'content': self.content
        }
        
        if self.tool_calls:
            message['tool_calls'] = self.tool_calls
            
        return message


class SessionRetentionPolicy(models.Model):
    """User-specific retention policies for chat sessions"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chat_retention_policy')
    default_retention_days = models.IntegerField(default=90)
    auto_archive_enabled = models.BooleanField(default=True)
    permanent_sessions_enabled = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Retention policy for {self.user.username}"