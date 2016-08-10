import zlib
from .tube import Tube


class ZipTube(Tube):
    """ Tube for compressing data stream.
    """
    def __init__(self, level=9):
        Tube.__init__(self)
        self.packer = zlib.compressobj(level)


    def process(self, data):
        res = self.packer.compress(data)
        if res:
            yield res


    def flush(self):
        res = self.packer.flush()
        if res:
            yield res
