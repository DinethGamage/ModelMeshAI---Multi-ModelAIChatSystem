"""
Session management for multi-turn conversations.
Handles in-memory storage of conversation history and document state.
"""

import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    """Represents a single message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Optional[Dict] = None


@dataclass
class Session:
    """Represents a chat session with history and state."""
    session_id: str
    messages: List[Message] = field(default_factory=list)
    document_uploaded: bool = False
    document_name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to the session history."""
        message = Message(role=role, content=content, metadata=metadata)
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get conversation history in a format suitable for LLMs.
        
        Args:
            limit: Maximum number of recent messages to return
            
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        messages = self.messages[-limit:] if limit else self.messages
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
    
    def set_document(self, document_name: str) -> None:
        """Mark that a document has been uploaded for this session."""
        self.document_uploaded = True
        self.document_name = document_name


class SessionManager:
    """Manages multiple chat sessions."""
    
    def __init__(self):
        """Initialize the session manager with empty storage."""
        self._sessions: Dict[str, Session] = {}
    
    def create_session(self) -> str:
        """
        Create a new session.
        
        Returns:
            New session ID
        """
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = Session(session_id=session_id)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Session object or None if not found
        """
        return self._sessions.get(session_id)
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, Session]:
        """
        Get existing session or create a new one.
        
        Args:
            session_id: Optional existing session ID
            
        Returns:
            Tuple of (session_id, session)
        """
        if session_id and session_id in self._sessions:
            return session_id, self._sessions[session_id]
        
        new_session_id = self.create_session()
        return new_session_id, self._sessions[new_session_id]
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            True if deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def clear_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clear sessions older than specified hours.
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of sessions cleared
        """
        current_time = datetime.now()
        to_delete = []
        
        for session_id, session in self._sessions.items():
            age = (current_time - session.last_activity).total_seconds() / 3600
            if age > max_age_hours:
                to_delete.append(session_id)
        
        for session_id in to_delete:
            del self._sessions[session_id]
        
        return len(to_delete)


# Global session manager instance
session_manager = SessionManager()
