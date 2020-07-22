import random
from concurrent.futures.thread import ThreadPoolExecutor
from brapper.data import lyrics_downloader as LyricsDownloader
from brapper.nlp import learner as Learner
from brapper.server import LyricsDAODTO, ModelDAODTO
from brapper.config.ctl_config import (
    NEW_MODEL_AGE_DAYS,
    NEW_SONG_AGE_DAYS,
    MIN_EPOCH_COUNT,
    MAX_EPOCH_COUNT,
)


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
                elif entry.is_newer(NEW_SONG_AGE_DAYS):
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
        db_entry = LyricsDAODTO(
            artist_name, "", 0
        ).save()  # save empty to avoid double downloads
        lyrics, song_count = self.lyrics_downloader.download_artist_songs(artist_id)
        self.logger.info(f"Lyrics for {artist_name} downloaded")
        db_entry.lyrics = lyrics
        db_entry.song_count = song_count
        db_entry.save()
        self.logger.info(f"Lyrics for {artist_name} saved into the database")
        self.running_jobs[
            job_id
        ] = f"{song_count} {artist_name} songs saved into the database"

    # API HANDLER
    def get_all_models_in_db(self) -> list:
        daodtos = ModelDAODTO.get_all()
        return [
            {"_id": str(daodto._id), "name": daodto.name, "created": daodto.created,}
            for daodto in daodtos
        ]

    # API HANDLER
    def train_new_model(self, model_name: str, artists: list, epoch_count: int) -> int:
        self.logger.info(
            f"Attempting to train new model {model_name} for {epoch_count} epochs"
        )
        if not MIN_EPOCH_COUNT <= epoch_count <= MAX_EPOCH_COUNT:
            raise JobNotStartedError(
                f"Epoch count not right - use value {MIN_EPOCH_COUNT} <= x <= {MAX_EPOCH_COUNT}",
                422,
            )
        saved_models = ModelDAODTO.get_all()
        for entry in saved_models:
            if model_name == entry.name:
                if entry.vocabulary:
                    raise JobNotStartedError(
                        "This model name is already taken, please choose a different one",
                        409,
                    )
                elif entry.is_newer(NEW_MODEL_AGE_DAYS):
                    raise JobNotStartedError(
                        "This model has been trained recently or is being trained right now",
                        409,
                    )
                else:
                    entry.delete()
                    break
        train_text = self.__get_text_from_artist_ids(artists)
        job_id = random.randint(1, 100000)
        self.logger.info(f"Submitting train job with id {job_id}")
        self.thread_pool.submit(
            self.__train_new_model, model_name, train_text, epoch_count, job_id
        )
        self.running_jobs[job_id] = None
        return job_id

    def __train_new_model(
        self, model_name: str, text: str, epoch_count: int, job_id: int
    ) -> None:
        db_entry = ModelDAODTO(model_name, []).save()
        db_entry.vocabulary = self.learner.train_new_model(
            model_name, text, epoch_count
        )
        db_entry.save()
        self.logger.info(f"New model {model_name} finished training and was saved into the database")
        self.running_jobs[
            job_id
        ] = f"Model {model_name} trained for {epoch_count} epochs"

    def train_existing_model(
        self, model_id: str, artists: list, epoch_count: int
    ) -> int:
        self.logger.info(
            f"Attempting to retrain new model {model_id} for {epoch_count} epochs"
        )
        if not MIN_EPOCH_COUNT <= epoch_count <= MAX_EPOCH_COUNT:
            raise JobNotStartedError(
                f"Epoch count not right - use value {MIN_EPOCH_COUNT} <= x <= {MAX_EPOCH_COUNT}",
                422,
            )
        model = ModelDAODTO.get_by_id(model_id)
        if not model:
            raise JobNotStartedError(
                f"Model ID {model_id} not found - try a different one", 422
            )
        train_text = self.__get_text_from_artist_ids(artists)
        job_id = random.randint(1, 100000)
        self.logger.info(f"Submitting retrain job with id {job_id}")
        self.thread_pool.submit(
            self.__train_existing_model,
            model,
            train_text,
            epoch_count,
            job_id,
        )
        self.running_jobs[job_id] = None
        return job_id

    def __train_existing_model(
        self,
        model: ModelDAODTO,
        text: str,
        epoch_count: int,
        job_id: int,
    ) -> None:
        model.vocabulary = self.learner.train_existing_model(
            model.name, model.vocabulary, text, epoch_count
        )
        model.save()
        self.logger.info(f"Existing model {model.name} finished training and was saved into the database")
        self.running_jobs[
            job_id
        ] = f"Model {model_name} retrained for {epoch_count} epochs"

    def __get_text_from_artist_ids(self, artist_ids: list) -> str:
        try:
            just_lyrics = [
                LyricsDAODTO.get_by_id(artist_id).lyrics for artist_id in artist_ids
            ]
            return "".join(just_lyrics)
        except AttributeError:
            raise JobNotStartedError(
                f"Invalid artist IDs - not found in the database", 422
            )


class JobNotStartedError(Exception):
    def __init__(self, message, status_code: int = 400):
        super().__init__()
        self.message = message
        self.status_code = status_code
