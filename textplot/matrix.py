

import numpy as np
import utils

from clint.textui import progress
from itertools import combinations
from collections import OrderedDict
from scipy.misc import comb


class Matrix(object):


    def __init__(self, text):

        """
        Store the text.

        :param text: A text instance.
        """

        self.text = text


    def key(self, term1, term2):

        """
        Get a unique key for a term pair.

        :param term1: The first term.
        :param term2: The second term.
        """

        return '_'.join(sorted((term1, term2)))


    def set_pair(self, term1, term2, **kwargs):

        """
        Set the value for a pair of terms.

        :param term1: The first term.
        :param term2: The second term.
        """

        k = self.key(term1, term2)
        d = self.score(term1, term2, **kwargs)
        self.distances[k] = d


    def get_pair(self, term1, term2):

        """
        Get the value for a pair of terms.

        :param term1: The first term.
        :param term2: The second term.
        """

        k = self.key(term1, term2)
        if k in self.pairs: return self.pair[k]
        else: return None


    def score(self, term1, term2, **kwargs):

        """
        How much do the kernel density estimates of two terms overlap?

        :param term1: The first term.
        :param term2: The second term.
        """

        t1_kde = self.text.kde(term1, **kwargs)
        t2_kde = self.text.kde(term2, **kwargs)

        # Integrate the overlap.
        overlap = np.minimum(t1_kde, t2_kde)
        return np.trapz(overlap)


    def all_pairs(self, anchor, sort=True):

        """
        Compute the pairs between an anchor terms and all other terms.

        :param anchor: The anchor term.
        :param sort: If true, sort the dictionary by value.
        """

        pairs = OrderedDict()
        for term in self.terms:
            pairs[term] = self.get_pair(anchor, term)

        if sort: pairs = utils.sort_dict(pairs)
        return overlaps


    def index(self, terms=None, **kwargs):

        """
        Index all word pair distances.

        :param terms: A list of terms to index.
        """

        self.pairs = {}

        # Use all terms by default.
        self.terms = terms or self.text.terms.keys()
        pairs = comb(len(terms), 2)

        with progress.Bar(expected_size=pairs) as bar:

            i = 0
            for t1, t2 in combinations(self.terms, 2):

                self.set_pairs(t1, t2, **kwargs)

                # Update progress.
                i += 1
                if i % 1000 == 0: bar.show(i)
