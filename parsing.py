import os
import time

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests

import db_connect

url_main = 'https://autopapa.ge/ru/search?utf8=%E2%9C%93&s%5Bprice_from%5D=20000&s%5Bprice_to%5D=50000&s%5Bbrand_id' \
           '%5D=0&s%5Bmodel_id%5D=0&s%5Bperiod%5D=0&s%5Byear_from%5D=0&s%5Byear_to%5D=0&s%5Bmileage_from%5D=0&s' \
           '%5Bmileage_to%5D=0&s%5Bcountry_id%5D=2&s%5Bcity_id%5D=2&s%5Bcondition%5D=0&s%5Bengine_type%5D%5B%5D=14&s' \
           '%5Bengine_capacity_from%5D=0&s%5Bengine_capacity_to%5D=0&s%5Bpower_from%5D=0&s%5Bpower_to%5D=0&s' \
           '%5Bgearbox%5D%5B%5D=62&s%5Bdoor_qty%5D=0&s%5Bseats_count%5D=0&s%5Bmaterial%5D=0&s%5Bcolor_finish%5D=0'


def html_code(url: str) -> BeautifulSoup:
    res = requests.get(url, headers={'User-Agent': UserAgent().random})
    soup: BeautifulSoup = BeautifulSoup(res.text, 'lxml')
    return soup


def parsing_auto(html: BeautifulSoup) -> list:
    cars = html.find_all('div', class_='boxCatalog2')
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
    return sorted_car_list


def get_info_car(html):
    """
    Получение всей информации о автомобиле
    """
    title_object = html.find('div', class_='titleObject')
    name = title_object.contents[0].strip()
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


def save_photo_car(url_list: list[str]):
    """ Сохраняем все фотографии автомобиля в папку img """
    try:
        for url in url_list:
            soup = html_code(url)
            base_url: str = 'https://autopapa.ge'
            for link in soup.find_all('a', class_='hidden-galler-images fancybox'):
                img_url = base_url + link.get('href')
                print(img_url)
                img_id = url.split('/')[-1]
                print(img_id)
                dir_path = os.path.join('img', img_id)
                os.makedirs(dir_path, exist_ok=True)
                response = requests.get(img_url)
                print(response)
                filename = img_url.split('/')[-1].replace('?', '-')
                orig_filename, id_filename = filename.split('-')
                new_filename = f"{id_filename}-{orig_filename}"
                print(new_filename)
                file = open(os.path.join(dir_path, new_filename), "wb")
                file.write(response.content)
                file.close()
                time.sleep(1)
            print(f"Автомобиль по адресу {url} сохранен")
        return True
    except Exception as e:
        print(e)
        return False


def main():
    # result = create_data_db(parsing_auto(url=url))
    # if result:
    #     print("Данные успешно получены")
    # else:
    #     print("Ошибка!")
    #
    for result in db_connect.car_link():
        print(f'{result}')
        get_info_car(html_code(url=result))
        print('################################################')
        time.sleep(3)


if __name__ == '__main__':
    main()
