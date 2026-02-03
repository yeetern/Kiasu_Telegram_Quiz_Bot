"""
Question Model - Project Kancil
Defines the structure for individual quiz questions, supporting 
multimodal content (text/photo) and instructional metadata.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from src.database import Base

class Question(Base):
    """
    Represents a single MCQ question within a QuizSet.
    """
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Association with the parent QuizSet
    quiz_set_id = Column(String(8), ForeignKey("quiz_sets.id"), nullable=False)
    
    # Content Metadata
    # content_type: 'text' or 'photo'
    content_type = Column(String, default="text", nullable=False)
    
    # content_data: Stores raw text or the Telegram file_id
    content_data = Column(String, nullable=False)
    
    # Instructional hint or reference (Subject, Chapter, Page)
    hint = Column(String, nullable=True)
    
    # Option Data
    # Format: [{"id": "A", "text": "Option A Content"}, ...]
    options_data = Column(JSON, nullable=False)
    
    # The identifier for the correct choice (e.g., 'A', 'B', 'C', or 'D')
    correct_option = Column(String, nullable=False)

    # Status flag for soft-deletion or moderation
    is_active = Column(Boolean, default=True)

    # Relationship mapping back to the QuizSet
    quiz_set = relationship("QuizSet", back_populates="questions")

    def __repr__(self):
        return (
            f"<Question(id={self.id}, type='{self.content_type}', "
            f"correct='{self.correct_option}')>"
        )