### Using kernel density estimation to search inside of long texts

#### Documents vs. Texts

Back when I was working at Virginia, Wayne Graham and I were tasked with the job of moving a big collection of old text encoding projects that had been developed at the Etext Center, a precursor to the Scholars' Lab, onto a more up-to-date server architecture. The Etext Center was one of the earliest and most venerable digital humanities outfits at Virgnia - and, in many ways, an early blueprint for the modern digital humanities center. For 15 years, from 1992 through 2007, a merry troupe of students, professors, librarians, and technologists pumped out thousands of digital editions of literary and historical texts. At core, it was a TEI encoding shop - most of the projects took the form of high-fidelity, interpretive editions of individual texts, or smallish groups of texts - the collected works of Mark Tain, for instance, as opposed to projects that work at the scale of tens or hundreds of thousands of texts.

For years, all of these projects were hosted on a single physical server in the library, which, by the time I showed up in 2011, was ancient and out of warranty, making it a ticking time bomb from an operations standpoint - everything had to get moved over to the library's modern server infrastructure. For the most part, this was a pretty straightforward process. Most of the projects consisted of a set of TEI documents - usually the core work product - and a set of XSLT stylesheets that transformed the XML into HTML for presentation on the web. For each project, we just grepped through all the XML files and scrubbed out hard-coded links to the old Etext website, plugged the scripts that generated the HTML into the Capistrano-backed deployment rig that powered the production servers, and then just shovelled all the files onto the new servers.

Again and again, though, there was one big sticking point - many of the projects had some kind of full-text searching functionality, which is a much harder to migrate than nice, static XML/XSLT files. To make things worse, most of the projects used an ancient and long-defunct XML search utility called XXX, meaning that we had to more or less rewrite everything from scratch. Fortunately, open-source search technologies are much better now than there were in the mid-90's, and we took a pretty standard approach to the problem - write some scripts to split up the TEI documents into little chunks (usually just breaking on some paragraph- or section-level unit of markup, like `<div2>` or `<p>`, depending on how the project), and then index all the sub-documents in Solr, which feeds results into a web interface that exposes all of the bells and whistles that come with Solr - hit-highlighting, faceting, pagination, etc.

This is an easy and effective solution to the problem - Solr's hit-highlighting did a good job of replicating the functionality of the old software, which was basically generated a stack of keyword-in-context concordance results. But, in the back of my head, I always had a kind of vague, diffuse, philosophical reluctance about this approach - a spidey sense that valuable information was being lost, that we were using a sub-optimal set of tools for the job. I rolled it around in my head for a few weeks during the walk home from work, and eventually realized that the problem was actually really low-level and fundamental, something far too open-ended to by tackled in the context of the server migrations. Really, we were bumping up against the limitations of the basic unit of information that software systems like Solr are built around - the idea of the "document," an organizating principle for information retrieval and large swaths of natural language processing and computation linguistics.

A document is basically a little packet of information that might contain some kind of information that you care about, mixed in with a collection of other similarly-structured packets - a corpus, a card catalog, a database, a library, the internet, etc. This idea is so ubiquitous - and, in most cases, so obviously useful - that it barely needs to be rehearsed. Almost every digital object that we interact with on a computer is modeled as a document at some level or another. Web pages are documents. This blog post is a document. Tweets, product listings on Amazon, user profiles on Facebook, Omeka items, Neatline records, Drupal nodes, emails - all documents. A key feature of documents, defined in this way, is that they're generally thought of as being discrete, self-sufficient units of information. A document contains inside itself all the information that it needs to be a useful. For example, if a doctor opens an electronic medical record for a patient, she doesn't care about any of the other records in the database - she just wants _the_ record for _this_ patient. Thought of this way, the task of searching becomes conceptually simple. Given some query, just find a subset of documents that are relevant to the query, and then rank the matching documents by the relevance scores, so that the best match sits at the top of the stack.

