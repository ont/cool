import os
import tubes
import datetime
from files import PakFile, SavFile
from tree import DateTree, DateSynced

class Box:
    def __init__(self, name, base = './paks'):
        self.name = name.decode('utf-8') if type(name) == bytes else name
        self.tree = DateTree(base).join(name)

        self.pak = self.tree.hour.suffix('.pak').liquid(PakFile)
        self.sav = self.tree.hour.suffix('.sav').liquid(SavFile)
        #self.idx = self.tree.hour.suffix('.idx')


    def save(self, data):
        with DateSynced():
            self.pak.save(data)
            self.sav.save(data)
            #self.idx


    def close(self):
        self.pak.close()
        self.sav.close()


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
