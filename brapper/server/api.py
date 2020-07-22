from flask import Flask, abort, jsonify, request

from brapper.config.server_config import BASE_API_URL
from brapper.controller import Controller, JobNotStartedError


server = Flask(__name__.split(".")[0])
ctl = Controller(server.logger)


@server.errorhandler(JobNotStartedError)
def handle_job_not_started(error):
    response = {
        "job_id": None,
        "info": error.message,
    }
    return jsonify(response), error.status_code


@server.route(f"{BASE_API_URL}/jobs/<int:job_id>", methods=["GET"])
def is_job_finished(job_id: int):
    is_finished, info = ctl.is_job_finished(job_id)
    return {"job_id": job_id, "is_finished": is_finished, "info": info}


@server.route(f"{BASE_API_URL}/lyrics", methods=["POST"])
def create_lyrics():
    if not request.json or "artist" not in request.json:
        abort(400)
    artist_name = request.json.get("artist")
    job_id, found_artist = ctl.download_lyrics(artist_name)
    response = {
        "job_id": job_id,
        "info": f"Found artist: {found_artist} - the artist's lyrics will be downloaded shortly",
    }
    return jsonify(response), 202


@server.route(f"{BASE_API_URL}/lyrics", methods=["GET"])
def get_all_lyrics():
    artist_list = ctl.get_all_artists_in_db()
    return jsonify(artist_list)


@server.route(f"{BASE_API_URL}/models", methods=["POST"])
def create_model():
    if (
        not request.json
        or "model_name" not in request.json
        or "based_on" not in request.json
        or "epochs" not in request.json
    ):
        abort(400)
    model_name = request.json.get("model_name").replace(" ", "-")
    artists = request.json.get("based_on")
    epochs = request.json.get("epochs")
    if not isinstance(epochs, int) or not isinstance(artists, list) or not artists:
        abort(400)
    response = {
        "job_id": ctl.train_new_model(model_name, artists, epochs),
        "info": f"Model {model_name} will be trained shortly",
    }
    return jsonify(response), 202


@server.route(f"{BASE_API_URL}/models/<string:model_id>", methods=["POST"])
def train_model(model_id: str):
    if (
        not request.json
        or "based_on" not in request.json
        or "epochs" not in request.json
    ):
        abort(400)
    artists = request.json.get("based_on")
    epochs = request.json.get("epochs")
    if not isinstance(epochs, int) or not isinstance(artists, list) or not artists:
        abort(400)
    response = {
        "job_id": ctl.train_existing_model(model_id, artists, epochs),
        "info": f"Selected model will be trained shortly",
    }
    return jsonify(response), 202


@server.route(f"{BASE_API_URL}/models", methods=["GET"])
def get_all_models():
    model_list = ctl.get_all_models_in_db()
    return jsonify(model_list)


if __name__ == "__main__":
    pass
