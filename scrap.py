import aiohttp
import asyncio
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


class Bank_Sites:

    ua = UserAgent()
    _headers = {"User-Agent": ua.chrome}

    def __init__ (self):

        self.usd_link = 'https://minfin.com.ua/ua/currency/banks/usd/'
        self.eur_link = 'https://minfin.com.ua/ua/currency/banks/eur/'
        
    async def get_html(self, link):
        '''
        Функція отримання запит з сайту НБУ
        '''
    
        async with aiohttp.ClientSession() as session:
            async with session.get(link, headers = _headers) as response:
                return await response.text()
    
    async def parsing_allbanks(self, link) -> list:
        
        '''
        Функція парсить дані обміну валют та конвертує у список ({Назва бунку, обмін в касах, обмін при оплаті карткою])
        '''

        bank_link =  await self.get_html(link)
        bank_html = BeautifulSoup(bank_link, 'lxml')
        bank_USD = bank_html.find('div', class_="mfm-grey-bg").find_all('td', class_="js-ex-rates mfcur-table-bankname")
        main_list = []       
        for line in bank_USD:
            exchange_cart = line.get('data-card')
            exchange_desk=  line.get('data-title')
            bank_name = line.text.strip('\n')
            temp_list = [bank_name,exchange_desk, exchange_cart]
            main_list.append(temp_list)
        
        return  main_list
    
    
    
    def get_cash(self, bank_list:list, cashdesk_or_card:str):
        
        '''
        # Перетворює загальний список у список лише з даними о курсах валют або у касах або по картці у форматі [Назва бунку, купівля, продаж]
        '''

        if cashdesk_or_card == 'cashdesk':
            index_=1
        elif cashdesk_or_card == 'card':
            index_=2
        exit_list=[]
        for v in bank_list:
            sell = v[index_].strip()
            sell=sell[:4]
            buy = v[index_].strip()
            buy=buy[-6:-1]
            try:
                sell = float(sell)
                buy = float(buy)
            except BaseException:
                print ("Неможливо конвертувати строку у числа")
            if sell == 0 or buy ==0:
                pass
            else:
                temp_list=[v[0], sell,buy]
                exit_list.append(temp_list)
           
        return tuple(exit_list)

    async def main(self):
        usb_dict = await self.parsing_allbanks(self.usd_link)
        with open('Recent_exchange_rates.txt','w') as file:
            file.write(str(usb_dict))
        asyncio.sleep(3600)
        print(sorted(self.get_cash(usb_dict, 'cashdesk'), key= lambda X: X[1]))
        


bank_sites = Bank_Sites()
asyncio.run(bank_sites.main())