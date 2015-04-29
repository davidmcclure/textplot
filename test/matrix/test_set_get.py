

from textplot.matrix import Matrix


def test_set_pair():

    """
    set_pair() should set the value under an order-independent key.
    """

    m = Matrix()
    m.set_pair('a', 'b', 1)

    assert m.get_pair('a', 'b') == 1
    assert m.get_pair('b', 'a') == 1


def test_update_key_set():

    """
    Keys should be added to a set of stored keys.
    """

    m = Matrix()
    m.set_pair('a', 'b', 1)
    m.set_pair('a', 'c', 2)

    assert m.keys == set(['a', 'b', 'c'])


def test_missing_key():

    """
    If an unindexed key pair is passed, return None.
    """

    m = Matrix()
    m.set_pair('a', 'b', 1)

    assert m.get_pair('a', 'c') == None
