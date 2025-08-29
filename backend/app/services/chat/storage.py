"""
Storage interfaces for session persistence with multiple backends
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from django.contrib.auth.models import User
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import uuid


class SessionStorageInterface(ABC):
    """Abstract interface for session storage backends"""
    
    @abstractmethod
    def create_session(self, user_id: int, title: str = "", **kwargs) -> Dict[str, Any]:
        """Create a new chat session"""
        pass
    
    @abstractmethod
    def get_session(self, session_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        pass
    
    @abstractmethod
    def list_sessions(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """List user sessions"""
        pass
    
    @abstractmethod
    def update_session(self, session_id: str, user_id: int, **kwargs) -> bool:
        """Update session metadata"""
        pass
    
    @abstractmethod
    def delete_session(self, session_id: str, user_id: int) -> bool:
        """Delete session and all its messages"""
        pass
    
    @abstractmethod
    def add_message(self, session_id: str, role: str, content: str, **kwargs) -> Dict[str, Any]:
        """Add message to session"""
        pass
    
    @abstractmethod
    def get_messages(self, session_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get messages for session"""
        pass


class JSONFileStorage(SessionStorageInterface):
    """JSON file-based storage implementation"""
    
    def __init__(self, storage_dir: str = "data/sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create index file if it doesn't exist
        self.index_file = self.storage_dir / "sessions_index.json"
        if not self.index_file.exists():
            self._write_index({})
    
    def _read_index(self) -> Dict[str, Any]:
        """Read the sessions index"""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _write_index(self, index: Dict[str, Any]):
        """Write the sessions index"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, default=str)
    
    def _get_session_file(self, session_id: str) -> Path:
        """Get session file path"""
        return self.storage_dir / f"{session_id}.json"
    
    def _read_session_file(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Read session data from file"""
        session_file = self._get_session_file(session_id)
        if not session_file.exists():
            return None
            
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _write_session_file(self, session_id: str, data: Dict[str, Any]):
        """Write session data to file"""
        session_file = self._get_session_file(session_id)
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def create_session(self, user_id: int, title: str = "", **kwargs) -> Dict[str, Any]:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        session_data = {
            'id': session_id,
            'user_id': user_id,
            'title': title,
            'created_at': now,
            'updated_at': now,
            'model_config': kwargs.get('model_config', {}),
            'context_window': kwargs.get('context_window', 4000),
            'system_prompt': kwargs.get('system_prompt', ''),
            'is_active': True,
            'archived_at': None,
            'retention_days': kwargs.get('retention_days', 90),
            'messages': []
        }
        
        # Update index
        index = self._read_index()
        if str(user_id) not in index:
            index[str(user_id)] = []
        
        index[str(user_id)].append({
            'session_id': session_id,
            'title': title,
            'created_at': now,
            'updated_at': now,
            'is_active': True
        })
        
        self._write_index(index)
        self._write_session_file(session_id, session_data)
        
        return session_data
    
    def get_session(self, session_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        session_data = self._read_session_file(session_id)
        if session_data and session_data.get('user_id') == user_id:
            return session_data
        return None
    
    def list_sessions(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """List user sessions"""
        index = self._read_index()
        user_sessions = index.get(str(user_id), [])
        
        # Sort by updated_at descending
        user_sessions.sort(key=lambda x: x['updated_at'], reverse=True)
        
        # Apply pagination
        return user_sessions[offset:offset + limit]
    
    def update_session(self, session_id: str, user_id: int, **kwargs) -> bool:
        """Update session metadata"""
        session_data = self.get_session(session_id, user_id)
        if not session_data:
            return False
        
        # Update session data
        for key, value in kwargs.items():
            if key in ['title', 'model_config', 'context_window', 'system_prompt', 'is_active', 'archived_at']:
                session_data[key] = value
        
        session_data['updated_at'] = datetime.now().isoformat()
        
        # Update index
        index = self._read_index()
        user_sessions = index.get(str(user_id), [])
        for session_ref in user_sessions:
            if session_ref['session_id'] == session_id:
                session_ref['updated_at'] = session_data['updated_at']
                session_ref['title'] = session_data.get('title', session_ref['title'])
                session_ref['is_active'] = session_data.get('is_active', session_ref['is_active'])
                break
        
        self._write_index(index)
        self._write_session_file(session_id, session_data)
        
        return True
    
    def delete_session(self, session_id: str, user_id: int) -> bool:
        """Delete session and all its messages"""
        session_data = self.get_session(session_id, user_id)
        if not session_data:
            return False
        
        # Remove from index
        index = self._read_index()
        user_sessions = index.get(str(user_id), [])
        index[str(user_id)] = [s for s in user_sessions if s['session_id'] != session_id]
        
        self._write_index(index)
        
        # Remove session file
        session_file = self._get_session_file(session_id)
        if session_file.exists():
            session_file.unlink()
        
        return True
    
    def add_message(self, session_id: str, role: str, content: str, **kwargs) -> Dict[str, Any]:
        """Add message to session"""
        # Find session by ID to get user_id
        session_data = self._read_session_file(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
        message_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        message = {
            'id': message_id,
            'session_id': session_id,
            'role': role,
            'content': content,
            'tokens': kwargs.get('tokens', 0),
            'model_used': kwargs.get('model_used', ''),
            'created_at': now,
            'generation_time_ms': kwargs.get('generation_time_ms'),
            'tool_calls': kwargs.get('tool_calls', []),
            'emotion_snapshot': kwargs.get('emotion_snapshot', ''),
            'metadata': kwargs.get('metadata', {})
        }
        
        # Add message to session
        session_data['messages'].append(message)
        session_data['updated_at'] = now
        
        # Update index
        index = self._read_index()
        user_sessions = index.get(str(session_data['user_id']), [])
        for session_ref in user_sessions:
            if session_ref['session_id'] == session_id:
                session_ref['updated_at'] = now
                break
        
        self._write_index(index)
        self._write_session_file(session_id, session_data)
        
        return message
    
    def get_messages(self, session_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get messages for session"""
        session_data = self._read_session_file(session_id)
        if not session_data:
            return []
        
        messages = session_data.get('messages', [])
        if limit:
            messages = messages[-limit:]  # Get latest messages
        
        return messages