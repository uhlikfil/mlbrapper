from lyricsgenius import Genius
from pathlib import Path
import datetime
import time

def __get_access_token() -> str:
    return "Awp1-RqQmLsXsBxkS7oEpET88sS-mTK06k-kbeJ_nK4cny6-cylEoduEpnZrwuB3"


def __unescape(text: str) -> str:
    return text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


def save_artist_songs(artist_name: str, num_of_songs: int = 15) -> None:
    gen = Genius(__get_access_token())
    artist = gen.search_artist(artist_name, max_songs=num_of_songs, sort="popularity")
    file_path = Path(__file__).parent.joinpath("lyrics", "randomID.txt") # TODO do a random hash for the file name
    with open(file_path, "w+", encoding="utf-8") as file_:
        for song in artist.songs:
            file_.write(f"{__unescape(song.lyrics)}\n\n")


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    save_artist_songs("Kendrick lamar")
    end_time = datetime.datetime.now()
    td = end_time - start_time
    print(td)

