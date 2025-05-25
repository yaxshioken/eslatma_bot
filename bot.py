from datetime import datetime
import logging
import sys
import os
import re
from html import escape

from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, BotCommand, ReplyKeyboardRemove, FSInputFile

from buttons import mijozlar_keyboard, cancel
from states import ClientState, UpdateDateState, PhoneState, AdminStates
from db import DB

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

scheduler = AsyncIOScheduler()
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()
db = DB()


@dp.message(F.text == "Ortga")
async def cancel_handler(message: Message, state: FSMContext):
    """Bu handler Barcha statelarni tozalab bosh menyuda qaytaradi"""
    await state.clear()
    await message.answer("Bekor qilindi. Asosiy menyudasiz.", reply_markup=mijozlar_keyboard)


@dp.message(F.text == "🆕 Yangi mijozni eslatmaga belgilash")
async def handler_client(message: Message, state: FSMContext) -> None:
    """Bu handler ✨ Yangi Mijozni eslatmaga belgilash ✨ ushbu buttonni hand qiladi va keyingi statega o'tadi """
    await message.answer(text="Iltimos, mijozning ismini kiriting. 😊", reply_markup=cancel)
    await state.set_state(ClientState.name)


@dp.message(ClientState.name)
async def handler_name(message: Message, state: FSMContext) -> None:
    """Bu handler mijozning ismini statega saqlaydi va
    kompaniya nomini foydalanuvchidan so'raydi keyingi statega o'tadi"""
    if db.check_client_name_unique(name=message.text):
        await message.answer(text="Mijoz ismiga o'zgartirish kiriting.Shu ism bilan Oldin yaratilgan",
                             reply_markup=cancel)
        await message.answer(text="Iltimos, mijozning ismini kiriting. 😊")
    else:
        await state.update_data(name=message.text)
        await message.answer(text="Iltimos, kompaniya nomini kiriting. 🙏", reply_markup=cancel)
        await state.set_state(ClientState.yaratilgan_sanasi)


@dp.message(ClientState.yaratilgan_sanasi)
async def handler_created_at(message: Message, state: FSMContext) -> None:
    """Bu handler kompaniya nomini statega saqlaydi va sanani foydalanuvchidan so'raydi keyingi statega o'tadi"""
    await state.update_data(company_name=message.text)
    await message.answer(
        text=f"Iltimos, qo'llab-quvvatlash boshlanish sanasini kiriting. Masalan:\n`{datetime.today().date()}` 📅",
        parse_mode='Markdown', reply_markup=cancel)
    await state.set_state(ClientState.tugaydigan_sanasi)


