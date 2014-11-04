

import utils

from collections import OrderedDict
from text import Text
from matrix import Matrix
from graphs import *


def frequent(path, term_depth=500, skim_depth=10, d_weights=False, **kwargs):

    """
    Use most frequent terms.
    """

    t = Text.from_file(path)
    m = Matrix(t)

    print 'Indexing terms:'
    m.index(t.most_frequent_terms(term_depth), **kwargs)

    g = Skimmer()

    print 'Generating graph:'
    g.build(m, skim_depth, d_weights)

    return g


def clumpy(path, term_depth=500, skim_depth=10, d_weights=False, **kwargs):

    """
    Use "clumpiest" terms.
    """

    t = Text.from_file(path)
    m = Matrix(t)

    print 'Indexing terms:'
    m.index(t.densities(**kwargs).keys()[:term_depth], **kwargs)

    g = Skimmer()

    print 'Generating graph:'
    g.build(m, skim_depth, d_weights)

    return g


def diachronic(path, term_depth=3000, spike_depth=1000, skim_depth=30,
             spike_bandwidth=500000, **kwargs):

    """
    Use most "spiky" terms, to capture diachronic shifts.
    """

    t = Text.from_file(path)
    m = Matrix(t)

    # Get the top X most frequent terms.
    frequent = t.most_frequent_terms(term_depth)

    spiky = OrderedDict()
    for term in frequent:
        spiky[term] = t.kde_max(term, bandwidth=spike_bandwidth)

    # Sort by KDE max.
    spiky = utils.sort_dict(spiky)

    print 'Indexing terms:'
    m.index(spiky.keys()[:spike_depth], **kwargs)

    g = Diachronic()

    print 'Generating graph:'
    g.build(m, skim_depth)

    return g
