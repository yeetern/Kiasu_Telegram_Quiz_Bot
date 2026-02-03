# src/states.py
from aiogram.fsm.state import State, StatesGroup

class QuizCreation(StatesGroup):
    naming = State()              # 1. 命名
    waiting_for_content = State() # 2. 等待题目内容(图/文)
    waiting_for_hint = State()    # 3. 等待 Hint
    waiting_for_poll = State()    # 4. 等待设置选项(A/B/C/D)
    confirm_next = State()        # 5. 确认下一题或结束