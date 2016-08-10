import sh
import os
import zlib
import msgpack
from box import Box

class TestBox:
    def test_correct_path(self, tmpdir):
        """ Checks that data will be saved under correct path.
        """
        res = sh.date('+%Y/%m/%d/%H.pak').strip()

        b = Box('test-box', base=str(tmpdir))
        b.save([1,2,3,4,5])
        b.close()

        print(list(tmpdir.visit()))
        assert tmpdir.join('test-box', res).check(file=1), ".pak file should exists"


    def test_sav_file(self, tmpdir):
        """ Checks that .sav file is used during saving.
        """
        res = sh.date('+%Y/%m/%d/%H.sav').strip()

        b = Box('test-box', base=str(tmpdir))
        b.save([1,2,3,4,5])

        sav_file = tmpdir.join('test-box', res)
        print(sav_file)
        print(open(str(sav_file), 'rb').read())
        assert sav_file.check(file=1), ".sav file should exists"
        assert sav_file.open('rb').read() == msgpack.packb([1,2,3,4,5]), ".sav file should contains serialized data"


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

        b = Box('test-box', base=str(tmpdir))
        b.save([1,2,3,4,5])
        b.close()

        paks = list(tmpdir.visit('*.pak'))

        assert len(paks) == 1, "only one .pak should be created"

        data = paks[0].open('rb').read()

        data = zlib.decompress(data)
        data = msgpack.unpackb(data)

        assert data == [1,2,3,4,5], "restored data from .pak should be [1,2,3,4,5]"


    def test_savs_and_paks_after_crash(self, tmpdir):
        b = Box('test-box', base=str(tmpdir))  ## restarting box, emulating crash...
        b.save([1,2,3,4,5])

        b = Box('test-box', base=str(tmpdir))  ## restarting box, emulating crash...
        b.save([1,2,3,4,5])

        b = Box('test-box', base=str(tmpdir))  ## restarting box, emulating crash...
        b.save([1,2,3,4,5])

        b = Box('test-box', base=str(tmpdir))  ## restarting box, emulating crash...
        b.save([1,2,3,4,5])
        b.close()                              ## .. and normaly close it

        savs = list(tmpdir.visit('*.sav'))
        assert len(savs) == 3, "total amount of .sav files should be 3 (*.sav, *_0001.sav and *_0002.sav)"

        savs = list(tmpdir.visit('*_000?.sav'))
        assert len(savs) == 2, "two incremental .sav files should be existed (*_0001.sav and *_0002.sav)"

        savs = list(tmpdir.visit('*_0003.sav'))
        assert len(savs) == 0, "no *_0003.sav should be existed (normal finish)"

        paks = list(tmpdir.visit('*.pak'))
        assert len(paks) == 4, "four paks should be found (three broken and one normal)"

        contents = [ x.open('rb').read() for x in paks ]  ## content of each .pak
        assert len(set(contents)) == 2, "three broken (equal) and one normal .pak"

        data = next(tmpdir.visit('*_0002.pak')).read('rb')
        data = zlib.decompress(data)
        data = msgpack.unpackb(data)
        assert data == [1,2,3,4,5], "restored data from normal .pak should be [1,2,3,4,5]"

        contents = [ x.open('rb').read() for x in tmpdir.visit('*.sav') ]  ## content of each .sav
        assert len(set(contents)) == 1, "all .sav files should be identical"

