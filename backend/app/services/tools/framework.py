"""
Tool plugin framework for extensible functionality
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class ToolStatus(Enum):
    """Tool execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DISABLED = "disabled"


@dataclass
class ToolParameter:
    """Tool parameter definition"""
    name: str
    type: str  # 'string', 'number', 'boolean', 'array', 'object'
    description: str
    required: bool = False
    default: Any = None
    enum: List[Any] = None


@dataclass
class ToolResult:
    """Tool execution result"""
    success: bool
    data: Any = None
    error: str = None
    execution_time_ms: int = 0
    metadata: Dict[str, Any] = None


class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self):
        self.status = ToolStatus.IDLE
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name identifier"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for LLM"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """Tool parameters definition"""
        pass
    
    @property
    def enabled(self) -> bool:
        """Whether the tool is enabled"""
        return True
    
    def get_schema(self) -> Dict[str, Any]:
        """Get OpenAI function calling schema"""
        properties = {}
        required = []
        
        for param in self.parameters:
            prop = {
                "type": param.type,
                "description": param.description
            }
            
            if param.enum:
                prop["enum"] = param.enum
                
            if param.default is not None:
                prop["default"] = param.default
                
            properties[param.name] = prop
            
            if param.required:
                required.append(param.name)
        
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate tool parameters"""
        for param in self.parameters:
            if param.required and param.name not in parameters:
                return False
        return True


# Tool Registry
class ToolRegistry:
    """Registry for managing available tools"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """Register a tool"""
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def unregister(self, tool_name: str):
        """Unregister a tool"""
        if tool_name in self._tools:
            del self._tools[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get tool by name"""
        return self._tools.get(tool_name)
    
    def list_tools(self, enabled_only: bool = True) -> List[BaseTool]:
        """List all tools"""
        tools = list(self._tools.values())
        if enabled_only:
            tools = [tool for tool in tools if tool.enabled]
        return tools
    
    def get_schemas(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """Get all tool schemas for LLM function calling"""
        tools = self.list_tools(enabled_only)
        return [tool.get_schema() for tool in tools]


# Global tool registry instance
tool_registry = ToolRegistry()


# Reserved tool implementations (disabled by default)
class FileRetrievalTool(BaseTool):
    """File retrieval tool (DISABLED - reserved for future)"""
    
    @property
    def name(self) -> str:
        return "file_retrieval"
    
    @property
    def description(self) -> str:
        return "Retrieve and read file contents from the system"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="file_path",
                type="string",
                description="Path to the file to retrieve",
                required=True
            ),
            ToolParameter(
                name="encoding",
                type="string",
                description="File encoding",
                default="utf-8"
            )
        ]
    
    @property
    def enabled(self) -> bool:
        # Disabled by default for security
        from django.conf import settings
        return getattr(settings, 'EASYVIZ_SETTINGS', {}).get('ENABLE_FILE_RETRIEVAL', False)
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute file retrieval (disabled)"""
        return ToolResult(
            success=False,
            error="File retrieval is disabled for security reasons"
        )


class ScriptExecutionTool(BaseTool):
    """Script execution tool (DISABLED - reserved for future)"""
    
    @property
    def name(self) -> str:
        return "script_execution"
    
    @property
    def description(self) -> str:
        return "Execute scripts or code snippets"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="script",
                type="string",
                description="Script content to execute",
                required=True
            ),
            ToolParameter(
                name="language",
                type="string",
                description="Script language",
                enum=["python", "javascript", "bash"],
                default="python"
            ),
            ToolParameter(
                name="timeout",
                type="number",
                description="Execution timeout in seconds",
                default=30
            )
        ]
    
    @property
    def enabled(self) -> bool:
        # Disabled by default for security
        from django.conf import settings
        return getattr(settings, 'EASYVIZ_SETTINGS', {}).get('ENABLE_SCRIPT_EXECUTION', False)
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute script (disabled)"""
        return ToolResult(
            success=False,
            error="Script execution is disabled for security reasons"
        )


# Example enabled tools
class LearningNodeQueryTool(BaseTool):
    """Query learning nodes and paths"""
    
    @property
    def name(self) -> str:
        return "learning_node_query"
    
    @property
    def description(self) -> str:
        return "Query learning nodes and recommended learning paths"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                type="string",
                description="Search query for learning nodes",
                required=True
            ),
            ToolParameter(
                name="difficulty",
                type="string",
                description="Difficulty level filter",
                enum=["beginner", "intermediate", "advanced"]
            ),
            ToolParameter(
                name="limit",
                type="number",
                description="Maximum number of results",
                default=10
            )
        ]
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute learning node query"""
        # Mock implementation
        return ToolResult(
            success=True,
            data={
                "nodes": [
                    {
                        "id": "node_001",
                        "title": "Introduction to Python",
                        "difficulty": "beginner",
                        "prerequisites": []
                    }
                ],
                "recommended_path": ["node_001"]
            },
            execution_time_ms=50
        )


class ReportGenerationTool(BaseTool):
    """Generate reports from data"""
    
    @property
    def name(self) -> str:
        return "report_generation"
    
    @property
    def description(self) -> str:
        return "Generate reports and summaries from conversation data"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="session_id",
                type="string",
                description="Chat session ID to generate report from",
                required=True
            ),
            ToolParameter(
                name="report_type",
                type="string",
                description="Type of report to generate",
                enum=["summary", "analysis", "insights"],
                default="summary"
            )
        ]
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> ToolResult:
        """Execute report generation"""
        # Mock implementation
        return ToolResult(
            success=True,
            data={
                "report_id": "report_001",
                "type": parameters.get("report_type", "summary"),
                "status": "generated",
                "sections": ["introduction", "key_points", "conclusion"]
            },
            execution_time_ms=200
        )


# Register default tools
def register_default_tools():
    """Register default tools in the registry"""
    tool_registry.register(FileRetrievalTool())
    tool_registry.register(ScriptExecutionTool())
    tool_registry.register(LearningNodeQueryTool())
    tool_registry.register(ReportGenerationTool())


# Tool execution service
class ToolExecutionService:
    """Service for executing tools"""
    
    def __init__(self, registry: ToolRegistry = None):
        self.registry = registry or tool_registry
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], 
                          context: Dict[str, Any] = None) -> ToolResult:
        """Execute a tool by name"""
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found"
            )
        
        if not tool.enabled:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' is disabled"
            )
        
        if not tool.validate_parameters(parameters):
            return ToolResult(
                success=False,
                error=f"Invalid parameters for tool '{tool_name}'"
            )
        
        try:
            tool.status = ToolStatus.RUNNING
            result = await tool.execute(parameters, context)
            tool.status = ToolStatus.COMPLETED if result.success else ToolStatus.FAILED
            return result
        except Exception as e:
            tool.status = ToolStatus.FAILED
            logger.exception(f"Tool execution failed: {tool_name}")
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with their schemas"""
        return self.registry.get_schemas(enabled_only=True)