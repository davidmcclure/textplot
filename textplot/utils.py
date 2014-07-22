

import re
import functools

from collections import OrderedDict


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


def sort_dict(d):

    """
    Sort an ordered dictionary by value, descending.

    :param d: A dictionary.
    """

    sort = sorted(d.iteritems(), key=lambda x: x[1], reverse=True)
    return OrderedDict(sort)


def int_dict(d):

    """
    Cast all integer-y values in a dictionary to integers.

    :param d: A dictionary.
    """

    for key in d:
        try:
            d[key] = int(d[key])
        except ValueError:
            continue

    return d
