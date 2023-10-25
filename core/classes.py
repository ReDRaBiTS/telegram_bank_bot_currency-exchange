import aiosqlite
from sqlite3 import Error
import aiohttp
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import pickle
import logging
import os
import asyncio



def db_path():
    data_base_name = "db.sqlite"
    directory = os.path.abspath(os.path.join('data'))
    if not os.path.exists(directory):
        os.makedirs(directory)
    db_path = os.path.join(directory, data_base_name)
    return  db_path
    
class DataBaseCommand:
    
    async def db_initialization() -> None:
        '''
        EN:Initializing the database and creating tables
        UA:Ініціалізація БД та створення таблиць
        '''


        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute(
                'CREATE TABLE IF NOT EXISTS users (\
                first_name VARCHAR(50), \
                last_name VARCHAR(50),\
                user_id INTEGER PRIMARY KEY\
                )'
            )
            await db.commit()
            await cursor.execute(
                'CREATE TABLE IF NOT EXISTS users_options \
                (user_id INTEGER PRIMARY KEY, bank_option VARCHAR(20))'
            )
            await db.commit()
            logging.debug("Встановлено з'єднання до БД")

    async def reg_new_user(
            first_name: str,
            last_name: str,
            user_id: int) -> None:

        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            try:
                example = await cursor.execute(
                    'SELECT EXISTS(SELECT (user_id) FROM users WHERE user_id = %d)' 
                    % user_id)
                example = await example.fetchall()
                if int(example[0][0]) == 0:
                    await cursor.execute(
                        'INSERT INTO users (first_name, last_name, user_id) VALUES ("%s", "%s"," %d")'
                        % (first_name, last_name, user_id))
                    await db.commit()
                    logging.debug('Запис у БД даних кристувача')
            except Error:
                print(Error)

    async def add_bank_options(bank_options: str, user_id: int) -> None:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            try:
                example = await cursor.execute(
                    'SELECT EXISTS(SELECT (bank_option) FROM users_options WHERE user_id = %d)' % user_id)
                example = await example.fetchall()
                if int(example[0][0]) == 0:
                    await cursor.execute(
                        'INSERT INTO users_options (user_id ,bank_option) VALUES (%d ,"%s")' % (user_id, bank_options))
                    await db.commit()
                if int(example[0][0]) == 1:
                    await cursor.execute(
                        'UPDATE users_options SET bank_option ="%s" WHERE user_id = %d' % (bank_options, user_id,))
                    await db.commit()
            except Error:
                print(Error)

    async def get_user_setting(user_id: int) -> None:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            try:
                data = await cursor.execute(
                    'SELECT bank_option FROM users_options WHERE user_id = %d' % user_id)
                data = await data.fetchall()
                return data[0][0]
            except Error:
                print(Error)


class Bank_Sites:

    def __init__(self) -> None:  # При додаванні нових валют, сюди додати посилання з сайту НБУ

        self.usd_link = 'https://minfin.com.ua/ua/currency/banks/usd/'
        self.eur_link = 'https://minfin.com.ua/ua/currency/banks/eur/'
        self.pln_link = 'https://minfin.com.ua/ua/currency/banks/pln/'

    async def get_html(self, link:str) -> str:
        '''
        EN: The function of receiving requests from the NBU website
        UA: Функція отримання запиту з сайту НБУ
        '''
        ua = UserAgent()
        headers = {"User-Agent": ua.chrome}
        async with aiohttp.ClientSession() as session:
            async with session.get(link, headers=headers) as response:
                return await response.text()

    async def parsing_allbanks(self, currency:str) -> list:
        '''
        EN: The function parses currency exchange data and converts it to a list 
            ({Bank name, exchange at cash desks, exchange when paying by card})
        UA: Функція парсить дані обміну валют та конвертує у список 
            ({Назва банку, обмін в касах, обмін при оплаті карткою])
        '''
        # UA: При додаванні нових валют, сюди додати її назву
        # EN: When adding new currencies, add its name here
        if currency == 'USD':
            link = self.usd_link
        elif currency == 'EUR':
            link = self.eur_link
        elif currency == 'PLN':
            link = self.pln_link
        bank_link = await self.get_html(link)
        bank_html = BeautifulSoup(bank_link, 'lxml')
        bank_USD = bank_html.find(
            'div', class_="mfm-grey-bg").find_all('td', class_="js-ex-rates mfcur-table-bankname")
        main_list = []
        for line in bank_USD:
            exchange_cart = line.get('data-card')
            exchange_desk = line.get('data-title')
            bank_name = line.text.strip('\n')
            temp_list = [bank_name, exchange_desk, exchange_cart]
            main_list.append(temp_list)
        logging.debug('Дані з сайта НБУ завантажені')
        return main_list

    def format_price_list(self, banks_list: list, exchange_option: str) -> tuple:
        '''
        # Перетворює загальний список у список лише з даними о курсах валют
         або у касах або по картці у форматі [Назва бунку, купівля, продаж]
        '''

        if exchange_option == 'cashdesk':
            index_ = 1
        elif exchange_option == 'card':
            index_ = 2
        exit_list = []
        for v in banks_list:
            sell = v[index_].strip()
            sell = sell[:4]
            buy = v[index_].strip()
            buy = buy[-6:-1]
            if buy == '/0.00':
                buy = v[index_].strip()
                buy = buy[-5:-1]

            try:
                sell = float(sell)
                buy = float(buy)
            except BaseException as BE:
                logging.error(f"Неможливо конвертувати строку у числа {v[0]}, {v[1]}, {v[2]} \n {BE}  ")
            if sell == 0 or buy == 0:
                pass
            else:
                temp_list = [v[0], sell, buy]
                exit_list.append(temp_list)

        return tuple(exit_list)


class Data_Manipulation:

    def __init__(self) -> None:
        self.bank = Bank_Sites()
        # UA: При додаванні нових валют, сюди додати її назву
        # EN: When adding new currencies, add its name here
        self.currency_list = ['USD', 'EUR', 'PLN']
        self.exchange_opinion = ['cashdesk', 'card']

    async def info_in_files(self) -> None:
        '''
        UA: Записує списки отриманих даних у бінарні файли
        EN: Writes lists of received data to binary files
        '''
        directory = os.path.abspath(os.path.join('data'))
        if not os.path.exists(directory):
            os.makedirs(directory)
        while True:
            for currency in self.currency_list:
                for opinion in self.exchange_opinion:
                    file_path = os.path.join(directory, f'Recent_exchange_rates_{opinion}_{currency}.bin')
                    with open(file_path, 'wb') as file:
                        not_format_data = await self.bank.parsing_allbanks(currency)
                        format_data = self.bank.format_price_list(not_format_data, opinion)
                        pickle.dump(format_data, file)
                        logging.debug('Дані з сайта НБУ Записані у файл')
            await asyncio.sleep(3600)

    def load_currency_info(self, exchange_opinion, currency) -> list:
        directory = os.path.abspath(os.path.join('data'))
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, f'Recent_exchange_rates_{exchange_opinion}_{currency}.bin')
        if currency in self.currency_list and exchange_opinion in self.exchange_opinion:
            with open(file_path, 'rb') as file:
                return pickle.load(file)


class Printing_Information_in_Message:

    def __init__(self, exchange_option: str, currency_name: str) -> None:
        self.BS = Bank_Sites()
        self.DM = Data_Manipulation()
        self.currency_name = currency_name
        self.exchange_option = exchange_option

    def print_rate(self) -> str:
        data = self.DM.load_currency_info(
            self.exchange_option, self.currency_name)
        return data[:6]
    
