# Session Data Persistence & Tool Plugin Framework Documentation

## Overview

This document describes the implementation of session data persistence and the tool plugin framework for YYC³ EasyVizAI.

## Storage Structure

### Database Models (SQLite Primary)

#### ChatSession
```python
class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True)  # UUID for session ID
    user = models.ForeignKey(User)           # Associated user
    title = models.CharField(max_length=255) # Session title
    created_at = models.DateTimeField()      # Creation timestamp
    updated_at = models.DateTimeField()      # Last update timestamp
    
    # Configuration
    model_config = models.JSONField()        # LLM model settings
    context_window = models.IntegerField()   # Context window size
    system_prompt = models.TextField()       # System prompt
    
    # Status & Retention
    is_active = models.BooleanField()        # Active status
    archived_at = models.DateTimeField()     # Archive timestamp
    retention_days = models.IntegerField()   # Retention policy
```

#### ChatMessage
```python
class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True)  # UUID for message ID
    session = models.ForeignKey(ChatSession) # Parent session
    role = models.CharField()                # user/assistant/system/tool
    content = models.TextField()             # Message content
    
    # Metadata
    tokens = models.IntegerField()           # Token count
    model_used = models.CharField()          # LLM model used
    created_at = models.DateTimeField()      # Creation timestamp
    generation_time_ms = models.IntegerField() # Generation time
    
    # Advanced features
    tool_calls = models.JSONField()          # Tool calls made
    emotion_snapshot = models.CharField()    # Emotion detected
    metadata = models.JSONField()            # Additional metadata
```

### JSON File Storage (Fallback)

#### Directory Structure
```
data/sessions/
├── sessions_index.json          # User session index
├── {session_id}.json            # Individual session files
└── ...
```

#### Session File Format
```json
{
  "id": "uuid-session-id",
  "user_id": 123,
  "title": "Session Title",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T01:00:00Z",
  "model_config": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7
  },
  "context_window": 4000,
  "system_prompt": "You are a helpful assistant",
  "is_active": true,
  "archived_at": null,
  "retention_days": 90,
  "messages": [
    {
      "id": "uuid-message-id",
      "session_id": "uuid-session-id",
      "role": "user",
      "content": "Hello!",
      "tokens": 1,
      "model_used": "",
      "created_at": "2024-01-01T00:00:00Z",
      "generation_time_ms": null,
      "tool_calls": [],
      "emotion_snapshot": "",
      "metadata": {}
    }
  ]
}
```

#### Index File Format
```json
{
  "123": [
    {
      "session_id": "uuid-session-id",
      "title": "Session Title",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T01:00:00Z",
      "is_active": true
    }
  ]
}
```

## Storage Interface

### SessionStorageInterface
Abstract interface for storage backends:

```python
class SessionStorageInterface(ABC):
    @abstractmethod
    def create_session(self, user_id: int, title: str = "", **kwargs) -> Dict[str, Any]:
        """Create a new chat session"""
    
    @abstractmethod
    def get_session(self, session_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
    
    @abstractmethod
    def add_message(self, session_id: str, role: str, content: str, **kwargs) -> Dict[str, Any]:
        """Add message to session"""
    
    # ... other methods
```

## Tool Plugin Framework

### Architecture

```
┌─────────────────┐
│   LLM Router    │ ← Calls tools based on function calling
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Tool Execution  │ ← Manages tool lifecycle
│    Service      │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Tool Registry  │ ← Discovers and manages tools
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   Tool Plugins  │ ← Individual tool implementations
└─────────────────┘
```

### Tool Plugin Interface

#### BaseTool Abstract Class
```python
class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name identifier"""
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for LLM"""
    
    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """Tool parameters definition"""
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute the tool with given parameters"""
```

#### Tool Parameter Definition
```python
@dataclass
class ToolParameter:
    name: str
    type: str  # 'string', 'number', 'boolean', 'array', 'object'
    description: str
    required: bool = False
    default: Any = None
    enum: List[Any] = None
```

#### Tool Result Structure
```python
@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: str = None
    execution_time_ms: int = 0
    metadata: Dict[str, Any] = None
```

### Available Tools

#### Enabled Tools
1. **Learning Node Query** (`learning_node_query`)
   - Query learning paths and nodes
   - Returns recommended learning sequences

2. **Report Generation** (`report_generation`)
   - Generate reports from session data
   - Create summaries and analysis

#### Disabled Tools (Security Reserved)
1. **File Retrieval** (`file_retrieval`)
   - Read file contents from system
   - **DISABLED** by default for security

2. **Script Execution** (`script_execution`)
   - Execute code snippets
   - **DISABLED** by default for security

### Tool Registration

```python
# Register a new tool
from app.services.tools.framework import tool_registry

class MyCustomTool(BaseTool):
    @property
    def name(self) -> str:
        return "my_custom_tool"
    
    # ... implement other methods

# Register the tool
tool_registry.register(MyCustomTool())
```

### OpenAI Function Calling Schema
Tools automatically generate OpenAI-compatible schemas:

```json
{
  "name": "learning_node_query",
  "description": "Query learning nodes and recommended learning paths",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query for learning nodes"
      },
      "difficulty": {
        "type": "string",
        "description": "Difficulty level filter",
        "enum": ["beginner", "intermediate", "advanced"]
      }
    },
    "required": ["query"]
  }
}
```

