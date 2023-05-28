from db_connect import *


def test_create_data_db():
    try:
        current_db = db_client["autopapa"]
        collection = current_db["autopapa"]
        for channel in collection.find():
            print(channel.items())
    except Exception as e:
        print("Error creating", e)


if __name__ == '__main__':
    # test_create_data_db()
    car_link()
