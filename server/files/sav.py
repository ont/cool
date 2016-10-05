import os
import common.tubes
from .liquid_stream import LiquidStreamFile

class SavFile(LiquidStreamFile):
    def start_file(self, file, **kargs):
        self.tube = tubes.MsgpackTube()

    def save_to_file(self, file, data, stamp=None, **kargs):
        data = {
            'stamp': stamp.timetuple(),
            'data': data
        }
        for chunk in self.tube(data, flush=True):
            file.write(chunk)
            file.flush()

    def stop_file(self, file, path=None, **kargs):
        if path.exists():
            path.unlink()
