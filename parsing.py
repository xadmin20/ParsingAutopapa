import json
import os
import time
import re

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests

import config
import db_connect


def html_code(url: str):
    """Получение html кода страницы
    :param url: https url страницы
    :return dict {'url': url, 'BeautifulSoup': BeautifulSoup}
    """
    url_and_html = {}
    res = requests.get(url, headers={'User-Agent': UserAgent().random})
    soup: BeautifulSoup = BeautifulSoup(res.text, 'lxml')
    url_and_html['url'] = url
    url_and_html['html'] = soup
    config.logging.info(f"Получен html код страницы {url}")
    return url_and_html


def parsing_auto(html: dict) -> list:
    """Парсинг страницы с автомобилями
    :param html: dict {'url': url, 'BeautifulSoup': BeautifulSoup}
    :return: list [{'name_car': str, 'link': str, 'image_link': str, 'description': str}]
    """
    cars = html['html'].find_all('div', class_='boxCatalog2')
    # Собираем информацию для каждого автомобиля
    car_info_list: list = []
    for car in cars:
        info: dict = {}
        # Имя и тип автомобиля
        name_car = car.find('div', class_='titleCatalog')
        if name_car:
            info['name_car'] = name_car.text.strip()
        # Ссылка на автомобиль
        link = car.find('a', href=True)
        if link:
            info['link'] = f"https://autopapa.ge{link['href']}"
            info['id'] = str(link['href']).split('/')[-1]
        # Ссылка на изображение автомобиля
        image = car.find('img', src=True)
        if image:
            info['image_link'] = image['src']
        # Описание автомобиля
        description = car.find('div', class_='paramCatalog')
        if description:
            cleaned_description = description.text.replace('\n', ' ').replace('\t', '').replace('\xa0', ' ')
            info['description'] = cleaned_description.strip()
        car_info_list.append(info)

    sorted_car_list = sorted(car_info_list, key=lambda x: int(x['id']), reverse=True)
    config.logging.info(f"Получена информация о {len(sorted_car_list)} автомобилях")
    return sorted_car_list


def get_info_car(html) -> dict:
    """Получение всей информации об автомобиле
    :param html: dict {'url': url, 'BeautifulSoup': BeautifulSoup}
    :return: dict {'name': str, 'price': str, 'link': str, 'currency': str, 'exchange_rate': str...}
    """
    info: dict = {}
    soup = html
    try:
        title_object = soup.find('div', class_='titleObject')
        if title_object is not None:
            name = title_object.contents[0].strip()
        else:
            name = ''
        result = soup.find('title').text
        title = re.search(r'\(# (\d+)\)', result)
        if title is not None:
            info['id'] = title.group(1)
        price = title_object.find('span', class_='priceObject').contents[0].strip()
        currency = title_object.find('span', class_='lari').contents[0]
        exchange_rate = title_object.find('a', class_='popup-calc').contents[0]
        div = html.find('div', class_="contactObjectNew").find('div')
        text_parts = div.contents[:4]
        address = text_parts[0].strip()
        customs_status = text_parts[3].get_text().replace(u'\xa0', u' ')
        nameInfoObject = html.find_all('div', class_="nameInfoObject")
        print(f"Название: {name}")
        if html.find('div', class_='vincode-wrap-ads'):
            print('VIN предоставлен')
        else:
            print('VIN НЕ предоставлен')
        print(f"Цена: {price} {currency} ({exchange_rate})")
        print(f"Адрес: {address} ({customs_status})")
        for info_car in nameInfoObject:
            print(info_car.text)
        time.sleep(2)
        info['name'] = name
        info['price'] = price
        info['link'] = f"https://autopapa.ge/ru/text_search?text_s={info['id']}"
        info['currency'] = currency
        info['exchange_rate'] = exchange_rate
        info['address'] = address
        info['customs_status'] = customs_status
        info['nameInfoObject'] = ' '.join([info_car.text for info_car in nameInfoObject])
        send_to_db = db_connect.add_if_not_exists(info)
        if send_to_db:
            config.logging.info(f"Данные успешно отправлены в БД")
        else:
            config.logging.info(f"Данные не отправлены в БД")
        return info
    except Exception as e:
        config.logging.error(f"Ошибка при получении информации об автомобиле {e}")


def save_photo_car(url: str):
    """ Сохраняем все фотографии автомобиля в папку img
    :param url: str ссылка на страницу с автомобилем
    :return: Bool
    """
    try:
        config.logging.info(f"Сохраняем фотографии автомобилей")
        soup = html_code(url=url)
        base_url: str = 'https://autopapa.ge'
        for link in soup['html'].find_all('a', class_='hidden-galler-images fancybox'):
            img_url = base_url + link.get('href')
            img_id = url.split('/')[-1]
            dir_path = os.path.join('img', img_id)
            os.makedirs(dir_path, exist_ok=True)
            response = requests.get(img_url)
            filename = img_url.split('/')[-1].replace('?', '-')
            orig_filename, id_filename = filename.split('-')
            new_filename = f"{id_filename}-{orig_filename}"
            with open(os.path.join(dir_path, new_filename), "wb") as file:
                file.write(response.content)
        config.logging.info(f"Автомобиль по адресу {url} сохранен")
        return True
    except Exception as e:
        config.logging.error(f"Ошибка при сохранении фотографий автомобиля {e}")
        return False


def main():
    """ Главная функция
    :return: None
    """
    result = parsing_auto(html=html_code(url=config.url_main))  # Список ссылок автомобилей
    if result:
        config.logging.info(f"Получена информация о {len(result)} автомобилях")
    else:
        config.logging.info(f"Не удалось получить информацию об автомобилях")
    #
    for url_ in result:
        html = html_code(url=url_['link'])
        info_car = get_info_car(html=html['html'])
        time.sleep(3)
        img_id = url_['link'].split('/')[-1]
        dir_path = os.path.join('img', img_id)
        os.makedirs(dir_path, exist_ok=True)
        with open(os.path.join(dir_path, f"{img_id}.json"), "w", encoding="utf-8") as file:
            file.write(json.dumps(info_car, ensure_ascii=False, indent=4))
        save_photo_car(url=url_['link'])


if __name__ == '__main__':
    """Запуск скрипта
    :return: None
    """
    config.logging.info(f"Запуск скрипта")
    main()
