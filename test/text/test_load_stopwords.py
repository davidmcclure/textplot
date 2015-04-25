

import pkgutil

from textplot.text import Text


def test_default_file():

    """
    When no path is passed to Text#load_stopwords(), the default file in the
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

    pass
