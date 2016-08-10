import tubes

class TestComplexTube:
    def test_complex_1(self):
        """ Checks that all tubes works together in both directions.
        """
        t_pack = tubes.MsgpackTube() | tubes.ZipTube()
        t_unpack = tubes.UnzipTube() | tubes.MsgunpackTube()

        data = [1,2,3,4,5] * 10

        objs = []
        for chunk in t_pack(data):
            for obj in t_unpack(chunk):
                objs.append(obj)

        assert objs == [], "ZipTube has internal cache and doesn't outuput compressed data immediatelly"

        data = [3,2,1]  ## additional object to pack
        for chunk in t_pack(data, flush=True):
            for obj in t_unpack(chunk):
                objs.append(obj)

        assert objs == [[1,2,3,4,5] * 10, [3,2,1]], "due to flush all objects must be outputted"



    def test_complex_2(self):
        """ Checks that all tubes works together in both directions.
        """
        t_pack = tubes.MsgpackTube() | tubes.ZipTube()
        t_unpack = tubes.UnzipTube() | tubes.MsgunpackTube()

        data = [1,2,3,4,5] * 10

        objs = []
        for chunk in t_pack(data):
            for obj in t_unpack(chunk):
                objs.append(obj)

        assert objs == [], "ZipTube has internal cache and doesn't outuput compressed data immediatelly"

        for chunk in t_pack(None, flush=True):
            for obj in t_unpack(chunk):
                objs.append(obj)

        assert objs == [[1,2,3,4,5] * 10], "due to flush all objects must be outputted"
