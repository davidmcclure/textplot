

from text import Text
from matrix import Matrix
from graph import Graph


def g1(path, w_depth, p_depth, **kwargs):

    t = Text.from_file(path)
    m = Matrix(t)
    m.index(t.most_frequent_terms(w_depth), **kwargs)

    g = Graph()
    g.g1(m, p_depth)

    return g


def g2(path, w_depth, p_depth, **kwargs):

    t = Text.from_file(path)
    m = Matrix(t)
    m.index(t.most_frequent_terms(w_depth), **kwargs)

    g = Graph()
    g.g2(m, p_depth)

    return g
