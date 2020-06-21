import tensorflow as tf

from brapper.config import (
    CHECKPOINTS_PATH,
    DEF_BATCH_SIZE,
    DEF_BUFFER_SIZE,
    DEF_EMBEDDING_DIMENSION,
    DEF_EPOCH_COUNT,
    DEF_RNN_UNITS,
    DEF_SEQ_LEN,
    LYRICS_PATH,
)


def train_new_model(
    artist_name: str,
    lyrics_id: int,
    tmp: bool = True,
    num_of_epochs: int = DEF_EPOCH_COUNT,
    seq_length: int = DEF_SEQ_LEN,
    buffer_size: int = DEF_BUFFER_SIZE,
    batch_size: int = DEF_BATCH_SIZE,
    embedding_dim: int = DEF_EMBEDDING_DIMENSION,
    rnn_units: int = DEF_RNN_UNITS,
) -> None:
    def loss_func(labels, logits):
        return tf.keras.losses.sparse_categorical_crossentropy(
            labels, logits, from_logits=True
        )

    lyrics = LYRICS_PATH.joinpath("tmp" if tmp else "", lyrics_id)
    model_name = f'{artist_name.replace(" ", "-")}_{lyrics_id}'
    with open(lyrics, "r", encoding="utf-8") as lyr_file:
        text = lyr_file.read()
        vocabulary = __create_char_map(text)
        encoded = __encode(text, vocabulary)

        dataset = __create_dataset(encoded)
        model = __create_model(len(vocabulary))
        model.compile(optimizer="adam", loss=loss_func)
        history = model.fit(
            dataset,
            epochs=num_of_epochs,
            callbacks=[__create_checkpoint_callback(model_name, tmp=tmp)],
        )


def load_model(model_name: str):
    pass


def __create_dataset(
    encoded_text: str,
    seq_length: int = DEF_SEQ_LEN,
    buffer_size: int = DEF_BUFFER_SIZE,
    batch_size: int = DEF_BATCH_SIZE,
) -> list:
    """ Turns the list of ints (encoded text) into a trainable dataset
        The list of encoded chars is divided into vectors with dimension of seq_length + 1
        These vectors are transformed into train tuples of input-target (for predicting the last character of the sequence)
        The training tuples are shuffled and batched into groups of batch_size
    :param encoded_text:str: List of characters encoded into ints
    :param seq_length:int: Dimension of the training vectors
    :param buffer_size:int: The training data is loaded into buffers
    :param batch_size:int: How many training vector tuples are there in one batch
    :rtype: Model checkpoint callback
    """
    # load the chars represented as ints as a dataset
    base_dataset = tf.data.Dataset.from_tensor_slices(encoded_text)
    # divide them into batches (sequences of chars)
    sequences = base_dataset.batch(seq_length + 1, drop_remainder=True)
    # create tuples of input-output for training
    inp_outp_dataset = sequences.map(lambda batch: (batch[:-1], batch[1:]))
    # shuffle the training data and batch it again
    return inp_outp_dataset.shuffle(buffer_size).batch(batch_size, drop_remainder=True)


def __create_model(
    vocab_size: int,
    batch_size: int = DEF_BATCH_SIZE,
    embedding_dim: int = DEF_EMBEDDING_DIMENSION,
    rnn_units: int = DEF_RNN_UNITS,
):
    """ Create a LSTM model, blackbox AF lol
    """
    return tf.keras.Sequential(
        [
            tf.keras.layers.Embedding(
                vocab_size, embedding_dim, batch_input_shape=[batch_size, None]
            ),
            tf.keras.layers.LSTM(
                rnn_units,
                return_sequences=True,
                stateful=True,
                recurrent_initializer="glorot_uniform",
            ),
            tf.keras.layers.Dense(vocab_size),
        ]
    )


def __create_checkpoint_callback(model_name: str, tmp: bool = True):
    """ Creates a ModelCheckpoint tf callback - the model state is saved after each epoch
    :param model_name:str: Directory name in which the checkpoints are saved
    :param tmp:bool: In tmp dir or not
    :rtype: Model checkpoint callback
    """
    path = str(
        CHECKPOINTS_PATH.joinpath("tmp" if tmp else "", model_name, "cp_{epoch}")
    )
    return tf.keras.callbacks.ModelCheckpoint(filepath=path, save_weights_only=True,)


def __create_char_map(text: str) -> list:
    """ Creates a set of chars where index of char is its key
    :param text:str: Text to create the key for
    :rtype: Dict of int : char and set of chars where index in the set is the key
    """
    return list(set(text))


def __encode(text: str, char_map: list) -> list:
    """ Change each character in the text into a unique integer value
    :param text:str: Text to encode into integers
    :param char_map:list: Set of chars where their index is the key
    :rtype: numpy array of integers
    """
    return [char_map.index(letter) for letter in text]


def __decode(encoded_text: list, char_map: list) -> str:
    """ Description
    :param encoded_text:list: List of ints to decode back to the original text
    :param char_map:list: Set of chars where their index is the key
    :rtype: Original text as a string
    """
    return "".join([char_map[encoded_letter] for encoded_letter in encoded_text])


if __name__ == "__main__":

    train_new_model("Kendrick Lamar", "20963", tmp=False)
