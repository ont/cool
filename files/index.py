import os
import tubes
from .liquid import LiquidFile

class IndexFile(LiquidFile):

    def start_file(self, file, path):
        self.tube = tubes.MsgpackTube()
        self.start_index()

    def save_to_file(self, file, path, data):
        data = self.save_to_index(data)

        file.truncate(0)
        for chunk in self.tube(data, flush=True):
            file.write(chunk)

    def stop_file(self, file, path):
        self.stop_index()

    def start_index(self):
        raise NotImplementedError

    def save_to_index(self, data):
        raise NotImplementedError

    def stop_index(self):
        raise NotImplementedError

