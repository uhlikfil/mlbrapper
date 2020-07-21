import random
from concurrent.futures.thread import ThreadPoolExecutor
from brapper.data import lyrics_downloader as LyricsDownloader
from brapper.nlp import learner as Learner
from brapper.server import LyricsDAODTO


class Controller:
    def __init__(self, logger):
        self.logger = logger

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
        daodtos = LyricsDAODTO.get_all()
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
            raise JobNotStartedError("The artist was not found on Genius.com", 422)
        saved_artists = LyricsDAODTO.get_all()
        for entry in saved_artists:
            if real_name == entry.artist:
                if entry.song_count > 0:
                    raise JobNotStartedError(
                        "The artist's lyrics were already downloaded before", 409
                    )
                elif entry.is_new():
                    raise JobNotStartedError(
                        "The artist's lyrics are being downloaded right now", 409
                    )
                else:
                    entry.delete()
                    break

        job_id = random.randint(1, 100000)
        self.logger.info(f"Submitting download job with id {job_id}")
        self.thread_pool.submit(
            self.__download_and_save_lyrics, artist_id, real_name, job_id
        )
        self.running_jobs[job_id] = None
        return job_id, real_name

    def __download_and_save_lyrics(
        self, artist_id: int, artist_name: str, job_id: int
    ) -> None:
        db_entry = LyricsDAODTO(artist_name, "", 0)
        db_entry.save()  # save empty to avoid double downloads
        lyrics, song_count = self.lyrics_downloader.download_artist_songs(artist_id)
        self.logger.info(f"Lyrics for {artist_name} downloaded")
        db_entry.lyrics = lyrics
        db_entry.song_count = song_count
        db_entry.save()
        self.logger.info(f"Lyrics for {artist_name} saved into the database")
        self.running_jobs[
            job_id
        ] = f"{song_count} {artist_name} songs saved into the database"

    def train_new_model(
        self, model_name: str, artists: list, epoch_count: int
    ) -> tuple:
        self.logger.info(
            f"Attempting to train new model {model_name} on {artists} lyrics with {epoch_count} epochs"
        )
        # TODO checks
        # raise JobNotStartedError("The model name is already used", 409)
        # raise JobNotStartedError(f"Artist ID {id} not found in the database", 422)
        # raise JobNotStartedError(f"Epoch count not right - use value {min} < x < {max}", 422)

        just_lyrics = [LyricsDAODTO.get_by_id(artist_id).lyrics for artist_id in artists]
        train_text = "".join(just_lyrics)

        job_id = random.randint(1, 100000)
        self.logger.info(f"Submitting train job with id {job_id}")
        self.thread_pool.submit(
            self.__train_new_model, model_name, train_text, epoch_count
        )
        self.running_jobs[job_id] = None
        return job_id

    def __train_new_model(self, model_name: str, text: str, epoch_count: int, job_id: int):
        model_name, vocab = self.learner.train_new_model(model_name, text, epoch_count)
        self.running_jobs[
            job_id
        ] = f"{song_count} {artist_name} songs saved into the database"


class JobNotStartedError(Exception):
    def __init__(self, message, status_code: int = 400):
        super().__init__()
        self.message = message
        self.status_code = status_code
