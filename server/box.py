import os
import datetime
import common.tubes
from server.files import PakFile, SavFile
from server.path import DatePath, DateSynced

class Box:
    def __init__(self, name, base = './boxes', indexes = None):
        self.name = name.decode('utf-8') if type(name) == bytes else name
        self.base = base
        self.dpath = DatePath(base).join(self.name)

        self.pak = PakFile(self.dpath.minute.suffix('.pak'))
        self.sav = SavFile(self.dpath.minute.suffix('.sav'))

        self.idxs = indexes if indexes else []


    def save(self, data, backup=True):
        with DateSynced():
            self.pak.save(data)

            if backup:
                self.sav.save(data)

            for idx in self.idxs:
                idx.save(data)


    def close(self):
        self.pak.close()
        self.sav.close()

        for idx in self.idxs:
            idx.close()


    def __repr__(self):
        return '<Box idxs={}>'.format(repr(self.idxs))

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
    import json
    err = 0

    b = Box('logs')

    for n, l in enumerate(open('logs/full.log')):
        if n and n % 10 == 0:
            print('total:', n)
            break

        try:
            data = json.loads(l)
            dt = datetime.datetime.fromtimestamp(data[0]['REQUEST_TIME'])
            with DateSynced(stamp=dt):
                b.save(data)
        except json.decoder.JSONDecodeError:
            err += 1
            print('err:', err)
        #n -= 1
        #if not n:
        #    break

    b.close()
