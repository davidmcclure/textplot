

import click

from textplot.text import Text
from textplot.graphs import Skimmer
from textplot.matrix import Matrix


def build_graph(path, term_depth=500, skim_depth=10,
                d_weights=False, **kwargs):

    """
    Tokenize a text, index a term matrix, and build out a graph.

    Args:
        path (str): The file path.
        term_depth (int): Consider the N most frequent terms.
        skim_depth (int): Connect each word to the N closest siblings.
        d_weights (bool): If true, give "close" nodes low weights.

    Returns:
        Skimmer: The indexed graph.
    """

    # Tokenize text.
    click.echo('\nTokenizing text...')
    t = Text.from_file(path)
    click.echo('Extracted %d tokens' % len(t.tokens))

    m = Matrix()

    # Index the term matrix.
    click.echo('\nIndexing terms:')
    m.index(t, t.most_frequent_terms(term_depth), **kwargs)

    g = Skimmer()

    # Construct the network.
    click.echo('\nGenerating graph:')
    g.build(t, m, skim_depth, d_weights)

    return g
