from django.db import models


class HealthCheck(models.Model):
    """健康检查记录模型"""
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='healthy')
    details = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"Health Check - {self.status} at {self.timestamp}"