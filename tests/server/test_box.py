import sh
import os
import zlib
import msgpack
import datetime
from tools import TestTools
from server.box import Box
from common.path import DateSynced

class TestBox(TestTools):
    date1 = datetime.datetime(2001, 2, 3, 4, 5)

    def test_name_as_bytes(self, tmpdir):
        b = Box(b'bytestring', base=str(tmpdir))
        ## no exception should be thrown

    def test_correct_path(self, tmpdir):
        """ Checks that data will be saved under correct path.
        """
        ## TODO: potential unstable test (race condition with timestamp in Box)
        res = sh.date('+%Y/%m/%d/%H/%M.pak').strip()

        b = Box('test-box', base=str(tmpdir))
        b.save([1,2,3,4,5])
        b.close()

        print(list(tmpdir.visit()))
        assert tmpdir.join('test-box', res).check(file=1), ".pak file should exists"


    def test_sav_file(self, tmpdir):
        """ Checks that .sav file is used during saving.
        """
        ## TODO: potential unstable test (race condition with timestamp in Box)
        #res = sh.date('+%Y/%m/%d/%H/%M.sav').strip()

        now = datetime.datetime.now()
        with DateSynced(stamp=now):
            b = Box('test-box', base=str(tmpdir))
            b.save([1,2,3,4,5])

        sav_file = tmpdir.join('test-box', now.strftime('%Y/%m/%d/%H/%M.sav'))
        print(sav_file)
        print(open(str(sav_file), 'rb').read())
        assert sav_file.check(file=1), ".sav file should exists"

        data = {
            'stamp': now.timetuple(),
            'data': [1,2,3,4,5]
        }
        assert sav_file.open('rb').read() == msgpack.packb(data), ".sav file should contains serialized data"


    def test_sav_was_deleted(self, tmpdir):
        """ Checks that .sav file was deleted after box.close()
        """
        res = sh.date('+%Y/%m/%d/%H.sav').strip()

        b = Box('test-box', base=str(tmpdir))
        b.save([1,2,3,4,5])
        b.close()

        assert tmpdir.join('test-box', res).exists() == False, ".sav should be deleted"


    def test_data_inside_pak(self, tmpdir):
        """ Checks content of .pak file
        """
        with DateSynced(stamp=self.date1):
            b = Box('test-box', base=str(tmpdir))
            b.save([1,2,3,4,5])
            b.close()

        paks = list(tmpdir.visit('*.pak'))

        assert len(paks) == 1, "only one .pak should be created"

        data = self.get_pak(tmpdir, '*.pak')

        assert data == [[2001, 2, 3, 4, 5], [1,2,3,4,5]], "restored data from .pak should be [1,2,3,4,5]"


    def test_savs_and_paks_after_crash(self, tmpdir):
        with DateSynced(stamp=self.date1):
            b = Box('test-box', base=str(tmpdir))  ## HH.sav
            b.save([1,2,3,4,5])

            b = Box('test-box', base=str(tmpdir))  ## HH.sav.0001 (restarting box, emulating crash)
            b.save([1,2,3,4,5])

            b = Box('test-box', base=str(tmpdir))  ## HH.sav.0002
            b.save([1,2,3,4,5])

            b = Box('test-box', base=str(tmpdir))  ## HH.sav.0003
            b.save([1,2,3,4,5])
            b.close()                              ## .. and normaly close it (HH.sav.0003 will be deleted)

        savs = list(tmpdir.visit('*.sav*'))
        assert len(savs) == 3, "total amount of .sav files should be 3 (*.sav, *.sav.0001 and *.sav.0002)"

        savs = list(tmpdir.visit('*.sav.000?'))
        assert len(savs) == 2, "two incremental .sav files should be existed (*.sav.0001 and *.sav.0002)"

        savs = list(tmpdir.visit('*_0003.sav'))
        assert len(savs) == 0, "no *_0003.sav should be existed (normal finish)"

        contents = [ x.open('rb').read() for x in tmpdir.visit('*.sav') ]  ## content of each .sav
        assert len(set(contents)) == 1, "all .sav files should be identical"

        paks = list(tmpdir.visit('*.pak*'))
        assert len(paks) == 4, "four paks should be found (three broken and one normal)"

        contents = [ x.open('rb').read() for x in paks ]  ## content of each .pak
        assert len(set(contents)) == 2, "three broken (equal) and one normal .pak"

        data = self.get_pak(tmpdir, '*.pak.0003')
        assert data == [[2001,2,3,4,5],[1,2,3,4,5]], "restored data from normal .pak should be [1,2,3,4,5]"
