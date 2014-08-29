

import networkx as nx
import matplotlib.pyplot as plt

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


    def build(self, matrix, depth):

        """
        1. For each term in the passed matrix, score its KDE similarity with
        all other indexed terms.

        2. With the ordered stack of similarities in hand, skim off the top X
        pairs and add them as edges.

        :param matrix: A term matrix.
        :param depth: Pairs per word.
        """

        for anchor in progress.bar(matrix.terms):

            n1 = matrix.text.unstem(anchor)

            # Heaviest pair scores:
            pairs = matrix.anchored_pairs(anchor).items()
            for term, weight in pairs[:depth]:

                n2 = matrix.text.unstem(term)
                self.graph.add_edge(n1, n2, weight=weight)


class Texture(Graph):


    def build(self, text):

        """
        An implementation of the Textexture algorithm described here:
        noduslabs.com/publications/Pathways-Meaning-Text-Network-Analysis.pdf

        :param text: The text.
        """

        # 2-word pass:
        for w in text.window(2):

            w1 = w[0]['stemmed']
            w2 = w[1]['stemmed']

            # Update an existing edge.
            if self.graph.has_edge(w1, w2):
                self.graph.edge[w1][w2]['weight'] += 1

            # Or, create a new edge.
            else: self.graph.add_edge(w1, w2, weight=1)

        # 5-word pass:
        for w in text.window(5):

            w1 = w[0]['stemmed']
            w2 = w[-1]['stemmed']

            # Update an existing edge.
            if self.graph.has_edge(w1, w2):
                self.graph.edge[w1][w2]['weight'] += 1

            # Or, create a new edge.
            else: self.graph.add_edge(w1, w2, weight=1)
