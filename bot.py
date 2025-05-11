import asyncio
import datetime
import logging
import sys
import os

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, BotCommand

from buttons import mijozlar
from states import ClientState

load_dotenv()

# Bot token can be obtained via https://t.me/BotFather
TOKEN = os.getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"""Assalomu alaykum ✋, {html.bold(message.from_user.full_name)}!  
Xush kelibsiz! 🌟  
{html.bold("Datafin IT")} kompaniyasining Texnik Qo'llab-Quvvatlash botiga xush kelibsiz! 🤖  
Sizga qanday yordam bera olishimiz mumkin?""", parse_mode='HTML',reply_markup=mijozlar)


@dp.message(F.text == "✨ Yangi Mijozni eslatmaga belgilash ✨")
async def create_client(message: Message,state:FSMContext) -> None:
    await message.answer(text="Iltimos, mijozning ismini kiriting. 😊")
    await state.set_state(ClientState.name)


@dp.message(ClientState.name)
async def create_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer(text="Iltimos, kompaniya nomini kiriting. 🙏")
    await state.set_state(ClientState.yaratilgan_sanasi)


@dp.message(ClientState.yaratilgan_sanasi)
async def create_created_at(message: Message, state: FSMContext) -> None:
    await state.update_data(created_at=message.text)
    await message.answer(
        text=f"Iltimos, qo'llab-quvvatlash boshlanish sanasini kiriting (Masalan: {datetime.date.today()}). 📅")
    await state.set_state(ClientState.tugaydigan_sanasi)


@dp.message(ClientState.tugaydigan_sanasi)
async def create_end_date(message: Message, state: FSMContext) -> None:
    await state.update_data(created_at=message.text)
    await message.answer(text=f"Iltimos, qo'llab-quvvatlash tugash sanasini kiriting (Masalan: {datetime.date.today()}). 📅")
    await state.set_state(ClientState.telefon_raqami)
@dp.message(ClientState.telefon_raqami)
async def create_phone_number(message:Message,state:FSMContext)->None:
    await state.update_data(end_date=message.text)
    await message.answer("Iltimos, mijozning telefon raqamini kiriting. 📱")
    await state.set_state(ClientState.finish)
@dp.message(ClientState.finish)
async def finish(message:Message,state:FSMContext)->None:
    await state.update_data(phone_number=message.text)
    data = await state.get_data()
    await message.answer(text=f"""{}""")
    await state.clear()


#
# @dp.message()
# async def echo_handler(message: Message) -> None:
#     """
#     Handler will forward receive a message back to the sender
#
#     By default, message handler will handle all message types (like a text, photo, sticker etc.)
#     """
#     try:
#         # Send a copy of the received message
#         await message.send_copy(chat_id=message.chat.id)
#     except TypeError:
#         # But not all the types is supported to be copied so need to handle it
#         await message.answer("Nice try!")

async def set_commands(bot):
    await bot.set_my_commands([
        BotCommand(command='start', description="botni ishga tushurish "),
        BotCommand(command='help', description="""Yordam """),
        BotCommand(command='client', description="E'lon berish")
    ])
async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.message.register(command_start_handler,CommandStart())
    dp.message.register(create_client)
    dp.message.register(create_name,ClientState.name)
    dp.message.register(create_created_at,ClientState.yaratilgan_sanasi)
    dp.message.register(create_end_date,ClientState.tugaydigan_sanasi)
    dp.message.register(create_phone_number,ClientState.telefon_raqami)


    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
