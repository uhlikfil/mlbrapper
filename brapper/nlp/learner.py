import numpy as np
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
    Path,
)


def generate_lyrics(
    model_name: str,
    start_lyrics: str,
    lyrics_size: int,
    embedding_dim: int = DEF_EMBEDDING_DIMENSION,
    rnn_units: int = DEF_RNN_UNITS,
) -> str:
    generated_lyrics = []
    model, vocabulary = __load_model(
        model_name, batch_size=1, embedding_dim=embedding_dim, rnn_units=rnn_units,
    )
    model.reset_states()
    encoded_lyrics = tf.expand_dims(__encode(start_lyrics, vocabulary), 0)
    for i in range(lyrics_size):
        predictions = model(encoded_lyrics)
        predictions = tf.squeeze(predictions, 0)
        predicted_char = tf.random.categorical(predictions, num_samples=1)[
            -1, 0
        ].numpy()
        encoded_lyrics = tf.expand_dims([predicted_char], 0)
        generated_lyrics.append(__decode([predicted_char], vocabulary))
    return start_lyrics + "".join(generated_lyrics)


def train_new_model(
    artist_name: str,
    lyrics_id: int,
    num_of_epochs: int = DEF_EPOCH_COUNT,
    seq_length: int = DEF_SEQ_LEN,
    buffer_size: int = DEF_BUFFER_SIZE,
    batch_size: int = DEF_BATCH_SIZE,
    embedding_dim: int = DEF_EMBEDDING_DIMENSION,
    rnn_units: int = DEF_RNN_UNITS,
) -> None:
    model_name = f'{artist_name.replace(" ", "-")}_{lyrics_id}'
    encoded, vocabulary = __get_encoded_text_and_key(__get_lyrics_path(lyrics_id))
    dataset = __create_dataset(
        encoded, seq_length=seq_length, buffer_size=buffer_size, batch_size=batch_size
    )
    model = __build_model(
        len(vocabulary),
        batch_size=batch_size,
        embedding_dim=embedding_dim,
        rnn_units=rnn_units,
    )
    __train_model(model, dataset, model_name, num_of_epochs=num_of_epochs)


def train_existing_model(
    model_name: str,
    lyrics_id: int,
    num_of_epochs: int = DEF_EPOCH_COUNT,
    seq_length: int = DEF_SEQ_LEN,
    buffer_size: int = DEF_BUFFER_SIZE,
    batch_size: int = DEF_BATCH_SIZE,
    embedding_dim: int = DEF_EMBEDDING_DIMENSION,
    rnn_units: int = DEF_RNN_UNITS,
) -> None:
    encoded, _ = __get_encoded_text_and_key(__get_lyrics_path(lyrics_id))
    dataset = __create_dataset(
        encoded, seq_length=seq_length, buffer_size=buffer_size, batch_size=batch_size
    )
    model, _ = __load_model(
        model_name,
        batch_size=batch_size,
        embedding_dim=embedding_dim,
        rnn_units=rnn_units,
    )
    __train_model(model, dataset, model_name, num_of_epochs=num_of_epochs)


def __train_model(model, dataset, model_name: str, num_of_epochs: int) -> None:
    model.compile(
        optimizer="adam",
        loss=lambda labels, logits: tf.keras.losses.sparse_categorical_crossentropy(
            labels, logits, from_logits=True
        ),
    )
    model.fit(
        dataset,
        epochs=num_of_epochs,
        callbacks=[__create_checkpoint_callback(model_name)],
    )


def __load_model(
    model_name: str, batch_size: int, embedding_dim: int, rnn_units: int
) -> (tf.keras.Sequential, list):
    lyrics_id = model_name.split("_")[-1]
    _, vocabulary = __get_encoded_text_and_key(__get_lyrics_path(lyrics_id))
    model = __build_model(
        len(vocabulary),
        batch_size=batch_size,
        embedding_dim=embedding_dim,
        rnn_units=rnn_units,
    )
    model.load_weights(
        tf.train.latest_checkpoint(CHECKPOINTS_PATH.joinpath(model_name))
    )
    model.build(tf.TensorShape([1, None]))
    return model, vocabulary


def __create_dataset(
    encoded_text: str, seq_length: int, buffer_size: int, batch_size: int,
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


def __build_model(
    vocab_size: int, batch_size: int, embedding_dim: int, rnn_units: int,
) -> tf.keras.Sequential:
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


def __create_checkpoint_callback(model_name: str):
    """ Creates a ModelCheckpoint tf callback - the model state is saved after each epoch
    :param model_name:str: Directory name in which the checkpoints are saved
    :rtype: Model checkpoint callback
    """
    return tf.keras.callbacks.ModelCheckpoint(
        filepath=str(CHECKPOINTS_PATH.joinpath(model_name, "cp_{epoch}")),
        save_weights_only=True,
    )


def __get_encoded_text_and_key(lyrics_path: str) -> (list, list):
    with open(lyrics_path, "r", encoding="utf-8") as lyr_file:
        text = lyr_file.read()
        vocabulary = __create_char_map(text)
        return __encode(text, vocabulary), vocabulary


def __create_char_map(text: str) -> list:
    """ Creates a set of chars where index of char is its key
    :param text:str: Text to create the key for
    :rtype: Dict of int : char and set of chars where index in the set is the key
    """
    return sorted(set(text))


def __encode(text: str, char_map: list) -> list:
    """ Change each character in the text into a unique integer value
    :param text:str: Text to encode into integers
    :param char_map:list: Set of chars where their index is the key
    :rtype: numpy array of integers
    """
    return np.array([char_map.index(letter) for letter in text])


def __decode(encoded_text: list, char_map: list) -> str:
    """ Description
    :param encoded_text:list: List of ints to decode back to the original text
    :param char_map:list: Set of chars where their index is the key
    :rtype: Original text as a string
    """
    return "".join([char_map[encoded_letter] for encoded_letter in encoded_text])


def __get_lyrics_path(lyrics_id: int or str) -> Path:
    return LYRICS_PATH.joinpath(str(lyrics_id))


if __name__ == "__main__":
    train_new_model("Eminem", 54799, 1)
    for i in range(1, 11):
        print(f"STARTING TRAINING {i}")
        train_existing_model("Eminem_54799", 54799, 5)
        epochs_done = 1 + i * 5
        print(f"GENERATING TEXT AFTER {epochs_done} EPOCHS")
        with open(f"after_epoch_{epochs_done}", "w+", encoding="utf-8") as e_file:
            e_file.write(
                generate_lyrics("Eminem_54799", "Roses are red, violets are blue", 3000)
            )
