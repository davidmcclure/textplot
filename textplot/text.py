

import os
import requests
import re
import matplotlib.pyplot as plt
import numpy as np
import utils

from nltk.stem import PorterStemmer
from sklearn.neighbors import KernelDensity
from collections import OrderedDict, Counter
from pyemd import emd
from scipy.stats import rankdata


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
        Get an ordered dictionary of term counts.
        """

        counts = OrderedDict()
        for term in self.terms:
            counts[term] = len(self.terms[term])

        return utils.sort_dict(counts)


    def term_count_ranks(self):

        """
        Get a ranked list of term counts.
        """

        counts = self.term_counts()
        ranks = rankdata(counts.values(), method='min')

        for i, term in enumerate(counts.keys()):
            counts[term] = ranks[i]

        return counts


    def term_count_percentiles(self):

        """
        Get a ranked list of term count percentiles.
        """

        counts = self.term_counts()
        top = float(max(counts.values()))

        for term, count in counts.items():
            counts[term] = np.log(count / top * 100) / 100

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


    def kde_max(self, term, **kwargs):

        """
        Get the max value on a term's KDE.

        :param term: A stemmed term.
        """

        return np.amax(self.kde(term, **kwargs))


    def kde_maxima(self, **kwargs):

        """
        Get an ordered dictionary of KDE maxima.
        """

        maxima = OrderedDict()
        for term in self.terms:
            maxima[term] = self.kde_max(term, **kwargs)

        return utils.sort_dict(maxima)


    def kde_max_ranks(self, **kwargs):

        """
        Get a ranked stack of KDE maxima.
        """

        maxima = self.kde_maxima(**kwargs)
        ranks = rankdata(maxima.values())

        for i, term in enumerate(maxima.keys()):
            maxima[term] = ranks[i]

        return maxima


    def kde_max_percentiles(self, **kwargs):

        """
        Get a ranked list of KDE max percentiles.
        """

        maxima = self.kde_maxima(**kwargs)
        top = float(max(maxima.values()))

        for term, peak in maxima.items():
            maxima[term] = np.log(peak / top * 100) / 100

        return utils.sort_dict(maxima)


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
        Compute the KDE overlaps between an anchor term and all other terms.

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


    def semantic_focus_ranks(self, **kwargs):

        """
        For each term, get the sum of the ranks of the KDE maximum and the
        instance count, which proxies semantic focus.
        """

        km = self.kde_max_percentiles(**kwargs)
        tc = self.term_count_percentiles()

        ranks = OrderedDict()
        for term in self.terms:
            ranks[term] = np.linalg.norm(np.array(0.5-tc[term], 0.5-km[term]))

        return utils.sort_dict(ranks, reverse=False)


    def most_focused_terms(self, depth, **kwargs):

        """
        Get the X most semantically focused terms in the text.

        :param depth: The number of terms.
        """

        return self.semantic_focus_ranks().keys()[:depth]


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


    def plot_semantic_focus(self, **kwargs):

        """
        Plot KDE max vs. term count.
        """

        km_p = self.kde_max_percentiles(**kwargs)
        tc_p = self.term_count_percentiles()

        xs = []
        ys = []
        for term in self.terms:
            x = tc_p[term]
            y = km_p[term]
            xs.append(x)
            ys.append(y)
            plt.annotate(term, xy=(x,y))

        plt.scatter(xs, ys)
        plt.xlabel('Term Count')
        plt.ylabel('KDE Max')

        plt.show()
