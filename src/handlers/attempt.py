# src/handlers/attempt.py
from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from src.database import get_db
from src.models import QuizSet, Question

router = Router()

# ==========================
# 1. 启动试卷 (Deep Linking)
# ==========================
@router.message(CommandStart(deep_link=True))
async def cmd_start_quiz(message: Message, command: CommandObject, state: FSMContext):
    """
    当用户点击链接 t.me/bot?start=quiz_id 时触发
    """
    quiz_id = command.args # 获取 URL 中的参数
    
    async for session in get_db():
        # 1. 检查试卷是否存在
        result = await session.execute(select(QuizSet).where(QuizSet.id == quiz_id))
        quiz = result.scalars().first()
        
        if not quiz:
            await message.answer("❌ 找不到该试卷，可能已被删除或链接无效。")
            return

        # 2. 获取该试卷所有题目的 ID (按 ID 排序)
        # 直接查 Question 表比较稳妥，避免异步延迟加载问题
        q_result = await session.execute(
            select(Question.id).where(Question.quiz_set_id == quiz_id).order_by(Question.id)
        )
        question_ids = q_result.scalars().all()
        
        if not question_ids:
            await message.answer("⚠️ 这套试卷似乎还没有题目。")
            return
            
        # 3. 初始化做题状态
        await state.update_data(
            quiz_id=quiz_id,
            q_ids=question_ids,  # 题目ID列表
            current_index=0,     # 当前第几题 (索引)
            score=0              # 当前得分
        )
        
        await message.answer(
            f"📝 **准备开始: {quiz.name}**\n"
            f"共 {len(question_ids)} 题。\n\n"
            "正在加载第 1 题...",
            parse_mode="Markdown"
        )
        
        # 发送第一题
        await send_current_question(message, state, session)
        break


# ==========================
# 2. 发送当前题目的辅助函数
# ==========================
async def send_current_question(message_or_callback, state: FSMContext, session):
    data = await state.get_data()
    index = data['current_index']
    q_ids = data['q_ids']
    
    # 检查是否已做完
    if index >= len(q_ids):
        score = data['score']
        total = len(q_ids)
        percentage = int((score / total) * 100)
        
        # 简单的评语
        comment = "太棒了！🎉" if percentage >= 80 else "继续加油！💪"
        
        text = (
            f"🏁 **试卷完成！**\n\n"
            f"✅ 得分: {score} / {total}\n"
            f"📊 正确率: {percentage}%\n\n"
            f"{comment}"
        )
        
        # 如果是 callback (点击选项触发的)，用 edit_text；如果是 message (刚开始)，用 answer
        if isinstance(message_or_callback, CallbackQuery):
            await message_or_callback.message.answer(text, parse_mode="Markdown")
        else:
            await message_or_callback.answer(text, parse_mode="Markdown")
            
        await state.clear()
        return

    # 获取题目详情
    q_id = q_ids[index]
    result = await session.execute(select(Question).where(Question.id == q_id))
    question = result.scalars().first()
    
    if not question:
        await message_or_callback.answer("题目加载失败，跳过。")
        await state.update_data(current_index=index + 1)
        await send_current_question(message_or_callback, state, session)
        return

    # 构建选项按钮 (Inline Keyboard)
    buttons = []
    # options_data 结构: [{"id":"A", "text":"..."}, {"id":"B", "text":"..."}]
    # 每行放 1 个选项，防止太长显示不下
    for opt in question.options_data:
        btn_text = f"{opt['id']}. {opt['text']}"
        # callback_data 格式: ans:题目ID:用户选的ID
        c_data = f"ans:{question.id}:{opt['id']}" 
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=c_data)])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    caption_text = f"📋 **第 {index + 1} / {len(q_ids)} 题**"
    
    # 根据是 message 还是 callback 决定发送方式
    # 这里为了简单，统一发送新消息 (旧消息保留作为记录)
    target = message_or_callback.message if isinstance(message_or_callback, CallbackQuery) else message_or_callback
    
    if question.content_type == 'photo':
        await target.answer_photo(
            photo=question.content_data,
            caption=caption_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        await target.answer(
            text=f"{caption_text}\n\n{question.content_data}",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )


# ==========================
# 3. 处理答案点击
# ==========================
@router.callback_query(F.data.startswith("ans:"))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    # 解析数据: ans:123:A
    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer("Error")
        return
        
    _, q_id_str, user_choice = parts
    q_id = int(q_id_str)
    
    async for session in get_db():
        # 查答案
        result = await session.execute(select(Question).where(Question.id == q_id))
        question = result.scalars().first()
        
        data = await state.get_data()
        current_score = data.get('score', 0)
        
        # 判断对错
        is_correct = (user_choice == question.correct_option)
        
        if is_correct:
            current_score += 1
            feedback = f"✅ **正确！**\n选了 {user_choice}"
        else:
            feedback = (
                f"❌ **错误** (你选了 {user_choice})\n"
                f"🔑 正确答案: **{question.correct_option}**\n\n"
                f"💡 **解析/Hint**: {question.hint or '暂无'}"
            )
            
        # 弹窗提示结果 (Toast Notification)
        # await callback.answer(feedback, show_alert=True) # 如果想要弹窗可以用这个
        await callback.answer() # 消除加载转圈
        
        # 发送反馈消息
        await callback.message.reply(feedback, parse_mode="Markdown")
        
        # 更新状态
        await state.update_data(
            score=current_score,
            current_index=data['current_index'] + 1
        )
        
        # 发送下一题
        await send_current_question(callback, state, session)
        break