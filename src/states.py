# src/states.py
from aiogram.fsm.state import StatesGroup, State

class QuizCreation(StatesGroup):
    naming = State()              # 1. 等待输入试卷名称
    waiting_for_content = State() # 2. 等待发送题目内容 (图/文)
    waiting_for_hint = State()    # 3. 等待发送 Hint/描述
    waiting_for_poll = State()    # 4. 等待发送选项 (A..., B...)
    confirm_next = State()        # 5. 等待确认 (下一题 / 结束)