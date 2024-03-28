from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)

rp_button = [
    [KeyboardButton(text="Video qo'shish"),
     KeyboardButton(text="Video ko'rish")
     ],
]

main_rp = ReplyKeyboardMarkup(keyboard=rp_button, resize_keyboard=True)


def order_keyboart():
    ikm = InlineKeyboardMarkup()
    ikm.add(InlineKeyboardButton("o'chirish", callback_data="o'chirish"))
    return ikm
