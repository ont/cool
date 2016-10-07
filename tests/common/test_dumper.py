import zlib
import msgpack
from common.dumper import Dumper

class FakeConfig:
    def __init__(self, tmpdir):
        self.storage = tmpdir
        self.queue = tmpdir


class TestDumper:

    def test_simple_dump(self, tmpdir):
        fk = FakeConfig(str(tmpdir))
        d = Dumper(fk)
        d.save([1,2,3,4])

        dats = list(tmpdir.visit('dat_*'))
        tmps = list(tmpdir.visit('tmp_*'))
        assert len(dats) == 1, "one dat_[uuid] file must exists"
        assert len(tmps) == 0, "no tmps must be existed"


    def test_dump_content(self, tmpdir):
        fk = FakeConfig(str(tmpdir))
        d = Dumper(fk)
        d.save([1,2,3,4])

        f = next(tmpdir.visit('dat_*'))
        data = f.read('rb')
        data = msgpack.unpackb(zlib.decompress(data))
        assert data == [1,2,3,4]

