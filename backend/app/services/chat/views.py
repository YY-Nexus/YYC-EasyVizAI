"""
Chat API views and endpoints
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import asyncio
from asgiref.sync import sync_to_async

from .models import ChatSession, ChatMessage
from .storage import JSONFileStorage, SessionStorageInterface
from ..llm_router.router import LLMService
from ..tools.framework import ToolExecutionService, register_default_tools

# Initialize services
llm_service = LLMService()
tool_service = ToolExecutionService()
json_storage = JSONFileStorage()

# Register default tools
register_default_tools()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_session(request):
    """Create a new chat session"""
    data = request.data
    title = data.get('title', '')
    model_config = data.get('model_config', {})
    
    try:
        # Use database storage by default, fallback to JSON
        session = ChatSession.objects.create(
            user=request.user,
            title=title,
            model_config=model_config,
            system_prompt=data.get('system_prompt', ''),
            context_window=data.get('context_window', 4000)
        )
        
        return Response({
            'session_id': str(session.id),
            'title': session.title,
            'created_at': session.created_at.isoformat(),
            'model_config': session.model_config
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        # Fallback to JSON storage
        try:
            session_data = json_storage.create_session(
                user_id=request.user.id,
                title=title,
                model_config=model_config,
                system_prompt=data.get('system_prompt', ''),
                context_window=data.get('context_window', 4000)
            )
            return Response(session_data, status=status.HTTP_201_CREATED)
        except Exception as json_error:
            return Response({
                'error': f'Failed to create session: {str(json_error)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session(request, session_id):
    """Get session metadata"""
    try:
        # Try database first
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            return Response({
                'session_id': str(session.id),
                'title': session.title,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
                'model_config': session.model_config,
                'system_prompt': session.system_prompt,
                'message_count': session.message_count,
                'total_tokens': session.total_tokens,
                'is_active': session.is_active
            })
        except ChatSession.DoesNotExist:
            # Fallback to JSON storage
            session_data = json_storage.get_session(session_id, request.user.id)
            if session_data:
                return Response(session_data)
            else:
                return Response({
                    'error': 'Session not found'
                }, status=status.HTTP_404_NOT_FOUND)
                
    except Exception as e:
        return Response({
            'error': f'Failed to get session: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_sessions(request):
    """List user sessions"""
    limit = int(request.GET.get('limit', 20))
    offset = int(request.GET.get('offset', 0))
    
    try:
        # Try database first
        try:
            sessions = ChatSession.objects.filter(user=request.user)[offset:offset + limit]
            session_list = [{
                'session_id': str(session.id),
                'title': session.title,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
                'message_count': session.message_count,
                'is_active': session.is_active
            } for session in sessions]
            
            return Response({
                'sessions': session_list,
                'total': ChatSession.objects.filter(user=request.user).count()
            })
        except Exception:
            # Fallback to JSON storage
            sessions = json_storage.list_sessions(request.user.id, limit, offset)
            return Response({
                'sessions': sessions,
                'total': len(sessions)
            })
            
    except Exception as e:
        return Response({
            'error': f'Failed to list sessions: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, session_id):
    """Send message to session"""
    data = request.data
    message_content = data.get('content', '')
    role = data.get('role', 'user')
    stream = data.get('stream', False)
    
    if not message_content:
        return Response({
            'error': 'Message content is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get session
        session = None
        session_data = None
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            session_data = json_storage.get_session(session_id, request.user.id)
            if not session_data:
                return Response({
                    'error': 'Session not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Add user message
        if session:
            user_message = ChatMessage.objects.create(
                session=session,
                role=role,
                content=message_content,
                tokens=len(message_content.split())  # Simple token estimation
            )
        else:
            user_message = json_storage.add_message(
                session_id=session_id,
                role=role,
                content=message_content,
                tokens=len(message_content.split())
            )
        
        # Prepare messages for LLM
        if session:
            messages = [{
                'role': msg.role,
                'content': msg.content
            } for msg in session.get_messages_for_context()]
        else:
            messages = [{
                'role': msg['role'],
                'content': msg['content']
            } for msg in json_storage.get_messages(session_id)]
        
        # Get model configuration
        model_config = session.model_config if session else session_data.get('model_config', {})
        model = model_config.get('model', 'gpt-3.5-turbo')
        
        if stream:
            return _handle_streaming_response(session_id, messages, model, session, session_data)
        else:
            return _handle_sync_response(session_id, messages, model, session, session_data)
            
    except Exception as e:
        return Response({
            'error': f'Failed to send message: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _handle_sync_response(session_id, messages, model, session, session_data):
    """Handle synchronous response"""
    async def _generate_response():
        try:
            response = await llm_service.chat_completion(
                session_id=session_id,
                messages=messages,
                model=model
            )
            
            # Save assistant message
            if session:
                assistant_message = ChatMessage.objects.create(
                    session=session,
                    role='assistant',
                    content=response.content,
                    tokens=response.usage.get('completion_tokens', 0),
                    model_used=response.model,
                    generation_time_ms=response.response_time_ms
                )
                message_id = str(assistant_message.id)
            else:
                assistant_message = json_storage.add_message(
                    session_id=session_id,
                    role='assistant',
                    content=response.content,
                    tokens=response.usage.get('completion_tokens', 0),
                    model_used=response.model,
                    generation_time_ms=response.response_time_ms
                )
                message_id = assistant_message['id']
            
            return {
                'message_id': message_id,
                'content': response.content,
                'model': response.model,
                'usage': response.usage,
                'generation_time_ms': response.response_time_ms
            }
        except Exception as e:
            return {'error': str(e)}
    
    # Run async function
    result = asyncio.run(_generate_response())
    
    if 'error' in result:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(result)


def _handle_streaming_response(session_id, messages, model, session, session_data):
    """Handle streaming response"""
    def event_stream():
        async def _stream_response():
            try:
                content_chunks = []
                async for chunk in llm_service.chat_completion_stream(
                    session_id=session_id,
                    messages=messages,
                    model=model
                ):
                    content_chunks.append(chunk)
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                
                # Save complete message
                complete_content = ''.join(content_chunks)
                if session:
                    assistant_message = ChatMessage.objects.create(
                        session=session,
                        role='assistant',
                        content=complete_content,
                        tokens=len(complete_content.split()),
                        model_used=model
                    )
                    message_id = str(assistant_message.id)
                else:
                    assistant_message = json_storage.add_message(
                        session_id=session_id,
                        role='assistant',
                        content=complete_content,
                        tokens=len(complete_content.split()),
                        model_used=model
                    )
                    message_id = assistant_message['id']
                
                yield f"data: {json.dumps({'type': 'done', 'message_id': message_id})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        # Convert async generator to sync
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async_gen = _stream_response()
            while True:
                try:
                    chunk = loop.run_until_complete(async_gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
        finally:
            loop.close()
    
    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history(request, session_id):
    """Get session message history"""
    cursor = request.GET.get('cursor')
    limit = int(request.GET.get('limit', 20))
    
    try:
        # Try database first
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            messages = session.messages.all()[:limit]
            
            return Response({
                'messages': [{
                    'id': str(msg.id),
                    'role': msg.role,
                    'content': msg.content,
                    'created_at': msg.created_at.isoformat(),
                    'tokens': msg.tokens,
                    'model_used': msg.model_used
                } for msg in messages]
            })
        except ChatSession.DoesNotExist:
            # Fallback to JSON storage
            messages = json_storage.get_messages(session_id, limit)
            return Response({'messages': messages})
            
    except Exception as e:
        return Response({
            'error': f'Failed to get history: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tool_call(request, session_id):
    """Execute tool call"""
    data = request.data
    tool_name = data.get('tool_name')
    parameters = data.get('parameters', {})
    
    if not tool_name:
        return Response({
            'error': 'Tool name is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    async def _execute_tool():
        return await tool_service.execute_tool(
            tool_name=tool_name,
            parameters=parameters,
            context={'session_id': session_id, 'user_id': request.user.id}
        )
    
    try:
        result = asyncio.run(_execute_tool())
        return Response({
            'tool_name': tool_name,
            'success': result.success,
            'data': result.data,
            'error': result.error,
            'execution_time_ms': result.execution_time_ms
        })
    except Exception as e:
        return Response({
            'error': f'Tool execution failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_session(request, session_id):
    """Delete or archive session"""
    try:
        # Try database first
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            session.archive()
            return Response({'message': 'Session archived'})
        except ChatSession.DoesNotExist:
            # Fallback to JSON storage
            success = json_storage.delete_session(session_id, request.user.id)
            if success:
                return Response({'message': 'Session deleted'})
            else:
                return Response({
                    'error': 'Session not found'
                }, status=status.HTTP_404_NOT_FOUND)
                
    except Exception as e:
        return Response({
            'error': f'Failed to delete session: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)