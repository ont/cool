#!/usr/bin/env python

import os
import glob
import click
import signal
import asyncio
import common.tubes

from server.box import Box
from server.loader import Loader
from server.recover import Recover
from common.config import Config

class Server:
    def __init__(self, host='127.0.0.1', port=26100, config=None, loader=None):
        """
        :host: host to listen on
        :port: port to listen on
        :config: instance of Config class (parsed confing)
        :loader: loader object for loading boxes/indexes from config)

        """
        self.loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.handle_connection, host=host, port=port)
        asyncio.ensure_future(coro)

        ## TODO: replace this with DI?
        self.config = config
        self.loader = loader

        self.boxes = {}
        self.recover_boxes()
        self.load_boxes()

        self.install_signals()


    async def handle_connection(self, reader, writer):
        data = b''
        tube = self.get_tube()

        while True:
            chunk = await reader.read(1024)
            print('net:', chunk)

            for packet in tube(chunk, flush=(not chunk)):
                box = self.get_box(packet[b'box'])
                data = packet[b'data']

                box.save(data)

                print('[{}] data:'.format(packet[b'box']), data)

            if not chunk:
                break


    def get_tube(self):
        return tubes.UnzipTube() | tubes.MsgunpackTube()


    def start(self):
        self.loop.run_forever()


    def recover_boxes(self):
        ## TODO: rewrite it to single recoverer of all boxes with DI
        for file in glob.glob(self.config.storage + '/*'):
            if os.path.isdir(file):
                name = bytes(os.path.basename(file), 'utf8')

                ## do recover of single box after possible crash
                Recover().recover( self.loader.load_box(name) )


    def load_boxes(self):
        boxes = self.loader.load_boxes()
        print('loaded boxes:', boxes)
        for box in boxes:
            name = bytes(box.name, 'utf8')
            self.boxes[name] = box



    def get_box(self, name):
        box = self.boxes.get(name)
        if not box:
            ## create box with no indexes
            box = self.boxes[name] = Box(name, self.config.storage)

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
@click.option('--config', default='/etc/cool/config.yml', help='Path to config file (default: /etc/cool/config.yml).')
def main(host, port, config):
    config = Config(config)
    loader = Loader(config)

    s = Server(
        host, port,
        config=config,
        loader=loader
    )
    s.start()


if __name__ == '__main__':
    main()
