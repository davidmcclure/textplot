

from text import Text
from matrix import Matrix
from graphs import Skimmer


def skimmer(path, word_depth, skim_depth, **kwargs):

    """
    Construct a "Skimmer" graph.

    :param path: The file path.
    :param word_depth: The number of words.
    :param skim_depth: The number of pair similarities per term.
    """

    t = Text.from_file(path)
    m = Matrix(t)

    print 'Indexing terms:'
    m.index(t.most_frequent_terms(w_depth), **kwargs)

    g = Skimmer()

    print 'Generating graph:'
    g.build(m, p_depth)

    return g
