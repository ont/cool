import tubes
from files.liquid import LiquidFile

class FileAgg(LiquidFile):

    ## TODO: >>>> HOW TO LOAD OLD AGGS??? (after crash restart or daemon restart) <<<<

    def start_file(self, file, path):
        self.tube = tubes.MsgpackTube()
        self.words_to_agg = {}  ## new empty map of words to aggregate counts


    def save_to_file(self, file, path, words):
        """ This method doesn't actually write to file
        """
        for word in words:
            if word not in self.words_to_agg:
                self.words_to_agg[word] = 0

            self.words_to_agg[word] += 1


    def stop_file(self, file, path):
        self.flush(file)


    ## TODO: code duplication
    def flush(self):
        self.file.truncate(0)

        for chunk in self.tube(self.words_to_agg, flush=True):
            self.file.write(chunk)

