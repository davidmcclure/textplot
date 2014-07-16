

import requests
import re
import textplot.utils as utils
import matplotlib.pyplot as plt
import numpy as np

from nltk.stem import PorterStemmer
from sklearn.neighbors import KernelDensity
from collections import OrderedDict


class Text(object):


    @classmethod
    def from_file(cls, path):

        """
        Create a text from a filepath.

        :param cls: The Text class.
        :param path: The filepath.
        """

        return cls(open(path, 'r').read())


    @classmethod
    def from_url(cls, url):

        """
        Create a text from a URL.

        :param cls: The Text class.
        :param path: The URL.
        """

        return cls(requests.get(url).text)


    def __init__(self, text):

        """
        Store and tokenize the text.

        :param text: The text as a raw string.
        """

        self.text = text
        self.stem = PorterStemmer().stem
        self.tokenize()


    def tokenize(self):

        """
        Tokenize the text.
        """

        self.tokens = []
        self.terms = OrderedDict()

        # Strip tags and downcase.
        text = utils.strip_tags(self.text).lower()

        # Walk words in the text.
        pattern = re.compile('[a-z]+')
        for i, match in enumerate(re.finditer(pattern, text)):

            # Stem the token.
            original = match.group(0)
            stemmed = self.stem(original)

            # Token:
            self.tokens.append({
                'original': original,
                'stemmed':  stemmed,
                'left':     match.start(),
                'right':    match.end()
            })

            # Token -> offset:
            if stemmed in self.terms: self.terms[stemmed].append(i)
            else: self.terms[stemmed] = [i]


    @utils.memoize
    def kde(self, word, bandwidth=5000, samples=1000, kernel='epanechnikov'):

        """
        Estimate the kernel density of the instances of word in the text.

        :param word: The word to query for.
        :param bandwidth: The kernel width.
        :param samples: The number points to sample.
        :param kernel: The kernel function.
        """

        # Term offsets and density sample axis:
        offsets = np.array(self.terms[word])[:, np.newaxis]
        samples = np.linspace(0, len(self.tokens), samples)[:, np.newaxis]

        # Density estimator:
        kde = KernelDensity(kernel=kernel, bandwidth=bandwidth).fit(offsets)

        # Estimate the kernel density.
        return np.exp(kde.score_samples(samples))


    @utils.memoize
    def get_pair_similarity(self, anchor, sample, **kwargs):

        """
        How similar is the distribution of a sample word to the distribution
        of an anchor word?

        :param anchor: The base word.
        :param sample: The query word.
        """

        a_kde = self.kde(anchor, **kwargs)
        s_kde = self.kde(sample, **kwargs)

        # Get the overlap between the two.
        overlap = [min(a_kde[i], s_kde[i]) for i in xrange(a_kde.size)]
        return np.trapz(overlap)


    @utils.memoize
    def get_all_similarities(self, anchor, **kwargs):

        """
        Given an anchor word, compute the similarities for all other words in
        the text.

        :param anchor: The anchor word.
        """

        anchor = self.stem(anchor)

        sims = OrderedDict()
        for term in self.terms:
            sim = self.get_pair_similarity(anchor, term, **kwargs)
            sims[term] = sim

        return sims


    @utils.memoize
    def query(self, query, **kwargs):

        """
        Given a query text as a raw string, sum the kernel density estimates
        of each of the tokens in the query.

        :param query: The query string.
        """

        query_text = Text(query)
        signals = []

        for term in query_text.terms:
            if term in self.terms:
                signals.append(self.kde(term, **kwargs))

        result = np.zeros(signals[0].size)
        for signal in signals: result += signal

        return result


    def plot_term_kdes(self, words, **kwargs):

        """
        Plot kernel density estimates for multiple words.

        :param words: The words to query.
        :param bandwidth: The kernel width.
        """

        for word in words:
            kde = self.kde(self.stem(word), **kwargs)
            plt.plot(kde)

        plt.show()


    def plot_query(self, query, **kwargs):

        """
        Plot a query result.

        :param query: The query string.
        """

        result = self.query(query, **kwargs)
        plt.plot(result)
        plt.show()


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
