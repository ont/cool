import os
import tubes

class Pak:
    def __init__(self, path):
        self.pak = self.create_pak(path)  ## inside we check file existance
        self.sav = self.create_sav(path)

        self.tube_pak = self.create_tube_pak()
        self.tube_sav = self.create_tube_sav()
        self.path = path


    ## TODO: move it to DI('tubes.file-packer') container, because it is changable application part
    def create_tube_pak(self):
        return tubes.MsgpackTube() | tubes.ZipTube()


    def create_tube_sav(self):
        return tubes.MsgpackTube()


    def write(self, data):
        for chunk in self.tube_sav(data, flush=True):  ## NOTE: actually we don't need flush=True for single MsgpackTube
            self.sav.write(chunk)                      ## TODO: fsync here?
            self.sav.flush()

        for chunk in self.tube_pak(data):
            self.pak.write(chunk)


    def close(self):
        for chunk in self.tube_pak(None, flush=True):
            self.pak.write(chunk)

        self.sav.close()
        self.pak.close()

        os.remove(self.sav.name)


    def create_sav(self, path):
        return path.suffix(self.usuff).suffix('.sav').open('wb')


    def create_pak(self, path):
        usuff, n = '', 0
        while path.suffix(usuff).suffix('.pak').exists():
            usuff, n = '_{:0>4}'.format(n), n+1

        self.usuff = usuff

        path.parent().makedirs()
        return path.suffix(usuff).suffix('.pak').open('wb')


class PakExistsException(Exception):
    pass
