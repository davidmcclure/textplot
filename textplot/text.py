

import os
import requests
import re
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import redis
import utils
import json
import datetime

from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from collections import OrderedDict, Counter
from sklearn.neighbors import KernelDensity
from scipy.misc import comb
from itertools import combinations
from clint.textui import progress


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
        Set the key prefix, connect to Redis.

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

        # Cache stopwords.
        stopwords = self.stopwords()

        # Get tokens.
        i = 0
        for token in utils.tokenize(self.text):

            # Don't index stopwords.
            if token['unstemmed'] in stopwords:
                continue

            # Token:
            self.tokens.append(token)

            # Term:
            stemmed = token['stemmed']
            if stemmed in self.terms: self.terms[stemmed].append(i)
            else: self.terms[stemmed] = [i]

            i += 1


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
        Given a stemmed term, get the most common unstemmed variant.

        :param term: A stemmed term.
        """

        originals = []
        for i in self.terms[term]:
            originals.append(self.tokens[i]['unstemmed'])

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

        # Get the offsets of the term instances.
        offsets = np.array(self.terms[term])[:, np.newaxis]

        # Fit the density estimator on the offsets.
        kde = KernelDensity(kernel=kernel, bandwidth=bandwidth).fit(offsets)

        # Estimate the density.
        samples = np.linspace(0, len(self.tokens), samples)[:, np.newaxis]
        return np.exp(kde.score_samples(samples))


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


    @utils.memoize
    def distance_between_terms(self, term1, term2, **kwargs):

        """
        How much do the kernel density estimates of two terms overlap?

        :param term1: The first term.
        :param term2: The second term.
        """

        t1_kde = self.kde(term1, **kwargs)
        t2_kde = self.kde(term2, **kwargs)

        # How much space between samples?.
        spacing = float(len(self.tokens)) / t1_kde.size

        # Integrate overlap between the two.
        overlap = np.minimum(t1_kde, t2_kde)
        return np.trapz(overlap, dx=spacing)


    def index_distances(self, **kwargs):

        """
        Index all word pair distances.
        """

        self.distances = {}

        expected = comb(len(self.terms), 2)
        with progress.Bar(expected_size=expected) as bar:

            i = 0
            for t1, t2 in combinations(self.terms.keys(), 2):

                self.set_distance(t1, t2, **kwargs)

                # Update progress.
                i += 1
                if i % 1000 == 0: bar.show(i)


    @utils.memoize
    def distance_key(self, term1, term2):

        """
        Get a unique key for a term pair.

        :param term1: The first term.
        :param term2: The second term.
        """

        return '_'.join(sorted((term1, term2)))


    def set_distance(self, term1, term2, **kwargs):

        """
        Set the value for a pair of terms.

        :param term1: The first term.
        :param term2: The second term.
        """

        k = self.distance_key(term1, term2)
        d = self.distance_between_terms(term1, term2, **kwargs)
        self.distances[k] = d


    @utils.memoize
    def distance(self, term1, term2):

        """
        Get the value for a pair of terms.

        :param term1: The first term.
        :param term2: The second term.
        """

        k = self.distance_key(term1, term2)
        if k in self.distances: return self.distances[k]
        else: return None


    def save_distances(self, path):

        """
        Save the distances as JSON.

        :param path: The file path.
        """

        with open(path, 'w') as out:
            json.dump(self.distances, out)


    def load_distances(self, path):

        """
        Load saved term distances JSON.

        :param path: The file path.
        """

        self.distances = json.load(open(path, 'r'))


    @utils.memoize
    def all_distances_from_term(self, anchor, sort=True):

        """
        Given a term, get the distances for all other words.

        :param anchor: The anchor term.
        :param sort: If true, sort the dictionary by value.
        """

        distances = OrderedDict()
        for term in self.terms:
            distances[term] = self.distance(anchor, term)

        if sort: distances = utils.sort_dict(distances)
        return distances


    def graph(self, depth=20):

        """
        For each term, use the liks with the nearest X terms as graph edges.

        :param depth: The number of edges to skim.
        """

        graph = nx.Graph()

        with progress.Bar(expected_size=len(self.terms)) as bar:

            for i, term in enumerate(self.terms):

                # Skim off the top X distances.
                top = self.all_distances_from_term(term).items()[:depth]

                # Unstem the terms and register the distances as edges.
                for edge in top:
                    n1 = self.unstem(term)
                    n2 = self.unstem(edge[0])
                    graph.add_edge(n1, n2, weight=edge[1])

                bar.show(i)

        return graph
