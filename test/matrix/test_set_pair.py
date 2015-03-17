

from textplot.matrix import Matrix


def test_set_pair():

    """
    Matrix#set_pair() should set the value under a key that will always be the
    same regardless of the order in which the terms are passed.
    """

    m = Matrix()
    m.set_pair('a', 'b', 5)
    # TODO
