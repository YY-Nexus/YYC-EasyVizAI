"""
Tools API views and endpoints
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import asyncio

from .framework import tool_registry, ToolExecutionService, register_default_tools

# Initialize and register tools
register_default_tools()
tool_service = ToolExecutionService()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_tools(request):
    """List available tools"""
    try:
        enabled_only = request.GET.get('enabled_only', 'true').lower() == 'true'
        tools = tool_registry.list_tools(enabled_only=enabled_only)
        
        return Response({
            'tools': [{
                'name': tool.name,
                'description': tool.description,
                'enabled': tool.enabled,
                'parameters': [
                    {
                        'name': param.name,
                        'type': param.type,
                        'description': param.description,
                        'required': param.required,
                        'default': param.default,
                        'enum': param.enum
                    } for param in tool.parameters
                ]
            } for tool in tools]
        })
    except Exception as e:
        return Response({
            'error': f'Failed to list tools: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tool_schemas(request):
    """Get tool schemas for LLM function calling"""
    try:
        enabled_only = request.GET.get('enabled_only', 'true').lower() == 'true'
        schemas = tool_registry.get_schemas(enabled_only=enabled_only)
        
        return Response({
            'schemas': schemas
        })
    except Exception as e:
        return Response({
            'error': f'Failed to get tool schemas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_tool(request):
    """Execute a tool"""
    data = request.data
    tool_name = data.get('tool_name')
    parameters = data.get('parameters', {})
    context = data.get('context', {})
    
    if not tool_name:
        return Response({
            'error': 'Tool name is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Add user context
    context['user_id'] = request.user.id
    
    async def _execute():
        return await tool_service.execute_tool(tool_name, parameters, context)
    
    try:
        result = asyncio.run(_execute())
        
        return Response({
            'tool_name': tool_name,
            'success': result.success,
            'data': result.data,
            'error': result.error,
            'execution_time_ms': result.execution_time_ms,
            'metadata': result.metadata
        })
    except Exception as e:
        return Response({
            'error': f'Tool execution failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tool_info(request, tool_name):
    """Get information about a specific tool"""
    try:
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            return Response({
                'error': 'Tool not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'name': tool.name,
            'description': tool.description,
            'enabled': tool.enabled,
            'status': tool.status.value,
            'parameters': [
                {
                    'name': param.name,
                    'type': param.type,
                    'description': param.description,
                    'required': param.required,
                    'default': param.default,
                    'enum': param.enum
                } for param in tool.parameters
            ],
            'schema': tool.get_schema()
        })
    except Exception as e:
        return Response({
            'error': f'Failed to get tool info: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)