#### USE CASES ####

# GET ALL AVAILABLE TRAINED MODELS
#   GET api/v1/trained_models
# returns list of trained models like [Eminem_53234, Kendrick-Lamar_36325] - the id will be used to fetch the lyrics sample


# CREATE NEW SONG
#   POST api/v1/compose
#   payload = { model: "Eminem_53234", start_lyrics: "Roses are red, violets are blue" }
# creates a new song based on the existing models - model chosen from the GET ALL AVAILABLE TRAINED MODELS request


# TRAIN NEW MODEL AND CREATE SONG
#   POST api/v1/compose_new?artist=Eminem&lyrics_sample=50
# searches for songs, downlaods lyrics, trains new model, creates a song
