

import networkx as nx
import matplotlib.pyplot as plt

from clint.textui import progress


class GraphBuilder(object):


    def __init__(self, text):
        """ Set the text. """
        self.text = text


    def top_terms_top_overlaps(self, t_depth=500, o_depth=10, **kwargs):

        """
        Get the X most frequent terms in the text. For each term, get the top
        X closes KDE overlaps, and use the pairs as weighted edges.

        :param t_depth: The number of terms.
        :param o_depth: The number of overlaps.
        """

        self.graph = nx.Graph()

        # Most frequent X terms:
        terms = self.text.most_frequent_terms(t_depth)
        for anchor in progress.bar(terms):

            n1 = self.text.unstem(anchor)

            # Closest X overlaps:
            overlaps = self.text.all_kde_overlaps(anchor, **kwargs).items()
            for term, overlap in overlaps[:o_depth]:

                n2 = self.text.unstem(term)
                self.graph.add_edge(n1, n2, weight=overlap)
                print n1, n2


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
