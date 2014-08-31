### Using kernel density estimation to create network visualizations of texts

Earlier in the summer, I was thinking about the distribution of words inside of long texts - the way they slosh around, ebb and flow, clump together in some parts but not others. Some words don't really do this at all - they're spaced evenly throughout the document, and their distribution doesn't say much about the overall structure of the text. This is certainly true for stopwords like "the" or "an," but it's also true for lots of words that carry more semantic information but aren't really associated with any particular content matter. For example, think of words like "quickly" or "never" - they're generic terms, free-agents that could be used in almost any context.

Other words, though, have a really strong semantic focus - they occur unevenly, and they tend to hang together with other words that orbit around a shared topic. For example, think of a long novel like _War and Peace_, which contains dozens of different conceptual threads - plot lines, characters, scenes, themes, motifs, etc. There are battles, dances, hunts, meals, duels, salons, parlors, and so on and so forth - and, in the broadest sense, the "war" sections and the "peace" sections. Some words are really closely associated with some of these topics but not others. If you open to a random page and see words like "Natasha," "dancing," "family," "marry," or "children," it's a pretty good bet that you're in a peace-y section. But if you see words like "Napoleon," "Borodino," "horse," "fire," "cannon," or "guns," it's probably a war section. Or, at a more granular level, if you see words like "historian" or "clock" or "inevitable," there's a good chance it's one of those pesky historiographic essays.

To borrow Franco Moretti's term, I was looking for a way to "operationalize" these distributions - a standardized way to generate some kind of profile that would capture the structure of the locations of a term inside a document, ideally in a way that it would be possible to compare it with with the distributions of other words. I started poking around, and quickly discovered that if you know anything about statistics (I really don't, so take all of this with a grain of salt), there's a really simple and obvious way to do this - a kernel density estimate, which takes an observed set of data points and works backward to approximate a probabilty density function that, if you sampled it the same number of times, would produce more or less the same set of data.

Kernel density estimation (KDE) is really simple - unlike the math behind something like topic modeling, which gets complicated pretty fast, KDE is basically just simple arithmetic. Think of the text as a big X-axis, where each integer corresponds to a word position in the text. So, for _War and Peace_, the text would stretch from the origin to the X-axis offset of 573,064, the number of words in the text. Then, any word in the text can be plotted just by laying down ticks on the X-axis at all the offsets where the word shows up in the text. For example, here's "horse" in _War and Peace_:

[fig]

This can be converted into a histogram by chopping up the X-axis into a set of evenly-spaced bins and drawing a bar up to a value on the Y-axis that representis the number of data points that fall inside that segement:

[fig]

A kernel density estimate is the same idea, except, instead of just counting up the points, each point is represented as a "kernel" function centered around that point. A kernel is just some kind of weighting function that models a decay in intensity around the data point. At the very simplest, it could be something like the triangular kernel, which just draws a pair of straight, angled lines down to the X-axis, but most applications use something smooth and gradual, like the Epanechnikov or Gaussian functions. I'm sure there are intelligent reasons for why you might prefer one over another, but, for the purposes of this project, they all give basically the same results.

[fig]

The important thing, though, is that the kernel transforms the point into a _range_ or _interval_ of significance, instead of just a dimensionless dot. This is cool because it maps realy well onto basic intuitions about the "scope" of a word in a text. When you come across a word, _where_ exactly does it have significance? Definitely right there, at the exact location where it appears, but not _just_ there - it also makes sense to think of a kind of "relevance" or "meaning energy" that dissipates around the word, slowly at first across the immediately surrounding words and then more quickly as the distance increases. Words aren't self-contained little atoms of information - they radiate meaning forward and backward onto one another, both at a grammatical level inside the sentence but also in a more literary, phenomenological sense at the register of an actual reading experience. As you slide your eyes across a text, each word carries a kind of pyschological energy that spikes highest at the moment that you actually encounter it. But that energy doesn't instantly materialize and then vanish - the word casts a shadow of meaning onto the words that follow it, and it also exerts an energy backwards in memory that revises the words that come before it. The kernel is a simple way to formalize this "meaning-shape" of a word as it appears to the psychological gaze of the reader, the region illuminated as the spotlight of attention sweeps across the text.

Anyway, once the all of the kernels are in place, estimating the probability density is just a matter of stepping through each position on the X-axis and adding up the values of all the kernel functions at that particular location. This gives a single, composite curve that captures the overall distributon of the term in the document. Here's "horse" again:

[fig]

This makes it possible to visually confirm of deny the earlier intuitions about words that tend to hang together in a text. Here's the peace-y cluster from above:

[fig]

And the war-y cluster:

[fig]

And all together, which teases out the basic contours of the two general categories:

[fig]

#### "More like this"

These are fun to look at, but the real payoff here is that the kernel density estimates make it easy to compute a really precise, high-resolution "similarity" score that measures the extent to which any two words appear in the same locations in the text. Since the kernel density estimates are just plain old probability density functions, we can use any one of the many statistical tests that measure the closeness of two distributions. There are literally dozens of ways to do this (see this paper for a really good survey of the options), but one of the simplest and most computationally efficient approaches is just to measure the size of the geometric "overlap" between the two distributions - for each sample point on the X-axis, take the smaller of the two corresponding Y-axis values in the two distributions. Then, take the discrete integral of the resulting area:

[fig]

Which gives a score between 0 and 1, where 0 would mean that the two words appear in completely different parts of the document, and 1 would mean that the words appear in _exactly_ the same places. So, for example, if you score a word against itself:

[fig]

The result is 1 (or, at least, it would be if we could compute a continuous integral), since, tautologically, a word occurs exactly where it does. And, for two words that clump in very different places, the result edges towards 0:

[fig]

More interestingly, though, we can precisely quantify the extent to which any two words hang together in the text. How similar is "horse" to "cannon"?

[fig]

Which puts "horse" just a tad closer than "shout," which weighs in at 0.XX:

[fig]

This, then, makes it possible to compute a ranked "more-like-this-list" for any given word - just iterate over all the other words in the text, compute the similarity score, and then sort the results. For example, here are the ten words that distribute most closely with "horse" (again, obiviously, "horse" itself is the _most_ similar):

[fig]

Or "Natasha":

[fig]

Which, intuitively, look right - the similarity metric surfaces a kind of bespoke "topic" for an individual word, a custom ordering from most similar to least similar.

#### Traversing the topic structure
