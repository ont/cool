import os
import msgpack
import datetime
import itertools
from box import Box
from path import DatePath, DateSynced
from tubes import MsgunpackTube

##
# * Problem of pak-sav-idx save order (if *.sav is first then it will be switch
#   first and drops all data for recover)
#
# * Premature idx flush (os file buffer overflow) <---> DatePath.open -->
#   FileProxy object with infinite buffer
# = not a problem (liquid_data flushes only of file switching)
#
# * No need for dt async flush of pak-sav-idx (because of sav autoflush at
#   every data arrive)
##

class Recover:
    """ Class which implements recovering after crash.

        Basic steps of recovering process:
          1. found all *.sav files
          2. for each founded .sav replay all saved data

        :name: name of box to recover
        :base: optional base path for box
    """
    def __init__(self, name, base='./boxes'):
        self.name = name.decode('utf-8') if type(name) == bytes else name
        self.base = base
        self.tube = MsgunpackTube()


    def recover(self):
        """ Starts recoverting process.
        """
        ## using DatePath here just for easy files finding
        dp = DatePath(self.base).join(self.name)

        savs = dp.join('*.sav').find(recursive=True)
        for sav in savs:
            self.recover_group(sav)


    def recover_group(self, sav):
        """Recover (replays) sav file and all its incremental neighbors

        :sav: sav file without increment suffix

        """
        box = self.recover_sav(sav, None)

        savs_inc = DatePath(sav).suffix('.????').find()
        for sav in savs_inc:
            self.recover_sav(sav, box)

        box.close()


    def recover_sav(self, sav, box):
        """Recover single sav file

        :sav: file to recover
        :box: temporary box for group of sav files or None if it must be created
        :returns: box

        """
        pak = self.get_pak(sav)
        if os.path.exists(pak):
            os.unlink(pak)

        try:
            data = open(sav, 'rb').read()
        except:
            ## TODO: log about failed sav file
            return  ## skip broken sav...

        os.unlink(sav)

        for record in self.tube(data):
            stamp = datetime.datetime( *record[b'stamp'][:5] )  ## take first 5 numbers (year, month, day, hour, minute)
            with DateSynced(stamp=stamp):
                if not box:
                    box = Box(self.name, base=self.base)
                box.save(record[b'data'])

        return box


    def get_pak(self, sav):
        """Returns corresponding pak for given sav

        :sav: path to sav file

        """
        return 'pak'.join(sav.rsplit('sav', 1))  ## some hacky method for doing rreplace
