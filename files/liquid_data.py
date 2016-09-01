class LiquidDataFile:
    """ Abstract helper class which helps to:
          - track DateTree fresh path
          - load old data from file (resuming after crash)
          - save data to file (rewriting old file content with new one)
    """

    def __init__(self, tree):
        """ tree: DateTree path which needs to be tracked
        """
        self.tree = tree
        self.file = None
        self.on_change_callb = lambda *x: x  ## nop callback by default
        self.refresh_file()


    def save(self, data):
        """ Main method to use. Data will be processed and saved in class
            variables (internal buffer).
        """
        if self.tree != self.tree.fresh():
            self.on_change()
            self.refresh_file()

        self.process_data(data)


    def on_change(self, callback=None):
        if callback:
            self.on_change_callb = callback
        else:
            self.on_change_callb()


    def refresh_file(self):
        self.close()

        self.tree = self.tree.fresh()
        self.tree.parent().makedirs()

        self.start_data()

        if self.tree.exists():
            data = self.tree.open('rb').read()
            self.load_data(data)

        self.file = self.tree.open('ab')  ## append mode: don't truncate file after opening
        self.file.seek(0)                 ## moving to start position  TODO: is it pointless??


    def close(self):
        if self.file:
            self.flush()
            self.file.close()


    def flush(self):
        data = self.save_data()
        self.file.truncate(0)
        self.file.seek(0)
        self.file.write(data)
        self.file.flush()


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
