from brapper.config.server_config import BASE_API_URL
from flask import Flask, jsonify, request, abort
from brapper.controller import Controller 

server = Flask(__name__.split('.')[0])
ctl = Controller()

@server.route(f"{BASE_API_URL}/lyrics", methods=["GET"])
def get_all_lyrics():
    return jsonify({"hello": "there"})


@server.route(f"{BASE_API_URL}/lyrics", methods=["POST"])
def create_lyrics():
    if not request.json or "artist_name" not in request.json:
        abort(400)
    artist_name = request.json.get("artist_name")
    ctl.download_lyrics(artist_name)


if __name__ == "__main__":
    server.run(debug=True)
