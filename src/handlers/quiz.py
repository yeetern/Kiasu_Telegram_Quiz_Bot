from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, func

from src.database import get_db
from src.models import Question

router = Router()

# === 1. 定义状态机 ===
class QuizStates(StatesGroup):
    waiting_for_answer = State()  # 机器人发题后，进入此状态，等待用户点击

# === 2. 出题逻辑 (/practice) ===
@router.message(Command("practice"))
async def cmd_practice(message: types.Message, state: FSMContext):
    # 获取数据库会话
    async for session in get_db():
        # 随机获取一道题 (Order by Random)
        # 注意：数据量大时 Random 效率低，MVP 阶段在大马完全够用
        result = await session.execute(
            select(Question).where(Question.is_active == True).order_by(func.random()).limit(1)
        )
        question = result.scalars().first()

        if not question:
            await message.answer("🚧 题库目前是空的，请联系管理员添加题目。")
            return

        # 构建选项按钮 (Inline Keyboard)
        builder = InlineKeyboardBuilder()
        for option in ["A", "B", "C", "D"]:
            # callback_data 格式: "answer:选项" (例如 "answer:A")
            builder.button(text=option, callback_data=f"answer:{option}")
        builder.adjust(2) # 每行显示2个按钮 (2x2 布局)

        # 发送题目
        # ⚠️ 容错处理：如果 Seeder 里的 file_id 是假的，send_photo 会报错
        # 这里我们做一个 fallback，如果图片发不出去，就发纯文字
        try:
            await message.answer_photo(
                photo=question.image_file_id,
                caption=f"📚 **Subject:** {question.subject}\n"
                        f"🔖 **Topic:** {question.topic}\n\n"
                        f"请选择正确答案：",
                reply_markup=builder.as_markup(),
                parse_mode="Markdown"
            )
        except Exception as e:
            # 图片 ID 无效时的降级方案
            await message.answer(
                text=f"📚 **Subject:** {question.subject}\n"
                     f"🔖 **Topic:** {question.topic}\n\n"
                     f"*(Image unavailable in MVP)*\n\n"
                     f"请选择正确答案：",
                reply_markup=builder.as_markup(),
                parse_mode="Markdown"
            )

        # === 关键步骤 ===
        # 将 question.id 存入 FSM，这样在用户点击按钮时，我们知道他在答哪道题
        await state.update_data(question_id=question.id)
        # 切换状态：等待用户点击
        await state.set_state(QuizStates.waiting_for_answer)

# === 3. 判题逻辑 (Callback Handler) ===
@router.callback_query(QuizStates.waiting_for_answer, F.data.startswith("answer:"))
async def handle_answer(callback: types.CallbackQuery, state: FSMContext):
    # 解析用户选择 "answer:B" -> "B"
    user_choice = callback.data.split(":")[1]
    
    # 获取 FSM 中存的 question_id
    data = await state.get_data()
    question_id = data.get("question_id")

    if not question_id:
        await callback.answer("Session expired. Please try /practice again.")
        await state.clear()
        return

    # 查询数据库比对答案
    async for session in get_db():
        result = await session.execute(select(Question).where(Question.id == question_id))
        question = result.scalars().first()

        if not question:
            await callback.answer("Error: Question not found.")
            await state.clear()
            return

        is_correct = (user_choice == question.correct_option)
        
        # === 构建反馈内容 (Feedback Loop) ===
        if is_correct:
            response_text = (
                f"✅ **Correct!**\n\n"
                f"You chose **{user_choice}**."
            )
        else:
            # 这里的 reference_data 是个 JSON，我们取出里面的信息
            ref = question.reference_data
            response_text = (
                f"❌ **Incorrect.**\n\n"
                f"Your answer: {user_choice}\n"
                f"Correct answer: **{question.correct_option}**\n\n"
                f"📖 **Reference:**\n"
                f"Textbook: _{ref.get('textbook', 'N/A')}_\n"
                f"Page: {ref.get('page', 'N/A')}\n"
                f"💡 **Note:** {ref.get('explanation', '')}"
            )

        # 发送反馈 (Edit the caption or send new message? 私聊通常发新消息比较明显)
        await callback.message.answer(response_text, parse_mode="Markdown")
        
        # 移除原消息的按钮 (防止重复点击)
        await callback.message.edit_reply_markup(reply_markup=None)
        
        # 结束当前状态
        await callback.answer() # 停止按钮转圈
        await state.clear()

