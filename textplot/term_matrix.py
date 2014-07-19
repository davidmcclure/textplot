

import json
import utils

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

                # Update bar.
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
        return cls(serialized['terms'], serialized['distances'])


    def __init__(self, terms, distances=None):

        """
        Set or initialize the term set and distances dictionary.

        :param terms: A set of terms.
        :param distances: A dict of pair-key -> distance.
        """

        self.distances = distances or {}
        self.terms = terms


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
        self.distances[key] = value


    def get_pair(self, term1, term2):

        """
        Get the value for a pair of terms.

        :param term1: The first term.
        :param term2: The second term.
        """

        key = self.key_from_terms(term1, term2)
        return self.distances[key]


    def marshall(self, path):

        """
        Save the matrix as JSON.

        :param path: The file location.
        """

        matrix = {
            'terms': self.terms,
            'distances': self.distances
        }

        with open(path, 'w') as out:
            json.dump(matrix, out)


    @utils.memoize
    def all_distances_from_term(self, anchor, sort=True):

        """
        Given a term, get the distances for all other words.

        :param anchor: The anchor term.
        :param sort: If true, sort the dictionary by value.
        """

        distances = OrderedDict()
        for term in self.terms:
            distances[term] = self.get_pair(anchor, term)

        if sort: distances = utils.sort_dict(distances)
        return distances


    def top_distances_per_term(self, depth=20):

        """
        For each term, yield the X "nearest" edges as 3-tuples.

        :param depth: The number of edges to skim.
        """

        for term in terms:
            top = self.all_distances_from_term(term).items()[:depth]
            for edge in top:
                yield (term, edge[0], edge[1])
