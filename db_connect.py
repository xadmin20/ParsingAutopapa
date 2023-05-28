import pymongo as pymongo
from typing import Union

import config

db_client = pymongo.MongoClient(config.site_db)


def create_data_db(data_list: Union[dict]) -> bool:
    """Создает БД"""
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
    """Возвращает список ссылок на автомобили"""
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


def test_double_delete() -> None:
    """Удаляет дубликаты из БД"""
    current_db = db_client["autopapa"]
    collection = current_db["autopapa"]
    docs = list(collection.find())
    unique_docs: list = []

    for doc in docs:
        if doc['id'] not in unique_docs:
            print(f"Добавлен уникальный документ {doc['id']}")
            unique_docs.append(doc['id'])
        else:
            collection.delete_one({'id': doc['id']})
            print(f"Удален дубликат {doc['id']}")
    print(f"Удалено {len(docs) - len(unique_docs)} дубликатов")


def test_openai():
    """Тестовая функция"""
    test_double_delete()
    current_db = db_client["autopapa"]
    collection = current_db["autopapa"]
    docs = collection.find({'id': '772984'})
    for doc in docs:
        print(doc)


test_openai()
