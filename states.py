from aiogram.fsm.state import StatesGroup, State


class ClientState(StatesGroup):
    name=State()
    kompaniya_nomi=State()
    yaratilgan_sanasi=State()
    tugaydigan_sanasi=State()
    telefon_raqami=State()
    finish=State()