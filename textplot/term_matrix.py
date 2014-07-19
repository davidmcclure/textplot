

import json

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

        matrix = cls(text.terms.keys())
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


    @classmethod
    def from_json(cls, path):

        """
        Unmarshall a JSON file.

        :param cls: TermMatrix.
        :param path: The JSON file.
        """

        serialized = json.load(open(path, 'r'))
        return cls(serialized['terms'], serialized['pairs'])


    def __init__(self, terms, pairs=None):

        """
        Set or initialize the term set and pairs dictionary.

        :param terms: A set of terms.
        :param pairs: A dict of pair-key -> value.
        """

        self.terms = terms
        self.pairs = pairs or {}


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

        key = self.key_from_terms(term1, term2)
        self.pairs[key] = value


    def get_pair(self, term1, term2):

        """
        Get the value for a pair of terms.

        :param term1: The first term.
        :param term2: The second term.
        """

        key = self.key_from_terms(term1, term2)
        return self.pairs[key]


    def marshall(self, path):

        """
        Save the matrix as JSON.

        :param path: The file location.
        """

        matrix = {
            'terms': self.terms,
            'pairs': self.pairs
        }

        with open(fpath, 'w') as out:
            json.dump(matrix, out)
