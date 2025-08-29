"""
Tests for session persistence and storage interfaces
"""
import os
import tempfile
import shutil
from django.test import TestCase
from django.contrib.auth.models import User
from .models import ChatSession, ChatMessage
from .storage import JSONFileStorage


class SessionPersistenceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_chat_session(self):
        """Test creating a chat session"""
        session = ChatSession.objects.create(
            user=self.user,
            title='Test Session',
            model_config={'model': 'gpt-3.5-turbo'}
        )
        
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.title, 'Test Session')
        self.assertEqual(session.model_config['model'], 'gpt-3.5-turbo')
        self.assertTrue(session.is_active)
    
    def test_add_messages_to_session(self):
        """Test adding messages to a session"""
        session = ChatSession.objects.create(
            user=self.user,
            title='Test Session'
        )
        
        # Add user message
        user_msg = ChatMessage.objects.create(
            session=session,
            role='user',
            content='Hello, how are you?',
            tokens=4
        )
        
        # Add assistant message
        assistant_msg = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content='I am doing well, thank you!',
            tokens=7,
            model_used='gpt-3.5-turbo'
        )
        
        self.assertEqual(session.message_count, 2)
        self.assertEqual(session.total_tokens, 11)
        
        messages = list(session.get_messages_for_context())
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].content, 'Hello, how are you?')
        self.assertEqual(messages[1].content, 'I am doing well, thank you!')
    
    def test_session_archival(self):
        """Test session archival"""
        session = ChatSession.objects.create(
            user=self.user,
            title='Test Session'
        )
        
        self.assertTrue(session.is_active)
        self.assertIsNone(session.archived_at)
        
        session.archive()
        
        self.assertFalse(session.is_active)
        self.assertIsNotNone(session.archived_at)


class JSONFileStorageTestCase(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.storage = JSONFileStorage(storage_dir=self.temp_dir)
        self.user_id = 1
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_create_session_json(self):
        """Test creating session with JSON storage"""
        session_data = self.storage.create_session(
            user_id=self.user_id,
            title='Test JSON Session',
            model_config={'model': 'gpt-4'}
        )
        
        self.assertEqual(session_data['user_id'], self.user_id)
        self.assertEqual(session_data['title'], 'Test JSON Session')
        self.assertEqual(session_data['model_config']['model'], 'gpt-4')
        self.assertTrue(session_data['is_active'])
        self.assertIsNotNone(session_data['id'])
    
    def test_add_message_json(self):
        """Test adding message with JSON storage"""
        session_data = self.storage.create_session(
            user_id=self.user_id,
            title='Test Session'
        )
        session_id = session_data['id']
        
        message_data = self.storage.add_message(
            session_id=session_id,
            role='user',
            content='Hello JSON storage!',
            tokens=3
        )
        
        self.assertEqual(message_data['role'], 'user')
        self.assertEqual(message_data['content'], 'Hello JSON storage!')
        self.assertEqual(message_data['tokens'], 3)
        self.assertIsNotNone(message_data['id'])
        
        messages = self.storage.get_messages(session_id)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['content'], 'Hello JSON storage!')
    
    def test_list_sessions_json(self):
        """Test listing sessions with JSON storage"""
        # Create multiple sessions
        session1 = self.storage.create_session(user_id=self.user_id, title='Session 1')
        session2 = self.storage.create_session(user_id=self.user_id, title='Session 2')
        
        sessions = self.storage.list_sessions(self.user_id)
        self.assertEqual(len(sessions), 2)
        
        # Should be sorted by updated_at descending
        self.assertEqual(sessions[0]['title'], 'Session 2')
        self.assertEqual(sessions[1]['title'], 'Session 1')
    
    def test_delete_session_json(self):
        """Test deleting session with JSON storage"""
        session_data = self.storage.create_session(user_id=self.user_id, title='To Delete')
        session_id = session_data['id']
        
        # Verify it exists
        retrieved = self.storage.get_session(session_id, self.user_id)
        self.assertIsNotNone(retrieved)
        
        # Delete it
        success = self.storage.delete_session(session_id, self.user_id)
        self.assertTrue(success)
        
        # Verify it's gone
        retrieved = self.storage.get_session(session_id, self.user_id)
        self.assertIsNone(retrieved)