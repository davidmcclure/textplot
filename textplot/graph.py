

import networkx as nx
import matplotlib.pyplot as plt

from clint.textui import progress


class Graph(object):


    def __init__(self):

        """
        Initialize the graph.
        """

        self.graph = nx.Graph()


    def g1(self, matrix, depth):

        """
        For each term, compute the pair score with all other terms. Then, skim
        off the top X pairs and add them as edges.

        :param matrix: A term matrix.
        :param depth: Pairs per word.
        """

        for anchor in progress.bar(matrix.terms):

            n1 = matrix.text.unstem(anchor)

            # Heaviest pair scores:
            pairs = matrix.all_pairs(anchor).items()
            for term, weight in pairs[:depth]:

                n2 = matrix.text.unstem(term)
                self.graph.add_edge(n1, n2, weight=weight)


    def g2(self, matrix, depth):

        """
        For each term, compute the pair score with all other terms. Then, skim
        off the top X pairs and add them as edges.

        :param matrix: A term matrix.
        :param depth: The number of edges.
        """

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
