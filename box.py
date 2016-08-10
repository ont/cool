import os
import tubes
import datetime
from pak import Pak, PakExistsException
from tree import DateTree

class Box:
    def __init__(self, name, base = './paks'):
        self.name = name.decode('utf-8') if type(name) == bytes else name
        self.tree = DateTree(base).join(name)

        self.pak = None


    def save(self, data):
        pak = self.get_pak()
        pak.write(data)


    def close(self):
        self.pak.close()


    def get_pak(self):
        path = self.tree.hour

        if not self.pak or self.pak.path != path:
            if self.pak:
                self.pak.close()

            self.pak = Pak(path)
            return self.pak

        return self.pak



    ## TODO: move it to DI('storage.path', time) container, because it is changable application part
    ## TODO: also remove self.base from this class
    ## TODO: rename and rewrite to DI('storage.pak') --> open file object, singleton
    ## TODO: better variant with common class "Tree" for storing pak/sav/index at right positions
    ## TODO: DI('storage.tree') --> tree singleton
    def get_base(self):
        part = datetime.datetime.now().strftime('%Y/%m/%d/%H')  ## TODO: manual path join here
        return os.path.join(self.base, self.name, part)


###
# TODO: must be rewritten to iterators
# PROBLEM: we feed tube with one chunk of data and tube can produce many chunks (unpacking mode)
#
# t << data
# for chunk in t:
#     print chunk
#
# for chunk in t << data:
#     print chunk
#
# for chunk in t(data):
#     print chunk
#
# for chunk in t.flush():
#     print chunk
#
