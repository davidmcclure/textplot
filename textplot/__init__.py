

from text import Text
from matrix import Matrix
from graphs import *


def skimmer(path, term_depth=500, skim_depth=10, d_weights=False, **kwargs):

    """
    Use most frequent terms.
    """

    t = Text.from_file(path)
    m = Matrix(t)

    print 'Indexing terms:'
    terms = t.all_kde_maxes(**kwargs).keys()[:term_depth]
    m.index(terms, **kwargs)

    g = Skimmer()

    print 'Generating graph:'
    g.build(m, skim_depth, d_weights)

    return g
