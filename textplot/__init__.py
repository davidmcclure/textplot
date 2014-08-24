

from text import Text
from matrix import Matrix
from graph import Graph


def graph(path, w_depth, p_depth, **kwargs):

    t = Text.from_file(path)
    m = Matrix(t)
    m.index(t.most_frequent_terms(w_depth), **kwargs)

    g = Graph()
    g.build(m, p_depth)

    return g
