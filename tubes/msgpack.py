import msgpack
from .tube import Tube

class MsgpackTube(Tube):
    """ This packer is supposed to be first in tube's chain.
    """
    def __init__(self):
        Tube.__init__(self)

    def process(self, data):
        yield msgpack.packb(data)

    def flush(self):
        return []  ## nothing to iterate on, nothing was cached in internal buffer, nothing to flush
