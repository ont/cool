
class Parser:
    def __call__(self, data):
        if type(data) == dict:
            return data.get('code', None)

        return None


    def __repr__(self):
        return 'http-code'
