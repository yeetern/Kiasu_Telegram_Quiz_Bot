# src/main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.handlers import creator, common, attempt  # <-- 加上 attempt


# ❌ 之前我写错了: from src import config
# ✅ 修正为: 从 src.config 模块中导入 config 对象
from src.config import config 

from src.database import init_db
from src.handlers import creator, common 

async def main():
    # 1. 初始化数据库
    await init_db()
    
    # 2. 初始化 Bot
    # 现在 config 是对象，所以可以访问 .BOT_TOKEN
    bot = Bot(token=config.BOT_TOKEN.get_secret_value())
    
    # 3. 初始化 Dispatcher
    dp = Dispatcher(storage=MemoryStorage())

    # 4. 注册路由 (注意顺序！)
    # 先加载 creator (/newquiz)，防止被 common 拦截
    dp.include_router(creator.router)

    # ✅ 去掉注释，启用做题功能
    dp.include_router(attempt.router) 

    dp.include_router(common.router)

    logging.info("Starting Bot...")
    
    # 删除 Webhook 防止冲突
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")