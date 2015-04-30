

from textplot.text import Text
from textplot.matrix import Matrix


def test_anchored_pairs():

    """
    For a given anchor term, anchored_pairs() should return an ordered map of
    term -> distance for all other indexed terms.
    """

    t = Text('aa bb cc dd')
    m = Matrix()

    m.index(t)

    pairs = m.anchored_pairs('aa')

    assert list(pairs.keys()) == ['bb', 'cc', 'dd']
    assert pairs['bb'] > pairs['cc'] > pairs['dd']
