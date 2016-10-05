import os
import common.tubes as tubes
from .liquid_stream import LiquidStreamFile

class PakFile(LiquidStreamFile):
    def start_file(self, file, stamp=None, **kargs):
        self.tube = tubes.MsgpackTube() | tubes.ZipTube()

        ## save stamp to pak as first data entry
        stamp = stamp.timetuple()[:5]
        for chunk in self.tube(stamp):
            file.write(chunk)


    def save_to_file(self, file, data, **kargs):
        for chunk in self.tube(data):
            file.write(chunk)

    def stop_file(self, file, **kargs):
        for chunk in self.tube(None, flush=True):
            file.write(chunk)

