

import re
import textplot.utils as utils
import requests

from nltk.stem import PorterStemmer
from collections import OrderedDict
from random import shuffle, randint
from itertools import islice


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
        for i, match in enumerate(re.finditer(pattern, text)):

            # Stem the token.
            stemmed = porter.stem(match.group(0))

            # Index the token.
            self.tokens.append(stemmed)

            # Index the term instance.
            if stemmed in self.terms: self.terms[stemmed].append(i)
            else: self.terms[stemmed] = [i]


    def slide_window(self, width=100):

        """
        Yield a sliding window across the text.

        :param width: The number of words in the window.
        """

        iterator = iter(self.tokens)
        result = tuple(islice(iterator, width))

        if len(result) == width:
            yield result

        for word in iterator:
            result = result[1:] + (word,)
            yield result


    def random_window(self, count, width=100):

        """
        Yield a random window.

        :param count: The number of windows to yield.
        :param width: The number of words in the window.
        """

        for i in xrange(count):
            start = randint(0, len(self.tokens) - count)
            yield self.tokens[start : start+count]


    def get_shuffled_terms(self):

        """
        Get a list of terms in randomized order.
        """

        terms = self.terms.keys()
        shuffle(terms)

        return terms
