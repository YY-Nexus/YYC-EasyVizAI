"""
Tests for tool plugin framework
"""
from django.test import TestCase
import asyncio
from .framework import (
    BaseTool, ToolParameter, ToolResult, ToolRegistry, 
    ToolExecutionService, tool_registry, register_default_tools
)


class MockTool(BaseTool):
    """Mock tool for testing"""
    
    @property
    def name(self) -> str:
        return "mock_tool"
    
    @property
    def description(self) -> str:
        return "A mock tool for testing"
    
    @property
    def parameters(self):
        return [
            ToolParameter(
                name="test_param",
                type="string",
                description="A test parameter",
                required=True
            ),
            ToolParameter(
                name="optional_param",
                type="number",
                description="An optional parameter",
                default=42
            )
        ]
    
    async def execute(self, parameters, context=None):
        if not parameters.get('test_param'):
            return ToolResult(success=False, error="test_param is required")
        
        return ToolResult(
            success=True,
            data={"message": f"Hello {parameters['test_param']}!"},
            execution_time_ms=10
        )


class ToolFrameworkTestCase(TestCase):
    def setUp(self):
        self.registry = ToolRegistry()
        self.service = ToolExecutionService(self.registry)
        self.mock_tool = MockTool()
        self.registry.register(self.mock_tool)
    
    def test_tool_registration(self):
        """Test tool registration"""
        self.assertEqual(len(self.registry.list_tools()), 1)
        self.assertEqual(self.registry.get_tool("mock_tool"), self.mock_tool)
    
    def test_tool_schema_generation(self):
        """Test tool schema generation"""
        schema = self.mock_tool.get_schema()
        
        self.assertEqual(schema['name'], 'mock_tool')
        self.assertEqual(schema['description'], 'A mock tool for testing')
        self.assertIn('parameters', schema)
        self.assertIn('test_param', schema['parameters']['properties'])
        self.assertIn('test_param', schema['parameters']['required'])
    
    def test_tool_execution_success(self):
        """Test successful tool execution"""
        async def run_test():
            result = await self.service.execute_tool(
                "mock_tool",
                {"test_param": "World"}
            )
            return result
        
        result = asyncio.run(run_test())
        
        self.assertTrue(result.success)
        self.assertEqual(result.data['message'], 'Hello World!')
        self.assertIsNone(result.error)
    
    def test_tool_execution_failure(self):
        """Test failed tool execution"""
        async def run_test():
            result = await self.service.execute_tool(
                "mock_tool",
                {}  # Missing required parameter
            )
            return result
        
        result = asyncio.run(run_test())
        
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
    
    def test_tool_not_found(self):
        """Test execution of non-existent tool"""
        async def run_test():
            result = await self.service.execute_tool(
                "nonexistent_tool",
                {}
            )
            return result
        
        result = asyncio.run(run_test())
        
        self.assertFalse(result.success)
        self.assertIn("not found", result.error)
    
    def test_parameter_validation(self):
        """Test parameter validation"""
        # Valid parameters
        self.assertTrue(self.mock_tool.validate_parameters({"test_param": "value"}))
        
        # Missing required parameter
        self.assertFalse(self.mock_tool.validate_parameters({}))


class DefaultToolsTestCase(TestCase):
    def setUp(self):
        register_default_tools()
        self.service = ToolExecutionService()
    
    def test_file_retrieval_tool_disabled(self):
        """Test that file retrieval tool is disabled by default"""
        async def run_test():
            result = await self.service.execute_tool(
                "file_retrieval",
                {"file_path": "/etc/passwd"}
            )
            return result
        
        result = asyncio.run(run_test())
        
        self.assertFalse(result.success)
        self.assertIn("disabled", result.error)
    
    def test_script_execution_tool_disabled(self):
        """Test that script execution tool is disabled by default"""
        async def run_test():
            result = await self.service.execute_tool(
                "script_execution",
                {"script": "print('hello')", "language": "python"}
            )
            return result
        
        result = asyncio.run(run_test())
        
        self.assertFalse(result.success)
        self.assertIn("disabled", result.error)
    
    def test_learning_node_query_tool_enabled(self):
        """Test that learning node query tool is enabled"""
        async def run_test():
            result = await self.service.execute_tool(
                "learning_node_query",
                {"query": "python basics"}
            )
            return result
        
        result = asyncio.run(run_test())
        
        self.assertTrue(result.success)
        self.assertIn("nodes", result.data)
    
    def test_report_generation_tool_enabled(self):
        """Test that report generation tool is enabled"""
        async def run_test():
            result = await self.service.execute_tool(
                "report_generation",
                {"session_id": "test_session"}
            )
            return result
        
        result = asyncio.run(run_test())
        
        self.assertTrue(result.success)
        self.assertIn("report_id", result.data)