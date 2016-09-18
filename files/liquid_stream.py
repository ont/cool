class LiquidStreamFile:
    """ Abstract helper class which helps to:
          - track DatePath fresh path
          - resolve files collisions
    """

    def __init__(self, dpath):
        """ dpath: DatePath path which needs to be tracked
        """
        self.dpath = dpath
        self.file = None
        self.suff = ''
        self.refresh_file()


    def save(self, data):
        """ Main method to use. Data will be saved to correct file.
        """
        if self.dpath != self.dpath.fresh():
            self.refresh_file()

        self.save_to_file(self.file, data,
                path=self.dpath.suffix(self.suff),
                stamp=self.dpath.stamp)


    def close(self):
        if self.file:
            self.stop_file(self.file, path=self.dpath.suffix(self.suff))
            self.file.close()


    def refresh_file(self):
        self.close()

        self.dpath = self.dpath.fresh()
        self.dpath.parent().makedirs()

        self.suff = self.find_free_suffix()
        self.file = self.dpath.suffix(self.suff).open('wb')

        self.start_file(self.file, path=self.dpath.suffix(self.suff))


    def find_free_suffix(self):
        """ Find next suffix for filepath that doesn't exists.
            For example:
                /some/path/file.txt       -- exists
                /some/path/file.txt.0001  -- exists
                /some/path/file.txt.0002  -- doesn't exists
                /some/path/file.txt.0003  -- exists

            .. then "0002" will be returned
        """
        n, suff = 1, ''
        while self.dpath.suffix(suff).exists():
            suff, n = '.{:0>4}'.format(n), n+1

        return suff


    # TODO: it is better than def switch_to_file(self, ofile, nfile)   (how to start the first file problem)
    # TODO: we need resume functionality
    def start_file(self, file, **kargs):
        raise NotImplementedError

    def save_to_file(self, file, data, **kargs):
        raise NotImplementedError

    def stop_file(self, file, **kargs):
        raise NotImplementedError

