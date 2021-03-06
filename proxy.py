#!/usr/bin/env python

import click
import asyncio

from proxy.pipe import ProxyPipe
from common.config import Config
from common.dumper import Dumper


class Proxy:
    def __init__(self, target, bind, dumper=None, headers={}, real_ip=False):
        self.dumper = dumper  ## TODO: change this to DI containers
        self.headers = headers
        self.real_ip = real_ip

        self.thost, self.tport = target
        self.lhost, self.lport = bind

        self.loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.handle_browser_to_proxy, host=self.lhost, port=self.lport)
        asyncio.ensure_future(coro)
        #self.loop.run_until_complete(coro)


    async def handle_browser_to_proxy(self, breader, bwriter):
        print('connecting')
        dreader, dwriter = await asyncio.open_connection(self.thost, self.tport)
        print('connected')

        if self.real_ip:
            client_ip, client_port = bwriter.get_extra_info('peername')
            self.headers['x-forwarded-for'] = client_ip
            self.headers['x-real-ip'] = client_ip

        pipe = ProxyPipe(breader, bwriter, dreader, dwriter, headers=self.headers, dumper=self.dumper)
        await pipe.start()


    def start(self):
        self.loop.run_forever()


def parse_host_port(ctx, param, value):
    if ':' not in value:
        raise click.BadParameter('Must be in form IP:PORT')

    host, port = value.split(':', 1)
    return (host, int(port))



@click.command()
@click.option('--config', default='/etc/cool/config.yml', help='Path to config file (default: /etc/cool/config.yml).')
@click.option('--target', required=True, callback=parse_host_port, help='Target pair IP:PORT to proxy to. All requests will be proxied to this port.')
@click.option('--bind', default='0.0.0.0:8080', callback=parse_host_port, help='Proxy will listen on this IP:PORT')
@click.option('--host', help='Name of site to proxy to. If present then "Host" header of all requests will be set to this value.')
@click.option('--real-ip', is_flag=True, help='If present then "X-Forwarded-For" and "X-Real-IP" headers will be set with client ip address.')
def main(config, target, bind, real_ip, host):
    ## TODO: move host and port (sender's options) to lazy container configuration
    headers = {}
    if host:
        headers['host'] = host

    p = Proxy(
        target,
        bind,
        dumper = Dumper( Config(config) ),
        headers = headers,
        real_ip = real_ip
    )
    p.start()


if __name__ == '__main__':
    main(auto_envvar_prefix='COOL')  ## auto-import of env vars COOL_*
