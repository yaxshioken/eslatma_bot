from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

mijozlar_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🆕 Yangi mijozni eslatmaga belgilash"),
            KeyboardButton(text="🔄 Davrni yangilash")
        ],
        [
            KeyboardButton(text="📞 Telefon raqam bo‘yicha qidirish"),
            KeyboardButton(text="Barcha  mijozlarni ko'rish 😊")
        ],
        [
            KeyboardButton(text="🚀 Yangi admin yaratamiz — jamoani rivojlantiraylik! 🤝")
        ],
        [
            KeyboardButton(text="🤗 Qo‘llab-quvvatlashdagi mijozlarni ko‘rish")
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
