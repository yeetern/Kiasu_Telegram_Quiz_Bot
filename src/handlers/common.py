from aiogram import Router, types, F  # <--- 关键！一定要加上 F
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user_name = message.from_user.first_name
    await message.answer(
        f"👋 Hello, {user_name}!\n\n"
        "我是 **Kiasu Quiz Bot** (Project Kancil)。\n"
        "这里可以让你安全地刷题，不用担心答错。\n\n"
        "目前系统正在构建中... 🚧"
    )

# === 临时添加的 ID 获取器 ===
@router.message(F.photo)
async def handle_photo_upload(message: types.Message):
    # 获取最大尺寸图片的 ID
    file_id = message.photo[-1].file_id
    await message.answer(f"📸 Image File ID:\n`{file_id}`", parse_mode="Markdown")
    print(f"!!! NEW FILE ID: {file_id}")