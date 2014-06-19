

import re
import textplot.utils as utils
import requests

from nltk.stem import PorterStemmer
from collections import OrderedDict
from itertools import islice
from random import shuffle


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
        self.tokenize()


    def tokenize(self):

        """
        Tokenize the text.
        """

        self.tokens = []
        self.terms = OrderedDict()

        # Strip tags and downcase.
        text = utils.strip_tags(self.text).lower()

        pattern = re.compile('[a-z]+')
        porter = PorterStemmer()

        # Iterate over tokens in the text.
        for match in re.finditer(pattern, text):

            # Stem the token.
            stemmed = porter.stem(match.group(0))

            # Index the token.
            self.tokens.append(stemmed)
            self.terms[stemmed] = True


    def slide_window(self, width=100):

        """
        Yield a sliding window across the text.
        """

        iterator = iter(self.tokens)
        result = tuple(islice(iterator, width))

        if len(result) == width:
            yield result

        for word in iterator:
            result = result[1:] + (word,)
            yield result


    def get_shuffled_terms(self):

        """
        Get a list of terms in randomized order.
        """

        terms = self.terms.keys()
        shuffle(terms)

        return terms
