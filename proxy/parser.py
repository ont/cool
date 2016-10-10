import time
import gzip
import asyncio
from io import BytesIO

try:
    from http_parser.parser import HttpParser
except ImportError:
    print("[!] NONFAST PARSER")
    from http_parser.pyparser import HttpParser


class ProxyParser:
    ## TODO: replace sender argument with DI container
    def __init__(self):
        self.reset()


    def reset(self):
        self.ts = None            ## timestamp of request
        self.b2p = HttpParser()   ## browser to proxy parser
        self.s2p = HttpParser()   ## server to proxy parser
        self.b2p_raw = b''        ## raw request
        self.s2p_raw = b''        ## raw response


        self.future = asyncio.Future()

        ## NOTE: wrong (see below)
        #self.data = {}           ## data to send through sender


    ## TODO: try: except:  with conversation logging (and self.reset()?)
    ## TODO: websockets/other-over-http case
    def from_browser(self, chunk):
        if not self.ts:
            self.ts = time.time()

        self.b2p.execute(chunk, len(chunk))
        self.b2p_raw += chunk



    ## TODO: try: except:  with conversation logging (and self.reset()?)
    ## TODO: websockets/other-over-http case
    def from_server(self, chunk):
        self.s2p.execute(chunk, len(chunk))
        self.s2p_raw += chunk

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

    ###
    # COMPLETELY WRONG: we need __simpliest__ proxy for just detecting request-response pairs of raw http
    # NOTE: check only s2p.is_message_complete()
    ###
    #def send(self):
    #    ## TODO: if sended: return ... (after successfull send clear b2p_raw and s2p_raw)
    #    ## TODO: make this method async

    #    for action in ('req_method', 'req_path', 'req_query', 'req_headers', 'req_body',
    #                   'res_code', 'res_headers', 'res_body'):
    #        action = getattr(self, 'add_' + action)
    #        action()

    #    print(self.data)
    #    self.reset()


    #def add_req_method(self):
    #    """ TODO: think about decomposing of each action_* into separate class
    #        Adds method (GET or POST) to result data for logging.
    #    """
    #    self.data['req_method'] = self.b2p.get_method()

    #def add_req_url(self):
    #    self.data['req_url'] = self.b2p.get_url()

    #def add_req_path(self):
    #    self.data['req_path'] = self.b2p.get_path()

    #def add_req_query(self):
    #    self.data['req_query'] = self.b2p.get_query_string()

    #def add_req_headers(self):
    #    self.data['req_headers'] = self.b2p.get_headers()

    #def add_req_body(self):
    #    self.data['req_body'] = self.b2p.recv_body()

    #def add_res_code(self):
    #    self.data['res_code'] = self.s2p.get_status_code()

    #def add_res_headers(self):
    #    self.data['res_headers'] = self.s2p.get_headers()

    #def add_res_body(self):
    #    hs = self.s2p.get_headers()
    #    body = self.s2p.recv_body()

    #    if hs.get('Content-Encoding', None) == 'gzip':
    #        sio = BytesIO(body)
    #        body = gzip.GzipFile(fileobj=sio).read()

    #    self.data['res_body'] = body
