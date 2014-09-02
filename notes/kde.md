### (Mental) maps of texts with kernel density estimation

Earlier in the summer, I was thinking about the way that words _distribute_ inside of long texts - the way they slosh around, ebb and flow, clump together in some parts but not others. Some words don't really do this at all - they're spaced evenly throughout the document, and their distribution doesn't say much about the overall structure of the text. This is certainly true for stopwords like "the" or "an," but it's also true for lots of words that carry more semantic information but aren't really associated with any particular content matter. For example, think of words like "quickly" or "never" - they're generic terms, free-agents that could be used in almost any context.

Other words, though, have a really strong semantic focus - they occur unevenly, and they tend to hang together with other words that orbit around a shared topic. For example, think of a long novel like _War and Peace_, which contains dozens of different conceptual threads - plot lines, characters, scenes, themes, motifs, etc. There are battles, dances, hunts, meals, duels, salons, parlors, and so on and so forth - and, in the broadest sense, the "war" sections and the "peace" sections. Some words are really closely associated with some of these topics but not others. If you open to a random page and see words like "Natasha," "dancing," "family," "marry," or "children," it's a pretty good bet that you're in a peace-y section. But if you see words like "Napoleon," "Borodino," "horse," "fire," "cannon," or "guns," it's probably a war section. Or, at a more granular level, if you see words like "historian" or "clock" or "inevitable," there's a good chance it's one of those pesky historiographic essays.

To borrow Franco Moretti's term, I was looking for a way to "operationalize" these distributions - a standardized way to generate some kind of profile that would capture the structure of the locations of a term inside a document, ideally in a way that would make it possible to compare it with with the distributions of other words. I started poking around, and quickly discovered that if you know anything about statistics (I really don't, so take all of this with a grain of salt), there's a really simple and obvious way to do this - a kernel density estimate, which takes an observed set of data points and works backward to approximate a probabilty density function that, if you sampled it the same number of times, would produce more or less the same set of data.

Kernel density estimation (KDE) is really simple - unlike the math behind something like topic modeling, which gets complicated pretty fast, KDE is basically just simple arithmetic. Think of the text as a big X-axis, where each integer corresponds to a word position in the text. So, for _War and Peace_, the text would stretch from the origin to the X-axis offset of 573,064, the number of words in the text. Then, any word in the text can be plotted just by laying down ticks on the X-axis at all the offsets where the word shows up in the text. For example, here's "horse" in _War and Peace_:

[fig]

This can be converted into a histogram by chopping up the X-axis into a set of evenly-spaced bins and drawing a bar up to a value on the Y-axis that representis the number of data points that fall inside that segement:

[fig]

A kernel density estimate is the same idea, except, instead of just counting up the points, each point is represented as a "kernel" function centered around that point. A kernel is just some kind of weighting function that models a decay in intensity around the data point. At the very simplest, it could be something like the triangular kernel, which just draws a pair of straight, angled lines down to the X-axis, but most applications use something smooth and gradual, like the Epanechnikov or Gaussian functions. For the purposes of this project, though, they all give basically the same results.

[fig]

The important thing, though, is that the kernel transforms the point into a _range_ or _interval_ of significance, instead of just a dimensionless dot. This is cool because it maps realy well onto basic intuitions about the "scope" of a word in a text. When you come across a word, _where_ exactly does it have significance? Definitely right there, at the exact location where it appears, but not _just_ there - it also makes sense to think of a kind of "relevance" or "meaning energy" that dissipates around the word, slowly at first across the immediately surrounding words and then more quickly as the distance increases. Words aren't self-contained little atoms of information - they radiate meaning forward and backward onto one another, both at a grammatical level inside the sentence but also in a more literary, phenomenological sense at the register of an actual reading experience. As you slide your eyes across a text, each word carries a kind of pyschological energy that spikes highest at the moment that you actually encounter it. But that energy doesn't instantly materialize and then vanish - the word casts a shadow of meaning onto the words that follow it, and it also exerts an energy backwards in memory that revises the words that come before it. The kernel is a simple way to formalize this "meaning-shape" of a word as it appears to the psychological gaze of the reader, the region illuminated as the spotlight of attention sweeps across the text.

