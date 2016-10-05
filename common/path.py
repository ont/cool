import os
import glob
import fnmatch
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
# DatePath('./paks').hour.suffix('.sav')
# DatePath('./paks').hour.unique().suffix('.sav')
# DatePath('./paks').hour.suffix('.sav', unique=True) <<<
#
# TODO: DatePath as immutable object (fixed timestamp)
# TODO: removing lazy replacing with freezed strftime self._path
#
# TODO: replace self.liquid(self) --> self.liquid(self, Proto)
#

class DateSynced:
    """ Use this object in transactions where all DatePath objects must by synced in time.

        with DateSynced():
            dt1 = dt1.fresh()
            sleep(1)
            dt2 = dt2.fresh()
            assert dt1.stamp == dt2.stamp, 'should be fresh and equal'
    """
    synced = False
    enters = []
    stamp = None

    def __init__(self, stamp = None):
        self.stamp = stamp

    def __enter__(self):
        DateSynced.enters.append(None)
        DateSynced.synced = True
        if self.stamp:
            DateSynced.actual(self.stamp)


    def __exit__(self, *args):
        DateSynced.enters.pop()
        if not DateSynced.enters:
            DateSynced.synced = False
            DateSynced.stamp = None


    @classmethod
    def actual(klass, stamp=None):
        """ Returns stamp for current active lock or save "stamp" into lock.
            If there is no locks then it simply returns "stamp".
            If "stamp" is None then it is replaced with current time.
        """
        if not stamp:
            stamp = datetime.datetime.now()

        if DateSynced.synced:
            if DateSynced.stamp:
                stamp = DateSynced.stamp
            else:
                DateSynced.stamp = stamp

        return stamp



class DatePath:
    """ This class implements DSL for building & manipulating pathes and
        turning them into "liquid files".
    """

    def __init__(self, path, stamp=None, exact=False):
        self.stamp = stamp if exact else DateSynced.actual(stamp)
        self._path = os.path.abspath(path)

    def __str__(self):
        return self.stamp.strftime(self._path)

    def __eq__(self, other):
        return self.path == other.path

    def fresh(self):
        """ Returns fresh variant of DatePath for now datetime.
        """
        stamp = DateSynced.actual()
        return DatePath(self._path, stamp=stamp)   ## no exact


    @property
    def path(self):
        return str(self)

    @property
    def minute(self):
        return DatePath(os.path.join(self._path, '%Y', '%m', '%d', '%H', '%M'), stamp=self.stamp, exact=True)

    @property
    def hour(self):
        return DatePath(os.path.join(self._path, '%Y', '%m', '%d', '%H'), stamp=self.stamp, exact=True)

    @property
    def day(self):
        return DatePath(os.path.join(self._path, '%Y', '%m', '%d'), stamp=self.stamp, exact=True)

    @property
    def month(self):
        return DatePath(os.path.join(self._path, '%Y', '%m'), stamp=self.stamp, exact=True)

    @property
    def year(self):
        return DatePath(os.path.join(self._path, '%Y'), stamp=self.stamp, exact=True)

    def parent(self):
        return DatePath(os.path.dirname(self._path), stamp=self.stamp, exact=True)

    def basename(self):
        return os.path.basename(self._path)

    def suffix(self, suff):
        return DatePath(self._path + self.escape(suff), stamp=self.stamp, exact=True)

    def join(self, part):
        return DatePath(os.path.join(self._path, self.escape(part)), stamp=self.stamp, exact=True)

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


    def find(self, recursive=True):
        """ Searches for files in self.path

            :recursive: if true then search in current path and in all subfolders
            :returns: iterator (list of founded files)

            TODO: return DatePath's instead of strings
        """
        if not recursive:
            return glob.glob(self.path)

        pattern = self.basename()
        for root, dirs, files in os.walk(self.parent().path):
            for file in fnmatch.filter(files, pattern):
                yield os.path.join(root, file)
