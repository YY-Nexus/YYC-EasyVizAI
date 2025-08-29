"""
WebSocket consumers for real-time communication
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class RealtimeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection"""
        # Extract topics from query parameters
        query_string = self.scope.get('query_string', b'').decode()
        params = dict(x.split('=') for x in query_string.split('&') if '=' in x)
        
        self.topics = params.get('topics', '').split(',')
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
            
        # Join groups for topics
        for topic in self.topics:
            if topic:
                await self.channel_layer.group_add(
                    f'topic_{topic}',
                    self.channel_name
                )
        
        await self.accept()
        
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave groups
        for topic in getattr(self, 'topics', []):
            if topic:
                await self.channel_layer.group_discard(
                    f'topic_{topic}',
                    self.channel_name
                )

    async def receive(self, text_data):
        """Handle message from WebSocket"""
        try:
            data = json.loads(text_data)
            # Handle heartbeat or other client messages
            if data.get('type') == 'heartbeat':
                await self.send(text_data=json.dumps({
                    'type': 'heartbeat_ack',
                    'timestamp': data.get('timestamp')
                }))
        except json.JSONDecodeError:
            pass

    async def event_message(self, event):
        """Handle event from group"""
        await self.send(text_data=json.dumps(event['message']))