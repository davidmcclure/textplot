

def plot_term_offsets(text, term, color='r', **kwargs):

    """
    Plot the raw, X-axis offsets of a term.
    """

    xs = text.terms[text.stem(term)]
    ys = np.zeros(len(xs))
    plt.scatter(xs, ys, marker='|', color=color)

    plt.axis([0, len(text.tokens), -1, 1])
    plt.axes().get_yaxis().set_visible(False)
    plt.xlabel('Word Offset')
    plt.title(term)

    fig = plt.gcf()
    fig.tight_layout()
    fig.set_size_inches(20, 3)

    return plt


def plot_term_histogram(text, term, color='#0067a2'):

    """
    Plot the X-axis offsets of a term.
    """

    xs = text.terms[text.stem(term)]
    plt.hist(xs, 40, color=color)

    plt.xlabel('Word Offset')
    plt.ylabel('Number of Occurrences')
    plt.title(term)

    fig = plt.gcf()
    fig.tight_layout()
    fig.set_size_inches(20, 8)

    return plt


def plot_term_kde(text, term, color='#0067a2', **kwargs):

    """
    Plot the KDE for an individual term.
    """

    kde = text.kde(text.stem(term), **kwargs)
    plt.plot(kde, color=color)

    plt.xlabel('Word Offset')
    plt.ylabel('Number of Occurrences')
    plt.title(term)

    fig = plt.gcf()
    fig.tight_layout()
    fig.set_size_inches(20, 8)

    return plt


def plot_kde_overlap(text, term1, term2, color1='#0067a2',
                     color2='#e8a945', overlap_color='#dddddd', **kwargs):

    """
    Plot the KDE overlap for two terms.
    """

    t1 = text.stem(term1)
    t2 = text.stem(term2)

    bc = text.score_braycurtis(t1, t2, **kwargs)

    kde1 = text.kde(t1, **kwargs)
    kde2 = text.kde(t2, **kwargs)
    plt.plot(kde1, color=color1, label=term1)
    plt.plot(kde2, color=color2, label=term2)

    overlap = np.minimum(kde1, kde2)
    plt.fill(overlap, color=overlap_color)
    plt.title(term1+', '+term2+' - '+str(round(bc, 4)))

    plt.xlabel('Word Offset')
    plt.ylabel('Number of Occurrences')
    plt.legend(loc='upper right')

    fig = plt.gcf()
    fig.tight_layout()
    fig.set_size_inches(20, 8)

    return plt

