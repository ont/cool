class LiquidDataFile:
    """ Abstract helper class which helps to:
          - track DatePath fresh path
          - load old data from file (resuming data saving)
          - save data to file (replacing old file content with new one)
    """

    def __init__(self, dpath):
        """ dpath: DatePath path which needs to be tracked
        """
        self.dpath = dpath
        self.on_change_callb = lambda *x: x  ## nop callback by default
        self.start_file()


    def save(self, data):
        """ Main method to use. Data will be processed and saved in class
            variables (internal buffer).
        """
        if self.dpath != self.dpath.fresh():
            self.on_change()
            self.refresh_file()

        self.process_data(data)
        self.empty = False


    def on_change(self, callback=None):
        if callback:
            self.on_change_callb = callback
        else:
            self.on_change_callb()


    def refresh_file(self):
        self.flush()
        self.dpath = self.dpath.fresh()

        self.start_file()


    def start_file(self):
        self.empty = True
        self.start_data()

        if self.dpath.exists():
            data = self.dpath.open('rb').read()
            self.load_data(data)


    def close(self):
        self.flush()


    def flush(self):
        if not self.empty:
            self.dpath.parent().makedirs()

            file = self.dpath.open('wb')
            file.write(self.save_data())
            file.close()


    # TODO: it is better than def switch_to_file(self, ofile, nfile)   (how to start the first file problem)
    # TODO: we need resume functionality
    # TODO: split LiquidFile into LiquidDataFile and LiquidStreamFile
    def start_data(self):
        raise NotImplementedError

    def load_data(self, data):
        raise NotImplementedError

    def process_data(self, data):
        raise NotImplementedError

    def save_data(self):
        raise NotImplementedError
