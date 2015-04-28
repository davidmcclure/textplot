

from textplot.text import Text
from collections import OrderedDict


def test_most_frequent_terms():

    """
    most_frequent_terms() should return the N most frequent terms.
    """

    t = Text('aa bb bb cc cc cc')

    # Top 2 words are 'cc' and 'bb'
    assert t.most_frequent_terms(2) == set(['cc', 'bb'])


def test_merge_smallest_bucket():

    """
    Say 1000 gets passed as the depth, and the 1000th term in the term-counts
    dictionary has a count of 10. But, there are 20 other terms that also show
    up 10 times in the text. In this case, all of the terms in this smallest
    bucket should be included, so as not to arbitrarily omit words that appear
    with the same frequency as words that do get included.
    """

    t = Text('aa bb bb cc cc dd dd dd')

    # Top 2 words are 'cc' and 'bb'
    assert t.most_frequent_terms(2) == set(['dd', 'cc', 'bb'])
