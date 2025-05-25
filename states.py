from aiogram.fsm.state import StatesGroup, State


class ClientState(StatesGroup):
    name = State()
    kompaniya_nomi = State()
    yaratilgan_sanasi = State()
    tugaydigan_sanasi = State()
    telefon_raqami = State()
    masul_xodim = State()
    finish = State()


class UpdateDateState(StatesGroup):
    phone_number = State()
    boshlanish_date = State()
    tugash_date = State()


class PhoneState(StatesGroup):
    raqami = State()


class AdminStates(StatesGroup):
    waiting_for_admin_id = State()
