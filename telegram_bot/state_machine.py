from aiogram.fsm.state import State, StatesGroup

class NoteForm(StatesGroup):
    title = State()
    content = State()
    tags = State()

class NoteSearch(StatesGroup):
    tags = State()