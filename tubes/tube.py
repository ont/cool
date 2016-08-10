
class Tube:

    def __init__(self):
        self.head = self
        self.child = None

    def __or__(self, other):
        self.child = other
        other.head = self.head
        return other


    def process(self, data):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError


    def __call__(self, data, flush=False):
        if data:
            yield from self.head_process(data)

        if flush:
            yield from self.head_flush()


    def head_process(self, data):
        yield from self.head.chain_process(data)

    def head_flush(self):
        yield from self.head.chain_flush()


    def chain_process(self, data):
        if self.child:
            for chunk in self.process(data):
                yield from self.child.chain_process(chunk)

        else:
            yield from self.process(data)


    def chain_flush(self):
        if self.child:
            for chunk in self.flush():
                yield from self.child.chain_process(chunk)

            yield from self.child.chain_flush()

        else:
            yield from self.flush()
