import os
import datetime

#
# TODO:
# better DSL:
# Tree().hour().suffix('.sav').open('rb')
# Tree().hour().join('file.sav').open('rb')
#
# so-so DSL:
# Tree().hour_file('.sav')
# Tree().hour_dir_file('file.sav')
#
# exotic DSL:
# Tree().Ymdh.suffix('.sav')
# Tree().Y.m.d.h.suffix('.sav').join('tmp')
# Tree().jY.jm.jd.jh.suffix('.sav').join('tmp')
# Tree().jY.jm.jd.jh.s('.sav').j('tmp').s('_').sY.s('-').sd.s('-')...
#
# TODO: our class relase easy access to dirs/files builded around _dates_
#
# DateTree('./paks').hour.suffix('.sav')
# DateTree('./paks').hour.unique().suffix('.sav')
# DateTree('./paks').hour.suffix('.sav', unique=True) <<<
#
# TODO: DateTree as immutable object (fixed timestamp)
# TODO: removing lazy replacing with freezed strftime self._path
#
# TODO: replace self.liquid(self) --> self.liquid(self, Proto)
#

class DateSynced:
    """ Use this object in transactions where all DateTree objects must by synced in time.

            with DateSynced():
                dt1 = dt1.fresh()
                sleep(1)
                dt2 = dt2.fresh()
                assert dt1.stamp == dt2.stamp, 'should fresh and equal'
    """
    synced = False
    stamp = None

    def __init__(self, stamp = None):
        DateSynced.stamp = stamp

    def __enter__(self):
        DateSynced.synced = True

    def __exit__(self, *args):
        DateSynced.synced = False
        DateSynced.stamp = None


class DateTree:
    """ This class implements DSL for building & manipulating pathes and
        turning them into "liquid files".
    """

    def __init__(self, path, stamp=None):
        self.stamp = stamp
        if not self.stamp:
            self.stamp = datetime.datetime.now()

        self._path = os.path.abspath(path)

    def __str__(self):
        return self.stamp.strftime(self._path)

    def __eq__(self, other):
        return self.path == other.path

    def fresh(self):
        """ Returns fresh variant of DateTree for now datetime.
        """
        if DateSynced.synced:
            if DateSynced.stamp:
                stamp = DateSynced.stamp
            else:
                stamp = DateSynced.stamp = datetime.datetime.now()
        else:
            stamp = datetime.datetime.now()

        return DateTree(self._path, stamp=stamp)


    @property
    def path(self):
        return str(self)

    @property
    def minute(self):
        return DateTree(os.path.join(self._path, '%Y', '%m', '%d', '%H', '%M'), stamp=self.stamp)

    @property
    def hour(self):
        return DateTree(os.path.join(self._path, '%Y', '%m', '%d', '%H'), stamp=self.stamp)

    @property
    def day(self):
        return DateTree(os.path.join(self._path, '%Y', '%m', '%d'), stamp=self.stamp)

    @property
    def month(self):
        return DateTree(os.path.join(self._path, '%Y', '%m'), stamp=self.stamp)

    @property
    def year(self):
        return DateTree(os.path.join(self._path, '%Y'), stamp=self.stamp)

    def parent(self):
        return DateTree(os.path.dirname(self._path), stamp=self.stamp)

    def suffix(self, suff):
        return DateTree(self._path + self.escape(suff), stamp=self.stamp)

    def join(self, part):
        return DateTree(os.path.join(self._path, self.escape(part)), stamp=self.stamp)

    def escape(self, part):
        """ Replaces all occurence of % to %% in path part.
            This is done because internal self._path var is in strftime format.
        """
        return part.replace('%', '%%')

    def exists(self):
        return os.path.exists(self.path)

    def open(self, mode):
        return open(self.path, mode)

    def unlink(self):
        os.unlink(self.path)

    def makedirs(self):
        if not self.exists():
            os.makedirs(self.path)
        return self

