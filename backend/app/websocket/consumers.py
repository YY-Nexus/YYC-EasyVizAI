"""
WebSocket consumers
"""
import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from app.llm.gateway import get_llm_gateway

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat"""
    
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'chat_{self.session_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected for session {self.session_id}")
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected for session {self.session_id}")
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'model_switch':
                await self.handle_model_switch(data)
            else:
                await self.send_error(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {str(e)}")
            await self.send_error(f"Error processing message: {str(e)}")
    
    async def handle_chat_message(self, data):
        """Handle chat message and generate response"""
        prompt = data.get('message', '').strip()
        if not prompt:
            await self.send_error("Empty message")
            return
        
        model_key = data.get('model')
        stream = data.get('stream', True)
        
        try:
            gateway = get_llm_gateway()
            
            # Send user message
            await self.send_message({
                'type': 'user_message',
                'message': prompt,
                'timestamp': data.get('timestamp')
            })
            
            # Send typing indicator
            await self.send_message({
                'type': 'typing',
                'status': True
            })
            
            # Generate and stream response
            response_text = ""
            async for chunk in gateway.generate_response(
                prompt=prompt,
                model_key=model_key,
                stream=stream
            ):
                response_text += chunk
                if stream:
                    await self.send_message({
                        'type': 'assistant_chunk',
                        'chunk': chunk,
                        'model': gateway.current_model
                    })
            
            # Send final message if not streaming
            if not stream:
                await self.send_message({
                    'type': 'assistant_message',
                    'message': response_text.strip(),
                    'model': gateway.current_model
                })
            
            # Stop typing indicator
            await self.send_message({
                'type': 'typing',
                'status': False
            })
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            await self.send_error(f"Failed to generate response: {str(e)}")
            await self.send_message({
                'type': 'typing',
                'status': False
            })
    
    async def handle_model_switch(self, data):
        """Handle model switching request"""
        model_key = data.get('model')
        if not model_key:
            await self.send_error("Model key is required")
            return
        
        try:
            gateway = get_llm_gateway()
            success = await gateway.load_model(model_key)
            
            await self.send_message({
                'type': 'model_switched',
                'model': model_key,
                'success': success,
                'current_model': gateway.current_model
            })
            
        except Exception as e:
            logger.error(f"Error switching model: {str(e)}")
            await self.send_error(f"Failed to switch model: {str(e)}")
    
    async def send_message(self, message):
        """Send message to WebSocket"""
        await self.send(text_data=json.dumps(message))
    
    async def send_error(self, error_message):
        """Send error message to WebSocket"""
        await self.send_message({
            'type': 'error',
            'error': error_message
        })
    
    # Group message handlers
    async def chat_message(self, event):
        """Handle message from room group"""
        await self.send_message(event['message'])