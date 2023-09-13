from aiogram.dispatcher.filters.state import State, StatesGroup

class Stages(StatesGroup):
    choice = State()
    number = State()
    points = State()
    university = State()
    direction = State()
    retry = State()