from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class ChatSession(models.Model):
    """聊天会话"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Session {self.id}: {self.title or 'Untitled'}"


class ChatMessage(models.Model):
    """聊天消息"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    tokens = models.IntegerField(default=0)
    emotion_snapshot = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class SemanticIndex(models.Model):
    """语义索引"""
    content_type = models.CharField(max_length=50)  # 'chat', 'document', 'code'
    content_id = models.CharField(max_length=100)   # Reference to original content
    content_text = models.TextField()               # The actual text content
    embedding = models.JSONField()                  # Vector embedding as JSON array
    metadata = models.JSONField(default=dict)       # Additional metadata
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'content_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.content_type}:{self.content_id}"


class LearningNode(models.Model):
    """学习节点"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    prerequisites = models.JSONField(default=list)  # List of prerequisite node IDs
    difficulty = models.IntegerField(default=1)     # 1-5 scale
    tags = models.JSONField(default=list)           # Topic tags
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class LearningProgress(models.Model):
    """学习进度"""
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    node = models.ForeignKey(LearningNode, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress_data = models.JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'node']

    def __str__(self):
        return f"{self.user.username} - {self.node.title}: {self.status}"


class LearningReport(models.Model):
    """学习报告"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField()
    knowledge_points = models.JSONField(default=list)
    date_from = models.DateField()
    date_to = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.date_from} - {self.date_to})"


class KnowledgePoint(models.Model):
    """知识点"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=100)
    importance = models.IntegerField(default=1)  # 1-5 scale
    source_type = models.CharField(max_length=50)  # 'chat', 'document', 'code'
    source_id = models.CharField(max_length=100)
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['importance']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title