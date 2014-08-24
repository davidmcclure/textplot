

from text import Text
from matrix import Matrix
from graphs import Skimmer


def skimmer(path, w_depth, p_depth, **kwargs):

    t = Text.from_file(path)
    m = Matrix(t)
    m.index(t.most_frequent_terms(w_depth), **kwargs)

    g = Skimmer()
    g.build(m, p_depth)

    return g
