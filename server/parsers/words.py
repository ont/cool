import re

class Parser:
    def __init__(self):
        ## TODO: only russian lang?
        self.re_split = re.compile(r'[^a-zа-я0-9]+', re.I)


    ## TODO: write recursive variant with type detection
    ## TODO: rewrite to tube?
    ## TODO: add word length restriction
    def __call__(self, data):
        words = set()

        if type(data) == dict:
            for k, v in data.items():
                words.update(self(k))
                words.update(self(v))
            return words

        elif type(data) in (list, tuple):
            for v in data:
                words.update(self(v))
            return words

        elif type(data) == str:
            return self.extract(data)

        elif type(data) == bytes:
            try:
                s = data.decode('utf8')
            except:
                return set()

            return self.extract(s)

        elif type(data) == int:
            return set([ str(data) ])
        else:
            return set()


    def extract(self, string):
        words = set()
        for word in self.re_split.split(string):
            if 0 < len(word) <= 32:
                words.add(word)

        return words


    def __repr__(self):
        return 'words'
