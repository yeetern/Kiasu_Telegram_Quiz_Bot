"""
Quiz Attempt Handler - Project Kancil
Improved to support persistent session saving and mistake review logic.
"""

import logging
from aiogram import Router, F, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

from src.database import get_db
from src.models import QuizSet, Question, QuizSession

router = Router()

class QuizAttempt(StatesGroup):
    in_progress = State()

# ==========================================
# 1. Start Quiz & Session Creation
# ==========================================
@router.message(CommandStart(deep_link=True))
async def start_quiz(message: Message, command: CommandObject, state: FSMContext):
    quiz_id = command.args
    async for session in get_db():
        res = await session.execute(select(QuizSet).where(QuizSet.id == quiz_id))
        quiz = res.scalar_one_or_none()
        
        if not quiz:
            return await message.answer("⚠️ This quiz link is no longer active.")

        q_res = await session.execute(
            select(Question).where(Question.quiz_set_id == quiz_id).order_by(Question.id)
        )
        questions = q_res.scalars().all()
        
        if not questions:
            return await message.answer("⚠️ This quiz currently has no questions.")
        
        # PERSISTENCE: Create a record in quiz_sessions immediately
        new_session = QuizSession(
            user_id=message.from_user.id,
            subject=quiz.name,
            total_count=len(questions),
            question_ids=[q.id for q in questions],
            user_answers={} # Initialize empty dict
        )
        session.add(new_session)
        await session.commit()

        await state.update_data(
            session_id=new_session.id, # Store DB ID for later updates
            q_ids=[q.id for q in questions], 
            current_index=0, 
            score=0, 
            total=len(questions),
            user_answers={} 
        )
        await state.set_state(QuizAttempt.in_progress)
        
        await message.answer(
            f"📖 **Quiz Started: {quiz.name}**\n"
            f"━━━━━━━━━━━━━━\n"
            f"Total Questions: {len(questions)}\n"
            "Take your time. Mistakes are part of learning! ✨"
        )
        await send_current_question(message, state, questions[0])
        break

# ==========================================
# 2. Question Delivery Logic
# ==========================================
async def send_current_question(message: Message, state: FSMContext, question: Question):
    data = await state.get_data()
    buttons = [
        InlineKeyboardButton(text=opt['id'], callback_data=f"ans:{opt['id']}") 
        for opt in question.options_data
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=[buttons])
    title = f"Question {data['current_index'] + 1} of {data['total']}"
    
    if question.content_type == 'photo':
        await message.answer_photo(photo=question.content_data, caption=f"📝 **{title}**", reply_markup=kb)
    else:
        await message.answer(text=f"📝 **{title}**\n\n{question.content_data}", reply_markup=kb)

# ==========================================
# 3. Answer Handling & Feedback
# ==========================================
@router.callback_query(QuizAttempt.in_progress, F.data.startswith("ans:"))
async def handle_ans(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split(":")[1]
    data = await state.get_data()
    
    async for session in get_db():
        q_id = data['q_ids'][data['current_index']]
        q_res = await session.execute(select(Question).where(Question.id == q_id))
        q = q_res.scalar_one()
        
        is_correct = (choice == q.correct_option)
        
        # Track answers locally in FSM
        new_answers = data.get('user_answers', {})
        new_answers[str(q_id)] = choice
        
        new_score = data['score'] + 1 if is_correct else data['score']
        await state.update_data(score=new_score, user_answers=new_answers)
        
        status_emoji = "✅" if is_correct else "❌"
        feedback = (
            f"━━━━━━━━━━━━━━\n"
            f"{status_emoji} **{'Correct!' if is_correct else 'Keep going!'}**\n"
            f"Your choice: **{choice}** | Correct: **{q.correct_option}**"
        )
        if q.hint:
            feedback += f"\n\n💡 **Instructional Reference:**\n{q.hint}"
        
        await callback.answer()
        
        if callback.message.photo:
            await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n{feedback}")
        else:
            await callback.message.edit_text(text=f"{callback.message.text}\n\n{feedback}")
        
        next_kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Continue ➡️", callback_data="go_next")
        ]])
        await callback.message.answer("Tap continue to proceed:", reply_markup=next_kb)
        break

# ==========================================
# 4. Finalizing & Review Trigger
# ==========================================
@router.callback_query(QuizAttempt.in_progress, F.data == "go_next")
async def go_next(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_idx = data['current_index'] + 1
    
    if new_idx < data['total']:
        await state.update_data(current_index=new_idx)
        async for session in get_db():
            q_res = await session.execute(select(Question).where(Question.id == data['q_ids'][new_idx]))
            await send_current_question(callback.message, state, q_res.scalar_one())
            break
    else:
        # END OF QUIZ: Save results to database
        async for session in get_db():
            db_sess = await session.get(QuizSession, data['session_id'])
            if db_sess:
                db_sess.correct_count = data['score']
                db_sess.user_answers = data['user_answers']
                db_sess.is_completed = True
                await session.commit()
        
        # Summary with Review Button
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Review Mistakes", callback_data=f"rev_mode:{data['session_id']}")],
            [InlineKeyboardButton(text="🔙 Back to Home", callback_data="home")]
        ])

        summary = (
            "🏁 **Practice Session Complete!**\n"
            "━━━━━━━━━━━━━━\n"
            f"📊 Final Score: **{data['score']}/{data['total']}**\n\n"
            "Mistakes are just data for improvement. Review them below! 🐿️"
        )
        await callback.message.answer(summary, reply_markup=kb)
        await state.clear()
    
    await callback.answer()