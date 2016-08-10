
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
class Index:
    def __init__(self, tree):
        self.tree = tree

    def save(self, key, rec_id):
        pass
