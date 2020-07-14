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
    return response, error.status_code


@server.route(f"{BASE_API_URL}/jobs/<int:job_id>", methods=["GET"])
def is_job_finished(job_id: int):
    is_finished, info = ctl.is_job_finished(job_id)
    return {"job_id": job_id, "is_finished": is_finished, "info": info}


@server.route(f"{BASE_API_URL}/lyrics", methods=["POST"])
def create_lyrics():
    if not request.json or "artist_name" not in request.json:
        abort(400)
    artist_name = request.json.get("artist_name")
    response = {
        "job_id": ctl.download_lyrics(artist_name),
        "info": "The artist's lyrics are being downloaded",
    }
    return response, 202


@server.route(f"{BASE_API_URL}/lyrics", methods=["GET"])
def get_all_lyrics():
    artist_list = ctl.get_all_artists_in_db()
    return jsonify(artist_list)


@server.route(f"{BASE_API_URL}/models", methods=["POST"])
def create_model():
    if not request.json or "model_name" not in request.json or "training_lyrics" not in request.json or "epochs" not in request.json:
        abort(400)
    model_name = request.json.get("model_name")
    training_lyrics = request.json.get("training_lyrics")
    epochs = request.json.get("epochs")


if __name__ == "__main__":
    pass
