

import requests
import re
import matplotlib.pyplot as plt
import numpy as np
import redis
import utils

from nltk.stem import PorterStemmer
from collections import OrderedDict, Counter
from sklearn.neighbors import KernelDensity
from itertools import combinations


class Text(object):


    @classmethod
    def from_file(cls, path, slug, **kwargs):

        """
        Create a text from a filepath.

        :param path: The filepath.
        :param slug: A Redis key prefix.
        """

        # Clear the namespace.
        text = cls(slug, **kwargs)
        text.clear()

        # Index the text.
        text.index(open(path, 'r').read())
        return text


    def __init__(self, slug, **kwargs):

        """
        Set the key prefix, connect to Redis.

        :param slug: A Redis key prefix.
        """

        self.slug = slug

        # Redis connection.
        self.redis = redis.StrictRedis(**kwargs)

        # Porter stemmer.
        self.stem = PorterStemmer().stem


    @property
    def wordcount_key(self):

        """
        Redis key for the word counter.
        """

        return self.slug+':wordcount'


    @property
    def wordcount(self):

        """
        How many words are in the text?
        """

        return int(self.redis.get(self.wordcount_key))


    @property
    def text_key(self):

        """
        Redis key for the raw text string.
        """

        return self.slug+':text'


    @property
    def text(self):

        """
        Get the raw text string.
        """

        return self.redis.get(self.text_key)


    @property
    def terms_key(self):

        """
        Redis key for the set of unique terms.
        """

        return self.slug+':terms'


    @property
    def terms(self):

        """
        Get the set of unique terms.
        """

        return self.redis.smembers(self.terms_key)


    def token_key(self, offset):

        """
        Redis key for a token at a given offset.

        :param offset: An integer offset.
        """

        return self.slug+':token:'+str(offset)


    def token(self, offset):

        """
        Get the hash for a token at a given offset, casting the start and end
        character offsets to integers.

        :param offset: An integer offset.
        """

        token = self.redis.hgetall(self.token_key(offset))
        return utils.numberify_dict(token)


    def offsets_key(self, term):

        """
        Redis key for the set of term offsets.

        :param term: A stemmed term.
        """

        return self.slug+':offsets:'+term


    def offsets(self, term):

        """
        Get the offsets for a term as a sorted list of integers.

        :param term: A stemmed term.
        """

        offsets = self.redis.smembers(self.offsets_key(term))
        return sorted(list(map(int, offsets)))


    def index(self, text):

        """
        Tokenize the text.

        :param text: The text, as a raw string.
        """

        pipe = self.redis.pipeline()

        # Store the original text
        pipe.set(self.text_key, text)

        # Generate and index tokens.
        for i, token in enumerate(utils.tokenize(text)):

            term = token['stemmed']

            # Token
            pipe.hmset(self.token_key(i), token)

            # Term
            pipe.sadd(self.terms_key, term)

            # Term -> offset
            pipe.sadd(self.offsets_key(term), i)

            # Wordcount++
            pipe.incr(self.wordcount_key)

        pipe.execute()


    def clear(self):

        """
        Clear the key namespaces for the text.
        """

        keys = self.redis.keys(self.slug+':*')
        if keys: self.redis.delete(*keys)


    def instance_count(self, term):

        """
        How many times does a given term appear in the text?

        :param term: A stemmed term.
        """

        return len(self.offsets(term))


    def term_counts(self, sort=True):

        """
        Map terms to instance counts.

        :param sort: If true, sort the dictionary by value.
        """

        counts = OrderedDict()
        for term in self.terms:
            counts[term] = self.instance_count(term)

        if sort: counts = utils.sort_dict(counts)
        return counts


    def unstem(self, term):

        """
        Given a stemmed term, get the most common unstemmed variant.

        :param term: A stemmed term.
        """

        originals = []
        for i in self.offsets(term):
            originals.append(self.token(i)['unstemmed'])

        mode = Counter(originals).most_common(1)
        return mode[0][0]


    @utils.memoize
    def kde(self, term, bandwidth=5000, samples=1000, kernel='epanechnikov'):

        """
        Estimate the kernel density of the instances of term in the text.

        :param term: The term to estimate.
        :param bandwidth: The kernel width.
        :param samples: The number points to sample.
        :param kernel: The kernel function.
        """

        # Term offsets and density sample axis:
        offsets = np.array(self.offsets(term))[:, np.newaxis]
        samples = np.linspace(0, self.wordcount, samples)[:, np.newaxis]

        # Density estimator:
        kde = KernelDensity(kernel=kernel, bandwidth=bandwidth).fit(offsets)

        # Estimate the kernel density.
        return np.exp(kde.score_samples(samples))


    @utils.memoize
    def distance_between_terms(self, term1, term2, **kwargs):

        """
        How much do the kernel density estimates of two terms overlap?

        :param term1: The first term.
        :param term2: The second term.
        """

        t1_kde = self.kde(term1, **kwargs)
        t2_kde = self.kde(term2, **kwargs)

        # Get the spacing between samples.
        spacing = float(self.wordcount) / t1_kde.size

        # Integrate overlap between the two.
        overlap = np.minimum(t1_kde, t2_kde)
        return np.trapz(overlap, dx=spacing)


    #@utils.memoize
    #def query(self, query, **kwargs):

        #"""
        #Given a query text as a raw string, sum the kernel density estimates
        #of each of the tokens in the query.

        #:param query: The query string.
        #"""

        #query_text = Text(query)
        #signals = []

        #for term in query_text.terms:
            #if term in self.terms:
                #signals.append(self.kde(term, **kwargs))

        #result = np.zeros(signals[0].size)
        #for signal in signals: result += signal

        #return result


    def plot_term_kdes(self, words, **kwargs):

        """
        Plot kernel density estimates for multiple words.

        :param words: The words to query.
        :param bandwidth: The kernel width.
        """

        for word in words:
            kde = self.kde(self.stem(word), **kwargs)
            plt.plot(kde)

        plt.show()


    #def plot_query(self, query, **kwargs):

        #"""
        #Plot a query result.

        #:param query: The query string.
        #"""

        #result = self.query(query, **kwargs)
        #plt.plot(result)
        #plt.show()
