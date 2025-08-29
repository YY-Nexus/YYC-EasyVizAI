"""
搜索增强与检索服务
"""
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from sentence_transformers import SentenceTransformer
import sqlite3
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from app.core.models import SemanticIndex, ChatMessage, KnowledgePoint


class MockSentenceTransformer:
    """Mock sentence transformer for testing"""
    
    def encode(self, texts):
        """Return mock embeddings"""
        if isinstance(texts, str):
            texts = [texts]
        return [np.random.rand(384).astype(np.float32) for _ in texts]


class VectorSearchService:
    """向量搜索服务"""
    
    def __init__(self):
        self.model = None
        self.dimension = 384  # MiniLM-L12-v2 embedding dimension
        self._init_vector_db()
    
    def _ensure_model_loaded(self):
        """确保模型已加载"""
        if self.model is None:
            try:
                self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            except Exception as e:
                # Fallback: use a simple mock for testing
                print(f"Warning: Could not load sentence transformer model: {e}")
                self.model = MockSentenceTransformer()
    
    def _init_vector_db(self):
        """初始化向量数据库"""
        os.makedirs(settings.CHROMA_PERSIST_DIRECTORY.parent, exist_ok=True)
        self.db_path = settings.CHROMA_PERSIST_DIRECTORY.parent / "vectors.db"
        
        # 使用SQLite with vector extension简化实现
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_type TEXT NOT NULL,
                content_id TEXT NOT NULL,
                content_text TEXT NOT NULL,
                embedding BLOB NOT NULL,
                metadata TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_content_type ON vectors(content_type)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_content_id ON vectors(content_id)")
        self.conn.commit()
    
    def embed_text(self, text: str) -> List[float]:
        """文本嵌入"""
        self._ensure_model_loaded()
        embedding = self.model.encode([text])[0]
        return embedding.tolist()
    
    def add_document(self, content_type: str, content_id: str, content_text: str, metadata: Dict = None):
        """添加文档到向量索引"""
        metadata = metadata or {}
        embedding = self.embed_text(content_text)
        embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
        
        # 同时存储到Django模型和SQLite
        SemanticIndex.objects.update_or_create(
            content_type=content_type,
            content_id=content_id,
            defaults={
                'content_text': content_text,
                'embedding': embedding,
                'metadata': metadata
            }
        )
        
        self.conn.execute("""
            INSERT OR REPLACE INTO vectors (content_type, content_id, content_text, embedding, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (content_type, content_id, content_text, embedding_bytes, json.dumps(metadata)))
        self.conn.commit()
    
    def search_similar(self, query: str, content_types: List[str] = None, limit: int = 10) -> List[Dict]:
        """相似性搜索"""
        query_embedding = self.embed_text(query)
        query_bytes = np.array(query_embedding, dtype=np.float32).tobytes()
        
        # 使用Django ORM进行简化的相似性搜索
        queryset = SemanticIndex.objects.all()
        if content_types:
            queryset = queryset.filter(content_type__in=content_types)
        
        results = []
        for item in queryset.order_by('-created_at')[:limit * 3]:  # Get more for ranking
            # 计算余弦相似度
            item_embedding = np.array(item.embedding, dtype=np.float32)
            query_arr = np.array(query_embedding, dtype=np.float32)
            
            # 归一化向量
            item_norm = np.linalg.norm(item_embedding)
            query_norm = np.linalg.norm(query_arr)
            
            if item_norm > 0 and query_norm > 0:
                similarity = np.dot(item_embedding, query_arr) / (item_norm * query_norm)
                results.append({
                    'content_type': item.content_type,
                    'content_id': item.content_id,
                    'content_text': item.content_text,
                    'metadata': item.metadata,
                    'similarity': float(similarity),
                    'created_at': item.created_at.isoformat()
                })
        
        # 按相似度排序并返回top results
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]


class FullTextSearchService:
    """全文检索服务"""
    
    @staticmethod
    def search_chat_messages(query: str, user_id: int = None, limit: int = 20) -> List[Dict]:
        """搜索聊天消息"""
        queryset = ChatMessage.objects.select_related('session')
        
        if user_id:
            queryset = queryset.filter(session__user_id=user_id)
        
        # 简单的全文搜索
        queryset = queryset.filter(content__icontains=query)
        
        results = []
        for msg in queryset.order_by('-created_at')[:limit]:
            results.append({
                'type': 'chat_message',
                'id': str(msg.id),
                'content': msg.content,
                'role': msg.role,
                'session_id': msg.session.id,
                'session_title': msg.session.title,
                'created_at': msg.created_at.isoformat(),
                'emotion_snapshot': msg.emotion_snapshot
            })
        
        return results
    
    @staticmethod
    def search_knowledge_points(query: str, category: str = None, limit: int = 20) -> List[Dict]:
        """搜索知识点"""
        queryset = KnowledgePoint.objects.all()
        
        if category:
            queryset = queryset.filter(category=category)
        
        # 搜索标题和内容
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        
        results = []
        for kp in queryset.order_by('-importance', '-created_at')[:limit]:
            results.append({
                'type': 'knowledge_point',
                'id': str(kp.id),
                'title': kp.title,
                'content': kp.content,
                'category': kp.category,
                'importance': kp.importance,
                'tags': kp.tags,
                'source_type': kp.source_type,
                'source_id': kp.source_id,
                'created_at': kp.created_at.isoformat()
            })
        
        return results


class HybridSearchService:
    """混合搜索服务 - 结合全文检索和向量检索"""
    
    def __init__(self):
        self.vector_service = VectorSearchService()
        self.fulltext_service = FullTextSearchService()
    
    def search(self, query: str, content_types: List[str] = None, user_id: int = None, 
               limit: int = 20, hybrid_ratio: float = 0.6) -> Dict[str, Any]:
        """
        混合搜索
        
        Args:
            query: 搜索查询
            content_types: 内容类型过滤
            user_id: 用户ID过滤
            limit: 结果数量限制
            hybrid_ratio: 向量搜索结果的权重比例 (0.0-1.0)
        """
        vector_limit = int(limit * hybrid_ratio)
        fulltext_limit = limit - vector_limit
        
        results = {
            'query': query,
            'total_results': 0,
            'vector_results': [],
            'fulltext_results': [],
            'combined_results': []
        }
        
        # 向量搜索
        if vector_limit > 0:
            vector_results = self.vector_service.search_similar(
                query, content_types, vector_limit
            )
            results['vector_results'] = vector_results
        
        # 全文搜索
        if fulltext_limit > 0:
            fulltext_results = []
            
            # 搜索聊天消息
            if not content_types or 'chat' in content_types:
                chat_results = self.fulltext_service.search_chat_messages(
                    query, user_id, fulltext_limit // 2
                )
                fulltext_results.extend(chat_results)
            
            # 搜索知识点
            if not content_types or 'knowledge' in content_types:
                knowledge_results = self.fulltext_service.search_knowledge_points(
                    query, limit=fulltext_limit // 2
                )
                fulltext_results.extend(knowledge_results)
            
            results['fulltext_results'] = fulltext_results[:fulltext_limit]
        
        # 合并结果
        combined = []
        combined.extend(results['vector_results'])
        combined.extend(results['fulltext_results'])
        
        # 去重和排序
        seen_ids = set()
        unique_results = []
        for item in combined:
            item_id = f"{item.get('type', item.get('content_type'))}_{item.get('id', item.get('content_id'))}"
            if item_id not in seen_ids:
                seen_ids.add(item_id)
                unique_results.append(item)
        
        results['combined_results'] = unique_results[:limit]
        results['total_results'] = len(unique_results)
        
        return results
    
    def index_content(self, content_type: str, content_id: str, content_text: str, metadata: Dict = None):
        """索引内容到向量数据库"""
        self.vector_service.add_document(content_type, content_id, content_text, metadata)


# 全局搜索服务实例
search_service = HybridSearchService()