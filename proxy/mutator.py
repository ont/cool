class Mutator(object):
    """Class for changing (mutating) request's headers.

       Usage:
       m = Mutator({'host': 'new.host.com'})
       ...
       old_headers = 'Host: some.old.com<CR><LF>Referrer: http://blabla.com'
       new_headers = m.mutate(old_headers)
    """

    def __init__(self, headers):
        """
        :headers: HTTP headers to replace/add

        """
        self.headers = {bytes(name, 'utf8'): bytes(value, 'utf8') for name, value in headers.items()}



    def mutate(self, request_headers):
        """Transform (mutate) given headers.
        """
        head, tail = self.buffer.split(b"\r\n\r\n", 1)
        lines = head.split(b"\r\n")  ## TODO: possible case of single \n

        replaced = []
        for n, line in enumerate(lines):
            if n == 0:
                continue  ## skip request line

            name, value = line.split(b':', 1)
            lname = name.lower()
            if lname in self.headers:
                lines[n] = name + b': ' + self.headers[lname]
                replaced.append(lname)


        for lname, value in self.headers.items():
            if lname not in replaced:
                lines.append(self.ucfirstb(lname) + b': ' + value)

        self.buffer = b"\r\n".join(lines) + b"\r\n\r\n" + tail


    def ucfirstb(self, name):
        """Returns name with first letter in uppercase.

        :name: string to transform
        :returns: name (as bytes) with first letter in uppercase

        """
        return name[0].upper() + name[1:].lower()
