"""
Event publishing system for real-time updates
"""
from typing import Dict, Any
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def publish_event(event_data: Dict[str, Any], topic: str = None):
    """
    Publish an event to WebSocket subscribers
    
    Args:
        event_data: Event data to send
        topic: Topic to publish to (defaults to event type)
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
        
    # Use event type as topic if not specified
    if not topic:
        topic = event_data.get('type', 'general')
    
    # Send to group
    async_to_sync(channel_layer.group_send)(
        f'topic_{topic}',
        {
            'type': 'event_message',
            'message': event_data
        }
    )