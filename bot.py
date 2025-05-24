import asyncio
from datetime import datetime
import logging
import sys
import os
import re
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, BotCommand, ReplyKeyboardRemove

from buttons import mijozlar_keyboard
from states import ClientState, UpdateDateState, PhoneState
from db import DB

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()
db = DB()


@dp.message(F.text == "🆕 Yangi mijozni eslatmaga belgilash")
async def handler_client(message: Message, state: FSMContext) -> None:
    """Bu handler ✨ Yangi Mijozni eslatmaga belgilash ✨ ushbu buttonni hand qiladi va keyingi statega o'tadi """
    await message.answer(text="Iltimos, mijozning ismini kiriting. 😊")
    await state.set_state(ClientState.name)


@dp.message(ClientState.name)
async def handler_name(message: Message, state: FSMContext) -> None:
    """Bu handler mijozning ismini statega saqlaydi va
    kompaniya nomini foydalanuvchidan so'raydi keyingi statega o'tadi"""
    if db.check_client_name_unique(name=message.text):
        await message.answer(text="Mijoz ismiga o'zgartirish kiriting.Shu ism bilan Oldin yaratilgan")
        await message.answer(text="Iltimos, mijozning ismini kiriting. 😊")
    else:
        await state.update_data(name=message.text)
        await message.answer(text="Iltimos, kompaniya nomini kiriting. 🙏")
        await state.set_state(ClientState.yaratilgan_sanasi)


@dp.message(ClientState.yaratilgan_sanasi)
async def handler_created_at(message: Message, state: FSMContext) -> None:
    """Bu handler kompaniya nomini statega saqlaydi va sanani foydalanuvchidan so'raydi keyingi statega o'tadi"""
    await state.update_data(company_name=message.text)
    await message.answer(
        text=f"Iltimos, qo'llab-quvvatlash boshlanish sanasini kiriting. Masalan:\n`{datetime.today().date()}` 📅",
        parse_mode='Markdown')
    await state.set_state(ClientState.tugaydigan_sanasi)


@dp.message(ClientState.tugaydigan_sanasi)
async def handler_end_date(message: Message, state: FSMContext) -> None:
    """Bu handler sanani statega saqlaydi va sanani foydalanuvchidan so'raydi keyingi statega o'tadi"""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", message.text):
        await message.answer(text="Noto‘g‘ri sana formati! Iltimos, YYYY-MM-DD shaklida yuboring.")
        await message.answer(
            text=f"Iltimos, qo'llab-quvvatlash boshlanish sanasini kiriting. Masalan:\n`{datetime.today().date()}` 📅",
            parse_mode='Markdown')
    else:
        await state.update_data(created_at=message.text)
        await message.answer(
            text=f"Iltimos, qo'llab-quvvatlash tugash sanasini kiriting Masalan:\n`{datetime.today().date()}` 📅",
            parse_mode='Markdown')
        await state.set_state(ClientState.telefon_raqami)


@dp.message(ClientState.telefon_raqami)
async def handler_phone_number(message: Message, state: FSMContext) -> None:
    """Bu handler sanani statega saqlaydi
    va foydalanuvchidan mijozning telefon raqamini so'raydi keyingi statega o'tadi"""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", message.text):
        await message.answer(text="Noto‘g‘ri sana formati! Iltimos, YYYY-MM-DD shaklida yuboring.")
        await message.answer(
            text=f"Iltimos, qo'llab-quvvatlash tugash sanasini kiriting Masalan:\n`{datetime.today().date()}` 📅",
            parse_mode='HTML')
    else:
        await state.update_data(end_date=message.text)
        await message.answer(
            "*Mijozning telefon raqamini kiriting.* Masalan: `+998940021444` 📱",
            parse_mode='Markdown'
        )
        await state.set_state(ClientState.masul_xodim)


