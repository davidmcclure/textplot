

class GraphBuilder(object):


    def __init__(self, text):

        """
        Set the text instance.
        """

        self.text = text

        # By default, use all terms.
        self.terms = self.text.terms.keys()
