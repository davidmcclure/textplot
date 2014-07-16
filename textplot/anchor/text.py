

import matplotlib.pyplot as plt
from textplot.text import Text as BaseText


class Text(BaseText):


    def plot_2d_term_comparison(self, word1, word2, **kwargs):

        """
        For two words, compute the similarities with all other words in the
        text. Then, put word1 on the X axis and word2 on the Y axis, and plot
        all of the terms according to their weights.

        :param word1: The first word.
        :param word1: The second word.
        """

        w1_sims = self.get_all_similarities(word1, **kwargs)
        w2_sims = self.get_all_similarities(word2, **kwargs)

        xs = [s[1] for s in w1_sims.items()]
        ys = [s[1] for s in w2_sims.items()]
        plt.scatter(xs, ys)

        for term in self.terms:
            plt.annotate(term, (w1_sims[term], w2_sims[term]))

        plt.show()


    def plot_weighted_centroids(self, anchors, **kwargs):

        """
        Given a list of anchor words, plot the weighted centroids of all other
        terms in the text.

        :param anchors: 3-tuples of (term, X, Y).
        """

        pass # TODO
