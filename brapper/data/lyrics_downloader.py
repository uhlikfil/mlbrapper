import datetime
import time
import uuid
from pathlib import Path

from lyricsgenius import Genius


def __get_access_token() -> str:
    return "Awp1-RqQmLsXsBxkS7oEpET88sS-mTK06k-kbeJ_nK4cny6-cylEoduEpnZrwuB3"


def __unescape_html(text: str) -> str:
    """ Replace html escaped chars (<, >, &) with the normal character
    :param text:str: Text to unescape
    :rtype: Text with the original html escaped characters
    """
    return text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


def save_artist_songs(artist_name: str, num_of_songs: int = 20) -> None:
    """ Find the artist on Genius.com, download the lyrics to his most popular songs and save them into a file
    :param artist_name:str: Name of the artist
    :param num_of_songs:int: How many song lyrics should be saved
    :rtype: None
    """
    artist = gen.search_artist(artist_name, max_songs=num_of_songs, sort="popularity")
    gen = Genius(__get_access_token())
    file_path = Path(__file__).parent.joinpath("lyrics", f"{uuid.uuid4()}.txt")
    with open(file_path, "w+", encoding="utf-8") as file_:
        for song in artist.songs:
            file_.write(f"{__unescape_html(song.lyrics)}\n\n")
