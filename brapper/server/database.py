from pymongo import MongoClient, errors as pymongo_errors
from bson.objectid import ObjectId
from datetime import datetime

from brapper.config.server_config import DB_PASS, DB_URI, DB_USER, DB_TIME_FORMAT


client = MongoClient(f"mongodb+srv://{DB_USER}:{DB_PASS}@{DB_URI}")
db = client.brapper


class BaseDAODTO(dict):

    db_name = None

    def __init__(self, _id=None, created: datetime = None):
        if _id:
            self._id = _id
        if created == None:
            self.created = datetime.now()
        elif isinstance(created, str):
            self.created = datetime.strptime(created, DB_TIME_FORMAT)
        else:
            self.created = created

    def __setattr__(self, name, value):
        self[name] = value

    def __getattr__(self, name):
        return self[name]

    def save(self):
        self.created = datetime.now()
        try:
            result = db[self.db_name].insert_one(self)
            self._id = result.inserted_id
        except pymongo_errors.DuplicateKeyError:
            query = {"_id": self._id}
            new_values = {"$set": self}
            db[self.db_name].update_one(query, new_values)
        finally:
            return self

    def delete(self):
        query = {"_id": self._id}
        return db[self.db_name].delete_one(query)

    def to_json(self):
        copy = self.copy()
        copy["_id"] = str(copy.get("_id"))
        return copy

    def is_newer(self, days_old: int) -> bool:
        try:
            return (datetime.now() - self.created).days < days_old
        except TypeError:
            return False

    @classmethod
    def get_all(cls) -> list:
        result = list(db[cls.db_name].find())
        return [cls.load_from_dict(db_entry) for db_entry in result]

    @classmethod
    def get_by_id(cls, _id: str):
        result = db[cls.db_name].find_one({"_id": ObjectId(_id)})
        return cls.load_from_dict(result)

    @classmethod
    def load_from_dict(cls, db_dict: dict):
        raise NotImplementedError("Must be overriden in the derived class")


class LyricsDAODTO(BaseDAODTO):

    db_name = "lyrics"

    def __init__(
        self,
        artist: str,
        lyrics: str,
        song_count: int,
        created: datetime = None,
        _id=None,
    ):
        super().__init__(_id, created)
        self.artist = artist
        self.lyrics = lyrics
        self.song_count = song_count

    @staticmethod
    def load_from_dict(db_dict: dict):
        return LyricsDAODTO(
            db_dict.get("artist"),
            db_dict.get("lyrics"),
            db_dict.get("song_count"),
            db_dict.get("created"),
            db_dict.get("_id"),
        )


class VocabDAODTO(BaseDAODTO):

    db_name = "vocabs"

    def __init__(
        self, model_name: str, chars: list, created: datetime = None, _id=None,
    ):
        super().__init__(_id, created)
        self.model_name = model_name
        self.chars = chars

    @staticmethod
    def load_from_dict(db_dict: dict):
        return VocabDAODTO(
            db_dict.get("model_name"),
            db_dict.get("chars"),
            db_dict.get("created"),
            db_dict.get("_id"),
        )


if __name__ == "__main__":
    pass
    # l = LyricsDAODTO("eminem", "haha", 1)
    # l.save()