## LLM Router

### Multi-Model Support

#### Supported Providers
1. **OpenAI**
   - GPT-3.5 Turbo, GPT-4, GPT-4 Turbo
   - Function calling support
   - Streaming support

2. **Anthropic**
   - Claude 3 (Haiku, Sonnet, Opus)
   - Large context windows (200k tokens)
   - No function calling (yet)

#### Model Configuration
```python
@dataclass
class ModelConfig:
    provider: ModelProvider
    model_id: str
    display_name: str
    context_window: int
    supports_functions: bool = False
    supports_streaming: bool = True
    temperature_range: tuple = (0.0, 2.0)
    max_tokens_default: int = 1000
    cost_per_1k_tokens: float = 0.0
```

#### Router Features
- **Automatic Fallback**: Falls back to default model on failure
- **Request Validation**: Validates parameters against model capabilities
- **Model Suggestions**: Suggests models based on requirements
- **Provider Abstraction**: Uniform interface across providers

### Usage Examples

#### Creating a Session
```python
# Via Django ORM
session = ChatSession.objects.create(
    user=user,
    title="My Chat Session",
    model_config={'model': 'gpt-3.5-turbo'}
)

# Via JSON Storage
session_data = json_storage.create_session(
    user_id=user.id,
    title="My Chat Session",
    model_config={'model': 'gpt-3.5-turbo'}
)
```

#### Using LLM Router
```python
from app.services.llm_router.router import LLMService

llm_service = LLMService()

# Generate response
response = await llm_service.chat_completion(
    session_id="session-id",
    messages=[{"role": "user", "content": "Hello"}],
    model="gpt-3.5-turbo"
)

# Stream response
async for chunk in llm_service.chat_completion_stream(
    session_id="session-id",
    messages=[{"role": "user", "content": "Hello"}],
    model="gpt-3.5-turbo"
):
    print(chunk)
```

#### Executing Tools
```python
from app.services.tools.framework import ToolExecutionService

tool_service = ToolExecutionService()

result = await tool_service.execute_tool(
    "learning_node_query",
    {"query": "python basics"},
    {"user_id": user.id}
)
```

## API Endpoints

### Chat Sessions
- `POST /api/v1/chat/session/` - Create session
- `GET /api/v1/chat/session/{id}/` - Get session info
- `GET /api/v1/chat/sessions/` - List sessions
- `POST /api/v1/chat/session/{id}/message/` - Send message (supports streaming)
- `GET /api/v1/chat/session/{id}/history/` - Get message history
- `POST /api/v1/chat/session/{id}/tool-call/` - Execute tool
- `DELETE /api/v1/chat/session/{id}/` - Archive session

### Tools
- `GET /api/v1/tools/` - List available tools
- `GET /api/v1/tools/schemas/` - Get tool schemas for LLM
- `POST /api/v1/tools/execute/` - Execute tool
- `GET /api/v1/tools/{tool_name}/` - Get tool info

### LLM Router
- `GET /api/v1/llm/models/` - List available models
- `GET /api/v1/llm/models/{model_id}/` - Get model info
- `POST /api/v1/llm/models/suggestions/` - Get model suggestions
- `POST /api/v1/llm/models/test/` - Test model
- `GET /api/v1/llm/providers/` - Get providers info

## Configuration

### Environment Variables
```bash
# Database (defaults to SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# LLM API Keys
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Tool Security
ENABLE_FILE_RETRIEVAL=false
ENABLE_SCRIPT_EXECUTION=false

# Session Settings
SESSION_RETENTION_DAYS=90
DEFAULT_LLM_MODEL=gpt-3.5-turbo

# Redis for WebSocket (optional)
REDIS_URL=redis://localhost:6379
```

### Settings
```python
EASYVIZ_SETTINGS = {
    'SESSION_RETENTION_DAYS': 90,
    'ENABLE_FILE_RETRIEVAL': False,
    'ENABLE_SCRIPT_EXECUTION': False,
    'DEFAULT_LLM_MODEL': 'gpt-3.5-turbo',
    'SUPPORTED_LLM_MODELS': [
        'gpt-3.5-turbo',
        'gpt-4',
        'claude-2',
        'claude-instant-1',
    ],
}
```

## Security Considerations

1. **Tool Execution**: File retrieval and script execution tools are disabled by default
2. **Input Validation**: All tool parameters are validated before execution
3. **User Isolation**: Sessions and data are isolated by user
4. **API Authentication**: All endpoints require authentication
5. **Data Retention**: Configurable retention policies for data cleanup

## Performance Considerations

1. **Storage Fallback**: JSON storage for scenarios where database is unavailable
2. **Async Execution**: All LLM and tool operations are asynchronous
3. **Streaming Support**: Real-time streaming for chat responses
4. **Connection Pooling**: Database connections are pooled
5. **Caching**: Model configurations and tool schemas are cached

## Testing

The implementation includes comprehensive tests for:
- Session persistence (both database and JSON)
- Tool plugin framework
- LLM router and multi-model support
- API endpoints
- Storage interfaces

Run tests with:
```bash
python manage.py test app.services.chat.tests
python manage.py test app.services.tools.tests  
python manage.py test app.services.llm_router.tests
```