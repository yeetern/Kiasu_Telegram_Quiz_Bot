# src/models/quiz_set.py
import uuid
from sqlalchemy import Column, String, BigInteger, Integer
from sqlalchemy.orm import relationship
from src.database import Base

class QuizSet(Base):
    __tablename__ = "quiz_sets"

    # 使用 UUID 字符串作为主键，生成 8 位短 ID (例如: 'a1b2c3d4')
    # 这样生成的链接比较短: t.me/bot?start=a1b2c3d4
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())[:8])
    
    name = Column(String, nullable=False)          # 试卷名称 (e.g. Physics Paper A)
    creator_id = Column(BigInteger, nullable=False) # 创建者的 Telegram User ID
    
    # 关联题目 (One-to-Many)
    # cascade="all, delete-orphan" 表示删除试卷时，里面的题目也会被删除
    questions = relationship("Question", back_populates="quiz_set", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QuizSet(id={self.id}, name={self.name})>"