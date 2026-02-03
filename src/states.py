"""
FSM State Definitions - Project Kancil
Defines the Finite State Machine (FSM) categories to track user progress 
through quiz creation and participation flows.
"""

from aiogram.fsm.state import State, StatesGroup

class QuizCreation(StatesGroup):
    """States for the Educator's quiz creation workflow."""
    naming = State()               # Inputting the quiz set title
    waiting_for_content = State()  # Sending question text or images
    waiting_for_hint = State()     # Adding optional instructional feedback/references
    confirm_next = State()         # Deciding to add another question or finalize

class QuizAttempt(StatesGroup):
    """States for the Student's practice session."""
    in_progress = State()          # Actively answering questions in a session