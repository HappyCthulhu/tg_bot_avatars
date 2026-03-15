from aiogram.fsm.state import State, StatesGroup


class DialogStates(StatesGroup):
    choosing_avatar = State()
    dialog = State()
