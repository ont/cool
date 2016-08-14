class LiquidFile:
    """ Abstract helper class which helps to:
          - track DateTree fresh path
          - avoid files overwrites
    """

    def __init__(self, tree):
        """ tree: DateTree path which needs to be tracked
        """
        self.tree = tree
        self.file = None
        self.suff = ''
        self.refresh_file()


    def save(self, data):
        """ Main method to use. Data will be saved to correct file.
        """
        if self.tree != self.tree.fresh():
            self.refresh_file()

        self.save_to_file(self.file, self.tree.suffix(self.suff), data)


    def close(self):
        if self.file:
            self.stop_file(self.file, self.tree.suffix(self.suff))
            self.file.close()


    def refresh_file(self):
        self.close()

        self.tree = self.tree.fresh()
        self.tree.parent().makedirs()

        n, suff = 1, ''
        while self.tree.suffix(suff).exists():
            suff, n = '.{:0>4}'.format(n), n+1

        self.suff = suff
        self.file = self.tree.suffix(suff).open('wb')
        self.start_file(self.file, self.tree.suffix(suff))


    # TODO: it is better than def switch_to_file(self, ofile, nfile)   (how to start the first file problem)
    def start_file(self, file, path):
        raise NotImplementedError

    def save_to_file(self, file, path, data):
        raise NotImplementedError

    def stop_file(self, file, path):
        raise NotImplementedError

