class ParserWords:
    ## TODO: write recursive variant with type detection
    ## TODO: rewrite to tube?
    ## TODO: add word length restriction
    def __call__(self, data):
        words = set()

        if type(data) == dict:
            for k, v in data.items():
                words.update(self(k))
                words.update(self(v))

        if type(data) in (list, tuple):
            for v in data:
                words.update(self(v))

        if type(data) == str:
            for word in data.split():
                ## length of 32 chars is for possible md5 checksumms
                if len(word) <= 32:
                    words.add(word)

        return words
