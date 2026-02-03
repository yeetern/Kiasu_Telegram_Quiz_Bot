# src/models/question.py
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from src.database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # --- 新增的外键：关联到 QuizSet ---
    quiz_set_id = Column(String, ForeignKey("quiz_sets.id"), nullable=False)
    
    # --- 内容字段 ---
    # content_type: 'text' 或 'photo'
    content_type = Column(String, default="text", nullable=False)
    # content_data: 如果是 text 存题目文本，如果是 photo 存 file_id
    content_data = Column(String, nullable=False)
    
    # --- 提示与解析 ---
    hint = Column(String, nullable=True)
    
    # --- 选项数据 ---
    # 存 JSON 格式: [{"id": "A", "text": "10N"}, {"id": "B", "text": "20N"}]
    options_data = Column(JSON, nullable=False)
    
    # --- 正确答案 ---
    # 存: "A", "B", "C", or "D"
    correct_option = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    # --- 反向关联 ---
    quiz_set = relationship("QuizSet", back_populates="questions")

    def __repr__(self):
        return f"<Question(id={self.id}, type={self.content_type}, ans={self.correct_option})>"