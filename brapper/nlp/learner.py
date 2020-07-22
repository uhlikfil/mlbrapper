import json
import random

import numpy as np
import tensorflow as tf

from brapper.config.ml_config import (
    DEF_BATCH_SIZE,
    DEF_BUFFER_SIZE,
    DEF_EMBEDDING_DIMENSION,
    DEF_EPOCH_COUNT,
    DEF_RNN_UNITS,
    DEF_SEQ_LEN,
    MODELS_PATH,
    VOCAB_PLACEHOLDER,
    VOCAB_SIZE,
)


def generate_lyrics(
    model_name: str,
    start_lyrics: str,
    lyrics_size: int,
    embedding_dim: int = DEF_EMBEDDING_DIMENSION,
    rnn_units: int = DEF_RNN_UNITS,
) -> str:
    generated_lyrics = []
    old_vocab = __load_charmap(model_name)
    vocabulary = __update_charmap(old_vocab, __create_charmap(start_lyrics))
    model = __load_model(model_name, len(vocabulary), 1, embedding_dim, rnn_units)
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
    model_name: str,
    text: str,
    epoch_count: int = DEF_EPOCH_COUNT,
    seq_length: int = DEF_SEQ_LEN,
    buffer_size: int = DEF_BUFFER_SIZE,
    batch_size: int = DEF_BATCH_SIZE,
    embedding_dim: int = DEF_EMBEDDING_DIMENSION,
    rnn_units: int = DEF_RNN_UNITS,
) -> list:
    vocabulary = __create_charmap(text)
    encoded = __encode(text, vocabulary)
    dataset = __create_dataset(
        encoded, seq_length=seq_length, buffer_size=buffer_size, batch_size=batch_size
    )
    model = __build_model(
        len(vocabulary),
        batch_size=batch_size,
        embedding_dim=embedding_dim,
        rnn_units=rnn_units,
    )
    __train_model(model, dataset, model_name, epoch_count=epoch_count)
    return vocabulary


def train_existing_model(
    model_name: str,
    vocabulary: list,
    text: str,
    epoch_count: int = DEF_EPOCH_COUNT,
    seq_length: int = DEF_SEQ_LEN,
    buffer_size: int = DEF_BUFFER_SIZE,
    batch_size: int = DEF_BATCH_SIZE,
    embedding_dim: int = DEF_EMBEDDING_DIMENSION,
    rnn_units: int = DEF_RNN_UNITS,
) -> list:
    new_vocab = __create_charmap(text)
    updated_vocab = __update_charmap(vocabulary, new_vocab)
    encoded = __encode(text, updated_vocab)
    dataset = __create_dataset(
        encoded, seq_length=seq_length, buffer_size=buffer_size, batch_size=batch_size
    )
    model = __load_model(
        model_name, len(updated_vocab), batch_size, embedding_dim, rnn_units
    )
    __train_model(model, dataset, model_name, epoch_count=epoch_count)
    return updated_vocab


def __train_model(model, dataset, model_name: str, epoch_count: int) -> None:
    model.compile(
        optimizer="adam",
        loss=lambda labels, logits: tf.keras.losses.sparse_categorical_crossentropy(
            labels, logits, from_logits=True
        ),
    )
    model.fit(
        dataset,
        epochs=epoch_count,
        callbacks=[__create_checkpoint_callback(model_name)],
    )


def __load_model(
    model_name: str,
    vocab_size: int,
    batch_size: int,
    embedding_dim: int,
    rnn_units: int,
) -> (tf.keras.Sequential, list):
    model = __build_model(
        vocab_size=vocab_size,
        batch_size=batch_size,
        embedding_dim=embedding_dim,
        rnn_units=rnn_units,
    )
    model.load_weights(
        tf.train.latest_checkpoint(MODELS_PATH.joinpath(model_name))
    ).expect_partial()
    model.build(tf.TensorShape([1, None]))
    return model


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
        filepath=str(MODELS_PATH.joinpath(model_name, "cp_{epoch}")),
        save_weights_only=True,
    )


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


def __create_charmap(text: str) -> list:
    """ Creates a set of chars where index of char is its key
    :param text:str: Text to create the key for
    :rtype: Dict of int : char and set of chars where index in the set is the key
    """
    result = sorted(set(text))
    return result + [VOCAB_PLACEHOLDER] * (VOCAB_SIZE - len(result))


def __update_charmap(old_charmap: list, new_charmap: list) -> list:
    clean_old = old_charmap[: old_charmap.index(VOCAB_PLACEHOLDER)]
    extra_chars = list(set(new_charmap) - set(old_charmap))
    result = clean_old + extra_chars
    return result + [VOCAB_PLACEHOLDER] * (VOCAB_SIZE - len(result))


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


if __name__ == "__main__":
    pass
