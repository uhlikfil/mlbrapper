import requests
import re
from bs4 import BeautifulSoup


max_songs_per_page = 50

base_url = "https://api.genius.com/"
session = requests.Session()
session.headers[
    "authorization"
] = "Bearer kZ-60qWhiJ1dE_GlqzylOz8FlzJoyG96PiUPTvbxoyRWYns9nOZCGC8cqTILtqjN"


def verify_artist_exists(artist_name: str) -> tuple:
    hits = search_web(artist_name).get("hits")
    if len(hits) > 0:
        best_hit = hits[0].get("result")
        found_artist = best_hit.get("primary_artist")
        return found_artist.get("id"), found_artist.get("name")
    else:
        return None, None


def download_artist_songs(artist_id: int, num_of_songs: int = 100) -> tuple:
    """ Find the artist on Genius.com, download the lyrics to their most popular songs
    :param artist_name:str: Name of the artist
    :param num_of_songs:int: How many song lyrics should be downloaded (maximum)
    :rtype: All the songs in one string, Number of songs actually downloaded
    """
    page = 1
    lyrics = []
    while page and len(lyrics) < num_of_songs:
        songs_response = get_songs(artist_id, page=page)
        for song_info in songs_response.get("songs"):
            if "title" in song_info and __result_is_lyrics(song_info.get("title")):
                song_lyrics = __scrape_song_lyrics_from_url(song_info.get("url"))
                if song_lyrics:
                    lyrics.append(song_lyrics)
                if len(lyrics) >= num_of_songs:
                    break
        page = songs_response.get("next_page")
    return (
        "\n\n".join([__unescape_html(song) for song in lyrics]),
        len(lyrics),
    )


def get_songs(artist_id: int, per_page: int = max_songs_per_page, page: int = 1):
    endpoint = f"artists/{artist_id}/songs"
    params = {"sort": "popularity", "per_page": per_page, "page": page}
    return __make_request(endpoint, query=params)


def search_web(search_term: str) -> str:
    endpoint = "search/"
    params = {"q": search_term}
    return __make_request(endpoint, query=params)


def __make_request(path, method: str = "GET", query: dict = {}):
    url = f"{base_url}{path}"
    try:
        response = session.request(method, url, params=query)
        return response.json().get("response") if response else None
    except requests.Timeout:
        return __make_request(path, method, query)


def __scrape_song_lyrics_from_url(url: str) -> str:
    """ Use BeautifulSoup to scrape song info off of a Genius song URL
    Taken from johnwmillr/LyricsGenius
    :param url: URL for the web page to scrape lyrics from
    """
    no_lyrics_str = "Lyrics for this song have yet to be released. Please check back once the song has been released."

    page = requests.get(url)
    if page.status_code == 404:
        return None
    # Scrape the song lyrics from the HTML
    html = BeautifulSoup(page.text, "html.parser")
    # Determine the class of the div
    old_div = html.find("div", class_="lyrics")
    new_div = html.find(
        "div", class_="SongPageGrid-sc-1vi6xda-0 DGVcp Lyrics__Root-sc-1ynbvzw-0 jvlKWy"
    )
    if old_div:
        lyrics = old_div.get_text()
    elif new_div:
        # Clean the lyrics since get_text() fails to convert "</br/>"
        lyrics = str(new_div)
        lyrics = lyrics.replace("<br/>", "\n")
        lyrics = re.sub(r"(\<.*?\>)", "", lyrics)
    else:
        return None  # In case the lyrics section isn't found
    return lyrics if no_lyrics_str not in lyrics else None


def __result_is_lyrics(song_title: str) -> bool:
    non_lyrics = [
        "track\\s?list",
        "album art(work)?",
        "liner notes",
        "booklet",
        "credits",
        "interview",
        "skit",
        "instrumental",
        "setlist",
    ]
    expression = r"".join(["({})|".format(term) for term in non_lyrics]).strip("|")
    regex = re.compile(expression, re.IGNORECASE)
    return not regex.search(__clean_str(song_title))


def __clean_str(string: str) -> str:
    return string.replace("\u200b", " ").strip().lower()


def __unescape_html(text: str) -> str:
    """ Replace html escaped chars (<, >, &) with the normal character
    :param text:str: Text to unescape
    :rtype: Text with the original html escaped characters
    """
    return text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


if __name__ == "__main__":
    pass
