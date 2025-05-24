from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

mijozlar_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🆕 Yangi mijozni eslatmaga belgilash"),
            KeyboardButton(text="🔄 Davrni yangilash"),
            KeyboardButton(text="📞 Telefon raqam bo‘yicha qidirish")
        ]
    ],
    resize_keyboard=True
)
