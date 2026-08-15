from aiogram.fsm.state import State, StatesGroup

class RoleSelectionStates(StatesGroup):
    waiting_for_role = State()
