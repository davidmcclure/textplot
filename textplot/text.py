

import requests
import re
import matplotlib.pyplot as plt
import numpy as np
import redis
import utils

from nltk.stem import PorterStemmer
from collections import OrderedDict, Counter
from sklearn.neighbors import KernelDensity
from scipy.misc import comb
from itertools import combinations
from clint.textui import progress


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

        # Redis connection and pipeline.
        self.redis = redis.StrictRedis(**kwargs)
        self.pipeline = self.redis.pipeline()

        # Porter stemmer.
        self.stem = PorterStemmer().stem


    @property
    def wordcount_key(self):

        """
        Redis key for the word counter.
        """

        return self.slug+':wordcount'


    def inc_wordcount(self):

        """
        Increment the wordcount.
        """

        self.pipeline.incr(self.wordcount_key)


    @utils.memoize
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


    @utils.memoize
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


    def set_term(self, term):

        """
        Register the existence of a term.

        :param term: A stemmed term.
        """

        self.pipeline.sadd(self.terms_key, term)


    @utils.memoize
    @property
    def terms(self):

        """
        Get the set of unique terms.
        """

        return self.redis.smembers(self.terms_key)


    @utils.memoize
    def has_term(self, term):

        """
        Does the text contain a term?

        :param term: A stemmed term.
        """

        return self.redis.sismember(self.terms_key, term)


    def token_key(self, offset):

        """
        Redis key for a token at a given offset.

        :param offset: An integer offset.
        """

        return self.slug+':token:'+str(offset)


    def set_token(self, offset, token):

        """
        Index a token.

        :param offset: The integer offset of the token.
        :param token: The token dictionary.
        """

        self.pipeline.hmset(self.token_key(offset), token)


    @utils.memoize
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


    def set_offset(self, offset, term):

        """
        Register a term instance offset.

        :param offset: The integer offset of the instance.
        :param term: The stemmed term.
        """

        self.pipeline.sadd(self.offsets_key(term), offset)


    @utils.memoize
    def offsets(self, term):

        """
        Get the offsets for a term as a sorted list of integers.

        :param term: A stemmed term.
        """

        offsets = self.redis.smembers(self.offsets_key(term))
        return sorted(list(map(int, offsets)))


    def distance_key(self, term1, term2):

        """
        Redis key for the density distance between tero terms.

        :param term1: The first term.
        :param term2: The second term.
        """

        terms = '_'.join(sorted((term1, term2)))
        return self.slug+':distance:'+terms


    def set_distance(self, term1, term2):

        """
        Set the density distance between tero terms.

        :param term1: The first term.
        :param term2: The second term.
        """

        k = self.distance_key(term1, term2)
        d = self.distance_between_terms(term1, term2)
        self.pipeline.set(k, d)


    @utils.memoize
    def distance(self, term1, term2):

        """
        Get the density distance between tero terms.

        :param term1: The first term.
        :param term2: The second term.
        """

        k = self.distance_key(term1, term2)
        return float(self.redis.get(k))


    def index(self, text):

        """
        Tokenize the text.

        :param text: The text, as a raw string.
        """

        # Store the original text
        self.pipeline.set(self.text_key, text)

        # Index tokens, terms, and wordcount.
        for i, token in enumerate(utils.tokenize(text)):
            term = token['stemmed']
            self.set_token(i, token)
            self.set_term(term)
            self.set_offset(i, term)
            self.inc_wordcount()

        self.pipeline.execute()


    def index_distances(self, batch_size=10000, **kwargs):

        """
        Index all pair distances.

        :param batch_size: Number of values to push to Redis at once.
        """

        expected = comb(len(self.terms), 2)
        with progress.Bar(expected_size=expected) as bar:

            i = 0
            for t1, t2 in combinations(self.terms, 2):

                self.set_distance(t1, t2)

                # Sync Redis.
                i += 1
                if i % batch_size == 0:
                    self.pipeline.execute()
                    bar.show(i)


    def clear(self):

        """
        Clear the key namespaces for the text.
        """

        keys = self.redis.keys(self.slug+':*')
        if keys: self.redis.delete(*keys)


    @utils.memoize
    def instance_count(self, term):

        """
        How many times does a given term appear in the text?

        :param term: A stemmed term.
        """

        return len(self.offsets(term))


    @utils.memoize
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


    @utils.memoize
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

        # Get the offsets of the term instances.
        offsets = np.array(self.offsets(term))[:, np.newaxis]

        # If no instances, return an array of 0's.
        if offsets.size == 0: return np.zeros(samples)

        # Fit the density estimator on the offsets.
        kde = KernelDensity(kernel=kernel, bandwidth=bandwidth).fit(offsets)

        # Estimate the density.
        samples = np.linspace(0, self.wordcount, samples)[:, np.newaxis]
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

        # How much space between samples?.
        spacing = float(self.wordcount) / t1_kde.size

        # Integrate overlap between the two.
        overlap = np.minimum(t1_kde, t2_kde)
        return np.trapz(overlap, dx=spacing)


    @utils.memoize
    def query(self, query, **kwargs):

        """
        Given a query text as a raw string, sum the kernel density estimates
        of each of the tokens in the query.

        :param query: The query string.
        """

        signals = []

        for t in utils.tokenize(query):
            signals.append(self.kde(t['stemmed'], **kwargs))

        result = np.zeros(signals[0].size)
        for signal in signals: result += signal

        return result


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


    def plot_query(self, query, **kwargs):

        """
        Plot a query result.

        :param query: The query string.
        """

        result = self.query(query, **kwargs)
        plt.plot(result)
        plt.show()
