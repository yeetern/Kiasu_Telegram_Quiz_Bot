"""
Quiz Creation Handler - Project Kancil
Manages the educator's workflow for creating quizzes, handling image/text 
content, instructional hints, and persisting data to the database.
"""

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

# ==========================================
# 1. Entry Point: /newquiz
# ==========================================
@router.message(Command("newquiz"))
async def cmd_newquiz(message: Message, state: FSMContext):
    """
    Starts the quiz creation wizard. 
    Clears any existing state and requests the quiz name.
    """
    await state.clear()
    welcome_text = (
        "🚀 **Start New Quiz Creation**\n"
        "━━━━━━━━━━━━━━\n"
        "Step 1: Please enter a **Name** for this quiz.\n"
        "*(Example: Physics Form 4 - Chapter 1)*"
    )
    await message.answer(welcome_text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(QuizCreation.naming)


# ==========================================
# 2. Quiz Naming -> Prompt for Content
# ==========================================
@router.message(QuizCreation.naming)
async def process_name(message: Message, state: FSMContext):
    """
    Saves the quiz name to the database and prompts for the first question.
    """
    quiz_name = message.text.strip()
    try:
        async for session in get_db():
            new_quiz = QuizSet(name=quiz_name, creator_id=message.from_user.id)
            session.add(new_quiz)
            await session.commit()
            await session.refresh(new_quiz)
            
            await state.update_data(quiz_id=new_quiz.id, question_count=0)
            
            instruction_text = (
                f"✨ Quiz **'{quiz_name}'** is ready!\n"
                "━━━━━━━━━━━━━━\n"
                "Please send the content for **Question 1**:\n\n"
                "📸 Send a **Screenshot** (Recommended)\n"
                "⌨️ Or type the **Text Question**"
            )
            await message.answer(instruction_text)
            await state.set_state(QuizCreation.waiting_for_content)
            break
    except Exception as e:
        logging.error(f"Database error during quiz naming: {e}")
        await message.answer("❌ Database error. Please try again.")


# ==========================================
# 3. Content Reception -> Option Selection
# ==========================================
@router.message(QuizCreation.waiting_for_content)
async def process_content(message: Message, state: FSMContext):
    """
    Processes the question content (photo or text) and asks for the correct answer.
    """
    if message.photo:
        c_type, c_data = "photo", message.photo[-1].file_id
    elif message.text:
        c_type, c_data = "text", message.text
    else:
        return await message.answer("⚠️ Please provide a photo or text for the question.")

    await state.update_data(temp_type=c_type, temp_data=c_data, temp_hint=None)
    
    # Inline buttons for A/B/C/D and the Hint feature
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="A", callback_data="set_ans:A"),
            InlineKeyboardButton(text="B", callback_data="set_ans:B"),
            InlineKeyboardButton(text="C", callback_data="set_ans:C"),
            InlineKeyboardButton(text="D", callback_data="set_ans:D")
        ],
        [InlineKeyboardButton(text="💡 Add Instructional Hint (Optional)", callback_data="add_hint")]
    ])
    
    prompt_text = (
        "📥 **Question content received**\n"
        "━━━━━━━━━━━━━━\n"
        "Select the **Correct Answer**:\n"
        "*(Or add a reference hint first using the button below)*"
    )
    await message.answer(prompt_text, reply_markup=kb)
    await state.set_state(QuizCreation.waiting_for_hint)


# ==========================================
# 4. Instructional Feedback (Hint) Flow
# ==========================================

@router.callback_query(QuizCreation.waiting_for_hint, F.data == "add_hint")
async def ask_for_hint(callback: CallbackQuery):
    """Triggers the input for a hint/textbook reference."""
    await callback.answer()
    await callback.message.edit_text(
        "📝 **Enter the Instructional Hint/Reference:**\n"
        "*(e.g., Refer to Textbook Page 42, Chapter 2)*"
    )

@router.message(QuizCreation.waiting_for_hint)
async def process_hint_text(message: Message, state: FSMContext):
    """Saves the hint text and returns to answer selection."""
    await state.update_data(temp_hint=message.text)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="A", callback_data="set_ans:A"),
        InlineKeyboardButton(text="B", callback_data="set_ans:B"),
        InlineKeyboardButton(text="C", callback_data="set_ans:C"),
        InlineKeyboardButton(text="D", callback_data="set_ans:D")
    ]])
    await message.answer("✅ **Hint saved.**\nNow, select the **Correct Answer**:", reply_markup=kb)


# ==========================================
# 5. Persistence & Navigation
# ==========================================
@router.callback_query(F.data.startswith("set_ans:"))
async def save_question(callback: CallbackQuery, state: FSMContext):
    """
    Saves the question to the DB and prompts the user to add more or finish.
    """
    # Guard against accidental clicks on old message buttons
    current_state = await state.get_state()
    if current_state != QuizCreation.waiting_for_hint:
        return await callback.answer("⚠️ Session expired or invalid state.")

    correct_opt = callback.data.split(":")[1]
    data = await state.get_data()
    
    # Generic options for screenshot-based questions
    opts = [{"id": i, "text": f"Option {i}"} for i in ["A", "B", "C", "D"]]
    
    try:
        async for session in get_db():
            new_q = Question(
                quiz_set_id=data['quiz_id'],
                content_type=data['temp_type'],
                content_data=data['temp_data'],
                hint=data.get('temp_hint'),
                options_data=opts,
                correct_option=correct_opt
            )
            session.add(new_q)
            await session.commit()
            
            new_count = data['question_count'] + 1
            await state.update_data(question_count=new_count)
            
            # Update UI for visual confirmation
            await callback.message.edit_text(
                f"🎯 **Question {new_count} configured!**\nCorrect Answer: `{correct_opt}`"
            )
            
            # Decision menu for next steps
            kb = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="➕ Add Next Question")],
                    [KeyboardButton(text="✅ Finish & Generate Link")]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            
            await callback.message.answer("What would you like to do next?", reply_markup=kb)
            await state.set_state(QuizCreation.confirm_next)
            break
        await callback.answer()
    except Exception as e:
        logging.error(f"Persistence error: {e}")
        await callback.message.answer("❌ Failed to save question. Please try again.")


# ==========================================
# 6. Branching Logic (Next / Finish)
# ==========================================

@router.message(QuizCreation.confirm_next, F.text == "➕ Add Next Question")
async def loop_next_question(message: Message, state: FSMContext):
    """Resets the state machine for the next question entry."""
    await message.answer(
        "👉 Please send the **Photo** or **Text** for the next question:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(QuizCreation.waiting_for_content)


@router.message(QuizCreation.confirm_next, F.text == "✅ Finish & Generate Link")
async def finish_quiz(message: Message, state: FSMContext):
    """Generates the final access link and cleans up the state."""
    data = await state.get_data()
    bot_info = await message.bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={data['quiz_id']}"
    
    success_text = (
        "🎊 **Quiz Successfully Created!**\n"
        "━━━━━━━━━━━━━━\n"
        f"📊 Total Questions: {data['question_count']}\n"
        f"🔗 Access Link: `{link}`\n\n"
        "Copy and share this link with your students for private practice."
    )
    await message.answer(success_text, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    await state.clear()