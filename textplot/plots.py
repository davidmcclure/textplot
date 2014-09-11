

import ggplot as gp
import pandas as pd


class Plots(object):


    def __init__(self, text):

        """
        :param text: A text instance.
        """

        self.text = text


    def save(self, path):

        """
        :param path: A target file path.
        """

        gp.ggsave(self.plot, path)


    def plot_term_histogram(self, term):

        """
        Plot the X-axis offsets of a term.

        :param term: The unstemmed term to plot.
        """

        df = pd.DataFrame({
            'offsets': self.text.terms[self.text.stem(term)]
        })

        self.plot = gp.ggplot(gp.aes(x='offsets'), data=df) + \
            gp.geom_histogram() + \
            gp.xlab('Word Offset') + \
            gp.ylab('Number of Occurrences') + \
            gp.theme_bw()
