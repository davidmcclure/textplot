

from textplot.matrix import Matrix


def test_set_pair():

    """
    Matrix#set_pair() should set the value under an order-independent key.
    """

    m = Matrix()
    m.set_pair('a', 'b', 1)

    assert m.get_pair('a', 'b') == 1
    assert m.get_pair('b', 'a') == 1
