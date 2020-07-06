from pathlib import Path

DEF_SEQ_LEN = 10
DEF_BUFFER_SIZE = 1000
DEF_BATCH_SIZE = 32
DEF_EMBEDDING_DIMENSION = 256
DEF_RNN_UNITS = 1024
DEF_EPOCH_COUNT = 50

VOCAB_SIZE = 300
VOCAB_PLACEHOLDER = "UNDEF"

rscs_base_path = Path(__file__).parent.parent.joinpath("resources")
LYRICS_PATH = rscs_base_path.joinpath("lyrics")
MODELS_PATH = rscs_base_path.joinpath("models")
VOCABS_PATH = rscs_base_path.joinpath("vocabs")
