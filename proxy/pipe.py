import asyncio
from proxy.parser import ProxyParser

## TODO: rename to ProxySniffer (main objective of this class is sitting in the middle and parsing http-flow)
class ProxyPipe:
    def __init__(self, breader, bwriter, dreader, dwriter, headers = {}, dumper=None):
        self.loop = asyncio.get_event_loop()
        self.breader = breader
        self.bwriter = bwriter
        self.dreader = dreader
        self.dwriter = dwriter

        ## TODO: rewrite this hell with DI
        self.dumper  = dumper               ## TODO: .. already configured object
        self.parser  = ProxyParser(headers) ## TODO: .. configuration in place


    async def start(self):
        await_coro = self.await_pair()  ## create coro (lazy call to await_pair with no args)
        await_task = asyncio.ensure_future(await_coro) ## shedule async execution of coro object (in future)

        ## await for special coro "wait" for completing of two tasks
        await asyncio.gather(*[
            self.server_to_browser(),
            self.browser_to_server()
        ])

        print('-- cancelling task --')
        await_task.cancel()  ## stops task and its coro


    async def browser_to_server(self):
        print('starting browser_to_server')
        while True:
            chunk = await self.breader.read(1000)
            if not chunk:
                self.parser.browser_stops()
                self.dwriter.close()
                break

            for chunk in self.parser.from_browser(chunk):
                self.dwriter.write(chunk)


    #def parse_chunk(self, chunk):
    #    return chunk.replace(b'localhost:8080', b'nginx.org')


    async def server_to_browser(self):
        print('starting server_to_browser')
        while True:
            chunk = await self.dreader.read(1000)
            if not chunk:
                self.parser.server_stops()
                self.bwriter.close()
                break

            for chunk in self.parser.from_server(chunk):
                self.bwriter.write(chunk)


    async def await_pair(self):
        """ Awaiting for request-response pair from parser.
        """
        while True:
            pair = await self.parser.get_pair()

            with self.dumper:
                self.dumper.save('request',  pair['request'])
                self.dumper.save('response', pair['response'])
