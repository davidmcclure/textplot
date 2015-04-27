

from textplot.text import Text
from nltk.stem import PorterStemmer


def test_unstem():

    """
    Given a word stem, Text#unstem() should return the most frequently-
    occurring unstemmed variant in the text.
    """

    # cat > cats
    t = Text('cat cat cats')
    assert t.unstem('cat') == 'cat'

    # cats > cat
    t = Text('cat cat cats cats cats')
    assert t.unstem('cat') == 'cats'
