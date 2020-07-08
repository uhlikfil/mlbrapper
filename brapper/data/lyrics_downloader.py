from lyricsgenius import Genius


class LyricsDownloader():

    def __init__(self):
        genius_access_token = "kZ-60qWhiJ1dE_GlqzylOz8FlzJoyG96PiUPTvbxoyRWYns9nOZCGC8cqTILtqjN"
        self.gen = Genius(genius_access_token, sleep_time=0, verbose=False)

    def verify_artist_exists(self, artist_name: str) -> str or bool:
        artist = self.gen.search_artist(artist_name, max_songs=1)
        return artist.name if artist else False

    def download_artist_songs(self, artist_name: str, num_of_songs: int = 100) -> tuple:
        """ Find the artist on Genius.com, download the lyrics to their most popular songs
        :param artist_name:str: Name of the artist
        :param num_of_songs:int: How many song lyrics should be downloaded (maximum)
        :rtype: All the songs in one string, Number of songs actually downloaded
        """
        artist = self.gen.search_artist(artist_name, max_songs=num_of_songs, sort="popularity")
        return "\n\n".join([self.__unescape_html(song.lyrics) for song in artist.songs]), len(artist.songs)


    def __unescape_html(self, text: str) -> str:
        """ Replace html escaped chars (<, >, &) with the normal character
        :param text:str: Text to unescape
        :rtype: Text with the original html escaped characters
        """
        return text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


if __name__ == "__main__":
    ld = LyricsDownloader()
    print(ld.verify_artist_exists("eminnem"))
