import common.tubes as tubes
from server.files import LiquidDataFile

class FileIds(LiquidDataFile):
    # TODO: react on new file event (top level aggs must be flushed)
    # TODO: ideally event handler must be in Index class

    def start_data(self):
        """ Start new file
        """
        self.id = 0             ## current id of data packet  in *.pak file (each new .pak started from zero id)
        self.words_to_ids = {}  ## new empty map of words to ids of records


    def load_data(self, data):
        """ Resume old file
        """
        if data:
            tube = tubes.MsgunpackTube()
            self.words_to_ids = next(tube(data, flush=True))

            ## find max id for each word then take max from them
            self.id = max([max(ids) for word, ids in self.words_to_ids.items()])
            self.id += 1


    def process_data(self, words):
        for word in words:
            if word not in self.words_to_ids:
                self.words_to_ids[word] = []

            self.words_to_ids[word].append(self.id)

        self.id += 1


    def save_data(self):
        tube = tubes.MsgpackTube()
        return b''.join( tube(self.words_to_ids, flush=True) )
