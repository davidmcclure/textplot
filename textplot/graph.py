

import networkx as nx

from clint.textui import progress


class Graph(object):


    def __init__(self):

        """
        Initialize the graph.
        """

        self.graph = nx.Graph()


    def top_pairs(self, matrix, depth):

        """
        For each of the X most frequent words in the text, use the Y heaviest
        pair scores as edges in a graph.

        :param matrix: A term matrix.
        :param depth: Pairs per word.
        """

        for anchor in progress.bar(matrix.terms):

            n1 = matrix.text.unstem(anchor)

            # Heaviest pair scores:
            pairs = matrix.all_pairs(anchor).items()
            for term, weight in pairs[depth]:

                n2 = matrix.text.unstem(term)
                self.graph.add_edge(n1, n2, weight=weight)
