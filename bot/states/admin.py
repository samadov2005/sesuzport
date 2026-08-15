from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    waiting_for_moderation_comment = State()
    waiting_for_search_query = State()
    waiting_for_broadcast_message = State()
    waiting_for_broadcast_confirm = State()
