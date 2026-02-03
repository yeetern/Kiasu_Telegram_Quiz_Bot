"""
Common Handlers - Project Kancil
Handles basic commands like /start and general bot information.
"""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Handles the /start command.
    
    Note: Deep links (t.me/bot?start=xyz) carry arguments. 
    If arguments are present, this handler yields to the attempt handler 
    to initiate a quiz session.
    """
    args = message.text.split()
    
    # If arguments exist, we assume it's a deep link (quiz_id)
    # The specialized handler in attempt.py will capture this via CommandStart(deep_link=True)
    if len(args) > 1:
        return 

    # Default welcome message for educators or new users
    welcome_text = (
        "👋 **Welcome to Project Kancil!**\n\n"
        "I am a failure-safe learning bot designed for private practice.\n\n"
        "🛠 **For Educators:**\n"
        "Use /newquiz to create a new instructional practice set.\n\n"
        "📖 **For Students:**\n"
        "Please use the specific link provided by your teacher to start a quiz."
    )
    
    await message.answer(welcome_text, parse_mode="Markdown")