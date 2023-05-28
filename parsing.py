from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
from test_db_mongo import create_data_db

url = 'https://autopapa.ge/ru/search?utf8=%E2%9C%93&s%5Bprice_from%5D=20000&s%5Bprice_to%5D=50000&s%5Bbrand_id%5D=0&s%5Bmodel_id%5D=0&s%5Bperiod%5D=0&s%5Byear_from%5D=0&s%5Byear_to%5D=0&s%5Bmileage_from%5D=0&s%5Bmileage_to%5D=0&s%5Bcountry_id%5D=2&s%5Bcity_id%5D=2&s%5Bcondition%5D=0&s%5Bengine_type%5D%5B%5D=14&s%5Bengine_capacity_from%5D=0&s%5Bengine_capacity_to%5D=0&s%5Bpower_from%5D=0&s%5Bpower_to%5D=0&s%5Bgearbox%5D%5B%5D=62&s%5Bdoor_qty%5D=0&s%5Bseats_count%5D=0&s%5Bmaterial%5D=0&s%5Bcolor_finish%5D=0'


def parsing_auto(url: str):
    res = requests.get(url, headers={'User-Agent': UserAgent().random})
    soup = BeautifulSoup(res.text, 'lxml')
    cars = soup.find_all('div', class_='boxCatalog2')

    # Собираем информацию для каждого автомобиля
    car_info_list = []
    for car in cars:
        info = {}
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
    print(sorted_car_list)
    return car_info_list


def main():
    result = create_data_db(parsing_auto(url=url))


if __name__ == '__main__':
    main()
