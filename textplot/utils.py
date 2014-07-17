

import re
import functools

from collections import OrderedDict


def strip_tags(text):

    """
    Replace all tags in a string with spaces, so as to preserve the original
    character offsets of the words.

    :param text: The original text.
    """

    pattern = re.compile('<\/?[^<>]*>')
    return pattern.sub(lambda x: len(x.group()) * ' ', text)


def memoize(obj):

    """
    Memoize a function, respecting kwargs. From:
    https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize

    :param obj: The cache dictionary.
    """

    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]

    return memoizer


def sort_dict(dictionary):

    """
    Sort an ordered dictionary by value, descending.

    :param dictionary: The dictionary.
    """

    sort = sorted(dictionary.iteritems(), key=lambda x: x[1], reverse=True)
    return OrderedDict(sort)
