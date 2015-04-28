

from textplot.text import Text
from collections import OrderedDict


def test_term_counts():

    """
    term_counts() should return a map of term -> count.
    """

    t = Text('aa bb bb cc cc cc')

    assert t.term_counts() == OrderedDict([
        ('cc', 3),
        ('bb', 2),
        ('aa', 1)
    ])
