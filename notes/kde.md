### Mapping texts with kernel density estimation

Earlier in the summer, I was thinking about the way that words _distribute_ inside of long texts - the way they slosh around, ebb and flow, clump together in some parts but not others. Some words don't really do this at all - they're spaced evenly throughout the document, and their distribution doesn't say much about the overall structure of the text. This is certainly true for stopwords like "the" or "an," but it's also true for lots of words that carry more semantic information but aren't really associated with any particular content matter. For example, think of words like "quickly" or "never" - they're generic terms, free-agents that could be used in almost any context.

Other words, though, have a really strong semantic focus - they occur unevenly, and they tend to hang together with other words that orbit around a shared topic. For example, think of a long novel like _War and Peace_, which contains dozens of different conceptual threads - plot lines, characters, scenes, themes, motifs, etc. There are battles, dances, hunts, meals, duels, salons, parlors, and so on and so forth - and, in the broadest sense, the "war" sections and the "peace" sections. Some words are really closely associated with some of these topics but not others. If you open to a random page and see words like "Natasha," "dancing," "family," "marry," or "children," it's a pretty good bet that you're in a peace-y section. But if you see words like "Napoleon," "Borodino," "horse," "fire," "cannon," or "guns," it's probably a war section. Or, at a more granular level, if you see words like "historian" or "clock" or "inevitable," there's a good chance it's one of those pesky historiographic essays.

To borrow Franco Moretti's term, I was looking for a way to "operationalize" these distributions - a standardized way to generate some kind of profile that would capture the structure of the locations of a term inside a document, ideally in a way that it would be possible to compare it with with the distributions of other words. I started poking around, and quickly discovered that if you know anything about statistics (I really don't, so take all of this with a grain of salt), there's a really simple and obvious way to do this - a kernel density estimate, which takes an observed set of data points and works backward to approximate a probabilty density function that, if you sampled it the same number of times, would produce more or less the same set of data.

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

This, then, points to a interesting next step - for any given word, you can just compute its similarity score with _every other word in the text_, and then sort the results in descending order to create a kind of "more-like-this" list. For example, here are the twenty words that distribute most closely with "horse," all clearly related to riding, firing, shouting, and other war-making activities:

[fig]

Or, at the other end of the spectrum, "Natasha" sits atop an immeditely-recogniziable stack of words related to family, women, joy, and youth:

[fig]

By skimming off the strongest links at the top of the stack, you end up with a little bespoke "topic" for the word, a community of siblings that intuitively hang together. This makes a lot of sense - the density functions just capture

#### Twisty little passages

the neat thing about this, though, is that this procedure creates a kind of implicit lattice of terms that binds the entire text together into a scrambled, dense network of relations. for example, once you've computed the sibling community for "horse," you can then do the same thing for any of the other words in the stack. if you take the second word, for example, and compute _its_ sibling community, you'll see many of the same words again, of course - by a kind of commutative property, words that were similar to "horse" will also be similar to "rode," since "rode" was similar to "horse" - but, since the distribution profile for "rode" is subtly different, other terms will start to creep into view. each time you do this, the semantic field will shift to center most closely on the anchoring word at the top of the stack. and as you do this again and again, you find that you start to traverse into completely different domains of meaning in the text. the war terms of the "horse" community can be followed into a cluster of terms about the body - no doubt, in the context of the war sections, related to _injury_ - which, in turn, can be used as a bridge to gain access to other body-related words like "face" and "lips," which finally give access to the prototypically peace-y threads in the text. each sibling community is like a room in a massive maze, and each of the words is like a door that leads into an adjacent room that occupies a very similar but slightly different place in the overall topic-blueprint of the text.

this fascinates me because it _de-linearizes_ the text - which, I think, is truer to the form it takes when it's executed in the mind of a reader. texts are one-dimensional lines, but - at the risk of generalizing, since this drifts into a subjective phenomenology of readng - we don't _think_ of texts as lines, or at least not _just_ as lines. we think of them as landscapes, regions, graphs, _maps_ - clusters of characters, scenes, ideas, emotional valences, color palettes, etc. the text scrolls by on a one-dimensional track, but we're constantly clipping things out and arranging them onto a heavily curated, continuously revised congnitive pinboard. notions of "proximity" or "closeness" become divorced from the literal, X-axis positions of things in the document. for example, in _War and Peace_, I think of the battles at Borodino and Austerliz as being very "close" to one another, in the sense that they're two of a kind, the two major military set pieces in the plot. even though they're actually separated by about 300,000 words:

[fig]

the similarity communities operationalize these implicit proximities, the path through the semantic web of the text that connects things like Borodino and Austerliz.

in a sense, then, the game of hopscotching through the word similarity communities might jibe more closely with the way that we _encode_ texts than going back and re-reading some section of the actual text.



when texts are actually instantiated by readers, they take the form of non-linear graphs or networks, cognitive atlases that map out the literary world encoded in the document. in a sense, then, the "maze" of interconnected topic threads surfaced by the





the text scrolls by on a one-dimensional track, but we're constantly clipping things out and arranging them onto a heavily curated, continuously revised mental pinboard.




as we read, we clip things out and post them onto heavily curated, continuously revised mental pinboards.

a tableau of little fragments of imagined scenes, which get clustered together and shaded by a mix of associations and emotional valences - delight, annoyance, interest, boredom





what you really want, though, is to be able to zoom back and see the entire blueprint at once. this fascinates me because it seems

this is neat, because it seems to formalize the little cognitive atlases that we construct when we read. this drifts into a kind of subjective phenomenology of reading, but

but - at the risk of generalizing, since this drifts into a subjective phenomenology of reading - we don't _think_ of texts as lines, or at least not _just_ as lines. we think of them as graphs, landscapes, regions, _maps_ - as we read, we pluck off little bits of information and pin them onto heavily curated, continuously revised mental pinboards.


the raw material of the text - the

two-dimensional map that organizes and represent the little literary world encoded in the document.

in memory, _War and Peace_ isn't an X-axis - it's a tableau of scenes, rendered in imagination, and laid out onto a kind of cognitive atlas.





the text scrolls past on a one-dimensional axis, but as we read we pluck things off and arrange them into conceptual spl

what you really want, though, is to be able to zoom back and wrap your head around the entire thing in a single glance - a god's eye view of the entire lattice of word-rooms, the original blueprint that captures the underlying topic structure of the document.

the war terms of the "horse" community be followed into a cluster of terms about the body (no doubt related to

hopscotch along the conceptual contiguities
each sibling community is like a single room in a massive maze, and each of the words is like a door that leads into an adjacent room

it's a way to operationalize the cognitive atlases that we construct when we
read, the schematic tableau that pulls things off of the one-dimensional axis of
the actual text as we encounter it and groups them together into related
clusters of meaning.

what you really want, though, is to be able to zoom back and see the entire maze in a single glance - the blueprint for the entire thing, the

this is a perfect task for network analysis - each of the words is a node, and each of the pairs in the sibling-communities is a weighted edge.

the basic idea here - converting a text into a network - is an old one.

in the past, though, network analysis of texts has focused more on surfacing more traditional, narrowly-understood notions of colocation - for example, illustrating the connections between words that appear together within a 2- or 5-word radius in the text. the cool thing about using the kernel density estimates as the underlying statistic is that the conventional layout algorithms produce




the organizing dialectics of texts - in
