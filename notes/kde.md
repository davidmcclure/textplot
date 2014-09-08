
## (Mental) maps of texts with kernel density estimation

Earlier in the summer, I was thinking about the way that words _distribute_ inside of long texts - the way they slosh around, ebb and flow, clump together in some parts but not others. Some words don't really do this at all - they're spaced evenly throughout the document, and their distribution doesn't say much about the overall structure of the text. This is certainly true for stopwords like "the" or "an," but it's also true for lots of words that carry more semantic information but aren't really associated with any particular content matter. For example, think of words like "quickly" or "put" - they're generic terms, free-agents that could be used in almost any context.

Other words, though, have a really strong semantic focus - they occur unevenly, and they tend to hang together with other words that orbit around a shared topic. For example, think of a long novel like _War and Peace_, which contains dozens of different conceptual threads - plot lines, characters, scenes, themes, motifs, etc. There are battles, dances, hunts, meals, duels, salons, parlors, and so on and so forth - and, in the broadest sense, the "war" sections and the "peace" sections. Some words are really closely associated with some of these topics but not others. If you open to a random page and see words like "Natasha," "dancing," "family," "marry," or "children," it's a pretty good bet that you're in a peace-y section. But if you see words like "Napoleon," "Borodino," "horse," "fire," "cannon," or "guns," it's probably a war section. Or, at a more granular level, if you see words like "historian" or "clock" or "inevitable," there's a good chance it's one of those pesky historiographic essays.

To borrow Franco Moretti's term, I was looking for a way to "operationalize" these distributions - a standardized way to generate some kind of lightweight, flexible statistic that would capture the structure of the locations of a term inside a document - ideally in a way that would make it easy to compare it with with the locations of other words. I started poking around, and quickly discovered that if you know anything about statistics (I really don't, so take all of this with a grain of salt), there's a really simple and obvious way to do this - a kernel density estimate, which takes a set of data points and works backward to approximate a probabilty density function that, if you sampled it the same number of times, would produce more or less the same set of data.

Kernel density estimation (KDE) is really easy to reason about - unlike the math behind something like topic modeling, which gets complicated pretty fast, KDE is basically just simple arithmetic. Think of the text as a big X-axis, where each integer corresponds to a word position in the text. So, for _War and Peace_, the text would stretch from the origin to the X-axis offset of 573,064, the number of words in the text. Then, any word in the text can be plotted just by laying down ticks on the X-axis at all the offsets where the word shows up in the text. For example, here's "horse" in _War and Peace_:

[fig]

One easy way to start to reason about this is to create a simple histogram, which projects the density of the points onto the Y-axis - chop up the X-axis into a set of evenly-spaced bins, and then draw bars up to the values on the Y-axis that represent the number of data points that fall within each segment:

[fig]

A kernel density estimate is the same idea, except, instead of just counting up the points, each point is represented as a "kernel" function centered around that point. A kernel is just some kind of weighting function that models a decay in intensity around the data point. At the very simplest, it could be something like the triangular kernel, which just draws a pair of straight, angled lines down to the X-axis, but most applications use something smooth and gradual, like the Epanechnikov or Gaussian functions. For the purposes of this project, though, they all give basically the same results.

[fig]

The important thing, though, is that the kernel transforms the point into a _range_ or _interval_ of significance, instead of just a dimensionless dot. This is cool because it maps realy well onto basic intuitions about the "scope" of a word in a text. When you come across a word, _where_ exactly does it have significance? Definitely right there, at the exact location where it appears, but not _just_ there - it also makes sense to think of a kind of "relevance" or "meaning energy" that dissipates around the word, slowly at first across the immediately surrounding words and then more quickly as the distance increases. Words aren't self-contained little atoms of information. As you slide your eyes across a text, each word carries a kind of pyschological energy that spikes highest at the moment that you actually encounter it. But that energy doesn't instantly materialize and then vanish - the word casts a shadow of meaning onto the words that follow it, and it also exerts an energy backwards in memory that revises the words that come before it. Words radiate meaning forward and backward onto one another. The kernel is a simple way to formalize this "meaning-shape" as it appears to the psychological gaze of the reader.

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

### "More like this"

These are fun to look at, but the real payoff is that the kernel density estimates make it easy to compute a really precise, high-resolution "similarity" score that measures the extent to which any two words appear in the same locations in the text. The end result of the estimation is just a plain old probability density function (PDF), which means that we can use any of the myriad of statistical tests that measure the closeness of two distributions. This is a common task that plays an important role in lots of different domains - really, whenever you need to say whether or not "this thing looks like this other thing" - and there are liverally dozens of ways to go about it (see this paper for a really good survey of the options). But, one of the simplest and most computationally efficient approaches is just to measure the size of the geometric "overlap" between the two distributions - for each sample point on the X-axis, take the smaller of the two corresponding Y-axis values in the two distributions. Then, take the discrete integral of the resulting area:

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

