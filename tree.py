import os
import datetime

import liquid

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


def lazy_tree(func):
    """ Special decorator for wrapping DateTree method.
        It stores method call history into DateTree._lazy storage
        for later replaying it with DateTree.fresh() method.
    """
    def wrapper(*args, **kargs):
        tree = args[0]
        tree_new = func(*args, **kargs)

        # append lazy call to stack of calls; args[1:] removes "self" from args list
        tree_new._lazy = tree._lazy + [ (func.__name__, args[1:], kargs) ]
        return tree_new

    return wrapper


class DateTree:
    """ This class implements DSL for building & manipulating pathes and
        turning them into "liquid files".
    """

    def __init__(self, path):
        self._lazy = [('base', path)]
        self.path = os.path.abspath(path)

    def __str__(self):
        return self.path

    def __eq__(self, other):
        return self.path == other.path


    def fresh(self):
        """ Returns fresh variant of DateTree with all its components
            replaced by fresh (current) datetime.
        """
        lazy = list(self._lazy)          ## make copy of _lazy
        tree = DateTree(lazy.pop(0)[1])  ## construct DateTree from "base" path

        while lazy:
            name, args, kargs = lazy.pop(0)  ## get next call

            if type(getattr(DateTree, name)) == property:
                tree = getattr(tree, name)
            else:
                method = getattr(tree, name)
                tree = method(*args, **kargs)

        return tree


    @property
    @lazy_tree
    def hour(self):
        return DateTree(os.path.join(
            self.path,
            self.get_year(),
            self.get_month(),
            self.get_day(),
            self.get_hour(),
        ))

    @property
    @lazy_tree
    def day(self):
        return DateTree(os.path.join(
            self.path,
            self.get_year(),
            self.get_month(),
            self.get_day(),
        ))

    @property
    @lazy_tree
    def month(self):
        return DateTree(os.path.join(
            self.path,
            self.get_year(),
            self.get_month(),
        ))


    @property
    @lazy_tree
    def year(self):
        return DateTree(os.path.join(
            self.path,
            self.get_year(),
        ))

    @lazy_tree
    def parent(self):
        return DateTree(os.path.dirname(self.path))

    @lazy_tree
    def suffix(self, suff):
        return DateTree(self.path + suff)

    @lazy_tree
    def join(self, part):
        return DateTree(os.path.join(self.path, part))

    def exists(self):
        return os.path.exists(self.path)

    def open(self, mode, liquid=False):
        return open(self.path, mode)

    def liquid(self):
        """ Converts builded DateTree path into LiquidFile.
        """
        return liquid.LiquidFile(self)

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


if __name__ == '__main__':
    t = DateTree('./paks').hour.suffix('.sav')
    t = t.fresh()
    print(t._lazy)
