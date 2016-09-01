import msgpack
import datetime
from tree import DateTree, DateSynced
from index import Index

class TestIndex:
    def test_simple(self, tmpdir):
        with DateSynced(stamp=datetime.datetime(2001, 2, 3, 4, 5)):
            i = Index(DateTree(str(tmpdir)))
            i.save({
                'test': 'me'
            })
            i.flush()

        data = next(tmpdir.visit('*/05.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'me': [0], b'test': [0]}

        data = next(tmpdir.visit('*/04.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'me': 1, b'test': 1}

        data = next(tmpdir.visit('*/03.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'me': 1, b'test': 1}

        data = next(tmpdir.visit('*/02.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'me': 1, b'test': 1}

        data = next(tmpdir.visit('*/2001.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'me': 1, b'test': 1}


    def test_multiple_writes(self, tmpdir):
        with DateSynced(stamp=datetime.datetime(2001, 2, 3, 4, 5)):
            i = Index(DateTree(str(tmpdir)))
            i.save({
                'test': 'me'
            })

        with DateSynced(stamp=datetime.datetime(2001, 2, 3, 4, 6)):
            i.save({
                'test': 'other'
            })

        with DateSynced(stamp=datetime.datetime(2001, 2, 3, 7, 8)):
            i.save({
                'test': 'other again'
            })
        i.flush()


        idxs = list(tmpdir.visit('*.idx'))
        assert len(idxs) == 8, "5 from first save + 1 new from next save + 2 new from last save"

        data = next(tmpdir.visit('*/08.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'other': [0], b'test': [0], b'again': [0]}

        data = next(tmpdir.visit('*/06.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'other': [0], b'test': [0]}

        data = next(tmpdir.visit('*/05.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'me': [0], b'test': [0]}

        data = next(tmpdir.visit('*/04.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'me': 1, b'other': 1, b'test': 2}

        data = next(tmpdir.visit('*/07.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'other': 1, b'test': 1, b'again': 1}

        data = next(tmpdir.visit('*/03.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'me': 1, b'other': 2, b'test': 3, b'again': 1}

        data = next(tmpdir.visit('*/02.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'me': 1, b'other': 2, b'test': 3, b'again': 1}

        data = next(tmpdir.visit('*/2001.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'me': 1, b'other': 2, b'test': 3, b'again': 1}


    def test_time_moving(self, tmpdir):
        with DateSynced(stamp=datetime.datetime(2001, 2, 3, 4, 5)):
            i = Index(DateTree(str(tmpdir)))
            i.save({
                'test': 'me'
            })

        idxs = list(tmpdir.visit('*.idx'))
        assert len(idxs) == 5, "five empty idx"

        data = [idx.read('rb') for idx in idxs]
        assert data == [b'', b'', b'', b'', b''], "all files are empty"


        with DateSynced(stamp=datetime.datetime(2001, 2, 3, 4, 6)):
            i.save({
                'test': 'other'
            })

        idxs = list(tmpdir.visit('*.idx'))
        assert len(idxs) == 6, "five empty idx + new one"

        data = next(tmpdir.visit('*/2001.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': 1, b'me': 1}

        data = next(tmpdir.visit('*/02.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': 1, b'me': 1}

        data = next(tmpdir.visit('*/03.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': 1, b'me': 1}

        data = next(tmpdir.visit('*/04.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': 1, b'me': 1}

        data = next(tmpdir.visit('*/05.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': [0], b'me': [0]}

        data = next(tmpdir.visit('*/06.idx')).read('rb')
        assert data == b'', "not yet flushed file"

        i.flush()

        data = next(tmpdir.visit('*/06.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': [0], b'other': [0]}

        data = next(tmpdir.visit('*/04.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': 2, b'me': 1, b'other': 1}


    def test_crash(self, tmpdir):
        with DateSynced(stamp=datetime.datetime(2001, 2, 3, 4, 5)):
            i = Index(DateTree(str(tmpdir)))
            i.save({
                'test': 'me'
            })
            ## crash here... Then we restart index
            i = Index(DateTree(str(tmpdir)))
            i.save({
                'test': 'other'
            })


        idxs = list(tmpdir.visit('*.idx'))
        data = [idx.read('rb') for idx in idxs]
        assert data == [b'', b'', b'', b'', b''], "all files are empty"


    def test_crash_after_time_movement(self, tmpdir):
        with DateSynced(stamp=datetime.datetime(2001, 2, 3, 4, 5)):
            i = Index(DateTree(str(tmpdir)))
            i.save({
                'test': 'me'
            })

        with DateSynced(stamp=datetime.datetime(2001, 2, 3, 4, 6)):
            i.save({
                'test': 'other'
            })
            ## crash ..
            i = Index(DateTree(str(tmpdir)))
            i.save({
                'test': 'some'
            })


        data = next(tmpdir.visit('*/2001.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': 1, b'me': 1}

        data = next(tmpdir.visit('*/02.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': 1, b'me': 1}

        data = next(tmpdir.visit('*/03.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': 1, b'me': 1}

        data = next(tmpdir.visit('*/04.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': 1, b'me': 1}

        data = next(tmpdir.visit('*/05.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': [0], b'me': [0]}

        data = next(tmpdir.visit('*/06.idx')).read('rb')
        assert data == b'', "not yet flushed file"

        i.flush()

        data = next(tmpdir.visit('*/2001.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': 2, b'me': 1, b'some': 1}

        data = next(tmpdir.visit('*/05.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': [0], b'me': [0]}

        data = next(tmpdir.visit('*/06.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': [0], b'some': [0]}



    def test_restoring_id_after_crash(self, tmpdir):
        with DateSynced(stamp=datetime.datetime(2001, 2, 3, 4, 5)):
            i = Index(DateTree(str(tmpdir)))
            i.save({
                'test': 'me'
            })
            i.save({
                'test': ['me','other']
            })
            i.flush()

            ## crash.. and restart
            i = Index(DateTree(str(tmpdir)))
            i.save({
                'other': 'test'
            })
            i.flush()

        data = next(tmpdir.visit('*/05.idx')).read('rb')
        assert msgpack.unpackb(data) == {b'test': [0,1,2], b'me': [0,1], b'other': [1,2]}

