"""Session management for maintaining analysis state and conversation history."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Session:
    """Represents an analysis session."""
    session_id: str
    created_at: datetime
    updated_at: datetime
    state: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    analysis_results: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Add a message to conversation history.
        
        Args:
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Optional metadata
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        self.updated_at = datetime.now()
    
    def update_state(self, key: str, value: Any):
        """
        Update session state.
        
        Args:
            key: State key
            value: State value
        """
        self.state[key] = value
        self.updated_at = datetime.now()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get session state value.
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            State value
        """
        return self.state.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "state": self.state,
            "conversation_history": self.conversation_history,
            "analysis_results": self.analysis_results,
            "metadata": self.metadata
        }


class InMemorySessionService:
    """
    In-memory session service for managing analysis sessions.
    
    Implements session management pattern for:
    - Creating and retrieving sessions
    - Maintaining conversation state
    - Storing analysis context
    - Session lifecycle management
    """
    
    def __init__(self, max_sessions: int = 100):
        """
        Initialize session service.
        
        Args:
            max_sessions: Maximum number of sessions to keep in memory
        """
        self.sessions: Dict[str, Session] = {}
        self.max_sessions = max_sessions
    
    def create_session(
        self,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """
        Create a new session.
        
        Args:
            metadata: Optional session metadata
            
        Returns:
            New Session instance
        """
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        now = datetime.now()
        
        session = Session(
            session_id=session_id,
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )
        
        self.sessions[session_id] = session
        
        # Enforce max sessions limit
        if len(self.sessions) > self.max_sessions:
            self._evict_oldest_session()
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session if found, None otherwise
        """
        return self.sessions.get(session_id)
    
    def update_session(
        self,
        session_id: str,
        state_updates: Optional[Dict[str, Any]] = None,
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> Optional[Session]:
        """
        Update session state and results.
        
        Args:
            session_id: Session identifier
            state_updates: State updates to apply
            analysis_results: Analysis results to store
            
        Returns:
            Updated Session if found, None otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        if state_updates:
            for key, value in state_updates.items():
                session.update_state(key, value)
        
        if analysis_results:
            session.analysis_results = analysis_results
            session.updated_at = datetime.now()
        
        return session
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def list_sessions(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[Session]:
        """
        List sessions with pagination.
        
        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            
        Returns:
            List of sessions
        """
        sessions = sorted(
            self.sessions.values(),
            key=lambda s: s.updated_at,
            reverse=True
        )
        return sessions[offset:offset + limit]
    
    def get_session_count(self) -> int:
        """
        Get total number of active sessions.
        
        Returns:
            Session count
        """
        return len(self.sessions)
    
    def clear_all_sessions(self):
        """Clear all sessions."""
        self.sessions.clear()
    
    def _evict_oldest_session(self):
        """Remove the oldest session to maintain max_sessions limit."""
        if not self.sessions:
            return
        
        oldest_session_id = min(
            self.sessions.keys(),
            key=lambda sid: self.sessions[sid].updated_at
        )
        del self.sessions[oldest_session_id]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get session service statistics.
        
        Returns:
            Dictionary with statistics
        """
        if not self.sessions:
            return {
                "total_sessions": 0,
                "active_sessions": 0,
                "average_conversation_length": 0
            }
        
        total_messages = sum(
            len(s.conversation_history) for s in self.sessions.values()
        )
        
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": len(self.sessions),
            "average_conversation_length": total_messages / len(self.sessions),
            "oldest_session": min(
                s.created_at for s in self.sessions.values()
            ).isoformat(),
            "newest_session": max(
                s.created_at for s in self.sessions.values()
            ).isoformat()
        }


# Global session service instance
_global_session_service: Optional[InMemorySessionService] = None


def get_session_service() -> InMemorySessionService:
    """
    Get the global session service instance.
    
    Returns:
        Global InMemorySessionService
    """
    global _global_session_service
    if _global_session_service is None:
        _global_session_service = InMemorySessionService()
    return _global_session_service