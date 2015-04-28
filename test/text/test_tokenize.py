

from textplot.text import Text


def test_set_tokens():

    """
    tokenize() should record individual tokens.
    """

    t = Text('aa bb cc')

    assert t.tokens[0]['unstemmed'] == 'aa'
    assert t.tokens[1]['unstemmed'] == 'bb'
    assert t.tokens[2]['unstemmed'] == 'cc'
    assert len(t.tokens) == 3


def test_set_term_offsets():

    """
    During tokenization, store map of token -> offsets positions.
    """

    t = Text('aa bb aa bb')

    assert t.terms['aa'] == [0, 2]
    assert t.terms['bb'] == [1, 3]


def test_ignore_stopwords():

    """
    Stopwords should be represented as None in the token list.
    """

    t = Text('aa the bb an cc')

    assert t.tokens[0]['unstemmed'] == 'aa'
    assert t.tokens[1] == None
    assert t.tokens[2]['unstemmed'] == 'bb'
    assert t.tokens[3] == None
    assert t.tokens[4]['unstemmed'] == 'cc'
    assert len(t.tokens) == 5
