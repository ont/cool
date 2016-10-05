import msgpack
from .tube import Tube


class MsgunpackTube(Tube):
    """ This packer is supposed to be first in tube's chain.
    """

    def __init__(self):
        Tube.__init__(self)
        self.unpacker = msgpack.Unpacker()

    def process(self, data):
        self.unpacker.feed(data)
        yield from self.unpacker

    def flush(self):
        return []  ## we can't create more object from incomplete data which was passed to process(...)
