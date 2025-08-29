#!/usr/bin/env python
"""
学习闭环自动化脚本

这个脚本可以用于手动运行学习闭环相关的任务，包括：
- 知识点提取
- 学习报告生成
- 内容索引
- 数据清理

使用方法:
    python learning_loop_automation.py [command] [options]

示例:
    python learning_loop_automation.py extract-knowledge --days 1
    python learning_loop_automation.py generate-report --user-id 1
    python learning_loop_automation.py run-daily-loop
    python learning_loop_automation.py index-sample-data
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

import argparse
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.utils import timezone

from app.core.learning_loop import learning_loop_service
from app.core.search import search_service
from app.core.models import ChatSession, ChatMessage, KnowledgePoint, LearningReport


def create_sample_data():
    """创建示例数据用于测试"""
    print("创建示例数据...")
    
    # 创建测试用户
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"创建用户: {user.username}")
    else:
        print(f"用户已存在: {user.username}")
    
    # 创建聊天会话
    session, created = ChatSession.objects.get_or_create(
        user=user,
        title="学习Django开发",
        defaults={'created_at': timezone.now()}
    )
    
    if created:
        print(f"创建聊天会话: {session.title}")
    
    # 创建示例聊天消息
    sample_messages = [
        {
            'role': 'user',
            'content': 'Django模型是什么？如何设计好的数据模型？',
            'tokens': 20
        },
        {
            'role': 'assistant',
            'content': 'Django模型是数据库表的Python抽象。好的模型设计应该遵循以下原则：1. 单一职责原则，每个模型只负责一个业务实体；2. 合理的字段类型选择；3. 适当的关系设计（ForeignKey、ManyToMany等）；4. 添加必要的索引；5. 使用Meta类定义排序、权限等。',
            'tokens': 80,
            'emotion_snapshot': {'sentiment': 'helpful', 'confidence': 0.9}
        },
        {
            'role': 'user',
            'content': '如何优化Django查询性能？',
            'tokens': 15
        },
        {
            'role': 'assistant',
            'content': 'Django查询优化主要包括：1. 使用select_related()预加载外键关系；2. 使用prefetch_related()预加载多对多关系；3. 避免N+1查询问题；4. 使用only()和defer()限制字段；5. 使用数据库索引；6. 查询缓存；7. 分页处理大数据集；8. 使用explain()分析查询计划。',
            'tokens': 90,
            'emotion_snapshot': {'sentiment': 'educational', 'confidence': 0.85}
        }
    ]
    
    for msg_data in sample_messages:
        message, created = ChatMessage.objects.get_or_create(
            session=session,
            role=msg_data['role'],
            content=msg_data['content'],
            defaults={
                'tokens': msg_data['tokens'],
                'emotion_snapshot': msg_data.get('emotion_snapshot', {}),
                'created_at': timezone.now()
            }
        )
        
        if created:
            print(f"创建消息: {msg_data['role']} - {msg_data['content'][:30]}...")
    
    print("示例数据创建完成！")
    return user


def extract_knowledge_points(days=1):
    """提取知识点"""
    print(f"从最近 {days} 天的对话中提取知识点...")
    
    extracted_count = learning_loop_service.knowledge_extractor.auto_extract_and_save(days)
    
    print(f"成功提取 {extracted_count} 个知识点")
    
    # 显示提取的知识点
    recent_kps = KnowledgePoint.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=1)
    ).order_by('-created_at')[:5]
    
    if recent_kps:
        print("\n最近提取的知识点:")
        for kp in recent_kps:
            print(f"- {kp.title} (类别: {kp.category}, 重要度: {kp.importance})")


def generate_report(user_id=None, date_str=None):
    """生成学习报告"""
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            print(f"用户 {user_id} 不存在")
            return
    else:
        # 使用第一个用户
        user = User.objects.first()
        if not user:
            print("没有找到用户，请先创建用户")
            return
    
    date = None
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            print("日期格式错误，请使用 YYYY-MM-DD 格式")
            return
    
    print(f"为用户 {user.username} 生成学习报告...")
    
    try:
        report = learning_loop_service.report_generator.generate_daily_report(user.id, date)
        
        print(f"报告生成成功:")
        print(f"- 标题: {report.title}")
        print(f"- 摘要: {report.summary}")
        print(f"- 知识点数量: {len(report.knowledge_points)}")
        print(f"- 报告ID: {report.id}")
        
        return report
    except Exception as e:
        print(f"报告生成失败: {e}")


def run_daily_loop(user_id=None):
    """运行每日学习闭环"""
    print("运行每日学习闭环...")
    
    try:
        results = learning_loop_service.run_daily_loop(user_id)
        
        print("学习闭环执行完成:")
        print(f"- 处理用户数: {results['users_processed']}")
        print(f"- 生成报告数: {results['reports_generated']}")
        print(f"- 提取知识点数: {results['knowledge_points_extracted']}")
        
    except Exception as e:
        print(f"学习闭环执行失败: {e}")


def index_sample_data():
    """索引示例数据到搜索服务"""
    print("将示例数据索引到搜索服务...")
    
    # 索引知识点
    knowledge_points = KnowledgePoint.objects.all()[:10]
    for kp in knowledge_points:
        search_service.index_content(
            'knowledge_point',
            str(kp.id),
            f"{kp.title}\n{kp.content}",
            {
                'category': kp.category,
                'importance': kp.importance,
                'tags': kp.tags
            }
        )
    
    print(f"索引了 {knowledge_points.count()} 个知识点")
    
    # 索引聊天消息
    messages = ChatMessage.objects.filter(role='assistant')[:10]
    for msg in messages:
        search_service.index_content(
            'chat_message',
            str(msg.id),
            msg.content,
            {
                'role': msg.role,
                'tokens': msg.tokens,
                'session_title': msg.session.title,
                'emotion_snapshot': msg.emotion_snapshot
            }
        )
    
    print(f"索引了 {messages.count()} 条聊天消息")
    
    # 索引学习报告
    reports = LearningReport.objects.all()[:5]
    for report in reports:
        search_service.index_content(
            'learning_report',
            str(report.id),
            f"{report.title}\n{report.summary}\n{report.content}",
            {
                'date_from': report.date_from.isoformat(),
                'date_to': report.date_to.isoformat(),
                'knowledge_points_count': len(report.knowledge_points)
            }
        )
    
    print(f"索引了 {reports.count()} 个学习报告")
    print("索引完成！")


def test_search(query="Django模型"):
    """测试搜索功能"""
    print(f"测试搜索功能，查询: '{query}'")
    
    try:
        # 测试混合搜索
        results = search_service.search(
            query=query,
            limit=5
        )
        
        print(f"混合搜索结果 (共 {results['total_results']} 个):")
        for i, result in enumerate(results['combined_results'][:3], 1):
            content_preview = result.get('content_text', result.get('content', ''))[:100]
            print(f"{i}. {result.get('type', result.get('content_type'))}: {content_preview}...")
        
    except Exception as e:
        print(f"搜索测试失败: {e}")


def show_stats():
    """显示系统统计信息"""
    print("系统统计信息:")
    print(f"- 用户数量: {User.objects.count()}")
    print(f"- 聊天会话数: {ChatSession.objects.count()}")
    print(f"- 聊天消息数: {ChatMessage.objects.count()}")
    print(f"- 知识点数量: {KnowledgePoint.objects.count()}")
    print(f"- 学习报告数: {LearningReport.objects.count()}")
    print(f"- 语义索引数: {search_service.vector_service.conn.execute('SELECT COUNT(*) FROM vectors').fetchone()[0]}")


def main():
    parser = argparse.ArgumentParser(description='学习闭环自动化脚本')
    parser.add_argument('command', choices=[
        'create-sample-data',
        'extract-knowledge',
        'generate-report',
        'run-daily-loop',
        'index-sample-data',
        'test-search',
        'show-stats',
        'full-demo'
    ], help='要执行的命令')
    
    parser.add_argument('--days', type=int, default=1, help='天数 (用于extract-knowledge)')
    parser.add_argument('--user-id', type=int, help='用户ID (用于generate-report)')
    parser.add_argument('--date', help='日期 YYYY-MM-DD (用于generate-report)')
    parser.add_argument('--query', default='Django模型', help='搜索查询 (用于test-search)')
    
    args = parser.parse_args()
    
    print(f"执行命令: {args.command}")
    print("-" * 50)
    
    if args.command == 'create-sample-data':
        create_sample_data()
    
    elif args.command == 'extract-knowledge':
        extract_knowledge_points(args.days)
    
    elif args.command == 'generate-report':
        generate_report(args.user_id, args.date)
    
    elif args.command == 'run-daily-loop':
        run_daily_loop(args.user_id)
    
    elif args.command == 'index-sample-data':
        index_sample_data()
    
    elif args.command == 'test-search':
        test_search(args.query)
    
    elif args.command == 'show-stats':
        show_stats()
    
    elif args.command == 'full-demo':
        print("运行完整演示...")
        create_sample_data()
        print("\n" + "="*50)
        extract_knowledge_points()
        print("\n" + "="*50)
        generate_report()
        print("\n" + "="*50)
        index_sample_data()
        print("\n" + "="*50)
        test_search()
        print("\n" + "="*50)
        show_stats()
        print("\n演示完成！")


if __name__ == '__main__':
    main()