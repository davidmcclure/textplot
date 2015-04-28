

from textplot.matrix import TextMatrix


def test_set_pair():

    """
    Matrix#set_pair() should set the value under an order-independent key.
    """

    m = TextMatrix()
    m.set_pair('a', 'b', 1)

    assert m.get_pair('a', 'b') == 1
    assert m.get_pair('b', 'a') == 1
