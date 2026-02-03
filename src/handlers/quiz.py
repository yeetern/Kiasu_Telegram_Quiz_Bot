"""
General Practice Handler - Project Kancil
Provides a global random practice mode (/practice) outside of specific quiz sets.
Focuses on low-pressure, instructional feedback for general revision.
"""

import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, func

from src.database import get_db
from src.models import Question

router = Router()

# ==========================================
# 1. State Definition
# ==========================================
class GeneralQuizStates(StatesGroup):
    """FSM states for the general practice flow."""
    waiting_for_answer = State()

# ==========================================
# 2. Random Question Logic (/practice)
# ==========================================
@router.message(Command("practice"))
async def cmd_random_practice(message: types.Message, state: FSMContext):
    """
    Fetches a random active question from the entire database 
    and presents it to the student.
    """
    async for session in get_db():
        # Fetch 1 random active question
        # Note: func.random() is efficient for MVP-scale databases
        result = await session.execute(
            select(Question).where(Question.is_active == True).order_by(func.random()).limit(1)
        )
        question = result.scalars().first()

        if not question:
            return await message.answer(
                "🚧 **Question Bank Empty**\n\n"
                "We are currently updating our database. Please check back later!"
            )

        # Build A/B/C/D MCQ Keyboard
        builder = InlineKeyboardBuilder()
        for option in ["A", "B", "C", "D"]:
            builder.button(text=option, callback_data=f"gen_ans:{option}")
        builder.adjust(2) 

        # Delivery logic with fallback for missing images
        header = (
            f"📚 **Subject:** {question.subject}\n"
            f"🔖 **Topic:** {question.topic}\n\n"
            "Choose the correct answer:"
        )

        try:
            # Try sending as photo if image_file_id exists
            if question.image_file_id:
                await message.answer_photo(
                    photo=question.image_file_id,
                    caption=header,
                    reply_markup=builder.as_markup(),
                    parse_mode="Markdown"
                )
            else:
                # Fallback to text if no image is defined
                await message.answer(
                    text=f"{header}\n\n*(No image provided)*",
                    reply_markup=builder.as_markup(),
                    parse_mode="Markdown"
                )
        except Exception as e:
            logging.error(f"Failed to send practice question: {e}")
            await message.answer("⚠️ Could not load question content. Please try again.")

        # Save question context to FSM
        await state.update_data(question_id=question.id)
        await state.set_state(GeneralQuizStates.waiting_for_answer)
        break

# ==========================================
# 3. Answer Evaluation & Instructional Feedback
# ==========================================
@router.callback_query(GeneralQuizStates.waiting_for_answer, F.data.startswith("gen_ans:"))
async def handle_general_answer(callback: types.CallbackQuery, state: FSMContext):
    """
    Evaluates the choice and provides detailed textbook references 
    to turn the mistake into a learning event.
    """
    user_choice = callback.data.split(":")[1]
    data = await state.get_data()
    question_id = data.get("question_id")

    if not question_id:
        await callback.answer("Session expired. Start over with /practice.")
        await state.clear()
        return

    async for session in get_db():
        result = await session.execute(select(Question).where(Question.id == question_id))
        question = result.scalars().first()

        if not question:
            await callback.answer("Error: Question details missing.")
            await state.clear()
            return

        is_correct = (user_choice == question.correct_option)
        
        # Build Feedback Content
        if is_correct:
            response_text = (
                f"✅ **Correct!**\n"
                f"━━━━━━━━━━━━━━\n"
                f"You chose **{user_choice}**. Great job on maintaining your accuracy! 🐿️"
            )
        else:
            ref = question.reference_data or {}
            response_text = (
                f"❌ **Keep learning!**\n"
                f"━━━━━━━━━━━━━━\n"
                f"Your choice: {user_choice}\n"
                f"Correct answer: **{question.correct_option}**\n\n"
                f"📖 **Instructional Reference:**\n"
                f"• Textbook: _{ref.get('textbook', 'N/A')}_\n"
                f"• Page: {ref.get('page', 'N/A')}\n\n"
                f"💡 **Note:** {ref.get('explanation', 'Review this concept to master it.')}"
            )

        # Notify user and remove buttons to prevent multiple attempts
        await callback.message.answer(response_text, parse_mode="Markdown")
        await callback.message.edit_reply_markup(reply_markup=None)
        
        await callback.answer() # Stop button loading animation
        await state.clear() # End practice session
        break