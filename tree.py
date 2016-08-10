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


class DateTree:

    def __init__(self, path):
        self.path = os.path.abspath(path)

    def __str__(self):
        return self.path

    def __eq__(self, other):
        return self.path == other.path

    @property
    def hour(self):
        return DateTree(os.path.join(
            self.path,
            self.get_year(),
            self.get_month(),
            self.get_day(),
            self.get_hour(),
        ))

    @property
    def day(self):
        return DateTree(os.path.join(
            self.path,
            self.get_year(),
            self.get_month(),
            self.get_day(),
        ))

    @property
    def month(self):
        return DateTree(os.path.join(
            self.path,
            self.get_year(),
            self.get_month(),
        ))


    @property
    def year(self):
        return DateTree(os.path.join(
            self.path,
            self.get_year(),
        ))

    def parent(self):
        return DateTree(os.path.dirname(self.path))

    def suffix(self, suff):
        return DateTree(self.path + suff)

    def join(self, part):
        return DateTree(os.path.join(self.path, part))

    def exists(self):
        return os.path.exists(self.path)

    def open(self, mode):
        return open(self.path, mode)

    def makedirs(self):
        if not self.exists():
            os.makedirs(self.path)
        return self


    def get_hour(self):
        return datetime.datetime.now().strftime('%H')

    def get_day(self):
        return datetime.datetime.now().strftime('%d')

    def get_month(self):
        return datetime.datetime.now().strftime('%m')

    def get_year(self):
        return datetime.datetime.now().strftime('%Y')
