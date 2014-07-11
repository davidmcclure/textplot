

import re


def strip_tags(text):

    """
    Replace all tags in a string with spaces, so as to preserve the original
    character offsets of the words.

    :param text: The original text.
    """

    pattern = re.compile('<\/?[^<>]*>')
    return pattern.sub(lambda x: len(x.group()) * ' ', text)
