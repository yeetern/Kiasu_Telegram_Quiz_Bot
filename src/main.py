import asyncio
import logging
from aiogram import Bot, Dispatcher
from sqlalchemy import text

from src.config import config
from src.database import engine, Base, AsyncSessionLocal # <--- Update import
from src.handlers import common, quiz
# 必须导入 models，否则 create_all 找不到表
from src.models import Question 
from src.services.seeder import seed_questions # <--- Update import

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    """初始化数据库：建表 + 播种"""
    async with engine.begin() as conn:
        # ⚠️ 生产环境通常用 Alembic 迁移，MVP 阶段直接用 create_all
        await conn.run_sync(Base.metadata.create_all)
    
    # 运行 Seeder
    async with AsyncSessionLocal() as session:
        await seed_questions(session)

async def main():
    logger.info("🚀 Starting Kiasu Quiz Bot...")

    # 1. 初始化数据库 (建表 + 数据)
    await init_db()

    # 2. 初始化 Bot 和 Dispatcher
    bot = Bot(token=config.BOT_TOKEN.get_secret_value())
    dp = Dispatcher()

    # 3. 注册路由
    dp.include_router(common.router)
    dp.include_router(quiz.router)

    # 4. 启动轮询
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped manually.")