@dp.message(ClientState.masul_xodim)
async def handler_masul_xodim(message: Message, state: FSMContext) -> None:
    """Bu handler mijozning telefon raqamini statega saqlaydi
    va ma'sul xodim belgilashni so'raydi keyingi statega o'tadi"""

    if db.check_unique_phone_number(message.text):
        await message.answer(text="Mijozning telefon raqami allaqachon mavjud!!!")
        await message.answer(
            "*Mijozning telefon raqamini kiriting.* Masalan: `+998940021444` 📱",
            parse_mode='Markdown'
        )
    else:
        await state.update_data(phone_number=message.text)
        await message.answer(
            "*🌟 Iltimos, mijozga xizmat ko‘rsatadigan Ma'sul ismini kiriting:* \n"
            "`Muhammad Rizo`\n"
            "`Jahongir`\n"
            "`Mirzohidjon`\n"
            "`Azizbek` 🌟",
            parse_mode='Markdown'
        )
        await state.set_state(ClientState.finish)


@dp.message(ClientState.finish)
async def finish(message: Message, state: FSMContext) -> None:
    """Bu handler masul xodimni statega saqlayai va statedagi ma'lumotlarni ma'lumotlar bazasiga saqlaydi.
     va foydalanuvchiga ma'lumotlar muvaffaqiyatli saqlangani haqida xabar yuboradi state yakunlanadi"""
    await state.update_data(masul_xodim=message.text)
    data = await state.get_data()
    name = str(data.get("name"))
    company = str(data.get("company_name"))
    created_at = (data.get("created_at"))
    end_date = (data.get("end_date"))
    phone_number = data.get("phone_number")
    masul_xodim = data.get("masul_xodim")
    if not db.insert_client(name, company, created_at, end_date, phone_number, masul_xodim):
        message_text = (
            f"{html.bold('✅ Foydalanuvchi muvaffaqiyatli yaratildi!')}\n\n"
            f"{html.italic('Ismi:')} {html.bold(data.get('name'))}\n"
            f"{html.italic('Kompaniyasi:')} {html.bold(data.get('company_name'))}\n"
            f"{html.italic('Ishga tushgan vaqti:')} {html.bold(data.get('created_at'))}\n"
            f"{html.italic('Xizmat tugash vaqti:')} {html.bold(data.get('end_date'))}\n"
            f"{html.italic('Telefon raqami:')} {html.bold(data.get('phone_number'))}\n"
            f"{html.italic("Ma'sul shaxs:")} {html.bold(data.get('masul_xodim'))}\n"
        )

        await message.answer(
            text=message_text,
            reply_markup=mijozlar_keyboard,
            parse_mode="HTML"
        )
    else:
        await message.answer(text="Ma'lumotlarni to'ldirishda xatolik")
    await state.clear()


@dp.message(F.text == "🔄 Davrni yangilash")
async def update_date(message: Message, bot: Bot, state: FSMContext):
    await message.answer(
        text=(
            "Yangilanishi kerak bo'lgan mijozning telefon raqamini kiriting. "
            f"Masalan: `+998940021444`"
        ),
        parse_mode="Markdown"
    )
    await state.set_state(UpdateDateState.phone_number)


@dp.message(UpdateDateState.phone_number)
async def handler_update_phone_number(message: Message, bot: Bot, state: FSMContext):
    if db.check_phone_number_exists(message.text):
        await state.update_data(telefon_raqami=message.text)
        await message.answer(
            text=f"Iltimos, qo'llab-quvvatlash boshlanish sanasini kiriting. Masalan:\n`{datetime.today().date()}` 📅",
            parse_mode="Markdown"
        )
        await state.set_state(UpdateDateState.boshlanish_date)

    else:
        await message.answer(text="Siz mavjud bo'lmagan mijoz raqamini kiritdingiz!! Yana bir bor urinib ko'ring!")
        await message.answer(
            "*Mijozning telefon raqamini kiriting.* Masalan: `+998940021444` 📱",
            parse_mode='Markdown'
        )


