

from textplot.text import Text
from textplot.graphs import Skimmer
from textplot.matrix import Matrix


def frequent(path, term_depth=500, skim_depth=10, d_weights=False, **kwargs):

    """
    Use most frequent terms.
    """

    print('Tokenizing text...')
    t = Text.from_file(path)
    m = Matrix()

    print('Indexing terms:')
    m.index(t, t.most_frequent_terms(term_depth), **kwargs)

    g = Skimmer()

    print('Generating graph:')
    g.build(t, m, skim_depth, d_weights)

    return g
