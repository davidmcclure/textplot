

import requests
import datetime
import re
import matplotlib.pyplot as plt
import numpy as np
import utils

from nltk.stem import PorterStemmer
from collections import OrderedDict, Counter
from sklearn.neighbors import KernelDensity
from itertools import combinations


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
    def term_counts(self, sort=True):

        """
        Map terms to instance counts.

        :param sort: If true, sort the dictionary by value.
        """

        counts = OrderedDict()
        for term in self.terms:
            counts[term] = len(self.terms[term])

        if sort: counts = utils.sort_dict(counts)
        return counts


    @utils.memoize
    def unstem(self, term):

        """
        Given a stemmed word, get the most common unstemmed version.

        :param term: A stemmed term.
        """

        originals = []
        for i in self.terms[term]:
            originals.append(self.tokens[i]['original'])

        mode = Counter(originals).most_common(1)
        return mode[0][0]


    @utils.memoize
    def kde(self, term, bandwidth=5000, samples=1000, kernel='epanechnikov'):

        """
        Estimate the kernel density of the instances of term in the text.

        :param term: The term to estimate.
        :param bandwidth: The kernel width.
        :param samples: The number points to sample.
        :param kernel: The kernel function.
        """

        # Term offsets and density sample axis:
        offsets = np.array(self.terms[term])[:, np.newaxis]
        samples = np.linspace(0, len(self.tokens), samples)[:, np.newaxis]

        # Density estimator:
        kde = KernelDensity(kernel=kernel, bandwidth=bandwidth).fit(offsets)

        # Estimate the kernel density.
        return np.exp(kde.score_samples(samples))


    @utils.memoize
    def distance_between_terms(self, term1, term2, **kwargs):

        """
        How much do the kernel density estimates of two terms overlap?

        :param term1: The first term.
        :param term2: The second term.
        """

        t1_kde = self.kde(term1, **kwargs)
        t2_kde = self.kde(term2, **kwargs)

        # Get the spacing between samples.
        spacing = float(len(self.tokens)) / t1_kde.size

        # Integrate overlap between the two.
        overlap = np.minimum(t1_kde, t2_kde)
        return np.trapz(overlap, dx=spacing)


    @utils.memoize
    def all_distances_from_term(self, anchor, sort=True, **kwargs):

        """
        Given an anchor word, compute the distances for all other words.

        :param anchor: The anchor term.
        :param sort: If true, sort the dictionary by value.
        """

        sims = OrderedDict()
        for term in self.terms:
            sims[term] = self.distance_between_terms(anchor, term, **kwargs)

        if sort: sims = utils.sort_dict(sims)
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
