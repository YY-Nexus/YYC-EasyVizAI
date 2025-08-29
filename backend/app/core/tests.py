"""
测试搜索和学习闭环 API
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from app.core.models import ChatSession, ChatMessage, KnowledgePoint, LearningReport


class SearchAPITest(TestCase):
    """搜索API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self.session = ChatSession.objects.create(
            user=self.user,
            title="测试会话"
        )
        
        self.message = ChatMessage.objects.create(
            session=self.session,
            role='assistant',
            content='Django是一个高级Python Web框架',
            tokens=10
        )
        
        self.knowledge_point = KnowledgePoint.objects.create(
            title='Django框架简介',
            content='Django是一个基于Python的Web开发框架',
            category='技术概念',
            importance=4,
            source_type='manual',
            source_id='test'
        )
    
    def test_hybrid_search(self):
        """测试混合搜索"""
        url = reverse('search-hybrid-search')
        data = {
            'query': 'Django',
            'limit': 10
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('query', response.data)
        self.assertIn('total_results', response.data)
        self.assertEqual(response.data['query'], 'Django')
    
    def test_vector_search(self):
        """测试向量搜索"""
        url = reverse('search-vector-search')
        data = {
            'query': 'Python框架',
            'limit': 5
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_fulltext_search(self):
        """测试全文搜索"""
        url = reverse('search-fulltext-search')
        data = {
            'query': 'Django',
            'type': 'all',
            'limit': 10
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_index_content(self):
        """测试内容索引"""
        url = reverse('search-index-content')
        data = {
            'content_type': 'test_document',
            'content_id': 'test_123',
            'content_text': '这是一个测试文档内容',
            'metadata': {'category': '测试'}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_search_empty_query(self):
        """测试空查询"""
        url = reverse('search-hybrid-search')
        data = {'query': ''}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class LearningLoopAPITest(TestCase):
    """学习闭环API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self.session = ChatSession.objects.create(
            user=self.user,
            title="学习会话"
        )
        
        ChatMessage.objects.create(
            session=self.session,
            role='assistant',
            content='Python是一种编程语言',
            tokens=10
        )
    
    def test_generate_daily_report(self):
        """测试生成每日报告"""
        url = reverse('learning-generate-daily-report')
        data = {}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('report_id', response.data)
        self.assertIn('title', response.data)
        self.assertIn('summary', response.data)
    
    def test_get_reports(self):
        """测试获取报告列表"""
        # 先创建一个报告
        LearningReport.objects.create(
            user=self.user,
            title='测试报告',
            content='测试内容',
            summary='测试摘要',
            date_from=timezone.now().date(),
            date_to=timezone.now().date()
        )
        
        url = reverse('learning-get-reports')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reports', response.data)
        self.assertIn('total_count', response.data)
        self.assertTrue(len(response.data['reports']) > 0)
    
    def test_get_report_detail(self):
        """测试获取报告详情"""
        report = LearningReport.objects.create(
            user=self.user,
            title='测试报告',
            content='测试内容',
            summary='测试摘要',
            date_from=timezone.now().date(),
            date_to=timezone.now().date()
        )
        
        url = reverse('learning-get-report-detail', kwargs={'pk': report.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], report.id)
        self.assertEqual(response.data['title'], '测试报告')
    
    def test_extract_knowledge_points(self):
        """测试提取知识点"""
        url = reverse('learning-extract-knowledge-points')
        data = {'days': 1}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('extracted_count', response.data)
    
    def test_run_daily_loop(self):
        """测试运行每日闭环"""
        url = reverse('learning-run-daily-loop')
        
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_get_insights(self):
        """测试获取学习洞察"""
        url = reverse('learning-get-insights')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_reports', response.data)
    
    def test_get_knowledge_points(self):
        """测试获取知识点列表"""
        # 创建测试知识点
        KnowledgePoint.objects.create(
            title='测试知识点',
            content='测试内容',
            category='测试',
            importance=3,
            source_type='test',
            source_id='test'
        )
        
        url = reverse('learning-get-knowledge-points')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('knowledge_points', response.data)
        self.assertTrue(len(response.data['knowledge_points']) > 0)


class LearningLoopServiceTest(TestCase):
    """学习闭环服务测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.session = ChatSession.objects.create(
            user=self.user,
            title="测试会话"
        )
    
    def test_knowledge_extraction(self):
        """测试知识点提取"""
        from app.core.learning_loop import KnowledgeExtractor
        
        message = ChatMessage.objects.create(
            session=self.session,
            role='assistant',
            content='机器学习是什么？机器学习是人工智能的一个分支',
            tokens=20
        )
        
        extractor = KnowledgeExtractor()
        knowledge_points = extractor.extract_from_chat(message)
        
        self.assertTrue(len(knowledge_points) > 0)
        self.assertIn('机器学习', knowledge_points[0]['content'])
    
    def test_learning_data_collection(self):
        """测试学习数据收集"""
        from app.core.learning_loop import LearningDataCollector
        
        ChatMessage.objects.create(
            session=self.session,
            role='user',
            content='测试消息',
            tokens=5
        )
        
        collector = LearningDataCollector()
        chat_data = collector.collect_chat_interactions(self.user.id, days=1)
        
        self.assertEqual(chat_data['total_messages'], 1)
        self.assertEqual(chat_data['user_messages'], 1)
    
    def test_report_generation(self):
        """测试报告生成"""
        from app.core.learning_loop import LearningReportGenerator
        
        ChatMessage.objects.create(
            session=self.session,
            role='assistant',
            content='Python是一种编程语言',
            tokens=10
        )
        
        generator = LearningReportGenerator()
        report = generator.generate_daily_report(self.user.id)
        
        self.assertIsNotNone(report)
        self.assertEqual(report.user, self.user)
        self.assertIn('学习日报', report.title)