# 搜索增强与学习闭环 API 文档

## 概述

YYC³ EasyVizAI 搜索增强与学习闭环功能提供了强大的内容检索和自动化学习总结能力。

## 功能特性

### 🔍 搜索功能
- **混合搜索**: 结合向量搜索和全文搜索
- **向量搜索**: 基于语义相似性的智能搜索
- **全文搜索**: 传统关键词匹配搜索
- **多类型内容**: 支持聊天、文档、代码等多种内容类型

### 🧠 学习闭环
- **自动知识点提取**: 从对话中自动识别和提取关键知识点
- **学习报告生成**: 自动生成每日学习报告
- **知识点归档**: 系统化管理和分类知识点
- **学习洞察**: 分析学习模式和提供建议

## API 端点

### 搜索 API

#### 混合搜索
```http
POST /api/v1/search/hybrid_search/
Content-Type: application/json
Authorization: Bearer <token>

{
    "query": "Django模型设计",
    "content_types": ["chat", "knowledge"],
    "limit": 20,
    "hybrid_ratio": 0.6
}
```

**响应示例:**
```json
{
    "query": "Django模型设计",
    "total_results": 15,
    "vector_results": [...],
    "fulltext_results": [...],
    "combined_results": [
        {
            "type": "chat_message",
            "id": "123",
            "content": "Django模型是...",
            "similarity": 0.89,
            "created_at": "2025-08-30T00:00:00Z"
        }
    ]
}
```

#### 向量搜索
```http
POST /api/v1/search/vector_search/
Content-Type: application/json

{
    "query": "机器学习算法",
    "content_types": ["knowledge"],
    "limit": 10
}
```

#### 全文搜索
```http
POST /api/v1/search/fulltext_search/
Content-Type: application/json

{
    "query": "Python",
    "type": "all",
    "limit": 20
}
```

#### 内容索引
```http
POST /api/v1/search/index_content/
Content-Type: application/json

{
    "content_type": "document",
    "content_id": "doc_123",
    "content_text": "这是一个文档内容...",
    "metadata": {
        "title": "文档标题",
        "category": "技术文档"
    }
}
```

### 学习闭环 API

#### 生成学习报告
```http
POST /api/v1/learning/generate_daily_report/
Content-Type: application/json

{
    "date": "2025-08-30"
}
```

**响应示例:**
```json
{
    "report_id": 456,
    "title": "学习日报 - 2025年08月30日",
    "summary": "今日进行了3次对话，共25条消息，完成了2个学习节点，积累了5个新知识点。",
    "date_from": "2025-08-30",
    "date_to": "2025-08-30",
    "knowledge_points_count": 5,
    "created_at": "2025-08-30T09:00:00Z"
}
```

#### 获取学习报告列表
```http
GET /api/v1/learning/get_reports/?days=30
```

#### 获取报告详情
```http
GET /api/v1/learning/456/get_report_detail/
```

#### 提取知识点
```http
POST /api/v1/learning/extract_knowledge_points/
Content-Type: application/json

{
    "days": 1
}
```

#### 运行学习闭环
```http
POST /api/v1/learning/run_daily_loop/
```

#### 获取学习洞察
```http
GET /api/v1/learning/get_insights/?days=7
```

#### 获取知识点列表
```http
GET /api/v1/learning/get_knowledge_points/?category=技术实现&limit=50
```

## 数据模型

### SemanticIndex (语义索引)
- `content_type`: 内容类型
- `content_id`: 内容ID
- `content_text`: 文本内容
- `embedding`: 向量嵌入
- `metadata`: 元数据

### KnowledgePoint (知识点)
- `title`: 标题
- `content`: 内容
- `category`: 类别
- `importance`: 重要程度 (1-5)
- `source_type`: 来源类型
- `tags`: 标签

### LearningReport (学习报告)
- `title`: 报告标题
- `content`: 报告内容
- `summary`: 摘要
- `knowledge_points`: 知识点列表
- `date_from`, `date_to`: 时间范围

## 自动化任务

### Celery 任务

系统包含以下自动化任务:

1. **每日学习闭环** (`daily_learning_loop_task`)
   - 时间: 每日 9:00 AM
   - 功能: 自动运行学习闭环，生成报告

2. **知识点提取** (`extract_knowledge_points_task`)
   - 时间: 每日 8:30 AM
   - 功能: 从最近对话中提取知识点

3. **数据清理** (`cleanup_old_data_task`)
   - 时间: 每周日 2:00 AM
   - 功能: 清理过期数据

### 运行 Celery

启动 Celery Worker:
```bash
cd backend
celery -A app worker -l info
```

启动 Celery Beat (定时任务):
```bash
cd backend
celery -A app beat -l info
```

## 配置

### 环境变量

```bash
# Redis URL for Celery
REDIS_URL=redis://localhost:6379/0

# Vector search settings
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

### Django 设置

```python
# Vector Search Settings
CHROMA_PERSIST_DIRECTORY = BASE_DIR / 'data' / 'chroma'
EMBEDDING_MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

# Learning Loop Settings
LEARNING_REPORT_SCHEDULE = '0 9 * * *'  # Daily at 9 AM
KNOWLEDGE_ARCHIVE_DIRECTORY = BASE_DIR / 'data' / 'knowledge'
```

## 使用示例

### Python 客户端示例

```python
import requests

# 搜索示例
response = requests.post('http://localhost:8000/api/v1/search/hybrid_search/', 
    json={
        'query': '如何优化数据库查询',
        'content_types': ['chat', 'knowledge'],
        'limit': 10
    },
    headers={'Authorization': 'Bearer <your-token>'}
)

results = response.json()
print(f"找到 {results['total_results']} 个结果")

# 生成学习报告示例
response = requests.post('http://localhost:8000/api/v1/learning/generate_daily_report/',
    json={'date': '2025-08-30'},
    headers={'Authorization': 'Bearer <your-token>'}
)

report = response.json()
print(f"报告生成成功: {report['title']}")
```

### JavaScript 客户端示例

```javascript
// 搜索功能
async function searchContent(query) {
    const response = await fetch('/api/v1/search/hybrid_search/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            query: query,
            limit: 20
        })
    });
    
    const results = await response.json();
    return results.combined_results;
}

// 学习报告功能
async function generateDailyReport() {
    const response = await fetch('/api/v1/learning/generate_daily_report/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    });
    
    const report = await response.json();
    console.log('报告生成成功:', report);
}
```

## 故障排除

### 常见问题

1. **模型下载失败**
   - 检查网络连接
   - 系统会自动使用 Mock 模型作为备选

2. **Redis 连接错误**
   - 确保 Redis 服务运行
   - 检查 `REDIS_URL` 配置

3. **搜索结果为空**
   - 确保内容已被索引
   - 使用 `index_content` API 手动索引

### 日志位置

- Django 日志: 控制台输出
- Celery 日志: Worker 控制台
- 数据库: `backend/db.sqlite3`

## 性能优化

### 搜索性能
- 使用向量数据库缓存
- 限制搜索结果数量
- 异步处理大量数据

### 学习闭环性能
- 批量处理知识点提取
- 定期清理过期数据
- 合理设置任务频率