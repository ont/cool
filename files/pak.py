import os
import tubes
from .liquid_stream import LiquidStreamFile

class PakFile(LiquidStreamFile):
    def start_file(self, file, **kargs):
        self.tube = tubes.MsgpackTube() | tubes.ZipTube()

    def save_to_file(self, file, data, **kargs):
        for chunk in self.tube(data):
            file.write(chunk)

    def stop_file(self, file, **kargs):
        for chunk in self.tube(None, flush=True):
            file.write(chunk)

