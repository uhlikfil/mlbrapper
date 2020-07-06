import random
from pathlib import Path

from lyricsgenius import Genius

from brapper.config import LYRICS_PATH


def save_artist_songs(artist_name: str, num_of_songs: int = 100) -> None:
    """ Find the artist on Genius.com, download the lyrics to his most popular songs and save them into a file
    :param artist_name:str: Name of the artist
    :param num_of_songs:int: How many song lyrics should be saved (maximum)
    :rtype: None
    """
    gen = Genius(__get_access_token())
    artist = gen.search_artist(artist_name, max_songs=num_of_songs, sort="popularity")
    file_path = LYRICS_PATH.joinpath(f"{artist_name}_temp")
    with open(file_path, "w+", encoding="utf-8") as file_:
        for index, song in enumerate(artist.songs):
            if song:
                file_.write(f"{__unescape_html(song.lyrics)}\n\n")
    file_path.rename(file_path.parent.joinpath(f"{artist_name}_{index + 1}"))


def get_lyrics(lyrics: str or list) -> str:
    if isinstance(lyrics, str):
        return __get_lyrics_from_file(lyrics)
    if isinstance(lyrics, list):
        "".join([__get_lyrics_from_file(lyrics) for lyrics in lyrics])


def __get_lyrics_from_file(file_name: str) -> str:
    path = LYRICS_PATH.joinpath(file_name)
    with open(path, "r", encoding="utf-8") as file_:
        return file_.read()


def __get_access_token() -> str:
    return "kZ-60qWhiJ1dE_GlqzylOz8FlzJoyG96PiUPTvbxoyRWYns9nOZCGC8cqTILtqjN"


def __unescape_html(text: str) -> str:
    """ Replace html escaped chars (<, >, &) with the normal character
    :param text:str: Text to unescape
    :rtype: Text with the original html escaped characters
    """
    return text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


if __name__ == "__main__":
    save_artist_songs("Suboi")
    save_artist_songs("Kendric Lamar")
