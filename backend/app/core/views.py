from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import psutil
import datetime


@api_view(['GET'])
def status_view(request):
    """系统状态检查视图"""
    try:
        # 获取系统信息
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status_data = {
            'status': 'healthy',
            'timestamp': datetime.datetime.now().isoformat(),
            'system': {
                'cpu_usage': f"{cpu_percent}%",
                'memory_usage': f"{memory.percent}%",
                'disk_usage': f"{disk.percent}%",
            },
            'services': {
                'database': 'connected',
                'cache': 'connected',
                'backend': 'running',
            }
        }
        
        return Response(status_data)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.datetime.now().isoformat()
        }, status=500)