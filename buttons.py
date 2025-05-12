from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

mijozlar = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="✨ Yangi Mijozni eslatmaga belgilash ✨"),
                                          KeyboardButton(text="🔄 Davrni yangilash 🔄")]], resize_keyboard=True,
                               one_time_keyboard=True)
