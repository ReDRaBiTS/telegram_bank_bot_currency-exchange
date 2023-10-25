# -*- coding: utf-8 -*-

from aiogram.utils.keyboard import InlineKeyboardBuilder,\
     ReplyKeyboardMarkup, KeyboardButton

def star_keyboard() -> None:
    markup = InlineKeyboardBuilder()
    markup.button(text = "У касах банку", callback_data = 'cashdesk')
    markup.button(text = "При оплаті карткою", callback_data = 'card')
    markup.adjust(1, 1)
    return markup.as_markup()

# UA: При додаванні нових валют, сюди додати її назву
# EN: When adding new currencies, add its name here
def bank_opinion() -> None:
    markup = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='USD'),KeyboardButton(text='EUR'),KeyboardButton(text='PLN')]
    ],
    resize_keyboard=True,
    input_field_placeholder = 'Виберіть валюту')
    return markup


def change_option_bank_keyboard() -> None:
    markup = InlineKeyboardBuilder()
    markup.button(
        text="Обмін валют у касі",
        callback_data="UP_CASS"
    )
    markup.button(
        text="Обмін валют через карту",
        callback_data="UP_CARD"
    )
    markup.adjust(1, 1)
    return markup.as_markup()

