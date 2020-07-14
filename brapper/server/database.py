from pymongo import MongoClient
from datetime import datetime

from brapper.config.server_config import DB_PASS, DB_URI, DB_USER


client = MongoClient(f"mongodb+srv://{DB_USER}:{DB_PASS}@{DB_URI}")
db = client.brapper


def save_lyrics(artist_name: str, lyrics: str, song_count: int) -> int:
    to_insert = {
        "artist": artist_name,
        "lyrics": lyrics,
        "num_of_songs": song_count,
        "created": str(datetime.now()),
    }
    return db.lyrics.insert_one(to_insert)


def update_lyrics(artist_name: str, lyrics: str, song_count: int) -> int:
    query = { "artist": artist_name }
    new_values = { 
        "$set": {
            "lyrics": lyrics,
            "num_of_songs": song_count,
            "created": str(datetime.now())
        }
    }
    return db.lyrics.update_one(query, new_values)


def get_all_lyrics() -> list:
    return list(db.lyrics.find())


if __name__ == "__main__":
    pass