@dp.message(UpdateDateState.boshlanish_date)
async def handler_update_boshlanish_date(message: Message, bot: Bot, state: FSMContext):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", message.text):
        await message.answer(text="Noto‘g‘ri sana formati! Iltimos, YYYY-MM-DD shaklida yuboring.")
        await message.answer(
            text=f"Iltimos, qo'llab-quvvatlash boshlanish sanasini kiriting (Masalan: {datetime.today().date()}). 📅")
    else:
        await message.answer(
            text=f"Iltimos, qo'llab-quvvatlash tugash sanasini kiriting. Masalan:\n`{datetime.today().date()}` 📅",
            parse_mode="Markdown"
        )
        await state.update_data(boshlanish_date=message.text)
        await state.set_state(UpdateDateState.tugash_date)


@dp.message(UpdateDateState.tugash_date)
async def handler_tugash_date(message: Message, bot: Bot, state: FSMContext):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", message.text):
        await message.answer(text="Noto‘g‘ri sana formati! Iltimos, YYYY-MM-DD shaklida yuboring.")
        await message.answer(
            text=f"Iltimos, qo'llab-quvvatlash tugash sanasini kiriting. Masalan:\n`{datetime.today().date()}` 📅",
            parse_mode="Markdown"
        )
    else:
        await state.update_data(tugash_date=message.text)
        data = await state.get_data()
        phone_number = data.get("telefon_raqami")
        boshlanish_date = data.get("boshlanish_date")
        tugash_date = data.get("tugash_date")
        if not db.update_date(phone_number, boshlanish_date, tugash_date):
            await message.answer(text="Ma'lumotlar muvafaqiyatli yangilandi", reply_markup=mijozlar_keyboard)
        else:
            await message.answer(text="Ma'lumotlarni to'ldirishda xatolik")
        await state.clear()


@dp.message(F.text == '📞 Telefon raqam bo‘yicha qidirish')
async def raqami(message: Message, state: FSMContext):
    await message.answer(
        "*Mijozning telefon raqamini kiriting.* Masalan: `+998940021444` 📱",
        parse_mode='Markdown'
    )
    await state.set_state(PhoneState.raqami)


@dp.message(PhoneState.raqami)
async def get_mijoz_by_phone_number(message: Message, state: FSMContext):
    phone = message.text.strip()
    mijoz_info = db.get_mijoz(phone)
    print(str(mijoz_info))
    if mijoz_info is None:

        await message.answer(
            text="❌ Bunday telefon raqamli mijoz topilmadi. Iltimos, raqamni tekshiring va qayta urinib ko‘ring.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            text=str(mijoz_info),
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove()
        )
    await message.answer("Asosiy menyu:", reply_markup=mijozlar_keyboard)
    await state.clear()


async def set_commands(bot):
    await bot.set_my_commands([
        BotCommand(command='start', description="botni ishga tushurish "),
        BotCommand(command='help', description="""Yordam """)
    ])


@dp.message()
async def command_start_handler(message: Message) -> None:
    """
    Bu funksiya start bosgan foydalanuvchini ma'lumotlar bazasida bor yo'qligini tekshiradi
    agar yo'q bo'lsa yaratadi
    """

    await message.answer(f"""Assalomu alaykum ✋, {html.bold(message.from_user.full_name)}!  
Xush kelibsiz! 🌟  
{html.bold("Datafin IT")} kompaniyasining Texnik Qo'llab-Quvvatlash botiga xush kelibsiz! 🤖  
Sizga qanday yordam bera olishimiz mumkin?""", parse_mode='HTML', reply_markup=mijozlar_keyboard)
    telegram_id = message.from_user.id
    user_exist = db.check_user_exist(telegram_id)
    if not user_exist:
        username = str(message.from_user.username)
        telegram_id = int(message.from_user.id)
        first_name = str(message.from_user.first_name)

        db.insert_user(username, telegram_id, first_name)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.message.register(command_start_handler, CommandStart())
    dp.message.register(handler_name, ClientState.name)
    dp.message.register(handler_created_at, ClientState.yaratilgan_sanasi)
    dp.message.register(handler_end_date, ClientState.tugaydigan_sanasi)
    dp.message.register(handler_phone_number, ClientState.telefon_raqami)
    dp.message.register(handler_masul_xodim, ClientState.masul_xodim)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())
