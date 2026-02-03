# src/handlers/common.py
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router()

# 只保留一个简单的 /start 命令，删除所有 echo 或者是 F.photo 的代码
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 你好！我是 Kiasu Quiz Bot。\n\n"
        "我是用来制作和练习题目的。\n"
        "👉 创建试卷: /newquiz"
    )