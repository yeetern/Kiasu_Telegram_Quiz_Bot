# src/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# ✅ 关键修正：必须从 src.config 导入 config 对象
from src.config import config

# 创建异步引擎
engine = create_async_engine(config.DATABASE_URL, echo=False)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

# 依赖注入函数
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# 初始化数据库表结构
async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # 如果需要重置可取消注释
        await conn.run_sync(Base.metadata.create_all)