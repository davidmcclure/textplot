

from scipy.misc import comb
from collections import OrderedDict
from clint.textui import progress
from itertools import combinations


class TermMatrix(object):


    @classmethod
    def from_text(cls, text, **kwargs):

        """
        Populate a term matrix from a text instance.

        :param cls: TermMatrix.
        :param path: The text.
        """

        matrix = cls()
        number = comb(len(text.terms), 2)

        # Get a progress bar.
        with progress.Bar(expected_size=number) as bar:

            i = 0
            for t1, t2 in combinations(text.terms, 2):

                # Compute the term distance.
                distance = text.distance_between_terms(t1, t2, **kwargs)
                matrix.set_pair(t1, t2, distance)

                # Update bar
                i += 1
                if i % 1000 == 0: bar.show(i)

        return matrix


    def __init__(self, terms=None, pairs=None):

        """
        Set or initialize the term set and pairs dictionary.

        :param terms: A set of terms.
        :param pairs: A dict of pair-key -> value.
        """

        self.pairs = pairs or OrderedDict()
        self.terms = terms or set()


    def key_from_terms(self, term1, term2):

        """
        Get a unique key for a term pair.

        :param term1: The first term.
        :param term2: The second term.
        """

        return '_'.join(sorted((term1, term2)))


    def set_pair(self, term1, term2, value):

        """
        Set the value for a pair of terms.

        :param term1: The first term.
        :param term2: The second term.
        :param value: The value.
        """

        # Set the value.
        key = self.key_from_terms(term1, term2)
        self.pairs[key] = value

        # Track the terms.
        self.terms.add(term1)
        self.terms.add(term2)


    def get_pair(self, term1, term2):

        """
        Get the value for a pair of terms.

        :param term1: The first term.
        :param term2: The second term.
        """

        key = self.key_from_terms(term1, term2)
        return self.pairs[key]
