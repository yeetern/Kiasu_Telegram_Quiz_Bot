# src/handlers/creator.py
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, 
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardRemove, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    CallbackQuery
)
from aiogram.fsm.context import FSMContext

from src.states import QuizCreation
from src.database import get_db
from src.models import QuizSet, Question

router = Router()

# ==========================
# 1. 开始创建 (/newquiz)
# ==========================
@router.message(Command("newquiz"))
async def cmd_newquiz(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🛠 **快速创建试卷**\n\n"
        "1️⃣ 请输入试卷名称 (例如: Physics Ch1):",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(QuizCreation.naming)


# ==========================
# 2. 接收命名 -> 创建 QuizSet
# ==========================
@router.message(QuizCreation.naming)
async def process_name(message: Message, state: FSMContext):
    quiz_name = message.text.strip()
    
    try:
        async for session in get_db():
            new_quiz = QuizSet(name=quiz_name, creator_id=message.from_user.id)
            session.add(new_quiz)
            await session.commit()
            await session.refresh(new_quiz)
            
            await state.update_data(quiz_id=new_quiz.id, question_count=0)
            
            await message.answer(
                f"✅ 试卷 **{quiz_name}** 已建立！\n\n"
                "2️⃣ 请发送 **第 1 题** 的内容 (图片或文字):"
            )
            await state.set_state(QuizCreation.waiting_for_content)
            break
    except Exception as e:
        await message.answer(f"❌ 数据库错误: {str(e)}")


# ==========================
# 3. 接收题目内容 -> 询问 Hint
# ==========================
@router.message(QuizCreation.waiting_for_content)
async def process_content(message: Message, state: FSMContext):
    content_type = "text"
    content_data = ""

    if message.photo:
        content_type = "photo"
        content_data = message.photo[-1].file_id
    elif message.text:
        content_type = "text"
        content_data = message.text
    else:
        await message.answer("⚠️ 请发送图片或文字作为题目。")
        return

    await state.update_data(temp_type=content_type, temp_data=content_data)
    
    # 【修改点】改用 Inline 按钮，保证用户一定能看到
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏭ 跳过 (无解析)", callback_data="hint:skip")]
        ]
    )
    
    await message.answer(
        "👌 题目已接收。\n\n"
        "3️⃣ 请发送 **解析/Hint** (文字):\n"
        "或者点击下方按钮跳过。",
        reply_markup=kb
    )
    await state.set_state(QuizCreation.waiting_for_hint)


# ==========================
# 4. 处理 Hint (两种情况：发文字 或 点跳过)
# ==========================

# 情况 A: 用户点击了 "跳过" 按钮
@router.callback_query(QuizCreation.waiting_for_hint, F.data == "hint:skip")
async def skip_hint(callback: CallbackQuery, state: FSMContext):
    # 消除加载动画
    await callback.answer()
    # 更新 Hint 为空
    await state.update_data(temp_hint=None)
    await callback.message.edit_text("✅ Hint: (无)")
    # 进入下一步
    await ask_for_correct_option(callback.message, state)

# 情况 B: 用户直接发了文字
@router.message(QuizCreation.waiting_for_hint)
async def process_hint_text(message: Message, state: FSMContext):
    await state.update_data(temp_hint=message.text)
    await message.answer("✅ Hint 已记录。")
    # 进入下一步
    await ask_for_correct_option(message, state)


# --- 辅助函数：显示 A B C D 按钮 ---
async def ask_for_correct_option(message: Message, state: FSMContext):
    buttons = [
        [
            InlineKeyboardButton(text="A", callback_data="set_ans:A"),
            InlineKeyboardButton(text="B", callback_data="set_ans:B"),
            InlineKeyboardButton(text="C", callback_data="set_ans:C"),
            InlineKeyboardButton(text="D", callback_data="set_ans:D"),
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(
        "4️⃣ **请点击正确答案：**",
        reply_markup=kb
    )
    await state.set_state(QuizCreation.waiting_for_poll)


# ==========================
# 5. 处理答案点击 (关键修正：增加错误捕捉)
# ==========================
@router.callback_query(F.data.startswith("set_ans:"))
async def process_button_click(callback: CallbackQuery, state: FSMContext):
    correct_option = callback.data.split(":")[1]
    await callback.answer(f"选择了: {correct_option}") # 先给反馈，防止转圈
    
    options_data = [
        {"id": "A", "text": "Option A"},
        {"id": "B", "text": "Option B"},
        {"id": "C", "text": "Option C"},
        {"id": "D", "text": "Option D"}
    ]
    
    data = await state.get_data()
    
    try:
        async for session in get_db():
            new_question = Question(
                quiz_set_id=data['quiz_id'],
                content_type=data['temp_type'],
                content_data=data['temp_data'],
                hint=data['temp_hint'],
                options_data=options_data,
                correct_option=correct_option
            )
            session.add(new_question)
            await session.commit()
            
            new_count = data['question_count'] + 1
            await state.update_data(question_count=new_count)
            
            # 修改原来的消息，去掉按钮
            await callback.message.edit_text(
                f"✅ **第 {new_count} 题已保存！**\n"
                f"正确答案: **{correct_option}**"
            )
            
            # 下一步键盘
            kb = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="下一题"), KeyboardButton(text="结束创建")]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            
            await callback.message.answer("👇 请选择下一步：", reply_markup=kb)
            await state.set_state(QuizCreation.confirm_next)
            break

    except Exception as e:
        # 如果报错，打印出来
        print(f"ERROR saving question: {e}")
        await callback.message.answer(f"❌ 保存失败，数据库错误: {e}")


# ==========================
# 6. 下一题 / 结束
# ==========================
@router.message(QuizCreation.confirm_next, F.text == "下一题")
async def loop_next_question(message: Message, state: FSMContext):
    await message.answer(
        "👉 请发送 **下一题** 的内容 (图/文)：",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(QuizCreation.waiting_for_content)


@router.message(QuizCreation.confirm_next, F.text == "结束创建")
async def finish_quiz_creation(message: Message, state: FSMContext):
    data = await state.get_data()
    quiz_id = data['quiz_id']
    count = data['question_count']
    bot_info = await message.bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={quiz_id}"
    
    await message.answer(
        f"🎉 **试卷制作完成！**\n\n"
        f"🆔 ID: `{quiz_id}`\n"
        f"🔢 题目数: {count}\n"
        f"🔗 {link}",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()