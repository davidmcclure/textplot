

from text import Text
from matrix import Matrix
from graphs import *


def skimmer(path, term_depth=500, skim_depth=10, **kwargs):

    """
    Use most frequent terms.
    """

    t = Text.from_file(path)
    m = Matrix(t)

    print 'Indexing terms:'
    m.index(t.most_frequent_terms(term_depth), **kwargs)

    g = Skimmer()

    print 'Generating graph:'
    g.build(m, skim_depth)

    return g
