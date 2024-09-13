import re
import time
import gspread
import datetime
from multiprocessing import Pool

from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver as Chromedriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_driver():
    options = ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    # options.add_argument('--disable-extensions')
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0")
    options.add_argument('--no-sandbox')
    driver = Chromedriver(options=options)

    return driver


def validator_url_hh(url):
    if 'https://hh.ru/vacancy/' in url:
        url = re.sub(r'\?.*', "?host=hh.ru", url)

    elif 'adsrv.hh.ru' in url:
        try:
            driver = create_driver()
            driver.implicitly_wait(3)
            driver.get(url)
            current_url = driver.current_url
            url = re.sub(r'\?.*', "?host=hh.ru", current_url)
        except TimeoutException:
            pass
        finally:
            driver.close()
            driver.quit()

    elif 'from=employer' in url:
        url = re.sub(r'\?.*', "?host=hh.ru", url)

    return url


def get_pages_count_hh(vacancy):
    driver = create_driver()
    driver.get(f'https://hh.ru/search/vacancy?text={vacancy}&area=1')
    time.sleep(10)
    element = driver.find_element(by=By.TAG_NAME, value='nav')
    page_list = [i for i in element.find_elements(by=By.TAG_NAME, value='li')]
    pages = int(page_list[-2].text)
    driver.close()
    driver.quit()

    return pages


def search_vacancy_hh(vacancy_url):
    vacancy_url = validator_url_hh(vacancy_url)
    driver = create_driver()
    pages = get_pages_count_hh(vacancy)
    data = []
    flag = False
    for page in range(0, pages + 1):
        driver.get(f'https://hh.ru/search/vacancy?text={vacancy}&area={area}&page={page}')
        vacancy_cards = driver.find_elements(by=By.CLASS_NAME, value='vacancy-info--umZA61PpMY07JVJtomBA')
        current_position = 1
        for vacancy_card in vacancy_cards:
            url = vacancy_card.find_element(by=By.TAG_NAME, value='a').get_attribute('href')
            url = validator_url_hh(url)
            if url == vacancy_url:
                current_page = page
                flag = True
                break
            current_position += 1

        if flag:
            current_page = current_page + 1
            if current_page == 41:
                current_page = 40
            current_date = datetime.datetime.now().strftime('%d-%m-%Y')
            dt = datetime.datetime.now()
            current_time = f"{dt.hour}:{dt.minute}"
            data.append(current_date)
            data.append(current_time)
            if area == 1:
                data.apeend('Мск')
            else:
                data.append('Спб')
            data.append(vacancy)
            data.append(vacancy_url)
            data.append(current_page)
            data.append(current_position)
            wks = gc.open("Вакансии").sheet1
            wks.append_row(data)
            driver.close()
            driver.quit()
            return

    driver.close()
    driver.quit()


def search_vacancy_avito(vacancy_url):
    data = []
    driver = create_driver()
    driver.get(f"https://www.avito.ru/{area}/vakansii?q={vacancy}")
    position = 1
    current_page = 1
    flag = False
    while True:
        time.sleep(3)
        vacancy_cards = driver.find_elements(by=By.CLASS_NAME, value='iva-item-content-rejJg')
        for vacancy_card in vacancy_cards:
            url = vacancy_card.find_element(by=By.TAG_NAME, value='a').get_attribute('href')
            if vacancy_url == url:
                current_position = position
                flag = True
                break
            position += 1
        position = 1

        if flag:
            break

        try:
            wait = WebDriverWait(driver, 10)
            next_page = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-marker="pagination-button/nextPage"]')))
            next_page.click()
            time.sleep(2)
            current_page += 1
        except NoSuchElementException as ex:
            print(ex, "Error in block 1")
            current_position = 'Не найдено'
            current_page = 'Не найдено'
            break

        except TimeoutException:
            current_position = 'Не найдено'
            current_page = 'Не найдено'
            break

    current_date = datetime.datetime.now().strftime('%d-%m-%Y')
    dt = datetime.datetime.now()
    current_time = f"{dt.hour}:{dt.minute}"
    data.append(current_date)
    data.append(current_time)
    if area == 'moskva':
        data.append('Мск')
    else:
        data.append('Спб')
    data.append(vacancy)
    data.append(vacancy_url)
    data.append(current_page)
    data.append(current_position)
    wks = gc.open("Вакансии").get_worksheet(1)
    wks.append_row(data)
    driver.close()
    driver.quit()


if __name__ == "__main__":
    gc = gspread.service_account(filename='../pythonMonitoringAvitoHH/key.json')
    print('Выберите платформу для мониторинга\n'
          '\n'
          'Введите 1 - HH.ru\n'
          'Введите 2 - Avito\n')
    choice = int(input('Введите: '))
    if choice == 1:
        area = int(input('Выберите регион поиска\n'
                        '1 - Москва\n'
                        '2 - Санкт-Петербург\n'
                        'Введите: '))
        vacancy = input('Введите название вакансии: ')
        print()
        vacancy_url = input('Введите ссылку на вакансию\n'
                            'Если ссылок несколько, введите их через пробел: ')
        iter_url = vacancy_url.split()
        print()
        print('Запускаю мониторинг...')
        print()
        p = Pool(processes=5)
        p.map(search_vacancy_hh, iter_url)
        print("Готово")


    else:
        area = int(input('Выберите регион поиска\n'
                        '1 - Москва\n'
                        '2 - Санкт-Петербург\n'
                        'Введите: '))
        if area == 1:
            area = 'moskva'
        else:
            area = 'sankt-peterburg'
        vacancy = input('Введите название вакансии: ')
        print()
        vacancy_url = input('Введите ссылку на вакансию\n'
                            'Если ссылок несколько, введите их через пробел: ')
        iter_url = vacancy_url.split()
        print()
        print('Запускаю мониторинг...')
        print()
        p = Pool(processes=5)
        p.map(search_vacancy_avito, iter_url)
        print("Готово")
