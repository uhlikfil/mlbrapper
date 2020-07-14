import random
from concurrent.futures.thread import ThreadPoolExecutor

from brapper.data import lyrics_downloader as LyricsDownloader
from brapper.server import database as Database


class Controller:
    def __init__(self, logger):
        self.logger = logger

        self.database = Database
        self.lyrics_downloader = LyricsDownloader
        self.running_jobs = {}
        self.thread_pool = ThreadPoolExecutor(4)

    def is_job_finished(self, job_id: int) -> tuple:
        self.logger.info(f"Checking job {job_id} state")
        if job_id not in self.running_jobs.keys():
            return True, "The job id doesn't exist anymore"
        else:
            result = self.running_jobs.get(job_id)
            if result == None:
                return False, "The job isn't finished yet"
            else:
                self.running_jobs.pop(job_id)
                return True, result

    def get_all_artists_in_db(self) -> list:
        all_documents = self.database.get_all_lyrics()
        return [entry.get("artist") for entry in all_documents]

    def download_lyrics(self, artist_name: str) -> int:
        self.logger.info(f"Attempting to download lyrics for {artist_name}")
        artist_id, real_name = self.lyrics_downloader.verify_artist_exists(artist_name)
        if not real_name:
            self.logger.info(f"Artist {artist_name} not found in the Genius database")
            raise JobNotStartedError("The artist was not found on Genius.com")
        if real_name in self.get_all_artists_in_db():
            self.logger.info(f"Artist {artist_name} already in the database")
            raise JobNotStartedError("The artist's lyrics were already downloaded before")

        job_id = random.randint(1, 100000)
        self.logger.info(f"Submitting download job with id {job_id}")
        self.thread_pool.submit(
            self.__download_and_save_lyrics, artist_id, real_name, job_id
        )
        return job_id

    def __download_and_save_lyrics(self, artist_id: int, artist_name: str, job_id: int) -> None:
        self.running_jobs[job_id] = None
        self.database.save_lyrics(artist_name, "", 0)
        lyrics, song_count = self.lyrics_downloader.download_artist_songs(artist_id)
        self.logger.info(f"Lyrics downloaded")
        self.database.update_lyrics(artist_name, lyrics, song_count)
        self.logger.info("Lyrics saved into database")
        self.running_jobs[
            job_id
        ] = f"{song_count} {artist_name} songs saved to the database"

    def train_new_model(self) -> list:
        pass

class JobNotStartedError(Exception):
    status_code = 200

    def __init__(self, message):
        super().__init__()
        self.message = message
