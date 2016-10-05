import common.tubes
from server.files import LiquidDataFile

class FileAgg(LiquidDataFile):

    def start_data(self):
        self.words_to_agg = {}  ## new empty map of words to aggregate counts


    def load_data(self, data):
        if data:
            tube = tubes.MsgunpackTube()
            self.words_to_agg = next(tube(data, flush=True))


    def process_data(self, words):
        for word in words:
            if word not in self.words_to_agg:
                self.words_to_agg[word] = 0

            self.words_to_agg[word] += 1


    def save_data(self):
        tube = tubes.MsgpackTube()
        return b''.join( tube(self.words_to_agg, flush=True) )
