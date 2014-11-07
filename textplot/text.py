

import os
import requests
import re
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import utils

from nltk.stem import PorterStemmer
from sklearn.neighbors import KernelDensity
from collections import OrderedDict, Counter
from pyemd import emd
from scipy.spatial import distance
from scipy import ndimage


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
        for token in utils.tokenize(self.text):

            # Ignore stopwords.
            if token['unstemmed'] in stopwords:
                self.tokens.append(None)

            else:

                # Token:
                self.tokens.append(token)

                # Term:
                offsets = self.terms.setdefault(token['stemmed'], [])
                offsets.append(token['offset'])


    def term_counts(self):

        """
        Get an ordered dictionary of term counts.
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


    def term_distances(self, term):

        """
        Get a list of distances between the occurrences of a term.

        :param term: A stemmed term.
        """

        distances = []
        for o1, o2 in utils.window(self.terms[term], 2):
            distances.append(o2-o1)

        return distances


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
    def kde(self, term, bandwidth=2000, samples=1000, kernel='gaussian'):

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


    def score_intersect(self, term1, term2, **kwargs):

        """
        Compute the geometric area of the overlap between the kernel density
        estimates of two terms.

        :param term1: The first term.
        :param term2: The second term.
        """

        t1_kde = self.kde(term1, **kwargs)
        t2_kde = self.kde(term2, **kwargs)

        # Integrate the overlap.
        overlap = np.minimum(t1_kde, t2_kde)
        return np.trapz(overlap)


    def score_cosine(self, term1, term2, **kwargs):

        """
        Compute a weighting score based on the cosine distance between the
        kernel density estimates of two terms.

        :param term1: The first term.
        :param term2: The second term.
        """

        t1_kde = self.kde(term1, **kwargs)
        t2_kde = self.kde(term2, **kwargs)

        return 1-distance.cosine(t1_kde, t2_kde)


    def score_braycurtis(self, term1, term2, **kwargs):

        """
        Compute a weighting score based on the "City Block" distance between
        the kernel density estimates of two terms.

        :param term1: The first term.
        :param term2: The second term.
        """

        t1_kde = self.kde(term1, **kwargs)
        t2_kde = self.kde(term2, **kwargs)

        return 1-distance.braycurtis(t1_kde, t2_kde)


    def score_emd(self, term1, term2, **kwargs):

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


    def anchored_scores(self, anchor, method='braycurtis', **kwargs):

        """
        Compute the intersections between an anchor term and all other terms.

        :param anchor: The anchor term.
        :param method: The scoring function.
        """

        evaluator = getattr(self, 'score_'+method)

        pairs = OrderedDict()
        for term in self.terms:
            pairs[term] = evaluator(anchor, term, **kwargs)

        return utils.sort_dict(pairs)


    def kde_max(self, term, **kwargs):

        """
        Get the maximum value of a term's KDE.

        :param term: A stemmed term.
        """

        return np.amax(self.kde(term, **kwargs))


    def normalized_kde_maxima(self, **kwargs):

        """
        For each term, get the difference between the term's KDE max and the
        lowest KDE max of any term.
        """

        maxima = OrderedDict()
        for term in self.terms:
            maxima[term] = self.kde_max(term, **kwargs)

        lowest = np.amin(maxima.values())
        for term in self.terms:
            maxima[term] -= lowest

        return utils.sort_dict(maxima)


    def frequency_ratios(self):

        """
        For each term, get the ratio between the number of times that the term
        occurs and the number of times that the most frequent term occurs.
        """

        counts = self.term_counts()

        highest = float(np.amax(counts.values()))
        for term in self.terms:
            counts[term] /= highest

        return utils.sort_dict(counts)


    def densities(self, **kwargs):

        """
        For each term, compute a "density" score by multiplying the normalized
        height of the kernel density estimate by the frequency ratio.
        """

        kms = self.normalized_kde_maxima(**kwargs)
        frs = self.frequency_ratios()

        densities = OrderedDict()
        for term in self.terms:
            densities[term] = kms[term] * frs[term]

        return utils.sort_dict(densities)


    def median_ratio(self, term):

        """
        Get the median offset as a ratio with the text length.
        :param term: A stemmed term.
        """

        return np.median(self.terms[term]) / len(self.tokens)


    def kde_max_ratio(self, term, **kwargs):

        """
        Get the position ratio of a term's KDE max.

        :param term: A stemmed term.
        """

        kde = self.kde(term, **kwargs)
        return np.where(kde==np.amax(kde))[0][0] / float(len(kde))


    def kde_center_of_mass_ratio(self, term, **kwargs):

        """
        Get the center of mass of a term's KDE as a ratio.

        :param term: A stemmed term.
        """

        kde = self.kde(term, **kwargs)
        com = ndimage.measurements.center_of_mass(kde)
        return com[0] / len(kde)


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
