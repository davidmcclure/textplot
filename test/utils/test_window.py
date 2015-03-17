

from textplot.utils import window


def test_window():

    """
    window() should generate a sliding window over an iterable.
    """

    itr = [1, 2, 3, 4, 5, 6]
    w = window(itr, 3)

    assert next(w) == (1, 2, 3)
    assert next(w) == (2, 3, 4)
    assert next(w) == (3, 4, 5)
    assert next(w) == (4, 5, 6)
