import uuid
from datetime import datetime
from sqlalchemy import String, Integer, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base

class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    # 使用 UUID 作为对外展示的 Quiz ID (看起来更高级，且防碰撞)
    # 例如: 550e8400-e29b... (或者我们之后缩短它)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    user_id: Mapped[int] = mapped_column(Integer, index=True) # 属于哪个用户
    
    # 考卷配置
    subject: Mapped[str] = mapped_column(String(50))
    total_count: Mapped[int] = mapped_column(Integer) # 这套题总共有几题 (e.g., 10)
    
    # 核心状态管理
    # 存储这套卷子包含的所有题目 ID列表，例如: [1, 5, 12, 8, 3]
    question_ids: Mapped[list] = mapped_column(JSON) 
    
    # 当前进度：0 代表正在做第 1 题 (question_ids[0])
    current_index: Mapped[int] = mapped_column(Integer, default=0)
    
    # 成绩记录
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # 状态
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # (可选) 以后可以存用户的具体答案: {"q1": "A", "q5": "C"}
    user_answers: Mapped[dict] = mapped_column(JSON, default={})

    def __repr__(self):
        return f"<QuizSession(id={self.id}, user={self.user_id}, progress={self.current_index}/{self.total_count})>"