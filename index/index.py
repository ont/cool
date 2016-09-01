#
# TODO:
#
#  ---dddddddddddddddddddddddddddd--------------------------------------> t
#     |--m--||--m--||--m--||--m--|
#     |-----------YYYY-----------|
#
#
#  d - day index {'key': [..ids in day..]}
#  m - month index {'key': [..days..]}
#  YYYY - year index {'key': [..months..]}  (it is BIG (!)) <---> better to do N requests to months indexes?
#
# TODO: no need for (id, data), (id, data)  (no inserts between packets inside pak)
#
# TODO:
# m --> {'key': [..(day, count), (day, count)..]}
# YYYY --> {'key': [..(month, count), (month, count)..]}
#
# TODO: (-)
# something that _exists_ in one day and _doesn't_exists_ at another --> otherwise
# unpacking for ids equals to fullscan (+) index just removes time to parse and search in record
#
# TODO: (+) index gives some aggr stats about keys
#

# TODO: better naming / design for supporting different types of indexes?

from tree import DateSynced
from index import FileIds, FileAgg
from parsers import ParserWords

class Index:
    def __init__(self, tree):
        self.tree = tree
        self.file_ids = FileIds(self.tree.minute.suffix('.idx'))
        self.file_ids.on_change(self.flush_aggs)
        self.file_aggs = [
            FileAgg(self.tree.hour.suffix('.idx')),
            FileAgg(self.tree.day.suffix('.idx')),
            FileAgg(self.tree.month.suffix('.idx')),
            FileAgg(self.tree.year.suffix('.idx')),
        ]

        ## TODO: DI('parser') here ?
        self.parser = ParserWords()


    def save(self, data):
        words = self.normlize_words( self.parser(data) )
        with DateSynced():
            self.file_ids.save(words)
            for f in self.file_aggs:
                f.save(words)


    def normlize_words(self, words):
        """ Converts each words from string to bytes.
        """
        return [bytes(x, 'utf8') for x in words]


    def flush(self):
        self.file_ids.flush()
        self.flush_aggs()


    def flush_aggs(self):
        for f in self.file_aggs:
            f.flush()

