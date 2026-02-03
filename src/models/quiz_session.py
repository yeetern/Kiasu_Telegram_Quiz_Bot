"""
Quiz Session Model - Project Kancil
Tracks active student attempts, maintaining state for progress, 
scoring, and answer history in a persistent database layer.
"""

import uuid
from datetime import datetime
from typing import List, Dict
from sqlalchemy import String, Integer, JSON, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base

class QuizSession(Base):
    """
    Represents an active or completed practice session for a specific user.
    """
    __tablename__ = "quiz_sessions"

    # UUID used as a public-facing unique identifier for the session
    # Provides better security/obfuscation than auto-incrementing integers
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    
    # Telegram User ID to identify who the session belongs to
    user_id: Mapped[int] = mapped_column(Integer, index=True) 
    
    # Practice Metadata
    subject: Mapped[str] = mapped_column(String(50))
    total_count: Mapped[int] = mapped_column(Integer) # Total questions in this set
    
    # Core State Management
    # Stores the ordered list of Question IDs for this specific session
    # e.g., [101, 205, 302, 140]
    question_ids: Mapped[List[int]] = mapped_column(JSON) 
    
    # Pointer to the current progress (0-indexed)
    current_index: Mapped[int] = mapped_column(Integer, default=0)
    
    # Scoring Metrics
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Session Status & Timestamps
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Answer History for later review
    # Format: {"101": "A", "205": "C"}
    user_answers: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict)

    def __repr__(self) -> str:
        return (
            f"<QuizSession(id={self.id[:8]}..., user={self.user_id}, "
            f"progress={self.current_index}/{self.total_count})>"
        )