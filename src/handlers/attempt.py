# src/handlers/attempt.py
import json
from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

# 引入数据库和模型
from src.database import get_db
from src.models import QuizSet, Question

router = Router()

# 定义做题的状态
class QuizAttempt(StatesGroup):
    in_progress = State()  # 正在做题中

# ==========================================
# 1. 入口：处理深层链接 /start <quiz_id>
# ==========================================
@router.message(CommandStart(deep_link=True))
async def cmd_start_quiz(message: Message, command: CommandObject, state: FSMContext):
    quiz_id = command.args  # 获取链接后面的参数 (UUID)
    
    async for session in get_db():
        # 1. 找试卷
        result = await session.execute(select(QuizSet).where(QuizSet.id == quiz_id))
        quiz = result.scalar_one_or_none()
        
        if not quiz:
            await message.answer("⚠️ 找不到这张试卷，可能已被删除。")
            return

        # 2. 找题目 (按 ID 排序)
        q_result = await session.execute(
            select(Question).where(Question.quiz_set_id == quiz_id).order_by(Question.id)
        )
        questions = q_result.scalars().all()
        
        if not questions:
            await message.answer("⚠️ 这张试卷里没有题目！")
            return

        # 3. 初始化状态
        # 我们只存题目的 ID 列表，节省内存
        q_ids = [q.id for q in questions]
        
        # 将必要信息存入 FSM 状态储存
        await state.update_data(
            quiz_title=quiz.name,
            q_ids=q_ids,
            current_index=0,
            score=0,
            total=len(q_ids)
        )
        await state.set_state(QuizAttempt.in_progress)

        # 4. 发送第一题
        await message.answer(f"📝 **开始答题：{quiz.name}**\n共 {len(q_ids)} 题", parse_mode="Markdown")
        await send_question(message, state, questions[0])

# ==========================================
# 2. 核心逻辑：发送题目
# ==========================================
async def send_question(message: Message, state: FSMContext, question: Question):
    data = await state.get_data()
    index = data['current_index']
    total = data['total']

    # 构建选项按钮
    # options_data 是一个列表: [{"id": "A", "text": "xxx"}, ...]
    buttons = []
    
    # 兼容性处理：有时候数据库读出来可能是字符串
    options = question.options_data
    if isinstance(options, str):
        options = json.loads(options)
        
    # 构造 Inline 键盘 (每行一个选项)
    for opt in options:
        # callback_data 格式: ans:选项ID
        buttons.append([
            InlineKeyboardButton(text=f"{opt['id']}. {opt['text']}", callback_data=f"ans:{opt['id']}")
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    question_text = f"**第 {index + 1}/{total} 题**"
    
    # 根据类型发送 (图片或纯文字)
    if question.content_type == 'photo':
        await message.answer_photo(
            photo=question.content_data,
            caption=question_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        # 纯文字
        text_content = f"{question_text}\n\n{question.content_data}"
        await message.answer(text_content, reply_markup=keyboard, parse_mode="Markdown")

# ==========================================
# 3. 交互：处理用户点击选项
# ==========================================
@router.callback_query(QuizAttempt.in_progress, F.data.startswith("ans:"))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    user_choice = callback.data.split(":")[1] # 获取 'A', 'B' 等
    
    data = await state.get_data()
    current_index = data['current_index']
    q_ids = data['q_ids']
    
    # 获取当前题目信息进行对比
    current_q_id = q_ids[current_index]
    
    # 查库获取正确答案和解析
    async for session in get_db():
        q_result = await session.execute(select(Question).where(Question.id == current_q_id))
        question = q_result.scalar_one()
        
        is_correct = (user_choice == question.correct_option)
        correct_opt = question.correct_option
        hint = question.hint or "无"

    # 计分逻辑
    if is_correct:
        await state.update_data(score=data['score'] + 1)
        feedback = f"✅ **回答正确!**"
    else:
        feedback = f"❌ **回答错误!**\n正确答案是: **{correct_opt}**"
    
    # 如果有解析，加上解析
    if hint and hint != "无":
        feedback += f"\n💡 解析: {hint}"

    # 弹窗提示结果 (show_alert=True 会有弹窗，False 只是上方浮动提示，推荐 True)
    await callback.answer(feedback, show_alert=True)
    
    # 准备下一题
    next_index = current_index + 1
    
    if next_index < data['total']:
        # 还有下一题 -> 更新 index -> 发送下一题
        await state.update_data(current_index=next_index)
        
        async for session in get_db():
            next_q_result = await session.execute(select(Question).where(Question.id == q_ids[next_index]))
            next_q = next_q_result.scalar_one()
            # 发送下一题 (注意：这里用 callback.message 继续在当前对话发送)
            await send_question(callback.message, state, next_q)
    else:
        # 全部做完 -> 结算
        # 重新获取一次最新分数
        final_data = await state.get_data()
        final_score = final_data['score']
        total = data['total']
        percentage = int((final_score / total) * 100)
        
        result_text = (
            f"🏁 **测试结束!**\n\n"
            f"📊 你的得分: **{final_score} / {total}**\n"
            f"📈 正确率: **{percentage}%**"
        )
        await callback.message.answer(result_text, parse_mode="Markdown")
        await state.clear() # 清除状态，结束会话