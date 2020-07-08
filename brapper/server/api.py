#### USE CASES ####

# GET ALL AVAILABLE TRAINED MODELS
#   GET api/v1/models
# returns list of trained models like [Eminem_53234, My-Model_36325]


# CREATE NEW SONG
#   GET api/v1/compose
#   payload = { model_name: "Eminem_53234", start_lyrics: "Roses are red, violets are blue" }
# creates a new song based on the existing models - model chosen from the GET ALL AVAILABLE TRAINED MODELS request


# TRAIN NEW MODEL
#   POST api/v1/models
#   payload = { model_name: My-Model, lyrics_id: 515165, num_of_epochs: 20 }
# returns the full name of the created model (My-Model_15155)

from brapper.controller import 
from flask import Flask, jsonify


server = Flask(__name__)

@server.route("/models", methods=["GET"])
def get_all_models():
    return jsonify({"hello": "there"})


if __name__ == "__main__":
    server.run(debug=True)