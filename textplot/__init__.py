

from text import Text
from matrix import Matrix
from graphs import *


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
    m.index(t.most_frequent_terms(word_depth), **kwargs)

    g = Skimmer()

    print 'Generating graph:'
    g.build(m, skim_depth)

    return g


def texture(path, **kwargs):

    """
    Construct a "Texture" graph.

    :param path: The file path.
    """

    t = Text.from_file(path)
    g = Texture()

    g.build(t)
    return g
