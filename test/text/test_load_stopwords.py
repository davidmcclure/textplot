

import pkgutil
import os

from textplot.text import Text


def test_default_file():

    """
    When no path is passed to load_stopwords(), the default file in the
    textplot module should be loaded.
    """

    defaults = set(
        pkgutil
        .get_data('textplot', 'data/stopwords.txt')
        .decode('utf8')
        .splitlines()
    )

    t = Text('test')

    assert t.stopwords == defaults


def test_custom_file():

    """
    Load a custom file, when a path is passed.
    """

    path = os.path.join(
        os.path.dirname(__file__),
        'fixtures/stopwords.txt'
    )

    t = Text('test', stopwords=path)

    assert t.stopwords == set(['sa', 'sb', 'sc'])
