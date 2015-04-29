

from textplot.text import Text
from textplot.matrix import TextMatrix
from textplot.graphs import Skimmer


def frequent(path, term_depth=500, skim_depth=10, d_weights=False, **kwargs):

    """
    Use most frequent terms.
    """

    print('Tokenizing text...')
    t = Text.from_file(path)
    m = TextMatrix(t)

    print('Indexing terms:')
    m.index(t.most_frequent_terms(term_depth), **kwargs)

    g = Skimmer()

    print('Generating graph:')
    g.build(m, skim_depth, d_weights)

    return g
