import click
import asyncio

from proxy.pipe import ProxyPipe
from proxy.dumper import ProxyDumper


class Proxy:
    def __init__(self, target, lhost='127.0.0.1', lport=8080, sender=None):
        self.sender = sender  ## TODO: change this to DI containers

        if ':' not in target:
            click.echo('target must be in form ip_addr:port')
            exit(1)

        self.target, self.port = target.split(':')
        self.port = int(self.port)

        self.loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.handle_browser_to_proxy, host=lhost, port=lport)
        asyncio.ensure_future(coro)
        #self.loop.run_until_complete(coro)


    async def handle_browser_to_proxy(self, breader, bwriter):
        print('connecting')
        dreader, dwriter = await asyncio.open_connection(self.target, self.port)
        print('connected')

        pipe = ProxyPipe(breader, bwriter, dreader, dwriter, self.dumper)
        pipe.start()


    def start(self):
        self.loop.run_forever()



@click.command()
@click.argument('target')  # TARGET: all requests will be proxied to this IP address
def main(target):
    ## TODO: move host and port (sender's options) to lazy container configuration
    s = ProxySender('localhost', 26100)
    p = Proxy(target, sender=s)
    p.start()


if __name__ == '__main__':
    main()
