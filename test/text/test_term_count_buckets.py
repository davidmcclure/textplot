

from textplot.text import Text
from collections import OrderedDict


def test_term_counts():

    """
    Text#term_counts() should return a map of term -> count.
    """

    t = Text('aa bb bb cc cc dd dd dd')

    assert t.term_count_buckets() == {
        1: ['aa'],
        2: ['bb', 'cc'],
        3: ['dd']
    }
