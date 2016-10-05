import msgpack
import common.tubes as tubes

class TestMsgpackTube:
    def test_correct_output(self):
        t = tubes.MsgpackTube()

        chunks = list( t([1,2,3,4,5]) )

        assert len(chunks) == 1, "msgpack packer has no internal cache"
        assert msgpack.unpackb(chunks[0]) == [1,2,3,4,5]
