import os
import tubes
from .liquid import LiquidFile

class PakFile(LiquidFile):
    def start_file(self, file, path):
        self.tube = tubes.MsgpackTube() | tubes.ZipTube()

    def save_to_file(self, file, path, data):
        for chunk in self.tube(data):
            file.write(chunk)

    def stop_file(self, file, path):
        for chunk in self.tube(None, flush=True):
            file.write(chunk)

