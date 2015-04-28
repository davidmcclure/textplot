

import numpy as np
import textplot.utils as utils

from clint.textui import progress
from itertools import combinations
from collections import OrderedDict
from scipy.misc import comb


class Matrix:


    def __init__(self):

        """
        Initialize the underlying dictionary.
        """

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


class TextMatrix(Matrix):


    def index(self, text, terms=None, **kwargs):

        """
        Index all term pair distances.

        Args:
            text (Text): The source text.
            terms (list): Terms to index.
        """

        self.pairs = {}

        # By default, use all terms.
        self.terms = terms or text.terms.keys()

        for t1, t2 in combinations(self.terms, 2):

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

        for term in self.terms:
            score = self.get_pair(anchor, term)
            if score: pairs[term] = score

        return utils.sort_dict(pairs)
