# -*- coding: utf-8 -*-

from config import API_KEY_TG
import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from core.classes import DataBaseCommand, Data_Manipulation
from app.handlers import main_message, change_option_bank, send_welcome, \
    callback_bank_opinion, show_bank_opinion
from app.commands import set_commands


async def main():
    bot = Bot(API_KEY_TG, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    await set_commands(bot)
    dp.message.register(send_welcome, F.text == '/start')
    dp.message.register(change_option_bank, F.text == '/change')
    # UA: При додаванні нових валют, сюди додати її назву
    # EN: When adding new currencies, add its name here
    dp.message.register(main_message, F.text.in_({'USD', 'EUR', 'PLN'}))
    dp.message.register(send_welcome, F.text == 'Змінити спосіб обміну')
    dp.callback_query.register(callback_bank_opinion,
                               F.data.in_({'cashdesk', 'card', 'main'}))
    dp.message.register(show_bank_opinion, F.text == '/show')

    await asyncio.gather(DataBaseCommand.db_initialization(),
                         Data_Manipulation().info_in_files(),
                         dp.start_polling(bot))


if __name__ == '__main__':
    logging.basicConfig(filename='log.txt', level=logging.DEBUG,
                        format='%(levelname)s: %(asctime)s - %(message)s')
    logging.debug("Бот запущений")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Вихід зпрограми")
        logging.debug("Ручне закритя бота")
