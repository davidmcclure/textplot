

import numpy as np
import textplot.utils as utils

from itertools import combinations
from clint.textui.progress import bar
from scipy.misc import comb
from collections import OrderedDict


class Matrix:


    def __init__(self):

        """
        Initialize the underlying dictionary.
        """

        self.clear()


    def clear(self):

        """
        Reset the pair mappings and key set.
        """

        self.keys = set()
        self.pairs = {}


    def key(self, term1, term2):

        """
        Get an order-independent key for a pair of terms.

        Args:
            term1 (str)
            term2 (str)

        Returns:
            str: The dictionary key.
        """

        return '_'.join(sorted((term1, term2)))


    def set_pair(self, term1, term2, value, **kwargs):

        """
        Set the value for a pair of terms.

        Args:
            term1 (str)
            term2 (str)
            value (mixed)
        """

        key = self.key(term1, term2)
        self.keys.update([term1, term2])
        self.pairs[key] = value


    def get_pair(self, term1, term2):

        """
        Get the value for a pair of terms.

        Args:
            term1 (str)
            term2 (str)

        Returns:
            The stored value.
        """

        key = self.key(term1, term2)
        return self.pairs.get(key, None)


    def index(self, text, terms=None, **kwargs):

        """
        Index all term pair distances.

        Args:
            text (Text): The source text.
            terms (list): Terms to index.
        """

        self.clear()

        # By default, use all terms.
        terms = terms or text.terms.keys()

        pairs = combinations(terms, 2)
        count = comb(len(terms), 2)

        for t1, t2 in bar(pairs, expected_size=count, every=1000):

            # Set the Bray-Curtis distance.
            score = text.score_braycurtis(t1, t2, **kwargs)
            self.set_pair(t1, t2, score)


    def anchored_pairs(self, anchor):

        """
        Get distances between an anchor term and all other terms.

        Args:
            anchor (str): The anchor term.

        Returns:
            OrderedDict: The distances, in descending order.
        """

        pairs = OrderedDict()

        for term in self.keys:
            score = self.get_pair(anchor, term)
            if score: pairs[term] = score

        return utils.sort_dict(pairs)
