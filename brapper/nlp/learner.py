import tensorflow as tf


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
    test_str = "hello there boy, aaa bbb"
    print(test_str)
    key = __create_char_map(test_str)
    print(key)
    encoded = __encode(test_str, key)
    print(encoded)
    decoded = __decode(encoded, key)
    print(decoded)
