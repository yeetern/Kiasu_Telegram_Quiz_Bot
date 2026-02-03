from sqlalchemy import String, Boolean, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base

class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # 题目图片 (Telegram file_id)
    # 也可以存 URL，但 MVP 我们先假设是 file_id
    image_file_id: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # 题目元数据
    subject: Mapped[str] = mapped_column(String(50))   # e.g., "Physics"
    topic: Mapped[str] = mapped_column(String(100))    # e.g., "Force and Motion"
    
    # 选项与答案
    # 简化版：题目文字直接写在 caption 里，这里只存正确选项
    correct_option: Mapped[str] = mapped_column(String(1)) # "A", "B", "C", "D"
    
    # 核心教育价值：引用信息
    # 存成 JSON: {"textbook": "Form 4 Physics", "page": 23, "explanation": "..."}
    reference_data: Mapped[dict] = mapped_column(JSON, default={})
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f"<Question(id={self.id}, subject='{self.subject}')>"