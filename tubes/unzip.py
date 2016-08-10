import zlib
from .tube import Tube

class UnzipTube(Tube):
    """ Tube for unzipping stream data.
    """
    def __init__(self):
        Tube.__init__(self)
        self.unpacker = zlib.decompressobj()

    def process(self, data):
        res = self.unpacker.decompress(data)
        if res:
            yield res

    def flush(self):
        res = self.unpacker.flush()
        if res:
            yield res
