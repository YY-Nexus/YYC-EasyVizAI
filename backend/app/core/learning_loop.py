"""
学习闭环自动化服务
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from django.template.loader import render_to_string

from app.core.models import (
    ChatMessage, ChatSession, LearningNode, LearningProgress, 
    LearningReport, KnowledgePoint, SemanticIndex
)
from app.core.search import search_service


class LearningDataCollector:
    """学习数据收集器"""
    
    @staticmethod
    def collect_chat_interactions(user_id: int, days: int = 1) -> Dict[str, Any]:
        """收集聊天交互数据"""
        start_date = timezone.now() - timedelta(days=days)
        
        messages = ChatMessage.objects.filter(
            session__user_id=user_id,
            created_at__gte=start_date
        ).select_related('session')
        
        data = {
            'total_messages': messages.count(),
            'user_messages': messages.filter(role='user').count(),
            'assistant_messages': messages.filter(role='assistant').count(),
            'total_tokens': sum(msg.tokens for msg in messages),
            'sessions': messages.values('session_id').distinct().count(),
            'topics': [],
            'emotions': [],
            'time_distribution': defaultdict(int)
        }
        
        # 分析主题和情感
        for msg in messages:
            if msg.emotion_snapshot:
                data['emotions'].append(msg.emotion_snapshot)
            
            # 时间分布
            hour = msg.created_at.hour
            data['time_distribution'][hour] += 1
        
        return data
    
    @staticmethod
    def collect_learning_progress(user_id: int, days: int = 1) -> Dict[str, Any]:
        """收集学习进度数据"""
        start_date = timezone.now() - timedelta(days=days)
        
        progress_updates = LearningProgress.objects.filter(
            user_id=user_id,
            last_updated__gte=start_date
        ).select_related('node')
        
        data = {
            'nodes_updated': progress_updates.count(),
            'completed_nodes': progress_updates.filter(status='completed').count(),
            'in_progress_nodes': progress_updates.filter(status='in_progress').count(),
            'difficulty_distribution': defaultdict(int),
            'tag_distribution': defaultdict(int),
            'progress_details': []
        }
        
        for progress in progress_updates:
            node = progress.node
            data['difficulty_distribution'][node.difficulty] += 1
            
            for tag in node.tags:
                data['tag_distribution'][tag] += 1
            
            data['progress_details'].append({
                'node_title': node.title,
                'status': progress.status,
                'difficulty': node.difficulty,
                'tags': node.tags,
                'updated_at': progress.last_updated.isoformat()
            })
        
        return data
    
    @staticmethod
    def collect_knowledge_creation(user_id: int = None, days: int = 1) -> Dict[str, Any]:
        """收集知识点创建数据"""
        start_date = timezone.now() - timedelta(days=days)
        
        queryset = KnowledgePoint.objects.filter(created_at__gte=start_date)
        # Note: KnowledgePoint doesn't have user field, so we collect all
        
        knowledge_points = queryset.all()
        
        data = {
            'total_points': knowledge_points.count(),
            'category_distribution': defaultdict(int),
            'importance_distribution': defaultdict(int),
            'source_distribution': defaultdict(int),
            'top_points': []
        }
        
        for kp in knowledge_points:
            data['category_distribution'][kp.category] += 1
            data['importance_distribution'][kp.importance] += 1
            data['source_distribution'][kp.source_type] += 1
        
        # 获取重要知识点
        top_points = knowledge_points.order_by('-importance', '-created_at')[:10]
        for kp in top_points:
            data['top_points'].append({
                'title': kp.title,
                'category': kp.category,
                'importance': kp.importance,
                'tags': kp.tags,
                'created_at': kp.created_at.isoformat()
            })
        
        return data


class KnowledgeExtractor:
    """知识点提取器"""
    
    @staticmethod
    def extract_from_chat(chat_message: ChatMessage) -> List[Dict[str, Any]]:
        """从聊天消息中提取知识点"""
        knowledge_points = []
        
        # 简单的知识点识别规则
        content = chat_message.content
        
        # 查找定义性内容
        if any(keyword in content.lower() for keyword in ['是什么', '定义', '概念', '原理']):
            knowledge_points.append({
                'title': f"来自聊天的概念: {content[:50]}...",
                'content': content,
                'category': '概念定义',
                'importance': 3,
                'source_type': 'chat',
                'source_id': str(chat_message.id),
                'tags': ['聊天', '概念']
            })
        
        # 查找技术实现
        if any(keyword in content.lower() for keyword in ['如何', '实现', '方法', '步骤']):
            knowledge_points.append({
                'title': f"实现方法: {content[:50]}...",
                'content': content,
                'category': '技术实现',
                'importance': 4,
                'source_type': 'chat',
                'source_id': str(chat_message.id),
                'tags': ['聊天', '实现']
            })
        
        # 查找问题解决
        if any(keyword in content.lower() for keyword in ['问题', '错误', '解决', '调试']):
            knowledge_points.append({
                'title': f"问题解决: {content[:50]}...",
                'content': content,
                'category': '问题解决',
                'importance': 5,
                'source_type': 'chat',
                'source_id': str(chat_message.id),
                'tags': ['聊天', '问题解决']
            })
        
        return knowledge_points
    
    @staticmethod
    def auto_extract_and_save(days: int = 1):
        """自动提取并保存知识点"""
        start_date = timezone.now() - timedelta(days=days)
        
        # 获取最近的聊天消息
        recent_messages = ChatMessage.objects.filter(
            created_at__gte=start_date,
            role='assistant'  # 主要从助手回复中提取知识点
        ).select_related('session')
        
        extracted_count = 0
        for message in recent_messages:
            knowledge_points = KnowledgeExtractor.extract_from_chat(message)
            
            for kp_data in knowledge_points:
                # 检查是否已存在类似的知识点
                existing = KnowledgePoint.objects.filter(
                    source_type=kp_data['source_type'],
                    source_id=kp_data['source_id']
                ).first()
                
                if not existing:
                    knowledge_point = KnowledgePoint.objects.create(**kp_data)
                    
                    # 同时添加到搜索索引
                    search_service.index_content(
                        'knowledge_point',
                        str(knowledge_point.id),
                        f"{knowledge_point.title}\n{knowledge_point.content}",
                        {
                            'category': knowledge_point.category,
                            'importance': knowledge_point.importance,
                            'tags': knowledge_point.tags
                        }
                    )
                    extracted_count += 1
        
        return extracted_count


class LearningReportGenerator:
    """学习报告生成器"""
    
    def __init__(self):
        self.collector = LearningDataCollector()
        self.extractor = KnowledgeExtractor()
    
    def generate_daily_report(self, user_id: int, date: datetime = None) -> LearningReport:
        """生成每日学习报告"""
        if date is None:
            date = timezone.now().date()
        
        # 收集数据
        chat_data = self.collector.collect_chat_interactions(user_id, days=1)
        learning_data = self.collector.collect_learning_progress(user_id, days=1)
        knowledge_data = self.collector.collect_knowledge_creation(user_id, days=1)
        
        # 生成报告内容
        report_content = self._generate_report_content(chat_data, learning_data, knowledge_data)
        summary = self._generate_summary(chat_data, learning_data, knowledge_data)
        knowledge_points = self._extract_key_knowledge_points(knowledge_data)
        
        # 创建报告
        report = LearningReport.objects.create(
            user_id=user_id,
            title=f"学习日报 - {date.strftime('%Y年%m月%d日')}",
            content=report_content,
            summary=summary,
            knowledge_points=knowledge_points,
            date_from=date,
            date_to=date
        )
        
        return report
    
    def _generate_report_content(self, chat_data: Dict, learning_data: Dict, knowledge_data: Dict) -> str:
        """生成报告内容"""
        content_parts = []
        
        # 聊天交互部分
        content_parts.append("## 💬 聊天交互统计")
        content_parts.append(f"- 总消息数: {chat_data['total_messages']}")
        content_parts.append(f"- 用户消息: {chat_data['user_messages']}")
        content_parts.append(f"- 助手回复: {chat_data['assistant_messages']}")
        content_parts.append(f"- 总tokens: {chat_data['total_tokens']}")
        content_parts.append(f"- 会话数: {chat_data['sessions']}")
        
        # 学习进度部分
        content_parts.append("\n## 📚 学习进度")
        content_parts.append(f"- 更新节点数: {learning_data['nodes_updated']}")
        content_parts.append(f"- 完成节点: {learning_data['completed_nodes']}")
        content_parts.append(f"- 进行中节点: {learning_data['in_progress_nodes']}")
        
        if learning_data['difficulty_distribution']:
            content_parts.append("- 难度分布:")
            for difficulty, count in learning_data['difficulty_distribution'].items():
                content_parts.append(f"  - 难度{difficulty}: {count}个节点")
        
        # 知识点部分
        content_parts.append("\n## 🧠 知识点统计")
        content_parts.append(f"- 新增知识点: {knowledge_data['total_points']}")
        
        if knowledge_data['category_distribution']:
            content_parts.append("- 类别分布:")
            for category, count in knowledge_data['category_distribution'].items():
                content_parts.append(f"  - {category}: {count}个")
        
        # 重要知识点
        if knowledge_data['top_points']:
            content_parts.append("\n## ⭐ 重要知识点")
            for i, point in enumerate(knowledge_data['top_points'][:5], 1):
                content_parts.append(f"{i}. **{point['title']}** (重要度: {point['importance']})")
                content_parts.append(f"   类别: {point['category']}")
        
        return "\n".join(content_parts)
    
    def _generate_summary(self, chat_data: Dict, learning_data: Dict, knowledge_data: Dict) -> str:
        """生成报告摘要"""
        summary_parts = []
        
        if chat_data['total_messages'] > 0:
            summary_parts.append(f"今日进行了{chat_data['sessions']}次对话")
            summary_parts.append(f"共{chat_data['total_messages']}条消息")
        
        if learning_data['completed_nodes'] > 0:
            summary_parts.append(f"完成了{learning_data['completed_nodes']}个学习节点")
        
        if knowledge_data['total_points'] > 0:
            summary_parts.append(f"积累了{knowledge_data['total_points']}个新知识点")
        
        if not summary_parts:
            return "今日无学习活动记录"
        
        return "，".join(summary_parts) + "。"
    
    def _extract_key_knowledge_points(self, knowledge_data: Dict) -> List[Dict]:
        """提取关键知识点"""
        return [
            {
                'title': point['title'],
                'category': point['category'],
                'importance': point['importance'],
                'tags': point['tags']
            }
            for point in knowledge_data['top_points'][:10]
        ]


class LearningLoopService:
    """学习闭环服务"""
    
    def __init__(self):
        self.report_generator = LearningReportGenerator()
        self.knowledge_extractor = KnowledgeExtractor()
    
    def run_daily_loop(self, user_id: int = None):
        """运行每日学习闭环"""
        results = {
            'reports_generated': 0,
            'knowledge_points_extracted': 0,
            'users_processed': 0
        }
        
        # 自动提取知识点
        extracted_count = self.knowledge_extractor.auto_extract_and_save(days=1)
        results['knowledge_points_extracted'] = extracted_count
        
        # 生成学习报告
        if user_id:
            users = [User.objects.get(id=user_id)]
        else:
            # 为所有活跃用户生成报告
            yesterday = timezone.now() - timedelta(days=1)
            active_users = User.objects.filter(
                chatsession__created_at__gte=yesterday
            ).distinct()[:100]  # 限制处理用户数
            users = list(active_users)
        
        for user in users:
            try:
                report = self.report_generator.generate_daily_report(user.id)
                results['reports_generated'] += 1
                results['users_processed'] += 1
                
                # 将报告添加到搜索索引
                search_service.index_content(
                    'learning_report',
                    str(report.id),
                    f"{report.title}\n{report.summary}\n{report.content}",
                    {
                        'user_id': user.id,
                        'date_from': report.date_from.isoformat(),
                        'date_to': report.date_to.isoformat(),
                        'knowledge_points_count': len(report.knowledge_points)
                    }
                )
            except Exception as e:
                print(f"Error generating report for user {user.id}: {e}")
                continue
        
        return results
    
    def get_learning_insights(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        """获取学习洞察"""
        start_date = timezone.now() - timedelta(days=days)
        
        # 获取学习报告
        reports = LearningReport.objects.filter(
            user_id=user_id,
            created_at__gte=start_date
        ).order_by('-created_at')
        
        # 分析学习模式
        insights = {
            'total_reports': reports.count(),
            'knowledge_categories': defaultdict(int),
            'learning_trends': [],
            'recommendations': []
        }
        
        for report in reports:
            for kp in report.knowledge_points:
                insights['knowledge_categories'][kp.get('category', 'unknown')] += 1
            
            insights['learning_trends'].append({
                'date': report.date_from.isoformat(),
                'knowledge_points': len(report.knowledge_points),
                'summary': report.summary
            })
        
        # 生成建议
        if insights['total_reports'] > 0:
            top_category = max(insights['knowledge_categories'].items(), key=lambda x: x[1])[0]
            insights['recommendations'].append(f"您在{top_category}方面学习较多，建议继续深入")
        
        return insights


# 全局学习闭环服务实例
learning_loop_service = LearningLoopService()