By skimming off the strongest links at the top of the stack, you end up with a little bespoke "distribution topic" for the word, a community of siblings that intuitively hang together.

### Twisty little passages

The really neat thing about this, though, is that this procedure implicitly binds together _all_ of the terms in the text into a huge lattice of connections. This makes it possible to step through the internal topic structure of the document. For example, once you've computed the sibling community for "horse," you can then do the same thing for any of the other words in the stack. If you take the second word, for example - "rode" - and compute _its_ sibling community, you'll see many of the same words again - by a sort of commutative property, words that were similar to "horse" will also be similar to "rode," since "rode" was similar to "horse". But, since the distribution of "rode" is subtly different, other terms will start to creep into view. Each time you do this, the semantic field will shift to center most closely on the anchoring word at the top of the stack. And as you do this again and again, you find that you start to traverse into completely different domains of meaning in the text. The war terms of the "horse" community can be followed into a cluster of terms about the body - no doubt, in the context of the war sections, related to _injury_ - which, in turn, can be used as a bridge to gain access to other body-related words like "face" and "lips," which finally give access to the prototypically peace-y threads in the text - "laugh," "smile," "dance," etc. Each sibling community is like a room in a massive maze, and each of the words is like a door that leads into an adjacent room that occupies a very similar but slightly different place in the overall topic-blueprint of the text.

This fascinates me because it _de-linearizes_ the text - which, I think, is truer to the form it takes when it's staged in the mind of a reader. Texts are one-dimensional lines, but - at the risk of generalizing, since this drifts into a subjective phenomenology of reading - we don't really think of texts as lines, or at least not _just_ as lines. We think of them as landscapes, regions, graphs, maps, diagrams, networks - clusters of characters, scenes, ideas, emotional valences, and color palettes, all set in relation to one another and wired up in lots of different ways. The text scrolls by on a one-dimensional track, but we're constantly clipping things out, shuffling them around, and arranging them onto a kind of congnitive pinboard, a mental map of the text as a little dimensional world instead of a linear axis of of words. Notions of "proximity" or "closeness" become divorced from the literal, X-axis positions of things in the document. In _War and Peace_, for example, I think of the battles at Borodino and Austerliz as being very "close" to one another, in the sense that they're the two major military set pieces in the plot. In fact, though, they're actually very "distant" in terms of where they actually appear in the text - they're separated by about 300,000 words, and their density functions only have an overlap of ~0.11, meaning, essentially, that they _don't_ overlap with each other about 90% of the time:

[fig]

So, how to operationalize that "conceptual" closeness? It turns out that this can be really easily captured just by creating a comprehensive network that traces out _all_ of the implicit linkages between the distribution topics, the "rooms" in the textual maze. The basic idea here - converting a text into a network - isn't a new one. In the past, lots of projects have experimented with representing a text as a social network, a set of relationships between characters to speak to one another or appear together in the same sections of the text. And, like I'm doing here, other projects have looked into different ways of representing all of the terms in a text in a graph, although in most cases the approaches have centered on the more traditional notion of "collocation," which has more to do with words that appear within a very tight window in the text. A really interesting project called TexTexture, for example, devised a method for visualizing the relationships between words that appeared within a 2- or 5- word radius in the document. As I'll show in a moment, though, I think that there are some interesting advantages to using the kernel density estimates as the underlying statistic when building out the network - the distributions tease out a kind of architectural blueprint of the document, which often maps (and at other times _doesn't_ map) onto the cognitive experience of the text in really interesting ways.

Anyway, once we've laid down all the piping to compute and compare the distribution densities of the words, building the actual graph is easy. For each word:

1. Compute the similarity between the word's probability density function and the function of every other word in the text.

1. Sort the list in descending order to get ranked stack of "distribution siblings," words that tend to show up in the same parts of the document.

1. Skim off the strongest links - say, the top 10 - and add them as nodes to a graph, using the similarity score as the weight of the edge that connects them.

Once this is in place, we get access to the whole scientific literature of graph-theoretic concepts, and the conceptual relationship between "austerlitz" and "borodino" falls out really easily - we can use Dijkstra's algorithm to get the shortest path between the two, which, unsurprisingly, makes just a single hop through the word "battle":

`austerlitz -> battle -> borodino`

With a path length of XXX, which puts "austerlitz" closer to "borodino" than about **XX%** of all other words in the text, even though they only co-occur about 10% of the time.

### Mapping the maze

