class Mutator(object):
    """Special class for transforming (mutating) part of headers and adding new one.
    """

    def __init__(self, headers):
        """
        :headers: headers to mutate (dictionary with name-value pairs for new headers)
        """
        self.headers = headers


    def mutate(self, headers):
        """Transform headers with data form self.headers

        :headers: dictionary with headers to transform
        :returns: transformed dictionary

        """
        used = []
        for name in headers:
            lname = name.lower()
            if lname in self.headers:
                headers[name] = self.headers[lname]
                used.append(lname)

        for lname in self.headers:
            if lname not in used:
                headers[self.ucfirst(lname)]

        return headers


    def ucfirst(self, name):
        """
        :name: name to transform
        :returns: name with first letter in uppercase

        """
        return name[0].upper() + name[1:].lower()
