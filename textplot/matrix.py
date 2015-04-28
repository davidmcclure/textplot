

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
        return self.pairs[key]


class TextMatrix(Matrix):


    def index(self, text, terms=None):

        """
        Index all term pair distances.

        Args:
            text (Text): The source text.
            terms (list): Terms to index.
        """

        pass


    def anchored_pairs(self, anchor):

        """
        Get distances between an anchor term and all other terms.

        Args:
            anchor (str): The anchor term.

        Returns:
            OrderedDict: The distances, in descending order.
        """

        pass
