#!/usr/bin/env python

import os
import glob
import click
import tubes
import signal
import asyncio

from box import Box
from recover import Recover

class Server:
    def __init__(self, host='127.0.0.1', port=26100, storage='./boxes'):
        self.loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.handle_connection, host=host, port=port)
        asyncio.ensure_future(coro)

        self.storage = storage

        self.boxes = {}
        self.load_boxes()

        self.install_signals()


    async def handle_connection(self, reader, writer):
        data = b''
        tube = self.get_tube()

        while True:
            chunk = await reader.read(1024)
            print(chunk)

            for packet in tube(chunk, flush=(not chunk)):
                box = self.get_box(packet[b'box'])
                data = packet[b'data']

                box.save(data)

                print('[{}] data:'.format(packet[b'box']), data)

            if not chunk:
                break


    def start(self):
        self.loop.run_forever()


    def load_boxes(self):
        for file in glob.glob(self.storage + '/*'):
            if os.path.isdir(file):
                name = bytes(os.path.basename(file), 'utf8')
                ## do recover after possible crash
                r = Recover(name, self.storage)
                r.recover()

                self.boxes[name] = Box(name, self.storage)


    def get_tube(self):
        return tubes.UnzipTube() | tubes.MsgunpackTube()


    def get_box(self, name):
        box = self.boxes.get(name)
        if not box:
            box = self.boxes[name] = Box(name, self.storage)

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
@click.option('--host', default='127.0.0.1', help='Host to listen on (default: 127.0.0.1).')
@click.option('--port', default=26100, help='Port to listen on (default: 26100).')
@click.option('--storage', help='Directory where all compressed logs will be saved (default: ./boxes). Also can be specified via COOL_STORAGE environment variable.')
def main(host, port, storage):
    if not storage:
        storage = os.getenv('COOL_STORAGE', './boxes')

    s = Server(host, port, storage)
    s.start()


if __name__ == '__main__':
    main()
