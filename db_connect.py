import pymongo as pymongo
from typing import Union

import config

db_client = pymongo.MongoClient(config.site_db)
current_db = db_client["autopapa"]
collection = current_db["autopapa"]


def create_data_db(data_list: Union[dict]) -> bool:
    """Создает БД
    :param data_list: dict словарь с данными об автомобиле
    :return: Bool
    """
    try:
        collection.insert_one(data_list)
        config.logging.info(f"Добавлен документ {data_list['id']}")
        return True
    except Exception as e:
        config.logging.error(f"Ошибка добавления документа {data_list['id']}", e)
        return False


def car_link() -> list:
    """Возвращает список ссылок на автомобили
    :return: list список ссылок на автомобили
    """
    link: list = []
    try:
        for channel in collection.find():
            car = channel.get("link")
            link.append(car)
            config.logging.info(f"Получена ссылка на автомобиль {car}")
    except Exception as e:
        config.logging.error(f"Ошибка получения ссылки на автомобиль", e)
        return []
    return link


def test_double_delete() -> None:
    """Удаляет дубликаты из БД
    :return: None
    """
    docs = list(collection.find())
    unique_docs: list = []
    for doc in docs:
        if doc['id'] not in unique_docs:
            unique_docs.append(doc['id'])
            config.logging.info(f"Добавлен документ {doc['id']}")
        else:
            collection.delete_one({'id': doc['id']})
            config.logging.info(f"Удален документ {doc['id']}")
    config.logging.info(f"Удалено {len(docs) - len(unique_docs)} дубликатов")


def add_if_not_exists(auto: dict):
    """Добавляет документ в БД, если его там нет, а если есть, то обновляет его
    :param auto: dict словарь с данными об автомобиле
    :return: Bool
    """
    config.logging.info(f"Добавление документа {auto['id']}")
    if not collection.find_one({'id': auto['id']}):
        result = collection.insert_one(auto)
        config.logging.info(f"Добавлен документ {result.inserted_id}")
        return True
    else:
        result = collection.update_one({'id': auto['id']}, {'$set': auto})
        config.logging.info(f"Обновлен документ {result.modified_count}")
        return False


def test_openai():
    """Тестовая функция
    :return: None
    """
    test_double_delete()
    docs = collection.find({'id': '772984'})
    for doc in docs:
        print(doc)
        config.logging.info(f"Получен документ {doc['id']}")


def test_print():
    """Тестовая функция
    :return: None
    """
    docs = list(collection.find({}))
    for doc in docs:
        print(doc)


def test_remove_documents_with_name_car():
    """Удаляет документы с полем name_car
    :return: None
    """
    result = collection.delete_many({'name_car': {'$exists': True}})
    print(f"Deleted {result.deleted_count} documents")

