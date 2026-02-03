"""
Common Handlers - Project Kancil
Handles basic commands like /start, /history, and shorthand /review commands.
"""

from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from sqlalchemy import select

from src.database import get_db
from src.models import QuizSession, Question  # Added Question import

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    args = message.text.split()
    if len(args) > 1:
        return # Handled by attempt.py

    welcome_text = (
        "👋 **Welcome to Project Kancil!**\n\n"
        "I am your private, failure-safe study companion.\n\n"
        "📜 **Commands:**\n"
        "• /history - View your past practice sessions.\n"
        "• /practice - Get a random question.\n\n"
        "To start a specific quiz, use the link provided by your teacher."
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@router.message(Command("history"))
async def cmd_history(message: Message):
    async for session in get_db():
        stmt = (
            select(QuizSession)
            .where(
                QuizSession.user_id == message.from_user.id,
                QuizSession.is_completed == True
            )
            .order_by(QuizSession.created_at.desc())
            .limit(5)
        )
        
        result = await session.execute(stmt)
        past_sessions = result.scalars().all()

        if not past_sessions:
            return await message.answer("🌱 Your archive is empty. Start your first quiz to track progress!")

        response = "📜 *Your Private Learning Archive*\n"
        response += "━━━━━━━━━━━━━━\n\n"
        
        for ps in past_sessions:
            date_str = ps.created_at.strftime("%Y-%m-%d")
            accuracy = int((ps.correct_count / ps.total_count) * 100)
            
            response += (
                f"📅 **{date_str}**\n"
                f"📝 Subject: {ps.subject}\n"
                f"📊 Result: {ps.correct_count}/{ps.total_count} ({accuracy}%)\n"
                f"🔍 Review: /review_{ps.id[:8]}\n\n"
            )
        
        response += "*(Only you can see this history)*"
        await message.answer(response, parse_mode="Markdown")

# ==========================================
# NEW: Shorthand Review Handler
# ==========================================
@router.message(F.text.regexp(r"^/review_[a-zA-Z0-9]{8}$"))
async def cmd_review_shorthand(message: Message):
    """
    Enables students to trigger a mistake review via the link in /history.
    Uses .like() for prefix matching on the UUID.
    """
    short_id = message.text.split("_")[1]
    
    async for db_session in get_db():
        # Safety Guardrail: Must match prefix AND user_id
        stmt = (
            select(QuizSession)
            .where(
                QuizSession.id.like(f"{short_id}%"),
                QuizSession.user_id == message.from_user.id
            )
        )
        result = await db_session.execute(stmt)
        quiz_sess = result.scalars().first()

        if not quiz_sess:
            return await message.answer("⚠️ Session not found or access denied.")

        review_text = f"📖 *Mistake Review: {quiz_sess.subject}*\n"
        review_text += "━━━━━━━━━━━━━━\n\n"
        has_mistakes = False

        # quiz_sess.user_answers is a Dict[str, str] mapping question_id -> user_choice
        for q_id_str, user_ans in quiz_sess.user_answers.items():
            q_stmt = select(Question).where(Question.id == int(q_id_str))
            q_res = await db_session.execute(q_stmt)
            q = q_res.scalars().first()

            if q and user_ans != q.correct_option:
                has_mistakes = True
                review_text += (
                    f"❓ *Question:* {q.content_data[:60]}...\n"
                    f"❌ Your choice: {user_ans} | ✅ Correct: {q.correct_option}\n"
                    f"💡 *Hint:* {q.hint or 'Check your textbook for more info.'}\n\n"
                )

        if not has_mistakes:
            await message.answer(f"🎉 Perfect score on **{quiz_sess.subject}**! Nothing to review.")
        else:
            await message.answer(review_text, parse_mode="Markdown")
        break