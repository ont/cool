import os
import tubes
import datetime
from files import PakFile, SavFile
from tree import DateTree, DateSynced

class Box:
    def __init__(self, name, base = './paks'):
        self.name = name.decode('utf-8') if type(name) == bytes else name
        self.tree = DateTree(base).join(name)

        self.pak = PakFile(self.tree.hour.suffix('.pak'))
        self.sav = SavFile(self.tree.hour.suffix('.sav'))
        #self.idx = IndexWord(self.tree)  <--- from base


    def save(self, data):
        with DateSynced():
            self.sav.save(data)
            self.pak.save(data)
            #self.idx.save(data)


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

if __name__ == "__main__":
    import os
    import index
    os.system('rm -rf /tmp/index')
    i = index.Index(DateTree('/tmp/index'))
    i.save({'test': 'me', 'abc': 123})
    i.save({'test': 'me', 'asdf': 123, 'ololo': 'trololo'})
    i.save({'ololo': 'trololo', 'kkk': 'mememe'})
    i.flush()
