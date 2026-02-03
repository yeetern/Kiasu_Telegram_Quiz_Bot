from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.question import Question

async def seed_questions(session: AsyncSession):
    """如果数据库为空，插入初始测试数据"""
    result = await session.execute(select(Question))
    first_q = result.scalars().first()
    
    if first_q:
        return  # 已经有数据了，跳过

    print("🌱 Seeding initial data...")
    
    # 创建一道测试题 (Physics)
    q1 = Question(
        image_file_id="AgACAgUAAxkBAAICQmX...", # 这是一个假 ID，之后我们会替换
        subject="Physics",
        topic="Force and Motion",
        correct_option="B",
        reference_data={
            "textbook": "KSSM Physics Form 4",
            "page": 45,
            "explanation": "F=ma. Mass is constant, so F is proportional to a."
        }
    )
    
    session.add(q1)
    await session.commit()
    print("✅ Seed data inserted: Question #1 (Physics)")