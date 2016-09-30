
class Parser:
    def __call__(self, data):
        if type(data) == dict:
            return data.get('method', None)

        return None

    def __repr__(self):
        return 'http-method'
