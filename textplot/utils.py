

import re
import numpy as np
import functools

from collections import OrderedDict
from nltk.stem import PorterStemmer
from itertools import islice


def memoize(obj):

    """
    Memoize a function, respecting kwargs. From:
    https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize

    :param obj: The cache dictionary.
    """

    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):

        # Serialize the args.
        key = str(args) + str(kwargs)

        # If uncached, run the call.
        if key not in cache:
            cache[key] = obj(*args, **kwargs)

        # Return the value.
        return cache[key]

    return memoizer


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

    for offset, token in enumerate(tokens):

        # Get the raw token.
        unstemmed = token.group(0)

        yield { # Emit the token.
            'stemmed':      stem(unstemmed),
            'unstemmed':    unstemmed,
            'offset':       offset,
            'left':         token.start(),
            'right':        token.end()
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
