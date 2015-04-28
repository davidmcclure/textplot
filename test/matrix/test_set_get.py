

from textplot.matrix import TextMatrix


def test_set_pair():

    """
    set_pair() should set the value under an order-independent key.
    """

    m = TextMatrix()
    m.set_pair('a', 'b', 1)

    assert m.get_pair('a', 'b') == 1
    assert m.get_pair('b', 'a') == 1


def test_missing_key():

    """
    If an unindexed key pair is passed, return None.
    """

    m = TextMatrix()
    m.set_pair('a', 'b', 1)

    assert m.get_pair('a', 'c') == None
