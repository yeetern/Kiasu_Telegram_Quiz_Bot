# src/main.py
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# 导入配置和数据库
from src.config import config
from src.database import init_db

# 导入我们的 Handlers
from src.handlers import creator, attempt, common

async def main():
    # 1. 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting Bot...")

    # 2. 初始化数据库 (建表)
    logger.info("Initializing Database...")
    await init_db()

    # 3. 创建 Bot 和 Dispatcher
    # 必须显式获取 SecretStr 的真实值
    bot = Bot(token=config.BOT_TOKEN.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())

    # 4. 注册路由 (Routers)
    # 这里的顺序很重要：
    # attempt (处理 deep link /start xxx)
    # creator (处理 /newquiz)
    # common (处理普通 /start 和兜底逻辑)
    dp.include_router(attempt.router)
    dp.include_router(creator.router)
    
    # 如果你有 common.py 处理普通的 /start 欢迎语，可以保留，
    # 但要确保 common.py 里的 CommandStart() 不要覆盖掉 attempt 的 deep_link
    # 或者直接把 common 放在最后
    if hasattr(common, 'router'):
        dp.include_router(common.router)

    # 5. 开始轮询
    logger.info("Bot is ready! Polling updates...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")