This is useful as a confirmation that the network is representing something real about the text - or, at least, that it jibes with the _experience_ of the text. But it's sort of like stumbling through one little twisty passage in the labyrinth with a torch, tracing out a single little thread of connection in the document. What your really want is to be able to zoom back and see the whole structure at once, to trace out all of the connections between each of the words in the text with all of the other words - a bird's-eye view of the entire thing. This is a perfect task job for any of the off-the-shelf network layout algorithms, which treat all of the nodes as "particles" that repel one another by default, but which are bound together by a set of attractive forces exerted by the edges that connect them. Force Atlas 2 in Gephi works well - _War and Peace_ unfolds into a huge, spindly triangle:

[fig]

War to the left, peace to the right, and history on top, rising out of the center point between the two poles. I was also struck by the extent to which the war/peace opposition overlaps - and also doesn't overlap - with an opposition between men and women. Peace, on the far right, is essentially synonymous with women and children - "Natasha," "Sonya," "Marya," "girl," "lady," "daughter," "mother," - and women appear almost nowhere else in the entire graph. Whereas the men are much more evenly distributed. Pierre shows up near the center of the main war/peace axis, right near the connection point with the historiography cluster, surrounded by words of spiritual anxiety and questing - "doubt," "soul," "time," "world," "live." Anatole, meanwhile, is in the farthest reaches of the peace sections, right next to "visitors" (he was one) and "daughters" (he eloped with one). Rostov and Andrei (Andrew, in the Garnett translation) land near the center at the bottom, in the middle of a bridge that runs from the women and children on the right, into the world of the aristocratic salon ("Anna," "Pavlovna," "sitting"), which, interestingly, crosses over into the war sections by way of a cluster of terms related to the body and physical contact - "lips," "hand," "fingers," "touched," "eyes," "face," "shoulders," and "arm." (Which, apparently, crop up both in the word of Russian high society - embraces, clasps, arms over shoulders, pats on backs - and in the physicality of military life.) Andrei and Rostov land in middle of this nexus. The men traverse the gradient between war and peace, whereas the women basically _instantiate_ peace in the text, and have almost no interaction with the history or the war. War and peace are enacted as war and _women_.

I was also really interested in the large amount of space between "Napoleon" and "Bonaparte," which seem like they should hang together pretty closely. "Napoleon" sits far to the left, along the side of the triangle running from "battle" to "history," in the middle of a section related to military strategy and tactics ("military," "plan," "campaign," "men," "group"). Whereas "Bonaparte" is way down at the bottom of the triangle with Andrei and Rostov in the gradient between the military and the salon. The two names enact different roles in the text - Napoleon is the man himself, and Bonaparte is the Russian imagination of the man.

Here's the _Odyssey_:

[fig]

Here, instead of war/peace, it's an opposition between land and sea, home and away. At the bottom are Ithaca, Penelope, the suitors, the world of people, civilization, conflict; at the top, the world of the "raft," the home away from home, the natural world, the physical and metaphorical space between Troy and Ithaca - "waves," "sea," "wind," "island," "cave," "shore," the cyclops, the sirens. There's an interesting affinity here with the architecture of _Walden_, which takes the form of long, narrow pillar of words, which also span a gradient between land/civilization and water/wilderness:

[fig]

The world of Concord is at the bottom - "civilization," "enterprise," "comforts," "luxury," "dollars," "fashion." As you move up, this gives way Thoreau's narrative about his attempt to build his own, simplified version of the this world - "roof," "built," "dwelling," "simple." Which in turn bleeds into the world of his day-to-day existince at Walden, anchored around the word "day" - "hoeing" the field, "planting beans," "singing" to himself, "sitting", "thinking." Then the graph crosses over completely into the world of the pond - "water," "surface," "depth," "waves," and "walden." Remarkably, at the very top of the network, along with "lake" and "shore," is "_boat_," which is eerily similar to the "raft" on top of the _Odyssey_ - the most extreme removal from human civilization, the smallest outpost of dry land which a person can survive. Both enact the same dialectic - between a world of men on land, and a world of solitude on the pond or at sea. Of course, the direction is different - Thoreau flees Concord for the pond, Odysseus is trying to escape the sea and make his way back to Ithaca. Or, maybe not. Tennyson, writing about twenty years before _Walden_, reads the _Odyssey_ as a false quest - surely Odysseus would quickly bore of domestic life on Ithaca and dream of adventure at sea. Perhaps Tennyson's Ulysses is enacting the same 19th century anxieties about urbanism and industrialsm that drove Thoreau into the woods?

The _Divine Comedy_ looks almost exactly like _Walden_, except Concord/Walden is replaced with hell/heaven, with, fittingly enough, "christ" perched on top of the whole thing:

[fig]


