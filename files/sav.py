import os
import tubes
from .liquid_stream import LiquidStreamFile

class SavFile(LiquidStreamFile):
    def start_file(self, file, path):
        self.tube = tubes.MsgpackTube()

    def save_to_file(self, file, path, data):
        for chunk in self.tube(data, flush=True):
            file.write(chunk)
            file.flush()

    def stop_file(self, file, path):
        if path.exists():
            path.unlink()
