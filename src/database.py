from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import config

# 创建异步引擎
engine = create_async_engine(
    config.DATABASE_URL,
    echo=False,  # 设为 True 可在控制台看到 SQL 语句
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

# 依赖注入函数 (以后在 Handler 里用)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase # <--- 新增
from src.config import config

class Base(DeclarativeBase): # <--- 新增
    pass

engine = create_async_engine(
    config.DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session