Anyway, once the all of the kernels are in place, estimating the probability density is just a matter of stepping through each position on the X-axis and adding up the values of all the kernel functions at that particular location. This gives a single, composite curve that captures the overall distributon of the term in the document. Here's "horse" again:

[fig]

Or, we can bump up the "bandwidth," a free parameter that controls the width of the kernel function, the radius of the meaning energy around a word. Higher bandwidths cause more of the kernels to overlap with each other and layer up to produce smooth, schematic functions that capture the really high-level shape of the distribution:

[fig]

Lower bandwidths, meanwhile, produce more differentiated functions that capture more granular detail about how the word distributes in any given section of the document:

[fig]

In either case, the density estimates make it possible to visually confirm the earlier intuitions about the groups of words that tend to hang together in the text. Here's the peace-y cluster from above:

[fig]

And the war-y cluster:

[fig]

And all together, which teases out the basic contours of the two general categories:

[fig]

#### "More like this"

These are fun to look at, but the real payoff here is that the kernel density estimates make it easy to compute a really precise, high-resolution "similarity" score that measures the extent to which any two words appear in the same locations in the text. Since the resulting signal plots just plain old probability density functions, we can use any one of the many statistical tests that measure the closeness of two distributions. There are literally dozens of ways to do this (see this paper for a really good survey of the options), but one of the simplest and most computationally efficient approaches is just to measure the size of the geometric "overlap" between the two distributions - for each sample point on the X-axis, take the smaller of the two corresponding Y-axis values in the two distributions. Then, take the discrete integral of the resulting area:

[fig]

Which gives a score between 0 and 1, where 0 would mean that the two words appear in completely different parts of the document, and 1 would mean that the words appear in _exactly_ the same places. So, for example, if you score a word against itself:

[fig]

The result is 1 (or, at least, it would be if we could compute a continuous integral), since, tautologically, a word occurs exactly where it does. And, for two words that clump in very different places, the result edges towards 0:

[fig]

More interestingly, though, we can precisely quantify the extent to which any two words do, in fact, show up in the same places. How similar is "horse" to "cannon"?

[fig]

Which puts "horse" just a tad closer than "shout," which weighs in at 0.XX:

[fig]

This, then, points to a interesting next step - for any given word, you can compute its similarity score with _every other word in the text_, and then sort the results in descending order to create a kind of "more-like-this" list. For example, here are the twenty words that distribute most closely with "horse," all clearly related to riding, firing, shouting, and other war-ish activities:

[fig]

Or, at the other end of the spectrum, "Natasha" sits atop an immeditely-recogniziable stack of words related to family, women, joy, and youth:

[fig]

By skimming off the strongest links at the top of the stack, you end up with a little bespoke "distribution topic" for the word, a community of siblings that intuitively hang together. This makes a lot of sense - the density functions just capture

#### Twisty little passages

The neat thing about this, though, is that this procedure creates a kind of implicit lattice of terms that binds the entire text together into a scrambled, dense network of relations. For example, once you've computed the sibling community for "horse," you can then do the same thing for any of the other words in the stack. If you take the second word, for example - "rode" - and compute _its_ sibling community, you'll see many of the same words again, of course - by a kind of commutative property, words that were similar to "horse" will also be similar to "rode," since "rode" was similar to "horse". But, since the distribution profile for "rode" is subtly different, other terms will start to creep into view. Each time you do this, the semantic field will shift to center most closely on the anchoring word at the top of the stack. And as you do this again and again, you find that you start to traverse into completely different domains of meaning in the text. The war terms of the "horse" community can be followed into a cluster of terms about the body - no doubt, in the context of the war sections, related to _injury_ - which, in turn, can be used as a bridge to gain access to other body-related words like "face" and "lips," which finally give access to the prototypically peace-y threads in the text - "laugh," "smile," "dance," etc. Each sibling community is like a room in a massive maze, and each of the words is like a door that leads into an adjacent room that occupies a very similar but slightly different place in the overall topic-blueprint of the text.

