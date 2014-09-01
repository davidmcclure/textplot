

import os
import requests
import re
import matplotlib.pyplot as plt
import numpy as np
import utils

from nltk.stem import PorterStemmer
from collections import OrderedDict, Counter
from sklearn.neighbors import KernelDensity
from pyemd import emd


class Text(object):


    @classmethod
    def from_file(cls, path):

        """
        Create a text from a file.

        :param path: The file path.
        """

        return cls(open(path, 'r').read())


    def __init__(self, text):

        """
        Store the raw text, tokenize.

        :param text: The text as a raw string.
        """

        self.text = text
        self.stem = PorterStemmer().stem
        self.tokenize()


    def stopwords(self, path='stopwords.txt'):

        """
        Load a set of stopwords.
        """

        # Get an absolute path for the file.
        path = os.path.join(os.path.dirname(__file__), path)

        with open(path) as f:
            return set(f.read().splitlines())


    def tokenize(self):

        """
        Tokenize the text.
        """

        self.tokens = []
        self.terms = OrderedDict()

        # Load stopwords.
        stopwords = self.stopwords()

        # Generate tokens.
        i = 0
        for token in utils.tokenize(self.text):

            # Ignore stopwords.
            if token['unstemmed'] in stopwords:
                continue

            # Token:
            self.tokens.append(token)

            # Term:
            stemmed = token['stemmed']
            if stemmed in self.terms: self.terms[stemmed].append(i)
            else: self.terms[stemmed] = [i]

            i += 1


    def term_counts(self):

        """
        Map terms to instance counts.
        """

        counts = OrderedDict()
        for term in self.terms:
            counts[term] = len(self.terms[term])

        return utils.sort_dict(counts)


    def term_count_buckets(self):

        """
        Build a dictionary that maps occurrence counts to the terms that
        appear that many times in the text.
        """

        buckets = {}
        for term, count in self.term_counts().items():
            if count in buckets: buckets[count].append(term)
            else: buckets[count] = [term]

        return buckets


    def most_frequent_terms(self, depth):

        """
        Get the X most frequent terms in the text, and then probe down to get
        any other terms that have the same count as the last term.

        :param depth: The number of terms.
        """

        counts = self.term_counts()

        # Get the top X terms and the instance count of the last word.
        top_terms = set(counts.keys()[:depth])
        end_count = counts.values()[:depth][-1]

        # Merge in all other words with that appear that number of times, so
        # that we don't truncate the last bucket - eg, half of the words that
        # appear 5 times, but not the other half.

        bucket = self.term_count_buckets()[end_count]
        return top_terms.union(set(bucket))


    def most_frequent_tokens(self, depth):

        """
        Get a filtered list of tokens that just includes terms that are among
        the top X most frequent in the text.

        :param depth: The number of terms.
        """

        terms = self.most_frequent_terms(depth)
        return [t for t in self.tokens if t['stemmed'] in terms]


    def unstem(self, term):

        """
        Given a stemmed term, get the most common unstemmed variant.

        :param term: A stemmed term.
        """

        originals = []
        for i in self.terms[term]:
            originals.append(self.tokens[i]['unstemmed'])

        mode = Counter(originals).most_common(1)
        return mode[0][0]


    @utils.memoize
    def kde(self, term, bandwidth=500, samples=1000, kernel='epanechnikov'):

        """
        Estimate the kernel density of the instances of term in the text.

        :param term: A stememd term.
        :param bandwidth: The kernel width.
        :param samples: The number samples.
        :param kernel: The kernel function.
        """

        # Get the offsets of the term instances.
        terms = np.array(self.terms[term])[:, np.newaxis]

        # Fit the density estimator on the terms.
        kde = KernelDensity(kernel=kernel, bandwidth=bandwidth).fit(terms)

        # Score an evely-spaced array of samples.
        x_axis = np.linspace(0, len(self.tokens), samples)[:, np.newaxis]
        scores = kde.score_samples(x_axis)

        # Scale the scores to integrate to 1.
        return np.exp(scores) * (len(self.tokens) / samples)


    def kde_overlap(self, term1, term2, **kwargs):

        """
        How much do the kernel density estimates of two terms overlap?

        :param term1: The first term.
        :param term2: The second term.
        """

        t1_kde = self.kde(term1, **kwargs)
        t2_kde = self.kde(term2, **kwargs)

        # Integrate the overlap.
        overlap = np.minimum(t1_kde, t2_kde)
        return np.trapz(overlap)


    def anchored_kde_overlaps(self, anchor, **kwargs):

        """
        Compute the KDE overlaps between an anchor terms and all other terms.

        :param anchor: The anchor term.
        """

        pairs = OrderedDict()
        for term in self.terms:
            pairs[term] = self.kde_overlap(anchor, term, **kwargs)

        return utils.sort_dict(pairs)


    def emd(self, term1, term2, **kwargs):

        """
        Compute the "earth mover's distance" between two terms.

        :param term1: The first term.
        :param term2: The second term.
        :param distances: A distance matrix.
        """

        t1_kde = self.kde(term1, **kwargs)
        t2_kde = self.kde(term2, **kwargs)

        dm = utils.offset_matrix(t1_kde.size)
        return emd(t1_kde, t2_kde, dm)


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
