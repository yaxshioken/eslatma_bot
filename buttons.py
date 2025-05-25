from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

mijozlar_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🆕 Yangi mijozni eslatmaga belgilash"),
            KeyboardButton(text="🔄 Davrni yangilash")
        ],
        [
            KeyboardButton(text="📞 Telefon raqam bo‘yicha qidirish"),
            KeyboardButton(text="Barcha aktiv mijozlarni ko'rish 😊")
        ],
        [
            KeyboardButton(text="🚀 Yangi admin yaratamiz — jamoani rivojlantiraylik! 🤝")
        ]
    ],
    resize_keyboard=True
)
cancel = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Ortga')
        ]
    ], resize_keyboard=True
)