This fascinates me because it _de-linearizes_ the text - which, I think, is truer to the form it takes when it's staged in the mind of a reader. Texts are one-dimensional lines, but - at the risk of generalizing, since this drifts into a subjective phenomenology of reading - we don't really think of texts as lines, or at least not _just_ as lines. We think of them as landscapes, regions, graphs, maps, diagrams, networks - clusters of characters, scenes, ideas, emotional valences, and color palettes, all set in relation to one another and wired up in lots of different ways. The text scrolls by on a one-dimensional track, but we're constantly clipping things out, shuffling them around, and arranging them onto a kind of congnitive pinboard, a mental map of the text as a little dimensional world instead of a linear axis of of words. Notions of "proximity" or "closeness" become divorced from the literal, X-axis positions of things in the document. In _War and Peace_, for example, I think of the battles at Borodino and Austerliz as being very "close" to one another, in the sense that they're the two major military set pieces in the plot. Even though they're actually separated by about 300,000 words, and their density distributions only have an overlap of ~0.11, meaning, essentially, that they _don't_ overlap with each other about 90% of the time:

[fig]

But, the conceptual closeness between the two can be teased out by actually constructing the implicit network that exists between all of the distribution topics, the "rooms" in the textual maze. This is easy - for each word in the text:

1. Compute the similarity between the word's probability density distribution and the distribution of every other word in the text.

1. Sort the list in descending order to get ranked stack of "distribution siblings," words that tend to show up in the same parts of the document.

1. Skim off the strongest links - say, the top 10 - and add them as nodes to a graph, and use the similarity score as the weight of the edge that connects them.

Now, with the whole scientific literature of graph-theoretic concepts available, the conceptual relationship between "austerlitz" and "borodino" falls out really easily - just use Dijkstra's algorithm to get the shortest path between the two, which, unsurprisingly, makes just a single hop through the word "battle":

`austerlitz -> battle -> borodino`

With a path length of XXX, which puts "austerlitz" closer to "borodino" than about **XX%** of all other words in the text, even though they only co-occur about 10% of the time.

### Text-ray

This is cool, but it's sort of like stumbling through one little twisty passage in the maze with a torch - what you really want is to be able to zoom back and see the whole structure at once, a blueprint that would organically surface the important regions and topics. Which, of course, is a perfect task job for any of the off-the-shelf network layout algorithms. Force Atlas 2 in Gephi works well - the algorithm thrashes around for a moment, and then unfolds into an equilibrium that tends to just _look like_ the text in remarkable ways. Here are the first few seconds of _War and Peace_:

[video]

And the final network:

[fig]

War to the left, peace to the right, and history on top. It's also striking the extent to which the war/peace opposition maps onto male female, although I guess that's not really surprising.

The _Odyssey_ is an opposition between near and far, land and sea - Ithaca, Penelope, and the suitors on the bottom, the "raft" at the very top, the thematic icon of distance, solitude, and vulnerability during the seeing and knowing the Aegean:

[fig]

_Walden_, occupies the same space between civilization and wilderness - at the bottom is the world of the town, of "people," "state," "tax," "comforts," and "government," and at the bery top the pure, impressionistic world of the pond - "lake," "boat," "shore," "surface," "reflected," "walden." This one fascinates me because of the remarkable conceptual cleanness of the gradient between the two - Concord fades into words that anchor that narrative about finding materials and building a house (Thoreau's purified version of Concord), which then gives way to the orbit of words around "day," the habits and rhythms of life in the woods, now far from the civilized world but still preoccupied with a human experience, which finally dissolves into the sub- or super-consciousness of the pond, which sits apart from

[fig]

The _Divine Comedy_, meanwhile, gives a tidy illustration of the universe - like _Walden_, a thin pillar of words running from hell at the bottom ("torment," "sad," and "wretched") to heaven at the top, with, fittingly enough, "christ" sitting on top of the whole affair:

[fig]

_Paradise Lost_ isn't quite as defined, but still resolves into an easily-recognizable triad - heaven on top, eden to the left, the war in heaven on the right, and hell on the bottom:

[fig]

_Notes from Undergound_ falls out into a pretty clean division between the two halves of the novella - the existentialist manifesto of the first fifty or so pages ("Underground"), and then the narratives with Zverkov and Liza in the second half:

[fig]





man/nature

bk


war and peace, ocean and land, near and far, heaven and hell, god and man,
civilization and wilderness
