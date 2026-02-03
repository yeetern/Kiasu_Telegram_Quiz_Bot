# src/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from src.config import config

# 1. 创建异步引擎
engine = create_async_engine(config.DATABASE_URL, echo=False)

# 2. 创建 Session 工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. 定义 ORM 基类
class Base(DeclarativeBase):
    pass

# 4. 依赖注入函数 (Dependency for Handlers)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# 5. 初始化数据库函数 (用于 main.py)
async def init_db():
    async with engine.begin() as conn:
        # 注意：生产环境中通常使用 Alembic 进行迁移，
        # 这里为了开发方便，直接创建所有表 (如果表不存在)
        await conn.run_sync(Base.metadata.create_all)