This makes sense, because most information just does, in fact, take the form of a big collection of documents. If I go to the digital catalog search interface in a library - Virgo at UVa, SearchWorks at Stanford - and type in "War and Peace," I want to find, well - _War and Peace_, one particular document in the library. In the simplest case, it's basically a hash lookup. More likely, though, you probably don't know exactly which document you want, but instead know the _type_ of document that you're looking for. For example, if I'm working on a piece of software and run into an error message that I can't make sense of, I usually just paste the entire output into Google. I don't know which exact page I want - it could be a StackOverflow answer, or a thread on a Google group, a blog post - but I do know that I want just one page that tells me exactly what's wrong an exactly how to fix it - the _best_ answer to the question, if not the only one. Search is a filtering process, a winnowing-down, a reduction from many to one, a fundemtanlly _comparaive_ process in which a set of documents are ranked against one another. For a given query X, for each document, the question is: "Does the document contain X, and if so, to what extent?" Usually, if some sort of vector space model is being used, this question can be boiled down to a single statistic between 0 and 1, where 0 is "not at all relevant" and 1 would basically mean that the query _is_ document.

But this breaks down in interesting and dramatic ways when applied to literary texts. The question of whether something is contained in the text becomes much less interesting. By the point you're critically interested in some combination of a text and an idea (a "query"), you already know that the idea has some kind of salience in the text. The question, instead, is _where_ or _when_ - texts are fundamentally dimensional in a way that "documents" aren't. In geometric terms, if a Solr document is a point with a single value, a text is a line, a progression, an X-axis along which things are positioned - words, narratives, plots, characters, themes, motifs. Reading takes place over time - literature is traversed, it exists as an experience within and across a textual interval. Texts unfold, arc, and progress. And far from being just a practical necessity - or even an annoyance, something to be "fixed" with technology - this experience of narrative-in-time is arguably fundamental to and even constitutative of literature. Peter Brooks, writing in the Freud-preoccupied 70s, argued that texts are powerful because they operate like little bite-sized fractals of human lives. The beginning is a birth, a coming into being, the initiation of a narrative tension that pushes forward into the middle of the text and strives towards a dischard and dissolution at the end, the narrative "death" that allows the reader to rehearse her own death.

Theory aside, though, the point is that we care much more about _where_, _when_, and _how_ things exist inside of texts, not just _if_ and _to what extent_. And the "things" tend to be more diffuse and composite than the things you'd search for in a commercial information system. In _War and Peace_, how does the distribution of "france" and "french" compare to the distribution of "russia" and "russian"? Where do Natasha, Pierre, and Andrei all show up in the same places? Where do particular motifs appear - Napoleon's white hands, Andrei finding spiritual transcendence in the sky, the Russian bear, etc.? What parts of the text lean masculine ("man," "boy," "he," "his") and which lean feminine ("woman", "girl," "she," "her")? In _Leaves of Grass_, where do "myself"-ish terms cluster in the text - things like "me," "my," "mine," "myself," and "I"? Whitman has a habit of addressing the reader directly - is there any pattern in the distribution of "you" and "your"? And beyond that, there's a whole class of comparative questions that arise constantly during interpretation. Where does _Leaves of Grass_ "sound like" this Yeats poem? Where does _Leaves of Grass_ sound like _Moby Dick_, or _Walden_, or Tennyson? Generally speaking, how does the "mass" of a word, a set of words, or a concept distribute across the width of the document? How do they slosh around and clump together?

# Segment length whack-a-mole

The common solution to this problem is to chop up the text into little evenly-spaced bits and shovel them all into a conventional document index like Solr.


the problem with this, though, is that it always prioritizes one particular class of query at the expense of others.


really, the "documents" in a literary text are _all continuous sequences of words, of all lengths_. The thing you're "looking for" could be a single word, a phrase, a sentence, a paragraph, a section, a chapter, a group of chapters, or any segement of any length that spans across the borders delineated by the obvious "section" taxononomies.















