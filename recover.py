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
    """


    def recover(self, box):
        """ Starts recoverting process for box.

        :box: box to recover

        """
        self.box = box

        savs = self.box.dpath.join('*.sav').find(recursive=True)
        for sav in savs:
            self.recover_group(sav)

        self.box.close()


    def recover_group(self, sav):
        """Recover (replays) sav file and all its incremental neighbors.

        :sav: sav file without increment suffix.

        """
        self.recover_sav(sav)

        savs_inc = DatePath(sav).suffix('.????').find()
        for sav in savs_inc:
            self.recover_sav(sav)


    def recover_sav(self, sav):
        """Recover single sav file.

        :sav: file to recover

        """
        pak = self.get_pak(sav)
        if os.path.exists(pak):
            os.unlink(pak)


        try:
            tube = MsgunpackTube()
            data = open(sav, 'rb').read()

            for record in tube(data):
                stamp = datetime.datetime( *record[b'stamp'][:5] )  ## take first 5 numbers (year, month, day, hour, minute)
                with DateSynced(stamp=stamp):
                    self.box.save(record[b'data'], backup=False)

        finally:
            ## TODO: log about failed sav file
            os.unlink(sav)



    def get_pak(self, sav):
        """Returns corresponding pak for given sav

        :sav: path to sav file

        """
        return 'pak'.join(sav.rsplit('sav', 1))  ## some hacky method for doing rreplace
