

from textplot.utils import sort_dict
from collections import OrderedDict


def test_descending():

    """
    sort_dict() should sort an ordered dictionary in descending order.
    """

    d = OrderedDict([
        ('a', 1),
        ('b', 2),
        ('c', 3)
    ])

    desc = sort_dict(d)

    assert list(desc.items()) == [
        ('c', 3),
        ('b', 2),
        ('a', 1)
    ]


def test_ascending():

    """
    When desc=False is passed, sort in ascending order.
    """

    d = OrderedDict([
        ('c', 3),
        ('b', 2),
        ('a', 1)
    ])

    asc = sort_dict(d, desc=False)

    assert list(asc.items()) == [
        ('a', 1),
        ('b', 2),
        ('c', 3)
    ]
