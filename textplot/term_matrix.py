

from collections import OrderedDict


class TermMatrix(object):


    def __init__(self):

        """
        Initialize the elements dictionary.
        """

        self.elements = OrderedDict()


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
        self.elements[key] = value


    def get_pair(self, term1, term2):

        """
        Get the value for a pair of terms.

        :param term1: The first term.
        :param term2: The second term.
        """

        key = self.key_from_terms(term1, term2)
        return self.elements[key]
