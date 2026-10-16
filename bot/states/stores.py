from __future__ import annotations
from aiogram.fsm.state import State, StatesGroup


class StoreSearchStates(StatesGroup):
    waiting_for_query = State()
