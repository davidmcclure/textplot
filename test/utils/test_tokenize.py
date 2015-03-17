

from textplot.utils import tokenize


def test_tokenize():

    """
    tokenize() should yield token dicts from a string.
    """

    text = 'aa bb cc dd'

    tokens = tokenize(text)

    aa = next(tokens)
    assert aa['stemmed']    == 'aa'
    assert aa['unstemmed']  == 'aa'
    assert aa['offset']     == 0

    bb = next(tokens)
    assert bb['stemmed']    == 'bb'
    assert bb['unstemmed']  == 'bb'
    assert bb['offset']     == 1

    cc = next(tokens)
    assert cc['stemmed']    == 'cc'
    assert cc['unstemmed']  == 'cc'
    assert cc['offset']     == 2

    dd = next(tokens)
    assert dd['stemmed']    == 'dd'
    assert dd['unstemmed']  == 'dd'
    assert dd['offset']     == 3


def test_stem():

    """
    Stemm-able tokens should be stemmed.
    """

    text = 'happy days'

    tokens = tokenize(text)

    t1 = next(tokens)
    assert t1['stemmed']    == 'happi'
    assert t1['unstemmed']  == 'happy'
    assert t1['offset']     == 0

    t2 = next(tokens)
    assert t2['stemmed']    == 'day'
    assert t2['unstemmed']  == 'days'
    assert t2['offset']     == 1
