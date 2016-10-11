import time
import gzip
import asyncio
from io import BytesIO
from proxy.mutator import Mutator

try:
    from http_parser.parser import HttpParser
except ImportError:
    print("[!] NONFAST PARSER")
    from http_parser.pyparser import HttpParser


class ProxyParser:
    def __init__(self, headers):
        self.mutator = Mutator(headers)
        self.reset()


    def reset(self):
        self.ts = None            ## timestamp of request
        self.b2p = HttpParser()   ## browser to proxy parser
        self.s2p = HttpParser()   ## server to proxy parser
        self.b2p_raw = b''        ## raw request
        self.s2p_raw = b''        ## raw response

        self.b2p_state = 'head'  ## what part of request to mutate+send next

        self.future = asyncio.Future()


    ## TODO: websockets/other-over-http case
    def from_browser(self, chunk):
        if not self.ts:
            self.ts = time.time()

        ## TODO: test parsed length, if error (parsed != len(chunk)) then close connection
        self.b2p.execute(chunk, len(chunk))
        self.b2p_raw += chunk

        ## TODO: move mutate-call/reassemble logic to external class?
        if self.b2p.is_headers_complete() and self.b2p_state == 'head':
            first_line = ' '.join([
                self.b2p.get_method(),
                self.b2p.get_url(),
                'HTTP/{}.{}'.format(*self.b2p.get_version())
            ])
            headers = self.mutator.mutate(self.b2p.get_headers())
            headers = '\r\n'.join(['{}: {}'.format(name, value) for name, value in headers.items()])

            self.b2p_state = 'body'
            #yield first_line + headers
            yield bytes(first_line + '\r\n' + headers + '\r\n\r\n', 'utf8')

        elif self.b2p.is_headers_complete() and self.b2p_state == 'body':
            chunk = self.b2p.recv_body()
            if chunk:
                yield chunk



    ## TODO: try: except:  with conversation logging (and self.reset()?)
    ## TODO: websockets/other-over-http case
    def from_server(self, chunk):
        ## TODO: test parsed length, if error (parsed != len(chunk)) then close connection
        self.s2p.execute(chunk, len(chunk))
        self.s2p_raw += chunk

        yield chunk

        if self.s2p.is_message_complete():
            self.resolve()



    ## TODO: for browsers crashes (incomplete requests)
    def browser_stops(self):
        print('-- browser stops --')


    ## TODO: for server crashes (incomplete responses)
    def server_stops(self):
        ## TODO: self.send() here...
        print('-- server stops --')


    def resolve(self):
        """Internal method of parser for resolving future returned
           from Parser.get_pair() method.
        """
        dt = int((time.time() - self.ts) * 1000)
        print('{}ms'.format(dt), self.b2p.get_method(), self.b2p.get_url(), '  {} bytes'.format(len(self.s2p_raw)))
        self.future.set_result({
            'request': self.b2p_raw,
            'response': self.s2p_raw,
            'time': dt
        })
        self.reset()


    def get_pair(self):
        """ Use "await" from this method for recieving final request-response pair.
            Returns: future object which will be resolved in future
        """
        return self.future
