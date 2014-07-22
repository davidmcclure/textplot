

import re
import functools

from collections import OrderedDict
from nltk.stem import PorterStemmer


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
    for match in re.finditer(pattern, text):

        # Get the raw token.
        unstemmed = match.group(0)

        yield { # Emit the token.
            'stemmed':      stem(unstemmed),
            'unstemmed':    unstemmed,
            'left':         match.start(),
            'right':        match.end()
        }


def sort_dict(d):

    """
    Sort an ordered dictionary by value, descending.

    :param d: A dictionary.
    """

    sort = sorted(d.iteritems(), key=lambda x: x[1], reverse=True)
    return OrderedDict(sort)


def numberify_dict(d):

    """
    Convert numberic values in a dictionary into ints / floats.

    :param d: A dictionary.
    """

    for k in d:
        v = d[k]
        if type(v) == str:

            # Try to cast to an integer first.
            try:
                d[k] = int(v)
            except ValueError:

                # Then, see if it's a float.
                try:
                    d[k] = float(v)
                except ValueError:
                    continue

    return d
