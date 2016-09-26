import os
import zlib
import msgpack
import datetime
from box import Box
from path import DateSynced
from recover import Recover

class TestBox:
    date1 = datetime.datetime(2001, 2, 3, 4, 5)
    date2 = datetime.datetime(2001, 2, 3, 4, 6)

    def test_simple_recover(self, tmpdir):
        """ Tests recovering after one crash
        """
        with DateSynced(stamp=self.date1):
            b = Box('test-box', base=str(tmpdir))
            b.save(['aaa', 'bbb', 'ccc'])
            b.save(['aaa', 'ccc', 'ddd'])

        savs = list(tmpdir.visit('*.sav'))
        assert len(savs) == 1, "one *.sav for backup"

        r = Recover('test-box', base=str(tmpdir))
        r.recover()

        savs = list(tmpdir.visit('*.sav'))
        assert len(savs) == 0, "after recovering no *.sav files must exist"

        pak = self.get_pak(tmpdir, '05.pak')
        idx = self.get_idx(tmpdir, '05.idx')
        assert pak == [[b'aaa', b'bbb', b'ccc'],[b'aaa', b'ccc', b'ddd']]
        assert idx == {b'aaa':[0,1], b'bbb':[0], b'ccc':[0,1], b'ddd': [1]}


    def test_multiple_recover(self, tmpdir):
        """ Test recovering after multiple crashes
        """
        with DateSynced(stamp=self.date1):
            b = Box('test-box', base=str(tmpdir))
            b.save(['aaa', 'bbb', 'ccc'])
            b.save(['aaa', 'bbb', 'ddd'])

        ## ...
        ## first crash
        ## ...

        with DateSynced(stamp=self.date2):
            b = Box('test-box', base=str(tmpdir))
            b.save(['after crash1'])

        ## ...
        ## second crash
        ## ...

        with DateSynced(stamp=self.date2):
            b = Box('test-box', base=str(tmpdir))
            b.save(['after crash2'])

        savs = list(tmpdir.visit('*.sav*'))
        assert len(savs) == 3, "05.sav, 06.sav and 06.sav.0001"

        r = Recover('test-box', base=str(tmpdir))
        r.recover()

        savs = list(tmpdir.visit('*.sav'))
        assert len(savs) == 0, "after recovering no *.sav files must exist"


        pak = self.get_pak(tmpdir, '05.pak')
        idx = self.get_idx(tmpdir, '05.idx')
        assert pak == [[b'aaa', b'bbb', b'ccc'], [b'aaa', b'bbb', b'ddd']]
        assert idx == {b'aaa':[0,1], b'bbb':[0,1], b'ccc':[0], b'ddd':[1]}

        pak = self.get_pak(tmpdir, '06.pak')
        idx = self.get_idx(tmpdir, '06.idx')
        assert idx == {b'after':[0,1], b'crash1':[0], b'crash2':[1]}
        assert pak == [[b'after crash1'], [b'after crash2']]

        idx = self.get_idx(tmpdir, '03.idx')
        assert idx == {b'after':2, b'crash1':1, b'crash2':1, b'aaa':2, b'bbb':2, b'ccc':1, b'ddd':1}


    def get_idx(self, tmpdir, fname):
        data = self.get_data(tmpdir, fname)
        return msgpack.unpackb(data)


    def get_pak(self, tmpdir, fname):
        data = self.get_data(tmpdir, fname)
        data = zlib.decompress(data)
        unpacker = msgpack.Unpacker()
        unpacker.feed(data)
        return list(unpacker)


    def get_data(self, tmpdir, fname):
        f = next(tmpdir.visit(fname))
        return f.read('rb')


