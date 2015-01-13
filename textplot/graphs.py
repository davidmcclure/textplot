

import networkx as nx
import matplotlib.pyplot as plt

from abc import ABCMeta, abstractmethod
from clint.textui import progress


class Graph:


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


    def write_graphml(self, path):

        """
        Write a GraphML file.

        :param path: The file path.
        """
        # The GraphML writer cannot handle numpy types.
        # Copy the graph and convert weights to python floats.
        graph = self.graph.copy()
        for edge in graph.edges_iter(data=True):
            edge[2]['weight'] = float(edge[2]['weight'])
        nx.readwrite.graphml.write_graphml(graph, path)


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
            for term, weight in list(pairs)[:skim_depth]:

                # If edges represent distance, use the complement of the raw
                # score, so that similar words are connected by "short" edges.
                if d_weights: weight = 1-weight

                n2 = matrix.text.unstem(term)
                self.graph.add_edge(n1, n2, weight=weight)
