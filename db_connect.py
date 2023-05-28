import pymongo as pymongo
from typing import Union

import config

db_client = pymongo.MongoClient(config.site_db)


def create_data_db(data_list: Union[dict]) -> bool:
    """ Создаем в БД записи из парсинга"""
    try:
        current_db = db_client["autopapa"]
        collection = current_db["autopapa"]
        collection.insert_many(data_list)

        for channel in collection.find():
            print(channel.keys())
        return True
    except Exception as e:
        print("Error creating", e)
        return False


def car_link() -> list:
    """ Формирует список из ссылок """
    link: list = []
    try:
        current_db = db_client["autopapa"]
        collection = current_db["autopapa"]
        for channel in collection.find():
            car = channel.get("link")
            link.append(car)
    except Exception as e:
        print("Error reed", e)
        return []
    return link


