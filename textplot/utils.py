

import re
import numpy as np
import functools

from collections import OrderedDict
from nltk.stem import PorterStemmer
from itertools import islice


def tokenize(text):

    """
    Yield tokens.

    Args:
        text (str): The original text.

    Yields:
        dict: The next token.
    """

    stem = PorterStemmer().stem
    tokens = re.finditer('[a-z]+', text.lower())

    for offset, match in enumerate(tokens):

        # Get the raw token.
        unstemmed = match.group(0)

        yield { # Emit the token.
            'stemmed':      stem(unstemmed),
            'unstemmed':    unstemmed,
            'offset':       offset
        }


def sort_dict(d, desc=True):

    """
    Sort an ordered dictionary by value, descending.

    Args:
        d (OrderedDict): An ordered dictionary.
        desc (bool): If true, sort desc.

    Returns:
        OrderedDict: The sorted dictionary.
    """

    sort = sorted(d.items(), key=lambda x: x[1], reverse=desc)
    return OrderedDict(sort)


def window(seq, n=2):

    """
    Yield a sliding window over an iterable.

    Args:
        seq (iter): The sequence.
        n (int): The window width.

    Yields:
        tuple: The next window.
    """

    it = iter(seq)
    result = tuple(islice(it, n))

    if len(result) == n:
        yield result

    for token in it:
        result = result[1:] + (token,)
        yield result
