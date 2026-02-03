"""
QuizSet Model - Project Kancil
Defines the container for a collection of questions, representing 
a specific practice paper or instructional module.
"""

import uuid
from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base

class QuizSet(Base):
    """
    Represents a quiz paper created by an educator.
    Uses a shortened UUID as the primary key for cleaner Telegram deep links.
    """
    __tablename__ = "quiz_sets"

    # Primary Key: Shortened UUID (8 characters)
    # Example deep link: https://t.me/KancilBot?start=a1b2c3d4
    id: Mapped[str] = mapped_column(
        String(8), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())[:8]
    )
    
    # Name/Title of the Quiz (e.g., "Physics Form 4: Heat")
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    # Telegram User ID of the Educator who created this set
    creator_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    
    # Relationship: One QuizSet contains many Questions.
    # cascade="all, delete-orphan" ensures child questions are deleted 
    # if the QuizSet is removed.
    questions: Mapped[list["Question"]] = relationship(
        "Question", 
        back_populates="quiz_set", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<QuizSet(id='{self.id}', name='{self.name}')>"