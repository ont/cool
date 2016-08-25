import tubes
from files.liquid import LiquidFile

class FileIds(LiquidFile):
    def __init__(self, index, tree):
        LiquidFile.__init__(self, tree)
        self.index = index   ## save link to parent of all IndexFiles


    def start_file(self, file, path):
        self.tube = tubes.MsgpackTube()
        self.id = 0             ## current id of data packet  in *.pak file (each new .pak started from zero id)
        self.words_to_ids = {}  ## new empty map of words to ids of records


    def save_to_file(self, file, path, words):
        """ This method doesn't actually write to file
        """
        for word in words:
            if word not in self.words_to_ids:
                self.words_to_ids[word] = []

            self.words_to_ids[word].append(self.id)

        self.id += 1


    def stop_file(self, file, path):
        self.index.flush()  ## flush whole index


    ## TODO: mostly same code as in FileAgg
    def flush(self):
        """ This method is called by Index class
        """
        self.file.truncate(0)
        self.file.seek(0)

        for chunk in self.tube(self.words_to_ids, flush=True):
            self.file.write(chunk)

        self.file.flush()

