import os
import tubes
from .liquid import LiquidFile

class SavFile(LiquidFile):
    def start_file(self, file, path):
        self.tube = tubes.MsgpackTube()

    def save_to_file(self, file, path, data):
        for chunk in self.tube(data, flush=True):
            file.write(chunk)
            file.flush()

    def stop_file(self, file, path):
        path.unlink()
