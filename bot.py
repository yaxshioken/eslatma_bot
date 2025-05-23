import asyncio
import datetime
import logging
import sys
import os

from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, BotCommand
from psycopg2 import Error

from buttons import mijozlar
from states import ClientState
from db import DB

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()
db = DB()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Bu start bosgan foydalanuvchini ma'lumotlar bazasida bor yo'qligini tekshiradi
    agar yo'q bo'lsa yaratadi
    """

    await message.answer(f"""Assalomu alaykum ✋, {html.bold(message.from_user.full_name)}!  
Xush kelibsiz! 🌟  
{html.bold("Datafin IT")} kompaniyasining Texnik Qo'llab-Quvvatlash botiga xush kelibsiz! 🤖  
Sizga qanday yordam bera olishimiz mumkin?""", parse_mode='HTML', reply_markup=mijozlar)
    telegram_id = message.from_user.id
    user_exist = db.check_user_exist(telegram_id)
    if not user_exist:
        username = str(message.from_user.username)
        telegram_id = int(message.from_user.id)
        first_name = str(message.from_user.first_name)

        db.insert_user(username, telegram_id, first_name)


@dp.message(F.text == "✨ Yangi Mijozni eslatmaga belgilash ✨")
async def create_client(message: Message, state: FSMContext) -> None:
    await message.answer(text="Iltimos, mijozning ismini kiriting. 😊")
    await state.set_state(ClientState.name)


@dp.message(ClientState.name)
async def create_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer(text="Iltimos, kompaniya nomini kiriting. 🙏")
    await state.set_state(ClientState.yaratilgan_sanasi)


@dp.message(ClientState.yaratilgan_sanasi)
async def create_created_at(message: Message, state: FSMContext) -> None:
    await state.update_data(company_name=message.text)
    await message.answer(
        text=f"Iltimos, qo'llab-quvvatlash boshlanish sanasini kiriting (Masalan: {datetime.date.today()}). 📅")
    await state.set_state(ClientState.tugaydigan_sanasi)


@dp.message(ClientState.tugaydigan_sanasi)
async def create_end_date(message: Message, state: FSMContext) -> None:
    await state.update_data(created_at=message.text)
    await message.answer(
        text=f"Iltimos, qo'llab-quvvatlash tugash sanasini kiriting (Masalan: {datetime.date.today()}). 📅")
    await state.set_state(ClientState.telefon_raqami)


@dp.message(ClientState.telefon_raqami)
async def create_phone_number(message: Message, state: FSMContext) -> None:
    await state.update_data(end_date=message.text)
    await message.answer("Iltimos, mijozning telefon raqamini kiriting. 📱")
    await state.set_state(ClientState.finish)


@dp.message(ClientState.finish)
async def finish(message: Message, state: FSMContext) -> None:
    await state.update_data(phone_number=message.text)
    data = await state.get_data()
    name = str(data.get("name"))
    company = str(data.get("company_name"))
    created_at = (data.get("created_at"))
    end_date = (data.get("end_date"))
    phone_number = data.get("phone_number")
    try:
        db.insert_client(name, company, created_at, end_date, phone_number)
        message_text = (
            f"{html.bold('✅ Foydalanuvchi muvaffaqiyatli yaratildi!')}\n\n"
            f"{html.italic('Ismi:')} {html.bold(data.get('name'))}\n"
            f"{html.italic('Kompaniyasi:')} {html.bold(data.get('company_name'))}\n"
            f"{html.italic('Ishga tushgan vaqti:')} {html.bold(data.get('created_at'))}\n"
            f"{html.italic('Xizmat tugash vaqti:')} {html.bold(data.get('end_date'))}\n"
            f"{html.italic('Telefon raqami:')} {html.bold(data.get('phone_number'))}"
        )

        await message.answer(
            text=message_text,
            parse_mode="HTML"
        )
    except Error as e:
        await message.answer(f"Xatolik:{e}")

        await message.answer(
            text="Foydalanuvchini yaratishda xato yuz berdi. Iltimos, qayta urinib ko'ring."
        )

    await state.clear()


async def set_commands(bot):
    await bot.set_my_commands([
        BotCommand(command='start', description="botni ishga tushurish "),
        BotCommand(command='help', description="""Yordam """)
    ])


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.message.register(command_start_handler, CommandStart())
    dp.message.register(create_client)
    dp.message.register(create_name, ClientState.name)
    dp.message.register(create_created_at, ClientState.yaratilgan_sanasi)
    dp.message.register(create_end_date, ClientState.tugaydigan_sanasi)
    dp.message.register(create_phone_number, ClientState.telefon_raqami)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
