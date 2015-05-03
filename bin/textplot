#!/usr/bin/env python


import click

from textplot.helpers import build_graph


@click.group()
def textplot():
    pass


@textplot.command()

@click.argument('in_path', type=click.Path())
@click.argument('out_path', type=click.Path())

@click.option(
    '--term_depth',
    default=1000,
    help='The total number of terms in the network.'
)

@click.option(
    '--skim_depth',
    default=10,
    help='The number of words each word is connected to in the network.'
)

@click.option(
    '--d_weights',
    is_flag=True,
    help='If set, connect "close" terms with low edge weights.'
)

@click.option(
    '--bandwidth',
    default=2000,
    help='The kernel bandwidth.'
)

@click.option(
    '--samples',
    default=1000,
    help='The number of times the kernel density is sampled.'
)

@click.option(
    '--kernel',
    default='gaussian',
    help='The kernel function.',
    type=click.Choice([
        'gaussian',
        'tophat',
        'epanechnikov',
        'exponential',
        'linear',
        'cosine'
    ])
)

def generate(in_path, out_path, **kwargs):

    """
    Convert a text into a GML file.
    """

    g = build_graph(in_path, **kwargs)
    g.write_gml(out_path)


if __name__ == '__main__':
    textplot()
