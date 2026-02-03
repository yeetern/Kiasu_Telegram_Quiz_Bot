"""
Quiz Attempt Handler - Project Kancil
Manages the student practice experience, providing instructional feedback 
and navigating through questions in a private, low-pressure environment.
"""

import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

from src.database import get_db
from src.models import QuizSet, Question

router = Router()

class QuizAttempt(StatesGroup):
    """FSM states for the quiz-taking process."""
    in_progress = State()

# ==========================================
# 1. Start Quiz via Deep Link
# ==========================================
@router.message(CommandStart(deep_link=True))
async def start_quiz(message: Message, command: CommandObject, state: FSMContext):
    """
    Handles deep links (e.g., t.me/bot?start=123).
    Fetches the quiz and prepares the session.
    """
    quiz_id = command.args
    async for session in get_db():
        # Fetch the Quiz Set
        res = await session.execute(select(QuizSet).where(QuizSet.id == quiz_id))
        quiz = res.scalar_one_or_none()
        
        if not quiz:
            return await message.answer("⚠️ This quiz link is no longer active.")

        # Fetch all questions for this quiz
        q_res = await session.execute(
            select(Question)
            .where(Question.quiz_set_id == quiz_id)
            .order_by(Question.id)
        )
        questions = q_res.scalars().all()
        
        if not questions:
            return await message.answer("⚠️ This quiz currently has no questions.")
        
        # Initialize session data
        await state.update_data(
            q_ids=[q.id for q in questions], 
            current_index=0, 
            score=0, 
            total=len(questions)
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
    """Sends the current question (photo or text) with A/B/C/D options."""
    data = await state.get_data()
    
    # Horizontal layout for MCQ options
    buttons = [
        InlineKeyboardButton(text=opt['id'], callback_data=f"ans:{opt['id']}") 
        for opt in question.options_data
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=[buttons])
    
    title = f"Question {data['current_index'] + 1} of {data['total']}"
    
    if question.content_type == 'photo':
        await message.answer_photo(
            photo=question.content_data, 
            caption=f"📝 **{title}**", 
            reply_markup=kb
        )
    else:
        await message.answer(
            f"📝 **{title}**\n\n{question.content_data}", 
            reply_markup=kb
        )

# ==========================================
# 3. Answer Handling & Feedback
# ==========================================
@router.callback_query(QuizAttempt.in_progress, F.data.startswith("ans:"))
async def handle_ans(callback: CallbackQuery, state: FSMContext):
    """Evaluates the answer and provides instructional feedback."""
    choice = callback.data.split(":")[1]
    data = await state.get_data()
    
    async for session in get_db():
        q_res = await session.execute(
            select(Question).where(Question.id == data['q_ids'][data['current_index']])
        )
        q = q_res.scalar_one()
        
        is_correct = (choice == q.correct_option)
        if is_correct:
            await state.update_data(score=data['score'] + 1)
        
        # Build Pedagogical Feedback
        status_emoji = "✅" if is_correct else "❌"
        status_text = "Correct!" if is_correct else "Keep going!"
        
        feedback = (
            f"━━━━━━━━━━━━━━\n"
            f"{status_emoji} **{status_text}**\n"
            f"Your choice: **{choice}** | Correct: **{q.correct_option}**"
        )
        
        if q.hint:
            feedback += f"\n\n💡 **Instructional Reference:**\n{q.hint}"
        
        await callback.answer()
        
        # Update current message to show result
        if callback.message.photo:
            await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n{feedback}")
        else:
            await callback.message.edit_text(text=f"{callback.message.text}\n\n{feedback}")
        
        # Next Step Button
        next_kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Continue ➡️", callback_data="go_next")
        ]])
        await callback.message.answer("Read the feedback above, then tap continue:", reply_markup=next_kb)
        break

# ==========================================
# 4. Navigation & Results
# ==========================================
@router.callback_query(QuizAttempt.in_progress, F.data == "go_next")
async def go_next(callback: CallbackQuery, state: FSMContext):
    """Moves to the next question or shows the final result summary."""
    data = await state.get_data()
    new_idx = data['current_index'] + 1
    
    if new_idx < data['total']:
        await state.update_data(current_index=new_idx)
        async for session in get_db():
            q_res = await session.execute(
                select(Question).where(Question.id == data['q_ids'][new_idx])
            )
            await send_current_question(callback.message, state, q_res.scalar_one())
            break
    else:
        # Final Summary
        score = data['score']
        total = data['total']
        accuracy = int(score / total * 100) if total > 0 else 0
        
        summary = (
            "🏁 **Practice Session Complete!**\n"
            "━━━━━━━━━━━━━━\n"
            f"📊 Final Score: **{score}/{total}**\n"
            f"📈 Accuracy: **{accuracy}%**\n\n"
            "Great job on finishing your practice. Review your notes for any questions you missed! 🐿️"
        )
        await callback.message.answer(summary)
        await state.clear()
    
    await callback.answer()