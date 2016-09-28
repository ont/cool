import os
import glob
import click
import tubes
import signal
import asyncio

from box import Box

class Server:
    box_base = './boxes'  ## TODO: move to config

    def __init__(self, host='127.0.0.1', port=26100):
        self.loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.handle_connection, host=host, port=port)
        asyncio.ensure_future(coro)

        self.boxes = {}
        self.load_boxes()

        self.install_signals()


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


    def load_boxes(self):
        for file in glob.glob(self.box_base + '/*'):
            if os.path.isdir(file):
                name = os.path.basename(file)
                ## do recover after possible crash
                r = Recover(name, self.box_base)
                r.recover()

                self.boxes[name] = Box(name, self.box_base)



    def get_tube(self):
        return tubes.UnzipTube() | tubes.MsgunpackTube()


    def get_box(self, name):
        box = self.boxes.get(name)
        if not box:
            box = self.boxes[name] = Box(name, self.box_base)

        return box


    def install_signals(self):
        for s in (signal.SIGINT, signal.SIGTERM):
            self.loop.add_signal_handler(s, self.close)


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
