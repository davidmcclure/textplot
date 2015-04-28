

from textplot.text import Text
from collections import OrderedDict


def test_term_count_buckets():

    """
    term_count_buckets() should map integer counts to the list of terms in the
    text that appear that many times.
    """

    t = Text('aa bb bb cc cc dd dd dd')

    assert t.term_count_buckets() == {
        1: ['aa'],
        2: ['bb', 'cc'],
        3: ['dd']
    }
