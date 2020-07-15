import random
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from brapper.data import lyrics_downloader as LyricsDownloader
from brapper.nlp import learner as Learner
from brapper.server import database as Database, LyricsDAODTO


class Controller:
    def __init__(self, logger):
        self.logger = logger

        self.database = Database
        self.lyrics_downloader = LyricsDownloader
        self.learner = Learner
        self.running_jobs = {}
        self.thread_pool = ThreadPoolExecutor(4)

    # API HANDLER
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

    # API HANDLER
    def get_all_artists_in_db(self) -> list:
        daodtos = self.database.get_all_lyrics()
        return [
            {
                "_id": str(daodto._id),
                "artist": daodto.artist,
                "song_count": daodto.song_count,
            }
            for daodto in daodtos
        ]

    # API HANDLER
    def download_lyrics(self, artist_name: str) -> int:
        self.logger.info(f"Attempting to download lyrics for {artist_name}")
        artist_id, real_name = self.lyrics_downloader.verify_artist_exists(artist_name)
        if not real_name:
            self.logger.info(f"Artist {artist_name} not found in the Genius database")
            raise JobNotStartedError("The artist was not found on Genius.com")
        saved_artists = self.database.get_all_lyrics()
        for entry in saved_artists:
            if real_name == entry.artist:
                if entry.song_count > 0:
                    self.logger.info(f"Artist {real_name} already in the database")
                    raise JobNotStartedError(
                        "The artist's lyrics were already downloaded before"
                    )
                elif (
                    datetime.now()
                    - datetime.strptime(entry.created, "%Y-%m-%d %H:%M:%S.%f")
                ).days < 1:
                    self.logger.info(
                        f"Artist {real_name} recently added with 0 songs - probably still downloading"
                    )
                    raise JobNotStartedError(
                        "The artist's lyrics are being downloaded right now"
                    )
                else:
                    self.logger.info(
                        f"Artist {real_name} has been in database with zero songs for quite some time - probably fuck up"
                    )
                    entry.delete()
                    break

        job_id = random.randint(1, 100000)
        self.logger.info(f"Submitting download job with id {job_id}")
        self.thread_pool.submit(
            self.__download_and_save_lyrics, artist_id, real_name, job_id
        )
        return job_id

    def __download_and_save_lyrics(
        self, artist_id: int, artist_name: str, job_id: int
    ) -> None:
        self.running_jobs[job_id] = None
        db_entry = LyricsDAODTO(artist_name, "", 0)
        db_entry.save()  # save empty to avoid double downloads
        lyrics, song_count = self.lyrics_downloader.download_artist_songs(artist_id)
        self.logger.info(f"Lyrics downloaded")
        db_entry.lyrics = lyrics
        db_entry.song_count = song_count
        db_entry.save()
        self.logger.info("Lyrics saved into database")
        self.running_jobs[
            job_id
        ] = f"{song_count} {artist_name} songs saved to the database"

    def train_new_model(
        self, model_name: str, artists: list, num_of_epochs: int
    ) -> tuple:
        pass
        # self.learner.train_new_model()


class JobNotStartedError(Exception):
    status_code = 200

    def __init__(self, message):
        super().__init__()
        self.message = message
