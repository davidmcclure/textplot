

import requests
import re
import matplotlib.pyplot as plt
import numpy as np

from nltk.stem import PorterStemmer
from sklearn.neighbors import KernelDensity
from collections import OrderedDict
from textplot import utils


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
