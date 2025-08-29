"""
Celery tasks for learning loop automation
"""
from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import logging

from app.core.learning_loop import learning_loop_service

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def daily_learning_loop_task(self):
    """每日学习闭环任务"""
    try:
        logger.info("Starting daily learning loop task")
        
        # 运行学习闭环
        results = learning_loop_service.run_daily_loop()
        
        logger.info(f"Daily learning loop completed: {results}")
        return {
            'status': 'success',
            'results': results,
            'timestamp': timezone.now().isoformat()
        }
    
    except Exception as exc:
        logger.error(f"Daily learning loop task failed: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(bind=True)
def extract_knowledge_points_task(self, days=1):
    """知识点提取任务"""
    try:
        logger.info(f"Starting knowledge points extraction for {days} days")
        
        extracted_count = learning_loop_service.knowledge_extractor.auto_extract_and_save(days)
        
        logger.info(f"Knowledge points extraction completed: {extracted_count} points extracted")
        return {
            'status': 'success',
            'extracted_count': extracted_count,
            'days': days,
            'timestamp': timezone.now().isoformat()
        }
    
    except Exception as exc:
        logger.error(f"Knowledge points extraction task failed: {exc}")
        raise self.retry(exc=exc, countdown=30, max_retries=2)


@shared_task(bind=True)
def generate_user_report_task(self, user_id, date_str=None):
    """生成用户学习报告任务"""
    try:
        logger.info(f"Generating learning report for user {user_id}")
        
        from datetime import datetime
        date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
        
        report = learning_loop_service.report_generator.generate_daily_report(user_id, date)
        
        logger.info(f"Learning report generated for user {user_id}: {report.id}")
        return {
            'status': 'success',
            'report_id': report.id,
            'user_id': user_id,
            'date': date.isoformat() if date else timezone.now().date().isoformat(),
            'timestamp': timezone.now().isoformat()
        }
    
    except Exception as exc:
        logger.error(f"Generate user report task failed for user {user_id}: {exc}")
        raise self.retry(exc=exc, countdown=30, max_retries=2)


@shared_task(bind=True)
def cleanup_old_data_task(self, days_to_keep=90):
    """清理旧数据任务"""
    try:
        logger.info(f"Starting cleanup of data older than {days_to_keep} days")
        
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        # 清理旧的语义索引
        from app.core.models import SemanticIndex
        old_indexes = SemanticIndex.objects.filter(created_at__lt=cutoff_date)
        indexes_count = old_indexes.count()
        old_indexes.delete()
        
        # 清理旧的学习报告（保留重要的）
        from app.core.models import LearningReport
        old_reports = LearningReport.objects.filter(
            created_at__lt=cutoff_date
        ).exclude(
            # 保留包含重要知识点的报告
            knowledge_points__len__gt=5  # This syntax may need adjustment based on DB
        )
        reports_count = old_reports.count()
        old_reports.delete()
        
        logger.info(f"Cleanup completed: {indexes_count} indexes, {reports_count} reports removed")
        return {
            'status': 'success',
            'indexes_removed': indexes_count,
            'reports_removed': reports_count,
            'days_to_keep': days_to_keep,
            'timestamp': timezone.now().isoformat()
        }
    
    except Exception as exc:
        logger.error(f"Cleanup task failed: {exc}")
        raise self.retry(exc=exc, countdown=120, max_retries=1)