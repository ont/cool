import datetime
from path import DateSynced

class TestTree:
    def test_sync(self):
        with DateSynced(stamp=datetime.datetime(2001, 2, 3, 4, 5)):
            actual = DateSynced.actual()

        assert actual == datetime.datetime(2001, 2, 3, 4, 5)

    def test_nested_sync(self):
        with DateSynced(stamp=datetime.datetime(2001, 2, 3, 4, 5)):
            with DateSynced():
                actual = DateSynced.actual()

        assert actual == datetime.datetime(2001, 2, 3, 4, 5)

    def test_nested_sync2(self):
        with DateSynced(stamp=datetime.datetime(2001, 2, 3, 4, 5)):
            with DateSynced(datetime.datetime(1995, 4, 3, 2, 1)):
                actual = DateSynced.actual()

        assert actual == datetime.datetime(2001, 2, 3, 4, 5), "first sync is more important then next syncs"


    def test1(self):
        with DateSynced():
            actual = DateSynced.actual(stamp=datetime.datetime(2001, 2, 3, 4, 5))
            actual = DateSynced.actual(stamp=datetime.datetime(1995, 4, 3, 2, 1))

        assert actual == datetime.datetime(2001, 2, 3, 4, 5)


    def test2(self):
        with DateSynced():
            with DateSynced():
                actual = DateSynced.actual(stamp=datetime.datetime(2001, 2, 3, 4, 5))
                actual = DateSynced.actual(stamp=datetime.datetime(1995, 4, 3, 2, 1))

        assert actual == datetime.datetime(2001, 2, 3, 4, 5)


    def test3(self):
        with DateSynced():
            with DateSynced(datetime.datetime(2004, 4, 4, 4, 4)):
                actual = DateSynced.actual(stamp=datetime.datetime(2001, 2, 3, 4, 5))
                actual = DateSynced.actual(stamp=datetime.datetime(1995, 4, 3, 2, 1))

        assert actual == datetime.datetime(2004, 4, 4, 4, 4)


    def test4(self):
        with DateSynced(datetime.datetime(2004, 4, 4, 4, 4)):
            with DateSynced():
                actual = DateSynced.actual(stamp=datetime.datetime(2001, 2, 3, 4, 5))
                actual = DateSynced.actual(stamp=datetime.datetime(1995, 4, 3, 2, 1))

        assert actual == datetime.datetime(2004, 4, 4, 4, 4)


    def test5(self):
        with DateSynced():
            with DateSynced():
                actual = DateSynced.actual(stamp=datetime.datetime(2001, 2, 3, 4, 5))

            actual = DateSynced.actual(stamp=datetime.datetime(1995, 4, 3, 2, 1))

        assert actual == datetime.datetime(2001, 2, 3, 4, 5)


    def test6(self):
        with DateSynced():
            with DateSynced(datetime.datetime(2004, 4, 4, 4, 4)):
                actual = DateSynced.actual(stamp=datetime.datetime(2001, 2, 3, 4, 5))

            actual = DateSynced.actual(stamp=datetime.datetime(1995, 4, 3, 2, 1))

        assert actual == datetime.datetime(2004, 4, 4, 4, 4)


    def test7(self):
        with DateSynced():
            with DateSynced(datetime.datetime(2004, 4, 4, 4, 4)):
                actual = DateSynced.actual(stamp=datetime.datetime(2001, 2, 3, 4, 5))

        actual = DateSynced.actual(stamp=datetime.datetime(1995, 4, 3, 2, 1))

        assert actual == datetime.datetime(1995, 4, 3, 2, 1)
