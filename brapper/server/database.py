from pymongo import MongoClient

db_client = MongoClient("mongodb://localhost:27017")


def __save_charmap(vocabulary: list, model_name: str) -> None:
    VOCABS_PATH.mkdir(exist_ok=True, parents=True)
    with open(VOCABS_PATH.joinpath(model_name), "w+", encoding="utf-8") as v_file:
        json.dump(vocabulary, v_file)


def __load_charmap(model_name: str) -> list:
    with open(VOCABS_PATH.joinpath(model_name), "r", encoding="utf-8") as v_file:
        return json.load(v_file)
