

import re


def strip_tags(text):

    """
    Replace all tags in a string with spaces, so as to preserve the original
    character offsets of the words.

    :param text: The original text.
    """

    pattern = re.compile('<\/?[^<>]*>')
    return pattern.sub(lambda x: len(x.group()) * ' ', text)


def centroid(points):

    """
    Compute the mean center of a set of points.

    :param points: A list of x/y tuples.
    """

    xs = [x for x,y in points]
    ys = [y for x,y in points]
    return (mean(xs), mean(ys))


def mean(numbers):

    """
    Average a list.

    :param numbers: List of numbers.
    """

    return float(sum(numbers)) / len(numbers)
