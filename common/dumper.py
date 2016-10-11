import os
import time
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

        if not os.path.exists(self.config.queue):
            os.makedirs(self.config.queue)

        self.uid = None     ## global uid for transaction
        self.trans = False  ## if True then in transaction mode


    def __enter__(self):
        self.trans = True

    def __exit__(self, *args):
        self.trans = False
        self.uid = None


    def save(self, box, data):
        """Saves data to queue dir.

        :data: serializable data to save

        """
        tube = MsgpackTube() | ZipTube()

        if not self.uid:
            self.gen_uid()

        stamp = time.time()
        packet = {
            'uid':   self.uid,
            'stamp': stamp,
            'box':   box,
            'data':  data
        }

        fuid = self.get_uid()
        ftmp = os.path.join(self.config.queue, 'tmp_' + fuid)
        fend = os.path.join(self.config.queue, 'dat_' + fuid)

        with open(ftmp, 'wb') as fobj:
            for chunk in tube(packet, flush=True):
                fobj.write(chunk)

        os.rename(ftmp, fend)

        if not self.trans:
            self.uid = None  ## next Dumper.save() will be with new uid


    def gen_uid(self):
        """Generates new random uid for data in transaction.
        """
        self.uid = self.get_uid()

    def get_uid(self):
        return str(uuid.uuid4())
