import zlib
import asyncio
import msgpack

class ProxySender:
    def __init__(self, host, port=26100, delay=10):
        self.host = host
        self.port = port
        self.delay = delay

        self.queue = []

        asyncio.ensure_future(self.process())


    async def process(self):
        while True:
            if self.queue:
                ## TODO: replace it to DI('tubes.packer') container
                data = zlib.compress(b''.join(msgpack.packb(x) for x in self.queue))

                print('.. sending {} bytes'.format(len(data)))

                reader, writer = await asyncio.open_connection(self.host, self.port)
                writer.write(data)
                writer.close()
                print('.. sended...')

                self.queue = []

            await asyncio.sleep(self.delay)


    def send(self, uuid, box, data):
        """ Puts data in queue for sending
        """
        self.queue.append({
            'uuid': 'some-uuid-here',
            'box': box,
            'data': data
        })
