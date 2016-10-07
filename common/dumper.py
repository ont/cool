import os
import uuid
from common.tubes import MsgpackTube, ZipTube

class Dumper:
    """Class for storing data packets in special queue dir.
    """

    def __init__(self, config):
        """
        :config: instance of Config class.
        """
        self.config = config


    def save(self, data):
        """Saves data to queue dir.

        :data: serializable data to save

        """
        tube = MsgpackTube() | ZipTube()
        uid = str(uuid.uuid4())

        ftmp = os.path.join(self.config.queue, 'tmp_' + uid)
        fend = os.path.join(self.config.queue, 'dat_' + uid)

        with open(ftmp, 'wb') as fobj:
            for chunk in tube(data, flush=True):
                fobj.write(chunk)

        os.rename(ftmp, fend)
