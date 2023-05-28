import pymongo as pymongo
from typing import Union


db_client = pymongo.MongoClient("mongodb+srv://xadmin:valenok@cluster0.0zbzipn.mongodb.net/?retryWrites=true&w=majority")


def create_data_db(data_list: Union[dict]):
    try:
        current_db = db_client["autopapa"]
        collection = current_db["autopapa"]
        collection.insert_many(data_list)

        for channel in collection.find():
            print(channel.keys())
        return True
    except Exception as e:
        print("Error creating", e)


def test_create_data_db():
    try:
        current_db = db_client["autopapa"]
        collection = current_db["autopapa"]
        for channel in collection.find():
            print(channel.items())
    except Exception as e:
        print("Error creating", e)
