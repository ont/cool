import zlib
import msgpack

class TestTools:
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



