import tubes
import msgpack

class TestMsgpackTube:
    def test_correct_output(self):
        t = tubes.MsgunpackTube()

        data = msgpack.packb([1,2,3,4,5])
        chunks = list( t(data) )

        assert len(chunks) == 1, "msgunpack unpacks to full object immediatelly"
        assert chunks[0] == [1,2,3,4,5]


    def test_partition(self):
        t = tubes.MsgunpackTube()
        data = msgpack.packb([1,2,3,4,5])

        chunks = list( t(data[:3]) )  ## send first 3 bytes
        assert chunks == [], "nothing to iterate on"

        chunks = list( t(data[3:]) )  ## send remaining bytes

        assert chunks == [[1,2,3,4,5]], "must be one complete object [1,2,3,4,5] among chunks"
