import os
import uuid
from common.tubes import MsgpackTube, ZipTube

class Dumper:
    """Class for storing data packets in special queue dir.
    """

    def __init__(self, path, config):
        """
        :path: path to queue dir.
        """
        self.path = path
        self.config = config


    def save(self, data):
        """Saves data to queue dir.

        :data: serializable data to save

        """
        tube = MsgpackTube() | ZipTube()
        ftmp = os.path.join(config.queue, 'tmp_' uuid.uuid4())
        fend = os.path.join(config.queue, 'dat_' uuid.uuid4())
        with open(ftmp, 'wb') as fdump:
            for chunk in tube(data, flush=True):
                ftmp.write(chunk)

        os.rename(ftmp, fend)
