"""
Main Entry Point - Project Kancil
Initializes database connections, configures the AIOGram dispatcher, 
and manages the bot's polling lifecycle.
"""

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Configuration and Database
from src.config import config 
from src.database import init_db

# Handlers
from src.handlers import creator, common, attempt 

async def main():
    # 1. Initialize Database
    # Ensures tables are created and the async engine is ready.
    await init_db()
    
    # 2. Initialize Bot 
    # Using DefaultBotProperties for consistent Markdown rendering.
    bot = Bot(
        token=config.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    # 3. Initialize Dispatcher
    # We use MemoryStorage for the MVP. For scaling, this can be swapped for Redis.
    dp = Dispatcher(storage=MemoryStorage())

    # 4. Register Routers (Order is critical!)
    # Higher priority routers are registered first.
    
    # Priority 1: Quiz Creation (Educator Flow)
    dp.include_router(creator.router)

    # Priority 2: Quiz Attempt (Student Flow - handles deep links via /start)
    dp.include_router(attempt.router) 

    # Priority 3: Common (Global commands like general /start or /help)
    # This acts as a fallback for start commands without arguments.
    dp.include_router(common.router)

    logging.info("Project Kancil is online. Polling started...")
    
    # Remove any pending updates from Telegram servers to prevent spam on startup
    await bot.delete_webhook(drop_pending_updates=True)
    
    # 5. Execution
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Standard logging configuration for production-ready output
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped successfully. Goodbye!")