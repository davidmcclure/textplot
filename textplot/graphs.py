

import networkx as nx
import matplotlib.pyplot as plt
import utils

from abc import ABCMeta, abstractmethod
from clint.textui import progress


class Graph(object):


    __metaclass__ = ABCMeta


    def __init__(self):

        """
        Initialize the graph.
        """

        self.graph = nx.Graph()


    @abstractmethod
    def build(self):
        pass


    def draw_spring(self, **kwargs):

        """
        Render a spring layout.
        """

        nx.draw_spring(
            self.graph,
            with_labels=True,
            font_size=10,
            edge_color='#dddddd',
            node_size=0,
            **kwargs
        )

        plt.show()


    def write_gml(self, path):

        """
        Write a GML file.

        :param path: The file path.
        """

        nx.readwrite.gml.write_gml(self.graph, path)


class Skimmer(Graph):


    def build(self, matrix, skim_depth=10, d_weights=False):

        """
        1. For each term in the passed matrix, score its KDE similarity with
        all other indexed terms.

        2. With the ordered stack of similarities in hand, skim off the top X
        pairs and add them as edges.

        :param matrix: A term matrix.
        :param skim_depth: The number of siblings to register for each term.
        :param d_weights: If true, give "close" words low edge weights.
        """

        for anchor in progress.bar(matrix.terms):

            n1 = matrix.text.unstem(anchor)

            # Heaviest pair scores:
            pairs = matrix.anchored_pairs(anchor).items()
            for term, weight in pairs[:skim_depth]:

                # If edges represent distance, use the complement of the raw
                # score, so that similar words are connected by "short" edges.
                if d_weights: weight = 1-weight

                n2 = matrix.text.unstem(term)
                self.graph.add_edge(n1, n2, weight=weight)


class Listserv(Graph):


    def build(self, matrix, skim_depth=10):

        """
        Register term count, KDE max, and center-of-mass on nodes.

        :param matrix: A term matrix.
        :param skim_depth: The number of sibling edges.
        """

        # Nodes:
        for term in progress.bar(matrix.terms):

            # Unstem the label.
            label = matrix.text.unstem(term);

            # Register the metadata.
            self.graph.add_node(label, {
                'count':    len(matrix.text.terms[term]),
                'kde_max':  matrix.text.kde_max(term),
                'median':   matrix.text.median_ratio(term)
            })

        # Edges:
        for anchor in progress.bar(matrix.terms):

            n1 = matrix.text.unstem(anchor)

            # Heaviest pair scores:
            pairs = matrix.anchored_pairs(anchor).items()
            for term, weight in pairs[:skim_depth]:

                n2 = matrix.text.unstem(term)
                self.graph.add_edge(n1, n2, weight=weight)
