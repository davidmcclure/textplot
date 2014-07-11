

import re
import textplot.utils as utils
import requests
import numpy as np

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
        self.stem = PorterStemmer().stem
        self.tokenize()


    def tokenize(self):

        """
        Tokenize the text.
        """

        self.tokens = []
        self.terms = OrderedDict()

        # Strip tags and downcase.
        text = utils.strip_tags(self.text).lower()

        # Walk words in the text.
        pattern = re.compile('[a-z]+')
        for i, match in enumerate(re.finditer(pattern, text)):

            # Stem the token.
            token = match.group(0)
            stemmed = self.stem(token)

            # Token:
            self.tokens.append({
                'token':    token,
                'stemmed':  stemmed,
                'left':     match.start(),
                'right':    match.end()
            })

            # Token -> offset:
            if stemmed in self.terms: self.terms[stemmed].append(i)
            else: self.terms[stemmed] = [i]


    def get_count_difference(self, word1, word2):

        """
        What is the difference between the number of instances of two words?

        :param word1: The first word.
        :param word2: The other word.
        """

        return abs(len(self.terms[word1]) - len(self.terms[word2]))


    def get_similarity(self, anchor, sample):

        """
        Given an "anchor" word, compute a similarity metric for another word.

        :param anchor: The word to compare against.
        :param sample: The word being compared.
        """

        distances = []

        anchor_offsets = np.array(self.terms[anchor])
        sample_offsets = np.array(self.terms[sample])

        for offset in anchor_offsets:

            # Get the closest instance of the sample.
            cidx = np.abs(sample_offsets - offset).argmin()

            # Get the distance between the two.
            distance = abs(sample_offsets[cidx] - offset)
            distances.append(distance)

        return np.mean(np.array(distances))


    def get_similarities(self, anchor):

        """
        Given an "anchor" word, compute a sorted list of similarities for all
        other terms in the text.

        :param anchor: The word to compare against.
        """

        sims = []
        anchor = self.stem(anchor)

        for term in self.terms:
            if self.get_count_difference(anchor, term) < 500:
                sims.append((term, self.get_similarity(term, anchor)))

        sims.sort(key=lambda s: s[1])
        return sims
