"""
搜索和学习闭环 API 视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta

from app.core.search import search_service
from app.core.learning_loop import learning_loop_service
from app.core.models import LearningReport, KnowledgePoint


class SearchViewSet(viewsets.ViewSet):
    """搜索API"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def hybrid_search(self, request):
        """混合搜索接口"""
        query = request.data.get('query', '')
        if not query:
            return Response(
                {'error': '查询参数不能为空'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        content_types = request.data.get('content_types', [])
        limit = min(request.data.get('limit', 20), 100)  # 最大100
        hybrid_ratio = request.data.get('hybrid_ratio', 0.6)
        
        try:
            results = search_service.search(
                query=query,
                content_types=content_types,
                user_id=request.user.id,
                limit=limit,
                hybrid_ratio=hybrid_ratio
            )
            return Response(results)
        except Exception as e:
            return Response(
                {'error': f'搜索失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def vector_search(self, request):
        """向量搜索接口"""
        query = request.data.get('query', '')
        if not query:
            return Response(
                {'error': '查询参数不能为空'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        content_types = request.data.get('content_types', [])
        limit = min(request.data.get('limit', 20), 100)
        
        try:
            results = search_service.vector_service.search_similar(
                query=query,
                content_types=content_types,
                limit=limit
            )
            return Response({
                'query': query,
                'results': results,
                'total_results': len(results)
            })
        except Exception as e:
            return Response(
                {'error': f'向量搜索失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def fulltext_search(self, request):
        """全文搜索接口"""
        query = request.data.get('query', '')
        if not query:
            return Response(
                {'error': '查询参数不能为空'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        search_type = request.data.get('type', 'all')  # 'chat', 'knowledge', 'all'
        limit = min(request.data.get('limit', 20), 100)
        
        try:
            results = []
            
            if search_type in ['chat', 'all']:
                chat_results = search_service.fulltext_service.search_chat_messages(
                    query, request.user.id, limit // 2 if search_type == 'all' else limit
                )
                results.extend(chat_results)
            
            if search_type in ['knowledge', 'all']:
                knowledge_results = search_service.fulltext_service.search_knowledge_points(
                    query, limit=limit // 2 if search_type == 'all' else limit
                )
                results.extend(knowledge_results)
            
            return Response({
                'query': query,
                'search_type': search_type,
                'results': results[:limit],
                'total_results': len(results)
            })
        except Exception as e:
            return Response(
                {'error': f'全文搜索失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def index_content(self, request):
        """手动索引内容"""
        content_type = request.data.get('content_type')
        content_id = request.data.get('content_id')
        content_text = request.data.get('content_text')
        metadata = request.data.get('metadata', {})
        
        if not all([content_type, content_id, content_text]):
            return Response(
                {'error': '缺少必要参数'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            search_service.index_content(content_type, content_id, content_text, metadata)
            return Response({'message': '内容索引成功'})
        except Exception as e:
            return Response(
                {'error': f'索引失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LearningLoopViewSet(viewsets.ViewSet):
    """学习闭环API"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate_daily_report(self, request):
        """生成每日学习报告"""
        date_str = request.data.get('date')
        date = None
        
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': '日期格式错误，请使用 YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            report = learning_loop_service.report_generator.generate_daily_report(
                request.user.id, date
            )
            return Response({
                'report_id': report.id,
                'title': report.title,
                'summary': report.summary,
                'date_from': report.date_from,
                'date_to': report.date_to,
                'knowledge_points_count': len(report.knowledge_points),
                'created_at': report.created_at
            })
        except Exception as e:
            return Response(
                {'error': f'报告生成失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def get_reports(self, request):
        """获取学习报告列表"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        reports = LearningReport.objects.filter(
            user=request.user,
            created_at__gte=start_date
        ).order_by('-created_at')
        
        data = []
        for report in reports:
            data.append({
                'id': report.id,
                'title': report.title,
                'summary': report.summary,
                'date_from': report.date_from,
                'date_to': report.date_to,
                'knowledge_points_count': len(report.knowledge_points),
                'created_at': report.created_at
            })
        
        return Response({
            'reports': data,
            'total_count': len(data)
        })
    
    @action(detail=True, methods=['get'])
    def get_report_detail(self, request, pk=None):
        """获取报告详情"""
        try:
            report = LearningReport.objects.get(id=pk, user=request.user)
            return Response({
                'id': report.id,
                'title': report.title,
                'content': report.content,
                'summary': report.summary,
                'knowledge_points': report.knowledge_points,
                'date_from': report.date_from,
                'date_to': report.date_to,
                'created_at': report.created_at
            })
        except LearningReport.DoesNotExist:
            return Response(
                {'error': '报告不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def extract_knowledge_points(self, request):
        """手动提取知识点"""
        days = int(request.data.get('days', 1))
        
        try:
            extracted_count = learning_loop_service.knowledge_extractor.auto_extract_and_save(days)
            return Response({
                'message': f'成功提取 {extracted_count} 个知识点',
                'extracted_count': extracted_count
            })
        except Exception as e:
            return Response(
                {'error': f'知识点提取失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def run_daily_loop(self, request):
        """运行每日学习闭环"""
        try:
            results = learning_loop_service.run_daily_loop(request.user.id)
            return Response({
                'message': '学习闭环执行完成',
                'results': results
            })
        except Exception as e:
            return Response(
                {'error': f'学习闭环执行失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def get_insights(self, request):
        """获取学习洞察"""
        days = int(request.query_params.get('days', 7))
        
        try:
            insights = learning_loop_service.get_learning_insights(request.user.id, days)
            return Response(insights)
        except Exception as e:
            return Response(
                {'error': f'获取洞察失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def get_knowledge_points(self, request):
        """获取知识点列表"""
        category = request.query_params.get('category')
        limit = min(int(request.query_params.get('limit', 50)), 200)
        
        queryset = KnowledgePoint.objects.all()
        if category:
            queryset = queryset.filter(category=category)
        
        knowledge_points = queryset.order_by('-importance', '-created_at')[:limit]
        
        data = []
        for kp in knowledge_points:
            data.append({
                'id': kp.id,
                'title': kp.title,
                'content': kp.content,
                'category': kp.category,
                'importance': kp.importance,
                'source_type': kp.source_type,
                'source_id': kp.source_id,
                'tags': kp.tags,
                'created_at': kp.created_at
            })
        
        return Response({
            'knowledge_points': data,
            'total_count': len(data)
        })