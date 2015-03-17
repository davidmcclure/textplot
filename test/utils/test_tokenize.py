

from textplot.utils import tokenize


def assert_abc(text):

    """
    Assert tokens aa/bb/cc.

    Args:
        text (str): A raw text string.
    """

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


def test_tokenize():

    """
    tokenize() should yield token dicts from a string.
    """

    assert_abc('aa bb cc')


def test_ignore_non_letters():

    """
    tokenize() should ignore non [a-z] characters.
    """

    assert_abc('aa. 12 bb? 34 cc!')


def test_stem():

    """
    Stemm-able tokens should be stemmed.
    """

    text = 'happy lovely days'

    tokens = tokenize(text)

    t1 = next(tokens)
    assert t1['stemmed']    == 'happi'
    assert t1['unstemmed']  == 'happy'
    assert t1['offset']     == 0

    t2 = next(tokens)
    assert t2['stemmed']    == 'love'
    assert t2['unstemmed']  == 'lovely'
    assert t2['offset']     == 1

    t3 = next(tokens)
    assert t3['stemmed']    == 'day'
    assert t3['unstemmed']  == 'days'
    assert t3['offset']     == 2


def test_ignore_case():

    """
    Tokens should be downcased.
    """

    text = 'One TWO ThReE'

    tokens = tokenize(text)

    t1 = next(tokens)
    assert t1['stemmed']    == 'one'
    assert t1['unstemmed']  == 'one'
    assert t1['offset']     == 0

    t2 = next(tokens)
    assert t2['stemmed']    == 'two'
    assert t2['unstemmed']  == 'two'
    assert t2['offset']     == 1

    t2 = next(tokens)
    assert t2['stemmed']    == 'three'
    assert t2['unstemmed']  == 'three'
    assert t2['offset']     == 2
