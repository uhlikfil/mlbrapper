from pymongo import MongoClient, errors as pymongo_errors
from datetime import datetime

from brapper.config.server_config import DB_PASS, DB_URI, DB_USER


client = MongoClient(f"mongodb+srv://{DB_USER}:{DB_PASS}@{DB_URI}")
db = client.brapper


class BaseDAODTO(dict):
    def __init__(self, db_name: str, _id=None):
        self.db_name = db_name
        if _id:
            self._id = _id

    def __setattr__(self, name, value):
        self[name] = value

    def __getattr__(self, name):
        return self[name]

    def save(self):
        try:
            result = db[self.db_name].insert_one(self.to_db_dict())
            self._id = result.inserted_id
            return result
        except pymongo_errors.DuplicateKeyError:
            query = {"_id": self._id}
            new_values = {"$set": self.to_db_dict()}
            return db[self.db_name].update_one(query, new_values)

    def delete(self):
        query = {"_id": self._id}
        return db[self.db_name].delete_one(query)

    def to_db_dict(self):
        copy = self.copy()
        copy.pop("db_name")
        return copy

    def to_json(self):
        copy = self.copy()
        copy.pop("db_name")
        copy["_id"] = str(copy.get("_id"))
        return copy


class LyricsDAODTO(BaseDAODTO):
    def __init__(
        self,
        artist: str,
        lyrics: str,
        song_count: int,
        created: datetime = None,
        _id=None,
    ):
        super().__init__("lyrics", _id)
        self.artist = artist
        self.lyrics = lyrics
        self.song_count = song_count
        self.created = created if created != None else str(datetime.now())

    @staticmethod
    def load_from_dict(db_dict: dict):
        return LyricsDAODTO(
            db_dict.get("artist"),
            db_dict.get("lyrics"),
            db_dict.get("song_count"),
            db_dict.get("created"),
            db_dict.get("_id"),
        )


def get_all_lyrics() -> list:
    result = list(db.lyrics.find())
    return [LyricsDAODTO.load_from_dict(db_entry) for db_entry in result]


if __name__ == "__main__":
    pass
    # l = LyricsDAODTO("eminem", "haha", 1)
    # l.save()
