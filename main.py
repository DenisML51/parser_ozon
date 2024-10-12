import json
import time
import undetected_chromedriver as uc 
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.ui import WebDriverWait

import pandas as pd 
import numpy as np


def page_down(driver):
    driver.execute_script('''
        const scrollStep = 200;
        const scrollInterval = 80;

        const scrollHeight = document.documentElement.scrollHeight;
        let currentPosition = 0;
        const interval = setInterval(() => {
            window.scrollBy(0, scrollStep);
            currentPosition += scrollStep;

            if (currentPosition >= scrollHeight) {
                clearInterval(interval);
            }
        }, scrollInterval);
    ''')


def get_url(data):
    data = pd.read_excel(data)
    data = data['Ссылка на товар']
    return data
    

def get_info(url):
    driver = uc.Chrome()
    driver.implicitly_wait(5)

    driver.get(url=url)
    time.sleep(2)

    page_down(driver=driver)
    time.sleep(2)

    page_source = str(driver.page_source)
    soup = BeautifulSoup(page_source, features="lxml")
    stat = soup.find('div', attrs={"id" : "section-characteristics"})
    if stat:
        info_stat = stat.find_all('dd', {'class' : 'xk2_27'})
        info_name = stat.find_all('dt', {'class' : 'k2x_27'})
        
        info = {}
        for i in range(len(info_stat)):
            info[info_name[i].text] = info_stat[i].text
    else:
        print(f"Характеристики квартиры не найдены на странице: {url}")

    driver.quit()
    return info

def add_info(info, data):
    data['info'] = info
    return True

if __name__ == '__main__':
    url = get_url('ozon_data.xlsx')
    data = pd.read_excel('ozon_data.xlsx')

    parsed = {}
    for i in range(3):
        info = get_info(url[i])
        parsed[f'{url[i]}'] = info

    df_parsed = pd.DataFrame([parsed]).T
    df_parsed.to_excel('new_ozo.xlsx')