Say you study Shakespeare, and you're trying to locate something of interest in the plays (for now, let's bracket the question of what those _somethings_ are for literary scholars). Where do the "documents" start and stop? It wouldn't be incorrect, from one perspective, to just say that each play is a separate document, and shovel all 39 of them into a document index like Solr or Elasticsearch. And in fact, if you're analyzing hundreds or thousands of texts - not just Shakespeare, say, but all available renaissance drama - then this makes a lot of sense. You don't really care about the internal structure of Shakespeare per se - how language sloshes around inside and among the plays, how plots develop, how characters interact - but rather how the half-a-million-odd words in Shakespeare contribute to a broader set of statistical insights about the surrounding corpus.

But what if you _are_ still interested in the internal mechanics of Shakespeare? Computational methods have been quiet on this front, mostly, no doubt, because real people are able to read and wrap their minds around the mechanics of individual texts, and there's less low-hanging fruit for computation to pick out. I can sit down and burn through all of Shakespeare in a few weeks - but I could spend a lifetime reading and still fail to chew through a corpus at the scale of hundreds of thousands or millions of texts, in the way that a computer can in a matter of seconds or minutes. People have been computing texts at a "close" level for thousands of years - there's less obvious work for computers to do. And furthermore, close analysis of literature doesn't play to the strengths of a computer - writing a program that could actually _read_ a literary text, in any kind of recognizable or interesting sense of the word, would involve solving the hardest of hard problem in artificial intelligence. We'd have to program a person - and, from the perspective of literary study, why bother, since we're already people?

But I wonder if, in largely putting aside computation when we reach the boundaries of texts, we're actually missing some interesting opportunities. Not to automate the act of _reading_ - which is maybe impossible and likely uninteresting - but instead to build a category of tools that could be thought of as _thinking aids_ or _mind maps_ for texts, ways to


software tools that instead of leading us away from the interiority of texts
towards insight in the aggregate instead lead us back into the text, that circle
around and air drop us back into the literary topography of the document.

Or, put differently, computational approaches to just literature, as it differs from literary history (and I think it does, although the difference has been eroded in unsustainable ways in recent years). Thus far, the digital humanities have been dominated by a blend of neo-New-Historicists (what _did_ this text mean, and what does it tell us about _then_?) and neo-Russian-Formalists (what do these texts tell us about literature in general?). What would the New Critics have done with computers?


to be reluctant to map its activities back onto the intellectual history 20th century literary theory and interpretive practice,





it would be literally impossible for me to chew through a corpus at the scale of hundreds of thousands or millions of texts, in the way that a computer can in a matter of seconds or minutes. People have been computing texts at a "close" level for thousands of years,


read the hundreds of thousands of millions of documents that computers can chew through

. Where do the "documents" start and stop? In a simplistic sense, we could just say that each individual play is a separate document, and shovel all 39 of them into a document index like Solr or Elasticsearch.

- or, for that matter, any kind of long document that's "about" lots of different things. Say you're interested in Whitman. Where do the "documents" start and stop? You could say that each literary "work," defined in some kind of chronological sense, is a document - but, Whitman only really wrote one thing. So, we could treat the two main versions of the text as separate documents


texts are lines, not points
so, common approach is to split them up into little mini documents
but this always does a kind of violence to the text
the decision of the segment size is fraught - whatever you choose, you'll prioritize one class of results over others
really, when searching for things in literary texts, the set of possible results is the set of all continuous strings words in the text, of all lengths








In information retrieval, a document is a discrete little packet of information - a cluster, a nodule, a data point that can be manipulated and analyzed as a single, unified entity. Documents aren't considered to be completely homogenous - in topic modelling, for example, documents are understood to have the ability to exhibit multiple topics, for example, to be about more than one thing. But, fundamentally, a document is the smallest unit of analysis

But this runs completely counter to the experience of a literary text, which fundemtanlly exists an an a progression, a narrative, a textual _interval_ that begins at the first word of the text and extends - both in a typographical and structural sense, and in a temporal sense, for any individual reading experience - to the last word of the text. This experience of a text as a space or an interval, a one-dimensional axis that is

If a document is a point, then a literary text is a line.

texts have a _dimensionality_ that documents don't - if a document is a point, then a text is a line, an X-axis, along which words, concepts, plots, events, and reading experiences can be plotted.


## Segment length whack-a-mole