@dp.message(ClientState.tugaydigan_sanasi)
async def handler_end_date(message: Message, state: FSMContext) -> None:
    """Bu handler sanani statega saqlaydi va sanani foydalanuvchidan so'raydi keyingi statega o'tadi"""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", message.text):
        await message.answer(text="Noto‘g‘ri sana formati! Iltimos, YYYY-MM-DD shaklida yuboring.")
        await message.answer(
            text=f"Iltimos, qo'llab-quvvatlash boshlanish sanasini kiriting. Masalan:\n`{datetime.today().date()}` 📅",
            parse_mode='Markdown', reply_markup=cancel)
    else:
        await state.update_data(created_at=message.text)
        await message.answer(
            text=f"Iltimos, qo'llab-quvvatlash tugash sanasini kiriting Masalan:\n`{datetime.today().date()}` 📅",
            parse_mode='Markdown', reply_markup=cancel)
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
            parse_mode='Markdown', reply_markup=cancel
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
            parse_mode='Markdown', reply_markup=cancel
        )
    else:
        await state.update_data(phone_number=message.text)
        await message.answer(
            "*🌟 Iltimos, mijozga xizmat ko‘rsatadigan Ma'sul ismini kiriting:* \n"
            "`Muhammad Rizo`\n"
            "`Jahongir`\n"
            "`Mirzohidjon`\n"
            "`Azizbek` 🌟",
            parse_mode='Markdown', reply_markup=cancel
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
    """Berilgan telefon raqam orqali mijozga xizmat ko'rsatish vaqtini yangilaydi"""
    await message.answer(
        text=(
            "Yangilanishi kerak bo'lgan mijozning telefon raqamini kiriting. "
            f"Masalan: `+998940021444`"
        ),
        parse_mode="Markdown", reply_markup=cancel
    )
    await state.set_state(UpdateDateState.phone_number)


@dp.message(UpdateDateState.phone_number)
async def handler_update_phone_number(message: Message, bot: Bot, state: FSMContext):
    if db.check_phone_number_exists(message.text):
        await state.update_data(telefon_raqami=message.text)
        await message.answer(
            text=f"Iltimos, qo'llab-quvvatlash boshlanish sanasini kiriting. Masalan:\n`{datetime.today().date()}` 📅",
            parse_mode="Markdown", reply_markup=cancel
        )
        await state.set_state(UpdateDateState.boshlanish_date)

    else:
        await message.answer(text="Siz mavjud bo'lmagan mijoz raqamini kiritdingiz!! Yana bir bor urinib ko'ring!")
        await message.answer(
            "*Mijozning telefon raqamini kiriting.* Masalan: `+998940021444` 📱",
            parse_mode='Markdown', reply_markup=cancel
        )


@dp.message(UpdateDateState.boshlanish_date)
async def handler_update_boshlanish_date(message: Message, bot: Bot, state: FSMContext):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", message.text):
        await message.answer(text="Noto‘g‘ri sana formati! Iltimos, YYYY-MM-DD shaklida yuboring.")
        await message.answer(
            text=f"Iltimos, qo'llab-quvvatlash boshlanish sanasini kiriting (Masalan: {datetime.today().date()}). 📅",
            reply_markup=cancel)
    else:
        await message.answer(
            text=f"Iltimos, qo'llab-quvvatlash tugash sanasini kiriting. Masalan:\n`{datetime.today().date()}` 📅",
            parse_mode="Markdown", reply_markup=cancel
        )
        await state.update_data(boshlanish_date=message.text)
        await state.set_state(UpdateDateState.tugash_date)


@dp.message(UpdateDateState.tugash_date)
async def handler_tugash_date(message: Message, bot: Bot, state: FSMContext):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", message.text):
        await message.answer(text="Noto‘g‘ri sana formati! Iltimos, YYYY-MM-DD shaklida yuboring.")
        await message.answer(
            text=f"Iltimos, qo'llab-quvvatlash tugash sanasini kiriting. Masalan:\n`{datetime.today().date()}` 📅",
            parse_mode="Markdown", reply_markup=cancel
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
            await message.answer(text="Ma'lumotlarni to'ldirishda xatolik", reply_markup=cancel)
        await state.clear()


@dp.message(F.text == '📞 Telefon raqam bo‘yicha qidirish')
async def raqami(message: Message, state: FSMContext):
    await message.answer(
        "*Mijozning telefon raqamini kiriting.* Masalan: `+998940021444` 📱",
        parse_mode='Markdown', reply_markup=cancel
    )
    await state.set_state(PhoneState.raqami)


@dp.message(PhoneState.raqami)
async def get_mijoz_by_phone_number(message: Message, state: FSMContext):
    phone = message.text.strip()
    mijoz_info = db.get_mijoz(phone)
    message_text = (
        f"{html.bold("📝 Mijoz ma'lumotlari ro‘yxati.")}\n\n"
        f"{html.italic('Ismi:')} {html.bold(mijoz_info[1])}\n"
        f"{html.italic('Kompaniyasi:')} {html.bold(mijoz_info[2])}\n"
        f"{html.italic('Ishga tushgan vaqti:')} {html.bold(mijoz_info[3])}\n"
        f"{html.italic('Xizmat tugash vaqti:')} {html.bold(mijoz_info[4])}\n"
        f"{html.italic('Telefon raqami:')} {html.bold(mijoz_info[6])}\n"
        f"{html.italic("Ma'sul shaxs:")} {html.bold(mijoz_info[7])}\n"
    )
    if mijoz_info is None:

        await message.answer(
            text="❌ Bunday telefon raqamli mijoz topilmadi. Iltimos, raqamni tekshiring va qayta urinib ko‘ring.",
            reply_markup=cancel
        )
    else:
        await message.answer(
            text=message_text,
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


@dp.message(F.text == "🚀 Yangi admin yaratamiz — jamoani rivojlantiraylik! 🤝")
async def create_admin(message: Message, state: FSMContext):
    await message.answer("Yangi adminning Telegram ID sini yuboring, iltimos 😊", reply_markup=cancel)
    await state.set_state(AdminStates.waiting_for_admin_id)


@dp.message(AdminStates.waiting_for_admin_id)
async def succes_end(message: Message, state: FSMContext):
    try:
        telegram_id = int(message.text)
    except ValueError:
        await message.answer("Iltimos, faqat raqam kiriting! 🔢")
        return

    if db.update_admin(telegram_id):
        await message.reply("✅ Admin muvaffaqiyatli yangilandi!")
        await state.clear()
    else:
        await message.answer("❗️Iltimos, mavjud bo‘lgan va to‘g‘ri ID kiriting!")


@dp.message(F.text == "Barcha aktiv mijozlarni ko'rish 😊")
async def get_all_clients(message: Message):
    data = db.get_clients()
    for mijoz_info in data:
        message_text = (
            f"{html.bold("📝 Mijoz ma'lumotlari ro‘yxati.")}\n\n"
            f"{html.italic('Ismi:')} {html.bold(mijoz_info[1])}\n"
            f"{html.italic('Kompaniyasi:')} {html.bold(mijoz_info[2])}\n"
            f"{html.italic('Ishga tushgan vaqti:')} {html.bold(mijoz_info[3])}\n"
            f"{html.italic('Xizmat tugash vaqti:')} {html.bold(mijoz_info[4])}\n"
            f"{html.italic('Telefon raqami:')} {html.bold(mijoz_info[6])}\n"
            f"{html.italic("Ma'sul shaxs:")} {html.bold(mijoz_info[7])}\n"
        )
        await message.answer(
            text=message_text,
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove()
        )
        with open("mijozlar_royxati.txt", 'a', encoding='utf-8') as f:
            f.write(f"""Ismi:{mijoz_info[1]}\n
Kompaniyasi:{mijoz_info[2]}\n
Ishga tushgan vaqti:{mijoz_info[3]}\n
Xizmat tugash vaqti:{mijoz_info[4]}\n
Telefon raqami:{mijoz_info[6]}\n
Ma'sul shaxs:{mijoz_info[7]}\n\n\n\n""")

    file = FSInputFile("mijozlar_royxati.txt")
    await message.answer_document(file, caption="📄 Mijozlar ro'yxati fayl ko'rinishida:")
    with open("mijozlar_royxati.txt", 'w', encoding='utf-8') as f:
        f.write("")
        f.close()
    await message.answer("Asosiy menyu:", reply_markup=mijozlar_keyboard)


@dp.message(F.text)
async def command_start_handler(message: Message) -> None:
    """
    Bu funksiya start bosgan foydalanuvchini ma'lumotlar bazasida bor yo'qligini tekshiradi
    agar yo'q bo'lsa yaratadi
    """
    if db.check_admin(message.from_user.id):
        name = escape(message.from_user.first_name)

        welcome_text = (
            f"👋 <b>Assalomu alaykum, {name}!</b>\n\n"
            "🎉 <b>Xush kelibsiz!</b>\n\n"
            "🤖 Siz <b>Datafin IT</b> kompaniyasining <i>Texnik Qo'llab-Quvvatlash mutaxassislari botidasiz</i>.\n\n"
            "💬 Biz bu yerda sizga tez va samarali yordam berish uchun tayyormiz.\n"
            "Quyidagi menyudan kerakli bo‘limni tanlang yoki savolingizni yozing.\n\n"
            "<b>Sizga doimo yordam beramiz!</b> 💡\n\n"
            "<b>Murojaat uchun:@Aziz_555</b>")

        await message.answer(welcome_text, parse_mode="HTML", reply_markup=mijozlar_keyboard)

    else:
        name = escape(message.from_user.first_name)

        welcome_text = (
            f"👋 <b>Assalomu alaykum, {name}!</b>\n\n"
            "🎉 <b>Xush kelibsiz!</b>\n\n"
            "🤖 Siz <b>Datafin IT</b> kompaniyasining <i>Texnik Qo'llab-Quvvatlash mutaxassislari botidasiz</i>.\n\n"
            "💬 Biz bu yerda sizga tez va samarali yordam berish uchun tayyormiz.\n"
            "Quyidagi menyudan kerakli bo‘limni tanlang yoki savolingizni yozing.\n\n"
            "<b>Sizga doimo yordam beramiz!</b> 💡\n\n"
            "<b>Murojaat uchun:@Aziz_555</b>"
        )
        telegram_id = message.from_user.id
        user_exist = db.check_user_exist(telegram_id)
        if not user_exist:
            username = str(message.from_user.username)
            telegram_id = int(message.from_user.id)
            first_name = str(message.from_user.first_name)

            db.insert_user(username, telegram_id, first_name)
        await message.answer(welcome_text, parse_mode="HTML")


async def scheduled_task(bot):
    data = db.get_clients()
    admins = db.get_all_admin()
    for mijoz_info in data:
        message_text = (
            f"{html.bold('📝 Mijoz ma\'lumotlari ro‘yxati.')}\n\n"
            f"{html.italic('Ismi:')} {html.bold(mijoz_info[1])}\n"
            f"{html.italic('Kompaniyasi:')} {html.bold(mijoz_info[2])}\n"
            f"{html.italic('Ishga tushgan vaqti:')} {html.bold(mijoz_info[3])}\n"
            f"{html.italic('Xizmat tugash vaqti:')} {html.bold(mijoz_info[4])}\n"
            f"{html.italic('Telefon raqami:')} {html.bold(mijoz_info[6])}\n"
            f"{html.italic('Ma\'sul shaxs:')} {html.bold(mijoz_info[7])}\n"
        )
        for admin in admins:
            chat_id = admin[0]
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=message_text,
                    parse_mode="HTML",
                    reply_markup=ReplyKeyboardRemove()
                )
            except Exception as e:
                print(f"Xabar yuborishda xatolik {chat_id} uchun: {e}")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.message.register(command_start_handler, CommandStart())
    dp.message.register(handler_name, ClientState.name)
    dp.message.register(handler_created_at, ClientState.yaratilgan_sanasi)
    dp.message.register(handler_end_date, ClientState.tugaydigan_sanasi)
    dp.message.register(handler_phone_number, ClientState.telefon_raqami)
    dp.message.register(handler_masul_xodim, ClientState.masul_xodim)

    scheduler.add_job(
        scheduled_task,
        'cron',
        hour='9,18',
        minute=5,
        args=(bot,)
    )
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())
