import logging
from core.classes import DataBaseCommand, Printing_Information_in_Message
from app.keyboards import star_keyboard, bank_opinion 
from aiogram import Bot
from aiogram.types import Message, CallbackQuery

# @dp.callback_query(F.data.in_({'USD', 'EUR'}))
async def main_message( message: Message, bot: Bot) -> None:
    DB = DataBaseCommand
    users_opinion_tuple = await DB.get_user_setting(message.from_user.id)
    # UA: При додаванні нових валют, сюди додати її назву
    # EN: When adding new currencies, add its name here
    if message.text == 'EUR': # при додаванні нових валют сюди додати нові варІанти
        PIM = Printing_Information_in_Message(users_opinion_tuple, 'EUR')
        currency = 'евро  🇪🇺'
    elif message.text == 'USD':
        PIM = Printing_Information_in_Message(users_opinion_tuple, 'USD')
        currency = 'доларів  🇺🇸'
    elif message.text == 'PLN':
        PIM = Printing_Information_in_Message(users_opinion_tuple, 'PLN')
        currency = 'злотих  🇵🇱'
    
    value_list = PIM.print_rate()
    value_list_sell = sorted(value_list, key=lambda x: x[1])
    await message.answer(f'''Топ 5 банків за курсом продаж {currency}:
            1. {value_list_sell[0][0]} - <b>{value_list_sell[0][1]}</b> грн.
            2. {value_list_sell[1][0]} - <b>{value_list_sell[1][1]}</b> грн.
            3. {value_list_sell[2][0]} - <b>{value_list_sell[2][1]}</b> грн.
            4. {value_list_sell[3][0]} - <b>{value_list_sell[3][1]}</b> грн.
            5. {value_list_sell[4][0]} - <b>{value_list_sell[4][1]}</b> грн.
            ''')

    value_list_buy = sorted(value_list, key=lambda x: x[2], reverse=True)
    await message.answer(f'''Топ 5 банків за курсом купівлі {currency}:
            1. {value_list_buy[0][0]} - <b>{value_list_buy[0][2]}</b> грн.
            2. {value_list_buy[1][0]} - <b>{value_list_buy[1][2]}</b> грн.
            3. {value_list_buy[2][0]} - <b>{value_list_buy[2][2]}</b> грн.
            4. {value_list_buy[3][0]} - <b>{value_list_buy[3][2]}</b> грн.
            5. {value_list_buy[4][0]} - <b>{value_list_buy[4][2]}</b> грн.
             ''')


# @dp.message(F.text == '/change')
async def change_option_bank(message:Message, bot: Bot) -> None:
    await message.answer(text='Виберить спосіб обміну', reply_markup=star_keyboard())



# @dp.message(F.text == '/start')
async def send_welcome(message: Message) -> None:
    await DataBaseCommand.reg_new_user(
        message.from_user.first_name,
        message.from_user.last_name,
        message.from_user.id)
    await message.answer(
        f'Привіт {message.from_user.first_name},\
            вибери яким способом ти хочеш обміняти валюту',
                         reply_markup= star_keyboard())
    logging.debug(
        f"Користувач {message.from_user.first_name} {message.from_user.last_name}\
            виконав команду ['help', 'start']")


# @dp.callback_query(F.data.in_({'cashdesk', 'card', 'main'}))
async def callback_bank_opinion(callback: CallbackQuery, bot: Bot) -> None:
    DB = DataBaseCommand
    if callback.data == 'cashdesk':
        await DB.add_bank_options('cashdesk', callback.from_user.id)
        await callback.message.answer('Вибрано обмін у кассі',\
                                    reply_markup= bank_opinion())
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
        await callback.answer(text='Ваші дані записано в БД')
        await callback.answer()
    elif callback.data == 'card':
        await DB.add_bank_options('card', callback.from_user.id)
        await callback.message.answer('Вибрано обмін карткою',
                                       reply_markup=bank_opinion())
        await callback.answer(text='Ваші дані записано в БД')
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
        await callback.answer()


async def show_bank_opinion(message:Message):
    DB = DataBaseCommand
    opinion = await DB.get_user_setting(message.from_user.id)
    if opinion == 'card':
        await message.answer(text='Вибрано обмін при оплаті карткою')
    elif opinion == 'cashdesk':
        await message.answer(text='Вибрано обмін у касах банку')
