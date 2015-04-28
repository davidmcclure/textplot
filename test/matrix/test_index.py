

from textplot.text import Text
from textplot.matrix import TextMatrix


def test_index():

    """
    index() should index the Bray-Curtis distances between terms.
    """

    t = Text('aa bb cc')
    m = TextMatrix()

    m.index(t)

    assert m.get_pair('aa', 'bb') == t.score_braycurtis('aa', 'bb')
    assert m.get_pair('aa', 'cc') == t.score_braycurtis('aa', 'cc')
    assert m.get_pair('bb', 'cc') == t.score_braycurtis('bb', 'cc')


def test_term_subset():

    """
    When a subset of terms is passed, just those terms should be indexed.
    """

    t = Text('aa bb cc')
    m = TextMatrix()

    m.index(t, terms=['aa', 'bb'])

    # Should index 'aa' and 'bb'.
    assert m.get_pair('aa', 'bb') == t.score_braycurtis('aa', 'bb')

    # Should ignore 'cc'.
    assert not m.get_pair('aa', 'cc')
    assert not m.get_pair('bb', 'cc')
