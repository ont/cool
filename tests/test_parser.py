from parsers import ParserWords

class TestParser:
    def test_dict(self):
        """ Checks dict data type
        """
        p = ParserWords()
        data = {
            'test': 'test',
            'me': 'me md5md5md5md5md5md5md5md5md5md512',
            'it may work qweqweqweqweqweqweqweqweqweqweqwe': 123
        }
        words = p(data)

        assert words == set(['test', 'me', 'it', 'may', 'work', 'md5md5md5md5md5md5md5md5md5md512']), "only small single words"


    def test_list_tuple(self):
        """ Checks list and tuple data type (iterables)
        """
        p = ParserWords()
        data = ['123', 123, 123.0, ('abc zxy', 'aww'), [[['me', 'and me here']]]]
        words = p(data)
        assert words == set(['123', 'abc', 'zxy', 'aww', 'me', 'and', 'here']), "only small single words"


    def test_list_recursive(self):
        """ Checks list and tuple data type (iterables)
        """
        p = ParserWords()
        data = [
            '123', 123, 123.0, (
                'abc zxy', 'aww', {
                    'test': 'test',
                    'me': 'me md5md5md5md5md5md5md5md5md5md512',
                    'it may work qweqweqweqweqweqweqweqweqweqweqwe': 123
                },
                None
            ),
            [[['me', 'and me here']]]
        ]
        words = p(data)
        assert words == set(['123', 'abc', 'zxy', 'it', 'may', 'work',
            'aww', 'me', 'and', 'here', 'test', 'md5md5md5md5md5md5md5md5md5md512']), "only small single words"
