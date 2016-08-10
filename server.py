import zlib
import click
import tubes
import signal
import asyncio
import msgpack

from box import Box

class Server:
    def __init__(self, host='127.0.0.1', port=26100):
        self.loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.handle_connection, host=host, port=port)
        asyncio.ensure_future(coro)

        self.boxes = {}
        for s in (signal.SIGINT, signal.SIGTERM):
            self.loop.add_signal_handler(s, self.close)


    async def handle_connection(self, reader, writer):
        data = b''
        tube = self.get_tube()

        while True:
            chunk = await reader.read(1000)

            for packet in tube(chunk, flush=(not chunk)):
                box = self.get_box(packet[b'box'])
                box.save(packet)
                print('[{}] packet:'.format(packet[b'box']), packet)

            if not chunk:
                break


    def start(self):
        self.loop.run_forever()


    def get_tube(self):
        return tubes.UnzipTube() | tubes.MsgunpackTube()


    def get_box(self, name):
        box = self.boxes.get(name)
        if not box:
            box = self.boxes[name] = Box(name)

        return box


    def close(self):
        print('[!] closing...')
        for name, box in self.boxes.items():
            box.close()

        exit(0)


@click.command()
@click.option('--host', default='127.0.0.1', help='Host to listen on.')
@click.option('--port', default=26100, help='Port to listen on.')
def main(host, port):
    s = Server(host, port)
    s.start()


if __name__ == '__main__':
    main()
