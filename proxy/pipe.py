import asyncio
from proxy.parser import ProxyParser
from proxy.mutator import Mutator

## TODO: rename to ProxySniffer (main objective of this class is sitting in the middle and parsing http-flow)
class ProxyPipe:
    def __init__(self, breader, bwriter, dreader, dwriter, dumper=None):
        self.loop = asyncio.get_event_loop()
        self.breader = breader
        self.bwriter = bwriter
        self.dreader = dreader
        self.dwriter = dwriter

        ## TODO: rewrite this hell with DI
        self.dumper  = dumper           ## TODO: .. already configured object
        self.parser  = ProxyParser()    ## TODO: .. no configuration, just create


    def start(self):
        ## TODO: test async <--> ensure_future replacement
        asyncio.async(self.start_loops())


    async def start_loops(self):
        asyncio.ensure_future(self.server_to_browser())  ## asyncio.async(..)
        asyncio.ensure_future(self.browser_to_server())  ## asyncio.async(..)
        asyncio.ensure_future(self.await_pair())         ## asyncio.async(..)


    async def browser_to_server(self):
        print('starting browser_to_server')
        while True:
            chunk = await self.breader.read(1000)
            if not chunk:
                self.parser.browser_stops()
                break

            self.parser.from_browser(chunk)
            self.dwriter.write(chunk)


    #def parse_chunk(self, chunk):
    #    return chunk.replace(b'localhost:8080', b'nginx.org')


    async def server_to_browser(self):
        print('starting server_to_browser')
        while True:
            chunk = await self.dreader.read(1000)
            if not chunk:
                ## TODO: self.parser.server_stops() --> calls ProxyParser.send(...)
                self.parser.server_stops()
                break

            self.parser.from_server(chunk)
            self.bwriter.write(chunk)


    async def await_pair(self):
        """ Awaiting for request-response pair from parser.
        """
        while True:
            pair = await self.parser.get_pair()

            if not pair:
                print('-- closing pipe')
                break

            #self.dumper.save('request',  pair['request'])
            #self.dumper.save('response', pair['response'])
