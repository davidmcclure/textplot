

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


def strip_tags(text):

    """
    Replace all tags in a string with spaces, so as to preserve the original
    character offsets of the words.

    :param text: The original text.
    """

    pattern = re.compile('<\/?[^<>]*>')
    return pattern.sub(lambda x: len(x.group()) * ' ', text)


def tokenize(text):

    """
    Yield tokens.

    :param text: The original text.
    """

    # Strip tags and downcase.
    text = strip_tags(text).lower()
    stem = PorterStemmer().stem

    # Walk words in the text.
    pattern = re.compile('[a-z]+')
    for offset, match in enumerate(re.finditer(pattern, text)):

        # Get the raw token.
        unstemmed = match.group(0)

        yield { # Emit the token.
            'stemmed':      stem(unstemmed),
            'unstemmed':    unstemmed,
            'offset':       offset,
            'left':         match.start(),
            'right':        match.end()
        }


def sort_dict(d, reverse=True):

    """
    Sort an ordered dictionary by value, descending.

    :param d: A dictionary.
    """

    sort = sorted(d.items(), key=lambda x: x[1], reverse=reverse)
    return OrderedDict(sort)


def window(seq, n=2):

    """
    Yield a sliding window over an iterable.

    :param seq: The sequence.
    :param n: The window width.
    """

    it = iter(seq)
    result = tuple(islice(it, n))

    if len(result) == n:
        yield result

    for token in it:
        result = result[1:] + (token,)
        yield result
